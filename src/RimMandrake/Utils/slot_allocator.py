#!/usr/bin/env python3
"""slot_allocator.py: how many helpers each seat may run now, from the measured token pace (SLOT_ALLOCATOR_BUILD_RULES_FILE).

Owner, 2026-10-26 ~13:30 PDT: "We should make this a semi-automated process going forward, so I don't have to stare at
it and guess." 13:05 (relayed): "If you already built the capability, please use it to determine the number of Foundry
and Bench agents yourself. My 5 was a guess."

Design: design/RimMandrake/operating_modes_2026-10-26.md §1.1-1.5 (three dials, hysteresis) and §9 (the measured fit).
Every number is in slot_rules.json beside this file; this code holds none of them.

  slot_allocator.py now [--json] [--write] [--seat S]   one line: mode, N per seat, why (--write: allocation.json)
  slot_allocator.py set --n N [--seat S] [--mode M] --owner-said "<his words>" [--hours H]
                                                         his word holds until the burn account's weekly reset
  slot_allocator.py clear                               drop his word

HOW N IS SET, in order (each step can only lower what the previous one allowed, except his word):
  1. Token mode from P, the pace ratio of the account these seats burn (`burn_account`, default the account this
     machine's own login uses): P = % of the week left / (days to reset x 100/7). DARK / ALMOST_OUT / CRUISE / BURN /
     SWEEP with the entry and leave lines of §1.1. Stepping DOWN is immediate; stepping UP needs the line held
     cross_hold_h and the mode at least min_mode_min old. A weekly reset ends ALMOST_OUT at once.
  2. Total fit (R8): mean helpers running over the last window_h x sustainable %/h / measured %/h. The measured %/h is
     the slope of account_usage's series when it has slope_min_points over slope_min_span_h; otherwise messages sent from
     THIS machine over the window / msgs_per_pct (the 13:05 hand calibration). Raised by at most raise_step per check.
  3. Split: FOUNDRY floor(total x share), BENCH the rest. While he writes in a window (presence BENCH), BENCH <= bench_n.
  4. His word (`set --owner-said`) replaces any of that. The 5-hour brake (session over 90% used) is 0 for everyone,
     even over his word: the account would refuse the calls anyway.
A rule never fires on an UNMEASURED input: a blind meter holds the previous mode, or 2 helpers if there is none.
Spare accounts are named as a recommendation; this file never switches an account.

Files (program-read, so scratch): $RM_STREAMS_DIR (default D:\\ClaudeWork\\rimmandrake\\streams) allocation.json
(the latest decision and its hysteresis state) and slot_override.json (his word). The 15-min writer is
pulse/streams.py collect (rm-pulse-streams.timer); the spawn hook is .claude/hooks/block_agent_over_slots.py.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

RULES = Path(os.environ.get("RM_SLOT_RULES", HERE / "slot_rules.json"))
TZ = ZoneInfo("America/Los_Angeles")
HOUR = 3600.0
SEAT_PROJECT = {"BENCH": "-home-mandrake-rm-bench", "FOUNDRY": "-home-mandrake-rm-foundry"}
CHUNK = 1 << 20


def streams_dir() -> Path:
    return Path(os.environ.get("RM_STREAMS_DIR", "/mnt/d/ClaudeWork/rimmandrake/streams"))


def projects_dir() -> Path:
    return Path(os.environ.get("RM_SLOT_PROJECTS", os.path.expanduser("~/.claude/projects")))


def owner_ledger() -> Path:
    data = Path(os.environ.get("RM_STREAMS_BENCH", "/home/mandrake/rm/bench"))
    return Path(os.environ.get("RM_SLOT_OWNER_LEDGER", data / "infrastructure/state/ledger/events/OWNER.jsonl"))


def load_rules(path=None) -> dict:
    return json.loads(Path(path or RULES).read_text(encoding="utf-8"))


def iso_z(t: float) -> str:
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def iso_local(t: float) -> str:
    return datetime.fromtimestamp(t, TZ).isoformat(timespec="seconds")


def epoch(s):
    if s is None or s == "":
        return None
    if isinstance(s, (int, float)):
        return float(s)
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


# ------------------------------------------------------------------------------------------------ transcript readers
def _records_backward(path, stop_before=None, max_bytes=64 * CHUNK):
    """Yield parsed records from the END of a jsonl, newest first; stop once a record is older than stop_before."""
    try:
        f = open(path, "rb")
    except OSError:
        return
    with f:
        f.seek(0, 2)
        pos, buf, read = f.tell(), b"", 0
        while pos > 0 and read < max_bytes:
            step = min(CHUNK, pos)
            pos -= step
            f.seek(pos)
            buf = f.read(step) + buf
            read += step
            lines = buf.split(b"\n")
            buf = lines[0] if pos > 0 else b""
            for raw in reversed(lines[1:] if pos > 0 else lines):
                if not raw.strip():
                    continue
                try:
                    rec = json.loads(raw)
                except ValueError:
                    continue
                if not isinstance(rec, dict):
                    continue
                yield rec
                t = epoch(rec.get("timestamp"))
                if stop_before is not None and t is not None and t < stop_before:
                    return


def helper_state(path, now, rules):
    """(running?, reason) for one subagent transcript. The stale_agents.py test (Lodestar): FINISHED = the last
    assistant record ends end_turn, nothing user-side after it, and the file is quiet. Anything unsure is running."""
    h = rules["helpers"]
    try:
        age = now - os.path.getmtime(path)
    except OSError:
        return False, "gone"
    if age > h["live_window_s"]:
        return False, f"silent {age / 60:.0f} min (past the 600 s kill)"
    stop, user_after = None, False
    for rec in _records_backward(path, max_bytes=2 * CHUNK):
        msg = rec.get("message")
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            stop = msg.get("stop_reason") or "none"
            break
        if rec.get("type") == "user":
            user_after = True
    if stop is None:
        return True, "no assistant record yet"
    if user_after:
        return True, "work resumed after its last answer"
    if stop != "end_turn":
        return True, f"last record {stop}"
    if age < h["quiet_s"]:
        return True, f"ended {age:.0f} s ago (quiet {h['quiet_s']} s)"
    return False, "ended"


def running_helpers(project_paths, now, rules):
    out = []
    for proj in project_paths:
        for p in glob.glob(os.path.join(str(proj), "*", "subagents", "agent-*.jsonl")):
            try:
                if now - os.path.getmtime(p) > rules["helpers"]["live_window_s"]:
                    continue
            except OSError:
                continue
            run, why = helper_state(p, now, rules)
            if run:
                out.append({"id": os.path.basename(p)[len("agent-"):-len(".jsonl")], "why": why, "path": p})
    return out


def _first_ts(path):
    try:
        with open(path, "rb") as f:
            for _ in range(50):
                raw = f.readline()
                if not raw:
                    break
                try:
                    t = epoch(json.loads(raw).get("timestamp"))
                except (ValueError, AttributeError):
                    continue
                if t:
                    return t
    except OSError:
        pass
    return None


def mean_helpers(project_paths, now, window_s):
    """Mean subagents running over [now-window, now]: each counts from its first record to its last write."""
    lo, total = now - window_s, 0.0
    for proj in project_paths:
        for p in glob.glob(os.path.join(str(proj), "*", "subagents", "agent-*.jsonl")):
            try:
                end = os.path.getmtime(p)
            except OSError:
                continue
            if end < lo:
                continue
            start = _first_ts(p) or end
            total += max(0.0, min(end, now) - max(start, lo))
    return total / window_s


def messages_in_window(root, now, window_s):
    """API messages (distinct assistant message ids) written by any Claude session on this machine in the window."""
    lo, ids = now - window_s, set()
    files = glob.glob(os.path.join(str(root), "*", "*.jsonl")) + glob.glob(os.path.join(str(root), "*", "*", "subagents", "*.jsonl"))
    for p in files:
        try:
            if os.path.getmtime(p) < lo:
                continue
        except OSError:
            continue
        for rec in _records_backward(p, stop_before=lo):
            msg = rec.get("message")
            if rec.get("type") != "assistant" or not isinstance(msg, dict):
                continue
            t = epoch(rec.get("timestamp"))
            if t is not None and t >= lo and msg.get("id"):
                ids.add(msg["id"])
    return len(ids)


def _is_owner_text(rec):
    if rec.get("type") != "user" or rec.get("isSidechain") or rec.get("isMeta"):
        return False
    origin = rec.get("origin")
    if isinstance(origin, dict) and origin.get("kind"):
        return origin.get("kind") == "human"
    c = (rec.get("message") or {}).get("content")
    if isinstance(c, list):
        if any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
            return False
        c = " ".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
    txt = str(c or "").strip()
    return bool(txt) and not txt.startswith("<") and not txt.startswith("Caveat")


def owner_last_window(project_paths, now, horizon_s=6 * HOUR):
    """Epoch of his newest typed message in any seat window (top-level transcripts only), or None in the horizon."""
    best, lo = None, now - horizon_s
    for proj in project_paths:
        for p in glob.glob(os.path.join(str(proj), "*.jsonl")):
            try:
                if os.path.getmtime(p) < lo:
                    continue
            except OSError:
                continue
            for rec in _records_backward(p, stop_before=lo):
                if _is_owner_text(rec):
                    t = epoch(rec.get("timestamp"))
                    if t and t >= lo:
                        best = t if best is None else max(best, t)
                    break
    return best


def owner_last_card(path, now):
    best = None
    for rec in _records_backward(path, max_bytes=CHUNK):
        if rec.get("byCard"):
            t = epoch(rec.get("ts"))
            if t:
                best = t if best is None else max(best, t)
                break
    return best


# ------------------------------------------------------------------------------------------------ meter readers
def _au_dir():
    return Path(os.environ.get("RM_ACCOUNT_USAGE_DIR", "/mnt/d/ClaudeWork/rimmandrake/account_usage"))


def meter_now(now):
    import account_usage as AU
    return AU.read_now(now)


def machine():
    if os.environ.get("RM_SLOT_MACHINE"):
        return os.environ["RM_SLOT_MACHINE"]
    import account_usage as AU
    return AU.machine_name()


def pick_burn_account(accounts, rules, here):
    want = rules.get("burn_account") or "auto"
    if want != "auto":
        return want, "pinned in slot_rules.json"
    live = [a for a in accounts.values() if (a.get("machine") or "").lower() == here.lower()
            and a.get("source") == "MEASURED"]
    if live:
        a = max(live, key=lambda r: epoch(r.get("measured_at")) or 0)
        return a["account"], f"this machine's ({here}) live login"
    return None, f"no MEASURED reading from this machine ({here})"


def slope(account, resets_at, now, rules):
    """(%/h, points, span_h) from account_usage's series for this account and week, or (None, n, span)."""
    fit = rules["fit"]
    lo = now - fit["window_h"] * HOUR
    pts = {}
    for rec in _records_backward(_au_dir() / "series.jsonl", max_bytes=4 * CHUNK):
        t = epoch(rec.get("ts"))
        if t is not None and t < lo - HOUR:
            break
        if rec.get("account") != account or rec.get("source") != "MEASURED" or rec.get("week_pct_used") is None:
            continue
        if resets_at and epoch(rec.get("week_resets_at")) != epoch(resets_at):
            continue
        m = epoch(rec.get("measured_at"))
        if m is not None and m >= lo:
            pts[m] = float(rec["week_pct_used"])
    n = len(pts)
    if n < 2:
        return None, n, 0.0
    xs = sorted(pts)
    span = (xs[-1] - xs[0]) / HOUR
    if n < fit["slope_min_points"] or span < fit["slope_min_span_h"]:
        return None, n, span
    mx = sum(xs) / n
    my = sum(pts.values()) / n
    den = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (pts[x] - my) for x in xs) / den if den else 0.0
    return max(b * HOUR, 0.0), n, span


def latest_streams(now):
    rec = None
    for rec in _records_backward(streams_dir() / "series.jsonl", max_bytes=4 * CHUNK):
        break
    if not rec or now - (rec.get("t") or 0) > 2 * HOUR:
        return None, None
    ms = rec.get("measures") or {}
    v = lambda k: (ms.get(k) or {}).get("v") if (ms.get(k) or {}).get("m") == "MEASURED" else None  # noqa: E731
    return v("A1"), v("D1")


def read_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def gather(now=None, rules=None):
    now = now or time.time()
    rules = rules or load_rules()
    root = projects_dir()
    seat_paths = {s: root / SEAT_PROJECT[s] for s in rules["seats"] if s in SEAT_PROJECT}
    inp = {"source": "UNMEASURED", "account": None, "week_pct_left": None, "week_pct_used": None,
           "hours_to_week_reset": None, "week_resets_at": None, "session_pct_used": None, "spare": []}
    try:
        meter = meter_now(now).get("accounts") or {}
        here = machine()
        acc, how = pick_burn_account(meter, rules, here)
        inp["account_how"] = how
        a = meter.get(acc) if acc else None
        if a:
            inp.update(account=acc, source=a.get("source") if not a.get("stale") else "STALE",
                       week_pct_left=a.get("week_pct_left"), week_pct_used=a.get("week_pct_used"),
                       hours_to_week_reset=a.get("hours_to_week_reset"), week_resets_at=a.get("week_resets_at"),
                       session_pct_used=a.get("session_pct_used") if a.get("session_pct_left") is not None else None,
                       measured_at=a.get("measured_at"))
        for name, o in meter.items():
            if name == acc or o.get("week_pct_left") is None or o.get("source") not in ("MEASURED", "ESTIMATE"):
                continue
            inp["spare"].append({"account": name, "pct_left": o["week_pct_left"], "pct_used": o.get("week_pct_used"),
                                 "hours_to_reset": o.get("hours_to_week_reset"), "resets_at": o.get("week_resets_at"),
                                 "source": o.get("source")})
    except Exception as e:  # noqa: BLE001
        inp["meter_error"] = f"{type(e).__name__}: {e}"
    fit = rules["fit"]
    win = fit["window_h"] * HOUR
    inp["rate_pct_per_h"], inp["rate_src"] = None, None
    if inp["account"] and inp["source"] == "MEASURED":
        r, n, span = slope(inp["account"], inp["week_resets_at"], now, rules)
        if r is not None:
            inp["rate_pct_per_h"], inp["rate_src"] = round(r, 3), f"meter slope, {n} readings over {span:.1f} h"
        else:
            msgs = messages_in_window(root, now, win)
            inp["msgs_window"] = msgs
            if msgs:
                inp["rate_pct_per_h"] = round(msgs / fit["msgs_per_pct"] / fit["window_h"], 3)
                inp["rate_src"] = (f"{msgs} messages from this machine in {fit['window_h']} h / {fit['msgs_per_pct']} per % "
                                   f"(meter has {n} readings over {span:.1f} h, too few for a slope)")
    inp["mean_helpers"] = round(mean_helpers(list(seat_paths.values()), now, win), 2)
    inp["helpers_running"] = {s: len(running_helpers([p], now, rules)) for s, p in seat_paths.items()}
    w = owner_last_window(list(seat_paths.values()), now)
    inp["owner_window_min"] = None if w is None else round((now - w) / 60, 1)
    c = owner_last_card(owner_ledger(), now)
    inp["owner_card_min"] = None if c is None else round((now - c) / 60, 1)
    inp["A1"], inp["D1"] = latest_streams(now)
    ov = read_json(streams_dir() / "slot_override.json")
    inp["override"] = ov if isinstance(ov, dict) else None
    return inp


# ------------------------------------------------------------------------------------------------ the rules
def pace(inp):
    left, h = inp.get("week_pct_left"), inp.get("hours_to_week_reset")
    if left is None or h is None:
        return None
    days = max(h, 1.0) / 24
    return left / (days * 100 / 7)


def _token(inp, state, rules, now, P):
    tk = rules["token"]
    prev, since = state.get("token_mode"), state.get("since") or now
    pending = state.get("pending") or None
    measured = inp.get("source") == "MEASURED"
    h, used = inp.get("hours_to_week_reset"), inp.get("week_pct_used")
    reset_changed = bool(state.get("reset_at") and inp.get("week_resets_at")
                         and epoch(state["reset_at"]) != epoch(inp["week_resets_at"]))
    if reset_changed:
        prev, pending = None, None
    if used is not None and used >= tk["DARK"]["enter_pct_used_ge"]:
        return "DARK", None, since if prev == "DARK" else now
    burn_line = measured and P > tk["BURN"]["enter_p_gt"] and h is not None and h < tk["BURN"]["enter_reset_h_lt"]
    age = now - since

    def hold(to, hold_h):
        p = pending if pending and pending.get("to") == to else {"to": to, "since": now}
        if now - p["since"] >= hold_h * HOUR and age >= tk["min_mode_min"] * 60:
            return to, None, now
        return prev, p, since

    if prev in (None, "DARK"):
        return ("ALMOST_OUT" if P < tk["ALMOST_OUT"]["enter_p_lt"] else "CRUISE"), ({"to": "BURN", "since": now} if burn_line else None), now
    if prev == "ALMOST_OUT":
        if P > tk["ALMOST_OUT"]["leave_p_gt"]:
            return hold("CRUISE", tk["ALMOST_OUT"]["leave_hold_h"])
        return prev, None, since
    if prev == "CRUISE":
        if P < tk["ALMOST_OUT"]["enter_p_lt"]:
            return "ALMOST_OUT", None, now
        if burn_line:
            return hold("BURN", tk["cross_hold_h"])
        return prev, None, since
    if prev == "BURN":
        if P < tk["BURN"]["leave_p_lt"] or (h is not None and h < tk["BURN"]["leave_reset_h_lt"]):
            return "SWEEP", None, now
        return prev, None, since
    if prev == "SWEEP":
        if P < tk["ALMOST_OUT"]["enter_p_lt"]:
            return "ALMOST_OUT", None, now
        if age >= tk["SWEEP"]["hold_h"] * HOUR:
            return "CRUISE", None, now
        return prev, None, since
    return "CRUISE", None, now


def _queue(inp, state, rules):
    a1, d1 = inp.get("A1"), inp.get("D1")
    q = rules["queue"]
    if a1 is None and d1 is None:
        return "UNMEASURED", "queues unmeasured (no streams record in 2 h)"
    enter = (a1 is not None and a1 > q["paydown_enter"]["A1_gt"]) or (d1 is not None and d1 >= q["paydown_enter"]["D1_ge"])
    if enter:
        return "PAYDOWN", f"A1 {a1}, D1 {d1} over 3 d"
    if state.get("queue_mode") == "PAYDOWN":
        leave = (a1 is None or a1 < q["paydown_leave"]["A1_lt"]) and (d1 is None or d1 < q["paydown_leave"]["D1_lt"])
        if not leave:
            return "PAYDOWN", f"A1 {a1}, D1 {d1}: not yet under the leave lines"
    return "CLEAR", f"A1 {a1}, D1 {d1}"


def _presence(inp, rules):
    pr = rules["presence"]
    w, c = inp.get("owner_window_min"), inp.get("owner_card_min")
    if w is not None and w <= pr["bench_min"]:
        return "BENCH", f"he wrote in a window {w:.0f} min ago"
    near = [x for x in (w, c) if x is not None]
    if not near or min(near) > pr["afk_min"]:
        return "AFK", "no window message or card for 60 min"
    return "PHONE", (f"last window message {w:.0f} min ago" if w is not None else "no window message") + \
        (f", last card {c:.0f} min ago" if c is not None else "")


def _override_live(ov, now):
    if not isinstance(ov, dict) or not ov.get("ownerSaid"):
        return None
    until = epoch(ov.get("until"))
    if until is not None and until <= now:
        return None
    return ov


def _lent_view(sp):
    used = sp.get("pct_used")
    if used is None and sp.get("pct_left") is not None:
        used = 100.0 - sp["pct_left"]
    return used, sp.get("pct_left"), sp.get("hours_to_reset"), sp.get("resets_at")


def lent_allowance(sp, rules, now):
    """(max % of his week we may still draw now, why) for an account under lent_accounts, or (None, '') if none.
    The owner's rule for a lent account: never under the floor; outside the end window at most max_used_by_us_pct of
    the week used (all of it counted as ours); off-limits through off_limits_through."""
    pol = (rules.get("lent_accounts") or {}).get(sp.get("account"))
    if not pol:
        return None, ""
    used, left, h, _ = _lent_view(sp)
    name = sp["account"]
    if left is None or used is None or h is None:
        return 0.0, f"{name}: lent account unmeasured, left alone"
    off = epoch(pol.get("off_limits_through"))
    if off is not None and now < off:
        return 0.0, f"{name}: off-limits until {pol['off_limits_through']} (his rule: this week's share is already used)"
    by_floor = left - pol["floor_pct_left"]
    if h <= pol["end_window_h"]:
        cap, where = by_floor, f"last {pol['end_window_h']} h before his reset: down to the {pol['floor_pct_left']}% floor"
    else:
        cap = min(by_floor, pol["max_used_by_us_pct"] - used)
        where = f"up to {pol['max_used_by_us_pct']}% of his week used (counting all {used:.0f}% as ours), floor {pol['floor_pct_left']}%"
    return max(0.0, cap), f"{name}: {where}"


def check_plan(sp, draw_pct, rules, now):
    """(ok, why) for a plan to draw draw_pct of an account's week. Refuses anything the lent rule forbids."""
    cap, why = lent_allowance(sp, rules, now)
    if cap is None:
        return True, f"{sp.get('account')}: no lent rule"
    if draw_pct > cap + 1e-9:
        return False, f"refused: draw {draw_pct:.0f}% > {cap:.0f}% allowed ({why})"
    return True, f"ok: draw {draw_pct:.0f}% <= {cap:.0f}% allowed ({why})"


def spare_line(sp, rules, now):
    """A recommendation line for an account the seats do not burn, or None. Never switches anything."""
    tail = (f", resets in {sp['hours_to_reset']:.0f} h" if sp.get("hours_to_reset") is not None else "") + \
        " (switching is a seat's call; never automatic)"
    cap, why = lent_allowance(sp, rules, now)
    if cap is not None:
        if cap < 1:
            return None
        pol = rules["lent_accounts"][sp["account"]]
        h = sp.get("hours_to_reset")
        early = h is not None and h >= 168 - pol["prefer_start_of_week_h"]
        return f"spare: {sp['account']} may lend {cap:.0f}% of his week" + (" (start of his week: preferred)" if early else "") + \
            f" [{why}]" + tail
    if sp["pct_left"] >= rules["spare"]["min_pct_left"]:
        return f"spare: {sp['account']} has {sp['pct_left']:.0f}% unused" + tail
    return None


def decide(inp, state, rules, now):
    """Pure: inputs + the previous state -> the decision (mode, total, per-seat N, why) and the next state."""
    state = dict(state or {})
    tk, fit, seats = rules["token"], rules["fit"], rules["seats"]
    P = pace(inp)
    blind = inp.get("source") not in ("MEASURED", "ESTIMATE") or P is None
    why = []
    if blind:
        mode = state.get("token_mode") or "CRUISE"
        pending, since = None, state.get("since") or now
        why.append(f"meter {inp.get('source') or 'UNMEASURED'} for {inp.get('account') or 'the burn account'}: holding "
                   f"{mode}" + ("" if state.get("token_mode") else " (no history)"))
    else:
        mode, pending, since = _token(inp, state, rules, now, P)
        h = inp["hours_to_week_reset"]
        why.append(f"{inp['account']} {inp['week_pct_left']:.0f}% left, {h / 24:.2f} d to reset -> P {P:.2f}"
                   + (" (ESTIMATE)" if inp.get("source") == "ESTIMATE" else ""))
        if pending:
            why.append(f"{pending['to']} line crossed {(now - pending['since']) / 60:.0f} min ago, needs {tk['cross_hold_h']} h")
    # total N
    ceiling = tk[mode]["n"]
    prev_total = state.get("total")
    if blind:
        total = prev_total if (state.get("token_mode") and prev_total is not None) else 2
    elif mode in ("DARK", "ALMOST_OUT"):
        total = ceiling
        why.append(f"{mode}: N {ceiling}")
    else:
        rate, mh = inp.get("rate_pct_per_h"), inp.get("mean_helpers")
        if rate and mh is not None and mh >= fit["min_mean_helpers"]:
            sust = inp["week_pct_left"] / max(inp["hours_to_week_reset"], 1.0)
            raw = mh * sust / rate
            total = max(1, min(ceiling, int(math.floor(raw))))
            why.append(f"burning {rate:.2f}%/h with {mh:.1f} helpers on average; sustainable {sust:.2f}%/h "
                       f"({100 * sust / rate:.0f}% of the rate) -> fits {raw:.1f}" + (f", {mode} ceiling {ceiling}" if raw > ceiling else ""))
            if rate * inp["hours_to_week_reset"] > inp["week_pct_left"]:
                why.append(f"at this rate it runs out in {inp['week_pct_left'] / rate:.0f} h, before the reset (projected)")
            if inp.get("rate_src"):
                why.append(f"rate from {inp['rate_src']}")
        elif mode == "CRUISE":
            total = ceiling
            for lim, n in tk["CRUISE"].get("steps") or []:
                if P < lim:
                    total = n
                    break
            why.append(f"no burn rate measured: CRUISE step for P -> {total}")
        else:
            total = ceiling
            why.append(f"no burn rate measured: {mode} N {ceiling}")
        if prev_total is not None and total > prev_total + fit["raise_step"] and not state.get("_fresh_week"):
            why.append(f"raised one step from {prev_total} (at most {fit['raise_step']} per check)")
            total = prev_total + fit["raise_step"]
    total = max(0, min(total, rules["total_max"]))
    # split per seat
    share = rules["split"]["FOUNDRY_share"]
    per = {s: 0 for s in seats}
    if "FOUNDRY" in per:
        per["FOUNDRY"] = int(math.floor(total * share))
    per["BENCH"] = total - sum(v for k, v in per.items() if k != "BENCH")
    if "FOUNDRY" in per:
        why.append(f"total {total} split BENCH {per['BENCH']} / FOUNDRY {per['FOUNDRY']} (FOUNDRY {share:.0%}, rounded down)")
    presence, pwhy = _presence(inp, rules)
    if presence == "BENCH" and per["BENCH"] > rules["presence"]["bench_n"]:
        per["BENCH"] = rules["presence"]["bench_n"]
        why.append(f"{pwhy}: BENCH at most {rules['presence']['bench_n']}")
    queue_mode, qwhy = _queue(inp, state, rules)
    if queue_mode == "PAYDOWN":
        why.append(f"PAYDOWN ({qwhy}): no new art or owner-facing design, half the slots enact and close")
    label = mode
    ov = _override_live(inp.get("override"), now)
    if ov:
        if ov.get("mode") in tk:
            label = ov["mode"]
            if ov.get("n") is None and ov.get("seats") is None:
                total = tk[ov["mode"]]["n"]
                per = {s: 0 for s in seats}
                per["BENCH"] = total
        if ov.get("seats"):
            per.update({k: int(v) for k, v in ov["seats"].items()})
        elif ov.get("n") is not None:
            per["BENCH"] = int(ov["n"])
        label = f"{label}+OWNER"
        why.insert(0, f"his word: \"{ov['ownerSaid']}\"" + (f" until {ov['until']}" if ov.get("until") else ""))
    sess = inp.get("session_pct_used")
    if sess is not None and sess > tk["session_brake_pct_used_gt"]:
        per = {s: 0 for s in per}
        why.insert(0, f"5-hour window {sess:.0f}% used: no new helpers until it resets")
    for sp in inp.get("spare") or []:
        rec = spare_line(sp, rules, now)
        if rec:
            why.append(rec)
    new_state = {"token_mode": mode, "since": since, "pending": pending, "queue_mode": queue_mode,
                 "reset_at": inp.get("week_resets_at") or state.get("reset_at"), "total": sum(per.values())
                 if not (sess is not None and sess > tk["session_brake_pct_used_gt"]) else total}
    inputs = {k: v for k, v in inp.items() if k != "override"}
    inputs["P"] = None if P is None else round(P, 3)
    return {"at": iso_local(now), "t": now, "mode": label, "token_mode": mode, "queue_mode": queue_mode,
            "presence": presence, "presence_why": pwhy, "n_total": sum(per.values()), "seats": per,
            "n": per.get(inp.get("seat") or "BENCH"), "why": "; ".join(why), "inputs": inputs,
            "override": ov, "state": new_state}


def line(dec):
    s = dec["seats"]
    seats = ", ".join(f"{k} {v}" for k, v in s.items() if k != "BENCH")
    return (f"{dec['mode']} {dec['queue_mode']} {dec['presence']} N={s.get('BENCH')} BENCH"
            + (f", {seats}" if seats else "") + f" (total {dec['n_total']}) | {dec['why']}")


def compute(now=None, rules=None, seat="BENCH"):
    now = now or time.time()
    rules = rules or load_rules()
    inp = gather(now, rules)
    inp["seat"] = seat
    prev = read_json(streams_dir() / "allocation.json") or {}
    return decide(inp, prev.get("state") or {}, rules, now)


def write(dec):
    d = streams_dir()
    d.mkdir(parents=True, exist_ok=True)
    tmp = d / "allocation.json.tmp"
    tmp.write_text(json.dumps(dec, indent=1, sort_keys=True, default=str), encoding="utf-8")
    os.replace(tmp, d / "allocation.json")


def write_now(now=None):
    dec = compute(now)
    write(dec)
    return dec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("now")
    n.add_argument("--json", action="store_true")
    n.add_argument("--write", action="store_true")
    n.add_argument("--seat", default=os.environ.get("AGENT_SEAT") or "BENCH")
    s = sub.add_parser("set")
    s.add_argument("--n", type=int)
    s.add_argument("--seat")
    s.add_argument("--mode")
    s.add_argument("--owner-said", required=False)
    s.add_argument("--hours", type=float)
    sub.add_parser("clear")
    pl = sub.add_parser("plan", help="check a plan to draw PCT of an account's week against its lent rule")
    pl.add_argument("--account", required=True)
    pl.add_argument("--draw", type=float, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "plan":
        now = time.time()
        acc = (meter_now(now).get("accounts") or {}).get(a.account)
        if not acc:
            print(f"refused: no meter reading for {a.account}", file=sys.stderr)
            return 2
        sp = {"account": a.account, "pct_left": acc.get("week_pct_left"), "pct_used": acc.get("week_pct_used"),
              "hours_to_reset": acc.get("hours_to_week_reset"), "resets_at": acc.get("week_resets_at")}
        ok, why = check_plan(sp, a.draw, load_rules(), now)
        print(why, file=sys.stdout if ok else sys.stderr)
        return 0 if ok else 2
    if a.cmd == "now":
        dec = compute(seat=a.seat)
        if a.write:
            write(dec)
        print(json.dumps(dec, indent=1, sort_keys=True, default=str) if a.json else line(dec))
        return 0
    if a.cmd == "clear":
        p = streams_dir() / "slot_override.json"
        if p.exists():
            p.unlink()
        print("cleared: the allocator decides again")
        return 0
    if not (a.owner_said or "").strip():
        print("refused: set needs --owner-said with his exact words (only his word overrides the allocator)", file=sys.stderr)
        return 2
    if a.n is None and not a.mode:
        print("refused: give --n or --mode", file=sys.stderr)
        return 2
    rules = load_rules()
    if a.mode and a.mode not in rules["token"]:
        print(f"refused: mode must be one of {sorted(k for k in rules['token'] if k.isupper())}", file=sys.stderr)
        return 2
    now = time.time()
    if a.hours:
        until = iso_local(now + a.hours * HOUR)
    else:
        cur = (read_json(streams_dir() / "allocation.json") or {}).get("state", {}).get("reset_at")
        until = cur if cur and (epoch(cur) or 0) > now else iso_local(now + 24 * HOUR)
    ov = {"ownerSaid": a.owner_said.strip(), "set_at": iso_local(now), "until": until, "mode": a.mode}
    if a.n is not None:
        if a.seat:
            ov["seats"] = {a.seat: a.n}
        else:
            ov["n"] = a.n
    d = streams_dir()
    d.mkdir(parents=True, exist_ok=True)
    (d / "slot_override.json").write_text(json.dumps(ov, indent=1), encoding="utf-8")
    print(f"set: his word holds until {until}: {json.dumps(ov)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
