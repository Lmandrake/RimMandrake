#!/usr/bin/env python3
"""Guard (DEV_SCRATCH_DIRS_MIGRATE_OFF_LODESTARS_LAWN): rm-artpiped's live promise needs a reading the daemon
rewrites while it is alive, idle or busy. registry.jsonl moves only when a job finishes, so an idle, healthy daemon
broke the promise twice. The daemon's status heartbeat (every ~10 s, `console.Console.tick`) goes to a per-pid file
`artpiped_<pid>.json`, whose name a live line cannot hold; StatusFile must therefore also write the stable
`<status_dir>/heartbeat.json`, and that file must not match `--status`'s `artpiped_*.json` glob.

--reading NAME replays the instance: the basename the live promise reads (the broken one was registry.jsonl).
Exit 0 pass, 1 fail.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import console  # noqa: E402

STABLE = "heartbeat.json"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reading", default=STABLE, help="basename the live promise reads under the status dir")
    a = ap.parse_args(argv)
    fails = []
    with tempfile.TemporaryDirectory() as td:
        status_dir = Path(td) / "status"
        sf = console.StatusFile(status_dir, pid=4242)
        t0 = time.time()
        sf.write({"schema": 1, "pid": 4242, "updated_at": t0, "phase": "IDLE", "pending": 0, "in_flight": []})
        reading = status_dir / a.reading
        if not reading.is_file():
            fails.append(f"an idle status write leaves no {a.reading} — the live promise would age out on a live daemon")
        elif os.path.getmtime(reading) < t0 - 2:
            fails.append(f"{a.reading} not refreshed by the status write")
        if a.reading.startswith("artpiped_") and a.reading.endswith(".json"):
            fails.append(f"{a.reading} matches --status's artpiped_*.json glob")
        if getattr(console.StatusFile, "HEARTBEAT_NAME", None) != a.reading:
            fails.append(f"console.StatusFile.HEARTBEAT_NAME is {getattr(console.StatusFile, 'HEARTBEAT_NAME', None)!r}, "
                         f"not {a.reading!r}")
    for f in fails:
        print("FAIL", f)
    print("selftest_artpiped_heartbeat:", "FAIL" if fails else "ok")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
