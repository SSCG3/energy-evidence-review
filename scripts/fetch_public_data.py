"""Download a small, attributed EIA public-data slice. No private API key required."""
import csv
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def main():
    folder = ROOT / 'examples/public_sources'
    folder.mkdir(parents=True, exist_ok=True)
    query = [('api_key', 'DEMO_KEY'), ('frequency', 'annual'), ('start', '2024'), ('end', '2024'), ('length', '20')]
    query += [('data[]', x) for x in ('net-summer-capacity', 'net-generation', 'average-retail-price')]
    query += [('facets[stateID][]', x) for x in ('CA', 'TX', 'NY')]
    url = 'https://api.eia.gov/v2/electricity/state-electricity-profiles/summary/data/?' + urllib.parse.urlencode(query)
    req = urllib.request.Request(url, headers={'User-Agent': 'EnergyEvidenceReview/0.2.0 (public-data reproducibility)'})
    with urllib.request.urlopen(req, timeout=45) as response:
        raw = response.read()
    payload = json.loads(raw)
    rows = payload['response']['data']
    if not rows or any(k not in x for x in rows for k in ('net-summer-capacity', 'net-generation', 'average-retail-price')):
        raise RuntimeError('EIA response missing expected columns; preserve old snapshot')
    stamp = datetime.now(timezone.utc).isoformat()
    (folder / 'eia_state_profiles_2024.json').write_bytes(raw)
    with (folder / 'eia_state_profiles_2024.csv').open('w', newline='') as handle:
        columns = ['period', 'stateID', 'stateDescription', 'net-summer-capacity', 'net-generation', 'average-retail-price']
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows({k: row[k] for k in columns} for row in rows)
    documents = []
    for row in rows:
        state, year = row['stateID'], row['period']
        name = row['stateDescription']
        documents.append({'id': f'EIA-{state}-{year}', 'title': f'EIA {name} Electricity Profile {year}',
                          'project': f'eia-{state.lower()}-{year}', 'version': 1, 'access': 'public', 'data_kind': 'public_eia',
                          'source_url': url, 'text': f"EIA State Electricity Profiles, Table 1. State: {name}. Period: {year}.\nNet summer generating capacity: {row['net-summer-capacity']} MW.\nNet generation: {row['net-generation']} MWh.\nAverage retail price: {row['average-retail-price']} cents/kWh.\nScope: all sectors; state-level generating capacity, not battery storage capacity. Values transformed verbatim from the downloaded EIA API row."})
    (ROOT / 'examples/corpora/eia-public.json').write_text(json.dumps(documents, ensure_ascii=False, indent=2))
    manifest = {'publisher': 'U.S. Energy Information Administration', 'dataset': 'State Electricity Profiles / Table 1 Summary',
                'description': payload['response'].get('description'), 'source_url': url, 'retrieved_at': stamp,
                'raw_sha256': hashlib.sha256(raw).hexdigest(), 'raw_file': 'eia_state_profiles_2024.json',
                'period': '2024', 'states': [row['stateID'] for row in rows], 'row_count': len(rows),
                'reuse_reference': 'https://www.eia.gov/about/copyrights_reuse.php',
                'transformation': 'Select three fields and retain their exact API values; units and scope explicitly stated. Corpus is a local text adapter, not an EIA-authored narrative.',
                'limitations': 'Small public slice selected during development; not independently selected or held out. No operational or external-adoption claim.'}
    (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    base = json.loads((ROOT / 'examples/documents.json').read_text())
    base = [d for d in base if d.get('data_kind') != 'public_eia']
    (ROOT / 'examples/documents.json').write_text(json.dumps(base + documents, ensure_ascii=False, indent=2))
    print('Downloaded EIA rows:', len(rows), 'states:', manifest['states'], 'raw SHA256:', manifest['raw_sha256'])
if __name__ == '__main__':
    main()
