import base64
import copy
import os
import unittest
from unittest.mock import patch
from src.engine import review, summary
from src.agents import EvidenceVerifierAgent
from src.corpus import validate, ingest
from src.protocol import Journal

def doc(id, text, **extra):
    return {"id": id, "title": id, "text": text, **extra}

class ReviewTests(unittest.TestCase):
    def test_conflict_keeps_both_sources(self):
        r = review([doc("a", "容量为100 MWh。"), doc("b", "Storage capacity: 120 MWh.")], "容量？")
        self.assertEqual(r["status"], "conflict")
        self.assertEqual({x["source"] for x in r["citations"]}, {"a", "b"})
    def test_equivalent_units_agree(self):
        r = review([doc("a", "capacity = 100 MWh"), doc("b", "capacity = 100000 kWh")], "capacity?")
        self.assertEqual(r["status"], "supported")
    def test_currency_is_not_implicitly_converted(self):
        r = review([doc("a", "Investment: 10 USD"), doc("b", "Investment: 10 CNY")], "investment?")
        self.assertEqual(r["status"], "conflict")
    def test_compound_query_reports_missing(self):
        r = review([doc("a", "capacity = 100 MWh")], "capacity and investment?")
        self.assertEqual(r["status"], "partial")
    def test_unknown_field_abstains(self):
        self.assertEqual(review([doc("a", "capacity = 100 MWh")], "telephone?")["status"], "insufficient")
    def test_hidden_claim_never_enters_trace(self):
        docs = [doc("a", "capacity = 100 MWh"), doc("b", "capacity = 999 MWh", access="internal", supersedes="a")]
        r = review(docs, "capacity?")
        self.assertNotIn("capacity = 999 MWh", str(r))
        self.assertEqual(r["answer"], "capacity: 100 MWh")
    def test_visible_revision_of_hidden_source(self):
        docs = [doc("a", "capacity = 999 MWh", access="internal"), doc("b", "capacity = 100 MWh", supersedes="a")]
        self.assertEqual(review(docs, "capacity?")["status"], "supported")
    def test_revision_does_not_erase_unreplaced_field(self):
        docs = [doc("a", "Operator: Energy Team.\ncapacity = 100 MWh"), doc("b", "capacity = 120 MWh", supersedes="a")]
        self.assertEqual(review(docs, "operator?")["status"], "supported")
    def test_cycle_rejected(self):
        with self.assertRaises(ValueError):
            validate([doc("a", "x", supersedes="b"), doc("b", "x", supersedes="a")])
    def test_project_choice_required(self):
        with self.assertRaises(ValueError):
            review([doc("a", "capacity = 1 MWh", project="A"), doc("b", "capacity = 2 MWh", project="B")], "capacity?")
    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            validate([doc("a", "x"), doc("a", "y")])
    def test_trace_detects_tampering(self):
        r = review([doc("a", "capacity = 1 MWh")], "capacity?")
        self.assertTrue(Journal.verify(r["trace"]))
        damaged = copy.deepcopy(r["trace"])
        damaged[1]["content"]["fields"] = []
        self.assertFalse(Journal.verify(damaged))
    def test_verifier_rejects_altered_quote(self):
        docs = [doc("a", "capacity = 1 MWh")]
        r = review(docs, "capacity?")
        r["decisions"][0]["citations"][0]["quote"] = "capacity = 9 MWh"
        self.assertFalse(EvidenceVerifierAgent().run(r["decisions"], docs)["passed"])
    def test_missing_model_does_not_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                review([], "capacity?", provider="llm")
    def test_text_import(self):
        r = ingest("test.txt", base64.b64encode(b"capacity = 1 MWh").decode())
        self.assertEqual(r["text"], "capacity = 1 MWh")
    def test_summary_filters_access(self):
        r = summary([doc("a", "investment = 999 CNY", access="internal")])
        self.assertEqual(r["investment"]["citations"], [])
    def test_model_roles_execute_three_distinct_calls(self):
        # Protocol mock: this is not a live-model result.
        calls = []
        def answer(client, role, instructions, payload):
            calls.append(role)
            return {"claims": []} if role == "analyst" else {"verdict": "revise", "issues": ["test"]} if role == "reviewer" else {"note": "mock note"}
        with patch.dict(os.environ, {"MODEL_BASE_URL": "https://example.invalid/v1", "MODEL_API_KEY": "test-only", "MODEL_NAME": "deepseek/test-fixture", "MODEL_REVIEWER_NAME": "z-ai/test-fixture"}):
            with patch("src.model.ModelClient.ask", new=answer):
                r = review([doc("a", "capacity = 1 MWh")], "capacity?", provider="llm")
        self.assertEqual(calls, ["analyst", "reviewer", "reporter"])
        self.assertIn("model_collaboration", r)

if __name__ == "__main__":
    unittest.main()
