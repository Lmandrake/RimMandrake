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
  - RIMMANDRAKE_DECIDE_MOAT_RAID_BAR_TEXT_SAYS_D4_SCENE_NEEDS_SIX (2026-11-23): the water is the kernel's own twin
    (validation_v2.PulseOracle over level_water.py, the recorded live drain to 1 dL), one pulse per 250 game ticks; a raider
    pays the mod's own step costs in game ticks (a swim square 113, a 2-notch climb 90 more), tires at each 250-tick check, steps
    in or out only while at most 2 notches of wall stand above the water, and is held where more do; six of them set out 48
    ticks apart. So a drain in bare flow pulses (no game time) and a moat raiders cross before it holds are both seen here.
The healthy fake (raiders swim the moat and tire, the sluice drains it into the pit in game time, it holds them, two are taken
from the lip, the pump pours chemfuel and the toss lights it; over a lowered leaf they walk) reads every row PASS. Red on the
scene at 7606237d1a (2 wide, brim-full, drained in no game time), and on that geometry in the scene as it stands now. A mod
whose raiders never enter the water reads the swim FAIL; a sluice that never drains reads the drain FAIL and what needs a dry
moat UNMEASURED; a drained moat whose raiders read not held reads the capture FAIL; a raid that is gone, or a swim read that
comes back REFUSED, reads UNMEASURED, never PASS; with fire_raid answering success (visit 1's second run) no row PASSes on a
REFUSED reply (the draft's MOAT_chemfuel_pumped did); an unpowered pump reads the chemfuel UNMEASURED. The fake proves the
scene's logic, never the game; the live half is
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
from validation_v2 import PulseOracle      # noqa: E402  the kernel's Python twin
O = C.O
XZ = r'-?\d+,-?\d+'
THINGDEFS = {d.text.strip() for f in (HERE.parent / 'Defs').rglob('*.xml') for t in ET.parse(f).getroot().iter('ThingDef')
             for d in t.findall('defName') if d.text} | {'Battery'}
HOSTILE = 'Pirate'
LEVEL = 10000                # RM_PumpMath.TankUnitsPerLevel
CAPACITY = 160000            # a 2x2 RM_LiquidTank: 4 squares x 4 levels x 10,000
U = 10000                    # water dL in one 0.5 m notch of one square (RM_Volume.UnitsPerLevel)
DL_PER_M = 2 * U
SWIM, CLIMB = 113, 90        # ticks: the median recorded raider's swim square; a 2-notch climb (45 x slow factor 2)
TANK_MODES = ('Store', 'Fill', 'Empty', 'Dump')


def xz(s):
    a, b = s.split(',')
    return int(a), int(b)


class Fake:
    """mod: 'healthy', 'noswim' (raiders stop at the bank), 'nodrain' (the lifted sluice moves nothing), 'nohold' (walls
    stand, but no raider in the moat reads held). fault: 'gone' (the raid is gone at the first poll), 'swimrefused' (ProofSwim REFUSED), 'nopower',
    'edgeraid' (jawa/fire_raid answers success). mod 'swimcheap': raiders never choose the lowered deck. Every other raider is
    slow on the deck (recorded raiders stand on it for a whole poll); a raider holds his deck square against the one behind him, who swims round (control_crowd.py)."""

    def __init__(self, mod='healthy', fault=None):
        self.mod, self.fault = mod, fault
        self.stop_on = 'default'
        self.g = {'grass': {C._moat_geom()['tank'], C._moat_geom()['battery']}, 'dug': {}, 'water': {}, 'fluid': {}, 'built': {}, 'pawns': {}, 'announced': set(), 'n': 0, 'lifted': False,
                  'leaf': None, 'tank': None, 'pour': False, 'charged': False, 'tick': 0, 'orders': [], 'lit': set(), 'mark': {}}
        self.saves, self.contract, self.drained_in = {}, [], None

    def save(self, k):
        self.saves[k] = deepcopy(self.g)

    def load(self, k):
        self.g = deepcopy(self.saves[k])

    def bad(self, why):
        self.contract.append(why)

    # ---- geometry the fake reads off what was dug and built
    def ring(self, c):
        return self.g['dug'].get(c, 0) == C.MOAT_DEEP and c != self.g['built'].get('RM_Sluice')

    def decked(self, c):
        lf = self.g['leaf']
        return bool(lf) and lf['progress'] == 0 and c in lf['deck']

    def deep(self, c):
        return self.g['water'].get(c, 0) >= 4 * U and not self.decked(c)          # 2 m and deeper is swum

    def climb(self, c):
        """Notches of wall a person on c stands under: the surface of chest-deep or deeper water, else the floor."""
        d, w = self.g['dug'].get(c, 0), self.g['water'].get(c, 0)
        if self.decked(c) or self.g['fluid'].get(c) == 'RM_Fluid_Chemfuel':
            return 0 if self.decked(c) else d
        return d - w // U if w >= 3 * U else d

    # ---- the clock and the governor (validation_core.Bridge.ticks over jawa/safe_advance)
    def ticks(self, n):
        g = self.g
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
        for _ in range(n // 10):
            g['tick'] += 10
            if g['tick'] % 250 == 0:
                self.flow()
                self.step_pump(250)
                for p in g['pawns'].values():
                    if p['hostile'] and self.deep((p['x'], p['z'])):
                        p['exh'] = round(p['exh'] + 0.1, 3)
            self.step_raid()
            for o in list(g['orders']):
                pid, _, at = o
                if pid in g['pawns'] and self.held(pid) and g['tick'] - at >= 180:
                    g['pawns'][pid]['prisoner'] = True
                    g['orders'].remove(o)
        return {'success': True, 'advanced': n}

    def held(self, pid):
        p = self.g['pawns'][pid]
        c = (p['x'], p['z'])
        return self.ring(c) and self.climb(c) > 2 and self.mod != 'nohold'

    def step_raid(self):
        g, lf = self.g, self.g['leaf']
        for k, p in g['pawns'].items():
            if not p['hostile'] or p['prisoner'] or g['tick'] < p['next']:
                continue
            c = (p['x'], p['z'])
            if c[1] >= O[1] + getattr(C, 'MOAT_W', 2) + 1:
                continue                                                          # in the plot, past the rim
            if lf and lf['progress'] == 0 and c[0] != lf['deck'][0][0] and c[1] < O[1]:
                nxt = (c[0] + (1 if c[0] < lf['deck'][0][0] else -1), c[1])       # over the lowered leaf
            else:
                nxt = (c[0], c[1] + 1)
            if self.mod == 'swimcheap' and lf and lf['progress'] == 0:            # a forced path: the deck is never chosen
                nxt = (c[0], c[1] + 1) if c[0] != lf['deck'][0][0] else (c[0] + 1, c[1])
            if self.decked(nxt) and any(k2 != k and q['hostile'] and (q['x'], q['z']) == nxt for k2, q in g['pawns'].items()):
                nxt = (nxt[0] + 1, nxt[1])                  # held by another raider (vanilla +175): round him through the water
            if abs(self.climb(nxt) - self.climb(c)) > 2 or (self.mod == 'noswim' and self.deep(nxt)):
                p['goal'] = None
                continue
            if p['goal'] != nxt:                                                  # he pays the next square's cost where he stands
                p['goal'] = nxt
                slow = self.decked(nxt) and int(k[5:]) % 2           # every other raider dawdles on the deck
                p['next'] = g['tick'] + (SWIM if self.deep(nxt) else 60 if slow else 13) + (CLIMB if self.climb(c) - self.climb(nxt) == 2 else 0)
                continue
            p['x'], p['z'], p['goal'] = nxt[0], nxt[1], None

    def flow(self):
        """One flow pulse of the dug squares that hold no chemfuel (the kernel twin; a shut sluice seals its square)."""
        g = self.g
        if not any(v for c, v in g['water'].items() if g['fluid'].get(c) == 'RM_Fluid_Water'):
            return
        o = PulseOracle(160, 160, {}, {}, per=1, budget=True)
        for c, d in g['dug'].items():
            if g['fluid'].get(c) != 'RM_Fluid_Chemfuel':
                o.D[c], o.W[c] = d, g['water'].get(c, 0)
        s = g['built'].get('RM_Sluice')
        o.sealed = {s} if s and (not g['lifted'] or self.mod == 'nodrain') else set()
        o.pulse()
        for c, w in o.W.items():
            g['water'][c] = w
            if w and g['fluid'].get(c) is None:
                g['fluid'][c] = 'RM_Fluid_Water'
        if 'liftedAt' in g['mark'] and 'dryAt' not in g['mark'] and not any(
                v for c, v in g['water'].items() if self.ring(c)):
            g['mark']['dryAt'] = g['tick']
            self.drained_in = g['tick'] - g['mark']['liftedAt']

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
            g['water'][ok[0]] = g['water'].get(ok[0], 0) + LEVEL // 2 if g['fluid'].get(ok[0]) == 'RM_Fluid_Chemfuel' else LEVEL // 2
            g['fluid'][ok[0]] = 'RM_Fluid_Chemfuel'

    def running(self):
        return self.g['charged'] and 'Battery' in self.g['built'] and self.fault != 'nopower'

    # ---- the bridge
    def call(self, tool, _answer=False, **kw):
        g = self.g
        if tool == 'jawa/flowworks_excavation_drive':
            c = (kw['x'], kw['z'])
            g['dug'][c] = g['dug'].get(c, 0) + kw['deepenLevels']
            # the real drive answers the square's depth and water: the scene reads the brim back (eb15c22de9)
            return {'success': True, 'depth': g['dug'][c], 'waterM': g['water'].get(c, 0) / DL_PER_M}
        if tool == 'jawa/flowworks_excavation_rect':
            rows = [{'x': x, 'z': z, 'd': g['dug'].get((x, z), 0), 'dl': g['water'].get((x, z), 0), 'fluid': g['fluid'].get((x, z))}
                    for x in range(kw['x'], kw['x'] + kw['w']) for z in range(kw['z'], kw['z'] + kw['h'])]
            return {'success': True, 'rows': rows}
        if tool == 'jawa/flowworks_pulse':
            for _ in range(kw['count']):
                self.flow()
            return {'success': True}
        if tool == 'jawa/destroy_batch':            # the plot's grass goes (nothing is built yet, so nothing else is in it)
            if 'Building' in kw['categories'] or 'Plant' not in kw['categories']:
                self.bad('destroy_batch %s' % kw)
            x, z, w, h = (int(v) for v in kw['rects'].split(','))
            g['grass'] -= {(x + i, z + j) for i in range(w) for j in range(h)}
            return {'success': True}
        if tool in ('jawa/spawn_batch', 'jawa/build_batch'):
            n = 0
            if tool == 'jawa/build_batch' and kw.get('wipeExisting') is False:
                tops = [xz(op.split(':')[1]) for op in kw['ops'].split(';')]
                if g['grass'] & {tuple(c) for c in tops}:       # live ArchSmall 2026-11-23: 'placing this would destroy'
                    return {'success': False, 'partial': True, 'error': 'op(s) failed: Plant_Grass', 'survived': 0}
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
            g['pawns'][pid] = {'x': kw['x'], 'z': kw['z'], 'hostile': kw['faction'] == HOSTILE, 'exh': 0.0,
                               'prisoner': False, 'goal': None, 'next': g['tick'] + 250 + 48 * (g['n'] % 6)}
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
        if tool == 'jawa/pawn_force_incapacitate':       # the free raiders and the bait colonist leave the map (pit-trap idiom)
            if kw.get('action') != 'vanish' or kw.get('pawn') not in g['pawns']:
                self.bad('pawn_force_incapacitate %s' % kw)
            g['pawns'].pop(kw.get('pawn'), None)
            return {'success': True}
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
                g['orders'].append((kw['targetAId'], lip, g['tick']))
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
        if tool == 'jawa/site_state':                # the capture trace's read (S.B.call, past the receipt)
            return {'success': True, 'pawns': [{'id': k, 'x': p['x'], 'z': p['z'], 'job': None} for k, p in g['pawns'].items()],
                    'state': {'tick': 0}}
        if tool == 'jawa/damage_log':               # who hurt a warden: nobody, or (fault 'stab') a held raider
            if self.fault == 'stab':
                raider = sorted(k for k, p in g['pawns'].items() if p['hostile'])[0]
                return {'success': True, 'events': [{'tick': 9, 'instigatorId': raider, 'damageDef': 'Stab'}]}
            return {'success': True, 'events': []}
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
            if g['lifted']:
                g['mark'] = {'liftedAt': g['tick']}
            return 'DOOR RM_Sluice lifted=%s open=%s' % (g['lifted'], g['lifted'])
        if method == 'ProofMakeDrawbridge':
            # hinge A sits at the first end, B at the second (the scene hinges on B since eb15c22de9); the winch is beyond it
            m = re.fullmatch(r'(%s);(%s);timber;([AB]);winch' % (XZ, XZ), arg or '')
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
            h = m.group(3)
            w = (a[0], a[1] - step) if h == 'A' else (b[0], b[1] + step)
            return 'DRAW ok=True leaves=1 tier=Timber hinges=%s winchAt=%d,%d' % (h, w[0], w[1])
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
            return 'VERDICT %s held=%s prisoner=%s cell=%d,%d' % ('Allowed' if self.held(arg) else 'NotHeld', self.held(arg),
                                                                  p['prisoner'], p['x'], p['z'])
        if method == 'ProofReachPair':
            return 'REACH canReach=False'
        if method == 'ProofReadout':
            return 'OK -'
        if method == 'ProofCell':
            return 'CELL burning=%s' % (xz(arg) in g['lit'])
        raise AssertionError('unexpected static %s.%s %r' % (typ, method, arg))


def run(mod='healthy', fault=None, **geometry):
    """geometry: MOAT_* constants of the scene for this run alone (a planted staging)."""
    F, was = Fake(mod, fault), {k: getattr(C, k) for k in geometry}
    for k, v in geometry.items():
        setattr(C, k, v)
    try:
        out = C.scene_moat_raid(F, lambda: F.save('begin'), lambda: F.load('begin'), {'calls': []})
    finally:
        for k, v in was.items():
            setattr(C, k, v)
    return {r['id']: r['status'] for r in out['rows']}, out, F


FAILS = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else why))
    if not ok:
        FAILS.append(label)


ROWS = ('MOAT_raiders_swim', 'MOAT_drains_fast', 'MOAT_two_held_and_captured', 'MOAT_rim_wardens_not_stabbed', 'MOAT_chemfuel_pumped',
        'MOAT_moat_burns', 'MOAT_control_bridge_down_no_swim')
rows, out, F = run()
check('every staging call keeps its tool contract (placed raid; proof args; a pump, a door and a leaf where asked)',
      not F.contract, F.contract)
check('the scene leaves the governor as it found it', F.stop_on == 'default', F.stop_on)
check('healthy fake (swim and tire, drain, hold, capture two, pump chemfuel, it burns; over the lowered leaf they walk): '
      'every row PASS', out['status'] == 'PASS' and all(rows.get(r) == 'PASS' for r in ROWS),
      (rows, [x['detail'] for x in out['rows']][:3]))
check('no row PASSes on a REFUSED reply', not any(x['status'] == 'PASS' and 'REFUSED' in x['detail'] for x in out['rows']),
      [x for x in out['rows'] if 'REFUSED' in x['detail']])
check('the sluice drains the moat in game time, the raid going on (frozen flow pulses: 0 ticks)',
      bool(F.drained_in) and F.drained_in >= 500, F.drained_in)
if hasattr(C, 'MOAT_W'):
    r, o, _ = run(MOAT_W=2, MOAT_N=12, MOAT_DEEP=6, MOAT_WATER_M=3.0, MOAT_PIT_DEEP=20)
    check('the old staging (2 wide, brim-full 3 m) played in game time: raiders cross before it holds, the capture never PASSes',
          r.get('MOAT_two_held_and_captured') in ('UNMEASURED', 'FAIL'), r)
    r, o, _ = run(MOAT_WATER_M=4.0)
    check('4 wide but brim-full: it holds too late, the capture never PASSes',
          r.get('MOAT_two_held_and_captured') in ('UNMEASURED', 'FAIL'), r)
    r, o, _ = run(MOAT_WATER_M=2.5)
    check('more than a metre of wall above the water: nobody enters, the swim FAILs', r.get('MOAT_raiders_swim') == 'FAIL', r)
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
check('a drained moat whose raiders read not held: the capture FAILs', r.get('MOAT_two_held_and_captured') == 'FAIL', r)
r, o, _ = run(fault='stab')
check('a held raider that stabs a warden on the rim (2026-11-23): MOAT_rim_wardens_not_stabbed FAILs',
      r.get('MOAT_rim_wardens_not_stabbed') == 'FAIL' and r.get('MOAT_two_held_and_captured') == 'PASS', r)
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
r, o, _ = run(mod='swimcheap')
check('raiders that never choose the lowered deck: the control FAILs (its staging excuses nobody)',
      r.get('MOAT_control_bridge_down_no_swim') == 'FAIL', [x for x in o['rows'] if 'control' in x['id']])
check('the control leaves a trace of who stood where', bool(o.get('moatControlTrace')), sorted(o))
if hasattr(C, '_moat_send'):
    stage = C._moat_stage

    def all_at_once(S, raised=True):
        G = stage(S, raised)
        if G['later']:
            C._moat_send(S, G, G['later'])
            G['later'] = []
        return G
    C._moat_stage = all_at_once
    r, o, _ = run()
    C._moat_stage = stage
    check('the old control staging (six at once on a 1-wide deck): a raider swims round the one who holds it, the control FAILs',
          r.get('MOAT_control_bridge_down_no_swim') == 'FAIL', r)


# sc_moat_walkers: one ordered colonist on the same map, and no raider (owner, 2026-11-23)
class Walk(Fake):
    """mod adds: 'refuse' (the colonist never enters the water), 'dryshod' (he crosses the raised moat with no swim square),
    'climber' (a drained 4 m moat does not stop him), 'deckwet' (the lowered leaf does not bear him: he swims)."""

    def call(self, tool, _answer=False, **kw):
        g = self.g
        if tool in ('jawa/lord_assault_spawn', 'jawa/fire_raid'):
            self.bad('a raid call in sc_moat_walkers: %s' % tool)
        if tool == 'jawa/order_pawn':
            # the live engine (visit 10): the reach labels follow a staged pour 60 ticks later; a Goto to a plot that reads
            # unreachable is taken and dropped, and the reply's success is False until he stands on the square
            if not self.stale():
                g['pawns'][kw['pawnId']]['to'] = (kw['x'], kw['z'])
            return {'success': False}
        return Fake.call(self, tool, _answer=_answer, **kw)

    def stale(self):
        return self.mod == 'laggy' or self.g['tick'] - self.g.get('poured', -99) < 60

    def static(self, typ, method, arg):
        if method == 'ProofReachPair':
            return 'REACHPAIR canReach=%s found=True' % (not self.stale())
        if method == 'ProofFillWithFluid':
            self.g['poured'] = self.g['tick']
        return Fake.static(self, typ, method, arg)

    def deep(self, c):
        return self.mod != 'dryshod' and Fake.deep(self, c)

    def decked(self, c):
        return self.mod != 'deckwet' and Fake.decked(self, c)

    def ticks(self, n):
        out = Fake.ticks(self, n)
        lf = self.g['leaf']
        for _ in range(n // 15):
            for p in self.g['pawns'].values():
                if not p.get('to'):
                    continue
                c, to = (p['x'], p['z']), p['to']
                deck = lf['deck'][0][0] if lf and lf['progress'] == 0 else None
                if deck is not None and c[1] < O[1] + C.MOAT_W and c[0] != deck:
                    nxt = (c[0] + (1 if c[0] < deck else -1), c[1])
                elif c[1] != to[1]:
                    nxt = (c[0], c[1] + (1 if c[1] < to[1] else -1))
                else:
                    nxt = (c[0] + (0 if c[0] == to[0] else 1 if c[0] < to[0] else -1), c[1])
                if self.mod == 'refuse' and Fake.deep(self, nxt):
                    continue
                if self.mod != 'climber' and not Fake.deep(self, nxt) and self.climb(nxt) - self.climb(c) > 2:
                    continue
                p['x'], p['z'] = nxt
                if self.deep(nxt):
                    p['exh'] = round(p['exh'] + 0.02, 3)
        return out


def walkers(mod='healthy', fault=None):
    # 'laggy': the reach labels never follow the pour
    F = Walk(mod, fault)
    o = C.scene_moat_walkers(F, lambda: F.save('begin'), lambda: F.load('begin'), {'calls': []})
    return {x['id']: x['status'] for x in o['rows']}, o, F


MW = ('MW_raised_leaf_swims_and_tires', 'MW_drains_fast', 'MW_drained_moat_is_not_walked_over', 'MW_chemfuel_pumped', 'MW_moat_burns',
      'MW_lowered_leaf_bears_him_dry')
r, o, F = walkers()
check('sc_moat_walkers: swims and tires, drains, the drained moat stops him, pumped, burns, the leaf bears him: every row PASS',
      all(r.get(x) == 'PASS' for x in MW) and len(r) == len(MW), (r, [x['detail'] for x in o['rows'] if x['status'] != 'PASS'][:3]))
check('sc_moat_walkers stages no raid and keeps its tool contracts', not F.contract, F.contract)
for mod, rid, want in (('dryshod', MW[0], 'FAIL'), ('refuse', MW[0], 'UNMEASURED'), ('nodrain', MW[1], 'FAIL'), ('nodrain', MW[2], 'UNMEASURED'),
                       ('climber', MW[2], 'FAIL'), ('deckwet', MW[5], 'FAIL'),
                       ('laggy', MW[0], 'UNMEASURED')):
    r, o, _ = walkers(mod)
    check('sc_moat_walkers, plant %s: %s %s' % (mod, rid, want), r.get(rid) == want, (r, [x['detail'] for x in o['rows'] if x['id'] == rid]))
r, o, _ = walkers(fault='nopower')
check('sc_moat_walkers, a pump that never runs: chemfuel and burn UNMEASURED', r.get(MW[3]) == 'UNMEASURED' and r.get(MW[4]) == 'UNMEASURED', r)
print('selftest_moat_scene: %s' % ('FAIL' if FAILS else 'ok'))
sys.exit(1 if FAILS else 0)
