from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

RegimeCode = Literal[
    "trending_bull",
    "trending_bear",
    "choppy_mean_reversion",
    "high_vol",
    "unclassified",
]
RegimeStatus = Literal["confirmed", "transition", "unclassified"]
TrendState = Literal["positive", "negative", "near_zero"]
CurveState = Literal["contango", "flat", "inverted"]
RegimeBlockedAction = Literal["skip_entries", "skip_rebalance"]

DEFAULT_REGIME_MODEL_NAME = "default-regime"
DEFAULT_HALT_REASON = "vix_spot_close_gt_32_for_2_days"
CANONICAL_DEFAULT_REGIME_VERSION = 2
_CANONICAL_DEFAULT_REGIME_PRECEDENCE: list[RegimeCode] = [
    "high_vol",
    "trending_bear",
    "trending_bull",
    "choppy_mean_reversion",
    "unclassified",
]


class TargetGrossExposureByRegime(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trending_bull: float = Field(default=1.0, ge=0.0)
    trending_bear: float = Field(default=0.5, ge=0.0)
    choppy_mean_reversion: float = Field(default=0.75, ge=0.0)
    high_vol: float = Field(default=0.0, ge=0.0)
    unclassified: float = Field(default=0.0, ge=0.0)


class RegimePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modelName: str = Field(default=DEFAULT_REGIME_MODEL_NAME, min_length=1, max_length=128)
    targetGrossExposureByRegime: TargetGrossExposureByRegime = Field(
        default_factory=TargetGrossExposureByRegime
    )
    blockOnTransition: bool = True
    blockOnUnclassified: bool = True
    honorHaltFlag: bool = True
    onBlocked: RegimeBlockedAction = "skip_entries"

    @model_validator(mode="after")
    def normalize_model_name(self) -> "RegimePolicy":
        self.modelName = str(self.modelName or "").strip() or DEFAULT_REGIME_MODEL_NAME
        return self


class RegimeModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trendPositiveThreshold: float = 0.02
    trendNegativeThreshold: float = -0.02
    curveContangoThreshold: float = 0.50
    curveInvertedThreshold: float = -0.50
    highVolEnterThreshold: float = 28.0
    # Deprecated compatibility field. Canonical default-regime v2 disables the
    # transition band by matching the strict high-vol entry threshold.
    highVolExitThreshold: float = 28.0
    bearVolMin: float = 15.0
    bearVolMaxExclusive: float = 25.0
    bullVolMaxExclusive: float = 15.0
    choppyVolMin: float = 10.0
    choppyVolMaxExclusive: float = 18.0
    haltVixThreshold: float = 32.0
    haltVixStreakDays: int = Field(default=2, ge=1)
    precedence: list[RegimeCode] = Field(
        default_factory=lambda: list(_CANONICAL_DEFAULT_REGIME_PRECEDENCE)
    )


class RegimeSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of_date: date
    effective_from_date: date
    model_name: str
    model_version: int
    regime_code: RegimeCode
    regime_status: RegimeStatus
    matched_rule_id: str | None = None
    halt_flag: bool
    halt_reason: str | None = None
    spy_return_20d: float | None = None
    rvol_10d_ann: float | None = None
    vix_spot_close: float | None = None
    vix3m_close: float | None = None
    vix_slope: float | None = None
    trend_state: TrendState | None = None
    curve_state: CurveState | None = None
    vix_gt_32_streak: int | None = None
    computed_at: datetime | None = None


class RegimeInputRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of_date: date
    spy_close: float | None = None
    return_1d: float | None = None
    return_20d: float | None = None
    rvol_10d_ann: float | None = None
    vix_spot_close: float | None = None
    vix3m_close: float | None = None
    vix_slope: float | None = None
    trend_state: TrendState | None = None
    curve_state: CurveState | None = None
    vix_gt_32_streak: int | None = None
    inputs_complete_flag: bool
    computed_at: datetime | None = None


class RegimeTransitionRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_name: str
    model_version: int
    effective_from_date: date
    prior_regime_code: RegimeCode | None = None
    new_regime_code: RegimeCode
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


def default_regime_model_config() -> dict[str, Any]:
    return canonical_default_regime_model_config().model_dump(mode="json")


def canonical_default_regime_model_config() -> RegimeModelConfig:
    return RegimeModelConfig(
        trendPositiveThreshold=0.02,
        trendNegativeThreshold=-0.02,
        curveContangoThreshold=0.50,
        curveInvertedThreshold=-0.50,
        highVolEnterThreshold=28.0,
        highVolExitThreshold=28.0,
        bearVolMin=15.0,
        bearVolMaxExclusive=25.0,
        bullVolMaxExclusive=15.0,
        choppyVolMin=10.0,
        choppyVolMaxExclusive=18.0,
        haltVixThreshold=32.0,
        haltVixStreakDays=2,
        precedence=list(_CANONICAL_DEFAULT_REGIME_PRECEDENCE),
    )


def canonical_default_regime_config_errors(
    config: RegimeModelConfig | Mapping[str, Any] | None,
) -> list[str]:
    cfg = config if isinstance(config, RegimeModelConfig) else RegimeModelConfig.model_validate(config or {})
    expected = canonical_default_regime_model_config()
    errors: list[str] = []

    comparable_fields = (
        "trendPositiveThreshold",
        "trendNegativeThreshold",
        "curveContangoThreshold",
        "curveInvertedThreshold",
        "highVolEnterThreshold",
        "highVolExitThreshold",
        "bearVolMin",
        "bearVolMaxExclusive",
        "bullVolMaxExclusive",
        "choppyVolMin",
        "choppyVolMaxExclusive",
        "haltVixThreshold",
        "haltVixStreakDays",
    )
    for field_name in comparable_fields:
        actual = getattr(cfg, field_name)
        canonical = getattr(expected, field_name)
        if actual != canonical:
            errors.append(f"{field_name}={actual!r} must equal canonical value {canonical!r}")

    if list(cfg.precedence) != list(expected.precedence):
        errors.append(
            "precedence must equal canonical order "
            f"{list(expected.precedence)!r}"
        )
    return errors


def validate_canonical_default_regime_config(
    config: RegimeModelConfig | Mapping[str, Any] | None,
) -> RegimeModelConfig:
    cfg = config if isinstance(config, RegimeModelConfig) else RegimeModelConfig.model_validate(config or {})
    errors = canonical_default_regime_config_errors(cfg)
    if errors:
        joined = "; ".join(errors)
        raise ValueError(f"default-regime must use canonical v2 semantics: {joined}")
    return cfg
