#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_HONOUR_DATED_WAIT_BEFORE_CONTINUING_TWICE_IDLE.

A run that ends success with a LEFT OPEN note on an item under a dated `rimflow wait` (still ahead) is NOT continued:
the wait is the item's own word that nothing can move before its date, so a continuation only burns a run. A wait
whose date has passed, or an item with no wait, continues as before. The finish-time item read (detached_helper
READ_ITEM) carries the wait so `plan` can see it. Exit 0 = every check passes."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
TMP = tempfile.mkdtemp(prefix="continue_honours_wait_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
sys.path.insert(0, RIMFLOW)
import detached_helper as DH  # noqa: E402
import left_open_continue as LOC  # noqa: E402

T0 = 1_800_000_000.0
ITEM = "RIMMANDRAKE_WAIT_ON_A_SOAK_FOR_THREE_DAYS"
FAILS = []
NO_GATES = {"paused": lambda m: None, "held": lambda m: None, "voided": lambda u: False, "blocked": lambda s: None}


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -- " + detail))
    if not ok:
        FAILS.append(name)


def run_rec(at):
    unit = "rm-detached-bench-accept-%d" % int(at)
    src = os.path.join(DH.runs_dir(), unit + ".brief.src.md")
    with open(src, "w", encoding="utf-8") as f:
        f.write("Do the ticket.")
    rec = {"unit": unit, "seat": "BENCH", "item": ITEM, "at": at, "status": "finished",
           "result": "success (exited 0)", "ended": at + 600, "brief_src": src}
    DH.write_record(rec)
    return rec


def got(wait_until):
    g = {"state": "doing", "notes": [{"event": "note", "id": ITEM, "ts": DH.iso(T0 + 500),
                                      "text": "LEFT OPEN: blocked on the soak"}]}
    if wait_until is not None:
        g["wait_until"] = wait_until
    return g


now = T0 + 700
p = LOC.plan(run_rec(T0), got(DH.iso(now + 3 * 86400)), {}, now=now, gates=NO_GATES)
check("a wait still ahead: no continuation", p.get("act") == "none" and "wait" in str(p.get("why")), str(p))
p = LOC.plan(run_rec(T0 + 1), got(DH.iso(now - 60)), {}, now=now, gates=NO_GATES)
check("a wait whose date has passed: continues", p.get("act") == "continue", str(p))
p = LOC.plan(run_rec(T0 + 2), got(None), {}, now=now, gates=NO_GATES)
check("no wait: continues", p.get("act") == "continue", str(p))
p = LOC.plan(run_rec(T0 + 3), got("not a date"), {}, now=now, gates=NO_GATES)
check("an unreadable wait date: no continuation, named", p.get("act") == "none" and "wait" in str(p.get("why")), str(p))

# READ_ITEM, run against a scratch ledger holding a claimed-then-waited item, reports the wait.
clone = os.path.join(TMP, "clone")
os.makedirs(os.path.join(clone, "src", "RimMandrake"))
os.symlink(RIMFLOW, os.path.join(clone, "src", "RimMandrake", "rimflow"))
code = ("import json,os,sys;sys.path.insert(0,os.path.join('src','RimMandrake','rimflow'));import model;"
        "it=type('I',(),{'state':'doing','wait_until':'2099-01-01T00:00:00Z'})();"
        "model.read=lambda:[];model.replay=lambda evs:type('W',(),{'items':{sys.argv[1]:it}})();"
        "exec(compile(open(sys.argv[2]).read().split('import model',1)[1],'r','exec'))")
helper = os.path.join(TMP, "read_item.py")
with open(helper, "w", encoding="utf-8") as f:
    f.write(DH.READ_ITEM)
r = subprocess.run([sys.executable, "-c", code, ITEM, helper], cwd=clone, capture_output=True, text=True, timeout=60)
try:
    out = json.loads(r.stdout)
except ValueError:
    out = {"unparsed": r.stdout + r.stderr}
check("READ_ITEM carries wait_until", out.get("wait_until") == "2099-01-01T00:00:00Z", str(out)[:300])

print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
