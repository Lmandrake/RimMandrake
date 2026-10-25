"""selftest_plot_unroof.py -- offline proof that extensions._prep_plot unroofs every cell it clears, before it clears them.

FILL_IN_FIXTURE_FIX_CRUSHES_COLONIST (owner, live 2026-10-25): the plots were carved out of mountain with the overhead
mountain left in place; it collapsed and crushed 8 fixture pawns on their first tick. A fake bridge records the calls of
one _prep_plot; the roof write must name None over the exact destroyed rect and come before destroy_batch, and a roof
write that does not read back must stop the chain UNMEASURED. Sanity: an unroofed rect smaller than the destroyed one,
or a roof write after the destroy, is reported (the checker can fail).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "Utils")
for _p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import extensions as EXT  # noqa: E402


class _T(object):
    anchor = (125, 125)

    def __init__(self, roof_reply=None):
        self.calls = []
        self.roof_reply = roof_reply or {"success": True}

    def _guard(self):
        return True

    def bridge_call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "jawa/static_call":
            return {"success": True, "result": "RESET cells=0 left=0"}
        if tool == "jawa/set_roof_batch":
            return self.roof_reply
        return {"success": True}


def order_probs(calls):
    """Why this call list leaves overhead roof over a cleared cell (empty when every destroyed rect was unroofed first)."""
    probs, unroofed = [], set()
    for tool, kw in calls:
        if tool == "jawa/set_roof_batch":
            ops = str(kw.get("ops", ""))
            if ops.startswith("None:"):
                unroofed.add(ops[len("None:"):])
        elif tool == "jawa/destroy_batch":
            if kw.get("rects") not in unroofed:
                probs.append("destroy_batch %s with its roof still on" % kw.get("rects"))
    if not any(tool == "jawa/destroy_batch" for tool, _ in calls):
        probs.append("no destroy_batch seen (instrument blind)")
    return probs


def main():
    probs = []
    t = _T()
    EXT._prep_plot(t, "G")
    probs += order_probs(t.calls)

    # a roof write that did not read back stops the chain UNMEASURED
    try:
        EXT._prep_plot(_T({"success": True, "cellsFailedVerify": 3}), "G")
        probs.append("a roof write with cellsFailedVerify=3 did not stop the plot")
    except EXT.ExpectationFailed as e:
        if not str(e).startswith("UNMEASURED"):
            probs.append("roof readback failure not UNMEASURED: %s" % e)

    # sanity: the checker sees a roof write after the destroy, and a too-small unroof rect
    late = [c for c in t.calls if c[0] != "jawa/set_roof_batch"] + [c for c in t.calls if c[0] == "jawa/set_roof_batch"]
    if not order_probs(late):
        probs.append("sanity: a roof write after destroy_batch was not caught")
    small = [("jawa/set_roof_batch", {"ops": "None:1,1,2,2"}) if c[0] == "jawa/set_roof_batch" else c for c in t.calls]
    if not order_probs(small):
        probs.append("sanity: an unroofed rect smaller than the destroyed one was not caught")

    print("selftest_plot_unroof: %s" % ("PASS" if not probs else "FAIL"))
    for p in probs:
        print("  - " + p)
    return 0 if not probs else 1


if __name__ == "__main__":
    sys.exit(main())
