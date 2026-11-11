"""Inspect the exact Windows stage without building or rerunning a suite."""
import hashlib
import json
from pathlib import Path
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
sys.path.insert(0, str(root / 'src/RimMandrake/Utils'))
import selftest_winstage
import winbuild

label = sys.argv[1]
proof = json.loads((here / label / 'selftest_receipt.json').read_text())
project = root / 'src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj'
stage = Path(winbuild.BUILD_ROOT) / selftest_winstage.stage_name_for(str(project), str(root))
expected = proof['sha256_after']
actual = {}
for rel in expected:
    path = stage / rel
    if rel.startswith('src/') and path.is_file():
        actual[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
missing = [rel for rel in expected if rel.startswith('src/') and rel not in actual]
mismatch = [rel for rel in actual if actual[rel] != expected[rel]]
generated = stage / project.relative_to(root).parent / 'obj/Release/net8.0/PumpOutflow.g.cs'
assert generated.is_file()
artifacts = list((generated.parents[3] / 'bin/Release/net8.0').glob('RimMandrakeFlowWorks.SelfTest.*'))
result = dict(time=time.time(), proof=label, stage=str(stage), missing=missing, mismatch=mismatch,
              sha256=actual, generated_path=str(generated),
              generated_sha256=hashlib.sha256(generated.read_bytes()).hexdigest(),
              artifacts={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts},
              build_source=json.loads((stage / 'BUILD_SOURCE.json').read_text()))
(here / (label + '_stage.json')).write_text(json.dumps(result, indent=2) + '\n')
(here / (label + '_PumpOutflow.g.cs.txt')).write_bytes(generated.read_bytes())
print(json.dumps({k: v for k, v in result.items() if k not in ('sha256', 'build_source')}, indent=2))
assert not missing and not mismatch and artifacts
