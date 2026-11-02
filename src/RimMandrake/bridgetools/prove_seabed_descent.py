#!/usr/bin/env python
"""Prove SEABED_DESCENT_ASCENT_1 live: a gravship flies from a sea tile down to its RM_SeabedLayer floor and back up.

SCRATCH QUICKTEST ONLY - never the campaign save. Every launch DESTROYS the map it leaves.

    python.exe prove_seabed_descent.py --out <win-dir>            run it all, write <out>/descent_proof.json
    python.exe prove_seabed_descent.py --out <win-dir> --read A2  exit 0/1 on one clause of the last run (<= 3 h old)

Clauses (infrastructure/state/live_proofs/SEABED_DESCENT_ASCENT_1.criteria):
  A1  from a surface map beside a sea, the pilot console's own gates (jawa/gravship_launch_check, which reproduces
      CompPilotConsole's tile-picker closure argument for argument) accept a tile on RM_SeabedLayer, and its fuel cost
      carries the depth fuel: its price minus the same route's surface price is 0.2 x depth (shipped settings,
      Patch_SeabedDescentFuel).
  A2  after the flight lands, Find.CurrentMap.Tile.Layer is RM_SeabedLayer and the map's parent is RM_SeabedSite.
  A3  launching from that floor back to a surface tile lands there: Find.CurrentMap.Tile.Layer is the surface again,
      and the climb pays the same depth fuel over the same baseline.

Step 0 reuses prove_gravship.py whole (fresh quicktest, a minimal flyable ship, one launch and landing); this script
starts from the ship it leaves on the surface. A clause whose step was never reached reads UNMEASURED (exit 1).
Never a flyer's flight: this moves a gravship, no creature.
"""
_RM_ROOT = __import__("pathlib").Path(__file__).resolve().parents[3]  # repo root, derived (not hardcoded)
import argparse
import json
import os
import subprocess
import sys
import time

SEABED = "RM_SeabedLayer"
SITE = "RM_SeabedSite"
FUEL_PER_METRE = 0.2   # RM_SeabedDescentKernel.DefaultFuelPerMeter, the shipped setting
MAX_AGE_S = 3 * 3600


def result_path(out):
    return os.path.join(out, "descent_proof.json")


def read_clause(out, clause):
    p = result_path(out)
    if not os.path.exists(p):
        print("UNMEASURED: no run on record at", p)
        return 1
    age = time.time() - os.path.getmtime(p)
    if age > MAX_AGE_S:
        print("UNMEASURED: last run is %.1f h old (> 3 h)" % (age / 3600))
        return 1
    rec = json.load(open(p)).get(clause)
    if not rec:
        print("UNMEASURED:", clause, "was never reached")
        return 1
    print(clause, "PASS" if rec.get("pass") else "FAIL", rec.get("why"))
    return 0 if rec.get("pass") else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Windows-visible directory for descent_proof.json")
    ap.add_argument("--read", choices=("A1", "A2", "A3"), help="only report one clause of the last run")
    ap.add_argument("--skip-setup", action="store_true", help="a ship already stands on the surface (debugging)")
    a = ap.parse_args()
    if a.read:
        return read_clause(a.out, a.read)

    os.makedirs(a.out, exist_ok=True)
    results = {}

    def record(clause, ok, why):
        results[clause] = {"pass": bool(ok), "why": why, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
        json.dump(results, open(result_path(a.out), "w"), indent=1)
        print(clause, "PASS" if ok else "FAIL", why)

    json.dump(results, open(result_path(a.out), "w"))   # a fresh, empty record: a stale PASS never survives a rerun

    if not a.skip_setup:
        here = os.path.dirname(os.path.abspath(__file__))
        rc = subprocess.run([sys.executable, os.path.join(here, "prove_gravship.py")]).returncode
        if rc != 0:
            print("UNMEASURED: prove_gravship.py setup failed (exit %d); no clause reached" % rc)
            return 1

    sys.path.insert(0, str(_RM_ROOT / "src" / "RimMandrake" / "Utils"))
    import rimbridge_client as rb  # noqa: E402
    host, port, token = rb.resolve_endpoint()
    S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
    S.connect()

    def call(t, **p):
        r = S.call(t, p) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
        return r

    def refuel():
        """prove_gravship.py's fill: god mode, select each tank, run the gizmo whose label STARTS WITH 'DEBUG: Fill'
        (a loose 'fill' match once ran 'Allow manual refill' and reported success on an empty tank)."""
        tanks = call("jawa/inspect_string", defName="ChemfuelTank").get("things") or []
        filled = 0
        call("rimworld/set_god_mode", enabled=True)
        for t in tanks:
            call("rimworld/click_cell", x=t.get("x"), z=t.get("z"))
            for g in call("rimworld/list_selected_gizmos").get("gizmos", []):
                if (g.get("label") or "").startswith("DEBUG: Fill"):
                    filled += bool(call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id")).get("success"))
                    break
            call("rimworld/clear_selection")
        call("rimworld/set_god_mode", enabled=False)
        print("refuelled %d of %d tanks" % (filled, len(tanks)))

    def fly(target, layer):
        """Launch to (target, layer), step to the landing marker, land. Returns the status after landing."""
        go = call("jawa/gravship_launch", targetTile=target, layer=layer, dryRun=False)
        if go.get("launched") is not True:
            return None, "launch refused: %s" % go
        deadline = time.time() + 240
        while time.time() < deadline:
            call("rimworld/step_game_ticks", ticks=250)
            st = call("jawa/gravship_status")
            if st.get("landingConfirmationPending"):
                break
            time.sleep(2)
        else:
            return None, "never reached the landing marker"
        land = call("jawa/gravship_land")
        if land.get("success") is not True:
            return None, "landing failed: %s" % land
        time.sleep(3)
        call("rimworld/step_game_ticks", ticks=250)
        return call("jawa/gravship_status"), go

    st = call("jawa/gravship_status")
    if st.get("engineCount") != 1:
        print("UNMEASURED: expected one grav engine after setup, have", st.get("engineCount"))
        return 1
    origin = st["engines"][0]["tile"]
    surface_layer = st["engines"][0].get("layer")
    print("ship on", surface_layer, "tile", origin)

    # -- A1: the console's gates offer a floor tile under a nearby sea ------------------------------------------
    csv_path = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "qt_neighbors.csv")
    call("jawa/world_neighbors", path=csv_path)
    nbr = {}
    with open(csv_path) as fh:
        for line in fh:
            parts = line.strip().split(",")
            if parts and parts[0].isdigit():
                nbr[int(parts[0])] = [int(x) for x in parts[1:] if x.strip().lstrip("-").isdigit()]
    refuel()
    seen, frontier, floor_chk, floor_tile, probed = {origin}, [origin], None, None, 0
    for ring in range(1, 12):
        nxt = []
        for t in frontier:
            for n in nbr.get(t, []):
                if n >= 0 and n not in seen:
                    seen.add(n)
                    nxt.append(n)
        frontier = nxt
        for t in frontier:
            probed += 1
            chk = call("jawa/gravship_launch_check", targetTile=t, layer=SEABED)
            if chk.get("wouldLaunch") and chk.get("targetLayer") == SEABED and (chk.get("targetElevation") or 0) < 0:
                floor_chk, floor_tile = chk, t
                break
        if floor_chk:
            break
    if not floor_chk:
        record("A1", False, "no RM_SeabedLayer tile accepted within 11 rings (%d probed) of tile %d" % (probed, origin))
        return 1
    depth = -float(floor_chk["targetElevation"])
    # The same route priced on the surface: the twin layer makes floor tile N sit under surface tile N, so the
    # vanilla part of both prices (distance from the origin, floored at 50) is identical and only the depth fuel
    # differs. The surface tile is sea, so the check refuses it, but it still reports its fuelCost.
    base = call("jawa/gravship_launch_check", targetTile=floor_tile, layer=surface_layer)
    if base.get("fuelCost") is None or base.get("targetLayer") != surface_layer:
        record("A1", False, "could not read the surface price of tile %d: %s" % (floor_tile, base))
        return 1
    baseline = float(base["fuelCost"])
    surcharge = FUEL_PER_METRE * depth
    cost = float(floor_chk["fuelCost"])
    record("A1", depth > 0 and abs((cost - baseline) - surcharge) <= 0.5,
           "floor tile %d (%s, depth %.0f m) accepted; fuelCost %.1f = surface price %.1f + depth fuel %.1f (want %.1f)" % (
               floor_tile, floor_chk.get("targetBiome"), depth, cost, baseline, cost - baseline, surcharge))

    # -- A2: descend; the landed map is on the floor layer -------------------------------------------------------
    st2, go = fly(floor_tile, SEABED)
    if st2 is None:
        record("A2", False, go)
        return 1
    ok2 = st2.get("currentMapLayer") == SEABED and st2.get("currentMapParent") == SITE and st2.get("currentMapTile") == floor_tile
    record("A2", ok2, "after descent: Find.CurrentMap.Tile.Layer=%s parent=%s tile=%s (want %s/%s/%d)" % (
        st2.get("currentMapLayer"), st2.get("currentMapParent"), st2.get("currentMapTile"), SEABED, SITE, floor_tile))
    if not ok2:
        return 1

    # -- A3: climb back to the surface tile the ship came from ---------------------------------------------------
    refuel()
    up = call("jawa/gravship_launch_check", targetTile=origin, layer=surface_layer)
    if not up.get("wouldLaunch"):
        record("A3", False, "the console refuses the surface tile %d from the floor: %s" % (origin, up.get("reasons")))
        return 1
    st3, go3 = fly(origin, surface_layer)
    if st3 is None:
        record("A3", False, go3)
        return 1
    up_cost = float(up.get("fuelCost") or 0)
    ok3 = (st3.get("currentMapLayer") == surface_layer and st3.get("currentMapTile") == origin
           and abs((up_cost - baseline) - surcharge) <= 0.5)
    record("A3", ok3, "after ascent: Find.CurrentMap.Tile.Layer=%s tile=%s (want %s/%d); climb fuelCost %.1f = surface price %.1f + depth fuel %.1f (want %.1f)" % (
        st3.get("currentMapLayer"), st3.get("currentMapTile"), surface_layer, origin, up_cost, baseline, up_cost - baseline, surcharge))
    return 0 if all(r["pass"] for r in results.values()) and len(results) == 3 else 1


if __name__ == "__main__":
    sys.exit(main())
