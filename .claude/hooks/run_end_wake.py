#!/usr/bin/env python3
"""Stop hook (asyncRewake): wake the live Conductor window when a detached run of its seat ends
(RIMMANDRAKE_WAKE_CONDUCTOR_ON_RUN_END_LOG_ONLY_TODAY; the logic is src/RimMandrake/rimflow/run_end_wake.py).
Any other window exits 0 at once and prints nothing; a failure never breaks the window it runs in."""
import os
import sys

proj = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
if (os.environ.get("AGENT_SEAT") or "").strip().upper() != "BENCH":
    sys.exit(0)
sys.path.insert(0, os.path.join(proj, "src", "RimMandrake", "rimflow"))
try:
    import run_end_wake
    code = run_end_wake.hook_main()
except Exception as e:      # noqa: BLE001 -- a hook never breaks the session it runs in
    print("run_end_wake: %s" % e, file=sys.stderr)
    code = 0
sys.exit(code)
