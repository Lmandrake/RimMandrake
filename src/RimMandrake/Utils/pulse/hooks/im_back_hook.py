#!/usr/bin/env python3
"""UserPromptSubmit hook: when the owner types "I'm back", prepend the since-you-left digest.

PREPARED, NOT INSTALLED (AWAY_DASHBOARD_BUILD_1): adding a hook is a settings change and
needs the owner's own OK. To install, add to ~/.claude/settings.json -> hooks:
  "UserPromptSubmit": [{"hooks": [{"type": "command", "timeout": 20,
     "command": "python3 /home/mandrake/rm/bench/src/RimMandrake/Utils/pulse/hooks/im_back_hook.py"}]}]
It only fires in sessions started after it is added. Without it, `./pulse back` does the same.
Never blocks a prompt: any failure exits 0 with no output.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    prompt = (json.load(sys.stdin).get("prompt") or "")
    if re.match(r"\s*(i'?m|i am)\s+back\b", prompt, re.I):
        out = subprocess.run([sys.executable, str(Path(__file__).resolve().parent.parent / "pulse.py"), "since", "--back"],
                             capture_output=True, text=True, timeout=15).stdout
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                                 "additionalContext": "Since-you-left digest (show it to him):\n" + out}}))
except Exception:
    pass
sys.exit(0)
