---
name: rank_sources
track: bonus
kind: local_formatter
requires_env: []
inputs: [items, query, limit]
outputs: [items, input_count, returned_count, method]
side_effect: false
---
# rank_sources

Ranks already-collected research items using query-term coverage and an
optional provider relevance score. The returned items include `rank_score`
and `matched_terms` so the ordering is auditable.

Use after search when the user asks to prioritize relevant sources. It does
not fetch new data or judge whether a claim is true.
