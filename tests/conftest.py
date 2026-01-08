from __future__ import annotations

from pathlib import Path
import sys

# Ensure the local `src/` package is imported before any installed package with the
# same name. This makes the test suite deterministic when a same-named package
# exists elsewhere in the environment.
root = Path(__file__).resolve().parents[1]
src = root / "src"
if str(src) not in sys.path:
    sys.path.insert(0, str(src))
