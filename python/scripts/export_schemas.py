from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from contract_codegen import SCHEMA_EXPORTS, write_typescript_contracts


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas"
TS_CONTRACTS = ROOT / "ts" / "src" / "contracts.ts"


def _write(name: str, model) -> None:
    SCHEMAS.mkdir(parents=True, exist_ok=True)
    path = SCHEMAS / name
    path.write_text(json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    for filename, model in SCHEMA_EXPORTS:
        _write(filename, model)
    write_typescript_contracts(TS_CONTRACTS)


if __name__ == "__main__":
    main()
