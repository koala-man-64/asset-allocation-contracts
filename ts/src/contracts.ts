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

export type GovernmentSignalSeverity = 'low' | 'medium' | 'high' | 'critical';
export type GovernmentSignalMappingStatus = 'pending_review' | 'mapped' | 'ignored';
export type GovernmentSignalMappingAction = 'map' | 'ignore' | 'defer';
export type GovernmentSignalAlertType = 'congress_trade' | 'contract_event' | 'composite';
export type CongressTradeChamber = 'house' | 'senate' | 'joint' | 'unknown';
export type CongressTradeRelationship = 'self' | 'spouse' | 'dependent_child' | 'joint' | 'unknown';
export type CongressTradeType = 'purchase' | 'sale' | 'partial_sale' | 'exchange' | 'other';
export type CongressTradeFilingStatus = 'new' | 'amended' | 'late' | 'unknown';
export type GovernmentContractEventType =
  | 'opportunity'
  | 'award'
  | 'modification'
  | 'option_exercise'
  | 'obligation'
  | 'outlay'
  | 'termination'
  | 'cancellation'
  | 'protest'
  | 'other';

export interface CongressTradeEvent {
  event_id: string;
  source_name: string;
  source_event_key: string;
  member_id?: string | null;
  member_name: string;
  chamber: CongressTradeChamber;
  party?: string | null;
  state?: string | null;
  district?: string | null;
  committee_names: string[];
  traded_at: string;
  filed_at?: string | null;
  notified_at?: string | null;
  relationship_type: CongressTradeRelationship;
  transaction_type: CongressTradeType;
  filing_status: CongressTradeFilingStatus;
  amendment_flag: boolean;
  late_filing_days?: number | null;
  asset_name: string;
  asset_description?: string | null;
  asset_type?: string | null;
  issuer_name?: string | null;
  issuer_ticker?: string | null;
  amount_lower_usd?: number | null;
  amount_upper_usd?: number | null;
  amount_bucket_label?: string | null;
  comments?: string | null;
  excess_return?: number | null;
  confidence?: number | null;
  mapping_status: GovernmentSignalMappingStatus;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface CongressTradeVersion {
  version_id: string;
  event_id: string;
  version_seq: number;
  version_kind: string;
  version_observed_at: string;
  event: CongressTradeEvent;
}

export interface CongressTradeEventListResponse {
  events: CongressTradeEvent[];
  total: number;
  limit: number;
  offset: number;
}

export interface GovernmentContractEvent {
  event_id: string;
  source_name: string;
  source_event_key: string;
  event_type: GovernmentContractEventType;
  event_at: string;
  recipient_name: string;
  recipient_ticker?: string | null;
  awarding_agency: string;
  funding_agency?: string | null;
  award_id?: string | null;
  parent_award_id?: string | null;
  opportunity_id?: string | null;
  solicitation_id?: string | null;
  title: string;
  description?: string | null;
  award_amount_usd?: number | null;
  obligation_delta_usd?: number | null;
  outlay_delta_usd?: number | null;
  cumulative_obligation_usd?: number | null;
  modification_number?: string | null;
  option_exercise_flag: boolean;
  termination_flag: boolean;
  cancellation_flag: boolean;
  protest_flag: boolean;
  naics_code?: string | null;
  psc_code?: string | null;
  competition_type?: string | null;
  set_aside_type?: string | null;
  contract_vehicle?: string | null;
  place_of_performance_country?: string | null;
  place_of_performance_state?: string | null;
  confidence?: number | null;
  mapping_status: GovernmentSignalMappingStatus;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface GovernmentContractVersion {
  version_id: string;
  event_id: string;
  version_seq: number;
  version_kind: string;
  version_observed_at: string;
  event: GovernmentContractEvent;
}

export interface GovernmentContractEventListResponse {
  events: GovernmentContractEvent[];
  total: number;
  limit: number;
  offset: number;
}

export interface IssuerGovernmentSignalDaily {
  as_of_date: string;
  symbol: string;
  issuer_name?: string | null;
  congress_purchase_count_1d: number;
  congress_purchase_count_7d: number;
  congress_purchase_count_30d: number;
  congress_purchase_count_90d: number;
  congress_sale_count_1d: number;
  congress_sale_count_7d: number;
  congress_sale_count_30d: number;
  congress_sale_count_90d: number;
  congress_net_amount_proxy_usd_30d: number;
  congress_net_amount_proxy_usd_90d: number;
  congress_amendment_rate_90d: number;
  congress_late_filing_rate_90d: number;
  congress_unique_members_90d: number;
  congress_unique_committees_90d: number;
  contract_award_count_30d: number;
  contract_award_count_90d: number;
  contract_obligation_delta_usd_30d: number;
  contract_obligation_delta_usd_90d: number;
  contract_outlay_delta_usd_30d: number;
  contract_outlay_delta_usd_90d: number;
  contract_modification_count_90d: number;
  contract_option_exercise_count_90d: number;
  contract_termination_count_90d: number;
  contract_cancellation_count_90d: number;
  contract_protest_count_90d: number;
  contract_unique_awarding_agencies_90d: number;
  contract_unique_naics_90d: number;
  contract_unique_psc_90d: number;
  last_congress_trade_at?: string | null;
  last_contract_event_at?: string | null;
  mapping_status: GovernmentSignalMappingStatus;
}

export interface GovernmentSignalAlert {
  alert_id: string;
  symbol: string;
  as_of_date: string;
  alert_type: GovernmentSignalAlertType;
  severity: GovernmentSignalSeverity;
  title: string;
  summary: string;
  congress_signal_score?: number | null;
  contract_signal_score?: number | null;
  composite_signal_score?: number | null;
  source_event_ids: string[];
  created_at?: string | null;
}

export interface GovernmentSignalAlertListResponse {
  alerts: GovernmentSignalAlert[];
  total: number;
  limit: number;
  offset: number;
}

export interface GovernmentSignalMappingReviewItem {
  mapping_id: string;
  source_name: string;
  entity_type: string;
  raw_key: string;
  raw_name: string;
  proposed_symbol?: string | null;
  confidence?: number | null;
  status: GovernmentSignalMappingStatus;
  reason?: string | null;
  updated_at?: string | null;
}

export interface GovernmentSignalMappingReviewResponse {
  items: GovernmentSignalMappingReviewItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface GovernmentSignalMappingOverrideRequest {
  action: GovernmentSignalMappingAction;
  symbol?: string | null;
  reason?: string | null;
}

export interface GovernmentSignalMappingOverrideResponse {
  mapping_id: string;
  status: GovernmentSignalMappingStatus;
  symbol?: string | null;
  updated_at: string;
}

export interface GovernmentSignalIssuerSummaryResponse {
  symbol: string;
  issuer_name?: string | null;
  as_of_date: string;
  issuer_daily: IssuerGovernmentSignalDaily;
  recent_congress_trades: CongressTradeEvent[];
  recent_contract_events: GovernmentContractEvent[];
  active_alerts: GovernmentSignalAlert[];
}

export interface GovernmentSignalPortfolioHolding {
  symbol: string;
  shares?: number | null;
  market_value?: number | null;
  portfolio_weight?: number | null;
}

export interface GovernmentSignalPortfolioIssuerExposure {
  symbol: string;
  issuer_name?: string | null;
  matched: boolean;
  market_value?: number | null;
  portfolio_weight?: number | null;
  issuer_daily?: IssuerGovernmentSignalDaily | null;
  alerts: GovernmentSignalAlert[];
}

export interface GovernmentSignalPortfolioExposureRequest {
  as_of_date?: string | null;
  holdings: GovernmentSignalPortfolioHolding[];
}

export interface GovernmentSignalPortfolioExposureResponse {
  as_of_date: string;
  holdings_analyzed: number;
  matched_holdings: number;
  unmatched_symbols: string[];
  total_market_value?: number | null;
  total_portfolio_weight?: number | null;
  exposures: GovernmentSignalPortfolioIssuerExposure[];
}
