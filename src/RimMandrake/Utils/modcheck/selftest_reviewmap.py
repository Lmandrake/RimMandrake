#!/usr/bin/env python3
"""Selftest for modcheck/reviewmap.py (offline, fake bridge, fake Saves folder)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modcheck import reviewmap as RM  # noqa: E402

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


# free_save_name: base, then _b, _c
check(RM.free_save_name("X", {}) == "X", "free name base")
check(RM.free_save_name("X", {"X.rws": 1}) == "X_b", "free name suffix b")
check(RM.free_save_name("X", {"X.rws": 1, "X_b.rws": 1}) == "X_c", "free name suffix c")

# judge_save: exactly one new file named right, nothing changed or gone
b = {"a.rws": (10, 1)}
check(RM.judge_save(b, {"a.rws": (10, 1), "K.rws": (5, 2)}, "K")["ok"], "one new file -> ok")
check(not RM.judge_save(b, {"a.rws": (11, 3), "K.rws": (5, 2)}, "K")["ok"], "changed slot -> FAIL (wrong-slot trap)")
check(not RM.judge_save(b, {"a.rws": (11, 3)}, "K")["ok"], "current slot written instead -> FAIL")
check(not RM.judge_save(b, {"a.rws": (10, 1), "Q.rws": (5, 2)}, "K")["ok"], "wrongly named new file -> FAIL")


class FakeB(object):
    def __init__(self, pawns=(), saves=None, write=None):
        self.calls, self.pawns, self.saves, self.write = [], list(pawns), saves, write

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": self.pawns}
        if tool == "jawa/destroy_bulk":
            return {"success": True, "matchedCount": 3}
        if tool == "rimworld/save_game":
            self.saves.update(self.write)
            return {"success": True}
        return {"success": True}


# save_keeper with an injected stat: the right new file -> ok; the current slot written -> not ok; existing -> refused
saves = {"cur.rws": (10, 1)}
B = FakeB(saves=saves, write={"K.rws": (7, 9)})
r = RM.save_keeper(B, "K", stat=lambda d: dict(saves), sleep=lambda s: None, wait_s=0)
check(r["ok"] and r["new"] == ["K.rws"], "save_keeper ok path: %s" % r)
saves2 = {"cur.rws": (10, 1)}
B2 = FakeB(saves=saves2, write={"cur.rws": (12, 5)})
r2 = RM.save_keeper(B2, "K", stat=lambda d: dict(saves2), sleep=lambda s: None, wait_s=0)
check(not r2["ok"] and r2["changed"] == ["cur.rws"], "save_keeper wrong-slot trap caught: %s" % r2)
r3 = RM.save_keeper(FakeB(saves={"K.rws": 1}), "K", stat=lambda d: {"K.rws": (1, 1)}, sleep=lambda s: None)
check(not r3["ok"] and r3.get("refused"), "save_keeper refuses an existing name")

# sweep_pawns: no keep rects -> the GSS sweep; keep rects -> outsiders killed by id, insiders and colonists kept
B = FakeB()
r = RM.sweep_pawns(B)
check([c[0] for c in B.calls] == ["jawa/destroy_bulk", "jawa/incident_queue_clear"], "plain sweep calls: %s" % B.calls)
pawns = [dict(id=1, x=5, z=5, isPlayer=True, intelligence="Humanlike"),        # colonist outside: kept
         dict(id=2, x=5, z=5, isPlayer=False, intelligence="Animal"),          # wild animal outside: removed
         dict(id=3, x=50, z=50, isPlayer=False, intelligence="Animal"),        # held animal inside: kept
         dict(id=4, x=51, z=51, isPlayer=False, intelligence="Humanlike"),     # prisoner inside: kept
         dict(id=5, x=0, z=0, dead=True)]                                      # corpse: ignored
B = FakeB(pawns=pawns)
r = RM.sweep_pawns(B, keep_rects=[(48, 48, 10, 10)])
killed = [kw["pawn"] for t, kw in B.calls if t == "jawa/pawn_force_incapacitate"]
check(killed == ["2"] and r["kept"] == 2, "keep-rect sweep: killed %s, %s" % (killed, r))
check(not any(t == "jawa/destroy_bulk" for t, _ in B.calls), "keep-rect sweep must not destroy_bulk (no exclusion list)")

B = FakeB(pawns=[pawns[0], pawns[1]])
r = RM.sweep_pawns(B, keep_rects=[(48, 48, 10, 10)])
check(any(t == "jawa/destroy_bulk" for t, _ in B.calls) and not any(t == "jawa/pawn_force_incapacitate" for t, _ in B.calls),
      "nothing held -> the clean destroy_bulk route: %s" % B.calls)

# pawn_xz reads every row shape seen
check(RM.pawn_xz({"x": 1, "z": 2}) == (1, 2), "pawn_xz x/z")
check(RM.pawn_xz({"position": {"x": 3, "z": 4}}) == (3, 4), "pawn_xz dict")
check(RM.pawn_xz({"position": "(5, 0, 6)"}) == (5, 6), "pawn_xz string")

# label_line: separators and newlines made safe
ln = RM.label_line(1, 2, "a|b\nc", "s|t", "#ffffff", "small", "tg")
check(ln.split("|") == ["1", "2", "a/b c", "s/t", "#ffffff", "small", "tg"], "label_line: %r" % ln)

print("FAIL\n  " + "\n  ".join(fails) if fails else "ok  reviewmap: save names, save judge (wrong-slot trap), sweep, labels")
sys.exit(1 if fails else 0)
