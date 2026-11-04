#!/usr/bin/env python3
"""A worker, checker or consult the account cut after real work is RESUMED (`claude -p --resume <session>`), not started
over; one that died before any work is a plain requeue; `rediagnose` re-runs a failed attribution consult; a consult
whose wait ran out while the breaker was open on the account is not a failed consult (RELENTLESS_RESUME_BUILD_ACCOUNT_LOST_RUNS).
Engine rows run the real tick on selftest_relentless's rig; sign rows read fixture files in the shapes
relentless_account.py reads (a transcript's API error record, a result object)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                  # noqa: E402
import relentless_account as A          # noqa: E402
import role_launch as RL                # noqa: E402
import selftest_relentless as T         # noqa: E402
import selftest_relentless_attrib as TA  # noqa: E402

ok = T.ok
SID = "0f3c2a1e-1111-4222-8333-444455556666"
LOST = {"kind": "account_error", "why": "the run ended on the account's own error: rate_limit", "session": SID}
BARE = {"kind": "account_error", "why": "the run ended on the account's own error: rate_limit"}
ITEM = "I0"


def _rec(**kw):
    return json.dumps(kw) + "\n"


def transcript(d, worked):
    """<box>/projects/<proj>/<SID>.jsonl ending on the account's rate_limit error, with or without a real turn first."""
    p = os.path.join(d, "projects", "-c-x")
    os.makedirs(p, exist_ok=True)
    with open(os.path.join(p, SID + ".jsonl"), "w") as f:
        f.write(_rec(type="user", message={"role": "user", "content": "go"}))
        if worked:
            f.write(_rec(type="assistant", message={"id": "m1", "usage": {"output_tokens": 812}}))
            f.write(_rec(type="user", message={"role": "user", "content": "tool result"}))
        f.write(_rec(type="assistant", isApiErrorMessage=True, error="rate_limit",
                     message={"id": "m2", "usage": {"output_tokens": 0}}))


def t_signs():
    d = tempfile.mkdtemp(prefix="rs-")
    log = os.path.join(d, "no-log.jsonl")
    try:
        transcript(d, True)
        got = A.loss({"at": 0}, None, 0, log, box=d)
        ok(got and got["kind"] == "account_error" and got.get("session") == SID,
           "a transcript with real work that ends on rate_limit names its session: %s" % got)
        ok(got["why"].startswith(A.ACCOUNT_MARK), "the words the jam class and the breaker read are unchanged")
        shutil.rmtree(os.path.join(d, "projects"))
        transcript(d, False)
        got = A.loss({"at": 0}, None, 0, log, box=d)
        ok(got and got["kind"] == "account_error" and "session" not in got,
           "one that died on its first turn has nothing to resume: %s" % got)
        shutil.rmtree(os.path.join(d, "projects"))
        out = os.path.join(d, "r.json")
        with open(out, "w") as f:
            json.dump({"is_error": True, "result": "You've hit your weekly limit", "session_id": SID,
                       "usage": {"output_tokens": 40}}, f)
        got = A.loss({"at": 0, "out": out}, None, 0, log, box=d)
        ok(got and got.get("session") == SID, "an error result object with output names its session: %s" % got)
        with open(out, "w") as f:
            json.dump({"is_error": True, "result": "You've hit your weekly limit", "session_id": SID,
                       "usage": {"output_tokens": 0}}, f)
        got = A.loss({"at": 0, "out": out}, None, 0, log, box=d)
        ok(got and "session" not in got, "an error result with no output is a plain requeue")
        ok(A.breaker_on_account({"why": LOST["why"]}) and not A.breaker_on_account({"why": "systemd-run exit 1"}),
           "an open breaker is read as the account's only on the account's words")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def worker_dies(x, sign):
    x.run_one(ITEM)
    st = x.st(ITEM)
    R.beat(x.s, ITEM, st["gen"], now=x.now)
    x.w.tok = 500
    x.w.account_sign = sign
    x.w.up[st["run"]["unit"]] = False
    return st


def t_worker_resumes():
    x = T.Rig(n=1, share=1.0, max_workers=1)
    was = worker_dies(x, LOST)
    x.r["max_workers"] = 0
    x.tick(30)
    st = x.st(ITEM)
    ok(st["status"] == "queued" and (st.get("resume") or {}).get("session") == SID and not st["failures"],
       "a worker cut after real work keeps its session, no strike: %s" % st.get("resume"))
    ok(st["clone"] == was["clone"], "its clone stays: the session's transcripts are keyed by it")
    x.w.account_sign = None
    x.r["max_workers"] = 1
    R.launch_ok(x.s)
    n = len(x.w.launches)
    x.run_one(ITEM)
    st = x.st(ITEM)
    item, unit, prompt, agent, clone = x.w.launches[n]
    ok(st["run"].get("resume") == SID, "the next launch carries --resume <session> (run desc): %s" % st["run"].get("resume"))
    ok(prompt.startswith(R.RESUME_WORDS) and ("generation %d" % st["gen"]) in prompt and ("--gen %d" % st["gen"]) in prompt,
       "it is told to continue, and the gen of its new lease: %r" % prompt[:160])
    ok(clone == was["clone"], "in the same clone")
    ok("resume" not in st, "the resume point is spent once")
    ok(x.s.attempts(ITEM)[-1].get("resumed") == SID, "the start row records the resumed session")
    try:
        R.beat(x.s, ITEM, st["gen"], now=x.now)
        ok(True, "the resumed worker reports on its new gen")
    except R.Fenced as e:
        ok(False, "the resumed worker reports on its new gen: %s" % e)
    # it dies again on the account with no work since: a plain requeue, a fresh worker
    x.w.up[st["run"]["unit"]] = False
    x.w.account_sign = BARE
    x.now += 400
    x.r["max_workers"] = 0
    x.tick(30)
    ok(x.st(ITEM)["status"] == "queued" and "resume" not in x.st(ITEM), "a cut with no work since leaves nothing to resume")
    x.w.account_sign = None
    x.r["max_workers"] = 1
    R.launch_ok(x.s)
    n = len(x.w.launches)
    x.run_one(ITEM)
    ok(not x.w.launches[n][2].startswith(R.RESUME_WORDS) and not x.st(ITEM)["run"].get("resume"),
       "so the next worker starts fresh with the full brief")
    x.done()


def t_worker_stale_resume_not_used():
    x = T.Rig(n=1, share=1.0, max_workers=1)
    worker_dies(x, LOST)
    x.r["max_workers"] = 0
    x.tick(30)
    with x.s.lock():
        st = x.s.load(ITEM)
        st["gen"] += 1          # a generation came and went since the cut (a launch failure, a return)
        x.s.save(st)
    x.w.account_sign = None
    x.r["max_workers"] = 1
    R.launch_ok(x.s)
    n = len(x.w.launches)
    x.run_one(ITEM)
    ok(not x.w.launches[n][2].startswith(R.RESUME_WORDS), "a resume point older than the last generation is not used")
    x.done()


def t_launch_argv():
    """The real Effects.launch puts --resume <session> into claude's argv; without one, nothing is added."""
    d = tempfile.mkdtemp(prefix="rs-")
    seen = []
    real = R.subprocess.run

    def fake_run(argv, **kw):
        seen.append(argv)
        return subprocess.CompletedProcess(argv, 0, "", "")
    fx = R.Effects.__new__(R.Effects)
    fx.RL, fx.r = RL, {"seat": "BENCH", "model": "opus"}
    try:
        R.subprocess.run = fake_run
        for resume in (SID, None):
            run = {"unit": "rm-relentless-work-x-g1", "out": os.path.join(d, "u.json"), "err": os.path.join(d, "u.err")}
            if resume:
                run["resume"] = resume
            why = fx.launch({"item": ITEM}, run, "go on", "rm-builder", d, 600, {"TMPDIR": d})
            argv = seen[-1]
            ok(why is None, "the launch goes through: %s" % why)
            if resume:
                i = argv.index("--resume")
                ok(argv[i + 1] == SID and i > argv.index("--") and argv.index("--agent") < i < argv.index("--output-format"),
                   "--resume <session> is claude's flag, not systemd-run's")
            else:
                ok("--resume" not in argv, "a fresh run carries no --resume")
    finally:
        R.subprocess.run = real
        shutil.rmtree(d, ignore_errors=True)


def to_check(x):
    x.run_one(ITEM)
    st = x.st(ITEM)
    R.contract(x.s, ITEM, st["gen"], "proof", live="once: test")
    R.finish(x.s, ITEM, st["gen"], "sha1", "evidence")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st(ITEM)
    ok(st["status"] == "checking", "the rig reaches the checker")
    return st


def t_checker_resumes():
    real = R.tree_present
    R.tree_present = lambda p: True
    try:
        x = T.Rig(n=1, share=1.0, same_failure_limit=2)
        st = to_check(x)
        chk0 = dict(st["check"])
        x.w.account_sign = LOST
        x.w.up[chk0["run"]["unit"]] = False
        x.tick(30)
        st = x.st(ITEM)
        ok(st["status"] == "checking" and (st["check"].get("resume") or {}).get("session") == SID
           and st["check"]["nonce"] == chk0["nonce"] and st["check"]["clone"] == chk0["clone"],
           "a checker cut after real work keeps its clone, nonce and session: %s" % st["status"])
        ok(not st.get("check_lost") and not st["failures"], "and counts nothing")
        x.w.account_sign = None
        br = R.load_breaker(x.s)
        br.update(until=x.now + 5000, why=LOST["why"])
        x.s._write(x.s.p("breaker.json"), json.dumps(br))
        n = len(x.w.launches)
        x.tick(30)
        ok(len(x.w.launches) == n and x.st(ITEM)["check"].get("resume"), "while the breaker is open it waits")
        R.launch_ok(x.s)
        x.tick(30)
        st = x.st(ITEM)
        new = x.w.launches[n:]
        ok(len(new) == 1 and new[0][2] == R.RESUME_WORDS and new[0][4] == chk0["clone"],
           "once it closes, the same checker is resumed in the same clone: %s" % [z[1] for z in new])
        ok(st["status"] == "checking" and st["check"]["run"].get("resume") == SID and st["check"]["nonce"] == chk0["nonce"]
           and st["check"]["unit"] != chk0["unit"] and "resume" not in st["check"],
           "a new unit, the same nonce, the resume spent")
        R.verdict(x.s, ITEM, st["check"]["nonce"], "PASS", "proof ran: exit 0")
        ok(x.st(ITEM)["check"].get("verdict") == "PASS", "the resumed checker's verdict counts on the nonce it remembers")
        x.done()
        # its tree is gone: the old road, a fresh checker
        x = T.Rig(n=1, share=1.0, same_failure_limit=2)
        st = to_check(x)
        x.w.account_sign = LOST
        x.w.up[st["check"]["run"]["unit"]] = False
        x.tick(30)
        x.w.account_sign = None
        R.launch_ok(x.s)
        R.tree_present = lambda p: False
        x.tick(30)
        ok(x.st(ITEM)["status"] in ("candidate", "checking") and not (x.st(ITEM).get("check") or {}).get("resumed"),
           "a resume whose tree is gone falls back to a fresh checker, no count")
        x.done()
        # no work before the cut: as before resuming existed
        R.tree_present = lambda p: True
        x = T.Rig(n=1, share=1.0, same_failure_limit=2)
        st = to_check(x)
        x.w.account_sign = BARE
        x.w.up[st["check"]["run"]["unit"]] = False
        x.tick(30)
        st = x.st(ITEM)
        ok(st["status"] == "candidate" and st["check"] is None, "a checker cut with no work is a plain new checker")
        x.done()
    finally:
        R.tree_present = real


def consult_running(x, item):
    TA.checked(x, item, "FAIL", "could not read D:")
    for _ in range(3):
        x.tick()
    h = x.st(item)["help"]
    ok(h["status"] == "running" and h.get("mode") == "diagnose", "the diagnostic consult runs")
    return h


def t_consult_resumes():
    real = R.tree_present
    R.tree_present = lambda p: True
    try:
        x = TA.rig([TA.STEVE], circling=T.HELP)
        h0 = dict(consult_running(x, TA.STEVE))
        x.w.account_sign = LOST
        x.w.up[h0["run"]["unit"]] = False
        x.tick()
        h = x.st(TA.STEVE)["help"]
        ok(h["status"] in ("wanted", "running") and h["clone"] == h0["clone"] and h["nonce"] == h0["nonce"],
           "a consult cut after real work keeps its clone and nonce: %s" % h["status"])
        x.w.account_sign = None
        R.launch_ok(x.s)
        for _ in range(2):
            if x.st(TA.STEVE)["help"]["status"] == "running":
                break
            x.tick()
        h = x.st(TA.STEVE)["help"]
        last = TA.launches(x, TA.STEVE, "help")[-1]
        ok(h["status"] == "running" and h["run"].get("resume") == SID and last[2] == R.RESUME_WORDS
           and last[4] == h0["clone"] and h["tries"] == h0["tries"], "it is resumed, the cut charged no try: %s" % h)
        route = A_answer(x, h["nonce"])
        ok(route == "proof", "the resumed consult answers on the nonce it remembers: %s" % route)
        x.done()
        # no work before the cut: wanted again from a fresh clone, no try charged
        x = TA.rig([TA.STEVE], circling=T.HELP)
        h0 = dict(consult_running(x, TA.STEVE))
        x.w.account_sign = BARE
        x.w.up[h0["run"]["unit"]] = False
        x.tick()
        h = x.st(TA.STEVE)["help"]
        ok(not h.get("resume") and h["tries"] <= h0["tries"], "a consult cut with no work is wanted again, no try charged")
        x.done()
    finally:
        R.tree_present = real


def A_answer(x, nonce):
    import relentless_attrib
    return relentless_attrib.answer(x.s, TA.STEVE, nonce, ["PROOF"],
                                    dict(R.relentless_explain.sample(), evidence="proof reads Player-prev.log"), x.r, x.now, R)


def t_no_room_under_account_breaker():
    for words, account in ((LOST["why"], True), ("systemd-run exit 1: boom", False)):
        x = TA.rig([TA.STEVE], circling=T.HELP)
        TA.checked(x, TA.STEVE, "FAIL", "could not read D:")
        br = R.load_breaker(x.s)
        br.update(until=x.now + 10 ** 6, why=words)
        x.s._write(x.s.p("breaker.json"), json.dumps(br))
        with x.s.lock():
            st = x.s.load(TA.STEVE)
            st["help"]["at"] = x.now - x.r["circling"]["help_wait_s"] - 1
            st["help"].update(status="wanted", run=None, nonce=None, clone=None)   # between tries, as help_retry leaves it
            x.s.save(st)
        x.tick()
        st = x.st(TA.STEVE)
        if account:
            ok(st["help"]["status"] == "wanted" and st["help"]["at"] == x.now and st["status"] != "held",
               "no room while the breaker is open on the account: the wait starts over, not a failed consult")
        else:
            ok(st["status"] == "held" and "no room" in (st["help"].get("end") or ""),
               "no room on any other cause is still a failed consult: %s" % st["status"])
        x.done()


def t_rediagnose():
    x = TA.rig([TA.STEVE], circling=T.HELP)
    TA.checked(x, TA.STEVE, "FAIL", "could not read D:")
    for _ in range(10):
        for c in TA.launches(x, TA.STEVE, "help"):
            x.w.up[c[1]] = False
        x.tick()
        if x.st(TA.STEVE)["status"] == "held":
            break
    st = x.st(TA.STEVE)
    ok(st["status"] == "held" and st["hold"]["kind"] == "attribution", "a diagnosis that never answered holds it")
    n = len(TA.launches(x, TA.STEVE, "help"))
    R.rediagnose(x.s, TA.STEVE, "test: the consult died in the token outage", now=x.now)
    st = x.st(TA.STEVE)
    ok(st["status"] == "blocked" and not st["hold"] and st["help"]["status"] == "wanted" and st["help"]["mode"] == "diagnose"
       and st["wait"]["sha"] == TA.SHA, "rediagnose wants the diagnostic consult again, the candidate's wait untouched")
    x.tick()
    con = TA.launches(x, TA.STEVE, "help")[n:]
    ok(len(con) == 1 and "DIAGNOSTICIAN" in con[0][2], "and the consult runs again: %d" % len(con))
    ok(TA.kept(x, TA.STEVE) and not TA.launches(x, TA.STEVE, "work")[1:], "no builder, no strike")
    for bad in (lambda: R.rediagnose(x.s, TA.STEVE, "again"), lambda: R.rediagnose(x.s, "NOPE", "x")):
        try:
            bad()
            ok(False, "rediagnose refuses an item that is not held for an attribution")
        except ValueError:
            ok(True, "rediagnose refuses an item that is not held for an attribution")
    x.done()


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("t_") and callable(fn):
            fn()
    print("%d failed" % len(T.FAILS) if T.FAILS else "all passed")
    sys.exit(1 if T.FAILS else 0)
