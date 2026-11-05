"""LIVE_SESSION_FIX_B1_NEEDS_PRISTINE_MAP: live_session B1 (validation_v2 --live --current-map) on a map it cannot measure
reads UNMEASURED/SITE, never FAIL or ABORT FAIL; a non-colonist standing in a plot is evicted, not a refusal.
Driver 7 evidence: ls_c1 (a kept RM_Shambles in a plot -> L4 FAIL + ABORT FAIL), ls_c1b (B1 rerun on ls_c1's dug map ->
L1 FAIL + ABORT FAIL). Proof: B1 run twice back to back on ONE mock map.
    python3 src/RimMandrake/FlowWorks/northstar/selftest_b1_pristine_map.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation_v2 as V  # noqa: E402

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class A(object):
    mock, fresh_map, current_map, reset_settings, progress, max_job_ticks = True, False, True, False, None, 6000
    fault = []


def quiet_run(B):
    with open(os.devnull, "w") as dn:
        so, sys.stdout = sys.stdout, dn
        try:
            return V.run_live(A, B=B)
        finally:
            sys.stdout = so


def rows(res):
    return {r["id"]: (r["status"], r["cls"]) for r in res["rows"]}


def failed(res):
    return [(r["id"], r["detail"][:120]) for r in res["rows"] if r["status"] == "FAIL" and r["id"] not in V.KNOWN_MOD_RED]


def main():
    x, z, w, h = V.site_rects()[0]
    # the clean mock's own non-PASS rows (whatever the mock cannot model today) are the baseline: a stray must add none
    base = set(f[0] for f in failed(quiet_run(V.MockBridge())))
    # run 1: a non-colonist the sweep leaves (kept on --current-map) stands in a plot -> evicted, the run is measured
    B = V.MockBridge()
    B.pawns.append(dict(id="Thing_RM_Shambles1", position=dict(x=x + 1, z=z + 1), intelligence="Animal"))
    r1 = quiet_run(B)
    st1 = rows(r1)
    extra = [f for f in failed(r1) if f[0] not in base]
    check(not extra, "run 1: no FAIL row beyond the clean mock's own %s (got %s)" % (sorted(base), extra[:3]))
    check(st1.get("L4_site_ready", ("?",))[0] == "PASS", "run 1: L4_site_ready PASS after evicting the stray (%s)"
          % (st1.get("L4_site_ready"),))
    check("ABORT" not in st1 and st1.get("L1_fresh_map", ("?",))[0] == "PASS", "run 1: no ABORT, L1 PASS")
    check(not any(p.get("id") == "Thing_RM_Shambles1" for p in B.pawns), "run 1: the stray left the map")
    # run 2, back to back on the SAME map: dug by run 1 -> UNMEASURED/SITE, never FAIL
    r2 = quiet_run(B)
    st2 = rows(r2)
    check(not failed(r2), "run 2: no FAIL row (got %s)" % failed(r2)[:3])
    check(st2.get("L1_fresh_map") == ("UNMEASURED", "SITE"), "run 2: L1_fresh_map UNMEASURED SITE (%s)" % (st2.get("L1_fresh_map"),))
    check(st2.get("ABORT") == ("UNMEASURED", "SITE"), "run 2: ABORT UNMEASURED SITE (%s)" % (st2.get("ABORT"),))
    check(not r2["green"], "run 2: not green (nothing was measured)")
    # a COLONIST in a plot is never evicted: the run refuses as UNMEASURED/SITE
    B3 = V.MockBridge()
    B3.pawns.append(dict(id="Thing_Human9", position=dict(x=x + 1, z=z + 1), isPlayer=True, intelligence="Humanlike"))
    r3 = quiet_run(B3)
    st3 = rows(r3)
    check(not failed(r3), "colonist in plot: no FAIL row (got %s)" % failed(r3)[:3])
    check(st3.get("L4_site_ready") == ("UNMEASURED", "SITE"), "colonist in plot: L4 UNMEASURED SITE (%s)" % (st3.get("L4_site_ready"),))
    check(st3.get("ABORT") == ("UNMEASURED", "SITE"), "colonist in plot: ABORT UNMEASURED SITE (%s)" % (st3.get("ABORT"),))
    check(any(p.get("id") == "Thing_Human9" for p in B3.pawns), "colonist in plot: the colonist was not removed")
    # abort classes: map preconditions are SITE; a harness or readback abort stays HARNESS (and FAILs)
    for msg, want in (("map size", "SITE"), ("raining at start: every 0-tick vector would carry rain", "SITE"),
                      ("site not pristine (a prior run dug this map)", "SITE"), ("site readback", "HARNESS"),
                      ("stale DLL: the running assembly is not the repo's", "HARNESS")):
        check(V.abort_class(msg) == want, "abort_class(%r) = %s" % (msg, want))
    # a real defect still FAILs: settings drift aborts HARNESS -> ABORT FAIL
    a = A()
    a.fault = ["settings_drift"]
    with open(os.devnull, "w") as dn:
        so, sys.stdout = sys.stdout, dn
        try:
            rd = V.run_live(a)
        finally:
            sys.stdout = so
    check(rows(rd).get("ABORT", ("?",))[0] == "FAIL", "settings_drift: ABORT still FAIL (%s)" % (rows(rd).get("ABORT"),))
    print("RESULT: %s" % ("PASS" if not FAILS else "FAIL %d" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
