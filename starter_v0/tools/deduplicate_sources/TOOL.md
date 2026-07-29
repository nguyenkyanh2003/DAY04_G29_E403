---
name: deduplicate_sources
track: bonus
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [items, input_count, unique_count, duplicates_removed]
side_effect: false
---
# deduplicate_sources

Removes duplicate research items by canonical URL, falling back to normalized
title. Common tracking parameters are ignored and the richer duplicate is kept.

Use after collecting results from one or more search tools. It does not fetch,
rank, summarize, or verify sources.
