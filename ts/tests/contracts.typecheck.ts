import type {
  AiChatStreamEvent,
  AgentProfileConfig,
  AgentProfilePreset,
  AgentStrategyBinding,
  AgentStrategyResolutionPreview,
  AuthProvider,
  AuthSessionStatus,
  AcknowledgeBrokerAlertRequest,
  BacktestBenchmarkAttribution,
  BacktestClaimRequest,
  BacktestCompleteRequest,
  BacktestDataQualityEventListResponse,
  BacktestLookupRequest,
  BacktestLookupResponse,
  BacktestFailRequest,
  BacktestPolicyEventListResponse,
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
  BrokerTradeApprovalPolicy,
  CongressTradeEventListResponse,
  CurrencyIntradayBar,
  CurrencyIntradayBarInterval,
  CurrencyIntradayBarsResponse,
  LiveCurrencyPriceSnapshot,
  LiveCurrencyPriceTick,
  LiveMarketPriceStatus,
  LiveStockAggregateSnapshot,
  LiveStockTradeSnapshot,
  LiveStockTradeTick,
  GovernmentSignalMappingOverrideRequest,
  GovernmentSignalPortfolioExposureRequest,
  IntradayMonitorCompleteRequest,
  IntradayRefreshClaimRequest,
  IntradayRefreshDomain,
  IntradayWatchlistUpsertRequest,
  PipelineActionResponse,
  PipelineQueueActionRequest,
  PipelineSyncView,
  PauseBrokerSyncRequest,
  PullRequestSyncView,
  OptionBacktestResult,
  OptionBrokerConstraintProfile,
  OptionPayoffProfile,
  OptionStrategyLadderResponse,
  OptionStrategyTemplate,
  NotificationActionDetailResponse,
  NotificationStatusResponse,
  RunPinsResponse,
  RunRecordResponse,
  RunStatusResponse,
  PortfolioAccount,
  PortfolioRevision,
  PortfolioSnapshot,
  TradeResponse,
  PortfolioUpsertRequest,
  SymbolCleanupRunReviewResponse,
  SymbolCleanupRunSummary,
  SymbolCleanupWorkReviewItem,
  SymbolEnrichmentResolveRequest,
  SymbolEnrichmentSymbolDetailResponse,
  SymbolResolutionResult,
  StockScreenerRequest,
  StockAggregateBar,
  StockAggregateBarsResponse,
  StockAggregateInterval,
  StockAggregateStreamEventType,
  StockTradeStreamEventType,
  StockScreenerPresetListResponse,
  StockScreenerPresetSummary,
  StockScreenerPresetUpsertRequest,
  StockScreenerPresetWorkspace,
  StockScreenerResponse,
  StockScreenerSourceCatalogResponse,
  StockScreenerSourceDescriptor,
  StockScreenerSortClause,
  ReconnectBrokerAccountRequest,
  RefreshBrokerAccountRequest,
  ConfigIdentity,
  ConfigReference,
  ExitPolicyPinImpactRequest,
  ExitPolicyPinImpactResponse,
  ExitPolicyPreset,
  ExitRuleAttributionResponse,
  ExitRuleDiagnostic,
  ExitRulePinImpact,
  ExitRulePreviewRequest,
  ExitRulePreviewResponse,
  ExitRule,
  ExitRuleSetConfig,
  ExitRuleVisualKey,
  GeneratedStrategyBacktestHandoff,
  GeneratedStrategyProvenance,
  GeneratedStrategySaveRequest,
  GeneratedStrategySaveResponse,
  RankingFieldReference,
  RankingPreviewResponse,
  RankingSchemaDraftGenerationRequest,
  RankingSchemaDraftGenerationResponse,
  RankingSchemaPreset,
  RankingSchemaSummary,
  RateLimitPolicyConfig,
  RateLimitPolicySummary,
  RateLimitThrottleSample,
  RateLimitUsageBucket,
  RateLimitUsageView,
  RebalancePolicyPreset,
  RegimeActivationDecision,
  RegimeGate,
  RegimeSourceRef,
  RiskPolicyConfig,
  StrategyConfig,
  StrategyComponentRefs,
  StrategyRiskPolicyPreset,
  StrategyVolatilityMetric,
  UniverseConfigPreset,
  UniverseConfigDraftGenerationRequest,
  UniverseConfigDraftGenerationResponse,
  UniverseCatalogResponse,
  TimeseriesPointResponse,
  TradeAccountBalanceHistoryResponse,
  TradeAccountSummary,
  TradeBlotterResponse,
  TradeMetricFeedResponse,
  TradeApprovalCreateRequest,
  TradeApprovalCreateResponse,
  TradeApprovalPayload,
  TradeApprovalReviewContext,
  TradeOrderPreviewRequest,
  TradePosition,
  UiRuntimeConfig,
  UniverseCondition,
  UniversePreviewRequest,
  UniversePreviewResponse,
  VolatilityTolerance,
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

const agentProfileConfig: AgentProfileConfig = {
  role: "alpha_research",
  maxWorkflowScope: "paper_preview",
  traits: {
    riskAppetite: 0.55,
    lossAversion: 0.45,
    patience: 0.6,
    conviction: 0.7,
    concentrationTolerance: 0.35,
    turnoverTolerance: 0.4,
    recencyBias: 0.5,
    contrarianBias: -0.1,
  },
  worldviewWeights: [
    { worldview: "quality", weight: 3 },
    { worldview: "momentum", weight: 2 },
  ],
  regimePreference: {
    preferredRegimes: ["trending_up", "low_volatility"],
    blockedRegimes: ["liquidity_stress"],
    honorModelHalt: true,
    blockWhenUnclassified: true,
  },
  evidencePolicy: {
    minimumConfidence: 0.7,
    minimumIndependentSignals: 2,
    requireRankingSupport: true,
    requireRegimeSupport: true,
    requireLiquiditySupport: true,
    maxContradictorySignals: null,
  },
  notes: [],
};

const agentProfilePreset: AgentProfilePreset = {
  identity: {
    name: "balanced-alpha-researcher",
    version: 1,
    status: "active",
    description: "",
    intendedUse: "research",
    thesis: "",
    whatToMonitor: [],
  },
  config: agentProfileConfig,
};

const agentStrategyBinding: AgentStrategyBinding = {
  agentProfileRef: { name: agentProfilePreset.identity.name, version: 1 },
  baseStrategyRef: { name: "core-quality-momentum", version: 4 },
  compilerVersion: 1,
  rankingRefsByWorldview: {
    quality: { name: "quality_momentum", version: 2 },
    momentum: { name: "price_momentum", version: 3 },
  },
  riskPolicyRefsByBand: {
    balanced: { name: "balanced_long_only", version: 1 },
  },
  rebalancePolicyRefsByBand: {
    medium: { name: "monthly_last_trading_day", version: 1 },
  },
  exitPolicyRefsByBand: {
    balanced: { name: "rank_decay_exit", version: 1 },
  },
  allowRankingOverride: true,
  allowRiskPolicyOverride: true,
  allowRebalanceOverride: true,
  allowExitPolicyOverride: true,
  minTopN: 10,
  maxTopN: 40,
  minHoldingPeriod: 5,
  maxHoldingPeriod: 63,
  minLookbackWindow: 21,
  maxLookbackWindow: 252,
  maxPositionSizePct: 8,
  allowedRegimes: [],
  blockedRegimes: ["liquidity_stress"],
};

const symbolResolution: SymbolResolutionResult = {
  status: "resolved",
  provider: "massive",
  domain: "market",
  inputSymbol: "I:VIX",
  canonicalSymbol: "^VIX",
  providerSymbol: "I:VIX",
  mappingVersion: "symbol-alias-v1",
};

const agentResolutionPreview: AgentStrategyResolutionPreview = {
  agentProfileRef: agentStrategyBinding.agentProfileRef,
  baseStrategyRef: agentStrategyBinding.baseStrategyRef,
  resolvedStrategy: {
    universeConfigName: "us-large-liquid",
    universeConfigVersion: null,
    universe: null,
    componentRefs: {
      universe: { name: "us-large-liquid", version: 1 },
      ranking: { name: "quality_momentum", version: 2 },
      rebalance: null,
      regimePolicy: null,
      riskPolicy: null,
      exitPolicy: null,
    },
    regimeSource: null,
    regimeGates: {},
    rebalance: "monthly",
    longOnly: true,
    topN: 20,
    lookbackWindow: 63,
    holdingPeriod: 21,
    costModel: "default",
    rankingSchemaName: "quality_momentum",
    rankingSchemaVersion: 2,
    regimePolicyConfigName: null,
    regimePolicyConfigVersion: null,
    regimePolicy: null,
    riskProfileName: null,
    riskPolicyName: null,
    riskPolicyVersion: null,
    positionPolicy: null,
    rebalancePolicy: null,
    strategyRiskPolicy: null,
    exitRuleSetName: null,
    exitRuleSetVersion: null,
    exitRegimeGate: null,
    intrabarConflictPolicy: "stop_first",
    exits: [],
  },
  appliedChanges: [
    {
      path: "rankingSchemaName",
      previousValue: "base-ranking",
      newValue: "quality_momentum",
      reasonCode: "dominant_worldview",
      reason: "quality carried the largest normalized worldview weight",
      clampStatus: "not_clamped",
    },
  ],
  warnings: [],
  agentProfileSnapshotHash: "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  baseStrategySnapshotHash: "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  bindingHash: "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  resolvedStrategyHash: "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
  compilerVersion: 1,
  validationStatus: "valid",
};
const agentResolutionStrategyTopN: number = agentResolutionPreview.resolvedStrategy.topN;

const currencyInterval: CurrencyIntradayBarInterval = "1m";
const currencyBar: CurrencyIntradayBar = {
  timestamp: "2026-05-20T00:00:00Z",
  open: 101000,
  high: 101250,
  low: 100900,
  close: 101200,
  volume: 12.5,
  vwap: 101125.25,
  transactions: 42,
  providerTimestampMs: 1779235200000,
};

const currencyBars: CurrencyIntradayBarsResponse = {
  symbol: "BTCUSD",
  baseCurrency: "BTC",
  providerSymbol: "X:BTCUSD",
  quoteCurrency: "USD",
  interval: currencyInterval,
  from: "2026-05-20T00:00:00Z",
  to: "2026-05-20T00:15:00Z",
  rowCount: 1,
  rows: [currencyBar],
};

const liveMarketPriceStatus: LiveMarketPriceStatus = "healthy";
const liveCurrencyTick: LiveCurrencyPriceTick = {
  provider: "massive",
  assetClass: "crypto",
  symbol: "BTCUSD",
  baseCurrency: "BTC",
  quoteCurrency: "USD",
  providerPair: "BTC-USD",
  providerChannel: "XT.BTC-USD",
  price: 101250.25,
  size: 0.025,
  exchangeId: 3,
  conditions: [1, 2],
  tradeId: "trade-123",
  providerTimestampMs: 1779235200123,
  providerReceivedTimestampMs: 1779235200456,
  observedAt: "2026-05-20T00:05:00Z",
  sequence: 7,
};

const liveCurrencySnapshot: LiveCurrencyPriceSnapshot = {
  provider: "massive",
  assetClass: "crypto",
  symbol: "BTCUSD",
  baseCurrency: "BTC",
  quoteCurrency: "USD",
  providerPair: "BTC-USD",
  providerChannel: "XT.BTC-USD",
  topic: "market-prices:massive:crypto:BTCUSD",
  status: liveMarketPriceStatus,
  lastTick: liveCurrencyTick,
  lastTickAgeSeconds: 1.25,
  connectedAt: "2026-05-20T00:00:00Z",
  lastProviderMessageAt: "2026-05-20T00:05:00Z",
  lastStatusAt: "2026-05-20T00:05:01Z",
  lastError: null,
};

const stockAggregateInterval: StockAggregateInterval = "1m";
const stockAggregateEventType: StockAggregateStreamEventType =
  "market_price.stock_aggregate";
const stockAggregateBar: StockAggregateBar = {
  provider: "massive",
  assetClass: "stocks",
  symbol: "AAPL",
  providerSymbol: "AAPL",
  interval: stockAggregateInterval,
  timestamp: "2026-05-20T14:30:00Z",
  open: 191.25,
  high: 191.9,
  low: 191.1,
  close: 191.7,
  volume: 1250,
  vwap: 191.52,
  transactions: 42,
  providerStartTimestampMs: 1779287400000,
  providerEndTimestampMs: 1779287459999,
  providerDelaySeconds: 1.25,
  observedAt: "2026-05-20T14:30:02Z",
  sequence: 7,
};

const stockAggregateBars: StockAggregateBarsResponse = {
  provider: "massive",
  assetClass: "stocks",
  symbol: "AAPL",
  providerSymbol: "AAPL",
  interval: stockAggregateInterval,
  from: "2026-05-20T14:30:00Z",
  to: "2026-05-20T14:31:00Z",
  rowCount: 1,
  rows: [stockAggregateBar],
};

const liveStockAggregateSnapshot: LiveStockAggregateSnapshot = {
  provider: "massive",
  assetClass: "stocks",
  symbol: stockAggregateBars.symbol,
  providerSymbol: "AAPL",
  interval: stockAggregateInterval,
  topic: "market-prices:massive:stocks:AAPL:1m",
  status: liveMarketPriceStatus,
  lastBar: stockAggregateBar,
  lastBarAgeSeconds: 1.25,
  providerDelaySeconds: 1.25,
  connectedAt: "2026-05-20T14:00:00Z",
  lastProviderMessageAt: "2026-05-20T14:30:02Z",
  lastStatusAt: "2026-05-20T14:30:03Z",
  lastError: null,
};
const liveStockAggregateEventType: StockAggregateStreamEventType =
  stockAggregateEventType === "market_price.stock_aggregate"
    ? "market_price.stock_status"
    : stockAggregateEventType;
const stockTradeEventType: StockTradeStreamEventType = "market_price.stock_trade";
const liveStockTradeTick: LiveStockTradeTick = {
  provider: "massive",
  assetClass: "stocks",
  symbol: "AAPL",
  providerSymbol: "AAPL",
  providerChannel: "T.AAPL",
  price: 191.72,
  size: 100,
  exchangeId: 12,
  conditions: [1, 37],
  tradeId: "trade-123",
  tape: 3,
  providerSequenceNumber: 875,
  providerTimestampMs: 1779287400123,
  tradeReportingFacilityId: 201,
  tradeReportingFacilityTimestampMs: 1779287400124,
  observedAt: "2026-05-20T14:30:02Z",
  sequence: 7,
};
const liveStockTradeSnapshot: LiveStockTradeSnapshot = {
  provider: "massive",
  assetClass: "stocks",
  symbol: "AAPL",
  providerSymbol: "AAPL",
  providerChannel: "T.AAPL",
  topic: "market-prices:massive:stocks:AAPL:trades",
  status: liveMarketPriceStatus,
  lastTrade: liveStockTradeTick,
  lastTradeAgeSeconds: 1.25,
  connectedAt: "2026-05-20T14:00:00Z",
  lastProviderMessageAt: "2026-05-20T14:30:02Z",
  lastStatusAt: "2026-05-20T14:30:03Z",
  lastError: null,
};
const liveStockTradeStatusEventType: StockTradeStreamEventType =
  stockTradeEventType === "market_price.stock_trade"
    ? "market_price.stock_trade_status"
    : stockTradeEventType;

const intradayRefreshDomain: IntradayRefreshDomain = "currency";
const intradayWatchlist: IntradayWatchlistUpsertRequest = {
  name: "Desk Watchlist",
  enabled: true,
  symbols: ["AAPL", "MSFT"],
  pollIntervalMinutes: 5,
  refreshCooldownMinutes: 15,
  autoRefreshEnabled: true,
  refreshDomains: ["market", intradayRefreshDomain],
  marketSession: "us_equities_regular",
};
const intradayMonitorComplete: IntradayMonitorCompleteRequest = {
  claimToken: "claim-1",
  symbolStatuses: [],
  events: [],
  refreshRequests: [
    { domain: "market", symbols: ["AAPL"] },
    { domain: "currency", symbols: ["EURUSD"] },
  ],
  refreshSymbols: ["AAPL"],
};
const intradayRefreshClaim: IntradayRefreshClaimRequest = {
  executionName: "intraday-currency-refresh-job",
  domain: intradayRefreshDomain,
};

const coveredCallTemplate: OptionStrategyTemplate = {
  strategyId: "covered_call",
  displayName: "Covered Call",
  payoffFamily: "stock_overlay_income",
  stage: "core_research",
  approvalLevel: 1,
  minLegs: 1,
  maxLegs: 1,
  requiredLegRoles: ["short_call", "underlying_stock"],
  usesStockOverlay: true,
  requiresStockPosition: true,
  requiresCashSecuring: false,
  definedRisk: true,
  netPremiumDirection: "credit",
  lifecycleModelRequired: false,
  support: {
    researchBacktestSupported: true,
    brokerPreviewSupported: true,
    liveSubmitSupported: false,
  },
  summary: "Long stock plus a short call.",
  notes: [],
};

const optionPayoff: OptionPayoffProfile = {
  strategyId: "covered_call",
  expirationScope: "final_expiration",
  maxProfitDescription: "Capped at the short call strike less stock basis plus premium.",
  maxLoss: 39500,
  maxLossDescription: "Stock can go to zero less premium received.",
  breakevens: [395],
  profitWindowLower: 395,
  profitWindowDescription: "Profitable above adjusted stock basis.",
  deltaSign: "positive",
  thetaSign: "positive",
  vegaSign: "negative",
  idealIvEnvironment: "rich",
  assumptions: [],
  support: coveredCallTemplate.support,
};

const optionLadder: OptionStrategyLadderResponse = {
  ladderVersion: "options-ladder-v1",
  templates: [coveredCallTemplate],
  exclusions: [
    {
      strategyId: "naked_short_straddle",
      reason: "Explicitly out of v1 options capability scope.",
      stage: "out_of_v1",
    },
  ],
};

const optionBrokerConstraints: OptionBrokerConstraintProfile = {
  provider: "alpaca",
  environment: "paper",
  capability: {
    provider: "alpaca",
    environment: "paper",
    approvalLevel: 3,
    supportsOptionAccounts: true,
    supportsOptionChains: true,
    supportsOptionQuotes: true,
    supportsOptionGreeks: true,
    supportsMultiLegOrders: true,
    supportsExercise: false,
    supportsWholeContractQuantityOnly: true,
    supportsNotionalOptionOrders: false,
    supportsExtendedHoursOptions: false,
    allowedOrderTypes: ["market", "limit"],
    allowedTimeInForce: ["day"],
    maxLegsPerOrder: 4,
    restrictions: [],
  },
  orderQuantityMode: "whole_contracts",
  allowedFamilies: ["covered_call"],
  blockedFamilies: ["calendar_spread"],
  multiLegRestrictions: [],
  researchOnly: true,
  brokerPreviewSupported: true,
  liveSubmitSupported: false,
};

const optionPreview: TradeOrderPreviewRequest = {
  accountId: "acct-1",
  environment: "paper",
  clientRequestId: "client-1",
  symbol: "MSFT260619C00450000",
  side: "buy",
  orderType: "limit",
  timeInForce: "day",
  assetClass: "option",
  quantity: 1,
  limitPrice: 5.25,
  allowExtendedHours: false,
  source: "manual",
  optionStrategyId: "long_call",
  optionLegs: [],
};

const tradeApprovalPolicy: BrokerTradeApprovalPolicy = {
  approvalMode: "required",
  releaseMode: "live_bearer",
  enabledEnvironments: ["paper", "live"],
  recipientGroupId: "desk-reviewers",
  recipientEmails: [],
  recipientPhoneNumbers: [],
  maxLiveBearerNotional: 2500,
  tokenTtlSeconds: 300,
  requireDistinctRequester: true,
};

const tradeApprovalReviewContext: TradeApprovalReviewContext = {
  source: "rebalance_proposal",
  accountLabel: "Core Live",
  provider: "alpaca",
  proposalId: "proposal-1",
  proposalTradeIndex: 0,
  sleeveId: "quality-core",
  sleeveName: "Quality Core",
  strategyRef: { strategyName: "quality-trend", strategyVersion: 4 },
  policyVersion: 7,
  estimatedCost: 525,
  estimatedFees: 1.25,
  cashAfter: 9475,
  buyingPowerAfter: 9475,
  riskChecks: [
    {
      checkId: "approval-live-bearer-cap",
      code: "max_live_bearer_notional",
      label: "Live bearer release cap",
      status: "pass",
      severity: "info",
      blocking: false,
      message: "Within live bearer cap.",
      metadata: {},
    },
  ],
  warnings: ["Live release requires one-time approval link."],
  confirmationRequired: true,
  releaseMode: tradeApprovalPolicy.releaseMode,
};

const tradeApprovalPayload: TradeApprovalPayload = {
  accountId: "acct-1",
  previewId: "preview-1",
  orderHash: "hash-1",
  placeIdempotencyKey: "place-idempotency-1",
  order: optionPreview,
  reviewContext: tradeApprovalReviewContext,
};

const tradeApprovalStatus: NotificationStatusResponse = {
  requestId: "notification-1",
  kind: "trade_approval",
  status: "delivered",
  sourceRepo: "asset-allocation-control-plane",
  clientRequestId: "client-1",
  title: "Approve option order",
  description: "Approve the reviewed trade.",
  createdAt: "2026-05-28T15:00:00Z",
  updatedAt: "2026-05-28T15:00:00Z",
  decisionStatus: "pending",
  executionStatus: "pending_approval",
  deliveries: [],
  tradeApproval: {
    accountId: tradeApprovalPayload.accountId,
    previewId: tradeApprovalPayload.previewId,
    orderHash: tradeApprovalPayload.orderHash,
    environment: optionPreview.environment,
    symbol: optionPreview.symbol,
    side: optionPreview.side,
    orderType: optionPreview.orderType,
    timeInForce: optionPreview.timeInForce,
    quantity: optionPreview.quantity,
    limitPrice: optionPreview.limitPrice,
    reviewContext: tradeApprovalReviewContext,
  },
};

const tradeApprovalAction: NotificationActionDetailResponse = {
  requestId: tradeApprovalStatus.requestId,
  tokenId: "token-1",
  kind: tradeApprovalStatus.kind,
  title: tradeApprovalStatus.title,
  description: tradeApprovalStatus.description,
  createdAt: tradeApprovalStatus.createdAt,
  decisionStatus: tradeApprovalStatus.decisionStatus,
  executionStatus: tradeApprovalStatus.executionStatus,
  tradeApproval: tradeApprovalStatus.tradeApproval,
};

const tradeApprovalCreateRequest: TradeApprovalCreateRequest = {
  source: "rebalance_proposal",
  clientRequestId: "approval-client-1",
  idempotencyKey: "approval-idempotency-1",
  proposalId: "proposal-1",
  proposalTradeIndexes: [0],
  reason: "Desk approval requested.",
  releaseMode: "paper_sandbox_bearer",
};

const tradeApprovalCreateResponse: TradeApprovalCreateResponse = {
  accountId: "acct-1",
  approvals: [tradeApprovalStatus],
};

const rateLimitPolicyConfig: RateLimitPolicyConfig = {
  rules: [
    {
      provider: "alpha_vantage",
      operation: "time_series_daily",
      windowSeconds: 60,
      maxRequests: 5,
      burstRequests: 5,
      maxConcurrency: 1,
      cooldownSeconds: 30,
      backgroundMaxWaitMs: 1000,
    },
  ],
};

const rateLimitPolicySummary: RateLimitPolicySummary = {
  name: "system_default",
  version: 1,
  description: "Default upstream limits",
  archived: false,
  usageCount: 0,
  status: "active",
  intendedUse: "production_candidate",
  thesis: "Protect provider quotas",
  whatToMonitor: ["429 spikes"],
  updatedAt: "2026-05-30T12:00:00Z",
  ruleCount: 1,
  providers: ["alpha_vantage"],
};

const rateLimitUsageBucket: RateLimitUsageBucket = {
  provider: "alpha_vantage",
  operation: "time_series_daily",
  windowSeconds: 60,
  maxRequests: 5,
  burstRequests: 5,
  maxConcurrency: 1,
  cooldownSeconds: 30,
  availableTokens: 2.5,
  tokenFillPct: 50,
  activeConcurrency: 0,
  allowCount: 11,
  denyCount: 2,
  cooldownCount: 1,
  upstreamThrottleCount: 0,
  lastDecisionAt: "2026-05-30T12:00:00Z",
  lastDeniedAt: "2026-05-30T12:00:00Z",
  lastCooldownAt: "2026-05-30T12:00:00Z",
  nearLimit: true,
};

const rateLimitThrottleSample: RateLimitThrottleSample = {
  observedAt: "2026-05-30T12:00:00Z",
  provider: "alpha_vantage",
  operation: "time_series_daily",
  workload: "interactive",
  reason: "local_rate_limit",
  retryAfterMs: 30000,
  policyName: "system_default",
  policyVersion: 1,
  message: "Burst exhausted",
};

const rateLimitUsageView: RateLimitUsageView = {
  policyName: "system_default",
  policyVersion: 1,
  generatedAt: "2026-05-30T12:00:01Z",
  buckets: [rateLimitUsageBucket],
  throttleSamples: [rateLimitThrottleSample],
  warnings: ["snapshot is process-local"],
};

const tradeMetricFeed: TradeMetricFeedResponse = {
  scope: "global",
  generatedAt: "2026-05-15T15:00:00Z",
  coverage: {
    accountCount: 2,
    includedAccountCount: 2,
    environments: ["paper", "live"],
    currencies: ["USD"],
    mixedEnvironment: true,
    mixedCurrency: false,
  },
  metrics: [
    {
      metricId: "open_positions",
      label: "Open Positions",
      value: 2,
      valueType: "count",
      status: "available",
      asOf: "2026-05-15T15:00:00Z",
      segments: [
        {
          segmentId: "paper",
          environment: "paper",
          accountCount: 1,
          value: 1,
          status: "available",
          asOf: "2026-05-15T15:00:00Z",
        },
      ],
      warnings: [],
    },
    {
      metricId: "desk.custom.future_metric",
      label: "Future Metric",
      value: null,
      valueType: "currency",
      currency: null,
      status: "unavailable",
      asOf: null,
      segments: [],
      warnings: ["Builder unavailable."],
    },
  ],
  warnings: ["Mixed execution environments are segmented."],
};

const tradeAccountBalanceHistory: TradeAccountBalanceHistoryResponse = {
  accountId: "acct-paper",
  points: [
    {
      accountId: "acct-paper",
      provider: "alpaca",
      environment: "paper",
      asOf: "2026-05-27T14:30:00Z",
      balance: 201125.25,
      equity: 201125.25,
      cash: -250.75,
      buyingPower: 402250.5,
      currency: "USD",
      sourceObservedAt: "2026-05-27T14:30:01Z",
      syncRunId: "sync-001",
    },
  ],
  totalPoints: 1,
  truncated: false,
  generatedAt: "2026-05-27T14:31:00Z",
};

const optionBacktestResult: OptionBacktestResult = {
  resultId: "option-result-1",
  runId: "run-1",
  strategyTemplate: coveredCallTemplate,
  payoff: optionPayoff,
  modelQuality: "fixture_backed",
  quoteSnapshots: [],
  chainSnapshots: [],
  lifecycleEvents: [],
  events: [],
};

const stockScreenerRequest: StockScreenerRequest = {
  q: "MS",
  as_of: "2026-05-04",
  limit: 250,
  offset: 0,
  sort: "ranking_score",
  direction: "desc",
  sorts: [
    { key: "ranking_score", direction: "desc" },
    { key: "return_5d", direction: "desc" },
    { key: "volume_pct_rank_252d", direction: "desc" },
  ],
  strategy_name: "quality-trend",
  ranking_schema_name: "quality_momentum",
  ranking_schema_version: 2,
  sectors: ["Technology"],
  has_silver: true,
  min_volume_pct_rank_252d: 0.6,
};

const stockScreenerSortClause: StockScreenerSortClause = {
  key: "return_5d",
  direction: "desc",
};

const stockScreenerTableSource: StockScreenerSourceDescriptor = {
  kind: "table",
  schema_name: "gold",
  table_name: "finance_data",
  symbol_column: "symbol",
  as_of_column: "date",
  selected_columns: ["market_cap", "pe_ratio"],
};

const stockScreenerSourceCatalog: StockScreenerSourceCatalogResponse = {
  warnings: [],
  sources: [
    {
      source: {
        kind: "layer",
        source_layer: "gold",
        selected_columns: [],
      },
      label: "Gold factors",
      capabilities: ["stock_identity", "as_of_date", "screening"],
      columns: [],
      default_column_names: ["symbol", "return_5d"],
    },
    {
      source: stockScreenerTableSource,
      label: "Finance Data",
      description: "Gold finance factors.",
      capabilities: ["stock_identity", "as_of_date", "screening"],
      columns: [
        {
          name: "market_cap",
          label: "Market Cap",
          data_type: "numeric",
          value_kind: "number",
          operators: ["eq", "gte", "lte"],
          sortable: true,
          filterable: true,
          default_visible: true,
        },
      ],
      default_column_names: ["market_cap"],
    },
  ],
};

const stockScreenerPresetWorkspace: StockScreenerPresetWorkspace = {
  q: "MS",
  as_of: "2026-05-04",
  source_layer: "platinum",
  source: {
    kind: "layer",
    source_layer: "platinum",
    selected_columns: [],
  },
  selected_columns: ["ranking_score", "return_5d"],
  dynamic_filters: [
    { column_name: "volume_pct_rank_252d", operator: "gte", value: 0.6 },
  ],
  dynamic_sorts: [{ column_name: "volume_pct_rank_252d", direction: "desc" }],
  sort: "ranking_score",
  direction: "desc",
  sorts: [
    { key: "ranking_score", direction: "desc" },
    stockScreenerSortClause,
  ],
  strategy_name: "quality-trend",
  ranking_schema_name: "quality_momentum",
  ranking_schema_version: 2,
  sectors: ["Technology"],
  min_volume_pct_rank_252d: 0.6,
  visible_column_ids: ["symbol", "return_5d", "ranking_score"],
};

const stockScreenerPresetUpsert: StockScreenerPresetUpsertRequest = {
  name: "Momentum desk",
  description: "Quality momentum workstation view",
  workspace: stockScreenerPresetWorkspace,
};

const stockScreenerPresetSummary: StockScreenerPresetSummary = {
  preset_id: "preset-1",
  name: stockScreenerPresetUpsert.name,
  description: stockScreenerPresetUpsert.description,
  workspace: stockScreenerPresetUpsert.workspace,
  created_at: "2026-05-31T15:00:00Z",
  updated_at: "2026-05-31T15:00:00Z",
};

const stockScreenerPresetList: StockScreenerPresetListResponse = {
  presets: [stockScreenerPresetSummary],
};

const stockScreenerResponse: StockScreenerResponse = {
  asOf: "2026-05-04",
  total: 1,
  limit: 250,
  offset: 0,
  source: stockScreenerTableSource,
  sourceColumns: stockScreenerSourceCatalog.sources[1].columns,
  filters: stockScreenerRequest,
  summary: {
    universeCount: 2,
    totalResultCount: 1,
    returnedCount: 1,
    coverage: {
      total: 2,
      withSilver: 2,
      withGold: 1,
      missingSilver: 0,
      missingGold: 1,
    },
  },
  facets: {
    sectors: [{ value: "Technology", count: 1 }],
    industries: [],
    countries: [{ value: "US", count: 1 }],
  },
  ranking: {
    schemaName: "quality_momentum",
    schemaVersion: 2,
    componentNames: ["Momentum", "Quality"],
  },
  rows: [
    {
      symbol: "MSFT",
      sector: "Technology",
      close: 421.03,
      return5d: 0.012,
      volumePctRank252d: 0.8,
      hasSilver: true,
      hasGold: 1,
      rankingRank: 3,
      rankingOverallScore: 0.91,
      rankingComponents: [
        { name: "Momentum", score: 0.87 },
        { name: "Quality", score: null },
      ],
      values: {
        market_cap: 3100000000000,
        pe_ratio: 34.2,
        date: "2026-05-04",
      },
    },
  ],
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
  rows: [
    {
      symbol: "AAPL",
      name: "Apple Inc.",
      sector: "Technology",
      industry: "Consumer Electronics",
      country: "US",
      close: 182.31,
      volume: 1300000,
    },
  ],
  rowCount: 2,
  previewLimit: 25,
  truncated: false,
  asOf: "2026-05-16",
};

const previewRequest: UniversePreviewRequest = {
  universeName: "u26_us_liquid_oversold_dislocation",
  asOfDate: "2020-03-20",
  sampleLimit: 50,
};
void previewRequest;

const regimeSource: RegimeSourceRef = {
  modelName: "default-regime",
  modelVersion: 3,
};

const trendingGate: RegimeGate = {
  blockedRegimes: ["liquidity_stress"],
};

const strategy: StrategyConfig = {
  regimeSource,
  regimeGates: {
    "risk-on": {
      when: {
        requiredRegimes: ["trending_up"],
        blockedRegimes: ["liquidity_stress"],
        honorModelHalt: true,
        blockWhenUnclassified: true,
        requireAllRequired: false,
      },
      allocations: [
        {
          strategyRef: {
            name: "quality_momentum",
            version: 3,
          },
          weight: 2,
        },
      ],
    },
  },
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
  positionPolicy: {
    regimeGate: { blockedRegimes: ["trending_down"] },
    targetPositionSize: { mode: "pct_of_allocatable_capital", value: 5 },
    maxPositionSize: { mode: "pct_of_allocatable_capital", value: 8 },
    maxOpenPositions: 10,
    allowedAssetClasses: ["equity"],
    requireOrderConfirmation: true,
  },
  strategyRiskPolicy: {
    enabled: true,
    scope: "strategy",
    marketStress: {
      regimeGate: trendingGate,
    },
  },
  exitRegimeGate: { blockedRegimes: ["high_volatility"] },
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

const universeDraftGenerationRequest: UniverseConfigDraftGenerationRequest = {
  plaintext: "US primary listings with market cap above 10 billion and strong dollar volume.",
  nameHint: "us-large-liquid",
  descriptionHint: "Generated US liquid equity draft.",
  intendedUse: "research",
};

const universeDraftGenerationResponse: UniverseConfigDraftGenerationResponse = {
  draft: {
    identity: {
      ...configIdentity,
      name: "generated-us-large-liquid",
      version: 1,
      status: "draft",
    },
    config: universePreset.config,
  },
  explanation: "Mapped the request to governed country, listing, market-cap, and liquidity filters.",
  assumptions: ["Dollar volume is represented by market.dollar_volume_20d."],
  warnings: ["Review thresholds before saving."],
  fieldsUsed: ["security.country", "security.market_cap", "market.dollar_volume_20d"],
  preview,
};

const rankingFieldReference: RankingFieldReference = {
  table: "market_data",
  column: "return_126d",
  label: "126 Day Return",
  valueKind: "number",
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

const rankingSchemaSummary: RankingSchemaSummary = {
  name: "quality_momentum",
  version: 3,
  status: "active",
  description: "Quality plus medium-term momentum.",
  intendedUse: "validation",
  thesis: "Favor durable compounders with price confirmation.",
  whatToMonitor: ["Factor drift"],
  archived: false,
  usageCount: 2,
  updatedAt: "2026-05-24T12:00:00Z",
  schemaProfile: {
    groupCount: 2,
    factorCount: 4,
    groupNames: ["quality", "momentum"],
    sourceTables: ["market_data", "fundamentals"],
    factorColumns: ["market_data.return_126d", "fundamentals.pe_ratio"],
    transformTypes: ["percentile_rank", "zscore"],
    directionCounts: { asc: 1, desc: 3 },
    missingPolicyCounts: { exclude: 2, zero: 2 },
  },
};

const rankingDraftGenerationRequest: RankingSchemaDraftGenerationRequest = {
  plaintext: "Rank the liquid universe by 126 day momentum and lower volatility.",
  nameHint: "generated-quality-momentum",
  descriptionHint: "Generated ranking draft.",
  universeConfigNameHint: "us_large_liquid",
  intendedUse: "research",
  previewStrategyName: "long_only_core",
  previewAsOfDate: "2026-05-08",
};

const rankingPreview: RankingPreviewResponse = {
  strategyName: "long_only_core",
  asOfDate: "2026-05-08",
  rowCount: 1,
  rows: [{ symbol: "AAPL", rank: 1, score: 0.98 }],
  warnings: [],
};

const rankingDraftGenerationResponse: RankingSchemaDraftGenerationResponse = {
  draft: {
    identity: {
      ...configIdentity,
      name: "generated-quality-momentum",
      version: 1,
      status: "draft",
    },
    config: rankingPreset.config,
  },
  explanation: "Mapped the request to governed ranking factors.",
  assumptions: ["Quality was not mapped because no governed factor was available."],
  warnings: ["Review factor coverage before saving."],
  fieldsUsed: [rankingFieldReference],
  unmappedSignals: ["quality"],
  preview: rankingPreview,
};

const generatedStrategyProvenance: GeneratedStrategyProvenance = {
  generationRequestId: "genreq-123",
  promptFingerprint: "sha256:prompt-abcdef1234567890",
  promptSummary: "Redacted summary of the requested strategy.",
  sourceContext: ["strategy workspace draft"],
  model: "strategy-draft-v1",
  generatedAt: "2026-05-24T12:00:00Z",
  outputFingerprint: "sha256:output-abcdef1234567890",
  assumptions: ["monthly rebalance"],
  warnings: ["Review liquidity filters before backtest."],
  unresolvedRequirements: ["Confirm benchmark."],
};

const generatedStrategySaveRequest: GeneratedStrategySaveRequest = {
  name: "generated-quality-momentum",
  description: "Human-reviewed generated draft.",
  config: strategy,
  provenance: generatedStrategyProvenance,
};

const generatedStrategyBacktestHandoff: GeneratedStrategyBacktestHandoff = {
  strategyRef: {
    strategyName: "generated-quality-momentum",
    strategyVersion: 7,
  },
  validationPath: "/api/backtests/validation",
  runPath: "/api/backtests/runs",
  method: "POST",
};

const generatedStrategySaveResponse: GeneratedStrategySaveResponse = {
  status: "saved",
  message: "Generated strategy saved for review.",
  strategyName: "generated-quality-momentum",
  strategyVersion: 7,
  strategyRef: generatedStrategyBacktestHandoff.strategyRef,
  provenanceId: "generated-quality-momentum-7",
  provenanceStatus: "recorded",
  reviewStatus: "pending_review",
  provenance: generatedStrategyProvenance,
  backtestHandoff: generatedStrategyBacktestHandoff,
};

const rebalancePreset: RebalancePolicyPreset = {
  identity: {
    ...configIdentity,
    name: "weekly_last_trading_day",
    thesis: "Weekly close signal with next-open execution.",
  },
  config: {
    regimeGate: { blockedRegimes: ["high_volatility"] },
    frequency: "weekly",
    executionTiming: "next_bar_open",
    cadence: "weekly",
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

const inactiveRegimeDecision: RegimeActivationDecision = {
  state: "inactive",
  reasonCode: "blocked_regime",
  inactiveAction: "target_zero",
  targetWeightMultiplier: 0,
  modelName: "default-regime",
  modelVersion: 3,
  asOfDate: "2026-05-15",
  effectiveFromDate: "2026-05-15",
  activeRegimes: ["liquidity_stress"],
  haltFlag: false,
};

const strategyVolatilityMetric: StrategyVolatilityMetric = "realized_vol_20d";
const strategyVolatilityTolerance: VolatilityTolerance = {
  metric: strategyVolatilityMetric,
  maxPct: 16,
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
    drawdown: {
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
    exposure: {
      volatilityTolerance: strategyVolatilityTolerance,
      limits: {
        drawdownReducePct: 8,
        drawdownBlockPct: 12,
      },
    },
    marketStress: {
      regimeGate: trendingGate,
      vixSpikeHalt: {
        threshold: 32,
        streakBars: 2,
        cooldownBars: 2,
      },
    },
  },
};

const riskPolicyConfig: RiskPolicyConfig = {
  policy: riskPreset.config,
};

const gatedExitRuleSetConfig: ExitRuleSetConfig = {
  regimeGate: { blockedRegimes: ["liquidity_stress"] },
  intrabarConflictPolicy: "priority_order",
  exits: [
    {
      id: "rank-decay-2",
      type: "rank_decay",
      description: "Close names that decay below the retained-rank cutoff.",
      visualKey: "rank_decay",
      scope: "position",
      action: "exit_full",
      minHoldBars: 0,
      rankThreshold: 2,
      priority: 1,
    },
  ],
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
        description: "Close names that have decayed below the retained-rank cutoff.",
        visualKey: "rank_decay",
        scope: "position",
        action: "exit_full",
        minHoldBars: 0,
        rankThreshold: 40,
      },
    ],
  },
};

const exitVisualKey: ExitRuleVisualKey = "trailing_stop_pct";
const exitRuleWithMetadata: ExitRule = {
  id: "trail-10pct",
  type: "trailing_stop_pct",
  description:
    "Trail the stop below the highest achieved price to reduce giveback after favorable movement.",
  visualKey: exitVisualKey,
  scope: "position",
  priceField: "low",
  value: 0.1,
  priority: 1,
  action: "exit_full",
  minHoldBars: 0,
  reference: "highest_since_entry",
};

const exitRuleSetConfig: ExitRuleSetConfig = {
  intrabarConflictPolicy: "priority_order",
  exits: [exitRuleWithMetadata],
};

const exitRulePreviewRequest: ExitRulePreviewRequest = {
  config: {
    intrabarConflictPolicy: exitRuleSetConfig.intrabarConflictPolicy,
    exits: exitRuleSetConfig.exits,
  },
  sampleBar: {
    low: 93.5,
    close: 101,
  },
  samplePosition: {
    entry_price: 100,
    highest_since_entry: 112,
  },
};

const exitRuleDiagnostic: ExitRuleDiagnostic = {
  code: "unsupported_evaluator",
  severity: "warning",
  message: "rank_decay is contract-valid but not supported by the evaluator.",
  ruleId: "rank-decay-40",
  field: "type",
  details: {
    ruleType: "rank_decay",
  },
};

const exitRulePreviewResponse: ExitRulePreviewResponse = {
  verdict: "warning",
  normalizedConfig: exitRuleSetConfig,
  diagnostics: [exitRuleDiagnostic],
  candidates: [
    {
      ruleId: "trail-10pct",
      ruleType: "trailing_stop_pct",
      priority: 1,
      triggered: false,
      action: "exit_full",
      priceField: "low",
      observedValue: 93.5,
      thresholdValue: 100.8,
    },
  ],
};

const exitRulePinImpact: ExitRulePinImpact = {
  ruleId: "trail-10pct",
  changeType: "modified",
  ruleType: "trailing_stop_pct",
  visualKey: "trailing_stop_pct",
  previousPriority: 1,
  proposedPriority: 0,
};

const exitPolicyPinImpactRequest: ExitPolicyPinImpactRequest = {
  strategyName: "quality-trend",
  strategyVersion: 4,
  currentExitPolicyName: "lifecycle-exits",
  currentExitPolicyVersion: 2,
  proposedExitPolicyName: "lifecycle-exits",
  proposedExitPolicyVersion: 3,
  proposedConfig: exitRuleSetConfig,
};

const exitPolicyPinImpactResponse: ExitPolicyPinImpactResponse = {
  strategyName: exitPolicyPinImpactRequest.strategyName,
  strategyVersion: exitPolicyPinImpactRequest.strategyVersion,
  currentExitPolicyName: "lifecycle-exits",
  currentExitPolicyVersion: 2,
  proposedExitPolicyName: "lifecycle-exits",
  proposedExitPolicyVersion: 3,
  diagnostics: [exitRuleDiagnostic],
  ruleImpacts: [exitRulePinImpact],
  changedRuleCount: 1,
};

const runtimeConfig: UiRuntimeConfig = {
  apiBaseUrl: "/api",
  authSessionMode: "cookie",
  authProvider: "oidc",
  oidcAuthority: "https://login.example.com/tenant/v2.0",
  oidcClientId: "11111111-2222-3333-4444-555555555555",
  oidcScopes: ["openid", "profile"],
  oidcAudience: ["asset-allocation-api"],
};

const authProvider: AuthProvider = "oidc";

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
    optionApprovalLevel: null,
    supportsOptionChains: false,
    supportsOptionGreeks: false,
    supportsOptionMultiLegOrders: false,
    supportsOptionExercise: false,
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
  normalizationWarnings: [],
  quarantinedRowCount: 0,
};

const kalshiPredictionMarketPosition: TradePosition = {
  accountId: "kalshi-live-subaccount-0",
  symbol: "KXNYC-26MAY10-T75",
  assetClass: "prediction_market",
  providerPositionId: "pos-123",
  providerInstrumentId: "KXNYC-26MAY10-T75",
  instrumentName: "NYC high temperature above 75F on May 10",
  outcomeSide: "yes",
  rawProviderStatus: "active",
  quantity: 12,
  marketValue: 720,
  sourceObservedAt: "2026-05-10T13:45:00Z",
  ingestedAt: "2026-05-10T13:45:03Z",
  syncRunId: "sync-001",
  sourcePayloadHash: "sha256:abc",
  normalizationWarnings: [
    {
      code: "unknown_kalshi_order_status",
      message: "Raw provider status was preserved.",
      severity: "warning",
      providerField: "status",
      rawValue: "resting",
    },
  ],
  quarantined: false,
};

const kalshiActivity: TradeBlotterResponse = {
  accountId: "kalshi-live-subaccount-0",
  rows: [
    {
      rowId: "kalshi-event-001",
      accountId: "kalshi-live-subaccount-0",
      provider: "kalshi",
      environment: "live",
      eventType: "settlement",
      occurredAt: "2026-05-10T13:45:00Z",
      providerEventId: "event-001",
      providerInstrumentId: "KXNYC-26MAY10-T75",
      instrumentName: "NYC high temperature above 75F on May 10",
      symbol: "KXNYC-26MAY10-T75",
      assetClass: "prediction_market",
      side: "buy",
      outcomeSide: "yes",
      status: "filled",
      rawProviderStatus: "settled",
      quantity: 10,
      price: 100,
      cashImpact: 420,
      sourceObservedAt: "2026-05-10T13:45:00Z",
      ingestedAt: "2026-05-10T13:45:03Z",
      syncRunId: "sync-001",
      normalizationWarnings: [],
      reconciliationRequired: false,
      quarantined: false,
    },
  ],
  sourceObservedAt: "2026-05-10T13:45:00Z",
  syncRunId: "sync-001",
  normalizationWarnings: [],
  unmappedRowCount: 0,
  quarantinedRowCount: 0,
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

const benchmarkAttribution: BacktestBenchmarkAttribution = {
  benchmarkSymbol: "SPY",
  attributionMethod: "simple_total_return",
  dataQualityStatus: "complete",
  strategyTotalReturn: 0.12,
  benchmarkTotalReturn: 0.08,
  excessTotalReturn: 0.04,
  strategyAnnualizedReturn: 0.11,
  benchmarkAnnualizedReturn: 0.07,
  excessAnnualizedReturn: 0.04,
  startTs: "2026-03-08T00:00:00Z",
  endTs: "2026-03-09T00:00:00Z",
  observationCount: 2,
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
  regimePolicyName: "default-regime-policy",
  regimePolicyVersion: 1,
  riskPolicyName: "balanced-risk",
  riskPolicyVersion: 3,
  exitPolicyName: "lifecycle-exits",
  exitPolicyVersion: 4,
  rebalancePolicyName: "monthly-rebalance",
  rebalancePolicyVersion: 5,
};

const exitRuleAttribution: ExitRuleAttributionResponse = {
  runId: "run-123",
  exitPolicyName: pins.exitPolicyName,
  exitPolicyVersion: pins.exitPolicyVersion,
  exitPolicyConfigHash: "sha256:abc",
  rules: [
    {
      ruleId: "trail-10pct",
      ruleType: "trailing_stop_pct",
      description: "Trailing stop exit.",
      visualKey: "trailing_stop_pct",
      priority: 1,
      closedPositionCount: 2,
      realizedPnl: 125.5,
      averageRealizedReturn: 0.045,
      winRate: 1,
      averageHoldingPeriodBars: 8.5,
      totalTransactionCost: 3.25,
    },
  ],
  unattributedExitCount: 0,
  missingRuleIds: [],
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
  policyEventsUrl: "/api/backtests/run-123/policy-events",
  dataQualityEventsUrl: "/api/backtests/run-123/data-quality-events",
};

const lookupResponse: BacktestLookupResponse = {
  found: true,
  state: "completed",
  run: runStatus,
  result: {
    run_id: "run-123",
    total_return: 0.12,
    requested_residual_cash_weight: 0,
    executed_residual_cash_weight: 0.15,
    benchmarkAttribution,
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
    requested_residual_cash_weight: 0,
    executed_residual_cash_weight: 0.15,
    benchmarkAttribution,
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

const policyEvents: BacktestPolicyEventListResponse = {
  events: [
    {
      run_id: "run-123",
      event_seq: 1,
      bar_ts: "2026-03-08T14:31:00Z",
      scope: "strategy",
      policy_type: "rebalance",
      decision: "applied",
      reason_code: "residual_cash_reserved",
      action: "reserve_cash",
      requested_target_weight: 0.5,
      executed_target_weight: 0.35,
      requested_residual_cash_weight: 0,
      executed_residual_cash_weight: 0.15,
      details: {},
    },
  ],
  total: 1,
  limit: 50,
  offset: 0,
};

const trade: TradeResponse = {
  execution_date: "2026-03-08T10:00:00Z",
  symbol: "MSFT",
  quantity: 10,
  price: 100,
  notional: 1000,
  commission: 1,
  slippage_cost: 0.5,
  cash_after: 98998.5,
  requested_target_weight: 0.5,
  executed_target_weight: 0.35,
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
void currencyInterval;
void currencyBar;
void currencyBars;
void stockAggregateInterval;
void stockAggregateEventType;
void stockAggregateBar;
void stockAggregateBars;
void liveStockAggregateSnapshot;
void liveStockAggregateEventType;
void stockTradeEventType;
void liveStockTradeTick;
void liveStockTradeSnapshot;
void liveStockTradeStatusEventType;
void authSession;
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
void policyEvents;
void point;
void trade;
void tradeMetricFeed;
void configReference;
void configIdentity;
void reusableComponentRefs;
void universePreset;
void universeDraftGenerationRequest;
void universeDraftGenerationResponse;
void rankingFieldReference;
void rankingPreset;
void rankingDraftGenerationRequest;
void rankingPreview;
void rankingDraftGenerationResponse;
void rebalancePreset;
void riskPreset;
void exitPreset;
void exitRuleWithMetadata;
void rateLimitPolicyConfig;
void rateLimitPolicySummary;
void rateLimitUsageBucket;
void rateLimitUsageView;
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

const workReviewItem: SymbolCleanupWorkReviewItem = {
  workId: "work-1",
  runId: "run-1",
  symbol: "AAPL",
  status: "completed",
  requestedFields: ["sector_norm", "issuer_summary_short"],
  attemptCount: 2,
  executionName: "symbol-cleanup-worker",
  createdAt: "2026-05-14T06:00:00Z",
  claimedAt: "2026-05-14T06:01:00Z",
  completedAt: "2026-05-14T06:01:45Z",
  updatedAt: "2026-05-14T06:01:45Z",
  acceptedUpdateCount: 1,
  rejectedUpdateCount: 1,
  lockedSkipCount: 1,
  overwriteCount: 0,
  result: {
    symbol: "AAPL",
    profile: {
      sector_norm: "Technology",
      issuer_summary_short: "Consumer hardware and services company.",
    },
    model: "gpt-5.4",
    confidence: 0.91,
    warnings: ["locked field skipped"],
  },
};

const runReview: SymbolCleanupRunReviewResponse = {
  run: runSummary,
  totalCount: 1,
  limit: 50,
  offset: 0,
  items: [workReviewItem],
};

const pullRequestSync: PullRequestSyncView = {
  checkedAt: "2026-05-15T15:00:00Z",
  status: "available",
  result: "target-stale",
  summary: {
    totalPullRequests: 1,
    drafts: 0,
    ready: 1,
    synced: 0,
    targetStale: 1,
    sourceStale: 0,
    conflicts: 0,
    unknown: 0,
    unavailable: 0,
    error: 0,
  },
  pullRequests: [
    {
      repo: "asset-allocation-ui",
      repositoryId: "5e10a80a-e19e-487d-bd1c-1a18e3b13e1c",
      pullRequestId: 280,
      title: "AB#178 Add symbol cleanup run review UI",
      status: "active",
      isDraft: false,
      sourceRefName: "refs/heads/feature",
      targetRefName: "refs/heads/main",
      sourceHeadSha: "2a954f01717a13765a28b1050ea96997a6c6fab5",
      targetHeadSha: "df3f6ec626b1e2f4a72f71a2b73dab1da5f022bf",
      lastMergeSourceCommit: "2a954f01717a13765a28b1050ea96997a6c6fab5",
      lastMergeTargetCommit: "1111111111111111111111111111111111111111",
      lastMergeCommit: "7a78f21a7afb10aeb9b3039eb385b18b0c08aef6",
      mergeStatus: "succeeded",
      result: "target-stale",
      workItems: [{ id: 178, title: "Review symbol cleanup results", workItemType: "User Story", state: "Active", links: [] }],
      commits: [
        {
          commitId: "2a954f01717a13765a28b1050ea96997a6c6fab5",
          comment: "Add review UI",
          authorName: "rudy",
          authoredAt: "2026-05-15T14:34:47Z",
          links: [],
          warnings: [],
        },
      ],
      links: [],
      warnings: ["Target branch moved after merge evaluation."],
      errors: [],
    },
  ],
  links: [],
  warnings: [],
  errors: [],
};

const pipelineSync: PipelineSyncView = {
  checkedAt: "2026-05-21T12:00:00Z",
  status: "available",
  result: "attention",
  summary: {
    totalPipelines: 1,
    healthy: 0,
    running: 1,
    failed: 1,
    pendingApprovals: 1,
    blocked: 0,
    unknown: 0,
    unavailable: 0,
    error: 0,
  },
  pipelines: [
    {
      repo: "asset-allocation-ui",
      pipelineId: 18,
      pipelineName: "asset-allocation-ui-deploy-prod",
      pipelineType: "deploy",
      definitionPath: "azure-pipelines/deploy-prod.yml",
      defaultBranch: "refs/heads/main",
      latestRun: {
        pipelineId: 18,
        pipelineName: "asset-allocation-ui-deploy-prod",
        runId: 5132,
        runNumber: "ui-deploy-20260521.1",
        status: "completed",
        result: "failed",
        sourceBranch: "refs/heads/main",
        sourceSha: "abcdef1234567890abcdef1234567890abcdef12",
        links: [],
        warnings: [],
      },
      activeRuns: [
        {
          pipelineId: 18,
          pipelineName: "asset-allocation-ui-deploy-prod",
          runId: 5133,
          runNumber: "ui-deploy-20260521.2",
          status: "inProgress",
          result: "unknown",
          links: [],
          warnings: [],
        },
      ],
      failedStages: [
        {
          name: "Deploy / Verify",
          status: "failed",
          result: "failed",
          runId: 5132,
          action: {
            kind: "retry-stage",
            label: "Retry Deploy / Verify",
            pipelineId: 18,
            runId: 5132,
            stageName: "Deploy / Verify",
            links: [],
          },
          links: [],
          warnings: ["Smoke verification failed."],
        },
      ],
      pendingApprovals: [
        {
          approvalId: "approval-1",
          status: "pending",
          approverDisplayName: "Rudy Prokes",
          action: {
            kind: "approve-check",
            label: "Approve deploy gate",
            pipelineId: 18,
            runId: 5133,
            approvalId: "approval-1",
            links: [],
          },
          links: [],
        },
      ],
      actions: [
        { kind: "queue", label: "Queue pipeline", pipelineId: 18, links: [] },
        { kind: "cancel", label: "Cancel active run", pipelineId: 18, runId: 5133, links: [] },
      ],
      links: [],
      warnings: [],
      errors: [],
    },
  ],
  links: [],
  warnings: [],
  errors: [],
};

const pipelineQueue: PipelineQueueActionRequest = {
  pipelineId: 18,
  sourceBranch: "refs/heads/main",
};

const pipelineAction: PipelineActionResponse = {
  pipelineId: 18,
  pipelineName: "asset-allocation-ui-deploy-prod",
  action: "approve-check",
  status: "completed",
  message: "Approved pipeline gate.",
  runId: 5133,
  approvalId: "approval-1",
  approvalStatus: "approved",
  details: {},
  links: [],
  warnings: [],
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
void workReviewItem;
void runReview;
void stockScreenerSortClause;
void pullRequestSync;
void pipelineSync;
void pipelineQueue;
void pipelineAction;
void aiEvent;
