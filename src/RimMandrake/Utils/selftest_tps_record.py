#!/usr/bin/env python3
"""Offline selftest of the TPS record maths (BRIDGE_TPS_REGULAR_REPORT_1, criterion C1).

    python3 src/RimMandrake/Utils/selftest_tps_record.py            Python checks + C# parity
    python3 src/RimMandrake/Utils/selftest_tps_record.py --no-cs    Python checks only

1. tps_record.py's maths against hand-worked expectations: the window, paused and speed
   normalisation, the mixed-speed exclusion, the rolling cap, the sustained low/high judgement,
   and the summary/verdict belt_watchdog prints.
2. The PRODUCTION C# (JawaBenchTpsMath.cs) built on Windows via winbuild staging into
   bridgetools/TpsMathSelfTest and fed the same vectors: every answer must match the Python port
   line for line, and the constants must agree. Without dotnet.exe this half reports SKIP and the
   run still fails loudly rather than passing on half the evidence (exit 1).
"""
import os
import subprocess
import sys
import tempfile
import json

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import tps_record as T  # noqa: E402

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


def F(v, places):
    """Mirror of JawaBenchTpsMath.F: round, then up to 4 decimals with trailing zeros trimmed."""
    if v is None:
        return "null"
    s = "%.4f" % round(v, places)
    s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ---- vectors shared by both halves ------------------------------------------------------------
C_VECTORS = [  # dTicks dReal frames paused mult changed
    (300, 5.0, 300, 0, 1, 0),      # speed 1, healthy: 60 / 60
    (150, 5.0, 300, 0, 1, 0),      # speed 1, half speed
    (900, 5.0, 300, 0, 3, 0),      # speed 3 (Fast) healthy: 180 / 180
    (850, 5.0, 300, 0, 15, 0),     # speed 4 (Ultrafast) 170 tps: dire against 900
    (850, 5.0, 300, 0, 3, 0),      # the SAME 170 tps at speed 3: fine
    (0, 5.0, 300, 300, 0, 0),      # fully paused (multiplier 0)
    (120, 5.0, 300, 160, 1, 0),    # paused for 53% of frames -> paused
    (240, 5.0, 300, 100, 1, 0),    # paused 33% -> still a run sample
    (600, 5.0, 300, 0, 3, 1),      # speed changed mid-window -> mixed
    (1800, 5.0, 300, 0, 6, 0),     # Superfast healthy
    (2000, 5.0, 300, 0, 6, 0),     # above target (the "nothing happening" 12x jump)
    (0, 0.0, 0, 0, 1, 0),          # degenerate window
]
W_VECTORS = [(5.0, 300), (60.0, 0), (60.5, 10), (0.0, 0), (5.0, -40)]
M_VECTORS = [[], [5], [3, 1, 2], [4, 1, 3, 2], [60, 59.5, 12, 61]]
S_VECTORS = [
    [0.5] * 5,                     # too few -> unknown
    [0.5] * 6,                     # low
    [1.0] + [0.4] * 6,             # low (only the tail counts)
    [0.4] * 5 + [0.9],             # one recovery -> ok
    [1.3] * 6,                     # high
    [1.0] * 8,                     # ok
    [0.6] * 6,                     # exactly LOW_RATIO is not below -> ok
]
R_VECTORS = [(0, 2_000_000), (1_048_000, 100), (1_048_500, 100), (1_048_576, 1), (10, 10)]


def py_lines():
    out = ["K " + " ".join([F(T.CADENCE_SECONDS, 4), F(T.MAX_WINDOW_SECONDS, 4), F(T.TICKS_PER_SECOND_AT_SPEED1, 4),
                            F(T.PAUSED_SHARE, 4), str(T.ROTATE_BYTES), str(T.RING_CAPACITY), str(T.SUSTAINED_SAMPLES),
                            F(T.LOW_RATIO, 4), F(T.HIGH_RATIO, 4)])]
    for v in C_VECTORS:
        r = T.compute(*v[:5], speed_changed=bool(v[5]))
        out.append("C %s %s %s %s %s" % (F(r["tps"], 2), F(r["target"], 2), F(r["ratio"], 3), F(r["pausedFrac"], 3), r["state"]))
    for d_real, d_ticks in W_VECTORS:
        out.append("W %d" % (1 if T.window_usable(d_real, d_ticks) else 0))
    for xs in M_VECTORS:
        out.append("M " + F(T.median(xs), 3))
    for xs in S_VECTORS:
        out.append("S " + T.sustained(xs))
    for cur, ln in R_VECTORS:
        out.append("R %d" % (1 if T.should_rotate(cur, ln) else 0))
    return out


def cs_input():
    rows = ["K"]
    rows += ["C %d %s %d %d %s %d" % v for v in C_VECTORS]
    rows += ["W %s %d" % v for v in W_VECTORS]
    rows += ["M " + " ".join(str(x) for x in xs) for xs in M_VECTORS]
    rows += ["S " + " ".join(str(x) for x in xs) for xs in S_VECTORS]
    rows += ["R %d %d" % v for v in R_VECTORS]
    return "\n".join(rows) + "\n"


def python_checks():
    c = lambda *v: T.compute(*v[:5], speed_changed=bool(v[5]))  # noqa: E731
    r = c(300, 5.0, 300, 0, 1, 0)
    check(r["tps"] == 60 and r["target"] == 60 and r["ratio"] == 1 and r["state"] == "run", "speed-1 healthy %r" % r)
    check(c(150, 5.0, 300, 0, 1, 0)["ratio"] == 0.5, "half speed ratio")
    r4, r3 = c(850, 5.0, 300, 0, 15, 0), c(850, 5.0, 300, 0, 3, 0)
    check(r4["tps"] == r3["tps"] == 170, "same tps both speeds")
    check(r4["ratio"] < T.LOW_RATIO < r3["ratio"], "170 tps is low at speed 4, fine at speed 3: %r %r" % (r4, r3))
    check(c(0, 5.0, 300, 300, 0, 0)["state"] == "paused", "multiplier 0 -> paused")
    check(c(120, 5.0, 300, 160, 1, 0)["state"] == "paused", "53% paused frames -> paused")
    check(c(240, 5.0, 300, 100, 1, 0)["state"] == "run", "33% paused frames -> run")
    check(c(600, 5.0, 300, 0, 3, 1)["state"] == "mixed", "speed change -> mixed")
    check(c(0, 0.0, 0, 0, 1, 0)["tps"] == 0, "zero window must not divide by zero")
    check(T.window_usable(5.0, 300) and not T.window_usable(61.0, 300) and not T.window_usable(5.0, -1),
          "window_usable gates load gaps and tick resets")
    check(T.median([4, 1, 3, 2]) == 2.5 and T.median([]) is None, "median")
    check([T.sustained(x) for x in S_VECTORS] == ["unknown", "low", "low", "ok", "high", "ok", "ok"], "sustained")
    check(T.should_rotate(1_048_500, 100) and not T.should_rotate(0, 2_000_000), "rotation cap (never rotate an empty file)")

    # summary / verdict over a fixture record
    now = 1_760_000_000.0

    def row(age, tps, mult, state="run", speed="Normal"):
        import time as _t
        utc = _t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime(now - age))
        tgt = 60.0 * mult
        return {"utc": utc, "tps": tps, "target": tgt, "ratio": (tps / tgt) if tgt else None, "state": state,
                "speed": speed, "frameMaxMs": 40, "gc0": 1}

    low = [row(5 * i, 25, 1) for i in range(8, 0, -1)]
    s = T.summarise(low, now=now)
    lvl, det = T.verdict(s)
    check(lvl == "WARN" and "SUSTAINED LOW" in det, "sustained low verdict: %s %s" % (lvl, det))
    fast_ok = [row(5 * i, 170, 3, speed="Fast") for i in range(8, 0, -1)]
    lvl, det = T.verdict(T.summarise(fast_ok, now=now))
    check(lvl == "OK", "170 tps at speed 3 must be OK: %s %s" % (lvl, det))
    ultra = [row(5 * i, 170, 15, speed="Ultrafast") for i in range(8, 0, -1)]
    lvl, det = T.verdict(T.summarise(ultra, now=now))
    check(lvl == "WARN" and "LOW" in det, "170 tps at speed 4 must WARN: %s %s" % (lvl, det))
    paused = [row(5 * i, 0, 0, state="paused", speed="Paused") for i in range(8, 0, -1)]
    lvl, det = T.verdict(T.summarise(paused, now=now))
    check(lvl == "INFO" and "paused" in det, "all-paused is INFO, never low: %s %s" % (lvl, det))
    old = [row(3600, 60, 1)]
    lvl, det = T.verdict(T.summarise(old, now=now))
    check(lvl == "INFO", "stale record is INFO: %s %s" % (lvl, det))
    lvl, det = T.verdict(T.summarise([], now=now))
    check(lvl == "UNKNOWN", "empty record is UNKNOWN: %s" % lvl)

    # reader: rotation order + malformed lines are counted
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "tps.1.jsonl"), "w") as fh:
            fh.write(json.dumps({"n": 1}) + "\n")
        with open(os.path.join(d, "tps.jsonl"), "w") as fh:
            fh.write(json.dumps({"n": 2}) + "\nnot json\n")
        rows, bad = T.read_samples(d)
        check([r["n"] for r in rows] == [1, 2] and bad == 1, "reader order/malformed: %r %d" % (rows, bad))


def cs_parity():
    import winbuild
    proj = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "TpsMathSelfTest")
    rc, rec = winbuild.stage_build(os.path.join(proj, "TpsMathSelfTest.csproj"), stage_name="TpsMathSelfTest")
    if rc:
        FAILS.append("C# parity harness build FAILED (rc %s)" % rc)
        return
    dll = winbuild.staged_win(rec, proj) + "\\bin\\Release\\net8.0\\TpsMathSelfTest.dll"
    p = subprocess.run([winbuild.dotnet_exe(), dll], input=cs_input(), capture_output=True, text=True,
                       cwd="/mnt/d/Luke/dev")
    got = [ln.strip() for ln in p.stdout.splitlines() if ln.strip()]
    want = py_lines()
    if p.returncode != 0:
        FAILS.append("C# harness exit %d: %s" % (p.returncode, p.stderr[-400:]))
    if len(got) != len(want):
        FAILS.append("C# answered %d lines, Python %d" % (len(got), len(want)))
    for i, (g, w) in enumerate(zip(got, want)):
        check(g == w, "C#/Python disagree on line %d: C# %r  py %r" % (i, g, w))
    print("C# parity: %d/%d lines identical" % (sum(1 for g, w in zip(got, want) if g == w), len(want)))


def main(argv):
    python_checks()
    print("python checks: %s" % ("PASS" if not FAILS else "FAIL"))
    if "--no-cs" in argv:
        print("C# parity: SKIPPED by --no-cs")
    elif not any(os.path.exists(c) for c in ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe",
                                               "/mnt/c/Program Files/dotnet/dotnet.exe"]):
        FAILS.append("C# parity UNMEASURED: no dotnet.exe on this machine (pass --no-cs to accept Python-only)")
    else:
        cs_parity()
    for f in FAILS:
        print("FAIL " + f)
    print("selftest_tps_record: %s (%d failures)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
