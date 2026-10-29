# Data contracts

## Document

```json
{"id":"example-1","title":"Example","project":"demo","access":"public","version":1,"text":"Storage capacity: 100 MWh."}
```

Required: unique nonempty string `id`, `title`, `text`. Optional `project` defaults to demo; `access` is public/internal; `supersedes` references a document in the same project. Cycles, missing replacement targets, duplicate IDs and corpora exceeding 400,000 characters are rejected. Metadata is an input assertion, not an authenticated issuer statement.

## Supported fields

`capacity`: storage energy in GWh/MWh/kWh; `power`: rated power in GW/MW/kW; `duration`: hours/minutes; `investment`: CNY/USD (no FX conversion); `operator`: explicit operator text; `generation_capacity`: net summer generating capacity in MW; `generation`: net generation in MWh; `retail_price`: cents/kWh.

Chinese and English documented patterns are in src/agents.py. Numeric units normalize using Decimal. Scope comes from one selected project; year/location differences must use distinct project IDs. This does not infer real-world applicability from document content or timestamps. Capitalization/punctuation, unseen phrasing, OCR, implicit facts and ambiguous scope require review.

## Output and journal

A review returns status, per-field decisions, exact quote offsets/line, source/version, units, visible corpus hash, role handoffs and latency. Status can be supported, conflict, insufficient, partial or needs_review. A supported result refers to this bounded evidence check, not universal truth. Hash links permit local consistency checking, not proof against a party recomputing all hashes. Model role notes are separate from structured conclusions.

## HTTP

GET /api/config returns a local request token and a configuration flag (never keys). POST /api/review, /api/summary and /api/ingest require X-Review-Token; permitted browser origins are local. Import accepts base64 PDF/TXT/MD up to 2 MB, PDF up to 50 pages with a text layer. No uploaded files are persisted. Binding, request checks and simulated document labels are not a multi-user production security architecture.
