"""SUMP_GLASSWALK_SPEED_RATIO_1, offline half: is glasswalk's pathCost 3 right for the spec's "~80%, never full speed"?

The law (decompiled 1.6, D:\\ClaudeWork\\rimmandrake\\decomp\\rw16\\all\\Verse.AI\\Pawn_PathFollower.cs, CostToMoveIntoCell):
  cost = TicksPerMoveCardinal + PathGrid.CalculatedCostAt   (terrain pathCost; TileGranite has none, so 0)
  then x1 for LocomotionUrgency.Jog (an ordered Goto), x2 (min 50) Walk, round(x0.75) Sprint.
  The pawn pays 1 per tick and carries the overshoot into the next cell, so ticks/cell == cost on average.
So glass/granite speed = T / (T + 3) at Jog: 13/16 = 0.81 for a standard colonist (MoveSpeed 4.6 -> 60/4.6 = 13.04).

The 2026-10-10 reading of 0.65 (granite 9.8, glass 15 ticks/cell) is not this law at ANY T: the law gives T/(T+3) = 0.77 at
T = 9.8, and 0.65 would need pathCost 5.3. The instrument explains it: the scene's timer called scenes.scenelib.run(10),
which plays at speed 4 for at least 200 ms (~80 ticks at ~400 ticks/s), so each sample was ~80 ticks, not 10, against
walks of 120-200 ticks. The live re-measure (prove_glasswalk_speed.py) times with exact rimworld/step_game_ticks steps.

Run: python3 src/RimMandrake/TheSump/test_glasswalk_speed_model.py   (exit 0 = every check holds)
"""
import ast
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEFS = os.path.join(HERE, "Defs", "TerrainDefs", "RM_SumpWalkways.xml")
PROVE = os.path.join(HERE, "prove_glasswalk_speed.py")
SCENELIB = os.path.join(ROOT, "src", "RimMandrake", "Utils", "scenes", "scenelib.py")

BAND = (0.72, 0.90)          # the spec's "~80%" acceptance band (as the 2026-10-10 scene judged it)
STANDARD_T = 60.0 / 4.6      # vanilla Human MoveSpeed 4.6 -> 13.04 ticks per cardinal cell


def cost(T, path_cost, urgency="Jog"):
    """Pawn_PathFollower.CostToMoveIntoCell for a cardinal step onto a plain floor (no edifice, no terrain tag factor)."""
    n = min(T + path_cost, 450.0)
    if urgency == "Amble":
        n = max(n * 3, 60.0)
    elif urgency == "Walk":
        n = max(n * 2, 50.0)
    elif urgency == "Sprint":
        n = float(int(n * 0.75 + 0.5))   # Mathf.RoundToInt (banker's rounding differs only at exact .5; irrelevant here)
    return max(n, 1.0)


def ticks_per_cell(T, path_cost, cells=200, urgency="Jog"):
    """Simulate the follower's pay loop: pay 1 per tick, carry the overshoot (nextCellCostLeft) into the next cell."""
    left, ticks = 0.0, 0
    for _ in range(cells):
        c = cost(T, path_cost, urgency)
        left = max(c + min(left, 0.0), 1.0)
        while left > 0:
            left -= 1.0
            ticks += 1
    return ticks / cells


def glass_path_cost():
    """RM_Glasswalk's own <pathCost>, read from its own TerrainDef element (None if absent)."""
    for td in ET.parse(DEFS).getroot().iter("TerrainDef"):
        if (td.findtext("defName") or "").strip() == "RM_Glasswalk":
            v = td.findtext("pathCost")
            return int(v) if v is not None else None
    return None


def times_exactly(path):
    """True when walk_exact's timing loop steps through step(), step() calls the bridge's rimworld/step_game_ticks, and no
    function calls S.run (scenelib.run's 200 ms floor is ~80 ticks a sample)."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    funcs = {f.name: f for f in tree.body if isinstance(f, ast.FunctionDef)}

    def calls(node):
        return [n for n in ast.walk(node) if isinstance(n, ast.Call)]

    def is_tool_call(c, tool):
        return (isinstance(c.func, ast.Attribute) and c.func.attr == "call" and c.args
                and isinstance(c.args[0], ast.Constant) and c.args[0].value == tool)

    step_ok = "step" in funcs and any(is_tool_call(c, "rimworld/step_game_ticks") for c in calls(funcs["step"]))
    loop_ok = "walk_exact" in funcs and any(
        isinstance(w, ast.While) and any(isinstance(c.func, ast.Name) and c.func.id == "step" for c in calls(w))
        for w in ast.walk(funcs["walk_exact"]))
    no_run = not any(isinstance(c.func, ast.Attribute) and c.func.attr == "run" for c in calls(tree))
    return step_ok and loop_ok and no_run


def walk_exact_fake(m):
    """Drive the proof's own walk_exact against a fake bridge: a pawn at T=13 ticks/cell. True when a clean walk times
    12 cells at 13*12 (+-STEP) ticks, and a walk with one blind position reading (None, or a text error) returns None."""
    class Sc:
        x, z = 0, 0

    def run(blind_at):
        clock = {"t": 0, "start": None, "reads": 0}

        class FakeS:
            @staticmethod
            def need(r, label):
                return r

            @staticmethod
            def call(tool, **kw):
                if tool == "rimworld/step_game_ticks":
                    clock["t"] += kw["ticks"]
                    return {"ok": True}
                if tool == "jawa/ordered_job":
                    clock["start"] = clock["t"] if kw.get("targetAX", 0) > 5 else None
                    return {}
                if tool == "jawa/pawn_get":
                    clock["reads"] += 1
                    if clock["start"] is None:
                        return {"pawns": [{"position": {"x": 1, "z": 1}}]}
                    if blind_at is not None and clock["reads"] == blind_at[0]:
                        return blind_at[1]
                    return {"pawns": [{"position": {"x": 1 + (clock["t"] - clock["start"]) // 13, "z": 1}}]}
                return {}

        saved = m.S
        m.S = FakeS
        try:
            return m.walk_exact(Sc(), 1)
        finally:
            m.S = saved
    clean = run(None)
    blind_none = run((40, {"pawns": [{}]}))
    blind_text = run((40, "error: no such pawn"))
    return clean is not None and abs(clean - 13 * 12) <= m.STEP and blind_none is None and blind_text is None


def gates_on_standard_pawn(path):
    """Import the live proof and feed its pure judge() the probes a blind checker named; True when each goes the right way.
    Returns (ok, [(label, got_exit, want_exit, line)])."""
    import types
    # Compile the SOURCE (never a cached .pyc: a same-size edit in the same second would be served stale).
    m = types.ModuleType("prove_glasswalk_speed")
    m.__file__ = path
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), m.__dict__)
    std = [4.6] * 4
    cases = [
        ("standard pawn T=13.04, granite 13.04, glass 16.04", std, [13.04, 13.1], [16.0, 16.1], 0),
        ("checker probe: MoveSpeed 6.12 (T=9.8), granite 9.8, glass 12.8", [6.12] * 4, [9.8, 9.8], [12.8, 12.8], 1),
        ("fast pawn T=12.0 (MoveSpeed 5.0), law-perfect readings", [5.0] * 4, [12.0, 12.0], [15.0, 15.0], 1),
        ("slow pawn T=14.3 (MoveSpeed 4.2), law-perfect readings", [4.2] * 4, [14.3, 14.3], [17.3, 17.3], 1),
        ("one MoveSpeed reading off-band (6.12) among 4.6s", [4.6, 4.6, 4.6, 6.12], [13.04] * 2, [16.04] * 2, 1),
        ("a MoveSpeed reading missing", [4.6, None, 4.6, 4.6], [13.04] * 2, [16.04] * 2, 1),
        ("base mutant: granite 11.5 for T=13.04", std, [11.5, 11.5], [14.5, 14.5], 1),
        ("delta mutant: glass 18 (delta 5) for T=13.04", std, [13.04] * 2, [18.0, 18.0], 1),
        ("the 2026-10-10 ratio 0.65 at T=13.04 (glass 20)", std, [13.04] * 2, [20.06] * 2, 1),
        ("one granite sample only", std, [13.04], [16.04, 16.04], 1),
        ("one glass sample only", std, [13.04, 13.04], [16.04], 1),
        ("granite-only averaging: granite [10, 16.08], glass law", std, [10.0, 16.08], [16.04, 16.04], 1),
        ("glass-only averaging: granite law, glass [13, 19.08]", std, [13.04, 13.04], [13.0, 19.08], 1),
        ("MoveSpeed averaging mutant: [4.2, 5.0, 4.2, 5.0] (mean 4.6, every reading off-band)", [4.2, 5.0, 4.2, 5.0],
         [13.04] * 2, [16.04] * 2, 1),
        ("averaging mutant: granite [10, 16], glass [13, 19] (means law-perfect)", std, [10.0, 16.08], [13.0, 19.08], 1),
    ]
    rows = []
    for label, sp, g, sg, want in cases:
        got, line = m.judge(g, sg, sp)
        word_ok = ("PASS" in line) if want == 0 else ("PASS" not in line)
        rows.append((label, got, want, line, word_ok))
    unmeasured_probe = "UNMEASURED" in rows[1][3]
    ok = all(got == want and wok for _, got, want, _, wok in rows) and unmeasured_probe
    tree = ast.parse(open(path, encoding="utf-8").read())
    mainf = [f for f in tree.body if isinstance(f, ast.FunctionDef) and f.name == "main"]
    names = {c.func.id for f in mainf for c in ast.walk(f) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
    wired = {"judge", "pick_standard_pawn"} <= names
    walk_ok = walk_exact_fake(m)
    we = [f for f in tree.body if isinstance(f, ast.FunctionDef) and f.name == "walk_exact"]
    # walk_exact must give up (return None) on a missing position, never `continue` past it (a blind gap hides ticks).
    blind_ok = bool(we) and not any(isinstance(n, ast.Continue) for n in ast.walk(we[0]))
    return ok and wired and blind_ok and walk_ok, rows, wired and blind_ok and walk_ok


def main_fake(m, move_speed, granite_tpc, glass_tpc):
    """Drive the live proof's own main() end to end against a fake bridge: spawned colonist n reads MoveSpeed
    move_speed[n-1] (the last value repeats; a number means every spawn; a per-pawn LIST is that pawn's successive
    readings, the last repeating, so a pawn can drift after the picker read it); granite_tpc / glass_tpc may be a list,
    one ticks/cell per timed walk on that floor (the last repeating), so single walks can differ from their mean; on TileGranite it walks granite_tpc ticks/cell, on RM_Glasswalk glass_tpc. Returns (exit, stdout)."""
    import contextlib
    import io
    clock = {"t": 0, "start": None, "x0": 1, "floor": None, "dropped": False, "tpc": None}
    walks = {"TileGranite": -1, "RM_Glasswalk": -1}
    speeds = move_speed if isinstance(move_speed, list) else [move_speed]
    reads = {}

    def speed_of(pid):
        v = speeds[min(pid, len(speeds)) - 1]
        if not isinstance(v, list):
            return v
        k = reads[pid] = reads.get(pid, -1) + 1
        return v[min(k, len(v) - 1)]

    def pos_x():
        if clock["start"] is None:
            return clock["x0"]
        tpc = clock["tpc"]
        return clock["x0"] + int((clock["t"] - clock["start"]) // tpc)

    class FakeScene:
        x, z = 0, 0

        def __init__(self, *a, **k):
            self.n = 0

        def __enter__(self):
            return self

        def room(self, **k):
            pass

        def floor(self, terr, rect):
            clock["floor"] = terr

        def colonist(self, x, z):
            self.n += 1
            return self.n

        def kill(self, pid):
            pass

        def teardown(self):
            pass

    class FakeS:
        Scene = FakeScene

        @staticmethod
        def need(r, label):
            return r

        @staticmethod
        def biome_map(*a, **k):
            return 7

        @staticmethod
        def drop_map(*a, **k):
            clock["dropped"] = True

        @staticmethod
        @contextlib.contextmanager
        def setting(*a, **k):
            yield

        @staticmethod
        def call(tool, **kw):
            if tool == "rimworld/step_game_ticks":
                clock["t"] += kw["ticks"]
                return {"ok": True}
            if tool == "jawa/ordered_job":
                if kw.get("targetAX", 0) > 5:
                    clock["x0"], clock["start"] = pos_x(), clock["t"]
                    k = walks[clock["floor"]] = walks[clock["floor"]] + 1
                    v = granite_tpc if clock["floor"] == "TileGranite" else glass_tpc
                    clock["tpc"] = v[min(k, len(v) - 1)] if isinstance(v, list) else v
                else:
                    clock["x0"], clock["start"] = 1, None
                return {}
            if tool == "jawa/pawn_get":
                return {"pawns": [{"position": {"x": pos_x(), "z": 1}}]}
            if tool == "jawa/pawn_stats":
                return {"stats": [{"defName": "MoveSpeed", "value": speed_of(kw["pawn"])}]}
            return {}

    saved = m.S
    m.S = FakeS
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            code = m.main()
    finally:
        m.S = saved
    return code, out.getvalue(), clock["dropped"]


def main_end_to_end(path):
    """The blind checker's probe, through main() itself: a MoveSpeed 6.12 pawn (T=9.8) showing granite 9.8 / glass 12.8
    must exit 1 UNMEASURED; a 4.6 pawn on law readings (13.04 / 16.04) exits 0 PASS; the same pawn at the 2026-10-10
    ratio (glass 20.06) exits 1; when the first spawn is off-band the picker takes the next in-band one and PASSes;
    a pawn that drifts out of band after the pick is UNMEASURED; a delta-5 world whose ratio (0.72) looks plausible FAILs;
    walks that are wrong one by one but law-perfect on average FAIL (main() must not average them away). Returns (ok, [(label, code, want, last RESULT line)])."""
    import types
    m = types.ModuleType("prove_glasswalk_speed")
    m.__file__ = path
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), m.__dict__)
    cases = [("checker probe through main(): MoveSpeed 6.12, granite 9.8, glass 12.8", 6.12, 9.8, 12.8, 1, "UNMEASURED"),
             ("standard pawn through main(): MoveSpeed 4.6, granite 13.04, glass 16.04", 4.6, 60 / 4.6, 60 / 4.6 + 3, 0, "PASS"),
             ("picker skips an off-band first spawn: MoveSpeed [6.12, 4.6], law readings", [6.12, 4.6], 60 / 4.6,
              60 / 4.6 + 3, 0, "PASS"),
             ("drift after the pick: MoveSpeed read 4.6 then 4.36 (T=13.76), law readings at 13.76",
              [[4.6, 4.6, 4.36]], 13.76, 16.76, 1, "UNMEASURED"),
             ("delta 5 inside the ratio band: MoveSpeed 4.6, granite 13.04, glass 18 (ratio 0.72)", 4.6, 60 / 4.6, 18.0,
              1, "FAIL"),
             ("averaging through main(): granite walks [10, 16.08] (mean law), glass law", 4.6, [10.0, 16.08],
              60 / 4.6 + 3, 1, "FAIL"),
             ("averaging through main(): granite law, glass walks [19.08, 13] (mean law)", 4.6, 60 / 4.6, [19.08, 13.0],
              1, "FAIL"),
             ("0.65 world through main(): MoveSpeed 4.6, granite 13.04, glass 20.06", 4.6, 60 / 4.6, 20.06, 1, "FAIL")]
    rows, ok = [], True
    for label, ms, g, s, want, word in cases:
        code, text, dropped = main_fake(m, ms, g, s)
        res = [ln for ln in text.splitlines() if ln.startswith("RESULT ")]
        line = res[-1] if res else "(no RESULT line)"
        good = code == want and len(res) == 1 and (" %s " % word) in line + " " and dropped
        if want != 0:
            good = good and "/A1 PASS" not in text
        ok = ok and good
        rows.append((label, code, want, line))
    return ok, rows


def main():
    fails = []

    def check(ok, msg):
        print(("PASS " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    pc = glass_path_cost()
    check(pc == 3, "RM_Glasswalk pathCost read from the def = %r (expected 3)" % pc)
    pc = pc or 3

    # The pay loop reproduces the closed form (ticks/cell == cost) across the whole pawn range.
    worst = max(abs(ticks_per_cell(T / 10.0, pc) - (T / 10.0 + pc)) for T in range(50, 401, 7))
    check(worst < 0.05, "simulated pay loop matches T+pathCost within 0.05 ticks/cell for T in 5..40 (worst %.3f)" % worst)

    r13 = ticks_per_cell(STANDARD_T, 0) / ticks_per_cell(STANDARD_T, pc)
    check(BAND[0] <= r13 <= BAND[1] and abs(r13 - 0.8) < 0.02,
          "standard colonist (T=%.2f): glass/granite speed = %.3f, in %s and ~0.80" % (STANDARD_T, r13, BAND))

    # "never full speed": strictly slower for every pawn below the engine's 450-tick cost cap, because pathCost is ADDED.
    # (At T >= 450 - pathCost both floors clamp to 450: a pawn that slow is immobile in practice, not "full speed".)
    never_full = all(cost(T / 10.0, pc) > cost(T / 10.0, 0) for T in range(10, int((450 - pc) * 10)))
    check(never_full, "glass strictly slower than granite for every T in 1..%d ticks/cell (never full speed below the cap)"
          % (450 - pc - 1))

    # Retune check: is 3 the pathCost closest to 0.80 for the standard pawn?
    best = min(range(0, 11), key=lambda c: abs(STANDARD_T / (STANDARD_T + c) - 0.80))
    check(best == pc, "pathCost closest to 0.80 for T=13.04 is %d (shipped %d)" % (best, pc))

    # The 2026-10-10 reading is outside the law: at T=9.8 the law says 0.77, the scene said 0.65.
    r98 = 9.8 / (9.8 + pc)
    check(abs(r98 - 0.65) > 0.08, "law at T=9.8 gives %.3f; the scene's 0.65 (implied pathCost %.1f) is outside the law (instrument suspect; A1 decides)"
          % (r98, 15 - 9.8))

    # The instrument: scenelib.run(n) never plays less than 200 ms at speed 4.
    lib = open(SCENELIB, encoding="utf-8").read()
    check("max(200," in lib, "scenelib.run floors each play_for at 200 ms (~80 ticks at speed 4): coarse for n=10")

    # The live proof must time with exact steps, not scenelib.run.
    if os.path.exists(PROVE):
        check(times_exactly(PROVE),
              "prove_glasswalk_speed.walk_exact's loop steps via step() -> rimworld/step_game_ticks; nothing calls S.run")
    else:
        check(False, "prove_glasswalk_speed.py exists")

    # The live proof measures a 13 ticks/cell pawn or says UNMEASURED (the item: "re-measure on a 13 ticks/cell pawn").
    if os.path.exists(PROVE):
        ok, rows, wired = gates_on_standard_pawn(PROVE)
        for label, got, want, line, wok in rows:
            print("   judge[%s] exit %d (want %d): %s" % (label, got, want, line))
        check(wired, "prove_glasswalk_speed.main picks the pawn with pick_standard_pawn and decides with judge; walk_exact times a fake 13 ticks/cell walk at 156 ticks and returns None on a blind reading")
        check(ok, "prove_glasswalk_speed.judge passes only a T=13.04+-0.7 pawn on law readings; the T=9.8 probe is "
                  "UNMEASURED and every base/delta/off-band/missing/averaging mutant exits 1")
        ok2, rows2 = main_end_to_end(PROVE)
        for label, got, want, line in rows2:
            print("   main[%s] exit %s (want %d): %s" % (label, got, want, line))
        check(ok2, "prove_glasswalk_speed.main() on a fake bridge: the checker's T=9.8 pawn exits 1 UNMEASURED, a T=13.04 "
                   "pawn on law readings exits 0 PASS (also as the 2nd spawn after an off-band one), a pawn drifting off-band after the pick exits 1 UNMEASURED, delta 5 (ratio 0.72) and the 0.65 world exit 1 FAIL, so do walks wrong singly but law-perfect on average; the map is dropped every time")

    print("RESULT SUMP_GLASSWALK_SPEED_RATIO_1/offline %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
