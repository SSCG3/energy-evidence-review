# Validation record — v0.2.0

All results are author-side development observations, not external reproduction.

## Local automated checks

- `python3 -m unittest discover -s tests -v`: 22 tests, including source quote integrity, hidden-source isolation, unit normalization, per-field revision behavior, invalid metadata, role-call protocol mocks and HTTP request/origin checks.
- `python3 evaluation/run_comparison.py`: 40 synthetic development cases, first-hit 28/40, all-source 36/40, coordinated 40/40. Four variations per category are not independent deployments.
- `python3 evaluation/run_public_data.py`: 12 EIA raw-row consistency checks, all methods 12/12; no comparative improvement is inferred.
- Actual EIA snapshot, raw hash and transformation: examples/public_sources/manifest.json.
- Text-layer PDF adapter import was exercised using examples/eia-california-2024.pdf. Scanned PDF/OCR is not supported.

## Actual domestic model calls

scripts/validate_models.py ran three scenarios, nine completions, using DeepSeek analyst/reporter and GLM reviewer. Exact IDs, usage, objections and outputs are retained in results/model-validation.json. Scenario completion and valid source IDs are not semantic-accuracy scores. Unit-test mocks are separate.

## Browser/noVNC

Run `node scripts/capture_browser.mjs` with an existing Chrome CDP endpoint at localhost:9222 and DISPLAY=:99. It opens a dedicated local window, exercises the actual UI and captures the desktop including the real 127.0.0.1:8765 address bar. It never draws an artificial address bar. The mobile screenshot is explicitly content-only.

See results/browser-validation.json for checks and actual browser identity, results/browser-review.json for the model-assisted UI run, and docs/screenshots for images. Old 0.1.0 screenshots are archived and must not be described as current.

## Report

scripts/build_report.py generates exactly ten English PDF pages and a corresponding Markdown source from actual run artifacts. The PDF is an author-side technical description, not a journal article, external review or employer certificate.
