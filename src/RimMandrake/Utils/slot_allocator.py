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
  3. Split: FOUNDRY floor(total x share), BENCH the rest. No lower N applies because he is present (owner, 2026-10-26:
     "No, just adjust later to make up for any additional spend I incur").
  4. Overage: helper-hours run above that N (his `set` word, or interactive work) are recorded as owed in the state.
     Once his word has lapsed and he is not in a window, the allocator lowers N by ceil(owed / hours left before the
     burn account's reset, less finish_margin_h), BENCH never below bench_floor, and credits every helper-hour left unused
     until the debt is 0. A weekly reset forgives what is left.
  5. His word (`set --owner-said`) replaces any of that. The 5-hour brake (session over 90% used) is 0 for everyone,
     even over his word: the account would refuse the calls anyway.
A rule never fires on an UNMEASURED input: a blind meter holds the previous mode, or 2 helpers if there is none.
Spare accounts are named as a recommendation; this file never switches an account.

SESSION CAP (Conductor session mode, `session_week_pct_cap` in rimflow/dispatcher_schedule.json, role Conductor): the
BENCH sitting is stamped by this allocator, in allocation.json state["sitting"] = {start, start_left, last_active,
reset_at}. A sitting starts at his first typed message in the BENCH window after >= sitting_idle_h (2 h) with none (the
newest such message is read each check, so the stamp lands within one 15-min check of it); start_left is the burn
account's week_pct_left as the allocator reads it then. A change of burn account or a weekly reset mid-sitting re-bases the stamp (stamp carries account, reset_at, carried
drop, last_left): the drop already spent is banked, never a difference across two meters; unmeasured = hold. While the sitting is live
(his last BENCH message < 2 h ago) and start_left - week_pct_left >= the cap, BENCH helper allocation is 0 ("session cap
reached: X% of the week this sitting"). An unmeasured reading never allows more: BENCH holds the last measured BENCH count
(never above the computed one) and the why says UNMEASURED. His `set --owner-said` word stands over it. The Conductor
never measures tokens itself; the spawn hook reading allocation.json is what refuses.

Files (program-read, so scratch): $RM_STREAMS_DIR (default D:\\ClaudeWork\\rimmandrake\\streams) allocation.json
(the latest decision and its hysteresis state) and slot_override.json (his word). The 15-min writer is
pulse/streams.py collect (rm-pulse-streams.timer); the spawn hook is .claude/hooks/block_agent_over_slots.py.
"""
from __future__ import annotations

import argparse
import fcntl
import glob
import json
import math
import os
import sys
import tempfile
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
    assistant record ends end_turn with no tool_use pending and nothing user-side after it: finished at once, no quiet
    wait. Anything ambiguous is running until the live window passes."""
    h = rules["helpers"]
    try:
        age = now - os.path.getmtime(path)
    except OSError:
        return False, "gone"
    if age > h["live_window_s"]:
        return False, f"silent {age / 60:.0f} min (past the 600 s kill)"
    stop, user_after, pending_tool = None, False, False
    for rec in _records_backward(path, max_bytes=2 * CHUNK):
        msg = rec.get("message")
        if isinstance(msg, dict) and msg.get("role") == "assistant" and rec.get("type") == "assistant":
            stop = msg.get("stop_reason") or "none"
            c = msg.get("content")
            pending_tool = isinstance(c, list) and any(isinstance(x, dict) and x.get("type") == "tool_use" for x in c)
            break
        if rec.get("type") == "user":
            user_after = True
    if stop is None:
        return True, "no assistant record yet"
    if user_after:
        return True, "work resumed after its last answer"
    if stop == "end_turn" and not pending_tool:
        return False, "ended"
    return True, f"last record {stop}" + (" with a tool call pending" if pending_tool else "")


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


def same_reset(a, b):
    """Two reset_at readings name the same weekly reset: within RESET_TOL_S (review U F9: account_usage's series
    carries 16:00 and 15:59, 15:00 and 15:00:00 for one week). None is not comparable -> False."""
    a, b = epoch(a), epoch(b)
    return a is not None and b is not None and abs(a - b) <= RESET_TOL_S


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
        if resets_at and not same_reset(rec.get("week_resets_at"), resets_at):
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


SITTING_IDLE_H = 2.0
# review U F9: one account's reset_at jitters by about a minute between readings (series.jsonl: 16:00 x70 vs 15:59
# x5, 13:00 vs 12:59); a weekly reset moves it by days. Within this many seconds it is the same reset.
RESET_TOL_S = 600


def session_cap_pct():
    """The Conductor's session_week_pct_cap from dispatcher_schedule.json (RM_DISPATCHER_SCHEDULE overrides the path)."""
    p = Path(os.environ.get("RM_DISPATCHER_SCHEDULE") or HERE.parent / "rimflow" / "dispatcher_schedule.json")
    try:
        for r in json.loads(p.read_text(encoding="utf-8")).get("roles") or []:
            if r.get("name") == "Conductor" and isinstance(r.get("session_week_pct_cap"), (int, float)):
                return float(r["session_week_pct_cap"])
    except (OSError, ValueError):
        pass
    return None


def sitting_step(inp, state, now):
    """Pure: (sitting stamp or None, live?, drop %-points or None, measured?) from inputs and the previous stamp.
    A reset_at within RESET_TOL_S of the stamp's is the same reset (jitter, review U F9). Across a real weekly reset
    the drop already measured is carried into the new week: conservative, it over-counts the sitting (review U N8)."""
    sit = dict(state.get("sitting") or {}) or None
    w = inp.get("owner_window_t")
    measured = inp.get("source") == "MEASURED" and isinstance(inp.get("week_pct_left"), (int, float))
    left = inp.get("week_pct_left") if measured else None
    reset = epoch(inp.get("week_resets_at"))
    acct = inp.get("account")
    if w is not None:
        if sit is None or w - (sit.get("last_active") or 0) > SITTING_IDLE_H * HOUR:
            sit = {"start": w, "start_left": left, "last_active": w, "reset_at": inp.get("week_resets_at"),
                   "account": acct, "carried": 0.0, "last_left": left}
        else:
            sit["last_active"] = max(sit.get("last_active") or 0, w)
    if sit is None:
        return None, False, None, measured
    # F9: a different burn account or a new weekly reset mid-sitting makes start_left a reading of another meter.
    # Re-base: bank the drop already spent on the old meter, start counting from the new one. Only on a measured
    # reading; until then the drop is unknown (hold), never zero.
    sit.setdefault("carried", 0.0)
    old_acct, old_reset = sit.get("account"), epoch(sit.get("reset_at"))
    changed = bool((acct and old_acct and acct != old_acct)
                   or (reset and old_reset and not same_reset(reset, old_reset)))
    if not changed and sit.get("start_left") is None and left is not None:
        # first reading of the SAME meter the sitting began on: the base. On another meter it is not (the old
        # meter's spend was never measured), so it is left for the re-base below to hold as unknown.
        sit["start_left"] = left
        sit.setdefault("last_left", left)
    if changed and left is not None:
        if sit.get("start_left") is None or sit.get("carried") is None:
            sit["carried"] = None  # the old meter's spend was never measured: unknown, held
        elif sit.get("last_left") is not None:
            sit["carried"] = float(sit["carried"]) + max(0.0, sit["start_left"] - sit["last_left"])
        # else: a legacy stamp with no last_left: a fresh base, carried as it was (review U F9, LOW)
        sit["start_left"], sit["account"], sit["reset_at"] = left, acct, inp.get("week_resets_at")
    elif not changed:
        if acct and not old_acct:
            sit["account"] = acct
        if reset and not old_reset:
            sit["reset_at"] = inp.get("week_resets_at")
    if left is not None:
        sit["last_left"] = left
    live = now - (sit.get("last_active") or 0) <= SITTING_IDLE_H * HOUR
    if changed and left is None:
        drop = None
    elif left is None or sit.get("start_left") is None or sit.get("carried", 0.0) is None:
        drop = None
    else:
        drop = sit.get("carried", 0.0) + sit["start_left"] - left
    return sit, live, drop, measured


def read_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def ops_dir() -> Path:
    return Path(os.environ.get("RM_OPS_WATCH_DIR", "/mnt/d/ClaudeWork/rimmandrake/ops_watch"))


def _finite(v):
    """A real finite number as float, else None (bools, strings, NaN, inf and ints too big for a float all fail)."""
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return None
    try:
        f = float(v)
    except (OverflowError, ValueError):
        return None
    return f if math.isfinite(f) else None


def ops_inputs(now, rules):
    """The ops watch's last pass (ops_watch.py status.json), cut to what the allocator acts on. A point counts only
    when MEASURED; a status older than ops.stale_min is reported and ignored (no brake from an old reading)."""
    o = rules.get("ops") or {}
    st = read_json(ops_dir() / "status.json")
    t = st.get("t") if isinstance(st, dict) else None
    t = _finite(t)
    if t is None:
        return {"ok": False, "why": f"no ops watch status with a time ({ops_dir() / 'status.json'})"}
    age = (now - t) / 60.0
    if age < -5:
        return {"ok": False, "why": f"ops watch status is stamped {-age:.0f} min in the future (clock skew?)",
                "age_min": round(age, 1)}
    if not age <= o.get("stale_min", 45):
        return {"ok": False, "why": f"ops watch status is {age:.0f} min old (rm-ops-watch.timer stopped?)",
                "age_min": round(age, 1)}
    pts = st.get("points") or {}

    pts = pts if isinstance(pts, dict) else {}

    def mv(k, marks=("MEASURED",), numeric=True):
        # a malformed point is ignored, never a crash in decide() and never a brake
        p = pts.get(k)
        if not isinstance(p, dict) or p.get("m") not in marks:
            return None
        v = p.get("v")
        if not numeric:
            return v if isinstance(v, str) else None
        return _finite(v)
    return {"ok": True, "age_min": round(age, 1), "root_free_gb": mv("disk.root_free_gb"),
            "codex_runway": mv("codex.runway", ("MEASURED", "ESTIMATE")), "steve_state": mv("steve.state", numeric=False),
            "steve_unowned_stall_min": mv("steve.unowned_stall_min"), "steve_invalid_streak": mv("steve.invalid_streak"),
            "alarms_open": sorted(k for k, a in (st.get("alarms") if isinstance(st.get("alarms"), dict) else {}).items()
                                  if isinstance(a, dict) and a.get("state") in ("OPEN", "PENDING"))}


def _ops(inp, rules, total, why):
    """-> (total, advice). The disk brake caps the total (applied before the owner's word, which still wins);
    Codex and the Steve lane are advice lines only: this allocator places Claude helpers, not Codex or testq work."""
    o = rules.get("ops") or {}
    ops = inp.get("ops")
    adv = {"disk": "UNMEASURED", "codex": "UNMEASURED", "steve_lane": "UNMEASURED"}
    if not ops:
        return total, adv
    if not ops.get("ok"):
        why.append("ops watch: " + ops.get("why", "unreadable") + " -- no disk brake, no Codex/Steve advice")
        return total, adv
    free = ops.get("root_free_gb")
    if free is not None:
        adv["disk"] = "OK"
        if free < o["disk_brake_free_gb"]:
            adv["disk"] = "BRAKE"
            if total > o["disk_brake_total"]:
                why.append(f"disk brake: {free:.0f} GB free on / (< {o['disk_brake_free_gb']} GB, the DISK_LOW line) "
                           f"-> total {total} capped at {o['disk_brake_total']}")
                total = o["disk_brake_total"]
            else:
                why.append(f"disk brake: {free:.0f} GB free on / (< {o['disk_brake_free_gb']} GB); total already "
                           f"{total}")
    cx = ops.get("codex_runway")
    if cx is not None:
        adv["codex"] = "CONSERVE" if cx < o["codex_conserve_runway"] else "OK"
        if adv["codex"] == "CONSERVE":
            why.append(f"Codex runway {cx:.2f} (< {o['codex_conserve_runway']}): send GPT/Codex consults only where "
                       f"a review is required")
    stall, inv = ops.get("steve_unowned_stall_min"), ops.get("steve_invalid_streak")
    if stall is not None or inv is not None:
        adv["steve_lane"] = "OK"
        if (stall or 0) > o["steve_stall_min"]:
            adv["steve_lane"] = "STALLED"
        elif (inv or 0) >= o["steve_invalid_streak"]:
            adv["steve_lane"] = "INVALID_STREAK"
        if adv["steve_lane"] != "OK":
            why.append(f"Steve lane {adv['steve_lane']} (stall {stall} min, INVALID streak {inv}): do not start a "
                       f"helper whose item waits on a testq run")
    return total, adv


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
            if (name == acc or o.get("week_pct_left") is None or o.get("stale")
                    or o.get("source") not in ("MEASURED", "ESTIMATE")):
                continue  # a stale poll (account_usage keeps source MEASURED, flags stale) offers nothing
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
    # an unreadable transcript directory is "unavailable" (None), never a measured zero helpers
    inp["helpers_running"] = {s: (len(running_helpers([p], now, rules)) if os.path.isdir(p) and os.access(p, os.R_OK | os.X_OK)
                                  else None) for s, p in seat_paths.items()}
    w = owner_last_window(list(seat_paths.values()), now)
    inp["owner_window_min"] = None if w is None else round((now - w) / 60, 1)
    bw = owner_last_window([seat_paths["BENCH"]], now, SITTING_IDLE_H * HOUR * 3) if "BENCH" in seat_paths else None
    inp["owner_window_t"] = bw
    inp["session_cap_pct"] = session_cap_pct()
    c = owner_last_card(owner_ledger(), now)
    inp["owner_card_min"] = None if c is None else round((now - c) / 60, 1)
    inp["A1"], inp["D1"] = latest_streams(now)
    ov = read_json(streams_dir() / "slot_override.json")
    inp["override"] = ov if isinstance(ov, dict) else None
    try:
        inp["ops"] = ops_inputs(now, rules)
    except Exception as e:  # noqa: BLE001
        inp["ops"] = {"ok": False, "why": f"{type(e).__name__}: {e}"}
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
                         and not same_reset(epoch(state["reset_at"]), epoch(inp["week_resets_at"])))  # jitter: same reset
    if reset_changed:
        prev, pending = None, None
    if used is not None and used >= tk["DARK"]["enter_pct_used_ge"]:
        return "DARK", None, since if prev == "DARK" else now
    burn_line = (measured and P > tk["BURN"]["enter_p_gt"] and h is not None and h < tk["BURN"]["enter_reset_h_lt"]
                 and h >= tk["BURN"]["leave_reset_h_lt"])  # never enter BURN already inside its own exit window
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
        if P < tk["ALMOST_OUT"]["enter_p_lt"]:
            return "ALMOST_OUT", None, now
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
        if state.get("queue_mode") == "PAYDOWN":
            return "PAYDOWN", "queues unmeasured (no streams record in 2 h): holding PAYDOWN, no leave line observed"
        return "UNMEASURED", "queues unmeasured (no streams record in 2 h)"
    enter = (a1 is not None and a1 > q["paydown_enter"]["A1_gt"]) or (d1 is not None and d1 >= q["paydown_enter"]["D1_ge"])
    if enter:
        return "PAYDOWN", f"A1 {a1}, D1 {d1} over 3 d"
    if state.get("queue_mode") == "PAYDOWN":
        # leaving PAYDOWN needs both counts seen under their lines: an unmeasured count holds it
        leave = (a1 is not None and a1 < q["paydown_leave"]["A1_lt"]) and (d1 is not None and d1 < q["paydown_leave"]["D1_lt"])
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


def _overage(inp, state, rules, now, base, per, ov, presence, why):
    """Record helper-hours run above the computed N (base) as owed; once his word has lapsed and he has left, lower `per`
    in place so the debt is repaid before the burn account's reset. Returns the record shown on the Pacing tile."""
    cfg = rules["overage"]
    owed = float(state.get("overage_h") or 0.0)
    last = state.get("overage_t")
    dt = 0.0 if last is None else max(0.0, min(now - float(last), cfg["max_accrual_dt_h"] * HOUR)) / HOUR
    forgiven = 0.0
    prev_reset, new_reset = epoch(state.get("reset_at")), epoch(inp.get("week_resets_at"))
    if owed > 0 and prev_reset is not None and prev_reset <= now and new_reset is not None and new_reset > prev_reset:
        forgiven, owed = owed, 0.0
        why.append(f"weekly reset: {forgiven:.1f} helper-h of overage forgiven")
    run = inp.get("helpers_running")
    run = run if isinstance(run, dict) else {}
    blind = sorted(s for s, v in run.items() if v is None)
    if blind:
        why.append(f"helper count unavailable for {', '.join(blind)}: no overage credited this check")
    over = sum(max(0, run[s] - base.get(s, 0)) for s in run if run[s] is not None)
    under = sum(max(0, base.get(s, 0) - run.get(s, 0)) for s in base) if run and not blind else 0
    paying = ov is None and presence != "BENCH"
    owed += over * dt
    credited = 0.0
    if paying and owed > 0:
        credited = min(owed, under * dt)
        owed -= credited
    owed = round(max(0.0, owed), 4)
    rec = {"owed_h": owed, "paying": bool(paying and owed > 0), "cut": 0, "accrued_h": round(over * dt, 4),
           "credited_h": round(credited, 4), "forgiven_h": round(forgiven, 4), "deadline_h": None, "eta_h": None, "plan": ""}
    if owed <= 0:
        return rec
    h = inp.get("hours_to_week_reset")
    window = max((h - cfg["finish_margin_h"]) if h is not None else cfg["default_window_h"], cfg["min_window_h"])
    rec["deadline_h"] = round(window, 2)
    if not paying:
        rec["plan"] = (f"owes {owed:.1f} helper-h; payback starts when " + ("his word lapses" if ov else "he leaves the window")
                       + f", to finish within {window:.0f} h (before the reset)")
        why.append(rec["plan"])
        return rec
    want = int(math.ceil(owed / window))
    cut = 0
    for seat, floor in (("BENCH", cfg["bench_floor"]), ("FOUNDRY", 0)):
        if seat in per and cut < want:
            take = min(want - cut, max(0, per[seat] - floor))
            per[seat] -= take
            cut += take
    rec["cut"] = cut
    rec["eta_h"] = round(owed / cut, 1) if cut else None
    short = cut < want
    rec["plan"] = (f"owes {owed:.1f} helper-h: N lowered by {cut} (wanted {want}) for about "
                   + (f"{rec['eta_h']:.0f} h" if cut else "?") + f", due within {window:.0f} h"
                   + ("; the floor stops it short, the rest is forgiven at the reset" if short else ""))
    why.append(rec["plan"])
    return rec


def _lent_view(sp):
    used = sp.get("pct_used")
    if used is None and sp.get("pct_left") is not None:
        used = 100.0 - sp["pct_left"]
    return used, sp.get("pct_left"), sp.get("hours_to_reset"), sp.get("resets_at")


def lent_allowance(sp, rules, now):
    """(max % of his week we may still draw now, why) for an account under lent_accounts, or (None, '') if none.
    The owner's rule for a lent account (2026-10-27): only in the first prefer_start_of_week_h after his weekly reset,
    at most max_used_by_us_pct of the week used (all of it counted as ours), never under the floor; 0 otherwise;
    off-limits through off_limits_through."""
    pol = (rules.get("lent_accounts") or {}).get(sp.get("account"))
    if not pol:
        return None, ""
    used, left, h, _ = _lent_view(sp)
    name = sp["account"]
    if left is None or used is None or h is None or sp.get("source", "MEASURED") not in ("MEASURED", "ESTIMATE"):
        return 0.0, f"{name}: lent account unmeasured, left alone"
    off = epoch(pol.get("off_limits_through"))
    if off is not None and now < off:
        return 0.0, f"{name}: off-limits until {pol['off_limits_through']} (his rule: this week's share is already used)"
    by_floor = left - pol["floor_pct_left"]
    if h < 168 - pol["prefer_start_of_week_h"]:
        return 0.0, (f"{name}: {h:.0f} h to his reset, outside the {pol['prefer_start_of_week_h']} h after it "
                     "(owner 2026-10-27: his account only right after a fresh reset)")
    cap = min(by_floor, pol["max_used_by_us_pct"] - used)
    where = (f"fresh reset (first {pol['prefer_start_of_week_h']} h): up to {pol['max_used_by_us_pct']}% of his week used "
             f"(counting all {used:.0f}% as ours), floor {pol['floor_pct_left']}%")
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
        return f"spare: {sp['account']} may lend {cap:.0f}% of his week (fresh reset)" + \
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
        used = inp.get("week_pct_used")
        if inp.get("source") == "MEASURED" and isinstance(used, (int, float)) and used >= tk["DARK"]["enter_pct_used_ge"]:
            # no pace (reset time unknown), but a measured near-empty week is DARK whatever the pace
            mode, since = "DARK", (since if state.get("token_mode") == "DARK" else now)
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
        # blind: hold the last total, but never above this mode's ceiling (a held total may come from an
        # owner override that has since expired)
        total = min(prev_total, ceiling) if (state.get("token_mode") and prev_total is not None) else min(2, ceiling)
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
    total, ops_advice = _ops(inp, rules, total, why)
    # split per seat
    share = rules["split"]["FOUNDRY_share"]
    per = split_total(total, seats, share)
    if "FOUNDRY" in per:
        why.append(f"total {total} split BENCH {per['BENCH']} / FOUNDRY {per['FOUNDRY']} (FOUNDRY {share:.0%}, rounded down)")
    presence, pwhy = _presence(inp, rules)
    queue_mode, qwhy = _queue(inp, state, rules)
    if queue_mode == "PAYDOWN":
        why.append(f"PAYDOWN ({qwhy}): no new art or owner-facing design, half the slots enact and close")
    label = mode
    base = dict(per)
    ov = _override_live(inp.get("override"), now)
    if ov:
        if isinstance(ov.get("mode"), str) and isinstance(tk.get(ov["mode"]), dict) and "n" in tk[ov["mode"]]:
            label = ov["mode"]
            if ov.get("n") is None and ov.get("seats") is None:
                total = tk[ov["mode"]]["n"]
                per = split_total(total, seats, share)
        if isinstance(ov.get("seats"), dict) and ov["seats"]:
            # a seat key we do not place (e.g. "bench") is folded to its seat, never added beside it
            per.update({str(k).upper(): int(v) for k, v in ov["seats"].items() if str(k).upper() in per})
        elif ov.get("n") is not None:
            per["BENCH"] = int(ov["n"])
        label = f"{label}+OWNER"
        why.insert(0, f"his word: \"{ov['ownerSaid']}\"" + (f" until {ov['until']}" if ov.get("until") else ""))
        if ops_advice["disk"] == "BRAKE":
            why.append("his word stands over the disk brake")
    pre_cut_total = sum(per.values())
    overage = _overage(inp, state, rules, now, base, per, ov, presence, why)
    sess = inp.get("session_pct_used")
    if sess is not None and inp.get("source") != "MEASURED":
        # a stale or estimated 5-hour reading may predate the window's reset: it brakes nothing
        why.append(f"5-hour window {sess:.0f}% used per a {inp.get('source') or 'UNMEASURED'} reading: not braking on it")
        sess = None
    if sess is not None and sess > tk["session_brake_pct_used_gt"]:
        per = {s: 0 for s in per}
        why.insert(0, f"5-hour window {sess:.0f}% used: no new helpers until it resets")
    sit, live, drop, _m = sitting_step(inp, state, now)
    cap = inp.get("session_cap_pct")
    held_n = state.get("bench_n")
    # his word stands over the cap only where it speaks for BENCH: a FOUNDRY-only override leaves BENCH's cap in force
    ov_bench = bool(ov) and not (isinstance(ov.get("seats"), dict) and ov["seats"]
                                 and "BENCH" not in {str(k).upper() for k in ov["seats"]})
    if cap is not None and live and "BENCH" in per and not ov_bench:
        if drop is not None and drop >= cap:
            per["BENCH"] = 0
            why.insert(0, f"session cap reached: {drop:.1f}% of the week this sitting (cap {cap:g}%, started at "
                          f"{sit['start_left']:.1f}% left)")
        elif drop is None:
            if held_n is not None:
                per["BENCH"] = min(per["BENCH"], int(held_n))
            why.insert(0, f"session cap UNMEASURED: no usable week reading for this sitting (cap {cap:g}%); BENCH held at "
                          f"{per['BENCH']}")
        else:
            why.append(f"sitting used {max(drop, 0):.1f}% of the week (cap {cap:g}%)")
    for sp in inp.get("spare") or []:
        rec = spare_line(sp, rules, now)
        if rec:
            why.append(rec)
    new_state = {"token_mode": mode, "since": since, "pending": pending, "queue_mode": queue_mode,
                 # a blind reading's reset_at is not adopted: the reset it names was never applied to the dial
                 "reset_at": (None if blind else inp.get("week_resets_at")) or state.get("reset_at"),
                 "overage_h": overage["owed_h"],
                 "overage_t": now, "sitting": sit,
                 "bench_n": (held_n if (cap is not None and live and drop is None and held_n is not None) else per.get("BENCH")),
                 "total": pre_cut_total
                 if not (sess is not None and sess > tk["session_brake_pct_used_gt"]) else total}
    inputs = {k: v for k, v in inp.items() if k != "override"}
    inputs["P"] = None if P is None else round(P, 3)
    return {"at": iso_local(now), "t": now, "mode": label, "token_mode": mode, "queue_mode": queue_mode,
            "presence": presence, "presence_why": pwhy, "n_total": sum(per.values()), "seats": per,
            "n": per.get(inp.get("seat") or "BENCH"), "why": "; ".join(why), "inputs": inputs,
            "overage": overage, "override": ov, "ops": ops_advice, "state": new_state}


def split_total(total, seats, share):
    """Total helpers -> per seat: FOUNDRY gets floor(total * share), BENCH the rest."""
    per = {s: 0 for s in seats}
    if "FOUNDRY" in per:
        per["FOUNDRY"] = int(math.floor(total * share))
    per["BENCH"] = total - sum(v for k, v in per.items() if k != "BENCH")
    return per


def override_until(hours, persisted_reset, meter_reset, now):
    """(until, error) for `set`: --hours, else the burn account's reset (persisted allocation, else the meter now).
    No reset known is an error, never a silent 24 h."""
    if hours:
        return iso_local(now + hours * HOUR), None
    for r in (persisted_reset, meter_reset):
        if r and (epoch(r) or 0) > now:
            return r, None
    return None, "the burn account's weekly reset is unavailable (no allocation record, meter gave none): pass --hours"


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
    """Publish dec as allocation.json unless a decision computed later is already there (the 15-min tick and a
    manual `now --write` may overlap: the slower one gathered the older reading). False when skipped."""
    d = streams_dir()
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "allocation.json.lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        cur = read_json(d / "allocation.json") or {}
        if isinstance(cur.get("t"), (int, float)) and isinstance(dec.get("t"), (int, float)) and cur["t"] > dec["t"]:
            return False
        write_atomic(d / "allocation.json", json.dumps(dec, indent=1, sort_keys=True, default=str))
    return True


def write_atomic(path, text):
    """Publish text at path by replace: a reader never sees it empty or half-written. One temp file per writer:
    the scheduled tick and a manual `now --write` may overlap; a shared temp name let one publish the other's
    decision and the other crash on a vanished file."""
    path = Path(path)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


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
              "hours_to_reset": acc.get("hours_to_week_reset"), "resets_at": acc.get("week_resets_at"),
              "source": "STALE" if acc.get("stale") else acc.get("source")}
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
    if a.seat and a.n is None:
        print("refused: --seat needs --n (a mode sets every seat; say the seat's count)", file=sys.stderr)
        return 2
    rules = load_rules()
    if a.mode and not (isinstance(rules["token"].get(a.mode), dict) and "n" in rules["token"][a.mode]):
        print(f"refused: mode must be one of {sorted(k for k in rules['token'] if k.isupper())}", file=sys.stderr)
        return 2
    now = time.time()
    if a.hours:
        until = iso_local(now + a.hours * HOUR)
    else:
        cur = ((read_json(streams_dir() / "allocation.json") or {}).get("state") or {}).get("reset_at")
        mr = None
        if not (cur and (epoch(cur) or 0) > now):
            mr = gather(now, rules).get("week_resets_at")
        until, err = override_until(None, cur, mr, now)
        if err:
            print("refused: " + err, file=sys.stderr)
            return 2
    ov = {"ownerSaid": a.owner_said.strip(), "set_at": iso_local(now), "until": until, "mode": a.mode}
    if a.n is not None:
        if a.seat:
            if a.seat.upper() not in rules["seats"]:
                print(f"refused: seat must be one of {rules['seats']}", file=sys.stderr)
                return 2
            ov["seats"] = {a.seat.upper(): a.n}
        else:
            ov["n"] = a.n
    d = streams_dir()
    d.mkdir(parents=True, exist_ok=True)
    write_atomic(d / "slot_override.json", json.dumps(ov, indent=1))  # a collector never reads it half-written
    print(f"set: his word holds until {until}: {json.dumps(ov)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
