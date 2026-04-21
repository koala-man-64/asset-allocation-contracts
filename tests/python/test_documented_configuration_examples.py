from __future__ import annotations

from asset_allocation_contracts.ranking import RankingSchemaConfig, RankingTransform
from asset_allocation_contracts.regime import (
    RegimeModelConfig,
    RegimePolicy,
    validate_canonical_default_regime_config,
)
from asset_allocation_contracts.strategy import StrategyConfig, UniverseDefinition
from asset_allocation_contracts.ui_config import UiRuntimeConfig


def test_documented_universe_definition_example_is_valid() -> None:
    payload = UniverseDefinition.model_validate(
        {
            "source": "postgres_gold",
            "root": {
                "kind": "group",
                "operator": "and",
                "clauses": [
                    {
                        "kind": "condition",
                        "field": "security.is_active",
                        "operator": "eq",
                        "value": True,
                    },
                    {
                        "kind": "group",
                        "operator": "or",
                        "clauses": [
                            {
                                "kind": "condition",
                                "field": "security.sector",
                                "operator": "in",
                                "values": ["technology", "health_care"],
                            },
                            {
                                "kind": "condition",
                                "field": "security.delisted_at",
                                "operator": "is_null",
                            },
                        ],
                    },
                ],
            },
        }
    )

    assert payload.source == "postgres_gold"
    assert payload.root.operator == "and"


def test_documented_strategy_example_is_valid() -> None:
    payload = StrategyConfig.model_validate(
        {
            "universeConfigName": "core-us-equities",
            "rebalance": "monthly",
            "longOnly": True,
            "topN": 20,
            "lookbackWindow": 63,
            "holdingPeriod": 21,
            "costModel": "default",
            "rankingSchemaName": "quality-momentum-v1",
            "regimePolicy": {
                "modelName": "default-regime",
                "mode": "observe_only",
            },
            "intrabarConflictPolicy": "priority_order",
            "exits": [
                {
                    "id": "stop-loss-8pct",
                    "type": "stop_loss_fixed",
                    "scope": "position",
                    "priceField": "low",
                    "value": 0.08,
                    "priority": 0,
                    "action": "exit_full",
                    "minHoldBars": 0,
                    "reference": "entry_price",
                },
                {
                    "id": "take-profit-15pct",
                    "type": "take_profit_fixed",
                    "scope": "position",
                    "priceField": "high",
                    "value": 0.15,
                    "priority": 1,
                    "action": "exit_full",
                    "minHoldBars": 0,
                    "reference": "entry_price",
                },
                {
                    "id": "trail-10pct",
                    "type": "trailing_stop_pct",
                    "scope": "position",
                    "priceField": "low",
                    "value": 0.1,
                    "priority": 2,
                    "action": "exit_full",
                    "minHoldBars": 0,
                    "reference": "highest_since_entry",
                },
                {
                    "id": "trail-2atr",
                    "type": "trailing_stop_atr",
                    "scope": "position",
                    "priceField": "low",
                    "value": 2.0,
                    "atrColumn": "atr_14",
                    "priority": 3,
                    "action": "exit_full",
                    "minHoldBars": 0,
                    "reference": "highest_since_entry",
                },
                {
                    "id": "time-stop-10-bars",
                    "type": "time_stop",
                    "scope": "position",
                    "priceField": "close",
                    "value": 10,
                    "priority": 4,
                    "action": "exit_full",
                    "minHoldBars": 0,
                },
            ],
        }
    )

    assert payload.regimePolicy is not None
    assert len(payload.exits) == 5


def test_documented_ranking_examples_are_valid() -> None:
    schema = RankingSchemaConfig.model_validate(
        {
            "universeConfigName": "core-us-equities",
            "groups": [
                {
                    "name": "quality",
                    "weight": 0.6,
                    "factors": [
                        {
                            "name": "gross_margin",
                            "table": "fundamentals",
                            "column": "gross_margin",
                            "weight": 1.0,
                            "direction": "desc",
                            "missingValuePolicy": "exclude",
                            "transforms": [
                                {
                                    "type": "winsorize",
                                    "params": {
                                        "lowerQuantile": 0.05,
                                        "upperQuantile": 0.95,
                                    },
                                },
                                {"type": "zscore", "params": {}},
                            ],
                        },
                        {
                            "name": "net_debt_to_ebitda",
                            "table": "fundamentals",
                            "column": "net_debt_to_ebitda",
                            "weight": 0.8,
                            "direction": "asc",
                            "missingValuePolicy": "exclude",
                            "transforms": [
                                {"type": "clip", "params": {"upper": 8}},
                            ],
                        },
                    ],
                    "transforms": [
                        {"type": "percentile_rank", "params": {}},
                    ],
                },
                {
                    "name": "momentum",
                    "weight": 0.4,
                    "factors": [
                        {
                            "name": "return_126d",
                            "table": "market_data",
                            "column": "return_126d",
                            "weight": 1.0,
                            "direction": "desc",
                            "missingValuePolicy": "zero",
                            "transforms": [
                                {"type": "coalesce", "params": {"value": 0}},
                                {"type": "percentile_rank", "params": {}},
                            ],
                        }
                    ],
                    "transforms": [],
                },
            ],
            "overallTransforms": [
                {"type": "minmax", "params": {}},
            ],
        }
    )
    transforms = [
        {"type": "percentile_rank", "params": {}},
        {"type": "zscore", "params": {}},
        {"type": "minmax", "params": {}},
        {"type": "clip", "params": {"lower": 0, "upper": 100}},
        {"type": "winsorize", "params": {"lowerQuantile": 0.05, "upperQuantile": 0.95}},
        {"type": "coalesce", "params": {"value": 0}},
        {"type": "log1p", "params": {}},
        {"type": "negate", "params": {}},
        {"type": "abs", "params": {}},
    ]

    assert len(schema.groups) == 2
    for item in transforms:
        RankingTransform.model_validate(item)


def test_documented_regime_examples_are_valid() -> None:
    policy = RegimePolicy.model_validate(
        {
            "modelName": "default-regime",
            "mode": "observe_only",
        }
    )
    config = RegimeModelConfig.model_validate(
        validate_canonical_default_regime_config({}).model_dump(mode="python")
    )

    assert policy.mode == "observe_only"
    assert config.haltVixStreakDays == 2
    assert validate_canonical_default_regime_config(config) == config


def test_documented_ui_runtime_config_examples_are_valid() -> None:
    minimal = UiRuntimeConfig.model_validate(
        {
            "apiBaseUrl": "/api",
            "oidcEnabled": False,
            "authRequired": False,
            "oidcScopes": [],
            "oidcAudience": [],
        }
    )
    oidc_enabled = UiRuntimeConfig.model_validate(
        {
            "apiBaseUrl": "https://control-plane.example.com/api",
            "oidcEnabled": True,
            "authRequired": True,
            "oidcAuthority": "https://login.example.com/tenant/v2.0",
            "oidcClientId": "11111111-2222-3333-4444-555555555555",
            "oidcScopes": "api://asset-allocation-api/user_impersonation openid profile",
            "oidcRedirectUri": "https://ui.example.com/auth/callback",
            "oidcPostLogoutRedirectUri": "https://ui.example.com/",
            "oidcAudience": "asset-allocation-api,asset-allocation-jobs",
        }
    )

    assert minimal.apiBaseUrl == "/api"
    assert oidc_enabled.oidcScopes == [
        "api://asset-allocation-api/user_impersonation",
        "openid",
        "profile",
    ]
    assert oidc_enabled.oidcAudience == [
        "asset-allocation-api",
        "asset-allocation-jobs",
    ]
