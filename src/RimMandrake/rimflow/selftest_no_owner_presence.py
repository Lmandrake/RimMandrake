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
    for words in ("live test flyer flight", "watch it take off", "glider pass", "Flight test", "it flew"):
        check(g(None, "BENCH", None, words, False)[1] is not None, "flight wording %r -> refused" % words)
    check(not hasattr(cli, "_idle_gate") and not {"idle_probe", "rimflow.idle_probe"} & set(sys.modules), "no idle gate, idle_probe never loaded")


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


def test_delegated_reach():
    """Review of 9456c1f533: the delegated take keeps its kept-by-design refusals on every path it can reach."""
    import argparse
    import time
    # (a) `bridge idle --host <other>` is report-only and the delegated gate applies there too. The `_locked` half is
    # the decision on a given world (the outer half re-reads the ledger under the bridge lock first)
    calls, emitted = [], []
    keep = cli._guard_call, cli._emit
    cli._guard_call = lambda hk, a: (calls.append(a), (0, "ok"))[1]
    cli._emit = lambda ev, w, quiet=False: emitted.append(ev)
    try:
        w = argparse.Namespace(bridge_hosts={"stevedesktop": {"holder": "OWNER", "since": "x"}}, last_seen={})
        mk = lambda action, **kw: argparse.Namespace(**dict(dict(action=action, purpose="deploy", force=False,
                                                                 idle_ok=False, flyer=False), **kw))
        rc = cli._bridge_other_host_locked(mk("idle"), "BENCH", w, "stevedesktop")
        check(rc == 1 and not calls and not emitted, "idle --host: OWNER hold -> NOT TAKEABLE, nothing taken "
              "(rc=%s calls=%s emitted=%s)" % (rc, calls, emitted))
        w.bridge_hosts = {}
        del calls[:], emitted[:]
        rc = cli._bridge_other_host_locked(mk("idle"), "BENCH", w, "stevedesktop")
        check(rc == 0 and not any(c and c[0] == "take" for c in calls) and not emitted,
              "idle --host on a free bridge reports TAKEABLE and takes nothing (calls=%s)" % calls)
        del calls[:], emitted[:]
        try:
            cli._bridge_other_host_locked(mk("take", idle_ok=True, flyer=True), "BENCH", w, "stevedesktop")
            refused = False
        except SystemExit:
            refused = True
        check(refused and not emitted, "take --host --idle-ok --flyer -> refused")
    finally:
        cli._guard_call, cli._emit = keep
    # (b) his OWNER hold in the shared (cross-clone) lock: takeable only 45 min after his last deliberate interaction
    # (owner, by card 2026-10-30: "45 minutes after my last interaction, or I deliberately release it"). The hold's
    # own touch counts as one; nothing about his presence at the machine is read. A live seat hold refuses `idle`.
    tmp = tempfile.mkdtemp(prefix="rf_nopres2_")
    try:
        os.makedirs(os.path.join(tmp, "items"))
        shared = os.path.join(tmp, "shared.json")
        env = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
        env.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(tmp, "items"),
                   RIMFLOW_SHARED_BRIDGE=shared, RIMFLOW_SEAT="BENCH", RIMFLOW_OWNER_CHAT_DIRS="",
                   RIMFLOW_OWNER_ACT_STAMP=os.path.join(tmp, "OWNER_LAST_ACT.json"))

        def rf(*a):
            return subprocess.run([sys.executable, os.path.join(HERE, "cli.py")] + list(a), env=env,
                                  capture_output=True, text=True, timeout=120)

        def put(holder, age_s):
            t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - age_s))
            with open(shared, "w") as f:
                json.dump({"holder": holder, "since": t, "touched": t, "clone": "/other"}, f)
        put("OWNER", 10 * 60)
        r = rf("bridge", "take", "--idle-ok", "--for", "deploy")
        check(r.returncode != 0 and "OWNER" in (r.stderr + r.stdout), "shared OWNER hold touched 10 min ago -> "
              "--idle-ok refused (%s)" % (r.stderr + r.stdout).strip()[:120])
        r = rf("bridge", "idle", "--for", "deploy")
        check(r.returncode == 1 and r.stdout.startswith("NOT TAKEABLE"), "shared OWNER hold touched 10 min ago -> "
              "bridge idle NOT TAKEABLE (%s)" % r.stdout.strip()[:120])
        put("OWNER", 3 * 3600)
        r = rf("bridge", "idle", "--for", "deploy")
        check(r.returncode == 0 and r.stdout.startswith("TAKEABLE"), "shared OWNER hold, no interaction for 3 h -> "
              "bridge idle TAKEABLE (%s)" % r.stdout.strip()[:120])
        put("FOUNDRY", 60)
        r = rf("bridge", "idle", "--for", "deploy")
        check(r.returncode == 1 and r.stdout.startswith("NOT TAKEABLE"), "shared live FOUNDRY hold -> bridge idle "
              "NOT TAKEABLE (%s)" % r.stdout.strip()[:120])
        put("FOUNDRY", 46 * 60)
        r = rf("bridge", "idle", "--for", "deploy")
        check(r.returncode == 0, "control: shared stale FOUNDRY hold -> TAKEABLE (%s)" % r.stdout.strip()[:120])
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
            if not fn.endswith((".py", ".json", ".ps1", ".cs", ".sh")) or fn.startswith("selftest_") or fn == "testpilot.py":
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
    for t in (test_gate, test_cli_end_to_end, test_delegated_reach, test_static):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    print("FAILED %d" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
