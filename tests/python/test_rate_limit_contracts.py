from __future__ import annotations

from asset_allocation_contracts.rate_limits import (
    RateLimitPolicyConfig,
    RateLimitPolicyUpsertRequest,
    RateLimitThrottleSample,
    RateLimitUsageBucket,
    RateLimitUsageView,
)


def test_rate_limit_policy_normalizes_operations_and_defaults_burst() -> None:
    payload = RateLimitPolicyUpsertRequest.model_validate(
        {
            "name": " system_default ",
            "description": " Default rate limits ",
            "status": "active",
            "intendedUse": "production_candidate",
            "thesis": " Protect upstream quotas ",
            "whatToMonitor": [" 429 spikes ", " queue pressure ", ""],
            "config": {
                "rules": [
                    {
                        "provider": "alpha_vantage",
                        "operation": "  time_series_daily  ",
                        "windowSeconds": 60,
                        "maxRequests": 5,
                        "maxConcurrency": 1,
                        "cooldownSeconds": 30,
                        "backgroundMaxWaitMs": 1_000,
                    }
                ]
            },
        }
    )

    rule = payload.config.rules[0]
    assert payload.name == "system_default"
    assert payload.description == "Default rate limits"
    assert payload.thesis == "Protect upstream quotas"
    assert payload.whatToMonitor == ["429 spikes", "queue pressure"]
    assert rule.operation == "time_series_daily"
    assert rule.burstRequests == 5


def test_rate_limit_policy_rejects_duplicate_provider_operation_pairs() -> None:
    try:
        RateLimitPolicyConfig.model_validate(
            {
                "rules": [
                    {
                        "provider": "quiver",
                        "operation": "congress_trading",
                        "windowSeconds": 60,
                        "maxRequests": 60,
                        "burstRequests": 60,
                        "maxConcurrency": 4,
                        "cooldownSeconds": 0,
                        "backgroundMaxWaitMs": 0,
                    },
                    {
                        "provider": "quiver",
                        "operation": " congress_trading ",
                        "windowSeconds": 120,
                        "maxRequests": 90,
                        "burstRequests": 90,
                        "maxConcurrency": 4,
                        "cooldownSeconds": 15,
                        "backgroundMaxWaitMs": 500,
                    },
                ]
            }
        )
    except Exception as exc:
        assert "Duplicate rate-limit rule" in str(exc)
    else:
        raise AssertionError("Expected duplicate provider/operation rules to fail validation.")


def test_rate_limit_rule_rejects_burst_below_window_budget() -> None:
    try:
        RateLimitPolicyConfig.model_validate(
            {
                "rules": [
                    {
                        "provider": "openai_responses",
                        "operation": "responses_create",
                        "windowSeconds": 60,
                        "maxRequests": 30,
                        "burstRequests": 10,
                        "maxConcurrency": 8,
                    }
                ]
            }
        )
    except Exception as exc:
        assert "burstRequests" in str(exc)
    else:
        raise AssertionError("Expected burstRequests below maxRequests to fail validation.")


def test_rate_limit_usage_contracts_capture_operator_view() -> None:
    bucket = RateLimitUsageBucket.model_validate(
        {
            "provider": "alpha_vantage",
            "operation": " time_series_daily ",
            "windowSeconds": 60,
            "maxRequests": 5,
            "burstRequests": 5,
            "maxConcurrency": 1,
            "cooldownSeconds": 30,
            "availableTokens": 2.5,
            "tokenFillPct": 50,
            "activeConcurrency": 0,
            "allowCount": 11,
            "denyCount": 2,
            "cooldownCount": 1,
            "upstreamThrottleCount": 0,
            "nearLimit": True,
        }
    )
    sample = RateLimitThrottleSample.model_validate(
        {
            "observedAt": "2026-05-30T12:00:00Z",
            "provider": "alpha_vantage",
            "operation": "time_series_daily",
            "workload": "interactive",
            "reason": "local_rate_limit",
            "retryAfterMs": 30_000,
            "policyName": " system_default ",
            "policyVersion": 1,
            "message": " Burst exhausted ",
        }
    )
    view = RateLimitUsageView.model_validate(
        {
            "policyName": "system_default",
            "policyVersion": 1,
            "generatedAt": "2026-05-30T12:00:01Z",
            "buckets": [bucket.model_dump(mode="json")],
            "throttleSamples": [sample.model_dump(mode="json")],
            "warnings": [" snapshot is process-local ", ""],
        }
    )

    assert bucket.operation == "time_series_daily"
    assert sample.policyName == "system_default"
    assert sample.message == "Burst exhausted"
    assert view.warnings == ["snapshot is process-local"]
    assert view.throttleSamples[0].reason == "local_rate_limit"
