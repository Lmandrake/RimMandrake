#!/usr/bin/env python3
"""Selftest: the mod-ledger reducer reads every line, also the lines above a late version.open
(RIMMANDRAKE_FIX_REDUCER_SKIPS_LINES_ABOVE_LATE_VERSION_OPEN).

    python3 src/RimMandrake/Utils/run_selftests.py --only modledger_reduce_late_version

Live failure, 2026-11-19: the round-5 re-mine of Gimme Some Slack re-wrote its version.open (its 'bars met' text
changed) at the end of BACKFILL.jsonl. The reducer took the version from each earlier line in the same elif chain
as every other kind, so it skipped all 49 bar.locked lines and every stage line: stage None, 0 bars
(modledger_backfill_accept.py FAIL 2 of 7).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modledger as M                                            # noqa: E402

FAIL = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAIL.append(name)


def ev(i, kind, subject, body, version="0.1.0"):
    return {"id": "BACKFILL:%04d" % i, "writer": "BACKFILL", "kind": kind, "subject": subject, "body": body,
            "version": version, "ts": "2026-11-19T23:%02d:00Z" % i, "evidence": []}


lines = [ev(1, "bar.locked", "bar:a", {"text": "experience bar"}),
         ev(2, "stage.accepted", "stage", {"from": "blind_challenge", "to": "in_game"}),
         ev(3, "finding.open", "finding:F1", {"class": "problem", "bars": ["a"], "text": "x", "proposed_fix": "y",
                                              "accept": "z"}),
         ev(4, "version.open", "version", {"version": "0.1.0", "text": "Design Version 0.1.0"})]
late = M.reduce(lines)
early = M.reduce([lines[3]] + lines[:3])
check("a bar.locked above a late version.open counts", "bar:a" in late["bars"], sorted(late["bars"]))
check("a stage line above a late version.open counts", late["stage"] == "in_game", late["stage"])
check("a finding above a late version.open counts", "finding:F1" in late["findings"], sorted(late["findings"]))
check("the version is the version.open's", late["version"] == "0.1.0", late["version"])
check("control: the same lines with version.open first reduce the same",
      (early["stage"], sorted(early["bars"]), sorted(early["findings"])) ==
      (late["stage"], sorted(late["bars"]), sorted(late["findings"])), (early["stage"], late["stage"]))
check("control: with no version.open the version is the lines' own", M.reduce(lines[:3])["version"] == "0.1.0",
      M.reduce(lines[:3])["version"])
print("selftest_modledger_reduce_late_version: %d failure%s" % (len(FAIL), "" if len(FAIL) == 1 else "s"))
sys.exit(1 if FAIL else 0)
