#!/usr/bin/env python3
"""ops_watch: the Dispatcher's deterministic measurement arm for Operations (V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE).

The owner, 2026-10-26: "I am most eager to have a competent agent appearing to check the spend of all the accounts
including CODEX, SteveDesktop's operation... monitor the disk." and (ledger 2026-10-27T05:59:41Z) Operations "should
just have those things automatically gathered for it, so it's not constantly burning tokens gathering it all up for
every question considered." So this program, with no AI, as the metronome's sense phase, listed in
rimflow/dispatcher_schedule.json "measure":

  GATHER   one record per metric family, reusing the instruments that already exist:
             accounts    account_usage.read_now() + slot_allocator.slope(): week % left, hours to reset, runway;
                         and the fleet's (fleet_readings): its summed burn, the hours until the switching plan has no
                         account for it (fleet_stop_h), each account's runway were the fleet moved there (moved_runway)
             codex       sim/csuite_codex_limits.readings(): the weekly window's used %, reset, runway
             steve       testq steward.json / steward_watch.json / done/*.json: state, fault, heartbeat, INVALID streak;
                         idle_with_takeable_min (the lane idle or on filler while in-game visit checks with a testq
                         block wait: the dispatch reading's ingame_testq block + running/ + pending/); a filing pass also runs testq/brake_release.py, which ACTS: one canary job on a known-cause brake
             testing     testq done jobs (Steve lane, per job) + testing_metrics history (archmagi, per day):
                         busy hours on runs that caught nothing (no FAIL, no finding, no close within 24 h)
             disk        free GB on / (WSL ext4), C:, D:; D: used GB (agent storage growth); scratch under the reaper
                         (the last line of rm-scratch-reap's runs.jsonl, written hourly: no 160 s dry run here)
                         clones outside the pool cap (scratch_outside: the reaper's sanity record, read only)
             timers      systemctl --user: failed units, timers overdue
             flow        the rimflow ledger (the dispatch clone's local origin/main): untriaged findings,
                         closes and verify passes in 24 h, lapsed leases
             process     process-commit share (git log, the resp_register PROC regex) over 24 h and 7 d
             tps         tps_record.py --json: tick ratio, stalls, coverage
             production  every stream measure (rm-streams-collect's series.jsonl, reused, not recomputed)
             v3          the section 6 success metrics no instrument measures yet, UNMEASURED with the reason
             seats       idle_with_work_min: how long a seat has sat idle through rings it did not answer with work, from
                         the Dispatcher's journal.jsonl and state.json (OP2); blind when either is missing or frozen
             roles       RO1, report-only: roles.<role>.acted_share, runs, silent_days, weeks_under, from the ledger
                         (role_use.py); class under rings nothing and lint refuses anything that would
   STORE   append-only JSONL, one file per family: $RM_OPS_WATCH_DIR/series/<family>.jsonl (default
           D:\\ClaudeWork\\rimmandrake\\ops_watch). Every point is {v, m: MEASURED|ESTIMATE|UNMEASURED, why?, unit?}.
           An instrument that errors writes UNMEASURED with the error, never 0.
   RANGES  the rules' ranges block (OP1): each metric's idle, sane, distressed, emergency classes with owner, ack_within_min
           and max_age_min. The seats verdict reads it; each reading carries its class. `lint` refuses a
           metric short of any of these, and so does load_rules, which then keeps the last good copy and flags it.
   FLAG    Andon rules from ops_watch_rules.json over MEASURED points: band (outside the 7-day mean +/- 3 sigma),
           run (n same-direction changes), silent (a series that stopped being MEASURED), target (a line crossed).
           Each flag names the series and the window. flags.json keeps when each flag first opened.
   WORSE   an alarm still crossed re-raises when its severity rises or its value passes the target's stated `worse` step
           ({"factor": 2} doubling, {"add": 50}), measured from the worst value told (ALARM_REPEAT_FIX_BREAK_ON_WORSE).
   ALARM   a target with alarm true files ONE rimflow item when its condition is NEW (alarms.json dedupes; it re-arms
           only after the condition clears; a failed filing stays PENDING and is retried next pass). Filed as RUNNER
           from the dispatch clone (its testq/ingest.py) under QHOME/ingest.lock. Only with --file-alarms.
   HAND    status.json (every current point: slot_allocator.py reads it), digest.json and digest.md: per KPI the
   OVER    current value, its mark, the change over 24 h and 7 d, and its open flags; one cheap read for Operations.
           digest_blind.md: an ALLOW-LIST (BLIND_KEYS: machine health, disk, stalls, flow, production output
           counts) and only their alarms and flags; everything else is withheld by default, and any line holding a
           token_talk term is dropped too: the only digest the token-blind roles read (review U N2, review V V1).
           Account and runway alarms (TOKEN_FAMILIES) are Operations': kept in alarms.json, never filed as items.

    python3 src/RimMandrake/Utils/ops_watch.py run [--file-alarms]   one pass (the timer passes --file-alarms)
           a --family pass without --compose is a sample: refused on the live store and refused --file-alarms
    python3 src/RimMandrake/Utils/ops_watch.py digest                 print digest.md
    python3 src/RimMandrake/Utils/ops_watch.py backfill               seed production from rm-streams-collect' history
"""
import argparse
import calendar
import fnmatch
import glob
import importlib.util
import inspect
import contextlib
import json
import math
import os
os.environ.setdefault("RIMFLOW_MACHINE_MINT", "1")  # machine minter: fixed alarm prefixes, see rimflow/model.py mint_problems
import re
import shlex
import shutil
import signal
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _p in (HERE, HERE / "ops_core", HERE / "sim"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

SCHEMA = "rm.ops_watch/1"
HOUR = 3600.0
DAY = 24 * HOUR
# families whose collector was removed: their old keys never read as silent and their alarms leave (relentless: the retired
# tick's belt, 2026-11-18; plan: the retired Producer's daily list, 2026-11-23)
REMOVED_FAMILIES = ("relentless", "plan", "health")
FAMILIES = ("accounts", "codex", "steve", "testing", "disk", "timers", "flow", "process", "tps", "production", "v3", "tokentalk",
            "evidence", "companion", "seats", "roles", "queues", "wrapup", "maturation", "pager")


LIVE_OPS_DIR = "/mnt/d/ClaudeWork/rimmandrake/ops_watch"


def ops_dir() -> Path:
    return Path(os.environ.get("RM_OPS_WATCH_DIR", LIVE_OPS_DIR))


def live_store() -> bool:
    """Whether ops_dir() is the store the allocator, the Dispatcher and the alarms read (RM_OPS_WATCH_LIVE_DIR names
    it, default LIVE_OPS_DIR; a selftest points it at its own dir to prove the refusal)."""
    live = os.environ.get("RM_OPS_WATCH_LIVE_DIR", LIVE_OPS_DIR)
    try:
        return ops_dir().resolve() == Path(live).resolve()
    except OSError:
        return True     # cannot tell: treat it as live, so a partial pass refuses rather than eats the slot


class PartialPass(RuntimeError):
    """A limited (--family, no --compose) pass asked to write where the live readers look, or to file real alarms.
    Its status.json held only its own families, so role_launch refused a scheduled slot, and its fixture readings
    filed two false scratch alarms (STATUS_FIX_HALF_PASS_ATE_THE_SLOT). Only the metronome's compose pass is whole."""


def rules_path() -> Path:
    return Path(os.environ.get("RM_OPS_WATCH_RULES", HERE / "ops_watch_rules.json"))


def qhome() -> Path:
    return Path(os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq"))


def data_clone() -> Path:
    return Path(os.environ.get("RM_STREAMS_BENCH", "/home/mandrake/rm/bench"))


def nonfinite_at(x, at="rules"):
    """-> the path of the first nonfinite number in a parsed JSON value, or None."""
    if isinstance(x, dict):
        return next(filter(None, (nonfinite_at(v, "%s.%s" % (at, k)) for k, v in x.items())), None)
    if isinstance(x, list):
        return next(filter(None, (nonfinite_at(v, "%s[%d]" % (at, i)) for i, v in enumerate(x))), None)
    return at if isinstance(x, float) and not finite(x) else None


CLASSES = ("idle", "sane", "under", "distressed", "emergency")     # OP1's vocabulary; a metric fills the ones it can act on
ALARMED = ("distressed", "emergency")
SEVERITY = ("idle", "sane", "distressed", "emergency")      # the ranges classes, least to worst
REPORT_ONLY = "roles."      # RO1: these metrics are read, never rung: only they may read under, and none may alarm


def ranges_of(rules) -> dict:
    """The metrics of the ranges block, {} when there is none."""
    r = rules.get("ranges")
    return {k: v for k, v in r.items() if not k.startswith("_")} if isinstance(r, dict) else {}


def is_limit(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def metric_problem(key, m, metrics):
    """-> what is wrong with one metric of the ranges block, or None. Numeric classes are lower bounds, so they cannot
    gap or overlap; the lowest must be 0 or a reading could fall outside every class."""
    if not isinstance(m, dict):
        return "%s is not an object" % key
    if not isinstance(m.get("owner"), str) or not m["owner"].strip():
        return "%s has no owner" % key
    if not isinstance(m.get("why"), str) or not m["why"].strip():
        return "%s names no why" % key
    if not is_limit(m.get("max_age_min")) or m["max_age_min"] <= 0:
        return "%s has no max_age_min" % key
    cl = m.get("classes")
    if not isinstance(cl, dict) or not cl:
        return "%s fills no class" % key
    odd = sorted(set(cl) - set(CLASSES))
    if odd:
        return "%s fills unknown classes %s" % (key, odd)
    if key.startswith(REPORT_ONLY) and any(c in cl for c in ALARMED):
        return "%s is report-only (RO1) and may not fill distressed or emergency" % key
    if "under" in cl and not key.startswith(REPORT_ONLY):
        return "%s: under is the report-only class of %s*: this reading would ring nobody" % (key, REPORT_ONLY)
    if any(c in cl for c in ALARMED) and (not is_limit(m.get("ack_within_min")) or m["ack_within_min"] <= 0):
        return "%s can read distressed or emergency and has no ack_within_min" % key
    specs = list(cl.values())
    if not all(isinstance(c, dict) and len(c) == 1 for c in specs):
        return "%s: a class is one of at_least, in, otherwise" % key
    if all("at_least" in c for c in specs):
        bounds = [c["at_least"] for c in specs]
        if not all(is_limit(b) for b in bounds) or len(set(bounds)) != len(bounds):
            return "%s: bounds are numbers and differ: %s" % (key, bounds)
        if min(bounds) != 0:
            return "%s: the lowest class starts at %s, not 0: a reading could fit no class" % (key, min(bounds))
    else:
        rest = [c for c in specs if c.get("otherwise") is True]
        lists = [c.get("in") for c in specs if "otherwise" not in c]
        if len(rest) != 1 or not all(isinstance(x, list) and x and all(isinstance(t, str) for t in x) for x in lists):
            return "%s: text classes are in-lists and exactly one otherwise" % key
    gates = m.get("idle_if") or []
    if not isinstance(gates, list) or not all(isinstance(g, str) for g in gates):
        return "%s: idle_if is a list of metric names" % key     # refused here, so load_rules keeps the last good copy
    for g in gates:
        gate = metrics.get(g)
        if not isinstance(gate, dict) or "idle" not in (gate.get("classes") or {}) or gate.get("idle_if"):
            return "%s: idle_if %s must name a metric that fills idle and has no idle_if of its own" % (key, g)
        if g.split(".", 1)[0] != key.split(".", 1)[0]:
            # stamp_ranges runs per family on that family's points alone: a gate from another family is never there,
            # so the metric would never be classed (and a verdict built on its class would skip it)
            return "%s: idle_if %s is another family's metric; a gate must share its family" % (key, g)
    return None


def ranges_problems(rules):
    """-> what `lint` and load_rules refuse: no ranges block, or any metric short of an owner, class, age or why."""
    r = rules.get("ranges")
    if not isinstance(r, dict):
        return ["no ranges block"]
    ms = ranges_of(rules)
    ro = [k for k in ms if k.startswith(REPORT_ONLY)] + [REPORT_ONLY + "x.y"]   # every real report-only key, and one unborn
    gating = sorted(str(t.get("key")) for t in rules.get("targets") or [] if isinstance(t, dict)
                    and (str(t.get("key")).startswith(REPORT_ONLY) or any(fnmatch.fnmatchcase(k, str(t.get("key"))) for k in ro)))
    if gating:
        return ["a target on a report-only metric (RO1): %s" % ", ".join(gating)]
    return [p for p in (metric_problem(k, ms[k], ms) for k in sorted(ms)) if p] or ([] if ms else ["the ranges block is empty"])


def base_class(m, v):
    """The class a reading falls in by value alone, None when it fits none."""
    cl = m["classes"]
    if isinstance(v, str):
        hit = [c for c, s in cl.items() if v in (s.get("in") or [])]
        return hit[0] if hit else next((c for c, s in cl.items() if s.get("otherwise")), None)
    if not is_num(v):
        return None
    fit = [(s["at_least"], c) for c, s in cl.items() if "at_least" in s and v >= s["at_least"]]
    return max(fit)[1] if fit else None


def read_class(ms, key, points):
    """The class of points[key] under the ranges metrics `ms`, or None: a reading not MEASURED has no class, and a
    gate not MEASURED leaves it unjudged, so nothing reads sane or idle on what was not seen."""
    p, m = points.get(key), ms.get(key)
    if not isinstance(p, dict) or not isinstance(m, dict) or p.get("m") != "MEASURED":
        return None
    gates = [read_class({g: ms.get(g)}, g, points) for g in m.get("idle_if") or []]
    return "idle" if "idle" in gates else None if None in gates else base_class(m, p.get("v"))


def stamp_ranges(points, rules):
    """Every reading the ranges block names carries its class, owner, ack_within_min and max_age_min. -> the keys of
    MEASURED readings that fit no class: a value the block did not foresee, flagged by the caller."""
    ms, lost = ranges_of(rules), []
    for k, m in ms.items():
        p = points.get(k)
        if not isinstance(p, dict) or not isinstance(m, dict) or not isinstance(m.get("classes"), dict):
            continue
        p["class"] = read_class(ms, k, points)
        p["owner"] = m.get("owner")
        p["max_age_min"] = m.get("max_age_min")
        if "ack_within_min" in m:
            p["ack_within_min"] = m["ack_within_min"]
        if p["class"] is None and p.get("m") == "MEASURED" and all(
                (points.get(g) or {}).get("m") == "MEASURED" for g in m.get("idle_if") or []):
            lost.append(k)
    return lost


def need_ranges(rules, keys):
    """-> why these metrics cannot be judged, or None: a limit that is missing must read blind, never sane."""
    ms = ranges_of(rules)
    bad = [k for k in keys if metric_problem(k, ms.get(k), ms)]
    return "the ranges block cannot judge %s" % ", ".join(bad) if bad else None


def load_rules(path=None) -> dict:
    """The rules, or the last good copy with `_load_error` set when the file is torn: a bad write to the rules must not
    stop every reading and alarm. With no good copy yet it raises, and the unit fails aloud."""
    last_good = ops_dir() / "rules_last_good.json"
    try:
        rules = json.loads(Path(path or rules_path()).read_text(encoding="utf-8"))
        if not isinstance(rules, dict):
            raise ValueError("the rules file's root is not an object")
        sd = rules.get("series_days", 8)
        if isinstance(sd, bool) or not isinstance(sd, (int, float)) or not finite(sd) or sd <= 0:
            raise ValueError("series_days is not a positive number: %r" % (sd,))  # every pass needs it before any collector
        at = nonfinite_at(rules)
        if at:      # 1e309 parses as infinity: every comparison against that limit would silently stay false
            raise ValueError("%s is not a finite number" % at)
        if "ranges" in rules and ranges_problems(rules):      # a metric nobody answers for must not reach a pass
            raise ValueError("ranges refused: " + "; ".join(ranges_problems(rules)))
    except (OSError, ValueError) as e:
        saved = read_json(last_good)
        if not isinstance(saved, dict):
            raise
        saved["_load_error"] = "%s: %s" % (type(e).__name__, str(e))
        return saved
    try:
        atomic_json(last_good, rules)
    except OSError:
        pass            # the copy is a spare; the rules in hand are good
    return rules


def iso(t: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def finite(v):
    """math.isfinite that says False for a JSON integer too large for a float, instead of raising OverflowError."""
    try:
        return math.isfinite(v)
    except OverflowError:
        return False


def epoch(s):
    if s is None:
        return None
    if isinstance(s, bool):
        return None
    if isinstance(s, (int, float)):
        return float(s) if finite(s) else None
    from datetime import datetime
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except (ValueError, OverflowError, OSError):
        return None


def M(v, unit=None, **x):
    p = {"v": v, "m": "MEASURED"}
    if unit:
        p["unit"] = unit
    if x:
        p["x"] = x
    return p


def E(v, why, unit=None, **x):
    p = {"v": v, "m": "ESTIMATE", "why": why}
    if unit:
        p["unit"] = unit
    if x:
        p["x"] = x
    return p


def U(why, unit=None):
    p = {"v": None, "m": "UNMEASURED", "why": why}
    if unit:
        p["unit"] = unit
    return p


def read_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def runway(left_pct, rate_pct_h, hours_to_reset):
    """Hours the quota lasts at the burn rate / hours to the reset; capped at 10 (a quota not being spent)."""
    if left_pct is not None and left_pct <= 0:
        return 0.0          # spent: runs out now, whatever the rate (known even before there is a rate)
    if left_pct is None or rate_pct_h is None or hours_to_reset is None or hours_to_reset <= 0:
        return None         # an unknown burn is not "no burn"
    if not all(math.isfinite(x) for x in (left_pct, rate_pct_h, hours_to_reset)):
        return None         # NaN would pass min(10.0, NaN) as a full runway
    if rate_pct_h <= 0:
        return 10.0
    return round(min(10.0, (left_pct / rate_pct_h) / hours_to_reset), 2)


FRESH_WEEK_H = 6.0  # a week younger than this has its age floored here when its average burn is the rate
FLAT_H = 3.0        # a Codex meter unmoved this long up to now is flat: a real pause, not a gap between jobs
RECENT_H = 6        # a flat meter's burn is its slope over this many hours ending now


def week_avg_rate(used_pct, hours_to_reset, week_h=168.0):
    """The week's average burn (% per h) and how it was got. A FRESH week (under FRESH_WEEK_H old) counts as
    FRESH_WEEK_H old: its own average over a few minutes is noise (1% in 10 min reads as a 0.1 runway), while
    reading it UNMEASURED made a just-reset, full account an alarm every tick (OPSWATCH_SILENCE_FRESH_WEEK_RUNWAY).
    The floor can understate the rate only inside those first hours, by at most FRESH_WEEK_H / age; a heavy early
    burn still reads low (30% in 3 h -> 5%/h). -> (rate | None, how | None)."""
    if used_pct is None or hours_to_reset is None:
        return None, None
    elapsed = week_h - hours_to_reset
    if elapsed >= FRESH_WEEK_H:
        return used_pct / elapsed, "the week's average burn (%.0f%% over %.0f h)" % (used_pct, elapsed)
    return used_pct / FRESH_WEEK_H, "a fresh week's burn (%.0f%% in its first %.1f h, counted over %.0f h)" % (
        used_pct, max(0.0, elapsed), FRESH_WEEK_H)


def flat_rate(readings, now, flat_h=FLAT_H, recent_h=RECENT_H):
    """The burn while the meter is flat, or None if it moved inside flat_h. `readings` are (epoch, used %) of one
    weekly window, oldest first. Codex writes a reading only when used, so silence up to `now` counts as flatness;
    a slope over the readings alone ends at the last one and would keep the last burst's rate through the quiet.
    -> (% per h over the last recent_h ending now, time the meter reached today's value) | None."""
    t, used = readings[-1]
    since = t
    for a, b in reversed(readings):
        if b != used:
            break
        since = a
    if (now - since) / HOUR < flat_h:
        return None
    start = now - recent_h * HOUR
    before = [b for a, b in readings if a <= start]
    base, base_t = (before[-1], start) if before else (readings[0][1], readings[0][0])
    return max(0.0, used - base) / ((now - base_t) / HOUR), since


def loan_runway(name, reading, rate, how, src, lent_rules, allowance, live, now):
    """A lent account's runway against the loan (slot_rules.json lent_accounts), not the week. The rule stops our draw
    at the end of his window or at the cap, so extrapolating to his weekly reset measures nothing of ours. Open loan:
    x the hours left in the window that the allowance lasts at this burn. Closed loan (allowance 0: outside the window,
    at the cap or floor, off-limits): nothing of ours to run out unless this machine is still on it, which is 0. The
    meter cannot tell his use from ours, so a closed loan with a burn and no live login here is his week, not an alarm.
    reading: {"left", "used", "h"}; live: this machine's account label, or None when unknown."""
    unit = "x the time to the end of the loan"
    def mark(v, why, **x):
        return M(v, unit, why=why, **x) if src == "MEASURED" else E(v, why + "; the reading is an ESTIMATE", unit, **x)
    h = reading["h"]
    if h is None:
        return U("no reset time, so the lent window cannot be placed")
    pol = lent_rules["lent_accounts"][name]
    cap, why = allowance({"account": name, "pct_left": reading["left"], "pct_used": reading["used"], "hours_to_reset": h,
                          "resets_at": None, "source": src}, lent_rules, now)
    open_h = h - (168.0 - pol["prefer_start_of_week_h"])
    if cap > 0 and open_h > 0:
        rw = runway(cap, rate, open_h)
        if rw is None:
            return U("the loan is open and no burn rate is known: " + why)
        extra = {"rate_pct_h": round(rate, 3), "loan_left_pct": round(cap, 1), "loan_h_left": round(open_h, 1)}
        if src == "MEASURED" and how.startswith("meter"):
            return M(rw, unit, rate_from=how, **extra)
        return E(rw, "rate from %s%s" % (how, "" if src == "MEASURED" else "; the reading is an ESTIMATE"), unit, **extra)
    if live is None:
        return U("the loan is closed and this machine's account cannot be read: " + why)
    if live == name:
        return mark(0.0, "this machine is on a closed loan: " + why)
    return mark(10.0, "the loan is closed and this machine is on %s: %s" % (live, why))


def live_label(au):
    """The registry label this machine's sessions are logged in as, or None when that cannot be read."""
    try:
        email = au.live_email()
        return next((label for label, mail in au.registry().items() if email and mail == email), None)
    except Exception:  # noqa: BLE001  an unknown login is None; the callers hold on it
        return None


# ================================================================================================== collectors
def c_accounts(now, rules, ctx):
    import account_usage as AU
    import slot_allocator as SA
    out = {}
    acc = (AU.read_now(now).get("accounts") or {})
    if not acc:
        return {"accounts._collector": U("account_usage.read_now() returned no account")}
    fit = {"fit": rules.get("accounts_fit")}
    live = live_label(AU)
    try:
        lent_rules = SA.load_rules()
        lent = set(lent_rules.get("lent_accounts") or {})
    except Exception as e:  # noqa: BLE001  no lent set: every account stays judged by its week, which alarms early
        lent_rules, lent = None, set()
        out["accounts._collector"] = U("slot_rules.json unreadable, no account is judged by its loan: %s: %s"
                                       % (type(e).__name__, str(e)))
    def account(name, a):
        src = a.get("source") or "UNMEASURED"
        if a.get("stale"):
            src = "ESTIMATE" if src == "MEASURED" else src
        left, h = a.get("week_pct_left"), a.get("hours_to_week_reset")
        k = "accounts.%s." % name
        reset = epoch(a.get("week_resets_at"))
        if (src in ("MEASURED", "ESTIMATE") and left is None and a.get("week_pct_used") is not None
                and reset is not None and 0 <= now - reset < 168 * 3600):
            # OPS_READING_FIX_SHUT_WINDOW_IS_FULL: the week reset AFTER the reading (read_now blanks a passed window's
            # figure). A reset quota is a fresh week, not an unknown one: up to one poll of new burn is unread, so 100%
            # left is an upper bound (ESTIMATE). It read UNMEASURED and raised role:<name>:ops on every launch inside
            # the gap (2026-11-04 20:20Z, 21 min after the system account's reset).
            h = round(168.0 - (now - reset) / 3600.0, 2)
            why = "the weekly reset at %s passed after the reading: a fresh week, its burn not yet read" % a.get(
                "week_resets_at")
            out[k + "week_left_pct"] = E(100.0, why + " (an upper bound)", "% of the weekly quota left",
                                         measured_at=a.get("measured_at"))
            out[k + "hours_to_reset"] = E(h, why + "; one week after the passed reset", "h to the weekly reset")
            out[k + "runway"] = E(10.0, why + "; nothing spent yet reads the cap", "x the time to reset")
            if name in lent:
                out[k + "loan_runway"] = loan_runway(name, {"left": 100.0, "used": 0.0, "h": h}, 0.0, why, "ESTIMATE",
                                                     lent_rules, SA.lent_allowance, live, now)
                out[k + "runway"]["judged_by"] = k + "loan_runway"
            return
        if src not in ("MEASURED", "ESTIMATE") or left is None:
            # the record's own why can describe another field (a closed session window): name the week's own gap
            why = "account_usage: %s" % (
                (a.get("why") or src) if src not in ("MEASURED", "ESTIMATE") else
                "a %s reading with no week figure left%s" % (src, " (record note: %s)" % a["why"] if a.get("why") else ""))
            for f in ("week_left_pct", "hours_to_reset", "runway") + (("loan_runway",) if name in lent else ()):
                out[k + f] = U(why)
            return
        mk = (lambda v, u, **x: M(v, u, **x)) if src == "MEASURED" else \
            (lambda v, u, **x: E(v, "account_usage reading is an ESTIMATE%s" % (" (stale)" if a.get("stale") else ""), u, **x))
        out[k + "week_left_pct"] = mk(left, "% of the weekly quota left", measured_at=a.get("measured_at"))
        # each per-model weekly limit as its own point (RIMMANDRAKE_READ_FABLE_WEEKLY_METER_USAGE_LINE_NEVER_SHOWED): a
        # launch of that model reads the lower of the two (role_launch.ops_reading); a window reset since the reading
        # is no point at all, so the all-models figure alone applies, never a guessed 100
        for scope, w in sorted((a.get("model_weeks") or {}).items()):
            if (w or {}).get("pct_left") is None:
                continue
            if w.get("carried_from"):    # the record's source could not see it: the last reading, carried
                out[k + "model_week_left_pct." + scope] = E(w["pct_left"], "carried from the reading at %s" % w[
                    "carried_from"], "%% of the %s weekly limit left" % scope, scope=scope, measured_at=w["carried_from"])
            else:
                out[k + "model_week_left_pct." + scope] = mk(w["pct_left"], "%% of the %s weekly limit left" % scope,
                                                             scope=scope, measured_at=a.get("measured_at"))
        out[k + "hours_to_reset"] = mk(h, "h to the weekly reset") if h is not None else U("no reset time")
        rate, how = None, None
        try:
            # the slope reads only MEASURED records, so it stays true of an ESTIMATE reading: flat readings mean flat
            r, n, span = SA.slope(name, a.get("week_resets_at"), now, fit)
        except (KeyError, TypeError, ValueError) as e:  # a bad rule costs the slope: the week average still reads
            r, n, span = None, 0, 0
            out["accounts._collector"] = U("accounts_fit unusable, runway uses the week average: %s: %s"
                                           % (type(e).__name__, str(e)))
        if r is not None:
            rate, how = r, "meter slope, %d readings over %.1f h" % (n, span)
        # an ESTIMATE says only that nothing was read: on an account not in use the week's average would invent a draw
        if rate is None and (src == "MEASURED" or live == name):
            rate, how = week_avg_rate(a.get("week_pct_used"), h)
        rw = runway(left, rate, h)
        if rw is None:
            out[k + "runway"] = U("no burn rate: the reading is an ESTIMATE of an account not in use, with no slope"
                                  if src != "MEASURED" and live != name else
                                  "no burn rate: no week figure or reset time, and the meter has no slope")
        elif rate is None:      # spent before any rate exists: 0 is as certain as the reading
            out[k + "runway"] = (M(0.0, "x the time to reset", why="quota spent") if src == "MEASURED" else
                                 E(0.0, "quota spent per an ESTIMATE reading", "x the time to reset"))
        elif src == "MEASURED" and how and how.startswith("meter"):
            out[k + "runway"] = M(rw, "x the time to reset", rate_pct_h=round(rate, 3), rate_from=how)
        else:
            out[k + "runway"] = E(rw, "rate from %s%s" % (how, "" if src == "MEASURED" else "; the reading is an ESTIMATE"),
                                  "x the time to reset", rate_pct_h=round(rate, 3))
        if name in lent:
            out[k + "loan_runway"] = loan_runway(name, {"left": left, "used": 100.0 - left, "h": h}, rate, how, src,
                                                 lent_rules, SA.lent_allowance, live, now)
            out[k + "runway"]["judged_by"] = k + "loan_runway"
    for name, a in sorted(acc.items()):
        try:
            account(name, a)
        except Exception as e:  # noqa: BLE001  one malformed account costs only itself
            for f in ("week_left_pct", "hours_to_reset", "runway"):
                out["accounts.%s.%s" % (name, f)] = U("account_usage: malformed account row: %s: %s" % (
                    type(e).__name__, str(e)))
    try:
        out.update(fleet_readings(acc, live, now, rules, SA.slope))
    except Exception as e:  # noqa: BLE001  a broken plan or rule costs the fleet readings, said aloud, not the rest
        why = "fleet readings failed: %s: %s" % (type(e).__name__, str(e))
        out["accounts.fleet_burn_pct_h"] = U(why)
        out["accounts.fleet_stop_h"] = U(why)
        for n in sorted(acc):
            out["accounts.%s.moved_runway" % n] = U(why)
    return out


# RIMMANDRAKE_READ_FLEET_MOVED_RUNWAY_IDLE_ACCOUNT_READS_TEN: runway() judges each account by its OWN burn, so an account
# not in use reads 10 by construction; nothing warned before the fleet stops of 2026-11-17 03:35 and 05:50 PST (lukas
# at its floor, system at 1% left, steven outside his window). These readings apply the FLEET's burn instead.
FLEET_KEYS = ("accounts.fleet_burn_pct_h", "accounts.fleet_stop_h")


def fleet_rate(meter, now, rules, slope_of):
    """The fleet's measured burn: the SUM of every account's meter slope, over the short window (rules
    fleet_fit.short_window_h, "a fast burn inside a few hours") and over the runway's own window (accounts_fit),
    the faster of the two. A sum, not the live account's slope: the fleet moves between accounts, and right after a
    move the new account's slope is mostly its idle hours. It counts every burn on the pool (the owner's own sessions,
    a lent account's owner), which errs early, never late. -> (rate %/h, how) or (None, why)."""
    ff = rules["fleet_fit"]
    short = {"window_h": ff["short_window_h"], "slope_min_points": ff["slope_min_points"],
             "slope_min_span_h": ff["slope_min_span_h"]}
    got = []
    for fit in (short, rules["accounts_fit"]):
        parts = []
        for n, r in sorted(meter.items()):
            b, k, span = slope_of(n, (r or {}).get("week_resets_at"), now, {"fit": fit})
            if b is not None:
                parts.append((n, b))
        if parts:
            got.append((sum(b for _n, b in parts), "the meter slopes over the last %g h, summed: %s" % (
                fit["window_h"], ", ".join("%s %.2f" % x for x in parts))))
    if not got:
        return None, "no account's meter has enough readings for a slope"
    return max(got)


def fleet_readings(meter, live, now, rules, slope_of, plan=None):
    """-> points: accounts.fleet_burn_pct_h, accounts.fleet_stop_h and accounts.<name>.moved_runway for every account
    of the switching plan. meter: account_usage.read_now()'s accounts; live: this machine's account label (None when
    unreadable); slope_of: slot_allocator.slope; plan: switching_plan.json (read when None).
      fleet_stop_h   hours until the plan has no account to run the fleet on, the plan's own lines() + pick() run
                     forward at the fleet's burn (switching_plan.simulate, resets refill), capped at fleet_fit.horizon_h.
                     0 = the plan has no account now: the fleet is stopped.
      moved_runway   that account's room above its plan line / (the fleet's burn x the hours to its expiry: its reset,
                     or steven's window end), capped at 10 like runway(); 0 when the plan cannot move there now.
    An account with no week figure counts as no room in the forecast (a stop may come later than it says: ESTIMATE),
    an ESTIMATE figure as its upper bound (ESTIMATE). No burn rate: every point UNMEASURED."""
    import switching_plan as SP
    plan = SP.load_plan() if plan is None else plan
    ff = rules["fleet_fit"]
    unit_h = "h until the plan has no account for the fleet (capped at %g)" % ff["horizon_h"]
    unit_rw = "x the time to reset, at the fleet's burn"
    names = list(plan["order"]) + sorted(n for n in meter if n not in plan["order"])
    rate, how = fleet_rate(meter, now, rules, slope_of)
    if rate is None:
        return {**{k: U("no fleet burn rate: " + how) for k in FLEET_KEYS},
                **{"accounts.%s.moved_runway" % n: U("no fleet burn rate: " + how) for n in names}}
    out = {"accounts.fleet_burn_pct_h": M(round(rate, 3), "% of the weekly quota per h", live=live, rate_from=how)}
    # every reading as the engine believes it (blind near-empty = 0), handed to the engine as MEASURED
    sm, guessed = {}, []
    for n in plan["order"]:
        r = meter.get(n) or {}
        p = SP.left(plan, r, now)
        if p is None and not SP.reset_passed(r, now):
            guessed.append("%s has no week figure (counted as no room)" % n)
        elif not SP.usable(r) and not SP.blind_zero(plan, r, now):
            guessed.append("%s is an ESTIMATE (its figure is an upper bound)" % n)
        sm[n] = {**r, "source": "MEASURED" if p is not None else "UNMEASURED", "stale": False, "week_pct_left": p}
    def mark(v, unit, why, **x):
        return E(v, why + "; " + "; ".join(guessed), unit, **x) if guessed else M(v, unit, why=why, **x)
    ev = SP.simulate(sm, now, plan, live, rate, hours=ff["horizon_h"], step_min=ff["step_min"])
    stop = next((e for e in ev if e["kind"] == "target" and e["target"] is None), None)
    if stop is None:
        out["accounts.fleet_stop_h"] = mark(float(ff["horizon_h"]), unit_h, "no stop inside %g h at %.2f%%/h" % (
            ff["horizon_h"], rate), rate_pct_h=round(rate, 3))
    else:
        on = [e["target"] for e in ev if e["kind"] == "target" and e["at"] <= stop["at"] and e["target"]]
        out["accounts.fleet_stop_h"] = mark(round(max(0.0, (stop["at"] - now) / HOUR), 2), unit_h,
                                            "the plan stops at %s at %.2f%%/h%s" % (
                                                iso(stop["at"]), rate, ", after " + " -> ".join(on) if on else
                                                ": it has no account now"),
                                            rate_pct_h=round(rate, 3), stop_at=iso(stop["at"]), pct=stop["pct"])
    ep = SP.at(plan, now, meter)
    line, elig = SP.lines(sm, ep, now)
    for n in names:
        k = "accounts.%s.moved_runway" % n
        r = sm.get(n) or {}
        if n not in ep["order"]:
            out[k] = M(0.0, unit_rw, why="not in the switching plan: the fleet is never moved here")
        elif r.get("week_pct_left") is None:
            out[k] = U("no week figure for %s" % n)
        elif not elig.get(n):
            why = ("outside its window" if not SP.in_window(ep, n, r, now) else "at or under its line %g%%" % line[n]
                   if r["week_pct_left"] <= line[n] else "its reading is from before a passed reset")
            out[k] = mark(0.0, unit_rw, "the plan cannot move the fleet here now: " + why, eligible=False)
        else:
            room = r["week_pct_left"] - line[n]
            exp = SP.expiry(ep, n, r, now)
            h = None if exp is None else (exp - now) / HOUR
            rw = runway(room, rate, h)
            out[k] = (U("no reset time for %s" % n) if rw is None else
                      mark(rw, unit_rw, "%.1f%% above its line %g%% at the fleet's %.2f%%/h, %.1f h to its expiry" % (
                          room, line[n], rate, h), room_pct=round(room, 1), hours=round(room / rate, 2) if rate > 0
                           else None, live=(n == live)))
    return out


def codex_dirs():
    # One account: the newest reading in any known session folder (the ChatGPT desktop app writes there too).
    import csuite_codex_limits as CX
    env = os.environ.get("RM_CODEX_SESSIONS")
    return env.split(os.pathsep) if env else list(CX.DIRS)


def c_codex(now, rules, ctx):
    import csuite_codex_limits as CX
    cr = rules["codex"]
    dirs = [d for d in codex_dirs() if os.path.isdir(d)]
    if not dirs:
        return {k: U("no codex sessions directory (%s)" % os.pathsep.join(codex_dirs())) for k in
                ("codex.week_used_pct", "codex.hours_to_reset", "codex.runway")}
    recs, nfiles = CX.readings(dirs, newer_than=now - cr["lookback_days"] * DAY,
                              cache=str(ops_dir() / "codex_readings_cache.json"))
    week, bad = [], []      # bad: the time of each record that cannot be used; None when not even that reads
    for r in recs:      # (ts, p_used, p_win, p_reset, s_used, s_win, s_reset, plan)
        try:
            if isinstance(r[2], str) or isinstance(r[5], str):
                raise ValueError("window is text")      # a weekly record in the wrong shape must not read as no record
            if r[2] == 10080:
                week.append((epoch(r[0]), float(r[1]), epoch(r[3])))
            elif r[5] == 10080 and r[4] is not None:
                week.append((epoch(r[0]), float(r[4]), epoch(r[6])))
        except (TypeError, ValueError, OverflowError, IndexError, KeyError):
            try:        # one bad record costs itself; a good one still reads, marked if the bad one is the newer
                bad.append(epoch(r[0]))
            except (TypeError, IndexError, KeyError):
                bad.append(None)
    def usable(w):      # negative usage is no reading: it would clamp to no burn and read as a healthy runway
        return w[0] is not None and w[2] is not None and finite(w[1]) and w[1] >= 0 and w[0] <= now + 300
    bad += [w[0] for w in week if not usable(w)]
    week = sorted(w for w in week if usable(w))
    if not week:
        why = "no weekly rate_limits reading in %d rollout file(s) modified in %d d" % (nfiles, cr["lookback_days"])
        return {k: U(why) for k in ("codex.week_used_pct", "codex.hours_to_reset", "codex.runway")}
    t, used, reset = week[-1]
    out = {}
    if reset <= now:
        why = "the weekly window of the last reading (%s) reset at %s; no reading since" % (iso(t), iso(reset))
        out["codex.week_used_pct"] = E(0.0, why, "% of the weekly quota used")
        out["codex.hours_to_reset"] = U(why)
        out["codex.runway"] = U(why)
        return out
    h = (reset - now) / HOUR
    age_h = (now - t) / HOUR
    newer = sum(1 for b in bad if b is None or b > t)
    if newer:
        out["codex.week_used_pct"] = E(used, "%d record(s) newer than the reading of %s cannot be read: a floor" % (newer, iso(t)),
                                       "% of the weekly quota used", reading_at=iso(t), files=nfiles)
    elif age_h > cr.get("stale_h", 6):
        # no Codex session here since; another machine may have spent it, so the % is a floor, not a reading
        out["codex.week_used_pct"] = E(used, "last reading %.1f h old (%s): a floor; spend elsewhere is unseen" % (
            age_h, iso(t)), "% of the weekly quota used", reading_at=iso(t), files=nfiles)
    else:
        out["codex.week_used_pct"] = M(used, "% of the weekly quota used", reading_at=iso(t), files=nfiles)
    out["codex.hours_to_reset"] = M(round(h, 1), "h to the weekly reset")
    window = [(a, b) for a, b, c in week if abs(c - reset) < HOUR]
    same = [w for w in window if w[0] >= now - cr["slope_window_h"] * HOUR]
    rate, how = None, None
    flat = None if newer else flat_rate(window, now)
    if flat:
        rate, how = flat[0], "the last %d h to now: the meter is flat since %s; spend elsewhere is unseen" % (
            RECENT_H, iso(flat[1]))
    elif len(same) >= 2 and (same[-1][0] - same[0][0]) / HOUR >= cr["slope_min_span_h"]:
        rate = max(0.0, (same[-1][1] - same[0][1]) / ((same[-1][0] - same[0][0]) / HOUR))
        how = "readings over the last %d h" % cr["slope_window_h"]
    if rate is None:
        rate, how = week_avg_rate(used, h)
    rw = runway(100.0 - used, rate, h)
    if rw is None:
        out["codex.runway"] = U("no burn rate")
    elif rate is None:
        out["codex.runway"] = (M(0.0, "x the time to reset", why="quota spent")
                               if out["codex.week_used_pct"]["m"] == "MEASURED" else
                               E(0.0, "quota spent per an ESTIMATE reading", "x the time to reset"))
    elif how.startswith("readings") and out["codex.week_used_pct"]["m"] == "MEASURED":
        out["codex.runway"] = M(rw, "x the time to reset", rate_pct_h=round(rate, 3), rate_from=how)
    else:
        out["codex.runway"] = E(rw, "rate from " + how, "x the time to reset", rate_pct_h=round(rate, 3),
                                rate_from="flat" if flat else how)
    return out


def done_jobs(since, bad=None, now=None):
    """testq done records finished at or after `since` (epoch), oldest first, read by file mtime first. A record in the
    window that cannot be read is appended to `bad` (when given), so a caller never mistakes the readable subset for all.
    Given `now`, a record dated in the future is such a record: sorted last, it would pass as the newest result."""
    out = []
    for f in glob.glob(str(qhome() / "done" / "*.json")):
        try:
            if os.path.getmtime(f) < since - DAY:
                continue
        except OSError:
            if bad is not None:
                bad.append(os.path.basename(f))     # cannot tell its age: count it as unseen, not as absent
            continue
        d = read_json(f)
        whole = isinstance(d, dict) and isinstance(d.get("result") or {}, dict) and isinstance(d.get("job") or {}, dict)
        fin = epoch(d.get("finished") or (d.get("result") or {}).get("finished")) if whole else None
        if fin is None:
            if bad is not None:
                try:
                    if os.path.getmtime(f) >= since:
                        bad.append(os.path.basename(f))
                except OSError:
                    pass
            continue
        if now is not None and fin > now + 300:
            if bad is not None:
                bad.append(os.path.basename(f))
            continue
        if fin >= since:
            out.append((fin, d))
    out.sort(key=lambda x: x[0])
    return out


OUTCOMES = ("DONE", "INVALID", "INTERRUPTED", "REFUSED")     # testq/schema.py's OUTCOMES; the selftest holds them equal


def outcome_of(d):
    """A done record's outcome, or None: one outside the schema's words is no outcome, never a known non-INVALID result."""
    oc = (d.get("result") or {}).get("outcome")
    return oc if isinstance(oc, str) and oc in OUTCOMES else None


def incident_unowned(inc):
    """True when this steward incident owns nobody: no item was filed, the item closed, or a readable ledger never heard
    of it. An unreadable ledger is False: c_flow says that aloud."""
    item = inc.get("item") if isinstance(inc, dict) else None
    if not item:
        return True
    try:
        import ops_ledger as pc
        it = pc._model().replay(pc.read_ledger(origin=rerun_root())).items.get(item)
    except Exception:  # noqa: BLE001
        return False
    return it is None or not it.open


def ladder_blind(inc):
    """True when a steward incident's ladder cannot run because the ledger is unreadable (testq/steward.py LEDGER_ERR,
    a torn shard after an unclean stop: OPS_STEVE_UNSTICK_VHRP) and it holds no item: nobody is escalating."""
    return isinstance(inc, dict) and not inc.get("item") and \
        str(inc.get("error") or "").startswith("ledger unreadable: ")


INVALID_SHARE_MIN_JOBS = 8     # fewer finished jobs in 24 h make a share an ESTIMATE: one death would read 50 %


def invalid_class_mod():
    """testq/invalid_class.py, loaded by path: putting testq/ on sys.path would shadow modules named like its own."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("testq_invalid_class", str(HERE / "testq" / "invalid_class.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def invalid_share(d24):
    """RIMMANDRAKE_STOP_STEVEDESKTOP_INVALID_RUNS_REPEATING_UNFIXED: the share of the last 24 h of Steve-lane jobs that
    died INVALID, split by whose fault (invalid_class: TEST, DELIVERY, GAME, UNKNOWN). Owner 2026-11-14: "So much
    waste. And it just keeps happening." The streak alarm saw none of it: deaths came between passes."""
    try:
        IC = invalid_class_mod()
    except Exception as e:  # noqa: BLE001 - an instrument that errors says so, never 0
        return U("testq/invalid_class.py would not load: %s" % e)
    s = IC.share(d24)
    if not s["jobs"]:
        return U("no Steve-lane job finished in 24 h")
    x = dict(jobs=s["jobs"], invalid=s["invalid"], **{k.lower(): v for k, v in sorted(s["by_class"].items())})
    if s["jobs"] < INVALID_SHARE_MIN_JOBS:
        return E(s["share"], "only %d job(s) in 24 h (< %d): too few for a share" % (s["jobs"], INVALID_SHARE_MIN_JOBS),
                 "share of jobs INVALID, 24 h", **x)
    return M(s["share"], "share of jobs INVALID, 24 h", **x)


def c_steve(now, rules, ctx):
    out = {}
    sj = read_json(qhome() / "steward.json")
    if not isinstance(sj, dict) or epoch(sj.get("epoch")) is None or "state" not in sj \
            or not isinstance(sj.get("fault"), bool) or epoch(sj["epoch"]) > now + 300:
        # a record with no state or fault, or from the future, says nothing about a stall: unknown, never a healthy 0
        out["steve.state"] = U("steward.json missing or unreadable under %s" % qhome())
        for k in ("heartbeat_age_min", "fault_min", "unowned_stall_min"):
            out["steve." + k] = U("steward.json missing or unreadable")
    else:
        hb = (now - epoch(sj["epoch"])) / 60.0
        wj = read_json(qhome() / "steward_watch.json")
        wj = wj if isinstance(wj, dict) else {}
        we = epoch(wj.get("epoch"))
        wage = (now - we) / 60.0 if we is not None and we <= now + 300 else None     # from the future: no reading
        st = sj.get("state")
        if hb > 30:
            out["steve.state"] = E(st, "steward.json is %.0f min old: its last word, not now" % hb, "steward state",
                                   reason=str(sj.get("reason") or ""), since=sj.get("since"))
        else:
            out["steve.state"] = M(st, "steward state", reason=str(sj.get("reason") or ""), since=sj.get("since"))
        out["steve.heartbeat_age_min"] = M(round(hb, 1), "min since steward.json")
        out["steve.watch_age_min"] = M(round(wage, 1), "min since steward_watch.json") if wage is not None else \
            U("steward_watch.json has no epoch")
        since = epoch(sj.get("since"))
        if hb > 30:
            fault_min = None    # a stale steward's fault flag is its last word, not now: unknown, never 0
            out["steve.fault_min"] = U("steward.json is %.0f min old: whether it is in a fault now is unknown" % hb)
        elif sj.get("fault") and (since is None or since > now + 300):
            fault_min = None
            out["steve.fault_min"] = U("steward reports a fault with no readable `since`: duration unknown")
        else:
            fault_min = round((now - since) / 60.0, 1) if sj.get("fault") else 0.0
            out["steve.fault_min"] = M(fault_min, "min in a fault state")
        nobody = []
        # a set `incident` is ownership whatever became of its item: the steward's ladder (testq/steward.py) keeps
        # escalating it until RUNNING, so a closed item is re-raised, not abandoned
        if fault_min and fault_min > 0 and not sj.get("incident"):
            nobody.append(("fault %s for %.0f min with no steward incident" % (st, fault_min), fault_min))
        elif fault_min and fault_min > 0 and ladder_blind(sj.get("incident")):
            nobody.append(("fault %s for %.0f min, the steward's ladder blind: %s" % (
                st, fault_min, str(sj["incident"]["error"])), fault_min))
        # both silent, nothing is left to re-raise: here an unfiled, unknown or closed item owns nothing
        if hb > 30 and (wage is None or wage > 30) and (not wj.get("incident") or incident_unowned(wj["incident"])):
            nobody.append(("steward silent %.0f min and its watcher silent %s" % (
                hb, "(never ran)" if wage is None else "%.0f min" % wage), hb))
        elif hb > 30 and ladder_blind(wj.get("incident")):     # the watcher runs but cannot escalate
            nobody.append(("steward silent %.0f min and its watcher's ladder blind: %s" % (
                hb, str(wj["incident"]["error"])), hb))
        if fault_min is None and not nobody:
            out["steve.unowned_stall_min"] = U("steward state stale or a fault of unknown duration: whether a stall is "
                                               "owned is unknown")
        elif nobody:
            why, v = max(nobody, key=lambda x: x[1])
            out["steve.unowned_stall_min"] = M(round(v, 1), "min stalled with nobody escalating", why=why)
        else:
            out["steve.unowned_stall_min"] = M(0.0, "min stalled with nobody escalating",
                                               why="the steward owns any stall" if fault_min else "no stall")
    bad = []
    jobs = done_jobs(now - 7 * DAY, bad, now)
    # a record with no outcome cannot say INVALID or not: unseen, like an unreadable one
    bad += [str((d.get("job") or {}).get("id") or "?") + " (no outcome)" for _, d in jobs
            if not outcome_of(d)]
    ctx["steve_jobs_bad"] = bad
    if not jobs:
        why = "no testq done record in 7 d under %s" % (qhome() / "done") + (
            " (%d unreadable)" % len(bad) if bad else "")
        for k in ("invalid_streak", "jobs_24h", "invalid_24h", "last_done_age_min"):
            out["steve." + k] = U(why)
        return out
    def run_of_invalid(js):
        """-> (length of the newest run, its oldest finish time, did a record with no outcome stop it)"""
        n, start = 0, None
        for fin, d in reversed(js):
            oc = outcome_of(d)
            if oc != "INVALID":
                if not oc and str((d.get("job") or {}).get("id") or "?") + " (no outcome)" not in bad:
                    bad.append(str((d.get("job") or {}).get("id") or "?") + " (no outcome)")   # the run's end is unknown
                return n, start, not oc
            n, start = n + 1, fin
        return n, start, False
    streak, run_start, stop_unknown = run_of_invalid(jobs)
    if streak == len(jobs):
        # every job in the week was INVALID: the run may start before the window, so read the whole done history
        older_bad = []
        streak, run_start, stop_unknown = run_of_invalid(done_jobs(0, older_bad, now))
        bad += [b for b in older_bad if b not in bad]
    last = jobs[-1]
    out["steve.invalid_streak"] = M(streak, "INVALID results in a row", last_job=(last[1].get("job") or {}).get("id"),
                                    last_cause=(last[1].get("result") or {}).get("cause"))
    d24 = [d for f, d in jobs if f >= now - DAY]
    out["steve.jobs_24h"] = M(len(d24), "jobs finished, 24 h")
    out["steve.invalid_24h"] = M(sum(1 for d in d24 if (d.get("result") or {}).get("outcome") == "INVALID"),
                                 "INVALID jobs, 24 h")
    out["steve.last_done_age_min"] = M(round((now - last[0]) / 60.0, 1), "min since the last job finished")
    out["steve.invalid_share_24h"] = invalid_share(d24)
    def may_be_in_run(b):
        """Could unseen record `b` sit inside the run? Only a record no older than the run can break it; an older
        bad record leaves a run of readable INVALIDs certain, and must not turn the alarm off (it needs MEASURED)."""
        if b.endswith(" (no outcome)"):
            return False            # placed by its finish time: it stopped the run (stop_unknown) or is older
        try:
            return run_start is None or os.path.getmtime(qhome() / "done" / b) >= run_start
        except OSError:
            return True
    streak_sure = not stop_unknown and not any(may_be_in_run(b) for b in bad)
    if bad:
        for k in ("invalid_streak", "jobs_24h", "invalid_24h", "last_done_age_min"):
            if k == "invalid_streak" and streak_sure:
                continue
            p = out["steve." + k]
            out["steve." + k] = E(p["v"], "%d done record(s) in the window unreadable (%s): counted over the readable "
                                  "rest" % (len(bad), ", ".join(bad[:3])), p.get("unit"), **(p.get("x") or {}))
    ctx["steve_jobs"] = jobs
    return out


# STEVE_SEATS_FIX_DIE_ON_REBOOT: are SteveDesktop's two Claude seats up AND connected? Each lives in a tmux session
# (accounts/stevedesktop_fleet.ps1 in claude-remote-control), so its screen is readable over ssh. A live process is
# not the test: on 2026-10-31 the Server sat alive at a trust prompt, never connected.
SEAT_PROBE = """cut -d. -f1 /proc/uptime
for s in %s; do p=$(tmux capture-pane -p -t "$s" 2>/dev/null); echo "$p" | grep -qE '%s' && echo "up $s"; done
echo probe-done"""
SEAT_PROBE_RESERVE_S = 2.0   # inside a beat: room left after the ssh for c_steve_seats to write its reading
SEAT_PROBE_MIN_S = 2.0       # a probe given less than this would read a slow ssh as an unreachable machine


def steve_seat_probe(cfg):
    """(reachable, uptime_s, {seats up}). Reachable is False unless the whole probe ran to its last line. Inside a
    metronome beat (15 s) the ssh ends SEAT_PROBE_RESERVE_S before the beat's kill: a 30 s wait on a hung host was
    killed with the pass every beat, so absent_since was never written and STEVE_SEATS never fired. A beat with no
    room left for a probe -> (None, None, set()): no reading, not an unreachable machine."""
    cmd = SEAT_PROBE % (" ".join(cfg["seats"]), cfg["ready"])
    budget = 30.0
    dl = beat_deadline()
    if dl is not None:
        budget = min(budget, dl - time.time() - SEAT_PROBE_RESERVE_S)
        if budget < SEAT_PROBE_MIN_S:
            return None, None, set()
    try:
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=%d" % max(1, min(10, int(budget))),
                            cfg["ssh"], cmd], capture_output=True, text=True, timeout=budget)
    except (OSError, subprocess.TimeoutExpired):
        return False, None, set()
    lines = r.stdout.split("\n")
    if "probe-done" not in lines or not lines[0].isdigit():
        return False, None, set()
    return True, int(lines[0]), {x[3:] for x in lines if x.startswith("up ")}


def c_steve_seats(now, rules, ctx, probed=None):
    """steve.seats_absent_min: how long a seat has been missing, not connected, or the machine out of reach (0 = both
    live). Over the rule's line it alarms: a ledger item and a Conductor log line. Absent since boot counts from the
    boot, so a reboot that never brought them back alarms at the first look past the line; a seat lost later counts
    from the first look that saw it, so one account switch (seconds) does not. Reach failing counts too: a machine
    gone is seats gone, and UNMEASURED would be silent."""
    cfg = rules.get("steve_seats")
    if not cfg:
        return {}
    reach, up, seen = probed if probed is not None else steve_seat_probe(cfg)
    if reach is None:     # the beat had no room to probe: no reading (absent_since stands for the next look)
        return {}
    missing = sorted(set(cfg["seats"]) - seen)
    p = ops_dir() / "steve_seats.json"
    st = read_json(p) if p.exists() else None
    since = st.get("absent_since") if isinstance(st, dict) else None
    if reach and not missing:
        if since is not None:
            p.unlink()
        return {"steve.seats_absent_min": M(0.0, "min a Steve seat has been absent", uptime_min=round(up / 60.0, 1))}
    if not is_num(since):
        since = now
    if reach and up <= HOUR:
        since = min(since, now - up)
    atomic_json(p, {"absent_since": since})
    said = "unreachable" if not reach else ", ".join(missing) + " absent"
    return {"steve.seats_absent_min": M(round((now - since) / 60.0, 1), "min a Steve seat has been absent", said=said,
                                        uptime_min=round(up / 60.0, 1) if reach else None)}


STEVE_TAKEABLE_KEY = "steve.idle_with_takeable_min"
FILLER_BY = "BENCH.filler"      # testq/archmagi_switch.py FILLER: the requester of a filler job


def c_steve_takeable(now, rules, ctx):
    """steve.idle_with_takeable_min (RIMMANDRAKE_WATCH_STEVE_LANE_IDLE_WHILE_VISIT_CHECKS_WAIT; page
    design/specs/2026-11-22-steve-idle-takeable/boundary.md): minutes the SteveDesktop lane has sat idle, braked or on
    filler while an in-game visit's check with a testq block waits for it. Measured 2026-11-22: 5.5 h (21:14Z-02:45Z)
    with 28 Pyrelands and 6 FlowWorks checks waiting, no reading fired. Four answers: 0 `busy` (a commissioned job, or
    any job on a waiting check's chain, runs or is ready); 0 `quiet` (nothing takeable waits); the minutes `waiting`
    since the later of the visit's opening and the last finish of a commissioned or takeable job; UNMEASURED when the
    dispatch reading (maturation_dispatch ingame_testq), the owner's hold or the queue could not be read."""
    unit = "min idle with takeable checks waiting"
    rf = str(HERE.parent / "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import maturation_dispatch as MD
    p = os.path.join(MD.sdir(), "reading.json")
    rd = read_json(p)
    if not isinstance(rd, dict):
        return {STEVE_TAKEABLE_KEY: U("the dispatch reading %s missing or unreadable" % p, unit)}
    at = epoch(rd.get("at"))
    if at is None or now - at > MATURATION_READING_MAX_AGE_S or at > now + 300:
        return {STEVE_TAKEABLE_KEY: U("the dispatch reading %s is %s old (the step is not ticking)" % (
            p, "of unknown age" if at is None else "%d min" % ((now - at) / 60)), unit)}
    blk = rd.get("ingame_testq")
    if not isinstance(blk, dict):
        return {STEVE_TAKEABLE_KEY: U("no ingame_testq block in %s (%s)" % (
            p, rd.get("ingame_testq_error") or "the dispatch tick did not write it"), unit)}
    # every mod the stage records put at in_game must be in the block: one missing is not read, never "nothing waits"
    unread = []
    for sr in sorted(glob.glob(str(data_clone() / "design" / "concepts" / "*" / "version" / "stage_record.json"))):
        mod = Path(sr).parent.parent.name
        rec = read_json(sr)
        if not isinstance(rec, dict):
            unread.append("%s (stage record unreadable)" % mod)
        elif rec.get("stage") == "in_game" and mod not in blk:
            unread.append("%s (at in_game, not in the dispatch reading)" % mod)
    waiting, opened, counts = {}, {}, {}
    for mod, e in sorted(blk.items()):
        if not isinstance(e, dict) or e.get("error") or e.get("hold_unreadable"):
            unread.append("%s (%s)" % (mod, (e or {}).get("error") if isinstance(e, dict) and e.get("error")
                                       else "the owner's hold unreadable"))
            continue
        if e.get("held") or e.get("blocked") or e.get("owed") == "exit met":
            continue        # his hold, a blocked visit, a visit whose exit is met: nothing to take
        ch = {k: [c for c in v if isinstance(c, str)] for k, v in (e.get("checks") or {}).items() if isinstance(v, list)}
        ch = {k: v for k, v in ch.items() if v}
        if not ch:
            continue
        t0 = epoch(e.get("opened"))
        if t0 is None:
            unread.append("%s (visit opening %r unreadable)" % (mod, e.get("opened")))
            continue
        waiting[mod], opened[mod] = ch, t0
    # the queue: what runs on the lane and what waits ready for it
    jobs = []
    for state in ("running", "pending"):
        d = qhome() / state
        try:
            names = sorted(n for n in os.listdir(d) if n.endswith(".json"))
        except OSError as e:
            return {STEVE_TAKEABLE_KEY: U("testq %s unreadable: %s" % (d, e), unit)}
        for n in names:
            r = read_json(d / n)
            j = (r.get("job") if state == "running" else r) if isinstance(r, dict) else None
            if not isinstance(j, dict):
                if state == "running":      # an unreadable running job could be the lane's work: cannot say idle
                    return {STEVE_TAKEABLE_KEY: U("testq running record %s unreadable" % n, unit)}
                continue
            host = (r.get("host") if state == "running" else j.get("host")) or "stevedesktop"   # testq.host_of
            jobs.append((state, host, j))

    def chains(j):
        s = j.get("selector") if isinstance(j.get("selector"), dict) else {}
        return {c for c in s.get("chains") or [] if isinstance(c, str)}

    def on_waiting(j, w):
        return set().union(*w.get(j.get("mod"), {}).values()) & chains(j) if j.get("mod") in w else set()

    def ready(j):           # testq.ready: no owner gate, its not_before passed, on the Steve lane
        nb = epoch(j.get("not_before")) if j.get("not_before") else None
        return not j.get("owner_gate") and (nb is None or nb <= now) and j.get("lane") in ("stevedesktop", "any")

    # a check whose job waits on the owner's gate is his, not the lane's: it does not wait for the lane
    for state, host, j in jobs:
        if state == "pending" and j.get("owner_gate") and j.get("mod") in waiting:
            g = chains(j)
            waiting[j["mod"]] = {k: v for k, v in waiting[j["mod"]].items() if not (set(v) & g)}
    # a check is drained when each of its chains ran DONE for the mod since the visit opened
    bad = list(ctx.get("steve_jobs_bad") or [])
    since = min(opened.values()) if opened else now - 7 * DAY
    done = ctx.get("steve_jobs") if since >= now - 7 * DAY and ctx.get("steve_jobs") is not None else None
    if done is None:
        done = done_jobs(min(since, now - 7 * DAY), bad, now)
    ran = {}
    for fin, d in done:
        j = d.get("job") or {}
        if outcome_of(d) == "DONE" and j.get("mod") in opened and fin >= opened[j["mod"]]:
            ran.setdefault(j["mod"], set()).update(chains(j))
    for mod in list(waiting):
        waiting[mod] = {k: v for k, v in waiting[mod].items() if not set(v) <= ran.get(mod, set())}
        if not waiting[mod]:
            del waiting[mod]
    counts = {m: len(v) for m, v in waiting.items()}
    sj = read_json(qhome() / "steward.json")
    sj = sj if isinstance(sj, dict) else {}
    steward = "%s%s" % (sj.get("state") or "unread", " (%s)" % sj["reason"] if sj.get("reason") else "")
    # either of the lane's games (testq.STEVE, testq.STEVE2): a visit job running on Steve2 is the lane's work too
    lane_hosts = ("stevedesktop", "stevedesktop.b")
    work = [(state, j) for state, host, j in jobs if host in lane_hosts and (state == "running" or ready(j))
            and (j.get("requested_by") != FILLER_BY or on_waiting(j, waiting))]
    if work:
        state, j = work[0]
        return {STEVE_TAKEABLE_KEY: M(0, unit, state="busy", job=j.get("id"), by=j.get("requested_by"),
                                      job_mod=j.get("mod"), job_state=state, waiting=counts)}
    if not waiting:
        if unread:
            return {STEVE_TAKEABLE_KEY: U("nothing known waits, but not read: %s" % "; ".join(unread[:4]), unit)}
        return {STEVE_TAKEABLE_KEY: M(0, unit, state="quiet", steward=steward)}
    # the clock: the later of the earliest waiting visit's opening and the last finish of a lane job that was work
    start = min(opened[m] for m in waiting)
    for fin, d in done:
        j = d.get("job") or {}
        h = d.get("host") or j.get("host") or "stevedesktop"
        if h in lane_hosts and fin > start and (j.get("requested_by") != FILLER_BY or on_waiting(j, waiting)):
            start = fin
    v = round(max(0.0, now - start) / 60.0, 1)
    run = [j for state, host, j in jobs if state == "running" and host in lane_hosts]
    said = "SteveDesktop %s for %.0f min, %s; %s waiting with a testq block (%s)" % (
        "on filler %s (%s)" % (run[0].get("id"), run[0].get("mod")) if run else "idle", v, steward,
        sum(counts.values()), ", ".join("%s %d" % (m, n) for m, n in sorted(counts.items())))
    x = dict(state="waiting", waiting=counts, steward=steward, running=run[0].get("id") if run else None,
             since=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start)), said=said,
             first={m: sorted(w)[:3] for m, w in sorted(waiting.items())})
    if unread:
        x["unread"] = unread[:6]
    if bad:
        return {STEVE_TAKEABLE_KEY: E(v, "%d done record(s) unreadable (%s): a check counted waiting may have run" % (
            len(bad), ", ".join(bad[:3])), unit, **x)}
    return {STEVE_TAKEABLE_KEY: M(v, unit, **x)}


def c_steve_all(now, rules, ctx):
    """The seat probe starts first, beside its siblings (STEVE_SEATS_FIX_SIBLINGS_EAT_THE_BEAT): run after them, a
    c_steve that read testq's done history for the whole 15 s beat left it <SEAT_PROBE_MIN_S, so it returned no
    reading every beat and STEVE_SEATS stayed quiet through an outage. Its budget is the beat's, not what is left."""
    cfg = rules.get("steve_seats")
    box, t = {}, None
    if cfg:
        def run():
            try:
                box["r"] = steve_seat_probe(cfg)
            except BaseException as e:  # noqa: BLE001  raised again on the pass's own thread below
                box["e"] = e
        t = threading.Thread(target=run, name="steve_seat_probe", daemon=True)
        t.start()
    try:
        out = c_steve(now, rules, ctx)
        try:        # after c_steve: it reads ctx["steve_jobs"], the week's done records c_steve already read
            out.update(c_steve_takeable(now, rules, ctx))
        except Exception as e:      # noqa: BLE001  this reading failing never costs the family's other points
            out[STEVE_TAKEABLE_KEY] = U("%s: %s" % (type(e).__name__, e), "min")
    finally:
        if t is not None:
            t.join()        # bounded: the probe's ssh times out inside the beat (or at 30 s outside one)
    if t is not None:
        if "e" in box:
            raise box["e"]
        out.update(c_steve_seats(now, rules, ctx, probed=box["r"]))
    return out


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def fail_count_unreadable(d):
    """A FAIL count that is there and no number (a string "0" is truthy) cannot say whether the job caught anything."""
    counts = (d.get("result") or {}).get("counts")
    return isinstance(counts, dict) and counts.get("FAIL") is not None and not is_num(counts["FAIL"])


def caught(d, closes, close_after_h):
    """A testq job caught something: a FAIL row, a finding it filed, or an item it ran closed within the window."""
    res = d.get("result") or {}
    counts, ing = res.get("counts"), d.get("ingested")
    if isinstance(counts, dict) and is_num(counts.get("FAIL")) and counts["FAIL"] > 0:
        return True
    groups = ing.get("groups") if isinstance(ing, dict) else None
    groups = groups if isinstance(groups, dict) else {}
    if any(g.get("findings") for g in groups.values() if isinstance(g, dict)):
        return True
    fin = epoch(d.get("finished") or res.get("finished")) or 0
    item = (d.get("job") or {}).get("item")
    items = set(groups) | ({item} if isinstance(item, str) else set())
    return any(fin <= c <= fin + close_after_h * HOUR for i in items if i for c in closes.get(i, ()))


def c_testing(now, rules, ctx):
    out = {}
    jobs = ctx.get("steve_jobs")
    bad = ctx.get("steve_jobs_bad")
    if jobs is None:
        bad = []
        jobs = done_jobs(now - 7 * DAY, bad, now)
    bad = bad or []
    # RIMMANDRAKE_RENAME_INGEST_REPAIR_ITEMS_MINT_REFUSES_THEM: ingest stamps a record `ingested` with an `error` once it
    # stops retrying; nothing read that, and 10 harness repairs were lost over 10 days without a sign
    lost = sorted(((d.get("job") or {}).get("id") or "?", str(d["ingested"]["error"])) for _, d in jobs
                  if isinstance(d.get("ingested"), dict) and d["ingested"].get("error"))
    gave = [j for j, _ in lost]
    said = "; ".join("%s: %s" % (j, err) for j, err in lost[:3])
    if bad:
        out["testing.ingest_gave_up_7d"] = E(len(gave), "%d done record(s) unreadable: a floor" % len(bad),
                                             "testq records ingest gave up on, 7 d", said=said, jobs=gave)
    else:
        out["testing.ingest_gave_up_7d"] = M(len(gave), "testq records ingest gave up on, 7 d", said=said, jobs=gave)
    closes = ctx.get("closes")
    if closes is None:      # costs the Steve half only: Archmagi's day records do not need the ledger
        out["testing.steve_nothing_h_7d"] = U("the ledger was not readable, so closes after a run are unknown")
    else:
        ch = rules["testing"]["close_after_h"]
        steve_h, steve_n, unk, young, young_h, settled = 0.0, 0, 0, 0, 0.0, 0
        for fin, d in jobs:
            st = epoch((d.get("result") or {}).get("started"))
            if st is None or fin - st <= 0 or not outcome_of(d) or fail_count_unreadable(d):
                unk += 1        # no span, or no outcome to say whether it caught anything
                continue
            if now - fin < ch * HOUR:       # its close window is still open: told beside the reading, never summed into it
                if not caught(d, closes, ch):
                    young += 1
                    young_h += (fin - st) / HOUR
                continue
            settled += 1
            if not caught(d, closes, ch):
                steve_h += (fin - st) / HOUR
                steve_n += 1
        if jobs and (unk or bad or not settled):
            out["testing.steve_nothing_h_7d"] = E(round(steve_h, 2), "%d of %d jobs have no start time or outcome (not counted); %d "
                                                  "settled, %d inside their %d h close window; %d unreadable" % (
                                                      unk, len(jobs), settled, young, ch, len(bad)),
                                                  "busy h on jobs that caught nothing, 7 d", jobs=len(jobs), settled=settled,
                                                  nothing_jobs=steve_n, no_span=unk, young=young, young_h=round(young_h, 2))
        elif jobs:
            out["testing.steve_nothing_h_7d"] = M(round(steve_h, 2), "busy h on jobs that caught nothing, 7 d", jobs=len(jobs),
                                                  nothing_jobs=steve_n, no_span=unk, settled=settled, young=young,
                                                  young_h=round(young_h, 2),
                                                  rule="no FAIL, no finding, no close of a run item within %d h" % ch)
        else:
            out["testing.steve_nothing_h_7d"] = U("no testq done record in 7 d")
    hist = Path(os.environ.get("RM_TESTING_METRICS_DIR", "/mnt/d/ClaudeWork/rimmandrake/testing_metrics")) / "history.jsonl"
    days, torn = {}, []
    try:
        with open(hist, encoding="utf-8") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except ValueError:
                    if line.strip():    # the day it names, if it still does: a torn row may have held that day's update
                        m = re.search(r'"day":\s*"([^"]*)"', line)
                        torn.append(m.group(1) if m else None)
                    continue
                if isinstance(r, dict) and isinstance(r.get("day"), str):
                    days[r["day"]] = r          # the last record of each day wins
    except OSError:
        days = {}
    lo = time.strftime("%Y-%m-%d", time.localtime(now - 7 * DAY))
    today = time.strftime("%Y-%m-%d", time.localtime(now))
    ah, adays, soft = 0.0, 0, 0
    blind = sum(1 for d in torn if d is None or d > lo)
    for day, r in sorted(days.items()):
        if not day or day <= lo or not isinstance(r, dict):
            continue
        if day > today or not re.fullmatch(r"\d{4}-\d\d-\d\d", day):
            blind += 1          # a day that has not happened, or is no date, cannot stand in for one that has
            continue
        a = _obj(_obj(r.get("machines")).get("archmagi"))      # a bad row reads as a blind day, the loop goes on
        est = []

        def val(x):
            # a value the day record itself marks UNMEASURED is unknown, never a 0; ESTIMATE taints the day
            if isinstance(x, dict):
                m = x.get("m", "MEASURED")
                if m == "ESTIMATE":
                    est.append(1)
                return x.get("v") if m in ("MEASURED", "ESTIMATE") else None
            return x
        vals = {k: val(a.get(k)) for k in ("busy_pct", "window_h", "findings", "closed_after_pass", "regressions")}
        vals["mod_fails"] = val(_obj(a.get("fail_split")).get("mod"))
        if not all(is_num(vals[k]) and finite(vals[k]) for k in ("busy_pct", "window_h")):
            blind += 1
            continue
        sig = [vals[k] for k in ("findings", "closed_after_pass", "regressions", "mod_fails")]
        if any(v is not None and not (is_num(v) and finite(v)) for v in sig):
            blind += 1          # a counter that is no number (a string "0" is truthy) says nothing about the day
            continue
        if all(v is None for v in sig):
            blind += 1          # busy but whether it caught anything is unknown: not "caught nothing"
            continue
        adays += 1
        if not any(sig):
            if any(v is None for v in sig) or est:
                soft += 1       # a "caught nothing" day with an unseen or estimated counter is provisional
            ah += vals["busy_pct"] / 100.0 * vals["window_h"]
        elif est:
            soft += 1
    if adays and not blind and not soft and adays >= 7:
        out["testing.archmagi_nothing_h_7d"] = M(round(ah, 2), "busy h on days that caught nothing, 7 d (day grain)",
                                                 days=adays)
    elif adays:
        out["testing.archmagi_nothing_h_7d"] = E(round(ah, 2), "%d of 7 days readable (%d blind: counted 0; %d with an "
                                                 "unseen or estimated counter)" % (adays, blind, soft),
                                                 "busy h on days that caught nothing, 7 d (day grain)", days=adays,
                                                 blind_days=blind, soft_days=soft)
    else:
        out["testing.archmagi_nothing_h_7d"] = U("no testing_metrics day record in 7 d (%s)" % hist)
    parts = [out[k] for k in ("testing.steve_nothing_h_7d", "testing.archmagi_nothing_h_7d")]
    if all(p["m"] == "MEASURED" for p in parts):
        out["testing.nothing_h_7d"] = M(round(sum(p["v"] for p in parts), 2), "test h catching nothing, 7 d (v3 <= 18)")
    elif all(p["m"] in ("MEASURED", "ESTIMATE") for p in parts):
        out["testing.nothing_h_7d"] = E(round(sum(p["v"] for p in parts), 2), "; ".join(
            p["why"] for p in parts if p["m"] == "ESTIMATE"), "test h catching nothing, 7 d (v3 <= 18)")
    else:
        out["testing.nothing_h_7d"] = U("a part is UNMEASURED: " + "; ".join(p.get("why", "") for p in parts
                                                                              if p["m"] != "MEASURED"))
    out.update(nightly_news(now, ctx))
    out.update(nightly_catchup_reading())
    return out


def nightly_held():
    """The owner, by card 2026-11-15: the nightly checks finished mods only and waits, stopped, until one has passed
    (nightly_scope.py): while timers_guard's finished-mod hold waits. Pinned by RM_NIGHTLY_HELD=0|1 in the selftests."""
    if os.environ.get("RM_NIGHTLY_HELD") in ("0", "1"):
        return os.environ["RM_NIGHTLY_HELD"] == "1"
    import timers_guard
    return timers_guard.hold_waits("finished-mod")


HELD_SAID = "nightly held: no mod has a passed Design Version (owner by card 2026-11-15, nightly_scope.py)"


def held_nightly(keys, state=None):
    """While the nightly waits: every nightly reading 0 (a held reading is no outage), and every build-cop group the
    alarms still hold reads 0, so it clears."""
    out = {k: M(0, "nightly held", said=HELD_SAID) for k in keys}
    if state is None:
        p = ops_dir() / "alarms.json"
        state = read_json(p) if p.exists() else {}
    for aid in (state if isinstance(state, dict) else {}):
        if aid.startswith("NIGHTLY_RED:testing.red_"):
            out["testing.red_" + aid.split(":testing.red_", 1)[1]] = M(0, "nightly reds with one first error line, no entry parking them",
                                          said=HELD_SAID)
    out["testing.nightly_reds_rerun_green"] = M(0, "nightly red groups green on one rerun", said=HELD_SAID)
    return out


def nightly_catchup_reading():
    """nightly_catchup.py's verdict: 1 when a night stopped being retried, so what the nightly feeds is reading an old night.
    Its age is deadman_check's; a reading that cannot be read holds the alarm."""
    if nightly_held():
        return {"testing.nightly_gave_up": M(0, "nights the sweep stopped being retried", said=HELD_SAID)}
    p = ops_dir() / "nightly_catchup.json"
    try:
        r = json.loads(p.read_text(encoding="utf-8"))
        st = r["state"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        return {"testing.nightly_gave_up": U("%s: %s" % (type(e).__name__, str(e)))}
    return {"testing.nightly_gave_up": M(1 if st in ("gave_up", "start_failed") else 0, "nights the sweep stopped being retried",
                                         night=r.get("night"), said=r.get("why", ""))}


def nightly_news(now, ctx):
    """TE1: the nightly's news, the only part of it that alarms (known_reds.py). A blind reading holds the alarm."""
    import known_reds
    keys = ("testing.nightly_news", "testing.nightly_known_reds", "testing.nightly_unparked_reds", "testing.nightly_reds_overdue")
    if nightly_held():
        return held_nightly(keys)
    try:
        v = known_reds.measure(ctx.get("open_ids"), now, with_cop=True)
    except Exception as e:  # noqa: BLE001  a list that cannot be read costs these readings, not the family's
        v = {"why": "%s: %s" % (type(e).__name__, str(e))}
    if v.get("why"):
        return {k: U(v["why"]) for k in keys}
    c = v["cop"]
    # news is the list's own faults (entries past their age, bad entries): a red no entry parks is a build-cop group
    lnews = [n for n in v["news"] if not n.startswith("red, not listed: ")]
    unparked = known_reds.uncovered(v)
    out = {keys[0]: M(len(lnews), "known-red list entries past their age, and bad entries", night=v["night"],
                      said="; ".join(lnews[:3]), news=lnews[:30], reds=len(v["reds"])),
           keys[1]: M(len(v["listed"]), "nightly reds on the known-red list", night=v["night"], cured=v["cured"][:30]),
           keys[2]: M(len(unparked), "nightly reds no known-red entry parks", night=v["night"], groups=len(c["groups"]),
                      detail_read=c["detail_read"], deleted=v.get("deleted", [])[:30]),
           keys[3]: M(len(c["overdue"]), "nightly reds red past their fix deadline, owned or not", night=v["night"],
                      said=c["overdue_said"], news=c["overdue"][:30])}
    # a compose pass (the metronome's sense beat, 15 s) never reruns: it reads the verdicts `rerun-reds` paid for, and
    # a group not rerun yet reads "later" (held, files nothing), as a pass out of budget does
    out.update(red_groups(c, v["night"], budget=0 if ctx.get("no_reruns") else None, ctx=ctx))
    return out


def rerun_reds(now=None, rules=None):
    """`ops_watch.py rerun-reds` (rm-ops-reds.timer): the NIGHTLY_REDS_FIX_RERUN_BEFORE_PAYING reruns, out of the
    metronome's sense beat, which cannot fit one (a group's rerun takes ~17 s). It reads the night and its red groups
    as a pass does (the flow collector for the open ids) and reruns each group a pass would file, within
    selftest.red_rerun_budget_s, then verifies one closed fix for a held group. Each verdict goes in nightly_rerun.json;
    it files nothing and writes no status.
    Its own lock, so a sense pass is never Busy behind a rerun."""
    import fcntl
    if nightly_held():
        return "rerun-reds: " + HELD_SAID
    now = now or time.time()
    rules = rules or load_rules()
    ops_dir().mkdir(parents=True, exist_ok=True)
    with open(ops_dir() / "rerun.lock", "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Busy("another rerun-reds holds %s" % (ops_dir() / "rerun.lock"))
        ctx = {"verify_held": True}
        c_flow(now, rules, ctx)
        pts = nightly_news(now, ctx)
    g = _obj(read_json(rerun_path()))
    return "rerun-reds: night %s, %d group verdict(s) kept, %d green; %d group reading(s)" % (
        g.get("night"), len(g.get("groups") or {}), sum(1 for e in (g.get("groups") or {}).values()
                                                         if isinstance(e, dict) and e.get("verdict") == "green"),
        sum(1 for k in pts if k.startswith("testing.red_")))


def red_subject(tests):
    """A group's item name words, from its first test's file: selftest_arena_judge.py -> ARENA_JUDGE; a bare
    selftest.py takes its folder's name (skills/generating-rimworld-sprites/scripts/selftest.py -> GENERATING_...)."""
    if not tests:
        return None
    path = Path(sorted(tests)[0])
    stem = re.sub(r"^selftest_?|_?selftest$", "", path.stem)
    if not stem:
        stem = next((d for d in reversed(path.parent.parts) if d.lower() not in ("scripts", "selftest", "utils", "src")), "")
    words = [w for w in re.sub(r"[^A-Za-z0-9]+", "_", stem).upper().split("_") if w][:4]
    return "_".join(words) if words and words[0][0].isalpha() else None


def rerun_path() -> Path:
    return ops_dir() / "nightly_rerun.json"


def _git(root, *args, timeout=60):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError("git %s: rc %d %s" % (" ".join(args), r.returncode, (r.stderr or "").strip()))
    return r.stdout.strip()


def rerun_root() -> Path:
    """The dispatch clone testq-tick already pulls, used for reruns and origin/main ledger reads."""
    return Path(os.environ.get("RM_OPS_RERUN_ROOT", "/home/mandrake/rm/dispatch"))


def rerun_tree_dirty(root):
    """-> why this checkout is not origin/main's code (None when it is). HEAD == origin/main is not the code that runs:
    a tracked edit anywhere, an untracked file under src/, or an untracked *.py anywhere (a skill's selftest imports its
    untracked sibling: CD3 #1) reruns the working tree, and a green from it would hide a red main. Other untracked
    files (the ledger's item stubs the dispatch clone always carries) run nothing and do not count."""
    try:
        dirty = (_git(root, "status", "--porcelain", "--untracked-files=no") + "\n"
                 + _git(root, "status", "--porcelain", "--untracked-files=all", "--", "src", ":(glob)**/*.py")
                 ).split("\n")
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as e:
        return "git status: %s" % str(e)
    dirty = sorted({ln.split(None, 1)[-1] for ln in dirty if ln.strip()})    # _git strips the first " M"
    return "working tree differs from origin/main: %s" % ", ".join(dirty[:3]) if dirty else None


def red_launch_checks(pt):
    """-> the `## launch-checks` block a fixer item filed from a red group carries (`must-fail: <its rerun>`: a fixer whose
    red already passes is refused at launch, GATE_FIRST, RIMMANDRAKE_RUN_LAUNCH_CHECKS_FIVE_STEWARDS_HIT_GATES), or None
    for an alarm that names no tests."""
    tests = ((pt or {}).get("x") or {}).get("tests")
    if not tests or not isinstance(tests, list):
        return None
    rimflow = str(Path(__file__).resolve().parents[1] / "rimflow")
    if rimflow not in sys.path:
        sys.path.insert(0, rimflow)
    import launch_checks
    return launch_checks.block_for("fix_red", cmd="python3 src/RimMandrake/Utils/run_selftests.py --only "
                                   + " ".join(shlex.quote(str(t)) for t in tests))


def rerun_at_main(tests, timeout, root=None, *, fix=None):
    """NIGHTLY_REDS_FIX_RERUN_BEFORE_PAYING: one plain rerun (run_selftests --only, no LLM) of a red group's tests in
    this checkout, brought to origin/main first by a fast-forward pull (as testq-tick/testq-sweep already do to the
    dispatch clone ops_watch runs from; it trails origin/main by minutes). -> (verdict, said, sha): verdict green
    (every test ran and passed), red, gone (every test was deleted at origin/main: nothing left to be red, files
    nothing) or unmeasured (could not rerun at origin/main: the group files as before).
    Existence is judged AFTER the pull, at origin/main, and "gone" needs git to show the deletion: a path the history
    never held (a parse bug) stays unmeasured. A group partly deleted reruns what is left (NIGHTLY_COP_FIX_RED_WARIWE_XVFM_WYEK:
    the arena trial's selftest_arena_prompt_rewrites.py, deleted by owner card, refiled because the old check ran
    before the pull and read the missing file as unmeasured). For a closed fix, require that commit and every test,
    and force a fresh run."""
    root = Path(root) if root else rerun_root()
    try:
        _git(root, "pull", "-q", "--ff-only", "origin", "main", timeout=90)
        head, main = _git(root, "rev-parse", "HEAD"), _git(root, "rev-parse", "origin/main")
        if fix:
            _git(root, "merge-base", "--is-ancestor", fix, head)
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as e:
        return "unmeasured", "git: %s" % str(e), None
    if head != main:
        return "unmeasured", "checkout at %s, origin/main at %s" % (head[:10], main[:10]), None
    dirty = rerun_tree_dirty(root)
    if dirty:
        return "unmeasured", dirty, head
    missing = [t for t in tests if not (root / t).is_file()]
    if fix and not tests:
        return "unmeasured", "empty test group", head
    if fix and missing:
        return "unmeasured", "missing group tests: " + ", ".join(missing), head
    deleted = {}
    for t in missing:
        try:
            at = _git(root, "log", "-1", "--format=%h", "--diff-filter=D", head, "--", t)
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as e:
            return "unmeasured", "git log %s: %s" % (t, str(e)), head
        if not at:
            return "unmeasured", "not at origin/main and never deleted there: %s" % t, head
        deleted[t] = at
    tests = [t for t in tests if t not in deleted]
    if not tests:
        return "gone", "deleted at origin/main: %s" % ", ".join(
            "%s (%s)" % (Path(t).name, c) for t, c in sorted(deleted.items())[:3]), head
    argv = [sys.executable, str(root / "src/RimMandrake/Utils/run_selftests.py")]
    if fix:
        argv += ["--no-cache", "--because", "verify closed nightly-red fix"]
    argv += ["--only", *tests]
    try:
        r = subprocess.run(argv, cwd=str(root), capture_output=True, text=True, timeout=max(1, int(timeout)))
    except subprocess.TimeoutExpired:
        return "unmeasured", "rerun passed its %d s budget" % timeout, head
    except OSError as e:
        return "unmeasured", "rerun: %s" % e, head
    out = r.stdout or ""
    res = next((ln for ln in reversed(out.splitlines()) if ln.startswith("RESULT:")), "")
    if not res:
        return "unmeasured", "rerun printed no RESULT line (rc %d)" % r.returncode, head
    # the checks above held when the run began, not through it: a testq pull (or an edit) mid-run mixes two revisions
    # into one verdict (CD3 #2), so the same checks again, and a moved or dirtied checkout is never green
    try:
        after = _git(root, "rev-parse", "HEAD")
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as e:
        return "unmeasured", "git after the rerun: %s" % str(e), head
    if after != head:
        return "unmeasured", "checkout moved during the rerun: %s -> %s" % (head[:10], after[:10]), head
    dirty = rerun_tree_dirty(root)
    if dirty:
        return "unmeasured", "after the rerun: " + dirty, head
    if fix and (crash := re.search(r"^CRASH \(.*", out, re.M)):
        return "unmeasured", crash[0], head
    all_pass = not fix or sorted(re.findall(r"^PASS +[\d.]+s  (\S+)", out, re.M)) == sorted(tests)
    if r.returncode == 0 and res.startswith("RESULT: GREEN") and all_pass and "UNMEASURED (" not in out and "DROPPED:" not in out:
        return "green", res, head
    if res.startswith("RESULT: GREEN"):
        return "unmeasured", "green with tests that did not run their check", head
    return "red", res, head


class RerunGate:
    """Each new group of a night is rerun once (the verdict kept in nightly_rerun.json for that night), within the
    pass's budget. verdict(g): green / gone (files nothing), red / unmeasured (files as before), later (budget spent)."""

    def __init__(self, night, run, budget, clock=time.monotonic, *, verify_held=False):
        self.night, self.run, self.clock = night, run, clock
        self.end = clock() + budget
        self.verify_held = verify_held
        st = read_json(rerun_path()) if rerun_path().exists() else {}
        self.st = st if isinstance(st, dict) and st.get("night") == night else {"night": night, "groups": {}}
        self.dirty = False

    def verdict(self, g, fix=None):
        hit = self.st["groups"].get(g["key"])
        if hit and (not fix or hit.get("fix") == fix) and sorted(hit.get("tests", [])) == sorted(g["tests"]):
            return hit["verdict"]
        if fix:
            if not self.verify_held:
                return "later"
            # One full test window (run_selftests' default is 600 s), after the new-group budget.
            self.verify_held = False
            left, kwargs = 600, {"fix": fix}
        else:
            left, kwargs = self.end - self.clock(), {}
            if left < 15:
                return "later"
        try:
            v, said, sha = self.run(list(g["tests"]), int(left), **kwargs)
        except Exception as e:  # noqa: BLE001  a broken rerun files the group as before
            v, said, sha = "unmeasured", "%s: %s" % (type(e).__name__, str(e)), None
        self.st["groups"][g["key"]] = {"verdict": v, "said": said, "sha": sha, "tests": list(g["tests"]),
                                       "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **kwargs}
        self.dirty = True
        self.save()     # each verdict as it lands: a pass killed at its deadline keeps the reruns it paid for
        return v

    def green(self):
        """Groups that filed nothing because origin/main has no red to fix: green on the rerun, or every test gone."""
        return sorted((k, e) for k, e in self.st["groups"].items()
                      if not e.get("fix") and e.get("verdict") in ("green", "gone"))

    def save(self):
        if self.dirty:
            atomic_json(rerun_path(), self.st)
            self.dirty = False


def rerun_budget_s():
    sys.path.insert(0, str(HERE.parent / "rimflow"))
    import testing_policy as TP
    return float(TP.param("selftest.red_rerun_budget_s"))


# The rerunner red_groups uses when a caller passes none; a test swaps it for a fake (None turns the gate off).
RERUN_REDS = rerun_at_main


def red_groups(c, night, state=None, rerun="default", budget=None, ctx=None):
    """BUILD COP (known_reds.py): one testing.red_<id> reading per root-cause group of the night's unparked reds, for
    the wildcard alarm NIGHTLY_COP_FIX (one raised item per group). An absent key holds its alarm, so a group gone from
    a READ night reads 0 and clears; an unread night (the sweep is rewriting its output) emits no group and holds all.
    New groups come at most selftest.red_new_items_per_pass a pass (the unit's deadline bounds the spawns), biggest
    first; the rest are absent, so held, and come next pass.
    NIGHTLY_REDS_FIX_RERUN_BEFORE_PAYING: before a new group files, its tests rerun once at origin/main (RerunGate);
    a group green on that rerun is a flake or a launch drop and files nothing, counted in
    testing.nightly_reds_rerun_green. A held group from before its fix item closed reads 0 on a matching green proof."""
    import known_reds
    if not c.get("detail_read"):
        return {}
    run = RERUN_REDS if rerun == "default" else rerun
    ctx = ctx or {}
    gate = RerunGate(night, run, rerun_budget_s() if budget is None else budget,
                     verify_held=ctx.get("verify_held", False)) if run else None
    if state is None:
        p = ops_dir() / "alarms.json"
        state = read_json(p) if p.exists() else {}
    held = {aid.split(":", 1)[1]: row for aid, row in _obj(state).items()
            if aid.startswith("NIGHTLY_RED:testing.red_")}
    cap = known_reds.new_items_per_pass()
    out, fresh = {}, 0
    for g in c["groups"]:
        if g["key"] not in held:
            if fresh >= cap:
                continue
            if gate is not None and gate.verdict(g) in ("green", "gone", "later"):
                continue
            fresh += 1
        out[g["key"]] = M(len(g["tests"]), "nightly reds with one first error line, no entry parking them", night=night,
                          subject=red_subject(g["tests"]), said=g["said"], news=["%s (due %s)" % (t, g["due"]) for t in g["tests"][:30]], due=g["due"],
                          titled={"%s (due %s)" % (t, g["due"]): Path(t).name for t in g["tests"][:30]},
                          tests=list(g["tests"]))
    live = {g["key"] for g in c["groups"]}
    for k in sorted(held.keys() - live):
        out[k] = M(0, "nightly reds with one first error line, no entry parking them", night=night, said="green or parked")
    if gate is not None:
        for g in c["groups"]:
            k = g["key"]
            row = _obj(held.get(k))
            item = row.get("item") or row.get("name")
            fix = ctx.get("closed_fixes", {}).get(item) if isinstance(item, str) else None
            if fix and stale_for_close(out[k], ctx["closes"].get(item)) and gate.verdict(g, fix) == "green":
                sha = gate.st["groups"][k]["sha"]
                out[k] = M(0, out[k]["unit"], night=night, said="all group tests green at %s" % sha)
        gate.save()
        gr = gate.green()
        out["testing.nightly_reds_rerun_green"] = M(
            len(gr), "nightly red groups green on one rerun at origin/main (flaky or a launch drop) or deleted there, filed nothing",
            night=night, said="; ".join("%s (%s)" % (", ".join(Path(t).name for t in e["tests"][:3]), (e.get("sha") or "")[:10])
                                        for _, e in gr[:3]),
            news=["%s at %s: %s" % (t, (e.get("sha") or "")[:10], e.get("said", "")) for _, e in gr for t in e["tests"]][:30])
    return out


def scratch_runs_path() -> Path:
    return Path(os.environ.get("RM_SCRATCH_REAP_RUNS", Path.home() / ".local/state/rm-scratch-reap/runs.jsonl"))


def last_line(path, chunk=1 << 22):
    with open(path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        pos = max(0, size - chunk)
        while True:
            f.seek(pos)
            buf = f.read(size - pos)
            lines = [ln for ln in buf.split(b"\n") if ln.strip()]
            if len(lines) >= 2 or pos == 0:
                return lines[-1].decode("utf-8", "replace") if lines else None
            pos = max(0, pos - chunk)


def disk_mounts():
    env = os.environ.get("RM_OPS_DISKS")
    if env:
        # each entry on its own: a bad one reads as its own UNMEASURED disk (mount None), never the whole family lost
        out = {}
        for i, kv in enumerate(env.split(",")):
            name, sep, mnt = kv.strip().partition("=")
            out[name if re.fullmatch(r"\w+", name) else "bad%d" % i] = mnt if sep and mnt else None
        return out
    # tmp: the /tmp tmpfs (18 GB, RAM-backed); full, every selftest's mkdtemp fails ENOSPC (TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP)
    return {"root": "/", "c": "/mnt/c", "d": "/mnt/d", "tmp": "/tmp"}


SO_RANGES = ("disk.scratch_outside_cap", "disk.scratch_outside_blind")


def scratch_outside(san, now, rules):
    """disk.scratch_outside_cap (OP2): clones the pool cap cannot see, from the newest phase of the cleaner's sanity
    record. Read only. A record that is missing, torn, stale, dated ahead or without the count reads UNMEASURED and
    counts in disk.scratch_outside_blind, whose target alarms: unlike disk.scratch_dirty_*, no record is never a pass.
    Freshness is the stamp inside the file, never its mtime."""
    ms, why, phase = ranges_of(rules), need_ranges(rules, SO_RANGES), None
    limit = None if why else ms["disk.scratch_outside_cap"]["max_age_min"]
    if why is None:
        d = read_json(san)
        rows = [(r["at"], n) for n, r in (d.items() if isinstance(d, dict) else ())
                if n in ("start", "end") and isinstance(r, dict) and is_num(r.get("at")) and finite(r["at"])]
        if not rows:
            why = "sanity record missing or torn: %s" % san
        else:
            at, phase = max(rows)
            got = d[phase].get("measures")
            v = got.get("rm_scratch_clones") if isinstance(got, dict) else None
            if at > now + 300:
                why = "sanity record is dated %d s ahead of the clock" % (at - now)
            elif now - at > limit * 60:
                why = "sanity record frozen: last stamped %s, %.0f min ago, limit %g" % (iso(at), (now - at) / 60.0, limit)
            elif not is_num(v) or not finite(v) or v < 0:
                why = "sanity record holds no rm_scratch_clones at its %s: %s" % (phase, str(d[phase].get("problems")))
    if why:
        return {"disk.scratch_outside_cap": U(why, "clones"), "disk.scratch_outside_distressed": U(why),
                "disk.scratch_outside_blind": M(1, "sources not seen", cause=why)}
    pts = {"disk.scratch_outside_cap": M(v, "clones", phase=phase, at=iso(at), max_age_min=limit)}
    state = read_class(ms, "disk.scratch_outside_cap", pts)
    cause = "%s clones outside the pool cap at the %s of the reaper run of %s" % (fmt(v), phase, iso(at)) if state in ALARMED else "none"
    pts["disk.scratch_outside_distressed"] = M(int(state in ALARMED), "1 when clones pile up outside the cap", state=state, cause=cause)
    pts["disk.scratch_outside_blind"] = M(0, "sources not seen", cause="none")
    return pts


RG_RANGES = ("disk.root_fall_gb", "disk.root_fall_blind")


def grower_line(w):
    """One writer of a growth capture, as the alarm title names it: the title is cut at 160, so who comes first."""
    return "pid %s %s %s GB: %s (cwd %s)" % (w.get("pid"), w.get("unit"), w.get("gb"), str(w.get("cmd") or "")[:60],
                                            w.get("cwd"))


def root_growth(sd, now, rules):
    """disk.root_fall_gb (GROWER_ALARM_WIRE_NOBODY_READS_IT): how far the root fell in disk_grower's window, from the
    newest row of growth.jsonl, which rm-scratch-pressure writes every 10 min. Distressed, the cause names the writers
    disk_grower caught in growth_capture.json at that same tick, so the grower is named while it still exists (the
    2026-10-31 and 11-04 falls went unnamed; alarms.log held the only GROWER line and nothing reads it). A row that is
    missing, torn, stale or dated ahead reads UNMEASURED and counts in disk.root_fall_blind. Read only; freshness is
    the row's own stamp."""
    ms, why = ranges_of(rules), need_ranges(rules, RG_RANGES)
    limit = None if why else ms["disk.root_fall_gb"]["max_age_min"]
    gp = sd / "growth.jsonl"
    if why is None:
        try:
            r = json.loads(last_line(gp) or "null")
            if not isinstance(r, dict):
                raise ValueError("no row")
            t, fall = r.get("t"), r.get("fall_gb")
            # OPS_ROOT_GROWER_MEASURE_CAUGHT_WRITING_QMOX: the alarm reads the fall that held for a tick (disk_grower
            # held_fall_gb), so walled-box churn reaped within a tick is not a grower; a row from before it reads fall_gb
            if "held_fall_gb" in r:
                fall = r.get("held_fall_gb")
            if not (is_num(t) and finite(t)):
                raise ValueError("the newest row has no stamp")
            if t > now + 300:
                raise ValueError("the newest row is dated %d s ahead of the clock" % (t - now))
            if now - t > limit * 60:
                raise ValueError("frozen: last row %s, %.0f min ago, limit %g" % (iso(t), (now - t) / 60.0, limit))
            if not (is_num(fall) and finite(fall)) or fall < 0:
                raise ValueError("the newest row holds no fall_gb" + (" (held_fall_gb)" if "held_fall_gb" in r else ""))
        except (OSError, ValueError) as e:
            why = "growth record %s: %s" % (gp, e)
    if why:
        return {"disk.root_fall_gb": U(why, "GB"), "disk.root_fall_distressed": U(why),
                "disk.root_fall_blind": M(1, "sources not seen", cause=why)}
    win = r.get("window_min")
    pts = {"disk.root_fall_gb": M(fall, "GB the root fell within %s min and still down a tick later" % win, at=iso(t),
                                  free_gb=r.get("free_gb"), raw_fall_gb=r.get("fall_gb"),
                                  top_writer_gb=r.get("top_writer_gb"), max_age_min=limit)}
    state = read_class(ms, "disk.root_fall_gb", pts)
    cause, writers = "none", []
    if state in ALARMED:
        cap = read_json(sd / "growth_capture.json")
        if isinstance(cap, dict) and cap.get("ts") == r.get("ts"):
            writers = [w for w in cap.get("writers") or [] if isinstance(w, dict)][:3]
            named = "; ".join(grower_line(w) for w in writers) or "no readable writer this tick (%s blind)" % cap.get("blind")
            gone = [f for f in cap.get("open_big") or [] if isinstance(f, dict) and f.get("deleted")][:1]
            named += "".join("; open deleted %s %s GB" % (f.get("path"), f.get("alloc_gb")) for f in gone)
        else:
            named = "writer unnamed: no growth_capture.json for the row of %s" % r.get("ts")
        cause = "%s; root fell %s GB in %s min (held a tick) to %s GB free at %s" % (named, fmt(fall), win, r.get("free_gb"),
                                                                                r.get("ts"))
    pts["disk.root_fall_distressed"] = M(int(state in ALARMED), "1 when the root falls fast", state=state,
                                         cause=cause, writers=writers)
    pts["disk.root_fall_blind"] = M(0, "sources not seen", cause="none")
    return pts


# WHEA (DDRIVE_PCIE_MONITOR_CORRECTED_FOR_NOW): Archmagi's D: NVMe (Kingston SFYRD4000G behind root port 0:6.3) logs
# WHEA-Logger 17, corrected PCIe AER errors, at a rising rate (6..16 a day, 2026-10-26..11-02). The System event log is
# readable without admin. Corrected = Level 3 (Warning); severe = Level 1/2 (Critical/Error) or id 18/20 (fatal), or
# 19, a corrected machine check: corrected, but the CPU, not this drive, so any one is news. Absolute path: a systemd
# user service has no /mnt/c on PATH (memwatch.py measured it). RM_OPS_WHEA_EVENTS names a file of canned lines (tests).
POWERSHELL = "/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe"
WHEA_DAYS = 8
WHEA_SEVERE_IDS = (18, 19, 20)
WHEA_SKEW_S = 300      # a row this far ahead of WSL's clock still counts; further ahead, the reading is blind
WHEA_PS = ("$ErrorActionPreference='Stop'; try { $e = @(Get-WinEvent -FilterHashtable @{LogName='System'; "
           "ProviderName='Microsoft-Windows-WHEA-Logger'; StartTime=(Get-Date).AddDays(-%d)}) } catch { "
           "if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') { $e = @() } else { 'ERR|' + $_.Exception.Message; exit 3 } }; "
           "foreach ($x in $e) { 'EV|{0}|{1}|{2}' -f $x.Id, $x.Level, $x.TimeCreated.ToUniversalTime().ToString('o') }; 'END|' + $e.Count")


def whea_lines():
    """-> the collector's raw lines: EV|id|level|iso-utc per event, then END|n. Raises OSError when it cannot ask."""
    canned = os.environ.get("RM_OPS_WHEA_EVENTS")
    if canned:
        return Path(canned).read_text(encoding="utf-8").splitlines()
    if not os.path.exists(POWERSHELL):
        raise OSError("no %s on this host (no Windows to ask)" % POWERSHELL)
    try:
        r = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", WHEA_PS % WHEA_DAYS],
                           capture_output=True, text=True, timeout=60)
    except (subprocess.TimeoutExpired, OSError) as e:
        raise OSError("powershell: %s" % e)
    out = (r.stdout or "").replace("\r", "").splitlines()
    if r.returncode != 0:
        raise OSError("powershell exit %d: %s" % (r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()))
    return out


def whea_parse(lines, now):
    """-> (events [(id, level, epoch)], why-not or None). A run with no END line, an END count that disagrees with the
    rows, or a row that will not parse is a blind reading: zero is claimed only when Windows said zero."""
    evs, end = [], None
    for ln in lines:
        f = ln.strip().split("|")
        if f[0] == "ERR":
            return [], "event log: " + "|".join(f[1:])
        if f[0] == "END":
            if end is not None:
                return [], "a second END line %r: the collector prints one" % ln
            end = f[1] if len(f) > 1 else ""
        elif f[0] == "EV":
            try:
                t = epoch(f[3])
                if t is None:
                    raise ValueError(f[3])
                evs.append((int(f[1]), int(f[2]), t))
            except (IndexError, ValueError):
                return [], "unreadable event row %r" % ln
        elif f[0]:
            return [], "unexpected line %r" % ln
    if end is None:
        return [], "no END line: the query did not finish"
    if not re.fullmatch(r"[0-9]+", end) or int(end) != len(evs):
        return [], "END says %r, %d rows read" % (end, len(evs))
    return evs, None


def whea_reading(now):
    """disk.whea_corrected_24h, disk.whea_severe_24h (rolling 24 h) and disk.whea_blind, with per-UTC-day counts of the
    last WHEA_DAYS days on the corrected point, so the daily curve is one read."""
    try:
        evs, why = whea_parse(whea_lines(), now)
    except (OSError, UnicodeError) as e:     # undecodable output is a blind reading, never a crash
        evs, why = [], str(e)
    ahead = max((e[2] - now for e in evs), default=0)
    if not why and ahead > WHEA_SKEW_S:
        # Windows' clock runs ahead of this one: the 24 h window cannot be placed, and dropping the row read a fatal as 0
        why = "a row dated %d s ahead of this clock (allowance %d s): the clocks disagree" % (ahead, WHEA_SKEW_S)
    if why:
        return {"disk.whea_corrected_24h": U(why, "events"), "disk.whea_severe_24h": U(why, "events"),
                "disk.whea_blind": M(1, "WHEA sources not seen", cause="WHEA count blind: " + why)}
    recent = [e for e in evs if now - DAY <= e[2] <= now + WHEA_SKEW_S]
    severe = [e for e in recent if e[1] in (1, 2) or e[0] in WHEA_SEVERE_IDS]
    corrected = [e for e in recent if e not in severe]
    by_day = {}
    for i, lv, t in evs:
        if not (i in WHEA_SEVERE_IDS or lv in (1, 2)):
            d = time.strftime("%Y-%m-%d", time.gmtime(t))
            by_day[d] = by_day.get(d, 0) + 1
    ids = sorted({e[0] for e in severe})
    newest = iso(max(e[2] for e in evs)) if evs else None
    return {"disk.whea_corrected_24h": M(len(corrected), "corrected WHEA hardware errors in 24 h", by_day_utc=by_day,
                                         newest=newest, days=WHEA_DAYS,
                                         cause="%d corrected WHEA errors in 24 h (by UTC day %s)" % (len(corrected), by_day)),
            "disk.whea_severe_24h": M(len(severe), "fatal or CPU WHEA errors in 24 h", ids=ids,
                                      cause="%d WHEA event(s) id %s (fatal 18/20, CPU machine check 19, or Level Error) in 24 h"
                                      % (len(severe), ids)),
            "disk.whea_blind": M(0, "WHEA sources not seen", cause="none")}


def c_disk(now, rules, ctx):
    # The three slow reads wait on subprocesses (find over the pool, git over the scratch clones and the seat and role
    # clones). They start first and overlap the rest: in series they took 21-29 s at load 45 on 2026-11-22, past the
    # sense phase's 15 s kill (RIMMANDRAKE_UNBLIND_OPS_DISK_FAMILY_TWENTY_OVERRUNS_STRAIGHT).
    from concurrent.futures import ThreadPoolExecutor
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    ex = ThreadPoolExecutor(max_workers=3)
    try:
        import scratch_clone
        try:
            import scratch_reap
            scratch_reap.mirror_tips()     # its cache fills by appending: fill it before scratch_stranded's threads read it
        except Exception:  # noqa: BLE001 - scratch_stranded raises the same cause in its own future, read below
            pass
        f_pool = ex.submit(scratch_clone.pool_reading, cached_sizes=True)     # sizes up to SIZE_MAX_AGE_S old
        f_scr = ex.submit(scratch_clone.scratch_stranded)
    except Exception as e:  # noqa: BLE001 - an import that fails is the pool alarm below, never silence
        f_pool = f_scr = e
    f_seat = ex.submit(seat_dirt_reading)
    try:
        return _c_disk(now, rules, ctx, f_pool, f_scr, f_seat)
    finally:
        ex.shutdown(wait=True)


def _c_disk(now, rules, ctx, f_pool, f_scr, f_seat):
    out = {}
    for name, mnt in disk_mounts().items():
        try:
            if mnt is None:
                raise OSError("bad RM_OPS_DISKS entry (want name=mount)")
            if mnt.startswith("/mnt/") and not os.path.ismount(mnt):
                raise OSError("not a mount point (the drive is not mounted; df would read the parent volume)")
            du = shutil.disk_usage(mnt)
            if du.total <= 0:
                raise OSError("total 0")
            out["disk.%s_free_gb" % name] = M(round(du.free / 1e9, 1), "GB free on %s" % mnt,
                                             total_gb=round(du.total / 1e9, 1))
            out["disk.%s_used_gb" % name] = M(round(du.used / 1e9, 1), "GB used on %s" % mnt)
            if name == "tmp":       # a small volume: the share is the honest line, GB free the absolute floor
                out["disk.tmp_used_pct"] = M(round(100 * du.used / du.total, 1), "% used on " + mnt)
        except OSError as e:
            out["disk.%s_free_gb" % name] = U("%s: %s" % (mnt or name, e))
            out["disk.%s_used_gb" % name] = U("%s: %s" % (mnt or name, e))
            if name == "tmp":
                out["disk.tmp_used_pct"] = U("%s: %s" % (mnt or name, e))
    p = scratch_runs_path()
    try:
        r = json.loads(last_line(p) or "null")
        t = epoch(r["ts"])
        age_h = (now - t) / HOUR
        tot, nob = {}, 0
        rows = r.get("rows")
        if not rows:
            raise ValueError("the reaper's last run has no rows (a scan that saw nothing is not 0 GB)")
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("verdict"), str):
                nob += 1
                continue
            if row.get("verdict") != "DELETED":
                if not (is_num(row.get("bytes")) and finite(row["bytes"])):
                    nob += 1
                    continue
                tot[row.get("verdict")] = tot.get(row.get("verdict"), 0) + row["bytes"]
        if age_h < -5 / 60:
            raise ValueError("the reaper's last run is dated in the future (%s)" % r["ts"])
        if age_h > 3:
            raise ValueError("the reaper's last run is %.1f h old (%s)" % (age_h, r["ts"]))
        mk = M if not nob else (lambda v, u, **x: E(v, "%d scratch row(s) with no byte count (not counted)" % nob, u, **x))
        out["disk.scratch_total_gb"] = mk(round(sum(tot.values()) / 1e9, 1), "GB of agent scratch the reaper sees",
                                         run=r["ts"], young_gb=round(tot.get("YOUNG", 0) / 1e9, 1),
                                         refuse_gb=round(tot.get("REFUSE", 0) / 1e9, 1))
        out["disk.scratch_refused_gb"] = mk(round(tot.get("REFUSE", 0) / 1e9, 1), "GB old enough to reap but refused")
    except (OSError, ValueError, KeyError, TypeError) as e:
        out["disk.scratch_total_gb"] = U("scratch_reap runs.jsonl (%s): %s" % (p, e))
        out["disk.scratch_refused_gb"] = U("scratch_reap runs.jsonl: %s" % e)
    # The expiry's own record. A missing or torn record is the alarm, not silence: nothing proves the expiry runs.
    rec = p.with_name("last_run.json")
    try:
        d = json.loads(rec.read_text())
        ok_t = d.get("last_ok_epoch") if isinstance(d, dict) else None
        if not (is_num(ok_t) and finite(ok_t)):
            raise ValueError("no successful run on record")
        if ok_t > now + 900:    # one pass of slack, as `now` is taken before this runs; a record from a fast clock would hold the alarm off for as long as it was fast
            raise ValueError("last clean run is in the future")
        out["disk.scratch_ok_age_h"] = M(math.ceil((now - ok_t) / HOUR * 100) / 100, "hours since the expiry last ran clean",
                                         failures=d.get("failures"), freed_bytes=d.get("freed_bytes"))
    except (OSError, ValueError) as e:
        out["disk.scratch_ok_age_h"] = M(9999, "hours since the expiry last ran clean", why="%s: %s" % (rec, e))
    # The cleaner's own sanity at each end of its last run (CLEANER_SANITY_BUILD_SPEAKS_UP_WHEN_FILTHY). The Dispatcher
    # carries it to the Conductor log; these file or reopen its one fixed item. No record yet is a clean reading of 0:
    # disk.scratch_ok_age_h above already alarms on a cleaner that never ran.
    san = rec.with_name("sanity.json")
    out.update(scratch_dirty(san))
    out.update(scratch_outside(san, now, rules))
    out.update(root_growth(rec.parent, now, rules))
    out.update(whea_reading(now))
    # The bounded worker-clone pool (WORKER_CLONES_MONITOR_POOL_NOT_RABBITS): read live each tick, never from a cache.
    # One number alarms: clones over the cap, bytes over the cap, plus every clone holding unpushed work nobody is using,
    # in the pool or anywhere else a helper clones (rm/scratch, session dirs: LIQUIDNET_SURFACEGAP_FIX_UNLANDED_CLONES).
    # A pool that cannot be read is the alarm too (9999), not silence.
    try:
        if isinstance(f_pool, Exception):
            raise f_pool
        pr, ss = f_pool.result(), f_scr.result()
        out["disk.pool_clones"] = M(pr["count"], "worker clones in the pool (cap %d)" % pr["max_clones"])
        out["disk.pool_gb"] = M(pr["gb"], "GB the pool holds")
        # the pool's limit is the disk floor (scratch_clone.pool_admit): its margin is the reading, unreadable floor = UNMEASURED
        out["disk.pool_floor_margin_gb"] = (M(pr["margin_gb"], "GB free on / above the pool floor, after the largest clone",
                                              floor_gb=pr["floor_gb"], root_free_gb=pr["root_free_gb"])
                                            if pr.get("margin_gb") is not None else U(pr.get("floor_error") or "no floor", "GB"))
        out["disk.pool_oldest_h"] = M(pr["oldest_h"], "hours since the oldest pool clone was made")
        out["disk.pool_breach"] = M(pr["breach"] + len(ss["stranded"]), "pool breaches: over count, under the disk floor, stranded unpushed clones",
                                    stranded=pr["stranded"] + ss["stranded"], unpushed=pr["unpushed"])
    except Exception as e:
        out["disk.pool_breach"] = M(9999, "pool breaches", why="pool unreadable: %s" % str(e))
    out.update(f_seat.result())
    return out


def scratch_dirty(san):
    """disk.scratch_dirty_start/_end from the cleaner's sanity.json. Mid-run the end is the last finished run's
    (`prev_end`, marked running), never a clean 0 (RIMMANDRAKE_HOLD_SCRATCH_DIRTY_END_WHILE_CLEANER_RUNS)."""
    out = {}
    for end in ("start", "end"):
        try:
            d = json.loads(san.read_text()) if san.exists() else {}
            row = d.get(end)
            running = end == "end" and not row and isinstance(d.get("prev_end"), dict)
            row = (d["prev_end"] if running else row) or {}
            x = {"running": True} if running else {}
            out["disk.scratch_dirty_" + end] = M(len(row.get("problems") or []), "sanity problems at the %s of the last run" % end,
                                                 problems=(row.get("problems") or [])[:6],
                                                 residual=(row.get("residual") or [])[:4], **x)
        except (OSError, ValueError, AttributeError) as e:
            out["disk.scratch_dirty_" + end] = M(9999, "sanity problems at the %s of the last run" % end, why="%s: %s" % (san, e))
    return out


def seat_dirt_reading():
    """disk.seat_dirt (RIMMANDRAKE_ALARM_SEAT_CLONE_DIRT_OLDER_THAN_AN_HOUR): paths dirty for over an hour that no safe
    class covers, and safe-class paths the tidy left past seat_dirt.TIDY_LATE_MIN, in the seat clone and in every role
    clone (seat_dirt.clones; the Dispatcher's role runs and the art daemon write there:
    RIMMANDRAKE_MOVE_SEAT_CLONE_WRITERS_INTO_OWN_POOL_CLONES). A read only: the tidy that lands the safe classes fetches
    and pushes, so it runs in rm-seat-tidy.timer, never here under the sense phase's 15 s kill
    (RIMMANDRAKE_UNBLIND_OPS_DISK_FAMILY_TWENTY_OVERRUNS_STRAIGHT). Unreadable is 9999, never silence."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import seat_dirt
        from concurrent.futures import ThreadPoolExecutor
        stale, fresh, late, paths, unread = 0, 0, 0, [], []

        def one(clone):
            try:
                return seat_dirt.reading(clone)
            except Exception as e:  # noqa: BLE001 - one unreadable clone makes the whole reading unreadable below
                return e
        cl = seat_dirt.clones()
        with ThreadPoolExecutor(max_workers=max(1, len(cl))) as ex:     # each clone's reading is git subprocesses
            got = list(ex.map(one, cl))
        for clone, r in zip(cl, got):
            tag = "" if clone == seat_dirt.SEAT_CLONE else os.path.basename(clone) + ":"
            if isinstance(r, Exception):
                unread.append("%s %s" % (clone, str(r)))
                continue
            stale += r["stale"]
            fresh += r["fresh"]
            late += r.get("tidy_late", 0)
            paths += [tag + p for p in r["stale_paths"]]
        if unread:
            return {"disk.seat_dirt": M(9999, "paths dirty in the seat and role clones", why="unreadable: " + "; ".join(unread))}
        return {"disk.seat_dirt": M(stale, "paths dirty in the seat and role clones over %d min" % seat_dirt.STALE_MIN,
                                    paths=paths[:12], fresh=fresh, tidy_late=late)}
    except Exception as e:
        return {"disk.seat_dirt": M(9999, "paths dirty in the seat clone", why="unreadable: %s" % str(e))}


def systemctl_json(*args):
    r = subprocess.run(["systemctl", "--user"] + list(args) + ["-o", "json", "--no-pager"], capture_output=True,
                       text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError("systemctl %s: exit %d %s" % (" ".join(args), r.returncode, r.stderr.strip()))
    return json.loads(r.stdout or "[]")


def one_shot_units(names):
    """signal_watch.one_shots: a dead harness scope or arena run is reported by whoever started it, not a failed timer
    (SCOPE_ALARM_FIX_DEAD_SELFTEST_STILL_SHOUTS). No timer list, or no reading: nothing is excused."""
    rf = str(HERE.parent / "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import signal_watch
    try:
        timers = [t.get("unit") for t in systemctl_json("list-timers", "--all") if isinstance(t, dict)]
    except Exception:  # noqa: BLE001
        return set()
    return signal_watch.one_shots(names, timers)


BLIP_GRACE_MIN = 45     # a timer unit still failed this long after its failed run is not waiting on its next run
BLIP_DAY_FAILS = 3      # this many failed runs of one unit in 24 h is a flapping unit, never a blip


def journal_runs(unit, since_h=24, run=None):
    """-> [(t, failed)] oldest first, one row per run of `unit` in the last since_h hours, read from systemd's own lines
    (a job-start "Starting" line opens a run; JOB_RESULT=failed or a UNIT_RESULT line fails it; t is the run's last
    failure, else its start). None when the journal cannot be read: the caller then counts the failure."""
    cmd = ["journalctl", "--user", "-u", unit, "--since", "-%dh" % since_h, "-o", "json", "--no-pager"]
    try:
        r = (run or subprocess.run)(cmd, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    runs = []
    for line in r.stdout.splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if not isinstance(e, dict) or e.get("SYSLOG_IDENTIFIER") != "systemd":
            continue
        try:
            t = int(e.get("__REALTIME_TIMESTAMP")) / 1e6
        except (TypeError, ValueError):
            continue
        job = e.get("JOB_RESULT")
        if e.get("JOB_TYPE") == "start" and not job:
            runs.append([t, False, False])
        elif job == "failed" or e.get("UNIT_RESULT") not in (None, "", "success"):
            if not runs or runs[-1][2]:   # no open run (its Starting fell before the window, or a start-limit hit):
                runs.append([t, True, False])   # a failed run of its own, never painted over an earlier one
            runs[-1][:2] = [t, True]
            runs[-1][2] = job == "failed"
        elif job and runs:
            runs[-1][2] = True
    return [(x[0], x[1]) for x in runs]


def blip_wait(runs, now, grace_min=BLIP_GRACE_MIN, day_fails=BLIP_DAY_FAILS):
    """-> why a failed timer unit is only awaiting its next run (one failed run after a good one, recent, not flapping),
    or None when its failure counts. RELAPSE_TIMERS_FIX_DIED_TWICE: timers-20261106020038 reopened twice on such blips
    (testq-tick 2026-11-06T06:30Z, rm-deploy-update 10:20Z), each healed by its own next run, while the real defects
    (rm-account-handover-system, rm-scratch-reap) failed run after run. Unreadable or silent journal: counts."""
    if not runs or not runs[-1][1]:
        return None
    fails = sum(1 for r in runs if r[1])
    if fails >= day_fails:
        return None
    if len(runs) >= 2 and runs[-2][1]:
        return None
    age = (now - runs[-1][0]) / 60.0
    if age >= grace_min:
        return None
    return "one failed run %.0f min ago after a good one (%d failed in 24 h); counts at %d min or on a second" % (
        max(age, 0), fails, grace_min)


def awaiting_retry(units, now, timers=None, runs_of=None, most=4):
    """-> {unit: why} for the failed units whose same-named timer is armed (a next elapse on record: something will run
    them again) and whose failure is a blip_wait blip. Timer rows are list-timers --all rows. No timer list, a timer with
    no next elapse, a unit past the first `most` (bounds journalctl at most x 10 s), or an error: nothing is excused."""
    if not units:
        return {}
    try:
        if timers is None:
            timers = systemctl_json("list-timers", "--all")
        armed = {t.get("unit") for t in timers if isinstance(t, dict) and t.get("next")}
    except Exception:  # noqa: BLE001
        return {}
    out = {}
    for n in units[:most]:
        if n.rsplit(".", 1)[0] + ".timer" not in armed:
            continue
        try:
            why = blip_wait((runs_of or journal_runs)(n), now)
        except Exception:  # noqa: BLE001  one unit's bad journal costs that unit its excuse, never the reading
            why = None
        if why:
            out[n] = why
    return out


PULSE_DEPLOY = "/home/mandrake/rm/pulse-deploy"   # rm-deploy-update's checkout (env RM_PULSE_DEPLOY overrides)


def deploy_update_age(now, root=None):
    """-> (minutes since rm-deploy-update last fast-forwarded the pulse-deploy checkout, why) or (None, why).
    pulse.update_code touches .git/pulse_update_last_good only on a good pull, so a pull refused for a dirty tree or a
    stale ref lock ages it while the unit may read anything (PULSE_DEPLOY_UNSTICK_DIRTY_CHECKOUT: stuck 2026-11-01 to
    11-02, the units it feeds ran old code, nothing alarmed). No checkout: UNMEASURED; a checkout with no stamp has
    never had a good pass on record, which is the alarm, not a blank."""
    root = Path(root or os.environ.get("RM_PULSE_DEPLOY") or PULSE_DEPLOY)
    if not (root / ".git").is_dir():
        return None, "no deploy checkout at %s" % root
    try:
        return round(max(now - (root / ".git" / "pulse_update_last_good").stat().st_mtime, 0) / 60.0, 1), "stamp"
    except FileNotFoundError:
        return 99999.0, "no good update pass on record (%s/.git/pulse_update_last_good absent)" % root
    except OSError as e:
        return None, "stamp unreadable: %s" % str(e)


def c_timers(now, rules, ctx):
    out = {}
    age, why = deploy_update_age(now)
    out["timers.deploy_update_age_min"] = (U(why, "min") if age is None
                                           else M(age, "min since the deploy checkout last fast-forwarded", why=why))
    try:                # two sources: neither one's failure takes the other's reading
        failed = systemctl_json("list-units", "--failed", "--all")
        names = sorted(str(u.get("unit") if isinstance(u, dict) else u) for u in failed)
        real = [n for n in names if n not in one_shot_units(names)]
        shots = sorted(set(names) - set(real))[:12]
        waiting = awaiting_retry(real, now)
        real = [n for n in real if n not in waiting]
        out["timers.failed_units"] = M(len(real), "failed user units", units=real[:12], one_shots=shots,
                                       awaiting_retry=waiting)
    except Exception as e:  # noqa: BLE001
        out["timers.failed_units"] = U("list-units: %s: %s" % (type(e).__name__, str(e)))
    try:
        timers = systemctl_json("list-timers", "--all")
    except Exception as e:  # noqa: BLE001
        out["timers.overdue_timers"] = U("list-timers: %s: %s" % (type(e).__name__, str(e)))
        return out
    over, nob = [], 0
    for t in timers:
        nxt = t.get("next") if isinstance(t, dict) else "bad"
        if nxt and (isinstance(nxt, bool) or not isinstance(nxt, (int, float))):
            nob += 1
        elif nxt and nxt / 1e6 < now - 600:
            over.append(t.get("unit"))
    mk = M if not nob else (lambda v, u, **x: E(v, "%d timer row(s) unreadable (not counted)" % nob, u, **x))
    out["timers.overdue_timers"] = mk(len(over), "timers whose next elapse is over 10 min past", units=over[:12])
    return out


# The daily findings judge's own wait (rm-findings-judge.timer, 07:20 PST daily; longest run 637 s, user journal to
# 2026-11-24): a finding filed just after one judge run has no outcome until the next, by design. Danger it guards: the
# alarm rang OPS_FINDINGS_DIAGNOSE every day on such waiting findings (alarms_log.jsonl 2026-11-22..24, filed and cleared
# by the judge each day), each ring raising a helper. One day plus two hours of slack: a finding past it was missed.
UNTRIAGED_GRACE_S = 26 * HOUR


def untriaged_reading(events, now=None):
    """Findings with no outcome past one judge cycle (findings design section 3). The fold's table is the one judge of an
    outcome, a spawn --from, a retype, an item of that name or a decide, and of an undo of any of them
    (findings_fold.no_outcome): this reading adds only the age (UNTRIAGED_GRACE_S from the finding's first event). A
    finding whose time cannot be read counts. A bad table costs this reading alone: UNMEASURED, not a guess."""
    try:
        import findings_fold
        untr = findings_fold.no_outcome(events)
        types = findings_fold.load_rules()["finding_types"]
    except Exception as e:  # noqa: BLE001  findings_fold.Unmeasured, or a fold that will not import
        return U("findings fold table: %s: %s" % (type(e).__name__, str(e)))
    now = time.time() if now is None else now
    born, first = {}, {}
    for e in events:          # the fold's own keys (finding_key over the same typed events, in ledger order)
        if e.get("event") == "finding" and e.get("type") in types:
            born.setdefault(findings_fold.finding_key(e, first), epoch(e.get("ts")))
    waiting = {n for n in untr if born.get(n) is not None and now - born[n] < UNTRIAGED_GRACE_S}
    late = untr - waiting
    return M(len(late), "findings with no outcome past one judge cycle", first=sorted(late)[:5],
             waiting_for_judge=len(waiting))


def c_flow(now, rules, ctx):
    import ops_ledger as pc
    model = pc._model()
    events = pc.read_ledger(origin=rerun_root())
    ctx["events"] = events
    world = model.replay(events)
    ctx["known_ids"] = set(world.items)
    ctx["open_ids"] = {i for i, it in world.items.items() if it.open}
    closes = {}
    c24 = set()
    v24 = 0
    for ev in events:
        t = model.epoch(ev.get("ts")) or 0
        if ev.get("event") == "close":
            closes.setdefault(ev.get("id"), []).append(t)
            if t >= now - DAY:
                c24.add(ev.get("id"))
        elif ev.get("event") == "verify" and t >= now - DAY and ev.get("result") == "pass":
            v24 += 1
    ctx["closes"] = closes
    ctx["closed_fixes"] = {i: it.closed_sha for i, it in world.items.items() if it.state == "done" and it.closed_sha}
    out = {"flow.untriaged_findings": untriaged_reading(events),
           "flow.closes_24h": M(len(c24), "items closed, 24 h"),
           "flow.verify_pass_24h": M(v24, "verify pass events, 24 h (maker or not)")}
    lapsed = sum(1 for it in world.items.values() if it.open and model.lease_status(it, now) == "lapsed")
    out["flow.lapsed_leases"] = M(lapsed, "open items with a lapsed lease")
    try:
        out["steve.incident_unclaimed_min"] = steve_incident_unclaimed(world, model, now, rules, lane_fault_since(now))
    except Exception as e:  # noqa: BLE001  a bad steve_incident rule costs this reading, not the family's
        out["steve.incident_unclaimed_min"] = U("steve_incident: %s: %s" % (type(e).__name__, str(e)))
    out["flow.ghost_runs"] = ghost_runs_reading()
    return out


def ghost_runs_reading():
    """flow.ghost_runs (RIMMANDRAKE_END_GHOST_RUNS_STORE_SAYS_STARTED_SYSTEMD_GONE): runs the control store holds started
    whose unit systemd reads gone, so their end receipt never ran. `pipe doctor` ends them. A unit systemd cannot read
    is listed, never counted; an unreadable store is UNMEASURED."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rimflow"))
        import control
        g = control.ghosts()
    except Exception as e:  # noqa: BLE001  could not look: said, never a 0
        return U("control store or systemd unreadable: %s: %s" % (type(e).__name__, str(e)))
    return M(len(g["gone"]), "runs the store holds started that systemd reads gone",
             gone=[r["unit"] for r in g["gone"]], unreadable=[r["unit"] for r in g["unreadable"]])


def lane_fault_since(now):
    """-> the epoch the steward's current fault began, or None: no fault, a stale or unreadable steward.json, or the
    machine down (an escalation blocked on the in-person step is waiting on the right thing then)."""
    sj = read_json(qhome() / "steward.json")
    if not isinstance(sj, dict) or not sj.get("fault") or sj.get("state") == "UNREACHABLE":
        return None
    hb, since = epoch(sj.get("epoch")), epoch(sj.get("since"))
    return since if hb is not None and now - hb <= 30 * 60 and since is not None and since <= now else None


def _lane_ticket():
    """testq/lane_ticket.py, loaded by path: putting testq/ on sys.path would shadow modules named like its own."""
    spec = importlib.util.spec_from_file_location("lane_ticket", os.path.join(HERE, "testq", "lane_ticket.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def steve_incident_unclaimed(world, model, now, rules, fault_since=None):
    """steve.incident_unclaimed_min: the age of the oldest unclaimed incident, from its first rung.
    Older incident records still use the ledger reading (id prefix
    rules steve_incident.prefix) that no seat holds: still proposed/ready (not doing/built/validated) (claim/start), no live lease, not blocked. The steward
    escalating a stall makes c_steve call it owned; this is the point that says nobody has picked the escalation up
    (owner 2026-10-28: the lane sat paused 21 min with an open STEVE_LANE_UNSTICK item and no alarm). An OWNER rung
    (an id holding rules steve_incident.owner_rung) is no seat's to claim, so it never counts; the steward has not filed
    one since STEWARD_RUNG_FIX_ASKS_THE_WRONG_GROWNUP (its T+120 rung is a told row for Operations), so only an older
    one matches (OPS_STEVE_UNSTICK_UNCLAIMED_ETBS: 2E27 read 35.9 and went on rising with a wake working the incident).
    A `doing` item whose lease lapsed has no claimant either. A BLOCKED one has none once the lane is in a fault with the
    machine up (FAULT_SINCE, lane_fault_since), for as long as that fault has stood: 2026-11-03 this read 0.0 for 75 min
    of BRAKED, the only item blocked on the in-person step of the UNREACHABLE fault that had already ended."""
    cfg = rules.get("steve_incident") or {}
    pre, rung = cfg.get("prefix", "STEVE_LANE_UNSTICK_"), cfg.get("owner_rung", "_OWNER_")
    lt = _lane_ticket()
    ages, names, unread = [], [], []
    active, legacy, seen = set(), set(), set()
    for source in ("steward.json", "steward_watch.json"):
        try:
            state = json.loads((qhome() / source).read_text(encoding="utf-8"))
            inc = state.get("incident")      # a record with no incident key holds none
            if inc is not None and not isinstance(inc, dict):
                raise ValueError("incident is not a record")
        except FileNotFoundError:
            continue
        except (AttributeError, OSError, ValueError) as e:
            unread.append("%s: %s" % (source, e))
            continue
        seen.add(source)
        if not inc:
            continue
        item = inc.get("item")
        if "opened" not in inc:
            legacy.add(item)
            continue
        active.add(item)
        it = world.items.get(item)
        if it and it.open:
            lease = model.lease_status(it, now)
            waiting = it.blocked and not (getattr(it, "blocked_reason", None) or "").startswith(lt.WAIT)
            if (lease == "live" or it.state not in ("proposed", "ready", "doing")
                    or (waiting and fault_since is None)
                    or (not it.blocked and it.state == "doing" and lease != "lapsed")):
                continue
        began = epoch(inc["opened"])
        if began is None or began > now + 300:
            unread.append("%s: incident has no readable first-rung time" % source)
            continue
        name = item or "SteveDesktop " + inc.get("state", source)
        ages.append(max(0.0, lt.unclaimed_s({name: {"open": {"began": began}}}, name, now) / 60.0))
        names.append(name)
    for it in world.items.values():
        if it.id in active or not it.id.startswith(pre) or rung in it.id or it.state not in ("proposed", "ready", "doing"):
            continue
        cause = lt.CAUSE_ITEM.fullmatch(it.id)
        if cause and it.id not in legacy:
            source = "steward_watch.json" if cause[1].startswith("STALEHEARTBEAT_") else "steward.json"
            if source in seen or (getattr(it, "blocked_reason", None) or "").startswith(lt.WAIT):
                continue
        lease = model.lease_status(it, now)
        if lease == "live" or (it.blocked and fault_since is None):
            continue
        if not it.blocked and it.state == "doing" and lease != "lapsed":
            continue
        t = model.epoch(it.created_at)
        if t is None:
            return U("incident %s has no readable creation time" % it.id)
        if t > now + 300:
            return U("incident %s is dated %.0f min in the future" % (it.id, (t - now) / 60.0))
        began = max(t, fault_since) if (it.blocked or fault_since is not None) else t     # the incident's clock, not the ticket's
        ages.append(max(0.0, (now - began) / 60.0))
        names.append(it.id)
    if not ages:
        if unread:
            return U("could not look at lane incident: " + "; ".join(unread))
        return M(0.0, "min the oldest unclaimed steward incident has waited", why="no unclaimed steward incident")
    old = sorted(zip(ages, names), key=lambda an: (-an[0], an[1]))[:3]     # oldest first: the ones the alarm hands over
    return M(round(old[0][0], 1), "min the oldest unclaimed steward incident has waited", first=[n for _, n in old],
             ages={n: round(a, 1) for a, n in old}, **({"could_not_look": unread} if unread else {}))


GIT_LOG_FMT = "--format=%x1e%ct%x1f%B%x1f"


def _git_log_commits(root, rx, *rev):
    """-> [[ct, n_files, all_process, any_process, message or None]] for `git log <rev>`, oldest first. The message is
    kept only when tokentalk reads it (not empty, not a 'ledger:' commit)."""
    r = subprocess.run(["git", "-C", str(root), "log", "--no-renames", "--name-only", GIT_LOG_FMT] + list(rev),
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError("git log: " + r.stderr.strip())
    out = []
    for rec in r.stdout.split("\x1e")[1:]:
        parts = rec.split("\x1f")
        if len(parts) < 3:
            continue
        try:
            ct = int(parts[0].strip())
        except ValueError:
            continue
        msg = parts[1].strip()
        files = [f.strip() for f in parts[2].split("\n") if f.strip()]
        out.append([ct, len(files), bool(files) and all(rx.match(f) for f in files), any(rx.match(f) for f in files),
                    msg if msg and not msg.startswith("ledger:") else None])
    out.reverse()
    return out


def git_window(since, rx_pattern, now=None):
    """-> the commits of the data clone with commit time >= since, oldest first (as _git_log_commits). process and
    tokentalk each ran a 7-day `git log` over ~8700 commits (3-5 s apiece of the 15 s sense limit, 2026-11-22). This
    reads once, caches by head in the ops store, and after that reads only the commits since the cached head. A head
    not descended from the cached one, a changed regex or root, or a window the cache does not cover reads whole."""
    root = str(data_clone())
    rx = re.compile(rx_pattern)
    p = ops_dir() / "git_window_cache.json"
    r = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError("git rev-parse: " + r.stderr.strip())
    head = r.stdout.strip()
    c = _load_json_dict(p)
    ok = (c.get("v") == 1 and c.get("root") == root and c.get("rx") == rx_pattern and isinstance(c.get("head"), str)
          and is_num(c.get("from")) and c["from"] <= since and isinstance(c.get("commits"), list))
    if ok and c["head"] != head:
        anc = subprocess.run(["git", "-C", root, "merge-base", "--is-ancestor", c["head"], head],
                             capture_output=True, text=True, timeout=60)
        ok = anc.returncode == 0
        if ok:
            c["commits"] = c["commits"] + _git_log_commits(root, rx, "%s..%s" % (c["head"], head))
    if not ok:
        c = {"v": 1, "root": root, "rx": rx_pattern, "from": since,
             "commits": _git_log_commits(root, rx, "--since=@%d" % int(since), head)}
    if c.get("head") != head or not ok:
        c["head"] = head
        c["commits"] = [x for x in c["commits"] if isinstance(x, list) and len(x) == 5 and x[0] >= since - DAY]
        c["from"] = max(c["from"], since - DAY) if is_num(c.get("from")) else since
        _save_json(p, c)
    return [x for x in c["commits"] if x[0] >= since]


def c_process(now, rules, ctx):
    commits = git_window(now - 7 * DAY, rules["process_regex"], now=now)
    out = {}
    for key, span in (("share_24h", DAY), ("share_7d", 7 * DAY)):
        cs = [x for x in commits if x[1] and x[0] >= now - span]
        if not cs:
            out["process." + key] = U("no commit with files in the window")
            continue
        p = sum(1 for x in cs if x[2])
        out["process." + key] = M(round(100.0 * p / len(cs), 1), "% of commits touching process paths only",
                                  commits=len(cs), process_only=p)
    try:  # the live lane's occupancy (FOUNDRY_THROUGHPUT_MEASURE_V2_GAP); a ledger that will not read must not cost the shares above
        import bridge_hours as BH
        import ops_ledger as pc
        evs = pc._model().read_clone(str(data_clone() / "infrastructure" / "state" / "ledger" / "events.jsonl"))
        for key, span in (("bridge_h_24h", DAY), ("bridge_h_7d", 7 * DAY)):
            out["process." + key] = M(BH.held_hours(evs, now, span), "hours the bridge lock was held (each hold cut at 6 h)")
    except Exception as e:  # noqa: BLE001
        for key in ("bridge_h_24h", "bridge_h_7d"):
            out["process." + key] = U("ledger: %s: %s" % (type(e).__name__, str(e)))
    return out


def game_health(now):
    """The standing game health check (HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME, owner C24): record every finished
    full-list session not yet in game_health_check.py's history, then read the newest row's breaches. A breach rings
    OPS_GAME_HEALTH_DEBUG (rules targets): a debug item, as C24 asks ("When it goes worse ... debug why")."""
    keys = ("tps.health_breaches", "tps.health_age_h", "tps.health_sessions")
    try:
        r = subprocess.run([sys.executable, str(HERE / "game_health_check.py"), "record", "--json"],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError("exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()))
        json.loads(r.stdout)
        r = subprocess.run([sys.executable, str(HERE / "game_health_check.py"), "latest", "--json"],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise RuntimeError("latest exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()))
        row = json.loads(r.stdout)
    except Exception as e:  # noqa: BLE001  a broken health check costs these readings, not the tps family's
        return {k: U("game_health_check.py failed: %s" % str(e)) for k in keys}
    if not isinstance(row, dict) or not isinstance(row.get("breaches"), list):
        return {k: U("no full-list game session recorded yet") for k in keys}
    end = epoch(row.get("end"))
    # breaches already debugged for this session (game_health_check.py debugged, a committed record) are carried, not
    # counted: else a finished session re-rings until the next full-list session (OPS_GAME_HEALTH_DEBUG_PXQI, 19 times)
    opn = row.get("open_breaches") if isinstance(row.get("open_breaches"), list) else row["breaches"]
    opn = [b for b in opn if isinstance(b, dict)]
    br = [b.get("key") for b in opn]
    out = {"tps.health_breaches": M(len(br), "limits crossed by the newest full-list session", session=row.get("session"),
                                    keys=br, said="; ".join("%s=%s (limit %s %s)" % (b.get("key"), b.get("value"),
                                                                                     b.get("op"), b.get("limit"))
                                                            for b in opn) or None,
                                    debugged=row.get("debugged") or None,
                                    # what the session was doing when each limit fell (game_health_check.py attribute)
                                    attribution={k: "; ".join(v) for k, v in (row.get("attribution") or {}).items()
                                                 if isinstance(v, list) and k in br} or None),
           "tps.health_age_h": M(round((now - end) / 3600.0, 1), "h since the newest full-list session ended")
           if end is not None else U("newest row has no readable end time")}
    try:
        with open(os.path.join(os.environ.get("RM_GAME_HEALTH_DIR", "/mnt/d/ClaudeWork/rimmandrake/game_health"),
                               "history.jsonl")) as fh:
            out["tps.health_sessions"] = M(sum(1 for ln in fh if ln.strip().endswith("}")), "full-list sessions recorded")
    except OSError as e:
        out["tps.health_sessions"] = U("history unreadable: %s" % e)
    return out


def c_tps(now, rules, ctx):
    health = game_health(now)
    out = dict(health)      # a recorder that fails must not take the game-health readings, measured apart, down with it
    try:
        r = subprocess.run([sys.executable, str(HERE / "tps_record.py"), "--recent", "--json"], capture_output=True,
                           text=True, timeout=90)
        if r.returncode != 0:
            raise RuntimeError("tps_record.py exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()))
        s = (json.loads(r.stdout) or {}).get("summary") or {}
        if not isinstance(s, dict):
            raise ValueError("tps_record gave a summary that is not an object")
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError, AttributeError) as e:
        why = "tps_record failed: %s: %s" % (type(e).__name__, str(e))
        out.update({k: U(why) for k in ("tps.ratio_median", "tps.stalls", "tps.stall_max_s")})
        return out
    if s.get("coverage") != "FRESH":
        why = "no fresh TPS session (coverage %s): the game is not running or the recorder is off" % s.get("coverage")
        out.update({k: U(why) for k in ("tps.ratio_median", "tps.stalls", "tps.stall_max_s")})
        return out
    rm = s.get("ratioMedian")
    if rm is None:
        out["tps.ratio_median"] = U("fresh session but no run window (paused or stalled the whole time)")
    elif is_num(rm):
        out["tps.ratio_median"] = M(rm, "tick ratio to target, median", speed=s.get("speed"), run=s.get("run"))
    else:
        out["tps.ratio_median"] = U("tps_record gave a ratio that is not a number: %r" % (rm,))
    out["tps.stalls"] = M(s.get("stalls"), "stalls in the window", samples=s.get("samples")) \
        if is_num(s.get("stalls")) else U("tps_record gave no stall count")
    out["tps.stall_max_s"] = M(s.get("stallMaxS"), "longest stall s") if is_num(s.get("stallMaxS")) else \
        M(0.0, "longest stall s", why="no stall in the window") if s.get("stalls") == 0 else U("tps_record gave no stall length")
    return out


def streams_series() -> Path:
    return Path(os.environ.get("RM_STREAMS_DIR", "/mnt/d/ClaudeWork/rimmandrake/streams")) / "series.jsonl"


def soft_point(p):
    """A streams measure that is not MEASURED, held to the three marks: an unknown mark is UNMEASURED with no value."""
    m = p.get("m") if p.get("m") in ("ESTIMATE", "UNMEASURED") else "UNMEASURED"
    return {"v": p.get("v") if m == "ESTIMATE" else None, "m": m,
            "why": ("streams mark %r: " % p.get("m") if m != p.get("m") else "") + str(p.get("why") or "")}


def c_production(now, rules, ctx):
    rec = json.loads(last_line(streams_series()) or "null")
    rt = epoch(rec.get("t")) if isinstance(rec, dict) else None
    if rt is None:
        return {"production._collector": U("streams series has no record with a readable time (%s)" % streams_series())}
    age = (now - rt) / 60.0
    if age < -5:
        return {"production._collector": U("the streams record is dated %.0f min in the future" % -age)}
    out = {"production.record_age_min": M(round(age, 1), "min since rm-streams-collect' last record")}
    stale = age > 60
    for k, p in sorted((rec.get("measures") or {}).items()):
        if not isinstance(p, dict):
            out["production." + k] = U("malformed measure in the streams record (%s)" % type(p).__name__)
            continue
        if stale:
            out["production." + k] = U("the streams record is %.0f min old (rm-streams-collect stopped?)" % age)
        elif p.get("m") == "MEASURED" and not (is_num(p.get("v")) and finite(p["v"])):
            out["production." + k] = U("the streams record marks this MEASURED with no number: %r" % (p.get("v"),))
        elif p.get("m") == "MEASURED":
            unit = ((p.get("x") or {}).get("unit")) if isinstance(p.get("x"), dict) else None
            unit = unit if isinstance(unit, str) else None
            out["production." + k] = M(p.get("v"), unit, asof=p.get("asof"))
        else:
            out["production." + k] = soft_point(p)
    ctx["production_src_t"] = rec["t"]
    return out


def c_v3(now, rules, ctx):
    return {"v3." + k: U(str(why)) for k, why in sorted(rules["v3_owed"].items())}


# ============================================================ token-talk drift (OPS_WATCH_BUILD_TOKEN_TALK_DRIFT)
def tt_regex(rules):
    """The rules' token_talk.terms as one case-insensitive whole-word regex (each term is a regex fragment)."""
    terms = (rules.get("token_talk") or {}).get("terms") or []
    if not terms:
        raise RuntimeError("rules token_talk.terms is empty: no word list, nothing can be counted")
    return re.compile(r"(?<![A-Za-z0-9_])(?:" + "|".join(terms) + r")(?![A-Za-z0-9_])", re.I)


def tt_roles_dir() -> Path:
    return Path(os.environ.get("RM_ROLE_RUNS_DIR", "/mnt/d/ClaudeWork/rimmandrake/dispatcher/roles"))


def tt_texts(now, rules, ctx):
    """-> (texts {group: [str]}, bad {group: why}). Groups: a ledger seat (its note/close text; Operations' own OPS_* items
    are left out), 'commits.<seat>' (commit messages; no commit names its seat, so the seat is the path owner: a commit
    touching any process path is BENCH's, else RELENTLESS's (the content builder since FOUNDRY retired, owner by card
    2026-11-02); 'ledger:' commits are skipped, the ledger is read directly),
    'role.<name>' (a finished run's result text; Operations excluded). A group in `bad` could not be read."""
    cfg = rules.get("token_talk") or {}
    since = now - cfg.get("window_days", 7) * DAY
    seats = cfg.get("seats") or []
    texts, bad = {}, {}
    try:
        events = ctx.get("events")
        if events is None:
            import ops_ledger as pc
            events = pc.read_ledger(origin=rerun_root())
        if not events:
            raise RuntimeError("ledger read gave no events")
        for ev in events:
            t = epoch(ev.get("ts"))
            if t is None or t < since or ev.get("seat") not in seats or ev.get("event") not in ("note", "close"):
                continue
            if str(ev.get("id") or "").startswith("OPS_"):
                continue
            body = " ".join(str(ev.get(k) or "") for k in ("text", "reason", "why")).strip()
            if body:
                texts.setdefault(ev["seat"], []).append(body)
    except Exception as e:  # noqa: BLE001
        for sn in seats:
            bad[sn] = "ledger unreadable: %s: %s" % (type(e).__name__, str(e))
    try:
        for _ct, _n, _all, anyp, msg in git_window(since, rules["process_regex"], now=now):
            if not msg:
                continue
            seat = "BENCH" if anyp else "RELENTLESS"
            if seat in seats:
                texts.setdefault("commits." + seat, []).append(msg)
    except Exception as e:  # noqa: BLE001
        for sn in seats:
            bad["commits." + sn] = "git log unreadable: %s: %s" % (type(e).__name__, str(e))
    rd = tt_roles_dir()
    names = set(cfg.get("roles") or [])
    try:
        if not rd.is_dir():
            raise RuntimeError("role run folder %s absent" % rd)
        for f in sorted(rd.glob("rm-role-*.json")):
            m = re.match(r"rm-role-(.+)-(\d+)\.json$", f.name)
            if not m or m.group(1) not in names or float(m.group(2)) < since:
                continue
            role = m.group(1)
            try:
                raw = f.read_text(encoding="utf-8")
                d = json.loads(raw)
            except Exception as e:  # noqa: BLE001 - one unreadable file blinds only its own role
                if now - f.stat().st_mtime < cfg.get("inflight_s", 7200):
                    continue            # still running (systemd creates the file empty at launch): skip, not a failure
                bad["role." + role] = "run %s unreadable: %s" % (f.name, type(e).__name__)
                continue
            res = d.get("result") if isinstance(d, dict) else None
            if not isinstance(res, str) or not res.strip():
                bad["role." + m.group(1)] = "run %s has no readable result text" % f.name
                continue
            texts.setdefault("role." + m.group(1), []).append(res)
    except Exception as e:  # noqa: BLE001
        bad["role._all"] = "role runs unreadable: %s: %s" % (type(e).__name__, str(e))
    return texts, bad


def tt_point(group, items, rx, cfg):
    n = len(items)
    if n < cfg.get("min_reports", 5):
        return U("%d report(s) in the window, under min_reports %d: a share of so few would be noise, not a reading"
                 % (n, cfg.get("min_reports", 5)), "% of reports")
    hits = [len(rx.findall(t)) for t in items]
    words = sum(len(t.split()) for t in items)
    terms = {}
    for t in items:
        for w in rx.findall(t):
            terms[w.lower()] = terms.get(w.lower(), 0) + 1
    top = sorted(terms.items(), key=lambda kv: -kv[1])[:5]
    return M(round(100.0 * sum(1 for h in hits if h) / n, 1), "% of reports with token talk", reports=n,
             hit_reports=sum(1 for h in hits if h), hits=sum(hits), per_1k_words=round(1000.0 * sum(hits) / max(words, 1), 2),
             top=top)


def tt_groups(rules):
    """-> the groups token_talk measures now: each seat, its commits, each role."""
    cfg = rules.get("token_talk") or {}
    seats = cfg.get("seats") or []
    return list(seats) + ["commits." + s for s in seats] + ["role." + r for r in (cfg.get("roles") or [])]


def tt_retired(k, rules):
    """A tokentalk.<group>.share key whose group token_talk no longer measures (a seat or role that left on purpose,
    or was deleted): its silence is the retirement, not an outage (TOKENTALK_SILENT_RETIRE_GHOST_SERIES)."""
    m = re.fullmatch(r"tokentalk\.(.+)\.share", k)
    return bool(m) and m.group(1) not in tt_groups(rules)


def c_tokentalk(now, rules, ctx):
    cfg = rules.get("token_talk") or {}
    rx = tt_regex(rules)
    texts, bad = tt_texts(now, rules, ctx)
    out = {}
    for g in tt_groups(rules):
        why = bad.get(g) or bad.get("role._all") if g.startswith("role.") else bad.get(g)
        if why:
            out["tokentalk." + g + ".share"] = U(why, "% of reports")
        elif g not in texts and g.startswith("role."):
            out["tokentalk." + g + ".share"] = U("no finished %s run in the window (none launched yet, or the folder is empty)"
                                                 % g[5:], "% of reports")
        else:
            out["tokentalk." + g + ".share"] = tt_point(g, texts.get(g, []), rx, cfg)
    return out


def c_evidence(now, rules, ctx):
    """close_evidence chain findings in its 30-day window (EVIDENCE_CUTOVER_CLONES_SYNC_CHECK): every tamper -- an
    old-code append, a hand edit, a deleted line -- is counted and named (file, line, kind) so its alarm target files
    it. close_evidence's own lookup() scopes the doubt; this is the loud half."""
    import close_evidence as ce
    fs = ce.tamper_findings()
    first = ["%s line %s %s: %s" % (Path(f["file"]).name, f["line"] or "-", f["kind"], f["msg"]) for f in fs[:5]]
    return {"evidence.tamper": M(len(fs), "close_evidence tamper findings (30-day window)", first=first,
                                 kinds=sorted({f["kind"] for f in fs}))}


def c_companion(now, rules, ctx):
    """companion.grant_hours_left: hours until the companion's test-profile grant lapses (COMPANION_GRANT_WIRE_LAPSES_AT_
    BEDTIME), read by rimflow/companion_grant.py. A lapsed grant (expired, absent, torn, non-test) is MEASURED at or
    under 0, since the companion reads it as campaign; only an unseeable folder is UNMEASURED. The alarm target in
    ops_watch_rules.json is the early warning.
    companion.grant_visible (1/0) is MEASURED always: a folder that cannot be seen, or a reader that fails, is 0 and
    alarms on its own target, so a blind grant fails closed instead of holding the hours alarm silent forever (blind
    review 2026-10-29 #1)."""
    try:
        rf = str(HERE.parent / "rimflow")
        if rf not in sys.path:
            sys.path.insert(0, rf)
        import companion_grant as cg
        g = cg.read(now=now)
    except Exception as e:  # noqa: BLE001 - a reader that cannot run is a grant nobody can see
        why = "grant reader raised %s: %s" % (type(e).__name__, e)
        return {"companion.grant_hours_left": U(why, "h"), "companion.grant_visible": M(0, why=why)}
    if g["state"] == "UNMEASURED":
        return {"companion.grant_hours_left": U(g["why"], "h"),
                "companion.grant_visible": M(0, why=g["why"], file=g["file"])}
    return {"companion.grant_hours_left": M(g["hours_left"], "h", state=g["state"], expires=g["expires"],
                                            profile=g["profile"], file=g["file"], why=g["why"]),
            "companion.grant_visible": M(1, file=g["file"])}


def tail_json_lines(p, chunk=1 << 21):
    """-> the parsed objects at the end of a JSONL file, oldest first. A torn line is skipped; a missing file raises."""
    with open(p, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - chunk))
        lines = f.read().split(b"\n")
    out = []
    for ln in lines[1:] if size > chunk else lines:
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if isinstance(r, dict):
            out.append(r)
    return out


def st_suppressed(points, fam):
    """A pass that did not measure <fam>.blind (the collector raised, or was taken out of the pass) must not read as
    quiet: the point is written here so its target alarms, on this pass, whatever stopped the collection."""
    why = str((points.get(fam + "._collector") or {}).get("why") or "the %s collector did not run this pass" % fam)
    return M(1, "sources not seen", cause=why)


# ---------------------------------------------------------------- seats: idle with work ready, from the Dispatcher (OP2)
ST_KEYS = ("seats.idle_with_work_min", "seats.paused", "seats.distressed", "seats.cause")
ST_RANGES = ("seats.paused", "seats.tick_age_s", "seats.idle_with_work_min", "seats.blind")


def role_use_module():
    p = HERE.parent / "rimflow" / "role_use.py"
    spec = importlib.util.spec_from_file_location("role_use", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def c_roles(now, rules, ctx):
    """roles.<role>.* (RO1): report-only, from role_use.py over the ledger c_flow read. A share under range two weeks
    running asks the Conductor for a named fix. Nothing here alarms; a ledger not seen is UNMEASURED, and so is a role
    with no output, whose share does not exist."""
    cfg = rules.get("roles")
    if not isinstance(cfg, dict) or not isinstance(cfg.get("roles"), dict):
        return {"roles._collector": U("ops_watch_rules.json has no roles block")}
    RU = role_use_module()
    events = ctx.get("events")
    if events is None:
        import ops_ledger as pc
        events = pc.read_ledger(origin=rerun_root())
    if not events:
        return {"roles._collector": U("the ledger read empty")}
    span, ms, pts = cfg["week_days"] * DAY, ranges_of(rules), {}
    this, last = RU.read(events, cfg, now - span, now), RU.read(events, cfg, now - 2 * span, now - span)
    for role, g in this.items():
        key, m = "roles.%s.acted_share" % role, {"m": "MEASURED"}
        detail = {k: g[k] for k in ("outputs", "acted", "items", "items_coarse")}
        detail.update(untouched=len(g["untouched"]), untouched_coarse=len(g["untouched_coarse"]))
        names = g["untouched"][:20]
        pts[key] = M(g["acted_share"], "share", untouched_items=names, **detail) if g["outputs"] \
            else U("%s has no output this week: runs and silent_days say why" % role, "share")
        pts["roles.%s.runs" % role] = M(g["runs"], "runs")
        pts["roles.%s.silent_days" % role] = M(g["silent_days"], "days of %d" % g["days"])
        was = last[role]["acted_share"]
        pts["roles.%s.weeks_under" % role] = M(RU.weeks_under(g["acted_share"], was, lambda v: base_class(ms[key], v) == "under"),
                                               "weeks", last_week=was) if key in ms else U("no range for " + key, "weeks")
    return pts


def st_dir(cfg) -> Path:
    return Path(os.environ.get("RM_DISPATCHER_STATE") or cfg.get("state_dir") or "/mnt/d/ClaudeWork/rimmandrake/dispatcher")


def st_paused(rows, now, limit):
    """The Dispatcher journals a skip each tick while its PAUSE file is up: a stop somebody chose."""
    for r in reversed(rows):
        t = epoch(r.get("at"))
        if t is None or t > now:
            continue
        if now - t > limit * 60:
            return False
        if r.get("do") == "skip" and str(r.get("why") or "").startswith("PAUSE file present"):
            return True
    return False


def st_idle_since(rows, seat, ss, now):
    """-> (epoch the seat's idle run began, rings in it), or None when the journal does not hold the rings state.json
    says are open, or False when the seat has no ring out and its current idle began after every ring in the run (it
    worked since; no ring yet in this idle). `ss` is that seat's state.json entry, already known to be open.
    Each ring row carries the seat's idle_since, which the Dispatcher restarts at a ring and drops the tick it sees the
    seat busy. So a ring whose idle_since is no later than the ring before it continues that idle; a later one means
    the seat worked in between (2026-10-31: no ring from 05:43 joins the 14:18 one, whose idle began 14:14:17). A
    verified hand-off ends the run. Reading from the end of the record, never from nh_streak, which a busy spell keeps."""
    rings, ids = [], set()
    for r in reversed(rows):
        t = epoch(r.get("at"))
        if r.get("seat") != seat or t is None or t > now:
            continue
        if r.get("do") == "verified":
            break
        if r.get("do") == "ring":
            since = r.get("idle_since")
            since = since if is_num(since) and finite(since) and since <= t else t
            if rings and rings[-1][1] > t + 1:
                break
            rings.append((t, since))
            ids.add(r.get("ring_id"))
    want = (ss.get("ring") or {}).get("ring_id") if isinstance(ss.get("ring"), dict) else None
    if not rings or (want and want not in ids):     # the open ring must be in THIS run, read at `now`, not any row
        return None
    cur = ss.get("idle_since")
    if not ss.get("ring") and is_num(cur) and finite(cur) and cur > rings[0][0] + 1:
        return False    # idle again after a busy spell (nh_streak outlives it), no ring yet: not idle WITH work
    return rings[-1][1], len(rings)


def c_seats(now, rules, ctx):
    """seats.idle_with_work_min (OP2): the longest any seat has sat idle since its first unanswered ring's idle began.
    A ring goes out only when the seat's queue has work, so an open ring run is idle WITH work; a seat at work, or with
    an empty queue, holds none. Limits in rules["seats"]. A state.json whose last_ok_tick stands still, dated ahead, or
    a journal that lacks a ring state.json calls open, reads UNMEASURED and counts in seats.blind, whose target alarms:
    nothing here reads sane on a source it did not see move. Freshness is the stamp inside the file, never its mtime."""
    cfg = rules.get("seats")
    if not isinstance(cfg, dict):
        return {**{k: U("ops_watch_rules.json has no seats block") for k in ST_KEYS},
                "seats.tick_age_s": U("ops_watch_rules.json has no seats block", "s"),
                "seats.blind": M(1, "sources not seen", cause="ops_watch_rules.json has no seats block")}
    no_range = need_ranges(rules, ST_RANGES)
    if no_range:
        return {**{k: U(no_range) for k in ST_KEYS}, "seats.tick_age_s": U(no_range, "s"),
                "seats.blind": M(1, "sources not seen", cause=no_range)}
    ms = ranges_of(rules)
    root = st_dir(cfg)
    limit = ms["seats.tick_age_s"]["max_age_min"]
    st = read_json(root / "state.json")
    t = epoch(st.get("last_ok_tick")) if isinstance(st, dict) else None
    why = None
    if t is None or not isinstance(st.get("seats"), dict):
        why = "state.json missing or torn in %s" % root
    elif t > now + 300:
        why = "state.json is dated %d s ahead of the clock" % (t - now)
    elif now - t > limit * 60:
        why = "state.json frozen: last good tick %s, %.0f min ago, limit %g" % (iso(t), (now - t) / 60.0, limit)
    rows = []
    if why is None:
        try:
            rows = tail_json_lines(root / "journal.jsonl")
        except OSError as e:
            why = "journal.jsonl unreadable: %s" % e
    sch = read_json(Path(cfg.get("schedule") or HERE.parent / "rimflow" / "dispatcher_schedule.json"))
    if why is None and not (isinstance(sch, dict) and isinstance(sch.get("seats"), dict)):
        why = "dispatcher_schedule.json missing or torn"
    worst, per, cause = 0, {}, "none"
    if why is None:
        for seat, ss in sorted(st["seats"].items()):
            sc = sch["seats"].get(seat) if isinstance(sch["seats"].get(seat), dict) else {}
            if not isinstance(ss, dict) or not sc.get("enabled", True) or not sc.get("wake", True):
                continue
            if not (ss.get("ring") or (ss.get("nh_streak") and ss.get("idle_since"))):
                continue            # no ring out, and no idle seat left with an unanswered one
            found = st_idle_since(rows, seat, ss, now)
            if found is False:
                continue
            if found is None:
                rung = (ss.get("ring") or {}).get("rung_at") if isinstance(ss.get("ring"), dict) else None
                if is_num(rung) and finite(rung) and abs(now - rung) < cfg["journal_grace_s"]:
                    continue        # the tick journals after state.json holds the ring; `now` is this run's start, so
                                    # a ring rung during the run is dated after it (21:22 alarm: now 21:22:00, ring 21:22:25)
                why = "journal.jsonl lacks the rings state.json holds open for %s" % seat
                break
            per[seat] = round((now - found[0]) / 60.0, 1)
            if per[seat] >= worst:
                worst = per[seat]
                cause = "%s idle %.0f min with work: %d ring(s) unanswered, since %s" % (seat, worst, found[1], iso(found[0]))
    pts = {}
    if t is not None and t <= now + 300:
        pts["seats.tick_age_s"] = M(round(max(now - t, 0)), "s", max_age_min=limit)
    else:
        pts["seats.tick_age_s"] = U(why, "s")
    if why is not None:
        for k in ST_KEYS:
            pts[k] = U(why, "min" if k.endswith("_min") else None)
        pts["seats.blind"] = M(1, "sources not seen", cause=why)
        return pts
    pts["seats.paused"] = M(int(bool(st_paused(rows, now, limit))), "1 while a PAUSE file stands")
    pts["seats.idle_with_work_min"] = M(worst, "min", per_seat=per)
    state = read_class(ms, "seats.idle_with_work_min", pts)
    cause = cause if state in ALARMED else "none"
    pts["seats.idle_with_work_min"]["x"]["state"] = state
    pts["seats.distressed"] = M(int(state in ALARMED), "1 when a seat is idle with work", state=state, cause=cause)
    pts["seats.cause"] = M(cause)
    pts["seats.blind"] = M(0, "sources not seen", cause="none")
    return pts


QUEUE_STALL_MIN = 20.0


def _mtimes(d, pattern, skip_worker_msg=False):
    """mtimes of the files still there: one moved between the listing and the stat (a claim or a finish) is skipped.
    A directory that is absent holds nothing; one that cannot be listed raises, so the queue reads UNMEASURED, never
    a calm 0 (Path.glob swallows a PermissionError into an empty listing)."""
    try:
        names = os.listdir(d)
    except FileNotFoundError:
        return []
    ts = []
    for name in names:
        if not fnmatch.fnmatchcase(name, pattern) or (skip_worker_msg and name.endswith(".worker_last_message.json")):
            continue
        try:
            ts.append(os.stat(os.path.join(d, name)).st_mtime)
        except FileNotFoundError:
            pass
    return ts


def newest_mtime(d, pattern="*.json"):
    ts = _mtimes(d, pattern, skip_worker_msg=True)
    return max(ts) if ts else None


# Old names each pass stats again, in turn (design/specs/2026-11-22-sense-families-cheap/boundary.md). It guards a
# progress file rewritten in place under an old name, which no listing shows; a miss can only read a moving queue as
# stalled (loud). At 4000 the queues family re-statted ~6900 names a pass on drvfs: 8.4 s of the 15 s sense limit.
PROGRESS_RESTAT = 250


def newest_progress_mtime(d, cache, now, pattern="*.json", checkpoint=None):
    """newest_mtime for a progress dir (done/, failed/), which gains files by a finish moving one in and grows to
    tens of thousands on drvfs (artpipe/done 19k: 16 s of stat a run, over the metronome's 15 s sense limit). `cache`
    (a dict, kept by the caller between runs) holds per dir the names already stat'd, their newest mtime and a rolling
    cursor: a pass stats every name new since, plus the next PROGRESS_RESTAT names it has seen, so a file rewritten in
    place under an old name is seen within len/PROGRESS_RESTAT passes. A vanished newest name costs one whole re-stat.
    An absent dir holds nothing; one that cannot be listed raises (as _mtimes). `now` is unused: kept for callers."""
    key = str(d)
    try:
        names = os.listdir(d)
    except FileNotFoundError:
        cache.pop(key, None)
        return None
    names = sorted(n for n in names if fnmatch.fnmatchcase(n, pattern) and not n.endswith(".worker_last_message.json"))
    c = cache.get(key)
    ok = (isinstance(c, dict) and isinstance(c.get("names"), list) and all(isinstance(n, str) for n in c["names"])
          and isinstance(c.get("cur"), int) and (c.get("newest") is None or isinstance(c.get("newest"), (int, float)))
          and (c.get("top") is None or isinstance(c.get("top"), str)))
    if not ok or (c["top"] is not None and c["top"] not in set(names)):
        c = {"names": [], "newest": None, "top": None, "cur": 0}
    seen = set(c["names"])
    old = [n for n in names if n in seen]
    cur = c["cur"] % len(old) if old else 0
    again = set(old[cur:cur + PROGRESS_RESTAT] + old[:max(0, cur + PROGRESS_RESTAT - len(old))])
    newest, top = c["newest"], c["top"]
    done = 0
    for name in names:
        if name in seen and name not in again:
            continue
        try:
            t = os.stat(os.path.join(d, name)).st_mtime
        except FileNotFoundError:
            continue
        seen.add(name)
        if newest is None or t > newest:
            newest, top = t, name
        done += 1
        if checkpoint and done % 2000 == 0:      # a cold pass killed at its limit still leaves its progress
            cache[key] = {"names": sorted(seen), "newest": newest, "top": top, "cur": c["cur"]}
            checkpoint()
    keep = set(names)
    cache[key] = {"names": names, "newest": newest if top in keep else None,
                  "top": top if top in keep else None, "cur": (cur + PROGRESS_RESTAT) if old else 0}
    return cache[key]["newest"]


def _load_json_dict(p):
    try:
        with open(p, encoding="utf-8") as fh:
            v = json.load(fh)
        return v if isinstance(v, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_json(p, v):
    tmp = str(p) + ".tmp"     # one fixed name: a writer killed mid-dump leaves one file, overwritten next time
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(v, fh, separators=(",", ":"))
        os.replace(tmp, p)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def oldest_mtime(d, pattern="*.json"):
    ts = _mtimes(d, pattern)
    return min(ts) if ts else None


def _q_dirs(q, now, pcache, cpath):
    """The directory form (artpipe, testq): pending/*.json waits, active/*.json is claimed (its mtime the heartbeat),
    each progress dir gains a file on a finish."""
    pend, act = Path(q["pending"]), Path(q["active"])
    if not pend.is_dir() or not act.is_dir():
        raise OSError('queue dir missing: %s' % (pend if not pend.is_dir() else act))
    plist = _mtimes(pend, "*.json")  # a job claimed between the glob and the stat is movement, not blindness
    alist = _mtimes(act, "*.json", skip_worker_msg=True)
    marks = [newest_mtime(act)] + [newest_progress_mtime(Path(x), pcache, now, checkpoint=lambda: _save_json(cpath, pcache))
                                   for x in q.get("progress", [])]
    return plist, alist, marks


def _iso_epoch(s):
    try:
        return calendar.timegm(time.strptime(str(s)[:19], "%Y-%m-%dT%H:%M:%S"))
    except (TypeError, ValueError):
        return None


def _q_designer(q, now, pcache, cpath):
    """The Designer's concepts (DESIGNER_STALL_MONITOR_READY_AND_FORGOTTEN): the Designer is run-now only, so a concept
    whose stage.json reads status=ready waits on someone launching it, and nothing else notices (FlowWorks sat at
    stage 2 ready for 12 h+ on 2026-11-04). Each ready concept is pending since it last moved: the later of its last
    history row (a run's open or close, an unblock, a reopen) and its open run's start. Pending times only, no marks,
    so the stall is the OLDEST ready concept's (a run on one concept never hides another left behind); a run open
    longer than the threshold with no close is a stall too (measured runs take 2 to 11 min). A concept at
    waiting_owner whose owner has ANSWERED (designer_stage.owner_moved; DESIGNER_ANSWERED_MONITOR_WAITING_ON_NOBODY)
    is pending too, since his answer (designer_stage.owner_answered_at): only a run's open moves it back to ready, so
    it is forgotten the same way. One still waiting on him, blocked or locked is not pending, nor is a concept no run
    has opened (role_launch.never_opened: it waits on a hand run-now, the sweep's rule), nor is a ready concept
    whose rejected last result is PARKED (designer_stage.rejection_parked, the rule role_launch.chain_sweep retries
    by; RELAPSE_QUEUES_FIX_DIED_TWICE): the stall alarm counts exactly what the sweep should have moved. root: the concepts dir
    (default designer_stage.concepts_root(), the Designer clone's design/concepts); repo: the clone whose OWNER shard
    is read (default designer_stage.REPO; the concept's own clone is read too); a missing root, a stage.json that does
    not parse, a ready concept with no readable time, or a waiting concept whose OWNER shard is unreadable is blind. A
    ready concept the launcher holds on the per-concept daily chain cap (role_launch.chain_capped; the dispatcher's
    state.json, RIMMANDRAKE_SKIP_CHAIN_CAPPED_CONCEPTS_IN_DESIGNER_STALL) is not pending either; an unreadable
    dispatcher state is blind."""
    rf = str(HERE.parent / "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import designer_stage as DS
    repo = q.get("repo") or DS.REPO
    if q.get("root"):
        root = Path(q["root"])
    else:
        root = Path(DS.concepts_root())
    if not root.is_dir():
        raise OSError("concepts dir missing: %s" % root)
    runs_dir = Path(q.get("runs_dir") or os.path.join(
        os.environ.get("RM_DISPATCHER_STATE", "/mnt/d/ClaudeWork/rimmandrake/dispatcher"), "roles"))
    plist, alist, marks = [], [], []
    import role_launch as RL
    sdir = os.environ.get("RM_DISPATCHER_STATE", "/mnt/d/ClaudeWork/rimmandrake/dispatcher")
    state_file = q.get("state_file") or os.path.join(sdir, "state.json")
    dstate = []     # the dispatcher state, read once and only when a ready concept needs it (unreadable: blind)

    def chain_capped(st_, folder):
        """The launcher holds this ready concept on the daily chain cap (role_launch.chain_capped, the one rule). The
        concept is matched to its chain_day key by folder name: the key is the path the launcher was given."""
        if not dstate:
            with open(state_file, encoding="utf-8") as fh:
                d = json.load(fh)
            if not isinstance(d, dict) or not isinstance(d.get("roles"), dict):
                raise ValueError("dispatcher state has no roles object: %s" % state_file)
            dstate.append(d)
        role = "DesignerCodex" if st_.get("runner") == "codex" else "Designer"
        rs = dstate[0]["roles"].get(role) or {}
        day = RL.day_of(now)
        want = os.path.basename(os.path.normpath(str(folder)))
        key = next((k[len(day) + 1:] for k in (rs.get("chain_day") or {})
                    if k.startswith(day + " ") and os.path.basename(os.path.normpath(k[len(day) + 1:])) == want), None)
        return key is not None and RL.chain_capped(rs, {}, key, st_.get("stage"), now)
    import mod_owner_hold as OH
    holds = OH.load()       # a concept the owner holds is not pending (mod_owner_hold.py); an unreadable file is blind
    for f in sorted(root.glob("*/stage.json")):
        if OH.key(f.parent) in holds:
            continue
        with open(f, encoding="utf-8") as fh:
            st = json.load(fh)
        if not isinstance(st, dict):
            raise ValueError("stage.json is not an object: %s" % f)
        if st.get("runner") == "codex":     # the Codex lane's own marks (queues-20261116013824): a stage it landed ...
            for h in (st.get("history") or []):
                t = _iso_epoch(h.get("at")) if isinstance(h, dict) else None
                if t is not None:
                    marks.append(t)
        run_id = (st.get("running") or {}).get("run") if isinstance(st.get("running"), dict) else None
        if run_id and runs_dir.is_dir():    # ... and a live run's files (events, stderr, spend) in the dispatcher's roles dir
            for rf_ in runs_dir.glob(glob.escape(str(run_id)) + ".*"):
                try:
                    marks.append(rf_.stat().st_mtime)
                except OSError:
                    pass
        run_at = _iso_epoch((st.get("running") or {}).get("at")) if isinstance(st.get("running"), dict) else None
        if run_at is not None:
            alist.append(run_at)
        if st.get("status") == "waiting_owner":
            try:
                ans = DS.owner_answered_at(st, str(f.parent), repo)
            except DS.Refused as e:
                raise OSError("%s: %s" % (f, e))
            if ans is not None:
                plist.append(max(t for t in (ans, run_at) if t is not None))
            continue
        if st.get("status") != "ready":
            continue
        if RL.never_opened(st):
            continue      # the sweep's own rule: a new concept waits on a hand run-now, not on a stalled chain
        if DS.rejection_parked(st, repo):
            continue      # the sweep's own rule: a retry cannot help; role_launch.parked_record says so
        if chain_capped(st, f.parent):
            continue      # held on the daily chain cap: role:<Role>:chain_cap already said so once (the same rule)
        hs = [h for h in (st.get("history") or []) if isinstance(h, dict)]
        last = _iso_epoch(hs[-1].get("at")) if hs else None
        if last is None and run_at is None:
            raise ValueError("ready concept with no readable history or run time: %s" % f)
        plist.append(max(t for t in (last, run_at) if t is not None))
    return plist, alist, marks


QUEUE_READERS = {"dirs": _q_dirs, "designer_stage": _q_designer}


def c_queues(now, rules, ctx):
    """queues.<name>.stalled_min (QUEUE_ORPHAN_WEDGE_1): the class 'a claimed or leased job is orphaned and the queue
    sits calmly idle'. For each work queue in rules["queues"], its reader (QUEUE_READERS; `reader`, default "dirs")
    gives the pending jobs' wait-start times, the claimed (active) files, and the movement marks (a newer
    claim, finish, heartbeat or watcher tick). stalled_min = minutes since max(newest mark, oldest pending start); 0
    when nothing is pending. An active job counts as in flight only through its mtime, so an orphan nobody
    heartbeats stops counting after its lease. A queue paused on purpose (paused_file present) or not switched on
    (armed_file absent) reads 0. A queue its reader cannot see reads UNMEASURED and counts in queues.blind, never 0.
    A new claim/lease queue is wired by a rules entry (and, if its shape is new, one reader), never a new family."""
    out = {}
    qs = rules.get("queues")
    if not isinstance(qs, list) or not qs:
        return {"queues.blind": U("ops_watch_rules.json has no queues list")}
    blind = []
    cpath = ops_dir() / "queue_progress_cache.json"
    pcache = _load_json_dict(cpath)
    for q in qs:
        n = q.get("name", "?")
        k = "queues.%s." % n
        try:
            reader = QUEUE_READERS[q.get("reader", "dirs")]
            off = bool((q.get("paused_file") and Path(q["paused_file"]).exists())
                       or (q.get("armed_file") and not Path(q["armed_file"]).exists()))
            try:
                plist, alist, marks = reader(q, now, pcache, cpath)
            except Exception:  # noqa: BLE001 - a queue switched off is not watched, so it cannot be blind
                if not off:
                    raise
                out[k + "stalled_min"] = M(0.0, "min pending > 0 with no claim, finish or heartbeat", why="switched off")
                continue
            marks = [m for m in marks if m is not None]
            with contextlib.suppress(OSError):      # the end of a pause: the time before it was not a stall
                if q.get("resumed_file"):
                    marks.append(Path(q["resumed_file"]).stat().st_mtime)
            if off:
                stalled = 0.0
            elif not plist:
                stalled = 0.0
            else:
                ref = max(marks + [min(plist)])
                stalled = max(0.0, (now - ref) / 60.0)
            out[k + "pending"] = M(len(plist), "jobs waiting")
            out[k + "active"] = M(len(alist), "files in active")
            out[k + "stalled_min"] = M(round(stalled, 1), "min pending > 0 with no claim, finish or heartbeat")
        except Exception as e:  # noqa: BLE001 - a reader that cannot see is blind, never a calm 0
            blind.append(n)
            out[k + "stalled_min"] = U("%s: %s" % (type(e).__name__, str(e)), "min")
    wanted = {str(Path(x)) for q in qs if isinstance(q, dict) for x in (q.get("progress") or [])}
    for k_ in [k_ for k_ in pcache if k_ not in wanted]:      # a dir dropped from the rules leaves the cache
        pcache.pop(k_)
    _save_json(cpath, pcache)
    out["queues.blind"] = M(len(blind), "queues not seen", names=",".join(blind))
    out.update(artpipe_signin_reading())
    return out


def artpipe_signin_reading(home=None, log_dir=None):
    """queues.artpipe.signins_bad: 1 when the one Codex sign-in is gone, torn or dead on the last call that could tell,
    else 0 (artpipe/signin_health.py: the folder and the door's call log, no network, no token in the point). A log or
    folder that cannot be read is UNMEASURED, never 0. Page:
    design/specs/2026-11-24-art-daemon-over-the-one-door/boundary.md."""
    k = "queues.artpipe.signins_bad"
    try:
        ap = str(HERE / "artpipe")
        if ap not in sys.path:
            sys.path.insert(0, ap)
        import signin_health as SH
        if home is None:
            home, log_dir = SH.defaults()
        v, facts = SH.check(Path(home), Path(log_dir))
    except Exception as e:  # noqa: BLE001 - an unreadable log or a failed import is blind, never a calm 0
        return {k: U("the Codex sign-in was not read: %s: %s" % (type(e).__name__, str(e)), "sign-ins")}
    bad = {str(home): v} if v in SH.BAD else {}
    return {k: M(len(bad), "the one Codex sign-in, gone, torn or dead", homes=1, bad=bad, **facts)}


def c_wrapup(now, rules, ctx):
    """AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED: what agents left at their end that is STILL there (rimflow/wrapup.py
    re-measures every filed row), and how many wrap-ups ran in 24 h: a wrap-up that never runs reads 0 there, so a 0
    standing is believed only beside a live record count. No state dir: UNMEASURED, never 0."""
    rf = str(HERE.parent / "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    out = {}
    try:
        import wrapup
        d = wrapup.state_dir()
        if not os.path.isdir(d):
            raise OSError("no wrap-up state dir %s" % d)
        rows = [(os.path.basename(f), r) for f, _, rs in wrapup.standing() for r in rs]
        out["wrapup.debris_standing"] = M(len(rows), "filed wrap-up rows still standing",
                                          first=["%s %s %s" % (f[:-5], r.get("kind"), r.get("what")) for f, r in rows[:6]])
        n, cut = 0, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - DAY))
        try:
            with open(os.path.join(d, "runs.jsonl"), encoding="utf-8") as f:
                for line in f:
                    try:
                        n += str(json.loads(line).get("at") or "") >= cut
                    except (ValueError, AttributeError):
                        continue
        except FileNotFoundError:
            pass
        out["wrapup.records_24h"] = M(n, "wrap-ups recorded in 24 h")
    except Exception as e:  # noqa: BLE001
        out["wrapup.debris_standing"] = U("%s: %s" % (type(e).__name__, str(e)))
        out["wrapup.records_24h"] = U("%s: %s" % (type(e).__name__, str(e)))
    return out


MATURATION_READING_MAX_AGE_S = 1800     # the Dispatch step ticks every 60 s; 30 missed ticks is a dead step (30 min, kept)
INGAME_VISIT_OWED_KEY = "maturation.ingame_visit_owed_no_driver_min"
INGAME_LOCK_QUERY_S = 0.25              # a local snapshot, below the 15 s sense beat even for a lock caught mid-write


def ingame_visit_owed(now, rd, last, rules):
    """Longest observed wait with bridge checks owed and no Arch lock holder or live pipeline driver."""
    unit = "min of visit with bridge checks owed"
    at = epoch(rd.get("at"))
    if at is None or at > now + 300 or now - at > MATURATION_READING_MAX_AGE_S:
        return U("the dispatch reading has no current timestamp", unit)
    entries = rd.get("ingame_testq")
    if not isinstance(entries, dict):
        return U("no in-game visit block: %s" % (rd.get("ingame_testq_error") or "dispatch has not written it"), unit)
    waiting = {}
    for mod, e in entries.items():
        if not isinstance(e, dict) or e.get("hold_unreadable") or e.get("error"):
            return U("%s: %s" % (mod, _obj(e).get("error") or "visit or hold unreadable"), unit)
        if e.get("blocked") or e.get("held") or e.get("owed") == "exit met":
            continue
        checks = e.get("bridge_checks")
        if not isinstance(checks, list):
            return U("%s: %s" % (mod, e.get("bridge_checks_error") or "no bridge checks reading"), unit)
        if checks:
            opened = epoch(e.get("opened"))
            if opened is None or opened > now:
                return U("%s: visit opening unreadable (%r)" % (mod, e.get("opened")), unit)
            waiting[mod] = opened, e.get("visit"), len(checks)
    if not waiting:
        return M(0, unit, state="quiet")

    import game_names
    if game_names.machine() != "archmagi":
        return U("could not look at Arch locks on this host", unit)
    deadline = beat_deadline()
    timeout = INGAME_LOCK_QUERY_S if deadline is None else min(INGAME_LOCK_QUERY_S, deadline - time.time())
    if timeout <= 0:
        return U("could not look at Arch locks: sense beat out of time", unit)
    query_until = time.monotonic() + timeout

    def probe(cmd, *, timeout, **kw):
        left = min(timeout, query_until - time.monotonic())
        if left <= 0:
            raise subprocess.TimeoutExpired(cmd, 0)
        return subprocess.run(cmd, timeout=left, **kw)

    cmd = [sys.executable, str(HERE.parent / "rimflow" / "game_lock.py"), "query", "all", "--json"]
    try:
        r = probe(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return U("could not look at Arch locks: %s" % e, unit)
    if r.returncode not in (0, 2):
        return U("Arch lock query failed (exit %s): %s" % (r.returncode, r.stderr.strip()), unit)
    locks = [g for g in json.loads(r.stdout)["games"] if g.get("game") in ("a", "b")]
    if {g.get("game") for g in locks} != {"a", "b"}:
        return U("could not look at both Arch locks", unit)
    for g in locks:
        if g.get("code") == 2 or g.get("state") not in ("FREE", "HELD", "HIS_HOLD"):
            return U(g.get("line") or "could not look at an Arch lock", unit)
    purposes = [g.get("purpose") or "" for g in locks if g["state"] == "HELD" or g.get("owner_hold")]
    waiting = {mod: v for mod, v in waiting.items() if not any(
        re.search(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(mod), purpose, re.I) for purpose in purposes)}
    for mod, (_, visit, _) in list(waiting.items()):
        row = _obj(_obj(rd.get("mods")).get(mod))
        live = row.get("live")
        if row.get("stage") != "in_game" or not isinstance(live, list):
            return U("%s: dispatch could not read the in-game running units" % mod, unit)
        if row.get("visit") not in (None, visit):
            continue
        if row.get("decision") == "launched" and _obj(row.get("launch")).get("rule") == "decide_ingame":
            live = live + [row.get("unit")]
        if live:
            import role_launch
            import run_alive
            lives = {name: run_alive.unit_fact(role_launch.unit_state(name, runner=probe))
                     for name in live if isinstance(name, str) and name}
            if "active" in lives.values():
                del waiting[mod]
            elif "unknown" in lives.values() or any(not isinstance(name, str) or not name for name in live):
                return U("%s: could not read the life of an in-game run (%s)" % (mod, live), unit)
    if not waiting:
        return M(0, unit, state="busy")
    prior = {}
    last_at = epoch(last.get("t"))
    if last_at is not None and 0 <= now - last_at <= compose_max_age_s(rules)[0]:
        p = _obj(last["points"].get(INGAME_VISIT_OWED_KEY))
        x = _obj(p.get("x"))
        if p.get("m") == "MEASURED" and x.get("state") == "waiting":
            prior = _obj(x.get("waiting_since"))
    waiting_since = {}
    for mod, (opened, visit, _) in waiting.items():
        old = _obj(prior.get(mod))
        start = epoch(old.get("at"))
        if old.get("visit") != visit or old.get("opened") != opened or start is None or not opened <= start <= last_at:
            start = now
        waiting_since[mod] = {"visit": visit, "opened": opened, "at": start}
    mod = min(waiting_since, key=lambda m: waiting_since[m]["at"])
    _, visit, n = waiting[mod]
    minutes = (now - waiting_since[mod]["at"]) / 60
    return M(minutes, unit, state="waiting", waiting={m: v[2] for m, v in waiting.items()},
             waiting_since=waiting_since,
             said="%s visit %s has %d bridge check(s) owed and no driver (waiting %d min)" % (mod, visit, n, minutes))


# danger: a dead list tick whose last streak still reads as now. rm-list-dispatch.timer ticks every 10 min; 6 missed ticks
# is a dead tick. It ends no work: the metric reads UNMEASURED.
LIST_READING_MAX_AGE_S = 3600
LIST_BLIND_KEY = "maturation.list_gate_blind_passes"


def list_gate_blind(now):
    """LIST_BLIND_KEY: the applied list_dispatch ticks in a row that held work on a reading that could not be made
    (list_dispatch.blind_hold), with the gate, the cause (it names the file) and the count of held items. Its alarm
    OPS_LIST_GATE_HOLDS_READY_WORK_ON_COULD_NOT_LOOK fires past the rules' line. A missing, torn or stale reading is
    UNMEASURED, never 0 (RIMMANDRAKE_SCOPE_COULD_NOT_LOOK_ONE_STRAY_FILE_HELD_ELEVEN_TICKETS: 11 ready items held for
    about a day on 123 unreadable sign-of-life files, and nothing told)."""
    rf = str(HERE.parent / "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    try:
        import list_dispatch as LD
        p = os.path.join(LD.sdir(create=False), "reading.json")
        with open(p, encoding="utf-8") as f:
            rd = json.load(f)
        age = now - float(rd.get("at") or 0)
        if age > LIST_READING_MAX_AGE_S:
            return U("list_dispatch reading %s is %d min old (the tick is not ticking)" % (p, age / 60), "passes")
        if not rd.get("apply"):
            return U("list_dispatch reading %s is a dry tick's" % p, "passes")
        bh = rd.get("blind_hold")
        if not isinstance(bh, dict) or not isinstance(bh.get("passes"), int):
            return U("no blind_hold block in %s" % p, "passes")
        if not bh["passes"]:
            return M(0, "passes", held=0)
        said = "%s held %s item(s) on a could-not-look for %d passes: %s" % (
            bh.get("gate"), bh.get("held"), bh["passes"], bh.get("cause"))
        return M(bh["passes"], "passes", held=bh.get("held"), gate=bh.get("gate"), cause=bh.get("cause"),
                 items=",".join(bh.get("items") or []), said=said)
    except Exception as e:  # noqa: BLE001  could not look is never "nothing held"
        return U("%s: %s" % (type(e).__name__, e), "passes")


def c_maturation(now, rules, ctx):
    """RIMMANDRAKE_WIRE_DISPATCH_TO_LAUNCH_BUILDERS_MODS_SAT_IDLE: the longest an advancing mod at the offline build has
    had work owed (build, a hand step, ready to advance) with nothing running on it, from maturation_dispatch.py's
    reading (rm-maturation-dispatch.timer). Its alarm OPS_MATURATION_IDLE_ADVANCING_MOD fires over 60 min (the owner,
    2026-11-14: four mods sat 6 to 9 h at Stage 3 unseen). A missing or stale reading is UNMEASURED, never 0."""
    rf = str(HERE.parent / "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    out = {}
    try:
        import maturation_dispatch as MD
        p = os.path.join(MD.sdir(), "reading.json")
        with open(p, encoding="utf-8") as f:
            rd = json.load(f)
        age = now - float(rd.get("at") or 0)
        if age > MATURATION_READING_MAX_AGE_S:
            raise ValueError("reading %s is %d min old (the step is not ticking)" % (p, age / 60))
        out["maturation.idle_owed_max_min"] = M(int(rd.get("idle_owed_max_min") or 0), "min",
                                                mods=",".join(rd.get("idle_owed_mods") or []))
        out["maturation.needs_conductor"] = M(len(rd.get("needs_conductor") or []), "lines",
                                              first=(rd.get("needs_conductor") or [])[:4])
        out["maturation.paused"] = M(len(rd.get("paused") or []), "mods", first=(rd.get("paused") or [])[:4])
        out["maturation.stalled"] = M(len(rd.get("stalled") or []), "mods", mods=",".join(rd.get("stalled") or []))
        h = rd.get("hand_acts")         # maturation_hands.observe: hand acts on the pipeline with no follow-up for a day
        out["maturation.hand_acts_overdue"] = M(
            h["overdue"], "acts", open=h.get("open"), oldest_h=h.get("oldest_h"), ids=",".join(h.get("ids") or [])
        ) if isinstance(h, dict) and isinstance(h.get("overdue"), int) else U(
            "no hand_acts block in %s (%s)" % (p, rd.get("hand_acts_error") or "maturation_hands.observe did not run"))
        c = rd.get("clone") or {}       # the dispatch clone the timers run from, measured by the same tick
        out["maturation.clone_behind_min"] = M(c["behind_min"], "min", behind=c.get("behind"), ahead=c.get("ahead"),
                                               level=c.get("level_pac")) if c.get("measured") else U(
            "the dispatch clone: %s" % (c.get("why") or "no clone reading in %s" % p))
    except Exception as e:  # noqa: BLE001
        out[INGAME_VISIT_OWED_KEY] = U("%s: %s" % (type(e).__name__, e))
        out["maturation.clone_behind_min"] = U("%s: %s" % (type(e).__name__, str(e)))
        out["maturation.hand_acts_overdue"] = U("%s: %s" % (type(e).__name__, str(e)))
        out["maturation.idle_owed_max_min"] = U("%s: %s" % (type(e).__name__, str(e)))
        out["maturation.needs_conductor"] = U("%s: %s" % (type(e).__name__, str(e)))
        out["maturation.paused"] = U("%s: %s" % (type(e).__name__, str(e)))
        out["maturation.stalled"] = U("%s: %s" % (type(e).__name__, str(e)))
    else:
        try:
            out[INGAME_VISIT_OWED_KEY] = ingame_visit_owed(now, rd, ctx.get("last_record") or {}, rules)
        except (ValueError, KeyError, AttributeError, TypeError) as e:
            out[INGAME_VISIT_OWED_KEY] = U("in-game visit reading unreadable: %s: %s" % (type(e).__name__, e))
    out[LIST_BLIND_KEY] = list_gate_blind(now)      # its own reading: a fault of the mod step's reading never blanks it
    return out


def c_pager(now, rules, ctx):
    """pager.*: a page to his phone that could not leave, refused callers, pages sent (ops_watch_pager.py; item
    RIMMANDRAKE_DESIGN_PUSHOVER_ALERTS_CRITICAL_ONLY_TWO_SENDERS). A pager dir that cannot be named is UNMEASURED."""
    import datetime as _dt
    try:
        import pager
        import ops_watch_pager
        return ops_watch_pager.points(pager.pager_dir(), _dt.datetime.fromtimestamp(now, _dt.timezone.utc))
    except Exception as e:  # noqa: BLE001  one family's fault never stops the pass
        why = "%s: %s" % (type(e).__name__, e)
        return {"pager.could_not_send": U(why, "faults whose page has not left"),
                "pager.refused_24h": U(why, "refused send attempts, 24 h"),
                "pager.sent_7d": U(why, "pages accepted by Pushover, 7 d")}


COLLECTORS = {"accounts": c_accounts, "codex": c_codex, "steve": c_steve_all, "flow": c_flow, "testing": c_testing,
              "disk": c_disk, "timers": c_timers, "process": c_process, "tps": c_tps, "production": c_production,
              "v3": c_v3, "tokentalk": c_tokentalk, "evidence": c_evidence, "companion": c_companion,
              "seats": c_seats, "roles": c_roles,
              "queues": c_queues, "wrapup": c_wrapup, "maturation": c_maturation, "pager": c_pager}
ORDER = ("accounts", "codex", "steve", "flow", "testing", "disk", "timers", "process", "tps", "production", "v3", "tokentalk",
         "evidence", "companion", "seats", "roles", "queues", "wrapup", "maturation", "pager")


# ==================================================================================================== storage
def series_path(fam) -> Path:
    return ops_dir() / "series" / ("%s.jsonl" % fam)


def read_series(fam, since, max_bytes=32 << 20):
    p = series_path(fam)
    out = []
    try:
        with open(p, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - max_bytes))
            data = f.read()
    except OSError:
        return out
    lines = data.split(b"\n")
    if size > max_bytes:
        lines = lines[1:]
    for ln in lines:
        if not ln.strip():
            continue
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if not isinstance(r, dict) or epoch(r.get("t")) is None or isinstance(r.get("t"), str) \
                or not isinstance(r.get("points"), dict):
            continue        # a torn or foreign line is skipped, never fatal to the pass
        if r["t"] >= since:
            out.append(r)
    return out


def append(fam, rec):
    p = series_path(fam)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, default=str) + "\n")


def atomic_json(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str), encoding="utf-8")
    os.replace(tmp, p)


# ===================================================================================================== Andon
def matches(key, pats):
    return any(fnmatch.fnmatchcase(key, p) for p in ([pats] if isinstance(pats, str) else pats))    # a bare string is one key


def num(p):
    v = p.get("v") if isinstance(p, dict) else None
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and finite(v) else None


def history(recs):
    """key -> [(t, value)] of MEASURED numeric points, oldest first."""
    h = {}
    for r in recs:
        for k, p in (r.get("points") or {}).items():
            v = num(p)
            if isinstance(p, dict) and p.get("m") == "MEASURED" and v is not None:
                h.setdefault(k, []).append((r["t"], v))
    return h


OPS = ("<", "<=", ">", ">=")


def _cmp(v, op, x):
    return {"<": v < x, "<=": v <= x, ">": v > x, ">=": v >= x}[op]


def step_problem(step):
    """-> what is wrong with a target's stated worsening step, or None: exactly one of {"factor": >1} or {"add": >0}."""
    if not isinstance(step, dict) or len(step) != 1 or not {"factor", "add"} >= set(step):
        return 'not one of {"factor": n} or {"add": n}'
    k, v = next(iter(step.items()))
    if not is_num(v) or not (1 if k == "factor" else 0) < v < 1e300:
        return "%s must be a number above %d" % (k, 1 if k == "factor" else 0)
    return None


def target_problem(tg):
    """-> what is wrong with one rules["targets"] row, or None. A bad row costs only itself and is said aloud as a
    bad_target flag: an alarm id is `tag:key`, parsed back at the first colon, so a tag may hold no colon."""
    if not isinstance(tg, dict):
        return "not an object: %r" % (tg,)
    if not isinstance(tg.get("key"), str) or not tg["key"]:
        return "no key: %r" % (tg.get("key"),)
    if tg.get("op") not in OPS:
        return "bad op %r on %s" % (tg.get("op"), tg["key"])
    v = tg.get("value")
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not -1e300 < v < 1e300:     # NaN fails the range too
        return "bad value %s on %s" % (str(v)[:40], tg["key"])
    if not isinstance(tg.get("tag"), str) or not tg["tag"] or ":" in tg["tag"]:
        return "bad tag %r on %s" % (tg.get("tag"), tg["key"])
    if tg.get("marks") is not None and not (isinstance(tg["marks"], list) and tg["marks"] and all(
            m in ("MEASURED", "ESTIMATE") for m in tg["marks"])):
        return "bad marks %r on %s" % (tg["marks"], tg["key"])
    if tg.get("worse") is not None and step_problem(tg["worse"]):
        return "bad worse %s on %s: %s" % (str(tg["worse"])[:40], tg["key"], step_problem(tg["worse"]))
    if "expedite_field" in tg:      # the Relentless expedite route it fed retired with the tick (2026-11-13)
        return "expedite_field on %s is retired: nothing expedites any more" % tg["key"]
    return None


def good_targets(rules):
    rows = rules.get("targets")
    return [t for t in rows if not target_problem(t)] if isinstance(rows, list) else []


def judged_elsewhere(p, points):
    """A week runway of a lent account stays a reading (account_pick and role_launch use it) but raises no alarm: its
    loan_runway point is the one judged, for as long as that point exists."""
    return p.get("judged_by") in points


def andon(points, hist, last_measured, rules, now):
    """-> [flag]. points: this pass's key -> point; hist: key -> [(t, v)] MEASURED before this pass;
    last_measured: key -> t of its last MEASURED point before this pass."""
    flags = []
    b, rn, sl = (rules.get(x) for x in ("band", "run", "silent"))
    off = {x for x, sec in (("band", b), ("run", rn), ("silent", sl)) if not isinstance(sec, dict)}
    off |= {"run"} if "band" in off else set()      # the run rule reads the band's baseline
    flags += [{"rule": "bad_rule", "key": "rules." + x, "value": None, "window": "now",
               "detail": "rule section %s missing or not an object: that rule is off, the others run" % x} for x in sorted(off)]
    gone = {k: U("no longer reported by its collector") for k in last_measured if k not in points}
    # a removed collector's keys still in the history are its removal, not a blind instrument
    gone = {k: p for k, p in gone.items() if k.split(".", 1)[0] not in REMOVED_FAMILIES}
    # a nightly red group's key exists only while the group is red: gone while its collector still reports the night is
    # the group cleared (fixed, deleted or parked), not a blind instrument (40 such silent flags, 2026-11-14)
    if any(counts_as_measured(points.get(k) or {}) for k in ("testing.nightly_news", "testing.nightly_known_reds")):
        gone = {k: p for k, p in gone.items() if not k.startswith("testing.red_")}
    def one(k, p):
        v = num(p)
        meas = p.get("m") == "MEASURED" and v is not None
        hs = hist.get(k, [])
        def band():
            if meas and matches(k, b["keys"]) and not matches(k, b["skip"]):
                base = [x for t, x in hs if now - b["baseline_days"] * DAY <= t <= now - b["exclude_recent_h"] * HOUR]
                if len(base) >= b["min_points"]:
                    mu = statistics.fmean(base)
                    sd = statistics.pstdev(base)
                    sig = max(sd, b["sigma_floor_rel"] * abs(mu), b["sigma_floor_abs"])
                    if abs(v - mu) > b["k_sigma"] * sig:
                        flags.append({"rule": "band", "key": k, "value": v, "window": "%dd baseline, %d pts" % (
                            b["baseline_days"], len(base)), "detail": "%.4g outside %.4g +/- %.1f x %.3g" % (
                            v, mu, b["k_sigma"], sig)})
        def run_rule():
            if meas and matches(k, rn["keys"]):
                seq = [x for t, x in hs if t >= now - b["baseline_days"] * DAY] + [v]
                dd = []
                for x in seq:
                    if not dd or x != dd[-1]:
                        dd.append(x)
                n = rn["n"]
                if len(dd) >= n + 1:
                    tail = dd[-(n + 1):]
                    diffs = [tail[i + 1] - tail[i] for i in range(n)]
                    if all(d > 0 for d in diffs) or all(d < 0 for d in diffs):
                        flags.append({"rule": "run", "key": k, "value": v, "window": "last %d changes" % n,
                                      "detail": "%s %d in a row: %.4g -> %.4g" % (
                                          "rising" if diffs[0] > 0 else "falling", n, tail[0], tail[-1])})
        def silent():
            # silence is "no MEASURED reading", the same test last_measured keeps: a MEASURED state string is not silent
            if (not counts_as_measured(p) and matches(k, sl["keys"]) and not matches(k, sl["skip"])
                    and not tt_retired(k, rules) and not judged_elsewhere(p, points)):
                lm = last_measured.get(k)
                lim = next((h for pat, h in sl["per_key"].items() if fnmatch.fnmatchcase(k, pat)), sl["default_h"])
                if lm is not None and now - lm > lim * HOUR:
                    flags.append({"rule": "silent", "key": k, "value": None, "window": "silent %.1f h (limit %g h)" % (
                        (now - lm) / HOUR, lim), "detail": "last MEASURED %s; now %s: %s" % (
                        iso(lm), p.get("m"), (p.get("why") or ""))})
        for name, check in (("band", band), ("run", run_rule), ("silent", silent)):
            try:
                if name not in off:
                    check()
            except Exception as e:  # noqa: BLE001  a bad rule costs that rule on this reading, not the others
                flags.append({"rule": "bad_rule", "key": k, "tag": name, "value": None, "window": "now",
                              "detail": "%s rule failed: %s: %s" % (name, type(e).__name__, str(e))})
    for k, p in sorted({**gone, **points}.items()):
        one(k, p)
    rows = rules.get("targets")
    if not isinstance(rows, list):
        rows = []
        flags.append({"rule": "bad_rule", "key": "rules.targets", "value": None, "window": "now",
                      "detail": "rule section targets missing or not a list: no target alarm can fire"})
    for i, tg in enumerate(rows):
        why = target_problem(tg)
        if why:
            flags.append({"rule": "bad_target", "key": "rules.targets[%d]" % i, "value": None, "window": "now",
                          "detail": "this rule is OFF until ops_watch_rules.json is fixed: " + why})
    for tg in good_targets(rules):
        marks = tg.get("marks") or ["MEASURED"]
        for k, p in sorted(points.items()):
            if not fnmatch.fnmatchcase(k, tg["key"]):
                continue
            v = num(p)
            if v is None or p.get("m") not in marks or judged_elsewhere(p, points):
                continue
            if _cmp(v, tg["op"], tg["value"]):
                flags.append({"rule": "target", "key": k, "value": v, "window": "now", "tag": tg["tag"],
                              "alarm": bool(tg.get("alarm")), "mark": p.get("m"),
                              "detail": "%.4g %s %g%s: %s" % (v, tg["op"], tg["value"],
                                                             "" if p.get("m") == "MEASURED" else " (%s)" % p.get("m"),
                                                             tg.get("why", ""))})
    return flags


def flag_id(f):
    return "%s|%s|%s" % (f["rule"], f.get("tag") or "", f["key"])


def target_state(points, rules):
    """alarm id -> True (crossed) / False (clear) / None (UNMEASURED: hold) for every alarm target."""
    st = {}
    for tg in good_targets(rules):
        if not tg.get("alarm"):
            continue
        marks = tg.get("marks") or ["MEASURED"]
        for k, p in points.items():
            if not fnmatch.fnmatchcase(k, tg["key"]):
                continue
            aid = "%s:%s" % (tg["tag"], k)
            v = num(p)
            new = False if judged_elsewhere(p, points) else (
                None if (v is None or p.get("m") not in marks) else bool(_cmp(v, tg["op"], tg["value"])))
            # two targets on one id: a crossing wins, then a hold; the later row never hides an earlier crossing
            old = st.get(aid, False)
            st[aid] = True if True in (old, new) else None if (old is None or new is None) else False
    return st


# ===================================================================================================== alarms
# Filing writes alarms.json first, on purpose: a name saved before the filing is what stops a repeat. On a full state
# disk that write raises, no alarm files, and the pass dies with the unit failed. DISK_LOW fires at 210 GB, well before.
def alarm_conf(rules):
    # a missing setting costs filing only: the filer's raise leaves each alarm PENDING with the error on its entry
    a = rules.get("alarm")
    a = dict(a) if isinstance(a, dict) else {}
    a["clone"] = os.environ.get("RM_OPS_ALARM_CLONE", a.get("clone"))
    a["parent"] = os.environ.get("RM_OPS_ALARM_PARENT", a.get("parent"))
    return a


def mint_name(tag, known, prefix):
    """A name for a new ledger item. A prefix that already is a whole name (it ends on a twist, as alarm_prefix makes
    it) is used as it stands, and is the same on every call (OPS_ALARMS_FIX_FIXED_ITEM_ID): a repeat of an alarm
    reopens one item through `rimflow live` and is counted. A bare prefix gets a random twist, as before."""
    import secrets
    import ops_ledger as pc
    model = pc._model()
    if prefix in known or not model.mint_problems(prefix, known):
        return prefix
    for _ in range(20):
        name = "%s_%s" % (prefix, secrets.token_hex(2).upper())
        if not model.mint_problems(name, known):
            return name
    raise RuntimeError("no mintable alarm name for " + tag)


def alarm_twist(base):
    """A twist that is the same on every call for one alarm base: four letters from the name itself (a name's last
    word needs a letter, so hex digits alone would not do)."""
    import zlib
    n = zlib.crc32(base.encode())
    return "".join(chr(65 + (n // 26 ** i) % 26) for i in range(4))


def alarm_prefix(tg, tag, key, state, aid, pt=None):
    """One fixed name per alarm. A rule's own name serves a rule with one key; a wildcard key, an unnamed rule, or a
    name another alarm already holds gets the tag or the key's tail so two alarms never share an item. A wildcard
    rule with `subject_field` names its item by what the reading says it is about (owner 2026-11-04: random group
    keys like NIGHTLY_COP_FIX_RED_CIXTEN_JSWD told him nothing), the key's tail only on a clash."""
    base = tg.get("name") or "OPS_ALARM_DIAGNOSE_" + re.sub(r"\W+", "_", tag).upper()
    held = {a.get("name") for k, a in state.items() if k != aid and isinstance(a, dict)}
    subject = ((pt or {}).get("x") or {}).get(tg.get("subject_field") or "") if "*" in tg.get("key", "") else None
    if isinstance(subject, str) and re.fullmatch(r"[A-Z][A-Z0-9_]*", subject):
        base = "%s_%s" % (tg.get("subject_prefix") or "OPS_FIX", subject)
        if "%s_%s" % (base, alarm_twist(base)) not in held:
            return "%s_%s" % (base, alarm_twist(base))
    if "*" in tg.get("key", "") or "%s_%s" % (base, alarm_twist(base)) in held:     # held names carry their twist
        long_base = "%s_%s" % (base, re.sub(r"\W+", "_", key.split(".", 1)[-1]).upper())
        name = "%s_%s" % (long_base, alarm_twist(long_base))
        import ops_ledger as pc
        if not pc._model().mint_problems(name, set()):
            return name
        # the key's tail made it too long or too many words for the namecheck, and mint_name would fail on it 20
        # times (OPS_FILER_FIX_ALARM_NAME_FAILS_GRAMMAR): the rule's own base, with a twist the key makes its own
        return "%s_%s" % (base, alarm_twist(base + "|" + key))
    return "%s_%s" % (base, alarm_twist(base))


def alarm_receiver_problem(conf, tag=None):
    """T2: -> why nobody would pick up an alarm filed with this conf's `for`/`needs`, or None. Asks rimflow
    incident.receiver_problem in the filing clone, the tree whose ledger and relentless rules the item lands under
    (this tree's when that clone has none). A tree that cannot answer is a problem too: an alarm filed blind may rot
    unread."""
    try:
        path = Path(conf["clone"]) / "src/RimMandrake/rimflow/incident.py"
        if not path.is_file():
            path = Path(__file__).resolve().parents[1] / "rimflow/incident.py"
        spec = importlib.util.spec_from_file_location("ops_watch_incident", str(path))
        inc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(inc)
        # `tag`: a drainer may take only some alarms (red_dispatch: the build cop's NIGHTLY_RED items). A filing clone
        # whose incident.py predates the drainer table fails CLOSED: its answer trusts the retired Relentless pool
        if "tag" not in inspect.signature(inc.receiver_problem).parameters:
            return ("receiver check failed: %s predates the drainer table (it would trust the retired Relentless pool); "
                    "sync that clone" % path)
        return inc.receiver_problem(conf.get("for"), conf.get("needs"), tag=tag)
    except Exception as e:     # noqa: BLE001 -- any failure to answer is reported, never swallowed
        return "receiver check failed: %s: %s" % (type(e).__name__, e)


def nobody_of(cache, conf, a):
    """-> alarm_receiver_problem for this alarm's tag (the head of its aid), asked once per tag per pass."""
    tag = (a.get("aid") or "").split(":", 1)[0]
    if tag not in cache:
        cache[tag] = alarm_receiver_problem(conf, tag or None)
    return cache[tag]


RAISE_REASON = "alarm: first in the BENCH queue (build-cop reds: red_dispatch.py launches the fixer)"


def already_filed(out, name):
    """Did rimflow refuse a spawn only because `name` is already an item? (_mint_or_die's 'NAME already exists')"""
    return isinstance(out, str) and ("%s already exists" % name) in out


def refusal_text(out, cap=300):
    """A refusal kept for alarms.json: its head names the reason (rimflow prints the problem first and its help text
    after), its tail ends a traceback, so a long one keeps both. Keeping only the tail once hid 'already exists' behind
    the naming help (OPS_FILER_FIX_ALARM_NAME_FAILS_GRAMMAR)."""
    out = (out or "").strip()
    if len(out) <= cap:
        return out
    half = (cap - 5) // 2
    return out[:half] + " ... " + out[-half:]


FILING_DEFERRED = "deferred: this beat's filing time is spent; the next pass files it"
FILING_PUBLISH_RESERVE_S = 4.0     # left for the publish and the rest of the pass when a metronome beat bounds it
FILING_FIRST_GUESS_S = 3.0         # one spawn + raise before any is measured


def beat_deadline():
    """The metronome's kill time for this pass (METRONOME_DEADLINE, epoch), or None outside a beat."""
    try:
        t = float(os.environ.get("METRONOME_DEADLINE") or "nan")
    except ValueError:
        return None
    return t if math.isfinite(t) else None


def real_filer(todo, conf):
    """todo: [{"name", "title"}] -> {name: None | error}, plus "_publish". Spawns as RUNNER from the dispatch clone
    under QHOME/ingest.lock and publishes its RUNNER shard (testq ingest.py does both). Nothing is filed for a
    receiver nobody picks up (alarm_receiver_problem), and every alarm it files or reopens is raised (first in the
    BENCH queue); build-cop red items are then launched on by rimflow/red_dispatch.py."""
    import fcntl
    path = Path(conf["clone"]) / "src/RimMandrake/Utils/testq/ingest.py"
    spec = importlib.util.spec_from_file_location("ops_watch_ingest", str(path))
    ing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ing)
    nobodies = {}       # per alarm tag: only a NEW item needs it, a note or a reopen goes to one already filed
    res = {}
    # inside a metronome beat (OPS_METRONOME_MIGRATE_CLOCKS_FENCED) the pass is killed at the deadline: a filing is
    # started only when it and the publish still fit, the rest stay PENDING (FILING_DEFERRED, no try counted) and the
    # publish always runs. A kill mid-spawn or mid-push is what this avoids; 13 pending filings overran beat 1749.
    deadline = beat_deadline()
    lock_wait = conf["lock_wait_s"] if deadline is None else max(
        0.0, min(conf["lock_wait_s"], deadline - time.time() - FILING_PUBLISH_RESERVE_S - FILING_FIRST_GUESS_S))
    if deadline is not None and time.time() + FILING_FIRST_GUESS_S + FILING_PUBLISH_RESERVE_S > deadline:
        return {a["name"]: FILING_DEFERRED for a in todo}
    with open(qhome() / "ingest.lock", "w") as lk:
        t0 = time.time()
        while True:
            try:
                fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() - t0 > lock_wait:
                    if deadline is not None:    # a busy lock inside a beat is time spent, not a failed try
                        return {a["name"]: FILING_DEFERRED for a in todo}
                    return {a["name"]: "ingest.lock busy for %d s" % lock_wait for a in todo}
                time.sleep(min(2, max(0.2, lock_wait / 4)))
        n = 0
        per = FILING_FIRST_GUESS_S
        for a in todo:
            if deadline is not None and time.time() + per + FILING_PUBLISH_RESERVE_S > deadline:
                res[a["name"]] = FILING_DEFERRED
                continue
            began = time.time()
            try:    # one alarm the spawn cannot carry (a NUL in an argument) costs itself, not the alarms behind it
                if a.get("note_only"):
                    rc, out = ing.rimflow("note", a["item"], "--text", a["text"])
                elif a.get("block_only"):   # a duplicate waits on its cause's repair; the block lifts when it closes (WP-04)
                    rc, out = ing.rimflow("block", a["item"], "--kind", "item", "--on", a["on"], "--until", "done",
                                          "--reason", a["reason"])
                elif a.get("reopen"):     # a repeat: the same item goes back to work and the outage is counted
                    rc, out = ing.rimflow("live", a["name"], "--result", "broken", "--detail", a["title"])
                    if rc != 0 and "retired item holds no promise" in (out or ""):
                        # the fixed item was dropped or superseded: a retired item cannot be reopened, so the alarm
                        # files a successor and keeps that name from here on (OPS_WATCH_FIX_RETIRED_ALARM_ITEM)
                        for k in range(1, 6):
                            w = a["name"].split("_")      # a name has 3-7 words: a 7-word base gives up its last one
                            new = "%s_%s" % ("_".join(w[:6]), alarm_twist("%s#%d" % (a["name"], k)))
                            rc, out = ing.rimflow("spawn", "--from", conf["parent"], "--for", conf["for"], "--needs", conf["needs"],
                                                  "--name", new, "--title", a["title"],
                                                  "--why", "ops_watch alarm (deterministic, no AI): %s; %s was retired" % (a["aid"], a["name"]))
                            if rc != 0 and already_filed(out, new):
                                # an earlier pass spawned this twist and died before saving it (the arena fan-out,
                                # 2026-11-06 05:01-05:06Z: 5 successors, one per killed beat). It is this alarm's
                                # successor: adopt it, and take the next twist only when it is retired too
                                rc, out = ing.rimflow("live", new, "--result", "broken", "--detail", a["title"])
                                if rc != 0 and "retired item holds no promise" in (out or ""):
                                    rc, out = 1, "%s already filed" % new
                                    continue
                            break
                        if rc != 0 and already_filed(out, new):
                            # all five twists exist: the last was filed by an earlier pass whose ledger read lags, so the
                            # alarm adopts it instead of failing forever (stuck 11-05 23:09Z on ..._AT_END_HPCK)
                            rc = 0
                        if rc == 0:
                            res.setdefault("_renamed", {})[a["name"]] = new
                            a["name"] = new
                elif nobody_of(nobodies, conf, a):     # stays PENDING with the reason on its entry, retried every pass
                    rc, out = 1, "no receiver: " + nobodies[a.get("aid", "").split(":", 1)[0]]
                else:
                    rc, out = ing.rimflow("spawn", "--from", conf["parent"], "--for", conf["for"], "--needs", conf["needs"],
                                          "--name", a["name"], "--title", a["title"],
                                          *(["--spec", a["spec"]] if a.get("spec") else []),
                                          "--why", "ops_watch alarm (deterministic, no AI): " + a["aid"])
                    if rc != 0 and already_filed(out, a["name"]):
                        # the filing clone's ledger holds it: an earlier pass filed it and this tree's ledger read lags
                        # (OPS_FILER_FIX_ALARM_NAME_FAILS_GRAMMAR). Filed, not failed; it was raised when it was filed
                        res[a["name"]] = None
                        res.setdefault("_already", []).append(a["name"])
                        continue
                if rc == 0 and not a.get("note_only"):
                    rrc, rout = ing.rimflow("raise", a["name"], "--reason", RAISE_REASON)
                    if rrc != 0:    # filed but not first: the alarm stands (a retry would re-spawn), the miss is logged
                        res.setdefault("_raise", {})[a["name"]] = rout
            except (ValueError, OSError) as e:
                rc, out = 1, "%s: %s" % (type(e).__name__, e)
            res[a["name"]] = None if rc == 0 else refusal_text(out)
            n += rc == 0
            per = max(per, time.time() - began)
        if n and deadline is not None and time.time() + FILING_PUBLISH_RESERVE_S / 2 > deadline:
            # no room left to push before the kill: testq's ingest keeps the lines and its next publish carries them
            res["_publish"] = "deferred: no time left in this beat; the next testq publish carries it"
            return res
        res["_publish"] = ing.publish(n, message="ledger: ops_watch alarm(s) %s" % ", ".join(
            a["name"] for a in todo if res.get(a["name"]) is None and a["name"] not in res.get("_already", []))) if n else "nothing to publish"
    return res


def is_token_key(key):
    """Is this KPI key a token, runway, quota or burn reading (Operations' alone)?"""
    return str(key).split(".", 1)[0] in TOKEN_FAMILIES


def token_alarm_title(aid):
    """An Operations-only alarm's title: its tag and family, never a key's account, value or line (review V, V2)."""
    tag, key = (aid.split(":", 1) + [""])[:2]
    return "Ops alarm for Operations: %s on %s; the reading is in digest.md" % (tag, key.split(".", 1)[0])


def worse_count(cur):
    """How many times this alarm has been re-raised for getting worse; a bad saved count restarts it."""
    n = cur.get("worse_n", 0)
    return n if isinstance(n, int) and not isinstance(n, bool) else 0


def tell_conductor(path, line, aid, now, log, cur=None):
    """One line on the Conductor log, when this rule owes one. A log that cannot be written is said in the log and, given
    the alarm's state `cur`, the line is kept owed on it (conductor_owed) for retry_conductor_lines to retry each pass:
    the alarm is OPEN by then and signal_watch skips OPEN, so a dropped line would never reach the Conductor
    (OPS_ALARM_FIX_LOG_LINE_NEVER_RETRIED). True when the line was written."""
    if not path:
        return True
    try:
        conductor_guard().refuse_if_test(path)
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n" + line)
        return True
    except OSError as e:
        log.append({"ts": iso(now), "event": "conductor_log_failed", "aid": aid, "error": str(e)})
        if isinstance(cur, dict):
            owed = cur.get("conductor_owed")
            owed = owed if isinstance(owed, list) else []
            cur["conductor_owed"] = owed + [{"path": str(path), "line": line}]
        return False


def retry_conductor_lines(state, now, log):
    """Retry every Conductor line still owed on an alarm; a delivered one is owed no more, a malformed one is dropped aloud."""
    for aid, cur in state.items():
        if not isinstance(cur, dict) or "conductor_owed" not in cur:
            continue
        owed = cur.pop("conductor_owed")
        if not isinstance(owed, list):
            log.append({"ts": iso(now), "event": "conductor_owed_unreadable", "aid": aid})
            continue
        for o in owed:
            if not (isinstance(o, dict) and isinstance(o.get("path"), str) and isinstance(o.get("line"), str)):
                log.append({"ts": iso(now), "event": "conductor_owed_unreadable", "aid": aid})
            elif tell_conductor(o["path"], o["line"], aid, now, log, cur):
                log.append({"ts": iso(now), "event": "conductor_log_retried", "aid": aid})


def _tries(cur):
    """A saved retry count, or 0 for one that cannot be counted from: never a raise after the filing succeeded."""
    n = cur.get("tries", 0)
    return n if isinstance(n, int) and not isinstance(n, bool) else 0


def fresh_news(cur, aid, points, rules):
    """The names in a note_field target's reading that this alarm has not told anyone yet, and all of them. A count can
    stand still across a line while what it counts changes: a new red on an open alarm must not vanish into it."""
    key = aid.split(":", 1)[1]
    tg = next((t for t in good_targets(rules) if t.get("alarm") and t.get("note_field") and t["tag"] == aid.split(":", 1)[0]
               and fnmatch.fnmatchcase(key, t["key"])), None)
    names = ((points.get(key) or {}).get("x") or {}).get(tg["note_field"]) if tg else None
    if not isinstance(names, list):
        return [], []
    told = cur.get("noted")
    told = told if isinstance(told, list) else []
    return [n for n in names if n not in told], names


def titled_names(title, pt, tg):
    """The note_field names a filing's title already shows: each name, or the short form its collector gave in x.titled
    ({name: text}), found in the title as cut. Those count as told; a name the cut dropped is said by the first note."""
    x = (pt or {}).get("x") or {}
    names = x.get(tg.get("note_field")) if tg.get("note_field") else None
    short = x.get("titled") if isinstance(x.get("titled"), dict) else {}
    if not isinstance(names, list):
        return []
    return [n for n in names if isinstance(n, str) and (n in title or (isinstance(short.get(n), str) and short[n]
                                                                        and short[n] in title))]


def severity_of(p):
    """A reading's severity: the class the ranges block stamped on it, else the class its collector judged (x.state)."""
    for s in (p.get("class"), (p.get("x") or {}).get("state")):
        if s in SEVERITY:
            return s
    return None


def step_crossed(told, v, op, step):
    """Has v moved a whole stated step past the value last told, the way this target's op calls worse? A factor cannot
    step from zero or below (nothing doubles from there), so such a reading breaks nothing."""
    if not step or not is_num(told) or not is_num(v):
        return False
    up = op in (">", ">=")
    if "add" in step:
        return v >= told + step["add"] if up else v <= told - step["add"]
    return told > 0 and (v >= told * step["factor"] if up else v <= told / step["factor"])


def worse_news(cur, aid, points, rules):
    """A crossed alarm that has already told someone: (what got worse, what to remember once that is told), or None.
    `told` is a ratchet, the worst reading told so far, so a value that wobbles back and returns says nothing twice. An
    alarm filed before it was kept takes today's reading as its baseline: a deploy re-raises nothing."""
    tag, key = aid.split(":", 1)
    p = points[key]
    v, sev = num(p), severity_of(p)
    told = cur.get("told")
    if not isinstance(told, dict):
        cur["told"] = {"v": v, "class": sev}
        return None
    rows = [t for t in good_targets(rules) if t.get("alarm") and t["tag"] == tag and fnmatch.fnmatchcase(key, t["key"])]
    tg = next((t for t in rows if v is not None and _cmp(v, t["op"], t["value"])), rows[0] if rows else {})
    # a class never told (no class at the filing): a crossed alarm is at least distressed, so only emergency rises from it
    was = told.get("class") if told.get("class") in SEVERITY else "distressed"
    said, keep = [], dict(told)
    if sev is not None and SEVERITY.index(sev) > SEVERITY.index(was):
        said.append("severity %s -> %s" % (was, sev))
        keep["class"] = sev
    if step_crossed(told.get("v"), v, tg.get("op"), tg.get("worse")):
        said.append("%s -> %s %s, the rule's step is %s" % (fmt(told.get("v")), fmt(v), p.get("unit") or "", json.dumps(tg["worse"])))
        keep["v"] = v
    return ("; ".join(said), keep, tg.get("conductor_log")) if said else None


def stale_for_close(point, closes):
    """True when a reading's `night` is no later than the item's last close: what it measured ran before the fix that
    closed it, so it is no evidence the fix died. False when either time is missing or unreadable. Pure."""
    night = ((point or {}).get("x") or {}).get("night") if isinstance(point, dict) else None
    try:
        last = max(float(c) for c in closes) if closes else None
    except (TypeError, ValueError):
        return False
    t = epoch(night) if isinstance(night, str) else None
    return bool(t and last and t <= last)


def _book_locked(fn):
    """The cause book's writer lock (cause_book.locked) from the pass's load of causes.json to its save, the filing
    between them included: role_launch's cause attach (RELENTLESS_ROLE_LAUNCH_HARDEN_CAUSE_BOOK) waits a few seconds
    for it and retries next tick, so its reading is never erased by this pass's save of an older load."""
    def wrap(*a, **k):
        with cause_mods()[0].locked(ops_dir() / "causes.json"):
            return fn(*a, **k)
    wrap.__name__ = fn.__name__
    wrap.__doc__ = fn.__doc__
    return wrap


@_book_locked
def run_alarms(points, rules, now, known_ids, filer, open_ids=None, closed_at=None, cause_tree=None):
    """Edge-triggered: file once on a NEW crossing, keep it while it holds, re-arm when it clears. A target with note_field
    also says what is new while it stays crossed: a note on its open item, or, the item closed (open_ids), a reopen. So
    does an alarm that got worse (ALARM_REPEAT_FIX_BREAK_ON_WORSE: its severity rose, or its value passed the target's
    stated `worse` step), which also gives the Conductor a line and, through worse_n, Operations a fresh alarm run.
    closed_at ({item: [close epoch, ...]}, the flow collector's ctx["closes"]): a closed item is not reopened on a
    reading whose `night` predates its last close (NIGHTLY_COP_FIX_RED_ENVEHB_GOEW): that night ran before the fix.
    cause_tree: the clone whose committed tree says which test paths are gone (jam_classes.cause_key), or that
    exists(path) callable itself (a replay's recorded tree); None judges
    none gone, and every alarm is its own cause (its id), as before the cause book."""
    p = ops_dir() / "alarms.json"
    state = read_json(p) if p.exists() else {}
    if not isinstance(state, dict):
        # the dedup state is there but unreadable: filing now could file every open alarm a second time. Hold all
        # filing (and leave the file for a human) until it reads again.
        return {"_alarm_state": {"state": "UNREADABLE", "error": "%s exists but is not a readable JSON object: alarm "
                                 "filing held this pass" % p}}
    log = []
    # an alarm of a removed family has no target left that could clear it: it leaves with its family
    for aid in [a for a in state if a.split(":", 1)[-1].split(".", 1)[0] in REMOVED_FAMILIES]:
        was = state.pop(aid)
        log.append({"ts": iso(now), "event": "family_removed", "aid": aid,
                    "item": was.get("item") if isinstance(was, dict) else None})
    # before any step: a line owed from an earlier pass is retried even when this pass clears its alarm
    retry_conductor_lines(state, now, log)
    ts = target_state(points, rules)
    conf = alarm_conf(rules)
    todo = []
    said_causes = set()     # this pass's Conductor lines, one per cause (conductor_line_owed)
    # OPSWATCH_BUILD_ALARMS_KEYED_BY_CAUSE: one repair item per cause. The book is read before any step; a book that
    # cannot be read holds no alarm (each files on its own id, as before the book) and is said aloud
    cb, jc = cause_mods()
    exists = (cause_tree if callable(cause_tree) else jc.tree_exists(cause_tree)) if cause_tree else None
    bp = ops_dir() / "causes.json"
    try:
        book = cb.load(bp)
    except (ValueError, OSError) as e:
        book = None
        log.append({"ts": iso(now), "event": "cause_book_unreadable", "error": str(e)})
    if book is not None:
        for r in cb.reconcile(book, known_ids, open_ids, state, now):
            log.append(dict(r, ts=iso(now)))
        # alarms already OPEN on items of their own, filed before the book knew their cause: the first holds the
        # cause, the others are blocked on it (cause_book dependents), and their notes go on as before
        for aid in sorted(state, key=lambda a: str((state[a] or {}).get("filed") or "") if isinstance(state[a], dict) else ""):
            cur = state[aid]
            if not (isinstance(cur, dict) and cur.get("state") == "OPEN" and isinstance(cur.get("item"), str)
                    and ts.get(aid) and open_ids is not None and cur["item"] in open_ids
                    and not is_token_key(aid.split(":", 1)[-1])):
                continue
            ck = cur.get("cause") or jc.cause_key(aid, points.get(aid.split(":", 1)[1]), exists)
            cur["cause"] = ck
            rec = cb.live(book, ck)
            if rec is None:
                cb.begin(book, ck, aid, cur["item"], now)
                cb.filed(book, ck, cur["item"], now)
            elif rec["item"] != cur["item"] and cb.attach(book, ck, aid, cur.get("title"), now, own_item=cur["item"], open_ids=open_ids):
                log.append({"ts": iso(now), "event": "cause_duplicate", "aid": aid, "item": cur["item"], "cause": ck,
                            "repair": rec["item"]})
    try:
        clear_passes = max(1, int(conf.get("clear_passes", 1)))
    except (TypeError, ValueError, OverflowError):     # a bad value reads as the safest: never an alarm cleared early, never a dead pass
        clear_passes = 4
        log.append({"ts": iso(now), "event": "bad_clear_passes", "value": str(conf.get("clear_passes"))[:40]})
    def one(aid):
        """One alarm's step. A malformed entry or a failure here costs that alarm only, and is said aloud."""
        crossed = ts.get(aid)          # True crossed / False clear / None UNMEASURED or no reading: hold
        cur = state.get(aid)
        if aid in state and not isinstance(cur, dict):
            # unreadable dedup state for this alarm alone: hold it (filing could repeat it) until it clears
            cur = state[aid] = {"state": "UNREADABLE", "since": iso(now),
                                "error": "alarms.json entry was not an object: filing held for this alarm"}
            log.append({"ts": iso(now), "event": "bad_state_entry", "aid": aid})
        if cur and not isinstance(cur.get("name", ""), str):
            cur.pop("name")     # a saved name of the wrong type cannot be retried: mint a fresh one
            log.append({"ts": iso(now), "event": "bad_saved_name", "aid": aid})
        if cur and is_token_key(aid.split(":", 1)[-1]) and (cur.get("item") or cur.get("state") == "PENDING"):
            # filed on a seat queue before review V (V2): from now on it is Operations' alone. The old ledger item is
            # kept as legacy_item (never noted again: a clear note would carry the reading onto a blind-read item)
            if cur.get("item"):
                cur["legacy_item"] = cur["item"]
            cur.update(state="OPEN", item=None, error=None, title=token_alarm_title(aid), **{"for": "Operations"})
            cur.pop("name", None)
            log.append({"ts": iso(now), "event": "moved_to_operations", "aid": aid, "legacy_item": cur.get("legacy_item")})
        if cur and cur.get("state") == "PENDING" and cur.get("name") in known_ids and not cur.get("reopen"):
            if open_ids is not None and cur["name"] not in open_ids and (not crossed or stale_for_close(
                    points.get(aid.split(":", 1)[1]), (closed_at or {}).get(cur["name"]))):
                # SELFTEST_FIX_LIVE_QUEUE_QBHV: closed since, but the only reading's night ran before that close, so it
                # is no evidence the fix died. SELFTEST_FIX_EXTRA_ART_COMMISSION_UBZM: nor is no crossed reading this
                # pass (a compose pass drops a carried reading: crossed None), which marked it a reopen that file_held
                # then filed on the pre-close night. Acknowledged on its item; the OPEN route's checks judge the next one
                cur.update(state="OPEN", item=cur["name"], error=None)
                cur.pop("deferred_at", None)
                log.append({"ts": iso(now), "event": "found_closed_stale_night" if crossed else "found_closed_not_crossed",
                            "aid": aid, "item": cur["name"]})
            elif open_ids is not None and cur["name"] not in open_ids:
                # on the ledger but closed since: acknowledging it would tell nobody. Keep it PENDING as a reopen
                cur["reopen"] = True
                log.append({"ts": iso(now), "event": "found_closed", "aid": aid, "item": cur["name"]})
            else:
                # filed by a pass that died before saving its state: the ledger has it, never file it twice
                cur.update(state="OPEN", item=cur["name"], error=None, filed=cur.get("filed") or iso(now))
                log.append({"ts": iso(now), "event": "found_filed", "aid": aid, "item": cur["name"]})
                # that pass may have died before its Conductor line too: the told ledger says whether it is still owed
                if cur.get("conductor_log") and conductor_line_owed(aid.split(":", 1)[1], said_causes):
                    tell_conductor(cur["conductor_log"], "- %s ops_watch ALARM %s: %s\n" % (
                        iso(now), cur["name"], cur.get("title") or aid), aid, now, log, cur)
        if crossed is False and cur:
            # An unfiled PENDING clears here too, logged cleared_unfiled, on purpose: filing a condition that has gone
            # would send a seat after nothing. A filing outage with the condition standing keeps retrying.
            # hysteresis: clear only after clear_passes clear readings in a row, so a reading that wobbles across
            # the line does not file a fresh item on every wobble
            seen = cur.get("clear_seen", 0)     # a bad saved count restarts the count; raising here would never clear
            cur["clear_seen"] = (seen if isinstance(seen, int) and not isinstance(seen, bool) else 0) + 1
            if cur["clear_seen"] >= clear_passes:
                log.append({"ts": iso(now), "event": "cleared" if cur.get("state") == "OPEN" else "cleared_unfiled",
                            "aid": aid, "item": cur.get("item")})
                if cur.get("item") and filer:
                    key = aid.split(":", 1)[1]
                    todo.append({"note_only": True, "item": cur["item"], "name": "note:" + aid,
                                 "text": "ops_watch: cleared at %s (%s now %s)" % (
                                     iso(now), key, (points.get(key) or {}).get("v"))})
                if cur.get("conductor_owed"):   # a raise line never delivered is stale now; dropped aloud, not silently
                    log.append({"ts": iso(now), "event": "conductor_owed_dropped", "aid": aid,
                                "lines": len(cur["conductor_owed"]) if isinstance(cur["conductor_owed"], list) else None})
                state.pop(aid, None)
                return
        if crossed and cur:
            cur["clear_seen"] = 0
        if cur and cur.get("state") == "UNREADABLE":
            return
        if cur and cur.get("state") == "OPEN" and not is_token_key(aid.split(":", 1)[-1]) \
                and not (cur.get("item") and isinstance(cur["item"], str) and (cur["item"] in known_ids or not known_ids or not crossed)):
            # OPEN on no item the ledger knows told nobody: file it, or a corrupt entry acknowledges the alarm for good.
            # known_ids is every item ever filed, closed ones too; empty means the ledger was not read, so nothing is judged
            cur.update(state="PENDING", item=None)
            log.append({"ts": iso(now), "event": "open_without_item", "aid": aid})
        if cur and cur.get("state") == "OPEN":
            if crossed:
                cur["last_seen"] = iso(now)
            fresh, names = fresh_news(cur, aid, points, rules) if crossed else ([], [])
            worse = worse_news(cur, aid, points, rules) if crossed else None
            if worse and is_token_key(aid.split(":", 1)[-1]):
                # Operations' alone, no item to note: worse_n is what it sees, as a new alarm key. No value in the log line
                cur.update(told=worse[1], worse_n=worse_count(cur) + 1)
                log.append({"ts": iso(now), "event": "worse", "aid": aid})
                return
            # OPS_ALARM_FIX_CLOSED_TICKET_SILENCES_FAULT: its item closed while the reading still stands crossed. Closing
            # the ticket is not fixing the fault: with nothing new to say this returned and the alarm stayed silent for
            # good, so it reopens here even with no news. open_ids None means the ledger was not read: nothing judged
            closed = bool(crossed and open_ids is not None and cur.get("item") and cur["item"] not in open_ids)
            if closed and stale_for_close(points.get(aid.split(":", 1)[1]), (closed_at or {}).get(cur["item"])):
                return      # NIGHTLY_COP_FIX_RED_ENVEHB_GOEW: the only reading is from before the close; the next one judges
            if not fresh and not worse and not closed:
                return
            if open_ids is None or cur.get("item") in open_ids:
                shown, used = [], 0     # whole names up to 600 chars; one that does not fit stays unnoted, said next pass
                for n in fresh:
                    add = len(str(n)) + (2 if shown else 0)
                    if shown and used + add > 600:
                        break
                    shown.append(n)
                    used += add
                left = fresh[len(shown):]
                names = [n for n in names if n not in left]
                lines = (["new at %s: %s%s" % (iso(now), "; ".join(map(str, shown)),
                                               " (+%d more next pass)" % len(left) if left else "")] if fresh else []) + (
                    ["WORSE at %s: %s" % (iso(now), worse[0])] if worse else [])
                key = aid.split(":", 1)[1]
                tg = next((t for t in good_targets(rules) if t.get("alarm") and t["tag"] == aid.split(":", 1)[0]
                           and fnmatch.fnmatchcase(key, t["key"])), {})
                todo.append({"note_only": True, "item": cur["item"], "name": "note:" + aid, "aid": aid,
                             "noted": names if fresh else None, "told": worse[1] if worse else None,
                             "worse": worse[0] if worse else None, "conductor_log": worse[2] if worse else None,
                             "text": "ops_watch: " + "; ".join(lines)})
                return
            if worse:
                cur["worse_n"] = worse_count(cur) + 1
            cur.update(state="PENDING", item=None, name=cur.get("item"), reopen=True, tries=0)
            log.append({"ts": iso(now), "event": "reopen_for_news" if fresh else "reopen_for_worse" if worse
                        else "reopen_closed_still_crossed", "aid": aid, "item": cur["name"]})
        if not crossed:
            if cur and cur.get("name") and cur.get("title"):
                # PENDING, not crossed now (UNMEASURED, or clear but not for clear_passes yet): the crossing was
                # real, so keep retrying the filing under the name and title it got when it crossed
                todo.append({"aid": aid, "name": cur["name"], "title": cur["title"], "reopen": bool(cur.get("reopen")),
                             "conductor_log": cur.get("conductor_log"), "key": aid.split(":", 1)[1],
                             "cause": cur.get("cause"), "spec": cur.get("spec")})
            return
        key = aid.split(":", 1)[1]
        tag = aid.split(":", 1)[0]
        pt = points[key]
        rows = [t for t in good_targets(rules) if t.get("alarm") and t["tag"] == tag and fnmatch.fnmatchcase(key, t["key"])]
        tg = next((t for t in rows if num(pt) is not None and _cmp(num(pt), t["op"], t["value"])), rows[0])
        if not cur:
            cur = {"state": "PENDING", "since": iso(now), "tries": 0}
            state[aid] = cur
            log.append({"ts": iso(now), "event": "crossed", "aid": aid, "v": pt.get("v"), "m": pt.get("m")})
        cur["told"] = {"v": num(pt), "class": severity_of(pt)}      # what this filing says; worse_news measures from it
        if is_token_key(key):
            # an account/runway/burn alarm is Operations' alone: never a ledger item (`rimflow queue` is read by the
            # token-blind roles), so nothing is filed; Operations' alarm runs read alarms.json and digest.md (V2)
            cur.update(state="OPEN", item=None, error=None, filed=iso(now), title=token_alarm_title(aid),
                       **{"for": "Operations"})
            log.append({"ts": iso(now), "event": "opened_for_operations", "aid": aid})
            return
        ck = None
        if book is not None:
            ck = jc.cause_key(aid, pt, exists)
            rec = cb.live(book, ck)
            if rec is not None and (rec.get("aids") or [None])[0] != aid:
                # another alarm of this cause holds its repair item: this one attaches to it and files nothing
                own = cur.get("item") or cur.get("name")
                said = (pt.get("x") or {}).get("said") or pt.get("v")
                cb.attach(book, ck, aid, said, now, own_item=own, open_ids=open_ids)
                cur.update(state="OPEN", item=rec["item"], name=rec["item"], cause=ck, error=None, reopen=False,
                           filed=cur.get("filed") or iso(now), title=cur.get("title") or "attached to %s" % rec["item"])
                log.append({"ts": iso(now), "event": "attached", "aid": aid, "item": rec["item"], "cause": ck,
                            "record": rec["state"]})
                if rec["state"] == "open":
                    todo.append({"note_only": True, "item": rec["item"], "name": "note:" + aid, "aid": aid,
                                 "text": "ops_watch: %s attached at %s (same cause %s): %s" % (
                                     aid, iso(now), ck, str(said))})
                return
        if not cur.get("name"):  # mint once; a retry keeps the saved name
            taken = set(known_ids) | {a["name"] for a in state.values() if isinstance(a, dict) and isinstance(a.get("name"), str)}
            try:
                cur["name"] = mint_name(tag, taken, alarm_prefix(tg, tag, key, state, aid, pt))
                # the name is already on the ledger: a repeat of an alarm that filed before. It reopens that item.
                cur["reopen"] = cur["name"] in known_ids
            except Exception as e:  # noqa: BLE001  one unnameable alarm stays PENDING and counted (signal_watch tells); the pass goes on
                cur.update(error=str(e), tries=_tries(cur) + 1)
                log.append({"ts": iso(now), "event": "mint_failed", "aid": aid})
                return
        if ck is not None:
            if cb.live(book, ck) is None:
                cb.begin(book, ck, aid, cur["name"], now)     # saved with alarms.json before the spawn
            cur["cause"] = ck
        title = "Ops alarm %s: %s = %s %s(%s), line %s %g" % (tag, key, pt.get("v"), (pt.get("unit") or "") + " ",
                                                            pt.get("m"), tg["op"], tg["value"])
        said = (pt.get("x") or {}).get(tg["title_field"]) if tg.get("title_field") else None   # what crossed, first
        said = said[0] if isinstance(said, list) and said else said
        if isinstance(said, str) and said:
            title = "Ops alarm %s: %s -- %s" % (tag, said, title.split(": ", 1)[1])
        cur["title"] = title[:160]  # cut-ok: an item title (one line); a name the title cut is told in the first note (titled_names)
        cur["noted"] = titled_names(cur["title"], pt, tg)   # what the title shows is told; a name it cut, the first note says
        cur["conductor_log"] = tg.get("conductor_log")     # a retry that files later still owes the Conductor its line
        cur["spec"] = red_launch_checks(pt)
        todo.append({"aid": aid, "name": cur["name"], "title": cur["title"], "conductor_log": tg.get("conductor_log"),
                     "key": key, "reopen": bool(cur.get("reopen")), "cause": cur.get("cause"),
                     "spec": cur["spec"]})
    for aid in sorted(set(ts) | set(state)):
        try:
            one(aid)
        except Exception as e:  # noqa: BLE001  stays PENDING and counted, with the reason, and the pass goes on
            why = "alarm step raised %s: %s" % (type(e).__name__, str(e))
            cur = state.get(aid)
            cur = cur if isinstance(cur, dict) else state.setdefault(aid, {"state": "PENDING", "since": iso(now), "tries": 0})
            cur["error"] = why
            log.append({"ts": iso(now), "event": "step_failed", "aid": aid, "error": why})
    if book is not None:
        todo.extend(cause_block_todo(k, d, r) for k, d, r in cb.queued_blocks(book))
    if todo and filer and beat_deadline() is not None:
        # a beat files what fits and defers the rest: the longest-untried go first, so no alarm starves behind a slow one
        todo.sort(key=lambda a: str((state.get(a.get("aid")) or {}).get("last_try") or ""))
    if todo and filer:
        atomic_json(p, state)   # the name is on disk before the spawn: a pass that dies mid-filing retries it, not a new one
        if book is not None:
            cb.save(bp, book)   # and its cause record: a restart completes it (cause_book.reconcile), never a second
    if todo:
        if filer:
            try:
                res = filer(todo, conf)
            except Fenced:      # a lost generation is not a failed try: run() stops the pass
                raise
            except Exception as e:  # noqa: BLE001  a filing that raises stays PENDING; the pass still reports
                res = {a["name"]: "filer raised %s: %s" % (type(e).__name__, str(e)) for a in todo}
        else:
            res = {a["name"]: "filing off (run without --file-alarms)" for a in todo}
        settle_filing(state, todo, res, filer, now, log, said_causes, book)
    atomic_json(p, state)
    if book is not None:
        cb.save(bp, book)
    if log:
        with open(ops_dir() / "alarms_log.jsonl", "a", encoding="utf-8") as f:
            for r in log:
                f.write(json.dumps(r, sort_keys=True) + "\n")
    return state


def settle_filing(state, todo, res, filer, now, log, said_causes, book=None):
    """Each todo alarm's filing result into its alarms.json entry and the alarm log: OPEN on its item, the error kept,
    or a deferral counted (no try). Shared by the alarm pass (run_alarms) and a light beat's held filing (file_held)."""
    cb = cause_mods()[0] if book is not None else None
    for a in todo:
        if a.get("block_only"):     # a duplicate's item blocked on its cause's repair; a failure stays queued, retried
            err = res.get(a["name"])
            if err is None and cb:
                cb.blocked(book, a["cause"], a["item"])
                log.append({"ts": iso(now), "event": "cause_blocked", "item": a["item"], "repair": a["on"], "cause": a["cause"]})
            elif filer and err != FILING_DEFERRED:
                log.append({"ts": iso(now), "event": "cause_block_failed", "item": a["item"], "error": str(err)})
            continue
        if a.get("note_only"):
            cur = state.get(a.get("aid"))
            if res.get(a["name"]) is None and isinstance(cur, dict):    # unsaid on a failed note: the next pass says it again
                if a.get("noted"):
                    cur["noted"] = a["noted"]
                if a.get("told"):
                    cur.update(told=a["told"], worse_n=worse_count(cur) + 1)
                    log.append({"ts": iso(now), "event": "worse", "aid": a["aid"], "item": a["item"], "said": a["worse"]})
                    # not conductor_line_owed: an open incident of this cause holds that line, and telling past it is the point
                    tell_conductor(a.get("conductor_log"), "- %s ops_watch WORSE %s: %s\n" % (iso(now), a["item"], a["worse"]), a["aid"], now, log, cur)
            continue
        try:
            cur = state[a["aid"]]
            err = res.get(a["name"])
            if filer and err == FILING_DEFERRED:     # not a try: last_try and the last real error stand
                cur["deferred_n"] = int(cur.get("deferred_n") or 0) + 1
                cur["deferred_at"] = iso(now)       # file_held takes it on the next light beat
                log.append({"ts": iso(now), "event": "file_deferred", "aid": a["aid"], "n": cur["deferred_n"]})
                continue
            cur["tries"] = _tries(cur) + (1 if filer else 0)
            cur["last_try"] = iso(now)
            cur.pop("deferred_at", None)        # a real try: from here the alarm pass retries it, as before
            if err is None:
                cur.update(state="OPEN", item=a["name"], name=a["name"], error=None, filed=iso(now))   # name: a successor stays the alarm's item
                if cb and a.get("cause"):
                    old = cb.filed(book, a["cause"], a["name"], now)
                    for other in (book.get(a["cause"]) or {}).get("aids") or ():   # attached under the old name
                        o = state.get(other)
                        if other != a["aid"] and isinstance(o, dict) and o.get("item") == old and old != a["name"]:
                            o.update(item=a["name"], name=a["name"])
                # the item is in the RUNNER shard whatever _publish says: a publish that failed is retried by the
                # next testq ingest (testq/ingest.py _publish keeps the lines), so OPEN is right either way
                log.append({"ts": iso(now), "event": "found_filed" if a["name"] in (res.get("_already") or []) else "filed",
                            "aid": a["aid"], "item": a["name"], "publish": res.get("_publish")})
                if (res.get("_raise") or {}).get(a["name"]):
                    log.append({"ts": iso(now), "event": "raise_failed", "aid": a["aid"], "item": a["name"],
                                "error": res["_raise"][a["name"]]})
                # a rule that also owes the Conductor a line (rules key conductor_log), one per cause: an outage is one ring
                if a.get("conductor_log") and conductor_line_owed(a.get("key"), said_causes):
                    tell_conductor(a["conductor_log"], "- %s ops_watch ALARM %s: %s\n" % (iso(now), a["name"], a["title"]), a["aid"], now, log, cur)
            else:
                cur["error"] = err
                if filer:
                    log.append({"ts": iso(now), "event": "file_failed", "aid": a["aid"], "error": err})
        except Exception as e:  # noqa: BLE001  a corrupt counter costs this alarm's bookkeeping; found_filed recovers it
            log.append({"ts": iso(now), "event": "step_failed", "aid": a["aid"], "error": str(e)})


def held_todo(state):
    """The PENDING alarms the alarm pass deferred (deferred_at), oldest try first, as filer todo entries."""
    todo = []
    for aid, cur in sorted(state.items(), key=lambda kv: str((kv[1] or {}).get("last_try") or "")
                           if isinstance(kv[1], dict) else ""):
        if not (isinstance(cur, dict) and cur.get("state") == "PENDING" and cur.get("deferred_at")
                and isinstance(cur.get("name"), str) and cur.get("name") and isinstance(cur.get("title"), str)):
            continue
        todo.append({"aid": aid, "name": cur["name"], "title": cur["title"], "conductor_log": cur.get("conductor_log"),
                     "key": aid.split(":", 1)[-1], "reopen": bool(cur.get("reopen")),
                     "cause": cur.get("cause")})
    return todo


FILING_QUEUE = "filing_queue.json"


def queue_filer(todo, conf):
    """The alarm pass's filer inside a beat (run(held_detach=True)): it files nothing. A spawn or reopen is deferred, so
    it goes PENDING and the detached filer (start_held_filer) files it; a note is queued for that filer. A real filing
    (rimflow spawn or live, raise, publish) took 17.7 s wall for one held alarm on 2026-11-22, more than the whole
    sense limit, so an alarm pass that filed in the beat was killed mid-filing (21:01 PST, stage alarms)."""
    notes = [a for a in todo if a.get("note_only") and a.get("name")]
    if notes:
        p = ops_dir() / FILING_QUEUE
        q = {a["name"]: a for a in _obj(read_json(p)).get("notes") or [] if isinstance(a, dict) and a.get("name")}
        q.update((a["name"], a) for a in notes)     # the newest wording of each note wins
        atomic_json(p, {"notes": list(q.values())})
    return {a["name"]: FILING_DEFERRED for a in todo}


def queued_notes(state):
    """The notes queue_filer left, for alarms still in the state (a note on an alarm since removed is dropped)."""
    q = _obj(read_json(ops_dir() / FILING_QUEUE)).get("notes") or []
    return [a for a in q if isinstance(a, dict) and a.get("note_only") and a.get("name") and a.get("item")
            and (not a.get("aid") or a["aid"] in state)]


HELD_FILER_UNIT = "rm-ops-held-filer"
HELD_FILER_LOCK = "held_filer.lock"
# A hang guard on the detached filer's unit: each rimflow call in real_filer is bounded at 120 s and a real held
# filing (a spawn or reopen, a raise, a publish) takes about 10-40 s, so 600 s is far above a real run.
HELD_FILER_MAX_S = 600


def spawn_held_filer(argv):
    """Start `argv` as its own transient user unit (outside the beat's cgroup, which systemd kills when the beat ends).
    -> "started" | the refusal (one unit name at a time: a filer already running refuses the second)."""
    rf = str(HERE.parent / "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import control as C     # the one admission point: a pipe switch, a duplicate and the end receipt are its
    try:
        r = C.launch_unit(["--user", "--collect", "--quiet", "-p", "RuntimeMaxSec=%d" % HELD_FILER_MAX_S,
                           "-p", "WorkingDirectory=%s" % HERE, "--"] + list(argv),
                          {"family": "ops_held_filer", "unit": HELD_FILER_UNIT, "reuse_name": True},
                          capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        return "not started: %s: %s" % (type(e).__name__, e)
    if r.returncode == 0 and not getattr(r, "refused", False):
        return "started"
    why = ((getattr(r, "stderr", None) or "") + (getattr(r, "stdout", None) or "")).strip()
    if "DUPLICATE" in why or "already loaded" in why or "already exists" in why:
        return "running"        # the unit is still up: a filer runs (it takes its lock a moment after it starts)
    return "not started: %s" % why


def start_held_filer(spawn=None):
    """A light compose pass's filing, moved out of the beat (RIMMANDRAKE_WATCH_OPS_SENSE_OVERRUN_MOST_FAMILIES_BLIND):
    inside the 15 s sense limit a held reopen (rimflow live, raise, publish) did not fit, the kill came mid-filing, and
    the next light pass began it again (2 of 2 kill stamps on 2026-11-22 20:40-20:42 PST were in this stage). Now the
    pass only starts `ops_watch.py file-held`, which files without the beat's deadline under its own lock.
    -> "nothing held" | "running" | "started" | "not started: <why>"."""
    import fcntl
    state = _obj(read_json(ops_dir() / "alarms.json"))
    blocks = False
    try:
        blocks = bool(cause_mods()[0].queued_blocks(cause_mods()[0].load(ops_dir() / "causes.json")))
    except (ValueError, OSError):
        pass
    if not (held_todo(state) or queued_notes(state) or blocks):
        return "nothing held"
    with open(ops_dir() / HELD_FILER_LOCK, "a") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return "running"
        fcntl.flock(lk, fcntl.LOCK_UN)
    return (spawn or spawn_held_filer)([sys.executable, str(Path(__file__).resolve()), "file-held"])


def file_held_detached(now=None):
    """`ops_watch.py file-held`: file what the alarm pass deferred, with no beat deadline, one filer at a time."""
    import fcntl
    for k in [k for k in os.environ if k.startswith("METRONOME_")]:
        os.environ.pop(k)       # no beat bounds this run: real_filer files without deferring
    with open(ops_dir() / HELD_FILER_LOCK, "a") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return "skipped: another held filer runs"
        before = len(held_todo(_obj(read_json(ops_dir() / "alarms.json"))))
        st = _obj(file_held(real_filer, load_rules(), now or time.time(), with_queue=True))
        return "held filings: %d before, %d still held" % (before, len(held_todo(st)))


@_book_locked
def file_held(filer, rules, now, with_queue=False):
    """A light beat's filing (ALARM_FILING_FIX_NO_ROOM_AT_INN). Alarms are composed on the beat that measures
    COMPOSE_ALARM_FAMILY, the heaviest sense pair (8-15 s of 15), so its filer, which starts a filing only when one and
    the publish still fit, deferred nearly every alarm: 8 nightly reds sat PENDING 12-17 passes and reached nobody.
    Every other compose pass (most take 0.4-3 s) files here what that pass DEFERRED (deferred_at), in its saved name
    and title, through the same filer and bookkeeping. A PENDING alarm whose last result was a real failure is not
    taken: the alarm pass retries it at its old cadence. Nothing is decided here: crossing, clearing and naming stay
    the alarm pass's, which has the readings and the ledger. -> the alarms.json state (unchanged when nothing is held)."""
    p = ops_dir() / "alarms.json"
    state = read_json(p) if p.exists() else {}
    if not isinstance(state, dict):
        return {}
    todo = held_todo(state)
    cb = cause_mods()[0]
    bp = ops_dir() / "causes.json"
    try:
        book = cb.load(bp)
    except (ValueError, OSError):
        book = None     # the alarm pass says it aloud; a held filing still lands on its own id
    if with_queue:      # the detached filer also says what a beat's alarm pass queued (queue_filer) and the book's blocks
        todo += queued_notes(state)
        if book is not None:
            todo += [cause_block_todo(k, d, r) for k, d, r in cb.queued_blocks(book)]
    if not todo:
        return state
    log = []
    try:
        res = filer(todo, alarm_conf(rules))
    except Fenced:
        raise
    except Exception as e:  # noqa: BLE001  a filing that raises stays PENDING; the pass still reports
        res = {a["name"]: "filer raised %s: %s" % (type(e).__name__, str(e)) for a in todo}
    settle_filing(state, todo, res, filer, now, log, set(), book)
    for r in log:
        r["held"] = True        # which beat filed it: the light one
    atomic_json(p, state)
    if book is not None:
        cb.save(bp, book)
    if with_queue:      # said or failed: a note left unsaid is queued again by the next alarm pass
        atomic_json(ops_dir() / FILING_QUEUE, {"notes": []})
    with open(ops_dir() / "alarms_log.jsonl", "a", encoding="utf-8") as f:
        for r in log:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return state


def cause_mods():
    """(cause_book, jam_classes): the alarm cause book and its key (OPSWATCH_BUILD_ALARMS_KEYED_BY_CAUSE)."""
    rf = str(Path(__file__).resolve().parent.parent / "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import cause_book
    import jam_classes
    return cause_book, jam_classes


def cause_block_todo(key, dep, repair):
    return {"block_only": True, "name": "block:" + dep, "item": dep, "on": repair, "cause": key,
            "reason": "ops_watch: one repair per cause (%s): %s is a duplicate of %s" % (key, dep, repair)}


def conductor_guard():
    rf = str(Path(__file__).resolve().parent.parent / "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    import conductor_log_guard
    return conductor_log_guard


def conductor_line_owed(key, said):
    """incident.line_owed on this pass's told ledger. A ledger that cannot answer owes the line: telling twice is the
    cheap failure."""
    rf = str(Path(__file__).resolve().parent.parent / "rimflow")
    if rf not in sys.path:
        sys.path.insert(0, rf)
    try:
        import incident as IN
        return IN.line_owed(key, said, str(ops_dir() / "told.jsonl"))
    except Exception:  # noqa: BLE001
        return True


# ===================================================================================================== digest
def trend(hs, now, back):
    """value change vs the MEASURED point nearest to now-back (within 25% of back), or None."""
    if not hs:
        return None
    tgt = now - back
    cand = [(abs(t - tgt), x) for t, x in hs if abs(t - tgt) <= 0.25 * back]
    return None if not cand else min(cand)[1]


def fmt(v):
    if v is None:
        return "-"
    if isinstance(v, float):
        return ("%.2f" % v).rstrip("0").rstrip(".") if abs(v) < 100 else "%.0f" % v
    return str(v)


def st_headline(g):
    cause = g("seats.cause").strip()
    return "seats idle with work %s min, tick %s s, blind %s%s" % (
        g("seats.idle_with_work_min").strip(), g("seats.tick_age_s").strip(), g("seats.blind").strip(),
        "" if cause == "none" else ": " + cause)


def headline(points, flags, alarms):
    def g(k):
        p = points.get(k) or {}
        return "%s %s" % (fmt(p.get("v")), "" if p.get("m") == "MEASURED" else "(%s)" % (p.get("m") or "absent"))
    accs = sorted({k.split(".")[1] for k in points if k.startswith("accounts.") and k.count(".") == 2
                   and not k.endswith("_collector")})
    parts = ["runway " + ", ".join("%s %s%s%s" % (a, g("accounts.%s.runway" % a).strip(), (
        " (loan %s)" % g("accounts.%s.loan_runway" % a).strip() if "accounts.%s.loan_runway" % a in points else ""), (
        " (fleet moved here %s)" % g("accounts.%s.moved_runway" % a).strip() if "accounts.%s.moved_runway" % a in points
        else ""))
        for a in accs)
             + ", codex " + g("codex.runway").strip()]
    if "accounts.fleet_stop_h" in points:
        # a reading with no stop_at is the horizon cap ("no stop inside N h"), not a stop at N h
        capped = str((points["accounts.fleet_stop_h"].get("x") or {}).get("why") or "").startswith("no stop inside")
        parts.append("%s %s h at %s %%/h" % ("no fleet stop inside" if capped else "fleet stop in",
                                             g("accounts.fleet_stop_h").strip(),
                                             g("accounts.fleet_burn_pct_h").strip()))
    parts.append("steve %s, INVALID streak %s, unowned stall %s min" % (
        g("steve.state").strip(), g("steve.invalid_streak").strip(), g("steve.unowned_stall_min").strip()))
    parts.append("disk free / %s GB, C: %s GB, D: %s GB, scratch %s GB, pool %s clones %s GB oldest %s h" % (
        g("disk.root_free_gb").strip(), g("disk.c_free_gb").strip(), g("disk.d_free_gb").strip(),
        g("disk.scratch_total_gb").strip(), g("disk.pool_clones").strip(), g("disk.pool_gb").strip(),
        g("disk.pool_oldest_h").strip()))
    parts.append(st_headline(g))
    opened = [a for a in alarms.values() if a.get("state") == "OPEN"]
    pend = [a for a in alarms.values() if a.get("state") == "PENDING"]
    parts.append("%d flag(s), %d alarm(s) open, %d pending" % (len(flags), len(opened), len(pend)))
    return " | ".join(parts)


def build_digest(points, hist, flags, alarms, now, run_s):
    by = {}
    for f in flags:
        by.setdefault(f["key"], []).append("%s%s: %s" % (f["rule"], "/" + f["tag"] if f.get("tag") else "", f["detail"]))
    kpis = {}
    for k, p in sorted(points.items()):
        hs = hist.get(k, [])
        v = num(p)
        d24 = trend(hs, now, DAY)
        d7 = trend(hs, now, 7 * DAY)
        kpis[k] = {"v": p.get("v"), "m": p.get("m"), "unit": p.get("unit"), "why": p.get("why"),
                   "d24": None if (v is None or d24 is None) else round(v - d24, 3),
                   "d7": None if (v is None or d7 is None) else round(v - d7, 3),
                   "n7": len([1 for t, _ in hs if t >= now - 7 * DAY]), "flags": by.get(k, [])}
        if "class" in p:
            kpis[k].update({f: p.get(f) for f in ("class", "owner", "ack_within_min", "max_age_min")})
    return {"schema": SCHEMA, "at": iso(now), "t": now, "run_s": run_s, "headline": headline(points, flags, alarms),
            "alarms": alarms, "flags": flags, "kpis": kpis}


def digest_md(dg):
    import pages_index as PX  # the line that links the other kept pages
    L = ["# Ops watch %s (pass %.1f s)" % (dg["at"], dg["run_s"] or 0), "", dg["headline"], "", PX.crossref_md("ops"), ""]
    al = {k: a for k, a in dg["alarms"].items()}
    if al:
        L.append("## Alarms")
        for k, a in sorted(al.items()):
            L.append("- %s %s since %s%s%s" % (a.get("state"), k, a.get("since"), " item %s" % a["item"] if a.get("item")
                                               else "", " error: " + str(a["error"]) if a.get("error") else ""))
        L.append("")
    if dg["flags"]:
        L.append("## Open flags")
        for f in dg["flags"]:
            L.append("- %s %s [%s] %s (open since %s)" % (f["rule"] + ("/" + f["tag"] if f.get("tag") else ""), f["key"],
                                                          f["window"], f["detail"], f.get("since", "now")))
        L.append("")
    fam = None
    for k, r in dg["kpis"].items():
        f = k.split(".", 1)[0]
        if f != fam:
            fam = f
            L += ["## " + f, "key | now | class | mark | d24h | d7d | n7d | flags", "---|---|---|---|---|---|---|---"]
        L.append("%s | %s | %s | %s | %s | %s | %d | %s" % (
            k.split(".", 1)[1], fmt(r["v"]) + (" " + r["unit"] if r.get("unit") and len(r["unit"]) < 40 else ""),
            r.get("class") or "", r["m"] if r["m"] == "MEASURED" else "%s: %s" % (r["m"], (r.get("why") or "")[:90]),
            fmt(r["d24"]), fmt(r["d7"]), r["n7"], "; ".join(x[:80] for x in r["flags"]) or ""))
    return "\n".join(L) + "\n"


# The families whose every point is a token, runway, quota or burn reading: Operations' alone (owner 2026-10-27:
# every role but it and the Conductor is token-blind; the Conductor reads anything, owner 2026-10-31). tokentalk is the drift measure OF token talk: Operations' too. Used for the alarm
# routing (run_alarms); the blind digest does NOT rely on it: that is an allow-list (BLIND_KEYS).
TOKEN_FAMILIES = ("accounts", "codex", "tokentalk")

# digest_blind.md is an ALLOW-LIST (review V, V1): a token-blind role sees exactly these series
# and nothing else. Machine health (steve, timers, tps), disk, stalls, flow and production output counts. Every key
# not named here is withheld by default, so a new collector, or a quota reading phrased without a token word
# (production.B, "% of the week used"), can never reach them. Adding a key is a decision: name it here, with care.
# Deliberately absent: every accounts.*, codex.*, tokentalk.* key, production.B (the week used), and anything new.
# companion.grant_hours_left is machine health: a lapsing grant stalls every live seat, so the blind roles see it.
BLIND_KEYS = frozenset("""
companion.grant_hours_left companion.grant_visible
disk.c_free_gb disk.c_used_gb disk.d_free_gb disk.d_used_gb disk.root_free_gb disk.root_used_gb
disk.scratch_dirty_end disk.scratch_dirty_start disk.scratch_ok_age_h disk.scratch_outside_blind disk.scratch_outside_cap
disk.scratch_outside_distressed disk.scratch_refused_gb disk.scratch_total_gb
disk.pool_breach disk.pool_clones disk.pool_gb disk.pool_oldest_h disk.seat_dirt
disk.whea_blind disk.whea_corrected_24h disk.whea_severe_24h
flow.closes_24h flow.lapsed_leases flow.untriaged_findings flow.verify_pass_24h
process.share_24h process.share_7d
production.A1 production.A2 production.A3 production.A4 production.A5
production.D1 production.D2 production.D3 production.D4
production.G1 production.G2 production.G3 production.G4 production.G5 production.G6 production.G7 production.G8
production.G9
production.O1 production.O2 production.O3 production.O4
production.P1 production.P2 production.P3 production.P4
production.V0 production.W1 production.W2 production.W3 production.W4 production.record_age_min
seats.blind seats.cause seats.distressed seats.idle_with_work_min seats.paused seats.tick_age_s
steve.fault_min steve.heartbeat_age_min steve.invalid_24h steve.invalid_streak steve.jobs_24h steve.last_done_age_min
steve.seats_absent_min steve.state steve.unowned_stall_min steve.watch_age_min
testing.archmagi_nothing_h_7d testing.nothing_h_7d testing.steve_nothing_h_7d
timers.failed_units timers.overdue_timers
tps.health_age_h tps.health_breaches tps.health_sessions tps.ratio_median tps.stall_max_s tps.stalls
v3.accepted_per_day v3.failure_signal_share v3.keep_going_per_day
""".split())
# the fields of an allowed point a blind role may see: value, mark, unit, the why of a non-MEASURED mark, the 24 h /
# 7 d change. Never d24/d7 of a withheld key, never the full digest's headline (it names runway).
BLIND_FIELDS = ("v", "m", "unit", "why", "d24", "d7", "class")


def blind_keep(key, p, rx):
    """May a token-blind role see this point? Only a BLIND_KEYS key; and, as a second net, none of its key, unit or
    why holds a token_talk term."""
    if key not in BLIND_KEYS:
        return False
    p = p if isinstance(p, dict) else {}
    return not rx.search(" ".join(str(x) for x in (key, p.get("unit") or "", p.get("why") or "")))


def blind_digest_md(dg, rules):
    """digest_blind.md: the digest for the token-blind roles (review U N2/F6, review V V1).
    Built only from allow-listed parts: the BLIND_KEYS points (BLIND_FIELDS of each), a headline computed from them,
    and the alarms and flags whose key is one of them. Nothing else of the digest is read, so nothing else can leak.
    Every line is then checked against the token_talk word list as a second net; the count withheld is printed,
    never the lines."""
    rx = tt_regex(rules)
    kp = {k: {f: (r or {}).get(f) for f in BLIND_FIELDS} for k, r in (dg.get("kpis") or {}).items()
          if blind_keep(k, r, rx)}
    al = {k: a for k, a in (dg.get("alarms") or {}).items()
          if isinstance(a, dict) and ":" in str(k) and str(k).split(":", 1)[1] in kp}
    fl = [f for f in dg.get("flags") or [] if isinstance(f, dict) and f.get("key") in kp]

    def g(k):
        r = kp.get(k) or {}
        return "%s%s" % (fmt(r.get("v")), "" if r.get("m") == "MEASURED" else " (%s)" % (r.get("m") or "absent"))
    opened = [a for a in al.values() if a.get("state") == "OPEN"]
    hl = ["steve %s, INVALID streak %s, unowned stall %s min" % (
              g("steve.state"), g("steve.invalid_streak"), g("steve.unowned_stall_min")),
          "disk free / %s GB, C: %s GB, D: %s GB, scratch %s GB, pool %s clones %s GB oldest %s h" % (
              g("disk.root_free_gb"), g("disk.c_free_gb"), g("disk.d_free_gb"), g("disk.scratch_total_gb"),
              g("disk.pool_clones"), g("disk.pool_gb"), g("disk.pool_oldest_h")),
          st_headline(g),
          "%d flag(s), %d alarm(s) open, %d pending" % (
              len(fl), len(opened), len([a for a in al.values() if a.get("state") == "PENDING"]))]
    L = ["# Ops watch, health digest %s (an allow-list of health series; account readings are Operations')"
         % dg.get("at"), "", " | ".join(hl), ""]
    body = []
    if al:
        body.append("## Alarms")
        for k, a in sorted(al.items()):
            body.append("- %s %s since %s%s" % (a.get("state"), k, a.get("since"),
                                                " item %s" % a["item"] if a.get("item") else ""))
        body.append("")
    if fl:
        body.append("## Open flags")
        for f in fl:
            body.append("- %s %s [%s] %s (open since %s)" % (f.get("rule", "?") + ("/" + f["tag"] if f.get("tag") else ""),
                                                             f["key"], f.get("window"), str(f.get("detail")),
                                                             f.get("since", "now")))
        body.append("")
    fam = None
    for k in sorted(kp):
        r = kp[k]
        f = k.split(".", 1)[0]
        if f != fam:
            fam = f
            body += ["## " + f, "key | now | class | mark | d24h | d7d", "---|---|---|---|---|---"]
        body.append("%s | %s | %s | %s | %s | %s" % (
            k.split(".", 1)[1], fmt(r["v"]) + (" " + r["unit"] if r.get("unit") and len(r["unit"]) < 40 else ""),
            r.get("class") or "",
            r["m"] if r["m"] == "MEASURED" else "%s: %s" % (r["m"], (r.get("why") or "")[:90]),
            fmt(r["d24"]), fmt(r["d7"])))
    out = [x for x in L + body if not rx.search(x)]
    withheld = len(L) + len(body) - len(out)
    if withheld:
        out.append("(%d line(s) withheld: they named an account reading)" % withheld)
    return "\n".join(out) + "\n"


def write_text_atomic(path, text):
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


# ======================================================================================================= run
class Busy(RuntimeError):
    pass


def _locked(fn):
    """One pass at a time (the timer and a hand run): two passes would append the series twice and could file one
    alarm twice. A second pass does not wait; it says so and exits clean (a failed unit would alarm on itself)."""
    def wrap(*a, **k):
        import fcntl
        ops_dir().mkdir(parents=True, exist_ok=True)
        with open(ops_dir() / "run.lock", "w") as lk:
            try:
                fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise Busy("another ops_watch pass holds %s" % (ops_dir() / "run.lock"))
            return fn(*a, **k)
    wrap.__name__ = fn.__name__
    wrap.__doc__ = fn.__doc__
    return wrap


LAST_MEASURED_RETIRE_DAYS = 365     # a key unmeasured this long is retired from last_measured.json (never "gone" forever)


def _obj(x):
    """A state file's body, or {} when it is torn or the wrong shape."""
    return x if isinstance(x, dict) else {}


def dead_targets(rules, points):
    """-> a bad_rule flag per target whose alarm cannot fire, read on a full pass. A literal key no reading carries (its
    collector ran) is dead. A wildcard counts instances (testing.red_<group>): none this pass is a quiet night, not a
    dead rule, so only a wildcard on a family no collector reports is."""
    out = []
    for t in good_targets(rules):
        fam = t["key"].split(".")[0]
        if any(c in t["key"] for c in "*?["):
            if fam not in COLLECTORS and not any(k.split(".")[0] == fam for k in points):
                out.append({"rule": "bad_rule", "key": "rules.target." + t["key"], "value": None, "window": "now",
                            "detail": "target %s names a family no collector reports: its alarm cannot fire" % t["key"]})
        elif fam + "._collector" not in points and not any(fnmatch.fnmatchcase(k, t["key"]) for k in points):
            out.append({"rule": "bad_rule", "key": "rules.target." + t["key"], "value": None, "window": "now",
                        "detail": "target %s matches no reading: its alarm cannot fire" % t["key"]})
    return out


def counts_as_measured(p):
    """A MEASURED point with a value. NaN is not one: no rule can read it, so it must not refresh a key's last reading."""
    return isinstance(p, dict) and p.get("m") == "MEASURED" and p.get("v") is not None and p.get("v") == p.get("v")


def carry_last_measured(lastm, saved, points, now):
    """-> (lastm for andon, saved for disk). `lastm` is read from the loaded series (series_days), so a key
    UNMEASURED longer than that loses its last MEASURED and its 'silent' flag. `saved` (last_measured.json) outlives the
    series: it fills the gap for keys this pass still reports (a key not reported stays the 'gone' rule's, from the
    series only, so a retired key is not 'gone' forever) and drops keys older than LAST_MEASURED_RETIRE_DAYS."""
    saved = {k: t for k, t in (saved if isinstance(saved, dict) else {}).items()
             if isinstance(t, (int, float)) and finite(t) and t <= now + 300}
    merged = dict(lastm)
    for k in points:
        if k not in merged and k in saved:
            merged[k] = saved[k]
    keep = dict(saved)
    keep.update(lastm)
    for k, p in points.items():
        if counts_as_measured(p):      # a state string too, as run() reads the series
            keep[k] = now
    keep = {k: t for k, t in keep.items() if now - t <= LAST_MEASURED_RETIRE_DAYS * DAY}
    return merged, keep


def steve_release_start():
    """Start testq/brake_release.py, Operations' deterministic hand on the Steve lane, in its own process (its import of
    testq reads TESTQ_QUEUE as this pass does) and its own session, output to ops_dir()/brake_release.out. -> the
    started record for steve_release_finish. It starts BEFORE the collectors: inside a metronome beat (15 s) the
    collectors of a steve beat took 8-15 s (2026-11-05), so a release started after them never fit and its reading
    went stale for hours; started first it runs beside them (~2.5 s) and costs the beat nothing."""
    out = ops_dir() / "brake_release.out"
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            proc = subprocess.Popen([sys.executable, str(HERE / "testq" / "brake_release.py")], stdout=fh,
                                    stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
    except (OSError, subprocess.SubprocessError) as e:
        return {"why": "%s: %s" % (type(e).__name__, str(e))}
    return {"proc": proc, "out": out}


def steve_release_finish(started):
    """-> flags: the release costs a flag when it fails, never the pass. Inside a beat it is waited for only while the
    beat leaves the filer its room; past that it runs on in its own session (no flag: nothing failed) and its reading,
    QHOME/brake_release.json, says how it ended. Outside a beat it gets 240 s, then its whole process group is
    killed."""
    why = started.get("why")
    proc = started.get("proc")
    if proc is not None:
        dl = beat_deadline()
        budget = 240.0 if dl is None else min(240.0, dl - time.time() - FILING_FIRST_GUESS_S - FILING_PUBLISH_RESERVE_S - 2)
        try:
            rc = proc.wait(timeout=max(budget, 0.01))
        except subprocess.TimeoutExpired:
            if dl is not None:
                return []
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            proc.wait()
            rc = None
            why = "TimeoutExpired: no end in %.0f s" % budget
        if rc:
            try:
                tail = Path(started["out"]).read_text(encoding="utf-8", errors="replace").strip()
            except OSError as e:
                tail = "its output is unreadable: %s" % e
            why = "exit %d: %s" % (rc, tail)
    return [{"rule": "brake_release", "key": "steve.brake_release", "value": None, "window": "now",
             "detail": "the brake release pass failed: " + why}] if why else []


def steve_release():
    """One release, waited for (a hand run, and the tests): steve_release_start then steve_release_finish."""
    return steve_release_finish(steve_release_start())


OLD_TIMER = "rm-ops-watch.timer"     # the clock the metronome's sense phase replaces (metronome_phases.json owns)
SENSE_PHASE = "sense"
EXIT_FENCED = 3
COMPOSE_MAX_AGE_S = 1000.0   # the FLOOR of the carry bound; compose_max_age_s() derives the real one from the round robin
METRONOME_PHASES = HERE / "systemd" / "metronome_phases.json"
METRONOME_TIMER = HERE / "systemd" / "rm-metronome.timer"
METRONOME_SENSE_TIMER = HERE / "systemd" / "rm-metronome-sense.timer"     # runs the sense phase when it is apart
COMPOSE_NEEDS_FLOW = ("testing",)   # collectors that read the flow collector's ctx (closes, open_ids): flow joins them
COMPOSE_ALARM_FAMILY = "flow"  # a compose pass files alarms only when it measures this family (its ctx: the ledger ids)


def compose_round_bound_s(phases=None, timer=None, n_families=None, sense_timer=None):
    """-> (seconds, why): the longest a healthy family can wait between its own sense passes while the metronome's
    round robin keeps turning, from the phase table and the timer, never a typed number. A pass whose families overrun
    is followed by one retry beat per family (metronome fam_retry) before the round moves on, so the worst turn of
    per_beat families costs 1 + per_beat beats; a beat starts the timer's OnUnitInactiveSec (+ AccuracySec) after the
    last one ENDED, and a beat lasts at most budget_s. A typed 1000 s (~1.5 rounds at 60 s beats, no retries) was
    under the measured round: plan read 18:38:14Z then 19:00:35Z (1341 s, 5 overruns in 16 beats), so plan.blind read
    1 on a healthy source three times in a day (RELAPSE_PLAN_FIX_DIED_TWICE). A beat that defers sense outright is not
    counted: that is a stalled phase, the metronome's own critical max_ok_age_s. (None, why) when either file does not read."""
    try:
        tab = json.loads(Path(phases or METRONOME_PHASES).read_text(encoding="utf-8"))
        sense = tab["phases"][SENSE_PHASE]
        per = int(sense["per_beat"])
        apart = bool(sense.get("apart"))
        # apart (its own unit): the gap is its own timer's, and a kill is no longer a normal turn (the limit is a hang
        # guard), so no retry beats are counted. pass_s is the longest real pass: the hang guard is 10 times that, and a
        # healthy round read off the hang guard would carry a dead family for 4 h
        budget = float(sense.get("pass_s") or sense["limit_s"]) + float(sense["cleanup_s"]) if apart else float(tab["budget_s"])
        timer = (sense_timer or METRONOME_SENSE_TIMER) if apart else timer
        unit = {"ms": 0.001, "s": 1, "sec": 1, "min": 60, "m": 60, "h": 3600}
        tmr = {}
        for line in Path(timer or METRONOME_TIMER).read_text(encoding="utf-8").splitlines():
            k, _, v = line.partition("=")
            m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(ms|sec|s|min|m|h)?\s*", v)
            if m:
                tmr[k.strip()] = float(m.group(1)) * unit[m.group(2) or "s"]
        gap = tmr["OnUnitInactiveSec"] + tmr.get("AccuracySec", 0.0)
        n = int(n_families if n_families is not None else len(FAMILIES))
        if per < 1 or n < 1 or not (gap > 0 and budget > 0):
            raise ValueError("per_beat %s, families %s, gap %s, budget %s" % (per, n, gap, budget))
    except (OSError, ValueError, KeyError, TypeError) as e:
        return None, "the round robin's bound does not read: %s: %s" % (type(e).__name__, str(e))
    if apart:
        beats = math.ceil(n / per)
        return beats * (gap + budget), "%d sense passes (%d families, %d a pass, apart) x %.0f s" % (
            beats, n, per, gap + budget)
    beats = math.ceil(n / per) * (1 + per)
    return beats * (gap + budget), "%d beats (%d families, %d a beat, each turn overrun and retried) x %.0f s" % (
        beats, n, per, gap + budget)


def compose_max_age_s(rules):
    """-> (seconds, sick flag or None): how old a carried family may be before it reads UNMEASURED, and so before its
    .blind target alarms. Never under the round robin's worst round (compose_round_bound_s): a rule may raise it, not
    lower it. A bound that does not read falls to COMPOSE_MAX_AGE_S, said aloud as a flag."""
    try:
        ruled = float(rules.get("compose_max_age_s", COMPOSE_MAX_AGE_S))
    except (TypeError, ValueError):
        ruled = COMPOSE_MAX_AGE_S
    bound, why = compose_round_bound_s()
    if bound is None:
        return ruled, {"rule": "compose_bound", "key": "compose.max_age_s", "value": None, "window": "now",
                       "detail": "carried families age out at %.0f s, maybe inside one round: %s" % (ruled, why)}
    return max(ruled, bound), None


class Fenced(RuntimeError):
    """The metronome generation this pass acts for is no longer the live one: it publishes nothing more."""


def observed_at(p):
    """The epoch a carried point was observed at (compose passes), or None for this pass's own reading."""
    o = (p.get("x") or {}).get("observed_at") if isinstance(p, dict) and isinstance(p.get("x"), dict) else None
    if not o:
        return None
    try:
        t = epoch(o)
    except (TypeError, ValueError, OverflowError):
        return None
    return t if is_num(t) else None


def carry_family(fam, recs, now, max_age, cause=None):
    """The points of family `fam`'s last series record, for a compose pass that did not measure it this beat: each
    carries observed_at (its record's time). None recorded, or older than max_age, reads UNMEASURED, never as now;
    `cause` (blind_families' kill note) is then said in each point's why."""
    recs = [r for r in recs if isinstance(r, dict) and is_num(r.get("t")) and r["t"] <= now + 300
            and isinstance(r.get("points"), dict)]
    last = recs[-1] if recs else None
    if last and now - last["t"] <= max_age:
        out = {}
        for k, p in last["points"].items():
            if isinstance(p, dict):
                p = dict(p)
                p["x"] = dict(p.get("x") or {}, observed_at=last.get("at") or iso(last["t"]))
            out[k] = p
        return out
    why = ("last measured %s, %.0f min ago: older than the round robin allows (%d min)" % (
        last.get("at") or iso(last["t"]), (now - last["t"]) / 60, max_age / 60) if last else
        "not measured yet: the round robin has not reached it")
    if cause:
        why += "; " + cause
    out = {k: U(why, p.get("unit") if isinstance(p, dict) else None) for k, p in (last or {}).get("points", {}).items()
           if not k.endswith("._collector")}
    out["%s._collector" % fam] = U(why)
    return out


SENSE_KILLS = "sense_kills.jsonl"     # one line per sense pass killed at its limit (on_sense_term)
BLIND_KEY = "sense.families_blind"
_STAGE = {"stage": "start", "t0": None, "families": []}     # what a killed pass was doing (on_sense_term)


def sense_stage(what):
    _STAGE["stage"] = what


def on_sense_term(signum, frame):
    """SIGTERM from the metronome at the sense limit: say which families and which stage it cut, then exit 143. Before
    this a killed pass left nothing (its log was empty), so 87 of 136 kills in 3 h could not be told apart."""
    t0 = _STAGE.get("t0") or time.time()
    try:
        with open(ops_dir() / SENSE_KILLS, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.time(), "at": iso(time.time()), "families": _STAGE.get("families") or [],
                                "stage": _STAGE.get("stage"), "seconds": round(time.time() - t0, 2),
                                "gen": os.environ.get("METRONOME_GEN")}, sort_keys=True) + "\n")
    except OSError:
        pass        # the age of the family's series still makes it blind; only the stage is lost
    os._exit(143)


def sense_kills():
    """-> the recent kill lines (oldest first); [] when none was ever written. An unreadable tail reads as none: the
    blind count stands on the series' ages alone, and only its cause loses the kills."""
    p = ops_dir() / SENSE_KILLS
    try:
        return tail_json_lines(p, chunk=1 << 18)
    except OSError:
        return []


def blind_families(prev, now, max_age, kills, measured=()):
    """-> {family: cause} for each family (ORDER) whose newest series record is older than max_age, or which has none in
    the series window; a family measured by this pass is never blind. The cause names its age and the sense passes on it
    killed since it last read (sense_kills), with the stage of the last one."""
    out = {}
    for fam in ORDER:
        if fam in measured:
            continue
        ts = [r["t"] for r in prev.get(fam) or [] if isinstance(r, dict) and is_num(r.get("t")) and r["t"] <= now + 300]
        last = max(ts) if ts else None
        if last is not None and now - last <= max_age:
            continue
        ks = [k for k in kills if isinstance(k, dict) and fam in (k.get("families") or [])
              and is_num(k.get("t")) and (last is None or k["t"] > last)]
        age = ("unread %.0f min" % ((now - last) / 60)) if last is not None else "no record in the series window"
        kill = ("; %d sense pass%s on it killed at the limit since, the last in %s after %s s" % (
            len(ks), "" if len(ks) == 1 else "es", ks[-1].get("stage"), ks[-1].get("seconds"))) if ks else \
            "; no kill recorded since (the round robin has not reached it, or its pass died without SIGTERM)"
        out[fam] = age + kill
    return out


def blind_point(blind, max_age):
    cause = "; ".join("%s %s" % (f, c) for f, c in sorted(blind.items()))
    return M(len(blind), "families unread past the round robin's bound", names=",".join(sorted(blind)) or None,
             cause=cause or None, bound_s=round(max_age))


@_locked
def run(now=None, rules=None, filer=None, families=None, compose=False, still_owner=None, held_detach=False):
    """One pass. `families` limits it to those collectors. With `compose` (the metronome's sense phase, a family or two
    a beat, round robin) every other family's last series record is carried in (carry_family), so the status, health
    verdict, digest and flags are a whole pass's; the alarms run, over that composite, only on the pass that measures
    COMPOSE_ALARM_FAMILY, about once a round; every other compose pass files what that pass deferred (file_held).
    `still_owner(what)` (the metronome's ownership fence) is asked before the
    series are written, before the alarms and before the status: False raises Fenced."""
    def fence(what):
        if still_owner is not None and not still_owner(what):
            raise Fenced("fenced before %s" % what)
    compose = bool(compose and families)
    _STAGE.update(t0=time.time(), families=list(families or []), stage="start")
    if families and not compose:     # a sample, never the live reading: refused before anything is written or filed
        if filer is not None and filer is real_filer:
            raise PartialPass("a --family pass without --compose files no alarms: its readings are not a whole pass's")
        if live_store():
            raise PartialPass("a --family pass without --compose writes nothing into the live store %s (status.json, "
                              "series, alarms): set RM_OPS_WATCH_DIR to a scratch dir" % ops_dir())
    now = now or time.time()
    rules = rules or load_rules()
    if compose and COMPOSE_ALARM_FAMILY not in families and any(f in families for f in COMPOSE_NEEDS_FLOW):
        families = [COMPOSE_ALARM_FAMILY] + list(families)
    if compose and COMPOSE_ALARM_FAMILY not in families:
        # the alarm family unread past the bound: no alarm (the blind one included) could run, so this pass reads it
        fl = [r["t"] for r in read_series(COMPOSE_ALARM_FAMILY, now - rules.get("series_days", 8) * DAY)
              if is_num(r.get("t")) and r["t"] <= now + 300]
        if not fl or now - max(fl) > compose_max_age_s(rules)[0]:
            families = [COMPOSE_ALARM_FAMILY] + list(families)
    whole = not families or compose
    t0 = time.time()
    ctx = {"no_reruns": True} if compose else {}
    points = {}
    since = now - rules.get("series_days", 8) * DAY
    prev = {}
    sick = []
    unfit = []
    release = None
    if filer is real_filer and (not families or "steve" in families):      # acts only where alarms are really filed
        fence("the steve release")
        release = steve_release_start()     # before the collectors: it runs beside them (steve_release_start)
    for fam in ORDER:
        if families and fam not in families:
            continue
        old = read_series(fam, since)
        prev[fam] = old
        ctx["last_record"] = old[-1] if old else {}
        sense_stage("collector %s" % fam)
        c0 = time.time()
        try:
            pts = COLLECTORS[fam](now, rules, ctx)
        except Exception as e:  # noqa: BLE001  an instrument that errors is UNMEASURED, never 0
            why = "collector error: %s: %s" % (type(e).__name__, str(e))
            last = old[-1]["points"] if old else {}
            pts = {k: U(why, p.get("unit") if isinstance(p, dict) else None) for k, p in last.items()
                   if not k.endswith("._collector")}
            if fam == "flow":      # these ledger points are known even before the first successful read
                for k in ("flow.untriaged_findings", "flow.closes_24h", "flow.verify_pass_24h", "flow.lapsed_leases",
                          "steve.incident_unclaimed_min"):
                    pts.setdefault(k, U(why))
            pts["%s._collector" % fam] = U(why)
        unfit += stamp_ranges(pts, rules)
        rec = {"schema": SCHEMA, "t": now, "at": iso(now), "family": fam, "points": pts,
               "collector_s": round(time.time() - c0, 2)}
        if fam == "production" and ctx.get("production_src_t"):
            rec["src_t"] = ctx["production_src_t"]
        dup = fam == "production" and old and old[-1].get("src_t") and old[-1].get("src_t") == rec.get("src_t")
        if not dup:
            fence("writing the %s series" % fam)
            try:
                append(fam, rec)
            except Exception as e:  # noqa: BLE001  the pass and the alarms outlive a series that cannot be written
                sick.append({"rule": "series_write", "key": "%s._series" % fam, "value": None, "window": "now",
                             "detail": "this pass's %s points were not kept: %s: %s" % (fam, type(e).__name__, str(e))})
        points.update(pts)
    if compose:
        sense_stage("carry")
        max_age, bound_flag = compose_max_age_s(rules)
        if bound_flag:
            sick.append(bound_flag)
        for fam in ORDER:
            if fam not in families:
                prev[fam] = read_series(fam, since)
        blind = blind_families(prev, now, max_age, sense_kills(), measured=families)
        carried = {}
        for fam in ORDER:
            if fam in families:
                continue
            carried.update(carry_family(fam, prev[fam], now, max_age, cause=blind.get(fam)))
        points = dict(carried, **points)        # this pass's own readings win
        points[BLIND_KEY] = blind_point(blind, max_age)
    elif whole:     # a whole pass measures every family: none is blind, and the target still has its reading
        points[BLIND_KEY] = blind_point({}, compose_max_age_s(rules)[0])
    if release is not None:
        sick += steve_release_finish(release)
    for fam, key in (("seats", "seats.blind"), ("disk", "disk.scratch_outside_blind")):
        if (whole or fam in families) and not counts_as_measured(points.get(key)):
            points[key] = st_suppressed(points, fam)
            stamp_ranges(points, rules)
    hist, lastm = {}, {}
    for fam, recs in prev.items():
        recs = [r for r in recs if r["t"] <= now + 300]     # a future row would read as just measured, and hide silence
        hist.update(history(recs))
        for r in recs:      # any MEASURED point, a state string too: only the band and run rules need a number
            for k, p in (r.get("points") or {}).items():
                if counts_as_measured(p):
                    lastm[k] = max(r["t"], lastm.get(k, r["t"]))
    lm_path = ops_dir() / "last_measured.json"
    lm_saved = _obj(read_json(lm_path)).get("t")
    lm_bad = lm_path.exists() and not (isinstance(lm_saved, dict)
                                       and all(is_num(v) and finite(v) for v in lm_saved.values()))
    fresh = {k: p for k, p in points.items() if not observed_at(p)}     # carried points were measured when observed
    lastm, saved_lm = carry_last_measured(lastm, lm_saved, fresh, now)
    try:
        flags = andon(points, hist, lastm, rules, now) + sick
    except Exception as e:  # noqa: BLE001  no flags this pass, said aloud; the alarms still run
        flags = sick + [{"rule": "bad_rule", "key": "rules", "value": None, "window": "now",
                         "detail": "andon failed: %s: %s" % (type(e).__name__, str(e))}]
    if rules.get("_load_error"):
        flags.append({"rule": "bad_rule", "key": "rules.file", "value": None, "window": "now",
                      "detail": "the rules file cannot be read, last good copy in use: %s" % rules["_load_error"]})
    # a collector down longer than the series window has no old keys left to go silent: this flag is what still says so
    flags += [{"rule": "collector", "key": k, "value": None, "window": "now", "detail": str(p.get("why"))}
              for k, p in sorted(points.items()) if k.endswith("._collector") and isinstance(p, dict)
              and p.get("m") == "UNMEASURED"]
    flags += [{"rule": "bad_rule", "key": "rules.range." + k, "value": points[k].get("v"), "window": "now",
               "detail": "%s reads %s, which fits no class of the ranges block" % (k, fmt(points[k].get("v")))} for k in unfit]
    if whole:    # a key no collector reports would keep its alarm silent for good; a limited pass cannot tell
        for k in sorted(ranges_of(rules)):
            if k.split(".")[0] + "._collector" not in points and k not in points:
                flags.append({"rule": "bad_rule", "key": "rules.range." + k, "value": None, "window": "now",
                              "detail": "range %s matches no reading: it can report no class" % k})
        flags += dead_targets(rules, points)
    if lm_bad:      # not overwritten: the flag repeats until someone repairs or removes it, and silence flags are at stake
        flags.append({"rule": "bad_rule", "key": "last_measured", "value": None, "window": "now",
                      "detail": "last_measured.json is unreadable: long-silent keys may read as not silent; repair or delete it"})
    try:
        if not lm_bad:
            fence("last_measured")
            atomic_json(lm_path, {"t": saved_lm})
    except OSError as e:    # a full disk is what the alarms below are for: never let it stop them
        flags.append({"rule": "bad_rule", "key": "last_measured", "value": None, "window": "now",
                      "detail": "last_measured.json not written: %s" % str(e)})
    sense_stage("alarms")
    try:
        if compose and COMPOSE_ALARM_FAMILY not in families:
            # this beat's pass is not the alarm pass: it composes nothing, but files what the alarm pass had to defer
            if filer and held_detach:      # outside the beat (start_held_filer): a filing here was killed mid-way
                fence("starting the held filer")
                why = start_held_filer()
                if why.startswith("not started"):
                    flags.append({"rule": "held_filer", "key": "alarms.held_filer", "value": None, "window": "now",
                                 "detail": "the deferred alarms were not filed this pass: %s" % why})
                alarms = _obj(read_json(ops_dir() / "alarms.json"))
            elif filer:
                fence("filing held alarms")
                def hfiler(todo, conf, _f=filer):
                    fence("filing")
                    return _f(todo, conf)
                alarms = _obj(file_held(hfiler, rules, now))
            else:
                alarms = _obj(read_json(ops_dir() / "alarms.json"))
        else:
            fence("the alarms")
            apts, afiler = points, filer
            if compose:
                ap = ops_dir() / "compose_alarm_pass.json"
                last_t = _obj(read_json(ap)).get("t")
                last_t = last_t if is_num(last_t) and last_t <= now else None
                # a carried reading counts once: one already seen by an earlier alarm pass holds (no clear, no file)
                apts = {k: p for k, p in points.items() if not observed_at(p) or last_t is None
                        or observed_at(p) > last_t}
                if filer:
                    def afiler(todo, conf, _f=queue_filer if held_detach else filer):
                        fence("filing")
                        return _f(todo, conf)
            alarms = run_alarms(apts, rules, now, ctx.get("known_ids") or set(), afiler, ctx.get("open_ids"),
                                ctx.get("closes"), cause_tree=alarm_conf(rules).get("clone") if afiler else None)
            if compose:
                atomic_json(ap, {"t": now, "at": iso(now)})
            if compose and filer and held_detach:
                fence("starting the held filer")
                why = start_held_filer()
                if why.startswith("not started"):
                    flags.append({"rule": "held_filer", "key": "alarms.held_filer", "value": None, "window": "now",
                                  "detail": "this pass's alarms were not filed: %s" % why})
    except Fenced:
        raise
    except Exception as e:  # noqa: BLE001  the digest still goes out, and says the alarms did not run
        alarms = _obj(read_json(ops_dir() / "alarms.json"))
        flags.append({"rule": "bad_rule", "key": "alarms", "value": None, "window": "now",
                      "detail": "NO ALARM RAN this pass: %s: %s" % (type(e).__name__, str(e))})
    _conf = alarm_conf(rules)
    if not (_conf.get("clone") and _conf.get("parent")):
        flags.append({"rule": "bad_rule", "key": "rules.alarm", "value": None, "window": "now",
                      "detail": "NO ALARM CAN BE FILED: the rules name no alarm.clone or alarm.parent"})
    flags += [{"rule": "alarm_state", "key": aid, "value": None, "window": "now", "detail": a.get("error") or "unreadable"}
              for aid, a in sorted(alarms.items()) if isinstance(a, dict) and a.get("state") == "UNREADABLE"]
    old = _obj(read_json(ops_dir() / "flags.json")).get("flags")
    old_flags = {flag_id(f): f for f in (old if isinstance(old, list) else [])
                 if isinstance(f, dict) and "rule" in f and "key" in f}
    for f in flags:
        f["since"] = (old_flags.get(flag_id(f)) or {}).get("since") or iso(now)
    run_s = round(time.time() - t0, 1)
    sense_stage("status")
    fence("the status")
    atomic_json(ops_dir() / "flags.json", {"at": iso(now), "flags": flags})
    st = {"schema": SCHEMA, "at": iso(now), "t": now, "run_s": run_s, "points": points, "flags": flags, "alarms": alarms}
    if compose:     # `at` is this beat's; what each family's readings are as of is here
        obs = {}
        for k, p in points.items():
            o = observed_at(p)
            fam = k.split(".")[0]
            if o and (fam not in obs or (obs[fam] or 0) > o):
                obs[fam] = o
        st["measured"] = sorted(families)
        st["observed"] = {f: iso(t) for f, t in sorted(obs.items())}
        st["oldest_observed_at"] = iso(min(obs.values())) if obs else iso(now)
    atomic_json(ops_dir() / "status.json", st)
    # every key of this pass too, not only those with history: a new key's first sample counts (review night r1)
    hist_all = {k: hist.get(k, []) + ([(now, num(points[k]))] if points.get(k, {}).get("m") == "MEASURED"
                                      and not observed_at(points[k])
                                      and num(points[k]) is not None else []) for k in set(hist) | set(points)}
    dg = build_digest(points, hist_all, flags, alarms, now, run_s)
    atomic_json(ops_dir() / "digest.json", dg)
    try:
        full = digest_md(dg)
    except Exception as e:  # noqa: BLE001  the headline survives a row that cannot be rendered
        full = "# ops_watch digest failed to render\n\n%s: %s\n\n%s\n" % (type(e).__name__, str(e), dg.get("headline"))
    write_text_atomic(ops_dir() / "digest.md", full)
    try:
        blind = blind_digest_md(dg, rules)
    except Exception as e:  # noqa: BLE001  fail closed and aloud: never a stale digest, never an unfiltered one
        blind = "# ops_watch blind digest unavailable\n\n%s at %s: check token_talk in ops_watch_rules.json\n" % (
            type(e).__name__, iso(now))
    write_text_atomic(ops_dir() / "digest_blind.md", blind)
    return dg


@_locked
def backfill_production(now=None, rules=None):
    """Seed series/production.jsonl from rm-streams-collect' own history so the KPI bands have a baseline on day one.
    Only into an empty production series (never rewrites what is there); each record keeps its source time."""
    now = now or time.time()
    rules = rules or load_rules()
    if read_series("production", 0):
        return 0
    since = now - rules.get("series_days", 8) * DAY
    n = 0
    with open(streams_series(), encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            t = rec.get("t") if isinstance(rec, dict) else None
            if not isinstance(t, (int, float)) or epoch(t) is None or t < since:
                continue
            pts = {}
            for k, p in sorted((rec.get("measures") or {}).items()):
                if not isinstance(p, dict):
                    continue
                if p.get("m") == "MEASURED":
                    pts["production." + k] = {"v": p.get("v"), "m": "MEASURED"}
                else:
                    pts["production." + k] = soft_point(p)
            append("production", {"schema": SCHEMA, "t": t, "at": iso(t), "family": "production", "points": pts,
                                  "src_t": t, "backfill": "rm-streams-collect series.jsonl"})
            n += 1
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--file-alarms", action="store_true", help="file NEW alarm crossings as rimflow items")
    r.add_argument("--family", action="append", help="only these families (testing, and the metronome's sense phase)")
    r.add_argument("--compose", action="store_true",
                   help="with --family: carry every other family's last reading in, so the status is a whole pass's")
    r.add_argument("--metronome-gen", type=int, help="the metronome's ownership generation (its sense phase)")
    d = sub.add_parser("digest")
    d.add_argument("--blind", action="store_true", help="print digest_blind.md (the token-blind roles' digest)")
    sub.add_parser("backfill", help="seed an empty production series from rm-streams-collect' history")
    sub.add_parser("file-held", help="file the alarms the alarm pass deferred, outside the beat (start_held_filer)")
    sub.add_parser("rerun-reds", help="rerun new nightly-red groups and verify closed fixes at origin/main")
    ln = sub.add_parser("lint", help="refuse a ranges block with a metric short of owner, class, age, ack or why")
    ln.add_argument("--rules", help="the rules file, default the shipped one")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        if a.family and not a.compose and a.file_alarms:
            print("ops_watch: REFUSED: --family without --compose files no alarms (STATUS_FIX_HALF_PASS_ATE_THE_SLOT)")
            return 2
        import metronome
        if a.metronome_gen is None and a.file_alarms:
            owner = metronome.owner_of(OLD_TIMER)
            if owner:
                print("ops_watch: the metronome's %s phase owns %s; a run without --metronome-gen files nothing: "
                      "run it without --file-alarms" % (owner, OLD_TIMER))
                return 0
        still_owner = None
        if a.metronome_gen is not None:
            mdir = metronome.state_dir(os.environ.get("METRONOME_DIR"))

            def still_owner(what):
                ok, why = metronome.may_act(mdir, SENSE_PHASE, a.metronome_gen)
                if not ok:
                    print("ops_watch: fenced before %s: %s" % (what, why))
                return ok
            if not still_owner("the pass"):
                return EXIT_FENCED
        old_term = signal.signal(signal.SIGTERM, on_sense_term) if a.compose else None
        try:
            dg = run(filer=real_filer if a.file_alarms else None, families=a.family, compose=a.compose,
                     still_owner=still_owner, held_detach=a.compose)
        except Busy as e:
            print("skipped: %s" % e)
            return 0
        except Fenced as e:
            print("ops_watch: %s" % e)
            return EXIT_FENCED
        except PartialPass as e:
            print("ops_watch: REFUSED: %s" % e)
            return 2
        finally:
            if old_term is not None:
                signal.signal(signal.SIGTERM, old_term)     # an in-process caller (a selftest) gets its own back
        print(dg["headline"])
        return 0
    if a.cmd == "lint":
        problems = ranges_problems(json.loads(Path(a.rules or rules_path()).read_text(encoding="utf-8")))
        print("\n".join("REFUSED: " + p for p in problems) or "ranges clean")
        return 1 if problems else 0
    if a.cmd == "file-held":
        print(file_held_detached())
        return 0
    if a.cmd == "rerun-reds":
        try:
            print(rerun_reds())
        except Busy as e:
            print("skipped: %s" % e)
        return 0
    if a.cmd == "backfill":
        print("production records backfilled: %d" % backfill_production())
        return 0
    if a.cmd == "digest":
        p = ops_dir() / ("digest_blind.md" if a.blind else "digest.md")
        print(p.read_text(encoding="utf-8") if p.exists() else "no digest yet: run ops_watch.py run")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
