"""Generate a fixed ten-page English report from current, actual artifacts."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
try:
    import pymupdf as fitz
except ImportError:
    raise SystemExit('Install requirements-report.txt to generate the PDF')

def build():
    syn = json.loads((ROOT/'results/comparison.json').read_text())
    pub = json.loads((ROOT/'results/public-data-comparison.json').read_text())
    live = json.loads((ROOT/'results/model-validation.json').read_text())
    manifest = json.loads((ROOT/'examples/public_sources/manifest.json').read_text())
    usages = [u for x in live['runs'] if x.get('success') for u in x['result']['model_collaboration']['usage']]
    total_tokens = sum(u.get('usage',{}).get('total_tokens',0) for u in usages)
    cost = sum(u.get('usage',{}).get('cost',0) for u in usages)
    counts = '; '.join(f"{m}: {v['passed']}/{v['total']}" for m,v in syn['metrics'].items())
    dataset = json.loads((ROOT/'examples/public_sources/eia_state_profiles_2024.json').read_text())['response']['data']
    rows = '\n'.join(f"{x['stateDescription']}: generating capacity {x['net-summer-capacity']} MW; net generation {x['net-generation']} MWh; average retail price {x['average-retail-price']} cents/kWh." for x in dataset)
    pages = [
('Project identity and executive overview', '''Energy Evidence Review is an independently implemented reference workbench for inspectable energy-document review. Its repository combines executable software, attributed public data, synthetic tests, actual output records and a reproducible report. The project owner and director is Quanxi Zhou (GitHub: SSCG3). Code and document preparation are AI-assisted; this disclosure is part of the provenance record rather than a statement of independent peer review.

The operational question is deliberately narrow: can a reviewer trace an extracted energy fact to a source, distinguish an explicit revision from an unresolved disagreement, and see when available information does not answer a question? The system retains a structured evidence record and a separate narrative surface. It does not operate infrastructure, certify engineering decisions or independently establish the truth of a source document.

The software supplies deterministic role agents and an optional three-exchange model workflow. The former provides repeatable source checks without network calls. The latter uses DeepSeek for analysis and reporting and GLM for review. Each stage has a defined input/output contract, and a human remains responsible for accepting a model note or resolving a source conflict.

The included materials comprise two synthetic energy scenarios and a genuine EIA electricity-data slice for three U.S. states in 2024. Tests are author-side development fixtures, not an independent benchmark. This report states the actual strengths and limitations so another engineer can reproduce or challenge the results.

Artifact identity: version 0.2.0; repository https://github.com/SSCG3/energy-evidence-review . Exact code, data and run identities are retained through Git commits, source hashes, run IDs and file checksums. The report does not assert external adoption, employer endorsement, production readiness or any immigration adjudication outcome.'''),
('Problem definition and U.S. energy context', '''Energy and industrial knowledge work frequently involves multiple technical records, revisions, differing unit conventions and people with different information access. A plausible sentence is not sufficient for review: the reader must know which source supports it, which project and period it describes, and whether another source disagrees. Document assistance should expose these questions instead of silently choosing a convenient value.

The public U.S. example uses EIA State Electricity Profiles, Table 1. Its fields are state-level net summer generating capacity, net generation and average retail electricity price. These quantities describe different concepts and have different units. Generating capacity in MW must not be mislabeled as battery energy capacity in MWh. California, New York and Texas are three separate evidence scopes; differences between their values are not contradictions about one project.

The synthetic storage example asks about capacity and power across two documents. Capacity values disagree, while power values use equivalent MW and kW expressions. A useful result exposes the unresolved capacity conflict and recognizes equivalent power quantities. Another question asks for an investment value available only in a simulated internal document, allowing the access-filter behavior to be checked without real confidential data.

This is an informational and administrative workflow. It is potentially adaptable to public technical briefs, source comparison and evidence-linked summaries. It is not a control-system safety function, a market forecast or an engineering certification. Any operational deployment would require independently specified domain acceptance criteria and security controls.

NIST AI risk-management publications and DOE energy-AI reports supply relevant background for source provenance and contextual evaluation. They neither endorse this project nor prove its eventual impact. Here, the concrete U.S. relationship is inspectable through the official EIA data adapter and documented transfer conditions, rather than inferred from the general importance of artificial intelligence.'''),
('Multi-role architecture and communication', '''The coordinator implements a sequential workflow with six bounded responsibilities. The Planner identifies supported fields from a question and records the chosen project. The Retriever works on visible sources only. The Extractor attaches exact spans and line locations to recognized facts. The Reconciler applies unit normalization and explicit replacement metadata. The Verifier checks quoted spans against source text. The Reporter presents per-field results and human-review requirements.

Responsibilities are reflected in separate Python classes and modules. The reporter's structured output is assembled by the coordinator; it is not represented as a hidden independent LLM. Offline roles use deterministic logic. The value of this decomposition is inspectability and change isolation; it is not evidence that multiple roles must outperform an equivalently programmed single routine.

Agents communicate through JSON records containing an ID, run ID, UTC timestamp, sender, receiver, message type and content. REQUEST starts work, HANDOFF transfers an intermediate result, and RESPONSE records a result or decision. Every event includes the preceding event hash and a hash of its own canonical payload. A verification function checks chain consistency. This makes a modified event detectable against its existing chain, but a party controlling the entire journal can recompute hashes; no immutable or independently timestamped audit claim is made.

When enabled, real model roles operate after the bounded evidence record exists. A DeepSeek analyst prepares evidence-linked claims, a GLM reviewer examines them against the same record, and a DeepSeek reporter prepares a human-review note using the evidence and objections. Separate prompts and model families are not equivalent to independent human expertise. Model text remains separate from authoritative structured fields and cannot silently replace them.

Only selected visible evidence is sent to the provider. The application exposes model failures rather than substituting a successful offline run. Runtime credentials stay in the server environment; no keys are included in the repository, journal or report. The program accepts DeepSeek and GLM model identifiers only, consistent with the project owner's specified model constraint.'''),
('Data assets, public sources and provenance', f'''The EIA snapshot was retrieved directly from the public API and is archived as original response bytes plus a selected CSV table. Its publisher is the U.S. Energy Information Administration. Dataset: State Electricity Profiles / Table 1 Summary, sourced upstream from Forms EIA-860, EIA-861 and EIA-923. Period: 2024. Selected states: CA, NY and TX. This is a small, disclosed selection for a reference demonstration.

Recorded source values:
{rows}

The transformation into review documents preserves the API values and explicitly states units and scope. The narrative adapter is project-generated; it is not an EIA-authored report. Each adapted document retains an official source URL and a distinct project identifier. No contradictory values are invented inside these official records to improve a test result. Synthetic conflict fixtures are stored and labeled separately.

Manifest retrieval timestamp: {manifest['retrieved_at']} . Raw SHA256: {manifest['raw_sha256']} . The source URL, selected fields, row count, retrieval script and reuse reference are recorded in examples/public_sources/manifest.json. Running scripts/fetch_public_data.py refreshes the snapshot and changes its hashes; published results should remain associated with their original snapshot.

A second data family consists of synthetic storage and solar-plus-storage documents created for development. Their organization names, internal budgets and technical records are fictional. They permit targeted access, revision and conflict cases without transferring employer information. User imports remain in browser/server memory; the application does not save uploaded files.

PDF import uses the optional pypdf dependency to extract a text layer and adds page markers. Scanned documents without usable text are rejected. Importing a PDF does not guarantee that an arbitrary fact pattern will be recognized. A project-generated EIA PDF adapter is included so another user can test text import against known source material.'''),
('Evidence algorithms and decision boundaries', '''Eight field families are currently recognized: storage energy capacity, rated power, duration, investment, operator, net summer generating capacity, net generation and retail price. English and Chinese patterns are explicit in src/agents.py. The implementation extracts recognizable statements such as Storage capacity: 100 MWh or an equivalent Chinese expression. It does not perform unrestricted semantic extraction, infer implicit facts or understand every document layout.

Numeric units normalize using Decimal arithmetic. Energy values normalize to MWh and power values to MW. Time converts minutes to hours. Currency values preserve their currency; the system does not infer exchange rates. Unit normalization is a deterministic representation change, not evidence that differently scoped statements are comparable. Selecting one project is required when several projects are present.

An explicit supersedes relation supplies revision precedence. Cycles, missing targets and cross-project replacement relations are rejected. Replacement operates per asserted field: a new capacity statement does not erase an older operator statement if the newer source does not restate that field. A hidden revision cannot replace a public claim within the public view. Timestamps alone do not establish authority or applicability.

After visible replacement handling, no recognized claim yields insufficient information; one distinct normalized value yields supported; multiple values yield conflict and human review. Compound questions can yield partial information. Supported means that the bounded check found supporting source patterns and agreement, not that the external world has been independently verified. Exact-source verification ensures retained quotes match original spans. A real semantic error in a source, ambiguous entity assignment or misleading input metadata can still pass these checks.

Source paragraphs are treated as data. Deterministic agents do not execute document instructions. Model prompts also specify untrusted-document handling, but this has not established comprehensive prompt-injection resistance. The local UI's role switch simulates source visibility and is not authenticated identity. These constraints are part of the method, not undisclosed exceptions to a production-grade claim.'''),
('Evaluation design and reproduction protocol', '''The synthetic suite contains 40 development cases: four variations in each of ten categories. Categories cover directly answerable facts, missing facts, unresolved conflicts, explicit supersession, equivalent units, fields joined across documents, restricted missing facts, partial answers, hidden revisions and unsupported questions. Numeric variations are not treated as forty independent real deployments. Cases were authored while developing the implementation and are not a blinded or held-out set.

Three methods receive the same corpus, question and simulated role. The first-hit baseline uses the first recognized fact for each field. The all-source baseline retains all recognized facts and normalized units but does not apply explicit revision precedence. Coordinated review adds per-field replacement handling and retained source verification. These baselines isolate specific mechanisms; none is claimed to represent the strongest available commercial RAG system.

For every run, the evaluator checks expected status, required source IDs, expected normalized value strings and journal integrity. Reference labels are used only after engine execution and never included in engine input. Quote-span invariants and access behavior are tested separately. This automatic scoring is narrower than human semantic review and may miss an unsupported interpretation outside the specified checks.

Public-data testing is separate: twelve checks use three EIA states and four questions per state. Three ask for known fields, and one asks about an investment value absent from the selected snapshot. Expected values derive from the archived raw API rows rather than an independently curated gold standard. This measures adapter and extraction consistency; it does not establish broad reasoning accuracy or generalization.

Commands: python3 -m unittest discover -s tests -v ; python3 evaluation/run_comparison.py ; python3 evaluation/run_public_data.py . The optional live-model program is scripts/validate_models.py. It runs three scenarios and up to nine completions, storing actual model IDs, response IDs, usage and failures. A protocol mock inside unit tests is explicitly distinguished from live-provider output. Changes to the engine or corpus require new results tied to new hashes.'''),
('Observed results and model-role observations', f'''Synthetic results from the recorded run are {counts}. All-source retrieval improves on first-hit extraction for documented conflicts and evidence aggregation; coordinated review additionally handles explicit revisions. The final scores reflect the predefined fixture checks. They are not population accuracy estimates, business-impact measurements or proof that multi-agent orchestration itself caused all improvements.

The public EIA checks return 12/12 for each of the three methods. This equal result matters: simple direct-field data do not demonstrate an advantage for the more elaborate workflow. The project retains that outcome rather than manufacturing conflicting official records or hiding a baseline that performs equally well. Per-question results, source hashes, corpus identity, Python version and timestamps are included in the JSON records.

Live domestic-model validation completed {live['successful_scenarios']}/{len(live['runs'])} scenarios, with {len(usages)} role completions. Requested model families were DeepSeek for analyst/reporter and GLM for reviewer. Recorded usage across those scenario calls totals {total_tokens} tokens; provider-reported cost totals USD {cost:.8f}. This is the provider's recorded charge field, not an independently reconciled invoice or a future cost guarantee. Additional development probes or browser runs are outside that nine-call total.

The conflict scenario produced a revise verdict from GLM. The raw review also contains debatable criticism, illustrating that a review role can itself be imperfect. The official-data and missing-data scenarios produced approve verdicts in this recorded run. Neither approve nor revise is used as an automatic correctness label; the structured evidence and model outputs remain available for inspection. Scenario completion indicates that the API exchange and JSON protocol succeeded, not that every sentence is factually or semantically correct.

All three analyst outputs passed the narrow check that cited source IDs belonged to supplied evidence. That check does not prove entailment. The project makes no claim of independent expert validation, verified national impact or real production adoption. A stronger assessment would use a pre-frozen unseen corpus, richer baselines, repeated stochastic runs and domain experts grading claim support.'''),
('Book-method mapping and Jinshi-informed elements', '''The methodological source is the applicant-supplied manuscript of Multi-Agent Collaboration: Engineering Practice and System Construction Based on Large Language Models. The manuscript was inspected selectively for implementation-relevant sections; it was not subjected to a complete technical audit. Its pagination and chapter wording may differ from the published edition. No manuscript PDF is redistributed in the public repository.

Section 5.1.1 motivates mapping tasks to agent responsibilities. Section 5.1.2 discusses sequential, parallel, hierarchical and negotiation patterns; this prototype uses a bounded sequential chain rather than claiming all four. Section 5.2.2 motivates structured messages with routing, types and context. Sections 5.4.1 and 5.4.4 inform explicit treatment of uncertainty and human intervention. Shared-context/audit discussion motivates retained execution records, while the report expressly limits their integrity guarantees.

The Jinshi relationship is conceptual engineering background: document-based knowledge work, permission boundaries, traceable evidence, coordinated review and technical handover. These elements are visible in the reference design. They are not a transfer of the employer system, its proprietary retrieval stack, confidential content or production benchmarks. No company logo, employer credential, employee record or internal business document is bundled.

Read-only inspection of the earlier project was limited to package metadata, frontend module routes and document-checker interface types, a backend entrypoint and a short API/progress-management excerpt. New implementation code and styling were generated independently under the user's direction with AI assistance. This record must not be repackaged as wholly manual authorship, as a company-authorized open-source release or as independently established ownership clearance.

The same public project can support technical inspection of a proposed method and an author's ability to organize public work. That does not make the repository itself proof of widespread acclaim or third-party influence. Book publication, employer responsibility and this newly developed public artifact remain distinct evidence categories. Public technical readers should evaluate the actual code, data and results; application-specific legal argument belongs in a separate private evidence index.'''),
('Local deployment, UI verification and screenshots', '''The core server and evaluation tools run on Python 3.10 or later with standard-library dependencies. Optional PDF support installs pypdf. The server binds to 127.0.0.1 on port 8765. Open that exact URL in a browser. Its request token and origin check protect local write endpoints from simple cross-site misuse; these measures do not provide enterprise authentication, tenant isolation or a production security review.

The workbench lets a user select one corpus, ask a question, inspect per-source quotes, generate a review brief, view role handoffs and export a JSON trace. It imports UTF-8 text/Markdown and PDF text layers. JSON corpus editing makes project, access and replacement metadata explicit. The source screen distinguishes the official EIA data from synthetic examples; evaluation screens read actual result files rather than hardcoded scores.

Browser verification uses a dedicated window in the existing noVNC desktop. Screenshots are captured from the actual display with the real address bar, not a drawn URL overlay. The capture script records navigation and interaction outcomes. Image files are illustrations of local execution, not evidence of public hosting at a localhost URL. The GitHub repository is the public distribution address; 127.0.0.1 refers to the machine running the application.

The screenshot collection covers the review workbench, structured agent journal, synthetic comparison, EIA source provenance, public-data result checks, model-role behavior and method mapping. Images do not replace the executable code or raw output records. If a screenshot and a later version disagree, use the release's exact commit, report, data snapshot and capture record rather than mixing versions.

A reproduction report should identify the downloaded commit, environment, corpus version, commands, observed failures and adaptation effort. Reading code is not executing it; executing it is not deploying it in a real organization. External participants may report actual feedback through the repository's issue template without being asked to endorse a predetermined result.'''),
('Limitations, transfer conditions and future assessment', '''The current implementation is a constrained reference, not a comprehensive energy-domain reasoning system. It supports documented expressions for eight field families, exact-source offsets and explicit metadata. It can miss unseen phrasing, OCR failures, implied values and entity/scope ambiguities. Numeric equivalence does not resolve differing assumptions. A genuine disagreement requires human review; a more recent date alone is not a universal conflict-resolution rule.

Both synthetic and public tests are small, author-side development evaluations. The EIA adapter and its expected field labels are closely related transformations of the same raw data. The three live-model scenarios demonstrate real role exchanges but not statistical reliability, successful independent replication or resistance to all adversarial documents. Unit, HTTP and source-integrity checks verify important invariants; they cannot substitute for a domain acceptance study.

Transfer to a different organization requires source permissions, explicit project/period scope, extraction-quality review, locally meaningful questions, independent expected evidence and new tests. A production deployment additionally needs identity-based authorization, secret management, observability, incident handling and domain review. Only permitted nonconfidential artifacts should be shared. The public package's reusable layer is a transparent workflow, contracts and evaluation protocol, not employer content.

Future work can add unseen-document evaluation, more varied extraction methods, stronger retrieval baselines and independent claim-support judgments. Another team may test how much adaptation the architecture requires and whether source traceability or conflict handling actually improves its review task. Results should include failures, costs and time; neither positive outcomes nor a specific adoption count is assumed.

References: EIA State Electricity Profiles and API documentation; EIA Copyrights and Reuse guidance; NIST AI RMF 1.0 and Generative AI Profile; DOE AI for Energy report as contextual references; the applicant-supplied multi-agent manuscript for method mapping; OpenRouter chat-completions documentation for provider integration. Links and frozen source metadata are available in docs/references.md and examples/public_sources/manifest.json. This report establishes inspectable development artifacts and reported local observations, not governmental endorsement or an adjudication outcome.''')]
    md = ['# Energy Evidence Review — Technical Report', '', 'Version 0.2.0 · Project owner/director: Quanxi Zhou · AI-assisted implementation and documentation', '', 'Generated: ' + datetime.now(timezone.utc).isoformat(), '']
    pdf = fitz.open()
    for index, (title, body) in enumerate(pages, 1):
        md.extend([f'## Page {index}. {title}', '', body, '', '<!-- page break -->', ''])
        page = pdf.new_page(width=595.28, height=841.89)
        page.draw_rect(fitz.Rect(0,0,595.28,8), color=None, fill=(0,.42,.40))
        page.insert_text((46,35), 'ENERGY EVIDENCE REVIEW  /  TECHNICAL REPORT', fontsize=8, fontname='hebo', color=(.2,.38,.4))
        title_height = page.insert_textbox(fitz.Rect(46,54,548,115), f'{index:02d}  {title}', fontsize=18, fontname='hebo', color=(.08,.18,.23))
        if title_height < 0:
            raise RuntimeError('Title overflow')
        remaining = page.insert_textbox(fitz.Rect(46,122,548,763), body, fontsize=10.4, fontname='helv', lineheight=1.38, color=(.13,.20,.24))
        if remaining < 0:
            raise RuntimeError(f'Page {index} text overflow: {remaining}')
        # Add a substantive artifact figure in remaining space; never overlap body text.
        figure_y = max(570, 763 - remaining + 14)
        figure_h = 763 - figure_y
        if figure_h >= 90:
            page.draw_rect(fitz.Rect(46, figure_y, 548, 763), color=(.8,.86,.86), fill=(.96,.98,.97))
            def line(text, y, size=8.5):
                page.insert_text((58,y),text,fontsize=size,fontname='helv',color=(.12,.28,.3))
            if index == 1:
                line('ARTIFACTS AT A GLANCE',figure_y+18)
                for j,(label,value) in enumerate([('Synthetic cases','40 / 40 checked'),('Public-data checks','12 / 12 checked'),('Domestic model roles',f'{len(usages)} live completions')]):
                    x=58+j*160
                    page.insert_text((x,figure_y+48),value,fontsize=13,fontname='hebo',color=(0,.4,.36))
                    page.insert_text((x,figure_y+67),label,fontsize=8,color=(.3,.4,.43))
                line('Executable code + frozen source data + raw results + review journal',figure_y+90)
            elif index == 2:
                line('KEEP QUANTITIES AND SCOPES DISTINCT',figure_y+18)
                line('Storage energy capacity       MWh          Synthetic project documents',figure_y+42)
                line('State generating capacity     MW           Official EIA state-year record',figure_y+61)
                line('Net generation                MWh          A period total, not installed capacity',figure_y+80)
            elif index == 3:
                line('IMPLEMENTED ROLE CHAIN',figure_y+18)
                line('Planner -> Retriever -> Extractor -> Reconciler -> Verifier -> Reporter',figure_y+43,9)
                line('Optional: DeepSeek analyst -> GLM reviewer -> DeepSeek reporter',figure_y+65,9)
                line('Every handoff -> typed JSON + source context + hash-linked record',figure_y+87)
            elif index == 4:
                line('FROZEN EIA 2024 SNAPSHOT / RAW VALUES',figure_y+18)
                line('State          Summer capacity (MW)          Generation (MWh)          Price (cents/kWh)',figure_y+39,8)
                for j,row in enumerate(dataset):
                    line(f"{row['stateID']:<15}{row['net-summer-capacity']:<30}{row['net-generation']:<30}{row['average-retail-price']}",figure_y+59+j*18,8)
            elif index == 5:
                line('DECISION CONTRACT',figure_y+18)
                for j,t in enumerate(['No recognized visible fact -> insufficient', 'One distinct normalized value -> supported', 'Different unresolved values -> conflict / human review', 'Some requested fields missing -> partial']):line(t,figure_y+40+j*18)
            elif index == 6:
                line('EVALUATION LAYERS',figure_y+18)
                line('40 synthetic fixtures -> targeted mechanism checks',figure_y+42)
                line('12 public-data questions -> raw-row / adapter consistency',figure_y+62)
                line('3 live-model scenarios -> API protocol, role exchange, recorded outputs',figure_y+82)
            elif index == 7:
                line('OBSERVED SYNTHETIC CASE CHECKS',figure_y+18)
                for j,(mode,v) in enumerate(syn['metrics'].items()):
                    y=figure_y+36+j*27
                    line(mode,y+9,8)
                    page.draw_rect(fitz.Rect(160,y,160+250*v['passed']/v['total'],y+12),color=None,fill=(0,.45,.41))
                    page.insert_text((425,y+10),f"{v['passed']}/{v['total']}",fontsize=9)
            elif index == 8:
                line('PUBLIC METHOD -> CHECKABLE ARTIFACT',figure_y+18)
                line('Book role mapping -> separate agent classes',figure_y+42)
                line('Structured collaboration -> JSON handoffs with context',figure_y+62)
                line('Enterprise review experience -> public-data / synthetic reimplementation',figure_y+82)
            elif index == 9:
                image=ROOT/'docs/screenshots/01-workbench-addressbar.png'
                if image.exists():page.insert_image(fitz.Rect(48,figure_y+4,546,759),filename=str(image),keep_proportion=True)
                else:line('High-resolution browser screenshots: docs/screenshots/',figure_y+36)
            else:
                line('WHAT CAN BE INDEPENDENTLY CHECKED',figure_y+18)
                line('Source URL + raw hash | exact commit | per-case outputs | real model IDs',figure_y+42)
                line('Not established: operational gains, independent adoption or broad impact',figure_y+65)
                line('Next evidence: actual external reproduction, failures and adaptation effort',figure_y+87)
        page.draw_line((46,787),(548,787),color=(.75,.82,.82))
        page.insert_text((46,806),'Quanxi Zhou  |  v0.2.0  |  Author-side development and evaluation',fontsize=7.5,color=(.4,.47,.5))
        page.insert_text((508,806),f'{index} / 10',fontsize=8,color=(.2,.35,.38))
    (ROOT/'docs/technical-report.md').write_text('\n'.join(md))
    pdf.set_metadata({'title':'Energy Evidence Review: Technical Report','author':'Quanxi Zhou; AI-assisted preparation','subject':'Independent multi-role reference implementation, public data, evaluation and limitations'})
    pdf.save(str(ROOT/'docs/technical-report.pdf'),garbage=4,deflate=True)
    print('Report pages:',len(pdf),'English words:',sum(len(b.split()) for _,b in pages))
if __name__=='__main__':build()
