"""Recover only the exact independent Opus Write payload; preserve its denial and verdict."""
import hashlib
import json
from pathlib import Path
import time

here = Path(__file__).resolve().parent
target = here.parent / 'JUDGE.md'
raw_path = here / 'judge_raw.json'
raw = json.loads(raw_path.read_bytes())
call = json.loads((here / 'judge_call.json').read_text())
assert call.get('returncode') == 0 and not call.get('error')
writes = [(i, x) for i, x in enumerate(raw['permission_denials']) if x['tool_name'] == 'Write'
          and x['tool_input']['file_path'] == str(target)]
assert len(writes) == 1
index, write = writes[0]
content = write['tool_input']['content'].encode()
assert content.decode().strip().splitlines()[-1] in ('would show: yes', 'would show: no')
assert list(raw['modelUsage']) == ['claude-opus-5-5']
with target.open('xb') as stream:
    stream.write(content)
assert target.read_bytes() == content
receipt = dict(time=time.time(), operation='verbatim recovery of denied independent Opus Write tool payload',
               source=str(raw_path), source_json_pointer=f'/permission_denials/{index}/tool_input/content',
               session_id=raw['session_id'], model=list(raw['modelUsage'])[0],
               original_write_permission_denied=True, cli_returncode=0,
               report_authored_by='independent Opus judge; verifier recovered exact bytes only',
               raw_sha256=hashlib.sha256(raw_path.read_bytes()).hexdigest(),
               judge_sha256=hashlib.sha256(content).hexdigest(), exact_payload_match=True,
               additional_reviewer_launched=False)
(here / 'judge_recovery.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
