"""Read the actual Windows stage, its provenance and selftest artifacts after the proof."""
import hashlib
import json
from pathlib import Path
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
if len(sys.argv) > 1:
    here = here / sys.argv[1]
    here.mkdir(exist_ok=True)
sys.path.insert(0, str(root / 'src/RimMandrake/Utils'))
import selftest_winstage
import winbuild

project = root / 'src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj'
stage = Path(winbuild.BUILD_ROOT) / selftest_winstage.stage_name_for(str(project), str(root))
before = json.loads((here / 'integrity_before.json').read_text())
checks = {}
for rel, digest in before['sha256'].items():
    path = stage / rel
    checks[rel] = dict(expected_sha256=digest,
                       stage_sha256=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)
expected_exclusions = {p: 'normal stage rsync excludes image assets and does not stage Whittle evidence'
                       for p in checks if Path(p).suffix.lower() in ('.png', '.psd', '.ogg', '.wav') or p.startswith('whittle/')}
artifacts = {}
for path in (stage / project.relative_to(root).parent / 'bin/Release/net8.0').glob('RimMandrakeFlowWorks.SelfTest.*'):
    artifacts[str(path.relative_to(stage))] = dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                                 bytes=path.stat().st_size, mtime=path.stat().st_mtime)
provenance = stage / 'BUILD_SOURCE.json'
saved_provenance = here / 'BUILD_SOURCE.json'
if saved_provenance.exists():
    assert saved_provenance.read_bytes() == provenance.read_bytes(), 'stage provenance changed'
else:
    saved_provenance.write_bytes(provenance.read_bytes())
line_endings = {}
for rel in ('src/RimMandrake/FlowWorks/Source/SelfTest/PipeSpanNetChecks.cs',
            'src/RimMandrake/FlowWorks/Source/Machinery/RM_PipePoles.cs'):
    data = (stage / rel).read_bytes()
    line_endings[rel] = dict(crlf=data.count(b'\r\n'), lf=data.count(b'\n'),
                             bare_cr=data.count(b'\r') - data.count(b'\r\n'))
record = dict(time=time.time(), stage=str(stage), inputs=checks, artifacts=artifacts,
              line_endings=line_endings,
              expected_stage_exclusions=expected_exclusions,
              all_inputs_match=all(v['expected_sha256'] == v['stage_sha256'] for p, v in checks.items() if p not in expected_exclusions))
out = here / ('stage_identity_verified.json' if (here / 'stage_identity.json').exists() else 'stage_identity.json')
assert not out.exists()
out.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(dict(stage=str(stage), all_inputs_match=record['all_inputs_match'], artifacts=artifacts), indent=2))
assert record['all_inputs_match'] and artifacts
