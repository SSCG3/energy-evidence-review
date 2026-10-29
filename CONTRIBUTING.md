# Contributing and independent reproduction

Run the local server, tests and both evaluation runners in README.md. Report Python/OS version, exact Git commit/tag, corpus hash, model IDs (if used), commands, outputs, failures and adaptation effort. Never include API keys or private documents.

For a new corpus, state its rights and origin, define task questions and expected evidence independently, freeze them before testing, and distinguish development from genuinely unseen evaluation. Equivalent unit handling, source revisions and document visibility must remain explicit.

Use imperative scoped commits (for example `fix: preserve unreplaced operator evidence`). Pull requests should describe the concrete behavior change and relevant tests; add screenshots for interface changes. Please label author-side tests, automated mocks, actual live calls and genuine external replication accurately.

A useful independent report says what was actually downloaded, read, run or adapted. A code review is not execution; execution is not real business adoption. Adoption may be reported only by the party who actually used the software, with its permission. No endorsements or successful outcomes are required to contribute.

Feedback can use GitHub Issues with the reproduction template. Do not include applicant case documents or legal conclusions in technical bug reports.
