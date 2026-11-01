#!/usr/bin/env python3
"""steward.py - the SteveDesktop lane steward, no LLM (STEVE_STEWARD_BUILD_NO_LLM_OWNER).

Design: design/RimMandrake/work_allocation_framework_2026-10-26.md section 6. The owner, 2026-10-26: "include some
persistent responsibility to guide SteveDesktop so it doesn't sit idle like that anymore." The lane sat 166 min
braked and unowned that morning; nothing in the system noticed, so nobody did.

  testq.py steward         one pass. The tick service runs it every 60 s after `tick` and the fill loop, and
                           before ingest.py (which commits and pushes the RUNNER lines it wrote).
  testq.py steward-watch   the heartbeat watcher, on its own timer (testq-steward-watch.timer, every 60 s): the
                           steward cannot see its own tick stop.
  testq.py pause --reason R [--hours H]   an intentional pause: with an expiry it never escalates until it expires.

What it knows (section 6.1), first match wins:
  UNREACHABLE      ssh_state.json says SteveDesktop is down                         fault
  QUARANTINE       QHOME/quarantine.json exists (an operator's hand quarantine)     fault, escalates at once
  RUNNING          a SteveDesktop job is running                                    the only state that ends an incident
  PAUSED           paused.json: an auto pause (it names an outcome) is a fault at once; a manual pause with an `until`
                   in the future is intentional; any other manual pause (or QHOME/fill.stop, aged by its mtime) turns
                   into a fault 60 min after it began
  READY            a job is ready but not admitted: a fault once it has waited 5 min (a not-ours busy worker, a
                   dispatcher that stopped admitting)
  BRAKED           fill_plan's brake (two filler jobs in a row not DONE): a fault, at once when either failure is a
                   HARNESS-class cause (HARNESS, DEPLOY, SYNC, SOURCE_SHA_MISSING, BLOCKED_SELECTION) with the job ids;
                   the day's lane-time budget or job cap is a brake too but NOT a fault: it expires at local midnight
  IDLE_EMPTY       nothing queued and the fill found nothing selectable (no history, every chain DRY), or it would
                   queue chains yet nothing is pending (the fill itself failed): an evidence gap, a fault
  EXHAUSTED        the fill's gap scan found nothing to do at all (fill_plan verdict "exhausted"): not a fault
  TICK_STOPPED     (after RUNNING and PAUSED: a job running or an intentional pause is not a fault) testq-tick.timer is not active on this machine (stopped by hand or by another seat): nothing is
                   dispatched, filled, reconciled or ingested; a fault at once (it outranks READY and IDLE_EMPTY,
                   whose "the fill failed?" was the misdiagnosis of 2026-10-28, when a cutover stopped every
                   rm-*/testq-* timer at 05:04 and nobody restarted them). An unknown state (no systemd) says nothing.
  STALE_HEARTBEAT  the watcher's: steward.json not written for 5 min

The unowned clock (section 6.1) adds the time between two passes while the state is a fault. Non-fault states freeze
it; only RUNNING ends the incident. A claim on the escalation item pauses it while the claim's lease is live, or for
2 h after a claim with no lease; a lapsed or released lease does not.

Escalation (section 6.4), each at most once per incident:
  T+10 min   spawn STEVE_LANE_UNSTICK_<STATE>_UNOWNED_<hex4> --for BENCH --needs offline (from the steward's own item),
             naming the state and job ids, or note the still-open item of an earlier incident (never a duplicate);
             a failed `steve:lane` record lights the pulse health row
  T+30 min   `rimflow raise` it: first in `rimflow next --seat BENCH` and a line in the phone brief
  T+120 min  with no claim: spawn for OWNER (needs owner; titled "IN PERSON:" when SteveDesktop is unreachable)
Recovery (RUNNING again) records `steve:lane` ok, notes the item and drops the items the incident spawned.

The LLM wake (the owner's card ruling 2026-10-26 12:27 PDT, "Yes, after 30 min", on STEVE_STEWARD_BUILD_NO_LLM_OWNER):
once an incident has been raised (T+30) and no claim holds its item, the steward MAY start ONE headless Claude session
to diagnose and restart the lane. ON by default, with these guards:
  one at a time   a fixed transient unit (systemd-run --user --unit testq-steward-wake); an active one blocks another
  hard caps       --max-budget-usd TESTQ_WAKE_BUDGET_USD (5) and RuntimeMaxSec TESTQ_WAKE_MAX_S (2700 s)
  no loop         one wake per incident, and TESTQ_WAKE_COOLDOWN_S (4 h) between any two (QHOME/wake.json)
  off switch      QHOME/wake.stop, or TESTQ_STEWARD_WAKE=0
The session runs in TESTQ_WAKE_CLONE (~/rm/bench, the BENCH seat's clone) as RIMFLOW_SEAT=BENCH, with no permission
flags of its own (the clone's settings decide); its brief (QHOME/wake/<stamp>.brief.md) points at steward.json,
steward.jsonl, tick.log, the escalation item and infrastructure/stevedesktop/RUNBOOK.md. Its output:
QHOME/wake/<stamp>.log.
A rung is published the pass it is written, and the session is never pointed at an item its clone cannot see: the spawn
lives on this clone's RUNNER shard, and the wake runs in another clone (BE53: that clone was behind; F27F: the publish
was blocked), where `claim` says "never been filed" (TESTQSTEWARD_FIX_ESCALATES_TO_A_GHOST). maybe_wake publishes and
pulls the wake clone with --ff-only, holds for up to TESTQ_WAKE_HOLD_S (600 s), then wakes anyway with a brief saying
the item is unpublished: a blocked publish can be the very fault the session has to fix (F27F).

Files (QHOME): steward.json {ts, epoch, state, fault, reason, jobs, incident, last_item} every pass; steward.jsonl one
line per state change or escalation; steward_watch.json the watcher's own state.
"""
import fcntl
import glob
import json
import os
import secrets
import shlex
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import schema as S  # noqa: E402
import testq as T  # noqa: E402

RIMFLOW_DIR = os.path.join(T.REPO, "src", "RimMandrake", "rimflow")
STEWARD_ITEM = os.environ.get("TESTQ_STEWARD_ITEM", "STEVE_STEWARD_BUILD_NO_LLM_OWNER")
L1_S, L2_S, L3_S = 600, 1800, 7200          # section 6.4: T+10, T+30, T+120 min of unowned clock
READY_GRACE_S = 300
MANUAL_PAUSE_S = 3600                       # section 6.1: "a pause with neither escalates at 60 min"
CLAIM_HOLD_S = 7200                         # a claim without a lease pauses the clock this long
LOCK_WAIT_S = 30                            # a pass waits this long for the other pass, then skips
STALE_S = 300                               # the watcher: steward.json older than this
HARNESS_CAUSES = {"HARNESS", "DEPLOY", "SYNC", "SOURCE_SHA_MISSING", "BLOCKED_SELECTION"}
TAG = {"UNREACHABLE": "OFFLINE", "QUARANTINE": "QUARANTINE", "PAUSED": "PAUSED", "READY": "STALLED",
       "BRAKED": "BRAKED", "IDLE_EMPTY": "IDLE", "STALE_HEARTBEAT": "STALLED", "TICK_STOPPED": "STALLED"}
LANE_TASK = "steve:lane"


def path(*parts):
    return T.q(*parts)


def iso(epoch):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def mods_default():
    return os.environ.get("TESTQ_FILL_MODS", "FlowWorks").split()


# ---------------------------------------------------------------- what state the lane is in

def _st(state, reason, fault_at=None, at_once=False, jobs=()):
    """fault_at: the epoch from which the state is a fault (0: already; None: never)."""
    return {"state": state, "reason": reason, "fault_at": fault_at, "at_once": at_once, "jobs": list(jobs)}


def lane_state(now, mods=None):
    ss = T.read_json(path("ssh_state.json")) or {}
    if ss.get("down_since"):
        return _st("UNREACHABLE", "ssh to SteveDesktop down since %s: %s" % (ss["down_since"],
                                                                            (ss.get("last_error") or "")[:120]), 0)
    if os.path.exists(path("quarantine.json")):
        qz = T.read_json(path("quarantine.json")) or {}
        return _st("QUARANTINE", "quarantined: %s" % (qz.get("reason") or "quarantine.json exists"), 0, at_once=True)
    run = T.steve_running()
    if run:
        return _st("RUNNING", "running %s" % ",".join(r["job"]["id"] for r in run), jobs=[r["job"]["id"] for r in run])
    pz = T.paused()
    if pz:
        since = S.parse_ts(pz["since"]) if pz.get("since") else now
        why = pz.get("reason") or pz.get("note") or ""
        if pz.get("outcome"):
            return _st("PAUSED", "auto pause by %s %s/%s: %s" % (pz.get("job"), pz.get("outcome"), pz.get("cause"),
                                                                 why[:120]), 0, jobs=[pz["job"]] if pz.get("job") else [])
        if pz.get("until"):
            until = S.parse_ts(pz["until"])
            return _st("PAUSED", "paused until %s: %s" % (pz["until"], why[:120]), until)
        return _st("PAUSED", "paused since %s with no expiry: %s" % (pz.get("since"), why[:120]),
                   since + MANUAL_PAUSE_S)
    if os.path.exists(path("fill.stop")):
        return _st("PAUSED", "fill stopped: %s exists" % path("fill.stop"),
                   os.path.getmtime(path("fill.stop")) + MANUAL_PAUSE_S)
    tick = tick_timer_state()
    if tick in ("inactive", "failed", "deactivating"):
        return _st("TICK_STOPPED", "testq-tick.timer is %s: nothing is dispatched, filled or ingested; "
                   "`systemctl --user start testq-tick.timer` (unless a cutover still needs it held: look for "
                   "~/rm/paused-timers-*.txt)" % tick, 0, at_once=True)
    ready = [j for j in T.records("pending") if T.ready(j, now)]
    if ready:
        t0 = min(max(S.parse_ts(j["submitted"]), S.parse_ts(j["not_before"]) if j.get("not_before") else 0)
                 for j in ready)
        return _st("READY", "%d ready job(s) not admitted (oldest ready since %s)" % (len(ready), iso(t0)),
                   t0 + READY_GRACE_S, jobs=[j["id"] for j in ready])
    plans = {m: T.fill_plan(m, int(os.environ.get("TESTQ_FILL_CHAINS", "4")),
                            int(os.environ.get("TESTQ_FILL_CAP") or T.FILL_CAP_DEFAULT), T.FILL_DAY_S, now)
             for m in mods or mods_default()}
    by = {}
    for m, p in plans.items():
        by.setdefault(p["verdict"], []).append(m)
    if "brake" in by:
        tails = [t for m in by["brake"] for t in plans[m].get("tail") or [] if t]
        jobs = [t["job"]["id"] if isinstance(t.get("job"), dict) else t.get("job") for t in tails]
        res = [t.get("result") or {} for t in tails]
        causes = ["%s/%s" % (r.get("outcome"), r.get("cause")) for r in res]
        harness = any(r.get("cause") in HARNESS_CAUSES for r in res)
        return _st("BRAKED", "filler brake on %s: last two filler jobs not DONE (%s: %s)%s"
                   % (",".join(by["brake"]), ",".join(str(j) for j in jobs), ", ".join(causes),
                      "; HARNESS-class, escalated at once" if harness else ""), 0, at_once=harness, jobs=jobs)
    if "pick" in by:
        return _st("IDLE_EMPTY", "fill would queue %s but nothing is pending (the fill failed?)"
                   % "; ".join("%s: %s" % (m, ",".join(plans[m]["pick"])) for m in by["pick"]), 0)
    gaps = [m for v in ("nohist", "dry") for m in by.get(v, [])]
    if gaps:
        return _st("IDLE_EMPTY", "nothing selectable: " + "; ".join(plans[m]["text"][:160] for m in gaps), 0)
    capped = by.get("cap", []) + by.get("budget", [])
    if capped:
        return _st("BRAKED", "day brake: " + plans[capped[0]]["text"][:200])
    if "exhausted" in by:
        return _st("EXHAUSTED", "the gap scan found nothing to fill: " + plans[by["exhausted"][0]]["text"][:200])
    return _st("IDLE_EMPTY", "idle; fill says: " + "; ".join("%s: %s" % (m, p["text"][:80]) for m, p in plans.items()),
               0)


# ---------------------------------------------------------------- side effects (tests replace these)

def rimflow(*args):
    import ingest
    return ingest.rimflow(*args)


def publish():
    if os.environ.get("TESTQ_INGEST_PUSH", "1") == "0":
        return "push off"
    import ingest
    return ingest.publish(0)


BENCH_SHARD = "infrastructure/state/ledger/events/BENCH.jsonl"


def drop_as_bench(item, reason):
    """RUNNER may not `drop` (model.RUNNER_VERBS, enforced at replay), so the retirement is the steward's BENCH hat, the
    one its wake session already wears; `publish_bench` carries that shard, which no other tick step commits."""
    import ingest
    env = dict(os.environ, RIMFLOW_SEAT="BENCH", CLAUDE_PROJECT_DIR=ingest.REPO)
    r = subprocess.run([sys.executable, ingest.CLI, "drop", item, "--reason", reason, "--why",
                        "steward: the lane recovered by itself"], env=env, capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr).strip()


def publish_bench():
    if os.environ.get("TESTQ_INGEST_PUSH", "1") == "0":
        return "push off"
    import ingest
    return ingest.publish(0, shard_rel=BENCH_SHARD, message="ledger: steward retired a recovered incident")


def flush_bench():
    """A retirement whose publish failed is closed locally, so no later drop carries it, and a dirty shard can stop the
    tick's --ff-only pull: every pass retries while the shard has unpublished work."""
    if os.environ.get("TESTQ_INGEST_PUSH", "1") == "0":
        return
    import ingest
    if ingest.unpublished(BENCH_SHARD):
        jlog({"ts": iso(time.time()), "event": "retired_publish", "result": publish_bench()})


def failreport(ok, cause=None):
    """pulse failreport (`steve:lane` health row); the dispatch clone is sparse and has no Utils/pulse, so the same
    record is written inline there."""
    try:
        sys.path.insert(0, os.path.join(HERE, "..", "pulse"))
        import failreport as F
        return F.report(LANE_TASK, ok, cause=cause, seat="RUNNER")
    except ImportError:
        pass
    rec = {"ts": time.time(), "task": LANE_TASK, "status": "ok" if ok else "failed", "seat": "RUNNER"}
    if not ok and cause:
        rec["cause"] = " ".join(str(cause).split())[:200]
    d = os.environ.get("RM_PULSE_STATE") or os.path.expanduser("~/.local/state/rm-dashboard")
    try:
        os.makedirs(d, exist_ok=True)
        fd = os.open(os.path.join(d, "failures.jsonl"), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            os.write(fd, (json.dumps(rec) + "\n").encode())
        finally:
            os.close(fd)
        return True
    except OSError:
        return False


def tick_timer_state():
    """systemctl's word for testq-tick.timer (active, inactive, failed, ...), or None when it cannot be asked."""
    try:
        r = subprocess.run(["systemctl", "--user", "is-active", "testq-tick.timer"], capture_output=True, text=True,
                           timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    word = r.stdout.strip()
    return word if word in ("active", "inactive", "failed", "activating", "deactivating", "reloading") else None


def restart_tick():
    try:
        r = subprocess.run(["systemctl", "--user", "restart", "testq-tick.timer"], capture_output=True, text=True,
                           timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        return "failed: %s" % e
    return "exit %d %s" % (r.returncode, r.stderr.strip()[-160:])


WAKE_UNIT = "testq-steward-wake"
RUNBOOK = "infrastructure/stevedesktop/RUNBOOK.md"


def wake_active():
    try:
        r = subprocess.run(["systemctl", "--user", "is-active", WAKE_UNIT + ".service"], capture_output=True,
                           text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return True                     # cannot tell: do not start a second one
    return r.stdout.strip() in ("active", "activating", "reloading")


def launch_wake(clone, brief_path, log_path, budget, max_s):
    """Start the capped session in its own transient unit (it outlives this oneshot pass; systemd kills it at
    RuntimeMaxSec). -> (ok, text)."""
    exe = os.environ.get("TESTQ_WAKE_CLAUDE") or shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    cmd = "exec %s -p \"$(cat %s)\" --max-budget-usd %s%s > %s 2>&1" % (
        shlex.quote(exe), shlex.quote(brief_path), shlex.quote(str(budget)),
        (" --model " + shlex.quote(os.environ["TESTQ_WAKE_MODEL"])) if os.environ.get("TESTQ_WAKE_MODEL") else "",
        shlex.quote(log_path))
    try:
        r = subprocess.run(["systemd-run", "--user", "--unit", WAKE_UNIT, "--collect", "-p", "RuntimeMaxSec=%d" % max_s,
                            "-p", "WorkingDirectory=%s" % clone, "--setenv=RIMFLOW_SEAT=BENCH",
                            "--setenv=PATH=%s" % os.environ.get("PATH", ""), "/bin/bash", "-c", cmd],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        return False, "systemd-run failed: %s" % e
    return r.returncode == 0, (r.stdout + r.stderr).strip()[-200:]


def wake_clone_sees(clone, item):
    """True when CLONE's ledger shards hold the event that creates ITEM: what `claim` there will replay."""
    for shard in glob.glob(os.path.join(clone, "infrastructure", "state", "ledger", "events", "*.jsonl")):
        try:
            with open(shard, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if item not in line:
                        continue
                    try:
                        ev = json.loads(line)
                    except ValueError:
                        continue
                    if ev.get("name" if ev.get("event") == "spawn" else "id") == item \
                            and ev.get("event") in ("spawn", "file"):
                        return True
        except OSError:
            continue
    return False


def pull_wake_clone(clone):
    """Fast-forward only: a dirty or diverged clone refuses, and the hold below then tells the truth about it."""
    if os.environ.get("TESTQ_INGEST_PUSH", "1") == "0":
        return "pull off"
    try:
        r = subprocess.run(["git", "-C", clone, "pull", "-q", "--ff-only", "origin", "main"], capture_output=True,
                           text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return "pull failed: %s" % e
    return "pulled" if r.returncode == 0 else "pull failed: " + (r.stderr or r.stdout).strip()[-200:]


def safe_publish():
    """A publish that dies must not lose the pass: the rung is on the shard and ingest retries it."""
    try:
        return publish()
    except (OSError, subprocess.SubprocessError) as e:
        return "publish failed: %s" % e


def reach_wake_clone(clone, item):
    """Make ITEM visible in CLONE -> None, or why it still is not."""
    if wake_clone_sees(clone, item):
        return None
    pub = safe_publish()
    pull = pull_wake_clone(clone)
    return None if wake_clone_sees(clone, item) else "publish: %s; pull: %s" % (pub, pull)


def wake_brief(inc, ls, clone, unseen=None):
    item_line = "escalation item: %s  (claim it first: `python3 src/RimMandrake/rimflow/cli.py claim %s --seat BENCH`)" \
        % (inc.get("item"), inc.get("item"))
    if unseen:
        item_line = """escalation item: %s is NOT in this clone yet. It is written in %s's RUNNER shard and has not
  reached you (%s).
  Do not claim it and do not `rimflow file` it: a second filing of that id is refused at replay. A stuck publish is
  part of the fault, so look at that clone first. Once it has published, `git pull --ff-only` here and claim it.""" \
            % (inc.get("item"), T.REPO, unseen[:300])
    return """You are a BENCH session started by the SteveDesktop lane steward (testq steward.py), not by a person. The
owner allowed this by card on 2026-10-26: one capped session when a lane alert is unanswered for 30 min.

The lane has been in a fault for %d min with no seat on it.
  state: %s
  why:   %s
  %s

Read, in this order, and nothing large into context:
  %s            the steward's current state and incident
  %s           one line per state change and escalation
  %s                the dispatcher's log (tail it)
  %s   how SteveDesktop is reached and brought back

Your job: diagnose why the lane is not RUNNING and restore it with the existing tools (`testq.py resume --reason`
once a pause's cause is dealt with, the RUNBOOK's restart paths). Do not live-test anything, do not deploy, do not
touch the owner's game. Note what you found and did on the item; close it only if the lane is RUNNING again. If you
cannot fix it, say exactly what the owner must do on the item and stop. You have a hard spending and time cap.
""" % (inc["unowned_s"] // 60, inc["state"], ls["reason"][:300], item_line,
       path("steward.json"), path("steward.jsonl"), path("tick.log"), os.path.join(clone, RUNBOOK))


def maybe_wake(inc, ls, now, src="steward"):
    """The capped LLM wake, at most once per incident -> what happened (also kept in inc["wake"])."""
    if inc.get("wake") or inc["level"] < 2 or not inc.get("item"):
        return None
    if os.environ.get("TESTQ_STEWARD_WAKE", "1") == "0" or os.path.exists(path("wake.stop")):
        return None
    if claim_holds(inc["item"], now):
        return None
    last = T.read_json(path("wake.json")) or {}
    cool = int(os.environ.get("TESTQ_WAKE_COOLDOWN_S", "14400"))
    if last.get("epoch") and now - last["epoch"] < cool:
        inc["wake"] = "skipped: cooldown, the last wake was %s" % last.get("ts")
        return inc["wake"]
    if wake_active():
        inc["wake"] = "skipped: a wake session is already running"
        return inc["wake"]
    clone = os.path.expanduser(os.environ.get("TESTQ_WAKE_CLONE", "~/rm/bench"))
    if not os.path.exists(os.path.join(clone, ".git")):
        inc["wake"] = "skipped: no wake clone at %s" % clone
        return inc["wake"]
    unseen = reach_wake_clone(clone, inc["item"])
    if unseen:
        hold = int(os.environ.get("TESTQ_WAKE_HOLD_S", "600"))
        if "wake_held" not in inc:
            inc["wake_held"] = now
            jlog({"ts": iso(now), "event": "wake_held", "by": src, "item": inc["item"], "why": unseen})
        if now - inc["wake_held"] < hold:
            return None
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(now))
    os.makedirs(path("wake"), exist_ok=True)
    brief, logp = path("wake", stamp + ".brief.md"), path("wake", stamp + ".log")
    with open(brief, "w", encoding="utf-8") as f:
        f.write(wake_brief(inc, ls, clone, unseen))
    budget = os.environ.get("TESTQ_WAKE_BUDGET_USD", "5")
    max_s = int(os.environ.get("TESTQ_WAKE_MAX_S", "2700"))
    ok, out = launch_wake(clone, brief, logp, budget, max_s)
    if ok:
        S.dump({"ts": iso(now), "epoch": now, "item": inc["item"], "log": logp, "brief": brief}, path("wake.json"))
        rimflow("note", inc["item"], "--text", "%s: started one capped headless BENCH session (budget $%s, %d s cap); "
                "log %s" % (src, budget, max_s, logp))
    inc["wake"] = ("started %s, log %s" % (iso(now), logp)) if ok else "launch failed: " + out
    jlog({"ts": iso(now), "event": "wake", "by": src, "result": inc["wake"], "item": inc["item"]})
    return inc["wake"]


def world():
    """The replayed ledger (production: every shard; a selftest: RIMFLOW_LEDGER)."""
    if RIMFLOW_DIR not in sys.path:
        sys.path.insert(0, os.path.dirname(RIMFLOW_DIR))
    from rimflow import model
    model.EVENTS = os.environ.get("RIMFLOW_LEDGER") or model.EVENTS
    return model, model.replay(model.read())


# ---------------------------------------------------------------- the clock and the escalation ladder

def claim_holds(item_id, now, w=None):
    """True while a claim on ITEM pauses the clock: a live lease, or no lease and under 2 h since the claim."""
    if not item_id:
        return False
    model, wd = w or world()
    it = wd.items.get(item_id)
    if not it or not it.open or not it.claim_ts or it.owner in (None, "RUNNER"):
        return False
    ls = model.lease_status(it, now)
    if ls == "live":
        return True
    if ls is None:
        t = model.epoch(it.claim_ts)
        return t is not None and now < t + CLAIM_HOLD_S
    return False


def _window(it, model):
    """-> (start, end) epochs a claim on IT covers in its current state, or None: from the claim to the lease's own
    expiry (a released lease stops at its release stamp), or CLAIM_HOLD_S from a lease-less claim."""
    if not it or not it.open or not it.claim_ts or it.owner in (None, "RUNNER"):
        return None
    start = model.epoch(it.claim_ts)
    if start is None:
        return None
    ls = getattr(it, "lease", None)
    if ls:
        end = model.epoch(ls.get("expires"))
        if end is None:
            return None
        if ls.get("released"):
            rel = model.epoch(ls.get("released"))
            end = min(end, rel) if rel is not None else end
    else:
        end = start + CLAIM_HOLD_S
    return start, end


def claim_cover(item_id, a, b, w=None):
    """Seconds of [A, B] that a claim on ITEM covered, from the ledger's own history: the item's state after each
    event holds until the next event, so a later close, release or reclaim cannot erase cover already earned.
    W (model, world) -> judge the current state only (a test double)."""
    if not item_id or b <= a:
        return 0
    if w:
        win = _window(w[1].items.get(item_id), w[0])
        return int(max(0, min(b, win[1]) - max(a, win[0]))) if win else 0
    if RIMFLOW_DIR not in sys.path:
        sys.path.insert(0, os.path.dirname(RIMFLOW_DIR))
    from rimflow import model
    model.EVENTS = os.environ.get("RIMFLOW_LEDGER") or model.EVENTS
    segs = []                                   # (event ts, claim window after that event)

    def observe(ev, world, ok):
        t = model.epoch(ev.get("ts"))
        if t is not None:
            segs.append((t, _window(world.items.get(item_id), model)))

    model.replay(model.read(), observe=observe)
    total = 0
    for k, (t, win) in enumerate(segs):
        if win is None:
            continue
        t_next = segs[k + 1][0] if k + 1 < len(segs) else float("inf")
        lo, hi = max(a, t, win[0]), min(b, t_next, win[1])
        if hi > lo:
            total += hi - lo
    return int(total)


def lock_open():
    """The one lock around every state-changing pass (steward and watcher): -> an open file, or None if the other
    pass still holds it after LOCK_WAIT_S."""
    f = open(path("steward.lock"), "a")
    t0 = time.time()
    while True:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return f
        except OSError:
            if time.time() - t0 >= LOCK_WAIT_S:
                f.close()
                return None
            time.sleep(0.1)


def open_lane_item(w):
    """An open escalation item of ours whose name says so: survives a lost steward.json (spawn landed, dump did not)."""
    for k, it in sorted(w[1].items.items()):
        if k.startswith("STEVE_LANE_UNSTICK_") and "_UNOWNED_" in k and it.open:
            return k
    return None


def item_open(item_id, w):
    it = w[1].items.get(item_id) if item_id else None
    return bool(it and it.open)


def mint(w, tag, who):
    model, wd = w
    known = set(wd.items)
    for _ in range(20):
        name = "STEVE_LANE_UNSTICK_%s_%s_%s" % (tag, who, secrets.token_hex(2).upper())
        if not model.mint_problems(name, known):
            return name
    raise RuntimeError("no mintable escalation name for %s/%s" % (tag, who))


def retire(items, why, now):
    """Drop what a recovered incident spawned -> the items still to retire. It was a stall that ended, no work was
    done, so no commit proves it: an open one holds ops_watch steve.incident_unclaimed_min high for hours (FCE8, D070,
    STEWARD_FIX_LEAVES_THE_LIGHTS_ON). An item a seat holds is left to that seat; a refused drop is retried next pass."""
    left = []
    for item in items:
        w = world()
        if not item_open(item, w):
            continue
        if claim_holds(item, now, w):
            left.append(item)
            continue
        rc, out = drop_as_bench(item, why)
        if rc == 0:
            jlog({"ts": iso(now), "event": "retired", "item": item, "publish": publish_bench()})
        else:
            left.append(item)
            jlog({"ts": iso(now), "event": "retire_failed", "item": item, "error": out[-200:]})
    return left


def jlog(rec):
    with open(path("steward.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def escalate(inc, ls, now, last_item, src="steward"):
    """Advance INC up the ladder by its unowned clock. -> the item the incident escalated (or None). Each rung is
    recorded in the incident only once its ledger write succeeded, so a refused write is retried next pass."""
    u = inc["unowned_s"]
    if inc["level"] >= 3 or u < L1_S:
        return None
    w = world()
    tag = TAG.get(inc["state"], "STALLED")
    what = "%s: %s%s" % (inc["state"], ls["reason"][:200], (" (jobs %s)" % ",".join(map(str, ls["jobs"])))
                         if ls.get("jobs") else "")
    if 1 <= inc["level"] < 3 and not item_open(inc.get("item"), w):
        inc.update(level=0, item=None)              # closed under a continuing fault: open (or reuse) another
    if inc["level"] < 1:
        if not item_open(last_item, w):
            last_item = open_lane_item(w)
        if item_open(last_item, w):
            rc, out = rimflow("note", last_item, "--text", "%s: SteveDesktop lane %s again since %s, %d min unowned"
                              % (src, what, inc["since"], u // 60))
            item = last_item
        else:
            item = mint(w, tag, "UNOWNED")
            rc, out = rimflow("spawn", "--from", STEWARD_ITEM, "--for", "BENCH", "--needs", "offline", "--name", item,
                              "--title", ("SteveDesktop lane %s, unowned %d min: %s" % (inc["state"], u // 60,
                                                                                        ls["reason"]))[:160])
        if rc != 0:
            inc["error"] = out[-200:]
            return None
        inc.update(level=1, item=item, error=None)
        failreport(False, "%s: %s" % (inc["state"], ls["reason"][:160]))
        jlog({"ts": iso(now), "event": "escalate", "level": 1, "item": item, "state": inc["state"], "by": src})
    if inc["level"] < 2 and u >= L2_S:
        rc, out = rimflow("raise", inc["item"], "--reason", "%s: lane unowned %d min (%s)" % (src, u // 60,
                                                                                               inc["state"]))
        if rc != 0:
            inc["error"] = out[-200:]
            if not item_open(inc["item"], world()):     # closed under us: the next pass opens (or reuses) one
                inc.update(level=0, item=None)
                return None
            return inc["item"]
        inc.update(level=2, error=None)
        jlog({"ts": iso(now), "event": "escalate", "level": 2, "item": inc["item"], "by": src})
    if inc["level"] < 3 and u >= L3_S and not claim_holds(inc["item"], now, w):
        down = inc["state"] == "UNREACHABLE"
        name = mint(w, tag, "OWNER")
        rc, out = rimflow("spawn", "--from", STEWARD_ITEM, "--for", "OWNER", "--needs", "owner", "--name", name,
                          "--title", ("%sSteveDesktop lane %s %d min, no seat on %s: %s"
                                      % ("IN PERSON: " if down else "", inc["state"], u // 60, inc["item"],
                                         ls["reason"]))[:160])
        if rc != 0:
            inc["error"] = out[-200:]
            return inc["item"]
        inc.update(level=3, owner_item=name, error=None)
        jlog({"ts": iso(now), "event": "escalate", "level": 3, "item": name, "by": src})
    return inc["item"]


def steward_pass(now=None, mods=None):
    """One pass -> the steward.json record it wrote (None if another pass held the lock)."""
    T.ensure_dirs()
    lk = lock_open()
    if lk is None:
        return None
    try:
        return _steward_pass(now, mods)
    finally:
        lk.close()


def _steward_pass(now, mods):
    now = time.time() if now is None else now
    prev = T.read_json(path("steward.json")) or {}
    ls = lane_state(now, mods)
    fault = ls["fault_at"] is not None and now >= ls["fault_at"]
    inc, last_item = prev.get("incident"), prev.get("last_item")
    dt = max(0.0, now - prev["epoch"]) if prev.get("epoch") else 0.0
    to_retire = list(prev.get("to_retire") or [])
    if ls["state"] == "RUNNING":
        if inc:
            failreport(True)
            if inc.get("item"):
                rimflow("note", inc["item"], "--text", "steward: SteveDesktop lane RUNNING again (%s) after %s, "
                        "%d min unowned" % (ls["reason"][:120], inc["state"], inc["unowned_s"] // 60))
            jlog({"ts": iso(now), "event": "recovered", "incident": inc})
            to_retire += [i for i in (inc.get("item"), inc.get("owner_item")) if i and i not in to_retire]
            inc = None
        to_retire = retire(to_retire, "steward: SteveDesktop lane RUNNING again (%s)" % ls["reason"][:120], now)
    elif fault:
        if not inc:
            inc = {"state": ls["state"], "since": iso(now), "unowned_s": 0, "level": 0, "item": None,
                   "owner_item": None}
            dt = 0.0
        inc["state"] = ls["state"]
        if prev.get("fault"):
            inc["unowned_s"] = int(inc["unowned_s"] + dt - claim_cover(inc.get("item"), now - dt, now))
        if ls["at_once"]:
            inc["unowned_s"] = max(inc["unowned_s"], L1_S)
        rung = (inc["level"], inc.get("item"), inc.get("owner_item"))
        item = escalate(inc, ls, now, last_item)
        last_item = item or last_item
        if (inc["level"], inc.get("item"), inc.get("owner_item")) != rung:
            jlog({"ts": iso(now), "event": "rung_publish", "item": inc.get("item"), "result": safe_publish()})
        maybe_wake(inc, ls, now)
    rec = {"ts": iso(now), "epoch": now, "state": ls["state"], "fault": fault, "reason": ls["reason"],
           "jobs": ls["jobs"], "incident": inc, "last_item": last_item, "to_retire": to_retire,
           "since": prev.get("since") if prev.get("state") == ls["state"] and prev.get("fault") == fault else iso(now)}
    if rec["since"] == iso(now) and (prev.get("state"), prev.get("fault")) != (ls["state"], fault):
        jlog({"ts": iso(now), "event": "state", "state": ls["state"], "fault": fault, "reason": ls["reason"],
              "from": prev.get("state")})
    S.dump(rec, path("steward.json"))
    return rec


# ---------------------------------------------------------------- the heartbeat watcher

def watch_pass(now=None):
    """steward.json older than STALE_S -> STALE_HEARTBEAT: restart the tick timer once, then escalate on the
    stale age (the steward's own ladder cannot run while it is the thing that stopped). None if locked out."""
    T.ensure_dirs()
    lk = lock_open()
    if lk is None:
        return None
    try:
        return _watch_pass(now)
    finally:
        lk.close()


def _watch_pass(now):
    now = time.time() if now is None else now
    wst = T.read_json(path("steward_watch.json")) or {"first_seen": now}
    sj = T.read_json(path("steward.json"))
    seen = sj["epoch"] if sj and sj.get("epoch") else wst.get("first_seen", now)
    age = now - seen
    inc = wst.get("incident")
    if age <= STALE_S:
        if inc:
            if not (sj or {}).get("incident"):      # the steward's own incident keeps the shared row failed
                failreport(True)
            if inc.get("item"):
                rimflow("note", inc["item"], "--text", "steward-watch: the steward is writing again (stale %d min)"
                        % (inc["unowned_s"] // 60))
                publish()
            wst["to_retire"] = (wst.get("to_retire") or []) + [i for i in (inc.get("item"), inc.get("owner_item")) if i]
            jlog({"ts": iso(now), "event": "recovered", "by": "watch", "incident": inc})
        wst["incident"] = None
    else:
        reason = "steward.json not written for %d s (the tick or the steward stopped)" % age
        if not inc:
            inc = {"state": "STALE_HEARTBEAT", "since": iso(now), "unowned_s": 0, "level": 0, "item": None,
                   "owner_item": None, "restarted": None}
            jlog({"ts": iso(now), "event": "state", "state": "STALE_HEARTBEAT", "fault": True, "reason": reason,
                  "by": "watch"})
        prev_t = wst.get("epoch") or now
        inc["covered_s"] = inc.get("covered_s", 0) + claim_cover(inc.get("item"), prev_t, now)
        inc["unowned_s"] = int(age - inc["covered_s"])
        if not inc.get("restarted"):
            inc["restarted"] = "%s %s" % (iso(now), restart_tick())
            jlog({"ts": iso(now), "event": "restart", "by": "watch", "result": inc["restarted"]})
        else:
            lvl = inc["level"]
            ls = {"reason": reason + "; restarting testq-tick.timer did not bring it back", "jobs": []}
            escalate(inc, ls, now, (sj or {}).get("last_item"), src="steward-watch")
            if inc["level"] != lvl:
                safe_publish()
            maybe_wake(inc, ls, now, src="steward-watch")
        wst["incident"] = inc
    wst["to_retire"] = retire(wst.get("to_retire") or [], "steward-watch: the steward is writing again", now)
    flush_bench()       # the watch has its own timer, so this retry outlives a stopped tick
    wst.update(ts=iso(now), epoch=now, age_s=int(age))
    S.dump(wst, path("steward_watch.json"))
    return wst


def cmd_steward(_a):
    rec = steward_pass()
    if rec is None:
        print("steward: another pass holds the lock; skipped")
        return 0
    inc = rec.get("incident") or {}
    print("steward: %s%s: %s%s" % (rec["state"], " (fault)" if rec["fault"] else "", rec["reason"][:160],
                                   "; incident since %s, %d min unowned, level %d%s" % (
                                       inc["since"], inc["unowned_s"] // 60, inc["level"],
                                       ", " + inc["item"] if inc.get("item") else "") if inc else ""))
    return 0


def cmd_watch(_a):
    w = watch_pass()
    if w is None:
        print("steward-watch: another pass holds the lock; skipped")
        return 0
    inc = w.get("incident")
    print("steward-watch: steward.json age %d s%s" % (w["age_s"], "; STALE, level %d" % inc["level"] if inc else ""))
    return 0


if __name__ == "__main__":
    sys.exit(cmd_watch(None) if sys.argv[1:] == ["watch"] else cmd_steward(None))
