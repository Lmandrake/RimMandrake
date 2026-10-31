#!/usr/bin/env python3
"""role_launch.py — the Dispatcher's role launcher (item DISPATCHER_BUILD_ROLE_LAUNCH_FROM_SCHEDULE; spec
design/RimMandrake/rimflow_v3_2026-10-26.md §3, §6). dispatcher.decide() calls decide_roles(); dispatcher.execute()
calls launch() / stop(). A program: it decides nothing the schedule and the role files do not say.

What it runs: every role in dispatcher_schedule.json `roles` that is `enabled` AND carries the launch keys
(LAUNCH_KEYS: instructions, seat, clone, model, ledger_item). An enabled role without them (Arbiter, Auditor, ...)
is still an ALARM, as in v3.0: switching on a role nobody can run must be loud.

When: the role's clock slots — `quick_checks_local` (Conductor) or `runs_local` (Operations), local "HH:MM" — each
once per local day, launched in the first tick at or after the slot and no later than `slot_late_s` after it (a
missed slot is journaled, never run late). The slot equal to `economy_pass_local` is the economy pass, which carries
that slot's running check with it: when a band skips the economy pass the whole slot is skipped (the cheaper reading,
operations.md says so). A role with `after_role` (Conductor -> Operations) launches a slot only after that role's own
scheduled run for the slot it follows (08:00 -> 07:30, 20:00 -> 19:30; never an alarm run or yesterday's late run)
finished done and none is going (after_ready); a slot of that role its band skipped on purpose is passed over for
its previous one within 24 h (Producer 09:00 in AMBER/RED -> Operations 19:30); it is decided after that role in each tick. Operations
also runs once per OPEN ops_watch alarm crossing (`alarm_runs`): `alarms_seen` is pruned to the alarms open now, so
one that clears runs again when it re-crosses (review W, W1); alarms already open when the role is first enabled run
once too (no baseline). One alarm run covers every open alarm not yet run, and alarm runs are at least
`alarm_run_gap_s` (ALARM_RUN_GAP_S) apart; alarms are read only from a MEASURED reading whose alarms dict is readable
(a blind tick prunes nothing and runs no alarm). One run per role at a time.

Weekdays (item DISPATCHER_BUILD_WEEKDAY_AND_EVENT_TRIGGERS): a slot may name its days, "Wed 09:00" or
"Mon,Thu 10:00" (parse_slot; an unreadable slot is an alarm and the role does not run). `weekly_plan_weekday` makes
that day's first run slot mode "weekly" (the Producer's Wednesday plan); band `slots: "weekly"` runs only that slot
and event runs (RED: "the Wednesday plan and replan requests only", v3 §3).

Ledger events (the same item), read once per tick with model.read() + replay (read_ledger), after a baseline: the
first MEASURED tick with the role enabled sets `event_cursor`; every launch of the role moves it to the launch time,
because every run reads the events up to its start. "After the cursor" is by identity, not by ts (review U, N4): the
cursor is this clone's clock and an event's ts is its writer's, so an event written on another clone before a launch
can be pulled after it. The window reaches EVENT_LOOKBACK_S behind the cursor and `events_seen` (the events a run or
the baseline already read) drops the ones counted; an event pulled more than EVENT_LOOKBACK_S late is still missed.
An event run fits beside the day's scheduled runs still to come (their budgets are reserved, N3), else it waits.
  - `slot_when: "done_claims"` (Arbiter): a scheduled slot launches only when a done claim — a `rimflow implemented`
    event (built) or a `rimflow close` — landed after the cursor; else the slot is marked "no done claims" (a hold,
    no alarm). The batches stay at the clock slots: the event is "claims are pending" (arbiter.md).
  - `slot_when: "pending_work"` (Arbiter since ARBITER_BUILD_LAUNCH_ON_ANY_PENDING_WORK): a scheduled slot launches
    when any `pending_work` kind (arbiter_pending.py: escapes, unresolved, done_claims, verify_backlog) has work, read
    from STATE (the ledger plus verdicts.jsonl and tiers_history.jsonl), never from the cursor: a launch consumes
    nothing, so what a run did not judge is pending again at the next slot. Nothing pending: the slot is marked
    "nothing pending" (a hold, no alarm). Unreadable stores: the slot launches, the reason in its trigger.
  - `event_runs` (Producer: plan_step_failure, replan_request): a run outside the clock, at most
    `event_runs_per_day`, when one happened after the cursor. A plan-step failure is a `verify` with result fail or a
    `block`, on an item still open AND on the plan (`plan_scope`: "raised" = put atop `next` by `rimflow raise`;
    "row" = a V1 milestone row; no other plan marker is on the ledger). A replan request is a `note` on the role's
    ledger_item whose text starts with `replan_note_prefix`. Past the per-day count the events wait for the next run.
  - an unreadable ledger (model.read raises on a malformed line), or a read with zero events, is UNMEASURED: a role
    with either key launches nothing that tick, clock slots included, and one alarm is raised per outage.

Gates, in order, each journaled (and each refusal an ALARM when it needs a human):
  1. off switch: the role's `off_file` exists (its first line is the reason) -> skip the slot, no alarm.
  2. the ops_watch reading (status.json, `ops_status`): REFUSED with an alarm when it is missing, unreadable, older
     than `ops_stale_s` (45 min, conductor.md), its account cannot be resolved, or the account's runway or
     week_left_pct point is UNMEASURED. (conductor.md's table puts UNMEASURED/stale in AMBER; the build brief of
     2026-10-27 says refuse: refusing is the stricter of the two, so a quick run never launches on a blind reading.)
     The account is the switcher-registry label whose email is the one this machine is logged in as
     (account_usage.registry()/live_email()): no account is named here.
  3. throttle band (role `throttle_bands`, as conductor.md writes them): FLOOR when week_left_pct < its line, else
     the highest band whose `runway_ge` the runway meets (an ESTIMATE counts as its value). The band's `slots`
     ("all" | "first" | "last" | "none") says which scheduled slots still run and `quick_cap_x` scales the run's budget.
     A role with no bands runs at x1.0. "quick" / "quick_one" (Operations): see slot_blocked.
  4. caps: the run's budget = its cap x the band factor; it is REFUSED (alarm) when today's spend plus that budget
     passes `daily_token_cap`. Today's spend = tokens of finished runs + the full budget of runs still going.
  5. account (dispatcher.account_gate, account_pick.py): the schedule's `account_pick` rule, asked at the moment of
     release; a SWITCH pick holds the launch (journaled once per slot) until the machine is switched or the slot is
     missed. The launch records the account it runs on.

Tokens: a finished run's `claude -p --output-format json` usage, ALL FOUR fields (input, cache_creation,
cache_read, output), each weighted by its price class (TOKEN_WEIGHTS, run_tokens: input-equivalent tokens, so a cap
measures cost, not context re-reads; ROLE_CAPS_REMEASURE_ON_REAL_RUNS). Every cap, budget, daily spend and overbudget
alarm here is in these units; the raw sum is kept beside it on the run as `raw_tokens`. A run over its budget is an ALARM after the fact: `claude -p` has no
token stop and nothing here stops a run at its budget: the budget is checked on its result. Only a `token_aware` role
(Operations, the Conductor) is told its band and budget in its launch message; every other role is token-blind and is told
neither (owner 2026-10-27; review T, F1/F2). A run still going after
`run_max_s` is stopped (its claude_bounded scope and its unit) with an alarm; it stays `running` and the stop is
re-issued each tick until systemd says the unit AND its claude_bounded scope are inactive/failed (claude lives in the
scope, outside the unit; the scope is resolved while the unit runs). supervise_roles() does this for every persisted
run before PAUSE, a blind tick or a disabled role can end the tick (review round Q).

How it launches (proved 2026-10-27, D:\\ClaudeWork\\rimmandrake\\role_launch_2026-10-27\\proof\\RESULT.md): as its OWN
transient user service, `systemd-run --user --collect --unit rm-role-<name>-<epoch>`, which runs
`claude_bounded.sh -p <prompt> --model <alias> --output-format json` in the role's clone (a STRUCTURED role, the
Arbiter, also gets `--json-schema` and its verdicts are appended by the launcher: STRUCTURED, harvest). The dispatcher tick is a
oneshot unit whose cgroup systemd kills when it exits; a child started there (even setsid) died before
claude_bounded made its scope, while the transient unit ran on and finished. PATH gets claude's directory: the user
manager's PATH has no ~/.local/bin. The model is the schedule's alias; claude resolves it from its own settings
(the GenAiSwitch route vars, genai_env.py's MODEL_VARS), and the id actually used is read back from the result.

Every launch, refusal, finish and stop is a dispatcher action: journaled, and noted on the role's `ledger_item`
(an alarm-run's note goes on its alarm item) when --apply. Dry-run launches nothing.
Names no host, account or model id.
"""
import calendar
import json
import math
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from fractions import Fraction

AUTH_BACKS_PER_DAY = 2
AUTH_RX = re.compile(r"failed to authenticate|oauth session expired|login expired|please run /login|"
                     r"authentication_failed", re.I)

try:
    import arbiter_pending as PW     # the rimflow dir is on sys.path (dispatcher.py, the selftests)
except ImportError:
    from rimflow import arbiter_pending as PW
try:
    import audit_prescreen as AP
except ImportError:
    from rimflow import audit_prescreen as AP

LAUNCH_KEYS = ("instructions", "seat", "clone", "model", "ledger_item")
ROLE_DEFAULTS = {"slot_late_s": 3600, "run_max_s": 1800}
ALARM_KEY_PREFIX = "alarm:"            # an Operations-only alarm (no ledger item) in alarms_seen: "alarm:<aid>" (V2)
ALARM_RUN_GAP_S = 3600                 # at least this long between two alarm runs of a role (review W, W1)
OPS_STALE_S = 45 * 60
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")      # time.localtime().tm_wday order
DONE_CLAIM_VERBS = ("implemented", "close")   # a done claim on the ledger: built (L0 passed) or closed against a sha
ACTIVE = ("active", "activating", "deactivating", "reloading")
TERMINAL = ("inactive", "failed")      # the only states that end a run; anything else ("unknown", a failed query) is busy
EVENT_LOOKBACK_S = 6 * 3600             # an event ingested this late after its writer stamped it still triggers (N4)
FUTURE_TOL_S = 300                     # a reading stamped further ahead than this is a clock fault, not fresh
USAGE_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
# The ONE token measure for role caps (ROLE_CAPS_REMEASURE_ON_REAL_RUNS, BENCH 2026-10-28 [A]): each usage field
# weighted by its price relative to an uncached input token (Anthropic's price classes: a cache write costs 1.25x for
# the 5-minute TTL and 2x for the 1-hour TTL, a cache read 0.1x, an output token 5x). Checked against the two proof
# records whose total_cost_usd is known (selftest_role_tokens W4). A raw count weighed the first real Operations run
# (15 turns, 1.04M of its 1.12M tokens cache reads) at 1,121,450; this measure weighs it at 285,538.
TOKEN_UNIT = "weighted_v1"             # stamped on each finished run: the unit of its `tokens`
TOKEN_WEIGHTS = {"input_tokens": Fraction(1), "cache_write_5m": Fraction(5, 4), "cache_write_1h": Fraction(2),
                 "cache_read_input_tokens": Fraction(1, 10), "output_tokens": Fraction(5)}
# genai_env.py (~/dev/Lodestar/bin/lib/genai_env.py) MODEL_VARS: the env var that names each alias's model id.
# A role whose run returns STRUCTURED output (ARBITER_VERDICT_WIRE_JSON_SCHEMA_HANDOFF): its launch gets
# `--json-schema <schema text>` (claude -p takes the schema itself, not a path: `claude -p --help`), the schema read from
# the role's clone (contracts/export.py generates it from contracts.models; never hand-edited), and a finished `done`
# run's result["structured_output"][key] entries are each validated against contracts.models.<model> (pydantic, imported
# only then: the tick stays stdlib-only) and the valid ones appended to `sink` by dispatcher.execute (role_verdicts).
# An invalid entry is refused, journaled whole and alarmed; its valid siblings still land (each verdict judges its own
# claim, and a refused one leaves its claim pending, so the next batch judges it again: refusing the whole batch would
# only throw away sound verdicts). No structured_output, or one not shaped {key: [...]}: alarm, nothing appended.
# A run-now TRIAL's verdicts (role_launch.py run-now --trial) sink to `trial_sink`, never to `sink`: the real store
# is the false-reject instrument and the pending gate's record of judged claims (arbiter_pending), so a hand-picked
# trial batch (a fixture claim among them) must not count there. `note_each`: every valid entry is also noted on its
# own claim's item (arbiter.md: the verdict lives on the item for its holder; advisory, it blocks nothing).
TRIAL_VERDICTS = os.path.join(os.path.dirname(PW.VERDICTS), "trial", "verdicts.jsonl")
TRIAL_TIERS_DATA = os.path.join(os.path.dirname(PW.TIERS_HISTORY), "trial")
STRUCTURED = {"Arbiter": {"schema": "src/RimMandrake/contracts/schemas/arbiter_batch.schema.json",
                          "key": "verdicts", "model": "ArbiterVerdict", "sink": PW.VERDICTS,
                          "trial_sink": TRIAL_VERDICTS, "note_each": True}}
# A role whose pre-step screens "since my last finished run" (AUDITOR_PRESCREEN_FIX_WINDOW_SINCE_LAST_RUN): a run that
# ends `done` gets a role_stamp action (dispatcher.execute writes it through AP.write_stamp, so a dry run writes
# nothing) carrying the run's launch time, which is at or before its pre-screen's `now`: the next window overlaps by the
# pre-step's seconds, never gaps. A failed run emits none, so its window is screened again by the next run.
FINISH_STAMP = {"Auditor": AP.STAMP}
# run-now (V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE): a one-shot run asked for by hand, held in the dispatcher state as
# st["roles"][R]["run_now"] and launched by the next tick through every gate a scheduled run passes. A request the
# ticks could not launch for this long (busy, account hold) expires, said; refusals (off, ops, band, cap) consume it.
RUN_NOW_TTL_S = 3600
RUN_NOW_MODES = ("run", "quick", "weekly", "economy")
CLAIM_PRE_ROLES = ("Arbiter",)         # roles whose run-now may name claims (isolated_evidence + arbiter_tiers pre-steps)
MODEL_VARS = {"opus": "ANTHROPIC_DEFAULT_OPUS_MODEL", "sonnet": "ANTHROPIC_DEFAULT_SONNET_MODEL",
              "haiku": "ANTHROPIC_DEFAULT_HAIKU_MODEL"}


# ---------------------------------------------------------------- paths and readings

def wsl_path(p):
    """D:\\x\\y -> /mnt/d/x/y (schedule paths are written Windows-native for the owner)."""
    if p and len(p) > 2 and p[1] == ":" and p[2] in "\\/":
        return "/mnt/%s/%s" % (p[0].lower(), p[3:].replace("\\", "/"))
    return p


def ops_status_path(sch):
    if sch.get("ops_status"):
        return wsl_path(sch["ops_status"])
    for m in sch.get("measure") or []:
        if m.get("name") == "ops_watch" and m.get("out"):
            return os.path.join(wsl_path(m["out"]), "status.json")
    return None


def utc_epoch(iso_s):
    try:
        return calendar.timegm(time.strptime(iso_s, "%Y-%m-%dT%H:%M:%SZ"))
    except (TypeError, ValueError):
        return None


def finite(v):
    """A real number: int/float, not bool, not NaN/inf (Python's json accepts NaN and Infinity)."""
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def ops_reading(status, account, now, stale_s=OPS_STALE_S):
    """Pure. status = parsed status.json (or None), account = resolved label (or None).
    -> {"state": "MEASURED", "account", "runway", "runway_m", "week_left", "week_left_m", "at"}
       or {"state": "UNMEASURED", "why"}."""
    if not isinstance(status, dict):
        return {"state": "UNMEASURED", "why": "ops_watch status.json missing or unreadable"}
    at = utc_epoch(status.get("at"))
    if at is None:
        return {"state": "UNMEASURED", "why": "ops_watch status.json has no readable 'at'"}
    if at - now > FUTURE_TOL_S:
        return {"state": "UNMEASURED", "why": "ops_watch status.json 'at' %s is %d min in the FUTURE (clock or file "
                "wrong)" % (status.get("at"), (at - now) // 60)}
    if now - at > stale_s:
        return {"state": "UNMEASURED", "why": "ops_watch status.json is STALE: at %s, %d min old (> %d)"
                % (status.get("at"), (now - at) // 60, stale_s // 60)}
    if not account:
        return {"state": "UNMEASURED", "why": "the account this machine runs on is not resolved (registry/live email)"}
    pts = status.get("points") or {}
    out = {"state": "MEASURED", "account": account, "at": status.get("at")}
    for key, name in (("runway", "runway"), ("week_left_pct", "week_left")):
        p = pts.get("accounts.%s.%s" % (account, key)) or {}
        if not isinstance(p, dict):
            p = {}
        if p.get("m") not in ("MEASURED", "ESTIMATE") or not finite(p.get("v")):
            return {"state": "UNMEASURED", "why": "accounts.%s.%s is %s%s%s" % (
                account, key, p.get("m") or "absent", (" (%s)" % p["why"]) if p.get("why") else "",
                "" if p.get("m") not in ("MEASURED", "ESTIMATE") else ", value %r not a finite number" % (p.get("v"),))}
        out[name], out[name + "_m"] = float(p["v"]), p["m"]
    return out


def band(role, reading):
    """Pure. -> (band name, band dict). No bands -> ("NONE", x1.0, all slots)."""
    bands = role.get("throttle_bands") or {}
    if not bands:
        return "NONE", {"quick_cap_x": 1.0, "slots": "all"}
    for name, b in bands.items():
        if "week_left_pct_lt" in b and reading["week_left"] < b["week_left_pct_lt"]:
            return name, b
    ranked = sorted(((b["runway_ge"], name, b) for name, b in bands.items() if "runway_ge" in b), reverse=True)
    if not ranked:
        raise ValueError("throttle_bands has no band with runway_ge: no band to fall back to")
    for ge, name, b in ranked:
        if reading["runway"] >= ge:
            return name, b
    return ranked[-1][1], ranked[-1][2]          # below every line: the lowest runway band


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


BAND_SLOTS = ("all", "none", "first", "last", "weekly", "quick", "quick_one")   # slot_blocked's policies


def validate_role(role):
    """Raises ValueError naming the first schedule value decide_roles cannot use (review round U, N5): a role with a
    bad value is skipped with an alarm, never allowed to raise through the whole tick."""
    bands = role.get("throttle_bands") or {}
    if not isinstance(bands, dict):
        raise ValueError("throttle_bands is not a mapping")
    for name, b in bands.items():
        if not isinstance(b, dict):
            raise ValueError("throttle band %s is not a mapping" % name)
        for k in ("runway_ge", "week_left_pct_lt", "quick_cap_x"):
            if k in b and not _num(b[k]):
                raise ValueError("throttle band %s: %s %r is not a number" % (name, k, b[k]))
        if "quick_cap_x" in b and b["quick_cap_x"] < 0:      # a negative budget would pass every cap (review r5)
            raise ValueError("throttle band %s: quick_cap_x %r is negative" % (name, b["quick_cap_x"]))
        if b.get("slots", "all") not in BAND_SLOTS:          # slot_blocked blocks nothing it does not know (r5)
            raise ValueError("throttle band %s: slots %r is not one of %s" % (name, b.get("slots"),
                                                                             ", ".join(BAND_SLOTS)))
    if bands and not any("runway_ge" in b for b in bands.values()):
        raise ValueError("throttle_bands has no band with runway_ge: no band to fall back to")
    if role.get("slot_when") not in (None, "done_claims", "pending_work"):
        raise ValueError("slot_when %r is not done_claims or pending_work" % role["slot_when"])
    kinds = role.get("pending_work", list(PW.KINDS))
    if not (isinstance(kinds, list) and kinds and all(k in PW.KINDS for k in kinds)):
        raise ValueError("pending_work %r is not a non-empty list of %s" % (kinds, ", ".join(PW.KINDS)))
    if "claim_window_days" in role:
        raise ValueError("claim_window_days is retired: the Arbiter's queue is the work after its cutoff stamp, with no "
                         "age limit (ARBITER_FIX_CLAIMS_AGE_OUT_UNJUDGED); remove the key")
    if "pre_launch_max_s" in role and not (_num(role["pre_launch_max_s"]) and role["pre_launch_max_s"] > 0):
        raise ValueError("pre_launch_max_s %r is not a number > 0" % (role["pre_launch_max_s"],))
    per_day = role.get("event_runs_per_day", 1)
    if not isinstance(per_day, int) or isinstance(per_day, bool) or per_day < 0:
        raise ValueError("event_runs_per_day %r is not a whole number >= 0" % (per_day,))
    for k in ("run_token_cap", "quick_token_cap", "economy_token_cap", "daily_token_cap"):
        if role.get(k) is not None and not (_num(role[k]) and role[k] >= 0):
            raise ValueError("%s %r is not a number >= 0" % (k, role[k]))
    for k in ("slot_late_s", "run_max_s"):
        # the time bounds are never optional: None would override ROLE_DEFAULTS and crash supervision on every tick;
        # 0 would stop every run at once (review V, V3)
        if not (_num(role.get(k)) and role[k] > 0):
            raise ValueError("%s %r is not a number > 0" % (k, role.get(k)))
    # decide_roles reads only TODAY's slots: a late window past local midnight would drop the slot silently after
    # midnight (neither launched nor journaled missed). Refuse it loudly (review night).
    for t in role.get("quick_checks_local") or role.get("runs_local") or []:
        h, m = parse_slot(t)[1].split(":")
        if (int(h) * 60 + int(m)) * 60 + role["slot_late_s"] >= 86400:
            raise ValueError("slot %r + slot_late_s %r crosses local midnight" % (t, role["slot_late_s"]))
    if not isinstance(role.get("event_runs") or [], list):
        raise ValueError("event_runs is not a list")


def slot_blocked(allowed, job, role, now=None):
    """Pure. May this band's `slots` setting stop this job? "all": never. "none": every scheduled slot, every alarm
    run and every event run. "first" / "last": only the first / last scheduled slot of the day (now's weekday).
    "weekly": only the weekly slot (mode "weekly", the Producer's Wednesday plan) and event runs go (v3 §3, RED:
    "the Wednesday plan and replan requests only"). "quick": the economy-pass slot is skipped whole (its running check
    goes with it: operations.md), the other running checks and alarm runs go. "quick_one": the economy-pass slot and
    alarm runs are skipped, and only the first NON-economy running check runs (Ops: 19:30)."""
    if allowed == "none":
        return True
    if allowed == "first":
        return bool(job["slot"]) and not job["first"]
    if allowed == "last":
        return bool(job["slot"]) and job["slot"] != slots(role, now)[-1][0]
    if allowed == "weekly":
        return job["mode"] not in ("weekly", "event")
    if allowed in ("quick", "quick_one"):
        if job["mode"] == "economy":
            return True
        if allowed == "quick_one":
            if not job["slot"]:
                return True
            quick = [t for t, m, _ in slots(role, now) if m != "economy"]
            return bool(quick) and job["slot"] != quick[0]
    return False


def parse_slot(s):
    """Pure. "HH:MM" (every day) | "Wed 09:00" | "Mon,Thu 10:00" -> (frozenset of tm_wday or None, "HH:MM").
    Raises ValueError on anything else: a slot the launcher cannot read is an alarm, never a guess."""
    parts = str(s).split()
    if len(parts) not in (1, 2):
        raise ValueError("slot %r: want 'HH:MM' or 'Ddd[,Ddd] HH:MM'" % (s,))
    hhmm = parts[-1]
    hm = hhmm.split(":")
    if len(hm) != 2 or not all(x.isdigit() for x in hm) or int(hm[0]) > 23 or int(hm[1]) > 59:
        raise ValueError("slot %r: time %r is not HH:MM" % (s, hhmm))
    if len(parts) == 1:
        return None, hhmm
    days = set()
    for d in parts[0].split(","):
        if d.strip().title() not in WEEKDAYS:
            raise ValueError("slot %r: weekday %r is not one of %s" % (s, d, ",".join(WEEKDAYS)))
        days.add(WEEKDAYS.index(d.strip().title()))
    return frozenset(days), hhmm


def weekday(t):
    return time.localtime(t).tm_wday


def slots(role, day=None):
    """-> [(slot, mode, cap)] in schedule order; slot is the schedule's string ("09:00", "Wed 09:00"). day (an epoch)
    keeps only the slots that run on that local weekday, and marks a slot on `weekly_plan_weekday` mode "weekly"
    (the day's first run slot: the Producer's Wednesday run, which carries the weekly plan). Raises ValueError on an unreadable slot."""
    times = role.get("quick_checks_local") or role.get("runs_local") or []
    quick = "quick_token_cap" in role
    wk = role.get("weekly_plan_weekday")
    if wk and str(wk).title() not in WEEKDAYS:
        raise ValueError("weekly_plan_weekday %r is not one of %s" % (wk, ",".join(WEEKDAYS)))
    qcap = role.get("quick_token_cap") if role.get("quick_token_cap") is not None else role.get("run_token_cap")
    out = []
    for t in times:
        days, hhmm = parse_slot(t)
        if day is not None and days is not None and weekday(day) not in days:
            continue
        # a cap of 0 is a cap (the launch is then refused), never a fall-back to another cap (review night r3)
        if hhmm == role.get("economy_pass_local") and role.get("economy_token_cap") is not None:
            out.append((t, "economy", role["economy_token_cap"]))
        elif (day is not None and wk and weekday(day) == WEEKDAYS.index(str(wk).title())
              and not any(m == "weekly" for _, m, _ in out)):          # the day's first run slot only
            out.append((t, "weekly", qcap))
        else:
            out.append((t, "quick" if quick else "run", qcap))
    return out


def slot_epoch(now, slot):
    """The epoch of a slot ("HH:MM" or "Ddd HH:MM": the weekday is the caller's filter) on now's local day."""
    lt = time.localtime(now)
    h, m = (int(x) for x in str(slot).split()[-1].split(":"))
    return time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, h, m, 0, 0, 0, -1))


def day_of(t):
    return time.strftime("%Y-%m-%d", time.localtime(t))


def slot_key(day, slot):
    """The ONE done/run key of a scheduled slot: "YYYY-MM-DD <slot as the schedule writes it>" ("2026-10-28 07:30",
    "2026-10-28 Wed 07:30"). Writers (the due list) and readers (after_slots) both build it here, so a weekday slot's
    parent and dependent agree (review dispatcher-full #6)."""
    return "%s %s" % (day_of(day), slot)


def prev_day(now):
    """An epoch on the local CALENDAR day before now's (noon of it): now - 86400 lands two days back just after a
    spring-forward midnight (a 23-hour day) (review dispatcher-full #7). mktime normalises day 0 to the month before."""
    lt = time.localtime(now)
    return time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday - 1, 12, 0, 0, 0, 0, -1))


# ---------------------------------------------------------------- ledger events (event triggers)

def ledger_reading(read):
    """read() -> {"events": [event], "world": model.World} (read_ledger), or raises. -> the same dict with
    state MEASURED, or {"state": "UNMEASURED", "why"} when it raises, returns nothing, or returns an EMPTY ledger: a
    ledger of zero events is a blind instrument, never "no claims" (instrument_traps.md)."""
    try:
        r = read()
    except Exception as e:  # noqa: BLE001  (model.read raises on a malformed line: REPORTED, never skipped)
        return {"state": "UNMEASURED", "why": "the ledger is unreadable: %s: %s" % (type(e).__name__, str(e)[:160])}
    if not isinstance(r, dict) or not r.get("events") or r.get("world") is None:
        return {"state": "UNMEASURED", "why": "the ledger read returned no events (a blind read, not an empty ledger)"}
    return dict(r, state="MEASURED")


def _after(events, since):
    """(epoch, ev) for the events after `since`. The epoch is the event's `ts` second plus the microseconds of its
    `tsn`: two events on one item in the same second stay two (ROLE_EVENT_KEY_WIDEN_SAME_SECOND_TWINS); int(epoch)
    is still the ts second, which the int-second keys of a seen list written before the widening match."""
    for ev in events:
        t = utc_epoch(ev.get("ts"))
        if t is None:
            continue
        tsn = ev.get("tsn")
        if isinstance(tsn, int) and not isinstance(tsn, bool) and tsn > 0:
            t += (tsn % 10 ** 9 // 1000) / 1e6
        if t > since:
            yield t, ev


def done_claims(events, since):
    """Pure. The done claims since `since` (epoch), oldest first: a `rimflow implemented` event (the item reached
    built: published at a sha, every L0 criterion passing) or a `rimflow close` (closed against a commit) — the two
    forms a "done" claim takes on the ledger (arbiter.md "When you run"). -> [(epoch, id, verb)]."""
    return [(t, ev.get("id"), ev.get("event")) for t, ev in _after(events, since)
            if ev.get("event") in DONE_CLAIM_VERBS and ev.get("id")]


def on_plan(item, scope):
    """Is this item a step of the Producer's plan? scope (schedule `plan_scope`): "raised" = it was put at the top
    of a seat's `next` with `rimflow raise` (producer.md step 3, how the plan is written onto the ledger); "row" = it
    carries a V1 milestone row. No other ledger marker of the plan exists (2026-10-27)."""
    return bool(item) and (("raised" in scope and item.raised) or ("row" in scope and item.row))


def plan_failures(events, world, since, scope, world_filter=True):
    """Pure but for the World it is handed. A failed plan step since `since`, oldest first (producer.md: "an Arbiter
    FAIL or an item blocked on the critical path"): a `verify` run with result `fail` (an Arbiter FAIL once verdicts
    are binding; an advisory verdict is not on the ledger and blocks nothing) or a `block`, on an item still open and
    on the plan (on_plan). world_filter False: every such event, open or on the plan or not: what a run READ, so an
    event filtered out at that moment is never run later when its item joins the plan (review V, V5).
    -> [(epoch, id, "verify fail" | "block")]."""
    out = []
    for t, ev in _after(events, since):
        verb = ev.get("event")
        if verb == "block" or (verb == "verify" and ev.get("result") == "fail"):
            it = world.items.get(ev.get("id"))
            if not world_filter or (it is not None and it.open and on_plan(it, scope)):
                out.append((t, ev.get("id"), "block" if verb == "block" else "verify fail"))
    return out


def replan_requests(events, since, item, prefix):
    """Pure. Operations' replan requests since `since`: a `note` on `item` (the Producer's ledger_item, where the
    economy pass writes) whose text starts with `prefix` (schedule `replan_note_prefix`, operations.md).
    -> [(epoch, item, "replan request")]."""
    p = (prefix or "").strip().lower()
    return [(t, item, "replan request") for t, ev in _after(events, since)
            if p and ev.get("event") == "note" and ev.get("id") == item
            and str(ev.get("text") or "").strip().lower().startswith(p)]


def pending_events(role, lr, since, world_filter=True):
    """Pure. The role's `event_runs` kinds that have happened since `since`, oldest first (world_filter: plan_failures)."""
    out = []
    for kind in role.get("event_runs") or []:
        if kind == "plan_step_failure":
            out += plan_failures(lr["events"], lr["world"], since, role.get("plan_scope") or ["raised", "row"],
                                 world_filter)
        elif kind == "replan_request":
            out += replan_requests(lr["events"], since, role.get("ledger_item"), role.get("replan_note_prefix"))
        elif kind == "done_claims":
            out += done_claims(lr["events"], since)
        else:
            raise ValueError("event_runs kind %r is not one of plan_step_failure, replan_request, done_claims" % kind)
    return sorted(out)


def event_key(ev):
    """One ledger event's identity in a trigger list: (epoch, id, what) -> "S.UUUUUU|id|what", the epoch always to the
    microsecond (.000000 for an event with no tsn), so a list event_key wrote is never mistaken for a pre-widening one."""
    t, iid, what = ev
    return "%d.%06d|%s|%s" % (int(t), int(round((t - int(t)) * 1e6)), iid, what)


def legacy_key(ev):
    """The int-second key event_key wrote before the widening."""
    t, iid, what = ev
    return "%d|%s|%s" % (int(t), iid, what)


def role_events(role, lr, since, world_filter=False):
    """Pure. Everything this role's run reads after `since`, for events_seen: its event_runs kinds plus, for
    slot_when, the done claims (deduplicated, oldest first). Unfiltered by default: a run read the event whether or
    not its item was on the plan then (review V, V5); the world filter applies only when choosing a trigger."""
    out = set(pending_events(role, lr, since, world_filter))
    if role.get("slot_when") == "done_claims":
        out |= set(done_claims(lr["events"], since))
    return sorted(out)


def unseen(evs, rs):
    """The events not yet read by a run (or baselined). The cursor is a wall-clock time on THIS clone while an event's
    ts is its writer's: an event written on another clone before a launch can be ingested after it. So the window
    reaches EVENT_LOOKBACK_S behind the cursor and an event counts once by identity, not by ts (review round U, N4)."""
    seen = set(rs.get("events_seen") or [])
    # a list with no microsecond key was written before the widening: its int-second keys still cover the events
    # they named, so a deploy re-fires nothing; the next run rewrites it widened
    old = not any("." in k.split("|", 1)[0] for k in seen)
    return [e for e in evs if event_key(e) not in seen and not (old and legacy_key(e) in seen)]


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def read_ledger():
    """The ledger as every production reader sees it (model.read(), no argument: history + every shard) folded into
    a World. Raises on a malformed line (model.read reports, never skips)."""
    import importlib.util
    mod = sys.modules.get("rimflow_model_ro")
    if mod is None:
        spec = importlib.util.spec_from_file_location(
            "rimflow_model_ro", os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules["rimflow_model_ro"] = mod
    events = mod.read()
    return {"events": events, "world": mod.replay(events=events)}


def _usage_vals(result):
    """-> the usage dict and its four fields, or (None, None) when any is missing, not a whole non-negative number, or
    a bool: an absent field is unknown spend, never zero (review Q 8)."""
    u = result.get("usage") if isinstance(result, dict) else None
    if not isinstance(u, dict):
        return None, None
    vals = [u.get(k) for k in USAGE_KEYS]
    if not all(finite(v) and v >= 0 and float(v).is_integer() for v in vals):
        return None, None
    return u, dict(zip(USAGE_KEYS, (int(v) for v in vals)))


def raw_tokens(result):
    """Pure. The unweighted sum of the four usage fields (kept on the run for the record), or None (UNMEASURED)."""
    u, v = _usage_vals(result)
    return None if v is None else sum(v.values())


def run_tokens(result):
    """Pure. usage of a `claude -p --output-format json` result -> its cost in input-equivalent tokens (TOKEN_WEIGHTS),
    rounded up, or None (UNMEASURED) as _usage_vals. Cache writes are split by TTL from usage.cache_creation when its
    two parts are whole non-negative numbers adding up to cache_creation_input_tokens; otherwise every write is
    weighed at the dearer 1h rate (never a guess in the cheap direction). The run is failed and its spend counted at
    its budget when UNMEASURED."""
    u, v = _usage_vals(result)
    if v is None:
        return None
    cw = v["cache_creation_input_tokens"]
    w5, w1 = 0, cw
    split = u.get("cache_creation")
    if isinstance(split, dict):
        a, b = split.get("ephemeral_5m_input_tokens"), split.get("ephemeral_1h_input_tokens")
        if (all(finite(x) and x >= 0 and float(x).is_integer() for x in (a, b))
                and int(a) + int(b) == cw):
            w5, w1 = int(a), int(b)
    W = TOKEN_WEIGHTS
    tot = (v["input_tokens"] * W["input_tokens"] + w5 * W["cache_write_5m"] + w1 * W["cache_write_1h"]
           + v["cache_read_input_tokens"] * W["cache_read_input_tokens"] + v["output_tokens"] * W["output_tokens"])
    return int(math.ceil(tot))


def spent_today(rs, now):
    day = day_of(now)
    tot = 0
    for r in rs.get("runs") or []:
        if r.get("day") != day:
            continue
        tot += r["tokens"] if r.get("tokens") is not None else r.get("budget", 0)
    return tot


def prompt(role, mode, trigger, band_name, reading, budget, cap, factor, spent, unit):
    """The launch message. Every role but those whose schedule entry says `token_aware: true` (Operations; the
    Conductor, owner 2026-10-31) is token-blind (owner 2026-10-27): its message carries no band, runway, week, budget or cap,
    and no order to watch one (review T, F1). Nothing stops a run at its budget mid-run: the real bounds are
    `run_max_s` (wall time) and the after-the-fact accounting (supervise_roles), both the Dispatcher's (F2)."""
    lines = ["[RimFlow Dispatcher — a program, not a person; role launch %s]" % unit,
             "You are the RimFlow %s role, run headless by the Dispatcher. Read %s and do what it says for this "
             "trigger, then stop." % (role["name"], role["instructions"]),
             "Trigger: %s %s." % (mode, trigger)]
    if role.get("token_aware") is True:
        lines += ["Throttle band: %s (account runway %.2f %s, week left %.0f%% %s; ops_watch status at %s)." % (
                      band_name, reading["runway"], reading["runway_m"], reading["week_left"], reading["week_left_m"],
                      reading["at"]),
                  "Token budget for this run: %d weighted tokens (cap %d x %.1f); daily cap %d, %d already used today. "
                  "Weighted = input-equivalent: a cache read counts 0.1, a cache write 1.25 (5m) or 2 (1h), an "
                  "output token 5. The Dispatcher checks it after the run; it does not stop you at it." % (
                      budget, cap, factor, role.get("daily_token_cap") or 0, spent)]
    lines.append("You work as seat %s in %s. Never take the bridge, restart the game or deploy." % (
        role["seat"], role["clone"]))
    return "\n".join(lines)


# ---------------------------------------------------------------- decide (pure but for obs)

def supervise_roles(sch, st, obs, now, act):
    """Every persisted run still `running`, of every role (enabled or not, in the schedule or not), checked on every
    tick BEFORE anything can end the tick early: PAUSE, a blind `claude agents`, a disabled role (review Q 1). A run
    stays `running` (busy, its budget counted) until systemd says its unit is inactive/failed: a stop is re-issued
    every tick until then (review Q 2), and any other unit state ("unknown", a failed query) is UNMEASURED, busy and
    alarmed, never a finish (review Q 3). -> the set of role names with a run in flight."""
    rst = st.setdefault("roles", {})
    by_name = roles_by_name(sch)
    busy = set()
    for name, rs in sorted(rst.items()):
        if not isinstance(rs, dict):
            continue
        try:
            _supervise_one(name, rs, dict(ROLE_DEFAULTS, **(by_name.get(name) or {})), obs, now, act, busy)
        except Exception as e:  # noqa: BLE001 - one role's bad run or value never stops the others' supervision (V3)
            busy.add(name)      # unknown: kept busy, never launched over
            act(do="alarm", kind="role:%s:supervise" % name, ticket=(by_name.get(name) or {}).get("ledger_item"),
                note=True, why="role %s supervision raised %s: %s; its runs are kept as running and checked again "
                "next tick" % (name, type(e).__name__, str(e)[:200]))
    return busy


def roles_by_name(sch):
    """{name: role} over the schedule's roles entries that are mappings; anything else is skipped here (decide_roles
    alarms it), so one malformed entry cannot raise through the tick (review V, V3)."""
    return {r.get("name"): r for r in sch.get("roles") or [] if isinstance(r, dict)}


def decide_order(roles):
    """Pure. Roles in decide order: each after the role its after_role names (whole chains, not just one level:
    review night r3), otherwise schedule order. A cycle or a name not in the list ends the chain."""
    by = {r.get("name"): r for r in roles}

    def depth(r):
        seen, d = set(), 0
        while r.get("after_role") in by and r.get("name") not in seen:
            seen.add(r.get("name"))
            r, d = by[r["after_role"]], d + 1
        return d
    return sorted(roles, key=depth)


def max_s_of(run, cfg):
    """A run's wall-time bound: its recorded run_max_s, else the role's run_max_s + pre_launch_max_s, else the
    default, whichever is first a positive number (a None or 0 from an older schedule never reaches a comparison:
    review V, V3). pre_launch_max_s (ARBITER_MEASURE_PRELAUNCH_EVIDENCE_TIME) is the pre-steps' own budget: the
    bound counts from launch, so without it the pre-steps would eat the role's run_max_s."""
    role_max = cfg.get("run_max_s")
    if _num(role_max) and role_max > 0 and _num(cfg.get("pre_launch_max_s")):
        role_max += cfg["pre_launch_max_s"]
    for v in (run.get("run_max_s"), role_max, ROLE_DEFAULTS["run_max_s"]):
        if _num(v) and v > 0:
            return v
    return ROLE_DEFAULTS["run_max_s"]


def _supervise_one(name, rs, cfg, obs, now, act, busy):
    """One role's persisted runs (supervise_roles' body, guarded per role there)."""
    for run in rs.get("runs") or []:
        if run.get("state") != "running":
            continue
        ustate = obs["unit_state"](run["unit"])
        if ustate in ACTIVE and not run.get("scope") and obs.get("scope"):
            # a run recorded before the scope was named at creation (no `marker`): learn claude_bounded's
            # MainPID-named scope while the unit's MainPID still exists (review round R, D)
            run["scope"] = obs["scope"](run["unit"], run.get("seat") or cfg.get("seat"))
        if ustate in TERMINAL:
            ustate = ended(run, ustate, obs)
        if ustate not in TERMINAL:
            busy.add(name)
            if ustate.startswith("unit "):
                act(do="alarm", kind="role:%s:scope" % name, ticket=run.get("item"), note=True,
                    why="%s run %s: %s; kept as running, checked again next tick" % (name, run["unit"], ustate))
            elif ustate not in ACTIVE:
                act(do="alarm", kind="role:%s:unit" % name, ticket=run.get("item"), note=True,
                    why="%s run %s unit state UNMEASURED (%s): kept as running, retried next tick"
                    % (name, run["unit"], ustate))
            max_s = max_s_of(run, cfg)
            if now - run["at"] >= max_s:
                tries = run.get("stop_tries", 0)
                run["stop_tries"] = tries + 1
                act(do="role_stop", role=name, unit=run["unit"], scope=run.get("scope"),
                    unit_gone=ustate.startswith("unit "),     # stop the scope alone: the unit was collected
                    marker=run.get("marker"), force=tries >= 2,     # TERM the run's stray processes, KILL from #3
                    since=run.get("at"),
                    seat=run.get("seat") or cfg.get("seat"), ticket=run.get("item"), note=tries == 0,
                    why="%s run %s still %s after %d s (run_max_s %d): stop #%d" % (
                        name, run["unit"], ustate, now - run["at"], max_s, tries + 1))
                if tries == 0:
                    act(do="alarm", kind="role:%s:overtime" % name, ticket=run.get("item"), note=True,
                        why="%s run %s passed run_max_s %d" % (name, run["unit"], max_s))
                else:
                    act(do="alarm", kind="role:%s:stop_failed" % name, ticket=run.get("item"), note=True,
                        why="%s run %s still %s after %d stop(s): NOT confirmed stopped, kept as running"
                        % (name, run["unit"], ustate, tries))
            continue
        res = obs["result"](run)
        tok = run_tokens(res)
        run["tokens"] = tok                     # input-equivalent (TOKEN_WEIGHTS): what caps and spend read
        run["raw_tokens"] = raw_tokens(res)     # the unweighted sum, for the record only
        run["token_unit"] = TOKEN_UNIT          # a run without it predates the weighting (its tokens are raw)
        run["state"] = "failed" if (not isinstance(res, dict) or res.get("is_error") or tok is None) else "done"
        res = res if isinstance(res, dict) else {}
        models = sorted(res.get("modelUsage") or {})
        act(do="role_done", role=name, unit=run["unit"], ticket=run.get("item"), note=True,
            why="%s %s run %s %s%s: %s weighted tokens of a %d budget (raw %s), model %s, %s" % (
                name, run.get("mode"), run["unit"], run["state"],
                " (after %d stop(s))" % run["stop_tries"] if run.get("stop_tries") else "",
                tok if tok is not None else "UNMEASURED (counted at its budget)",
                run.get("budget") or 0, run["raw_tokens"] if run["raw_tokens"] is not None else "?",
                ",".join(models) or "?",
                # an auth failure reports subtype `success` with is_error: "failed ... success" hid it on 10-30
                "%s%s" % (res.get("subtype") or "no result",
                          " but is_error (%s)" % (res.get("terminal_reason") or "?") if res.get("is_error") else "")),
            # a token-blind role reads its ledger item: its note is a FIXED outcome (blind_note), never the result's
            # subtype or text; the journal and Operations' item keep `why` (review dispatcher-full #2)
            blind=blind(name, "completed" if run["state"] == "done" else "failed", run.get("mode"), run["unit"]))
        if run["state"] == "done" and name in STRUCTURED:
            harvest(name, run, res, act)
        if run["state"] == "done" and name in FINISH_STAMP:
            act(do="role_stamp", role=name, unit=run["unit"], ticket=run.get("item"), path=FINISH_STAMP[name],
                at=run["at"], why="%s run %s finished done: its window ends at its launch %s" % (
                    name, run["unit"], iso(run["at"])))
        if tok is not None and tok > (run.get("budget") or 0):
            act(do="alarm", kind="role:%s:overbudget" % name, ticket=run.get("item"), note=True,
                why="%s run %s used %d weighted tokens (raw %s), budget %d" % (
                    name, run["unit"], tok, run["raw_tokens"], run.get("budget") or 0))
        if run["state"] == "failed":
            text = res.get("result") or run.get("err_tail") or ""
            back = auth_failed_back(rs, run, text, now)
            act(do="alarm", kind="role:%s:failed" % name, ticket=run.get("item"), note=True, conductor_log=True,
                raise_first="%s run failed%s." % (name, ": its slot is given back, it reruns once the login works"
                                                  if back else ""),
                # a blind role's item gets the fixed line only: the result text is outside text (a usage-limit
                # message names no token word); the full why goes to Operations' item (dispatcher.route_note)
                blind=blind(name, "failed", run.get("mode"), run["unit"]),
                why="%s run %s ended without a good result (%s)" % (
                    name, run["unit"], ("usage UNMEASURED: " if res and tok is None else "")
                    + (text or "no result file")[:160]))
    rs["runs"] = [r for r in rs.get("runs") or [] if r.get("state") == "running" or now - r["at"] < 2 * 86400]


def auth_failed_back(rs, run, text, now):
    """A run killed by a lost login did no work: its slot, alarm mark and event cursor go back so it runs again
    (10-30: three such runs spent the day's alarm and event limits). At most AUTH_BACKS_PER_DAY per role, so a login
    that fails only for role runs cannot loop. -> True when given back."""
    used = rs.get("auth_backs") if (rs.get("auth_backs") or {}).get("day") == day_of(now) else {"day": day_of(now), "n": 0}
    p = run.get("consumed")
    if not (p and AUTH_RX.search(str(text))) or used["n"] >= AUTH_BACKS_PER_DAY or rs.get("pending_launch"):
        return False
    if any(r.get("at", 0) > run["at"] for r in rs.get("runs") or []):    # a later run already moved the marks
        return False
    rs["pending_launch"] = p
    if not unlaunch(rs, run["unit"]):
        rs.pop("pending_launch", None)
        return False
    used["n"] += 1
    rs["auth_backs"] = used
    run.pop("consumed", None)
    return True


def harvest(name, run, res, act):
    """Pure but for act. A done STRUCTURED run's result -> one role_verdicts action carrying its valid entries (the
    append happens in dispatcher.execute, so a dry run writes nothing), one :verdict_refused alarm journaling every
    invalid entry whole with its errors, or one :verdicts alarm when structured_output is missing or misshapen.
    Alarms are noted without blind text: they carry outside text, so route_note sends them to Operations' item."""
    spec = dict(STRUCTURED[name])
    trial = spec.get("trial_sink") and " run-now trial " in str(run.get("slot") or "")
    if trial:
        spec["sink"] = spec["trial_sink"]
    key, unit, item = spec["key"], run.get("unit"), run.get("item")
    so = res.get("structured_output") if isinstance(res, dict) else None
    entries = so.get(key) if isinstance(so, dict) and set(so) == {key} else None
    if not isinstance(entries, list):
        act(do="alarm", kind="role:%s:verdicts" % name, ticket=item, note=True,
            why="%s run %s finished done without a usable structured_output (%s): nothing appended to %s; its "
                "claims stay pending" % (name, unit, "absent" if so is None else
                                         "keys %s, want {%s: [...]}" % (sorted(so) if isinstance(so, dict)
                                                                       else type(so).__name__, key), spec["sink"]))
        return
    try:
        from contracts import models as CM
        model = getattr(CM, spec["model"])
    except Exception as e:  # noqa: BLE001 - no validator: nothing is appended unvalidated
        act(do="alarm", kind="role:%s:verdicts" % name, ticket=item, note=True,
            why="%s run %s: contracts.models.%s unavailable (%s: %s): %d entries NOT appended" % (
                name, unit, spec["model"], type(e).__name__, str(e)[:120], len(entries)))
        return
    good, bad = [], []
    for e in entries:
        errs = CM.errors(model, e)
        (bad if errs else good).append((e, errs))
    if good:
        act(do="role_verdicts", role=name, unit=unit, path=spec["sink"], rows=[e for e, _ in good],
            why="%s run %s: %d %s appended to %s" % (name, unit, len(good), key, spec["sink"]))
        for e, _ in good if spec.get("note_each") else ():
            act(do="role_verdict_note", role=name, unit=unit, ticket=e["item"], note=True,
                why="%s%s verdict (advisory: it blocks nothing and sends nothing back) on %s at sha %s: %s; causes: %s; "
                    "evidence: %s; run %s; record %s" % (
                        "TRIAL " if trial else "", name, e["item"], e["sha"], e["disposition"],
                        ", ".join(e.get("causes") or []) or "none", "; ".join(e.get("evidence") or []) or "none",
                        unit, spec["sink"]))
    if bad:
        act(do="alarm", kind="role:%s:verdict_refused" % name, ticket=item, note=True,
            refused=[e for e, _ in bad],
            why="%s run %s: %d of %d %s refused by contracts.models.%s, NOT appended (their claims stay pending): %s"
                % (name, unit, len(bad), len(entries), key, spec["model"], "; ".join(
                    "%s: %s" % (e.get("item") if isinstance(e, dict) else repr(e)[:40], ", ".join(errs)[:200])
                    for e, errs in bad)[:600]))


def append_verdicts(path, rows):
    """Append rows, one JSON line each, to path (its directory made), in ONE write of the whole batch with O_APPEND,
    then fsync: a reader never sees half a batch's line. Raises OSError (dispatcher.execute alarms it)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        n = os.write(fd, data)
        if n != len(data):
            raise OSError("short write to %s: %d of %d bytes" % (path, n, len(data)))
        os.fsync(fd)
    finally:
        os.close(fd)


# ---- notes for a token-blind role's ledger item (review dispatcher-full #2). A blind item gets ONLY a text built
# here from closed sets: a known role name, a known mode, a dispatcher unit name, and a fixed outcome. Reasons, error
# output, exception text, result subtypes and triggers (alarm keys, ledger event text) are outside text that can
# carry an account id or a figure in words no token list knows: they go to the journal and Operations' item only.
# The closed sets and the renderer live in contracts.blind_core (stdlib only; the 2-minute tick imports it), with a
# pydantic twin contracts.blind.BlindNote (BLINDVIEW_BUILD_CLOSED_TYPE_LEAKPROOF). These names stay for callers.
_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.append(_SRC)
from contracts import blind_core as _BC  # noqa: E402

BLIND_ROLES = _BC.NOTE_ROLES
BLIND_MODES = _BC.NOTE_MODES
BLIND_OUTCOMES = _BC.NOTE_OUTCOMES


def blind(role, outcome, mode=None, unit=None):
    """An action's blind-note fields (dispatcher.route_note renders them with blind_note)."""
    return {"role": role, "outcome": outcome, "mode": mode, "unit": unit}


def blind_note(b):
    """Pure. -> the fixed text for a blind item, or None when ANY field is outside its closed set (the note then goes
    to Operations' item, never to the blind one). "dispatcher: Conductor quick run: completed" (the unit name is
    never in the text: its digits are a payload a blind page must not carry). contracts.blind_core.note_text."""
    return _BC.note_text(b)


def ended(run, ustate, obs):
    """The unit is inactive/failed. -> ustate (terminal) only when the run's termination is POSITIVELY established,
    else a "unit ..." reason it is still busy (review dispatcher-full #1). claude lives in claude_bounded's scope,
    outside the unit (its shell traps TERM), so the unit ending is not claude ending:
      - the scope, named at creation (role_scope: claude-seat-<seat>-<unit>.scope, persisted with the run before
        systemd-run), must be inactive/failed too; and
      - no process may still carry the run's RM_ROLE_UNIT=<unit> marker (procs_of: claude and every child inherit
        it), which also covers a clone whose claude_bounded.sh predates CLAUDE_SCOPE_UNIT and named the scope by
        PID. The scan UNMEASURED is busy, never a finish.
    A run recorded before markers existed has only its scope; with no scope resolved it is never retired by the
    clock any more (the old run_max_s "UNCONFIRMED" retirement let a surviving claude overlap the next run)."""
    scope = run.get("scope")
    if not scope:
        return "unit %s, scope never resolved: termination UNCONFIRMED, kept busy (stop claude-seat-%s-* by hand)" \
            % (ustate, run.get("seat") or "?")
    sstate = obs["unit_state"](scope)
    if sstate not in TERMINAL:
        return "unit %s but scope %s %s" % (ustate, scope, sstate)
    if run.get("marker"):
        n = obs["procs"](run["marker"], since=run.get("at")) if obs.get("procs") else None
        n = len(n) if isinstance(n, list) else n
        if n is None:
            return "unit %s, scope %s %s, its process check UNMEASURED" % (ustate, scope, sstate)
        if n:
            return "unit %s, scope %s %s, but %d process(es) marked RM_ROLE_UNIT=%s still run" % (
                ustate, scope, sstate, n, run["marker"])
    return ustate


def after_slots(after_cfg, job, now):
    """Pure. The after_role's slots this scheduled job may follow, newest first: its slots at or before the job's slot
    today, then the previous calendar day's (prev_day) after the job's slot time (24 h back at most). -> slot_key()s
    ("YYYY-MM-DD HH:MM" / "YYYY-MM-DD Wed HH:MM", the done/run keys), empty when it has no slots."""
    mine = slot_epoch(now, job["slot"])
    keys = []
    for day in (now, prev_day(now)):
        for t, _, _ in slots(after_cfg, day):
            e = slot_epoch(day, t)
            if mine - 86400 < e <= mine:
                keys.append((e, slot_key(day, t)))
    return [k for _, k in sorted(keys, reverse=True)]


def after_ready(cfg, rst, busy, job, now, after_cfg=None):
    """`after_role` (Conductor: "each after an Operations run", conductor.md; Producer: after the economy pass): a
    scheduled slot waits until that role's OWN scheduled run for the slot it follows (after_slots: Conductor 08:00 ->
    Operations 07:30 today, 20:00 -> 19:30) finished done, and none of its runs is in flight. A slot of that role the
    band skipped on purpose (done "band X": Operations' 07:30 in AMBER/RED) is passed over for its previous slot within
    24 h (review T, F4: the Producer's 09:00 then follows the 19:30 run). An alarm run, or yesterday's run launched
    late, never counts (review round R, B). A parent that is not enabled holds every scheduled slot (review
    dispatcher-full #4). -> None when ready, else why it waits."""
    after = cfg.get("after_role")
    if not after or not job["slot"]:
        return None
    if not (after_cfg or {}).get("enabled"):
        # a disabled parent holds its dependent: a run it finished before it was disabled does not stand in for the
        # checks it no longer makes (review dispatcher-full #4)
        return "%s is not enabled" % after
    if after in busy:
        return "an %s run is still going" % after
    keys = after_slots(after_cfg or {}, job, now)
    if not keys:
        return "%s has no scheduled slots to follow" % after
    ars = rst.get(after) or {}
    skipped = []
    for key in keys:
        mine = [r for r in ars.get("runs") or [] if r.get("slot") == key and r.get("mode") != "alarm"]
        if any(r.get("state") == "done" for r in mine):
            return None
        if mine:
            return "the %s %s run ended %s" % (after, key, mine[-1].get("state"))
        how = (ars.get("done") or {}).get(key)
        if how and str(how).startswith("band "):
            skipped.append(key)
            continue
        if how:
            return "the %s %s slot was not run (%s)" % (after, key, how)
        return "the %s %s run has not run yet" % (after, key)
    return "every %s slot in the last 24 h was skipped by its band (%s)" % (after, ", ".join(skipped))


def decide_roles(sch, st, obs, now, act, busy=None, gate=None):
    """Mutates st["roles"]; calls act(**kw) per action. obs needs: ops() -> status dict|None, account() -> label|None,
    unit_state(unit) -> str, result(run) -> dict|None, off(path) -> first line|None, and, for a role with
    `slot_when` or `event_runs`, ledger() -> read_ledger()'s dict (or raises). busy = supervise_roles()'s
    answer (run here when the caller did not). gate("role_launch") -> (go, pick) is the dispatcher's account pick
    (account_pick.py), asked last, at the moment of release: a held launch keeps its slot due (it is missed only
    after slot_late_s, like any wait)."""
    if busy is None:
        busy = supervise_roles(sch, st, obs, now, act)
    rst = st.setdefault("roles", {})
    by_name = roles_by_name(sch)
    reading_cache = {}
    tick_launch = {}      # role -> the unit decide is launching now, until its role_launch action is built (V7)

    def reading():
        # one status.json read per tick: the alarm keys come from the same snapshot the reading judged (review night r3)
        if "r" not in reading_cache:
            reading_cache["s"] = obs["ops"]()
            reading_cache["r"] = ops_reading(reading_cache["s"], obs["account"](), now,
                                             sch.get("ops_stale_s", OPS_STALE_S))
        return reading_cache["r"]

    def ledger():
        """One ledger read per tick, shared by every role that triggers on it. UNMEASURED: one alarm per outage
        (st["ledger_blind"]), and the roles that need it launch nothing until it reads again."""
        if "l" not in reading_cache:
            lr = ledger_reading(obs.get("ledger") or (lambda: None))
            if lr["state"] != "MEASURED":
                if not st.get("ledger_blind"):
                    act(do="alarm", kind="role:ledger", note=True,
                        why="ledger UNMEASURED (%s): the roles that trigger on ledger events launch nothing until it "
                        "reads again; alarmed once per outage" % lr["why"])
                st["ledger_blind"] = lr["why"]
            elif st.pop("ledger_blind", None):
                act(do="role_hold", role="*", why="ledger readable again (%d events): event triggers resume"
                    % len(lr["events"]))
            reading_cache["l"] = lr
        return reading_cache["l"]

    # a role that runs after another is decided after it, so the one it follows is marked/launched first (R, B)
    bad = [r for r in sch.get("roles") or [] if not isinstance(r, dict)]
    if bad:
        act(do="alarm", kind="role:schedule", note=True,
            why="%d roles entr(y/ies) in the schedule are not mappings (%s): skipped; the other roles are decided"
            % (len(bad), ", ".join(type(r).__name__ for r in bad)))
    roles = decide_order([r for r in sch.get("roles") or [] if isinstance(r, dict)])
    def one(role):
        name = role.get("name", "?")
        req = (rst.get(name) or {}).get("run_now") if isinstance(rst.get(name), dict) else None
        if not role.get("enabled") and not req:
            return
        missing = [k for k in LAUNCH_KEYS if not role.get(k)]
        if missing:
            act(do="alarm", kind="role:" + name, note=True, conductor_log=True, why="role %s is enabled but cannot be launched: no %s in the schedule"
                % (name, ", ".join(missing)))
            return
        cfg = dict(ROLE_DEFAULTS, **role)
        if role.get("enabled") and cfg.get("after_role") and not (by_name.get(cfg["after_role"]) or {}).get("enabled"):
            act(do="alarm", kind="role:%s:after" % name, ticket=role["ledger_item"], note=True,
                blind=blind(name, "after_disabled"),
                why="role %s runs only after a %s run, and %s is not enabled: its scheduled checks will not run"
                % (name, cfg["after_role"], cfg["after_role"]))
        rs = rst.setdefault(name, {})
        rs.setdefault("done", {})
        rs.setdefault("runs", [])
        try:
            validate_role(cfg)
            today = slots(cfg, now)
            if cfg.get("after_role"):
                slots(dict(ROLE_DEFAULTS, **(by_name.get(cfg["after_role"]) or {})), now)
        except ValueError as e:
            act(do="alarm", kind="role:%s:schedule" % name, ticket=role["ledger_item"], note=True,
                blind=blind(name, "schedule_unreadable"),
                why="role %s NOT RUN: its schedule entry is unreadable: %s" % (name, e))
            return
        # ---- the ledger, for a role that triggers on its events (Arbiter: done claims; Producer: plan-step
        # failures, replan requests). Blind: this role launches nothing this tick, not even a clock slot.
        lr = None
        if (cfg.get("slot_when") or cfg.get("event_runs")) and not req:      # a run-now reads no ledger, moves no cursor
            lr = ledger()
            if lr["state"] != "MEASURED":
                return
            if "event_cursor" not in rs:
                # first MEASURED tick with the role enabled: the baseline. Events before it are not run as events;
                # the role's next scheduled run reads them (its instructions say so).
                rs["event_cursor"] = now
                rs["events_seen"] = [event_key(e) for e in role_events(cfg, lr, now - EVENT_LOOKBACK_S)]
                act(do="role_hold", role=name, why="%s event triggers: baseline set at %s; ledger events after it "
                    "trigger" % (name, iso(now)))
        # ---- what is due now
        due = []
        for i, (hhmm, mode, cap) in enumerate([] if req else today):      # a run-now goes first; slots next tick
            key = slot_key(now, hhmm)
            t = slot_epoch(now, hhmm)
            if key in rs["done"] or now < t:
                continue
            if now - t > cfg["slot_late_s"]:
                rs["done"][key] = "missed"
                act(do="role_hold", role=name, why="%s slot %s missed (tick %d s late > slot_late_s)%s"
                    % (name, hhmm, now - t, ("; it waited: " + rs["waiting"][1]) if (rs.get("waiting") or [None])[0]
                       == key else ""))
                continue
            due.append({"key": key, "slot": hhmm, "first": i == 0, "mode": mode, "cap": cap,
                        "item": role["ledger_item"], "trigger": "slot %s local%s" % (
                            hhmm, " (weekly plan, %s)" % cfg["weekly_plan_weekday"] if mode == "weekly" else "")})
        if role.get("alarm_runs") and not req:
            # alarms_seen holds the OPEN alarms a run already covered (or a band/cap/off switch passed over). It is
            # pruned to what is open now, so an alarm that clears is eligible again when it re-crosses (review W, W1).
            # Read only from a MEASURED reading with a readable alarms dict: a blind one would prune every key and
            # re-run every open alarm when it reads again (review R, C). No baseline: alarms already open when the
            # role is first enabled run once. One alarm run covers every unseen open alarm, at most one per
            # alarm_run_gap_s.
            open_items = alarm_reading((reading_cache["s"] or {}).get("alarms")) if reading()["state"] == "MEASURED" \
                else None
            if open_items is None:
                if not rs.get("alarm_blind"):
                    act(do="role_hold", role=name, why="%s alarm runs held: %s; none launches until both read" % (
                        name, reading()["why"] if reading()["state"] != "MEASURED"
                        else "ops_watch alarms unreadable in status.json"))
                rs["alarm_blind"] = True
            else:
                rs.pop("alarm_blind", None)
                rs["alarms_seen"] = [k for k in rs.get("alarms_seen") or [] if k in open_items]
                fresh = [k for k in open_items if k not in rs["alarms_seen"]]
                # daily limits, held as data in the schedule (review X, X1): at most alarm_runs_per_alarm_per_day runs
                # for one alarm key and alarm_runs_per_day alarm runs in all, so a flapping alarm cannot make a paid
                # run every cycle. Absent = no limit. Limited keys stay unseen: they wait for tomorrow (or clearing).
                ad = rs.get("alarm_day") if (rs.get("alarm_day") or {}).get("day") == day_of(now) else \
                    {"day": day_of(now), "n": 0, "keys": {}}
                per_key, per_day = cfg.get("alarm_runs_per_alarm_per_day"), cfg.get("alarm_runs_per_day")
                if fresh and per_day is not None and ad["n"] >= int(per_day):
                    capped = fresh
                    fresh = []
                elif fresh and per_key is not None:
                    capped = [k for k in fresh if ad["keys"].get(k, 0) >= int(per_key)]
                    fresh = [k for k in fresh if k not in capped]
                else:
                    capped = []
                if capped and rs.get("alarm_limit_hold") != [day_of(now)] + capped:     # journal each set once a day
                    rs["alarm_limit_hold"] = [day_of(now)] + capped
                    act(do="role_hold", role=name, why="%s alarm run for %s waits: the daily alarm-run limit is used "
                        "(alarm_runs_per_alarm_per_day %s, alarm_runs_per_day %s); the scheduled running checks read "
                        "it" % (name, ", ".join(capped), per_key, per_day))
                gap = int(cfg.get("alarm_run_gap_s", ALARM_RUN_GAP_S))
                last = rs.get("alarm_last_run")
                if fresh and last is not None and now - last < gap:
                    if rs.get("alarm_gap_hold") != fresh:          # journal each waiting set once
                        act(do="role_hold", role=name, why="%s alarm run for %s waits: the last alarm run was %d s "
                            "ago (alarm_run_gap_s %d)" % (name, ", ".join(fresh), now - last, gap))
                    rs["alarm_gap_hold"] = fresh
                elif fresh:
                    rs.pop("alarm_gap_hold", None)
                    # an account alarm has no ledger item (it is Operations' alone, never on a seat queue: review V,
                    # V2): its run notes on the role's own ledger_item; mark() records every key the run covers
                    item = fresh[0]
                    due.append({"key": "alarm " + item, "slot": None, "first": False, "mode": "alarm",
                                "cap": cfg.get("run_token_cap"), "seen": fresh,
                                "item": role["ledger_item"] if item.startswith(ALARM_KEY_PREFIX) else item,
                                "trigger": "ops_watch alarm " + ", ".join(fresh)})
        if cfg.get("event_runs") and not req:
            try:
                pend = unseen(pending_events(cfg, lr, rs["event_cursor"] - EVENT_LOOKBACK_S), rs)
            except ValueError as e:
                act(do="alarm", kind="role:%s:schedule" % name, ticket=role["ledger_item"], note=True,
                    blind=blind(name, "events_unreadable"), why="role %s NOT RUN: %s" % (name, e))
                return
            per_day = int(cfg.get("event_runs_per_day", 1))
            used = [k for k in rs["done"] if k.startswith(day_of(now) + " event")]
            if pend and len(used) < per_day:
                t0, iid, what = pend[0]
                due.append({"key": "%s event#%d" % (day_of(now), len(used) + 1), "slot": None, "first": False,
                            "mode": "event", "cap": cfg.get("run_token_cap"), "item": role["ledger_item"],
                            "trigger": "ledger event: %s on %s at %s%s" % (
                                what, iid, iso(t0), (" (+%d more since %s)" % (len(pend) - 1, iso(rs["event_cursor"])))
                                if len(pend) > 1 else "")})
            elif pend and rs.get("event_cap_day") != day_of(now):
                rs["event_cap_day"] = day_of(now)
                act(do="role_hold", role=name, why="%s: %d ledger event(s) pending, event_runs_per_day %d used: the "
                    "next run reads them" % (name, len(pend), per_day))
        rs["done"] = {k: v for k, v in rs["done"].items() if k[:10] >= day_of(now - 2 * 86400)}
        if req:
            if now - float(req.get("at") or 0) > RUN_NOW_TTL_S:
                refuse_now(rs, "expired", now)
                act(do="role_hold", role=name, why="%s run-now by %s (%s) expired: not launchable for %d s (busy or "
                    "held); ask again" % (name, req.get("by"), req.get("why"), RUN_NOW_TTL_S))
                return
            due = [run_now_job(cfg, req, now)]
        if not due:
            return
        job = due[0]                                      # one launch per role per tick
        off = obs["off"](wsl_path(role.get("off_file") or ""))
        if off is not None:
            sk = skip_event(rs, job, "off")
            if sk is None:
                mark(rs, job, "off")
            elif not sk:
                return
            refuse_now(rs, "off switch", now, job)
            act(do="role_hold", role=name, why="%s %s skipped: off switch %s (%s)" % (
                name, job["trigger"], role.get("off_file"), off or "no reason given"))
            return
        if name in busy:
            return                                      # one run at a time: wait for the running one
        if cfg.get("window_name") and obs.get("window_live"):
            # a standing window of this role (Conductor: the Remote Control window, conductor.md) writes the findings
            # itself: no headless `claude -p` beside it. Held, not marked: the slot waits (missed after slot_late_s).
            # Unreadable holds too. Journaled once per slot, not every tick.
            live, why = obs["window_live"](cfg["window_name"])
            if live is not False:
                if rs.get("window_hold") != job["key"]:
                    rs["window_hold"] = job["key"]
                    act(do="role_hold", role=name, why="%s %s not launched: %s (%s)" % (
                        name, job["trigger"], "conductor window live" if live else "window UNMEASURED",
                        "%s; the window does the check" % why if live else why))
                return
            rs.pop("window_hold", None)
        if job["slot"] and cfg.get("slot_when") == "done_claims":
            claims = unseen(done_claims(lr["events"], rs["event_cursor"] - EVENT_LOOKBACK_S), rs)
            if not claims:
                mark(rs, job, "no done claims")
                act(do="role_hold", role=name, why="%s %s not run: no done claim (implemented/close) since %s" % (
                    name, job["trigger"], iso(rs["event_cursor"])))
                return
            job["trigger"] += ", %d done claim(s) since %s (oldest %s %s)" % (
                len(claims), iso(rs["event_cursor"]), claims[0][2], claims[0][1])
        if job["slot"] and cfg.get("slot_when") == "pending_work":
            # state, not a cursor: nothing is consumed, so work a launch did not finish is pending at the next slot
            # (ARBITER_BUILD_LAUNCH_ON_ANY_PENDING_WORK). Unreadable stores: launch, since work may be pending. No cutoff
            # stamp: HOLD with an alarm, since launching would hand the Arbiter the whole pre-enable backlog
            # (ARBITER_DECIDE_BACKLOG_NEVER_DRAINS).
            try:
                stores = obs["pending_stores"]() if obs.get("pending_stores") else None
                if stores is None:
                    raise OSError("no pending_stores reader in obs")
                pend = PW.pending(lr, stores, now, cfg.get("pending_work") or PW.KINDS)
                what = PW.summary(pend)
            except PW.NoCutoff as e:
                mark(rs, job, "no cutoff")
                act(do="alarm", kind="role:%s:cutoff" % name, ticket=job["item"], note=True,
                    why="%s %s not run: %s" % (name, job["trigger"], e))
                return
            except (OSError, ValueError) as e:
                pend, what = True, "work stores UNMEASURED (%s), launched since work may be pending" % e
            if not pend:
                mark(rs, job, "nothing pending")
                act(do="role_hold", role=name, why="%s %s not run: nothing pending (%s)" % (
                    name, job["trigger"], ", ".join(cfg.get("pending_work") or PW.KINDS)))
                return
            job["trigger"] += ", pending: " + what
        wait = after_ready(cfg, rst, busy, job, now, dict(ROLE_DEFAULTS, **(by_name.get(cfg.get("after_role")) or {})))
        if wait:
            if (rs.get("waiting") or [None])[0] != job["key"]:      # journal the wait once, not every tick
                act(do="role_hold", role=name, why="%s %s waits: runs after a finished %s run; %s" % (
                    name, job["trigger"], cfg["after_role"], wait))
            rs["waiting"] = [job["key"], wait]
            return
        rs.pop("waiting", None)
        r = reading()
        if r["state"] != "MEASURED":
            refuse_now(rs, "ops reading " + r["state"], now, job)
            act(do="alarm", kind="role:%s:ops" % name, ticket=job["item"], note=True,
                why="%s %s REFUSED: %s" % (name, job["trigger"], r["why"]))
            return
        bname, b = band(cfg, r)
        allowed = b.get("slots", "all")
        if slot_blocked(allowed, job, cfg, now):
            sk = skip_event(rs, job, "band " + bname)
            if sk is None:
                mark(rs, job, "band " + bname)
            elif not sk:
                return
            refuse_now(rs, "band " + bname, now, job)
            act(do="role_hold", role=name, why="%s %s not run: band %s runs %s scheduled slots (runway %.2f %s, "
                "week left %.0f%%)" % (name, job["trigger"], bname, allowed, r["runway"], r["runway_m"],
                                       r["week_left"]))
            return
        factor = float(b.get("quick_cap_x", 1.0)) if job["mode"] in ("quick", "run", "weekly", "event") else 1.0
        if not job["cap"]:
            refuse_now(rs, "no cap", now, job)
            act(do="alarm", kind="role:" + name, note=True, conductor_log=True, why="role %s has no token cap for %s" % (name, job["mode"]))
            return
        budget = int(job["cap"] * factor)
        spent = spent_today(rs, now)
        daily = role.get("daily_token_cap")           # 0 is a cap of zero; only absent (None) is no cap
        if daily is not None and (job["mode"] in ("event", "alarm") or job.get("manual")):
            # (an alarm run reserves too: it may spend only what the day's scheduled runs leave, review X, X1)
            # the day's scheduled runs not yet run keep their budget: an event run may spend only what they leave,
            # so it can never make the 09:00 (Wednesday: the weekly plan) refuse on the daily cap (review U, N3)
            # a slot this band will block never runs, so it reserves nothing (review V, V6)
            reserve = sum(int(c * (float(b.get("quick_cap_x", 1.0)) if m in ("quick", "run", "weekly") else 1.0))
                          for i, (hh, m, c) in enumerate(today if role.get("enabled") else [])
                          if c and slot_key(now, hh) not in rs["done"]
                          # a run-now does not keep budget for a slot already past its late window (it never runs)
                          and not (job.get("manual") and now - slot_epoch(now, hh) > float(cfg["slot_late_s"]))
                          and not slot_blocked(allowed, {"slot": hh, "first": i == 0, "mode": m}, cfg, now))
            if job.get("manual") and spent + budget + reserve > daily:
                refuse_now(rs, "daily cap", now, job)
                act(do="alarm", kind="role:%s:cap" % name, ticket=job["item"], note=True,
                    why="%s %s REFUSED: daily_token_cap %d, %d used today + %d budget + %d kept for the day's "
                        "scheduled runs" % (name, job["trigger"], daily, spent, budget, reserve))
                return
            if (reserve or job["mode"] == "alarm") and spent + budget + reserve > daily:
                if rs.get("event_reserve_day") != day_of(now):          # journalled once a day; the event waits
                    rs["event_reserve_day"] = day_of(now)
                    act(do="role_hold", role=name, why="%s %s waits: the day's scheduled run(s) still to come keep "
                        "their share of the daily cap; the event runs once they leave room" % (name, job["trigger"]))
                return
        if daily is not None and spent + budget > daily:
            # an event run refused on the cap is not a run (ROLE_LAUNCH_REVIEW_FINISH_ROUND_FIVE): it keeps the day's
            # event quota and launches once it fits (a raised cap, a band that shrinks its budget); alarmed once
            sk = skip_event(rs, job, "daily cap")
            if sk is None:
                mark(rs, job, "daily cap")
            elif not sk:
                return
            act(do="alarm", kind="role:%s:cap" % name, ticket=job["item"], note=True,
                why="%s %s REFUSED: daily_token_cap %d, %d used today + %d budget" % (
                    name, job["trigger"], daily, spent, budget))
            return
        go, pk = gate("role_launch") if gate else (True, {})
        if not go:
            if rs.get("account_hold") != job["key"]:     # journal the hold once per job, not every tick
                act(do="role_hold", role=name, why="%s %s held for the account switch: %s" % (
                    name, job["trigger"], pk.get("why")))
            rs["account_hold"] = job["key"]
            return
        rs.pop("account_hold", None)
        unit = "rm-role-%s-%d" % (name.lower(), int(now))
        # built before anything is consumed: a raise here leaves the slot due (review V, V7)
        message = prompt(cfg, job["mode"], job["trigger"], bname, r, budget, job["cap"], factor, spent, unit)
        tick_launch[name] = unit
        # what the launch consumes, so execute can give it back if the launch does not happen (review U, N6)
        rs["pending_launch"] = {"unit": unit, "mode": job["mode"], "key": job["key"],
                                "done": rs["done"].get(job["key"]), "had_done": job["key"] in rs["done"],
                                "alarms_seen": rs.get("alarms_seen"), "event_cursor": rs.get("event_cursor"),
                                "alarm_day": json.loads(json.dumps(rs.get("alarm_day"))),
                                "events_seen": rs.get("events_seen"), "alarm_last_run": rs.get("alarm_last_run")}
        if job.get("manual"):
            rs["pending_launch"]["run_now"] = rs.get("run_now")
            rs["run_now_last"] = dict(rs.pop("run_now"), outcome="launched", unit=unit, decided=now)
        rs.pop("event_skip", None)
        mark(rs, job, "launch")
        if job["mode"] == "alarm":
            rs["alarm_last_run"] = now        # the gap runs from launched alarm runs only, not from passed-over ones
            ad = rs.get("alarm_day") if (rs.get("alarm_day") or {}).get("day") == day_of(now) else \
                {"day": day_of(now), "n": 0, "keys": {}}
            ad["n"] += 1
            for k in job.get("seen") or []:
                ad["keys"][k] = ad["keys"].get(k, 0) + 1
            rs["alarm_day"] = ad
        if lr is not None:
            rs["event_cursor"] = now      # every run reads the events up to its launch (arbiter.md, producer.md)
            rs["events_seen"] = [event_key(e) for e in role_events(cfg, lr, now - EVENT_LOOKBACK_S)]
        act(do="role_launch", role=name, unit=unit, ticket=job["item"], note=True, mode=job["mode"], budget=budget,
            slot=job["key"], band=bname, seat=role["seat"], run_max_s=max_s_of({}, cfg), account=pk.get("account"),
            why="%s %s, band %s, budget %d (cap %d x %.1f), %d used today, unit %s, model %s%s" % (
                name, job["trigger"], bname, budget, job["cap"], factor, spent, unit, role["model"],
                (", account %s (%s)" % (pk["account"], pk["state"])) if pk.get("account") else ""),
            # the blind item's note: role, mode, unit and a fixed outcome; execute swaps the outcome for the true one
            # (held / failed: review V, V4), never for a reason or an error text (review dispatcher-full #2)
            blind=blind(name, "launched", job["mode"], unit),
            message=message, **({"run_now": job["manual"], "pre_launch": job.get("pre_launch")} if job.get("manual")
                                else {}))
        tick_launch.pop(name, None)
        busy.add(name)            # launched this tick: a role that runs after it waits for it (R, B)

    for role in roles:
        # one role's bad schedule value (or a malformed reading) skips THAT role with an alarm; the other roles are
        # still decided and the supervise actions already built still execute (review round U, N5)
        try:
            one(role)
        except Exception as e:  # noqa: BLE001
            nm = role.get("name", "?") if isinstance(role, dict) else "?"
            unit = tick_launch.pop(nm, None)
            if unit and isinstance(rst.get(nm), dict):
                unlaunch(rst[nm], unit)     # it raised after consuming its slot/alarm/event: give it back (V7)
            act(do="alarm", kind="role:%s:schedule" % nm, ticket=(role.get("ledger_item") if isinstance(role, dict)
                                                                 else None), note=True,
                why="role %s NOT RUN this tick: deciding it raised %s: %s" % (nm, type(e).__name__, str(e)[:200]))


def unlaunch(rs, unit):
    """Give back what decide consumed for the launch of `unit` (slot or alarm mark, event cursor, events seen) when
    the launch did not happen: a failed systemd-run, or execute's off/PAUSE recheck. -> True if rolled back."""
    p = rs.get("pending_launch") or {}
    if p.get("unit") != unit:
        return False
    rs.pop("pending_launch", None)
    if p["mode"] == "alarm":
        rs["alarms_seen"] = p["alarms_seen"]
        if p.get("alarm_day") is None:
            rs.pop("alarm_day", None)
        else:
            rs["alarm_day"] = p["alarm_day"]
        if p.get("alarm_last_run") is None:
            rs.pop("alarm_last_run", None)
        else:
            rs["alarm_last_run"] = p["alarm_last_run"]
    elif p["had_done"]:
        rs.setdefault("done", {})[p["key"]] = p["done"]
    else:
        rs.setdefault("done", {}).pop(p["key"], None)
    for k in ("event_cursor", "events_seen"):
        if p[k] is None:
            rs.pop(k, None)
        else:
            rs[k] = p[k]
    if p.get("run_now") is not None:          # a run-now that did not launch is asked again, not lost
        rs["run_now"] = p["run_now"]
        rs.pop("run_now_last", None)
    return True


def alarm_keys(alarms):
    """Pure. ops_watch alarms.json -> the keys of its OPEN alarms: the ledger item filed for it, or, for an alarm
    filed for Operations alone (no ledger item: review V, V2), ALARM_KEY_PREFIX + its alarm id."""
    out = set()
    for aid, a in (alarms or {}).items() if isinstance(alarms, dict) else ():
        if not isinstance(a, dict) or a.get("state") != "OPEN":
            continue
        if a.get("item"):
            out.add(a["item"])
        elif a.get("for") == "Operations":
            out.add(ALARM_KEY_PREFIX + str(aid))
    return out


def alarm_reading(alarms):
    """Pure. -> the sorted keys of the OPEN alarms, or None when the alarms are not readable (absent, not a mapping,
    or ops_watch's UNREADABLE marker): None never prunes alarms_seen."""
    if not isinstance(alarms, dict) or "_alarm_state" in alarms:
        return None
    return sorted(alarm_keys(alarms))


def skip_event(rs, job, how):
    """An event run skipped (off switch, band) is not a run: it is NOT marked, so the day's event_runs_per_day stays
    unused and the event launches once the switch is gone or the band allows it (review night r2). -> None for a
    non-event job (mark it as before); True when this skip is new (journal it), False when already journalled."""
    if job["mode"] != "event":
        return None
    rec = [job["key"], how]
    if rs.get("event_skip") == rec:
        return False
    rs["event_skip"] = rec
    return True


def run_now_cap(cfg, mode):
    """The token cap a run-now of `mode` runs under: the cap the same mode's scheduled run has (slots()). None = the
    role has no run of that mode (the request is refused)."""
    if mode == "economy":
        return cfg.get("economy_token_cap")
    if mode == "quick":
        return cfg.get("quick_token_cap") if "quick_token_cap" in cfg else None
    if mode == "weekly" and cfg.get("quick_token_cap") is not None:
        return cfg["quick_token_cap"]
    return cfg.get("run_token_cap") if mode in ("run", "weekly") else None


CLAIM_RX = re.compile(r"([A-Za-z0-9_]+)@([0-9A-Za-z]{7,40})")


def run_now_request(sch, a, now):
    """Pure. A run-now request from its CLI fields (role, by, why, mode, claims ["ITEM@SHA"], trial, days) -> the
    record kept in st["roles"][role]["run_now"]. Raises ValueError naming the bad field."""
    role = next((r for r in sch.get("roles") or [] if isinstance(r, dict) and r.get("name") == a.get("role")), None)
    if role is None:
        raise ValueError("no role %r in the schedule" % (a.get("role"),))
    by, why = str(a.get("by") or "").strip(), str(a.get("why") or "").strip()
    if not by:
        raise ValueError("--by: say which seat asks")
    if not why:
        raise ValueError("--why: say why this run is asked for")
    cfg = dict(ROLE_DEFAULTS, **role)
    mode = a.get("mode") or ("quick" if "quick_token_cap" in cfg else "run")
    if mode not in RUN_NOW_MODES or not run_now_cap(cfg, mode):
        raise ValueError("mode %r: a run-now runs one of %s that %s has a token cap for" % (
            mode, "/".join(RUN_NOW_MODES), role["name"]))
    claims = []
    for c in a.get("claims") or []:
        m = CLAIM_RX.fullmatch(str(c).strip())
        if not m:
            raise ValueError("claim %r is not ITEM@SHA (a ledger item, @, a 7-40 character sha)" % (c,))
        claims.append([m.group(1), m.group(2).lower()])
    if a.get("trial") and not claims:
        raise ValueError("--trial needs --claim: a trial judges named claims only (without them the schedule's own "
                         "pre-steps would write the real tiers record)")
    if claims and role["name"] not in CLAIM_PRE_ROLES:
        raise ValueError("claims name what to judge: a %s request only, not %s" % ("/".join(CLAIM_PRE_ROLES),
                                                                                  role["name"]))
    days = a.get("days")
    days = 7 if days is None else days
    if not (_num(days) and 0 < days <= 60):
        raise ValueError("days %r: the claims' close window must be > 0 and <= 60" % (days,))
    return {"at": now, "by": by, "why": why, "mode": mode, "claims": claims, "trial": bool(a.get("trial")),
            "days": days}


def run_now_job(cfg, req, now):
    """Pure. The due job for a run-now request: no slot (no slot gate, no after_role wait, no event cursor), its
    mode's cap, and for named claims the Arbiter's pre-steps for exactly those claims (a trial's tiers in their own
    data dir, its verdicts in TRIAL_VERDICTS: harvest reads " run-now trial " in the key)."""
    trial, claims, days = bool(req.get("trial")), req.get("claims") or [], "%g" % req.get("days", 7)
    pre = None
    if claims:
        pre = [["python3", "src/RimMandrake/rimflow/isolated_evidence.py", "--run", "--seat", "DISPATCHER"]
               + [x for i, _ in claims for x in ("--item", i)] + ["--days", days],
               ["python3", "src/RimMandrake/rimflow/arbiter_tiers.py"]
               + [x for i, sh in claims for x in ("--claim", "%s@%s" % (i, sh))] + ["--days", days]
               + (["--data", TRIAL_TIERS_DATA] if trial else [])]
    trigger = "run-now by %s: %s" % (req.get("by"), req.get("why"))
    if claims:
        trigger += "; judge exactly these claims: " + ", ".join("%s@%s" % (i, sh) for i, sh in claims)
    if trial:
        trigger += "; TRIAL: the verdicts are recorded in %s, apart from the real record" % TRIAL_VERDICTS
    return {"key": "%s run-now%s %s" % (day_of(now), " trial" if trial else "", iso(req.get("at") or now)),
            "slot": None, "first": False, "mode": req.get("mode") or "run", "cap": run_now_cap(cfg, req.get("mode")),
            "item": cfg["ledger_item"], "trigger": trigger, "manual": req, "pre_launch": pre}


def refuse_now(rs, how, now, job=None):
    """A run-now refused (or expired) is consumed, said once: one-shot, never retried by the ticks. A no-op for
    a scheduled job."""
    if job is not None and not job.get("manual"):
        return
    req = rs.pop("run_now", None)
    if req is not None:
        rs["run_now_last"] = dict(req, outcome="refused: " + how, decided=now)


def launch_role(role, a):
    """The schedule entry execute launches for action `a`: the entry itself, or for a run-now, a copy that is enabled
    for this one launch and runs the request's pre-steps when it named claims."""
    if not a.get("run_now"):
        return role
    out = dict(role, enabled=True)
    if a.get("pre_launch"):
        out["pre_launch"] = a["pre_launch"]
    return out


def mark(rs, job, how):
    if job["mode"] == "alarm":
        seen = job.get("seen") or [job["item"]]
        rs["alarms_seen"] = sorted(set(rs.get("alarms_seen") or []) | set([seen] if isinstance(seen, str) else seen))
    else:
        rs["done"][job["key"]] = how


# ---------------------------------------------------------------- side effects (dispatcher.execute calls these)

def model_id(alias, env=None):
    """The id the GenAI route names for alias (genai_env.py's reading), or None when this machine has no route
    var (subscription: claude resolves the alias itself). Recorded, never passed: claude gets the alias."""
    env = os.environ if env is None else env
    v = (env.get(MODEL_VARS.get(alias, "")) or "").strip()
    if not v:
        try:
            with open(os.path.expanduser("~/.claude/settings.json"), encoding="utf-8") as f:
                v = ((json.load(f).get("env") or {}).get(MODEL_VARS.get(alias, "")) or "").strip()
        except (OSError, ValueError, AttributeError):
            v = ""
    return v.replace("[1m]", "") or None


def run_paths(root, unit):
    d = os.path.join(root, "roles")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, unit + ".json"), os.path.join(d, unit + ".err")


def role_scope(seat, unit):
    """The claude_bounded scope a role run gets, named by the launcher (CLAUDE_SCOPE_UNIT), known before
    systemd-run and persisted with the run: claude-seat-<seat>-<unit>.scope (review dispatcher-full #1)."""
    return "claude-seat-%s-%s.scope" % (seat, unit)


def _started_at(proc, n, btime):
    """Epoch a /proc process started (stat field 22 / CLK_TCK + boot time), or None when not readable."""
    try:
        with open(os.path.join(proc, n, "stat"), "rb") as f:
            rest = f.read().rsplit(b")", 1)[1].split()
        return btime + int(rest[19]) / float(os.sysconf("SC_CLK_TCK"))
    except (OSError, IndexError, ValueError):
        return None


def _boot_time(proc):
    try:
        with open(os.path.join(proc, "stat"), "rb") as f:
            for line in f:
                if line.startswith(b"btime "):
                    return int(line.split()[1])
    except (OSError, ValueError):
        pass
    return None


SCAN_RETRIES = 3          # re-reads of an unreadable environ before the scan is called blind
SCAN_RETRY_S = 0.05
SINCE_SLACK_S = 5       # clock-tick rounding and boot-time granularity between a run's `at` and its first process


def scan_marked(marker, proc="/proc", uid=None, since=None):
    """-> (pids carrying RM_ROLE_UNIT=<marker>, None) or (the pids it could see, why the scan is blind).
    Blind (review r2 #3): /proc unlistable, or a process whose environ cannot be read and that is not POSITIVELY
    ruled out. Ruled out: it exited mid-scan (entry gone), it belongs to another uid (a run of ours never changes
    uid), or `since` (the run's start, epoch) is given and it started more than SINCE_SLACK_S before it (the marker
    is inherited, so every process of a run is younger than the run). Measured 2026-10-27: this user's systemd,
    (sd-pam) and ssh-agent are same-uid and unreadable (non-dumpable), so without `since` a real scan is blind."""
    want = ("RM_ROLE_UNIT=%s" % marker).encode()
    try:
        names = os.listdir(proc)
    except OSError as e:
        return [], "%s unlistable (%s)" % (proc, type(e).__name__)
    me, out = os.getpid(), []
    uid = os.getuid() if uid is None else uid
    btime = _boot_time(proc) if since is not None else None
    todo = [n for n in names if n.isdigit() and int(n) != me]
    why = {}
    for attempt in range(SCAN_RETRIES + 1):
        if attempt:
            time.sleep(SCAN_RETRY_S)        # a process mid-exec (or just forked) is unreadable for a moment; a
        why = {}                            # non-dumpable one stays so, and only that one makes the scan blind
        again = []
        for n in todo:
            try:
                with open(os.path.join(proc, n, "environ"), "rb") as f:
                    env = f.read()
            except FileNotFoundError:
                continue                    # exited between listdir and open
            except OSError:
                try:
                    owner = os.stat(os.path.join(proc, n)).st_uid
                except FileNotFoundError:
                    continue                # exited
                except OSError:
                    owner = None            # unknown owner: not ruled out
                if owner is not None and owner != uid:
                    continue                # another user's process: never one of our runs
                started = _started_at(proc, n, btime) if btime is not None else None
                if started is not None and started < since - SINCE_SLACK_S:
                    continue                # older than the run: cannot carry its inherited marker
                why[n] = "pid %s (uid %s) environ unreadable" % (n, owner)
                again.append(n)
                continue
            if want in env.split(b"\0"):
                out.append(int(n))
        todo = again
        if not todo:
            break
    blind = why[sorted(why, key=int)[0]] if why else None
    return out, blind


def procs_of(marker, proc="/proc", uid=None, since=None):
    """-> the pids (not ours) carrying RM_ROLE_UNIT=<marker>, or None when the scan is blind (scan_marked): a
    partial scan is never "none" (review r2 #3)."""
    pids, blind = scan_marked(marker, proc, uid, since)
    return None if blind else pids


SCOPE_GRACE_S = 600     # the scope's own bound sits this far past run_max_s: the Dispatcher's stop comes first
SCOPE_STOP_S = 30       # TERM -> KILL escalation of that bound (TimeoutStopSec)


def scope_bound_s(role):
    """The independent wall-time bound (s) of a role run's unit and claude scope: its run_max_s + SCOPE_GRACE_S."""
    return int(max_s_of({}, dict(ROLE_DEFAULTS, **(role or {})))) + SCOPE_GRACE_S


def schema_args(role):
    """["--json-schema", <compact schema text>] for a STRUCTURED role, read from its clone; [] for every other role.
    Raises ValueError when the schema cannot be read or is not a JSON object: the launch is refused (execute alarms
    role:<name>:launch_failed), never a schema-less run whose verdicts would have nowhere to go."""
    spec = STRUCTURED.get(role.get("name"))
    if not spec:
        return []
    p = os.path.join(role["clone"], spec["schema"])
    try:
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError) as e:
        raise ValueError("role %s: json schema %s unreadable: %s" % (role.get("name"), p, e))
    if not isinstance(doc, dict):
        raise ValueError("role %s: json schema %s is not a JSON object" % (role.get("name"), p))
    return ["--json-schema", json.dumps(doc, separators=(",", ":"), sort_keys=True)]


def launch_argv(role, unit, msg, out, err, claude):
    """The transient unit's argv. A role's `pre_launch` (an argv or a list of argvs, run in its clone) runs first inside the same unit,
    its stdout sent to the err file so `out` stays claude's JSON alone; if it exits non-zero, claude never starts
    (the Arbiter's arbiter_tiers.py: a batch with no fresh tiers.json would judge blind -- review AA brief AA7)."""
    bounded = os.path.join(role["clone"], "src", "RimMandrake", "Utils", "claude_bounded.sh")
    path = os.path.dirname(claude) + ":" + os.environ.get("PATH", "/usr/bin:/bin")
    cmd = [bounded, "-p", msg, "--model", role["model"], "--name", "ROLE %s %s" % (role["name"], unit)] \
        + schema_args(role) + ["--output-format", "json", "--dangerously-skip-permissions"]
    pre = role.get("pre_launch")
    if pre:
        # one argv, or a list of argvs run in order, each only if the one before exited 0 (the Arbiter:
        # isolated_evidence.py, then arbiter_tiers.py)
        steps = pre if isinstance(pre, list) and pre and all(isinstance(x, list) for x in pre) else [pre]
        if not all(isinstance(st, list) and st and all(isinstance(x, str) and x for x in st) for st in steps):
            raise ValueError("role %s: pre_launch must be a non-empty argv list or a list of them, got %r"
                             % (role.get("name"), pre))
        # the pre-steps' words are quoted into the script; the claude argv (the message) stays positional, unquoted
        script = " && ".join(" ".join(shlex.quote(x) for x in st) + " 1>&2" for st in steps)
        cmd = ["/bin/sh", "-c", script + ' && exec "$@"', "role-pre-launch"] + cmd
    bound = scope_bound_s(role)
    return ["systemd-run", "--user", "--quiet", "--collect", "--unit", unit,
            "-p", "StandardOutput=file:" + out, "-p", "StandardError=file:" + err,
            "--working-directory", role["clone"],
            "--setenv", "AGENT_SEAT=" + role["seat"], "--setenv", "RIMFLOW_SEAT=" + role["seat"],
            # the scope's name, chosen here and persisted with the run, and the marker every process of the run
            # inherits: the two things supervise checks before a run counts as ended (review dispatcher-full #1)
            "--setenv", "CLAUDE_SCOPE_UNIT=" + role_scope(role["seat"], unit)[:-len(".scope")],
            "--setenv", "RM_ROLE_UNIT=" + unit,
            # the run's own wall-time bound, independent of the Dispatcher (review r2 #2): claude_bounded sets it on
            # the scope (RuntimeMaxSec, TERM, then KILL after SCOPE_STOP_S), and the unit gets the same bound; so a
            # run is ended even if no tick ever supervises it again (timer off, dry-run root, unreadable state)
            "--setenv", "CLAUDE_SCOPE_RUNTIME_MAX=%d" % bound,
            "-p", "RuntimeMaxSec=%d" % bound, "-p", "TimeoutStopSec=%d" % SCOPE_STOP_S,
            "--setenv", "PATH=" + path, "--"] + cmd


def launch(role, unit, msg, root, claude, runner=subprocess.run):
    """-> (ok, out, run-record fields). Starts the transient unit and returns at once. ok False only when
    systemd-run itself said no; a raise (a timeout) leaves the caller's run record in place, since the unit may be up.
    The scope is named by the launcher (role_scope), never looked up: the caller recorded it before this call."""
    out, err = run_paths(root, unit)
    r = runner(launch_argv(role, unit, msg, out, err, claude), capture_output=True, text=True, timeout=60,
               stdin=subprocess.DEVNULL)
    text = ((r.stdout or "") + (r.stderr or "")).strip()[-200:]
    if r.returncode:
        return False, "systemd-run exit %d: %s" % (r.returncode, text), {}
    scope = role_scope(role["seat"], unit)
    return True, "unit %s started (scope %s)" % (unit, scope), {
        "out": out, "err": err, "scope": scope, "marker": unit, "model_id": model_id(role["model"])}


def scope_of(unit, seat, runner=subprocess.run):
    """claude_bounded's scope for the unit (claude-seat-<seat>-<unit MainPID>.scope), or None when not knowable now."""
    try:
        r = runner(["systemctl", "--user", "show", "-p", "MainPID", "--value", unit], capture_output=True, text=True,
                   timeout=30, stdin=subprocess.DEVNULL)
        main_pid = (r.stdout or "").strip() if not r.returncode else ""
    except Exception:  # noqa: BLE001
        main_pid = ""
    return ("claude-seat-%s-%s.scope" % (seat, main_pid)) if main_pid.isdigit() and main_pid != "0" else None


def unit_state(unit, runner=subprocess.run):
    """ActiveState, or "unknown" when systemctl fails, times out or says nothing (supervise_roles keeps it busy)."""
    try:
        r = runner(["systemctl", "--user", "show", "-p", "ActiveState", "--value", unit], capture_output=True,
                   text=True, timeout=30, stdin=subprocess.DEVNULL)
        if r.returncode:
            return "unknown"
        return (r.stdout or "").strip() or "unknown"
    except Exception:  # noqa: BLE001
        return "unknown"


def read_result(run):
    try:
        with open(run["out"], encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError, KeyError, TypeError):
        try:
            with open(run.get("err") or "", encoding="utf-8", errors="replace") as f:
                run["err_tail"] = f.read()[-300:]
        except OSError:
            pass
        return None


def _stop_call(runner, argv, timeout):
    """One systemctl call, never raising: -> its line for the stop result."""
    try:
        r = runner(argv, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except Exception as e:  # noqa: BLE001 - a hung or failing systemctl must not skip the other targets (r2 #1)
        return "%s %s raised %s: %s" % (argv[2], argv[-1], type(e).__name__, str(e)[:80])
    if r.returncode == 0:
        return "%s %s ok" % (argv[2], argv[-1])
    return "%s %s exit %d: %s" % (argv[2], argv[-1], r.returncode,
                                  ((r.stdout or "") + (r.stderr or "")).strip()[-120:])


def _signal_marked(marker, force, procs, kill, since=None):
    """TERM (KILL when force) every process carrying the run's marker that the scan can see, even when it is partly
    blind (the next tick's ended() still holds the run busy then); never raises. -> its line."""
    blind = None
    try:
        if procs:
            pids = procs(marker, since=since)
        else:
            pids, blind = scan_marked(marker, since=since)
    except Exception as e:  # noqa: BLE001
        return "marker scan raised %s: UNMEASURED" % type(e).__name__
    if pids is None:
        return "marker scan UNMEASURED"
    if blind and not pids:
        return "marker scan UNMEASURED (%s)" % blind
    if not pids:
        return "no process marked %s" % marker
    sig, sent = (signal.SIGKILL if force else signal.SIGTERM), 0
    for pid in pids:
        try:
            kill(pid, sig)
            sent += 1
        except Exception:  # noqa: BLE001 - gone, or not ours: the next tick's scan decides
            pass
    return "%s to %d of %d process(es) marked %s%s" % ("KILL" if force else "TERM", sent, len(pids), marker,
                                                       "; scan partly UNMEASURED (%s)" % blind if blind else "")


def stop(unit, scope, runner=subprocess.run, seat=None, unit_gone=False, marker=None, force=False, procs=None,
         kill=os.kill, since=None):
    """The claude process lives in claude_bounded's scope (role_scope, persisted with the run), outside the unit:
    stopping the unit alone would leave it running. Every target is tried on its own and none can stop the others
    (review r2 #1): a systemctl that raises or hangs (its timeout) is one line of the result, never an exit.
      - force (the third stop on): the marked processes get KILL FIRST (no systemd involved, so a hung systemctl
        cannot hold it back), then `systemctl kill --signal=SIGKILL` the scope (its whole cgroup), then the stops;
      - else: `systemctl stop --no-block` the scope, then the unit (queued, never waited on), then TERM the marked.
    A run recorded before scopes were named and with none resolved: resolve it now from the unit's MainPID. Whether
    the stop took is decided by the next tick (supervise: unit, scope AND marker scan), not here. Never raises."""
    said = []
    if not scope and seat and not unit_gone:
        try:
            scope = scope_of(unit, seat, runner)
        except Exception as e:  # noqa: BLE001
            said.append("scope lookup raised %s" % type(e).__name__)
    names = [n for n in (scope, None if unit_gone else unit) if n]
    if marker and force:
        said.append(_signal_marked(marker, True, procs, kill, since))
    if force and scope:
        said.append(_stop_call(runner, ["systemctl", "--user", "kill", "--signal=SIGKILL", scope], 30))
    for n in names:
        said.append(_stop_call(runner, ["systemctl", "--user", "stop", "--no-block", n], 30))
    if marker and not force:
        said.append(_signal_marked(marker, False, procs, kill, since))
    return "; ".join(said) or "nothing to stop (no scope, unit gone, no marker)"


def off_switch(path):
    """-> None when the file is absent, else its first line ('' when empty)."""
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.readline().strip()
    except OSError:
        return "unreadable"


def read_ops(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError, TypeError):
        return None


def resolve_account():
    """The switcher-registry label of the account this machine's sessions are logged in as (account_usage)."""
    utils = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils")
    if utils not in sys.path:
        sys.path.append(utils)
    try:
        import account_usage as AU
        email = AU.live_email()
        for label, mail in AU.registry().items():
            if email and mail == email:
                return label
    except Exception:  # noqa: BLE001
        pass
    return None


def _cli_state(root, wait_s=500):
    """The live state under the tick's own lock (dispatcher.stop_runs's pattern): a request written beside a tick
    would be lost to its save. -> (lock file, D, state)."""
    import fcntl
    import dispatcher as D
    os.makedirs(root, exist_ok=True)
    lk = open(os.path.join(root, "tick.lock"), "w")
    t0 = time.time()
    while True:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.time() - t0 > wait_s:
                lk.close()
                raise OSError("tick.lock at %s held for %d s" % (root, wait_s))
            time.sleep(2)
    try:
        st = D.load_state(root) if os.path.exists(os.path.join(root, "state.json")) else {}
    except Exception:
        lk.close()
        raise
    return lk, D, st


def main(argv=None):
    """run-now: ask for one run of a role by hand (it need not be enabled); the next dispatcher tick launches it
    through every gate a scheduled run passes (off switch, PAUSE, busy, ops reading, band, caps, account).
    run-status: what a role's last run-now did."""
    import argparse
    p = argparse.ArgumentParser(prog="role_launch.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run-now")
    r.add_argument("--schedule", help="the dispatcher schedule (default dispatcher_schedule.json)")
    r.add_argument("--root", help="the dispatcher state dir (default the live one)")
    r.add_argument("--role", required=True)
    r.add_argument("--by")
    r.add_argument("--why")
    r.add_argument("--mode", help="/".join(RUN_NOW_MODES) + " (default the role's own scheduled mode)")
    r.add_argument("--claim", action="append", default=[], help="ITEM@SHA (Arbiter only): judge exactly these")
    r.add_argument("--trial", action="store_true", help="verdicts to the trial record, apart from the real one")
    r.add_argument("--days", type=float, default=7, help="the named claims closed within this many days")
    r.add_argument("--cancel", action="store_true")
    r.add_argument("--apply", action="store_true")
    s = sub.add_parser("run-status")
    s.add_argument("--root")
    s.add_argument("--role", required=True)
    a = p.parse_args(argv)
    import dispatcher as D
    root = a.root or D.state_root(True)
    if a.cmd == "run-status":
        try:
            st = D.load_state(root) if os.path.exists(os.path.join(root, "state.json")) else {}
        except Exception as e:  # noqa: BLE001
            print("UNMEASURED: state unreadable: %s" % e, file=sys.stderr)
            return 2
        rs = (st.get("roles") or {}).get(a.role) or {}
        print(json.dumps({"pending": rs.get("run_now"), "last": rs.get("run_now_last"),
                          "running": [x for x in rs.get("runs") or [] if x.get("state") == "running"]}, indent=1))
        return 0
    now = time.time()
    if not a.cancel:
        try:
            sch = D.load_schedule(a.schedule)
            req = run_now_request(sch, {"role": a.role, "by": a.by, "why": a.why, "mode": a.mode,
                                        "claims": a.claim, "trial": a.trial, "days": a.days}, now)
        except (OSError, ValueError) as e:
            print("REFUSED: %s" % e, file=sys.stderr)
            return 2
        print(json.dumps(req))
    if not a.apply:
        print("dry run: nothing written (--apply writes it)")
        return 0
    try:
        lk, D, st = _cli_state(root)
    except Exception as e:  # noqa: BLE001
        print("UNMEASURED: %s; nothing written" % e, file=sys.stderr)
        return 2
    try:
        rs = st.setdefault("roles", {}).setdefault(a.role, {})
        if a.cancel:
            gone = rs.pop("run_now", None)
            if gone is not None:
                rs["run_now_last"] = dict(gone, outcome="cancelled", decided=now)
            D.save(st, root)
            print("cancelled" if gone else "no request pending")
            return 0
        if rs.get("run_now"):
            print("REFUSED: a run-now is already pending for %s (%s); --cancel it first" % (
                a.role, json.dumps(rs["run_now"])), file=sys.stderr)
            return 1
        rs["run_now"] = req
        D.save(st, root)
        print("requested: the next dispatcher tick decides it (role_launch.py run-status --role %s)" % a.role)
        return 0
    finally:
        lk.close()


if __name__ == "__main__":
    sys.exit(main())
