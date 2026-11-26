#!/usr/bin/env python3
"""WSL-side watchdog for the Windows telemetry stack (rm-telemetry-health.timer, every 2 min).

The Windows scheduled task "RimMandrake\\Telemetry" runs supervise.py every minute and is the real
keeper; this is the second pair of eyes, the same shape as rm-pulse-health: if telemetryd's
heartbeat (E:\\telemetry\\state\\heartbeat.json) is older than 3 minutes, kick the task once
(`schtasks /Run`) and say so in the journal. It never starts Windows processes itself.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tcommon import cfg, read_json  # noqa: E402

STALE_S = 180
# A systemd user unit runs with a bare PATH, so the bare name raised FileNotFoundError and the unit went failed
# without kicking (5 failures 2026-11-23..26). Windows interop keeps the exe at a fixed path.
SCHTASKS_FALLBACK = "/mnt/c/Windows/System32/schtasks.exe"


def schtasks() -> str:
    return shutil.which("schtasks.exe") or SCHTASKS_FALLBACK


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    st = cfg()["state"]
    if not os.path.isdir(st):
        print("telemetry state dir absent: not installed (UNMEASURED)")
        return 0
    if os.path.exists(os.path.join(st, "DISABLED")):
        print("telemetry DISABLED (state/DISABLED present): not kicking")
        return 0
    hb = read_json(os.path.join(st, "heartbeat.json"))
    agev = time.time() - hb["at"] if hb else None
    if agev is not None and agev < STALE_S:
        print(f"telemetryd heartbeat {agev:.0f}s old: ok (vm_error={hb.get('vm_error')})")
        return 0
    print(f"telemetryd heartbeat {'missing' if agev is None else f'{agev:.0f}s old'}: kicking RimMandrake\\Telemetry")
    if "--kick" in argv:
        r = subprocess.run([schtasks(), "/Run", "/TN", "RimMandrake\\Telemetry"], capture_output=True, text=True, timeout=60)
        print("kicked" if r.returncode == 0 else f"kick FAILED: {r.stderr.strip()}")
        return 0 if r.returncode == 0 else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
