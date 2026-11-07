#!/usr/bin/env python3
"""PreToolUse hook for this Artisan loop, doing three things: deliver a note from the owner to a running pass, warn once a
pass's context runs large, and refuse game commands while a loop ahead in the queue is running."""
import json
import os
import re
import subprocess
import sys

AHEAD = ["rm-ralph-graffiti", "rm-ralph-gss"]
SOFT, HARD = 250_000, 350_000
WARNED = "ralph/.context_warned"
GAME = re.compile(
    r"bridge\s+take|rimbridge|live_session|modset_builder[^|;&]*--apply|modlist_swap|deploy_custom_mods[^|;&]*--apply"
    r"|logwait|\./game\s+\S*\s*\S*\s*(up|down|loading)\b|--live\b|northstar_driver|northstar_site|gate_live_proof|firefoam_aim_live_proof|human_review\.py"
    r"|RimWorldWin64|steam://|Start-Process|taskkill|system_click|system_screenshot")


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
    if not GAME.search(command):
        return 0
    if not any(subprocess.run(["systemctl", "--user", "is-active", "--quiet", u]).returncode == 0 for u in AHEAD):
        return 0
    print("REFUSED: another Artisan loop has the game, and it goes first. Do the offline work you can. When only the game "
          "can tell you more: write ralph/PROGRESS.md, create ralph/NEED_GAME, commit, push and end your turn. The loop "
          "waits at no token cost and starts a fresh pass when the game is free.", file=sys.stderr)
    return 2


sys.exit(main())
