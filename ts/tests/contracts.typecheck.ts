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
  BrokerAccountOnboardingCandidate,
  BrokerAccountOnboardingCandidateListResponse,
  BrokerAccountOnboardingRequest,
  BrokerAccountOnboardingResponse,
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
  SymbolResolutionResult,
  ReconnectBrokerAccountRequest,
  RefreshBrokerAccountRequest,
  ConfigIdentity,
  ConfigReference,
  ExitPolicyPreset,
  RankingSchemaPreset,
  RebalancePolicyPreset,
  RegimePolicyPreset,
  StrategyConfig,
  StrategyComponentRefs,
  StrategyRiskPolicyPreset,
  UniverseConfigPreset,
  UniverseCatalogResponse,
  TimeseriesPointResponse,
  TradeAccountSummary,
  UiRuntimeConfig,
  UniverseCondition,
  UniversePreviewResponse,
} from "../src/contracts";
import {
  GOLD_MARKET_SILVER_SOURCE_COLUMNS,
  LEGACY_SILVER_MARKET_COLUMNS,
  SILVER_MARKET_COLUMNS,
  SILVER_MARKET_CORPORATE_ACTION_COLUMNS,
  SYMBOL_ALIAS_RULES,
  SYMBOL_ALIAS_RULESET_VERSION,
} from "../src";
import type { SilverMarketColumn } from "../src";

const silverMarketColumns: readonly SilverMarketColumn[] = SILVER_MARKET_COLUMNS;
const silverCorporateActionColumns = SILVER_MARKET_CORPORATE_ACTION_COLUMNS satisfies readonly SilverMarketColumn[];
const goldMarketSourceColumns = GOLD_MARKET_SILVER_SOURCE_COLUMNS satisfies readonly SilverMarketColumn[];
const legacySilverMarketColumnCount: 9 = LEGACY_SILVER_MARKET_COLUMNS.length;
const silverMarketColumnCount: 11 = SILVER_MARKET_COLUMNS.length;
const silverCorporateActionColumnCount: 2 = silverCorporateActionColumns.length;
const goldMarketSourceColumnCount: 9 = goldMarketSourceColumns.length;
const symbolAliasRules = SYMBOL_ALIAS_RULES;
const symbolAliasRulesetVersion: 'symbol-alias-v1' = SYMBOL_ALIAS_RULESET_VERSION;
const massiveVixRule = symbolAliasRules.find((rule) => rule.providerSymbol === 'I:VIX');
const massiveVixCanonical: '^VIX' | undefined = massiveVixRule?.canonicalSymbol;

const symbolResolution: SymbolResolutionResult = {
  status: "resolved",
  provider: "massive",
  domain: "market",
  inputSymbol: "I:VIX",
  canonicalSymbol: "^VIX",
  providerSymbol: "I:VIX",
  mappingVersion: "symbol-alias-v1",
};

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
  componentRefs: {
    universe: {
      name: "us_large_liquid",
      version: 1,
    },
    ranking: {
      name: "quality_momentum",
      version: 1,
    },
    rebalance: {
      name: "monthly_last_trading_day",
      version: 1,
    },
    regimePolicy: {
      name: "observe_only_default",
      version: 1,
    },
    riskPolicy: {
      name: "balanced_long_only",
      version: 1,
    },
    exitPolicy: {
      name: "rank_decay_exit",
      version: 1,
    },
  },
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

const configReference: ConfigReference = {
  name: "us_large_liquid",
  version: 1,
};

const configIdentity: ConfigIdentity = {
  name: "us_large_liquid",
  version: 1,
  status: "active",
  description: "US large-cap liquid common equities.",
  intendedUse: "validation",
  thesis: "Stable baseline universe for long-only ranking research.",
  whatToMonitor: ["constituent count", "turnover", "liquidity drift"],
};

const reusableComponentRefs: StrategyComponentRefs = {
  universe: configReference,
  ranking: { name: "momentum_12_1", version: 1 },
  rebalance: { name: "quarterly_last_trading_day", version: 1 },
  regimePolicy: { name: "observe_only_default", version: 1 },
  riskPolicy: { name: "balanced_long_only", version: 1 },
  exitPolicy: { name: "rebalance_only", version: 1 },
};

const universePreset: UniverseConfigPreset = {
  identity: configIdentity,
  config: {
    source: "postgres_gold",
    root: {
      kind: "group",
      operator: "and",
      clauses: [
        { kind: "condition", field: "security.country", operator: "eq", value: "US" },
        { kind: "condition", field: "security.primary_listing", operator: "eq", value: true },
        { kind: "condition", field: "security.market_cap", operator: "gte", value: 10000000000 },
        { kind: "condition", field: "market.dollar_volume_20d", operator: "gte", value: 50000000 },
        { kind: "condition", field: "security.is_price_liquidity_eligible", operator: "eq", value: true },
      ],
    },
  },
};

const rankingPreset: RankingSchemaPreset = {
  identity: {
    ...configIdentity,
    name: "quality_momentum",
    thesis: "Pair durable quality with medium-term price strength.",
  },
  config: {
    universeConfigName: "us_large_liquid",
    groups: [
      {
        name: "momentum",
        weight: 1,
        factors: [
          {
            name: "return_126d",
            table: "market_data",
            column: "return_126d",
            weight: 1,
            direction: "desc",
            missingValuePolicy: "zero",
            transforms: [{ type: "percentile_rank", params: {} }],
          },
        ],
        transforms: [],
      },
    ],
    overallTransforms: [],
  },
};

const rebalancePreset: RebalancePolicyPreset = {
  identity: {
    ...configIdentity,
    name: "monthly_last_trading_day",
    thesis: "Monthly close signal with next-open execution.",
  },
  config: {
    frequency: "monthly",
    executionTiming: "next_bar_open",
    cadence: "monthly",
    dayRule: "last_trading_day",
    anchor: "next_open",
    tradeDelayBars: 0,
    driftThresholdBps: 0,
    maxTurnoverPerRebalance: 0.35,
    minTradeNotional: 0,
    cashBufferPct: 1,
    allowPartialRebalance: true,
    closeRemovedPositions: true,
  },
};

const regimePreset: RegimePolicyPreset = {
  identity: {
    ...configIdentity,
    name: "observe_only_default",
    thesis: "Tag market state without changing exposures.",
  },
  config: {
    modelName: "default-regime",
    mode: "observe_only",
  },
};

const riskPreset: StrategyRiskPolicyPreset = {
  identity: {
    ...configIdentity,
    name: "balanced_long_only",
    thesis: "Limit strategy drawdowns while keeping the first grid simple.",
  },
  config: {
    enabled: true,
    scope: "strategy",
    stopLoss: {
      id: "strategy-stop-loss",
      enabled: true,
      basis: "strategy_nav_drawdown",
      thresholdPct: 8,
      action: "reduce_exposure",
      reductionPct: 50,
    },
    reentry: {
      cooldownBars: 0,
      requireApproval: false,
    },
  },
};

const exitPreset: ExitPolicyPreset = {
  identity: {
    ...configIdentity,
    name: "rank_decay_exit",
    thesis: "Exit names that fall below the retained-rank cutoff.",
  },
  config: {
    intrabarConflictPolicy: "priority_order",
    exits: [
      {
        id: "rank-decay-40",
        type: "rank_decay",
        scope: "position",
        action: "exit_full",
        minHoldBars: 0,
        rankThreshold: 40,
      },
    ],
  },
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

const kalshiBrokerSummary: BrokerAccountSummary = {
  accountId: "kalshi-live-subaccount-0",
  broker: "kalshi",
  name: "Kalshi Live Subaccount 0",
  accountNumberMasked: "GEN-0001",
  baseCurrency: "USD",
  overallStatus: "warning",
  tradeReadiness: "ready",
  connectionHealth: {
    overallStatus: "warning",
    authStatus: "authenticated",
    connectionState: "degraded",
    syncStatus: "never_synced",
    staleReason: "Seeded account; provider refresh has not completed.",
    syncPaused: false,
  },
  equity: 0,
  cash: 0,
  buyingPower: 0,
  openPositionCount: 0,
  openOrderCount: 0,
  alertCount: 0,
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

const onboardingCandidate: BrokerAccountOnboardingCandidate = {
  candidateId: "alpaca:paper:acct-paper",
  provider: "alpaca",
  environment: "paper",
  suggestedAccountId: "alpaca-paper-acct-paper",
  displayName: "Alpaca Paper",
  accountNumberMasked: "****1234",
  baseCurrency: "USD",
  state: "available",
  allowedExecutionPostures: ["monitor_only", "paper"],
  blockedExecutionPostureReasons: {
    sandbox: "Sandbox execution is only available for sandbox accounts.",
    live: "Live execution requires live account approval.",
  },
  canOnboard: true,
};

const onboardingCandidates: BrokerAccountOnboardingCandidateListResponse = {
  candidates: [onboardingCandidate],
  discoveryStatus: "completed",
  message: "Broker account discovery completed.",
  generatedAt: "2026-05-03T20:00:00Z",
};

const onboardingRequest: BrokerAccountOnboardingRequest = {
  candidateId: onboardingCandidate.candidateId,
  provider: "alpaca",
  environment: "paper",
  displayName: "Alpaca Paper",
  readiness: "review",
  executionPosture: "paper",
  initialRefresh: true,
  reason: "Initial account onboarding for paper trading.",
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

const kalshiTradeAccount: TradeAccountSummary = {
  accountId: "kalshi-live-subaccount-0",
  name: "Kalshi Live Subaccount 0",
  provider: "kalshi",
  environment: "live",
  accountNumberMasked: "GEN-0001",
  baseCurrency: "USD",
  readiness: "ready",
  capabilities: {
    canReadAccount: true,
    canReadPositions: true,
    canReadOrders: true,
    canReadHistory: true,
    canPreview: false,
    canSubmitPaper: false,
    canSubmitSandbox: false,
    canSubmitLive: false,
    canCancel: false,
    supportsMarketOrders: false,
    supportsLimitOrders: false,
    supportsStopOrders: false,
    supportsFractionalQuantity: false,
    supportsNotionalOrders: false,
    supportsEquities: false,
    supportsEtfs: false,
    supportsOptions: false,
    readOnly: true,
    unsupportedReason: "Kalshi trade desk execution is not supported in v1.",
  },
  cash: 0,
  buyingPower: 0,
  equity: 0,
  openOrderCount: 0,
  positionCount: 0,
  unresolvedAlertCount: 0,
  killSwitchActive: false,
  freshness: {
    balancesState: "unknown",
    positionsState: "unknown",
    ordersState: "unknown",
    staleReason: "Seeded account; provider refresh has not completed.",
  },
  confirmationRequired: false,
};

const onboardingResponse: BrokerAccountOnboardingResponse = {
  account: brokerSummary,
  created: true,
  reenabled: false,
  refreshAction: actionResponse,
  audit: {
    auditId: "audit-1",
    accountId: brokerSummary.accountId,
    category: "onboarding",
    outcome: "saved",
    requestedAt: "2026-05-03T20:00:01Z",
    grantedRoles: ["AssetAllocation.AccountPolicy.Write"],
    summary: "Onboarded broker account.",
    before: {},
    after: { executionPosture: onboardingRequest.executionPosture },
  },
  message: "Broker account onboarded.",
  generatedAt: "2026-05-03T20:00:02Z",
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
void onboardingCandidate;
void onboardingCandidates;
void onboardingRequest;
void actionResponse;
void onboardingResponse;
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
void configReference;
void configIdentity;
void reusableComponentRefs;
void universePreset;
void rankingPreset;
void rebalancePreset;
void regimePreset;
void riskPreset;
void exitPreset;
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
