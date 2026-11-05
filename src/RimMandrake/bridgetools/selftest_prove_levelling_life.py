#!/usr/bin/env python3
"""selftest for prove_levelling_life.judge (LEVELLING_TICK_DIAGNOSE_DRY_GC_SPIKE live clause L1), offline.

The blind checker (gen 5) found the judge passed a fresh process that never ran the r17 map1 first cycle: a tiny one-rig
map with workCycles=4 maxMs=0.40 walked=2 ports=1 map=0 tick=1200 read PASS. Every probe below must go red; the r17 cold
launch readout (it4's real first=[...] shape with a sub-20 ms max) must go green.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prove_levelling_life as P  # noqa: E402


def entry(ms, walked, ports, mp, tick):
    return (f"{ms:.2f}ms(walk 0.00,links 0.00,plan 0.00,moves 0.00):gc0=0:walked={walked}:ports={ports}:links=14:"
            f"allocKB=8(walk 0,links 0):pre=0.00(hl 0.00):comp=0.00:bumps=0:hl=0:builds=0:map={mp}:tick={tick}")


def life(ms=12.5, n=8, ok=4210, bad=0, max_entry=None, passed=None):
    passed = (ok > 0 and bad == 0 and n >= 2 and ms < 20) if passed is None else passed
    return (f"LEVELLIFE prejit={ok}/{bad} prejitMs=812.3 types=31 firstFailure=[] workCycles={n} maxMs={ms:.2f} "
            f"max=[{max_entry or entry(ms, 39752, 28, 1, 48007)}] pass={passed}")


def time(*es):
    return "LEVELTIME fast=1 calls=12 meanMs=1.000 maxMs=12.50 max=[-] ownMaxMs=0 ownMax=[-] gcCalls=0 gcMs=0.0 " \
           "walkedMean=1 allocKBMean=0.0 allocKBMax=0 first=[" + " | ".join(es) + "]"


R17 = time(entry(2.42, 0, 0, 0, 48007), entry(12.50, 39752, 28, 1, 48007), entry(0.05, 0, 0, 0, 48257))
NOW = 50100

CASES = [
    # name, life, time, ticks_now, expected exit
    ("r17 cold launch, max 12.5 ms: PASS", life(), R17, NOW, 0),
    ("checker probe: tiny one-rig map0 fresh process (walked=2 ports=1 tick=1200)",
     life(0.40, 4, max_entry=entry(0.40, 2, 1, 0, 1200)), time(entry(0.40, 2, 1, 0, 1200)), 2300, 1),
    ("first working cycle on map0, r17-sized", life(), time(entry(12.5, 39752, 28, 0, 48007)), NOW, 1),
    ("first working cycle too few ports", life(), time(entry(12.5, 39752, 27, 1, 48007)), NOW, 1),
    ("first working cycle walked too little", life(), time(entry(12.5, 34999, 28, 1, 48007)), NOW, 1),
    ("another save loaded first (map0 call at tick 900)", life(),
     time(entry(2.0, 0, 0, 0, 900), entry(12.5, 39752, 28, 1, 48007)), NOW, 1),
    ("profile reset later: first entries at tick 60000", life(),
     time(entry(1.0, 39752, 28, 1, 60000)), 62000, 1),
    ("fewer than 1000 ticks since the first r17 cycle", life(), R17, 49006, 1),
    ("no working cycle in first=[]", life(), time(entry(0.1, 0, 0, 0, 48007)), NOW, 1),
    ("empty first=[]", life(), time(), NOW, 1),
    ("first r17 cycle slower than the lifetime max (readouts disagree)", life(ms=5.0),
     time(entry(12.5, 39752, 28, 1, 48007)), NOW, 1),
    ("lifetime max 28.80 ms (it4)", life(28.80), R17, NOW, 1),
    ("lifetime max exactly 20.00 ms", life(20.00), R17, NOW, 1),
    ("prejit had a failure", life(bad=1), R17, NOW, 1),
    ("prejit compiled nothing", life(ok=0), R17, NOW, 1),
    ("only 3 work cycles", life(n=3), R17, NOW, 1),
    ("readout pass=False with numbers fine", life(passed=False), R17, NOW, 1),
    # the C# readout's pass= must not be the only guard: each number is judged here even when the readout says True
    ("max 28.80 ms though readout says pass=True", life(28.80, passed=True), R17, NOW, 1),
    ("prejit failure though readout says pass=True", life(bad=1, passed=True), R17, NOW, 1),
    ("prejit compiled nothing though readout says pass=True", life(ok=0, passed=True), R17, NOW, 1),
    ("no LEVELLIFE line", "REFUSED: Type not found", R17, NOW, 2),
    ("no LEVELTIME line", life(), "", NOW, 2),
    ("no ticksGame", life(), R17, None, 2),
    ("unparseable first entry", life(), time("garbage"), NOW, 2),
]


class FakeBridge:
    """rimbridge_client stand-in that applies jawa/static_call's real argument rule (JawaBenchCompanionProbeTools.cs
    StaticCall: an empty args string is ZERO parameters; only overloads with that many parameters match) to
    RM_Levelling's one overload, ProofTiming(string). gen 8 blind checker: main() passed args='' and could never exit 0."""
    calls: list = []

    def __init__(self, **_kw):
        pass

    def connect(self):
        pass

    def call(self, tool, params):
        FakeBridge.calls.append((tool, dict(params)))
        args = params.get("args", "")
        raw = [] if not args else args.split("|")
        if tool != "jawa/static_call" or params.get("method") != "ProofTiming" or len(raw) != 1:
            return {"success": False, "error": f"No public static ProofTiming with {len(raw)} params."}
        a = raw[0].strip()
        text = life() if "life" in a else ("RESET" if "reset" in a else R17)
        return {"success": True, "result": text, "ticksGame": NOW}


def main_reads_through_static_call() -> int:
    """main() end to end on a perfect r17 readout: exit 0, and no call can reset or mis-arity the profile."""
    import types
    fake = types.ModuleType("rimbridge_client")
    fake.resolve_endpoint = lambda: ("127.0.0.1", 0, "")
    fake.RimBridge = FakeBridge
    saved = sys.modules.get("rimbridge_client")
    sys.modules["rimbridge_client"] = fake
    FakeBridge.calls = []
    try:
        rc = P.main()
    finally:
        if saved is None:
            sys.modules.pop("rimbridge_client", None)
        else:
            sys.modules["rimbridge_client"] = saved
    args = [c[1].get("args", "") for c in FakeBridge.calls]
    ok = rc == 0 and len(args) == 2 and all(a.strip() and "reset" not in a and "fast=" not in a for a in args)
    print(("ok   " if ok else "FAIL ") + f"main() through a static_call-rule fake bridge: exit {rc} (want 0), args {args}")
    return 0 if ok else 1


def main() -> int:
    bad = main_reads_through_static_call()
    for name, lt, tt, now, want in CASES:
        rc, line = P.judge(lt, tt, now)
        ok = rc == want
        bad += not ok
        print(("ok   " if ok else "FAIL ") + f"{name}: exit {rc} (want {want}) {line[:160]}")
    # the window and signature constants are what pin r17: a loosened one must be visible here
    pins = (P.R17_MAP, P.R17_MIN_PORTS, P.R17_MIN_WALKED, P.R17_TICK_LO, P.R17_TICK_HI, P.MIN_TICKS_RUN, P.MIN_CYCLES, P.BAR_MS)
    if pins != (1, 28, 35000, 48000, 48300, 1000, 4, 20.0):
        bad += 1
        print(f"FAIL r17 pins changed: {pins}")
    print(f"{len(CASES) + 2 - bad}/{len(CASES) + 2} ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
