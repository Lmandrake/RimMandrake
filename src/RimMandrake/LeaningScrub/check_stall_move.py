#!/usr/bin/env python3
"""Read the Stall chain's recorded path/job samples and say whether the 2026-10-07 shared move recurred.

LEANINGSCRUB_STALL_SHARED_MOVE_1: on 2026-10-07 both stall animals (RM_Thornhold 0.4, RM_Shirrel 0.7) moved the same
+12,+12 in the first 250 ticks, then held; no job was sampled, so the move could not be named. validation.py's
stall_chain now samples the job at every step (_path). This reads its note "Stall: path lengths (cells) and sampled
jobs over 1500 ticks" from a modcheck run JSON (or the frozen extract in live_evidence/) and:
  exit 0  the small animal held (path < 1.5 cells) and every sampled job of both animals is wander-family;
  exit 1  the small animal moved, or any non-wander job was sampled -- the job names are printed (the move named);
  exit 2  no stall reading in the file (UNMEASURED, never a pass).
Usage: check_stall_move.py <run.json | extract.json>...   |   check_stall_move.py --selftest
"""
import json
import sys

NOTE = "Stall: path lengths (cells) and sampled jobs over 1500 ticks"
WANDER = {None, "GotoWander", "Wait_Wander", "Wait_MaintainPosture", "Wait"}
SMALL, BIG = "RM_Thornhold", "RM_Shirrel"
HOLD = 1.5


def readings(obj):
    """Every result dict recorded under NOTE, wherever it sits (modcheck evidence 'call' or extract 'note')."""
    out = []
    if isinstance(obj, dict):
        if (obj.get("call") == NOTE or obj.get("note") == NOTE) and isinstance(obj.get("result"), dict):
            out.append(obj["result"])
        for v in obj.values():
            out.extend(readings(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(readings(v))
    return out


def judge(res):
    """(ok, lines) for one reading {pawnId: {path, jobs, ...}}."""
    lines, ok = [], True
    small = [v for k, v in res.items() if k.startswith(SMALL)]
    big = [v for k, v in res.items() if k.startswith(BIG)]
    if len(small) != 1 or len(big) != 1:
        return None, ["reading lacks one %s and one %s: %s" % (SMALL, BIG, sorted(res))]
    for name, row in ((SMALL, small[0]), (BIG, big[0])):
        other = sorted(set(str(j) for j in row.get("jobs") or [] if j not in WANDER))
        lines.append("%s path %.1f jobs-outside-wander %s" % (name, row.get("path", -1), other or "none"))
        if other:
            ok = False
    if small[0].get("path", 99) >= HOLD:
        ok = False
        lines.append("%s moved %.1f cells (>= %.1f) in the Stall" % (SMALL, small[0]["path"], HOLD))
    return ok, lines


def check(paths):
    found, bad = 0, 0
    for p in paths:
        with open(p) as fh:
            for res in readings(json.load(fh)):
                found += 1
                ok, lines = judge(res)
                if ok is None:
                    return 2
                bad += 0 if ok else 1
                print("%s: %s -- %s" % (p, "HELD" if ok else "MOVED", "; ".join(lines)))
    if not found:
        print("UNMEASURED: no '%s' reading in %s" % (NOTE, paths))
        return 2
    print("%d reading(s), %d with a move" % (found, bad))
    return 1 if bad else 0


def selftest():
    held = {SMALL + "1": {"path": 0.0, "jobs": [None, "Wait_Wander"]}, BIG + "2": {"path": 12.3, "jobs": ["GotoWander"]}}
    flee = {SMALL + "1": {"path": 17.0, "jobs": [None, "Flee", "Wait_Wander"]},
            BIG + "2": {"path": 16.5, "jobs": [None, "Flee", "Wait_Wander"]}}
    wander_moved = {SMALL + "1": {"path": 17.0, "jobs": ["GotoWander"]}, BIG + "2": {"path": 3.0, "jobs": []}}
    assert judge(held)[0] is True
    ok, lines = judge(flee)
    assert ok is False and any("Flee" in l for l in lines), lines
    assert judge(wander_moved)[0] is False
    assert judge({SMALL + "1": held[SMALL + "1"]})[0] is None
    assert readings({"x": [{"call": NOTE, "result": held}]}) == [held]
    print("selftest ok")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    if not sys.argv[1:]:
        print(__doc__)
        sys.exit(2)
    sys.exit(check(sys.argv[1:]))
