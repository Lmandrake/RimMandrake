"""Offline checks for climb_proof.py's pure verdicts (PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP). No bridge."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import climb_proof as C  # noqa: E402

fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


LINE = "CLIMB k=2 held=True trapped=True cell=11,3 | POCKET k=2 comp=7 pocket=True size=9 depth=3 gen=5 built=5 rebuilds=3"
kv = C.parse(LINE)
check("parse reads both halves", kv.get("held") == "True" and kv.get("pocket") == "True" and kv.get("size") == "9")
check("a fresh grid is evidence", C.fresh(kv))
check("trapped person: PASS", C.state_verdict(kv, want_held=True, want_trapped=True, want_pocket=True)[0] == "PASS")
check("can-fail: a free pawn read as trapped is FAIL", C.state_verdict(kv, want_held=False)[0] == "FAIL")
stale = C.parse(LINE.replace("built=5", "built=4"))
check("a stale grid is UNMEASURED, never PASS or FAIL", C.state_verdict(stale, want_held=True)[0] == "UNMEASURED")
check("no pawn line is UNMEASURED", C.state_verdict(C.parse("POCKET k=2 pocket=True gen=1 built=1"))[0] == "UNMEASURED")
check("REFUSED text parses to no verdict", C.state_verdict(C.parse("REFUSED: no spawned pawn 9"))[0] == "UNMEASURED")

R = (10, 10, 5, 5)
row_out = {"orderAccepted": True, "ticksElapsed": 900, "position": {"x": 12, "z": 17}}
row_in = {"orderAccepted": True, "ticksElapsed": 900, "position": [12, 12]}
check("walked out of the rect: PASS", C.walk_verdict(row_out, R, True)[0] == "PASS")
check("can-fail: stayed in when it should walk out", C.walk_verdict(row_in, R, True)[0] == "FAIL")
check("stayed in when held: PASS", C.walk_verdict(row_in, R, False)[0] == "PASS")
check("a game that never ticked is UNMEASURED", C.walk_verdict(dict(row_in, ticksElapsed=0), R, False)[0] == "UNMEASURED")
check("an unaccepted order is UNMEASURED", C.walk_verdict(dict(row_in, orderAccepted=False), R, False)[0] == "UNMEASURED")
check("owed rows are named, four of them", len(C.OWED) == 4 and all(k.startswith("CLIMB_") for k in C.OWED))

# PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS: the mask row
MP = C.parse("CLIFF k=2 bits=0xFB vanilla=0xFF derived=True derives=4 | POCKET k=2 comp=0 pocket=False")
MB = C.parse("CLIFF k=3 bits=0xFF vanilla=0xFF derived=True derives=4 | POCKET k=3 comp=0 pocket=False")
check("mask: person sealed east, muffalo open: PASS", C.mask_verdict(MP, MB) == "PASS")
check("can-fail: person still open east is FAIL", C.mask_verdict(MB, MB) == "FAIL")
check("masks not derived: UNMEASURED", C.mask_verdict(dict(MP, derived="False"), MB) == "UNMEASURED")
check("vanilla has no east step (a wall): UNMEASURED", C.mask_verdict(dict(MP, vanilla="0xFB"), MB) == "UNMEASURED")
check("a REFUSED read: UNMEASURED", C.mask_verdict(C.parse("REFUSED: no masks"), MB) == "UNMEASURED")

print("%s: %d failure(s)" % ("PASS" if not fails else "FAIL", len(fails)))
sys.exit(1 if fails else 0)
