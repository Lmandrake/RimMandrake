#!/usr/bin/env python3
"""Offline half of sc_ice (RIMMANDRAKE_REBUILD_FLOWWORKS_ICE_SCENE_BASIN_NEVER_FROZE): scene_ice against a fake map that holds
each bridge tool to its contract and models the three things that sank visit 1 (2026-11-15):
  - ProofStageBasin's contract is x;z;w;h;levels;waterM;FluidDef: the draft sent '60,60,5,5;freeze', was REFUSED, and froze nothing;
  - flowworks_job_probe designates and orders nothing: the draft's "cut" never happened;
  - ICE_melts_back_into_pond read the fill's own 20,000 dL and PASSED with no ice anywhere.
The fake freezes a square only when ThinIce is painted on it (vanilla's FreezeManager lays ThinIce on the temp grid), deepens a
square only when a designated cut is ORDERED, and melts a crushed-ice pile 10,000 ticks above 0 C into the melt ledger.
  mod='ice'    the healthy mod: a cut through frozen water leaves one crushed ice that thaws to 10,000 dL -> every row PASS
  mod=None     a cut through frozen water leaves nothing -> ICE_cut FAIL, the melt UNMEASURED (never PASS), the control PASS
  mod='always' crushed ice on every cut -> the control FAILs
  fault='thaw' the painted ice is gone before the cut lands -> the cut row UNMEASURED, never PASS
  fault='cold' the site never gets above 0 C -> the melt row UNMEASURED
  fault='nomelt' warm, the pile never melts -> the melt row FAILs
  fault='refuse' the work giver refuses the frozen square -> the cut row FAILs (MOD), the melt UNMEASURED
Red on the draft at 2b4bffe212, green on the fix. The fake proves the scene's logic, never the game; the live half is
`python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_ice --out <json>`.
    python3 selftest_ice_scene.py [path/to/concept_scenes.py]
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
BASIN = re.compile(r'^-?\d+;-?\d+;\d+;\d+;\d+;[\d.]+;\w*$')
XZ = re.compile(r'^(-?\d+),(-?\d+)$')
RECT = re.compile(r'^(-?\d+),(-?\d+),(\d+),(\d+)$')


def cells_of(rect):
    m = RECT.match(rect or '')
    if not m:
        return None
    x, z, w, h = (int(v) for v in m.groups())
    return [(x + i, z + j) for i in range(w) for j in range(h)]


class Fake:
    def __init__(self, mod='ice', fault=None):
        self.mod, self.fault = mod, fault
        self.stop_on = 'default'
        self.g = {'d': {}, 'dl': {}, 'ice': set(), 'desig': set(), 'orders': [], 'piles': {}, 'ledger': [0, 0, 0, 0, 0],
                  'tick': 0, 'n': 0, 'temp': -5.0 if fault == 'cold' else 12.0}
        self.saves, self.contract = {}, []

    def save(self, k):
        self.saves[k] = deepcopy(self.g)

    def load(self, k):
        self.g = deepcopy(self.saves[k])

    def ticks(self, n):
        g = self.g
        g['tick'] += n
        if self.fault == 'thaw':
            g['ice'].clear()
        for o in list(g['orders']):
            if g['tick'] - o['at'] >= 500:                      # the ordered cut lands
                g['orders'].remove(o)
                c = o['cell']
                g['d'][c] = g['d'].get(c, 0) + 1
                g['desig'].discard(c)
                if (self.mod == 'ice' and c in g['ice']) or self.mod == 'always':
                    lip = (c[0] - 1, c[1])
                    g['piles'][lip] = g['piles'].get(lip, 0) + 1
                    g['piles_at'] = g['tick']
        if g['temp'] > 0 and self.fault != 'nomelt':
            for lip in list(g['piles']):
                g.setdefault('warm', {}).setdefault(lip, 0)
                g['warm'][lip] += n
                while g['piles'].get(lip) and g['warm'][lip] >= 10000:
                    g['warm'][lip] -= 10000
                    g['piles'][lip] -= 1
                    g['ledger'][0] += 10000
                if not g['piles'].get(lip):
                    g['piles'].pop(lip, None)
        return {'success': True, 'advanced': n}

    def call(self, tool, **kw):
        g = self.g
        if tool == 'jawa/flowworks_excavation_drive':
            c = (kw['x'], kw['z'])
            g['d'][c] = g['d'].get(c, 0) + kw['deepenLevels']
            return {'success': True, 'depth': g['d'][c]}
        if tool == 'jawa/flowworks_excavation_rect':
            rows = [{'x': x, 'z': z, 'd': g['d'].get((x, z), 0), 'dl': g['dl'].get((x, z), 0)}
                    for (x, z) in cells_of('%d,%d,%d,%d' % (kw['x'], kw['z'], kw['w'], kw['h']))]
            return {'success': True, 'rows': rows}
        if tool == 'jawa/mod_settings_field':
            return {'success': True, 'value': None}
        if tool == 'jawa/spawn_pawn':
            g['n'] += 1
            return {'success': True, 'pawns': [{'id': 'Human%d' % (900 + g['n'])}]}
        if tool == 'jawa/set_terrain_batch':
            for op in kw['ops'].split(';'):
                d, _, r = op.partition(':')
                cs = cells_of(r) or ([tuple(int(v) for v in XZ.match(r).groups())] if XZ.match(r) else None)
                if cs is None:
                    self.contract.append('set_terrain_batch op %r' % op)
                    return {'success': False}
                if d == 'ThinIce':
                    g['ice'].update(c for c in cs if g['dl'].get(c))   # thin ice lies on water only
            return {'success': True}
        if tool == 'jawa/get_terrain_batch':
            cs = cells_of(kw['rects'])
            if cs is None:
                self.contract.append('get_terrain_batch rects %r' % kw['rects'])
                return {'success': False}
            return {'success': True, 'ops': ';'.join('%s:%d,%d' % ((('ThinIce' if c in g['ice'] else 'WaterShallow'),) + c)
                                                     for c in cs)}
        if tool == 'jawa/cell_temperature':
            if not XZ.match(kw.get('cell') or ''):
                self.contract.append('cell_temperature cell %r' % kw.get('cell'))
            return {'success': True, 'temperature': g['temp']}
        if tool == 'jawa/designate_batch':
            if kw.get('designation') != 'RM_DigCanal' or cells_of(kw.get('rect')) is None:
                self.contract.append('designate_batch %s' % kw)
            g['desig'].update(cells_of(kw.get('rect')) or [])
            return {'success': True}
        if tool == 'jawa/flowworks_job_probe':
            c = (kw['x'], kw['z'])
            refuse = self.fault == 'refuse' and c in g['ice']
            present = c in g['desig']
            return {'success': True, 'terrain': 'ThinIce' if c in g['ice'] else 'WaterShallow', 'designationPresent': present,
                    'designator': {'accepted': not refuse},
                    'workGiver': {'shouldSkip': not present, 'hasJobOnCell': present and not refuse,
                                  'jobDef': 'RM_DigCanalJob' if present and not refuse else None},
                    'pawn': {'workTypeDisabled': False, 'canReach': True}}
        if tool == 'jawa/ordered_job':
            c = (kw['targetAX'], kw['targetAZ'])
            if kw.get('jobDef') != 'RM_DigCanalJob' or c not in g['desig']:
                self.contract.append('ordered_job %s without a designation' % kw)
                return {'success': True, 'accepted': False}
            g['orders'].append({'cell': c, 'at': g['tick']})
            return {'success': True, 'accepted': True}
        if tool == 'jawa/list_things':
            cs = set(cells_of(kw['rect']) or [])
            return {'success': True, 'things': [{'def': kw['defName'], 'x': c[0], 'z': c[1], 'stackCount': n}
                                                for c, n in g['piles'].items() if c in cs and kw['defName'] == 'RM_CrushedIce']}
        if tool == 'jawa/destroy_batch':
            cs = set(cells_of(kw['rects']) or [])
            for c in list(g['piles']):
                if c in cs:
                    g['piles'].pop(c)
            return {'success': True}
        if tool == 'jawa/static_call':
            return {'success': True, 'result': self.static(kw['method'], kw.get('args', ''))}
        raise AssertionError('unexpected tool %s %s' % (tool, kw))

    def static(self, method, arg):
        g = self.g
        if method == 'ProofFillWithFluid':
            x, z, m, _f = arg.split(',')
            g['dl'][(int(x), int(z))] = int(float(m) * 20000)
            return 'FILLED (%s, 0, %s) W=%ddL' % (x, z, g['dl'][(int(x), int(z))])
        if method == 'ProofStageBasin':
            if not BASIN.match(arg or ''):
                self.contract.append('ProofStageBasin given %r (its contract is x;z;w;h;levels;waterM;FluidDef)' % arg)
                return 'REFUSED: arg must be x;z;w;h;levels;waterM;FluidDef'
            return 'BASIN cells=25 dug=25 filled=25 refused=0 maxDepth=2'
        if method == 'ProofMeltLedger':
            return ';'.join(str(v) for v in g['ledger'])
        raise AssertionError('unexpected static %s' % method)


def run(mod='ice', fault=None):
    F = Fake(mod, fault)
    out = C.scene_ice(F, lambda: F.save('begin'), lambda: F.load('begin'), {'calls': []})
    return {r['id']: r['status'] for r in out['rows']}, out, F


FAILS = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else why))
    if not ok:
        FAILS.append(label)


CUT, MELT, CTRL = 'ICE_cut_leaves_crushed_ice', 'ICE_melts_back_into_pond', 'ICE_control_unfrozen_cut_no_crushed_ice'
rows, out, F = run()
check('every staging call keeps its tool contract (no ProofStageBasin verb, cuts designated before ordered)', not F.contract,
      F.contract)
check('the scene orders real cuts (both ponds deepened)', len([o for o in out['calls'] if o['tool'] == 'jawa/ordered_job']) == 2,
      [c['tool'] for c in out['calls']][:40])
check('healthy fake (frozen cut leaves crushed ice, it thaws to 10,000 dL): every row PASS',
      out['status'] == 'PASS' and all(rows.get(r) == 'PASS' for r in (CUT, MELT, CTRL)), rows)
r, o, _ = run(mod=None)
check("no crushed ice from a frozen cut: the cut FAILs, the melt UNMEASURED (never PASS), the control PASS",
      r.get(CUT) == 'FAIL' and r.get(MELT) == 'UNMEASURED' and r.get(CTRL) == 'PASS' and o['status'] != 'PASS', r)
r, o, _ = run(mod='always')
check('crushed ice on every cut: the control FAILs', r.get(CTRL) == 'FAIL', r)
r, o, _ = run(fault='thaw')
check('the ice gone before the cut lands: the cut and the melt UNMEASURED, none PASS',
      r.get(CUT) == 'UNMEASURED' and r.get(MELT) == 'UNMEASURED', r)
r, o, _ = run(fault='cold')
check('a site that never gets above 0 C: the melt UNMEASURED, the cut still judged', r.get(MELT) == 'UNMEASURED'
      and r.get(CUT) == 'PASS', r)
r, o, _ = run(fault='nomelt')
check('warm, the pile never melts: the melt FAILs', r.get(MELT) == 'FAIL', r)
r, o, _ = run(fault='refuse')
check('the work giver refuses the frozen square: the cut FAILs (MOD), the melt UNMEASURED',
      r.get(CUT) == 'FAIL' and [x for x in o['rows'] if x['id'] == CUT][0]['kind'] == 'MOD' and r.get(MELT) == 'UNMEASURED', r)
print('selftest_ice_scene: %s' % ('FAIL' if FAILS else 'ok'))
sys.exit(1 if FAILS else 0)
