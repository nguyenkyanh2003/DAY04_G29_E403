from __future__ import annotations

from typing import Any

from tools._shared import err, terms


def _source_terms(source: dict[str, Any]) -> set[str]:
    return terms(" ".join(str(source.get(key) or "") for key in ("title", "summary")))


def _label(source: dict[str, Any], fallback: str) -> str:
    return str(source.get("source") or source.get("title") or source.get("url") or fallback)


def compare_sources(
    source_a: dict[str, Any] | None = None,
    source_b: dict[str, Any] | None = None,
    max_terms: int = 12,
) -> dict[str, Any]:
    try:
        if not isinstance(source_a, dict) or not isinstance(source_b, dict):
            raise ValueError("source_a and source_b must be objects")
        max_terms = max(1, min(int(max_terms or 12), 30))
        a_terms, b_terms = _source_terms(source_a), _source_terms(source_b)
        union = a_terms | b_terms
        return {
            "tool": "compare_sources",
            "source_a": _label(source_a, "source_a"),
            "source_b": _label(source_b, "source_b"),
            "shared_terms": sorted(a_terms & b_terms)[:max_terms],
            "only_source_a": sorted(a_terms - b_terms)[:max_terms],
            "only_source_b": sorted(b_terms - a_terms)[:max_terms],
            "lexical_similarity": round(len(a_terms & b_terms) / len(union), 4) if union else 0.0,
            "warning": "Lexical overlap is not fact-checking or proof of agreement.",
        }
    except Exception as exc:
        return err("compare_sources", exc)
