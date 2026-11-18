#!/usr/bin/env python3
"""Failing acceptance cases for ticket RIMMANDRAKE_CLOSE_CARRIED_GAPS_REPAIRED_WITHOUT_CLAIM_FORM (owner by card
2026-11-17, design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md, rule 2 and "Two bugs fixed").

Rule 2: the second look checks whether the listed problems were fixed "by reading the fix itself, never by whether a
form was filed". Today coverage_judge.delta_merge re-adds every carried (unclaimed) gap as `unfixed` and turns a covered
word into not_covered, whatever the judge's own checklist rows say. Pyrelands look 8 (tickets/look8_replay.json): no
claim form matched, the judge redid every row the three carried gaps name, all parts ok, and said the changes answer
them; the merge refused anyway.

Contract (delta_merge only; delta_plan and the rows it asks for are unchanged):
  a carried gap CLOSES when all of these hold, read from the judge's OWN checklist (before the prior rows are appended):
    - it names at least one id;
    - every id it names has a row the judge wrote this look;
    - each of those rows has at least one part, and every part has ok True;
    - no gap the judge returned this look (kept or dropped) names any of its ids.
  a closed gap leaves rec["gaps"] and is listed in rec["answered"] as {"gid", "ids", "what"}; every other carried gap is
  carried exactly as today. A covered word with no carried gap left stands.
Input kinds read: the look-8 replay; a mix (one closes, one does not); a row not redone this look (prior row ok); a
not-ok part; a row with no parts; a gap the judge repeats; a gap with no ids; a gap with some ids redone; a not_covered
word with the judge's own open gap; the prompt's carried heading.
Run from the repo root:  python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_carried_gap_closes_on_ok_rows.py
Prints every wrong case, then: cases read, wrong count (worst), limit 0. Exit 1 when any case is wrong."""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
import coverage_judge as CJ  # noqa: E402

with open(os.path.join(HERE, "look8_replay.json")) as f:
    L8 = json.load(f)

wrong, n = [], 0


def expect(name, ok, got):
    global n
    n += 1
    if not ok:
        wrong.append("%s: got %s" % (name, got))


def row(i, oks=(True,)):
    return {"id": i, "parts": [{"what": "part %d of %s" % (k, i), "scene": "sc_x", "ok": o} for k, o in enumerate(oks)]}


def cgap(gid, ids, sev="problem"):
    return {"gid": gid, "ids": list(ids), "what": "gap %s" % gid, "severity": sev, "new_since": "changed",
            "bar_kind": "experience"}


def plan(carried, ids, prior_rows=()):
    return {"claims": [], "refused": [], "changed": ["scene:sc_x"], "against": "rm-coverage-judge-1",
            "prior_checklist": [dict(r) for r in prior_rows], "entries": {}, "ids": list(ids),
            "claimed_gaps": [], "carried": [dict(g) for g in carried], "loose": False}


def merge(verdict, gaps, rows, dp):
    rec = {"verdict": verdict, "gaps": [dict(g) for g in gaps], "checklist": [dict(r) for r in rows], "reasons": "r"}
    return CJ.delta_merge(rec, dp)


def open_gids(rec):
    return sorted(g.get("gid") for g in rec.get("gaps") or [] if g.get("carried"))


def answered(rec):
    return sorted(a.get("gid") for a in rec.get("answered") or [] if isinstance(a, dict))


# 1. the look-8 replay: every carried gap's rows redone by the judge, all ok, no claim form -> covered, 3 answered
dp = plan(L8["carried"], [r["id"] for r in L8["judge_rows"]], L8["prior_checklist"])
rec = merge("covered", [], copy.deepcopy(L8["judge_rows"]), dp)
expect("look-8 replay: covered", rec.get("verdict") == "covered", rec.get("verdict"))
expect("look-8 replay: no carried gap left", open_gids(rec) == [], open_gids(rec))
expect("look-8 replay: g1 g2 g3 answered", answered(rec) == ["g1", "g2", "g3"], answered(rec))
expect("look-8 replay: the merged checklist still holds all 45 rows",
       len(rec.get("checklist") or []) == len(L8["prior_checklist"]), len(rec.get("checklist") or []))
CJ.apply_bar_rule(rec)
expect("look-8 replay: still covered after the bar rule", rec.get("verdict") == "covered", rec.get("verdict"))

A, B = cgap("g1", ["a"]), cgap("g2", ["b"])
# 2. mix: a's row ok, b's row has a not-ok part -> g1 answered, g2 carried, not_covered
rec = merge("covered", [], [row("a"), row("b", (True, False))], plan([A, B], ["a", "b"]))
expect("mix: g1 answered", answered(rec) == ["g1"], answered(rec))
expect("mix: g2 carried and not_covered", open_gids(rec) == ["g2"] and rec.get("verdict") == "not_covered",
       (open_gids(rec), rec.get("verdict")))
# 3. a row not redone this look stays open, even with the prior row ok
rec = merge("covered", [], [row("a")], plan([A, B], ["a"], [row("b")]))
expect("row not redone (prior ok): g2 carried", open_gids(rec) == ["g2"] and rec.get("verdict") == "not_covered",
       (open_gids(rec), rec.get("verdict")))
# 4. every part not ok stays open
rec = merge("covered", [], [row("a", (False,))], plan([A], ["a"]))
expect("not-ok part: carried", open_gids(rec) == ["g1"] and answered(rec) == [], (open_gids(rec), answered(rec)))
# 5. a row with no parts proves nothing
rec = merge("covered", [], [{"id": "a", "parts": []}], plan([A], ["a"]))
expect("row with no parts: carried", open_gids(rec) == ["g1"], open_gids(rec))
# 6. the judge repeats the gap (its own gap on the same id) -> not answered, whatever the row says
rec = merge("not_covered", [{"what": "a still open", "ids": ["a"], "new_since": "unfixed", "severity": "problem"}],
            [row("a")], plan([A], ["a"]))
expect("repeated by the judge: not answered", answered(rec) == [] and rec.get("verdict") == "not_covered",
       (answered(rec), rec.get("verdict")))
# 7. a judge gap on the id that the merge drops still keeps the carried gap open
rec = merge("covered", [{"what": "a again", "ids": ["a"], "new_since": "first", "severity": "problem"}],
            [row("a")], plan([A], []))
expect("repeated but dropped: not answered", answered(rec) == [] and open_gids(rec) == ["g1"],
       (answered(rec), open_gids(rec)))
# 8. a carried gap with no ids has nothing to read: stays
rec = merge("covered", [], [row("a")], plan([cgap("g1", [])], ["a"]))
expect("no ids: carried", open_gids(rec) == ["g1"], open_gids(rec))
# 9. some ids redone, one not: stays
rec = merge("covered", [], [row("a")], plan([cgap("g1", ["a", "c"])], ["a"], [row("c")]))
expect("partial ids: carried", open_gids(rec) == ["g1"], open_gids(rec))
# 10. the judge's own open gap keeps not_covered even when the carried gap closes
rec = merge("not_covered", [{"what": "new on a changed row", "ids": ["b"], "new_since": "changed",
                             "severity": "problem"}], [row("a"), row("b", (False,))], plan([A], ["a", "b"]))
expect("own gap stands, carried closes", answered(rec) == ["g1"] and rec.get("verdict") == "not_covered"
       and [g.get("what") for g in rec.get("gaps") or []] == ["new on a changed row"],
       (answered(rec), rec.get("verdict"), rec.get("gaps")))
# 11. polish carried gap answered the same way (closure is by rows, not severity)
rec = merge("covered", [], [row("a")], plan([cgap("g1", ["a"], "polish")], ["a"]))
expect("polish carried gap with ok rows: answered", answered(rec) == ["g1"], answered(rec))

# 12. the judge is told how a carried gap closes (rule 2: it reads the fix itself)
CAR = ("A carried gap is closed when every row on its ids that you write this look is all ok; one you find still "
       "open, write its row with the part not ok.")
d = os.path.join(ROOT, "design", "concepts", "X")
p = CJ.delta_prompt(d, ROOT, plan([A], ["a"]), 2)
expect("delta prompt says how a carried gap closes", CAR in " ".join(p.split()), "sentence absent")
expect("delta prompt no longer says only 'do not repeat them' for carried gaps",
       "carried on file (do not repeat them)" not in p, "old heading present")
# 13. the Designer's brief says the same (roles/designer_lock.md item 3 today: "A gap you do not claim stays open;")
with open(os.path.join(ROOT, "src", "RimMandrake", "rimflow", "roles", "designer_lock.md")) as f:
    lock = " ".join(f.read().split())
LOCK = ("A gap you do not claim stays open unless the judge's own rows on all its ids read ok; then it is closed and "
        "listed as answered.")
expect("designer_lock.md says how an unclaimed gap closes", LOCK in lock and "A gap you do not claim stays open;"
       not in lock, "old sentence present or new one absent")

for w in wrong:
    print("WRONG", w)
print("cases read %d; wrong %d (worst); limit 0" % (n, len(wrong)))
sys.exit(1 if wrong else 0)
