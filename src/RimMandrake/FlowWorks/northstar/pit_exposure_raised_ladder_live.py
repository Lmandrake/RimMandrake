#!/usr/bin/env python3
"""pit_exposure_raised_ladder_live.py - live bridge test: a colonist on a dry pit floor is exposed only while it has no way out.

    python.exe src\\RimMandrake\\FlowWorks\\northstar\\pit_exposure_raised_ladder_live.py <colonistName> <ladderX,Z> <outsideX,Z>

The colonist must already stand on an open pit floor whose only way out is the ladder at ladderX,Z (the geyser-pit scene's G1:
Scotty 20,73 21,90 on EVENING_20261113_FLOWWORKS_LIQUID_LOOK). Each read is ONE paused tick: position, RM_NorthstarProofs
.ProofExposure (exposed, marker) and RM_WallReach.ProofReachPair to the outside cell, so the reads cannot disagree.
Ruled: ladder raised -> no reach out AND exposed AND (after 260 ticks) the marker hediff; ladder lowered -> reach out AND not
exposed AND (after 260 ticks) no marker. The ladder is left as found. Exit 0 PASS, 1 FAIL, 2 UNMEASURED.
Live 2026-11-13: before HasNoWayOut a colonist behind a raised ladder read canReach=False and exposed=False (IsTrapped is
captures-only; own colonists are not captured unless superdeepCapturesOwnFaction). MOD fix, this run: PASS.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Utils"))
import validation_core as V  # noqa: E402

NP, PP, WR = "RimMandrake.FlowWorks.RM_NorthstarProofs", "RimMandrake.FlowWorks.RM_PromotionProofs", "RimMandrake.FlowWorks.RM_WallReach"


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    name, lad, out = sys.argv[1:4]
    B = V.Bridge()
    B.stop_on = "clock_discontinuity,modal_stuck,colony_loss,cancel"

    def s(t, m, a):
        r = B.call("jawa/static_call", type=t, method=m, args=a) or {}
        return str(r.get("result") or r.get("error") or r)

    cols = [c for c in (B.call("rimworld/list_colonists") or {}).get("colonists") or [] if c.get("name") == name]
    if not cols:
        print("UNMEASURED: no colonist named %s" % name)
        return 2
    pid = str(cols[0]["thingIdNumber"])
    was = re.search(r"raised=(\w+)", s(PP, "ProofLadder", lad + ",read"))
    if not was or was.group(1) not in ("True", "False"):
        print("UNMEASURED: no ladder at %s" % lad)
        return 2

    def read():
        B.call("rimworld/pause_game")
        e, r = s(NP, "ProofExposure", pid), s(WR, "ProofReachPair", "%s;%s" % (pid, out))
        g = lambda pat, txt: (re.search(pat, txt) or [None, "?"])[1]
        return dict(exposed=g(r"exposed=(\w+)", e), marker=g(r"marker=(\w+)", e), canReach=g(r"canReach=(\w+)", r))

    rows, bad = [], []
    try:
        for op, want in (("raise", dict(exposed="True", marker="True", canReach="False")),
                         ("lower", dict(exposed="False", marker="False", canReach="True"))):
            s(PP, "ProofLadder", "%s,%s" % (lad, op))
            s(WR, "ProofReachForce", "-")
            now = read()
            B.ticks(260)
            later = read()
            row = dict(op=op, now=now, after260=later)
            rows.append(row)
            print(row)
            for k in ("exposed", "canReach"):
                if now[k] != want[k]:
                    bad.append("%s: %s=%s at once, ruled %s" % (op, k, now[k], want[k]))
            for k in want:
                if later[k] != want[k]:
                    bad.append("%s: %s=%s after 260 ticks, ruled %s" % (op, k, later[k], want[k]))
    finally:
        s(PP, "ProofLadder", "%s,%s" % (lad, "raise" if was.group(1) == "True" else "lower"))
        B.call("rimworld/pause_game")
    if any("?" in r["now"].values() or "?" in r["after260"].values() for r in rows):
        print("UNMEASURED: a read came back without its field: %r" % rows)
        return 2
    print("FAIL: " + "; ".join(bad) if bad else "PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
