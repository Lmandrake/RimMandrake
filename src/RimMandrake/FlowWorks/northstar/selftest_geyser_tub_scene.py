#!/usr/bin/env python3
"""Offline half of sc_geyser_tub (RIMMANDRAKE_POINT_FLOWWORKS_GEYSER_CHECK_AT_VISIT_ONE_RUNNER): scene_geyser_tub against a
fake map that answers each read the way the mod does, as measured live on visit 2 (geyser_tub_live.py PASS 4 of 4,
design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/geyser_tub_live.json):
  - RM_Patch_MouseoverDepth.ProofPitLabel says "line=Pit, ... Water N m" on a dug square and adds " · Hot tub" only on an
    open pool's heated squares (RM_GeyserPit.TubReadoutAt): the vent dug under, water over the seat deeper than the 0.4 m
    mound (RM_GeyserTubMath.Covered), the square joined to the vent by water and nearer than the 2.5 reach
    (PoolRegion, InReach);
  - an ordered RM_SoakInGeyserPool on a heated square gives RM_HotPoolSoak while in and RM_HotPoolAfterglow after;
  - jawa/inspect_string on the vent names the steam geyser and no "Hot tub", and no need is ever named HotSpring (the
    draft's two reads, which visit 2 read FAIL on a build geyser_tub_live.py read PASS on).
Situations varied: which geyser the map lists first (one too near the east edge for the pit and its cold control is
skipped), dry vs filled pit, a wet pit off the pool, the soak order taken or refused, and four planted mod faults. Not
varied, because the C# selftests decide them (PitLook1114Checks, RM_GeyserTubMath): bath-less liquids, a capped vent,
the reach slider, the feature switched off. Planted faults, each must turn its row FAIL (never PASS): NO_TUB_WORD,
WORD_ON_DRY_PIT, HEAT_LEAKS_BESIDE, NO_AFTERGLOW. A refused order must read UNMEASURED. Red on the draft at 8c72e112f1
(its reads find no "Hot tub" and no HotSpring need on a healthy map), green on the fix. The fake proves the scene's
logic, never the game; the live half is
`python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_geyser_tub --out <json>`.
    python3 selftest_geyser_tub_scene.py [path/to/concept_scenes.py]
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

LABEL, POOL = 'RimMandrake.FlowWorks.RM_Patch_MouseoverDepth', 'RimMandrake.FlowWorks.RM_GeyserPoolProof'
SUBMERGE, FLUIDID = 'RimMandrake.FlowWorks.RM_SubmergeDraw', 'RimMandrake.FlowWorks.RM_FluidIdentityProof'
MOUND_M, REACH, NOTCH_M = 0.4, 2.5, 0.5        # RM_GeyserTubMath.GeyserMetres, DefaultReach; RM_UnderLiquid notch
SOAK_TICKS = 1500                              # the fake soak's length: longer than the 600-tick mid read, shorter than 3300


class Fake:
    def __init__(self, fault=None, geysers=((192, 184),), refuse=False):
        self.fault, self.refuse = fault, refuse
        self.g = {'t': 0, 'geysers': {'SteamGeyser%d' % i: xz for i, xz in enumerate(geysers)}, 'depth': {}, 'water': {},
                  'pawns': {}, 'soak': None}
        self.saves, self.contract = {}, []

    def save(self, k):
        self.saves[k] = deepcopy(self.g)

    def load(self, k):
        self.g = deepcopy(self.saves[k])

    def bad(self, why):
        self.contract.append(why)
        return {'success': False, 'message': why}

    # ---- the pool, as RM_GeyserPit reads it
    def vent(self, gid):
        x, z = self.g['geysers'][gid]
        return [(x + i, z + j) for i in (0, 1) for j in (0, 1)]

    def open_pool(self, gid):
        v = self.vent(gid)
        seat = min(self.g['depth'].get(c, 0) for c in v)
        level = min(self.g['water'].get(c, 0.0) for c in v)
        return seat > 0 and level > MOUND_M

    def heated(self, gid):
        if not self.open_pool(gid):
            return set()
        x, z = self.g['geysers'][gid]
        wet = {c for c, m in self.g['water'].items() if m > 0 and self.g['depth'].get(c, 0) > 0}
        if self.fault == 'HEAT_LEAKS_BESIDE':
            return {c for c in wet if abs(c[0] - x) <= 9 and abs(c[1] - z) <= 9}
        seen, todo = set(), [c for c in self.vent(gid) if c in wet]
        while todo:
            c = todo.pop()
            if c in seen:
                continue
            seen.add(c)
            todo += [(c[0] + dx, c[1] + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (c[0] + dx, c[1] + dz) in wet]
        return {c for c in seen if (c[0] + 0.5 - (x + 1)) ** 2 + (c[1] + 0.5 - (z + 1)) ** 2 < REACH ** 2}

    def label(self, c):
        d = self.g['depth'].get(c, 0)
        if not d:
            return 'line=Ground, 0.0 m deep'
        w = min(self.g['water'].get(c, 0.0), d * NOTCH_M)
        head = 'line=Pit, %.1f m water in %.1f m (walk speed 30%%)' % (w, d * NOTCH_M) if w else \
            'line=Pit, %.1f m deep (walk speed 100%%)' % (d * NOTCH_M)
        t = '%s — Hole %d m · Water %.2f m (%s L)' % (head, d * NOTCH_M, w, format(int(w * 2000), ','))
        tub = any(c in self.heated(g) or (c in self.vent(g) and self.open_pool(g)) for g in self.g['geysers'])
        if self.fault == 'WORD_ON_DRY_PIT':
            tub = tub or (not w and any(c in self.vent(g) or abs(c[0] - self.g['geysers'][g][0]) <= 2 for g in self.g['geysers']))
        if tub and self.fault != 'NO_TUB_WORD':
            t += ' · Hot tub'
        return t

    # ---- the bridge
    def ticks(self, n):
        self.g['t'] += n

    def probe_of(self, *a, **kw):
        return self.bad('probe_of unmodelled here')

    def call(self, tool, **kw):
        g = self.g
        if tool == 'jawa/list_things':
            if kw.get('defName') != 'SteamGeyser':
                return self.bad('list_things of %s' % kw.get('defName'))
            things = [{'id': i, 'def': 'SteamGeyser', 'x': x, 'z': z, 'spawned': True} for i, (x, z) in g['geysers'].items()]
            return {'success': True, 'things': things[:int(kw.get('limit') or 100)]}
        if tool == 'jawa/flowworks_excavation_drive':
            c = (kw['x'], kw['z'])
            g['depth'][c] = min(16, g['depth'].get(c, 0) + int(kw.get('deepenLevels') or 0))
            if float(kw.get('setBodyWaterM', -1)) >= 0:
                g['water'][c] = float(kw['setBodyWaterM'])
            return {'success': True, 'cell': {'x': c[0], 'z': c[1]}, 'depth': g['depth'][c]}
        if tool == 'jawa/static_call':
            return {'success': True, 'result': self.static(kw['type'], kw['method'], kw.get('args', ''))}
        if tool == 'jawa/inspect_string':
            x, z = (int(v) for v in kw['rect'].split(',')[:2])
            hit = [i for i in g['geysers'] if (x, z) in self.vent(i)]
            return {'success': True, 'matched': len(hit), 'things': [{'id': i, 'defName': 'SteamGeyser', 'label': 'steam geyser'}
                                                                    for i in hit]}
        if tool == 'jawa/spawn_pawn':
            pid = 'Human%d' % (100 + len(g['pawns']))
            g['pawns'][pid] = (kw['x'], kw['z'])
            return {'success': True, 'pawns': [{'id': pid}]}
        if tool == 'jawa/ordered_job':
            gid, b = kw.get('targetAId'), (kw.get('targetBX'), kw.get('targetBZ'))
            if kw.get('jobDef') != 'RM_SoakInGeyserPool' or kw.get('pawnId') not in g['pawns']:
                return self.bad('ordered_job %s' % kw)
            if self.refuse or gid not in g['geysers'] or b not in self.heated(gid):
                return {'success': True, 'accepted': False, 'note': 'no soak square'}
            g['soak'] = (kw['pawnId'], gid, g['t'])
            return {'success': True, 'accepted': True}
        if tool == 'jawa/pawn_get':
            hs, s = [], g['soak']
            if s and s[0] == kw.get('pawn'):
                age = g['t'] - s[2]
                if age < SOAK_TICKS:
                    hs.append({'def': 'RM_HotPoolSoak', 'severity': 1.0})
                elif self.fault != 'NO_AFTERGLOW':
                    hs.append({'def': 'RM_HotPoolAfterglow', 'severity': 0.5})
            return {'success': True, 'pawns': [{'id': kw.get('pawn'), 'hediffs': hs}]}
        if tool == 'jawa/pawn_need':
            return {'success': True, 'needs': [{'need': 'Mood', 'level': 0.5}, {'need': 'Food', 'level': 0.4}]}
        return self.bad('unmodelled tool %s' % tool)

    def static(self, typ, method, arg):
        g = self.g
        if (typ, method) == (LABEL, 'ProofPitLabel'):
            x, z = (int(v) for v in arg.split(','))
            return self.label((x, z))
        if (typ, method) == (SUBMERGE, 'ProofFillRect'):
            x0, z0, w, h, m, fluid = arg.split(',')
            if fluid != 'RM_Fluid_Water':
                return 'REFUSED: fake models water only'
            n = 0
            for i in range(int(w)):
                for j in range(int(h)):
                    c = (int(x0) + i, int(z0) + j)
                    if g['depth'].get(c, 0):
                        g['water'][c] = float(m)
                        n += 1
            return 'FILLED %d cells %s m' % (n, m)
        if (typ, method) == (FLUIDID, 'ProofFillWithFluid'):
            x, z, m, fluid = arg.split(',')
            g['water'][(int(x), int(z))] = float(m)
            return 'FILLED (%s, 0, %s) fluid=%s' % (x, z, fluid)
        if (typ, method) == (POOL, 'Read'):
            if arg not in g['geysers']:
                return 'no geyser %s' % arg
            s = g['soak']
            soakers = 1 if s and s[1] == arg and g['t'] - s[2] < SOAK_TICKS else 0
            return 'spawned=True thingId=%s heated=%d pool=%s soakers=%d' % (arg, len(self.heated(arg)), self.open_pool(arg), soakers)
        self.contract.append('unmodelled static %s.%s' % (typ, method))
        return 'REFUSED: unmodelled'


ROWS = ('TUB_dry_pit_not_a_tub', 'TUB_reads_hot_tub', 'TUB_beside_stays_cold', 'TUB_pawn_soaks_bonus')
PLANTS = {'NO_TUB_WORD': 'TUB_reads_hot_tub', 'WORD_ON_DRY_PIT': 'TUB_dry_pit_not_a_tub',
          'HEAT_LEAKS_BESIDE': 'TUB_beside_stays_cold', 'NO_AFTERGLOW': 'TUB_pawn_soaks_bonus'}
FAILS = []


def run(**kw):
    f = Fake(**kw)
    res = {'calls': []}
    out = C.scene_geyser_tub(f, lambda: f.save('begin'), lambda: f.load('begin'), res)
    f.res = res
    return {r['id']: r['status'] for r in out['rows']}, {r['id']: r['detail'] for r in out['rows']}, f


def check(ok, what):
    print('%s  %s' % ('ok  ' if ok else 'FAIL', what))
    if not ok:
        FAILS.append(what)


def main():
    rows, detail, f = run()
    check(not f.contract, 'every staging call keeps its tool contract %s' % f.contract[:3])
    check(set(rows) == set(ROWS) and all(v == 'PASS' for v in rows.values()),
          'healthy pool: every row PASS, %d of %d read (%s)' % (sum(v == 'PASS' for v in rows.values()), len(ROWS), rows))
    check(not f.g['depth'] and not f.g['soak'], 'the scene reloads its begin snapshot: nothing dug or soaking after it')
    for plant, rid in sorted(PLANTS.items()):
        got, d, _ = run(fault=plant)
        check(got.get(rid) == 'FAIL', 'planted %s turns %s FAIL (got %s: %s)' % (plant, rid, got.get(rid), str(d.get(rid))[:90]))
    got, _, _ = run(refuse=True)
    check(got.get('TUB_pawn_soaks_bonus') == 'UNMEASURED', 'a refused soak order reads UNMEASURED (got %s)' % got.get('TUB_pawn_soaks_bonus'))
    got, _, f2 = run(geysers=((245, 120), (64, 98)))
    aim = [c['args'].get('targetAId') for c in f2.res['calls'] if c['tool'] == 'jawa/ordered_job']
    check(all(v == 'PASS' for v in got.values()) and aim == ['SteamGeyser1'],
          'a geyser too near the east edge is skipped; the next one is read (%s, soak on %s)' % (got, aim))
    got, _, _ = run(geysers=((245, 120),))
    check(list(got.values()) == ['UNMEASURED'], 'no geyser with room for its pit: one UNMEASURED staging row (%s)' % got)
    got, _, _ = run(geysers=())
    check(list(got.values()) == ['UNMEASURED'], 'no geyser at all: one UNMEASURED staging row (%s)' % got)
    print('selftest_geyser_tub_scene: %s' % ('ok' if not FAILS else 'FAIL (%d)' % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
