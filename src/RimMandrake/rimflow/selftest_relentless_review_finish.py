#!/usr/bin/env python3
"""selftest_relentless_review_finish.py — relentless.py defects from its full-file review
(RELENTLESS_REVIEW_FINISH_TOO_BIG_TO_SKIM). Each check fails on the code before the fix.

1. lease(): a full pool that has no room for the top item's NEW clone does not stop an item further down that already
   has its own clone: that one starts (its kept commits are what would free room), and the pool wait is said once.
2. staffing(): content stopped by the owner's token pause (only_system_and_live) is not ready work, so the pause reads
   as no under-staffing and raises no staffing or jam alarm.
3. step(): a checker clone a retry lets go (its launch failed, the account change-over killed it) is removed, not left
   in the pool as an orphan it protects for an hour.
4. level_books: a set-equal reordered shard (code_review, art) that gains a line after shuffled_shards looked refuses
   the level instead of being overwritten with HEAD.
5. level_books: a line appended to that shard AFTER _level_rows' first look but before the restore (the window the
   unlocked restore left open, SHARD_LEVEL_FIX_APPEND_LOST_MIDRESTORE) is kept: compare and restore run under the
   shard's flock, and the writers (code_review_status, artledger) take that flock and follow a replaced inode; the
   level also holds their directories EXCLUSIVE (writers take them SHARED) across restore and reset, clean shards too.

Runs on selftest_relentless's FakeWorld; no ledger, clone or unit is touched.

    python3 src/RimMandrake/rimflow/selftest_relentless_review_finish.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import selftest_relentless as SR    # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def t_pool_full_lets_a_cloned_item_run():
    x = SR.staffed(n=2)
    x.w.pool = {"/c/L%d" % i: {"busy": True} for i in range(10)}
    x.tick()
    ok(not x.w.launches and {x.st("I0")["status"], x.st("I1")["status"]} == {"queued"},
       "fixture: both items queued, nothing starts in a full pool of live clones")
    # the lower item gets its own clone back (kept commits), in place of a live one: the pool stays at its cap
    del x.w.pool["/c/L0"]
    mine = x.w.clone_path("I1", len(x.st("I1")["quarantined"]))
    x.w.pool[mine] = {"kept": True}
    st = x.st("I1")
    st["clone"] = mine          # a put-down run's clone, kept for its commits
    x.s.save(st)
    acts = x.tick()
    started = [l[0] for l in x.w.launches]
    ok(started == ["I1"], "the item that has its clone starts though the top one has no room: %s" % started)
    waits = [a for a in acts or [] if isinstance(a, dict) and a.get("do") == "wait"
             and str(a.get("why", "")).startswith(("pool full", "pool at"))]
    ok(len(waits) <= 1, "the pool wait is said at most once a tick: %s" % waits)
    ok(x.st("I0")["status"] == "queued", "the top item keeps its place in line")
    x.done()


def t_owner_pause_is_not_under_staffing():
    x = SR.staffed(n=3)
    x.r["only_system_and_live"] = True      # the owner's token pause; FakeWorld has no system items
    x.tick()
    r = SR.reading(x)
    ok(not x.w.launches, "fixture: the pause starts no content")
    ok(r["ready"] == 0 and not r["under"], "content stopped by the pause is not ready, so not under-staffed: ready %s "
       "under %s why %s" % (r["ready"], r["under"], r.get("why")))
    x.tick(), x.tick()
    ok(not x.w.alarms and not x.w.jams, "no staffing or jam alarm for a pause he chose: %s %s" % (x.w.alarms, x.w.jams))
    x.done()


def to_check(x, i):
    """Run `i` to its finish, so the next ticks start its check."""
    x.run_one(i)
    st = x.st(i)
    if not st["contract"]:
        SR.R.contract(x.s, i, st["gen"], "proof", live="once: test")
    SR.R.finish(x.s, i, st["gen"], "sha1", "evidence")
    x.w.up[st["run"]["unit"]] = False


def checker_clones(x):
    return sorted(c for c in x.w.pool if "/check-" in c)


def t_checker_clone_let_go():
    # a checker that never launched: its clone goes at once, not an hour later as a fresh orphan
    x = SR.Rig(n=1, share=1.0)
    x.w.pool = {"/c/other": {"busy": True}}
    to_check(x, "I0")
    x.w.lfail = "launch refused"
    x.tick(), x.tick()
    ok(x.st("I0")["status"] == "candidate" and x.st("I0")["check"] is None, "fixture: the check launch failed")
    ok(checker_clones(x) == [], "a checker clone whose launch failed is removed: %s" % checker_clones(x))
    x.done()
    # a checker the account change-over killed: a new checker comes, the old clone does not stay behind
    x = SR.Rig(n=1, share=1.0)
    x.w.pool = {"/c/other": {"busy": True}}
    to_check(x, "I0")
    x.tick(), x.tick()
    st = x.st("I0")
    ok(st["status"] == "checking", "fixture: the check runs")
    x.w.account_sign = {"kind": "account_switch", "why": "change-over killed it"}
    x.w.up[st["check"]["run"]["unit"]] = False
    for _ in range(4):
        x.tick()
        if x.st("I0")["status"] != "checking":
            break
    ok(st["check"]["clone"] not in x.w.pool, "an account-lost checker's clone is removed: %s" % checker_clones(x))
    x.done()


def t_shuffled_shard_append_refused():
    import subprocess
    import tempfile
    d = tempfile.mkdtemp(prefix="rl-shuffle-")
    g = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=d, check=True,
                                  capture_output=True, text=True)
    p = "infrastructure/state/code_review/B.jsonl"
    os.makedirs(os.path.join(d, os.path.dirname(p)))
    g("init", "-q", "-b", "main")
    with open(os.path.join(d, p), "w") as f:
        f.write("a\nb\nc\n")
    g("add", p)
    g("commit", "-qm", "s")
    with open(os.path.join(d, p), "w") as f:
        f.write("c\na\nb\n")
    fx = SR.R.Effects.__new__(SR.R.Effects)
    fx.books = d
    got = fx.shuffled_shards([(" M", p)])
    ok(dict(got) == {p: b"c\na\nb\n"}, "shuffled_shards keeps the bytes it compared: %r" % (got,))
    with open(os.path.join(d, p), "a") as f:     # a writer appends after the look
        f.write("d\n")
    why = fx._level_rows([(" M", p)], {}, os.path.join(d, "keep"), {}, {}, 3, got)
    with open(os.path.join(d, p)) as f:
        now = f.read()
    ok(why and "moved while levelling" in why and now.endswith("d\n"),
       "a line appended after the look refuses the level and is kept: %r %r" % (why, now))
    import shutil
    shutil.rmtree(d, ignore_errors=True)


def _shuffled_repo():
    import subprocess
    import tempfile
    d = tempfile.mkdtemp(prefix="rl-shuffle-")
    g = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=d, check=True,
                                  capture_output=True, text=True)
    p = "infrastructure/state/code_review/B.jsonl"
    os.makedirs(os.path.join(d, os.path.dirname(p)))
    g("init", "-q", "-b", "main")
    with open(os.path.join(d, p), "w") as f:
        f.write("a\nb\nc\n")
    g("add", p)
    g("commit", "-qm", "s")
    with open(os.path.join(d, p), "w") as f:
        f.write("c\na\nb\n")
    return d, p


def t_shuffled_shard_append_mid_restore_kept():
    import shutil
    import subprocess
    d, p = _shuffled_repo()
    fx = SR.R.Effects.__new__(SR.R.Effects)
    fx.books = d
    got = fx.shuffled_shards([(" M", p)])
    real = subprocess.run
    fired = []

    def run(a, *k, **kw):   # the writer arrives while _level_rows reads HEAD's bytes: after its first look, before restore
        r = real(a, *k, **kw)
        if not fired and isinstance(a, list) and "show" in a and ("HEAD:" + p) in a:
            fired.append(1)
            with open(os.path.join(d, p), "a") as f:
                f.write("d\n")
        return r
    subprocess.run = run
    try:    # a level that went on past the restore reaches git and the store this bare fixture lacks: read the file anyway
        why = fx._level_rows([(" M", p)], {}, os.path.join(d, "keep"), {}, {}, 3, got)
    except Exception as e:      # noqa: BLE001
        why = "raised %r" % e
    finally:
        subprocess.run = real
    with open(os.path.join(d, p)) as f:
        now = f.read()
    ok(fired, "fixture: the append fired inside the window")
    ok("d" in now.splitlines(), "a line appended between the look and the restore survives: why=%r file=%r" % (why, now))
    ok(why and "moved while levelling" in why, "and the level refuses: %r" % (why,))
    shutil.rmtree(d, ignore_errors=True)


def _writer_waits_and_follows(name, open_locked):
    import fcntl
    import shutil
    import tempfile
    import threading
    d = tempfile.mkdtemp(prefix="rl-wlock-")
    fp = os.path.join(d, "S.jsonl")
    with open(fp, "w") as f:
        f.write("a\n")
    held = os.open(fp, os.O_RDONLY)
    fcntl.flock(held, fcntl.LOCK_EX)        # the level holds the shard

    def write():
        fd = open_locked(fp)
        try:
            os.write(fd, b"late\n")
        finally:
            os.close(fd)
    t = threading.Thread(target=write)
    t.start()
    t.join(0.4)
    with open(fp) as f:
        before = f.read()
    ok(t.is_alive() and before == "a\n", "%s: an append waits while the shard's flock is held: %r" % (name, before))
    tmp = fp + ".new"                       # git replaces the file meanwhile (a new inode at the path)
    with open(tmp, "w") as f:
        f.write("a\nz\n")
    os.replace(tmp, fp)
    os.close(held)
    t.join(5)
    with open(fp) as f:
        after = f.read()
    ok(not t.is_alive() and after == "a\nz\nlate\n",
       "%s: once released the append lands on the file now at the path: %r" % (name, after))
    shutil.rmtree(d, ignore_errors=True)


def t_writers_take_the_shard_lock():
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils", "art"))
    import code_review_status as CRS
    import artledger as AL
    _writer_waits_and_follows("code_review_status", CRS._open_shard_locked)
    _writer_waits_and_follows("artledger", AL._open_shard_locked)


def t_level_holds_append_dirs():
    """GPT round-4: git's checkout unlinks the shard and writes a new inode, which a writer could lock and append to
    mid-write; and a CLEAN shard origin changes is not in `shuffled` at all. The level holds both directories
    EXCLUSIVE, and the real writers wait on them, shuffled or clean."""
    import shutil
    import tempfile
    import threading
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils", "art"))
    import code_review_status as CRS
    import artledger as AL
    d = tempfile.mkdtemp(prefix="rl-dirs-")
    for x in SR.R.APPEND_ONLY_DIRS:
        os.makedirs(os.path.join(d, x))
    fx = SR.R.Effects.__new__(SR.R.Effects)
    fx.books = d
    cr = os.path.join(d, "infrastructure/state/code_review")
    old_rec, old_env = CRS.REC_DIR, {k: os.environ.get(k) for k in ("ART_LEDGER_DIR", "ART_SEAT")}
    CRS.REC_DIR = cr
    os.environ["ART_LEDGER_DIR"] = os.path.join(d, "infrastructure/state/art")
    os.environ["ART_SEAT"] = "B"        # used only when no RIMFLOW_SEAT resolves first; the path below follows seat()
    art = AL.shard_path()
    try:
        writers = [threading.Thread(target=CRS.append_records, args=([{"path": "x"}], "B")),
                   threading.Thread(target=lambda: (lambda w: (w.add({"kind": "t"}), w.flush()))(AL.Writer(set())))]
        with fx.append_dirs_locked():
            for t in writers:
                t.start()
            for t in writers:
                t.join(0.4)
            held = [os.path.exists(os.path.join(cr, "B.jsonl")), os.path.exists(art)]
            ok(all(t.is_alive() for t in writers) and held == [False, False],
               "no code_review or art append while the level holds their directories: %r" % (held,))
        for t in writers:
            t.join(5)
        ok(not any(t.is_alive() for t in writers) and os.path.getsize(os.path.join(cr, "B.jsonl"))
           and os.path.getsize(art), "and both land once it lets go")
    finally:
        CRS.REC_DIR = old_rec
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    try:
        t_pool_full_lets_a_cloned_item_run()
        t_owner_pause_is_not_under_staffing()
        t_checker_clone_let_go()
        t_shuffled_shard_append_refused()
        t_shuffled_shard_append_mid_restore_kept()
        t_writers_take_the_shard_lock()
        t_level_holds_append_dirs()
    except Exception as e:      # noqa: BLE001  a crash is a FAIL with its reason
        import traceback
        traceback.print_exc()
        FAILS.append("crashed: %s" % e)
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
