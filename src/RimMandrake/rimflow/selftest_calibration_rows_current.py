#!/usr/bin/env python3
"""selftest_calibration_rows_current.py - the PRODUCTION calibration rows a free check can re-earn read CALIBRATED now
(RIMMANDRAKE_RECHECK_ADVANCE_CALIBRATION_TEST_PASSES_WITHOUT_ROW).

Only a CALIBRATED brief's refusal counts (refusal_contract.advisory). A row's status is tied to its brief hash, so an
edit to a brief file (maturation.py is maturation_advance's) makes status() UNTESTED in silence and every refusal of
that family advisory: the refusal-loop alarm stops seeing it. selftest_maturation.py --submit cannot catch that (it
builds its own registry), so this test reads the registry the pipeline reads (RC.calibration_path(),
RM_JUDGE_CALIBRATION honoured) and fails when a REQUIRED family has no row, or a row with a free_check (deterministic,
costs nothing to re-run) reads anything but CALIBRATED at its brief's current hash. It names the REQUIRED briefs' .py
files below, and they are pipeline_files, so ./publish's door runs it on every change to them (pipeline_tests.json).
Not seen by the door: a change to a brief's non-.py file (evidence_gate_corpus.json) or to the registry alone
(door_inputs reads .py files and same-stem .json only). A model_check family spends to recalibrate and is not held
here.

Every FAIL line carries a key: the current hash of the REQUIRED briefs, its digits spelt as letters. The door re-runs
a red test on the base commit and waves it through when the FAIL lines match there, with runs of 4+ digits blanked;
the key survives that blanking, so a brief edit on top of a red the base already had (a stale or missing row) is a new
red.

Fix a red: `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate`, then commit
infrastructure/state/judge_calibration.json with the change. Reads only; writes nothing. No model, no network."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import refusal_contract as RC  # noqa: E402

# family -> brief files its row must include, named as paths so the door's input reader (publish.door_inputs)
# ties this test to them
REQUIRED = {
    "maturation_advance": ("src/RimMandrake/rimflow/maturation.py",),
    "evidence_gate": ("src/RimMandrake/rimflow/evidence_gate.py",),
}
FIX = ("run `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate` and commit %s with the change"
       % RC.CALIBRATION_REL)
FAILS = []
DIGITS_AS_LETTERS = str.maketrans("0123456789", "ghijklmnop")


def key(files):
    """-> the briefs' current hash with no digits, so publish._norm (4+ digits -> N) cannot blank it."""
    return RC.brief_hash(list(files), RC.calibration_root()).translate(DIGITS_AS_LETTERS)


def check(name, ok, got="", files=()):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s [key %s]" % (
        got, key(files or [f for b in sorted(REQUIRED.items()) for f in b[1]]))))
    if not ok:
        FAILS.append(name)


def main():
    path = RC.calibration_path()
    if not os.path.isfile(path):
        check("the calibration registry is readable", False, "%s is not a file; %s" % (path, FIX))
        return 1
    fams = RC.load_calibration(path)["families"]
    if not fams:
        check("the calibration registry holds families", False, "%s: unparseable or empty; %s" % (path, FIX))
        return 1
    for fam, brief in sorted(REQUIRED.items()):
        row = fams.get(fam)
        check("%s has a row in the registry" % fam, isinstance(row, dict), "no row in %s; %s" % (path, FIX), brief)
        if isinstance(row, dict):
            check("%s's row's brief includes %s" % (fam, ", ".join(brief)),
                  set(brief) <= set(row.get("brief") or ()), "%r" % (row.get("brief"),), brief)
            check("%s's row has a free_check" % fam, bool(row.get("free_check")), "%r" % (row.get("free_check"),),
                  brief)
    for fam, row in sorted(fams.items()):
        if not isinstance(row, dict) or not row.get("free_check"):
            continue
        now = RC.brief_hash(row.get("brief") or [], RC.calibration_root())
        st = RC.status(fam)
        check("%s reads CALIBRATED at its brief's current hash" % fam, st == "CALIBRATED",
              "%s (recorded %s at %s, brief now %s); %s" % (st, row.get("status"), row.get("hash"), now, FIX),
              row.get("brief") or [fam])
    print("ALL PASS" if not FAILS else "%d FAILED: %s" % (len(FAILS), ", ".join(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
