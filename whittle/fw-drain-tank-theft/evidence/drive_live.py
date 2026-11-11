"""One live attempt with unconditional stop/stamp/release after scene restoration."""
import json
from pathlib import Path
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
label = sys.argv[1]
assert label.startswith('live_attempt') and '/' not in label
out = here / (label + '.json')
assert not out.exists(), 'Preserve earlier attempts'
def win(path):
    return subprocess.check_output(['wslpath','-w',str(path)],text=True).strip()
cmd = ['python.exe', win(root / 'src/RimMandrake/FlowWorks/northstar/tank_theft_live.py'), '--out', win(out)]
receipt = dict(started=time.time(),command=cmd,cleanup=[])
rc = 1
try:
    rc = subprocess.run(cmd,cwd=root).returncode
    receipt['proof_returncode'] = rc
finally:
    # Each independent cleanup debt is attempted even if the preceding command fails.
    commands = [
        ['python3',str(here/'control_session.py'),'stop'],
        ['python3','src/RimMandrake/rimflow/cli.py','game'],
        ['python3','src/RimMandrake/rimflow/cli.py','bridge','release'],
        ['./game'],
        ['python3','src/RimMandrake/rimflow/cli.py','bridge','who'],
    ]
    for command in commands:
        p = subprocess.run(command,cwd=root,capture_output=True,text=True)
        receipt['cleanup'].append(dict(command=command,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
        print(p.stdout,p.stderr,flush=True)
        if p.returncode: rc = 1
    receipt['finished'] = time.time()
    (here/(label+'_cleanup.json')).write_text(json.dumps(receipt,indent=2)+'\n')
sys.exit(rc)
