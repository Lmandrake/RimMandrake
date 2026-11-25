#!/usr/bin/env python3
"""Apply the reaper to temporary run dirs and a clone with nothing unique but a dirty file."""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from selftest_scratch_reap import FAILS, R, acts, age, check, clone, commit, run_reaper

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rimflow"))
import run_tmp  # noqa: E402


def deadline_bypassed_by_run_tmp(runs):
    runs.mkdir()
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    name = run_tmp.pid_name("exited", child.pid)
    child.wait()
    now = time.time() + run_tmp.GRACE_S + 1
    real_rmtree = shutil.rmtree

    def finish_opening_scan(*args):
        nonlocal now
        now += 2

    def remove_then_expire(path, *args, **kwargs):
        real_rmtree(path, *args, **kwargs)
        if Path(path).parent == runs:
            finish_opening_scan()

    with patch("time.time", lambda: now), patch.object(run_tmp, "users", return_value=(set(), [])) as users:
        first = runs / name
        first.mkdir()
        with patch.object(R, "sanity_start", side_effect=finish_opening_scan):
            rc, _ = run_reaper("--apply", "--max-seconds", "1")
        check(rc == 0 and first.is_dir() and not users.called,
              "deadline_bypassed_by_run_tmp: an expired apply skips the per-run sweep and leaves the dir")
        if first.exists():
            first.rmdir()

        for prefix in ("", f".reaping-{child.pid}-"):
            first, second = (runs / (prefix + name + suffix) for suffix in ("-a", "-b"))
            first.mkdir()
            second.mkdir()
            with patch.object(shutil, "rmtree", side_effect=remove_then_expire):
                rc, _ = run_reaper("--apply", "--max-seconds", "1")
            kind = "crash pin" if prefix else "run dir"
            check(rc == 0 and not first.exists() and second.is_dir(),
                  f"deadline_bypassed_by_run_tmp: the next {kind} stays when the first deletion spends the budget")
            rc, _ = run_reaper("--apply", "--max-seconds", "1")
            check(rc == 0 and not second.exists(), f"the next apply has time to remove the remaining {kind}")


def dirty_archive_claims_bundle_restore(td, root, origin, archive):
    source = clone(origin, root / "untracked_file_clone")
    dirty = "ITEM_PROSE.md"
    payload = b"only copy\n"
    (source / dirty).write_bytes(payload)
    wrong = td / "wrong"
    wrong.mkdir()
    (wrong / dirty).write_bytes(b"lost copy\n")
    age(source)
    real_make_tar = R.make_tar

    def wrong_bytes(top, paths, out):
        real_make_tar(wrong if top == source else top, paths, out)

    with patch.object(R, "make_tar", side_effect=wrong_bytes):
        rc, rows = run_reaper("--apply")
    check(rc == 1 and rows[source.name]["verdict"] == "REFUSE" and (source / dirty).is_file() and not acts(archive),
          "dirty_archive_claims_bundle_restore: a listable tar with wrong bytes leaves the source and no receipt")

    if not source.exists():
        clone(origin, source)
        (source / dirty).write_bytes(payload)
        age(source)
    rc, rows = run_reaper("--apply")
    check(rc == 0 and rows[source.name]["verdict"] == "DELETED" and not source.exists(),
          "a verified dirty-only archive lets apply remove the source")
    dest = Path(rows[source.name]["archive"])
    restored = td / "restored"
    restored.mkdir()
    subprocess.run(["tar", "-xzf", str(dest / "dirty.tar.gz"), "-C", str(restored)], check=True)
    check((restored / dirty).read_bytes() == payload and not (dest / "clone.bundle").exists(),
          "the dirty-only archive restores the untracked file's bytes")
    receipt = next(a for a in acts(archive) if a["archive"] == str(dest))
    check("tar restored" in receipt["verify"] and "bundle" not in receipt["verify"],
          "dirty_archive_claims_bundle_restore: the dirty-only receipt records a tar restore and no bundle restore")


def main():
    with tempfile.TemporaryDirectory(prefix="selftest_scratch_reap_restore_deadline_") as tmp:
        td = Path(tmp)
        root, origin, archive = td / "scratch", td / "origin", td / "archive"
        runs, corpus, transcripts = td / "runs", td / "corpus", td / "transcripts"
        for folder in (root, origin, archive, transcripts, corpus / "infrastructure/state/ledger/events",
                       corpus / "infrastructure/state/items"):
            folder.mkdir(parents=True)
        env = dict(SCRATCH_REAP_ROOTS=str(root), SCRATCH_REAP_SCAN=str(root), SCRATCH_REAP_STATE=str(td / "state"),
                   SCRATCH_REAP_CORPUS=str(corpus), SCRATCH_REAP_TRANSCRIPTS=str(transcripts),
                   SCRATCH_REAP_MIRRORS=str(origin), SCRATCH_REAP_RM_SCRATCH=str(root), SCRATCH_REAP_TMP="",
                   LEFTOVERS_ARCHIVE_ROOT=str(archive), RM_RUN_TMP_ROOT=str(runs), GIT_CONFIG_GLOBAL=os.devnull,
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        with patch.dict(os.environ, env):
            subprocess.run(["git", "init", "-q", "-b", "main", str(origin)], check=True)
            commit(origin, "a.txt", "on main")
            deadline_bypassed_by_run_tmp(runs)
            dirty_archive_claims_bundle_restore(td, root, origin, archive)
    return int(bool(FAILS))


if __name__ == "__main__":
    sys.exit(main())
