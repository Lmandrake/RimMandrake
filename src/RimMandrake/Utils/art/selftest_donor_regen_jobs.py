#!/usr/bin/env python3
"""selftest_donor_regen_jobs.py — the blind-read and stranded-job guards of art/donor_regen_jobs.py (review wave 87).

  1. recent_429s: journalctl exits 0 with no lines for a unit systemd does not know, so an empty journal is "no 429s"
     only when the unit is loaded; otherwise it raises and the caller backs off (was: 0 -> files during a 429 storm).
  2. requeue_one: a manifest that cannot be archived puts the job back in failed/ (was: job stranded under a hidden
     .requeue name, invisible to every queue reader).
  3. build: an unparseable pending/active job refuses the build before any scan (was: its def looked untargeted and
     was filed again as a duplicate job).
  4. requeue --dry-run runs the publish-time recheck, so it lists only what a real run would requeue.
  5. submit_one: a refusal is logged even when _refs/ does not exist yet (was: FileNotFoundError).
Offline: temp dirs only, every subprocess faked.
"""
from __future__ import annotations

import atexit
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_selftest_donor_regen_jobs_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import donor_regen_jobs as DJ  # noqa: E402

FAILS = []
RL = {"status": "failed", "worker_stderr_tail": "last status: 429 Too Many Requests"}


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:400]}]"))
    if not cond:
        FAILS.append(msg)


def new_art(refs=True):
    art = Path(tempfile.mkdtemp(prefix="art_"))
    for d in ("pending", "active", "failed", "done") + (("_refs",) if refs else ()):
        (art / d).mkdir()
    return art


@contextlib.contextmanager
def swap(obj, **kw):
    old = {k: getattr(obj, k) for k in kw}
    for k, v in kw.items():
        setattr(obj, k, v)
    try:
        yield
    finally:
        for k, v in old.items():
            setattr(obj, k, v)


class Gate:
    def __init__(self, eligible=True, recheck_ok=True):
        self.eligible, self.recheck_ok = eligible, recheck_ok

    def classify(self, r):
        return {"id": r["id"], "eligible": self.eligible, "verdict": "OK" if self.eligible else "REFUSED_KEPT",
                "reason": "test"}

    def recheck(self, rows):
        if self.recheck_ok:
            return list(rows), []
        return [], [{"id": r["id"], "verdict": "REFUSED_REGEN", "reason": "rendered since"} for r in rows]


def failjob(art, jid):
    (art / "failed" / f"{jid}.json").write_text(json.dumps({"id": jid, "target_def": "RM_X", "facings": []}))
    (art / "failed" / f"{jid}.manifest.json").write_text(json.dumps(RL))


def case_journal():
    def fake(load_state, journal_out):
        def run(cmd, **k):
            if cmd[0] == "systemctl":
                return subprocess.CompletedProcess(cmd, 0, load_state + "\n", "")
            return subprocess.CompletedProcess(cmd, 0, journal_out, "")
        return run
    with swap(DJ.subprocess, run=fake("not-found", "")):
        try:
            n = DJ.recent_429s()
            check(False, "1 an unknown unit's empty journal is blind, not 429-free (raises)", f"returned {n}")
        except OSError:
            check(True, "1 an unknown unit's empty journal is blind, not 429-free (raises)")
    with swap(DJ.subprocess, run=fake("loaded", "a HTTP 429\nb ok\nc 429 again\n")):
        try:
            n = DJ.recent_429s()
        except OSError as e:
            n = e
        check(n == 2, "1b a loaded unit's journal is counted", n)
    art = new_art()
    failjob(art, "dregen_RM_X_a_v1")
    with swap(DJ.subprocess, run=fake("not-found", "")):
        with contextlib.redirect_stdout(io.StringIO()):
            DJ.requeue(art, 40, 10, False, Gate())
    check(not list((art / "pending").iterdir()), "1c requeue backs off when the unit is unknown",
          [p.name for p in (art / "pending").iterdir()])


def case_manifest_rename():
    art = new_art()
    jid = "dregen_RM_X_b_v1"
    failjob(art, jid)
    park = art / "_requeued_manifests"
    park.mkdir()
    real = os.rename

    def rename(a, b):
        if str(a).endswith(".manifest.json"):
            raise PermissionError(13, "denied", str(a))
        return real(a, b)
    err = None
    with swap(DJ.os, rename=rename):
        try:
            r = DJ.requeue_one(art, jid, park)
        except OSError as e:
            r, err = None, e
    hidden = [p.name for p in (art / "failed").iterdir() if p.name.startswith(".")]
    check(err is None and (art / "failed" / f"{jid}.json").is_file() and not hidden
          and not (art / "pending" / f"{jid}.json").exists(),
          "2 a manifest that cannot be archived leaves the job in failed/, never under a hidden name",
          (r, err, hidden))


def case_build_refuses():
    art = new_art()
    (art / "pending" / "someone_elses_job.json").write_text('{"id": "x", "target_def": "RM_')   # torn
    audit, census, out = art / "audit.json", art / "census.json", art / "jobs.json"
    audit.write_text(json.dumps({"roster": {}, "defs": {}}))
    census.write_text(json.dumps({"biome_order": [], "biomes": {}}))

    class Scanned(Exception):
        pass

    def boom(*a, **k):
        raise Scanned()
    rc = None
    with swap(DJ, ART=art, load_xml_defs=boom), swap(DJ.BA, Repo=boom, Cls=boom):
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            try:
                rc = DJ.build(audit, census, None, out)
            except Scanned:
                rc = "scanned on"
    check(rc == 2 and not out.exists(), "3 an unparseable queued job refuses the build (its def is unknown)", rc)
    un = []
    with swap(DJ, ART=art):
        DJ.queue_view(un)
    check(len(un) == 1 and "someone_elses_job" in un[0], "3b queue_view reports the unreadable job", un)


def case_dry_parity():
    art = new_art()
    failjob(art, "dregen_RM_X_c_v1")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        DJ.requeue(art, 40, 10, True, Gate(recheck_ok=False), journal=lambda: 0)
    check("would requeue" not in buf.getvalue(),
          "4 requeue --dry-run omits a job the publish-time recheck refuses", buf.getvalue())
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        DJ.requeue(art, 40, 10, True, Gate(), journal=lambda: 0)
    check("would requeue dregen_RM_X_c_v1" in buf.getvalue() and (art / "failed" / "dregen_RM_X_c_v1.json").is_file(),
          "4b the dry run lists an eligible job and moves nothing", buf.getvalue())


def case_refused_log():
    art = new_art(refs=False)
    jobs = art / "jobs.json"
    jobs.write_text(json.dumps({"rows": [{"id": "dregen_RM_X_d_v1", "facings": [], "target_def": "RM_X"}]}))
    err = None
    with swap(DJ, ART=art, in_flight=lambda: 0, queue_view=lambda *a: ({}, set())):
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                rc = DJ.submit_one(jobs, 40, False, Gate(eligible=False))
            except OSError as e:
                rc, err = None, e
    log = art / "_refs" / "jobs.refused.log"
    check(err is None and rc == 0 and log.is_file(), "5 a refusal is logged even before _refs/ exists", (rc, err))


def main() -> int:
    for c in (case_journal, case_manifest_rename, case_build_refuses, case_dry_parity, case_refused_log):
        try:
            c()
        except Exception as e:                             # noqa: BLE001
            check(False, f"{c.__name__} crashed", repr(e))
    print("ALL PASS" if not FAILS else f"{len(FAILS)} FAIL")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
