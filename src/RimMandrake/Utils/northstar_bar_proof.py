#!/usr/bin/env python3
"""northstar_bar_proof.py -- a live-proof line that runs chosen chains of a mod's validation suite and reads named bars.

    python3 src/RimMandrake/Utils/northstar_bar_proof.py --mod TheForge --chains voices,dormancy \\
        --bar voices.voices_off_no_cue --bar dormancy.clock_off_removes_slowing
    python3 src/RimMandrake/Utils/northstar_bar_proof.py --mock ...     offline: the bars EXIST in a mock run

Live (default): the northstar driver runs under python.exe (RimBridge binds Windows loopback) with
`run --mod M --plan src/RimMandrake/<M>/northstar_plan.py --chains C --out <fresh file>`, and the verdict is the named
bars read from that run's own --out file: exit 0 when every one is PASS, 1 when any is not (FAIL, UNMEASURED, absent).
The driver's exit code is not the verdict: running some chains leaves the rest NOT_RUN. Generalises
TheForge/live_proof.py (UNPROVEN_LIVE_LEGS_TRIAGE_1) so a triage can bind an owed leg to existing bars without a
per-item wrapper. Read-only towards the repo; the suite itself stages and tears down its own test pads.

--mock: python3 driver `--mock --mock-skip-site`; exit 0 when every named bar is present in the run (any status), 1 when
one is absent. That proves the bar ids are real, offline, so a live line can never wait on a typo.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
NORTHSTAR = os.path.join(HERE, "northstar_driver", "cli.py")
sys.path.insert(0, HERE)
TIMEOUT = 520


def win(path):
    out = subprocess.run(["wslpath", "-w", path], capture_output=True, text=True, timeout=20).stdout.strip()
    if not out:
        raise SystemExit("wslpath gave nothing for %s" % path)
    return out


def bar_rows(out_path):
    """-> {bar id: (status, detail)} from a northstar --out file."""
    with open(out_path) as f:
        bars = json.load(f).get("bars", [])
    return {b.get("id"): (b.get("status"), b.get("detail", "")) for b in bars}


def verdict(rows, wanted, mock):
    """-> (ok, lines). Live: every wanted bar PASS. Mock: every wanted bar present."""
    lines, ok = [], True
    for bar in wanted:
        r = rows.get(bar)
        good = r is not None and (mock or r[0] == "PASS")
        ok = ok and good
        lines.append("%s %s -> %s" % ("ok " if good else "BAD", bar, "absent" if r is None else r[0]))
    return ok, lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mod", required=True)
    ap.add_argument("--plan", help="default src/RimMandrake/<mod>/northstar_plan.py")
    ap.add_argument("--chains", required=True, help="comma-separated chains to run")
    ap.add_argument("--bar", action="append", required=True, help="chain.component bar id; repeat")
    ap.add_argument("--mock", action="store_true", help="offline: bars must exist in a mock run")
    a = ap.parse_args(argv)
    plan = a.plan or os.path.join(REPO, "src", "RimMandrake", a.mod, "northstar_plan.py")
    if not os.path.exists(plan):
        print("no plan at %s" % plan)
        return 2
    bad_chain = [b for b in a.bar if b.split(".", 1)[0] not in a.chains.split(",")]
    if bad_chain:
        print("bar(s) outside --chains, they could never run: %s" % bad_chain)
        return 2
    if a.mock:   # offline: a private temp dir, so the check needs no agent storage root (a blind box has none)
        scratch = tempfile.mkdtemp(prefix="northstar_bar_proof_")
    else:        # live: the driver runs under python.exe and writes on the Windows side, under the agent storage root
        import rmpaths
        scratch = rmpaths.rm_str("scratch", "northstar_bar_proof")
        os.makedirs(scratch, exist_ok=True)
    # a name of this run alone: a stale or concurrent run's file can never pass for this one
    out = os.path.join(scratch, "%s_%d_%d.json" % (a.mod, os.getpid(), time.time_ns()))
    if a.mock:
        argv_ = [sys.executable, NORTHSTAR, "run", "--mock", "--mock-skip-site", "--mod", a.mod, "--plan", plan,
                 "--chains", a.chains, "--out", out]
    else:
        argv_ = ["python.exe", win(NORTHSTAR), "run", "--mod", a.mod, "--plan", win(plan), "--chains", a.chains,
                 "--out", win(scratch) + "\\" + os.path.basename(out)]
    print("$ " + " ".join(argv_), flush=True)
    try:
        rc = subprocess.run(argv_, stdin=subprocess.DEVNULL, timeout=TIMEOUT).returncode
        if not os.path.exists(out):
            print("FAIL: the driver wrote no %s (exit %d)" % (out, rc))
            return 1
        rows = bar_rows(out)
    finally:
        if a.mock:
            shutil.rmtree(scratch, ignore_errors=True)
    ok, lines = verdict(rows, a.bar, a.mock)
    print("\n".join(lines))
    print("%s (%s, driver exit %d, %s)" % ("PASS" if ok else "FAIL", "mock: bars exist" if a.mock else "live", rc, out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
