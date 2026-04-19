export type ExitRuleType =
  | 'stop_loss_fixed'
  | 'take_profit_fixed'
  | 'trailing_stop_pct'
  | 'trailing_stop_atr'
  | 'time_stop';

export type ExitRuleScope = 'position';
export type ExitRuleAction = 'exit_full';
export type ExitRulePriceField = 'open' | 'high' | 'low' | 'close';
export type ExitRuleReference = 'entry_price' | 'highest_since_entry';
export type IntrabarConflictPolicy = 'stop_first' | 'take_profit_first' | 'priority_order';
export type RegimeCode =
  | 'trending_bull'
  | 'trending_bear'
  | 'choppy_mean_reversion'
  | 'high_vol'
  | 'unclassified';
export type RegimeBlockedAction = 'skip_entries' | 'skip_rebalance';
export type UniverseSource = 'postgres_gold';
export type UniverseGroupOperator = 'and' | 'or';
export type UniverseConditionOperator =
  | 'eq'
  | 'ne'
  | 'gt'
  | 'gte'
  | 'lt'
  | 'lte'
  | 'in'
  | 'not_in'
  | 'is_null'
  | 'is_not_null';
export type UniverseFieldId =
  | 'market.close'
  | 'security.is_active'
  | 'security.sector'
  | 'security.delisted_at'
  | 'market.trade_date'
  | 'market.timestamp'
  | 'returns.return_20d'
  | 'returns.return_126d'
  | 'quality.piotroski_f_score'
  | 'earnings.surprise_pct';
export type UniverseValue = string | number | boolean;
export type UniverseValueKind = 'string' | 'number' | 'boolean' | 'date' | 'datetime';
export type RankingTransformType =
  | 'percentile_rank'
  | 'zscore'
  | 'minmax'
  | 'clip'
  | 'winsorize'
  | 'coalesce'
  | 'log1p'
  | 'negate'
  | 'abs';
export type RankingDirection = 'asc' | 'desc';
export type RankingMissingValuePolicy = 'exclude' | 'zero';
export type RegimeStatus = 'confirmed' | 'transition' | 'unclassified';
export type TrendState = 'positive' | 'negative' | 'near_zero';
export type CurveState = 'contango' | 'flat' | 'inverted';
export type RunStatus = 'queued' | 'running' | 'completed' | 'failed';
export type TradeRole = 'entry' | 'rebalance_increase' | 'rebalance_decrease' | 'exit';
export type SymbolCleanupStatus = 'queued' | 'running' | 'completed' | 'failed';
export type SymbolWorkStatus = 'queued' | 'claimed' | 'completed' | 'failed';
export type SymbolSourceKind = 'provider' | 'ai' | 'derived' | 'override';
export type SymbolValidationStatus = 'accepted' | 'rejected' | 'pending' | 'locked';
export type SymbolOverwriteMode = 'fill_missing' | 'full_reconcile';
export type SymbolEnrichmentField =
  | 'security_type_norm'
  | 'exchange_mic'
  | 'country_of_risk'
  | 'sector_norm'
  | 'industry_group_norm'
  | 'industry_norm'
  | 'is_adr'
  | 'is_etf'
  | 'is_cef'
  | 'is_preferred'
  | 'share_class'
  | 'listing_status_norm'
  | 'issuer_summary_short';

export interface ExitRule {
  id: string;
  type: ExitRuleType;
  scope: ExitRuleScope;
  priceField?: ExitRulePriceField;
  value?: number;
  atrColumn?: string;
  priority?: number;
  action: ExitRuleAction;
  minHoldBars: number;
  reference?: ExitRuleReference;
}

export interface UniverseCondition {
  kind: 'condition';
  field: UniverseFieldId;
  operator: UniverseConditionOperator;
  value?: UniverseValue;
  values?: UniverseValue[];
}

export interface UniverseFieldDefinition {
  id: UniverseFieldId;
  label: string;
  valueKind: UniverseValueKind;
  operators: UniverseConditionOperator[];
}

export interface UniverseCatalogResponse {
  source: UniverseSource;
  fields: UniverseFieldDefinition[];
}

export interface UniversePreviewResponse {
  source: UniverseSource;
  symbolCount: number;
  sampleSymbols: string[];
  fieldsUsed: UniverseFieldId[];
  warnings: string[];
}

export interface UniverseGroup {
  kind: 'group';
  operator: UniverseGroupOperator;
  clauses: UniverseNode[];
}

export type UniverseNode = UniverseGroup | UniverseCondition;

export interface UniverseDefinition {
  source: UniverseSource;
  root: UniverseGroup;
}

export interface TargetGrossExposureByRegime {
  trending_bull: number;
  trending_bear: number;
  choppy_mean_reversion: number;
  high_vol: number;
  unclassified: number;
}

export interface RegimePolicy {
  modelName: string;
  targetGrossExposureByRegime: TargetGrossExposureByRegime;
  blockOnTransition: boolean;
  blockOnUnclassified: boolean;
  honorHaltFlag: boolean;
  onBlocked: RegimeBlockedAction;
}

export interface StrategyConfig {
  universeConfigName?: string;
  universe?: UniverseDefinition;
  rebalance: string;
  longOnly: boolean;
  topN: number;
  lookbackWindow: number;
  holdingPeriod: number;
  costModel: string;
  rankingSchemaName?: string;
  regimePolicy?: RegimePolicy;
  intrabarConflictPolicy: IntrabarConflictPolicy;
  exits: ExitRule[];
}

export interface RankingTransform {
  type: RankingTransformType;
  params: Record<string, string | number | boolean | null>;
}

export interface RankingFactor {
  name: string;
  table: string;
  column: string;
  weight: number;
  direction: RankingDirection;
  missingValuePolicy: RankingMissingValuePolicy;
  transforms: RankingTransform[];
}

export interface AiChatRequest {
  prompt: string;
  role?: string | null;
  systemInstructions?: string | null;
}

export interface AiChatError {
  code: string;
  message: string;
  retryable: boolean;
}

export interface AiChatStartedData {
  requestId: string;
  model: string;
  providerResponseId?: string | null;
}

export interface AiChatStatusData {
  code: string;
  message: string;
  providerResponseId?: string | null;
}

export interface AiChatReasoningSummaryDeltaData {
  delta: string;
}

export interface AiChatOutputTextDeltaData {
  delta: string;
}

export interface AiChatCompletedData {
  requestId: string;
  model: string;
  providerResponseId?: string | null;
  outputText: string;
  reasoningSummary: string;
  finishReason?: string | null;
}

export interface AiChatErrorData {
  error: AiChatError;
}

export interface AiChatStartedEvent {
  sequenceNumber: number;
  event: 'started';
  data: AiChatStartedData;
}

export interface AiChatStatusEvent {
  sequenceNumber: number;
  event: 'status';
  data: AiChatStatusData;
}

export interface AiChatReasoningSummaryDeltaEvent {
  sequenceNumber: number;
  event: 'reasoning_summary_delta';
  data: AiChatReasoningSummaryDeltaData;
}

export interface AiChatOutputTextDeltaEvent {
  sequenceNumber: number;
  event: 'output_text_delta';
  data: AiChatOutputTextDeltaData;
}

export interface AiChatCompletedEvent {
  sequenceNumber: number;
  event: 'completed';
  data: AiChatCompletedData;
}

export interface AiChatErrorEvent {
  sequenceNumber: number;
  event: 'error';
  data: AiChatErrorData;
}

export type AiChatStreamEvent =
  | AiChatStartedEvent
  | AiChatStatusEvent
  | AiChatReasoningSummaryDeltaEvent
  | AiChatOutputTextDeltaEvent
  | AiChatCompletedEvent
  | AiChatErrorEvent;

export interface SymbolProviderFacts {
  symbol: string;
  name?: string | null;
  description?: string | null;
  sector?: string | null;
  industry?: string | null;
  industry2?: string | null;
  country?: string | null;
  exchange?: string | null;
  assetType?: string | null;
  ipoDate?: string | null;
  delistingDate?: string | null;
  status?: string | null;
  isOptionable?: boolean | null;
  sourceNasdaq?: boolean | null;
  sourceMassive?: boolean | null;
  sourceAlphaVantage?: boolean | null;
}

export interface SymbolProfileValues {
  security_type_norm?: string | null;
  exchange_mic?: string | null;
  country_of_risk?: string | null;
  sector_norm?: string | null;
  industry_group_norm?: string | null;
  industry_norm?: string | null;
  is_adr?: boolean | null;
  is_etf?: boolean | null;
  is_cef?: boolean | null;
  is_preferred?: boolean | null;
  share_class?: string | null;
  listing_status_norm?: string | null;
  issuer_summary_short?: string | null;
}

export interface SymbolCleanupWorkItem {
  workId: string;
  runId: string;
  symbol: string;
  status: SymbolWorkStatus;
  requestedFields: SymbolEnrichmentField[];
  attemptCount: number;
  executionName?: string | null;
  claimedAt?: string | null;
  lastError?: string | null;
}

export interface SymbolCleanupRunSummary {
  runId: string;
  status: SymbolCleanupStatus;
  mode: SymbolOverwriteMode;
  queuedCount: number;
  claimedCount: number;
  completedCount: number;
  failedCount: number;
  acceptedUpdateCount: number;
  rejectedUpdateCount: number;
  lockedSkipCount: number;
  overwriteCount: number;
  startedAt?: string | null;
  completedAt?: string | null;
}

export interface SymbolEnrichmentResolveRequest {
  symbol: string;
  overwriteMode: SymbolOverwriteMode;
  requestedFields: SymbolEnrichmentField[];
  providerFacts: SymbolProviderFacts;
  currentProfile?: SymbolProfileValues | null;
}

export interface SymbolEnrichmentResolveResponse {
  symbol: string;
  profile: SymbolProfileValues;
  model?: string | null;
  confidence?: number | null;
  sourceFingerprint?: string | null;
  warnings: string[];
}

export interface SymbolProfileCurrent extends SymbolProfileValues {
  symbol: string;
  sourceKind: SymbolSourceKind;
  sourceFingerprint?: string | null;
  aiModel?: string | null;
  aiConfidence?: number | null;
  validationStatus: SymbolValidationStatus;
  marketCapUsd?: number | null;
  marketCapBucket?: string | null;
  avgDollarVolume20d?: number | null;
  liquidityBucket?: string | null;
  isTradeableCommonEquity?: boolean | null;
  dataCompletenessScore?: number | null;
  updatedAt?: string | null;
}

export interface SymbolProfileHistoryEntry {
  historyId: string;
  symbol: string;
  fieldName: SymbolEnrichmentField;
  previousValue?: string | number | boolean | null;
  newValue?: string | number | boolean | null;
  sourceKind: SymbolSourceKind;
  aiModel?: string | null;
  aiConfidence?: number | null;
  changeReason?: string | null;
  runId?: string | null;
  updatedAt: string;
}

export interface SymbolProfileOverride {
  symbol: string;
  fieldName: SymbolEnrichmentField;
  value?: string | number | boolean | null;
  isLocked: boolean;
  updatedBy?: string | null;
  updatedAt?: string | null;
}

export interface SymbolEnrichmentSummaryResponse {
  backlogCount: number;
  lastRun?: SymbolCleanupRunSummary | null;
  activeRun?: SymbolCleanupRunSummary | null;
  validationFailureCount: number;
  lockCount: number;
}

export interface SymbolEnrichmentSymbolListItem {
  symbol: string;
  name?: string | null;
  status: SymbolValidationStatus;
  sourceKind: SymbolSourceKind;
  updatedAt?: string | null;
  missingFieldCount: number;
  lockedFieldCount: number;
  dataCompletenessScore?: number | null;
}

export interface SymbolEnrichmentSymbolDetailResponse {
  providerFacts: SymbolProviderFacts;
  currentProfile?: SymbolProfileCurrent | null;
  overrides: SymbolProfileOverride[];
  history: SymbolProfileHistoryEntry[];
}

export interface SymbolEnrichmentEnqueueRequest {
  symbols: string[];
  fullScan: boolean;
  overwriteMode: SymbolOverwriteMode;
  maxSymbols?: number | null;
}

export interface RankingGroup {
  name: string;
  weight: number;
  factors: RankingFactor[];
  transforms: RankingTransform[];
}

export interface RankingSchemaConfig {
  universeConfigName?: string;
  groups: RankingGroup[];
  overallTransforms: RankingTransform[];
}

export interface RankingPreviewRow {
  symbol: string;
  rank: number;
  score: number;
}

export interface RankingMaterializationSummary {
  runId: string;
  strategyName: string;
  rankingSchemaName: string;
  rankingSchemaVersion: number;
  outputTableName: string;
  startDate?: string | null;
  endDate?: string | null;
  rowCount: number;
  dateCount: number;
}

export interface RegimeModelConfig {
  trendPositiveThreshold: number;
  trendNegativeThreshold: number;
  curveContangoThreshold: number;
  curveInvertedThreshold: number;
  highVolEnterThreshold: number;
  highVolExitThreshold: number;
  bearVolMin: number;
  bearVolMaxExclusive: number;
  bullVolMaxExclusive: number;
  choppyVolMin: number;
  choppyVolMaxExclusive: number;
  haltVixThreshold: number;
  haltVixStreakDays: number;
  precedence: RegimeCode[];
}

export interface RegimeSnapshot {
  as_of_date: string;
  effective_from_date: string;
  model_name: string;
  model_version: number;
  regime_code: RegimeCode;
  regime_status: RegimeStatus;
  matched_rule_id?: string | null;
  halt_flag: boolean;
  halt_reason?: string | null;
  spy_return_20d?: number | null;
  rvol_10d_ann?: number | null;
  vix_spot_close?: number | null;
  vix3m_close?: number | null;
  vix_slope?: number | null;
  trend_state?: TrendState | null;
  curve_state?: CurveState | null;
  vix_gt_32_streak?: number | null;
  computed_at?: string | null;
}

export interface RegimeInputRow {
  as_of_date: string;
  spy_close?: number | null;
  return_1d?: number | null;
  return_20d?: number | null;
  rvol_10d_ann?: number | null;
  vix_spot_close?: number | null;
  vix3m_close?: number | null;
  vix_slope?: number | null;
  trend_state?: TrendState | null;
  curve_state?: CurveState | null;
  vix_gt_32_streak?: number | null;
  inputs_complete_flag: boolean;
  computed_at?: string | null;
}

export interface RegimeTransitionRow {
  model_name: string;
  model_version: number;
  effective_from_date: string;
  prior_regime_code?: RegimeCode | null;
  new_regime_code: RegimeCode;
  trigger_rule_id?: string | null;
  computed_at?: string | null;
}

export interface RegimeModelSummary {
  name: string;
  description?: string;
  version: number;
  updated_at?: string | null;
  active_version?: number | null;
  activated_at?: string | null;
  activated_by?: string | null;
}

export interface RegimeModelRevision {
  name: string;
  version: number;
  description?: string;
  config: RegimeModelConfig;
  status?: string | null;
  config_hash?: string | null;
  published_at?: string | null;
  created_at?: string | null;
  activated_at?: string | null;
  activated_by?: string | null;
}

export interface RegimeModelDetailResponse {
  model: RegimeModelSummary;
  activeRevision?: RegimeModelRevision | null;
  revisions: RegimeModelRevision[];
  latest?: RegimeSnapshot | null;
}

export interface UiRuntimeConfig {
  apiBaseUrl: string;
  oidcEnabled: boolean;
  authRequired: boolean;
  oidcAuthority?: string;
  oidcClientId?: string;
  oidcScopes: string[];
  oidcRedirectUri?: string;
  oidcPostLogoutRedirectUri?: string;
  oidcAudience: string[];
}

export interface AuthSessionStatus {
  authMode: string;
  subject: string;
  displayName?: string | null;
  username?: string | null;
  requiredRoles: string[];
  grantedRoles: string[];
}

export interface RunRecordResponse {
  run_id: string;
  status: RunStatus;
  submitted_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  run_name?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  error?: string | null;
}

export interface RunListResponse {
  runs: RunRecordResponse[];
  limit: number;
  offset: number;
}

export interface BacktestSummary {
  run_id?: string;
  run_name?: string;
  start_date?: string;
  end_date?: string;
  total_return?: number;
  annualized_return?: number;
  annualized_volatility?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  trades?: number;
  initial_cash?: number;
  final_equity?: number;
  gross_total_return?: number;
  gross_annualized_return?: number;
  total_commission?: number;
  total_slippage_cost?: number;
  total_transaction_cost?: number;
  cost_drag_bps?: number;
  avg_gross_exposure?: number;
  avg_net_exposure?: number;
  sortino_ratio?: number;
  calmar_ratio?: number;
  closed_positions?: number;
  winning_positions?: number;
  losing_positions?: number;
  hit_rate?: number;
  avg_win_pnl?: number;
  avg_loss_pnl?: number;
  avg_win_return?: number;
  avg_loss_return?: number;
  payoff_ratio?: number;
  profit_factor?: number;
  expectancy_pnl?: number;
  expectancy_return?: number;
  [key: string]: unknown;
}

export interface BacktestResultMetadata {
  results_schema_version: number;
  bar_size: string;
  periods_per_year: number;
  strategy_scope: string;
}

export interface TimeseriesPointResponse {
  date: string;
  portfolio_value: number;
  drawdown: number;
  period_return?: number | null;
  /** @deprecated Use period_return. */
  daily_return?: number | null;
  cumulative_return?: number | null;
  cash?: number | null;
  gross_exposure?: number | null;
  net_exposure?: number | null;
  turnover?: number | null;
  commission?: number | null;
  slippage_cost?: number | null;
}

export interface TimeseriesResponse {
  metadata?: BacktestResultMetadata | null;
  points: TimeseriesPointResponse[];
  total_points: number;
  truncated: boolean;
}

export interface RollingMetricPointResponse {
  date: string;
  window_periods?: number | null;
  /** @deprecated Use window_periods. */
  window_days?: number | null;
  rolling_return?: number | null;
  rolling_volatility?: number | null;
  rolling_sharpe?: number | null;
  rolling_max_drawdown?: number | null;
  turnover_sum?: number | null;
  commission_sum?: number | null;
  slippage_cost_sum?: number | null;
  n_trades_sum?: number | null;
  gross_exposure_avg?: number | null;
  net_exposure_avg?: number | null;
}

export interface RollingMetricsResponse {
  metadata?: BacktestResultMetadata | null;
  points: RollingMetricPointResponse[];
  total_points: number;
  truncated: boolean;
}

export interface TradeResponse {
  execution_date: string;
  symbol: string;
  quantity: number;
  price: number;
  notional: number;
  commission: number;
  slippage_cost: number;
  cash_after: number;
  position_id?: string | null;
  trade_role?: TradeRole | null;
}

export interface TradeListResponse {
  trades: TradeResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface ClosedPositionResponse {
  position_id: string;
  symbol: string;
  opened_at: string;
  closed_at: string;
  holding_period_bars: number;
  average_cost: number;
  exit_price: number;
  max_quantity: number;
  resize_count: number;
  realized_pnl: number;
  realized_return?: number | null;
  total_commission: number;
  total_slippage_cost: number;
  total_transaction_cost: number;
  exit_reason?: string | null;
  exit_rule_id?: string | null;
}

export interface ClosedPositionListResponse {
  positions: ClosedPositionResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface BacktestReconcileResponse {
  dispatchedCount: number;
  dispatchFailedCount: number;
  failedStaleRunningCount: number;
  skippedActiveCount: number;
  noActionCount: number;
  dispatchedRunIds: string[];
  dispatchFailedRunIds: string[];
  failedRunIds: string[];
}
