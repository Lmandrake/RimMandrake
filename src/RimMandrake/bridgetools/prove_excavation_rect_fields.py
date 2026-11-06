"""FW_PROOF_TOOLS_HARDEN_READ_GAPS A1: the running bridge's jawa/flowworks_excavation_rect rows carry `dl` (exact water,
decilitres) and `fluid` (the recorded FluidDef defName or null) -- the fields scenarios_map.verify_plots/soak and
review_map.visual_verdict now judge (GPT 4.5, 7.12). Read-only: one 4x4 rect at the map centre, nothing is changed.

  python.exe src/RimMandrake/bridgetools/prove_excavation_rect_fields.py

Exit 0: every row has dl (an int >= 0) and fluid (a string, null, or absent because the transport drops nulls --
proved per row by terrain also being absent and by an includeTerrain=true control carrying terrain). Exit 1: a row lacks one (the deployed
JawaBench predates this item). Exit 2: no verdict (no game in Playing, the call failed).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402


def judge(reply, control=None):
    """(code, why) for one excavation_rect reply (includeTerrain=false) and its control (same rect, includeTerrain=true).

    The RimBridge transport omits null-valued members, so a dry cell's `fluid: null` arrives as an absent key. An
    absent fluid counts as null ONLY when the reply proves nulls are dropped: `terrain` (null by construction at
    includeTerrain=false) is absent from that row too, and the control shows the same literal carries a terrain string
    on every row. A present `terrain: null` means nulls survive transport, so an absent fluid is then a missing field.
    dl is never null and is always required. 0 holds, 1 fields missing, 2 unmeasured."""
    if not (reply or {}).get("success"):
        return 2, "excavation_rect failed: %r" % (str(reply)[:300],)
    rows = reply.get("rows") or []
    if not rows:
        return 2, "excavation_rect returned no rows (onlyNonZero must be false)"
    absent_fluid = []
    for r in rows:
        if "dl" not in r:
            return 1, "row %s,%s lacks dl: keys %s" % (r.get("x"), r.get("z"), sorted(r))
        if not isinstance(r["dl"], int) or isinstance(r["dl"], bool) or r["dl"] < 0:
            return 1, "row %s,%s dl=%r is not a non-negative int" % (r.get("x"), r.get("z"), r["dl"])
        if "fluid" not in r:
            if "terrain" in r:
                return 1, "row %s,%s lacks fluid while terrain=%r is sent (nulls survive transport): keys %s" % (
                    r.get("x"), r.get("z"), r["terrain"], sorted(r))
            absent_fluid.append(r)
            continue
        if r["fluid"] is not None and not isinstance(r["fluid"], str):
            return 1, "row %s,%s fluid=%r is not a defName or null" % (r.get("x"), r.get("z"), r["fluid"])
    if absent_fluid:
        if not (control or {}).get("success"):
            return 2, "%d rows omit fluid (null-dropped?) and the includeTerrain=true control failed: %r" % (
                len(absent_fluid), str(control)[:200])
        crows = control.get("rows") or []
        if len(crows) != len(rows):
            return 2, "control returned %d rows, the read %d" % (len(crows), len(rows))
        for r in crows:
            if not isinstance(r.get("terrain"), str):
                return 1, "control row %s,%s carries no terrain string (keys %s): the row literal is not what the " \
                          "proof assumes, so an absent fluid cannot be read as null" % (r.get("x"), r.get("z"), sorted(r))
            if "dl" not in r:
                return 1, "control row %s,%s lacks dl: keys %s" % (r.get("x"), r.get("z"), sorted(r))
    wet = sum(1 for r in rows if isinstance(r.get("fluid"), str))
    return 0, "%d rows, every one carries dl and fluid (%d fluid null-dropped in transport, %d a defName)" % (
        len(rows), len(absent_fluid), wet)


def main():
    h, p, t = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=t, timeout=120)
    c.connect()
    mi = c.call("jawa/map_info", {}, check=False) or {}
    sx, sz = mi.get("sizeX"), mi.get("sizeZ")
    if not sx or not sz:
        print("NO VERDICT: no map (map_info %r)" % (str(mi)[:200],))
        return 2
    r = c.call("jawa/flowworks_excavation_rect", {"x": sx // 2, "z": sz // 2, "w": 4, "h": 4, "onlyNonZero": False,
                                                   "includeTerrain": False}, check=False)
    ctl = c.call("jawa/flowworks_excavation_rect", {"x": sx // 2, "z": sz // 2, "w": 4, "h": 4, "onlyNonZero": False,
                                                     "includeTerrain": True}, check=False)
    code, why = judge(r, ctl)
    print(("PASS: " if code == 0 else "FAIL: " if code == 1 else "NO VERDICT: ") + why)
    return code


if __name__ == "__main__":
    sys.exit(main())
