"""Extract the returned CLI result verbatim; never synthesize a verdict."""
import hashlib,json,sys,time
from pathlib import Path
here=Path(__file__).resolve().parent
mode=sys.argv[1]
raw=here/(mode+'_raw.json')
data=json.loads(raw.read_text())
assert isinstance(data.get('result'),str) and data['result'].strip(), data
result=data['result']
out=here/'broaden_result.txt' if mode=='broaden' else here.parent/'JUDGE.md'
assert not out.exists()
out.write_text(result)
receipt=dict(time=time.time(),mode=mode,raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),result_sha256=hashlib.sha256(result.encode()).hexdigest(),output=str(out),extraction='result string unchanged; no added newline or verdict',subtype=data.get('subtype'),is_error=data.get('is_error'),usage=data.get('usage'),total_cost_usd=data.get('total_cost_usd'))
(here/(mode+'_extraction.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(result)
