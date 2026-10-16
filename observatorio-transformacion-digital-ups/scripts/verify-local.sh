#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT_DIR/apps/api"
python -m compileall -q app
pytest -q
python - <<'PY'
from app.data.portfolio_seed import INITIATIVES, ACTIVITIES, MODEL16_GROUPS
print(f"Initiatives: {len(INITIATIVES)}")
print(f"Activity/phase rows: {sum(len(v) for v in ACTIVITIES.values())}")
print(f"Institutional model groups: {len(MODEL16_GROUPS)}")
missing=[i['code'] for i in INITIATIVES if i['code'] not in ACTIVITIES]
if missing:
    raise SystemExit(f"Missing activity groups: {missing}")
PY

cd "$ROOT_DIR"
python - <<'PY'
import yaml
files = ('docker-compose.yml','docker-compose.mac.yml','docker-compose.test.yml','docker-compose.server.yml')
for name in files:
    with open(name, encoding='utf-8') as f:
        doc=yaml.safe_load(f)
    assert 'services' in doc and doc['services'], name
    print(f"{name}: OK ({', '.join(sorted(doc['services']))})")
PY

for script in scripts/*.sh; do bash -n "$script"; done
printf '\nBackend, seed, shell scripts and all Compose manifests verified.\n'
