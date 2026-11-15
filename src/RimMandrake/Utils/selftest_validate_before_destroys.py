#!/usr/bin/env python3
"""No mutating bridge call under a dry run, a plan, or an unreadable keep snapshot (RIMMANDRAKE_VALIDATE_BEFORE_BRIDGE_DESTROYS).

Stub clients record every call; nothing reaches a game. Covers the Python half of the GPT bridge review's
validate-before-destroy findings:
  p1.F15 validation_core.remove_intruders with KEEP_UNREAD set sends nothing (sweep_non_colonists already refused);
  p1.F20 bridge_latency.run(do_real=False) never paints terrain;
  p1.F22 rimbridge_lineup --dry-run / no --apply never turns god mode on.
VBD_SRC=<dir> imports the three modules from another directory (how it was watched failing on the base).
"""
import os
import sys

import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "modcheck"))     # validation_core imports preconditions from there
SRC = os.environ.get("VBD_SRC") or HERE
fails = []


def load(name):
    """The module under test from SRC by file path (a module's own sys.path edits cannot swap it for another copy)."""
    spec = importlib.util.spec_from_file_location(name + "_under_test", os.path.join(SRC, name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check(ok, name, why=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else "  " + str(why)))
    if not ok:
        fails.append(name)


class Stub:
    def __init__(self, tools=()):
        self.calls = []
        self._tools = [{"name": t} for t in tools]

    def call(self, tool, params=None, *a, **k):
        self.calls.append(tool)
        if tool == "rimworld/get_cell_info":
            return {"cell": {"terrainDefName": "Soil"}}
        if tool == "rimworld/list_debug_action_children":
            return {"children": [{"label": "Muffalo"}, {"label": "Hare"}]}
        return {}

    def list_tools(self):
        return self._tools

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


WRITES = ("jawa/set_terrain", "rimworld/set_god_mode", "rimworld/execute_debug_action", "jawa/destroy_bulk",
          "jawa/destroy_pawns", "jawa/kill_hostiles")


def writes(stub):
    return [c for c in stub.calls if c in WRITES or c.startswith("jawa/destroy")]


def main():
    V = load("validation_core")
    s = Stub()
    V.KEEP_UNREAD[0] = True
    try:
        r = V.remove_intruders(s)
    except Exception as e:  # noqa: BLE001 - the base reaches _helpers().read_pawns on the stub
        r = {"error": repr(e)}
    finally:
        V.KEEP_UNREAD[0] = False
    check(s.calls == [] and r.get("removed") == [], "remove_intruders_refuses_when_keep_unreadable", (s.calls, r))

    L = load("bridge_latency")
    L.find_designator = lambda *a, **k: "architect-designator:floors:build-concrete"
    s = Stub(tools=["jawa/set_terrain"])
    try:
        L.run(s, 2, False, False)
    except Exception as e:  # noqa: BLE001 - the stub's empty replies may end run() early; only writes are judged
        print("     (run ended early on the stub: %s)" % type(e).__name__)
    check(not writes(s), "latency_bench_paints_no_terrain_without_do_real", writes(s))

    LU = load("rimbridge_lineup")
    for argv in (["--dry-run", "--apply"], ["--dry-run"], []):
        s = Stub()
        LU.resolve_endpoint = lambda *a, **k: ("127.0.0.1", 1, "tok")
        LU.RimBridge = lambda *a, **k: s
        old = sys.argv
        sys.argv = ["rimbridge_lineup.py"] + argv
        try:
            LU.main()
        except SystemExit:
            pass
        finally:
            sys.argv = old
        check(not writes(s), "lineup_sends_no_write_with_%s" % ("_".join(a.strip("-") for a in argv) or "no_apply"), writes(s))
    print("validate before destroys: %d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
