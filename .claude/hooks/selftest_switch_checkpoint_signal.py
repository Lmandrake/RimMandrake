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


def run(env, session=None):
    e = {k: v for k, v in os.environ.items()
         if k not in ("RM_DETACHED_UNIT", "RM_SWITCH_PLAN_DIR", "RM_SWITCH_SIGNAL_DIR", "CLAUDE_CODE_ENTRYPOINT")}
    e.update(env)
    ev = {"hook_event_name": "PostToolUse", "tool_name": "Bash"}
    if session:
        ev["session_id"] = session
    r = subprocess.run([sys.executable, HOOK], input=json.dumps(ev), capture_output=True, text=True, timeout=30, env=e)
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
        bare = {k: v for k, v in env.items() if k != "RM_DETACHED_UNIT"}
        rc, out = run(dict(bare, CLAUDE_CODE_ENTRYPOINT="sdk-cli"), session="s-p")
        ok(rc == 0 and out == "", "a `claude -p` run outside detached_helper (a judge, a script): silent")
        rc, out = run(bare, session="s-none")
        ok(rc == 0 and out == "", "no entrypoint and no unit (not a Claude window): silent")
        # 2026-11-20: a switch closes every window and reopens it fresh (launch_fleet.ps1 -Fresh), and the 2026-11-17
        # 03:35 stop killed the Conductor window and 3 more with no word to them. A window (entrypoint `cli`, measured
        # on the live Conductor's children; `claude -p` runs read `sdk-cli`) is told once per notice per session.
        win = dict(bare, CLAUDE_CODE_ENTRYPOINT="cli")
        rc, out = run(win, session="conductor-1")
        wctx = ((json.loads(out) if out else {}).get("hookSpecificOutput") or {}).get("additionalContext", "")
        ok(rc == 0 and "SWITCH PENDING" in wctx and "./publish" in wctx and "handoff" in wctx
           and "subagent" in wctx and "fresh" in wctx,
           "a window on a soft notice: told the switch reopens it fresh; publish, handoff, no new subagent (read %r)"
           % wctx[:120])
        ok(not re.search(r"%|USD|\$|spend|budget|remain|left of", wctx, re.I), "the window line states no spend")
        rc, out = run(win, session="conductor-1")
        ok(rc == 0 and out == "", "the same window, the same notice: told once")
        rc, out = run(win, session="hestia-2")
        ok("SWITCH PENDING" in out, "another window session is told on its own")
        # 2026-11-25 2:00 PM PST (RIMMANDRAKE_SILENCE_SWITCH_PENDING_SIGNAL_WHEN_LEVEL_ONLY_UNREAD): one second after
        # steven's reset its level was not read yet; the pass decided soft ("no new start until it is read"), no switch
        # was pending, and the hook told the Conductor SWITCH PENDING and each run CHECKPOINT NOW.
        def raw(n):
            with open(os.path.join(plan, "notice.json"), "w") as f:
                json.dump(n, f)

        def both(tag):
            o1 = run(dict(env, RM_DETACHED_UNIT="rm-detached-bench-%s-9" % tag))[1]
            o2 = run(win, session="window-%s" % tag)[1]
            return o1, o2
        raw({"account": "steven", "account_end": False, "at": "2026-11-25T14:00:00-08:00", "drain": False, "line": 52,
             "message": "switch pending: publish and finish; no new helpers", "pct_left": None,
             "since": "2026-11-25T14:00:00-08:00", "state": "soft", "warning": None,
             "why": "steven reads RESET PASSED and its last level (None) cannot prove that it is above its warning "
                    "line: no new start until it is read"})
        o1, o2 = both("reset")
        ok(o1 == "" and o2 == "", "the notice of 2:00 PM (soft, drain false, level null, older writer): no line to a "
                                  "detached run, none to a window (read %r / %r)" % (o1[:60], o2[:60]))
        for tag, n in (("stale", {"drain": False, "pct_left": 54.0}), ("follower", {"drain": True, "pct_left": None})):
            raw({"account": "steven", "account_end": False, "at": "2026-11-25T14:10:00-08:00", "line": 52,
                 "since": "2026-11-25T14:10:%02d-08:00" % len(tag), "state": "soft", "switch_pending": False,
                 "message": "the level of steven is not read yet: no new run starts until it is read; live runs go on",
                 **n})
            o1, o2 = both(tag)
            ok(o1 == "" and o2 == "", "a level-not-read notice (%s, switch_pending false): no line to a run or a window "
                                      "(read %r / %r)" % (tag, o1[:60], o2[:60]))
        for tag, n in (("drain", {"switch_pending": True}), ("drain-older-writer", {})):
            raw({"account": "steven", "account_end": False, "at": "2026-11-25T20:00:00-08:00", "drain": True,
                 "line": 52, "pct_left": 52.0, "since": "2026-11-25T20:00:%02d-08:00" % len(tag), "state": "soft",
                 "message": "draining: no new start; live runs finish on this account, then it switches", **n})
            o1, o2 = both(tag)
            ok("CHECKPOINT NOW" in o1 and "SWITCH PENDING" in o2,
               "a real pending switch (drain true, %s): the run and the window are each told" % tag)
        raw({"account": "steven", "drain": False, "pct_left": 60.0, "line": 52, "state": "soft",
             "since": "2026-11-25T21:00:00-08:00", "at": "2026-11-25T21:00:00-08:00", "switch_pending": True,
             "message": "switch pending: publish and finish; no new helpers"})
        o1, o2 = both("prepoll")
        ok("CHECKPOINT NOW" in o1 and "SWITCH PENDING" in o2,
           "a switch due before its poll (soft, drain false, switch_pending true): both are told")
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
