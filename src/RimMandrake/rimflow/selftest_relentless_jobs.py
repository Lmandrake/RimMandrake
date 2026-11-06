#!/usr/bin/env python3
"""RELENTLESS_SHRINK_TICK_SLOW_PHASES_DETACHED. Slow read-only work leaves the supervisor tick for a detached job
(relentless_jobs): a request while it runs is coalesced, never lost (gen fence); a duplicate start touches nothing; a job
killed mid-run is found lost on the next tick and launched again, its last good answer intact; the showing stage reads
the job's answer for the Mods walk instead of walking it inline.

    python3 src/RimMandrake/rimflow/selftest_relentless_jobs.py
"""
import fcntl
import inspect
import json
import os
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R  # noqa: E402
import relentless_jobs as J  # noqa: E402
import relentless_showing as S  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def store():
    return R.Store(tempfile.mkdtemp(prefix="relentless_jobs_"))


class Launch:
    def __init__(self):
        self.n = 0

    def __call__(self, kind):
        self.n += 1
        return None


def hold(st, kind):
    """Another process's running job, as the kernel sees it: the kind lock held on a separate open file."""
    fd = os.open(J._path(st, kind, ".lock"), os.O_CREAT | os.O_RDWR, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return fd


def t_request_launches_once_and_coalesces():
    st, la = store(), Launch()
    J.request(st, "mods_fp", {"n": 1}, la)
    ok(la.n == 1 and J.table(st, "mods_fp")["state"] == "queued", "a request with no job running launches one")
    fd = hold(st, "mods_fp")
    J.request(st, "mods_fp", {"n": 2}, la)
    J.request(st, "mods_fp", {"n": 3}, la)
    t = J.table(st, "mods_fp")
    ok(la.n == 1 and t["gen"] == 3 and t["want"] == {"n": 3},
       "requests while a job runs launch nothing more; the newest want and gen are recorded (%d launches, gen %s)"
       % (la.n, t["gen"]))
    os.close(fd)
    # a request that arrives while the job computes: the job goes round again on the newest want
    seen = []

    def fn(want):
        seen.append(want["n"])
        if len(seen) == 1:
            J.request(st, "mods_fp", {"n": 4}, la)
        return {"n": want["n"]}

    got = J.run(st, "mods_fp", fn)
    res, t = J.result(st, "mods_fp"), J.table(st, "mods_fp")
    ok(got == "done" and seen == [3, 4] and res["out"] == {"n": 4} and res["gen"] == t["gen"] == 4,
       "a request during the run is not lost: the job reran on it (computed %s, result gen %s, table gen %s)"
       % (seen, res and res["gen"], t["gen"]))
    ok(la.n == 1, "and the running job's own lock kept that request from launching a second job (%d)" % la.n)
    ok(not J.running(st, "mods_fp") and t["state"] == "done" and t["runs"] == 1, "the job ends done and lets go of its lock")


def t_duplicate_start_touches_nothing():
    st, la = store(), Launch()
    J.request(st, "mods_fp", {"n": 1}, la)
    J.run(st, "mods_fp", lambda w: {"v": "first"})
    before_t, before_r = J.table(st, "mods_fp"), J.result(st, "mods_fp")
    J.request(st, "mods_fp", {"n": 2}, la)
    fd = hold(st, "mods_fp")
    calls = []
    got = J.run(st, "mods_fp", lambda w: calls.append(w) or {"v": "dup"})
    os.close(fd)
    ok(got == "duplicate" and not calls, "a second job started while one runs exits duplicate without working (%s)" % got)
    ok(J.result(st, "mods_fp") == before_r, "and leaves the running job's result alone")
    t = J.table(st, "mods_fp")
    ok(t["state"] == "queued" and t["gen"] == before_t["gen"] + 1 and t.get("pid") == before_t.get("pid"),
       "and the table as the request left it (state %s)" % t["state"])


def t_kill_mid_job_reconciles_on_restart():
    st, la = store(), Launch()
    J.request(st, "mods_fp", {"n": 1}, la)
    J.run(st, "mods_fp", lambda w: {"v": "good"})
    J.request(st, "mods_fp", {"n": 2}, la)
    child = ("import sys, time; sys.path.insert(0, %r); import relentless as R, relentless_jobs as J; "
             "J.run(R.Store(%r), 'mods_fp', lambda w: time.sleep(60))" % (HERE, st.root))
    p = subprocess.Popen([sys.executable, "-c", child])
    deadline = time.time() + 20
    while time.time() < deadline and J.table(st, "mods_fp").get("state") != "running":
        time.sleep(0.05)
    ok(J.table(st, "mods_fp").get("state") == "running" and J.running(st, "mods_fp"), "the detached job is running")
    os.kill(p.pid, signal.SIGKILL)
    p.wait(timeout=20)
    t = J.table(st, "mods_fp")
    ok(t["state"] == "running" and not J.running(st, "mods_fp"),
       "killed mid-job: the table still says running, but no process holds the lock")
    ok((J.result(st, "mods_fp") or {}).get("out") == {"v": "good"}, "the last good answer survived the kill")
    acts, n0 = [], la.n
    J.reconcile(st, acts, la)
    t = J.table(st, "mods_fp")
    ok([a["do"] for a in acts] == ["job_lost", "job_relaunch"] and la.n == n0 + 1 and t["state"] == "queued"
       and t["lost"] == 1, "the next tick finds it lost and launches it again: %s" % acts)
    got = J.run(st, "mods_fp", lambda w: {"v": "fresh", "n": w["n"]})
    ok(got == "done" and J.result(st, "mods_fp")["out"] == {"v": "fresh", "n": 2},
       "the relaunched job answers the want the killed one never finished")
    acts = []
    J.reconcile(st, acts, la)
    ok(not acts and la.n == n0 + 1, "a finished job is not reconciled again: %s" % acts)
    # a queued row nobody ever started (the launch failed) is launched again; a live job is left alone
    J.request(st, "mods_fp", {"n": 3}, lambda k: "systemctl exit 5: no such unit")
    acts = []
    J.reconcile(st, acts, la)
    ok([a["do"] for a in acts] == ["job_relaunch"], "a launch that never started is retried by the next tick: %s" % acts)
    fd = hold(st, "mods_fp")
    J.request(st, "mods_fp", {"n": 4}, la)
    acts = []
    J.reconcile(st, acts, la)
    os.close(fd)
    ok(not acts, "a running job (lock held) is never called lost: %s" % acts)


def t_showing_reads_the_job_answer():
    st, la = store(), Launch()
    mods = tempfile.mkdtemp(prefix="relentless_jobs_mods_")
    os.makedirs(os.path.join(mods, "A", "About"))
    with open(os.path.join(mods, "A", "About", "About.xml"), "w") as f:
        f.write("<x/>")
    want = S.mods_fp(["A", "B"], mods)
    fp = J.ModsFp(st, mods, la)
    ok(fp(["B", "A"]) == want and fp.inline == 1 and fp.hits == 0, "a mod set the job has not answered is walked inline once")
    fp.close()
    ok(la.n == 1, "and a job is asked to fingerprint it")
    ok(J.run(st, "mods_fp") == "done", "the mods_fp job runs")
    fp = J.ModsFp(st, mods, la)
    ok(fp(["A", "B"]) == want and fp.hits == 1 and fp.inline == 0, "the next pass reads the job's answer, no walk")
    J.request(st, "mods_fp", {"root": mods, "sets": {"A\nB": ["A", "B"]}}, la)
    lag = J.ModsFp(st, mods, la)
    lag(["A", "B"])
    ok(lag.inline == 1 and lag.hits == 0, "an answer older than the newest request (job running, dead or failing) is "
       "not used: walked inline")
    J.run(st, "mods_fp")
    other = J.ModsFp(st, mods + "_elsewhere", la)
    other(["A", "B"])
    ok(other.inline == 1, "an answer for another Mods root is never used")
    bare = J.ModsFp(st, mods, None)
    ok(bare(["A", "B"]) == want and bare.inline == 1 and bare.close() is None and la.n == 2,
       "without a launcher it walks inline and asks nothing (the old behaviour)")
    ok(J.launcher(st, "mods_fp") is None, "a test store never launches the live unit")
    src = inspect.getsource(S.tick)
    ok("fpr(man[\"mods\"])" in src and "mods_fp(man" not in src, "the showing stage takes its fingerprint from ModsFp")
    ok("relentless_jobs.reconcile(" in inspect.getsource(R._tick), "every tick reconciles the job table")


def t_unchanged_answer_does_not_poke_the_tick():
    import relentless_wake
    pokes, real = [], relentless_wake.poke
    relentless_wake.poke = lambda *a, **k: pokes.append(a)
    try:
        st, la = store(), Launch()
        J.request(st, "mods_fp", {"n": 1}, la)
        J.run(st, "mods_fp", lambda w: {"v": "same"})
        ok(len(pokes) == 1, "the first answer pokes (%d)" % len(pokes))
        J.request(st, "mods_fp", {"n": 2}, la)
        J.run(st, "mods_fp", lambda w: {"v": "same"})
        ok(len(pokes) == 1, "the same answer again pokes nobody: no tick -> job -> tick loop (%d)" % len(pokes))
        J.request(st, "mods_fp", {"n": 3}, la)
        J.run(st, "mods_fp", lambda w: {"v": "changed"})
        ok(len(pokes) == 2, "a changed answer pokes (%d)" % len(pokes))
    finally:
        relentless_wake.poke = real


def main():
    for t in (t_request_launches_once_and_coalesces, t_duplicate_start_touches_nothing,
              t_kill_mid_job_reconciles_on_restart, t_showing_reads_the_job_answer,
              t_unchanged_answer_does_not_poke_the_tick):
        t()
    print("selftest_relentless_jobs: %s" % ("OK" if not FAILS else "FAILED %d" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
