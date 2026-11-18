#!/usr/bin/env python3
"""soak_read.py - one-command reader of the SteveDesktop CPU soak (steve_cpu_soak.ps1, task 'SteveDiag CPU Soak').

    python3 src/RimMandrake/Utils/steve_cpu_retest/soak_read.py [--run RUN] [--json]

Prints: verdict (RUNNING / ENDED / STALLED / NOT_PLANNED / UNREACHABLE), run id, started, planned end, steps and passes
done, every FAIL step with CPU and time, reboots, the CONTROL result, the last reading and its age.
Exit codes keep the four answers apart: 0 = read, running or ended, instrument PROVEN by a passing CONTROL;
1 = read, but no passing CONTROL in this run (faults=0 is UNMEASURED, not clean); 2 = read, soak not running when it should
be (STALLED) or nothing planned; 3 = could not reach SteveDesktop (nothing is known about the soak).
"""
import argparse, json, os, re, sys, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FETCH_PS = r"""$sd='C:\SteveDesktop\diag\soak'
$t=Get-ScheduledTask 'SteveDiag CPU Soak' -EA 0
$h=[ordered]@{now=(Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ');
 boot=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ');
 task=$(if($t){[string]$t.State}else{'MISSING'}); prime95=@(Get-Process prime95 -EA 0).Count;
 state=$(if(Test-Path "$sd\state.json"){[IO.File]::ReadAllText("$sd\state.json")}else{$null})}
'SOAKREAD_HEADER ' + ($h | ConvertTo-Json -Compress)
'SOAKREAD_LOG'
if(Test-Path "$sd\soak.log"){ Get-Content "$sd\soak.log" }
'SOAKREAD_DONE'
"""

TS = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)Z (.*)$")


def epoch(iso):
    return datetime.strptime(iso.rstrip("Z"), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).timestamp()


def kv(text):
    return dict(p.split("=", 1) for p in text.split() if "=" in p)


def parse_fetch(out):
    """ssh stdout -> (header dict, log lines) or None when the answer is not a whole reading."""
    if "SOAKREAD_HEADER " not in out or "SOAKREAD_DONE" not in out:
        return None
    head_line = next(li for li in out.splitlines() if li.startswith("SOAKREAD_HEADER "))
    try:
        head = json.loads(head_line[len("SOAKREAD_HEADER "):])
        head["state"] = json.loads(head["state"]) if head.get("state") else None
    except (ValueError, TypeError):
        return None
    body = out.split("SOAKREAD_LOG", 1)[1].split("SOAKREAD_DONE", 1)[0]
    return head, [li.strip() for li in body.splitlines() if li.strip()]


def summarize(head, lines, run=None):
    """Pure: the reading -> a dict. run=None reads the run named in state.json (else the last SOAK START in the log)."""
    st = head.get("state") or {}
    run = run or st.get("run")
    if not run:
        starts = [kv(m.group(2)).get("run") for m in map(TS.match, lines) if m and m.group(2).startswith("SOAK START")]
        run = next((r for r in reversed(starts) if r), None)
    s = {"run": run, "started": None, "end_planned": None, "steps": 0, "passes_complete": 0, "fails": [],
         "reboots": [], "restarts": [], "waits": [], "controls": [], "ended": None, "last_step": None,
         "worker_probe": None}
    if run and st.get("run") == run:
        s["end_planned"] = st.get("end_utc")
    mine = False
    for li in lines:
        m = TS.match(li)
        if not m:
            continue
        ts, rest = m.group(1) + "Z", m.group(2)
        f = kv(rest)
        if rest.startswith(("SOAK PLAN", "SOAK START", "SOAK REBOOT", "SOAK RESUME", "SOAK RESTART", "SOAK END",
                            "SOAK INTERRUPTED", "SOAK REFUSED", "CONTROL", "PROBES")):
            mine = f.get("run", "").rstrip(":") == run
            if not mine:
                continue
            if rest.startswith("SOAK START"):
                s["started"] = ts
                s["end_planned"] = s["end_planned"] or f.get("end")
            elif rest.startswith("SOAK REBOOT"):
                s["reboots"].append({"at": ts, "boot": f.get("boot"), "prev_boot": f.get("prev_boot")})
            elif rest.startswith("SOAK RESTART"):
                s["restarts"].append(ts)
            elif rest.startswith("SOAK END"):
                s["ended"] = {"at": ts, "reason": rest.split("reason=", 1)[1] if "reason=" in rest else "?"}
            elif rest.startswith("CONTROL"):
                s["controls"].append({"at": ts, "ok": f.get("ok") == "1", "fields": f})
            elif rest.startswith("PROBES"):
                s["worker_probe"] = f.get("worker_probe")
            continue
        if not mine:
            continue
        if rest.startswith("pass="):
            s["steps"] += 1
            s["last_step"] = {"at": ts, "line": rest}
            if " FAIL " in rest:
                s["fails"].append({"at": ts, "pass": f.get("pass"), "cpu": f.get("cpu"),
                                   "why": rest.split(" FAIL ", 1)[1].split(" fatal=", 1)[0]})
        elif rest.startswith("PASS_COMPLETE"):
            s["passes_complete"] += 1
        elif rest.startswith("WAIT:"):
            s["waits"].append({"at": ts, "why": rest[5:].strip()})
    now = epoch(head["now"])
    s["last_reading_age_s"] = int(now - epoch(s["last_step"]["at"])) if s["last_step"] else None
    s["control_proven"] = bool(s["controls"]) and all(c["ok"] for c in s["controls"])
    alive = head.get("task") == "Running" or head.get("prime95", 0) > 0
    if not run or not s["started"]:
        s["verdict"] = "NOT_PLANNED" if not st or st.get("finished") or not run else ("RUNNING" if alive else "STALLED")
    elif s["ended"] or (st.get("run") == run and st.get("finished")):
        s["verdict"] = "ENDED"
    elif alive:
        s["verdict"] = "RUNNING"
    else:
        s["verdict"] = "STALLED"
    s.update(now=head["now"], boot=head.get("boot"), task=head.get("task"), prime95=head.get("prime95"))
    return s


def exit_code(s):
    if s["verdict"] in ("STALLED", "NOT_PLANNED"):
        return 2
    return 0 if s["control_proven"] else 1


def render(s):
    out = ["SOAK %s run=%s task=%s prime95=%s now=%s boot=%s" % (s["verdict"], s["run"], s["task"], s["prime95"],
                                                                 s["now"], s["boot"])]
    out.append("started=%s planned_end=%s steps=%d passes_complete=%d" % (s["started"], s["end_planned"], s["steps"],
                                                                        s["passes_complete"]))
    if not s["controls"]:
        out.append("CONTROL none in this run: fault count is UNMEASURED")
    for c in s["controls"]:
        out.append("CONTROL %s at %s (%s)" % ("PROVEN" if c["ok"] else "FAILED", c["at"],
                                              " ".join("%s=%s" % kv_ for kv_ in c["fields"].items() if kv_[0] != "run")))
    if s["steps"] == 0:
        out.append("faults: no step logged yet (UNMEASURED)")
    elif not s["fails"]:
        out.append("faults=0 in %d steps%s" % (s["steps"], "" if s["control_proven"] else " (UNMEASURED: instrument unproven)"))
    else:
        out.append("faults=%d in %d steps:" % (len(s["fails"]), s["steps"]))
        out += ["  FAIL %s pass=%s cpu=%s %s" % (f["at"], f["pass"], f["cpu"], f["why"]) for f in s["fails"]]
    out.append("reboots=%d%s" % (len(s["reboots"]), "".join(" [%s boot=%s]" % (r["at"], r["boot"]) for r in s["reboots"])))
    if s["restarts"]:
        out.append("task restarts same boot=%d" % len(s["restarts"]))
    if s["waits"]:
        out.append("waits=%d last: %s %s" % (len(s["waits"]), s["waits"][-1]["at"], s["waits"][-1]["why"]))
    if s["ended"]:
        out.append("ENDED %s reason=%s" % (s["ended"]["at"], s["ended"]["reason"]))
    if s["last_step"]:
        out.append("last reading %ds old: %s %s" % (s["last_reading_age_s"], s["last_step"]["at"], s["last_step"]["line"]))
    else:
        out.append("last reading: none")
    if s["worker_probe"] == "blind":
        out.append("note: the testq-worker probe is blind under SYSTEM; only a running RimWorldWin64 makes the soak wait")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", help="read this run id instead of the one in state.json")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    import steve_cpu_retest as rt
    rc, out = rt.ps(FETCH_PS, timeout=120)
    got = parse_fetch(out or "") if rc is not None else None
    if got is None:
        print("SOAK UNREACHABLE: could not read SteveDesktop (%s); nothing is known about the soak" %
              ("ssh down or timed out" if rc is None else "rc=%s, no whole reading in the answer" % rc))
        return 3
    s = summarize(got[0], got[1], a.run)
    print(json.dumps(s, indent=1) if a.json else render(s))
    return exit_code(s)


if __name__ == "__main__":
    sys.exit(main())
