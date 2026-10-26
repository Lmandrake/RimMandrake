#!/usr/bin/env python3
"""facing_regen_batch.publish() commit message carries no hardcoded agent session/model (TRANSIENT_PIN_FIX_STALE_TRAILER)."""
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
print("selftest_facing_regen_batch_trailer OK")
