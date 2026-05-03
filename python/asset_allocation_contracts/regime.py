from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

RegimeCode = Literal[
    "trending_up",
    "trending_down",
    "mean_reverting",
    "low_volatility",
    "high_volatility",
    "liquidity_stress",
    "macro_alignment",
    "unclassified",
]
RegimeSignalState = Literal["active", "inactive", "insufficient_data"]
RegimeTransitionType = Literal["entered", "exited"]
RegimePolicyMode = Literal["observe_only"]
RegimeMetricComparison = Literal["gte", "lte", "between", "bool_true"]
TrendState = Literal["positive", "negative", "near_zero"]
CurveState = Literal["contango", "flat", "inverted"]

DEFAULT_REGIME_MODEL_NAME = "default-regime"
DEFAULT_HALT_REASON = "high_volatility_and_stress_cluster"
CANONICAL_DEFAULT_REGIME_VERSION = 3
DEFAULT_REGIME_ACTIVATION_THRESHOLD = 0.60
DEFAULT_REGIME_DISPLAY_NAMES: dict[RegimeCode, str] = {
    "trending_up": "Trending (Up)",
    "trending_down": "Trending (Down)",
    "mean_reverting": "Mean-Reverting",
    "low_volatility": "Low Volatility",
    "high_volatility": "High Volatility",
    "liquidity_stress": "Liquidity Regime",
    "macro_alignment": "Global/Macro Regime",
    "unclassified": "Unclassified",
}
_LEGACY_DEFAULT_REGIME_POLICY_FIELDS = frozenset(
    {
        "targetGrossExposureByRegime",
        "blockOnTransition",
        "blockOnUnclassified",
        "honorHaltFlag",
        "onBlocked",
    }
)


class RegimeMetricRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric: str = Field(..., min_length=1, max_length=128)
    comparison: RegimeMetricComparison
    lower: float | None = None
    upper: float | None = None
    description: str = Field(default="", max_length=512)

    @model_validator(mode="after")
    def validate_thresholds(self) -> "RegimeMetricRule":
        if self.comparison in {"gte", "lte"} and self.lower is None:
            raise ValueError(f"{self.metric}: {self.comparison} requires lower.")
        if self.comparison == "between":
            if self.lower is None or self.upper is None:
                raise ValueError(f"{self.metric}: between requires lower and upper.")
            if float(self.upper) < float(self.lower):
                raise ValueError(f"{self.metric}: upper must be >= lower.")
        if self.comparison == "bool_true" and (self.lower is not None or self.upper is not None):
            raise ValueError(f"{self.metric}: bool_true does not accept thresholds.")
        return self


class RegimeSignalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    displayName: str = Field(..., min_length=1, max_length=128)
    requiredMetrics: list[str] = Field(default_factory=list)
    rules: list[RegimeMetricRule] = Field(default_factory=list)


class RegimePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modelName: str = Field(default=DEFAULT_REGIME_MODEL_NAME, min_length=1, max_length=128)
    modelVersion: int | None = Field(default=None, ge=1)
    mode: RegimePolicyMode = "observe_only"

    @model_validator(mode="before")
    @classmethod
    def reject_legacy_default_regime_fields(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value
        model_name = str(value.get("modelName") or DEFAULT_REGIME_MODEL_NAME).strip() or DEFAULT_REGIME_MODEL_NAME
        if model_name != DEFAULT_REGIME_MODEL_NAME:
            return value

        legacy_fields = sorted(_LEGACY_DEFAULT_REGIME_POLICY_FIELDS.intersection(value.keys()))
        if legacy_fields:
            joined = ", ".join(legacy_fields)
            raise ValueError(
                "default-regime policy no longer accepts legacy fields: "
                f"{joined}. Use mode='observe_only'."
            )
        return value

    @model_validator(mode="after")
    def normalize_model_name(self) -> "RegimePolicy":
        self.modelName = str(self.modelName or "").strip() or DEFAULT_REGIME_MODEL_NAME
        return self


class RegimePolicyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modelName: str = Field(default=DEFAULT_REGIME_MODEL_NAME, min_length=1, max_length=128)
    modelVersion: int | None = Field(default=None, ge=1)
    mode: RegimePolicyMode = "observe_only"

    @model_validator(mode="after")
    def normalize_model_name(self) -> "RegimePolicyConfig":
        self.modelName = str(self.modelName or "").strip() or DEFAULT_REGIME_MODEL_NAME
        return self

    def resolved_policy(self) -> RegimePolicy:
        return RegimePolicy(modelName=self.modelName, modelVersion=self.modelVersion, mode=self.mode)


class RegimePolicyConfigSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=128)
    description: str = Field(default="", max_length=2048)
    version: int = Field(default=1, ge=1)
    archived: bool = False
    usageCount: int = Field(default=0, ge=0)
    modelName: str = Field(default=DEFAULT_REGIME_MODEL_NAME, min_length=1, max_length=128)
    modelVersion: int | None = Field(default=None, ge=1)
    mode: RegimePolicyMode = "observe_only"
    updatedAt: datetime | None = None


class RegimePolicyConfigRevision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=128)
    version: int = Field(..., ge=1)
    description: str = Field(default="", max_length=2048)
    config: RegimePolicyConfig
    configHash: str | None = None
    createdAt: datetime | None = None
    createdBy: str | None = None


class RegimePolicyConfigDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy: RegimePolicyConfigSummary
    activeRevision: RegimePolicyConfigRevision | None = None
    revisions: list[RegimePolicyConfigRevision] = Field(default_factory=list)


class RegimePolicyConfigUpsertRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=128)
    description: str = Field(default="", max_length=2048)
    config: RegimePolicyConfig


class RegimeModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activationThreshold: float = Field(default=DEFAULT_REGIME_ACTIVATION_THRESHOLD, ge=0.0, le=1.0)
    signalConfigs: dict[RegimeCode, RegimeSignalConfig] = Field(
        default_factory=lambda: canonical_default_regime_signal_configs()
    )
    haltVixThreshold: float = 32.0
    haltVixStreakDays: int = Field(default=2, ge=1)


class RegimeSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    regime_code: RegimeCode
    display_name: str = Field(..., min_length=1, max_length=128)
    signal_state: RegimeSignalState
    score: float = Field(..., ge=0.0, le=1.0)
    activation_threshold: float = Field(..., ge=0.0, le=1.0)
    is_active: bool
    matched_rule_id: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)


class RegimeSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of_date: date
    effective_from_date: date
    model_name: str
    model_version: int
    signals: list[RegimeSignal] = Field(default_factory=list)
    active_regimes: list[RegimeCode] = Field(default_factory=list)
    halt_flag: bool
    halt_reason: str | None = None
    computed_at: datetime | None = None


class RegimeInputRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of_date: date
    metric_values: dict[str, Any] = Field(default_factory=dict)
    inputs_complete_flag: bool
    computed_at: datetime | None = None


class RegimeTransitionRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_name: str
    model_version: int
    effective_from_date: date
    regime_code: RegimeCode
    transition_type: RegimeTransitionType
    prior_score: float | None = Field(default=None, ge=0.0, le=1.0)
    new_score: float | None = Field(default=None, ge=0.0, le=1.0)
    activation_threshold: float = Field(..., ge=0.0, le=1.0)
    trigger_rule_id: str | None = None
    computed_at: datetime | None = None


class RegimeModelSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str = ""
    version: int
    updated_at: datetime | None = None
    active_version: int | None = None
    activated_at: datetime | None = None
    activated_by: str | None = None


class RegimeModelRevision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    version: int
    description: str = ""
    config: RegimeModelConfig
    status: str | None = None
    config_hash: str | None = None
    published_at: datetime | None = None
    created_at: datetime | None = None
    activated_at: datetime | None = None
    activated_by: str | None = None


class RegimeModelDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: RegimeModelSummary
    activeRevision: RegimeModelRevision | None = None
    revisions: list[RegimeModelRevision] = Field(default_factory=list)
    latest: RegimeSnapshot | None = None


def canonical_default_regime_signal_configs() -> dict[RegimeCode, RegimeSignalConfig]:
    return {
        "trending_up": RegimeSignalConfig(
            displayName=DEFAULT_REGIME_DISPLAY_NAMES["trending_up"],
            requiredMetrics=["spy_above_sma_200", "qqq_above_sma_200", "spy_return_20d"],
            rules=[
                RegimeMetricRule(
                    metric="spy_above_sma_200",
                    comparison="bool_true",
                    description="Broad U.S. equity index is above its 200-day average.",
                ),
                RegimeMetricRule(
                    metric="qqq_above_sma_200",
                    comparison="bool_true",
                    description="Nasdaq-100 proxy is above its 200-day average.",
                ),
                RegimeMetricRule(
                    metric="spy_return_20d",
                    comparison="gte",
                    lower=0.02,
                    description="Broad market 20-day return is at least +2%.",
                ),
            ],
        ),
        "trending_down": RegimeSignalConfig(
            displayName=DEFAULT_REGIME_DISPLAY_NAMES["trending_down"],
            requiredMetrics=["spy_below_sma_200", "qqq_below_sma_200", "spy_return_20d"],
            rules=[
                RegimeMetricRule(
                    metric="spy_below_sma_200",
                    comparison="bool_true",
                    description="Broad U.S. equity index is below its 200-day average.",
                ),
                RegimeMetricRule(
                    metric="qqq_below_sma_200",
                    comparison="bool_true",
                    description="Nasdaq-100 proxy is below its 200-day average.",
                ),
                RegimeMetricRule(
                    metric="spy_return_20d",
                    comparison="lte",
                    lower=-0.02,
                    description="Broad market 20-day return is at most -2%.",
                ),
            ],
        ),
        "mean_reverting": RegimeSignalConfig(
            displayName=DEFAULT_REGIME_DISPLAY_NAMES["mean_reverting"],
            requiredMetrics=["rsi_14d", "bb_width_20d", "abs_spy_return_20d"],
            rules=[
                RegimeMetricRule(
                    metric="rsi_14d",
                    comparison="between",
                    lower=30.0,
                    upper=70.0,
                    description="RSI is in the neutral mean-reversion corridor.",
                ),
                RegimeMetricRule(
                    metric="bb_width_20d",
                    comparison="lte",
                    lower=0.18,
                    description="Bollinger band width remains compressed.",
                ),
                RegimeMetricRule(
                    metric="abs_spy_return_20d",
                    comparison="lte",
                    lower=0.03,
                    description="The broad market is not in a strong directional burst.",
                ),
            ],
        ),
        "low_volatility": RegimeSignalConfig(
            displayName=DEFAULT_REGIME_DISPLAY_NAMES["low_volatility"],
            requiredMetrics=["vix_spot_close", "atr_14d_pct_of_close", "bb_width_20d"],
            rules=[
                RegimeMetricRule(
                    metric="vix_spot_close",
                    comparison="lte",
                    lower=15.0,
                    description="VIX is in the low-volatility zone.",
                ),
                RegimeMetricRule(
                    metric="atr_14d_pct_of_close",
                    comparison="lte",
                    lower=0.03,
                    description="ATR is narrow relative to price.",
                ),
                RegimeMetricRule(
                    metric="bb_width_20d",
                    comparison="lte",
                    lower=0.12,
                    description="Bollinger bands remain narrow.",
                ),
            ],
        ),
        "high_volatility": RegimeSignalConfig(
            displayName=DEFAULT_REGIME_DISPLAY_NAMES["high_volatility"],
            requiredMetrics=["vix_spot_close", "atr_14d_pct_of_close", "gap_atr"],
            rules=[
                RegimeMetricRule(
                    metric="vix_spot_close",
                    comparison="gte",
                    lower=25.0,
                    description="VIX is elevated relative to normal conditions.",
                ),
                RegimeMetricRule(
                    metric="atr_14d_pct_of_close",
                    comparison="gte",
                    lower=0.04,
                    description="ATR has expanded materially relative to price.",
                ),
                RegimeMetricRule(
                    metric="gap_atr",
                    comparison="gte",
                    lower=0.50,
                    description="Overnight or opening gaps are large versus ATR.",
                ),
            ],
        ),
        "liquidity_stress": RegimeSignalConfig(
            displayName=DEFAULT_REGIME_DISPLAY_NAMES["liquidity_stress"],
            requiredMetrics=["volume_pct_rank_252d", "gap_atr", "hy_oas_z_20d"],
            rules=[
                RegimeMetricRule(
                    metric="volume_pct_rank_252d",
                    comparison="lte",
                    lower=0.20,
                    description="Trading volume sits in the bottom quintile of the last year.",
                ),
                RegimeMetricRule(
                    metric="gap_atr",
                    comparison="gte",
                    lower=0.75,
                    description="Gap size indicates stressed execution conditions.",
                ),
                RegimeMetricRule(
                    metric="hy_oas_z_20d",
                    comparison="gte",
                    lower=1.0,
                    description="High-yield spreads have widened versus the recent baseline.",
                ),
            ],
        ),
        "macro_alignment": RegimeSignalConfig(
            displayName=DEFAULT_REGIME_DISPLAY_NAMES["macro_alignment"],
            requiredMetrics=["global_equity_alignment", "rates_event_flag", "cross_asset_stress_alignment"],
            rules=[
                RegimeMetricRule(
                    metric="global_equity_alignment",
                    comparison="bool_true",
                    description="Global equity proxies are moving in the same direction.",
                ),
                RegimeMetricRule(
                    metric="rates_event_flag",
                    comparison="bool_true",
                    description="A rates or macro event flag is active.",
                ),
                RegimeMetricRule(
                    metric="cross_asset_stress_alignment",
                    comparison="bool_true",
                    description="Rates, credit, and volatility proxies are aligned.",
                ),
            ],
        ),
        "unclassified": RegimeSignalConfig(
            displayName=DEFAULT_REGIME_DISPLAY_NAMES["unclassified"],
            requiredMetrics=[],
            rules=[],
        ),
    }


def default_regime_display_name(regime_code: RegimeCode) -> str:
    return DEFAULT_REGIME_DISPLAY_NAMES[regime_code]


def default_regime_model_config() -> dict[str, Any]:
    return canonical_default_regime_model_config().model_dump(mode="json")


def canonical_default_regime_model_config() -> RegimeModelConfig:
    return RegimeModelConfig(
        activationThreshold=DEFAULT_REGIME_ACTIVATION_THRESHOLD,
        signalConfigs=canonical_default_regime_signal_configs(),
        haltVixThreshold=32.0,
        haltVixStreakDays=2,
    )


def canonical_default_regime_config_errors(
    config: RegimeModelConfig | Mapping[str, Any] | None,
) -> list[str]:
    cfg = config if isinstance(config, RegimeModelConfig) else RegimeModelConfig.model_validate(config or {})
    expected = canonical_default_regime_model_config()
    actual_dump = cfg.model_dump(mode="json")
    expected_dump = expected.model_dump(mode="json")
    errors: list[str] = []

    if actual_dump.get("activationThreshold") != expected_dump.get("activationThreshold"):
        errors.append(
            "activationThreshold must equal canonical value "
            f"{expected_dump['activationThreshold']!r}"
        )
    if actual_dump.get("haltVixThreshold") != expected_dump.get("haltVixThreshold"):
        errors.append(
            f"haltVixThreshold={actual_dump.get('haltVixThreshold')!r} must equal "
            f"canonical value {expected_dump['haltVixThreshold']!r}"
        )
    if actual_dump.get("haltVixStreakDays") != expected_dump.get("haltVixStreakDays"):
        errors.append(
            f"haltVixStreakDays={actual_dump.get('haltVixStreakDays')!r} must equal "
            f"canonical value {expected_dump['haltVixStreakDays']!r}"
        )

    actual_signal_configs = actual_dump.get("signalConfigs") or {}
    expected_signal_configs = expected_dump.get("signalConfigs") or {}
    if actual_signal_configs != expected_signal_configs:
        for regime_code in expected_signal_configs:
            if actual_signal_configs.get(regime_code) != expected_signal_configs.get(regime_code):
                errors.append(f"signalConfigs.{regime_code} must equal canonical default-regime rule set")
        for regime_code in actual_signal_configs:
            if regime_code not in expected_signal_configs:
                errors.append(f"signalConfigs.{regime_code} is not part of the canonical default-regime taxonomy")

    return errors


def validate_canonical_default_regime_config(
    config: RegimeModelConfig | Mapping[str, Any] | None,
) -> RegimeModelConfig:
    cfg = config if isinstance(config, RegimeModelConfig) else RegimeModelConfig.model_validate(config or {})
    errors = canonical_default_regime_config_errors(cfg)
    if errors:
        joined = "; ".join(errors)
        raise ValueError(f"default-regime must use canonical v3 semantics: {joined}")
    return cfg
