"""Bounded role agents. Offline agents use explicit rules, not hidden LLM calls."""
import re
from decimal import Decimal, InvalidOperation
FIELDS = {
    "generation_capacity": ("发电装机容量", "净夏季发电容量", "generating capacity", "net summer capacity", "generation_capacity"),
    "generation": ("发电量", "net generation", "generation"),
    "retail_price": ("零售电价", "average retail price", "retail_price"),
    "capacity": ("储能容量", "容量", "energy capacity", "storage capacity", "capacity"),
    "power": ("功率", "rated power", "power rating", "power"),
    "duration": ("时长", "持续时间", "discharge duration", "duration"),
    "investment": ("投资额", "投资", "investment", "budget"),
    "operator": ("运营方", "运营单位", "operator"),
}
PATTERNS = {
    "generation_capacity": r"(?:net summer generating capacity|net summer capacity|净夏季发电容量|发电装机容量)\s*(?:为|是|is|:|：|=)?\s*([\d,.]+\s*(?:GW|MW|kW))\b",
    "generation": r"(?:net generation|净发电量|发电量)\s*(?:为|是|is|:|：|=)?\s*([\d,.]+\s*(?:GWh|MWh|kWh))\b",
    "retail_price": r"(?:average retail price|零售电价)\s*(?:为|是|is|:|：|=)?\s*([\d,.]+\s*cents/kWh)",
    "capacity": r"(?:储能容量|容量|energy capacity|storage capacity|capacity)\s*(?:为|是|is|of|:|：|=)?\s*([\d,.]+\s*(?:GWh|MWh|kWh))\b",
    "power": r"(?:额定功率|功率|rated power|power rating|power)\s*(?:为|是|is|of|:|：|=)?\s*([\d,.]+\s*(?:GW|MW|kW))\b",
    "duration": r"(?:放电时长|时长|持续时间|discharge duration|duration)\s*(?:为|是|is|of|:|：|=)?\s*([\d,.]+\s*(?:hours?|hrs?|h|minutes?|min|小时|分钟))",
    "investment": r"(?:投资额|投资|investment|budget)\s*(?:为|是|is|of|:|：|=)?\s*([\d,.]+\s*(?:(?:million\s+)?(?:CNY|USD)|万元|亿元|元))",
    "operator": r"(?:运营单位|运营方|operator)\s*(?:为|是|is|:|：|=)\s*([^;；。\n]+)",
}

def normalize(field, value):
    if field == "operator":
        return value.strip().rstrip(".;；。 ").casefold()
    match = re.fullmatch(r"([\d,.]+)\s*(.*)", value.strip(), re.I)
    if not match:
        return value.strip().casefold()
    try:
        number = Decimal(match[1].replace(",", ""))
    except InvalidOperation:
        return value.strip().casefold()
    unit = match[2].lower().replace(" ", "")
    units = {
        "capacity": {"gwh": (1000, "MWh"), "mwh": (1, "MWh"), "kwh": (Decimal("0.001"), "MWh")},
        "power": {"gw": (1000, "MW"), "mw": (1, "MW"), "kw": (Decimal("0.001"), "MW")},
        "duration": {"h": (1, "h"), "hour": (1, "h"), "hours": (1, "h"), "hr": (1, "h"), "hrs": (1, "h"), "小时": (1, "h"), "min": (Decimal(1)/60, "h"), "minute": (Decimal(1)/60, "h"), "minutes": (Decimal(1)/60, "h"), "分钟": (Decimal(1)/60, "h")},
        "investment": {"cny": (1, "CNY"), "millioncny": (1000000, "CNY"), "元": (1, "CNY"), "万元": (10000, "CNY"), "亿元": (100000000, "CNY"), "usd": (1, "USD"), "millionusd": (1000000, "USD")},
    }
    unit_field = {"generation_capacity": "power", "generation": "capacity"}.get(field, field)
    factor, base = units.get(unit_field, {}).get(unit, (1, unit))
    return f"{format((number * Decimal(factor)).normalize(), 'f')} {base}"

class PlannerAgent:
    name = "planner"
    def run(self, question):
        fields = [key for key, names in FIELDS.items() if any(name in question.lower() for name in names)]
        if "generation_capacity" in fields:
            fields = [f for f in fields if f not in ("capacity", "generation") or (f == "generation" and "net generation" in question.lower())]
        # Generating capacity (MW) is not battery energy capacity (MWh).
        return {"question": question, "fields": fields, "requires_human": not fields,
                "strategy": "retrieve -> extract -> reconcile -> verify -> report"}

class RetrieverAgent:
    name = "retriever"
    def run(self, documents, fields):
        return [{"document": d, "fields": [f for f in fields if re.search(PATTERNS[f], d["text"], re.I)]}
                for d in documents if any(re.search(PATTERNS[f], d["text"], re.I) for f in fields)]

class ExtractorAgent:
    name = "extractor"
    def run(self, retrieved):
        claims = []
        for item in retrieved:
            doc = item["document"]
            for field in item["fields"]:
                for match in re.finditer(PATTERNS[field], doc["text"], re.I):
                    a, b = match.span(1)
                    line = doc["text"].count("\n", 0, a) + 1
                    claims.append({"source": doc["id"], "title": doc["title"], "project": doc.get("project", "demo"),
                                   "field": field, "value": match[1].strip(), "normalized": normalize(field, match[1]),
                                   "quote": match[0], "start": match.start(), "end": match.end(), "line": line,
                                   "version": doc.get("version", 1), "source_url": doc.get("source_url"), "data_kind": doc.get("data_kind", "synthetic")})
        return claims

class ReconcilerAgent:
    name = "reconciler"
    def run(self, claims, documents, fields, mode):
        mapping = {d["id"]: d for d in documents}
        decisions = []
        for field in fields:
            hits = [c for c in claims if c["field"] == field]
            if mode == "checked":
                # Only a visible replacement that actually asserts this field can supersede it.
                superseded = set()
                for c in hits:
                    current = mapping[c["source"]]
                    while current.get("supersedes"):
                        superseded.add(current["supersedes"])
                        current = mapping.get(current["supersedes"])
                        if current is None:
                            break
                hits = [c for c in hits if c["source"] not in superseded]
            if mode == "baseline":
                hits = hits[:1]
            values = {c["normalized"] for c in hits}
            status = "insufficient" if not hits else "conflict" if len(values) > 1 else "supported"
            decisions.append({"field": field, "status": status, "values": sorted(values), "citations": hits,
                              "reason": "No visible supporting claim" if not hits else "Disagreement needs human review" if status == "conflict" else "Visible claims agree after explicit supersession and unit normalization"})
        return decisions

class EvidenceVerifierAgent:
    name = "verifier"
    def run(self, decisions, documents):
        mapping = {d["id"]: d for d in documents}
        findings = []
        for d in decisions:
            for c in d["citations"]:
                doc = mapping.get(c["source"])
                if not doc or doc["text"][c["start"]:c["end"]] != c["quote"]:
                    findings.append({"field": d["field"], "source": c["source"], "issue": "quote/source mismatch"})
        return {"passed": not findings, "findings": findings, "scope": "Exact source spans and rule-based field decisions, not general semantic truth"}
