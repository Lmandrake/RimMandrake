#!/usr/bin/env python3
"""signal_watch.py -- failure signals nobody acted on get an answer inside the Dispatcher tick; the Conductor hears only
when the answer failed (census: infrastructure/state/items/closed/LOGIN_LOSS_FIX_DEAD_SIGNALS.md).

Each every_s, not under PAUSE (schedule key `signal_watch`; off when absent or enabled false):
  units  (TIMER_FAILED_FIX_AUTO_REPAIR) a failed user unit. A .scope is dead already: reset-failed clears it. A service
         named by restart_rx (an allow list: a timer alone says nothing about what an early start does, so nightly and
         login-adjacent jobs stay out) with its .timer: reset-failed and one start, at most repairs_per_day, so a broken
         job cannot loop. Past that, or any other unit standing over alarm_after_s: alarm timer:<unit>. deny_rx wins over
         both. rm-scratch-reap.service sat failed 21 h and rm-scratch-bound scopes 47 h.
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
            "flag_after_s": 72 * 3600, "flag_every_s": 7 * 86400, "flags_stale_s": 6 * 3600, "ops_dir": None,
            "restart_rx": "^(rm-scratch-reap|rm-pulse-update)\\.service$",
            "deny_rx": "(?i)switch|login|logout|account|rm-role-"}


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
    if re.search(cfg["restart_rx"], unit) and unit[:-len(".service")] + ".timer" in timers:
        return "start"
    return None


def _units_step(cfg, S, reading, now, act, iso):
    failed, timers = reading
    day = int(now // 86400)
    old = S.get("units") if isinstance(S.get("units"), dict) else {}
    # a unit that left stays booked for its day: a repair that holds five minutes must still count against the cap
    book = {u: r for u, r in old.items() if u in failed or r.get("day") == day}
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
                why="%s first failed %s; %s" % (u, iso(r["since"]), "%d automatic repairs today did not hold" % r["n"]
                                                if how else "no safe automatic repair for it"),
                raise_first="%s needs a look: `systemctl --user status %s`." % (u, u))


def _files_step(cfg, alarms, act):
    for aid, a in sorted(alarms.items()):
        if not isinstance(a, dict) or a.get("state") == "OPEN" or not a.get("error"):
            continue
        tries = a.get("tries")
        if isinstance(tries, int) and tries >= cfg["file_tries"]:
            act(do="alarm", kind="ops:file_failed:" + aid, note=True, conductor_log=True,
                why="ops_watch could not file alarm %s after %d tries: %s" % (aid, tries, str(a["error"])[:160]),
                raise_first="An ops alarm is unfiled because its filer is broken.")


def _flags_step(cfg, S, flags, now, act, ts):
    rows = [f for f in flags.get("flags") or [] if isinstance(f, dict)]
    answered = {f.get("key") for f in rows if f.get("alarm")}      # a rule with alarm true files its own item
    # a flag that cleared is forgotten: its next rising is a new incident, and the state cannot outgrow the live flags
    seen = {k: t for k, t in (S.get("flags") or {}).items() if k in {f.get("key") for f in rows}}
    S["flags"] = seen
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

    def guarded(name, fn):    # one bad source costs its own watch, said aloud, never the other two
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            act(do="alarm", kind="signal:" + name, note=True, conductor_log=True,
                why="signal watch: %s raised %s: %s" % (name, type(e).__name__, str(e)[:200]),
                raise_first="A signal watch is blind.")

    def blind(name, why):
        act(do="alarm", kind="signal:" + name, note=True, conductor_log=True, why="signal watch blind: " + why,
            raise_first="A signal watch is blind.")

    def read(name):           # a reader that raises is a reader with no reading
        try:
            return so[name]()
        except Exception:  # noqa: BLE001
            return None

    reading = read("units")
    if reading is None:
        blind("units", "systemctl gave no reading, failed units unseen this pass")
    else:
        guarded("units", lambda: _units_step(cfg, S, reading, now, act, iso))
    alarms = read("alarms")
    if not isinstance(alarms, dict):
        blind("alarms", "alarms.json unreadable, unfiled alarms unseen this pass")
    else:
        guarded("alarms", lambda: _files_step(cfg, alarms, act))
    flags = read("flags")
    try:
        at = ts(flags.get("at")) if isinstance(flags, dict) else None
    except Exception:  # noqa: BLE001
        at = None
    if at is None or now - at > cfg["flags_stale_s"]:      # a frozen snapshot is no standing flag
        blind("flags", "flags.json unreadable or stale (written %s)" % (iso(at) if at is not None else "unknown"))
    else:
        guarded("flags", lambda: _flags_step(cfg, S, flags, now, act, ts))


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
