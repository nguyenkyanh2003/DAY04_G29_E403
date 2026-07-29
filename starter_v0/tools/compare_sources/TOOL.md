---
name: compare_sources
track: bonus
kind: local_formatter
requires_env: []
inputs: [source_a, source_b, max_terms]
outputs: [source_a, source_b, shared_terms, only_source_a, only_source_b, lexical_similarity, warning]
side_effect: false
---
# compare_sources

Compares the title and summary terms of two already-collected sources. It
returns shared and source-specific terms plus a transparent Jaccard score.

Use for a quick lexical comparison. It does not fetch source content,
fact-check claims, or prove that two sources agree.
