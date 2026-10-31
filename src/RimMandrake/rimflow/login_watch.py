#!/usr/bin/env python3
"""login_watch.py — a lost login is answered inside the Dispatcher tick, in minutes, without any AI (LOGIN_LOSS_FIX_DEAD_SIGNALS).

Why: on 2026-10-30 the live login expired at 05:57Z and nothing answered for 8.1 h. FOUNDRY sat idle, role runs died on
"Failed to authenticate" and spent their daily limits, and the signals that knew went nowhere: account_usage wrote
`auth status failed` 31 times, the Dispatcher journal took 218 `unwakeable` alarms.

Each tick (schedule key `login_watch`; off when absent or enabled false):
  probe      `claude auth status`: loggedIn false, or a failed run that says the login is gone, is a failure; a crash or
             a timeout is no reading, and blind_alarm_n of those in a row alarm login:blind, so a changed CLI cannot
             hide an outage. confirm_n failures in a row are a dead login, so one bad process never holds the fleet.
             It reads, it never refreshes on purpose, and it runs the same command account_usage has run every 15 min
             since the switch tooling went on HOLD.
  dead       alarm login:expired:<epoch> (ledger note + Conductor log, per outage, again every alarm_every_s) naming the
             healthy logins and the exact way back; rings, recovers and role launches hold through the same gate an
             account switch uses, so dead runs stop eating the daily limits.
  switch     one `claude-account use <account> --confirm <machine>`, detached, only when ALL of: auto_switch true, the
             owner's hold file absent (his word: "Please disable any script that will auto log me out for awhile and
             stay on this account"), the machine armed, no PAUSE, and a healthy login that is not lent and is over the
             account_pick target_min week line exists; hold and PAUSE are read again at release. Not back after
             switch_verify_s, or systemd-run refused: alarm login:switch_failed, every alarm_every_s until the login is
             back, never a second try.
  back       alarm login:back:<epoch>; the gate opens by itself and held work goes.
  stranded   the login works but a seat window still sits on an API error (its turn ended on it, so its Stop hook never
             ran and no ring can reach it): a seat_restart request for it, at most rescues_per_day, then an alarm. A
             request cancelled or a restart that left the same error standing alarms after rescue_wait_s. A
             Conductor window (kind conductor) is only alarmed: the owner talks to it. An auth or server error waits
             stranded_after_s, a rate limit waits for the reset its message names, or limit_wait_s when it names none
             (RATE_LIMIT_FIX_STRANDED_WINDOWS; 200 such records in transcripts, 10-2026).

Role runs that die on an auth error: role_launch.supervise_roles gives their slot back (role_launch.AUTH_RX).
"""
import json
import datetime
import os
import re
import shutil
import subprocess
import tempfile
import zoneinfo

import account_pick as AP
import seat_restart as SR
import session_match as SM

DEFAULTS = {
    "enabled": False, "confirm_n": 2, "blind_alarm_n": 5, "stranded_after_s": 300, "limit_wait_s": 5 * 3600, "rescue_wait_s": 2 * 3600, "rescues_per_day": 2, "probe_timeout_s": 30,
    "auto_switch": False, "switch_verify_s": 900, "usage_stale_s": 3600, "account_cmd": "claude-account",
    "hold_file": None, "usage_latest": None, "armed_file": None, "machine_file": None}
SCRUB_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "CLAUDE_CODE_OAUTH_TOKEN",
             "CLAUDE_CONFIG_DIR", "CLAUDE_SECURESTORAGE_CONFIG_DIR")    # the login the windows use, nothing else


RESET_RX = re.compile(r"resets (?:(?P<mon>[A-Z][a-z]{2}) (?P<day>\d{1,2}),? (?:at )?)?(?P<h>\d{1,2})(?::(?P<m>\d{2}))?\s*(?P<ap>am|pm) \((?P<tz>[\w/+-]+)\)", re.I)
GONE_RX = re.compile(r"not logged in|log ?in expired|session expired|please (run|log)", re.I)


def config(sch):
    return dict(DEFAULTS, **(sch.get("login_watch") or {}))


def probe(claude, timeout=30):
    """-> (True | False | None, why). None: no reading (a timeout, a missing binary), which proves nothing."""
    cwd = tempfile.mkdtemp(prefix="login-watch-")
    try:
        r = subprocess.run([claude, "auth", "status"], cwd=cwd, capture_output=True, text=True, timeout=timeout,
                           env={k: v for k, v in os.environ.items() if k not in SCRUB_ENV})
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, "auth status gave no reading: %s" % type(e).__name__
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
    try:
        said = json.loads(r.stdout)
    except ValueError:
        said = None
    state = said.get("loggedIn") if isinstance(said, dict) else None
    if isinstance(state, bool):                       # an error object has no loggedIn: that is no reading
        return (True, "") if state else (False, "auth status says not logged in")
    said = "%s %s" % (r.stdout, r.stderr)
    if r.returncode != 0 and GONE_RX.search(said):
        return False, "auth status exited %d: %s" % (r.returncode, said.strip()[:120])
    return None, "auth status unreadable (exit %d): %s" % (r.returncode, said.strip()[:120])


def healthy_logins(cfg, live, lent, now, rule=None):
    """-> account names with a fresh MEASURED reading through their own login, over account_pick's target_min week
    line, the owner's priority first, then emptiest week. AP.pick cannot answer this: it needs a MEASURED reading of
    the current account, and a dead login has none. The live account is left out, and so is a lent one: a machine does
    not move onto a lent account by itself. Live or lent unknown: nothing can be picked."""
    if live is None or lent is None:
        return []
    try:
        with open(cfg["usage_latest"], encoding="utf-8") as f:
            recs = json.load(f).get("accounts") or {}
    except (OSError, ValueError, TypeError, AttributeError):
        return []
    if not isinstance(recs, dict):
        return []
    rule = rule or {}
    floor = (rule.get("target_min") or {}).get("week_left_pct_ge", 0)
    prio = (AP.load_priority(rule) if rule else None) or []
    out = []
    for name, r in recs.items():
        if name == live or name in lent or not isinstance(r, dict) or r.get("source") != "MEASURED":
            continue
        at = SR._ts(r.get("measured_at"))
        if at is None or now - at > cfg["usage_stale_s"]:
            continue
        used = r.get("week_pct_used")
        if not isinstance(used, (int, float)) or 100.0 - used < floor:
            continue
        out.append((prio.index(name) if name in prio else len(prio), used, name))
    return [n for _, _, n in sorted(out)]


def switch_block(cfg, paused):
    """-> why no automatic switch may run, or None."""
    if not cfg.get("auto_switch"):
        return "auto_switch is off"
    if not cfg.get("hold_file") or os.path.exists(cfg["hold_file"]):
        return "the owner's switching HOLD stands (%s)" % cfg.get("hold_file")
    if paused:
        return "PAUSE is on"
    if not cfg.get("armed_file") or not os.path.exists(cfg["armed_file"]):
        return "this machine is not armed for switching"
    return None


def machine(cfg):
    try:
        with open(cfg["machine_file"], encoding="utf-8") as f:
            return json.load(f).get("machine")
    except (OSError, ValueError, TypeError, AttributeError):
        return None


def limit_reset(text, at):
    """`You've hit your session limit · resets 1:10pm (America/Los_Angeles)`, or the weekly `resets Oct 31, 5pm (...)`
    -> the first such moment after at, or None. Both passes of an hour the autumn clock change repeats are tried."""
    m = RESET_RX.search(text or "")
    if not m:
        return None
    try:
        tz = zoneinfo.ZoneInfo(m["tz"])
        hour = int(m["h"]) % 12 + (12 if m["ap"].lower() == "pm" else 0)
        base = datetime.datetime.fromtimestamp(at, tz).replace(hour=hour, minute=int(m["m"] or 0), second=0, microsecond=0)
        if m["mon"]:
            month, day = datetime.datetime.strptime(m["mon"], "%b").month, int(m["day"])
            days = [base.replace(month=month, day=day), base.replace(year=base.year + 1, month=month, day=day)]
        else:
            days = [base, base + datetime.timedelta(days=1)]
    except (ValueError, OSError, zoneinfo.ZoneInfoNotFoundError):
        return None
    return min((t for t in (d.replace(fold=f).timestamp() for d in days for f in (0, 1)) if t > at), default=None)


def _record_text(rec):
    c = (rec.get("message") or {}).get("content")
    return " ".join(b.get("text") or "" for b in c if isinstance(b, dict)) if isinstance(c, list) else str(c or "")


def stranded(sch, cfg, sessions, now):
    """-> [{seat, sess, start, path, size, at, error, conductor}]: seat windows idle on a turn an API error ended, due."""
    out = []
    for seat, c in (SR.config(sch) or {}).items():
        named = SR._find(sessions, SM.names_of(c))
        if len(named) != 1 or named[0].get("status") != "idle":
            continue
        start = SR.reg_start(SR.session_file(named[0].get("pid")))   # `claude agents` does not carry procStart
        path = SR.transcript_for(named[0], c)
        try:
            recs = SR._tail_records(path, 1 << 17)
            size = os.path.getsize(path)
        except (OSError, SR.Malformed, TypeError):
            continue
        last = None
        for r in recs:
            if r.get("type") in ("user", "assistant") and not r.get("isSidechain"):
                last = r
        at = SR._ts((last or {}).get("timestamp"))
        err = SR.api_ended(last)
        if not err or at is None:
            continue
        due = at + cfg["stranded_after_s"]
        if err == "rate_limit":
            due = max(due, limit_reset(_record_text(last), at) or at + cfg["limit_wait_s"])
        if now >= due:
            out.append({"seat": seat, "sess": named[0], "start": start, "path": path, "size": size, "at": at, "error": err,
                        "conductor": c.get("kind") == "conductor"})
    return out


def rescue_request(w, now):
    """The request file `seat_restart.py request` would write, had the window been able to run it."""
    s = w["sess"]
    return {"seat": w["seat"], "pid": s.get("pid"), "start": w["start"], "session_id": s.get("sessionId"),
            "ticket": None, "reason": "window stranded on %s, the way is clear again" % w.get("error", "an API error"), "ts": now,
            "ctx_tokens": None, "input_ts": None, "tx_offset": w["size"], "tx_path": w["path"]}


def _stranded_step(cfg, sch, L, windows, now, act, iso):
    day = int(now // 86400)
    res = L.setdefault("rescues", {})
    for w in windows:
        seat = w["seat"]
        r = res.get(seat) or {}
        if r.get("day") != day:                       # a new day resets the count, never the answered error
            r = dict(r, day=day, n=0)
        answered = r.get("for") == w["at"]
        if answered and now - r.get("at", now) < cfg["rescue_wait_s"]:     # the restart path has its time to end this
            continue
        if answered or w["conductor"] or w["start"] is None or r["n"] >= cfg["rescues_per_day"]:
            act(do="alarm", kind="login:stranded:" + seat, seat=seat, note=True, conductor_log=True,
                why="%s's window has sat on %s since %s although the way is clear%s" % (
                    seat, w.get("error", "an API error"), iso(w["at"]), "" if w["conductor"] else
                    "; the restart requested for this error did not clear it" if answered else
                    "; its session file gives no birth record to restart it by" if w["start"] is None else
                    "; %d automatic restarts today did not clear it" % r["n"]),
                raise_first="%s window needs a look: type anything in it or restart it." % seat)
            continue
        r["n"] += 1
        r["for"], r["at"] = w["at"], now
        res[seat] = r
        act(do="login_rescue", seat=seat, note=True, request=rescue_request(w, now),
            why="%s's window has sat on %s since %s and the way is clear: fresh window requested" % (
                seat, w.get("error", "an API error"), iso(w["at"])))


def way_back(good, box):
    """Never /login in a window: every machine-wide Remote Control drop on record was one (~/.claude/CLAUDE.md)."""
    if good and box:
        return "`claude-account use %s --confirm %s` from a plain terminal" % (good[0], box)
    return "`claude auth login` from a plain terminal, not /login in a window"


def give_back(st, a, spent=False):
    """A login_switch or login_rescue decided but never done: its state goes back, so the next tick decides again.
    spent: the rescue was tried and failed, so it keeps its place in the day's limit."""
    L = st.get("login") or {}
    if a["do"] == "login_switch":
        L.pop("switch_at", None)
        L.pop("switched_to", None)
        return
    r = (L.get("rescues") or {}).get(a["seat"])
    if r:
        r.pop("for", None)
        if not spent:
            r["n"] = max(0, r["n"] - 1)


def switch_failed(st):
    """systemd-run refused: the switch will not come back, so the failed alarm need not wait out switch_verify_s."""
    st.setdefault("login", {})["switch_at"] = 0


def step(sch, st, obs, now, act, iso):
    """-> the hold reason while the login is dead, else None. Never raises past the caller's guard for a bad reading:
    a probe with no reading leaves the state as it stands."""
    cfg = config(sch)
    lo = obs.get("login")
    if not cfg["enabled"] or not lo:
        return None
    L = st.setdefault("login", {})
    ok, why = lo["probe"]()
    if ok is None:                                    # blind: an outage stays one, a healthy login stays healthy
        L["blind"] = L.get("blind", 0) + 1
        if L["blind"] >= cfg["blind_alarm_n"]:        # the Dispatcher rate-limits by kind
            act(do="alarm", kind="login:blind", note=True, conductor_log=True,
                why="the login cannot be read, %d ticks running: %s" % (L["blind"], why),
                raise_first="Login watch is blind: a dead login would go unseen until this is fixed.")
        return L.get("hold")
    L.pop("blind", None)
    if ok:
        if L.get("dead_since"):
            act(do="alarm", kind="login:back:%d" % L["dead_since"], note=True, conductor_log=True,
                why="the login works again after %.1f h dead (since %s)%s: held rings and role runs go now" % (
                    (now - L["dead_since"]) / 3600.0, iso(L["dead_since"]),
                    "; automatic switch to %s" % L["switched_to"] if L.get("switched_to") else ""),
                raise_first="Nothing to do unless a seat stays idle: stranded windows are restarted next.")
        for k in ("dead_since", "fails", "hold", "switch_at", "switched_to", "first_fail"):
            L.pop(k, None)
        agents = obs.get("agents") or {}
        if agents.get("state") == "MEASURED" and lo.get("stranded") and not obs.get("paused"):
            _stranded_step(cfg, sch, L, lo["stranded"](agents.get("sessions")), now, act, iso)
        return None
    L["fails"] = L.get("fails", 0) + 1
    L.setdefault("first_fail", now)
    if L["fails"] < cfg["confirm_n"]:
        return None
    L.setdefault("dead_since", L["first_fail"])
    L["hold"] = "login dead since %s (%s)" % (iso(L["dead_since"]), why)
    live, lent = lo["account"]() if lo.get("account") else (None, None)
    good = healthy_logins(cfg, live, lent, now, sch.get("account_pick"))
    block = switch_block(cfg, obs.get("paused"))
    box = machine(cfg)
    if not block and not (good and box):
        block = "no healthy login to move to" if not good else "machine name unreadable"
    if not block and "switch_at" not in L:            # by key: a refused switch is 0, tried and owed its alarm
        L["switch_at"], L["switched_to"] = now, good[0]
        act(do="login_switch", account=good[0], machine=box, command=cfg["account_cmd"], note=True,
            conductor_log=True, kind="login:switch", why="%s: switching the machine to %s by itself" % (L["hold"], good[0]),
            raise_first="Automatic account switch running; every Claude window restarts.")
    if "switch_at" in L:
        if now - L["switch_at"] > cfg["switch_verify_s"]:     # the Dispatcher repeats it every alarm_every_s
            act(do="alarm", kind="login:switch_failed:%d" % L["dead_since"], note=True, conductor_log=True,
                why="%s: the automatic switch to %s did not bring it back" % (L["hold"], L.get("switched_to")),
                raise_first="LOGIN DEAD, automatic switch failed. Way back: %s." % way_back(good, box))
        return L["hold"]
    act(do="alarm", kind="login:expired:%d" % L["dead_since"], note=True, conductor_log=True,   # rate-limited by kind
        why="%s; live account %s. No automatic way back: %s. Healthy logins: %s. Rings and role runs are held." % (
            L["hold"], live or "UNMEASURED", block, ", ".join(good) or "none measured"),
        raise_first="LOGIN DEAD, fleet held. Way back: %s." % way_back(good, box))
    return L["hold"]


def run_switch(a, fx=None):
    """Detached, because `use` closes every Claude window and may outlast the tick. -> the journal's result text."""
    argv = ["systemd-run", "--user", "--collect", "--unit", "rm-login-switch-%d" % int(a["epoch"]), a["command"],
            "use", a["account"], "--confirm", a["machine"]]
    if fx:
        return fx(argv)
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as e:
        return "FAILED: %s" % type(e).__name__
    return ("started: " if r.returncode == 0 else "FAILED: ") + (r.stderr or r.stdout).strip()[:200]


def write_rescue(a):
    SR._write_json(SR.request_path(a["seat"]), a["request"])
    return "restart requested"
