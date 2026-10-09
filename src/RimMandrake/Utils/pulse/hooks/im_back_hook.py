#!/usr/bin/env python3
"""UserPromptSubmit hook: when the owner types "I'm back", prepend the since-you-left digest.

INSTALLED 2026-10-08 in .claude/settings.json (owner OK by card, AWAY_DASHBOARD_BUILD_1).
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
        # How far back, if he says: "I'm back 3h", "... last 6 hours", "... since 17:30", "... since 5pm".
        span = ["--back"]
        m = re.search(r"(\d+)\s*(d|days?|h|hrs?|hours?|m|mins?|minutes?)\b", prompt, re.I)
        t = re.search(r"since\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", prompt, re.I)
        if t:
            hh = int(t[1]) % 12 + (12 if (t[3] or "").lower() == "pm" else 0) if t[3] else int(t[1])
            span = ["--since", f"{hh}:{t[2] or '00'}"]
        elif m:
            span = ["--since", m[1] + m[2][0].lower()]
        out = subprocess.run([sys.executable, str(Path(__file__).resolve().parent.parent / "pulse.py"), "since", *span],
                             capture_output=True, text=True, timeout=15).stdout
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                                 "additionalContext": "Since-you-left digest (show it to him):\n" + out}}))
except Exception:
    pass
sys.exit(0)
