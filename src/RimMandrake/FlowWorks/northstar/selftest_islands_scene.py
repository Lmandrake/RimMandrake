#!/usr/bin/env python3
"""Offline half of sc_islands (RIMMANDRAKE_REBUILD_FLOWWORKS_ISLANDS_SCENE_SPAWNED_A_DRAW_STYLE): scene_islands against a
fake map that holds each staging call to its tool's contract and models what sank visit 1 (2026-11-15):
  - jawa/spawn_batch places ThingDefs only: the ThingDef names are read from FlowWorks's own Defs, so 'RM_SuspensionBridge'
    (a DrawStyleCategoryDef) is refused 'unknown ThingDef' as the game refused it;
  - RM_SuspensionProofs.ProofBuild and RM_DrawbridgeProofs.ProofMakeDrawbridge/ProofLeaf/ProofDevSet keep their argument
    shapes and the build rules the mod enforces (ends on undug ground, a dug interior, a leaf of at most 4 timber squares,
    the winch on the hinge side beside the end anchor, nothing already built there);
  - the governor: a hostile on the default stop list stops safe_advance and site_recover vanishes it, unless the scene
    narrows B.stop_on for its own raid.
The healthy fake (sappers shell the west winch, its leaf crashes, they walk off; held winches keep them on the span) reads
every row PASS; sappers that never take a winch read ISL_raiders_destroy_a_winch FAIL and the staged loss still asks the
drop and the escape; a leaf that stays up after its winch falls reads the drop FAIL and the escape UNMEASURED; raiders that
leave over raised leaves read the trap and the control FAIL; a raid that is gone reads every row UNMEASURED, never PASS.
Red on the draft at 2b4bffe212, green on the fix. The fake proves the scene's logic, never the game; the live half is
`python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_islands --out <json>`.
    python3 selftest_islands_scene.py [path/to/concept_scenes.py]
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
             for d in t.findall('defName') if d.text}
HOSTILE = 'Pirate'
MAX_LEAF_TIMBER = 4         # RM_DrawbridgeSettings.maxLeafTimber
FULL = 100                  # a leaf's full progress (any positive number: the scene reads 0 / not 0)
WINCH_HP = 200              # RM_DrawbridgeWinch_Timber MaxHitPoints
SHELL = 70                  # damage one poll of sapper fire does to a raised leaf's winch


class Fake:
    """mod: 'healthy', 'nowinch' (sappers never take a winch), 'nodrop' (a leaf stays up when its winch falls).
    fault: 'leaky' (raiders walk off over raised leaves), 'gone' (the raid is dead or gone at the first poll)."""

    def __init__(self, mod='healthy', fault=None):
        self.mod, self.fault = mod, fault
        self.stop_on = 'default'
        self.g = {'dug': {}, 'built': set(), 'leaves': {}, 'winches': {}, 'pawns': {}, 'announced': set(), 'n': 0,
                  'sappers': False, 'jobs': 0}
        self.saves, self.contract = {}, []

    def save(self, k):
        self.saves[k] = deepcopy(self.g)

    def load(self, k):
        self.g = deepcopy(self.saves[k])

    def bad(self, why):
        self.contract.append(why)

    # ---- the clock and the governor (validation_core.Bridge.ticks over jawa/safe_advance)
    def ticks(self, n):
        g = self.g
        hostile = [k for k, p in g['pawns'].items() if p['hostile']]
        new = [k for k in hostile if k not in g['announced']]
        g['announced'].update(new)
        if new and (self.stop_on == 'default' or 'hostile_arrival' in self.stop_on.split(',')):
            for k in hostile:
                del g['pawns'][k]                       # site_recover -> remove_intruders
            return {'success': True, 'advanced': n}
        if self.fault == 'gone':
            for k in hostile:
                del g['pawns'][k]
            return {'success': True, 'advanced': n}
        if n < 60:
            return {'success': True, 'advanced': n}
        if self.mod != 'nowinch' and g['sappers'] and hostile:
            for cell, w in list(g['winches'].items()):
                leaf = g['leaves'][w['leaf']]
                if leaf['progress'] > 0:
                    g['jobs'] += 1
                    w['hp'] -= SHELL
                    if w['hp'] <= 0:
                        self.lose(cell)
                    break
        down = [dx for dx, l in g['leaves'].items() if l['progress'] == 0]
        for k in hostile:
            p = g['pawns'][k]
            if self.fault == 'leaky' or (down and min(down) < 10):
                p['x'] = max(p['x'] - 4, O[0] - 2)
            elif down:
                p['x'] = min(p['x'] + 4, O[0] + 23)
        return {'success': True, 'advanced': n}

    def lose(self, cell):
        w = self.g['winches'].pop(cell)
        if self.mod != 'nodrop':
            self.g['leaves'][w['leaf']]['progress'] = 0     # RM_Drawbridges: a lost winch crashes its leaf down

    # ---- the bridge
    def call(self, tool, _answer=False, **kw):
        g = self.g
        if tool == 'jawa/flowworks_excavation_drive':
            c = (kw['x'], kw['z'])
            g['dug'][c] = g['dug'].get(c, 0) + kw['deepenLevels']
            return {'success': True}
        if tool == 'jawa/spawn_batch':
            errs = []
            for i, op in enumerate(kw['ops'].split(';')):
                d = op.split(':')[0]
                if d not in THINGDEFS:
                    self.bad('spawn_batch given %s, not a ThingDef' % d)
                    errs.append({'op': i, 'def': d, 'error': 'unknown ThingDef'})
            return {'success': not errs, 'errors': errs}
        if tool == 'jawa/spawn_pawn':
            if kw.get('faction') == '?':
                return {'success': False, 'details': {'available': [{'def': 'PlayerColony', 'hostile': False},
                                                                    {'def': 'Mechanoid', 'hostile': True},
                                                                    {'def': HOSTILE, 'hostile': True}]}}
            g['n'] += 1
            pid = 'Human%d' % (900 + g['n'])
            g['pawns'][pid] = {'x': kw['x'], 'z': kw['z'], 'hostile': kw['faction'] == HOSTILE}
            if kw['faction'] not in ('player', HOSTILE):
                self.bad('spawn_pawn faction %r' % kw['faction'])
            return {'success': True, 'pawns': [{'id': pid}]}
        if tool in ('jawa/set_pawn_skill', 'jawa/pawn_gear'):
            return {'success': True}
        if tool == 'jawa/lord_assault_spawn':
            ids = kw['pawns'].split(',')
            if not all(i in g['pawns'] for i in ids):
                self.bad('lord_assault_spawn given unknown pawns %s' % ids)
            g['sappers'] = kw.get('sappers') is True
            return {'success': True}
        if tool == 'jawa/list_pawns':
            hostile = kw.get('faction') == 'hostile'
            return {'success': True, 'pawns': [{'id': k, 'x': p['x'], 'z': p['z'], 'dead': False}
                                               for k, p in g['pawns'].items() if p['hostile'] == hostile]}
        if tool == 'jawa/list_things':
            x, z, w, h = (int(v) for v in kw['rect'].split(','))
            return {'success': True, 'things': [{'id': 'Thing_W%d_%d' % c, 'def': 'RM_DrawbridgeWinch_Timber', 'maxHitPoints': WINCH_HP}
                                                for c in g['winches'] if kw.get('defName') == 'RM_DrawbridgeWinch_Timber'
                                                and x <= c[0] < x + w and z <= c[1] < z + h]}
        if tool == 'jawa/destroy_batch':
            if kw.get('categories') != 'Building':
                self.bad('destroy_batch categories %r' % kw.get('categories'))
            x, z, w, h = (int(v) for v in kw['rects'].split(','))
            hit = [c for c in g['winches'] if x <= c[0] < x + w and z <= c[1] < z + h]
            for c in hit:
                self.lose(c)
            return {'success': True, 'destroyed': len(hit)}
        if tool == 'jawa/set_thing_props':
            for c, w in g['winches'].items():
                if kw['thing'] == 'Thing_W%d_%d' % c:
                    w['hp'] = min(kw['hitPoints'], WINCH_HP)
            return {'success': True}
        if tool == 'jawa/mod_settings_field':
            if kw.get('field') == 'WinchJobs':
                return {'success': True, 'value': g['jobs']}
            return {'success': True, 'value': None}
        if tool == 'jawa/static_call':
            return {'success': True, 'result': self.static(kw['type'], kw['method'], kw.get('args', ''))}
        if tool == 'jawa/fire_raid':
            return {'success': True, 'executed': True}
        raise AssertionError('unexpected tool %s %s' % (tool, kw))

    def ground(self, c):
        return c not in self.g['dug'] and c not in self.g['built']

    def span(self, arg, n):
        a = arg.split(';')
        if len(a) < n or not re.fullmatch(XZ, a[0]) or not re.fullmatch(XZ, a[1]):
            return None
        (x1, z1), (x2, z2) = (tuple(int(v) for v in s.split(',')) for s in a[:2])
        if z1 != z2:
            return None
        x1, x2 = min(x1, x2), max(x1, x2)
        return a, x1, x2, z1

    def static(self, typ, method, arg):
        g = self.g
        if method == 'ProofBuild':
            s = self.span(arg, 3)
            if s is None or s[0][2] not in ('rope', 'timber', 'steel', 'heavy', 'steelgrated', 'heavygrated'):
                self.bad('ProofBuild given %r' % arg)
                return 'REFUSED: arg must be x1,z1;x2,z2;tier[;god] on the current map'
            a, x1, x2, z = s
            limit = {'rope': 12, 'timber': 8}.get(a[2], 20)
            if not (self.ground((x1, z)) and self.ground((x2, z))):
                return 'BUILD ok=False anchors=0 decks=0 blueprints=0 records=0 reason=must_end_on_solid,_undug_ground'
            if not all((x, z) in g['dug'] for x in range(x1 + 1, x2)) or x2 - x1 - 1 > limit:
                return 'BUILD ok=False anchors=0 decks=0 blueprints=0 records=0 reason=bad_span'
            g['built'].update({(x1, z), (x2, z)})
            return 'BUILD ok=True anchors=2 decks=%d blueprints=0 records=1 reason=-' % (x2 - x1 - 1)
        if method == 'ProofMakeDrawbridge':
            s = self.span(arg, 4)
            if s is None or s[0][2] not in ('timber', 'steel') or s[0][3] not in ('A', 'B'):
                self.bad('ProofMakeDrawbridge given %r' % arg)
                return 'REFUSED: arg must be x1,z1;x2,z2;timber|steel;A|B[;winch] on the current map'
            a, x1, x2, z = s
            built = self.static(typ, 'ProofBuild', '%d,%d;%d,%d;%s;god' % (x1, z, x2, z, a[2]))
            if not built.startswith('BUILD ok=True'):
                return 'DRAW ok=False leaves=0 tier=%s hinges=- winchAt=- firstAt=- reason=build:%s' % (a[2], built)
            if x2 - x1 - 1 > 2 * MAX_LEAF_TIMBER:
                return 'DRAW ok=False leaves=0 tier=%s hinges=- winchAt=- firstAt=- reason=too_long' % a[2]
            leaves = 1 if x2 - x1 - 1 <= MAX_LEAF_TIMBER else 2
            at = []
            if len(a) > 4 and a[4] == 'winch':
                for c in ([(x1 - 1, z)] if a[3] == 'A' else [(x2 + 1, z)]) if leaves == 1 else [(x1 - 1, z), (x2 + 1, z)]:
                    if not self.ground(c):
                        return 'DRAW ok=False leaves=%d tier=%s hinges=- winchAt=- firstAt=- reason=winch_square_built_on' % (leaves, a[2])
                    g['winches'][c] = {'hp': WINCH_HP, 'leaf': x1 + 2 - O[0]}
                    g['built'].add(c)
                    at.append('%d,%d' % c)
            g['leaves'][x1 + 2 - O[0]] = {'cells': range(x1 + 1, x2), 'z': z, 'progress': 0, 'target': 'lowered'}
            return 'DRAW ok=True leaves=%d tier=%s hinges=%s winchAt=%s firstAt=%d,%d reason=-' % (
                leaves, a[2], a[3], '|'.join(at) or '-', x1, z)
        if method in ('ProofLeaf', 'ProofDevSet'):
            a = arg.split(';')
            if not re.fullmatch(XZ, a[0]) or (method == 'ProofLeaf' and len(a) != 1) or \
                    (method == 'ProofDevSet' and (len(a) < 2 or a[1] not in ('raise', 'lower'))):
                self.bad('%s given %r' % (method, arg))
                return 'REFUSED: bad args'
            x, z = (int(v) for v in a[0].split(','))
            leaf = next((l for l in g['leaves'].values() if x in l['cells'] and z == l['z']), None)
            if leaf is None:
                return 'LEAF none' if method == 'ProofLeaf' else 'REFUSED: not a drawbridge leaf square'
            dx = next(k for k, l in g['leaves'].items() if l is leaf)
            if method == 'ProofDevSet':
                leaf['target'] = 'raised' if a[1] == 'raise' else 'lowered'
                if len(a) > 2 and a[2] == 'instant':
                    leaf['progress'] = FULL if a[1] == 'raise' else 0
                return 'DEVSET target=%s progress=%d' % (leaf['target'], leaf['progress'])
            has = any(w['leaf'] == dx for w in g['winches'].values())
            return 'LEAF leaf=1/1 progress=%d full=%d target=%s raised=%d/3 frozen=False winch=%s powered=False hold=False ' \
                   'auto=False pending=none tip=False hinge=A version=1' % (leaf['progress'], FULL, leaf['target'],
                                                                           3 if leaf['progress'] else 0, has)
        if method == 'ProofFillWithFluid':          # the draft's water fill (x,z,metres,fluid): accepted, so its spawn_batch is reached
            return 'FILLED %s' % arg if re.fullmatch(r'-?\d+,-?\d+,[\d.]+,\w+', arg or '') else 'REFUSED: bad args'
        if typ == 'RimWorld.SappersUtility' and method in ('HasBuildingDestroyerWeapon', 'IsGoodSapper'):
            return 'True' if arg in g['pawns'] else 'REFUSED: no such pawn'
        raise AssertionError('unexpected static %s.%s %r' % (typ, method, arg))


def run(mod='healthy', fault=None):
    F = Fake(mod, fault)
    out = C.scene_islands(F, lambda: F.save('begin'), lambda: F.load('begin'), {'calls': []})
    return {r['id']: r['status'] for r in out['rows']}, out, F


FAILS = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else why))
    if not ok:
        FAILS.append(label)


ROWS = ('ISL_trapped_while_winches_stand', 'ISL_raiders_destroy_a_winch', 'ISL_lost_winch_drops_its_leaf',
        'ISL_raiders_escape', 'ISL_control_unbreakable_winches_stay_trapped')
check('the fake knows the real ThingDefs (RM_DrawbridgeGate in, RM_SuspensionBridge out)',
      'RM_DrawbridgeGate' in THINGDEFS and 'RM_SuspensionBridge' not in THINGDEFS, sorted(THINGDEFS)[:5])
rows, out, F = run()
check('every staging call keeps its tool contract (ThingDefs only; proof args; build rules)', not F.contract, F.contract)
check('the scene leaves the governor as it found it', F.stop_on == 'default', F.stop_on)
check('healthy fake (sappers take the west winch, its leaf crashes, they walk off; held winches hold): every row PASS',
      out['status'] == 'PASS' and all(rows.get(r) == 'PASS' for r in ROWS), (rows, [x['detail'] for x in out['rows']][:2]))
r, o, F = run(mod='nowinch')
check('sappers that never take a winch: that row FAILs, the staged loss still asks the drop and the escape (PASS)',
      r.get('ISL_raiders_destroy_a_winch') == 'FAIL' and r.get('ISL_lost_winch_drops_its_leaf') == 'PASS'
      and r.get('ISL_raiders_escape') == 'PASS' and 'staged=True' in str(o['rows']) and o['status'] != 'PASS', r)
r, o, _ = run(mod='nodrop')
check('a leaf that stays up after its winch falls: the drop FAILs, the escape UNMEASURED',
      r.get('ISL_lost_winch_drops_its_leaf') == 'FAIL' and r.get('ISL_raiders_escape') == 'UNMEASURED', r)
r, o, _ = run(fault='leaky')
check('raiders that walk off over raised leaves: the trap and the control FAIL',
      r.get('ISL_trapped_while_winches_stand') == 'FAIL' and r.get('ISL_control_unbreakable_winches_stay_trapped') == 'FAIL', r)
r, o, _ = run(fault='gone')
check('a raid that is gone at the first poll: every row UNMEASURED, none PASS',
      all(r.get(x) == 'UNMEASURED' for x in ROWS) and 'PASS' not in r.values(), r)
F = Fake()
_static = F.static
F.static = lambda typ, m, arg: ('REFUSED: no current map' if m == 'ProofLeaf' and F.g['pawns'] and F.g['announced']
                                else _static(typ, m, arg))
o = C.scene_islands(F, lambda: F.save('begin'), lambda: F.load('begin'), {'calls': []})
r = {x['id']: x['status'] for x in o['rows']}
check('a REFUSED leaf read mid-watch is never a lost winch: the scene stops UNMEASURED, no row PASS',
      'PASS' not in r.values() and r.get('scene_islands_staging') == 'UNMEASURED', r)
print('selftest_islands_scene: %s' % ('FAIL' if FAILS else 'ok'))
sys.exit(1 if FAILS else 0)
