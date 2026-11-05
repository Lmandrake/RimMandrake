#!/usr/bin/env python3
"""RELENTLESS_CORE_FIX_CODEX_FOUND_TEN_MORE: the Codex re-review's ten findings on relentless.py and relentless_game.py,
each row red without its fix, or a rejection shown green with its reason.

  #1  charge: an "estimated" basis is never a measurement, whatever number rides with it.
  #2  run_fixture: a timed-out fixture's backgrounded child is killed with its group, never left writing the books tree.
  #3  prepare() of the synthetic SHOWINGS clone (no item record) bundles without a TypeError.
  #4  restore_commits: two off-HEAD refs falling on one fallback name both come back; none is overwritten.
  #5  restore_bundle: an untracked file whose path upstream now holds as a directory is named, not skipped in silence.
  #6  REJECTED: a suspended checker counted in `active` with extra=1 is admitted at capacity 1, because worker_cap adds
      `extra` to the CAP (cap + extra), it does not ask for another place. The green row below pins that reading.
  #7  help_start resumes a consult in its own clone before make_room, which could evict that very tree.
  #8  _lease: a hold landing while prepare() runs outside the lock is neither launched over nor overwritten to queued.
  #9  relentless_game: a batched passenger's lane remedy rides the staging that carries it, and is spent by it.
  #10 lives in selftest_relentless_game.py t_fail_on_a_restarted_game_is_offline (a FAIL read after a restart grants
      no live iteration on the new process).
"""
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R  # noqa: E402
import relentless_game as G  # noqa: E402
import selftest_relentless as S  # noqa: E402
import selftest_relentless_game as SG  # noqa: E402

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


def t_estimated_is_charged_the_reserve():
    base = tempfile.mkdtemp(prefix="cx10_")
    try:
        store = R.Store(base)
        r = {"run_reserve": 1000}
        now = 1793866000.0
        for i, (tok, basis, want) in enumerate(((1, "estimated", 1000), (0, "estimated", 1000), (None, None, 1000),
                                                (0, "result", 0), (500, "transcript", 500), (7, None, 7))):
            st = {"spent": 0}
            got = R.charge(store, st, tok, now, r, "u%d" % i, basis)
            ok(got == want and st["spent"] == want, "#1 tokens=%s basis=%s is charged %s: %s" % (tok, basis, want, got))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_fixture_timeout_kills_the_group():
    books = tempfile.mkdtemp(prefix="cx10_")
    try:
        fake = bind(types.SimpleNamespace(books=books), "run_fixture")
        code, tail = fake.run_fixture("echo hi", timeout=20)
        ok(code == 0 and "hi" in tail, "#2 a plain fixture still answers: %s %r" % (code, tail))
        t0 = time.time()
        code, tail = fake.run_fixture("(sleep 2; touch late-result) & wait", timeout=1)
        ok(code is None, "#2 a timed-out fixture never reads as a pass: %s %r" % (code, tail))
        time.sleep(max(0, 3.5 - (time.time() - t0)))
        ok(not os.path.exists(os.path.join(books, "late-result")),
           "#2 its backgrounded child died with it: nothing wrote the books tree after the timeout")
    finally:
        shutil.rmtree(books, ignore_errors=True)


def t_showings_clone_bundles_without_a_record():
    base = tempfile.mkdtemp(prefix="cx10_")
    try:
        store = R.Store(base)
        c = os.path.join(base, "clones", "SHOWINGS")
        os.makedirs(os.path.join(c, ".git"))
        fake = types.SimpleNamespace(base=base, store=store, books=base,
                                     bundle_clone=lambda item, cl: os.path.join(base, "orphans", "bundles", "b1"))
        bind(fake, "prepare")
        try:
            why = fake.prepare({"item": "SHOWINGS", "clone": c, "gen": 0})
            raised = None
        except TypeError as e:
            why, raised = None, e
        ok(raised is None and isinstance(why, str) and why.startswith("clone failed"),
           "#3 a SHOWINGS clone with a gap and WIP bundles, no TypeError (the scratch clone then fails here): %s %s"
           % (raised, why))
        lines = [json.loads(ln) for ln in open(store.p("journal.jsonl"))] if os.path.exists(store.p("journal.jsonl")) else []
        ok(any(e.get("do") == "clone_remade" and e.get("bundle") for e in lines), "#3 the journal keeps where its bundle went")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_fallback_refs_never_overwrite():
    base = tempfile.mkdtemp(prefix="cx10_")
    try:
        src, dst = os.path.join(base, "src"), os.path.join(base, "dst")
        os.makedirs(src)
        git(src, "init", "-q", "-b", "main")
        git(src, "commit", "-q", "--allow-empty", "-m", "root")
        git(src, "clone", "-q", src, dst)
        git(src, "checkout", "-q", "-b", "carried/main")
        git(src, "commit", "-q", "--allow-empty", "-m", "A")
        a = git(src, "rev-parse", "HEAD")
        git(src, "checkout", "-q", "main")
        git(src, "commit", "-q", "--allow-empty", "-m", "B")
        b = git(src, "rev-parse", "HEAD")
        bundle = os.path.join(base, "bundle")
        os.makedirs(bundle)
        cb = os.path.join(bundle, "commits.bundle")
        git(src, "bundle", "create", cb, "refs/heads/carried/main", "refs/heads/main")
        store = R.Store(base + "/store")
        os.makedirs(store.item_dir("I0"), exist_ok=True)
        fake = bind(types.SimpleNamespace(store=store), "git", "restore_commits")
        bad = fake.restore_commits("I0", bundle, cb, dst)
        refs = dict(ln.split()[::-1] for ln in git(dst, "for-each-ref", "--format=%(objectname) %(refname)").splitlines())
        held = set(refs.values())
        ok(not bad and a in held and b in held,
           "#4 both off-HEAD refs come back, neither overwritten by the other's fallback name: %s %s" % (bad, refs))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_untracked_dir_clash_is_named():
    base = tempfile.mkdtemp(prefix="cx10_")
    try:
        c, bundle, stage = (os.path.join(base, x) for x in ("c", "bundle", "stage"))
        for d in (c, bundle, stage):
            os.makedirs(d)
        os.makedirs(os.path.join(c, "cache"))
        with open(os.path.join(c, "cache", "config"), "w") as f:
            f.write("upstream\n")
        with open(os.path.join(stage, "cache"), "w") as f:
            f.write("my wip\n")
        with open(os.path.join(stage, "fresh.txt"), "w") as f:
            f.write("new\n")
        with tarfile.open(os.path.join(bundle, "real_untracked.tar"), "w") as t:
            t.add(os.path.join(stage, "cache"), "cache")
            t.add(os.path.join(stage, "fresh.txt"), "fresh.txt")
        store = R.Store(base + "/store")
        os.makedirs(store.item_dir("I0"), exist_ok=True)
        fake = bind(types.SimpleNamespace(store=store), "git", "restore_bundle")
        bad = fake.restore_bundle("I0", bundle, c)
        ok(any("cache" in b for b in bad), "#5 a file whose path upstream now holds as a directory is named: %s" % bad)
        ok(os.path.exists(os.path.join(c, "fresh.txt")), "#5 the rest still comes back")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_resumed_checker_is_admitted_at_cap_one():
    """#6 REJECTED, pinned: extra raises the cap; it is not another place asked for."""
    base = tempfile.mkdtemp(prefix="cx10_")
    try:
        store = R.Store(base)
        fx = types.SimpleNamespace(paused=lambda: False, mem_gb=lambda: 64.0)
        r = dict(RULES, max_workers=1, staffing=None, day_spend_limit=10 ** 12)
        now = time.time()
        ok(R.admission(store, fx, r, now, 1, extra=1) is None,
           "#6 one checker already counted active, cap 1, extra=1: it resumes")
        ok(R.admission(store, fx, r, now, 1, extra=0) == "max_workers", "#6 the instrument can see: new work at cap 1 waits")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_consult_resumes_before_make_room():
    real = (R.tree_present, R.make_room, R.help_resume)
    calls = []
    R.tree_present = lambda p: True
    R.make_room = lambda *a, **k: calls.append("make_room") or "pool full: only the consult's own saved tree"
    R.help_resume = lambda store, fx, r, item, now, acts: calls.append("resume")
    try:
        x = S.Rig(1, max_workers=4)
        x.tick()
        with x.s.lock():
            st = x.s.load("I0")
            st["help"] = {"at": x.now, "status": "wanted", "resume": "sess-1", "clone": "/c/help-I0", "nonce": "n0",
                          "tries": 1, "mode": None}
            x.s.save(st)
        x.r["circling"] = dict(x.r.get("circling") or {}, help_wait_s=3600)
        acts = []
        del calls[:]        # the tick above may have made room for its own lease
        R.help_start(x.s, x.w, x.r, "I0", x.now, acts)
        ok(calls == ["resume"], "#7 a consult with its saved tree resumes there; no room is made first: %s %s" % (calls, acts))
        x.done()
    finally:
        R.tree_present, R.make_room, R.help_resume = real


def t_hold_during_prepare_wins():
    for label, answer in (("prepare succeeds", None), ("prepare fails", "clone failed: boom")):
        x = S.Rig(1)
        holds = []

        def prep(st, x=x, answer=answer):
            if not holds:
                holds.append(R.hold(x.s, st["item"], "hold it, his words", now=x.now))
            return answer
        x.w.prepare = prep
        for _ in range(6):
            x.tick()
            if holds:
                break
        st = x.st("I0")
        ok(holds and not [l for l in x.w.launches if l[0] == "I0"],
           "#8 %s: a hold landing during prepare launches no worker: %s" % (label, x.w.launches))
        ok(st["status"] in ("stopping", "held"), "#8 %s: the hold's state stands, never put back to queued: %s"
           % (label, st["status"]))
        x.done()


def t_passenger_remedy_rides():
    x = SG.rig(2, share=1.0, max_workers=2)
    SG.two_in_prove(x)
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)       # I0 waits while I1 is untried
    G.step(x.s, x.w, x.r, "I1", x.now, acts, R)       # the running game serves I1
    with x.s.lock():
        st = x.s.load("I1")
        st["game"].update(phase="prove", waits_reload=x.now)
        st["game"]["remedy"] = {"mods": ["mandrake.rsw.armoury"], "cmds": ["python.exe m.py run Armoury"],
                                "why": "I1's producer", "at": x.now}
        x.s.save(st)
    x.w.rows.append({"at": SG.iso_(x.now - 5), "item": "I1", "criterion": "A2", "sha": SG.SHA, "outcome": "UNMEASURED",
                     "why": "not deployed: RM_Y"})
    x.now += 30
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    st = x.st("I0")
    prompt = x.w.launches[-1][2] if x.w.launches else ""
    ok(st["game"]["phase"] == "staging" and st["game"]["batch"] == ["I1"], "#9 I0 stages carrying I1: %s" % st["game"])
    ok("python.exe m.py run Armoury" in prompt and "mandrake.rsw.armoury" in prompt,
       "#9 the passenger's lane fix rides the staging that carries it")
    ok(not x.st("I1")["game"].get("remedy"), "#9 and that staging spends it: %s" % x.st("I1")["game"].get("remedy"))
    ok(G.merged_remedy([None, {}]) is None and G.merged_remedy([{"mods": ["b"], "cmds": ["c"], "why": "w", "at": 1},
                                                             {"mods": ["a", "b"], "why": "v", "at": 2}])
       == {"mods": ["a", "b"], "cmds": ["c"], "why": "w; v", "at": 2}, "#9 remedies merge as a union")
    x.done()


def main():
    for t in (t_estimated_is_charged_the_reserve, t_fixture_timeout_kills_the_group, t_showings_clone_bundles_without_a_record,
              t_fallback_refs_never_overwrite, t_untracked_dir_clash_is_named, t_resumed_checker_is_admitted_at_cap_one,
              t_consult_resumes_before_make_room, t_hold_during_prepare_wins, t_passenger_remedy_rides):
        t()
    fails = FAILS + SG.FAILS + S.FAILS
    print("\n%d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
