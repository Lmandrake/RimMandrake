#!/usr/bin/env python3
"""selftest_scratch_reap_spike_causes.py -- the three transient causes that spiked scratch_reap's refused count over its
end line on 2026-11-05 count once per cause, not once per row (REAPER_SPIKE_FIX_THREE_STRANGERS_AT_DOOR).

  A. 11:03Z, 139: entries deleted INSIDE a candidate while it was walked (a selftest's rmtree) read as `unreadable:
     … No such file`. Now: a one-off vanish is walked again and judged normally; a tree that keeps losing entries is
     YOUNG (changing), never REFUSE.
  B. 12:02Z, 140: 94 corrupt repos (lender gone, `missing object … for refs/heads/main`) inside one session were 94
     rows. Now: one REFUSE row, the session's, naming them; the corrupt repos stay kept.
  C. 15:01Z, 69: one process standing in a pruned worktree (`/home/mandrake/wt_p3/.git` pointing at a gitdir that
     is gone) made the user scan blind, so every candidate was refused. Now: a pruned worktree is seen, not blind,
     and the missing gitdir's own path is held.
Guards kept: a really unreadable spot still refuses; a corrupt clone still never deletes."""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "rimflow")]
import scratch_reap as R  # noqa: E402

FAILS = []
OLD = time.time() - 30 * 86400


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def age(top: Path):
    for dp, dns, fns in os.walk(top, topdown=False):
        for n in dns + fns:
            os.utime(os.path.join(dp, n), (OLD, OLD), follow_symlinks=False)
    os.utime(top, (OLD, OLD))


def git(c: Path, *a):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", "-C", str(c), *a], capture_output=True, text=True, env=env, check=True).stdout.strip()


def corrupt_repo(c: Path):
    c.mkdir(parents=True)
    git(c, "init", "-q", "-b", "main")
    (c / "f.txt").write_text("x")
    git(c, "add", "f.txt")
    git(c, "commit", "-q", "-m", "x")
    sha = git(c, "rev-parse", "HEAD")
    (c / ".git" / "objects" / sha[:2] / sha[2:]).unlink()      # the lender it borrowed from is gone


def case_vanish(root: Path):
    c = root / "BENCH" / "vanish" / "clone"
    c.mkdir(parents=True)
    git(c, "init", "-q", "-b", "main")
    for i in range(6):
        (c / f"f{i}.txt").write_text("x")
    age(c.parent.parent)
    real = R.os.scandir

    class Listed(list):                                 # listed first, then the rmtree takes one: its stat finds nothing
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def listed_then(path, victim_of):
        with real(path) as it:
            got = Listed(it)
        v = victim_of(got)
        if v is not None:
            os.unlink(v.path)
        return got
    budget = {"n": 1}                                   # one entry deleted under the first walk only

    def racing(path):
        if path != str(c) or not budget["n"]:
            return real(path)
        budget["n"] -= 1
        return listed_then(path, lambda es: next(e for e in es if e.name.startswith("f")))

    R.os.scandir = racing
    try:
        row = R.judge_clone(c, R.Ctx(time.time()))
    finally:
        R.os.scandir = real
    check(row["verdict"] != "REFUSE" and not any("unreadable" in w for w in row["why"]),
          f"A1 one entry deleted mid-walk: walked again, not refused ({row['verdict']} {row['why'][:1]})")

    def always(path):                                   # a selftest still tearing it down on the second walk too
        if path != str(c):
            return real(path)
        return listed_then(path, lambda es: next((e for e in es if e.name.startswith("f")), None))

    R.os.scandir = always
    try:
        row = R.judge_clone(c, R.Ctx(time.time()))
    finally:
        R.os.scandir = real
    check(row["verdict"] == "YOUNG" and row.get("changing"), f"A2 a tree losing entries on every walk is YOUNG, changing "
          f"({row['verdict']} {row['why'][:1]})")
    shutil.rmtree(c)
    rows = [r for r in [row] if (r["verdict"] != "REFUSE" and not r.get("changing")) or os.path.lexists(r["path"])]
    check(rows == [], "A3 judge_all's filter drops a changing row once its tree is gone")

    e = root / "BENCH" / "ghost" / "clone"             # listed on every walk, never stat-able: not a delete in progress
    e.mkdir(parents=True)
    git(e, "init", "-q", "-b", "main")
    (e / "ghost.txt").write_text("x")
    age(e.parent.parent)

    def ghost_scandir(path):
        if path != str(e):
            return real(path)

        class Ghost:
            def __init__(self, de):
                self._de, self.name, self.path = de, de.name, de.path

            def stat(self, follow_symlinks=True):
                if self.name == "ghost.txt":
                    raise FileNotFoundError(2, "No such file or directory")
                return self._de.stat(follow_symlinks=follow_symlinks)

            def is_dir(self, follow_symlinks=True):
                return self._de.is_dir(follow_symlinks=follow_symlinks)
        with real(path) as it:
            return Listed(Ghost(x) for x in it)

    R.os.scandir = ghost_scandir
    try:
        row = R.judge_clone(e, R.Ctx(time.time()))
    finally:
        R.os.scandir = real
    check(row["verdict"] == "REFUSE" and any("listed but cannot be read" in w for w in row["why"]),
          f"A5 an entry listed but never stat-able is still refused as unreadable ({row['verdict']} {row['why'][:1]})")
    shutil.rmtree(e.parent)

    d = root / "BENCH" / "locked" / "clone"            # the guard stays: an unreadable spot still refuses
    (d / ".git").mkdir(parents=True)
    (d / "sub").mkdir()
    age(d.parent.parent)
    os.chmod(d / "sub", 0)
    try:
        row = R.judge_clone(d, R.Ctx(time.time()))
    finally:
        os.chmod(d / "sub", 0o755)
    check(os.geteuid() == 0 or (row["verdict"] == "REFUSE" and any("unreadable" in w for w in row["why"])),
          f"A4 a really unreadable spot still refuses ({row['verdict']})")
    shutil.rmtree(d.parent)


def sighted_ctx():
    """A Ctx blind to nothing: in a walled box every foreign pid reads "Permission denied", a global hold that would
    mask the corrupt-repo reason this case is about (the box's process table is not the fixture)."""
    ctx = R.Ctx(time.time())
    ctx.live.blind, ctx.borrows.hold = [], []
    return ctx


def case_corrupt(root: Path):
    s = root / "FOUNDRY" / "claude-1000" / "-home-x" / "5ac3d971-76d6-4b1a-8656-3c6104d96849"
    n = 5
    for i in range(n):
        corrupt_repo(s / "scratchpad" / f"r{i}" / "repo")
    age(s)
    row, inner = R.judge_session(s, sighted_ctx())
    check(row["verdict"] == "REFUSE", f"B1 the session holding corrupt repos is refused ({row['verdict']})")
    check(any(f"{n} inner repo(s) git cannot read" in w for w in row["why"]),
          f"B2 its row names all {n} corrupt repos once ({row['why'][:2]})")
    check(not [r for r in inner if r["verdict"] == "REFUSE"], f"B3 no per-repo REFUSE rows "
          f"({len([r for r in inner if r['verdict'] == 'REFUSE'])} of {n})")
    check(len(row.get("corrupt_inner", [])) == n, "B4 the session row lists every corrupt repo it keeps")
    alone = R.judge_clone(s / "scratchpad" / "r0" / "repo", sighted_ctx())
    check(alone["verdict"] == "REFUSE" and alone.get("corrupt"), f"B5 a corrupt repo judged alone is still refused "
          f"({alone['verdict']})")
    shutil.rmtree(s.parent.parent.parent)


def case_pruned_worktree(td: Path):
    repo = td / "main_repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    wt = td / "wt_p3"
    wt.mkdir()
    gd = repo / ".git" / "worktrees" / "wt_p3"             # pruned: the file still points here, the dir is gone
    (wt / ".git").write_text(f"gitdir: {gd}\n")
    live = R.Live.__new__(R.Live)
    live.blind, live.paths = [], []
    got = live._repo_of(str(wt))
    check(got is None and live.blind == [], f"C1 a process standing in a pruned worktree is not blind ({live.blind})")
    check((os.path.realpath(gd), "the missing gitdir a live worktree names") in live.paths,
          f"C2 the missing gitdir is held by its path ({live.paths})")
    live.blind, live.paths = [], []
    live._repo_of(str(wt), quiet=True)
    check(live.blind == [], "C3 a path merely named there is not blind either")
    other = td / "wt_live"                              # the guard stays: an unreadable .git is still blind
    other.mkdir()
    (other / ".git").write_text("no gitdir line here\n")
    live.blind, live.paths = [], []
    check(live._repo_of(str(other)) is None and live.blind, "C5 a .git file we cannot parse stays blind")

    class FakeLive:
        blind = ["pid 1 x: Permission denied"] * 3

    class FakeBorrows:
        hold = []
    ctx = R.Ctx.__new__(R.Ctx)
    ctx.live, ctx.borrows = FakeLive(), FakeBorrows()
    check(ctx.global_holds() == ["cannot see a process: pid 1 x: Permission denied"],
          f"C4 one blind cause is one hold, however many processes repeat it ({ctx.global_holds()})")


def main():
    td = Path(tempfile.mkdtemp(prefix="selftest_spike_causes_"))
    root, sd = td / ".seat-tmp", td / "state"
    root.mkdir()
    sd.mkdir()
    for sub in ("ledger/events", "items"):              # an empty ledger: nothing names these fixtures
        (td / "corpus" / "infrastructure" / "state" / sub).mkdir(parents=True)
    os.environ.pop("SCRATCH_REAP_SANITY", None)
    os.environ.update(SCRATCH_REAP_ROOTS=str(root), SCRATCH_REAP_STATE=str(sd), SCRATCH_REAP_RM_SCRATCH=str(td / "rm_scratch"),
                      SCRATCH_REAP_CORPUS=str(td / "corpus"), SCRATCH_REAP_TMP="", SCRATCH_REAP_MIRRORS=str(td / "nomirror"),
                      SCRATCH_REAP_TTL_HOURS="0")       # ctime cannot be backdated: every tree here is old enough
    try:
        case_vanish(root)
        case_corrupt(root)
        case_pruned_worktree(td)
    finally:
        shutil.rmtree(td, ignore_errors=True)
    print("FAIL" if FAILS else "OK", "selftest_scratch_reap_spike_causes")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
