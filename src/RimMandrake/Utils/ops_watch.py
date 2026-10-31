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
             steve       testq steward.json / steward_watch.json / done/*.json: state, fault, heartbeat, INVALID streak
             testing     testq done jobs (Steve lane, per job) + testing_metrics history (archmagi, per day):
                         busy hours on runs that caught nothing (no FAIL, no finding, no close within 24 h)
             disk        free GB on / (WSL ext4), C:, D:; D: used GB (agent storage growth); scratch under the reaper
                         (the last line of rm-scratch-reap's runs.jsonl, written hourly: no 160 s dry run here)
             timers      systemctl --user: failed units, timers overdue
             flow        the rimflow ledger (pulse_core.read_ledger, the union of clones): untriaged findings,
                         closes and verify passes in 24 h, lapsed leases
             process     process-commit share (git log, the resp_register PROC regex) over 24 h and 7 d
             tps         tps_record.py --json: tick ratio, stalls, coverage
             production  every RimPulse stream measure (rm-pulse-streams' series.jsonl, reused, not recomputed)
             v3          the section 6 success metrics no instrument measures yet, UNMEASURED with the reason
   STORE   append-only JSONL, one file per family: $RM_OPS_WATCH_DIR/series/<family>.jsonl (default
           D:\\ClaudeWork\\rimmandrake\\ops_watch). Every point is {v, m: MEASURED|ESTIMATE|UNMEASURED, why?, unit?}.
           An instrument that errors writes UNMEASURED with the error, never 0.
   FLAG    Andon rules from ops_watch_rules.json over MEASURED points: band (outside the 7-day mean +/- 3 sigma),
           run (n same-direction changes), silent (a series that stopped being MEASURED), target (a line crossed).
           Each flag names the series and the window. flags.json keeps when each flag first opened.
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
    python3 src/RimMandrake/Utils/ops_watch.py digest                 print digest.md
    python3 src/RimMandrake/Utils/ops_watch.py backfill               seed production from rm-pulse-streams' history
    python3 src/RimMandrake/Utils/ops_watch.py install [--apply]      the systemd user timer (plan unless --apply)
"""
import argparse
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
            "evidence", "companion", "arena")


def ops_dir() -> Path:
    return Path(os.environ.get("RM_OPS_WATCH_DIR", "/mnt/d/ClaudeWork/rimmandrake/ops_watch"))


def rules_path() -> Path:
    return Path(os.environ.get("RM_OPS_WATCH_RULES", HERE / "ops_watch_rules.json"))


def qhome() -> Path:
    return Path(os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq"))


def data_clone() -> Path:
    return Path(os.environ.get("RM_STREAMS_BENCH", "/home/mandrake/rm/bench"))


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


# ================================================================================================== collectors
def c_accounts(now, rules, ctx):
    import account_usage as AU
    import slot_allocator as SA
    out = {}
    acc = (AU.read_now(now).get("accounts") or {})
    if not acc:
        return {"accounts._collector": U("account_usage.read_now() returned no account")}
    fit = {"fit": rules["accounts_fit"]}
    def account(name, a):
        src = a.get("source") or "UNMEASURED"
        if a.get("stale"):
            src = "ESTIMATE" if src == "MEASURED" else src
        left, h = a.get("week_pct_left"), a.get("hours_to_week_reset")
        k = "accounts.%s." % name
        if src not in ("MEASURED", "ESTIMATE") or left is None:
            why = "account_usage: %s" % (a.get("why") or src)
            for f in ("week_left_pct", "hours_to_reset", "runway"):
                out[k + f] = U(why)
            return
        mk = (lambda v, u, **x: M(v, u, **x)) if src == "MEASURED" else \
            (lambda v, u, **x: E(v, "account_usage reading is an ESTIMATE%s" % (" (stale)" if a.get("stale") else ""), u, **x))
        out[k + "week_left_pct"] = mk(left, "% of the weekly quota left", measured_at=a.get("measured_at"))
        out[k + "hours_to_reset"] = mk(h, "h to the weekly reset") if h is not None else U("no reset time")
        rate, how = None, None
        if src == "MEASURED":
            r, n, span = SA.slope(name, a.get("week_resets_at"), now, fit)
            if r is not None:
                rate, how = r, "meter slope, %d readings over %.1f h" % (n, span)
        if rate is None:
            rate, how = week_avg_rate(a.get("week_pct_used"), h)
        rw = runway(left, rate, h)
        if rw is None:
            out[k + "runway"] = U("no burn rate: no week figure or reset time, and the meter has no slope")
        elif rate is None:      # spent before any rate exists: 0 is as certain as the reading
            out[k + "runway"] = (M(0.0, "x the time to reset", why="quota spent") if src == "MEASURED" else
                                 E(0.0, "quota spent per an ESTIMATE reading", "x the time to reset"))
        elif src == "MEASURED" and how and how.startswith("meter"):
            out[k + "runway"] = M(rw, "x the time to reset", rate_pct_h=round(rate, 3), rate_from=how)
        else:
            out[k + "runway"] = E(rw, "rate from %s%s" % (how, "" if src == "MEASURED" else "; the reading is an ESTIMATE"),
                                  "x the time to reset", rate_pct_h=round(rate, 3))
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
    recs, nfiles = CX.readings(dirs, newer_than=now - cr["lookback_days"] * DAY)
    week, bad = [], []      # bad: the time of each record that cannot be used; None when not even that reads
    for r in recs:      # (ts, p_used, p_win, p_reset, s_used, s_win, s_reset, plan)
        try:
            if r[2] == 10080:
                week.append((epoch(r[0]), float(r[1]), epoch(r[3])))
            elif r[5] == 10080 and r[4] is not None:
                week.append((epoch(r[0]), float(r[4]), epoch(r[6])))
        except (TypeError, ValueError, OverflowError, IndexError, KeyError):
            try:        # one bad record costs itself; a good one still reads, marked if the bad one is the newer
                bad.append(epoch(r[0]))
            except (TypeError, IndexError, KeyError):
                bad.append(None)
    bad += [w[0] for w in week if w[0] is None or w[2] is None or not finite(w[1]) or w[0] > now + 300]
    week = sorted(w for w in week if w[0] is not None and w[2] is not None and finite(w[1]) and w[0] <= now + 300)
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
    same = [(a, b) for a, b, c in week if abs(c - reset) < HOUR and a >= now - cr["slope_window_h"] * HOUR]
    rate, how = None, None
    if len(same) >= 2 and (same[-1][0] - same[0][0]) / HOUR >= cr["slope_min_span_h"]:
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
        out["codex.runway"] = E(rw, "rate from " + how, "x the time to reset", rate_pct_h=round(rate, 3))
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
        if hb > 30 and (wage is None or wage > 30) and not wj.get("incident"):
            nobody.append(("steward silent %.0f min and its watcher silent %s" % (
                hb, "(never ran)" if wage is None else "%.0f min" % wage), hb))
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
    if closes is None:
        return {"testing.nothing_h_7d": U("the ledger was not readable, so closes after a run are unknown")}
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
    days = {}
    try:
        with open(hist, encoding="utf-8") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if isinstance(r, dict) and isinstance(r.get("day"), str):
                    days[r["day"]] = r          # the last record of each day wins
    except OSError:
        days = {}
    lo = time.strftime("%Y-%m-%d", time.localtime(now - 7 * DAY))
    ah, adays, blind, soft = 0.0, 0, 0, 0
    for day, r in sorted(days.items()):
        if not day or day <= lo or not isinstance(r, dict):
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
        if not all(isinstance(vals[k], (int, float)) and not isinstance(vals[k], bool) for k in ("busy_pct", "window_h")):
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
        return dict(kv.split("=", 1) for kv in env.split(","))
    return {"root": "/", "c": "/mnt/c", "d": "/mnt/d"}


def c_disk(now, rules, ctx):
    out = {}
    for name, mnt in disk_mounts().items():
        try:
            if mnt.startswith("/mnt/") and not os.path.ismount(mnt):
                raise OSError("not a mount point (the drive is not mounted; df would read the parent volume)")
            du = shutil.disk_usage(mnt)
            if du.total <= 0:
                raise OSError("total 0")
            out["disk.%s_free_gb" % name] = M(round(du.free / 1e9, 1), "GB free on %s" % mnt,
                                             total_gb=round(du.total / 1e9, 1))
            out["disk.%s_used_gb" % name] = M(round(du.used / 1e9, 1), "GB used on %s" % mnt)
        except OSError as e:
            out["disk.%s_free_gb" % name] = U("%s: %s" % (mnt, e))
            out["disk.%s_used_gb" % name] = U("%s: %s" % (mnt, e))
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
            if not isinstance(row, dict):
                nob += 1
                continue
            if row.get("verdict") != "DELETED":
                if not isinstance(row.get("bytes"), (int, float)):
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
    return out


def systemctl_json(*args):
    r = subprocess.run(["systemctl", "--user"] + list(args) + ["-o", "json", "--no-pager"], capture_output=True,
                       text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError("systemctl %s: exit %d %s" % (" ".join(args), r.returncode, r.stderr.strip()[-200:]))
    return json.loads(r.stdout or "[]")


def c_timers(now, rules, ctx):
    out = {}
    try:                # two sources: neither one's failure takes the other's reading
        failed = systemctl_json("list-units", "--failed", "--all")
        names = sorted(str(u.get("unit") if isinstance(u, dict) else u) for u in failed)
        out["timers.failed_units"] = M(len(names), "failed user units", units=names[:12])
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


def c_flow(now, rules, ctx):
    import pulse_core as pc
    model = pc._model()
    events = pc.read_ledger()
    ctx["events"] = events
    world = model.replay(events)
    ctx["known_ids"] = set(world.items)
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
    untr = sorted(n for n, f in world.findings.items() if f.get("type") == "UNTRIAGED" and n not in world.items)
    out = {"flow.untriaged_findings": M(len(untr), "findings UNTRIAGED, not yet items", first=untr[:5]),
           "flow.closes_24h": M(len(c24), "items closed, 24 h"),
           "flow.verify_pass_24h": M(v24, "verify pass events, 24 h (maker or not)")}
    lapsed = sum(1 for it in world.items.values() if it.open and model.lease_status(it, now) == "lapsed")
    out["flow.lapsed_leases"] = M(lapsed, "open items with a lapsed lease")
    try:
        out["steve.incident_unclaimed_min"] = steve_incident_unclaimed(world, model, now, rules)
    except Exception as e:  # noqa: BLE001  a bad steve_incident rule costs this reading, not the family's
        out["steve.incident_unclaimed_min"] = U("steve_incident: %s: %s" % (type(e).__name__, str(e)[:160]))
    return out


def steve_incident_unclaimed(world, model, now, rules):
    """steve.incident_unclaimed_min: the age of the OLDEST open steward incident item (id prefix
    rules steve_incident.prefix) that no seat holds: still proposed/ready (not doing/built/validated) (claim/start), no live lease, not blocked. The steward
    escalating a stall makes c_steve call it owned; this is the point that says nobody has picked the escalation up
    (owner 2026-10-28: the lane sat paused 21 min with an open STEVE_LANE_UNSTICK item and no alarm)."""
    pre = (rules.get("steve_incident") or {}).get("prefix", "STEVE_LANE_UNSTICK_")
    ages, names = [], []
    for it in world.items.values():
        if not it.id.startswith(pre) or it.state not in ("proposed", "ready") or it.blocked:
            continue
        if model.lease_status(it, now) == "live":
            continue
        t = model.epoch(it.created_at)
        if t is None:
            return U("incident %s has no readable creation time" % it.id)
        ages.append(max(0.0, (now - t) / 60.0))
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
    return out


def c_tps(now, rules, ctx):
    r = subprocess.run([sys.executable, str(HERE / "tps_record.py"), "--json"], capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        raise RuntimeError("tps_record.py exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[-200:]))
    s = (json.loads(r.stdout) or {}).get("summary") or {}
    out = {}
    if s.get("coverage") != "FRESH":
        why = "no fresh TPS session (coverage %s): the game is not running or the recorder is off" % s.get("coverage")
        return {k: U(why) for k in ("tps.ratio_median", "tps.stalls", "tps.stall_max_s")}
    rm = s.get("ratioMedian")
    out["tps.ratio_median"] = M(rm, "tick ratio to target, median", speed=s.get("speed"), run=s.get("run")) \
        if rm is not None else U("fresh session but no run window (paused or stalled the whole time)")
    out["tps.stalls"] = M(s.get("stalls"), "stalls in the window", samples=s.get("samples")) \
        if s.get("stalls") is not None else U("tps_record gave no stall count")
    out["tps.stall_max_s"] = M(s.get("stallMaxS"), "longest stall s") if s.get("stallMaxS") is not None else \
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
    out = {"production.record_age_min": M(round(age, 1), "min since rm-pulse-streams' last record")}
    stale = age > 60
    for k, p in sorted((rec.get("measures") or {}).items()):
        if not isinstance(p, dict):
            out["production." + k] = U("malformed measure in the streams record (%s)" % type(p).__name__)
            continue
        if stale:
            out["production." + k] = U("the streams record is %.0f min old (rm-pulse-streams stopped?)" % age)
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


COLLECTORS = {"accounts": c_accounts, "codex": c_codex, "steve": c_steve, "flow": c_flow, "testing": c_testing,
              "disk": c_disk, "timers": c_timers, "process": c_process, "tps": c_tps, "production": c_production,
              "v3": c_v3, "tokentalk": c_tokentalk, "evidence": c_evidence, "companion": c_companion,
              "arena": c_arena}
ORDER = ("accounts", "codex", "steve", "flow", "testing", "disk", "timers", "process", "tps", "production", "v3", "tokentalk",
         "evidence", "companion", "arena")


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
    return None


def good_targets(rules):
    rows = rules.get("targets")
    return [t for t in rows if not target_problem(t)] if isinstance(rows, list) else []


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
            if not meas and matches(k, sl["keys"]) and not matches(k, sl["skip"]):
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
            if v is None or p.get("m") not in marks:
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
            new = None if (v is None or p.get("m") not in marks) else bool(_cmp(v, tg["op"], tg["value"]))
            # two targets on one id: a crossing wins, then a hold; the later row never hides an earlier crossing
            old = st.get(aid, False)
            st[aid] = True if True in (old, new) else None if (old is None or new is None) else False
    return st


# ===================================================================================================== alarms
# Filing writes alarms.json first, on purpose: a name saved before the filing is what stops a repeat. On a full state
# disk that write raises, no alarm files, and the pass dies with the unit failed. DISK_LOW fires at 210 GB, well before.
def alarm_conf(rules):
    a = dict(rules["alarm"])
    a["clone"] = os.environ.get("RM_OPS_ALARM_CLONE", a["clone"])
    a["parent"] = os.environ.get("RM_OPS_ALARM_PARENT", a["parent"])
    return a


def mint_name(tag, known, prefix):
    import secrets
    import pulse_core as pc
    model = pc._model()
    for _ in range(20):
        name = "%s_%s" % (prefix, secrets.token_hex(2).upper())
        if not model.mint_problems(name, known):
            return name
    raise RuntimeError("no mintable alarm name for " + tag)


def real_filer(todo, conf):
    """todo: [{"name", "title"}] -> {name: None | error}, plus "_publish". Spawns as RUNNER from the dispatch clone
    under QHOME/ingest.lock and publishes its RUNNER shard (testq ingest.py does both)."""
    import fcntl
    path = Path(conf["clone"]) / "src/RimMandrake/Utils/testq/ingest.py"
    spec = importlib.util.spec_from_file_location("ops_watch_ingest", str(path))
    ing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ing)
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
            if a.get("note_only"):
                rc, out = ing.rimflow("note", a["item"], "--text", a["text"])
            else:
                rc, out = ing.rimflow("spawn", "--from", conf["parent"], "--for", conf["for"], "--needs", conf["needs"],
                                      "--name", a["name"], "--title", a["title"],
                                      "--why", "ops_watch alarm (deterministic, no AI): " + a["aid"])
            res[a["name"]] = None if rc == 0 else out[-300:]
            n += rc == 0
        res["_publish"] = ing.publish(n, message="ledger: ops_watch alarm(s) %s" % ", ".join(
            a["name"] for a in todo if res.get(a["name"]) is None)) if n else "nothing to publish"
    return res


def is_token_key(key):
    """Is this KPI key a token, runway, quota or burn reading (Operations' alone)?"""
    return str(key).split(".", 1)[0] in TOKEN_FAMILIES


def token_alarm_title(aid):
    """An Operations-only alarm's title: its tag and family, never a key's account, value or line (review V, V2)."""
    tag, key = (aid.split(":", 1) + [""])[:2]
    return "Ops alarm for Operations: %s on %s; the reading is in digest.md" % (tag, key.split(".", 1)[0])


def _tries(cur):
    """A saved retry count, or 0 for one that cannot be counted from: never a raise after the filing succeeded."""
    n = cur.get("tries", 0)
    return n if isinstance(n, int) and not isinstance(n, bool) else 0


def run_alarms(points, rules, now, known_ids, filer):
    """Edge-triggered: file once on a NEW crossing, keep it while it holds, re-arm when it clears."""
    p = ops_dir() / "alarms.json"
    state = read_json(p) if p.exists() else {}
    if not isinstance(state, dict):
        # the dedup state is there but unreadable: filing now could file every open alarm a second time. Hold all
        # filing (and leave the file for a human) until it reads again.
        return {"_alarm_state": {"state": "UNREADABLE", "error": "%s exists but is not a readable JSON object: alarm "
                                 "filing held this pass" % p}}
    log = []
    ts = target_state(points, rules)
    conf = alarm_conf(rules)
    todo = []
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
        if cur and cur.get("state") == "PENDING" and cur.get("name") in known_ids:
            # filed by a pass that died before saving its state: the ledger has it, never file it twice
            cur.update(state="OPEN", item=cur["name"], error=None, filed=cur.get("filed") or iso(now))
            log.append({"ts": iso(now), "event": "found_filed", "aid": aid, "item": cur["name"]})
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
            return
        if not crossed:
            if cur and cur.get("name") and cur.get("title"):
                # PENDING, not crossed now (UNMEASURED, or clear but not for clear_passes yet): the crossing was
                # real, so keep retrying the filing under the name and title it got when it crossed
                todo.append({"aid": aid, "name": cur["name"], "title": cur["title"]})
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
                cur["name"] = mint_name(tag, taken, tg.get("name") or "OPS_ALARM_DIAGNOSE")
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
        cur["title"] = title[:160]
        todo.append({"aid": aid, "name": cur["name"], "title": cur["title"]})
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
                continue
            try:
                cur = state[a["aid"]]
                err = res.get(a["name"])
                cur["tries"] = _tries(cur) + (1 if filer else 0)
                cur["last_try"] = iso(now)
                if err is None:
                    cur.update(state="OPEN", item=a["name"], error=None, filed=iso(now))
                    # the item is in the RUNNER shard whatever _publish says: a publish that failed is retried by the
                    # next testq ingest (testq/ingest.py _publish keeps the lines), so OPEN is right either way
                    log.append({"ts": iso(now), "event": "filed", "aid": a["aid"], "item": a["name"],
                                "publish": res.get("_publish")})
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


def headline(points, flags, alarms):
    def g(k):
        p = points.get(k) or {}
        return "%s %s" % (fmt(p.get("v")), "" if p.get("m") == "MEASURED" else "(%s)" % (p.get("m") or "absent"))
    accs = sorted({k.split(".")[1] for k in points if k.startswith("accounts.") and k.count(".") == 2
                   and not k.endswith("_collector")})
    parts = ["runway " + ", ".join("%s %s" % (a, g("accounts.%s.runway" % a).strip()) for a in accs)
             + ", codex " + g("codex.runway").strip()]
    parts.append("steve %s, INVALID streak %s, unowned stall %s min" % (
        g("steve.state").strip(), g("steve.invalid_streak").strip(), g("steve.unowned_stall_min").strip()))
    parts.append("disk free / %s GB, C: %s GB, D: %s GB, scratch %s GB" % (
        g("disk.root_free_gb").strip(), g("disk.c_free_gb").strip(), g("disk.d_free_gb").strip(),
        g("disk.scratch_total_gb").strip()))
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
            L += ["## " + f, "key | now | mark | d24h | d7d | n7d | flags", "---|---|---|---|---|---|---"]
        L.append("%s | %s | %s | %s | %s | %d | %s" % (
            k.split(".", 1)[1], fmt(r["v"]) + (" " + r["unit"] if r.get("unit") and len(r["unit"]) < 40 else ""),
            r["m"] if r["m"] == "MEASURED" else "%s: %s" % (r["m"], (r.get("why") or "")[:90]),
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
disk.scratch_refused_gb disk.scratch_total_gb
flow.closes_24h flow.lapsed_leases flow.untriaged_findings flow.verify_pass_24h
process.share_24h process.share_7d
production.A1 production.A2 production.A3 production.A4 production.A5
production.D1 production.D2 production.D3 production.D4
production.G1 production.G2 production.G3 production.G4 production.G5 production.G6 production.G7 production.G8
production.G9
production.O1 production.O2 production.O3 production.O4
production.P1 production.P2 production.P3 production.P4
production.V0 production.W1 production.W2 production.W3 production.W4 production.record_age_min
steve.fault_min steve.heartbeat_age_min steve.invalid_24h steve.invalid_streak steve.jobs_24h steve.last_done_age_min
steve.state steve.unowned_stall_min steve.watch_age_min
testing.archmagi_nothing_h_7d testing.nothing_h_7d testing.steve_nothing_h_7d
timers.failed_units timers.overdue_timers
tps.ratio_median tps.stall_max_s tps.stalls
v3.accepted_per_day v3.failure_signal_share v3.keep_going_per_day
""".split())
# the fields of an allowed point a blind role may see: value, mark, unit, the why of a non-MEASURED mark, the 24 h /
# 7 d change. Never d24/d7 of a withheld key, never the full digest's headline (it names runway).
BLIND_FIELDS = ("v", "m", "unit", "why", "d24", "d7")


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
          "disk free / %s GB, C: %s GB, D: %s GB, scratch %s GB" % (
              g("disk.root_free_gb"), g("disk.c_free_gb"), g("disk.d_free_gb"), g("disk.scratch_total_gb")),
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
            body += ["## " + f, "key | now | mark | d24h | d7d", "---|---|---|---|---"]
        body.append("%s | %s | %s | %s | %s" % (
            k.split(".", 1)[1], fmt(r["v"]) + (" " + r["unit"] if r.get("unit") and len(r["unit"]) < 40 else ""),
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
        if isinstance(p, dict) and p.get("m") == "MEASURED" and num(p) is not None:
            keep[k] = now
    keep = {k: t for k, t in keep.items() if now - t <= LAST_MEASURED_RETIRE_DAYS * DAY}
    return merged, keep


@_locked
def run(now=None, rules=None, filer=None, families=None):
    now = now or time.time()
    rules = rules or load_rules()
    t0 = time.time()
    ctx = {}
    points = {}
    since = now - rules.get("series_days", 8) * DAY
    prev = {}
    sick = []
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
        rec = {"schema": SCHEMA, "t": now, "at": iso(now), "family": fam, "points": pts}
        if fam == "production" and ctx.get("production_src_t"):
            rec["src_t"] = ctx["production_src_t"]
        dup = fam == "production" and old and old[-1].get("src_t") and old[-1].get("src_t") == rec.get("src_t")
        if not dup:
            try:
                append(fam, rec)
            except Exception as e:  # noqa: BLE001  the pass and the alarms outlive a series that cannot be written
                sick.append({"rule": "series_write", "key": "%s._series" % fam, "value": None, "window": "now",
                             "detail": "this pass's %s points were not kept: %s: %s" % (fam, type(e).__name__, str(e)[:160])})
        points.update(pts)
    hist, lastm = {}, {}
    for fam, recs in prev.items():
        recs = [r for r in recs if r["t"] <= now + 300]     # a future row would read as just measured, and hide silence
        hist.update(history(recs))
        for r in recs:      # any MEASURED point, a state string too: only the band and run rules need a number
            for k, p in (r.get("points") or {}).items():
                if isinstance(p, dict) and p.get("m") == "MEASURED" and p.get("v") is not None:
                    lastm[k] = max(r["t"], lastm.get(k, r["t"]))
    lastm, saved_lm = carry_last_measured(lastm, _obj(read_json(ops_dir() / "last_measured.json")).get("t"),
                                          points, now)
    try:
        flags = andon(points, hist, lastm, rules, now) + sick
    except Exception as e:  # noqa: BLE001  no flags this pass, said aloud; the alarms still run
        flags = sick + [{"rule": "bad_rule", "key": "rules", "value": None, "window": "now",
                         "detail": "andon failed: %s: %s" % (type(e).__name__, str(e)[:160])}]
    if rules.get("_load_error"):
        flags.append({"rule": "bad_rule", "key": "rules.file", "value": None, "window": "now",
                      "detail": "the rules file cannot be read, last good copy in use: %s" % rules["_load_error"]})
    if not families:    # a key no collector reports would keep its alarm silent for good; a limited pass cannot tell
        for t in good_targets(rules):
            fam = t["key"].split(".")[0]
            if fam + "._collector" not in points and not any(fnmatch.fnmatchcase(k, t["key"]) for k in points):
                flags.append({"rule": "bad_rule", "key": "rules.target." + t["key"], "value": None, "window": "now",
                              "detail": "target %s matches no reading: its alarm cannot fire" % t["key"]})
    try:
        atomic_json(ops_dir() / "last_measured.json", {"t": saved_lm})
    except OSError as e:    # a full disk is what the alarms below are for: never let it stop them
        flags.append({"rule": "bad_rule", "key": "last_measured", "value": None, "window": "now",
                      "detail": "last_measured.json not written: %s" % str(e)[:160]})
    try:
        alarms = run_alarms(points, rules, now, ctx.get("known_ids") or set(), filer)
    except Exception as e:  # noqa: BLE001  the digest still goes out, and says the alarms did not run
        alarms = _obj(read_json(ops_dir() / "alarms.json"))
        flags.append({"rule": "bad_rule", "key": "alarms", "value": None, "window": "now",
                      "detail": "NO ALARM RAN this pass: %s: %s" % (type(e).__name__, str(e)[:160])})
    flags += [{"rule": "alarm_state", "key": aid, "value": None, "window": "now", "detail": a.get("error") or "unreadable"}
              for aid, a in sorted(alarms.items()) if isinstance(a, dict) and a.get("state") == "UNREADABLE"]
    old = _obj(read_json(ops_dir() / "flags.json")).get("flags")
    old_flags = {flag_id(f): f for f in (old if isinstance(old, list) else [])
                 if isinstance(f, dict) and "rule" in f and "key" in f}
    for f in flags:
        f["since"] = (old_flags.get(flag_id(f)) or {}).get("since") or iso(now)
    run_s = round(time.time() - t0, 1)
    atomic_json(ops_dir() / "flags.json", {"at": iso(now), "flags": flags})
    atomic_json(ops_dir() / "status.json", {"schema": SCHEMA, "at": iso(now), "t": now, "run_s": run_s,
                                             "points": points, "flags": flags, "alarms": alarms})
    # every key of this pass too, not only those with history: a new key's first sample counts (review night r1)
    hist_all = {k: hist.get(k, []) + ([(now, num(points[k]))] if points.get(k, {}).get("m") == "MEASURED"
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
    """Seed series/production.jsonl from rm-pulse-streams' own history so the KPI bands have a baseline on day one.
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
                                  "src_t": t, "backfill": "rm-pulse-streams series.jsonl"})
            n += 1
    return n


# =================================================================================================== install
UNIT = """# rm-ops-watch: ops_watch.py, the Dispatcher's deterministic measurement arm for Operations
# (V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE; listed in src/RimMandrake/rimflow/dispatcher_schedule.json "measure").
# Runs from the pulse-deploy checkout (rm-pulse-update fast-forwards it), like rm-pulse-streams. No AI.
[Unit]
Description=Ops watch (accounts, Codex, Steve lane, disk, timers, KPIs; Andon flags; alarms)

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {deploy}/src/RimMandrake/Utils/ops_watch.py run --file-alarms
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
    r.add_argument("--family", action="append", help="only these families (testing)")
    d = sub.add_parser("digest")
    d.add_argument("--blind", action="store_true", help="print digest_blind.md (the token-blind roles' digest)")
    sub.add_parser("backfill", help="seed an empty production series from rm-pulse-streams' history")
    i = sub.add_parser("install")
    i.add_argument("--apply", action="store_true")
    i.add_argument("--deploy", default=os.environ.get("RM_PULSE_DEPLOY", "/mnt/d/ClaudeWork/rimmandrake/pulse-deploy"))
    a = ap.parse_args(argv)
    if a.cmd == "run":
        try:
            dg = run(filer=real_filer if a.file_alarms else None, families=a.family)
        except Busy as e:
            print("skipped: %s" % e)
            return 0
        print(dg["headline"])
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
