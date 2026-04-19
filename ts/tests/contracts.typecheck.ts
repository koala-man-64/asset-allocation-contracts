import type {
  AuthSessionStatus,
  BacktestClaimRequest,
  BacktestCompleteRequest,
  BacktestLookupRequest,
  BacktestLookupResponse,
  BacktestFailRequest,
  BacktestResultLinks,
  BacktestRunRequest,
  BacktestRunResponse,
  BacktestStartRequest,
  BacktestStreamEvent,
  RunPinsResponse,
  RunRecordResponse,
  RunStatusResponse,
  PortfolioAccount,
  PortfolioRevision,
  PortfolioSnapshot,
  PortfolioUpsertRequest,
  StrategyConfig,
  UniverseCatalogResponse,
  TimeseriesPointResponse,
  UiRuntimeConfig,
  UniverseCondition,
  UniversePreviewResponse,
} from "../src/contracts";

const catalog: UniverseCatalogResponse = {
  source: "postgres_gold",
  fields: [
    {
      id: "market.close",
      label: "Close Price",
      valueKind: "number",
      operators: ["eq", "gt"],
    },
  ],
};

const preview: UniversePreviewResponse = {
  source: "postgres_gold",
  symbolCount: 2,
  sampleSymbols: ["AAPL", "MSFT"],
  fieldsUsed: ["market.close", "quality.piotroski_f_score"],
  warnings: [],
};

const strategy: StrategyConfig = {
  universeConfigName: "core-us-equities",
  rebalance: "monthly",
  longOnly: true,
  topN: 20,
  lookbackWindow: 63,
  holdingPeriod: 21,
  costModel: "default",
  intrabarConflictPolicy: "priority_order",
  exits: [],
};

const runtimeConfig: UiRuntimeConfig = {
  apiBaseUrl: "/api",
  oidcEnabled: true,
  authRequired: true,
  oidcAuthority: "https://login.example.com/tenant/v2.0",
  oidcClientId: "11111111-2222-3333-4444-555555555555",
  oidcScopes: ["openid", "profile"],
  oidcAudience: ["asset-allocation-api"],
};

const authSession: AuthSessionStatus = {
  authMode: "oidc",
  subject: "user-123",
  requiredRoles: ["admin"],
  grantedRoles: ["admin"],
};

const claimRequest: BacktestClaimRequest = {
  executionName: "backtest-job-01",
};

const startRequest: BacktestStartRequest = {
  executionName: "backtest-job-01",
};

const completeRequest: BacktestCompleteRequest = {
  summary: {
    run_id: "run-123",
    total_return: 0.12,
  },
};

const failRequest: BacktestFailRequest = {
  error: "Backtest failed",
};

const lookupRequest: BacktestLookupRequest = {
  strategyRef: {
    strategyName: "quality-trend",
    strategyVersion: 4,
  },
  startTs: "2026-03-08T00:00:00Z",
  endTs: "2026-03-09T00:00:00Z",
  barSize: "1d",
  runName: "lookup-smoke",
};

const runRequest: BacktestRunRequest = {
  strategyConfig: strategy,
  startTs: "2026-03-08T00:00:00Z",
  endTs: "2026-03-09T00:00:00Z",
  barSize: "1d",
  runName: "run-smoke",
};

const runRecord: RunRecordResponse = {
  run_id: "run-123",
  status: "completed",
  submitted_at: "2026-03-08T00:00:00Z",
  strategy_name: "quality-trend",
  strategy_version: 4,
  bar_size: "1d",
  execution_name: "backtest-job-01",
};

const pins: RunPinsResponse = {
  strategyName: "quality-trend",
  strategyVersion: 4,
  rankingSchemaName: "quality-momentum",
  rankingSchemaVersion: 7,
  universeName: "core-us-equities",
  universeVersion: 5,
  regimeModelName: "default-regime",
  regimeModelVersion: 2,
};

const runStatus: RunStatusResponse = {
  ...runRecord,
  results_ready_at: "2026-03-08T01:05:00Z",
  results_schema_version: 4,
  pins,
};

const links: BacktestResultLinks = {
  summaryUrl: "/api/backtests/run-123/summary",
  metricsTimeseriesUrl: "/api/backtests/run-123/metrics/timeseries",
  metricsRollingUrl: "/api/backtests/run-123/metrics/rolling",
  tradesUrl: "/api/backtests/run-123/trades",
  closedPositionsUrl: "/api/backtests/run-123/positions/closed",
};

const lookupResponse: BacktestLookupResponse = {
  found: true,
  state: "completed",
  run: runStatus,
  result: {
    run_id: "run-123",
    total_return: 0.12,
  },
  links,
};

const runResponse: BacktestRunResponse = {
  run: runStatus,
  created: true,
  reusedInflight: false,
  streamUrl: "/api/backtests/run-123/events",
};

const streamEvent: BacktestStreamEvent = {
  event: "completed",
  run: runStatus,
  summary: {
    run_id: "run-123",
    total_return: 0.12,
  },
  metadata: {
    results_schema_version: 4,
    bar_size: "1d",
    periods_per_year: 252,
    strategy_scope: "long_only",
  },
  links,
};

const point: TimeseriesPointResponse = {
  date: "2026-03-09",
  portfolio_value: 102.0,
  drawdown: 0.01,
  period_return: 0.02,
  trade_count: 5,
};

const condition: UniverseCondition = {
  kind: "condition",
  field: "market.close",
  operator: "gt",
  value: 10,
};

void strategy;
void runtimeConfig;
void authSession;
void claimRequest;
void startRequest;
void completeRequest;
void failRequest;
void lookupRequest;
void runRequest;
void runRecord;
void pins;
void runStatus;
void links;
void lookupResponse;
void runResponse;
void streamEvent;
void point;
const portfolioAccount: PortfolioAccount = {
  accountId: "acct-001",
  name: "Core Long Only",
  status: "active",
  mode: "internal_model_managed",
  accountingDepth: "position_level",
  cadenceMode: "strategy_native",
  baseCurrency: "USD",
  inceptionDate: "2026-01-02",
  mandate: "Internal model sleeve account",
  openAlertCount: 1,
};

const portfolioRevision: PortfolioRevision = {
  portfolioName: "core-balanced",
  version: 3,
  allocations: [
    {
      sleeveId: "quality-core",
      strategy: {
        strategyName: "quality-trend",
        strategyVersion: 4,
      },
      targetWeight: 0.6,
      enabled: true,
      rebalancePriority: 0,
      sleeveName: "Quality Core",
      notes: "",
    },
    {
      sleeveId: "defensive",
      strategy: {
        strategyName: "defensive-value",
        strategyVersion: 2,
      },
      targetWeight: 0.4,
      enabled: true,
      rebalancePriority: 1,
      sleeveName: "Defensive",
      notes: "",
    },
  ],
};

const portfolioSnapshot: PortfolioSnapshot = {
  accountId: "acct-001",
  accountName: "Core Long Only",
  asOf: "2026-03-31",
  nav: 1025000,
  cash: 25000,
  grossExposure: 1,
  netExposure: 1,
  sinceInceptionPnl: 25000,
  sinceInceptionReturn: 0.025,
  currentDrawdown: 0.03,
  openAlertCount: 1,
  freshness: [{ domain: "valuation", state: "fresh", reason: "" }],
  slices: [],
};

const portfolioUpsert: PortfolioUpsertRequest = {
  name: "core-balanced",
  allocations: portfolioRevision.allocations,
};

void catalog;
void preview;
void condition;
void portfolioAccount;
void portfolioRevision;
void portfolioSnapshot;
void portfolioUpsert;
