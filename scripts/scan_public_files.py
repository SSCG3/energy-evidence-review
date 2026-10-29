"""Minimal local prepublication check. Never prints matching secrets."""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATTERNS=[re.compile(rb'ghp_[A-Za-z0-9]{30,}'),re.compile(rb'sk-or-v1-[a-fA-F0-9]{64}')]
def main():
    findings=[]
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(x in path.parts for x in ('.git','__pycache__','.venv')):
            continue
        if path.name.startswith('.env') and path.name!='.env.example':
            findings.append(str(path.relative_to(ROOT))+': local environment file must not be published')
        data=path.read_bytes()
        if any(pattern.search(data) for pattern in PATTERNS):
            findings.append(str(path.relative_to(ROOT))+': credential-shaped content detected')
    for finding in findings:print(finding)
    print('Public-file credential scan:', 'PASS' if not findings else 'FAIL')
    return bool(findings)
if __name__=='__main__':raise SystemExit(main())
