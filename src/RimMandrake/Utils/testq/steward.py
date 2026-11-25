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
  RUNNING          a SteveDesktop job is running: not a fault, and NOT recovery (an open incident's clock runs on)
  PAUSED           paused.json: an auto pause (it names an outcome) is a fault at once; a manual pause with an `until`
                   in the future is intentional; any other manual pause (or QHOME/fill.stop with no `until: <ISO>` line, aged by its mtime) turns
                   into a fault 60 min after it began
  READY            a job is ready but not admitted: a fault once it has waited 5 min (a not-ours busy worker, a
                   dispatcher that stopped admitting)
  BRAKED           fill_plan's brake (two filler jobs in a row not DONE): a fault, at once when either failure is a
                   HARNESS-class cause (HARNESS, DEPLOY, SYNC, SOURCE_SHA_MISSING, BLOCKED_SELECTION) with the job ids;
                   when both jobs have a recorded non-fault cause and Operations has not spent its canary on them
                   (brake_release.py), a fault only RELEASE_GRACE_S after the later one finished;
                   the day's lane-time budget or job cap is a brake too but NOT a fault: it expires at local midnight,
                   and it ends an incident (the lane stands idle on purpose, every check above it passed)
  IDLE_EMPTY       nothing queued and the fill found nothing selectable (no history, every chain DRY), or it would
                   queue chains yet nothing is pending (the fill itself failed): an evidence gap, a fault
  SWITCHED         SteveDesktop is on pipeline work only (rimflow/host_work_switch.py, fill_plan verdict "switched"):
                   the owner's order, never a fault and never aged; a fill.stop beside it is not read
  EXHAUSTED        the fill's gap scan found nothing to do at all (fill_plan verdict "exhausted"): not a fault,
                   and it ends an incident
  TICK_STOPPED     (after RUNNING and PAUSED: a job running or an intentional pause is not a fault) testq-tick.timer is not active on this machine (stopped by hand or by another seat): nothing is
                   dispatched, filled, reconciled or ingested; a fault at once (it outranks READY and IDLE_EMPTY,
                   whose "the fill failed?" was the misdiagnosis of 2026-10-28, when a cutover stopped every
                   rm-*/testq-* timer at 05:04 and nobody restarted them). An unknown state (no systemd) says nothing.
  STALE_HEARTBEAT  the watcher's: steward.json not written for 5 min

The unowned clock (section 6.1) adds the time between two passes while the state is a fault, or RUNNING inside an open
incident. Only proof ends an incident (STEWARD_FIX_ENDS_ON_GREEN_NOT_RUNNING, T4 of
design/RimMandrake/dispatcher_risk_response_2026-10-29.md): a stevedesktop job that came back DONE with its canary on,
finishing after the incident began (testq.lane_proven_after, the filler brake's own predicate). RUNNING is not proof
(R02 there): a resumed lane on a dead game ran INVALID/CANARY again and again while each RUNNING closed the incident. Any
other non-fault state (the day brake, EXHAUSTED, an intentional pause, a young READY) freezes the unowned clock and
leaves the incident open. The impact clock (incident impact_s, now minus since) never pauses. Without a proof a
reboot after a settled lane resumes the old unowned clock; with one it starts fresh (2DEB: a one-minute reboot read
"unowned 70 min" across a lane that had since proven itself). A claim on the escalation item pauses the unowned clock
while the claim's lease is live, or for 2 h after a claim with no lease; a lapsed or released lease does not, and one
incident pauses for at most CLAIM_HOLD_S (2 h) in all (incident claim_paused_s): a renewed lease is not a fix.

Escalation (section 6.4), each at most once per incident:
  T+10 min   spawn a cause-keyed STEVE_LANE_UNSTICK item --for ALARM_SEAT (BENCH, the Conductor seat, which
             works its raised items) --needs offline (from the steward's own item), naming the state and job ids, or note
             the still-open item of this cause; refused, with the reason on the incident,
             when rimflow incident.receiver_problem says nobody would pick it up (T2, ALARMS_REWIRE_OFF_RETIRED_BENCH);
             a failed `steve:lane` record lights the pulse health row
  T+30 min   `rimflow raise` it: first in `rimflow next --seat BENCH`, a line in the phone brief
  T+120 min  with no claim: tell Operations, never him (STEWARD_RUNG_FIX_ASKS_THE_WRONG_GROWNUP: unsticking a lane is no
             delegation_policy s2 call, and its OWNER needs=owner item went back to agents): one told row, metric
             STEVE_RUNG_KIND, routed by alarm_routes.json steve.* to an Operations incident whose chain climbs to the
             Conductor; it names the drainable item, which stays open, and says "IN PERSON:" when SteveDesktop is
             unreachable. No new item. (An older incident's incident.owner_item is only retired.)
Recovery (a DONE+canary job after the incident began) records `steve:lane` ok, notes the item and waits on its cause.

The LLM wake (the owner's card ruling 2026-10-26 12:27 PDT, "Yes, after 30 min", on STEVE_STEWARD_BUILD_NO_LLM_OWNER):
once an incident has been raised (T+30) and no claim holds its item, the steward MAY start ONE headless Claude session
to diagnose and restart the lane. ON by default, with these guards:
  one at a time   a fixed transient unit (systemd-run --user --unit testq-steward-wake); an active one blocks another
  hard caps       spend_watchdog --cap-usd TESTQ_WAKE_BUDGET_USD (5), from outside the agent (never --max-budget-usd:
                  the agent is not told its spend, owner 2026-11-16) and RuntimeMaxSec TESTQ_WAKE_MAX_S (2700 s)
  no loop         one wake per incident (one that died of no fault of its own is tried again), and TESTQ_WAKE_COOLDOWN_S (4 h) between any two (QHOME/wake.json)
  login           held while `claude auth status` says the login is gone; a wake that dies on auth anyway gives its
                  cooldown back and goes again, at most TESTQ_WAKE_RETRIES (2) times (OPS_ALARM_RETRY_AFTER_AUTH_DEATH:
                  10-30 08:58Z died in seconds, was reported started, and a braked lane sat 14 h)
  told            `started` means systemd took it. settle_wake reads the ended run (log, <log>.exit) once; a death goes
                  on the item, steward.jsonl, the incident and the Conductor log
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
os.environ.setdefault("RIMFLOW_MACHINE_MINT", "1")  # machine minter: fixed alarm prefixes, see rimflow/model.py mint_problems
import re
import secrets
import shlex
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.append(os.path.join(HERE, "..", "..", "rimflow"))
import failure_class as FC  # noqa: E402
import schema as S  # noqa: E402
import testq as T  # noqa: E402
import brake_release as BR  # noqa: E402
import lane_ticket as LT  # noqa: E402

RIMFLOW_DIR = os.path.join(T.REPO, "src", "RimMandrake", "rimflow")
STEWARD_ITEM = os.environ.get("TESTQ_STEWARD_ITEM", "STEVE_STEWARD_BUILD_NO_LLM_OWNER")
L1_S, L2_S, L3_S = 600, 1800, 7200          # section 6.4: T+10, T+30, T+120 min of unowned clock
# budget: danger=a ready lane that nobody works goes unseen; ends no work: the steward's clock starts
READY_GRACE_S = 300
MANUAL_PAUSE_S = 3600                       # section 6.1: "a pause with neither escalates at 60 min"
# budget: danger=a claim with no lease holds the escalation for ever; ends no work: the steward's clock runs again
CLAIM_HOLD_S = 7200                         # a claim without a lease pauses the clock this long
# budget: danger=two passes wait on each other; ends no work: the pass is skipped; the next timer beat runs it
LOCK_WAIT_S = 30                            # a pass waits this long for the other pass, then skips
# budget: danger=a dead steward goes unseen; ends no work: the watcher says that the steward is stale
STALE_S = 300                               # the watcher: steward.json older than this
LEDGER_ERR = "ledger unreadable: "          # inc["error"] prefix; ops_watch counts it as nobody escalating
HARNESS_CAUSES = {"HARNESS", "DEPLOY", "SYNC", "SOURCE_SHA_MISSING", "BLOCKED_SELECTION"}
TAG = {"UNREACHABLE": "OFFLINE", "QUARANTINE": "QUARANTINE", "PAUSED": "PAUSED", "READY": "STALLED",
       "BRAKED": "BRAKED", "IDLE_EMPTY": "IDLE", "STALE_HEARTBEAT": "STALLED", "TICK_STOPPED": "STALLED"}
LANE_TASK = "steve:lane"


def path(*parts):
    return T.q(*parts)


def iso(epoch):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def mods_default():
    import coverage     # the filler's own list: TESTQ_FILL_MODS, else wired_mods.json (TESTQ_MODS_WIRE_BEYOND_FLOWWORKS)
    return coverage.fill_mods()


# ---------------------------------------------------------------- what state the lane is in

UNIT_PAUSE_S = 24 * 3600     # a pause that waits for a unit is told of after a day (a 49 h pause stood unseen, 2026-11-15)
# budget: danger=a hold that outlasts a build and a push goes unseen; ends no work: the steward's clock starts
COMPANION_GRACE_S = 900     # a hold outlasting a build and a push, and more than one retry of a blip, is a fault


def fill_stop_until(p):
    """-> the epoch of a `until: <ISO time>` line in a hand-written fill.stop, or None. A deliberate filler stop (an
    owner's order for the day) named no end, so it always aged into a fault 60 min after its mtime and paged a seat
    (STEVE_LANE_UNSTICK_PAUSED_UNOWNED_PAUSED_ARJYIP, 2026-11-24). A torn or missing line keeps that 60 min ageing."""
    try:
        with open(p) as f:
            for line in f:
                k, _, v = line.partition(":")
                if k.strip().lower() == "until" and v.strip():
                    return int(S.parse_ts(v.strip()))
    except (OSError, TypeError, ValueError):
        return None
    return None


def _switched():
    """-> the host work switch's text for SteveDesktop, or None (testq/pipeline_admit.steve_switched)."""
    import pipeline_admit as PA
    return PA.steve_switched() if T.switch_applies() else None


def _st(state, reason, fault_at=None, at_once=False, jobs=(), settled=False):
    """fault_at: the epoch from which the state is a fault (0: already; None: never). settled: the lane is working as
    intended, so this state ends an incident."""
    return {"state": state, "reason": reason, "fault_at": fault_at, "at_once": at_once, "jobs": list(jobs),
            "settled": settled}


def lane_state(now, mods=None):
    ss = T.read_json(path("ssh_state.json")) or {}
    if ss.get("down_since"):
        # a live manual pause (an owner's hardware work) outranks the box going dark until the pause expires: its
        # `until`, or for a pause with none the 60 min after which the PAUSED state below would escalate it anyway
        # (STEVE_STEWARD_FIX_PLANNED_OUTAGE_CRIED_WOLF). An auto pause (it names an outcome) covers nothing.
        pz = T.paused() or {}
        held = None
        if pz and not pz.get("outcome"):
            try:
                held = (S.parse_ts(pz["until"]) if pz.get("until") else
                        S.parse_ts(pz["since"]) + MANUAL_PAUSE_S if pz.get("since") else None)
            except (TypeError, ValueError):     # a torn pause covers nothing: the outage is a fault
                held = None
        return _st("UNREACHABLE", "ssh to SteveDesktop down since %s: %s%s" % (
            ss["down_since"], (ss.get("last_error") or "")[:120],
            "; inside the pause until %s" % iso(held) if held and held > now else ""),
            held if held and held > now else 0)
    if os.path.exists(path("quarantine.json")):
        qz = T.read_json(path("quarantine.json")) or {}
        return _st("QUARANTINE", "quarantined: %s" % (qz.get("reason") or "quarantine.json exists"), 0, at_once=True)
    run = T.steve_running()
    if run:
        return _st("RUNNING", "running %s" % ",".join(r["job"]["id"] for r in run), jobs=[r["job"]["id"] for r in run],
                   settled=True)
    pz = T.paused()
    if pz:
        since = S.parse_ts(pz["since"]) if pz.get("since") else now
        why = pz.get("reason") or pz.get("note") or ""
        if pz.get("outcome"):
            return _st("PAUSED", "auto pause by %s %s/%s: %s" % (pz.get("job"), pz.get("outcome"), pz.get("cause"),
                                                                 why[:120]), 0, jobs=[pz["job"]] if pz.get("job") else [])
        if pz.get("until_unit"):
            return _st("PAUSED", "paused until unit %s is over: %s" % (pz["until_unit"], why[:120]), since + UNIT_PAUSE_S)
        if pz.get("until"):
            until = S.parse_ts(pz["until"])
            return _st("PAUSED", "paused until %s: %s" % (pz["until"], why[:120]), until)
        return _st("PAUSED", "paused since %s with no expiry: %s" % (pz.get("since"), why[:120]),
                   since + MANUAL_PAUSE_S)
    if not T.steve_lanes():     # every live game is stopped after two equal endings (lane_stop.py): it retries by itself
        stops = [x for x in (T.LS.stopped(T, h) for h in T.STEVE_HOSTS) if x]
        return _st("PAUSED", "; ".join("stopped until %s after equal endings: %s" % (x["until"], x["signature"][:100])
                                       for x in stops),
                   min(S.parse_ts(x["first"]) for x in stops) + T.LS.ESCALATE_S)
    sw = _switched()
    if os.path.exists(path("fill.stop")) and not sw:   # under the host switch a fill.stop adds nothing, and never ages
        until = fill_stop_until(path("fill.stop"))
        if until is not None:
            return _st("PAUSED", "fill stopped until %s: %s exists" % (iso(until), path("fill.stop")), until)
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
    with T.done_once():
        plans = {m: T.fill_plan(m, int(os.environ.get("TESTQ_FILL_CHAINS", "4")),
                            int(os.environ.get("TESTQ_FILL_CAP") or T.FILL_CAP_DEFAULT), now=now)
             for m in mods or mods_default()}
    by = {}
    for m, p in plans.items():
        by.setdefault(p["verdict"], []).append(m)
    if "switched" in by:    # the owner's order on the machine (rimflow/host_work_switch.py): intended, never a fault
        return _st("SWITCHED", plans[by["switched"][0]]["text"][:240], None, settled=True)
    if "brake" in by:
        tails = [t for m in by["brake"] for t in plans[m].get("tail") or [] if t]
        jobs = [t["job"]["id"] if isinstance(t.get("job"), dict) else t.get("job") for t in tails]
        res = [t.get("result") or {} for t in tails]
        causes = ["%s/%s" % (r.get("outcome"), r.get("cause")) for r in res]
        harness = any(r.get("cause") in HARNESS_CAUSES for r in res)
        if BR.releasable(tails, now):
            due = max(S.parse_ts(t.get("finished") or (t.get("result") or {}).get("finished")) for t in tails)
            return _st("BRAKED", "filler brake on %s on recorded non-fault causes (%s: %s): Operations' canary releases "
                       "it" % (",".join(by["brake"]), ",".join(str(j) for j in jobs), ", ".join(causes)),
                       due + BR.RELEASE_GRACE_S, jobs=jobs)
        return _st("BRAKED", "filler brake on %s: last two filler jobs not DONE (%s: %s)%s"
                   % (",".join(by["brake"]), ",".join(str(j) for j in jobs), ", ".join(causes),
                      "; HARNESS-class, escalated at once" if harness else ""), 0, at_once=harness, jobs=jobs)
    if "pick" in by:
        return _st("IDLE_EMPTY", "fill would queue %s but nothing is pending (the fill failed?)"
                   % "; ".join("%s: %s" % (m, ",".join(plans[m]["pick"])) for m in by["pick"]), 0)
    if "companion" in by:   # the stager is failing or behind: the filler holds rather than die at deploy
        m = by["companion"][0]
        return _st("IDLE_EMPTY", "filler held: " + plans[m]["text"][:200], plans[m]["since"] + COMPANION_GRACE_S)
    if "facts" in by:       # what the host lacks, or facts too old to say: the filler holds rather than die on the load
        return _st("IDLE_EMPTY", "filler held: " + "; ".join(plans[m]["text"][:160] for m in by["facts"]), 0)
    gaps = [m for v in ("nohist", "dry") for m in by.get(v, [])]
    if gaps:
        return _st("IDLE_EMPTY", "nothing selectable: " + "; ".join(plans[m]["text"][:160] for m in gaps), 0)
    capped = by.get("cap", [])     # the job backstop; no lane-time budget (FILL_NO_DANGERLESS_DAY_BUDGET)
    if capped:
        return _st("BRAKED", "day brake: " + plans[capped[0]]["text"][:200], settled=True)
    if "exhausted" in by:
        return _st("EXHAUSTED", "the gap scan found nothing to fill: " + plans[by["exhausted"][0]]["text"][:200],
                   settled=True)
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
# the L1 item's seat: the Conductor seat (alarm_routes.json drainers, RIMMANDRAKE_NAME_RECEIVER_FOR_SEAT_ALARMS_PENDING_WITH_NONE); the T2 check
# (rimflow incident.receiver_problem) refuses the spawn if no program would pick it up
ALARM_SEAT = "BENCH"
# the T+120 rung's told-ledger metric: alarm_routes.json steve.* sends it to Operations (alarm_census reads it here)
STEVE_RUNG_KIND = "steve.lane_unowned_rung"


def _incident_mod():
    """rimflow incident.py of this tree (ingest.REPO), loaded by path: the steward runs outside the rimflow dir."""
    import importlib.util
    import ingest
    spec = importlib.util.spec_from_file_location(
        "steward_incident", os.path.join(ingest.REPO, "src/RimMandrake/rimflow/incident.py"))
    inc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inc)
    return inc


def tell_operations(why, item, now):
    """The T+120 rung: one told row for Operations' incident ladder (incident.step folds it; its `item` rides along).
    Raises on a write it could not make, so the caller retries next pass."""
    IN = _incident_mod()
    IN.append([{"metric": STEVE_RUNG_KIND, "kind": STEVE_RUNG_KIND, "why": str(why)[:300], "told_at": iso(now),
                "item": item, "class": (IN.route_of(IN.load_table(), STEVE_RUNG_KIND) or {}).get("class")}])


def nobody_for(seat, needs):
    """-> why nobody would pick up an item filed --for seat --needs needs, or None (incident.receiver_problem in this
    tree). A tree that cannot answer is reported as a problem, so an alarm is never filed blind."""
    try:
        return _incident_mod().receiver_problem(seat, needs)
    except Exception as e:     # noqa: BLE001
        return "receiver check failed: %s: %s" % (type(e).__name__, e)


def bench(*args):
    """The steward's BENCH hat writes cause waits and legacy retirements."""
    import ingest
    env = dict(os.environ, RIMFLOW_SEAT="BENCH", CLAUDE_PROJECT_DIR=ingest.REPO)
    try:
        r = subprocess.run([sys.executable, ingest.CLI, *args], env=env, capture_output=True, text=True, timeout=300)  # budget: class=rimflow
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, "could not run rimflow %s: %s" % (args[0], e)
    return r.returncode, (r.stdout + r.stderr).strip()


def drop_as_bench(item, reason):
    return bench("drop", item, "--reason", reason, "--why", "steward: the lane recovered by itself")


def publish_bench():
    if os.environ.get("TESTQ_INGEST_PUSH", "1") == "0":
        return "push off"
    import ingest
    return ingest.publish(0, shard_rel=BENCH_SHARD, message="ledger: steward updated a recovered incident")


def flush_bench():
    """A retirement or wait whose publish failed is recorded locally, and a dirty shard can stop the
    tick's --ff-only pull: every pass retries while the shard has unpublished work."""
    if os.environ.get("TESTQ_INGEST_PUSH", "1") == "0":
        return
    import ingest
    if ingest.unpublished(BENCH_SHARD):
        jlog({"ts": iso(time.time()), "event": "retired_publish", "result": publish_bench()})


def failreport(ok, cause=None):
    """The `steve:lane` health row, one line in failures.jsonl (the record RimPulse's failreport wrote; written
    inline since failreport went with the dashboard, 2026-11-18). Nothing reads the file since the dashboard's daemon."""
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


NOT_RUNNING = 0      # tick_run_start(): systemd says no tick runs now
# A running tick older than this is treated as stopped. It equals testq-tick.service's TimeoutStartSec, which kills it then.
TICK_HUNG_S = 14400  # budget: danger=a hung tick that never writes steward.json; evidence=2026-11-12 tick ran 23 min; longest=1386.2s (user journal, 14 days to 2026-11-24)


def tick_run_start():
    """-> the epoch the running testq-tick.service started, NOT_RUNNING when none runs, None when systemd cannot be asked.
    steward.json is written once per tick, after the fill loop, so a tick that runs past STALE_S is not a stopped steward."""
    try:
        r = subprocess.run(["systemctl", "--user", "show", "testq-tick.service", "-p", "ActiveState",
                            "-p", "InactiveExitTimestamp", "--timestamp=unix"], capture_output=True, text=True,
                           timeout=1800)   # budget: class=call
    except (OSError, subprocess.SubprocessError):
        return None
    f = dict(ln.split("=", 1) for ln in r.stdout.splitlines() if "=" in ln)
    if r.returncode or "ActiveState" not in f:
        return None
    if f["ActiveState"] not in ("activating", "active", "reloading"):
        return NOT_RUNNING
    try:
        return float(f.get("InactiveExitTimestamp", "").lstrip("@"))
    except ValueError:
        return None


def restart_tick():
    try:
        r = subprocess.run(["systemctl", "--user", "restart", "testq-tick.timer"], capture_output=True, text=True,
                           timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        return "failed: %s" % e
    return "exit %d %s" % (r.returncode, r.stderr.strip()[-160:])


WAKE_UNIT = "testq-steward-wake"
WAKE_AUTH_TEXT_MAX = 400        # an auth death's log IS the short API error; a long log merely quotes one
WAKE_AUTH_RX = re.compile(r"failed to authenticate|oauth session expired|login expired|please run /login|"
                          r"authentication_failed|not logged in", re.I)
RUNBOOK = "infrastructure/stevedesktop/RUNBOOK.md"


def wake_active():
    try:
        r = subprocess.run(["systemctl", "--user", "is-active", WAKE_UNIT + ".service"], capture_output=True,
                           text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return True                     # cannot tell: do not start a second one
    return r.stdout.strip() in ("active", "activating", "reloading")


def exit_path(log_path):
    return log_path + ".exit"


def wake_login():
    """`claude auth status`, the Dispatcher's own probe -> (True | False | None, why); None = no reading, which holds
    nothing (login_watch alarms a blind probe)."""
    exe = os.environ.get("TESTQ_WAKE_CLAUDE") or shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    if RIMFLOW_DIR not in sys.path:
        sys.path.insert(0, RIMFLOW_DIR)
    try:
        import login_watch
        return login_watch.probe(exe)
    except Exception as e:  # noqa: BLE001 - a broken probe must not stop a wake
        return None, "probe raised %s" % type(e).__name__


def wake_outcome(rec):
    """-> (ok | auth | died, text) for a finished wake. A negative exit code records a signal. Otherwise a short log
    naming the login is an auth death: that is all 20261030T085851Z.log held. No exit file: systemd killed it at its cap."""
    try:
        with open(rec["exit"], encoding="utf-8") as f:
            code = f.read().strip()
    except OSError:
        code = None
    try:
        with open(rec["log"], encoding="utf-8", errors="replace") as f:
            log = f.read()
    except OSError:
        log = ""
    tail = " ".join(log[-200:].split())
    if code and code.startswith("-") and code[1:].isdigit():
        return "died", "signal %s: %s" % (code[1:], tail or "empty log")
    if len(log) <= WAKE_AUTH_TEXT_MAX and WAKE_AUTH_RX.search(log):
        return "auth", tail
    if code == "0":
        return "ok", tail
    return "died", "exit %s: %s" % (code if code else "unrecorded (killed at its cap?)", tail or "empty log")


def conductor_raise(why, first, now):
    """A RAISE FIRST line in the Conductor log, the line dispatcher.conductor_log writes. -> what happened."""
    p = os.environ.get("TESTQ_CONDUCTOR_LOG")
    try:
        if not p:
            with open(os.path.join(RIMFLOW_DIR, "dispatcher_schedule.json"), encoding="utf-8") as f:
                p = json.load(f)["no_handoff"]["conductor_log"]
        if RIMFLOW_DIR not in sys.path:
            sys.path.insert(0, RIMFLOW_DIR)
        import conductor_log_guard
        conductor_log_guard.refuse_if_test(p)
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n%s — STEWARD ESCALATION: %s\n  RAISE FIRST: %s\n" % (iso(now), why, first))
        return "logged"
    except (OSError, ValueError, KeyError, TypeError) as e:
        return "conductor log failed: %s" % e


def settle_wake(inc, now, src="steward"):
    """A wake that ended is looked at once, by the pass that launched it. A death is told on the item, the journal,
    the incident and the Conductor log, because `started` only ever meant systemd took it. An auth death did no work:
    its cooldown goes back and the incident may wake again, through maybe_wake's login check, TESTQ_WAKE_RETRIES times.
    -> ok | auth | died, or None when nothing was settled."""
    rec = T.read_json(path("wake.json")) or {}
    if not rec.get("exit") or rec.get("outcome") or rec.get("by", "steward") != src or wake_active():
        return None
    verdict, text = wake_outcome(rec)
    rec.update(outcome=verdict, outcome_text=text, settled=iso(now))
    said = None
    if verdict != "ok":
        mine = bool(inc) and inc.get("item") == rec.get("item")
        said = "the wake started %s died: %s" % (rec.get("ts"), text)
        again = False
        if verdict == "auth":
            cause = FC.ACCOUNT
        elif text.startswith("signal "):
            cause = FC.KILLED
        elif text.startswith("exit unrecorded"):
            cause = FC.TIMED_OUT
        else:
            cause = FC.ENDED
        out = FC.read(cause)
        if verdict == "auth":
            again = mine and inc.get("wake_retries", 0) < int(os.environ.get("TESTQ_WAKE_RETRIES", "2"))
            if again or not mine:
                rec["epoch"] = None                 # the cooldown paces work done; this did none
        if mine:
            if again:
                inc["wake_retries"] = inc.get("wake_retries", 0) + 1
                inc.pop("wake", None)
                said += "; it wakes again once the login works"
            elif not out.counts:        # it did not count (failure_class): not the incident's one wake, tried again
                inc["wake"] = "skipped: %s; it wakes again after its cooldown" % said
            else:
                inc["wake"] = said
    S.dump(rec, path("wake.json"))
    jlog({"ts": iso(now), "event": "wake_result", "by": src, "item": rec.get("item"), "result": verdict, "text": text})
    if said:
        rimflow("note", rec.get("item"), "--text", "%s: %s; log %s" % (src, said, rec.get("log")))
        conductor_raise("%s: %s (item %s, log %s)" % (src, said, rec.get("item"), rec.get("log")),
                        "A lane wake died: no agent is looking at %s." % rec.get("item"), now)
    return verdict


def launch_wake(clone, brief_path, log_path, budget, max_s):
    """Start the capped session in its own transient unit (it outlives this oneshot pass; systemd kills it at
    RuntimeMaxSec). -> (ok, text)."""
    exe = os.environ.get("TESTQ_WAKE_CLAUDE") or shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    sys.path.insert(0, RIMFLOW_DIR)
    import spend_watchdog
    # Record the watchdog's signed return code on fd 3, falling back to the shell status if Python fails.
    record_exit = (
        "import os, runpy, sys\n"
        "status = runpy.run_path(sys.argv[1])['main'](sys.argv[2:])\n"
        "os.write(3, str(status).encode('ascii'))"
    )
    import effort as EF     # RIMFLOW_DIR is on the path (above): the one effort table
    claude = "%s -p \"$(cat %s)\" --effort %s --dangerously-skip-permissions" % (
        shlex.quote(exe), shlex.quote(brief_path), EF.level())
    cmd = 'status=$(%s%s 3>&1 > %s 2>&1); echo "${status:-$?}" > %s' % (
        spend_watchdog.wrap_shell(claude, budget, python="python3 -c " + shlex.quote(record_exit)),
        (" --model " + shlex.quote(os.environ["TESTQ_WAKE_MODEL"])) if os.environ.get("TESTQ_WAKE_MODEL") else "",
        shlex.quote(log_path), shlex.quote(exit_path(log_path)))
    try:
        import control as C     # the one admission point (control.py)
        r = C.launch_unit(["--user", "--collect", "-p", "RuntimeMaxSec=%d" % max_s,
                           "-p", "WorkingDirectory=%s" % clone, "--setenv=RIMFLOW_SEAT=BENCH",
                           "--setenv=PATH=%s" % os.environ.get("PATH", ""), "--", "/bin/bash", "-c", cmd],
                          # budget: danger=a hung launch holds the steward's pass; longest=1.3s (admission to start of 1057
                          # budget: runs, control.db)
                          {"family": "testq", "unit": WAKE_UNIT, "reuse_name": True}, capture_output=True, text=True, timeout=60)
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
                           # budget: danger=a hung git pull holds the steward's pass; never reached in the 14 days to
                           # budget: 2026-11-24; no record of its run
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
touch ArchBig. Note what you found and did on the item; close it only if the lane is RUNNING again. If you
cannot fix it, say exactly what the owner must do on the item and stop. You have a hard spending and time cap.
""" % (inc["unowned_s"] // 60, inc["state"], ls["reason"][:300], item_line,
       path("steward.json"), path("steward.jsonl"), path("tick.log"), os.path.join(clone, RUNBOOK))


def maybe_wake(inc, ls, now, src="steward"):
    """The capped LLM wake, at most once per incident -> what happened (also kept in inc["wake"]). A "skipped:" is not
    that one wake: it is tried again each pass, so a cooldown that ends under a live incident wakes it
    (OPS_STEVE_UNSTICK_UNCLAIMED_A00D: 26F1's skip at 19:31Z held for good, the cooldown ended 20:33Z, the lane sat)."""
    if (inc.get("wake") and not inc["wake"].startswith("skipped:")) or inc["level"] < 2 or not inc.get("item"):
        return None
    if os.environ.get("TESTQ_STEWARD_WAKE", "1") == "0" or os.path.exists(path("wake.stop")):
        return None
    try:
        if claim_pauses(inc, now):
            return None
    except LedgerUnreadable as e:           # VHRP: no wake on a blind ledger, and no raise before the heartbeat;
        inc["error"] = (LEDGER_ERR + str(e))[:200]      # the error marks the ladder blind; the next pass retries
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
    live, why = wake_login()
    if live is False:                       # it would die on this at once and spend the incident's one wake
        if "wake_login_held" not in inc:
            inc["wake_login_held"] = now
            jlog({"ts": iso(now), "event": "wake_login_held", "by": src, "item": inc["item"], "why": why})
        return None
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
        S.dump({"ts": iso(now), "epoch": now, "item": inc["item"], "log": logp, "brief": brief, "by": src,
                "exit": exit_path(logp)}, path("wake.json"))
        rimflow("note", inc["item"], "--text", "%s: started one capped headless BENCH session (budget $%s, %d s cap); "
                "log %s" % (src, budget, max_s, logp))
    inc["wake"] = ("started %s, log %s" % (iso(now), logp)) if ok else "launch failed: " + out
    jlog({"ts": iso(now), "event": "wake", "by": src, "result": inc["wake"], "item": inc["item"]})
    return inc["wake"]


class LedgerUnreadable(Exception):
    """The ledger could not be read (a torn shard after an unclean stop: OPS_STEVE_UNSTICK_VHRP). A pass that meets it
    still writes its heartbeat; the ladder records the error on the incident and retries next pass."""


def read_events(model):
    """model.read() -> events; a LedgerError becomes LedgerUnreadable, so no pass dies before its heartbeat."""
    try:
        return model.read()
    except model.LedgerError as e:
        raise LedgerUnreadable(str(e)) from e


def world():
    """The replayed ledger (production: every shard; a selftest: RIMFLOW_LEDGER)."""
    if RIMFLOW_DIR not in sys.path:
        sys.path.insert(0, os.path.dirname(RIMFLOW_DIR))
    from rimflow import model
    model.EVENTS = os.environ.get("RIMFLOW_LEDGER") or model.EVENTS
    return model, model.replay(read_events(model))


# ---------------------------------------------------------------- the clock and the escalation ladder

def claim_holds(item_id, now, w=None):
    """True while a claim on ITEM pauses the clock: a live lease, or no lease and under 2 h since the claim."""
    if not item_id:
        return False
    model, wd = w or world()
    it = wd.items.get(item_id)
    win = _window(it, model)
    return bool(win and now < win[1])


def abandoned(item_id, now, w):
    """True for an open item a seat started under a claim that has lapsed: its holder is gone, relentless drains only
    proposed/ready, and steve.incident_unclaimed_min does not count it, so a rung parked there is seen by nobody
    (A00D: the wake's 26F1 took a new fault at 19:10Z). A start with no claim is relentless's live worker, not this."""
    it = w[1].items.get(item_id) if item_id else None
    return bool(it and it.open and it.state == "doing" and it.claim_ts and not claim_holds(item_id, now, w))


def claim_pauses(inc, now, w=None):
    """True while a claim on INC's item may still pause INC: claim_holds, and the incident has not yet spent its
    CLAIM_HOLD_S of claim pause (STEWARD_FIX_ENDS_ON_GREEN_NOT_RUNNING: a renewed lease paused the clock forever)."""
    return inc.get("claim_paused_s", 0) < CLAIM_HOLD_S and claim_holds(inc.get("item"), now, w)


def capped_cover(inc, a, b):
    """claim_cover over [A, B] for INC's item, capped so one incident never pauses for more than CLAIM_HOLD_S in all;
    -> the seconds paused, added to inc["claim_paused_s"]. An unreadable ledger pauses nothing: the clock runs."""
    try:
        cover = claim_cover(inc.get("item"), a, b)
    except LedgerUnreadable:
        cover = 0
    c = min(cover, max(0, CLAIM_HOLD_S - inc.get("claim_paused_s", 0)))
    inc["claim_paused_s"] = inc.get("claim_paused_s", 0) + c
    return c


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
        if getattr(it, "state", None) == "ready" and LT.CAUSE_ITEM.fullmatch(it.id):
            return None                         # reclaim cleared the lease and returned the cause to the pool
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

    model.replay(read_events(model), observe=observe)
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


def open_lane_item(w, now):
    """Find an older escalation when an in-flight incident has no cause key."""
    for k, it in sorted(w[1].items.items()):
        if (k.startswith("STEVE_LANE_UNSTICK_") and "_UNOWNED_" in k and not LT.CAUSE_ITEM.fullmatch(k)
                and it.open and not abandoned(k, now, w)):
            return k
    return None


def item_open(item_id, w):
    it = w[1].items.get(item_id) if item_id else None
    return bool(it and it.open)


def mint(w, tag, who, cause=None):
    """Keep the landed name of a cause. A terminal ticket needs a named successor."""
    model, wd = w
    known = set(wd.items)
    if cause:
        base = name = "STEVE_LANE_UNSTICK_%s_%s_%s" % (tag, who, cause)
        n = 1
        while name in known and not item_open(name, w):
            n += 1
            name = "%s_R%d" % (base, n)
        if name in known or not model.mint_problems(name, known):
            return name
    for _ in range(20):
        name = "STEVE_LANE_UNSTICK_%s_%s_%s" % (tag, who, secrets.token_hex(2).upper())
        if not model.mint_problems(name, known):
            return name
    raise RuntimeError("no mintable escalation name for %s/%s" % (tag, who))


def retire(items, why, now):
    """Wait on a cause or retire a legacy item. Leave work a seat holds and retry refused writes."""
    left = []
    for k, item in enumerate(items):
        try:
            w = world()
        except LedgerUnreadable as e:
            jlog({"ts": iso(now), "event": "retire_failed", "item": item, "error": (LEDGER_ERR + str(e))[:200]})
            return left + list(items[k:])
        if not item_open(item, w):
            continue
        if claim_holds(item, now, w) or (w[1].items[item].state == "doing" and not abandoned(item, now, w)):
            left.append(item)
            continue
        it, event = w[1].items[item], "retired"
        cause = LT.CAUSE_ITEM.fullmatch(item)
        if cause:
            if it.blocked:
                continue
            rc, out = bench("block", item, "--kind", "external", "--reason", LT.WAIT + cause[1] + " (" + it.title + ")")
            event = "cause_wait"
        else:
            rc, out = drop_as_bench(item, why)
        if rc == 0:
            jlog({"ts": iso(now), "event": event, "item": item, "publish": publish_bench()})
        else:
            left.append(item)
            jlog({"ts": iso(now), "event": "retire_failed", "item": item, "error": out[-200:]})
    return left


def jlog(rec):
    with open(path("steward.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def escalate(inc, ls, now, last_item, src="steward"):
    """Advance INC up the ladder by its unowned clock. -> the item the incident escalated (or None). Each rung is
    recorded in the incident only once its ledger write succeeded, so a refused write is retried next pass. An
    unreadable ledger is that refusal too: inc["error"] says so and the pass goes on to write its heartbeat."""
    try:
        return _escalate(inc, ls, now, last_item, src)
    except LedgerUnreadable as e:
        inc["error"] = (LEDGER_ERR + str(e))[:200]
        jlog({"ts": iso(now), "event": "escalate_failed", "by": src, "error": inc["error"]})
        return None


def _escalate(inc, ls, now, last_item, src):
    u = inc["unowned_s"]
    if u < L1_S:
        return None
    key = inc.get("key")
    if key:
        inc.setdefault("opened", iso(now - max(0, u - L1_S) if inc["level"] else now))
    w = world()
    left = not item_open(inc.get("item"), w) or (
        (not key or u >= L2_S) and abandoned(inc.get("item"), now, w))
    if inc["level"] >= 3 and not left:
        return None
    tag = TAG.get(inc["state"], "STALLED")
    what = "%s: %s%s" % (inc["state"], ls["reason"][:200], (" (jobs %s)" % ",".join(map(str, ls["jobs"])))
                         if ls.get("jobs") else "")
    if inc["level"] >= 1 and left:                  # closed or left under a continuing fault: open (or reuse) another.
        inc.update(level=0, item=None)              # At L3 too: Operations' told row is no item to drain (ETBS)
    if inc["level"] < 1:
        item = mint(w, tag, "UNOWNED", key or LT.cause_key(inc["state"], ls["reason"]))
        if key:
            book = {key: {"item": item, "open": None, "incidents": []}} if item_open(item, w) else {}
            _, act = LT.step(book, {"state": inc["state"], "reason": inc["cause_reason"],
                                    "began": S.parse_ts(inc["opened"])})
            last_item = act[1] if act[0] == "note" else None
        elif not item_open(last_item, w) or abandoned(last_item, now, w):
            last_item = open_lane_item(w, now) or (item if item_open(item, w) else None)
        if item_open(last_item, w):
            it = w[1].items[last_item]
            changes = []
            if key and abandoned(last_item, now, w):
                changes.append("reclaim")
            if key and it.blocked and (it.blocked_reason or "").startswith(LT.WAIT):
                changes.append("unblock")
            for verb in changes:
                rc, out = bench(verb, last_item, "--reason", "steward: lane cause returned")
                if rc:
                    inc["error"] = out[-200:]
                    return None
                publish_bench()
            rc, out = rimflow("note", last_item, "--text", "%s: SteveDesktop lane %s again since %s, %d min unowned"
                              % (src, what, inc["since"], u // 60))
            item = last_item
        elif nobody_for(ALARM_SEAT, "offline"):     # T2: never an item nobody picks up; the error is on the incident
            rc, out = 1, "no receiver: " + nobody_for(ALARM_SEAT, "offline")
        else:
            rc, out = rimflow("spawn", "--from", STEWARD_ITEM, "--for", ALARM_SEAT, "--needs", "offline", "--name", item,
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
    if inc["level"] < 3 and u >= L3_S and not claim_pauses(inc, now, w):
        if inc.get("told"):                         # a reissued item: Operations already holds this incident's rung
            inc.update(level=3, error=None)
            return inc["item"]
        why = ("%sSteveDesktop lane %s %d min, no seat on %s: %s"
               % ("IN PERSON: " if inc["state"] == "UNREACHABLE" else "", inc["state"], u // 60, inc["item"],
                  ls["reason"]))
        try:
            tell_operations(why, inc["item"], now)
        except Exception as e:     # noqa: BLE001  (a torn or unwritable told ledger: retried next pass)
            inc["error"] = ("told: %s: %s" % (type(e).__name__, e))[-200:]
            return inc["item"]
        inc.update(level=3, told=iso(now), error=None)
        jlog({"ts": iso(now), "event": "escalate", "level": 3, "item": inc["item"], "told": STEVE_RUNG_KIND, "by": src})
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
    settle_wake(inc, now)
    dt = max(0.0, now - prev["epoch"]) if prev.get("epoch") else 0.0
    to_retire = list(prev.get("to_retire") or [])
    proof = None
    if inc:
        try:
            began = S.parse_ts(inc["since"])
        except (KeyError, TypeError, ValueError):     # an unreadable start: it begins now, never "proven" by old jobs
            began, inc["since"] = now, iso(now)
        inc["impact_s"] = int(now - began)          # the impact clock: never paused, never frozen
        proof = T.lane_proven_after([{"finished": inc["since"]}])
    if inc and proof:
        pj = (proof.get("job") or {}).get("id") or "?"
        failreport(True)
        if inc.get("item"):
            rimflow("note", inc["item"], "--text", "steward: SteveDesktop lane proven again: job %s DONE with its "
                    "canary on at %s, after %s since %s (%d min unowned, %d min impact)"
                    % (pj, proof.get("finished") or (proof.get("result") or {}).get("finished"), inc["state"],
                       inc["since"], inc["unowned_s"] // 60, inc["impact_s"] // 60))
        jlog({"ts": iso(now), "event": "recovered", "proof": pj, "incident": inc})
        to_retire += [i for i in (inc.get("item"), inc.get("owner_item")) if i and i not in to_retire]
        inc = None
    if inc is None and (ls["settled"] or proof):
        to_retire = retire(to_retire, "steward: SteveDesktop lane %s again (%s)" % (ls["state"], ls["reason"][:120]),
                           now)
    elif inc and ls["state"] == "RUNNING":
        # RUNNING is not recovery (STEWARD_FIX_ENDS_ON_GREEN_NOT_RUNNING). The clock keeps running and the ladder climbs;
        # no wake while a job holds the lane.
        if prev.get("fault") or prev.get("state") == "RUNNING":
            inc["unowned_s"] = int(inc["unowned_s"] + dt - capped_cover(inc, now - dt, now))
        rung = (inc["level"], inc.get("item"), inc.get("told"))
        last_item = escalate(inc, dict(ls, reason="lane RUNNING again (%s) but no DONE+canary job since %s"
                                       % (ls["reason"], inc["since"])), now, last_item) or last_item
        if (inc["level"], inc.get("item"), inc.get("told")) != rung:
            jlog({"ts": iso(now), "event": "rung_publish", "item": inc.get("item"), "result": safe_publish()})
    elif fault:
        key = LT.cause_key(ls["state"], ls["reason"])
        if not inc:
            inc = {"state": ls["state"], "since": iso(now), "unowned_s": 0, "level": 0, "item": None,
                   "told": None}
            dt = 0.0
        else:
            old_item = inc.get("item")
            named = LT.CAUSE_ITEM.fullmatch(old_item or "")
            old_key = inc.get("key") or (named[1] if named else None)
            if (old_key and old_key != key) or inc["state"] != ls["state"]:
                jlog({"ts": iso(now), "event": "cause_changed", "incident": inc, "next": key})
                if old_item and old_item not in to_retire:
                    to_retire.append(old_item)
                inc = {k: inc[k] for k in ("unowned_s", "opened") if k in inc}
                inc.update(since=iso(now), level=0, item=None, told=None)
        inc["state"] = ls["state"]
        inc.update(key=key, cause_reason=ls["reason"])
        if prev.get("fault") or prev.get("state") == "RUNNING":
            inc["unowned_s"] = int(inc["unowned_s"] + dt - capped_cover(inc, now - dt, now))
        if ls["at_once"]:
            inc["unowned_s"] = max(inc["unowned_s"], L1_S)
        rung = (inc["level"], inc.get("item"), inc.get("told"))
        item = escalate(inc, ls, now, last_item)
        last_item = item or last_item
        if (inc["level"], inc.get("item"), inc.get("told")) != rung:
            jlog({"ts": iso(now), "event": "rung_publish", "item": inc.get("item"), "result": safe_publish()})
        maybe_wake(inc, ls, now)
    if inc and to_retire:
        pending = [i for i in to_retire if i != inc.get("item")]
        waits = [i for i in pending if LT.CAUSE_ITEM.fullmatch(i)]
        to_retire = [i for i in pending if i not in waits] + retire(waits, "steward: lane cause changed", now)
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
    settle_wake(inc, now, src="steward-watch")
    if age > STALE_S:
        start = tick_run_start()
        if start and now - start <= TICK_HUNG_S:      # a long tick still running: its steward pass writes at its end;
            # an open incident stays as it is (no recovery, no rung) until that pass writes or the tick hangs
            wst.update(ts=iso(now), epoch=now, age_s=int(age), tick_running_s=int(now - start))
            S.dump(wst, path("steward_watch.json"))
            return wst
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
                   "told": None, "restarted": None}
            jlog({"ts": iso(now), "event": "state", "state": "STALE_HEARTBEAT", "fault": True, "reason": reason,
                  "by": "watch"})
        prev_t = wst.get("epoch") or now
        capped_cover(inc, prev_t, now)
        inc["impact_s"] = int(now - S.parse_ts(inc["since"]))
        inc["unowned_s"] = int(age - inc["claim_paused_s"])
        if not inc.get("restarted"):
            inc["restarted"] = "%s %s" % (iso(now), restart_tick())
            jlog({"ts": iso(now), "event": "restart", "by": "watch", "result": inc["restarted"]})
        else:
            lvl = inc["level"]
            ls = {"reason": reason + "; restarting testq-tick.timer did not bring it back", "jobs": []}
            inc.update(key=LT.cause_key(inc["state"], ls["reason"]), cause_reason=ls["reason"])
            escalate(inc, ls, now, (sj or {}).get("last_item"), src="steward-watch")
            if inc["level"] != lvl:
                safe_publish()
            maybe_wake(inc, ls, now, src="steward-watch")
        wst["incident"] = inc
    pending = [i for i in wst.get("to_retire") or [] if i != (wst["incident"] or {}).get("item")]
    wst["to_retire"] = retire(pending, "steward-watch: the steward is writing again", now)
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
