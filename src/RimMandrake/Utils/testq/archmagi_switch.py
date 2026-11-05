#!/usr/bin/env python3
"""archmagi_switch.py - the section 2 trial switch for the Archmagi backfill (ARCHMAGI_BACKFILL_WIRE_TRIAL_SWITCH).

Spec: design/RimMandrake/work_allocation_framework_2026-10-26.md section 2. Owner ruling 2026-10-26 (by card): Archmagi's
game may run scripted batch tests unattended under these rules, only while no agent holds Archmagi's bridge.

Pure: `decide(inp, state, now)` -> (new_state, events). No I/O; testq.py gathers the inputs every tick and writes the
state back (queue/archmagi_state.json, key "switch"). The switch says whether the backfill MAY admit; the per-job gate
(testq.archmagi_gate: bridge free and silent, driver lock, runner clone, back-off) still decides each admission.

  S1 Saturation  ON when, all at once: SteveDesktop's useful (non-filler) ready work has waited (oldest ready job > 30 min,
                 or ready work > 60 lane-minutes) continuously for 60 min; SteveDesktop's INVALID share over the last 6 h
                 is under 20%; the bridge gate is open. OFF on a bridge take, the ready queue draining, or the latch.
  S2 Failover    ON when SteveDesktop has been paused, quarantined or unreachable for more than 30 min with fix-purpose
                 jobs ready, and the bridge gate is open. OFF when SteveDesktop is healthy again, or on a bridge take.
  S3 Never       `s3_refusal(job, ...)`: filler, guard and sweep jobs never run on Archmagi; a job that needs a deploy or
                 a load runs only when the value queued for that load is at least twice the load time (the train rule).
  Cooldown       after any OFF, no ON for 30 min.
  Latch          2 consecutive INVALID attempts on Archmagi latch the switch OFF until the HARNESS item LATCH_ITEM is
                 closed on the ledger after the latch was set (inp["latch_closed_at"]).

`inp` keys (testq.switch_inputs builds them):
  useful_oldest_wait_s  age of the oldest ready non-filler job (None: none ready)
  useful_lane_s         summed estimated lane seconds of the ready non-filler jobs
  fix_ready             count of ready fix-purpose jobs
  steve_invalid_share   INVALID / finished attempts on SteveDesktop over 6 h (None: no attempts, which reads as healthy)
  steve_unavailable_s   seconds SteveDesktop has been paused/quarantined/unreachable (None: it is available)
  gate_ok, gate_why     testq.archmagi_gate() (the bridge gate and friends)
  bridge_holder         who holds the bridge now, else None (a take turns the switch OFF)
  arch_invalid_streak   trailing run of INVALID results on Archmagi, newest first, counted since the last latch clear
  latch_closed_at       epoch of the latest ledger close of LATCH_ITEM (None: never closed)
  force                 TESTQ_ARCHMAGI_SWITCH=force: S1/S2 ON conditions waived (an operator's or a test's seam); the
                        latch, the cooldown and S3 still bind
"""

SUSTAIN_S = 3600            # S1 must hold for 60 min running
OLDEST_WAIT_S = 1800        # S1: oldest ready non-filler job waited > 30 min
LANE_S = 3600               # S1: or ready non-filler work > 60 lane-minutes
INVALID_SHARE_MAX = 0.20    # S1: SteveDesktop's INVALID share over 6 h under 20%
UNAVAILABLE_S = 1800        # S2: SteveDesktop down/paused/quarantined > 30 min
COOLDOWN_S = 1800           # after OFF, no ON for 30 min
LATCH_STREAK = 2            # 2 consecutive INVALID attempts on Archmagi
LATCH_ITEM = "ARCHMAGI_LATCH_FIX_TWO_STRIKES"
NEVER_PURPOSES = ("guard", "sweep")
FILLER = "BENCH.filler"
LOAD_S = 900                # one load of the owner's full list (11-25 min measured 10-25; the low end, so the rule binds)
HISTORY_MAX = 200
TICK_GAP_S = 300            # S1's sustain clock: readings further apart than this are not "running"


def s1_pressure(inp):
    """-> why S1's queue condition holds now, else None."""
    w = inp.get("useful_oldest_wait_s")
    if w is not None and w > OLDEST_WAIT_S:
        return "oldest ready non-filler job waited %d min" % (w // 60)
    lane = inp.get("useful_lane_s") or 0
    if lane > LANE_S:
        return "ready non-filler work %d lane-min" % (lane // 60)
    return None


def _event(events, now, kind, rule, why):
    events.append({"at": now, "kind": kind, "rule": rule, "why": why})


def decide(inp, state, now):
    """-> (new state, events). `state` is the previous switch state ({} at first)."""
    st = dict(state or {})
    if not state:
        st["latch_cleared_at"] = now        # the trial starts clean (testq counts the INVALID streak from here)
    st.setdefault("on", False)
    events = []

    # the latch: set on 2 consecutive INVALID attempts; cleared by a ledger close of LATCH_ITEM after it was set
    latch = st.get("latch")
    unlatched = False
    if latch and inp.get("latch_closed_at") and inp["latch_closed_at"] > latch["at"]:
        st["latch"] = None
        st["latch_cleared_at"] = now
        _event(events, now, "unlatch", None, "%s closed" % LATCH_ITEM)
        latch, unlatched = None, True
    # this tick's streak was counted before the clear: only the next tick's (results after latch_cleared_at) may latch
    if not latch and not unlatched and (inp.get("arch_invalid_streak") or 0) >= LATCH_STREAK:
        latch = st["latch"] = {"at": now, "why": "%d consecutive INVALID attempts on archmagi" % inp["arch_invalid_streak"],
                               "item": LATCH_ITEM}
        _event(events, now, "latch", st.get("rule"), latch["why"] + "; closed until %s is closed" % LATCH_ITEM)

    # S1's 60-minute sustain clock runs whether or not the switch is on
    # ("for 60 min running": a gap in the readings longer than TICK_GAP_S - a stopped timer - restarts it)
    pressure = s1_pressure(inp)
    seen = st.get("s1_seen")
    if pressure and st.get("s1_since") and seen is not None and now - seen <= TICK_GAP_S:
        pass
    elif pressure:
        st["s1_since"] = now
    else:
        st["s1_since"] = None
    st["s1_seen"] = now if pressure else None

    def off(why):
        _event(events, now, "off", st.get("rule"), why)
        st.update(on=False, rule=None, off_at=now, since=None)

    if st["on"]:
        rule = st.get("rule")
        if latch:
            off("latched: " + latch["why"])
        elif inp.get("bridge_holder"):
            off("bridge taken by %s" % inp["bridge_holder"])
        elif rule == "S1" and not inp.get("force") and not pressure and not inp.get("useful_oldest_wait_s") \
                and not inp.get("useful_lane_s"):
            off("the ready queue drained")
        elif rule == "S2" and not inp.get("force") and inp.get("steve_unavailable_s") is None:
            off("SteveDesktop healthy again")
        elif rule == "FORCE" and not inp.get("force"):
            off("force withdrawn")
    if not st["on"]:
        why = on_reason(inp, st, now, latch)
        if why[0]:
            st.update(on=True, rule=why[0], since=now)
            _event(events, now, "on", why[0], why[1])
        st["closed_why"] = None if st["on"] else why[1]
    if st["on"]:
        st["closed_why"] = None
    hist = (st.get("history") or []) + events
    st["history"] = hist[-HISTORY_MAX:]
    return st, events


def on_reason(inp, st, now, latch):
    """-> (rule, why) when the switch may turn ON now, else (None, the first reason it may not)."""
    if latch:
        return None, "latched since %s: %s (close %s)" % (latch["at"], latch["why"], LATCH_ITEM)
    off_at = st.get("off_at")
    if off_at and now - off_at < COOLDOWN_S:
        return None, "cooling down %d s more after OFF" % (COOLDOWN_S - (now - off_at))
    if not inp.get("gate_ok"):
        return None, "bridge gate closed: %s" % inp.get("gate_why")
    if inp.get("force"):
        return "FORCE", "TESTQ_ARCHMAGI_SWITCH=force"
    s2_no = None
    un = inp.get("steve_unavailable_s")
    if un is not None:
        if un <= UNAVAILABLE_S:
            s2_no = "S2: SteveDesktop unavailable %d s, needs > %d s" % (un, UNAVAILABLE_S)
        elif not inp.get("fix_ready"):
            s2_no = "S2: SteveDesktop unavailable %d min but no fix-purpose job is ready" % (un // 60)
        else:
            return "S2", "SteveDesktop unavailable %d min, %d fix job(s) ready" % (un // 60, inp["fix_ready"])
    # S2 not met: S1 still applies (a queue backed up behind a short outage is saturation too)
    rule, why = s1_reason(inp, st, now)
    return (rule, why) if rule else (None, "%s; %s" % (s2_no, why) if s2_no else why)


def s1_reason(inp, st, now):
    pressure = s1_pressure(inp)
    if not pressure:
        return None, "S1: SteveDesktop is not saturated with useful work"
    held = now - (st.get("s1_since") or now)
    if held < SUSTAIN_S:
        return None, "S1: %s, held %d min of 60" % (pressure, held // 60)
    share = inp.get("steve_invalid_share")
    if share is not None and share >= INVALID_SHARE_MAX:
        return None, "S1: SteveDesktop INVALID share %.0f%% over 6 h (needs < 20%%)" % (share * 100)
    return "S1", "%s for %d min; Steve INVALID %s" % (pressure, held // 60,
                                                   "n/a" if share is None else "%.0f%%" % (share * 100))


def s3_refusal(job, queued_load_value_s=0, load_s=LOAD_S):
    """-> why S3 forbids JOB on Archmagi, else None. `queued_load_value_s`: the lane seconds queued for the same load as
    this job (its own included), for a job that needs a deploy or a load (the train rule: at least twice the load)."""
    if job.get("requested_by") == FILLER:
        return "S3: filler never runs on archmagi"
    if job.get("purpose") in NEVER_PURPOSES:
        return "S3: %s jobs never run on archmagi" % job["purpose"]
    if needs_load(job) and queued_load_value_s < 2 * load_s:
        return "S3: needs a deploy/load; %d s queued for it is under twice the load (%d s)" % (
            queued_load_value_s, 2 * load_s)
    return None


def needs_load(job):
    """A job that cannot run on the game already up: it names extra mods to deploy (`deploy`). Archmagi's phases never
    deploy or launch (they refuse), so such a job is only worth sending as part of a train."""
    return bool(job.get("deploy"))


def load_key(job):
    return (job.get("profile"), tuple(sorted(job.get("deploy") or ())))
