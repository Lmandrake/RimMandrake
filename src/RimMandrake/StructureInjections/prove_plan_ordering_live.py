"""prove_plan_ordering_live.py -- TILE_STRUCTURE_DESIGNS_1 clause A1, against the running game.

The claim: GenStep_RimplacePlan.ApplyPlan lands a plan's terrain, things and roof in the right order, so what the plan
says is what stands on the map, and it still stands after the game runs. The roster's flagged risk was the order of
terrain and roof (a roof that lands before its walls collapses; a floor laid under a later building is replaced).

Steps, on the current map (the lane's quicktest map):
  1. pick an anchor near the map centre, clear the plan's rect (jawa/clear_area, destroy) so nothing is left to clear;
  2. replay Templates/dwelling_test.txt there by the mod's own debug action (it calls ApplyPlan, as Generate does);
  3. read back every TERRAIN cell (jawa/get_terrain_batch) and every ROOF cell (jawa/get_roof_batch) of the plan, and
     every planned Wall (jawa/list_things in the rect);
  4. step 2500 ticks (unsupported roof collapses well inside that) and read the roof and the walls again.
A1 holds when every planned terrain cell reads its terrain, every planned roof cell reads its roof both times, and every
planned wall stands both times. A read that returns no cells is UNMEASURED, never a pass.

    python.exe src/RimMandrake/StructureInjections/prove_plan_ordering_live.py
    python3 src/RimMandrake/StructureInjections/prove_plan_ordering_live.py --selftest   (offline: parse and judge)

Exit 0 holds, 1 fails, 2 UNMEASURED (no bridge, no map, the mod or its debug action is absent, a read came back empty).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PLAN = os.path.join(HERE, "Templates", "dwelling_test.txt")
ACTION = "Actions\\T: Run plan: dwelling_test.txt"
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
TICKS = 2500   # roof collapse of an unsupported roof is checked every few hundred ticks; 2500 is far past it


def parse(path=PLAN):
    """-> {footprint: (x, z, w, h), terrain: {(x,z): def}, roof: {(x,z): def}, walls: {(x,z)}} in plan coordinates."""
    out = {"footprint": None, "terrain": {}, "roof": {}, "walls": set()}
    with open(path, encoding="utf-8") as f:
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if p[0] == "FOOTPRINT":
                out["footprint"] = tuple(int(v) for v in p[1:5])
            elif p[0] == "TERRAIN":
                out["terrain"][(int(p[1]), int(p[2]))] = p[3]
            elif p[0] == "ROOF":
                out["roof"][(int(p[1]), int(p[2]))] = p[3]
            elif p[0] == "THING" and p[1] == "Wall":
                out["walls"].add((int(p[2]), int(p[3])))
    return out


def cells_of(ops):
    """The ops grammar of get_terrain_batch / get_roof_batch (JawaBenchTerrainTools.TryParseOps): `Def:x,z,w,h`,
    separated by ';' or newlines; w and h default 1. -> {(x, z): def}."""
    out = {}
    for op in re.split(r"[;\n\r]", ops or ""):
        op = op.strip()
        if not op:
            continue
        d, sep, coords = op.partition(":")
        nums = [v.strip() for v in coords.split(",")] if sep else []
        if not sep or not d.strip() or len(nums) not in (2, 4) or not all(re.fullmatch(r"-?\d+", v) for v in nums):
            raise ValueError("an op this reader does not know: %r" % op[:80])
        x, z = int(nums[0]), int(nums[1])
        w, h = (int(nums[2]), int(nums[3])) if len(nums) == 4 else (1, 1)
        for i in range(w):
            for j in range(h):
                out[(x + i, z + j)] = d.strip()
    return out


def judge(plan, off, terrain, roof, walls_at, label):
    """plan cells shifted by off=(dx, dz) against the read maps. -> list of faults (empty = holds)."""
    dx, dz = off
    bad = []
    if terrain is not None:
        miss = [(c, d, terrain.get((c[0] + dx, c[1] + dz))) for c, d in sorted(plan["terrain"].items())
                if terrain.get((c[0] + dx, c[1] + dz)) != d]
        if miss:
            bad.append("%s: %d of %d terrain cells wrong, e.g. %s" % (label, len(miss), len(plan["terrain"]), miss[:3]))
    miss = [(c, d, roof.get((c[0] + dx, c[1] + dz))) for c, d in sorted(plan["roof"].items())
            if roof.get((c[0] + dx, c[1] + dz)) != d]
    if miss:
        bad.append("%s: %d of %d roof cells wrong, e.g. %s" % (label, len(miss), len(plan["roof"]), miss[:3]))
    gone = sorted(c for c in plan["walls"] if (c[0] + dx, c[1] + dz) not in walls_at)
    if gone:
        bad.append("%s: %d of %d walls missing, e.g. %s" % (label, len(gone), len(plan["walls"]), gone[:3]))
    return bad


def selftest():
    plan = parse()
    ok = len(plan["terrain"]) == 130 and len(plan["roof"]) == 192 and plan["footprint"] == (100, 100, 16, 12) and plan["walls"]
    print("%s  the plan parses: %d terrain, %d roof, %d walls, footprint %s" % (
        "ok  " if ok else "FAIL", len(plan["terrain"]), len(plan["roof"]), len(plan["walls"]), plan["footprint"]))
    bad = 0 if ok else 1
    off = (400, 400)
    t = {(x + 400, z + 400): d for (x, z), d in plan["terrain"].items()}
    r = {(x + 400, z + 400): d for (x, z), d in plan["roof"].items()}
    w = {(x + 400, z + 400) for (x, z) in plan["walls"]}
    one_roof = next(iter(r))
    cases = [
        ("a true read holds", t, r, w, 0),
        ("a lost roof cell fails", t, {k: v for k, v in r.items() if k != one_roof}, w, 1),
        ("a wrong floor fails", {k: ("Soil" if i == 0 else v) for i, (k, v) in enumerate(sorted(t.items()))}, r, w, 1),
        ("a missing wall fails", t, r, set(list(w)[1:]), 1),
    ]
    for name, tt, rr, ww, want in cases:
        got = 1 if judge(plan, off, tt, rr, ww, "x") else 0
        print("%s  %s" % ("ok  " if got == want else "FAIL", name))
        bad += got != want
    for ops, want in (("StrawMatting:100,100,3,1", {(100, 100): "StrawMatting", (101, 100): "StrawMatting", (102, 100): "StrawMatting"}),
                      ("RoofConstructed:5,6;None:7,6,1,2", {(5, 6): "RoofConstructed", (7, 6): "None", (7, 7): "None"})):
        got = cells_of(ops)
        print("%s  ops %r read" % ("ok  " if got == want else "FAIL", ops))
        bad += got != want
    print("selftest %s" % ("passed" if not bad else "FAILED"))
    return 1 if bad else 0


def must(b, tool, **kw):
    r = b.call(tool, **kw)
    if not isinstance(r, dict) or r.get("success") is False:
        raise RuntimeError("%s refused: %s" % (tool, str(r)[:300]))
    return r


def walls(b, rect):
    """-> {(x, z)} of the Walls standing in rect. A row with no position dict is a reader fault, raised."""
    r = must(b, "jawa/list_things", defName="Wall", rect=rect, limit=2000)
    out = set()
    for t in r.get("things") or []:
        pos = t.get("position")
        if not isinstance(pos, dict):
            raise RuntimeError("list_things gave a row with no position: %r" % (str(t)[:200],))
        out.add((int(pos["x"]), int(pos["z"])))
    return out


def live():
    import validation_core as vc
    b = vc.Bridge()
    plan = parse()
    fx, fz, fw, fh = plan["footprint"]
    mi = must(b, "jawa/map_info")
    sx, sz = int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or 0)
    if sx < 60 or sz < 60:
        return 2, ["UNMEASURED: no map, or a map too small (%sx%s)" % (sx, sz)]
    x, z = sx // 2, sz // 2           # the anchor: the plan's footprint origin lands here
    dx, dz = x - fx, z - fz
    rect = "%d,%d,%d,%d" % (x - 2, z - 2, fw + 4, fh + 4)
    must(b, "jawa/clear_area", rect=rect, dryRun=False)
    b.call("rimworld/execute_debug_action", path=ACTION, x=x, z=z)
    trects = ";".join("%d,%d,1,1" % (c[0] + dx, c[1] + dz) for c in sorted(plan["terrain"]))
    rrects = ";".join("%d,%d,1,1" % (c[0] + dx, c[1] + dz) for c in sorted(plan["roof"]))
    terrain = cells_of(must(b, "jawa/get_terrain_batch", rects=trects).get("ops"))
    roof = cells_of(must(b, "jawa/get_roof_batch", rects=rrects).get("ops"))
    w0 = walls(b, rect)
    if not terrain or not roof:
        return 2, ["UNMEASURED: a read came back empty (terrain %d cells, roof %d cells)" % (len(terrain), len(roof))]
    if not w0:
        return 1, ["FAIL: no Wall stands in %s after the replay (did the debug action run? is mandrake.rm.injections loaded?)" % rect]
    lines = ["anchor (%d,%d) offset (%d,%d); read %d terrain, %d roof, %d walls" % (x, z, dx, dz, len(terrain), len(roof), len(w0))]
    bad = judge(plan, (dx, dz), terrain, roof, w0, "after replay")
    b.call("rimworld/step_game_ticks", ticks=TICKS)
    roof2 = cells_of(must(b, "jawa/get_roof_batch", rects=rrects).get("ops"))
    bad += judge(plan, (dx, dz), None, roof2, walls(b, rect), "after %d ticks" % TICKS)
    return (1 if bad else 0), lines + bad


def main(argv):
    if "--selftest" in argv:
        return selftest()
    try:
        code, lines = live()
    except Exception as e:  # noqa: BLE001 - a refused or failed call is no verdict
        code, lines = 2, ["UNMEASURED: %s" % str(e)[:400]]
    for ln in lines:
        print("A1  " + ln)
    print("A1 %s" % {0: "PASS", 1: "FAIL"}.get(code, "UNMEASURED"))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
