from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalize_scopes(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        normalized = value.replace(",", " ").strip()
        return [scope for scope in normalized.split() if scope]
    if isinstance(value, (list, tuple, set)):
        scopes: list[str] = []
        for item in value:
            text = str(item or "").strip()
            if text:
                scopes.append(text)
        return scopes
    text = str(value).strip()
    return [text] if text else []


AuthSessionMode = Literal["bearer", "cookie"]


class UiRuntimeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    apiBaseUrl: str = Field(default="/api", min_length=1)
    authSessionMode: AuthSessionMode = "bearer"
    oidcEnabled: bool = False
    authRequired: bool = False
    oidcAuthority: str | None = None
    oidcClientId: str | None = None
    oidcScopes: list[str] = Field(default_factory=list)
    oidcRedirectUri: str | None = None
    oidcPostLogoutRedirectUri: str | None = None
    oidcAudience: list[str] = Field(default_factory=list)

    @field_validator("oidcScopes", "oidcAudience", mode="before")
    @classmethod
    def normalize_scopes(cls, value: Any) -> list[str]:
        return _normalize_scopes(value)


class AuthSessionStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    authMode: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    displayName: str | None = None
    username: str | None = None
    requiredRoles: list[str] = Field(default_factory=list)
    grantedRoles: list[str] = Field(default_factory=list)
