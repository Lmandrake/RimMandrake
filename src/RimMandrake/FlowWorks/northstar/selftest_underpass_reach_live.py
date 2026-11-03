"""underpass_reach_live.py (UNDERPASS_REACH_VERIFY_WALK_UNDER_FOR_REAL) runs offline against a FakeBridge and its verdict is
the right one: a production-shaped PASS read is PASS (exit 0), a vetoed walk is FAIL (exit 1), a control that cannot see a veto
or a bridge that did not build is UNMEASURED (exit 2), and the C# read it calls exists with the fields the script parses.
Proves the SCRIPT and its source pins, never the game (the live rows are infrastructure/state/live_proofs/<item>.txt).

    python3 src/RimMandrake/FlowWorks/northstar/selftest_underpass_reach_live.py
"""
import io
import os
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import underpass_reach_live as U  # noqa: E402

GOOD = {"A1": "REACH veto=False reach=True reachPawnless=True found=True cells=8 onDeck=2 under=2 view=floor agree=True",
        "A2": "REACH veto=False reach=True reachPawnless=True found=True cells=4 onDeck=2 under=0 view=deck agree=True"}
CTL = "REACH veto=True reach=False reachPawnless=False found=False cells=0 onDeck=0 under=0 view=deck agree=True"


class FakeBridge:
    def __init__(self, clause, read=None, control=CTL, build="BUILD ok=True anchors=2 decks=2", at=None):
        self.clause, self.read, self.control, self.build, self.at = clause, read or GOOD[clause], control, build, at
        self.calls = []
        s = U.SCENES[clause]
        self.origin = (60 + s["plot"][0], 60 + s["plot"][1])
        self.pawn_at = at or (self.origin[0] + s["pawn"][0], self.origin[1] + s["pawn"][1])
        self.control_cell = "%d,%d" % (self.origin[0] + s["control"][0], self.origin[1] + s["control"][1])

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "jawa/static_call":
            m, arg = kw.get("method"), kw.get("args", "")
            if m == "ProofBuild":
                return {"success": True, "result": self.build}
            if m == "ProofBand":
                return {"success": True, "result": "BAND under=False onDeck=False passes=False view=deck deckNotches=-1"}
            if m == "ProofReach":
                assert arg.split(";")[0] == "41594", arg
                return {"success": True, "result": self.control if arg.endswith(";" + self.control_cell) else self.read}
            return {"success": True, "result": "?"}
        if tool == "jawa/spawn_pawn":
            return {"pawns": [{"id": "Human41594"}]}
        if tool == "jawa/list_pawns":
            return {"pawns": [{"id": "Human41594", "x": self.pawn_at[0], "z": self.pawn_at[1]}]}
        return {"success": True}


def run(argv, fb):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = U.main(argv, bridge=fb)
    return rc, buf.getvalue()


def main():
    fails = []

    def check(ok, msg):
        if not ok:
            fails.append(msg)

    for cl in ("A1", "A2"):
        fb = FakeBridge(cl)
        rc, txt = run([cl], fb)
        check(rc == 0 and "PASS" in txt, "%s: a good read passes (rc=%s %s)" % (cl, rc, txt[:200]))
        digs = [c for c in fb.calls if c[0] == "jawa/flowworks_excavation_drive"]
        check(len(digs) == len(U.SCENES[cl]["digs"]), "%s: every plot square is dug" % cl)
        check(any(c[0] == "jawa/pawn_force_incapacitate" for c in fb.calls), "%s: the colonist is cleaned up" % cl)
        # can-fail: the bug a01c76fe25 fixed (reach refused the walk A* takes)
        bad = GOOD[cl].replace("veto=False", "veto=True").replace("reach=True reachPawnless=True",
                                                                  "reach=False reachPawnless=False").replace("agree=True", "agree=False")
        rc, txt = run([cl], FakeBridge(cl, read=bad))
        check(rc == 1 and "FAIL" in txt, "%s: a vetoed walk fails (rc=%s)" % (cl, rc))
        rc, _ = run([cl], FakeBridge(cl, read=GOOD[cl].replace("found=True", "found=False").replace("agree=True", "agree=False")))
        check(rc == 1, "%s: no A* path fails" % cl)
        rc, _ = run([cl], FakeBridge(cl, control=GOOD[cl]))
        check(rc == 2, "%s: a control that sees no veto is UNMEASURED, never PASS (rc=%s)" % (cl, rc))
        rc, _ = run([cl], FakeBridge(cl, build="BUILD ok=False reason=undug"))
        check(rc == 2, "%s: a bridge that did not build is UNMEASURED" % cl)
        rc, _ = run([cl], FakeBridge(cl, at=(0, 0)))
        check(rc == 2, "%s: a colonist off the plot is UNMEASURED" % cl)
    # A1 needs a square UNDER a deck; A2 needs the path ON the sunken deck and the deck view
    rc, _ = run(["A1"], FakeBridge("A1", read=GOOD["A1"].replace("under=2", "under=0")))
    check(rc == 1, "A1: a path that never goes under the deck fails")
    rc, _ = run(["A2"], FakeBridge("A2", read=GOOD["A2"].replace("onDeck=2", "onDeck=0")))
    check(rc == 1, "A2: a path that never stands on the sunken deck fails")
    rc, _ = run(["A2"], FakeBridge("A2", read=GOOD["A2"].replace("view=deck", "view=floor")))
    check(rc == 1, "A2: the floor view at ledge height (the old rule) fails")

    # source pins: the C# read exists, runs production and answers every field the script parses
    cs = os.path.join(HERE, "..", "Source", "Pits", "Suspension", "RM_SuspensionProofs.cs")
    with open(cs, encoding="utf-8") as f:
        src = f.read()
    body = src[src.find("public static string ProofReach("):]
    body = body[:body.find("public static string", 10)]
    check("public static string ProofReach(" in src, "RM_SuspensionProofs.ProofReach exists")
    for pin in ("RM_SuperdeepTrap.RelativeVeto(map, p.Position, dest, PathEndMode.OnCell, p)",
                "map.reachability.CanReach(p.Position, dest, PathEndMode.OnCell, TraverseParms.For(p))",
                "TraverseParms.For(TraverseMode.PassDoors)", "map.pathFinder.FindPathNow(p.Position, dest, p)",
                "map.reachability.ClearCache()", "RM_SuspensionUnderpass.UsesFloorView(p)"):
        check(pin in body, "ProofReach calls production: " + pin)
    for field in ("veto", "reach", "reachPawnless", "found", "cells", "onDeck", "under", "view", "agree"):
        check('" %s="' % field in body or '"REACH %s="' % field in body, "ProofReach answers %s=" % field)
    # the live proof file names both clauses, one line each, through this script
    lp = os.path.join(HERE, "..", "..", "..", "..", "infrastructure", "state", "live_proofs", U.ITEM + ".txt")
    with open(lp, encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if ln.startswith("live-proof ")]
    for cl in ("A1", "A2"):
        check(any(ln.startswith("live-proof %s: " % cl) and "underpass_reach_live.py %s" % cl in ln for ln in lines),
              "live_proofs names %s" % cl)
    for m in fails:
        print("FAIL " + m)
    print("selftest_underpass_reach_live: %s (%d failed)" % ("OK" if not fails else "FAILED", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
