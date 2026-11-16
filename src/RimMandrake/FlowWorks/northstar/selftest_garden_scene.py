#!/usr/bin/env python3
"""Offline half of sc_garden (RIMMANDRAKE_REBUILD_FLOWWORKS_GARDEN_SCENE_MACHINES_NEVER_PIPED): scene_garden against a fake
map that holds each staging call to its bridge tool's contract and models what sank visit 1 (2026-11-15):
  - a machine is on a net only through pipe: pipe cells joined 4-way, a building ON a pipe cell joins it, a tank touching
    one joins it (sprinkler_live.py's measured layout); a head pulses every 2,500 ticks and sprays only with a pump on its
    net (cells x 5 units from the net's tanks), so the draft's side-by-side spawn never filled or drew anything;
  - the governor: a colonist's Food falls 0.15 a 2,500 ticks and safe_advance raises GovernorStop('starving') under 0.05,
    so one unfed 60,000-tick advance stops (the draft stopped at tick 480);
  - the converters (CompLiquidConverter.CompTickRare's budget, one candidate), the still's sun, the drill's pending charge
    (Building_LiquidDrill.TickRare), the walled yard's sheet, a thirsty colonist drinking at a faucet.
Planted faults, each must turn its row FAIL (never PASS, never UNMEASURED): CALLER_CONV_DROPS_CLIPPED, CALLER_SPR_SPRAYS_
WITHOUT_PUMP, DEF_STILL_RATE_TENFOLD, DRILL_CHARGES_WHOLE_LEVEL, SHEET_DRY_ISLAND. Vacuous worlds must read UNMEASURED: no
sun (the still never ran), colonists that starve even fed (the window breaks). Red on the draft at 2b4bffe212, green on the
fix. The fake proves the scene's logic, never the game; the live half is
`python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_garden --out <json>`.
    python3 selftest_garden_scene.py [path/to/concept_scenes.py]
"""
from copy import deepcopy
import importlib.util
import math
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

SIZE2 = {'RM_LiquidTank': 160000, 'RM_LiquidTankTall': 320000, 'RM_SunPanStill': 0, 'RM_LiquidDrill': 0}
DEFS = set(SIZE2) | {'RM_UniversalPipe', 'RM_LiquidPump', 'RM_SprinklerHead', 'RM_PipeFaucet', 'RM_DripFilter',
                     'PowerConduit', 'Battery', 'Wall'}
CONV = {'RM_DripFilter': ('RM_Liquid_ToxicWater', 4800, 6000, 2000), 'RM_SunPanStill': ('RM_Liquid_SaltWater', 6000, 4000, 2000)}
OP_XZ = re.compile(r'^(\w+):(-?\d+),(-?\d+)(?:,([0-3]))?$')
OP_RECT = re.compile(r'^(\w+):(-?\d+),(-?\d+),(\d+),(\d+)$')
NSP, SHEET = 'RimMandrake.FlowWorks.RM_NorthstarProofs', 'RimMandrake.FlowWorks.Sheet.RM_SheetProofs'


class GovernorStop(Exception):
    pass


class Fake:
    def __init__(self, fault=None):
        self.fault = fault
        self.g = {'t': 1000, 'b': {}, 'pipes': set(), 'tanks': {}, 'dug': {}, 'pawns': {'Col1': [0.4, 0.9], 'Col2': [0.4, 0.9]},
                  'set': {}, 'conv': {}, 'drill': None, 'yield': None, 'spill': None, 'heads': {}, 'drinks': 0}
        self.saves, self.contract = {}, []

    def save(self, k):
        self.saves[k] = deepcopy(self.g)

    def load(self, k):
        self.g = deepcopy(self.saves[k])

    def bad(self, why):
        self.contract.append(why)
        return {'success': False, 'message': why}

    # ---- geometry
    def foot(self, d, x, z):
        return [(x + i, z + j) for i in range(2) for j in range(2)] if d in SIZE2 else [(x, z)]

    def at(self, cell):
        return [(k, b) for k, b in self.g['b'].items() if cell in b['cells']]

    def net(self, key):
        """The pipe component a building is on (frozenset of pipe cells), or None."""
        b = self.g['b'][key]
        seeds = [c for c in b['cells'] if c in self.g['pipes']]
        if not seeds and b['def'] in ('RM_LiquidTank', 'RM_LiquidTankTall'):
            seeds = [(x + dx, z + dz) for x, z in b['cells'] for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
                     if (x + dx, z + dz) in self.g['pipes']]
        if not seeds:
            return None
        seen, todo = set(), list(seeds[:1])
        while todo:
            c = todo.pop()
            if c in seen or c not in self.g['pipes']:
                continue
            seen.add(c)
            todo += [(c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)]
        return frozenset(seen)

    def members(self, net, d=None):
        return [k for k, b in self.g['b'].items() if net is not None and self.net(k) == net and (d is None or b['def'] == d)]

    def tanks_on(self, key):
        n = self.net(key)
        return [k for k in self.members(n) if k in self.g['tanks']]

    # ---- the clock and the governor
    def ticks(self, n):
        g = self.g
        for _ in range(n // 250):
            g['t'] += 250
            for p in g['pawns'].values():
                p[0] -= 0.015
                if p[0] < 0.05:
                    raise GovernorStop('safe_advance stopped: starving: food category Starving')
            self.rare()
        return {'success': True}

    def sun(self):
        return 0.0 if self.fault == 'night' else max(0.0, math.sin(2 * math.pi * (self.g['t'] % 60000) / 60000.0))

    def draw(self, tanks, liquid, units):
        have = sum(self.g['tanks'][k][1] for k in tanks if self.g['tanks'][k][0] == liquid)
        if have < units:
            return False
        for k in tanks:
            t = self.g['tanks'][k]
            if t[0] == liquid:
                take = min(t[1], units)
                t[1] -= take
                units -= take
                if t[1] == 0:
                    t[0] = None
        return True

    def rare(self):
        g = self.g
        for k, b in list(g['b'].items()):
            d = b['def']
            if d == 'RM_SprinklerHead' and (g['t'] - b['built']) % 2500 == 250:
                net = self.net(k)
                pressure = bool(self.members(net, 'RM_LiquidPump')) or self.fault == 'CALLER_SPR_SPRAYS_WITHOUT_PUMP'
                if not pressure:
                    g['heads'][k] = 'No pressure'
                elif self.draw(self.tanks_on(k), 'RM_Liquid_FreshWater', 25 * 5):
                    g['heads'][k] = 'Spraying: 25 cells'
                else:
                    g['heads'][k] = 'Dry: nothing in the tanks on this network'
            if d in CONV:
                self.convert(k, *CONV[d])
            if d == 'RM_PipeFaucet':
                for p in g['pawns'].values():
                    if p[1] < 0.3 and self.draw(self.tanks_on(k), 'RM_Liquid_FreshWater', 250):
                        p[1] = 1.0
            if d == 'RM_LiquidDrill':
                self.drill(k)
        for p in g['pawns'].values():
            p[1] = max(0.0, p[1] - 0.002)

    def convert(self, k, liquid, per_day, inp, out):
        g = self.g
        if k == 'RM_SunPanStill' or self.g['b'][k]['def'] == 'RM_SunPanStill':
            per_day = per_day * (10 if self.fault == 'DEF_STILL_RATE_TENFOLD' else 1)
            env = self.sun()
        else:
            env = 1.0
        if env <= 0:
            return
        per = per_day * 10 / 240.0 * float(g['set'].get('converterRateMultiplier', 1.0)) * env
        acc = g['conv'].get(k, 0.0) + per
        tanks = self.tanks_on(k)
        src = [t for t in tanks if g['tanks'][t][0] == liquid]
        if not src:
            g['conv'][k] = min(acc, per + 1)
            return
        cap = min(acc, per + inp if per > inp else inp)
        clipped = max(0.0, min(acc - cap, per))
        acc = cap
        n = int(acc // inp)
        have = sum(g['tanks'][t][1] for t in src)
        n = min(n, have // inp)
        dst = [t for t in tanks if g['tanks'][t][0] in (None, 'RM_Liquid_FreshWater') and t not in src]
        room = sum(g['tanks'][t][2] - g['tanks'][t][1] for t in dst)
        n = min(n, room // out)
        if n > 0:
            self.draw(src, liquid, n * inp)
            left = n * out
            for t in dst:
                put = min(left, g['tanks'][t][2] - g['tanks'][t][1])
                if put:
                    g['tanks'][t][0], g['tanks'][t][1] = 'RM_Liquid_FreshWater', g['tanks'][t][1] + put
                    left -= put
            acc -= n * inp
            acc += 0.0 if self.fault == 'CALLER_CONV_DROPS_CLIPPED' else clipped
        g['conv'][k] = acc

    def outlet(self, k):
        x, z = self.g['b'][k]['at']
        return (x, z + 2)

    def drill(self, k):
        g = self.g
        o = self.outlet(k)
        d = g['drill']
        if g['yield'] is None or o not in g['dug']:
            return
        lv, water = g['dug'][o]
        room = lv - water
        if room <= 0:
            return
        per = max(0.05, float(g['set'].get('drillUnitsPerCycle', 1.0)))
        if d['pending'] < room:
            want = max(0.0, min(room - d['pending'], per))
            got = min(want, g['yield'][1])
            g['yield'][1] -= got
            d['pending'] += got
        add = min(room, d['pending'])
        if add <= 0:
            return
        g['dug'][o] = (lv, water + add)
        d['pending'] -= math.ceil(add) if self.fault == 'DRILL_CHARGES_WHOLE_LEVEL' else add

    # ---- the bridge
    def call(self, tool, **kw):
        g = self.g
        if tool == 'jawa/build_batch':
            out = 0
            for op in kw['ops'].split(';'):
                m = OP_XZ.match(op)
                if not m or m.group(1) not in DEFS:
                    return self.bad('build_batch op %r' % op)
                d, x, z = m.group(1), int(m.group(2)), int(m.group(3))
                if d == 'Wall' and not kw.get('stuff'):
                    return self.bad('Wall needs stuff')
                if d == 'RM_UniversalPipe':
                    g['pipes'].add((x, z))
                    continue
                key = '%s%d' % (d, len(g['b']))
                g['b'][key] = {'def': d, 'at': (x, z), 'cells': self.foot(d, x, z), 'built': g['t']}
                if d in ('RM_LiquidTank', 'RM_LiquidTankTall'):
                    g['tanks'][key] = [None, 0, SIZE2[d]]
                if d == 'RM_LiquidDrill':
                    g['drill'] = {'key': key, 'pending': 0.0}
                out += 1
            return {'success': True, 'survived': out}
        if tool == 'jawa/spawn_batch':                # the draft's spawn: same 'Def:x,z' grammar, no pipe laid unless named
            return self.call('jawa/build_batch', ops=kw['ops'], faction='player', stuff='Steel')
        if tool in ('jawa/set_terrain_batch', 'jawa/set_roof_batch', 'jawa/set_plants'):
            if not all(OP_RECT.match(op) for op in kw['ops'].split(';')):
                return self.bad('%s ops %r' % (tool, kw['ops']))
            return {'success': True}
        if tool == 'jawa/destroy_batch':
            return {'success': True} if re.match(r'^-?\d+,-?\d+,\d+,\d+$', kw['rects']) else self.bad('destroy rects')
        if tool in ('jawa/weather_set', 'jawa/gss_stage'):
            return {'success': True}
        if tool == 'jawa/mod_settings_field':
            if kw['action'] == 'set':
                g['set'][kw['field']] = kw['value']
                return {'success': True}
            return {'success': True, 'value': {'sheetOverflowEnabled': 'False', 'converterRateMultiplier': '1',
                                               'drillUnitsPerCycle': '1'}.get(kw['field'], 'True')}
        if tool == 'jawa/flowworks_excavation_drive':
            g['dug'][(kw['x'], kw['z'])] = (kw['deepenLevels'], 0.0)
            return {'success': True}
        if tool == 'jawa/spawn_pawn':
            pid = 'Col%d' % (len(g['pawns']) + 1)
            g['pawns'][pid] = [0.9, 0.9]
            return {'success': True, 'pawns': [{'id': pid}]}
        if tool == 'jawa/list_pawns':
            return {'success': True, 'pawns': [{'id': k} for k in g['pawns']]}
        if tool == 'jawa/pawn_need':
            p = g['pawns'].get(kw['pawn'])
            if p is None:
                return self.bad('pawn_need on unknown pawn %s' % kw['pawn'])
            if kw['action'] == 'list':
                return {'success': True, 'needs': [{'need': 'Food', 'level': p[0]}, {'need': 'RM_Thirst', 'level': p[1]}]}
            p[0 if kw['need'] == 'Food' else 1] = kw['level']
            return {'success': True}
        if tool == 'jawa/list_things':
            x, z, w, h = (int(v) for v in kw['rect'].split(','))
            hits = [k for k, b in g['b'].items() if b['def'] == kw['defName'] and any(
                x <= c[0] < x + w and z <= c[1] < z + h for c in b['cells'])]
            return {'success': True, 'things': [{'id': k} for k in hits]}
        if tool == 'jawa/inspect_string':
            return {'success': True, 'things': [{'inspect': [g['heads'].get(kw['thingIds'], 'Idle')]}]}
        if tool == 'jawa/static_call':
            return {'success': True, 'result': self.static(kw['type'], kw['method'], kw['args']), 'ticksGame': g['t']}
        return self.bad('unmodelled tool %s' % tool)

    def static(self, typ, method, arg):
        g = self.g
        if (typ, method) == (NSP, 'ProofTank'):
            a = arg.split(';')
            m = re.match(r'^(-?\d+),(-?\d+)$', a[0])
            if len(a) not in (2, 4) or not m or a[1] not in ('Store', 'Fill', 'Empty', 'Dump'):
                self.contract.append('ProofTank arg %r' % arg)
                return 'REFUSED: arg must be x,z;Mode or x,z;Mode;LiquidDef;units on the current map'
            hit = [k for k, _ in self.at((int(m.group(1)), int(m.group(2)))) if k in g['tanks']]
            if not hit:
                return 'REFUSED: no RM_LiquidTank at (%s)' % a[0]
            t = g['tanks'][hit[0]]
            if len(a) == 4:
                if int(a[3]) > t[2]:
                    return 'REFUSED: bad liquid/units (capacity %d)' % t[2]
                t[0], t[1] = (a[2] if int(a[3]) else None), int(a[3])
            return 'TANK mode=Store effective=Store liquid=%s units=%d' % (t[0] or 'none', t[1])
        if (typ, method) == (NSP, 'ProofDrill'):
            a = arg.split(';')
            d = g['drill']
            if len(a) not in (1, 3) or d is None or not any(k == d['key'] for k, _ in self.at(tuple(int(v) for v in a[0].split(',')))):
                return 'REFUSED: no RM_LiquidDrill at %s' % a[0]
            if len(a) == 3:
                g['yield'] = [a[1], float(a[2])]
            o = self.outlet(d['key'])
            return 'DRILL yield=%s reserve=%r pending=%r outletUnits=%r outlet=%d,%d block=None' % (
                g['yield'][0] if g['yield'] else 'none', g['yield'][1] if g['yield'] else 0.0, d['pending'],
                g['dug'].get(o, (0, 0.0))[1], o[0], o[1])
        if (typ, method) == (SHEET, 'ProofSheetSpill'):
            ok = g['set'].get('sheetOverflowEnabled') == 'True'
            dl = int(arg.split(';')[1])
            g['spill'] = (dl if ok else 0, arg.split(';')[0])
            return 'SPILL offered=%d accepted=%d' % (dl, dl if ok else 0)
        if (typ, method) == (SHEET, 'ProofSheetRect'):
            x, z = (int(v) for v in arg.split(';')[:2])
            dl = g['spill'][0] if g['spill'] else 0
            walls = sum(1 for b in g['b'].values() if b['def'] == 'Wall' and (b['at'][0] in (x - 1, x + 5) or b['at'][1] in (z - 1, z + 5)))
            if not dl:
                return 'SHEETRECT dl=0 wet=0 maxDl=0 edgeMaxDl=0 ice=0 film=0 sheet=0 pool=0'
            if walls < 24:
                dl //= 4                                 # an open yard: the sheet runs off the rect
            wet = 24 if self.fault == 'SHEET_DRY_ISLAND' else 25
            return 'SHEETRECT dl=%d wet=%d maxDl=%d edgeMaxDl=0 ice=0 film=0 sheet=%d pool=0' % (dl, wet, -(-dl // wet), wet)
        self.contract.append('unmodelled static %s.%s' % (typ, method))
        return 'REFUSED: unmodelled'


def run(fault=None):
    f = Fake(fault)
    res = {'calls': []}
    try:
        out = C.scene_garden(f, lambda: f.save('begin'), lambda: f.load('begin'), res)
    except Exception as e:                        # noqa: BLE001 - the draft lets a GovernorStop escape the scene
        return {'error': repr(e)[:200], 'rows': {}}, f
    return {'rows': {r['id']: r['status'] for r in out['rows']}, 'detail': {r['id']: r['detail'] for r in out['rows']}}, f


ROWS = ('GARDEN_head_draws_its_net', 'GARDEN_no_pump_no_spray', 'GARDEN_faucet_drinks_from_its_tank',
        'GARDEN_filter_keeps_its_rate', 'GARDEN_still_within_its_def_rate', 'GARDEN_drill_pours_its_yield',
        'GARDEN_drill_charges_what_landed', 'GARDEN_walled_yard_lies_level')
PLANTS = {'CALLER_CONV_DROPS_CLIPPED': 'GARDEN_filter_keeps_its_rate', 'CALLER_SPR_SPRAYS_WITHOUT_PUMP': 'GARDEN_no_pump_no_spray',
          'DEF_STILL_RATE_TENFOLD': 'GARDEN_still_within_its_def_rate',
          'DRILL_CHARGES_WHOLE_LEVEL': 'GARDEN_drill_charges_what_landed', 'SHEET_DRY_ISLAND': 'GARDEN_walled_yard_lies_level'}
FAILS = []


def check(ok, what):
    print('%s  %s' % ('ok  ' if ok else 'FAIL', what))
    if not ok:
        FAILS.append(what)


def main():
    healthy, f = run()
    check(not f.contract, 'every staging call keeps its tool contract %s' % f.contract[:3])
    check(all(healthy['rows'].get(r) == 'PASS' for r in ROWS) and set(healthy['rows']) == set(ROWS),
          'healthy garden: every row PASS %s' % (healthy.get('error') or healthy['rows']))
    for plant, rid in sorted(PLANTS.items()):
        got, _ = run(plant)
        check(got['rows'].get(rid) == 'FAIL', 'planted %s turns %s FAIL (got %s)' % (plant, rid, got['rows'].get(rid)))
    got, _ = run('night')
    check(got['rows'].get('GARDEN_still_within_its_def_rate') == 'UNMEASURED', 'no sun: the still row is UNMEASURED, not PASS')
    hungry = Fake()
    real = hungry.ticks

    def starve(n):                                # the staging ticks pass; the first window chunk stops on hunger
        if n >= 2500:
            raise GovernorStop('safe_advance stopped: starving: food category Starving')
        return real(n)
    hungry.ticks = starve
    res = {'calls': []}
    out = C.scene_garden(hungry, lambda: hungry.save('b'), lambda: hungry.load('b'), res) if hasattr(C, 'GARDEN_W') else {'rows': []}
    check(out['rows'] and not any(r['status'] == 'PASS' for r in out['rows']),
          'a broken clock: no row PASSes %s' % [(r['id'], r['status']) for r in out['rows']][:4])
    lo_hi = C._conv_window(60000, C.FILTER, C.CONV_MULT) if hasattr(C, '_conv_window') else (0, 0)
    dropped = C._conv_batches(241, C.FILTER['per'] * C.CONV_MULT, C.FILTER['inp'], keep=False, a0=C.FILTER['per'] * C.CONV_MULT + 1) \
        if hasattr(C, '_conv_batches') else 0
    check(dropped < lo_hi[0], 'the filter window %s excludes a dropped-clip run (%d batches at its best)' % (lo_hi, dropped))
    print('selftest_garden_scene: %s' % ('ok' if not FAILS else 'FAIL (%d)' % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
