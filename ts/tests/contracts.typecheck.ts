import type {
  AiChatStreamEvent,
  AuthProvider,
  AuthSessionStatus,
  PasswordAuthSessionRequest,
  AcknowledgeBrokerAlertRequest,
  BacktestClaimRequest,
  BacktestCompleteRequest,
  BacktestDataQualityEventListResponse,
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
  StrategyConfig,
  UniverseCatalogResponse,
  TimeseriesPointResponse,
  UiRuntimeConfig,
  UniverseCondition,
  UniversePreviewResponse,
} from "../src/contracts";
import {
  GOLD_MARKET_SILVER_SOURCE_COLUMNS,
  LEGACY_SILVER_MARKET_COLUMNS,
  SILVER_MARKET_COLUMNS,
  SILVER_MARKET_CORPORATE_ACTION_COLUMNS,
} from "../src";
import type { SilverMarketColumn } from "../src";

const silverMarketColumns: readonly SilverMarketColumn[] = SILVER_MARKET_COLUMNS;
const silverCorporateActionColumns = SILVER_MARKET_CORPORATE_ACTION_COLUMNS satisfies readonly SilverMarketColumn[];
const goldMarketSourceColumns = GOLD_MARKET_SILVER_SOURCE_COLUMNS satisfies readonly SilverMarketColumn[];
const legacySilverMarketColumnCount: 9 = LEGACY_SILVER_MARKET_COLUMNS.length;
const silverMarketColumnCount: 11 = SILVER_MARKET_COLUMNS.length;
const silverCorporateActionColumnCount: 2 = silverCorporateActionColumns.length;
const goldMarketSourceColumnCount: 9 = goldMarketSourceColumns.length;

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
  authSessionMode: "cookie",
  authProvider: "oidc",
  oidcEnabled: true,
  authRequired: true,
  oidcAuthority: "https://login.example.com/tenant/v2.0",
  oidcClientId: "11111111-2222-3333-4444-555555555555",
  oidcScopes: ["openid", "profile"],
  oidcAudience: ["asset-allocation-api"],
};

const authProvider: AuthProvider = "password";

const authSession: AuthSessionStatus = {
  authMode: "oidc",
  subject: "user-123",
  requiredRoles: ["admin"],
  grantedRoles: ["admin"],
};

const passwordSessionRequest: PasswordAuthSessionRequest = {
  password: "operator-secret",
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

const dataQualityEvents: BacktestDataQualityEventListResponse = {
  events: [
    {
      run_id: "run-123",
      event_seq: 1,
      bar_ts: "2026-03-08T14:35:00Z",
      severity: "error",
      table_name: "fundamental_signal_daily",
      symbol: "AAPL",
      field_name: "quality_score",
      reason_code: "available_after_bar",
      action: "exclude_value",
      details: {
        availableAt: "2026-03-08T14:37:00Z",
      },
    },
  ],
  total: 1,
  limit: 50,
  offset: 0,
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
void authProvider;
void authSession;
void passwordSessionRequest;
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
void dataQualityEvents;
void point;
const portfolioAccount: PortfolioAccount = {
  accountId: "acct-001",
  name: "Core Long Only",
  description: "",
  status: "active",
  mode: "internal_model_managed",
  accountingDepth: "position_level",
  cadenceMode: "strategy_native",
  rebalanceCadence: "weekly",
  rebalanceAnchor: "Strategy native cadence",
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
