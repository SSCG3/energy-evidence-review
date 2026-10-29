# Repository Guidelines

This is an independent public reference implementation, not Jinshi source code or an immigration decision.

## Structure
`src/` contains bounded agents, orchestration, corpus adapters and an optional model client. `web/` is the workbench. `examples/` contains synthetic materials. `evaluation/` holds author-side cases and scoring. `results/` stores actual runs. `docs/` contains the technical report, source mapping and screenshots.

## Commands
Run `python3 server.py`, `python3 -m unittest discover -s tests -v`, and `python3 evaluation/run_comparison.py`. Optional PDF support uses `pip install -r requirements-pdf.txt`. Core code uses Python standard library only.

## Changes
Use four-space Python indentation, snake_case functions and explicit data contracts. Keep credentials out of logs and Git. Preserve source citations, version relations, unit normalization and permission-filter invariants. Tests must not feed expected labels to the engine. Recompute results after engine changes; preserve published release results under versioned directories.

## Claims and provenance
Describe deterministic agents as deterministic. Distinguish model mocks, live model calls and external replication. Do not invent adoption, experts, employer clearance, commercial outcomes or benchmark superiority. No copying employer code/data or redistributing manuscripts. Public docs describe software use; private case analysis belongs outside this repository.

## Review
Commit messages use imperative scoped descriptions. Include relevant tests and screenshots for UI changes. Do not spawn subagents unless explicitly requested by the user.
