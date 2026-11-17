#!/usr/bin/env python3
"""RIMMANDRAKE_UNSTICK_PULSE_DEPLOY_GIT_SIXTEEN_TIMEOUTS_A_DAY: the checkout rm-deploy-update pulls must live on ext4.
On the drvfs mount (/mnt/*) one `git status` took 28.7 s under load and the 80 s pull budget timed out 16 times a day, twice
past the 3600 s last-good-pass limit (unit failed). Class guard: every place that names the deploy checkout (the unit files in
the repo, ops_watch.PULSE_DEPLOY) names the SAME path, and it is not under /mnt/. Worst value printed with the count read.

    python3 src/RimMandrake/Utils/pulse/selftest_pulse_deploy_on_ext4.py
"""
import re
import sys
from pathlib import Path

U = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(U))
import ops_watch as OW  # noqa: E402

FAILS = []


def check(msg, ok, *_):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


canon = OW.PULSE_DEPLOY
check(f"ops_watch.PULSE_DEPLOY is not on a Windows mount: {canon}", not canon.startswith("/mnt/"))
paths = []
for f in sorted((U / "systemd").glob("*.service")):
    txt = f.read_text(encoding="utf-8")
    for m in re.finditer(r"(?:RM_PULSE_DEPLOY=|ExecStart=-?/usr/bin/python3 )(/\S*?pulse-deploy)\b", txt):
        paths.append((f.name, m.group(1)))
check(f"instrument sees the unit references (read {len(paths)}, need >= 3)", len(paths) >= 3, paths)
bad = [(n, p) for n, p in paths if p != canon]
check(f"every unit reference equals the one deploy root (worst: {bad[:1] or 'none'}; {len(paths)} read)", not bad, bad)
sys.exit(1 if FAILS else 0)
