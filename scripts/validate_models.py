"""Explicit, bounded live model validation (3 scenarios / 9 completions)."""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.engine import review
from src.protocol import digest

def main():
    synthetic = json.loads((ROOT / 'examples/corpora/storage-demo.json').read_text())
    # Use current sample definitions, not obsolete v0.1 fixture text.
    all_docs = json.loads((ROOT / 'examples/documents.json').read_text())
    synthetic = [d for d in all_docs if d.get('project') == 'storage-demo']
    public = json.loads((ROOT / 'examples/corpora/eia-public.json').read_text())
    cases = [('synthetic_conflict', synthetic, 'capacity and power?', 'storage-demo'),
             ('public_eia', public, 'net summer generating capacity and net generation and average retail price?', public[0]['project']),
             ('public_missing', public, 'investment?', public[0]['project'])]
    runs = []
    for name, docs, question, project in cases:
        try:
            result = review(docs, question, provider='llm', project=project)
            allowed = {c['source'] for c in result['citations']}
            claims = result['model_collaboration']['analyst'].get('claims', [])
            valid_ids = all(set(c.get('source_ids', [])).issubset(allowed) for c in claims if isinstance(c, dict))
            runs.append({'case': name, 'success': True, 'source_id_check': valid_ids, 'result': result})
            print(name, 'completed', result['status'], 'roles:', len(result['model_collaboration']['usage']), flush=True)
        except Exception as exc:
            runs.append({'case': name, 'success': False, 'error': str(exc)})
            print(name, 'failed', type(exc).__name__, flush=True)
    report = {'generated_at': datetime.now(timezone.utc).isoformat(), 'model': os.getenv('MODEL_NAME'),
              'scope': 'Live provider protocol and evidence-workflow demonstration; not statistical semantic accuracy or external review.',
              'max_planned_completions': 9, 'runs': runs, 'successful_scenarios': sum(x['success'] for x in runs),
              'engine_sources_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').glob('*.py'))}}
    (ROOT/'results/model-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    if report['successful_scenarios'] != 3:
        return 1
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
