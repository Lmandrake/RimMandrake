#!/usr/bin/env python3
"""Offline half of sc_pit_trap_raid (RIMMANDRAKE_REBUILD_FLOWWORKS_PITTRAP_SCENE_STOPPED_BY_OWN_RAID): scene_pit_trap_raid
against a fake map that holds each bridge tool to its contract and models what sank visit 1 (2026-11-15, rows.jsonl
sc_pit_trap_raid_20261115T132552): the governor. A hostile on the map at arm stops jawa/safe_advance (GovernorStop
hostile_arrival, "present at arm") unless the scene narrows B.stop_on for its own raid; the draft ran S.ticks(4000) right
after fire_raid on the default list and died at tick 60 with no rows.
  - every jawa/ call names only parameters its C# [Tool] declares (the signature reader of selftest_bridge_args), and the
    staging keeps each tool's contract: ProofCover is a read-only x,z probe, set_plants names a def, a lid rests on two
    banks, RM_CaptureDown is ordered by a spawned colonist on a held raider from an undug square beside it;
  - the healthy fake (two fall onto the spikes, the warden captures both from the lip, the open pit holds nobody) reads
    every row PASS; a mod whose capture never makes a prisoner, and an open pit raiders fall into, read their rows FAIL;
  - a raid that never reaches the trench, a raid of nobody (an all-zero watch), a cover that never springs, and REFUSED
    ProofTrap / ProofCaptureDown replies read UNMEASURED, never PASS.
Red on the draft at 2b4bffe212, green on the fix. The fake proves the scene's logic, never the game; the live half is
`python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_pit_trap_raid --out <json>`.
    python3 selftest_pit_trap_raid_scene.py [path/to/concept_scenes.py]
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
    """mod: 'capture' (RM_CaptureDown makes a held raider a prisoner), None (the order is taken, nobody becomes one),
    'falls_open' (raiders walk into an open trench and are held). fault: 'far' (the raid spawns 40 squares off), 'zero'
    (fire_raid spawns nobody), 'nofall' (the lids never give way), 'refuse_capture' (ProofCaptureDown REFUSED),
    'refuse_trap' (ProofTrap REFUSED)."""

    def __init__(self, mod='capture', fault=None):
        self.mod, self.fault = mod, fault
        self.stop_on = 'default'
        self.g = {'dug': {}, 'spikes': set(), 'covers': {}, 'hostile': {}, 'player': {}, 'orders': {}, 'settings': {},
                  'n': 0, 'ticked': 0}
        self.saves, self.contract, self.stops = {}, [], []

    def save(self, k):
        self.saves[k] = deepcopy(self.g)

    def load(self, k):
        settings = self.g['settings']           # settings are not part of the map: they stay as poked until restored
        self.g = deepcopy(self.saves[k])
        self.g['settings'] = settings

    # ---- the clock and the governor (validation_core.Bridge.ticks over jawa/safe_advance)
    def ticks(self, n):
        g = self.g
        stops = self.stop_on == 'default' or 'hostile_arrival' in self.stop_on.split(',')
        if stops and g['hostile']:
            first = sorted(g['hostile'])[0]
            r = {'state': 'stopped', 'executed': 60, 'requested': min(n, 2500),
                 'stopBy': {'kind': 'hostile_arrival', 'severity': 'threat', 'subjectId': first,
                            'detail': 'present at arm: Human Thrasher (humanlike)'}}
            self.stops.append(r)
            raise clockgate.GovernorStop(r)
        g['ticked'] += n
        for hid, h in sorted(g['hostile'].items()):
            if h['held'] or self.fault == 'far':
                continue
            nz = min(h['z'] + n // 100, O[1] + 9)
            cell = (h['x'], O[1])
            if h['z'] < O[1] <= nz and g['covers'].get(cell) and self.fault != 'nofall':
                h['z'], h['held'] = O[1], True
                if sum(1 for q in g['hostile'].values() if q['held']) >= 2:
                    for c in g['covers']:
                        g['covers'][c] = False      # the deck gives way whole
                continue
            if h['z'] < O[1] <= nz and cell in g['dug'] and not g['covers'].get(cell):
                if self.mod == 'falls_open':
                    h['z'], h['held'] = O[1], True
                    continue
                nz = O[1] - 1                       # an open trench: they stop at its lip
            h['z'] = nz
        for pid, warden in list(g['orders'].items()):
            h = g['hostile'].get(pid)
            if self.mod == 'capture' and h and h['held'] and n >= 300 and self._verdict(pid) == 'Allowed':
                h['prisoner'] = True
            del g['orders'][pid]
        return {'success': True, 'advanced': n}

    def _verdict(self, pid):
        h = self.g['hostile'][pid]
        if self.g['settings'].get('captureDownEnabled') != 'True':
            return 'SettingOff'
        if h.get('prisoner'):
            return 'AlreadyPrisoner'
        return 'Allowed' if h['held'] else 'NotHeld'

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
            if not all(k in kw for k in ('kindDef', 'x', 'z', 'faction')):
                self.contract.append('spawn_pawn without kindDef/x/z/faction: %s' % kw)
            g['n'] += 1
            pid = 'Human%d' % (900 + g['n'])
            if kw.get('faction') == 'player':
                g['player'][pid] = (kw['x'], kw['z'])
            return {'success': True, 'pawns': [{'id': pid}]}
        if tool == 'jawa/fire_raid':
            if kw.get('dryRun') is not False or not XZ.match(str(kw.get('spawnCenter', ''))):
                self.contract.append('fire_raid not a placed live raid: %s' % kw)
            cx, cz = (int(v) for v in str(kw.get('spawnCenter') or '%d,%d' % (O[0], O[1] - 20)).split(','))
            if self.fault == 'far':
                cz -= 40
            for i in range(0 if self.fault == 'zero' else 6):
                g['n'] += 1
                g['hostile']['Human%d' % (500 + g['n'])] = {'x': cx - 2 + i % 5, 'z': cz - i // 5, 'held': False}
            return {'success': True, 'executed': True}
        if tool == 'jawa/list_pawns':
            ps = [{'id': k, 'x': h['x'], 'z': h['z'], 'dead': False} for k, h in g['hostile'].items()] \
                if kw.get('faction') == 'hostile' else []
            if kw.get('rect'):
                x, z, w, hh = (int(v) for v in kw['rect'].split(','))
                ps = [p for p in ps if x <= p['x'] < x + w and z <= p['z'] < z + hh]
            return {'success': True, 'pawns': ps}
        if tool == 'jawa/list_things':
            if not re.match(r'^-?\d+,-?\d+,\d+,\d+$', kw.get('rect', '')):
                self.contract.append('list_things rect not x,z,w,h: %r' % kw.get('rect'))
            return {'success': True, 'things': []}
        if tool == 'jawa/ordered_job':
            pid, w = kw.get('targetAId'), kw.get('pawnId')
            h = g['hostile'].get(pid)
            lip = (kw.get('targetBX'), kw.get('targetBZ'))
            if kw.get('jobDef') != 'RM_CaptureDown' or w not in g['player'] or h is None:
                self.contract.append('ordered_job is no RM_CaptureDown by a colonist on a raider: %s' % kw)
                return {'success': True, 'accepted': False}
            if lip in g['dug'] or None in lip or C._cheb(lip, (h['x'], h['z'])) > 1:
                self.contract.append('RM_CaptureDown lip %s is no undug square beside %s' % (lip, (h['x'], h['z'])))
                return {'success': True, 'accepted': False}
            g['orders'][pid] = w
            return {'success': True, 'accepted': True, 'requestedJobDef': 'RM_CaptureDown'}
        if tool == 'jawa/static_call':
            return {'success': True, 'result': self.static(kw['type'], kw['method'], kw.get('args', ''))}
        if tool == 'jawa/mod_settings_field':
            if kw.get('action') == 'set':
                g['settings'][kw['field']] = kw['value']
            return {'success': True, 'value': g['settings'].get(kw['field'], 'False')}
        raise AssertionError('unexpected tool %s %s' % (tool, kw))

    def static(self, typ, method, arg):
        g = self.g
        if method == 'ProofCover':
            if not XZ.match(arg or ''):
                self.contract.append('ProofCover given %r (its contract is x,z)' % arg)
                return 'REFUSED: arg must be x,z on a current map with FlowWorks'
            c = tuple(int(v) for v in arg.split(','))
            return 'COVER cell=%d,%d present=%s covered=%s sprung=False' % (c + (c in g['covers'], g['covers'].get(c, False)))
        if method in ('ProofTrap', 'ProofCaptureDown'):
            if not isinstance(arg, str):
                self.contract.append('%s given %r (its contract is a pawn id string)' % (method, arg))
            h = g['hostile'].get(arg)
            if h is None or self.fault == ('refuse_trap' if method == 'ProofTrap' else 'refuse_capture'):
                return 'REFUSED: no spawned pawn %s' % arg
            if method == 'ProofTrap':
                return 'TRAP descents=1 lastCell=none pos=%d,%d held=%s last=-' % (h['x'], h['z'], h['held'])
            return 'VERDICT %s held=%s prisoner=%s cell=%d,%d' % (self._verdict(arg), h['held'], bool(h.get('prisoner')),
                                                                 h['x'], h['z'])
        raise AssertionError('unexpected static %s.%s' % (typ, method))


ROWS = ('PTR_two_fall', 'PTR_fallen_become_prisoners', 'PTR_control_open_pit_no_one_falls')


def run(mod='capture', fault=None):
    F = Fake(mod, fault)
    try:
        out = C.scene_pit_trap_raid(F, lambda: F.save('begin'), lambda: F.load('begin'), {'calls': []})
    except Exception as e:                       # noqa: BLE001 - a GovernorStop out of the scene is the visit-1 failure
        return {}, {'status': 'CRASH', 'rows': [], 'error': repr(e)[:300]}, F
    return {r['id']: r['status'] for r in out['rows']}, out, F


FAILS = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else str(why)[:600]))
    if not ok:
        FAILS.append(label)


print('under test: %s' % SRC)
rows, out, F = run()
check('the scene\'s own raid never stops the clock (no GovernorStop hostile_arrival; visit 1 died at tick 60 of it)',
      not F.stops and out['status'] != 'CRASH', out.get('error') or F.stops[:1])
check('every staging call keeps its tool contract (C# parameters, ProofCover x,z, set_plants def, lids on two banks, '
      'RM_CaptureDown by a colonist from an undug lip)', not F.contract, F.contract)
check('the scene leaves the governor as it found it', F.stop_on == 'default', F.stop_on)
check('healthy fake (two fall, both captured from the lip, the open pit holds nobody): every row PASS',
      out['status'] == 'PASS' and all(rows.get(r) == 'PASS' for r in ROWS), rows)
r, o, _ = run(mod=None)
check('a mod whose capture makes no prisoner: PTR_fallen_become_prisoners FAIL, the fall and the control PASS',
      r.get('PTR_fallen_become_prisoners') == 'FAIL' and r.get('PTR_two_fall') == 'PASS'
      and r.get('PTR_control_open_pit_no_one_falls') == 'PASS' and o['status'] == 'FAIL', r)
r, o, _ = run(mod='falls_open')
check('raiders that fall into the open pit: the control FAILs', r.get('PTR_control_open_pit_no_one_falls') == 'FAIL', r)
for fault, label in (('far', 'a raid that never reaches the trench'), ('zero', 'a raid of nobody (an all-zero watch)')):
    r, o, _ = run(fault=fault)
    check('%s: every row UNMEASURED, none PASS' % label,
          all(r.get(x) == 'UNMEASURED' for x in ROWS) and 'PASS' not in r.values() and o['status'] != 'PASS', r)
r, o, _ = run(fault='nofall')
check('lids that never give way (nobody fell): PTR_two_fall FAIL, the capture UNMEASURED, never PASS',
      r.get('PTR_two_fall') == 'FAIL' and r.get('PTR_fallen_become_prisoners') == 'UNMEASURED', r)
r, o, _ = run(fault='refuse_capture')
check('ProofCaptureDown REFUSED: the capture row UNMEASURED, never PASS or FAIL',
      r.get('PTR_fallen_become_prisoners') == 'UNMEASURED' and o['status'] != 'PASS', r)
r, o, _ = run(fault='refuse_trap')
check('ProofTrap REFUSED: the fall row UNMEASURED, never PASS', r.get('PTR_two_fall') == 'UNMEASURED'
      and 'PASS' not in (r.get('PTR_two_fall'), r.get('PTR_fallen_become_prisoners')), r)
r, o, _ = run(mod='falls_open', fault='refuse_trap')
check('ProofTrap REFUSED on raiders standing in the open pit: the control UNMEASURED, never PASS',
      r.get('PTR_control_open_pit_no_one_falls') == 'UNMEASURED', r)
print('selftest_pit_trap_raid_scene: %s (%d failed)' % ('FAIL' if FAILS else 'ok', len(FAILS)))
sys.exit(1 if FAILS else 0)
