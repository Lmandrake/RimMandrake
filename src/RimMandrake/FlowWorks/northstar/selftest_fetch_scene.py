#!/usr/bin/env python3
"""Offline half of sc_fetch_fallen (RIMMANDRAKE_REBUILD_FLOWWORKS_FETCH_SCENE_RAID_NEVER_CAME): scene_fetch_fallen against a
fake map that holds each bridge tool to its contract and models the two things that sank visit 1 (2026-11-15):
  - ProofCover is a read-only "x,z" probe: anything else is REFUSED (the draft sent '61,61;cover' and laid no lid);
  - the governor: a hostile_arrival on the default stop list stops safe_advance and site_recover vanishes every raider
    (the draft's raid was gone at tick 60), unless the scene narrows B.stop_on for its own raid.
The healthy fake (raiders cross the lidded trench, two fall, the mod ladders the pit) reads every row PASS; today's mod (no
fetch job) reads FETCH_ladder_into_pit FAIL; a raid that never reaches the trench reads every row UNMEASURED, never PASS;
a crossing ladder in the control reads FAIL. Red on the draft at 2b4bffe212, green on the fix.
The fake proves the scene's logic, never the game; the live half is
`python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_fetch_fallen --out <json>`.
    python3 selftest_fetch_scene.py [path/to/concept_scenes.py]
"""
from copy import deepcopy
import importlib.util
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (HERE, ROOT / 'src/RimMandrake/Utils', ROOT / 'src/RimMandrake/Utils/modcheck'):
    sys.path.insert(0, str(p))
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'concept_scenes.py'
spec = importlib.util.spec_from_file_location('concept_scenes_under_test', SRC)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
O = C.O
XZ = re.compile(r'^-?\d+,-?\d+$')
COVER_REFUSED = 'REFUSED: arg must be x,z on a current map with FlowWorks'


class Fake:
    """mod: 'fetch' (raiders ladder the pit for a fallen comrade), None (today: no fetch job), 'crossing' (a ladder goes in
    whether or not anyone fell). fault: 'far' (the raid spawns 40 squares off and never comes), 'one' (one raider falls)."""

    def __init__(self, mod='fetch', fault=None):
        self.mod, self.fault = mod, fault
        self.stop_on = 'default'
        self.g = {'dug': {}, 'spikes': set(), 'covers': {}, 'hostile': {}, 'ladders': [], 'announced': set(), 'n': 0,
                  'fall_poll': None, 'polls': 0}
        self.saves, self.contract = {}, []

    def save(self, k):
        self.saves[k] = deepcopy(self.g)

    def load(self, k):
        self.g = deepcopy(self.saves[k])

    # ---- the clock and the governor (validation_core.Bridge.ticks over jawa/safe_advance)
    def ticks(self, n):
        g = self.g
        stops = self.stop_on == 'default' or 'hostile_arrival' in self.stop_on.split(',')
        new = [h for h in g['hostile'] if h not in g['announced']]
        g['announced'].update(new)
        if new and stops:
            g['hostile'].clear()                       # site_recover -> remove_intruders on the whole map
            return {'success': True, 'advanced': n}
        g['polls'] += 1
        trench = set(C._trap_cells()) if hasattr(C, '_trap_cells') else set()
        for hid, h in sorted(g['hostile'].items()):
            if h['held'] or self.fault == 'far':
                continue
            nz = min(h['z'] + n // 100, O[1] + 9)
            if h['z'] < O[1] <= nz and (h['x'], O[1]) in g['covers'] and g['covers'][(h['x'], O[1])]:
                h['z'], h['held'] = O[1], True
                if sum(1 for q in g['hostile'].values() if q['held']) >= (1 if self.fault == 'one' else 2):
                    for c in g['covers']:
                        g['covers'][c] = False             # the deck gives way whole
                    g['fall_poll'] = g['polls']
                continue
            if h['z'] < O[1] <= nz and (h['x'], O[1]) in g['dug']:
                nz = O[1] - 1                              # an open trench: they stop at its lip
            h['z'] = nz
        held = any(h['held'] for h in g['hostile'].values())
        if (self.mod == 'fetch' and held and g['polls'] >= (g['fall_poll'] or 0) + 2) or \
                (self.mod == 'crossing' and g['hostile'] and g['polls'] >= 3):
            if not g['ladders'] and trench:
                g['ladders'] = [{'def': 'RM_LadderPortable', 'x': O[0], 'z': O[1]}]
        return {'success': True, 'advanced': n}

    # ---- the bridge
    def call(self, tool, **kw):
        g = self.g
        if tool == 'jawa/flowworks_excavation_drive':
            c = (kw['x'], kw['z'])
            g['dug'][c] = g['dug'].get(c, 0) + kw['deepenLevels']
            return {'success': True}
        if tool == 'jawa/spawn_batch':
            for op in kw['ops'].split(';'):
                d, xz = op.split(':')
                x, z = (int(v) for v in xz.split(',')[:2])
                if d == 'RM_Spikes':
                    g['spikes'].add((x, z))
            return {'success': True}
        if tool == 'jawa/build_batch':
            for op in kw['ops'].split(';'):
                d, xz = op.split(':')
                c = tuple(int(v) for v in xz.split(',')[:2])
                banks = sum(1 for dz in (-1, 1) if (c[0], c[1] + dz) not in g['dug']) + \
                    sum(1 for dx in (-1, 1) if (c[0] + dx, c[1]) not in g['dug'])
                if d.startswith('RM_PitCover') and g['dug'].get(c, 0) >= 8 and banks >= 2:
                    g['covers'][c] = True
                else:
                    self.contract.append('cover refused at %s (banks %d)' % (c, banks))
            return {'success': True}
        if tool == 'jawa/set_plants':
            if not all(':' in op for op in kw['ops'].split(';')):
                self.contract.append('set_plants op names no def: %s' % kw['ops'])
                return {'success': False, 'message': 'Could not parse ops.'}
            return {'success': True}
        if tool == 'jawa/spawn_pawn':
            g['n'] += 1
            return {'success': True, 'pawns': [{'id': 'Human%d' % (900 + g['n'])}]}
        if tool == 'jawa/fire_raid':
            cx, cz = (int(v) for v in (kw.get('spawnCenter') or '%d,%d' % (O[0], O[1] - 20)).split(','))
            if self.fault == 'far':
                cz -= 40
            for i in range(6):
                g['n'] += 1
                g['hostile']['Human%d' % (500 + g['n'])] = {'x': cx - 2 + i % 5, 'z': cz - i // 5, 'held': False}
            return {'success': True, 'executed': True}
        if tool == 'jawa/list_pawns':
            require_hostile = kw.get('faction') == 'hostile'
            ps = [{'id': k, 'x': h['x'], 'z': h['z'], 'dead': False} for k, h in g['hostile'].items()] if require_hostile else []
            return {'success': True, 'pawns': ps}
        if tool == 'jawa/list_things':
            x, z, w, h = (int(v) for v in kw['rect'].split(','))
            return {'success': True, 'things': [t for t in g['ladders'] if t['def'] == kw['defName']
                                                and x <= t['x'] < x + w and z <= t['z'] < z + h]}
        if tool == 'jawa/static_call':
            return {'success': True, 'result': self.static(kw['type'], kw['method'], kw.get('args', ''))}
        if tool == 'jawa/mod_settings_field':
            return {'success': True, 'value': None}
        raise AssertionError('unexpected tool %s %s' % (tool, kw))

    def static(self, typ, method, arg):
        g = self.g
        if method == 'ProofCover':
            if not XZ.match(arg or ''):
                self.contract.append('ProofCover given %r (its contract is x,z)' % arg)
                return COVER_REFUSED
            c = tuple(int(v) for v in arg.split(','))
            return 'COVER cell=%d,%d present=%s covered=%s sprung=False' % (c + (c in g['covers'], g['covers'].get(c, False)))
        if method in ('ProofTrap', 'ProofCaptureDown'):
            h = g['hostile'].get(arg)
            if h is None:
                return 'REFUSED: no spawned pawn %s' % arg
            return ('TRAP descents=1 pos=%d,%d held=%s' if method == 'ProofTrap' else 'VERDICT x cell=%d,%d held=%s prisoner=True') % (
                h['x'], h['z'], h['held'])
        raise AssertionError('unexpected static %s.%s' % (typ, method))


def run(mod='fetch', fault=None, scene='scene_fetch_fallen'):
    F = Fake(mod, fault)
    out = getattr(C, scene)(F, lambda: F.save('begin'), lambda: F.load('begin'), {'calls': []})
    return {r['id']: r['status'] for r in out['rows']}, out, F


FAILS = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else why))
    if not ok:
        FAILS.append(label)


ROWS = ('FETCH_two_fell', 'FETCH_ladder_into_pit', 'FETCH_control_none_fallen_no_ladder')
rows, out, F = run()
check('every staging call keeps its tool contract (ProofCover x,z; set_plants names a def; lids rest on two banks)',
      not F.contract, F.contract)
check('the scene leaves the governor as it found it', F.stop_on == 'default', F.stop_on)
check('healthy fake (two fall, the mod ladders the pit): every row PASS', out['status'] == 'PASS'
      and all(rows.get(r) == 'PASS' for r in ROWS), rows)
r, o, _ = run(mod=None)
check("today's mod (no fetch job): FETCH_ladder_into_pit FAIL, the fall and the control PASS",
      r.get('FETCH_ladder_into_pit') == 'FAIL' and r.get('FETCH_two_fell') == 'PASS'
      and r.get('FETCH_control_none_fallen_no_ladder') == 'PASS' and o['status'] != 'PASS', r)
r, o, _ = run(fault='far')
check('a raid that never reaches the trench: every row UNMEASURED, none PASS',
      all(r.get(x) == 'UNMEASURED' for x in ROWS) and 'PASS' not in r.values(), r)
r, o, _ = run(mod='crossing')
check('a crossing ladder with nobody fallen: the control FAILs', r.get('FETCH_control_none_fallen_no_ladder') == 'FAIL', r)
r, o, _ = run(fault='one')
check('one raider falls: FETCH_two_fell FAILs, the ladder still judged', r.get('FETCH_two_fell') == 'FAIL'
      and r.get('FETCH_ladder_into_pit') == 'PASS', r)
r, o, F = run(scene='scene_pit_trap_raid')
check('scene_pit_trap_raid shares the staging: fallen become prisoners, open pit holds nobody',
      not F.contract and r.get('PTR_fallen_become_prisoners') == 'PASS' and r.get('PTR_control_open_pit_no_one_falls') == 'PASS', r)
print('selftest_fetch_scene: %s' % ('FAIL' if FAILS else 'ok'))
sys.exit(1 if FAILS else 0)
