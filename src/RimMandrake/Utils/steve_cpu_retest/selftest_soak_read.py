#!/usr/bin/env python3
"""selftest_soak_read.py - the soak reader's four answers kept apart, offline (Steve faked).
Proves: UNREACHABLE (ssh down, or a partial answer) exits 3 and claims nothing; a running run with a passing CONTROL reads
RUNNING exit 0 with its FAIL steps (CPU, time) and reboots counted, and an older run's lines in the same log are not
counted; no CONTROL or a failed CONTROL exits 1 and calls faults=0 UNMEASURED; a planned run whose task and Prime95 are
both gone reads STALLED exit 2; nothing planned reads NOT_PLANNED exit 2; an ENDED run carries its reason."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import soak_read as m
import steve_cpu_retest as rt

fails = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


RUN = "S20261118T012929Z"
STATE = {"run": RUN, "end_utc": "2026-11-21T01:29:29Z", "started": True, "finished": None, "boot": "2026-11-17T19:51:20Z"}
OLD = ["2026-11-17T18:51:58Z SOAK START hours=6 end=2026-11-18T00:51:58Z cpus=18",
       "2026-11-17T19:09:30Z pass=2 cpu=2 FAIL prime95_error x1 fatal=1 whea=0 alive=1 heat=pkg_c=46/47",
       "2026-11-17T19:17:06Z SOAK END steps=32 passes_started=2 reason=YIELD: STOP file"]
CTL_OK = "2026-11-18T01:30:00Z CONTROL run=%s inject_fatal_seen=1 inject_died_seen=1 heat_seen=1 load_seen=1 load=100 ok=1" % RUN
CTL_BAD = CTL_OK.replace("inject_fatal_seen=1", "inject_fatal_seen=0").replace("ok=1", "ok=0")
NEW = ["2026-11-18T01:29:29Z SOAK PLAN run=%s hours=72 end=2026-11-21T01:29:29Z" % RUN,
       "2026-11-18T01:29:32Z SOAK START run=%s hours=72 end=2026-11-21T01:29:29Z cpus=18 boot=2026-11-17T19:51:20Z" % RUN,
       "2026-11-18T01:29:32Z PROBES run=%s worker_probe=blind rimworld=0" % RUN]
STEPS = ["2026-11-18T01:31:00Z pass=1 cpu=0 PASS fatal=0 whea=0 alive=1 load=100 heat=pkg_c=40/41 core_max_c=41",
         "2026-11-18T01:31:46Z pass=1 cpu=1 FAIL prime95_error x1 fatal=1 whea=0 alive=1 load=100 heat=x",
         "2026-11-18T01:32:31Z pass=1 cpu=2 FAIL WHEA x2 fatal=0 whea=2 alive=1 load=99 heat=x",
         "2026-11-18T01:47:00Z PASS_COMPLETE pass=1",
         "2026-11-18T03:00:00Z SOAK REBOOT run=%s boot=2026-11-18T02:58:00Z prev_boot=2026-11-17T19:51:20Z" % RUN,
         "2026-11-18T03:00:00Z SOAK RESUME run=%s end=2026-11-21T01:29:29Z cpus=18" % RUN,
         "2026-11-18T03:01:00Z pass=1 cpu=0 PASS fatal=0 whea=0 alive=1 load=100 heat=x"]


def head(now="2026-11-18T03:01:30Z", task="Running", p95=1, state=STATE):
    return {"now": now, "boot": "2026-11-18T02:58:00Z", "task": task, "prime95": p95, "state": state}


def fetch_text(h, lines):
    hh = dict(h)
    hh["state"] = json.dumps(h["state"]) if h["state"] else None
    return "SOAKREAD_HEADER %s\nSOAKREAD_LOG\n%s\nSOAKREAD_DONE\n" % (json.dumps(hh), "\n".join(lines))


# UNREACHABLE: ssh down, and a cut-off answer, both exit 3 and print no soak fact
for label, fake in (("ssh down", (None, "")), ("partial answer", (0, "SOAKREAD_HEADER {\"now\":1}\nSOAKREAD_LOG\n"))):
    rt.ps = lambda script, timeout=90, f=fake: f
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = m.main([])
    check(rc == 3 and "UNREACHABLE" in buf.getvalue() and "faults" not in buf.getvalue(), "unreachable (%s) -> exit 3, no claim" % label)

# the round trip through the fetch format
got = m.parse_fetch(fetch_text(head(), OLD + NEW + [CTL_OK] + STEPS))
check(got is not None and got[0]["state"]["run"] == RUN and len(got[1]) == len(OLD + NEW + STEPS) + 1, "fetch text parses whole")

s = m.summarize(*got)
check(s["verdict"] == "RUNNING" and m.exit_code(s) == 0, "running + passing control -> RUNNING exit 0")
check(s["steps"] == 4 and s["passes_complete"] == 1, "steps and passes counted for this run only (old run's step ignored)")
check([(f["cpu"], f["at"]) for f in s["fails"]] == [("1", "2026-11-18T01:31:46Z"), ("2", "2026-11-18T01:32:31Z")],
      "every FAIL step listed with CPU and time; the old run's FAIL is not")
check("prime95_error x1" in s["fails"][0]["why"] and "WHEA x2" in s["fails"][1]["why"], "FAIL causes kept")
check(len(s["reboots"]) == 1 and s["reboots"][0]["boot"] == "2026-11-18T02:58:00Z", "a reboot is a data point")
check(s["last_reading_age_s"] == 30, "last reading age measured from Steve's clock")
check(s["started"] == "2026-11-18T01:29:32Z" and s["end_planned"] == "2026-11-21T01:29:29Z", "start and planned end")
check(s["worker_probe"] == "blind" and "blind" in m.render(s), "a blind worker probe is said, not hidden")

s = m.summarize(*m.parse_fetch(fetch_text(head(), OLD + NEW + [STEPS[0]])))
check(m.exit_code(s) == 1 and "UNMEASURED" in m.render(s) and not s["fails"], "no CONTROL -> exit 1, faults=0 UNMEASURED")
s = m.summarize(*m.parse_fetch(fetch_text(head(), OLD + NEW + [CTL_BAD, STEPS[0]])))
check(m.exit_code(s) == 1 and "CONTROL FAILED" in m.render(s) and "UNMEASURED" in m.render(s), "failed CONTROL -> exit 1")
s = m.summarize(*m.parse_fetch(fetch_text(head(), OLD + NEW + [CTL_OK])))
check("no step logged yet" in m.render(s) and s["last_reading_age_s"] is None, "no step yet -> UNMEASURED, age None (not 0)")

s = m.summarize(*m.parse_fetch(fetch_text(head(task="Ready", p95=0), OLD + NEW + [CTL_OK] + STEPS)))
check(s["verdict"] == "STALLED" and m.exit_code(s) == 2, "task and Prime95 gone mid-run -> STALLED exit 2")

ended = OLD + NEW + [CTL_OK] + STEPS + ["2026-11-21T01:29:00Z SOAK END run=%s steps=900 passes_started=200 fails=2 reason=END: time" % RUN]
st_done = dict(STATE, finished="END: time")
s = m.summarize(*m.parse_fetch(fetch_text(head(task="Ready", p95=0, state=st_done), ended)))
check(s["verdict"] == "ENDED" and m.exit_code(s) == 0 and s["ended"]["reason"] == "END: time", "ENDED carries its reason, exit 0")

s = m.summarize(*m.parse_fetch(fetch_text(head(task="Ready", p95=0, state=None), OLD)))
check(s["verdict"] == "NOT_PLANNED" and m.exit_code(s) == 2, "nothing planned -> NOT_PLANNED exit 2")

s = m.summarize(*m.parse_fetch(fetch_text(head(), OLD + NEW + [CTL_OK] + STEPS)), run="S20990101T000000Z")
check(s["steps"] == 0 and not s["started"], "--run of an absent run reads nothing of the others")

print("%d FAIL" % len(fails) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
