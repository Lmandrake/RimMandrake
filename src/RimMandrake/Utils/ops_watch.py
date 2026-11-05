#!/usr/bin/env python3
"""ops_watch: the Dispatcher's deterministic measurement arm for Operations (V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE).

The owner, 2026-10-26: "I am most eager to have a competent agent appearing to check the spend of all the accounts
including CODEX, SteveDesktop's operation... monitor the disk." and (ledger 2026-10-27T05:59:41Z) Operations "should
just have those things automatically gathered for it, so it's not constantly burning tokens gathering it all up for
every question considered." So this program, with no AI, every 15 min (rm-ops-watch.timer, listed in
rimflow/dispatcher_schedule.json "measure"):

  GATHER   one record per metric family, reusing the instruments that already exist:
             accounts    account_usage.read_now() + slot_allocator.slope(): week % left, hours to reset, runway
             codex       sim/csuite_codex_limits.readings(): the weekly window's used %, reset, runway
             steve       testq steward.json / steward_watch.json / done/*.json: state, fault, heartbeat, INVALID streak;
                         a filing pass also runs testq/brake_release.py, which ACTS: one canary job on a known-cause brake
             testing     testq done jobs (Steve lane, per job) + testing_metrics history (archmagi, per day):
                         busy hours on runs that caught nothing (no FAIL, no finding, no close within 24 h)
             disk        free GB on / (WSL ext4), C:, D:; D: used GB (agent storage growth); scratch under the reaper
                         (the last line of rm-scratch-reap's runs.jsonl, written hourly: no 160 s dry run here)
                         clones outside the pool cap (scratch_outside: the reaper's sanity record, read only)
             timers      systemctl --user: failed units, timers overdue
             flow        the rimflow ledger (pulse_core.read_ledger, the union of clones): untriaged findings,
                         closes and verify passes in 24 h, lapsed leases
             process     process-commit share (git log, the resp_register PROC regex) over 24 h and 7 d
             tps         tps_record.py --json: tick ratio, stalls, coverage
             production  every stream measure (rm-streams-collect's series.jsonl, reused, not recomputed)
             v3          the section 6 success metrics no instrument measures yet, UNMEASURED with the reason
             relentless  the belt, from its own store: live, under_min, breaker_open_min, checks_wait, ready, tick_age_s,
                         progress_age_min; distressed and cause (OP2, DI2); blind when a source is missing or frozen
             seats       idle_with_work_min: how long a seat has sat idle through rings it did not answer with work, from
                         the Dispatcher's journal.jsonl and state.json (OP2); blind when either is missing or frozen
             roles       RO1, report-only: roles.<role>.acted_share, runs, silent_days, weeks_under, from the ledger
                         (role_use.py); class under rings nothing and lint refuses anything that would
   STORE   append-only JSONL, one file per family: $RM_OPS_WATCH_DIR/series/<family>.jsonl (default
           D:\\ClaudeWork\\rimmandrake\\ops_watch). Every point is {v, m: MEASURED|ESTIMATE|UNMEASURED, why?, unit?}.
           An instrument that errors writes UNMEASURED with the error, never 0.
   RANGES  the rules' ranges block (OP1): each metric's idle, sane, distressed, emergency classes with owner, ack_within_min
           and max_age_min. The relentless and seats verdicts read it; each reading carries its class. `lint` refuses a
           metric short of any of these, and so does load_rules, which then keeps the last good copy and flags it.
   FLAG    Andon rules from ops_watch_rules.json over MEASURED points: band (outside the 7-day mean +/- 3 sigma),
           run (n same-direction changes), silent (a series that stopped being MEASURED), target (a line crossed).
           Each flag names the series and the window. flags.json keeps when each flag first opened.
   WORSE   an alarm still crossed re-raises when its severity rises or its value passes the target's stated `worse` step
           ({"factor": 2} doubling, {"add": 50}), measured from the worst value told (ALARM_REPEAT_FIX_BREAK_ON_WORSE).
   ALARM   a target with alarm true files ONE rimflow item when its condition is NEW (alarms.json dedupes; it re-arms
           only after the condition clears; a failed filing stays PENDING and is retried next pass). Filed as RUNNER
           from the dispatch clone (its testq/ingest.py) under QHOME/ingest.lock. Only with --file-alarms.
   HEALTH  ops_health.py, on a full pass only: Operations' ONE verdict for Relentless, health.json (healthy/degraded, the
           error budget per SLI, the ordered system items, as_of); its points health.state and health.spent_slis (the
           OPS_ERROR_BUDGET_DIAGNOSE alarm). PIPELINE_BUDGET_ENFORCE_HEAL_THYSELF.
   HAND    status.json (every current point: slot_allocator.py reads it), digest.json and digest.md: per KPI the
   OVER    current value, its mark, the change over 24 h and 7 d, and its open flags; one cheap read for Operations.
           digest_blind.md: an ALLOW-LIST (BLIND_KEYS: machine health, disk, stalls, flow, production output
           counts) and only their alarms and flags; everything else is withheld by default, and any line holding a
           token_talk term is dropped too: the only digest the token-blind roles read (review U N2, review V V1).
           Account and runway alarms (TOKEN_FAMILIES) are Operations': kept in alarms.json, never filed as items.

    python3 src/RimMandrake/Utils/ops_watch.py run [--file-alarms]   one pass (the timer passes --file-alarms)
    python3 src/RimMandrake/Utils/ops_watch.py digest                 print digest.md
    python3 src/RimMandrake/Utils/ops_watch.py backfill               seed production from rm-streams-collect' history
    python3 src/RimMandrake/Utils/ops_watch.py install [--apply]      the systemd user timer (plan unless --apply)
"""
import argparse
import calendar
import fnmatch
import glob
import importlib.util
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _p in (HERE, HERE / "pulse", HERE / "sim"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

SCHEMA = "rm.ops_watch/1"
HOUR = 3600.0
DAY = 24 * HOUR
FAMILIES = ("accounts", "codex", "steve", "testing", "disk", "timers", "flow", "process", "tps", "production", "v3", "tokentalk",
            "evidence", "companion", "arena", "relentless", "seats", "plan", "roles", "queues", "wrapup")


def ops_dir() -> Path:
    return Path(os.environ.get("RM_OPS_WATCH_DIR", "/mnt/d/ClaudeWork/rimmandrake/ops_watch"))


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
            raise ValueError("ranges refused: " + "; ".join(ranges_problems(rules))[:300])
    except (OSError, ValueError) as e:
        saved = read_json(last_good)
        if not isinstance(saved, dict):
            raise
        saved["_load_error"] = "%s: %s" % (type(e).__name__, str(e)[:160])
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
                                       % (type(e).__name__, str(e)[:120]))
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
        out[k + "hours_to_reset"] = mk(h, "h to the weekly reset") if h is not None else U("no reset time")
        rate, how = None, None
        try:
            # the slope reads only MEASURED records, so it stays true of an ESTIMATE reading: flat readings mean flat
            r, n, span = SA.slope(name, a.get("week_resets_at"), now, fit)
        except (KeyError, TypeError, ValueError) as e:  # a bad rule costs the slope: the week average still reads
            r, n, span = None, 0, 0
            out["accounts._collector"] = U("accounts_fit unusable, runway uses the week average: %s: %s"
                                           % (type(e).__name__, str(e)[:120]))
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
                    type(e).__name__, str(e)[:120]))
    return out


def codex_dirs():
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
        import pulse_core as pc
        it = pc._model().replay(pc.read_ledger()).items.get(item)
    except Exception:  # noqa: BLE001
        return False
    return it is None or not it.open


def ladder_blind(inc):
    """True when a steward incident's ladder cannot run because the ledger is unreadable (testq/steward.py LEDGER_ERR,
    a torn shard after an unclean stop: OPS_STEVE_UNSTICK_VHRP) and it holds no item: nobody is escalating."""
    return isinstance(inc, dict) and not inc.get("item") and \
        str(inc.get("error") or "").startswith("ledger unreadable: ")


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
                                   reason=str(sj.get("reason") or "")[:160], since=sj.get("since"))
        else:
            out["steve.state"] = M(st, "steward state", reason=str(sj.get("reason") or "")[:160], since=sj.get("since"))
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
                st, fault_min, str(sj["incident"]["error"])[:120]), fault_min))
        # both silent, nothing is left to re-raise: here an unfiled, unknown or closed item owns nothing
        if hb > 30 and (wage is None or wage > 30) and (not wj.get("incident") or incident_unowned(wj["incident"])):
            nobody.append(("steward silent %.0f min and its watcher silent %s" % (
                hb, "(never ran)" if wage is None else "%.0f min" % wage), hb))
        elif hb > 30 and ladder_blind(wj.get("incident")):     # the watcher runs but cannot escalate
            nobody.append(("steward silent %.0f min and its watcher's ladder blind: %s" % (
                hb, str(wj["incident"]["error"])[:120]), hb))
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


def steve_seat_probe(cfg):
    """(reachable, uptime_s, {seats up}). Reachable is False unless the whole probe ran to its last line."""
    cmd = SEAT_PROBE % (" ".join(cfg["seats"]), cfg["ready"])
    try:
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", cfg["ssh"], cmd],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return False, None, set()
    lines = r.stdout.split("\n")
    if "probe-done" not in lines or not lines[0].isdigit():
        return False, None, set()
    return True, int(lines[0]), {x[3:] for x in lines if x.startswith("up ")}


def c_steve_seats(now, rules, ctx):
    """steve.seats_absent_min: how long a seat has been missing, not connected, or the machine out of reach (0 = both
    live). Over the rule's line it alarms: a ledger item and a Conductor log line. Absent since boot counts from the
    boot, so a reboot that never brought them back alarms at the first look past the line; a seat lost later counts
    from the first look that saw it, so one account switch (seconds) does not. Reach failing counts too: a machine
    gone is seats gone, and UNMEASURED would be silent."""
    cfg = rules.get("steve_seats")
    if not cfg:
        return {}
    reach, up, seen = steve_seat_probe(cfg)
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


def c_steve_all(now, rules, ctx):
    out = c_steve(now, rules, ctx)
    out.update(c_steve_seats(now, rules, ctx))
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
    closes = ctx.get("closes")
    if closes is None:      # costs the Steve half only: Archmagi's day records do not need the ledger
        out["testing.steve_nothing_h_7d"] = U("the ledger was not readable, so closes after a run are unknown")
    else:
        ch = rules["testing"]["close_after_h"]
        steve_h, steve_n, unk, young = 0.0, 0, 0, 0
        for fin, d in jobs:
            st = epoch((d.get("result") or {}).get("started"))
            if st is None or fin - st <= 0 or not outcome_of(d) or fail_count_unreadable(d):
                unk += 1        # no span, or no outcome to say whether it caught anything
                continue
            if not caught(d, closes, ch):
                steve_h += (fin - st) / HOUR
                steve_n += 1
                if now - fin < ch * HOUR:
                    young += 1      # its close window is still open: "caught nothing" is provisional
        if jobs and (unk or young or bad):
            out["testing.steve_nothing_h_7d"] = E(round(steve_h, 2), "%d of %d jobs have no start time or outcome (not counted); %d "
                                                  "counted jobs are inside their %d h close window; %d unreadable" % (unk, len(jobs), young, ch,
                                                                                      len(bad)),
                                                  "busy h on jobs that caught nothing, 7 d", jobs=len(jobs),
                                                  nothing_jobs=steve_n, no_span=unk, young=young)
        elif jobs:
            out["testing.steve_nothing_h_7d"] = M(round(steve_h, 2), "busy h on jobs that caught nothing, 7 d", jobs=len(jobs),
                                                  nothing_jobs=steve_n, no_span=unk,
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


def nightly_catchup_reading():
    """nightly_catchup.py's verdict: 1 when a night stopped being retried, so what the nightly feeds is reading an old night.
    Its age is deadman_check's; a reading that cannot be read holds the alarm."""
    p = ops_dir() / "nightly_catchup.json"
    try:
        r = json.loads(p.read_text(encoding="utf-8"))
        st = r["state"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        return {"testing.nightly_gave_up": U("%s: %s" % (type(e).__name__, str(e)[:160]))}
    return {"testing.nightly_gave_up": M(1 if st in ("gave_up", "start_failed") else 0, "nights the sweep stopped being retried",
                                         night=r.get("night"), said=r.get("why", ""))}


def nightly_news(now, ctx):
    """TE1: the nightly's news, the only part of it that alarms (known_reds.py). A blind reading holds the alarm."""
    import known_reds
    keys = ("testing.nightly_news", "testing.nightly_known_reds", "testing.nightly_unparked_reds", "testing.nightly_reds_overdue")
    try:
        v = known_reds.measure(ctx.get("open_ids"), now, with_cop=True)
    except Exception as e:  # noqa: BLE001  a list that cannot be read costs these readings, not the family's
        v = {"why": "%s: %s" % (type(e).__name__, str(e)[:160])}
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
                      detail_read=c["detail_read"]),
           keys[3]: M(len(c["overdue"]), "nightly reds red past their fix deadline, owned or not", night=v["night"],
                      said=c["overdue_said"], news=c["overdue"][:30])}
    # a compose pass (the metronome's sense beat, 15 s) never reruns: it reads the verdicts `rerun-reds` paid for, and
    # a group not rerun yet reads "later" (held, files nothing), as a pass out of budget does
    out.update(red_groups(c, v["night"], budget=0 if ctx.get("no_reruns") else None))
    return out


def rerun_reds(now=None, rules=None):
    """`ops_watch.py rerun-reds` (rm-ops-reds.timer): the NIGHTLY_REDS_FIX_RERUN_BEFORE_PAYING reruns, out of the
    metronome's sense beat, which cannot fit one (a group's rerun takes ~17 s). It reads the night and its red groups
    as a pass does (the flow collector for the open ids) and reruns each group a pass would file, within
    selftest.red_rerun_budget_s, saving each verdict in nightly_rerun.json; it files nothing and writes no status.
    Its own lock, so a sense pass is never Busy behind a rerun."""
    import fcntl
    now = now or time.time()
    rules = rules or load_rules()
    ops_dir().mkdir(parents=True, exist_ok=True)
    with open(ops_dir() / "rerun.lock", "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Busy("another rerun-reds holds %s" % (ops_dir() / "rerun.lock"))
        ctx = {}
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
        raise RuntimeError("git %s: rc %d %s" % (" ".join(args), r.returncode, (r.stderr or "").strip()[:120]))
    return r.stdout.strip()


def rerun_root() -> Path:
    """The clone reruns happen in: the dispatch clone rm-ops-watch runs from and testq already pulls, never the
    clone a hand-run ops_watch happens to sit in (a seat clone must not be pulled under its owner)."""
    return Path(os.environ.get("RM_OPS_RERUN_ROOT", "/home/mandrake/rm/dispatch"))


def rerun_at_main(tests, timeout, root=None):
    """NIGHTLY_REDS_FIX_RERUN_BEFORE_PAYING: one plain rerun (run_selftests --only, no LLM) of a red group's tests in
    this checkout, brought to origin/main first by a fast-forward pull (as testq-tick/testq-sweep already do to the
    dispatch clone ops_watch runs from; it trails origin/main by minutes). -> (verdict, said, sha): verdict green
    (every test ran and passed), red, or unmeasured (could not rerun at origin/main: the group files as before)."""
    root = Path(root) if root else rerun_root()
    gone = [t for t in tests if not (root / t).is_file()]
    if gone:
        return "unmeasured", "not in this checkout: %s" % ", ".join(gone[:3]), None
    try:
        _git(root, "pull", "-q", "--ff-only", "origin", "main", timeout=90)
        head, main = _git(root, "rev-parse", "HEAD"), _git(root, "rev-parse", "origin/main")
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as e:
        return "unmeasured", "git: %s" % str(e)[:160], None
    if head != main:
        return "unmeasured", "checkout at %s, origin/main at %s" % (head[:10], main[:10]), None
    argv = [sys.executable, str(root / "src/RimMandrake/Utils/run_selftests.py"), "--only", *tests]
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
    if r.returncode == 0 and res.startswith("RESULT: GREEN") and "UNMEASURED (" not in out and "DROPPED:" not in out:
        return "green", res[:160], head
    if res.startswith("RESULT: GREEN"):
        return "unmeasured", "green with tests that did not run their check", head
    return "red", res[:160], head


class RerunGate:
    """Each new group of a night is rerun once (the verdict kept in nightly_rerun.json for that night), within the
    pass's budget. verdict(g): green (files nothing), red / unmeasured (files as before), later (budget spent)."""

    def __init__(self, night, run, budget, clock=time.monotonic):
        self.night, self.run, self.clock = night, run, clock
        self.end = clock() + budget
        st = read_json(rerun_path()) if rerun_path().exists() else {}
        self.st = st if isinstance(st, dict) and st.get("night") == night else {"night": night, "groups": {}}
        self.dirty = False

    def verdict(self, g):
        hit = self.st["groups"].get(g["key"])
        if hit and sorted(hit.get("tests", [])) == sorted(g["tests"]):
            return hit["verdict"]
        left = self.end - self.clock()
        if left < 15:
            return "later"
        try:
            v, said, sha = self.run(list(g["tests"]), int(left))
        except Exception as e:  # noqa: BLE001  a broken rerun files the group as before
            v, said, sha = "unmeasured", "%s: %s" % (type(e).__name__, str(e)[:160]), None
        self.st["groups"][g["key"]] = {"verdict": v, "said": said, "sha": sha, "tests": list(g["tests"]),
                                       "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        self.dirty = True
        self.save()     # each verdict as it lands: a pass killed at its deadline keeps the reruns it paid for
        return v

    def green(self):
        return sorted((k, e) for k, e in self.st["groups"].items() if e.get("verdict") == "green")

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


def red_groups(c, night, state=None, rerun="default", budget=None):
    """BUILD COP (known_reds.py): one testing.red_<id> reading per root-cause group of the night's unparked reds, for
    the wildcard alarm NIGHTLY_COP_FIX (one raised item per group). An absent key holds its alarm, so a group gone from
    a READ night reads 0 and clears; an unread night (the sweep is rewriting its output) emits no group and holds all.
    New groups come at most selftest.red_new_items_per_pass a pass (the unit's deadline bounds the spawns), biggest
    first; the rest are absent, so held, and come next pass.
    NIGHTLY_REDS_FIX_RERUN_BEFORE_PAYING: before a new group files, its tests rerun once at origin/main (RerunGate);
    a group green on that rerun is a flake or a launch drop and files nothing, counted in
    testing.nightly_reds_rerun_green."""
    import known_reds
    if not c.get("detail_read"):
        return {}
    run = RERUN_REDS if rerun == "default" else rerun
    gate = RerunGate(night, run, rerun_budget_s() if budget is None else budget) if run else None
    if state is None:
        p = ops_dir() / "alarms.json"
        state = read_json(p) if p.exists() else {}
    held = {aid.split(":", 1)[1] for aid in (state if isinstance(state, dict) else {})
            if aid.startswith("NIGHTLY_RED:testing.red_")}
    cap = known_reds.new_items_per_pass()
    out, fresh = {}, 0
    for g in c["groups"]:
        if g["key"] not in held:
            if fresh >= cap:
                continue
            if gate is not None and gate.verdict(g) in ("green", "later"):
                continue
            fresh += 1
        out[g["key"]] = M(len(g["tests"]), "nightly reds with one first error line, no entry parking them", night=night,
                          subject=red_subject(g["tests"]), said=g["said"], news=["%s (due %s)" % (t, g["due"]) for t in g["tests"][:30]], due=g["due"],
                          titled={"%s (due %s)" % (t, g["due"]): Path(t).name for t in g["tests"][:30]})
    live = {g["key"] for g in c["groups"]}
    for k in sorted(held - live):
        out[k] = M(0, "nightly reds with one first error line, no entry parking them", night=night, said="green or parked")
    if gate is not None:
        gate.save()
        gr = gate.green()
        out["testing.nightly_reds_rerun_green"] = M(
            len(gr), "nightly red groups green on one rerun at origin/main: flaky or a launch drop, filed nothing",
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
                why = "sanity record holds no rm_scratch_clones at its %s: %s" % (phase, str(d[phase].get("problems"))[:160])
    if why:
        return {"disk.scratch_outside_cap": U(why, "clones"), "disk.scratch_outside_distressed": U(why),
                "disk.scratch_outside_blind": M(1, "sources not seen", cause=why[:300])}
    pts = {"disk.scratch_outside_cap": M(v, "clones", phase=phase, at=iso(at), max_age_min=limit)}
    state = read_class(ms, "disk.scratch_outside_cap", pts)
    cause = "%s clones outside the pool cap at the %s of the reaper run of %s" % (fmt(v), phase, iso(at)) if state in ALARMED else "none"
    pts["disk.scratch_outside_distressed"] = M(int(state in ALARMED), "1 when clones pile up outside the cap", state=state, cause=cause)
    pts["disk.scratch_outside_blind"] = M(0, "sources not seen", cause="none")
    return pts


def c_disk(now, rules, ctx):
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
    for end in ("start", "end"):
        try:
            d = json.loads(san.read_text()) if san.exists() else {}
            row = d.get(end) or {}
            out["disk.scratch_dirty_" + end] = M(len(row.get("problems") or []), "sanity problems at the %s of the last run" % end,
                                                 problems=(row.get("problems") or [])[:6],
                                                 residual=(row.get("residual") or [])[:4])
        except (OSError, ValueError, AttributeError) as e:
            out["disk.scratch_dirty_" + end] = M(9999, "sanity problems at the %s of the last run" % end, why="%s: %s" % (san, e))
    out.update(scratch_outside(san, now, rules))
    # The bounded worker-clone pool (WORKER_CLONES_MONITOR_POOL_NOT_RABBITS): read live each tick, never from a cache.
    # One number alarms: clones over the cap, bytes over the cap, plus every clone holding unpushed work nobody is using,
    # in the pool or anywhere else a helper clones (rm/scratch, session dirs: LIQUIDNET_SURFACEGAP_FIX_UNLANDED_CLONES).
    # A pool that cannot be read is the alarm too (9999), not silence.
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import scratch_clone
        pr = scratch_clone.pool_reading()
        ss = scratch_clone.scratch_stranded()
        out["disk.pool_clones"] = M(pr["count"], "worker clones in the pool (cap %d)" % pr["max_clones"])
        out["disk.pool_gb"] = M(pr["gb"], "GB the pool holds (cap %s)" % pr["max_gb"])
        out["disk.pool_oldest_h"] = M(pr["oldest_h"], "hours since the oldest pool clone was made")
        out["disk.pool_breach"] = M(pr["breach"] + len(ss["stranded"]), "pool breaches: over count, over bytes, stranded unpushed clones",
                                    stranded=pr["stranded"] + ss["stranded"], unpushed=pr["unpushed"])
    except Exception as e:
        out["disk.pool_breach"] = M(9999, "pool breaches", why="pool unreadable: %s" % str(e)[:160])
    return out


def systemctl_json(*args):
    r = subprocess.run(["systemctl", "--user"] + list(args) + ["-o", "json", "--no-pager"], capture_output=True,
                       text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError("systemctl %s: exit %d %s" % (" ".join(args), r.returncode, r.stderr.strip()[-200:]))
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


PULSE_DEPLOY = "/mnt/d/ClaudeWork/rimmandrake/pulse-deploy"   # rm-deploy-update's checkout (env RM_PULSE_DEPLOY overrides)


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
        return None, "stamp unreadable: %s" % str(e)[:120]


def c_timers(now, rules, ctx):
    out = {}
    age, why = deploy_update_age(now)
    out["timers.deploy_update_age_min"] = (U(why, "min") if age is None
                                           else M(age, "min since the deploy checkout last fast-forwarded", why=why))
    try:                # two sources: neither one's failure takes the other's reading
        failed = systemctl_json("list-units", "--failed", "--all")
        names = sorted(str(u.get("unit") if isinstance(u, dict) else u) for u in failed)
        real = [n for n in names if n not in one_shot_units(names)]
        out["timers.failed_units"] = M(len(real), "failed user units", units=real[:12], one_shots=sorted(set(names) - set(real))[:12])
    except Exception as e:  # noqa: BLE001
        out["timers.failed_units"] = U("list-units: %s: %s" % (type(e).__name__, str(e)[:160]))
    try:
        timers = systemctl_json("list-timers", "--all")
    except Exception as e:  # noqa: BLE001
        out["timers.overdue_timers"] = U("list-timers: %s: %s" % (type(e).__name__, str(e)[:160]))
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


def untriaged_reading(events):
    """Findings with no outcome yet (findings design section 3). The fold's table is the one judge of an outcome, a spawn
    --from, a retype, an item of that name or a decide, and of an undo of any of them (findings_fold.no_outcome): this
    reading adds no test of its own. A bad table costs this reading alone: UNMEASURED, not a guess."""
    try:
        import findings_fold
        untr = findings_fold.no_outcome(events)
    except Exception as e:  # noqa: BLE001  findings_fold.Unmeasured, or a fold that will not import
        return U("findings fold table: %s: %s" % (type(e).__name__, str(e)[:160]))
    return M(len(untr), "findings with no outcome yet", first=sorted(untr)[:5])


def c_flow(now, rules, ctx):
    import pulse_core as pc
    model = pc._model()
    events = pc.read_ledger()
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
    out = {"flow.untriaged_findings": untriaged_reading(events),
           "flow.closes_24h": M(len(c24), "items closed, 24 h"),
           "flow.verify_pass_24h": M(v24, "verify pass events, 24 h (maker or not)")}
    lapsed = sum(1 for it in world.items.values() if it.open and model.lease_status(it, now) == "lapsed")
    out["flow.lapsed_leases"] = M(lapsed, "open items with a lapsed lease")
    try:
        out["steve.incident_unclaimed_min"] = steve_incident_unclaimed(world, model, now, rules, lane_fault_since(now))
    except Exception as e:  # noqa: BLE001  a bad steve_incident rule costs this reading, not the family's
        out["steve.incident_unclaimed_min"] = U("steve_incident: %s: %s" % (type(e).__name__, str(e)[:160]))
    return out


def lane_fault_since(now):
    """-> the epoch the steward's current fault began, or None: no fault, a stale or unreadable steward.json, or the
    machine down (an escalation blocked on the in-person step is waiting on the right thing then)."""
    sj = read_json(qhome() / "steward.json")
    if not isinstance(sj, dict) or not sj.get("fault") or sj.get("state") == "UNREACHABLE":
        return None
    hb, since = epoch(sj.get("epoch")), epoch(sj.get("since"))
    return since if hb is not None and now - hb <= 30 * 60 and since is not None and since <= now else None


def steve_incident_unclaimed(world, model, now, rules, fault_since=None):
    """steve.incident_unclaimed_min: the age of the OLDEST open steward incident item (id prefix
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
    ages, names = [], []
    for it in world.items.values():
        if not it.id.startswith(pre) or rung in it.id or it.state not in ("proposed", "ready", "doing"):
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
        ages.append(max(0.0, (now - (max(t, fault_since) if it.blocked else t)) / 60.0))
        names.append(it.id)
    if not ages:
        return M(0.0, "min the oldest unclaimed steward incident has waited", why="no unclaimed steward incident")
    return M(round(max(ages), 1), "min the oldest unclaimed steward incident has waited", first=names[:3])


def c_process(now, rules, ctx):
    rx = re.compile(rules["process_regex"])
    r = subprocess.run(["git", "-C", str(data_clone()), "log", "--since=@%d" % int(now - 7 * DAY), "--no-renames",
                        "--name-only", "--format=@@%ct"], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError("git log: " + r.stderr.strip()[-200:])
    commits, cur = [], None
    for line in r.stdout.splitlines():
        if line.startswith("@@"):
            cur = [int(line[2:]), []]
            commits.append(cur)
        elif line.strip() and cur is not None:
            cur[1].append(line.strip())
    out = {}
    for key, span in (("share_24h", DAY), ("share_7d", 7 * DAY)):
        cs = [fs for t, fs in commits if fs and t >= now - span]
        if not cs:
            out["process." + key] = U("no commit with files in the window")
            continue
        p = sum(1 for fs in cs if all(rx.match(f) for f in fs))
        out["process." + key] = M(round(100.0 * p / len(cs), 1), "% of commits touching process paths only",
                                  commits=len(cs), process_only=p)
    try:  # the live lane's occupancy (FOUNDRY_THROUGHPUT_MEASURE_V2_GAP); a ledger that will not read must not cost the shares above
        import bridge_hours as BH
        import pulse_core as pc
        evs = pc._model().read_clone(str(data_clone() / "infrastructure" / "state" / "ledger" / "events.jsonl"))
        for key, span in (("bridge_h_24h", DAY), ("bridge_h_7d", 7 * DAY)):
            out["process." + key] = M(BH.held_hours(evs, now, span), "hours the bridge lock was held (each hold cut at 6 h)")
    except Exception as e:  # noqa: BLE001
        for key in ("bridge_h_24h", "bridge_h_7d"):
            out["process." + key] = U("ledger: %s: %s" % (type(e).__name__, str(e)[:120]))
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
            raise RuntimeError("exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[-200:]))
        json.loads(r.stdout)
        r = subprocess.run([sys.executable, str(HERE / "game_health_check.py"), "latest", "--json"],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise RuntimeError("latest exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[-200:]))
        row = json.loads(r.stdout)
    except Exception as e:  # noqa: BLE001  a broken health check costs these readings, not the tps family's
        return {k: U("game_health_check.py failed: %s" % str(e)[:200]) for k in keys}
    if not isinstance(row, dict) or not isinstance(row.get("breaches"), list):
        return {k: U("no full-list game session recorded yet") for k in keys}
    end = epoch(row.get("end"))
    br = [b.get("key") for b in row["breaches"] if isinstance(b, dict)]
    out = {"tps.health_breaches": M(len(br), "limits crossed by the newest full-list session", session=row.get("session"),
                                    keys=br, said="; ".join("%s=%s (limit %s %s)" % (b.get("key"), b.get("value"),
                                                                                     b.get("op"), b.get("limit"))
                                                            for b in row["breaches"])[:400] or None,
                                    # what the session was doing when each limit fell (game_health_check.py attribute)
                                    attribution={k: "; ".join(v)[:600] for k, v in (row.get("attribution") or {}).items()
                                                 if isinstance(v, list)} or None),
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
        r = subprocess.run([sys.executable, str(HERE / "tps_record.py"), "--json"], capture_output=True, text=True, timeout=90)
        if r.returncode != 0:
            raise RuntimeError("tps_record.py exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[-200:]))
        s = (json.loads(r.stdout) or {}).get("summary") or {}
        if not isinstance(s, dict):
            raise ValueError("tps_record gave a summary that is not an object")
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError, AttributeError) as e:
        why = "tps_record failed: %s: %s" % (type(e).__name__, str(e)[:200])
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
            "why": ("streams mark %r: " % p.get("m") if m != p.get("m") else "") + str(p.get("why") or "")[:200]}


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
    touching any process path is BENCH's, else FOUNDRY's; 'ledger:' commits are skipped, the ledger is read directly),
    'role.<name>' (a finished run's result text; Operations excluded). A group in `bad` could not be read."""
    cfg = rules.get("token_talk") or {}
    since = now - cfg.get("window_days", 7) * DAY
    seats = cfg.get("seats") or ["FOUNDRY"]
    texts, bad = {}, {}
    try:
        events = ctx.get("events")
        if events is None:
            import pulse_core as pc
            events = pc.read_ledger()
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
            bad[sn] = "ledger unreadable: %s: %s" % (type(e).__name__, str(e)[:120])
    try:
        rx = re.compile(rules["process_regex"])
        r = subprocess.run(["git", "-C", str(data_clone()), "log", "--since=@%d" % int(since), "--no-renames", "--name-only",
                            "--format=%x1e%ct%x1f%B%x1f"], capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError("git log: " + r.stderr.strip()[-200:])
        for rec in r.stdout.split("\x1e")[1:]:
            parts = rec.split("\x1f")
            if len(parts) < 3:
                continue
            msg, files = parts[1].strip(), [f for f in parts[2].split("\n") if f.strip()]
            if not msg or msg.startswith("ledger:"):
                continue
            seat = "BENCH" if any(rx.match(f) for f in files) else "FOUNDRY"
            if seat in seats:
                texts.setdefault("commits." + seat, []).append(msg)
    except Exception as e:  # noqa: BLE001
        for sn in seats:
            bad["commits." + sn] = "git log unreadable: %s: %s" % (type(e).__name__, str(e)[:120])
    rd = tt_roles_dir()
    names = set(cfg.get("roles") or ["producer", "arbiter", "auditor", "innovator"])
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
        bad["role._all"] = "role runs unreadable: %s: %s" % (type(e).__name__, str(e)[:120])
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


def c_tokentalk(now, rules, ctx):
    cfg = rules.get("token_talk") or {}
    rx = tt_regex(rules)
    texts, bad = tt_texts(now, rules, ctx)
    out = {}
    seats = cfg.get("seats") or ["FOUNDRY"]
    groups = list(seats) + ["commits." + s for s in seats] + ["role." + r for r in (cfg.get("roles") or
              ["producer", "arbiter", "auditor", "innovator"])]
    for g in groups:
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


def c_arena(now, rules, ctx):
    """arena.two_live: 0 when `arena who` passes, else the failed-check bitmask (ARENA_TWO_LIVE).
    arena.push_refused_24h: alarm lines (PUSH_REFUSED / PUSH_HOOK_CRASH) in <arena>/alarms/arena.jsonl in the last 24 h
    (ARENA_PUSH_REFUSED) - the reader of the hook's alarm file. No arm.toml (the arena switch is not installed) or an
    arena module that cannot run is UNMEASURED, never 0."""
    ad = str(HERE / "arena")
    if ad not in sys.path:
        sys.path.insert(0, ad)
    import arena as AR
    try:
        tp = AR.arm_toml_path()
    except Exception as e:  # noqa: BLE001
        return {"arena.two_live": U("arena root unresolved: %s" % e), "arena.push_refused_24h": U("arena root unresolved")}
    if not tp.exists():
        why = "no arm.toml at %s: the arena switch is not installed" % tp
        return {"arena.two_live": U(why), "arena.push_refused_24h": U(why)}
    try:                # the refusal log below is its own source: it reads whatever becomes of this one
        r = AR.ops_two_live(tp)
        out = {"arena.two_live": M(r["value"], "failed-check bitmask (0 = one arm live)", why=r["why"], mode=r.get("mode"))}
    except Exception as e:  # noqa: BLE001
        out = {"arena.two_live": U("arena who: %s: %s" % (type(e).__name__, str(e)[:160]))}
    try:
        af = "?"
        af = AR.alarm_path()
        n = AR.alarms_since(af, now - 86400)
        out["arena.push_refused_24h"] = M(n, "pre-push refusals/crashes alarmed in the last 24 h", file=str(af))
    except Exception as e:  # noqa: BLE001
        out["arena.push_refused_24h"] = U("alarm file %s unreadable: %s" % (af, e))
    return out


# ---------------------------------------------------------------- relentless: the belt read from its own store (OP2, DI2)
RL_STAFFING = ("relentless.live", "relentless.under_min", "relentless.checks_wait", "relentless.ready")
RL_KEYS = RL_STAFFING + ("relentless.breaker_open_min", "relentless.tick_age_s", "relentless.progress_age_min",
                         "relentless.no_live_min", "relentless.why", "relentless.distressed", "relentless.cause")
RL_RANGES = ("relentless.why", "relentless.ready", "relentless.tick_age_s", "relentless.under_min",
             "relentless.breaker_open_min", "relentless.no_live_min", "relentless.progress_age_min", "relentless.blind")


def rl_root(cfg) -> Path:
    return Path(os.environ.get("RELENTLESS_ROOT") or cfg.get("root") or "/home/mandrake/rm/relentless")


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


def rl_last_progress(store, cfg, now):
    """Newest thing that proves the belt moved: a journal act named in `progress_acts`, or a running worker's beat.
    A staffing reading stamped every tick proves only that the tick ran. -> epoch or None."""
    acts = set(cfg.get("progress_acts") or [])
    newest = None
    for d in tail_json_lines(store / "journal.jsonl"):
        for a in (d.get("acts") if d.get("do") in ("tick", "game_next") else [d]) or []:
            t = epoch(d.get("at"))
            if isinstance(a, dict) and a.get("do") in acts and t is not None and t <= now:
                newest = max(newest or t, t)
    for f in glob.glob(str(store / "items" / "*" / "state.json")):
        st = read_json(f)
        t = st.get("last_beat") if isinstance(st, dict) and st.get("status") == "running" else None
        if is_num(t) and finite(t) and t <= now:
            newest = max(newest or t, t)
    return newest


def rl_run_min(rows, now, pred):
    """Minutes the tail of the staffing record has held `pred`, unbroken, up to now; 0 when its last row does not."""
    since = None
    for r in reversed(rows):
        if not is_num(r.get("t")) or r["t"] > now:
            continue
        if not pred(r):
            break
        since = r["t"]
    return 0 if since is None else round((now - since) / 60.0, 1)


def rl_verdict(rec, points, ms):
    """-> (state, cause) for one readable staffing reading, from the classes of the ranges block: the worst class, and
    the first metric standing in it. Idle is a stop somebody chose, not a jam however long it lasts. A metric whose
    input was not seen has no class and is not judged, so only "distressed" and "emergency" mean anything when an
    input is missing: the caller reads the rest as UNMEASURED."""
    if read_class(ms, "relentless.why", points) == "idle":
        return "idle", "none"
    said = "%s of %s places, %s ready: %s" % (rec.get("running") if rec.get("places") is None else rec["places"],
                                             rec.get("target"), rec.get("ready"), str(rec.get("why") or "filling"))
    worst = "sane", "none"
    for key, name in (("relentless.under_min", "under"), ("relentless.breaker_open_min", "breaker open"),
                      ("relentless.no_live_min", "nothing live"), ("relentless.progress_age_min", "no progress")):
        c = read_class(ms, key, points)
        if c in ALARMED and worst[0] != "emergency" and c != worst[0]:
            worst = c, "%s %.0f min: %s" % (name, points[key]["v"], said)
    return worst


BOOKS_FETCH_BLIND_S = 1800      # the belt lands commits every few minutes; the books_behind target's own 30 min line


def rl_books_behind(books, now):
    """-> (minutes the books clone has been behind origin/main, commits behind), or (None, why). The age is the oldest
    commit it lacks: a clone that jams (BOOKS_STALE_FIX_OPS_CANNOT_SEE_IT) runs stale code with every other reading sane.
    A refused fetch leaves the old ref, and a level clone on an old ref reads 0 behind however far origin has gone: one
    refusal is a blip, but a refused fetch with the ref unmoved for BOOKS_FETCH_BLIND_S is no reading."""
    def git(*a, t=60):
        return subprocess.run(["git", "-C", str(books), *a], capture_output=True, text=True, timeout=t)
    try:
        if not (Path(books) / ".git").exists():
            return None, "no books clone at %s" % books
        got = git("fetch", "--quiet", "origin", t=30)
        if got.returncode:
            try:        # the ref's reflog, not FETCH_HEAD: a refused fetch rewrites FETCH_HEAD, so its stamp is always new
                age = now - (Path(books) / ".git" / "logs" / "refs" / "remotes" / "origin" / "main").stat().st_mtime
            except OSError:
                age = None
            if age is None or age > BOOKS_FETCH_BLIND_S:
                return None, "books clone fetch refused, origin/main %s: %s" % (
                    "has no reflog" if age is None else "unmoved for %d min" % (age // 60), got.stderr[-120:])
        r = git("log", "--format=%ct", "HEAD..origin/main")
    except (OSError, subprocess.SubprocessError) as e:
        return None, "books clone unreadable: %s" % str(e)[:120]
    if r.returncode:
        return None, "books clone unreadable: %s" % r.stderr[-120:]
    ts = [int(x) for x in r.stdout.split() if x.isdigit()]
    return (0.0, 0) if not ts else (round(max(now - min(ts), 0) / 60.0, 1), len(ts))


def rl_game_hold_idle(items_dir, now):
    """-> (minutes the running game has been held by a game-phase holder that does not use it, {holder, kind}), or
    (None, why). RELENTLESS_GAME_HOLD_UNSTICK_IDLE_LIVE_ITER: one live user at a time, so an idle holder parks every other game item
    (ATMOSBASE_PROOF_FIX_UNLIT_LEAVES_DARK_LAMP held it 47 min on 2026-11-03, bridge free, ten items waiting). Counted:
    a `proving` item whose prove pid is gone (minutes since proved_at), and a live-iterating worker (minutes since it
    last held the bridge for its item, or since the FAIL). relentless_game.lapse_holds frees both within live_idle_s
    (20 min) on a tick; above 30 the release is not happening."""
    try:
        names = sorted(os.listdir(items_dir))
    except OSError as e:
        return None, "items unreadable: %s" % str(e)[:120]
    worst, who = 0.0, {"holder": None, "kind": None}
    for n in names:
        st = read_json(Path(items_dir) / n / "state.json")
        if not isinstance(st, dict):
            continue
        g, li, since, kind = st.get("game") or {}, st.get("live_iter"), None, None
        if st.get("status") == "game" and g.get("phase") == "proving":
            pid = g.get("prove_pid")
            if not (is_num(pid) and os.path.exists("/proc/%d" % int(pid))):
                since, kind = g.get("proved_at"), "proving, pid gone"
        elif st.get("status") == "running" and isinstance(li, dict):
            since, kind = (li.get("bridge_seen") or li.get("at")), "live_iter"
        if is_num(since) and finite(since) and since <= now + 300:
            m = round(max(now - since, 0) / 60.0, 1)
            if m > worst:
                worst, who = m, {"holder": n, "kind": kind}
    return worst, who


def rl_live_measured(live_dir, now, cfg):
    """-> (percent of the recent live runs that measured: PASS or FAIL, {n, measured, cause}) or (None, why).
    LIVE_RUNS_FIX_MOSTLY_MEASURE_NOTHING: 25 of 263 live runs (9.5%) measured anything while every other reading was
    sane. Recent = the newest `measured_runs` rows of runs.jsonl within `measured_window_h`; fewer than
    `measured_min_runs` there is too few to judge, UNMEASURED (the lane idle is not a low share)."""
    n_max, win_h, n_min = (cfg.get("measured_runs", 40), cfg.get("measured_window_h", 24), cfg.get("measured_min_runs", 12))
    try:
        rows = tail_json_lines(Path(live_dir) / "runs.jsonl")
    except OSError as e:
        return None, "live/runs.jsonl unreadable: %s" % str(e)[:120]
    recent = [r for r in rows if isinstance(r, dict) and r.get("outcome") and
              now - win_h * 3600 <= (epoch(r.get("at")) or 0) <= now + 300][-n_max:]
    if len(recent) < n_min:
        return None, "only %d live runs in %gh (%d needed to judge)" % (len(recent), win_h, n_min)
    good = sum(r["outcome"] in ("PASS", "FAIL") for r in recent)
    whys = {}
    for r in recent:
        if r["outcome"] not in ("PASS", "FAIL"):
            k = "%s: %s" % (r["outcome"], re.sub(r"[0-9a-f]{7,}|\d+", "N", str(r.get("why") or ""))[:80])
            whys[k] = whys.get(k, 0) + 1
    top = sorted(whys.items(), key=lambda kv: -kv[1])[:3]
    return round(100.0 * good / len(recent), 1), {"n": len(recent), "measured": good,
                                                  "cause": "; ".join("%dx %s" % (v, k) for k, v in top) or "none"}


CHURN_UNITS = ("items returned in the churn window with >= churn_returns returns or one failure class repeated",
               "weighted tokens per 24 h on attempts that were returned",
               "% of weighted tokens over tokens_window_h on attempts that were returned")
CHURN_KEYS = ("relentless.churn_items", "relentless.returned_tokens_day", "relentless.returned_tokens_pct")


def churn_blind(why, tokens_only=False):
    """The churn points read UNMEASURED, keys written out so the alarm census can read each one."""
    pts = {"relentless.returned_tokens_day": U(why, CHURN_UNITS[1]), "relentless.returned_tokens_pct": U(why, CHURN_UNITS[2])}
    if not tokens_only:
        pts["relentless.churn_items"] = U(why, CHURN_UNITS[0])
    return pts


def attempt_failed(r, ok_ends):
    """One attempts.jsonl row -> (epoch or None, ending class) when it is a FAILED ATTEMPT (rl_churn's doc), else None."""
    if not isinstance(r, dict) or not isinstance(r.get("gen"), int) or r.get("start"):
        return None
    if r.get("end") and r["end"] not in ok_ends and "kind" not in r and not attempt_waited(r):
        return epoch(r.get("at")), str(r["end"])
    return None


def attempt_waited(r):
    """One attempts.jsonl row is a WAIT: a `snag --wait-hours` ending (relentless.fail writes wait=true), time not work.
    relentless.fail already keeps it out of the approach ladder; it is no failed attempt, its return is no bounce and its
    gen's spend is no returned work (OPS_CHURN_DIAGNOSE_OPS_GCNF_SOGA: OPS_METRONOME_MIGRATE_CLOCKS_FENCED, cutting one
    clock a day by design, read 'bouncing: 5 returns; waiting_for_sample failed it 5 times' off five planned waits)."""
    return isinstance(r, dict) and isinstance(r.get("gen"), int) and bool(r.get("end")) and r.get("wait") is True


def in_churn(st, fails, now, cfg, waits=0):
    """rl_churn's per-item rule, the one churn definition (RUNNING_NOW's row colours read it too): fails is
    [(epoch, class)] of the item's failed attempts; in churn when one is inside churn_window_h and state.json returns >=
    churn_returns or one class failed it churn_same_class times. waits: the item's wait rows (attempt_waited), whose
    returns state.json counts too and churn does not."""
    return bool(churn_why(st, fails, now, cfg, waits))


def churn_why(st, fails, now, cfg, waits=0):
    """in_churn's reasons, [] when not in churn. The same-class count is windowed to the event (B7, 2026-11-05): a class
    counts only when it failed the item inside churn_window_h, so an old A,A and a new B is not a same-class repeat; an
    old A and a new A is one (the new failure repeats a known one, however slowly the item bounces)."""
    lo = now - float(cfg.get("churn_window_h", 12)) * HOUR
    recent = {c for t, c in fails if lo <= (t or 0) <= now + 300}
    if not recent:
        return []
    same = {}
    for _, c in fails:
        same[c] = same.get(c, 0) + 1
    rets = st.get("returns") if is_num(st.get("returns")) else 0
    rets = max(0, rets - (waits if is_num(waits) else 0))     # a planned wait is a return, never a bounce
    out = ["%d returns" % rets] if rets >= int(cfg.get("churn_returns", 3)) else []
    rep = sorted(c for c in recent if same[c] >= int(cfg.get("churn_same_class", 2)))
    return out + ["%s failed it %d times" % (c, same[c]) for c in rep]


def stage_since(st):
    """When an item entered the stage it is in, by the field each stage writes; None when the stage has no clock. The one
    definition: RUNNING_NOW's time-in-place and churn_item's stuck reason both read it."""
    def field(d, k):
        v = d.get(k) if isinstance(d, dict) else None
        return float(v) if is_num(v) else None
    chk, cand, status = st.get("check"), st.get("candidate"), st.get("status")
    if not isinstance(status, str):
        return None
    return {"queued": field(st, "returned_at") or field(st, "enrolled_at"), "running": field(st, "started_at"), "candidate": field(cand, "at"),
            "checking": field(chk, "at"), "closing": field(st, "tomb_since") or field(chk, "verdict_at") or field(cand, "at"),
            "game": field(st.get("game"), "entered_at"), "held": field(st.get("hold"), "at"), "blocked": field(st, "blocked_at"),
            "stopping": field(st, "stopping_since"), "retiring": field(st, "stopping_since")}.get(status)


CHURN_ITEM_UNIT = "reasons this item churns: bouncing, spend rising with no landed result, stuck in a stage"
CHURN_ITEM_TAG = "CHURN_ITEM"
CHURN_ITEM_PREFIX = "relentless.churn_item."


def churn_subject(item):
    """-> the subject of an item's churn alarm, OPS_CHURN_DIAGNOSE_<subject>_<twist>: the item's first plain word (an intent
    or banned word would break the name grammar) and four letters of the whole id, so each item has one fixed name of its
    own and two items sharing a first word never share one."""
    try:
        import pulse_core as pc
        m = pc._model()
        bad = set(m.INTENT_WORDS) | set(m.BANNED_NAME_WORDS)
    except Exception:  # noqa: BLE001 -- no word bank: a fixed plain word still mints
        bad = None
    word = next((w[:12] for w in str(item).split("_") if re.fullmatch(r"[A-Z][A-Z0-9]*", w) and bad is not None
                 and w[:12] not in bad), "ITEM")
    return "%s_%s" % (word, alarm_twist(str(item)))


def held_churn_items(state=None):
    """Items whose churn alarm alarms.json holds: a held item no longer churning must read 0 to clear (an absent key holds).
    None when alarms.json is there but unreadable: then nothing new may file (the cap cannot be counted)."""
    if state is None:
        p = ops_dir() / "alarms.json"
        state = read_json(p) if p.exists() else {}
    if not isinstance(state, dict):
        return None
    pre = CHURN_ITEM_TAG + ":" + CHURN_ITEM_PREFIX
    return {aid[len(pre):] for aid in (state if isinstance(state, dict) else {}) if aid.startswith(pre)}


def churn_item_points(per, now, cfg, spend_known, held="read"):
    """CHURN_WATCH_BUILD_NAMES_EVERY_BOUNCER (owner 2026-11-05: "what items are just bouncing around the build pipeline,
    costing more and more, or stuck in testing a very very long time without progress"): one relentless.churn_item.<ID>
    reading per item, its value the number of reasons it churns, for the wildcard alarm OPS_CHURN_DIAGNOSE_* (one fixed
    item per churning item, routed to Operations by its OPS_ name). per: {item: (state, fails, spend placed in the
    tokens window)}. Reasons, numbers from relentless.item_bands (shared with RUNNING_NOW's row colours):
      bouncing: churn_why (returns, or a class repeated that failed it inside the window);
      spend rising: not done, retired, closing or put down (held, blocked), state.json spent at the hot `spent` band, and
        spend placed in the window;
      stuck: in a churn_item_stuck_stages stage (game, checking) for the hot age_s band of that stage.
    A held item no longer churning reads 0 (clears); with the spend files unread it holds (UNMEASURED) unless another
    reason still names it. New items come at most churn_item_new_per_pass a pass, and never past churn_item_max_open held
    at once, largest spend first; the rest are absent, so not filed, and come later (57 items read in churn on
    2026-11-05: one raised OPS_ item each would take the whole belt; past the cap relentless.churn_items' incident alarm
    is the one that speaks)."""
    bands = cfg.get("item_bands") if isinstance(cfg.get("item_bands"), dict) else {}
    hot_spent = (bands.get("spent") or [None, None])[1]
    ages = bands.get("age_s") if isinstance(bands.get("age_s"), dict) else {}
    stages = cfg.get("churn_item_stuck_stages") or ("game", "checking")
    parked = set(cfg.get("churn_item_parked_statuses") or ("blocked", "held"))
    held = held_churn_items() if held == "read" else held
    if held is None:
        return {}           # alarms.json unreadable: every churn alarm holds, none files (run_alarms holds filing too)
    cap = max(0, min(int(cfg.get("churn_item_new_per_pass", 5)), int(cfg.get("churn_item_max_open", 12)) - len(held)))
    flagged = []
    torn = set()
    for n, (st, fails, recent, *more) in per.items():
        if not isinstance(st, dict):
            torn.add(n)
            continue
        status = st.get("status") if isinstance(st.get("status"), str) else None
        if status in ("done", "retired") or status in parked:
            # put down (blocked on a named wait, or held): no worker is sent and nothing spends, so a churn alarm only
            # buys a diagnosis run of a cause the block already records (OPS_CHURN_DIAGNOSE_JAM_VPZP_ECXS: JAM_CLASS,
            # blocked on CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS, read 'unmeasured failed it 4 times; spend rising');
            # a held alarm on it reads 0 and clears, and it is read afresh once it is picked up again
            continue
        why = ["bouncing: " + "; ".join(r)] if (r := churn_why(st, fails, now, cfg, more[0] if more else 0)) else []
        spent = st.get("spent") if is_num(st.get("spent")) else 0
        # closing is landing; a put-down item (held, blocked) is sent no run, so its spend is flat, not rising
        # (OPS_CHURN_DIAGNOSE_PIPELINE_NIZE_JOZV: PIPELINE_RENAME_WORKERS_NOW_SWAPPABLE, blocked on reach since 04:02Z with
        # nothing spent after, read 10453k 'spend rising' from the day before's ten UNMEASURED checks)
        if is_num(hot_spent) and spent >= hot_spent and recent > 0 and status not in ("closing", "held", "blocked"):
            why.append("spend rising: %.1fM weighted, %dk in the last %gh, nothing landed" % (
                spent / 1e6, round(recent / 1e3), float(cfg.get("tokens_window_h", 24))))
        t, band = stage_since(st), ages.get(status)
        if status in stages and t and isinstance(band, list) and len(band) > 1 and now - t >= band[1]:
            why.append("stuck: %s for %.1f h, no progress out of it" % (status, (now - t) / HOUR))
        if why:
            flagged.append((-spent, n, st, why))
    flagged.sort(key=lambda f: (f[0], f[1]))
    out, fresh = {}, 0
    for neg, n, st, why in flagged:
        if n not in held:
            if fresh >= cap:
                continue
            fresh += 1
        out[CHURN_ITEM_PREFIX + n] = M(len(why), CHURN_ITEM_UNIT, item=n, subject=churn_subject(n), status=st.get("status"),
                                       gen=st.get("gen"), returns=st.get("returns"), spent=-neg,
                                       said="%s: %s" % (n, "; ".join(why))[:400], reasons=why)
    for n in sorted(held - {f[1] for f in flagged}):
        if n in torn:
            out[CHURN_ITEM_PREFIX + n] = U("state.json of %s torn: whether it still churns is unknown" % n, CHURN_ITEM_UNIT)
        elif spend_known or n not in per:
            out[CHURN_ITEM_PREFIX + n] = M(0, CHURN_ITEM_UNIT, item=n, said="%s: no longer churning" % n)
        else:
            out[CHURN_ITEM_PREFIX + n] = U("spend files unread: whether %s still churns on spend is unknown" % n, CHURN_ITEM_UNIT)
    return out


def rl_churn(store, now, cfg):
    """-> {churn point key: point}. OPS_CHURN_MEASURE_RETURNS_ARE_NOT_PROGRESS: on 2026-11-04 47 items had been returned 3+
    times (one at gen 20) on broken tests and unreachable evidence read as broken work, ~157M weighted tokens, and no reading
    said so: a return counted as the belt moving. Read from the store only, no AI:
      a FAILED ATTEMPT is an attempts.jsonl row with a gen and an `end` that is not in churn_not_fail_ends (the class is its
      signature); an item is IN CHURN when it has a failed attempt inside churn_window_h and either state.json returns >=
      churn_returns or one class failed it churn_same_class times or more.
      RETURNED TOKENS: every run in the spend-YYYYMMDD.json files (marker rm-relentless-{work|check}-<sha1(item)[:10]>-g<gen>)
      whose (item, gen) LAST ending is a failure (a gen-less row, e.g. `done`, belongs to the gen open when it was written):
      a gen that failed a check and was then accepted or resumed sent nothing back (OPS_CHURN_DIAGNOSE_RETURNED_WORK_IWIV,
      2026-11-05: such gens were 9.8 of a 66.2% reading); a run is placed in time by its gen's start row. A run the instrument
      cannot place (unknown marker or no start row) is `unmapped`: over churn_max_unmapped_pct of the window it reads
      UNMEASURED, and no spend in the window is UNMEASURED too (an idle lane is not a clean one).
      x.by_end (OPS_CHURN_DIAGNOSE_RETURNED_WORK_IWIV): the returned spend per ending class of the gen's last failed row
      and lane (work|check), largest first, each "<end>/<lane> <pct of total>%": the 2026-11-04 alarm was diagnosed by
      hand from the store; this reads the shared cause (account_lost/work, unmeasured/check ...) off the point itself."""
    win_h, toks_h = float(cfg.get("churn_window_h", 12)), float(cfg.get("tokens_window_h", 24))
    ok_ends = set(cfg.get("churn_not_fail_ends") or ("finish", "done", "unhold", "blocked", "hold", "conductor_hold",
                                                    "reach_adopted", "reach_repaired", "reach_waiter_released",
                                                    "reach_held", "game_env_route"))
    tlo = now - toks_h * HOUR
    try:
        names = sorted(os.listdir(store / "items"))
    except OSError as e:
        why = "items unreadable: %s" % str(e)[:120]
        return churn_blind(why)
    import hashlib
    by_hash, gen_end, started, churn, classes, torn, per = {}, {}, {}, [], {}, 0, {}
    ended_at = {}       # (item, gen) -> epoch of its latest ending row: a gen ended before the window spent nothing in it
    waited = set()      # (item, gen) whose last ending is a wait (attempt_waited): time, not work, so no returned spend
    for n in names:
        by_hash[hashlib.sha1(n.encode()).hexdigest()[:10]] = n
        st = read_json(store / "items" / n / "state.json")
        fails, cur, waits = [], None, 0
        try:
            with open(store / "items" / n / "attempts.jsonl", encoding="utf-8") as f:
                for ln in f:
                    try:
                        r = json.loads(ln)
                    except ValueError:
                        continue
                    if not isinstance(r, dict):
                        continue
                    if not isinstance(r.get("gen"), int):
                        # a gen-less ending (`done` is written without one) belongs to the gen open when it was written
                        if cur is not None and r.get("end") and "kind" not in r:
                            gen_end[(n, cur)] = str(r["end"])
                        if cur is not None and r.get("end"):
                            ended_at[(n, cur)] = max(ended_at.get((n, cur)) or 0, epoch(r.get("at")) or 0)
                        continue
                    if r.get("start"):
                        started[(n, r["gen"])] = epoch(r.get("at"))
                        cur = r["gen"]
                        continue
                    if r.get("end") and "kind" not in r:
                        gen_end[(n, r["gen"])] = str(r["end"])
                        (waited.add if attempt_waited(r) else waited.discard)((n, r["gen"]))
                        waits += attempt_waited(r)
                    if r.get("end"):
                        k_ = (n, r["gen"])
                        ended_at[k_] = max(ended_at.get(k_) or 0, epoch(r.get("at")) or 0)
                    if attempt_failed(r, ok_ends):
                        t, end = attempt_failed(r, ok_ends)
                        fails.append((t or 0, end))
        except OSError:
            pass        # an item never started has no attempts file
        if not isinstance(st, dict):
            torn += 1
            per[n] = [None, fails, 0, waits]      # torn: a held alarm on it holds, never clears on a state it cannot read
            continue
        per[n] = [st, fails, 0, waits]
        if in_churn(st, fails, now, cfg, waits):
            churn.append((-(st.get("spent") or 0) if is_num(st.get("spent")) else 0, n))
            last = fails[-1][1]
            classes[last] = classes.get(last, 0) + 1
    # a gen is RETURNED when its last ending is a failure: a gen that failed a check and then ended done (or resumed:
    # unhold) sent nothing back to a worker, so its spend is not returned work
    failed = {k: e for k, e in gen_end.items() if e not in ok_ends and k not in waited}
    churn.sort()
    cause = ", ".join("%d %s" % (v, k) for k, v in sorted(classes.items(), key=lambda kv: -kv[1])[:4]) or "none"
    pts = {"relentless.churn_items": M(len(churn), CHURN_UNITS[0], first=[n for _, n in churn[:5]], window_h=win_h,
                                       last_fail=cause, torn_states=torn,
                                       spent=sum(-s for s, _ in churn))}
    tot = ret = unmapped = 0
    by_end = {}
    rx = re.compile(r"rm-relentless-(?:work|check)-([0-9a-f]{10})-g(\d+)")
    day0 = time.strftime("%Y%m%d", time.gmtime(tlo))
    files = sorted(p for p in glob.glob(str(store / "spend-*.json")) if Path(p).name[6:14] >= day0)
    for p in files:
        sp = read_json(p)
        runs = sp.get("runs") if isinstance(sp, dict) else None
        if not isinstance(runs, dict):
            why = "spend file unreadable: %s" % p
            pts.update(churn_blind(why, tokens_only=True))
            pts.update(churn_item_points(per, now, cfg, False))
            return pts
        for m, tk in runs.items():
            if not is_num(tk):
                continue
            g = rx.match(m)
            key = (by_hash.get(g.group(1)), int(g.group(2))) if g else None
            t = started.get(key) if key else None
            if key and key[0] in per and not (ended_at.get(key) and ended_at[key] < tlo and (t or 0) < tlo):
                # the item's spend in the window's day files: a gen started earlier still burns, but one that also ENDED
                # before the window spent nothing in it (OPS_CHURN_DIAGNOSE_BRIDGE_GRXX_AYXK: a day file reaches up to 48 h
                # back, so BRIDGE_STALL_DIAGNOSTIC_1, blocked since 08:25Z the day before, read 1996k 'spend rising')
                per[key[0]][2] += tk
            if t is None:
                unmapped += tk     # its day file is in the window; when in it, unknown: counted against the reading
                continue
            if not tlo <= t <= now + 300:
                continue
            tot += tk
            if key in failed:
                ret += tk
                k = "%s/%s" % (failed[key], m.split("-")[2])
                by_end[k] = by_end.get(k, 0) + tk
    pts.update(churn_item_points(per, now, cfg, True))     # the spend was read: no placed spend is no rising spend
    if tot <= 0:
        why = "no placed spend in the last %gh (%d spend files)" % (toks_h, len(files))
        pts.update(churn_blind(why, tokens_only=True))
        return pts
    share = 100.0 * unmapped / (tot + unmapped)
    if share > float(cfg.get("churn_max_unmapped_pct", 20)):
        why = "%.0f%% of the window's spend files has no item or gen start the instrument can place" % share
        pts.update(churn_blind(why, tokens_only=True))
        return pts
    x = {"total": tot, "returned": ret, "unmapped": unmapped, "window_h": toks_h,
         "by_end": ["%s %.1f%%" % (k, 100.0 * v / tot) for k, v in sorted(by_end.items(), key=lambda kv: (-kv[1], kv[0]))[:6]]}
    pts["relentless.returned_tokens_day"] = M(round(ret * 24.0 / toks_h), CHURN_UNITS[1], **x)
    pts["relentless.returned_tokens_pct"] = M(round(100.0 * ret / tot, 1), CHURN_UNITS[2], **x)
    return pts


def rl_jams(store, now):
    """JAM_CLASS_BUILD_OPS_DETECTOR_PER_CLASS: the belt's journaled jams read against rimflow/jam_classes.json.
    relentless.jam_unnamed counts jams no class names, relentless.jam_repeat jams of a class after its fixed.at; both
    targets alarm. A registry or journal that cannot be read makes both UNMEASURED (and relentless.blind counts it)."""
    try:
        root = str(HERE.parent)
        if root not in sys.path:
            sys.path.insert(0, root)
        import importlib
        jc = importlib.import_module("rimflow.jam_classes")
        reg = jc.load()
        c = jc.census(reg, store / "journal.jsonl", now)
    except (OSError, ValueError, KeyError, TypeError, ImportError) as e:
        c = {"error": "jam registry unreadable: %s" % e}
    if "error" in c:
        why = "jams unreadable: %s" % c["error"]
        return {"relentless.jam_unnamed": U(why, "jams"), "relentless.jam_repeat": U(why, "jams")}
    un, rep = c["unnamed"], c["repeats"]
    return {"relentless.jam_unnamed": M(len(un), "jams", first=(un[0]["why"][:200] if un else "none"),
                                        window_days=c["window_days"]),
            "relentless.jam_repeat": M(len(rep), "jams", first=("%s: %s" % (rep[0]["cls"], rep[0]["why"][:180]) if rep
                                                                 else "none"), classes=sorted({r["cls"] for r in rep}),
                                       window_days=c["window_days"])}


CHECK_VERDICT_ACTS = ("blind_fail", "proof_weak", "game_entered", "unmeasured", "proof_rework")


def rl_checks_lost(store, now, cfg, chunk=1 << 23):
    """CHECKER_DEATHS_ALARM_BUILD_29_WENT_UNHEARD: on 2026-11-03 every walled checker died at launch (EACCES) for 2.5 h,
    29 of 29, and each item read only its own checker_lost. -> the point relentless.checks_lost_items: how many DIFFERENT
    items lost a checker (journal act checker_lost; an account_lost is the account's, not the checker's) inside
    checks_lost_window_h, with the checks started and the verdicts given in that window beside it. UNMEASURED when the
    journal cannot be read, or the tail read does not reach back to the window's start (a count from half a window
    would read low)."""
    window = float(cfg.get("checks_lost_window_h", 1)) * 3600.0
    start = now - window
    p = store / "journal.jsonl"
    try:
        with open(p, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - chunk))
            lines = f.read().split(b"\n")
    except OSError as e:
        return U("journal.jsonl unreadable: %s" % e, "items")
    if size > chunk:
        lines = lines[1:]       # the first line is torn by the seek
    oldest, lost, started, verdicts = None, {}, 0, 0
    empty, err = 0, None        # CHECKER_DEATHS_MONITOR_29_NOBODY_NOTICED: relentless.run_output on the act
    for ln in lines:
        try:
            d = json.loads(ln)
        except ValueError:
            continue
        t = epoch(d.get("at")) if isinstance(d, dict) else None
        if t is None:
            continue
        oldest = t if oldest is None else min(oldest, t)
        if t < start or t > now:
            continue
        for a in (d.get("acts") if d.get("do") in ("tick", "game_next") else [d]) or []:
            if not isinstance(a, dict):
                continue
            do = a.get("do")
            if do == "checker_lost" and a.get("item"):
                lost[a["item"]] = lost.get(a["item"], 0) + 1
                empty += a.get("out_bytes") == 0        # it wrote no output: died at launch, not mid-check
                err = a.get("err_tail") or err
            elif do == "check_started":
                started += 1
            elif do in CHECK_VERDICT_ACTS:
                verdicts += 1
    if size > chunk and (oldest is None or oldest > start):
        return U("journal tail read (%d MB) does not reach back %g h" % (chunk >> 20, window / 3600.0), "items")
    worst = sorted(lost, key=lambda i: (-lost[i], i))
    return M(len(lost), "items", lost=sum(lost.values()), started=started, verdicts=verdicts, window_h=window / 3600.0,
             empty=empty, err=(err or "")[:200],
             items=worst[:12], first=("%d checkers lost on %d items in %g h (%d wrote no output), %d verdicts, %d checks started (%s)"
                                      % (sum(lost.values()), len(lost), window / 3600.0, empty, verdicts, started,
                                         ", ".join(worst[:5])) if lost else "none"))


CHECK_RUN_BREAKS = CHECK_VERDICT_ACTS + ("check_passed",)   # done is not one: an item closes off the checker too
CHECK_DEATHS = ("checker_lost", "check_launch_fail")


def rl_checker_deaths_run(store, now, cfg, chunk=1 << 23):
    """CHECKER_DEATHS_MONITOR_29_NOBODY_NOTICED: on 2026-11-03 every walled checker died at launch for 2.5 h and none
    gave a verdict; each item read only its own checker_lost. -> the point relentless.checker_deaths_run: how many
    DIFFERENT items are in the run of checker deaths (checker_lost, check_launch_fail) that ends now, across items, with
    no verdict between and every death empty. The run is broken by any verdict act (CHECK_RUN_BREAKS, and a live_broken read
    after a checker's PASS: a checker that judged, so the launch works; a closing retry's live_broken is not one) and by a checker_lost whose run wrote output (out_bytes > 0: it started and died
    mid-check, not at launch). out_bytes 0 or check_launch_fail is empty; out_bytes absent or None (an act from before
    relentless.run_output, or an unreadable out file) is not known to hold output, so it stays in the run and counts as
    unknown. Only acts inside checker_run_window_h are read. UNMEASURED as rl_checks_lost: unreadable journal, or a tail
    read that does not reach back to the window's start."""
    window = float(cfg.get("checker_run_window_h", 3)) * 3600.0
    start = now - window
    p = store / "journal.jsonl"
    try:
        with open(p, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - chunk))
            lines = f.read().split(b"\n")
    except OSError as e:
        return U("journal.jsonl unreadable: %s" % e, "items")
    if size > chunk:
        lines = lines[1:]       # the first line is torn by the seek
    oldest, run, since, err, broke = None, [], None, None, None
    empty = unknown = 0
    for ln in lines:
        try:
            d = json.loads(ln)
        except ValueError:
            continue
        t = epoch(d.get("at")) if isinstance(d, dict) else None
        if t is None:
            continue
        oldest = t if oldest is None else min(oldest, t)
        if t < start or t > now:
            continue
        for a in (d.get("acts") if d.get("do") in ("tick", "game_next") else [d]) or []:
            if not isinstance(a, dict):
                continue
            do = a.get("do")
            wrote = do == "checker_lost" and isinstance(a.get("out_bytes"), int) and a["out_bytes"] > 0
            if do in CHECK_RUN_BREAKS or (do == "live_broken" and a.get("after_check")) or wrote:
                run, since, err, empty, unknown = [], None, None, 0, 0
                broke = "%s %s at %s" % (do, a.get("item") or "", d.get("at"))
            elif do in CHECK_DEATHS and a.get("item"):
                run.append(a["item"])
                since = since or d.get("at")
                if do == "check_launch_fail" or a.get("out_bytes") == 0:
                    empty += 1
                else:
                    unknown += 1
                err = a.get("err_tail") or a.get("why") or err
    if size > chunk and (oldest is None or oldest > start):
        return U("journal tail read (%d MB) does not reach back %g h" % (chunk >> 20, window / 3600.0), "items")
    items = list(dict.fromkeys(run))
    return M(len(items), "items", deaths=len(run), empty=empty, unknown=unknown, since=since, err=(err or "")[:200],
             broken_by=broke or "nothing in the window", window_h=window / 3600.0, items=items[:12],
             first=("%d checkers in a row on %d items died with no verdict since %s (%d wrote no output, %d unknown; "
                    "last break: %s): %s" % (len(run), len(items), since, empty, unknown, broke or "none in window",
                                             ", ".join(items[:5])) if run else "none"))

def c_relentless(now, rules, ctx):
    """The belt's own readings (OP2), judged here (DI2: a stall names one cause) with no AI. Every limit is in
    rules["relentless"]. A source that is missing, torn, frozen or dated ahead makes its readings UNMEASURED and counts
    in relentless.blind, whose target alarms: nothing here can read sane on a source it did not see move, so with any
    source the verdict reads blind (staffing, reading, the staffing rows, breaker, journal) it is UNMEASURED unless what was
    seen already proves distress; the books, game-hold and live-run probes are not its inputs, so they count in
    relentless.blind (which alarms) without unseating it. Freshness is the stamp inside
    the file, never its mtime; relentless.progress_age_min catches a stamp that moves on a belt that does not."""
    cfg = rules.get("relentless")
    if not isinstance(cfg, dict):
        return {**{k: U("ops_watch_rules.json has no relentless block") for k in RL_KEYS},
                "relentless.blind": M(1, "sources not seen", cause="ops_watch_rules.json has no relentless block")}
    no_range = need_ranges(rules, RL_RANGES)
    if no_range:
        return {**{k: U(no_range) for k in RL_KEYS}, "relentless.blind": M(1, "sources not seen", cause=no_range[:300])}
    ms = ranges_of(rules)
    store = rl_root(cfg) / "store"
    limit = ms["relentless.tick_age_s"]["max_age_min"]
    rows_limit = ms["relentless.no_live_min"]["max_age_min"]
    pts, bad = {}, []

    def missing(k, why):
        pts[k] = U(why)
        bad.append(why)

    rec = read_json(store / "staffing.json")
    t = rec.get("t") if isinstance(rec, dict) else None
    why = None
    if not is_num(t) or not finite(t):
        why = "staffing.json missing or torn in %s" % store
    elif t > now + 300:
        why = "staffing.json is dated %d s ahead of the clock" % (t - now)
    elif now - t > limit * 60:
        why = "staffing.json frozen: last stamped %s, %.0f min ago, limit %g" % (iso(t), (now - t) / 60.0, limit)
    fresh = why is None
    if is_num(t) and finite(t) and t <= now + 300:
        pts["relentless.tick_age_s"] = M(round(max(now - t, 0)), "s", max_age_min=limit)
    else:
        pts["relentless.tick_age_s"] = U(why, "s")
    if fresh:
        ch = rec.get("checks") if isinstance(rec.get("checks"), dict) else {}
        pts["relentless.live"] = M(rec.get("live"), "workers and checks running", target=rec.get("target"),
                                   places=rec.get("places"), max_age_min=limit)
        pts["relentless.under_min"] = M(rec.get("minutes_under"), "min", max_age_min=limit)
        pts["relentless.checks_wait"] = M(ch.get("waiting"), "checks waiting", oldest_wait_s=ch.get("oldest_wait_s"),
                                          max_age_min=limit)
        pts["relentless.ready"] = M(rec.get("ready"), "items ready", max_age_min=limit)
        if not all(is_num(pts[k]["v"]) for k in RL_STAFFING):
            fresh, why = False, "staffing.json lacks a reading: %s" % sorted(
                k.split(".")[1] for k in RL_STAFFING if not is_num(pts[k]["v"]))
    if not fresh:
        for k in RL_STAFFING:
            pts[k] = U(why)
        bad.append(why)
    rd = read_json(store / "reading.json")
    rd_t = epoch(rd.get("at")) if isinstance(rd, dict) else None
    if rd_t is None:
        bad.append("reading.json missing or torn in %s" % store)
    elif rd_t > now + 300:      # a stamp ahead would read fresh until the clock caught up with it
        bad.append("reading.json is dated %d s ahead of the clock" % (rd_t - now))
    elif now - rd_t > limit * 60:
        bad.append("reading.json frozen: last stamped %s" % iso(rd_t))
    try:
        rows = tail_json_lines(store / "staffing.jsonl")
        newest = max((r["t"] for r in rows if is_num(r.get("t")) and finite(r["t"]) and r["t"] <= now), default=None)
        rows_why = "staffing.jsonl has no reading" if newest is None else (
            "staffing.jsonl frozen: last row %s" % iso(newest) if now - newest > rows_limit * 60 else None)
    except OSError as e:
        rows, rows_why = [], "staffing.jsonl unreadable: %s" % e
    if rows_why:
        bad.append(rows_why)
    br = read_json(store / "breaker.json")
    breaker_min = None
    if not isinstance(br, dict):
        missing("relentless.breaker_open_min", "breaker.json missing or torn in %s" % store)
    else:
        until = br.get("until")
        opened = is_num(until) and finite(until) and until > now
        if opened and rows_why:         # how long it has been open is only in the record
            pts["relentless.breaker_open_min"] = U("breaker open until %s, for how long unseen: %s" % (iso(until), rows_why))
        else:
            breaker_min = rl_run_min(rows, now, lambda r: str(r.get("why") or "").startswith("breaker open")) if opened else 0
            pts["relentless.breaker_open_min"] = M(breaker_min, "min", until=iso(until) if opened else None,
                                                   said=str(br.get("why") or "")[:200], max_age_min=limit)
    try:
        last = rl_last_progress(store, cfg, now)
    except OSError as e:
        last = None
        missing("relentless.progress_age_min", "journal.jsonl unreadable: %s" % e)
    progress_min = None if last is None else round((now - last) / 60.0, 1)
    if "relentless.progress_age_min" not in pts:
        if last is None:
            missing("relentless.progress_age_min", "journal.jsonl holds no progress act and no worker beats")
        else:
            pts["relentless.progress_age_min"] = M(progress_min, "min")
    if fresh and not rows_why:
        pts["relentless.no_live_min"] = M(rl_run_min(rows, now, lambda r: r.get("live") == 0), "min")
    else:
        pts["relentless.no_live_min"] = U(rows_why or why, "min")
    pts["relentless.why"] = M(str(rec.get("why") or "filling")) if fresh else U(why)
    state, cause = "unseen", why
    if fresh:
        state, cause = rl_verdict(rec, pts, ms)
    if state in ALARMED or (fresh and not bad):
        pts["relentless.distressed"] = M(int(state in ALARMED), "1 when the belt is distressed or worse", state=state, cause=cause)
        pts["relentless.cause"] = M(cause)
    else:
        pts["relentless.distressed"] = pts["relentless.cause"] = U(why or "; ".join(bad)[:300])
    behind_min, behind_n = rl_books_behind(rl_root(cfg) / "books", now)
    if behind_min is None:
        pts["relentless.books_behind_min"] = U(behind_n, "min")
        bad.append(str(behind_n))       # an unreadable books clone must reach relentless.blind (the MEASURED alarm cannot)
    else:
        pts["relentless.books_behind_min"] = M(behind_min, "min", behind=behind_n)
    held, who = rl_game_hold_idle(store / "items", now)
    if held is None:
        pts["relentless.game_hold_idle_min"] = U(who, "min")
        bad.append(str(who))
    else:
        pts["relentless.game_hold_idle_min"] = M(held, "min", **who)
    pct, got = rl_live_measured(rl_root(cfg) / "live", now, cfg)
    pts["relentless.live_measured_pct"] = U(got, "%") if pct is None else M(pct, "%", **got)
    if pct is None and "unreadable" in str(got):     # too few runs is idle, not blind; an unreadable file is blind
        bad.append(str(got))
    for k, p in rl_churn(store, now, cfg).items():
        pts[k] = p
        if p.get("m") == "UNMEASURED" and "unreadable" in str(p.get("why")) and p["why"] not in bad:
            bad.append(p["why"])      # an unreadable store or spend file is blind; no spend yet is only idle
    lost_p = rl_checks_lost(store, now, cfg)
    pts["relentless.checks_lost_items"] = lost_p
    if lost_p.get("m") == "UNMEASURED":
        bad.append(lost_p["why"])       # an unread journal hides every dead checker: blind, never quiet
    run_p = rl_checker_deaths_run(store, now, cfg)
    pts["relentless.checker_deaths_run"] = run_p
    if run_p.get("m") == "UNMEASURED" and run_p["why"] not in bad:
        bad.append(run_p["why"])        # the same journal: blind, never quiet
    for k, p in rl_jams(store, now).items():
        pts[k] = p
        if p.get("m") == "UNMEASURED" and p["why"] not in bad:
            bad.append(p["why"])        # an unread journal or registry hides every jam class: blind, never quiet
    pts["relentless.blind"] = M(len(bad), "sources not seen", cause="; ".join(bad)[:300] or "none")
    return pts


def st_suppressed(points, fam):
    """A pass that did not measure <fam>.blind (the collector raised, or was taken out of the pass) must not read as
    quiet: the point is written here so its target alarms, on this pass, whatever stopped the collection."""
    why = str((points.get(fam + "._collector") or {}).get("why") or "the %s collector did not run this pass" % fam)
    return M(1, "sources not seen", cause=why[:300])


# ---------------------------------------------------------------- plan: the priority list and its advance (DI3, MI1)
PL_KEYS = ("plan.list_state", "plan.days_since_advance", "plan.distressed", "plan.cause")
PL_RANGES = ("plan.list_state", "plan.list_age_h", "plan.days_since_advance", "plan.blind")


def plan_modules():
    root = str(HERE.parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    import importlib
    return importlib.import_module("rimflow.priority_list"), importlib.import_module("rimflow.model")


def pl_verdict(ms, pts, closes, days, state):
    """-> (class, cause): the worst class of the three judged readings, and the first reading standing in it."""
    flat = sorted(days.items(), key=lambda kv: -kv[1])[:1]
    said = {"plan.list_state": "priority list %s" % state,
            "plan.list_age_h": "priority list %s h old" % (pts["plan.list_age_h"].get("v") if isinstance(pts.get("plan.list_age_h"), dict) else "?"),
            "plan.days_since_advance": "%s flat %s days despite %d closes" % (flat[0][0], flat[0][1], closes) if flat else "no entry read"}
    worst = "sane", "none"
    for key, text in said.items():
        c = read_class(ms, key, pts)
        if c in ALARMED and (worst[0] == "sane" or c == "emergency" and worst[0] != "emergency"):
            worst = c, text
    return worst


def c_plan(now, rules, ctx):
    """plan.* (DI3, MI1): is the priority list one anybody may obey, and does each entry's finish-line reading rise?
    Read from the data clone, as the ring and the pool read their own. Limits in the ranges block; the rest in
    rules["plan"]. Closes are counted only to be named: they clear nothing. An entry's best reading and when it last
    rose are kept in plan_advance.json beside the series; a torn one, a ledger or a reading not seen counts in
    plan.blind, whose target alarms."""
    no_range = need_ranges(rules, PL_RANGES)
    cfg = rules.get("plan")
    if no_range or not isinstance(cfg, dict) or not isinstance(cfg.get("status_rank"), dict):
        why = no_range or "ops_watch_rules.json has no plan.status_rank"
        return {**{k: U(why) for k in PL_KEYS}, "plan.list_age_h": U(why, "h"), "plan.blind": M(1, "sources not seen", cause=why[:300])}
    PL, model = plan_modules()
    ms, root = ranges_of(rules), data_clone()
    got = PL.load(root)
    bad, closes, entries = [], 0, got["entries"]
    state = got["state"]
    try:
        evs = model.read_clone(str(root / "infrastructure" / "state" / "ledger" / "events.jsonl"))
        world = model.replay(evs)
        if not world.items:
            raise ValueError("the ledger holds no items")
    except Exception as e:  # noqa: BLE001  whatever stopped the ledger: not seen, never sane, never a closed entry
        world, evs = None, []
        bad.append("ledger: %s: %s" % (type(e).__name__, str(e)[:160]))
    pts = {"plan.entries": M(len(entries), "entries")}
    if got["state"] == "ok":
        t = PL.epoch(got["doc"]["set_at"])
        if t > now + PL.FUTURE_SLACK_S:
            state = "future_set_at"
            pts["plan.list_age_h"] = U("set_at %s is ahead of now" % got["doc"]["set_at"], "h")
        else:
            pts["plan.list_age_h"] = M(round(max(now - t, 0) / HOUR, 2), "h", set_at=got["doc"]["set_at"], set_by=got["doc"]["set_by"])
    else:
        pts["plan.list_age_h"] = U(got["why"], "h")
    closed = PL.closed_entries(entries, world, model.OPEN_STATES) if world is not None else []
    if closed:
        state = "closed_entry"
    p = ops_dir() / "plan_advance.json"
    kept = read_json(p) if p.exists() else {}
    if not isinstance(kept, dict):
        bad.append("plan_advance.json is torn")
        kept = {}
    live = [e for e in entries if PL.entry_key(e) not in closed]
    new, days, unread = PL.advance(live, root, cfg["status_rank"], kept, now)
    bad += ["%s: %s" % kv for kv in sorted(unread.items())]
    if got["state"] == "ok":        # a torn list says nothing about advance, and must not start every clock again
        atomic_json(p, new)
    if world is not None and days:
        since = min(new[k]["rose_t"] for k in days)
        closes = sum(1 for ev in evs if ev.get("event") == "close" and (epoch(ev.get("ts")) or 0) >= since)
    pts["plan.list_state"] = M(state, why=(got["why"] or ", ".join(closed))[:300])
    if days:
        pts["plan.days_since_advance"] = M(max(days.values()), "days", per_entry=days, closes=closes)
    else:
        pts["plan.days_since_advance"] = U("no entry on the list to read: %s" % state, "days")
    cls, cause = pl_verdict(ms, pts, closes, days, state)
    pts["plan.distressed"] = M(int(cls in ALARMED), "1 when the plan list is distressed or worse", state=cls, cause=cause)
    pts["plan.cause"] = M(cause)
    pts["plan.blind"] = M(len(bad), "sources not seen", cause="; ".join(bad)[:300] or "none")
    return pts


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
        import pulse_core as pc
        events = pc.read_ledger()
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
                "seats.blind": M(1, "sources not seen", cause=no_range[:300])}
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
        pts["seats.blind"] = M(1, "sources not seen", cause=why[:300])
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


PROGRESS_RESTAT = 4000        # names already seen that each pass stats again, in turn


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


def _q_ralph_c(q, now, pcache, cpath):
    """The arena's live-test runner queue (ralph_c_runner): a candidate in candidates.jsonl with no counted result is
    pending since its publication `ts`; a runner claims it as claims/<cand> (O_EXCL, taken over after CLAIM_TTL_S);
    a run's log is written under logs/ when it ends, beside results/<run>.json. A claim is written once and a run may
    take hours (its proof alone 1800 s), so the run's heartbeat is the lane's event log (events/*.jsonl: every
    live act of a lane appends one). The runner's own pending() decides what waits, so this reads the queue the
    runners read. A ralph_c dir that is missing or a module that cannot run is blind."""
    ad = str(HERE / "arena")
    if ad not in sys.path:
        sys.path.insert(0, ad)
    import ralph_c_runner as R
    p = R.rpaths(Path(q["root"]))
    if not p["rc"].is_dir():
        raise OSError("ralph_c dir missing: %s" % p["rc"])
    pub = os.stat(p["candidates"]).st_mtime if p["candidates"].exists() else now
    plist = [_iso_epoch(c.get("ts")) or pub for c in R.pending(p)]
    alist = _mtimes(p["claims"], "*")
    marks = [max(alist) if alist else None, newest_mtime(p["results"]), newest_mtime(p["logs"], "*.log"),
             newest_mtime(p["events"], "*.jsonl")]
    return plist, alist, marks


REPLAY_INFLIGHT = ("RUNNING", "HOLD_CAPACITY", "RESTARTED", "STALLED")


def _last_jsonl(path, tail=1 << 16):
    with open(path, "rb") as f:
        f.seek(0, 2)
        f.seek(max(0, f.tell() - tail))
        lines = [x for x in f.read().splitlines() if x.strip()]
    return json.loads(lines[-1]) if lines else {}


def _q_replay(q, now, pcache, cpath):
    """The arena replay arms and their watcher (replay_watch.py): the replay's work is each arm's task list, and what
    notices a dead or hung arm is the watcher's tick. An arm is in flight when the last tick saw it RUNNING,
    HOLD_CAPACITY, RESTARTED or STALLED, or when its logs/<arm>.log moved after that tick and does not end on the
    runner's `runner ends` line (a relaunch no tick has seen; an arm that finished after the last tick is not in
    flight). It is pending since that tick, and the only movement is the next tick: an arm running with nobody
    watching is the orphan this class is about. Past the replay's stop line nothing is in flight (the watcher stands
    down there too), whatever is left on disk. A replay dir that is missing, a tick line that does not parse, or an
    arm in flight with no ticks.jsonl at all (no watcher ever ticked: no start to measure from) is blind."""
    import replay_watch as RW
    if now >= float(q.get("stop_line", RW.STOP_LINE)):
        return [], [], []
    replay = Path(q.get("replay") or RW.DEFAULTS["replay"])
    ticks = Path(q.get("ticks") or Path(RW.DEFAULTS["arena"]) / "replay_watch" / "ticks.jsonl")
    if not replay.is_dir():
        raise OSError("replay dir missing: %s" % replay)
    tick_t, states = None, {}
    if ticks.exists():
        tick_t = os.stat(ticks).st_mtime
        states = {r["arm"]: r.get("state") for r in _last_jsonl(ticks).get("rows", [])}
    plist = []
    for arm in q.get("arms") or RW.ARMS:
        lf = replay / "logs" / ("%s.log" % arm)
        try:
            lm = os.stat(lf).st_mtime
        except FileNotFoundError:
            lm = None
        moved = lm is not None and (tick_t is None or lm > tick_t)
        if moved:
            last = RW.parse_log(RW.read_text(lf, 1 << 14))
            moved = not (last and RW.ENDS.match(last[-1][1]))
        if states.get(arm) in REPLAY_INFLIGHT or moved:
            if tick_t is None:
                raise OSError("replay arm %s in flight and no replay_watch tick ever: %s" % (arm, ticks))
            plist.append(tick_t)
    return plist, [], [tick_t]


def _q_designer(q, now, pcache, cpath):
    """The Designer's concepts (DESIGNER_STALL_MONITOR_READY_AND_FORGOTTEN): the Designer is run-now only, so a concept
    whose stage.json reads status=ready waits on someone launching it, and nothing else notices (FlowWorks sat at
    stage 2 ready for 12 h+ on 2026-11-04). Each ready concept is pending since it last moved: the later of its last
    history row (a run's open or close, an unblock, a reopen) and its open run's start. Pending times only, no marks,
    so the stall is the OLDEST ready concept's (a run on one concept never hides another left behind); a run open
    longer than the threshold with no close is a stall too (measured runs take 2 to 11 min). A concept at
    waiting_owner whose owner has ANSWERED (designer_stage.owner_moved; DESIGNER_ANSWERED_MONITOR_WAITING_ON_NOBODY)
    is pending too, since his answer (designer_stage.owner_answered_at): only a run's open moves it back to ready, so
    it is forgotten the same way. One still waiting on him, blocked or locked is not pending. root: the concepts dir
    (default designer_stage.concepts_root(), the Designer clone's design/concepts); repo: the clone whose OWNER shard
    is read (default designer_stage.REPO; the concept's own clone is read too); a missing root, a stage.json that does
    not parse, a ready concept with no readable time, or a waiting concept whose OWNER shard is unreadable is blind."""
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
    plist, alist = [], []
    for f in sorted(root.glob("*/stage.json")):
        with open(f, encoding="utf-8") as fh:
            st = json.load(fh)
        if not isinstance(st, dict):
            raise ValueError("stage.json is not an object: %s" % f)
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
        hs = [h for h in (st.get("history") or []) if isinstance(h, dict)]
        last = _iso_epoch(hs[-1].get("at")) if hs else None
        if last is None and run_at is None:
            raise ValueError("ready concept with no readable history or run time: %s" % f)
        plist.append(max(t for t in (last, run_at) if t is not None))
    return plist, alist, []


QUEUE_READERS = {"dirs": _q_dirs, "ralph_c": _q_ralph_c, "replay_arms": _q_replay, "designer_stage": _q_designer}


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
            out[k + "stalled_min"] = U("%s: %s" % (type(e).__name__, str(e)[:150]), "min")
    wanted = {str(Path(x)) for q in qs if isinstance(q, dict) for x in (q.get("progress") or [])}
    for k_ in [k_ for k_ in pcache if k_ not in wanted]:      # a dir dropped from the rules leaves the cache
        pcache.pop(k_)
    _save_json(cpath, pcache)
    out["queues.blind"] = M(len(blind), "queues not seen", names=",".join(blind))
    return out


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
        out["wrapup.debris_standing"] = U("%s: %s" % (type(e).__name__, str(e)[:160]))
        out["wrapup.records_24h"] = U("%s: %s" % (type(e).__name__, str(e)[:160]))
    return out


COLLECTORS = {"accounts": c_accounts, "codex": c_codex, "steve": c_steve_all, "flow": c_flow, "testing": c_testing,
              "disk": c_disk, "timers": c_timers, "process": c_process, "tps": c_tps, "production": c_production,
              "v3": c_v3, "tokentalk": c_tokentalk, "evidence": c_evidence, "companion": c_companion,
              "arena": c_arena, "relentless": c_relentless, "seats": c_seats, "plan": c_plan, "roles": c_roles,
              "queues": c_queues, "wrapup": c_wrapup}
ORDER = ("accounts", "codex", "steve", "flow", "testing", "disk", "timers", "process", "tps", "production", "v3", "tokentalk",
         "evidence", "companion", "arena", "relentless", "seats", "plan", "roles", "queues", "wrapup")


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
    if tg.get("expedite_field") is not None and not (isinstance(tg["expedite_field"], str) and tg["expedite_field"]):
        return "bad expedite_field %r on %s" % (tg["expedite_field"], tg["key"])
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
            if not counts_as_measured(p) and matches(k, sl["keys"]) and not matches(k, sl["skip"]):
                lm = last_measured.get(k)
                lim = next((h for pat, h in sl["per_key"].items() if fnmatch.fnmatchcase(k, pat)), sl["default_h"])
                if lm is not None and now - lm > lim * HOUR:
                    flags.append({"rule": "silent", "key": k, "value": None, "window": "silent %.1f h (limit %g h)" % (
                        (now - lm) / HOUR, lim), "detail": "last MEASURED %s; now %s: %s" % (
                        iso(lm), p.get("m"), (p.get("why") or "")[:160])})
        for name, check in (("band", band), ("run", run_rule), ("silent", silent)):
            try:
                if name not in off:
                    check()
            except Exception as e:  # noqa: BLE001  a bad rule costs that rule on this reading, not the others
                flags.append({"rule": "bad_rule", "key": k, "tag": name, "value": None, "window": "now",
                              "detail": "%s rule failed: %s: %s" % (name, type(e).__name__, str(e)[:160])})
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
                          "detail": "this rule is OFF until ops_watch_rules.json is fixed: " + why[:200]})
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
    import pulse_core as pc
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
        import pulse_core as pc
        if not pc._model().mint_problems(name, set()):
            return name
        # the key's tail made it too long or too many words for the namecheck, and mint_name would fail on it 20
        # times (OPS_FILER_FIX_ALARM_NAME_FAILS_GRAMMAR): the rule's own base, with a twist the key makes its own
        return "%s_%s" % (base, alarm_twist(base + "|" + key))
    return "%s_%s" % (base, alarm_twist(base))


def alarm_receiver_problem(conf):
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
        return inc.receiver_problem(conf.get("for"), conf.get("needs"))
    except Exception as e:     # noqa: BLE001 -- any failure to answer is reported, never swallowed
        return "receiver check failed: %s: %s" % (type(e).__name__, e)


RAISE_REASON = "alarm: first in relentless pool_order (ALARMS_REWIRE_OFF_RETIRED_BENCH)"


def expedite_of(tg, pt):
    """The fixer items an alarm hands to Relentless: the ids its point names in the target's `expedite_field` (OPS_CHURN_
    MEASURE_RETURNS_ARE_NOT_PROGRESS: STEVE_INCIDENT_UNCLAIMED came back 12 times as OPS_STEVE_UNSTICK_UNCLAIMED_*, each
    time one more item nobody claimed, while the steward's own STEVE_LANE_UNSTICK_* item sat unclaimed under it)."""
    f = (tg or {}).get("expedite_field")
    ids = ((pt or {}).get("x") or {}).get(f) if f else None
    ids = [ids] if isinstance(ids, str) else ids
    return [i for i in ids or [] if isinstance(i, str) and re.fullmatch(r"[A-Z][A-Z0-9_]+", i)][:3]


def expedite_owner(ids, conf, why):
    """-> {id: None | refusal}. `relentless.py expedite set <id> --level expedited --by Operations` from the filing clone,
    the escalation route the owner gave Operations (card 2026-11-03). Its own process, without a Relentless worker's
    environment (relentless_expedite.WORKER_ENV refuses those). A refusal costs that id only and is said, never raised."""
    out = {}
    env = {k: v for k, v in os.environ.items()
           if k not in ("RELENTLESS_GEN", "RELENTLESS_HELP_NONCE", "RELENTLESS_ROOT", "RELENTLESS_SUPERVISOR")}
    for i in ids:
        try:
            r = subprocess.run([sys.executable, str(Path(conf["clone"]) / "src/RimMandrake/rimflow/relentless.py"),
                                "expedite", "set", i, "--level", "expedited", "--by", "Operations", "--why", why[:300]],
                               capture_output=True, text=True, timeout=120, env=env)
            out[i] = None if r.returncode == 0 else ("exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[-200:]))
        except (OSError, subprocess.SubprocessError, KeyError) as e:
            out[i] = "%s: %s" % (type(e).__name__, str(e)[:200])
    return out


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


def real_filer(todo, conf):
    """todo: [{"name", "title"}] -> {name: None | error}, plus "_publish". Spawns as RUNNER from the dispatch clone
    under QHOME/ingest.lock and publishes its RUNNER shard (testq ingest.py does both). Nothing is filed for a
    receiver nobody picks up (alarm_receiver_problem), and every alarm it files or reopens is raised, so relentless
    pool_order takes it before unraised work."""
    import fcntl
    path = Path(conf["clone"]) / "src/RimMandrake/Utils/testq/ingest.py"
    spec = importlib.util.spec_from_file_location("ops_watch_ingest", str(path))
    ing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ing)
    nobody = alarm_receiver_problem(conf)     # only a NEW item needs it: a note or a reopen goes to one already filed
    res = {}
    with open(qhome() / "ingest.lock", "w") as lk:
        t0 = time.time()
        while True:
            try:
                fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() - t0 > conf["lock_wait_s"]:
                    return {a["name"]: "ingest.lock busy for %d s" % conf["lock_wait_s"] for a in todo}
                time.sleep(2)
        n = 0
        for a in todo:
            try:    # one alarm the spawn cannot carry (a NUL in an argument) costs itself, not the alarms behind it
                if a.get("note_only"):
                    rc, out = ing.rimflow("note", a["item"], "--text", a["text"])
                elif a.get("reopen"):     # a repeat: the same item goes back to work and the outage is counted
                    rc, out = ing.rimflow("live", a["name"], "--result", "broken", "--detail", a["title"][:300])
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
                                continue
                            break
                        if rc == 0:
                            res.setdefault("_renamed", {})[a["name"]] = new
                            a["name"] = new
                elif nobody:            # stays PENDING with the reason on its entry, retried every pass
                    rc, out = 1, "no receiver: " + nobody
                else:
                    rc, out = ing.rimflow("spawn", "--from", conf["parent"], "--for", conf["for"], "--needs", conf["needs"],
                                          "--name", a["name"], "--title", a["title"],
                                          "--why", "ops_watch alarm (deterministic, no AI): " + a["aid"])
                    if rc != 0 and already_filed(out, a["name"]):
                        # the filing clone's ledger holds it: an earlier pass filed it and this tree's ledger read lags
                        # (OPS_FILER_FIX_ALARM_NAME_FAILS_GRAMMAR). Filed, not failed; it was raised when it was filed
                        res[a["name"]] = None
                        res.setdefault("_already", []).append(a["name"])
                        continue
                if rc == 0 and a.get("expedite"):
                    res.setdefault("_expedite", {}).update(expedite_owner(a["expedite"], conf, "ops_watch alarm %s: "
                                                                          "nobody claimed it, Operations hands it to Relentless" % a.get("aid")))
                if rc == 0 and not a.get("note_only"):
                    rrc, rout = ing.rimflow("raise", a["name"], "--reason", RAISE_REASON)
                    if rrc != 0:    # filed but not first: the alarm stands (a retry would re-spawn), the miss is logged
                        res.setdefault("_raise", {})[a["name"]] = rout[-300:]
            except (ValueError, OSError) as e:
                rc, out = 1, "%s: %s" % (type(e).__name__, e)
            res[a["name"]] = None if rc == 0 else refusal_text(out)
            n += rc == 0
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
        log.append({"ts": iso(now), "event": "conductor_log_failed", "aid": aid, "error": str(e)[:200]})
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


def run_alarms(points, rules, now, known_ids, filer, open_ids=None, closed_at=None):
    """Edge-triggered: file once on a NEW crossing, keep it while it holds, re-arm when it clears. A target with note_field
    also says what is new while it stays crossed: a note on its open item, or, the item closed (open_ids), a reopen. So
    does an alarm that got worse (ALARM_REPEAT_FIX_BREAK_ON_WORSE: its severity rose, or its value passed the target's
    stated `worse` step), which also gives the Conductor a line and, through worse_n, Operations a fresh alarm run.
    closed_at ({item: [close epoch, ...]}, the flow collector's ctx["closes"]): a closed item is not reopened on a
    reading whose `night` predates its last close (NIGHTLY_COP_FIX_RED_ENVEHB_GOEW): that night ran before the fix."""
    p = ops_dir() / "alarms.json"
    state = read_json(p) if p.exists() else {}
    if not isinstance(state, dict):
        # the dedup state is there but unreadable: filing now could file every open alarm a second time. Hold all
        # filing (and leave the file for a human) until it reads again.
        return {"_alarm_state": {"state": "UNREADABLE", "error": "%s exists but is not a readable JSON object: alarm "
                                 "filing held this pass" % p}}
    log = []
    # before any step: a line owed from an earlier pass is retried even when this pass clears its alarm
    retry_conductor_lines(state, now, log)
    ts = target_state(points, rules)
    conf = alarm_conf(rules)
    todo = []
    said_causes = set()     # this pass's Conductor lines, one per cause (conductor_line_owed)
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
            if open_ids is not None and cur["name"] not in open_ids:
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
                lines = (["new at %s: %s%s" % (iso(now), "; ".join(map(str, shown))[:600],
                                               " (+%d more next pass)" % len(left) if left else "")] if fresh else []) + (
                    ["WORSE at %s: %s" % (iso(now), worse[0])] if worse else [])
                key = aid.split(":", 1)[1]
                tg = next((t for t in good_targets(rules) if t.get("alarm") and t["tag"] == aid.split(":", 1)[0]
                           and fnmatch.fnmatchcase(key, t["key"])), {})
                todo.append({"note_only": True, "item": cur["item"], "name": "note:" + aid, "aid": aid,
                             "expedite": expedite_of(tg, points.get(key)) if worse else [],
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
                             "expedite": cur.get("expedite") or []})
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
        if not cur.get("name"):  # mint once; a retry keeps the saved name
            taken = set(known_ids) | {a["name"] for a in state.values() if isinstance(a, dict) and isinstance(a.get("name"), str)}
            try:
                cur["name"] = mint_name(tag, taken, alarm_prefix(tg, tag, key, state, aid, pt))
                # the name is already on the ledger: a repeat of an alarm that filed before. It reopens that item.
                cur["reopen"] = cur["name"] in known_ids
            except Exception as e:  # noqa: BLE001  one unnameable alarm stays PENDING and counted (signal_watch tells); the pass goes on
                cur.update(error=str(e)[:200], tries=_tries(cur) + 1)
                log.append({"ts": iso(now), "event": "mint_failed", "aid": aid})
                return
        title = "Ops alarm %s: %s = %s %s(%s), line %s %g" % (tag, key, pt.get("v"), (pt.get("unit") or "") + " ",
                                                            pt.get("m"), tg["op"], tg["value"])
        said = (pt.get("x") or {}).get(tg["title_field"]) if tg.get("title_field") else None   # what crossed, first
        said = said[0] if isinstance(said, list) and said else said
        if isinstance(said, str) and said:
            title = "Ops alarm %s: %s -- %s" % (tag, said, title.split(": ", 1)[1])
        owners = expedite_of(tg, pt)
        if owners:      # the owner is named in the title, so the alarm item is never one more unclaimed item
            title = "%s; owner: Relentless, %s expedited by Operations" % (title, ", ".join(owners))
        cur["title"] = title[:160] if not owners else title[:300]
        cur["noted"] = titled_names(cur["title"], pt, tg)   # what the title shows is told; a name it cut, the first note says
        cur["expedite"] = owners
        cur["conductor_log"] = tg.get("conductor_log")     # a retry that files later still owes the Conductor its line
        todo.append({"aid": aid, "name": cur["name"], "title": cur["title"], "conductor_log": tg.get("conductor_log"),
                     "key": key, "reopen": bool(cur.get("reopen")), "expedite": owners})
    for aid in sorted(set(ts) | set(state)):
        try:
            one(aid)
        except Exception as e:  # noqa: BLE001  stays PENDING and counted, with the reason, and the pass goes on
            why = "alarm step raised %s: %s" % (type(e).__name__, str(e)[:200])
            cur = state.get(aid)
            cur = cur if isinstance(cur, dict) else state.setdefault(aid, {"state": "PENDING", "since": iso(now), "tries": 0})
            cur["error"] = why
            log.append({"ts": iso(now), "event": "step_failed", "aid": aid, "error": why})
    if todo and filer:
        atomic_json(p, state)   # the name is on disk before the spawn: a pass that dies mid-filing retries it, not a new one
    if todo:
        if filer:
            try:
                res = filer(todo, conf)
            except Exception as e:  # noqa: BLE001  a filing that raises stays PENDING; the pass still reports
                res = {a["name"]: "filer raised %s: %s" % (type(e).__name__, str(e)[:200]) for a in todo}
        else:
            res = {a["name"]: "filing off (run without --file-alarms)" for a in todo}
        for a in todo:
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
                cur["tries"] = _tries(cur) + (1 if filer else 0)
                cur["last_try"] = iso(now)
                if err is None:
                    cur.update(state="OPEN", item=a["name"], name=a["name"], error=None, filed=iso(now))   # name: a successor stays the alarm's item
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
                log.append({"ts": iso(now), "event": "step_failed", "aid": a["aid"], "error": str(e)[:200]})
    atomic_json(p, state)
    if log:
        with open(ops_dir() / "alarms_log.jsonl", "a", encoding="utf-8") as f:
            for r in log:
                f.write(json.dumps(r, sort_keys=True) + "\n")
    return state


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


def rl_headline(g):
    cause = g("relentless.cause").strip()
    return "relentless %s live, %s ready, under %s min, breaker %s min, %s checks waiting, tick %s s, blind %s%s" % (
        g("relentless.live").strip(), g("relentless.ready").strip(), g("relentless.under_min").strip(),
        g("relentless.breaker_open_min").strip(), g("relentless.checks_wait").strip(), g("relentless.tick_age_s").strip(),
        g("relentless.blind").strip(), "" if cause == "none" else ": " + cause)


def st_headline(g):
    cause = g("seats.cause").strip()
    return "seats idle with work %s min, tick %s s, blind %s%s" % (
        g("seats.idle_with_work_min").strip(), g("seats.tick_age_s").strip(), g("seats.blind").strip(),
        "" if cause == "none" else ": " + cause)


def plan_headline(g):
    cause = g("plan.cause").strip()
    return "plan list %s, age %s h, days since advance %s, blind %s%s" % (
        g("plan.list_state").strip(), g("plan.list_age_h").strip(), g("plan.days_since_advance").strip(),
        g("plan.blind").strip(), "" if cause == "none" else ": " + cause)


def headline(points, flags, alarms):
    def g(k):
        p = points.get(k) or {}
        return "%s %s" % (fmt(p.get("v")), "" if p.get("m") == "MEASURED" else "(%s)" % (p.get("m") or "absent"))
    accs = sorted({k.split(".")[1] for k in points if k.startswith("accounts.") and k.count(".") == 2
                   and not k.endswith("_collector")})
    parts = ["runway " + ", ".join("%s %s%s" % (a, g("accounts.%s.runway" % a).strip(), (
        " (loan %s)" % g("accounts.%s.loan_runway" % a).strip() if "accounts.%s.loan_runway" % a in points else ""))
        for a in accs)
             + ", codex " + g("codex.runway").strip()]
    parts.append("steve %s, INVALID streak %s, unowned stall %s min" % (
        g("steve.state").strip(), g("steve.invalid_streak").strip(), g("steve.unowned_stall_min").strip()))
    parts.append("disk free / %s GB, C: %s GB, D: %s GB, scratch %s GB, pool %s clones %s GB oldest %s h" % (
        g("disk.root_free_gb").strip(), g("disk.c_free_gb").strip(), g("disk.d_free_gb").strip(),
        g("disk.scratch_total_gb").strip(), g("disk.pool_clones").strip(), g("disk.pool_gb").strip(),
        g("disk.pool_oldest_h").strip()))
    parts.append(rl_headline(g))
    parts.append(st_headline(g))
    parts.append(plan_headline(g))
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
    L = ["# Ops watch %s (pass %.1f s)" % (dg["at"], dg["run_s"] or 0), "", dg["headline"], ""]
    al = {k: a for k, a in dg["alarms"].items()}
    if al:
        L.append("## Alarms")
        for k, a in sorted(al.items()):
            L.append("- %s %s since %s%s%s" % (a.get("state"), k, a.get("since"), " item %s" % a["item"] if a.get("item")
                                               else "", " error: " + str(a["error"])[:120] if a.get("error") else ""))
        L.append("")
    if dg["flags"]:
        L.append("## Open flags")
        for f in dg["flags"]:
            L.append("- %s %s [%s] %s (open since %s)" % (f["rule"] + ("/" + f["tag"] if f.get("tag") else ""), f["key"],
                                                          f["window"], f["detail"][:200], f.get("since", "now")))
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

# digest_blind.md is an ALLOW-LIST (review V, V1): a token-blind role (Producer, Arbiter, Auditor, Innovator) sees exactly these series
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
disk.pool_breach disk.pool_clones disk.pool_gb disk.pool_oldest_h
flow.closes_24h flow.lapsed_leases flow.untriaged_findings flow.verify_pass_24h
process.share_24h process.share_7d
production.A1 production.A2 production.A3 production.A4 production.A5
production.D1 production.D2 production.D3 production.D4
production.G1 production.G2 production.G3 production.G4 production.G5 production.G6 production.G7 production.G8
production.G9
production.O1 production.O2 production.O3 production.O4
production.P1 production.P2 production.P3 production.P4
production.V0 production.W1 production.W2 production.W3 production.W4 production.record_age_min
relentless.blind relentless.breaker_open_min relentless.cause relentless.checks_wait relentless.distressed relentless.live
relentless.no_live_min relentless.progress_age_min relentless.ready relentless.tick_age_s relentless.under_min
plan.blind plan.cause plan.days_since_advance plan.distressed plan.list_age_h plan.list_state
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
          rl_headline(g),
          st_headline(g),
          plan_headline(g),
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
                                                             f["key"], f.get("window"), str(f.get("detail"))[:200],
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


def publish_health(points, prev, ctx, rules, now):
    """Operations' one verdict (ops_health.py, health.json) from this pass's points and the series. -> its points:
    health.state, health.spent_slis (the OPS_ERROR_BUDGET_DIAGNOSE target) and health.drifted_slis. A failure is UNMEASURED and flagged;
    the old verdict then ages until Relentless reads it as stale."""
    import ops_health
    try:
        world = None
        if ctx.get("events") is not None:
            import pulse_core as pc
            world = pc._model().replay(ctx["events"])
        v = ops_health.publish(points, prev, world, rules, str(data_clone()), now,
                               stamp={"ledger": ops_health.ledger_mark(ctx.get("events"))})
    except Exception as e:  # noqa: BLE001  the pass outlives its verdict, and says so
        why = "health verdict not written: %s: %s" % (type(e).__name__, str(e)[:160])
        return {"health.state": U(why), "health.spent_slis": U(why), "health.drifted_slis": U(why),
                "health.incident_slis": U(why), "health.unmeasured": U(why)}
    x = {"spent": v["spent"], "system_items": len(v["system_items"] or []), "why": v["why"][:300]}
    guardless = v.get("recurring_unguarded")
    inc = v.get("incident") or {}
    if inc.get("bad") or (inc.get("slis") and len(inc.get("unmeasured") or ()) < len(inc["slis"])):
        inc_pt = M(len(inc["bad"]), "incident SLIs reading bad now", cause=inc["cause"][:300],
                   unmeasured=inc.get("unmeasured") or [])
    else:       # nothing to judge: no incident SLI, or none of them could see this pass
        inc_pt = U("no incident SLI measured this pass: %s" % (", ".join(inc.get("unmeasured") or ()) or "none configured"))
    return {"health.recurring_unguarded": U("no ledger or alarm log this pass") if guardless is None else M(
                len(guardless), "alarm kinds that came back with no class guard test", said=", ".join(r["kind"] for r in guardless[:5])),
            "health.incident_slis": inc_pt,
            "health.state": M(v["state"], None, **x),
            # the health rules are unusable: no budget was read (OPS_HEALTH_FIX_BROKEN_RULES_READ_HEALTHY); alarm REPAIR_ALARM
            "health.unmeasured": M(int(v["state"] == "unmeasured"), "health verdicts with unusable rules",
                                   said=v["why"][:300] if v["state"] == "unmeasured" else ""), "health.spent_slis": M(len(v["spent"]), "SLIs with a spent budget", **x),
            "health.drifted_slis": M(len(v["drifted"]), "SLIs whose point changed unit under them", said=", ".join(v["drifted"]))}


def steve_release():
    """Operations' deterministic hand on the Steve lane: testq/brake_release.py, its own process so its import of testq
    reads TESTQ_QUEUE as this pass does. -> flags: it costs a flag when it fails, never the pass."""
    why = None
    try:
        r = subprocess.run([sys.executable, str(HERE / "testq" / "brake_release.py")], capture_output=True, text=True,
                           timeout=240)
        if r.returncode != 0:
            why = "exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[-200:])
    except (OSError, subprocess.SubprocessError) as e:
        why = "%s: %s" % (type(e).__name__, str(e)[:200])
    return [{"rule": "brake_release", "key": "steve.brake_release", "value": None, "window": "now",
             "detail": "the brake release pass failed: " + why}] if why else []


OLD_TIMER = "rm-ops-watch.timer"     # the clock the metronome's sense phase replaces (metronome_phases.json owns)
SENSE_PHASE = "sense"
EXIT_FENCED = 3
COMPOSE_MAX_AGE_S = 1000.0   # a carried family reading older than this reads UNMEASURED (rules: compose_max_age_s):
                             # ~1.5 rounds of the sense round robin (21 families, 2 a beat, 60 s beats)
COMPOSE_NEEDS_FLOW = ("testing",)   # collectors that read the flow collector's ctx (closes, open_ids): flow joins them
COMPOSE_ALARM_FAMILY = "flow"  # a compose pass files alarms only when it measures this family (its ctx: the ledger ids)


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


def carry_family(fam, recs, now, max_age):
    """The points of family `fam`'s last series record, for a compose pass that did not measure it this beat: each
    carries observed_at (its record's time). None recorded, or older than max_age, reads UNMEASURED, never as now."""
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
    out = {k: U(why, p.get("unit") if isinstance(p, dict) else None) for k, p in (last or {}).get("points", {}).items()
           if not k.endswith("._collector")}
    out["%s._collector" % fam] = U(why)
    return out



def held_health(now, max_age):
    """The health.* points of the last status a compose alarm pass wrote (each with observed_at), for a compose pass
    without the ledger; None when there is none within max_age, so that pass computes its own verdict."""
    st = _obj(read_json(ops_dir() / "status.json"))
    pts, t = st.get("points"), st.get("t")
    if not isinstance(pts, dict) or not is_num(t) or not 0 <= now - t <= max_age:
        return None
    hs = pts.get("health.state")
    obs = ((hs.get("x") or {}).get("observed_at") if isinstance(hs, dict) else None) or st.get("at") or iso(t)
    try:
        seen = epoch(obs)       # a verdict carried pass after pass ages from the pass that made it
    except (TypeError, ValueError, OverflowError):
        return None
    if not is_num(seen) or not 0 <= now - seen <= max_age:
        return None
    out = {}
    for k, p in pts.items():
        if k.startswith("health.") and isinstance(p, dict):
            out[k] = dict(p, x=dict(p.get("x") or {}, observed_at=obs))
    return out if out.get("health.state", {}).get("m") == "MEASURED" else None


@_locked
def run(now=None, rules=None, filer=None, families=None, compose=False, still_owner=None):
    """One pass. `families` limits it to those collectors. With `compose` (the metronome's sense phase, a family or two
    a beat, round robin) every other family's last series record is carried in (carry_family), so the status, health
    verdict, digest and flags are a whole pass's; the alarms run, over that composite, only on the pass that measures
    COMPOSE_ALARM_FAMILY, about once a round. `still_owner(what)` (the metronome's ownership fence) is asked before the
    series are written, before the alarms and before the status: False raises Fenced."""
    def fence(what):
        if still_owner is not None and not still_owner(what):
            raise Fenced("fenced before %s" % what)
    compose = bool(compose and families)
    if compose and COMPOSE_ALARM_FAMILY not in families and any(f in families for f in COMPOSE_NEEDS_FLOW):
        families = [COMPOSE_ALARM_FAMILY] + list(families)
    whole = not families or compose
    now = now or time.time()
    rules = rules or load_rules()
    t0 = time.time()
    ctx = {"no_reruns": True} if compose else {}
    points = {}
    since = now - rules.get("series_days", 8) * DAY
    prev = {}
    sick = []
    unfit = []
    for fam in ORDER:
        if families and fam not in families:
            continue
        old = read_series(fam, since)
        prev[fam] = old
        try:
            pts = COLLECTORS[fam](now, rules, ctx)
        except Exception as e:  # noqa: BLE001  an instrument that errors is UNMEASURED, never 0
            why = "collector error: %s: %s" % (type(e).__name__, str(e)[:200])
            last = old[-1]["points"] if old else {}
            pts = {k: U(why, p.get("unit") if isinstance(p, dict) else None) for k, p in last.items()
                   if not k.endswith("._collector")}
            pts["%s._collector" % fam] = U(why)
        unfit += stamp_ranges(pts, rules)
        rec = {"schema": SCHEMA, "t": now, "at": iso(now), "family": fam, "points": pts}
        if fam == "production" and ctx.get("production_src_t"):
            rec["src_t"] = ctx["production_src_t"]
        dup = fam == "production" and old and old[-1].get("src_t") and old[-1].get("src_t") == rec.get("src_t")
        if not dup:
            fence("writing the %s series" % fam)
            try:
                append(fam, rec)
            except Exception as e:  # noqa: BLE001  the pass and the alarms outlive a series that cannot be written
                sick.append({"rule": "series_write", "key": "%s._series" % fam, "value": None, "window": "now",
                             "detail": "this pass's %s points were not kept: %s: %s" % (fam, type(e).__name__, str(e)[:160])})
        points.update(pts)
    try:
        max_age = float(rules.get("compose_max_age_s", COMPOSE_MAX_AGE_S))
    except (TypeError, ValueError):
        max_age = COMPOSE_MAX_AGE_S
    if compose:
        carried = {}
        for fam in ORDER:
            if fam in families:
                continue
            prev[fam] = read_series(fam, since)
            carried.update(carry_family(fam, prev[fam], now, max_age))
        points = dict(carried, **points)        # this pass's own readings win
    if filer is real_filer and (not families or "steve" in families):      # acts only where alarms are really filed
        fence("the steve release")
        sick += steve_release()
    for fam, key in (("relentless", "relentless.blind"), ("seats", "seats.blind"), ("plan", "plan.blind"),
                     ("disk", "disk.scratch_outside_blind")):
        if (whole or fam in families) and not counts_as_measured(points.get(key)):
            points[key] = st_suppressed(points, fam)
            stamp_ranges(points, rules)
    health_flag = None
    if compose and COMPOSE_ALARM_FAMILY not in families:
        # the verdict needs the ledger, which only the alarm pass reads: carry that pass's, never make one without it
        points.update(held_health(now, max_age) or {"health.state": U(
            "the health verdict is made on the beat that measures %s; none within %d min" % (
                COMPOSE_ALARM_FAMILY, max_age / 60))})
    elif whole:      # a limited pass has not measured every SLI: it never overwrites the verdict
        points.update(publish_health(points, prev, ctx, rules, now))
        if points["health.state"].get("m") != "MEASURED":
            health_flag = {"rule": "health", "key": "health.state", "value": None, "window": "now",
                           "detail": "NO HEALTH VERDICT this pass: %s" % points["health.state"].get("why")}
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
                         "detail": "andon failed: %s: %s" % (type(e).__name__, str(e)[:160])}]
    if health_flag:
        flags.append(health_flag)
    if rules.get("_load_error"):
        flags.append({"rule": "bad_rule", "key": "rules.file", "value": None, "window": "now",
                      "detail": "the rules file cannot be read, last good copy in use: %s" % rules["_load_error"]})
    # a collector down longer than the series window has no old keys left to go silent: this flag is what still says so
    flags += [{"rule": "collector", "key": k, "value": None, "window": "now", "detail": str(p.get("why"))[:200]}
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
                      "detail": "last_measured.json not written: %s" % str(e)[:160]})
    try:
        if compose and COMPOSE_ALARM_FAMILY not in families:
            alarms = _obj(read_json(ops_dir() / "alarms.json"))       # held: this beat's pass is not the alarm pass
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
                    def afiler(todo, conf, _f=filer):
                        fence("filing")
                        return _f(todo, conf)
            alarms = run_alarms(apts, rules, now, ctx.get("known_ids") or set(), afiler, ctx.get("open_ids"),
                                ctx.get("closes"))
            if compose:
                atomic_json(ap, {"t": now, "at": iso(now)})
    except Fenced:
        raise
    except Exception as e:  # noqa: BLE001  the digest still goes out, and says the alarms did not run
        alarms = _obj(read_json(ops_dir() / "alarms.json"))
        flags.append({"rule": "bad_rule", "key": "alarms", "value": None, "window": "now",
                      "detail": "NO ALARM RAN this pass: %s: %s" % (type(e).__name__, str(e)[:160])})
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
        full = "# ops_watch digest failed to render\n\n%s: %s\n\n%s\n" % (type(e).__name__, str(e)[:200], dg.get("headline"))
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


# =================================================================================================== install
UNIT = """# rm-ops-watch: ops_watch.py, the Dispatcher's deterministic measurement arm for Operations
# (V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE; listed in src/RimMandrake/rimflow/dispatcher_schedule.json "measure").
# Runs from the one Operations deploy (src/RimMandrake/Utils/systemd/ops_clocks.json). No AI.
[Unit]
Description=Ops watch (accounts, Codex, Steve lane, disk, timers, KPIs; Andon flags; alarms)

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {deploy}/src/RimMandrake/Utils/ops_watch.py run --file-alarms
# ops_memory reads this pass back from VictoriaMetrics once telemetryd has ingested it; "-": its failure never fails
# the pass (a missing or blind generation is what ops_memory.py check reports)
ExecStartPost=-/usr/bin/python3 {deploy}/src/RimMandrake/Utils/ops_memory.py build --wait-ingest 120
TimeoutStartSec=420s
Nice=10
"""
TIMER = """[Unit]
Description=Ops watch every 15 min

[Timer]
OnCalendar=*:07/15
Persistent=true

[Install]
WantedBy=timers.target
"""


def install(apply, deploy):
    d = Path.home() / ".config/systemd/user"
    files = {d / "rm-ops-watch.service": UNIT.format(deploy=deploy), d / "rm-ops-watch.timer": TIMER}
    for p, body in files.items():
        old = p.read_text() if p.exists() else None
        print(("unchanged " if old == body else "write ") + str(p))
        if apply and old != body:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)
    if apply:
        for cmd in (["daemon-reload"], ["enable", "--now", "rm-ops-watch.timer"]):
            r = subprocess.run(["systemctl", "--user"] + cmd, capture_output=True, text=True, timeout=60)
            print("systemctl --user %s: exit %d %s" % (" ".join(cmd), r.returncode, r.stderr.strip()))
            if r.returncode:
                return 1
    else:
        print("plan only: pass --apply to write and enable")
    return 0


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
    sub.add_parser("rerun-reds", help="rerun the night's new red groups at origin/main (out of the metronome's beat)")
    ln = sub.add_parser("lint", help="refuse a ranges block with a metric short of owner, class, age, ack or why")
    ln.add_argument("--rules", help="the rules file, default the shipped one")
    i = sub.add_parser("install")
    i.add_argument("--apply", action="store_true")
    i.add_argument("--deploy", default=__import__("ops_clocks").deploy(),
                   help="the one Operations deploy (systemd/ops_clocks.json)")
    a = ap.parse_args(argv)
    if a.cmd == "run":
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
        try:
            dg = run(filer=real_filer if a.file_alarms else None, families=a.family, compose=a.compose,
                     still_owner=still_owner)
        except Busy as e:
            print("skipped: %s" % e)
            return 0
        except Fenced as e:
            print("ops_watch: %s" % e)
            return EXIT_FENCED
        print(dg["headline"])
        return 0
    if a.cmd == "lint":
        problems = ranges_problems(json.loads(Path(a.rules or rules_path()).read_text(encoding="utf-8")))
        print("\n".join("REFUSED: " + p for p in problems) or "ranges clean")
        return 1 if problems else 0
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
    return install(a.apply, a.deploy)


if __name__ == "__main__":
    sys.exit(main())
