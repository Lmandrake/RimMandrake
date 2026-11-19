#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_SELECT_CALIBRATION_TEST_ON_REGISTRY_EDIT_JSON_UNSEEN.

selftest_calibration_rows_current.py holds the production calibration rows CALIBRATED at the door, but the door
(publish.pipeline_selection) never runs it for a change to the registry alone or to evidence_gate_corpus.json (a brief
file of evidence_gate): door_inputs reads .py files and same-stem .json only, and neither path is a pipeline_files
pattern. So a commit that deletes the maturation_advance row, or edits the corpus, lands with no recheck. Measured
2026-11-18 on the commit that added the test: both selections are empty.

Passes when each of those one-file changes selects selftest_calibration_rows_current.py at the door, and a change to an
unrelated .json file selects nothing (so "select it for everything" does not pass).

    python3 src/RimMandrake/rimflow/acceptance/calibration_registry_door_accept.py     exit 0 = pass, 1 = fail

Expected on a correct result: `PASS 3/3`. The builder does not edit this file.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
import publish as P  # noqa: E402

TEST = "src/RimMandrake/rimflow/selftest_calibration_rows_current.py"
cfg = json.load(open(os.path.join(ROOT, P.PIPELINE_TESTS), encoding="utf-8"))


def selected(path):
    return [c["test"] for c in P.pipeline_selection(ROOT, [path], cfg)]


rows = [("a registry-only change selects the calibration-rows test",
         TEST in selected("infrastructure/state/judge_calibration.json")),
        ("an evidence_gate_corpus.json change selects the calibration-rows test",
         TEST in selected("src/RimMandrake/rimflow/evidence_gate_corpus.json")),
        ("an unrelated .json change selects nothing", selected("src/RimMandrake/rimflow/mod_owner_hold_unrelated.json")
         == [])]
for name, ok in rows:
    print("%s %s" % ("ok  " if ok else "FAIL", name))
n = sum(ok for _, ok in rows)
print("%s %d/%d" % ("PASS" if n == len(rows) else "FAIL", n, len(rows)))
sys.exit(0 if n == len(rows) else 1)
