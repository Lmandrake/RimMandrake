#!/usr/bin/env python3
"""PostToolUse hook: tell a DETACHED run to checkpoint when an account switch is pending
(RIMMANDRAKE_CHECKPOINT_SIGNAL_BEFORE_SOFT_SWITCH, goal 2 of RIMMANDRAKE_CHECKPOINT_HARD_STOP_NOT_KILL).

A switch (`claude-account use`) or the plan's stop SIGTERMs every Claude process; a detached run then dies with its
green work unpublished. When the switching plan's notice (switching_plan.py write_notice -> notice.json) reads `soft`,
the run's next tool call gets one line of context: commit and publish what is green, write its ledger note, carry on.
The plan holds a switch made above the line for checkpoint_grace_s after the first soft notice (switching_plan.json).
Once per notice (its `since`) per run. The signal never states spend, a cap or what is left of one.

Outside a detached run (no RM_DETACHED_UNIT) it exits at once and prints nothing; an unreadable notice is silent
(this hook never breaks the run it rides in).
"""
import hashlib
import json
import os
import sys
import tempfile

SIGNAL = ("CHECKPOINT NOW (switching plan, notice since %s): an account switch is pending, and it stops every running "
          "Claude process within minutes. Before your next long step: commit what is green and land it with "
          "`./publish -m \"...\" <explicit paths>`, then write your ledger note (state, evidence paths, one NEXT) and "
          "publish its shard. Then carry on with the work; if this run is stopped, it is resumed from what you published.")


def notice_path():
    d = os.environ.get("RM_SWITCH_PLAN_DIR") or "/mnt/d/ClaudeWork/rimmandrake/switching_plan"
    return os.path.join(d, "notice.json")


def marker_path(unit, since):
    """One file per (run, notice): created exclusively, so two tool calls at once cannot both deliver."""
    d = os.environ.get("RM_SWITCH_SIGNAL_DIR") or os.path.join(tempfile.gettempdir(), "rm_switch_signal")
    tag = hashlib.sha256(since.encode("utf-8")).hexdigest()[:16]
    return os.path.join(d, "%s.%s" % ("".join(c for c in unit if c.isalnum() or c in "-_."), tag))


def signal(unit):
    """-> the context line owed to this run now, or None (no soft notice, already told for this notice, unreadable)."""
    try:
        with open(notice_path(), encoding="utf-8") as fh:
            n = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(n, dict) or n.get("state") != "soft":
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
    return SIGNAL % (since or "an unmeasured time")


def main():
    unit = os.environ.get("RM_DETACHED_UNIT")
    if not unit:
        return 0
    try:
        sys.stdin.read()
    except (OSError, ValueError):
        pass
    text = signal(unit)
    if text:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:   # noqa: BLE001 -- a hook never breaks the session it runs in
        sys.exit(0)
