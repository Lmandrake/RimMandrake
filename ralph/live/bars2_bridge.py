"""bars2_bridge.py <part...> -- pass-2 bridge bars on the story map, row z = 126..140, x = 169..196.
  hung     4 m (D8) pits x 172..175: z 129..131 under a timber bridge (171,130)-(176,130), z 135..137 under a steel bridge
           (171,136)-(176,136); BEFORE (open pits) and AFTER (bridges) on the same rect.
  cover    2 m (D4) pit x 179..181, z 129..131 under RM_PitCover_PlankLattice on all 9 squares, in the same frame as the
           timber bridge (before = open, after = covered).
  under    4 m trench x 186..193, z 129..131; steel bridge (189,128)-(190,132) across it; a colonist on the trench floor
           at (186,130) walks to (189,130) (under the deck: shot), then on to (193,130) (shot).
"""
import sys
from bars2_common import bridge, shot, log, j, dig, square, depths, spawn, build, things, proof, where, play, tick, SUSP

B = bridge()
parts = sys.argv[1:] or ["hung", "cover", "under"]
TABLE = []


def row(line, status, note):
    TABLE.append((line, status, note))
    log("ROW", line, status, note)


def walk(pid, x, z, steps=20):
    B.call("jawa/order_pawn", pawnId=pid, x=x, z=z, waitTicks=0, draft=True)
    w = None
    for k in range(steps):
        B.call("rimworld/step_game_ticks", ticks=30, pauseFirst=True)
        w = where(B, [pid])
        if w and (w[0][1], w[0][2]) == (x, z):
            break
    log("walk", pid, "->", (x, z), "at", w)
    return w


B.call("jawa/kill_hostiles")
cen = B.call("jawa/pawn_census", faction="player") or {}
for p in cen.get("pawns") or []:
    if p.get("x") is not None and 168 <= p.get("x") <= 197 and 125 <= p.get("z") <= 141:
        log("moving", p.get("id"), "out of the row", (p.get("x"), p.get("z")))
        B.call("jawa/order_pawn", pawnId=p.get("id"), x=200, z=143, waitTicks=0, draft=True)
MAIN = (169, 126, 15, 14)
if "hung" in parts or "cover" in parts:
    dig(B, square(172, 129, 4, 3), 8)
    dig(B, square(172, 135, 4, 3), 8)
    dig(B, square(179, 129, 3, 3), 4)
    for c in [(171, 130), (176, 130), (171, 136), (176, 136)]:
        dig(B, [c], 0)
    B.call("rimworld/clear_selection")
    play(B, 700)
    log("depths", sorted(set(depths(B, 169, 126, 15, 14).values())))
    shot(B, "bridge_before_open", MAIN)
if "hung" in parts:
    a = proof(B, SUSP, "ProofBuild", "171,130;176,130;timber;god")
    b = proof(B, SUSP, "ProofBuild", "171,136;176,136;steel;god")
if "cover" in parts:
    build(B, ";".join("RM_PitCover_PlankLattice:%d,%d" % c for c in square(179, 129, 3, 3)))
    log("covers", len(things(B, "RM_PitCover_PlankLattice", (179, 129, 3, 3))))
if "hung" in parts or "cover" in parts:
    B.call("rimworld/clear_selection")
    play(B, 900)
    shot(B, "bridge_after_built", MAIN)
    shot(B, "bridge_close_timber", (171, 128, 6, 5), root=4.5)
if "hung" in parts:
    row("suspension_bridge_reads_hung", "STAGED", "timber=%s | steel=%s" % (a[:120], b[:120]))
if "cover" in parts:
    row("pit_cover_unlike_bridge", "STAGED", "covers=%d" % len(things(B, "RM_PitCover_PlankLattice", (179, 129, 3, 3))))

if "under" in parts:
    dig(B, square(186, 129, 8, 3), 8)
    for c in [(189, 128), (190, 128), (189, 132), (190, 132)]:
        dig(B, [c], 0)
    p = spawn(B, (186, 130))
    rect = (184, 126, 12, 8)
    play(B, 600)
    shot(B, "under_before", rect)
    r = proof(B, SUSP, "ProofBuild", "189,128;190,132;steel;god")
    play(B, 600)
    shot(B, "under_bridge_pawn_west", rect)
    w1 = walk(p, 189, 130)
    play(B, 250)
    shot(B, "under_pawn_under_deck", rect)
    shot(B, "under_close", (187, 127, 5, 7), root=4.5)
    w2 = walk(p, 193, 130, steps=25)
    play(B, 600)
    shot(B, "under_after_east", rect)
    d = depths(B, 184, 126, 12, 8)
    row("pawn_walks_under_deck", "READ", "build=%s mid=%s end=%s depth_end=%s" % (
        r[:100], w1, w2, d.get((w2[0][1], w2[0][2])) if w2 else None))

B.call("rimworld/clear_selection")
print("\n=== bars2_bridge TABLE ===")
for line, st, note in TABLE:
    print("%-36s %-8s %s" % (line, st, note[:400]))
