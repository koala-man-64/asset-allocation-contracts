from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
for path in (SCRIPT_DIR, PACKAGE_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from contract_codegen import write_schema_exports, write_typescript_contracts


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas"
TS_CONTRACTS = ROOT / "ts" / "src" / "contracts.ts"


def main() -> None:
    write_schema_exports(SCHEMAS)
    write_typescript_contracts(TS_CONTRACTS)


if __name__ == "__main__":
    main()
