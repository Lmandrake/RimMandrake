#!/usr/bin/env python3
"""RELENTLESS_REVIEW_FIX_ROUND_FIVE_DIGS: the Codex r5 re-review's 21 findings on relentless.py and relentless_game.py
(review files: D:\\ClaudeWork\\rimmandrake\\relentless\\RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN\\review\\r5\\rev_*.txt). 20 were
real and are fixed, each with a row red without its fix; one is rejected. Rows #1-#4 and #19-#21 live in
selftest_relentless_codex_five_b.py and run from here too.

relentless_game.py
  #1  green_stands: a contract row in the same whole second as a fractional offline_green.at reads as after it.  (_b)
  #2  not_measuring: a signal-killed proof (`exited -11`) counts toward the repeat cutoff.                       (_b)
  #3  the stage road waits on an unread game (state None), as the prove road does; it never launches.           (_b)
  #4  _env: an environment row from before the latest staging holds nothing.                                    (_b)
relentless.py
  #5  contract: a proof-only worker may not replace a live line already set (only a redesign, or `rebind`).
  #6  charge: a replay after a crash charges the item what the day booked for that run, never a second figure.
  #7  contract: a widening may not overwrite a scenario already set (a binding repair is `rebind`).
  #8  run_fixture_cmd: a flooding fixture's output is drained to a bounded tail, never buffered whole.
  #9  account_lost: a pilot step whose sitting the account cut stays owed (piloting() stays true).
  #10 REJECTED: proof_gate's unchanged-proof guard reading an old proof_only record (no contract snapshot) as a new
      proof. selftest_relentless_codex_seven pins that on purpose ("an older hold with no contract snapshot is read as
      before"): with no snapshot nothing tells a contract-only repair from none, and failing closed would hold a real
      repair as proof_unchanged, while failing open costs one Marker. Records without a snapshot predate _FOUND_SEVEN.
  #11 hold/unhold: a person's hold of a blocked item lifts back to blocked, its blocker kept.
  #12 hook_fence: a `.git` FILE (linked worktree, submodule) is followed to its git dir, never "marker unreadable".
  #13 shuffled_shards: only the merge=union shard dirs (APPEND_ONLY_DIRS) may be reordered; any other .jsonl is dirt.
  #14 ignored_collision: a symlink (even to a dir) where origin now wants a folder is a collision.
  #15 item_mods: a lone ALL-CAPS mod name in the title is kept; only underscore-joined item ids are stripped.
  #16 saved patches use `git diff --binary --no-textconv --no-ext-diff` (a textconv driver never replaces the bytes).
  #17 keep_gitless: a folder os.walk cannot list is no empty tree: it is kept, never removed.
  #18 restore_commits: a cherry-pick left with an unmerged path (modify/delete) is no "already landed".
  #19 help: a consult whose clone an unreaped quarantine still holds is never resumed there.                    (_b)
  #20 tick: a wake's game pass spends the tick's remaining game budget, never a fresh one.                      (_b)
  #21 tick: a wake that lands during the final flush is left for game_next / the next tick.                     (_b)
"""
import inspect
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import tracemalloc
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


def refused(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def bind(obj, *names):
    for n in names:
        setattr(obj, n, types.MethodType(getattr(R.Effects, n), obj))
    return obj


def git(cwd, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, check=True,
                          capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout.strip()


def rig(**kw):
    base = tempfile.mkdtemp(prefix="cx5_")
    s = R.Store(base)
    st = R.new_state("I0", 1000.0, "t")
    st.update(status="running", gen=1, approach="build", **kw)
    with s.lock():
        s.save(st)
    return base, s


def proof_only(s):
    with s.lock():
        st = s.load("I0")
        st["proof_only"] = {"sha": "x", "at": 1}
        s.save(st)


def t_live_line_kept():
    base, s = rig()
    try:
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", live="once: the first", r=RULES)
        proof_only(s)
        e = refused(R.contract, s, "I0", 1, "python3 a/selftest_y.py", live="once: another", why="change proof", r=RULES)
        ok(e is not None and s.load("I0")["contract"]["live"] == "once: the first",
           "#5 a proof-only worker may not replace the live line: %s" % e)
        R.contract(s, "I0", 1, "python3 a/selftest_y.py", why="change proof", r=RULES)
        ok(s.load("I0")["contract"]["live"] == "once: the first", "#5 a proof change that leaves live out keeps it")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_scenario_kept():
    base, s = rig()
    try:
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", scenario="a dead jawa on a quicktest map", r=RULES)
        e = refused(R.contract, s, "I0", 1, "python3 a/selftest_x.py", live="once: widen", scenario="empty world",
                    why="widen", r=RULES)
        ok(e is not None and "rebind" in e and s.load("I0")["contract"].get("scenario") == "a dead jawa on a quicktest map",
           "#7 a widening may not overwrite the scenario: %s" % e)
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", live="once: widen", why="widen", r=RULES)
        ok(s.load("I0")["contract"].get("live") == "once: widen", "#7 the same widening without a scenario passes")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_charge_replay_takes_the_booked_figure():
    base = tempfile.mkdtemp(prefix="cx5_")
    try:
        store = R.Store(base)
        now = 1793866000.0
        R.charge(store, {"spent": 0}, 1000, now, {"run_reserve": 5000}, "u", "result")     # booked; the item unsaved
        st = {"spent": 0}
        got = R.charge(store, st, 20000, now, {"run_reserve": 5000}, "u", "result")
        with open(store.p("spend-%s.json" % R.day_key(now))) as f:
            d = json.load(f)
        ok(got == 1000 and st["spent"] == 1000 and d["spent"] == 1000,
           "#6 a replayed run is charged what the day booked: got %s item %s day %s" % (got, st["spent"], d["spent"]))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_fixture_output_bounded():
    code = "import sys; [sys.stdout.write('x' * 1048576) for _ in range(40)]; sys.stdout.write('END'); sys.exit(3)"
    tracemalloc.start()
    try:
        rc, tail = R.run_fixture_cmd("%s -c \"%s\"" % (sys.executable, code), None, 120)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    ok(rc == 3 and tail.endswith("END") and len(tail) <= 600, "#8 exit and tail read: %s %r" % (rc, tail[-20:]))
    ok(peak < 8 * 1048576, "#8 40 MB of fixture output never sits in memory: peak %d bytes" % peak)


def t_account_loss_keeps_pilot_step():
    for session in (None, "sess-1"):
        base, s = rig()
        try:
            with s.lock():
                st = s.load("I0")
                st.update(gen=7, pilot_step={"sat_gen": 7, "after": 3})
                ok(R.piloting(st), "#9 setup: gen 7 is the pilot's sitting")
                R.account_lost(s, st, {"why": "the account ran dry", "kind": "usage_limit",
                                       **({"session": session} if session else {})}, RULES, 2000.0)
            st = s.load("I0")
            ok(st["gen"] == 8 and R.piloting(st) and st.get("pilot_step"),
               "#9 session %s: the cut sitting stays owed at gen 8: %s" % (session, st.get("pilot_step")))
            R.pilot_sat(st, "proof_weak")
            ok((st.get("piloted") or 0) == (1 if session else 0),
               "#9 session %s: a later ending consumes the step only if it was sat: piloted=%s" % (session, st.get("piloted")))
        finally:
            shutil.rmtree(base, ignore_errors=True)


def t_hold_of_blocked_keeps_blocker():
    base, s = rig()
    try:
        with s.lock():
            st = s.load("I0")
            st.update(status="blocked", block_pending={"on": "OTHER_ITEM", "kind": "item"})
            s.save(st)
        R.hold(s, "I0", "hold it, his words", now=2000.0)
        R.unhold(s, "I0", "go on", now=2100.0)
        st = s.load("I0")
        ok(st["status"] == "blocked" and st.get("block_pending", {}).get("on") == "OTHER_ITEM",
           "#11 unhold returns a blocked item to its block: %s %s" % (st["status"], st.get("block_pending")))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_hook_fence_follows_git_file():
    base = tempfile.mkdtemp(prefix="cx5_")
    try:
        top, gd = os.path.join(base, "wt"), os.path.join(base, "real.git")
        os.makedirs(top)
        os.makedirs(gd)
        with open(os.path.join(top, ".git"), "w") as f:
            f.write("gitdir: %s\n" % gd)
        store = R.Store(os.path.join(base, "store"))
        ok(R.hook_fence(top, store) is None, "#12 a .git file with no marker in its git dir: not a relentless clone")
        with open(os.path.join(gd, "relentless.json"), "w") as f:
            json.dump({"item": "NOT_ENROLLED_X", "gen": 1}, f)
        old = os.environ.pop("RELENTLESS_GEN", None)
        try:
            why = R.hook_fence(top, store)
        finally:
            if old is not None:
                os.environ["RELENTLESS_GEN"] = old
        ok(why and "not enrolled" in why, "#12 the marker in the git dir the file names is read: %s" % why)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_only_union_shards_reorder():
    d = tempfile.mkdtemp(prefix="cx5_")
    try:
        cr, other = "infrastructure/state/code_review/B.jsonl", "data/order.jsonl"
        git(d, "init", "-q", "-b", "main")
        for p in (cr, other):
            os.makedirs(os.path.join(d, os.path.dirname(p)), exist_ok=True)
            with open(os.path.join(d, p), "w") as f:
                f.write("a\nb\nc\n")
        git(d, "add", cr, other)
        git(d, "commit", "-qm", "s")
        for p in (cr, other):
            with open(os.path.join(d, p), "w") as f:
                f.write("c\na\nb\n")
        fx = R.Effects.__new__(R.Effects)
        fx.books = d
        got = fx.shuffled_shards([(" M", cr), (" M", other)])
        ok(cr in got and other not in got, "#13 a reordered union shard levels, any other .jsonl is dirt: %s" % sorted(got))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_symlink_ancestor_collides():
    base = tempfile.mkdtemp(prefix="cx5_")
    try:
        up, b = os.path.join(base, "up"), os.path.join(base, "books")
        os.makedirs(up)
        git(up, "init", "-q", "-b", "main")
        with open(os.path.join(up, ".gitignore"), "w") as f:
            f.write("cache\n")
        git(up, "add", ".gitignore")
        git(up, "commit", "-qm", "ignore cache")
        git(base, "clone", "-q", up, b)
        os.makedirs(os.path.join(up, "cache"))
        with open(os.path.join(up, "cache", "new.txt"), "w") as f:
            f.write("tracked now\n")
        git(up, "add", "-f", "cache/new.txt")
        git(up, "commit", "-qm", "track cache")
        git(b, "fetch", "-q", "origin")
        target = os.path.join(base, "elsewhere")
        os.makedirs(target)
        os.symlink(target, os.path.join(b, "cache"))
        fake = bind(types.SimpleNamespace(books=b), "git", "git_ok", "ignored_collision")
        why = fake.ignored_collision()
        ok(why and "cache" in why, "#14 an ignored symlink where origin now wants a folder is a collision: %s" % why)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_caps_mod_name_in_title():
    base = tempfile.mkdtemp(prefix="cx5_")
    try:
        items = {"FIX_RENDER": types.SimpleNamespace(title="FOOMOD rendering crash"),
                 "FIX_OTHER": types.SimpleNamespace(title="after BARMOD_STALL_SHARED_MOVE lands")}
        fake = types.SimpleNamespace(books=base, ledger_items=lambda: (None, types.SimpleNamespace(items=items)),
                                     mod_names=lambda: {"foomod": "RimMandrake/FooMod", "barmod": "RimMandrake/BarMod"},
                                     changed=lambda *a: [])
        bind(fake, "item_mods")
        got = fake.item_mods({"item": "FIX_RENDER", "last_sha": None})
        ok(got == ["RimMandrake/FooMod"], "#15 a lone ALL-CAPS mod name in the title is the mod: %s" % got)
        got = fake.item_mods({"item": "FIX_OTHER", "last_sha": None})
        ok(got == [], "#15 an underscore-joined item id in the title still names no mod: %s" % got)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_saved_patches_skip_textconv():
    src = inspect.getsource(R.Effects)
    bare = src.count('"diff", "--binary"') - src.count('"diff", "--binary", "--no-textconv", "--no-ext-diff"')
    ok(src.count('"diff", "--binary"') >= 3 and bare == 0,
       "#16 every saved patch is the raw bytes (--no-textconv --no-ext-diff): %d without" % bare)


def t_unreadable_tree_is_kept():
    if os.geteuid() == 0:
        ok(True, "#17 skipped as root: a mode-000 folder stays readable")
        return
    base = tempfile.mkdtemp(prefix="cx5_")
    locked = os.path.join(base, "clones", "I0", "work")
    try:
        store = R.Store(base)
        fake = bind(types.SimpleNamespace(base=base, store=store, r={}), "keep_gitless")
        os.makedirs(locked)
        with open(os.path.join(locked, "wip.py"), "w") as f:
            f.write("only copy\n")
        os.chmod(locked, 0)
        got, why = fake.keep_gitless("I0", os.path.dirname(locked))
        ok(got is None and why, "#17 a folder that cannot be listed is no empty tree: %s %s" % (got, why))
    finally:
        os.chmod(locked, stat.S_IRWXU)
        shutil.rmtree(base, ignore_errors=True)


def t_modify_delete_is_not_landed():
    base = tempfile.mkdtemp(prefix="cx5_")
    try:
        src, dst = os.path.join(base, "src"), os.path.join(base, "dst")
        os.makedirs(src)
        git(src, "init", "-q", "-b", "main")
        with open(os.path.join(src, "f.txt"), "w") as f:
            f.write("v1\n")
        git(src, "add", "f.txt")
        git(src, "commit", "-qm", "root")
        root = git(src, "rev-parse", "HEAD")
        with open(os.path.join(src, "f.txt"), "w") as f:
            f.write("v2\n")
        git(src, "commit", "-qam", "upstream modifies f")
        git(base, "clone", "-q", src, dst)     # before the carried branch exists: it is on no remote of dst
        git(src, "checkout", "-q", "-b", "side", root)
        git(src, "rm", "-q", "f.txt")
        git(src, "commit", "-qm", "delete f")
        dele = git(src, "rev-parse", "HEAD")
        bundle = os.path.join(base, "bundle")
        os.makedirs(bundle)
        cb = os.path.join(bundle, "commits.bundle")
        git(src, "bundle", "create", cb, "HEAD", "refs/heads/side")
        store = R.Store(base + "/store")
        os.makedirs(store.item_dir("I0"), exist_ok=True)
        fake = bind(types.SimpleNamespace(store=store), "git", "restore_commits")
        bad = fake.restore_commits("I0", bundle, cb, dst)
        ok(any(dele[:10] in x for x in bad), "#18 a modify/delete conflict is named, not read as landed: %s" % bad)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    for t in (t_live_line_kept, t_scenario_kept, t_charge_replay_takes_the_booked_figure, t_fixture_output_bounded,
              t_account_loss_keeps_pilot_step, t_hold_of_blocked_keeps_blocker, t_hook_fence_follows_git_file,
              t_only_union_shards_reorder, t_symlink_ancestor_collides, t_caps_mod_name_in_title,
              t_saved_patches_skip_textconv, t_unreadable_tree_is_kept, t_modify_delete_is_not_landed):
        try:
            t()
        except Exception as e:  # noqa: BLE001  a row that raises is a failed row, the rest still run
            ok(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    if os.path.exists(os.path.join(HERE, "selftest_relentless_codex_five_b.py")):
        r = subprocess.run([sys.executable, os.path.join(HERE, "selftest_relentless_codex_five_b.py")],
                           capture_output=True, text=True, timeout=400)
        sys.stdout.write(r.stdout[-4000:])
        ok(r.returncode == 0, "rows #1-#4, #19-#21 (selftest_relentless_codex_five_b.py) pass: exit %s" % r.returncode)
    else:
        ok(False, "selftest_relentless_codex_five_b.py is missing")
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
