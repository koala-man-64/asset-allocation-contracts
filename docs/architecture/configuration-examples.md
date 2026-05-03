# Configuration Examples

This reference documents valid configuration objects owned by `asset-allocation-contracts`.

It is intentionally limited to configuration surfaces that control behavior:

- `StrategyConfig`, `UniverseDefinition`, and `ExitRule`
- `ConfigReference`, `ConfigIdentity`, and reusable strategy component presets
- `RebalancePolicy`, `StrategyRiskPolicy`, and reusable exit policy bundles
- `RankingSchemaConfig`, `RankingGroup`, `RankingFactor`, and `RankingTransform`
- `RegimePolicy` and `RegimeModelConfig`
- `UiRuntimeConfig`
- The repo bootstrap env surface defined by `.env.template` and `docs/ops/env-contract.*`

It does not cover non-configuration payloads such as backtest request/response objects, auth session status responses, or constant-only modules such as `finance.py`, `market_history.py`, and `paths.py`.

## Strategy, Universe, and Exit Rules

Source of truth:

- `python/asset_allocation_contracts/strategy.py`
- `schemas/strategy-config.schema.json`
- `schemas/config-reference.schema.json`
- `schemas/config-identity.schema.json`
- `schemas/strategy-component-refs.schema.json`
- `schemas/*-preset.schema.json`
- `schemas/strategy-risk-profile-*.schema.json`
- `schemas/strategy-rebalance-policy.schema.json`
- `schemas/strategy-risk-policy.schema.json`
- `schemas/exit-rule-set-config.schema.json`
- `schemas/universe-definition.schema.json`
- `ts/src/contracts.ts`

`StrategyConfig` requires at least one of `componentRefs.universe`, `universeConfigName`, or `universe`.
For reusable backtests, `componentRefs` is the canonical pinning surface. Inline `universe`, `rebalancePolicy`, `regimePolicy`, `strategyRiskPolicy`, and `exits` remain supported for compatibility and scratch research, but reusable validation or production-candidate runs should pin immutable reusable presets by `name + version`.
When `riskProfileName` is present, `positionPolicy` must also be present as the embedded execution snapshot.

### Minimal inline universe

```json
{
  "universe": {
    "source": "postgres_gold",
    "root": {
      "kind": "group",
      "operator": "and",
      "clauses": [
        {
          "kind": "condition",
          "field": "market.close",
          "operator": "gt",
          "value": 0
        }
      ]
    }
  },
  "rebalance": "monthly",
  "longOnly": true,
  "topN": 20,
  "lookbackWindow": 63,
  "holdingPeriod": 21,
  "costModel": "default",
  "intrabarConflictPolicy": "stop_first",
  "exits": []
}
```

### Nested universe definition

This example shows the three supported `UniverseCondition` patterns:

- `eq`, `ne`, `gt`, `gte`, `lt`, and `lte` use `value`
- `in` and `not_in` use `values`
- `is_null` and `is_not_null` use neither `value` nor `values`

`UniverseCondition.field` must be one of the governed public field ids exported by the contracts package. The initial catalog is:

- `market.close`
- `security.is_active`
- `security.sector`
- `security.delisted_at`
- `market.trade_date`
- `market.timestamp`
- `returns.return_20d`
- `returns.return_126d`
- `quality.piotroski_f_score`
- `earnings.surprise_pct`
- `security.market_cap`
- `market.dollar_volume_20d`
- `security.primary_listing`
- `security.country`
- `security.is_price_liquidity_eligible`

```json
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
          "value": true
        },
      {
        "kind": "group",
        "operator": "or",
        "clauses": [
          {
            "kind": "condition",
            "field": "security.sector",
            "operator": "in",
            "values": ["technology", "health_care"]
          },
          {
            "kind": "condition",
            "field": "security.delisted_at",
            "operator": "is_null"
          }
        ]
      }
    ]
  }
}
```

### Strategy with all exit rule types

```json
{
  "universeConfigName": "core-us-equities",
  "rebalance": "monthly",
  "longOnly": true,
  "topN": 20,
  "lookbackWindow": 63,
  "holdingPeriod": 21,
  "costModel": "default",
  "rankingSchemaName": "quality-momentum-v1",
  "riskProfileName": "balanced",
  "regimePolicy": {
    "modelName": "default-regime",
    "mode": "observe_only"
  },
  "positionPolicy": {
    "targetPositionSize": {
      "mode": "pct_of_allocatable_capital",
      "value": 5
    },
    "maxPositionSize": {
      "mode": "pct_of_allocatable_capital",
      "value": 8
    },
    "maxOpenPositions": 20
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
      "reference": "entry_price"
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
      "reference": "entry_price"
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
      "reference": "highest_since_entry"
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
      "reference": "highest_since_entry"
    },
    {
      "id": "time-stop-10-bars",
      "type": "time_stop",
      "scope": "position",
      "priceField": "close",
      "value": 10,
      "priority": 4,
      "action": "exit_full",
      "minHoldBars": 0
    },
    {
      "id": "rank-decay-40",
      "type": "rank_decay",
      "scope": "position",
      "rankThreshold": 40,
      "priority": 5,
      "action": "exit_full",
      "minHoldBars": 0
    }
  ]
}
```

Validation notes:

- `ExitRule.id` must be unique within a strategy.
- `riskProfileName` requires an embedded `positionPolicy` snapshot so runtime and backtests never need a late-bound catalog lookup.
- `trailing_stop_atr` requires `atrColumn`.
- `time_stop` requires an integer `value` and only allows `priceField: "close"`.
- `rank_decay` requires `rankThreshold` and does not accept `value`, `reference`, `atrColumn`, or `priceField`.
- `StrategyPositionPolicy.targetPositionSize` percentage sizing still cannot allocate more than `100%` across the selected long-only basket.
- The Python model still strips legacy `enabled` toggles from `regimePolicy` and `exits` for compatibility, but the canonical schema does not model those fields.

### Reusable strategy component refs

Reusable backtests should pin all six component families with `StrategyConfig.componentRefs`. A config publisher may still include resolved inline snapshots beside those refs for auditability, but the immutable identity is the `name + version` pair in `componentRefs`.

```json
{
  "componentRefs": {
    "universe": { "name": "us_large_liquid", "version": 1 },
    "ranking": { "name": "quality_momentum", "version": 1 },
    "rebalance": { "name": "monthly_last_trading_day", "version": 1 },
    "regimePolicy": { "name": "observe_only_default", "version": 1 },
    "riskPolicy": { "name": "balanced_long_only", "version": 1 },
    "exitPolicy": { "name": "rank_decay_exit", "version": 1 }
  },
  "rebalance": "monthly",
  "longOnly": true,
  "topN": 20,
  "lookbackWindow": 252,
  "holdingPeriod": 21,
  "costModel": "default",
  "intrabarConflictPolicy": "priority_order",
  "exits": []
}
```

Inline scratch configs remain valid for research notes, one-off experiments, and migration compatibility:

```json
{
  "universe": {
    "source": "postgres_gold",
    "root": {
      "kind": "group",
      "operator": "and",
      "clauses": [
        { "kind": "condition", "field": "security.country", "operator": "eq", "value": "US" },
        { "kind": "condition", "field": "market.close", "operator": "gt", "value": 5 },
        { "kind": "condition", "field": "market.dollar_volume_20d", "operator": "gte", "value": 25000000 }
      ]
    }
  },
  "rankingSchemaName": "scratch-quality-momentum",
  "rebalancePolicy": {
    "frequency": "monthly",
    "executionTiming": "next_bar_open"
  },
  "regimePolicy": {
    "modelName": "default-regime",
    "mode": "observe_only"
  },
  "strategyRiskPolicy": {
    "scope": "strategy",
    "stopLoss": {
      "thresholdPct": 8,
      "action": "reduce_exposure",
      "reductionPct": 50
    }
  },
  "exits": [
    { "id": "rank-decay-40", "type": "rank_decay", "rankThreshold": 40 }
  ]
}
```

Validation notes:

- `ConfigReference.version` and `ConfigIdentity.version` are positive integers.
- `ConfigIdentity.status` is `draft`, `active`, or `deprecated`.
- `ConfigIdentity.intendedUse` is `research`, `validation`, or `production_candidate`.
- Reusable preset wrappers use `extra: forbid`; unknown fields should fail validation instead of being silently ignored.
- Published reusable configs are immutable by `name + version`; changes require a new version.

### Starter reusable preset library

The starter library is scoped to US liquid long-only equity backtests. It deliberately excludes long/short, ETF allocation, execution-policy, cost-model, data-quality, compliance, and surveillance expansion.

Universes:

| name | version | first grid | definition |
| --- | ---: | --- | --- |
| `us_large_liquid` | 1 | yes | US primary-listed names, `security.market_cap >= 10000000000`, `market.dollar_volume_20d >= 50000000`, `market.close > 5`, `security.is_price_liquidity_eligible = true` |
| `us_mid_large_liquid` | 1 | yes | Same controls with `security.market_cap >= 2000000000` and `market.dollar_volume_20d >= 25000000` |
| `sector_balanced_large` | 1 | no | `us_large_liquid` base plus sector balancing constraints resolved by the backtest runner, not by the universe contract itself |

Rankings:

| name | version | groups |
| --- | ---: | --- |
| `momentum_12_1` | 1 | 12-1 momentum using `return_252d` excluding the most recent month where available; first implementation may approximate with governed return fields until a dedicated column is published |
| `quality_momentum` | 1 | quality score plus medium-term momentum |
| `value_quality_momentum` | 1 | value, quality, and momentum with percentile/minmax transforms |

Rebalance:

| name | version | `RebalancePolicy` |
| --- | ---: | --- |
| `monthly_last_trading_day` | 1 | `cadence: monthly`, `dayRule: last_trading_day`, `anchor: next_open`, `tradeDelayBars: 0` |
| `quarterly_last_trading_day` | 1 | `cadence: quarterly`, `dayRule: last_trading_day`, `anchor: next_open`, `tradeDelayBars: 0` |

Regime:

| name | version | policy |
| --- | ---: | --- |
| `observe_only_default` | 1 | `RegimePolicy(modelName: default-regime, mode: observe_only)` |

Risk:

| name | version | first grid | policy |
| --- | ---: | --- | --- |
| `balanced_long_only` | 1 | yes | baseline position sizing and strategy-level drawdown controls for diversified long-only baskets |
| `conservative_long_only` | 1 | no | lower position size, tighter drawdown stop, higher cash buffer |
| `aggressive_long_only` | 1 | no | larger position size and looser drawdown stop for later sensitivity tests |

Exits:

| name | version | policy |
| --- | ---: | --- |
| `rebalance_only` | 1 | no position-level exits; removed names are closed by rebalance policy |
| `rank_decay_exit` | 1 | `ExitRule(type: rank_decay, rankThreshold: 40)` plus rebalance exits |

First matrix:

| component | values |
| --- | --- |
| universe | `us_large_liquid`, `us_mid_large_liquid` |
| ranking | `momentum_12_1`, `quality_momentum`, `value_quality_momentum` |
| rebalance | `monthly_last_trading_day`, `quarterly_last_trading_day` |
| risk | `balanced_long_only` |
| exits | `rebalance_only`, `rank_decay_exit` |
| regime | `observe_only_default` |

This produces `2 universes x 3 rankings x 2 rebalances x 1 risk x 2 exits x 1 regime = 24` first-pass runs.

### Reusable preset wrapper example

```json
{
  "identity": {
    "name": "us_large_liquid",
    "version": 1,
    "status": "active",
    "description": "US large-cap, primary-listed, liquid common-equity universe.",
    "intendedUse": "validation",
    "thesis": "A stable large-liquid universe reduces capacity and stale-price artifacts in first-pass long-only ranking tests.",
    "whatToMonitor": ["constituent count", "daily turnover", "spread and slippage drift"]
  },
  "config": {
    "source": "postgres_gold",
    "root": {
      "kind": "group",
      "operator": "and",
      "clauses": [
        { "kind": "condition", "field": "security.country", "operator": "eq", "value": "US" },
        { "kind": "condition", "field": "security.primary_listing", "operator": "eq", "value": true },
        { "kind": "condition", "field": "security.market_cap", "operator": "gte", "value": 10000000000 },
        { "kind": "condition", "field": "market.dollar_volume_20d", "operator": "gte", "value": 50000000 },
        { "kind": "condition", "field": "market.close", "operator": "gt", "value": 5 },
        { "kind": "condition", "field": "security.is_price_liquidity_eligible", "operator": "eq", "value": true }
      ]
    }
  }
}
```

### Strategy risk profile detail

```json
{
  "name": "balanced",
  "description": "Default balanced posture for diversified long-only sleeves.",
  "presetClass": "balanced",
  "version": 1,
  "isSystem": true,
  "usageCount": 6,
  "config": {
    "presetClass": "balanced",
    "positionPolicy": {
      "targetPositionSize": {
        "mode": "pct_of_allocatable_capital",
        "value": 5
      },
      "maxPositionSize": {
        "mode": "pct_of_allocatable_capital",
        "value": 8
      },
      "maxOpenPositions": 20
    }
  }
}
```

Validation notes:

- `presetClass` is a governed posture label: `conservative`, `balanced`, or `aggressive`.
- Reusable risk profiles require `targetPositionSize`, `maxPositionSize`, and `maxOpenPositions`.
- `targetPositionSize` and `maxPositionSize` must share the same sizing mode, and `maxPositionSize` cannot be smaller than `targetPositionSize`.

## Ranking Schema

Source of truth:

- `python/asset_allocation_contracts/ranking.py`
- `schemas/ranking-schema.schema.json`
- `ts/src/contracts.ts`

### Ranking schema example

```json
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
                "upperQuantile": 0.95
              }
            },
            {
              "type": "zscore",
              "params": {}
            }
          ]
        },
        {
          "name": "net_debt_to_ebitda",
          "table": "fundamentals",
          "column": "net_debt_to_ebitda",
          "weight": 0.8,
          "direction": "asc",
          "missingValuePolicy": "exclude",
          "transforms": [
            {
              "type": "clip",
              "params": {
                "upper": 8
              }
            }
          ]
        }
      ],
      "transforms": [
        {
          "type": "percentile_rank",
          "params": {}
        }
      ]
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
            {
              "type": "coalesce",
              "params": {
                "value": 0
              }
            },
            {
              "type": "percentile_rank",
              "params": {}
            }
          ]
        }
      ],
      "transforms": []
    }
  ],
  "overallTransforms": [
    {
      "type": "minmax",
      "params": {}
    }
  ]
}
```

### Valid transform examples

```json
[
  { "type": "percentile_rank", "params": {} },
  { "type": "zscore", "params": {} },
  { "type": "minmax", "params": {} },
  { "type": "clip", "params": { "lower": 0, "upper": 100 } },
  { "type": "winsorize", "params": { "lowerQuantile": 0.05, "upperQuantile": 0.95 } },
  { "type": "coalesce", "params": { "value": 0 } },
  { "type": "log1p", "params": {} },
  { "type": "negate", "params": {} },
  { "type": "abs", "params": {} }
]
```

Validation notes:

- Group names must be unique inside `RankingSchemaConfig`.
- Factor names must be unique inside each `RankingGroup`.
- `clip` requires at least one of `lower` or `upper`.
- `winsorize` only accepts quantiles between `0` and `1`.
- `coalesce` requires `params.value`.

## Regime Policy and Model Configuration

Source of truth:

- `python/asset_allocation_contracts/regime.py`
- `schemas/regime-policy.schema.json`
- `schemas/regime-model-config.schema.json`
- `ts/src/contracts.ts`

### Regime policy example

```json
{
  "modelName": "default-regime",
  "modelVersion": 3,
  "mode": "observe_only"
}
```

### Regime model config example

```json
{
  "activationThreshold": 0.6,
  "haltVixThreshold": 32.0,
  "haltVixStreakDays": 2
}
```

Validation notes:

- `haltVixStreakDays` must be at least `1`.
- `RegimePolicy.modelName` is trimmed and falls back to `default-regime` when blank.
- `RegimePolicy.mode` is `observe_only` in this first-pass reusable strategy config layer.
- The current `default-regime` policy rejects legacy actioning fields such as `targetGrossExposureByRegime`, `blockOnTransition`, and `onBlocked`.

Canonical `default-regime` v3 notes:

- The canonical taxonomy is `trending_up`, `trending_down`, `mean_reverting`, `low_volatility`, `high_volatility`, `liquidity_stress`, `macro_alignment`, and `unclassified`.
- `signalConfigs` defaults to the canonical v3 rule set when omitted.
- `validate_canonical_default_regime_config` enforces the canonical activation threshold, halt controls, and signal configuration.

## UI Runtime Configuration

Source of truth:

- `python/asset_allocation_contracts/ui_config.py`
- `schemas/ui-runtime-config.schema.json`
- `ts/src/contracts.ts`

### Minimal UI runtime config

```json
{
  "apiBaseUrl": "/api",
  "authSessionMode": "bearer",
  "authProvider": "disabled",
  "oidcEnabled": false,
  "authRequired": false,
  "oidcScopes": [],
  "oidcAudience": []
}
```

### OIDC-enabled UI runtime config

This is also a valid Python input payload because `oidcScopes` and `oidcAudience` accept comma-separated or space-separated strings and normalize them to arrays.

```json
{
  "apiBaseUrl": "https://control-plane.example.com/api",
  "authSessionMode": "cookie",
  "authProvider": "oidc",
  "oidcEnabled": true,
  "authRequired": true,
  "oidcAuthority": "https://login.example.com/tenant/v2.0",
  "oidcClientId": "11111111-2222-3333-4444-555555555555",
  "oidcScopes": "api://asset-allocation-api/user_impersonation openid profile",
  "oidcRedirectUri": "https://ui.example.com/auth/callback",
  "oidcPostLogoutRedirectUri": "https://ui.example.com/",
  "oidcAudience": "asset-allocation-api,asset-allocation-jobs"
}
```

### Password-auth UI runtime config

```json
{
  "apiBaseUrl": "/api",
  "authSessionMode": "cookie",
  "authProvider": "password",
  "oidcEnabled": false,
  "authRequired": true,
  "oidcScopes": [],
  "oidcAudience": []
}
```

Validation notes:

- `apiBaseUrl` must be a non-empty string.
- `authSessionMode` defaults to `bearer`; deployed browser sessions may set `cookie`.
- `authProvider` defaults to `disabled`; password auth requires `authSessionMode: "cookie"`.
- `oidcScopes` and `oidcAudience` normalize `string`, `list`, `tuple`, and `set` inputs into string arrays.

## Repo Bootstrap Env Configuration

Source of truth:

- `.env.template`
- `docs/ops/env-contract.csv`
- `docs/ops/env-contract.md`
- `scripts/setup-env.ps1`

This repo uses `.env.web` as the sync surface for GitHub variables and secrets. The example below is structurally valid and matches the documented env contract.

```dotenv
JOBS_REPOSITORY=example-org/asset-allocation-jobs
UI_REPOSITORY=example-org/asset-allocation-ui
DISPATCH_APP_ID=123456
PYTHON_PUBLISH_REPOSITORY_URL=https://upload.pypi.org/legacy/
DISPATCH_APP_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASC...\n-----END PRIVATE KEY-----\n
PYTHON_PUBLISH_USERNAME=__token__
PYTHON_PUBLISH_PASSWORD=pypi-AgEIcHlwaS5vcmcCI...
```

Validation notes:

- `DISPATCH_APP_PRIVATE_KEY` must be stored with literal `\n` escapes, not raw multiline PEM content.
- TypeScript publish auth is not part of `.env.web`; npm trusted publishing handles that in GitHub Actions.
- Retired `NPM_TOKEN` and `NPM_REGISTRY_URL` keys must not appear in `.env.web`.

## What This Reference Excludes

These contract surfaces are real and public, but they are not configuration objects:

- Backtest claim/start/complete/fail/listing/summary payloads in `python/asset_allocation_contracts/backtest.py`
- Auth session status payloads in `python/asset_allocation_contracts/ui_config.py`
- Constant and path helpers in `finance.py`, `market_history.py`, and `paths.py`

Use the generated schemas in `schemas/` when you need the full language-neutral contract shape for those payloads.
