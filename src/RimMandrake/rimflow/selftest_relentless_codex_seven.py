#!/usr/bin/env python3
"""RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN: the Codex full-file review's findings on relentless.py, each row red without
its fix. #1 (a product file named by the proof) lives in selftest_relentless.py t_review_wrong_verdicts; #7 (an owed
GREEN-FULL with no proof line) in selftest_relentless_game.py t_owed_final_joins_the_clauses."""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R  # noqa: E402

FAILS = []
RULES = R.rules()


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def bind(obj, *names):
    for n in names:
        setattr(obj, n, types.MethodType(getattr(R.Effects, n), obj))
    return obj


def git(cwd, *a):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, check=True,
                   capture_output=True, text=True, stdin=subprocess.DEVNULL)


def t_empty_commit_is_no_proof():
    """#2: an empty commit above the weak sha, with the contract the WEAK was found on, moved no proof."""
    class Fx:
        moved = []
        def changed(self, b, s, i): return self.moved
        def existed(self, sha, p): return False
    k0 = {"proof": "python3 selftest_x.py", "live": None, "by_gen": 1, "why": "w"}
    st = {"item": "I", "contract": dict(k0), "proof_only": {"sha": "A", "contract": dict(k0)}}
    k, why = R.proof_gate(Fx(), RULES, st, {"sha": "B"})
    ok(k == "proof_unchanged", "an empty commit with the weak contract is proof_unchanged: %s %s" % (k, why))
    st["contract"]["proof"] = "python3 selftest_x.py --strict"
    ok(R.proof_gate(Fx(), RULES, st, {"sha": "B"})[0] is None, "a changed contract on an empty commit is a new proof")
    st["contract"] = dict(k0)
    fx = Fx()
    fx.moved = ["src/selftest_x.py"]
    ok(R.proof_gate(fx, RULES, st, {"sha": "B"})[0] is None, "a moved proof file is a new proof")
    st = {"item": "I", "contract": dict(k0), "proof_only": {"sha": "A"}}
    ok(R.proof_gate(Fx(), RULES, st, {"sha": "B"})[0] is None, "an older hold with no contract snapshot is read as before")
    st = {"item": "I", "contract": dict(k0), "proof_only": {"sha": "A", "contract": dict(k0), "binding": True}}
    ok(R.proof_gate(Fx(), RULES, st, {"sha": "B"})[0] is None,
       "a binding repair may live off the sha (a ledger criterion): not refused for an empty commit")


def t_gitless_clone_is_kept():
    """#3: a pool clone with no .git is moved aside whole, never deleted with its untracked files."""
    base = tempfile.mkdtemp(prefix="cx7_")
    try:
        store = R.Store(base)
        os.makedirs(store.p("items", "I0"))
        fake = bind(types.SimpleNamespace(base=base, store=store, r={}), "keep_gitless", "remove_clone")
        c = os.path.join(base, "clones", "I0")
        os.makedirs(os.path.join(c, "src"))
        with open(os.path.join(c, "src", "work.py"), "w") as f:
            f.write("only copy\n")
        out = fake.remove_clone({"item": "I0", "clone": c})
        ok(out is None and not os.path.exists(c), "the clone folder is gone from the pool")
        kept = [os.path.join(dp, f) for dp, _, fs in os.walk(store.p("items", "I0", "gitless")) for f in fs]
        ok(len(kept) == 1 and open(kept[0]).read() == "only copy\n", "its untracked file is kept: %s" % kept)
        os.makedirs(os.path.join(c, "empty"))
        ok(fake.keep_gitless("I0", c) == (None, None), "a tree with no file has nothing to keep")
        os.symlink(base, os.path.join(c, "empty", "assets"))
        got, _ = fake.keep_gitless("I0", c)
        ok(got and os.path.islink(os.path.join(got, "empty", "assets")), "a tree holding only a dir symlink is kept: %s" % got)
        os.makedirs(c)
        with open(os.path.join(c, "x"), "w") as f:
            f.write("y")
        fake.store = types.SimpleNamespace(p=lambda *a: os.path.join("/proc/nonexistent_cx7", *a))
        got, why = fake.keep_gitless("I0", c)
        ok(got is None and why and os.path.exists(os.path.join(c, "x")), "a tree that cannot move stays: %s" % why)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_merge_lists_what_it_brought():
    """#4: a merge commit names the paths it brought in (first parent), for work_sha and the live-check selection."""
    d = tempfile.mkdtemp(prefix="cx7m_")
    try:
        git(d, "init", "-q", "-b", "main")
        git(d, "commit", "-q", "--allow-empty", "-m", "a")
        git(d, "checkout", "-q", "-b", "f")
        with open(os.path.join(d, "hook.py"), "w") as f:
            f.write("x\n")
        git(d, "add", "hook.py")
        git(d, "commit", "-q", "-m", "OTHER_ITEM: hook", "hook.py")
        git(d, "checkout", "-q", "main")
        with open(os.path.join(d, "doc.md"), "w") as f:
            f.write("y\n")
        git(d, "add", "doc.md")
        git(d, "commit", "-q", "-m", "c", "doc.md")
        git(d, "merge", "-q", "--no-ff", "-m", "I0: merge", "f")
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()
        fake = bind(types.SimpleNamespace(books=d), "git", "touched", "changed")
        ok(fake.touched(sha) == ["hook.py"], "touched names the merged hook: %s" % fake.touched(sha))
        ok("hook.py" in fake.changed(None, sha, "I0"), "changed names the merged hook: %s" % fake.changed(None, sha, "I0"))
        ok(fake.touched(sha + "~1") == ["doc.md"], "a plain commit is read as before")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_deleted_shard_is_refused_by_name():
    """#5: a tracked ledger shard deleted from the working tree is refused, not a FileNotFoundError."""
    shard = R.LEDGER_DIR + "X.jsonl"
    outs = {"rev-list": "1", "status": " D %s\0" % shard, "diff": ""}
    fake = types.SimpleNamespace(books=tempfile.gettempdir(), git_ok=lambda c, *a: outs[a[0]],
                                 shuffled_shards=lambda rows: {}, drop_stray_untracked=lambda rows: rows)
    bind(fake, "level_books")
    try:
        why = fake.level_books()
    except FileNotFoundError as e:
        why = "raised %s" % e
    ok(why and "deleted" in why and shard in why, "refused by name: %s" % why)


def t_cooling_system_item_pauses_nothing():
    """#6: a queued system item cooling after a refused start, or out on a consult, waits on no place."""
    now = time.time()
    fx = types.SimpleNamespace(first={"SYS": 1}, pause_scope={"global": None, "lanes": ["x"]})
    q = {"item": "SYS", "status": "queued"}
    ok(R.content_pause(fx, [dict(q)], now=now) is not None, "a system item waiting for a place pauses content")
    ok(R.content_pause(fx, [dict(q, start_again_at=now + 3600)], now=now) is None, "one cooling does not")
    ok(R.content_pause(fx, [dict(q, help={"status": "running"})], now=now) is None, "one on a consult does not")
    ok(R.content_pause(fx, [dict(q, start_again_at=now - 1)], now=now) is not None, "a cooldown run out pauses again")


def t_r3_review_rows():
    """The r3 re-review (review/r3/rev_part*.txt), each row red without its fix."""
    import calendar
    import json
    d = tempfile.mkdtemp()
    try:
        store = R.Store(d)
        item = "I3"
        os.makedirs(store.item_dir(item))
        # p0.4: a torn last line (no newline) must not swallow the next record
        p = os.path.join(store.item_dir(item), "attempts.jsonl")
        with open(p, "w") as f:
            f.write('{"end": "worker_lost"')
        store.attempt(item, {"end": "kept"})
        ok([a.get("end") for a in store.attempts(item)] == ["kept"], "p0.4 a record after a torn line survives")
        # p0.2: an older proof_weak that reads PASS never speaks for a newer PROOF_OWED hold
        os.remove(p)
        pass_detail = "GAP:OTHER: the checker wrote a mutant in another file entirely"
        ok(R.relentless_wall.acted_weak("WEAK", pass_detail) == "PASS", "p0.2 precondition: the detail reads PASS")
        store.attempt(item, {"end": "proof_weak", "sha": "S", "detail": pass_detail})
        st = {"item": item, "proof_only": {"sha": "S"}}
        ok(R.weak_reads_pass(st, store), "p0.2 a lone legacy proof_weak reading PASS still reads PASS")
        store.attempt(item, {"end": R.relentless_attrib.PROOF_OWED, "sha": "S", "detail": "repair the proof"})
        ok(not R.weak_reads_pass(st, store), "p0.2 a newer PROOF_OWED at the sha is not read through the old WEAK")
        # p0.1: a day file with a non-dict basis blocks spending; a failed write raises instead of reading low
        now = time.time()
        with open(store.p("spend-%s.json" % R.day_key(now)), "w") as f:
            json.dump({"spent": 0, "runs": {}, "basis": []}, f)
        ok(R.spent_today(store, now) == R.UNREADABLE_SPEND, "p0.1 a list basis is an unreadable day, not an empty one")
        os.remove(store.p("spend-%s.json" % R.day_key(now)))

        def boom(path, text):
            raise OSError("disk full")
        real = store._write
        store._write = boom
        raised = False
        try:
            R.charge(store, {"spent": 0}, 100, now, RULES, "u1", "stream")
        except OSError:
            raised = True
        store._write = real
        ok(raised, "p0.1 a charge that cannot be booked raises")
        ok(R.charge(store, {"spent": 0}, 100, now, RULES, "u2", "stream") == 100 and R.spent_today(store, now) == 100,
           "p0.1 a booked charge reads back")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # p0.5: undecodable fixture output is replaced, not raised
    rc, tail = R.run_fixture_cmd("%s -c 'import os; os.write(1, bytes([255]))'" % sys.executable, None, 30)
    ok(rc == 0 and tail, "p0.5 undecodable output returns (exit %s)" % rc)
    # p0.3: a re-submitted identical contract (new by_gen/why) on an empty commit is no proof
    class Fx:
        def changed(self, b, s, i): return []
        def existed(self, sha, p): return False
    k0 = {"proof": "python3 selftest_x.py", "live": None, "by_gen": 1, "why": "w"}
    st = {"item": "I", "contract": dict(k0, by_gen=2, why="again"), "proof_only": {"sha": "A", "contract": dict(k0)}}
    ok(R.proof_gate(Fx(), RULES, st, {"sha": "B"})[0] == "proof_unchanged", "p0.3 bookkeeping-only contract change")
    # p2.1: a bad title pattern is skipped, never raised
    it = types.SimpleNamespace(id="X", title="anything")
    try:
        got = R.hand_check(it, {"hand_check": {"title_rx": ["[", "any"]}})
    except Exception as e:      # noqa: BLE001
        got = e
    ok(isinstance(got, str), "p2.1 a bad regex is skipped and the next one still matches: %r" % (got,))
    # p3.3: ts_epoch is UTC whatever the local DST
    old = os.environ.get("TZ")
    os.environ["TZ"] = "America/Los_Angeles"
    time.tzset()
    try:
        want = calendar.timegm((2026, 7, 1, 12, 0, 0, 0, 0, 0))
        ok(R.ts_epoch("2026-07-01T12:00:00Z") == want, "p3.3 a summer ledger ts is read as UTC")
    finally:
        if old is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = old
        time.tzset()


def t_r7_high_rows():
    """The r7 graded review's HIGH claims that held (review/r7/triage.md), each red without its fix."""
    import selftest_relentless as T
    import selftest_relentless_resume as SR
    real = R.tree_present
    R.tree_present = lambda p: True
    # a verdict file first read past the check's deadline used to raise Fenced on every tick, for ever (whole #2)
    x = T.Rig(n=1, share=1.0, same_failure_limit=5)
    try:
        st = SR.to_check(x)
        nonce = st["check"]["nonce"]
        box = os.path.join(x.d, "box")
        os.makedirs(box)
        with open(os.path.join(box, "verdict.json"), "w") as f:
            f.write('{"word": "PASS", "reasons": "ran it"}')
        with x.s.lock():
            cur = x.s.load(SR.ITEM)
            cur["check"].update(box=box, deadline=x.now - 1)
            x.s.save(cur)
        x.w.up[st["check"]["run"]["unit"]] = False
        for _ in range(4):
            x.tick(7200)
        cur = x.st(SR.ITEM)
        ok((cur.get("check") or {}).get("nonce") != nonce,
           "a verdict file read past its deadline ends that check instead of trapping it: %s" % cur["status"])
        ok((cur.get("check") or {}).get("verdict") != "PASS", "and a late verdict is still no verdict")
    finally:
        x.done()
        R.tree_present = real
    # two checkers cut by the account over the cap each counted the other and waited for ever (whole #3)
    R.tree_present = lambda p: True
    x = T.Rig(n=1, share=1.0, same_failure_limit=5)
    try:
        st = SR.to_check(x)
        with x.s.lock():
            cur = x.s.load(SR.ITEM)
            cur["check"]["resume"] = {"session": SR.SID, "at": x.now}
            x.s.save(cur)
            twin = dict(cur, item="I1")
            x.s.save(twin)
        n = len(x.w.launches)
        acts = []
        r = dict(x.r, max_workers=1, staffing=None, day_spend_limit=10 ** 12)
        R.check_resume(x.s, x.w, r, SR.ITEM, x.now, acts)
        ok(len(x.w.launches) == n + 1 and "resume" not in x.st(SR.ITEM)["check"],
           "a cut checker resumes though its peers fill the cap: %s" % acts)
        fx = types.SimpleNamespace(paused=lambda: False, mem_gb=lambda: 64.0)
        ok(R.admission(x.s, fx, r, x.now, 9) == "max_workers", "the instrument can see: a new run over the cap still waits")
    finally:
        x.done()
        R.tree_present = real
    # a binding repair approved while closing moved the contract under a PASS of the old one (whole #1)
    base = tempfile.mkdtemp(prefix="cx7_")
    try:
        s = R.Store(base)
        st = R.new_state("I0", 1000.0, "t")
        st.update(status="running", gen=1, approach="build")
        with s.lock():
            s.save(st)
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", obligation="the gourd selects", r=RULES)
        R.rebind(s, "I0", 1, {"proof": "python3 a/selftest_y.py"},
                 {"before": "ran x, gone", "after": "runs y, same rows", "behaviour": "same", "defect": "x is gone"}, r=RULES)
        with s.lock():
            cur = s.load("I0")
            cur["status"] = "closing"
            s.save(cur)
        try:
            R.bind_judge(s, "I0", "rm-judge", "approve", "same rows", env={}, r=RULES, cwd=base)
            ok(False, "a closing item takes no binding repair")
        except ValueError as e:
            ok("closing" in str(e), "a closing item takes no binding repair: %s" % str(e)[:60])
        ok(s.load("I0")["contract"]["proof"] == "python3 a/selftest_x.py", "and its contract does not move")
        with s.lock():
            cur = s.load("I0")
            cur["status"] = "running"
            s.save(cur)
        R.bind_judge(s, "I0", "rm-judge", "approve", "same rows", env={}, r=RULES, cwd=base)
        ok(s.load("I0")["contract"]["proof"] == "python3 a/selftest_y.py", "the instrument can see: a running item's repair still moves")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    for t in (t_empty_commit_is_no_proof, t_gitless_clone_is_kept, t_merge_lists_what_it_brought,
              t_deleted_shard_is_refused_by_name, t_cooling_system_item_pauses_nothing, t_r3_review_rows,
              t_r7_high_rows):
        print("--", t.__name__)
        t()
    print("selftest_relentless_codex_seven: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
