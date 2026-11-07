#!/usr/bin/env python3
"""Refuse commands that touch the live game until the Gimme Some Slack Ralph loop has let go of it."""
import json
import re
import subprocess
import sys

GSS_EVENTS = "/mnt/d/ClaudeWork/rimmandrake/ralph_gss/events.log"
GAME = re.compile(
    r"bridge\s+take|rimbridge|live_session|stage_colony|graffiti_v1_live_proof|/tmp/gr/cycle|modset_builder[^|;&]*--apply"
    r"|modlist_swap|deploy_custom_mods[^|;&]*--apply|logwait|\./game\s+\S*\s*\S*\s*(up|down|loading)\b|--live\b"
    r"|RimWorldWin64|steam://|Start-Process|taskkill|system_click|system_screenshot")


def gss_has_game():
    if subprocess.run(["pgrep", "-f", "GimmeSomeSlack/northstar/proof_all"], capture_output=True).returncode == 0:
        return True
    if subprocess.run(["systemctl", "--user", "is-active", "--quiet", "rm-ralph-gss"]).returncode != 0:
        return False
    with open(GSS_EVENTS, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    return not (lines and "GAME_WAIT" in lines[-1])


def main():
    if "--held" in sys.argv:
        return 0 if gss_has_game() else 1
    command = (json.load(sys.stdin).get("tool_input") or {}).get("command", "")
    if not GAME.search(command) or not gss_has_game():
        return 0
    print("REFUSED: the Gimme Some Slack loop still has the game, and it has been told to yield to you. Do the offline "
          "work you can. When only the game can tell you more: write ralph/PROGRESS.md, create ralph/NEED_GAME, commit, "
          "push and end your turn. The loop waits at no token cost and starts a fresh pass when the game is free.",
          file=sys.stderr)
    return 2


sys.exit(main())
