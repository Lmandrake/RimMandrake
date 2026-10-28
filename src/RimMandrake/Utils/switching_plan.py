#!/usr/bin/env python3
"""The standard switching plan engine (ACCOUNTS_PLAN_BUILD_STANDARD_SWITCHING): which Claude account this machine
burns, read every pass from the meter (account_usage.py) and the rules in switching_plan.json. No LLM, no dates in
code: reset times come from the meter each week.

Each pass:
  target = the owner's fixed priority (10:15: steven after his reset to 50%, then system, then lukas): the first
           account in plan order that is MEASURED, fresh, inside its window (steven: the first 48 h after his
           reset) and above its line (steven: leave_pct_left; others: the switch-away floor, 0%, while another
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

Brake: a file HOLD in the output dir makes every pass passive (the owner's or an agent's brake); it is the only
gate (the account_failover cutover gate was removed 2026-10-28: that script is retired and never wrote its marker).

    switching_plan.py check [--dry-run]   one pass (the timer runs this every 5 min)
    switching_plan.py status [--rate R]   what the next pass would do, the pool, the notice and the week ahead
                                          (simulate() at R %/h, default the pool's pace); acts on nothing
    switching_plan.py install [--deploy D] the durable systemd user timer account-plan.timer

Env seams (selftests): RM_SWITCH_PLAN (plan json), RM_SWITCH_PLAN_DIR (output dir), RM_CLAUDE_ACCOUNT (switcher).
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
OUT = Path(os.environ.get("RM_SWITCH_PLAN_DIR", "/mnt/d/ClaudeWork/rimmandrake/switching_plan"))
CA = os.environ.get("RM_CLAUDE_ACCOUNT") or str(Path.home() / ".local/bin/claude-account")
UNIT = "account-plan"   # outside the rm-*/testq-* glob of timers_guard on purpose: nothing else restarts or stops it
WEEK = 7 * 86400
STALE_PENDING_S = 2400  # arm + use + disarm at 600 s each plus the reads: a pending marker older is a pass that died
NOTICE_FRESH_S = 20 * 60  # readers (slot_allocator) ignore an older notice: the timer stopped
DRY = False
clock = time.time  # a seam: check() re-reads it after the slow poll


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


def lines(meter: dict, plan: dict, now: float) -> tuple[dict, dict]:
    """-> ({name: line}, {name: eligible}). An account's line is its leave_pct_left when it has one; else the
    switch-away floor while some OTHER account has budget above its wait floor to take over, else the wait floor
    (we idle on it until a reset). Eligible = MEASURED, fresh, in its window, above its line."""
    fl = plan["floors"]

    def ok(n, ln):
        r = meter.get(n)
        return (usable(r) and not reset_passed(r, now) and in_window(plan, n, r, now, plan.get("window_margin_min", 0) * 60)
                and r["week_pct_left"] > ln)

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


# ------------------------------------------------------------------ the decision (pure)
def decide(meter: dict, live, now: float, plan: dict, state: dict, markers: dict, polled: bool = False) -> dict:
    """-> {do: skip|poll|normal|soft|switch|hold|stop|stopped|start, to, account, line, pct_left, why, poll}
    (the HOLD brake is the caller's: check() and status())"""
    if not live:
        return {"do": "skip", "why": "live account unknown (claude-account --json status failed)"}
    order, fr = plan["order"], plan["fresh"]
    line, elig = lines(meter, plan, now)
    for m in markers.values():  # an account we left at its line is no target again before its reset: no flapping
        f = m.get("from")       # when its meter recovers and re-reads the same last 1%
        rs = next_reset(meter.get(f) or {}, now) if f in elig and f != live else None
        # a pending marker whose target is live now is a switch that landed before its pass could record it
        landed = m.get("phase") == "done" or (m.get("phase") == "pending" and m.get("to") == live)
        if landed and m.get("under") and rs is not None and (epoch(m.get("at")) or 0) > rs - WEEK:
            elig[f] = False
    lr = meter.get(live) or {}
    pl = left(plan, lr, now)
    if ((state.get("stopped") or {}).get("account") == live and live in elig and pl is not None
            and pl <= line[live] + plan["soft_margin_pct"]):
        elig[live] = False  # a fleet stopped in its soft zone never restarts there: another account with budget wins
    target = pick(meter, plan, now, elig)
    blind = blind_zero(plan, lr, now)
    base = {"account": live, "line": line.get(live), "pct_left": left(plan, lr, now), "to": None}

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
        if p is not None and n in line and p - line[n] <= fr["near_pct"] and (a is None or a > fr["max_age_min"]):
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
    # under its line on a post-reset reading: the reading is an upper bound (usage only grows inside a week), so even
    # an old or ESTIMATE figure proves the line is reached
    under = p is not None and live in line and p <= line[live] and not reset_passed(lr, now)
    # a windowed account (steven) past its window is as spent as one at its line; the window is timed from the last
    # reset the recorded one implies, so it is enforced even when his reading predates that reset
    w, nr = (plan["accounts"].get(live) or {}).get("window_h_after_reset"), next_reset(lr, now)
    out = live in order and w is not None and nr is not None and (WEEK - (nr - now)) / 3600 > w
    under = under or out

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
        if m and m.get("phase") != "failed":
            age = now - (epoch(m.get("at")) or 0)
            if m.get("phase") == "pending" and age < STALE_PENDING_S and under:
                return {**base, "do": "stop", "key": stop_key(live, lr, now),
                        "why": f"transition {key} is pending yet live is still {live} at {p}% <= its "
                               f"{line[live]}% line: stop rather than overshoot"}
            if (m.get("phase") == "done" or age < STALE_PENDING_S) and not under:
                return {**base, "do": "hold", "to": target, "key": key,
                        "why": f"transition {key} already {m.get('phase')}: never repeated; live is still {live} "
                               "(a done switch that reads back as the old account is a human's move: respected)"}
        if target in stale:
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
        return {**base, "do": "soft", "why": "reading not fresh near a line after a poll: " + "; ".join(stale[live])}
    if p <= line[live] + plan["soft_margin_pct"]:
        return {**base, "do": "soft", "why": f"{live} at {p}% is within {plan['soft_margin_pct']} of its "
                                             f"{line[live]}% line: switch pending, publish and finish"}
    lead_h = plan["switch_lead_min"] / 60
    for n in order:
        r = meter.get(n) or {}
        h = r.get("hours_to_week_reset")
        if n == live or h is None or not 0 < h <= lead_h:
            continue
        fresh = {**r, "source": "MEASURED", "stale": False, "week_pct_left": 100.0, "age_min": 0,
                 "hours_to_week_reset": 168.0, "week_resets_at": iso((next_reset(r, now) or now) + WEEK)}
        after = {**meter, n: fresh}
        _l, el = lines(after, plan, now + h * 3600)
        if pick(after, plan, now + h * 3600, el) not in (live, None):
            return {**base, "do": "soft", "why": f"{n}'s reset in {round(h * 60)} min will pull the machine to it: "
                                                 "switch pending, publish and finish"}
    return {**base, "do": "normal", "why": f"{live} at {p}% above its {line[live]}% line"}


# ------------------------------------------------------------------ the pool (pure; slot_allocator paces on it)
def pool(meter: dict, now: float, plan: dict, live=None) -> dict:
    """What the plan will still spend and the burn rate that spends it without losing more than the owner's priority
    gives up: each account's present budget (down to its line) is due at its expiry (next reset; steven's window
    end), unless higher-priority eligible accounts that outlive it hold more than the pace burns before it expires
    (then it is lost by his rule and not paced for), and
    its next refill (100 - line) at the refill's own expiry. The rate is the max over deadlines of cumulative spend /
    hours; pct and deadline_h are the binding deadline's. -> {pct, rate_pct_h, deadline_h, total_pct, parts}; rate
    None when no account has a reset time. `live` is unused (kept for the allocator's call)."""
    fl = plan["floors"]
    plain = [n for n in plan["order"] if (plan["accounts"].get(n) or {}).get("window_h_after_reset") is None]
    exp = {n: expiry(plan, n, meter.get(n), now) for n in plan["order"]}
    _ln, elig = lines(meter, plan, now)
    last = max((n for n in plain if exp[n] is not None), key=lambda n: exp[n], default=None)
    horizon = max((exp[n] for n in plain if exp[n] is not None), default=None)
    horizon = None if horizon is None else horizon + WEEK  # every account's refills up to one week past the last expiry
    present, refills = {}, []
    for n in plan["order"]:
        r = meter.get(n) or {}
        cfg = plan["accounts"].get(n) or {}
        e = exp[n]
        if e is None:
            continue
        p = left(plan, r, now)
        if p is None and reset_passed(r, now):
            p = 100.0
        leave = cfg.get("leave_pct_left")
        ln = leave if leave is not None else (fl["wait_pct_left"] if n == last else fl["switch_away_pct_left"])
        if e > now and (cfg.get("window_h_after_reset") is None or in_window(plan, n, r, now)):
            present[n] = (max(0.0, (p if p is not None else 0.0) - ln), e)
        k = 1
        while k == 1 or (horizon is not None and e + k * WEEK <= horizon):
            refills.append((n, 100.0 - ln, e + k * WEEK))
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

    # the owner's priority: a present budget is lost at its expiry (and not paced for) when the higher eligible
    # accounts that outlive it hold more than the pool's pace burns before it expires; the pace depends on what is
    # kept, so settle it by a few rounds (start with everything kept: the fastest pace, the fewest losses)
    keep = set(present)
    for _ in range(4):
        rate = pace([(n, *present[n]) for n in keep] + refills)[2]
        new = {n for n, (_sp, e) in present.items()
               if sum(present[m][0] for m in present if m != n and elig.get(m) and outranks(plan, m, n)
                      and present[m][1] > e) < rate * (e - now) / 3600 or not any(
                   elig.get(m) and outranks(plan, m, n) and present[m][1] > e for m in present if m != n)}
        if new == keep:
            break
        keep = new
    parts = [(n, *present[n]) for n in keep] + refills
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
        ln, el = lines(sm, plan, t)
        tgt = pick(sm, plan, t, el)
        if tgt != cur:
            ev.append({"kind": "target", "at": t, "target": tgt, "pct": snap()})
            cur = tgt
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
        elif e["target"] is None:
            out.append(f"{when}  IDLE    no account above its line: hard stop until a reset  [{pc}]")
        else:
            a = plan["accounts"].get(e["target"]) or {}
            to = a.get("leave_pct_left")
            out.append(f"{when}  target  {e['target']}" + (f" (to {to}% left, inside its window)" if to is not None else "")
                       + f"  [{pc}]")
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
    return r.returncode, r.stdout if full else (r.stdout + r.stderr)[-2000:]


def switcher_status() -> dict:
    rc, out = run([CA, "--json", "status"], full=True, timeout=120)
    if rc != 0:
        return {}
    dec, i = json.JSONDecoder(), out.find("{")
    while i >= 0:
        try:
            obj, _ = dec.raw_decode(out[i:])
            if isinstance(obj, dict) and "live" in obj:
                return obj
        except ValueError:
            pass
        i = out.find("{", i + 1)
    return {}


def meter_now() -> dict:
    sys.path.insert(0, str(HERE))
    import account_usage
    return account_usage.read_now().get("accounts") or {}


def meter_poll() -> None:
    rc, out = run([sys.executable, str(HERE / "account_usage.py"), "poll"], timeout=420)
    log({"do": "meter_poll", "rc": rc, "out": out[-300:]})


def write_notice(d: dict, now: float) -> None:
    state = {"soft": "soft", "stop": "stop", "stopped": "stop"}.get(d["do"], "none")
    prev = read_json(OUT / "notice.json", {}) or {}
    since = prev.get("since") if prev.get("state") == state and prev.get("since") else iso(now)
    msg = {"soft": "switch pending: publish and finish; no new helpers",
           "stop": "hard stop: the fleet is stopped until a reset", "none": ""}[state]
    write_atomic(OUT / "notice.json", {"state": state, "since": since, "at": iso(now), "account": d.get("account"),
                                       "line": d.get("line"), "pct_left": d.get("pct_left"), "message": msg,
                                       "why": d.get("why")})


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


def check(dry: bool = False, now=None, meter_fn=meter_now, poll_fn=meter_poll) -> int:
    """One pass under an exclusive non-blocking lock: a pass that finds another running stands down (the markers are
    not a lock, and two passes could both switch)."""
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "check.lock", "a") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            log({"do": "skip", "why": "another pass holds check.lock", "acted": False})
            return 0
        return _check(dry, now, meter_fn, poll_fn)


ACTS = ("soft", "stop", "stopped", "switch")


def _check(dry, now, meter_fn, poll_fn) -> int:
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
    meter = meter_fn()
    t1 = clock()
    now += t1 - t0  # a slow status or meter read moves time on too: windows are judged when the pass acts
    d = decide(meter, live, now, plan, state, read_markers())
    pre = None
    if d.get("poll"):
        last = epoch(state.get("last_poll")) or 0
        if not dry and now - last >= plan["fresh"]["max_age_min"] * 60:
            # the poll can take minutes: if this pass would brake on what it already sees, the brake goes out first
            pre = decide(meter, live, now, plan, state, read_markers(), polled=True)
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
                now += clock() - t1  # time moved during the poll: windows and resets are judged at the new time
                if (OUT / "HOLD").exists():
                    log({"do": "passive", "why": f"{OUT / 'HOLD'} appeared during the poll"})
                    return 0
        if d is not pre:
            d = decide(meter, live, now, plan, state, read_markers(), polled=True)
    rec = {"do": d["do"], "live": live, "to": d.get("to"), "why": d.get("why"), "pct_left": d.get("pct_left"),
           "line": d.get("line")}
    if dry or d["do"] in ("passive", "skip", "hold"):
        pl, ln = d.get("pct_left"), d.get("line")
        if not dry and d["do"] == "hold" and pl is not None and ln is not None and pl <= ln + plan["soft_margin_pct"]:
            write_notice({**d, "do": "soft"}, now)  # held near a line: the soft brake still goes out
        log({**rec, "acted": False})
        return 0
    rc = 0
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
        d2 = decide(m2, live, n2, plan, state, mk, polled=True)
        same = d2["do"] == d["do"] and d2.get("to") == d.get("to")
        if same and d2.get("under"):  # exhaustion seen on the recheck latches into the marker
            d["under"] = True
        # a brake that became due while we armed is never dropped with the lapsed act: a stop now due, or a spent live
        # account whose switch target changed, stops the fleet now (the next pass switches from the stopped fleet)
        due = d2["do"] == "stop" or (d2["do"] == "switch" and d2.get("under"))
        if d["do"] == "stop" and due:
            return True  # live is still spent: the stop holds even if a switch target appeared meanwhile
        if not same and due and d["do"] != "stop" and (state.get("stopped") or {}).get("account") != live:
            brake.update({**d2, "do": "stop", "key": d2["key"] if d2["do"] == "stop" else stop_key(live, m2.get(live) or {}, n2)})
            return ["fleet-stop"]
        return same
    if d["do"] == "switch":
        write_marker(d["key"], {"phase": "pending", "at": iso(now), "from": live, "to": d["to"], "under": d.get("under")})
        write_notice({**d, "do": "soft"}, now)
        res = armed_call(st, ["use", d["to"]], still)
        ok = (res.get("use") or (1,))[0] == 0
        lapsed = (res.get("use") or (1,))[0] is None and "lapsed" in str(res.get("use"))
        write_marker(d["key"], {"phase": "done" if ok else "lapsed" if lapsed else "failed", "at": iso(now), "from": live, "to": d["to"],
                                "under": d.get("under"), "result": res})
        if ok:
            state.pop("stopped", None)
            save_state(state)
            write_notice({**d, "do": "normal"}, now)
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
                state["stopped"] = {"account": live, "key": brake.get("key"), "at": iso(now)}
                save_state(state)
            rc = 0 if braked else 1
    elif d["do"] == "stop":
        write_notice(d, now)
        res = armed_call(st, ["fleet-stop"], still)
        rec["result"], rc = res, 0 if (res.get("fleet-stop") or (1,))[0] == 0 else 1
        if not rc:  # recorded only once the fleet is stopped: a pass that died mid-call retries the stop
            state["stopped"] = {"account": live, "key": d["key"], "at": iso(now)}
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
        write_notice(d, now)
    log({**rec, "acted": d["do"] in ("switch", "stop", "start")})
    return rc


# ------------------------------------------------------------------ status / install
SERVICE = """[Unit]
Description=Claude account standard switching plan (switching_plan.py check)

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {script} check
TimeoutStartSec=2700s
"""
TIMER = """[Unit]
Description=Claude account standard switching plan, every 5 min

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
"""


def install(deploy: str) -> str:
    script = Path(deploy) / "src/RimMandrake/Utils/switching_plan.py"
    if not script.exists():
        raise SystemExit(f"install: {script} does not exist (pass --deploy <checkout>)")
    units = Path.home() / ".config/systemd/user"
    units.mkdir(parents=True, exist_ok=True)
    (units / f"{UNIT}.service").write_text(SERVICE.format(script=script))
    (units / f"{UNIT}.timer").write_text(TIMER)
    for argv in (["daemon-reload"], ["enable", "--now", f"{UNIT}.timer"]):
        subprocess.run(["systemctl", "--user", *argv], check=True)
    return f"{UNIT}.timer -> {script}"


def status(rate=None) -> int:
    plan, state, now = load_plan(), load_state(), time.time()
    meter = meter_now()
    live = switcher_status().get("live")
    hold = (OUT / "HOLD").exists()
    d = decide(meter, live, now, plan, state, read_markers(), polled=True)
    pl = pool(meter, now, plan, live)
    rate = rate if rate is not None else pl.get("rate_pct_h")
    print(json.dumps({"live": live, "hold": hold, "next_pass": {"do": "passive", "why": f"{OUT / 'HOLD'} present",
                                                                "would_do": d} if hold else d,
                      "pool": pl, "notice": read_json(OUT / "notice.json"), "stopped": state.get("stopped")},
                     indent=1, sort_keys=True))
    print(f"\nThe week ahead at {rate} %/h (the engine's own pick run forward on the meter's reset times; "
          f"polls, soft notices and stops not modelled){' -- HOLD present: no pass acts until it is removed' if hold else ''}:")
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
    p = sub.add_parser("install")
    p.add_argument("--deploy", default=os.environ.get("RM_PULSE_DEPLOY", "/mnt/d/ClaudeWork/rimmandrake/pulse-deploy"))
    a = ap.parse_args(argv)
    if a.cmd == "check":
        return check(dry=a.dry_run)
    if a.cmd == "install":
        print(install(a.deploy))
        return 0
    return status(a.rate)


if __name__ == "__main__":
    sys.exit(main())
