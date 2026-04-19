# Configuration Examples

This reference documents valid configuration objects owned by `asset-allocation-contracts`.

It is intentionally limited to configuration surfaces that control behavior:

- `StrategyConfig`, `UniverseDefinition`, and `ExitRule`
- `RankingSchemaConfig`, `RankingGroup`, `RankingFactor`, and `RankingTransform`
- `RegimePolicy` and `RegimeModelConfig`
- `UiRuntimeConfig`
- The repo bootstrap env surface defined by `.env.template` and `docs/ops/env-contract.*`

It does not cover non-configuration payloads such as backtest request/response objects, auth session status responses, or constant-only modules such as `finance.py`, `market_history.py`, and `paths.py`.

## Strategy, Universe, and Exit Rules

Source of truth:

- `python/asset_allocation_contracts/strategy.py`
- `schemas/strategy-config.schema.json`
- `schemas/universe-definition.schema.json`
- `ts/src/contracts.ts`

`StrategyConfig` requires at least one of `universeConfigName` or `universe`.

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
  "regimePolicy": {
    "modelName": "default-regime",
    "targetGrossExposureByRegime": {
      "trending_bull": 1.0,
      "trending_bear": 0.5,
      "choppy_mean_reversion": 0.75,
      "high_vol": 0.0,
      "unclassified": 0.0
    },
    "blockOnTransition": true,
    "blockOnUnclassified": true,
    "honorHaltFlag": true,
    "onBlocked": "skip_entries"
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
    }
  ]
}
```

Validation notes:

- `ExitRule.id` must be unique within a strategy.
- `trailing_stop_atr` requires `atrColumn`.
- `time_stop` requires an integer `value` and only allows `priceField: "close"`.
- The Python model still strips legacy `enabled` toggles from `regimePolicy` and `exits` for compatibility, but the canonical schema does not model those fields.

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
  "targetGrossExposureByRegime": {
    "trending_bull": 1.0,
    "trending_bear": 0.5,
    "choppy_mean_reversion": 0.75,
    "high_vol": 0.0,
    "unclassified": 0.0
  },
  "blockOnTransition": true,
  "blockOnUnclassified": true,
  "honorHaltFlag": true,
  "onBlocked": "skip_entries"
}
```

### Regime model config example

```json
{
  "trendPositiveThreshold": 0.02,
  "trendNegativeThreshold": -0.02,
  "curveContangoThreshold": 0.5,
  "curveInvertedThreshold": -0.5,
  "highVolEnterThreshold": 28.0,
  "highVolExitThreshold": 28.0,
  "bearVolMin": 15.0,
  "bearVolMaxExclusive": 25.0,
  "bullVolMaxExclusive": 15.0,
  "choppyVolMin": 10.0,
  "choppyVolMaxExclusive": 18.0,
  "haltVixThreshold": 32.0,
  "haltVixStreakDays": 2,
  "precedence": [
    "high_vol",
    "trending_bear",
    "trending_bull",
    "choppy_mean_reversion",
    "unclassified"
  ]
}
```

Validation notes:

- `haltVixStreakDays` must be at least `1`.
- `precedence` must contain valid regime codes.
- `RegimePolicy.modelName` is trimmed and falls back to `default-regime` when blank.
- `highVolExitThreshold` remains for one compatibility release, but canonical `default-regime` v2 sets it equal to `highVolEnterThreshold` so the `25-28` transition band is disabled.

Canonical `default-regime` v2 rule matrix:

- Trend state: `positive` when `return_20d > 0.02`, `negative` when `return_20d < -0.02`, otherwise `near_zero`.
- Curve state: `contango` when `vix_slope >= 0.5`, `inverted` when `vix_slope <= -0.5`, otherwise `flat`.
- High-vol entry: requires `rvol_10d_ann > 28.0` and an `inverted` curve. Exact `28.0` does not trigger `high_vol`; `28.01` does.
- Halt overlay: requires `vix_spot_close > 32.0` for `2+` consecutive sessions. Exact `32.0` does not halt; `32.01` does.

## UI Runtime Configuration

Source of truth:

- `python/asset_allocation_contracts/ui_config.py`
- `schemas/ui-runtime-config.schema.json`
- `ts/src/contracts.ts`

### Minimal UI runtime config

```json
{
  "apiBaseUrl": "/api",
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

Validation notes:

- `apiBaseUrl` must be a non-empty string.
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
