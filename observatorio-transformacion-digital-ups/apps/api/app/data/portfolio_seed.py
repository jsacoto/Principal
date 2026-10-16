from __future__ import annotations

# Generated compact snapshot payload. Source: UPS Notion portfolio snapshot 2026-10-16.
# Keeping the snapshot compressed makes repository transport reproducible without changing the data model.
import base64
import gzip
import json

from .portfolio_blob_01 import CHUNK_01
from .portfolio_blob_02 import CHUNK_02
from .portfolio_blob_03 import CHUNK_03
from .portfolio_blob_04 import CHUNK_04
from .portfolio_blob_05 import CHUNK_05
from .portfolio_blob_06 import CHUNK_06

_PAYLOAD = json.loads(gzip.decompress(base64.b64decode(CHUNK_01 + CHUNK_02 + CHUNK_03 + CHUNK_04 + CHUNK_05 + CHUNK_06)).decode("utf-8"))

REFERENCE_MATURITY = _PAYLOAD["REFERENCE_MATURITY"]
MODEL16_GROUPS = _PAYLOAD["MODEL16_GROUPS"]
NOTION_ROOT = _PAYLOAD["NOTION_ROOT"]
SNAPSHOT_DATE = _PAYLOAD["SNAPSHOT_DATE"]
DIMENSIONS = _PAYLOAD["DIMENSIONS"]
OBJECTIVES = _PAYLOAD["OBJECTIVES"]
USER_DIRECTORY = _PAYLOAD["USER_DIRECTORY"]
INITIATIVES = _PAYLOAD["INITIATIVES"]
PROVISIONAL_CONTRIBUTIONS = _PAYLOAD["PROVISIONAL_CONTRIBUTIONS"]
OBJECTIVE_DIMENSION_HEATMAP = _PAYLOAD["OBJECTIVE_DIMENSION_HEATMAP"]
KEY_RESULTS = _PAYLOAD["KEY_RESULTS"]
KPIS = _PAYLOAD["KPIS"]
ACTIVITIES = _PAYLOAD["ACTIVITIES"]
ACTIVITY_RESPONSIBLE_IDS = _PAYLOAD["ACTIVITY_RESPONSIBLE_IDS"]
