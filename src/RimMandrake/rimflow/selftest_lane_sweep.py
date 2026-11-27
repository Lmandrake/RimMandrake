#!/usr/bin/env python3
"""selftest_lane_sweep.py - the offline sweep of the ticket lane and the work bundles (lane_sweep.py).

Item RIMMANDRAKE_BUILD_LANE_BUNDLE_SWEEP_FIVE_STUCK_STATES_SEEN; page design/specs/2026-11-27-lane-bundle-sweep/boundary.md
(each t_ function is one promise of it, by name). Each *_found test plants one stuck state that was measured live
(design/specs/2026-11-26-simulation-census/evidence.md, rank 2, and the FlowWorks bundle WB-mod-FlowWorks-20261126-113858)
and asserts that the sweep reports it; t_shipped_code_sweeps_clean asserts that the shipped code reports nothing. Every
test prints its worst value, its limit and how many cases it read. Offline: a fake clock, a scratch ledger and stores;
nothing launches, closes or publishes. Written before lane_sweep.py, and seen failing on a sweep that cannot see each
fault before it passed.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
FAILS = []


def chk(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def LS():
    import lane_sweep
    return lane_sweep


def seen(res, kind, regime):
    """-> the findings of `kind` in `regime`."""
    return [f for f in res["findings"] if f["kind"] == kind and f["regime"] == regime]


def found(name, regime, plant, kind):
    """One planted fault: the sweep of `regime` with `plant` reports a finding of `kind`, and the same regime on the
    shipped code reports none of that kind (so the finding is the plant's, not the regime's)."""
    S = LS()
    bad = S.sweep([regime], plant=plant)
    good = S.sweep([regime])
    hit, clean = seen(bad, kind, regime), seen(good, kind, regime)
    print("     %s: planted %s: %d finding(s) of %s; worst %s, limit %s, cases %d; shipped: %d of that kind, cases %d"
          % (name, plant, len(hit), kind, bad["worst"], bad["limit"], bad["cases"], len(clean), good["cases"]))
    for f in hit[:2]:
        print("       %s" % S.line(f))
    chk(bool(hit), "%s: the sweep reports the planted %s (%s in regime %s)" % (name, plant, kind, regime))
    chk(not clean, "%s: the shipped code shows no %s in regime %s" % (name, kind, regime))
    chk(bad["cases"] > 0 and good["cases"] > 0, "%s: the sweep read cases (%d planted, %d shipped)" % (
        name, bad["cases"], good["cases"]))


def t_block_on_a_finished_ticket_found():
    """evidence rank 2: a block whose predecessor was already closed held 16 h. Plant: block_facts as it read before
    its fix (a closed predecessor still blocks)."""
    found("block on a finished ticket", "block", "block_on_done", "no_ender")


def t_chain_limit_with_no_next_step_found():
    """evidence rank 2: a ticket at the chain limit waited 39 h with no next step. Plant: the Conductor's stops view
    without its chain_stop row, so nobody is told and nothing grants the next run."""
    found("chain limit with no next step", "chain", "chain_no_row", "untold")


def t_load_line_hold_without_end_found():
    """evidence rank 2: the machine-load line held the lane 2.2 h, and nothing tells anyone when it does not fall.
    Plant: the Conductor's stops view without its machine_load notice."""
    found("load-line hold without end", "load_held", "load_no_row", "untold")


def t_bundle_member_rightly_left_open_restarts_found():
    """The FlowWorks bundle WB-mod-FlowWorks-20261126-113858 restarted 5 times, and the Conductor log said "5 of at
    most 3 today" (a daily limit that a bundle does not have). Plant: the continuation line as it read before."""
    found("bundle member rightly left open restarts", "bundle_left_open", "loc_old_line", "false_count")
    S = LS()
    res = S.sweep(["bundle_left_open"])
    b = res["bundles"].get("bundle_left_open") or []
    ends = [x.get("state") for x in b]
    restarts = max([int(x.get("restarts") or 0) for x in b] or [0])
    print("     bundles %s, restarts %d (5 members end one per run, the 6th stays rightly LEFT OPEN)" % (ends, restarts))
    chk(restarts == 5, "bundle member rightly left open: the bundle restarts once per run that ends a member (%d of 5)"
        % restarts)
    chk(ends and ends[-1] == "raised", "bundle member rightly left open: the restart that ends none raises it to the "
        "Conductor (%s)" % (ends[-1] if ends else None))


def t_one_ticket_bundles_found():
    """The Workshop lane launched one bundle per ticket of one system (one-ticket bundles). Plant: system_of without
    the item table, so a ticket with no home of its own stops joining its parent's home."""
    found("one-ticket bundles", "home", "system_per_ticket", "split")


def t_shipped_code_sweeps_clean():
    S = LS()
    t0 = time.time()
    res = S.sweep(S.REGIMES)
    took = time.time() - t0
    print("     %d regime(s), %d case(s), %d finding(s); worst %s, limit %s (%s); %.1f s" % (
        len(S.REGIMES), res["cases"], len(res["findings"]), res["worst"], res["limit"], res.get("worst_at"), took))
    for f in res["findings"][:8]:
        print("       %s" % S.line(f))
    chk(not res["findings"], "shipped code: no ticket or bundle stays in a state that nothing ends (%d finding(s))"
        % len(res["findings"]))
    chk(res["cases"] >= 144 * len(S.REGIMES), "shipped code: every tick of every regime was read (%d cases)"
        % res["cases"])
    chk(set(S.REGIMES) >= {"idle", "block", "chain", "load_held", "load_burst", "bundle_left_open", "home", "death",
                           "refuse", "wait"}, "shipped code: the written range is swept (%s)" % ", ".join(S.REGIMES))


def main():
    for fn in (t_block_on_a_finished_ticket_found, t_chain_limit_with_no_next_step_found,
               t_load_line_hold_without_end_found, t_bundle_member_rightly_left_open_restarts_found,
               t_one_ticket_bundles_found, t_shipped_code_sweeps_clean):
        print("== " + fn.__name__)
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            chk(False, "%s raised %s: %s" % (fn.__name__, type(e).__name__, str(e)[:300]))
    print("FAIL %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
