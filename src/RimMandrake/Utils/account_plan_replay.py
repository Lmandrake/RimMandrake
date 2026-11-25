#!/usr/bin/env python3
"""Both engines over the recorded readings (page design/specs/2026-11-24-account-plan-one-file/boundary.md, promise
replay_names_each_difference). It reads; it acts on nothing and writes only its report.

Two parts:
  passes    each pass that the old engine logged (its own log.jsonl), decided again by account_plan.decide on the
            readings of that moment and on the old plan file of that moment (git history of switching_plan.json,
            converted). Each difference gets a cause from CAUSES, or the word UNEXPLAINED.
  measures  the owner's two measures over the same days, three ways:
            actual    what happened: points above the line at each reset (the reader's series), the switches (the
                      switcher's log), the minutes of refused starts for a switch that no level forced (the old log)
            old rule  the old engine's rule (the first eligible account in the order) run on the recorded burn
            new plan  account_plan.decide run on the recorded burn, with a moment of no live run at each pass
                      (`idle`) and with never such a moment (`busy`)
The model of the two runs: the machine's burn in each interval is what the readings show, summed over the accounts,
and it lands on the account that the rule keeps live; one point is the same work on each account; a switch is instant.

    account_plan_replay.py --from 2026-11-10 --to 2026-11-24 [--out report.md]
"""
import argparse
import bisect
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import account_end as AE  # noqa: E402
import account_plan as AP  # noqa: E402
import time_budget  # noqa: E402

REPO = HERE.parent.parent.parent
OLD_LOG = Path("/mnt/d/ClaudeWork/rimmandrake/switching_plan/log.jsonl")
CAUSES = {
    "STAY": "the old engine left an account that was not finished, for the order or for a reset; the plan stays",
    "NO_REFUSAL_ABOVE_THE_WARNING": "the old engine refused new work above the warning line (its soft zone, or a reset "
                                    "that was near); the plan refuses new work only at the account's line",
    "WARNING_LINE": "the two engines end the account at different levels (one at its warning line, one at its line)",
    "ENTRY_LINE": "the plan sends no switch to an account inside its own warning zone",
    "MARKER": "the old engine held or kept an account out by a marker; the plan reads the level",
    "NEXT_BY_WEEK_AHEAD": "both leave the account; the plan picks the next one by the week ahead, not by the order",
    "RESCUE": "the plan leaves an unfinished account to save points from a reset, worth a switch, with no run live",
    "UNREADABLE_LEVEL": "the level could not be read at that pass; the two engines treat a blind meter differently",
    "RESET_DAY": "the plan lowers the line on the day of the account's reset (owner, 2026-11-24); with that rule off, "
                 "the two agree",
    "PLAN_DATA": "the old engine's line at that pass is not the line of its committed plan file of that time (the "
                 "file in the timer's clone differed)",
}
class CouldNotLook(Exception):
    """A source of the replay cannot be read. The text names it."""


SKIP = ("passive", "skip", "poll", "meter_poll", "account_end", "start", "stopped")


def jsonl(path):
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for ln in f:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    continue
    except OSError as e:
        raise CouldNotLook("%s cannot be read: %s" % (path, e)) from e
    return out


def legacy_plans(repo=REPO):
    """[(commit time, the old plan file at that commit)], oldest first. CouldNotLook when git gives none."""
    rel = "src/RimMandrake/Utils/switching_plan.json"
    try:
        r = subprocess.run(["git", "-C", str(repo), "log", "--format=%H %ct", "--", rel], capture_output=True, text=True,
                           timeout=time_budget.CALL_S)
    except (OSError, subprocess.SubprocessError) as e:
        raise CouldNotLook("the git history of %s cannot be read: %s" % (rel, e)) from e
    out = []
    for ln in r.stdout.splitlines():
        sha, ct = ln.split()
        try:
            text = subprocess.run(["git", "-C", str(repo), "show", "%s:%s" % (sha, rel)], capture_output=True, text=True,
                                  timeout=time_budget.CALL_S).stdout
            out.append((float(ct), json.loads(text)))
        except (OSError, ValueError, subprocess.SubprocessError):
            continue
    if not out:
        raise CouldNotLook("the git history of %s names no commit" % rel)
    return sorted(out, key=lambda x: x[0])


def plan_at(plans, t, today):
    """The old plan file in force at t, with the account-end numbers of today where that day had none."""
    hit = None
    for ct, p in plans:
        if ct <= t:
            hit = p
    hit = dict(hit if hit is not None else plans[0][1])
    hit.setdefault("account_end", today["account_end"])
    hit.setdefault("fresh", today["fresh"])
    hit.setdefault("exceptions", [])
    return hit


class Series:
    """The reader's series, by account and time."""

    def __init__(self, rows):
        import account_usage as AU
        self.AU, self.by, self.times = AU, {}, {}
        for r in rows or []:
            t = AP.stamp(r.get("ts"))
            if isinstance(r, dict) and r.get("account") and t is not None:
                self.by.setdefault(r["account"], []).append((t, r))
        for a in self.by:
            self.by[a].sort(key=lambda x: x[0])
            self.times[a] = [t for t, _r in self.by[a]]
        self.all = sorted(((t, r) for a in self.by for t, r in self.by[a]), key=lambda x: x[0])
        self.all_t = [t for t, _r in self.all]

    def rows_at(self, t):
        out = {}
        for a in self.by:
            i = bisect.bisect_right(self.times[a], t)
            if i:
                out[a] = self.AU.derive_record(self.by[a][i - 1][1], t)
        return out

    def window(self, t0, t1):
        return [r for _t, r in self.all[bisect.bisect_left(self.all_t, t0):bisect.bisect_right(self.all_t, t1)]]


def classify(old, new) -> str:
    """The cause of a difference between the old engine's logged pass and the plan's decision, or UNEXPLAINED.
    '' when they agree: both keep the live account, or both leave it for the same account, or both stop."""
    od, nd = old.get("do"), new.get("do")
    old_to = old.get("to") if od in ("switch", "drain") else None
    new_to = new.get("to") if nd == "switch" or new.get("drain_of") == "switch" else None
    if new.get("drain_of") == "switch" and new_to is None:
        new_to = "?"
    old_stop, new_stop = od in ("stop",), nd in ("stop",) or new.get("drain_of") == "stop"
    old_soft = od == "soft"
    new_soft = nd == "soft"
    why_old = str(old.get("why") or "")
    if AP.is_num(old.get("line")) and AP.is_num(new.get("line")) and abs(old["line"] - new["line"]) > 2:
        return "PLAN_DATA"
    if old_to and new_to:
        return "" if (old_to == new_to or new_to == "?") else "NEXT_BY_WEEK_AHEAD"
    if old_stop and new_stop:
        return ""
    if not old_to and not new_to and not old_stop and not new_stop:
        if old_soft == new_soft:
            return ""
        if old_soft:
            if "reads" in why_old or "not fresh" in why_old or "cannot prove" in why_old or "not confirmed" in why_old:
                return "UNREADABLE_LEVEL"
            return "NO_REFUSAL_ABOVE_THE_WARNING"
        if new.get("pct_left") is None or "reads" in str(new.get("why")):
            return "UNREADABLE_LEVEL"
        return "WARNING_LINE"
    if od == "hold" and "already" in why_old:
        return "MARKER"
    if old_to and not new_to:
        if new_stop:
            return "ENTRY_LINE"
        pl, ln = old.get("pct_left"), old.get("line")
        if pl is not None and ln is not None and pl > ln:
            return "STAY"
        return "ENTRY_LINE" if nd in ("soft", "normal") else "UNEXPLAINED"
    if new_to and not old_to:
        if not new.get("under") and nd == "switch":
            return "RESCUE"
        if old_stop or od == "hold" or "kept" in why_old:
            return "MARKER"
        return "WARNING_LINE"
    if old_stop != new_stop:
        return "WARNING_LINE" if new_stop else "ENTRY_LINE"
    return "UNEXPLAINED"


def passes(series, old_log, switches, plans, today, seed, t0, t1):
    """-> (compared, {cause: count}, {cause: its first lines}, unexplained lines, episodes). An episode is a run of
    passes, at most 30 min apart, with one cause, one live account and one target: [cause, first time, last time, passes, line]."""
    counts, shown, bad, n, eps, last = {}, {}, [], 0, [], None
    sw_t = [AP.stamp_or(s.get("ts"), 0) for s in switches]
    for rec in old_log:
        t = AP.stamp(rec.get("at"))
        if t is None or not t0 <= t <= t1 or rec.get("dry") or rec.get("do") in SKIP or not rec.get("live"):
            continue
        legacy = plan_at(plans, t, today)
        plan = AP.convert_legacy(legacy, seed)
        rows = series.rows_at(t)
        state = {}
        f = {"now": t, "live": rec["live"], "runs": None, "rows": rows,
             "burn_live": AE.burn_of(series.window(t - 3600, t), rec["live"], t, plan["numbers"]["account_end"]),
             "burn_h": AP.fleet_burn(series.window(t - 86400, t), t, 24), "switches": switches[:bisect.bisect_right(sw_t, t)],
             "hand": "respected" in str(rec.get("why")), "markers": {}, "state": state}
        new = AP.decide(plan, f)
        n += 1
        cause = classify(rec, new)
        if not cause:
            continue
        off = json.loads(json.dumps(plan))
        off["numbers"]["reset_day"]["hours"] = 0
        if not classify(rec, AP.decide(off, f)):
            cause = "RESET_DAY"
        counts[cause] = counts.get(cause, 0) + 1
        line = "%s  old %s%s (%s%% left, line %s) | plan %s%s: %s" % (
            AP.pacific(t), rec["do"], " -> %s" % rec["to"] if rec.get("to") else "", rec.get("pct_left"), rec.get("line"),
            new["do"], " -> %s" % new["to"] if new.get("to") else "", str(new.get("why"))[:160])   # cut-ok: a one-line replay report row
        key = (cause, rec["live"], new.get("to"))
        if last == key and t - eps[-1][2] <= 1800:      # the same difference, with at most a pass or two between
            eps[-1][2], eps[-1][3] = t, eps[-1][3] + 1
        else:
            eps.append([cause, t, t, 1, line])
        last = key
        shown.setdefault(cause, [])
        if len(shown[cause]) < 3:
            shown[cause].append(line)
        if cause == "UNEXPLAINED":
            bad.append(line)
    return n, counts, shown, bad, eps


# ------------------------------------------------------------------ the measures, modelled
def burn_stream(series, t0, t1):
    """[(time, points)]: the rises of what is used between two MEASURED readings of one account in one week; and
    [(time, account, level)]: a refill that no reset time explains (what is used fell by 20 points in one week)."""
    burn, refill = [], []
    for a, rd in series.by.items():
        prev = None
        for t, r in rd:
            u, rs = r.get("week_pct_used"), AP.stamp(r.get("week_resets_at"))
            if r.get("source") != "MEASURED" or not AP.is_num(u):
                continue
            if prev is not None and t0 < t <= t1:
                same = prev[2] is None or rs is None or abs(prev[2] - rs) <= AE.RESET_JITTER_S
                if same and u > prev[1]:
                    burn.append((t, u - prev[1]))
                elif same and u < prev[1] - 20:
                    refill.append((t, a, 100 - u))
            prev = (t, u, rs)
    return sorted(burn), sorted(refill)


def reset_times(series):
    """{account: [each weekly reset instant the readings name]}, by cluster (a reset time moves by a minute)."""
    out = {}
    for a, rd in series.by.items():
        xs = sorted({AP.stamp(r.get("week_resets_at")) for _t, r in rd if AP.stamp(r.get("week_resets_at"))})
        keep = []
        for x in xs:
            if not keep or x - keep[-1] > 86400:
                keep.append(x)
        out[a] = keep
    return out


def synth(left, nxt, t):
    return {"source": "MEASURED", "stale": False, "week_pct_left": round(left, 3), "week_pct_used": round(100 - left, 3),
            "age_min": 0.0, "week_resets_at": AP.iso(nxt) if nxt else None,
            "hours_to_week_reset": (nxt - t) / 3600 if nxt else None}


def model(series, switches, plans, today, seed, t0, t1, rule, idle=True, drain_h="plan"):
    """One run of the days t0..t1 under `rule` ('old' or 'new'). -> {erased: {account: points}, erased_total,
    switches, early (switches off an account above its line), idle_pts, burn}. drain_h: another rescue.drain_h than
    the seed's (None: a rescue never refuses a start)."""
    import switching_plan as SP
    burn, refill = burn_stream(series, t0, t1)
    resets = reset_times(series)
    rows0 = series.rows_at(t0)
    accts = [a for a in today["order"] if a in rows0]
    left = {a: (rows0[a].get("week_pct_left") if rows0[a].get("week_pct_left") is not None else 100.0) for a in accts}
    live = next((s.get("to") for s in reversed(switches) if AP.stamp_or(s.get("ts"), float("inf")) <= t0), accts[0])
    if live not in accts:
        live = accts[0]
    events = sorted([(t, 1, "burn", p) for t, p in burn] + [(t, 0, "refill", (a, lv)) for t, a, lv in refill
                                                             if a in accts]
                    + [(r, 0, "reset", a) for a in accts for r in resets.get(a, []) if t0 < r <= t1])
    erased, n_sw, early, idle_pts, total, sim_sw, recent = {}, 0, 0, 0.0, 0.0, [], []

    def nxt(a, t):
        return next((r for r in resets.get(a, []) if r > t), None)

    for t, _k, kind, x in events:
        legacy = plan_at(plans, t, today)
        plan = AP.convert_legacy(legacy, seed)
        if drain_h != "plan":
            plan["numbers"]["rescue"]["drain_h"] = drain_h
        if kind == "reset":
            env = AP.Env(t - 1, lambda a: left.get(a), lambda a: x and t)
            rl = AP.rule_of(plan, x, env)
            line = rl["line"] if rl else AP.standing_line(plan, x)
            erased[x] = erased.get(x, 0.0) + max(0.0, left[x] - (line if line is not None else 0))
            left[x] = 100.0
            continue
        if kind == "refill":
            left[x[0]] = max(left[x[0]], x[1])
            continue
        rows = {a: synth(left[a], nxt(a, t), t) for a in accts}
        recent = [(tt, p) for tt, p in recent if tt > t - 86400] + [(t, x)]
        span_h = max(1.0, (t - max(t0, t - 86400)) / 3600)
        if rule == "new":
            f = {"now": t, "live": live, "runs": [] if idle else ["a-live-run"] * 5, "rows": rows,
                 "burn_live": {"rate": sum(p for _tt, p in recent) / span_h / 60, "stale": False, "age_s": 0},
                 "burn_h": sum(p for _tt, p in recent) / span_h, "switches": sim_sw, "hand": False, "markers": {},
                 "state": {}}
            d = AP.decide(plan, f)
            to = d.get("to") if d["do"] == "switch" or d.get("drain_of") == "switch" else None
            stop = d["do"] == "stop" or d.get("drain_of") == "stop"
            under = bool(d.get("under")) or d.get("drain_of") == "switch"
        else:
            eff = SP.at(legacy, t, rows)
            _line, elig = SP.lines(rows, eff, t)
            tgt = SP.pick(rows, eff, t, elig)
            to = tgt if tgt not in (None, live) else None
            stop = tgt is None
            under = not elig.get(live, False)
        if to:
            n_sw += 1
            early += 0 if under else 1
            sim_sw = sim_sw + [{"from": live, "to": to, "ts": AP.iso(t)}]
            live = to
        total += x
        if stop:
            idle_pts += x
        else:
            left[live] = max(0.0, left[live] - x)
    return {"erased": {a: round(v, 1) for a, v in sorted(erased.items())}, "erased_total": round(sum(erased.values()), 1),
            "switches": n_sw, "early": early, "idle_pts": round(idle_pts, 1), "burn": round(total, 1)}


def actual(series, switches, old_log, plans, today, seed, t0, t1):
    """What happened in t0..t1, measured: erased points, switches, refused-start minutes for a switch above the line."""
    def line_at(a, t):
        plan = AP.convert_legacy(plan_at(plans, t, today), seed)
        env = AP.Env(t - 1, lambda x: None, lambda x: t)
        rl = AP.rule_of(plan, a, env) if a in plan["accounts"] else None
        return rl["line"] if rl else AP.standing_line(plan, a) if a in plan["accounts"] else None
    rows = [r for _t, r in series.all]
    m = AP.measures(rows, [s for s in switches if t0 <= AP.stamp_or(s.get("ts"), 0) <= t1], line_at, since=t0)
    erased, unmeasured, n_sw = {}, [], 0
    for w, v in m.items():
        n_sw += v["switches"]
        for a, x in v["erased"].items():
            if AP.stamp(v["resets"].get(a)) is not None and AP.stamp(v["resets"][a]) > t1:
                continue
            if isinstance(x, str):
                unmeasured.append("%s week of %s: %s" % (a, w, x))
            else:
                erased[a] = erased.get(a, 0.0) + x
    drains = sorted(AP.stamp(r.get("at")) for r in old_log
                    if r.get("do") == "drain" and not r.get("dry") and t0 <= AP.stamp_or(r.get("at"), 0) <= t1)
    mins = sum(min(b - a, 360) for a, b in zip(drains, drains[1:]) if b - a <= 360) / 60 + (5 if drains else 0)
    return {"erased": {a: round(v, 1) for a, v in sorted(erased.items())}, "erased_total": round(sum(erased.values()), 1),
            "switches": n_sw, "unmeasured": unmeasured, "refused_start_min": round(mins),
            "drain_passes": len(drains)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--from", dest="t0", required=True)
    ap.add_argument("--to", dest="t1", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    t0, t1 = AP.stamp(a.t0), AP.stamp(a.t1)
    if t0 is None or t1 is None or t1 <= t0:
        print("REFUSED: --from and --to are ISO times, --to after --from")
        return AP.REFUSED
    import switching_plan as SP
    try:
        rows, old_log, plans = jsonl(AE.SERIES), jsonl(OLD_LOG), legacy_plans()
    except CouldNotLook as e:
        print("COULD NOT LOOK: %s" % e)
        return AP.COULD_NOT_LOOK
    switches = SP.switches()
    if switches is None:
        print("COULD NOT LOOK: the switcher's log cannot be read")
        return AP.COULD_NOT_LOOK
    today, seed = SP.load_plan(HERE / "switching_plan.json"), json.loads(AP.SEED.read_text())
    series = Series(rows)
    t_start = time.time()
    n, counts, shown, bad, eps = passes(series, old_log, switches, plans, today, seed, t0, t1)
    out = ["# Replay %s to %s" % (AP.pacific(t0), AP.pacific(t1)), "",
           "Made by `account_plan_replay.py` in %.0f s. Readings: %d lines of the series; old passes: %d lines; "
           "switches: %d; old plan files: %d." % (time.time() - t_start, len(rows), len(old_log), len(switches), len(plans)),
           "", "## Passes", "",
           "Passes compared: %d. Same decision: %d. Different with a named cause: %d. UNEXPLAINED: %d." % (
               n, n - sum(counts.values()), sum(v for k, v in counts.items() if k != "UNEXPLAINED"),
               counts.get("UNEXPLAINED", 0)), ""]
    for cause, c in sorted(counts.items(), key=lambda kv: -kv[1]):
        mine = [e for e in eps if e[0] == cause]
        out.append("- **%s** (%d passes in %d episodes): %s" % (cause, c, len(mine),
                                                                 CAUSES.get(cause, "no cause in the list fits")))
        show = mine if cause in ("RESCUE", "STAY", "NEXT_BY_WEEK_AHEAD", "ENTRY_LINE", "UNEXPLAINED") else mine[:3]
        out += ["  - %d passes to %s: `%s`" % (e[3], AP.pacific(e[2]), e[4]) for e in show]
    act = actual(series, switches, old_log, plans, today, seed, t0, t1)
    runs = {"old rule": model(series, switches, plans, today, seed, t0, t1, "old"),
            "new plan, idle": model(series, switches, plans, today, seed, t0, t1, "new", idle=True),
            "new plan, busy": model(series, switches, plans, today, seed, t0, t1, "new", idle=False),
            "new plan, busy, a rescue never refuses a start (rescue.drain_h null)":
                model(series, switches, plans, today, seed, t0, t1, "new", idle=False, drain_h=None)}
    out += ["", "## Measures", "",
            "| run | points erased at resets | by account | switches | of them off an unfinished account | burn that "
            "found no account | refused-start minutes for a switch above the line |", "|---|---|---|---|---|---|---|",
            "| actual (measured) | %s | %s | %d | not recorded | not recorded | %d (%d drain passes) |" % (
                act["erased_total"], act["erased"], act["switches"], act["refused_start_min"], act["drain_passes"])]
    for name, r in runs.items():
        out.append("| %s (modelled) | %s | %s | %d | %d | %s of %s | %s |" % (
            name, r["erased_total"], r["erased"], r["switches"], r["early"], r["idle_pts"], r["burn"],
            "not modelled" if name == "old rule" else "0" if (name.endswith("idle") or "null" in name) else
            "at most %d x 2 h (one drain for each rescue)" % r["early"]))
    if act["unmeasured"]:
        out += ["", "UNMEASURED in the actual row (not counted as 0): " + "; ".join(act["unmeasured"])]
    text = "\n".join(out) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    print(text)
    print("REPLAY: %d passes, %d unexplained" % (n, counts.get("UNEXPLAINED", 0)))
    return AP.OK if not counts.get("UNEXPLAINED") else AP.NO


if __name__ == "__main__":
    sys.exit(main())
