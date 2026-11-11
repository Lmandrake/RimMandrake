"""Extract model result unchanged, retaining complete CLI JSON and byte receipts."""
import hashlib
import json
from pathlib import Path
import sys
import time

here=Path(__file__).resolve().parent
mode=sys.argv[1]
assert mode in ('broaden','judge','judge_final')
raw=here/(mode+'_raw.json')
response=json.loads(raw.read_text())
assert response.get('type')=='result' and not response.get('is_error'), response
result=response['result']
assert isinstance(result,str) and result.strip()
target=here/('broaden_report.md') if mode=='broaden' else here.parent/'JUDGE.md'
if mode == 'judge_final':
    assert target.read_bytes() == (here / 'JUDGE_first.md').read_bytes(), 'Preserve the first verdict before replacement'
else:
    assert not target.exists()
target.write_bytes(result.encode())
receipt=dict(time=time.time(),raw_path=str(raw),raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),extracted_path=str(target),extracted_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),unchanged_result=target.read_bytes()==result.encode(),model_usage=response.get('modelUsage'),last_line=result.strip().splitlines()[-1])
(here/(mode+'_extraction.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
