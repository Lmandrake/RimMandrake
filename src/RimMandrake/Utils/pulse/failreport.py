"""One attempt of a job, for RimPulse (RIMPULSE_FAILURES_BUILD_ONLY_THE_STUCK, GPT rec 12).

    from failreport import report          # sys.path: src/RimMandrake/Utils/pulse
    report("build:FlowWorks", ok=False, cause="CS0103 in RM_Pump.cs", seat="FOUNDRY")
    report("build:FlowWorks", ok=True)

Appends one JSON line to <RM_PULSE_STATE or ~/.local/state/rm-dashboard>/failures.jsonl, which the daemon reads
every tick. RimPulse turns the records into history (a failure, then a recovery) and raises red ONLY when the
owner-relevant consequence holds: `lost=True` (the job's output is gone) or `blocks=True` (required work cannot go
on) with no success for 15 minutes. Routine agent iteration - a build that fails then passes - never alarms.

Never raises: a job must not fail because its report could not be written (it says so on stderr and returns
False). Stdlib only, so any tool can import it cheaply.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path


def failures_path() -> Path:
    return Path(os.environ.get("RM_PULSE_STATE", Path.home() / ".local" / "state" / "rm-dashboard")) / "failures.jsonl"


def report(task: str, ok: bool, cause: str | None = None, seat: str | None = None, blocks: bool = False,
           lost: bool = False, link: str | None = None) -> bool:
    rec = {"ts": time.time(), "task": str(task)[:80], "status": "ok" if ok else "failed"}
    if not ok:
        rec.update({k: v for k, v in (("cause", " ".join(str(cause or "").split())[:200] or None),
                                      ("blocks", bool(blocks) or None), ("lost", bool(lost) or None)) if v})
    if seat or os.environ.get("RIMFLOW_SEAT"):
        rec["seat"] = str(seat or os.environ["RIMFLOW_SEAT"]).upper()[:16]
    if link:
        rec["link"] = os.path.abspath(link)
    try:
        p = failures_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        # one write() of one short line on an O_APPEND fd: concurrent reporters never interleave inside a line
        fd = os.open(p, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            os.write(fd, (json.dumps(rec, ensure_ascii=False) + "\n").encode())
        finally:
            os.close(fd)
        return True
    except OSError as e:
        print(f"failreport: could not record {task}: {e}", file=sys.stderr)
        return False
