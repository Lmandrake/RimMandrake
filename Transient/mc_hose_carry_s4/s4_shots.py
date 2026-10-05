"""s4_shots.py -- stage S4 eyeball proof: a colonist carries a hose round a wall, is drafted (end dropped), resumes, the hose
is wound in, then a laid hose is walled in (cut) and auto-retracts. Screenshots + census reads into this folder.

    python.exe Transient/mc_hose_carry_s4/s4_shots.py        (from the repo root; game up, a colonist on the map)
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src", "RimMandrake", "MessyConduit"))
import validation_hose as VH  # noqa: E402

V = VH.V
VH.SHOTS = HERE
SITE = (78, 58, 36, 20)
REEL = (82, 68)
TARGET = (104, 68)
STAND = (85, 68)
WALL = [(93, z) for z in range(61, 75)]
FRAME = (79, 59, 30, 18)
LOG = []


def hose(B):
    h, c = B.hose(REEL)
    return {"carry": h.get("carry"), "trail": (h.get("trail") or {}).get("count"), "pulled": (h.get("trail") or {}).get("pulled"),
            "far": h.get("far"), "wound": h.get("wound"), "endKind": h.get("endKind"), "draw": h.get("draw"),
            "carrier": (h.get("carrier") or {}).get("pos"), "live": c.get("live")}


RUN = time.strftime("%H%M%S")


def shot(B, name, rect=FRAME):
    # a unique game-side name: the copy helper takes the first file that EXISTS, so a same-named shot from an earlier run
    # in RimWorld's Screenshots folder was copied instead of the new one (cycle 2, 2026-10-05)
    name = name + "_" + RUN
    p = B.shot_rect(name, rect)
    st = hose(B)
    LOG.append({"shot": name, "file": p, "state": st})
    print(name, json.dumps(st)[:300])


def play(B, seconds):
    """Real frames between ticks (the pawn's draw tween only advances on rendered frames)."""
    B.call("rimworld/set_time_speed", speed="Normal")
    time.sleep(seconds)
    B.call("rimworld/set_time_speed", speed="Paused")


def main():
    B = VH.H()
    B.call("rimworld/set_time_speed", speed="Paused")
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % SITE, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % SITE)
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % SITE)
    B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % SITE)
    B.call("jawa/build_batch", ops=V.ops("RM_HoseReel", [REEL]), faction="player", wipeExisting=False)
    B.call("jawa/build_batch", ops=V.ops("Wall", WALL), stuff="Steel", faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    B.ticks(2)
    col = B.hp("colonists")
    pawns = [p for p in col.get("pawns") or [] if not p.get("downed")]
    pid = pawns[0]["id"]
    if pawns[0].get("drafted"):
        B.hp("pawn:%d=undraft" % pid)
    B.hp("pawn:%d=tp:%d,%d" % ((pid,) + STAND))
    shot(B, "s4_00_reel_stored")
    print(B.hp("order:%d,%d=deploy:%d,%d" % (REEL + TARGET)))
    print(B.hp("startjob:%d,%d=forced;%d" % (REEL + (pid,))))
    for _ in range(40):
        if hose(B)["carry"] == "Carrying":
            break
        B.ticks(15)
    for i, n in enumerate((1.0, 1.6, 1.6, 1.6)):
        play(B, n)
        shot(B, "s4_%02d_carry" % (i + 1))
    B.hp("pawn:%d=draft" % pid)
    B.ticks(35)
    shot(B, "s4_05_dropped")
    B.hp("pawn:%d=undraft" % pid)
    B.hp("startjob:%d,%d=work;%d" % (REEL + (pid,)))
    for _ in range(80):
        if hose(B)["carry"] == "Laid":
            break
        B.ticks(15)
    B.ticks(30)
    shot(B, "s4_06_laid")
    B.hp("order:%d,%d=retract" % REEL)
    B.hp("startjob:%d,%d=forced;%d" % (REEL + (pid,)))
    for _ in range(80):
        if hose(B)["carry"] == "Retracting":
            break
        B.ticks(15)
    play(B, 2.5)
    shot(B, "s4_07_winding")
    play(B, 3.3)
    shot(B, "s4_08_winding_more")
    for _ in range(80):
        if hose(B)["carry"] == "Stored":
            break
        B.ticks(30)
    # cut hose: DEV-lay to the target, wall the end in, the corridor check retracts it -> animated ghost
    B.hp("pawn:%d=tp:%d,%d" % (pid, 80, 74))
    print(B.hp("lay:%d,%d,%d,%d" % (REEL + TARGET)))
    B.ticks(5)
    ring = [(TARGET[0] + dx, TARGET[1] + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if (dx, dz) != (0, 0)]
    B.call("jawa/build_batch", ops=V.ops("Wall", ring), stuff="Steel", faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    for _ in range(60):
        if not (hose(B)["carry"] in ("Laid", "Dropped")):
            break
        B.ticks(10)
    play(B, 1.5)
    shot(B, "s4_09_cut_autoretract")
    play(B, 3.0)
    shot(B, "s4_10_cut_autoretract_later")
    with open(os.path.join(HERE, "s4_shots_log.json"), "w") as f:
        json.dump(LOG, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
