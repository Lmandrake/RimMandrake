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
                                 shuffled_shards=lambda rows: {})
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


def main():
    for t in (t_empty_commit_is_no_proof, t_gitless_clone_is_kept, t_merge_lists_what_it_brought,
              t_deleted_shard_is_refused_by_name, t_cooling_system_item_pauses_nothing):
        print("--", t.__name__)
        t()
    print("selftest_relentless_codex_seven: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
