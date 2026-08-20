#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""broadcast.py — the OWNER speaks to every agent window at once.

    ./src/RimMandrake/Utils/broadcast.py "Game is up"
    ./src/RimMandrake/Utils/broadcast.py --all "WRAP is initiated"
    ./src/RimMandrake/Utils/broadcast.py --to CHECK,BUILD "Game is loading"
    ./src/RimMandrake/Utils/broadcast.py --list

🔴 THIS IS A USER TOOL. AGENTS DO NOT RUN IT.
Owner's ruling, 2026-08-19: agents do not message each other, at all. `SendMessage`
and `ListAgents` are DENIED to them in `.claude/settings.json`, so an agent has no
way to reach a peer through the supported channel. This script deliberately goes
around that — it writes the peer socket directly, which permission rules do not
gate — and that is exactly why **only the owner may run it.** An agent that runs
this to talk to another agent is breaking the ruling by the back door.

WHAT IT IS FOR, and nothing else: announcing a change of GAME STATE that every
seat must know at the same moment — *game is up* · *game is loading* · *WRAP is
initiated*. Not findings, not specs, not handoffs. Those are queue items.

HOW IT WORKS
------------
Every live Claude Code session publishes itself under ~/.claude/sessions/ :

    <pid>.json                 name, cwd, kind, status, messagingSocketPath
    <pid>.<sha256>.key         {"peerToken": "<hex32>", ...}

We read both, then speak the session inbox protocol over the unix socket:

    {"type":"auth","token":"<peerToken>"}\\n
    {"msgV":1,"msg_id":"<uuid>","type":"user","priority":"next",
     "message":{"role":"user","content":
       "<cross-session-message from-name=\\"OWNER\\">TEXT</cross-session-message>"}}\\n

⚠️ The frame is READ OFF THE INSTALLED CLI (2.1.237), not documented. If a Claude
Code upgrade changes it, this script starts failing and the fix is to re-read it.
It is pinned in one place — `frame()` below — for exactly that reason.

🔑 By DEFAULT this only reaches windows whose cwd is this repo, so the owner's
other projects never get fleet traffic. `--all` overrides that.
"""
import json
import os
import re
import socket
import sys
import uuid

SESSIONS = os.path.expanduser("~/.claude/sessions")
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))   # Utils -> RimMandrake -> src -> repo
KEY_RE = re.compile(r"^(\d+)\.[0-9a-f]{64}\.key$")


def sessions():
    """Every live session: the .json record, joined to its peerToken."""
    tokens = {}
    try:
        names = os.listdir(SESSIONS)
    except OSError:
        return []
    for fn in names:
        m = KEY_RE.match(fn)
        if not m:
            continue
        try:
            with open(os.path.join(SESSIONS, fn), encoding="utf-8") as fh:
                tokens[int(m.group(1))] = json.load(fh).get("peerToken")
        except Exception:
            pass
    out = []
    for fn in names:
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(SESSIONS, fn), encoding="utf-8") as fh:
                rec = json.load(fh)
        except Exception:
            continue
        sock = rec.get("messagingSocketPath")
        # 🔑 The socket file EXISTING is the liveness test. A record whose process
        # has gone leaves the .json behind; the socket goes with the process.
        if not sock or not os.path.exists(sock):
            continue
        rec["peerToken"] = tokens.get(rec.get("pid"))
        out.append(rec)
    return sorted(out, key=lambda r: r.get("name") or "")


def frame(text, sender="OWNER"):
    """⚠️ The wire format, pinned in one place. See the module docstring."""
    esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return json.dumps({
        "msgV": 1,
        "msg_id": str(uuid.uuid4()),
        "type": "user",
        "priority": "next",
        "message": {"role": "user", "content":
                    '<cross-session-message from-name="%s">%s</cross-session-message>'
                    % (sender, esc)},
    })


def send(rec, text, sender="OWNER"):
    if not rec.get("peerToken"):
        return "no peer token"
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(rec["messagingSocketPath"])
        s.sendall((json.dumps({"type": "auth", "token": rec["peerToken"]}) + "\n").encode())
        s.sendall((frame(text, sender) + "\n").encode())
        s.close()
        return None
    except Exception as e:                       # noqa: BLE001 - report, never raise
        return "%s: %s" % (type(e).__name__, e)


def main(argv):
    args, only, everywhere, sender = [], None, False, "OWNER"
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--all":
            everywhere = True
        elif a == "--list":
            only = "\x00list"
        elif a == "--to" and i + 1 < len(argv):
            i += 1
            only = [x.strip().upper() for x in argv[i].split(",") if x.strip()]
        elif a == "--from" and i + 1 < len(argv):
            i += 1
            sender = argv[i]
        else:
            args.append(a)
        i += 1

    live = sessions()
    if not everywhere:
        live = [r for r in live
                if os.path.realpath(r.get("cwd") or "") == os.path.realpath(REPO)]

    if only == "\x00list":
        for r in sessions():
            here = "  " if os.path.realpath(r.get("cwd") or "") == os.path.realpath(REPO) else " *"
            print("%s %-18s %-9s pid%-8s %s"
                  % (here, r.get("name"), r.get("status"), r.get("pid"), r.get("cwd")))
        print("\n  (* = outside this repo; needs --all)")
        return 0

    text = " ".join(args).strip()
    if not text:
        print(__doc__.split("HOW IT WORKS")[0].strip())
        return 2

    if isinstance(only, list):
        live = [r for r in live if any(k in (r.get("name") or "").upper() for k in only)]
    if not live:
        print("no live sessions matched")
        return 1

    me = os.environ.get("CLAUDE_CODE_MESSAGING_SOCKET")
    for r in live:
        if me and r.get("messagingSocketPath") == me:
            print("  %-18s skipped (this window)" % r.get("name"))
            continue
        err = send(r, text, sender)
        print("  %-18s %s" % (r.get("name"), err or "delivered"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
