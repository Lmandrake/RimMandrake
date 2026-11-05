#!/usr/bin/env python3
"""Class guard for NIGHTLY_COP_FIX_RED_APGIHI_JAKI: the metronome's sense round robin cannot drift from
ops_watch.FAMILIES.

The instance: db682f0890 added `wrapup` to ops_watch.FAMILIES while metronome_phases.json kept a hand-copied
families list without it; selftest_metronome caught it only in the 03:00 nightly. The class: any hand copy of that
tuple. The guard: the shipped table names the tuple by reference ("ops_watch.FAMILIES") and load_table resolves it
from ops_watch.py's source, so adding a family there reaches the round robin with no second edit.
"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import metronome as m  # noqa: E402

FAILS = []


def ok(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)


raw = json.loads((HERE / "systemd" / "metronome_phases.json").read_text(encoding="utf-8"))
ok(raw["phases"]["sense"].get("families") == "ops_watch.FAMILIES",
   "shipped table: sense.families is the reference \"ops_watch.FAMILIES\", not a hand copy that can drift")

resolve = getattr(m, "resolve_families", None)
ok(resolve is not None, "metronome.resolve_families exists")
if resolve is not None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # the instance: ops_watch gains `wrapup`; the table is not touched
        (td / "ops_watch.py").write_text('X = 1\nFAMILIES = ("accounts", "codex",\n            "wrapup")\n')
        ok(resolve("ops_watch.FAMILIES", here=td) == ["accounts", "codex", "wrapup"],
           "instance: a family added to ops_watch.FAMILIES reaches the round robin with no table edit")
        (td / "ops_watch.py").write_text("FAMILIES = tuple(x for x in 'ab')\n")
        try:
            resolve("ops_watch.FAMILIES", here=td)
            ok(False, "a FAMILIES that is not a literal is refused by name")
        except ValueError as e:
            ok("FAMILIES" in str(e), "a FAMILIES that is not a literal is refused by name")
        try:
            resolve("ops_watch.NOPE", here=td)
            ok(False, "an unknown reference is refused by name")
        except ValueError as e:
            ok("NOPE" in str(e), "an unknown reference is refused by name")

    src = (HERE / "ops_watch.py").read_text(encoding="utf-8")
    import ast
    fams = next(list(ast.literal_eval(n.value)) for n in ast.parse(src).body
                if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "FAMILIES")
    ok(m.load_table()["phases"]["sense"]["families"] == fams,
       "load_table: the shipped sense round robin is exactly ops_watch.FAMILIES (%d families)" % len(fams))

print("selftest_metronome_families_ref: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
