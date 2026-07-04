# Hot Trend Lab Integration

This integration adds an English-language Hot Trend Lab tutorial column to the DeTime repository without changing the existing documentation design or rewriting existing pages.

Changed existing file:

- `mkdocs.yml`: added one Tutorials navigation group named `Hot Trend Lab`.

Added directories and files:

- `docs/tutorials/hot-trend-lab.md`
- `docs/tutorials/hot-trend-lab/`
- `examples/hot_trends/`
- `examples/notebooks/hot_trends/`

Paper-writing materials:

- Manuscript and journal-facing materials are kept outside this public code tree.

Data sources:

- The Hot Trend Lab fetches public data at runtime.
- Each notebook records source coverage, freshness, query context, and measurement limits.

Local checks performed in this packaging environment:

```bash
$env:PYTHONPATH='src;examples'
python -m compileall -q examples/hot_trends
@'
from pathlib import Path
import json
for p in Path('examples/notebooks/hot_trends').glob('*.ipynb'):
    json.loads(p.read_text())
print('hot trend notebooks valid JSON')
'@ | python -
```

Network notebooks were not executed in this packaging environment because external network access was unavailable to the container.

Additional compatibility change:

- `scripts/check_doc_consistency.py`: keeps public documentation checks focused on code, docs, and release evidence.
