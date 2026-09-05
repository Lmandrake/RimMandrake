#!/usr/bin/env python
"""Prove the tag -> decision round trip without touching the owner's file.

Retags two samples in the FiftyOne dataset exactly as a click in the App would,
runs the exporter, and diffs the export against creature_register.decisions.json.
A PASS means a tag change lands as a decision change in our own row shape.
Ends by restoring the two samples to their original tags.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fiftyone_sync as sync  # noqa: E402

TARGETS = {"GRimCobra": ("regen", "prio:A"), "Iguana": ("cut", None)}


def main():
    ds = sync.load_dataset()
    view = ds.match(__import__("fiftyone").ViewField("defName").is_in(list(TARGETS)))
    before = {}
    for s in view:
        before[s["defName"]] = list(s.tags)
        s.tags = [t for t in TARGETS[s["defName"]] if t]
        s["note"] = "round-trip probe"
        s.save()
    print("retagged:", {k: (before[k], [t for t in TARGETS[k] if t]) for k in before})

    sync.do_export()
    changed = sync.do_diff()

    exp = json.load(open(sync.EXPORT))["decisions"]
    ok = (exp["GRimCobra"] == {"decision": "regen", "prio": "A", "note": "round-trip probe"}
          and exp["Iguana"]["decision"] == "cut"
          and changed == len(TARGETS))
    print("ROUND TRIP:", "PASS" if ok else "FAIL")

    for s in view:                      # restore
        s.tags = before[s["defName"]]
        s["note"] = ""
        s.save()
    sync.do_export()
    print("after restore, changed rows =", sync.do_diff())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
