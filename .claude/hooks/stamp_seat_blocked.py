#!/usr/bin/env python3
"""stamp_seat_blocked.py — a CERTAIN "this seat needs a human" signal.

Wired to `Notification` (sets the flag) and `UserPromptSubmit` (clears it).

WHY THIS REPLACES A GUESS
=========================
The board's `MAYBE STUCK` band inferred "this seat is stopped" from the process
state reported by `claude agents --json`, gated behind a 90-second dwell timer to
stop it flapping. That was a **guess**, and it was labelled as one on screen for
exactly that reason: people match their response rate to an alarm's observed
reliability, so a half-right band gets obeyed half the time.

Claude Code already emits the real thing. The `Notification` hook fires with a
**matchable type** — `permission_prompt`, `idle_prompt`, `agent_needs_input`,
`agent_completed` — so "waiting at a prompt" is a fact we are told, not a state
we infer from timing. ⇒ **the guess becomes a certainty, and the dwell timer
becomes unnecessary for anything this hook covers.**

The old inference stays as a fallback: it catches a seat that has *crashed*,
which by definition sends no notification at all. Silence and stopped look the
same from outside, and only one of them announces itself.

CLEARING IS THE HALF THAT GETS FORGOTTEN
========================================
A flag that is set and never cleared is the `LIVE BRIDGE TAKEN` failure again —
it marks the seat blocked forever, which is worse than never flagging it.
`UserPromptSubmit` fires when the seat receives input, which is precisely the
moment it stopped waiting. **Both halves are wired here, deliberately, in one
file, so neither can be added without the other.**
"""
import json
import os
import sys
import time

STATUS_DIR = "infrastructure/state/status"

# Types that mean a HUMAN is required. `agent_completed` is deliberately absent:
# a finished agent is news, not a blockage, and mixing the two would put a
# low-urgency event into the band reserved for certain ones.
NEEDS_HUMAN = {"permission_prompt", "idle_prompt", "agent_needs_input",
               "elicitation_request"}


def main():
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    seat = (os.environ.get("AGENT_SEAT") or "").upper()
    if not seat:
        return 0

    payload = {}
    try:
        payload = json.load(sys.stdin)
    except Exception:
        pass

    event = payload.get("hook_event_name") or ""
    ntype = payload.get("notification_type") or payload.get("type") or ""

    path = os.path.join(root, STATUS_DIR, "%s.json" % seat)
    try:
        cur = {}
        if os.path.exists(path):
            try:
                with open(path) as fh:
                    cur = json.load(fh)
            except Exception:
                cur = {}

        if event == "UserPromptSubmit":
            # Received input ⇒ no longer waiting. Clear both halves.
            cur.pop("blocked_since", None)
            cur.pop("blocked_why", None)
        elif ntype in NEEDS_HUMAN or (event == "Notification" and not ntype):
            # An untyped Notification still means Claude wanted the human's
            # attention — treat it as blocking rather than dropping it, and
            # record what we were told so the board can show the reason.
            cur.setdefault("blocked_since", int(time.time()))
            cur["blocked_why"] = ntype or "notification"
        else:
            return 0

        cur["seat"] = seat
        tmp = path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(cur, fh)
        os.replace(tmp, path)
    except Exception:
        pass          # observational. Never block a seat over bookkeeping.
    return 0


if __name__ == "__main__":
    sys.exit(main())
