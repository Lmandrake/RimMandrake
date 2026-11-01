#!/usr/bin/env python3
"""Selftest for publish.py (the thin plain-git wrapper) against a throwaway bare repo + clones
on ext4 (never /tmp).

    python3 src/RimMandrake/Utils/selftest_publish.py
"""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import publish as P  # noqa: E402

ROOT = os.path.expanduser("~/.cache/publish-selftest")
ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"}
os.environ.update(ENV)
LINES = "".join("line %d\n" % i for i in range(1, 11))


def sh(cwd, *a):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr))
    return r.stdout.strip()


def write(repo, path, text):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)


def show(repo, path, ref="origin/main"):
    sh(repo, "fetch", "-q")
    return sh(repo, "show", "%s:%s" % (ref, path)) + "\n"


def world():
    os.makedirs(ROOT, exist_ok=True)
    d = tempfile.mkdtemp(dir=ROOT)
    bare, a, b = (os.path.join(d, n) for n in ("bare.git", "a", "b"))
    sh(d, "init", "-q", "--bare", "-b", "main", bare)
    sh(d, "clone", "-q", bare, a)
    write(a, "f.txt", LINES)
    write(a, "g.txt", "g\n")
    sh(a, "add", "f.txt", "g.txt")
    sh(a, "commit", "-q", "-m", "seed")
    sh(a, "push", "-q", "origin", "HEAD:main")
    sh(d, "clone", "-q", bare, b)
    return d, a, b


def peer_push(b, path, text, msg="peer"):
    sh(b, "pull", "-q", "--rebase")
    write(b, path, text)
    sh(b, "add", path)
    sh(b, "commit", "-q", "-m", msg, "--", path)
    sh(b, "push", "-q", "origin", "HEAD:main")
    return sh(b, "rev-parse", "HEAD")


def quiet(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a)
    return r, buf.getvalue()


def refused(fn, *a):
    try:
        quiet(fn, *a)
    except P.Refuse as e:
        return str(e)
    return None


def t_commits_only_named_paths(a, b):
    write(a, "f.txt", LINES.replace("line 3", "LINE 3"))
    write(a, "g.txt", "dirty, not mine to publish\n")
    write(a, "junk.txt", "untracked\n")
    sh(a, "add", "g.txt")                                     # a staged peer file must not ride along
    sha, log = quiet(P.publish, a, ["f.txt"], "mine")
    assert "PUBLISHED %s" % sha in log, log
    assert sha == sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main")
    assert "LINE 3" in show(a, "f.txt") and show(a, "g.txt") == "g\n"
    assert sh(a, "show", "--name-only", "--format=", "HEAD") == "f.txt"


def t_new_file_and_delete(a, b):
    write(a, "dir/new.sh", "#!/bin/sh\n")
    os.remove(os.path.join(a, "g.txt"))
    quiet(P.publish, a, ["dir/new.sh", "g.txt"], "add+rm")
    names = sh(a, "ls-tree", "-r", "--name-only", "origin/main").split()
    assert "dir/new.sh" in names and "g.txt" not in names, names


def t_rebases_onto_moved_origin(a, b):
    peer = peer_push(b, "g.txt", "peer g\n")
    write(a, "f.txt", LINES.replace("line 9", "LINE 9"))
    sha, _ = quiet(P.publish, a, ["f.txt"], "mine")
    assert sh(a, "rev-parse", sha + "^") == peer
    assert "LINE 9" in show(a, "f.txt") and show(a, "g.txt") == "peer g\n"


def t_push_race_retries(a, b):
    write(a, "f.txt", LINES.replace("line 5", "LINE 5"))
    seen = {}

    def race(attempt):
        if attempt == 0:
            seen["peer"] = peer_push(b, "g.txt", "raced\n")
    P.before_push = race
    try:
        sha, log = quiet(P.publish, a, ["f.txt"], "mine")
    finally:
        P.before_push = None
    assert "origin moved" in log, log
    assert sh(a, "rev-parse", sha + "^") == seen["peer"]


def t_dirty_tree_survives_rebase(a, b):
    peer_push(b, "g.txt", "peer\n")
    write(a, "f.txt", LINES.replace("line 1\n", "LINE 1\n"))
    write(a, "h.txt", "untracked\n")
    sh(a, "add", "h.txt")
    sh(a, "commit", "-q", "-m", "h", "--", "h.txt")
    write(a, "h.txt", "uncommitted edit\n")                     # reset --keep must leave it alone
    quiet(P.publish, a, ["f.txt"], "mine")
    assert open(os.path.join(a, "h.txt")).read() == "uncommitted edit\n"
    assert show(a, "h.txt") == "untracked\n"


def t_real_overlap_lands_commit_leaves_clone_and_file(a, b):
    """A dirty file that really overlaps origin must not stop the commit landing, and must not be touched."""
    peer_push(b, "g.txt", "peer v2\n")
    write(a, "g.txt", "my uncommitted edit\n")                 # dirty, and origin changed the same line
    write(a, "f.txt", LINES.replace("line 3", "LINE 3"))
    head0 = sh(a, "rev-parse", "HEAD")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        sha = P.publish(a, ["f.txt"], "mine")
    assert "LANDED, CLONE NOT MOVED" in buf.getvalue() and "g.txt" in buf.getvalue(), buf.getvalue()
    assert show(a, "f.txt") == LINES.replace("line 3", "LINE 3") and show(a, "g.txt") == "peer v2\n"
    assert sha == sh(a, "rev-parse", "origin/main")
    assert open(os.path.join(a, "g.txt")).read() == "my uncommitted edit\n"   # the peer's bytes, untouched
    assert sh(a, "log", "-1", "--format=%s") == "mine" and sh(a, "rev-parse", "HEAD^") == head0   # branch stayed
    assert not sh(a, "stash", "list")
    write(a, "g.txt", "peer v2\n")                              # the overlap resolves: the branch catches up
    write(a, "h.txt", "next\n")
    sha2 = P_quiet_publish(a, ["h.txt"], "next")
    assert sha2 == sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main")
    assert sh(a, "log", "-3", "--format=%s").splitlines()[:2] == ["next", "mine"]    # replayed once, not twice


def P_quiet_publish(a, paths, msg):
    with contextlib.redirect_stdout(io.StringIO()):
        return P.publish(a, paths, msg)


def clean_hunks(a):
    return [ln for ln in sh(a, "diff", "-U0", "HEAD").splitlines()
            if ln[:1] in "+-" and ln[:3] not in ("+++", "---")]


def t_peer_hunk_in_file_origin_moved_merges_in_place(a, b):
    """Tonight's jam: a peer's uncommitted hunk in a file origin also changed, away from origin's lines."""
    peer_push(b, "f.txt", LINES.replace("line 2", "ORIGIN 2"))
    write(a, "f.txt", LINES.replace("line 9", "PEER 9"))
    write(a, "h.txt", "mine\n")
    sha = P_quiet_publish(a, ["h.txt"], "mine")
    assert sha == sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main")   # the clone moved too
    assert open(os.path.join(a, "f.txt")).read() == LINES.replace("line 2", "ORIGIN 2").replace("line 9", "PEER 9")
    assert clean_hunks(a) == ["-line 9", "+PEER 9"]              # exactly the peer's hunk, still uncommitted
    assert show(a, "f.txt") == LINES.replace("line 2", "ORIGIN 2")
    assert not os.path.exists(os.path.join(sh(a, "rev-parse", "--absolute-git-dir"), "rm-dirty-parked", "x"))


SHARD = "ledger/events/S.jsonl"


def seed_shard(a, b):
    write(a, ".gitattributes", "ledger/events/*.jsonl merge=union\n")
    write(a, SHARD, "seed\n")
    P_quiet_publish(a, [".gitattributes", SHARD], "shard")
    sh(b, "pull", "-q", "--rebase")


def append(a, path, line):
    fd = os.open(os.path.join(a, path), os.O_WRONLY | os.O_APPEND)
    os.write(fd, line.encode())
    os.close(fd)


def t_shard_appends_on_both_sides_land(a, b):
    seed_shard(a, b)
    peer_push(b, SHARD, "seed\nfrom origin\n")
    ino = os.stat(os.path.join(a, SHARD)).st_ino
    append(a, SHARD, "live append\n")
    write(a, "h.txt", "mine\n")
    sha = P_quiet_publish(a, ["h.txt"], "mine")
    assert sha == sh(a, "rev-parse", "HEAD")
    assert os.stat(os.path.join(a, SHARD)).st_ino == ino         # git never replaced the file under a live appender
    assert sorted(open(os.path.join(a, SHARD))) == ["from origin\n", "live append\n", "seed\n"]
    assert clean_hunks(a) == ["+live append"]                    # a pure addition against the index
    sha2 = P_quiet_publish(a, [SHARD], "ledger")
    assert sorted(show(a, SHARD).splitlines()) == ["from origin", "live append", "seed"] and sha2


def t_stale_shard_snapshot_in_index_lands(a, b):
    """A commit races appends: the index holds an older snapshot of the shard, every line of it still on disk."""
    seed_shard(a, b)
    peer_push(b, SHARD, "seed\nfrom origin\n")
    append(a, SHARD, "first\n")
    sh(a, "add", SHARD)
    append(a, SHARD, "second\n")
    write(a, "h.txt", "mine\n")
    sha = P_quiet_publish(a, ["h.txt"], "mine")
    assert sha == sh(a, "rev-parse", "HEAD")                     # landed and moved: not stranded
    assert sorted(open(os.path.join(a, SHARD))) == ["first\n", "from origin\n", "second\n", "seed\n"]


def t_shard_index_line_missing_from_disk_is_not_dropped(a, b):
    """The staged shard holds a line the file does not: not a stale snapshot, so the clone stays put."""
    seed_shard(a, b)
    peer_push(b, SHARD, "seed\nfrom origin\n")
    append(a, SHARD, "only staged\n")
    sh(a, "add", SHARD)
    write(a, SHARD, "seed\nlater\n")
    write(a, "h.txt", "mine\n")
    P_quiet_publish(a, ["h.txt"], "mine")
    assert "only staged" in sh(a, "show", ":" + SHARD)
    assert open(os.path.join(a, SHARD)).read() == "seed\nlater\n"
    assert show(a, "h.txt") == "mine\n"


def t_carry_that_died_mid_write_finishes(a, b):
    """A torn tail that upstream's line completes is our own dead carry: finished, not a conflict for ever."""
    seed_shard(a, b)
    peer_push(b, SHARD, "seed\nfrom origin\n")
    append(a, SHARD, "local\nfrom or")
    write(a, "h.txt", "mine\n")
    sha = P_quiet_publish(a, ["h.txt"], "mine")
    assert sha == sh(a, "rev-parse", "HEAD")
    assert sorted(open(os.path.join(a, SHARD))) == ["from origin\n", "local\n", "seed\n"]


def t_shard_is_never_swapped_even_if_a_merge_exists(a, b):
    """A torn tail nothing completes: merge-file could still resolve it, but only by replacing a live inode."""
    seed_shard(a, b)
    peer_push(b, SHARD, "seed\nfrom origin\n")
    append(a, SHARD, "torn tail")
    ino = os.stat(os.path.join(a, SHARD)).st_ino
    write(a, "h.txt", "mine\n")
    P_quiet_publish(a, ["h.txt"], "mine")
    assert os.stat(os.path.join(a, SHARD)).st_ino == ino
    assert open(os.path.join(a, SHARD)).read() == "seed\ntorn tail"
    assert show(a, "h.txt") == "mine\n"


def t_unmerged_index_is_left_alone(a, b):
    peer_push(b, "f.txt", LINES.replace("line 2", "ORIGIN 2"))
    sh(a, "fetch", "-q")
    blob = sh(a, "hash-object", "-w", "f.txt")
    write(a, "f.txt", LINES.replace("line 5", "MINE 5"))
    subprocess.run(["git", "update-index", "--index-info"], cwd=a, check=True, text=True,
                   input="0 %s\tf.txt\n100644 %s 1\tf.txt\n100644 %s 2\tf.txt\n" % ("0" * 40, blob, blob))
    import seat_sync as S
    g, target = S.Git(a), sh(a, "rev-parse", "origin/main")
    head = sh(a, "rev-parse", "HEAD")
    assert S.dirty_merges(g, head, target, [])[1] == ["f.txt"]
    assert sh(a, "ls-files", "-u", "--", "f.txt")                # both stages still there


def t_mode_change_with_equal_bytes_is_not_claimed(a, b):
    sh(b, "pull", "-q", "--rebase")
    os.chmod(os.path.join(b, "f.txt"), 0o755)
    sh(b, "commit", "-qam", "exec")
    sh(b, "push", "-q", "origin", "HEAD:main")
    os.chmod(os.path.join(a, "f.txt"), 0o755)
    write(a, "h.txt", "mine\n")
    P_quiet_publish(a, ["h.txt"], "mine")
    assert show(a, "h.txt") == "mine\n"
    assert os.stat(os.path.join(a, "f.txt")).st_mode & 0o100


def t_commit_displaced_by_the_move_is_pinned_and_named(a, b):
    """No check can close the gap before git reads HEAD: plant it, with HEAD already past what the caller saw."""
    head = sh(a, "rev-parse", "HEAD")
    peer_push(b, "z.txt", "up\n")
    sh(a, "fetch", "-q")
    target = sh(a, "rev-parse", "origin/main")
    write(a, "n.txt", "peer commit\n")
    sh(a, "add", "n.txt")
    sh(a, "commit", "-qm", "peer", "--", "n.txt")
    late = sh(a, "rev-parse", "HEAD")
    import seat_sync as S
    try:
        S.reset_keep(S.Git(a), head, target, [])
    except S.Refused as e:
        assert late[:12] in str(e)
    else:
        raise AssertionError("a displaced commit went unreported")
    assert sh(a, "rev-parse", "refs/rm-rescued/" + late) == late


def t_save_in_the_swap_gap_survives(a, b):
    """The editor saves after the last compare: the swap displaces it, the proof sees it, it goes back and merges."""
    import seat_sync as Q
    peer_push(b, "f.txt", LINES.replace("line 2", "ORIGIN 2"))
    write(a, "f.txt", LINES.replace("line 5", "MINE 5"))
    real, fired = Q._exchange, []

    def gap(x, y):
        if not fired:
            fired.append(1)
            write(a, "f.txt", LINES.replace("line 5", "MINE 5").replace("line 7", "LATE 7"))
        real(x, y)
    Q._exchange = gap
    try:
        write(a, "h.txt", "mine\n")
        P_quiet_publish(a, ["h.txt"], "mine")
    finally:
        Q._exchange = real
    got = open(os.path.join(a, "f.txt")).read()
    assert fired and all(w in got for w in ("MINE 5", "LATE 7", "ORIGIN 2")), got


def t_second_save_in_the_gap_is_parked_not_overwritten(a, b):
    import glob
    import seat_sync as Q
    peer_push(b, "f.txt", LINES.replace("line 2", "ORIGIN 2"))
    write(a, "f.txt", LINES.replace("line 5", "MINE 5"))
    real, n = Q._exchange, []

    def gap(x, y):
        n.append(1)
        if len(n) <= 2:
            write(a, "f.txt", LINES.replace("line 5", "MINE 5").replace("line 7", "LATE %d" % len(n)))
        real(x, y)
    Q._exchange = gap
    try:
        write(a, "h.txt", "mine\n")
        P_quiet_publish(a, ["h.txt"], "mine")
    finally:
        Q._exchange = real
    kept = open(os.path.join(a, "f.txt")).read() + "".join(open(f).read() for f in glob.glob(
        os.path.join(a, ".git", "rm-dirty-parked", "*", "late-*")))
    assert "LATE 1" in kept and "LATE 2" in kept
    assert show(a, "h.txt") == "mine\n"


def t_write_through_an_old_descriptor_keeps_the_park(a, b):
    """The swap proved the bytes, then the holder of the old inode wrote: the path no longer sees it, the park must."""
    import glob
    import seat_sync as Q
    peer_push(b, "f.txt", LINES.replace("line 2", "ORIGIN 2"))
    write(a, "f.txt", LINES.replace("line 5", "MINE 5"))
    fd = os.open(os.path.join(a, "f.txt"), os.O_WRONLY | os.O_APPEND)
    real = Q.reset_keep

    def later(*k):
        os.write(fd, b"LATE\n")
        return real(*k)
    Q.reset_keep = later
    try:
        write(a, "h.txt", "mine\n")
        P_quiet_publish(a, ["h.txt"], "mine")
    finally:
        Q.reset_keep = real
        os.close(fd)
    swaps = glob.glob(os.path.join(a, ".git", "rm-dirty-parked", "*", "swap-*"))
    assert swaps and "LATE" in open(swaps[0]).read()


def t_clean_shard_keeps_its_inode(a, b):
    """No dirty line at all: git would unlink and rewrite it, and an append through an open fd would vanish."""
    seed_shard(a, b)
    peer_push(b, SHARD, "seed\nfrom origin\n")
    write(a, "h.txt", "mine\n")
    fd = os.open(os.path.join(a, SHARD), os.O_WRONLY | os.O_APPEND)   # an appender already holds it open
    P_quiet_publish(a, ["h.txt"], "mine")
    os.write(fd, b"late append\n")
    os.close(fd)
    assert sorted(open(os.path.join(a, SHARD))) == ["from origin\n", "late append\n", "seed\n"]


def t_overlap_appearing_after_preview_changes_nothing(a, b):
    """Planted: a peer's edit lands between the preview and the write. _carry must abort before anything moves."""
    import seat_sync
    peer_push(b, "f.txt", LINES.replace("line 2", "ORIGIN 2"))
    write(a, "f.txt", LINES.replace("line 9", "PEER 9"))
    write(a, "h.txt", "mine\n")
    real = seat_sync.dirty_merges
    def peer_edits(*args):
        got = real(*args)
        write(a, "f.txt", LINES.replace("line 2", "PEER 2"))
        return got
    seat_sync.dirty_merges = peer_edits
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            P.publish(a, ["h.txt"], "mine")
    finally:
        seat_sync.dirty_merges = real
    assert "LANDED, CLONE NOT MOVED" in buf.getvalue(), buf.getvalue()
    assert open(os.path.join(a, "f.txt")).read() == LINES.replace("line 2", "PEER 2")
    assert show(a, "h.txt") == "mine\n"


def t_reset_refused_restores_index_and_keeps_original(a, b):
    """Planted: git refuses after the carry. Index back as it was; the original bytes stay parked; a re-run lands."""
    import seat_sync
    peer_push(b, "f.txt", LINES.replace("line 2", "ORIGIN 2"))
    dirty = LINES.replace("line 9", "PEER 9")
    write(a, "f.txt", dirty)
    write(a, "h.txt", "mine\n")
    real = seat_sync.reset_keep
    def boom(*args, **kw):
        raise seat_sync.Refused("planted refusal")
    seat_sync.reset_keep = boom
    try:
        why = refused(P.publish, a, ["h.txt"], "mine")
    finally:
        seat_sync.reset_keep = real
    assert why and "planted refusal" in why, why
    gd = sh(a, "rev-parse", "--absolute-git-dir")
    parked = [os.path.join(r, n) for r, _, ns in os.walk(os.path.join(gd, "rm-dirty-parked")) for n in ns]
    assert parked and open(parked[0]).read() == dirty, parked
    assert sh(a, "diff", "--cached", "--name-only") == ""        # index matches HEAD again
    assert "PEER 9" in open(os.path.join(a, "f.txt")).read() and "ORIGIN 2" in open(os.path.join(a, "f.txt")).read()
    sha = P_quiet_publish(a, [], None)                           # the re-run merges to the same result
    assert sha == sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main")
    assert open(os.path.join(a, "f.txt")).read() == LINES.replace("line 2", "ORIGIN 2").replace("line 9", "PEER 9")


def t_crash_between_carry_and_move_loses_nothing(a, b):
    """Planted: publish dies right after the working-tree write. The file holds both sides; the next run finishes."""
    import seat_sync
    peer_push(b, "f.txt", LINES.replace("line 2", "ORIGIN 2"))
    write(a, "f.txt", LINES.replace("line 9", "PEER 9"))
    write(a, "h.txt", "mine\n")
    real = seat_sync.Git.run
    def die(self, *args, **kw):
        if args[:1] == ("update-index",):
            raise KeyboardInterrupt("planted crash")
        return real(self, *args, **kw)
    seat_sync.Git.run = die
    try:
        try:
            P.publish(a, ["h.txt"], "mine")
            raise AssertionError("the planted crash did not fire")
        except KeyboardInterrupt:
            pass
    finally:
        seat_sync.Git.run = real
    sha = P_quiet_publish(a, [], None)
    assert sha == sh(a, "rev-parse", "origin/main")
    assert open(os.path.join(a, "f.txt")).read() == LINES.replace("line 2", "ORIGIN 2").replace("line 9", "PEER 9")
    assert clean_hunks(a) == ["-line 9", "+PEER 9"]


def t_third_version_in_index_is_not_dropped(a, b):
    """Index, working tree, HEAD and origin all differ: no merge is defined, so the clone stays put."""
    peer_push(b, "f.txt", LINES.replace("line 2", "ORIGIN 2"))
    write(a, "f.txt", LINES.replace("line 5", "STAGED 5"))
    sh(a, "add", "f.txt")
    write(a, "f.txt", LINES.replace("line 7", "WORK 7"))
    write(a, "h.txt", "mine\n")
    P_quiet_publish(a, ["h.txt"], "mine")
    assert open(os.path.join(a, "f.txt")).read() == LINES.replace("line 7", "WORK 7")
    assert "STAGED 5" in sh(a, "show", ":f.txt")
    assert show(a, "h.txt") == "mine\n"


def t_binary_dirty_file_is_never_merged(a, b):
    with open(os.path.join(a, "b.bin"), "wb") as f:
        f.write(b"\0one\n")
    P_quiet_publish(a, ["b.bin"], "bin")
    sh(b, "pull", "-q", "--rebase")
    with open(os.path.join(b, "b.bin"), "wb") as f:
        f.write(b"\0two\n")
    sh(b, "commit", "-qam", "bin2")
    sh(b, "push", "-q", "origin", "HEAD:main")
    with open(os.path.join(a, "b.bin"), "wb") as f:
        f.write(b"\0mine\n")
    write(a, "h.txt", "mine\n")
    P_quiet_publish(a, ["h.txt"], "mine")
    assert open(os.path.join(a, "b.bin"), "rb").read() == b"\0mine\n"


def t_conflict_aborts_rebase(a, b):
    peer_push(b, "g.txt", "peer says x\n")
    write(a, "g.txt", "i say y\n")
    why = refused(P.publish, a, ["g.txt"], "clash")
    assert why and "g.txt" in why, why
    assert not os.path.isdir(os.path.join(a, ".git", "rebase-merge"))
    assert sh(a, "log", "-1", "--format=%s") == "clash"         # commit intact locally


def t_ambiguous_push_detected_as_landed(a, b):
    write(a, "f.txt", LINES.replace("line 2", "LINE 2"))
    real = P.run

    def flaky(top, *args, check=True):
        if args[:1] == ("push",):
            real(top, *args, check=check)                       # remote accepts...
            return subprocess.CompletedProcess(args, 128, "", "fatal: the remote end hung up")
        return real(top, *args, check=check)
    P.run = flaky
    try:
        sha, log = quiet(P.publish, a, ["f.txt"], "mine")
    finally:
        P.run = real
    assert "it landed" in log, log
    assert sha == sh(a, "rev-parse", "origin/main")


def t_nothing_to_publish(a, b):
    why = refused(P.publish, a, ["f.txt"], "noop")
    assert why and "nothing to publish" in why, why


def t_pushes_existing_local_commits(a, b):
    write(a, "x.txt", "x\n")
    sh(a, "add", "x.txt")
    sh(a, "commit", "-q", "-m", "x", "--", "x.txt")
    sha, _ = quiet(P.publish, a, [], None)
    assert sha == sh(a, "rev-parse", "origin/main")


def t_refuses_on_mnt(a, b):
    real = os.path.realpath
    P.os.path.realpath = lambda p: "/mnt/d/Luke/dev/RimMandrake" if p == a else real(p)
    try:
        why = refused(P.publish, a, ["f.txt"], "x")
    finally:
        P.os.path.realpath = real
    assert why and "/home/mandrake/rm/<seat>" in why, why


# ---- committed mod DLLs at landing (rebuilt from committed source, winbuild mocked) ----------------------
MOD = "src/RimMandrake/M"
DLL = MOD + "/Assemblies/M.dll"
HOOK = r"""#!/usr/bin/env python3
import hashlib, subprocess, sys
def git(*a):
    return subprocess.run(["git", *a], capture_output=True).stdout
for line in sys.stdin.read().splitlines():
    sha = line.split()[1]
    names = sorted(n for n in git("ls-tree", "-r", "--name-only", sha, "--", "%(mod)s/Source").decode().split()
                   if n.endswith(".cs"))
    want = "dll:" + hashlib.sha256(b"".join(n.encode() + git("show", "%%s:%%s" %% (sha, n)) for n in names)).hexdigest()
    if git("show", "%%s:%(dll)s" %% sha).decode() != want:
        sys.stderr.write("pre-push REFUSED (DLL_SOURCE_STAMP_GUARD_1): committed DLL disagrees\n  MISMATCH %(dll)s\n")
        sys.exit(1)
""" % {"mod": MOD, "dll": DLL}


def fake_build(tree):
    """What the mocked winbuild writes for the C# in `tree` (a worktree root)."""
    import hashlib
    src = os.path.join(tree, MOD, "Source")
    names = sorted(f for f in os.listdir(src) if f.endswith(".cs"))
    data = b"".join((MOD + "/Source/" + n).encode() + open(os.path.join(src, n), "rb").read() for n in names)
    write(tree, DLL, "dll:" + hashlib.sha256(data).hexdigest())
    write(tree, DLL + ".srchash", "# project: RimMandrake/M/Source/M.csproj\n" + "".join(
        "%s %s\n" % (hashlib.sha256(open(os.path.join(src, n), "rb").read()).hexdigest(), n) for n in names))


def mock_winbuild(calls):
    def wb(scratch, csproj):
        calls.append((scratch, os.path.relpath(csproj, scratch)))
        fake_build(scratch)
        return 0, "BUILT"
    return wb


def seed_mod(a, b):
    for n in ("A", "B", "C"):
        write(a, MOD + "/Source/%s.cs" % n, "class %s {}\n" % n)
    write(a, MOD + "/Source/M.csproj", "<Project/>\n")
    fake_build(a)
    sh(a, "add", MOD)
    sh(a, "commit", "-q", "-m", "mod")
    sh(a, "push", "-q", "origin", "HEAD:main")
    sh(b, "pull", "-q", "--rebase")
    P.SCRATCH_ROOT = os.path.join(os.path.dirname(a), "scratch")


def dll_matches(repo, ref="origin/main"):
    """origin's DLL equals a build of origin's committed source (checked in a fresh checkout)."""
    chk = os.path.join(os.path.dirname(repo), "chk")
    shutil.rmtree(chk, ignore_errors=True)
    sh(repo, "fetch", "-q")
    sh(os.path.dirname(repo), "clone", "-q", "--shared", repo, chk)
    sh(chk, "checkout", "-q", "--detach", sh(repo, "rev-parse", ref))
    want = open(os.path.join(chk, DLL)).read()
    fake_build(chk)
    return open(os.path.join(chk, DLL)).read() == want


def t_dll_only_replay_conflict_rebuilds(a, b):
    seed_mod(a, b)
    write(b, MOD + "/Source/A.cs", "class A { int peer; }\n")       # peer: source + its DLL, landed first
    fake_build(b)
    sh(b, "add", MOD)
    sh(b, "commit", "-q", "-m", "peer A + dll")
    sh(b, "push", "-q", "origin", "HEAD:main")
    write(a, MOD + "/Source/B.cs", "class B { int mine; }\n")       # mine: another file + my DLL -> DLL-only conflict
    fake_build(a)
    write(a, MOD + "/Source/C.cs", "class C { UNCOMMITTED PEER EDIT }\n")   # must not leak into the build
    calls = []
    real, P.winbuild = getattr(P, "winbuild", None), mock_winbuild(calls)
    try:
        sha, log = quiet(P.publish, a, [MOD + "/Source/B.cs", DLL, DLL + ".srchash"], "mine B + dll")
    finally:
        P.winbuild = real
    assert "PUBLISHED" in log and calls, log
    assert sha == sh(a, "rev-parse", "origin/main")
    assert "int peer" in show(a, MOD + "/Source/A.cs") and "int mine" in show(a, MOD + "/Source/B.cs")
    assert dll_matches(a), "landed DLL is not a build of the landed source"
    assert "UNCOMMITTED" in open(os.path.join(a, MOD + "/Source/C.cs")).read()      # peer edit untouched
    assert not sh(a, "stash", "list") and not os.listdir(P.SCRATCH_ROOT)             # no stash, scratch removed


def t_stamp_guard_refusal_rebuilds_and_retries(a, b):
    seed_mod(a, b)
    hooks = os.path.join(os.path.dirname(a), "hooks")
    write(hooks, "pre-push", HOOK)
    os.chmod(os.path.join(hooks, "pre-push"), 0o755)
    sh(a, "config", "core.hooksPath", hooks)
    write(a, MOD + "/Source/B.cs", "class B { int changed; }\n")    # source only: the committed DLL goes stale
    write(a, MOD + "/Source/C.cs", "class C { UNCOMMITTED PEER EDIT }\n")
    calls = []
    real, P.winbuild = getattr(P, "winbuild", None), mock_winbuild(calls)
    P.MAX_TRIES, old_tries = 2, P.MAX_TRIES
    try:
        sha, log = quiet(P.publish, a, [MOD + "/Source/B.cs"], "source only")
    finally:
        P.winbuild, P.MAX_TRIES = real, old_tries
    assert "DLL_SOURCE_STAMP_GUARD_1" in log and len(calls) == 1, log
    assert sha == sh(a, "rev-parse", "origin/main") and dll_matches(a)
    assert "UNCOMMITTED" in open(os.path.join(a, MOD + "/Source/C.cs")).read()


def t_stamp_guard_rebuild_never_overwrites_dirty_dll(a, b):
    """review wave 87: the rebuild writes the DLL pair into the worktree; an uncommitted edit there is refused, kept."""
    seed_mod(a, b)
    hooks = os.path.join(os.path.dirname(a), "hooks")
    write(hooks, "pre-push", HOOK)
    os.chmod(os.path.join(hooks, "pre-push"), 0o755)
    sh(a, "config", "core.hooksPath", hooks)
    write(a, MOD + "/Source/B.cs", "class B { int changed; }\n")
    write(a, DLL, "SOMEONE'S UNCOMMITTED LOCAL BUILD")
    calls = []
    real, P.winbuild = getattr(P, "winbuild", None), mock_winbuild(calls)
    P.MAX_TRIES, old_tries = 2, P.MAX_TRIES
    try:
        why = refused(P.publish, a, [MOD + "/Source/B.cs"], "source only")
    finally:
        P.winbuild, P.MAX_TRIES = real, old_tries
    assert why and "uncommitted edits" in why and DLL in why, why
    assert open(os.path.join(a, DLL)).read() == "SOMEONE'S UNCOMMITTED LOCAL BUILD"
    assert not calls, calls


PUBLISH_PY = os.environ.get("PUBLISH_PY", os.path.join(os.path.dirname(os.path.abspath(__file__)), "publish.py"))


def race_once(a, b, workers=12, pushes=10, tag="w"):
    """`workers` real ./publish processes in ONE clone commit a file each while a peer keeps moving origin.
    Returns (lost, lied): files missing from origin/main or from disk, and workers that printed PUBLISHED
    although their file is not on origin/main."""
    import threading
    stop = threading.Event()

    def mover():
        for i in range(pushes):
            try:
                peer_push(b, "%smv%d.txt" % (tag, i), "m%d\n" % i)
            except Exception:  # noqa: BLE001
                pass
        stop.set()
    for i in range(workers):
        write(a, "%s%d.txt" % (tag, i), "w%d\n" % i)
    t = threading.Thread(target=mover)
    t.start()
    env = dict(os.environ, PYTHONPATH=os.path.dirname(os.path.abspath(__file__)))
    cmd = ("for n in $(seq 30); do %s %s -m w%d " + tag + "%d.txt && exit 0; sleep 0.1; done; exit 1")
    procs = [subprocess.Popen(["bash", "-c", cmd % (sys.executable, PUBLISH_PY, i, i)], cwd=a, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for i in range(workers)]
    res = [(p.communicate(), p.returncode) for p in procs]
    t.join()
    sh(a, "fetch", "-q")
    onorigin = set(sh(a, "ls-tree", "-r", "--name-only", "origin/main").splitlines())
    lost, lied = [], []
    for i, ((so, se), rc) in enumerate(res):
        f = "%s%d.txt" % (tag, i)
        if f not in onorigin or not os.path.exists(os.path.join(a, f)):
            lost.append(f)
            if "PUBLISHED" in so:
                lied.append(f)
        elif f in onorigin and rc not in (0,):
            pass
    return lost, lied, res


def t_concurrent_publishers_lose_nothing(a, b):
    """Old code lost commits in ~16% of these rounds (measured 4/25); 15 rounds catch it ~93% of the time."""
    for rnd in range(15):
        lost, lied, res = race_once(a, b, tag="r%d_" % rnd)
        assert not lost, "round %d: commits vanished: %s (printed PUBLISHED anyway: %s)" % (rnd, lost, lied)
        for (so, se), rc in res:
            assert rc == 0 and "PUBLISHED" in so, "worker failed: rc=%s %s%s" % (rc, so, se)


def t_stale_head_aborts_not_discards(a, b):
    """A commit that lands on HEAD between the replay and the reset makes publish refuse, never drop it."""
    peer_push(b, "g.txt", "moved\n")
    write(a, "mine.txt", "m\n")
    sh(a, "add", "mine.txt")
    sh(a, "commit", "-q", "-m", "mine")

    def intrude():
        write(a, "intruder.txt", "i\n")
        sh(a, "add", "intruder.txt")
        sh(a, "commit", "-q", "-m", "intruder")
    P.before_reset = intrude
    try:
        msg = refused(P.rebase, a)
    finally:
        P.before_reset = None
    assert msg and "HEAD moved" in msg, msg
    assert os.path.exists(os.path.join(a, "intruder.txt"))
    assert "intruder" in sh(a, "log", "--format=%s")


def t_lock_times_out_loudly(a, b):
    import fcntl
    fd = os.open(P.lock_path(a), os.O_CREAT | os.O_RDWR)
    fcntl.flock(fd, fcntl.LOCK_EX)
    old = P.LOCK_TIMEOUT
    P.LOCK_TIMEOUT = 0.5
    try:
        write(a, "x.txt", "x\n")
        msg = refused(P.publish, a, ["x.txt"], "x")
    finally:
        P.LOCK_TIMEOUT = old
        os.close(fd)
    assert msg and "lock" in msg, msg
    assert "x.txt" not in sh(a, "log", "--format=%s", "--name-only")


def t_lock_released_when_holder_dies(a, b):
    code = ("import fcntl,os,sys,time;sys.path.insert(0,%r);import publish as P;"
            "fd=os.open(P.lock_path(%r),os.O_CREAT|os.O_RDWR);fcntl.flock(fd,fcntl.LOCK_EX);"
            "print('held',flush=True);time.sleep(60)") % (os.path.dirname(PUBLISH_PY), a)
    h = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, text=True)
    assert h.stdout.readline().strip() == "held"
    h.kill()
    h.wait()
    write(a, "x.txt", "x\n")
    quiet(P.publish, a, ["x.txt"], "x")
    assert show(a, "x.txt") == "x\n"


# ---- the real race: live appenders and a live editor in one clone while origin moves the same files ------------
PUBLISHER = ("import sys,fcntl\nsys.path.insert(0,%r)\nimport seat_sync,publish\n"
             "if sys.argv[1]=='bare': seat_sync.reset_merging=lambda g,h,t,k=None: seat_sync.reset_keep(g,h,t,k)\n"
             "sys.exit(publish.main(sys.argv[2:]))\n") % os.path.dirname(os.path.abspath(__file__))


def live_race(a, b, seconds, mutant="real"):
    """Three flock-and-append writers on one shard, one editor rewriting its own line (it checks mtime first, as the
    Edit tool does), two ./publish loops in the clone, and a peer clone pushing to the same shard and the same file.
    Returns (lines written, lines missing from origin, publishes by outcome)."""
    import fcntl
    import threading
    import time
    seed_shard(a, b)
    stop = time.time() + seconds
    written, lock, last_peer, outcomes = [], threading.Lock(), [0], {}

    def appender(n):
        i = 0
        while time.time() < stop:
            line = "w%d-%d\n" % (n, i)
            fd = os.open(os.path.join(a, SHARD), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            fcntl.flock(fd, fcntl.LOCK_EX)
            os.write(fd, line.encode())
            os.close(fd)
            with lock:
                written.append(line.strip())
            i += 1
            time.sleep(0.002)

    def editor():
        i = 0
        full = os.path.join(a, "f.txt")
        while time.time() < stop:
            m = os.stat(full).st_mtime_ns
            text = open(full).read().splitlines(True)
            text[8] = "PEER %d\n" % i
            if os.stat(full).st_mtime_ns == m:          # the Edit tool's own stale-read check
                with open(full, "w") as f:
                    f.writelines(text)
                last_peer[0] = i
            i += 1
            time.sleep(0.05)

    def mover():
        i = 0
        while time.time() < stop:
            subprocess.run(["git", "pull", "-q", "--rebase"], cwd=b, capture_output=True)
            with open(os.path.join(b, SHARD), "a") as f:
                f.write("m-%d\n" % i)
            text = open(os.path.join(b, "f.txt")).read().splitlines(True)
            text[1] = "ORIGIN %d\n" % i
            open(os.path.join(b, "f.txt"), "w").writelines(text)
            sh(b, "commit", "-qam", "mover %d" % i)
            if not subprocess.run(["git", "push", "-q", "origin", "HEAD:main"], cwd=b, capture_output=True).returncode:
                with lock:
                    written.append("m-%d" % i)
                i += 1
            else:
                sh(b, "reset", "-q", "--hard", "HEAD~1")
            time.sleep(0.2)

    def publisher(n):
        i = 0
        while time.time() < stop:
            name = "p%d-%d.txt" % (n, i)
            write(a, name, "x\n")
            paths = [name] + ([SHARD] if n == 0 else [])
            r = subprocess.run([sys.executable, "-c", PUBLISHER, mutant, "-m", name, *paths], cwd=a,
                               capture_output=True, text=True)
            kind = "refused" if r.returncode else ("stranded" if "NOT MOVED" in r.stdout else "landed")
            with lock:
                outcomes[kind] = outcomes.get(kind, 0) + 1
                if r.returncode:
                    outcomes.setdefault("why", []).append(r.stderr[:300])
            i += 1

    ts = [threading.Thread(target=f, args=x) for f, x in
          [(appender, (0,)), (appender, (1,)), (appender, (2,)), (editor, ()), (mover, ()), (publisher, (0,)), (publisher, (1,))]]
    [t.start() for t in ts]
    [t.join() for t in ts]
    write(a, "last.txt", "x\n")
    sh(a, "fetch", "-q")
    subprocess.run([sys.executable, "-c", PUBLISHER, mutant, "-m", "last", "last.txt", SHARD], cwd=a, capture_output=True)
    subprocess.run([sys.executable, "-c", PUBLISHER, mutant], cwd=a, capture_output=True)
    disk = set(open(os.path.join(a, SHARD)).read().split())
    origin = set(show(a, SHARD).split())
    missing = [w for w in written if w not in origin]
    gone_from_disk = [w for w in written if w not in disk]
    f_txt = open(os.path.join(a, "f.txt")).read()
    return dict(written=len(written), missing=missing[:5], n_missing=len(missing), gone_from_disk=len(gone_from_disk),
                outcomes=outcomes, peer_kept="PEER %d\n" % last_peer[0] in f_txt,
                level=sh(a, "rev-list", "--count", "HEAD..origin/main"))


def t_live_race_loses_nothing_and_lands(a, b):
    got = live_race(a, b, 6)
    assert got["n_missing"] == 0 and got["gone_from_disk"] == 0, got
    assert got["peer_kept"] and got["level"] == "0" and not got["outcomes"].get("refused"), got
    assert got["outcomes"].get("landed", 0) >= 2 and got["written"] > 100, got


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("t_")]


def main():
    if sys.argv[1:2] == ["--race"]:                              # --race <seconds> [bare]: the long evidence run
        d, a, b = world()
        try:
            print(live_race(a, b, int(sys.argv[2]), (sys.argv[3:4] or ["real"])[0]))
        finally:
            shutil.rmtree(d, ignore_errors=True)
        return 0
    ok = 0
    for t in TESTS:
        d, a, b = world()
        try:
            t(a, b)
            ok += 1
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, e))
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print("%d/%d passed" % (ok, len(TESTS)))
    return 0 if ok == len(TESTS) else 1


if __name__ == "__main__":
    sys.exit(main())
