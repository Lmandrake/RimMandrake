#!/usr/bin/env python3
"""The owner's presence at the machine is not an event (owner 2026-10-30, verbatim: "I really, really need you to
strip "when I come back to the machine" as an event for anything changing. It's causing so many problems and I
don't need it.").

Proves, on throwaway state only:
  bridge      `bridge idle` / `bridge take --idle-ok` succeed on a free bridge without reading any input clock: a
              fake powershell that would report him at the keyboard (idle 5 s) and that writes a marker when run is
              never invoked; the event carries a `delegated:` why and no idleProbe field
  kept        an OWNER hold, a live other holder, `--flyer` and flight wording still refuse (his deliberate acts and
              the flyer rule are not presence)
  static      no production code under src/ (testpilot excepted: another seat strips it; selftests name them as tripwires) imports idle_probe, calls
              GetLastInputInfo, or keeps an owner-return probe in the arena lane
The dispatcher (selftest_dispatcher*.py), seat_restart (selftest_seat_restart.py) and the arena lane
(selftest_arena_lane.py) each carry an observer that raises if read, in their own selftests.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))          # src/
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import cli  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def test_gate():
    g = cli._delegated_gate
    ev, ref = g(None, "BENCH", None, "deploy and restart", False)
    check(ev and not ref and ev["why"].startswith("delegated:") and set(ev) == {"why"},
          "free bridge -> delegated take, no presence field (%s)" % (ev or ref))
    check(g("BENCH", "BENCH", 1, "deploy", False)[0] is not None, "ours -> allowed")
    check(g("FOUNDRY", "BENCH", 46 * 60, "deploy", False)[0] is not None, "stale holder (45-min rule) -> allowed")
    check(g("FOUNDRY", "BENCH", 60, "deploy", False)[1] is not None, "live other holder -> refused")
    check("OWNER" in (g("OWNER", "BENCH", 99_999, "deploy", False)[1] or ""), "OWNER hold -> refused even if stale")
    check("flyer" in (g(None, "BENCH", None, "deploy", True)[1] or ""), "--flyer -> refused")
    for words in ("live test flyer flight", "watch it take off", "glider pass"):
        check(g(None, "BENCH", None, words, False)[1] is not None, "flight wording %r -> refused" % words)
    check(not hasattr(cli, "_idle_gate") and "idle_probe" not in sys.modules, "no idle gate, idle_probe never loaded")


def test_cli_end_to_end():
    tmp = tempfile.mkdtemp(prefix="rf_nopres_")
    try:
        os.makedirs(os.path.join(tmp, "items"))
        marker = os.path.join(tmp, "PS_WAS_RUN")
        fake = os.path.join(tmp, "fakeps")
        with open(fake, "w") as f:      # would say "owner at the keyboard, idle 5 s" if anything asked
            f.write("#!/bin/sh\ntouch '%s'\necho 'RMIDLE|5000|99000000|1|RimWorldWin64'\n" % marker)
        os.chmod(fake, 0o755)
        env = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
        env.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(tmp, "items"),
                   RIMFLOW_SHARED_BRIDGE=os.path.join(tmp, "shared.json"), RIMFLOW_PROBE="no-reading",
                   RIMFLOW_SEAT="BENCH", RIMFLOW_POWERSHELL=fake, PATH=tmp + os.pathsep + env.get("PATH", ""))
        os.symlink(fake, os.path.join(tmp, "powershell.exe"))

        def rf(*a):
            return subprocess.run([sys.executable, os.path.join(HERE, "cli.py")] + list(a), env=env,
                                  capture_output=True, text=True, timeout=120)
        r = rf("bridge", "idle", "--for", "deploy")
        check(r.returncode == 0 and r.stdout.startswith("TAKEABLE  delegated:"),
              "bridge idle on a free bridge -> TAKEABLE (%s)" % (r.stdout + r.stderr).strip()[:120])
        r = rf("bridge", "take", "--idle-ok", "--flyer", "--for", "deploy")
        check(r.returncode != 0, "e2e --flyer refused")
        r = rf("bridge", "take", "--idle-ok", "--for", "deploy")
        check(r.returncode == 0, "e2e delegated take succeeds with him 'at the keyboard' (%s)"
              % (r.stderr or r.stdout).strip()[:120])
        r = rf("next", "--ringed", "--peek")
        check("unrecognized" not in r.stderr and "invalid choice" not in r.stderr,
              "next --ringed still parses (%s)" % r.stderr.strip()[:120])
        check(not os.path.exists(marker), "the input-clock probe (powershell) was never run")
        evs = []
        for root, _d, files in os.walk(tmp):
            for fn in files:
                if fn.endswith(".jsonl"):
                    with open(os.path.join(root, fn)) as f:
                        evs += [json.loads(ln) for ln in f if ln.strip().startswith("{")]
        t = [e for e in evs if e.get("event") == "bridge" and e.get("state") == "taken"]
        check(t and t[-1].get("why", "").startswith("delegated:") and "idleProbe" not in t[-1],
              "the taken event carries a delegated why and no idleProbe (%s)" % (t[-1:] or "none"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


PRESENCE = re.compile(r"\bimport idle_probe\b|from rimflow import idle_probe|GetLastInputInfo|def owner_returned|"
                      r"class OwnerReturned|owner_idle_s")


def test_static():
    hits = []
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
        for fn in files:
            # selftests are skipped: they name these symbols to assert their absence (tripwire observers)
            if not (fn.endswith(".py") or fn.endswith(".json")) or fn.startswith("selftest_") or fn == "testpilot.py":
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, encoding="utf-8") as f:
                    text = f.read()
            except (OSError, UnicodeDecodeError):
                continue
            if PRESENCE.search(text):
                hits.append(os.path.relpath(path, SRC))
    check(not hits, "no presence probe left in src/ (%s)" % hits[:8])
    check(not os.path.exists(os.path.join(HERE, "idle_probe.py")), "rimflow/idle_probe.py is deleted")
    # sanity: the scan can see (instrument_traps): this file itself names the pattern
    with open(__file__, encoding="utf-8") as f:
        check(PRESENCE.search(f.read()) is not None, "control: the scanner matches a known hit")


def main():
    for t in (test_gate, test_cli_end_to_end, test_static):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    print("FAILED %d" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
