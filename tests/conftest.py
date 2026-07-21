# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.meta_path[:] = [
    finder
    for finder in sys.meta_path
    if not any(token in finder.__class__.__module__.lower() for token in ("detime", "de_time"))
]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

for name in list(sys.modules):
    if name == "detime" or name.startswith("detime.") or name == "tsdecomp" or name.startswith("tsdecomp."):
        sys.modules.pop(name)
