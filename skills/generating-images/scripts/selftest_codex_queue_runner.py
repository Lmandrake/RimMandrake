#!/usr/bin/env python3
"""Selftest for codex_queue_runner.py — zero quota, subprocess.run stubbed out."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import types
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import codex_queue_runner as Q  # noqa: E402

TOTAL = 0
FAILURES = []


def check(name, cond):
    global TOTAL
    TOTAL += 1
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILURES.append(name)


def test_submit_and_claim(root: Path) -> None:
    Q.init_queue(root)
    Q.submit_job(root, {"job_id": "a", "kind": "generate", "prompt": "x",
                        "out": str(root / "out" / "a.png"), "images": []})
    Q.submit_job(root, {"job_id": "b", "kind": "generate", "prompt": "y",
                        "out": str(root / "out" / "b.png"), "images": []})
    d = Q.dirs(root)
    check("both jobs land in pending/", len(list(d["pending"].glob("*.json"))) == 2)

    claimed = Q.claim_job(root)
    check("claim_job returns a path", claimed is not None)
    check("claimed job moved OUT of pending/", len(list(d["pending"].glob("*.json"))) == 1)
    check("claimed job moved INTO inflight/", claimed.parent == d["inflight"])

    claimed2 = Q.claim_job(root)
    check("second claim gets the OTHER job, not a repeat",
          claimed2 is not None and claimed2.name != claimed.name)
    check("claim_job on an empty pending/ returns None", Q.claim_job(root) is None)


def test_claim_without_init(root: Path) -> None:
    """claim_job must work even when init_queue() was never called - submit_job
    only creates pending/, so claim_job owns creating inflight/ itself. A
    version that let a missing inflight/ raise OSError and swallowed it as
    'another worker claimed it' returned None here instead of the job -
    caught by this test before it shipped."""
    Q.submit_job(root, {"job_id": "noinit", "kind": "generate", "prompt": "x",
                        "out": str(root / "out" / "noinit.png"), "images": []})
    claimed = Q.claim_job(root)
    check("claim_job succeeds with no prior init_queue() call", claimed is not None)


def test_submit_atomic_write(root: Path) -> None:
    """No .tmp file survives a normal submit, and content round-trips."""
    Q.submit_job(root, {"job_id": "c", "kind": "edit", "prompt": "z",
                        "out": str(root / "out" / "c.png"), "images": ["/x.png"]})
    d = Q.dirs(root)
    leftovers = list(d["pending"].glob("*.tmp.*"))
    check("no .tmp leftover after submit_job", leftovers == [])
    job = json.loads((d["pending"] / "c.json").read_text(encoding="utf-8"))
    check("submitted job content round-trips", job["prompt"] == "z" and job["images"] == ["/x.png"])


def test_run_one_job_success(root: Path, monkeypatch_subprocess) -> None:
    """A stubbed codex_image.py call that DOES produce the file: done/, no mismatch."""
    Q.submit_job(root, {"job_id": "ok1", "kind": "generate", "prompt": "a crate",
                        "out": str(root / "out" / "ok1.png"), "images": []})
    job_path = Q.claim_job(root)

    out_path = Path(root / "out" / "ok1.png")

    def fake_run(cmd, **kw):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"\x89PNG")
        # find the --output-last-message path in cmd and write a matching self-report
        i = cmd.index("--output-last-message")
        Path(cmd[i + 1]).write_text(json.dumps({"path": str(out_path), "notes": "a crate"}),
                                    encoding="utf-8")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch_subprocess(fake_run)
    # avoid touching a real CODEX_HOME's rollout directory in this stub run
    Q.codex_grumpiness.read_meters = lambda home, after_mtime=None: {"ok": False, "reason": "stub"}

    m = Q.run_one_job(job_path, 0, root, timeout=30)
    check("successful job reports file_landed", m["file_landed"] is True)
    check("successful job has codex_image_exit 0", m["codex_image_exit"] == 0)
    check("no self_report_mismatch on a matching report", "self_report_mismatch" not in m)
    d = Q.dirs(root)
    check("manifest written to done/", (d["done"] / "ok1.json").is_file())
    check("job removed from inflight/ after completion", not job_path.exists())
    written = json.loads((d["done"] / "ok1.json").read_text(encoding="utf-8"))
    check("done/ manifest preserves the original job fields", written["prompt"] == "a crate")
    check("AGENTS.md was placed in the job's output directory",
          (out_path.parent / "AGENTS.md").is_file())


def test_run_one_job_failure(root: Path, monkeypatch_subprocess) -> None:
    """codex_image.py exits nonzero and produces nothing: failed/, stderr captured."""
    Q.submit_job(root, {"job_id": "bad1", "kind": "generate", "prompt": "boom",
                        "out": str(root / "out" / "bad1.png"), "images": []})
    job_path = Q.claim_job(root)

    def fake_run(cmd, **kw):
        return types.SimpleNamespace(returncode=1, stdout="", stderr="ERROR no image produced")

    monkeypatch_subprocess(fake_run)
    Q.codex_grumpiness.read_meters = lambda home, after_mtime=None: {"ok": False, "reason": "stub"}

    m = Q.run_one_job(job_path, 1, root, timeout=30)
    check("failed job reports file_landed False", m["file_landed"] is False)
    d = Q.dirs(root)
    check("manifest written to failed/, not done/",
          (d["failed"] / "bad1.json").is_file() and not (d["done"] / "bad1.json").is_file())
    written = json.loads((d["failed"] / "bad1.json").read_text(encoding="utf-8"))
    check("stderr tail captured in the failed manifest",
          "no image produced" in written["manifest"]["stderr_tail"])


def test_self_report_mismatch_detected(root: Path, monkeypatch_subprocess) -> None:
    """The file lands, but the agent's own self-report names a DIFFERENT path."""
    Q.submit_job(root, {"job_id": "mismatch1", "kind": "generate", "prompt": "x",
                        "out": str(root / "out" / "mismatch1.png"), "images": []})
    job_path = Q.claim_job(root)
    out_path = Path(root / "out" / "mismatch1.png")

    def fake_run(cmd, **kw):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"\x89PNG")
        i = cmd.index("--output-last-message")
        Path(cmd[i + 1]).write_text(
            json.dumps({"path": "/somewhere/else/entirely.png", "notes": "wrong path"}),
            encoding="utf-8")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch_subprocess(fake_run)
    Q.codex_grumpiness.read_meters = lambda home, after_mtime=None: {"ok": False, "reason": "stub"}

    m = Q.run_one_job(job_path, 0, root, timeout=30)
    check("file_landed still True (harvest found the real file)", m["file_landed"] is True)
    check("self_report_mismatch recorded when paths disagree",
          "self_report_mismatch" in m and "/somewhere/else/entirely.png" in m["self_report_mismatch"])


def main() -> int:
    real_subprocess_run = Q.subprocess.run

    def monkeypatch_subprocess(fn):
        Q.subprocess.run = fn

    try:
        with tempfile.TemporaryDirectory() as td:
            test_submit_and_claim(Path(td))
        with tempfile.TemporaryDirectory() as td:
            test_claim_without_init(Path(td))
        with tempfile.TemporaryDirectory() as td:
            test_submit_atomic_write(Path(td))
        with tempfile.TemporaryDirectory() as td:
            test_run_one_job_success(Path(td), monkeypatch_subprocess)
        with tempfile.TemporaryDirectory() as td:
            test_run_one_job_failure(Path(td), monkeypatch_subprocess)
        with tempfile.TemporaryDirectory() as td:
            test_self_report_mismatch_detected(Path(td), monkeypatch_subprocess)
    finally:
        Q.subprocess.run = real_subprocess_run

    if FAILURES:
        print("%d/%d FAILED: %s" % (len(FAILURES), TOTAL, ", ".join(FAILURES)))
        return 1
    print("%d/%d passed" % (TOTAL, TOTAL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
