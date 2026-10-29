"""Bounded multi-role evidence review orchestration."""
import time
from .agents import PlannerAgent, RetrieverAgent, ExtractorAgent, ReconcilerAgent, EvidenceVerifierAgent, FIELDS
from .corpus import validate
from .protocol import Journal, VERSION, digest
from .model import ModelClient

def review(documents, question, role="public", mode="checked", provider="offline", project=None):
    validate(documents)
    if not isinstance(question, str) or not question.strip() or len(question) > 2000:
        raise ValueError("Question must be 1–2000 characters")
    if role not in ("public", "internal") or mode not in ("baseline", "retrieval_all", "checked") or provider not in ("offline", "llm"):
        raise ValueError("Unknown role, mode or provider")
    start = time.perf_counter()
    client = ModelClient() if provider == "llm" else None
    visible = [d for d in documents if d.get("access", "public") in ("public", role)]
    projects = sorted({d.get("project", "demo") for d in visible})
    if project is None and len(projects) > 1:
        raise ValueError("Choose one project before comparing facts across documents")
    project = project or (projects[0] if projects else "demo")
    visible = [d for d in visible if d.get("project", "demo") == project]
    journal = Journal()
    journal.emit("user", "planner", "REQUEST", {"question": question, "role": role, "project": project})
    plan = PlannerAgent().run(question)
    journal.emit("planner", "retriever", "HANDOFF", plan)
    retrieved = RetrieverAgent().run(visible, plan["fields"])
    journal.emit("retriever", "extractor", "HANDOFF", {"source_ids": [x["document"]["id"] for x in retrieved], "requested_fields": plan["fields"]})
    claims = ExtractorAgent().run(retrieved)
    journal.emit("extractor", "reconciler", "HANDOFF", {"claims": claims})
    decisions = ReconcilerAgent().run(claims, visible, plan["fields"], mode)
    journal.emit("reconciler", "verifier", "HANDOFF", {"decisions": decisions, "mode": mode})
    verification = EvidenceVerifierAgent().run(decisions, visible)
    journal.emit("verifier", "reporter", "RESPONSE", verification)
    statuses = {x["status"] for x in decisions}
    status = "conflict" if "conflict" in statuses else "partial" if "supported" in statuses and "insufficient" in statuses else "supported" if statuses == {"supported"} else "insufficient"
    if not verification["passed"]:
        status = "needs_review"
    answer = "\n".join(x["field"] + ": " + (" / ".join(x["values"]) if x["values"] else "资料中未找到") + ("（冲突，需人工确认）" if x["status"] == "conflict" else "") for x in decisions) or "未识别到支持的资料字段；请人工检查或改写问题。"
    citations = [c for x in decisions for c in x["citations"]]
    output = {"question": question, "project": project, "status": status, "answer": answer, "citations": citations,
              "decisions": decisions, "verification": verification, "mode": mode, "provider": provider,
              "field": plan["fields"][0] if len(plan["fields"]) == 1 else None,
              "corpus_sha256": digest(visible), "version": VERSION, "run_id": journal.run_id}
    if client:
        output["model_collaboration"] = client.collaborate(question, decisions, journal)
        output["model_draft"] = output["model_collaboration"]["reporter"]["note"]
    journal.emit("reporter", "human", "RESPONSE", {"status": status, "answer": answer, "requires_human": status != "supported", "result_hash": digest(output)})
    output.update({"trace": journal.events, "trace_valid": Journal.verify(journal.events), "elapsed_ms": round((time.perf_counter() - start) * 1000, 3)})
    return output

def summary(documents, role="public", project=None):
    return {field: review(documents, field, role, project=project) for field in FIELDS}
