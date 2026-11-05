#!/usr/bin/env python3
"""selftest for prove_level_nodrain (PERF_SCENE_REMEASURE_BASINS_OFF_EDGE live clause A1), offline.

judge: a clean sinks-off reading at 100-rig scale passes; each bar over, a drain that still ran, a gate left open, a gate
that never read open (blind instrument), too few links, no moves, all-GC calls, the wrong map and an old deploy must not.
run(): against a fake bridge, the setting is set False for the timing and put back (also when a call raises). The C#
reader's gate expression is the one the excavation pulse hands its kernel (source check). Exit 0 = every case as expected.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prove_level_nodrain as P  # noqa: E402

ROOT = HERE.parents[2]
fails = []


def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


def perf(ms="6.902", tick="0.02761", kb="428.4", ac=20, links=100, calls=20, moves=755):
    return (f"LEVELPERF calls={calls} msAvg={ms} msMax=10.672 msPerTick={tick} allocKBAvg={kb} allocCalls={ac} gcs={20 - ac}"
            f" links={links} moves={moves} cycleTicks=250")


def g(gate=False, setting=False, edge=False, sunk="2102.9"):
    return f"DRAINGATE gate={gate} setting={setting} drainEdge={edge} sunk={sunk}"


OPEN = g(True, True)
S = (325, 325)
check("clean: sinks off, sunk flat, bars met -> PASS", P.judge(perf(), S, OPEN, g(), g())[0] == 0)
check("can-fail: 40 ms a cycle -> FAIL", P.judge(perf(ms="40", tick="0.16"), S, OPEN, g(), g())[0] == 1)
check("can-fail: msPerTick alone over -> FAIL", P.judge(perf(tick="0.2"), S, OPEN, g(), g())[0] == 1)
check("can-fail: 4 MB a cycle -> FAIL", P.judge(perf(kb="4096"), S, OPEN, g(), g())[0] == 1)
check("can-fail: water sank during the timing -> SITE, never PASS", P.judge(perf(), S, OPEN, g(), g(sunk="2110"))[0] == 2)
check("can-fail: gate still open (drain edge setter) -> SITE", P.judge(perf(), S, OPEN, g(True, False, True), g(True, False, True))[0] == 2
      and "drain edge" in P.judge(perf(), S, OPEN, g(True, False, True), g(True, False, True))[1])
check("can-fail: gate open after the timing -> SITE", P.judge(perf(), S, OPEN, g(), g(True, True))[0] == 2)
check("sanity probe: a gate that never read open is a blind instrument -> 2", P.judge(perf(), S, g(), g(), g())[0] == 2)
check("100-rig scale: links 99 -> SITE", P.judge(perf(links=99), S, OPEN, g(), g())[0] == 2)
check("no levelling work (moves 0) -> SITE", P.judge(perf(moves=0), S, OPEN, g(), g())[0] == 2)
check("GC in every call -> UNMEASURED", P.judge(perf(kb="NaN", ac=0), S, OPEN, g(), g())[0] == 2)
check("short run -> INSTRUMENT", P.judge(perf(calls=4), S, OPEN, g(), g())[0] == 2)
check("wrong map -> SITE", P.judge(perf(), (250, 250), OPEN, g(), g())[0] == 2)
check("old deploy (no DRAINGATE) -> INSTRUMENT", P.judge(perf(), S, "REFUSED: Method not found", g(), g())[0] == 2)


class Fake:
    def __init__(self, fail_at=None, v0=True):
        self.setting, self.sets, self.fail_at, self.sunk = v0, [], fail_at, 2102.9

    def call(self, tool, p):
        if tool == "jawa/map_info":
            return {"sizeX": 325, "sizeZ": 325}
        if tool == "jawa/mod_settings_field":
            if p["action"] == "set":
                self.sets.append(p["value"])
                self.setting = p["value"] == "True"
                return {"success": True}
            return {"success": True, "value": self.setting}
        m = p["method"]
        if m == self.fail_at:
            raise RuntimeError("bridge dropped")
        if m == "ProofDrainGate":
            return {"result": g(self.setting, self.setting, False, "%.1f" % self.sunk)}
        if m == "ProofLevelPerf":
            if self.setting:
                self.sunk += 2084.0                  # a draining scene: the timing ran with the gate open
            return {"result": perf(calls=int(p["args"]))}
        raise AssertionError(m)


f = Fake()
rc, line = P.run(f)
check("run: sets False then puts True back, PASS", rc == 0 and f.sets == ["False", "True"] and "PASS A1" in line)
f = Fake(fail_at="ProofLevelPerf")
try:
    P.run(f)
    raised = False
except RuntimeError:
    raised = True
check("run: a bridge failure mid-timing still puts the setting back", raised and f.sets == ["False", "True"])


class NoSet(Fake):
    def call(self, tool, p):
        if tool == "jawa/mod_settings_field" and p["action"] == "set":
            self.sets.append(p["value"])
            return {"success": False}
        return super().call(tool, p)


f = NoSet()
check("can-fail run: a set that did not take times a draining scene -> SITE, never PASS", P.run(f)[0] == 2)

src = (ROOT / "src/RimMandrake/FlowWorks/Source/RM_NorthstarProofs.cs").read_text(encoding="utf-8")
ex = (ROOT / "src/RimMandrake/FlowWorks/Source/RM_MapComponent_Excavation.cs").read_text(encoding="utf-8")
check("source: the kernel's gate is setting || AnyDrainEdge (the expression ProofDrainGate reports)",
      "flowKernel.edgeSinksEnabled = RimMandrakeFlowWorksSettings.edgeSinksEnabled || MapControls.RM_MapControls.AnyDrainEdge(map);" in ex
      and "bool setting = RimMandrakeFlowWorksSettings.edgeSinksEnabled, drainEdge = MapControls.RM_MapControls.AnyDrainEdge(map);" in src
      and '"DRAINGATE gate=" + (setting || drainEdge)' in src)
check("source: the reader's line matches the judge's pattern",
      all(k in src for k in ('" setting=" + setting', '" drainEdge=" + drainEdge', '" sunk=" + ex.SinkTransferredTotal')))

print("RESULT: %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
sys.exit(1 if fails else 0)
