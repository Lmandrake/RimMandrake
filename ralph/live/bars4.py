"""bars4.py -- the pit's built half under the current depth look, on the fw3_bars map (game A). Shots b2_<name>_r<zoom>_*.

  python.exe ralph/live/bars4.py <X0> <Z0> [parts...]     parts: sod ladders spikes bridge (default all)

  sod      a 9x7 grass field (Plant_Grass, full growth: a temperate meadow) at (X0, Z0); BEFORE; then a 3x2 pit 2 m at its
           centre, spiked, woven-scrap covers; AFTER at root 20, and the seam at root 11 (the closest a player can zoom).
  ladders  a 5x5 pit 2 m at (X0+12, Z0): RM_Ladder on each wall's middle square, N and S lowered, E and W raised; a 3x3 2 m
           pit (X0+19, Z0) and a 3x3 4 m pit (X0+19, Z0+4), a portable ladder against each north wall (reaches / too short).
  spikes   a 3x2 pit 2 m at (X0, Z0+9), spiked, open.
  bridge   a 4x3 pit 4 m at (X0+12, Z0+8), a timber suspension bridge across its middle row, a drafted colonist walking
           under it from the south row to the north row (BEFORE and AFTER).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bars2_common import bridge, shot, log, dig, square, build, things, proof, play, where, PROMO, SUSP  # noqa: E402

B = bridge()
X0, Z0 = int(sys.argv[1]), int(sys.argv[2])
parts = sys.argv[3:] or ["sod", "ladders", "spikes", "bridge"]
T = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
for f, v in (("pitLookMode", os.environ.get("FW_LOOK", "1")), ("pitSinkPerLevel", "0.3")):
    r = B.call("jawa/mod_settings_field", typeName=T, action="set", field=f, value=v) or {}
    log(f, r.get("valueBefore"), "->", r.get("valueAfter"))
proof(B, "RimMandrake.FlowWorks.SectionLayer_RMExcavationWalls", "RedrawAll", "")
B.call("jawa/set_fog", action="unfog", rect="%d,%d,32,22" % (X0 - 3, Z0 - 3))
B.call("rimworld/clear_selection")

if "sod" in parts:
    field = (X0, Z0, 9, 7)
    pit = square(X0 + 3, Z0 + 2, 3, 2)
    B.call("jawa/set_plants", ops="Plant_Grass:%d,%d,%d,%d" % field, growth=1.0, density=1.0, clearFirst=True)
    play(B, 600)
    shot(B, "sod_before", (X0 - 1, Z0 - 1, 11, 9), root=20)
    dig(B, pit, 4)
    build(B, ";".join("RM_Spikes:%d,%d" % c for c in pit), stuff="WoodLog")
    build(B, ";".join("RM_PitCover_WovenScrap:%d,%d" % c for c in pit), stuff="WoodLog")
    log("covers", len(things(B, "RM_PitCover_WovenScrap", (X0 + 3, Z0 + 2, 3, 2))))
    play(B, 900)
    shot(B, "sod_after", (X0 - 1, Z0 - 1, 11, 9), root=20)
    shot(B, "sod_seam", (X0 + 1, Z0 + 1, 7, 4), root=11)

if "ladders" in parts:
    px, pz = X0 + 12, Z0
    dig(B, square(px, pz, 5, 5), 4)
    walls = {0: (px + 2, pz + 4), 1: (px + 4, pz + 2), 2: (px + 2, pz), 3: (px, pz + 2)}
    for r, c in walls.items():
        build(B, "RM_Ladder:%d,%d,%d" % (c[0], c[1], r), stuff="WoodLog")
    for r, c in walls.items():
        proof(B, PROMO, "ProofLadder", "%d,%d,%s" % (c[0], c[1], "lower" if r in (0, 2) else "raise"))
    dig(B, square(X0 + 19, Z0, 3, 3), 4)
    dig(B, square(X0 + 19, Z0 + 4, 3, 3), 8)
    build(B, "RM_LadderPortable:%d,%d,0" % (X0 + 20, Z0 + 2), stuff="WoodLog")
    build(B, "RM_LadderPortable:%d,%d,0" % (X0 + 20, Z0 + 6), stuff="WoodLog")
    play(B, 900)
    shot(B, "ladders4", (px - 1, pz - 1, 7, 7))
    shot(B, "portable", (X0 + 18, Z0 - 1, 5, 9))

if "spikes" in parts:
    dig(B, square(X0, Z0 + 9, 3, 2), 4)
    build(B, ";".join("RM_Spikes:%d,%d" % c for c in square(X0, Z0 + 9, 3, 2)), stuff="WoodLog")
    play(B, 600)
    shot(B, "spikes_open", (X0 - 2, Z0 + 7, 7, 6))

if "bridge" in parts:
    bx, bz = X0 + 12, Z0 + 8
    dig(B, square(bx, bz, 4, 3), 8)
    for c in [(bx - 1, bz + 1), (bx + 4, bz + 1)]:
        dig(B, [c], 0)
    a = proof(B, SUSP, "ProofBuild", "%d,%d;%d,%d;timber;god" % (bx - 1, bz + 1, bx + 4, bz + 1))
    r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=bx + 1, z=bz, faction="player", count=1) or {}
    pid = next((p.get("id") for p in r.get("pawns") or [] if p.get("id")), None)
    B.call("jawa/order_pawn", pawnId=pid, x=bx + 1, z=bz, draft=True, waitTicks=30)
    play(B, 800)
    shot(B, "under_before", (bx - 2, bz - 1, 8, 5))
    B.call("jawa/order_pawn", pawnId=pid, x=bx + 2, z=bz + 1, draft=True, waitTicks=0)
    for k in range(12):
        play(B, 250)
        w = where(B, [pid])
        if w and (w[0][1], w[0][2]) == (bx + 2, bz + 1):
            break
    shot(B, "under_mid", (bx - 2, bz - 1, 8, 5))
    B.call("jawa/order_pawn", pawnId=pid, x=bx + 2, z=bz + 2, draft=True, waitTicks=0)
    play(B, 2500)
    shot(B, "under_after", (bx - 2, bz - 1, 8, 5))
    log("under walker", where(B, [pid]), "bridge", a[:200])
