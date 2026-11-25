#!/usr/bin/env python3
"""Offline half of sc_walk (RIMMANDRAKE_FINISH_FLOWWORKS_WALK_SCENE_HALF_THE_BAR_UNASKED): scene_walk_moat_season against a
fake engine. Every bar row is asked (pond pays, reload digest + pre-fill control, toggle digest, switch took, pays again,
no leftovers, log clean), the healthy fake reads all PASS, and each injected fault turns its row FAIL or UNMEASURED, never
PASS: a vacuous read (absent keys, a REFUSED census, a lost journal, no mid-way save) is UNMEASURED. The fake proves the
scene's logic, never the game; the live half is `python.exe concept_scenes.py --scene scene_walk_moat_season --out <json>`.
"""
from copy import deepcopy
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import concept_scenes as C  # noqa: E402

L_PER_DL = 200.0   # the readout's 1.00 m = 2,000 L at 10 dL a metre


class Fake:
    """A pond engine: dug cells hold water (dL); an active pulse levels each 4-connected dug component."""

    def __init__(self, fault=None):
        self.fault = fault
        self.g = {'dug': {}, 'water': {}, 'fluid': {}, 'pawns': {}}
        self.settings = {'depthEngineEnabled': True, 'depthEngineLiveForTests': False}
        self.at_load = True
        self.journal, self.seq = [{'Sequence': 100, 'Level': 'Message', 'Message': 'loaded', 'RepeatCount': 1}], 100
        self.saves = {}

    # ---- the engine
    def active(self):
        live = self.settings['depthEngineLiveForTests'] in (True, 'True') and self.fault != 'snap'
        return (self.settings['depthEngineEnabled'] in (True, 'True')) if live else self.at_load

    def level(self):
        if not self.active():
            return
        dug, seen = self.g['dug'], set()
        for c in dug:
            if c in seen:
                continue
            comp, todo = [], [c]
            while todo:
                q = todo.pop()
                if q in seen or q not in dug:
                    continue
                seen.add(q); comp.append(q)
                todo += [(q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] + 1), (q[0], q[1] - 1)]
            total = sum(self.g['water'].get(q, 0.0) for q in comp)
            if self.fault == 'pond_endless':
                continue
            fl = next((self.g['fluid'][q] for q in comp if q in self.g['fluid']), None)
            for q in comp:
                self.g['water'][q] = total / len(comp)
                if fl and total and not (self.fault == 'leftover_fluid' and self.settings['depthEngineEnabled'] is True
                                         and q == comp[-1]):
                    self.g['fluid'][q] = fl
        for q, f in self.g['fluid'].items():
            if f == C.FUEL and self.fault == 'fuel_drains':
                self.g['water'][q] = self.g['water'].get(q, 0.0) / 2
            if f == C.FUEL and self.fault == 'fuel_turns_water':
                self.g['fluid'][q] = C.WATER
        if self.fault == 'leftover_fluid':
            for q in list(self.g['fluid'])[-1:]:
                del self.g['fluid'][q]
        if self.fault == 'fw_error':
            self.log('Error', 'Exception in RimMandrake.FlowWorks.RM_MapComponent_Excavation.Pulse: NullReferenceException')
        self.log('Message', 'some other mod chatters')

    def log(self, level, msg):
        self.seq += 50 if self.fault == 'lost' else 1
        self.journal.append({'Sequence': self.seq, 'Level': level, 'Message': msg, 'RepeatCount': 1})

    def ticks(self, n):
        if n >= 250:
            self.level()

    # ---- saves (the scene-begin snapshot and the mid-way save)
    def save(self, name):
        self.saves[name] = deepcopy(self.g)

    def load(self, name):
        self.g = deepcopy(self.saves[name])
        if self.fault == 'reload_loses_water' and name == 'mid':
            self.g['water'] = {}
        if self.fault == 'swimmer_moved' and name == 'mid':
            self.g['pawns'] = {k: (c[0], c[1] - 3) for k, c in self.g['pawns'].items()}
        self.at_load = self.settings['depthEngineEnabled'] in (True, 'True')

    # ---- the bridge
    def call(self, tool, **kw):
        g = self.g
        if tool == 'jawa/flowworks_excavation_drive':
            c = (kw['x'], kw['z'])
            g['dug'][c] = g['dug'].get(c, 0) + kw['deepenLevels']
            return {'success': True}
        if tool == 'jawa/flowworks_excavation_rect':
            blind = lambda c: self.fault == 'fuel_blind' and g['fluid'].get(c) == C.FUEL   # noqa: E731
            return {'success': True, 'rows': [{'x': x, 'z': z, 'dl': None if blind((x, z)) else round(g['water'].get((x, z), 0.0), 3)}
                                              for x in range(kw['x'], kw['x'] + kw['w']) for z in range(kw['z'], kw['z'] + kw['h'])]}
        if tool == 'jawa/flowworks_pulse':
            for _ in range(min(kw.get('count', 1), 3)):
                self.level()
            return {'success': True}
        if tool == 'jawa/flowworks_engine_state':
            e = {'success': True, 'depthEngineEnabled': self.settings['depthEngineEnabled'], 'nextPulseTick': 1}
            if self.fault != 'blind_keys':
                e.update(excavatedCellCount=len(g['dug']), superdeepCellCount=len(g['dug']), bodyCount=0, activeFluid=C.WATER)
            return e
        if tool == 'jawa/mod_settings_field':
            if kw['action'] == 'get':
                return {'success': True, 'value': self.settings.get(kw['field'])}
            v = kw['value']
            self.settings[kw['field']] = {'True': True, 'False': False}.get(v, v)
            return {'success': True}
        if tool == 'rimbridge/list_logs':
            after = kw.get('afterSequence')
            logs = [e for e in self.journal if after is None or e['Sequence'] > after]
            if kw.get('minimumLevel') == 'warning':
                logs = [e for e in logs if e['Level'] != 'Message']
            return {'success': True, 'logs': logs[-kw.get('limit', 1000):]}
        if tool == 'jawa/spawn_pawn':
            pid = 'Human%d' % (len(g['pawns']) + 1)
            g['pawns'][pid] = (kw['x'], kw['z'] + (10 if self.fault == 'spawn_ashore' else 0))
            return {'success': True, 'pawns': [{'id': pid}]}
        if tool == 'jawa/order_pawn':
            if kw['pawnId'] in g['pawns']:
                g['pawns'][kw['pawnId']] = (kw['x'], kw['z'])
            return {'success': True}
        if tool == 'jawa/static_call':
            return {'success': True, 'result': self.static(kw['type'], kw['method'], kw.get('args', ''))}
        raise AssertionError('unexpected tool %s %s' % (tool, kw))

    def static(self, typ, method, arg):
        g = self.g
        if method == 'Warning':
            self.log('Warning', arg)
            return None
        if method == 'ProofFillWithFluid':
            x, z, m, fl = arg.split(',')
            c = (int(x), int(z))
            if c not in g['dug']:
                return 'REFUSED: not excavated'
            g['water'][c] = float(m) * 10
            if not (self.fault == 'fuel_unrecorded' and fl == C.FUEL):
                g['fluid'][c] = fl
            return 'FILLED %s' % (c,)
        if method == 'ProofReadout':
            c = tuple(int(v) for v in arg.split(','))
            if c not in g['dug']:
                return 'OK -'
            w = g['water'].get(c, 0.0)
            return 'OK Hole %g m · Water %.2f m (%s L)' % (g['dug'][c] / 2.0, w / 10, format(int(round(w * L_PER_DL)), ','))
        if method == 'ProofPawnSink':
            if arg not in g['pawns']:
                return 'REFUSED: no spawned pawn ' + arg
            c = g['pawns'][arg]
            return 'SINK id=%s cell=%d,%d depth=%d waterDl=%d fluid=none sink=0 drawDz=0 moving=False enabled=True' % (
                arg, c[0], c[1], g['dug'].get(c, 0), g['water'].get(c, 0))
        if method == 'ProofSwim':
            c = tuple(int(v) for v in arg.split(','))
            for pid, at in g['pawns'].items():
                if at == c:
                    w = g['water'].get(c, 0.0) / 10 if c in g['dug'] else 0.0
                    return 'SWIM %s class=Swimmer natural=False load=0.00 water=%.2f deepCell=%s exhaustion=0.000' % (
                        pid, w, w >= 1.8)
            return 'REFUSED: no pawn at %s' % (c,)
        if method == 'ProofCensus':
            if self.fault == 'refused_census':
                return 'REFUSED: no excavation component on the current map'
            wet = [c for c in g['dug'] if g['water'].get(c, 0) > 0]
            rec = [c for c in wet if c in g['fluid']]
            return 'FLUIDID wet %d | recorded %d | unrecorded %d | fluids [%s] | bodies []' % (
                len(wet), len(rec), len(wet) - len(rec), ','.join(sorted({g['fluid'][c] for c in rec})))
        raise AssertionError('unexpected static %s.%s' % (typ, method))


def run(fault=None):
    F = Fake(fault)
    receipt = {'calls': []}
    hooks = {} if fault == 'no_hooks' else {'save_mid': lambda: F.save('mid'), 'load_mid': lambda: F.load('mid')}
    out = C.scene_walk_moat_season(F, lambda: F.save('begin'), lambda: F.load('begin'), receipt, **hooks)
    return {r['id']: r['status'] for r in out['rows']}, out, F


FAILS = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else why))
    if not ok:
        FAILS.append(label)


BAR = ('WALK_pond_pays', 'WALK_reload_digest_matches', 'WALK_control_prefill_reload_differs', 'WALK_toggle_off_on_digest_matches',
       'WALK_switch_off_holds_water', 'WALK_pond_pays_again', 'WALK_no_leftovers', 'WALK_log_clean',
       'WALK_swimmer_survives_reload', 'WALK_second_order_pond_pays', 'WALK_second_order_fuel_holds',
       'WALK_second_order_no_leftovers')

rows, out, F = run()
check('every bar row is asked (pond pays again, no leftovers, log clean among them)', set(BAR) <= set(rows), sorted(rows))
check('the healthy fake reads every row PASS and the scene PASS', out['status'] == 'PASS' and set(rows.values()) == {'PASS'}, rows)
check('settings poked are restored (live switch off again, engine on)',
      F.settings == {'depthEngineEnabled': True, 'depthEngineLiveForTests': False}, F.settings)

# each fault: the row it must catch, and the verdict it must read (never PASS)
CASES = (
    ('reload_loses_water', 'WALK_reload_digest_matches', 'FAIL'),
    ('snap', 'WALK_switch_off_holds_water', 'FAIL'),            # the off/on never reached the engine (the visit-1 draft)
    ('pond_endless', 'WALK_pond_pays', 'FAIL'),
    ('pond_endless', 'WALK_pond_pays_again', 'FAIL'),
    ('leftover_fluid', 'WALK_no_leftovers', 'FAIL'),
    ('fw_error', 'WALK_log_clean', 'FAIL'),
    ('lost', 'WALK_log_clean', 'UNMEASURED'),                    # a journal gap is not a clean log
    ('blind_keys', 'WALK_toggle_off_on_digest_matches', 'UNMEASURED'),   # absent keys: None == None must not pass
    ('blind_keys', 'WALK_reload_digest_matches', 'UNMEASURED'),
    ('refused_census', 'WALK_no_leftovers', 'UNMEASURED'),
    ('refused_census', 'WALK_toggle_off_on_digest_matches', 'UNMEASURED'),
    ('no_hooks', 'WALK_reload_digest_matches', 'UNMEASURED'),
    # holder run-1794816885: the swimmer at the mid-way save, and the second order (chemfuel first, water drained after)
    ('swimmer_moved', 'WALK_swimmer_survives_reload', 'FAIL'),        # the red: the swimmer is not where the save had it
    ('reload_loses_water', 'WALK_swimmer_survives_reload', 'FAIL'),   # "the swimmers stand on the bed"
    ('spawn_ashore', 'WALK_swimmer_survives_reload', 'UNMEASURED'),   # nobody was in the water at the save
    ('no_hooks', 'WALK_swimmer_survives_reload', 'UNMEASURED'),
    ('blind_keys', 'WALK_swimmer_survives_reload', 'UNMEASURED'),
    ('fuel_drains', 'WALK_second_order_fuel_holds', 'FAIL'),
    ('fuel_turns_water', 'WALK_second_order_no_leftovers', 'FAIL'),
    ('fuel_unrecorded', 'WALK_second_order_no_leftovers', 'FAIL'),
    ('fuel_blind', 'WALK_second_order_fuel_holds', 'UNMEASURED'),
    ('refused_census', 'WALK_second_order_no_leftovers', 'UNMEASURED'),
    ('pond_endless', 'WALK_second_order_pond_pays', 'FAIL'),
)
for fault, rid, want in CASES:
    r, o, _ = run(fault)
    check('fault %s: %s reads %s' % (fault, rid, want), r.get(rid) == want and o['status'] != 'PASS', (r.get(rid), r))

# the three split scenes (RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES): each asks only its own rows, reads
# all PASS on the healthy fake, and each fault turns the row it owns red (never PASS) in the scene that owns it
SPLIT = {
    'scene_walk_reload': ('WALK_reload_digest_matches', 'WALK_swimmer_survives_reload', 'WALK_control_prefill_reload_differs',
                          'WALK_log_clean'),
    'scene_walk_switch': ('WALK_pond_pays', 'WALK_toggle_off_on_digest_matches', 'WALK_switch_off_holds_water',
                          'WALK_pond_pays_again', 'WALK_no_leftovers', 'WALK_log_clean'),
    'scene_walk_second_order': ('WALK_second_order_pond_pays', 'WALK_second_order_fuel_holds',
                                'WALK_second_order_no_leftovers', 'WALK_log_clean'),
}


def run_split(name, fault=None):
    F = Fake(fault)
    receipt = {'calls': []}
    hooks = {} if fault == 'no_hooks' else {'save_mid': lambda: F.save('mid'), 'load_mid': lambda: F.load('mid')}
    out = C.STAGE3_SCENES[name](F, lambda: F.save('begin'), lambda: F.load('begin'), receipt, **hooks)
    return {r['id']: r['status'] for r in out['rows']}, out, F


covered = set()
for name, want_rows in SPLIT.items():
    r, o, f = run_split(name)
    check('%s asks exactly its own rows' % name, sorted(r) == sorted(want_rows), sorted(r))
    check('%s: the healthy fake reads every row PASS' % name, o['status'] == 'PASS' and set(r.values()) == {'PASS'}, r)
    check('%s restores the settings it poked' % name,
          f.settings == {'depthEngineEnabled': True, 'depthEngineLiveForTests': False}, f.settings)
    covered |= set(want_rows)
check('the three split scenes ask every sc_walk bar row between them', set(BAR) <= covered, sorted(set(BAR) - covered))
for fault, rid, want in CASES:
    owner = next(n for n, rows_ in SPLIT.items() if rid in rows_ and rid != 'WALK_log_clean') if rid != 'WALK_log_clean' \
        else 'scene_walk_switch'
    r, o, _ = run_split(owner, fault)
    check('split %s, fault %s: %s reads %s' % (owner, fault, rid, want), r.get(rid) == want and o['status'] != 'PASS',
          (r.get(rid), r))
for name in ('scene_walk_reload', 'scene_walk_second_order'):     # the log row is each scene's own
    for fault, want in (('fw_error', 'FAIL'), ('lost', 'UNMEASURED')):
        r, o, _ = run_split(name, fault)
        check('split %s, fault %s: WALK_log_clean reads %s' % (name, fault, want), r.get('WALK_log_clean') == want, r)
r, o, _ = run_split('scene_walk_reload')
ticks_gap = [c for c in o['calls'] if c['tool'] == 'jawa/flowworks_excavation_drive']
check('sc_walk_reload stages only the pond and the swim pool (18 squares dug, no moat)', len(ticks_gap) == 18, len(ticks_gap))

check('vacuous reads: None, REFUSED, an all-zero vector', C._vacuous(None) and C._vacuous('REFUSED x') and C._vacuous((0, 0, None))
      and C._vacuous((0, 0.0)) and not C._vacuous((21, 21, 0, C.WATER, 'FLUIDID wet 21', 400.0)))
check('litres parse: the live readout line, a dry hole, a blind line',
      C._litres('OK Hole 2 m · Water 1.00 m (2,000 L)') == 2000.0 and C._litres('OK Hole 2 m') == 0.0
      and C._litres('OK -') is None and C._litres('REFUSED x') is None)
print('selftest_walk_scene: %s' % ('FAIL' if FAILS else 'ok'))
sys.exit(1 if FAILS else 0)
