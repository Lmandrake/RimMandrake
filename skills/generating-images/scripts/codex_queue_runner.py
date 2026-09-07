#!/usr/bin/env python3
"""codex_queue_runner.py — N one-shot `codex exec` workers draining a file queue.

CODEX_PARALLEL_WORKERS_1's own architecture: NOT a persistent app-server
controller (that heavier design was reviewed and largely declined - see
`infrastructure/state/items/FOUNDRY_REBOOT_HANDOFF_202609070239.md`). This is
N parallel, independent `codex_image.py generate|edit` subprocess calls, each
against its own `--codex-home` (openai/codex #11435: parallel instances
cross-talk through a shared one), draining a plain directory of job files.

    codex_queue_runner.py init   --queue-root DIR
    codex_queue_runner.py submit --queue-root DIR --job-id ID --kind generate \
        --prompt "..." --out /abs/path.png [--image REF.png ...]
    codex_queue_runner.py run    --queue-root DIR --workers 4
    codex_queue_runner.py status --queue-root DIR

Queue layout (all under --queue-root):
    pending/<job_id>.json    submitted, unclaimed
    inflight/<job_id>.json   claimed by a worker (atomic rename FROM pending)
    done/<job_id>.json       job spec + manifest + timing + rate-limit reading
    failed/<job_id>.json     job spec + error
    .worker_homes/w<N>/      one CODEX_HOME per worker slot, seeded once

Each job's `out` directory gets a copy of `queue_worker_AGENTS.md` (the
receiving-agent contract) - `codex exec`'s cwd IS that directory
(`codex_image.py do_image`'s own `workdir = out.parent`), so this is where
AGENTS.md discovery actually looks.

Every job's manifest is captured two ways and cross-checked: `codex_image.py`'s
own harvest-by-directory-diff (the reliable one - CODEX_WRAPPER_HARVEST_FIX_1)
decides whether a file actually landed, and `--output-schema`/`-o` capture the
agent's own structured self-report for the `notes` field. A mismatch between
"a file landed" and "the agent claims a path" is recorded, not hidden.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import codex_grumpiness  # noqa: E402

CODEX_IMAGE = str(HERE / "codex_image.py")
AGENTS_MD_TEMPLATE = HERE.parent / "references" / "queue_worker_AGENTS.md"
MANIFEST_SCHEMA = HERE.parent / "references" / "queue_manifest.schema.json"

DEFAULT_TIMEOUT_S = 600
VALID_KINDS = ("generate", "edit")


# --------------------------------------------------------------------------
# queue directory plumbing
# --------------------------------------------------------------------------

def dirs(queue_root: Path) -> dict[str, Path]:
    return {
        "pending": queue_root / "pending",
        "inflight": queue_root / "inflight",
        "done": queue_root / "done",
        "failed": queue_root / "failed",
        "homes": queue_root / ".worker_homes",
    }


def init_queue(queue_root: Path) -> None:
    d = dirs(queue_root)
    for p in d.values():
        p.mkdir(parents=True, exist_ok=True)


def submit_job(queue_root: Path, job: dict) -> Path:
    """Write one job file into pending/. Atomic: write-temp-then-rename, so a
    worker never sees a half-written job (the same shape write_bridge_file uses
    elsewhere in this repo)."""
    d = dirs(queue_root)
    d["pending"].mkdir(parents=True, exist_ok=True)
    dest = d["pending"] / f"{job['job_id']}.json"
    tmp = dest.with_suffix(f".json.tmp.{os.getpid()}")
    tmp.write_text(json.dumps(job, indent=1), encoding="utf-8")
    os.replace(tmp, dest)
    return dest


def claim_job(queue_root: Path) -> Path | None:
    """Atomically move the oldest pending job into inflight/. None if empty.

    `os.rename` (same filesystem, same drive) is atomic - two workers racing
    this never both succeed on the same file. A worker that loses the race
    gets FileNotFoundError/OSError and just tries the next candidate.
    """
    d = dirs(queue_root)
    d["inflight"].mkdir(parents=True, exist_ok=True)
    if not d["pending"].is_dir():
        return None
    pending = sorted(d["pending"].glob("*.json"), key=lambda p: p.stat().st_mtime)
    for p in pending:
        dest = d["inflight"] / p.name
        try:
            os.rename(p, dest)
            return dest
        except FileNotFoundError:
            continue  # another worker claimed it first (p vanished under us)
    return None


def worker_home(queue_root: Path, slot: int) -> Path:
    return dirs(queue_root)["homes"] / f"w{slot}"


# --------------------------------------------------------------------------
# one job
# --------------------------------------------------------------------------

def ensure_agents_md(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "AGENTS.md"
    if not dest.is_file():
        dest.write_text(AGENTS_MD_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")


def run_one_job(job_path: Path, slot: int, queue_root: Path, timeout: int) -> dict:
    """Claim -> run codex_image.py -> read the manifest -> file done/failed.

    Returns the manifest dict that was written, for the caller to print/log.
    """
    job = json.loads(job_path.read_text(encoding="utf-8"))
    job_id = job["job_id"]
    kind = job["kind"]
    out = Path(job["out"]).resolve()
    ensure_agents_md(out.parent)

    home = worker_home(queue_root, slot)
    last_msg = home / f"{job_id}.last_message.json"
    last_msg.parent.mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, CODEX_IMAGE, kind,
           "--out", str(out), "--prompt", job["prompt"],
           "--codex-home", str(home),
           "--output-schema", str(MANIFEST_SCHEMA),
           "--output-last-message", str(last_msg),
           "--timeout", str(job.get("timeout", timeout))]
    if job.get("reasoning_effort"):
        cmd += ["--reasoning-effort", job["reasoning_effort"]]
    for img in job.get("images", []):
        cmd += ["--image", img]

    started_wall = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - started_wall

    manifest = {
        "job_id": job_id, "kind": kind, "out": str(out), "worker_slot": slot,
        "duration_s": round(elapsed, 1), "codex_image_exit": r.returncode,
        "file_landed": out.is_file(),
    }

    if last_msg.is_file():
        try:
            reported = json.loads(last_msg.read_text(encoding="utf-8"))
            manifest["agent_reported"] = reported
            # The cross-check the docstring promises: does the schema-validated
            # self-report agree with what actually landed on disk?
            reported_path = reported.get("path")
            if reported_path and Path(reported_path).resolve() != out:
                manifest["self_report_mismatch"] = (
                    f"agent reported {reported_path!r}, harvested file is at {out}")
        except (ValueError, OSError) as exc:
            manifest["agent_reported_error"] = str(exc)

    rl = codex_grumpiness.read_meters(home, after_mtime=started_wall)
    manifest["rate_limits"] = rl

    d = dirs(queue_root)
    d["done"].mkdir(parents=True, exist_ok=True)
    d["failed"].mkdir(parents=True, exist_ok=True)
    ok = manifest["file_landed"] and r.returncode == 0
    target = (d["done"] if ok else d["failed"]) / job_path.name
    if not ok:
        manifest["stderr_tail"] = (r.stderr or r.stdout or "")[-1500:]
    manifest_out = {**job, "manifest": manifest}
    target.write_text(json.dumps(manifest_out, indent=1), encoding="utf-8")
    job_path.unlink(missing_ok=True)  # remove from inflight/
    return manifest


def worker_loop(slot: int, queue_root: Path, timeout: int, results: list) -> None:
    while True:
        job_path = claim_job(queue_root)
        if job_path is None:
            return
        m = run_one_job(job_path, slot, queue_root, timeout)
        results.append(m)
        status = "OK  " if m["file_landed"] else "FAIL"
        print(f"[w{slot}] {status} {m['job_id']} ({m['duration_s']}s)"
              + (f"  grumpy={m['rate_limits'].get('grumpy')}"
                 if m["rate_limits"].get("ok") else ""), flush=True)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def cmd_init(a) -> int:
    init_queue(Path(a.queue_root))
    print(f"queue initialised at {a.queue_root}")
    return 0


def cmd_submit(a) -> int:
    if a.kind not in VALID_KINDS:
        print(f"ERROR --kind must be one of {VALID_KINDS}", file=sys.stderr)
        return 2
    if a.kind == "edit" and not a.image:
        print("ERROR --kind edit requires at least one --image", file=sys.stderr)
        return 2
    job = {"job_id": a.job_id, "kind": a.kind, "prompt": a.prompt,
           "out": str(Path(a.out).resolve()), "images": a.image or []}
    if a.reasoning_effort:
        job["reasoning_effort"] = a.reasoning_effort
    dest = submit_job(Path(a.queue_root), job)
    print(f"submitted {dest}")
    return 0


def cmd_run(a) -> int:
    queue_root = Path(a.queue_root)
    init_queue(queue_root)
    import threading
    results: list = []
    lock = threading.Lock()

    def _run(slot):
        local = []
        worker_loop(slot, queue_root, a.timeout, local)
        with lock:
            results.extend(local)

    threads = [threading.Thread(target=_run, args=(i,)) for i in range(a.workers)]
    started = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - started

    ok = sum(1 for m in results if m["file_landed"])
    print(f"\n{len(results)} job(s) drained by {a.workers} worker(s) in "
          f"{elapsed:.1f}s wall-clock — {ok} ok, {len(results) - ok} failed")
    return 0 if ok == len(results) else 1


def cmd_status(a) -> int:
    d = dirs(Path(a.queue_root))
    for name, p in d.items():
        if name == "homes":
            continue
        n = len(list(p.glob("*.json"))) if p.is_dir() else 0
        print(f"{name:10s} {n}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="create the queue directory skeleton")
    i.add_argument("--queue-root", required=True)
    i.set_defaults(func=cmd_init)

    s = sub.add_parser("submit", help="add one job to pending/")
    s.add_argument("--queue-root", required=True)
    s.add_argument("--job-id", required=True)
    s.add_argument("--kind", required=True, choices=VALID_KINDS)
    s.add_argument("--prompt", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--image", action="append", help="repeat for multiple (edit only)")
    s.add_argument("--reasoning-effort", default=None)
    s.set_defaults(func=cmd_submit)

    r = sub.add_parser("run", help="drain pending/ with N parallel workers")
    r.add_argument("--queue-root", required=True)
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    r.set_defaults(func=cmd_run)

    st = sub.add_parser("status", help="count jobs in each queue directory")
    st.add_argument("--queue-root", required=True)
    st.set_defaults(func=cmd_status)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
