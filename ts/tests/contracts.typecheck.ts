import type {
  AiChatStreamEvent,
  AuthSessionStatus,
  AcknowledgeBrokerAlertRequest,
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
  BrokerAccountActionResponse,
  BrokerAccountDetail,
  BrokerAccountListResponse,
  BrokerAccountSummary,
  CongressTradeEventListResponse,
  GovernmentSignalMappingOverrideRequest,
  GovernmentSignalPortfolioExposureRequest,
  PauseBrokerSyncRequest,
  RunPinsResponse,
  RunRecordResponse,
  RunStatusResponse,
  PortfolioAccount,
  PortfolioRevision,
  PortfolioSnapshot,
  PortfolioUpsertRequest,
  SymbolCleanupRunSummary,
  SymbolEnrichmentResolveRequest,
  SymbolEnrichmentSymbolDetailResponse,
  ReconnectBrokerAccountRequest,
  RefreshBrokerAccountRequest,
  StrategyAllocationExposureRequest,
  StrategyAllocationExposureResponse,
  StrategyComparisonRequest,
  StrategyComparisonResponse,
  StrategyConfig,
  StrategyRiskPolicy,
  StrategyScenarioForecastRequest,
  StrategyScenarioForecastResponse,
  StrategyTradeHistoryRequest,
  StrategyTradeHistoryResponse,
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

const strategyRiskPolicy: StrategyRiskPolicy = {
  grossExposureLimit: 1,
  netExposureLimit: 1,
  singleNameMaxWeight: 0.08,
  sectorMaxWeight: 0.25,
  turnoverBudget: 0.35,
  maxDrawdownLimit: 0.2,
  liquidityParticipationRate: 0.1,
  maxTradeNotionalBaseCcy: 250000,
  notes: "Operator risk envelope.",
};

const comparisonRequest: StrategyComparisonRequest = {
  strategies: [
    { strategyName: "quality-trend", strategyVersion: 4, role: "baseline" },
    { strategyName: "defensive-value", strategyVersion: 2, role: "challenger" },
  ],
  startDate: "2026-01-01",
  endDate: "2026-03-31",
  benchmarkSymbol: "SPY",
  costModel: "institutional",
  barSize: "1d",
  regimeModelName: "default-regime",
  scenarioAssumption: "high_volatility",
  includeForecast: true,
};

const comparisonResponse: StrategyComparisonResponse = {
  asOf: "2026-04-29T12:00:00Z",
  benchmarkSymbol: "SPY",
  costModel: "institutional",
  barSize: "1d",
  strategies: comparisonRequest.strategies,
  metrics: [
    {
      metric: "sharpe_ratio",
      label: "Sharpe",
      unit: "score",
      values: {
        "quality-trend": 1.2,
        "defensive-value": 0.9,
      },
      winnerStrategyName: "quality-trend",
      notes: "",
    },
  ],
  runEvidence: [
    {
      strategyName: "quality-trend",
      strategyVersion: 4,
      runId: "run-123",
      startDate: "2026-01-01",
      endDate: "2026-03-31",
      barSize: "1d",
      costModel: "institutional",
      resultSchemaVersion: 4,
      warnings: [],
    },
  ],
  warnings: [],
  blockedReasons: [],
};

const forecastRequest: StrategyScenarioForecastRequest = {
  strategies: comparisonRequest.strategies,
  asOfDate: "2026-04-29",
  horizon: "3M",
  regimeModelName: "default-regime",
  regimeAssumption: "high_volatility",
  costDragOverrideBps: 12,
  tunableParameters: {
    topN: 25,
    longOnly: true,
  },
};

const forecastResponse: StrategyScenarioForecastResponse = {
  asOf: "2026-04-29T12:00:00Z",
  horizon: "3M",
  regimeAssumption: "high_volatility",
  source: "control_plane",
  forecasts: [
    {
      strategyName: "quality-trend",
      strategyVersion: 4,
      expectedReturn: 0.03,
      expectedActiveReturn: 0.01,
      downside: -0.04,
      upside: 0.08,
      confidence: "medium",
      sampleSize: 12,
      sampleMode: "regime_conditioned",
      appliedRegimeCode: "high_volatility",
      source: "backtest",
      notes: ["Uses matched historical regime windows."],
    },
  ],
  warnings: [],
};

const allocationExposureRequest: StrategyAllocationExposureRequest = {
  strategyName: "quality-trend",
  strategyVersion: 4,
  accountIds: ["acct-001"],
  includePositions: true,
};

const allocationExposureResponse: StrategyAllocationExposureResponse = {
  strategyName: "quality-trend",
  strategyVersion: 4,
  asOf: "2026-04-29T12:00:00Z",
  totalMarketValue: 100000,
  aggregateTargetWeight: 0.6,
  aggregateActualWeight: 0.58,
  aggregateGrossExposure: 0.58,
  aggregateNetExposure: 0.58,
  exposures: [
    {
      accountId: "acct-001",
      accountName: "Core Long Only",
      portfolioName: "core-balanced",
      portfolioVersion: 3,
      sleeveId: "quality-core",
      sleeveName: "Quality Core",
      strategyName: "quality-trend",
      strategyVersion: 4,
      asOf: "2026-04-29",
      targetWeight: 0.6,
      actualWeight: 0.58,
      drift: -0.02,
      marketValue: 58000,
      grossExposure: 0.58,
      netExposure: 0.58,
      status: "active",
    },
  ],
  positions: [
    {
      accountId: "acct-001",
      portfolioName: "core-balanced",
      sleeveId: "quality-core",
      symbol: "MSFT",
      asOf: "2026-04-29",
      quantity: 10,
      marketValue: 4200,
      weight: 0.042,
    },
  ],
  warnings: [],
};

const tradeHistoryRequest: StrategyTradeHistoryRequest = {
  strategyName: "quality-trend",
  strategyVersion: 4,
  startDate: "2026-01-01",
  endDate: "2026-04-29",
  sources: ["backtest", "portfolio_ledger"],
  limit: 200,
  offset: 0,
};

const tradeHistoryResponse: StrategyTradeHistoryResponse = {
  strategyName: "quality-trend",
  strategyVersion: 4,
  trades: [
    {
      source: "portfolio_ledger",
      timestamp: "2026-04-29T14:30:00Z",
      symbol: "MSFT",
      side: "buy",
      quantity: 10,
      price: 420,
      notional: 4200,
      commission: 1,
      slippageCost: 0.5,
      realizedPnl: null,
      accountId: "acct-001",
      portfolioName: "core-balanced",
      runId: null,
      orderId: null,
      eventId: "evt-001",
    },
  ],
  total: 1,
  limit: 200,
  offset: 0,
  warnings: [],
};

const runtimeConfig: UiRuntimeConfig = {
  apiBaseUrl: "/api",
  authSessionMode: "cookie",
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

const brokerSummary: BrokerAccountSummary = {
  accountId: "alpaca-core",
  broker: "alpaca",
  name: "Core Long Only",
  accountNumberMasked: "****1234",
  baseCurrency: "USD",
  overallStatus: "warning",
  tradeReadiness: "blocked",
  tradeReadinessReason: "Reconnect required.",
  highestAlertSeverity: "critical",
  connectionHealth: {
    overallStatus: "warning",
    authStatus: "reauth_required",
    connectionState: "reconnect_required",
    syncStatus: "stale",
    lastSuccessfulSyncAt: "2026-04-20T13:30:00Z",
    staleReason: "Positions are stale.",
    syncPaused: false,
  },
  equity: 250000,
  cash: 42000,
  buyingPower: 180000,
  openPositionCount: 12,
  openOrderCount: 3,
  lastSyncedAt: "2026-04-20T13:30:00Z",
  snapshotAsOf: "2026-04-20T13:29:00Z",
  activePortfolioName: "growth-core",
  strategyLabel: "Quality / Momentum",
  alertCount: 2,
};

const brokerList: BrokerAccountListResponse = {
  accounts: [brokerSummary],
  generatedAt: "2026-04-20T13:45:00Z",
};

const brokerDetail: BrokerAccountDetail = {
  account: brokerList.accounts[0],
  capabilities: {
    canReadBalances: true,
    canReadPositions: true,
    canReadOrders: true,
    canTrade: true,
    canReconnect: true,
    canPauseSync: true,
    canRefresh: true,
    canAcknowledgeAlerts: true,
    canReadTradingPolicy: true,
    canWriteTradingPolicy: true,
    canReadAllocation: true,
    canWriteAllocation: true,
    canReleaseTradeConfirmation: true,
  },
  accountType: "margin",
  tradingBlocked: true,
  tradingBlockedReason: "Reconnect before trading resumes.",
  dayTradeBuyingPower: 95000,
  maintenanceExcess: 32000,
  alerts: [
    {
      alertId: "alert-1",
      accountId: "alpaca-core",
      severity: "critical",
      status: "open",
      code: "auth_expired",
      title: "Broker token expired",
      message: "Reconnect the broker account.",
      observedAt: "2026-04-20T13:31:00Z",
    },
  ],
  syncRuns: [
    {
      runId: "sync-1",
      accountId: "alpaca-core",
      trigger: "manual",
      scope: "full",
      status: "failed",
      requestedAt: "2026-04-20T13:31:00Z",
      completedAt: "2026-04-20T13:32:00Z",
      warningCount: 1,
      errorMessage: "Token refresh failed.",
    },
  ],
  recentActivity: [
    {
      activityId: "activity-1",
      accountId: "alpaca-core",
      activityType: "acknowledge_alert",
      status: "completed",
      requestedAt: "2026-04-20T13:40:00Z",
      completedAt: "2026-04-20T13:40:02Z",
      actor: "ops@example.com",
      summary: "Acknowledged token expiry.",
      relatedAlertId: "alert-1",
    },
  ],
};

const reconnectRequest: ReconnectBrokerAccountRequest = {
  reason: "Manual reconnect from the desk.",
};

const pauseRequest: PauseBrokerSyncRequest = {
  paused: false,
  reason: "Resume after reconnect.",
};

const refreshRequest: RefreshBrokerAccountRequest = {
  scope: "full",
  force: true,
  reason: "Operator refresh.",
};

const acknowledgeRequest: AcknowledgeBrokerAlertRequest = {
  note: "Queued for desk follow-up.",
};

const actionResponse: BrokerAccountActionResponse = {
  actionId: "action-1",
  accountId: "alpaca-core",
  action: "refresh",
  status: "accepted",
  requestedAt: "2026-04-20T13:45:00Z",
  message: "Refresh queued.",
  resultingConnectionHealth: {
    overallStatus: "warning",
    authStatus: "reauth_required",
    connectionState: "reconnect_required",
    syncStatus: "syncing",
    syncPaused: false,
  },
  tradeReadiness: "review",
  syncPaused: false,
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
void strategyRiskPolicy;
void comparisonRequest;
void comparisonResponse;
void forecastRequest;
void forecastResponse;
void allocationExposureRequest;
void allocationExposureResponse;
void tradeHistoryRequest;
void tradeHistoryResponse;
void runtimeConfig;
void authSession;
void brokerSummary;
void brokerList;
void brokerDetail;
void reconnectRequest;
void pauseRequest;
void refreshRequest;
void acknowledgeRequest;
void actionResponse;
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
  description: "",
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
  description: "",
  allocationMode: "percent",
  allocations: [
    {
      sleeveId: "quality-core",
      strategy: {
        strategyName: "quality-trend",
        strategyVersion: 4,
      },
      allocationMode: "percent",
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
      allocationMode: "percent",
      targetWeight: 0.4,
      enabled: true,
      rebalancePriority: 1,
      sleeveName: "Defensive",
      notes: "",
    },
  ],
  notes: "",
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
  description: "",
  allocationMode: "percent",
  allocations: portfolioRevision.allocations,
  notes: "",
};

const congressEvents: CongressTradeEventListResponse = {
  events: [],
  total: 0,
  limit: 50,
  offset: 0,
};

const overrideRequest: GovernmentSignalMappingOverrideRequest = {
  action: "map",
  symbol: "LMT",
  reason: "Manual recipient mapping",
};

const exposureRequest: GovernmentSignalPortfolioExposureRequest = {
  holdings: [{ symbol: "LMT", market_value: 100000, portfolio_weight: 0.05 }],
};

const resolveRequest: SymbolEnrichmentResolveRequest = {
  symbol: "AAPL",
  overwriteMode: "fill_missing",
  requestedFields: ["sector_norm", "issuer_summary_short"],
  providerFacts: {
    symbol: "AAPL",
    name: "Apple Inc.",
    exchange: "NASDAQ",
  },
};

const detail: SymbolEnrichmentSymbolDetailResponse = {
  providerFacts: {
    symbol: "AAPL",
  },
  currentProfile: {
    symbol: "AAPL",
    sourceKind: "ai",
    validationStatus: "accepted",
    sector_norm: "Technology",
  },
  overrides: [],
  history: [],
};

const runSummary: SymbolCleanupRunSummary = {
  runId: "run-1",
  status: "queued",
  mode: "fill_missing",
  queuedCount: 1,
  claimedCount: 0,
  completedCount: 0,
  failedCount: 0,
  acceptedUpdateCount: 0,
  rejectedUpdateCount: 0,
  lockedSkipCount: 0,
  overwriteCount: 0,
};

const aiEvent: AiChatStreamEvent = {
  sequenceNumber: 1,
  event: "completed",
  data: {
    requestId: "req-1",
    model: "gpt-5.4",
    outputText: "Apple summary",
    reasoningSummary: "",
  },
};

void catalog;
void preview;
void condition;
void portfolioAccount;
void portfolioRevision;
void portfolioSnapshot;
void portfolioUpsert;
void congressEvents;
void overrideRequest;
void exposureRequest;
void resolveRequest;
void detail;
void runSummary;
void aiEvent;
