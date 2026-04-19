from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

GovernmentSignalSeverity = Literal["low", "medium", "high", "critical"]
GovernmentSignalMappingStatus = Literal["pending_review", "mapped", "ignored"]
GovernmentSignalMappingAction = Literal["map", "ignore", "defer"]
GovernmentSignalAlertType = Literal["congress_trade", "contract_event", "composite"]
CongressTradeChamber = Literal["house", "senate", "joint", "unknown"]
CongressTradeRelationship = Literal["self", "spouse", "dependent_child", "joint", "unknown"]
CongressTradeType = Literal["purchase", "sale", "partial_sale", "exchange", "other"]
CongressTradeFilingStatus = Literal["new", "amended", "late", "unknown"]
GovernmentContractEventType = Literal[
    "opportunity",
    "award",
    "modification",
    "option_exercise",
    "obligation",
    "outlay",
    "termination",
    "cancellation",
    "protest",
    "other",
]


class CongressTradeEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(..., min_length=1, max_length=128)
    source_name: str = Field(..., min_length=1, max_length=64)
    source_event_key: str = Field(..., min_length=1, max_length=255)
    member_id: str | None = Field(default=None, min_length=1, max_length=64)
    member_name: str = Field(..., min_length=1, max_length=255)
    chamber: CongressTradeChamber = "unknown"
    party: str | None = Field(default=None, min_length=1, max_length=32)
    state: str | None = Field(default=None, min_length=1, max_length=16)
    district: str | None = Field(default=None, min_length=1, max_length=16)
    committee_names: list[str] = Field(default_factory=list)
    traded_at: datetime
    filed_at: datetime | None = None
    notified_at: datetime | None = None
    relationship_type: CongressTradeRelationship = "unknown"
    transaction_type: CongressTradeType
    filing_status: CongressTradeFilingStatus = "unknown"
    amendment_flag: bool = False
    late_filing_days: int | None = Field(default=None, ge=0)
    asset_name: str = Field(..., min_length=1, max_length=255)
    asset_description: str | None = Field(default=None, max_length=2000)
    asset_type: str | None = Field(default=None, min_length=1, max_length=64)
    issuer_name: str | None = Field(default=None, min_length=1, max_length=255)
    issuer_ticker: str | None = Field(default=None, min_length=1, max_length=32)
    amount_lower_usd: float | None = Field(default=None, ge=0)
    amount_upper_usd: float | None = Field(default=None, ge=0)
    amount_bucket_label: str | None = Field(default=None, min_length=1, max_length=64)
    comments: str | None = Field(default=None, max_length=4000)
    excess_return: float | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    mapping_status: GovernmentSignalMappingStatus = "pending_review"
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @model_validator(mode="after")
    def validate_amount_bounds(self) -> "CongressTradeEvent":
        if (
            self.amount_lower_usd is not None
            and self.amount_upper_usd is not None
            and self.amount_lower_usd > self.amount_upper_usd
        ):
            raise ValueError("amount_upper_usd must be >= amount_lower_usd.")
        return self


class CongressTradeVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_id: str = Field(..., min_length=1, max_length=128)
    event_id: str = Field(..., min_length=1, max_length=128)
    version_seq: int = Field(..., ge=1)
    version_kind: str = Field(..., min_length=1, max_length=64)
    version_observed_at: datetime
    event: CongressTradeEvent


class CongressTradeEventListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[CongressTradeEvent]
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)


class GovernmentContractEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(..., min_length=1, max_length=128)
    source_name: str = Field(..., min_length=1, max_length=64)
    source_event_key: str = Field(..., min_length=1, max_length=255)
    event_type: GovernmentContractEventType
    event_at: datetime
    recipient_name: str = Field(..., min_length=1, max_length=255)
    recipient_ticker: str | None = Field(default=None, min_length=1, max_length=32)
    awarding_agency: str = Field(..., min_length=1, max_length=255)
    funding_agency: str | None = Field(default=None, min_length=1, max_length=255)
    award_id: str | None = Field(default=None, min_length=1, max_length=128)
    parent_award_id: str | None = Field(default=None, min_length=1, max_length=128)
    opportunity_id: str | None = Field(default=None, min_length=1, max_length=128)
    solicitation_id: str | None = Field(default=None, min_length=1, max_length=128)
    title: str = Field(..., min_length=1, max_length=512)
    description: str | None = Field(default=None, max_length=4000)
    award_amount_usd: float | None = None
    obligation_delta_usd: float | None = None
    outlay_delta_usd: float | None = None
    cumulative_obligation_usd: float | None = None
    modification_number: str | None = Field(default=None, min_length=1, max_length=64)
    option_exercise_flag: bool = False
    termination_flag: bool = False
    cancellation_flag: bool = False
    protest_flag: bool = False
    naics_code: str | None = Field(default=None, min_length=1, max_length=16)
    psc_code: str | None = Field(default=None, min_length=1, max_length=16)
    competition_type: str | None = Field(default=None, min_length=1, max_length=128)
    set_aside_type: str | None = Field(default=None, min_length=1, max_length=128)
    contract_vehicle: str | None = Field(default=None, min_length=1, max_length=128)
    place_of_performance_country: str | None = Field(default=None, min_length=1, max_length=64)
    place_of_performance_state: str | None = Field(default=None, min_length=1, max_length=64)
    confidence: float | None = Field(default=None, ge=0, le=1)
    mapping_status: GovernmentSignalMappingStatus = "pending_review"
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GovernmentContractVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_id: str = Field(..., min_length=1, max_length=128)
    event_id: str = Field(..., min_length=1, max_length=128)
    version_seq: int = Field(..., ge=1)
    version_kind: str = Field(..., min_length=1, max_length=64)
    version_observed_at: datetime
    event: GovernmentContractEvent


class GovernmentContractEventListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[GovernmentContractEvent]
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)


class IssuerGovernmentSignalDaily(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of_date: date
    symbol: str = Field(..., min_length=1, max_length=32)
    issuer_name: str | None = Field(default=None, min_length=1, max_length=255)
    congress_purchase_count_1d: int = Field(default=0, ge=0)
    congress_purchase_count_7d: int = Field(default=0, ge=0)
    congress_purchase_count_30d: int = Field(default=0, ge=0)
    congress_purchase_count_90d: int = Field(default=0, ge=0)
    congress_sale_count_1d: int = Field(default=0, ge=0)
    congress_sale_count_7d: int = Field(default=0, ge=0)
    congress_sale_count_30d: int = Field(default=0, ge=0)
    congress_sale_count_90d: int = Field(default=0, ge=0)
    congress_net_amount_proxy_usd_30d: float = 0
    congress_net_amount_proxy_usd_90d: float = 0
    congress_amendment_rate_90d: float = 0
    congress_late_filing_rate_90d: float = 0
    congress_unique_members_90d: int = Field(default=0, ge=0)
    congress_unique_committees_90d: int = Field(default=0, ge=0)
    contract_award_count_30d: int = Field(default=0, ge=0)
    contract_award_count_90d: int = Field(default=0, ge=0)
    contract_obligation_delta_usd_30d: float = 0
    contract_obligation_delta_usd_90d: float = 0
    contract_outlay_delta_usd_30d: float = 0
    contract_outlay_delta_usd_90d: float = 0
    contract_modification_count_90d: int = Field(default=0, ge=0)
    contract_option_exercise_count_90d: int = Field(default=0, ge=0)
    contract_termination_count_90d: int = Field(default=0, ge=0)
    contract_cancellation_count_90d: int = Field(default=0, ge=0)
    contract_protest_count_90d: int = Field(default=0, ge=0)
    contract_unique_awarding_agencies_90d: int = Field(default=0, ge=0)
    contract_unique_naics_90d: int = Field(default=0, ge=0)
    contract_unique_psc_90d: int = Field(default=0, ge=0)
    last_congress_trade_at: datetime | None = None
    last_contract_event_at: datetime | None = None
    mapping_status: GovernmentSignalMappingStatus = "pending_review"


class GovernmentSignalAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alert_id: str = Field(..., min_length=1, max_length=128)
    symbol: str = Field(..., min_length=1, max_length=32)
    as_of_date: date
    alert_type: GovernmentSignalAlertType
    severity: GovernmentSignalSeverity
    title: str = Field(..., min_length=1, max_length=255)
    summary: str = Field(..., min_length=1, max_length=4000)
    congress_signal_score: float | None = None
    contract_signal_score: float | None = None
    composite_signal_score: float | None = None
    source_event_ids: list[str] = Field(default_factory=list)
    created_at: datetime | None = None


class GovernmentSignalAlertListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alerts: list[GovernmentSignalAlert]
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)


class GovernmentSignalMappingReviewItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mapping_id: str = Field(..., min_length=1, max_length=128)
    source_name: str = Field(..., min_length=1, max_length=64)
    entity_type: str = Field(..., min_length=1, max_length=64)
    raw_key: str = Field(..., min_length=1, max_length=255)
    raw_name: str = Field(..., min_length=1, max_length=512)
    proposed_symbol: str | None = Field(default=None, min_length=1, max_length=32)
    confidence: float | None = Field(default=None, ge=0, le=1)
    status: GovernmentSignalMappingStatus = "pending_review"
    reason: str | None = Field(default=None, max_length=1000)
    updated_at: datetime | None = None


class GovernmentSignalMappingReviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[GovernmentSignalMappingReviewItem]
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)


class GovernmentSignalMappingOverrideRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: GovernmentSignalMappingAction
    symbol: str | None = Field(default=None, min_length=1, max_length=32)
    reason: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_action_requirements(self) -> "GovernmentSignalMappingOverrideRequest":
        if self.action == "map" and not self.symbol:
            raise ValueError("symbol is required when action='map'.")
        if self.action != "map" and self.symbol is not None:
            raise ValueError("symbol is only allowed when action='map'.")
        return self


class GovernmentSignalMappingOverrideResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mapping_id: str = Field(..., min_length=1, max_length=128)
    status: GovernmentSignalMappingStatus
    symbol: str | None = Field(default=None, min_length=1, max_length=32)
    updated_at: datetime


class GovernmentSignalIssuerSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(..., min_length=1, max_length=32)
    issuer_name: str | None = Field(default=None, min_length=1, max_length=255)
    as_of_date: date
    issuer_daily: IssuerGovernmentSignalDaily
    recent_congress_trades: list[CongressTradeEvent] = Field(default_factory=list)
    recent_contract_events: list[GovernmentContractEvent] = Field(default_factory=list)
    active_alerts: list[GovernmentSignalAlert] = Field(default_factory=list)


class GovernmentSignalPortfolioHolding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(..., min_length=1, max_length=32)
    shares: float | None = None
    market_value: float | None = None
    portfolio_weight: float | None = None


class GovernmentSignalPortfolioIssuerExposure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(..., min_length=1, max_length=32)
    issuer_name: str | None = Field(default=None, min_length=1, max_length=255)
    matched: bool = True
    market_value: float | None = None
    portfolio_weight: float | None = None
    issuer_daily: IssuerGovernmentSignalDaily | None = None
    alerts: list[GovernmentSignalAlert] = Field(default_factory=list)


class GovernmentSignalPortfolioExposureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of_date: date | None = None
    holdings: list[GovernmentSignalPortfolioHolding]

    @model_validator(mode="after")
    def validate_holdings(self) -> "GovernmentSignalPortfolioExposureRequest":
        if not self.holdings:
            raise ValueError("holdings must not be empty.")
        return self


class GovernmentSignalPortfolioExposureResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of_date: date
    holdings_analyzed: int = Field(..., ge=0)
    matched_holdings: int = Field(..., ge=0)
    unmatched_symbols: list[str] = Field(default_factory=list)
    total_market_value: float | None = None
    total_portfolio_weight: float | None = None
    exposures: list[GovernmentSignalPortfolioIssuerExposure] = Field(default_factory=list)
