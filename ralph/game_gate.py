#!/usr/bin/env python3
"""Refuse commands that touch the live game while the Graffiti Ralph loop is running: it has the one game first."""
import json
import os
import re
import subprocess
import sys

GAME = re.compile(
    r"bridge\s+take|rimbridge|live_session|modset_builder[^|;&]*--apply|modlist_swap|deploy_custom_mods[^|;&]*--apply"
    r"|logwait|\./game\s+\S*\s*\S*\s*(up|down|loading)\b|proof_all\.py(?![^|;&]*--offline)|--live\b"
    r"|(?<!selftest_)gss_playtest_runner|human_review\.py|save_review_map|pole_shots|shader_sway_look"
    r"|RimWorldWin64|steam://|Start-Process|taskkill|system_click|system_screenshot")


def deliver_owner_note():
    """A note from the owner reaches a running pass once: the next command is refused with it."""
    note = "ralph/OWNER_NOTE"
    if not os.path.exists(note):
        return False
    with open(note, encoding="utf-8") as f:
        text = f.read()
    os.rename(note, note + ".delivered")
    print("NOT RUN: the owner sent you a note while you were working. Read it, take it into your work now, then run "
          "your command again.\n\n" + text, file=sys.stderr)
    return True


def main():
    if deliver_owner_note():
        return 2
    command = (json.load(sys.stdin).get("tool_input") or {}).get("command", "")
    if not GAME.search(command):
        return 0
    if subprocess.run(["systemctl", "--user", "is-active", "--quiet", "rm-ralph-graffiti"]).returncode != 0:
        return 0
    print("REFUSED: the Graffiti loop has the game, and it goes first. Do the offline work you can. When only the game "
          "can tell you more: write ralph/PROGRESS.md, create ralph/NEED_GAME, commit, push, release the bridge if you "
          "hold it, and end your turn. The loop waits at no token cost and starts a fresh pass when the game is free.",
          file=sys.stderr)
    return 2


sys.exit(main())
