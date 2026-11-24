#!/usr/bin/env python3
"""due(): a render that died spends no attempt; and facing_regen_batch.publish() commit message carries no hardcoded agent session/model (TRANSIENT_PIN_FIX_STALE_TRAILER)."""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import facing_regen_batch as B

seen = []
real = B.subprocess.run
B.subprocess.run = lambda argv, **kw: (seen.append(argv), subprocess.CompletedProcess(argv, 0, "PUBLISHED x", ""))[1]
try:
    B.publish(["a.png"], 1)
finally:
    B.subprocess.run = real
pub = [a for a in seen if a and a[0] == "./publish"]
assert pub, seen
msg = pub[0][pub[0].index("-m") + 1]
assert "Claude-Session" not in msg and "Co-Authored-By" not in msg and "facing_regen_batch.py" in msg, msg
# a-dead-render-spends-no-attempt (failure_class): a Codex call that failed or raised leaves the picture due
fail = {"status": "retryable_failure", "attempts": 9}
assert B.due(dict(fail, outcome="APPARATUS FAULT")), "a render that died spends no attempt"
assert not B.due(fail) and B.due(dict(fail, attempts=1)), "a record with no outcome reads as before"
assert not B.due(dict(fail, outcome="MOD FAILURE")), "a picture refused on its merits is not drawn again"
assert B.due({"status": "pending", "attempts": 0}) and not B.due({"status": "installed", "attempts": 1})
print("selftest_facing_regen_batch_trailer OK")
