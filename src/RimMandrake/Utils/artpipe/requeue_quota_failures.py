#!/usr/bin/env python3
"""requeue_quota_failures.py — put back jobs the daemon failed only because the
codex meter was exhausted ("You've hit your usage limit ... try again at HH:MM").

A quota failure is not an art rejection: the worker never ran. The daemon treats
failed/ as terminal, so without this the whole wave dies the moment the meter
trips (22 rut_* jobs did exactly that 2026-09-18 22:18 PDT, in 10 s).

    python3 requeue_quota_failures.py            # one pass
    python3 requeue_quota_failures.py --loop 600 # every 10 min until killed

Moves `failed/<id>.json` -> `pending/<id>.json` (a fresh claim for the daemon)
and parks the manifest under `<state>/_requeued_manifests/` so the failure
stays on the record. The queue is the artpipe STATE DIR (outside git since
2026-10-02; `artpipe_state.py where` prints it), resolved by state_dir; a
missing state dir is refused, never reported as "requeued 0". Never touches a manifest whose stderr does not carry the
quota sentence — a validator REJECT or a worker crash stays failed.
"""
from __future__ import annotations
import argparse, json, shutil, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state_dir  # noqa: E402

SENTENCE = "hit your usage limit"


def one_pass(art: Path, dry_run: bool = False) -> tuple[int, int]:
    """Returns (requeued, failed manifests examined). Before 2026-10-03 this read the
    pre-migration in-repo queue (infrastructure/artpipe), found no failed/ there and
    printed "requeued 0" forever; the examined count is printed so that cannot recur."""
    park = art / "_requeued_manifests"
    moved = seen = 0
    for man in sorted((art / "failed").glob("*.manifest.json")):
        seen += 1
        try:
            d = json.loads(man.read_text())
        except Exception:
            continue
        if SENTENCE not in (d.get("worker_stderr_tail") or ""):
            continue
        job = art / "failed" / man.name.replace(".manifest.json", ".json")
        if not job.exists():
            continue
        dest = art / "pending" / job.name
        if dest.exists():
            continue
        moved += 1
        if dry_run:
            print(f"would requeue {job.name}")
            continue
        park.mkdir(parents=True, exist_ok=True)
        shutil.move(str(job), str(dest))
        shutil.move(str(man), str(park / f"{man.stem}.{int(time.time())}.json"))
    return moved, seen


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--loop", type=int, default=0, help="seconds between passes; 0 = once")
    ap.add_argument("--state", type=Path, default=None, help="artpipe state dir (default: state_dir.STATE_ROOT)")
    ap.add_argument("--dry-run", action="store_true", help="name what would move, move nothing")
    a = ap.parse_args()
    art = state_dir.require(a.state)
    if not (art / "failed").is_dir() or not (art / "pending").is_dir():
        raise SystemExit(f"{art} has no failed/ or pending/; refusing to report 'requeued 0'")
    while True:
        n, seen = one_pass(art, a.dry_run)
        print(f"{time.strftime('%H:%M:%S')} {art}: requeued {n} of {seen} failed manifests", flush=True)
        if not a.loop:
            return 0
        time.sleep(a.loop)


if __name__ == "__main__":
    sys.exit(main())
