#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_REFUSE_MISSING_TOOL_SCENES_GRAFFITI_READS_READY (spec:
design/specs/2026-11-15-cheap-guards-at-every-door.md, guard SCENES_CAN_ASK, part 1). Written by the filing seat; the
builder does not edit it.

    python3 src/RimMandrake/rimflow/acceptance/guard_scene_stops_accept.py      # exit 0 and "PASS 10/10" when built

THE CONTRACT IT FIXES: `maturation.undeclared_stops(root, mod, tt, ended=None) -> {bar id: [reason, ...]}`
  For every test of the table with a `file` and an `entry` (an in-game scene), the entry function and every function
  of the same file it reaches by name (transitively; read with `ast`, nothing is imported or run) is searched for a
  `raise` whose message starts "MISSING TOOL". A bar that scene decides is listed when
    - the scene's row in design/concepts/<mod>/scenes.json (same id as the test) names no `owed_parts_item`
      -> reason "<file>:<line> stops at MISSING TOOL; declare owed_parts_item in scenes.json or build the probe", or
    - every item it names is in `ended` (default: maturation.ledger_ended) while the raise is still there
      -> reason "... its owed item <ID> is closed but the raise remains".
  A scene with a declared, still-open item is NOT listed here: owed_scene_parts already counts it.
  A file that cannot be parsed is reported under the key "__did_not_run__" and lists no bar.
  `evaluate` counts every listed bar as not runnable in `every_bar_has_a_check_that_runs`, with the reason in `observed`.
"""
import os
import sys
import tempfile
import json

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
sys.path.insert(0, RIMFLOW)
RESULTS = []
MOD = "Fix"

SCENES_PY = '''
class ExpectationFailed(Exception):
    pass

def _probe(t):
    raise ExpectationFailed("MISSING TOOL: no probe reads the breach pick")

def _deep(t):
    return _probe(t)

def scene_direct(t):
    if t:
        raise ExpectationFailed("MISSING TOOL: no tool removes an ideoligion")

def scene_helper(t):
    return _deep(t)

def scene_declared(t):
    return _probe(t)

def scene_closed(t):
    return _probe(t)

def scene_clean(t):
    """MISSING TOOL is only mentioned here, in words."""
    # MISSING TOOL in a comment
    note = "MISSING TOOL as a plain string, never raised"
    return note

def scene_other_raise(t):
    raise ExpectationFailed("SITE: no flat ground")
'''


def check(ok, what):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + what)


def main():
    try:
        import maturation as M
        fn = M.undeclared_stops
    except Exception as e:  # noqa: BLE001
        fn = None
        print("FAIL  maturation.undeclared_stops: %r" % (e,))
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "design/concepts", MOD))
        os.makedirs(os.path.join(root, "src"))
        with open(os.path.join(root, "src/validation.py"), "w") as f:
            f.write(SCENES_PY)
        with open(os.path.join(root, "src/broken.py"), "w") as f:
            f.write("def scene_broken(t:\n")
        names = ("direct", "helper", "declared", "closed", "clean", "other_raise")
        scenes = [{"id": "sc_" + n} for n in names]
        scenes[2]["owed_parts_item"] = "OPEN_PROBE_ITEM"
        scenes[3]["owed_parts_item"] = ["CLOSED_PROBE_ITEM"]
        with open(os.path.join(root, "design/concepts", MOD, "scenes.json"), "w") as f:
            json.dump({"scenes": scenes}, f)
        tests = {"sc_" + n: {"id": "sc_" + n, "kind": "live_minimal", "stage": "6", "file": "src/validation.py",
                             "entry": "scene_" + n} for n in names}
        tests["sc_broken"] = {"id": "sc_broken", "kind": "live_minimal", "stage": "6", "file": "src/broken.py",
                              "entry": "scene_broken"}
        tests["T_OFF"] = {"id": "T_OFF", "kind": "offline", "file": "src/validation.py", "command": "true"}
        tt = {"tests": tests, "bars": [{"id": "bar_" + n, "decides": ["sc_" + n]} for n in names] + [
            {"id": "bar_broken", "decides": ["sc_broken"]}, {"id": "bar_two", "decides": ["T_OFF", "sc_helper"]}]}
        try:
            out = fn(root, MOD, tt, ended={"CLOSED_PROBE_ITEM"})
        except Exception as e:  # noqa: BLE001
            out = {"__raised__": [repr(e)]}
        txt = lambda b: " ".join(out.get(b) or [])     # noqa: E731
        check("bar_direct" in out and "src/validation.py:" in txt("bar_direct") and "owed_parts_item" in txt("bar_direct"),
              "an undeclared MISSING TOOL raise in the entry lists its bar, with file:line and the fix")
        check("bar_helper" in out, "a raise two calls down from the entry is found")
        check("bar_two" in out, "every bar the scene decides is listed")
        check("bar_declared" not in out, "a declared, open owed item is left to owed_scene_parts")
        check("bar_closed" in out and "CLOSED_PROBE_ITEM" in txt("bar_closed") and "closed" in txt("bar_closed"),
              "a closed owed item with the raise still there is listed, naming the item")
        check("bar_clean" not in out, "MISSING TOOL in a docstring, comment or plain string is not a stop")
        check("bar_other_raise" not in out, "another kind of raise is not a MISSING TOOL stop")
        check("bar_broken" not in out and any("broken.py" in x for x in out.get("__did_not_run__") or []),
              "an unparseable file is did_not_run and refuses nothing")
        try:
            empty = fn(root, MOD, {"tests": {}, "bars": []}, ended=set())
        except Exception as e:  # noqa: BLE001
            empty = repr(e)
        check(empty == {}, "an empty table reads {}")
    try:
        src = open(os.path.join(RIMFLOW, "maturation.py"), encoding="utf-8").read()
    except OSError:
        src = ""
    check("undeclared_stops(" in src.split("def evaluate(", 1)[-1].split("\ndef advance(", 1)[0],
          "evaluate counts those bars not runnable")
    n = sum(RESULTS)
    print("%s %d/%d" % ("PASS" if n == len(RESULTS) else "FAIL", n, len(RESULTS)))
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
