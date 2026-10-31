#!/usr/bin/env python3
"""signal_watch.py -- failure signals nobody acted on get an answer inside the Dispatcher tick; the Conductor hears only
when the answer failed (census: infrastructure/state/items/closed/LOGIN_LOSS_FIX_DEAD_SIGNALS.md).

Each every_s, not under PAUSE (schedule key `signal_watch`; off when absent or enabled false):
  units  (TIMER_FAILED_FIX_AUTO_REPAIR) a failed user unit. A .scope is dead already: reset-failed clears it. A .service
         with a .timer: reset-failed and one start, at most repairs_per_day, so a broken job cannot loop. Past that, or
         a unit there is no safe repair for (no timer, or deny_rx: nothing that can touch a login) standing over
         alarm_after_s: alarm timer:<unit>. rm-scratch-reap.service sat failed 21 h and rm-scratch-bound scopes 47 h.
  files  (STEVE_STALL_FIX_FILE_FAILED_ROUTE) ops_watch retries a failed alarm filing every pass; file_tries failures
         mean the filer is broken, and its error sat in alarms_log.jsonl: alarm ops:file_failed:<aid>.
  flags  (OPS_FLAGS_FIX_NO_ACTION) a flag standing flag_after_s means the digest's readers did not move it: a note to
         Operations; still standing flag_every_s later, the Conductor too. A flag with a known answer is a rule with
         alarm true instead, which files an item for Operations (flow.untriaged_findings, ops_watch_rules.json).
"""
import json
import os
import re
import subprocess

DEFAULTS = {"enabled": False, "every_s": 300, "repairs_per_day": 2, "alarm_after_s": 3600, "file_tries": 3,
            "flag_after_s": 72 * 3600, "flag_every_s": 7 * 86400, "ops_dir": None,
            "deny_rx": "switch|login|logout|account|rm-role-"}


def config(sch):
    return dict(DEFAULTS, **(sch.get("signal_watch") or {}))


def _systemctl(*args, timeout=20):
    return subprocess.run(("systemctl", "--user") + args, capture_output=True, text=True, timeout=timeout)


def read_units():
    """-> (failed unit names, timer names), or None for no reading."""
    try:
        out = []
        for args in (("list-units", "--failed", "--all"), ("list-timers", "--all")):
            r = _systemctl(*args, "--output=json")
            if r.returncode != 0:
                return None
            out.append([u.get("unit") for u in json.loads(r.stdout or "[]")])
    except (OSError, ValueError, AttributeError, subprocess.TimeoutExpired):
        return None
    return out[0], out[1]


def read_json(cfg, name):
    try:
        with open(os.path.join(cfg["ops_dir"], name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError, TypeError):
        return None


def plan(cfg, unit, timers):
    """-> 'reset' | 'start' | None (no safe repair)."""
    if re.search(cfg["deny_rx"], unit):
        return None
    if unit.endswith(".scope"):
        return "reset"
    if unit.endswith(".service") and unit[:-len(".service")] + ".timer" in timers:
        return "start"
    return None


def _units_step(cfg, S, reading, now, act, iso):
    failed, timers = reading
    day = int(now // 86400)
    book = {u: r for u, r in (S.get("units") or {}).items() if u in failed}    # a unit that left is forgotten
    S["units"] = book
    for u in failed:
        r = book.setdefault(u, {"since": now, "day": day, "n": 0})
        if r["day"] != day:
            r.update(day=day, n=0)
        how = plan(cfg, u, timers)
        if how and r["n"] < cfg["repairs_per_day"]:
            r["n"] += 1
            act(do="unit_repair", unit=u, how=how, why="%s failed: %s (%d/%d today)" % (
                u, "restart" if how == "start" else "clear", r["n"], cfg["repairs_per_day"]))
        elif now - r["since"] >= cfg["alarm_after_s"]:
            act(do="alarm", kind="timer:" + u, note=True, conductor_log=True,
                why="%s failed since %s; %s" % (u, iso(r["since"]), "%d automatic repairs today did not hold" % r["n"]
                                                if how else "no safe automatic repair for it"),
                raise_first="%s needs a look: `systemctl --user status %s`." % (u, u))


def _files_step(cfg, alarms, act):
    for aid, a in sorted((alarms or {}).items()):
        if isinstance(a, dict) and a.get("state") != "OPEN" and a.get("error") and a.get("tries", 0) >= cfg["file_tries"]:
            act(do="alarm", kind="ops:file_failed:" + aid, note=True, conductor_log=True,
                why="ops_watch could not file alarm %s after %d tries: %s" % (aid, a["tries"], str(a["error"])[:160]),
                raise_first="An ops alarm is unfiled because its filer is broken.")


def _flags_step(cfg, S, flags, now, act, ts):
    rows = [f for f in (flags or {}).get("flags") or [] if isinstance(f, dict)]
    answered = {f.get("key") for f in rows if f.get("alarm")}      # a rule with alarm true files its own item
    seen = S.setdefault("flags", {})
    for f in rows:
        key, at = f.get("key"), ts(f.get("since"))
        if at is None or key in answered or now - at < cfg["flag_after_s"] or now - seen.get(key, -1e18) < cfg["flag_every_s"]:
            continue
        told = key in seen
        seen[key] = now
        extra = {"conductor_log": True, "raise_first": "A trend has stood for days and its Operations note did not move it."} if told else {}
        act(do="alarm", kind="ops:flag:%s" % key, note=True,
            why="ops flag %s has stood %.0f h: %s" % (key, (now - at) / 3600.0, str(f.get("detail"))[:160]), **extra)


def step(sch, st, obs, now, act, iso, ts):
    cfg = config(sch)
    so = obs.get("signals")
    if not cfg["enabled"] or not so or obs.get("paused"):
        return
    S = st.setdefault("signals", {})
    if now - S.get("at", -1e18) < cfg["every_s"]:
        return
    S["at"] = now
    reading = so["units"]()
    if reading is None:
        act(do="alarm", kind="signal:units", note=True, why="systemctl gave no reading: failed units unseen this pass")
    else:
        _units_step(cfg, S, reading, now, act, iso)
    _files_step(cfg, so["alarms"](), act)
    _flags_step(cfg, S, so["flags"](), now, act, ts)


def give_back(st, a):
    r = ((st.get("signals") or {}).get("units") or {}).get(a["unit"])
    if r:
        r["n"] = max(0, r["n"] - 1)


def repair(a, fx=None):
    """-> the journal's result text; 'FAILED: ...' when systemctl refused."""
    steps = [("reset-failed", a["unit"])] + ([("start", "--no-block", a["unit"])] if a["how"] == "start" else [])
    for args in steps:
        try:
            r = fx(args) if fx else _systemctl(*args)
        except (OSError, subprocess.TimeoutExpired) as e:
            return "FAILED: %s: %s" % (args[0], type(e).__name__)
        if r.returncode != 0:
            return "FAILED: %s: %s" % (args[0], (r.stderr or "").strip()[:160])
    return "repaired: %s %s" % (a["how"], a["unit"])
