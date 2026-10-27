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
finished done and none is going (after_ready); it is decided after that role in each tick. Operations
also runs once per ops_watch alarm item FILED after the role was first seen enabled (`alarm_runs`); alarms already
open at that first tick are the baseline, covered by the next running check; the baseline is taken only from a
MEASURED ops_watch reading (a blind first tick sets none and runs no alarm). One run per role at a time.

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

Tokens: a finished run's `claude -p --output-format json` usage, ALL FOUR fields (input, cache_creation,
cache_read, output): the conservative reading. A run over its budget is an ALARM after the fact: `claude -p` has no
token stop, so the budget is told to the role in its prompt and checked on its result. A run still going after
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
OPS_STALE_S = 45 * 60
ACTIVE = ("active", "activating", "deactivating", "reloading")
TERMINAL = ("inactive", "failed")      # the only states that end a run; anything else ("unknown", a failed query) is busy
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
    for ge, name, b in ranked:
        if reading["runway"] >= ge:
            return name, b
    return ranked[-1][1], ranked[-1][2]          # below every line: the lowest runway band


def slot_blocked(allowed, job, role):
    """Pure. May this band's `slots` setting stop this job? "all": never. "none": every scheduled slot and every
    alarm run. "first" / "last": only the first / last scheduled slot. "quick": the economy-pass slot is skipped whole
    (its running check goes with it: operations.md), the other running checks and alarm runs go. "quick_one": the
    economy-pass slot and alarm runs are skipped, and only the first NON-economy running check runs (Ops: 19:30)."""
    if allowed == "none":
        return True
    if allowed == "first":
        return bool(job["slot"]) and not job["first"]
    if allowed == "last":
        return bool(job["slot"]) and job["slot"] != slots(role)[-1][0]
    if allowed in ("quick", "quick_one"):
        if job["mode"] == "economy":
            return True
        if allowed == "quick_one":
            if not job["slot"]:
                return True
            quick = [t for t, m, _ in slots(role) if m != "economy"]
            return bool(quick) and job["slot"] != quick[0]
    return False


def slots(role):
    """-> [(HH:MM, mode, cap)] in schedule order."""
    times = role.get("quick_checks_local") or role.get("runs_local") or []
    quick = "quick_token_cap" in role
    out = []
    for t in times:
        if t == role.get("economy_pass_local") and role.get("economy_token_cap"):
            out.append((t, "economy", role["economy_token_cap"]))
        else:
            out.append((t, "quick" if quick else "run", role.get("quick_token_cap") or role.get("run_token_cap")))
    return out


def slot_epoch(now, hhmm):
    lt = time.localtime(now)
    h, m = (int(x) for x in hhmm.split(":"))
    return time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, h, m, 0, 0, 0, -1))


def day_of(t):
    return time.strftime("%Y-%m-%d", time.localtime(t))


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
    lines = ["[RimFlow Dispatcher — a program, not a person; role launch %s]" % unit,
             "You are the RimFlow %s role, run headless by the Dispatcher. Read %s and do what it says for this "
             "trigger, then stop." % (role["name"], role["instructions"]),
             "Trigger: %s %s." % (mode, trigger),
             "Throttle band: %s (account runway %.2f %s, week left %.0f%% %s; ops_watch status at %s)." % (
                 band_name, reading["runway"], reading["runway_m"], reading["week_left"], reading["week_left_m"],
                 reading["at"]),
             "Token budget for this run: %d tokens (cap %d x %.1f); daily cap %d, %d already used today. At the "
             "budget, write one note on %s saying what was left undone, and stop." % (
                 budget, cap, factor, role.get("daily_token_cap") or 0, spent, role["ledger_item"]),
             "You work as seat %s in %s. Never take the bridge, restart the game or deploy." % (role["seat"],
                                                                                              role["clone"])]
    return "\n".join(lines)


# ---------------------------------------------------------------- decide (pure but for obs)

def supervise_roles(sch, st, obs, now, act):
    """Every persisted run still `running`, of every role (enabled or not, in the schedule or not), checked on every
    tick BEFORE anything can end the tick early: PAUSE, a blind `claude agents`, a disabled role (review Q 1). A run
    stays `running` (busy, its budget counted) until systemd says its unit is inactive/failed: a stop is re-issued
    every tick until then (review Q 2), and any other unit state ("unknown", a failed query) is UNMEASURED, busy and
    alarmed, never a finish (review Q 3). -> the set of role names with a run in flight."""
    rst = st.setdefault("roles", {})
    by_name = {r.get("name"): r for r in sch.get("roles") or []}
    busy = set()
    for name, rs in sorted(rst.items()):
        if not isinstance(rs, dict):
            continue
        cfg = dict(ROLE_DEFAULTS, **(by_name.get(name) or {}))
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
                elif now - run["at"] < (run.get("run_max_s") or cfg["run_max_s"]):
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
                max_s = run.get("run_max_s") or cfg["run_max_s"]
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
                act(do="alarm", kind="role:%s:scope" % name, ticket=run.get("item"), note=True,
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
                    run.get("budget") or 0, ",".join(models) or "?", res.get("subtype") or "no result"))
            if tok is not None and tok > (run.get("budget") or 0):
                act(do="alarm", kind="role:%s:overbudget" % name, ticket=run.get("item"), note=True,
                    why="%s run %s used %d tokens, budget %d" % (name, run["unit"], tok, run.get("budget") or 0))
            if run["state"] == "failed":
                act(do="alarm", kind="role:%s:failed" % name, ticket=run.get("item"), note=True,
                    why="%s run %s ended without a good result (%s)" % (
                        name, run["unit"], ("usage UNMEASURED: " if res and tok is None else "")
                        + (res.get("result") or run.get("err_tail") or "no result file")[:160]))
        rs["runs"] = [r for r in rs.get("runs") or [] if r.get("state") == "running" or now - r["at"] < 2 * 86400]
    return busy


def after_slot(after_cfg, job, now):
    """Pure. The after_role's slot this scheduled job follows: its latest slot at or before the job's slot today,
    else its last slot yesterday. -> its done/run key "YYYY-MM-DD HH:MM", or None when it has no slots."""
    times = [t for t, _, _ in slots(after_cfg)]
    if not times:
        return None
    mine = slot_epoch(now, job["slot"])
    before = [t for t in times if slot_epoch(now, t) <= mine]
    if before:
        return "%s %s" % (day_of(now), max(before, key=lambda t: slot_epoch(now, t)))
    return "%s %s" % (day_of(now - 86400), max(times, key=lambda t: slot_epoch(now - 86400, t)))


def after_ready(cfg, rst, busy, job, now, after_cfg=None):
    """`after_role` (Conductor: "each after an Operations run", conductor.md): a scheduled slot waits until that
    role's OWN scheduled run for the slot it follows (after_slot: Conductor 08:00 -> Operations 07:30 today, 20:00 ->
    19:30) finished done, and none of its runs is in flight. An alarm run, or yesterday's run launched late, never
    counts (review round R, B). -> None when ready, else why it waits."""
    after = cfg.get("after_role")
    if not after or not job["slot"]:
        return None
    if after in busy:
        return "an %s run is still going" % after
    key = after_slot(after_cfg or {}, job, now)
    if key is None:
        return "%s has no scheduled slots to follow" % after
    ars = rst.get(after) or {}
    mine = [r for r in ars.get("runs") or [] if r.get("slot") == key and r.get("mode") != "alarm"]
    if any(r.get("state") == "done" for r in mine):
        return None
    if mine:
        return "the %s %s run ended %s" % (after, key, mine[-1].get("state"))
    how = (ars.get("done") or {}).get(key)
    if how:
        return "the %s %s slot was not run (%s)" % (after, key, how)
    return "the %s %s run has not run yet" % (after, key)


def decide_roles(sch, st, obs, now, act, busy=None):
    """Mutates st["roles"]; calls act(**kw) per action. obs needs: ops() -> status dict|None, account() -> label|None,
    unit_state(unit) -> str, result(run) -> dict|None, off(path) -> first line|None. busy = supervise_roles()'s
    answer (run here when the caller did not)."""
    if busy is None:
        busy = supervise_roles(sch, st, obs, now, act)
    rst = st.setdefault("roles", {})
    by_name = {r.get("name"): r for r in sch.get("roles") or []}
    reading_cache = {}

    def reading():
        if "r" not in reading_cache:
            reading_cache["r"] = ops_reading(obs["ops"](), obs["account"](), now,
                                             sch.get("ops_stale_s", OPS_STALE_S))
        return reading_cache["r"]

    # a role that runs after another is decided after it, so the one it follows is marked/launched first (R, B)
    roles = sorted(sch.get("roles") or [], key=lambda r: 1 if r.get("after_role") else 0)
    for role in roles:
        name = role.get("name", "?")
        if not role.get("enabled"):
            continue
        missing = [k for k in LAUNCH_KEYS if not role.get(k)]
        if missing:
            act(do="alarm", kind="role:" + name, why="role %s is enabled but cannot be launched: no %s in the schedule"
                % (name, ", ".join(missing)))
            continue
        cfg = dict(ROLE_DEFAULTS, **role)
        if cfg.get("after_role") and not (by_name.get(cfg["after_role"]) or {}).get("enabled"):
            act(do="alarm", kind="role:%s:after" % name, ticket=role["ledger_item"], note=True,
                why="role %s runs only after a %s run, and %s is not enabled: its scheduled checks will not run"
                % (name, cfg["after_role"], cfg["after_role"]))
        rs = rst.setdefault(name, {})
        rs.setdefault("done", {})
        rs.setdefault("runs", [])
        # ---- what is due now
        due = []
        for i, (hhmm, mode, cap) in enumerate(slots(cfg)):
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
                        "item": role["ledger_item"], "trigger": "slot %s local" % hhmm})
        if role.get("alarm_runs"):
            open_items = sorted({a.get("item") for a in ((obs["ops"]() or {}).get("alarms") or {}).values()
                                 if a.get("state") == "OPEN" and a.get("item")})
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
                    due.append({"key": "alarm " + item, "slot": None, "first": False, "mode": "alarm",
                                "cap": cfg.get("run_token_cap"), "item": item, "trigger": "ops_watch alarm " + item})
        rs["done"] = {k: v for k, v in rs["done"].items() if k[:10] >= day_of(now - 2 * 86400)}
        if not due:
            continue
        job = due[0]                                      # one launch per role per tick
        off = obs["off"](wsl_path(role.get("off_file") or ""))
        if off is not None:
            mark(rs, job, "off")
            act(do="role_hold", role=name, why="%s %s skipped: off switch %s (%s)" % (
                name, job["trigger"], role.get("off_file"), off or "no reason given"))
            continue
        if name in busy:
            continue                                      # one run at a time: wait for the running one
        wait = after_ready(cfg, rst, busy, job, now, dict(ROLE_DEFAULTS, **(by_name.get(cfg.get("after_role")) or {})))
        if wait:
            if (rs.get("waiting") or [None])[0] != job["key"]:      # journal the wait once, not every tick
                act(do="role_hold", role=name, why="%s %s waits: runs after a finished %s run; %s" % (
                    name, job["trigger"], cfg["after_role"], wait))
            rs["waiting"] = [job["key"], wait]
            continue
        rs.pop("waiting", None)
        r = reading()
        if r["state"] != "MEASURED":
            act(do="alarm", kind="role:%s:ops" % name, ticket=job["item"], note=True,
                why="%s %s REFUSED: %s" % (name, job["trigger"], r["why"]))
            continue
        bname, b = band(cfg, r)
        allowed = b.get("slots", "all")
        if slot_blocked(allowed, job, cfg):
            mark(rs, job, "band " + bname)
            act(do="role_hold", role=name, why="%s %s not run: band %s runs %s scheduled slots (runway %.2f %s, "
                "week left %.0f%%)" % (name, job["trigger"], bname, allowed, r["runway"], r["runway_m"],
                                       r["week_left"]))
            continue
        factor = float(b.get("quick_cap_x", 1.0)) if job["mode"] in ("quick", "run") else 1.0
        if not job["cap"]:
            act(do="alarm", kind="role:" + name, why="role %s has no token cap for %s" % (name, job["mode"]))
            continue
        budget = int(job["cap"] * factor)
        spent = spent_today(rs, now)
        daily = role.get("daily_token_cap")
        if daily and spent + budget > daily:
            mark(rs, job, "daily cap")
            act(do="alarm", kind="role:%s:cap" % name, ticket=job["item"], note=True,
                why="%s %s REFUSED: daily_token_cap %d, %d used today + %d budget" % (
                    name, job["trigger"], daily, spent, budget))
            continue
        mark(rs, job, "launch")
        unit = "rm-role-%s-%d" % (name.lower(), int(now))
        act(do="role_launch", role=name, unit=unit, ticket=job["item"], note=True, mode=job["mode"], budget=budget,
            slot=job["key"], band=bname, seat=role["seat"], run_max_s=cfg["run_max_s"],
            why="%s %s, band %s, budget %d (cap %d x %.1f), %d used today, unit %s, model %s" % (
                name, job["trigger"], bname, budget, job["cap"], factor, spent, unit, role["model"]),
            message=prompt(cfg, job["mode"], job["trigger"], bname, r, budget, job["cap"], factor, spent, unit))
        busy.add(name)            # launched this tick: a role that runs after it waits for it (R, B)


def mark(rs, job, how):
    if job["mode"] == "alarm":
        rs["alarms_seen"] = sorted(set(rs.get("alarms_seen") or []) | {job["item"]})
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
