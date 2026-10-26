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
                                     QHOME/fill.stop, lane time per local day (TESTQ_FILL_HOURS, 20 h; a job
                                     backstop TESTQ_FILL_CAP, 200), a paused lane, two non-DONE fillers running;
                                     every tick runs it for each of TESTQ_FILL_MODS (FlowWorks)
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
        if host == ARCHMAGI and not rec.get("yield"):
            holder = bridge_holder()
            if holder:     # a window took the bridge anyway (forced): the seat wins, the job goes back
                rec.update(**{"yield": holder})
                move(jid, "running", "running", rec)
                remote(["stop", "--attempt", latest])
                log("%s on archmagi: %s took the bridge mid-run; attempt %s stopped, the job goes back" % (
                    jid, holder, latest))
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
    if host == ARCHMAGI and not rec.get("cancel") and archmagi_bounce(rec, res):
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
    if host != STEVE:
        done["host"] = host
    move(jid, "running", "done", done)
    worker_for(host)(["ack", "--attempt", res["attempt"]])
    log("%s DONE-> %s %s %s (%s%s)" % (jid, res["outcome"], res["cause"] or "", res.get("counts"), res["attempt"],
                                       "" if host == STEVE else " on " + host))
    why = PAUSE_ON.get((res["outcome"], res["cause"]))
    if why and not rec.get("cancel") and not paused(host):
        S.dump({"since": S.utcnow(), "job": jid, "attempt": res["attempt"], "outcome": res["outcome"],
                "cause": res["cause"], "reason": why, "note": (res.get("note") or "")[-300:]}, pause_path(host))
        log("LANE%s PAUSED by %s %s/%s: %s; `testq.py resume%s --reason R` lifts it" % (
            "" if host == STEVE else " " + host, jid, res["outcome"], res["cause"], why,
            "" if host == STEVE else " --lane " + host))


def pause_path(host=STEVE):
    return q("paused.json") if host == STEVE else q("%s_paused.json" % host)


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
    env.update(TESTQ_HOME=home, TESTQ_WORKER_HOST=ARCHMAGI,
               TESTQ_MODS_DIR=os.environ.get("TESTQ_ARCHMAGI_MODS_DIR") or ARCH_MODS_DIR)
    try:
        r = subprocess.run([sys.executable, os.path.join(run, "infrastructure", "stevedesktop", "worker.py")] + args,
                           cwd=run, env=env, input=stdin, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, {"error": "archmagi worker %s: %s" % (" ".join(args), e)}
    lines = r.stdout.strip().splitlines()
    try:
        return r.returncode, json.loads(lines[-1])
    except (ValueError, IndexError):
        return r.returncode, {"error": "no JSON from the archmagi worker (exit %d): %s" % (
            r.returncode, (r.stdout + r.stderr)[-300:])}


def archmagi_bounce(rec, res):
    """A REFUSED attempt that measured nothing about the mod (Archmagi may not deploy / has no game / its guard was
    taken) or one stopped to yield to a window: the job goes back to pending instead of finishing. -> True if so."""
    job = rec["job"]
    jid = job["id"]
    yielded = rec.get("yield") and res["outcome"] == "INTERRUPTED"
    if not yielded and not (res["outcome"] == "REFUSED" and res["cause"] in ARCH_BOUNCE):
        return False
    why = "yielded to %s" % rec["yield"] if yielded else "%s/%s: %s" % (res["outcome"], res["cause"],
                                                                        (res.get("note") or "")[:200])
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
    drain_outbox(archmagi_worker(["outbox"])[1].get("outbox") or [], ARCHMAGI)
    if os.environ.get("TESTQ_ARCHMAGI") != "1" or any(host_of(r) == ARCHMAGI for r in records("running")):
        return
    ok, why = archmagi_gate()
    cands = archmagi_candidates(steve_up, steve_busy) if ok else []
    said = why if not ok else ("no candidate job" if not cands else None)
    if said and arch_state().get("last_gate") != said.split(" (")[0].split(" used ")[0]:
        log("archmagi lane: %s" % said)
    if said:
        arch_state_update(last_gate=said.split(" (")[0].split(" used ")[0])
        return
    job = cands[0]
    rc, o = archmagi_worker(["start"], stdin=json.dumps(job))
    if not o.get("attempt"):
        log("%s: archmagi start failed (exit %d): %s; stays pending" % (job["id"], rc, o.get("error") or o))
        return
    move(job["id"], "pending", "running", {"job": job, "attempt": o["attempt"], "sent": S.utcnow(), "host": ARCHMAGI,
                                           "attempts": [o["attempt"]], "auto_retries": 0, "cancel": False})
    arch_state_update(last_gate=None)
    log("%s admitted on archmagi -> %s (%s, prio %d, %s, lane %s; gate: %s)" % (
        job["id"], o["attempt"], job["purpose"], job["priority"], job["profile"], job["lane"], why))


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
    out = {"refusal": None, "rows": None, "drivers": None}
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
        for tag, key in (("EXPECTED_ROWS ", "rows"), ("EXPECTED_DRIVERS ", "drivers")):
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
    log("lane%s resumed (paused since %s by %s %s/%s): %s" % ("" if lane == STEVE else " " + lane, pz.get("since"),
                                                           pz.get("job"), pz.get("outcome"), pz.get("cause"),
                                                           a.reason))
    return 0


def sel_text(job):
    sel = job.get("selector", {})
    return " ".join("%s=%s" % (k, ",".join(v) if isinstance(v, list) else v) for k, v in sel.items())


def cmd_sweep(a):
    """The design's sweep rotation, one mod per call: at most one --full per mod per day, overnight (the timer)."""
    ensure_dirs()
    today = time.strftime("%Y-%m-%d")
    for st in STATES:
        for rec in records(st):
            job = job_of(rec)
            if job.get("mod") == a.mod and job.get("purpose") == "sweep" and (job.get("selector") or {}).get("full") \
                    and time.strftime("%Y-%m-%d", time.localtime(S.parse_ts(job["submitted"]))) == today:
                print("already: %s (%s, submitted %s)" % (job["id"], st, job["submitted"]))
                return 0
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "origin/main"], capture_output=True, text=True,
                       timeout=60)
    if r.returncode != 0:
        print("REFUSED: no origin/main in %s: %s" % (REPO, r.stderr.strip()[-200:]))
        return 2
    sub = argparse.Namespace(mod=a.mod, chains=None, rows=None, item=None, full=True, purpose="sweep", by=a.by,
                             sha=r.stdout.strip(), for_item=a.for_item, profile=None, priority=a.priority,
                             not_before=None, supersedes=None, owner_gate=None, lane="stevedesktop", deploy=None,
                             timeout=14400, no_canary=False, no_validity=False, no_sha_check=True)
    return cmd_submit(sub)


FILLER = "BENCH.filler"     # requested_by of a filler job: BENCH's dispatcher, not a window


SITE_HOLD_ROW = "<site hold"      # modcheck's row when the site could not be held: no verdict on the chain
FILL_DAY_S = int(float(os.environ.get("TESTQ_FILL_HOURS") or 20) * 3600)   # filler lane time per local day
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


def fill_pick(hist, n, now):
    """-> (the `n` stalest chains that are not DRY, the DRY chains skipped). A DRY chain (its last FILL_DRY_RUNS runs
    measured nothing: unwired, or its driver never ran) would only spend a filler job on UNMEASURED again; it is
    re-tried once its latest run is FILL_DRY_RETRY_S old, so newly wired chains come back on their own."""
    ages = ages_of(hist)
    dry = sorted(c for c in hist if is_dry(hist[c], now))
    pick = sorted((c for c in hist if c not in dry), key=lambda c: (ages[c], c))[:n]
    return pick, dry


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


def cmd_fill(a):
    """Never let Steve's lane idle, with no LLM in the loop: when nothing is pending or running, queue the
    `--n` stalest chains of MOD (oldest last real run first). Brakes: the stop file, a daily cap, a paused lane, and
    two filler jobs in a row that did not come back DONE."""
    ensure_dirs()
    stop = q("fill.stop")
    if os.path.exists(stop):
        print("stopped: %s exists" % stop)
        return 0
    if paused():
        print("lane paused; no fill")
        return 0
    now = time.time()   # an owner-gated, not-yet-due or other-lane job cannot run, so it does not keep Steve busy
    busy = [j for j in records("pending") if ready(j, now)] + steve_running()   # an archmagi job is not Steve
    if busy:
        print("busy: %d pending/running" % len(busy))
        return 0
    today = time.strftime("%Y-%m-%d")
    mine = sorted((job_of(r) for st in ("done", "cancelled", "running", "pending") for r in records(st)
                   if job_of(r).get("requested_by") == FILLER), key=lambda j: j["submitted"])
    n_today = sum(1 for j in mine if time.strftime("%Y-%m-%d", time.localtime(S.parse_ts(j["submitted"]))) == today)
    if n_today >= a.cap:
        print("cap: %d filler jobs today (cap %d)" % (n_today, a.cap))
        return 0
    # TESTQ_FILL_CAP_SCALE_AND_SKIP_DRY: the day's brake is lane TIME, not a job count. A count of 8 was spent in an
    # hour of ~4-min jobs and left SteveDesktop idle for the other 23 (2026-10-25).
    spent = fill_spent_s(read_json(q("done", j["id"] + ".json")) for j in mine
                         if time.strftime("%Y-%m-%d", time.localtime(S.parse_ts(j["submitted"]))) == today)
    if spent >= a.day_s:
        print("cap: filler lane time today %d s >= day budget %d s (%d jobs)" % (spent, a.day_s, n_today))
        return 0
    tail = [read_json(q("done", j["id"] + ".json")) for j in mine[-2:]]
    if len(tail) == 2 and all(t and (t.get("result") or {}).get("outcome") != "DONE" for t in tail):
        print("brake: the last two filler jobs did not come back DONE (%s); fix the lane, then submit by hand"
              % ", ".join(j["id"] for j in mine[-2:]))
        return 0
    hist = chain_history(a.mod)
    if not hist:
        print("no chain history for %s yet (one full sweep seeds it); no fill" % a.mod)
        return 0
    pick, dry = fill_pick(hist, a.n, now)
    # A chain the history still holds but modcheck no longer declares (renamed, removed) is forever the stalest, and
    # cmd_submit refuses any job naming it: without this the filler re-submits it every tick and Steve idles for good.
    for _ in range(3):
        why = bad_selection(a.mod, {"chains": pick}) if pick else None
        gone = unknown_chains(why) if why else set()
        if not gone & set(pick):
            break
        log("filler: %s no longer declares %s; dropped from the fill history" % (a.mod, ",".join(sorted(gone))))
        hist = {c: v for c, v in hist.items() if c not in gone}
        pick, dry = fill_pick(hist, a.n, now)
    if not pick:
        print("dry: every chain of %s measured nothing in its last %d runs (%s); no fill" % (
            a.mod, FILL_DRY_RUNS, ",".join(dry)))
        return 0
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "origin/main"], capture_output=True, text=True,
                       timeout=60)
    if r.returncode != 0:
        print("REFUSED: no origin/main in %s: %s" % (REPO, r.stderr.strip()[-200:]))
        return 2
    log("filler: %s stalest %s (%d today, cap %d, %d s of %d s; %d dry skipped)" % (
        a.mod, ",".join(pick), n_today + 1, a.cap, spent, a.day_s, len(dry)))
    sub = argparse.Namespace(mod=a.mod, chains=",".join(pick), rows=None, item=None, full=False, purpose="guard",
                             by=FILLER, sha=r.stdout.strip(), for_item=None, profile=None, priority=20,
                             not_before=None, supersedes=None, owner_gate=None, lane="stevedesktop", deploy=None,
                             timeout=7200, no_canary=False, no_validity=False, no_sha_check=True)
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
UNITS = {
    "testq-tick.service": """[Unit]
Description=testq dispatch tick (TESTQ_DISPATCHER_BUILD_SSH_NO_LLM)

[Service]
Type=oneshot
WorkingDirectory={clone}
ExecStartPre=-/usr/bin/git -C {clone} pull -q --ff-only origin main
ExecStart=/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/testq.py tick
ExecStart=-/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/ingest.py
ExecStart=-/bin/bash -c 'for m in ${{TESTQ_FILL_MODS:-FlowWorks}}; do /usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/testq.py fill "$m"; done'
TimeoutStartSec=900
""",
    "testq-sweep.service": """[Unit]
Description=testq daily full sweep request (design: at most one --full per mod per day, overnight)

[Service]
Type=oneshot
WorkingDirectory={clone}
ExecStartPre=-/usr/bin/git -C {clone} pull -q --ff-only origin main
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
        for argv in (["daemon-reload"], ["enable", "--now", "testq-tick.timer"],
                     ["enable", "--now", "testq-sweep.timer"]):
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
    s.add_argument("--by", default="BENCH", help="the requesting seat (BENCH owns FlowWorks)")
    s.add_argument("--for-item")
    s.add_argument("--priority", type=int, default=40)
    s = sub.add_parser("fill", help="queue the stalest chains when the lane is idle (the tick runs it)")
    s.add_argument("mod")
    s.add_argument("--n", type=int, default=int(os.environ.get("TESTQ_FILL_CHAINS", "4")), help="chains per job")
    s.add_argument("--cap", type=int, default=int(os.environ.get("TESTQ_FILL_CAP") or FILL_CAP_DEFAULT),
                   help="filler jobs per day: a backstop; the day budget is --day-s of lane time")
    s.add_argument("--day-s", type=int, default=FILL_DAY_S,
                   help="filler lane seconds per local day (TESTQ_FILL_HOURS, default 20 h)")
    sub.add_parser("tick")
    s = sub.add_parser("install-timer")
    s.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    if getattr(a, "job", None) and not S.JOB_ID_RE.match(a.job):
        print("REFUSED: %r is not a job id" % a.job)
        return 2
    return {"submit": cmd_submit, "list": cmd_list, "show": cmd_show, "cancel": cmd_cancel, "resume": cmd_resume,
            "sweep": cmd_sweep, "fill": cmd_fill,
            "tick": cmd_tick,
            "install-timer": cmd_install_timer}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
