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
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
import artpiped  # noqa: E402

REPO_ROOT = HERE.parents[3]
sys.path.insert(0, str(REPO_ROOT / "skills" / "generating-images" / "scripts"))
import pnglib  # noqa: E402

MOCK_WORKER = HERE / "mock_codex_worker.py"
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
             prompt: str = "a small weathered supply crate, top-down game sprite") -> dict:
    return {
        "id": job_id, "rimflow_item_id": "SELFTEST_ARTPIPE",
        "reference": str(reference) if reference else None,
        "canvas": {"width": 64, "height": 64},
        "prompt": prompt,
        "style_notes": "", "priority": priority, "background": "transparent",
        "facing": None, "facings": [],
    }


def make_job(pending_dir: Path, job_id: str, reference: Path | None,
             priority: int = 100, prompt: str | None = None) -> Path:
    job = job_dict(job_id, reference, priority,
                   prompt or "a small weathered supply crate, top-down game sprite")
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
        common.ensure_queue_dirs(self.pending, self.active, self.done,
                                  self.failed, self.artsrc)
        self.reference = tmp / "reference.png"
        make_reference(self.reference)

    def daemon_args(self, *extra: str) -> list[str]:
        return [sys.executable, str(HERE / "artpiped.py"),
                "--pending-dir", str(self.pending), "--active-dir", str(self.active),
                "--done-dir", str(self.done), "--failed-dir", str(self.failed),
                "--artsrc-dir", str(self.artsrc), "--codex-home-root", str(self.codex_homes),
                "--throughput-log", str(self.root / "throughput.jsonl"),
                "--worker-script", str(MOCK_WORKER), "--validator-script", str(VALIDATOR),
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

            moved = artpiped.reconcile(q.active, q.pending, q.done, q.failed, min_age_s=600.0)
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
        ok("row1: daemon exits 0", proc.returncode == 0, proc.stderr)
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
        stale_path = q.artsrc / f"{job_id}.png"
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

        # Finding: codex_home dirs were "w<slot>" — unique only within ONE
        # process. Two daemons sharing --codex-home-root, both filling slots
        # 0..2, would have collided on identical paths before the pid-scoped
        # fix. Real end-to-end proof (not just the pure-path check above):
        # every codex_home directory either daemon actually created must
        # carry a pid, and at least two distinct pids must appear.
        home_dirs = [p.name for p in q.codex_homes.iterdir() if p.is_dir()]
        pids_seen = {name.rsplit("-", 1)[-1] for name in home_dirs if "-" in name}
        ok("atomicity: codex_home dirs are pid-scoped across the two real daemons",
           len(pids_seen) >= 2, f"home dirs: {home_dirs}")


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
        ok("dry-run: no image ever written to _artsrc/", not any(q.artsrc.glob("*.png")))


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
