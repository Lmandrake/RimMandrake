#!/usr/bin/env python3
"""selftest for switch_checkpoint_signal.py (RIMMANDRAKE_CHECKPOINT_SIGNAL_BEFORE_SOFT_SWITCH): a detached run is told
once per soft notice to checkpoint; nothing outside a detached run, on a normal or stop notice, or on an unreadable
notice; the signal states no spend. Runs the hook as Claude Code does (a subprocess, the event JSON on stdin).
    python3 .claude/hooks/selftest_switch_checkpoint_signal.py      exit 0 when every check prints PASS"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "switch_checkpoint_signal.py")
FAILS = []


def ok(cond, what):
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def run(env):
    e = {k: v for k, v in os.environ.items() if k not in ("RM_DETACHED_UNIT", "RM_SWITCH_PLAN_DIR", "RM_SWITCH_SIGNAL_DIR")}
    e.update(env)
    r = subprocess.run([sys.executable, HOOK], input='{"hook_event_name": "PostToolUse", "tool_name": "Bash"}',
                       capture_output=True, text=True, timeout=30, env=e)
    return r.returncode, r.stdout.strip()


def main():
    if not os.path.exists(HOOK):
        ok(False, "the hook exists")
        return 1
    tmp = tempfile.mkdtemp(prefix="switch_signal_")
    try:
        plan, marks = os.path.join(tmp, "plan"), os.path.join(tmp, "marks")
        os.makedirs(plan)
        env = {"RM_SWITCH_PLAN_DIR": plan, "RM_SWITCH_SIGNAL_DIR": marks, "RM_DETACHED_UNIT": "rm-detached-bench-x-1"}

        def notice(state, since):
            with open(os.path.join(plan, "notice.json"), "w") as f:
                json.dump({"state": state, "since": since, "at": since, "pct_left": 3, "line": 2,
                           "message": "switch pending: publish and finish; no new helpers"}, f)
        rc, out = run(env)
        ok(rc == 0 and out == "", "no notice file: silent, exit 0")
        notice("soft", "2026-11-18T14:00:00-08:00")
        rc, out = run(env)
        ctx = ((json.loads(out) if out else {}).get("hookSpecificOutput") or {}).get("additionalContext", "")
        ok(rc == 0 and "CHECKPOINT NOW" in ctx and "./publish" in ctx and "ledger note" in ctx,
           "a soft notice: the detached run is told to checkpoint and publish (read %r)" % ctx[:80])
        ok(not re.search(r"%|USD|\$|spend|budget|remain|left of", ctx, re.I),
           "the signal states no spend, cap or remainder")
        # 2026-11-20 (live runs finish past the soft line): the signal never says the run is about to be stopped
        ok("within minutes" not in ctx and "finish" in ctx and "hard line" in ctx,
           "the signal says the run finishes on its account and names the hard line (read %r)" % ctx[:300])
        rc, out = run(env)
        ok(rc == 0 and out == "", "the same notice: told once, not on every tool call")
        notice("soft", "2026-11-18T15:00:00-08:00")
        rc, out = run(env)
        ok("CHECKPOINT NOW" in out, "a new soft notice (a new since): told again")
        rc, out = run(dict(env, RM_DETACHED_UNIT="rm-detached-bench-y-2"))
        ok("CHECKPOINT NOW" in out, "another detached run is told on its own")
        # Codex review 2026-11-18: two tool calls at once on one notice deliver it once
        notice("soft", "2026-11-18T15:30:00-08:00")
        import concurrent.futures as CF
        with CF.ThreadPoolExecutor(8) as ex:
            outs = list(ex.map(lambda _: run(dict(env, RM_DETACHED_UNIT="rm-detached-bench-race-3"))[1], range(8)))
        ok(sum("CHECKPOINT NOW" in o for o in outs) == 1,
           "eight concurrent tool calls on one notice: exactly one signal (read %d)" % sum("CHECKPOINT NOW" in o for o in outs))
        rc, out = run({k: v for k, v in env.items() if k != "RM_DETACHED_UNIT"})
        ok(rc == 0 and out == "", "not a detached run (a window, the Conductor): silent")
        for st in ("none", "stop"):
            notice(st, "2026-11-18T16:00:00-08:00")
            rc, out = run(env)
            ok(rc == 0 and out == "", "a %s notice: silent" % st)
        with open(os.path.join(plan, "notice.json"), "w") as f:
            f.write("{not json")
        rc, out = run(env)
        ok(rc == 0 and out == "", "an unreadable notice: silent, exit 0")
        settings = json.load(open(os.path.join(os.path.dirname(HOOK), "..", "settings.json")))
        wired = [h.get("command", "") for g in settings.get("hooks", {}).get("PostToolUse", [])
                 for h in g.get("hooks", [])]
        ok(any("switch_checkpoint_signal.py" in c for c in wired), "settings.json wires it as a PostToolUse hook")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
