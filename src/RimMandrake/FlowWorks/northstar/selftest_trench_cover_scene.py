#!/usr/bin/env python3
"""Offline half of sc_trench_cover (RIMMANDRAKE_REBUILD_FLOWWORKS_TRENCH_SCENE_READ_LID_PROOF): scene_trench_cover against a
fake map that holds each bridge tool to its contract and models what visit 1 (2026-11-15, rows.jsonl sc_trench_cover_
20261115T131926) read: the draft asked RM_PromotionProofs.ProofCover, the pit-LID probe, for a trench pawn's combat cover
(present=False covered=False on a mod whose RM_TrenchCover.ProofTrenchCover read 0.441 square-on the same day,
evidence/sc_trench_cover__proof_*.json), and passed TR_no_raider_shelters_in_pit on an empty 2x2 rect while its raid stood
far off (11 hostiles on the map, none near).
  - every jawa/ call names only parameters its C# [Tool] declares (selftest_bridge_args' signature reader); the cover is
    read with ProofTrenchCover "target;shooter" (two spawned pawns, a ranged shooter), never the lid probe; the raid is a
    placed live raid; the scene's own raid never stops the strict governor and the governor and settings are left as found;
  - the healthy fake (0.441 square-on in the trench, 0 on open ground, raiders stop at the lip) reads every row PASS;
    planted faults FAIL their row: trench cover equal to open ground (0 in the trench), open ground reading trench cover,
    a raider standing in the cage pit;
  - vacuous reads are UNMEASURED, never PASS: an all-zero TRENCH vector, a REFUSED reply, a raid that never came, a raid
    of nobody.
The visit-1 governor let the draft's 2,500 ticks run (`lenient`, the default here); `strict` stops on any hostile unless
the scene narrowed B.stop_on (the pit-trap fake's model). Red on the draft at 2b4bffe212, green on the fix. The fake proves
the scene's logic, never the game; the live half is
`python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_trench_cover --out <json>`.
    python3 selftest_trench_cover_scene.py [path/to/concept_scenes.py]
"""
from copy import deepcopy
import glob
import importlib.util
import os
from pathlib import Path
import re
import sys

os.environ.setdefault('RIMBRIDGE_GOVERNOR_LOG', '')     # a fake stop leaves no row in the real governor_stops.jsonl
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (HERE, ROOT / 'src/RimMandrake/Utils', ROOT / 'src/RimMandrake/Utils/modcheck'):
    sys.path.insert(0, str(p))
import clockgate  # noqa: E402

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'concept_scenes.py'
spec = importlib.util.spec_from_file_location('concept_scenes_under_test', SRC)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
O = C.O
XZ = re.compile(r'^-?\d+,-?\d+$')
TOOLS = ROOT / 'src/RimMandrake/bridgetools/JawaBench.BridgeTools'
TRENCH_TYPE = 'RimMandrake.FlowWorks.RM_TrenchCover'
RANGED = {'Mercenary_Gunner'}
BEFORE = {'trenchCoverEnabled': 'True', 'trenchCoverStrength': '0.6', 'trenchCoverCap': '0.75'}   # the owner's own values


def signatures():
    """{tool: [parameter names]} from the C# [Tool] methods (the same reader as selftest_bridge_args.signatures)."""
    sigs = {}
    for f in glob.glob(str(TOOLS / '*.cs')):
        txt = open(f, encoding='utf-8', errors='ignore').read()
        for m in re.finditer(r'\[Tool\(\s*"([^"]+)"(.*?)public static (?:async )?(?:Task<\w+>|\w+) \w+\((.*?)\)\s*\{', txt, re.S):
            sigs[m.group(1)] = re.findall(r'\b[A-Za-z\[\]<>?]+\s+(\w+)\s*(?:=|,)', m.group(3).replace('\n', ' ') + ',')
    return sigs


SIGS = signatures()


class Fake:
    """mod: 'cover' (0.441 square-on from a 1 m trench, 0 on open ground), 'flat' (the trench reads as open ground),
    'everywhere' (open ground reads trench cover too), 'shelter' (a raider walks into the cage pit). fault: 'zero' (every
    TRENCH read an all-zero vector), 'refuse' (ProofTrenchCover REFUSED), 'far' (the raid lands 40 squares off and holds),
    'nobody' (fire_raid spawns no one). governor: 'lenient' (visit 1: the clock ran) or 'strict'."""

    def __init__(self, mod='cover', fault=None, governor='lenient'):
        self.mod, self.fault, self.governor = mod, fault, governor
        self.stop_on = 'default'
        self.g = {'dug': {}, 'pawns': {}, 'settings': dict(BEFORE), 'n': 0, 'ticked': 0}
        self.saves, self.contract, self.stops, self.methods = {}, [], [], []

    def save(self, k):
        self.saves[k] = deepcopy(self.g)

    def load(self, k):
        settings = self.g['settings']           # settings are not part of the map: they stay as poked until restored
        self.g = deepcopy(self.saves[k])
        self.g['settings'] = settings

    def hostiles(self):
        return {k: p for k, p in self.g['pawns'].items() if p['faction'] == 'hostile'}

    # ---- the clock and the governor (validation_core.Bridge.ticks over jawa/safe_advance)
    def ticks(self, n):
        g = self.g
        stops = self.stop_on == 'default' or 'hostile_arrival' in self.stop_on.split(',')
        if self.governor == 'strict' and stops and self.hostiles():
            r = {'state': 'stopped', 'executed': 60, 'requested': min(n, 2500),
                 'stopBy': {'kind': 'hostile_arrival', 'severity': 'threat', 'subjectId': sorted(self.hostiles())[0],
                            'detail': 'present at arm: Human Thrasher (humanlike)'}}
            self.stops.append(r)
            raise clockgate.GovernorStop(r)
        g['ticked'] += n
        pit = (O[0] + 12, O[1])
        for i, (hid, h) in enumerate(sorted(self.hostiles().items())):
            if self.fault == 'far' or h.get('inPit'):
                continue
            at_line = h['z'] >= O[1] - 1
            if at_line and self.mod == 'shelter' and i == 0:
                h['x'], h['z'], h['inPit'] = pit[0], pit[1], True     # the planted fault: shelter in the cage
                continue
            h['z'] = min(h['z'] + n // 100, O[1] - 1)                  # they stop at the trench's south lip
        return {'success': True, 'advanced': n}

    # ---- the bridge
    def call(self, tool, **kw):
        g = self.g
        if tool.startswith('jawa/'):
            unknown = sorted(set(kw) - set(SIGS.get(tool, ())))
            if tool not in SIGS or unknown:
                self.contract.append('%s: parameters the C# does not declare %s' % (tool, unknown or 'tool unknown'))
        if tool == 'jawa/flowworks_excavation_drive':
            c = (kw['x'], kw['z'])
            g['dug'][c] = g['dug'].get(c, 0) + kw['deepenLevels']
            return {'success': True, 'cell': {'x': c[0], 'z': c[1]}, 'depth': g['dug'][c], 'waterSet': False, 'waterDl': 0}
        if tool == 'jawa/mod_settings_field':
            if kw.get('typeName') != C.SETTINGS:
                self.contract.append('mod_settings_field on %r' % kw.get('typeName'))
            if kw.get('action') == 'set':
                g['settings'][kw['field']] = str(kw['value'])
            return {'success': True, 'value': g['settings'].get(kw['field'])}
        if tool == 'jawa/spawn_pawn':
            if not all(k in kw for k in ('kindDef', 'x', 'z', 'faction')):
                self.contract.append('spawn_pawn without kindDef/x/z/faction: %s' % kw)
            g['n'] += 1
            pid = 'Human%d' % (900 + g['n'])
            g['pawns'][pid] = {'kind': kw.get('kindDef'), 'faction': kw.get('faction'), 'x': kw.get('x'), 'z': kw.get('z')}
            return {'success': True, 'pawns': [{'id': pid}]}
        if tool == 'jawa/fire_raid':
            if kw.get('dryRun') is not False or not XZ.match(str(kw.get('spawnCenter', ''))):
                self.contract.append('fire_raid not a placed live raid: %s' % kw)
            cx, cz = (int(v) for v in str(kw.get('spawnCenter') or '%d,%d' % (O[0], O[1] - 45)).split(','))
            if self.fault == 'far':
                cz -= 40
            for i in range(0 if self.fault == 'nobody' else 6):
                g['n'] += 1
                g['pawns']['Human%d' % (500 + g['n'])] = {'kind': 'Mercenary_Slasher', 'faction': 'hostile',
                                                          'x': cx - 2 + i % 5, 'z': cz - i // 5}
            return {'success': True, 'executed': True}
        if tool == 'jawa/list_pawns':
            ps = [{'id': k, 'x': h['x'], 'z': h['z'], 'dead': False} for k, h in self.hostiles().items()] \
                if kw.get('faction') == 'hostile' else []
            if kw.get('rect'):
                x, z, w, hh = (int(v) for v in kw['rect'].split(','))
                ps = [p for p in ps if x <= p['x'] < x + w and z <= p['z'] < z + hh]
            return {'success': True, 'pawns': ps}
        if tool == 'jawa/order_pawn':
            return {'success': False, 'message': '0/1 pawn(s) standing'}
        if tool == 'rimworld/screenshot_cell_rect':
            return {'success': True}
        if tool == 'jawa/static_call':
            self.methods.append(kw['method'])
            return {'success': True, 'result': self.static(kw['type'], kw['method'], kw.get('args', ''))}
        raise AssertionError('unexpected tool %s %s' % (tool, kw))

    def static(self, typ, method, arg):
        g = self.g
        if method == 'ProofCover':                 # the pit-lid probe: no lid on a trench square reads covered=False
            if not XZ.match(arg or ''):
                self.contract.append('ProofCover given %r (its contract is x,z)' % arg)
                return 'REFUSED: arg must be x,z'
            c = tuple(int(v) for v in arg.split(','))
            return 'COVER cell=%d,%d present=False covered=False sprung=False depth=%d' % (c + (g['dug'].get(c, 0),))
        if method == 'ProofTrenchCover':
            if typ != TRENCH_TYPE:
                self.contract.append('ProofTrenchCover on %r' % typ)
            ids = str(arg).split(';')
            t, s = (g['pawns'].get(i) for i in ids) if len(ids) == 2 else (None, None)
            if t is None or s is None:
                self.contract.append('ProofTrenchCover given %r (its contract is "targetId;shooterId" of spawned pawns)' % arg)
                return 'REFUSED: arg must be targetId;shooterId'
            if s['kind'] not in RANGED:
                self.contract.append('ProofTrenchCover shooter %s has no ranged verb' % s['kind'])
                return 'REFUSED: shooter has no ranged verb'
            if self.fault == 'refuse':
                return 'REFUSED: no current map'
            if self.fault == 'zero':
                return ('TRENCH trench=0.000 vanilla=0.000 combined=0.000 hit=0.000 hitNoTrench=0.000 cage=False '
                        'target=%d,%d shooter=%d,%d size=1.000' % (t['x'], t['z'], s['x'], s['z']))
            dug = g['dug'].get((t['x'], t['z']), 0) >= 2
            square_on = s['x'] == t['x'] and abs(s['z'] - t['z']) >= 9
            on = g['settings'].get('trenchCoverEnabled') == 'True' and g['settings'].get('trenchCoverStrength') == '1.0'
            if self.mod == 'everywhere':
                cov = 0.441 if square_on and on else 0.0
            else:
                cov = 0.441 if dug and square_on and on and self.mod != 'flat' else 0.0
            h0 = 0.332
            return ('TRENCH trench=%.3f vanilla=0.000 combined=%.3f hit=%.3f hitNoTrench=%.3f cage=False target=%d,%d '
                    'shooter=%d,%d size=1.000' % (cov, cov, h0 * (1 - cov), h0, t['x'], t['z'], s['x'], s['z']))
        raise AssertionError('unexpected static %s.%s' % (typ, method))


COVER_ROWS = ('TR_trench_pawn_covered', 'TR_trench_hit_falls', 'TR_control_open_ground_no_cover')
RAID_ROW = 'TR_no_raider_shelters_in_pit'
ROWS = COVER_ROWS + (RAID_ROW,)


def run(mod='cover', fault=None, governor='lenient'):
    F = Fake(mod, fault, governor)
    try:
        out = C.scene_trench_cover(F, lambda: F.save('begin'), lambda: F.load('begin'), {'calls': []})
    except Exception as e:                       # noqa: BLE001 - a GovernorStop out of the scene is a crash
        return {}, {'status': 'CRASH', 'rows': [], 'error': repr(e)[:300]}, F
    return {r['id']: r['status'] for r in out['rows']}, out, F


FAILS = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else str(why)[:600]))
    if not ok:
        FAILS.append(label)


print('under test: %s' % SRC)
rows, out, F = run(governor='strict')
check('the scene\'s own raid never stops the strict governor (narrowed for every tick of it)',
      not F.stops and out['status'] != 'CRASH', out.get('error') or F.stops[:1])
check('the scene leaves the governor as it found it', F.stop_on == 'default', F.stop_on)
check('the owner\'s cover settings are restored', F.g['settings'] == BEFORE, F.g['settings'])
rows, out, F = run()
check('every staging call keeps its tool contract (C# parameters, ProofTrenchCover target;shooter with a ranged '
      'shooter, a placed live raid)', not F.contract, F.contract)
check('cover is read as combat cover (RM_TrenchCover.ProofTrenchCover), never the pit-lid ProofCover',
      'ProofTrenchCover' in F.methods and 'ProofCover' not in F.methods, sorted(set(F.methods)))
check('healthy fake (0.441 in the trench, 0 on open ground, raiders stop at the lip): every row PASS',
      out['status'] == 'PASS' and all(rows.get(r) == 'PASS' for r in ROWS), rows)
r, o, _ = run(mod='flat')
check('planted fault, trench cover equal to open ground (0 in the trench): the cover and hit rows FAIL',
      r.get('TR_trench_pawn_covered') == 'FAIL' and r.get('TR_trench_hit_falls') == 'FAIL' and o['status'] == 'FAIL', r)
r, o, _ = run(mod='everywhere')
check('planted fault, open ground reads trench cover: the control FAILs',
      r.get('TR_control_open_ground_no_cover') == 'FAIL' and o['status'] == 'FAIL', r)
r, o, _ = run(mod='shelter')
check('planted fault, a raider standing in the cage pit: %s FAIL' % RAID_ROW, r.get(RAID_ROW) == 'FAIL', r)
for fault, label in (('zero', 'an all-zero TRENCH vector'), ('refuse', 'a REFUSED ProofTrenchCover reply')):
    r, o, _ = run(fault=fault)
    check('%s: every cover row UNMEASURED, never PASS' % label,
          all(r.get(x) == 'UNMEASURED' for x in COVER_ROWS) and o['status'] != 'PASS', r)
for fault, label in (('far', 'a raid that never came'), ('nobody', 'a raid of nobody')):
    r, o, _ = run(fault=fault)
    check('%s: %s UNMEASURED, never PASS' % (label, RAID_ROW), r.get(RAID_ROW) == 'UNMEASURED' and o['status'] != 'PASS', r)
r, o, _ = run(mod='shelter', fault='far')
check('a raid that never came cannot FAIL or PASS the pit row on its own', r.get(RAID_ROW) == 'UNMEASURED', r)
print('selftest_trench_cover_scene: %s (%d failed)' % ('FAIL' if FAILS else 'ok', len(FAILS)))
sys.exit(1 if FAILS else 0)
