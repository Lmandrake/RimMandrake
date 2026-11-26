#!/usr/bin/env python3
"""selftest_look_notes.py: the promises of design/specs/2026-11-26-look-notes-moved-pins/boundary.md.

Each t_<promise> runs one case of look_notes.py, or the walk_brief gate of maturation.py on a scratch root.
Item RIMMANDRAKE_LIST_MOVED_PINS_IN_LOOK_NOTES. Exit 0 when every promise holds.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rimflow"))
import look_notes as LN  # noqa: E402

FAILS = []


def ok(cond, what):
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def t_an_unchanged_pin_is_not_listed():
    ok(LN.run_case(LN.case_unchanged_not_listed), "an unchanged pin is not listed")


def t_a_moved_pin_is_listed_old_beside_new():
    ok(LN.run_case(LN.case_moved_listed_old_new), "a moved numeric pin is listed old -> new, with its cell")


def t_a_pin_whose_line_is_deleted_is_listed_gone():
    ok(LN.run_case(LN.case_deleted_listed_gone), "a pin whose line was deleted is listed as gone")


def t_an_empty_pin_set_says_so():
    ok(LN.run_case(LN.case_empty_says_so), "an empty pin set (empty list or no file) lists nothing and says so")


def t_a_pin_with_no_value_is_unmeasured():
    ok(LN.run_case(LN.case_no_value_unmeasured), "a pin with no stored value is listed UNMEASURED, never dropped")


def t_an_unreadable_pins_file_is_could_not_look():
    root = tempfile.mkdtemp(prefix="look_notes_st_")
    try:
        p = LN.pins_path(root, "M")
        os.makedirs(os.path.dirname(p))
        with open(p, "w") as f:
            f.write("{not json")
        n = LN.notes(root, "M")
        rc = LN.main(["M", "--root", root])
        ok(n["pins"] is None and n["why"] and rc == 2 and "COULD NOT LOOK" in LN.render("M", n),
           "a pins file that cannot be parsed is COULD NOT LOOK, exit 2, never an empty set")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_the_walk_brief_names_each_listed_pin():
    import maturation as M  # noqa: E402  the caller: the walk_brief clause of the move to his_walk
    root = tempfile.mkdtemp(prefix="look_notes_st_")
    try:
        with open(os.path.join(root, "v.txt"), "w") as f:
            f.write("shallow = 0.25\n")
        p = LN.pins_path(root, "M")
        os.makedirs(os.path.dirname(p))
        with open(p, "w") as f:
            json.dump({"pins": [{"id": "PIN_A", "said": "good", "cell": "c1", "value": "0.49",
                                 "read": {"path": "v.txt", "regex": r"shallow = ([0-9.]+)"}},
                                {"id": "PIN_B", "said": "fine", "cell": "c2", "value": "0.25",
                                 "read": {"path": "v.txt", "regex": r"shallow = ([0-9.]+)"}}]}, f)
        silent = M.walk_brief_pins_why(root, "M", "## What changed since his last look\nthe water retune\n")
        named = M.walk_brief_pins_why(root, "M", "## What changed since his last look\nPIN_A (cell c1): 0.49 -> 0.25\n")
        prefix = M.walk_brief_pins_why(root, "M", "PIN_AB moved\n")
        ok(len(silent) == 1 and "PIN_A" in silent[0] and "PIN_B" not in silent[0] and named == [] and len(prefix) == 1,
           "the walk brief gate refuses a brief silent on a moved pin, names only the moved one, and passes when it is "
           "named (a longer id is not a mention)")
        with open(p, "w") as f:
            f.write("{not json")
        bad = M.walk_brief_pins_why(root, "M", "anything")
        ok(len(bad) == 1 and "cannot be read" in bad[0], "the gate names an unreadable pins file, never reads it as none")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_pin_records_the_value_now_and_refuses_a_reader_that_finds_nothing():
    root = tempfile.mkdtemp(prefix="look_notes_st_")
    try:
        with open(os.path.join(root, "v.txt"), "w") as f:
            f.write("shallow = 0.49\n")
        good = LN.pin(root, "M", "PIN_A", "good", "c1", "v.txt", r"shallow = ([0-9.]+)")
        again = LN.pin(root, "M", "PIN_A", "good", "c1", "v.txt", r"shallow = ([0-9.]+)", value="0.50")
        bad = LN.pin(root, "M", "PIN_B", "x", "c2", "v.txt", r"deep = ([0-9.]+)")
        pins, _ = LN.read_pins(root, "M")
        ok(good[0] and again[0] and not bad[0] and len(pins) == 1 and pins[0]["value"] == "0.50",
           "pin records the value found now, a re-pin replaces its entry, and a reader that finds nothing is refused")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    t_an_unchanged_pin_is_not_listed()
    t_a_moved_pin_is_listed_old_beside_new()
    t_a_pin_whose_line_is_deleted_is_listed_gone()
    t_an_empty_pin_set_says_so()
    t_a_pin_with_no_value_is_unmeasured()
    t_an_unreadable_pins_file_is_could_not_look()
    t_the_walk_brief_names_each_listed_pin()
    t_pin_records_the_value_now_and_refuses_a_reader_that_finds_nothing()
    print("selftest_look_notes: %s" % ("ALL PASS" if not FAILS else "%d FAIL" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
