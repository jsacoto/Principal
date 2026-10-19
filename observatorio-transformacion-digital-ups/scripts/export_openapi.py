#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "apps" / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from app.main import app  # noqa: E402


def main() -> None:
    output = ROOT / "openapi" / "openapi.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    schema = app.openapi()
    output.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OpenAPI exported: {output}")
    print(f"Contract version: {schema['info']['version']}")
    print(f"Documented paths: {len(schema.get('paths', {}))}")


if __name__ == "__main__":
    main()
