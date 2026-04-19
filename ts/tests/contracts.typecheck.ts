import type {
  AiChatStreamEvent,
  SymbolCleanupRunSummary,
  SymbolEnrichmentResolveRequest,
  SymbolEnrichmentSymbolDetailResponse,
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

void catalog;
void preview;
void condition;

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

void resolveRequest;
void detail;
void runSummary;
void aiEvent;
