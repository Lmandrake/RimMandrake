"""Publish only the two integration fixes, registered checks and shipping pairs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
paths = [
    'src/RimMandrake/Cauldron/Source/RM_GasTap.cs',
    'src/RimMandrake/LuminousPigment/Source/FlowWorksWaterBridge.cs',
    *['src/RimMandrake/FlowWorks/Source/SelfTest/' + name for name in (
        'RimMandrakeFlowWorks.SelfTest.csproj', 'TankTheftCallerChecks.cs',
        'TankTheftHarness.cs', 'TankTheftHarness.targets', 'ExternalTankTheftChecks.cs')],
    *['src/RimMandrake/' + mod + '/Assemblies/' + dll + suffix
      for mod, dll in (('Cauldron', 'RimMandrake.Cauldron.dll'),
                       ('LuminousPigment', 'RimMandrakeLuminousPigment.dll'))
      for suffix in ('', '.srchash')],
]
receipt = json.loads((here / 'external_green2/selftest_receipt.json').read_text())
assert receipt['returncode'] == 0 and receipt['source_test_hashes_unchanged']
assert json.loads((here / 'external_build_after.json').read_text())['pairs']
hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in paths}
for name in paths[:7]:
    assert hashes[name] == receipt['sha256_after'][name], name
target = here / 'external_publish_inputs.json'
assert not target.exists()
target.write_text(json.dumps(dict(paths=paths, sha256=hashes), indent=2) + '\n')
message = ('Scope external FlowWorks tank transfers\n\n'
           'Attribute GlowTank draws and Cauldron gas delivery; cover production bodies.\n'
           'Co-Authored-By: Codex (GPT) via WSL codex-cli')
sys.exit(subprocess.run(['./publish', '-m', message, *paths], cwd=root).returncode)
