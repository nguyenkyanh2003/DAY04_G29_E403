from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit

from tools._shared import err, fold_text


def _identity(item: dict[str, Any]) -> str:
    url = str(item.get("url") or "").strip()
    if url:
        parsed = urlsplit(url)
        host = parsed.netloc.lower().removeprefix("www.")
        path = parsed.path.rstrip("/")
        query = urlencode(sorted(
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if not key.lower().startswith("utm_") and key.lower() not in {"fbclid", "gclid"}
        ))
        if host:
            return f"url:{host}{path}?{query}" if query else f"url:{host}{path}"
    title = re.sub(r"[^a-z0-9]+", " ", fold_text(str(item.get("title") or ""))).strip()
    return f"title:{title}" if title else ""


def deduplicate_sources(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list")

        unique: list[dict[str, Any]] = []
        positions: dict[str, int] = {}
        for raw in items:
            if not isinstance(raw, dict):
                raise ValueError("each item must be an object")
            item = dict(raw)
            key = _identity(item)
            if not key or key not in positions:
                if key:
                    positions[key] = len(unique)
                unique.append(item)
                continue

            kept = unique[positions[key]]
            if len(str(item.get("summary") or "")) > len(str(kept.get("summary") or "")):
                kept["summary"] = item["summary"]
            for field, value in item.items():
                if value and not kept.get(field):
                    kept[field] = value

        return {
            "tool": "deduplicate_sources",
            "items": unique,
            "input_count": len(items),
            "unique_count": len(unique),
            "duplicates_removed": len(items) - len(unique),
        }
    except Exception as exc:
        return err("deduplicate_sources", exc)
