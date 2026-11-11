"""Read the Windows stage against the exact tested manifest, after the runner exits."""
import hashlib
import json
from pathlib import Path
import sys
import time

here = Path(__file__).resolve().parent
attempt = here / sys.argv[1]
manifest = json.loads((attempt / 'integrity_before.json').read_text())['sha256']
root = here.parents[2]
stage = Path('/mnt/d/ClaudeWork/rimmandrake/build/selftest_RimMandrakeFlowWorks.SelfTest_79bb8021')
compared, mismatches = {}, []
for name, expected in manifest.items():
    if not name.startswith('src/'):
        continue
    p = stage / name
    actual = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    compared[name] = actual
    if actual != expected:
        mismatches.append(name)
generated = stage / 'src/RimMandrake/FlowWorks/Source/SelfTest/obj/Release/net8.0/TankTheft.g.cs'
receipt = dict(time=time.time(), stage=str(stage), compared_sha256=compared, mismatches=mismatches,
               generated=str(generated), generated_sha256=hashlib.sha256(generated.read_bytes()).hexdigest() if generated.is_file() else None)
target = attempt / 'windows_stage_readback.json'
assert not target.exists(), 'Preserve original readback'
target.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(dict(compared=len(compared), mismatches=mismatches, generated_sha256=receipt['generated_sha256'])))
assert not mismatches
