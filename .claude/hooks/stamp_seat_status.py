#!/usr/bin/env python3
"""stamp_seat_status.py — prove a seat is BREATHING, without asking it to remember.

Wired to PostToolUse and UserPromptSubmit. Writes one small JSON per seat to
`infrastructure/state/status/<SEAT>.json`, which `board.py` renders.

WHY A HOOK AND NOT A CONVENTION
===============================
Every hand-maintained status field in this repo has gone stale, including the
run sheet, which was 1.5 h behind its own source queues on 2026-08-14 while
reading as current. A seat that is busy is exactly the seat that forgets to say
so, and a seat that has CRASHED cannot say anything at all — yet a hand-written
"working on L4" sits there looking alive forever.

So the two halves are split by who can be trusted with them:

  the HOOK owns   `updated` and `tool`   — liveness. Cannot be forgotten.
  the SEAT owns   `item` and `state`     — meaning. Cannot be automated.

The board ages every line off `updated`. ⇒ a seat that stops updating its `item`
goes amber on its own instead of lying quietly. **That is the whole design.**

The seat's half is written by `board.py say "<what I am doing>"`, which merges
into this same file rather than replacing it.
"""
import json
import os
import sys
import time

STATUS_DIR = "infrastructure/state/status"


def main():
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    seat = os.environ.get("AGENT_SEAT")
    if not seat:
        return 0                      # not a fleet seat; nothing to stamp

    # The hook is fed JSON on stdin. A malformed or absent payload must never
    # break the seat's tool call — this hook is observational, not a gate.
    tool = ""
    try:
        payload = json.load(sys.stdin)
        tool = payload.get("tool_name") or ""
    except Exception:
        pass

    path = os.path.join(root, STATUS_DIR, "%s.json" % seat.upper())
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Merge, never replace: the seat's `item`/`state` live in this file too
        # and a stamp must not wipe what the seat said about itself.
        cur = {}
        if os.path.exists(path):
            try:
                with open(path) as fh:
                    cur = json.load(fh)
            except Exception:
                cur = {}
        cur.update({
            "seat": seat.upper(),
            "pid": os.getppid(),
            "updated": int(time.time()),
            "tool": tool,
        })
        tmp = path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(cur, fh)
        os.replace(tmp, path)         # atomic: the board never reads a half file
    except Exception:
        pass                          # observational. Never block a tool call.
    return 0


if __name__ == "__main__":
    sys.exit(main())
