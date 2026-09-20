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

🔴 `DEFAULT_CODEX_HOME_ROOT` is deliberately OUTSIDE this repo (see
`_default_codex_home_root()`) — an earlier version pointed inside it
(`infrastructure/artpipe/_codex_homes/`), and seeding a worker home copies
`auth.json` there. A `.gitignore` entry for that path is a backstop only;
never point `--codex-home-root` back inside the repo.

⚠️ A SEPARATE, NARROWER caveat for `acquire_codex_home_lease()`'s lockfiles,
which normally live under `DEFAULT_CODEX_HOME_ROOT` on `/mnt/c` (the Windows
user profile, not `/mnt/d`): `flock()` there coordinates ONLY the processes
sharing this ONE WSL distro's kernel/VFS view of that path. It does NOT
coordinate with a Windows-side process touching the same directory directly
(codex.exe itself never takes this lock — it doesn't know it exists), and it
does NOT coordinate with a SECOND WSL distro that also mounts `/mnt/c` — a
different distro's kernel holds its own, entirely independent lock state
over what is, from Windows' side, the same physical files. "Never lets two
live holders share one codex_home" is true only among daemons run from
*this* distro; a daemon started from a different WSL distro, or run
natively on Windows, is invisible to this lease mechanism entirely.
"""
from __future__ import annotations

import fcntl
import json
import os
import sys
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

HERE = Path(__file__).resolve().parent
DEFAULT_WORKER_SCRIPT = (REPO_ROOT / "skills" / "generating-images" / "scripts"
                          / "codex_image.py")
DEFAULT_GEMINI_WORKER_SCRIPT = (REPO_ROOT / "skills" / "generating-images" / "scripts"
                                / "gemini_image.py")
DEFAULT_VALIDATOR = (REPO_ROOT / "skills" / "generating-rimworld-sprites"
                      / "scripts" / "validate_sprite.py")
MANIFEST_SCHEMA = HERE / "manifest.schema.json"
AGENTS_MD = HERE / "AGENTS.md"


# --------------------------------------------------------------------------
# canvas law (FLORA_LEGIBILITY_BAR_1 spec item 3 / ART_PAINTERLY_RESTORATION_1)
# --------------------------------------------------------------------------
#
# ONE canonical implementation of "size (in cells) x 128 px/cell, rounded up
# to a power of two, floor 256" — the same law `gen_creature_register.py`,
# `gen_weapon_register.py`, `gen_furniture_register.py`, `gen_vehicle_register.py`
# and `gen_plant_register.py` each spell out inline as
# `clamp(ceil_pow2(cells * 128), 256, 1024)`, and `fill_queue.py`'s advisory
# ceiling check used to duplicate a fifth time. This is the one place that
# formula lives now; those callers may switch to it, and any FUTURE
# canvas-computing script (flora job authoring included) should call this
# rather than re-deriving the arithmetic.
#
# Floor 256 is the owner's prefer-higher tiebreak (ART_PAINTERLY_RESTORATION_1,
# 2026-09-14); 1024 is the image model's real ceiling per
# `generating-rimworld-sprites/SKILL.md` ("past ~1024-1280px you are
# upscaling, not adding detail").
CANVAS_FLOOR_PX = 256
CANVAS_CEILING_PX = 1024


def canvas_for_cells(cells: float) -> int:
    """cells (drawSize, or a plant's own mature-size measure) -> canvas edge
    px: ceil_pow2(cells * 128), clamped to [CANVAS_FLOOR_PX, CANVAS_CEILING_PX].
    `cells <= 0` is treated as 1.0 rather than raising — a caller with an
    unmeasured size should pass 1.0 itself and record that it did, not rely
    on this function to paper over it silently."""
    import math
    want = max(1.0, float(cells)) * 128.0
    px = CANVAS_FLOOR_PX
    while px < want and px < CANVAS_CEILING_PX:
        px *= 2
    return max(CANVAS_FLOOR_PX, min(CANVAS_CEILING_PX, px))


_CELLS_NOTE_RE = None  # compiled lazily — most callers never need it


def cells_from_register_note(note: str) -> float | None:
    """A flora register decision's free-text `note` sometimes carries an
    explicit cell count the owner wrote down himself — "5 cells wide", "5
    cells" — which is a MEASUREMENT (his own number), not a guess, and is
    more precise than the coarse small/medium/large/huge categorical sizeBin
    it sits beside. Returns None (never a guessed number) when no such
    pattern is present.

    Deliberately narrow: only "<number> cell(s)", optionally followed by one
    more word ("wide") — matches
    `design/Jawa/worldbuilding/review/flora_assignment_register.decisions.json`'s
    actual usage (checked 2026-09-17: "5 cells wide", "5 cells") and nothing
    fuzzier, so it never mis-parses an unrelated number in a longer note."""
    global _CELLS_NOTE_RE
    if _CELLS_NOTE_RE is None:
        import re
        _CELLS_NOTE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*cells?\b", re.IGNORECASE)
    if not note:
        return None
    m = _CELLS_NOTE_RE.search(note)
    return float(m.group(1)) if m else None


def _import_codex_image():
    """The one place this module reaches into codex_image.py — shared by
    `_default_codex_home_root()` and `codex_sandbox_preflight()` so both use
    the identical import path rather than two copies of the same
    sys.path dance."""
    sys.path.insert(0, str(REPO_ROOT / "skills" / "generating-images" / "scripts"))
    import codex_image  # noqa: E402
    return codex_image


def _default_codex_home_root() -> Path:
    """Where per-slot worker CODEX_HOMEs live — OUTSIDE the repo, always.

    `infrastructure/artpipe/_codex_homes/` (the original default) is inside
    this PUBLIC repo, and seeding a worker home copies `auth.json` into it —
    a credential leak, not a config choice. The owner has gitignored that
    path as a backstop; this function is the actual fix: never point there
    in the first place. Prefers the Windows user profile (codex.exe is a
    Windows binary, and a genuinely NEW home needs a one-time UAC-gated
    sandbox setup — see codex_image.py's own SANDBOX_SEED_* — so this must
    be a real persistent directory, never tmpfs/`/tmp`, or every restart
    re-pays that prompt). Falls back to a directory beside (never inside)
    the repo when no `/mnt/c` profile is discoverable at all — a WSL-only
    dev box with no Windows filesystem to use.
    """
    codex_image = _import_codex_image()
    wh = codex_image.windows_home()
    if wh is not None:
        return wh / ".codex_workers" / "artpipe"
    return REPO_ROOT.parent / "artpipe_codex_workers"


def codex_sandbox_preflight(base: Path | None = None) -> tuple[bool, str]:
    """Run ONCE at daemon startup, before ANY worker home is leased
    (CODEX_UAC_STORM_1, 2026-09-09) — the same check
    codex_image.seed_sandbox_from_template() runs per-home, done here once
    so a version-incompatible (or altogether missing) seed template blocks
    the WHOLE codex channel up front, instead of letting every one of N
    concurrent workers independently discover it by each trying (and
    failing, or UAC-prompting) its own first job.

    Returns (ok, message). `ok` is False for BOTH a proven "mismatch" and
    for "no_template" — this preflight cannot know whether a template-less
    machine will hit a *reachable* UAC prompt (a human happens to be
    watching) or an unattended one, so it treats "unknown" the same as
    "known bad": codex workers are refused, never let to gamble. The
    gemini channel is entirely unaffected — see main()'s own admission
    checks, which only gate the codex channel on this.
    """
    codex_image = _import_codex_image()
    try:
        resolved_base = base if base is not None else codex_image.base_codex_home()
    except codex_image.EnvError as exc:
        return False, f"cannot find the shared/base codex home to check against: {exc}"
    status, _template_fp, installed_fp, message = \
        codex_image.check_sandbox_fingerprint(resolved_base)
    if status == "match":
        return True, f"sandbox seed template matches the installed build ({installed_fp})"
    return False, message


DEFAULT_CODEX_HOME_ROOT = _default_codex_home_root()
MAX_CODEX_HOME_SLOTS = 64

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

    _refuse_contradicted_facing(path, job)

    return job


# Viewpoint phrases that CONTRADICT the per-facing direction build_job_prompt()
# stamps onto every job carrying a `facing`. The stamp tells the model "we see
# its BACK, no face, no eyes" for north and "NOT a top-down or overhead view"
# for east/west; a prompt body that also says "top-down pawn sprite, three
# facings" hands the model both instructions at once and lets it pick.
#
# MEASURED 2026-09-20 over the whole done/ queue: 348 jobs carry a facing, and
# **42 of them had the stamp fire while their own body said "top-down"** — the
# deeps_* v2 and rot_* v2 families. That is the mechanism behind the defect the
# owner has named repeatedly ("south isn't south, north isn't north",
# ARTPIPE_FACING_COHERENCE_1) — not a missing stamp, which has been in place
# since 2026-09-14, but a stamp being argued with.
#
# There is no exemption list and none is needed: the check only fires when the
# job declares a `facing`. An asset that genuinely wants an overhead view — a
# floor tile, a map icon — simply does not set one.
_FACING_CONTRADICTIONS = {
    "top-down": "an overhead camera, which the owner ruled is never a facing",
    "top down": "an overhead camera, which the owner ruled is never a facing",
    "overhead": "an overhead camera, which the owner ruled is never a facing",
    "three facings": "several facings at once, when this job draws exactly one",
    "four facings": "several facings at once, when this job draws exactly one",
    "all facings": "several facings at once, when this job draws exactly one",
}


def _refuse_contradicted_facing(path, job: dict) -> None:
    """Refuse a single-facing job whose prompt argues with its own stamp.

    ARTPIPE_FACING_COHERENCE_1 §1: a facing job that the hook has not stamped
    is refused "the same way the canvas ceiling refuses". The stamp itself was
    built 2026-09-14 (PYRELANDS_FACING_REGRESSION_1); this is the refusal half,
    and it catches the case the stamp cannot — a body that overrides it.
    """
    facing = job.get("facing")
    if not facing:
        return
    low = (job.get("prompt") or "").lower()
    hits = sorted(ph for ph in _FACING_CONTRADICTIONS if ph in low)
    if not hits:
        return
    why = "; ".join(f"{ph!r} asks for {_FACING_CONTRADICTIONS[ph]}" for ph in hits)
    raise JobError(
        f"{path}: this job declares facing {facing!r}, so the daemon stamps an "
        f"explicit per-facing view direction onto it — but the prompt body "
        f"contradicts that stamp: {why}. Say the SURFACE, never the camera or "
        f"the set: 'rear view, seen from behind, no face or eyes visible' / "
        f"'front view, eyes toward the viewer' / 'side profile at the "
        f"creature's own eye level'. If this asset really wants an overhead "
        f"view, drop the 'facing' key instead."
    )


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


def acquire_codex_home_lease(codex_home_root: Path, max_slots: int = MAX_CODEX_HOME_SLOTS):
    """Find (or reuse) a per-slot codex_home this process can hold
    exclusively. Returns (home_path, open_lockfile_handle) — keep the handle
    open for the daemon's whole lifetime; closing it (or the process dying)
    releases the lock immediately.

    Bounds growth WITHOUT naming a home after a pid: tries `w0`, `w1`, ...
    up to `max_slots`, `flock`-ing each candidate's lockfile non-blocking.
    A slot already held by a LIVE process fails the lock and this moves on
    to the next candidate — so two daemons never share one CODEX_HOME
    (openai/codex #11435's interference), without either naming homes after
    a pid (which accumulated one home per restart forever) or needing a
    separate dead-pid cleanup pass on start: a crashed process's flock is
    released by the kernel the instant it dies, so the very next daemon to
    probe that slot acquires it immediately, no cleanup step required.
    """
    codex_home_root.mkdir(parents=True, exist_ok=True)
    for i in range(max_slots):
        home = codex_home_root / f"w{i}"
        home.mkdir(parents=True, exist_ok=True)
        lock_path = home / ".artpipe_lease.lock"
        fh = open(lock_path, "a+")
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fh.close()
            continue
        fh.seek(0)
        fh.truncate()
        fh.write(f"pid={os.getpid()} acquired={time.time()}\n")
        fh.flush()
        return home, fh
    raise RuntimeError(
        f"no free codex_home lease among w0..w{max_slots - 1} under {codex_home_root} "
        f"— either genuinely {max_slots} daemons are live, or a lease is stuck")
