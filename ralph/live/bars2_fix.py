"""bars2_fix.py <part...> -- pass-2 re-shoots.
  wall2   new geared colonist inside the granite ring (207..213,147..153) at (210,150); climb over (213,150); close shot
          mid-climb; on landing (x>=214) re-draft and hold beside the wall; AFTER shot shows it outside the ring.
  jump8   Longjump into the empty 4 m pit (192..194,148..150) from (193,153); hediffs before/after (reader proven on Bryan).
"""
import sys
from bars2_common import bridge, shot, log, j, dig, depths, spawn, proof, where, hediffs, play, tick, num, PARITY

B = bridge()
parts = sys.argv[1:] or ["wall2", "jump8"]
TABLE = []


def row(line, status, note):
    TABLE.append((line, status, note))
    log("ROW", line, status, note)


B.call("jawa/kill_hostiles")
if "wall2" in parts:
    for old in ("Human43018",):
        B.call("jawa/order_pawn", pawnId=old, x=208, z=152, waitTicks=0, draft=True)
    a = spawn(B, (210, 150))
    ga = B.call("jawa/pawn_gear", pawn=a, action="wear", **{"def": "RM_ClimbingGear"}) or {}
    log("geared wear", ga.get("success"))
    rect = (205, 145, 11, 11)
    # a closed ring gets a roof built by the colony (run 2026-11-07 17:19: NO_CROSSING roofed=True): take it off first
    rr = B.call("jawa/set_roof_batch", ops="None:207,147,7,7") or {}
    log("unroof", j({k: rr.get(k) for k in ("success", "cellsChanged", "cellsFailedVerify", "message")}, 300))
    play(B, 600)
    shot(B, "wall2_before", rect)
    ra = proof(B, PARITY, "ProofLadderParity", "climb:%d,213,150" % num(a))
    t0 = tick(B)
    landed = None
    closed = False
    for k in range(30):
        B.call("rimworld/step_game_ticks", ticks=30, pauseFirst=True)
        w = where(B, [a])
        log("t+%d" % ((tick(B) or 0) - (t0 or 0)), w)
        if w and not closed and w[0][1] >= 212:
            play(B, 300)
            shot(B, "wall2_mid", rect)
            shot(B, "wall2_mid_close", (210, 147, 6, 7), root=4.5)
            closed = True
        if w and w[0][1] >= 214:
            landed = (w[0][1], w[0][2], (tick(B) or 0) - (t0 or 0))
            B.call("rimworld/set_draft", pawnId=a, drafted=True)
            B.call("jawa/order_pawn", pawnId=a, x=214, z=150, waitTicks=0, draft=True)
            break
    play(B, 700)
    shot(B, "wall2_after", rect)
    log("landed", landed, "now", where(B, [a]))
    row("geared_pawn_scales_built_wall", "READ", "climb=%s landed=%s now=%s" % (ra[:90], landed, where(B, [a])))

if "jump8" in parts:
    d = depths(B, 192, 148, 3, 3)
    log("pit depths", d)
    dig(B, [(193, 153)], 0)
    p = spawn(B, (193, 153))
    log("grant", j(B.call("jawa/grant_ability", pawn=p, ability="Longjump"), 200))
    h0 = hediffs(B, p)
    log("hediffs before", h0)
    rect = (190, 146, 6, 9)
    play(B, 400)
    shot(B, "jump8_before", rect)
    r = B.call("jawa/pawn_use_ability", pawn=p, action="cast", ability="Longjump", x=193, z=149, mode="job") or {}
    log("cast", j(r, 400))
    for k in range(6):
        B.call("rimworld/step_game_ticks", ticks=40, pauseFirst=True)
        log("jump t", k, where(B, [p]))
    play(B, 700)
    shot(B, "jump8_after", rect)
    h1 = hediffs(B, p)
    w = where(B, [p])
    dd = depths(B, 190, 146, 6, 9)
    log("hediffs after", h1, "at", w, "depth", dd.get((w[0][1], w[0][2])) if w else None)
    row("jump_into_pit_lands_unhurt(4m)", "READ", "at=%s depth=%s before=%s after=%s" % (
        w, dd.get((w[0][1], w[0][2])) if w else None, h0, h1))

B.call("rimworld/clear_selection")
print("\n=== bars2_fix TABLE ===")
for line, st, note in TABLE:
    print("%-36s %-8s %s" % (line, st, note[:400]))
