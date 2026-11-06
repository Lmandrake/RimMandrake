#!/usr/bin/env python3
"""selftest_relentless_dispute.py - RELENTLESS_BUILD_LIVE_DISPUTE_LOOP (redesign_final §3.3, G11/G12/G13, row 08).

Owner 2026-11-05: test builder makes a test, solution builder builds, "then immediately the test builder responds to
any challenges, then the solution builder immediately responds back... and the third party arbitration if needed".
Acceptance, by case:
(1) a challenge resumes the Setter's own session (at its own box cwd) and the answer prints IN the builder's call;
(2) an answer that lands after the call's budget is printed by the builder's next `boxrun` (relentless.py main), once;
(3) two simultaneous challenges are answered one at a time (per-Setter-session lock);
(4) a Setter session with no transcript goes straight to the arbiter (fresh, excluded from marking);
(5) a second reply is refused; a stale generation, a clause challenged twice, mode off are refused;
(6) an amend counts only after VALIDATE re-runs it (hash moves, history kept); a failing amend goes to the arbiter;
(7) a dispute files 0 ledger items (no rimflow/cli call, nothing written outside the item's exam and run dirs);
(8) every job reaches an answer or a ruling, including a killed answerer (restart, then the arbiter);
(9) >max_clauses clauses in one run sends the whole exam back once (malformed); WP-03 R4 arbiter (arbitrate_exam);
(10) the `challenge` verb is registered; the deployed claude CLI still offers --resume (probe, skipped if absent).
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                      # noqa: E402
import relentless_exam as E                 # noqa: E402
import relentless_dispute as D              # noqa: E402
import selftest_relentless_exam as X        # noqa: E402  (its throwaway repo, local box and good exam)

FAILS = []
IT = "FOO_DOUBLE_RETURNS_TWICE"
GEN = 3
CFG = {"mode": "shadow", "in_call_s": 10, "max_clauses": 3, "answer_tries": 2, "arbiter_tries": 2}
CALLS = []                                   # every subprocess argv any code ran during the test (case 7)


def ok(cond, what):
    print(("  ok    " if cond else "  FAIL  ") + what)
    if not cond:
        FAILS.append(what)


class Claude:
    """Stands in for claude -p: the Setter's resumed turns and the arbiter's fresh ones, scripted."""
    def __init__(self, store, answers=(), rulings=(), nap=0.0, amend=None):
        self.store, self.answers, self.rulings, self.nap, self.amend = store, list(answers), list(rulings), nap, amend
        self.calls, self.active, self.max_active = [], 0, 0
        self.lock = threading.Lock()

    def __call__(self, cwd, prompt, cfg, out, session=None, resume=None):
        with self.lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            self.calls.append({"cwd": cwd, "resume": resume, "agent": cfg.get("setter_agent"), "prompt": prompt})
        try:
            time.sleep(self.nap)
            m = re.search(r"Write (\S+\.answer\.json)", prompt)
            if m:
                verdict = self.answers.pop(0) if self.answers else None
                if verdict:
                    if verdict == "amend" and self.amend:
                        self.amend()
                    E._write(m.group(1), {"verdict": verdict, "why": "SETTER-WHY-%s" % verdict})
                return resume
            m = re.search(r"Write (\S+ruling\.json)", prompt)
            if m:
                w = self.rulings.pop(0) if self.rulings else None
                if w:
                    E._write(m.group(1), {"winner": w, "why": "ARBITER-WHY-%s" % w})
                return "arb-%d" % len(self.calls)
            return resume
        finally:
            with self.lock:
                self.active -= 1


def boxer_rec(repo, tmp, seen):
    inner = X.local_boxer(repo, tmp)

    def boxer(rules, source, sha, files, item=None, nonce=None):
        seen.append(nonce)
        return inner(rules, source, sha, files, item=item)
    return boxer


def setup(tmp, name, session="sess-1", clauses=None):
    repo, base, _wrong, _right = X.make_repo(tmp)
    store = R.Store(os.path.join(tmp, name))
    store.save({"item": IT, "gen": GEN, "status": "doing"})
    d = E.item_dir(store, IT)
    files = os.path.join(d, "files")
    os.makedirs(os.path.join(d, "setter", "files"), exist_ok=True)
    os.makedirs(files, exist_ok=True)
    for n, body in (("t_double.py", X.T_DOUBLE), ("t_name.py", X.T_NAME)):
        for where in (files, os.path.join(d, "setter", "files")):
            with open(os.path.join(where, n), "w") as f:
                f.write(body)
    exam = json.loads(json.dumps(X.GOOD))
    if clauses:
        exam["clauses"] = clauses
    E._write(os.path.join(d, "setter", "exam.json"), exam)
    E._write(os.path.join(d, "exam.json"), dict(exam, item=IT, base_sha=base, exam_hash="h0" * 32, mode="shadow",
                                                setter={"session": session, "model": "opus"}))
    E.set_status(store, IT, state="validated", base=base, exam_hash="h0" * 32)
    ev = os.path.join(tmp, name + "_evidence.txt")
    with open(ev, "w") as f:
        f.write("box output: FAIL double(3)=3\n")
    return store, repo, base, ev


def deps_for(store, repo, tmp, claude, seen, find=None):
    return D.Deps(setter=claude, boxer=boxer_rec(repo, tmp, seen), text_of=lambda i: X.ITEM_TEXT,
                  find=find or (lambda sid: "/boxes/exam-n1/tree" if sid == "sess-1" else None), rules={})


def threaded(store, deps, threads):
    def kicker(s, item, job):
        t = threading.Thread(target=D.work, args=(s, item, job, CFG, deps))
        t.start()
        threads.append(t)
    return kicker


def say_into(lines):
    return lambda s: lines.append(s)


def t_in_call(tmp):
    store, repo, base, ev = setup(tmp, "incall")
    c, seen, th, out = Claude(store, answers=["stand"]), [], [], []
    deps = deps_for(store, repo, tmp, c, seen)
    j = D.ask(store, IT, GEN, "c1", "wrong", ev, "double is not asked", cfg=CFG, kicker=threaded(store, deps, th), say=say_into(out))
    [t.join() for t in th]
    ok(j["state"] == "answered" and any("SETTER-WHY-stand" in s for s in out),
       "1a the Setter's answer prints on the builder's stdout inside the challenge call")
    ok(c.calls and c.calls[0]["resume"] == "sess-1" and seen[0] == "exam-n1" and "FAIL double(3)=3" in c.calls[0]["prompt"],
       "1b the answer comes from the Setter's OWN session (--resume), in a box re-made at its cwd, with the evidence")
    rows = E._lines(D.rows_path(store, IT, GEN))
    ok(len(rows) == 1 and rows[0]["winner"] == "setter" and rows[0]["final"] is False,
       "1c a stand leaves a provisional who-was-right row (setter, not final)")
    return store


def t_after_timeout(tmp):
    store, repo, base, ev = setup(tmp, "late")
    c, seen, out = Claude(store, answers=["stand"]), [], []
    deps = deps_for(store, repo, tmp, c, seen)
    cfg = dict(CFG, in_call_s=0.2)
    j = D.ask(store, IT, GEN, "c1", "unbindable", ev, cfg=cfg, kicker=lambda s, i, k: None, say=say_into(out))
    ok(j["state"] == "asked" and any("pending" in s and "boxrun" in s for s in out),
       "2a past the call's budget the builder is told where the answer will print, and is not blocked")
    D.work(store, IT, j["id"], cfg, deps)                      # the detached worker finishes later
    saved = (R.Store, R.relentless_boxrun.verb)
    R.Store = lambda *a, **k: store
    R.relentless_boxrun.verb = lambda *a, **k: 0
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = R.main(["boxrun", "--item", IT, "--gen", str(GEN)])
        buf2 = io.StringIO()
        with contextlib.redirect_stdout(buf2):
            R.main(["boxrun", "--item", IT, "--gen", str(GEN)])
    finally:
        R.Store, R.relentless_boxrun.verb = saved
    ok(rc == 0 and "SETTER-WHY-stand" in buf.getvalue() and j["id"] in buf.getvalue(),
       "2b the builder's next `relentless.py boxrun` prints the late answer")
    ok("SETTER-WHY-stand" not in buf2.getvalue(), "2c it prints once (delivered is recorded)")
    return store


def t_serialised(tmp):
    store, repo, base, ev = setup(tmp, "two")
    c, seen = Claude(store, answers=["stand", "stand"], nap=0.4), []
    deps = deps_for(store, repo, tmp, c, seen)
    cfg = dict(CFG, in_call_s=0)
    j1 = D.ask(store, IT, GEN, "c1", "wrong", ev, cfg=cfg, kicker=lambda s, i, k: None, say=lambda s: None)
    j2 = D.ask(store, IT, GEN, "c2", "unfair", ev, cfg=cfg, kicker=lambda s, i, k: None, say=lambda s: None)
    ts = [threading.Thread(target=D.work, args=(store, IT, j["id"], cfg, deps)) for j in (j1, j2)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    st = [D.load(store, IT, j["id"])["state"] for j in (j1, j2)]
    ok(c.max_active == 1 and len(c.calls) == 2 and st == ["answered", "answered"],
       "3 two simultaneous challenges are answered one after the other in the Setter's session (max 1 at once)")
    return store


def t_no_session(tmp):
    store, repo, base, ev = setup(tmp, "nosess", session="gone")
    c, seen, th, out = Claude(store, rulings=["setter"]), [], [], []
    deps = deps_for(store, repo, tmp, c, seen)
    j = D.ask(store, IT, GEN, "c1", "wrong", ev, cfg=CFG, kicker=threaded(store, deps, th), say=say_into(out))
    [t.join() for t in th]
    ex = E._read(os.path.join(E.item_dir(store, IT), "excluded.json")) or {}
    ok(j["state"] == "ruled" and j["answer"]["verdict"] == "no_session" and j["ruling"]["winner"] == "setter"
       and any("ARBITER-WHY-setter" in s for s in out), "4a a Setter session that cannot be resumed goes to the arbiter")
    ok(len(c.calls) == 1 and c.calls[0]["resume"] is None and j["ruling"]["session"] in ex.get("sessions", []),
       "4b the arbiter is a fresh session, recorded as excluded from marking the item")
    return store


def t_reply(tmp):
    store, repo, base, ev = setup(tmp, "reply")
    c, seen, th, out = Claude(store, answers=["stand"], rulings=["builder"]), [], [], []
    deps = deps_for(store, repo, tmp, c, seen)
    kick = threaded(store, deps, th)
    j = D.ask(store, IT, GEN, "c1", "wrong", ev, cfg=CFG, kicker=kick, say=say_into(out))
    [t.join() for t in th]
    j = D.reply(store, IT, GEN, j["id"], "the item never asks for 2*n", cfg=CFG, kicker=kick, say=say_into(out))
    [t.join() for t in th]
    ok(j["state"] == "ruled" and j["ruling"]["winner"] == "builder" and any("ARBITER-WHY-builder" in s for s in out),
       "5a one reply, then the arbiter rules in the same call")
    rows = E._lines(D.rows_path(store, IT, GEN))
    ok([r["final"] for r in rows] == [False, True] and rows[-1]["winner"] == "builder" and rows[-1]["builder_reply"],
       "5b the arbiter's row is the final who-was-right row")
    refused = []
    for what, fn in (("second reply", lambda: D.reply(store, IT, GEN, j["id"], "again", cfg=CFG, kicker=kick, say=lambda s: None)),
                     ("stale gen", lambda: D.ask(store, IT, GEN - 1, "c2", "wrong", ev, cfg=CFG, kicker=kick, say=lambda s: None)),
                     ("same clause", lambda: D.ask(store, IT, GEN, "c1", "wrong", ev, cfg=CFG, kicker=kick, say=lambda s: None)),
                     ("no clause", lambda: D.ask(store, IT, GEN, "c9", "wrong", ev, cfg=CFG, kicker=kick, say=lambda s: None)),
                     ("mode off", lambda: D.ask(store, IT, GEN, "c2", "wrong", ev, cfg={"mode": "off"}, kicker=kick, say=lambda s: None))):
        try:
            fn()
        except ValueError:
            refused.append(what)
    ok(refused[:1] == ["second reply"], "5c a duplicate reply is refused")
    ok(refused == ["second reply", "stale gen", "same clause", "no clause", "mode off"],
       "5d stale generation, a clause challenged twice, an unknown clause and mode off are refused (got %s)" % refused)
    return store


def t_amend(tmp):
    store, repo, base, ev = setup(tmp, "amend")
    d = E.item_dir(store, IT)
    good = json.loads(json.dumps(X.GOOD))
    good["clauses"][0]["check"]["timeout_s"] = 61

    def write_good():
        E._write(os.path.join(d, "setter", "exam.json"), good)
    c, seen, th, out = Claude(store, answers=["amend"], amend=write_good), [], [], []
    deps = deps_for(store, repo, tmp, c, seen)
    j = D.ask(store, IT, GEN, "c1", "wrong", ev, cfg=CFG, kicker=threaded(store, deps, th), say=say_into(out))
    [t.join() for t in th]
    ex = E._read(os.path.join(d, "exam.json"))
    vals = E._lines(os.path.join(d, "validation.jsonl"))
    ok(j["state"] == "settled" and ex["exam_hash"] != "h0" * 32 and ex["amended_from"] == "h0" * 32
       and ex["clauses"][0]["check"]["timeout_s"] == 61 and vals and vals[-1]["attempt"] == "amend" and vals[-1]["ok"]
       and len(E._lines(os.path.join(d, "exam_history.jsonl"))) == 1,
       "6a an amend is re-VALIDATED at once and only then frozen (hash moves, old exam kept)")
    ok(E._lines(D.rows_path(store, IT, GEN))[-1]["winner"] == "builder", "6b a validated amend is a builder-right row")
    before = ex["exam_hash"]
    bad = X.with_clause(X.clause("c3", ["test", "-f", "src/foo.py"]))

    def write_bad():
        E._write(os.path.join(d, "setter", "exam.json"), bad)
    c2 = Claude(store, answers=["amend"], rulings=["setter"], amend=write_bad)
    deps2 = deps_for(store, repo, tmp, c2, seen)
    th2 = []
    j2 = D.ask(store, IT, GEN, "c2", "wrong", ev, cfg=CFG, kicker=threaded(store, deps2, th2), say=lambda s: None)
    [t.join() for t in th2]
    ok(j2["state"] == "ruled" and j2["answer"]["verdict"] == "amend_refused" and E._read(os.path.join(d, "exam.json"))["exam_hash"] == before
       and any(r["code"] == "EXISTENCE_ONLY" for r in j2["answer"]["refusals"]),
       "6c an amend that fails VALIDATE does not count: the exam stays, the arbiter rules")
    return store


def t_killed(tmp):
    store, repo, base, ev = setup(tmp, "killed")
    c, seen = Claude(store, answers=[], rulings=["environment"]), []
    deps = deps_for(store, repo, tmp, c, seen)
    cfg = dict(CFG, in_call_s=0)
    j = D.ask(store, IT, GEN, "c1", "unfair", ev, cfg=cfg, kicker=lambda s, i, k: None, say=lambda s: None)
    D.update(store, IT, j["id"], state="answering", attempts=1)          # its worker was killed mid-turn
    kicks = []
    D.deliver(store, IT, GEN, say=lambda s: None, kicker=lambda s, i, k: kicks.append(k), alive=lambda i, k: False, cfg=cfg)
    ok(kicks == [j["id"]] and D.load(store, IT, j["id"])["state"] == "asked", "8a a killed answerer is restarted by the next boxrun")
    D.update(store, IT, j["id"], state="answering", attempts=2)          # killed again
    D.deliver(store, IT, GEN, say=lambda s: None, kicker=lambda s, i, k: D.work(s, i, k, cfg, deps), alive=lambda i, k: False, cfg=cfg)
    jj = D.load(store, IT, j["id"])
    ok(jj["state"] == "ruled" and jj["answer"]["verdict"] == "no_answer" and jj["ruling"]["winner"] == "environment",
       "8b killed twice: the arbiter rules (no hang)")
    j3 = D.ask(store, IT, GEN, "c2", "wrong", ev, cfg=cfg, kicker=lambda s, i, k: None, say=lambda s: None)
    D.update(store, IT, j3["id"], state="arbitrating", arb_attempts=2)
    D.deliver(store, IT, GEN, say=lambda s: None, kicker=lambda s, i, k: None, alive=lambda i, k: False, cfg=cfg)
    ok(D.load(store, IT, j3["id"])["ruling"]["winner"] == "void", "8c an arbiter killed twice leaves a recorded void ruling")
    return store


def t_malformed_and_exam(tmp):
    cl = [X.clause("c%d" % i, ["python3", ".exam/t_double.py"]) for i in (1, 2, 3, 4)]
    store, repo, base, ev = setup(tmp, "malformed", clauses=cl)
    c, seen = Claude(store, answers=["stand"]), []
    deps = deps_for(store, repo, tmp, c, seen)
    cfg = dict(CFG, in_call_s=0)
    js = [D.ask(store, IT, GEN, x, "wrong", ev, cfg=cfg, kicker=lambda s, i, k: None, say=lambda s: None) for x in ("c1,c2", "c3")]
    j4 = D.ask(store, IT, GEN, "c4", "wrong", ev, cfg=cfg, kicker=lambda s, i, k: None, say=lambda s: None)
    D.work(store, IT, j4["id"], cfg, deps)
    ok([j["kind"] for j in js] == ["clause", "clause"] and j4["kind"] == "malformed"
       and "WHOLE exam" in c.calls[0]["prompt"], "9a a 4th challenged clause sends the whole exam back to the Setter (malformed)")
    for j in js:
        D.work(store, IT, j["id"], cfg, D.Deps(setter=Claude(store, answers=["stand"]), boxer=boxer_rec(repo, tmp, []),
                                                text_of=lambda i: X.ITEM_TEXT, find=lambda s: "/b/n/tree", rules={}))
    E.set_status(store, "OTHER_ITEM", state="arbiter_owed", base=base,
                 refusals=[{"clause": "c1", "code": "EXISTENCE_ONLY", "why": "grep only"}])
    ca = Claude(store, rulings=["bar"])
    r = D.arbitrate_exam(store, "OTHER_ITEM", cfg, D.Deps(setter=ca, boxer=boxer_rec(repo, tmp, []), text_of=lambda i: X.ITEM_TEXT, rules={}))
    st = E.status(store, "OTHER_ITEM")
    ok(r and r["winner"] == "bar" and st["state"] == "arbiter_ruled" and "EXISTENCE_ONLY" in ca.calls[0]["prompt"]
       and "builder (" not in ca.calls[0]["prompt"], "9b WP-03 R4: a twice-refused exam's arbiter rules setter|environment|bar")
    src = open(os.path.join(HERE, "relentless_exam.py")).read()
    ok("relentless_dispute.arbitrate_exam(store, a.item)" in src, "9c the exam unit launches that arbiter on arbiter_owed")
    return store


def t_role_entry(tmp):
    """WP-15/08 join: role_launch's 2nd identical rejection reaches a fresh arbiter's ruling through role_launch.to_arbiter."""
    import role_launch as RL
    store, repo, base, ev = setup(tmp, "role_entry")
    c, seen = Claude(store, rulings=["builder"]), []
    deps = deps_for(store, repo, tmp, c, seen)
    saved = (R.Store, D.Deps, D.config)
    R.Store, D.Deps, D.config = (lambda *a, **k: store), (lambda: deps), (lambda path=None: dict(CFG))
    try:
        said = RL.to_arbiter("Designer", "/x/concept_a", IT, "4|module|decisions[d1]", ["decisions[d1]: no event"])
        off = dict(CFG, mode="off")
        D.config = lambda path=None: off
        said_off = RL.to_arbiter("Designer", "/x/concept_a", IT, "sig", ["r"])
    finally:
        R.Store, D.Deps, D.config = saved
    rows = E._lines(os.path.join(E.item_dir(store, IT), "role_dispute.jsonl"))
    ok(said and "ruled builder" in said and len(c.calls) == 1 and c.calls[0]["agent"] == "rm-judge"
       and "decisions[d1]: no event" in c.calls[0]["prompt"], "10a to_arbiter -> one fresh arbiter rules: %r" % said)
    ok(len(rows) == 1 and rows[0]["winner"] == "builder" and rows[0]["final"], "10b the who-was-right row is logged")
    ok(said_off is None and len(c.calls) == 1, "10c mode off: no arbiter, falls back (None)")
    return store


def t_registration_and_cli(store):
    saved = R.Store
    R.Store = lambda *a, **k: store
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = R.main(["challenge", "--item", IT, "--gen", str(GEN), "--status"])
    finally:
        R.Store = saved
    ok(rc == 0 and "relentless challenge" in buf.getvalue(), "10a `relentless.py challenge --status` is registered and lists jobs")
    claude = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    if os.path.exists(claude):
        try:
            h = subprocess.run([claude, "--help"], capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            ok("--resume" in (h.stdout + h.stderr), "10b the deployed claude CLI still offers --resume (the transport)")
        except (OSError, subprocess.SubprocessError) as e:
            print("  skip  10b claude --help: %s" % e)
    else:
        print("  skip  10b no claude CLI on this host")


def t_no_filing_and_all_reached(stores, tmp):
    bad = [a for a in CALLS if any("cli.py" in str(x) or "rimflow" == os.path.basename(str(x)) for x in a)]
    ok(not bad, "7a a dispute ran no rimflow/cli command (0 ledger items filed): %s" % bad[:2])
    stray = []
    for s in stores:
        for dp, _dn, fn in os.walk(s.dir):
            for f in fn:
                rel = os.path.relpath(os.path.join(dp, f), s.dir)
                if not (rel.startswith("exams" + os.sep) or rel.startswith(os.path.join("items", IT) + os.sep)
                        or rel == ".lock"):
                    stray.append(rel)
    ok(not stray, "7b nothing written outside the item's exam and run dirs: %s" % stray[:3])
    left = [(j["id"], j.get("state")) for s in stores for it in os.listdir(E.exam_root(s))
            for j in D.jobs(s, it) if j.get("state") not in D.ANSWERED]
    ok(not left, "8d every job reached an answer or an arbiter ruling: %s" % left)


def main():
    tmp = tempfile.mkdtemp(prefix="selftest_dispute_")
    real_run, real_popen = subprocess.run, subprocess.Popen

    def rec_run(argv, *a, **k):
        CALLS.append(argv if isinstance(argv, (list, tuple)) else [argv])
        return real_run(argv, *a, **k)

    class RecPopen(real_popen):
        def __init__(self, argv, *a, **k):
            CALLS.append(argv if isinstance(argv, (list, tuple)) else [argv])
            super().__init__(argv, *a, **k)
    subprocess.run, subprocess.Popen = rec_run, RecPopen
    try:
        stores = [t_in_call(tmp), t_after_timeout(tmp), t_serialised(tmp), t_no_session(tmp), t_reply(tmp),
                  t_amend(tmp), t_killed(tmp), t_malformed_and_exam(tmp), t_role_entry(tmp)]
        t_registration_and_cli(stores[0])
        t_no_filing_and_all_reached(stores, tmp)
    finally:
        subprocess.run, subprocess.Popen = real_run, real_popen
        shutil.rmtree(tmp, ignore_errors=True)
    print("RESULT %s (%d failed)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
