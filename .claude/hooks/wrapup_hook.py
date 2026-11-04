#!/usr/bin/env python3
"""wrapup_hook.py — SessionEnd and SubagentStop: the window's and the in-window helper's deterministic wrap-up.

AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED (owner, 2026-11-04: "We need a deterministic check that ALWAYS happens after
the agent finishes to ensure that any wrap-up occurs. Period."). The work is src/RimMandrake/rimflow/wrapup.py; this
reads the hook's stdin and builds the agent's context:

  SessionEnd    kind session: the window's clone (cwd) plus every other cwd its transcript ran in; the seat's claims
                made since the transcript's first timestamp; its bridge hold; its debts (owner session:<id>).
  SubagentStop  kind subagent, report-only: the clones the helper's own transcript ran in other than the window's.

Inside a launched unit (RM_ROLE_UNIT set) it does nothing: the unit's ExecStopPost runs the one wrap-up for that run.
Always exits 0 and prints nothing to the window; the record is wrapup's runs.jsonl.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
TRANSCRIPT_MAX_LINES = 200000


def transcript_facts(path):
    """-> (first epoch or None, [cwds]) of a JSONL transcript."""
    import calendar
    import time
    first, cwds = None, []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for n, line in enumerate(f):
                if n >= TRANSCRIPT_MAX_LINES:
                    break
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(d, dict):
                    continue
                ts = d.get("timestamp")
                if first is None and isinstance(ts, str) and len(ts) >= 19:
                    try:
                        first = calendar.timegm(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))
                    except ValueError:
                        pass
                c = d.get("cwd")
                if isinstance(c, str) and c and c not in cwds:
                    cwds.append(c)
    except OSError:
        pass
    return first, cwds


def git_top(path):
    """The clone a cwd belongs to (walk up to .git), or None."""
    p = os.path.abspath(path)
    while p and p != "/":
        if os.path.exists(os.path.join(p, ".git")):
            return p
        p = os.path.dirname(p)
    return None


def build_ctx(hook, env=None):
    env = os.environ if env is None else env
    if env.get("RM_ROLE_UNIT"):
        return None
    event = hook.get("hook_event_name") or ""
    seat = env.get("AGENT_SEAT") or env.get("RIMFLOW_SEAT")
    sid = hook.get("session_id") or env.get("CLAUDE_CODE_SESSION_ID") or "unknown"
    home = git_top(hook.get("cwd") or os.getcwd())
    if event == "SessionEnd":
        since, cwds = transcript_facts(hook.get("transcript_path") or "")
        clones = []
        for c in ([home] if home else []) + [git_top(x) for x in cwds]:
            if c and c not in clones:
                clones.append(c)
        return {"kind": "session", "key": sid, "seat": seat, "owner": "session:" + sid,
                "holder": env.get("RIMFLOW_BRIDGE_SEAT") or seat, "clones": clones, "since": since,
                "report_only": hook.get("reason") == "clear"}     # /clear: the window itself goes on
    if event == "SubagentStop":
        _, cwds = transcript_facts(hook.get("agent_transcript_path") or "")
        clones = []
        for c in (git_top(x) for x in cwds):
            if c and c != home and c not in clones:
                clones.append(c)
        return {"kind": "subagent", "key": "%s-%s" % (sid, hook.get("agent_id") or "helper"), "seat": seat,
                "owner": "subagent:%s" % (hook.get("agent_id") or sid), "holder": env.get("RIMFLOW_BRIDGE_SEAT") or seat,
                "clones": clones, "since": None}
    return None


def main():
    try:
        hook = json.load(sys.stdin)
    except ValueError:
        return 0
    ctx = build_ctx(hook if isinstance(hook, dict) else {})
    if ctx is None:
        return 0
    import wrapup
    wrapup.run(wrapup.World(), ctx)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001  a hook never breaks the window
        sys.stderr.write("wrapup_hook: %s: %s\n" % (type(e).__name__, e))
        sys.exit(0)
