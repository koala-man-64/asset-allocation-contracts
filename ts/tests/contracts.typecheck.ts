import type {
  PortfolioAccount,
  PortfolioRevision,
  PortfolioSnapshot,
  PortfolioUpsertRequest,
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
