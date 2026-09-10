#!/usr/bin/env python3
"""selftest_artpipe.py — proves artpiped.py's mechanics without ever
touching real Codex.

Every scenario here drives `artpiped.py` as a real subprocess against a
throwaway tempdir queue, with `--worker-script mock_codex_worker.py` and
`$ARTPIPE_MOCK_CONTROL` steering that mock's behaviour per job id — the same
black-box style `selftest_cli.py` already uses in this repo, and for the
same reason: these are the daemon's actual claim/reconcile/detector/
validator code paths, not a hand-simulation of them. NEVER invokes real
codex.exe or generates a real image.

🔑 Fixture rule, learned the hard way: an active/ job must be produced by
`artpiped.claim_next()` (or by a real daemon run), never hand-written
directly into `active/`. An earlier version of `test_crash_reconciliation`
wrote straight into `active/` with today's mtime — which meant it could
never have caught the bug where `claim_next()` forgot to stamp a fresh
mtime after the rename (reconcile()'s age gate then measured time-since-
FILED instead of time-since-CLAIMED, and stole a job that had only been
claimed a moment ago). Going through the real claim path is what makes that
bug visible at all.

    python3 selftest_artpipe.py
"""
from __future__ import annotations

import json
import os
import queue
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
import artpiped  # noqa: E402
import mock_codex_worker  # noqa: E402 — reused directly for write_rollout() in a couple of tests

REPO_ROOT = HERE.parents[3]
sys.path.insert(0, str(REPO_ROOT / "skills" / "generating-images" / "scripts"))
import pnglib  # noqa: E402
import codex_grumpiness  # noqa: E402

MOCK_WORKER = HERE / "mock_codex_worker.py"
MOCK_GEMINI_WORKER = HERE / "mock_gemini_worker.py"
VALIDATOR = common.DEFAULT_VALIDATOR
SCHEMA = common.MANIFEST_SCHEMA

FAILED: list[str] = []


def ok(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"ok    {name}")
    else:
        FAILED.append(name)
        print(f"FAIL  {name}" + (f"\n      {detail}" if detail else ""))


# --------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------

def make_reference(path: Path, w: int = 64, h: int = 64) -> None:
    """64x64 RGBA: transparent border, a solid opaque 32x32 red box centred —
    enough geometry for validate_sprite.py's checks to have something to
    compare against."""
    rgba = bytearray(w * h * 4)
    box = (w - 32) // 2
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            if box <= x < box + 32 and box <= y < box + 32:
                rgba[i:i + 4] = bytes((200, 30, 30, 255))
    pnglib.write_rgba(str(path), w, h, bytes(rgba))


def job_dict(job_id: str, reference: Path | str | None, priority: int = 100,
             prompt: str = "a small weathered supply crate, top-down game sprite",
             channel: str = "codex") -> dict:
    return {
        "id": job_id, "rimflow_item_id": "SELFTEST_ARTPIPE",
        "reference": str(reference) if reference else None,
        "canvas": {"width": 64, "height": 64},
        "prompt": prompt,
        "style_notes": "", "priority": priority, "background": "transparent",
        "channel": channel, "facing": None, "facings": [],
    }


def make_job(pending_dir: Path, job_id: str, reference: Path | None,
             priority: int = 100, prompt: str | None = None,
             channel: str = "codex") -> Path:
    job = job_dict(job_id, reference, priority,
                   prompt or "a small weathered supply crate, top-down game sprite",
                   channel)
    dest = pending_dir / f"{job_id}.json"
    common.atomic_write_json(dest, job)
    return dest


class Queue:
    """One throwaway queue tree, with a fresh reference PNG ready to use."""

    def __init__(self, tmp: Path):
        self.root = tmp
        self.pending = tmp / "pending"
        self.active = tmp / "active"
        self.done = tmp / "done"
        self.failed = tmp / "failed"
        self.artsrc = tmp / "_artsrc"
        self.codex_homes = tmp / "_codex_homes"
        self.throughput_log = tmp / "throughput.jsonl"
        common.ensure_queue_dirs(self.pending, self.active, self.done,
                                  self.failed, self.artsrc)
        self.reference = tmp / "reference.png"
        make_reference(self.reference)

    def daemon_args(self, *extra: str) -> list[str]:
        return [sys.executable, str(HERE / "artpiped.py"),
                "--pending-dir", str(self.pending), "--active-dir", str(self.active),
                "--done-dir", str(self.done), "--failed-dir", str(self.failed),
                "--artsrc-dir", str(self.artsrc), "--codex-home-root", str(self.codex_homes),
                "--throughput-log", str(self.throughput_log),
                "--worker-script", str(MOCK_WORKER),
                "--gemini-worker-script", str(MOCK_GEMINI_WORKER),
                "--validator-script", str(VALIDATOR),
                "--manifest-schema", str(SCHEMA), "--poll-interval", "0.1",
                *extra]

    def run(self, control: dict, *extra: str, timeout: float = 60) -> subprocess.CompletedProcess:
        control_path = self.root / "control.json"
        control_path.write_text(json.dumps(control))
        env = dict(os.environ)
        env["ARTPIPE_MOCK_CONTROL"] = str(control_path)
        return subprocess.run(self.daemon_args(*extra), capture_output=True,
                               text=True, timeout=timeout, env=env)


# --------------------------------------------------------------------------
# scenarios
# --------------------------------------------------------------------------

def test_crash_reconciliation():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        # Explicit priorities: claim_next() sorts by (priority, name), and
        # "fresh" < "orphan" alphabetically would otherwise silently swap
        # which gets claimed first.
        make_job(q.pending, "orphan", q.reference, priority=1)
        make_job(q.pending, "fresh", q.reference, priority=2)

        # Both jobs go through the REAL claim path (claim_next), never a
        # hand-written active/ file — see this file's own module docstring
        # for why that distinction is the whole point of this test.
        orphan_active = artpiped.claim_next(q.pending, q.active)
        fresh_active = artpiped.claim_next(q.pending, q.active)
        ok("fixture: both jobs claimed via the real claim path",
           orphan_active is not None and fresh_active is not None
           and orphan_active.name == "orphan.json" and fresh_active.name == "fresh.json")

        # The ONLY hand-edit in this fixture: backdate the mtime claim_next()
        # just stamped, standing in for "15 minutes elapsed" on the orphan
        # only — never for "claim_next never touched this file".
        old = time.time() - 900
        os.utime(orphan_active, (old, old))

        proc = q.run({}, "--reconcile-only", "--reconcile-min-age", "600")
        ok("reconcile: exits 0", proc.returncode == 0, proc.stderr)
        ok("reconcile: the OLD claim is returned to pending/",
           (q.pending / "orphan.json").is_file() and not orphan_active.is_file())
        ok("reconcile: the FRESH claim (claimed moments ago) is left in active/, not stolen",
           fresh_active.is_file() and not (q.pending / "fresh.json").is_file())


def test_claim_next_stamps_fresh_mtime_not_filing_time():
    """Finding: reconcile()'s age gate reads st_mtime, but os.rename PRESERVES
    mtime — so before this fix, a job that sat in pending/ for 20 minutes
    before being claimed carried that 20-minute-old timestamp straight into
    active/, and reconcile() (or a second daemon's startup reconcile) would
    read a claim made one second ago as one stale enough to steal back."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_path = make_job(q.pending, "oldfiled", q.reference)
        old = time.time() - 1200  # filed 20 minutes ago
        os.utime(job_path, (old, old))

        claimed = artpiped.claim_next(q.pending, q.active)
        ok("claim: returns the claimed path", claimed is not None and claimed.name == "oldfiled.json")
        if claimed:
            age = time.time() - claimed.stat().st_mtime
            ok("claim: stamps a FRESH mtime, not the original ~20min-old filing time",
               age < 5, f"age={age:.1f}s (would read ~1200s on the old bug)")

            moved = artpiped.reconcile(q.active, q.pending, q.done, q.failed,
                                      q.throughput_log, min_age_s=600.0)
            ok("claim: a job filed >10min ago but claimed JUST NOW is not stolen by reconcile",
               not any(jid == "oldfiled" for jid, _ in moved) and claimed.is_file())


def test_row5_no_manifest_fails_request_not_account():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "row5job", q.reference)
        make_job(q.pending, "healthy_after", q.reference)
        proc = q.run({"row5job": "no_manifest", "healthy_after": "ok"}, "--once", "--workers", "1")
        ok("row5: daemon exits 0", proc.returncode == 0, proc.stderr)

        manifest = q.failed / "row5job.manifest.json"
        ok("row5: job lands in failed/", (q.failed / "row5job.json").is_file())
        ok("row5: manifest present", manifest.is_file())
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("row5: status failed", m.get("status") == "failed", str(m))
            ok("row5: detector_row is 5", m.get("detector_row") == 5, str(m))

        ok("row5: does NOT stop the account — the next job still succeeds",
           (q.done / "healthy_after.json").is_file())


def test_row1_rate_limit_hard_stop():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "ratelimited1", q.reference, priority=1)
        make_job(q.pending, "after1", q.reference, priority=2)
        make_job(q.pending, "after2", q.reference, priority=3)
        # workers=1 forces strict ordering: ratelimited1 must finish (and set
        # hard_stop) before the daemon ever considers claiming after1/after2.
        proc = q.run({"ratelimited1": "rate_limited", "after1": "ok", "after2": "ok"},
                      "--once", "--workers", "1")
        # Finding 5: exit code tracks whether work ACTUALLY REMAINS
        # (pending/), not merely whether a wedge happened — here after1/
        # after2 are genuinely still pending (blocked by the hard stop),
        # so this run correctly exits nonzero.
        ok("row1: daemon exits NONZERO — real work is still pending",
           proc.returncode != 0, proc.stdout + proc.stderr)
        ok("row1: the final line says WORK REMAINS", "WORK REMAINS" in proc.stdout,
           proc.stdout)
        ok("row1: ratelimited1 failed", (q.failed / "ratelimited1.json").is_file())

        m_path = q.failed / "ratelimited1.manifest.json"
        if m_path.is_file():
            m = json.loads(m_path.read_text())
            ok("row1: detector_row is 1", m.get("detector_row") == 1, str(m))

        ok("row1: hard stop blocked after1 — still pending, untouched",
           (q.pending / "after1.json").is_file())
        ok("row1: hard stop blocked after2 — still pending, untouched",
           (q.pending / "after2.json").is_file())
        ok("row1: nothing claimed into active/ afterward", not any(q.active.glob("*.json")))


def test_prompt_echo_does_not_cause_false_hard_stop():
    """Finding: _looks_rate_limited used to substring-match the WHOLE captured
    output, which under a failure dump (codex_image.py prints up to 2000
    chars of raw transcript to stderr on ANY error) routinely echoes the
    prompt back verbatim. A job whose own prompt/style text innocently
    contains throttle-adjacent phrasing must never trip the permanent
    account hard-stop — this drives the REAL daemon subprocess end to end,
    not just the pure _looks_rate_limited() unit check below."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "promptecho"
        prompt = ("a rusted industrial valve; note: the flow was rate limited "
                   "to reduce pressure on the corroded pipe")
        job = job_dict(job_id, q.reference, prompt=prompt)
        common.atomic_write_json(q.pending / f"{job_id}.json", job)

        proc = q.run({job_id: "tool_error_echo_prompt"}, "--once", "--workers", "1")
        ok("prompt-echo: daemon exits 0", proc.returncode == 0, proc.stderr)

        manifest = q.failed / f"{job_id}.manifest.json"
        ok("prompt-echo: job fails as a plain worker error", manifest.is_file())
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("prompt-echo: worker_status is worker_error, not rate_limited",
               m.get("worker_status") == "worker_error", str(m))
            ok("prompt-echo: detector_row is NOT 1 — no false hard-stop from the echoed prompt",
               m.get("detector_row") != 1, str(m))


def test_stale_output_never_accepted_after_worker_failure():
    """Finding: a stale _artsrc/<id>.png left by a PREVIOUS attempt used to
    be accepted as this run's output whenever the worker failed or timed
    out, because the exit code was ignored once image_present was true.
    Fix: delete the target output before spawning, and never file 'ok' off
    an image when the worker exited nonzero. This plants a genuinely valid
    stale file first, then a worker that fails WITHOUT touching that path."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "staleoutput"
        make_job(q.pending, job_id, q.reference)
        stale_path = q.artsrc / job_id / f"{job_id}.png"  # the real per-job scratch dir
        stale_path.parent.mkdir(parents=True, exist_ok=True)
        make_reference(stale_path)  # a genuinely valid image — just STALE
        ok("fixture: the stale file really is there before the run",
           stale_path.is_file())

        proc = q.run({job_id: "tool_error"}, "--once", "--workers", "1")
        ok("stale-output: daemon exits 0", proc.returncode == 0, proc.stderr)
        ok("stale-output: job fails despite a valid-looking stale file at its output path",
           (q.failed / f"{job_id}.json").is_file())
        manifest = q.failed / f"{job_id}.manifest.json"
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("stale-output: worker_status is worker_error, never 'ok'",
               m.get("worker_status") == "worker_error", str(m))
            ok("stale-output: status is failed", m.get("status") == "failed", str(m))
        ok("stale-output: the stale file was deleted before the worker ran "
           "(and the failing mock never recreated it)", not stale_path.is_file())


def test_nonzero_exit_never_trusted_even_with_a_fresh_looking_image():
    """The other half of the same finding: even when the worker DOES manage
    to write a perfectly valid image before dying (a kill mid-write, not a
    stale leftover), a nonzero exit must still fail the job — checked BEFORE
    image_present, never after."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "failwithimage"
        make_job(q.pending, job_id, q.reference)
        proc = q.run({job_id: "fail_with_image"}, "--once", "--workers", "1")
        ok("fail-with-image: daemon exits 0", proc.returncode == 0, proc.stderr)
        ok("fail-with-image: job fails despite a genuinely valid image on disk",
           (q.failed / f"{job_id}.json").is_file())
        ok("fail-with-image: never landed in done/", not (q.done / f"{job_id}.json").is_file())
        manifest = q.failed / f"{job_id}.manifest.json"
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("fail-with-image: worker_status is worker_error",
               m.get("worker_status") == "worker_error", str(m))


def test_validator_catches_bad_file():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "badimg", q.reference)
        make_job(q.pending, "goodimg", q.reference)
        proc = q.run({"badimg": "bad_image", "goodimg": "ok"}, "--once", "--workers", "2")
        ok("validator: daemon exits 0", proc.returncode == 0, proc.stderr)

        ok("validator: worker's 'ok' self-report is NOT trusted — job fails anyway",
           (q.failed / "badimg.json").is_file())
        bad_manifest = q.failed / "badimg.manifest.json"
        if bad_manifest.is_file():
            m = json.loads(bad_manifest.read_text())
            ok("validator: badimg validator verdict is REJECT", m.get("validator") == "REJECT", str(m))
            ok("validator: badimg findings are non-empty",
               bool(m.get("validator_findings")), str(m))

        ok("validator: a genuinely valid mutated candidate passes and lands in done/",
           (q.done / "goodimg.json").is_file())
        good_manifest = q.done / "goodimg.manifest.json"
        if good_manifest.is_file():
            m = json.loads(good_manifest.read_text())
            ok("validator: goodimg validator verdict is PASS", m.get("validator") == "PASS", str(m))


def test_cannot_validate_distinguished_from_reject():
    """Finding: run_validator collapsed every nonzero validate_sprite.py exit
    into REJECT. Exit 2 means unusable INPUT (e.g. a missing reference
    path), not a rejected image — a job whose reference happens to be
    wrong must be reported as its own kind of failure, never as though the
    worker had produced bad art."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "badrefpath"
        bogus_ref = str(q.root / "does_not_exist.png")
        job = job_dict(job_id, bogus_ref)
        common.atomic_write_json(q.pending / f"{job_id}.json", job)

        # ok_ignore_reference succeeds WITHOUT reading --image at all, so the
        # WORKER never trips over the bogus path — only the daemon's own
        # post-hoc run_validator() call does, which is exactly what this
        # test is isolating.
        proc = q.run({job_id: "ok_ignore_reference"}, "--once", "--workers", "1")
        ok("cannot-validate: daemon exits 0", proc.returncode == 0, proc.stderr)

        manifest_path = q.failed / f"{job_id}.manifest.json"
        ok("cannot-validate: job fails — a bad reference path is never a silent pass",
           manifest_path.is_file())
        if manifest_path.is_file():
            m = json.loads(manifest_path.read_text())
            ok("cannot-validate: validator verdict is CANNOT_VALIDATE, not REJECT",
               m.get("validator") == "CANNOT_VALIDATE", str(m))
            ok("cannot-validate: worker_status names a bad reference path, not an image defect",
               m.get("worker_status") == "bad_reference_path", str(m))


def test_fill_queue_verifies_reference_path_and_stores_absolute():
    """The other half of the same finding: fill_queue.py should catch a
    dangling reference at filing time, before a job carrying it ever
    reaches the daemon, and should store whatever real path it accepts as
    an ABSOLUTE path."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))

        bad_list = q.root / "bad_refs.json"
        bad_list.write_text(json.dumps([{
            "id": "missingref", "rimflow_item_id": "SELFTEST_ARTPIPE", "prompt": "x",
            "canvas_w": 64, "canvas_h": 64, "reference": str(q.root / "nope.png"),
        }]))
        fill = [sys.executable, str(HERE / "fill_queue.py"), "--input", str(bad_list),
                "--pending-dir", str(q.pending), "--active-dir", str(q.active),
                "--done-dir", str(q.done), "--failed-dir", str(q.failed)]
        proc = subprocess.run(fill, capture_output=True, text=True, timeout=30)
        ok("fill_queue: a dangling reference is refused at filing time, not later",
           proc.returncode != 0 and not (q.pending / "missingref.json").is_file(),
           proc.stdout + proc.stderr)

        good_list = q.root / "good_refs.json"
        good_list.write_text(json.dumps([{
            "id": "hasref", "rimflow_item_id": "SELFTEST_ARTPIPE", "prompt": "x",
            "canvas_w": 64, "canvas_h": 64,
            # relative path — fill_queue must resolve it to absolute.
            "reference": os.path.relpath(str(q.reference), start=str(q.root)),
        }]))
        fill2 = [sys.executable, str(HERE / "fill_queue.py"), "--input", str(good_list),
                 "--pending-dir", str(q.pending), "--active-dir", str(q.active),
                 "--done-dir", str(q.done), "--failed-dir", str(q.failed)]
        proc2 = subprocess.run(fill2, capture_output=True, text=True, cwd=str(q.root), timeout=30)
        ok("fill_queue: a real (relative) reference is accepted", proc2.returncode == 0,
           proc2.stdout + proc2.stderr)
        filed = q.pending / "hasref.json"
        if filed.is_file():
            stored = json.loads(filed.read_text())["reference"]
            ok("fill_queue: the stored reference path is absolute", os.path.isabs(stored), stored)


def test_fill_queue_blank_priority_cell_does_not_crash():
    """Finding: int(row.get('priority', 100)) crashes on a blank CSV cell,
    because csv.DictReader gives '' (a present, falsy value), not a
    missing key — int('') raises. A single blank cell in a big CSV must
    not take down the whole file's worth of otherwise-valid rows."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        csv_path = q.root / "art_list.csv"
        csv_path.write_text(
            "id,rimflow_item_id,prompt,canvas_w,canvas_h,priority\n"
            "blankprio,SELFTEST_ARTPIPE,a plain crate,64,64,\n"
        )
        fill = [sys.executable, str(HERE / "fill_queue.py"), "--input", str(csv_path),
                "--pending-dir", str(q.pending), "--active-dir", str(q.active),
                "--done-dir", str(q.done), "--failed-dir", str(q.failed)]
        proc = subprocess.run(fill, capture_output=True, text=True, timeout=30)
        ok("fill_queue: a blank priority cell does not crash the row",
           proc.returncode == 0, proc.stdout + proc.stderr)
        filed = q.pending / "blankprio.json"
        ok("fill_queue: the job is filed with the default priority",
           filed.is_file() and json.loads(filed.read_text()).get("priority") == 100)


def test_fill_queue_write_job_never_leaves_a_corrupt_id_blocking_file():
    """Below-cap note: write_job's O_EXCL create-and-write directly at the
    real destination path could leave a partially-written file there if the
    process died mid-write, permanently blocking every future refile of
    that id. The write-tmp-then-os.link pattern means dest only ever
    exists fully-formed or not at all. This proves the happy path still
    produces a complete, parseable file (the crash-mid-write case itself
    isn't simulable from here, but the ordering guarantee — write, close,
    THEN publish — is what the code review asked for and is what this
    exercises end to end)."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        art_list = q.root / "one.json"
        art_list.write_text(json.dumps([{
            "id": "linked", "rimflow_item_id": "SELFTEST_ARTPIPE", "prompt": "x",
            "canvas_w": 64, "canvas_h": 64,
        }]))
        fill = [sys.executable, str(HERE / "fill_queue.py"), "--input", str(art_list),
                "--pending-dir", str(q.pending), "--active-dir", str(q.active),
                "--done-dir", str(q.done), "--failed-dir", str(q.failed)]
        proc = subprocess.run(fill, capture_output=True, text=True, timeout=30)
        ok("fill_queue: files cleanly via write-tmp-then-link", proc.returncode == 0, proc.stderr)
        dest = q.pending / "linked.json"
        ok("fill_queue: the destination is a complete, parseable job file",
           dest.is_file() and json.loads(dest.read_text())["id"] == "linked")
        leftover_tmps = list(q.pending.glob(".linked.json.tmp.*"))
        ok("fill_queue: no leftover tmp file after a clean run", not leftover_tmps,
           [str(p) for p in leftover_tmps])


def test_two_concurrent_daemons_claim_atomically():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        n = 10
        control = {}
        for i in range(n):
            jid = f"race{i}"
            make_job(q.pending, jid, q.reference, priority=i)
            control[jid] = "ok"

        control_path = q.root / "control.json"
        control_path.write_text(json.dumps(control))
        env = dict(os.environ)
        env["ARTPIPE_MOCK_CONTROL"] = str(control_path)

        procs = [subprocess.Popen(q.daemon_args("--once", "--workers", "3"),
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, env=env)
                 for _ in range(2)]
        outs = [p.communicate(timeout=90) for p in procs]

        ok("atomicity: both daemons exit 0",
           all(p.returncode == 0 for p in procs),
           "\n".join(o[1] for o in outs))
        ok("atomicity: pending/ fully drained", not any(q.pending.glob("*.json")))
        ok("atomicity: active/ fully drained (no orphaned claim)", not any(q.active.glob("*.json")))

        # Exclude the *.manifest.json siblings — a bare glob("*.json") also
        # matches them, and "raceN.manifest.json".stem is "raceN.manifest",
        # not "raceN".
        done_ids = {p.stem for p in q.done.glob("*.json") if not p.name.endswith(".manifest.json")}
        failed_ids = {p.stem for p in q.failed.glob("*.json") if not p.name.endswith(".manifest.json")}
        ok("atomicity: every job accounted for exactly once, none lost",
           len(done_ids | failed_ids) == n,
           f"done={sorted(done_ids)} failed={sorted(failed_ids)}")
        ok("atomicity: no job claimed twice into both done/ and failed/",
           not (done_ids & failed_ids), f"overlap={done_ids & failed_ids}")
        manifests = list(q.done.glob("*.manifest.json")) + list(q.failed.glob("*.manifest.json"))
        ok("atomicity: exactly one manifest per job, no duplicates",
           len(manifests) == n, f"{len(manifests)} manifests for {n} jobs")

        # Finding 1 (this pass): codex_home dirs are now a bounded, LEASED
        # pool ("w0".."wN-1", no pid in the name) rather than one dir per
        # pid — so growth is bounded across restarts. The collision-safety
        # proof is different now: with --workers 3 on each of 2 daemons
        # running CONCURRENTLY, the flock lease means neither process can
        # ever be handed a slot the other is actively holding, so exactly
        # 2*3=6 DISTINCT slot dirs must exist (no sharing/reuse WITHIN one
        # concurrent run), and each slot's lockfile must name one of the
        # two real child pids — proving both processes actually acquired
        # leases, not just that six directories happen to exist.
        home_dirs = sorted(p for p in q.codex_homes.iterdir() if p.is_dir())
        ok("atomicity: exactly 2*workers distinct leased codex_home dirs, no cross-daemon reuse",
           len(home_dirs) == 6, f"home dirs: {[p.name for p in home_dirs]}")

        real_pids = {str(p.pid) for p in procs}
        lock_pids = set()
        for home in home_dirs:
            lock = home / ".artpipe_lease.lock"
            if lock.is_file():
                text = lock.read_text()
                m = re.search(r"pid=(\d+)", text)
                if m:
                    lock_pids.add(m.group(1))
        ok("atomicity: every leased home's lockfile names one of the two real daemon pids",
           lock_pids and lock_pids <= real_pids, f"lock_pids={lock_pids} real_pids={real_pids}")
        ok("atomicity: BOTH real daemon pids actually appear across the leases",
           lock_pids == real_pids, f"lock_pids={lock_pids} real_pids={real_pids}")


def test_dry_run_never_touches_the_queue():
    """Finding: --dry-run used to run through the REAL claim/finalize path
    with a synthetic "dry_run" status, which still renamed real jobs out of
    pending/ into active/ and then into done/ — permanently consuming the
    real queue and blocking a later real re-file as a duplicate id. Now it
    is a pure read: pending/ must be byte-for-byte unchanged afterward."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "dryjob", q.reference)
        before = (q.pending / "dryjob.json").read_bytes()

        # A control that would fail hard if the mock were ever actually
        # invoked — proves --dry-run really never spawns it.
        proc = q.run({"dryjob": "rate_limited"}, "--dry-run")
        ok("dry-run: daemon exits 0", proc.returncode == 0, proc.stderr)
        ok("dry-run: reports the job it would claim", "dryjob" in proc.stdout, proc.stdout)
        ok("dry-run: pending/dryjob.json is untouched, byte for byte",
           (q.pending / "dryjob.json").is_file()
           and (q.pending / "dryjob.json").read_bytes() == before)
        ok("dry-run: nothing moved into active/", not any(q.active.glob("*.json")))
        ok("dry-run: nothing moved into done/ or failed/",
           not any(q.done.glob("*.json")) and not any(q.failed.glob("*.json")))
        ok("dry-run: no image ever written to _artsrc/", not any(q.artsrc.rglob("*.png")))


def test_fill_queue_refuses_duplicate_id():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        art_list = q.root / "art_list.json"
        art_list.write_text(json.dumps([{
            "id": "dupcheck", "rimflow_item_id": "SELFTEST_ARTPIPE",
            "prompt": "x", "canvas_w": 64, "canvas_h": 64,
        }]))
        fill = [sys.executable, str(HERE / "fill_queue.py"), "--input", str(art_list),
                "--pending-dir", str(q.pending), "--active-dir", str(q.active),
                "--done-dir", str(q.done), "--failed-dir", str(q.failed)]
        first = subprocess.run(fill, capture_output=True, text=True, timeout=30)
        ok("fill_queue: first file succeeds", first.returncode == 0, first.stderr)
        second = subprocess.run(fill, capture_output=True, text=True, timeout=30)
        ok("fill_queue: second identical file is refused as duplicate",
           second.returncode != 0 and "REFUSED duplicate" in second.stderr,
           second.stdout + second.stderr)
        ok("fill_queue: pending/ still has exactly one dupcheck.json",
           len(list(q.pending.glob("dupcheck.json"))) == 1)


def test_load_job_validates_value_shapes_not_just_key_presence():
    """Finding: a job with "canvas": {} used to pass load_job's key-presence
    check cleanly and then KeyError deep inside build_job_prompt() — AFTER a
    worker slot had already been acquired, which used to leak it
    permanently. Catching this at load_job() means process_job never
    reaches ctx.slots.get() for a malformed job at all."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        bad = q.pending / "badcanvas.json"
        common.atomic_write_json(bad, {
            "id": "badcanvas", "rimflow_item_id": "SELFTEST_ARTPIPE",
            "canvas": {}, "prompt": "x",
        })
        try:
            common.load_job(bad)
            ok("load_job: rejects an empty canvas object", False,
               "load_job did not raise for canvas={}")
        except common.JobError as exc:
            ok("load_job: rejects an empty canvas object", True)
            ok("load_job: names the actual problem (canvas)", "canvas" in str(exc), str(exc))

        # And end to end: the daemon must fail this job cleanly rather than
        # crash, and must not leak a slot doing it (proven by a SECOND,
        # healthy job in the same --workers 1 run still completing).
        make_job(q.pending, "healthy", q.reference)
        proc = q.run({}, "--once", "--workers", "1")
        ok("load_job e2e: daemon exits 0 despite the malformed job", proc.returncode == 0, proc.stderr)
        ok("load_job e2e: the malformed job fails cleanly", (q.failed / "badcanvas.json").is_file())
        ok("load_job e2e: a healthy job filed alongside it still completes — no leaked slot",
           (q.done / "healthy.json").is_file())


# --------------------------------------------------------------------------
# in-process detector/helper unit checks — cheap, no subprocess needed
# --------------------------------------------------------------------------

def test_detector_meter_thresholds():
    """note_meters() now consumes codex_grumpiness.read_meters()'s own
    flattened return shape (`{"ok":.., "secondary_used_percent":..,
    "primary_used_percent":..}`), not a raw rate_limits object — see
    test_meters_flow_end_to_end for the real rollout-format proof; this is
    the pure threshold-logic check."""
    d = artpiped.Detector()
    d.note_meters({"ok": True, "secondary_used_percent": 82.0, "primary_used_percent": 10.0})
    ok("detector: 82% weekly warns but does not block", not d.admission_blocked())
    ok("detector: warn is logged once", d.warn_logged)

    d2 = artpiped.Detector()
    d2.note_meters({"ok": True, "secondary_used_percent": 91.0, "primary_used_percent": 10.0})
    ok("detector: 91% weekly refuses new claims", d2.admission_blocked() and d2.refuse_new)

    d3 = artpiped.Detector()
    d3.note_meters({"ok": True, "secondary_used_percent": 98.0, "primary_used_percent": 10.0})
    ok("detector: 98% weekly is a full stop", d3.admission_blocked() and d3.stop_all)

    d4 = artpiped.Detector()
    d4.note_meters({"ok": True, "secondary_used_percent": 5.0, "primary_used_percent": 72.0})
    ok("detector: 72% five-hour drops concurrency to 1", d4.current_n(3) == 1)

    d5 = artpiped.Detector()
    reset_at = time.time() + 9999
    d5.note_meters({"ok": True, "secondary_used_percent": 5.0,
                     "primary_used_percent": 91.0, "primary_resets_at": reset_at})
    ok("detector: 91% five-hour sleeps until resets_at",
       d5.admission_blocked() and d5.sleep_until == reset_at)

    d6 = artpiped.Detector()
    ok("detector: missing meter data blocks nothing (ignorance != 0%)",
       not d6.admission_blocked())
    d6.note_meters(None)
    ok("detector: None meters is a no-op", not d6.admission_blocked())
    d6.note_meters({"ok": False, "reason": "no rollout file found under this CODEX_HOME"})
    ok("detector: codex_grumpiness' own ok:False 'no data' shape is also a no-op",
       not d6.admission_blocked())


def test_meters_flow_end_to_end_through_codex_grumpiness():
    """Below-cap note honored via reuse: rather than re-implementing the
    rollout-parsing artpiped.py now imports
    skills/generating-images/scripts/codex_grumpiness.py for it. This proves
    the WHOLE chain works with that module's REAL rollout shape: mock writes
    a rollout the way codex_grumpiness actually reads it
    (payload.rate_limits, not a bare top-level key) -> the daemon's
    read_meters() call parses it -> Detector.note_meters() reacts to it."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "meterjob", q.reference)
        # Override into the 80-90% WARN band specifically, so the print is
        # unambiguous evidence the real value was read, not just any bucket.
        proc = q.run({"meterjob": {"behavior": "ok", "weekly": 85.0}}, "--once", "--workers", "1")
        ok("meters e2e: daemon exits 0", proc.returncode == 0, proc.stderr)
        ok("meters e2e: job succeeds (an 85% weekly warn doesn't fail the job)",
           (q.done / "meterjob.json").is_file())

        manifest = q.done / "meterjob.manifest.json"
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            after = m.get("meter_after") or {}
            ok("meters e2e: meter_after was actually read (ok:True) through codex_grumpiness",
               after.get("ok") is True, str(after))
            ok("meters e2e: secondary_used_percent reflects the mock's override (85)",
               after.get("secondary_used_percent") == 85.0, str(after))
        ok("meters e2e: row 2's warn message fired for the 80-90% band",
           "WARNING weekly Codex usage" in proc.stderr, proc.stderr)


def test_meter_after_never_reads_a_previous_jobs_rollout():
    """Below-cap note: meter_after used to read the newest rollout under a
    codex_home with NO floor — a worker that died before writing its own
    rollout would leave read_meters() reading whatever a PREVIOUS job on
    that reused slot last wrote, misattributing its meters to this job.
    Fixed by codex_grumpiness.read_meters(codex_home, after_mtime=...).
    Proven here directly at the read_meters level: an old rollout written
    before `after_mtime` must not be returned."""
    import codex_grumpiness
    with tempfile.TemporaryDirectory() as td:
        home = Path(td) / "codex_home"
        day_dir = home / "sessions" / "2026" / "01" / "01"
        day_dir.mkdir(parents=True)
        old_rollout = day_dir / "rollout-1-old.jsonl"
        old_rollout.write_text(json.dumps({
            "payload": {"type": "token_count", "info": {},
                        "rate_limits": {"primary": {"used_percent": 1.0},
                                        "secondary": {"used_percent": 1.0}}},
        }) + "\n")
        # Backdate it well before "job_started_at" below.
        old_time = time.time() - 100
        os.utime(old_rollout, (old_time, old_time))

        job_started_at = time.time()
        result = codex_grumpiness.read_meters(home, after_mtime=job_started_at)
        ok("meter_after: an old rollout (written before this job even started) "
           "is NOT returned for it", not result.get("ok"), str(result))

        # A rollout written AFTER job_started_at (simulating this job's own
        # worker actually producing one) IS returned.
        new_rollout = day_dir / "rollout-2-new.jsonl"
        new_rollout.write_text(json.dumps({
            "payload": {"type": "token_count", "info": {},
                        "rate_limits": {"primary": {"used_percent": 2.0},
                                        "secondary": {"used_percent": 3.0}}},
        }) + "\n")
        result2 = codex_grumpiness.read_meters(home, after_mtime=job_started_at)
        ok("meter_after: a rollout written by THIS job's own worker is returned",
           result2.get("ok") is True and result2.get("secondary_used_percent") == 3.0,
           str(result2))


def test_detector_wall_clock_halving():
    d = artpiped.Detector()
    slow = artpiped.BASELINE_WALL_CLOCK_S * artpiped.WALL_CLOCK_MULTIPLIER + 1
    for _ in range(2):
        d.note_wall_clock(slow, configured_n=4)
    ok("detector: two slow requests do not yet halve N", d.current_n(4) == 4)
    d.note_wall_clock(slow, configured_n=4)
    ok("detector: three consecutive >2x-baseline requests halve N", d.current_n(4) == 2)


def test_row6_timeout_language_never_reads_as_rate_limited():
    ok("row6: ordinary timeout text never matches the rate-limit detector",
       not artpiped._looks_rate_limited(
           "ERROR codex exec exceeded 150s after 151s and nothing new reached generated_images/"))
    ok("row6: an explicit TooManyRequests string DOES match",
       artpiped._looks_rate_limited("codex: TooManyRequests - rate limited"))


def test_rate_limit_marker_strips_prompt_echo_but_not_real_refusals():
    """Finding: _looks_rate_limited used to substring-match the WHOLE
    combined output, which under --verbose (or any failure dump) includes
    up to 4000 chars of raw transcript that routinely echoes the prompt
    back verbatim — a benign prompt phrase could trigger a permanent
    account hard-stop. Pure unit check of the mitigation (see
    test_prompt_echo_does_not_cause_false_hard_stop for the same thing
    proven through the real daemon subprocess)."""
    prompt = "a rusted valve; note the valve was rate limited to reduce flow"
    transcript_with_echo_only = f"--- last codex output ---\n{prompt}\nOK saved"

    ok("marker: stripping the prompt suppresses its own echoed phrasing",
       not artpiped._looks_rate_limited(transcript_with_echo_only, prompt))
    # Sanity: without stripping, the SAME text really would have triggered —
    # proving the mitigation does something, not vacuously passing because
    # the tightened marker list alone already missed it.
    ok("marker: (sanity) the unstripped haystack really did contain the phrase",
       artpiped._looks_rate_limited(transcript_with_echo_only, None))

    real_refusal = transcript_with_echo_only + "\ncodex: TooManyRequests"
    ok("marker: a genuine refusal alongside the same prompt still triggers",
       artpiped._looks_rate_limited(real_refusal, prompt))


# --------------------------------------------------------------------------
# fresh-review fixes (cf488dd8 -> this pass): 9 findings + Gemini backend
# --------------------------------------------------------------------------

def test_codex_home_root_default_is_outside_the_repo():
    """Finding: infrastructure/artpipe/_codex_homes/ was INSIDE this public
    repo, and seeding a worker home copies auth.json there — a credential
    leak, not a config choice. The real fix moves the default out; a
    .gitignore entry is a backstop only."""
    root = common.DEFAULT_CODEX_HOME_ROOT
    ok("codex-home-root: default is not inside the repo",
       common.REPO_ROOT not in root.parents and root != common.REPO_ROOT, str(root))


def test_codex_home_lease_bounds_growth_and_avoids_collision():
    """Finding: growth must be BOUNDED (no pid-in-name accumulation across
    restarts) while still never letting two live holders share one
    codex_home (openai/codex #11435's interference). Two separate open()
    calls on the same lockfile — even in one process — get two distinct
    open file descriptions, so this genuinely exercises flock contention,
    not just two Python objects agreeing not to collide."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        home1, fh1 = common.acquire_codex_home_lease(root, max_slots=4)
        home2, fh2 = common.acquire_codex_home_lease(root, max_slots=4)
        ok("lease: two concurrent leases get two DISTINCT slots", home1 != home2,
           f"{home1} vs {home2}")
        ok("lease: slot dirs are small bounded names, not pid-suffixed",
           home1.name in ("w0", "w1") and home2.name in ("w0", "w1"),
           f"{home1.name}, {home2.name}")

        fh1.close()  # release — simulates that holder's process exiting
        home1b, fh1b = common.acquire_codex_home_lease(root, max_slots=4)
        ok("lease: releasing a slot lets the NEXT acquire REUSE it, not grow",
           home1b == home1, f"{home1b} vs {home1}")

        existing_slots = [p for p in root.iterdir() if p.is_dir()]
        ok("lease: still only 2 slot directories exist after release+reuse (bounded)",
           len(existing_slots) == 2, [p.name for p in existing_slots])
        fh1b.close()
        fh2.close()


def test_reference_less_job_size_mismatch_is_caught():
    """Finding: a reference-less job used to accept ANY returned image as
    ok — validate_sprite.py is skipped entirely with no reference, and
    nothing else checked the size. The image tool is KNOWN to ignore
    requested size (design addendum §2.3) — this is the normal case."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "norefwrongsize"
        make_job(q.pending, job_id, None)  # no reference -> generate, validator skipped
        proc = q.run({job_id: "wrong_size"}, "--once", "--workers", "1")
        ok("size-check: daemon exits 0", proc.returncode == 0, proc.stderr)
        ok("size-check: a reference-less job with a size mismatch FAILS, never a silent ok",
           (q.failed / f"{job_id}.json").is_file())
        manifest = q.failed / f"{job_id}.manifest.json"
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("size-check: worker_status is size_mismatch",
               m.get("worker_status") == "size_mismatch", str(m))
            ok("size-check: width/height recorded in the manifest",
               m.get("width") == 32 and m.get("height") == 32, str(m))


def test_reference_less_job_correct_size_still_passes():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "norefrightsize"
        make_job(q.pending, job_id, None)
        proc = q.run({job_id: "ok"}, "--once", "--workers", "1")
        ok("size-check: daemon exits 0", proc.returncode == 0, proc.stderr)
        ok("size-check: a reference-less job with the RIGHT size still passes",
           (q.done / f"{job_id}.json").is_file())
        manifest = q.done / f"{job_id}.manifest.json"
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("size-check: width/height recorded even on the happy path",
               m.get("width") == 64 and m.get("height") == 64, str(m))
            ok("size-check: validator is 'skipped' (no reference), not a silent PASS",
               m.get("validator") == "skipped", str(m))


def test_worker_self_report_folded_into_manifest_and_detects_row1():
    """Finding: the worker's --output-last-message file was never READ,
    only deleted. Its structured content must fold into the daemon's own
    manifest and participate in row 1 detection — the spec names "-o last
    message" as a detection source, not just the raw transcript."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "refusedinmanifest"
        make_job(q.pending, job_id, q.reference)
        proc = q.run({job_id: "refused_rate_limit_in_manifest"}, "--once", "--workers", "1")
        # Finding 5: this hard-stops the codex Detector, but nothing else
        # was queued behind it — pending/ drains clean, so the daemon
        # correctly exits 0 (a wedge that leaves no work behind is not
        # "abandoned work"; see test_row1_rate_limit_hard_stop for the
        # contrasting case where real work IS left pending).
        ok("self-report: daemon exits 0 — the hard stop happened but nothing "
           "was left pending behind it", proc.returncode == 0, proc.stdout + proc.stderr)
        ok("self-report: the final line still reports hard_stop=True honestly",
           "hard_stop=True" in proc.stdout, proc.stdout)
        manifest = q.failed / f"{job_id}.manifest.json"
        ok("self-report: job fails", manifest.is_file())
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("self-report: detector_row is 1 — caught via the -o last-message note, "
               "not the (clean) transcript", m.get("detector_row") == 1, str(m))
            wsr = m.get("worker_self_report") or {}
            ok("self-report: the worker's own manifest is folded into the daemon's",
               wsr.get("status") == "refused" and "TooManyRequests" in (wsr.get("note") or ""),
               str(wsr))


def test_detector_deescalates_after_fresh_healthy_reading():
    """Finding: one 93% weekly reading used to wedge refuse_new/n_override
    FOREVER, even after the window resets. Every threshold must be
    RECOMPUTED from the current reading — only row 1's hard_stop stays
    latched."""
    d = artpiped.Detector()
    # WEEKLY_STOP is 97.0 — 98% is the stop_all band, not 93% (that's the
    # 90-97 refuse_new band, a different assertion below covers it).
    d.note_meters({"ok": True, "secondary_used_percent": 98.0, "primary_used_percent": 10.0})
    ok("deescalate: 98% weekly sets stop_all", d.stop_all and d.admission_blocked())

    d.note_meters({"ok": True, "secondary_used_percent": 1.0, "primary_used_percent": 1.0})
    ok("deescalate: a fresh 1% reading clears stop_all/refuse_new",
       not d.stop_all and not d.refuse_new and not d.admission_blocked())

    d1b = artpiped.Detector()
    d1b.note_meters({"ok": True, "secondary_used_percent": 93.0, "primary_used_percent": 10.0})
    ok("deescalate: 93% weekly (the 90-97 band) sets refuse_new, not stop_all",
       d1b.refuse_new and not d1b.stop_all and d1b.admission_blocked())
    d1b.note_meters({"ok": True, "secondary_used_percent": 1.0, "primary_used_percent": 1.0})
    ok("deescalate: a fresh 1% reading clears refuse_new too",
       not d1b.refuse_new and not d1b.admission_blocked())

    d2 = artpiped.Detector()
    d2.note_meters({"ok": True, "secondary_used_percent": 5.0, "primary_used_percent": 75.0})
    ok("deescalate: 75% five-hour drops to N=1", d2.current_n(4) == 1)
    d2.note_meters({"ok": True, "secondary_used_percent": 5.0, "primary_used_percent": 5.0})
    ok("deescalate: a fresh low five-hour reading restores full N",
       d2.current_n(4) == 4 and d2.n_override is None and d2.sleep_until is None)

    d3 = artpiped.Detector()
    d3.note_rate_limited()
    ok("deescalate: hard_stop is set", d3.hard_stop)
    d3.note_meters({"ok": True, "secondary_used_percent": 1.0, "primary_used_percent": 1.0})
    ok("deescalate: hard_stop STAYS latched even after a healthy reading — "
       "only row 1's state never clears", d3.hard_stop and d3.admission_blocked())


def test_detector_resets_at_coercion_never_crashes():
    """Finding: an ISO-string resets_at would TypeError the main thread
    comparing `time.time() < sleep_until`; a seconds-remaining value would
    silently no-op the sleep forever. Anything not a plain numeric epoch is
    treated as unknown — logged, falls back to the milder N=1 action,
    never crashes."""
    d = artpiped.Detector()
    d.note_meters({"ok": True, "secondary_used_percent": 5.0, "primary_used_percent": 95.0,
                   "primary_resets_at": "2026-09-10T00:00:00Z"})
    ok("resets_at: an ISO string does not crash the detector — reaching this line IS the proof",
       True)
    ok("resets_at: an unusable resets_at falls back to N=1, never a trusted sleep",
       d.sleep_until is None and d.n_override == 1)

    d2 = artpiped.Detector()
    d2.note_meters({"ok": True, "secondary_used_percent": 5.0, "primary_used_percent": 95.0,
                    "primary_resets_at": None})
    ok("resets_at: a missing resets_at falls back to N=1, never crashes",
       d2.sleep_until is None and d2.n_override == 1)

    d3 = artpiped.Detector()
    d3.note_meters({"ok": True, "secondary_used_percent": 5.0, "primary_used_percent": 95.0,
                    "primary_resets_at": {"weird": "object"}})
    ok("resets_at: non-scalar garbage does not crash the detector, falls back",
       d3.sleep_until is None and d3.n_override == 1)

    d4 = artpiped.Detector()
    good_epoch = time.time() + 500
    d4.note_meters({"ok": True, "secondary_used_percent": 5.0, "primary_used_percent": 95.0,
                    "primary_resets_at": good_epoch})
    ok("resets_at: a genuine numeric epoch IS trusted and used directly",
       d4.sleep_until == good_epoch and d4.n_override is None)


def test_exit_code_zero_on_clean_drain_with_healthy_meters():
    """The contrasting case to the row1/self-report tests above: a
    genuinely clean run — nothing wedged, nothing left behind — must still
    exit 0."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "healthyjob", q.reference)
        proc = q.run({"healthyjob": {"behavior": "ok", "weekly": 10.0}}, "--once", "--workers", "1")
        ok("exit-code: a genuinely clean drain exits 0", proc.returncode == 0,
           proc.stdout + proc.stderr)
        ok("exit-code: the final line says CLEAN DRAIN", "CLEAN DRAIN" in proc.stdout, proc.stdout)


def test_per_job_scratch_directory_is_real_not_shared():
    """Finding: AGENTS.md claimed per-job scratch dirs but codex_image.py
    sets its workdir to the shared _artsrc/ root — either make the code
    true or the doc honest. Fixed by giving each job a REAL subdirectory
    (out lives at _artsrc/<job_id>/<job_id>.png), which IS the worker's
    cwd (codex_image.py sets workdir = out.parent)."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "scratchA", q.reference)
        make_job(q.pending, "scratchB", q.reference)
        proc = q.run({"scratchA": "ok", "scratchB": "ok"}, "--once", "--workers", "2")
        ok("scratch: daemon exits 0", proc.returncode == 0, proc.stderr)
        a_png = q.artsrc / "scratchA" / "scratchA.png"
        b_png = q.artsrc / "scratchB" / "scratchB.png"
        ok("scratch: job A's output lives in ITS OWN per-job subdir", a_png.is_file())
        ok("scratch: job B's output lives in ITS OWN per-job subdir", b_png.is_file())
        ok("scratch: the two jobs do NOT share one flat directory — no <id>.png "
           "sitting directly in _artsrc/",
           not (q.artsrc / "scratchA.png").is_file() and not (q.artsrc / "scratchB.png").is_file())


def test_codex_one_retry_rescues_transient_failure():
    """Finding: row 1 spec requires ONE retry max on a failed request —
    none existed. fail_then_ok fails on invocation 1, succeeds on
    invocation 2; the mock's own invocation counter proves it was called
    exactly twice, never a third time."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "retryok"
        make_job(q.pending, job_id, q.reference)
        proc = q.run({job_id: "fail_then_ok"}, "--once", "--workers", "1")
        ok("retry: daemon exits 0", proc.returncode == 0, proc.stderr)
        ok("retry: the job succeeds after ONE retry", (q.done / f"{job_id}.json").is_file())
        manifest = q.done / f"{job_id}.manifest.json"
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("retry: daemon_attempts is 2", m.get("daemon_attempts") == 2, str(m))
        counter = q.artsrc / job_id / f".{job_id}.invocations"
        ok("retry: the mock was invoked exactly twice, never a third time",
           counter.is_file() and counter.read_text().strip() == "2",
           counter.read_text() if counter.is_file() else "no counter file")


def test_codex_retry_never_applied_to_rate_limited():
    """The other half: a throttle refusal must go straight to the hard
    stop, never spend the one retry on it."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "noretryratelimit"
        make_job(q.pending, job_id, q.reference)
        proc = q.run({job_id: "rate_limited"}, "--once", "--workers", "1")
        # Finding 5: exit code tracks remaining PENDING work, not merely a
        # wedge — a single job hard-stopping with nothing queued behind it
        # exits 0. hard_stop is still reported honestly in the log line.
        ok("no-retry: daemon exits 0 — nothing was left pending behind the wedge",
           proc.returncode == 0, proc.stdout + proc.stderr)
        ok("no-retry: hard_stop is still reported honestly", "hard_stop=True" in proc.stdout,
           proc.stdout)
        counter = q.artsrc / job_id / f".{job_id}.invocations"
        ok("no-retry: rate_limited is invoked EXACTLY ONCE — never retried",
           counter.is_file() and counter.read_text().strip() == "1",
           counter.read_text() if counter.is_file() else "no counter file")


def test_detector_wall_clock_uses_rolling_median_not_naive_last_three():
    """Finding: row 4 must be the ROLLING MEDIAN of the last 5 readings for
    3 consecutive calls — not "the last 3 readings were each individually
    slow". Sequence [200, 200, 1]: the naive "all of the last 3 above
    threshold" check would NOT fire (1 fails it), but the rolling median of
    [200, 200, 1] is 200, comfortably above 2x baseline — and this is the
    3rd consecutive call with a >threshold median, so it SHOULD fire. If
    this assertion fails, the old naive statistic crept back in."""
    d = artpiped.Detector()
    threshold = artpiped.BASELINE_WALL_CLOCK_S * artpiped.WALL_CLOCK_MULTIPLIER
    d.note_wall_clock(threshold + 76, configured_n=4)   # slow
    ok("median: 1 slow reading does not yet halve N", d.current_n(4) == 4)
    d.note_wall_clock(threshold + 76, configured_n=4)   # slow
    ok("median: 2 slow readings do not yet halve N", d.current_n(4) == 4)
    d.note_wall_clock(1.0, configured_n=4)              # a FAST outlier
    ok("median: a 3rd call whose window's ROLLING MEDIAN is still above "
       "threshold halves N, even though the raw 3rd reading itself was "
       "fast — proving this is the median statistic, not 'all of the last 3'",
       d.current_n(4) == 2)


def test_repair_completes_manifest_written_but_not_moved_crash():
    """Finding: reconcile() deliberately leaves this crash state (manifest
    written, job file never moved out of active/) for a human with no
    tool. --repair (folded into --reconcile-only) completes it."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "crashmidmove", q.reference)
        active_path = artpiped.claim_next(q.pending, q.active)
        ok("fixture: claimed via the real claim path", active_path is not None)
        # Simulate the crash: the manifest got written (as finalize_job's
        # FIRST step does) but the process died before moving the job file.
        common.atomic_write_json(q.done / "crashmidmove.manifest.json",
                                 {"id": "crashmidmove", "status": "ok", "channel": "codex"})
        ok("fixture: active/ file still sitting there (the crash state)", active_path.is_file())

        proc = q.run({}, "--reconcile-only", "--reconcile-min-age", "600")
        ok("repair: exits 0", proc.returncode == 0, proc.stderr)
        ok("repair: completed the move into done/", (q.done / "crashmidmove.json").is_file())
        ok("repair: active/ no longer holds the stuck file", not active_path.is_file())
        ok("repair: reported in the output", "repaired crashmidmove" in proc.stdout, proc.stdout)


def test_repair_leaves_genuinely_ambiguous_state_alone():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "ambiguous", q.reference)
        active_path = artpiped.claim_next(q.pending, q.active)
        common.atomic_write_json(q.done / "ambiguous.manifest.json",
                                 {"id": "ambiguous", "status": "ok"})
        common.atomic_write_json(q.failed / "ambiguous.manifest.json",
                                 {"id": "ambiguous", "status": "failed"})
        moved = artpiped.repair(q.active, q.done, q.failed)
        ok("repair: BOTH manifests existing is genuinely ambiguous — left alone",
           not any(jid == "ambiguous" for jid, _ in moved) and active_path.is_file())


def test_repair_standalone_flag_works_without_reconcile_only():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "repaironly", q.reference)
        active_path = artpiped.claim_next(q.pending, q.active)
        common.atomic_write_json(q.failed / "repaironly.manifest.json",
                                 {"id": "repaironly", "status": "failed"})
        proc = q.run({}, "--repair")
        ok("repair-only: exits 0", proc.returncode == 0, proc.stderr)
        ok("repair-only: completed the move into failed/", (q.failed / "repaironly.json").is_file())
        ok("repair-only: prints a repair-only summary", "repair-only" in proc.stdout, proc.stdout)
        ok("repair-only: active_path is gone", not active_path.is_file())


# --------------------------------------------------------------------------
# GEMINI_WORKER_BACKEND_1
# --------------------------------------------------------------------------

def test_gemini_channel_routes_and_records_cost():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "geminijob"
        make_job(q.pending, job_id, q.reference, channel="gemini")
        proc = q.run({job_id: "ok"}, "--once", "--workers", "1")
        ok("gemini: daemon exits 0", proc.returncode == 0, proc.stderr)
        ok("gemini: job succeeds via the mock gemini worker", (q.done / f"{job_id}.json").is_file())
        manifest = q.done / f"{job_id}.manifest.json"
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("gemini: channel recorded as gemini", m.get("channel") == "gemini", str(m))
            ok("gemini: cost_usd matches gemini-3-pro-image's known price",
               m.get("cost_usd") == 0.134, str(m))
            ok("gemini: model recorded", m.get("model") == "gemini-3-pro-image", str(m))
            ok("gemini: validator ran and passed", m.get("validator") == "PASS", str(m))
        lines = [json.loads(l) for l in q.throughput_log.read_text().splitlines() if l.strip()]
        # A pre-flight billing-INTENT row (finding 2) also carries
        # channel="gemini" — filter it out to isolate the actual
        # completion row this test cares about.
        gemini_lines = [l for l in lines
                        if l.get("channel") == "gemini" and l.get("record") != "intent"]
        ok("gemini: throughput.jsonl carries the channel + cost",
           len(gemini_lines) == 1 and gemini_lines[0].get("cost_usd") == 0.134, lines)


def test_gemini_bad_image_is_caught_by_revalidation_and_still_billed():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "geminibad"
        make_job(q.pending, job_id, q.reference, channel="gemini")
        proc = q.run({job_id: "bad_image"}, "--once", "--workers", "1")
        ok("gemini-bad: daemon exits 0", proc.returncode == 0, proc.stderr)
        ok("gemini-bad: job fails", (q.failed / f"{job_id}.json").is_file())
        manifest = q.failed / f"{job_id}.manifest.json"
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("gemini-bad: validator REJECT", m.get("validator") == "REJECT", str(m))
            ok("gemini-bad: still billed — the API call itself succeeded (exit 0)",
               m.get("cost_usd") == 0.134, str(m))


def test_gemini_api_error_never_billed():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "geminierror"
        make_job(q.pending, job_id, q.reference, channel="gemini")
        proc = q.run({job_id: "api_error"}, "--once", "--workers", "1")
        ok("gemini-error: daemon exits 0", proc.returncode == 0, proc.stderr)
        manifest = q.failed / f"{job_id}.manifest.json"
        ok("gemini-error: job fails", manifest.is_file())
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("gemini-error: NOT billed — the API call itself never succeeded",
               m.get("cost_usd") == 0.0, str(m))


def test_gemini_wrong_size_caught_independent_of_validator():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "geminiwrongsize"
        make_job(q.pending, job_id, None, channel="gemini")  # no reference — validator skipped
        proc = q.run({job_id: "wrong_size"}, "--once", "--workers", "1")
        ok("gemini-size: daemon exits 0", proc.returncode == 0, proc.stderr)
        manifest = q.failed / f"{job_id}.manifest.json"
        ok("gemini-size: job fails on size, not a silent ok", manifest.is_file())
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("gemini-size: worker_status is size_mismatch",
               m.get("worker_status") == "size_mismatch", str(m))


def test_gemini_budget_hard_stop():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "geminicap1", q.reference, priority=1, channel="gemini")
        make_job(q.pending, "geminicap2", q.reference, priority=2, channel="gemini")
        # gemini-3-pro-image costs $0.134/image — cap at one image's worth
        # so the second job is refused before it ever runs.
        proc = q.run({"geminicap1": "ok", "geminicap2": "ok"},
                     "--once", "--workers", "1", "--gemini-budget-usd", "0.134")
        ok("gemini-budget: daemon exits nonzero (a wedge, per finding 5)",
           proc.returncode != 0, proc.stdout + proc.stderr)
        ok("gemini-budget: the first job spends the budget and succeeds",
           (q.done / "geminicap1.json").is_file())
        ok("gemini-budget: the second job is NEVER claimed — still pending",
           (q.pending / "geminicap2.json").is_file())
        ok("gemini-budget: nothing claimed into active/ afterward",
           not any(q.active.glob("*.json")))


def test_gemini_budget_is_durable_across_restarts():
    """Cost is tracked in throughput.jsonl and the cap is read from it — a
    SECOND daemon invocation (simulating a restart) must inherit the spend
    already recorded, not start counting from zero."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "restart1", q.reference, channel="gemini")
        proc1 = q.run({"restart1": "ok"}, "--once", "--workers", "1",
                      "--gemini-budget-usd", "1000")
        ok("gemini-restart: first run succeeds", proc1.returncode == 0, proc1.stderr)
        ok("gemini-restart: first job done", (q.done / "restart1.json").is_file())

        make_job(q.pending, "restart2", q.reference, channel="gemini")
        proc2 = q.run({"restart2": "ok"}, "--once", "--workers", "1",
                      "--gemini-budget-usd", "0.10")
        ok("gemini-restart: second (fresh) run exits nonzero — already over budget",
           proc2.returncode != 0, proc2.stdout + proc2.stderr)
        ok("gemini-restart: second job never claimed", (q.pending / "restart2.json").is_file())
        ok("gemini-restart: the refusal is logged before any claim attempt",
           "already at/over its $0.10 budget" in proc2.stderr, proc2.stderr)


def test_gemini_never_touches_codex_homes():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "onlygemini", q.reference, channel="gemini")
        proc = q.run({"onlygemini": "ok"}, "--once", "--workers", "2")
        ok("gemini-isolation: daemon exits 0", proc.returncode == 0, proc.stderr)
        ok("gemini-isolation: the job succeeds", (q.done / "onlygemini.json").is_file())
        no_homes = not q.codex_homes.is_dir() or not any(q.codex_homes.iterdir())
        ok("gemini-isolation: NO codex_home directory was ever created for a gemini-only run",
           no_homes, list(q.codex_homes.iterdir()) if q.codex_homes.is_dir() else "codex_homes/ absent")


def test_mixed_channel_queue_codex_wedge_does_not_block_gemini():
    """A codex hard-stop must not stall gemini jobs sitting in the same
    queue, and vice versa — claim_next()'s channel_blocked filtering."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "codexratelimited", q.reference, priority=1, channel="codex")
        make_job(q.pending, "geminihealthy", q.reference, priority=2, channel="gemini")
        proc = q.run({"codexratelimited": "rate_limited", "geminihealthy": "ok"},
                     "--once", "--workers", "1")
        # Finding 5: both jobs are fully accounted for (one failed, one
        # done) and nothing is left pending — a clean drain, exit 0, even
        # though the codex channel genuinely wedged along the way.
        ok("mixed: daemon exits 0 — nothing left pending despite the codex wedge",
           proc.returncode == 0, proc.stdout + proc.stderr)
        ok("mixed: hard_stop is still reported honestly", "hard_stop=True" in proc.stdout,
           proc.stdout)
        ok("mixed: the codex job hard-stopped", (q.failed / "codexratelimited.json").is_file())
        ok("mixed: the UNRELATED gemini job still got claimed and finished",
           (q.done / "geminihealthy.json").is_file())


def test_fill_queue_channel_flag_and_per_row_override():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        art_list = q.root / "mixed.json"
        art_list.write_text(json.dumps([
            {"id": "viagemini", "rimflow_item_id": "SELFTEST_ARTPIPE", "prompt": "x",
             "canvas_w": 64, "canvas_h": 64},
            {"id": "viacodexoverride", "rimflow_item_id": "SELFTEST_ARTPIPE", "prompt": "x",
             "canvas_w": 64, "canvas_h": 64, "channel": "codex"},
        ]))
        fill = [sys.executable, str(HERE / "fill_queue.py"), "--input", str(art_list),
                "--pending-dir", str(q.pending), "--active-dir", str(q.active),
                "--done-dir", str(q.done), "--failed-dir", str(q.failed),
                "--channel", "gemini"]
        proc = subprocess.run(fill, capture_output=True, text=True, timeout=30)
        ok("fill_queue --channel: exits 0", proc.returncode == 0, proc.stdout + proc.stderr)
        job1 = json.loads((q.pending / "viagemini.json").read_text())
        ok("fill_queue --channel: --channel gemini applies when the row is silent",
           job1.get("channel") == "gemini", job1)
        job2 = json.loads((q.pending / "viacodexoverride.json").read_text())
        ok("fill_queue --channel: a row's own 'channel' overrides --channel",
           job2.get("channel") == "codex", job2)


# --------------------------------------------------------------------------
# third review (477dfb06 -> this pass): 7 confirmed findings + 4 lower notes
# --------------------------------------------------------------------------

def _write_stub_script(path: Path, body: str) -> Path:
    path.write_text("#!/usr/bin/env python3\n" + body)
    return path


def test_run_validator_never_raises_on_timeout_or_bad_exit():
    """Finding 1 (half): run_validator's bare subprocess.run(timeout=60)
    used to be able to raise TimeoutExpired straight into its caller — and
    ANY non-{0,1,2} exit used to be folded into "cannot_validate" (finding
    4), blaming the job's reference for the validator's own crash. Direct
    unit test of run_validator() itself, with real (fast) stub scripts —
    no need to actually wait out the real 60s timeout to prove the
    exception path is closed: a short custom timeout on a script that
    sleeps past it exercises the identical code path."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        sleepy = _write_stub_script(tdp / "sleepy_validator.py",
                                     "import time\ntime.sleep(5)\n")
        crashy = _write_stub_script(tdp / "crashy_validator.py",
                                     "import sys\nsys.exit(42)\n")
        ref = tdp / "ref.png"
        make_reference(ref)
        cand = tdp / "cand.png"
        make_reference(cand)

        verdict, findings = artpiped.run_validator(sleepy, str(ref), cand, timeout=0.5)
        ok("run_validator: a hung validator returns 'validator_error', never raises",
           verdict == "validator_error", (verdict, findings))
        ok("run_validator: the timeout is named in the findings", any("s" in f for f in findings),
           findings)

        verdict2, findings2 = artpiped.run_validator(crashy, str(ref), cand, timeout=10)
        ok("run_validator: an exit code outside 0/1/2 (a crash) is 'validator_error', "
           "NOT folded into 'cannot_validate' (finding 4)", verdict2 == "validator_error",
           (verdict2, findings2))
        ok("run_validator: the bad exit code is named", any("42" in f for f in findings2), findings2)

        missing = tdp / "does_not_exist.py"
        verdict3, findings3 = artpiped.run_validator(missing, str(ref), cand, timeout=10)
        ok("run_validator: a missing/non-executable validator script also "
           "returns 'validator_error', never raises", verdict3 == "validator_error",
           (verdict3, findings3))


def test_validator_crash_reported_as_validator_error_not_bad_reference_end_to_end():
    """Finding 4, end to end through the real daemon: point --validator-script
    at a script that exits a nonstandard code (simulating the validator
    itself being broken) against a job with a perfectly GOOD reference —
    the daemon must blame the validator, not the job's reference."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        tdp = Path(td)
        crashy = _write_stub_script(tdp / "crashy_validator.py", "import sys\nsys.exit(42)\n")
        job_id = "validatorcrash"
        make_job(q.pending, job_id, q.reference)
        proc = q.run({job_id: "ok"}, "--once", "--workers", "1",
                     "--validator-script", str(crashy))
        ok("validator-crash e2e: daemon exits 0", proc.returncode == 0, proc.stderr)
        manifest = q.failed / f"{job_id}.manifest.json"
        ok("validator-crash e2e: job fails", manifest.is_file())
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("validator-crash e2e: worker_status is validator_could_not_run, "
               "NOT bad_reference_path", m.get("worker_status") == "validator_could_not_run",
               str(m))
            ok("validator-crash e2e: validator field is ERROR, not CANNOT_VALIDATE",
               m.get("validator") == "ERROR", str(m))


def test_gemini_validator_error_preserves_channel_and_bills_correctly():
    """Finding 1, end to end: a gemini job whose IMAGE generation genuinely
    succeeded (billable) but whose VALIDATION step then breaks (the
    validator itself crashes) must still land with channel=gemini and the
    correct cost recorded — not silently miscounted as codex."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        tdp = Path(td)
        crashy = _write_stub_script(tdp / "crashy_validator.py", "import sys\nsys.exit(42)\n")
        job_id = "geminivalidatorcrash"
        make_job(q.pending, job_id, q.reference, channel="gemini")
        proc = q.run({job_id: "ok"}, "--once", "--workers", "1",
                     "--validator-script", str(crashy))
        ok("gemini-validator-crash: daemon exits 0", proc.returncode == 0, proc.stderr)
        manifest = q.failed / f"{job_id}.manifest.json"
        ok("gemini-validator-crash: job fails", manifest.is_file())
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("gemini-validator-crash: channel is STILL gemini, never defaulted to codex",
               m.get("channel") == "gemini", str(m))
            ok("gemini-validator-crash: the image WAS generated so this IS billed "
               "(the validator breaking afterward doesn't refund it)",
               m.get("cost_usd") == 0.134, str(m))
            ok("gemini-validator-crash: worker_status is validator_could_not_run",
               m.get("worker_status") == "validator_could_not_run", str(m))
        lines = [json.loads(l) for l in q.throughput_log.read_text().splitlines() if l.strip()]
        gemini_lines = [l for l in lines
                        if l.get("channel") == "gemini" and l.get("record") != "intent"]
        ok("gemini-validator-crash: throughput.jsonl correctly attributes the "
           "cost to gemini, not codex",
           len(gemini_lines) == 1 and gemini_lines[0].get("cost_usd") == 0.134, lines)


def test_process_job_exception_safety_net_preserves_gemini_channel_and_cost():
    """Direct pin of finding 1's exact original mechanism: an unexpected
    exception raised INSIDE process_gemini_job (run_validator's own
    subprocess.run used to be able to raise TimeoutExpired straight
    through it, before this whole review pass) must never surface as a
    result missing 'channel' — that is what let finalize_job default a
    REAL gemini job to "codex" and permanently under-count the durable
    budget. Proven by monkeypatching process_gemini_job to raise, in
    process, and calling process_job() directly — the cheapest, most
    precise way to pin this exact safety net without needing a real
    subprocess to misbehave."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "explodes"
        job_path = make_job(q.pending, job_id, q.reference, channel="gemini")

        class _CtxStub:
            artsrc_dir = q.artsrc

        def boom(*_a, **_k):
            raise RuntimeError("simulated unexpected failure deep inside process_gemini_job")

        original = artpiped.process_gemini_job
        artpiped.process_gemini_job = boom
        try:
            result = artpiped.process_job(job_path, _CtxStub())
        finally:
            artpiped.process_gemini_job = original

        ok("safety-net: the result from a raised exception still carries channel=gemini",
           result.get("channel") == "gemini", result)
        ok("safety-net: cost_usd is a safe 0.0, never missing/None",
           result.get("cost_usd") == 0.0, result)
        ok("safety-net: status is failed", result.get("status") == "failed", result)


def test_reconcile_ignores_worker_last_message_sidecar():
    """Finding 2: a naive `*.json` glob over active/ also matches
    <id>.worker_last_message.json (it ends in .json too) — reconcile()
    used to treat it as a phantom job (job_id = "foo.worker_last_message",
    a bogus id no manifest will ever exist for) and promote it to
    pending/, where it gets claimed, fails common.load_job's required-
    field check, and is written into throughput.jsonl as a fake failed
    job."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "orphanwithsidecar"
        make_job(q.pending, job_id, q.reference)
        claimed = artpiped.claim_next(q.pending, q.active)
        ok("fixture: claimed via the real claim path", claimed is not None)
        sidecar = q.active / f"{job_id}.worker_last_message.json"
        sidecar.write_text(json.dumps({"id": job_id, "status": "ok", "note": "x"}))
        old = time.time() - 1200
        os.utime(claimed, (old, old))
        os.utime(sidecar, (old, old))

        moved = artpiped.reconcile(q.active, q.pending, q.done, q.failed,
                                  q.throughput_log, min_age_s=600.0)
        ok("reconcile: the real orphaned job is reconciled back to pending",
           any(jid == job_id for jid, _ in moved), moved)
        ok("reconcile: the sidecar is NEVER promoted to pending as a phantom job",
           not (q.pending / f"{job_id}.worker_last_message.json").is_file())
        ok("reconcile: the sidecar itself is cleaned up, not left behind either",
           not sidecar.is_file())


def test_repair_ignores_worker_last_message_sidecar():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "repairsidecar"
        make_job(q.pending, job_id, q.reference)
        claimed = artpiped.claim_next(q.pending, q.active)
        sidecar = q.active / f"{job_id}.worker_last_message.json"
        sidecar.write_text(json.dumps({"id": job_id, "status": "ok"}))
        common.atomic_write_json(q.done / f"{job_id}.manifest.json",
                                 {"id": job_id, "status": "ok", "channel": "codex"})

        moved = artpiped.repair(q.active, q.done, q.failed)
        ok("repair: the real job is repaired (moved into done/)",
           any(jid == job_id for jid, _ in moved), moved)
        ok("repair: the sidecar is never treated as a phantom job needing repair",
           not (q.done / f"{job_id}.worker_last_message.json").is_file()
           and not (q.failed / f"{job_id}.worker_last_message.json").is_file())
        ok("repair: the sidecar itself is cleaned up too", not sidecar.is_file())


def test_retry_decision_reads_last_message_note_before_retrying():
    """Finding 3: the retry decision used to read ONLY stdout+stderr — a
    throttle visible ONLY in the -o last-message note (clean transcript,
    nonzero exit) would be RETRIED against an already-throttled account.
    rate_limited_note_only_nonzero_exit behaves identically on every
    invocation, so the mock's own invocation counter proves whether a
    (wasteful, wrong) retry happened."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "noteonlythrottle"
        make_job(q.pending, job_id, q.reference)
        proc = q.run({job_id: "rate_limited_note_only_nonzero_exit"}, "--once", "--workers", "1")
        ok("note-retry: daemon exits 0 (a lone hard-stopped job, nothing pending after)",
           proc.returncode == 0, proc.stdout + proc.stderr)
        manifest = q.failed / f"{job_id}.manifest.json"
        ok("note-retry: job fails", manifest.is_file())
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("note-retry: detector_row is 1 — caught via the note", m.get("detector_row") == 1,
               str(m))
            ok("note-retry: daemon_attempts is 1 — NEVER retried against a throttled account",
               m.get("daemon_attempts") == 1, str(m))
        counter = q.artsrc / job_id / f".{job_id}.invocations"
        ok("note-retry: the mock was invoked exactly once — the old bug would show 2",
           counter.is_file() and counter.read_text().strip() == "1",
           counter.read_text() if counter.is_file() else "no counter file")


def test_reconcile_min_age_derives_from_timeout_edit():
    """Finding 6: a hardcoded 600s default had only 40s of margin over the
    real worst case at the DEFAULT --timeout-edit (560s), and didn't move
    at all if --timeout-edit was raised — silently reopening the double-
    claim race reconcile() exists to close."""
    default_220 = artpiped.default_reconcile_min_age(220)
    ok("reconcile-min-age: derived default at timeout_edit=220 has real margin "
       "over the hardcoded 600s's thin 40s cushion", default_220 > 600, default_220)

    default_400 = artpiped.default_reconcile_min_age(400)
    ok("reconcile-min-age: raising --timeout-edit raises the derived default too "
       "(a hardcoded value would not move at all)", default_400 > default_220,
       (default_220, default_400))

    args = artpiped.parse_args(["--timeout-edit", "300"])
    ok("reconcile-min-age: parse_args uses the DERIVED default when not overridden",
       args.reconcile_min_age == artpiped.default_reconcile_min_age(300), args.reconcile_min_age)

    args2 = artpiped.parse_args(["--timeout-edit", "300", "--reconcile-min-age", "42"])
    ok("reconcile-min-age: an explicit --reconcile-min-age still overrides the derivation",
       args2.reconcile_min_age == 42.0, args2.reconcile_min_age)


def test_agents_md_manifest_example_uses_absolute_path_wording():
    """Finding 7 (doc-only, no code path to pin — checked textually): the
    manifest example must say "absolute path", matching
    manifest.schema.json's own "out" description, not "the filename you
    saved" (which reads as a bare cwd-relative name)."""
    text = common.AGENTS_MD.read_text()
    ok("AGENTS.md: the manifest example's 'out' field says ABSOLUTE path",
       "ABSOLUTE path" in text or "absolute path" in text.lower())
    ok("AGENTS.md: no longer claims a crashed-with-nothing-captured run is "
       "reconciled to pending/ (the real code fails it to failed/ immediately)",
       "reconciles the job back to `pending/` for it" not in text)


def test_prune_old_scratch_dirs_removes_only_old_terminally_decided_jobs():
    """Lower note: _artsrc/<id>/ scratch dirs were never cleaned up at all.
    Pruned only when BOTH terminally decided (a manifest exists) AND that
    manifest is old — never a dir with no manifest (might still be
    pending/active, or not a real job at all)."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))

        old_done_dir = q.artsrc / "olddonejob"
        old_done_dir.mkdir(parents=True)
        (old_done_dir / "olddonejob.png").write_bytes(b"x")
        manifest = q.done / "olddonejob.manifest.json"
        common.atomic_write_json(manifest, {"id": "olddonejob", "status": "ok"})
        old_time = time.time() - 20 * 86400
        os.utime(manifest, (old_time, old_time))

        fresh_dir = q.artsrc / "freshdonejob"
        fresh_dir.mkdir(parents=True)
        (fresh_dir / "freshdonejob.png").write_bytes(b"x")
        common.atomic_write_json(q.done / "freshdonejob.manifest.json",
                                 {"id": "freshdonejob", "status": "ok"})

        orphan_dir = q.artsrc / "notdonejob"
        orphan_dir.mkdir(parents=True)
        (orphan_dir / "notdonejob.png").write_bytes(b"x")

        pruned = artpiped.prune_old_scratch_dirs(q.artsrc, q.done, q.failed, max_age_days=14.0)
        ok("prune: the old, terminally-decided job's scratch dir is removed",
           "olddonejob" in pruned and not old_done_dir.is_dir())
        ok("prune: a fresh terminally-decided job's scratch dir is left alone",
           "freshdonejob" not in pruned and fresh_dir.is_dir())
        ok("prune: a scratch dir with NO manifest at all is never touched",
           "notdonejob" not in pruned and orphan_dir.is_dir())

        pruned_disabled = artpiped.prune_old_scratch_dirs(q.artsrc, q.done, q.failed,
                                                            max_age_days=0)
        ok("prune: max_age_days<=0 disables pruning entirely", pruned_disabled == [])


def test_prune_wired_into_daemon_startup():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        old_dir = q.artsrc / "staledonejob"
        old_dir.mkdir(parents=True)
        (old_dir / "staledonejob.png").write_bytes(b"x")
        manifest = q.done / "staledonejob.manifest.json"
        common.atomic_write_json(manifest, {"id": "staledonejob", "status": "ok"})
        old_time = time.time() - 20 * 86400
        os.utime(manifest, (old_time, old_time))

        proc = q.run({}, "--reconcile-only", "--prune-scratch-days", "14")
        ok("prune e2e: exits 0", proc.returncode == 0, proc.stderr)
        ok("prune e2e: the stale scratch dir is gone", not old_dir.is_dir())
        ok("prune e2e: reported in the output", "pruned old scratch dir for staledonejob"
           in proc.stdout, proc.stdout)


def test_gemini_cost_billed_only_on_genuine_success_not_exit_0_alone():
    """Lower note: cost used to be computed from `code == 0` alone, before
    ever checking an image actually existed — an exit-0-no-image no-op was
    billed even though nothing was generated."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "geminiexit0noimage"
        make_job(q.pending, job_id, q.reference, channel="gemini")
        proc = q.run({job_id: "ok_no_image"}, "--once", "--workers", "1")
        ok("no-image-billing: daemon exits 0", proc.returncode == 0, proc.stderr)
        manifest = q.failed / f"{job_id}.manifest.json"
        ok("no-image-billing: job fails (exit 0 but no image)", manifest.is_file())
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("no-image-billing: cost_usd is 0.0 — never billed for a no-op",
               m.get("cost_usd") == 0.0, str(m))
        lines = [json.loads(l) for l in q.throughput_log.read_text().splitlines() if l.strip()]
        # lines[0] is now the pre-flight intent row (finding 2) — the
        # completion row (with the real cost_usd this test cares about) is
        # whichever row is NOT tagged record="intent".
        completion = [l for l in lines if l.get("record") != "intent"]
        ok("no-image-billing: throughput.jsonl agrees — 0.0, not the per-image price",
           completion and completion[0].get("cost_usd") == 0.0, lines)


def test_gemini_budget_reservation_prevents_concurrent_overshoot():
    """Lower note: admission was checked ONLY at claim time against
    spent_usd alone — with N workers, up to N gemini jobs could all be
    claimed in the SAME instant (none has reported cost back yet),
    collectively overshooting the cap by up to (N-1) jobs' worth.
    Reserving the conservative estimate AT claim time closes this: with 3
    gemini jobs queued, --workers 3, and a budget that fits exactly ONE
    image, only ONE should ever be claimed, not up to 3."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        for i in range(3):
            make_job(q.pending, f"reserve{i}", q.reference, priority=i, channel="gemini")
        control = {f"reserve{i}": "ok" for i in range(3)}
        proc = q.run(control, "--once", "--workers", "3", "--gemini-budget-usd", "0.134")
        ok("reservation: daemon exits nonzero — 2 of 3 jobs are still pending",
           proc.returncode != 0, proc.stdout + proc.stderr)
        done_ids = {p.stem for p in q.done.glob("reserve*.json") if not p.name.endswith(".manifest.json")}
        ok("reservation: exactly ONE of the three gemini jobs ran, not up to 3",
           len(done_ids) == 1, done_ids)
        ok("reservation: the other two were never even claimed — still pending",
           len(list(q.pending.glob("reserve*.json"))) == 2)
        ok("reservation: nothing left dangling in active/", not any(q.active.glob("*.json")))


def test_finalize_job_writes_throughput_before_manifest():
    """Lower note: a crash between writing the manifest and appending to
    throughput.jsonl used to lose the cost row forever (read_gemini_spend()
    only ever sums that file, never scans manifests). Mechanically pins
    the reordering fix by spying on both common functions and recording
    call order — append_jsonl (throughput) must run before
    atomic_write_json (the manifest)."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "orderingcheck"
        make_job(q.pending, job_id, q.reference, channel="gemini")
        claimed = artpiped.claim_next(q.pending, q.active)
        result = {"id": job_id, "channel": "gemini", "status": "ok",
                 "worker_status": "ok", "validator": "PASS", "cost_usd": 0.134,
                 "elapsed_s": 1.0, "model": "gemini-3-pro-image", "daemon_attempts": 1}

        call_order = []
        orig_append = common.append_jsonl
        orig_write = common.atomic_write_json

        def spy_append(*a, **k):
            call_order.append("throughput")
            return orig_append(*a, **k)

        def spy_write(*a, **k):
            call_order.append("manifest")
            return orig_write(*a, **k)

        artpiped.common.append_jsonl = spy_append
        artpiped.common.atomic_write_json = spy_write
        try:
            detector = artpiped.Detector()
            budget = artpiped.GeminiBudget(1000.0, q.throughput_log)
            artpiped.finalize_job(claimed, result, q.done, q.failed, q.active,
                                  q.throughput_log, detector, budget, 1)
        finally:
            artpiped.common.append_jsonl = orig_append
            artpiped.common.atomic_write_json = orig_write

        ok("ordering: throughput.jsonl is written BEFORE the manifest",
           call_order == ["throughput", "manifest"], call_order)
        lines = [json.loads(l) for l in q.throughput_log.read_text().splitlines() if l.strip()]
        ok("ordering: the throughput row itself carries the right channel/cost",
           lines and lines[0].get("channel") == "gemini" and lines[0].get("cost_usd") == 0.134,
           lines)


# --------------------------------------------------------------------------
# fourth review (de58a58f -> this pass): 4 confirmed findings + 2 lower notes
# --------------------------------------------------------------------------

def test_malformed_gemini_job_preserves_channel_and_releases_reservation():
    """Finding 1: a malformed GEMINI job used to hardcode channel="codex"
    in the JobError fallback, so finalize_job's gemini branch (which
    releases the claim-time reservation) never ran for it — the
    reservation leaked forever, and enough malformed gemini jobs would
    eventually block the whole channel at $0 real spend."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "malformedgemini"
        # channel=gemini but missing canvas/prompt/rimflow_item_id —
        # common.load_job raises JobError before ever seeing job.get("channel").
        common.atomic_write_json(q.pending / f"{job_id}.json",
                                 {"id": job_id, "channel": "gemini"})
        proc = q.run({}, "--once", "--workers", "1", "--gemini-budget-usd", "0.134")
        ok("malformed-gemini: daemon exits 0", proc.returncode == 0, proc.stderr)
        manifest = q.failed / f"{job_id}.manifest.json"
        ok("malformed-gemini: job fails", manifest.is_file())
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("malformed-gemini: channel is gemini, NOT hardcoded codex",
               m.get("channel") == "gemini", str(m))

        # If the reservation had leaked, a SECOND, perfectly healthy
        # gemini job would be refused even though nothing was ever really
        # spent (reserved_usd alone reaching the cap).
        make_job(q.pending, "healthygemini", q.reference, channel="gemini")
        proc2 = q.run({"healthygemini": "ok"}, "--once", "--workers", "1",
                      "--gemini-budget-usd", "0.134")
        ok("malformed-gemini: a second, healthy gemini job is NOT blocked by "
           "a leaked reservation from the malformed one", proc2.returncode == 0,
           proc2.stdout + proc2.stderr)
        ok("malformed-gemini: the healthy job actually ran",
           (q.done / "healthygemini.json").is_file())


def test_gemini_budget_spend_is_read_live_not_cached_at_construction():
    """Finding 2 core mechanism: N daemons each used to read spend ONCE at
    construction and cache it — so N daemons would each independently
    believe there was room for a full cap's worth. Two GeminiBudget
    objects sharing one throughput_log, neither ever told directly about
    the other's spend, must each see it live on their next check."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        throughput_log = tdp / "throughput.jsonl"
        budget_a = artpiped.GeminiBudget(0.134, throughput_log, spent_so_far=0.0)
        budget_b = artpiped.GeminiBudget(0.134, throughput_log, spent_so_far=0.0)
        ok("live-spend: both budgets start unblocked",
           not budget_a.admission_blocked() and not budget_b.admission_blocked())

        # Simulate a DIFFERENT process's job finishing for real.
        common.append_jsonl(throughput_log, {"id": "x", "channel": "gemini", "cost_usd": 0.134})

        ok("live-spend: budget_b sees the spend WITHOUT ever being told directly",
           budget_b.admission_blocked())
        ok("live-spend: budget_a also sees it on its own next check",
           budget_a.admission_blocked())


def test_gemini_budget_live_reread_sees_concurrent_external_spend_end_to_end():
    """Finding 2, end to end: while a SINGLE real daemon process is
    running (not just at its own startup), an EXTERNAL throughput row —
    simulating a DIFFERENT daemon's concurrent spend — lands on disk
    between this daemon's first and second claim attempts. The second
    must see it live, without this process's own gemini_budget ever
    being told about it directly."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        # job2 is deliberately NOT filed yet — with only job1 pending, a
        # fast mock could claim+finish it and go straight to idle-polling
        # well before this test's own poll loop even notices job1 is done,
        # racing the injection below for no reason. Filing job2 only AFTER
        # the injection removes that race entirely while still exercising
        # the real mechanism: the daemon's own poll loop discovering
        # newly-available work under an already-tightened budget.
        make_job(q.pending, "livereread1", q.reference, priority=1, channel="gemini")
        control_path = q.root / "control.json"
        control_path.write_text(json.dumps({"livereread1": "ok", "livereread2": "ok"}))
        env = dict(os.environ)
        env["ARTPIPE_MOCK_CONTROL"] = str(control_path)

        proc = subprocess.Popen(
            q.daemon_args("--workers", "1", "--poll-interval", "0.1",
                         "--gemini-budget-usd", "0.268"),  # exactly 2 images' worth
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        try:
            deadline = time.time() + 15
            while time.time() < deadline and not (q.done / "livereread1.json").is_file():
                time.sleep(0.05)
            ok("live-reread e2e: job1 completed", (q.done / "livereread1.json").is_file())

            # The "other daemon's" spend, landing WHILE this process keeps
            # running — exhausts the remaining half of the cap BEFORE job2
            # ever exists for this daemon to find.
            common.append_jsonl(q.throughput_log, {"id": "external-other-daemon",
                                                    "channel": "gemini", "cost_usd": 0.134})
            make_job(q.pending, "livereread2", q.reference, priority=2, channel="gemini")
            time.sleep(1.0)  # several poll cycles for the running daemon to react

            ok("live-reread e2e: job2 was NEVER claimed after the external "
               "spend landed — still pending", (q.pending / "livereread2.json").is_file())
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


def test_recovered_throttle_note_never_fails_a_successful_job():
    """Finding 3: _looks_rate_limited ran UNCONDITIONALLY on the -o note
    after the retry loop — a worker that recovered from an INTERNAL
    throttle (its own note honestly narrates "first attempt returned
    TooManyRequests; retried once and succeeded", exit 0, good image) got
    filed FAILED and latched the account hard-stop, punishing a success."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "recoveredjob"
        make_job(q.pending, job_id, q.reference)
        proc = q.run({job_id: "recovered_from_throttle"}, "--once", "--workers", "1")
        ok("recovered: daemon exits 0", proc.returncode == 0, proc.stdout + proc.stderr)
        ok("recovered: the job SUCCEEDS despite the note mentioning TooManyRequests",
           (q.done / f"{job_id}.json").is_file())
        manifest = q.done / f"{job_id}.manifest.json"
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("recovered: status is ok", m.get("status") == "ok", str(m))
            ok("recovered: detector_row is NOT 1 — no hard-stop for a success",
               m.get("detector_row") != 1, str(m))
        ok("recovered: hard_stop is NOT latched", "hard_stop=False" in proc.stdout, proc.stdout)


def test_detector_unwedges_via_direct_meter_reread_without_a_new_job():
    """Finding 4 core mechanism: note_meters()'s only OTHER caller is
    finalize_job of a COMPLETING codex job, but admission_blocked() then
    refuses to let any NEW codex job be claimed while wedged — a catch-22
    that used to last until restart. Re-reading meters DIRECTLY
    (codex_grumpiness.read_meters needs no job) and feeding note_meters
    must de-escalate exactly the way a job-triggered reading would."""
    with tempfile.TemporaryDirectory() as td:
        home = Path(td) / "codex_home"
        d = artpiped.Detector()
        d.note_meters({"ok": True, "secondary_used_percent": 98.0, "primary_used_percent": 5.0})
        ok("unwedge: stop_all is set", d.stop_all and d.admission_blocked())

        day_dir = home / "sessions" / "2026" / "01" / "01"
        day_dir.mkdir(parents=True)
        (day_dir / "rollout-1-fresh.jsonl").write_text(json.dumps({
            "payload": {"type": "token_count", "info": {},
                        "rate_limits": {"primary": {"used_percent": 1.0},
                                        "secondary": {"used_percent": 1.0}}},
        }) + "\n")
        fresh = codex_grumpiness.read_meters(home)
        d.note_meters(fresh)
        ok("unwedge: a direct re-read (no job involved at all) clears stop_all",
           not d.stop_all and not d.admission_blocked())


def test_daemon_unwedges_codex_channel_without_restart_end_to_end():
    """Finding 4, end to end: a persistent (non---once) daemon wedges
    stop_all via job1, with job2 still pending. It must claim and finish
    job2 WITHOUT a restart once a fresh, healthy meter reading appears in
    the ALREADY-LEASED codex_home — proving main()'s own periodic refresh
    is actually wired up, not just the Detector method in isolation."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "wedgejob1", q.reference, priority=1)
        make_job(q.pending, "wedgejob2", q.reference, priority=2)
        control_path = q.root / "control.json"
        control_path.write_text(json.dumps({
            "wedgejob1": {"behavior": "ok", "weekly": 98.0},
            "wedgejob2": "ok",
        }))
        env = dict(os.environ)
        env["ARTPIPE_MOCK_CONTROL"] = str(control_path)

        proc = subprocess.Popen(
            q.daemon_args("--workers", "1", "--poll-interval", "0.1",
                         "--meter-refresh-interval", "0.1"),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        try:
            deadline = time.time() + 15
            while time.time() < deadline and not (q.done / "wedgejob1.json").is_file():
                time.sleep(0.05)
            ok("unwedge e2e: job1 completed (and wedged stop_all)",
               (q.done / "wedgejob1.json").is_file())

            time.sleep(0.3)
            ok("unwedge e2e: job2 is genuinely blocked right after the wedge",
               (q.pending / "wedgejob2.json").is_file())

            # --workers 1 means the first (only) lease is always w0 —
            # deterministic, since this fresh codex_homes root has no
            # contention.
            fresh_home = q.codex_homes / "w0"
            mock_codex_worker.write_rollout(fresh_home, weekly=1.0, five_h=1.0)

            deadline2 = time.time() + 15
            while time.time() < deadline2 and not (q.done / "wedgejob2.json").is_file():
                time.sleep(0.05)
            ok("unwedge e2e: job2 is claimed and finished WITHOUT a restart, "
               "once a fresh healthy reading appeared",
               (q.done / "wedgejob2.json").is_file())
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


def test_reconcile_never_requeues_gemini_orphan_with_existing_throughput_row():
    """Lower note: a crash between the throughput append and the manifest
    write used to let reconcile() silently requeue the orphan for a full
    fresh retry — for a GEMINI job that already spent real money before
    crashing, the retry could spend it again with no human ever told.
    Fixed: such an orphan is routed to failed/ with an
    ambiguous_billing_crash manifest, never auto-requeued."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "crashedgeminibilling"
        make_job(q.pending, job_id, q.reference, channel="gemini")
        claimed = artpiped.claim_next(q.pending, q.active)
        ok("fixture: claimed via the real claim path", claimed is not None)
        # Simulate the crash: throughput row exists (written FIRST, per
        # finalize_job's own ordering), but no manifest anywhere and the
        # job file is still sitting in active/ — exactly what a kill
        # between those two steps leaves behind.
        common.append_jsonl(q.throughput_log, {"id": job_id, "channel": "gemini",
                                                "cost_usd": 0.134, "status": "ok"})
        old = time.time() - 1200
        os.utime(claimed, (old, old))

        moved = artpiped.reconcile(q.active, q.pending, q.done, q.failed,
                                  q.throughput_log, min_age_s=600.0)
        ok("no-rebill: the job is NEVER requeued to pending",
           not (q.pending / f"{job_id}.json").is_file())
        ok("no-rebill: routed to failed/ instead", (q.failed / f"{job_id}.json").is_file())
        manifest = q.failed / f"{job_id}.manifest.json"
        ok("no-rebill: manifest exists", manifest.is_file())
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("no-rebill: worker_status is ambiguous_billing_crash",
               m.get("worker_status") == "ambiguous_billing_crash", str(m))
        ok("no-rebill: reported in the moved list", any(jid == job_id for jid, _ in moved), moved)


def test_reconcile_still_requeues_codex_orphan_regardless_of_throughput_row():
    """Companion: a CODEX orphan (never billed, regardless) is unaffected
    by this check — still requeued to pending/ normally, even in the
    implausible case a throughput row already exists for it."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "crashedcodexnobilling"
        make_job(q.pending, job_id, q.reference, channel="codex")
        claimed = artpiped.claim_next(q.pending, q.active)
        common.append_jsonl(q.throughput_log, {"id": job_id, "channel": "codex", "status": "ok"})
        old = time.time() - 1200
        os.utime(claimed, (old, old))

        moved = artpiped.reconcile(q.active, q.pending, q.done, q.failed,
                                  q.throughput_log, min_age_s=600.0)
        ok("codex-unaffected: still requeued to pending normally",
           (q.pending / f"{job_id}.json").is_file())
        ok("codex-unaffected: NOT routed to failed/", not (q.failed / f"{job_id}.json").is_file())


def test_wall_clock_baseline_is_per_mode_not_pooled():
    """Lower note: 62.0s is the GENERATE median while edit timings (a
    220s default timeout) are a different population entirely — pooling
    them into one statistic would trip row 4 constantly for an edit-heavy
    workload under perfectly ordinary conditions. The SAME wall-clock
    value must be judged differently depending on which mode it came
    from."""
    edit_typical = 140.0  # under edit's OWN 2x-baseline (300s), over generate's (124s)

    d = artpiped.Detector()
    for _ in range(3):
        d.note_wall_clock(edit_typical, configured_n=4, mode="edit")
    ok("per-mode: edit-typical wall clocks do NOT halve N under edit's own baseline",
       d.current_n(4) == 4)

    d2 = artpiped.Detector()
    for _ in range(3):
        d2.note_wall_clock(edit_typical, configured_n=4, mode="generate")
    ok("per-mode: the SAME value DOES halve N when (deliberately, for this test) "
       "evaluated against generate's baseline — proving the two are genuinely "
       "separate histories, not a shared one", d2.current_n(4) == 2)


def test_finalize_job_feeds_per_attempt_not_summed_wall_clock():
    """Lower note: elapsed_s is the RETRY-SUMMED total (useful for
    reporting how long the whole job took, retries included);
    attempt_elapsed_s is the LAST attempt's own elapsed — what row 4
    should see. A job that used its one retry (e.g. 40s + 40s = 80s
    summed) must not look like an 80s single request to the detector."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "attemptcheck"
        make_job(q.pending, job_id, q.reference, channel="codex")
        claimed = artpiped.claim_next(q.pending, q.active)
        result = {"id": job_id, "channel": "codex", "status": "ok",
                 "worker_status": "ok", "validator": "PASS",
                 "elapsed_s": 80.0, "attempt_elapsed_s": 40.0, "mode": "generate",
                 "meter_before": None, "meter_after": None, "daemon_attempts": 2}
        detector = artpiped.Detector()
        budget = artpiped.GeminiBudget(1000.0, q.throughput_log)
        artpiped.finalize_job(claimed, result, q.done, q.failed, q.active,
                              q.throughput_log, detector, budget, 4)
        ok("per-attempt: the detector's generate history recorded 40.0 (the "
           "per-attempt value), not 80.0 (the retry-summed total)",
           detector.wall_clock_history.get("generate") == [40.0],
           detector.wall_clock_history)


def gemini_run_ctx(q: "Queue") -> artpiped.RunCtx:
    """A minimal RunCtx for calling process_gemini_job() directly, in
    process, without going through a whole daemon subprocess — the gemini
    path never touches ctx.slots/codex_home_root at all, so a placeholder
    empty Queue is enough."""
    return artpiped.RunCtx(
        worker_script=MOCK_WORKER, validator_script=VALIDATOR,
        manifest_schema=SCHEMA, artsrc_dir=q.artsrc, active_dir=q.active,
        codex_home_root=q.codex_homes, workers_count=1,
        timeout_generate=60, timeout_edit=60, reasoning_effort="low",
        verbose=False, slots=queue.Queue(), gemini_worker_script=MOCK_GEMINI_WORKER,
        gemini_timeout=60, throughput_log=q.throughput_log)


def set_mock_control(root: Path, control: dict) -> None:
    """For tests that call process_gemini_job()/run_gemini_worker() directly
    (in-process), rather than through Queue.run()'s own subprocess — the
    mock worker is still a CHILD subprocess either way, and it reads
    $ARTPIPE_MOCK_CONTROL from whatever environment it inherits."""
    control_path = root / "control.json"
    control_path.write_text(json.dumps(control))
    os.environ["ARTPIPE_MOCK_CONTROL"] = str(control_path)


# --------------------------------------------------------------------------
# Round 5 (fifth review, 7e874fdd): budget/billing edge cases. Every
# existing gemini-budget test above uses a cap that is an EXACT MULTIPLE of
# GEMINI_RESERVE_ESTIMATE_USD (0.134) — 0.134, 1000.0, etc — so the "cap
# minus what's already committed" remainder is always either the full
# per-image cost or exactly zero. The fractional-cap tests below use caps
# that are NOT multiples, so a nonzero-but-insufficient remainder actually
# occurs — the exact window finding 1 was about.
# --------------------------------------------------------------------------

def test_gemini_budget_admission_and_reserve_share_predicate_with_fractional_cap():
    """Finding 1's precise bug: admission_blocked() and reserve() used to
    apply DIFFERENT thresholds (admission ignored the estimate entirely;
    reserve() didn't). A cap that is an exact multiple of the per-image
    cost can never show this — spent+reserved always lands EXACTLY on a
    boundary, never in the fractional gap between "some room" and "not
    quite enough room for one more". cap=0.2 sits between 1x (0.134) and
    2x (0.268) the per-image cost, so after one reservation the remainder
    (0.066) is real, nonzero, and still short of a second image."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        throughput_log = tdp / "throughput.jsonl"
        cap = 0.2  # deliberately NOT a multiple of 0.134
        est = artpiped.GEMINI_RESERVE_ESTIMATE_USD
        budget = artpiped.GeminiBudget(cap, throughput_log, spent_so_far=0.0)

        ok("fractional-cap: starts unblocked with nothing spent or reserved",
           not budget.admission_blocked())
        ok("fractional-cap: first reservation succeeds", budget.reserve(est))

        # Now spent=0, reserved=est=0.134, cap=0.2. A SECOND reservation
        # attempt must be refused by BOTH admission_blocked() and reserve()
        # — the old bug's whole failure mode was these two disagreeing.
        ok("fractional-cap: admission_blocked() now says no room for a second image",
           budget.admission_blocked())
        ok("fractional-cap: reserve() independently agrees — refuses the second slot",
           not budget.reserve(est))

        # The first job actually completes for its real, billed cost — a
        # REAL throughput row, since spend is always re-read live from
        # throughput_log (cross-process consistency), never trusted from
        # in-memory bookkeeping alone; see GeminiBudget._refresh_spent.
        common.append_jsonl(throughput_log, {"id": "j1", "channel": "gemini", "cost_usd": est})
        budget.release_reservation(est, est)
        remainder = cap - budget.spent_usd
        ok("fractional-cap: a real, nonzero remainder exists after the first job",
           0 < remainder < est, remainder)
        ok("fractional-cap: that remainder is still too small to admit another image "
           "— the window the review named actually opens, and admission still refuses",
           budget.admission_blocked())
        ok("fractional-cap: reserve() agrees post-release too",
           not budget.reserve(est))


def test_gemini_budget_never_overshoots_cap_with_concurrent_gemini_workers_end_to_end():
    """Finding 1, end to end against the real mock/daemon machinery: two
    gemini jobs, --workers 2, and a fractional cap (0.2) sized for exactly
    one image with a nonzero leftover. Before the reserve-or-return fix, a
    same-tick second claim could slip through on admission_blocked()
    alone and only get caught (too late) by reserve() — this proves the
    daemon now keeps the SECOND job in pending/ rather than ever billing
    past the cap."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "fraccap1", q.reference, priority=1, channel="gemini")
        make_job(q.pending, "fraccap2", q.reference, priority=2, channel="gemini")
        proc = q.run({"fraccap1": "ok", "fraccap2": "ok"},
                      "--once", "--workers", "2", "--gemini-budget-usd", "0.2")
        ok("no-overshoot: fraccap1 (fits the cap) completes",
           (q.done / "fraccap1.json").is_file(), proc.stdout + proc.stderr)
        ok("no-overshoot: fraccap2 is left in pending — never claimed, never billed",
           (q.pending / "fraccap2.json").is_file())
        spent, skipped = artpiped.read_gemini_spend(q.throughput_log)
        ok("no-overshoot: total recorded spend never exceeds the cap",
           spent <= 0.2 + 1e-9, spent)
        ok("no-overshoot: no unparseable throughput lines from this run", skipped == 0, skipped)


def test_gemini_intent_row_written_before_worker_runs_and_excluded_from_spend():
    """Finding 2's core mechanism: process_gemini_job() must journal a
    billing-INTENT row for this job id BEFORE the worker subprocess (the
    thing that actually spends real money) even runs — that's the ONLY
    record that survives a crash mid-API-call. Calling process_gemini_job()
    directly (never finalize_job(), which writes the separate completion
    row) isolates that this row exists purely from the pre-flight write,
    and that read_gemini_spend() must never count it as spend on its own."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "intentcheck"
        job = job_dict(job_id, q.reference, channel="gemini")
        set_mock_control(Path(td), {job_id: "ok"})
        ctx = gemini_run_ctx(q)
        out_png = q.artsrc / job_id / f"{job_id}.png"
        result = artpiped.process_gemini_job(job, job_id, q.reference, out_png, ctx)
        ok("intent: process_gemini_job itself still reports success",
           result.get("status") == "ok", result)

        lines = [json.loads(l) for l in q.throughput_log.read_text().splitlines() if l.strip()]
        ok("intent: exactly one throughput row exists (the intent — finalize_job "
           "never ran, so no completion row exists yet)", len(lines) == 1, lines)
        ok("intent: it is tagged record=intent for this exact job id",
           lines and lines[0].get("record") == "intent" and lines[0].get("id") == job_id,
           lines)
        spent, skipped = artpiped.read_gemini_spend(q.throughput_log)
        ok("intent: an intent-only row must NOT count as spend on its own "
           "(it carries no confirmed cost — see read_gemini_spend's docstring)",
           spent == 0.0 and skipped == 0, (spent, skipped))


def test_reconcile_catches_crash_during_gemini_api_call_via_intent_row():
    """Finding 2, end to end: the crash window this closes is DURING the
    API call itself — before finalize_job ever gets a chance to write
    anything. Simulated here by writing ONLY the intent row (as
    process_gemini_job does right before spawning the worker) and then
    killing the job with no completion row at all, exactly as a real kill
    -9 mid-call would leave things. reconcile() must treat this exactly
    like the already-covered post-completion crash: routed to failed/ as
    ambiguous_billing_crash, never silently requeued to retry (and
    potentially double-spend)."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        job_id = "midcallcrash"
        make_job(q.pending, job_id, q.reference, channel="gemini")
        claimed = artpiped.claim_next(q.pending, q.active)
        ok("mid-call-crash: fixture claimed the job via the real claim path",
           claimed is not None)

        # The ONLY thing a real mid-call crash would have produced: the
        # pre-flight intent row, written before the worker subprocess ever
        # ran — no completion row, no manifest, nothing else.
        artpiped._write_gemini_billing_intent(q.throughput_log, job_id)

        old = time.time() - 900
        os.utime(claimed, (old, old))

        moved = artpiped.reconcile(q.active, q.pending, q.done, q.failed,
                                    q.throughput_log, min_age_s=600.0)
        ok("mid-call-crash: never silently requeued to pending/",
           not (q.pending / f"{job_id}.json").is_file())
        ok("mid-call-crash: routed to failed/ instead",
           (q.failed / f"{job_id}.json").is_file())
        manifest_path = q.failed / f"{job_id}.manifest.json"
        if manifest_path.is_file():
            m = json.loads(manifest_path.read_text())
            ok("mid-call-crash: manifest flags it ambiguous_billing_crash",
               m.get("worker_status") == "ambiguous_billing_crash", m)


def test_default_reconcile_min_age_accounts_for_gemini_timeout_too():
    """Finding 3: min_age used to derive from --timeout-edit alone. A long
    --gemini-timeout with a short --timeout-edit used to compute a min_age
    far too small to protect a genuinely still-running gemini call from
    being falsely reconciled as an orphan mid-flight."""
    codex_only = artpiped.default_reconcile_min_age(60)
    with_long_gemini = artpiped.default_reconcile_min_age(60, gemini_timeout=2000)
    ok("reconcile-min-age: a long --gemini-timeout raises the computed min_age "
       "well past what --timeout-edit alone would give",
       with_long_gemini > codex_only * 2, (codex_only, with_long_gemini))
    ok("reconcile-min-age: a short gemini_timeout leaves the codex-driven "
       "worst case in charge (max(), not gemini overriding unconditionally)",
       artpiped.default_reconcile_min_age(600, gemini_timeout=10) >= codex_only,
       artpiped.default_reconcile_min_age(600, gemini_timeout=10))


def test_dry_run_never_creates_queue_directories():
    """Finding 4: --dry-run promises to touch nothing. Before the fix,
    main() called ensure_queue_dirs() (mkdir's pending/active/done/failed/
    _artsrc) BEFORE checking args.dry_run at all — so even a pure
    --dry-run against a brand-new tree silently created every queue
    directory. This only proves anything if the directories provably do
    NOT exist beforehand — never use the Queue fixture here, it creates
    them itself."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        pending, active, done, failed, artsrc = (
            tdp / "pending", tdp / "active", tdp / "done", tdp / "failed", tdp / "_artsrc")
        ok("dry-run fixture: none of the queue dirs exist yet",
           not any(p.exists() for p in (pending, active, done, failed, artsrc)))

        proc = subprocess.run(
            [sys.executable, str(HERE / "artpiped.py"),
             "--pending-dir", str(pending), "--active-dir", str(active),
             "--done-dir", str(done), "--failed-dir", str(failed),
             "--artsrc-dir", str(artsrc), "--codex-home-root", str(tdp / "_codex_homes"),
             "--throughput-log", str(tdp / "throughput.jsonl"),
             "--worker-script", str(MOCK_WORKER),
             "--gemini-worker-script", str(MOCK_GEMINI_WORKER),
             "--validator-script", str(VALIDATOR), "--manifest-schema", str(SCHEMA),
             "--dry-run"],
            capture_output=True, text=True, timeout=30)
        ok("dry-run: exits 0 with nothing pending", proc.returncode == 0, proc.stderr)
        ok("dry-run: STILL creates none of the queue directories",
           not any(p.exists() for p in (pending, active, done, failed, artsrc)),
           [str(p) for p in (pending, active, done, failed, artsrc) if p.exists()])


def test_read_gemini_spend_counts_skipped_unparseable_lines():
    """Finding 5, first half: a torn/unparseable throughput.jsonl line
    used to be silently invisible to read_gemini_spend() — total spend
    read back as though the line never existed at all, with no signal
    that the ledger itself might be incomplete."""
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "throughput.jsonl"
        log.write_text(
            json.dumps({"id": "a", "channel": "gemini", "cost_usd": 0.134}) + "\n"
            + "{not valid json at all\n"
            + "\n"  # blank lines are NOT torn lines — must not be counted
            + json.dumps({"id": "b", "channel": "gemini", "cost_usd": 0.134}) + "\n"
        )
        spent, skipped = artpiped.read_gemini_spend(log)
        ok("skip-count: valid rows still sum correctly", abs(spent - 0.268) < 1e-9, spent)
        ok("skip-count: exactly the one torn line is counted, blank lines are not",
           skipped == 1, skipped)


def test_gemini_budget_ledger_strict_refuses_admission_on_torn_line():
    """Finding 5, second half: a torn line makes the ledger's TRUE spend
    unknown, never provably lower than what's readable — so under
    --gemini-ledger-strict (the default), any unparseable line must
    refuse gemini admission outright until a human looks, regardless of
    how much headroom the readable rows alone suggest. --no-gemini-
    ledger-strict is the documented opt-out back to the old, permissive
    behaviour."""
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "throughput.jsonl"
        log.write_text("{not valid json\n")

        strict = artpiped.GeminiBudget(1000.0, log, ledger_strict=True)
        ok("ledger-strict: refuses admission on a torn line even with a huge cap "
           "and zero readable spend", strict.admission_blocked())

        lenient = artpiped.GeminiBudget(1000.0, log, ledger_strict=False)
        ok("ledger-lenient: --no-gemini-ledger-strict allows admission through "
           "the same torn line (documented opt-out)", not lenient.admission_blocked())


def test_read_gemini_spend_locked_caches_by_size_and_mtime():
    """Finding 5, third half: re-reading and re-summing the WHOLE
    throughput.jsonl on every single poll tick doesn't scale. Given a
    cache dict, read_gemini_spend_locked() must skip the actual re-read
    entirely when the file's (size, mtime) hasn't changed since the last
    call, and must re-read when it has."""
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "throughput.jsonl"
        common.append_jsonl(log, {"id": "a", "channel": "gemini", "cost_usd": 0.134})

        calls = []
        orig = artpiped.read_gemini_spend

        def spy(path):
            calls.append(1)
            return orig(path)

        artpiped.read_gemini_spend = spy
        try:
            cache: dict = {}
            r1 = artpiped.read_gemini_spend_locked(log, cache)
            r2 = artpiped.read_gemini_spend_locked(log, cache)
            ok("cache: unchanged file does NOT trigger a second real read",
               len(calls) == 1, calls)
            ok("cache: both calls return the same, correct value", r1 == r2 == (0.134, 0))

            common.append_jsonl(log, {"id": "b", "channel": "gemini", "cost_usd": 0.134})
            r3 = artpiped.read_gemini_spend_locked(log, cache)
            ok("cache: a real change (new size/mtime) DOES trigger a fresh read",
               len(calls) == 2, calls)
            ok("cache: the fresh read reflects the new total", abs(r3[0] - 0.268) < 1e-9, r3)
        finally:
            artpiped.read_gemini_spend = orig


def test_looks_gemini_quota_error_detects_429_but_not_generic_error():
    """Finding 6's classifier, in isolation: must recognize the markers a
    real quota/429 exhaustion is expected to use, and must NOT
    mis-classify an ordinary, unrelated worker failure as one (a false
    positive there just costs one needless backoff sleep; a false
    negative burns real budget hammering a provider that already said
    no — but over-eager matching would make EVERY failure look like a
    quota error, which is just as useless)."""
    ok("quota-detect: recognizes a 429/RESOURCE_EXHAUSTED message",
       artpiped._looks_gemini_quota_error("API error 429 RESOURCE_EXHAUSTED: rate limit exceeded"))
    ok("quota-detect: recognizes bare 'quota exceeded' phrasing",
       artpiped._looks_gemini_quota_error("Quota Exceeded for this project"))
    ok("quota-detect: does not flag an unrelated worker error",
       not artpiped._looks_gemini_quota_error(
           "gemini_image.py: unexpected response shape from the API"))
    ok("quota-detect: does not flag empty/None text", not artpiped._looks_gemini_quota_error(""))


def test_process_gemini_job_marks_quota_error_worker_status_end_to_end():
    """Finding 6, end to end against the real mock subprocess: a quota/429
    failure must come back tagged worker_status="quota_error" (so
    finalize_job's gemini branch can drive GeminiBudget's backoff), while
    an ordinary worker fault must still come back as the pre-existing
    "worker_error" — the classifier must not blur the two."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))

        job_id = "quotafail"
        job = job_dict(job_id, q.reference, channel="gemini")
        set_mock_control(Path(td), {job_id: "api_error"})
        ctx = gemini_run_ctx(q)
        out_png = q.artsrc / job_id / f"{job_id}.png"
        result = artpiped.process_gemini_job(job, job_id, q.reference, out_png, ctx)
        ok("quota-error: status is failed", result.get("status") == "failed", result)
        ok("quota-error: worker_status is quota_error, not the generic worker_error",
           result.get("worker_status") == "quota_error", result)
        ok("quota-error: never billed", result.get("cost_usd") == 0.0, result)

        job_id2 = "genericfail"
        job2 = job_dict(job_id2, q.reference, channel="gemini")
        set_mock_control(Path(td), {job_id2: "generic_error"})
        out_png2 = q.artsrc / job_id2 / f"{job_id2}.png"
        result2 = artpiped.process_gemini_job(job2, job_id2, q.reference, out_png2, ctx)
        ok("generic-error: worker_status stays worker_error — not mis-classified as quota",
           result2.get("worker_status") == "worker_error", result2)


def test_gemini_budget_backs_off_after_quota_error_and_recovers():
    """Finding 6's backoff mechanics in isolation: consecutive quota
    errors must escalate the sleep (base, then doubled), and a single
    note_recovered() call must reset the streak back to the base delay —
    never leaving a transient quota bump escalating forever once the
    provider has actually recovered."""
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "throughput.jsonl"
        budget = artpiped.GeminiBudget(1000.0, log)
        ok("backoff: unblocked before any quota error", not budget.admission_blocked())

        budget.note_quota_error()
        ok("backoff: admission blocked immediately after a quota error",
           budget.admission_blocked())
        delay1 = budget.backoff_sleep_until - time.time()
        ok("backoff: first sleep is ~= GEMINI_BACKOFF_BASE_S",
           8.0 <= delay1 <= artpiped.GEMINI_BACKOFF_BASE_S + 1.0, delay1)

        budget.note_quota_error()
        delay2 = budget.backoff_sleep_until - time.time()
        ok("backoff: a second consecutive quota error roughly doubles the sleep",
           18.0 <= delay2 <= 2 * artpiped.GEMINI_BACKOFF_BASE_S + 1.0, delay2)

        budget.note_recovered()
        budget.backoff_sleep_until = 0.0  # simulate the earlier sleep having elapsed
        ok("backoff: admission unblocked again once the wait elapses and streak resets",
           not budget.admission_blocked())

        budget.note_quota_error()
        delay3 = budget.backoff_sleep_until - time.time()
        ok("backoff: after note_recovered(), the NEXT quota error restarts at the "
           "base delay rather than continuing to escalate from before",
           8.0 <= delay3 <= artpiped.GEMINI_BACKOFF_BASE_S + 1.0, delay3)


def test_gemini_quota_error_backs_off_and_blocks_next_gemini_job_end_to_end():
    """Finding 6, full end to end through the real daemon subprocess: a
    quota-erroring gemini job must trip GeminiBudget's backoff, and a
    second, otherwise-healthy gemini job queued right behind it must be
    left untouched in pending/ for the duration of that backoff — never
    claimed and hammered against a provider that just said no."""
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "quotajob1", q.reference, priority=1, channel="gemini")
        make_job(q.pending, "quotajob2", q.reference, priority=2, channel="gemini")
        proc = q.run({"quotajob1": "api_error", "quotajob2": "ok"},
                      "--once", "--workers", "1", "--gemini-budget-usd", "1000")
        ok("quota-backoff: daemon exits nonzero — real work is still pending",
           proc.returncode != 0, proc.stdout + proc.stderr)
        ok("quota-backoff: quotajob1 failed with quota_error",
           (q.failed / "quotajob1.json").is_file())
        m_path = q.failed / "quotajob1.manifest.json"
        if m_path.is_file():
            m = json.loads(m_path.read_text())
            ok("quota-backoff: manifest records worker_status quota_error",
               m.get("worker_status") == "quota_error", m)
        ok("quota-backoff: quotajob2 was never claimed — still sitting in pending/",
           (q.pending / "quotajob2.json").is_file())
        ok("quota-backoff: quotajob2 was never billed", not (q.done / "quotajob2.json").is_file())


def main() -> int:
    for fn in (
        test_crash_reconciliation,
        test_claim_next_stamps_fresh_mtime_not_filing_time,
        test_row5_no_manifest_fails_request_not_account,
        test_row1_rate_limit_hard_stop,
        test_prompt_echo_does_not_cause_false_hard_stop,
        test_stale_output_never_accepted_after_worker_failure,
        test_nonzero_exit_never_trusted_even_with_a_fresh_looking_image,
        test_validator_catches_bad_file,
        test_cannot_validate_distinguished_from_reject,
        test_fill_queue_verifies_reference_path_and_stores_absolute,
        test_fill_queue_blank_priority_cell_does_not_crash,
        test_fill_queue_write_job_never_leaves_a_corrupt_id_blocking_file,
        test_two_concurrent_daemons_claim_atomically,
        test_dry_run_never_touches_the_queue,
        test_fill_queue_refuses_duplicate_id,
        test_load_job_validates_value_shapes_not_just_key_presence,
        test_detector_meter_thresholds,
        test_meters_flow_end_to_end_through_codex_grumpiness,
        test_meter_after_never_reads_a_previous_jobs_rollout,
        test_detector_wall_clock_halving,
        test_row6_timeout_language_never_reads_as_rate_limited,
        test_rate_limit_marker_strips_prompt_echo_but_not_real_refusals,
        test_codex_home_root_default_is_outside_the_repo,
        test_codex_home_lease_bounds_growth_and_avoids_collision,
        test_reference_less_job_size_mismatch_is_caught,
        test_reference_less_job_correct_size_still_passes,
        test_worker_self_report_folded_into_manifest_and_detects_row1,
        test_detector_deescalates_after_fresh_healthy_reading,
        test_detector_resets_at_coercion_never_crashes,
        test_exit_code_zero_on_clean_drain_with_healthy_meters,
        test_per_job_scratch_directory_is_real_not_shared,
        test_codex_one_retry_rescues_transient_failure,
        test_codex_retry_never_applied_to_rate_limited,
        test_detector_wall_clock_uses_rolling_median_not_naive_last_three,
        test_repair_completes_manifest_written_but_not_moved_crash,
        test_repair_leaves_genuinely_ambiguous_state_alone,
        test_repair_standalone_flag_works_without_reconcile_only,
        test_gemini_channel_routes_and_records_cost,
        test_gemini_bad_image_is_caught_by_revalidation_and_still_billed,
        test_gemini_api_error_never_billed,
        test_gemini_wrong_size_caught_independent_of_validator,
        test_gemini_budget_hard_stop,
        test_gemini_budget_is_durable_across_restarts,
        test_gemini_never_touches_codex_homes,
        test_mixed_channel_queue_codex_wedge_does_not_block_gemini,
        test_fill_queue_channel_flag_and_per_row_override,
        test_run_validator_never_raises_on_timeout_or_bad_exit,
        test_validator_crash_reported_as_validator_error_not_bad_reference_end_to_end,
        test_gemini_validator_error_preserves_channel_and_bills_correctly,
        test_process_job_exception_safety_net_preserves_gemini_channel_and_cost,
        test_reconcile_ignores_worker_last_message_sidecar,
        test_repair_ignores_worker_last_message_sidecar,
        test_retry_decision_reads_last_message_note_before_retrying,
        test_reconcile_min_age_derives_from_timeout_edit,
        test_agents_md_manifest_example_uses_absolute_path_wording,
        test_prune_old_scratch_dirs_removes_only_old_terminally_decided_jobs,
        test_prune_wired_into_daemon_startup,
        test_gemini_cost_billed_only_on_genuine_success_not_exit_0_alone,
        test_gemini_budget_reservation_prevents_concurrent_overshoot,
        test_finalize_job_writes_throughput_before_manifest,
        test_malformed_gemini_job_preserves_channel_and_releases_reservation,
        test_gemini_budget_spend_is_read_live_not_cached_at_construction,
        test_gemini_budget_live_reread_sees_concurrent_external_spend_end_to_end,
        test_recovered_throttle_note_never_fails_a_successful_job,
        test_detector_unwedges_via_direct_meter_reread_without_a_new_job,
        test_daemon_unwedges_codex_channel_without_restart_end_to_end,
        test_reconcile_never_requeues_gemini_orphan_with_existing_throughput_row,
        test_reconcile_still_requeues_codex_orphan_regardless_of_throughput_row,
        test_wall_clock_baseline_is_per_mode_not_pooled,
        test_finalize_job_feeds_per_attempt_not_summed_wall_clock,
        test_gemini_budget_admission_and_reserve_share_predicate_with_fractional_cap,
        test_gemini_budget_never_overshoots_cap_with_concurrent_gemini_workers_end_to_end,
        test_gemini_intent_row_written_before_worker_runs_and_excluded_from_spend,
        test_reconcile_catches_crash_during_gemini_api_call_via_intent_row,
        test_default_reconcile_min_age_accounts_for_gemini_timeout_too,
        test_dry_run_never_creates_queue_directories,
        test_read_gemini_spend_counts_skipped_unparseable_lines,
        test_gemini_budget_ledger_strict_refuses_admission_on_torn_line,
        test_read_gemini_spend_locked_caches_by_size_and_mtime,
        test_looks_gemini_quota_error_detects_429_but_not_generic_error,
        test_process_gemini_job_marks_quota_error_worker_status_end_to_end,
        test_gemini_budget_backs_off_after_quota_error_and_recovers,
        test_gemini_quota_error_backs_off_and_blocks_next_gemini_job_end_to_end,
    ):
        print(f"--- {fn.__name__} ---")
        try:
            fn()
        except Exception as exc:  # a raised exception is a FAIL, not a crash of the suite
            FAILED.append(fn.__name__)
            print(f"FAIL  {fn.__name__} raised {type(exc).__name__}: {exc}")

    print()
    if FAILED:
        print(f"{len(FAILED)} FAILED: {', '.join(FAILED)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
