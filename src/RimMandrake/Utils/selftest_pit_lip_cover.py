#!/usr/bin/env python3
# selftest-timeout: 900   (the FlowWorks SelfTest stage+build alone took 487 s from an ext4 clone, 2026-11-02)
"""PIT_LIP_OCCLUDER_FIX_GHOSTED_HALVES: the near-lip pit cover on br1f's s8 frame, offline.

1. The live proof's pure verdicts (FlowWorks/northstar/proof_pit_lip_cover.py): each passes a good frame record and fails
   a planted bad one (a piece over the ground muffalo, a piece outside its pawn's rect, a missing side piece, a covered
   occupant window), and answers UNMEASURED when the record cannot see (no pieces, the pawn absent).
2. The C# cases PitLip_* and PitSide_* of FlowWorks' SelfTest (selftest_flowworks_stock.py --only): the shipped decision math
   on s8's real pit (outside muffalo never covered, the west overhang is the in-pit muffalo under the side bank, the
   occupant window opens past half and stays shut at the clamp, the frame record is wired).

    python3 selftest_pit_lip_cover.py [--no-dotnet]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "northstar"))
import proof_pit_lip_cover as P  # noqa: E402

GOOD = """frame 10 now 11 enabled 1 cutSetting 1 clamp 0 cutWidth 1
sunk Muffalo1 4 131 134 112.5 115.5 0
sunk Human2 4 134.9 136.1 112.55 114.05 1
piece Muffalo1 N 131 132 112.5 113 
piece Muffalo1 N 131 132 113 114
piece Muffalo1 S 131 132 114 114.82
piece Muffalo1 N 132 134 112.5 114
piece Human2 N 134.9 135 112.55 114
piece Human2 X 136 136.1 112.55 114
pawn Muffalo1 4 131 134 112.5 115.5
pawn Human2 4 134.9 136.1 112.55 114.05
pawn Muffalo3 0 136 139 112 115
"""


def check(ok, msg):
    if not ok:
        raise SystemExit("FAIL " + msg)
    print("ok   " + msg)


def pure():
    rep = P.parse_report(GOOD)
    check(len(rep["sunk"]) == 2 and len(rep["pawns"]) == 3 and len(rep["pieces"]) == 6, "the record parses (6 pieces)")
    check(rep["head"].get("clamp") == "0", "the header parses")
    st, det = P.v_no_ghost(rep, "Muffalo3")
    check(st == "PASS", "A1 good frame passes: %s" % det)
    bad = P.parse_report(GOOD.replace("piece Human2 X", "piece Human2 N"))
    check(P.v_no_ghost(bad, "Muffalo3")[0] == "FAIL", "can-fail A1: a drawn piece over the ground muffalo")
    check(P.v_no_ghost(rep, "Nobody9")[0] == "UNMEASURED", "A1 cannot see an absent pawn")
    blind = P.parse_report("\n".join(x for x in GOOD.splitlines() if not x.startswith("piece")))
    check(P.v_no_ghost(blind, "Muffalo3")[0] == "UNMEASURED", "A1 with no piece drawn is UNMEASURED, never PASS")
    st, det = P.v_cover_with_pit(rep, "Muffalo1", 131, 114)
    check(st == "PASS", "A2 good frame passes: %s" % det)
    check(P.v_cover_with_pit(P.parse_report(GOOD.replace("piece Muffalo1 S", "piece Muffalo1 N 131 132 113 113.5 \n#")), "Muffalo1", 131, 114)[0]
          == "FAIL", "can-fail A2: no side piece above the lip in the overhang column (the seam)")
    check(P.v_cover_with_pit(P.parse_report(GOOD.replace("piece Muffalo1 N 132 134", "piece Muffalo1 N 132 135.5")), "Muffalo1", 131, 114)[0]
          == "FAIL", "can-fail A2: a piece past its pawn's own rect")
    st, det = P.v_window(rep, "Human2", clamp_on=False)
    check(st == "PASS" and det["hiddenShare"] > 0.9, "A3 clamp off: window open and bare: %s" % det)
    check(P.v_window(rep, "Human2", clamp_on=True)[0] == "FAIL", "can-fail A3: a cut with the clamp on")
    covered = P.parse_report(GOOD + "piece Human2 N 135 136 112.55 114\n")
    check(P.v_window(covered, "Human2", clamp_on=False)[0] == "FAIL", "can-fail A3: a near piece inside the window")
    shut = P.parse_report(GOOD.replace("112.55 114.05 1", "112.55 114.05 0"))
    check(P.v_window(shut, "Human2", clamp_on=True)[0] == "PASS", "A3 clamp on: shut passes")
    check(P.v_window(shut, "Human2", clamp_on=False)[0] == "FAIL", "can-fail A3: clamp off with the window shut")


def main(argv):
    pure()
    if "--no-dotnet" in argv:
        return 0
    r = subprocess.run([sys.executable, os.path.join(HERE, "selftest_flowworks_stock.py"), "--only", "PitLip*,PitSide*"])
    return r.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
