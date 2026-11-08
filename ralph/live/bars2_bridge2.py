"""bars2_bridge2.py -- re-shoots for the bridge bars (the 15x14 rect did not fit at play zoom).
  main    AFTER of bars2_bridge's row (timber + steel bridges, plank cover) on a rect that fits (169,127,14,11).
  hung2   fresh row z 116..125: 4 m pit x 172..175 z 118..120 (timber bridge (171,119)-(176,119)), 4 m pit x 172..175
          z 122..124 (rope bridge (171,123)-(176,123)), 2 m pit x 179..181 z 118..120 (plank cover); BEFORE and AFTER.
  under2  the underpass colonist (Human43081) back under the deck at (190,130), settled 1 s, shot + census.
"""
import os
import sys
from bars2_common import bridge, shot, log, dig, square, build, things, proof, where, play, SUSP

B = bridge()
parts = sys.argv[1:] or ["main", "hung2", "under2"]
B.call("jawa/kill_hostiles")
B.call("rimworld/clear_selection")
if "main" in parts:
    play(B, 600)
    shot(B, "bridge_after_built", (169, 127, 14, 11))
if "hung2" in parts:
    dx = next((int(a[3:]) for a in sys.argv[1:] if a.startswith("dx=")), int(os.environ.get("B2_DX", "0")))
    X = 172 + dx   # west pit column; an argument dx=N moves the whole row onto fresh ground
    dig(B, square(X, 118, 4, 3), 8)
    dig(B, square(X, 122, 4, 3), 8)
    dig(B, square(X + 7, 118, 3, 3), 4)
    for c in [(X - 1, 119), (X + 4, 119), (X - 1, 123), (X + 4, 123)]:
        dig(B, [c], 0)
    R = (X - 3, 116, 14, 10)
    B.call("rimworld/clear_selection")
    play(B, 700)
    shot(B, "hung2_before", R)
    a = proof(B, SUSP, "ProofBuild", "%d,119;%d,119;timber;god" % (X - 1, X + 4))
    b = proof(B, SUSP, "ProofBuild", "%d,123;%d,123;rope;god" % (X - 1, X + 4))
    build(B, ";".join("RM_PitCover_PlankLattice:%d,%d" % c for c in square(X + 7, 118, 3, 3)))
    log("covers", len(things(B, "RM_PitCover_PlankLattice", (X + 7, 118, 3, 3))))
    B.call("rimworld/clear_selection")
    play(B, 900)
    shot(B, "hung2_after", R)
    print("TABLE hung2 X=%d timber=%s | rope=%s" % (X, a[:110], b[:110]))
if "under2" in parts:
    pid = "Human43081"
    B.call("jawa/order_pawn", pawnId=pid, x=190, z=130, waitTicks=0, draft=True)
    for k in range(15):
        B.call("rimworld/step_game_ticks", ticks=30, pauseFirst=True)
        w = where(B, [pid])
        if w and (w[0][1], w[0][2]) == (190, 130):
            break
    B.call("rimworld/step_game_ticks", ticks=60, pauseFirst=True)
    play(B, 1000)
    w = where(B, [pid])
    B.call("rimworld/clear_selection")
    shot(B, "under2_pawn_at_190", (184, 126, 11, 9))
    log("under2 at", w, "after", where(B, [pid]))
    print("TABLE under2 at=%s" % (w,))
