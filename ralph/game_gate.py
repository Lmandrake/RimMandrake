#!/usr/bin/env python3
"""PreToolUse hook for this Artisan loop, doing three things: deliver a note from the owner to a running pass, warn once a
pass's context runs large, and refuse every game command on this machine: this loop's game is SteveDesktop's, reached
through ralph/steve.sh, and Archmagi's belongs to other loops."""
import json
import os
import re
import shlex
import sys

SOFT, HARD = 250_000, 350_000
WARNED = "ralph/.context_warned"
GAME = re.compile(
    r"bridge\s+take|rimbridge|live_session|modset_builder[^|;&]*--apply|modlist_swap|deploy_custom_mods[^|;&]*--apply"
    r"|logwait|modcheck\s+run|\./game\s+\S*\s*\S*\s*(up|down|loading)\b|proof_all\.py(?![^|;&]*--offline)|--live\b"
    r"|(?<!selftest_)gss_playtest_runner|human_review\.py|save_review_map|pole_shots|shader_sway_look"
    r"|RimWorldWin64|steam://|Start-Process|taskkill|system_click|system_screenshot")


def local_part(command):
    """The command minus its ralph/steve.sh segments: those run on Steve, whatever their arguments say."""
    try:
        lex = shlex.shlex(command.replace("\n", ";"), posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        return command
    kept, segment = [], []
    for token in tokens + [";"]:
        if token and set(token) <= set("();<>|&"):
            if segment and not segment[0].endswith("ralph/steve.sh"):
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
    if not GAME.search(local_part(command)):
        return 0
    print("REFUSED: that drives a game on this machine, and Archmagi's game belongs to other loops. Yours is on SteveDesktop: "
          "run it through ralph/steve.sh (CLAUDE.md has the commands).", file=sys.stderr)
    return 2


sys.exit(main())
