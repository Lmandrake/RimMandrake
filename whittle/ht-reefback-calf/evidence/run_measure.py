import hashlib
import json
from pathlib import Path
import os
import subprocess
import time

here = Path(__file__).resolve().parent
repo = here.parents[2]
script = repo/'src/RimMandrake/HugeThings/northstar/measure_reefback_calf.py'
cmd = ['python3',str(script),'--repo-root',str(repo), '--game-dir',
       str(Path(os.environ['RM_STEAMAPPS'])/'common/RimWorld'),
       '--engine-il',str(here/'raw/engine.stdout.txt'),'--out',str(here/'raw/measure')]
started = time.time()
r = subprocess.run(cmd,capture_output=True,timeout=120)
(here/'raw/measure.stdout.txt').write_bytes(r.stdout)
(here/'raw/measure.stderr.txt').write_bytes(r.stderr)
receipt={'command':cmd,'rc':r.returncode,'elapsed':time.time()-started,
         'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),
         'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),
         'stderr_sha256':hashlib.sha256(r.stderr).hexdigest()}
(here/'raw/measure.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(r.stdout.decode(),end='')
print(r.stderr.decode(),end='')
raise SystemExit(r.returncode)
