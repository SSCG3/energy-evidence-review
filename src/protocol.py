"""Structured, hash-linked message journal for an inspectable local execution."""
import hashlib
import json
import uuid
from datetime import datetime, timezone
VERSION = "0.2.0"
def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
class Journal:
    def __init__(self):
        self.run_id = str(uuid.uuid4())
        self.events = []
    def emit(self, sender, receiver, kind, content):
        entry = {"id": len(self.events) + 1, "run_id": self.run_id,
                 "timestamp": datetime.now(timezone.utc).isoformat(), "sender": sender,
                 "receiver": receiver, "type": kind, "content": content,
                 "previous_hash": self.events[-1]["hash"] if self.events else "0" * 64}
        entry["hash"] = digest(entry)
        self.events.append(entry)
        return entry
    @staticmethod
    def verify(events):
        previous = "0" * 64
        for index, entry in enumerate(events, 1):
            payload = {k: v for k, v in entry.items() if k != "hash"}
            if entry.get("id") != index or entry.get("previous_hash") != previous or digest(payload) != entry.get("hash"):
                return False
            previous = entry["hash"]
        return True
