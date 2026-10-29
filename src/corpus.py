"""Corpus validation and text/PDF adapters. No documents persist on the server."""
import base64
import io

def validate(documents):
    if not isinstance(documents, list) or len(documents) > 100:
        raise ValueError("Expected an array of at most 100 documents")
    ids = set()
    total = 0
    for document in documents:
        if not isinstance(document, dict) or not all(isinstance(document.get(k), str) and document[k] for k in ("id", "title", "text")):
            raise ValueError("Each document needs nonempty string id, title and text")
        if document["id"] in ids:
            raise ValueError("Duplicate document ID")
        ids.add(document["id"])
        if document.get("access", "public") not in ("public", "internal"):
            raise ValueError("Unknown document access label")
        if not isinstance(document.get("project", "demo"), str):
            raise ValueError("Project must be a string")
        if document.get("supersedes") is not None and not isinstance(document["supersedes"], str):
            raise ValueError("supersedes must be a document ID")
        total += len(document["text"])
    if total > 400000:
        raise ValueError("Corpus exceeds 400,000 characters")
    mapping = {d["id"]: d for d in documents}
    for document in documents:
        seen = {document["id"]}
        current = document
        while current.get("supersedes"):
            target = current["supersedes"]
            if target in seen:
                raise ValueError("Cyclic supersession metadata")
            seen.add(target)
            if target not in mapping:
                raise ValueError("supersedes points to an absent document")
            older = mapping[target]
            if older.get("project", "demo") != document.get("project", "demo"):
                raise ValueError("Supersession cannot cross projects")
            current = older
    return documents

def ingest(filename, encoded):
    if not isinstance(filename, str) or not isinstance(encoded, str):
        raise ValueError("Filename and base64 content required")
    if len(encoded) > 2800000:
        raise ValueError("Upload exceeds 2 MB")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise ValueError("Invalid base64 content") from exc
    if filename.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError("PDF import requires pip install -r requirements-pdf.txt") from exc
        try:
            reader = PdfReader(io.BytesIO(raw))
            if len(reader.pages) > 50:
                raise ValueError("PDF exceeds 50-page prototype limit")
            text = "\n".join("[PDF page %d]\n%s" % (i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages))
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError("Unable to parse PDF; use a text PDF or UTF-8 text") from exc
        if len(text.strip()) < 30:
            raise ValueError("No usable text layer; OCR is not implemented")
    elif filename.lower().endswith((".txt", ".md")):
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("Text must use UTF-8") from exc
    else:
        raise ValueError("Supported uploads: PDF, UTF-8 TXT and MD")
    if len(text) > 200000:
        raise ValueError("Extracted text exceeds 200,000 characters")
    return {"title": filename, "text": text, "notice": "Review extraction quality; factual extraction supports documented field patterns only."}
