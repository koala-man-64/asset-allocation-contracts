from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from asset_allocation_contracts.regime import RegimeCode
from asset_allocation_contracts.strategy import ConfigIdentity, ConfigReference, StrategyConfig


AgentWorkflowScope = Literal["research", "recommendation", "paper_preview"]
AgentRole = Literal[
    "alpha_research",
    "portfolio_manager",
    "risk_reviewer",
    "execution_specialist",
    "critic",
]
AgentWorldview = Literal[
    "momentum",
    "quality",
    "value",
    "growth",
    "mean_reversion",
    "event_driven",
    "macro",
    "sentiment",
    "volatility",
    "liquidity",
]
AgentRiskBand = Literal["conservative", "balanced", "aggressive"]
AgentTurnoverBand = Literal["low", "medium", "high"]
AgentClampStatus = Literal["not_clamped", "clamped", "blocked"]
AgentResolutionValidationStatus = Literal["valid", "warning", "blocked"]


class AgentWorldviewWeight(BaseModel):
    model_config = ConfigDict(extra="forbid")

    worldview: AgentWorldview
    weight: float = Field(..., gt=0)


class AgentBehaviorTraits(BaseModel):
    model_config = ConfigDict(extra="forbid")

    riskAppetite: float = Field(default=0.5, ge=0.0, le=1.0)
    lossAversion: float = Field(default=0.5, ge=0.0, le=1.0)
    patience: float = Field(default=0.5, ge=0.0, le=1.0)
    conviction: float = Field(default=0.5, ge=0.0, le=1.0)
    concentrationTolerance: float = Field(default=0.5, ge=0.0, le=1.0)
    turnoverTolerance: float = Field(default=0.5, ge=0.0, le=1.0)
    recencyBias: float = Field(default=0.5, ge=0.0, le=1.0)
    contrarianBias: float = Field(default=0.0, ge=-1.0, le=1.0)


class AgentEvidencePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    minimumConfidence: float = Field(default=0.6, ge=0.0, le=1.0)
    minimumIndependentSignals: int = Field(default=1, ge=1)
    requireRankingSupport: bool = True
    requireRegimeSupport: bool = False
    requireLiquiditySupport: bool = True
    maxContradictorySignals: int | None = Field(default=None, ge=0)


class AgentRegimePreference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preferredRegimes: list[RegimeCode] = Field(default_factory=list)
    blockedRegimes: list[RegimeCode] = Field(default_factory=list)
    honorModelHalt: bool = True
    blockWhenUnclassified: bool = True

    @field_validator("preferredRegimes", "blockedRegimes")
    @classmethod
    def dedupe_regimes(cls, value: list[RegimeCode]) -> list[RegimeCode]:
        seen: set[str] = set()
        normalized: list[RegimeCode] = []
        for item in value or []:
            code = str(item or "").strip()
            if code and code not in seen:
                seen.add(code)
                normalized.append(item)
        return normalized

    @model_validator(mode="after")
    def validate_rule_sets(self) -> "AgentRegimePreference":
        overlap = sorted(set(self.preferredRegimes).intersection(self.blockedRegimes))
        if overlap:
            joined = ", ".join(overlap)
            raise ValueError(f"Agent regimes cannot both prefer and block: {joined}.")
        return self


class AgentProfileConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: AgentRole
    maxWorkflowScope: AgentWorkflowScope = "research"
    traits: AgentBehaviorTraits = Field(default_factory=AgentBehaviorTraits)
    worldviewWeights: list[AgentWorldviewWeight] = Field(..., min_length=1)
    regimePreference: AgentRegimePreference = Field(default_factory=AgentRegimePreference)
    evidencePolicy: AgentEvidencePolicy = Field(default_factory=AgentEvidencePolicy)
    notes: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: object) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("notes must be a list.")
        normalized: list[str] = []
        for item in value:
            text = str(item or "").strip()
            if text:
                if len(text) > 1000:
                    raise ValueError("Agent profile notes must be 1000 characters or less.")
                normalized.append(text)
        return normalized

    @model_validator(mode="after")
    def validate_worldview_weights(self) -> "AgentProfileConfig":
        seen: set[str] = set()
        duplicates: list[str] = []
        for item in self.worldviewWeights:
            if item.worldview in seen and item.worldview not in duplicates:
                duplicates.append(item.worldview)
            seen.add(item.worldview)
        if duplicates:
            joined = ", ".join(sorted(duplicates))
            raise ValueError(f"worldviewWeights must be unique by worldview: {joined}.")
        return self


class AgentProfilePreset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity: ConfigIdentity
    config: AgentProfileConfig


class AgentStrategyBinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agentProfileRef: ConfigReference
    baseStrategyRef: ConfigReference
    compilerVersion: int = Field(default=1, ge=1)
    rankingRefsByWorldview: dict[AgentWorldview, ConfigReference] = Field(default_factory=dict)
    riskPolicyRefsByBand: dict[AgentRiskBand, ConfigReference] = Field(default_factory=dict)
    rebalancePolicyRefsByBand: dict[AgentTurnoverBand, ConfigReference] = Field(default_factory=dict)
    exitPolicyRefsByBand: dict[AgentRiskBand, ConfigReference] = Field(default_factory=dict)
    allowRankingOverride: bool = True
    allowRiskPolicyOverride: bool = True
    allowRebalanceOverride: bool = True
    allowExitPolicyOverride: bool = True
    minTopN: int = Field(default=5, ge=1)
    maxTopN: int = Field(default=100, ge=1)
    minHoldingPeriod: int = Field(default=1, ge=1)
    maxHoldingPeriod: int = Field(default=252, ge=1)
    minLookbackWindow: int = Field(default=5, ge=1)
    maxLookbackWindow: int = Field(default=504, ge=1)
    maxPositionSizePct: float | None = Field(default=None, gt=0.0, le=100.0)
    allowedRegimes: list[RegimeCode] = Field(default_factory=list)
    blockedRegimes: list[RegimeCode] = Field(default_factory=list)

    @field_validator("allowedRegimes", "blockedRegimes")
    @classmethod
    def dedupe_regimes(cls, value: list[RegimeCode]) -> list[RegimeCode]:
        seen: set[str] = set()
        normalized: list[RegimeCode] = []
        for item in value or []:
            code = str(item or "").strip()
            if code and code not in seen:
                seen.add(code)
                normalized.append(item)
        return normalized

    @model_validator(mode="after")
    def validate_constraints(self) -> "AgentStrategyBinding":
        if self.minTopN > self.maxTopN:
            raise ValueError("minTopN cannot exceed maxTopN.")
        if self.minHoldingPeriod > self.maxHoldingPeriod:
            raise ValueError("minHoldingPeriod cannot exceed maxHoldingPeriod.")
        if self.minLookbackWindow > self.maxLookbackWindow:
            raise ValueError("minLookbackWindow cannot exceed maxLookbackWindow.")
        overlap = sorted(set(self.allowedRegimes).intersection(self.blockedRegimes))
        if overlap:
            joined = ", ".join(overlap)
            raise ValueError(f"Agent binding regimes cannot both allow and block: {joined}.")
        return self


class AgentAppliedConfigChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(..., min_length=1, max_length=256)
    previousValue: Any | None = None
    newValue: Any | None = None
    reasonCode: str = Field(..., min_length=1, max_length=128)
    reason: str = Field(default="", max_length=1000)
    clampStatus: AgentClampStatus = "not_clamped"

    @field_validator("path", "reasonCode", "reason", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        if value is None:
            return value
        return str(value).strip()


class AgentStrategyResolutionPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agentProfileRef: ConfigReference
    baseStrategyRef: ConfigReference
    resolvedStrategy: StrategyConfig
    appliedChanges: list[AgentAppliedConfigChange] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list, max_length=50)
    agentProfileSnapshotHash: str = Field(..., min_length=16, max_length=128)
    baseStrategySnapshotHash: str = Field(..., min_length=16, max_length=128)
    bindingHash: str = Field(..., min_length=16, max_length=128)
    resolvedStrategyHash: str = Field(..., min_length=16, max_length=128)
    compilerVersion: int = Field(default=1, ge=1)
    validationStatus: AgentResolutionValidationStatus = "valid"

    @field_validator(
        "agentProfileSnapshotHash",
        "baseStrategySnapshotHash",
        "bindingHash",
        "resolvedStrategyHash",
        mode="before",
    )
    @classmethod
    def normalize_hash(cls, value: object) -> object:
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
        normalized: list[str] = []
        for item in value:
            text = str(item or "").strip()
            if text:
                if len(text) > 1000:
                    raise ValueError("Agent resolution warnings must be 1000 characters or less.")
                normalized.append(text)
        return normalized
