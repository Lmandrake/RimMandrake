#!/usr/bin/env python3
"""peers.py — who else is live in this repo right now, and how to reach them.

    python3 src/RimMandrake/Utils/peers.py

WHY THIS EXISTS
===============
Rule 6b says to reply to the address a message came from and never to guess a
session name. For *initiating* contact it pointed at the state files:

    grep -A1 'Cross-session address' AGENT_*_state.md

That reads a CLAIM. The addresses there are PID-based, republished by hand on
resume, and on 2026-08-12 a seat reported all four stale at once — every agent
had rebooted and the files still advertised dead sockets. A stale address is
worse than none: it routes silently to nothing, or to whoever inherited the PID.

Claude Code already maintains the ground truth. Each live session writes
`~/.claude/sessions/<pid>.json` with its name, socket path, session id, cwd and
a heartbeat, and that registry is what `ListAgents` resolves against. Reading it
cannot go stale, because the sessions themselves write it.

⚠️ TWO NAMESPACES, AND THEY DO NOT FEED EACH OTHER — measured 2026-08-13
=======================================================================
`NAME` is the only string `SendMessage` accepts. `SEAT` is who that session
actually is, joined here from `.claude/session_roles/<sessionId>` — the file the
SessionStart hook and `set_agent_window.sh` both write.

They are separate fields and the hook cannot bridge them: `sessionTitle` sets
the CONVERSATION title, while the addressable name lives in
`~/.claude/sessions/<pid>.json` and is only written by `--name`, `/rename` or
the agent-name setter. Measured with three seats live: all three role files read
`AGENT <retired seat>` / `AGENT <retired seat>` / `AGENT <retired seat>` while all three names were
`rimworld-*` with `nameSource: "derived"`.

**So SEAT is the column you read, and NAME is the column you send to.** A seat
launched from a current Windows Terminal profile carries `--name 'AGENT <SEAT>'`
and the two agree; one launched any other way shows a generated NAME, and this
join is then the ONLY way to tell who it is. Do not guess from tab order.
"""
import json
import os
import sys
import time

SESSIONS = os.path.expanduser("~/.claude/sessions")
STALE_AFTER = 15 * 60          # heartbeat older than this: flag it, don't hide it


def load():
    out = []
    try:
        names = os.listdir(SESSIONS)
    except OSError:
        return out
    for fn in names:
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(SESSIONS, fn), "r", encoding="utf-8") as fh:
                out.append(json.load(fh))
        except Exception:
            continue                      # a half-written heartbeat is not fatal
    return out


def seat_of(repo, session_id):
    """The seat this session declared, from the role file, or "" if none.

    Same file the hook reads, keyed the same way, so this cannot disagree with
    the identity a session is actually wearing. Missing is normal and not an
    error: a session that never declared a role has no seat to show.
    """
    if not session_id:
        return ""
    path = os.path.join(repo, ".claude", "session_roles", session_id)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            title = fh.read().strip().splitlines()[0]
    except (OSError, IndexError):
        return ""
    # Stored as "AGENT BUILD"; the seat is the last token.
    parts = title.split()
    return parts[-1].upper() if parts else ""


def alive(pid):
    """The registry is a file; the process is the truth. Cheap liveness check."""
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError, TypeError):
        return False


def main():
    repo = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    me = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    now = time.time()

    rows = [s for s in load()
            if os.path.normpath(s.get("cwd", "")) == os.path.normpath(repo)]
    if not rows:
        print("no live sessions registered for %s" % repo)
        return 0

    for s in rows:
        s["_seat"] = seat_of(repo, s.get("sessionId"))
    # Seat first, so the seats read in a stable order and an undeclared
    # session sorts to the bottom where it is conspicuous.
    rows.sort(key=lambda s: (s.get("_seat") or "~", s.get("name") or ""))

    mismatched = False
    # 🔴 The name is QUOTED and the column is wide enough for the longest seat
    # name (`AGENT DECIDE`, 12 chars). It used to be a bare "%-12s", and the
    # then-longest name, a retired seat's, was itself exactly 12 chars
    # — so the field consumed its own padding and the PID ran onto the end of the
    # name: `AGENT <SEAT> 932`. A seat read that as the address and the send
    # bounced. Only a retired seat's name (9 chars) ever rendered correctly, which is why
    # the bug hid: replying to that seat worked, so the format looked fine.
    print("%-9s %-17s %-8s %-9s %s"
          % ("SEAT", "NAME (send to this)", "PID", "STATUS", "ADDRESS"))
    for s in rows:
        pid = s.get("pid")
        age = now - (s.get("updatedAt", 0) / 1000.0)
        seat = s.get("_seat") or "?"
        name = s.get("name") or "?"
        flags = []
        if s.get("sessionId") == me:
            flags.append("<- you")
        if not alive(pid):
            flags.append("DEAD PROCESS")
        elif age > STALE_AFTER:
            flags.append("stale heartbeat %dm" % (age / 60))
        if seat != "?" and not name.endswith(seat):
            flags.append("name!=seat")
            mismatched = True
        print("%-9s %-17s %-8s %-9s uds:%s %s" % (
            seat, "'%s'" % name, pid, s.get("status") or "?",
            s.get("messagingSocketPath") or "?", " ".join(flags)))

    print("\n⭐ SEND TO THE NAME COLUMN, NEVER THE SEAT COLUMN. They agree only "
          "when a\nsession was launched with `--name`; otherwise the seat is a "
          "label this script\njoins on, and SendMessage has never heard of it.")
    if mismatched:
        print("\n⚠️  A `name!=seat` row was launched WITHOUT `--name 'AGENT "
              "<SEAT>'`, so it\n    is addressable only by its generated name. "
              "Reinstall the profiles —\n    `python3 src/RimMandrake/Utils/install_wt_seat_"
              "profiles.py --apply` — and it is fixed at\n    that session's "
              "next launch, never mid-session.")
    print("\nReply to an incoming message by copying its from= verbatim "
          "(Rule 6b).\nUse this only to INITIATE contact with a role you have "
          "not heard from.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
