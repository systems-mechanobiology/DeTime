# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import sys
from pathlib import Path


def prefer_repo_source(root: Path) -> None:
    """Make release scripts import this checkout, not a stale editable wheel."""
    sys.meta_path[:] = [
        finder
        for finder in sys.meta_path
        if not any(token in finder.__class__.__module__.lower() for token in ("detime", "de_time"))
    ]
    source = str(root / "src")
    sys.path = [entry for entry in sys.path if entry != source]
    sys.path.insert(0, source)
    for name in list(sys.modules):
        if name == "detime" or name.startswith("detime."):
            sys.modules.pop(name)
