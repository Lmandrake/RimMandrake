#!/usr/bin/env python3
"""login_watch.py — a lost login is answered inside the Dispatcher tick, in minutes, without any AI (LOGIN_LOSS_FIX_DEAD_SIGNALS).

Why: on 2026-10-30 the live login expired at 05:57Z and nothing answered for 8.1 h. FOUNDRY sat idle, role runs died on
"Failed to authenticate" and spent their daily limits, and the signals that knew went nowhere: account_usage wrote
`auth status failed` 31 times, the Dispatcher journal took 218 `unwakeable` alarms.

Each tick (schedule key `login_watch`; off when absent or enabled false):
  probe      `claude auth status`: rc != 0 or loggedIn false is a failure; a timeout is no reading. confirm_n failures in
             a row are a dead login, so one bad process never holds the fleet. It reads, it never refreshes on purpose,
             and it runs the same command account_usage has run every 15 min since the switch tooling went on HOLD.
  dead       alarm login:expired:<epoch> (ledger note + Conductor log, per outage, again every alarm_every_s) naming the
             healthy logins and the exact way back; rings, recovers and role launches hold through the same gate an
             account switch uses, so dead runs stop eating the daily limits.
  switch     one `claude-account use <account> --confirm <machine>`, detached, only when ALL of: auto_switch true, the
             owner's hold file absent (his word: "Please disable any script that will auto log me out for awhile and
             stay on this account"), the machine armed, no PAUSE, and a healthy login that is not lent exists. Not
             back after switch_verify_s: alarm login:switch_failed, never a second try.
  back       alarm login:back:<epoch>; the gate opens by itself and held work goes.
  stranded   the login works but a seat window still sits on an auth error (its turn ended on the API error, so its
             Stop hook never ran and no ring can reach it): a seat_restart request for it, at most rescues_per_day,
             then an alarm. A Conductor window (kind conductor) is only alarmed: the owner talks to it.

Role runs that die on an auth error: role_launch.supervise_roles gives their slot back (role_launch.AUTH_RX).
"""
import json
import os
import shutil
import subprocess
import tempfile

import seat_restart as SR
import session_match as SM

DEFAULTS = {
    "enabled": False, "confirm_n": 2, "stranded_after_s": 300, "rescues_per_day": 2, "probe_timeout_s": 30,
    "auto_switch": False, "switch_verify_s": 900, "usage_stale_s": 3600, "account_cmd": "claude-account",
    "hold_file": None, "usage_latest": None, "armed_file": None, "machine_file": None}
SCRUB_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "CLAUDE_CODE_OAUTH_TOKEN",
             "CLAUDE_CONFIG_DIR", "CLAUDE_SECURESTORAGE_CONFIG_DIR")    # the login the windows use, nothing else


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
    if r.returncode != 0:
        return False, "auth status exited %d" % r.returncode
    try:
        if not json.loads(r.stdout).get("loggedIn"):
            return False, "auth status says not logged in"
    except (ValueError, AttributeError):
        return None, "auth status unreadable"
    return True, ""


def healthy_logins(cfg, live, lent, now):
    """-> account names with a fresh MEASURED reading through their own login, emptiest week first. The live account
    is left out, and so is a lent one: a machine does not move onto a lent account by itself. Live or lent unknown:
    nothing can be picked."""
    if live is None or lent is None:
        return []
    try:
        with open(cfg["usage_latest"], encoding="utf-8") as f:
            recs = json.load(f).get("accounts") or {}
    except (OSError, ValueError, TypeError, AttributeError):
        return []
    out = []
    for name, r in recs.items():
        if name == live or name in lent or not isinstance(r, dict) or r.get("source") != "MEASURED":
            continue
        at = SR._ts(r.get("measured_at"))
        if at is None or now - at > cfg["usage_stale_s"]:
            continue
        out.append((r.get("week_pct_used") if isinstance(r.get("week_pct_used"), (int, float)) else 100.0, name))
    return [n for _, n in sorted(out)]


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


def stranded(sch, cfg, sessions, now):
    """-> [{seat, sess, path, size, at, conductor}]: seat windows idle on a turn that ended on an auth error."""
    out = []
    for seat, c in (SR.config(sch) or {}).items():
        named = SR._find(sessions, SM.names_of(c))
        if len(named) != 1 or named[0].get("status") != "idle":
            continue
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
        if SR.auth_ended(last) and at is not None and now - at >= cfg["stranded_after_s"]:
            out.append({"seat": seat, "sess": named[0], "path": path, "size": size, "at": at,
                        "conductor": c.get("kind") == "conductor"})
    return out


def rescue_request(w, now):
    """The request file `seat_restart.py request` would write, had the window been able to run it."""
    s = w["sess"]
    return {"seat": w["seat"], "pid": s.get("pid"), "start": SR.reg_start(s), "session_id": s.get("sessionId"),
            "ticket": None, "reason": "window stranded on an expired login, login works again", "ts": now,
            "ctx_tokens": None, "input_ts": None, "tx_offset": w["size"], "tx_path": w["path"]}


def _stranded_step(cfg, sch, L, windows, now, act, iso):
    day = int(now // 86400)
    res = L.setdefault("rescues", {})
    for w in windows:
        seat = w["seat"]
        r = res.get(seat) if (res.get(seat) or {}).get("day") == day else {"day": day, "n": 0}
        if r.get("for") == w["at"]:                   # this error was answered: the restart path reports its own end
            continue
        if w["conductor"] or r["n"] >= cfg["rescues_per_day"]:
            act(do="alarm", kind="login:stranded:" + seat, seat=seat, note=True, conductor_log=True,
                why="%s's window has sat on an auth error since %s although the login works%s" % (
                    seat, iso(w["at"]), "" if w["conductor"] else
                    "; %d automatic restarts today did not clear it" % r["n"]),
                raise_first="%s window needs a look: type anything in it or restart it." % seat)
            continue
        r["n"] += 1
        r["for"] = w["at"]
        res[seat] = r
        act(do="login_rescue", seat=seat, note=True, request=rescue_request(w, now),
            why="%s's window has sat on an auth error since %s and the login works: fresh window requested" % (
                seat, iso(w["at"])))


def step(sch, st, obs, now, act, iso):
    """-> the hold reason while the login is dead, else None. Never raises past the caller's guard for a bad reading:
    a probe with no reading leaves the state as it stands."""
    cfg = config(sch)
    lo = obs.get("login")
    if not cfg["enabled"] or not lo:
        return None
    L = st.setdefault("login", {})
    ok, why = lo["probe"]()
    if ok is None:
        return L.get("hold")                          # blind: an outage stays one, a healthy login stays healthy
    if ok:
        if L.get("dead_since"):
            act(do="alarm", kind="login:back:%d" % L["dead_since"], note=True, conductor_log=True,
                why="the login works again after %.1f h dead (since %s)%s: held rings and role runs go now" % (
                    (now - L["dead_since"]) / 3600.0, iso(L["dead_since"]),
                    "; automatic switch to %s" % L["switched_to"] if L.get("switched_to") else ""),
                raise_first="Nothing to do unless a seat stays idle: stranded windows are restarted next.")
        for k in ("dead_since", "fails", "hold", "alarmed_at", "switch_at", "switched_to", "switch_alarmed", "first_fail"):
            L.pop(k, None)
        agents = obs.get("agents") or {}
        if agents.get("state") == "MEASURED" and lo.get("stranded"):
            _stranded_step(cfg, sch, L, lo["stranded"](agents.get("sessions")), now, act, iso)
        return None
    L["fails"] = L.get("fails", 0) + 1
    L.setdefault("first_fail", now)
    if L["fails"] < cfg["confirm_n"]:
        return None
    L.setdefault("dead_since", L["first_fail"])
    L["hold"] = "login dead since %s (%s)" % (iso(L["dead_since"]), why)
    live, lent = lo["account"]() if lo.get("account") else (None, None)
    good = healthy_logins(cfg, live, lent, now)
    block = switch_block(cfg, obs.get("paused"))
    box = machine(cfg)
    if not block and not (good and box):
        block = "no healthy login to move to" if not good else "machine name unreadable"
    if not block and not L.get("switch_at"):
        L["switch_at"], L["switched_to"] = now, good[0]
        act(do="login_switch", account=good[0], machine=box, command=cfg["account_cmd"], note=True,
            conductor_log=True, kind="login:switch", why="%s: switching the machine to %s by itself" % (L["hold"], good[0]),
            raise_first="Automatic account switch running; every Claude window restarts.")
    if L.get("switch_at"):
        if now - L["switch_at"] > cfg["switch_verify_s"] and not L.get("switch_alarmed"):
            L["switch_alarmed"] = True
            act(do="alarm", kind="login:switch_failed:%d" % L["dead_since"], note=True, conductor_log=True,
                why="%s: the automatic switch to %s did not bring it back in %d s" % (
                    L["hold"], L.get("switched_to"), cfg["switch_verify_s"]),
                raise_first="LOGIN DEAD, automatic switch failed: log in by hand.")
        return L["hold"]
    every = sch.get("alarm_every_s", 6 * 3600)
    if now - L.get("alarmed_at", -1e18) >= every:
        L["alarmed_at"] = now
        way = ("`claude-account use %s --confirm %s` from a plain terminal, or /login in any window" % (good[0], box)
               if good else "/login in any window")
        act(do="alarm", kind="login:expired:%d" % L["dead_since"], note=True, conductor_log=True,
            why="%s; live account %s. No automatic way back: %s. Healthy logins: %s. Rings and role runs are held." % (
                L["hold"], live or "UNMEASURED", block, ", ".join(good) or "none measured"),
            raise_first="LOGIN DEAD, fleet held. Way back: %s." % way)
    return L["hold"]


def run_switch(a, fx=None):
    """Detached, because `use` closes every Claude window and may outlast the tick. -> the journal's result text."""
    argv = ["systemd-run", "--user", "--collect", "--unit", "rm-login-switch-%d" % int(a["epoch"]), a["command"],
            "use", a["account"], "--confirm", a["machine"]]
    if fx:
        return fx(argv)
    r = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    return ("started: " if r.returncode == 0 else "FAILED: ") + (r.stderr or r.stdout).strip()[:200]


def write_rescue(a):
    SR._write_json(SR.request_path(a["seat"]), a["request"])
    return "restart requested"
