"""ladders5.py -- pass 4: the ladder rig printed down its wall (LADDER_RAILS_DRAWN_ON_THE_FACE), the climbing gear worn, on
the current quick-test map east of the colonists. Shots l5_<name>_r<zoom>_<HHMMSS> (bars2_common's ZOOMS: root 11 and 20).

  python.exe ralph/live/ladders5.py [parts...]      parts: rig steel portable gear (default all)

  rig       a 5x5 pit 2 m deep, a wooden RM_Ladder on the middle of each wall and a colonist on the floor: all lowered (shot),
            then all raised (shot): the same ladders, so ladder_state_legible compares like with like.
  steel     a 5x4 pit 4 m deep, RM_LadderSteel on each wall, north and east lowered, south and west raised.
  portable  a 3x3 pit 2 m and a 3x3 pit 4 m: a portable ladder against the north wall and the east wall of each.
  gear      a colonist wearing RM_ClimbingGear facing south, east, north and west, and the kit on the ground beside him.
  bridge    a 4x3 pit 4 m deep, a timber suspension bridge over its middle row, a colonist walking under it from the south
            row to the north row (BEFORE, MID, AFTER; pawn_walks_under_deck), and the bridge alone (suspension_bridge_reads_hung).
  dig       a colonist with a steel shovel digs one designated soil square (digging_takes_hours): game ticks to the first notch.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bars2_common as C  # noqa: E402
from bars2_common import bridge, log, dig, square, build, proof, play, PROMO  # noqa: E402

C.PREFIX = "l5"
B = bridge()
parts = sys.argv[1:] or ["rig", "steel", "portable", "gear", "bridge"]
T = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
for f, v in (("pitLookMode", "1"), ("pitSinkPerLevel", "0.3")):
    r = B.call("jawa/mod_settings_field", typeName=T, action="set", field=f, value=v) or {}
    log(f, r.get("valueBefore"), "->", r.get("valueAfter"))
cen = B.call("jawa/pawn_census", faction="player") or {}
cols = [p for p in cen.get("pawns") or [] if p.get("isColonist")]
X0 = sum(p["x"] for p in cols) // len(cols) + 10
Z0 = sum(p["z"] for p in cols) // len(cols) - 8
log("origin", X0, Z0)
B.call("jawa/set_fog", action="unfog", rect="%d,%d,40,30" % (X0 - 3, Z0 - 3))
B.call("jawa/clear_area", rect="%d,%d,36,26" % (X0 - 2, Z0 - 2), dryRun=False)
B.call("rimworld/clear_selection")


def shot(name, rect, root=None):
    # bars2_common names shots b2_*; this pass's are l5_*
    return C.shot(B, "l5_" + name, rect, root=root)


def ladder(c, r, state):
    return proof(B, PROMO, "ProofLadder", "%d,%d,%s" % (c[0], c[1], state))


if "rig" in parts:
    px, pz = X0, Z0
    dig(B, square(px, pz, 5, 5), 4)
    walls = {0: (px + 2, pz + 4), 1: (px + 4, pz + 2), 2: (px + 2, pz), 3: (px, pz + 2)}
    for r, c in walls.items():
        build(B, "RM_Ladder:%d,%d,%d" % (c[0], c[1], r), stuff="WoodLog")
    pid = C.spawn(B, (px + 1, pz + 1))
    for r, c in walls.items():
        ladder(c, r, "lower")
    proof(B, "RimMandrake.FlowWorks.SectionLayer_RMExcavationWalls", "RedrawAll", "")
    play(B, 600)
    shot("rig_lowered", (px - 2, pz - 2, 9, 9))
    for r, c in walls.items():
        ladder(c, r, "raise")
    play(B, 400)
    shot("rig_raised", (px - 2, pz - 2, 9, 9))

if "steel" in parts:
    px, pz = X0 + 10, Z0
    dig(B, square(px, pz, 5, 4), 8)
    walls = {0: (px + 2, pz + 3), 1: (px + 4, pz + 1), 2: (px + 2, pz), 3: (px, pz + 2)}
    for r, c in walls.items():
        build(B, "RM_LadderSteel:%d,%d,%d" % (c[0], c[1], r), stuff="Steel")
    for r, c in walls.items():
        ladder(c, r, "lower" if r in (0, 1) else "raise")
    play(B, 600)
    shot("steel_mixed", (px - 2, pz - 2, 9, 8))

if "portable" in parts:
    for k, (d, label) in enumerate(((4, "2m"), (8, "4m"))):
        px, pz = X0 + 20, Z0 + k * 6
        dig(B, square(px, pz, 3, 3), d)
        build(B, "RM_LadderPortable:%d,%d,0" % (px + 1, pz + 2), stuff="WoodLog")
        build(B, "RM_LadderPortable:%d,%d,1" % (px + 2, pz + 1), stuff="WoodLog")
    play(B, 600)
    shot("portable", (X0 + 18, Z0 - 2, 7, 13))

if "gear" in parts:
    gx, gz = X0 + 27, Z0 + 2
    B.call("jawa/spawn_batch", ops="RM_ClimbingGear:%d,%d" % (gx, gz))
    ids = []
    for k in range(4):
        pid = C.spawn(B, (gx + 2 + k * 2, gz))
        g = B.call("jawa/pawn_gear", pawn=pid, action="wear", **{"def": "RM_ClimbingGear"}) or {}
        log("wear", pid, str(g)[:200])
        ids.append(pid)
    play(B, 300)
    for pid, rot in zip(ids, ("South", "East", "North", "West")):
        r = B.call("jawa/set_pawn_rotation", pawnId=pid, dir=rot.lower(), lockRotation=True) or {}
        log("rot", pid, rot, str(r)[:120])
    time.sleep(1)
    shot("gear", (gx - 1, gz - 1, 10, 3), root=8)
    shot("gear_play", (gx - 1, gz - 2, 10, 5))
if "bridge" in parts:
    bx, bz = X0 + 2, Z0 + 9
    dig(B, square(bx, bz, 4, 3), 8)
    for c in [(bx - 1, bz + 1), (bx + 4, bz + 1)]:
        dig(B, [c], 0)
    a = proof(B, C.SUSP, "ProofBuild", "%d,%d;%d,%d;timber;god" % (bx - 1, bz + 1, bx + 4, bz + 1))
    play(B, 300)
    shot("bridge_empty", (bx - 3, bz - 2, 10, 7))
    pid = C.spawn(B, (bx + 1, bz))
    play(B, 400)
    shot("under_before", (bx - 3, bz - 2, 10, 7))
    B.call("jawa/order_pawn", pawnId=pid, x=bx + 1, z=bz + 2, draft=True, waitTicks=0)
    seen_mid = False
    for k in range(16):
        play(B, 200)
        w = C.where(B, [pid])
        log("walker", w)
        if w and w[0][2] == bz + 1 and not seen_mid:
            shot("under_mid", (bx - 3, bz - 2, 10, 7))
            seen_mid = True
        if w and w[0][2] == bz + 2:
            break
    play(B, 300)
    shot("under_after", (bx - 3, bz - 2, 10, 7))
if "dig" in parts:
    c = (X0 + 12, Z0 + 10)
    B.call("jawa/set_terrain", terrainDef="Soil", x=c[0], z=c[1])
    p = C.spawn(B, (c[0] + 1, c[1]), draft=False)
    g = B.call("jawa/pawn_gear", pawn=p, action="inventory", **{"def": "RM_Shovel", "stuff": "Steel"}) or {}
    log("shovel", str(g)[:200])
    B.call("jawa/designate_batch", action="add", designation="RM_DigCanal", rect="%d,%d,1,1" % c)
    d0 = C.depths(B, c[0], c[1], 1, 1).get(c, 0)
    t0 = C.tick(B)
    od = B.call("jawa/ordered_job", pawnId=p, jobDef="RM_DigCanalJob", targetAX=c[0], targetAZ=c[1], waitTicks=0) or {}
    log("order", str(od)[:200], "d0", d0, "t0", t0)
    cut, jobs = None, []
    for k in range(80):
        B.call("rimworld/step_game_ticks", ticks=250, pauseFirst=True)
        dt = (C.tick(B) or 0) - (t0 or 0)
        d = C.depths(B, c[0], c[1], 1, 1).get(c, 0)
        cen = (B.call("jawa/pawn_census", ids=p) or {}).get("pawns") or [{}]
        jb = cen[0].get("job") or cen[0].get("curJob") or cen[0].get("jobDef")
        if not jobs or jobs[-1][1] != jb:
            jobs.append((dt, jb))
        if k == 6:
            play(B, 300)
            shot("dig_mid", (c[0] - 3, c[1] - 2, 7, 5))
        if d != d0:
            cut = dt
            break
    log("RESULT dig: first notch after %s ticks (%.2f in-game h) d %s->%s jobs=%s" % (cut, (cut or 0) / 2500.0, d0,
        C.depths(B, c[0], c[1], 1, 1).get(c, 0), jobs[:8]))
log("done")
