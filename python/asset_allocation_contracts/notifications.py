from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from asset_allocation_contracts.trade_desk import (
    TradeEnvironment,
    TradeOrderPreviewRequest,
    TradeOrderSide,
    TradeOrderType,
    TradeTimeInForce,
)

NotificationKind = Literal["message", "trade_approval"]
NotificationDeliveryChannel = Literal["email", "sms"]
NotificationDeliveryStatus = Literal["pending", "sent", "failed", "skipped"]
NotificationDecision = Literal["approve", "deny"]
NotificationDecisionStatus = Literal["not_required", "pending", "approved", "denied", "expired"]
NotificationExecutionStatus = Literal[
    "not_applicable",
    "pending_approval",
    "submitted",
    "blocked",
    "release_failed",
]
NotificationRequestStatus = Literal["pending", "delivered", "delivery_failed", "decided", "expired"]


def _normalize_required_text(value: object, field_name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"{field_name} is required.")
    return normalized


def _normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _normalize_url(value: object, field_name: str) -> str | None:
    normalized = _normalize_optional_text(value)
    if normalized is None:
        return None
    lowered = normalized.lower()
    if not (lowered.startswith("https://") or lowered.startswith("http://localhost") or lowered.startswith("http://127.0.0.1")):
        raise ValueError(f"{field_name} must be an https URL, or localhost http URL.")
    return normalized


class NotificationRecipient(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recipientId: str | None = Field(default=None, min_length=1, max_length=128)
    displayName: str | None = Field(default=None, min_length=1, max_length=160)
    email: str | None = Field(default=None, min_length=3, max_length=320)
    phoneNumber: str | None = Field(default=None, min_length=3, max_length=32)
    channels: list[NotificationDeliveryChannel] = Field(default_factory=list)

    @field_validator("recipientId", "displayName", "email", "phoneNumber", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("channels", mode="before")
    @classmethod
    def normalize_channels(cls, value: object) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("channels must be a list.")
        normalized: list[str] = []
        for item in value:
            channel = str(item or "").strip().lower()
            if channel and channel not in normalized:
                normalized.append(channel)
        return normalized

    @model_validator(mode="after")
    def validate_delivery_addresses(self) -> "NotificationRecipient":
        if not self.channels:
            raise ValueError("channels must include at least one delivery channel.")
        if "email" in self.channels and not self.email:
            raise ValueError("email is required when email delivery is requested.")
        if "sms" in self.channels and not self.phoneNumber:
            raise ValueError("phoneNumber is required when sms delivery is requested.")
        return self


class TradeApprovalPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    previewId: str = Field(..., min_length=1, max_length=128)
    orderHash: str = Field(..., min_length=1, max_length=128)
    placeIdempotencyKey: str = Field(..., min_length=16, max_length=160)
    order: TradeOrderPreviewRequest

    @field_validator("accountId", "previewId", "orderHash", "placeIdempotencyKey", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @model_validator(mode="after")
    def validate_order_alignment(self) -> "TradeApprovalPayload":
        if self.accountId != self.order.accountId:
            raise ValueError("accountId must match order.accountId.")
        return self


class TradeApprovalDisplay(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accountId: str = Field(..., min_length=1, max_length=128)
    previewId: str = Field(..., min_length=1, max_length=128)
    orderHash: str = Field(..., min_length=1, max_length=128)
    environment: TradeEnvironment
    symbol: str = Field(..., min_length=1, max_length=32)
    side: TradeOrderSide
    orderType: TradeOrderType
    timeInForce: TradeTimeInForce = "day"
    quantity: float | None = Field(default=None, gt=0)
    notional: float | None = Field(default=None, gt=0)
    limitPrice: float | None = Field(default=None, gt=0)
    stopPrice: float | None = Field(default=None, gt=0)

    @field_validator("accountId", "previewId", "orderHash", "symbol", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)


class CreateNotificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sourceRepo: str = Field(..., min_length=1, max_length=160)
    sourceSystem: str | None = Field(default=None, min_length=1, max_length=160)
    clientRequestId: str = Field(..., min_length=1, max_length=128)
    idempotencyKey: str = Field(..., min_length=16, max_length=160)
    kind: NotificationKind
    title: str = Field(..., min_length=1, max_length=160)
    description: str = Field(..., min_length=1, max_length=2000)
    targetUrl: str | None = Field(default=None, min_length=1, max_length=2048)
    recipients: list[NotificationRecipient] = Field(default_factory=list)
    expiresAt: datetime | None = None
    tradeApproval: TradeApprovalPayload | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("sourceRepo", "clientRequestId", "idempotencyKey", "title", "description", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("sourceSystem", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("targetUrl", mode="before")
    @classmethod
    def normalize_target_url(cls, value: object) -> str | None:
        return _normalize_url(value, "targetUrl")

    @model_validator(mode="after")
    def validate_payload_by_kind(self) -> "CreateNotificationRequest":
        if not self.recipients:
            raise ValueError("recipients must include at least one recipient.")
        if self.kind == "trade_approval" and self.tradeApproval is None:
            raise ValueError("tradeApproval is required for trade_approval notifications.")
        if self.kind == "message" and self.tradeApproval is not None:
            raise ValueError("tradeApproval is only valid for trade_approval notifications.")
        return self


class NotificationDeliveryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recipientId: str = Field(..., min_length=1, max_length=128)
    channel: NotificationDeliveryChannel
    address: str = Field(..., min_length=1, max_length=320)
    status: NotificationDeliveryStatus = "pending"
    provider: str | None = Field(default=None, min_length=1, max_length=64)
    providerMessageId: str | None = Field(default=None, min_length=1, max_length=160)
    attemptedAt: datetime | None = None
    sanitizedError: str | None = Field(default=None, min_length=1, max_length=500)

    @field_validator("recipientId", "address", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("provider", "providerMessageId", "sanitizedError", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class NotificationStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requestId: str = Field(..., min_length=1, max_length=128)
    kind: NotificationKind
    status: NotificationRequestStatus = "pending"
    sourceRepo: str = Field(..., min_length=1, max_length=160)
    sourceSystem: str | None = Field(default=None, min_length=1, max_length=160)
    clientRequestId: str = Field(..., min_length=1, max_length=128)
    title: str = Field(..., min_length=1, max_length=160)
    description: str = Field(..., min_length=1, max_length=2000)
    targetUrl: str | None = Field(default=None, min_length=1, max_length=2048)
    createdAt: datetime
    updatedAt: datetime
    expiresAt: datetime | None = None
    decisionStatus: NotificationDecisionStatus = "not_required"
    decision: NotificationDecision | None = None
    decidedAt: datetime | None = None
    decidedBy: str | None = Field(default=None, min_length=1, max_length=160)
    executionStatus: NotificationExecutionStatus = "not_applicable"
    executionOrderId: str | None = Field(default=None, min_length=1, max_length=128)
    executionMessage: str | None = Field(default=None, min_length=1, max_length=500)
    deliveries: list[NotificationDeliveryResult] = Field(default_factory=list)
    tradeApproval: TradeApprovalDisplay | None = None

    @field_validator("requestId", "sourceRepo", "clientRequestId", "title", "description", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator(
        "sourceSystem",
        "targetUrl",
        "decidedBy",
        "executionOrderId",
        "executionMessage",
        mode="before",
    )
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class NotificationActionDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requestId: str = Field(..., min_length=1, max_length=128)
    tokenId: str = Field(..., min_length=1, max_length=128)
    kind: NotificationKind
    title: str = Field(..., min_length=1, max_length=160)
    description: str = Field(..., min_length=1, max_length=2000)
    targetUrl: str | None = Field(default=None, min_length=1, max_length=2048)
    createdAt: datetime
    expiresAt: datetime | None = None
    decisionStatus: NotificationDecisionStatus = "not_required"
    executionStatus: NotificationExecutionStatus = "not_applicable"
    tradeApproval: TradeApprovalDisplay | None = None

    @field_validator("requestId", "tokenId", "title", "description", mode="before")
    @classmethod
    def normalize_required_text_fields(cls, value: object, info) -> str:
        return _normalize_required_text(value, info.field_name)

    @field_validator("targetUrl", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, value: object) -> str | None:
        return _normalize_optional_text(value)


class NotificationDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: NotificationDecision
    reason: str = Field(default="", max_length=1000)

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value: object) -> str:
        return str(value or "").strip()
