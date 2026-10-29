"""Evaluate exact EIA snapshot fields; labels derive from raw API rows."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.engine import review
from src.agents import normalize
from src.protocol import digest

def main():
    raw=json.loads((ROOT/'examples/public_sources/eia_state_profiles_2024.json').read_text())
    docs=json.loads((ROOT/'examples/corpora/eia-public.json').read_text())
    expected={f"EIA-{x['stateID']}-{x['period']}":x for x in raw['response']['data']}
    checks=[('generation_capacity','net summer generating capacity?','net-summer-capacity','MW'),('generation','net generation?','net-generation','MWh'),('retail_price','average retail price?','average-retail-price','cents/kWh'),('investment','investment?',None,None)]
    runs=[]
    for d in docs:
        for field,question,column,unit in checks:
            for mode in ('baseline','retrieval_all','checked'):
                output=review([d],question,mode=mode)
                value=normalize(field,f"{expected[d['id']][column]} {unit}") if column else None
                ok=output['status']==('supported' if column else 'insufficient') and (value in output['answer'] if column else not output['citations'])
                runs.append({'id':d['id']+'-'+field,'mode':mode,'pass':ok,'expected_value':value,'result':output})
    metrics={m:{'passed':sum(x['pass'] for x in runs if x['mode']==m),'total':sum(x['mode']==m for x in runs)} for m in ('baseline','retrieval_all','checked')}
    report={'generated_at':datetime.now(timezone.utc).isoformat(),'source_manifest':'examples/public_sources/manifest.json','corpus_sha256':digest(docs),'metrics':metrics,'limitations':'Three states, one year, direct field adapters and raw-row reference labels. This measures adapter/extraction consistency, not broad reasoning or held-out model performance.','runs':runs}
    (ROOT/'results/public-data-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(metrics))
    return int(any(not x['pass'] for x in runs))
if __name__=='__main__':raise SystemExit(main())
