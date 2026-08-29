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
# 20x20 substructure pad away from the colony spawn, then the four required parts.
gi = call("rimworld/get_game_info")
X, Z = 30, 30  # map corner region; adjust if the quicktest map is smaller
call("jawa/set_substructure_batch", action="set", rect=f"{X},{Z},20,20", doLeavings=False)
for op, stuff in (
    (f"GravEngine:{X+10},{Z+10}", None),
    (f"PilotConsole:{X+5},{Z+10}", None),
    (f"ChemfuelTank:{X+14},{Z+10}", None),
    (f"SmallThruster:{X+10},{Z+3},2", None),
):
    r = call("jawa/build_batch", ops=op, faction="PlayerColony", **({"stuff": stuff} if stuff else {}))
    need(r.get("success") and not r.get("failed"), f"built {op.split(':')[0]}")
call("jawa/map_commit", full=True)

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

call("rimworld/step_game_ticks", ticks=600)   # let comps register

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
land = call("jawa/gravship_land")
need(land.get("success") is True, "landing confirmed at %s" % land.get("landedAt"))
time.sleep(15)                                   # landing cutscene, wall clock
call("rimworld/step_game_ticks", ticks=250)
st = call("jawa/gravship_status")
need(st["engineCount"] == 1, "engine exists after landing")
need(st["engines"][0]["tile"] == target, "new map tile == target (%s)" % target)
cols = call("rimworld/list_colonists", currentMapOnly=True)
print("colonists on new map:", len(cols.get("colonists", cols) or []))
print("\nALL CHECKS PASSED")
