from __future__ import annotations

from typing import Any

from tools._shared import err, terms


def _provider_score(value: Any) -> float:
    try:
        return max(0.0, min(float(value), 1.0))
    except (TypeError, ValueError):
        return 0.0


def rank_sources(
    items: list[dict[str, Any]] | None = None,
    query: str = "",
    limit: int = 5,
) -> dict[str, Any]:
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list")
        limit = max(1, min(int(limit or 5), 20))
        query_terms = terms(query)
        ranked: list[dict[str, Any]] = []

        for index, raw in enumerate(items):
            if not isinstance(raw, dict):
                raise ValueError("each item must be an object")
            item = dict(raw)
            item_terms = terms(" ".join(str(item.get(key) or "") for key in ("title", "summary", "source")))
            matched = sorted(query_terms & item_terms)
            coverage = len(matched) / len(query_terms) if query_terms else 0.0
            score = 0.7 * coverage + 0.3 * _provider_score(item.get("score"))
            item["rank_score"] = round(score, 4)
            item["matched_terms"] = matched
            item["_input_order"] = index
            ranked.append(item)

        ranked.sort(key=lambda item: (-item["rank_score"], item["_input_order"]))
        for item in ranked:
            item.pop("_input_order")
        return {
            "tool": "rank_sources",
            "query": query,
            "items": ranked[:limit],
            "input_count": len(items),
            "returned_count": min(len(ranked), limit),
            "method": "70% query-term coverage + 30% provider score",
        }
    except Exception as exc:
        return err("rank_sources", exc)
