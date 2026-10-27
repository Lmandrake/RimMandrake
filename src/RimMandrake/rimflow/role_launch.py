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
also runs once per ops_watch alarm item FILED after the role was first seen enabled (`alarm_runs`); alarms already
open at that first tick are the baseline, covered by the next running check; the baseline is taken only from a
MEASURED ops_watch reading (a blind first tick sets none and runs no alarm). One run per role at a time.

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
cache_read, output): the conservative reading. A run over its budget is an ALARM after the fact: `claude -p` has no
token stop and nothing here stops a run at its budget: the budget is checked on its result. Only a `token_aware` role
(Operations) is told its band and budget in its launch message; every other role is token-blind and is told
neither (owner 2026-10-27; review T, F1/F2). A run still going after
`run_max_s` is stopped (its claude_bounded scope and its unit) with an alarm; it stays `running` and the stop is
re-issued each tick until systemd says the unit AND its claude_bounded scope are inactive/failed (claude lives in the
scope, outside the unit; the scope is resolved while the unit runs). supervise_roles() does this for every persisted
run before PAUSE, a blind tick or a disabled role can end the tick (review round Q).

How it launches (proved 2026-10-27, D:\\ClaudeWork\\rimmandrake\\role_launch_2026-10-27\\proof\\RESULT.md): as its OWN
transient user service, `systemd-run --user --collect --unit rm-role-<name>-<epoch>`, which runs
`claude_bounded.sh -p <prompt> --model <alias> --output-format json` in the role's clone. The dispatcher tick is a
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
import subprocess
import sys
import time

LAUNCH_KEYS = ("instructions", "seat", "clone", "model", "ledger_item")
ROLE_DEFAULTS = {"slot_late_s": 3600, "run_max_s": 1800}
ALARM_KEY_PREFIX = "alarm:"            # an Operations-only alarm (no ledger item) in alarms_seen: "alarm:<aid>" (V2)
OPS_STALE_S = 45 * 60
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")      # time.localtime().tm_wday order
DONE_CLAIM_VERBS = ("implemented", "close")   # a done claim on the ledger: built (L0 passed) or closed against a sha
ACTIVE = ("active", "activating", "deactivating", "reloading")
TERMINAL = ("inactive", "failed")      # the only states that end a run; anything else ("unknown", a failed query) is busy
EVENT_LOOKBACK_S = 6 * 3600             # an event ingested this late after its writer stamped it still triggers (N4)
FUTURE_TOL_S = 300                     # a reading stamped further ahead than this is a clock fault, not fresh
USAGE_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
# genai_env.py (~/dev/Lodestar/bin/lib/genai_env.py) MODEL_VARS: the env var that names each alias's model id.
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
    if bands and not any("runway_ge" in b for b in bands.values()):
        raise ValueError("throttle_bands has no band with runway_ge: no band to fall back to")
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
    out = []
    for t in times:
        days, hhmm = parse_slot(t)
        if day is not None and days is not None and weekday(day) not in days:
            continue
        if hhmm == role.get("economy_pass_local") and role.get("economy_token_cap"):
            out.append((t, "economy", role["economy_token_cap"]))
        elif (day is not None and wk and weekday(day) == WEEKDAYS.index(str(wk).title())
              and not any(m == "weekly" for _, m, _ in out)):          # the day's first run slot only
            out.append((t, "weekly", role.get("quick_token_cap") or role.get("run_token_cap")))
        else:
            out.append((t, "quick" if quick else "run", role.get("quick_token_cap") or role.get("run_token_cap")))
    return out


def slot_epoch(now, slot):
    """The epoch of a slot ("HH:MM" or "Ddd HH:MM": the weekday is the caller's filter) on now's local day."""
    lt = time.localtime(now)
    h, m = (int(x) for x in str(slot).split()[-1].split(":"))
    return time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, h, m, 0, 0, 0, -1))


def day_of(t):
    return time.strftime("%Y-%m-%d", time.localtime(t))


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
    for ev in events:
        t = utc_epoch(ev.get("ts"))
        if t is not None and t > since:
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
    """One ledger event's identity in a trigger list: (epoch, id, what) -> "epoch|id|what"."""
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
    return [e for e in evs if event_key(e) not in seen]


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


def run_tokens(result):
    """Pure. usage of a `claude -p --output-format json` result -> total tokens (all four fields) or None
    (UNMEASURED) when the usage block or any field is missing, not a whole non-negative number, or a bool: an absent
    field is unknown spend, never zero (review Q 8). The run is then failed and its spend counted at its budget."""
    u = result.get("usage") if isinstance(result, dict) else None
    if not isinstance(u, dict):
        return None
    vals = [u.get(k) for k in USAGE_KEYS]
    if not all(finite(v) and v >= 0 and float(v).is_integer() for v in vals):
        return None
    return int(sum(vals))


def spent_today(rs, now):
    day = day_of(now)
    tot = 0
    for r in rs.get("runs") or []:
        if r.get("day") != day:
            continue
        tot += r["tokens"] if r.get("tokens") is not None else r.get("budget", 0)
    return tot


def prompt(role, mode, trigger, band_name, reading, budget, cap, factor, spent, unit):
    """The launch message. Every role but one whose schedule entry says `token_aware: true` (Operations, the only AI
    that analyses burn) is token-blind (owner 2026-10-27): its message carries no band, runway, week, budget or cap,
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
                  "Token budget for this run: %d tokens (cap %d x %.1f); daily cap %d, %d already used today. The "
                  "Dispatcher checks it after the run; it does not stop you at it." % (
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


def max_s_of(run, cfg):
    """A run's wall-time bound: its recorded run_max_s, else the role's, else the default, whichever is first a
    positive number (a None or 0 from an older schedule never reaches a comparison: review V, V3)."""
    for v in (run.get("run_max_s"), cfg.get("run_max_s"), ROLE_DEFAULTS["run_max_s"]):
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
            # claude runs in claude_bounded's scope, outside the unit: learn its name while the unit's MainPID
            # still exists (review round R, D)
            run["scope"] = obs["scope"](run["unit"], run.get("seat") or cfg.get("seat"))
        if ustate in TERMINAL:
            # the unit ending is not claude ending: claude_bounded's shell traps TERM and claude lives on in its
            # scope. Retired only when the scope is empty too (inactive/failed = no process left or no such
            # unit) (review round R, D).
            if run.get("scope"):
                sstate = obs["unit_state"](run["scope"])
                if sstate not in TERMINAL:
                    ustate = "unit %s but scope %s %s" % (ustate, run["scope"], sstate)
            elif now - run["at"] < max_s_of(run, cfg):
                ustate = "unit %s, scope never resolved (claude may still run)" % ustate
            else:
                run["scope_unconfirmed"] = True
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
                    unit_gone=ustate.startswith("unit "),     # stop the scope alone: `systemctl stop` of a
                    # collected unit fails the whole call
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
        if run.get("scope_unconfirmed"):
            act(do="alarm", kind="role:%s:scope_unconfirmed:%s" % (name, run["unit"]), ticket=run.get("item"),
                note=True,      # its own kind: role:<name>:scope was raised every tick and rate-limited this away
                why="%s run %s: unit ended, its claude_bounded scope was never resolved; retired at run_max_s "
                "UNCONFIRMED (a claude may still run under claude-seat-%s-*)" % (name, run["unit"],
                                                                               run.get("seat") or "?"))
        res = obs["result"](run)
        tok = run_tokens(res)
        run["tokens"] = tok
        run["state"] = "failed" if (not isinstance(res, dict) or res.get("is_error") or tok is None) else "done"
        res = res if isinstance(res, dict) else {}
        models = sorted(res.get("modelUsage") or {})
        act(do="role_done", role=name, unit=run["unit"], ticket=run.get("item"), note=True,
            why="%s %s run %s %s%s: %s tokens of a %d budget, model %s, %s" % (
                name, run.get("mode"), run["unit"], run["state"],
                " (after %d stop(s))" % run["stop_tries"] if run.get("stop_tries") else "",
                tok if tok is not None else "UNMEASURED (counted at its budget)",
                run.get("budget") or 0, ",".join(models) or "?", res.get("subtype") or "no result"),
            # a token-blind role reads its ledger item: its note carries no tokens or budget (review U N2); the
            # journal keeps `why`
            note_text=None if cfg.get("token_aware") is True else "%s %s run %s %s, %s" % (
                name, run.get("mode"), run["unit"], run["state"], res.get("subtype") or "no result"))
        if tok is not None and tok > (run.get("budget") or 0):
            act(do="alarm", kind="role:%s:overbudget" % name, ticket=run.get("item"), note=True,
                why="%s run %s used %d tokens, budget %d" % (name, run["unit"], tok, run.get("budget") or 0))
        if run["state"] == "failed":
            act(do="alarm", kind="role:%s:failed" % name, ticket=run.get("item"), note=True,
                why="%s run %s ended without a good result (%s)" % (
                    name, run["unit"], ("usage UNMEASURED: " if res and tok is None else "")
                    + (res.get("result") or run.get("err_tail") or "no result file")[:160]))
    rs["runs"] = [r for r in rs.get("runs") or [] if r.get("state") == "running" or now - r["at"] < 2 * 86400]


def after_slots(after_cfg, job, now):
    """Pure. The after_role's slots this scheduled job may follow, newest first: its slots at or before the job's slot
    today, then yesterday's after the job's slot time (24 h back at most). -> ["YYYY-MM-DD HH:MM", ...] (done/run keys),
    empty when it has no slots."""
    mine = slot_epoch(now, job["slot"])
    keys = []
    for day in (now, now - 86400):
        for t, _, _ in slots(after_cfg, day):
            e = slot_epoch(day, t)
            if mine - 86400 < e <= mine:
                keys.append((e, "%s %s" % (day_of(day), str(t).split()[-1])))
    return [k for _, k in sorted(keys, reverse=True)]


def after_ready(cfg, rst, busy, job, now, after_cfg=None):
    """`after_role` (Conductor: "each after an Operations run", conductor.md; Producer: after the economy pass): a
    scheduled slot waits until that role's OWN scheduled run for the slot it follows (after_slots: Conductor 08:00 ->
    Operations 07:30 today, 20:00 -> 19:30) finished done, and none of its runs is in flight. A slot of that role the
    band skipped on purpose (done "band X": Operations' 07:30 in AMBER/RED) is passed over for its previous slot within
    24 h (review T, F4: the Producer's 09:00 then follows the 19:30 run). An alarm run, or yesterday's run launched
    late, never counts (review round R, B). -> None when ready, else why it waits."""
    after = cfg.get("after_role")
    if not after or not job["slot"]:
        return None
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
        if "r" not in reading_cache:
            reading_cache["r"] = ops_reading(obs["ops"](), obs["account"](), now,
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
    roles = sorted((r for r in sch.get("roles") or [] if isinstance(r, dict)),
                   key=lambda r: 1 if r.get("after_role") else 0)
    def one(role):
        name = role.get("name", "?")
        if not role.get("enabled"):
            return
        missing = [k for k in LAUNCH_KEYS if not role.get(k)]
        if missing:
            act(do="alarm", kind="role:" + name, why="role %s is enabled but cannot be launched: no %s in the schedule"
                % (name, ", ".join(missing)))
            return
        cfg = dict(ROLE_DEFAULTS, **role)
        if cfg.get("after_role") and not (by_name.get(cfg["after_role"]) or {}).get("enabled"):
            act(do="alarm", kind="role:%s:after" % name, ticket=role["ledger_item"], note=True,
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
            if cfg.get("slot_when") not in (None, "done_claims"):
                raise ValueError("slot_when %r is not done_claims" % cfg["slot_when"])
        except ValueError as e:
            act(do="alarm", kind="role:%s:schedule" % name, ticket=role["ledger_item"], note=True,
                why="role %s NOT RUN: its schedule entry is unreadable: %s" % (name, e))
            return
        # ---- the ledger, for a role that triggers on its events (Arbiter: done claims; Producer: plan-step
        # failures, replan requests). Blind: this role launches nothing this tick, not even a clock slot.
        lr = None
        if cfg.get("slot_when") or cfg.get("event_runs"):
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
        for i, (hhmm, mode, cap) in enumerate(today):
            key = "%s %s" % (day_of(now), hhmm)
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
        if role.get("alarm_runs"):
            open_items = sorted(alarm_keys((obs["ops"]() or {}).get("alarms")))
            if "alarms_seen" not in rs:
                if reading()["state"] != "MEASURED":
                    # a blind first reading is not a baseline: [] would make every alarm already open a paid run on
                    # the next readable tick (review round R, C). No alarm runs until a MEASURED reading sets it.
                    if not rs.get("baseline_wait"):
                        act(do="role_hold", role=name, why="%s alarm runs: no baseline yet, the ops_watch reading is "
                            "UNMEASURED (%s); no alarm run launches until it is MEASURED" % (name, reading()["why"]))
                    rs["baseline_wait"] = True
                    open_items = []
                else:
                    rs.pop("baseline_wait", None)
                    rs["alarms_seen"] = open_items       # the baseline at first enable: not run
            for item in open_items:
                if item not in rs["alarms_seen"]:
                    # an account alarm has no ledger item (it is Operations' alone, never on a seat queue: review V,
                    # V2): its run notes on the role's own ledger_item; mark() still records it by its key
                    due.append({"key": "alarm " + item, "slot": None, "first": False, "mode": "alarm",
                                "cap": cfg.get("run_token_cap"), "seen": item,
                                "item": role["ledger_item"] if item.startswith(ALARM_KEY_PREFIX) else item,
                                "trigger": "ops_watch alarm " + item})
        if cfg.get("event_runs"):
            try:
                pend = unseen(pending_events(cfg, lr, rs["event_cursor"] - EVENT_LOOKBACK_S), rs)
            except ValueError as e:
                act(do="alarm", kind="role:%s:schedule" % name, ticket=role["ledger_item"], note=True,
                    why="role %s NOT RUN: %s" % (name, e))
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
        if not due:
            return
        job = due[0]                                      # one launch per role per tick
        off = obs["off"](wsl_path(role.get("off_file") or ""))
        if off is not None:
            mark(rs, job, "off")
            act(do="role_hold", role=name, why="%s %s skipped: off switch %s (%s)" % (
                name, job["trigger"], role.get("off_file"), off or "no reason given"))
            return
        if name in busy:
            return                                      # one run at a time: wait for the running one
        if job["slot"] and cfg.get("slot_when") == "done_claims":
            claims = unseen(done_claims(lr["events"], rs["event_cursor"] - EVENT_LOOKBACK_S), rs)
            if not claims:
                mark(rs, job, "no done claims")
                act(do="role_hold", role=name, why="%s %s not run: no done claim (implemented/close) since %s" % (
                    name, job["trigger"], iso(rs["event_cursor"])))
                return
            job["trigger"] += ", %d done claim(s) since %s (oldest %s %s)" % (
                len(claims), iso(rs["event_cursor"]), claims[0][2], claims[0][1])
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
            act(do="alarm", kind="role:%s:ops" % name, ticket=job["item"], note=True,
                why="%s %s REFUSED: %s" % (name, job["trigger"], r["why"]))
            return
        bname, b = band(cfg, r)
        allowed = b.get("slots", "all")
        if slot_blocked(allowed, job, cfg, now):
            mark(rs, job, "band " + bname)
            act(do="role_hold", role=name, why="%s %s not run: band %s runs %s scheduled slots (runway %.2f %s, "
                "week left %.0f%%)" % (name, job["trigger"], bname, allowed, r["runway"], r["runway_m"],
                                       r["week_left"]))
            return
        factor = float(b.get("quick_cap_x", 1.0)) if job["mode"] in ("quick", "run", "weekly", "event") else 1.0
        if not job["cap"]:
            act(do="alarm", kind="role:" + name, why="role %s has no token cap for %s" % (name, job["mode"]))
            return
        budget = int(job["cap"] * factor)
        spent = spent_today(rs, now)
        daily = role.get("daily_token_cap")
        if daily and job["mode"] == "event":
            # the day's scheduled runs not yet run keep their budget: an event run may spend only what they leave,
            # so it can never make the 09:00 (Wednesday: the weekly plan) refuse on the daily cap (review U, N3)
            # a slot this band will block never runs, so it reserves nothing (review V, V6)
            reserve = sum(int(c * (float(b.get("quick_cap_x", 1.0)) if m in ("quick", "run", "weekly") else 1.0))
                          for i, (hh, m, c) in enumerate(today) if c and "%s %s" % (day_of(now), hh) not in rs["done"]
                          and not slot_blocked(allowed, {"slot": hh, "first": i == 0, "mode": m}, cfg, now))
            if reserve and spent + budget + reserve > daily:
                if rs.get("event_reserve_day") != day_of(now):          # journalled once a day; the event waits
                    rs["event_reserve_day"] = day_of(now)
                    act(do="role_hold", role=name, why="%s %s waits: the day's scheduled run(s) still to come keep "
                        "their share of the daily cap; the event runs once they leave room" % (name, job["trigger"]))
                return
        if daily and spent + budget > daily:
            mark(rs, job, "daily cap")
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
                                "events_seen": rs.get("events_seen")}
        mark(rs, job, "launch")
        if lr is not None:
            rs["event_cursor"] = now      # every run reads the events up to its launch (arbiter.md, producer.md)
            rs["events_seen"] = [event_key(e) for e in role_events(cfg, lr, now - EVENT_LOOKBACK_S)]
        act(do="role_launch", role=name, unit=unit, ticket=job["item"], note=True, mode=job["mode"], budget=budget,
            slot=job["key"], band=bname, seat=role["seat"], run_max_s=cfg["run_max_s"], account=pk.get("account"),
            why="%s %s, band %s, budget %d (cap %d x %.1f), %d used today, unit %s, model %s%s" % (
                name, job["trigger"], bname, budget, job["cap"], factor, spent, unit, role["model"],
                (", account %s (%s)" % (pk["account"], pk["state"])) if pk.get("account") else ""),
            note_text=None if cfg.get("token_aware") is True else "%s %s launched, unit %s" % (
                name, job["trigger"], unit),
            # the launch's subject for execute's true-outcome note (held / failed: review V, V4); None = use `why`
            note_base=None if cfg.get("token_aware") is True else "%s %s, unit %s" % (name, job["trigger"], unit),
            message=message)
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
    elif p["had_done"]:
        rs.setdefault("done", {})[p["key"]] = p["done"]
    else:
        rs.setdefault("done", {}).pop(p["key"], None)
    for k in ("event_cursor", "events_seen"):
        if p[k] is None:
            rs.pop(k, None)
        else:
            rs[k] = p[k]
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


def mark(rs, job, how):
    if job["mode"] == "alarm":
        rs["alarms_seen"] = sorted(set(rs.get("alarms_seen") or []) | {job.get("seen") or job["item"]})
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


def launch_argv(role, unit, msg, out, err, claude):
    bounded = os.path.join(role["clone"], "src", "RimMandrake", "Utils", "claude_bounded.sh")
    path = os.path.dirname(claude) + ":" + os.environ.get("PATH", "/usr/bin:/bin")
    return ["systemd-run", "--user", "--quiet", "--collect", "--unit", unit,
            "-p", "StandardOutput=file:" + out, "-p", "StandardError=file:" + err,
            "--working-directory", role["clone"],
            "--setenv", "AGENT_SEAT=" + role["seat"], "--setenv", "RIMFLOW_SEAT=" + role["seat"],
            "--setenv", "PATH=" + path, "--",
            bounded, "-p", msg, "--model", role["model"], "--name", "ROLE %s %s" % (role["name"], unit),
            "--output-format", "json", "--dangerously-skip-permissions"]


def launch(role, unit, msg, root, claude, runner=subprocess.run):
    """-> (ok, out, run-record fields). Starts the transient unit and returns at once. ok False only when
    systemd-run itself said no; a raise (a timeout) leaves the caller's run record in place, since the unit may be up.
    The MainPID lookup cannot lose the run: a failure leaves scope None, and stop() resolves it then (review Q 4)."""
    out, err = run_paths(root, unit)
    r = runner(launch_argv(role, unit, msg, out, err, claude), capture_output=True, text=True, timeout=60,
               stdin=subprocess.DEVNULL)
    text = ((r.stdout or "") + (r.stderr or "")).strip()[-200:]
    if r.returncode:
        return False, "systemd-run exit %d: %s" % (r.returncode, text), {}
    scope = scope_of(unit, role["seat"], runner)
    return True, "unit %s started (scope %s)" % (unit, scope or "not yet known"), {
        "out": out, "err": err, "scope": scope, "model_id": model_id(role["model"])}


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


def stop(unit, scope, runner=subprocess.run, seat=None, unit_gone=False):
    """The claude process lives in claude_bounded's scope (claude-seat-<seat>-<unit MainPID>.scope), outside the
    unit: stopping the unit alone would leave it running. No scope recorded (its lookup failed at launch): resolve it
    now, while the unit still runs. Whether the stop took is decided by the next tick's unit state, not here."""
    if not scope and seat:
        scope = scope_of(unit, seat, runner)
    names = [n for n in (scope, None if unit_gone else unit) if n]
    r = runner(["systemctl", "--user", "stop"] + names, capture_output=True, text=True, timeout=120,
               stdin=subprocess.DEVNULL)
    return "stopped %s" % " ".join(names) if r.returncode == 0 else "stop exit %d: %s" % (
        r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()[-160:])


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
