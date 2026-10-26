#!/usr/bin/env python3
"""testq.py - the test queue and its no-LLM dispatcher (TESTQ_DISPATCHER_BUILD_SSH_NO_LLM).

Plan: design/RimMandrake/test_orchestration_two_machines_2026-10-25.md sections 3 and 6. Records: schema.py.

  testq.py submit MOD --chains a,b | --rows r1,r2 | --item ID | --full   --purpose P --by SEAT --sha SHA [...]
  testq.py list [--state pending|running|done|cancelled]
  testq.py show JOB                  at most 20 lines: state, selection, attempt, outcome, the failing rows
  testq.py cancel JOB --reason R     pending -> cancelled; running -> the worker is told to stop
  testq.py resume --reason R         lift a lane pause (paused.json) once its cause is dealt with
  testq.py tick                      one dispatch pass (a systemd user timer runs it every 60 s)
  testq.py install-timer [--apply]   that timer: testq-tick.{service,timer} in the user manager, ticking from the
                                     dispatch clone (~/rm/dispatch, pulled before every tick, never an agent's clone),
                                     then ingest.py (results -> RUNNER ledger events, committed from that clone).
                                     The clone may be sparse: it needs src/RimMandrake/{Utils/testq,rimflow} and
                                     infrastructure/state.

The queue is plain files under TESTQ_QUEUE (default /mnt/d/ClaudeWork/rimmandrake/testq):
  pending/<job>.json   the job record
  running/<job>.json   {"job", "attempt", "sent", "attempts", "auto_retries", "cancel"}
  done/<job>.json      {"job", "result", "attempts", "finished"}   - the last attempt's testq.result/1
  cancelled/<job>.json {"job", "reason", "at"}
  orphans/<attempt>.json  a worker result for a job this queue never sent (kept, acked)
  ssh_state.json, train.json, tick.log, tick.lock
  paused.json          the lane is paused (design section 6): {since, job, attempt, outcome, cause, reason, note}

One tick, under a non-blocking lock (a second tick while one runs exits at once):
  1. SSH: while SteveDesktop is unreachable nothing is sent; it is probed again every TESTQ_PROBE_S (300 s).
  2. Reconcile each running job by asking the worker for the job's LATEST attempt id first, so a retry is never
     sent twice: finished -> fetch the result, move to done/, ack it; dead -> `start` again without --retry
     (the worker finalizes the dead attempt and answers with it); a finished INTERRUPTED/CRASH or INVALID/GAME_DIED
     attempt gets ONE automatic `start --retry`. A job finishing INVALID/CANARY (a red canary) or REFUSED/SYNC (the
     runner pull failed) PAUSES the lane: paused.json is written and ingest.py files a finding.
  3. Drain the worker's outbox: duplicates of results already in done/ are acked; results for jobs the queue
     does not know go to orphans/ and are acked.
  4. Admit one ready job when the lane is idle and not paused: no owner_gate, not_before passed, lane stevedesktop or any;
     highest priority first, then the current train (same profile as the last job sent), then oldest.
     The worker's exit 75 (busy) leaves it pending.
Archmagi lane: jobs with lane=archmagi stay pending; the dispatcher never drives Archmagi's game (the BENCH seat
holds that bridge). TESTQ_ARCHMAGI=1 is reserved for that backfill and today only reports it is not built.
"""
import argparse
import fcntl
import glob
import json
import os
import shlex
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import schema as S  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
QHOME = os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq")
STATES = ("pending", "running", "done", "cancelled")
# How SteveDesktop's WSL is reached: the same env and default as rimflow/host_guard.py's SSH_TARGETS.
SSH_TARGET = os.environ.get("STEVE_WSL", "mandrake@stevedesktop-wsl")
SSH = shlex.split(os.environ.get("TESTQ_SSH", "ssh -o BatchMode=yes -o ConnectTimeout=15 -o LogLevel=ERROR"))
REMOTE_RUNNER = os.environ.get("TESTQ_REMOTE_RUNNER", "~/rm/runner")
PROBE_S = int(os.environ.get("TESTQ_PROBE_S", "300"))
# a dead attempt (machine reboot, OOM) or a game that died mid-run: one automatic retry
AUTO_RETRY = {("INTERRUPTED", "CRASH"), ("INVALID", "GAME_DIED")}
# design section 6: these pause the lane until `resume`, and ingest.py files a finding for each
PAUSE_ON = {("INVALID", "CANARY"): "the vanilla canary was red after a load",
            ("REFUSED", "SYNC"): "the runner pull/pin failed (someone wrote in the runner clone?)"}
EX_BUSY = 75


class SshDown(Exception):
    pass


def q(*parts):
    return os.path.join(QHOME, *parts)


def ensure_dirs():
    for d in STATES + ("orphans",):
        os.makedirs(q(d), exist_ok=True)


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def log(msg):
    line = "%s %s" % (S.utcnow(), msg)
    with open(q("tick.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def where(job_id):
    for st in STATES:
        if os.path.exists(q(st, job_id + ".json")):
            return st
    return None


def move(job_id, src, dst, record):
    """Write the record into dst/ (atomic), then drop it from src/."""
    S.dump(record, q(dst, job_id + ".json"))
    if src != dst:
        try:
            os.remove(q(src, job_id + ".json"))
        except FileNotFoundError:
            pass


def records(state):
    out = []
    for f in sorted(glob.glob(q(state, "*.json"))):
        r = read_json(f)
        if r is not None:
            out.append(r)
    return out


def job_of(rec):
    return rec if rec.get("schema") == S.JOB_SCHEMA else rec.get("job") or {}


# ---------------------------------------------------------------- the worker, over ssh

def remote(args, stdin=None, timeout=180):
    """Run `worker.py ARGS` in SteveDesktop's runner clone -> (exit code, last JSON line). SshDown on ssh failure."""
    cmd = "cd %s && python3 infrastructure/stevedesktop/worker.py %s" % (
        REMOTE_RUNNER, " ".join(shlex.quote(a) for a in args))
    try:
        r = subprocess.run(SSH + [SSH_TARGET, cmd], input=stdin, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise SshDown("ssh timed out after %d s: worker.py %s" % (timeout, " ".join(args)))
    if r.returncode == 255:
        raise SshDown((r.stderr.strip() or "ssh exit 255")[-200:])
    lines = r.stdout.strip().splitlines()
    try:
        return r.returncode, json.loads(lines[-1])
    except (ValueError, IndexError):
        return r.returncode, {"error": "no JSON from worker (exit %d): %s" % (r.returncode, (r.stdout + r.stderr)[-300:])}


def ssh_reachable():
    """False while SteveDesktop is marked down and the next probe is not due; otherwise probe it."""
    st = read_json(q("ssh_state.json")) or {}
    if st.get("down_since") and time.time() - st.get("last_probe", 0) < PROBE_S:
        return None
    try:
        rc, status = remote(["status"], timeout=60)
    except SshDown as e:
        st.update(down_since=st.get("down_since") or S.utcnow(), last_probe=time.time(), last_error=str(e))
        S.dump(st, q("ssh_state.json"))
        log("ssh DOWN (since %s): %s; next probe in %d s" % (st["down_since"], e, PROBE_S))
        return None
    if st.get("down_since"):
        log("ssh back after being down since %s" % st["down_since"])
    S.dump({"down_since": None, "last_probe": time.time(), "last_error": None}, q("ssh_state.json"))
    return status


# ---------------------------------------------------------------- the tick

def reconcile(rec):
    job = rec["job"]
    jid = job["id"]
    rc, st = remote(["status", "--job", jid])
    latest, state = st.get("attempt"), st.get("state")
    if latest and latest != rec.get("attempt"):          # the worker knows a newer attempt: follow it
        rec["attempts"] = sorted(set(rec.get("attempts", []) + [latest]), key=lambda a: int(a.rsplit(".a", 1)[1]))
        rec["attempt"] = latest
        move(jid, "running", "running", rec)
    if state == "running":
        return
    if state == "dead":
        rc, o = remote(["start"], stdin=json.dumps(job))
        log("%s attempt %s dead: worker finalized it (%s)" % (jid, latest, o.get("state")))
        return
    if state in (None, "none") or not latest:
        rec.pop("attempt", None)
        move(jid, "running", "pending", job)
        log("%s: the worker has no attempt for it (%s); back to pending" % (jid, st.get("error") or state))
        return
    rc, res = remote(["result", "--attempt", latest])
    if res.get("schema") != S.RESULT_SCHEMA:
        log("%s: result for %s unreadable: %s" % (jid, latest, res.get("error")))
        return
    if (res["outcome"], res["cause"]) in AUTO_RETRY and rec.get("auto_retries", 0) < 1 and not rec.get("cancel"):
        rc, o = remote(["start", "--retry"], stdin=json.dumps(job))
        if o.get("attempt"):
            rec.update(attempt=o["attempt"], auto_retries=rec.get("auto_retries", 0) + 1,
                       attempts=rec.get("attempts", []) + [o["attempt"]])
            move(jid, "running", "running", rec)
            remote(["ack", "--attempt", latest])
            log("%s attempt %s %s/%s: one automatic retry -> %s" % (jid, latest, res["outcome"], res["cause"],
                                                                     o["attempt"]))
            return
    finish(rec, res)


def finish(rec, res):
    jid = rec["job"]["id"]
    move(jid, "running", "done", {"job": rec["job"], "result": res, "attempts": rec.get("attempts") or [res["attempt"]],
                                  "cancelled": bool(rec.get("cancel")), "finished": S.utcnow()})
    remote(["ack", "--attempt", res["attempt"]])
    log("%s DONE-> %s %s %s (%s)" % (jid, res["outcome"], res["cause"] or "", res.get("counts"), res["attempt"]))
    why = PAUSE_ON.get((res["outcome"], res["cause"]))
    if why and not rec.get("cancel") and not paused():
        S.dump({"since": S.utcnow(), "job": jid, "attempt": res["attempt"], "outcome": res["outcome"],
                "cause": res["cause"], "reason": why, "note": (res.get("note") or "")[-300:]}, q("paused.json"))
        log("LANE PAUSED by %s %s/%s: %s; `testq.py resume --reason R` lifts it" % (jid, res["outcome"],
                                                                                 res["cause"], why))


def paused():
    return read_json(q("paused.json"))


def drain_outbox(outbox):
    running = {r["job"]["id"] for r in records("running")}
    for aid in outbox:
        jid = aid.rsplit(".a", 1)[0]
        if jid in running:
            continue
        done = read_json(q("done", jid + ".json"))
        if done and aid in done.get("attempts", []) + [done["result"]["attempt"]]:
            remote(["ack", "--attempt", aid])
            continue
        rc, res = remote(["result", "--attempt", aid])
        if res.get("schema") == S.RESULT_SCHEMA:
            S.dump(res, q("orphans", aid + ".json"))
            remote(["ack", "--attempt", aid])
            log("orphan result %s (%s %s) kept in orphans/" % (aid, res.get("outcome"), res.get("cause") or ""))


def ready(job, now):
    if job.get("owner_gate"):
        return False
    if job.get("not_before") and S.parse_ts(job["not_before"]) > now:
        return False
    return job.get("lane") in ("stevedesktop", "any")


def admit(status):
    if records("running") or paused():
        return
    if status.get("busy"):
        log("worker busy with %s (not ours); nothing admitted" % status.get("current"))
        return
    now = time.time()
    train = (read_json(q("train.json")) or {}).get("profile")
    cands = [j for j in records("pending") if ready(j, now)]
    if not cands:
        if os.environ.get("TESTQ_ARCHMAGI") == "1" and any(j.get("lane") == "archmagi" for j in records("pending")):
            log("archmagi lane requested but not built: archmagi jobs stay pending")
        return
    cands.sort(key=lambda j: (-j["priority"], j["profile"] != train, j["submitted"], j["id"]))
    job = cands[0]
    rc, o = remote(["start"], stdin=json.dumps(job))
    if rc == EX_BUSY:
        log("%s: worker busy (%s); stays pending" % (job["id"], o.get("busy_with")))
        return
    if not o.get("attempt"):
        log("%s: start failed (exit %d): %s; stays pending" % (job["id"], rc, o.get("error") or o))
        return
    move(job["id"], "pending", "running", {"job": job, "attempt": o["attempt"], "sent": S.utcnow(),
                                           "attempts": [o["attempt"]], "auto_retries": 0, "cancel": False})
    S.dump({"profile": job["profile"], "at": S.utcnow()}, q("train.json"))
    log("%s admitted -> %s (%s, prio %d, %s)%s" % (job["id"], o["attempt"], job["purpose"], job["priority"],
                                                   job["profile"], " duplicate" if o.get("duplicate") else ""))


def cmd_tick(_a):
    ensure_dirs()
    with open(q("tick.lock"), "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("tick already running")
            return 0
        status = ssh_reachable()
        if status is None:
            return 0
        try:
            for rec in records("running"):
                reconcile(rec)
            drain_outbox(remote(["outbox"])[1].get("outbox") or [])
            admit(remote(["status"])[1])
        except SshDown as e:
            S.dump({"down_since": S.utcnow(), "last_probe": time.time(), "last_error": str(e)}, q("ssh_state.json"))
            log("ssh dropped mid-tick: %s" % e)
    return 0


# ---------------------------------------------------------------- queue verbs

def same_request(a, b):
    keys = ("mod", "selector", "purpose", "source_sha", "item", "profile", "lane", "deploy", "canary", "validity",
            "owner_gate", "not_before")
    return all(a.get(k) == b.get(k) for k in keys)


def published(sha):
    r = subprocess.run(["git", "-C", REPO, "merge-base", "--is-ancestor", sha, "origin/main"], capture_output=True)
    return r.returncode == 0


def cmd_submit(a):
    ensure_dirs()
    sel = {}
    for k in ("chains", "rows"):
        if getattr(a, k):
            sel[k] = [x for x in getattr(a, k).split(",") if x]
    if a.item:
        sel["item"] = a.item
    if a.full:
        sel["full"] = True
    kw = {k: v for k, v in (("item", a.for_item), ("profile", a.profile), ("priority", a.priority),
                            ("not_before", a.not_before), ("supersedes", a.supersedes), ("owner_gate", a.owner_gate),
                            ("lane", a.lane), ("timeout_s", a.timeout)) if v is not None}
    kw.update(deploy=a.deploy or [], canary=not a.no_canary, validity=not a.no_validity)
    try:
        job = S.make_job(a.mod, sel, a.purpose, a.by, a.sha, **kw)
    except S.SchemaError as e:
        print("REFUSED: %s" % e)
        return 2
    if not a.no_sha_check and not published(a.sha):
        print("REFUSED: %s is not on origin/main; the runner pulls origin, so ./publish first" % a.sha)
        return 2
    for other in records("pending") + [r["job"] for r in records("running")]:
        if same_request(job, other):
            print(json.dumps({"job": other["id"], "duplicate": True, "state": where(other["id"])}))
            return 0
    if job["supersedes"]:
        st = where(job["supersedes"])
        if st == "pending":
            old = read_json(q("pending", job["supersedes"] + ".json"))
            move(old["id"], "pending", "cancelled", {"job": old, "reason": "superseded by " + job["id"],
                                                     "at": S.utcnow()})
    S.dump(job, q("pending", job["id"] + ".json"))
    print(json.dumps({"job": job["id"], "state": "pending"}))
    return 0


def cmd_cancel(a):
    ensure_dirs()
    st = where(a.job)
    if st == "pending":
        job = read_json(q("pending", a.job + ".json"))
        move(a.job, "pending", "cancelled", {"job": job, "reason": a.reason, "at": S.utcnow()})
    elif st == "running":
        rec = read_json(q("running", a.job + ".json"))
        rec.update(cancel=True, cancel_reason=a.reason)
        move(a.job, "running", "running", rec)
        try:
            remote(["stop", "--attempt", rec["attempt"]])
        except SshDown as e:
            print("stop not delivered (%s); the next tick sees the INTERRUPTED result or the finished run" % e)
    else:
        print("REFUSED: %s is %s" % (a.job, st or "unknown"))
        return 2
    print(json.dumps({"job": a.job, "was": st, "cancelled": True}))
    return 0


def cmd_resume(a):
    ensure_dirs()
    pz = paused()
    if not pz:
        print("not paused")
        return 0
    os.remove(q("paused.json"))
    log("lane resumed (paused since %s by %s %s/%s): %s" % (pz.get("since"), pz.get("job"), pz.get("outcome"),
                                                         pz.get("cause"), a.reason))
    return 0


def sel_text(job):
    sel = job.get("selector", {})
    return " ".join("%s=%s" % (k, ",".join(v) if isinstance(v, list) else v) for k, v in sel.items())


def cmd_list(a):
    ensure_dirs()
    pz = paused()
    if pz:
        print("PAUSED since %s by %s %s/%s: %s  (testq.py resume --reason R)" % (pz.get("since"), pz.get("job"),
                                                                              pz.get("outcome"), pz.get("cause"),
                                                                              pz.get("reason")))
    for st in ([a.state] if a.state else STATES):
        for rec in records(st):
            job, res = job_of(rec), rec.get("result") or {}
            extra = rec.get("attempt") or ("%s %s %s" % (res.get("outcome"), res.get("cause") or "",
                                                          res.get("counts")) if res else rec.get("reason", ""))
            print("%-9s %s %-12s %-10s p%-3d %s  %s" % (st, job.get("id"), job.get("mod"), job.get("purpose"),
                                                      job.get("priority", 0), sel_text(job)[:50], extra))
    return 0


def cmd_show(a):
    st = where(a.job)
    if not st:
        print("unknown job %s" % a.job)
        return 2
    rec = read_json(q(st, a.job + ".json"))
    job, res = job_of(rec), rec.get("result") or {}
    lines = ["%s  %s" % (a.job, st.upper()),
             "%s %s  purpose=%s prio=%d profile=%s lane=%s" % (job["mod"], sel_text(job), job["purpose"],
                                                               job["priority"], job["profile"], job["lane"]),
             "by %s at %s, source %s%s" % (job["requested_by"], job["submitted"], job["source_sha"][:10],
                                          ", for " + job["item"] if job.get("item") else "")]
    if job.get("owner_gate") or job.get("not_before"):
        lines.append("waits: owner_gate=%s not_before=%s" % (job.get("owner_gate"), job.get("not_before")))
    if rec.get("attempts"):
        lines.append("attempts: %s" % ", ".join(rec["attempts"]))
    if rec.get("reason"):
        lines.append("cancelled: %s" % rec["reason"])
    if res:
        lines.append("result: %s %s %s  runner %s  phases %s" % (res["outcome"], res["cause"] or "", res.get("counts"),
                                                                 (res.get("runner_sha") or "")[:10], res.get("phase_s")))
        lines.append("note: %s" % res.get("note", "")[:200])
        bad = [r for r in res.get("rows") or [] if r["verdict"] != "PASS"]
        for r in bad[:20 - len(lines) - 1]:
            lines.append("  %-10s %s/%s  %s" % (r["verdict"], r["chain"], r["row"], (r["detail"] or "")[:80]))
        if res.get("artifacts"):
            lines.append("sheet: %s" % res["artifacts"][0]["path"])
    print("\n".join(lines[:20]))
    return 0


DISPATCH = os.path.expanduser("~/rm/dispatch")
UNITS = {
    "testq-tick.service": """[Unit]
Description=testq dispatch tick (TESTQ_DISPATCHER_BUILD_SSH_NO_LLM)

[Service]
Type=oneshot
WorkingDirectory={clone}
ExecStartPre=-/usr/bin/git -C {clone} pull -q --ff-only origin main
ExecStart=/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/testq.py tick
ExecStart=/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/ingest.py
TimeoutStartSec=900
""",
    "testq-tick.timer": """[Unit]
Description=testq dispatch tick every 60 s

[Timer]
OnBootSec=2min
OnUnitInactiveSec=60s
AccuracySec=5s

[Install]
WantedBy=timers.target
""",
}


def cmd_install_timer(a):
    if not os.path.isdir(os.path.join(DISPATCH, ".git")):
        print("REFUSED: no dispatch clone at %s (git clone the repo there first)" % DISPATCH)
        return 2
    unit_dir = os.path.expanduser("~/.config/systemd/user")
    for name, text in UNITS.items():
        path = os.path.join(unit_dir, name)
        print("%s %s" % ("write" if a.apply else "would write", path))
        if a.apply:
            os.makedirs(unit_dir, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text.format(clone=DISPATCH))
    if a.apply:
        for argv in (["daemon-reload"], ["enable", "--now", "testq-tick.timer"]):
            r = subprocess.run(["systemctl", "--user"] + argv, capture_output=True, text=True, timeout=60)
            print("systemctl --user %s: exit %d %s" % (" ".join(argv), r.returncode, r.stderr.strip()[-200:]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="testq.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("submit")
    s.add_argument("mod")
    s.add_argument("--chains")
    s.add_argument("--rows")
    s.add_argument("--item", action="append", help="modcheck --item (repeatable)")
    s.add_argument("--full", action="store_true")
    s.add_argument("--purpose", required=True, choices=S.PURPOSES)
    s.add_argument("--by", required=True, help="the submitting seat")
    s.add_argument("--sha", required=True, help="a published commit the run must include")
    s.add_argument("--for-item", help="the rimflow item the run is for")
    s.add_argument("--profile", choices=S.PROFILES)
    s.add_argument("--priority", type=int)
    s.add_argument("--not-before")
    s.add_argument("--supersedes")
    s.add_argument("--owner-gate")
    s.add_argument("--lane", choices=S.LANES)
    s.add_argument("--deploy", action="append")
    s.add_argument("--timeout", type=int)
    s.add_argument("--no-canary", action="store_true")
    s.add_argument("--no-validity", action="store_true")
    s.add_argument("--no-sha-check", action="store_true", help="skip the is-it-on-origin/main check")
    s = sub.add_parser("list")
    s.add_argument("--state", choices=STATES)
    s = sub.add_parser("show")
    s.add_argument("job")
    s = sub.add_parser("cancel")
    s.add_argument("job")
    s.add_argument("--reason", required=True)
    s = sub.add_parser("resume")
    s.add_argument("--reason", required=True)
    sub.add_parser("tick")
    s = sub.add_parser("install-timer")
    s.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    if getattr(a, "job", None) and not S.JOB_ID_RE.match(a.job):
        print("REFUSED: %r is not a job id" % a.job)
        return 2
    return {"submit": cmd_submit, "list": cmd_list, "show": cmd_show, "cancel": cmd_cancel, "resume": cmd_resume,
            "tick": cmd_tick,
            "install-timer": cmd_install_timer}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
