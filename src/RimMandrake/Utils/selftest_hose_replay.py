#!/usr/bin/env python3
# selftest-timeout: 300   (25 s on 2026-10-28, build included; a cold dotnet restore adds ~60 s)
"""Selftest of the offline hose replay harness (hose_replay.py, FlowWorks/Source/Replay/; HOSE_PERF_BUILD_OFFLINE_REPLAY_HARNESS).

Every gate is proved able to go red before its green is believed: each of the seven gates gets the fault built to break
it (ReplayTick.Fault) and must read RED on that gate, on a scenario where that fault has something to break. Then:
  - every scenario is green against the committed op-count baseline (Replay/baseline.txt) on the working tree;
  - the 16,384-cell dirty capacity cliff is visible: 16,385 changed cells overflow once into a second whole rebuild,
    16,384 do not (the instrument can see the cliff the advisory names);
  - a trace written by `gen` and replayed through `--trace` gives the same fingerprint stream as the generated scenario
    (the RMREPLAY 1 file format round-trips, so a recorded trace replays the same way).

    python3 src/RimMandrake/Utils/selftest_hose_replay.py
"""
from __future__ import annotations

import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hose_replay  # noqa: E402
from selftest_flowworks_stock import _to_windows_path  # noqa: E402

# fault -> (scenario where it has something to break, the gate that must go red)
FAULTS = [
    ("CutNoRoute", "splitjoin", "noflow"),
    ("StaleComps", "setup", "comps"),        # a lay at 600 under the comps settle 500 built, read again by settle 750
    ("Leak", "cold", "conserve"),
    ("PatchSkip", "rain", "patch"),
    ("Nondet", "cold", "determinism"),
    ("Alloc", "rain", "alloc"),
    ("DoubleWork", "aligned", "ceiling"),
]

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def gates(stdout, scenario):
    m = re.search(r"^RESULT %s (PASS|FAIL) (.*)$" % re.escape(scenario), stdout, re.M)
    if not m:
        return None, {}
    return m.group(1), dict(kv.split("=", 1) for kv in m.group(2).split())


def work(report_path, name):
    with open(report_path) as f:
        m = re.search(r"^\s+%s\s+(\d+)\s+(\d+)" % name, f.read(), re.M)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def main():
    root = tempfile.mkdtemp(prefix="selftest-", dir=hose_replay.RUNS if os.path.isdir(hose_replay.RUNS) else None)

    # 1. every scenario green on the working tree, against the committed baseline (this call builds)
    rc, out, err, d = hose_replay.run_replay(["run"], out_dir=os.path.join(root, "all"))
    if rc == 4:
        print(out[-4000:] + err[-2000:])
    check(rc == 0, "all scenarios green against Replay/baseline.txt (rc=%s)" % rc)
    for sc in ("dry", "setup", "rain", "cold", "dirty16383", "dirty16384", "dirty16385", "settings", "aligned", "splitjoin"):
        verdict, g = gates(out, sc)
        check(verdict == "PASS" and g.get("ceiling") == "green", "%s PASS with the ceiling checked (%s %s)" % (sc, verdict, g))
    if rc in (3, 4) or "RESULT" not in out:
        print(err[-3000:])
        return finish(root)

    # 2. the dirty-capacity cliff is visible
    over5, _ = work(os.path.join(d, "dirty16385.txt"), "Overflows")
    whole5, _ = work(os.path.join(d, "dirty16385.txt"), "WholeRebuilds")
    over4, _ = work(os.path.join(d, "dirty16384.txt"), "Overflows")
    whole4, _ = work(os.path.join(d, "dirty16384.txt"), "WholeRebuilds")
    check((over5, whole5) == (1, 2), "16,385 dirty cells overflow once into a second whole rebuild (overflows %s, rebuilds %s)" % (over5, whole5))
    check((over4, whole4) == (0, 1), "16,384 dirty cells patch without overflow (overflows %s, rebuilds %s)" % (over4, whole4))
    calls = re.search(r"warm HoseWorldPatch.Patch: (\d+) calls, (\d+) bytes", open(os.path.join(d, "rain.txt")).read())
    check(calls is not None and int(calls.group(1)) > 100, "the alloc gate saw warm patches in rain (%s)" % (calls and calls.group(0)))

    # 3. each gate goes red on its own fault
    for fault, sc, gate in FAULTS:
        rc, out, err, _ = hose_replay.run_replay(["run", "--scenario", sc, "--inject", fault],
                                                 out_dir=os.path.join(root, "inject-" + fault), no_build=True)
        verdict, g = gates(out, sc)
        check(rc == 1 and g.get(gate) == "RED", "inject %s on %s turns %s RED (rc=%s %s)" % (fault, sc, gate, rc, g))

    # 4. gen -> --trace round trip
    trace = os.path.join(root, "splitjoin.rmreplay")
    rc_g, out_g, err_g, _ = hose_replay.run_replay(["gen", "--scenario", "splitjoin", "--out", _to_windows_path(trace)],
                                                   out_dir=os.path.join(root, "gen"), no_build=True)
    check(rc_g == 0 and os.path.isfile(trace), "gen wrote a trace (rc=%s)" % rc_g)
    rc_t, out_t, err_t, dt = hose_replay.run_replay(["run", "--trace", _to_windows_path(trace)],
                                                    out_dir=os.path.join(root, "trace"), no_build=True)
    fp_gen = open(os.path.join(d, "splitjoin.fp")).read() if os.path.isfile(os.path.join(d, "splitjoin.fp")) else None
    fp_file = open(os.path.join(dt, "splitjoin.fp")).read() if os.path.isfile(os.path.join(dt, "splitjoin.fp")) else ""
    check(rc_t == 0 and fp_gen is not None and fp_gen == fp_file and fp_gen.count("\n") == 3000,
          "the saved trace replays to the generated scenario's fingerprints (rc=%s, %s ticks)" % (rc_t, fp_file.count("\n")))
    return finish(root)


def finish(root):
    print("reports: %s" % _to_windows_path(root))
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
