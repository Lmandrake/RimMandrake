#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_GUARD_CONTROL_COPY_RETAINED_RULES_ONE_WORD_REVERSES (parent finding 5): the exam's control
copy (designer_stage.py exam-control) may have paraphrases of the removed leaf's rule stripped by hand
(roles/designer_exam.md step 5), but control_copy_errors never compares the RETAINED leaves to the tree, so a hand edit
that reverses one ("Pawns must not climb" -> "Pawns must climb") passes. Red on base 25d20f71e0 (watched). What a strip
may change is the open design question; this test pins only what any answer must hold: a reversed retained rule is
refused, the untouched generated copy passes."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import designer_stage as DS  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def main():
    tmp = tempfile.mkdtemp(prefix="control_copy_accept_")
    try:
        d = os.path.join(tmp, "Foo")
        os.makedirs(d)
        tree = {"root": "a pit you climb out of", "leaves": [
            {"id": "l_climb", "rule": "Pawns must not climb the north wall.", "core": True},
            {"id": "l_ladder", "rule": "A ladder lets a pawn climb out.", "core": True},
            {"id": "l_flood", "rule": "The pit floods in rain.", "core": True}]}
        with open(os.path.join(d, "tree.json"), "w") as f:
            json.dump(tree, f)
        with open(os.path.join(d, "sheet.md"), "w") as f:
            f.write("# Foo\nl_climb: no north wall\nl_ladder: ladder\nl_flood: flood\n")
        ids = [x["id"] for x in tree["leaves"]]
        try:
            DS.exam_control(d, "l_flood")
        except DS.Refused as e:
            print("UNMEASURED: exam-control refused on the fixture: %s" % e)
            return 2
        check("the generated copy passes", DS.control_copy_errors(d, "l_flood", ids) == [],
              DS.control_copy_errors(d, "l_flood", ids))
        p = os.path.join(d, DS.CONTROL_DIR, "tree.json")
        with open(p) as f:
            bad = json.load(f)
        for x in bad["leaves"]:
            if x["id"] == "l_climb":
                x["rule"] = "Pawns must climb the north wall."
        with open(p, "w") as f:
            json.dump(bad, f)
        errs = DS.control_copy_errors(d, "l_flood", ids)
        check("a retained leaf's rule reversed by hand is refused", bool(errs), errs)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
