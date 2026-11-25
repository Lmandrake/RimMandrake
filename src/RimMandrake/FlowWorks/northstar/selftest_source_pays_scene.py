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
      once, the endless body drops) turns its row FAIL. Never PASS;
  (d) SRC_flow_stops_when_empty over a sweep of film regimes (film_regimes: film depth x how the sink draws it, in whole
      dL) reads the fake's own truth when the sink comes off: PASS only at 0 dL with the draw stopped, FAIL on a stuck,
      stalled or creeping film, UNMEASURED only when the film still drains at SRC_FILM_PULSES
      (RIMMANDRAKE_REPIN_SOURCE_PAYS_FILM_IS_NOT_A_LEAK; red on the row at 59a01946ac).
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
        self.film = None          # (wet line in notches, mode, rate): the sink draws the film under the wet line slowly
        self.film_end = None      # the truth when the unlimited sink comes off: (film left, last pulse's draw)

    # ---- the engine
    def comps(self):
        key = tuple(sorted(self.dug.items()))         # the components change only with a dig: cached per dug map
        if getattr(self, '_comps_key', None) != key:
            self._comps_key, self._comps = key, list(self._flood())
        return iter(self._comps)

    def _flood(self):
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
        depths = {}
        for q in comp:                                # squares grouped by depth: the bisection reads a handful of groups
            depths[self.dug[q]] = depths.get(self.dug[q], 0) + 1
        lo, hi = -max(depths), 0.0
        if vol >= sum(d * n for d, n in depths.items()):
            return 0.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if sum(n * max(0.0, mid + d) for d, n in depths.items()) > vol:
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
            if self.film:
                self.spread(comp, sum(self.water.get(q, 0.0) for q in comp))
                continue
            h = self.surface(comp, sum(self.water.get(q, 0.0) for q in comp))
            for q in comp:
                self.water[q] = frozen.get(q, max(0.0, h + self.dug[q]))

    def one_pulse(self):
        if self.weather == 'Rain' and self.fault == 'stepped_rain':
            # live 2026-11-25 (bundle_shrink_20261125, sc_source_refills): the emptied pond read 0 L for 4,500 ticks of rain,
            # then 1,250 L, and 1,250 L again 1,000 ticks later: rain lands in lumps more than 1,000 ticks apart
            self.rain_pulses = getattr(self, 'rain_pulses', 0) + 1
            if self.rain_pulses >= 18 and self.rain_pulses % 10 == 8:
                for q in self.dug:
                    self.water[q] = min(self.dug[q], self.water.get(q, 0.0) + 1.25)
        elif self.weather == 'Rain' and self.fault not in ('never_refills', 'no_rain'):
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
                if self.film and s['rate'] < 0:
                    take = self.film_take(comp, q, vol, above, s)
                s['last'] = take
                if take <= 0:
                    continue
                if self.film:
                    self.spread(comp, vol - take)
                else:
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

    def spread(self, comp, vol):
        """Section (d): vol over comp as whole dL a square (RM_Volume.UnitsPerLitre: the live engine stores dL), one surface,
        the remainder handed out a dL at a time to the squares nearest the next dL; the comp's total is kept exactly."""
        total = int(round(vol * U))
        h = self.surface(comp, total / U)
        want = {q: max(0.0, h + self.dug[q]) * U for q in comp}
        got = {q: int(w) for q, w in want.items()}
        rest = total - sum(got.values())
        for q in sorted(comp, key=lambda c: (got[c] - want[c], c))[:max(0, rest)]:
            got[q] += 1
        for q in comp:
            self.water[q] = got[q] / U

    def film_take(self, comp, q, vol, above, s):
        """Section (d): fast down to the wet line, then the film at its mode's rate, in whole fake dL (1 / U notch)."""
        wet, mode, rate = self.film
        reserve = sum(max(0.0, -self.dug[q] + wet + self.dug[p]) for p in comp)
        if vol > reserve + 1e-9:
            return min(100.0, vol - reserve)
        left = max(0.0, above)
        if mode == 'phantom':                      # the pond empties, yet the sink's total keeps creeping
            s['drained'] += 1.0 / U
            return min(1.0, left)
        if mode == 'stall' and left < 0.5 * s.setdefault('film0', left):
            return 0.0                             # the film stops moving half way: water left, no draw
        want = rate * left if mode == 'prop' else rate
        return min(left, max(1.0 / U, round(want * U) / U)) if want > 0 else 0.0

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
            if self.sinks[c]['rate'] < 0:
                reach = [q for q in ((c[0] + 1, c[1]), (c[0], c[1])) if q in self.dug]
                comp = next(cm for cm in self.comps() if reach[0] in cm)
                vol = sum(self.water.get(p, 0.0) for p in comp)
                left = vol - sum(max(0.0, -self.dug[reach[0]] + self.dug[p]) for p in comp)
                self.film_end = (max(0.0, left), self.sinks[c].get('last', 0.0))
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


class _FakeSites(types.ModuleType):
    """test_site_saves for the fake: the scene loads the river site for its lake row when the calm map has no limitless
    body (visit 4). river=True loads verified and turns the fake's map into one with a limitless body; else the load is
    not verified (the river site is built on another tier), so the row must read UNMEASURED."""
    def __init__(self):
        super().__init__('test_site_saves')

    @staticmethod
    def load_site(call, site, **kw):
        F = call.__self__
        F.__dict__.setdefault('site_loads', []).append(site)   # film_sweep builds its Fake without run()
        if site == 'river' and getattr(F, 'river', False):
            F.lake = True
            return {'site': site, 'save': 'fake', 'verified': True, 'problems': []}
        return {'site': site, 'save': 'fake', 'verified': False, 'problems': ['fake: the river site is not on this list']}


sys.modules['test_site_saves'] = _FakeSites()


def run(C, sigs, fault=None, lake=False, river=False):
    F = Fake(fault, lake, sigs)
    F.river, F.site_loads = river, []
    out = C.scene_source_pays(F, lambda: None, lambda: None, {'calls': []})
    return {r['id']: r['status'] for r in out['rows']}, out, F


def film_regimes(C):
    """Section (d)'s range: what the game can vary for SRC_flow_stops_when_empty once the pond is at its wet line.
    Varied: the film's depth (a thin film, half the wet line, the wet line itself: the scene's wet line is 0.05 notch) and how
    the sink draws it: a constant rate from 0 to 1 notch a pulse, a rate that falls with the film left (live: about 0.0035 of
    it a pulse, visit_2 evidence/exp/source_pays_long.json), a film that stops half way, and a total that creeps after the
    pond is empty. Every draw is whole fake dL, as the live engine's is. Left out: a film thicker than the wet line (the
    fast phase must reach the wet line in 500 pulses, unchanged by this fix), rain during the draw (the scene locks Clear),
    and more than one sink (the scene places one)."""
    out = []
    for wet in (0.005, 0.025, 0.05):
        for r in (0.0, 1e-4, 3e-4, 1e-3, 2.5e-3, 2.75e-3, 3e-3, 0.01, 0.03, 0.1, 1.0):   # 2.5e-3..3e-3: the bound's edge
            out.append((wet, 'const', r))
        for k in (5e-4, 1e-3, 2e-3, 3.5e-3, 1e-2, 5e-2):
            out.append((wet, 'prop', k))
        out += [(wet, 'stall', 0.03), (wet, 'phantom', 0.0)]
    return out


def film_sweep(C, sigs):
    """(d) The row against the fake's own truth at the moment the sink comes off: PASS only when the film is gone and the
    sink drew nothing in its last pulse; FAIL when water is left and the draw stopped, or the total crept with no water;
    UNMEASURED only when the film was still draining at the bound."""
    cases = film_regimes(C)
    bad, worst, tally = [], (0, None), {}
    for wet, mode, rate in cases:
        F = Fake(None, False, sigs)
        F.film = (wet, mode, rate)
        out = C.scene_source_pays(F, lambda: None, lambda: None, {'calls': []})
        r = next(x for x in out['rows'] if x['id'] == 'SRC_flow_stops_when_empty')
        left, last = F.film_end
        m = re.search(r"'film pulses', (\d+)", r['detail'])
        film = int(m.group(1)) if m else None
        truth = 'FAIL' if mode == 'phantom' else ('PASS' if left < 1e-9 and last < 1e-9 else
                                                  'UNMEASURED' if last > 1e-9 else 'FAIL')
        tally[r['status']] = tally.get(r['status'], 0) + 1
        if r['status'] != truth:
            bad.append((wet, mode, rate, r['status'], truth, left, film))
        if r['status'] == 'PASS' and isinstance(film, int) and film > worst[0]:
            worst = (film, (wet, mode, rate))
    seen = sorted({(b[1], b[3], b[4]) for b in bad})
    print('      film sweep: %d cases %s; worst PASS spent %s of %s film pulses at %s' % (
        len(cases), sorted(tally.items()), worst[0], getattr(C, 'SRC_FILM_PULSES', None), worst[1]))
    check('(d) the film sweep sees every verdict (a sweep of one verdict is a blind fake)',
          {'PASS', 'FAIL', 'UNMEASURED'} <= set(tally), tally)
    check('(d) the film sweep reads every case as the fake\'s truth (%d cases)' % len(cases), not bad, (seen, bad[:6]))


def split_scenes(C, sigs):
    """(e) sc_source_pays's split scenes (RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES): each asks only its
    rows, reads them PASS on the healthy fake, and each planted fault turns its row red, never PASS; _src_brim's arithmetic."""
    if not hasattr(C, 'scene_source_draws'):
        check('(e) the split scenes exist', False, 'no scene_source_draws in this revision')
        return

    def go(name, fault=None):
        F = Fake(fault, False, sigs)
        out = getattr(C, name)(F, lambda: None, lambda: None, {'calls': []})
        return {r['id']: r['status'] for r in out['rows']}, out, F
    draws = ('SRC_pond_drops', 'SRC_shore_recedes', 'SRC_control_tap_zero')
    r, o, F = go('scene_source_draws')
    check('(e) sc_source_draws asks exactly its three rows, all PASS on the healthy fake',
          r == {k: 'PASS' for k in draws} and o['status'] == 'PASS', r)
    check('(e) sc_source_draws makes only declared bridge calls and leaves no sink or weather lock', not F.bad and not F.sinks
          and F.weather == 'Clear', (F.bad, F.sinks, F.weather))
    for fault, rid, want in (('pays_nothing', 'SRC_pond_drops', 'FAIL'), ('shore_frozen', 'SRC_shore_recedes', 'FAIL'),
                             ('zero_tap_drains', 'SRC_control_tap_zero', 'FAIL'),
                             ('refused_readout', 'SRC_pond_drops', 'UNMEASURED'), ('zero_rect', 'SRC_shore_recedes', 'UNMEASURED'),
                             ('sink_refused', 'SRC_control_tap_zero', 'UNMEASURED')):
        r, o, _ = go('scene_source_draws', fault)
        check('(e) sc_source_draws, fault %s: %s reads %s' % (fault, rid, want), r.get(rid) == want and o['status'] != 'PASS', r)
    for fault, want in ((None, 'PASS'), ('stepped_rain', 'PASS'), ('never_refills', 'FAIL'), ('instant_refill', 'FAIL'),
                        ('no_rain', 'UNMEASURED'), ('refused_readout', 'UNMEASURED')):
        r, o, F = go('scene_source_refills', fault)
        check('(e) sc_source_refills, %s: SRC_refill_visible reads %s' % (fault or 'healthy', want),
              r == {'SRC_refill_visible': want} and (o['status'] == 'PASS') == (want == 'PASS') and F.weather == 'Clear', r)
    b = C._src_brim('OK Hole 2 m · Water 0.00 m (0 L)', 'OK Hole 2 m · Water 0.63 m (1,250 L)')
    check('(e) _src_brim: a 2 m hole read wet at 0.63 m (1,250 L) has its brim at 2 x 1250 / 0.63 L',
          b is not None and abs(b - 2 * 1250 / 0.63) < 1e-6, b)
    check('(e) _src_brim cannot say from an unreadable line or a dry one',
          C._src_brim('REFUSED', 'OK Hole 2 m · Water 0.63 m (1,250 L)') is None
          and C._src_brim('OK Hole 2 m', 'OK Hole 2 m · Water 0.00 m (0 L)') is None, None)


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
    check('(b) the calm endless row states its reason (the river site did not load verified)',
          'river site' in lake and 'did not load verified' in lake and F.site_loads == ['river'], (lake, F.site_loads))
    r3, o3, F3 = run(C, sigs, river=True)
    check('(b) on the calm map the lake row goes to the river site and reads PASS there',
          r3.get('SRC_lake_reads_endless') == 'PASS' and F3.site_loads == ['river'], (r3, F3.site_loads))
    r4, o4, F4 = run(C, sigs, 'lake_drops', river=True)
    check('(c) fault lake_drops on the river site: SRC_lake_reads_endless reads FAIL',
          r4.get('SRC_lake_reads_endless') == 'FAIL' and o4['status'] != 'PASS', r4)
    r5, o5, F5 = run(C, sigs, lake=True)
    check('(b) a map that already has a limitless body loads no other site', F5.site_loads == [], F5.site_loads)
    check('(b) the calm scene is not PASS while a row is UNMEASURED', out['status'] != 'PASS', out['status'])
    r2, o2, F2 = run(C, sigs, lake=True)
    check('(b) a fake map with a limitless body reads every row PASS', set(r2.values()) == {'PASS'} and o2['status'] == 'PASS', r2)
    check('(b) the sinks came off and the weather lock was released', not F.sinks and F.weather == 'Clear', (F.sinks, F.weather))

    for fault, lk, rid, verdict in CASES:
        r, o, _ = run(C, sigs, fault, lk)
        check('(c) fault %s: %s reads %s' % (fault, rid, verdict), r.get(rid) == verdict and o['status'] != 'PASS', (r.get(rid), r))
    film_sweep(C, sigs)
    split_scenes(C, sigs)
    n = len(FAILS)
    print('selftest_source_pays_scene [%s]: %s (%d failed)' % (where, 'FAIL' if FAILS else 'ok', n))
    sys.exit(1 if FAILS else 0)


if __name__ == '__main__':
    main()
