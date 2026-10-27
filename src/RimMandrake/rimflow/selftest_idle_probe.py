#!/usr/bin/env python3
"""Delegated bridge take (BRIDGE_IDLE_BUILD_TWENTY_MINUTE_WATCH): fake probe readings against the real rule.
Pure-function cases plus end-to-end `bridge take --idle-ok` on a throwaway ledger with a fake powershell."""
import json
import os
import stat
import subprocess
import sys
import tempfile
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import idle_probe as ip  # noqa: E402
import importlib.util  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def reading(sec):
    return ip.parse("noise\nRMIDLE|%d|123|RimWorldWin64\n" % (sec * 1000))


def main():
    spec = importlib.util.spec_from_file_location("rf_cli", os.path.join(HERE, "cli.py"))
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    gate = cli._idle_gate
    ev, ref = gate(None, "BENCH", None, "deploy and restart", False, reading(19 * 60))
    check(ref and "need 20" in ref, "idle 19 min -> refuse")
    ev, ref = gate(None, "BENCH", None, "deploy and restart", False, reading(21 * 60))
    check(ev and ref is None and ev["why"].startswith("delegated: bridge idle") and "idle_seconds=1260" in ev["idleProbe"],
          "idle 21 min -> allow, why starts 'delegated:', reading recorded")
    ev, ref = gate(None, "BENCH", None, "x", False, ip.unmeasured("boom"))
    check(ref and "UNMEASURED" in ref, "UNMEASURED -> refuse")
    for bad in ("", "RMIDLE|-1|0|", "RMIDLE|abc|1|x", "RMIDLE|5|1"):
        check(ip.parse(bad)["state"] == "UNMEASURED", "garbage %r -> UNMEASURED" % bad)
    ev, ref = gate(None, "BENCH", None, "x", True, reading(3600))
    check(ref and "flyer" in ref, "--flyer -> refuse even when idle")
    ev, ref = gate(None, "BENCH", None, "live test flyer flight on the strip", False, reading(3600))
    check(ref and "flyer" in ref, "purpose text naming flight -> refuse")
    ev, ref = gate("FOUNDRY", "BENCH", 60, "x", False, reading(3600))
    check(ref and "FOUNDRY" in ref, "held by other live seat -> refuse")
    ev, ref = gate("FOUNDRY", "BENCH", 46 * 60, "x", False, reading(3600))
    check(ev is not None, "held by stale seat (45 min rule) -> allow")
    ev, ref = gate("OWNER", "BENCH", 99999, "x", False, reading(3600))
    check(ref and "OWNER" in ref, "OWNER hold -> refuse even if stale")
    ev, ref = gate("BENCH", "BENCH", 1, "x", False, reading(3600))
    check(ev is not None, "already ours -> allow")

    # end to end through the CLI with a fake powershell (exercises parse + ledger event)
    tmp = tempfile.mkdtemp(prefix="rf_idle_")
    try:
        os.makedirs(os.path.join(tmp, "items"))
        fake = os.path.join(tmp, "fakeps")

        def setfake(sec):
            with open(fake, "w") as f:
                f.write("#!/bin/sh\n" + ("exit 5\n" if sec is None else "echo 'RMIDLE|%d|1|RimWorldWin64'\n" % (sec * 1000)))
            os.chmod(fake, 0o755)
        env = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
        env.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(tmp, "items"),
                   RIMFLOW_SHARED_BRIDGE=os.path.join(tmp, "shared.json"), RIMFLOW_PROBE="no-reading",
                   RIMFLOW_SEAT="BENCH", RIMFLOW_POWERSHELL=fake)

        def rf(*a):
            return subprocess.run([sys.executable, os.path.join(HERE, "cli.py")] + list(a), env=env,
                                  capture_output=True, text=True)
        setfake(None)
        r = rf("bridge", "take", "--idle-ok", "--for", "deploy")
        check(r.returncode != 0 and "UNMEASURED" in r.stderr + r.stdout, "e2e probe failure -> take refused")
        setfake(19 * 60)
        r = rf("bridge", "take", "--idle-ok", "--for", "deploy")
        check(r.returncode != 0, "e2e 19 min -> take refused")
        setfake(21 * 60)
        r = rf("bridge", "take", "--idle-ok", "--flyer", "--for", "deploy")
        check(r.returncode != 0, "e2e --flyer refused")
        r = rf("bridge", "take", "--idle-ok", "--for", "deploy")
        check(r.returncode == 0, "e2e 21 min -> taken (%s)" % (r.stderr or r.stdout).strip()[:80])
        evs = []
        for root, _d, files in os.walk(tmp):
            for fn in files:
                if fn.endswith(".jsonl"):
                    evs += [json.loads(l) for l in open(os.path.join(root, fn)) if l.strip().startswith("{")]
        t = [e for e in evs if e.get("event") == "bridge" and e.get("state") == "taken"]
        check(t and t[-1].get("why", "").startswith("delegated: bridge idle") and "idle_seconds=1260" in t[-1]["idleProbe"],
              "e2e ledger event carries why + probe reading")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("FAILED %d" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
