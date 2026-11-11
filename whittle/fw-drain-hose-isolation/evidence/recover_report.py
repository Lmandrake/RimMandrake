"""Recover the fresh independent judge's exact JSON result, with a receipt and no edits."""
import hashlib
import json
from pathlib import Path
import time

here = Path(__file__).resolve().parent
import sys
mode = sys.argv[1]
assert mode in ('broaden','judge')
raw = here / (mode + '_raw.json')
record = json.loads(raw.read_text())
assert record.get('subtype') == 'success' and not record.get('is_error')
assert not record.get('permission_denials')
report = record['result'].encode('utf-8')
assert report.strip()
if mode == 'judge':
    assert report.decode().splitlines()[-1] in ('would show: yes', 'would show: no')
out = here.parent / 'JUDGE.md' if mode == 'judge' else here / 'broaden_report.md'
assert not out.exists(), 'Preserve independent reports'
out.write_bytes(report)
receipt = dict(time=time.time(), operation='Unchanged UTF-8 copy of the complete fresh CLI JSON result string to report file',
               raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(), result_sha256=hashlib.sha256(report).hexdigest(),
               file_sha256=hashlib.sha256(out.read_bytes()).hexdigest(), unchanged=out.read_bytes() == report,
               session_id=record.get('session_id'), total_cost_usd=record.get('total_cost_usd'),
               usage=record.get('usage'), modelUsage=record.get('modelUsage'),
               permission_denials=record.get('permission_denials'), last_line=report.decode().splitlines()[-1])
assert not (here / (mode + '_recovery.json')).exists()
(here / (mode + '_recovery.json')).write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('usage', 'modelUsage')}, indent=2))
