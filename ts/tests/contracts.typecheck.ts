import type {
  CongressTradeEventListResponse,
  GovernmentSignalMappingOverrideRequest,
  GovernmentSignalPortfolioExposureRequest,
  UniverseCatalogResponse,
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

const condition: UniverseCondition = {
  kind: "condition",
  field: "market.close",
  operator: "gt",
  value: 10,
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

void catalog;
void preview;
void condition;
void congressEvents;
void overrideRequest;
void exposureRequest;
