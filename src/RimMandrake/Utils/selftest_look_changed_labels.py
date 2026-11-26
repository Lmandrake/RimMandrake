#!/usr/bin/env python3
"""selftest_look_changed_labels.py: the promises of design/specs/2026-11-26-look-changed-labels/boundary.md, offline, on temp
trees. Prints one line, PASS n/n (each failed promise first, one line each). Also run by `look_changed_labels.py --selftest`."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import look_changed_labels as LC  # noqa: E402
import walk_twins  # noqa: E402

CELLS = [{"key": "1", "name": "burn front AFTER", "inputs": ["src/a.py"]}, {"key": "2", "name": "creatures", "inputs": ["src/b.py"]},
         {"key": "4", "name": "roofed grass", "inputs": ["src/d.py"]}]


def tree():
    root = tempfile.mkdtemp(prefix="look_changed_")
    for f, text in (("src/a.py", "a1"), ("src/b.py", "b1"), ("src/c.py", "c1"), ("src/d.py", "d1")):
        os.makedirs(os.path.dirname(os.path.join(root, f)), exist_ok=True)
        with open(os.path.join(root, f), "w") as fh:
            fh.write(text)
    os.makedirs(os.path.join(LC.mod_dir(root, "M"), "version"), exist_ok=True)
    return root


def walked(root, by="OWNER"):
    with open(os.path.join(LC.mod_dir(root, "M"), "version", "stage_record.json"), "w") as f:
        json.dump({"moves": [{"from": "pre_human", "to": "his_walk", "at": "2026-11-20T10:00:00-08:00", "by": "BENCH"},
                             {"from": "his_walk", "to": "in_game", "at": "2026-11-20T12:00:00-08:00", "by": by, "confirmed": {}}]}, f)


def second_save():
    """His look at save ONE (cells 1, 2, 4); then a.py changes, cell 4 goes, cell 3 joins. -> (root, label_cells of TWO)."""
    root = tree()
    LC.record("M", "ONE", CELLS, root, now="2026-11-20T09:00:00-08:00")
    walked(root)
    with open(os.path.join(root, "src/a.py"), "w") as fh:
        fh.write("a2")
    two = CELLS[:2] + [{"key": "3", "name": "scorch-fruit", "inputs": ["src/c.py"], "params": {"pods": 16}}]
    res = LC.label_cells("M", two, root)
    LC.record("M", "TWO", two, root, now="2026-11-21T09:00:00-08:00")
    return root, res


def t_a_cell_whose_inputs_changed_gets_the_label():
    root, res = second_save()
    st = walk_twins.station("SIGN 1 " + LC.sign_name("burn front AFTER", res["labels"].get("1")), "", 0, 0)
    return (res["labels"].get("1") == LC.LABEL_CHANGED and not res["why"]
            and res["last_look"] == "design/concepts/M/look_cells/ONE.json"
            and st["tag"] == "AFTER" and st["name"].startswith("[CHANGED SINCE YOUR LAST LOOK]")
            and any(ln.startswith("1 burn front AFTER: " + LC.LABEL_CHANGED) for ln in LC.show("M", "TWO", root))), (res, st)


def t_an_unchanged_cell_gets_no_label():
    _, res = second_save()
    return res["labels"].get("2") is None and "2" in res["labels"] and LC.sign_name("creatures", None) == "creatures", res


def t_a_cell_absent_from_the_last_look_is_new():
    _, res = second_save()
    return res["labels"].get("3") == LC.LABEL_NEW, res


def t_no_prior_look_labels_every_cell_new():
    r = tree()
    fresh = LC.label_cells("M", CELLS, r)                    # no record at all
    LC.record("M", "ONE", CELLS, r, now="2026-11-20T09:00:00-08:00")
    walked(r, by="DISPATCH")                                 # a move out of his_walk that is not his look
    notyet = LC.label_cells("M", CELLS, r)
    gone = LC.label_cells("M", CELLS + [{"key": "9", "name": "x", "inputs": ["src/nope.py"]}], r)
    r3 = tree()
    with open(os.path.join(LC.mod_dir(r3, "M"), "version", "stage_record.json"), "w") as f:
        f.write("{not json")
    blind = LC.label_cells("M", CELLS, r3)                   # could not look, never every cell new
    return (len(fresh["labels"]) == 3 and all(v == LC.LABEL_NEW for v in fresh["labels"].values()) and not fresh["why"]
            and all(v == LC.LABEL_NEW for v in notyet["labels"].values()) and notyet["last_look"] is None
            and blind["why"] and not blind["labels"] and gone["why"] and not gone["labels"]), (fresh, notyet, blind, gone)


def t_a_cell_removed_since_the_last_look_is_named_in_the_notes():
    root, res = second_save()
    return res["notes"] == ["removed since your last look: 4 roofed grass"] and res["notes"][0] in LC.show("M", "TWO", root), res


def main():
    tests = [t_a_cell_whose_inputs_changed_gets_the_label, t_an_unchanged_cell_gets_no_label,
             t_a_cell_absent_from_the_last_look_is_new, t_no_prior_look_labels_every_cell_new,
             t_a_cell_removed_since_the_last_look_is_named_in_the_notes]
    bad = 0
    for t in tests:
        try:
            ok, detail = t()
        except Exception as e:      # noqa: BLE001  a crash is a failed promise, named
            ok, detail = False, "%s: %s" % (type(e).__name__, e)
        if not ok:
            bad += 1
            print("FAIL %s: %s" % (t.__name__, detail))
    print("%s %d/%d" % ("FAIL" if bad else "PASS", len(tests) - bad, len(tests)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
