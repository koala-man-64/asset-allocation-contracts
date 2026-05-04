from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SymbolIdentityProvider = Literal["massive", "alpha_vantage", "nasdaq"]
SymbolIdentityDomain = Literal["market", "finance", "earnings", "price-target"]
SymbolResolutionStatus = Literal["resolved", "unsupported", "ambiguous", "invalid"]
SymbolResolutionErrorCode = Literal["unsupported", "ambiguous", "invalid"]

SYMBOL_ALIAS_RULESET_VERSION = "symbol-alias-v1"


class SymbolAliasRule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: SymbolIdentityProvider
    domain: SymbolIdentityDomain
    providerSymbol: str = Field(min_length=1, max_length=32)
    canonicalSymbol: str = Field(min_length=1, max_length=32)


class SymbolResolutionError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: SymbolResolutionErrorCode
    message: str = Field(min_length=1, max_length=500)
    provider: SymbolIdentityProvider | None = None
    domain: SymbolIdentityDomain | None = None
    inputSymbol: str | None = Field(default=None, max_length=32)


class SymbolResolutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: SymbolResolutionStatus
    provider: SymbolIdentityProvider
    domain: SymbolIdentityDomain
    inputSymbol: str = Field(max_length=32)
    canonicalSymbol: str | None = Field(default=None, min_length=1, max_length=32)
    providerSymbol: str | None = Field(default=None, min_length=1, max_length=32)
    mappingVersion: str = Field(default=SYMBOL_ALIAS_RULESET_VERSION, min_length=1, max_length=64)
    error: SymbolResolutionError | None = None


SYMBOL_ALIAS_RULES: tuple[SymbolAliasRule, ...] = (
    SymbolAliasRule(
        provider="massive",
        domain="market",
        providerSymbol="I:VIX",
        canonicalSymbol="^VIX",
    ),
    SymbolAliasRule(
        provider="massive",
        domain="market",
        providerSymbol="I:VIX3M",
        canonicalSymbol="^VIX3M",
    ),
)
