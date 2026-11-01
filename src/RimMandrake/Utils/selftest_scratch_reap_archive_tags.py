#!/usr/bin/env python3
"""Selftest for scratch_reap.py's answer to SCRATCHREAP_FIX_ARCHIVE_TAGS_CRY_WOLF, apart from selftest_scratch_reap.py:
that one plants processes and reads the machine, this one only reads git. The live-process gate is stubbed: a busy
machine's unreadable pid would hold every fixture, and that gate is selftest_scratch_reap.py's to prove."""
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import selftest_scratch_reap as T  # noqa: E402
from selftest_scratch_reap import R, age, check, clone, clone_old, commit, git, acts, run_reaper  # noqa: E402


def archive_tag_cases(td: Path, origin: Path):
    """SCRATCHREAP_FIX_ARCHIVE_TAGS_CRY_WOLF: a hash or a ref name is not content. A clone from before a history rewrite
    goes when its objects are proved held or kept; a dead tracking ref holds nothing; a dead local ref still refuses."""
    root = td / "r_tags"
    s = root / "S"
    s.mkdir(parents=True)
    (td / "archive_tags").mkdir()
    keys = ("SCRATCH_REAP_ROOTS", "SCRATCH_REAP_SCAN", "LEFTOVERS_ARCHIVE_ROOT", "SCRATCH_REAP_MIRRORS")
    saved = {k: os.environ.get(k) for k in keys}
    os.environ.update(SCRATCH_REAP_ROOTS=str(root), SCRATCH_REAP_SCAN=str(root), LEFTOVERS_ARCHIVE_ROOT=str(td / "archive_tags"))
    caps = R.BUNDLE_CAP, R.RESIDUE_CAP
    dead = "1" * 40

    def old_clone(name: str, tag: str, text: str) -> Path:
        """Tag <tag> moved: this clone's copy is a commit of its own, holding <text>; every commit hash here is new."""
        c = clone(origin, s / name)
        git(c, "checkout", "-q", "--orphan", "before_rewrite")
        (c / "kept.txt").write_text(text)
        git(c, "add", "--", "kept.txt")
        git(c, "commit", "-q", "-m", "history before the rewrite")
        git(c, "tag", "-f", tag)
        return c

    def proved_tag(tag: str, text: str):
        w = clone(origin, td / f"tag_writer_{tag}")
        (w / "kept.txt").write_text(text)
        git(w, "add", "--", "kept.txt")
        git(w, "commit", "-q", "-m", "on GitHub under this tag")
        git(w, "tag", tag)
        git(w, "push", "-q", "origin", "refs/tags/" + tag)

    try:
        # a dead tracking ref and a dangling origin/HEAD are not a reason to keep a clean clone
        c = clone_old(origin, s / "dead_tracking_clone")
        (c / ".git/refs/remotes/origin/backup").mkdir(parents=True)
        (c / ".git/refs/remotes/origin/backup/gone").write_text(dead + "\n")
        (c / ".git/refs/remotes/origin/HEAD").write_text("ref: refs/remotes/origin/nowhere\n")
        orphan = subprocess.run(
            ["git", "-C", str(c), "hash-object", "-w", "--stdin"], input="what only the dead ref reached\n", capture_output=True,
            text=True, check=True).stdout.strip()
        age(c)
        # a dead local ref is work we cannot read
        h = clone_old(origin, s / "dead_head_clone")
        (h / ".git/refs/heads/lost").write_text(dead + "\n")
        age(h)
        # a clone's tag that moved on GitHub, its old object gone with the lender's gc; and one GitHub never had
        proved_tag("moved_dead", "moved\n")
        m = clone_old(origin, s / "dead_moved_tag_clone")
        (m / ".git/refs/tags/moved_dead").write_text(dead + "\n")
        age(m)
        u = clone_old(origin, s / "dead_unknown_tag_clone")
        (u / ".git/refs/tags/only_here").write_text(dead + "\n")
        age(u)
        rc, rows = run_reaper("--apply")
        check(rows["dead_moved_tag_clone"]["verdict"] == "DELETED" and not m.exists(), "a dead tag GitHub has by name does not hold the clone")
        check((Path(rows["dead_moved_tag_clone"]["archive"]) / "dead_refs.txt").read_text().startswith(dead), "the dead name is kept")
        check(rows["dead_unknown_tag_clone"]["verdict"] == "REFUSE" and u.exists(), "a dead tag on no mirror still refuses")
        shutil.rmtree(u)
        check(rows["dead_tracking_clone"]["verdict"] == "DELETED" and not c.exists(), "a dead tracking ref and origin/HEAD do not hold a clean clone")
        with tarfile.open(Path(rows["dead_tracking_clone"]["archive"]) / "objects.tar.gz") as tf:
            check(any(orphan[2:] in n for n in tf.getnames()), "an object only the dead ref reached is kept")
        check(rows["dead_head_clone"]["verdict"] == "REFUSE" and h.exists(), "a dead refs/heads ref still refuses")
        check("cannot list refs" in " ".join(rows["dead_head_clone"]["why"]), "the refusal names the ref list")
        shutil.rmtree(h)

        # a clone holding GitHub's tag as GitHub has it holds nothing unique, though no branch reaches the tag
        plain = clone_old(origin, s / "current_tag_clone")
        check("moved_dead" in git(plain, "tag"), "the fixture clone has the tag")
        rc, rows = run_reaper("--apply")
        check(rows["current_tag_clone"]["verdict"] == "DELETED" and not rows["current_tag_clone"].get("archive"),
              "a tag on the mirror is pushed: nothing to bundle")

        # an annotated tag of its own on a pushed commit: its text is on no mirror
        at = clone_old(origin, s / "own_annotated_tag_clone")
        git(at, "tag", "-a", "note_here", "-m", "the only copy of this note")
        tag_sha = git(at, "rev-parse", "note_here")
        age(at)
        rc, rows = run_reaper("--apply")
        row = rows["own_annotated_tag_clone"]
        check(rc == 0 and row["verdict"] == "DELETED" and row.get("archive"), "an annotated tag of its own is preserved first")
        got = td / "annot_restore.git"
        subprocess.run(["git", "init", "-q", "--bare", str(got)], check=True)
        git(got, "fetch", "-q", str(origin), "+refs/heads/main:refs/heads/main")
        git(got, "fetch", "-q", str(Path(row["archive"]) / "clone.bundle"), "refs/rm/*:refs/rm/*")
        check("the only copy of this note" in git(got, "cat-file", "-p", tag_sha), "the tag restores from the bundle")

        # a live tracking ref's commits are still counted: it proves nothing about a push
        t = clone_old(origin, s / "live_tracking_clone")
        commit(t, "only_here.txt", "fetched once, branch gone from the remote")
        sha = git(t, "rev-parse", "HEAD")
        git(t, "update-ref", "refs/remotes/origin/gone_branch", sha)
        git(t, "reset", "-q", "--hard", "HEAD~1")
        R._MIRROR_TIPS = None
        tips, n, _, err = R.unique_commits(t)
        check(err is None and n == 1 and tips == [sha], "a readable tracking ref still counts as a tip")
        shutil.rmtree(t)

        # the whole history moved, every blob is on the mirror under a tag: nothing but the metadata is kept
        proved_tag("snap_a", "on github\n")
        a = old_clone("moved_tag_proved_clone", "snap_a", "on github\n")
        age(a)
        R.BUNDLE_CAP = 1
        rc, rows = run_reaper("--apply")
        row = rows["moved_tag_proved_clone"]
        check(rc == 0 and row["verdict"] == "DELETED" and not a.exists(), "a tag-only difference does not block the reap")
        kept = Path(row["archive"])
        check(not (kept / "clone.bundle").exists(), "over the cap: no bundle")
        names = (kept / "residual.txt").read_text()
        check(" commit " in names and " blob " not in names, "the commit is kept, a blob GitHub holds is not")
        check("refs/tags/snap_a" in (kept / "refs.txt").read_text(), "the ref list is kept")
        check(json.loads((kept / "manifest.json").read_text())["residual"]["objects"] >= 1, "the manifest counts the objects")

        # the same, with one blob nowhere else: that blob is kept, restorable, and only then is the clone deleted
        proved_tag("snap_b", "on github too\n")
        b = old_clone("moved_tag_unique_clone", "snap_b", "excised text, on no mirror\n")
        blob, tip = git(b, "rev-parse", "HEAD:kept.txt"), git(b, "rev-parse", "HEAD")
        age(b)
        rc, rows = run_reaper("--apply")
        row = rows["moved_tag_unique_clone"]
        check(rc == 0 and row["verdict"] == "DELETED" and not b.exists(), "a residual blob is kept, then the clone goes")
        kept = Path(row["archive"])
        check(blob in (kept / "residual.txt").read_text(), "the residual list names the blob")
        r = td / "restore_residual"
        subprocess.run(["git", "init", "-q", "--bare", str(r)], check=True)
        shutil.copy(kept / "residual.pack", r / "objects/pack/residual.pack")
        git(r, "index-pack", str(r / "objects/pack/residual.pack"))
        check(git(r, "cat-file", "-p", blob) == "excised text, on no mirror", "the residual blob restores from the pack alone")
        check("history before the rewrite" in git(r, "log", "-1", "--format=%s", tip) and "kept.txt" in git(r, "ls-tree", tip),
              "the commit and its tree restore from the pack alone")
        check(any(x.get("path") == str(b) and "residual" in x.get("verify", "") for x in acts(td / "archive_tags")), "acts.jsonl records it")

        # over the cap: stays, and a refusal is not a failed run
        proved_tag("snap_c", "third\n")
        o = old_clone("moved_tag_over_cap_clone", "snap_c", "too much to keep\n")
        age(o)
        R.RESIDUE_CAP = 1
        rc, rows = run_reaper("--apply")
        row = rows["moved_tag_over_cap_clone"]
        check(rc == 0 and row["verdict"] == "REFUSE" and o.exists(), "a residual over the cap refuses and deletes nothing")
        R.RESIDUE_CAP = caps[1]
        shutil.rmtree(o)

        # the proof is the tag: gone from the mirror, or the mirror unreadable, the same blob is residual
        proved_tag("snap_d", "tag decides\n")
        d = old_clone("tag_absent_clone", "snap_d", "tag decides\n")
        blob = git(d, "rev-parse", "HEAD:kept.txt")
        check(blob in R.proved_objects(), "a blob under a mirror tag is proved")
        git(origin, "tag", "-d", "snap_d")
        check(blob not in R.proved_objects(), "the same blob without the tag is not")
        age(d)
        rc, rows = run_reaper("--apply")
        kept = Path(rows["tag_absent_clone"]["archive"])
        check(not d.exists() and blob in (kept / "residual.txt").read_text(), "a mirror without the tag excuses nothing: the blob is kept")
        os.environ["SCRATCH_REAP_MIRRORS"] = str(td / "no_such_mirror")
        check(R.proved_objects() == set(), "an unreadable mirror proves nothing")
        neg = clone(origin, td / "neg_clone")
        tip = git(neg, "rev-parse", "HEAD")
        work = td / "neg_work"
        work.mkdir()
        real_tips, real_proved = R.mirror_tips, R.proved_objects
        R.mirror_tips, R.proved_objects = lambda: [tip], set     # a tip named, but no mirror walked
        try:
            R.make_residual(neg, [tip], work, "test")
            check(tip in (work / "residual.txt").read_text(), "a mirror tip that was never walked excludes nothing")
        finally:
            R.mirror_tips, R.proved_objects = real_tips, real_proved
    finally:
        R.BUNDLE_CAP, R.RESIDUE_CAP = caps
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def zombie_cases(td: Path):
    """A real zombie cannot be read but holds nothing: it must not blind a run."""
    pid = os.fork()
    if pid == 0:
        os._exit(0)
    real = R.Live._read
    try:
        for _ in range(50):
            if " Z " in R._who(f"/proc/{pid}") + " ":
                break
            time.sleep(0.02)

        def denied(self, p, base, cmds):
            if p == str(pid):
                raise PermissionError(13, "Permission denied")
            return real(self, p, base, cmds)
        R.Live._read = denied
        check(not [b for b in R.Live(time.time()).blind if f"pid {pid} " in b], "a zombie is not a blind spot")
    finally:
        R.Live._read = real
        os.waitpid(pid, 0)


def main() -> int:
    with tempfile.TemporaryDirectory(dir="/tmp") as tds:        # not $TMPDIR: on a seat that is a root the real reaper reaps
        td = Path(tds)
        os.environ.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
                          GIT_CONFIG_GLOBAL="/dev/null")
        origin = td / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
        seed = clone(origin, td / "seed")
        commit(seed, "a.txt", "a")
        git(seed, "push", "-q", "origin", "HEAD:main")
        st = td / "corpus/infrastructure/state"
        for x in ("handoffs", "ledger/events", "items/closed"):
            (st / x).mkdir(parents=True)
        (st / "canon.yml").write_text("start_savegame: x.rws\n")
        (td / "tr/-proj").mkdir(parents=True)
        os.environ.update(SCRATCH_REAP_CORPUS=str(td / "corpus"), SCRATCH_REAP_STATE=str(td / "state"), SCRATCH_REAP_TTL_HOURS="24",
                          SCRATCH_REAP_MIRRORS=str(origin), SCRATCH_REAP_TRANSCRIPTS=str(td / "tr"),
                          SCRATCH_REAP_PROTECTED=str(td / "protected"))
        R.Ctx.global_holds = lambda self: []
        archive_tag_cases(td, origin)
        zombie_cases(td)
    print("FAILED: " + "; ".join(T.FAILS) if T.FAILS else "ALL PASS")
    return 1 if T.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
