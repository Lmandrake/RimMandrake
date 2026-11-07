#!/usr/bin/env python3
"""PreToolUse hook for this Artisan loop, doing three things: deliver a note from the owner to a running pass, warn once a
pass's context runs large, and refuse game commands while a loop ahead on this loop's game is running.

The worked example is RimWorld's two games on one machine (RimMandrake's game_instance.py). RM_GAME_INSTANCE says which game
this loop drives; nothing set is game a, today's game.

A resource can have several copies on one machine (RimWorld's game a and game b). COPY is the one this loop uses, read
from COPY_ENV. AHEAD names, for each copy, the systemd units that go first on it, so a loop running on another copy never
holds this one up. Keep the unit names exact: `systemctl is-active` reads a misspelt or renamed unit as "not running", and
that looks like a free resource. A copy with no entry in AHEAD is refused by name, because a typo must not mean "free".

Two refusals hold whatever the queue says. A kill by image name takes every game on the machine. And a loop on a named game
stays off desktop tools and Steam's launch: both games share one image name and one window title, click and screenshot tools
aim at the desktop rather than a game, and steam:// can only ever start game a. Use the bridge's own screenshots.

A loop whose game is on another machine sets WRAPPER to the script that reaches it and DEFAULT_COPY to that game (a loop on
Archmagi driving SteveDesktop's game b: "ralph/steve.sh" and "b"). Then a game command outside the wrapper is refused
whatever the queue says, because it would land on this machine's game, which is some other loop's. `systemctl --user` reads
this machine's units, so AHEAD can only name loops whose units run here, wherever their games are."""
import json
import os
import re
import shlex
import subprocess
import sys

WRAPPER = "ralph/steve.sh"
COPY_ENV = "RM_GAME_INSTANCE"
DEFAULT_COPY = "b"
AHEAD = {"b": []}
SOFT, HARD = 250_000, 350_000
WARNED = "ralph/.context_warned"
GAME = re.compile(
    r"bridge\s+take|rimbridge|live_session|modset_builder[^|;&]*--apply|modlist_swap|deploy_custom_mods[^|;&]*--apply"
    r"|logwait|\./game\s+\S*\s*\S*\s*(up|down|loading)\b|--live\b|northstar_driver|northstar_site|gate_live_proof|firefoam_aim_live_proof|human_review\.py"
    r"|stage_colony|graffiti_v1_live_proof|/tmp/gr/cycle|RimWorldWin64|steam://|Start-Process|taskkill|system_click|system_screenshot")

NEVER = re.compile(r"taskkill[^|;&]*/IM\b[^|;&]*RimWorld", re.I)
NEVER_ON_NAMED = re.compile(r"system_click|system_screenshot|steam://|steam\.exe", re.I)


def local_part(command):
    """The command minus its WRAPPER segments: those run on the other machine, whatever their arguments say."""
    try:
        lex = shlex.shlex(command.replace("\n", ";"), posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        return command
    kept, segment = [], []
    for token in tokens + [";"]:
        if token and set(token) <= set("();<>|&"):
            if segment and not segment[0].endswith(WRAPPER):
                kept.append(" ".join(segment))
            segment = []
        else:
            segment.append(token)
    return " ; ".join(kept)


def owner_note():
    if not os.path.exists("ralph/OWNER_NOTE"):
        return None
    with open("ralph/OWNER_NOTE", encoding="utf-8") as f:
        text = f.read()
    os.rename("ralph/OWNER_NOTE", "ralph/OWNER_NOTE.delivered")
    return ("NOT RUN: the owner sent you a note while you were working. Read it, take it into your work now, then run "
            "your command again.\n\n" + text)


def context_size(transcript):
    """The size of this pass's context, from the last usage in its transcript; None when it can't be read."""
    try:
        with open(transcript, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 400_000))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        usage = (row.get("message") or {}).get("usage") if row.get("type") == "assistant" else None
        if usage and not row.get("isSidechain"):
            return (usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
                    + usage.get("cache_read_input_tokens", 0))
    return None


def context_warning(hook, transcript):
    size = context_size(transcript) if transcript else None
    if size is None or size < SOFT:
        return None
    try:
        with open(WARNED, encoding="utf-8") as f:
            session, level = f.read().split()
    except (OSError, ValueError):
        session, level = "", "0"
    level = int(level) if session == hook.get("session_id") else 0
    want = 2 if size >= HARD else 1
    if level >= want:
        return None
    with open(WARNED, "w", encoding="utf-8") as f:
        f.write(f"{hook.get('session_id')} {want}\n")
    if want == 2:
        return (f"NOT RUN: your context is about {size // 1000}k tokens. Every step now costs several times what it did at "
                "the start. Finish the fix in hand, write ralph/PROGRESS.md, commit, push and retire. A fresh pass starts "
                "at once. Then run your command again if you still need it.")
    return (f"NOT RUN: your context is about {size // 1000}k tokens. Keep going while what you've learned is paying for "
            "itself, but retire at your next natural stopping point, and send heavy reading and screenshot review to "
            "subagents. Run your command again.")


def main():
    hook = json.load(sys.stdin)
    message = owner_note() or context_warning(hook, hook.get("transcript_path"))
    if message:
        print(message, file=sys.stderr)
        return 2
    command = (hook.get("tool_input") or {}).get("command", "")
    copy = (os.environ.get(COPY_ENV) or DEFAULT_COPY).strip().lower()
    if NEVER.search(command):
        print("REFUSED: taskkill /IM takes every game on this machine, another loop's included. Stop yours by pid: "
              "python3 src/RimMandrake/Utils/game_instance.py stop", file=sys.stderr)
        return 2
    if copy != "a" and NEVER_ON_NAMED.search(command):
        print("REFUSED: on game %s, desktop clicks and screenshots hit whatever window is on top, and Steam's launch can only "
              "start game a. Use the bridge's screenshots and game_instance.py launch." % copy, file=sys.stderr)
        return 2
    if WRAPPER and GAME.search(local_part(command)):
        print("REFUSED: that drives a game on this machine, and that game belongs to other loops. Yours is reached through "
              "%s." % WRAPPER, file=sys.stderr)
        return 2
    if not GAME.search(command):
        return 0
    if copy not in AHEAD:
        print("REFUSED: this loop's %s is %r, which this gate's AHEAD does not name. Tell whoever runs the loop." % (COPY_ENV, copy),
              file=sys.stderr)
        return 2
    if not any(subprocess.run(["systemctl", "--user", "is-active", "--quiet", u]).returncode == 0 for u in AHEAD[copy]):
        return 0
    print("REFUSED: another Artisan loop has the game, and it goes first. Do the offline work you can. When only the game "
          "can tell you more: write ralph/PROGRESS.md, create ralph/NEED_GAME, commit, push and end your turn. The loop "
          "waits at no token cost and starts a fresh pass when the game is free.", file=sys.stderr)
    return 2


sys.exit(main())
