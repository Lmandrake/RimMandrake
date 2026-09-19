#!/usr/bin/env python3
"""requeue_quota_failures.py — put back jobs the daemon failed only because the
codex meter was exhausted ("You've hit your usage limit ... try again at HH:MM").

A quota failure is not an art rejection: the worker never ran. The daemon treats
failed/ as terminal, so without this the whole wave dies the moment the meter
trips (22 rut_* jobs did exactly that 2026-09-18 22:18 PDT, in 10 s).

    python3 requeue_quota_failures.py            # one pass
    python3 requeue_quota_failures.py --loop 600 # every 10 min until killed

Moves `failed/<id>.json` -> `pending/<id>.json` (a fresh claim for the daemon)
and parks the manifest under Transient/artpipe_quota_failures/ so the failure
stays on the record. Never touches a manifest whose stderr does not carry the
quota sentence — a validator REJECT or a worker crash stays failed.
"""
from __future__ import annotations
import argparse, json, shutil, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ART = ROOT / "infrastructure" / "artpipe"
PARK = ROOT / "Transient" / "artpipe_quota_failures"
SENTENCE = "hit your usage limit"


def one_pass() -> int:
    PARK.mkdir(parents=True, exist_ok=True)
    moved = 0
    for man in sorted((ART / "failed").glob("*.manifest.json")):
        try:
            d = json.loads(man.read_text())
        except Exception:
            continue
        if SENTENCE not in (d.get("worker_stderr_tail") or ""):
            continue
        job = ART / "failed" / man.name.replace(".manifest.json", ".json")
        if not job.exists():
            continue
        dest = ART / "pending" / job.name
        if dest.exists():
            continue
        shutil.move(str(job), str(dest))
        shutil.move(str(man), str(PARK / f"{man.stem}.{int(time.time())}.json"))
        moved += 1
    return moved


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--loop", type=int, default=0, help="seconds between passes; 0 = once")
    a = ap.parse_args()
    while True:
        n = one_pass()
        print(f"{time.strftime('%H:%M:%S')} requeued {n}", flush=True)
        if not a.loop:
            return 0
        time.sleep(a.loop)


if __name__ == "__main__":
    sys.exit(main())
