#!/usr/bin/env python3
# selftest-timeout: 530
"""Selftest for scratch_reap.py, the expiry that nobody has to run by hand.

The planted cases are the brief's (SCRATCH_CLONES_BUILD_EXPIRY_NO_ONE_TIDIES): a live session, borrowed alternates, an
unpushed commit, a dirty tree, a young dir, an unreadable state; plus a protected path, a canonical save, a blind spot
that must hold everything, a clone whose lender is gone, a bad archive root, and the alarm and record paths.
A path is deleted only if nothing in it is unique, or after its work was bundled and restored and logged."""
import json
import os
import subprocess
import sys
import errno
import fcntl
import shutil
import socket
import tarfile
import tempfile
import time
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scratch_reap as R  # noqa: E402

R.CTIME_COUNTS = False                                  # age() can only reach mtimes; third_review_cases turns it back on

FAILS = []
OLD = 3 * 86400
UUID_OK = "11111111-2222-3333-4444-555555555555"
UUID_MIX = "99999999-8888-7777-6666-555555555555"
UUID_LIVEP = "aaaaaaaa-2222-3333-4444-555555555555"
UUID_LIVET = "bbbbbbbb-2222-3333-4444-555555555555"
UUID_SUB = "cccccccc-2222-3333-4444-555555555555"
UUID_LOOSE = "dddddddd-2222-3333-4444-555555555555"
UUID_YOUNG = "eeeeeeee-2222-3333-4444-555555555555"


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def git(cwd, *a):
    return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, check=True).stdout.strip()


def age(d: Path, secs=OLD):
    stamp = time.time() - secs
    for dp, dns, fns in os.walk(d):
        for n in dns + fns:
            os.utime(os.path.join(dp, n), (stamp, stamp), follow_symlinks=False)
    os.utime(d, (stamp, stamp))


def clone(origin, dest):
    subprocess.run(["git", "clone", "-q", str(origin), str(dest)], check=True, capture_output=True)
    return Path(dest)


def commit(c: Path, name: str, msg: str):
    (c / name).write_text(msg + "\n")
    git(c, "add", "--", name)
    git(c, "commit", "-q", "-m", msg)


def dated(c: Path, name: str, text: str, msg: str, when: str, committed: str | None = None):
    (c / name).write_text(text + "\n")
    git(c, "add", "--", name)
    env = dict(os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=committed or when)
    subprocess.run(["git", "-C", str(c), "commit", "-q", "-m", msg], check=True, capture_output=True, env=env)


def run_reaper(*args):
    from io import StringIO
    import contextlib
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        rc = R.main(["--json", *args])
    return rc, {Path(r["path"]).name: r for r in json.loads(buf.getvalue())}


def acts(archive: Path) -> list[dict]:
    f = archive / "acts.jsonl"
    return [json.loads(ln) for ln in f.read_text().splitlines()] if f.exists() else []


def bundle_of(rows, name):
    return Path(rows[name]["archive"]) / "clone.bundle"


def sleeper(cwd: Path, env=None) -> subprocess.Popen:
    return subprocess.Popen(["sleep", "300"], cwd=cwd, env=env)


def sessions_root(root):
    return root / "BENCH" / "claude-1000" / "-proj"


def main() -> int:
    """One at a time: a run plants an undumpable process, and the /proc scan of a run beside it rightly holds everything."""
    if os.environ.get("SCRATCH_REAP_SELFTEST_ONCE"):      # the parent below holds the lock: taking it here would deadlock
        return run()
    lock = open(Path(tempfile.gettempdir()) / "selftest_scratch_reap.lock", "w")
    fcntl.flock(lock, fcntl.LOCK_EX)
    # A stranger's unreadable pid on a busy machine rightly holds every fixture (Live.blind): one bad attempt says nothing,
    # three in a row say the code. Fresh processes: an attempt that died leaves no patched module behind.
    for attempt in range(1, 4):
        rc = subprocess.run([sys.executable, __file__], env={**os.environ, "SCRATCH_REAP_SELFTEST_ONCE": "1"}).returncode
        if rc == 0:
            break
        print(f"RETRY: attempt {attempt} failed", flush=True)
    tags = subprocess.run([sys.executable, str(Path(__file__).with_name("selftest_scratch_reap_archive_tags.py"))])
    return rc or tags.returncode            # apart because that one stubs the live-process gate this one proves


def run() -> int:
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds)
        for k, v in {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                     "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"}.items():
            os.environ[k] = v
        origin = td / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
        seed = clone(origin, td / "seed")
        commit(seed, "a.txt", "a")
        git(seed, "push", "-q", "origin", "HEAD:main")

        root = td / "scratch"
        seat = root / "FOUNDRY"
        seat.mkdir(parents=True)
        corpus = td / "seatclone"
        (corpus / "infrastructure/state/ledger/events").mkdir(parents=True)
        (corpus / "infrastructure/state/items/closed").mkdir(parents=True)
        (corpus / "infrastructure/state/handoffs").mkdir(parents=True)
        (corpus / "infrastructure/state/canon.yml").write_text("start_savegame: Canon_Named_Save.rws\n")
        archive = td / "archive"
        archive.mkdir()
        transcripts = td / "transcripts"
        (transcripts / "-proj").mkdir(parents=True)
        prot = td / "protected_seat_clone"
        os.environ.update(SCRATCH_REAP_ROOTS=str(root), SCRATCH_REAP_CORPUS=str(corpus),
                          SCRATCH_REAP_STATE=str(td / "state"), SCRATCH_REAP_TTL_HOURS="24",
                          SCRATCH_REAP_MIRRORS=str(origin), SCRATCH_REAP_TRANSCRIPTS=str(transcripts),
                          SCRATCH_REAP_SCAN=os.pathsep.join([str(root), str(td / "live_elsewhere")]),
                          SCRATCH_REAP_PROTECTED=str(seat / "seat_clone_held"),
                          LEFTOVERS_ARCHIVE_ROOT=str(archive))
        (td / "live_elsewhere").mkdir()
        procs = []

        # a commit rewritten on main, an amended one, and saves the repo itself tracks
        writer = clone(origin, td / "writer")
        rewritten = clone(origin, seat / "rewritten_history_clone")
        amended = clone(origin, seat / "amended_after_push_clone")
        same = clone(origin, seat / "rewritten_same_content_clone")
        dated(writer, "twin.txt", "on main", "Same work", "2026-01-01T00:00:00Z")
        dated(rewritten, "twin.txt", "before the rewrite", "Same work", "2026-01-01T00:00:00Z")
        dated(amended, "twin.txt", "amended here", "Same work", "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z")
        commit(writer, "gap.txt", "main moved on, so the same commit below has another parent")
        dated(writer, "twin2.txt", "same", "Same again", "2026-01-03T00:00:00Z")
        dated(same, "twin2.txt", "same", "Same again", "2026-01-03T00:00:00Z")
        commit(writer, "CANONICAL_Tracked.rws", "the repo tracks this save")
        git(writer, "push", "-q", "origin", "HEAD:main")
        (corpus / "CANONICAL_Tracked.rws").write_text("save")
        tracked = clone(origin, seat / "tracked_canon_clone")
        commit(clone(origin, seat / "tracked_canon_gone_clone"), "CANONICAL_Dropped.rws", "a save no seat clone has")
        changed = clone(origin, seat / "tracked_canon_changed_clone")
        (changed / "CANONICAL_Tracked.rws").write_text("a run wrote over it")
        # the plain cases
        clean = clone(origin, seat / "clean_pushed_clone")
        unpushed = clone(origin, seat / "unpushed_clone")
        commit(unpushed, "b.txt", "only here")
        unpushed_sha = git(unpushed, "rev-parse", "HEAD")
        dirty = clone(origin, seat / "dirty_tracked_clone")
        (dirty / "a.txt").write_text("edited\n")
        untracked = clone(origin, seat / "untracked_file_clone")
        (untracked / "ITEM_PROSE.md").write_text("only copy\n")
        renamed = clone(origin, seat / "renamed_clone")
        git(renamed, "mv", "a.txt", "z.txt")
        (renamed / "with space \n.txt").write_text("odd name\n")
        stashed = clone(origin, seat / "stashed_clone")
        (stashed / "a.txt").write_text("stash me\n")
        git(stashed, "stash", "-q")
        reflogged = clone(origin, seat / "reflog_only_clone")
        commit(reflogged, "r.txt", "dropped from the branch")
        lost_sha = git(reflogged, "rev-parse", "HEAD")
        git(reflogged, "reset", "-q", "--hard", "HEAD~1")
        oddref = clone(origin, seat / "odd_ref_clone")
        commit(oddref, "w.txt", "wip")
        git(oddref, "update-ref", "refs/wip/keep", "HEAD")
        git(oddref, "reset", "-q", "--hard", "HEAD~1")
        oddref_sha = git(oddref, "rev-parse", "refs/wip/keep")
        noremote = seat / "no_remote_clone"
        noremote.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main", str(noremote)], check=True)
        commit(noremote, "n.txt", "only copy")
        localremote = clone(unpushed, seat / "local_remote_clone")   # its "remote" is one more scratch clone
        localremote_sha = git(localremote, "rev-parse", "HEAD")
        # a commit pushed by ANOTHER clone: this clone's origin/main ref is stale but the mirror proves it
        stale = clone(origin, seat / "stale_ref_clone")
        commit(stale, "s.txt", "pushed elsewhere")
        relay = clone(origin, td / "relay")
        git(relay, "fetch", "-q", str(stale), "main")
        git(relay, "merge", "-q", "--ff-only", "FETCH_HEAD")
        git(relay, "push", "-q", "origin", "HEAD:main")
        # alternates: a clone's objects are borrowed, by a clone inside the roots and by one outside them
        lender = clone(origin, seat / "lender_clone")
        borrower = seat / "borrower_clone"
        subprocess.run(["git", "clone", "-q", "--shared", str(lender), str(borrower)], check=True, capture_output=True)
        lender2 = clone(origin, seat / "lent_to_outside_clone")
        far = td / "live_elsewhere" / "far_borrower"
        subprocess.run(["git", "clone", "-q", "--shared", str(lender2), str(far)], check=True, capture_output=True)
        rel_lender = clone(origin, seat / "lent_relative_clone")
        rel_b = td / "live_elsewhere" / "rel_borrower"
        subprocess.run(["git", "clone", "-q", "--shared", str(rel_lender), str(rel_b)], check=True, capture_output=True)
        (rel_b / ".git/objects/info/alternates").write_text(
            os.path.relpath(rel_lender / ".git/objects", rel_b / ".git/objects") + "\n")
        wt_owner = clone(origin, seat / "worktree_target_clone")
        wt = td / "live_elsewhere" / "wt"
        git(wt_owner, "worktree", "add", "-q", str(wt), "-b", "wt")
        # a clone whose lender is gone, its objects still in the store: reads through the store, nothing unique
        orphan = seat / "orphan_lender_gone_clone"
        tmp_lender = clone(origin, td / "tmp_lender")
        subprocess.run(["git", "clone", "-q", "--shared", str(tmp_lender), str(orphan)], check=True, capture_output=True)
        subprocess.run(["rm", "-rf", str(tmp_lender)], check=True)
        # unreadable: an inner dir (young or old), a corrupt repo, an in-progress rebase
        locked = clone(origin, seat / "unreadable_clone")
        (locked / "secret").mkdir()
        (locked / "secret/f").write_text("x")
        locked_young = clone(origin, seat / "unreadable_young_clone")
        (locked_young / "secret").mkdir()
        corrupt = clone(origin, seat / "corrupt_git_clone")
        (corrupt / ".git/HEAD").write_text("garbage\n")
        rebasing = clone(origin, seat / "rebase_in_progress_clone")
        (rebasing / ".git/rebase-merge").mkdir()
        linked = seat / "dotgit_file_clone"
        linked.mkdir()
        (linked / ".git").write_text("gitdir: /nonexistent\n")
        # protected, by name, inside, and holding
        held = clone(origin, seat / "seat_clone_held")
        canon = clone(origin, seat / "canon_mark_clone")
        (canon / "CANONICAL_Colony.rws").write_text("save")
        canon2 = clone(origin, seat / "canon_named_clone")
        (canon2 / "Canon_Named_Save.rws").write_text("save")
        # ledger
        mentioned = clone(origin, seat / "crackedlands_rename_clone")
        (corpus / "infrastructure/state/items/OPEN_ITEM.md").write_text("Work sits in %s\n" % mentioned)
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        old_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 30 * 86400))
        recent = clone(origin, seat / "recent_event_clone")
        history = clone(origin, seat / "old_event_clone")
        undated = clone(origin, seat / "undated_event_clone")
        (corpus / "infrastructure/state/ledger/events/FOUNDRY.jsonl").write_text(
            json.dumps({"ts": now_iso, "text": "see %s" % recent}) + "\n"
            + json.dumps({"ts": old_iso, "text": "see %s" % history}) + "\n"
            + json.dumps({"text": "see %s" % undated}) + "\n")
        # sessions
        sr = sessions_root(root)

        def session(uuid):
            s = sr / uuid
            (s / "scratchpad").mkdir(parents=True)
            return s
        sess_ok = session(UUID_OK)
        clone(origin, sess_ok / "scratchpad" / "pushclone")
        sess_mix = session(UUID_MIX)
        mix_clean = clone(origin, sess_mix / "scratchpad" / "mix_clean")
        mix_big = clone(origin, sess_mix / "scratchpad" / "mix_unpushed")
        commit(mix_big, "c.txt", "local only")
        mix_borrowed = clone(origin, sess_mix / "scratchpad" / "mix_borrowed")
        subprocess.run(["git", "clone", "-q", "--shared", str(mix_borrowed), str(td / "live_elsewhere" / "mix_b")],
                       check=True, capture_output=True)
        sess_loose = session(UUID_LOOSE)
        (sess_loose / "scratchpad" / "notes.txt").write_text("only copy of a thought\n")
        sess_lp = session(UUID_LIVEP)
        lp_clone = clone(origin, sess_lp / "scratchpad" / "lp_clone")
        sess_lt = session(UUID_LIVET)
        sess_sub = session(UUID_SUB)
        sess_young = session(UUID_YOUNG)
        y_clone = clone(origin, sess_young / "scratchpad" / "y_clone")

        # a process running inside the clone: a live cwd holds it
        live_cwd = clone(origin, seat / "live_cwd_clone")
        live_fd = clone(origin, seat / "live_open_file_clone")
        live_env = clone(origin, seat / "live_env_clone")
        loose = seat / "loose_file.txt"
        loose.write_text("not a clone\n")

        old = [p for p in seat.iterdir() if p.is_dir() and p.name != "young_clone"]
        for d in old + [sr]:
            age(d)
        young = clone(origin, seat / "young_clone")
        os.chmod(locked / "secret", 0)
        os.chmod(locked_young / "secret", 0)
        (y_clone / "just_now.txt").write_text("touched\n")

        procs.append(sleeper(live_cwd))
        f_open = open(live_fd / "a.txt")
        procs.append(subprocess.Popen(["sleep", "300"], stdin=f_open))
        f_open.close()
        procs.append(subprocess.Popen(["sleep", "300"], env=dict(os.environ, SOME_DIR=str(live_env / "x"))))
        procs.append(subprocess.Popen(["sleep", "300"], env=dict(os.environ, CLAUDE_CODE_SESSION_ID=UUID_LIVEP)))
        (transcripts / "-proj" / (UUID_LIVET + ".jsonl")).write_text("{}\n")
        (transcripts / "-proj" / UUID_SUB / "subagents").mkdir(parents=True)
        (transcripts / "-proj" / UUID_SUB / "subagents" / "agent-x.jsonl").write_text("{}\n")
        # the seat scratch's own helper uses the old transcript dir, whose top file is ancient: a subagent's write counts
        (transcripts / "-proj" / (UUID_SUB + ".jsonl")).write_text("{}\n")
        stale_t = time.time() - OLD
        os.utime(transcripts / "-proj" / (UUID_SUB + ".jsonl"), (stale_t, stale_t))
        stale_t2 = transcripts / "-proj" / (UUID_OK + ".jsonl")
        stale_t2.write_text("{}\n")
        os.utime(stale_t2, (stale_t, stale_t))

        try:
            run_cases(locals())
        finally:
            for p in procs:
                p.kill()
                p.wait()
            for d in (locked / "secret", locked_young / "secret"):
                if d.exists():
                    os.chmod(d, 0o700)

    # the mention prefilter: the lookaround regex over the whole corpus per needle hit the 1800 s unit timeout
    # (SCRATCHREAP_FIX_THIRTY_MINUTES_OF_HOMEWORK). Count regex scans against a corpus that lacks the needle.
    class _Rx:
        n = 0

        def __init__(self, rx):
            self.rx = rx

        def finditer(self, t):
            _Rx.n += 1
            return self.rx.finditer(t)
    R._CORPUS, R._VOCAB = [("a.md", "x" * 1000 + "\nnames /tmp/hit/dir here\n"), ("b.md", "nothing relevant")], None
    real_compile = R.re.compile
    R.re.compile = lambda pat, *a: _Rx(real_compile(pat, *a))
    try:
        hit = R.ledger_mentions(Path("/tmp/hit/dir"), "clone")
        miss = R.ledger_mentions(Path("/tmp/absent/zzzdir"), "clone")
    finally:
        R.re.compile = real_compile
        R._CORPUS = R._VOCAB = None
    check(len(hit) >= 1 and "a.md" in hit[0], "ledger_mentions still finds a real mention")
    check(miss == [] and _Rx.n == 1, f"ledger_mentions skips the regex when the needle is absent (scans={_Rx.n}, want 1)")
    print("ALL PASS" if not FAILS else f"{len(FAILS)} FAIL")
    return 1 if FAILS else 0


def run_cases(env):
    g = env.__getitem__
    td, seat, origin, archive, corpus, root = g("td"), g("seat"), g("origin"), g("archive"), g("corpus"), g("root")
    rc, rows = run_reaper()
    v = {k: r["verdict"] for k, r in rows.items()}
    why = {k: " | ".join(r["why"]) for k, r in rows.items()}
    real_read, calls = R.Live._read, []

    def flaky(self, pid, base, cmds):                 # a forked child, unreadable until its exec lands
        if pid == str(os.getppid()) and len(calls) < stuck:
            calls.append(pid)
            raise PermissionError(13, "Permission denied")
        return real_read(self, pid, base, cmds)
    R.Live._read = flaky
    try:
        stuck = 2
        check(not [b for b in R.Live(time.time()).blind if f"pid {os.getppid()} " in b], "a process unreadable for a moment is not a blind spot")
        calls.clear()
        stuck = 99
        check(any(f"pid {os.getppid()} " in b for b in R.Live(time.time()).blind), "a process that stays unreadable is a blind spot")
    finally:
        R.Live._read = real_read
    check(rc == 0, "a dry run exits 0")
    check(v.get("clean_pushed_clone") == "DELETE", "an old, clean, pushed clone is a DELETE")
    for name, word in (("unpushed_clone", "on no remote"), ("dirty_tracked_clone", "tracked file(s) changed"),
                       ("untracked_file_clone", "untracked"), ("stashed_clone", "stash"),
                       ("reflog_only_clone", "on no remote"), ("odd_ref_clone", "on no remote"),
                       ("no_remote_clone", "no remote"), ("local_remote_clone", "on no remote"),
                       ("renamed_clone", "tracked file(s) changed")):
        check(v.get(name) == "ARCHIVE" and word in why[name], f"{name}: unique work means bundle first ({v.get(name)})")
    check(v.get("stale_ref_clone") == "DELETE", "a commit on the mirror counts as pushed despite a stale ref")
    check(v.get("rewritten_same_content_clone") == "DELETE", "a commit main holds under a rewritten hash counts as pushed")
    check(v.get("rewritten_history_clone") == "ARCHIVE" and "other content" in why["rewritten_history_clone"],
          "main's author and dates over other content is not main's commit")
    check(v.get("amended_after_push_clone") == "ARCHIVE", "an amend after the push is unique work, whatever its author date")
    check(v.get("tracked_canon_clone") == "DELETE" and "tracked_canon_clone" in rows, "the repo's own clean copy of a save holds nothing")
    check(v.get("tracked_canon_changed_clone") == "REFUSE" and "canonical save" in why["tracked_canon_changed_clone"],
          "a tracked save with local changes holds its clone")
    check(v.get("tracked_canon_gone_clone") == "REFUSE" and "canonical save" in why["tracked_canon_gone_clone"],
          "a tracked save no seat clone still holds keeps its clone")
    for name, word in (("lender_clone", "borrows"), ("lent_to_outside_clone", "borrows"),
                       ("lent_relative_clone", "borrows"), ("worktree_target_clone", "borrows"),
                       ("unreadable_clone", "unreadable"), ("unreadable_young_clone", "unreadable"),
                       ("corrupt_git_clone", "git cannot read"), ("rebase_in_progress_clone", "in progress"),
                       ("dotgit_file_clone", ".git is a file"), ("seat_clone_held", "protected"),
                       ("canon_mark_clone", "canonical save"), ("canon_named_clone", "canonical save"),
                       ("crackedlands_rename_clone", "names"), ("recent_event_clone", "names"),
                       ("undated_event_clone", "names"), ("live_cwd_clone", "pid"), ("live_open_file_clone", "pid"),
                       ("live_env_clone", "pid")):
        check(v.get(name) == "REFUSE" and word in why[name], f"{name}: skipped, reported ({v.get(name)}: {why.get(name, '')[:70]})")
    check(v.get("borrower_clone") == "DELETE", "a clean, pushed BORROWER is deletable (only its lender must stay)")
    check(v.get("orphan_lender_gone_clone") == "DELETE", "a clone whose lender is gone reads through the store, not a failure")
    check(v.get("old_event_clone") == "DELETE", "a month-old mention is history, not a hold")
    check(v.get("young_clone") == "YOUNG", "a clone touched within the TTL is YOUNG")
    check(v.get(UUID_OK) == "DELETE" and v.get("pushclone") == "DELETE", "an old session of pushed clones goes")
    check(v.get("mix_clean") == "DELETE" and v.get("mix_unpushed") == "ARCHIVE" and v.get("mix_borrowed") == "REFUSE",
          "a session's clones are judged one by one, so one bad clone keeps only itself")
    check(v.get(UUID_MIX) == "REFUSE" and "inner clone" in why[UUID_MIX], "the session shell stays while a clone inside it stays")
    check(v.get(UUID_LOOSE) == "ARCHIVE", "loose session files are tarred before the shell goes")
    check(v.get(UUID_LIVEP) == "REFUSE" and "live session" in why[UUID_LIVEP] and "lp_clone" not in rows,
          "a session whose uuid a process carries is held whole, inner clones not even judged")
    check(v.get(UUID_LIVET) == "REFUSE" and "transcript" in why[UUID_LIVET], "a fresh transcript holds its session")
    check(v.get(UUID_SUB) == "REFUSE" and "transcript" in why[UUID_SUB], "a fresh SUBAGENT transcript holds its session")
    check(v.get(UUID_YOUNG) == "YOUNG" and "y_clone" not in rows, "a touch anywhere inside keeps the whole session YOUNG")
    check("loose_file.txt" not in rows, "loose files outside sessions are never candidates")
    check(g("clean").exists() and g("unpushed").exists() and not acts(archive), "the dry run touches nothing")
    check(not (td / "state/last_run.json").exists() and (td / "state/last_dry_run.json").exists(),
          "a dry run never writes the record ops_watch alarms on")
    check(rows["mix_clean"]["bytes"] > 0 and rows[UUID_MIX]["bytes"] < rows["mix_clean"]["bytes"],
          "a session's bytes are its residue: no byte counts twice")

    # guard, independent of what candidates() offers
    ctx = R.Ctx(time.time())
    for p, name in ((Path("/home/mandrake/rm/bench"), "seat clone"), (Path("/home/mandrake/rm/arena/replay/x/y"), "replay"),
                    (Path("/home/mandrake/rm/store.git"), "store.git"), (Path("/home/mandrake/rm/arena-vet"), "arena-vet"),
                    (root, "a root itself")):
        check(R.judge_clone(p, ctx)["verdict"] == "REFUSE", f"guard: {name} is REFUSED")
    outside = clone_old(origin, td / "outside")
    check("outside the reap roots" in " ".join(R.judge_clone(outside, ctx)["why"]), "guard: an old clean clone outside the roots is REFUSED")
    os.environ["SCRATCH_REAP_ROOTS"] = "/home/mandrake/rm"
    check("protected" in R.judge_clone(Path("/home/mandrake/rm/foundry"), ctx)["why"][0], "guard: foundry refused even with rm/ as a root")
    check("protected" in R.judge_clone(Path("/home/mandrake/rm/dispatch"), ctx)["why"][0], "guard: dispatch refused too")
    os.environ["SCRATCH_REAP_ROOTS"] = str(root)

    # fail closed, everything at once
    real_live = R.Live.__init__

    def blind(self, now):
        real_live(self, now)
        self.blind = ["pid 1234: Permission denied"]
    R.Live.__init__ = blind
    try:
        rc, r2 = run_reaper()
    finally:
        R.Live.__init__ = real_live
    check(r2["clean_pushed_clone"]["verdict"] == "REFUSE" and r2[UUID_OK]["verdict"] == "REFUSE",
          "a process of ours we cannot inspect holds EVERYTHING")
    bad_alt = td / "live_elsewhere" / "unreadable_alternates"
    subprocess.run(["git", "clone", "-q", "--shared", str(origin), str(bad_alt)], check=True, capture_output=True)
    alt = bad_alt / ".git/objects/info/alternates"
    os.chmod(alt, 0)
    try:
        rc, r2 = run_reaper()
    finally:
        os.chmod(alt, 0o600)
    check(r2["clean_pushed_clone"]["verdict"] == "REFUSE" and "borrower" in " ".join(r2["clean_pushed_clone"]["why"]),
          "an alternates file we cannot read holds EVERYTHING")
    alt.unlink()
    alt.symlink_to(td / "gone_since_find_met_it")          # what a clone removed mid-scan looks like to the reader
    rc, r2 = run_reaper()
    alt.unlink()
    alt.write_text(str(origin / ".git/objects") + "\n")
    check(not any("cannot read a borrower" in " ".join(r["why"]) for r in r2.values()),
          "a borrower file gone since find met it stops nothing")
    os.environ["SCRATCH_REAP_TRANSCRIPTS"] = str(td / "no_such_transcripts")
    rc, r2 = run_reaper()
    os.environ["SCRATCH_REAP_TRANSCRIPTS"] = str(td / "transcripts")
    check(r2[UUID_OK]["verdict"] == "REFUSE", "an unreadable transcript tree holds the sessions")

    # the archive root is gone: unique work stays, the unit fails, clean work still goes
    probe = clone_old(origin, seat / "arch_probe_clone")
    os.environ["LEFTOVERS_ARCHIVE_ROOT"] = str(td / "unmounted")
    (probe / "f.txt").write_text("work\n")
    age(probe)
    only = {"SCRATCH_REAP_ROOTS": str(td / "isolated"), "SCRATCH_REAP_SCAN": str(td / "isolated")}
    iso = td / "isolated" / "S"
    iso.mkdir(parents=True)
    os.replace(probe, iso / "arch_probe_clone")
    age(td / "isolated")
    saved = {k: os.environ.get(k) for k in only}
    os.environ.update(only)
    rc, r3 = run_reaper("--apply")
    check(rc == 1 and (iso / "arch_probe_clone").exists() and r3["arch_probe_clone"]["verdict"] == "REFUSE",
          "no archive root: the path stays and the run exits 1")
    rec = json.loads((td / "state/last_run.json").read_text())
    check(rec["ok"] is False and rec["failures"], "the failed run says so in last_run.json")
    check(rec["last_ok_epoch"] is None, "a failed run does not count as a clean one")
    os.environ.update({k: v for k, v in saved.items()})
    os.environ["LEFTOVERS_ARCHIVE_ROOT"] = str(archive)
    (td / "state/alarms_seen.json").unlink()

    # the changed-since-scan race: a clone becomes live between scan and rmtree
    race = clone_old(origin, seat / "race_clone")
    real_judge = R.judge_all

    def touch_after_scan(ctx):
        rows = real_judge(ctx)
        (race / "new.txt").write_text("someone arrived\n")
        return rows
    R.judge_all = touch_after_scan
    # the real run
    rc, rows = run_reaper("--apply")
    R.judge_all = real_judge
    v = {k: r["verdict"] for k, r in rows.items()}
    check(rc == 0, "the real run exits 0")
    check(race.exists() and v["race_clone"] == "YOUNG" and "changed since the scan" in rows["race_clone"]["why"][0],
          "a clone touched between scan and delete survives")
    gone = ["clean", "stale", "borrower", "unpushed", "dirty", "untracked", "stashed", "reflogged", "oddref", "noremote",
            "localremote", "renamed", "orphan", "mix_clean", "mix_big", "history"]
    check(not [n for n in gone if g(n).exists()], "--apply removes every DELETE and ARCHIVE clone: "
          + str([n for n in gone if g(n).exists()]))
    kept = ["lender", "lender2", "rel_lender", "wt_owner", "locked", "locked_young", "corrupt", "rebasing", "linked", "held",
            "canon", "canon2", "mentioned", "recent", "undated", "live_cwd", "live_fd", "live_env", "young", "loose",
            "sess_mix", "mix_borrowed", "sess_lp", "lp_clone", "sess_lt", "sess_sub", "sess_young", "y_clone"]
    check(not [n for n in kept if not g(n).exists()], "--apply leaves every refused, live, young or other path: "
          + str([n for n in kept if not g(n).exists()]))
    git(g("far"), "fsck", "--connectivity-only")
    check(True, "the outside borrower still reads its objects after the run")

    # bundles restore: a fresh clone of the mirror plus the bundle gets the only copy back, from a dir we did not plan
    all_acts = acts(archive)
    for name, sha in (("unpushed_clone", g("unpushed_sha")), ("reflog_only_clone", g("lost_sha")),
                      ("odd_ref_clone", g("oddref_sha")), ("local_remote_clone", g("localremote_sha"))):
        back = td / ("back_" + name)
        subprocess.run(["git", "clone", "-q", str(origin), str(back)], check=True, capture_output=True)
        git(back, "fetch", "-q", str(bundle_of(rows, name)), "refs/rm/*:refs/rescued/*")
        check(git(back, "cat-file", "-t", sha) == "commit", f"{name}: the bundle restores the only copy of its commit")
        a = [x for x in all_acts if x["path"].endswith(name)]
        check(len(a) == 1 and a[0]["kind"] == "scratch-clone" and a[0]["archive"] and a[0]["ts"],
              f"{name}: one acts.jsonl line, so his digest lists it")
    bare = td / "back_noremote"
    subprocess.run(["git", "init", "-q", str(bare)], check=True)
    git(bare, "fetch", "-q", str(bundle_of(rows, "no_remote_clone")), "refs/rm/*:refs/rescued/*")
    check(git(bare, "log", "-1", "--format=%s", "refs/rescued/0") == "only copy", "a clone with no remote restores from nothing but its bundle")
    tar = Path(rows["dirty_tracked_clone"]["archive"]) / "dirty.tar.gz"
    check(subprocess.run(["tar", "-xzOf", str(tar), "a.txt"], capture_output=True, text=True).stdout == "edited\n",
          "the dirty file's edit is in the tar")
    tar = Path(rows["untracked_file_clone"]["archive"]) / "dirty.tar.gz"
    check("ITEM_PROSE.md" in subprocess.run(["tar", "-tzf", str(tar)], capture_output=True, text=True).stdout, "the untracked file is in the tar")
    tar = Path(rows["renamed_clone"]["archive"]) / "dirty.tar.gz"
    listing = subprocess.run(["tar", "-tzf", str(tar)], capture_output=True, text=True).stdout
    check("z.txt" in listing and "with space" in listing, "a rename and a newline in a name both reach the tar")
    check(rows["dirty_tracked_clone"].get("archive") and not rows["clean_pushed_clone"].get("archive"), "only unique work is bundled")
    run_lines = [x for x in all_acts if x["kind"] == "scratch-expiry-run"]
    check(len(run_lines) == 1 and Path(run_lines[0]["manifest"]).exists(), "clean deletes reach the digest in one run line")
    alarms = (td / "state/alarms.log").read_text()
    check("lender_clone" in alarms, "a refusal is written as an alarm line")
    rec = json.loads((td / "state/last_run.json").read_text())
    check(rec["ok"] is True and rec["freed_bytes"] > 0 and rec["counts"]["DELETED"] > 5 and rec["last_ok_epoch"],
          "last_run.json records the real run")

    # a session shell goes once its clones have aged out, carrying its residue; the next run alarms nothing new
    n_before = len(alarms.splitlines())
    check(g("sess_ok").exists() and rows[UUID_OK]["verdict"] == "YOUNG" and not g("sess_loose").exists(),
          "a shell whose clones just went waits one TTL (their removal touched it); a shell of loose files goes now")
    residue = rows[UUID_LOOSE]["archive"]
    age(g("sess_ok"))
    rc, rows = run_reaper("--apply")
    check(not g("sess_ok").exists(), "the shell goes on a later run")
    check(len((td / "state/alarms.log").read_text().splitlines()) == n_before, "a standing refusal alarms once, not hourly")
    tar = Path(residue) / "residue.tar.gz"
    check("notes.txt" in subprocess.run(["tar", "-tzf", str(tar)], capture_output=True, text=True).stdout, "the residue was tarred first")

    # a clone that cannot be preserved stays, and the run is not a failure
    over = clone_old(origin, seat / "over_cap_clone")
    (over / "w.txt").write_text("work\n")
    age(over)
    real_cap = R.make_tar

    def boom(*a, **k):
        raise R.PreserveFailed("tar: disk full")
    R.make_tar = boom
    rc, rows = run_reaper("--apply")
    R.make_tar = real_cap
    check(rc == 1 and over.exists() and rows["over_cap_clone"]["verdict"] == "REFUSE", "a preservation that breaks stays and fails the run")

    def too_big(*a, **k):
        raise R.OverCap("bundle is 9 GB")
    R.make_tar = too_big
    rc, rows = run_reaper("--apply")
    R.make_tar = real_cap
    check(rc == 0 and over.exists() and rows["over_cap_clone"]["verdict"] == "REFUSE", "too big to keep is a refusal, not a failure")

    # the run-time cap defers, never skips the checks
    d1 = clone_old(origin, seat / "deferred_clone")
    rc, rows = run_reaper("--apply", "--max-seconds", "0.000001")
    check(d1.exists() and rows["deferred_clone"].get("deferred") is True, "--max-seconds leaves the rest for the next run")
    # a held lock is not a failure and does nothing
    import fcntl
    with open(td / "state/run.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        from io import StringIO
        import contextlib
        b = StringIO()
        with contextlib.redirect_stdout(b):
            c = subprocess.run([sys.executable, str(Path(R.__file__)), "--apply"], capture_output=True, text=True).returncode
        check(c == 0 and d1.exists(), "a run that finds the lock held stands down")

    # disk pressure, at the unit boundary
    real_run = R.subprocess.run
    calls = []

    def fake_run(cmd, **k):
        if cmd[0] == "systemctl":
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return real_run(cmd, **k)
    R.subprocess.run = fake_run
    real_free = R.free_gb
    try:
        R.free_gb = lambda p="/": 100.0
        rec = td / "state/last_run.json"
        R.pressure_check()
        check(not calls, "pressure: a run inside the cooldown means no second start")
        d = json.loads(rec.read_text())
        d["end_epoch"] = time.time() - 3600
        rec.write_text(json.dumps(d))
        R.pressure_check()
        check(len(calls) == 1 and "rm-scratch-reap.service" in calls[0], "pressure: low disk starts the reaper's unit")
        R.free_gb = lambda p="/": 900.0
        calls.clear()
        R.pressure_check()
        check(not calls, "pressure: a healthy disk starts nothing")
    finally:
        R.subprocess.run = real_run
        R.free_gb = real_free
    review_cases(td, origin)
    second_review_cases(td, origin)
    third_review_cases(td, origin)


UUID_LOCKED = "11111111-2222-4333-8444-555555555555"


def tree_names(tgz: Path) -> str:
    return subprocess.run(["tar", "-tzf", str(tgz)], capture_output=True, text=True).stdout


def tree_names_and_bytes(tgz: Path) -> str:
    with tarfile.open(tgz) as t:
        return "".join(t.extractfile(m).read().decode() for m in t if m.isfile())


def review_cases(td: Path, origin: Path):
    """Each case is a way a first version lost work: a second reader found them, so each is planted here."""
    root2 = td / "r2"
    s2 = root2 / "S"
    s2.mkdir(parents=True)
    saved = {k: os.environ.get(k) for k in ("SCRATCH_REAP_ROOTS", "SCRATCH_REAP_SCAN", "LEFTOVERS_ARCHIVE_ROOT")}
    os.environ.update(SCRATCH_REAP_ROOTS=str(root2), SCRATCH_REAP_SCAN=str(root2), LEFTOVERS_ARCHIVE_ROOT=str(td / "archive"))
    procs = []
    try:
        nested = clone(origin, s2 / "nested_clone")
        (nested / ".git/info/exclude").write_text("vendored/\n")
        subprocess.run(["git", "init", "-q", str(nested / "vendored")], check=True)
        ign = clone(origin, s2 / "ignored_work_clone")
        (ign / ".git/info/exclude").write_text("notes.txt\n__pycache__/\n")
        (ign / "notes.txt").write_text("a night of notes\n")
        (ign / "__pycache__").mkdir()
        (ign / "__pycache__/a.pyc").write_text("x")
        mm = clone(origin, s2 / "staged_then_edited_clone")
        (mm / "a.txt").write_text("staged version\n")
        git(mm, "add", "a.txt")
        (mm / "a.txt").write_text("worktree version\n")
        gone = clone(origin, s2 / "deletion_only_clone")
        git(gone, "rm", "-q", "a.txt")
        assume = clone(origin, s2 / "assume_unchanged_clone")
        (assume / "a.txt").write_text("hidden from status\n")
        git(assume, "update-index", "--assume-unchanged", "a.txt")
        skip = clone(origin, s2 / "skip_worktree_clone")
        (skip / "a.txt").write_text("hidden from status\n")
        git(skip, "update-index", "--skip-worktree", "a.txt")
        canon = clone(origin, s2 / "canon_hidden_change_clone")
        (canon / "CANONICAL_Tracked.rws").write_text("a run wrote over it\n")
        git(canon, "update-index", "--assume-unchanged", "CANONICAL_Tracked.rws")
        tracking = clone(origin, s2 / "local_tracking_ref_clone")
        commit(tracking, "only_here.txt", "only here")
        git(tracking, "update-ref", "refs/remotes/origin/fake", "HEAD")
        hide = clone(origin, s2 / "only_a_tracking_ref_clone")
        commit(hide, "only_here.txt", "only under a tracking ref")
        git(hide, "update-ref", "refs/remotes/origin/fake", "HEAD")
        git(hide, "reset", "-q", "--hard", "HEAD~1")
        git(hide, "reflog", "expire", "--expire=now", "--all")
        twin = clone(origin, s2 / "other_content_clone")
        dated(twin, "twin.txt", "other bytes", "Same work", "2026-01-01T00:00:00Z")
        crash = clone(origin, s2 / ".reaping-1-crashed_clone")
        gens = clone(origin, s2 / "generations_clone")
        (gens / "w.txt").write_text("w\n")
        pin_a = clone(origin, s2 / "process_arrives_clone")
        pin_b = clone(origin, s2 / "write_arrives_clone")
        lender = clone(origin, s2 / "idle_lender_clone")
        far = td / "not_scanned"
        far.mkdir()
        borrower = clone(lender, far / "borrower")
        subprocess.run(["git", "-C", str(borrower), "repack", "-adq"], check=True, capture_output=True)
        (borrower / ".git/objects/info/alternates").write_text(str(lender / ".git/objects") + "\n")
        alias_target = clone(origin, s2 / "alias_target_clone")
        for c in s2.iterdir():
            age(c)
        procs.append(sleeper(borrower))
        procs.append(sleeper(alias_target))
        time.sleep(0.3)

        rc, rows = run_reaper()
        v = {k: r["verdict"] for k, r in rows.items()}
        why = {k: " | ".join(r["why"]) for k, r in rows.items()}
        check(v.get("nested_clone") == "REFUSE" and "nested" in why["nested_clone"], "a repo nested in an ignored dir is refused")
        check(v.get("ignored_work_clone") == "ARCHIVE" and rows["ignored_work_clone"]["dirty"] == ["notes.txt"],
              "ignored notes are work; ignored bytecode is not")
        check(v.get("staged_then_edited_clone") == "ARCHIVE", "staged, then edited, is work")
        check(v.get("deletion_only_clone") == "ARCHIVE", "a staged deletion alone is work")
        for n in ("assume_unchanged_clone", "skip_worktree_clone"):
            check(v.get(n) == "REFUSE" and "assume-unchanged" in why[n], f"{n}: git status cannot vouch, so it stays")
        check(v.get("canon_hidden_change_clone") == "REFUSE" and "canonical save" in why["canon_hidden_change_clone"],
              "a save changed under an index flag is held by its bytes")
        check(v.get("local_tracking_ref_clone") == "ARCHIVE" and rows["local_tracking_ref_clone"]["unique"] == 1,
              "a local tracking ref proves no push")
        check(v.get("only_a_tracking_ref_clone") == "ARCHIVE" and rows["only_a_tracking_ref_clone"]["tips"],
              "a commit held only by a tracking ref is kept")
        check(v.get("other_content_clone") == "ARCHIVE" and rows["other_content_clone"]["changed"], "changed content goes to a patch")
        check(v.get(".reaping-1-crashed_clone") == "DELETE", "a pin a crash left behind is judged like any other")
        check(v.get("idle_lender_clone") == "REFUSE" and "borrows" in why["idle_lender_clone"],
              "a running clone outside the scan keeps its lender")

        alias = td / "alias_root"
        alias.symlink_to(root2)
        check(R.Live(time.time()).users(alias / "S/alias_target_clone"), "a process is seen through a symlinked root")

        ctx = R.Ctx(time.time())
        row = R.judge_clone(gens, ctx)
        first, second = R.preserve(dict(row)), R.preserve(dict(row))
        check(first != second and (Path(first) / "dirty.tar.gz").exists() and (Path(second) / "dirty.tar.gz").exists(),
              "a second preservation never overwrites the first")

        real_refresh = R.Ctx.refresh

        def arrive_proc(self):
            for g in s2.glob(".reaping-*process_arrives_clone"):
                procs.append(sleeper(g))
                time.sleep(0.2)
            real_refresh(self)

        def arrive_write(self):
            for g in s2.glob(".reaping-*write_arrives_clone"):
                (g / "late.txt").write_text("late\n")
            real_refresh(self)

        for name, fake, c, n in ((("a process"), arrive_proc, pin_a, "process_arrives_clone"), ("a write", arrive_write, pin_b, "write_arrives_clone")):
            R.Ctx.refresh = fake
            ctx = R.Ctx(time.time())
            r = R.judge_clone(c, ctx)
            fails = []
            R.act(r, ctx, fails)
            R.Ctx.refresh = real_refresh
            check(c.exists() and not list(s2.glob(".reaping-*" + n)) and r["verdict"] == "REFUSE" and "arrived" in " ".join(r["why"]),
                  f"{name} arriving at the pinned path puts it back")

        rc, rows = run_reaper("--apply")
        a = {k: Path(r["archive"]) for k, r in rows.items() if r.get("archive")}
        check(rc == 0 and not mm.exists() and not ign.exists() and crash.exists() is False, "the review clones go once preserved")
        p = a["staged_then_edited_clone"]
        check("staged version" in (p / "staged.patch").read_text() and "worktree version" in (p / "unstaged.patch").read_text(),
              "both versions of a staged-then-edited file are kept")
        check((a["deletion_only_clone"] / "staged.patch").read_text().count("deleted file") == 1, "the deletion is in the patch")
        check("notes.txt" in tree_names(a["ignored_work_clone"] / "dirty.tar.gz"), "ignored notes are in the tar")
        check("Same work" in (a["other_content_clone"] / "rewritten.patch").read_text()
              and "other bytes" in (a["other_content_clone"] / "rewritten.patch").read_text(), "the rewritten commit's own diff is kept")
        check((a["only_a_tracking_ref_clone"] / "clone.bundle").exists(), "the tracking ref's commit is bundled")
        check((a["local_tracking_ref_clone"] / "clone.bundle").exists(), "the local-ref commit is bundled")
        check(nested.exists() and assume.exists() and skip.exists() and canon.exists() and lender.exists(), "refused clones remain")

        # restore test, by its two failures
        bare = td / "cannot_restore"
        rt = clone(origin, bare)
        commit(rt, "x.txt", "x")
        tip = [git(rt, "rev-parse", "HEAD").strip()]
        real_git = R.git
        for mode, word in (("fetch", "restore test"), ("for-each-ref", "tips came back")):
            def lying(repo, *a, _m=mode, **k):
                if str(repo).endswith("dst.git") and a[0] == _m:
                    if _m == "fetch":
                        return subprocess.CompletedProcess(a, 1, "", "restore broke")
                    return subprocess.CompletedProcess(a, 0, "", "")
                return real_git(repo, *a, **k)
            R.git = lying
            w = td / f"w_{mode}"
            w.mkdir()
            try:
                R.make_bundle(rt, tip, w)
                check(False, f"restore failure by {mode} is noticed")
            except R.PreserveFailed as e:
                check(word in str(e), f"restore failure by {mode} is noticed")
            finally:
                R.git = real_git

        # a tip left off the bundle must be refused, not lost
        try:
            R.preserve({"path": str(rt), "kind": "clone", "unique": 2, "tips": [], "why": [], "bytes": 1, "age_h": 1})
            check(False, "unique commits with no tip stop the preservation")
        except R.PreserveFailed:
            check(True, "unique commits with no tip stop the preservation")

        # the safety evidence, unreadable
        items = Path(os.environ["SCRATCH_REAP_CORPUS"]) / "infrastructure/state/items"
        R._CORPUS = None
        os.chmod(items, 0)
        try:
            R.corpus()
            check(False, "an unreadable items dir stops the run")
        except RuntimeError:
            check(True, "an unreadable items dir stops the run")
        finally:
            os.chmod(items, 0o700)
            R._CORPUS = None
        tr = Path(os.environ["SCRATCH_REAP_TRANSCRIPTS"]) / "-proj" / UUID_LOCKED
        (tr / "sub").mkdir(parents=True)
        os.chmod(tr / "sub", 0)
        try:
            check(R.transcripts_fresh(time.time()) is None, "a transcript behind an unreadable dir blinds the scan")
        finally:
            os.chmod(tr / "sub", 0o700)
            subprocess.run(["rm", "-rf", str(tr)], check=True)

        # find's complaints
        h = R.Borrows._harmless
        check(h("find: ‘/proc/1/fdinfo’: Permission denied"), "another user's dir cannot hold a borrower")
        check(h("bfs: error: /proc/1/fdinfo: Permission denied."), "and in bfs's wording")
        mine = td / "denied_outside"
        mine.mkdir()
        check(not h(f"find: ‘{mine}’: Permission denied"), "a dir of ours outside the roots stays a hold")
        check(h(f"find: ‘{root2 / 'S'}’: Permission denied"), "a dir of ours under a root is refused with its candidate")
        check(not h("Permission denied somewhere"), "a line that names no path stays a hold")
        check(h(f"find: ‘{td}/gone_since’: Permission denied"), "a dir gone since find met it holds nothing")

        # the process table
        real_read, real_system, seen = R.Live._read, R.undumpable_system, []
        parent = str(os.getppid())

        def locked_up(self, pid, base, cmds):
            if pid == parent:
                seen.append(1)
                if len(seen) <= stuck:
                    raise PermissionError(13, "Permission denied")
            return real_read(self, pid, base, cmds)
        R.Live._read = locked_up
        R.undumpable_system = lambda base: True
        try:
            stuck, seen[:] = 1, []
            R._SYSTEM_PIDS.clear()
            R.Live(time.time())
            check(len(seen) >= 2 and parent not in R._SYSTEM_PIDS, "a forked child called systemd still gets read once it has exec'd")
            stuck, seen[:] = 99, []
            check(not [b for b in R.Live(time.time()).blind if f"pid {parent}:" in b] and parent in R._SYSTEM_PIDS, "a real undumpable system process is exempt")
            seen[:] = []
            R.Live(time.time())
            check(len(seen) == 1, "and costs no retries next time")
        finally:
            R.Live._read, R.undumpable_system = real_read, real_system
            R._SYSTEM_PIDS.clear()

        real_open = open

        def status_denied(f, *a, **k):
            if str(f) == f"/proc/{parent}/status":
                raise PermissionError(13, "Permission denied")
            return real_open(f, *a, **k)
        R.open = status_denied
        try:
            check(any("status" in b for b in R.Live(time.time()).blind), "an unreadable status is blindness, not an ended process")
        finally:
            del R.open
    finally:
        for p in procs:
            p.kill()
            p.wait()
        for k, val in saved.items():
            if val is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = val


def second_review_cases(td: Path, origin: Path):
    """The second reader's round: the same rule, planted."""
    root3 = td / "r3"
    s3 = root3 / "S"
    s3.mkdir(parents=True)
    (td / "archive3").mkdir()
    keys = ("SCRATCH_REAP_ROOTS", "SCRATCH_REAP_SCAN", "LEFTOVERS_ARCHIVE_ROOT")
    saved = {k: os.environ.get(k) for k in keys}
    os.environ.update(SCRATCH_REAP_ROOTS=str(root3), SCRATCH_REAP_SCAN=str(root3), LEFTOVERS_ARCHIVE_ROOT=str(td / "archive3"))
    procs = []
    locked = td / "denied_above_cwd"
    try:
        # a crash's pin keeps the session's identity
        uid = "abcdef01-2345-6789-abcd-ef0123456789"
        pinned = sessions_root(root3) / f".reaping-7-{uid}"
        pinned.mkdir(parents=True)
        (pinned / "note.txt").write_text("old\n")
        procs.append(sleeper(td, dict(os.environ, CLAUDE_CODE_SESSION_ID=uid)))
        # a bare repo in a session lends to a clone elsewhere
        bare_owner = sessions_root(root3) / "fedcba98-7654-3210-fedc-ba9876543210"
        (bare_owner / "scratchpad").mkdir(parents=True)
        subprocess.run(["git", "clone", "-q", "--bare", str(origin), str(bare_owner / "scratchpad/cache.git")], check=True, capture_output=True)
        holder = root3 / "elsewhere" / "holder"
        clone(origin, holder)
        (holder / ".git/objects/info/alternates").write_text(str(bare_owner / "scratchpad/cache.git/objects") + "\n")
        # handwritten files in ignored build dirs
        hand = clone(origin, s3 / "ignored_bin_clone")
        (hand / ".git/info/exclude").write_text("bin/\n")
        (hand / "bin").mkdir()
        (hand / "bin/recover-colony.py").write_text("only copy\n")
        # a diff driver in the clone's config
        ext = clone(origin, s3 / "external_diff_clone")
        git(ext, "config", "diff.external", "/bin/true")
        (ext / "a.txt").write_text("staged only here\n")
        git(ext, "add", "a.txt")
        (ext / "a.txt").write_text("worktree only here\n")
        lying_index = clone(origin, s3 / "lying_patch_clone")
        (lying_index / "a.txt").write_text("staged\n")
        git(lying_index, "add", "a.txt")
        # bytes a bundle cannot hold
        lfs = clone(origin, s3 / "lfs_clone")
        (lfs / ".git/lfs/objects/aa").mkdir(parents=True)
        (lfs / ".git/lfs/objects/aa/media").write_text("the real bytes\n")
        filt = clone(origin, s3 / "filter_clone")
        git(filt, "config", "filter.crypt.clean", "cat")
        (filt / ".git/info/attributes").write_text("a.txt filter=crypt\n")
        # an arrival that keeps old timestamps
        old = clone(origin, s3 / "old_stamps_arrive_clone")
        (old / "w.txt").write_text("work\n")
        # a live worktree outside the scan
        lender = clone(origin, s3 / "worktree_lender_clone")
        far = td / "far3"
        far.mkdir()
        main_tree = clone(origin, far / "main")
        (main_tree / ".git/objects/info/alternates").write_text(str(lender / ".git/objects") + "\n")
        git(main_tree, "worktree", "add", "-q", str(far / "wt"))
        for c in [*s3.iterdir(), root3 / "BENCH", root3 / "elsewhere"]:
            age(c)
        procs.append(sleeper(far / "wt"))
        time.sleep(0.3)

        live = R.Live(time.time())
        check(live.users(pinned), "a crash's pin does not hide a live session")
        check(uid in R.needles(pinned, "session"), "the ledger is asked about the real session name")
        real_fresh = live.fresh
        live.sessions, live.cmdblob, live.fresh = set(), "", {uid: time.time()}
        check(live.users(pinned), "a fresh transcript still holds a pinned session")
        check(real_fresh is not None, "the transcript map was read")
        check(live.users(lender) and not live.blind[1:], "a live linked worktree keeps what its repo borrows")
        rc, rows = run_reaper()
        v = {k: r["verdict"] for k, r in rows.items()}
        why = {k: " | ".join(r["why"]) for k, r in rows.items()}
        check(v.get(bare_owner.name) == "REFUSE" and "borrows" in why[bare_owner.name], "a session lending from a bare repo stays")
        check(v.get("ignored_bin_clone") == "ARCHIVE" and rows["ignored_bin_clone"]["dirty"] == ["bin/"], "an ignored bin/ is work until proven not")
        check(v.get("lfs_clone") == "REFUSE" and "lfs" in why["lfs_clone"], "git-lfs bytes are held")
        check(v.get("filter_clone") == "REFUSE" and "filter" in why["filter_clone"], "a content filter is held")

        d = R.disposable
        check(not (d("bin/") or d("obj/x.txt") or d("a.lock") or d("Transient/codebase_health_notes.md") or d("infrastructure/state/queuenotes.md")),
              "a name alone does not make a file disposable")
        check(d("__pycache__/") and d("x/y.pyc") and d("Transient/codebase_health.json") and d("infrastructure/state/queue/") and d("infrastructure/state/queue/BENCH.md"),
              "what tools write again is")

        # the preservation
        ctx = R.Ctx(time.time())
        r = R.judge_clone(ext, ctx)
        p = Path(R.preserve(dict(r)))
        check("staged only here" in (p / "staged.patch").read_text(), "an external diff cannot empty the staged patch")
        check("staged only here" in tree_names_and_bytes(p / "staged.tar.gz"), "the staged blob itself is kept")
        real_git, w = R.git, td / "w_lying"
        w.mkdir()

        def wrong_bytes(repo, *a, **k):
            if a[0] == "cat-file":
                return subprocess.CompletedProcess(a, 0, "not the blob\n", "")
            return real_git(repo, *a, **k)
        R.git = wrong_bytes
        try:
            R.make_index_state(lying_index, w)
            check(False, "bytes that are not the staged blob stop the preservation")
        except R.PreserveFailed as e:
            check("not the blob" in str(e), "bytes that are not the staged blob stop the preservation")
        finally:
            R.git = real_git

        real_preserve = R.preserve

        def import_after_tar(row):
            out = real_preserve(row)
            t = os.stat(old)
            f = old / "imported.txt"
            f.write_text("arrived after the tar\n")
            os.utime(f, (1000, 1000))
            os.utime(old, ns=(t.st_atime_ns, t.st_mtime_ns))
            row["top_ctime"] = os.lstat(old).st_ctime_ns       # past the top's own guard, to the deep one
            return out
        ctx = R.Ctx(time.time())
        r = R.judge_clone(old, ctx)
        R.preserve = import_after_tar
        fails = []
        R.act(r, ctx, fails)
        R.preserve = real_preserve
        check(old.exists() and (old / "imported.txt").exists() and r["verdict"] == "REFUSE" and "arrived" in " ".join(r["why"]),
              "an arrival under an old timestamp is still an arrival")

        # digests
        rd = td / "digests"
        rd.mkdir()
        git(rd, "init", "-q")
        env = dict(os.environ, GIT_AUTHOR_DATE="2026-01-01T00:00:00Z", GIT_COMMITTER_DATE="2026-01-01T00:00:00Z")

        def ci(msg):
            subprocess.run(["git", "-C", str(rd), "commit", "-q", "--allow-empty", "-m", msg], check=True, capture_output=True, env=env)
            return git(rd, "rev-parse", "HEAD")
        (rd / "tool.sh").write_text("v1\n")
        git(rd, "add", ".")
        base = ci("base")
        (rd / "tool.sh").write_text("v2\n")
        git(rd, "add", ".")
        plain = ci("same")
        git(rd, "reset", "-q", "--hard", base)
        (rd / "tool.sh").write_text("v2\n")
        os.chmod(rd / "tool.sh", 0o755)
        git(rd, "add", ".")
        run = ci("same")
        dg = R.commit_digests(rd, "--no-walk=unsorted", plain, run)
        check(dg[plain][0] == dg[run][0] and dg[plain][1] != dg[run][1], "a mode change is a content change")
        git(rd, "reset", "-q", "--hard", base)
        blobs = sorted((subprocess.run(["git", "-C", str(rd), "hash-object", "-w", "--stdin"], input=t, capture_output=True, text=True, check=True).stdout.strip(), t)
                       for t in ("one\n", "two\n"))
        (ba, ta), (bb, tb) = blobs
        (rd / "a").write_text(ta)
        (rd / "b").write_text(tb)
        git(rd, "add", ".")
        two = ci("names")
        git(rd, "reset", "-q", "--hard", base)
        (rd / f"a\n{bb} b").write_text(ta)
        git(rd, "add", ".")
        one = ci("names")
        dg = R.commit_digests(rd, "--no-walk=unsorted", two, one)
        check(dg[two][1] != dg[one][1], "a newline in a name cannot forge two entries")

        # denied ancestors
        foreign = root3 / "foreign_denied"
        foreign.mkdir()
        outside = td / "foreign_outside"
        outside.mkdir()
        real_lstat = os.lstat

        def other_owner(f, *a, **k):
            st = real_lstat(f, *a, **k)
            if str(f) in (str(foreign), str(outside)):
                return types.SimpleNamespace(st_uid=os.getuid() + 1, st_mode=st.st_mode)
            return st
        os.lstat = other_owner
        try:
            h = R.Borrows._harmless
            check(not h(f"find: ‘{foreign}’: Permission denied"), "another user's dir inside our trees stays a hold")
            check(h(f"find: ‘{outside}’: Permission denied"), "another user's dir outside them does not")
        finally:
            os.lstat = real_lstat
        (locked / "sub").mkdir(parents=True)
        procs.append(sleeper(locked / "sub"))
        time.sleep(0.2)
        os.chmod(locked, 0)
        check(any("cannot see the repo" in b for b in R.Live(time.time()).blind), "a live cwd beneath a denied dir blinds the scan")
        os.chmod(locked, 0o700)
        broken = td / "broken_wt"
        broken.mkdir()
        (broken / ".git").write_text("nonsense\n")
        procs.append(sleeper(broken))
        time.sleep(0.2)
        check(any(".git" in b and "broken_wt" in b for b in R.Live(time.time()).blind), "a `.git` file we cannot follow blinds the scan")
    finally:
        os.chmod(locked, 0o700) if locked.exists() else None
        for p in procs:
            p.kill()
            p.wait()
        for k, val in saved.items():
            if val is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = val


def third_review_cases(td: Path, origin: Path):
    """The third reader's round."""
    root4 = td / "r4"
    s4 = root4 / "S"
    s4.mkdir(parents=True)
    (td / "archive4").mkdir()
    keys = ("SCRATCH_REAP_ROOTS", "SCRATCH_REAP_SCAN", "LEFTOVERS_ARCHIVE_ROOT", "GIT_CONFIG_GLOBAL")
    saved = {k: os.environ.get(k) for k in keys}
    os.environ.update(SCRATCH_REAP_ROOTS=str(root4), SCRATCH_REAP_SCAN=str(root4), LEFTOVERS_ARCHIVE_ROOT=str(td / "archive4"))
    try:
        # an index a tar alone could not rebuild
        idx = clone(origin, s4 / "index_clone")
        (idx / "tool.sh").write_text("run\n")
        (idx / "gone\nfile").write_text("x\n")
        git(idx, "add", ".")
        git(idx, "commit", "-q", "-m", "tools")
        subprocess.run(["git", "-C", str(idx), "push", "-q", "origin", "HEAD:refs/heads/index_base"], check=True, capture_output=True)
        os.chmod(idx / "tool.sh", 0o755)
        (idx / "link").symlink_to("tool.sh")
        (idx / "new.txt").write_text("staged only\n")
        git(idx, "add", "tool.sh", "link", "new.txt")
        git(idx, "rm", "-q", "--cached", "gone\nfile")
        (idx / "gone\nfile").unlink()
        cr = clone(origin, s4 / "carriage_clone")
        (cr / "normal.txt").write_text("n\n")
        (cr / "a\rb.txt").write_text("the name has a return\n")
        rep = clone(origin, s4 / "replaced_clone")
        (rep / "only.txt").write_text("unique\n")
        git(rep, "add", ".")
        git(rep, "commit", "-q", "-m", "unique work")
        x = git(rep, "rev-parse", "HEAD")
        git(rep, "replace", x, x + "~1")
        filt = clone(origin, s4 / "global_filter_clone")
        (filt / ".gitattributes").write_text("a.txt filter=strip\n")
        gc = td / "gitconfig4"
        gc.write_text('[filter "strip"]\n\tclean = cat\n\tsmudge = cat\n')
        os.environ["GIT_CONFIG_GLOBAL"] = str(gc)
        mnt = clone(origin, s4 / "mounted_clone")
        (mnt / "cache").mkdir()
        (s4 / "view").mkdir()
        bound = clone(origin, s4 / "view/under_bind_clone")
        sock_c = clone(origin, s4 / "socket_clone")
        listener = socket.socket(socket.AF_UNIX)
        listener.bind(str(sock_c / "s"))
        listener.listen()
        mapped = clone(origin, s4 / "mapped\nclone")
        mapper = subprocess.Popen([sys.executable, "-c", "import mmap,sys\nf=open(sys.argv[1],'rb')\nm=mmap.mmap(f.fileno(),0,prot=mmap.PROT_READ)\n"
                                   "f.close()\nprint('up',flush=True)\nimport time\ntime.sleep(300)", str(mapped / "a.txt")],
                                  stdout=subprocess.PIPE, text=True, cwd=td)
        mapper.stdout.readline()
        fold = clone(origin, s4 / "foldcase_clone")
        git(fold, "config", "core.ignorecase", "true")
        (fold / "NOTES.txt").write_text("unique work\n")
        (fold / "notes.txt").write_text("tracked\n")
        git(fold, "add", "notes.txt")
        git(fold, "commit", "-q", "-m", "notes")
        tc = clone(origin, s4 / "trustctime_clone")
        git(tc, "config", "core.trustctime", "false")
        st = (tc / "a.txt").stat()
        tc_old = (tc / "a.txt").read_bytes()
        git(tc, "status")
        (tc / "a.txt").write_bytes(bytes(reversed(tc_old)) if tc_old != tc_old[::-1] else b"Z" * len(tc_old))
        os.utime(tc / "a.txt", ns=(st.st_atime_ns, st.st_mtime_ns))
        def add_gitlink(name):
            c = clone(origin, s4 / name)
            git(c, "update-index", "--add", "--cacheinfo", "160000", git(c, "rev-parse", "HEAD"), "vendor/dep")
            git(c, "commit", "-q", "-m", "a submodule")
            (c / "vendor/dep").mkdir(parents=True)
            return c
        (add_gitlink("gitlink_clone") / "vendor/dep/recovery-notes.txt").write_text("only copy\n")
        add_gitlink("empty_gitlink_clone")
        clone(origin, s4 / "relative_clone")
        rel = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)", "S/relative_clone/task.py"], cwd=root4)
        tagged = clone(origin, s4 / "unreadable_tag_clone")
        git(tagged, "tag", "keep")
        os.chmod(tagged / ".git/refs/tags/keep", 0)
        lend = clone(origin, s4 / "open_elsewhere_lender")
        far = td / "outside4"
        far.mkdir()
        subprocess.run(["git", "clone", "-q", "--shared", str(lend), str(far / "borrower")], check=True, capture_output=True)
        held = subprocess.Popen([sys.executable, "-c", "import sys, time; f = open(sys.argv[1]); print(flush=True); time.sleep(300)", str(far / "borrower/a.txt")], cwd=td, stdout=subprocess.PIPE)
        held.stdout.readline()
        lend2 = clone(origin, s4 / "argv_only_lender")
        subprocess.run(["git", "clone", "-q", "--shared", str(lend2), str(far / "borrower2")], check=True, capture_output=True)
        (far / "borrower2/task.py").write_text("import time\nprint(flush=True)\ntime.sleep(300)\n")
        argvb = subprocess.Popen([sys.executable, str(far / "borrower2/task.py")], cwd=td, stdout=subprocess.PIPE)
        argvb.stdout.readline()
        lend3 = clone(origin, s4 / "dirnamed_lender")
        subprocess.run(["git", "clone", "-q", "--shared", str(lend3), str(far / "borrower3")], check=True, capture_output=True)
        envb = subprocess.Popen([sys.executable, "-c", "import time; print(flush=True); time.sleep(300)"], cwd=td, stdout=subprocess.PIPE, env={**os.environ, "REPO_ROOT": str(far / "borrower3")})
        envb.stdout.readline()
        alt = clone(origin, s4 / "alternate_tag_clone")
        git(alt, "tag", "before-alternate-migration")
        os.chmod(alt / ".git/refs/tags/before-alternate-migration", 0)
        clone(origin, s4 / "dotdot_clone")
        dd = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)", f"{s4}/view/../dotdot_clone/task.py"], cwd=td)
        sub = clone(origin, s4 / "subject_clone")
        dated(sub, "a.txt", "theirs\n", "same\x02suffix", "2020-01-02T03:04:05Z")
        sessions = sessions_root(root4)
        hazy = sessions / "11111111-2222-3333-4444-555555555555"
        hazy_clone = clone(origin, hazy / "scratchpad/inner")
        (hazy / "closed").mkdir()
        empty = sessions / "66666666-7777-8888-9999-aaaaaaaaaaaa"
        (empty / "scratchpad").mkdir(parents=True)
        (empty / "scratchpad/TODO-rescue-colony").write_text("")
        wt = td / "wt4"
        wt.mkdir()
        (wt / ".git").write_text("gitdir: ../no_such_repo.git\n")
        for c in [*s4.iterdir(), hazy, empty]:
            age(c)
        os.chmod(hazy / "closed", 0)
        table = td / "mountinfo4"
        table.write_text(f"36 35 8:1 / {mnt}/cache rw - ext4 /dev/x rw\n40 35 8:1 / /other\\040place rw - ext4 /dev/x rw\n"
                         f"41 35 8:1 / {s4}/view rw - ext4 /dev/x rw\n42 35 8:1 / / rw - ext4 /dev/x rw\n")
        real_table, R.MOUNTINFO = R.MOUNTINFO, str(table)
        rc, rows = run_reaper()
        v = {k: r["verdict"] for k, r in rows.items()}
        why = {k: " | ".join(r["why"]) for k, r in rows.items()}
        check(v.get("mounted_clone") == "REFUSE" and "mount" in why["mounted_clone"], "a mount inside holds its candidate")
        check(v.get("under_bind_clone") == "REFUSE" and "mount" in why["under_bind_clone"], "a bind above a candidate holds it")
        check(v.get("socket_clone") == "REFUSE" and "socket" in why["socket_clone"], "a listening socket holds its candidate")
        check(v.get("mapped\nclone") == "REFUSE" and "uses" in why["mapped\nclone"], "a mapping under a name with a newline holds")
        check(v.get("foldcase_clone") == "ARCHIVE" and "NOTES.txt" in rows["foldcase_clone"]["dirty"], "core.ignorecase hides no untracked file")
        check(v.get("trustctime_clone") == "ARCHIVE" and "a.txt" in rows["trustctime_clone"]["dirty"], "core.trustctime hides no edit")
        check(v.get("gitlink_clone") == "REFUSE" and "submodule" in why["gitlink_clone"], "a file in an uninitialised submodule's dir holds")
        check(v.get("empty_gitlink_clone") == "ARCHIVE", "an empty gitlink dir stops nothing")
        check(v.get("relative_clone") == "REFUSE" and "uses" in why["relative_clone"], "a script named relative to a cwd holds its clone")
        check(v.get("unreadable_tag_clone") == "REFUSE" and "refs" in why["unreadable_tag_clone"], "a ref git warns past holds")
        check(v.get("open_elsewhere_lender") == "REFUSE" and "pid" in why["open_elsewhere_lender"], "a borrower with only an open file keeps its lender")
        check(v.get("argv_only_lender") == "REFUSE" and "borrows" in why["argv_only_lender"], "a borrower known only by its argv keeps its lender")
        check(v.get("alternate_tag_clone") == "REFUSE" and "refs" in why["alternate_tag_clone"], "a ref named like the lender's error still holds")
        check(v.get("dirnamed_lender") == "REFUSE" and "borrows" in why["dirnamed_lender"], "a borrower named only by a variable keeps its lender")
        check(v.get("dotdot_clone") == "REFUSE" and "uses" in why["dotdot_clone"], "an absolute argv through `..` holds its clone")
        check(rows.get("subject_clone", {}).get("unique") == 2, "a mark inside a subject makes no twin of main's commit")
        check(v.get("index_clone") == "ARCHIVE", "a staged index is preserved")
        check(v.get("replaced_clone") == "ARCHIVE" and rows["replaced_clone"]["unique"] == 2, "a replace ref hides no commit")
        check(v.get("global_filter_clone") == "REFUSE" and "filter" in why["global_filter_clone"], "a filter from the global config is held")
        check(v.get(hazy.name) == "REFUSE" and "inner" not in rows and hazy_clone.exists(),
              "an unreadable session offers none of its clones")
        check(v.get(empty.name) == "ARCHIVE", "an empty file with a name is residue")
        check("a\rb.txt" in rows["carriage_clone"]["dirty"], "a carriage return survives into the dirty list")
        mapper.kill()
        mapper.wait()
        rel.kill()
        rel.wait()
        dd.kill()
        dd.wait()
        held.kill()
        held.wait()
        argvb.kill()
        argvb.wait()
        envb.kill()
        envb.wait()
        os.chmod(alt / ".git/refs/tags/before-alternate-migration", 0o644)
        os.chmod(tagged / ".git/refs/tags/keep", 0o644)
        fresh = td / "ctime4"
        fresh.mkdir()
        age(fresh)
        R.CTIME_COUNTS = True
        check(time.time() - R.Tree(fresh).newest < 60, "a copy keeping old mtimes is young by its ctime")
        R.CTIME_COUNTS = False
        table.write_text(f"36 35 8:1 / {root4} rw - ext4 /dev/x rw\n")
        check(R.Ctx(time.time()).mounted(s4 / "foldcase_clone"), "a mount exactly at a reap root holds")
        table.write_text("")
        listener.close()
        (sock_c / "s").unlink()
        here = os.getcwd()
        os.chdir(mapped)
        check(R.Live(time.time()).users(mapped), "this job's own cwd holds a candidate")
        os.chdir(here)
        real_sockets, R.UNIX_SOCKETS = R.UNIX_SOCKETS, str(td / "no_socket_table")
        check(any("unix sockets" in b for b in R.Live(time.time()).blind), "no socket table is a blind spot")
        R.UNIX_SOCKETS = real_sockets
        d1 = R.commit_digests(idx, "-1")
        check(d1 and len(d1) == 1, "the digests read a commit whose subject holds nothing odd")
        nasty = clone(origin, td / "nasty4")
        dated(nasty, "a\x01b.txt", "x", "odd", "2020-01-02T03:04:05Z")
        d2 = R.commit_digests(nasty, "-1")
        check(d2 and len(d2) == 1 and list(d2.values())[0][0].endswith("odd"), "a path holding a mark splits no record")
        tar_tree = td / "tar4"
        tar_tree.mkdir()
        (tar_tree / "unique.log").write_text("only copy\n")
        (tar_tree / "notes.txt").write_text("n\n")
        os.environ["TAR_OPTIONS"] = "--exclude=*.log"
        R.make_tar(tar_tree, None, td / "tar4.tgz")
        del os.environ["TAR_OPTIONS"]
        check("unique.log" in tree_names(td / "tar4.tgz"), "TAR_OPTIONS leaves nothing out")
        real_fsync = os.fsync

        def eio(fd):
            raise OSError(errno.EIO, "gone")

        os.fsync = eio
        try:
            R.durable(td, False)
            check(False, "a directory fsync that failed is not forgiven")
        except OSError:
            check(True, "a directory fsync that failed is not forgiven")

        def einval(fd):
            raise OSError(errno.EINVAL, "no")

        os.fsync = einval
        R.durable(td, False)
        os.fsync = real_fsync
        R.MOUNTINFO = str(td / "no_mount_table")
        ctx = R.Ctx(time.time())
        check("mount table" in " ".join(ctx.mounted(s4)), "no mount table holds")
        R.MOUNTINFO = str(table)

        # the index comes back whole
        ctx = R.Ctx(time.time())
        synced, real_durable = [], R.durable
        R.durable = lambda p, must_sync=True: (synced.append((Path(p).name, must_sync)), real_durable(p, must_sync))[1]
        p = Path(R.preserve(dict(R.judge_clone(idx, ctx))))
        R.durable = real_durable
        check({("manifest.json", True), ("index.txt", True), ("staged.tar.gz", True)} <= set(synced), "every archive file is synced before the source goes")
        back = td / "restored4"
        subprocess.run(["git", "clone", "-q", "-b", "index_base", str(origin), str(back)], check=True, capture_output=True)
        blobs = td / "blobs4"
        blobs.mkdir()
        subprocess.run(["tar", "-xzf", str(p / "staged.tar.gz"), "-C", str(blobs)], check=True)
        for b in [f for f in blobs.rglob("*") if f.is_file()]:
            git(back, "hash-object", "-w", "--no-filters", str(b))
        git(back, "read-tree", "--empty")
        subprocess.run(["git", "-C", str(back), "update-index", "-z", "--index-info"], input=(p / "index.txt").read_bytes(), check=True)
        ls = ["git", "ls-files", "-s", "-z"]
        check(subprocess.run(ls, cwd=back, capture_output=True).stdout == subprocess.run(ls, cwd=idx, capture_output=True).stdout,
              "the manifest's steps rebuild modes, a symlink and a deletion exactly")

        # a touch of the top, a walk cut short, a repo not there
        age(cr)
        ctx = R.Ctx(time.time())
        row = R.judge_clone(cr, ctx)
        pin = cr.with_name(".reaping-9-carriage_clone")
        os.rename(cr, pin)
        check(not R.pinned_holds(cr, pin, row, ctx), "an untouched pin passes")
        os.utime(pin)
        check("not the tree" in " ".join(R.pinned_holds(cr, pin, row, ctx)), "a touch of the top is a change")
        os.rename(pin, cr)
        age(cr)
        ctx = R.Ctx(time.time())
        row = R.judge_clone(cr, ctx)
        os.rename(cr, pin)
        mode = pin.stat().st_mode & 0o777
        os.chmod(pin, 0o700 if mode != 0o700 else 0o750)
        check("not the tree" in " ".join(R.pinned_holds(cr, pin, row, ctx)), "a new mode on the top is a change")
        os.chmod(pin, mode)
        os.rename(pin, cr)
        age(cr)
        ctx = R.Ctx(time.time())
        row = R.judge_clone(cr, ctx)
        stand = clone(origin, s4 / "standin4")
        age(stand)
        real_holds, ctx2 = R.pinned_holds, R.Ctx(time.time())
        row2 = R.judge_clone(stand, ctx2)
        R.pinned_holds = lambda p, pin2, r, c: (p.mkdir(), ["someone"])[1]
        fails2 = []
        R.act(row2, ctx2, fails2)
        R.pinned_holds = real_holds
        check(stand.is_dir() and not any(stand.iterdir()) and fails2 and "stands there" in fails2[0], "a dir made during the pin is not swallowed by the unpin")
        roll = s4 / "roll_a"
        roll.mkdir()
        R.rename_new(roll, s4 / "roll_b")
        check((s4 / "roll_b").is_dir() and not roll.exists(), "rename_new moves a dir to a free name")
        roll.mkdir()
        try:
            R.rename_new(roll, s4 / "roll_b")
            refused = False
        except FileExistsError:
            refused = True
        check(refused and roll.is_dir(), "rename_new will not replace an empty dir")
        lv = object.__new__(R.Live)
        lv.blind, lv.paths = [], []
        lv._lenders(str(s4 / "no_such_named_dir"), quiet=True)
        check(not lv.blind, "a named dir that is no repo says nothing")
        bare_q = s4 / "quiet_repo"
        (bare_q / "objects/info").mkdir(parents=True)
        (bare_q / "HEAD").write_text("ref: refs/heads/main\n")
        (bare_q / "objects/info/alternates").mkdir()
        lv._lenders(str(bare_q), quiet=True)
        check(lv.blind, "a named repo with unreadable alternates stays blind")
        shutil.rmtree(bare_q)
        wtq = s4 / "quiet_wt"
        wtq.mkdir()
        (wtq / ".git").write_text("gitdir: /nowhere\n")
        os.chmod(wtq / ".git", 0)
        lv.blind.clear()
        lv._lenders(str(wtq), quiet=True)
        os.chmod(wtq / ".git", 0o600)
        check(lv.blind, "a named worktree with an unreadable .git stays blind")
        shutil.rmtree(wtq)
        shortcut_target = s4 / "shortcut_target"
        shortcut_target.mkdir()
        shortcut = td / "shortcut_link"
        shortcut.symlink_to(shortcut_target)
        holder = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)", str(shortcut / "task.py")])
        try:
            time.sleep(0.3)
            check(R.Live(time.time()).users(shortcut_target), "a process naming a clone through a symlink holds it")
        finally:
            holder.kill()
            holder.wait()
        (shortcut_target / "src").mkdir()
        dotted = td / "dotted_link"
        dotted.symlink_to(shortcut_target / "src")
        holder = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)", f"{dotted}/../tools/w.py"])
        try:
            time.sleep(0.3)
            check(R.Live(time.time()).users(shortcut_target), "a symlink before a dot-dot names the real dir")
        finally:
            holder.kill()
            holder.wait()
        (shortcut_target / "bare_word").mkdir()
        holder = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)", f"--repo={shortcut_target}", f"-I{shortcut_target}/attached"],
                                  env={**os.environ, "CPPFLAGS": f"-O2 -I{shortcut_target}/flagged -isystem{shortcut_target}/longflag",
                                       "RELDIR": "../shortcut_target/rel", "BAREDIR": "bare_word",
                                       "RELFLAG": "-I../shortcut_target/relflag"},
                                  cwd=shortcut_target)
        try:
            time.sleep(0.3)
            named = R.Live(time.time()).named
            check(os.path.realpath(shortcut_target) in named, "an option's value names a dir")
            check(os.path.realpath(shortcut_target / "attached") in named, "an attached short option names a dir")
            check(os.path.realpath(shortcut_target / "flagged") in named, "a flag in a variable names a dir")
            check(os.path.realpath(shortcut_target / "longflag") in named, "a long attached flag names a dir")
            check(os.path.realpath(shortcut_target / "rel") in named, "a relative path in a variable names a dir")
            check(os.path.realpath(shortcut_target / "relflag") in named, "a relative attached flag names a dir")
            check(os.path.realpath(shortcut_target / "bare_word") in named, "a bare word that is a dir there names it")
        finally:
            holder.kill()
            holder.wait()
        shutil.rmtree(shortcut_target)
        shutil.rmtree(s4 / "roll_b")
        roll.rmdir()
        reflogged = clone(origin, s4 / "reflog4")
        (reflogged / "only.txt").write_text("x\n")
        git(reflogged, "add", "only.txt")
        git(reflogged, "commit", "-qm", "only here")
        lost = git(reflogged, "rev-parse", "HEAD")
        git(reflogged, "reset", "-q", "--hard", "HEAD~1")
        logf = reflogged / ".git/logs/HEAD"
        logf.write_text("".join(ln for ln in logf.read_text(errors="replace").splitlines(True) if not ln.split()[1] == lost))
        reflog_b = reflogged / ".git/logs/refs/heads"
        for q in reflog_b.rglob("*"):
            if q.is_file():
                q.write_text("".join(ln for ln in q.read_text(errors="replace").splitlines(True) if not ln.split()[1] == lost))
        check(lost in R.reflog_tips(reflogged)[0], "a reflog entry's old value is a tip")
        age(cr)
        real_preserve, R.preserve = R.preserve, lambda r: os.chmod(r["path"], mode) or "x"
        fails = []
        R.act(row, ctx, fails)
        R.preserve = real_preserve
        check(cr.exists() and row["verdict"] == "REFUSE" and "top changed" in " ".join(row["why"]), "a same-mode chmod during preservation stops the pin")
        os.rename(cr, pin)
        for states, want, says in ((["Z"], True, "a zombie holds nothing"), (["Z", "Z"], True, "a zombie group holds nothing"),
                                   (["Z", "S"], False, "a zombie leader with a running thread is still a process"), ([], False, "no threads read is no proof")):
            proc = Path(tempfile.mkdtemp(dir=str(pin.parent)))
            for i, st in enumerate(states):
                (proc / "task" / str(i)).mkdir(parents=True)
                (proc / "task" / str(i) / "stat").write_text(f"{i} (a) b) {st} 1 1\n")
            check(R.dead(str(proc)) is want, says)
            shutil.rmtree(proc)
        real_run, R.subprocess.run = R.subprocess.run, lambda *a, **k: (_ for _ in ()).throw(subprocess.TimeoutExpired("find", 900))
        try:
            late = R.Borrows()
        finally:
            R.subprocess.run = real_run
        check(late.hold and "partial" in late.hold[0], "a borrower walk that times out is a hold, not a crash")
        real_of, R.Borrows.of = R.Borrows.of, lambda self, p: ["a borrower arrived"]
        check("a borrower arrived" in R.pinned_holds(cr, pin, row, ctx), "a borrower found at the last look holds")
        R.Borrows.of = real_of
        real_cap, R.WALK_CAP = R.WALK_CAP, 1
        check("cap" in " ".join(R.pinned_holds(cr, pin, row, ctx)), "a capped last look proves nothing")
        R.WALK_CAP = real_cap
        os.rename(pin, cr)
        live = object.__new__(R.Live)
        live.blind, live.paths = [], []
        check(live._repo_of(str(wt)) is None and live.blind, "a gitdir that is not there is blind")

        # a file whose name carries a return reaches the tar
        age(cr)
        rc, rows = run_reaper("--apply")
        with tarfile.open(Path(rows["carriage_clone"]["archive"]) / "dirty.tar.gz") as t:
            names = t.getnames()
        check(any(n.endswith("a\rb.txt") for n in names) and not cr.exists(),
              "a name with a return is in the tar")
        R.MOUNTINFO = real_table
    finally:
        os.chmod(hazy / "closed", 0o700)
        for k, val in saved.items():
            if val is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = val


def clone_old(origin, dest):
    c = clone(origin, dest)
    age(c)
    return c


if __name__ == "__main__":
    sys.exit(main())
