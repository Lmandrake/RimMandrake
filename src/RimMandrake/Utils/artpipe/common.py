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
    try:
        job = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise JobError(f"{path}: unreadable job file — {exc}") from exc
    missing = [f for f in REQUIRED_JOB_FIELDS if f not in job]
    if missing:
        raise JobError(f"{path}: missing required field(s) {missing}")
    if job["id"] != path.stem:
        raise JobError(f"{path}: job id {job['id']!r} does not match filename "
                        f"{path.stem!r} — refusing to guess which is right")
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
