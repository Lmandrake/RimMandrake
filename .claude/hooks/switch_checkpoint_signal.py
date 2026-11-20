#!/usr/bin/env python3
"""PostToolUse hook: tell a DETACHED run to checkpoint when an account switch is pending
(RIMMANDRAKE_CHECKPOINT_SIGNAL_BEFORE_SOFT_SWITCH, goal 2 of RIMMANDRAKE_CHECKPOINT_HARD_STOP_NOT_KILL).

A switch (`claude-account use`) or the plan's stop SIGTERMs every Claude process. Since 2026-11-20 the plan waits for
live detached runs to end before it switches (owner: "And yes for live runs finish past, absolutely."), and stops them
only at the account's hard line, after a failed switch, or at the end of pull_drain_max_s
(design/specs/2026-11-20-account-drain/boundary.md). When the switching plan's notice (switching_plan.py write_notice ->
notice.json) reads `soft`, the run's next tool call gets one line of context: the run finishes on this account; publish
what is green as you go, so a hard-line stop loses nothing. Once per notice (its `since`) per run. The signal never
states spend, a cap or what is left of one.

Outside a detached run (no RM_DETACHED_UNIT) it exits at once and prints nothing; an unreadable notice is silent
(this hook never breaks the run it rides in).
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
