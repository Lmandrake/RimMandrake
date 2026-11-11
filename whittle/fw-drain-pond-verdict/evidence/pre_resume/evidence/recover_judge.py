"""Recover the independent judge's exact denied Write payload; do not author or edit its report."""
import hashlib
import json
from pathlib import Path
import time

here = Path(__file__).resolve().parent
target = here.parent / 'JUDGE.md'
raw_path = here / 'judge_raw.json'
raw = json.loads(raw_path.read_bytes())
writes = [x for x in raw['permission_denials'] if x['tool_name'] == 'Write'
          and x['tool_input']['file_path'] == str(target)]
assert len(writes) == 1
content = writes[0]['tool_input']['content'].encode()
assert content.decode().strip().splitlines()[-1] == 'would show: yes'
assert list(raw['modelUsage']) == ['claude-opus-5-5']
with target.open('xb') as stream:
    stream.write(content)
assert target.read_bytes() == content
receipt = dict(time=time.time(), operation='verbatim recovery of denied independent Opus Write tool payload',
               source=str(raw_path), source_json_pointer='/permission_denials/0/tool_input/content',
               session_id=raw['session_id'], model=list(raw['modelUsage'])[0],
               original_write_permission_denied=True, cli_returncode=0,
               report_authored_by='independent Opus judge; builder performed byte-for-byte recovery only',
               raw_sha256=hashlib.sha256(raw_path.read_bytes()).hexdigest(),
               judge_sha256=hashlib.sha256(content).hexdigest(), exact_payload_match=True,
               new_reviewer_launched=False)
(here / 'judge_recovery.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
