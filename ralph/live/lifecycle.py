#!/usr/bin/env python3
"""Where the game is in its life now (menu, loading, map), and a screenshot of the screen. python.exe ralph/live/lifecycle.py [shotname]"""
import json, os, sys
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "northstar_matrix"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import run_live as RL  # noqa: E402
B = RL.LiveBridge()
for tool in ("rimworld/get_ui_state", "rimworld/get_game_info"):
    print(tool, json.dumps(B.call(tool))[:600])
