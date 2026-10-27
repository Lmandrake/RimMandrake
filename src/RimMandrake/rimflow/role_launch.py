#!/usr/bin/env python3
"""role_launch.py — the Dispatcher's role launcher (item DISPATCHER_BUILD_ROLE_LAUNCH_FROM_SCHEDULE; spec
design/RimMandrake/rimflow_v3_2026-10-26.md §3, §6). dispatcher.decide() calls decide_roles(); dispatcher.execute()
calls launch() / stop(). A program: it decides nothing the schedule and the role files do not say.

What it runs: every role in dispatcher_schedule.json `roles` that is `enabled` AND carries the launch keys
(LAUNCH_KEYS: instructions, seat, clone, model, ledger_item). An enabled role without them (Arbiter, Auditor, ...)
is still an ALARM, as in v3.0: switching on a role nobody can run must be loud.

When: the role's clock slots — `quick_checks_local` (Conductor) or `runs_local` (Operations), local "HH:MM" — each
once per local day, launched in the first tick at or after the slot and no later than `slot_late_s` after it (a
missed slot is journaled, never run late). The slot equal to `economy_pass_local` is the economy pass. Operations
also runs once per ops_watch alarm item FILED after the role was first seen enabled (`alarm_runs`); alarms already
open at that first tick are the baseline, covered by the next running check. One run per role at a time.

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
     ("all" | "first" | "none") says which scheduled slots still run and `quick_cap_x` scales the run's budget.
     A role with no bands (Operations: operations.md writes none) runs at x1.0.
  4. caps: the run's budget = its cap x the band factor; it is REFUSED (alarm) when today's spend plus that budget
     passes `daily_token_cap`. Today's spend = tokens of finished runs + the full budget of runs still going.

Tokens: a finished run's `claude -p --output-format json` usage, ALL FOUR fields (input, cache_creation,
cache_read, output): the conservative reading. A run over its budget is an ALARM after the fact: `claude -p` has no
token stop, so the budget is told to the role in its prompt and checked on its result. A run still going after
`run_max_s` is stopped (its claude_bounded scope and its unit) with an alarm.

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
import os
import subprocess
import sys
import time

LAUNCH_KEYS = ("instructions", "seat", "clone", "model", "ledger_item")
ROLE_DEFAULTS = {"slot_late_s": 3600, "run_max_s": 1800}
OPS_STALE_S = 45 * 60
ACTIVE = ("active", "activating", "deactivating", "reloading")
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


def ops_reading(status, account, now, stale_s=OPS_STALE_S):
    """Pure. status = parsed status.json (or None), account = resolved label (or None).
    -> {"state": "MEASURED", "account", "runway", "runway_m", "week_left", "week_left_m", "at"}
       or {"state": "UNMEASURED", "why"}."""
    if not isinstance(status, dict):
        return {"state": "UNMEASURED", "why": "ops_watch status.json missing or unreadable"}
    at = utc_epoch(status.get("at"))
    if at is None:
        return {"state": "UNMEASURED", "why": "ops_watch status.json has no readable 'at'"}
    if now - at > stale_s:
        return {"state": "UNMEASURED", "why": "ops_watch status.json is STALE: at %s, %d min old (> %d)"
                % (status.get("at"), (now - at) // 60, stale_s // 60)}
    if not account:
        return {"state": "UNMEASURED", "why": "the account this machine runs on is not resolved (registry/live email)"}
    pts = status.get("points") or {}
    out = {"state": "MEASURED", "account": account, "at": status.get("at")}
    for key, name in (("runway", "runway"), ("week_left_pct", "week_left")):
        p = pts.get("accounts.%s.%s" % (account, key)) or {}
        if p.get("m") not in ("MEASURED", "ESTIMATE") or not isinstance(p.get("v"), (int, float)):
            return {"state": "UNMEASURED", "why": "accounts.%s.%s is %s%s" % (
                account, key, p.get("m") or "absent", (" (%s)" % p["why"]) if p.get("why") else "")}
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
    """Pure. usage of a `claude -p --output-format json` result -> total tokens (all four fields) or None."""
    u = (result or {}).get("usage")
    if not isinstance(u, dict):
        return None
    return sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens",
                                             "cache_read_input_tokens", "output_tokens"))


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

def decide_roles(sch, st, obs, now, act):
    """Mutates st["roles"]; calls act(**kw) per action. obs needs: ops() -> status dict|None, account() -> label|None,
    unit_state(unit) -> str, result(run) -> dict|None, off(path) -> first line|None."""
    rst = st.setdefault("roles", {})
    reading_cache = {}

    def reading():
        if "r" not in reading_cache:
            reading_cache["r"] = ops_reading(obs["ops"](), obs["account"](), now,
                                             sch.get("ops_stale_s", OPS_STALE_S))
        return reading_cache["r"]

    for role in sch.get("roles") or []:
        name = role.get("name", "?")
        if not role.get("enabled"):
            continue
        missing = [k for k in LAUNCH_KEYS if not role.get(k)]
        if missing:
            act(do="alarm", kind="role:" + name, why="role %s is enabled but cannot be launched: no %s in the schedule"
                % (name, ", ".join(missing)))
            continue
        cfg = dict(ROLE_DEFAULTS, **role)
        rs = rst.setdefault(name, {})
        rs.setdefault("done", {})
        rs.setdefault("runs", [])
        # ---- runs in flight: finished? over time?
        busy = False
        for run in rs["runs"]:
            if run.get("state") != "running":
                continue
            ustate = obs["unit_state"](run["unit"])
            if ustate in ACTIVE:
                if now - run["at"] >= cfg["run_max_s"]:
                    act(do="role_stop", role=name, unit=run["unit"], scope=run.get("scope"), ticket=run["item"],
                        note=True, why="%s run %s still going after %d s (run_max_s): stopped"
                        % (name, run["unit"], now - run["at"]))
                    act(do="alarm", kind="role:%s:overtime" % name, ticket=run["item"], note=True,
                        why="%s run %s passed run_max_s %d" % (name, run["unit"], cfg["run_max_s"]))
                    run["state"] = "stopped"
                else:
                    busy = True
                continue
            res = obs["result"](run)
            tok = run_tokens(res)
            run["tokens"] = tok
            run["state"] = "failed" if (res is None or res.get("is_error") or tok is None) else "done"
            models = sorted((res or {}).get("modelUsage") or {})
            act(do="role_done", role=name, unit=run["unit"], ticket=run["item"], note=True,
                why="%s %s run %s %s: %s tokens of a %d budget, model %s, %s" % (
                    name, run["mode"], run["unit"], run["state"], tok if tok is not None else "UNMEASURED",
                    run["budget"], ",".join(models) or "?", (res or {}).get("subtype") or "no result"))
            if tok is not None and tok > run["budget"]:
                act(do="alarm", kind="role:%s:overbudget" % name, ticket=run["item"], note=True,
                    why="%s run %s used %d tokens, budget %d" % (name, run["unit"], tok, run["budget"]))
            if run["state"] == "failed":
                act(do="alarm", kind="role:%s:failed" % name, ticket=run["item"], note=True,
                    why="%s run %s ended without a good result (%s)" % (
                        name, run["unit"], ((res or {}).get("result") or run.get("err") or "no result file")[:160]))
        rs["runs"] = [r for r in rs["runs"] if now - r["at"] < 2 * 86400]
        # ---- what is due now
        due = []
        for i, (hhmm, mode, cap) in enumerate(slots(cfg)):
            key = "%s %s" % (day_of(now), hhmm)
            t = slot_epoch(now, hhmm)
            if key in rs["done"] or now < t:
                continue
            if now - t > cfg["slot_late_s"]:
                rs["done"][key] = "missed"
                act(do="role_hold", role=name, why="%s slot %s missed (tick %d s late > slot_late_s)"
                    % (name, hhmm, now - t))
                continue
            due.append({"key": key, "slot": hhmm, "first": i == 0, "mode": mode, "cap": cap,
                        "item": role["ledger_item"], "trigger": "slot %s local" % hhmm})
        if role.get("alarm_runs"):
            open_items = sorted({a.get("item") for a in ((obs["ops"]() or {}).get("alarms") or {}).values()
                                 if a.get("state") == "OPEN" and a.get("item")})
            if "alarms_seen" not in rs:
                rs["alarms_seen"] = open_items           # the baseline at first enable: not run
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
        if busy:
            continue                                      # one run at a time: wait for the running one
        r = reading()
        if r["state"] != "MEASURED":
            act(do="alarm", kind="role:%s:ops" % name, ticket=job["item"], note=True,
                why="%s %s REFUSED: %s" % (name, job["trigger"], r["why"]))
            continue
        bname, b = band(cfg, r)
        allowed = b.get("slots", "all")
        if job["slot"] and (allowed == "none" or (allowed == "first" and not job["first"])):
            mark(rs, job, "band " + bname)
            act(do="role_hold", role=name, why="%s %s not run: band %s runs %s scheduled slots (runway %.2f %s, "
                "week left %.0f%%)" % (name, job["trigger"], bname, allowed, r["runway"], r["runway_m"],
                                       r["week_left"]))
            continue
        factor = float(b.get("quick_cap_x", 1.0)) if job["mode"] == "quick" else 1.0
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
            slot=job["key"], band=bname,
            why="%s %s, band %s, budget %d (cap %d x %.1f), %d used today, unit %s, model %s" % (
                name, job["trigger"], bname, budget, job["cap"], factor, spent, unit, role["model"]),
            message=prompt(cfg, job["mode"], job["trigger"], bname, r, budget, job["cap"], factor, spent, unit))


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
    """-> (ok, out, run-record fields). Starts the transient unit and returns at once."""
    out, err = run_paths(root, unit)
    r = runner(launch_argv(role, unit, msg, out, err, claude), capture_output=True, text=True, timeout=60,
               stdin=subprocess.DEVNULL)
    text = ((r.stdout or "") + (r.stderr or "")).strip()[-200:]
    if r.returncode:
        return False, "systemd-run exit %d: %s" % (r.returncode, text), {}
    pid = runner(["systemctl", "--user", "show", "-p", "MainPID", "--value", unit], capture_output=True, text=True,
                 timeout=30, stdin=subprocess.DEVNULL)
    main_pid = (pid.stdout or "").strip()
    scope = ("claude-seat-%s-%s.scope" % (role["seat"], main_pid)) if main_pid not in ("", "0") else None
    return True, "unit %s started (scope %s)" % (unit, scope or "not yet known"), {
        "out": out, "err": err, "scope": scope, "model_id": model_id(role["model"])}


def unit_state(unit, runner=subprocess.run):
    try:
        r = runner(["systemctl", "--user", "show", "-p", "ActiveState", "--value", unit], capture_output=True,
                   text=True, timeout=30, stdin=subprocess.DEVNULL)
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


def stop(unit, scope, runner=subprocess.run):
    """The claude process lives in claude_bounded's scope (claude-seat-<seat>-<unit MainPID>.scope), outside the
    unit: stopping the unit alone would leave it running."""
    names = [n for n in (scope, unit) if n]
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
