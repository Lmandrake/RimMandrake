#!/usr/bin/env python3
"""selftest_arena_trial.py — arena_trial.py: the trial's explicit task list (ARENA_TRIAL_TASKS_FIX_DEFAULT_ALL_FROZEN).

Pure checks on select()/read_list() with synthetic banks, plus a shape check of the committed default
trial_tasks.json (at most 50 distinct ids, all three eras, oldest first). No git, no frozen bank needed.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_analysis as AA  # noqa: E402
import arena_trial as T  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -- %s" % (detail,)))
    if not ok:
        FAILS.append(name)


def bank(n=241, cs_every=6):
    """n tasks, chrono = i (oldest first), every cs_every-th one C#."""
    return {"B%03d" % i: {"kind": "csharp" if i % cs_every == 0 else ("python-util", "tooling")[i % 2], "chrono": i}
            for i in range(n)}


def t_select():
    b = bank()
    ids = T.select(b)
    eras, _ = AA.era_map(b)
    check("default: exactly 50 ids, distinct", len(ids) == 50 and len(set(ids)) == 50, len(ids))
    check("default is NOT every frozen task", len(ids) < len(b), len(ids))
    span = sorted({eras[t] for t in ids})
    check("the list spans all three eras of the bank", span == [0, 1, 2], span)
    per = [sum(1 for t in ids if eras[t] == e) for e in range(3)]
    check("eras split evenly, remainder to the newest (16, 17, 17)", per == [16, 17, 17], per)
    check("oldest first (chrono ascending)", [b[t]["chrono"] for t in ids] == sorted(b[t]["chrono"] for t in ids))
    cs = sum(1 for t in ids if b[t]["kind"] == "csharp")
    share = sum(1 for s in b.values() if s["kind"] == "csharp") / len(b)
    check("C# in proportion by default (bank share %.2f -> %d of 50)" % (share, cs), abs(cs - 50 * share) <= 3, cs)
    no = T.select(b, csharp=False)
    check("--no-csharp: no C# task, still 50 over three eras", len(no) == 50 and not any(
        b[t]["kind"] == "csharp" for t in no), len(no))
    check("deterministic", T.select(b) == ids)
    for bad in (51, 0, 241, "50"):
        try:
            T.select(b, bad)
            check("n=%r refused" % (bad,), False)
        except T.TrialError:
            check("n=%r refused (at most 50)" % (bad,), True)
    small = bank(20)
    check("a bank smaller than n -> every task, still oldest first", T.select(small) == sorted(small))
    try:
        T.select({"A": {"kind": "x", "chrono": 1}, "B": {"kind": "x"}})
        check("a bank task with no chronology key refuses", False)
    except T.TrialError:
        check("a bank task with no chronology key refuses", True)


def t_read_list():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "l")
        for body, want in (('{"schema": "%s", "tasks": ["A", "B"]}' % T.SCHEMA, ["A", "B"]), ('["A", "B"]', ["A", "B"]),
                           ("A\n\nB\n", ["A", "B"])):
            p.write_text(body)
            check("read_list accepts %r" % body[:14], T.read_list(p) == want)
        for body in ('{"schema": "other", "tasks": ["A"]}', '["A", "A"]', "A\nA\n", "[1, 2]", '{"tasks": "A"}'):
            p.write_text(body)
            try:
                T.read_list(p)
                check("read_list refuses %r" % body, False)
            except ValueError:
                check("read_list refuses %r" % body, True)


def t_default_file():
    ids = T.read_list(T.DEFAULT_PATH)
    doc = json.loads(T.DEFAULT_PATH.read_text(encoding="utf-8"))
    check("committed default trial_tasks.json: 1..50 distinct ids", 0 < len(ids) <= T.MAX_N, len(ids))
    check("committed default spans three eras", len(doc.get("eras_in_trial", [])) == 3 and all(
        doc["eras_in_trial"]), doc.get("eras_in_trial"))
    check("committed default: C# included (owner: C# tasks stay in the pool), sibling order checked",
          doc.get("csharp") is True and doc.get("kinds", {}).get("csharp", 0) > 0 and "check_rounds" in doc.get("order", ""),
          (doc.get("csharp"), doc.get("kinds")))
    check("analysis CLI default is this file", AA.TRIAL_DEFAULT == T.DEFAULT_PATH)


def main():
    for t in (t_select, t_read_list, t_default_file):
        t()
    print("\n%d failure(s)%s" % (len(FAILS), (": " + ", ".join(FAILS)) if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
