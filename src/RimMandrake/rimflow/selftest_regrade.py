#!/usr/bin/env python3
"""selftest_regrade.py - regrade.py's noise guard on a planted store and audit record.

Item REGRADE_SAMPLE_BUILD_NOISE_GUARDED (spec design/RimMandrake/relentless_improvement_loop_2026-11-03.md, "Regrade
noise guard"). Each check names the broken version it catches:
  cap       - at most 3 draws per UTC day, never a re-draw         (broken: a day drains the whole store)
  recorded  - one grader's VIOLATED is recorded, not acted on       (broken: one noisy grade files work)
  two       - two distinct graders on one item -> ACT               (broken: agreement never acts)
  same      - the same grader twice is refused                      (broken: one grader "agrees" with itself)
  kind      - one plain tag VIOLATED on two items -> ACT            (broken: a repeating kind is never seen)
  stop      - 14 days, nothing actionable -> STOPPED, draw refuses  (broken: it runs forever)
  wired     - the daily findings judge prompt carries the step      (broken: nobody ever runs it)

    python3 src/RimMandrake/rimflow/selftest_regrade.py
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import delivery_metrics as dm, regrade as rg          # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FAILS = []
DAY = 86400.0
T0 = dm.ep("2026-11-06T09:00:00Z")


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def plant(root, n=10):
    s = os.path.join(root, "store")
    for k in range(n):
        d = os.path.join(s, "items", "ITEM_%02d" % k)
        os.makedirs(d)
        with open(os.path.join(d, "state.json"), "w") as f:
            json.dump({"status": "done", "done_at": T0 - DAY, "last_sha": "abc%02d" % k,
                       "check": {"verdict": "PASS", "reasons": ""}, "contract": {"proof": "true"}}, f)
        open(os.path.join(d, "attempts.jsonl"), "w").close()
    os.makedirs(os.path.join(root, "ledger"))
    return s


def run(args, store, audits, now):
    out, err = io.StringIO(), io.StringIO()
    code = None
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = rg.main(["--store", store, "--audits", audits] + args, now=now)
        except SystemExit as e:
            code, msg = 1, str(e.code)
            err.write(msg)
    return code, out.getvalue(), err.getvalue()


def main():
    root = tempfile.mkdtemp(prefix="selftest_regrade_")
    old_ledger = dm.LEDGER
    try:
        store = plant(root)
        dm.LEDGER = os.path.join(root, "ledger")
        audits = os.path.join(root, "close_audits.jsonl")
        # cap
        c1, o1, _ = run(["draw", "--n", "2"], store, audits, T0)
        c2, o2, _ = run(["draw", "--n", "5"], store, audits, T0 + 60)
        c3, _, e3 = run(["draw"], store, audits, T0 + 120)
        today = [l.split()[1] for l in (o1 + o2).splitlines()]
        check(c1 == 0 and c2 == 0 and len(today) == 3, "cap: two draws on one day give 3 items in total (%s)" % today)
        check(c3 != 0 and "CAP" in e3, "cap: a fourth draw that day is refused")
        _, o4, _ = run(["draw"], store, audits, T0 + DAY)
        _, o5, _ = run(["draw"], store, audits, T0 + 2 * DAY)
        drawn = today + [l.split()[1] for l in (o4 + o5).splitlines()]
        check(len(drawn) == 9 and len(set(drawn)) == 9, "cap: never re-draws an item across days (%d drawn, %d unique)"
              % (len(drawn), len(set(drawn))))
        rows = dm._jsonl(audits)
        check(not dm.damaged(rows), "the record stays well-formed for delivery_metrics")
        s0, s1 = "R20261106", "R20261107"
        a, b = today[0], today[1]
        x, y = [l.split()[1] for l in o4.splitlines()][:2]
        g = lambda smp, it, v, by, tag=None, t=T0 + 3 * DAY: run(
            ["grade", smp, it, v, "--by", by, "--how", "reran proof", "--evidence", "exit 1"]
            + (["--tag", tag] if tag else []), store, audits, t)
        # recorded
        cv, _, ev = g(s0, a, "VIOLATED", "grader-1")
        check(cv != 0 and "--tag" in ev, "recorded: a VIOLATED without a plain tag is refused")
        g(s0, a, "VIOLATED", "grader-1", "The test checked the file, not the running game.")
        g(s0, b, "HOLDS", "grader-1")
        _, rep, _ = run(["report", "--json"], store, audits, T0 + 3 * DAY)
        f = json.loads(rep)["findings"]
        check(not f["act"] and [r["item"] for r in f["recorded"]] == [a],
              "recorded: one grader's VIOLATED is recorded, not acted on")
        # same grader again
        cs, _, es = g(s0, a, "VIOLATED", "Grader-1 ", "Only proven on the minimal mod list.")
        check(cs != 0 and "different grader" in es, "same: the same grader grading the item twice is refused")
        # two graders
        g(s0, a, "VIOLATED", "grader-2", "Only proven on the minimal mod list.")
        _, rep, _ = run(["report", "--json"], store, audits, T0 + 3 * DAY)
        f = json.loads(rep)["findings"]
        check([z.get("item") for z in f["act"]] == [a] and f["act"][0]["why"] == "two graders agree" and not f["recorded"],
              "two: two distinct graders calling one item VIOLATED is actionable")
        # kind repeats
        g(s1, x, "VIOLATED", "grader-1", "A finding was closed without the item's own test running.")
        g(s1, y, "VIOLATED", "grader-3", "a finding was closed without the item's own test running")
        _, txt, _ = run(["report"], store, audits, T0 + 3 * DAY)
        check("ACT kind repeats on 2 items" in txt and x in txt and y in txt,
              "kind: the same plain tag VIOLATED on two items is actionable")
        # stop: a fresh record with only noise
        audits2 = os.path.join(root, "noise.jsonl")
        _, o, _ = run(["draw", "--n", "1"], store, audits2, T0)
        it = o.split()[1]
        run(["grade", "R20261106", it, "VIOLATED", "--by", "g1", "--how", "h", "--evidence", "e", "--tag", "Noise."],
            store, audits2, T0 + DAY)
        cr, txt13, _ = run(["report"], store, audits2, T0 + 13 * DAY)
        check(cr == 0 and "RUNNING" in txt13, "stop: still running on day 13")
        cr, txt14, _ = run(["report"], store, audits2, T0 + 14 * DAY)
        cd, _, ed = run(["draw"], store, audits2, T0 + 14 * DAY)
        check(cr == 3 and "STOPPED" in txt14 and cd != 0 and "STOPPED" in ed,
              "stop: 14 days with nothing actionable says STOPPED and draw refuses")
        cr, txt, _ = run(["report"], store, audits, T0 + 30 * DAY)
        check(cr == 0 and "RUNNING" in txt, "stop: a regrade that found something that held up keeps running")
        # wired
        with open(os.path.join(REPO, "src", "RimMandrake", "Utils", "findings_judge_prompt.md"), encoding="utf-8") as fh:
            p = fh.read()
        check("rimflow/regrade.py draw" in p and "regrade.py report" in p and "close_audits.jsonl" in p,
              "wired: the daily findings judge prompt draws, grades and reports the regrade")
    finally:
        dm.LEDGER = old_ledger
        shutil.rmtree(root, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
