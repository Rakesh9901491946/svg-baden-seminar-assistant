"""Load and validate the attributed local source corpus."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sources.json"

class SourceDataError(ValueError):
    pass

def load_sources(path: Path | str = DATA_PATH) -> list[dict[str, Any]]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        sources = data["sources"]
        if not isinstance(sources, list):
            raise ValueError("sources must be a list")
        for source in sources:
            for key in ("id", "title", "url", "retrieved_at", "provider", "text"):
                if not source.get(key):
                    raise ValueError(f"source missing {key}")
            if not source["url"].startswith("https://www.svg-baden.de/"):
                raise ValueError("source URL is outside the approved domain")
        return sources
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise SourceDataError(f"Could not load source corpus: {exc}") from exc

def parse_source_json(raw: str) -> list[dict[str, Any]]:
    """Validate JSON payloads used by refresh tooling and tests."""
    try:
        payload = json.loads(raw)
        sources = payload["sources"]
        if not isinstance(sources, list):
            raise ValueError("sources must be a list")
        for source in sources:
            if not all(source.get(k) for k in ("id", "title", "url", "retrieved_at", "provider", "text")):
                raise ValueError("source record is incomplete")
        return sources
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise SourceDataError(str(exc)) from exc
