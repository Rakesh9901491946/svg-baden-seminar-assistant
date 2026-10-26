"""Validate the manually refreshed public-source corpus; does not fetch pages."""
import json
from pathlib import Path
from app.sources import parse_source_json

path = Path(__file__).parent / "data/sources.json"
sources = parse_source_json(path.read_text(encoding="utf-8"))
print(f"Validated {len(sources)} attributed sources in {path}")
