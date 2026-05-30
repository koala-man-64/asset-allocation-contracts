from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from asset_allocation_contracts.strategy import (
    ConfigIdentity,
    ReusableConfigIntendedUse,
    ReusableConfigStatus,
    ReusableConfigSummaryBase,
)

RateLimitProvider = Literal[
    "alpha_vantage",
    "quiver",
    "openai_responses",
    "alpaca",
    "etrade",
    "schwab",
    "kalshi",
]
RateLimitQuotaUnit = Literal["request", "token_1k"]
RateLimitWorkload = Literal["interactive", "background"]
RateLimitThrottleReason = Literal[
    "local_rate_limit",
    "local_concurrency_limit",
    "local_cooldown",
    "upstream_429",
]


class RateLimitRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: RateLimitProvider
    operation: str = Field(..., min_length=1, max_length=128)
    windowSeconds: int = Field(..., ge=1, le=3600)
    maxRequests: int = Field(..., ge=1, le=1_000_000)
    burstRequests: int | None = Field(default=None, ge=1, le=1_000_000)
    maxConcurrency: int = Field(default=1, ge=1, le=10_000)
    cooldownSeconds: int = Field(default=0, ge=0, le=86_400)
    backgroundMaxWaitMs: int = Field(default=0, ge=0, le=3_600_000)
    quotaUnit: RateLimitQuotaUnit = "request"

    @field_validator("operation", mode="before")
    @classmethod
    def normalize_operation(cls, value: object) -> object:
        if value is None:
            return value
        return str(value).strip().lower()

    @model_validator(mode="after")
    def validate_rule(self) -> "RateLimitRule":
        if self.burstRequests is None:
            self.burstRequests = self.maxRequests
        if self.burstRequests < self.maxRequests:
            raise ValueError("burstRequests must be greater than or equal to maxRequests.")
        return self


class RateLimitPolicyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rules: list[RateLimitRule] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_unique_rules(self) -> "RateLimitPolicyConfig":
        seen: set[tuple[str, str]] = set()
        for rule in self.rules:
            key = (rule.provider, rule.operation)
            if key in seen:
                raise ValueError(
                    f"Duplicate rate-limit rule for provider '{rule.provider}' operation '{rule.operation}'."
                )
            seen.add(key)
        return self


class RateLimitPolicySummary(ReusableConfigSummaryBase):
    ruleCount: int = Field(default=0, ge=0)
    providers: list[RateLimitProvider] = Field(default_factory=list)

    @field_validator("providers", mode="before")
    @classmethod
    def normalize_providers(cls, value: object) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("providers must be a list.")
        normalized: list[str] = []
        for item in value:
            text = str(item or "").strip().lower()
            if text and text not in normalized:
                normalized.append(text)
        return normalized


class RateLimitPolicyRevision(ConfigIdentity):
    model_config = ConfigDict(extra="forbid")

    config: RateLimitPolicyConfig
    configHash: str | None = None
    createdAt: datetime | None = None
    createdBy: str | None = None


class RateLimitPolicyDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy: RateLimitPolicySummary
    activeRevision: RateLimitPolicyRevision | None = None
    revisions: list[RateLimitPolicyRevision] = Field(default_factory=list)


class RateLimitPolicyUpsertRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=128)
    description: str = Field(default="", max_length=2048)
    status: ReusableConfigStatus = "active"
    intendedUse: ReusableConfigIntendedUse = "research"
    thesis: str = Field(default="", max_length=4096)
    whatToMonitor: list[str] = Field(default_factory=list)
    config: RateLimitPolicyConfig

    @field_validator("name", "description", "thesis", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        if value is None:
            return value
        return str(value).strip()

    @field_validator("whatToMonitor", mode="before")
    @classmethod
    def normalize_monitoring_notes(cls, value: object) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("whatToMonitor must be a list.")
        return [str(item).strip() for item in value if str(item).strip()]


class RateLimitUsageBucket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: RateLimitProvider
    operation: str = Field(..., min_length=1, max_length=128)
    windowSeconds: int = Field(..., ge=1, le=3600)
    maxRequests: int = Field(..., ge=1, le=1_000_000)
    burstRequests: int = Field(..., ge=1, le=1_000_000)
    maxConcurrency: int = Field(..., ge=1, le=10_000)
    cooldownSeconds: int = Field(..., ge=0, le=86_400)
    quotaUnit: RateLimitQuotaUnit = "request"
    availableTokens: float = Field(default=0.0, ge=0.0)
    tokenFillPct: float = Field(default=0.0, ge=0.0, le=100.0)
    activeConcurrency: int = Field(default=0, ge=0)
    allowCount: int = Field(default=0, ge=0)
    denyCount: int = Field(default=0, ge=0)
    cooldownCount: int = Field(default=0, ge=0)
    upstreamThrottleCount: int = Field(default=0, ge=0)
    lastDecisionAt: datetime | None = None
    lastDeniedAt: datetime | None = None
    lastCooldownAt: datetime | None = None
    nearLimit: bool = False

    @field_validator("operation", mode="before")
    @classmethod
    def normalize_usage_operation(cls, value: object) -> object:
        if value is None:
            return value
        return str(value).strip().lower()


class RateLimitThrottleSample(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observedAt: datetime
    provider: RateLimitProvider
    operation: str = Field(..., min_length=1, max_length=128)
    workload: RateLimitWorkload
    reason: RateLimitThrottleReason
    retryAfterMs: int = Field(..., ge=0, le=3_600_000)
    quotaUnit: RateLimitQuotaUnit = "request"
    policyName: str | None = Field(default=None, min_length=1, max_length=128)
    policyVersion: int | None = Field(default=None, ge=1)
    message: str | None = Field(default=None, max_length=512)

    @field_validator("operation", "policyName", "message", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if value is None:
            return None
        text = str(value).strip()
        return text or None


class RateLimitUsageView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policyName: str = Field(..., min_length=1, max_length=128)
    policyVersion: int = Field(..., ge=1)
    generatedAt: datetime
    buckets: list[RateLimitUsageBucket] = Field(default_factory=list)
    throttleSamples: list[RateLimitThrottleSample] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("policyName", mode="before")
    @classmethod
    def normalize_policy_name(cls, value: object) -> object:
        if value is None:
            return value
        return str(value).strip()

    @field_validator("warnings", mode="before")
    @classmethod
    def normalize_warnings(cls, value: object) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("warnings must be a list.")
        return [str(item).strip() for item in value if str(item).strip()]
