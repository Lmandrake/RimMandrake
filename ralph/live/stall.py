"""stall.py -- load the stalled-raid save and read why the raiders at the pit lip Wait forever.

  python.exe ralph/live/stall.py [save]     (default fw_story1_stall)

For each raider: position, job, duty; then ProofReachPair to each colonist inside the compound (canReach vs found)
and ProofReach (Stale / Residual counters) before and after 600 ticks of play.
"""
import json
import re
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fwb  # noqa: E402
import story1  # noqa: E402

V = fwb.V
WR = "RimMandrake.FlowWorks.RM_WallReach"


def sc(B, method, args=""):
    r = B.call("jawa/static_call", type=WR, method=method, args=args) or {}
    return r.get("result") or r.get("returnValue") or r


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    name = sys.argv[1] if len(sys.argv) > 1 else "fw_story1_stall"
    B = fwb.FW()
    ld = B.call("rimworld/load_game", saveName=name) or {}
    print("LOAD", str(ld)[:200])
    ok, t = V._wait_playing(B)
    print("PLAYING", ok, t)
    print("REACH0", sc(B, "ProofReach"))
    print("RESET", sc(B, "ProofReachReset"))
    for rnd in range(2):
        raiders = [p for p in story1.pawns(B, "hostile") if not p.get("dead")]
        cols = [p for p in story1.pawns(B, "player") if not p.get("dead")]
        for p in raiders:
            print("RAIDER", story1.brief(p), "duty=", p.get("duty") or p.get("dutyDef"))
            for c in cols[:3]:
                pid = p.get("thingIDNumber") or int(re.sub(r"\D", "", str(p.get("id")))[-9:] or 0)
                arg = "%s;%d,%d" % (pid, c.get("x"), c.get("z"))
                print("   to", c.get("name"), c.get("x"), c.get("z"), sc(B, "ProofReachPair", arg))
                print("   to", c.get("name"), "touch", sc(B, "ProofReachPair", arg + ";touch"))
        print("REACH", rnd, sc(B, "ProofReach"))
        if rnd == 0:
            B.call("rimworld/play_for", durationMs=10000, speed="Superfast")
    B.call("rimworld/pause_game")


if __name__ == "__main__":
    main()
