#!/usr/bin/env python3
# selftest-timeout: 300
"""selftest_scratch_reap_tmp_committed_saves.py — a git-less repo COPY in /tmp is scratch, not work (OPS_TMP_DRAIN_RESTORE_DEVU).

The instance (2026-11-04): agents' mutation runs copied the repo tree, without .git, to /tmp/rmmut, /tmp/mj, /tmp/bj
(3.7 GB each). The copy carries the committed world/*.rws, so keeps_work() called it work; sweep_tmp left it to the clone
judgment, which never sees a dir with no .git, and the 18 GB tmpfs alarmed TMP_FULL twice. A save whose bytes are a
blob origin/main already tracks is not work; an untracked save beside it still is.

Every path is a temp root named through SCRATCH_REAP_TMP / SCRATCH_REAP_SAVE_REPO; the real /tmp is never written.
"""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
FAILS = []
IDLE = 3


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()


def main():
    td = Path(tempfile.mkdtemp(prefix="selftest_scratch_reap_tmp_cs_"))
    roots, tmp, repo = td / "roots", td / "tmp", td / "repo"
    for d in (roots, tmp, repo / "world"):
        d.mkdir(parents=True)
    (td / "transcripts").mkdir()
    os.environ.update(SCRATCH_REAP_ROOTS=os.pathsep.join([str(roots), str(tmp)]), SCRATCH_REAP_TMP=str(tmp),
                      SCRATCH_REAP_SCAN=os.pathsep.join([str(roots), str(tmp)]), SCRATCH_REAP_CORPUS=str(td / "corpus"),
                      SCRATCH_REAP_STATE=str(td / "state"), SCRATCH_REAP_TRANSCRIPTS=str(td / "transcripts"),
                      SCRATCH_REAP_MIRRORS=str(td / "nomirror"), SCRATCH_REAP_RM_SCRATCH="/nonexistent",
                      LEFTOVERS_ARCHIVE_ROOT=str(td / "archive"), SCRATCH_REAP_TMP_IDLE_HOURS=str(IDLE / 3600),
                      RM_RUN_TMP_ROOT=str(td / "runs"), SCRATCH_REAP_SAVE_REPO=str(repo))
    os.environ.pop("SCRATCH_REAP_UNIT", None)
    os.environ.pop("SCRATCH_REAP_PROTECTED", None)
    try:
        committed = "<savegame>the canonical world</savegame>"
        (repo / "world" / "W.rws").write_text(committed)
        git(td, "init", "-q", "-b", "main", str(repo))
        git(repo, "add", "world/W.rws")
        git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "w")
        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")

        for name in ("repocopy", "nested/m"):                       # /tmp/mj shape and /tmp/bj/m shape
            (tmp / name / "world").mkdir(parents=True)
            (tmp / name / "world" / "W.rws").write_text(committed)
            (tmp / name / "src.py").write_text("x = 1\n")
        (tmp / "realsave" / "world").mkdir(parents=True)              # a copy beside an untracked save
        (tmp / "realsave" / "world" / "W.rws").write_text(committed)
        (tmp / "realsave" / "mine.rws").write_text("<savegame>an agent's own</savegame>")
        (tmp / "edited" / "world").mkdir(parents=True)                # a tracked name whose bytes changed
        (tmp / "edited" / "world" / "W.rws").write_text(committed + " edited")
        (tmp / "W.rws").write_text(committed)                          # a loose copy of the committed save
        time.sleep(IDLE + 0.5)

        import scratch_reap as s
        ctx = s.Ctx(time.time())
        out, rows = s.sweep_tmp(ctx, False, 0)
        picked = {os.path.relpath(r["path"], tmp) for r in rows}
        ok({"repocopy", "nested", "W.rws"} <= picked, "a repo copy holding only committed saves is idle scratch (%s, work=%s)" % (sorted(picked), out["work"]))
        ok(not ({"realsave", "edited"} & picked), "a dir with an untracked or edited save is still work (%s)" % sorted(picked))
        ok(out["work"] == 2, "exactly the two real-save dirs are the clone judgment's (work=%s)" % out["work"])

        os.environ["SCRATCH_REAP_SAVE_REPO"] = str(td / "no-such-repo")
        s._COMMITTED_SAVES = None
        out, rows = s.sweep_tmp(s.Ctx(time.time()), False, 0)
        ok(not rows and out["work"] == 5, "with no readable origin/main every save is work, as before (work=%s, rows=%s)" % (out["work"], len(rows)))
    finally:
        subprocess.run(["rm", "-rf", str(td)])
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
