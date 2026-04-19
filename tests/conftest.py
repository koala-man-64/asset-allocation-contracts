from __future__ import annotations

import sys
from pathlib import Path

# Force pytest to import the contracts from this checkout, not an unrelated
# editable install that may still be registered in site-packages.
PYTHON_SRC = Path(__file__).resolve().parents[1] / "python"
python_src_str = str(PYTHON_SRC)
if python_src_str not in sys.path:
    sys.path.insert(0, python_src_str)
