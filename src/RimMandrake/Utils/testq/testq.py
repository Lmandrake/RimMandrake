#!/usr/bin/env python3
"""testq.py - the test queue and its no-LLM dispatcher (TESTQ_DISPATCHER_BUILD_SSH_NO_LLM).

Plan: design/RimMandrake/test_orchestration_two_machines_2026-10-25.md sections 3 and 6. Records: schema.py.

  testq.py submit MOD --chains a,b | --rows r1,r2 | --item ID | --full   --purpose P --by SEAT --sha SHA [...]
  testq.py list [--state pending|running|done|cancelled]
  testq.py show JOB                  at most 20 lines: state, selection, attempt, outcome, the failing rows
  testq.py cancel JOB --reason R     pending -> cancelled; running -> the worker is told to stop
  testq.py resume --reason R         lift a lane pause (paused.json) once its cause is dealt with
  testq.py sweep MOD [--by SEAT]     queue today's one full sweep of MOD (purpose=sweep, origin/main), unless a sweep
                                     of MOD was already submitted today (local calendar date); the testq-sweep
                                     timer runs it nightly at 01:30 local for each of TESTQ_SWEEP_MODS (FlowWorks)
  testq.py fill MOD [--n 4]          Steve never idles, no LLM: if nothing is pending/running, queue the N chains
                                     whose last real run is oldest, skipping DRY ones (last 2 runs all UNMEASURED,
                                     re-tried after 3 days) (requested_by BENCH.filler, prio 20). Brakes:
                                     QHOME/fill.stop, lane time per local day (TESTQ_FILL_HOURS, 8 h; a job
                                     backstop TESTQ_FILL_CAP, 200), a paused lane, two non-DONE fillers running;
                                     every tick runs it for each mod `coverage.py wired` names (wired_mods.json;
                                     TESTQ_FILL_MODS overrides)
  testq.py maintenance --reason R --since T [--until T]  record a maintenance reboot or known hardware outage, after the
                                     fact too: a job killed inside it is not a lane fault (nonfault_cause, brake_release.py)
  testq.py pause --reason R [--hours H]  pause the lane by hand; with --hours it is intentional until then (the
                                     steward never escalates it before), without, the steward escalates it at 60 min
  testq.py steward                   the lane steward (steward.py; STEVE_STEWARD_BUILD_NO_LLM_OWNER): state, unowned
                                     clock, escalation to BENCH at 10/30 min and the owner at 120 min; the tick runs it
  testq.py steward-watch             its heartbeat watcher (testq-steward-watch.timer, every 60 s)
  testq.py tick                      one dispatch pass (a systemd user timer runs it every 60 s)
  testq.py install-timer [--apply]   that timer: testq-tick.{service,timer} in the user manager, ticking from the
                                     dispatch clone (~/rm/dispatch, pulled before every tick, never an agent's clone),
                                     then ingest.py (results -> RUNNER ledger events, committed from that clone), then
                                     findings_fold.py run (the no-AI findings sorter; its exit 2 fails the unit).
                                     The clone may be sparse: it needs src/RimMandrake/{Utils/testq,rimflow,contracts},
                                     infrastructure/state, AND src/RimMandrake/Utils/modcheck plus each filled mod's
                                     source (every wired mod's folder): without them preview, bad_selection and the
                                     filler's gap order (gaps.py) are blind and say so ("blind: ...").

The queue is plain files under TESTQ_QUEUE (default /mnt/d/ClaudeWork/rimmandrake/testq):
  pending/<job>.json   the job record
  running/<job>.json   {"job", "attempt", "sent", "attempts", "auto_retries", "cancel"}
  done/<job>.json      {"job", "result", "attempts", "finished"}   - the last attempt's testq.result/1
  cancelled/<job>.json {"job", "reason", "at"}
  orphans/<attempt>.json  a worker result for a job this queue never sent (kept, acked)
  quarantined/<job>.json  a done record from inside a Steve SIMD fault window: must not count (fault_monitor.py, ingest.py)
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
  4. Admit one ready job when the lane is idle and not paused: no owner_gate, not_before passed, lane stevedesktop
     or any;
     highest priority first, then the current train (same profile as the last job sent), then oldest.
     The worker's exit 75 (busy) leaves it pending.
  5. The Archmagi backfill (TESTQ_ARCHMAGI_LANE_BUILD_BACKFILL; plan section 3 "Archmagi backfill", section 6 "SSH
     down"), independent of ssh. OFF unless TESTQ_ARCHMAGI=1 is in the tick's environment; QHOME/archmagi.stop also
     stops it. It runs the SAME worker.py, locally, from its own runner clone (TESTQ_ARCHMAGI_RUNNER, default
     ~/rm/archrunner: never an agent's or the dispatch clone), TESTQ_HOME=QHOME/archmagi_worker, with
     archmagi_phases.py as the phases: it never deploys (drift -> REFUSED/DEPLOY), never launches or stops the
     owner's game (none running -> REFUSED/LOAD), and its attempt holds Archmagi's host guard (the driver lock that
     `rimflow bridge take` takes), so a seat's take is refused while it runs, never raced.
     One job is admitted only when every gate holds (archmagi_gate): this machine is Archmagi; no window holds the
     bridge (shared bridge file AND the BRIDGE mirror); the driver lock is FREE or STALE; the bridge was silent for
     TESTQ_ARCHMAGI_SILENT_S (600 s: the bridge call log and the last bridge take/release); no back-off or pause.
     Candidates: lane=archmagi, and lane=any only while SteveDesktop is down or busy; profile in
     TESTQ_ARCHMAGI_PROFILES (default full-list: a targeted job wants modcheck's minimal-list load). A REFUSED
     DEPLOY/LOAD/GUARD_HELD attempt hands the job back to pending (DEPLOY: never again on Archmagi; LOAD: the lane
     backs off TESTQ_ARCHMAGI_BACKOFF_S, 1800 s). A window holder appearing mid-run (a forced take) stops the
     attempt and hands the job back. A red canary / refused pull pauses only this lane (archmagi_paused.json;
     `resume --lane archmagi`).
     The section 2 trial switch (ARCHMAGI_BACKFILL_WIRE_TRIAL_SWITCH; work_allocation_framework_2026-10-26.md section 2,
     rules in archmagi_switch.py) sits in front of the gate: with TESTQ_ARCHMAGI=1 the lane admits only while the
     switch is ON (S1 saturation / S2 failover), never an S3 job (filler, guard, sweep; a deploy/load job outside a
     train worth twice the load); 30-min cooldown after any OFF; 2 consecutive archmagi INVALID latch it until
     ARCHMAGI_LATCH_FIX_TWO_STRIKES is closed on the ledger. State: archmagi_state.json "switch" (+ "takes", "yields").
     A bridge take mid-run writes TESTQ_ARCHMAGI_YIELD_FILE: validation_core.row stops the proof at its next row
     boundary and keeps the measured rows on the job (dropped from its selector); after TESTQ_ARCHMAGI_YIELD_GRACE_S
     (180 s) without one the attempt is stopped outright. TESTQ_ARCHMAGI_SWITCH=force waives S1/S2 only (an operator's
     or a test's seam). `testq.py archmagi-report [--days N]` judges the trial: verified items/day net of load time and
     displaced interactive minutes, priced at SteveDesktop's verified items per lane-hour.
"""
import argparse
import fcntl
import glob
import json
import os
import shlex
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import schema as S  # noqa: E402
import archmagi_switch as SW  # noqa: E402
if os.path.dirname(os.path.dirname(HERE)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(HERE)))      # src/RimMandrake, for contracts (stdlib-only modules)
from contracts import compat as CC  # noqa: E402

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
ARCHMAGI = "archmagi"
STEVE = "stevedesktop"


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


def heartbeat(job_id):
    """The worker just confirmed this job is running: bump running/<job>.json's mtime. ops_watch's
    queues.testq.stalled_min sees a running job only through that mtime, so a long healthy run with jobs pending
    behind it read as a stall (OPS_TESTQ_UNSTICK_ECPK); an orphan the worker no longer confirms still goes stale."""
    try:
        os.utime(q("running", job_id + ".json"))
    except FileNotFoundError:
        pass


def records(state):
    """Every readable record file in `state`. An unreadable one is skipped as before, but named on stderr: a
    skipped file is accounted, never silent (contracts policy)."""
    out, bad = [], []
    for f in sorted(glob.glob(q(state, "*.json"))):
        r = read_json(f)
        if r is not None:
            out.append(r)
        else:
            bad.append(os.path.basename(f))
    if bad:
        print("testq: %d unreadable %s record(s) skipped: %s" % (len(bad), state, " ".join(bad[:5])), file=sys.stderr)
    return out


def result_problems(res):
    """What schema.validate_result says about a result testq.py is about to use (None when it holds)."""
    try:
        S.validate_result(res)
        return None
    except Exception as e:  # noqa: BLE001 - shadow only
        return "%s: %s" % (type(e).__name__, e)


def last_json_object(lines, rc, text):
    """The worker's last stdout line as an object, else an {"error": ...} dict: a line that is JSON but not an object
    (list, string, null) must not reach res.get() in reconcile()/drain_outbox()."""
    try:
        o = json.loads(lines[-1])
    except (ValueError, IndexError):
        o = None
    else:
        if not isinstance(o, dict):
            return {"error": "worker line is JSON but not an object (%s, exit %d): %s" % (
                type(o).__name__, rc, text[-300:])}
    return o if o is not None else {"error": "no JSON from worker (exit %d): %s" % (rc, text[-300:])}


def invalid_result(rec, attempt, reason):
    """A tagged result that breaks testq.result/1 is recorded, not trusted: INVALID/HARNESS carrying the reason."""
    return {"schema": S.RESULT_SCHEMA, "job": rec["job"]["id"], "attempt": attempt, "outcome": "INVALID",
            "cause": "HARNESS", "rows": [], "counts": {}, "started": S.utcnow(), "finished": S.utcnow(),
            "note": ("result breaks testq.result/1: " + reason)[-300:]}


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
    return r.returncode, last_json_object(lines, r.returncode, r.stdout + r.stderr)


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
        record_lane_window("machine_down", st["down_since"], S.utcnow(), st.get("last_error") or "ssh down")
    S.dump({"down_since": None, "last_probe": time.time(), "last_error": None}, q("ssh_state.json"))
    return status


# ---------------------------------------------------------------- the tick

def host_of(rec):
    return rec.get("host") or STEVE


def worker_for(host):
    return archmagi_worker if host == ARCHMAGI else remote


def reconcile(rec):
    job = rec["job"]
    jid = job["id"]
    host = host_of(rec)
    remote = worker_for(host)       # noqa: F811 - the same verbs, on this record's machine
    rc, st = remote(["status", "--job", jid])
    latest, state = st.get("attempt"), st.get("state")
    if latest and latest != rec.get("attempt"):          # the worker knows a newer attempt: follow it
        rec["attempts"] = sorted(set(rec.get("attempts", []) + [latest]), key=lambda a: int(a.rsplit(".a", 1)[1]))
        rec["attempt"] = latest
        move(jid, "running", "running", rec)
    if state == "running":
        heartbeat(jid)
        if host == ARCHMAGI and not rec.get("yield"):
            holder = bridge_holder()
            if holder:     # a window took the bridge anyway (forced): the seat wins, the job goes back
                # section 2: the attempt aborts at its NEXT ROW BOUNDARY (validation_core.row reads the yield file and
                # leaves the rows it measured beside it); past the grace it is stopped outright, as before
                ask_yield(holder, latest)
                rec.update(**{"yield": holder, "yield_at": time.time()})
                move(jid, "running", "running", rec)
                note_switch_take(holder)
                log("%s on archmagi: %s took the bridge mid-run; attempt %s asked to yield at its next row boundary "
                    "(stopped outright after %d s)" % (jid, holder, latest, yield_grace_s()))
        if host == ARCHMAGI and rec.get("yield") and not rec.get("stop_sent") and \
                time.time() - (rec.get("yield_at") or 0) >= yield_grace_s():
            rec["stop_sent"] = time.time()
            move(jid, "running", "running", rec)
            remote(["stop", "--attempt", latest])
            log("%s on archmagi: no row boundary within %d s of the take; attempt %s stopped, the job goes back" % (
                jid, yield_grace_s(), latest))
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
    if not CC.testq_result_readable(res):
        log("%s: result for %s unreadable: %s" % (jid, latest, res.get("error")))
        return
    shadow = result_problems(res)
    if shadow:
        log("%s: result for %s breaks testq.result/1, recorded INVALID/HARNESS: %s" % (jid, latest, shadow))
        res = invalid_result(rec, latest, shadow)
    if host == ARCHMAGI and not rec.get("cancel") and archmagi_bounce(rec, res):
        return
    if host == STEVE and (res["outcome"], res["cause"]) == ("REFUSED", "GUARD_HELD") and not rec.get("cancel"):
        # a driver took the game guard between the worker's start check and the attempt's acquire: nothing was measured,
        # so the job is NOT finished. Ask for a fresh attempt every tick (no retry budget); busy (75) = still held.
        rc, o = remote(["start", "--retry"], stdin=json.dumps(job))
        if o.get("attempt") and o["attempt"] != latest:
            rec.update(attempt=o["attempt"], attempts=rec.get("attempts", []) + [o["attempt"]])
            move(jid, "running", "running", rec)
            remote(["ack", "--attempt", latest])
            log("%s attempt %s REFUSED/GUARD_HELD (late): requeued -> %s" % (jid, latest, o["attempt"]))
        else:
            log("%s attempt %s REFUSED/GUARD_HELD (late): guard still held (%s); stays running, asked again next tick" % (
                jid, latest, o.get("busy_with") or o.get("error") or rc))
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
    host = host_of(rec)
    done = {"job": rec["job"], "result": res, "attempts": rec.get("attempts") or [res["attempt"]],
            "cancelled": bool(rec.get("cancel")), "finished": S.utcnow()}
    if rec.get("sent"):
        done["sent"] = rec["sent"]      # when it was admitted: its span, for nonfault_cause
    if host != STEVE:
        done["host"] = host
    move(jid, "running", "done", done)
    worker_for(host)(["ack", "--attempt", res["attempt"]])
    log("%s DONE-> %s %s %s (%s%s)" % (jid, res["outcome"], res["cause"] or "", res.get("counts"), res["attempt"],
                                       "" if host == STEVE else " on " + host))
    why = PAUSE_ON.get((res["outcome"], res["cause"]))
    # A red canary is a HARNESS-class pause (a crowded anchor, a stale marker): the next job restarts the game and runs
    # the canary again, so the FIRST consecutive red does not stop the lane (an idle SteveDesktop costs more than one
    # more attempt); a second consecutive red, or any non-canary pause, still does. ingest.py files the finding either way.
    armed = autoresume_path(host)
    if (res["outcome"], res["cause"]) == ("INVALID", "CANARY"):
        if why and not rec.get("cancel") and not paused(host) and not read_json(armed):
            S.dump({"since": S.utcnow(), "job": jid, "attempt": res["attempt"]}, armed)
            log("LANE%s: canary red on %s; auto-resumed ONCE (a second consecutive red pauses)" % (
                "" if host == STEVE else " " + host, jid))
            why = None
    elif os.path.exists(armed):
        os.remove(armed)
    if why and not rec.get("cancel") and not paused(host):
        S.dump({"since": S.utcnow(), "job": jid, "attempt": res["attempt"], "outcome": res["outcome"],
                "cause": res["cause"], "reason": why, "note": (res.get("note") or "")[-300:]}, pause_path(host))
        log("LANE%s PAUSED by %s %s/%s: %s; `testq.py resume%s --reason R` lifts it" % (
            "" if host == STEVE else " " + host, jid, res["outcome"], res["cause"], why,
            "" if host == STEVE else " --lane " + host))


def pause_path(host=STEVE):
    return q("paused.json") if host == STEVE else q("%s_paused.json" % host)


def autoresume_path(host=STEVE):
    return q("canary_autoresume.json") if host == STEVE else q("%s_canary_autoresume.json" % host)


def paused(host=STEVE):
    return read_json(pause_path(host))


def drain_outbox(outbox, host=STEVE):
    remote = worker_for(host)       # noqa: F811
    running = {r["job"]["id"] for r in records("running") if host_of(r) == host}
    for aid in outbox:
        jid = aid.rsplit(".a", 1)[0]
        if jid in running:
            continue
        done = read_json(q("done", jid + ".json"))
        if done and aid in done.get("attempts", []) + [done["result"]["attempt"]]:
            remote(["ack", "--attempt", aid])
            continue
        rc, res = remote(["result", "--attempt", aid])
        if CC.testq_result_readable(res):
            bad = result_problems(res)
            if bad:
                log("orphan result %s breaks testq.result/1: %s" % (aid, bad))
            S.dump(res, q("orphans", aid + ".json"))
            remote(["ack", "--attempt", aid])
            log("orphan result %s (%s %s) kept in orphans/" % (aid, res.get("outcome"), res.get("cause") or ""))


def ready(job, now):
    if job.get("owner_gate"):
        return False
    if job.get("not_before") and S.parse_ts(job["not_before"]) > now:
        return False
    return job.get("lane") in ("stevedesktop", "any")


def steve_running():
    return [r for r in records("running") if host_of(r) == STEVE]


def admit(status):
    if steve_running() or paused():
        return
    if status.get("busy"):
        log("worker busy with %s (not ours); nothing admitted" % status.get("current"))
        return
    now = time.time()
    train = (read_json(q("train.json")) or {}).get("profile")
    cands = [j for j in records("pending") if ready(j, now)]
    if not cands:
        return
    cands.sort(key=lambda j: (-j["priority"], j["profile"] != train, j["submitted"], j["id"]))
    job = cands[0]
    why = job.get("requested_by") == FILLER and companion_unready(job)
    if why:     # the filler picks again next tick; a cancel is not counted by the brake (brake_tail)
        move(job["id"], "pending", "cancelled", {"job": job, "reason": why, "at": S.utcnow()})
        log("%s cancelled at admission: %s" % (job["id"], why))
        return
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
        steve_up = status is not None
        if steve_up:
            try:
                for rec in steve_running():
                    reconcile(rec)
                drain_outbox(remote(["outbox"])[1].get("outbox") or [])
                admit(remote(["status"])[1])
            except SshDown as e:
                S.dump({"down_since": S.utcnow(), "last_probe": time.time(), "last_error": str(e)},
                       q("ssh_state.json"))
                log("ssh dropped mid-tick: %s" % e)
                steve_up = False
        archmagi_tick(steve_up=steve_up, steve_busy=bool(steve_running()) or bool((status or {}).get("busy")))
    return 0


# ---------------------------------------------------------------- the Archmagi backfill (TESTQ_ARCHMAGI_LANE_BUILD_BACKFILL)

ARCH_SILENT_S = 600          # plan section 3: "only when the bridge is free and has been silent for 10 min"
ARCH_BACKOFF_S = 1800        # after REFUSED/LOAD (no game running): look again in 30 min, not every minute
ARCH_MODS_DIR = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
ARCH_BOUNCE = {"DEPLOY", "LOAD", "GUARD_HELD"}    # REFUSED causes that hand the job back instead of finishing it
PHASES = ("DEPLOY", "LOAD", "DOWN", "STATUS")


def _env_int(name, default):
    try:
        return int(os.environ.get(name) or default)
    except ValueError:
        return default


def arch_home():
    return os.environ.get("TESTQ_ARCHMAGI_HOME") or q("archmagi_worker")


def arch_runner():
    return os.path.abspath(os.path.expanduser(os.environ.get("TESTQ_ARCHMAGI_RUNNER") or "~/rm/archrunner"))


def arch_state():
    return read_json(q("archmagi_state.json")) or {}


def arch_state_update(**kw):
    st = arch_state()
    st.update(kw)
    S.dump(st, q("archmagi_state.json"))


def _rimflow():
    """-> (model, host_guard) from the rimflow package next door (imported late: the Steve lane does not need them)."""
    d = os.path.join(HERE, "..", "..", "rimflow")
    if d not in sys.path:
        sys.path.insert(0, d)
    import model
    import host_guard
    return model, host_guard


def bridge_holder():
    """-> who holds Archmagi's bridge per the shared bridge file or the BRIDGE mirror, else None. Unreadable files
    read as free here; the driver lock (taken by the worker) is what actually refuses a second driver."""
    try:
        model, _hg = _rimflow()
    except Exception as e:      # noqa: BLE001
        return "unknown (rimflow not importable: %s)" % e
    sh = model.read_shared_bridge()
    if sh and sh.get("holder"):
        return "%s (shared bridge file, for: %s)" % (sh["holder"], sh.get("purpose"))
    try:
        with open(model.bridge_mirror_path(), encoding="utf-8") as f:
            for line in f:
                if line.startswith("HELD"):
                    return "%s (BRIDGE mirror)" % " ".join(line.split()[1:2])
                if line.startswith("FREE"):
                    break
    except OSError:
        pass
    return None


def bridge_log_path():
    p = os.environ.get("TESTQ_BRIDGE_LOG")
    if p is not None:
        return p
    sys.path.insert(0, os.path.join(HERE, ".."))
    from rmpaths import rm_str
    return rm_str("scratch", "bridge_calls.jsonl")


def bridge_silence_s(now=None):
    """-> (seconds since the bridge was last used, or None when that cannot be shown). Used = the bridge call log
    (every rimbridge_client call appends to it) and the shared bridge file's last take/release/touch."""
    now = now or time.time()
    p = bridge_log_path()
    try:
        last = os.path.getmtime(p)
    except OSError:
        return None
    try:
        model, _hg = _rimflow()
        sh_path = model.shared_bridge_path()
        if sh_path and os.path.exists(sh_path):
            last = max(last, os.path.getmtime(sh_path))
    except Exception:       # noqa: BLE001 - the call log alone still bounds it
        pass
    return max(0, int(now - last))


def runner_problem(path):
    """-> why PATH may not be the Archmagi runner clone, else None. It is detached and pulled per attempt, so it must
    never be an agent's clone or the dispatch clone (which pulls before every tick)."""
    if not os.path.isfile(os.path.join(path, "infrastructure", "stevedesktop", "worker.py")) or \
            not os.path.exists(os.path.join(path, ".git")):
        return "no runner clone at %s (git clone the repo there; TESTQ_ARCHMAGI_RUNNER names another)" % path
    if os.environ.get("TESTQ_SKIP_PULL") != "1":        # tests run the worker in place with nothing pulled or pinned
        shared = {os.path.realpath(os.path.expanduser(c)) for c in ("~/rm/bench", "~/rm/foundry", DISPATCH)}
        shared.add(os.path.realpath(REPO))
        if os.path.realpath(path) in shared:
            return "%s is an agent's or the dispatch clone; the archmagi runner needs its own" % path
    return None


def archmagi_gate(now=None):
    """-> (True, why) when the backfill may admit ONE job now, else (False, the first closed gate)."""
    if os.environ.get("TESTQ_ARCHMAGI") != "1":
        return False, "off (TESTQ_ARCHMAGI=1 not set)"
    if os.path.exists(q("archmagi.stop")):
        return False, "stopped (%s exists)" % q("archmagi.stop")
    pz = paused(ARCHMAGI)
    if pz:
        return False, "paused since %s by %s %s/%s" % (pz.get("since"), pz.get("job"), pz.get("outcome"),
                                                       pz.get("cause"))
    now = now or time.time()
    until = arch_state().get("backoff_until") or 0
    if until > now:
        return False, "backing off %d s more (%s)" % (until - now, arch_state().get("backoff_why"))
    try:
        model, hg = _rimflow()
    except Exception as e:      # noqa: BLE001 - cannot read the locks: closed
        return False, "rimflow not importable: %s" % e
    if hg.local_host() != ARCHMAGI:
        return False, "this machine is %s, not archmagi" % hg.local_host()
    prob = runner_problem(arch_runner())
    if prob:
        return False, prob
    holder = bridge_holder()
    if holder:
        return False, "bridge held by " + holder
    st = hg.status()
    if st.get("state") not in ("FREE", "STALE"):     # STALE: its holder is dead; the worker's guard takes it over
        return False, "driver lock %s%s" % (st.get("state"), " by %s for %s" % (st.get("seat"), st.get("purpose"))
                                            if st.get("seat") else "")
    quiet = bridge_silence_s(now)
    need = _env_int("TESTQ_ARCHMAGI_SILENT_S", ARCH_SILENT_S)
    if quiet is None:
        return False, "cannot show the bridge is silent (no bridge call log at %s)" % bridge_log_path()
    if quiet < need:
        return False, "bridge used %d s ago (needs %d s of silence)" % (quiet, need)
    return True, "free, silent %d s" % quiet


def archmagi_candidates(steve_up, steve_busy, now=None):
    """Jobs the backfill may take: lane archmagi; lane any only while SteveDesktop is down or busy (plan section 6:
    ssh down re-routes profile-compatible jobs); never lane stevedesktop; only TESTQ_ARCHMAGI_PROFILES; never a job
    Archmagi already refused to deploy."""
    now = now or time.time()
    profiles = (os.environ.get("TESTQ_ARCHMAGI_PROFILES") or "full-list").split(",")
    skip = arch_state().get("skip") or {}
    out = []
    for j in records("pending"):
        if j.get("owner_gate") or (j.get("not_before") and S.parse_ts(j["not_before"]) > now):
            continue
        if j["id"] in skip or j.get("profile") not in profiles:
            continue
        if j.get("lane") == ARCHMAGI or (j.get("lane") == "any" and (not steve_up or steve_busy)):
            out.append(j)
    # S3 Never (section 2): filler, guard and sweep never; a job needing a deploy/load only as part of a train worth
    # twice the load
    est = est_lane_s(now)
    train = {}
    for j in out:
        train[SW.load_key(j)] = train.get(SW.load_key(j), 0) + est
    out = [j for j in out if not SW.s3_refusal(j, train.get(SW.load_key(j), 0),
                                               _env_int("TESTQ_ARCHMAGI_LOAD_S", SW.LOAD_S))]
    out.sort(key=lambda j: (-j["priority"], j["submitted"], j["id"]))
    return out


def archmagi_worker(args, stdin=None, timeout=180):
    """Run `worker.py ARGS` locally in the Archmagi runner clone -> (exit code, last JSON line), like remote()."""
    run = arch_runner()
    home = arch_home()
    phases = os.path.join(home, "phases", "archmagi_phases.py")
    os.makedirs(os.path.dirname(phases), exist_ok=True)
    # a COPY outside the clone: a job pinned to an older sha has no archmagi_phases.py of its own
    import shutil
    shutil.copy2(os.path.join(HERE, "archmagi_phases.py"), phases)
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("TESTQ_CMD_") and k not in ("TESTQ_HOME", "TESTQ_REPO", "TESTQ_CLONE",
                                                          "TESTQ_MODS_DIR", "RM_HOST_GUARD_GEN", "TESTQ_UNIT")}
    for ph in PHASES:
        env["TESTQ_CMD_" + ph] = os.environ.get("TESTQ_ARCHMAGI_CMD_" + ph) or "python3 %s %s" % (
            shlex.quote(phases), ph.lower())
    if os.environ.get("TESTQ_ARCHMAGI_CMD_RUN"):
        env["TESTQ_CMD_RUN"] = os.environ["TESTQ_ARCHMAGI_CMD_RUN"]
    # the lane honours the job's profile (full-list = the owner's running list): modcheck must not swap ModsConfig
    # to MINIMAL, compose, or restore it. WSLENV carries the flag into python.exe (TESTQ_ARCHMAGI_FIX_OWNER_MODLIST_SWAP).
    env["MODCHECK_KEEP_MODLIST"] = "1"
    env["WSLENV"] = (env["WSLENV"] + ":" if env.get("WSLENV") else "") + "MODCHECK_KEEP_MODLIST"
    # the row-boundary yield (section 2): validation_core.row stops a proof when this file exists; /p hands python.exe
    # the path in Windows form, so it must live on a drive Windows sees (the agent storage root by default)
    env["TESTQ_YIELD_FILE"] = yield_path()
    env["WSLENV"] += ":TESTQ_YIELD_FILE/p"
    env.update(TESTQ_HOME=home, TESTQ_WORKER_HOST=ARCHMAGI,
               TESTQ_MODS_DIR=os.environ.get("TESTQ_ARCHMAGI_MODS_DIR") or ARCH_MODS_DIR)
    try:
        r = subprocess.run([sys.executable, os.path.join(run, "infrastructure", "stevedesktop", "worker.py")] + args,
                           cwd=run, env=env, input=stdin, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, {"error": "archmagi worker %s: %s" % (" ".join(args), e)}
    lines = r.stdout.strip().splitlines()
    return r.returncode, last_json_object(lines, r.returncode, r.stdout + r.stderr)


def archmagi_bounce(rec, res):
    """A REFUSED attempt that measured nothing about the mod (Archmagi may not deploy / has no game / its guard was
    taken) or one stopped to yield to a window: the job goes back to pending instead of finishing. -> True if so."""
    job = rec["job"]
    jid = job["id"]
    # asked to yield: whatever it ended as (INTERRUPTED by the stop, or a modcheck cut short at a row boundary) measured
    # the mod only partly, so it goes back. A DONE that finished before it saw the request stands.
    yielded = rec.get("yield") and res["outcome"] != "DONE"
    if not yielded and not (res["outcome"] == "REFUSED" and res["cause"] in ARCH_BOUNCE):
        return False
    why = "yielded to %s" % rec["yield"] if yielded else "%s/%s: %s" % (res["outcome"], res["cause"],
                                                                        (res.get("note") or "")[:200])
    if yielded:
        job = record_yield_progress(job, res)
    if res["cause"] == "DEPLOY" and not yielded:
        st = arch_state()
        skip = st.get("skip") or {}
        skip[jid] = {"at": S.utcnow(), "why": why}
        arch_state_update(skip=skip)
    if res["cause"] == "LOAD" and not yielded:
        arch_state_update(backoff_until=time.time() + _env_int("TESTQ_ARCHMAGI_BACKOFF_S", ARCH_BACKOFF_S),
                          backoff_why=why)
    move(jid, "running", "pending", job)
    archmagi_worker(["ack", "--attempt", res["attempt"]])
    log("%s back to pending from archmagi (%s)" % (jid, why))
    return True


def archmagi_tick(steve_up, steve_busy):
    """Step 5 of the tick: reconcile, drain and (gates permitting) admit on Archmagi. Admits nothing unless enabled;
    an attempt started before it was switched off is still reconciled to the end."""
    mine = [r for r in records("running") if host_of(r) == ARCHMAGI]
    if os.environ.get("TESTQ_ARCHMAGI") != "1" and not mine:     # switched off: still finish what it started
        return
    for rec in mine:
        reconcile(rec)
    if not any(host_of(r) == ARCHMAGI and r.get("yield") for r in records("running")):
        close_takes()       # no yielding attempt left: the game is the taker's from here on (switched on or off)
    drain_outbox(archmagi_worker(["outbox"])[1].get("outbox") or [], ARCHMAGI)
    if os.environ.get("TESTQ_ARCHMAGI") != "1":
        return
    ok, why = archmagi_gate()
    sw = switch_step(steve_up, ok, why)
    if any(host_of(r) == ARCHMAGI for r in records("running")):
        return
    if ok and not sw.get("on"):
        ok, why = False, "switch off (%s)" % sw.get("closed_why")
    cands = archmagi_candidates(steve_up, steve_busy) if ok else []
    said = why if not ok else ("no candidate job" if not cands else None)
    if said and arch_state().get("last_gate") != said.split(" (")[0].split(" used ")[0]:
        log("archmagi lane: %s" % said)
    if said:
        arch_state_update(last_gate=said.split(" (")[0].split(" used ")[0])
        return
    job = cands[0]
    clear_yield()           # a request left from an earlier take must not stop this attempt at its first row
    rc, o = archmagi_worker(["start"], stdin=json.dumps(job))
    if not o.get("attempt"):
        log("%s: archmagi start failed (exit %d): %s; stays pending" % (job["id"], rc, o.get("error") or o))
        return
    move(job["id"], "pending", "running", {"job": job, "attempt": o["attempt"], "sent": S.utcnow(), "host": ARCHMAGI,
                                           "attempts": [o["attempt"]], "auto_retries": 0, "cancel": False,
                                           "switch_rule": sw.get("rule")})
    arch_state_update(last_gate=None)
    log("%s admitted on archmagi -> %s (%s, prio %d, %s, lane %s; gate: %s; switch %s)" % (
        job["id"], o["attempt"], job["purpose"], job["priority"], job["profile"], job["lane"], why, sw.get("rule")))


# ---------------------------------------------------------------- the section 2 trial switch (ARCHMAGI_BACKFILL_WIRE_TRIAL_SWITCH)

YIELD_GRACE_S = 180      # a bridge take: wait this long for a row boundary, then stop the attempt outright
EST_DEFAULT_S = 900      # a job's lane seconds when no finished Steve job of the last 7 days says otherwise


def yield_grace_s():
    return _env_int("TESTQ_ARCHMAGI_YIELD_GRACE_S", YIELD_GRACE_S)


def yield_path():
    p = os.environ.get("TESTQ_ARCHMAGI_YIELD_FILE")
    if p:
        return p
    sys.path.insert(0, os.path.join(HERE, ".."))
    from rmpaths import rm_str
    return rm_str("scratch", "testq_archmagi_yield.json")


def ask_yield(holder, attempt):
    p = yield_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    for f in (p + ".rows.json",):
        if os.path.exists(f):
            os.remove(f)
    S.dump({"holder": holder, "attempt": attempt, "asked": S.utcnow()}, p)


def clear_yield():
    p = yield_path()
    for f in (p, p + ".rows.json"):
        try:
            os.remove(f)
        except FileNotFoundError:
            pass


def record_yield_progress(job, res):
    """A yielded attempt: keep the rows it measured (validation_core.row left them beside the yield file) in
    archmagi_state.json "progress" (the job dict is schema-closed, testq_schema.json), and when the job names its rows,
    drop the PASSED ones from its selector so the next attempt does not redo them. A FAIL row stays selected: the final
    result must carry it, or the job would finish DONE with the failure hidden. Item/chain/full selectors cannot be
    narrowed (the rows inside them are not named up front): their progress is recorded and the proof runs whole again."""
    p = yield_path()
    rows = [r for r in (read_json(p + ".rows.json") or {}).get("rows") or [] if isinstance(r, dict)]
    measured = [r for r in rows if r.get("status") in ("PASS", "FAIL")]
    job = dict(job)
    sel = dict(job.get("selector") or {})
    if sel.get("rows"):
        passed = {r.get("id") for r in measured if r.get("status") == "PASS"}
        left = [r for r in sel["rows"] if r not in passed]
        if left and len(left) < len(sel["rows"]):
            sel["rows"] = left
            job["selector"] = sel
    st = arch_state()
    prog = st.get("progress") or {}
    prog[job["id"]] = (prog.get(job["id"]) or [])[-20:] + [{"attempt": res.get("attempt"), "at": S.utcnow(),
                                                           "rows": measured,
                                                           "last_row": rows[-1].get("id") if rows else None}]
    ys = (st.get("yields") or [])[-SW.HISTORY_MAX:]
    ys.append({"at": time.time(), "job": job["id"], "attempt": res.get("attempt"), "rows_kept": len(measured)})
    arch_state_update(yields=ys, progress=prog)
    clear_yield()
    return job


def note_switch_take(holder):
    """A bridge take while an attempt runs: remember when, so the report can charge the interactive time it displaced
    (take -> the attempt handing the game back)."""
    st = arch_state()
    takes = (st.get("takes") or [])[-SW.HISTORY_MAX:]
    takes.append({"at": time.time(), "holder": holder, "released": None})
    arch_state_update(takes=takes)


def close_takes(now=None):
    """The attempt handed the game back: close every open take with that time."""
    st = arch_state()
    takes = st.get("takes") or []
    if any(t.get("released") is None for t in takes):
        for t in takes:
            if t.get("released") is None:
                t["released"] = now or time.time()
        arch_state_update(takes=takes)


def _ts(s):
    try:
        return S.parse_ts(s[:19] + "Z")
    except (TypeError, ValueError):
        return None


def _res_span(done):
    r = done.get("result") or {}
    a, b = _ts(r.get("started") or ""), _ts(r.get("finished") or "")
    return (a, b) if a is not None and b is not None else None


def est_lane_s(now=None):
    """Mean lane seconds of SteveDesktop's finished jobs over the last 7 days (EST_DEFAULT_S when there are none)."""
    now = now or time.time()
    spans = []
    for d in records("done"):
        if d.get("host", STEVE) != STEVE:
            continue
        sp = _res_span(d)
        if sp and now - sp[1] < 7 * 86400 and sp[1] >= sp[0]:
            spans.append(sp[1] - sp[0])
    return int(sum(spans) / len(spans)) if spans else EST_DEFAULT_S


def latch_closed_at(item=SW.LATCH_ITEM):
    """-> epoch of the latest ledger `close` of ITEM, else None (TESTQ_LEDGER_EVENTS names the events dir)."""
    d = os.environ.get("TESTQ_LEDGER_EVENTS") or os.path.join(REPO, "infrastructure", "state", "ledger", "events")
    best = None
    for f in glob.glob(os.path.join(d, "*.jsonl")):
        try:
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    if item not in line:
                        continue
                    try:
                        ev = json.loads(line)
                    except ValueError:
                        continue
                    if ev.get("id") == item and ev.get("event") == "close":
                        t = _ts(ev.get("ts") or "")
                        if t and (best is None or t > best):
                            best = t
        except OSError:
            continue
    return best


def switch_inputs(steve_up, gate_ok, gate_why, now=None):
    """Gather the section 2 switch's inputs from the queue and the lane files (archmagi_switch.decide reads them)."""
    now = now or time.time()
    pend = [j for j in records("pending") if ready(j, now)]
    useful = [j for j in pend if j.get("requested_by") != FILLER]
    waits = [now - _ts(j["submitted"]) for j in useful if _ts(j.get("submitted") or "")]
    est = est_lane_s(now)
    fix_ready = sum(1 for j in records("pending") if j.get("purpose") == "fix" and not j.get("owner_gate")
                    and not (j.get("not_before") and S.parse_ts(j["not_before"]) > now)
                    and j.get("lane") in ("stevedesktop", "any", ARCHMAGI))
    n = inv = 0
    arch = []
    for d in records("done"):
        sp = _res_span(d)
        if not sp:
            continue
        if d.get("host", STEVE) == STEVE:
            if now - sp[1] <= 6 * 3600:
                n += 1
                inv += (d["result"].get("outcome") == "INVALID")
        elif d.get("host") == ARCHMAGI:
            arch.append((sp[1], d["result"].get("outcome")))
    sw = arch_state().get("switch")
    # the trial starts clean: before the switch first ran, archmagi INVALIDs belong to the untried lane, not to it
    cleared = (sw.get("latch_cleared_at") or 0) if sw else now
    streak = 0
    for t, outcome in sorted(arch, reverse=True):
        if t <= cleared or outcome != "INVALID":
            break
        streak += 1
    since = []
    pz = paused(STEVE)
    if pz:
        since.append(_ts(pz.get("since") or "") or now)
    ssh = read_json(q("ssh_state.json")) or {}
    if not steve_up and ssh.get("down_since"):
        since.append(_ts(ssh["down_since"]) or now)
    return {"useful_oldest_wait_s": max(waits) if waits else None, "useful_lane_s": est * len(useful),
            "fix_ready": fix_ready, "steve_invalid_share": (inv / n) if n else None,
            "steve_unavailable_s": (now - min(since)) if since else None,
            "gate_ok": gate_ok, "gate_why": gate_why, "bridge_holder": bridge_holder(),
            "arch_invalid_streak": streak, "latch_closed_at": latch_closed_at(),
            "force": os.environ.get("TESTQ_ARCHMAGI_SWITCH") == "force"}


def switch_step(steve_up, gate_ok, gate_why, now=None):
    """One tick of the section 2 switch: decide, store (archmagi_state.json "switch"), log each transition."""
    now = now or time.time()
    inp = switch_inputs(steve_up, gate_ok, gate_why, now)
    st, events = SW.decide(inp, arch_state().get("switch") or {}, now)
    st["inputs"] = {k: v for k, v in inp.items() if k not in ("gate_why",)}
    st["read_at"] = S.utcnow()
    arch_state_update(switch=st)
    for ev in events:
        log("archmagi switch %s%s: %s" % (ev["kind"].upper(), " " + ev["rule"] if ev.get("rule") else "", ev["why"]))
    return st


def _verified(done):
    """-> the item ids a done record verified (DONE, at least one PASS row, no FAIL or UNMEASURED), else []. A job
    naming no item counts as one unit under its job id."""
    r = done.get("result") or {}
    st = [x.get("status") for x in r.get("rows") or [] if isinstance(x, dict)]
    if r.get("outcome") != "DONE" or "PASS" not in st or "FAIL" in st or "UNMEASURED" in st:
        return []
    job = done.get("job") or {}
    items = list((job.get("selector") or {}).get("item") or []) or ([job["item"]] if job.get("item") else [])
    return items or ["job:" + job.get("id", "?")]


def archmagi_report(days=7.0, now=None):
    """The trial's judgement (section 2): verified items per day on Archmagi, after charging its load time and the
    interactive minutes it displaced. A charged hour is priced at SteveDesktop's verified items per lane-hour over the
    same window (what that hour buys on the batch lane), so `net_items_per_day` is items, not hours."""
    now = now or time.time()
    if not days or days <= 0:
        raise ValueError("--days must be > 0 (got %r)" % days)
    lo = now - days * 86400
    lanes = {ARCHMAGI: {"items": set(), "jobs": 0, "done": 0, "invalid": 0, "lane_s": 0, "load_s": 0},
             STEVE: {"items": set(), "jobs": 0, "done": 0, "invalid": 0, "lane_s": 0, "load_s": 0}}
    for d in records("done"):
        sp = _res_span(d)
        host = d.get("host", STEVE)
        if not sp or sp[1] < lo or host not in lanes:
            continue
        L = lanes[host]
        L["jobs"] += 1
        L["done"] += (d["result"].get("outcome") == "DONE")
        L["invalid"] += (d["result"].get("outcome") == "INVALID")
        L["lane_s"] += max(0, sp[1] - sp[0])
        L["load_s"] += int((d["result"].get("phase_s") or {}).get("load") or 0)
        L["items"].update(_verified(d))
    st = arch_state()
    displaced = 0
    for t in st.get("takes") or []:
        end = t.get("released") or now
        if end >= lo:
            displaced += max(0, end - max(t["at"], lo))
    a, b = lanes[ARCHMAGI], lanes[STEVE]
    steve_rate = len(b["items"]) / (b["lane_s"] / 3600.0) if b["lane_s"] else None
    charged_h = (a["load_s"] + displaced) / 3600.0
    sw = st.get("switch") or {}
    out = {"window_days": days, "archmagi_jobs": a["jobs"], "archmagi_done": a["done"], "archmagi_invalid": a["invalid"],
           "verified_items": len(a["items"]), "verified_items_per_day": round(len(a["items"]) / days, 3),
           "lane_h": round(a["lane_s"] / 3600.0, 3), "load_h": round(a["load_s"] / 3600.0, 3),
           "displaced_interactive_min": round(displaced / 60.0, 1),
           "steve_items_per_lane_h": None if steve_rate is None else round(steve_rate, 3),
           "net_items_per_day": None if steve_rate is None and charged_h else
           round((len(a["items"]) - charged_h * (steve_rate or 0)) / days, 3),
           "yields": sum(1 for y in st.get("yields") or [] if y.get("at", 0) >= lo),
           "switch": {"on": sw.get("on"), "rule": sw.get("rule"), "closed_why": sw.get("closed_why"),
                      "latch": sw.get("latch"), "off_at": sw.get("off_at"),
                      "transitions": sum(1 for e in sw.get("history") or [] if e.get("at", 0) >= lo)}}
    return out


def cmd_archmagi_report(a):
    if a.days <= 0:
        print("REFUSED: --days must be > 0")
        return 2
    r = archmagi_report(days=a.days)
    print(json.dumps(r, indent=1))
    net = r["net_items_per_day"]
    print("archmagi trial, %g d: %d verified items (%.2f/day), load %.1f h, %.0f interactive min displaced -> net %s "
          "items/day; switch %s%s" % (
              r["window_days"], r["verified_items"], r["verified_items_per_day"], r["load_h"],
              r["displaced_interactive_min"], "UNMEASURED (no SteveDesktop rate to price the charges)" if net is None
              else "%.2f" % net, "ON " + str(r["switch"]["rule"]) if r["switch"]["on"] else "off",
              "" if r["switch"]["on"] else " (%s)" % r["switch"]["closed_why"]))
    return 0


# ---------------------------------------------------------------- queue verbs

def same_request(a, b):
    keys = ("mod", "selector", "purpose", "source_sha", "item", "profile", "lane", "deploy", "canary", "validity",
            "owner_gate", "not_before", "gate")
    return all(a.get(k) == b.get(k) for k in keys)


def published(sha):
    r = subprocess.run(["git", "-C", REPO, "merge-base", "--is-ancestor", sha, "origin/main"], capture_output=True)
    return r.returncode == 0


# modcheck targeting's own refusals (targeting.TargetError): the run on the worker would refuse the same selection
# as BLOCKED_SELECTION after spending a runner slot. A mod modcheck cannot find (RuntimeError) is not one of them.
SELECTION_REFUSALS = ("unknown row", "unknown chain", "is offline", "catalogue is incomplete", "empty selection")


def preview(mod, sel):
    """-> {"refusal", "rows", "drivers"} from `modcheck run MOD --preview` (0.2 s, offline; TESTQ_JOB_PLAN_WIRE_PREVIEW):
    the refusal text when modcheck would refuse SEL, the row ids the run will execute, and the "pre" drivers
    [{name, timeout_s}] `--drivers on` would start. A full selector previews the drivers only. A mod it cannot find,
    or any other trouble, is neither refused nor planned (every value None)."""
    out = {"refusal": None, "rows": None, "drivers": None, "chains": None, "driver_chains": None}
    args = []
    for k in ("chains", "rows"):
        if sel.get(k):
            args += ["--" + k, ",".join(sel[k])]
    if not args and sel.get("full"):
        args = ["--full"]
    if not args:
        return out
    cli = os.path.join(HERE, "..", "modcheck", "cli.py")
    try:
        r = subprocess.run([sys.executable, cli, "run", mod] + args + ["--preview"], capture_output=True, text=True,
                           timeout=60, cwd=REPO)
    except (OSError, subprocess.SubprocessError):
        return out
    for line in ((r.stdout or "") + (r.stderr or "")).splitlines():
        if line.startswith("REFUSED:") and any(k in line for k in SELECTION_REFUSALS):
            return dict(out, refusal=line[len("REFUSED:"):].strip())
        for tag, key in (("EXPECTED_ROWS ", "rows"), ("EXPECTED_DRIVERS ", "drivers"),
                         ("EXPECTED_CHAINS ", "chains"), ("EXPECTED_DRIVER_CHAINS ", "driver_chains")):
            if line.startswith(tag):
                try:
                    out[key] = json.loads(line[len(tag):])
                except ValueError:
                    out[key] = None
    return out


def preview_plan(mod, sel):
    """-> (refusal text or None, the row ids the run will execute or None): preview() without the drivers."""
    p = preview(mod, sel)
    return p["refusal"], p["rows"]


# The worker (infrastructure/stevedesktop/worker.py driver_budget_export) gives a job's drivers half its run timeout,
# never more than 2 h; modcheck/drivers.py never starts a driver whose timeout_s exceeds the budget left.
WORKER_DRIVER_SHARE, WORKER_DRIVER_CAP_S = 2, 7200
DRIVER_SLACK_S = 120    # modcheck/drivers.py AFTER_SLACK_S: per driver, the runner's map recovery between drivers


def sized_timeout(requested_s, drivers):
    """-> (the job's run timeout, seconds the drivers need, warning or None). TESTQ_SIZING_FIX_DRIVER_BUDGET_FROM_PLAN:
    a 2700 s job gives its drivers 1350 s, so thirst_live (then 2700 s) was SKIPPED_BUDGET on every targeted thirst
    job and its rows read UNMEASURED. The timeout is raised until the worker's share covers every planned driver."""
    need = sum(int(d.get("timeout_s") or 0) + DRIVER_SLACK_S for d in drivers or [])
    t = max(int(requested_s), need * WORKER_DRIVER_SHARE)
    warn = None
    if need > WORKER_DRIVER_CAP_S:
        t = max(int(requested_s), WORKER_DRIVER_CAP_S * WORKER_DRIVER_SHARE)
        warn = ("the planned drivers need %d s but the worker caps the driver budget at %d s: the drivers past it "
                "will be SKIPPED_BUDGET and their chains read UNMEASURED" % (need, WORKER_DRIVER_CAP_S))
    return min(t, 6 * 3600), need, warn


def split_sweep(drivers, driver_chains, chains, cap_s=WORKER_DRIVER_CAP_S):
    """TESTQ_SWEEP_FIX_DRIVERS_OVER_CAP -> a list of chain-name lists, one per sweep job, each needing at most cap_s of
    driver time, covering every chain once. Drivers that share a chain go together (a chain selection starts every
    driver that serves any selected chain); components are packed first-fit-decreasing; chains no driver serves ride
    with the first job. One list (all chains) when everything already fits.
    TESTQ_SWEEP_FIX_EMPTY_BOX_SHIPPED: only chains in CHAINS count; a driver serving none of them (every chain it serves
    already holds a verdict) costs nothing and makes no group, so no returned group is ever empty."""
    need = {d["name"]: int(d.get("timeout_s") or 0) + DRIVER_SLACK_S for d in drivers or []}
    wanted = set(chains)
    comps = []                          # [set of driver names, set of chains]
    for name, cs in (driver_chains or {}).items():
        mine = [{name}, set(cs) & wanted]
        if not mine[1]:
            continue
        for c in [c for c in comps if c[1] & mine[1]]:
            mine[0] |= c[0]
            mine[1] |= c[1]
            comps.remove(c)
        comps.append(mine)
    cost = lambda c: sum(need.get(n, 0) for n in c[0])
    if sum(cost(c) for c in comps) <= cap_s:
        return [list(chains)]
    bins = []                           # [seconds, set of chains]
    for c in sorted(comps, key=cost, reverse=True):
        for b in bins:
            if b[0] + cost(c) <= cap_s:
                b[0] += cost(c)
                b[1] |= c[1]
                break
        else:
            bins.append([cost(c), set(c[1])])
    served = set().union(*[b[1] for b in bins]) if bins else set()
    out = [[c for c in chains if c in b[1]] for b in bins]
    out[0] += [c for c in chains if c not in served]
    return [g for g in out if g]


def bad_selection(mod, sel):
    """-> the modcheck refusal text when SEL is a selection modcheck would refuse for MOD, else None."""
    return preview_plan(mod, sel)[0]


def unknown_chains(why):
    """-> the chain names a bad_selection refusal rules out of a live job: unknown (modcheck's `unknown chain(s) for
    MOD: a, b; chains are: ...`) or offline-only (`every selected chain of MOD is offline (a, b)`), else an empty set."""
    m = (re.search(r"unknown chain\(s\) for [^:]*:\s*([^;]*)", why or "")
         or re.search(r"every selected chain of \S+ is offline \(([^)]*)\)", why or ""))
    return {c.strip() for c in m.group(1).split(",") if c.strip()} if m else set()


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
                            ("lane", a.lane), ("timeout_s", a.timeout), ("gate", getattr(a, "gate", None))) if v is not None}
    ri = {}
    for pair in getattr(a, "row_item", None) or []:
        k, sep, v = pair.partition("=")
        if not sep:
            print("REFUSED: --row-item wants ROW_OR_CHAIN=ITEM, got %r" % pair)
            return 2
        ri[k] = v
    kw.update(row_items=ri, deploy=a.deploy or [], canary=not a.no_canary, validity=not a.no_validity)
    try:
        job = S.make_job(a.mod, sel, a.purpose, a.by, a.sha, **kw)
    except S.SchemaError as e:
        print("REFUSED: %s" % e)
        return 2
    why = S.deploy_problem(list(a.deploy or []), os.path.join(REPO, "src"))
    if why:
        print("REFUSED: --deploy %s; the worker would die INVALID/DEPLOY on a booked slot" % why)
        return 2
    pv = preview(a.mod, sel)
    bad, planned = pv["refusal"], pv["rows"]
    if bad:
        print("REFUSED: %s (checked before queueing: a bad row id would burn a runner slot)" % bad)
        return 2
    stale = already_tested(a, sel, pv)
    if stale:
        print("REFUSED: %s" % stale)
        return 2
    asked = job["timeout_s"]
    job["timeout_s"], driver_need, size_warn = sized_timeout(asked, pv["drivers"])
    if not a.no_sha_check and not published(a.sha):
        print("REFUSED: %s is not on origin/main; the runner pulls origin, so ./publish first" % a.sha)
        return 2
    for other in records("pending") + [r["job"] for r in records("running")]:
        if same_request(job, other):
            print(json.dumps({"job": other["id"], "duplicate": True, "state": where(other["id"])}))
            return 0
    if job["supersedes"]:
        def supersede():
            if where(job["supersedes"]) == "pending":
                old = read_json(q("pending", job["supersedes"] + ".json"))
                move(old["id"], "pending", "cancelled", {"job": old, "reason": "superseded by " + job["id"],
                                                         "at": S.utcnow()})
            return 0
        if under_tick_lock(supersede):
            return 2
    S.dump(job, q("pending", job["id"] + ".json"))
    out = {"job": job["id"], "state": "pending"}
    if driver_need:             # what the planned drivers reserve, and the timeout raised to give them room
        out.update(drivers=[d.get("name") for d in pv["drivers"]], driver_need_s=driver_need,
                   timeout_s=job["timeout_s"])
        if job["timeout_s"] != asked:
            out["timeout_raised_from"] = asked
        if size_warn:
            out["warning"] = size_warn
    if planned is not None:     # the plan modcheck will run, so the submitter sees prerequisites and the time it costs
        out["planned_rows"] = len(planned)
        per = row_seconds(a.mod)
        if per:
            out["est_s"] = int(per * len(planned))
    print(json.dumps(out))
    return 0


def git_head():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip()


def retest_stop(mod):
    """-> {chains that must not run now}: a verdict at their code version, or a repair open. The rule's own fault
    stops nothing: it costs a run, never a queue. A mod with no history skips the probe: nothing can be settled."""
    recs = records("done")
    if not any(job_of(r).get("mod") == mod for r in recs):
        return set()
    import gaps
    try:
        st = gaps.settled(mod, recs)
    except Exception as e:      # noqa: BLE001
        log("retest rule could not read %s: %s" % (mod, e))
        return set()
    return st["settled"] | set(st["held"])


def pilot_stop(mod):
    """-> {chain: item} the Test Pilot rule has taken (gaps.pilot_chains); {} when unreadable."""
    import gaps
    try:
        w = gaps.ledger()
        if not gaps.routed_ids(w):      # the common case: nothing routed, so no modcheck probe is paid for
            return {}
        return gaps.settled(mod, records("done"), w)["pilot"]
    except Exception as e:      # noqa: BLE001
        log("pilot rule could not read %s: %s" % (mod, e))
        return {}


def already_tested(a, sel, pv):
    """Owner ruling by card 2026-10-31, "Retest only after a code change": why this submit must not run, or None.
    Every chain it would run holds a verdict at its code version, or waits for a repair (gaps.settled). The filler
    has asked already; a --rows job may want rows no run reached; --retest-why is a human's reason."""
    if (getattr(a, "retest_why", None) or "").strip():
        return None
    chains = pv.get("chains") or sel.get("chains") or []
    sha = getattr(a, "sha", None)
    if chains and not (sha and not git_head().startswith(sha)):
        taken = pilot_stop(a.mod)       # owner 2026-10-31, the Test Pilot rule: a routed item is not retested by code
        hit = sorted(c for c in chains if c in taken)
        if hit and (len(hit) == len(chains) or sel.get("chains") or sel.get("full") or sel.get("rows")):
            return ("%s belong to items routed to a Test Pilot (%s; `rimflow pilot`): no more code-and-retest; "
                    "--retest-why REASON overrides" % (",".join(hit[:6]), ",".join(sorted({taken[c] for c in hit})[:3])))
    if a.by == FILLER or sel.get("rows"):
        return None
    if not chains or (sha and not git_head().startswith(sha)):     # the rule reads THIS checkout: another sha is unknown
        return None
    stop = retest_stop(a.mod)
    # chains named one by one, or --full: each must earn its run. An --item's chains are modcheck's choice: one fresh
    # one is enough.
    hit = sorted(c for c in chains if c in stop)
    if len(hit) == len(chains) or (hit and (sel.get("chains") or sel.get("full"))):
        return ("%s already hold a verdict at this code version, or wait for a harness repair: the owner's retest rule; "
                "drop them, or --retest-why REASON overrides" % ",".join(hit[:6]))
    return None


def row_seconds(mod, recs=None, last=20):
    """-> the median lane seconds per executed row over MOD's last `last` DONE jobs (start -> finish / rows that
    were not NOT_RUN), or None with no history. The submit estimate: rows planned x this."""
    if recs is None:
        recs = [read_json(p) for p in glob.glob(q("done", "*.json"))]
    per = []
    for rec in recs:
        res, job = (rec or {}).get("result") or {}, (rec or {}).get("job") or {}
        ran = [r for r in res.get("rows") or [] if r.get("verdict") != "NOT_RUN"]
        if job.get("mod") != mod or res.get("outcome") != "DONE" or not ran:
            continue
        try:
            wall = S.parse_ts(res["finished"]) - S.parse_ts(res["started"])
        except (KeyError, TypeError, ValueError):
            continue
        if wall > 0:
            per.append((res["finished"], wall / len(ran)))
    per = sorted(v for _, v in sorted(per)[-last:])
    return per[len(per) // 2] if per else None


def under_tick_lock(fn):
    """-> fn() run holding tick.lock, so a state change made outside the tick (cancel, supersede) cannot interleave
    with a tick moving the same job (a cancel rewriting running/ after the tick moved it to done/ left the job in two
    states). Waits up to TESTQ_LOCK_WAIT_S (300 s) for a running tick, then refuses (2) with nothing changed."""
    deadline = time.time() + float(os.environ.get("TESTQ_LOCK_WAIT_S", "300"))
    with open(q("tick.lock"), "w") as lk:
        while True:
            try:
                fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() >= deadline:
                    print("REFUSED: a tick still holds %s; nothing changed, try again" % q("tick.lock"))
                    return 2
                time.sleep(0.5)
        return fn()


def cmd_cancel(a):
    ensure_dirs()
    return under_tick_lock(lambda: cancel_locked(a))


def cancel_locked(a):
    st = where(a.job)
    if st == "pending":
        job = read_json(q("pending", a.job + ".json"))
        move(a.job, "pending", "cancelled", {"job": job, "reason": a.reason, "at": S.utcnow()})
    elif st == "running":
        rec = read_json(q("running", a.job + ".json"))
        rec.update(cancel=True, cancel_reason=a.reason)
        move(a.job, "running", "running", rec)
        try:
            worker_for(host_of(rec))(["stop", "--attempt", rec["attempt"]])
        except SshDown as e:
            print("stop not delivered (%s); the next tick sees the INTERRUPTED result or the finished run" % e)
    else:
        print("REFUSED: %s is %s" % (a.job, st or "unknown"))
        return 2
    print(json.dumps({"job": a.job, "was": st, "cancelled": True}))
    return 0


def cmd_resume(a):
    ensure_dirs()
    lane = getattr(a, "lane", None) or STEVE
    pz = paused(lane)
    if not pz:
        print("not paused")
        return 0
    os.remove(pause_path(lane))
    if lane == STEVE and pz.get("until") and not pz.get("outcome"):
        record_lane_window("maintenance", pz.get("since"), S.utcnow(), pz.get("reason") or "")
    log("lane%s resumed (paused since %s by %s %s/%s): %s" % ("" if lane == STEVE else " " + lane, pz.get("since"),
                                                           pz.get("job"), pz.get("outcome"), pz.get("cause"),
                                                           a.reason))
    return 0


def sel_text(job):
    sel = job.get("selector", {})
    return " ".join("%s=%s" % (k, ",".join(v) if isinstance(v, list) else v) for k, v in sel.items())


def cmd_sweep(a):
    """The design's sweep rotation, one mod per call: at most one --full per mod per day, overnight (the timer).
    TESTQ_SWEEP_FIX_DRIVERS_OVER_CAP: when the mod's drivers need more than the worker's driver cap, the sweep is
    queued as N chain-group jobs (purpose=sweep) that each fit, so no driver is SKIPPED_BUDGET; each group is
    queued at most once a day."""
    ensure_dirs()
    today = time.strftime("%Y-%m-%d")
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "origin/main"], capture_output=True, text=True,
                       timeout=60)
    if r.returncode != 0:
        print("REFUSED: no origin/main in %s: %s" % (REPO, r.stderr.strip()[-200:]))
        return 2
    pv = preview(a.mod, {"full": True})
    # Owner ruling by card 2026-10-31, "Retest only after a code change": the sweep runs only the chains with no
    # verdict at their code version (gaps.settled). None left: no sweep tonight, whatever the calendar says.
    stop = retest_stop(a.mod)
    todo = [c for c in pv["chains"] or [] if c not in stop]
    if pv["chains"] and not todo:
        print("no sweep: every chain of %s holds a verdict at its code version" % a.mod)
        return 0
    groups = None
    if pv["drivers"] and todo and pv["driver_chains"]:
        g = split_sweep(pv["drivers"], pv["driver_chains"], todo)
        groups = g if len(g) > 1 else None
    sels = [{"chains": g} for g in groups] if groups else (
        [{"chains": todo}] if stop and todo else [{"full": True}])
    todays = []
    for st in STATES:
        for rec in records(st):
            job = job_of(rec)
            if job.get("mod") == a.mod and job.get("purpose") == "sweep" \
                    and time.strftime("%Y-%m-%d", time.localtime(S.parse_ts(job["submitted"]))) == today:
                todays.append((job, st))
    rc = 0
    for sel in sels:
        dup = [(j, st) for j, st in todays if (j.get("selector") or {}).get("full")
               or (j.get("selector") or {}) == sel]
        if dup:
            print("already: %s (%s, submitted %s)" % (dup[0][0]["id"], dup[0][1], dup[0][0]["submitted"]))
            continue
        sub = argparse.Namespace(mod=a.mod, chains=",".join(sel["chains"]) if "chains" in sel else None, rows=None,
                                 item=None, full="full" in sel, purpose="sweep", by=a.by,
                                 sha=r.stdout.strip(), for_item=a.for_item, profile=None, priority=a.priority,
                                 not_before=None, supersedes=None, owner_gate=None, lane="stevedesktop", deploy=None,
                                 timeout=14400, no_canary=False, no_validity=False, no_sha_check=True)
        rc = cmd_submit(sub) or rc
    return rc


FILLER = "BENCH.filler"     # requested_by of a filler job: BENCH's dispatcher, not a window


SITE_HOLD_ROW = "<site hold"      # modcheck's row when the site could not be held: no verdict on the chain
FILL_DAY_S = int(float(os.environ.get("TESTQ_FILL_HOURS") or 8) * 3600)   # filler lane time per local day
FILL_CAP_DEFAULT = 200              # filler JOBS per day: a backstop only; the day budget is lane time
FILL_DRY_RUNS = 2                   # a chain whose last this-many runs measured nothing is DRY ...
FILL_DRY_RETRY_S = 3 * 86400        # ... and is skipped until its latest run is older than this (new wiring lands)


def chain_history(mod, recs=None):
    """-> {chain: [(epoch, kind), ...] oldest first} over finished jobs of MOD, kind per run of that chain:
    "measured" (a row read PASS/FAIL/anything but UNMEASURED), "dry" (every row it ran was UNMEASURED: an unwired or
    unmeasurable chain) or "void" (its only rows were the site hold: the site, not the chain). NOT_RUN rows are not
    runs; a chain named only by NOT_RUN rows gets an empty history (it is known, never run)."""
    hist = {}
    for rec in records("done") if recs is None else recs:
        job, res = job_of(rec), rec.get("result") or {}
        if job.get("mod") != mod:
            continue
        t = S.parse_ts(rec.get("finished") or job["submitted"])
        by = {}
        for r in res.get("rows") or []:
            c = r.get("chain")
            if c:
                by.setdefault(c, []).append(r)
        for c, rows in by.items():
            ran = [r for r in rows if r.get("verdict") != "NOT_RUN"]
            hist.setdefault(c, [])
            if not ran:
                continue
            if all(str(r.get("row") or "").startswith(SITE_HOLD_ROW) for r in ran):
                kind = "void"
            elif all(r.get("verdict") == "UNMEASURED" for r in ran):
                kind = "dry"
            else:
                kind = "measured"
            hist[c].append((t, kind))
    for c in hist:
        hist[c].sort()
    return hist


def ages_of(hist):
    """{chain: epoch of its latest run that was not VOID} (0: never really run)."""
    return {c: max([t for t, k in runs if k != "void"] or [0]) for c, runs in hist.items()}


def chain_ages(mod):
    """-> {chain: epoch of the latest finished job that actually ran a row of it} (see chain_history)."""
    return ages_of(chain_history(mod))


def is_dry(runs, now, dry_runs=FILL_DRY_RUNS, retry_s=FILL_DRY_RETRY_S):
    real = [(t, k) for t, k in runs if k != "void"]
    last = real[-dry_runs:]
    return len(last) >= dry_runs and all(k == "dry" for _, k in last) and now - last[-1][0] < retry_s


def fill_spent_s(recs):
    """Lane seconds the given finished filler jobs took (result started -> finished)."""
    total = 0
    for rec in recs:
        res = (rec or {}).get("result") or {}
        try:
            total += max(0, int(S.parse_ts(res["finished"]) - S.parse_ts(res["started"])))
        except (KeyError, TypeError, ValueError):
            total += sum((res.get("phase_s") or {}).values())
    return total


def lane_proven_after(tail):
    """-> the done record of a job that proves Steve's lane works again after the braking filler jobs TAIL, or None:
    any job (a hand submission counts) on the stevedesktop lane that came back DONE with its canary on (a red canary
    ends INVALID/CANARY, never DONE), finishing after the later of TAIL. Without it a brake outlived its cause: the
    lane was fixed and proven by hand at 11:45 PDT 2026-10-26, yet two stale filler failures kept the filler braked
    all afternoon, because only FILLER jobs were ever read."""
    last = max(S.parse_ts(t.get("finished") or (t.get("result") or {}).get("finished") or "1970-01-01T00:00:00Z")
               for t in tail)
    best = None
    for rec in records("done"):
        job, res = job_of(rec), rec.get("result") or {}
        if (job.get("lane") or STEVE) != STEVE or res.get("outcome") != "DONE" or job.get("canary") is False:
            continue
        try:
            fin = S.parse_ts(rec.get("finished") or res["finished"])
        except (KeyError, TypeError, ValueError):
            continue
        if fin > last and (best is None or fin > best[0]):
            best = (fin, rec)
    return best[1] if best else None


def record_lane_window(kind, since, until, why):
    """Append a closed span SteveDesktop was out for a non-fault reason to lane_windows.jsonl. Never breaks its caller:
    a lost record only means a job that died in it counts as a fault, and a person is asked."""
    try:
        with open(q("lane_windows.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"kind": kind, "since": since, "until": until, "why": str(why)[:200]}) + "\n")
    except OSError as e:
        log("lane window not recorded (%s %s..%s): %s" % (kind, since, until, e))


def lane_windows(now):
    """-> [(kind, since epoch, until epoch)], the recorded non-fault spans: lane_windows.jsonl (`maintenance`, a resumed
    `pause --hours`, an ssh outage that ended) plus the ones still open (a pause with an expiry, ssh down now). A pause
    with no expiry is not here: it says the lane is held, not why."""
    out = []
    try:
        with open(q("lane_windows.jsonl"), encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        lines = []
    for ln in lines:
        try:
            r = json.loads(ln)
            out.append((r["kind"], S.parse_ts(r["since"]), S.parse_ts(r["until"])))
        except (ValueError, KeyError, TypeError):       # a torn line says nothing
            continue
    pz = paused() or {}
    if pz.get("until") and pz.get("since") and not pz.get("outcome"):
        out.append(("maintenance", S.parse_ts(pz["since"]), now))
    down = (read_json(q("ssh_state.json")) or {}).get("down_since")
    if down:
        out.append(("machine_down", S.parse_ts(down), now))
    return out


def machine_killed(res):
    """A result that says the attempt was killed from outside. Any other failure (a refused sync, a stale deploy, a red
    canary) is the lane's own, whatever else was going on at the time."""
    return res.get("outcome") == "INTERRUPTED" or (res.get("outcome"), res.get("cause")) == ("INVALID", "GAME_DIED")


def companion_hold(rev="origin/main"):
    """Why the filler may not submit at `rev`, or None: the stager's record (companion_stage.py) has not staged the
    companion those sources need. No record: the stager never ran, no hold, and the worker's refusal still stands."""
    st = read_json(q("companion_stage.json"))
    if not st:
        return None
    import companion_stage as CS
    return CS.hold_reason(st, rev)


def companion_unready(job):
    """Live, at admission: why this job's companion is not on SteveDesktop, or None. Only once a stager has run."""
    if not read_json(q("companion_stage.json")):
        return None
    import companion_stage as CS
    return CS.unready_at(job["source_sha"])


def nonfault_cause(rec, windows):
    """-> the recorded non-fault cause of a finished job that was not DONE ("cancel", "maintenance", "machine_down",
    "companion_stale", "stale_load"), or None: it counts as a fault. A killed job is excused only by a recorded window overlapping its
    span, admission to finish (a done record older than `sent` has only its last attempt's stamps). A job the worker
    refused for a companion not built from its sources is a cause the stager (companion_stage.py) fixes by itself, and
    brake_release holds its canary until it has."""
    if (rec or {}).get("cancelled"):
        return "cancel"
    res = (rec or {}).get("result") or {}
    import retest
    if retest.companion_stale(res):
        return "companion_stale"
    if retest.stale_load(res) == "repaired":
        # STEVE_LANE_UNSTICK_BRAKED_UNOWNED_8EB8: the game ran a list other than the one modcheck composed; the worker
        # now restarts onto the composed list by itself, so the brake's canary is the proof. Once it restarted and the
        # load still did not fit ("unrepaired"), it is a fault: the steward's ladder and the repair item have it.
        return "stale_load"
    if not machine_killed(res):
        return None
    try:
        end = S.parse_ts(rec.get("finished") or res["finished"])
        start = S.parse_ts(rec.get("sent") or res.get("started") or rec.get("finished") or res["finished"])
    except (KeyError, TypeError, ValueError):
        return None
    for kind, since, until in windows:
        if since <= end and until >= start:
            return kind
    return None


def filler_jobs():
    """Every filler job in any state, oldest submission first."""
    return sorted((job_of(r) for st in ("done", "cancelled", "running", "pending") for r in records(st)
                   if job_of(r).get("requested_by") == FILLER), key=lambda j: j["submitted"])


def brake_tail(mine):
    """-> the two finished filler jobs holding the brake, or None. A deliberate cancel never counts, in either
    direction: a cancelled job (cancelled/, or a running job told to stop, `cancelled` on its done record) is out of the
    window, so it neither brakes the lane nor hides two real failures around it. Nor does a stale companion count beside
    a real fault: that job ran nothing, and the stager fixes it (one crash after it braked the lane, 2026-11-03). Two
    stale in a row do brake: the stager is not keeping up, and the filler would spin. The two jobs must be in a row: a
    job that proved the lane since the earlier one (lane_proven_after) breaks the run."""
    import retest
    gone = {job_of(r)["id"] for r in records("cancelled")} | {job_of(r)["id"] for r in records("done") if r.get("cancelled")}
    counted = [j for j in mine if j["id"] not in gone]
    newest = [read_json(q("done", j["id"] + ".json")) for j in counted[-2:]]
    if len(newest) < 2 or not all(t and (t.get("result") or {}).get("outcome") != "DONE" for t in newest):
        return None
    tail = newest
    if not all(retest.companion_stale(t.get("result")) for t in newest):
        tail = []
        for j in reversed(counted):
            t = read_json(q("done", j["id"] + ".json"))
            if not t or (t.get("result") or {}).get("outcome") == "DONE":
                return None
            if not retest.companion_stale(t.get("result")):
                tail.insert(0, t)
                if len(tail) == 2:
                    break
        if len(tail) < 2:
            return None
    return None if lane_proven_after(tail[:1]) else tail


def fill_plan(mod, n, cap, day_s, now=None):
    """-> {"verdict", "text", ...}: what `fill MOD` would do now, without doing it. Shared by `cmd_fill` and the
    steward (steward.py), so the lane's brakes are read from ONE place. verdict:
      stopped  fill.stop exists          paused  the lane is paused       busy    a ready pending or a running job
      cap      the daily job backstop    budget  the day's lane time      brake   last two filler jobs not DONE (a cancel is not counted: brake_tail),
                                                                          and no DONE+canary job since (lane_proven_after)
      nohist   no history, no catalogue  dry      every chain is DRY       exhausted  nothing may be filler
      companion  a job at origin/main could only die at deploy: its companion is not staged (companion_hold)
      pick     `pick` would be queued (fill_rank: the evidence-gap order)"""
    ensure_dirs()
    now = time.time() if now is None else now
    stop = q("fill.stop")
    if os.path.exists(stop):
        return {"verdict": "stopped", "text": "stopped: %s exists" % stop}
    if paused():
        return {"verdict": "paused", "text": "lane paused; no fill"}
    # an owner-gated, not-yet-due or other-lane job cannot run, so it does not keep Steve busy
    busy = [j for j in records("pending") if ready(j, now)] + steve_running()   # an archmagi job is not Steve
    if busy:
        return {"verdict": "busy", "text": "busy: %d pending/running" % len(busy)}
    today = time.strftime("%Y-%m-%d", time.localtime(now))
    mine = filler_jobs()
    n_today = sum(1 for j in mine if time.strftime("%Y-%m-%d", time.localtime(S.parse_ts(j["submitted"]))) == today)
    out = {"n_today": n_today, "mine": mine}
    if n_today >= cap:
        return dict(out, verdict="cap", text="cap: %d filler jobs today (cap %d)" % (n_today, cap))
    # TESTQ_FILL_CAP_SCALE_AND_SKIP_DRY: the day's brake is lane TIME, not a job count. A count of 8 was spent in an
    # hour of ~4-min jobs and left SteveDesktop idle for the other 23 (2026-10-25).
    spent = fill_spent_s(read_json(q("done", j["id"] + ".json")) for j in mine
                         if time.strftime("%Y-%m-%d", time.localtime(S.parse_ts(j["submitted"]))) == today)
    out["spent"] = spent
    if spent >= day_s:
        return dict(out, verdict="budget", text="cap: filler lane time today %d s >= day budget %d s (%d jobs)"
                    % (spent, day_s, n_today))
    tail = brake_tail(mine)
    if tail:
        return dict(out, verdict="brake", tail=tail,
                    text="brake: the last two filler jobs did not come back DONE (%s); fix the lane, then submit by "
                         "hand" % ", ".join(job_of(t)["id"] for t in tail))
    hold = companion_hold()
    if hold:
        since = (read_json(q("companion_stage.json")) or {}).get("since") or now
        return dict(out, verdict="companion", text=hold, since=since)
    return dict(out, **fill_rank(mod, n, now, today))


def fill_rank(mod, n, now, today=None, exclude=()):
    """The order half of fill_plan (TESTQ_FILL_RANK_BY_EVIDENCE_GAPS; gaps.py has the order and its reasons):
    verdict pick (rank, purpose, pick, row_items), exhausted (nothing may be queued as filler: every chain PASSED or
    FAILED-with-no-fix at the current identity, or is DRY) or nohist (no history and no modcheck catalogue)."""
    import gaps
    today = today or time.strftime("%Y-%m-%d", time.localtime(now))
    recs = records("done")
    hist = chain_history(mod, recs)
    g = gaps.rank(mod, n, now, recs, lambda c: is_dry(hist.get(c) or [], now), exclude=exclude)
    plan = {k: g[k] for k in ("rank", "purpose", "row_items", "dry", "held", "ident", "counts", "flaky", "blind",
                              "why")}
    if g["rank"]:
        return dict(plan, verdict="pick", pick=g["pick"], text="would queue %s" % g["text"])
    if not hist and not g["counts"]["never_run"] and g["blind"]:
        return dict(plan, verdict="nohist", pick=[], text="no chain history for %s yet and %s; no fill"
                    % (mod, "; ".join(g["blind"])))
    if g["all_dry"]:      # every chain measured nothing twice: unwired, a fault for the steward, not exhaustion
        return dict(plan, verdict="dry", pick=[], text="dry: every chain of %s measured nothing in its last %d runs "
                                                       "(%s); no fill" % (mod, FILL_DRY_RUNS, ",".join(g["dry"])))
    return dict(plan, verdict="exhausted", pick=[], text="%s: %s; no fill" % (mod, g["text"]))


def cmd_fill(a):
    """Never let Steve's lane idle, with no LLM in the loop: when nothing is pending or running, queue up to `--n`
    chains of MOD from the first non-empty rank of the evidence-gap order (gaps.py: a FAIL whose fix has landed, an
    item owing a live level, UNMEASURED/NOT_RUN at the current identity, never run at it). A chain that PASSED at the
    current identity is never filler. Brakes (`fill_plan`): the stop file, a daily cap and lane-time budget, a paused
    lane, and two filler jobs in a row that did not come back DONE (a cancel is not counted; a brake whose jobs all have
    a recorded non-fault cause is released by Operations' one canary, brake_release.py)."""
    now = time.time()
    plan = fill_plan(a.mod, a.n, a.cap, a.day_s, now)
    if plan["verdict"] != "pick":
        print(plan["text"])
        return 0
    n_today, spent = plan["n_today"], plan["spent"]
    # A chain the history still holds but modcheck no longer declares (renamed, removed) would be re-submitted every
    # tick and refused every time, and Steve would idle for good: drop it and rank again.
    gone_all = set()
    for _ in range(3):
        why = bad_selection(a.mod, {"chains": plan["pick"]}) if plan["pick"] else None
        gone = unknown_chains(why) if why else set()
        if not gone & set(plan["pick"]):
            break
        gone_all |= gone
        log("filler: %s no longer declares %s; not ranked" % (a.mod, ",".join(sorted(gone))))
        plan = dict(plan, **fill_rank(a.mod, a.n, now, exclude=gone_all))
    if plan["verdict"] != "pick":
        print(plan["text"])
        return 0
    pick = plan["pick"]
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "origin/main"], capture_output=True, text=True,
                       timeout=60)
    if r.returncode != 0:
        print("REFUSED: no origin/main in %s: %s" % (REPO, r.stderr.strip()[-200:]))
        return 2
    log("filler: %s %s %s (%d today, cap %d, %d s of %d s; %d dry skipped%s)" % (
        a.mod, plan["rank"], ",".join(pick), n_today + 1, a.cap, spent, a.day_s, len(plan["dry"]),
        "; blind: " + "; ".join(plan["blind"]) if plan["blind"] else ""))
    sub = argparse.Namespace(mod=a.mod, chains=",".join(pick), rows=None, item=None, full=False,
                             purpose=plan["purpose"], by=FILLER, sha=r.stdout.strip(), for_item=None, profile=None,
                             priority=20, not_before=None, supersedes=None, owner_gate=None, lane="stevedesktop",
                             deploy=None, timeout=7200, no_canary=False, no_validity=False, no_sha_check=True,
                             row_item=["%s=%s" % kv for kv in sorted((plan.get("row_items") or {}).items())])
    return cmd_submit(sub)


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
            extra = (rec.get("attempt") and rec["attempt"] + ("" if host_of(rec) == STEVE else " @" + host_of(rec))) or ("%s %s %s" % (res.get("outcome"), res.get("cause") or "",
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
# git's auto gc/maintenance DETACHES by default; a oneshot tick's pull/ingest then left a background repack in the unit's
# cgroup, killed or orphaned at unit end (463 "Found left-over process (git)" lines on 2026-10-26, four tmp_pack_* files,
# 8,972 loose objects that never shrank, so every tick started another). Foreground auto gc finishes inside the tick.
GIT_ENV = ("Environment=GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=gc.autoDetach GIT_CONFIG_VALUE_0=false "
           "GIT_CONFIG_KEY_1=maintenance.autoDetach GIT_CONFIG_VALUE_1=false\n")
UNITS = {
    "testq-tick.service": """[Unit]
Description=testq dispatch tick (TESTQ_DISPATCHER_BUILD_SSH_NO_LLM)

[Service]
Type=oneshot
WorkingDirectory={clone}
{git_env}ExecStartPre=-/usr/bin/git -C {clone} pull -q --ff-only origin main
ExecStart=-/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/companion_stage.py run
ExecStart=/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/testq.py tick
ExecStart=-/bin/bash -c 'for m in $(/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/coverage.py wired); do /usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/testq.py fill "$m"; done'
ExecStart=-/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/testq.py steward
ExecStart=-/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/ingest.py
ExecStart=/usr/bin/python3 {clone}/src/RimMandrake/Utils/findings_fold.py run
TimeoutStartSec=900
""",
    "testq-sweep.service": """[Unit]
Description=testq daily full sweep request (design: at most one --full per mod per day, overnight)

[Service]
Type=oneshot
WorkingDirectory={clone}
{git_env}ExecStartPre=-/usr/bin/git -C {clone} pull -q --ff-only origin main
ExecStart=/bin/bash -c 'for m in ${{TESTQ_SWEEP_MODS:-FlowWorks}}; do /usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/testq.py sweep "$m"; done'
TimeoutStartSec=300
""",
    "testq-sweep.timer": """[Unit]
Description=testq daily full sweep at 01:30 local

[Timer]
OnCalendar=*-*-* 01:30:00
Persistent=true

[Install]
WantedBy=timers.target
""",
    # the steward cannot see its own tick stop (design 2026-10-26 section 6.1): this watcher has its own timer and
    # never pulls, so a bad pull that kills the tick does not take the watcher with it
    "testq-steward-watch.service": """[Unit]
Description=testq steward heartbeat watcher (STEVE_STEWARD_BUILD_NO_LLM_OWNER)

[Service]
Type=oneshot
WorkingDirectory={clone}
ExecStart=/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/testq.py steward-watch
TimeoutStartSec=300
""",
    "testq-steward-watch.timer": """[Unit]
Description=testq steward heartbeat watcher every 60 s

[Timer]
OnBootSec=3min
OnUnitInactiveSec=60s
AccuracySec=5s

[Install]
WantedBy=timers.target
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


def cmd_pause(a):
    ensure_dirs()
    if paused():
        print("already paused: %s" % json.dumps(paused()))
        return 1
    now = time.time()
    rec = {"since": S.utcnow(), "job": None, "attempt": None, "outcome": None, "cause": None, "reason": a.reason,
           "note": "paused by hand", "until": None}
    if a.hours:
        rec["until"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now + a.hours * 3600))
    S.dump(rec, pause_path())
    log("LANE PAUSED by hand%s: %s; `testq.py resume --reason R` lifts it" % (
        " until " + rec["until"] if rec["until"] else " (no expiry: the steward escalates it at 60 min)", a.reason))
    return 0


def cmd_maintenance(a):
    """Record, after the fact too, that SteveDesktop was taken down on purpose or crashed for a known hardware reason,
    so a job that died inside the window does not count as a lane fault (nonfault_cause)."""
    ensure_dirs()
    until = a.until or S.utcnow()
    try:
        bad = S.parse_ts(a.since) > S.parse_ts(until)
    except (TypeError, ValueError) as e:
        print("REFUSED: --since/--until: %s" % e)
        return 2
    if bad:
        print("REFUSED: --since %s is after --until %s" % (a.since, until))
        return 2
    record_lane_window("maintenance", a.since, until, a.reason)
    print(json.dumps({"kind": "maintenance", "since": a.since, "until": until, "reason": a.reason}))
    return 0


def cmd_steward(a):
    import steward
    return steward.cmd_steward(a)


def cmd_steward_watch(a):
    import steward
    return steward.cmd_watch(a)


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
                f.write(text.format(clone=DISPATCH, git_env=GIT_ENV))
    if a.apply:
        for argv in (["daemon-reload"], ["enable", "--now", "testq-tick.timer"],
                     ["enable", "--now", "testq-sweep.timer"], ["enable", "--now", "testq-steward-watch.timer"]):
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
    s.add_argument("--row-item", action="append", metavar="ROW_OR_CHAIN=ITEM",
                   help="a row id (or chain name) whose result belongs to ITEM, not --for-item (repeatable); "
                        "ingest then verifies each item from its own rows only")
    s.add_argument("--profile", choices=S.PROFILES)
    s.add_argument("--priority", type=int)
    s.add_argument("--not-before")
    s.add_argument("--supersedes")
    s.add_argument("--owner-gate")
    s.add_argument("--lane", choices=S.LANES)
    s.add_argument("--gate", choices=S.GATES, help="modcheck run --gate (default: modcheck's own)")
    s.add_argument("--deploy", action="append")
    s.add_argument("--timeout", type=int)
    s.add_argument("--no-canary", action="store_true")
    s.add_argument("--no-validity", action="store_true")
    s.add_argument("--no-sha-check", action="store_true", help="skip the is-it-on-origin/main check")
    s.add_argument("--retest-why", help="run chains that already hold a verdict at their code version, and say why")
    s = sub.add_parser("list")
    s.add_argument("--state", choices=STATES)
    s = sub.add_parser("show")
    s.add_argument("job")
    s = sub.add_parser("cancel")
    s.add_argument("job")
    s.add_argument("--reason", required=True)
    s = sub.add_parser("resume")
    s.add_argument("--reason", required=True)
    s.add_argument("--lane", choices=(STEVE, ARCHMAGI), default=STEVE)
    s = sub.add_parser("sweep")
    s.add_argument("mod")
    s.add_argument("--by", default="BENCH", help="the requesting seat (default BENCH; FOUNDRY owns FlowWorks since the v3 cutover)")
    s.add_argument("--for-item")
    s.add_argument("--priority", type=int, default=40)
    s = sub.add_parser("fill", help="queue the stalest chains when the lane is idle (the tick runs it)")
    s.add_argument("mod")
    s.add_argument("--n", type=int, default=int(os.environ.get("TESTQ_FILL_CHAINS", "4")), help="chains per job")
    s.add_argument("--cap", type=int, default=int(os.environ.get("TESTQ_FILL_CAP") or FILL_CAP_DEFAULT),
                   help="filler jobs per day: a backstop; the day budget is --day-s of lane time")
    s.add_argument("--day-s", type=int, default=FILL_DAY_S,
                   help="filler lane seconds per local day (TESTQ_FILL_HOURS, default 8 h)")
    sub.add_parser("tick")
    s = sub.add_parser("archmagi-report", help="the section 2 trial: verified items/day net of load and displaced time")
    s.add_argument("--days", type=float, default=7.0)
    s = sub.add_parser("pause", help="pause the lane by hand (with --hours: intentional until then)")
    s.add_argument("--reason", required=True)
    s.add_argument("--hours", type=float)
    s = sub.add_parser("maintenance", help="record a maintenance reboot or a known hardware outage of SteveDesktop")
    s.add_argument("--reason", required=True)
    s.add_argument("--since", required=True, help="ISO UTC start")
    s.add_argument("--until", help="ISO UTC end, default now")
    sub.add_parser("steward", help="the lane steward pass (the tick runs it)")
    sub.add_parser("steward-watch", help="the steward's heartbeat watcher (its own timer)")
    s = sub.add_parser("install-timer")
    s.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    if getattr(a, "job", None) and not S.JOB_ID_RE.match(a.job):
        print("REFUSED: %r is not a job id" % a.job)
        return 2
    return {"submit": cmd_submit, "list": cmd_list, "show": cmd_show, "cancel": cmd_cancel, "resume": cmd_resume,
            "sweep": cmd_sweep, "fill": cmd_fill,
            "tick": cmd_tick, "pause": cmd_pause, "maintenance": cmd_maintenance, "steward": cmd_steward, "steward-watch": cmd_steward_watch,
            "install-timer": cmd_install_timer, "archmagi-report": cmd_archmagi_report}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
