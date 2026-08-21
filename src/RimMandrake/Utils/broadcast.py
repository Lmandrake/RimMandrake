#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""broadcast.py — the OWNER speaks to every agent window at once.

    ./src/RimMandrake/Utils/broadcast.py "Game is up"
    ./src/RimMandrake/Utils/broadcast.py --all "WRAP is initiated"
    ./src/RimMandrake/Utils/broadcast.py --to CHECK,BUILD "Game is loading"
    ./src/RimMandrake/Utils/broadcast.py --list

⭐ SAYING IT IS RECORDING IT. A message that announces game state also appends the
OWNER's `game` event, so there is no second command to forget:

    "Game is up"          -> UP          "Game is loading"   -> LOADING
    "Game is down"        -> DOWN        "WRAP is initiated" -> GOING_DOWN
    "at the main menu"    -> UP          "deploying"         -> DEPLOYING

It prints what it recorded. Prose that merely mentions the game records nothing.

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

🔴 WHY EVERY WINDOW STILL ASKS "accept / reject", investigated 2026-08-21
--------------------------------------------------------------------------
It is NOT `crossSessionInbound`. That is already at its most permissive value.
Confirmed against the installed binary 2.1.238, which carries the enum literally:

    crossSessionInbound: ["accept","hold","refuse"]        N1i={accept:0,hold:1,refuse:2}

There is no fourth, stronger value, and `.claude/settings.json` has held `accept`
since 2026-08-19 (`6bdac8e`).

🔑 `accept` IS OVERRIDDEN BY A PERMISSION-MODE RULE. Per Anthropic's cross-session
messaging docs, when the two sides are in different permission-mode classes the
receiver holds the message for approval regardless:

  * receiver PROMPTS for permissions -> delivers, unless the SENDER bypasses
  * receiver BYPASSES permissions    -> holds, unless the SENDER also bypasses

The agent windows run in bypass mode. This script is a plain socket writer and
does not identify as bypassing. Receiver bypasses + sender does not => HELD.
That is the dialog, and it is working as designed.

⛔ WHAT WILL NOT FIX IT, all checked so they are not tried again:
  * a stronger `crossSessionInbound` — there isn't one
  * a hook on receipt — no hook event fires on receiving a peer message
  * gating on `from-name="OWNER"` — the receiver cannot see sender identity,
    only the sender's permission-mode class
  * a `permissions` entry — those govern what a session SENDS, not what it takes

⚠️ THE OPEN QUESTION, and nobody should guess at it: which field of the auth
handshake or the frame declares the sender's bypass class. It is not in the
session's `~/.claude/sessions/<pid>.json` — those carry pid, name, cwd, status,
peerProtocol and peerFeatures, and no permission mode. Pin it by reading the CLI's
own outbound peer send, then set it here. A GUESSED field name is worse than the
dialog: it fails silently and looks fixed.

✅ AND THE SAFETY PROPERTY SURVIVES THE FIX, which is why the fix is worth making.
Auto-delivery does NOT open agent-to-agent messaging: agents are blocked at the
SENDING end by `.claude/hooks/block_peer_messages.py`, and an agent running THIS
script is already the violation. Nothing about inbound needs to distinguish the
owner, because nothing else can legitimately reach the socket.

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


# ---------------------------------------------------------------------------
# GAME STATE — the owner says it, this records it
# ---------------------------------------------------------------------------
# 🔴 OWNER, 2026-08-21: "change the python implementation of the user declaring the
# game up or down to a simple broadcast message, not a python script."
#
# Before this, announcing a load was TWO acts: a broadcast so the seats heard it, and
# `rimflow game UP --seat OWNER` so the board believed it. The second was forgotten
# every time — the board sat at DOWN through an entire session on 2026-08-21 while the
# game was up, so every item gated on `needs: game-up` stayed unoffered.
#
# 🔑 Now the sentence IS the command. The owner types what he was going to type anyway
# and the ledger event is a side effect of being understood.
#
# ⚠️ DELIBERATELY CONSERVATIVE. It matches whole phrases, not the bare word "game", and
# it prints what it recorded so a wrong guess is visible in the same breath. Prose that
# merely mentions the game records nothing — silence is the safe failure here, because a
# WRONG game state is worse than none: `satisfiable()` gates bridge work on it.
GAME_PHRASES = [
    # order matters — the first match wins, so the specific ones come first
    ("GOING_DOWN", ("going down", "wrap is initiated", "wrap initiated",
                    "about to close", "closing the game", "shutting down")),
    ("LOADING",    ("is loading", "game loading", "loading now", "loading the game")),
    ("DEPLOYING",  ("deploying", "deploy window", "is deploying")),
    ("UP",         ("game is up", "game up", "at the main menu", "main menu",
                    "game's up", "we are up", "it is up", "it's up")),
    ("DOWN",       ("game is down", "game down", "game's down", "is closed",
                    "has closed", "went down", "is unstable", "brought it down")),
]


def game_state_in(text):
    """-> the state this sentence announces, or None. First match wins."""
    low = " %s " % " ".join(text.lower().split())
    for state, phrases in GAME_PHRASES:
        for p in phrases:
            if p in low:
                return state
    return None


def record_game(state, text):
    """Append the OWNER's `game` event. Never fatal — the message still goes out."""
    import subprocess
    cli = os.path.join(REPO, "src/RimMandrake/rimflow/cli.py")
    if not os.path.exists(cli):
        return "rimflow not found; state NOT recorded"
    env = dict(os.environ, RIMFLOW_SEAT="OWNER")
    try:
        p = subprocess.run([sys.executable, cli, "game", state],
                           capture_output=True, text=True, timeout=30,
                           cwd=REPO, env=env)
    except Exception as e:                       # noqa: BLE001 - never gate the send
        return "state NOT recorded: %s" % e
    if p.returncode:
        return "state NOT recorded: %s" % (p.stderr or p.stdout or "?").strip()[:160]
    return None


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

    # 🔑 Record BEFORE delivering. A seat woken by this message will run
    # `rimflow next` within the second, and it must read the new state, not the old one.
    state = game_state_in(text)
    if state:
        err = record_game(state, text)
        print("  game -> %-12s %s" % (state, err or "recorded in the ledger"))

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
