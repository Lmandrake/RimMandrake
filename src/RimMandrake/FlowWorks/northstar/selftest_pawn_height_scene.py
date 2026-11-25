#!/usr/bin/env python3
"""Offline half of sc_pawn_height: scene_pawn_height against a fake map that models the shipped sink.

Since RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES the scene gives ONE order over five pads (D0..D4) and ONE
order back, and reads the sink every tick (it gave 46 one-cell orders before). The fake walks an ordered pawn one cell every
STEP_T ticks along x, sets its Position when a step ends, and draws a walking pawn's sink between the two cells of its step,
as RM_Patch_PitDepthDrawOffset.SinkOf does; a pawn standing still sinks by min(depth, 8) x 0.05, clamped to the room above
its column's south lip (RM_PitDrawMath.ClampSinkToLip: visit 1, 2026-11-15, dug one-row pads and read 17 clamped zeros).
ProofSwim reads deepCell for a pawn in >= 1.8 m of water and exhaustion that grows while it swims.
  healthy            every row PASS
  fault='flat'       the sink never applies -> the offset row UNMEASURED (an all-zero read), the control UNMEASURED
  fault='grows'      the sink stops deepening past D3 -> the offset row FAILs
  fault='oneway'     the walk back reads a different sink -> the offset row FAILs
  fault='stuck'      the pawn never leaves the ground -> the offset row UNMEASURED (unreached pads), never PASS
  fault='detour'     the path goes round the pads on the row north of them (no wall there) -> UNMEASURED, never PASS
  fault='noswim'     2 m of water and no swim -> the swim row FAILs
  fault='notire'     swims, exhaustion never rises -> the swim row FAILs
  fault='dryswim'    the pool holds no water -> the swim row UNMEASURED
  fault='stepsink'   a walking pawn sinks on undug ground -> the control FAILs
The fake proves the scene's logic, never the game; the live half is
`python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_pawn_height --out <json>`.
    python3 selftest_pawn_height_scene.py [path/to/concept_scenes.py]
"""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (HERE, ROOT / 'src/RimMandrake/Utils', ROOT / 'src/RimMandrake/Utils/modcheck'):
    sys.path.insert(0, str(p))
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'concept_scenes.py'
spec = importlib.util.spec_from_file_location('concept_scenes_under_test', SRC)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
PER, CAP, DL_PER_M, STEP_T = 0.05, 8, 20000, 13


class Fake:
    def __init__(self, fault=None):
        self.fault = fault
        self.g = {'d': {}, 'dl': {}, 'pawns': {}, 'ex': {}, 'n': 0, 'tick': 0, 'back': False, 'walk': {}, 'walls': set(),
                  'drafted': set()}
        self.saves, self.contract = {}, []

    def save(self, k):
        self.saves[k] = deepcopy(self.g)

    def load(self, k):
        self.g = deepcopy(self.saves[k])

    def ticks(self, n):
        g = self.g
        for _ in range(n):
            g['tick'] += 1
            for pid, w in list(g['walk'].items()):
                w['k'] += 1
                if w['k'] >= STEP_T:
                    g['pawns'][pid] = w['path'].pop(0)
                    w['k'] = 0
                    if not w['path']:
                        del g['walk'][pid]
            for pid, c in g['pawns'].items():
                if self.swims(c) and self.fault != 'notire':
                    g['ex'][pid] = min(1.0, g['ex'].get(pid, 0.0) + 1 / 5000.0)
        return {'success': True, 'advanced': n}

    def water_m(self, c):
        return self.g['dl'].get(c, 0) / DL_PER_M

    def swims(self, c):
        return self.water_m(c) >= 1.8 and self.fault != 'noswim'

    def still_sink(self, c):
        d = self.g['d'].get(c, 0)
        if self.fault == 'flat' or d <= 0:
            return 0.0
        s = (min(d, 3) if self.fault == 'grows' else min(d, CAP)) * PER
        if self.fault == 'oneway' and self.g['back']:
            s += 0.02
        room, k = 0, 1                                     # rows of the same-or-deeper hole south of this one
        while self.g['d'].get((c[0], c[1] - k), 0) >= d:
            room, k = room + 1, k + 1
        return min(s, float(room))

    def sink(self, pid):
        g, c = self.g, self.g['pawns'][pid]
        w = g['walk'].get(pid)
        if not w:
            return self.still_sink(c)
        nxt = w['path'][0]
        if g['d'].get(c, 0) == 0 and g['d'].get(nxt, 0) == 0:
            return 0.3 if self.fault == 'stepsink' else 0.0
        a, b = self.still_sink(c), self.still_sink(nxt)
        return a + (b - a) * w['k'] / float(STEP_T)

    def path(self, at, to):
        """Straight along x on the pawn's row, then along z; 'detour' walks the row north of the pads (walls ignored)."""
        out, (x, z) = [], at
        if self.fault == 'detour':
            out.append((x, z + 1)); z += 1
        while x != to[0]:
            x += 1 if to[0] > x else -1
            if (x, z) in self.g['walls'] and self.fault != 'detour':
                self.contract.append('path through a wall at %s' % ((x, z),))
            out.append((x, z))
        while z != to[1]:
            z += 1 if to[1] > z else -1
            out.append((x, z))
        return out

    def call(self, tool, **kw):
        g = self.g
        if tool == 'jawa/flowworks_excavation_drive':
            c = (kw['x'], kw['z'])
            g['d'][c] = g['d'].get(c, 0) + kw['deepenLevels']
            return {'success': True, 'depth': g['d'][c]}
        if tool == 'jawa/flowworks_excavation_rect':
            rows = [{'x': kw['x'] + i, 'z': kw['z'] + j, 'd': g['d'].get((kw['x'] + i, kw['z'] + j), 0),
                     'dl': g['dl'].get((kw['x'] + i, kw['z'] + j), 0)} for i in range(kw['w']) for j in range(kw['h'])]
            return {'success': True, 'rows': rows}
        if tool == 'jawa/mod_settings_field':
            return {'success': True, 'value': None}
        if tool == 'jawa/flowworks_pulse':
            return {'success': True}
        if tool == 'jawa/build_batch':
            for op in kw['ops'].split(';'):
                d, xz = op.split(':')
                if d != 'Wall' or kw.get('stuff') != 'Steel':
                    self.contract.append('build_batch %s' % op)
                g['walls'].add(tuple(int(v) for v in xz.split(',')))
            return {'success': True}
        if tool == 'jawa/set_draft':
            g['drafted'].add(kw['pawnId'])
            return {'success': True}
        if tool == 'jawa/spawn_pawn':
            if kw.get('kindDef') != 'Colonist' or kw.get('count') != 1:
                self.contract.append('spawn_pawn %s' % kw)
            g['n'] += 1
            pid = 'Human%d' % (900 + g['n'])
            g['pawns'][pid] = (kw['x'], kw['z'])
            return {'success': True, 'pawns': [{'id': pid}]}
        if tool == 'jawa/order_pawn':
            pid, to = kw['pawnId'], (kw['x'], kw['z'])
            if pid not in g['pawns']:
                return {'success': False, 'message': 'no pawn %s' % pid}
            if kw.get('waitTicks') != 0:
                self.contract.append('order_pawn waitTicks %s: the scene reads every tick itself' % kw.get('waitTicks'))
            at = g['pawns'][pid]
            if to[0] < at[0]:
                g['back'] = True
            if self.fault == 'stuck' or self.water_m(at) > 0:
                return {'success': True, 'accepted': True}
            pth = self.path(at, to)
            if pth:
                g['walk'][pid] = {'path': pth, 'k': 0}
            return {'success': True, 'accepted': True}
        if tool == 'jawa/destroy_batch':
            return {'success': True, 'destroyed': 0}
        if tool == 'jawa/static_call':
            return {'success': True, 'result': self.static(kw['method'], kw.get('args', ''))}
        raise AssertionError('unexpected tool %s %s' % (tool, kw))

    def static(self, method, arg):
        g = self.g
        if method == 'ProofFillWithFluid':
            x, z, m, _f = arg.split(',')
            c = (int(x), int(z))
            if not g['d'].get(c):
                return 'REFUSED: not excavated'
            if self.fault != 'dryswim':
                g['dl'][c] = int(min(float(m), g['d'][c] * 0.5) * DL_PER_M)
            return 'FILLED (%s, 0, %s) W=%ddL' % (x, z, g['dl'].get(c, 0))
        if method == 'ProofPawnSink':
            if arg not in g['pawns']:
                return 'REFUSED: no spawned pawn ' + arg
            c = g['pawns'][arg]
            s = self.sink(arg)
            return ('SINK id=%s cell=%d,%d depth=%d waterDl=%d fluid=none sink=%g drawDz=%g moving=%s wallOverHead=0 '
                    'enabled=True' % (arg, c[0], c[1], g['d'].get(c, 0), g['dl'].get(c, 0), round(s, 4), -round(s, 4),
                                      arg in g['walk']))
        if method == 'ProofSwim':
            parts = arg.split(',')
            if len(parts) != 2:
                self.contract.append('ProofSwim given %r (its contract is x,z)' % arg)
                return 'REFUSED: arg must be x,z on a current map'
            c = (int(parts[0]), int(parts[1]))
            for pid, at in g['pawns'].items():
                if at == c:
                    return ('SWIM %s class=Swimmer natural=False load=0.00 enduranceH=2.00 costX=1.00 water=%.2f deepCell=%s '
                            'pathCost=0 liquidOk=True exhaustion=%.3f headUp=True'
                            % (pid, self.water_m(c), self.swims(c), g['ex'].get(pid, 0.0)))
            return 'REFUSED: no pawn at (%d, 0, %d)' % c
        if method == 'ProofReadout':
            x, z = (int(v) for v in arg.split(','))
            d, w = g['d'].get((x, z), 0), self.water_m((x, z))
            return 'OK Hole %g m' % (d * 0.5) + (' · Water %.2f m (%s L)' % (w, format(int(w * 1000), ',')) if w else '')
        raise AssertionError('unexpected static %s' % method)


def run(fault=None):
    F = Fake(fault)
    out = C.scene_pawn_height(F, lambda: F.save('begin'), lambda: F.load('begin'), {'calls': []})
    return {r['id']: r['status'] for r in out['rows']}, out, F


FAILS = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else why))
    if not ok:
        FAILS.append(label)


OFF, SWIM, CTRL = 'PH_offset_follows_depth', 'PH_swims_and_tires_at_2m', 'PH_control_undug_no_offset'
rows, out, F = run()
check('every staging call keeps its tool contract (one colonist per spawn; ProofSwim x,z; walls; orders read per tick)',
      not F.contract, F.contract)
check('healthy fake (sink by depth, drawn between the cells of a step, same both ways; swims and tires at 2 m): every row '
      'PASS', out['status'] == 'PASS' and all(rows.get(r) == 'PASS' for r in (OFF, SWIM, CTRL)), rows)
orders = [c for c in out['calls'] if c['tool'] == 'jawa/order_pawn']
check('one order over the pads and one back (it was 46 orders of one cell each)', len(orders) == 2, len(orders))
reads = [c for c in out['calls'] if c['tool'] == 'jawa/static_call' and c['args'][1] == 'ProofPawnSink']
check('the sink is read every tick of both orders (2 x 6 cells x %d ticks at least)' % STEP_T,
      len(reads) >= 2 * 6 * STEP_T, len(reads))
r, o, _ = run('flat')
check('a sink that never applies: the offset row UNMEASURED, never PASS; the control cannot rule anything out',
      r.get(OFF) == 'UNMEASURED' and r.get(CTRL) == 'UNMEASURED' and o['status'] != 'PASS', r)
for fault, label in (('grows', 'a sink that stops deepening past D3'), ('oneway', 'the walk back reads a different sink')):
    r, o, _ = run(fault)
    check('%s: the offset row FAILs' % label, r.get(OFF) == 'FAIL', r)
for fault, label in (('stuck', 'a pawn that never leaves the ground'), ('detour', 'a path round the pads')):
    r, o, _ = run(fault)
    check('%s: the offset row UNMEASURED, never PASS' % label, r.get(OFF) == 'UNMEASURED' and o['status'] != 'PASS', r)
r, o, _ = run('noswim')
check('2 m of water and no swim: the swim row FAILs', r.get(SWIM) == 'FAIL', r)
r, o, _ = run('notire')
check('swims, never tires: the swim row FAILs', r.get(SWIM) == 'FAIL', r)
r, o, _ = run('dryswim')
check('a pool that holds no water: the swim row UNMEASURED, never PASS', r.get(SWIM) == 'UNMEASURED', r)
r, o, _ = run('stepsink')
check('a walking pawn sinking on undug ground: the control FAILs', r.get(CTRL) == 'FAIL', r)
print('selftest_pawn_height_scene: %s' % ('FAIL' if FAILS else 'ok'))
sys.exit(1 if FAILS else 0)
