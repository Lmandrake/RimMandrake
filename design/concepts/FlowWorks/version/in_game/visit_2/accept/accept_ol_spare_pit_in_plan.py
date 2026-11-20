#!/usr/bin/env python3
"""Acceptance test of RIMMANDRAKE_DIG_OL_SPARE_PIT_ONLY_IN_OLD_SAVE (FlowWorks 0.1.0, visit 2).

OL_OWNER_LOOK_READS read OL_pour_never_no_room UNMEASURED in visit 2: "could not brim the spare pit: REFUSED: (143, 103)
is not dug". owner_look_regressions --acts pours on SPARE=(140,100), the spare dry pit of the 11-12 keeper save; a scene
big_pit_scene.py stages has no spare pit, so the row could never be measured on any freshly staged big pit.
The fix: big_pit_scene plans a dry spare pit inside the site and writes it to scene_plan.json; stage digs it; OL --acts
reads it from --plan, and says it cannot look when a plan has none (never a guess at another save's pit).
Cases, on a fake bridge that keeps the dug squares stage made and answers RM_GodLiquid as the C# does:
  (c1) the plan names a spare [x, z, side, depth] inside the site rect, at least the copies' own spacing off every copy;
  (c2) stage digs every spare square to the spare's depth and spawns nothing on it;
  (c3) OL --plan <that plan> --acts brims a square stage dug, and OL_pour_never_no_room reads PASS;
  (c4) OL --acts on a plan with no spare (the visit-2 plan): the row is UNMEASURED and names the missing spare, and no
       SetLevel goes to the old save's pit at 143,103;
  (c5) --acts x,z still pours at x,z (a save whose spare is known by hand).
Red at the filing commit 16d4894f4893 on c1-c4; c5 must stay green.
"""
import importlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
NS = ROOT / 'src/RimMandrake/FlowWorks/northstar'
OLD_PLAN = ROOT / 'design/concepts/FlowWorks/version/in_game/visit_2/evidence/bigpit/scene_plan.json'
sys.path.insert(0, str(NS))
FAILS = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else str(why)[:400]))
    if not ok:
        FAILS.append(label)


def world_cls():
    import selftest_big_pit_scene as T

    class World(T.FakeBridge):
        """The selftest's plan bridge plus the squares stage digs and RM_GodLiquid's replies (Debug/RM_GodLiquid.cs)."""
        def __init__(self):
            super().__init__([])
            self.dug, self.spawned, self.levels = {}, set(), []

        def call(self, tool, **kw):
            if tool == 'jawa/flowworks_excavation_drive':
                self.dug[(kw['x'], kw['z'])] = kw.get('deepenLevels')
                return {'success': True}
            if tool == 'jawa/spawn_batch':          # ops "def:x,z,n" (big_pit_scene.spawn_stuffed)
                for op in str(kw.get('ops') or '').split(';'):
                    x, z = (int(v) for v in op.split(':', 1)[1].split(',')[:2])
                    self.spawned.add((x, z))
                return {'success': True, 'thingsPlaced': 1}
            if tool == 'jawa/spawn_pawn':
                self.spawned.add((kw['x'], kw['z']))
                return {'success': True}
            if tool == 'jawa/static_call':
                m, a = kw.get('method'), str(kw.get('args'))
                if m == 'ProofResetRect':
                    return {'result': 'RESET cells=1'}
                if kw.get('type', '').endswith('RM_GodLiquid'):
                    x, z = (int(v) for v in a.split('|')[0].split(','))
                    if m == 'SetLevel':
                        self.levels.append((x, z))
                        if (x, z) not in self.dug:
                            return {'result': 'REFUSED: (%d, %d) is not dug; a level is set on a pit' % (x, z)}
                        return {'result': 'OK set (%d, %d) to 4 m of RM_Fluid_Water over 36 squares' % (x, z)}
                    if m == 'PourOverflow':
                        return {'result': 'OK poured 1000 L at (%d, %d): 0 L into the pit, 1000 L overflowed' % (x, z)}
                    return {'result': 'OK drained'}
                if m == 'ProofSubmerge':
                    return {'result': 'REFUSED: nothing drawn under liquid'}
            return super().call(tool, **kw)
    return World


def staged():
    """plan then stage on one fake world -> (plan, world)."""
    import big_pit_scene as S
    S = importlib.reload(S)
    out = tempfile.mkdtemp(prefix='accept_ol_spare_')
    S.OUT, S.STEP = out, 'plan'
    w = world_cls()()
    w.origin = S.DEFAULT_ORIGIN
    S.B = w
    S.ROWS[:] = []
    S.do_plan(None)
    plan = json.load(open(Path(out) / 'scene_plan.json'))
    S.STEP = 'stage'
    S.sky_gate = lambda *a, **k: None   # validation_core's open-sky gate is live-only (roof and rock reads)
    S.labels = lambda plan: None         # the series labels (modcheck.reviewmap) are not under test
    try:
        S.stage(plan)
    except SystemExit as ex:
        print('      stage exited %s: %s' % (ex.code, S.ROWS[-1:]))
    return plan, w, S


def ol(world, plan_path, *acts):
    import owner_look_regressions as O
    O = importlib.reload(O)
    O.B = world
    out = tempfile.mkdtemp(prefix='accept_ol_spare_ol_')
    O.main(['owner_look_regressions.py', out, '--plan', str(plan_path)] + list(acts))
    rows = json.load(open(Path(out) / 'owner_look_regressions.json'))
    return [r for r in rows if r['row'] == 'OL_pour_never_no_room']


def main():
    plan, w, S = staged()
    sp = plan.get('spare')
    sx, sz, sw, sh = plan['site']
    gap = None
    if sp:
        x0, z0, side, _d = sp
        gap = min(max(cx - (x0 + side), x0 - (cx + S.PW), cz - (z0 + side), z0 - (cz + S.PW)) for _k, cx, cz, _f, _fl in plan['copies'])
    # the copies' own spacing, read from COPY_ROWS (BP0 at dx 2 ends at 18, BP1 starts at 21: 3 free columns)
    spacing = min(b[1] - (a[1] + S.PW) for a, b in zip(S.COPY_ROWS, S.COPY_ROWS[1:]) if a[2] == b[2])
    check('(c1) the plan names a spare inside the site, >= %d cells off every copy: %s gap %s' % (spacing, sp, gap),
          sp and len(sp) == 4 and sx <= sp[0] and sp[0] + sp[2] <= sx + sw and sz <= sp[1] and sp[1] + sp[2] <= sz + sh
          and gap is not None and gap >= spacing, plan.get('spare'))
    # the spare is an offset from the origin: sweep every origin choose_origin can return on a 250 map (its whole grid)
    bad, n = [], 0
    for o in [S.DEFAULT_ORIGIN] + [(x, z) for z in range(8, 250 - S.SITE_H - 12, 8) for x in range(8, 250 - S.SITE_W - 8, 8)]:
        if getattr(S, 'spare_for', None) is None:
            break
        n += 1
        x0, z0, side, _d = S.spare_for(o)
        ax, az, aw, ah = S.site_rect(o)
        g = min(max(cx - (x0 + side), x0 - (cx + S.PW), cz - (z0 + side), z0 - (cz + S.PW)) for _k, cx, cz, _f, _fl in S.copies_for(o))
        if not (ax <= x0 and x0 + side <= ax + aw and az <= z0 and z0 + side <= az + ah and g >= spacing):
            bad.append((o, g))
    check('(c1b) over all %d origins the spare stays inside the site, >= %d off every copy (%d bad)' % (n, spacing, len(bad)),
          n and not bad, bad[:4])
    if sp:
        cells = {(sp[0] + i, sp[1] + j) for i in range(sp[2]) for j in range(sp[2])}
        undug = [c for c in cells if w.dug.get(c) != sp[3]]
        hit = [s for s in w.spawned if isinstance(s, tuple) and s in cells]
        check('(c2) stage digs all %d spare squares to %s notches and spawns nothing there (%d undug, %d spawned)'
              % (len(cells), sp[3], len(undug), len(hit)), cells and not undug and not hit, (undug[:4], hit[:4]))
    else:
        check('(c2) stage digs the spare', False, 'no spare in the plan')
    pp = Path(tempfile.mkdtemp(prefix='accept_ol_spare_plan_')) / 'scene_plan.json'
    pp.write_text(json.dumps(plan))
    w.levels[:] = []
    r = ol(w, pp, '--acts')
    check('(c3) --acts on the staged plan brims a dug square and reads PASS: %s at %s' % (r[:1], w.levels),
          r and r[0]['verdict'] == 'PASS' and w.levels and all(c in w.dug for c in w.levels), r)
    w.levels[:] = []
    r = ol(w, OLD_PLAN, '--acts')
    check('(c4) a plan with no spare: UNMEASURED naming it, no SetLevel at the old save\'s 143,103: %s %s' % (r[:1], w.levels),
          r and r[0]['verdict'] == 'UNMEASURED' and 'spare' in r[0]['got'] and 'plan' in r[0]['got']
          and (143, 103) not in w.levels, r)
    w.levels[:] = []
    x, z = sorted(w.dug)[0]
    r = ol(w, OLD_PLAN, '--acts', '%d,%d' % (x - 3, z - 3))
    check('(c5) --acts x,z pours at x,z: %s' % w.levels, w.levels and w.levels[0] == (x, z), (r, w.levels))
    print('accept_ol_spare_pit_in_plan: %s' % ('FAIL %s' % FAILS if FAILS else 'ok'))
    sys.exit(1 if FAILS else 0)


if __name__ == '__main__':
    main()
