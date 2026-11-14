#!/usr/bin/env python3
"""retired_loops_check: the recurring proof that the Relentless, Artisan and Whittle loops stay retired (owner 2026-11-13,
design/RimMandrake/retired_loops_2026-11-13.md; item RIMMANDRAKE_RETIRE_RELENTLESS_ARTISAN_WHITTLE_NOTHING_TO_RESUME).

Run by deadman_check each pass (rm-deadman.timer, every 15 min) as the arm `retired_loops`, so a failure reopens the one
fixed item LIVE_RESTORE_RETIRED_LOOPS and rings the phone (no AI in the path). Archmagi only: SteveDesktop is NOT covered.
It fails when (1) a unit named in the retirement doc is not masked, (2) any rm-relentless*, rm-artisan*, rm-whittle*,
rm-ralph* or whittle-claude@ unit is loaded (a masked unit reads load=masked and is fine) or its file is enabled,
(3) a relentless.py / ralph_*.py / whittle*.py worker process is alive, (4) systemd or ps cannot be read: UNMEASURED,
never a pass. A manual detached_helper.py run (rm-detached-* units) is not a violation.

    python3 src/RimMandrake/Utils/retired_loops_check.py        prints the reading, exit 1 on alarm/unmeasured
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

RETIRED_UNITS = (
    "rm-relentless.timer", "rm-relentless.service", "rm-relentless-release.timer", "rm-relentless-release.service",
    "rm-relentless-wake.path", "rm-relentless-wake.service", "rm-relentless-job@.service",
    "rm-store-ledger-diff.timer", "rm-store-ledger-diff.service",
    "rm-artisan-now.timer", "rm-artisan-now.service", "rm-whittle-now.timer", "rm-whittle-now.service",
    "whittle-claude@.service",
)
FORBIDDEN = re.compile(r"^(rm-relentless|rm-artisan|rm-whittle|rm-ralph|whittle-claude@)")
WORKER = re.compile(r"^(relentless\.py|ralph_[\w-]*\.py|whittle[\w-]*\.py)$")
UNMEASURED = "UNMEASURED"


def real_runner(argv):
    """-> (returncode, stdout). Raises on a missing binary or a hang; the caller turns that into UNMEASURED."""
    r = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout


def _rows(out):
    """Whitespace-split non-empty lines, a leading bullet glyph dropped."""
    rows = []
    for ln in out.splitlines():
        parts = ln.replace("●", " ").replace("*", " ").split()
        if parts:
            rows.append(parts)
    return rows


def judge(files_out, units_out, ps_out):
    """Pure. files_out: `list-unit-files --no-legend`; units_out: `list-units --all --plain --no-legend`; ps_out:
    `ps -eo pid,args`. -> {"status": "ok"|"alarm"|"unmeasured", "problems": [..], "line": str}."""
    files = {}
    for p in _rows(files_out):
        if len(p) >= 2:
            files[p[0]] = p[1]
    units = {}
    for p in _rows(units_out):
        if len(p) >= 3:
            units[p[0]] = (p[1], p[2])
    if not files or not any(re.search(r"\.(service|timer|socket|target|path)$", u) for u in files):
        return {"status": "unmeasured", "problems": [], "line": "UNMEASURED: no unit files readable from systemctl"}
    if not units:
        return {"status": "unmeasured", "problems": [], "line": "UNMEASURED: no units readable from systemctl list-units"}
    if not any(a.startswith("PID") for a in (ln.split()[0].upper() for ln in ps_out.splitlines()[:1] if ln.split())):
        return {"status": "unmeasured", "problems": [], "line": "UNMEASURED: ps output unreadable"}
    bad = []
    for u in RETIRED_UNITS:
        st = files.get(u)
        if st is None:
            bad.append("%s is not listed (retired units must stay masked)" % u)
        elif st not in ("masked", "masked-runtime"):
            bad.append("%s is %s, not masked" % (u, st))
    for u, st in sorted(files.items()):
        if FORBIDDEN.match(u) and (st.startswith("enabled") or st in ("linked", "linked-runtime", "alias")):
            bad.append("%s file is %s" % (u, st))
    for u, (load, active) in sorted(units.items()):
        if FORBIDDEN.match(u) and load not in ("masked", "not-found"):
            bad.append("%s is loaded (%s/%s)" % (u, load, active))
    for ln in ps_out.splitlines()[1:]:
        parts = ln.split()
        if len(parts) < 2 or not parts[0].isdigit():
            continue
        if any(WORKER.match(os.path.basename(a)) for a in parts[1:4]):   # the interpreter and script, never a brief's prose
            bad.append("worker process alive: pid %s %s" % (parts[0], " ".join(parts[1:4])[:100]))
    bad = list(dict.fromkeys(bad))
    if bad:
        return {"status": "alarm", "problems": bad,
                "line": "RETIRED LOOP BACK: %d problem(s): %s" % (len(bad), "; ".join(bad)[:600])}
    return {"status": "ok", "problems": [],
            "line": "retired loops stay off: %d units masked, none loaded, no worker process" % len(RETIRED_UNITS)}


def measure(runner=real_runner):
    """Read systemd and ps through runner(argv) -> (rc, out). Any failure is UNMEASURED."""
    try:
        outs = []
        for argv in (["systemctl", "--user", "list-unit-files", "--no-legend", "--no-pager"],
                     ["systemctl", "--user", "list-units", "--all", "--plain", "--no-legend", "--no-pager"],
                     ["ps", "-eo", "pid,args"]):
            rc, out = runner(argv)
            if rc != 0 or not isinstance(out, str):
                return {"status": "unmeasured", "problems": [],
                        "line": "UNMEASURED: %s exit %s" % (" ".join(argv[:3]), rc)}
            outs.append(out)
    except Exception as e:  # noqa: BLE001
        return {"status": "unmeasured", "problems": [], "line": "UNMEASURED: %s: %s" % (type(e).__name__, e)}
    return judge(*outs)


def arm_reason(result):
    """-> None when the loops are off, else the reason string deadman files (LIVE_RESTORE_RETIRED_LOOPS)."""
    return None if result["status"] == "ok" else result["line"]


def write_reading(path, result, now=None):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    tmp = str(path) + ".tmp"
    Path(tmp).write_text(json.dumps(dict(result, t=now or time.time(), steve_covered=False), indent=1), encoding="utf-8")
    os.replace(tmp, path)


def main():
    res = measure()
    print(res["line"])
    return 0 if res["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
