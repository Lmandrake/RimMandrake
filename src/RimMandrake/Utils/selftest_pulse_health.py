#!/usr/bin/env python3
"""selftest for pulse.py health (OPS_TIMER_REPAIR_EC51): rm-pulse-update restarts the spine, which takes ~6 s to serve; a
health run landing in that window must neither fail its unit (ops_watch reads a failed unit as TIMER_FAILED) nor restart
the spine a second time. Fakes only: no port, no systemd.

    python3 src/RimMandrake/Utils/selftest_pulse_health.py
"""
import io
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "pulse"))
import pulse  # noqa: E402


def run(answers):
    """-> (exit code, seconds slept, systemctl calls), each ask taking the next answer."""
    answers, slept, calls = list(answers), [], []

    def urlopen(url, timeout=None):
        a = answers.pop(0)
        if isinstance(a, Exception):
            raise a
        return io.BytesIO(json.dumps({"collected_at": time.time() - a}).encode())

    saved = urllib.request.urlopen, time.sleep, subprocess.run, pulse.append
    urllib.request.urlopen, time.sleep = urlopen, slept.append
    subprocess.run, pulse.append = lambda a, **k: calls.append(a), lambda *a, **k: None
    try:
        return pulse.health(True), sum(slept), calls
    finally:
        urllib.request.urlopen, time.sleep, subprocess.run, pulse.append = saved


def main():
    refused = ConnectionRefusedError("connection refused")
    assert run([2]) == (0, 0, []), "a fresh snapshot passes on the first ask"
    code, slept, calls = run([refused, 2])
    assert (code, calls) == (0, []) and slept == pulse.HEALTH_RETRY_S > 6, "a spine mid-restart gets a second ask"
    assert run([refused, refused])[0] == 1 and run([refused, refused])[2], "still down: fail and restart"
    assert run([300, 300])[0] == 1 and run([300, 300])[2], "answering but stale (a hang): fail and restart"
    unit = (HERE / "pulse/systemd/rm-pulse-health.service").read_text()
    limit = int(re.search(r"^TimeoutStartSec=(\d+)s$", unit, re.M).group(1))
    worst = 2 * pulse.HEALTH_ASK_S + pulse.HEALTH_RETRY_S + pulse.HEALTH_RESTART_S
    assert worst < limit, "worst run %d s must finish inside TimeoutStartSec %d s" % (worst, limit)
    print("selftest_pulse_health: ok")


if __name__ == "__main__":
    main()
