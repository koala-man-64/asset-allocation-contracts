from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol


DEFAULT_BRANCH = "refs/heads/main"


class AzureDevOpsClient(Protocol):
    def get_definition_id(self, pipeline_name: str) -> int:
        ...

    def get_latest_run(self, definition_id: int, branch: str) -> dict[str, Any] | None:
        ...

    def queue_run(
        self,
        *,
        definition_id: int,
        branch: str,
        variables: dict[str, str],
    ) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class RetryDecision:
    pipeline_name: str
    definition_id: int
    action: str
    reason: str
    latest_run_id: int | None = None
    queued_run_id: int | None = None


class RestAzureDevOpsClient:
    def __init__(self, *, organization: str, project: str, token: str, api_version: str) -> None:
        self.organization = organization.rstrip("/")
        self.project = project
        self.token = token
        self.api_version = api_version

    def get_definition_id(self, pipeline_name: str) -> int:
        data = self._request_json(
            "GET",
            "build/definitions",
            {
                "name": pipeline_name,
                "api-version": self.api_version,
            },
        )
        definitions = data.get("value", [])
        exact_matches = [item for item in definitions if item.get("name") == pipeline_name]
        if not exact_matches:
            raise ValueError(f"Pipeline definition was not found: {pipeline_name}")
        if len(exact_matches) > 1:
            raise ValueError(f"Pipeline definition name is ambiguous: {pipeline_name}")
        definition_id = exact_matches[0].get("id")
        if not isinstance(definition_id, int):
            raise ValueError(f"Pipeline definition is missing an integer id: {pipeline_name}")
        return definition_id

    def get_latest_run(self, definition_id: int, branch: str) -> dict[str, Any] | None:
        data = self._request_json(
            "GET",
            "build/builds",
            {
                "definitions": str(definition_id),
                "branchName": branch,
                "queryOrder": "queueTimeDescending",
                "$top": "1",
                "api-version": self.api_version,
            },
        )
        runs = data.get("value", [])
        return runs[0] if runs else None

    def queue_run(
        self,
        *,
        definition_id: int,
        branch: str,
        variables: dict[str, str],
    ) -> dict[str, Any]:
        body = {
            "definition": {"id": definition_id},
            "sourceBranch": branch,
            "variables": {name: {"value": value} for name, value in variables.items()},
        }
        return self._request_json(
            "POST",
            "build/builds",
            {"api-version": self.api_version},
            body,
        )

    def _request_json(
        self,
        method: str,
        path: str,
        query: dict[str, str],
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        project = urllib.parse.quote(self.project, safe="")
        url = f"{self.organization}/{project}/_apis/{path}?{urllib.parse.urlencode(query)}"
        payload = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(url, data=payload, method=method)
        request.add_header("Authorization", f"Bearer {self.token}")
        request.add_header("Accept", "application/json")
        if payload is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                response_body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Azure DevOps API {method} {path} failed: HTTP {exc.code}: {error_body}") from exc
        return json.loads(response_body) if response_body else {}


def retry_failed_pipelines(
    *,
    client: AzureDevOpsClient,
    pipeline_names: list[str],
    branch: str,
    release_build_id: str,
    release_build_number: str,
    release_source_version: str,
) -> list[RetryDecision]:
    decisions: list[RetryDecision] = []
    for pipeline_name in pipeline_names:
        definition_id = client.get_definition_id(pipeline_name)
        latest_run = client.get_latest_run(definition_id, branch)
        if latest_run is None:
            decisions.append(
                RetryDecision(
                    pipeline_name=pipeline_name,
                    definition_id=definition_id,
                    action="skipped",
                    reason=f"no runs found on {branch}",
                )
            )
            continue

        run_id = _optional_int(latest_run.get("id"))
        status = str(latest_run.get("status") or "")
        result = str(latest_run.get("result") or "")
        if status != "completed":
            decisions.append(
                RetryDecision(
                    pipeline_name=pipeline_name,
                    definition_id=definition_id,
                    action="skipped",
                    reason=f"latest run {run_id} is {status or 'unknown'}, not completed",
                    latest_run_id=run_id,
                )
            )
            continue
        if result != "failed":
            decisions.append(
                RetryDecision(
                    pipeline_name=pipeline_name,
                    definition_id=definition_id,
                    action="skipped",
                    reason=f"latest completed run {run_id} result is {result or 'unknown'}",
                    latest_run_id=run_id,
                )
            )
            continue

        queued_run = client.queue_run(
            definition_id=definition_id,
            branch=branch,
            variables={
                "RETRIED_BY_CONTRACTS_RELEASE_BUILD_ID": release_build_id,
                "RETRIED_BY_CONTRACTS_RELEASE_BUILD_NUMBER": release_build_number,
                "RETRIED_BY_CONTRACTS_RELEASE_SOURCE_VERSION": release_source_version,
                "RETRIED_FAILED_RUN_ID": str(run_id or ""),
            },
        )
        decisions.append(
            RetryDecision(
                pipeline_name=pipeline_name,
                definition_id=definition_id,
                action="queued",
                reason=f"latest completed run {run_id} failed",
                latest_run_id=run_id,
                queued_run_id=_optional_int(queued_run.get("id")),
            )
        )
    return decisions


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Queue one retry for downstream Azure Pipelines whose latest main run failed."
    )
    parser.add_argument("--organization", default=os.environ.get("SYSTEM_COLLECTIONURI"))
    parser.add_argument("--project", default=os.environ.get("SYSTEM_TEAMPROJECT"))
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--api-version", default="7.1")
    parser.add_argument("--pipeline", dest="pipelines", action="append", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    token = os.environ.get("SYSTEM_ACCESSTOKEN")
    organization = args.organization
    project = args.project
    if not token:
        raise SystemExit("SYSTEM_ACCESSTOKEN is required to queue downstream pipeline retries.")
    if not organization:
        raise SystemExit("Azure DevOps organization URL is required.")
    if not project:
        raise SystemExit("Azure DevOps project is required.")

    client = RestAzureDevOpsClient(
        organization=organization,
        project=project,
        token=token,
        api_version=args.api_version,
    )
    decisions = retry_failed_pipelines(
        client=client,
        pipeline_names=list(args.pipelines),
        branch=args.branch,
        release_build_id=os.environ.get("BUILD_BUILDID", ""),
        release_build_number=os.environ.get("BUILD_BUILDNUMBER", ""),
        release_source_version=os.environ.get("BUILD_SOURCEVERSION", ""),
    )
    for decision in decisions:
        print(
            "pipeline={pipeline} definition={definition} action={action} "
            "latest_run={latest} queued_run={queued} reason={reason}".format(
                pipeline=decision.pipeline_name,
                definition=decision.definition_id,
                action=decision.action,
                latest=decision.latest_run_id or "",
                queued=decision.queued_run_id or "",
                reason=decision.reason,
            )
        )
    return 0


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) else None


if __name__ == "__main__":
    raise SystemExit(main())
