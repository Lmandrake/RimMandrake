"""Record a real source identity check against the proof's full input manifest."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
here = Path(__file__).resolve().parent
root = here.parents[2]
proof = here / sys.argv[2] if len(sys.argv) > 2 else here
before = json.loads((proof / 'integrity_before.json').read_text())
sha = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in before['sha256']}
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
changed = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=root, text=True).splitlines()
record = dict(time=time.time(), HEAD=head, sha256=sha,
              matches_proof_inputs=sha == before['sha256'], matches_tested_HEAD=head == before['HEAD'],
              tracked_changed_paths=changed,
              changed_production_paths=[p for p in changed if '/Source/' in p and '/SelfTest/' not in p])
out = here / (sys.argv[1] + '.json')
assert not out.exists()
out.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({k:v for k,v in record.items() if k != 'sha256'}, indent=2))
assert record['matches_proof_inputs'] and record['matches_tested_HEAD'] and not record['changed_production_paths']
