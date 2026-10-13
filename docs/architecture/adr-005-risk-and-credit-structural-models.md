# ADR-005: Advanced Risk and Structural Credit Models

- Status: Accepted (contracts layer); runtime-common, jobs and control-plane adoption pending
- Contracts version: 5.5.0
- Work items: AB#3569 (Cornish-Fisher VaR/ES), AB#2650 (Merton/KMV distance-to-default), AB#3567 (opt-in Kelly sizing), AB#3568 (paper-book parametric VaR/ES measure kind)
- Routing: This is a contracts-authoring change. Consumer repos plan adoption only.

## Context

Parametric VaR/ES is currently Gaussian, which understates the tail loss of negatively skewed, fat-tailed equity returns. The gold layer has no structural credit factor, and Kelly sizing is advisory only.

This ADR is the reference for the shared contract shapes and the numerical definitions that `asset-allocation-runtime-common` and `asset-allocation-jobs` must implement. The numbers in the test-vector tables are the oracle for unit tests.

## Contract changes in 5.5.0

All additions are optional or new, so existing payloads stay valid.

| Shape | Change |
|---|---|
| `BacktestSummary` | New optional fields: `return_skewness`, `return_excess_kurtosis`, `var_95`, `es_97_5`, `var_95_cornish_fisher`, `es_97_5_cornish_fisher`, `cornish_fisher_fallback_reason`, `kelly_fraction` |
| `CornishFisherFallbackReason` | New literal: `non_monotonic_tail` \| `insufficient_observations` \| `undefined_moments` |
| `StrategyRiskExposurePolicy.kellySizing` | New optional `StrategyRiskKellySizingPolicy` section |
| `UniverseFieldId` | New fields: `credit.distance_to_default`, `credit.merton_pd`, both numeric with full comparison operators |

Conventions for the new `BacktestSummary` fields:
- `var_95`, `es_97_5` and their Cornish-Fisher variants are one-period losses expressed as positive return fractions, constrained by `ge=0`.
- When the Cornish-Fisher values are null, `cornish_fisher_fallback_reason` says why.

### Deferred: AB#3568 paper-book measure kind

`PortfolioRiskMeasureKind` and the paper-book models are not yet in this repository. The "existing 11 kinds" the original plan refers to live outside the published contracts.

When that enum moves here, add `"parametric_var_es"` as a new member. Its payload should reuse the `BacktestSummary` field names above: `var_95`, `es_97_5`, `var_95_cornish_fisher`, `es_97_5_cornish_fisher`, `cornish_fisher_fallback_reason`.

## 1. Cornish-Fisher VaR and ES (AB#3569)

### Moments

Returns `R_t` (t = 1..N) follow the zero-mean convention used for parametric risk: moments are raw, not demeaned.

- σ = sqrt(Σ R_t² / N)
- S = (Σ R_t³ / N) / σ³
- K = (Σ R_t⁴ / N) / σ⁴ − 3 (excess kurtosis)

This is deliberately not `scipy.stats.skew`/`kurtosis`, which demean. Tests must use these definitions.

### Quantile

Losses sit in the **left tail**. Use the left-tail standard normal quantile: c = Φ⁻¹(1 − confidence), so c = −1.64485 for 95% and c = −1.95996 for 97.5%.

The Cornish-Fisher quantile is:

w(c) = c + (c² − 1)·S/6 + (c³ − 3c)·K/24 − (2c³ − 5c)·S²/36

VaR_CF = −w(c₉₅) · σ

> Using +1.64485 inverts the skew adjustment: negative skew would *lower* VaR. Do not use it.

### Expected shortfall

ES is the CF quantile averaged over the tail, ES = (1/α)·∫₀^α −w(Φ⁻¹(u))·σ du, with α = 0.025 and c = c₉₇.₅. In closed form:

ES_CF = σ · (φ(c)/α) · [ 1 + c·S/6 + (c² − 1)·K/24 + (1 − 2c²)·S²/36 ]

At S = K = 0 this reduces to the Gaussian ES, σ·φ(c)/α.

### Validity guard: global monotonicity domain

dw/dz = A·z² + B·z + C, where:
- A = K/8 − S²/6
- B = S/3
- C = 1 − K/8 + 5S²/36

The expansion is a valid, monotone quantile function for every z if and only if:

(A > 0 and B² < 4AC)  or  (A = 0 and B = 0 and C > 0)

Fallback rules, in this order:
1. Fewer than 60 observations → `insufficient_observations`.
2. σ = 0, or S or K not finite → `undefined_moments`.
3. Outside the domain above → `non_monotonic_tail`.

On fallback, the Cornish-Fisher fields are null and `var_95`/`es_97_5` remain the Gaussian values. A local derivative check at the VaR quantile alone is not sufficient and must not be used.

### Test vectors (σ = 0.015)

| Case | S | K | var_95 | es_97_5 | var_95_cornish_fisher | es_97_5_cornish_fisher | fallback |
|---|---|---|---|---|---|---|---|
| Normal | 0 | 0 | 0.02467 | 0.03507 | 0.02467 | 0.03507 | — |
| Fat-tailed | −0.65 | 2.4 | 0.02467 | 0.03507 | 0.02660 | 0.04973 | — |
| Extreme | −3.5 | 15 | 0.02467 | 0.03507 | null | null | `non_monotonic_tail` (A < 0) |
| Mild skew, no kurtosis | −0.2 | 0 | 0.02467 | 0.03507 | null | null | `non_monotonic_tail` (A < 0) |

The fat-tailed case uses w(c₉₅) = −1.77325, which is +7.8% VaR over Gaussian. The original plan's 0.02976 (+20.6%) was wrong.

## 2. Merton/KMV distance-to-default (AB#2650)

### Inputs

All inputs are point-in-time as of `as_of_date`.

| Symbol | Meaning | Source in `asset-allocation-jobs` |
|---|---|---|
| E | Market cap | `gold.finance_data.market_cap` (optional column; missing → exclusion `missing_market_cap`) |
| σ_E | Annualized equity volatility | `gold.market_data.vol_60d` (confirm annualization) |
| r | Risk-free rate | `gold.regime_macro_inputs_daily.rate_2y`, converted to a decimal (there is no `gold.treasury_rates` table) |
| D | Default barrier | 0.5 × `long_term_debt` + `current_liabilities` from Silver `balance_sheet` |

- **Balance-sheet join:** use the latest report whose availability or filing date is ≤ `as_of_date`, never the period-end date.
- **Barrier caveat:** `current_liabilities` stands in for short-term debt because no short-term debt column exists. It overstates the KMV barrier (it includes payables and accruals), which biases DD downward. That is accepted and documented.
- **Units:** E and D must be on the same scale.

### Solver

- T = 1 and μ_A = r (risk-neutral).
- Seed: V_A⁽⁰⁾ = E + D and σ_A⁽⁰⁾ = σ_E·E/(E + D).
- Each iteration applies damped fixed-point updates with λ = 0.5:
  - σ_A ← (1−λ)·σ_A + λ·σ_E·E / (V_A·Φ(d₁))
  - V_A ← (1−λ)·V_A + λ·(E + D·e^(−rT)·Φ(d₂)) / Φ(d₁)
  - d₁ and d₂ are evaluated with the freshly updated σ_A.
- Stop when the maximum relative change is below 1e-6.
- **k_max = 200.** The default-boundary vector needs about 76 iterations, so k_max = 50 is insufficient.
- If the solver does not converge: `is_converged = false` and the output factors are null.

### Outputs

- DD = (ln(V_A/D) + (r − σ_A²/2)·T) / (σ_A·√T), **clipped to [0, 10] for every row**.
- PD = Φ(−DD).

### Edge cases

| Case | Output |
|---|---|
| D ≤ 0 | DD = 10, PD = Φ(−10) ≈ 0 |
| E missing or ≤ 0 | Null factors with `missing_market_cap` |
| Financials and REITs | Null factors with `sector_excluded`. Derive the sector and industry vocabulary from `core.symbols` values; `'Financial Services'` is unverified. |

### Test vectors (r = 0.03, T = 1)

| Case | E | σ_E | D | V_A | σ_A | DD | PD |
|---|---|---|---|---|---|---|---|
| Investment grade | 100 | 0.22 | 20 | 119.409 | 0.1842 | 9.769 | ≈ 0 |
| Stressed levered | 5 | 0.65 | 8 | 12.735 | 0.2607 | 1.768 | 0.0386 |
| Default boundary | 0.5 | 1.20 | 3 | 3.210 | 0.2710 | 0.225 | 0.4112 |

These replace the original plan's values. Its stressed and boundary rows were not reproducible.

### Storage (jobs repo)

- Table `gold.credit_risk_daily`, keyed by `(symbol, as_of_date)`, in the jobs repo's migration sequence. The next migration is `0044`; there is no `cp-0205`.
- Columns: `market_cap`, `default_barrier`, `asset_value`, `asset_volatility`, `distance_to_default`, `merton_pd`, `is_converged`, `exclusion_reason`.
- The job is chained after gold finance and market, not run on cron.
- It is exposed to strategies through `credit.distance_to_default` and `credit.merton_pd`, which need a universe binding and a gold column-lookup seed entry.

## 3. Opt-in Kelly sizing (AB#3567)

`BacktestSummary.kelly_fraction` is the full-Kelly fraction published by a backtest:

f* = p − (1 − p)/b, where p = `hit_rate` and b = `payoff_ratio`

It is null when either input is null or b ≤ 0.

A strategy opts in by adding `strategyRiskPolicy.exposure.kellySizing`. Presence is the opt-in; there is no enable toggle.

| Field | Default | Constraint |
|---|---|---|
| `referenceBacktestRunId` | required | 1–128 characters |
| `minClosedPositions` | 30 | ≥ 1 |
| `fractionMultiplier` | 0.25 (quarter Kelly) | (0, 1] |
| `floorScalar` | 0.25 | (0, 1], ≤ `capScalar` |
| `capScalar` | 1.0 | (0, 1] |
| `fallbackScalar` | 1.0 | within [`floorScalar`, `capScalar`] |

### Runtime rule

If the reference run is missing, unpublished, has `closed_positions < minClosedPositions`, or has no `kelly_fraction`:
- scalar = `fallbackScalar`
- emit `KELLY_POLICY_FALLBACK_TRIGGERED` with a typed reason

Otherwise:
- scalar = clamp(`fractionMultiplier` × `kelly_fraction`, `floorScalar`, `capScalar`)

Target weights are multiplied by the scalar, and the scalar never exceeds 1.0, so exposure is never levered above baseline. A negative Kelly fraction clamps to `floorScalar`.

This replaces the original design (floor 0.05, cap 0.25, fallback 1.0, multiplier unused). That design sized thin-evidence strategies at full exposure while cutting well-evidenced ones by at least 75%.

| Case | kelly_fraction | closed_positions | Scalar |
|---|---|---|---|
| Normal | 0.72 | 42 | clamp(0.18, 0.25, 1.0) = 0.25 |
| Strong | 2.0 | 42 | clamp(0.50, 0.25, 1.0) = 0.50 |
| Very strong | 6.0 | 42 | clamp(1.50, 0.25, 1.0) = 1.0 |
| Thin evidence | 2.0 | 12 | 1.0 (fallback) |

## Rollout

1. **Contracts 5.5.0** (this change): publish.
2. **runtime-common:**
   - Implement the Cornish-Fisher VaR/ES with the global guard.
   - Implement the Merton solver.
   - Populate the new `BacktestSummary` fields.
   - Apply `kellySizing` in the allocator.
   - Pin to contracts 5.5.0.
3. **jobs:**
   - Migration `0044_gold_credit_risk_daily.sql`.
   - A gold credit-risk job modeled on `tasks/finance_data/gold_finance_data.py`.
   - The column-lookup seed entry and the universe bindings.
4. **AB#3568:** move `PortfolioRiskMeasureKind` into contracts, then add `parametric_var_es`.

## Verification

- Pin every test vector above at absolute tolerance 1e-4 (5e-4 for V_A).
- Gaussian parity at S = K = 0.
- A boundary-case convergence test within k_max.
- A point-in-time join test with a future-dated balance-sheet row.
- A Kelly table test covering every row above.
