#!/usr/bin/env python3
"""list_run_on_steve_accept.py - the acceptance test of RIMMANDRAKE_RUN_LIST_WORK_ON_STEVEDESKTOP_NO_SUPPORTED_WAY.

Offline. The contract it holds: src/RimMandrake/rimflow/run_host.py
  plan(host, item, brief_path, facts, model=, budget=) -> {"verdict": "LOCAL"|"REMOTE"|"REFUSED"|"COULD NOT LOOK", "why", "argv"}
    facts: {"reachable", "claude", "account", "picked_account", "push", "launcher", "clone", "free_gb"}; None = unread
  The REMOTE argv runs the host's own detached_helper.py launch (RIMMANDRAKE_FINISH_STEVE_HOST_LAUNCH_NEVER_RAN_ON_REAL_MACHINE
  retired the first contract, a bare systemd-run of claude in a clone that nobody made).
  stop_argv(rec) -> the argv that stops a run whose record names its host
and `detached_helper.py launch --host NAME`. Prints 12 checks; exit 0 all pass, 1 not. Base 2026-11-24: 0/12, exit 1.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RF = os.path.dirname(HERE)
sys.path.insert(0, RF)
GOOD = {"reachable": True, "claude": "2.1.331", "account": "a", "picked_account": "a", "push": True,
        "launcher": True, "clone": "~/rm/relentless/clones/ITEM_ONE.det", "free_gb": 800}
BAD = []


def check(name, fn):
    try:
        ok = bool(fn())
        why = ""
    except Exception as e:  # noqa: BLE001 - a missing module or function is a failed check
        ok, why = False, " (%s: %s)" % (type(e).__name__, e)
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, why))
    if not ok:
        BAD.append(name)


def P(host="stevedesktop", **kw):
    import run_host
    return run_host.plan(host, "ITEM_ONE", "/tmp/brief.md", dict(GOOD, **kw), model="sonnet", budget=5)


def argv():
    return [str(x) for x in P()["argv"]]


def launch_help():
    r = subprocess.run([sys.executable, os.path.join(RF, "detached_helper.py"), "launch", "--help"], capture_output=True,
                       text=True, timeout=120)
    return r.returncode == 0 and "--host" in r.stdout


check("this machine is LOCAL", lambda: P("archmagi")["verdict"] == "LOCAL")
check("the host's name in any letter case", lambda: P("SteveDesktop")["verdict"] == "REMOTE")
check("an unknown host is REFUSED by name", lambda: P("steve9")["verdict"] == "REFUSED" and "steve9" in P("steve9")["why"])
check("each unread fact is COULD NOT LOOK, named", lambda: all(
    P(**{k: None})["verdict"] == "COULD NOT LOOK" and k in P(**{k: None})["why"] for k in GOOD))
check("a machine that is down is COULD NOT LOOK", lambda: P(reachable=False)["verdict"] == "COULD NOT LOOK")
check("a login that is not the Dispatcher's pick is REFUSED", lambda: P(account="b")["verdict"] == "REFUSED")
check("no push route is REFUSED", lambda: P(push=False)["verdict"] == "REFUSED")
check("the test lane's own clones are REFUSED", lambda: all(
    P(clone=c)["verdict"] == "REFUSED" for c in ("~/rm/runner", "~/rm/runner_b", "/home/mandrake/rm/runner")))
check("a good plan runs the host's own launcher for the item", lambda: argv()[0] == "ssh"
      and "detached_helper.py launch" in " ".join(argv())
      and "ITEM_ONE" in " ".join(argv()) and P()["verdict"] == "REMOTE")
check("the plan never states a spend", lambda: "max-budget-usd" not in " ".join(argv()))
check("a stop reaches the host", lambda: (lambda a: a[0] == "ssh" and "u-1" in " ".join(a) and "stop" in " ".join(a))(
    [str(x) for x in __import__("run_host").stop_argv({"unit": "u-1", "host": "stevedesktop"})]))
check("detached_helper.py launch takes --host", launch_help)
print("%d/12" % (12 - len(BAD)))
sys.exit(1 if BAD else 0)
