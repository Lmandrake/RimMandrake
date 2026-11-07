#!/usr/bin/env python3
"""selftest_nulltex_probe.py - nulltex_probe.py --live's verdicts against a fake bridge (no game).
WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR: 0 null calls is no reading (exit 2), never a FAIL; a first reading of 0
is re-read once; A2 passes only on a RimThemes top caller."""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("NULLTEX_OUT", "/tmp")
import nulltex_probe as P  # noqa: E402

FAILS = []


def check(label, ok):
    print(("PASS " if ok else "FAIL ") + label)
    if not ok:
        FAILS.append(label)


def fake_bridge(readings):
    calls = []

    class RB:
        def __init__(self, **kw):
            pass

        def connect(self):
            pass

        def call(self, tool, params=None):
            calls.append(tool)
            return readings[min(len(calls), len(readings)) - 1]

    mod = types.ModuleType("rimbridge_client")
    mod.resolve_endpoint = lambda: ("127.0.0.1", 5174, "t")
    mod.RimBridge = RB
    sys.modules["rimbridge_client"] = mod
    P.time = types.SimpleNamespace(sleep=lambda s: None)
    return calls


RT = "aRandomKiwi.RimThemes.UI_BackgroundMain_Patch.Prefix"
hit = {"installed": True, "nullCalls": 40, "byCaller": [{"caller": RT, "count": 40}]}
zero = {"installed": True, "armed": True, "nullCalls": 0, "byCaller": []}
other = {"installed": True, "nullCalls": 9, "byCaller": [{"caller": "Verse.Widgets.DrawTextureFitted", "count": 9}]}

calls = fake_bridge([zero, zero])
check("0 calls twice -> exit 2 (no reading), re-read once", P.live("A1") == 2 and len(calls) == 2)
calls = fake_bridge([zero, hit])
check("0 then calls -> A1 PASS on the re-read", P.live("A1") == 0 and len(calls) == 2)
calls = fake_bridge([hit])
check("calls on the first read -> A1 PASS, no re-read", P.live("A1") == 0 and len(calls) == 1)
fake_bridge([hit])
check("RimThemes top caller -> A2 PASS", P.live("A2") == 0)
fake_bridge([other])
check("another top caller -> A2 FAIL (refuted)", P.live("A2") == 1)
fake_bridge([{"installed": False, "installError": "x"}])
check("probe not installed -> FAIL", P.live("A1") == 1)
fake_bridge([{"installed": True, "nullCalls": 3, "byCaller": [{"caller": "<no managed caller>", "count": 3}]}])
check("only an unmanaged caller -> A1 FAIL", P.live("A1") == 1)

# --- WORLD_NULLTEX_FLOOD_HUNT_NEEDS_A_STACK: the selftest and world clauses
OWN = "JawaBench.BridgeTools.JawaBenchNullTexSelftestCaller.Fire [JawaBench.BridgeTools]"
fake_bridge([{"installed": True, "armed": True, "captured": True, "frames": [OWN], "target": "t"}])
check("selftest captured -> PASS", P.live("selftest") == 0)
fake_bridge([{"installed": True, "armed": True, "captured": False, "frames": None, "error": "boom"}])
check("selftest not captured -> FAIL", P.live("selftest") == 1)
fake_bridge([{"installed": True, "armed": False, "captured": True, "frames": [OWN]}])
check("selftest while disarmed -> FAIL: nothing real would be recorded", P.live("selftest") == 1)
fake_bridge([{"installed": False, "captured": False}])
check("selftest, probe not installed -> FAIL", P.live("selftest") == 1)
fake_bridge([{"content": None}])
check("selftest with no reading -> exit 2, not a FAIL", P.live("selftest") == 2)


def stack(caller, count, world_load=0):
    return {"caller": caller, "count": count, "worldLoad": world_load}


check("split_stacks divides one caller between the two tables",
      P.split_stacks([stack("c", 9, 5)]) == ({"c": 5}, {"c": 4}))
check("is_culprit refuses the probes and an unmanaged line",
      not P.is_culprit(OWN) and not P.is_culprit("RimMandrake.NullTexTrace.NullTexTrace.Prefix [NullTexTrace]")
      and not P.is_culprit("<no managed caller above GUI.DrawTexture>") and P.is_culprit(RT))

MAP = {"mapBiome": "RM_X"}
LOADER = "aRandomKiwi.RimThemes.LoaderGM.OnGUI [RimThemes]"
world_hit = {"installed": True, "armed": True, "worldLoadsSeen": 1, "nullCalls": 9, "stacks": [stack(RT, 9, 7)]}
no_calls = {"installed": True, "armed": True, "worldLoadsSeen": 1, "nullCalls": 0, "stacks": []}


def world(readings, log):
    fake_bridge(readings)
    P.read_load_time_log = lambda: log
    return P.live("world")


check("a world-load caller -> A2 PASS", world([MAP, world_hit], ([], 9)) == 0)
check("no world-load null, a load-time culprit -> PASS, reported as such", world([MAP, no_calls], ([LOADER], 100)) == 0)
check("no map -> exit 2", world([{"error": "no map"}], ([LOADER], 100)) == 2)
check("not installed -> FAIL", world([MAP, {"installed": False}], ([LOADER], 100)) == 1)
check("nothing captured by either instrument -> exit 2, never a pass", world([MAP, no_calls], ([], 0)) == 2)
check("the load-time log unread and no calls -> exit 2", world([MAP, no_calls], (None, "not in this load")) == 2)
unmanaged = {"installed": True, "armed": True, "worldLoadsSeen": 1, "nullCalls": 3, "stacks": [stack("<no managed caller above GUI.DrawTexture>", 3)]}
check("only unmanaged frames -> A2 FAIL", world([MAP, unmanaged], ([], 3)) == 1)
probe_only = {"installed": True, "armed": True, "worldLoadsSeen": 1, "nullCalls": 1, "stacks": [stack(OWN, 1, 1)]}
check("only a probe's own frame -> A2 FAIL", world([MAP, probe_only], ([], 1)) == 1)

check("disarmed with a load-time caller -> exit 2: it did not watch the load",
      world([MAP, dict(no_calls, armed=False)], ([LOADER], 100)) == 2)


def world_line(readings, log):
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = world(readings, log)
    return code, buf.getvalue()


unnamed_world = dict(no_calls, nullCalls=3, stacks=[stack("<no managed caller above GUI.DrawTexture>", 3, 3)])
code, text = world_line([MAP, unnamed_world], ([LOADER], 3))
check("an unnamed world null is never reported as a world load with no null",
      code == 0 and "drew no null" not in text and "name no culprit" in text)
code, text = world_line([MAP, dict(no_calls, droppedStacks=4)], ([LOADER], 4))
check("dropped stacks are never reported as a world load with no null: exit 2",
      code == 2 and "drew no null" not in text and "could not read 4 call(s)" in text)
check("no load watched since install -> exit 2: a later reading says nothing about the load",
      world([MAP, dict(no_calls, worldLoadsSeen=0)], ([LOADER], 100)) == 2)
code, text = world_line([MAP, dict(world_hit, droppedStacks=2)], ([], 9))
check("a world top culprit with dropped stacks says so", code == 0 and "among the stacks kept (2 call(s) unread)" in text)
fake_bridge([dict(hit, droppedStacks=2)])
check("A2 with dropped stacks -> exit 2: the ranking is open", P.live("A2") == 2)
fake_bridge([dict(hit, recordErrors=1)])
check("A2 with a record error -> exit 2: the ranking is open", P.live("A2") == 2)
code, text = world_line([MAP, no_calls], ([LOADER], 100))
check("a clean zero says the world load drew no null", code == 0 and "drew no null" in text)

print("SELFTEST " + ("PASS" if not FAILS else "FAIL: %d" % len(FAILS)))
sys.exit(1 if FAILS else 0)
