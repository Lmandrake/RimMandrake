#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_KEEP_BRIDGE_HEARTBEAT_TO_HOLDER_CLONE_ONLY (filed 2026-11-16 by
RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD): every detached helper is seat BENCH, so one helper's
ledger note (cli.py -> model.touch_shared_bridge) refreshed the shared bridge lock another BENCH helper held for a live
run and stamped the NOTE WRITER's clone on it (05:13:59: Explosive Knockback's walk-raid hold read as held from the
unstick helper's clone). A heartbeat from another clone must leave the hold as it was.

    python3 src/RimMandrake/rimflow/selftest_shared_bridge_touch_own_clone.py      # 2 checks; exit 0 when both pass
"""
import json
import os
import sys
import tempfile

d = tempfile.mkdtemp(prefix="shared_bridge_touch_")
p = os.path.join(d, "BRIDGE_SHARED.json")
os.environ["RIMFLOW_SHARED_BRIDGE"] = p
os.environ["CLAUDE_PROJECT_DIR"] = "/clones/OTHER_HELPER.det"     # the clone this process (the note writer) runs in
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model  # noqa: E402

held = {"holder": "BENCH", "since": "2026-11-16T13:07:56Z", "touched": "2026-11-16T13:07:56Z",
        "purpose": "EK sc_walk_raid rerun", "clone": "/clones/HOLDER.det"}
with open(p, "w") as f:
    json.dump(held, f)
model.touch_shared_bridge("BENCH")
got = json.load(open(p))
fails = 0
for ok, what in ((got.get("clone") == "/clones/HOLDER.det", "the hold keeps its holder's clone (read %s)" % got.get("clone")),
                 (got.get("touched") == held["touched"], "a note from another clone does not refresh the hold")):
    print(("PASS " if ok else "FAIL ") + what)
    fails += not ok
sys.exit(1 if fails else 0)
