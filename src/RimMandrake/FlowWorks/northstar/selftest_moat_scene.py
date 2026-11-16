#!/usr/bin/env python3
"""Offline half of sc_moat_raid (RIMMANDRAKE_REBUILD_FLOWWORKS_MOAT_SCENE_PASSED_ON_REFUSED): scene_moat_raid against a
fake map that holds each staging call to its tool's contract and models what sank visit 1 (2026-11-15):
  - jawa/fire_raid is an unplaced map-edge raid (and refused when the world holds no Pirate faction): a scene that needs
    raiders at its moat places them (spawn_pawn + lord_assault_spawn);
  - RM_NorthstarProofs.ProofTank takes "x,z;Mode" or "x,z;Mode;LiquidDef;units" (anything else REFUSED); ProofPump needs an
    RM_LiquidPump on its cell; ProofDrainGate is a read with no verb; RM_FlowDoorRules.ProofSetGate needs a flow door;
    RM_DrawbridgeProofs.ProofMakeDrawbridge needs undug ends, a dug interior and at most 4 timber squares;
  - the pump pours one level (10,000 tank units) a 250-tick cycle, only from a Dump tank, only while powered, only into a
    dry or same-fluid square beside it; a lowered leaf decks its squares (no swim there);
  - the governor: a hostile on the default stop list stops safe_advance and site_recover vanishes it.
The healthy fake (raiders swim the ring and tire, the sluice drains it into the pit, the dry ring holds them, two are taken
from the lip, the pump pours chemfuel and the toss lights it; over a lowered leaf they walk) reads every row PASS. A mod
whose raiders never enter the water reads the swim FAIL; a sluice that never drains reads the drain FAIL and what needs a dry
moat UNMEASURED; a dry ring that holds nobody reads the capture FAIL; a raid that is gone, or a swim read that comes back
REFUSED, reads UNMEASURED, never PASS; with fire_raid answering success (visit 1's second run) no row PASSes on a REFUSED
reply (the draft's MOAT_chemfuel_pumped did); an unpowered pump reads the chemfuel UNMEASURED. Red on the draft at 2b4bffe212, green
on the fix. The fake proves the scene's logic, never the game; the live half is
`python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_moat_raid --out <json>`.
    python3 selftest_moat_scene.py [path/to/concept_scenes.py]
"""
from copy import deepcopy
import importlib.util
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (HERE, ROOT / 'src/RimMandrake/Utils', ROOT / 'src/RimMandrake/Utils/modcheck'):
    sys.path.insert(0, str(p))
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'concept_scenes.py'
spec = importlib.util.spec_from_file_location('concept_scenes_under_test', SRC)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
O = C.O
XZ = r'-?\d+,-?\d+'
THINGDEFS = {d.text.strip() for f in (HERE.parent / 'Defs').rglob('*.xml') for t in ET.parse(f).getroot().iter('ThingDef')
             for d in t.findall('defName') if d.text} | {'Battery'}
HOSTILE = 'Pirate'
LEVEL = 10000                # RM_PumpMath.TankUnitsPerLevel
CAPACITY = 160000            # a 2x2 RM_LiquidTank: 4 squares x 4 levels x 10,000
DL_PER_M = 10000             # water dL in one square per metre (2 notches)
TANK_MODES = ('Store', 'Fill', 'Empty', 'Dump')


def xz(s):
    a, b = s.split(',')
    return int(a), int(b)


class Fake:
    """mod: 'healthy', 'noswim' (raiders stop at the bank), 'nodrain' (the lifted sluice moves nothing), 'nohold' (the dry ring
    holds nobody). fault: 'gone' (the raid is gone at the first poll), 'swimrefused' (ProofSwim REFUSED), 'nopower',
    'edgeraid' (jawa/fire_raid answers success)."""

    def __init__(self, mod='healthy', fault=None):
        self.mod, self.fault = mod, fault
        self.stop_on = 'default'
        self.g = {'dug': {}, 'water': {}, 'fluid': {}, 'built': {}, 'pawns': {}, 'announced': set(), 'n': 0, 'lifted': False,
                  'leaf': None, 'tank': None, 'pour': False, 'charged': False, 'tick': 0, 'orders': [], 'lit': set()}
        self.saves, self.contract = {}, []

    def save(self, k):
        self.saves[k] = deepcopy(self.g)

    def load(self, k):
        self.g = deepcopy(self.saves[k])

    def bad(self, why):
        self.contract.append(why)

    # ---- geometry the fake reads off what was dug and built
    def ring(self, c):
        return self.g['dug'].get(c, 0) == getattr(C, 'MOAT_DEEP', 8)

    def decked(self, c):
        lf = self.g['leaf']
        return bool(lf) and lf['progress'] == 0 and c in lf['deck']

    def deep(self, c):
        return self.g['water'].get(c, 0) >= DL_PER_M and not self.decked(c)

    # ---- the clock and the governor (validation_core.Bridge.ticks over jawa/safe_advance)
    def ticks(self, n):
        g = self.g
        g['tick'] += n
        hostile = [k for k, p in g['pawns'].items() if p['hostile']]
        new = [k for k in hostile if k not in g['announced']]
        g['announced'].update(new)
        if (new or hostile) and (self.stop_on == 'default' or 'hostile_arrival' in self.stop_on.split(',')):
            for k in hostile:
                del g['pawns'][k]                       # site_recover -> remove_intruders
            return {'success': True, 'advanced': n}
        if self.fault == 'gone':
            for k in hostile:
                del g['pawns'][k]
        self.settle()
        for _ in range(n // 120):
            self.step_raid()
            self.settle()
        for pid, cap in list(g['orders']):
            if n >= 900 and pid in g['pawns'] and g['pawns'][pid]['held']:
                g['pawns'][pid]['prisoner'] = True
                g['orders'].remove((pid, cap))
        self.step_pump(n)
        return {'success': True, 'advanced': n}

    def step_raid(self):
        g = self.g
        lf = g['leaf']
        for p in g['pawns'].values():
            if not p['hostile'] or p['held'] or p['prisoner']:
                continue
            if lf and lf['progress'] == 0 and p['x'] != lf['deck'][0][0] and p['z'] < O[1]:
                p['x'] += 1 if p['x'] < lf['deck'][0][0] else -1      # over the lowered leaf
                continue
            nxt = (p['x'], p['z'] + 1)
            if self.mod == 'noswim' and self.deep(nxt):
                continue
            if p['z'] < O[1] + 2:
                p['z'] += 1
            if self.deep((p['x'], p['z'])):
                p['exh'] = round(p['exh'] + 0.1, 3)

    def settle(self):
        """A raider of the ring on a drained (dry, undecked) square is held: a 4 m pit with nothing to swim in."""
        for p in self.g['pawns'].values():
            c = (p['x'], p['z'])
            if p['hostile'] and self.ring(c) and not self.g['water'].get(c) and not self.decked(c) and self.mod != 'nohold':
                p['held'] = True

    def step_pump(self, n):
        g = self.g
        pump, t = g['built'].get('RM_LiquidPump'), g['tank']
        if not (pump and t and g['pour'] and self.running() and t['mode'] == 'Dump'):
            return
        for _ in range(n // 250):
            if t['units'] < LEVEL:
                return
            side = [c for c in ((pump[0] - 1, pump[1] + dz) for dz in (-1, 0, 1)) if self.ring(c)]
            ok = [c for c in side if g['fluid'].get(c) in (None, 'RM_Fluid_Chemfuel') or not g['water'].get(c)]
            if not ok:
                return
            t['units'] -= LEVEL
            g['water'][ok[0]] = g['water'].get(ok[0], 0) + LEVEL // 2
            g['fluid'][ok[0]] = 'RM_Fluid_Chemfuel'

    def running(self):
        return self.g['charged'] and 'Battery' in self.g['built'] and self.fault != 'nopower'

    # ---- the bridge
    def call(self, tool, _answer=False, **kw):
        g = self.g
        if tool == 'jawa/flowworks_excavation_drive':
            c = (kw['x'], kw['z'])
            g['dug'][c] = g['dug'].get(c, 0) + kw['deepenLevels']
            return {'success': True}
        if tool == 'jawa/flowworks_excavation_rect':
            rows = [{'x': x, 'z': z, 'd': g['dug'].get((x, z), 0), 'dl': g['water'].get((x, z), 0), 'fluid': g['fluid'].get((x, z))}
                    for x in range(kw['x'], kw['x'] + kw['w']) for z in range(kw['z'], kw['z'] + kw['h'])]
            return {'success': True, 'rows': rows}
        if tool == 'jawa/flowworks_pulse':
            if g['lifted'] and self.mod != 'nodrain':
                wet = [c for c, v in g['water'].items() if v and g['fluid'].get(c) == 'RM_Fluid_Water']
                for c in wet:
                    g['water'][c] = max(0, g['water'][c] - DL_PER_M // 4)
            return {'success': True}
        if tool in ('jawa/spawn_batch', 'jawa/build_batch'):
            n = 0
            for op in kw['ops'].split(';'):
                d, at = op.split(':')
                if d not in THINGDEFS:
                    self.bad('%s given %s, not a ThingDef' % (tool, d))
                    continue
                if d == 'RM_Sluice' and (tool != 'jawa/build_batch' or not kw.get('stuff')):
                    self.bad('RM_Sluice (a stuffed flow door) placed without build_batch stuff')
                g['built'][d] = xz(at.split(',', 2)[0] + ',' + at.split(',')[1])
                n += 1
            return {'success': True, 'survived': n}
        if tool == 'jawa/fire_raid':
            self.bad('fire_raid: an unplaced map-edge raid (refused outright when no Pirate faction is in the world)')
            if self.fault == 'edgeraid':                # visit 1's second run: accepted, and nobody ever reached the moat
                return {'success': True}
            return {'success': False, 'message': "FactionDef 'Pirate' exists but no such faction is in this world."}
        if tool == 'jawa/spawn_pawn':
            if kw.get('faction') == '?':
                return {'success': False, 'details': {'available': [{'def': 'PlayerColony', 'hostile': False},
                                                                    {'def': HOSTILE, 'hostile': True}]}}
            g['n'] += 1
            pid = 'Human%d' % (900 + g['n'])
            g['pawns'][pid] = {'x': kw['x'], 'z': kw['z'], 'hostile': kw['faction'] == HOSTILE, 'exh': 0.0, 'held': False,
                               'prisoner': False}
            if kw['faction'] not in ('player', HOSTILE):
                self.bad('spawn_pawn faction %r' % kw['faction'])
            return {'success': True, 'pawns': [{'id': pid}]}
        if tool == 'jawa/lord_assault_spawn':
            if not all(i in g['pawns'] for i in kw['pawns'].split(',')):
                self.bad('lord_assault_spawn given unknown pawns')
            return {'success': True}
        if tool == 'jawa/list_pawns':
            hostile = kw.get('faction') == 'hostile'
            return {'success': True, 'pawns': [{'id': k, 'x': p['x'], 'z': p['z'], 'dead': False}
                                               for k, p in g['pawns'].items() if p['hostile'] == hostile]}
        if tool == 'jawa/list_things':
            if kw.get('defName') == 'Battery' and 'Battery' in g['built']:
                return {'success': True, 'things': [{'id': 'Battery77', 'def': 'Battery'}]}
            return {'success': True, 'things': []}
        if tool == 'jawa/battery_set':
            g['charged'] = kw.get('thing') == 'Battery77'
            return {'success': True}
        if tool == 'jawa/ordered_job':
            if kw['jobDef'] == 'RM_CaptureDown':
                lip = (kw.get('targetBX'), kw.get('targetBZ'))
                if g['dug'].get(lip):
                    self.bad('RM_CaptureDown lip %s is a dug square' % (lip,))
                g['orders'].append((kw['targetAId'], lip))
                return {'success': True, 'accepted': True, 'requestedJobDef': 'RM_CaptureDown'}
            if kw['jobDef'] == 'RM_TossFlame':
                c = (kw['targetAX'], kw['targetAZ'])
                if g['fluid'].get(c) == 'RM_Fluid_Chemfuel' and g['water'].get(c):
                    g['lit'].add(c)
                return {'success': True, 'accepted': True}
            self.bad('ordered_job %s' % kw['jobDef'])
            return {'success': False}
        if tool == 'jawa/mod_settings_field':
            return {'success': True, 'value': 'True'}
        if tool == 'jawa/static_call':
            return {'success': True, 'result': self.static(kw['type'], kw['method'], kw.get('args', ''))}
        raise AssertionError('unexpected tool %s %s' % (tool, kw))

    def static(self, typ, method, arg):
        g = self.g
        if method == 'ProofFillWithFluid':
            m = re.fullmatch(r'(-?\d+),(-?\d+),([\d.]+),(\w+)', arg or '')
            c = (int(m.group(1)), int(m.group(2))) if m else None
            if not c or not g['dug'].get(c):
                self.bad('fill on an undug square %s' % arg)
                return 'REFUSED: not excavated'
            g['water'][c] = int(float(m.group(3)) * DL_PER_M)
            g['fluid'][c] = m.group(4)
            return 'FILLED %s' % arg
        if method == 'ProofTank':
            a = (arg or '').split(';')
            if len(a) not in (2, 4) or not re.fullmatch(XZ, a[0]):
                self.bad('ProofTank arg %r' % arg)
                return 'REFUSED: arg must be x,z;Mode or x,z;Mode;LiquidDef;units on the current map'
            if 'RM_LiquidTank' not in g['built']:
                self.bad('ProofTank with no tank built')
                return 'REFUSED: no RM_LiquidTank at ' + a[0]
            if a[1] not in TANK_MODES:
                return 'REFUSED: unknown mode ' + a[1]
            t = g['tank'] or {'liquid': 'none', 'units': 0}
            if len(a) == 4:
                if not a[3].isdigit() or int(a[3]) > CAPACITY:
                    return 'REFUSED: bad liquid/units'
                t = {'liquid': a[2], 'units': int(a[3])}
            t['mode'] = a[1]
            g['tank'] = t
            return 'TANK mode=%s effective=%s liquid=%s units=%d' % (t['mode'], t['mode'], t['liquid'], t['units'])
        if method == 'ProofPump':
            a = (arg or '').split(';')
            if g['built'].get('RM_LiquidPump') != xz(a[0]):
                self.bad('ProofPump where no pump is: %r' % arg)
                return 'REFUSED: no RM_LiquidPump at ' + a[0]
            if len(a) > 1:
                g['pour'] = a[1] == 'pour'
            t = g['tank']
            return 'PUMP running=%s moved=0 pour=%s tank=%s' % (self.running(), g['pour'],
                                                                 'none' if not t else '%s:%d' % (t['liquid'], t['units']))
        if method == 'ProofDrainGate':
            if arg:
                self.bad('ProofDrainGate is a read (no verb, no cell): %r' % arg)
            return 'DRAINGATE gate=False setting=False drainEdge=False sunk=0'
        if method == 'ProofSetGate':
            m = re.fullmatch(r'current\|(%s)\|(true|false)' % XZ, arg or '')
            if not m or g['built'].get('RM_Sluice') != xz(m.group(1)):
                self.bad('ProofSetGate %r with no flow door there' % arg)
                return 'REFUSED: no flow door'
            g['lifted'] = m.group(2) == 'true'
            return 'DOOR RM_Sluice lifted=%s open=%s' % (g['lifted'], g['lifted'])
        if method == 'ProofMakeDrawbridge':
            m = re.fullmatch(r'(%s);(%s);timber;A;winch' % (XZ, XZ), arg or '')
            if not m:
                self.bad('ProofMakeDrawbridge arg %r' % arg)
                return 'DRAW ok=False reason=args'
            a, b = xz(m.group(1)), xz(m.group(2))
            step = 1 if b[1] > a[1] else -1
            inner = [(a[0], z) for z in range(a[1] + step, b[1], step)]
            if g['dug'].get(a) or g['dug'].get(b) or not all(g['dug'].get(c) for c in inner) or len(inner) > 4:
                self.bad('ProofMakeDrawbridge breaks the build rules: %r' % arg)
                return 'DRAW ok=False reason=rules'
            g['leaf'] = {'deck': inner, 'progress': 0, 'target': 'lowered'}
            return 'DRAW ok=True leaves=1 tier=Timber hinges=A winchAt=%d,%d' % (a[0], a[1] - step)
        if method in ('ProofLeaf', 'ProofDevSet'):
            a = (arg or '').split(';')
            lf = g['leaf']
            if not lf or xz(a[0]) not in lf['deck']:
                self.bad('%s off the deck %r' % (method, arg))
                return 'LEAF none'
            if method == 'ProofDevSet':
                lf['target'] = 'raised' if a[1] == 'raise' else 'lowered'
                lf['progress'] = 100 if a[1] == 'raise' else 0
                return 'DEVSET target=%s progress=%d' % (lf['target'], lf['progress'])
            return 'LEAF leaf=1/1 progress=%d target=%s winch=True' % (lf['progress'], lf['target'])
        if method == 'ProofSwim':
            if self.fault == 'swimrefused':
                return 'REFUSED: no current map'
            c = xz(arg)
            for k, p in g['pawns'].items():
                if (p['x'], p['z']) == c:
                    return 'SWIM %s class=Human natural=False water=%.2f deepCell=%s exhaustion=%.3f' % (
                        k, g['water'].get(c, 0) / DL_PER_M, self.deep(c) and self.ring(c), p['exh'])
            return 'REFUSED: no pawn at %d,%d' % c
        if method == 'ProofCaptureDown':
            p = g['pawns'].get(arg)
            if not p:
                return 'REFUSED: no spawned pawn ' + arg
            return 'VERDICT %s held=%s prisoner=%s cell=%d,%d' % ('Allowed' if p['held'] else 'NotHeld', p['held'],
                                                                  p['prisoner'], p['x'], p['z'])
        if method == 'ProofReadout':
            return 'OK -'
        if method == 'ProofCell':
            return 'CELL burning=%s' % (xz(arg) in g['lit'])
        raise AssertionError('unexpected static %s.%s %r' % (typ, method, arg))


def run(mod='healthy', fault=None):
    F = Fake(mod, fault)
    out = C.scene_moat_raid(F, lambda: F.save('begin'), lambda: F.load('begin'), {'calls': []})
    return {r['id']: r['status'] for r in out['rows']}, out, F


FAILS = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else why))
    if not ok:
        FAILS.append(label)


ROWS = ('MOAT_raiders_swim', 'MOAT_drains_fast', 'MOAT_two_held_and_captured', 'MOAT_chemfuel_pumped', 'MOAT_moat_burns',
        'MOAT_control_bridge_down_no_swim')
rows, out, F = run()
check('every staging call keeps its tool contract (placed raid; proof args; a pump, a door and a leaf where asked)',
      not F.contract, F.contract)
check('the scene leaves the governor as it found it', F.stop_on == 'default', F.stop_on)
check('healthy fake (swim and tire, drain, hold, capture two, pump chemfuel, it burns; over the lowered leaf they walk): '
      'every row PASS', out['status'] == 'PASS' and all(rows.get(r) == 'PASS' for r in ROWS),
      (rows, [x['detail'] for x in out['rows']][:3]))
check('no row PASSes on a REFUSED reply', not any(x['status'] == 'PASS' and 'REFUSED' in x['detail'] for x in out['rows']),
      [x for x in out['rows'] if 'REFUSED' in x['detail']])
r, o, _ = run(fault='edgeraid')
check('fire_raid answering success (visit 1): no row PASSes on a REFUSED reply, and the healthy rows still PASS',
      not any(x['status'] == 'PASS' and 'REFUSED' in x['detail'] for x in o['rows']) and all(r.get(x) == 'PASS' for x in ROWS),
      [(x['id'], x['status'], x['detail'][:90]) for x in o['rows'] if 'REFUSED' in x['detail']] or r)
r, o, _ = run(mod='noswim')
check('raiders that stop at the bank: the swim FAILs, the capture (nobody swam) UNMEASURED',
      r.get('MOAT_raiders_swim') == 'FAIL' and r.get('MOAT_two_held_and_captured') == 'UNMEASURED', r)
r, o, _ = run(mod='nodrain')
check('a lifted sluice that drains nothing: the drain FAILs, capture and chemfuel UNMEASURED, none PASS on a wet moat',
      r.get('MOAT_drains_fast') == 'FAIL' and r.get('MOAT_two_held_and_captured') == 'UNMEASURED'
      and r.get('MOAT_chemfuel_pumped') == 'UNMEASURED', r)
r, o, _ = run(mod='nohold')
check('a dry ring that holds nobody: the capture FAILs', r.get('MOAT_two_held_and_captured') == 'FAIL', r)
r, o, _ = run(fault='gone')
check('a raid that is gone at the first poll: swim, capture and control UNMEASURED, none of them PASS',
      all(r.get(x) == 'UNMEASURED' for x in ('MOAT_raiders_swim', 'MOAT_two_held_and_captured',
                                               'MOAT_control_bridge_down_no_swim')), r)
r, o, _ = run(fault='swimrefused')
check('a REFUSED swim read: the swim and the control UNMEASURED, never PASS',
      r.get('MOAT_raiders_swim') == 'UNMEASURED' and r.get('MOAT_control_bridge_down_no_swim') == 'UNMEASURED', r)
r, o, _ = run(fault='nopower')
check('a pump that never runs: the chemfuel UNMEASURED and the burn (no chemfuel square) UNMEASURED',
      r.get('MOAT_chemfuel_pumped') == 'UNMEASURED' and r.get('MOAT_moat_burns') == 'UNMEASURED', r)
print('selftest_moat_scene: %s' % ('FAIL' if FAILS else 'ok'))
sys.exit(1 if FAILS else 0)
