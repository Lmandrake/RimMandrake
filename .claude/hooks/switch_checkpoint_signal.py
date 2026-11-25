#!/usr/bin/env python3
"""PostToolUse hook: tell a DETACHED run to checkpoint when an account switch is pending
(RIMMANDRAKE_CHECKPOINT_SIGNAL_BEFORE_SOFT_SWITCH, goal 2 of RIMMANDRAKE_CHECKPOINT_HARD_STOP_NOT_KILL).

A switch (`claude-account use`) or the plan's stop SIGTERMs every Claude process. Since 2026-11-20 the plan waits for
live detached runs to end before it switches (owner: "And yes for live runs finish past, absolutely."), and stops them
only at the account's hard line, after a failed switch, or at the end of pull_drain_max_s
(design/specs/2026-11-20-account-drain/boundary.md). When the switching plan's notice (switching_plan.py write_notice ->
notice.json) reads `soft` and a switch is pending (`switch_pending`; a soft notice of a level that is only not read
says none), the run's next tool call gets one line of context: the run finishes on this account; publish
what is green as you go, so a hard-line stop loses nothing. Once per notice (its `since`) per run. The signal never
states spend, a cap or what is left of one.

An interactive window (CLAUDE_CODE_ENTRYPOINT `cli`; a `claude -p` run reads `sdk-cli`, both measured 2026-11-20 on
the live Fleet's children) is not waited for: the switch closes it and launch_fleet.ps1 -Fresh reopens it as a new
session (the 2026-11-17 03:35 stop killed the Conductor window and 3 more with no word to them). So a window gets
WINDOW_SIGNAL once per notice per session (session_id from the event, plus agent_id when the event carries one):
publish, write the handoff, launch no new subagent. Anything else (no unit, not a window) exits at once and prints
nothing; an unreadable notice is silent (this hook never breaks the run it rides in).
"""
import hashlib
import json
import os
import sys
import tempfile

SIGNAL = ("CHECKPOINT NOW (switching plan, notice since %s): an account switch is pending. It waits for running runs "
          "like you to finish; no new run starts meanwhile. Carry on and finish your work. Only if the account reaches "
          "its hard line first is every Claude process stopped, so before your next long step commit what is green "
          "and land it with `./publish -m \"...\" <explicit paths>`, then write your ledger note (state, evidence "
          "paths, one NEXT) and publish its shard; a stopped run is resumed from what you published.")
WINDOW_SIGNAL = ("SWITCH PENDING (switching plan, notice since %s): an account switch is pending. When the detached runs "
                 "end, or the account reaches its hard line, every Claude window on this machine is closed and reopened "
                 "fresh, as a new session: this conversation and any subagent it runs are not kept. Before your next "
                 "long step commit what is green and land it with `./publish -m \"...\" <explicit paths>`, write your "
                 "handoff or progress file (state, evidence paths, one NEXT), and launch no new subagent.")


def notice_path():
    d = os.environ.get("RM_SWITCH_PLAN_DIR") or "/mnt/d/ClaudeWork/rimmandrake/switching_plan"
    return os.path.join(d, "notice.json")


def switch_pending(n):
    """A switch is pending: a soft notice that is not only a level not read (2026-11-25 2:00 PM PST: one second after a
    reset the level was unread, the notice read soft, and every run and window was told a switch was pending). The
    notice's `switch_pending` decides (switching_plan.notice_of); a notice of an older writer, which has no such field,
    is pending unless it is the shape of an unread level: no drain and no level."""
    if n.get("state") != "soft":
        return False
    if "switch_pending" in n:
        return n.get("switch_pending") is True
    return bool(n.get("drain")) or n.get("pct_left") is not None


def marker_path(unit, since):
    """One file per (run, notice): created exclusively, so two tool calls at once cannot both deliver."""
    d = os.environ.get("RM_SWITCH_SIGNAL_DIR") or os.path.join(tempfile.gettempdir(), "rm_switch_signal")
    tag = hashlib.sha256(since.encode("utf-8")).hexdigest()[:16]
    return os.path.join(d, "%s.%s" % ("".join(c for c in unit if c.isalnum() or c in "-_."), tag))


def signal(unit, text=SIGNAL):
    """-> the context line owed to this run now, or None (no soft notice, already told for this notice, unreadable)."""
    try:
        with open(notice_path(), encoding="utf-8") as fh:
            n = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(n, dict) or not switch_pending(n):
        return None
    since = str(n.get("since") or n.get("at") or "")
    m = marker_path(unit, since)
    try:
        os.makedirs(os.path.dirname(m), exist_ok=True)
        os.close(os.open(m, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))   # the claim: atomic, once per notice
    except FileExistsError:
        return None
    except OSError:
        return None     # never repeat it on every call because the claim cannot be written
    return text % (since or "an unmeasured time")


def window_key(raw):
    """The marker name for an interactive window's session; None when the event names no session."""
    try:
        ev = json.loads(raw) if raw else {}
    except ValueError:
        return None
    sid = str(ev.get("session_id") or "") if isinstance(ev, dict) else ""
    return ("window-%s-%s" % (sid, ev.get("agent_id") or "")) if sid else None


def main():
    unit = os.environ.get("RM_DETACHED_UNIT")
    window = not unit and os.environ.get("CLAUDE_CODE_ENTRYPOINT") == "cli"
    if not unit and not window:
        return 0
    try:
        raw = sys.stdin.read()
    except (OSError, ValueError):
        raw = ""
    if window:
        key = window_key(raw)
        text = signal(key, WINDOW_SIGNAL) if key else None
    else:
        text = signal(unit)
    if text:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:   # noqa: BLE001 -- a hook never breaks the session it runs in
        sys.exit(0)
