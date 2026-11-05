#!/usr/bin/env python3
"""Live proof of PLAYER_START_SITE_1 clause A1: the yard spawns around an empty landing clearing.

    python.exe src/RimUtinni/StructureInjectionsRUT/Source/ZeddosYard/zeddos_yard_live_proof.py A1 < /dev/null

Needs: the game up on a disposable quicktest map (any size >= 170), StructureInjections +
StructureInjectionsRUT deployed. MUTATES THAT MAP (runs RUT_GenStep_ZeddosYard through
jawa/run_genstep, as StructureInjectionsRUT/validation.py does for every other plan); never run it
on a canonical save. Exit 0 when the clause holds, 1 when it does not, 2 on usage.

A1 holds when, after one run of the GenStep:
  * the ship-wreck defs the plan names grew by >= 60 things on the map and AncientFortifiedWall by >= 10
    (before/after delta, so pre-existing map content cannot pass for the yard);
  * none of the plan's defNames stands inside the map-placed landing clearing (the plan's centred
    100x94 rect, at least the item's fixed 96x90, offset exactly as RM_PlanKernel.Offset centres a footprint on map.Center);
  * a cell the plan paints AncientMegastructure reads back as AncientMegastructure.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import gen_zeddos_yard_plan as gen  # noqa: E402
import rimbridge_client as rb  # noqa: E402

GENSTEP = "RUT_GenStep_ZeddosYard"
# The item's floor, FIXED (not gen's constants): v2 ring hull 92x86 + 2-cell margin each side.
NEED_W, NEED_H = 92 + 2 * 2, 86 + 2 * 2   # 96, 90


def count(b, defs, rect=None):
    """countMatched of one jawa/list_things; a reply without success and an integer countMatched is a
    FAIL, never a zero (a missing baseline would manufacture growth; a missing clearing read would pass)."""
    params = {"defName": ",".join(sorted(defs)), "limit": 5000}
    if rect:
        params["rect"] = "%d,%d,%d,%d" % rect
    r = b.call("jawa/list_things", params) or {}
    n = r.get("countMatched")
    if r.get("success") is not True or not isinstance(n, int) or isinstance(n, bool):
        raise SystemExit("A1 FAIL: jawa/list_things gave no count evidence: %s" % json.dumps(r)[:300])
    return n


def main(argv):
    if argv[1:] != ["A1"]:
        print(__doc__)
        return 2
    host, port, token = rb.resolve_endpoint()
    lay = gen.layout()
    plan_defs = {t[0] for t in lay["things"]}
    ship_defs = set(gen.SHIP_DEFS)
    with rb.RimBridge(host, port, token, timeout=240) as b:
        info = b.call("jawa/map_info") or {}
        map_id = info.get("mapId")
        sx, sz = info.get("sizeX"), info.get("sizeZ")
        if map_id is None:
            print("A1 FAIL: jawa/map_info gave no mapId; cannot bind the proof to one map")
            return 1
        if not sx or not sz or sx < gen.W or sz < gen.H:
            print("A1 FAIL: no map or map smaller than the %dx%d plan (map_info sizeX=%r sizeZ=%r)" % (gen.W, gen.H, sx, sz))
            return 1
        dx, dz = sx // 2 - gen.W // 2, sz // 2 - gen.H // 2      # RM_PlanKernel.Offset, centerOnMap
        cx0, cz0, cw, ch = gen.clearing_rect()
        if cw < NEED_W or ch < NEED_H:
            print("A1 FAIL: the plan's landing clearing is %dx%d, below the item's 96x90 (hull 92x86 + 2)" % (cw, ch))
            return 1
        clearing = (cx0 + dx, cz0 + dz, cw, ch)
        # list_things / run_genstep / get_terrain_batch act on Find.CurrentMap and take no map id, so the
        # proof re-reads mapId after EVERY call and fails on any change: a map switch can then only hide
        # inside one call's round trip. The bridge is leased to one driver, so that window is not used.
        def same_map(step):
            now = (b.call("jawa/map_info") or {}).get("mapId")
            if now != map_id:
                raise SystemExit("A1 FAIL: the current map changed at %s (mapId %r -> %r)" % (step, map_id, now))

        ships0 = count(b, ship_defs); same_map("baseline ships")
        walls0 = count(b, {gen.MEGA_WALL}); same_map("baseline walls")
        r = b.call("jawa/run_genstep", {"genStepDef": GENSTEP}) or {}
        same_map("run_genstep")
        if not r.get("success"):
            print("A1 FAIL: jawa/run_genstep(%s) -> %s" % (GENSTEP, json.dumps(r)[:400]))
            return 1
        ships1 = count(b, ship_defs); same_map("after ships")
        walls1 = count(b, {gen.MEGA_WALL}); same_map("after walls")
        inside = count(b, plan_defs, clearing); same_map("clearing")
        mx, mz, _ = lay["terrain"][len(lay["terrain"]) // 2]
        t = b.call("jawa/get_terrain_batch", {"rects": "%d,%d,1,1" % (mx + dx, mz + dz), "mapId": map_id}) or {}
        same_map("terrain")
        # one cell read: success, exactly one cell read, and its only distinct terrain is the plan's
        mega_ok = (t.get("success") is True and t.get("cellsRead") == 1
                   and t.get("distinctTerrains") == [gen.MEGA_TERRAIN])
    ok = ships1 - ships0 >= 60 and walls1 - walls0 >= 10 and inside == 0 and mega_ok
    print("A1 %s: ship wrecks +%d (need >=60), wall stubs +%d (need >=10), plan things inside clearing %s = %d (need 0), "
          "megastructure at (%d,%d) = %s" % ("PASS" if ok else "FAIL", ships1 - ships0, walls1 - walls0, clearing, inside,
                                              mx + dx, mz + dz, mega_ok))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
