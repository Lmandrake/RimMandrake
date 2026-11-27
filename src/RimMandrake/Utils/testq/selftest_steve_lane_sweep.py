#!/usr/bin/env python3
"""Selftest of steve_lane_sweep.py (RIMMANDRAKE_BUILD_STEVE_LANE_SWEEP_PAUSE_HELD_49_HOURS): each measured fault of the
SteveDesktop lane, planted, is reported by the sweep; each check is red on a fault of its own kind; the shipped code
sweeps clean over every regime of design/specs/2026-11-27-steve-lane-sweep/boundary.md. Every line prints its worst
value, its limit and how many cases it read. Offline: a temp queue home, a fake clock, no ssh, no game.
STEVE_LANE_SWEEP_BLIND=<CHECK,...> switches checks off: the run that shows a test red when the sweep cannot see.
STEVE_LANE_SWEEP_PLANT=<plant> plants a fault in every regime: the run that shows the clean sweep red.
--quick: the regimes cut to 16 h and no seeded mixes (the door at ./publish); the planted faults are whole."""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import steve_lane_sweep as W  # noqa: E402

FAILS = []
QUICK = "--quick" in sys.argv[1:]
OUT = {}


def check(name, ok, msg):
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, msg))
    if not ok:
        FAILS.append(name)


def m(out, k):
    x = out["measures"][k]
    return "%s worst %s limit %s cases %s" % (k, x["worst"], x["limit"], x["cases"])


def found(out, check_name):
    return [v for v in out["violations"] if v["check"] == check_name]


def t_pause_with_no_end_found():
    """2026-11-15..17: a pause held 49.3 h. Planted (no tick ends a pause, a record with no end of its own at 2 h):
    the sweep reports PAUSE_PAST_END and the pause stands to the run's end; on the shipped code it ends on time."""
    p, c = OUT["plant:pause_no_end"], OUT["ctrl:pause_no_end"]
    hits = found(p, "PAUSE_PAST_END")
    held_h = ((p["measures"]["pause_late_s"]["worst"] or 0) + W.LS.DEFAULT_PAUSE_H * 3600) / 3600
    check("t_pause_with_no_end_found", bool(hits) and held_h >= 49.3 - 0.05 and not c["violations"],
          "planted: %d PAUSE_PAST_END, first at %s h, held %.1f h (the measured 49.3 h; %s); shipped: %d violation(s), %s"
          % (len(hits), hits[0]["h"] if hits else None, held_h, m(p, "pause_late_s"), len(c["violations"]),
             m(c, "pause_late_s")))


def t_one_refusal_repeated_found():
    """2026-11-23: Steve2 gave the same refusal 47 times in 11 h. Planted (an ending stops nothing): the sweep reports
    REPEAT on Steve2 and at least 47 equal refusals in a row in 11 h; on the shipped code no third equal refusal comes
    sooner than lane_stop.RETRY_S after the one before."""
    p, c = OUT["plant:repeat"], OUT["ctrl:repeat"]
    hits = [v for v in found(p, "REPEAT") if v["detail"]["game"] == "Steve2"]
    n = p["measures"]["same_refusals_max"]
    check("t_one_refusal_repeated_found", bool(hits) and n >= 47 and not found(c, "REPEAT"),
          "planted: %d REPEAT on Steve2, %d equal refusals in a row in 11 h (measured 47), %s; shipped: %d REPEAT, %s, "
          "%d in a row" % (len(hits), n, m(p, "repeat_gap_s"), len(found(c, "REPEAT")), m(c, "repeat_gap_s"),
                           c["measures"]["same_refusals_max"]))


def t_account_gate_refusing_every_launch_found():
    """2026-11-26: SteveDesktop's account gate refused every launch for 3.6 h (a run it could not end counted as live).
    Planted (the code before 44a3797f6e: no bound, no write-now stop): STUCK on SteveDesktop; shipped: it switches."""
    p, c = OUT["gate_plant"], OUT["gate"]
    if p.get("error") or c.get("error"):
        # whole lines, never a cut by characters: a cut lands inside a path whose length differs from clone to clone,
        # so ./publish could not match this red on origin/main (2026-11-27, RELAPSE_MATURATION_FIX_DIED_TWICE)
        err = [ln.strip() for ln in str(p.get("error") or c.get("error")).splitlines() if ln.strip()]
        check("t_account_gate_refusing_every_launch_found", False, "part C did not run: %s" % " | ".join(err[-3:]))
        return
    hits = [v for v in p["violations"] if v["detail"].get("machine") == "SteveDesktop"]
    sw = [s for s in c.get("switches") or [] if "SteveDesktop" in s]
    check("t_account_gate_refusing_every_launch_found",
          bool(hits) and p["refused_max_min"] > p["limit_min"] and not c["violations"] and bool(sw)
          and c["refused_max_min"] <= c["limit_min"],
          "planted: %d STUCK on SteveDesktop, refused %s min in a row (measured 216 min), limit %s min, %s gate reads; "
          "shipped: %d STUCK, refused %s min at most, limit %s min, %s gate reads, switch %s" % (
              len(hits), p["refused_max_min"], p["limit_min"], p["gate_reads"], len(c["violations"]),
              c["refused_max_min"], c["limit_min"], c["gate_reads"], sw))


def t_each_check_sees_its_fault():
    """Each check with no measured fault of its own is red on a planted one (mutate-your-checker)."""
    bad = []
    for name, (_reg, _plant, want) in sorted(W.MUTANTS.items()):
        hits = found(OUT["mut:" + name], want)
        print("  mutant %-13s -> %s: %d found" % (name, want, len(hits)))
        if not hits:
            bad.append(name)
    check("t_each_check_sees_its_fault", not bad, "%d mutant(s), not seen: %s" % (len(W.MUTANTS), bad or "none"))


def t_shipped_lane_sweeps_clean():
    """The shipped testq tick and fill code over every regime of the range: nothing stays in a state nothing ends."""
    names = [n for n, _r, _p in W.regions(QUICK)]
    bad = [(n, OUT[n]["violations"][:2]) for n in names if OUT[n]["violations"]]
    for k in ("pause_late_s", "stop_late_s", "running_stale_passes", "pending_free_passes", "ssh_mark_late_s"):
        vals = [OUT[n]["measures"][k] for n in names]
        ws = [v["worst"] for v in vals if v["worst"] is not None]
        print("  %-21s worst %s limit %s cases %d" % (k, max(ws) if ws else None, vals[0]["limit"],
                                                       sum(v["cases"] for v in vals)))
    gaps = [OUT[n]["measures"]["repeat_gap_s"] for n in names]
    gs = [g["worst"] for g in gaps if g["worst"] is not None]
    print("  %-21s worst %s limit %s cases %d (smallest gap: the stop's RETRY_S, one pass to admit, a 1-2 min "
          "refusal)" % ("repeat_gap_s", min(gs) if gs else None, gaps[0]["limit"], sum(g["cases"] for g in gaps)))
    done = sum(OUT[n]["measures"]["jobs_done"] for n in names)
    check("t_shipped_lane_sweeps_clean", not bad and done > 0,
          "%d regime(s), %d passes, %d jobs ended; violating: %s" % (
              len(names), sum(OUT[n]["passes"] for n in names), done, bad or "none"))


def main():
    t0 = time.time()
    cases = [("plant:" + k, reg, plant) for k, (reg, plant, _c) in W.PLANTED.items()]
    # the shipped control: long enough to pass the fault's own end (the pause's 2 h; the repeat's 11 h)
    cases += [("ctrl:" + k, dict(reg, hours=min(reg["hours"], 11)), None) for k, (reg, _p, _c) in W.PLANTED.items()]
    cases += [("mut:" + k, reg, plant) for k, (reg, plant, _c) in W.MUTANTS.items()]
    cases += [("gate", None, False), ("gate_plant", None, True)]
    cases += W.regions(QUICK)
    OUT.update(W.sweep_all(cases))
    for t in (t_pause_with_no_end_found, t_one_refusal_repeated_found, t_account_gate_refusing_every_launch_found,
              t_each_check_sees_its_fault, t_shipped_lane_sweeps_clean):
        try:
            t()
        except Exception as e:      # a test that cannot read its run is red, not skipped
            check(t.__name__, False, "%s: %s" % (type(e).__name__, e))
    for k in sorted(OUT, key=lambda k: -(OUT[k].get("seconds") or 0))[:3]:
        print("  slowest: %s %.1f s" % (k, OUT[k].get("seconds") or 0))
    print("%s: %d case(s) swept in %.1f s, %d failed%s" % (
        "FAIL" if FAILS else "PASS", len(cases), time.time() - t0, len(FAILS), (": " + ", ".join(FAILS)) if FAILS
        else "" + (" (BLIND: %s)" % ",".join(sorted(W.BLIND)) if W.BLIND else "")))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
