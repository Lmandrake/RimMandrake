#!/usr/bin/env python3
"""selftest_regprobe.py - the register probe's cores, classifier and log reading (RIMMANDRAKE_BUILD_STEVE_REGISTER_PROBE_SEES_UPPER_HALF_LOSS).

Offline: no ssh, no Steve. Needs gcc and an AVX2 CPU here (Archmagi has both); without them the core part is UNMEASURED and
the test exits 2, never passes.
1. The shipped cores (regprobe_asm.S) run natively through regprobe_harness.c with each injection, and the shipped classifier
   (regprobe_classify.h) on planted register values: every planted fault gets its class, the clean ones stay clean.
2. Seen red on planted faults in the checker itself: three classifier mutants (upper half ignored, one low lane ignored,
   scalar compare dropped) and one core mutant (only the low 128 bits stored, the old hold test's blindness) must each
   fail part 1.
3. The log reader (testq/regprobe_log.py): fault / clean / partial / unmeasured / unproven / planted stay apart; a missing,
   stale, control-failed or inject-build log is UNMEASURED, never CLEAN; a planted fault in a clean log reads FAULT; the
   formats parsed are the ones regprobe.c writes; two reader mutants must fail.
4. fault_monitor.py: steve_read takes the probe's tail, the mirror feeds `regprobe`, and `check` fails on a
   blind installed probe.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
TESTQ = os.path.join(HERE, "..", "testq")
sys.path.insert(0, TESTQ)
import regprobe_log as RL  # noqa: E402

FAILS = []


def check(ok, msg, sink=None):
    sink = FAILS if sink is None else sink
    if sink is FAILS:
        print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        sink.append(msg)


# ---------------------------------------------------------------- 1, 2: cores and classifier

EXPECT = {
    "core_avx_clean": ("clean", 0, ""),
    "core_avx_vzeroupper": ("upper_half_loss", 16, ",".join("%d:zero" % i for i in range(16))),
    "core_avx_flip_ymm5": ("lower_half_error", 1, "5:-"),
    "core_sse_clean": ("clean", 0, ""),
    "core_sse_flip_xmm5": ("sse_error", 1, "5:-"),
    "core_gpr_clean": ("clean", 0, ""),
    "core_gpr_flip_rbx": ("scalar_error", 1, ""),
    "plant_avx_none": ("clean", 0, ""),
    "plant_upper_zero": ("upper_half_loss", 1, "3:zero"),
    "plant_upper_minus_k": ("upper_half_loss", 1, "9:minus_k"),
    "plant_upper_one_bit": ("upper_half_loss", 1, "15:other"),
    "plant_lower_lane1": ("lower_half_error", 1, "4:-"),
    "plant_lower_beats_upper": ("lower_half_error", 2, "2:-,7:other"),
    "plant_sse_upper_ignored": ("clean", 0, ""),
    "plant_sse_lane1": ("sse_error", 1, "11:-"),
    "plant_gpr_rcx": ("scalar_error", 1, ""),
}
CASE_RE = re.compile(r"^CASE (\S+) class=(\S+) nbad=(\d+) details=(\S*)$")


def run_harness(srcdir, tmp):
    """-> ({case: (class, nbad, details)}, why) building the harness from the sources in srcdir."""
    exe = os.path.join(tmp, "harness")
    r = subprocess.run(["gcc", "-O2", "-Wno-unused-function", "-o", exe, os.path.join(srcdir, "regprobe_harness.c"),
                        os.path.join(srcdir, "regprobe_asm.S")], capture_output=True, text=True)
    if r.returncode:
        return None, "build failed: " + r.stderr.strip()[-300:]
    r = subprocess.run([exe], capture_output=True, text=True, timeout=60)
    got = {}
    for line in r.stdout.splitlines():
        m = CASE_RE.match(line)
        if m:
            got[m.group(1)] = (m.group(2), int(m.group(3)), m.group(4))
    return got, "exit %d" % r.returncode


def case_checks(got, sink):
    for name, want in EXPECT.items():
        check(got.get(name) == want, "%s -> %s (got %s)" % (name, want, got.get(name)), sink)


MUTANTS = [
    ("regprobe_classify.h", "classifier ignores the upper half",
     "    if (obs[2] == e[2] && obs[3] == e[3])\n        return RP_CLEAN;", "    return RP_CLEAN;"),
    ("regprobe_classify.h", "classifier ignores low lane 1",
     "int lo = obs[0] == e[0] && obs[1] == e[1];", "int lo = obs[0] == e[0];"),
    ("regprobe_classify.h", "classifier drops the scalar compare",
     "return obs[reg] == RP_GPAT[reg] ? RP_CLEAN : RP_SCALAR;", "return RP_CLEAN;"),
    ("regprobe_asm.S", "AVX core stores only the low 128 bits",
     "    vmovdqu [r8+\\i*32], ymm\\i", "    vmovdqu [r8+\\i*32], xmm\\i"),
]


def core_part():
    if not shutil.which("gcc"):
        return "UNMEASURED: no gcc on this machine"
    with open("/proc/cpuinfo") as f:
        if " avx2" not in f.read():
            return "UNMEASURED: this CPU has no AVX2"
    srcs = ("regprobe_harness.c", "regprobe_asm.S", "regprobe_classify.h")
    with tempfile.TemporaryDirectory() as tmp:
        got, why = run_harness(HERE, tmp)
        if got is None:
            check(False, "harness builds from the shipped sources: " + why)
            return None
        case_checks(got, FAILS)
        for fname, label, old, new in MUTANTS:
            mdir = os.path.join(tmp, "m")
            shutil.rmtree(mdir, ignore_errors=True)
            os.makedirs(mdir)
            for s in srcs:
                shutil.copy(os.path.join(HERE, s), mdir)
            path = os.path.join(mdir, fname)
            with open(path) as f:
                body = f.read()
            if old not in body:
                check(False, "mutant '%s' still applies (its target text is gone: update the mutant)" % label)
                continue
            with open(path, "w") as f:
                f.write(body.replace(old, new))
            mgot, why = run_harness(mdir, tmp)
            sink = []
            if mgot is None:
                sink.append("mutant did not build: " + why)
            else:
                case_checks(mgot, sink)
            check(mgot is not None and len(sink) > 0, "RED on mutant '%s': %d case(s) fail" % (label, len(sink)))
    return None


# ---------------------------------------------------------------- 3: the log reader

T0 = RL.epoch("2026-11-20 20:00:00")


def ts(m):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(T0 + m * 60)) + "Z"


def start(m=0, build="normal", boot="2026-11-20 19:00:00Z"):
    return "%s RPSTART boot=%s logical_cpus=18 cycle=300s chunk_ms=20 avx_ms=150+150 sse_ms=50 gpr_ms=50 build=%s mode=loop pid=42 version=1" % (ts(m), boot, build)


def control(m=0, ok=1):
    return "%s RPCONTROL cpu=4 upper_seen=1 lower_seen=1 sse_seen=1 scalar_seen=1 clean_seen=%d ok=%d" % (ts(m), ok, ok)


def cyc(m, result="clean", bad="", unm=""):
    return ("%s RPCYCLE uptime_h=1.00 result=%s cpus_measured=18/18 holds=396 bad_holds=%d avx_ms=5400 sse_ms=900 gpr_ms=900 "
            "preempts=2500 bad=[%s] unmeasured=[%s] order=[3,1,0,2] secs=7.4" % (ts(m), result, bool(bad), bad, unm))


def fault(m, cpu=8, cls="upper_half_loss"):
    return ("%s RPFAULT cpu=%d path=avx class=%s reg=ymm3 detail=zero churn=1 hold_ms=20.1 preempts=19 expected=a:b:c:d "
            "observed=a:b:0:0 running=[RimWorldWin64,stevecheck,svchost:80]" % (ts(m), cpu, cls))


def reader_checks(rl, sink):
    now = T0 + 20 * 60
    w, _ = rl.verdict(rl.analyse([]), now)
    check(w == "UNMEASURED", "an empty log is UNMEASURED, not CLEAN", sink)
    good = [start(), control(), cyc(5), cyc(10), cyc(15, "partial", unm="7:avx_migrated")]
    a = rl.analyse(good)
    w, line = rl.verdict(a, now)
    check(w == "CLEAN" and a["boots"][-1]["cycles"]["clean"] == 2 and a["boots"][-1]["cycles"]["partial"] == 1,
          "clean and partial cycles under a passing control read CLEAN, counted apart (%s)" % line, sink)
    w, line = rl.verdict(rl.analyse(good + [fault(16), cyc(16, "fault", bad="8:upper_half_loss")]), now)
    check(w == "FAULT" and "upper_half_loss:1" in line and "8:1" in line,
          "a planted fault in a clean log reads FAULT with its class and CPU (%s)" % line, sink)
    w, _ = rl.verdict(rl.analyse(good), T0 + 15 * 60 + 3 * 300 + 1)
    check(w == "UNMEASURED", "a log whose newest cycle is over 3 cycles old is UNMEASURED (stale), not CLEAN", sink)
    a = rl.analyse([start(), control(ok=0), cyc(5), cyc(10, "fault", bad="2:upper_half_loss")])
    w, _ = rl.verdict(a, now)
    check(w == "UNMEASURED" and a["boots"][-1]["cycles"]["unproven"] == 2 and a["boots"][-1]["cycles"]["fault"] == 0,
          "cycles under a failed control are unproven, neither clean nor fault", sink)
    a = rl.analyse([start(), cyc(5)])
    check(rl.verdict(a, now)[0] == "UNMEASURED", "cycles with no control line are UNMEASURED", sink)
    a = rl.analyse([start(build="inject_vzeroupper"), control(), fault(5), cyc(5, "fault", bad="0:upper_half_loss")])
    w, _ = rl.verdict(a, now)
    check(w == "UNMEASURED" and a["boots"][-1]["cycles"]["planted"] == 1 and not a["boots"][-1]["faults"],
          "an inject build's faults are planted: never counted as real", sink)
    a = rl.analyse([start(), control(), cyc(5, "unmeasured", unm="0:affinity_failed")])
    check(rl.verdict(a, now)[0] == "UNMEASURED" and a["boots"][-1]["cycles"]["unmeasured"] == 1,
          "a cycle that could look at nothing is unmeasured, not clean", sink)
    a = rl.analyse(good + ["garbage line", ts(17) + " RPCYCLE result=bogus"])
    check(a["unparsed"] == 2, "lines the reader does not understand are counted", sink)
    a = rl.analyse([start(boot="2026-11-19 10:00:00Z"), control(), fault(1), cyc(1, "fault", bad="5:lower_half_error"),
                    start(2), control(2), cyc(5)])
    w, _ = rl.verdict(a, now)
    check(len(a["boots"]) == 2 and w == "CLEAN" and a["boots"][0]["cycles"]["fault"] == 1,
          "a new boot starts a new row; the old boot's fault stays in history", sink)
    a = rl.analyse([start(boot="2026-11-20 08:00:00Z"), control(), cyc(1), start(2), control(2), cyc(5)])
    check(len(a["boots"]) == 2 and a["boots"][-1]["boot"] == "2026-11-20 19:00:00",
          "two boots on one day are two rows, keyed by the whole boot stamp (date and time)", sink)
    a = rl.analyse([start(), control(), cyc(1), start(2, boot="2026-11-20 19:00:01Z"), control(2), cyc(5)])
    check(len(a["boots"]) == 1 and a["boots"][0]["starts"] == 2, "a restart whose boot= is a second off stays in its boot", sink)


READER_MUTANTS = [
    ("fault check dropped", '    if c["fault"]:\n        return "FAULT"', '    if False:\n        return "FAULT"'),
    ("control not required", 'counted = cur["build"] == "normal" and cur["control_ok"] is True', 'counted = True'),
]


def reader_part():
    reader_checks(RL, FAILS)
    with open(RL.__file__) as f:
        src = f.read()
    for label, old, new in READER_MUTANTS:
        if old not in src:
            check(False, "reader mutant '%s' still applies" % label)
            continue
        mod = types.ModuleType("rl_mutant")
        exec(compile(src.replace(old, new), "rl_mutant", "exec"), mod.__dict__)
        sink = []
        reader_checks(mod, sink)
        check(len(sink) > 0, "RED on reader mutant '%s': %d check(s) fail" % (label, len(sink)))
    with open(os.path.join(HERE, "regprobe.c")) as f:
        c = f.read()
    check(all(s in c for s in ('"RPSTART boot=%s logical_cpus=%d cycle=%.0fs', "build=%s", '"RPCONTROL cpu=%d upper_seen=%d',
                               "ok=%d", '"RPCYCLE uptime_h=%.2f result=%s', "bad=[%s] unmeasured=[%s]", '"RPFAULT cpu=%d path=%s class=%s')),
          "the formats the reader parses are the ones regprobe.c writes")
    fx = os.path.join(HERE, "..", "..", "..", "..", "infrastructure", "state", "facts", "stevedesktop_cpu_fault_2026-11-19",
                      "regprobe_red_green")
    for name, want in (("red_inject_vzeroupper.log", "planted"), ("green_normal.log", "clean")):
        p = os.path.join(fx, name)
        if not os.path.exists(p):
            check(False, "real probe output %s is in the repo" % name)
            continue
        with open(p) as f:
            a = RL.analyse(f.read().splitlines())
        b = a["boots"][-1] if a["boots"] else {"cycles": {}}
        check(a["unparsed"] == 0 and b["cycles"].get(want) == 1,
              "the reader reads the probe's real output from SteveDesktop: %s -> one %s cycle" % (name, want))


# ---------------------------------------------------------------- 4: fault_monitor wiring

def monitor_part():
    import fault_monitor as FM
    T = FM.T
    saved = T.QHOME, FM.ps
    tmp = tempfile.mkdtemp()
    try:
        T.QHOME = tmp
        FM.ps = lambda script, timeout=120: (0, "AUDIODRV 4 Stopped\nFACTS 1795200000 18 1\n"
                                                + "\n".join([start(), control(), cyc(5)]) + "\n")
        fx = FM.steve_read()
        check(fx and len(fx["rp_lines"]) == 3 and fx["audio"]["verdict"] == "OFF", "steve_read takes the probe's tail whole")
        w, _ = FM.regprobe_section(now=T0)
        check(w == "UNMEASURED", "no mirror: the probe section is UNMEASURED")
        FM.merge_mirror(fx["rp_lines"], "regprobe.log")
        w, lines = FM.regprobe_section(now=T0 + 6 * 60)
        check(w == "CLEAN", "the mirror feeds the probe section: %s" % lines[0])
        T.S.dump({"at": FM.stamp(T0 + 3600), "phase": "CLEAN"}, T.q("fault_state.json"))
        rc = FM.check(now=T0 + 3600)
        check(rc == 1, "check fails when the installed probe has gone quiet (blind)")
    finally:
        T.QHOME, FM.ps = saved
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    blind = core_part()
    reader_part()
    monitor_part()
    if blind:
        print(blind)
        return 2
    print("%d FAIL" % len(FAILS) if FAILS else "ALL OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
