#!/usr/bin/env python3
"""One suite component as a live-proof clause: exit 0 when its verdict is PASS, 1 otherwise (FAIL, UNMEASURED, absent).

    python3 src/RimMandrake/Utils/northstar_driver/component_proof.py --mod Wastes --chain rite_of_tipping \
        --component tipping_off_refuses_the_offer [--mock]

Runs ONLY that chain of <mod>/validation.py through the northstar driver (python.exe live, python3 with --mock) and
reads that one component from the driver's `components` records. Changes nothing on the running game beyond what the
chain itself stages and tears down. --mock is the offline half: it proves the chain and component names are real
(a live-proof line naming a component the suite no longer has would otherwise read FAIL forever); on a mock run the
component is found but not PASS, so --mock exits 0 when the component EXISTS.

Why a wrapper: a live-proof line must be a literal command a gate can read (no shell expansion), and the driver's
summary is per north-star bar, not per component.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
CLI = os.path.join(HERE, "cli.py")
SCRATCH = "/mnt/d/ClaudeWork/rimmandrake/scratch/component_proof"
TIMEOUT = 520


def win(path):
    out = subprocess.run(["wslpath", "-w", path], capture_output=True, text=True, timeout=20).stdout.strip()
    if not out:
        raise SystemExit("wslpath gave nothing for %s" % path)
    return out


def find(out_path, chain, component):
    """-> the component record from a driver --out file, or None if absent."""
    with open(out_path) as f:
        doc = json.load(f)
    for c in doc.get("components", []):
        if c.get("chain") == chain and c.get("name") == component:
            return c
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mod", required=True)
    ap.add_argument("--chain", required=True)
    ap.add_argument("--component", required=True)
    ap.add_argument("--mock", action="store_true", help="offline: exit 0 when the component exists")
    a = ap.parse_args(argv)
    plan = os.path.join(REPO, "src", "RimMandrake", a.mod, "northstar_plan.py")
    if not os.path.isfile(plan):
        print("FAIL: no plan %s" % plan)
        return 1
    os.makedirs(SCRATCH, exist_ok=True)
    # a name of this run alone: a stale or concurrent run's file can never pass for this one
    out = os.path.join(SCRATCH, "%s_%s_%d_%d.json" % (a.mod, a.chain, os.getpid(), time.time_ns()))
    if a.mock:
        argv2 = [sys.executable, CLI, "run", "--mock", "--mock-skip-site", "--mod", a.mod, "--plan", plan,
                 "--chains", a.chain, "--out", out]
    else:
        argv2 = ["python.exe", win(CLI), "run", "--mod", a.mod, "--plan", win(plan), "--chains", a.chain,
                 "--out", win(out)]
    log = out[:-len(".json")] + ".log"          # the driver's console, kept for the FAIL reader, never printed here
    print("$ " + " ".join(argv2) + "  > " + log, flush=True)
    with open(log, "w") as lf:
        rc = subprocess.run(argv2, stdin=subprocess.DEVNULL, stdout=lf, stderr=subprocess.STDOUT,
                            timeout=TIMEOUT).returncode
    if not os.path.exists(out):
        print("FAIL: the driver wrote no %s (exit %d)" % (out, rc))
        return 1
    c = find(out, a.chain, a.component)
    if c is None:
        print("FAIL: no component %s.%s in %s" % (a.chain, a.component, out))
        return 1
    v = str(c.get("verdict") or "")
    if a.mock:
        print("EXISTS %s.%s (mock verdict %s) -> %s" % (a.chain, a.component, v, out))
        return 0
    ok = v.startswith("PASS")
    print("%s %s.%s: %s -- %s -> %s" % ("PASS" if ok else "FAIL", a.chain, a.component, v,
                                        str(c.get("evidenceFull") or "")[:400], out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
