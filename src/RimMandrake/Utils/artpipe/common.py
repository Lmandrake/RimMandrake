#!/usr/bin/env python3
"""common.py — shared paths, atomic-write and job-dir helpers for artpipe.

Nothing here talks to codex, the network, or the rimflow ledger. It exists so
`artpiped.py`, `fill_queue.py` and `selftest_artpipe.py` agree on one
definition of "where is the queue" and "how do I write a JSON file without a
reader ever seeing a half-written one" instead of three subtly different
copies of the same twenty lines.

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import common

⚠️ RESIDUAL RISK, STATED HONESTLY RATHER THAN CLAIMED AWAY: this module's
atomic-claim helpers (`artpiped.py`'s `claim_next`/`reconcile`, both built on
`os.rename`) are proven correct by `selftest_artpipe.py` running on
`tempfile.TemporaryDirectory()` — real Linux tmpfs/ext4 inside the WSL2 VM.
Production runs on `/mnt/d` (DrvFs/9p), which this repo has ALREADY MEASURED
serving minutes-stale reads to a second process (see the owner's own
`drvfs-stale-reads-mimic-revert` note). The selftests demonstrate the CLAIM
LOGIC is correct; they do not demonstrate that DrvFs itself honors POSIX
rename atomicity under two real WSL processes racing the same file — that is
not independently measured here, and cannot be fixed from user space.
`claim_next`/`reconcile` mitigate by re-`stat()`-ing a path immediately after
renaming it and treating a stat that can't see it as a lost race, same as a
FileNotFoundError on the rename itself — a mitigation, not a proof. Watch
`throughput.jsonl` for duplicate or vanished ids if two daemons (or a daemon
and a human editing the queue by hand) are ever run against the real
`/mnt/d` queue at once.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

# this file -> artpipe -> Utils -> RimMandrake -> src -> repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
QUEUE_ROOT = REPO_ROOT / "infrastructure" / "artpipe"

DEFAULT_PENDING = QUEUE_ROOT / "pending"
DEFAULT_ACTIVE = QUEUE_ROOT / "active"
DEFAULT_DONE = QUEUE_ROOT / "done"
DEFAULT_FAILED = QUEUE_ROOT / "failed"
DEFAULT_ARTSRC = QUEUE_ROOT / "_artsrc"
DEFAULT_THROUGHPUT_LOG = QUEUE_ROOT / "throughput.jsonl"
DEFAULT_CODEX_HOME_ROOT = QUEUE_ROOT / "_codex_homes"

HERE = Path(__file__).resolve().parent
DEFAULT_WORKER_SCRIPT = (REPO_ROOT / "skills" / "generating-images" / "scripts"
                          / "codex_image.py")
DEFAULT_VALIDATOR = (REPO_ROOT / "skills" / "generating-rimworld-sprites"
                      / "scripts" / "validate_sprite.py")
MANIFEST_SCHEMA = HERE / "manifest.schema.json"
AGENTS_MD = HERE / "AGENTS.md"

# What a job file must carry (ART_PIPELINE_DAEMON_1's field list: id,
# rimflow item id, reference path, canvas, facings, style notes, priority —
# `prompt` is the daemon's own addition, since something has to carry the
# actual generation instruction the worker acts on).
REQUIRED_JOB_FIELDS = ("id", "rimflow_item_id", "canvas", "prompt")


class JobError(ValueError):
    """A job file is malformed — never silently coerced, always refused."""


def load_job(path: Path) -> dict:
    """Load and validate a job file — VALUE shapes, not just key presence.

    A job with `"canvas": {}` used to pass this function clean (the key was
    present) and then blow up as an uncaught KeyError deep inside
    build_job_prompt()'s `canvas['width']` — reached AFTER a worker slot had
    already been acquired, which is exactly the kind of exception that used
    to leak it permanently. Catching shape problems here, before
    process_job ever calls `ctx.slots.get()`, means a malformed job can
    never reach that code path at all.
    """
    try:
        job = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise JobError(f"{path}: unreadable job file — {exc}") from exc
    if not isinstance(job, dict):
        raise JobError(f"{path}: job file is not a JSON object")

    missing = [f for f in REQUIRED_JOB_FIELDS if f not in job]
    if missing:
        raise JobError(f"{path}: missing required field(s) {missing}")

    if job["id"] != path.stem:
        raise JobError(f"{path}: job id {job['id']!r} does not match filename "
                        f"{path.stem!r} — refusing to guess which is right")
    if not isinstance(job["id"], str) or not job["id"]:
        raise JobError(f"{path}: 'id' must be a non-empty string")
    if not isinstance(job["rimflow_item_id"], str) or not job["rimflow_item_id"]:
        raise JobError(f"{path}: 'rimflow_item_id' must be a non-empty string")
    if not isinstance(job["prompt"], str) or not job["prompt"].strip():
        raise JobError(f"{path}: 'prompt' must be a non-empty string")

    canvas = job["canvas"]
    if not isinstance(canvas, dict) or "width" not in canvas or "height" not in canvas:
        raise JobError(f"{path}: 'canvas' must be an object with 'width' and 'height'")
    for k in ("width", "height"):
        v = canvas[k]
        if not isinstance(v, int) or isinstance(v, bool) or v <= 0:
            raise JobError(f"{path}: canvas.{k} must be a positive integer, got {v!r}")

    ref = job.get("reference")
    if ref is not None and (not isinstance(ref, str) or not ref):
        raise JobError(f"{path}: 'reference' must be a non-empty string path or null")

    return job


def atomic_write_json(path: Path, obj: dict) -> None:
    """Write JSON so a reader never sees a half-written file.

    Same shape as atomic_copy.py's temp-then-replace: a per-call unique temp
    name beside the destination (same directory, same filesystem, so
    os.replace is a rename, not a copy across a boundary), never a fixed
    `<dst>.tmp` two callers could truncate into each other.
    """
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}.{time.time_ns()}")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n")
    os.replace(tmp, path)


def append_jsonl(path: Path, obj: dict) -> None:
    """Append one JSON line. One os.write syscall is one atomic append on
    POSIX for a line well under PIPE_BUF, which is what keeps two daemon
    processes from interleaving mid-line into throughput.jsonl."""
    line = (json.dumps(obj, sort_keys=True, default=str) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, line)
    finally:
        os.close(fd)


def id_taken(job_id: str, *dirs: Path) -> Path | None:
    """First directory among `dirs` that already holds a job file named
    `job_id` — or None if it is genuinely free everywhere checked."""
    for d in dirs:
        p = d / f"{job_id}.json"
        if p.is_file():
            return p
    return None


def ensure_queue_dirs(pending: Path, active: Path, done: Path, failed: Path,
                       artsrc: Path) -> None:
    for d in (pending, active, done, failed, artsrc):
        d.mkdir(parents=True, exist_ok=True)
