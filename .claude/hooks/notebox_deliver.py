#!/usr/bin/env python3
"""PostToolUse and Stop hook: hand a pending station note to the Relentless worker it is bound to
(STATION_NOTEBOX_BUILD_WHISPER_AT_NEXT_TURN; the logic and record are src/RimMandrake/rimflow/notebox.py).
Outside a Relentless worker (no RELENTLESS_GEN, or no .git/relentless.json) it exits at once and prints nothing."""
import os
import sys

event = sys.argv[1] if len(sys.argv) > 1 else "PostToolUse"
proj = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
if not os.environ.get("RELENTLESS_GEN") or not os.path.exists(os.path.join(proj, ".git", "relentless.json")):
    sys.exit(0)
sys.path.insert(0, os.path.join(proj, "src", "RimMandrake", "rimflow"))
try:
    import notebox
except Exception as e:      # noqa: BLE001 -- a hook never breaks the session it runs in
    print("notebox_deliver: %s" % e, file=sys.stderr)
    sys.exit(0)
sys.exit(notebox.main(["deliver", "--event", event]))
