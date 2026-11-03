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

print("SELFTEST " + ("PASS" if not FAILS else "FAIL: %d" % len(FAILS)))
sys.exit(1 if FAILS else 0)
