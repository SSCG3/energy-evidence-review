# Book methods and Jinshi engineering context

## Book mapping

Source: the applicant-supplied manuscript of 《多智能体协同：基于大语言模型的工程实践与系统构建》. Manuscript pagination may differ from the published edition. Relevant manuscript sections were inspected; no whole-manuscript technical validation is claimed and the manuscript is not redistributed.

| Section | Method | Independent implementation |
|---|---|---|
| 5.1.1 | Map responsibilities to agent roles | Planner, retriever, extractor, reconciler, verifier, reporter |
| 5.1.2, manuscript pp.108–110 | Sequential collaboration with explicit handoffs | Coordinator and bounded role calls |
| 5.2.2, manuscript pp.117–118 | Structured messages with routing and types | JSON REQUEST / HANDOFF / RESPONSE events |
| 5.4.1 and 5.4.4 | Hallucination concerns and human intervention | Explicit missing/conflict outcomes; separately labeled model notes |
| 5.3 discussion of shared context/audit | Retained context and process records | Visible-source trace and hash-linked local journal |

This is a selective application of public engineering ideas, not a claim to implement every book mechanism. Book authorship/publication is established separately from this repository. The book's publication does not establish this software's effectiveness.

## Jinshi-informed elements

| Publicly describable engineering pattern | Public reference implementation | Boundary |
|---|---|---|
| Enterprise knowledge sources | Replaceable public/synthetic document corpus | No Jinshi data or interfaces |
| RAG-like source grounding | Field-aware source retrieval and citations | Not a reproduction of Jinshi retrieval quality |
| Team responsibility boundaries | Explicit agents and message contracts | No corporate organization chart copied |
| Permission-aware delivery | Filter visible sources before processing | Role simulation, not corporate authentication |
| Quality review and escalation | Conflict/missing flags, human disposition | No production acceptance claim |
| Technical handover and inspection | Reproducible tests, report, code and trace | No transfer of employer deliverables |

Read-only structural inspection was limited to the source project's package metadata, frontend module routes and document-checker interface types, backend entrypoint and a short API/progress-management excerpt. No source code, styles, icons, credentials, internal documents, database contents or manuscript PDF were copied into this repository. This is a newly AI-assisted reference implementation under the user's direction. The project does not establish employer approval or ownership clearance; no such clearance document is asserted to exist.
