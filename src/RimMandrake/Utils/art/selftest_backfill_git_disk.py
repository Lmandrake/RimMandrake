#!/usr/bin/env python3
"""selftest_backfill_git_disk.py — backfill.step_git decides "on disk now" from the worktree (review wave 90).

A history picture whose bytes are not on disk today is copied into the store. The old code asked the newest
texture snapshot instead, so a picture the snapshot listed but that was deleted since was never stored, and was
recorded on_disk_now=True. Offline: a throwaway git repo, ledger and store under one temp dir.
"""
from __future__ import annotations

import atexit
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_selftest_backfill_git_disk_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:400]}]"))
    if not cond:
        FAILS.append(msg)


def png(color):
    from PIL import Image
    b = io.BytesIO()
    Image.new("RGBA", (8, 8), color).save(b, "PNG")
    return b.getvalue()


def git(repo, *a):
    subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True,
                   env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                            GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null"))


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="bf-git-"))
    os.environ.update(ARTSTORE=str(tmp / "store"), ART_LEDGER_DIR=str(tmp / "ledger"),
                      ART_SRC_ROOT=str(tmp / "repo" / "src"), ART_SEAT="BUILD")
    import artledger as L
    import backfill as BF
    repo = tmp / "repo"
    tex = repo / "src" / "RimMandrake" / "M" / "Textures"
    tex.mkdir(parents=True)
    git(repo, "init", "-q")
    gone, kept = png((200, 10, 10, 255)), png((10, 200, 10, 255))
    (tex / "gone.png").write_bytes(gone)
    (tex / "kept.png").write_bytes(kept)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "add")
    # a dated snapshot that still lists gone.png, then gone.png is deleted from disk and history moves on
    snap = tmp / "ledger" / "snapshots"
    snap.mkdir(parents=True)
    rel = "src/RimMandrake/M/Textures/"
    (snap / "2026-10-04_textures.tsv").write_text(
        "sha256\tbytes\tpath\n" + "".join(f"{L.sha256_bytes(b)}\t{len(b)}\t{rel}{n}\n"
                                          for n, b in (("gone.png", gone), ("kept.png", kept))))
    git(repo, "rm", "-q", f"{rel}gone.png")
    git(repo, "commit", "-q", "-m", "rm")
    old_root = L.REPO_ROOT
    L.REPO_ROOT = repo
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            r = BF.step_git(budget=60)
    finally:
        L.REPO_ROOT = old_root
    sg, sk = L.sha256_bytes(gone), L.sha256_bytes(kept)
    check(L.store_has(sg), "a history picture deleted since the last snapshot is copied into the store", r)
    check(not L.store_has(sk), "a picture still on disk is not duplicated into the store", r)
    ev = {e["sha"]: e for e in L.read_events() if e.get("type") == "variant" and e.get("kind") == "git"}
    check(ev.get(sg, {}).get("on_disk_now") is False and ev.get(sk, {}).get("on_disk_now") is True,
          "on_disk_now describes the worktree", {k[:8]: v.get("on_disk_now") for k, v in ev.items()})
    # `art.py backfill artpipe` with no _artsrc to read is UNMEASURED: it must not exit 0 like a clean import
    import argparse
    import art as A
    old_ap = BF.ARTPIPE
    BF.ARTPIPE = tmp / "no_artpipe_here"
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            rc = A.cmd_backfill(argparse.Namespace(step="artpipe", budget=60))
    finally:
        BF.ARTPIPE = old_ap
    check(rc != 0, "an UNMEASURED backfill step exits non-zero", rc)
    # the same class in the donor and canon steps (w94): a source that is not there is UNMEASURED, never a clean 0
    saved = BF.BUNDLES, BF.CENSUS_CSV, BF.CANON
    BF.BUNDLES, BF.CENSUS_CSV, BF.CANON = tmp / "no_bundles", tmp / "no_census.csv", tmp / "no_canon"
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            rc_d = A.cmd_backfill(argparse.Namespace(step="donor", budget=60))
            rc_c = A.cmd_backfill(argparse.Namespace(step="canon", budget=60))
            BF.BUNDLES = tmp / "bundles"
            BF.BUNDLES.mkdir()
            r_half = BF.step_donor(budget=60)
            BF.CENSUS_CSV.write_text("source,path,row_id\n")
            rc_ok = A.cmd_backfill(argparse.Namespace(step="donor", budget=60))
    finally:
        BF.BUNDLES, BF.CENSUS_CSV, BF.CANON = saved
    check(rc_d != 0, "backfill donor with neither donor source present exits non-zero", rc_d)
    check(rc_c != 0, "backfill canon with no canon_references dir exits non-zero", rc_c)
    check("census" in r_half.get("error", "").lower() or "no_census" in r_half.get("error", ""),
          "backfill donor names the one source it could not see", r_half)
    check(rc_ok == 0, "control: backfill donor with both sources present (and empty) exits 0", rc_ok)
    print("ALL PASS" if not FAILS else f"{len(FAILS)} FAIL")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
