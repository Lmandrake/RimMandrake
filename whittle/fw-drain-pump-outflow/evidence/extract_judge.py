"""Extract the exact CLI result string without editing it; preserve raw JSON and hashes."""
from pathlib import Path
import json,hashlib,time,sys
here=Path(__file__).resolve().parent
mode=sys.argv[1];assert mode in ('judge','judge_final')
raw=here/(mode+'_raw.json');data=json.loads(raw.read_bytes());assert not data.get('is_error') and isinstance(data.get('result'),str),data
payload=data['result'].encode('utf-8');target=here.parent/'JUDGE.md';assert not target.exists(),'Preserve earlier judge before a new final extraction'
target.write_bytes(payload)
r=dict(time=time.time(),raw_path=str(raw),raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),extracted_path=str(target),result_utf8_sha256=hashlib.sha256(payload).hexdigest(),extracted_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),exact_result_unchanged=target.read_bytes()==payload,subtype=data.get('subtype'),is_error=data.get('is_error'),session_id=data.get('session_id'),last_line=data['result'].splitlines()[-1])
(here/(mode+'_extraction.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));print(data['result'])
