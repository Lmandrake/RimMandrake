"""Parent review of retained observations; no game interaction."""
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import time

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'whittle/ht-juvenile-tier'
LIVE = WORK / 'evidence/raw/live-attempt5'
s = json.loads((LIVE / 'loaded-methods.json').read_text())
assert s['ok'] and not s['errors'] and s['restoration']['ok']
assert s['original_settings'] == s['restoration']['readbacks']
assert s['settings_files_before'] == s['settings_files_after']
assert s['environment_before'] == s['environment_after']

def f32(x):
    try:
        return struct.unpack('<f', struct.pack('<f', x))[0]
    except OverflowError:
        return math.copysign(math.inf, x)

def tier(x, ladder, force):
    return 0 if force < 0 else max(1 if force > 0 else 0, sum(x >= t for t in ladder))

checked = runtime = 0
for row in [r['fields'] for r in s['observations']] + s['resolved_kind_census']:
    base = float(row['base'])
    ladder = list(map(float, row['thresholds'].split(',')))
    force = int(row['force'])
    parts = [] if row['stages'] in ['', 'null'] else row['stages'].split(',')
    factors = [float(x.split(':', 1)[1]) if ':' in x else None for x in parts]
    maximum = 1.
    for x in factors:
        if x is not None and x > maximum:
            maximum = x
    adult = tier(f32(base * maximum), ladder, force)
    valid = bool(factors) and all(x is not None and math.isfinite(x) and x > 0 for x in factors)
    spacing = tier(f32(base * max(factors)), ladder, force) if valid else adult
    assert int(row['AdultTier']) == adult and int(row['SpacingTier']) == spacing, row
    comp_factor = maximum if math.isfinite(maximum) and maximum > 1 else 1
    comp = force >= 0 and (force > 0 or f32(base * comp_factor) >= ladder[0])
    assert (row['DefQualifies'] == 'True') == comp, row
    assert (row['eligibleNoT3'] == 'True') == (adult >= 2), row
    assert (row['eligibleWithT3'] == 'True') == (adult >= 2 and spacing != 3), row
    if row['GetTier'] != 'unsupported':
        expected = f32(f32(base) * f32(factors[int(row['stageIndex'])]))
        actual = f32(float(row['body']))
        bits = struct.unpack('<I', struct.pack('<f', expected))[0]
        assert actual == expected and row['body'] == row['bodyAgain'], row
        assert row['bodyFloat32Bits'] == f'{bits:08X}', row
        assert int(row['GetTier']) == tier(actual, ladder, force), row
        assert 'memoOwnPawn:True,memoDefault:True,offset:0' in row['VEF'], row
        runtime += 1
    if 'fixtureRandBefore' in row:
        assert row['fixtureRandBefore'] == row['fixtureRandAfter'], row
    checked += 1
assert len(s['observations']) == 153 and len(s['resolved_kind_census']) == 686
preflights = {}
for name in ['preflight-offline', 'preflight-live']:
    p = json.loads((LIVE / (name + '.json')).read_text())
    assert p['rows'] and all(r['status'] == 'PASS' for r in p['rows'])
    if name == 'preflight-offline':
        assert next(r for r in p['rows'] if r['id'] == 'O13')['status'] == 'PASS'
    preflights[name] = {'all_rows_pass': len(p['rows']), 'required_except_O02':
                       sum(r['required'] and r['id'] != 'O02' for r in p['rows'])}
for name in ['entry-before', 'entry-after']:
    p = json.loads((LIVE / (name + '.json')).read_text())
    assert p['ticksGame'] == [-1, -1, -1]
    for r in p['calls']:
        assert r['result']['success'] and r['result']['state'] == {'programState': 'Entry', 'hasCurrentGame': False}
mod = ROOT / 'src/RimMandrake/HugeThings'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
a = s['artifact']
assert sha(mod / 'Assemblies/RM_HugeThings.dll') == a['dll_sha256'] == a['deployed_dll_sha256']
assert sha(mod / 'Assemblies/RM_HugeThings.dll.srchash') == a['stamp_sha256'] == a['deployed_stamp_sha256']
inputs = re.findall(r'^([0-9a-f]{64}) (.+)$', a['source_stamp'], re.M)
assert len(inputs) == 51
for h, rel in inputs:
    assert sha(mod / 'Source' / rel.strip()) == h, rel
assert json.loads(Path('/home/mandrake/codex-steve/ht-loop/evidence/juvenile-tier.json').read_text()) == s
result = dict(at=time.time(), ok=True, independently_derived_rows=checked, runtime_rows=runtime,
              observations=153, census=686, restored_setting_fields=len(s['original_settings']),
              settings_file_inventory_count=len(s['settings_files_before']), preflights=preflights,
              exact_environment_and_rng=True, compiled_inputs=51,
              artifact={k: v for k, v in a.items() if k != 'source_stamp'},
              scope='Parent numeric/float32/force/gate/artifact audit. L1 Entry, no generated-pawn modifiers, map/passage/flight/L4 claim.',
              audit_correction='Initial parent one-off incorrectly expected O13 in live-only rows. O13 is an offline row; both complete returned row sets are PASS. No live result changed.')
(WORK / 'parent_admin/accepted-live-audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
