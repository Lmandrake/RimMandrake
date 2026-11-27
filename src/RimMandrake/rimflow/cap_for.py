#!/usr/bin/env python3
"""cap_for.py — the spend cap of a launch, read from that verb's measured cost in the run records.

    python3 src/RimMandrake/rimflow/cap_for.py <verb> [--model M] [--records DIR]

Why: of 934 runs with a cost (7.2 days to 2026-11-26), 16 ended at their cap and 14 of those 16 caps sat below that
verb's p90 cost; 2 items hit the cap twice (design/specs/2026-11-26-script-candidates/evidence.md G11). A cap is a
runaway guard (CLAUDE.md §No limit without the danger it guards): it must stop a run that spends an account, never an
ordinary run of the verb. Item RIMMANDRAKE_BUILD_CAP_FOR_VERB_FOURTEEN_CAPS_UNDER_P90. Page
design/specs/2026-11-27-cap-for/boundary.md.

It prints one line. MEASURED: the cap in list dollars (spend_watchdog takes dollars) and in weighted_v2 tokens, the
verb's need (p90, max, n runs, how many ended at their cap, the window the records span) and the danger. UNMEASURED:
fewer runs than FLOOR_RUNS; the line names the cause and a fallback cap with where it comes from, or no number when the
records hold too few runs of any verb. COULD NOT LOOK: the folder cannot be listed; no number, exit 2.

The verb and the p90 are those of measure/rows.py G11 (verb_of, pct). A run's cost is its record's `tokens` (weighted_v2,
the launch's own part of a resumed session: detached_helper.own_part), else its legacy `cost_usd` through
role_launch.list_usd_to_weighted. A run with neither (running, UNMEASURED) is not read. --model filters on the record's
`model` field as written (an alias such as `opus`).

The cap never reaches a brief (CLAUDE.md §No launched agent is told its spend): capped_argv hands it to
spend_watchdog.wrap only, and nothing here builds text a launched agent reads.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# budget: danger=a cap sized from too few runs sits below the verb's real p90 and stops ordinary runs (14 of 16 caps hit
# in G11 sat below p90). measured=order statistics: the next run outspends all n seen with chance 1/(n+1); at or under
# the 10% the p90 bar leaves above it needs n >= 9. Fewer runs: UNMEASURED and the fallback.
FLOOR_RUNS = 9
# budget: danger=a runaway run spends an account (owner 2026-11-12: "Don't let any burn go to 90M this time ok?"); the
# cap stops it, never an ordinary run. measured=2026-11-27 run records: the dearest run of each verb with >= 9 runs cost
# 2.19x (READ, n=41) and 1.76x (OPS, n=11) that verb's p90, so 3x p90 stops none of the runs seen and still stops a
# runaway at 3 times the need, not at the flat 120 dollars of 146 of the 160 records.
P90_MULTIPLE = 3
DANGER = "danger: a runaway run spends an account (spend_watchdog stops it from outside; the agent is never told)"
EXIT_COULD_NOT_LOOK = 2
EXIT_NO_NUMBER = 3


class CouldNotLook(Exception):
    """The run records folder cannot be listed: could not look is never "no records"."""


class NoCap(Exception):
    """No measured cap and no fallback number: the launch must state its own cap."""


def verb_of(item):
    """The verb of an item name, as measure/rows.py G11 reads it: the word after RIMMANDRAKE_/RIMMASTER_, else the first."""
    p = (item or "").split("_")
    return p[1] if len(p) > 1 and p[0] in ("RIMMANDRAKE", "RIMMASTER") else p[0]


def pct(xs, q):
    """Nearest-rank percentile, as measure/rows.py's pct: sorted(xs)[min(n-1, int(n*q))]; None for no values."""
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * q))] if xs else None


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def records_dir(records=None):
    if records:
        return records
    import detached_helper as DH
    return DH.runs_dir()


def read_runs(records=None):
    """-> (runs, unreadable count, folder). Each run: {verb, model, wt, capped, at}; wt None when the record has no
    cost. Raises CouldNotLook when the folder cannot be listed (a missing folder is never made)."""
    import detached_helper as DH
    import role_launch as RL
    d = records_dir(records)
    try:
        names = sorted(os.listdir(d))
    except OSError as e:
        raise CouldNotLook("the run records folder %s cannot be listed (%s)" % (d, e.strerror or e))
    runs, bad = [], 0
    for name in names:
        unit = DH.record_unit(name)
        if not unit:
            continue
        try:
            with open(os.path.join(d, name), encoding="utf-8") as f:
                rec = json.load(f)
        except (OSError, ValueError):
            bad += 1
            continue
        if not DH.is_record(rec, unit):
            continue
        if _num(rec.get("tokens")) and rec.get("token_unit") == RL.TOKEN_UNIT:
            wt = int(rec["tokens"])
        elif _num(rec.get("cost_usd")):
            wt = RL.list_usd_to_weighted(rec["cost_usd"])
        else:
            wt = None
        try:
            with open(os.path.join(d, unit + ".out.json"), encoding="utf-8") as f:
                res = json.load(f)
        except (OSError, ValueError):
            res = None
        runs.append({"verb": verb_of(rec.get("item")).upper(), "model": rec.get("model"), "wt": wt,
                     "capped": DH.cap_stopped(res), "at": rec.get("at") if _num(rec.get("at")) else None})
    return runs, bad, d


def _day(t):
    return time.strftime("%Y-%m-%d", time.gmtime(t))


def _window(rs):
    ats = [r["at"] for r in rs if r["at"] is not None]
    return "window %s..%s" % (_day(min(ats)), _day(max(ats))) if ats else "window unknown (no record dates)"


def _fig(wt):
    import role_launch as RL
    return "%s weighted_v2 ($%.2f list)" % ("{:,}".format(int(wt)), RL.weighted_to_list_usd(wt))


def cap_for(verb, model=None, records=None):
    """-> {verb, model, state MEASURED|UNMEASURED, cap_wt, cap_usd (None: no number), p90_wt, max_wt, n, capped_n,
    pooled_n, unreadable, cause, fallback_from, line}. Raises CouldNotLook."""
    import role_launch as RL
    verb = verb.upper()
    runs, bad, d = read_runs(records)
    pool = [r for r in runs if r["wt"] is not None and (model is None or r["model"] == model)]
    own = [r for r in pool if r["verb"] == verb]
    ws = [r["wt"] for r in own]
    p90, mx = pct(ws, 0.9), (max(ws) if ws else None)
    on = " on %s" % model if model else ""
    tail = (", %d record file%s unreadable" % (bad, "" if bad == 1 else "s")) if bad else ""
    out = {"verb": verb, "model": model, "n": len(own), "capped_n": sum(r["capped"] for r in own), "p90_wt": p90,
           "max_wt": mx, "pooled_n": len(pool), "unreadable": bad, "cause": None, "fallback_from": None,
           "records": d}
    if len(own) >= FLOOR_RUNS:
        cap = P90_MULTIPLE * p90
        out.update(state="MEASURED", cap_wt=cap, cap_usd=RL.weighted_to_list_usd(cap))
        out["line"] = ("CAP %s%s: $%.2f list = %s weighted_v2 = %dx p90 | need: p90 %s, max %s, n=%d runs (%d ended at "
                       "their cap%s), %s%s | %s" % (
                           verb, on, out["cap_usd"], "{:,}".format(cap), P90_MULTIPLE, _fig(p90), _fig(mx), len(own),
                           out["capped_n"], ": their need is at least their cost" if out["capped_n"] else "",
                           _window(own), tail, DANGER))
        return out
    out["state"] = "UNMEASURED"
    out["cause"] = "%d runs of %s%s with a cost in the records, fewer than the floor of %d (FLOOR_RUNS)" % (
        len(own), verb, on, FLOOR_RUNS)
    if len(pool) < FLOOR_RUNS:
        out.update(cap_wt=None, cap_usd=None)
        out["line"] = ("UNMEASURED %s%s: %s, and %d runs of every verb, fewer than the floor too: no fallback number; the "
                       "launch must state its cap (--budget-usd)%s | %s" % (verb, on, out["cause"], len(pool), tail,
                                                                           DANGER))
        return out
    pp = pct([r["wt"] for r in pool], 0.9)
    if p90 is not None and p90 > pp:
        base, src = p90, "%dx the p90 of this verb's own %d runs (%s), dearer than every verb's p90 (%s, n=%d)" % (
            P90_MULTIPLE, len(own), _fig(p90), _fig(pp), len(pool))
    else:
        base, src = pp, "%dx the p90 of every verb's runs%s (%s, n=%d, %s)" % (
            P90_MULTIPLE, on, _fig(pp), len(pool), _window(pool))
    cap = P90_MULTIPLE * base
    out.update(cap_wt=cap, cap_usd=RL.weighted_to_list_usd(cap), fallback_from=src)
    out["line"] = "UNMEASURED %s%s: %s | fallback cap $%.2f list = %s weighted_v2, from %s%s | %s" % (
        verb, on, out["cause"], out["cap_usd"], "{:,}".format(cap), src, tail, DANGER)
    return out


def capped_argv(verb, argv, model=None, records=None, python=None):
    """-> (argv run under spend_watchdog at the verb's cap, the cap_for result). The cap goes to the watchdog's
    --cap-usd only; the claude argv (and the brief it carries) is untouched. Raises CouldNotLook, or NoCap when the
    records give no number (the launch must state its cap)."""
    import spend_watchdog
    r = cap_for(verb, model=model, records=records)
    if r["cap_usd"] is None:
        raise NoCap(r["line"])
    return spend_watchdog.wrap(argv, r["cap_usd"], python=python), r


def main(argv=None):
    ap = argparse.ArgumentParser(description="the spend cap of a launch, from the verb's measured cost")
    ap.add_argument("verb", help="the item's verb (RIMMANDRAKE_<VERB>_...), e.g. FIX, BUILD, READ")
    ap.add_argument("--model", help="only runs whose record names this model (as written there, e.g. opus)")
    ap.add_argument("--records", help="the run records folder (default: detached_helper.runs_dir())")
    a = ap.parse_args(argv)
    try:
        r = cap_for(a.verb, model=a.model, records=a.records)
    except CouldNotLook as e:
        print("COULD NOT LOOK: %s: no cap" % e)
        return EXIT_COULD_NOT_LOOK
    print(r["line"])
    return 0 if r["cap_usd"] is not None else EXIT_NO_NUMBER


if __name__ == "__main__":
    sys.exit(main())
