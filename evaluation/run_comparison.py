"""Author-side fixture evaluation. Expected labels never enter engine input."""
import csv
import hashlib
import json
import platform
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.engine import review
from src.protocol import Journal, VERSION, digest

def main():
    suite = ROOT / "evaluation/cases.json"
    cases = json.loads(suite.read_text())
    runs = []
    modes = ("baseline", "retrieval_all", "checked")
    for case in cases:
        for mode in modes:
            output = review(case["documents"], case["question"], case.get("role", "public"), mode)
            cited = {c["source"] for c in output["citations"]}
            checks = {"status_ok": output["status"] == case["expected_status"],
                      "evidence_ok": set(case["expected_sources"]).issubset(cited),
                      "value_ok": all(value in output["answer"] for value in case["expected_values"]),
                      "trace_ok": Journal.verify(output["trace"])}
            runs.append({"id": case["id"], "category": case["category"], "mode": mode,
                         **checks, "pass": all(checks.values()), "result": output})
    metrics = {mode: {"passed": sum(x["pass"] for x in runs if x["mode"] == mode), "total": len(cases)} for mode in modes}
    per_category = {category: {mode: {"passed": sum(x["pass"] for x in runs if x["mode"] == mode and x["category"] == category),
                                     "total": sum(x["mode"] == mode and x["category"] == category for x in runs)} for mode in modes}
                    for category in sorted({x["category"] for x in cases})}
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / "src").glob("*.py"))}
    report = {"version": VERSION, "generated_at": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
              "provider": "offline", "suite_sha256": hashlib.sha256(suite.read_bytes()).hexdigest(), "source_sha256": source_hashes,
              "limitations": "Synthetic development fixtures; four variations per category; not blinded, held out, independent or production evidence. No live LLM calls.",
              "metrics": metrics, "per_category": per_category, "runs": runs}
    dest = ROOT / "results" / ("v" + VERSION)
    dest.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(report, ensure_ascii=False, indent=2)
    (dest / "comparison.json").write_text(encoded)
    (ROOT / "results/comparison.json").write_text(encoded)
    keys = ["id", "category", "mode", "status_ok", "evidence_ok", "value_ok", "trace_ok", "pass"]
    with (dest / "scores.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows({key: row[key] for key in keys} for row in runs)
    print(json.dumps(metrics))
    if metrics["checked"]["passed"] != len(cases):
        print("Checked failures:", [x["id"] for x in runs if x["mode"] == "checked" and not x["pass"]])
        return 1
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
