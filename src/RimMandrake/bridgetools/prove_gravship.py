#!/usr/bin/env python
"""Prove jawa/gravship_* live - GRAVSHIP_LAUNCH_TRAVEL_1's verify step.

SCRATCH QUICKTEST ONLY - never the campaign save. The launch DESTROYS the origin
map; that is the feature under test.

Run under python.exe (Windows loopback), game at main menu after launch_and_wait.sh:

    python.exe prove_gravship.py

What it proves, in order:
  1. gravship_status answers with no engine (quicktest map has none).
  2. A minimal flyable ship can be authored: substructure rect, GravEngine,
     PilotConsole, ChemfuelTank, thruster; fuel via the console's own numbers.
  3. launch_check REFUSES a hostile-range tile (exercise the refusal path).
  4. launch_check passes a near valid tile; launch dryRun=true moves nothing.
  5. launch dryRun=false: cutscene -> travel -> landingConfirmationPending.
  6. gravship_land confirms; new map exists; its tile == target (jawa/map_info /
     rimworld/get_game_info), colonists aboard.

⚠ Facts this script already respects (do not relearn them):
  * A tool-built ChemfuelTank needs time to register with thrusters - step_game_ticks
    ~600 between authoring and the first launch_check (map-authoring.md).
  * spawn_batch places factionless; build_batch with faction is the god-mode path.
  * The cutscene runs on WALL CLOCK (WorldComponentUpdate), travel runs on TICKS -
    poll status on a wall-clock sleep loop, and step_game_ticks for the travel leg.
  * Refuelling: no bridge primitive; use the debug action 'Set fuel to max' by path
    lookup (list_debug_action_children, never a constructed path), on the tank.
  * A LINKED thruster is not an ACTIVE one (THRUSTER_INSTABUILD_NEVER_ACTIVE_1):
    the 1x5 exhaust zone must be free of blockWind things AND substructure, and
    the state only refreshes on CompTickRare. jawa/inspect_string is the judge.
"""
import json
import sys
import time

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
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


def need(cond, msg):
    if not cond:
        print("FAIL:", msg)
        sys.exit(1)
    print("ok:", msg)


# -- 0. scratch map ----------------------------------------------------------
# start_debug_game_ready only works FROM THE MAIN MENU; on a loaded game it
# no-ops and the "quicktest" is silently the campaign. Go to the menu first.
if call("rimworld/get_game_info").get("status") == "game_loaded":
    mm = call("rimworld/go_to_main_menu")
    print("went to main menu:", mm.get("success", mm))
    time.sleep(5)
call("rimworld/start_debug_game_ready", timeoutMs=280000,
     readiness="mapData", pauseIfNeeded=True)
for _ in range(120):
    if call("rimworld/get_ui_state").get("programState") == "Playing":
        break
    time.sleep(1)

st = call("jawa/gravship_status")
need(st.get("success") is True, "gravship_status answers")
need(st.get("engineCount") == 0, "quicktest map has no engine (fresh baseline)")

# -- 1. author a minimal ship ------------------------------------------------
# Site + geometry per THRUSTER_INSTABUILD_NEVER_ACTIVE_1 (2026-08-29 mapping):
# CompGravshipThruster.CanBeActive needs the 1x5 exhaust exclusion zone (offset
# (0,0,-5), rotated with the thruster) free of blockWind things AND substructure,
# the facing edge outdoors, a linked engine, and a CompTickRare (250 ticks) to
# recalculate. So: flat roofless site, thruster on the pad's SOUTH EDGE with its
# exhaust hanging off-pad, zone force-cleared, ticks stepped, and the verdict
# read off jawa/inspect_string - never inferred.
def probe_site(X, Z):
    for sx in (0, 10, 19):
        for sz in (-7, 0, 10, 19):
            ci = call("rimworld/get_cell_info", x=X + sx, z=Z + sz).get("cell") or {}
            if ci.get("roofDefName") or not ci.get("walkable", False):
                return False
            if "water" in (ci.get("terrainDefName") or "").lower():
                return False
    return True

site = next(((X, Z) for X, Z in
             ((30, 40), (60, 40), (110, 60), (160, 90), (40, 110), (90, 130))
             if probe_site(X, Z)), None)
need(site is not None, "found a flat, roofless, walkable 20x20 site")
X, Z = site
print("site:", site)

# Clear the work rect plus the 8-row south margin the exhaust needs.
call("jawa/destroy_batch", rects=f"{X-1},{Z-8},22,29", categories="Plant,Item,Filth")
call("jawa/set_substructure_batch", action="set", rect=f"{X},{Z},20,20", doLeavings=False)
for op in (
    f"GravEngine:{X+10},{Z+10}",
    f"PilotConsole:{X+5},{Z+10}",
    f"ChemfuelTank:{X+14},{Z+10}",
    f"SmallThruster:{X+10},{Z+1},2",   # south edge, exhaust pointing off-pad
):
    r = call("jawa/build_batch", ops=op, faction="PlayerColony")
    need(r.get("success") and not r.get("failed"), f"built {op.split(':')[0]}")
call("jawa/map_commit", full=True)

# Multi-cell things spawn CENTRED: read the thruster's actual southmost cell,
# then guarantee its zone - 5 cells south of it, no substructure, nothing in it.
tx = X + 10
occ = [z for z in range(Z - 2, Z + 4)
       if any(t.get("defName") == "SmallThruster"
              for t in (call("rimworld/get_cell_info", x=tx, z=z).get("cell") or {}).get("things", []))]
need(occ, "thruster found on the map")
zone = f"{tx},{min(occ)-5},1,5"
call("jawa/set_substructure_batch", action="remove", rect=zone, doLeavings=False)
call("jawa/destroy_batch", rects=zone, categories="All")
call("jawa/map_commit", full=True)
print("exhaust zone cleared:", zone)

# Fuel the tank. There is NO refuel debug action on this modlist (measured:
# the only 'fuel' leaf under Actions is a vehicle lister). The route is the
# god-mode fill GIZMO: select the tank, list its gizmos, execute the fill one.
call("rimworld/set_god_mode", enabled=True)
call("rimworld/click_cell", x=X + 14, z=Z + 10)
giz = call("rimworld/list_selected_gizmos")
filled = False
for g in giz.get("gizmos", []):
    label = (g.get("label") or "") + " " + (g.get("description") or "")
    if "fuel" in label.lower() or "fill" in label.lower():
        fr = call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
        filled = bool(fr.get("success"))
        print("executed gizmo:", g.get("label"), "->", filled)
        break
if not filled:
    print("gizmos seen:", [g.get("label") for g in giz.get("gizmos", [])])
call("rimworld/set_god_mode", enabled=False)
call("rimworld/clear_selection")
print("tank filled:", filled)

call("rimworld/step_game_ticks", ticks=600)   # let comps register (rare tick = 250)

# Adjudicate thruster activity by the inspect pane, not by inference: a linked
# thruster is not an active one, and inspect_string names the failing gate.
active = False
for _ in range(6):
    ins = call("jawa/inspect_string", defName="SmallThruster")
    lines = [ln for th in (ins.get("things") or ins.get("results") or [])
             for ln in (th.get("inspect") or [])]
    bad = [ln for ln in lines if any(k in ln for k in
           ("Not functional", "Not connected", "Blocked", "must be outside"))]
    print("thruster inspect:", "; ".join(bad) if bad else "(no failing gate)")
    if lines and not bad:
        active = True
        break
    call("rimworld/step_game_ticks", ticks=300)
need(active, "thruster reports no failing gate (THRUSTER_INSTABUILD_NEVER_ACTIVE_1)")

# -- 2. refusal path ---------------------------------------------------------
far = call("jawa/gravship_launch_check", targetTile=1)  # tile 1: almost surely out of range
need(far.get("success") and far.get("wouldLaunch") is False and far.get("reasons"),
     "refusal path: far/invalid tile refuses with reasons: %s" % far.get("reasons"))

# -- 3. find a near valid tile ----------------------------------------------
# jawa/world_neighbors is a whole-world CSV dumper (its `path` is an output
# file). Dump once, read the origin row, expand two rings of neighbours.
origin = call("jawa/gravship_status")["engines"][0]["tile"]
import os as _os
csv_path = _os.path.join(_os.environ.get("TEMP", r"C:\Windows\Temp"), "qt_neighbors.csv")
call("jawa/world_neighbors", path=csv_path)
nbr = {}
with open(csv_path) as fh:
    for line in fh:
        parts = line.strip().split(",")
        if parts and parts[0].isdigit():
            nbr[int(parts[0])] = [int(p) for p in parts[1:] if p.strip().lstrip("-").isdigit()]
ring = list(nbr.get(origin, []))
ring += [t2 for t in ring for t2 in nbr.get(t, [])]
target = None
for t in dict.fromkeys(ring):
    if t == origin or t < 0:
        continue
    chk = call("jawa/gravship_launch_check", targetTile=t)
    if chk.get("wouldLaunch"):
        target = t
        print("target tile:", t, "cost", chk.get("fuelCost"), "dist", chk.get("distance"))
        break
    else:
        print("  tile", t, "refused:", chk.get("reasons"))
need(target is not None, "found a launchable neighbour tile")

# -- 4. dryRun moves nothing -------------------------------------------------
dr = call("jawa/gravship_launch", targetTile=target)      # dryRun defaults TRUE
need(dr.get("success") and dr.get("dryRun") is True and dr.get("launched") is False,
     "dryRun default true, nothing launched")
st = call("jawa/gravship_status")
need(st["engineCount"] == 1 and not st["travelling"], "state unchanged after dryRun")

# -- 4b. colonists aboard ----------------------------------------------------
# The launch takes what stands on substructure; everything else dies with the
# origin map. Walk every colonist onto the pad (drafted, so they hold position).
ordr = call("jawa/order_pawn", pawnId="colonists", x=X + 8, z=Z + 8,
            waitTicks=5000, timeoutSeconds=180, unpause=True)
aboard = 0
for row in (ordr.get("pawns") or ordr.get("results") or []):
    end = row.get("end") or row.get("endCell") or {}
    if X <= end.get("x", -1) < X + 20 and Z <= end.get("z", -1) < Z + 20:
        aboard += 1
print("colonists standing on the pad:", aboard)
need(aboard >= 1, "at least one colonist aboard before launch")

# -- 5. launch ---------------------------------------------------------------
go = call("jawa/gravship_launch", targetTile=target, dryRun=False)
need(go.get("launched") is True, "launched; origin map will be destroyed: %s" % go.get("originMapWillBeDestroyed"))
deadline = time.time() + 180
pending = False
while time.time() < deadline:
    call("rimworld/step_game_ticks", ticks=250)
    st = call("jawa/gravship_status")
    print("  state: cutscene=%s travelling=%s landing=%s" % (
        st.get("cutsceneInProgress"), st.get("travelling"), st.get("landingConfirmationPending")))
    if st.get("landingConfirmationPending"):
        pending = True
        break
    time.sleep(2)
need(pending, "reached the landing-marker halfway state")

# -- 6. land -----------------------------------------------------------------
# skipCutscene defaults TRUE (GRAVSHIP_LANDING_DIRECT_PLACE_1): placement is
# synchronous, no render chain, no wall-clock cutscene wait needed.
land = call("jawa/gravship_land")
need(land.get("success") is True, "landing confirmed at %s" % land.get("landedAt"))
time.sleep(3)
call("rimworld/step_game_ticks", ticks=250)
st = call("jawa/gravship_status")
need(st["engineCount"] == 1, "engine exists after landing")
need(st["engines"][0]["tile"] == target, "new map tile == target (%s)" % target)
for part in ("GravEngine", "PilotConsole", "ChemfuelTank", "SmallThruster"):
    ins = call("jawa/inspect_string", defName=part)
    n = len(ins.get("things") or ins.get("results") or [])
    need(n >= 1, "%s present on the new map (x%d)" % (part, n))
cols = call("rimworld/list_colonists", currentMapOnly=True)
ncol = len(cols.get("colonists", cols) or [])
need(ncol >= 1, "colonists alive on the new map: %d" % ncol)
print("\nALL CHECKS PASSED")
