#!/usr/bin/env python3
"""RELENTLESS_REVIEW_FIX_ROUND_SIX_STILL_DIGS: the Codex r6 full-file review's 22 findings on relentless.py (review files:
D:\\ClaudeWork\\rimmandrake\\relentless\\RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN\\r6\\rev_part*.txt, line numbers at 887d8937e4).
All 22 were real and are fixed, each with a row red without its fix (checked by running these rows against the
pre-fix relentless.py). Rows #16-#18 and #22 run the real tick on selftest_relentless's rig, in _b; it runs from here.

  #1  charge: a run is looked for in every day file from its launch, so a crash recovered two days later books it once.
  #2  restore_deleted: a tracked symlink is hashed by its link text, so an unchanged one's deletion goes through.
  #3  state_only_push: "beyond origin/main", not "beyond every remote": a commit origin/topic holds is still pushed.
  #4  unlanded: an unpublished merge carrying a resolution (diff-tree --cc non-empty) is unlanded; a clean one is not.
  #5  landed_commit: an unreadable worker sha returns it as is, never re-raises TypeError from re.escape(None).
  #6  gpt_consult: the answer file is removed before the call, so a failed call never reads an older answer.
  #7  level_books' derived-file restore unlinks a symlink before writing, never writes through it to its target.
  #8  level_books: a raise after the reset landed (HEAD moved) never runs _unlevel over origin's shards.
  #9  item_mods: Foo_Bar in a title or id reaches the folder known as foo_bar (runs joined by `_` as well as bare).
  #10 a bundle's patch is streamed under its cap and killed past it; a tarball is sized before tar writes a byte.
  #11 prose_moves: a close move staged by `git mv` (destination `A `) is published like an untracked one.
  #12 changed(): an unread item log falls back to the whole base..sha diff (a superset), never a partial list.
  #13 changed(): --no-renames, so a renamed hook's source path is in the list and its live line is owed.
  #14 help_checkout: a consult clone whose push url could not be disabled is removed and refused.
  #15 owner_pause: pipeline_prefixes given as a string is one prefix; empty or non-string entries let nothing through.
  #16 checking: bind_moved is asked again under the lock that consumes a PASS.                                   (_b)
  #17 checking: a blind FAIL is owed in the state before the item moves; a failed ledger write is retried.       (_b)
  #18 closing: a retry tick spent waiting on origin (published() unknown) is no counted closing attempt.         (_b)
  #19 give_back(expect=): the filler's unreserved give-back moves only from the status it read (an owner's `held` stands).
  #20 help_resume: a resumed consult gets a fresh deadline with its fresh start.
  #21 action_fired: an execution row with no sha is unread (None), never a match for the row's build.
  #22 game_pass: a busy game skips a waiting item (continue), never breaks before the staging holder's own step.  (_b)
"""
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile
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
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, check=True,
                          capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout.strip()


def repo(base, name="r"):
    d = os.path.join(base, name)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main")
    git(d, "commit", "-q", "--allow-empty", "-m", "root")
    return d


def write(d, p, text):
    os.makedirs(os.path.dirname(os.path.join(d, p)) or d, exist_ok=True)
    with open(os.path.join(d, p), "w") as f:
        f.write(text)


def guarded(fn, *a, **k):
    try:
        return fn(*a, **k), None
    except Exception as e:      # noqa: BLE001  a row reads a raise as its answer
        return None, "%s: %s" % (type(e).__name__, e)


def t1_charge_two_days_later():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        store = R.Store(base)
        launch = 1793866000.0
        R.charge(store, {"spent": 0}, 1000, launch, {"run_reserve": 5000}, "u", "result", since=launch)   # booked
        st = {"spent": 0}
        later = launch + 2 * 86400 + 60
        got, err = guarded(R.charge, store, st, 1000, later, {"run_reserve": 5000}, "u", "result", since=launch)
        d = R._day(store, later)
        ok(err is None and "u" not in d["runs"] and d["spent"] == 0 and got == 1000,
           "#1 a run recovered two days after its launch is booked once: today %s, charged %s %s" % (d, got, err))
        src = inspect.getsource(R.settle) + inspect.getsource(R.reap_quarantined)
        ok(src.count("since=") >= 2, "#1 settle and reap_quarantined pass the run's launch to charge()")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t2_symlink_deletion():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        c = repo(base)
        write(c, "target.txt", "target bytes\n")
        os.symlink("target.txt", os.path.join(c, "link"))
        git(c, "add", "target.txt", "link")
        git(c, "commit", "-q", "-m", "link")
        b = os.path.join(base, "bundle")
        os.makedirs(b)
        write(b, "HEAD", git(c, "rev-parse", "HEAD"))
        write(b, "deleted", "link")
        bad = R.restore_deleted(b, c)
        ok(not bad and not os.path.lexists(os.path.join(c, "link")) and os.path.exists(os.path.join(c, "target.txt")),
           "#2 an unchanged tracked symlink's deletion goes through: %s" % bad)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t3_state_only_push_topic_remote():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        up = os.path.join(base, "up.git")
        git(base, "init", "-q", "--bare", "-b", "main", up)
        c = repo(base, "c")
        git(c, "remote", "add", "origin", up)
        git(c, "push", "-q", "origin", "main")
        write(c, "src/code.py", "x = 1\n")
        git(c, "add", "src/code.py")
        git(c, "commit", "-q", "-m", "code")
        git(c, "push", "-q", "origin", "HEAD:refs/heads/topic")       # origin/topic holds it; origin/main does not
        git(c, "fetch", "-q", "origin")
        ok(R.state_only_push(c) is False, "#3 a code commit origin/topic holds is still no state-only push to main")
        git(c, "reset", "-q", "--hard", "origin/main")
        write(c, R.POOL_STATE[0] + "x.md", "a lesson\n")
        git(c, "add", R.POOL_STATE[0] + "x.md")
        git(c, "commit", "-q", "-m", "lesson")
        ok(R.state_only_push(c) is True, "#3 control: a lesson-only commit is state-only")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t4_unlanded_merge_resolution():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        up = os.path.join(base, "up.git")
        git(base, "init", "-q", "--bare", "-b", "main", up)
        c = repo(base, "c")
        write(c, "f.txt", "a\n")
        git(c, "add", "f.txt")
        git(c, "commit", "-q", "-m", "base")
        b0 = git(c, "rev-parse", "HEAD")
        git(c, "remote", "add", "origin", up)
        git(c, "checkout", "-q", "-b", "side")
        write(c, "f.txt", "side\n")
        git(c, "commit", "-q", "-am", "side")
        git(c, "checkout", "-q", "-b", "g", b0)
        write(c, "g.txt", "g\n")
        git(c, "add", "g.txt")
        git(c, "commit", "-q", "-m", "g")
        git(c, "checkout", "-q", "main")
        write(c, "f.txt", "mine\n")
        git(c, "commit", "-q", "-am", "mine")
        # origin/main holds mine, side and g by hash (an `ours` merge), so no plain commit of HEAD is unlanded
        git(c, "checkout", "-q", "-b", "pub")
        git(c, "merge", "-q", "-s", "ours", "-m", "ours", "side", "g")
        git(c, "push", "-q", "origin", "pub:main")
        git(c, "fetch", "-q", "origin")
        git(c, "checkout", "-q", "main")
        subprocess.run(["git", "merge", "-q", "side"], cwd=c, capture_output=True)      # conflicts on f.txt
        write(c, "f.txt", "resolved by hand\n")
        git(c, "add", "f.txt")
        git(c, "commit", "-q", "-m", "merge with a resolution")
        merge = git(c, "rev-parse", "HEAD")
        left = R.unlanded(c)
        ok(left is not None and merge in left, "#4 an unpublished merge carrying a resolution is unlanded: %s" % left)
        git(c, "reset", "-q", "--hard", "HEAD~1")
        git(c, "merge", "-q", "--no-ff", "-m", "clean merge", "g")
        left = R.unlanded(c)
        ok(left == [], "#4 control: a clean merge of commits origin holds adds nothing: %s" % left)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t5_landed_commit_unreadable_sha():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        up = os.path.join(base, "up.git")
        git(base, "init", "-q", "--bare", "-b", "main", up)
        c = repo(base, "c")
        git(c, "remote", "add", "origin", up)
        git(c, "push", "-q", "origin", "main")
        got, err = guarded(R.landed_commit, "f" * 40, c)
        ok(err is None and got == ("f" * 40, None), "#5 an unreadable worker sha is returned as is: %s %s" % (got, err))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t6_gpt_consult_stale_answer():
    base = tempfile.mkdtemp(prefix="cx6_")
    real = R.subprocess.run
    try:
        out = os.path.join(base, "p.answer.md")
        write(base, "p.answer.md", "OPTION: an old answer | from a nonce gone\n")

        def failing(argv, **k):
            return subprocess.CompletedProcess(argv, 7, "", "vendor down")
        R.subprocess.run = failing
        got = R.gpt_consult(os.path.join(base, "p"), out, 120)
        ok("old answer" not in (got or ""), "#6 a failed vendor call never reads an earlier answer: %r" % got)
    finally:
        R.subprocess.run = real
        shutil.rmtree(base, ignore_errors=True)


class _Store:
    def __init__(self, base):
        self.base, self.rows = base, []

    def p(self, *a):
        return os.path.join(self.base, "store", *a)

    def journal(self, row):
        self.rows.append(row)


def t7_restore_never_writes_through_symlink():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        b = repo(base, "books")
        p = R.ITEMS_DIR + "X.md"
        write(b, p, "the item's prose\n")
        git(b, "add", p)
        git(b, "commit", "-q", "-m", "item")
        victim = os.path.join(base, "victim.txt")
        write(base, "victim.txt", "not ours\n")
        os.unlink(os.path.join(b, p))
        os.symlink(victim, os.path.join(b, p))
        fake = bind(types.SimpleNamespace(books=b, store=_Store(base), r={}), "git", "_level_rows_locked")
        fake.shards_locked = lambda extra=(): _null()
        guarded(fake._level_rows_locked, [(" M", p)], {}, os.path.join(base, "keep"), {}, {}, "1", {})
        with open(victim) as f:
            v = f.read()
        ok(v == "not ours\n", "#7 the restore never writes through a symlink to its target: %r" % v)
    finally:
        shutil.rmtree(base, ignore_errors=True)


class _null:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def t8_no_unlevel_after_reset_landed():
    for moved in (True, False):
        base = tempfile.mkdtemp(prefix="cx6_")
        try:
            shard = R.LEDGER_DIR + "X.jsonl"
            write(base, shard, '{"a":1}\n')
            state = {"head": "h0"}
            calls = []

            def git_ok(c, *a):
                return {"rev-list": "1", "status": " M %s\0" % shard, "diff": "", "show": '{"a":1}\n{"b":2}\n',
                        "rev-parse": state["head"]}[a[0]]

            def git_(c, *a, **k):
                return subprocess.CompletedProcess(a, 0, state["head"] + "\n", "")

            def level_rows(*a):
                if moved:
                    state["head"] = "h1"        # the reset landed
                raise OSError("the journal write after the reset failed")
            fake = types.SimpleNamespace(books=base, store=_Store(base), git_ok=git_ok, git=git_,
                                         shuffled_shards=lambda rows: {}, drop_stray_untracked=lambda rows: rows,
                                         _level_rows=level_rows, _unlevel=lambda *a: calls.append(a),
                                         _carry_late=lambda *a: None)
            bind(fake, "level_books")
            _, err = guarded(fake.level_books)
            if moved:
                ok(err and not calls, "#8 a raise after the reset landed never unlevels origin's shards: %s %d" % (err, len(calls)))
            else:
                ok(err and len(calls) == 1, "#8 control: a raise before the reset still unlevels: %d" % len(calls))
        finally:
            shutil.rmtree(base, ignore_errors=True)


def t9_underscore_mod_folder():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        items = {"FIX_THING": types.SimpleNamespace(title="Foo_Bar rendering crash")}
        fake = types.SimpleNamespace(books=base, ledger_items=lambda: (None, types.SimpleNamespace(items=items)),
                                     mod_names=lambda: {"foo_bar": "RimMandrake/Foo_Bar"}, changed=lambda *a: [])
        bind(fake, "item_mods")
        got = fake.item_mods({"item": "FIX_THING", "last_sha": None})
        ok(got == ["RimMandrake/Foo_Bar"], "#9 Foo_Bar in a title reaches the folder foo_bar: %s" % got)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t10_bundle_caps_before_writing():
    base = tempfile.mkdtemp(prefix="cx6_")
    caps = R.BUNDLE_PATCH_MAX, R.BUNDLE_MAX
    try:
        c = repo(base, "c")
        write(c, "big.txt", "small\n")
        git(c, "add", "big.txt")
        git(c, "commit", "-q", "-m", "big")
        write(c, "big.txt", "".join("line %d %s\n" % (i, "x" * 80) for i in range(60000)))     # ~5 MB of diff
        out = os.path.join(base, "out")
        os.makedirs(out)
        R.BUNDLE_PATCH_MAX = 1 << 20
        fake = bind(types.SimpleNamespace(), "git", "git_ok", "_bundle_write")
        _, err = guarded(fake._bundle_write, c, out, ["big.txt"], [], [], [], [])
        size = os.path.getsize(os.path.join(out, "diff.patch")) if os.path.exists(os.path.join(out, "diff.patch")) else 0
        ok(err and size <= 2 * (1 << 20), "#10 a runaway patch stops at its cap: %d bytes on disk (%s)" % (size, err))
        git(c, "checkout", "--", "big.txt")
        R.BUNDLE_PATCH_MAX, R.BUNDLE_MAX = caps[0], 1 << 20
        write(c, "loose.bin", "y" * (3 << 20))
        out2 = os.path.join(base, "out2")
        os.makedirs(out2)
        _, err = guarded(fake._bundle_write, c, out2, ["loose.bin"], [], [], [], [])
        ok(err and not os.path.exists(os.path.join(out2, "untracked.tar")),
           "#10 a tarball over the cap is refused before tar writes it: %s" % err)
    finally:
        R.BUNDLE_PATCH_MAX, R.BUNDLE_MAX = caps
        shutil.rmtree(base, ignore_errors=True)


def t11_staged_close_move():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        b = repo(base, "books")
        write(b, R.ITEMS_DIR + "X.md", "prose\n")
        git(b, "add", R.ITEMS_DIR + "X.md")
        git(b, "commit", "-q", "-m", "item")
        os.makedirs(os.path.join(b, R.ITEMS_DIR, "closed"))
        git(b, "mv", R.ITEMS_DIR + "X.md", R.ITEMS_DIR + "closed/X.md")
        fake = bind(types.SimpleNamespace(books=b), "git", "prose_moves")
        got = fake.prose_moves()
        ok(got == [R.ITEMS_DIR + "X.md", R.ITEMS_DIR + "closed/X.md"], "#11 a staged git mv close is published: %s" % got)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t12_13_changed():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        b = repo(base, "books")
        write(b, "src/hooks/old_hook.py", "x = 1\n")
        git(b, "add", "src/hooks/old_hook.py")
        git(b, "commit", "-q", "-m", "hook")
        root = git(b, "rev-parse", "HEAD")
        git(b, "mv", "src/hooks/old_hook.py", "src/hooks/new_hook.py")
        git(b, "commit", "-q", "-m", "I0: rename the hook")
        write(b, "doc.md", "d\n")
        git(b, "add", "doc.md")
        git(b, "commit", "-q", "-m", "I0: doc")
        sha = git(b, "rev-parse", "HEAD")
        fake = bind(types.SimpleNamespace(books=b), "git", "changed")
        got = fake.changed(root, sha, "I0")
        ok("src/hooks/old_hook.py" in got and "src/hooks/new_hook.py" in got,
           "#13 a renamed hook's source path is listed: %s" % got)
        real = fake.git

        def no_log(c, *a, **k):
            return subprocess.CompletedProcess(a, 128, "", "fatal: log broke") if a[0] == "log" else real(c, *a, **k)
        fake.git = no_log
        got, err = guarded(fake.changed, root, sha, "I0")
        ok(err is None and "src/hooks/new_hook.py" in (got or []),
           "#12 an unread item log is no partial list (the hook commit is kept): %s %s" % (got, err))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t14_help_checkout_push_url():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        d = os.path.join(base, "help-c0")
        os.makedirs(d)
        fake = types.SimpleNamespace(help_path=lambda st: d, _detached_clone=lambda *a, **k: (d, None),
                                     git=lambda c, *a, **k: subprocess.CompletedProcess(a, 1, "", "locked config"))
        bind(fake, "help_checkout")
        got, why = fake.help_checkout({"item": "I0"}, "abc")
        ok(got is None and why and not os.path.exists(d), "#14 a clone that can still push is refused: %s %s" % (got, why))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t15_pause_prefix_string():
    fx = types.SimpleNamespace(owner_pause_rule={"pipeline_only": True, "pipeline_prefixes": "LIGHTSPEED_"}, first={})
    p = R.owner_pause(fx, [])
    ok(p and not R.owner_pipeline(p, fx, "LOGS_FIX_X") and not R.owner_pipeline(p, fx, "ART_FIX_X")
       and R.owner_pipeline(p, fx, "LIGHTSPEED_RUN_X"),
       "#15 a string prefix is one prefix, never its letters: %s" % (p or {}).get("prefixes"))
    fx.owner_pause_rule = {"pipeline_only": True, "pipeline_prefixes": ["", None, "LIGHTSPEED_"]}
    p = R.owner_pause(fx, [])
    ok(not R.owner_pipeline(p, fx, "ANY_ITEM"), "#15 an empty prefix lets nothing through: %s" % p.get("prefixes"))


def t19_give_back_expect():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        s = R.Store(base)
        st = R.new_state("I0", 1000.0, "t")
        st.update(status="held")
        with s.lock():
            s.save(st)
        _, err = guarded(R.give_back, s, "I0", "no longer a kind", expect="queued")
        ok(err is None and s.load("I0")["status"] == "held", "#19 an owner's hold written meanwhile stands: %s %s"
           % (s.load("I0")["status"], err))
        src = inspect.getsource(R._lease)
        line = [x for x in src.splitlines() if "no longer a kind of item the filler may take" in x]
        ok(line and "expect=" in line[0], "#19 the filler's unreserved give-back names the status it read: %s" % line)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t20_help_resume_deadline():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        s = R.Store(base)
        st = R.new_state("I0", 1000.0, "t")
        st.update(status="running", gen=1, help={"status": "wanted", "resume": {"session": "s1", "at": 1500.0},
                                                   "tries": 1, "agent": "rm-consult", "clone": os.path.join(base, "c"),
                                                   "nonce": "n", "deadline": 1200.0, "started_at": 1100.0})
        with s.lock():
            s.save(st)
        fx = types.SimpleNamespace(launch=lambda *a, **k: None)
        now = 5000.0
        R.help_resume(s, fx, RULES, "I0", now, [])
        h = s.load("I0")["help"]
        ok((h.get("deadline") or 0) > now, "#20 a resumed consult's deadline is after its resume: %s at %s" % (h.get("deadline"), now))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t21_action_fired_shaless():
    base = tempfile.mkdtemp(prefix="cx6_")
    try:
        s = R.Store(base)
        with s.lock():
            s.save(R.new_state("I0", 1000.0, "t"))
        s.attempt("I0", {"at": "2026-11-06T10:00:00Z", "end": "game_env_fix"})
        got = R.action_fired(s, {"action": "deploy", "item": "I0", "sha": "abc", "at": "2026-11-06T09:00:00Z"})
        ok(got is not True, "#21 an execution with no sha is no match for the row's build: %s" % got)
        s.attempt("I0", {"at": "2026-11-06T10:05:00Z", "end": "game_env_fix", "sha": "abc"})
        got = R.action_fired(s, {"action": "deploy", "item": "I0", "sha": "abc", "at": "2026-11-06T09:00:00Z"})
        ok(got is True, "#21 control: one naming the build matches: %s" % got)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    for t in (t1_charge_two_days_later, t2_symlink_deletion, t3_state_only_push_topic_remote, t4_unlanded_merge_resolution,
              t5_landed_commit_unreadable_sha, t6_gpt_consult_stale_answer, t7_restore_never_writes_through_symlink,
              t8_no_unlevel_after_reset_landed, t9_underscore_mod_folder, t10_bundle_caps_before_writing,
              t11_staged_close_move, t12_13_changed, t14_help_checkout_push_url, t15_pause_prefix_string,
              t19_give_back_expect, t20_help_resume_deadline, t21_action_fired_shaless):
        try:
            t()
        except Exception as e:      # noqa: BLE001  a row that raises is a FAIL, never a stopped file
            ok(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    b = subprocess.run([sys.executable, os.path.join(HERE, "selftest_relentless_codex_six_b.py")], capture_output=True,
                       text=True, timeout=400, stdin=subprocess.DEVNULL)
    sys.stdout.write(b.stdout)
    ok(b.returncode == 0, "selftest_relentless_codex_six_b.py exit %d %s" % (b.returncode, b.stderr[-300:]))
    print("%s: %d failure(s)" % (os.path.basename(__file__), len(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
