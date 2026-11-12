"""EXCAVATION_WALL_ART_1 live scene: what a player sees of the pit wall faces, spikes and ladder, on one quicktest map.

    python.exe wall_art_scene.py <repo_win_path> <out_win_dir> [stage|dig|shots|things|all|save:<name>]

Row of 3x3 pits from (92,112), 2 dry squares between: D1 D2 D3 D4 dry (flowworks_excavation_drive, the engine's own dig),
D4 with 1 m of water (fill 2 notches: the face shortens, the water covers its foot), D4 spiked, D4 laddered (lowered on the
north wall, a second raised on the south wall by ProofLadder), D3 where spikes are TRIED (the Architect must refuse: spikes
need a 2 m drop), and a 3x3 given the player's own "Dig to 4 m" order for the colonists (each colonist gets a shovel: digging
without one is refused by design, "Needs a shovel"). Spikes and ladders go through rimworld/apply_architect_designator, so
the placeworkers decide, as for a player (god mode on only so the blueprint completes at once).
Shots: the whole row at an ordinary zoom (fit to the row) and each pit at the closest zoom, as PNGs + scene_<step>_<ts>.json.
Findings 2026-11-12 (CLAUDE_ARCHMAGI_FWLIVE): the centre square of a 3x3 D4 pit refuses spikes (no wall over it), so a
spiked pit shows a ring of stakes; a long `dig` wait on an unfed quicktest starves the colony (feed or keep it short).
"""
import json
import os
import shutil
import sys
import time

REPO = sys.argv[1]  # the clone, as a Windows path (python.exe)
OUT = sys.argv[2]
STEP = sys.argv[3] if len(sys.argv) > 3 else "all"
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "northstar"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import validation_core as V  # noqa: E402
from water_scenes_walk import fit_root_size  # noqa: E402

B = V.Bridge()
LOG = []
OX, OZ = 92, 112
PITS = {  # name -> (dx, notches, fill)
    "D1": (0, 1, 0), "D2": (5, 2, 0), "D3": (10, 3, 0), "D4": (15, 4, 0),
    "D4_WATER": (20, 4, 2), "D4_SPIKES": (25, 4, 0), "D4_LADDER": (30, 4, 0), "D3_SPIKES_TRY": (35, 3, 0),
}
DUG_BY_COLONISTS = (OX + 42, OZ)   # 3x3, "Dig to 4 m" designator, colonists dig it
DESIG = "architect-designator:orders:highlight-designator-tutortagnotset-14"
SPIKES = "architect-designator:structure:build-rm-spikes"
LADDER = "architect-designator:structure:build-rm-ladder"


def log(k, v):
    LOG.append({k: v})
    print(k, json.dumps(v)[:400])
    sys.stdout.flush()


def call(tool, **kw):
    try:
        return B.call(tool, **kw) or {}
    except Exception as ex:  # noqa: BLE001
        return {"success": False, "error": str(ex)}


def look(x, z):
    r = call("jawa/static_call", type="RimMandrake.FlowWorks.RM_WaterLookProofs", method="ProofWaterLook", args="%d,%d" % (x, z))
    return str(r.get("result") or r.get("error") or r)


def shot(name, rect, root=None):
    x, z, w, h = rect
    call("jawa/clear_ui", all=True)
    call("rimworld/jump_camera_to_cell", x=int(x + w // 2), z=int(z + h // 2))
    call("rimworld/set_camera_zoom", rootSize=root or fit_root_size(rect))
    time.sleep(1.5)
    r = call("jawa/take_screenshot", fileName="ewa_%s_%d" % (name, int(time.time())))
    src = r.get("filePath")
    for _ in range(12):
        if src and os.path.exists(src):
            break
        time.sleep(0.5)
    dst = os.path.join(OUT, name + ".png")
    shutil.copyfile(src, dst)
    log("shot", {"name": name, "rect": rect, "rootSize": root or fit_root_size(rect), "file": dst})


def stage():
    # SITE (2026-11-12 run 2): a quicktest lake beside the row ran into the dug pits and drowned D2..D4. So the row and a
    # 12-cell halo are reset (dug cells and water bodies released) and painted Soil before anything is dug.
    site = (OX - 15, OZ - 16, 76, 36)
    r = call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect", args="%d;%d;%d;%d" % site)
    log("reset", str(r.get("result") or r)[:200])
    call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % site)
    call("jawa/kill_hostiles")
    call("jawa/weather_set", weather="Clear", lockWeather=True)
    for name, (dx, n, fill) in PITS.items():
        for i in range(3):
            for j in range(3):
                call("jawa/flowworks_excavation_drive", x=OX + dx + i, z=OZ + j, deepenLevels=n, setFill=-1, fillInLevels=0)
        if fill:
            for i in range(3):
                for j in range(3):
                    call("jawa/flowworks_excavation_drive", x=OX + dx + i, z=OZ + j, deepenLevels=0, setFill=fill, fillInLevels=0)
        log("pit", {"name": name, "look_centre": look(OX + dx + 1, OZ + 1)})
    # the player's own dig order on a fresh 3x3
    for c in (call("rimworld/list_colonists").get("colonists") or []):
        call("jawa/pawn_gear", pawn=c.get("name"), action="inventory", **{"def": "RM_Shovel", "stuff": "WoodLog", "count": 1})
    r = call("rimworld/apply_architect_designator", designatorId=DESIG, x=DUG_BY_COLONISTS[0], z=DUG_BY_COLONISTS[1], width=3, height=3)
    log("dig_to_4m_designate", {k: r.get(k) for k in ("success", "message", "appliedCells", "rejectedCells") if k in r})
    call("rimworld/set_god_mode", enabled=True)
    for name in ("D4_SPIKES", "D3_SPIKES_TRY"):
        dx = PITS[name][0]
        r = call("rimworld/apply_architect_designator", designatorId=SPIKES, x=OX + dx, z=OZ, width=3, height=3)
        log("spikes_designate_" + name, {k: r.get(k) for k in r if k not in ("state", "operation")})
    dx = PITS["D4_LADDER"][0]
    # lowered ladder on the north wall (middle square of the top row), one on the south wall to raise
    for (cx, cz, rot) in ((OX + dx + 1, OZ + 2, 0), (OX + dx + 1, OZ, 2)):
        r = call("rimworld/apply_architect_designator", designatorId=LADDER, x=cx, z=cz, rotation=rot)
        log("ladder_designate", {"cell": [cx, cz], "rot": rot, **{k: r.get(k) for k in r if k not in ("state", "operation")}})
    r = call("jawa/static_call", type="RimMandrake.FlowWorks.RM_PromotionProofs", method="ProofLadder", args="%d,%d,raise" % (OX + dx + 1, OZ))
    log("ladder_raise_south", str(r.get("result") or r)[:200])
    call("rimworld/set_god_mode", enabled=False)
    # a colonist standing in the laddered pit, for scale
    r = call("jawa/spawn_pawn", kindDef="Colonist", x=OX + dx + 1, z=OZ + 1, faction="player")
    log("colonist_in_ladder_pit", {k: r.get(k) for k in ("success", "message") if k in r})


def things():
    for d in ("RM_Spikes", "RM_Ladder"):
        r = call("jawa/list_things", defName=d, rect="%d,%d,%d,%d" % (OX - 2, OZ - 2, 50, 8))
        log("things_" + d, {k: r.get(k) for k in r if k not in ("state", "operation")})


def dig_wait(seconds):
    call("rimworld/set_time_speed", speed="Superfast")
    t0 = time.time()
    while time.time() - t0 < seconds:
        time.sleep(15)
        looks = [look(DUG_BY_COLONISTS[0] + i, DUG_BY_COLONISTS[1] + j) for i in range(3) for j in range(3)]
        log("dig_progress", {"t": int(time.time() - t0), "hollow": [l.split("hollow=")[1][:1] if "hollow=" in l else "?" for l in looks]})
        if all("hollow=4" in l or "hollow 4" in l for l in looks):
            break
    call("rimworld/pause_game")


def midday():
    """Step the governed clock to 10:00-14:00 (ticksAbs mod a day; longitude ignored: judge the light in the picture)."""
    hour = None
    for _ in range(14):
        t = call("jawa/time_clock")
        if t.get("ticksAbs") is None:
            break
        hour = (t["ticksAbs"] % 60000) / 2500.0
        if 10 <= hour <= 14:
            break
        B.ticks(2000)
    log("hour", hour)


def shots():
    midday()
    row = (OX - 2, OZ - 2, 49, 7)
    shot("row_ordinary_zoom", row)
    for name, (dx, n, fill) in PITS.items():
        shot("close_" + name, (OX + dx - 1, OZ - 1, 5, 5), root=11.0)
    shot("close_DUG_BY_COLONISTS", (DUG_BY_COLONISTS[0] - 1, DUG_BY_COLONISTS[1] - 1, 5, 5), root=11.0)


if __name__ == "__main__":
    if STEP in ("all", "stage"):
        stage()
        things()
    if STEP in ("all", "dig"):
        dig_wait(int(os.environ.get("EWA_DIG_S", "240")))
    if STEP in ("all", "shots"):
        shots()
    if STEP == "things":
        things()
    if STEP.startswith("save:"):   # save:<name> -> a keeper savegame of this scene for the owner's look (never overwrites)
        from modcheck.reviewmap import save_keeper
        log("save", save_keeper(B, STEP.split(":", 1)[1]))
    with open(os.path.join(OUT, "scene_%s_%s.json" % (STEP, time.strftime("%Y%m%dT%H%M%S"))), "w") as f:
        json.dump(LOG, f, indent=1)
