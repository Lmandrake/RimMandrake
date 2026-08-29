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
def fresh_quicktest():
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

fresh_quicktest()
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
    """The whole work rect must be roof-free (no mountain, no collapse risk when
    clearing) and hold no water/impassable-liquid terrain. Rock walls and chunks
    are THINGS, invisible to terrain reads - the roof-free guarantee makes them
    safe to bulldoze wholesale below."""
    rect = f"{X-1},{Z-8},22,29"
    roofs = call("jawa/get_roof_batch", rects=rect)
    if not roofs.get("success") or any(r != "None" for r in roofs.get("roofs", [])):
        return False
    terr = call("jawa/get_terrain_batch", rects=rect)
    return bool(terr.get("success")) and not any(
        w in t.lower() for t in terr.get("terrains", [])
        for w in ("water", "marsh", "lava", "mud", "bridge"))

def scan_for_site():
    return next(((X, Z) for Z in range(40, 211, 24) for X in range(30, 211, 24)
                 if probe_site(X, Z)), None)

site = scan_for_site()
for _ in range(2):                      # an all-mountain map: reroll, ~90 s each
    if site:
        break
    print("no roof-free site on this map; rerolling the quicktest")
    fresh_quicktest()
    site = scan_for_site()
need(site is not None, "found a roof-free, dry 20x20 site (grid scan)")
X, Z = site
print("site:", site)

# Bulldoze the work rect plus the 8-row south margin the exhaust needs.
# Building is included deliberately: stray mineables blockWind and the rect is
# proven roof-free, so there is nothing above to collapse.
call("jawa/destroy_batch", rects=f"{X-1},{Z-8},22,29",
     categories="Plant,Item,Filth,Building")
call("jawa/set_substructure_batch", action="set", rect=f"{X},{Z},20,20", doLeavings=False)
# Substructure is REFUSED, silently, on floor terrain (AncientConcrete ruins on
# quicktest maps - 75/400 cells on 2026-08-29). Parts standing in a hole read
# "Not connected to grav engine". Verify coverage; repaint holes to Soil, retry.
holes = []
for _ in range(2):
    tl = call("jawa/get_terrain_layers", rect=f"{X},{Z},20,20", limit=400)
    holes = [c for c in tl.get("cells", []) if not c.get("isSubstructure")]
    if not holes:
        break
    print("substructure holes:", len(holes), "- repainting to Soil, retrying")
    call("jawa/set_terrain_batch",
         ops=";".join(f"Soil:{c['x']},{c['z']},1,1" for c in holes))
    call("jawa/set_substructure_batch", action="set", rect=f"{X},{Z},20,20", doLeavings=False)
need(not holes, "substructure covers the full pad (400/400)")
for op in (
    f"GravEngine:{X+10},{Z+10}",
    f"PilotConsole:{X+5},{Z+10}",
    f"ChemfuelTank:{X+14},{Z+10}",
    # Rot 0 (north-FACING): GetExclusionZone puts the 1x5 zone and the exhaust
    # on the OPPOSITE side of the rotation (offset (0,0,-5) rotates with rot),
    # i.e. south of pos - off-pad. Rot 2 was measured blocked by the pad itself.
    f"SmallThruster:{X+10},{Z+1},0",
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

# Fuel, VGE-style (measured 2026-08-29): on this modlist ChemfuelTank is VGE's
# astrofuel storage (PipeSystem.CompProperties_ResourceStorage, net
# VGE_AstrofuelNet, capacity 250) and SmallThruster is a net CONSUMER whose
# CanBeActive is postfixed false while its net has no fuel
# (CompGravshipThruster_CanBeActive_Patch + CompResourceThruster.HasFuel).
# So: pipe the tank to the thruster, then god-mode-fill the tank. A tank and
# thruster with no pipe between them are two separate one-building nets.
def cells_of(defname, x0, z0, r=3):
    out = []
    for cx in range(x0 - r, x0 + r + 1):
        for cz in range(z0 - r, z0 + r + 1):
            things = (call("rimworld/get_cell_info", x=cx, z=cz).get("cell") or {}).get("things", [])
            if any(t.get("defName") == defname for t in things):
                out.append((cx, cz))
    return out

tank_cells = set(cells_of("ChemfuelTank", X + 14, Z + 10))
thr_cells = set(cells_of("SmallThruster", tx, Z + 1))
need(tank_cells and thr_cells, "tank and thruster footprints read back")
pipe_cells = []
for pz in range(Z + 2, Z + 10):            # vertical run beside the tank column
    pipe_cells.append((X + 14, pz))
for px in range(X + 11, X + 14):           # horizontal run toward the thruster
    pipe_cells.append((px, Z + 2))
pipe_cells.append((tx, Z + 3))             # cardinal-adjacent to the thruster
pipe_cells = [c for c in pipe_cells if c not in tank_cells | thr_cells]
ops = ";".join(f"VGE_AstrofuelPipe:{cx},{cz}" for cx, cz in dict.fromkeys(pipe_cells))
r = call("jawa/build_batch", ops=ops, faction="PlayerColony")
need(r.get("success") and not r.get("failed"), "astrofuel pipe run built (%d cells)" % len(pipe_cells))
call("jawa/map_commit", full=True)
call("rimworld/step_game_ticks", ticks=60)  # let the pipe net regenerate

call("rimworld/set_god_mode", enabled=True)
call("rimworld/click_cell", x=min(tank_cells)[0], z=min(tank_cells)[1])
giz = call("rimworld/list_selected_gizmos")
labels = [(g.get("label") or "") for g in giz.get("gizmos", [])]
print("tank gizmos:", labels)
# Exact prefix: a loose 'fill' match executed 'Allow manual refill' instead
# (measured 2026-08-29) and left the tank empty with success: true.
filled = False
for g in giz.get("gizmos", []):
    if (g.get("label") or "").startswith("DEBUG: Fill"):
        fr = call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
        filled = bool(fr.get("success"))
        print("executed gizmo:", g.get("label"), "->", filled)
        break
call("rimworld/set_god_mode", enabled=False)
call("rimworld/clear_selection")
need(filled, "tank filled via god-mode fill gizmo")

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
