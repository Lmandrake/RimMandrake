#!/usr/bin/env python3
"""Close whatever dialog is open (a failed load's message box). python.exe ralph/live/close_dialogs.py"""
import json, os, sys
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "northstar_matrix"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import run_live as RL  # noqa: E402
B = RL.LiveBridge()
print(json.dumps(B.call("jawa/clear_ui", all=True))[:300])
print(json.dumps(B.call("rimworld/get_ui_state"))[:200])
