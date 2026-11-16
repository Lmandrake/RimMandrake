#!/usr/bin/env python3
"""Offline half of sc_source_pays (RIMMANDRAKE_REBUILD_FLOWWORKS_SOURCE_PAYS_SCENE_POND_NEVER_THERE): scene_source_pays
against a fake engine (dug squares hold water to one surface per dug component, an RM_FlowSink map control, rain while the
weather is locked to Rain, an optional limitless body). It checks:
  (a) every staging call matches its bridge tool's contract (the C# [Tool] parameters, and the static_call methods' C#
      parameter counts), and every filled square was dug first;
  (b) the healthy calm fake reads every bar row PASS but SRC_lake_reads_endless, which reads UNMEASURED with its reason (the
      calm site has no limitless body), and a fake map with one reads it PASS;
  (c) a vacuous read (REFUSED readout, an all-zero vector, a sink never placed, a draw or a rain that never happened) reads
      UNMEASURED, and a planted fault (pays nothing, shore frozen, tap 0 drains, never empties, never refills, refills at
      once, the endless body drops) turns its row FAIL. Never PASS.
`--rev 2b4bffe212` runs the same checks against the visit-1 draft (git show into a temp dir): it must exit 1 (RED).
The fake proves the scene's logic, never the game; the live half is
`python.exe concept_scenes.py --scene scene_source_pays --out <json>`.
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
U = 1000.0          # fake decilitres per notch (rect dl); the readout: a notch is 0.5 m and 500 L
LAKE_CELL = (105, 135)
_TMP = None


def bridge_contract():
    """signatures() and check_source() from selftest_bridge_args.py, without running its checks."""
    src = (HERE / 'selftest_bridge_args.py').read_text(encoding='utf-8').split('\nFAILS = []')[0]
    ns = {'__file__': str(HERE / 'selftest_bridge_args.py'), '__name__': 'bridge_args_lib'}
    exec(compile(src, 'selftest_bridge_args.py', 'exec'), ns)
    return ns['signatures'](), ns['check_source']


def static_params(typ, method):
    """The C# parameter count of public static <method> in the class named by `typ`; None when no such method."""
    short = typ.rsplit('.', 1)[-1]
    for f in glob.glob(str(ROOT / 'src/RimMandrake/FlowWorks/Source/**/*.cs'), recursive=True):
        txt = open(f, encoding='utf-8', errors='ignore').read()
        if not re.search(r'\bclass %s\b' % short, txt):
            continue
        m = re.search(r'public static \w+ %s\(([^)]*)\)' % method, txt)
        if m:
            return len([p for p in m.group(1).split(',') if p.strip()])
    return None


class Fake:
    def __init__(self, fault=None, lake=False, sigs=None):
        self.fault, self.lake, self.sigs = fault, lake, sigs or {}
        self.dug, self.water = {}, {}
        self.sinks, self.nid = {}, 0
        self.weather, self.tick_rem = 'Clear', 0
        self.stock = 1.0e6
        self.bad, self.statics, self.fill_undug = [], set(), []

    # ---- the engine
    def comps(self):
        seen = set()
        for c in self.dug:
            if c in seen:
                continue
            comp, todo = [], [c]
            while todo:
                q = todo.pop()
                if q in seen or q not in self.dug:
                    continue
                seen.add(q); comp.append(q)
                todo += [(q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] + 1), (q[0], q[1] - 1)]
            yield comp

    def surface(self, comp, vol):
        """The one surface (notches relative to the brim, <= 0) that holds vol over this component's floors."""
        lo, hi = -max(self.dug[q] for q in comp), 0.0
        if vol >= sum(self.dug[q] for q in comp):
            return 0.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if sum(max(0.0, mid + self.dug[q]) for q in comp) > vol:
                hi = mid
            else:
                lo = mid
        return lo

    def level(self):
        if self.fault == 'pays_nothing':
            return
        for comp in self.comps():
            if len(comp) < 2:
                continue
            frozen = {q: self.water.get(q, 0.0) for q in comp if self.fault == 'shore_frozen' and self.dug[q] == 1}
            h = self.surface(comp, sum(self.water.get(q, 0.0) for q in comp))
            for q in comp:
                self.water[q] = frozen.get(q, max(0.0, h + self.dug[q]))

    def one_pulse(self):
        if self.weather == 'Rain' and self.fault not in ('never_refills', 'no_rain'):
            for q in self.dug:
                self.water[q] = self.dug[q] if self.fault == 'instant_refill' else min(self.dug[q], self.water.get(q, 0.0) + 0.1)
        for (sx, sz), s in self.sinks.items():
            reach = [q for q in ((sx, sz), (sx + 1, sz), (sx - 1, sz), (sx, sz + 1), (sx, sz - 1)) if q in self.dug]
            cap = 100.0 if s['rate'] < 0 else (5.0 if self.fault == 'zero_tap_drains' else s['rate'])
            for q in reach:
                comp = next(c for c in self.comps() if q in c)
                vol = sum(self.water.get(p, 0.0) for p in comp)
                floor = -self.dug[q]
                above = vol - sum(max(0.0, floor + self.dug[p]) for p in comp)   # what can still run down to this square
                take = min(cap, max(0.0, above))
                if take <= 0:
                    continue
                h = self.surface(comp, vol - take)
                for p in comp:
                    self.water[p] = max(0.0, h + self.dug[p])
                s['drained'] += take
                if self.fault == 'endless_pond':            # the source never runs dry: what the sink took comes back
                    h = self.surface(comp, vol)
                    for p in comp:
                        self.water[p] = max(0.0, h + self.dug[p])
        if self.lake:
            for q in self.dug:
                if abs(q[0] - LAKE_CELL[0]) + abs(q[1] - LAKE_CELL[1]) == 1:
                    took = self.dug[q] - self.water.get(q, 0.0)
                    self.water[q] = float(self.dug[q])
                    if self.fault == 'lake_drops':
                        self.stock -= took
        self.level()

    def ticks(self, n):
        self.tick_rem += n
        while self.tick_rem >= 250:
            self.tick_rem -= 250
            self.one_pulse()

    def bodies(self):
        return [{'id': 7, 'limitless': True, 'stock': self.stock, 'capacity': 1.0e6, 'cellCount': 900}] if self.lake else \
            [{'id': 3, 'limitless': False, 'stock': 40.0, 'capacity': 40.0, 'cellCount': 12}]

    # ---- the bridge
    def call(self, tool, **kw):
        if tool.startswith('jawa/'):
            if tool not in self.sigs:
                self.bad.append('unknown tool %s' % tool)
            else:
                self.bad += ['%s has no parameter %s' % (tool, k) for k in kw if k not in self.sigs[tool]]
        if tool == 'jawa/flowworks_excavation_drive':
            c = (kw['x'], kw['z'])
            self.dug[c] = self.dug.get(c, 0) + kw['deepenLevels']
            return {'success': True}
        if tool == 'jawa/flowworks_excavation_rect':
            dl = lambda c: 0 if self.fault == 'zero_rect' else round(self.water.get(c, 0.0) * U)
            return {'success': True, 'rows': [{'x': x, 'z': z, 'dl': dl((x, z))} for x in range(kw['x'], kw['x'] + kw['w'])
                                              for z in range(kw['z'], kw['z'] + kw['h']) if (x, z) in self.dug]}
        if tool == 'jawa/flowworks_pulse':
            for _ in range(kw.get('count', 1)):
                self.one_pulse()
            p = {'pulse': kw.get('count', 1)}
            if kw.get('includeBodies') and self.fault != 'refused_bodies':
                p['bodies'] = self.bodies()
            return {'success': True, 'pulses': [p]}
        if tool == 'jawa/weather_set':
            if kw.get('unlock'):
                self.weather = 'Clear'
            elif kw.get('weather') and self.fault != 'no_rain':
                self.weather = kw['weather']
            return {'success': True}
        if tool == 'jawa/weather_get':
            return {'success': True, 'weather': {'current': self.weather, 'rainRate': 1.0 if self.weather == 'Rain' else 0.0}}
        if tool == 'jawa/spawn_batch':
            return {'success': True}
        if tool == 'jawa/mod_settings_field':
            return {'success': True, 'value': None}
        if tool == 'jawa/static_call':
            self.statics.add((kw['type'], kw['method'], len(kw.get('args', '').split('|')) if kw.get('args') else 0))
            return {'success': True, 'result': self.static(kw['type'], kw['method'], kw.get('args', ''))}
        raise AssertionError('unexpected tool %s %s' % (tool, kw))

    def static(self, typ, method, arg):
        if method == 'ProofFillWithFluid':
            x, z, m, _fl = arg.split(',')
            c = (int(x), int(z))
            if c not in self.dug:
                self.fill_undug.append(c)
                return 'REFUSED: not excavated'
            self.water[c] = min(float(self.dug[c]), float(m) * 2)
            return 'FILLED %s W=%ddL' % (c, self.water[c] * U)
        if method == 'ProofReadout':
            if self.fault == 'refused_readout':
                return 'REFUSED no current map'
            c = tuple(int(v) for v in arg.split(','))
            if self.lake and c == LAKE_CELL:
                return 'OK Endless (about 3 m deep)'
            if c not in self.dug:
                return 'OK -'
            w = self.water.get(c, 0.0)
            return 'OK Hole %g m · Water %.2f m (%s L)' % (self.dug[c] / 2.0, w / 2, format(int(round(w * 500)), ','))
        if method == 'PlaceSink':
            cell, _filter, rate = arg.split('|')
            c = tuple(int(v) for v in cell.split(','))
            if self.fault == 'sink_refused' or c in self.sinks:
                return 'REFUSED: a map control already stands at (%d, 0, %d)' % c
            self.nid += 1
            self.sinks[c] = {'id': 'RM_FlowSink%d' % self.nid, 'rate': float(rate), 'drained': 0.0}
            return 'OK ' + self.line(c)
        if method == 'Remove':
            c = next((k for k, s in self.sinks.items() if s['id'] == arg), None)
            if c is None:
                return 'REFUSED: not a FlowWorks map control'
            line = self.line(c)
            del self.sinks[c]
            return 'OK removed ' + line
        if method == 'Report':
            if self.fault == 'drained_blind':
                return 'REFUSED: no current map'
            return '\n'.join([self.line(c) for c in self.sinks] + ['controls=%d enabled=True drainedTotal=%.0f' % (
                len(self.sinks), sum(s['drained'] for s in self.sinks.values()))])
        raise AssertionError('unexpected static %s.%s(%s)' % (typ, method, arg))

    def line(self, c):
        s = self.sinks[c]
        return 'sink %s at %d,%d filter=any rate=%s active=True drained=%s' % (
            s['id'], c[0], c[1], 'unlimited' if s['rate'] < 0 else '%g' % s['rate'], ('%.3f' % s['drained']).rstrip('0').rstrip('.'))


def load_module(rev):
    """concept_scenes as it is now, or as it was at `rev` (git show into a temp dir; imported with this folder's paths)."""
    if not rev:
        import concept_scenes as C
        return C, 'working tree'
    rel = 'src/RimMandrake/FlowWorks/northstar/concept_scenes.py'
    src = subprocess.run(['git', '-C', str(ROOT), 'show', '%s:%s' % (rev, rel)], capture_output=True, text=True, timeout=60)
    if src.returncode != 0:
        raise SystemExit('git show %s failed: %s' % (rev, src.stderr.strip()))
    global _TMP   # kept until exit: inspect.getsource reads the file; the finalizer removes it
    _TMP = tempfile.TemporaryDirectory(prefix='source_pays_rev_')
    tmp = Path(_TMP.name) / 'concept_scenes.py'
    tmp.write_text(src.stdout, encoding='utf-8')
    mod = types.ModuleType('concept_scenes_at_%s' % rev)
    mod.__file__ = str(HERE / 'concept_scenes.py')          # its sys.path setup reads __file__: point it at this folder
    exec(compile(tmp.read_text(encoding='utf-8'), str(tmp), 'exec'), mod.__dict__)
    return mod, '%s (%s)' % (rev, tmp)


FAILS = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else str(why)[:600]))
    if not ok:
        FAILS.append(label)


BAR = ('SRC_pond_drops', 'SRC_shore_recedes', 'SRC_control_tap_zero', 'SRC_flow_stops_when_empty', 'SRC_refill_visible',
       'SRC_lake_reads_endless')
CASES = (   # (fault, lake map?, row, the verdict it must read)
    ('pays_nothing', False, 'SRC_pond_drops', 'FAIL'),
    ('pays_nothing', False, 'SRC_shore_recedes', 'FAIL'),
    ('shore_frozen', False, 'SRC_shore_recedes', 'FAIL'),         # false_pass: the number drops but the shore never moves
    ('zero_tap_drains', False, 'SRC_control_tap_zero', 'FAIL'),
    ('endless_pond', False, 'SRC_flow_stops_when_empty', 'FAIL'),  # red: the pond stays full however much is taken
    ('never_refills', False, 'SRC_refill_visible', 'FAIL'),
    ('instant_refill', False, 'SRC_refill_visible', 'FAIL'),       # false_pass: refill is instant
    ('lake_drops', True, 'SRC_lake_reads_endless', 'FAIL'),
    ('refused_readout', False, 'SRC_pond_drops', 'UNMEASURED'),
    ('refused_readout', False, 'SRC_refill_visible', 'UNMEASURED'),
    ('refused_readout', False, 'SRC_control_tap_zero', 'UNMEASURED'),
    ('zero_rect', False, 'SRC_shore_recedes', 'UNMEASURED'),       # an all-zero vector
    ('zero_rect', False, 'SRC_pond_drops', 'UNMEASURED'),
    ('zero_rect', False, 'SRC_flow_stops_when_empty', 'UNMEASURED'),
    ('sink_refused', False, 'SRC_control_tap_zero', 'UNMEASURED'),
    ('sink_refused', False, 'SRC_flow_stops_when_empty', 'UNMEASURED'),
    ('drained_blind', False, 'SRC_flow_stops_when_empty', 'UNMEASURED'),
    ('no_rain', False, 'SRC_refill_visible', 'UNMEASURED'),        # an event that never happened
    ('refused_bodies', True, 'SRC_lake_reads_endless', 'UNMEASURED'),
)


def run(C, sigs, fault=None, lake=False):
    F = Fake(fault, lake, sigs)
    out = C.scene_source_pays(F, lambda: None, lambda: None, {'calls': []})
    return {r['id']: r['status'] for r in out['rows']}, out, F


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rev', help='run against concept_scenes.py at this commit (2b4bffe212 = the visit-1 draft: RED)')
    a = ap.parse_args()
    C, where = load_module(a.rev)
    print('scene under test: %s' % where)
    sigs, check_source = bridge_contract()
    import inspect
    fns = [getattr(C, n) for n in dir(C) if n == '_source_pays' or n.startswith('_src_')]
    probs = sum((check_source(inspect.getsource(f), sigs, f.__name__) for f in fns), [])
    check('(a) the scene source names only declared tool parameters (%d functions)' % len(fns), not probs and fns, probs)

    rows, out, F = run(C, sigs)
    for r in out['rows']:
        print('      healthy calm: %-26s %-10s %s' % (r['id'], r['status'], r['detail'][:90]))
    check('(a) every bridge call the scene made matched its C# [Tool] parameters', not F.bad, F.bad)
    st = sorted(F.statics)
    wrong = [(t, m, n, static_params(t, m)) for t, m, n in st if static_params(t, m) not in (n, 1)]
    check('(a) every static_call names a real C# method with that many | arguments %s' % [m for _, m, _ in st], not wrong, wrong)
    check('(a) every filled square was dug first', not F.fill_undug, F.fill_undug[:5])
    check('(b) every bar row is asked', set(BAR) <= set(rows), sorted(rows))
    want = {r: 'PASS' for r in BAR}
    want['SRC_lake_reads_endless'] = 'UNMEASURED'
    check('(b) the healthy calm fake reads every row PASS, the endless row UNMEASURED', rows == want, rows)
    lake = next((r['detail'] for r in out['rows'] if r['id'] == 'SRC_lake_reads_endless'), '')
    check('(b) the calm endless row states its reason (no limitless body, owed on the river site)',
          'no limitless body' in lake and 'river site' in lake, lake)
    check('(b) the calm scene is not PASS while a row is UNMEASURED', out['status'] != 'PASS', out['status'])
    r2, o2, F2 = run(C, sigs, lake=True)
    check('(b) a fake map with a limitless body reads every row PASS', set(r2.values()) == {'PASS'} and o2['status'] == 'PASS', r2)
    check('(b) the sinks came off and the weather lock was released', not F.sinks and F.weather == 'Clear', (F.sinks, F.weather))

    for fault, lk, rid, verdict in CASES:
        r, o, _ = run(C, sigs, fault, lk)
        check('(c) fault %s: %s reads %s' % (fault, rid, verdict), r.get(rid) == verdict and o['status'] != 'PASS', (r.get(rid), r))
    n = len(FAILS)
    print('selftest_source_pays_scene [%s]: %s (%d failed)' % (where, 'FAIL' if FAILS else 'ok', n))
    sys.exit(1 if FAILS else 0)


if __name__ == '__main__':
    main()
