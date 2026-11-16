#!/usr/bin/env python3
"""Offline half of sc_hose_look (RIMMANDRAKE_REBUILD_FLOWWORKS_HOSE_SCENE_PUMP_HAD_NO_SOURCE): scene_hose_look against a
fake map that holds each staging call to its bridge tool's contract and models what sank visit 1 (2026-11-15):
  - a pump runs only when powered (a charged battery in the plot, ~120 ticks after build, the way vanilla's power net
    switches a new consumer on), with water in a dug cell beside it, and a hose laid from a reel touching it to a cell
    beside the far tank; the draft's bare spawn_batch pump and reel had none of these, so it never ran;
  - a hose goes Plump ~60 ticks after liquid first moves through it and Flat ~530 ticks after the last move; its tint is
    the liquid it carries; the far tank gains 10,000 units a 250-tick pump cycle.
Planted faults, each must turn its row FAIL (never PASS, never UNMEASURED): PLUMP_ON_LAY (the look keyed to the lay, the
control's foil), NEVER_PLUMPS, STAYS_PLUMP_AFTER_CUT, TINT_WRONG. Vacuous worlds must read UNMEASURED: a census that
lists no hose, a pump that never powers. Red on the draft at 2b4bffe212, green on the fix. The fake proves the scene's
logic, never the game; the live half is
`python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_hose_look --out <json>`.
    python3 selftest_hose_look_scene.py [path/to/concept_scenes.py]
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
import validation_core as V  # noqa: E402

NSP, HPROBE = 'RimMandrake.FlowWorks.RM_NorthstarProofs', 'RimMandrake.FlowWorks.Hose.HoseProbe'
SIZE = {'RM_LiquidTank': (2, 2), 'RM_HoseReel': (2, 2), 'Battery': (1, 2), 'RM_LiquidPump': (1, 1)}
OP = re.compile(r'^(\w+):(-?\d+),(-?\d+)(?:,([0-3]))?$')
OP_RECT = re.compile(r'^(\w+):(-?\d+),(-?\d+),(\d+),(\d+)$')
RECT = re.compile(r'^(-?\d+),(-?\d+),(\d+),(\d+)$')
WATER = 'RM_Liquid_FreshWater'


def n4(c):
    return [(c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)]


class Fake:
    def __init__(self, fault=None):
        self.fault = fault
        self.g = {'t': 1000, 'b': {}, 'dug': {}, 'n': 0, 'hose': None, 'flow_t': None, 'tank': 0, 'built_t': {}, 'charged': set()}
        self.saves, self.contract = {}, []

    def save(self, k):
        self.saves[k] = deepcopy(self.g)

    def load(self, k):
        self.g = deepcopy(self.saves[k])

    def bad(self, why):
        self.contract.append(why)
        return {'success': False, 'message': why}

    # ---- geometry
    def of(self, d):
        return [(k, b) for k, b in self.g['b'].items() if b['def'] == d]

    def at(self, cell, d=None):
        return next((k for k, b in self.g['b'].items() if cell in b['cells'] and (d is None or b['def'] == d)), None)

    def powered(self):
        if self.fault == 'no_power':
            return False
        return any(k in self.g['charged'] and self.g['t'] - self.g['built_t'][k] >= 120 for k, _ in self.of('Battery'))

    def running(self):
        """Powered, water beside the pump, a laid hose from a reel touching the pump to a cell touching the far tank."""
        g, pumps = self.g, self.of('RM_LiquidPump')
        if not pumps or not self.powered() or not g['hose']:
            return False
        pc = pumps[0][1]['cells'][0]
        wet = any(g['dug'].get(c, (0, 0))[0] >= 1 and g['dug'][c][1] > 0 for c in n4(pc))
        reel = g['b'].get(g['hose']['reel'])
        coupled = reel is not None and any(c in reel['cells'] for c in n4(pc))
        reaches = any(g['hose']['end'] in n4(c) for _, t in self.of('RM_LiquidTank') for c in t['cells'])
        return wet and coupled and reaches

    def state(self):
        g = self.g
        if not g['hose']:
            return None
        if self.fault == 'PLUMP_ON_LAY':
            return 'Plump'
        if self.fault == 'NEVER_PLUMPS':
            return 'Flat'
        if g['flow_t'] is None:
            return 'Flat'
        on_since, last = g['flow_t']
        if self.fault == 'STAYS_PLUMP_AFTER_CUT':
            return 'Plump' if g['t'] - on_since >= 60 else 'Flat'
        return 'Plump' if g['t'] - on_since >= 60 and g['t'] - last <= 530 else 'Flat'

    # ---- the clock
    def ticks(self, n):
        g = self.g
        for _ in range(n):
            g['t'] += 1
            if self.running():
                g['flow_t'] = (g['flow_t'][0] if g['flow_t'] and g['t'] - g['flow_t'][1] <= 530 else g['t'], g['t'])
                if g['t'] % 250 == 0:
                    g['tank'] += 10000
        return {'success': True}

    # ---- the bridge
    def call(self, tool, _answer=False, **kw):
        g = self.g
        if tool == 'jawa/build_batch':
            if kw.get('faction') != 'player':
                return self.bad('build_batch faction %r' % kw.get('faction'))
            out = 0
            for op in kw['ops'].split(';'):
                m = OP.match(op)
                if not m or m.group(1) not in SIZE:
                    return self.bad('build_batch op %r' % op)
                d, x, z, rot = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4) or 0)
                w, h = SIZE[d]
                if d == 'RM_HoseReel':                       # Position -> footprint corner, as V.reel_pos does it
                    sx, sz = V.REEL_POS_SHIFT[rot]
                    x, z = x - sx, z - sz
                cells = [(x + i, z + j) for i in range(w) for j in range(h)]
                if any(self.at(c) for c in cells):
                    continue
                g['n'] += 1
                key = '%s%d' % (d, g['n'])
                g['b'][key] = {'def': d, 'cells': cells, 'pos': (int(m.group(2)), int(m.group(3)))}
                g['built_t'][key] = g['t']
                out += 1
            return {'success': True, 'placed': out, 'survived': out}
        if tool == 'jawa/spawn_batch':                       # the draft's spawn: no power, no source, no hose
            return self.call('jawa/build_batch', ops=kw['ops'], faction='player')
        if tool in ('jawa/set_terrain_batch', 'jawa/set_roof_batch'):
            return {'success': True} if all(OP_RECT.match(op) for op in kw['ops'].split(';')) else self.bad('%s ops' % tool)
        if tool == 'jawa/destroy_batch':
            m = RECT.match(kw.get('rects', ''))
            if not m:
                return self.bad('destroy rects %r' % kw.get('rects'))
            x, z, w, h = (int(v) for v in m.groups())
            gone = [k for k, b in g['b'].items() if any(x <= c[0] < x + w and z <= c[1] < z + h for c in b['cells'])]
            for k in gone:
                del g['b'][k]
            if g['hose'] and g['hose']['reel'] in gone:
                g['hose'] = None
            return {'success': True, 'destroyed': len(gone)}
        if tool == 'jawa/flowworks_excavation_drive':
            if not all(isinstance(kw.get(k), (int, float)) for k in ('x', 'z', 'deepenLevels', 'setBodyWaterM')):
                return self.bad('excavation_drive args %r' % kw)
            c = (kw['x'], kw['z'])
            lv, w = g['dug'].get(c, (0, 0.0))
            lv += kw['deepenLevels']
            if kw['setBodyWaterM'] >= 0:
                if lv < 1:
                    return self.bad('water set on an undug cell %s' % (c,))
                w = kw['setBodyWaterM']
            g['dug'][c] = (lv, w)
            return {'success': True}
        if tool == 'jawa/list_things':
            m = RECT.match(kw.get('rect', ''))
            if not m:
                return self.bad('list_things rect %r' % kw.get('rect'))
            x, z, w, h = (int(v) for v in m.groups())
            hits = [k for k, b in self.of(kw['defName']) if any(x <= c[0] < x + w and z <= c[1] < z + h for c in b['cells'])]
            return {'success': True, 'things': [{'id': k} for k in hits]}
        if tool == 'jawa/battery_set':
            if kw.get('thing') not in g['b'] or kw.get('mode') != 'setPct':
                return self.bad('battery_set %r' % kw)
            g['charged'].add(kw['thing'])
            return {'success': True}
        if tool in ('rimworld/screenshot_cell_rect', 'jawa/weather_set'):
            return {'success': True}
        if tool == 'jawa/static_call':
            if (kw.get('type'), kw.get('method')) == (NSP, 'ProofPump'):
                cell = tuple(int(v) for v in kw['args'].split(';')[0].split(','))
                if not self.at(cell, 'RM_LiquidPump'):
                    return {'success': True, 'result': 'REFUSED: no RM_LiquidPump at %s' % (cell,)}
                return {'success': True, 'result': 'PUMP running=%s moved=0 pour=False tank=none' % self.running()}
            return self.bad('unmodelled static %s.%s' % (kw.get('type'), kw.get('method')))
        return self.bad('unmodelled tool %s' % tool)

    def probe_of(self, typ, cmd, wait_s=20.0, poll_s=0.3, answer=False):
        g = self.g
        if typ != HPROBE:
            return self.bad('probe type %s' % typ)
        if cmd == 'census':
            if self.fault == 'no_census' or not g['hose']:
                return {'success': True, 'cmd': 'census', 'tick': g['t'], 'hoses': []}
            reel = g['b'][g['hose']['reel']]
            return {'success': True, 'cmd': 'census', 'tick': g['t'], 'hoses': [
                {'id': 1, 'reel': list(reel['pos']), 'state': self.state(), 'carry': 'Laid',
                 'tintLiquid': ('RM_Liquid_Chemfuel' if self.fault == 'TINT_WRONG' else WATER) if g['flow_t'] else None,
                 'netLink': 'tank' if self.running() else None}]}
        m = re.match(r'^(lay|pump|tank):(-?\d+),(-?\d+)(?:,(-?\d+),(-?\d+))?$', cmd)
        if not m:
            return self.bad('probe verb %r' % cmd)
        verb, cell = m.group(1), (int(m.group(2)), int(m.group(3)))
        if verb == 'lay':
            reel = self.at(cell, 'RM_HoseReel')
            if reel is None or m.group(4) is None:
                return self.bad('lay with no reel at %s' % (cell,))
            g['hose'] = {'reel': reel, 'end': (int(m.group(4)), int(m.group(5)))}
            return {'success': True, 'cmd': cmd, 'reason': None, 'layOk': True}
        if verb == 'pump':
            if not self.at(cell, 'RM_LiquidPump'):
                return {'success': False, 'cmd': cmd, 'error': 'no pump there'}
            return {'success': True, 'cmd': cmd, 'powered': self.powered(), 'tick': g['t']}
        if not self.at(cell, 'RM_LiquidTank'):
            return {'success': False, 'cmd': cmd, 'error': 'no tank there'}
        return {'success': True, 'cmd': cmd, 'liquid': WATER if g['tank'] else None, 'units': g['tank'], 'tick': g['t']}


def run(fault=None):
    f = Fake(fault)
    res = {'calls': []}
    try:
        out = C.scene_hose_look(f, lambda: f.save('begin'), lambda: f.load('begin'), res)
    except Exception as e:                        # noqa: BLE001
        return {'error': repr(e)[:200], 'rows': {}}, f
    return {'rows': {r['id']: r['status'] for r in out['rows']}, 'detail': {r['id']: r['detail'] for r in out['rows']}}, f


ROWS = ('HOSE_plump_when_flowing', 'HOSE_tinted_carried_liquid', 'HOSE_flat_when_not', 'HOSE_control_unpowered_stays_flat')
PLANTS = {'PLUMP_ON_LAY': 'HOSE_control_unpowered_stays_flat', 'NEVER_PLUMPS': 'HOSE_plump_when_flowing',
          'STAYS_PLUMP_AFTER_CUT': 'HOSE_flat_when_not', 'TINT_WRONG': 'HOSE_tinted_carried_liquid'}
FAILS = []


def check(ok, what):
    print('%s  %s' % ('ok  ' if ok else 'FAIL', what))
    if not ok:
        FAILS.append(what)


def main():
    healthy, f = run()
    check(not f.contract, 'every staging call keeps its tool contract %s' % f.contract[:3])
    check(all(healthy['rows'].get(r) == 'PASS' for r in ROWS) and set(healthy['rows']) == set(ROWS),
          'healthy plot: every row PASS %s' % (healthy.get('error') or healthy['rows']))
    for plant, rid in sorted(PLANTS.items()):
        got, _ = run(plant)
        check(got['rows'].get(rid) == 'FAIL', 'planted %s turns %s FAIL (got %s)' % (plant, rid, got['rows'].get(rid)))
    for world in ('no_census', 'no_power'):
        got, _ = run(world)
        check(got['rows'] and not any(v == 'PASS' for v in got['rows'].values()),
              '%s: no row PASSes on a vacuous read %s' % (world, got.get('error') or got['rows']))
    print('selftest_hose_look_scene: %s' % ('ok' if not FAILS else 'FAIL (%d)' % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
