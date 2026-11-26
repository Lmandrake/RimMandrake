#!/usr/bin/env python3
"""compare.py - the live before/after of the shared scene runner (RIMMANDRAKE_PROVE_SCENE_RUNNER_LIVE_SAME_ROWS_FEWER_CALLS).

    python3 design/specs/2026-11-26-scene-runner-live-proof/compare.py [evidence dir]

Reads the two arms' kept evidence: knockback_runner.py's run jsonl (old_arm.jsonl) with its counted calls
(old_arm_calls.json, count_old_arm.py), and scene_runner.py's report (new_arm.json). Holds (exit 0) only when:
  - the new arm's outcome is a verdict (not NO_RUN, PROOF_BUILD or RESTORE) and its scene-begin reload verified;
  - every old scene has a new VERDICT row with the same status (old INVALID = new UNMEASURED), and no extra scene;
  - each verdict's clauses (`name=True [...]`) are the same, in the same order, in both arms;
  - the new arm made fewer bridge calls than the old arm.
Exit 1 when any of these fails, 2 when the evidence cannot be read.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLAUSE = re.compile(r"(\w+)=(True|False) \[")
SAME = {"PASS": "PASS", "FAIL": "FAIL", "ERROR": "FAIL", "INVALID": "UNMEASURED"}


def main(argv):
    d = argv[1] if len(argv) > 1 else os.path.join(HERE, "evidence")
    try:
        new = json.load(open(os.path.join(d, "new_arm.json"), encoding="utf-8"))
        old = [json.loads(l) for l in open(os.path.join(d, "old_arm.jsonl"), encoding="utf-8") if l.strip()]
        old_calls = json.load(open(os.path.join(d, "old_arm_calls.json"), encoding="utf-8"))["bridge_calls"]["total"]
        new_calls = new["bridge_calls"]["total"]
    except (OSError, ValueError, KeyError, TypeError) as ex:
        print("UNREADABLE evidence in %s: %s: %s" % (d, type(ex).__name__, ex))
        return 2
    bad = []
    if new.get("outcome") not in ("PASS", "FAIL", "UNMEASURED"):
        bad.append("new arm outcome %s is no verdict" % new.get("outcome"))
    if (new.get("restore") or {}).get("verified") is not True:
        bad.append("new arm's scene-begin reload not verified: %s" % new.get("restore"))
    olds = {r["scene"]: r["status"] for r in old if r.get("type") == "scenario"}
    news = {r["scene"]: r["status"] for r in new.get("rows") or [] if r.get("check") == "VERDICT"}
    if not olds:
        bad.append("old arm has no scene rows")
    for s, st in sorted(olds.items()):
        want = SAME.get(st, "FAIL")
        if news.get(s) != want:
            bad.append("%s: old %s, new %s" % (s, st, news.get(s)))
    # the verdict's clauses (east=True [...] pit=True [...]): the same clause, true or false, in both arms
    oldt = {r["scene"]: r.get("detail") or "" for r in old if r.get("type") == "scenario"}
    newt = {r["scene"]: r.get("measured") or "" for r in new.get("rows") or [] if r.get("check") == "VERDICT"}
    for s in sorted(set(oldt) & set(newt)):
        if CLAUSE.findall(oldt[s]) != CLAUSE.findall(newt[s]):
            bad.append("%s clauses: old %s, new %s" % (s, CLAUSE.findall(oldt[s]), CLAUSE.findall(newt[s])))
    for s in sorted(set(news) - set(olds)):
        bad.append("%s: new only" % s)
    if not new_calls < old_calls:
        bad.append("new arm made %s bridge calls, old %s: not fewer" % (new_calls, old_calls))
    for s in sorted(olds):
        print("%-28s old %-8s new %s" % (s, olds[s], news.get(s)))
    print("bridge calls: old %s, new %s; wall: old %s s, new %s s" % (
        old_calls, new_calls, json.load(open(os.path.join(d, "old_arm_calls.json"))).get("wall_s"),
        (new.get("split") or {}).get("total_s")))
    if bad:
        print("DIFFERS: " + "; ".join(bad))
        return 1
    print("SAME ROWS, FEWER CALLS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
