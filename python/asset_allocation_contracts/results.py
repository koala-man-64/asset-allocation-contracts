from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StrictStr

NonNegativeCount = Annotated[int, Field(ge=0, strict=True)]


class ResultsReconcileResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rankingDirtyCount: NonNegativeCount
    rankingNoopCount: NonNegativeCount
    canonicalEnqueuedCount: NonNegativeCount
    canonicalUpToDateCount: NonNegativeCount
    canonicalSkippedCount: NonNegativeCount
    publicationSignalsProcessedCount: NonNegativeCount
    publicationSignalsErrorCount: NonNegativeCount
    errorCount: NonNegativeCount
    errors: list[StrictStr]
