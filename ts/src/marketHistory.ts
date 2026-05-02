export const BRONZE_MARKET_COLUMNS = [
  'symbol',
  'date',
  'open',
  'high',
  'low',
  'close',
  'volume',
  'short_interest',
  'short_volume',
  'dividend_amount',
  'split_coefficient',
  'ingested_at',
  'source_hash',
] as const;

export const LEGACY_SILVER_MARKET_COLUMNS = [
  'date',
  'symbol',
  'open',
  'high',
  'low',
  'close',
  'volume',
  'short_interest',
  'short_volume',
] as const;

export const SILVER_MARKET_COLUMNS = [
  'date',
  'symbol',
  'open',
  'high',
  'low',
  'close',
  'volume',
  'short_interest',
  'short_volume',
  'dividend_amount',
  'split_coefficient',
] as const;

export const SILVER_MARKET_NUMERIC_COLUMNS = [
  'open',
  'high',
  'low',
  'close',
  'volume',
  'short_interest',
  'short_volume',
  'dividend_amount',
  'split_coefficient',
] as const;

export const SILVER_MARKET_CORPORATE_ACTION_COLUMNS = [
  'dividend_amount',
  'split_coefficient',
] as const;

export const GOLD_MARKET_SILVER_SOURCE_COLUMNS = [
  'date',
  'symbol',
  'open',
  'high',
  'low',
  'close',
  'volume',
  'dividend_amount',
  'split_coefficient',
] as const;

export type BronzeMarketColumn = (typeof BRONZE_MARKET_COLUMNS)[number];
export type LegacySilverMarketColumn = (typeof LEGACY_SILVER_MARKET_COLUMNS)[number];
export type SilverMarketColumn = (typeof SILVER_MARKET_COLUMNS)[number];
export type SilverMarketNumericColumn = (typeof SILVER_MARKET_NUMERIC_COLUMNS)[number];
export type SilverMarketCorporateActionColumn = (typeof SILVER_MARKET_CORPORATE_ACTION_COLUMNS)[number];
export type GoldMarketSilverSourceColumn = (typeof GOLD_MARKET_SILVER_SOURCE_COLUMNS)[number];
