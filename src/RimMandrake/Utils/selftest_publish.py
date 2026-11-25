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

# the machine-wide push lock (RM_ROOT/.publish-push.lock) of this run's publishes lives in a temp root, so a selftest
# never waits on, nor holds up, a real ./publish (children read PUBLISH_RM_ROOT, this process P.RM_ROOT)
os.makedirs(os.path.expanduser("~/.cache/publish-selftest"), exist_ok=True)
P.RM_ROOT = os.environ["PUBLISH_RM_ROOT"] = tempfile.mkdtemp(prefix="lockroot-",
                                                             dir=os.path.expanduser("~/.cache/publish-selftest"))
__import__("atexit").register(shutil.rmtree, P.RM_ROOT, True)

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


def t_unnamed_owner_shard_warns_and_named_does_not(a, b):
    shard = P.OWNER_SHARD
    write(a, shard, "{}\n")
    sh(a, "add", shard)
    sh(a, "commit", "-q", "-m", "seed owner shard")
    sh(a, "push", "-q", "origin", "HEAD:main")
    write(a, shard, "{}\n{\"ruling\": 1}\n")
    write(a, "f.txt", LINES.replace("line 3", "LINE 3"))
    _, log = quiet(P.publish, a, ["f.txt"], "mine")
    assert "WARNING" in log and shard in log, log
    assert "ruling" not in show(a, shard), "the warning must not publish it"
    _, log = quiet(P.publish, a, [shard], "his ruling")
    assert "WARNING" not in log, log
    assert "ruling" in show(a, shard)
    write(a, "g.txt", "clean shard now\n")
    _, log = quiet(P.publish, a, ["g.txt"], "mine")
    assert "WARNING" not in log, log


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


def t_refused_tree_check_leaves_no_commit(a, b):
    """RIMMANDRAKE_UNDO_REFUSED_PUBLISH_COMMIT_NEXT_RUN_LANDED_IT: publish commits, then runs the tree checks; a red refused
    but left its commit on HEAD, so the next publish (its named paths "carry no change") pushed that commit, the refused file
    in it (2026-11-17: two fenced mod-ledger lines reached origin/main and turned selftest_modledger_tree red)."""
    os.makedirs(os.path.join(a, os.path.dirname(P.TREE_CHECKS)), exist_ok=True)
    with open(os.path.join(a, P.TREE_CHECKS), "w") as f:
        f.write('{"budget_s": 30, "timeout_s": 20, "checks": [{"test": "nobad.py", "fix": "remove bad.txt"}]}')
    write(a, "nobad.py", "import os, sys\nsys.exit(1 if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bad.txt')) else 0)\n")
    quiet(P.publish, a, [P.TREE_CHECKS, "nobad.py"], "the door's list and its check, committed: the door reads the commit")
    before = sh(a, "rev-parse", "HEAD")
    write(a, "good.txt", "good\n")
    write(a, "bad.txt", "bad\n")
    why = refused(P.publish, a, ["good.txt", "bad.txt"], "mine")
    assert why and "nobad.py" in why, why
    assert sh(a, "rev-parse", "HEAD") == before, "the refused commit stayed on HEAD"
    assert open(os.path.join(a, "good.txt")).read() == "good\n" and os.path.exists(os.path.join(a, "bad.txt"))
    assert sh(a, "diff", "--cached", "--name-only", "--", "good.txt", "bad.txt") == "", "the refused paths stayed staged"
    os.remove(os.path.join(a, "bad.txt"))                   # the fix: the refused file goes; the rest is published again
    sha, log = quiet(P.publish, a, ["good.txt"], "mine")
    assert "PUBLISHED %s" % sha in log, log
    names = sh(a, "ls-tree", "-r", "--name-only", "origin/main").split()
    assert "good.txt" in names and "bad.txt" not in names, names


def t_new_file_and_delete(a, b):
    write(a, "dir/new.sh", "#!/bin/sh\n")
    os.remove(os.path.join(a, "g.txt"))
    quiet(P.publish, a, ["dir/new.sh", "g.txt"], "add+rm")
    names = sh(a, "ls-tree", "-r", "--name-only", "origin/main").split()
    assert "dir/new.sh" in names and "g.txt" not in names, names


ITEMS_DIR = "infrastructure/state/items"
BENCH_SHARD = "infrastructure/state/ledger/events/BENCH.jsonl"


def _close_move(a, iid):
    """What `rimflow close` does on disk: append to the shard and rename the prose into items/closed/ (no commit)."""
    with open(os.path.join(a, BENCH_SHARD), "a") as f:
        f.write('{"event": "close", "id": "%s"}\n' % iid)
    os.makedirs(os.path.join(a, ITEMS_DIR, "closed"), exist_ok=True)
    os.rename(os.path.join(a, ITEMS_DIR, iid + ".md"), os.path.join(a, ITEMS_DIR, "closed", iid + ".md"))


def t_shard_publish_carries_the_close_prose_move(a, b):
    """RIMMANDRAKE_LAND_CLOSED_PROSE_MOVE_HELPERS_PUBLISH_SHARD_ONLY: a helper publishes only its ledger shard after
    `rimflow close`; the prose rename close made must land with it (five items drifted, 2026-11-18/19)."""
    for iid in ("ITEM_A", "ITEM_B"):
        write(a, "%s/%s.md" % (ITEMS_DIR, iid), "# %s\n" % iid)
    write(a, BENCH_SHARD, "")
    sh(a, "add", ITEMS_DIR, BENCH_SHARD)
    sh(a, "commit", "-q", "-m", "seed items")
    sh(a, "push", "-q", "origin", "HEAD:main")
    _close_move(a, "ITEM_A")
    os.remove(os.path.join(a, ITEMS_DIR, "ITEM_B.md"))      # a deletion with no closed copy is not a close move
    quiet(P.publish, a, [BENCH_SHARD], "ledger: close ITEM_A")
    names = sh(a, "ls-tree", "-r", "--name-only", "origin/main").split()
    assert ITEMS_DIR + "/closed/ITEM_A.md" in names, "closed prose did not land: %s" % names
    assert ITEMS_DIR + "/ITEM_A.md" not in names, "live prose still on main: %s" % names
    assert ITEMS_DIR + "/ITEM_B.md" in names, "an unrelated deletion was carried: %s" % names


def t_non_ledger_publish_carries_no_prose_move(a, b):
    write(a, "%s/ITEM_A.md" % ITEMS_DIR, "# ITEM_A\n")
    write(a, BENCH_SHARD, "")
    sh(a, "add", ITEMS_DIR, BENCH_SHARD)
    sh(a, "commit", "-q", "-m", "seed items")
    sh(a, "push", "-q", "origin", "HEAD:main")
    _close_move(a, "ITEM_A")
    write(a, "g.txt", "changed\n")
    quiet(P.publish, a, ["g.txt"], "code only")
    names = sh(a, "ls-tree", "-r", "--name-only", "origin/main").split()
    assert ITEMS_DIR + "/ITEM_A.md" in names and ITEMS_DIR + "/closed/ITEM_A.md" not in names, \
        "a publish that names no ledger shard carried a prose move: %s" % names


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


def t_replay_never_doubles_a_shard_line_origin_already_holds(a, b):
    # LEDGER_UNION_DEDUPE_PUBLISH_DOUBLED_LINES: merge=union in the plumbing replay wrote a line again when origin had
    # already landed it (another clone, the belt), so shards grew byte-identical twins on every publish.
    seed_shard(a, b)
    append(a, SHARD, "carried\nmine only\n")
    sh(a, "commit", "-q", "-m", "mine", "--", SHARD)
    peer_push(b, SHARD, "seed\npeer first\ncarried\nfrom origin\n")    # origin landed `carried` under other lines
    sha = P_quiet_publish(a, [], None)
    got = show(a, SHARD).splitlines()
    assert sorted(got) == ["carried", "from origin", "mine only", "peer first", "seed"], got
    assert got[:4] == ["seed", "peer first", "carried", "from origin"], got   # origin stays a prefix: append-only
    assert sha and sorted(open(os.path.join(a, SHARD)).read().splitlines()) == sorted(got)


def twin_world(a, b):
    """Clone a holds commit C (new items/X.md + a shard line); origin holds C's twin landed under other shard context,
    then moves items/X.md to items/closed/. Returns C."""
    seed_shard(a, b)
    peer_push(b, SHARD, "seed\npeer line\n")
    write(a, "items/X.md", "prose\n")
    sh(a, "add", "--", "items/X.md")
    append(a, SHARD, "C line\n")
    sh(a, "commit", "-q", "-m", "C", "--", "items/X.md", SHARD)
    write(b, "items/X.md", "prose\n")
    sh(b, "add", "--", "items/X.md")
    append(b, SHARD, "C line\n")
    sh(b, "commit", "-q", "-m", "C", "--", "items/X.md", SHARD)
    os.makedirs(os.path.join(b, "items/closed"), exist_ok=True)
    sh(b, "mv", "items/X.md", "items/closed/X.md")
    sh(b, "commit", "-q", "-m", "close X")
    sh(b, "push", "-q", "origin", "HEAD:main")
    sh(a, "fetch", "-q")
    assert sh(a, "cherry", "origin/main", "HEAD").startswith("+"), "the world must make git cherry call C unlanded"
    return sh(a, "rev-parse", "HEAD")


def t_landed_twin_is_not_replayed_over_an_upstream_move(a, b):
    # RIMMANDRAKE_SKIP_LANDED_TWINS_PUBLISH_REPLAY_RESURRECTS_FILES: git cherry called a landed commit unlanded (its
    # union-shard context differed), the replay re-added prose origin had moved to closed/, and the orphan-prose hook
    # refused every publish; where no hook stopped it, origin took the same commit 27 times.
    twin_world(a, b)
    before = sh(a, "rev-parse", "origin/main")
    write(a, "h.txt", "mine\n")
    sha = P_quiet_publish(a, ["h.txt"], "mine")
    names = sh(a, "ls-tree", "-r", "--name-only", "origin/main").split()
    assert "items/X.md" not in names and "items/closed/X.md" in names, names
    assert sh(a, "rev-parse", sha + "^") == before, "exactly one new commit lands"
    assert sorted(show(a, SHARD).splitlines()) == ["C line", "peer line", "seed"]
    assert sha == sh(a, "rev-parse", "HEAD") and not os.path.exists(os.path.join(a, "items/X.md"))


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


def evil_merge(a):
    """A local merge whose resolution changes a line neither side had: git cherry and diff-tree both miss it."""
    sh(a, "checkout", "-q", "-b", "side")
    write(a, "s.txt", "side\n")
    sh(a, "add", "s.txt")
    sh(a, "commit", "-q", "-m", "side", "--", "s.txt")
    sh(a, "checkout", "-q", "main")
    write(a, "m.txt", "main\n")
    sh(a, "add", "m.txt")
    sh(a, "commit", "-q", "-m", "main", "--", "m.txt")
    sh(a, "merge", "-q", "--no-ff", "--no-commit", "side")
    write(a, "g.txt", "only in the merge\n")
    sh(a, "add", "g.txt")
    sh(a, "commit", "-q", "-m", "merge")


def t_a_local_merge_refuses_never_vanishes(a, b):
    evil_merge(a)
    peer_push(b, "f.txt", LINES.replace("line 2", "ORIGIN 2"))
    head = sh(a, "rev-parse", "HEAD")
    write(a, "h.txt", "mine\n")
    why = refused(P.publish, a, ["h.txt"], "mine")
    assert why and "is a merge" in why, why
    assert sh(a, "rev-parse", "HEAD^") == head and show(a, "g.txt", "HEAD") == "only in the merge\n"


def t_sync_refuses_a_merge_it_would_drop(a, b):
    import seat_sync as S
    evil_merge(a)
    peer_push(b, "s.txt", "side\n")                            # both plain commits are upstream: only the merge is not
    peer_push(b, "m.txt", "main\n")
    sh(a, "fetch", "-q")
    try:
        S.plan(S.Git(a))
    except S.Refused as e:
        assert "NOT on origin/main" in str(e), e
        return
    raise AssertionError("plan accepted a merge whose change is on no other commit")


def t_carried_files_sharing_a_target_blob_keep_their_own_inodes(a, b):
    for n in ("p.txt", "q.txt"):
        peer_push(b, n, LINES)
    sh(a, "pull", "-q", "--rebase")
    up = LINES.replace("line 2", "ORIGIN 2")
    sh(b, "pull", "-q", "--rebase")
    for n in ("p.txt", "q.txt"):
        write(b, n, up)
    sh(b, "add", "p.txt", "q.txt")
    sh(b, "commit", "-q", "-m", "same blob", "--", "p.txt", "q.txt")
    sh(b, "push", "-q", "origin", "HEAD:main")
    write(a, "p.txt", LINES.replace("line 5", "PEER P"))
    write(a, "q.txt", LINES.replace("line 7", "PEER Q"))
    write(a, "h.txt", "mine\n")
    sha, log = quiet(P.publish, a, ["h.txt"], "mine")
    assert "WRITE LANDED" not in log, log
    assert "PEER P" in open(os.path.join(a, "p.txt")).read() and "ORIGIN 2" in open(os.path.join(a, "q.txt")).read()
    assert "PEER Q" in open(os.path.join(a, "q.txt")).read()


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
    # PUBLISH_EDGES_FIX_MODE_GLOB_DLL_RESET: upstream's hunk is taken back out, so it never reads as the peer's edit
    assert open(os.path.join(a, "f.txt")).read() == dirty, open(os.path.join(a, "f.txt")).read()
    assert "taken back out" in why, why
    sha = P_quiet_publish(a, [], None)                           # the re-run merges to the same result
    assert sha == sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main")
    assert open(os.path.join(a, "f.txt")).read() == LINES.replace("line 2", "ORIGIN 2").replace("line 9", "PEER 9")


def t_refused_reset_takes_shard_carry_back_out_keeping_later_appends(a, b):
    """PUBLISH_EDGES_FIX_MODE_GLOB_DLL_RESET: a refused move cuts upstream's lines out of a shard; an append made after
    the carry stays, and the inode never changes."""
    import seat_sync
    seed_shard(a, b)
    shard = SHARD
    peer_push(b, shard, open(os.path.join(b, shard)).read() + '{"up": 1}\n')
    append(a, shard, '{"mine": 1}\n')
    before = open(os.path.join(a, shard)).read()
    ino = os.stat(os.path.join(a, shard)).st_ino
    write(a, "h.txt", "mine\n")
    real = seat_sync.reset_keep
    def boom(*args, **kw):
        append(a, shard, '{"later": 1}\n')
        raise seat_sync.Refused("planted refusal")
    seat_sync.reset_keep = boom
    try:
        why = refused(P.publish, a, ["h.txt"], "mine")
    finally:
        seat_sync.reset_keep = real
    assert why and "taken back out" in why, why
    got = open(os.path.join(a, shard)).read()
    assert got == before + '{"later": 1}\n', got
    assert os.stat(os.path.join(a, shard)).st_ino == ino


def t_glob_named_path_commits_only_itself(a, b):
    """PUBLISH_EDGES_FIX_MODE_GLOB_DLL_RESET: `a[b].txt` is a path, not a pattern that also matches `ab.txt`."""
    write(a, "a[b].txt", "mine\n")
    write(a, "ab.txt", "a peer's untracked file\n")
    write(a, "f.txt", LINES.replace("line 1\n", "DIRTY 1\n"))
    write(a, "f*", "star\n")
    quiet(P.publish, a, ["a[b].txt", "f*"], "glob names")
    names = sorted(sh(a, "show", "--name-only", "--format=", "HEAD").split("\n"))
    assert names == ["a[b].txt", "f*"], names
    assert "ab.txt" not in sh(a, "ls-tree", "-r", "--name-only", "origin/main").split("\n")
    assert "DIRTY 1" not in show(a, "f.txt")
    staged = sh(a, "diff", "--cached", "--name-only")
    assert staged == "", "a glob name staged other paths: %r" % staged
    assert sh(a, "status", "--porcelain", "--", ":(literal)ab.txt") == "?? ab.txt", "the peer's ab.txt was touched"
    assert "DIRTY 1" in open(os.path.join(a, "f.txt")).read(), "the peer's dirty f.txt was lost"


def t_hooks_keep_their_own_glob_pathspecs(a, b):
    """Literal pathspecs are publish's, never its hooks': a pre-commit/pre-push glob must still match (game_art.py
    globs `*.html`), or the guard silently sees nothing and passes."""
    hooks = os.path.join(os.path.dirname(a), "hooks")
    for h in ("pre-commit", "pre-push"):
        write(hooks, h, "#!/bin/sh\ntest -n \"$(git ls-files -- '*.txt')\" || { echo GLOB_BLIND >&2; exit 1; }\n")
        os.chmod(os.path.join(hooks, h), 0o755)
    sh(a, "config", "core.hooksPath", hooks)
    write(a, "h.txt", "mine\n")
    P.MAX_TRIES, old_tries = 1, P.MAX_TRIES
    try:
        sha = P_quiet_publish(a, ["h.txt"], "mine")
    finally:
        P.MAX_TRIES = old_tries
    assert sha == sh(a, "rev-parse", "origin/main")


def t_hook_refusal_stops_at_once_with_its_reason(a, b):
    """RIMMANDRAKE_STOP_RETRYING_A_PRE_PUSH_REFUSAL: a pre-push hook's `REFUSED` is a verdict, not a race. Retried, it
    cost three sleeps and showed only git's last line ("failed to push some refs"), never the hook's reason."""
    hooks = os.path.join(os.path.dirname(a), "hooks")
    count = os.path.join(os.path.dirname(a), "hook_runs")
    write(hooks, "pre-push", "#!/bin/sh\necho x >> '%s'\necho 'pre-push REFUSED (orphan item prose): X.md: no ledger"
          " row at all' >&2\nexit 1\n" % count)
    os.chmod(os.path.join(hooks, "pre-push"), 0o755)
    sh(a, "config", "core.hooksPath", hooks)
    write(a, "h.txt", "mine\n")
    P.MAX_TRIES, old_tries = 3, P.MAX_TRIES
    try:
        try:
            P_quiet_publish(a, ["h.txt"], "mine")
            raise AssertionError("a refusing hook published")
        except P.Refuse as e:
            got = str(e)
    finally:
        P.MAX_TRIES = old_tries
    runs = len(open(count).read().split())
    assert runs == 1, "the refusing hook ran %d times" % runs
    assert "no ledger row at all" in got, "the refusal lost the hook's reason: %r" % got


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


ADDED = "conversations/2026-11-17-2328-2c2a405a.md"


def t_untracked_copy_identical_to_origins_does_not_stop_the_move(a, b):
    """RIMMANDRAKE_UNBLOCK_PUBLISH_UNTRACKED_FILE_EQUALS_ORIGIN_COPY. ./publish refused twice on 2026-11-17 with
    'Untracked working tree file ... would be overwritten' when another lander had already pushed a byte-identical
    copy (22215 bytes both ways). An identical untracked file carries nothing of ours: it is parked, not a blocker."""
    peer_push(b, ADDED, "landed by the other seat\n")
    write(a, ADDED, "landed by the other seat\n")               # untracked here, identical to origin's blob
    write(a, "f.txt", LINES.replace("line 4", "LINE 4"))
    sha = P_quiet_publish(a, ["f.txt"], "mine")
    assert sha == sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main")   # the clone moved too
    assert open(os.path.join(a, ADDED)).read() == "landed by the other seat\n"     # and the file is still there
    assert show(a, ADDED) == "landed by the other seat\n"
    gd = sh(a, "rev-parse", "--absolute-git-dir")
    import seat_sync as S
    assert not [n for n in os.listdir(gd) if n.startswith(S.ADDED_PARK)], "a park was left behind after success"


def t_a_file_held_open_keeps_its_park(a, b):
    """RIMMANDRAKE_GUARD_PARK_DROP_AGAINST_LATE_FD_SAVE: an identical untracked file is parked, the move writes upstream's
    copy at the path, and the park was deleted once the bytes matched; a writer still holding the parked file open then
    saved into a file with no name left. A park is kept while any process holds one of its files open, and named."""
    import glob
    import seat_sync as S
    peer_push(b, ADDED, "landed by the other seat\n")
    write(a, ADDED, "landed by the other seat\n")
    fd = os.open(os.path.join(a, ADDED), os.O_WRONLY | os.O_APPEND)     # an editor holds it open across the publish
    try:
        write(a, "f.txt", LINES.replace("line 4", "LINE 4"))
        sha, log = quiet(P.publish, a, ["f.txt"], "mine")
        os.write(fd, b"LATE\n")
    finally:
        os.close(fd)
    kept = glob.glob(os.path.join(sh(a, "rev-parse", "--absolute-git-dir"), S.ADDED_PARK + "-*", ADDED))
    assert kept and "LATE" in open(kept[0]).read(), "the save through the open file had no name left (%s)" % kept
    assert os.path.dirname(os.path.dirname(kept[0])) in log or S.ADDED_PARK in log, log


def t_a_different_untracked_file_is_refused_by_name_never_lost(a, b):
    """The other half of the same rule: untracked content that is NOT origin's is somebody's unsaved work. The
    refusal NAMES the path (the old one named only git's first collision) and the file is never overwritten."""
    peer_push(b, ADDED, "origin's version\n")
    write(a, ADDED, "MY UNSAVED DRAFT\n")
    write(a, "f.txt", LINES.replace("line 4", "LINE 4"))
    head0 = sh(a, "rev-parse", "HEAD")
    why = refused(P.publish, a, ["f.txt"], "mine")
    assert why and ADDED in why and "DIFFERENT" in why, why
    assert open(os.path.join(a, ADDED)).read() == "MY UNSAVED DRAFT\n"   # the draft is untouched
    assert sh(a, "log", "-1", "--format=%s") == "mine" and sh(a, "rev-parse", "HEAD^") == head0   # commit intact
    assert not sh(a, "stash", "list")


def t_an_unhashable_untracked_path_is_refused_not_called_identical(a, b):
    """'Could not look' is not 'equal': a symlink (or a directory) where the move adds a file cannot be hashed, so
    it must be refused by name rather than parked as if it held origin's bytes."""
    peer_push(b, ADDED, "origin's version\n")
    os.makedirs(os.path.dirname(os.path.join(a, ADDED)), exist_ok=True)
    os.symlink("/etc/hosts", os.path.join(a, ADDED))
    write(a, "f.txt", LINES.replace("line 4", "LINE 4"))
    why = refused(P.publish, a, ["f.txt"], "mine")
    assert why and ADDED in why and "cannot be hashed" in why, why
    assert os.path.islink(os.path.join(a, ADDED)), "the symlink was replaced"


def t_a_refused_move_puts_the_parked_identical_copy_back(a, b):
    """The park is inside .git and is deleted only once every file is back. If the reset refuses AFTER the park, the
    file must be at its path again, not stranded in .git."""
    import seat_sync as S
    peer_push(b, ADDED, "origin's version\n")
    write(a, ADDED, "origin's version\n")
    write(a, "f.txt", LINES.replace("line 4", "LINE 4"))
    real = S._reset_keep_moved
    gd = sh(a, "rev-parse", "--absolute-git-dir")
    seen = []

    def boom(*args, **kw):          # record that the park really happened before the refusal: else this proves nothing
        seen.append((os.path.lexists(os.path.join(a, ADDED)),
                     [n for n in os.listdir(gd) if n.startswith(S.ADDED_PARK)
                      and os.path.isfile(os.path.join(gd, n, ADDED))]))
        raise S.Refused("planted: the reset refused after the park")
    S._reset_keep_moved = boom
    try:
        why = refused(P.publish, a, ["f.txt"], "mine")
    finally:
        S._reset_keep_moved = real
    assert why and "planted" in why, why
    assert seen and seen[0][0] is False and seen[0][1], f"the file was never parked before the refusal: {seen}"
    assert open(os.path.join(a, ADDED)).read() == "origin's version\n", "the parked copy did not come back"
    assert not [n for n in os.listdir(gd) if n.startswith(S.ADDED_PARK)], "the park outlived the refusal"


def _writer_in_the_gap(S, dst, text):
    """Patch Path.mkdir so a save lands at dst when the restore makes dst's parent: the step every restore (old
    check-then-rename and new) takes after any 'is it free?' check and before the move. -> the undo."""
    real = S.Path.mkdir

    def mkdir(self, *a, **kw):
        r = real(self, *a, **kw)
        if os.path.abspath(str(self)) == os.path.dirname(os.path.abspath(dst)) and not os.path.lexists(dst):
            with open(dst, "w") as f:
                f.write(text)
        return r
    S.Path.mkdir = mkdir
    return lambda: setattr(S.Path, "mkdir", real)


def t_a_restore_never_overwrites_a_save_landing_after_its_check(a, b):
    """RIMMANDRAKE_HARDEN_PUBLISH_PARK_RESTORE_RACE_CODEX_FOUND (1). A writer saves at the parked path between the
    restore's 'is it free?' check and the move back: that save is somebody's work and must survive; the parked copy
    stays in the park, which is kept."""
    import seat_sync as S
    write(a, ADDED, "origin's version\n")
    g = S.Git(a)
    park, moved = S._park_added(g, [ADDED])
    dst = os.path.join(a, ADDED)
    undo = _writer_in_the_gap(S, dst, "A SAVE MADE IN THE GAP\n")
    try:
        S._unpark_added(g, park, moved)
    finally:
        undo()
    assert open(dst).read() == "A SAVE MADE IN THE GAP\n", "the restore overwrote a save it did not park"
    assert open(os.path.join(park, ADDED)).read() == "origin's version\n", "the parked copy was lost"


def t_a_stop_tracking_restore_never_overwrites_a_save_in_the_gap(a, b):
    """The same race in the sibling park (files upstream stopped tracking, rm-untrack-keep-*), found by Codex on the fix:
    the reset refuses, and a save lands at the kept path before it is moved back."""
    import seat_sync as S
    write(a, "kept.txt", "ours, untracked upstream\n")
    sh(a, "add", "kept.txt")
    sh(a, "commit", "-q", "-m", "kept", "--", "kept.txt")
    g = S.Git(a)
    head = sh(a, "rev-parse", "HEAD")
    dst = os.path.join(a, "kept.txt")
    undo = _writer_in_the_gap(S, dst, "A SAVE MADE IN THE GAP\n")
    real_run = S.Git.run

    def run(self, *args, **kw):
        if args[:3] == ("reset", "-q", "--keep"):
            raise S.Refused("planted: the reset refused")
        return real_run(self, *args, **kw)
    S.Git.run = run
    try:
        why = None
        try:
            S._reset_keep_moved(g, head, head + "~1", ["kept.txt"])
        except S.Refused as e:
            why = str(e)
    finally:
        S.Git.run = real_run
        undo()
    assert why and "planted" in why, why
    assert open(dst).read() == "A SAVE MADE IN THE GAP\n", "the restore overwrote a save it did not park"
    gd = sh(a, "rev-parse", "--absolute-git-dir")
    kept = [os.path.join(gd, n, "kept.txt") for n in os.listdir(gd) if n.startswith("rm-untrack-keep")]
    assert kept and open(kept[0]).read() == "ours, untracked upstream\n", f"the kept copy was lost: {kept}"


def t_a_park_dir_that_cannot_be_made_is_a_refusal(a, b):
    """Codex on the fix: making the park dir raised a bare OSError (ENOSPC), which skipped every caller's Refused
    rollback. It must be a Refused."""
    import seat_sync as S
    real = S.Path.mkdir

    def full(self, *a, **kw):
        if S.ADDED_PARK in str(self):
            raise OSError(28, "No space left on device")
        return real(self, *a, **kw)
    write(a, ADDED, "origin's version\n")
    S.Path.mkdir = full
    try:
        S._park_added(S.Git(a), [ADDED])
        raised = None
    except S.Refused as e:
        raised = "Refused"
    except OSError as e:
        raised = "OSError %s" % e
    finally:
        S.Path.mkdir = real
    assert raised == "Refused", raised
    assert open(os.path.join(a, ADDED)).read() == "origin's version\n", "the file left its path"


def t_two_parks_in_one_second_never_share_a_dir(a, b):
    """RIMMANDRAKE_HARDEN_PUBLISH_PARK_RESTORE_RACE_CODEX_FOUND (2). A retained park (a copy that could not come
    back) is the only copy left: a second park in the same process and second must not reuse its dir."""
    import seat_sync as S
    g = S.Git(a)
    real = S.time.strftime
    S.time.strftime = lambda fmt, *t: "20261118_180000"
    real_rand, draws = S.os.urandom, iter([b"\0\0\0", b"\0\0\0", b"\1\1\1"])
    S.os.urandom = lambda n: next(draws, None) or real_rand(n)     # the second park draws the first's name once
    try:
        write(a, ADDED, "first\n")
        p1, _ = S._park_added(g, [ADDED])
        write(a, ADDED, "second\n")
        p2, _ = S._park_added(g, [ADDED])
    finally:
        S.time.strftime = real
        S.os.urandom = real_rand
    assert p1 != p2, f"two parks share {p1}"
    assert open(os.path.join(p1, ADDED)).read() == "first\n", "the second park overwrote the retained first"
    assert open(os.path.join(p2, ADDED)).read() == "second\n"


def _with_env(**kv):
    old = {k: os.environ.get(k) for k in kv}
    os.environ.update(kv)

    def undo():
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return undo


def t_a_skipped_door_leaves_its_reason_on_the_landed_commit(a, b):
    """RIMMANDRAKE_RECORD_DOOR_SKIP_FOUR_LANDINGS_LEFT_NO_TRACE. A skip only printed a line, so which landings skipped
    the door could not be read afterwards. The reason now rides on the landed commit as a trailer, for both skips."""
    write(a, "f.txt", LINES.replace("line 4", "LINE 4"))
    undo = _with_env(RM_PUBLISH_SKIP_PIPELINE_CHECKS="selftest: pipeline door known red on base",
                     RM_PUBLISH_SKIP_TREE_CHECKS="selftest: tree door known red on base")
    try:
        sha = P_quiet_publish(a, ["f.txt"], "mine")
    finally:
        undo()
    body = sh(a, "log", "-1", "--format=%B", sha)
    trailers = sh(a, "log", "-1", "--format=%(trailers:key=Door-skipped,valueonly)", sha)
    assert sha == sh(a, "rev-parse", "origin/main"), "it did not land"
    assert "RM_PUBLISH_SKIP_PIPELINE_CHECKS: selftest: pipeline door known red on base" in trailers, body
    assert "RM_PUBLISH_SKIP_TREE_CHECKS: selftest: tree door known red on base" in trailers, body


def t_a_skip_with_no_commit_of_its_own_is_refused(a, b):
    """The other half: a skip whose landing makes no commit of its own (no paths, or nothing changed in them) has no
    commit to carry its reason, so it is refused before anything moves."""
    write(a, "f.txt", LINES.replace("line 4", "LINE 4"))
    sh(a, "add", "f.txt")
    sh(a, "commit", "-q", "-m", "by hand", "--", "f.txt")
    tip = sh(a, "rev-parse", "origin/main")
    undo = _with_env(RM_PUBLISH_SKIP_PIPELINE_CHECKS="selftest: no paths named")
    try:
        why = refused(P.publish, a, [], None)
    finally:
        undo()
    assert why and "RM_PUBLISH_SKIP_PIPELINE_CHECKS" in why, why
    assert sh(a, "rev-parse", "origin/main") == tip, "it landed anyway"


def t_both_skip_reasons_survive_a_replace_trailer_config(a, b):
    """Codex on the fix: with trailer.ifexists=replace in git config, the second Door-skipped trailer replaced the
    first, so one skip's reason was lost."""
    sh(a, "config", "trailer.ifexists", "replace")
    write(a, "f.txt", LINES.replace("line 4", "LINE 4"))
    undo = _with_env(RM_PUBLISH_SKIP_PIPELINE_CHECKS="pipeline why", RM_PUBLISH_SKIP_TREE_CHECKS="tree why")
    try:
        sha = P_quiet_publish(a, ["f.txt"], "mine")
    finally:
        undo()
    trailers = sh(a, "log", "-1", "--format=%(trailers:key=Door-skipped,valueonly)", sha)
    assert "pipeline why" in trailers and "tree why" in trailers, trailers


def t_a_skip_never_carries_an_earlier_local_commit_past_the_door(a, b):
    """Codex on the fix: a skip whose run also lands an earlier local commit could push that commit with no record
    (e.g. this run's own commit dropped in the replay as already upstream). A skip lands only this run's commit."""
    write(a, "g.txt", "an earlier commit\n")
    sh(a, "add", "g.txt")
    sh(a, "commit", "-q", "-m", "earlier, by hand", "--", "g.txt")
    write(a, "f.txt", LINES.replace("line 4", "LINE 4"))
    tip = sh(a, "rev-parse", "origin/main")
    undo = _with_env(RM_PUBLISH_SKIP_PIPELINE_CHECKS="selftest: two commits")
    try:
        why = refused(P.publish, a, ["f.txt"], "mine")
    finally:
        undo()
    assert why and "earlier" in why, why
    assert sh(a, "rev-parse", "origin/main") == tip, "it landed anyway"
    assert sh(a, "log", "-1", "--format=%s") == "earlier, by hand", "this run's commit was not undone"
    assert open(os.path.join(a, "f.txt")).read() == LINES.replace("line 4", "LINE 4"), "the file was lost"


def t_a_skip_reads_a_fresh_origin_not_a_stale_tracking_ref(a, b):
    """Codex round 2: the earlier-commit guard read the local origin/main before any fetch. A commit already pushed
    from here, with the tracking ref stale, read as unpublished and a valid skip landing was refused."""
    o = sh(a, "rev-parse", "origin/main")
    write(a, "g.txt", "already pushed\n")
    sh(a, "add", "g.txt")
    sh(a, "commit", "-q", "-m", "pushed by plain git", "--", "g.txt")
    sh(a, "push", "-q", "origin", "HEAD:main")
    sh(a, "update-ref", "refs/remotes/origin/main", o)          # the tracking ref is stale
    write(a, "f.txt", LINES.replace("line 4", "LINE 4"))
    undo = _with_env(RM_PUBLISH_SKIP_PIPELINE_CHECKS="selftest: stale ref")
    try:
        sha = P_quiet_publish(a, ["f.txt"], "mine")
    finally:
        undo()
    assert sh(a, "log", "-1", "--format=%(trailers:key=Door-skipped,valueonly)", sha), "no trailer"


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


def t_dll_rebuild_never_overwrites_a_save_made_during_the_build(a, b):
    """PUBLISH_EDGES_FIX_MODE_GLOB_DLL_RESET: the dirty check runs before a build of minutes; a save to the DLL pair
    landing during it is kept, nothing is installed over it, and the landing refuses naming the path."""
    seed_mod(a, b)
    hooks = os.path.join(os.path.dirname(a), "hooks")
    write(hooks, "pre-push", HOOK)
    os.chmod(os.path.join(hooks, "pre-push"), 0o755)
    sh(a, "config", "core.hooksPath", hooks)
    write(a, MOD + "/Source/B.cs", "class B { int changed; }\n")
    calls = []
    inner = mock_winbuild(calls)
    def wb(scratch, csproj):
        write(a, DLL + ".srchash", "A PEER'S SAVE DURING THE BUILD\n")
        return inner(scratch, csproj)
    real, P.winbuild = getattr(P, "winbuild", None), wb
    P.MAX_TRIES, old_tries = 2, P.MAX_TRIES
    dll_before = open(os.path.join(a, DLL)).read()
    try:
        why = refused(P.publish, a, [MOD + "/Source/B.cs"], "source only")
    finally:
        P.winbuild, P.MAX_TRIES = real, old_tries
    assert calls and why and "while the DLL rebuilt" in why and DLL + ".srchash" in why, why
    assert open(os.path.join(a, DLL + ".srchash")).read() == "A PEER'S SAVE DURING THE BUILD\n"
    assert open(os.path.join(a, DLL)).read() == dll_before            # the DLL swapped first went back
    assert not [n for n in os.listdir(os.path.join(a, MOD, "Assemblies")) if n.endswith(".publish-tmp")]


def rollback_world(a, absent=False):
    """A clone whose HEAD holds X (or not, when `absent`) and Y, a scratch build of both, and Y saved over in the
    worktree so install_pairs installs X and then refuses on Y: the rollback path runs on X."""
    if not absent:
        write(a, "X.bin", "X AT HEAD\n")
    write(a, "Y.bin", "Y AT HEAD\n")
    sh(a, "add", "--", *(["Y.bin"] if absent else ["X.bin", "Y.bin"]))
    sh(a, "commit", "-qm", "seed rollback")
    scratch = tempfile.mkdtemp(dir=os.path.dirname(a))
    write(scratch, "X.bin", "X REBUILT\n")
    write(scratch, "Y.bin", "Y REBUILT\n")
    write(a, "Y.bin", "Y SAVED BY A PEER\n")
    return sh(a, "rev-parse", "HEAD"), scratch


def side_files(a):
    return sorted(n for n in os.listdir(a) if ".publish-" in n)


def t_refused_publish_keeps_a_peer_commit_made_during_the_checks(a, b):
    """RIMMANDRAKE_GUARD_PUBLISH_ROLLBACK_AGAINST_PEER_COMMIT: the publish lock does not cover a plain `git commit`, and
    a red door undid this run's commit with a bare `reset --soft <made>~1`, taking a peer's commit made on top of it
    during the checks off the branch too. A refused publish never removes a commit it did not make."""
    real = P.tree_checks

    def peer_commits_then_red(top, changed, gate=None):
        write(a, "peer.txt", "peer\n")
        sh(a, "add", "peer.txt")
        sh(a, "commit", "-q", "-m", "peer, by hand")
        raise P.Refuse("planted red door")
    P.tree_checks = peer_commits_then_red
    try:
        write(a, "mine.txt", "mine\n")
        why = refused(P.publish, a, ["mine.txt"], "mine")
    finally:
        P.tree_checks = real
    assert why and "planted red door" in why, why
    assert sh(a, "log", "-1", "--format=%s") == "peer, by hand", "the peer's commit was taken off the branch"
    assert "HEAD moved" in why, "the refusal does not say it left HEAD alone: %s" % why


def t_rollback_keeps_a_save_landing_before_the_undo_swap(a, b):
    """PUBLISH_ROLLBACK_FIX_RACE_STILL_AJAR: rollback compared read(dst)==new, then swapped HEAD's bytes back; a peer
    save in that gap went into the tmp and the cleanup deleted it. It must survive in the worktree."""
    import seat_sync as S
    head, scratch = rollback_world(a)
    real, n = S._exchange, []
    def gap(x, y):
        n.append(1)
        if len(n) == 2:                                  # the rollback's swap: a peer saves X just before it
            write(a, "X.bin", "X SAVED IN THE UNDO GAP\n")
        real(x, y)
    S._exchange = gap
    try:
        why = refused(P.install_pairs, a, head, scratch, ["X.bin", "Y.bin"])
    finally:
        S._exchange = real
    assert why and "Y.bin" in why, why
    assert open(os.path.join(a, "X.bin")).read() == "X SAVED IN THE UNDO GAP\n"
    assert open(os.path.join(a, "Y.bin")).read() == "Y SAVED BY A PEER\n"
    assert not side_files(a), side_files(a)


def t_rollback_restores_head_when_nobody_saved(a, b):
    """The plain rollback still puts HEAD's bytes back and leaves no side file."""
    head, scratch = rollback_world(a)
    why = refused(P.install_pairs, a, head, scratch, ["X.bin", "Y.bin"])
    assert why and "Y.bin" in why, why
    assert open(os.path.join(a, "X.bin")).read() == "X AT HEAD\n"
    assert not side_files(a), side_files(a)


def t_rollback_of_a_new_file_keeps_a_save_landing_before_the_undo(a, b):
    """PUBLISH_ROLLBACK_FIX_RACE_STILL_AJAR: a file absent at HEAD was unlinked after the compare; a peer save in the
    gap was deleted. It must survive in the worktree; with no save, the file goes."""
    head, scratch = rollback_world(a, absent=True)
    real = os.rename
    def gap(x, y, *k, **kw):
        if os.path.basename(str(x)) == "X.bin":
            write(a, "X.bin", "X SAVED IN THE UNDO GAP\n")
        return real(x, y, *k, **kw)
    real_unlink = os.unlink
    def unlink_gap(x, *k, **kw):                         # the old code's blind unlink: same gap, same save
        if os.path.basename(str(x)) == "X.bin":
            write(a, "X.bin", "X SAVED IN THE UNDO GAP\n")
        return real_unlink(x, *k, **kw)
    os.rename, os.unlink = gap, unlink_gap
    try:
        why = refused(P.install_pairs, a, head, scratch, ["X.bin", "Y.bin"])
    finally:
        os.rename, os.unlink = real, real_unlink
    assert why and "Y.bin" in why, why
    assert open(os.path.join(a, "X.bin")).read() == "X SAVED IN THE UNDO GAP\n"
    assert not side_files(a), side_files(a)
    head2, scratch2 = head, scratch
    os.unlink(os.path.join(a, "X.bin"))
    why = refused(P.install_pairs, a, head2, scratch2, ["X.bin", "Y.bin"])
    assert why and not os.path.exists(os.path.join(a, "X.bin")) and not side_files(a), (why, side_files(a))


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


# RIMMANDRAKE_RETRY_PUBLISH_ON_INDEX_LOCK_FAILED_TWICE_RUNNING: 2026-11-18 7:28 PM and 8:00 PM PST, ./publish in the
# Conductor's clone exited 2 on "Unable to create .git/index.lock: File exists" while another process held the index.
PROBE = ("import os,sys,time;p=sys.argv[1];fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY);print('held',flush=True);"
         "time.sleep(float(sys.argv[2]));os.close(fd);os.unlink(p)")


def hold_index(a, seconds):
    lock = os.path.join(a, ".git", "index.lock")
    pr = subprocess.Popen([sys.executable, "-c", PROBE, lock, str(seconds)], stdout=subprocess.PIPE, text=True)
    assert pr.stdout.readline().strip() == "held"
    return pr, lock


def t_index_lock_held_five_seconds_lands_on_its_own(a, b):
    write(a, "f.txt", LINES.replace("line 4", "LINE 4"))
    pr, lock = hold_index(a, 5)
    try:
        sha, log = quiet(P.publish, a, ["f.txt"], "mine, under a held lock")
    finally:
        pr.kill()
        pr.wait()
        if os.path.exists(lock):
            os.unlink(lock)
    assert sha and "LINE 4" in show(a, "f.txt"), log


def t_index_lock_held_long_exits_its_own_code_naming_the_holder(a, b):
    write(a, "f.txt", LINES.replace("line 6", "LINE 6"))
    pr, lock = hold_index(a, 120)
    try:
        r = subprocess.run([sys.executable, os.path.abspath(P.__file__), "-m", "mine, lock never freed", "f.txt"], cwd=a,
                           capture_output=True, text=True, timeout=120,
                           env=dict(os.environ, PUBLISH_INDEX_LOCK_WAIT="2"))
    finally:
        pr.kill()
        pr.wait()
        if os.path.exists(lock):
            os.unlink(lock)
    text = r.stdout + r.stderr
    assert r.returncode == P.LOCK_HELD_EXIT and r.returncode not in (0, 2), (r.returncode, text)
    assert "index.lock" in text and str(pr.pid) in text and "python" in text, text
    assert "LINE 6" not in show(a, "f.txt"), "nothing was published"

LSHARD = P.LEDGER_SHARDS + "S.jsonl"


def seed_ledger(a, b, text="seed\n"):
    write(a, ".gitattributes", P.LEDGER_SHARDS + "*.jsonl merge=union\n")
    write(a, LSHARD, text)
    P_quiet_publish(a, [".gitattributes", LSHARD], "shard")
    sh(b, "pull", "-q", "--rebase")


def ledger(a, paths):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        sha = P.publish(a, paths, "ledger", ledger=True)
    return sha, buf.getvalue()


def t_a_ledger_landing_waits_for_no_peer_publish_and_takes_no_peer_commit(a, b):
    # boundary design/specs/2026-11-22-ledger-write-lands-its-shard: the launch gate waited up to 600 s on a peer's
    # publish lock and was refused by a red test of a peer's unpublished commit (2026-11-21 to 11-23)
    seed_ledger(a, b)
    write(a, "f.txt", LINES.replace("line 3", "PEER LINE 3"))
    sh(a, "commit", "-q", "-m", "a peer's unpublished work", "--", "f.txt")
    peers = sh(a, "rev-parse", "HEAD")
    append(a, LSHARD, "mine\n")
    old, P.LOCK_TIMEOUT = P.LOCK_TIMEOUT, 1
    try:
        with P.clone_lock(a):
            sha, log = ledger(a, [LSHARD])
    finally:
        P.LOCK_TIMEOUT = old
    assert sha and "PUBLISHED " + sha in log, log
    assert show(a, LSHARD) == "seed\nmine\n"
    assert "PEER" not in show(a, "f.txt"), "a peer's commit rode along"
    assert sh(a, "rev-parse", "HEAD") == peers, "a held clone's branch moved"
    # the peer's own publish afterwards lands its commit and doubles no ledger line
    P_quiet_publish(a, [], None)
    assert "PEER LINE 3" in show(a, "f.txt") and show(a, LSHARD) == "seed\nmine\n", show(a, LSHARD)


def t_a_ledger_landing_levels_a_free_clone(a, b):
    seed_ledger(a, b)
    peer_push(b, LSHARD, "seed\npeer\n")
    append(a, LSHARD, "mine\n")
    sha, log = ledger(a, [LSHARD])
    assert sha == sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main"), log
    assert show(a, LSHARD) == "seed\npeer\nmine\n" and not sh(a, "status", "--porcelain")


def t_a_ledger_landing_that_loses_a_push_race_keeps_both_lines(a, b):
    seed_ledger(a, b)
    append(a, LSHARD, "mine\n")

    def race(attempt):
        if attempt == 0:
            peer_push(b, LSHARD, "seed\npeer\n")
    P.before_push = race
    try:
        sha, log = ledger(a, [LSHARD])
    finally:
        P.before_push = None
    assert sha and show(a, LSHARD) == "seed\npeer\nmine\n", show(a, LSHARD)


def t_a_ledger_landing_whose_lines_another_landing_carried_says_published(a, b):
    # two writers in one clone's shard: the first landing carries both lines. The second was told "nothing to publish" and
    # its rimflow write exited 4, WRITTEN NOT PUBLISHED, for a line that is on origin
    seed_ledger(a, b)
    append(a, LSHARD, "first\nsecond\n")
    one, _log = ledger(a, [LSHARD])
    two, log = ledger(a, [LSHARD])
    assert two == one and "PUBLISHED " + one in log, (one, two, log)
    # the same in a held clone, which waits for no peer
    append(a, LSHARD, "third\n")
    old, P.LOCK_TIMEOUT = P.LOCK_TIMEOUT, 1
    try:
        with P.clone_lock(a):
            three, _log = ledger(a, [LSHARD])
            four, log = ledger(a, [LSHARD])
    finally:
        P.LOCK_TIMEOUT = old
    assert four == three and "PUBLISHED " + three in log, log
    # a line taken out of the shard here is no append: the ordinary route commits it
    write(a, LSHARD, "seed\nsecond\n")
    assert P.land_ledger(a, [LSHARD], "x\n") is None


def t_a_ledger_landing_never_puts_back_a_line_origin_removed(a, b):
    seed_ledger(a, b, "seed\nbad\n")
    peer_push(b, LSHARD, "seed\n")
    append(a, LSHARD, "mine\n")
    ledger(a, [LSHARD])
    assert "bad" not in show(a, LSHARD) and "mine" in show(a, LSHARD), show(a, LSHARD)


def t_a_ledger_landing_of_a_torn_line_or_with_no_origin_takes_the_ordinary_route(a, b):
    seed_ledger(a, b)
    append(a, LSHARD, "whole\nhalf a li")
    assert P.land_ledger(a, [LSHARD], "x\n") is None and show(a, LSHARD) == "seed\n"
    append(a, LSHARD, "ne\n")
    url = sh(a, "remote", "get-url", "origin")
    sh(a, "remote", "set-url", "origin", url + "-gone")
    assert P.land_ledger(a, [LSHARD], "x\n") is None
    sh(a, "remote", "set-url", "origin", url)
    assert P.land_ledger(a, [LSHARD], "x\n") and show(a, LSHARD) == "seed\nwhole\nhalf a line\n"


def t_a_ledger_landing_of_another_path_goes_the_ordinary_way(a, b):
    seed_ledger(a, b)
    append(a, LSHARD, "mine\n")
    write(a, "g.txt", "prose\n")
    sha, log = ledger(a, [LSHARD, "g.txt"])
    assert sha == sh(a, "rev-parse", "HEAD") and show(a, "g.txt") == "prose\n" and "mine" in show(a, LSHARD), log


def t_a_ledger_landing_refused_by_the_hook_says_so_and_lands_nothing(a, b):
    seed_ledger(a, b)
    append(a, LSHARD, "mine\n")
    hook = os.path.join(sh(a, "rev-parse", "--absolute-git-dir"), "hooks", "pre-push")
    os.makedirs(os.path.dirname(hook), exist_ok=True)
    with open(hook, "w") as f:
        f.write("#!/bin/sh\necho 'pre-push REFUSED: planted' >&2\nexit 1\n")
    os.chmod(hook, 0o755)
    try:
        ledger(a, [LSHARD])
        raise AssertionError("a hook refusal must raise")
    except P.Refuse as e:
        assert "planted" in str(e), e
    assert show(a, LSHARD) == "seed\n"


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
