"""Check code/data linkage of the included author-side observations."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    report=json.loads((ROOT/'results/comparison.json').read_text())
    failures=[]
    for name,expected in report['source_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            failures.append('Changed engine source: '+name)
    actual=hashlib.sha256((ROOT/'evaluation/cases.json').read_bytes()).hexdigest()
    if actual!=report['suite_sha256']:
        failures.append('Changed synthetic case suite')
    manifest=json.loads((ROOT/'examples/public_sources/manifest.json').read_text())
    actual=hashlib.sha256((ROOT/'examples/public_sources'/manifest['raw_file']).read_bytes()).hexdigest()
    if actual!=manifest['raw_sha256']:
        failures.append('Public data raw hash mismatch')
    live=json.loads((ROOT/'results/model-validation.json').read_text())
    for run in live['runs']:
        for entry in run.get('result',{}).get('model_collaboration',{}).get('usage',[]):
            if not entry['model'].startswith(('deepseek/','z-ai/')):
                failures.append('Unexpected model family in live validation')
    browser=json.loads((ROOT/'results/browser-validation.json').read_text())
    if not all(x['passed'] for x in browser['checks']):
        failures.append('Browser check failed')
    try:
        from pypdf import PdfReader
        if len(PdfReader(ROOT/'docs/technical-report.pdf').pages)!=10:
            failures.append('Report is not 10 pages')
    except ImportError:
        print('Optional PDF page-count check skipped: install requirements-pdf.txt')
    for failure in failures:print(failure)
    print('Artifact linkage:', 'PASS' if not failures else 'FAIL')
    return bool(failures)
if __name__=='__main__':raise SystemExit(main())
