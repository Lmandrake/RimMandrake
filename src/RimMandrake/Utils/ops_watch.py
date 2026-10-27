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
FAMILIES = ("accounts", "codex", "steve", "testing", "disk", "timers", "flow", "process", "tps", "production", "v3", "tokentalk")


def ops_dir() -> Path:
    return Path(os.environ.get("RM_OPS_WATCH_DIR", "/mnt/d/ClaudeWork/rimmandrake/ops_watch"))


def rules_path() -> Path:
    return Path(os.environ.get("RM_OPS_WATCH_RULES", HERE / "ops_watch_rules.json"))


def qhome() -> Path:
    return Path(os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq"))


def data_clone() -> Path:
    return Path(os.environ.get("RM_STREAMS_BENCH", "/home/mandrake/rm/bench"))


def load_rules(path=None) -> dict:
    return json.loads(Path(path or rules_path()).read_text(encoding="utf-8"))


def iso(t: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def epoch(s):
    if s is None:
        return None
    if isinstance(s, bool):
        return None
    if isinstance(s, (int, float)):
        return float(s) if math.isfinite(s) else None
    from datetime import datetime
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
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
    if rate_pct_h <= 0:
        return 10.0
    return round(min(10.0, (left_pct / rate_pct_h) / hours_to_reset), 2)


# ================================================================================================== collectors
def c_accounts(now, rules, ctx):
    import account_usage as AU
    import slot_allocator as SA
    out = {}
    acc = (AU.read_now(now).get("accounts") or {})
    if not acc:
        return {"accounts._collector": U("account_usage.read_now() returned no account")}
    fit = {"fit": rules["accounts_fit"]}
    for name, a in sorted(acc.items()):
        src = a.get("source") or "UNMEASURED"
        if a.get("stale"):
            src = "ESTIMATE" if src == "MEASURED" else src
        left, h = a.get("week_pct_left"), a.get("hours_to_week_reset")
        k = "accounts.%s." % name
        if src not in ("MEASURED", "ESTIMATE") or left is None:
            why = "account_usage: %s" % (a.get("why") or src)
            for f in ("week_left_pct", "hours_to_reset", "runway"):
                out[k + f] = U(why)
            continue
        mk = (lambda v, u, **x: M(v, u, **x)) if src == "MEASURED" else \
            (lambda v, u, **x: E(v, "account_usage reading is an ESTIMATE%s" % (" (stale)" if a.get("stale") else ""), u, **x))
        out[k + "week_left_pct"] = mk(left, "% of the weekly quota left", measured_at=a.get("measured_at"))
        out[k + "hours_to_reset"] = mk(h, "h to the weekly reset") if h is not None else U("no reset time")
        rate, how = None, None
        if src == "MEASURED":
            r, n, span = SA.slope(name, a.get("week_resets_at"), now, fit)
            if r is not None:
                rate, how = r, "meter slope, %d readings over %.1f h" % (n, span)
        if rate is None and h is not None and a.get("week_pct_used") is not None:
            elapsed = 168.0 - h
            if elapsed >= 6:
                rate, how = a["week_pct_used"] / elapsed, "the week's average burn (%.0f%% over %.0f h)" % (
                    a["week_pct_used"], elapsed)
        rw = runway(left, rate, h)
        if rw is None:
            out[k + "runway"] = U("no burn rate: the week is under 6 h old and the meter has no slope")
        elif rate is None:      # spent before any rate exists: 0 is as certain as the reading
            out[k + "runway"] = (M(0.0, "x the time to reset", why="quota spent") if src == "MEASURED" else
                                 E(0.0, "quota spent per an ESTIMATE reading", "x the time to reset"))
        elif src == "MEASURED" and how and how.startswith("meter"):
            out[k + "runway"] = M(rw, "x the time to reset", rate_pct_h=round(rate, 3), rate_from=how)
        else:
            out[k + "runway"] = E(rw, "rate from %s%s" % (how, "" if src == "MEASURED" else "; the reading is an ESTIMATE"),
                                  "x the time to reset", rate_pct_h=round(rate, 3))
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
    week = []
    for r in recs:      # (ts, p_used, p_win, p_reset, s_used, s_win, s_reset, plan)
        if r[2] == 10080:
            week.append((epoch(r[0]), float(r[1]), epoch(r[3])))
        elif r[5] == 10080 and r[4] is not None:
            week.append((epoch(r[0]), float(r[4]), epoch(r[6])))
    week = sorted(w for w in week if w[0] is not None and w[2] is not None)
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
    if age_h > cr.get("stale_h", 6):
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
    elapsed = 168.0 - h
    if rate is None and elapsed >= 6:
        rate, how = used / elapsed, "the week's average burn (%.0f%% over %.0f h)" % (used, elapsed)
    rw = runway(100.0 - used, rate, h)
    if rw is None:
        out["codex.runway"] = U("no burn rate: the week is under 6 h old")
    elif rate is None:
        out["codex.runway"] = (M(0.0, "x the time to reset", why="quota spent")
                               if out["codex.week_used_pct"]["m"] == "MEASURED" else
                               E(0.0, "quota spent per an ESTIMATE reading", "x the time to reset"))
    elif how.startswith("readings") and out["codex.week_used_pct"]["m"] == "MEASURED":
        out["codex.runway"] = M(rw, "x the time to reset", rate_pct_h=round(rate, 3), rate_from=how)
    else:
        out["codex.runway"] = E(rw, "rate from " + how, "x the time to reset", rate_pct_h=round(rate, 3))
    return out


def done_jobs(since, bad=None):
    """testq done records finished at or after `since` (epoch), oldest first, read by file mtime first. A record in the
    window that cannot be read is appended to `bad` (when given), so a caller never mistakes the readable subset for all."""
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
        fin = epoch(d.get("finished") or (d.get("result") or {}).get("finished")) if isinstance(d, dict) else None
        if fin is None:
            if bad is not None:
                try:
                    if os.path.getmtime(f) >= since:
                        bad.append(os.path.basename(f))
                except OSError:
                    pass
            continue
        if fin >= since:
            out.append((fin, d))
    out.sort(key=lambda x: x[0])
    return out


def c_steve(now, rules, ctx):
    out = {}
    sj = read_json(qhome() / "steward.json")
    if not isinstance(sj, dict) or epoch(sj.get("epoch")) is None:
        out["steve.state"] = U("steward.json missing or unreadable under %s" % qhome())
        for k in ("heartbeat_age_min", "fault_min", "unowned_stall_min"):
            out["steve." + k] = U("steward.json missing or unreadable")
    else:
        hb = (now - epoch(sj["epoch"])) / 60.0
        wj = read_json(qhome() / "steward_watch.json")
        wj = wj if isinstance(wj, dict) else {}
        we = epoch(wj.get("epoch"))
        wage = (now - we) / 60.0 if we is not None else None
        st = sj.get("state")
        if hb > 30:
            out["steve.state"] = E(st, "steward.json is %.0f min old: its last word, not now" % hb, "steward state",
                                   reason=(sj.get("reason") or "")[:160], since=sj.get("since"))
        else:
            out["steve.state"] = M(st, "steward state", reason=(sj.get("reason") or "")[:160], since=sj.get("since"))
        out["steve.heartbeat_age_min"] = M(round(hb, 1), "min since steward.json")
        out["steve.watch_age_min"] = M(round(wage, 1), "min since steward_watch.json") if wage is not None else \
            U("steward_watch.json has no epoch")
        since = epoch(sj.get("since"))
        if hb > 30:
            fault_min = None    # a stale steward's fault flag is its last word, not now: unknown, never 0
            out["steve.fault_min"] = U("steward.json is %.0f min old: whether it is in a fault now is unknown" % hb)
        elif sj.get("fault") and since is None:
            fault_min = None
            out["steve.fault_min"] = U("steward reports a fault with no readable `since`: duration unknown")
        else:
            fault_min = round((now - since) / 60.0, 1) if sj.get("fault") else 0.0
            out["steve.fault_min"] = M(fault_min, "min in a fault state")
        nobody = []
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
    jobs = done_jobs(now - 7 * DAY, bad)
    # a record with no outcome cannot say INVALID or not: unseen, like an unreadable one
    bad += [((d.get("job") or {}).get("id") or "?") + " (no outcome)" for _, d in jobs
            if not (d.get("result") or {}).get("outcome")]
    ctx["steve_jobs_bad"] = bad
    if not jobs:
        why = "no testq done record in 7 d under %s" % (qhome() / "done") + (
            " (%d unreadable)" % len(bad) if bad else "")
        for k in ("invalid_streak", "jobs_24h", "invalid_24h", "last_done_age_min"):
            out["steve." + k] = U(why)
        return out
    def run_of_invalid(js):
        n = 0
        for _, d in reversed(js):
            oc = (d.get("result") or {}).get("outcome")
            if oc != "INVALID":
                if not oc and ((d.get("job") or {}).get("id") or "?") + " (no outcome)" not in bad:
                    bad.append(((d.get("job") or {}).get("id") or "?") + " (no outcome)")   # the run's end is unknown
                break
            n += 1
        return n
    streak = run_of_invalid(jobs)
    if streak == len(jobs):
        # every job in the week was INVALID: the run may start before the window, so read the whole done history
        older_bad = []
        streak = run_of_invalid(done_jobs(0, older_bad))
        bad += [b for b in older_bad if b not in bad]
    last = jobs[-1]
    out["steve.invalid_streak"] = M(streak, "INVALID results in a row", last_job=(last[1].get("job") or {}).get("id"),
                                    last_cause=(last[1].get("result") or {}).get("cause"))
    d24 = [d for f, d in jobs if f >= now - DAY]
    out["steve.jobs_24h"] = M(len(d24), "jobs finished, 24 h")
    out["steve.invalid_24h"] = M(sum(1 for d in d24 if (d.get("result") or {}).get("outcome") == "INVALID"),
                                 "INVALID jobs, 24 h")
    out["steve.last_done_age_min"] = M(round((now - last[0]) / 60.0, 1), "min since the last job finished")
    if bad:
        for k in ("invalid_streak", "jobs_24h", "invalid_24h", "last_done_age_min"):
            p = out["steve." + k]
            out["steve." + k] = E(p["v"], "%d done record(s) in the window unreadable (%s): counted over the readable "
                                  "rest" % (len(bad), ", ".join(bad[:3])), p.get("unit"), **(p.get("x") or {}))
    ctx["steve_jobs"] = jobs
    return out


def caught(d, closes, close_after_h):
    """A testq job caught something: a FAIL row, a finding it filed, or an item it ran closed within the window."""
    res = d.get("result") or {}
    if (res.get("counts") or {}).get("FAIL"):
        return True
    groups = ((d.get("ingested") or {}).get("groups") or {})
    if any(g.get("findings") for g in groups.values() if isinstance(g, dict)):
        return True
    fin = epoch(d.get("finished") or res.get("finished")) or 0
    items = set(groups) | {(d.get("job") or {}).get("item")}
    return any(fin <= c <= fin + close_after_h * HOUR for i in items if i for c in closes.get(i, ()))


def c_testing(now, rules, ctx):
    out = {}
    jobs = ctx.get("steve_jobs")
    bad = ctx.get("steve_jobs_bad")
    if jobs is None:
        bad = []
        jobs = done_jobs(now - 7 * DAY, bad)
    bad = bad or []
    closes = ctx.get("closes")
    if closes is None:
        return {"testing.nothing_h_7d": U("the ledger was not readable, so closes after a run are unknown")}
    ch = rules["testing"]["close_after_h"]
    steve_h, steve_n, unk, young = 0.0, 0, 0, 0
    for fin, d in jobs:
        st = epoch((d.get("result") or {}).get("started"))
        if st is None or fin - st <= 0 or not (d.get("result") or {}).get("outcome"):
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
                days[r.get("day")] = r          # the last record of each day wins
    except OSError:
        days = {}
    lo = time.strftime("%Y-%m-%d", time.localtime(now - 7 * DAY))
    ah, adays, blind, soft = 0.0, 0, 0, 0
    for day, r in sorted(days.items()):
        if not day or day <= lo or not isinstance(r, dict):
            continue
        a = (r.get("machines") or {}).get("archmagi") or {}
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
        vals["mod_fails"] = val((a.get("fail_split") or {}).get("mod"))
        if not all(isinstance(vals[k], (int, float)) and not isinstance(vals[k], bool) for k in ("busy_pct", "window_h")):
            blind += 1
            continue
        sig = [vals[k] for k in ("findings", "closed_after_pass", "regressions", "mod_fails")]
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
            if row.get("verdict") != "DELETED":
                if not isinstance(row.get("bytes"), (int, float)):
                    nob += 1
                    continue
                tot[row.get("verdict")] = tot.get(row.get("verdict"), 0) + row["bytes"]
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
    failed = systemctl_json("list-units", "--failed", "--all")
    names = sorted(u.get("unit") for u in failed)
    out["timers.failed_units"] = M(len(names), "failed user units", units=names[:12])
    over = []
    for t in systemctl_json("list-timers", "--all"):
        nxt = t.get("next")
        if nxt and nxt / 1e6 < now - 600:
            over.append(t.get("unit"))
    out["timers.overdue_timers"] = M(len(over), "timers whose next elapse is over 10 min past", units=over[:12])
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
    return out


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
    out = {"production.record_age_min": M(round(age, 1), "min since rm-pulse-streams' last record")}
    stale = age > 60
    for k, p in sorted((rec.get("measures") or {}).items()):
        if not isinstance(p, dict):
            continue
        if stale:
            out["production." + k] = U("the streams record is %.0f min old (rm-pulse-streams stopped?)" % age)
        elif p.get("m") == "MEASURED":
            unit = ((p.get("x") or {}).get("unit")) if isinstance(p.get("x"), dict) else None
            out["production." + k] = M(p.get("v"), unit, asof=p.get("asof"))
        else:
            out["production." + k] = soft_point(p)
    ctx["production_src_t"] = rec["t"]
    return out


def c_v3(now, rules, ctx):
    return {"v3." + k: U(why) for k, why in sorted(rules["v3_owed"].items())}


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
    seats = cfg.get("seats") or ["BENCH", "FOUNDRY"]
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
    names = set(cfg.get("roles") or ["conductor", "producer", "arbiter", "auditor", "innovator"])
    try:
        if not rd.is_dir():
            raise RuntimeError("role run folder %s absent" % rd)
        for f in sorted(rd.glob("rm-role-*.json")):
            m = re.match(r"rm-role-(.+)-(\d+)\.json$", f.name)
            if not m or m.group(1) not in names or float(m.group(2)) < since:
                continue
            d = json.loads(f.read_text(encoding="utf-8"))
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
    seats = cfg.get("seats") or ["BENCH", "FOUNDRY"]
    groups = list(seats) + ["commits." + s for s in seats] + ["role." + r for r in (cfg.get("roles") or
              ["conductor", "producer", "arbiter", "auditor", "innovator"])]
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


COLLECTORS = {"accounts": c_accounts, "codex": c_codex, "steve": c_steve, "flow": c_flow, "testing": c_testing,
              "disk": c_disk, "timers": c_timers, "process": c_process, "tps": c_tps, "production": c_production,
              "v3": c_v3, "tokentalk": c_tokentalk}
ORDER = ("accounts", "codex", "steve", "flow", "testing", "disk", "timers", "process", "tps", "production", "v3", "tokentalk")


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
    return any(fnmatch.fnmatchcase(key, p) for p in pats)


def num(p):
    v = p.get("v") if isinstance(p, dict) else None
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def history(recs):
    """key -> [(t, value)] of MEASURED numeric points, oldest first."""
    h = {}
    for r in recs:
        for k, p in (r.get("points") or {}).items():
            v = num(p)
            if isinstance(p, dict) and p.get("m") == "MEASURED" and v is not None:
                h.setdefault(k, []).append((r["t"], v))
    return h


def _cmp(v, op, x):
    return {"<": v < x, "<=": v <= x, ">": v > x, ">=": v >= x}[op]


def andon(points, hist, last_measured, rules, now):
    """-> [flag]. points: this pass's key -> point; hist: key -> [(t, v)] MEASURED before this pass;
    last_measured: key -> t of its last MEASURED point before this pass."""
    flags = []
    b, rn, sl = rules["band"], rules["run"], rules["silent"]
    gone = {k: U("no longer reported by its collector") for k in last_measured if k not in points}
    for k, p in sorted({**gone, **points}.items()):
        v = num(p)
        meas = p.get("m") == "MEASURED" and v is not None
        hs = hist.get(k, [])
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
        if not meas and matches(k, sl["keys"]) and not matches(k, sl["skip"]):
            lm = last_measured.get(k)
            lim = next((h for pat, h in sl["per_key"].items() if fnmatch.fnmatchcase(k, pat)), sl["default_h"])
            if lm is not None and now - lm > lim * HOUR:
                flags.append({"rule": "silent", "key": k, "value": None, "window": "silent %.1f h (limit %g h)" % (
                    (now - lm) / HOUR, lim), "detail": "last MEASURED %s; now %s: %s" % (
                    iso(lm), p.get("m"), (p.get("why") or "")[:160])})
    for tg in rules["targets"]:
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
    for tg in rules["targets"]:
        if not tg.get("alarm"):
            continue
        marks = tg.get("marks") or ["MEASURED"]
        for k, p in points.items():
            if not fnmatch.fnmatchcase(k, tg["key"]):
                continue
            aid = "%s:%s" % (tg["tag"], k)
            v = num(p)
            st[aid] = None if (v is None or p.get("m") not in marks) else bool(_cmp(v, tg["op"], tg["value"]))
    return st


# ===================================================================================================== alarms
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
    clear_passes = max(1, int(conf.get("clear_passes", 1)))
    for aid in sorted(set(ts) | set(state)):
        crossed = ts.get(aid)          # True crossed / False clear / None UNMEASURED or no reading: hold
        cur = state.get(aid)
        if cur and cur.get("state") == "PENDING" and cur.get("name") in known_ids:
            # filed by a pass that died before saving its state: the ledger has it, never file it twice
            cur.update(state="OPEN", item=cur["name"], error=None, filed=cur.get("filed") or iso(now))
            log.append({"ts": iso(now), "event": "found_filed", "aid": aid, "item": cur["name"]})
        if crossed is False and cur:
            # hysteresis: clear only after clear_passes clear readings in a row, so a reading that wobbles across
            # the line does not file a fresh item on every wobble
            cur["clear_seen"] = cur.get("clear_seen", 0) + 1
            if cur["clear_seen"] >= clear_passes:
                log.append({"ts": iso(now), "event": "cleared" if cur.get("state") == "OPEN" else "cleared_unfiled",
                            "aid": aid, "item": cur.get("item")})
                if cur.get("item") and filer:
                    key = aid.split(":", 1)[1]
                    todo.append({"note_only": True, "item": cur["item"], "name": "note:" + aid,
                                 "text": "ops_watch: cleared at %s (%s now %s)" % (
                                     iso(now), key, (points.get(key) or {}).get("v"))})
                state.pop(aid, None)
                continue
        if crossed and cur:
            cur["clear_seen"] = 0
        if cur and cur.get("state") == "OPEN":
            if crossed:
                cur["last_seen"] = iso(now)
            continue
        if not crossed:
            if cur and cur.get("name") and cur.get("title"):
                # PENDING, not crossed now (UNMEASURED, or clear but not for clear_passes yet): the crossing was
                # real, so keep retrying the filing under the name and title it got when it crossed
                todo.append({"aid": aid, "name": cur["name"], "title": cur["title"]})
            continue
        key = aid.split(":", 1)[1]
        tag = aid.split(":", 1)[0]
        pt = points[key]
        tg = next(t for t in rules["targets"] if t.get("alarm") and t["tag"] == tag and fnmatch.fnmatchcase(key, t["key"]))
        if not cur:
            cur = {"state": "PENDING", "since": iso(now), "tries": 0}
            state[aid] = cur
            log.append({"ts": iso(now), "event": "crossed", "aid": aid, "v": pt.get("v"), "m": pt.get("m")})
        if not cur.get("name"):  # mint once; a retry keeps the saved name
            taken = set(known_ids) | {a.get("name") for a in state.values() if isinstance(a, dict) and a.get("name")}
            cur["name"] = mint_name(tag, taken, tg.get("name") or "OPS_ALARM_DIAGNOSE")
        title = "Ops alarm %s: %s = %s %s(%s), line %s %g" % (tag, key, pt.get("v"), (pt.get("unit") or "") + " ",
                                                            pt.get("m"), tg["op"], tg["value"])
        cur["title"] = title[:160]
        todo.append({"aid": aid, "name": cur["name"], "title": cur["title"]})
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
            cur = state[a["aid"]]
            err = res.get(a["name"])
            cur["tries"] = cur.get("tries", 0) + (1 if filer else 0)
            cur["last_try"] = iso(now)
            if err is None:
                cur.update(state="OPEN", item=a["name"], error=None, filed=iso(now))
                log.append({"ts": iso(now), "event": "filed", "aid": a["aid"], "item": a["name"],
                            "publish": res.get("_publish")})
            else:
                cur["error"] = err
                if filer:
                    log.append({"ts": iso(now), "event": "file_failed", "aid": a["aid"], "error": err})
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
            L.append("- %s %s since %s%s%s" % (a.get("state"), k, a.get("since"), " item " + a["item"] if a.get("item")
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


@_locked
def run(now=None, rules=None, filer=None, families=None):
    now = now or time.time()
    rules = rules or load_rules()
    t0 = time.time()
    ctx = {}
    points = {}
    since = now - rules["series_days"] * DAY
    prev = {}
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
            append(fam, rec)
        points.update(pts)
    hist, lastm = {}, {}
    for fam, recs in prev.items():
        h = history(recs)
        hist.update(h)
        for k, hs in h.items():
            lastm[k] = hs[-1][0]
    flags = andon(points, hist, lastm, rules, now)
    old_flags = {flag_id(f): f for f in (read_json(ops_dir() / "flags.json") or {}).get("flags", [])}
    for f in flags:
        f["since"] = (old_flags.get(flag_id(f)) or {}).get("since") or iso(now)
    alarms = run_alarms(points, rules, now, ctx.get("known_ids") or set(), filer)
    run_s = round(time.time() - t0, 1)
    atomic_json(ops_dir() / "flags.json", {"at": iso(now), "flags": flags})
    atomic_json(ops_dir() / "status.json", {"schema": SCHEMA, "at": iso(now), "t": now, "run_s": run_s,
                                             "points": points, "flags": flags, "alarms": alarms})
    hist_all = {k: v + ([(now, num(points[k]))] if points.get(k, {}).get("m") == "MEASURED" and num(points[k]) is not None
                        else []) for k, v in hist.items()}
    dg = build_digest(points, hist_all, flags, alarms, now, run_s)
    atomic_json(ops_dir() / "digest.json", dg)
    md = digest_md(dg)
    tmp = ops_dir() / "digest.md.tmp"
    tmp.write_text(md, encoding="utf-8")
    os.replace(tmp, ops_dir() / "digest.md")
    return dg


@_locked
def backfill_production(now=None, rules=None):
    """Seed series/production.jsonl from rm-pulse-streams' own history so the KPI bands have a baseline on day one.
    Only into an empty production series (never rewrites what is there); each record keeps its source time."""
    now = now or time.time()
    rules = rules or load_rules()
    if read_series("production", 0):
        return 0
    since = now - rules["series_days"] * DAY
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
    sub.add_parser("digest")
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
        p = ops_dir() / "digest.md"
        print(p.read_text(encoding="utf-8") if p.exists() else "no digest yet: run ops_watch.py run")
        return 0
    return install(a.apply, a.deploy)


if __name__ == "__main__":
    sys.exit(main())
