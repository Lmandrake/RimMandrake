"""FW_PROOF_TOOLS_HARDEN_READ_GAPS A1: the running bridge's jawa/flowworks_excavation_rect rows carry `dl` (exact water,
decilitres) and `fluid` (the recorded FluidDef defName or null) -- the fields scenarios_map.verify_plots/soak and
review_map.visual_verdict now judge (GPT 4.5, 7.12). Read-only: one 4x4 rect at the map centre, nothing is changed.

  python.exe src/RimMandrake/bridgetools/prove_excavation_rect_fields.py

Exit 0: every row has both keys, dl is an int >= 0 and fluid is a string or null. Exit 1: a row lacks one (the deployed
JawaBench predates this item). Exit 2: no verdict (no game in Playing, the call failed).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402


def judge(reply):
    """(code, why) for one excavation_rect reply: 0 holds, 1 fields missing, 2 unmeasured."""
    if not (reply or {}).get("success"):
        return 2, "excavation_rect failed: %r" % (str(reply)[:300],)
    rows = reply.get("rows") or []
    if not rows:
        return 2, "excavation_rect returned no rows (onlyNonZero must be false)"
    for r in rows:
        if "dl" not in r or "fluid" not in r:
            return 1, "row %s,%s lacks dl/fluid: keys %s" % (r.get("x"), r.get("z"), sorted(r))
        if not isinstance(r["dl"], int) or isinstance(r["dl"], bool) or r["dl"] < 0:
            return 1, "row %s,%s dl=%r is not a non-negative int" % (r.get("x"), r.get("z"), r["dl"])
        if r["fluid"] is not None and not isinstance(r["fluid"], str):
            return 1, "row %s,%s fluid=%r is not a defName or null" % (r.get("x"), r.get("z"), r["fluid"])
    return 0, "%d rows, every one carries dl and fluid" % len(rows)


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
    code, why = judge(r)
    print(("PASS: " if code == 0 else "FAIL: " if code == 1 else "NO VERDICT: ") + why)
    return code


if __name__ == "__main__":
    sys.exit(main())
