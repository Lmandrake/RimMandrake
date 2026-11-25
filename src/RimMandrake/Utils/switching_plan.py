#!/usr/bin/env python3
"""The standard switching plan engine (ACCOUNTS_PLAN_BUILD_STANDARD_SWITCHING): which Claude account this machine
burns, read every pass from the meter (account_usage.py) and the rules in switching_plan.json. No LLM, no dates in
code: reset times come from the meter each week.

Each pass:
  target = the owner's fixed priority (10:15: steven after his reset to 50%, then system, then lukas): the first
           account in plan order that is MEASURED, fresh, inside its window (steven: the first 48 h after his
           reset) and above its line (steven: leave_pct_left; others: the switch-away floor, 1%, while another
           account can take over, else the wait floor, 2%). A lower account's budget that expires first is lost.
  target != live  -> arm, `claude-account use <target>`, disarm (once per transition and target week: a marker)
  target == live  -> normal, or SOFT at line + soft_margin (allocator gives 0 new helpers; seats publish and finish),
                     or SOFT when an earlier account's reset (which will pull the machine to it) is near
  no target       -> HARD STOP once per account-week: arm, `claude-account fleet-stop`, disarm; fleet-start when a
                     reset gives the live account headroom again
Near a line, or when a reading is old, an ESTIMATE, or from before a reset that has passed, the pass polls the meter
itself first and never acts on the old figure. Blind meter = 0%: once an account's last MEASURED figure is at or under
floors.blind_zero_pct, a blind reading of it (ESTIMATE, stale) counts as 0% at once: an exhausted account often cannot
be read at all, and the engine never sits waiting on a meter that cannot see it.

A switch the plan did not make is respected (owner's account ruling, ACCOUNTPLAN_FIX_UNDOES_SWITCH_IN_FOUR_MIN: `use lukas`
at 11:26 was undone by this engine at 11:30): the switcher's own log names the last switch; when no transition marker of
ours accounts for it, that account stays live, whatever the priority or a reset would pull to, until it is spent (at its
line, past its window) or the next switch. A failover (login_watch) reads the same, on purpose: the log
cannot tell them from his hand, and leaving a working account alone is the safe way to be wrong.

Live runs finish (owner 2026-11-20: "And yes for live runs finish past, absolutely. Actually 0.1% is even ok kept. We
just don't want to crash to zero and get stuck."): `claude-account use` and `fleet-stop` stop every Claude process, so
a switch or a stop that falls due WAITS while a detached run is live (the pass reads `soft` with `drain`). A switch made
above the line (a priority or reset pull) waits at most pull_drain_max_s. Live runs that cannot be read count as live.

The end of an account (owner 2026-11-24; account_end.py, page design/specs/2026-11-24-account-end/boundary.md): the
account is used down to its own line. At the warning line (2%, 3% at a fast or unread burn; an account kept above zero:
its own line, one point more at a fast burn) every live run is warned, with the percent, the burn and the minutes to
the line: it saves a note, publishes what is done and keeps working. New work still starts, and a run that starts
there gets the same warning in its start package. At the line the switch goes: at 1% with a run live every run is told
to record its state at once, the pass pauses (sized from the burn, 3 min at most), and the switch goes. An account
whose line is above 1% has no pause at its line: its runs are told to save and end, and the switch goes when the last
has ended (or at 1%, if its line is at most emergency_max_line). While an account ends, the pass repeats each minute
inside its 5-min beat.

Brake: a file HOLD in the output dir makes every pass passive (the owner's or an agent's brake); it is the only
gate.

    switching_plan.py check [--dry-run]   one pass (the timer runs this every 5 min)
    switching_plan.py status [--rate R] [--model M]   what the next pass would do (as a run of M sees each level), the pool, the notice and the week ahead
                                          (simulate() at R %/h, default the pool's pace); acts on nothing
    its timer: src/RimMandrake/Utils/systemd/account-plan.{service,timer} (ops_clocks.py install account-plan --apply --enable)

Env seams (selftests): RM_SWITCH_PLAN (plan json), RM_SWITCH_PLAN_DIR (output dir), RM_CLAUDE_ACCOUNT (switcher),
RM_ACCOUNTS_DIR (the switcher's folder, whose log.jsonl names the last switch).
"""
import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN_PATH = Path(os.environ.get("RM_SWITCH_PLAN", HERE / "switching_plan.json"))
LIVE_OUT = Path("/mnt/d/ClaudeWork/rimmandrake/switching_plan")
OUT = Path(os.environ.get("RM_SWITCH_PLAN_DIR", LIVE_OUT))
CA = os.environ.get("RM_CLAUDE_ACCOUNT") or str(Path.home() / ".local/bin/claude-account")
SWITCH_LOG = Path(os.environ.get("RM_ACCOUNTS_DIR", Path.home() / ".claude-accounts")) / "log.jsonl"
UNIT = "account-plan"   # outside the rm-*/testq-* glob of timers_guard on purpose: nothing else restarts or stops it
WEEK = 7 * 86400
STALE_PENDING_S = 2400  # arm + use + disarm at 600 s each plus the reads: a pending marker older is a pass that died
NOTICE_FRESH_S = 20 * 60  # readers (slot_allocator) ignore an older notice: the timer stopped
DRY = False
clock = time.time  # a seam: check() re-reads it after the slow poll
sleep = time.sleep  # a seam: the pause before an emergency switch, and the repeats while an account ends
sys.path.insert(0, str(HERE))
import account_end as AE  # noqa: E402


# ------------------------------------------------------------------ small helpers
def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).astimezone().isoformat(timespec="seconds")


def epoch(s):
    try:
        return datetime.fromisoformat(str(s)).timestamp() if s else None
    except ValueError:
        return None


def load_plan(path=None) -> dict:
    return json.loads(Path(path or PLAN_PATH).read_text())


def write_atomic(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True))
    os.replace(tmp, path)


def read_json(path: Path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def load_state() -> dict:
    return read_json(OUT / "state.json", {}) or {}


def save_state(st: dict) -> None:
    write_atomic(OUT / "state.json", st)


def read_markers() -> dict:
    d = OUT / "markers"
    out = {}
    if d.is_dir():
        for p in d.glob("*.json"):
            v = read_json(p)
            if isinstance(v, dict):
                out[p.stem] = v
    return out


def write_marker(key: str, obj: dict) -> None:
    write_atomic(OUT / "markers" / f"{key}.json", obj)


def log(rec: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rec["at"] = iso(time.time())
    if DRY:
        rec["dry"] = True
    with open(OUT / "log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    print(json.dumps(rec, sort_keys=True))


# ------------------------------------------------------------------ the meter, read
def next_reset(r: dict, now: float):
    """Epoch of the account's next weekly reset: the recorded one, rolled a week on while it has passed."""
    rs = epoch((r or {}).get("week_resets_at"))
    if rs is None:
        return None
    while rs <= now:
        rs += WEEK
    return rs


def reset_passed(r: dict, now: float) -> bool:
    """The reading is from before a reset that has since landed: its figures say nothing about now."""
    rs = epoch((r or {}).get("week_resets_at"))
    return rs is not None and rs <= now


def usable(r) -> bool:
    return bool(r) and r.get("source") == "MEASURED" and not r.get("stale") and r.get("week_pct_left") is not None


def blind_zero(plan: dict, r, now: float) -> bool:
    """Blind meter = 0% (owner 2026-10-28 11:2x, relayed): a reading the meter cannot refresh (ESTIMATE, stale) whose
    last MEASURED figure was at or under blind_zero_pct, inside the same week, counts as exhausted."""
    p = (r or {}).get("week_pct_left")
    return (bool(r) and not usable(r) and p is not None and not reset_passed(r, now)
            and p <= plan["floors"].get("blind_zero_pct", -1))


def left(plan: dict, r, now: float):
    """week_pct_left as the engine believes it: 0 for a blind near-empty account."""
    return 0.0 if blind_zero(plan, r, now) else (r or {}).get("week_pct_left")


# ------------------------------------------------------------------ dated exceptions (pure)
EXC_KEYS = {"id", "from", "until", "ends_at_reset_of", "order", "accounts"}
EXC_RULES = {"leave_pct_left", "window_h_after_reset"}
EXC_MAX_S = WEEK  # [D] an exception is temporary: at most one week from its `from` (a standing change is a plan edit)


def _stamp(s):
    """Epoch of an ISO time that carries its UTC offset, else None (a naive time would be read in the host's zone)."""
    try:
        d = datetime.fromisoformat(str(s))
    except (TypeError, ValueError):
        return None
    return d.timestamp() if d.tzinfo is not None else None


def exception_problems(plan: dict) -> list:
    """The guard on plan["exceptions"]: one line per refused exception (by id). A refused exception is never applied;
    the standing plan stands. Two exceptions whose spans overlap are both refused (which one wins is not data)."""
    return _guard(plan)[0]


def _guard(plan: dict):
    """-> (problems, the exceptions that pass: [(exception, from, until)])."""
    exc = plan.get("exceptions", [])
    if not isinstance(exc, list):
        return ["exceptions: not a list"], []
    out, good = [], []
    order = plan.get("order") or []
    for i, e in enumerate(exc):
        eid = e.get("id") if isinstance(e, dict) else None
        tag = f"exception {eid or '#%d' % i}"
        if not isinstance(e, dict) or not eid:
            out.append(f"{tag}: needs an id")
            continue
        bad = []
        f, u = _stamp(e.get("from")), _stamp(e.get("until"))
        if f is None:
            bad.append("`from` must be an ISO time with its UTC offset")
        if u is None:
            bad.append("`until` (its expiry) must be an ISO time with its UTC offset")
        if f is not None and u is not None and not 0 < u - f <= EXC_MAX_S:
            bad.append(f"`until` must fall after `from` and within {EXC_MAX_S // 86400} days of it")
        if not any(isinstance(v, str) and v.strip() for k, v in e.items() if k.startswith("_")):
            bad.append("needs its provenance in a `_why`")
        extra = sorted(k for k in e if k not in EXC_KEYS and not k.startswith("_"))
        if extra:
            bad.append(f"unknown keys {extra}")
        if "order" not in e and "accounts" not in e:
            bad.append("changes nothing (no `order`, no `accounts`)")
        if "order" in e and (not isinstance(e["order"], list) or sorted(map(str, e["order"])) != sorted(order)
                             or len(set(e["order"])) != len(e["order"])):
            bad.append(f"`order` must reorder the standing accounts {order}")
        if e.get("ends_at_reset_of") is not None and e["ends_at_reset_of"] not in order:
            bad.append("`ends_at_reset_of` names no account of the plan")
        accs = e.get("accounts", {})
        if not isinstance(accs, dict):
            bad.append("`accounts` must be a map")
            accs = {}
        for n, cfg in accs.items():
            if n not in order or not isinstance(cfg, dict) or not cfg:
                bad.append(f"`accounts.{n}` is no account of the plan or sets nothing")
                continue
            for k, v in cfg.items():
                if k.startswith("_"):
                    continue
                num = isinstance(v, (int, float)) and not isinstance(v, bool)
                if k not in EXC_RULES:
                    bad.append(f"`accounts.{n}.{k}` is not a rule an exception may set {sorted(EXC_RULES)}")
                elif k == "leave_pct_left" and not (num and 0 <= v <= 100):
                    bad.append(f"`accounts.{n}.leave_pct_left` must be a number in [0, 100]")
                elif k == "window_h_after_reset" and v is not None and not (num and 0 < v <= 168):
                    bad.append(f"`accounts.{n}.window_h_after_reset` must be null or hours in (0, 168]")
        if bad:
            out.append(f"{tag}: " + "; ".join(bad))
        else:
            good.append((e, f, u))
    clash = set()
    for a in range(len(good)):
        for b in range(a + 1, len(good)):
            (ea, fa, ua), (eb, fb, ub) = good[a], good[b]
            if fa < ub and fb < ua:
                out.append(f"exception {ea['id']} and {eb['id']}: spans overlap; both refused")
                clash |= {a, b}
    return out, [g for i, g in enumerate(good) if i not in clash]


def _first_reset_after(r, t0: float):
    """The account's first weekly reset after t0, from any one of its reset instants (rolled by whole weeks)."""
    rs = epoch((r or {}).get("week_resets_at"))
    if rs is None:
        return None
    while rs - WEEK > t0:
        rs -= WEEK
    while rs <= t0:
        rs += WEEK
    return rs


def active_exception(plan: dict, now: float, meter=None):
    """-> (exception, end epoch) standing at `now`, or None. Active from `from` to the earlier of `until` and the
    first reset of `ends_at_reset_of` after `from` (read from the meter; no reading: `until` alone)."""
    if not plan.get("exceptions"):
        return None
    for e, f, end in _guard(plan)[1]:
        n = e.get("ends_at_reset_of")
        rs = _first_reset_after((meter or {}).get(n), f) if n else None
        end = min(end, rs) if rs is not None else end
        if f <= now < end:
            return e, end
    return None


def at(plan: dict, now: float, meter=None) -> dict:
    """The plan in force at `now`: the standing plan, or a copy with the exception standing then applied (its order,
    its per-account rules; `_exception` names it). The plan read is never edited."""
    hit = active_exception(plan, now, meter)
    if hit is None:
        return plan
    e, end = hit
    accs = {n: dict(c or {}) for n, c in plan["accounts"].items()}
    for n, cfg in (e.get("accounts") or {}).items():
        for k, v in cfg.items():
            if not k.startswith("_"):
                accs[n][k], accs[n]["_" + k] = v, f"exception {e['id']} (until {iso(end)})"
    return {**plan, "order": list(e.get("order") or plan["order"]), "accounts": accs,
            "_exception": e["id"], "_exception_until": iso(end)}


def in_window(plan: dict, name: str, r, now: float, margin_s: float = 0) -> bool:
    """Inside the account's window (always, for an account without one). margin_s: with that much of it still left,
    so a switch that takes minutes never lands after the window closed."""
    w = (plan["accounts"].get(name) or {}).get("window_h_after_reset")
    if w is None:
        return True
    rs = next_reset(r, now)
    return rs is not None and not reset_passed(r, now) and (rs - now - margin_s) / 3600 >= 168 - w


def expiry(plan: dict, name: str, r, now: float):
    """When the account's present budget is lost to us: its next weekly reset, or for a windowed account (steven)
    the end of the window after its last reset. None when the meter has no reset time."""
    rs = next_reset(r, now)
    if rs is None:
        return None
    w = (plan["accounts"].get(name) or {}).get("window_h_after_reset")
    return rs if w is None else rs - WEEK + w * 3600


def lines(meter: dict, plan: dict, now: float, out=()) -> tuple[dict, dict]:
    """-> ({name: line}, {name: eligible}). An account's line is its leave_pct_left when it has one; else the
    switch-away floor while some OTHER account has budget above its wait floor to take over, else the wait floor
    (we idle on it until a reset). Eligible = MEASURED, fresh, in its window, above its line, and not in `out` (the
    accounts a transition marker keeps out: they can take over from nobody, so they never lower another's line)."""
    fl = plan["floors"]

    def ok(n, ln):
        r = meter.get(n)
        return (n not in out and usable(r) and not reset_passed(r, now)
                and in_window(plan, n, r, now, plan.get("window_margin_min", 0) * 60) and r["week_pct_left"] > ln)

    strict = {}
    for n in plan["order"]:
        leave = (plan["accounts"].get(n) or {}).get("leave_pct_left")
        strict[n] = ok(n, leave if leave is not None else fl["wait_pct_left"])
    line, elig = {}, {}
    for n in plan["order"]:
        leave = (plan["accounts"].get(n) or {}).get("leave_pct_left")
        other = any(strict[m] for m in plan["order"] if m != n)
        line[n] = leave if leave is not None else (fl["switch_away_pct_left"] if other else fl["wait_pct_left"])
        elig[n] = ok(n, line[n])
    return line, elig


def pick(meter: dict, plan: dict, now: float, elig: dict):
    """The owner's fixed priority (2026-10-28 10:15): the first eligible account in plan order."""
    return next((n for n in plan["order"] if elig.get(n)), None)


def outranks(plan: dict, a, b) -> bool:
    """a comes before b in the owner's priority (an account outside the plan ranks last)."""
    o = plan["order"]
    return a in o and (b not in o or o.index(a) < o.index(b))


def switch_key(frm: str, to: str, target_rec: dict) -> str:
    rs = epoch((target_rec or {}).get("week_resets_at"))
    wk = datetime.fromtimestamp(rs, timezone.utc).astimezone().strftime("%Y%m%d") if rs else "unknown"
    return f"use_{frm}_to_{to}_{wk}"


def stop_key(name: str, rec: dict, now: float) -> str:
    rs = next_reset(rec, now)
    return f"{name}_" + (datetime.fromtimestamp(rs, timezone.utc).astimezone().strftime("%Y%m%d") if rs else "unknown")


def is_spent(plan: dict, line: dict, live, lr: dict, now: float) -> bool:
    """live is at its line on a post-reset reading (an upper bound: usage only grows inside a week, so even an old or
    ESTIMATE figure proves the line is reached), or a windowed account (steven) past its window, timed from the last
    reset the recorded one implies, so it is enforced even when his reading predates that reset."""
    p = left(plan, lr, now)
    w, nr = (plan["accounts"].get(live) or {}).get("window_h_after_reset"), next_reset(lr, now)
    return ((p is not None and live in line and p <= line[live] and not reset_passed(lr, now))
            or (live in plan["order"] and w is not None and nr is not None and (WEEK - (nr - now)) / 3600 > w))


def switches(path=None) -> list | None:
    """Every switch that changed the live account, oldest first, from the switcher's own append-only log; [] when it
    has none, None when it cannot be read. A malformed line is skipped (a line being appended right now)."""
    try:
        text = Path(path or SWITCH_LOG).read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return []
    except OSError:
        return None
    out = []
    for ln in text.splitlines():
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if isinstance(r, dict) and r.get("op") == "use" and r.get("changed"):
            out.append(r)
    return out


def last_switch(path=None):
    """The newest switch that changed the live account: {from, to, ts}, or None when the log has none."""
    return (switches(path) or [None])[-1]


def manual_switch(sw, markers: dict, live, history=None):
    """The last switch when it put `live` there and the plan did not make it, else None. The plan writes its marker
    before it calls `use` and the call ends inside STALE_PENDING_S; one call makes at most ONE switch, the first of its
    transition in the switcher's log (`history`, default the log; by POSITION, a shared second proves no order) after
    the marker, landing no later than the call `ended` (both stamps are this machine's wall clock, to the second).
    Any other switch of that transition in the span is his (RIMMANDRAKE_ATTRIBUTE_MANUAL_SWITCH_BY_LOG_NOT_OLD_MARKER:
    his own lukas->system->lukas->system inside 40 min was read as the plan's and a later pull could undo it). A
    lapsed marker never called `use`. A switch with no readable time is the plan's to judge: nothing can say it is
    recent; an unreadable log falls back to the marker's window alone."""
    ts = epoch((sw or {}).get("ts"))
    if ts is None or sw.get("to") != live:
        return None
    if history is None:
        history = switches()
    for m in markers.values():
        at = epoch(m.get("at"))
        if not (m.get("from") == sw.get("from") and m.get("to") == sw.get("to") and m.get("phase") != "lapsed"
                and at is not None and 0 <= ts - at <= STALE_PENDING_S):
            continue
        ended = epoch(m.get("ended"))
        if ended is not None and ts > ended:
            continue  # landed after the plan's call returned: not the plan's
        if history:
            same = [r for r in history if r.get("from") == sw.get("from") and r.get("to") == sw.get("to")
                    and at <= (epoch(r.get("ts")) or -1) <= ts]
            if not same or same[-1] != sw:  # sw is the newest switch: the log's last of its transition, or after it
                same.append(sw)
            if len(same) > 1:
                continue  # the plan's switch is an earlier one in the log: this one is his
        return None
    return sw


def refilled(plan: dict, name, m: dict, then, meter: dict, now: float) -> bool:
    """The account refilled after the marker was written, its weekly reset unmoved (steven's spare reset of
    2026-11-21..24: left at 5%, then 97% MEASURED). Usage only grows inside a week, so a level well above the most it
    could read when left proves a refill. Read from a MEASURED, non-stale figure taken after the marker only, never an
    estimate. 'Well above': over its fast warning line for `then` (the most a switch away leaves it at,
    account_end.warning_line) plus the plan's soft margin, so a refilled account is never a target inside its soft zone
    (RIMMANDRAKE_CLEAR_STEVEN_MARKER_HIS_REFILL_READS_AS_SPENT)."""
    r, t = meter.get(name), epoch(m.get("at"))
    age = (r or {}).get("age_min")
    if not usable(r) or t is None or not isinstance(age, (int, float)) or now - age * 60 <= t or then is None:
        return False
    return r["week_pct_left"] > AE.warning_line(then, None, plan["account_end"]) + plan["soft_margin_pct"]


def marker_lifted(raw: dict, plan: dict, name, m: dict, meter: dict, now: float | None = None) -> bool:
    """A marker keeps an account out at the line it was left at. A dated exception standing now that gives it a LOWER
    line opened budget the marker never saw (owner, by card 2026-11-17: steven left at 52% on 11-12, then 'switch to
    Steve' down to 35%), so the marker stops keeping it out while that exception stands; it binds again after. The
    line left at is the marker's own `line`, else the leave line of the plan in force when it was written. Inside such
    an exception a MEASURED refill after the marker lifts it too (refilled; owner, by card 2026-11-24: 'Use Steve down
    to 5% left'); the standing plan's markers keep their meaning."""
    cfg = plan["accounts"].get(name) or {}
    if not plan.get("_exception") or not str(cfg.get("_leave_pct_left", "")).startswith("exception"):
        return False
    then = m.get("line")
    if not isinstance(then, (int, float)) or isinstance(then, bool):
        t = epoch(m.get("at"))
        then = None if t is None else (at(raw, t, meter)["accounts"].get(name) or {}).get("leave_pct_left")
    return then is not None and (cfg["leave_pct_left"] < then
                                 or (now is not None and refilled(plan, name, m, then, meter, now)))


# ------------------------------------------------------------------ the decision (pure)
def runs_why(live_runs) -> str:
    if live_runs is None:
        return "the live runs are UNMEASURED (systemd could not be read), so they count as live"
    return "%d live run(s): %s" % (len(live_runs), ", ".join(live_runs[:4]) + (" ..." if len(live_runs) > 4 else ""))


def drained(d: dict, plan: dict, live_runs) -> dict:
    """A switch or stop due on an account at its line waits while a detached run is live: -> the decision as a drain
    (`soft`, drain and account_end true: the save order at the line), or d, `emergency` true when it goes with a run
    live on an account at 1%. live_runs None (unreadable) counts as live. An account kept well above zero waits for its
    runs (no emergency), down to 1%."""
    if d.get("do") not in ("switch", "stop") or (d["do"] == "switch" and not d.get("under")):
        return d
    if live_runs is not None and not live_runs:
        return d
    p, ln, cfg = d.get("pct_left"), d.get("line"), plan["account_end"]
    if p is None or ln is None:
        return d
    if p <= cfg["emergency_pct"]:
        return {**d, "emergency": True} if AE.has_emergency(ln, cfg) else d
    w = d.get("warn_line")
    if w is None or p > w:      # past its window with budget left: the runs finish as they are, nobody is told to end
        return {**d, "do": "soft", "drain": True, "drain_of": d["do"],
                "why": f"{d['account']} at {p}% must be left: the {d['do']} waits while live runs finish "
                       f"({runs_why(live_runs)}); no new start; it goes when they end. Was: " + str(d.get("why"))}
    return {**d, "do": "soft", "drain": True, "account_end": True, "drain_of": d["do"],
            "why": f"{d['account']} at {p}% is at its {ln}% line: the {d['do']} waits while live runs "
                   f"save and end ({runs_why(live_runs)}); no new start; it goes when they end"
                   + (f" or at {cfg['emergency_pct']}%" if AE.has_emergency(ln, cfg) else "") + ". Was: "
                   + str(d.get("why"))}


def decide(meter: dict, live, now: float, plan: dict, state: dict, markers: dict, polled: bool = False,
           manual=None, live_runs=(), burn=None) -> dict:
    """-> {do: skip|poll|normal|soft|switch|hold|stop|stopped|start, to, account, line, pct_left, why, poll, drain}
    (the HOLD brake is the caller's: check() and status()). manual: manual_switch(), the switch to respect.
    live_runs: the live detached runs (None: unreadable); a switch or stop due at the line waits on them (drained).
    burn: account_end.read_burn of the live account; None reads as unknown (the safe warning line)."""
    return drained(_decide(meter, live, now, plan, state, markers, polled, manual, burn), at(plan, now, meter), live_runs)


def warn_at(plan: dict, line: dict, live, burn, state: dict):
    """The live account's warning line: account_end.warning_line, never under the one that already fired (latched in
    state["account_end"] until the account changes or resets). None for an account outside the plan."""
    if live not in line:
        return None
    w = AE.warning_line(line[live], burn, plan["account_end"])
    ep = state.get("account_end") or {}
    return max(w, ep["warn_line"]) if (ep.get("account") == live and ep.get("warn_line") is not None
                                       and not lowered(ep, line[live])) else w


def lowered(ep: dict, line) -> bool:
    """The account's line fell after its warning (a dated exception opened more of it): the warning no longer stands."""
    return line is not None and ep.get("line") is not None and line < ep["line"]


def _decide(meter: dict, live, now: float, plan: dict, state: dict, markers: dict, polled: bool = False,
            manual=None, burn=None) -> dict:
    if not live:
        return {"do": "skip", "why": "live account unknown (claude-account --json status failed)"}
    raw, plan = plan, at(plan, now, meter)  # the plan in force now: a dated exception, when one stands
    order, fr = plan["order"], plan["fresh"]
    kept_out = set()
    for m in markers.values():  # an account we left at its line is no target again before its reset: no flapping
        f = m.get("from")       # when its meter recovers and re-reads the same last 1%
        rs = next_reset(meter.get(f) or {}, now) if f in order and f != live else None
        # a pending marker whose target is live now is a switch that landed before its pass could record it
        landed = m.get("phase") == "done" or (m.get("phase") == "pending" and m.get("to") == live)
        if (landed and m.get("under") and rs is not None and (epoch(m.get("at")) or 0) > rs - WEEK
                and not marker_lifted(raw, plan, f, m, meter, now)):
            kept_out.add(f)
    line, elig = lines(meter, plan, now, kept_out)
    lr = meter.get(live) or {}
    pl = left(plan, lr, now)
    warn = warn_at(plan, line, live, burn, state)
    spent_at = line     # the account is used down to its own line; the warning line only warns (owner 2026-11-24)
    cfg = plan["account_end"]
    for n in elig:  # no switch lands on an account that would be warned at once
        if n != live and elig[n] and AE.has_emergency(line[n], cfg):
            elig[n] = meter[n]["week_pct_left"] > AE.target_line(line[n], cfg)
    if ((state.get("stopped") or {}).get("account") == live and live in elig and pl is not None
            and pl <= line[live] + plan["soft_margin_pct"]):
        elig[live] = False  # a fleet stopped in its soft zone never restarts there: another account with budget wins
    target = pick(meter, plan, now, elig)
    # a switch the plan did not make stands until the account is spent. Not on a fleet this engine stopped there: the
    # soft-zone rule just above decides that one. Never for an account outside the plan's rules (it has no line).
    held = bool(manual) and live in line and not is_spent(plan, spent_at, live, lr, now) and (
        (state.get("stopped") or {}).get("account") != live)
    if held:
        target = live
    respected = f"; {manual.get('from')} -> {live} at {manual.get('ts')} was not the plan's: respected" if held else ""
    blind = blind_zero(plan, lr, now)
    base = {"account": live, "line": line.get(live), "pct_left": left(plan, lr, now), "to": None, "warn_line": warn,
            "exception": plan.get("_exception")}
    if warn is not None and pl is not None and live in line and line[live] < pl <= warn:
        # inside the warning zone: the runs are warned and keep working, new work starts (RIMMANDRAKE_BURN_TO_LINE_...)
        base.update(warning=True, last_account=not any(v for n, v in elig.items() if n != live))
    if plan.get("_exception"):
        base["exception_until"] = plan["_exception_until"]
    refused = exception_problems(raw)
    if refused:
        base["exception_refused"] = refused

    # fresh readings before any act; reasons are kept per account so an unrelated account never blocks
    stale = {}

    def why(n, text):
        stale.setdefault(n, []).append(text)

    if not usable(lr) and not blind:
        why(live, f"{live} (live) reads {lr.get('source')}{' stale' if lr.get('stale') else ''}")
    for n in {live, target} - {None}:
        r = meter.get(n) or {}
        p, a = r.get("week_pct_left"), r.get("age_min")
        if n == live and blind:
            continue
        # at the end of an account the reading is kept fresher (account_end.poll_min)
        old = cfg["poll_min"] if n == live and warn is not None and p is not None and p <= warn + 1 else fr["max_age_min"]
        if p is not None and n in line and p - line[n] <= fr["near_pct"] and (a is None or a > old):
            why(n, f"{n} at {p}% is within {fr['near_pct']} of its {line[n]}% line on a {a}-min-old reading")
    if target is not None and target != live:
        a = (meter.get(target) or {}).get("age_min")
        if a is None or a > fr["max_age_min"]:
            why(target, f"{target} (the switch target) was read {a} min ago")
    for n in order:
        if reset_passed(meter.get(n), now):
            why(n, f"{n}'s reset has passed and the reading predates it")
        r = meter.get(n)
        if target is None and n != live and (not r or r.get("week_pct_left") is None):
            why(n, f"{n} has no reading: read it before any stop")
        elif (target is None and n != live and r and not usable(r) and not blind_zero(plan, r, now)
                and not reset_passed(r, now) and in_window(plan, n, r, now) and n in line
                and (r.get("week_pct_left") or 0) > line[n]):
            why(n, f"{n} may have headroom ({r.get('week_pct_left')}%) but reads {r.get('source')}"
                   f"{' stale' if r.get('stale') else ''}: read it before any stop")
    # a blind 0% live account never waits on a poll for anything but where it can go (the owner, 11:2x)
    if blind:
        why_poll = stale.get(target, []) if target else [t for k, v in stale.items() if k != live for t in v]
    else:
        why_poll = [t for v in stale.values() for t in v]
    if why_poll and not polled:
        return {**base, "do": "poll", "poll": True, "why": "; ".join(why_poll)}
    p = left(plan, lr, now)
    under = is_spent(plan, spent_at, live, lr, now)
    out = under and not (p is not None and live in line and p <= spent_at[live] and not reset_passed(lr, now))

    if target is None:
        st = state.get("stopped") or {}
        if st.get("account") == live:
            return {**base, "do": "stopped", "why": f"hard-stopped on {live}; waiting for a reset"}
        if not under:
            return {**base, "do": "soft", "why": f"no account has headroom but {live}'s reading cannot prove its line "
                                                 f"({lr.get('source')}, {p}%): no new helpers, no stop yet"}
        return {**base, "do": "stop", "key": stop_key(live, lr, now),
                "why": f"no account has headroom (outside windows or at lines); {live} at {p}% is spent"
                       + (" (past its window)" if out else "")
                       + (" (blind meter = 0%)" if blind else "")}

    if target != live and target in stale and under:
        # spent, and the highest-priority account is unconfirmed: a confirmed account beats a stop
        def fresh(n):
            a = (meter.get(n) or {}).get("age_min")
            return a is not None and a <= fr["max_age_min"]
        conf = {n: elig[n] and n != live and n not in stale and fresh(n) for n in elig}
        target = pick(meter, plan, now, conf) or target
    if target != live:
        key = switch_key(live, target, meter.get(target))
        m = markers.get(key)
        if m and m.get("phase") == "lapsed":  # skipped after a slow arm: as if never tried
            m = None
        if m and m.get("phase") == "failed" and under and (state.get("stopped") or {}).get("account") != live:
            return {**base, "do": "stop", "key": stop_key(live, lr, now),
                    "why": f"switch {key} failed and {live} at {p}% is spent: hard stop, the switch is retried "
                           "from the stopped fleet"}
        # RIMMANDRAKE_SKIP_RESTOP_OF_STOPPED_FLEET_PUSH_EACH_PASS: a stop already recorded on live is never stopped
        # again (record_stop would re-stamp it and send a new red phone push every pass)
        stopped_here = (state.get("stopped") or {}).get("account") == live
        if m and m.get("phase") != "failed":
            age = now - (epoch(m.get("at")) or 0)
            if m.get("phase") == "pending" and age < STALE_PENDING_S and under and stopped_here:
                return {**base, "do": "stopped", "why": f"hard-stopped on {live}; transition {key} is still pending"}
            if m.get("phase") == "pending" and age < STALE_PENDING_S and under:
                return {**base, "do": "stop", "key": stop_key(live, lr, now),
                        "why": f"transition {key} is pending yet live is still {live} at {p}% <= its "
                               f"{spent_at[live]}% line: stop rather than overshoot"}
            if (m.get("phase") == "done" or age < STALE_PENDING_S) and not under:
                return {**base, "do": "hold", "to": target, "key": key,
                        "why": f"transition {key} already {m.get('phase')}: never repeated; live is still {live} "
                               "(a done switch that reads back as the old account is a human's move: respected)"}
        if target in stale:
            if under and stopped_here:
                return {**base, "do": "stopped", "why": f"hard-stopped on {live}; {target} cannot be confirmed: "
                                                        + "; ".join(stale[target])}
            if under:
                return {**base, "do": "stop", "key": stop_key(live, lr, now),
                        "why": f"{live} at {p}% <= its line and {target} cannot be confirmed: "
                               + "; ".join(stale[target])}
            return {**base, "do": "soft", "to": target, "why": "switch pending, target not confirmed after a poll: "
                                                               + "; ".join(stale[target])}
        before = outranks(plan, target, live)  # the switch is the target's pull (a reset), not live's reading
        near = p is not None and live in line and p - line[live] <= fr["near_pct"]
        if not (usable(lr) or under or live not in order or before or (polled and near)):
            return {**base, "do": "hold", "to": target, "why": f"{live} reads {lr.get('source')}: no switch away "
                                                                "from an account the meter cannot see"}
        tr = meter[target]
        return {**base, "do": "switch", "to": target, "key": key, "under": under,
                "why": f"{target} is the highest-priority account with headroom ({tr['week_pct_left']}% > "
                       f"{line[target]}%); {live} at {p}%" + (" (blind meter = 0%)" if blind else "")}

    # target == live
    if (state.get("stopped") or {}).get("account") == live:
        if live in stale or p <= line[live] + plan["soft_margin_pct"]:
            return {**base, "do": "stopped", "why": f"hard-stopped on {live}: no fleet-start on an unconfirmed reading "
                                                    "or into the soft zone"}
        return {**base, "do": "start", "why": f"{live} has headroom again after the hard stop"}
    if live in stale:
        return {**base, "do": "soft", "unread": True,
                "why": "reading not fresh near a line after a poll: " + "; ".join(stale[live])}
    if p <= line[live] + plan["soft_margin_pct"]:
        return {**base, "do": "soft", "why": f"{live} at {p}% is within {plan['soft_margin_pct']} of its "
                                             f"{line[live]}% line: switch pending, publish and finish{respected}"}
    if held:  # no reset pulls the machine off it, so no "publish and finish" for a switch that will not come
        return {**base, "do": "normal", "why": f"{live} at {p}% above its {line[live]}% line{respected}"}
    lead_h = plan["switch_lead_min"] / 60
    for n in order:
        r = meter.get(n) or {}
        h = r.get("hours_to_week_reset")
        if n == live or h is None or not 0 < h <= lead_h:
            continue
        fresh = {**r, "source": "MEASURED", "stale": False, "week_pct_left": 100.0, "age_min": 0,
                 "hours_to_week_reset": 168.0, "week_resets_at": iso((next_reset(r, now) or now) + WEEK)}
        after = {**meter, n: fresh}
        then = at(raw, now + h * 3600, after)
        _l, el = lines(after, then, now + h * 3600)
        if pick(after, then, now + h * 3600, el) not in (live, None):
            return {**base, "do": "soft", "why": f"{n}'s reset in {round(h * 60)} min will pull the machine to it: "
                                                 "switch pending, publish and finish"}
    return {**base, "do": "normal", "why": f"{live} at {p}% above its {line[live]}% line"}


# ------------------------------------------------------------------ the pool (pure; slot_allocator paces on it)
def pool(meter: dict, now: float, plan: dict, live=None) -> dict:
    """What the plan will still spend and the burn rate that spends it without losing more than the owner's priority
    gives up: each account's present budget (down to its line) is due at its expiry (next reset; steven's window
    end), unless higher-priority eligible accounts that outlive it hold more than the pace without it burns before
    it expires (then it is lost by his rule and not paced for; when it is kept, those higher budgets are due by its
    expiry, since pick() burns them first), and
    its next refill (100 - line) at the refill's own expiry. The rate is the max over deadlines of cumulative spend /
    hours; pct and deadline_h are the binding deadline's. -> {pct, rate_pct_h, deadline_h, total_pct, parts}; rate
    None when no account has a reset time. `live` is unused (kept for the allocator's call).
    Present budgets follow the plan in force now (a dated exception, when one stands); each refill follows the plan
    in force just after the reset that brings it."""
    raw, plan = plan, at(plan, now, meter)
    plain = [n for n in plan["order"] if (plan["accounts"].get(n) or {}).get("window_h_after_reset") is None]
    exp = {n: expiry(plan, n, meter.get(n), now) for n in plan["order"]}
    _ln, elig = lines(meter, plan, now)
    last = max((n for n in plain if exp[n] is not None), key=lambda n: exp[n], default=None)
    horizon = max((exp[n] for n in plain if exp[n] is not None), default=None)
    horizon = None if horizon is None else horizon + WEEK  # every account's refills up to one week past the last expiry
    def budget(pl, n, r, p, t):
        """(spend down to the line, expiry) of n at t under the plan pl, (0, expiry) outside its window."""
        cfg = pl["accounts"].get(n) or {}
        leave = cfg.get("leave_pct_left")
        ln = leave if leave is not None else (pl["floors"]["wait_pct_left"] if n == last
                                              else pl["floors"]["switch_away_pct_left"])
        e = expiry(pl, n, r, t)
        inside = cfg.get("window_h_after_reset") is None or in_window(pl, n, r, t)
        return (max(0.0, p - ln) if inside and e is not None and e > t else 0.0), e

    def pieces(n, r, p, t):
        """-> ([(spend, due)], expiry): n's budget at t under the plan in force then. The part only a dated exception
        opens (a lower line, a lifted window) is due when that exception ends, unless the expiry comes first."""
        sp, e = budget(at(raw, t, meter), n, r, p, t)
        hit = active_exception(raw, t, meter)
        if hit is None or e is None or e <= hit[1]:
            return [(sp, e)], e
        end = hit[1]
        sa, ea = budget(at(raw, end, meter), n, r, p, end)  # what still stands once the exception has ended
        keep = min(sp, sa)
        return [x for x in ((keep, min(e, ea) if ea is not None else e), (sp - keep, end)) if x[0] > 0] or [(0.0, e)], e

    present, refills, split = {}, [], {}
    for n in plan["order"]:
        r = meter.get(n) or {}
        cfg = plan["accounts"].get(n) or {}
        e = exp[n]
        if e is None:
            continue
        p = left(plan, r, now)
        if p is None and reset_passed(r, now):
            p = 100.0
        if e > now and (cfg.get("window_h_after_reset") is None or in_window(plan, n, r, now)):
            split[n], _e = pieces(n, r, p if p is not None else 0.0, now)
            present[n] = (sum(sp for sp, _d in split[n]), e)
        rs = next_reset(r, now)
        k = 0
        while True:  # each refill follows the plan in force once ITS reset has landed (review finding 3)
            rk = rs + k * WEEK
            parts_k, ef = pieces(n, {**r, "week_resets_at": iso(rk + WEEK)}, 100.0, rk + 1)
            if k and (horizon is None or ef > horizon):
                break
            refills += [(n, sp, d) for sp, d in parts_k]
            k += 1

    def pace(parts):
        parts = sorted(parts, key=lambda t: t[2])
        cum, rate, bind, dl = 0.0, 0.0, 0.0, None
        for _n, sp, d in parts:
            cum += sp
            h = (d - now) / 3600
            if h > 0 and (dl is None or cum / h > rate):
                rate, bind, dl = cum / h, cum, h
        return parts, cum, rate, bind, dl

    def placed(keep):
        """Kept present budgets at their deadlines. A higher eligible account that outlives a kept lower one is
        burned FIRST by pick(), so its budget is due by the lower one's expiry: else the pace would list the lower
        budget as spendable while it waits behind the higher one and expires ([R] GPT 2026-10-28 final round)."""
        due = {n: present[n][1] for n in keep}
        for n in keep:
            for m in keep:
                if m != n and elig.get(m) and outranks(plan, m, n) and present[m][1] > present[n][1]:
                    due[m] = min(due[m], present[n][1])
        return [(n, sp, min(d, due[n])) for n in keep for sp, d in split[n]] + refills

    def blockers(n):
        return [m for m in present if m != n and elig.get(m) and outranks(plan, m, n) and present[m][1] > present[n][1]]

    # the owner's priority: a present budget is lost at its expiry (and not paced for) when the higher eligible
    # accounts that outlive it hold more than the pool's pace WITHOUT it burns before it expires (judged without
    # it: pacing for it pulls those higher budgets forward, which would justify any rescue); the pace depends on
    # what is kept, so settle it by a few rounds (start with everything kept)
    keep = set(present)
    for _ in range(4):
        new = {n for n, (_sp, e) in present.items()
               if not blockers(n) or sum(present[m][0] for m in blockers(n))
               < pace(placed(keep - {n}))[2] * (e - now) / 3600}
        if new == keep:
            break
        keep = new
    parts = placed(keep)
    if not parts:
        return {"pct": None, "rate_pct_h": None, "deadline_h": None, "total_pct": None, "parts": [],
                "why": "no account has a reset time"}
    parts, cum, rate, bind, dl = pace(parts)
    return {"pct": round(bind, 2), "rate_pct_h": round(rate, 4), "deadline_h": round(dl, 2) if dl else None,
            "total_pct": round(cum, 2),
            "parts": [{"account": n, "spend_pct": round(sp, 2), "by_h": round((d - now) / 3600, 2)} for n, sp, d in parts]}


# ------------------------------------------------------------------ the week ahead (pure; status prints it)
def simulate(meter: dict, now: float, plan: dict, live, rate_pct_h: float, hours: float = 168,
             step_min: float = 1) -> list:
    """The engine's own lines() + pick() run forward from the meter: every account refills to 100% at its reset
    (the meter's reset time, rolled by whole weeks: resets are fixed instants, so a DST change never moves them) and
    the target burns at rate_pct_h down to its line. Ignores polls, soft notices and stops (timing only). -> events
    [{kind: target|reset, at, target|account, pct: {name: %}}]; the first is the target at `now`."""
    pct, rs = {}, {}
    for n in plan["order"]:
        r = meter.get(n) or {}
        rs[n] = next_reset(r, now)
        pct[n] = 100.0 if reset_passed(r, now) else left(plan, r, now)
    ev, cur, t, end = [], object(), now, now + hours * 3600

    def snap():
        return {n: None if v is None else round(v, 1) for n, v in pct.items()}
    while t <= end:
        for n in plan["order"]:
            if rs[n] is not None and rs[n] <= t:
                pct[n], rs[n] = 100.0, rs[n] + WEEK
                ev.append({"kind": "reset", "at": t, "account": n, "pct": snap()})
        sm = {n: ({"source": "MEASURED", "stale": False, "week_pct_left": pct[n], "age_min": 0,
                   "week_resets_at": iso(rs[n]) if rs[n] else None,
                   "hours_to_week_reset": (rs[n] - t) / 3600 if rs[n] else None}
                  if pct[n] is not None else {"source": "UNMEASURED", "week_pct_left": None})
              for n in plan["order"]}
        ep = at(plan, t, meter)  # the plan in force at t: a dated exception ends inside the week ahead
        ln, el = lines(sm, ep, t)
        tgt = pick(sm, ep, t, el)
        key = (tgt, ep.get("_exception"))
        if key != cur:
            a = (ep["accounts"].get(tgt) or {}) if tgt else {}
            ev.append({"kind": "target", "at": t, "target": tgt, "pct": snap(), "to": a.get("leave_pct_left"),
                       "window": a.get("window_h_after_reset") is not None, "exception": ep.get("_exception"),
                       "exception_until": ep.get("_exception_until")})
            cur = key
        dt = step_min * 60
        if tgt is not None:
            pct[tgt] = max(ln[tgt], pct[tgt] - rate_pct_h * dt / 3600)
        t += dt
    return ev


def week_lines(ev: list, plan: dict) -> list:
    out = []
    for e in ev:
        when = datetime.fromtimestamp(e["at"], timezone.utc).astimezone().strftime("%a %Y-%m-%d %H:%M %Z")
        pc = ", ".join(f"{n} {'?' if v is None else v}%" for n, v in e["pct"].items())
        if e["kind"] == "reset":
            out.append(f"{when}  reset   {e['account']} refills to 100%  [{pc}]")
        else:
            by = ""
            if e.get("exception"):
                u = datetime.fromtimestamp(epoch(e["exception_until"]), timezone.utc).astimezone()
                by = f"  (exception {e['exception']} until {u.strftime('%a %H:%M %Z')})"
            if e["target"] is None:
                out.append(f"{when}  IDLE    no account above its line: hard stop until a reset{by}  [{pc}]")
                continue
            if "to" in e:
                to, win = e["to"], e.get("window")
            else:  # an event from before exceptions: the standing rules
                a = plan["accounts"].get(e["target"]) or {}
                to, win = a.get("leave_pct_left"), a.get("window_h_after_reset") is not None
            out.append(f"{when}  target  {e['target']}"
                       + (f" (to {to}% left{', inside its window' if win else ''})" if to is not None else "")
                       + f"{by}  [{pc}]")
    return out


# ------------------------------------------------------------------ the world (impure)
def run(argv, full=False, timeout=600):
    """-> (rc, out). full=True returns stdout whole: a parser must never see a truncated tail (the ~2030-char status
    once lost its opening brace to a 2000-char tail)."""
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, f"{argv[1:2]} timed out after {timeout} s"
    except OSError as e:
        return 127, f"{argv[:1]} could not run: {e}"
    return r.returncode, r.stdout if full else (r.stdout + r.stderr)


def switcher_status() -> dict:
    """The switcher's whole status when it names the live account, else {} (account_live, the one reader)."""
    sys.path.insert(0, str(HERE))
    import account_live as AL
    return AL.status_of(AL.read(exe_path=CA))


def meter_now() -> dict:
    sys.path.insert(0, str(HERE))
    import account_usage
    return account_usage.read_now().get("accounts") or {}


def levelled(meter: dict, model=None) -> dict:
    """Pure. The meter as a run of `model` sees it: each account's week figures are the LOWER of its all-models
    weekly limit and that model's own (account_usage.week_left_for), `week_limit` naming which; `model_weeks_left`
    carries every per-model limit as LEFT. model None (the plan's `level_model` unset) changes no figure: the machine
    runs every model, so only the all-models limit is the whole account's level
    (RIMMANDRAKE_READ_FABLE_WEEKLY_METER_USAGE_LINE_NEVER_SHOWED)."""
    sys.path.insert(0, str(HERE))
    import account_usage
    out = {}
    for n, r in (meter or {}).items():
        r = dict(r or {})
        r["model_weeks_left"] = {k: (w or {}).get("pct_left") for k, w in (r.get("model_weeks") or {}).items()}
        lv, lim, h = account_usage.week_left_for(r, model)
        r["week_limit"] = lim
        if lim != "all models":
            r.update(week_pct_left=lv, week_pct_used=round(100 - lv, 1), hours_to_week_reset=h,
                     week_resets_at=r["model_weeks"][lim].get("resets_at"))
        out[n] = r
    return out


def meter_poll() -> None:
    rc, out = run([sys.executable, str(HERE / "account_usage.py"), "poll"], timeout=420)
    log({"do": "meter_poll", "rc": rc, "out": out})


def next_refill(meter: dict, plan: dict, now: float) -> dict:
    """First metered reset that can give an account headroom under this engine's rules."""
    candidates = sorted(((rs, n) for n in plan["order"]
                         if (rs := next_reset(meter.get(n), now)) is not None),
                        key=lambda pair: (pair[0], plan["order"].index(pair[1])))
    for rs, name in candidates:
        rec = {"source": "MEASURED", "stale": False, "age_min": 0,
               "week_pct_left": 100, "week_resets_at": iso(rs + WEEK)}
        _, eligible = lines({name: rec}, at(plan, rs, meter), rs)
        if eligible.get(name):
            return {"reset_at": iso(rs), "reset_account": name}
    return {}


def notify_stop(state: dict) -> None:
    """Existing phone route, once per successful stop; failed deliveries retry on the next pass."""
    stopped = state.get("stopped") or {}
    if not stopped or stopped.get("phone_notified"):
        return
    from ops_core import phone_push
    until = stopped.get("reset_at")
    resume = (f"The next account refills at {until}; the fleet will restart after the switcher confirms headroom "
              "(checked every five minutes)." if until else
              "The next account's reset time is unmeasured; the fleet will restart once headroom is confirmed.")
    try:
        phone_push.send({"key": "account-plan-hard-stop:" + stopped["at"], "kind": "red",
                         "title": "Claude stopped: all accounts are out",
                         "detail": "Claude usage is out on every account. The Claude windows were stopped. " + resume})
    except Exception as e:
        log({"do": "phone_notice_failed", "error": str(e)})
        return
    stopped["phone_notified"] = True
    save_state(state)


def record_stop(state: dict, d: dict, now: float) -> None:
    state["stopped"] = {"account": d.get("account"), "key": d.get("key"), "at": iso(now),
                        **{k: d[k] for k in ("reset_at", "reset_account") if k in d}}
    save_state(state)  # crash recovery never repeats fleet-stop just to deliver the notice
    write_notice({**d, "do": "stop", "stopped_at": iso(now)}, now)
    notify_stop(state)


def write_notice(d: dict, now: float) -> None:
    write_atomic(OUT / "notice.json", notice_of(d, now, read_json(OUT / "notice.json", {}) or {}))


def notice_of(d: dict, now: float, prev: dict) -> dict:
    """The notice of the decision d (pure). prev: the notice before it, whose `since` goes on while the state does."""
    state = {"soft": "soft", "stop": "stop", "stopped": "stop"}.get(d["do"], "none")
    since = (d.get("stopped_at") if state == "stop" else None) or (
        prev.get("since") if prev.get("state") == state and prev.get("since")
        and bool(prev.get("drain")) == bool(d.get("drain")) else iso(now))     # a drain's own start bounds a pull
    warned = bool(d.get("warning")) and state in ("soft", "none") and not d.get("drain")
    # a soft decision only because the live level is not read (account_plan.decide `unread`): no switch is pending
    unread = state == "soft" and bool(d.get("unread")) and not d.get("account_end")
    msg = {"soft": ("the account is at its line: save your work now and publish; no new start" if d.get("account_end")
                    else "the level of %s is not read yet: no new run starts until it is read; live runs go on" % (
                        d.get("account") or "the live account") if unread
                    else "draining: no new start; live runs finish on this account, then it switches" if d.get("drain")
                    else "the account nears its line: save a note, publish what is done, keep working; new work "
                         "still starts" if warned else "switch pending: publish and finish; no new helpers"),
           "stop": "hard stop: the fleet is stopped until a reset",
           "none": "the account nears its line: save a note, publish what is done, keep working; new work still starts"
                   if warned else ""}[state]
    return {"state": state, "since": since, "at": iso(now), "account": d.get("account"),
            "line": d.get("line"), "pct_left": d.get("pct_left"), "message": msg,
            "why": d.get("why"), "drain": bool(d.get("drain")) and state == "soft",
            "account_end": bool(d.get("account_end")) and state == "soft",
            # what the checkpoint hook reads (switch_checkpoint_signal.py): a soft notice of an unread level is none
            "switch_pending": state == "soft" and not unread,
            # the warning's text, which a run that starts now gets in its start package
            "warning": d.get("warning_text") if warned else None,
            **({k: d.get(k) or prev.get(k) for k in ("reset_at", "reset_account")} if state == "stop" else {})}


def armed_call(st: dict, argv: list, still=None) -> dict:
    """arm if the machine is disarmed, run the switcher verb, disarm again if it was disarmed before. `still()` is
    asked after a slow arm whether the decision still holds; when it does not, the verb is skipped as 'lapsed'. A
    `still()` that returns a verb list instead names a brake now due in its place: it runs while the machine is armed."""
    machine = st.get("machine") or ""
    was_armed = bool(st.get("armed"))
    out = {}
    if not was_armed:
        out["arm"] = run([CA, "arm", "--confirm", machine])
    ok = still() if (was_armed or out["arm"][0] == 0) and still is not None else True
    if isinstance(ok, list):
        out[argv[0]] = (None, f"lapsed: the decision no longer holds after arming; {ok[0]} is due instead")
        out[ok[0]] = run([CA, *ok])
    elif not ok:
        out[argv[0]] = (None, "lapsed: the decision no longer holds after arming")
    elif was_armed or out["arm"][0] == 0:
        out[argv[0]] = run([CA, *argv, *(["--confirm", machine] if argv[0] == "use" else [])])
    else:
        out[argv[0]] = (None, "not armed")
    if not was_armed:
        out["disarm"] = run([CA, "disarm"])
    return out


def live_detached_runs(runner=subprocess.run):
    """-> the live detached run units (rm-detached-* services, active or activating, less their -return and -continue
    steps), or None when systemd cannot be read."""
    try:
        r = runner(["systemctl", "--user", "list-units", "--type=service", "--state=active,activating", "--plain",
                    "--no-legend", "rm-detached-*"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    units = [ln.split()[0] for ln in (r.stdout or "").splitlines() if ln.split()]
    return [u[:-len(".service")] for u in units if u.endswith(".service")
            and not u[:-len(".service")].endswith(("-return", "-continue"))]


def default_runs():
    """The live plan dir reads the live runs; a test's plan dir never does (it reads none unless it hands runs_fn)."""
    return live_detached_runs() if OUT == LIVE_OUT else []


def default_burn(live, now, cfg):
    """The live plan dir reads the live series; a test's plan dir reads none (unknown: the safe values)."""
    return (AE.read_burn(live, now, cfg, since=live_since(live)) if OUT == LIVE_OUT
            else AE.stale_burn("a test's plan reads no series"))


def live_since(live):
    """When `live` last went live, by the switcher's log; None when the log's last switch is to another account."""
    sw = last_switch()
    return epoch(sw.get("ts")) if sw and sw.get("to") == live else None


def burn_now(live, meter, now, cfg, burn_fn):
    """The burn this pass acts on. A level that cannot be read, or is older than stale_min, makes it stale too: the
    warning line, the pause and each text then use the safe values, whatever the series says."""
    r = meter.get(live) or {}
    if not usable(r) or (r.get("age_min") is not None and r["age_min"] > cfg["stale_min"]):
        return AE.stale_burn("the level reads %s, %s min old" % (
            str(r.get("source")) + (" stale" if r.get("stale") else ""), num_age(r)))
    try:
        return burn_fn(live, now, cfg)
    except Exception as e:  # noqa: BLE001  could not read is the safe value, never a slow burn
        return AE.stale_burn("%s: %s" % (type(e).__name__, e))


def num_age(r):
    return "?" if r.get("age_min") is None else "%g" % round(r["age_min"])


def check(dry: bool = False, now=None, meter_fn=meter_now, poll_fn=meter_poll, runs_fn=None, burn_fn=None, orders=None,
          passes: int = 1) -> int:
    """One pass under an exclusive non-blocking lock: a pass that finds another running stands down (the markers are
    not a lock, and two passes could both switch). `passes` > 1: while an account ends the pass repeats each REPEAT_S."""
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "check.lock", "a") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            log({"do": "skip", "why": "another pass holds check.lock", "acted": False})
            return 0
        rc = _check(dry, now, meter_fn, poll_fn, runs_fn or default_runs, burn_fn or default_burn, orders)
        for _ in range(passes - 1):
            if dry or not load_state().get("account_end") or load_state().get("stopped") or (OUT / "HOLD").exists():
                break
            sleep(REPEAT_S)
            rc = _check(dry, None, meter_fn, poll_fn, runs_fn or default_runs, burn_fn or default_burn, orders)
        if not dry and OUT == LIVE_OUT:
            flush_events()
    if not dry and OUT == LIVE_OUT and not (OUT / "HOLD").exists():
        resume_stopped_runs()
    return rc


def resume_stopped_runs():
    """After a live pass: start the sweep that resumes the detached runs a fleet stop killed (rimflow/stop_resume.py,
    RIMMANDRAKE_CHECKPOINT_HARD_STOP_NOT_KILL). Only for the live plan dir, so a test's pass never reads the live runs;
    never under HOLD (it acts on nothing); never fails the pass. Writes no plan line: headroom reads the plan log."""
    try:
        sys.path.insert(0, str(HERE.parent / "rimflow"))
        import stop_resume
        print(stop_resume.kick(plan_dir=str(OUT), acct_log=str(SWITCH_LOG)))
    except Exception as e:  # noqa: BLE001
        print(f"stop_resume did not run: {type(e).__name__}: {e}", file=sys.stderr)
    try:    # the runs that saved and ended because the account ended
        import left_open_continue
        print(left_open_continue.kick_waiting(plan_dir=str(OUT)))
    except Exception as e:  # noqa: BLE001
        print(f"left_open_continue did not run: {type(e).__name__}: {e}", file=sys.stderr)


ACTS = ("soft", "stop", "stopped", "switch")
REPEAT_S = 60   # page LIMITS, poll_min: 4 repeats fit inside one 5-min beat


# ------------------------------------------------------------------ the end of an account: its steps
def default_orders():
    """The live plan dir orders the live runs; a test's plan dir never does (it hands its own)."""
    return AE.Orders() if OUT == LIVE_OUT else None


def record_step(state: dict, step: str, text: str, now: float) -> None:
    """One Conductor log line now, and one ledger event owed (flush_events writes it after the pass's acts, so a slow
    publish never delays an order or a switch). Never raises: a record never stops a step."""
    state.setdefault("account_end_events", []).append(f"ACCOUNT END {step} at {iso(now)}: {text}")
    save_state(state)
    log({"do": "account_end", "step": step, "text": text, "acted": False})
    if OUT == LIVE_OUT:
        try:
            AE.conductor_line(f"{step}: {text}", now)
        except Exception as e:  # noqa: BLE001
            print(f"account_end: conductor log not written: {e}", file=sys.stderr)


def flush_events() -> None:
    state = load_state()
    texts = state.get("account_end_events") or []
    if not texts:
        return
    try:
        left_over = AE.ledger_events(texts)
    except Exception as e:  # noqa: BLE001  tried again at the next pass
        print(f"account_end: ledger events not written: {type(e).__name__}: {e}", file=sys.stderr)
        return
    state = load_state()
    state["account_end_events"] = left_over
    if not left_over:
        state.pop("account_end_events")
    save_state(state)


def end_episode(state: dict, d: dict, orders, why: str) -> None:
    """The account did not end after all (a reset, another account live): its undelivered orders are withdrawn."""
    ep = state.pop("account_end", None) or {}
    save_state(state)
    if ep.get("acts") and orders is not None:
        n, err = orders.withdraw(ep["acts"], why)
        log({"do": "account_end", "step": "over", "text": f"{why}; {err or '%s order(s) withdrawn' % n}", "acted": False})


def send_orders(state: dict, d: dict, step: str, mode: str, text: str, runs, orders, now, deadline=None):
    """The order of one step to every live run that has not had it. -> (units ordered now, why not or None)."""
    ep = state["account_end"]
    seen = ep.setdefault("ordered", {})
    store, blind = [], []
    if orders is not None:
        try:
            store = orders.store_runs()
        except Exception as e:  # noqa: BLE001  said in the step's record; the runs systemd lists are ordered all the same
            blind = ["the control store could not be read (%s)" % e]
    units = sorted(set(runs or []) | set(store))
    todo = [u for u in units if step not in (seen.get(u) or {})]
    blind += [] if runs is not None else ["systemd could not be read"]
    if not todo or orders is None:
        return [], "; ".join(blind) or None
    act, err = orders.send(todo, mode, text, deadline)
    if err:
        return [], "; ".join(blind + ["the orders could NOT be written: " + err])
    ep.setdefault("acts", []).append(act)
    for u in todo:
        seen.setdefault(u, {})[step] = now
    save_state(state)
    return todo, "; ".join(blind) or None


def facts(d: dict, plan: dict, burn, runs) -> str:
    b = burn or {}
    rate = "burn STALE (%s)" % (b.get("why") or "unread") if b.get("stale", True) or b.get("rate") is None else \
        "burn %.3f%% a minute" % b["rate"]
    m = AE.minutes_left(d["pct_left"], burn, plan["account_end"]) if d.get("pct_left") is not None else None
    em = AE.has_emergency(d.get("line"), plan["account_end"])
    return (f"{d['account']} at {d.get('pct_left')}% (line {d.get('line')}%, warning line {d.get('warn_line')}%), {rate}, "
            + (("about %s min to the emergency step" % ("?" if m is None else int(m))) if em else "no emergency step on "
               "this account") + f"; {runs_why(runs)}")


def open_episode(state: dict, d: dict, now: float) -> bool:
    """The end of the live account is recorded (its warning line latched). -> True when it opens now."""
    if (state.get("account_end") or {}).get("account") == d["account"]:
        return False
    state["account_end"] = {"account": d["account"], "warn_line": d.get("warn_line"), "line": d.get("line"),
                            "warned_at": iso(now)}
    save_state(state)
    return True


def warn_step(state: dict, d: dict, plan: dict, burn, runs, orders, now: float) -> None:
    """Step 1, at the warning line: every live run is warned (save a note, publish what is done, keep working); it ends
    no run and refuses no start. Recorded once; a run that appears later gets the warning too."""
    first = open_episode(state, d, now)
    sent, err = send_orders(state, d, "warn", "warn", d["warning_text"], runs, orders, now)
    if first:
        record_step(state, "warning", facts(d, plan, burn, runs) + f"; warned: {', '.join(sent) or 'none'}"
                    + (f"; {err}" if err else ""), now)
    elif err:
        log({"do": "account_end", "step": "warn", "text": err, "acted": False})


def save_step(state: dict, d: dict, plan: dict, burn, runs, orders, now: float) -> None:
    """Step 2, at the line of an account whose switch waits for its runs: every live run is told to save and end.
    Recorded once; a run that appears later gets its order too."""
    open_episode(state, d, now)
    ep = state["account_end"]
    first = not ep.get("save_at")
    if first:
        ep["save_at"] = iso(now)
        save_state(state)
    last = d.get("drain_of") != "switch"
    text = AE.save_text(d["account"], d.get("pct_left"), burn, d.get("line"), plan["account_end"], last)
    sent, err = send_orders(state, d, "save", "at_easy_spot", text, runs, orders, now)
    if first:
        record_step(state, "save order at the line", facts(d, plan, burn, runs) + f"; ordered: {', '.join(sent) or 'none'}"
                    + (f"; {err}" if err else ""), now)
    elif err:
        log({"do": "account_end", "step": "save", "text": err, "acted": False})


def emergency_step(state: dict, d: dict, plan: dict, burn, runs, runs_fn, orders, now: float) -> bool:
    """Step 3: the emergency order, then the pause. -> True to go on with the switch, False on a HOLD. A pass that died
    in the pause finds its start in the state and waits only what is left."""
    open_episode(state, d, now)
    ep = state["account_end"]
    em, first = ep.get("emergency"), False
    if not em:
        first = True
        secs = AE.pause_s(burn, plan["account_end"])
        em = ep["emergency"] = {"at": now, "pause_s": secs}
        save_state(state)
    last = d["do"] == "stop"
    text = AE.emergency_text(d["account"], d.get("pct_left"), burn, em["pause_s"], last)
    t0 = clock()
    sent, err = send_orders(state, d, "emergency", "write_now", text, runs, orders, now, em["at"] + em["pause_s"])
    if first:
        record_step(state, "emergency", facts(d, plan, burn, runs) + f"; pause {em['pause_s']} s; ordered: "
                    f"{', '.join(sent) or 'none'}" + (f"; {err}" if err else ""), now)
    while True:
        left_s = em["at"] + em["pause_s"] - (now + clock() - t0)
        if left_s <= 0:
            break
        try:
            still_live = runs_fn()
        except Exception:  # noqa: BLE001  unreadable counts as live
            still_live = None
        if still_live is not None and not still_live:
            break       # the last run ended: nothing is left to wait for
        sleep(min(5, left_s))
        if (OUT / "HOLD").exists():
            break
    return not (OUT / "HOLD").exists()


def saved_lines(state: dict, orders) -> str:
    """What each ordered run had saved, read before the switch stops it."""
    ep = state.get("account_end") or {}
    got = ep.get("ordered") or {}
    if not got or orders is None:
        return "no run was ordered"
    return "; ".join("%s: %s" % (u, orders.saved(u, min(v.values()))) for u, v in sorted(got.items()))


def _check(dry, now, meter_fn, poll_fn, runs_fn=default_runs, burn_fn=default_burn, orders=None) -> int:
    global DRY
    DRY = dry
    t0 = clock()
    now = now or t0
    plan, state = load_plan(), load_state()
    if (OUT / "HOLD").exists():
        log({"do": "passive", "why": f"{OUT / 'HOLD'} present"})
        return 0
    st = switcher_status()
    live = st.get("live")
    raw_meter_fn = meter_fn
    meter_fn = lambda: levelled(raw_meter_fn(), plan.get("level_model"))  # noqa: E731  unset: all-models only
    meter = meter_fn()
    t1 = clock()
    now += t1 - t0  # a slow status or meter read moves time on too: windows are judged when the pass acts
    t_now = t1  # the clock sample `now` stands for: a stamp taken later is now + clock() - t_now

    def manual_now():  # read at each decision: a human can switch during a slow poll
        return manual_switch(last_switch(), read_markers(), live)
    try:
        runs = runs_fn()
    except Exception:  # noqa: BLE001  unreadable runs count as live
        runs = None
    orders = orders or default_orders()
    burn = burn_now(live, meter, now, plan["account_end"], burn_fn)
    d = decide(meter, live, now, plan, state, read_markers(), manual=manual_now(), live_runs=runs, burn=burn)
    pre = None
    if d.get("poll"):
        last = epoch(state.get("last_poll")) or 0
        gap = plan["account_end"]["poll_min"] if d.get("warn_line") is not None and d.get("pct_left") is not None and (
            d["pct_left"] <= d["warn_line"] + 1) else plan["fresh"]["max_age_min"]
        if not dry and now - last >= gap * 60 - 5:  # 5 s: a repeat each 60 s must not miss its poll by the pass's own time
            # the poll can take minutes: if this pass would brake on what it already sees, the brake goes out first
            pre = decide(meter, live, now, plan, state, read_markers(), polled=True, manual=manual_now(),
                         live_runs=runs, burn=burn)
            if ((pre["do"] == "stop" and (state.get("stopped") or {}).get("account") != live)
                    or (pre["do"] == "switch" and pre.get("under"))):
                d = pre  # a brake on a spent account is never deferred behind a slow poll (agents keep burning)
            else:
                if pre["do"] in ACTS:
                    write_notice({**pre, "do": "soft"}, now)
                state["last_poll"] = iso(now)
                save_state(state)
                poll_fn()
                st = switcher_status()
                live = st.get("live")
                meter = meter_fn()
                t_now = clock()
                now += t_now - t1  # time moved during the poll: windows and resets are judged at the new time
                burn = burn_now(live, meter, now, plan["account_end"], burn_fn)
                if (OUT / "HOLD").exists():
                    log({"do": "passive", "why": f"{OUT / 'HOLD'} appeared during the poll"})
                    return 0
        if d is not pre:
            d = decide(meter, live, now, plan, state, read_markers(), polled=True, manual=manual_now(), live_runs=runs,
                       burn=burn)
    d.update(next_refill(meter, plan, now))
    if state.get("stopped"):
        d["stopped_at"] = state["stopped"].get("at")
    rec = {"do": d["do"], "live": live, "to": d.get("to"), "why": d.get("why"), "pct_left": d.get("pct_left"),
           "line": d.get("line")}
    if dry or d["do"] in ("passive", "skip", "hold"):
        pl, ln = d.get("pct_left"), d.get("line")
        if not dry and d["do"] == "hold" and pl is not None and ln is not None and pl <= ln + plan["soft_margin_pct"]:
            write_notice({**d, "do": "soft"}, now)  # held near a line: the soft brake still goes out
        log({**rec, "acted": False})
        return 0
    rc = 0
    ep = state.get("account_end") or {}
    if ep and ep.get("account") != live:
        end_episode(state, d, orders, f"{live} is live now")
    elif ep and d.get("pct_left") is not None and d["pct_left"] > (ep.get("warn_line") or 0) + plan["account_end"]["clear_pct"]:
        end_episode(state, d, orders, f"{live} reads {d['pct_left']}%: it has reset")
    elif ep and lowered(ep, d.get("line")):
        end_episode(state, d, orders, f"{live}'s line was lowered from {ep['line']}% to {d['line']}%")
    if d.get("account_end") and d["do"] == "soft":
        write_notice(d, now)    # first: nothing new starts while the orders go out
        save_step(state, d, plan, burn, runs, orders, now)
    elif d.get("warning"):      # the warning zone: the runs are warned and keep working; nothing is refused
        d["warning_text"] = AE.warn_text(d["account"], d.get("pct_left"), burn, d.get("line"), plan["account_end"],
                                         bool(d.get("last_account")))
        warn_step(state, d, plan, burn, runs, orders, now)
    if d.get("emergency") and (state.get("stopped") or {}).get("account") != live:
        write_notice({**d, "do": "soft", "drain": True, "account_end": True}, now)
        t_e = clock()
        if not emergency_step(state, d, plan, burn, runs, runs_fn, orders, now):
            log({"do": "passive", "why": f"{OUT / 'HOLD'} appeared in the pause"})
            return 0
        now += clock() - t_e
        t_now = clock()
    saved = saved_lines(state, orders) if d["do"] in ("switch", "stop") and state.get("account_end") else None
    t2 = clock()
    brake = {}

    def still():
        """A slow arm can close a window, pass a reset or spend a target: re-read the meter and re-decide at the new
        time (without this pass's own pending marker); the act goes ahead only if the same act is still due."""
        if (OUT / "HOLD").exists():  # the owner's brake, set while we armed
            return False
        mk = {k: v for k, v in read_markers().items() if k != d.get("key")}
        live2 = switcher_status().get("live") or live  # a human may have switched while we armed
        if live2 != live:
            return False
        m2, n2 = meter_fn(), now + clock() - t2
        d2 = decide(m2, live, n2, plan, state, mk, polled=True, manual=manual_switch(last_switch(), mk, live),
                    live_runs=runs, burn=burn)
        d2.update(next_refill(m2, plan, n2))
        same = d2["do"] == d["do"] and d2.get("to") == d.get("to")
        if same and d2.get("under"):  # exhaustion seen on the recheck latches into the marker
            d["under"] = True
        # a brake that became due while we armed is never dropped with the lapsed act: a stop now due, or a spent live
        # account whose switch target changed, stops the fleet now (the next pass switches from the stopped fleet)
        due = d2["do"] == "stop" or (d2["do"] == "switch" and d2.get("under"))
        if d["do"] == "stop" and due:
            d.update(next_refill(m2, plan, n2))
            return True  # live is still spent: the stop holds even if a switch target appeared meanwhile
        if not same and due and d["do"] != "stop" and (state.get("stopped") or {}).get("account") != live:
            brake.update({**d2, "do": "stop", "key": d2["key"] if d2["do"] == "stop" else stop_key(live, m2.get(live) or {}, n2)})
            return ["fleet-stop"]
        return same
    if d["do"] == "switch" and not d.get("under") and (runs is None or runs):
        # a switch made above the line (a priority or reset pull, nothing spent) waits while a detached run is live, so
        # it finishes on its own account and keeps its cache (owner 2026-11-20, "live runs finish past"); at most
        # pull_drain_max_s after the first drain notice. A switch at or under the line waits in decide (drained).
        bound = plan.get("pull_drain_max_s") or 0
        nt = read_json(OUT / "notice.json", {}) or {}
        since = epoch(nt.get("since")) if nt.get("state") == "soft" and nt.get("drain") else None
        if isinstance(bound, (int, float)) and bound > 0 and (since is None or now - since < bound):
            write_notice({**d, "do": "soft", "drain": True,
                          "why": f"the switch to {d['to']} waits while live runs finish: {d.get('why')}"}, now)
            left_s = int(bound - (now - since)) if since is not None else int(bound)
            log({**rec, "do": "drain", "acted": False,
                 "why": f"switch to {d['to']} waits while live runs finish ({runs_why(runs)}), at most {left_s} s more "
                        f"(pull_drain_max_s {bound}); was: {d.get('why')}"})
            return 0
    if d["do"] == "switch":
        write_marker(d["key"], {"phase": "pending", "at": iso(now), "from": live, "to": d["to"], "under": d.get("under"),
                                "line": d.get("line")})
        write_notice({**d, "do": "soft", "drain": True, "account_end": True}, now)  # nothing starts inside the switch
        res = armed_call(st, ["use", d["to"]], still)
        ok = (res.get("use") or (1,))[0] == 0
        lapsed = (res.get("use") or (1,))[0] is None and "lapsed" in str(res.get("use"))
        # `ended`: a switch of this transition in the log after the call returned is his, not this marker's
        write_marker(d["key"], {"phase": "done" if ok else "lapsed" if lapsed else "failed", "at": iso(now), "from": live, "to": d["to"],
                                "under": d.get("under"), "line": d.get("line"), "result": res,
                                "ended": iso(now + clock() - t_now)})
        if ok:
            state.pop("stopped", None)
            save_state(state)
            write_notice({**d, "do": "normal"}, now)
            if saved is not None:
                record_step(state, "switch", f"{live} -> {d['to']}; {facts(d, plan, burn, runs)}; before the switch: "
                            f"{saved}", now + clock() - t2)
                state.pop("account_end", None)
                save_state(state)
        rec["result"], rc = res, 0 if ok else 1
        if not ok and not lapsed and d.get("under") and (state.get("stopped") or {}).get("account") != live:
            # a failed switch off a spent account never leaves it burning: stop now, retry the switch from the stop
            res2 = armed_call(switcher_status() or st, ["fleet-stop"])
            rec["brake"] = res2
            if (res2.get("fleet-stop") or (1,))[0] == 0:
                brake.update({**d, "do": "stop", "key": stop_key(live, meter.get(live) or {}, now),
                              "why": f"switch {d['key']} failed and {live} is spent: hard stop"})
                res = {**res, "fleet-stop": res2["fleet-stop"]}
        if brake:
            braked = (res.get("fleet-stop") or (1,))[0] == 0
            write_notice(brake, now)
            if braked:
                record_stop(state, brake, now + clock() - t2)
                if saved is not None:
                    record_step(state, "stop in place of the switch", f"{facts(d, plan, burn, runs)}; before the stop: "
                                f"{saved}", now + clock() - t2)
            rc = 0 if braked else 1
    elif d["do"] == "stop":
        write_notice(d, now)
        res = armed_call(st, ["fleet-stop"], still)
        rec["result"], rc = res, 0 if (res.get("fleet-stop") or (1,))[0] == 0 else 1
        if not rc:  # recorded only once the fleet is stopped: a pass that died mid-call retries the stop
            record_stop(state, d, now + clock() - t2)
            if saved is not None:
                record_step(state, "stop, no account has headroom", f"{facts(d, plan, burn, runs)}; before the stop: {saved}",
                            now + clock() - t2)
                state.pop("account_end", None)
                save_state(state)
    elif d["do"] == "start":
        res = armed_call(st, ["fleet-start"], still)
        if (res.get("fleet-start") or (1,))[0] == 0:
            state.pop("stopped", None)
            save_state(state)
            write_notice({**d, "do": "normal"}, now)
        else:
            rc = 1
        rec["result"] = res
    else:
        if d["do"] == "stopped":
            stopped = state.get("stopped") or {}
            stopped.update({k: d[k] for k in ("reset_at", "reset_account") if k in d})
            save_state(state)
            notify_stop(state)
        write_notice(d, now)
    log({**rec, "acted": d["do"] in ("switch", "stop", "start")})
    return rc


# ------------------------------------------------------------------ status
def status(rate=None, model=None) -> int:
    plan, state, now = load_plan(), load_state(), time.time()
    meter = levelled(meter_now(), model or plan.get("level_model"))
    live = switcher_status().get("live")
    hold = (OUT / "HOLD").exists()
    mk = read_markers()
    burn = burn_now(live, meter, now, plan["account_end"], default_burn)
    d = decide(meter, live, now, plan, state, mk, polled=True, manual=manual_switch(last_switch(), mk, live),
               live_runs=default_runs(), burn=burn)
    pl = pool(meter, now, plan, live)
    rate = rate if rate is not None else pl.get("rate_pct_h")
    print(json.dumps({"live": live, "hold": hold, "level_model": model or plan.get("level_model"),
                      "levels": {n: {"week_pct_left": r.get("week_pct_left"), "week_limit": r.get("week_limit"),
                                     "model_weeks_left": r.get("model_weeks_left")} for n, r in meter.items()},
                      "next_pass": {"do": "passive", "why": f"{OUT / 'HOLD'} present",
                                                                "would_do": d} if hold else d,
                      "account_end": {"burn": burn, "warn_line": d.get("warn_line"),
                                             "pause_s": AE.pause_s(burn, plan["account_end"]),
                                             "episode": state.get("account_end")},
                      "pool": pl, "notice": read_json(OUT / "notice.json"), "stopped": state.get("stopped")},
                     indent=1, sort_keys=True))
    print(f"\nThe week ahead at {rate} %/h (the engine's own pick run forward on the meter's reset times; "
          f"polls, soft notices, stops and a respected manual switch not modelled){' -- HOLD present: no pass acts until it is removed' if hold else ''}:")
    if rate:
        print("\n".join(week_lines(simulate(meter, now, plan, live, rate), plan)))
    else:
        print("no burn rate: pass --rate")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("status")
    p.add_argument("--rate", type=float, default=None, help="burn %%/h for the week ahead (default: the pool's pace)")
    p.add_argument("--model", default=None, help="read each account's level as a run of this model sees it (the "
                   "lower of all-models and its own weekly limit); acts on nothing")
    a = ap.parse_args(argv)
    if a.cmd == "check":
        return check(dry=a.dry_run, passes=5)
    return status(a.rate, a.model)


if __name__ == "__main__":
    sys.exit(main())
