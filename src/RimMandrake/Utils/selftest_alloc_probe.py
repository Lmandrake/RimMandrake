#!/usr/bin/env python3
"""Offline proof of jawa/alloc_probe (MONO_ALLOC_MEASURE_PER_TICK_ON_GAME).

    python3 src/RimMandrake/Utils/selftest_alloc_probe.py              core units + judges + every mutant (must go red)
    python3 src/RimMandrake/Utils/selftest_alloc_probe.py --no-mutants
    python3 src/RimMandrake/Utils/selftest_alloc_probe.py --judges-only   parts 2-3 only (no dotnet.exe: runs in a walled box)

1. bridgetools/AllocProbeSelfTest (net8, CoreCLR) compiles the PRODUCTION JawaBenchAllocCore.cs (a copy outside the clone)
   and runs its units: CoreCLR's exact GC.GetAllocatedBytesForCurrentThread PASSes the known-allocation calibration within
   10 % (large and small objects), a 0-counter reads BLIND, a 2x / 12 %-high counter reads OFF, 8 % low PASSes, a paired
   control cancels another thread's allocation, an absent counter or GC-hit trials read UNMEASURED, the per-system meter
   drops bytes from calls a collection landed in, landings classify explicit / implicit-slow / implicit-fast and the
   trigger line names the cause (explicit caller, or implicit).
2. prove_alloc_probe.py's judges on fixture probes (A1: BLIND threadAlloc + a PASSing heap counter holds, nothing trusted
   does not; A2: too few ticks / no RimMandrake row / a fault fail; A3: NONE fails, an implicit verdict holds).
3. The companion source registers jawa/alloc_probe and calls the core (the companion build itself is winbuild.py's).
Each MUTANT breaks one rule of the core and must turn a unit red.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
BT = os.path.join(REPO, "src", "RimMandrake", "bridgetools")
CORE = os.path.join(BT, "JawaBench.BridgeTools", "JawaBenchAllocCore.cs")
PROBE = os.path.join(BT, "JawaBench.BridgeTools", "JawaBenchAllocProbe.cs")
PROJ = os.path.join(BT, "AllocProbeSelfTest", "AllocProbeSelfTest.csproj")
UNITS = ["CalExactLargePasses", "CalExactSmallPasses", "CalBlindReadsBlind", "CalDoubleReadsOff", "CalJustOutsideTolerance",
         "CalControlSubtracted", "CalAbsentUnmeasured", "CalGcTrialsDiscarded", "ObjectBytesPerRuntime", "TrustedNeedsEveryProbe",
         "MeterGcCallsCarryNoBytes", "RowScalesToAllCalls", "ClassifyLandings", "TriggerNamesTheCause"]

MUTANTS = [
    ("tolerance_20pct", "internal const double Tolerance = 0.10;", "internal const double Tolerance = 0.20;", "CalJustOutsideTolerance"),
    ("no_control", "c.Nets.Add((d - b) - (b - a));", "c.Nets.Add(d - b);", "CalControlSubtracted"),
    ("gc_trials_kept", "if (gcCount() != g0) { c.Discarded++; continue; }", "", "CalGcTrialsDiscarded"),
    ("blind_as_off", "if (MedianRead == 0) return Blind;", "", "CalBlindReadsBlind"),
    ("gc_bytes_counted", "if (gcLanded) { GcCalls++; return; }", "if (gcLanded) GcCalls++;", "MeterGcCallsCarryNoBytes"),
    ("trusted_any_probe", "all &= c.Verdict == Pass;", "all |= c.Verdict == Pass;", "TrustedNeedsEveryProbe"),
    ("explicit_ignored", "if (!string.IsNullOrEmpty(l.ExplicitCaller)) return \"explicit\";", "", "ClassifyLandings"),
    ("unhooked_still_implicit", ': !explicitHooked ? "unknown (a GC.Collect hook failed: explicit calls may be unseen)"', "", "TriggerNamesTheCause"),
    ("mono_header_24", "long raw = payload + (mono ? 32 : 24);", "long raw = payload + 24;", "ObjectBytesPerRuntime"),
]


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def run(core_text, label):
    import winbuild
    fails = []
    fd, p = tempfile.mkstemp(prefix="AllocCore_", suffix=".cs", dir=winbuild.BUILD_ROOT)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(core_text)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_alloc_probe_%s.log" % label)
    try:
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="AllocProbeSelfTest", extra=("-p:CoreFile=" + winbuild.win(p),))
            finally:
                sys.stdout.flush()
                os.dup2(saved, 1)
                os.close(saved)
    finally:
        os.unlink(p)
    if rc:
        return {}, ["build FAILED (rc %s), log %s" % (rc, log)]
    dll = winbuild.staged_win(rec, os.path.dirname(PROJ)) + "\\bin\\Release\\net8.0\\AllocProbeSelfTest.dll"
    pr = subprocess.run([winbuild.dotnet_exe(), dll], capture_output=True, text=True, cwd="/mnt/d/Luke/dev", timeout=180)
    units = {}
    for ln in pr.stdout.splitlines():
        ln = ln.strip()
        if ln.startswith("U ") and not ln.startswith("U-count"):
            parts = ln.split(" ", 2)
            units[parts[1]] = parts[2] if len(parts) > 2 else "?"
    for u in UNITS:
        if u not in units:
            fails.append("unit %s did not run" % u)
        elif units[u] != "ok":
            fails.append("unit %s: %s" % (u, units[u][:500]))
    for u in sorted(set(units) - set(UNITS)):
        fails.append("unit %s ran but is not in UNITS" % u)
    if pr.returncode != 0 and not fails:
        fails.append("harness exit %d: %s" % (pr.returncode, pr.stderr[-400:]))
    return units, fails


def judges():
    sys.path.insert(0, BT)
    import prove_alloc_probe as P
    fails = []
    cal_ok = ["threadAlloc/large BLIND ratio=0.000", "threadAlloc/small BLIND", "threadAlloc/1MB BLIND",
              "gcTotalMemory/large PASS ratio=1.010", "gcTotalMemory/small PASS", "gcTotalMemory/1MB PASS",
              "monoUsedSize/large PASS", "monoUsedSize/small OFF", "monoUsedSize/1MB PASS"]
    good = {"calibration": cal_ok, "trusted": "gcTotalMemory", "gameTicks": 5000, "faults": 0,
            "systems": ["RimMandrake.FlowWorks.RM_MapComponent_Hoses:MapComponentTick calls=5000 bytesPerTick=812.0"],
            "trigger": "slow=2 explicit=0 implicitSlow=2 verdict=implicit (no GC.Collect call: the collector fired on allocation)"}
    cases = [
        ("A1 blind thread + trusted heap holds", P.judge_a1(good)[0], 0),
        ("A1 nothing trusted fails", P.judge_a1(dict(good, trusted=None))[0], 1),
        ("A1 thread UNMEASURED fails", P.judge_a1(dict(good, calibration=["threadAlloc/large UNMEASURED"] + cal_ok[3:]))[0], 1),
        ("A1 trusted with a non-PASS probe fails", P.judge_a1(dict(good, trusted="monoUsedSize"))[0], 1),
        ("A1 missing probe fails", P.judge_a1(dict(good, calibration=cal_ok[:-1]))[0], 1),
        ("A1 bad verdict word fails", P.judge_a1(dict(good, calibration=cal_ok[:-1] + ["monoUsedSize/1MB WEIRD"]))[0], 1),
        ("A1 thread counter trusted holds (it works: the item's own goal)", P.judge_a1(dict(good, trusted="threadAlloc", calibration=[
            "threadAlloc/large PASS", "threadAlloc/small PASS", "threadAlloc/1MB PASS", "gcTotalMemory/large OFF", "gcTotalMemory/small OFF",
            "gcTotalMemory/1MB OFF", "monoUsedSize/large OFF", "monoUsedSize/small OFF", "monoUsedSize/1MB OFF"]))[0], 0),
        ("A1 unknown trusted fails", P.judge_a1(dict(good, trusted="nonesuch"))[0], 1),
        ("A1 monoUsedSize UNMEASURED fails", P.judge_a1(dict(good, calibration=cal_ok[:-1] + ["monoUsedSize/1MB UNMEASURED"]))[0], 1),
        ("A2 good holds", P.judge_a2(good)[0], 0),
        ("A2 too few ticks fails", P.judge_a2(dict(good, gameTicks=100))[0], 1),
        ("A2 no RimMandrake row fails", P.judge_a2(dict(good, systems=["Verse.X:MapComponentTick calls=1"]))[0], 1),
        ("A2 fault fails", P.judge_a2(dict(good, faults=1))[0], 1),
        ("A2 refused start fails", P.judge_a2(dict(good, refusal="refused: no heap counter passed calibration"))[0], 1),
        ("A3 implicit verdict holds", P.judge_a3(good)[0], 0),
        ("A3 NONE fails", P.judge_a3(dict(good, trigger="NONE: no landing"))[0], 1),
        ("A3 unknown verdict fails", P.judge_a3(dict(good, trigger="slow=1 explicit=0 implicitSlow=1 verdict=unknown (a GC.Collect hook failed: explicit calls may be unseen)"))[0], 1),
        ("A3 refused start fails", P.judge_a3(dict(good, refusal="refused: no heap counter"))[0], 1),
        ("A3 no window unmeasured", P.judge_a3(dict(good, gameTicks=0))[0], 2),
    ]
    for name, got, want in cases:
        if got != want:
            fails.append("judge %s: exit %s, want %s" % (name, got, want))
    t = P.table(good)
    if "| RimMandrake.FlowWorks.RM_MapComponent_Hoses:MapComponentTick | 5000 | 812.0 |" not in t:
        fails.append("table row not rendered: " + t[-300:])
    return fails


def wiring():
    src = read(PROBE)
    need = ['"jawa/alloc_probe"', "A.Calibrate(", "A.Trusted(", "A.Row(", "A.Trigger(", "GC.GetTotalMemory(false)",
            "GetAllocatedBytesForCurrentThread", "GetMonoUsedSizeLong", "JawaBenchSafetyCore.Test"]
    return ["companion source lacks %s" % n for n in need if n not in src]


def main(argv):
    if "--judges-only" in argv:                                  # no Windows build: the runner's judges and the wiring
        fails = judges() + wiring()
        for f in fails:
            print("FAIL " + f)
        print("selftest_alloc_probe --judges-only: %s" % ("PASS" if not fails else "FAIL"))
        return 1 if fails else 0
    core = read(CORE)
    units, fails = run(core, "base")
    fails += judges() + wiring()
    print("base: %d units, %d failures" % (len(units), len(fails)))
    for f in fails:
        print("FAIL base " + f)
    if fails or "--no-mutants" in argv:
        print("selftest_alloc_probe: %s" % ("PASS (mutants skipped)" if not fails else "FAIL"))
        return 1 if fails else 0
    bad = []
    for name, old, new, want in MUTANTS:
        if core.count(old) != 1:
            bad.append("mutant %s: anchor found %d times" % (name, core.count(old)))
            continue
        u, f = run(core.replace(old, new), name)
        if not u:                                              # a build failure kills nothing: it is a harness error
            bad.append("mutant %s: no units ran (%s)" % (name, "; ".join(f)[:300]))
            continue
        got = u.get(want)
        red = got is not None and got != "ok"
        print("mutant %-20s %s (%s)" % (name, "red" if red else "SURVIVED", want))
        if not red:
            bad.append("mutant %s survived (%s: %s)" % (name, want, got or "did not run"))
    for b in bad:
        print("FAIL " + b)
    print("selftest_alloc_probe: %s" % ("PASS" if not bad else "FAIL"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
