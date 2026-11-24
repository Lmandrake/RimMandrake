#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_LENGTHEN_WAITS_UNDER_ONE_HOUR_CACHE_DIES_AFTER (rank 7 of one_page.md).

Contract:
  1. design/specs/2026-11-23-long-waits/experiment.json, written by the FIRST act of the item from one real detached run:
     {"setting": "BASH_MAX_TIMEOUT_MS", "unit", "asked_s", "call_lasted_s", "cut_by_harness": bool,
      "cache_rebuilt_after": bool, "evidence": path or text}. The setting is used only when the call outlived 660 s, was
     not cut, and the turn after it did not rebuild the prompt cache.
  2. detached_helper.launch_argv sets BASH_MAX_TIMEOUT_MS in the unit, between 30 and 59 minutes (a wait past 59 minutes
     rebuilt the whole cache in 17 of 18 measured gaps).
  3. src/RimMandrake/Utils/waitalive.py
       run [--name N] [--max DUR] [--silence DUR] [--progress FILE] -- CMD...     start CMD and wait for it
       attach NAME [--max DUR] [--silence DUR]                                    wait again for one started earlier
     The sign of life is growth of CMD's output, of the progress file, or of the CPU time of its process tree. It prints
     one verdict line last, kills nothing, and exits: 0 FINISHED rc=0 | 1 FINISHED rc=N | 2 usage | 3 HUNG (pid named) |
     4 STILL RUNNING at --max | 5 COULD NOT LOOK (no such job, state unreadable) | 6 DIED with no exit code.
     The started job holds no pipe of the caller (else the call never returns). 3 and 4 print `pid <n>`: the leader of the job's own process group. Its state folder is $WAITALIVE_STATE.
Expected when built: PASS 14/14."""
import json
import os
import re
import signal
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

TOOL = os.path.join(H.UTILS, "waitalive.py")
ENV = dict(os.environ, WAITALIVE_STATE=tempfile.mkdtemp())
EXP = os.path.join(H.REPO, "design/specs/2026-11-23-long-waits/experiment.json")


def wa(*a):
    if not os.path.isfile(TOOL):
        raise RuntimeError("no file src/RimMandrake/Utils/waitalive.py")
    r = subprocess.run([sys.executable, TOOL] + list(a), env=ENV, capture_output=True, text=True, timeout=60,
                       stdin=subprocess.DEVNULL)
    return r.returncode, (r.stdout + r.stderr).strip()


def end(out):
    for p in re.findall(r"pid[ =](\d+)", out):
        try:
            os.kill(int(p), signal.SIGKILL)
        except OSError:
            pass


def last(out):
    return out.splitlines()[-1] if out else ""


H.check("a job that ends well: 0 and FINISHED rc=0", lambda: (
    lambda r: r[0] == 0 and "FINISHED rc=0" in last(r[1]))(wa("run", "--", "sh", "-c", "echo hi")))
H.check("a job that fails: 1 and its own code, never 0", lambda: (
    lambda r: r[0] == 1 and "rc=7" in last(r[1]))(wa("run", "--", "sh", "-c", "exit 7")))
H.check("a silent, idle job: HUNG with its pid, inside the silence bound, not killed", lambda: (
    lambda r: (end(r[1]), r[0] == 3 and "HUNG" in last(r[1]) and re.search(r"pid[ =]\d+", r[1]))[1])(
        wa("run", "--max", "40s", "--silence", "2s", "--", "sleep", "30")))
H.check("a slow job that prints is alive past the silence bound", lambda: wa(
    "run", "--max", "40s", "--silence", "2s", "--", "sh", "-c", "for i in 1 2 3 4 5 6 7 8 9; do echo $i; sleep 0.5; done")[0] == 0)
H.check("a silent job that burns CPU is alive", lambda: wa(
    "run", "--max", "40s", "--silence", "2s", "--", sys.executable, "-c",
    "import time\nt=time.time()\nwhile time.time()-t<5: pass")[0] == 0)


def attach():
    rc, out = wa("run", "--name", "j1", "--max", "2s", "--silence", "20s", "--", "sh", "-c",
                 "for i in 1 2 3 4 5 6 7 8 9 10; do echo $i; sleep 0.5; done")
    if rc != 4 or "STILL RUNNING" not in last(out):
        raise RuntimeError("at --max: rc %s, %s" % (rc, last(out)))
    rc, out = wa("attach", "j1", "--max", "30s", "--silence", "20s")
    return rc == 0 and "FINISHED rc=0" in last(out)


H.check("at --max the job keeps running, and attach takes its end", attach)
H.check("a job nobody started: COULD NOT LOOK, never finished", lambda: (
    lambda r: r[0] == 5 and "COULD NOT LOOK" in last(r[1]))(wa("attach", "never_started_job")))


def died():
    rc, out = wa("run", "--name", "k1", "--max", "1s", "--silence", "20s", "--", "sleep", "40")
    m = re.search(r"pid[ =](\d+)", out)
    if rc != 4 or not m:
        raise RuntimeError("at --max: rc %s, %s" % (rc, last(out)))
    os.killpg(int(m.group(1)), signal.SIGKILL)
    rc, out = wa("attach", "k1", "--max", "20s", "--silence", "10s")
    return rc == 6 and "DIED" in last(out)


H.check("a job killed from outside: DIED, apart from a failure and from hung", died)
H.check("no command: usage, exit 2", lambda: wa("run", "--")[0] == 2)


def setting():
    import detached_helper as DH
    rec = {"unit": "rm-detached-t", "seat": "BENCH", "item": "X", "clone": "/tmp/c", "model": "opus", "budget_usd": 0.0,
           "max_s": None, "out": "/tmp/o", "err": "/tmp/e", "state": "/tmp/s", "brief_file": "/tmp/b", "at": 0}
    m = re.search(r"BASH_MAX_TIMEOUT_MS=(\d+)", " ".join(DH.launch_argv(rec, "m", "/usr/bin/claude")))
    if not m:
        raise RuntimeError("launch_argv sets no BASH_MAX_TIMEOUT_MS")
    return 1_800_000 <= int(m.group(1)) <= 3_540_000


H.check("the detached unit gets the setting, 30 to 59 minutes", setting)


def exp():
    with open(EXP) as f:
        return json.load(f)


H.check("the experiment was run in a real detached unit, outlived 660 s and was not cut", lambda: (
    lambda e: e["setting"] == "BASH_MAX_TIMEOUT_MS" and bool(e["unit"]) and e["call_lasted_s"] > 660
    and e["cut_by_harness"] is False)(exp()))
H.check("the experiment read the cache after the wait, and it stood", lambda: exp()["cache_rebuilt_after"] is False)
H.check("the page names its promises", lambda: H.page(
    "design/specs/2026-11-23-long-waits/boundary.md", "a-hung-job-is-named", "a-failure-is-never-finished-well",
    "no-wait-outlives-the-cache"))
H.check("its selftest runs at ./publish", lambda: H.listed("src/RimMandrake/Utils/selftest_waitalive.py"))
H.done(14)
