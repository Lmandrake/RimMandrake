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


def make_job(pending_dir: Path, job_id: str, reference: Path | None,
             priority: int = 100) -> Path:
    job = {
        "id": job_id, "rimflow_item_id": "SELFTEST_ARTPIPE",
        "reference": str(reference) if reference else None,
        "canvas": {"width": 64, "height": 64},
        "prompt": "a small weathered supply crate, top-down game sprite",
        "style_notes": "", "priority": priority, "background": "transparent",
        "facing": None, "facings": [],
    }
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
        # Simulate a crash: a job sitting in active/ with NO manifest anywhere
        # — exactly what a killed daemon leaves behind mid-claim.
        orphan = q.active / "orphan.json"
        common.atomic_write_json(orphan, {
            "id": "orphan", "rimflow_item_id": "SELFTEST_ARTPIPE",
            "reference": None, "canvas": {"width": 64, "height": 64},
            "prompt": "x",
        })
        # Backdate it past --reconcile-min-age: reconcile() must not treat a
        # FRESH active/ claim as a crash orphan (that would steal a live
        # daemon's in-flight job — the exact bug the concurrency test below
        # caught), so only an old claim reads as abandoned here.
        old = time.time() - 900
        os.utime(orphan, (old, old))
        proc = q.run({}, "--reconcile-only", "--reconcile-min-age", "600")
        ok("reconcile: exits 0", proc.returncode == 0, proc.stderr)
        ok("reconcile: orphan moved back to pending/", (q.pending / "orphan.json").is_file())
        ok("reconcile: orphan gone from active/", not orphan.is_file())

        # A FRESH active/ claim (just made, no manifest yet) must be left
        # alone — it is indistinguishable from another live daemon's
        # in-flight job by content alone, only by age.
        fresh = q.active / "fresh.json"
        common.atomic_write_json(fresh, {
            "id": "fresh", "rimflow_item_id": "SELFTEST_ARTPIPE",
            "reference": None, "canvas": {"width": 64, "height": 64},
            "prompt": "x",
        })
        proc2 = q.run({}, "--reconcile-only", "--reconcile-min-age", "600")
        ok("reconcile: exits 0 on the second pass", proc2.returncode == 0, proc2.stderr)
        ok("reconcile: a FRESH in-flight-looking claim is left in active/, not stolen",
           fresh.is_file() and not (q.pending / "fresh.json").is_file())


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


def test_dry_run_never_spawns_a_worker():
    with tempfile.TemporaryDirectory() as td:
        q = Queue(Path(td))
        make_job(q.pending, "dryjob", q.reference)
        # A control that would fail hard if the mock were ever actually
        # invoked - proves --dry-run really never spawns it.
        proc = q.run({"dryjob": "rate_limited"}, "--once", "--dry-run", "--workers", "1")
        ok("dry-run: daemon exits 0", proc.returncode == 0, proc.stderr)
        ok("dry-run: job lands in done/ as a synthetic dry_run pass",
           (q.done / "dryjob.json").is_file())
        ok("dry-run: no image ever written to _artsrc/", not any(q.artsrc.glob("*.png")))
        manifest = q.done / "dryjob.manifest.json"
        if manifest.is_file():
            m = json.loads(manifest.read_text())
            ok("dry-run: status is dry_run, not ok", m.get("status") == "dry_run", str(m))


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


# --------------------------------------------------------------------------
# in-process detector/helper unit checks — cheap, no subprocess needed
# --------------------------------------------------------------------------

def test_detector_meter_thresholds():
    d = artpiped.Detector()
    d.note_meters({"secondary": {"used_percent": 82.0}, "primary": {"used_percent": 10.0}})
    ok("detector: 82% weekly warns but does not block", not d.admission_blocked())
    ok("detector: warn is logged once", d.warn_logged)

    d2 = artpiped.Detector()
    d2.note_meters({"secondary": {"used_percent": 91.0}, "primary": {"used_percent": 10.0}})
    ok("detector: 91% weekly refuses new claims", d2.admission_blocked() and d2.refuse_new)

    d3 = artpiped.Detector()
    d3.note_meters({"secondary": {"used_percent": 98.0}, "primary": {"used_percent": 10.0}})
    ok("detector: 98% weekly is a full stop", d3.admission_blocked() and d3.stop_all)

    d4 = artpiped.Detector()
    d4.note_meters({"secondary": {"used_percent": 5.0}, "primary": {"used_percent": 72.0}})
    ok("detector: 72% five-hour drops concurrency to 1", d4.current_n(3) == 1)

    d5 = artpiped.Detector()
    reset_at = time.time() + 9999
    d5.note_meters({"secondary": {"used_percent": 5.0},
                     "primary": {"used_percent": 91.0, "resets_at": reset_at}})
    ok("detector: 91% five-hour sleeps until resets_at",
       d5.admission_blocked() and d5.sleep_until == reset_at)

    d6 = artpiped.Detector()
    ok("detector: missing meter data blocks nothing (ignorance != 0%)",
       not d6.admission_blocked())
    d6.note_meters(None)
    ok("detector: None rate_limits is a no-op", not d6.admission_blocked())


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


def main() -> int:
    for fn in (
        test_crash_reconciliation,
        test_row5_no_manifest_fails_request_not_account,
        test_row1_rate_limit_hard_stop,
        test_validator_catches_bad_file,
        test_two_concurrent_daemons_claim_atomically,
        test_dry_run_never_spawns_a_worker,
        test_fill_queue_refuses_duplicate_id,
        test_detector_meter_thresholds,
        test_detector_wall_clock_halving,
        test_row6_timeout_language_never_reads_as_rate_limited,
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
