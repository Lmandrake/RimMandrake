#!/usr/bin/env python3
"""FILLIN_PROOF_FIX_ORDER_NEVER_FILLS: the fill-in chains (toggle_fill_in, toggle_fill_in_displacement) against a mock bridge.

Live defect (J20261026T080819Z-17015d): the harness ordered a bare RM_FillInCanalJob (targetA only); on an unpaid pit the
RM_FillPaidCheck toil ends it at once, and the dug cell read D=7, not the D=1 the chain dug, so one fill-in could never
reach D=0 inside its budget. Holds here:
  - the order carries the staged gravel as targetB (a bare order is never sent);
  - a D=1 cell that fills to 0 PASSes, one that stays at 1 FAILs;
  - a cell that reads D != 1 before the order is UNMEASURED naming the depth (a fixture fault, not a mod FAIL), and no
    order is spent on it.
Exit 0 green, 1 red."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import selftest_extensions as S  # noqa: E402  (sets sys.path for modcheck)
import extensions as EXT  # noqa: E402


def _base(tool, p):
    if tool == "jawa/static_call" and p.get("method") == "ProofResetRect":
        return {"result": "RESET x left=0"}
    if tool == "jawa/spawn_pawn":
        return {"pawns": [{"id": "P1"}]}
    return {"success": True}


def _run(chain, pre_depth, post_depth):
    """Run `chain` with the target cell reading `pre_depth` until ordered and `post_depth` after.
    -> (verdicts, orders sent, UNMEASURED/FAIL messages)."""
    st, orders = {"ordered": False}, []

    def h(tl, p):
        if tl == "jawa/flowworks_job_probe":
            return S.FILLIN_OK[tl]
        g = S._gravel_mock(tl, p, orders)
        if g is not None:
            if tl == "jawa/ordered_job" and g.get("accepted"):
                st["ordered"] = True
            return g
        if tl == "jawa/flowworks_excavation_report":
            return {"success": True, "depth": post_depth if st["ordered"] else pre_depth, "fill": 1,
                    "isSourceCell": False, "overflowDestroyedTotal": 0.0}
        if tl == "jawa/flowworks_excavation_drive":
            return {"success": True, "depth": 1, "fill": 1}
        return _base(tl, p)

    return S._ext_run(EXT, chain, h), orders


def main():
    out = []
    for chain, comp in (("toggle_fill_in", "fill_in_on"), ("toggle_fill_in_displacement", "fill_in_displacement_on")):
        got, orders = _run(chain, 1, 0)
        if got.get(comp) != "PASS":
            out.append("%s/%s D=1 -> 0: %s, want PASS (%s)" % (chain, comp, got.get(comp), got))
        if not orders or any(o.get("targetBId") != "G1" for o in orders):
            out.append("%s: fill-in order without the staged gravel as targetB: %r" % (chain, orders))
        for pre in (7, 0, None):
            got, orders = _run(chain, pre, 0)
            if got.get(comp) != "UNMEASURED":
                out.append("%s/%s pre-order D=%r: %s, want UNMEASURED" % (chain, comp, pre, got.get(comp)))
            if orders:
                out.append("%s pre-order D=%r: an order was still sent: %r" % (chain, pre, orders))
    got, _ = _run("toggle_fill_in", 1, 1)
    if got.get("fill_in_on") != "FAIL":
        out.append("toggle_fill_in/fill_in_on D=1 that never fills: %s, want FAIL" % got.get("fill_in_on"))
    # the guard message names the depth it read (the live report said D=7; a reader must see it)
    try:
        class _T(object):
            def _guard(self):
                return True

            def bridge_call(self, tool, **p):
                return {"success": True, "depth": 7}
        EXT._expect_dug_one(_T(), (129, 131))
        out.append("_expect_dug_one passed a D=7 cell")
    except EXT.ExpectationFailed as e:
        if "D=7" not in str(e) or not str(e).startswith("UNMEASURED"):
            out.append("_expect_dug_one message does not say UNMEASURED with D=7: %s" % e)
    if out:
        print("selftest_fill_in_order: FAIL")
        for o in out:
            print("  - " + o)
        return 1
    print("selftest_fill_in_order: PASS -- 2 chains x (D=1 pass, D=7/0/None unmeasured, gravel targetB), never-fills FAIL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
