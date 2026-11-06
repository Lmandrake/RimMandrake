#!/usr/bin/env python3
"""RELENTLESS_TICK_MEASURE_OUTLASTS_ITS_NAP. Every supervisor tick's journal row names the child processes it waited on,
by command, with their count and seconds, so the next slow tick says which command ate it (relentless_tickprof).

    python3 src/RimMandrake/rimflow/selftest_relentless_tick_profile.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R  # noqa: E402
import relentless_tickprof as P  # noqa: E402
import selftest_relentless as T  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def t_label():
    cases = {
        ("git", "fetch", "-q", "origin"): "git fetch",
        ("git", "--no-optional-locks", "status", "--porcelain"): "git status",
        ("git", "-C", "/x/y", "cherry", "a", "b"): "git cherry",
        ("python3", "/a/b/scratch_clone.py", "clone", "relentless"): "scratch_clone.py clone",
        ("/usr/bin/python3", "-I", "/a/publish.py", "-m", "msg"): "publish.py",
        ("python3", "-m", "pytest", "x"): "pytest x",
        ("/mnt/c/WINDOWS/system32/tasklist.exe", "/FO", "CSV"): "tasklist.exe",
    }
    for argv, want in cases.items():
        ok(P.label(list(argv)) == want, "label %r -> %r (got %r)" % (argv, want, P.label(list(argv))))
    ok(P.label("git log -1") == "git log", "a shell string is split")
    ok(P.label([]) == "?", "an empty argv is named, not raised on")


def t_tally():
    base = (subprocess.Popen.__init__, subprocess.Popen.wait)
    with P.Tally() as t:
        subprocess.run(["true"])
        subprocess.run(["true"])
        subprocess.check_output(["echo", "hi"])
        detached = subprocess.Popen(["sleep", "0.2"])       # nobody waits on it inside: a worker, never counted
    detached.wait()
    rows = {r["cmd"]: r for r in t.top()}
    ok(rows.get("true", {}).get("n") == 2 and rows.get("echo", {}).get("n") == 1, "run and check_output are counted: %s" % rows)
    ok("sleep" not in rows, "a child nobody waited on inside the tick is not counted")
    ok((subprocess.Popen.__init__, subprocess.Popen.wait) == base, "the patch is removed on exit")
    try:
        with P.Tally():
            raise ValueError("boom")
    except ValueError:
        pass
    ok((subprocess.Popen.__init__, subprocess.Popen.wait) == base, "and on an exception")
    outer = P.Tally().__enter__()       # a leaked patch (no exit) must not stack under the next one
    with P.Tally() as inner:
        subprocess.run(["true"])
    ok(inner.top()[0]["n"] == 1 and outer.top() == [], "a leaked patch is replaced, never stacked: %s %s"
       % (inner.top(), outer.top()))
    ok((subprocess.Popen.__init__, subprocess.Popen.wait) == base, "and the base is back after")


def t_tick_row():
    x = T.Rig(n=2, share=1.0, max_workers=10, staffing=dict(T.STAFF))
    real_sync = x.w.sync

    def sync_runs_git():
        subprocess.run(["git", "version"], capture_output=True)
        return real_sync()
    x.w.sync = sync_runs_git
    x.tick()
    with open(x.s.p("journal.jsonl"), encoding="utf-8") as f:
        ticks = [j for j in (json.loads(ln) for ln in f if ln.strip()) if j.get("do") == "tick"]
    ok(bool(ticks), "the tick wrote its journal row")
    row = ticks[-1] if ticks else {}
    cmds = {p["cmd"]: p for p in row.get("proc", [])}
    ok("git version" in cmds and cmds["git version"]["n"] == 1 and cmds["git version"]["s"] >= 0,
       "the tick's row names the child it waited on: %s" % row.get("proc"))
    ok(isinstance(row.get("proc_s"), float) and row["proc_s"] >= cmds.get("git version", {}).get("s", 0),
       "and the total of child seconds: %s" % row.get("proc_s"))
    ok((subprocess.Popen.__init__, subprocess.Popen.wait) == P._BASE, "the tick leaves subprocess unpatched")
    ok(isinstance(row.get("py_calls"), list) and isinstance(row.get("py_leaves"), list),
       "the row carries the in-process tallies too")


def t_sampler():
    """The in-process half: a tick's Python time is named by the call of the tick that spent it."""
    import time as _t

    def hot_call():
        end = _t.monotonic() + 0.6
        while _t.monotonic() < end:
            pass

    def _tick():
        hot_call()
        subprocess.run(["sleep", "0.3"])

    with P.Sampler(every=0.02) as s:
        _tick()
    calls = {r["at"]: r["s"] for r in s.top("calls")}
    leaves = {r["at"]: r["s"] for r in s.top("leaves")}
    ok(calls.get("selftest_relentless_tick_profile:hot_call", 0) >= 0.3,
       "the sampler names the tick's hot call: %s" % calls)
    ok(any(k.endswith("[child]") and "_tick" in k for k in leaves), "and marks time spent waiting on a child: %s" % leaves)
    ok(not s._t.is_alive(), "the sampler thread ends with the tick")


def main():
    for t in (t_label, t_tally, t_tick_row, t_sampler):
        t()
    print("selftest_relentless_tick_profile: %s" % ("OK" if not FAILS else "FAILED %d" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
