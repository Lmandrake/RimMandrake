import hashlib
import json
from pathlib import Path
import subprocess
import time

here = Path(__file__).resolve().parent
script = here / 'read_cut_contract.ps1'
cmd = ['/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe',
       '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
       subprocess.check_output(['wslpath', '-w', str(script)], text=True).strip(),
       '-GameDir', 'D:\\SteamLibrary\\steamapps\\common\\RimWorld']
started = time.time()
r = subprocess.run(cmd, capture_output=True, timeout=90)
for name, data in [('stdout.txt', r.stdout), ('stderr.txt', r.stderr)]:
    (here / 'raw' / ('engine-cut-contract.' + name)).write_bytes(data)
(here / 'raw/engine-cut-contract.receipt.json').write_text(json.dumps({
    'command': cmd, 'rc': r.returncode, 'elapsed': time.time()-started,
    'script_sha256': hashlib.sha256(script.read_bytes()).hexdigest(),
    'stdout_sha256': hashlib.sha256(r.stdout).hexdigest(),
    'stderr_sha256': hashlib.sha256(r.stderr).hexdigest(),
    'mode': 'reflection-only IL metadata; no assembly execution'}, indent=2)+'\n')
print('engine rc', r.returncode)
raise SystemExit(r.returncode)
