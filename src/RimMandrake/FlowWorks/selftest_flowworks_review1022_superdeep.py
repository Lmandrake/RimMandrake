#!/usr/bin/env python3
"""FlowWorks DIRTY-file review 2026-10-22 (superdeep helper), fixed offline (no game). Each check reads FlowWorks source and
fails on the pre-fix code; each carries a planted regression that must fail (can-fail).

RELATIVE_VETO_CLOSURE_AT_ENTRY: RM_SuperdeepTrap.RelativeVeto (the CanReach postfix's relative-rule veto, the default rule)
  ended in `() => g.JoinedByLadders(k, cs, cd, p)`. The lambda captures the PARAMETER p, so the compiler allocated its
  closure at method entry on every CanReach call, early returns included. The lambda now lives in VetoedWhole, reached only
  when both ends are judged; RelativeVeto's own body holds no lambda. The call-site pins of SelfTest/CliffMaskChecks.cs
  ("RM_PocketGridMath.ReachVetoedWhole(startPocket, ..., destWayIn," and "() => g.JoinedByLadders(k, cs, cd, p))") still hold.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
FAILS = []


def check(name, ok, detail=""):
    print("  %-5s %s %s" % ("ok" if ok else "FAIL", name, detail if not ok else ""))
    if not ok:
        FAILS.append(name)


def read(rel):
    return open(os.path.join(SRC, rel), encoding="utf-8").read()


def body_of(src, sig):
    i = src.index(sig)
    j = src.index("{", i)
    d = 0
    for k in range(j, len(src)):
        d += {"{": 1, "}": -1}.get(src[k], 0)
        if d == 0:
            return src[j:k + 1]
    raise ValueError(sig)


def collapse(s):
    return re.sub(r"\s+", " ", s)


def veto_problems(trap):
    """Empty when RelativeVeto allocates no closure at entry and the ladder-graph decision is still wired."""
    probs = []
    try:
        veto = body_of(trap, "public static bool RelativeVeto(")
    except ValueError:
        return ["RelativeVeto not found"]
    # strip // comments so prose never counts as a lambda
    code = "\n".join(line.split("//")[0] for line in veto.splitlines())
    if "=>" in code:
        probs.append("RelativeVeto holds a lambda (captures p: closure built at entry on every CanReach)")
    if "VetoedWhole(startPocket, startNarrow, startWayOut, destPocket, destNarrow, destWayIn, g, k, cs, cd, p)" not in collapse(code):
        probs.append("RelativeVeto does not decide through VetoedWhole")
    try:
        helper = collapse(body_of(trap, "private static bool VetoedWhole("))
    except ValueError:
        return probs + ["VetoedWhole not found"]
    if "RM_PocketGridMath.ReachVetoedWhole(startPocket, startNarrow, startWayOut, destPocket, destNarrow, destWayIn, " \
            "() => g.JoinedByLadders(k, cs, cd, p))" not in helper:
        probs.append("VetoedWhole does not lift the veto through the ladder graph")
    flat = collapse(trap)
    # the C# call-site pins (SelfTest/CliffMaskChecks.cs) must keep matching
    if "RM_PocketGridMath.ReachVetoedWhole(startPocket, startNarrow, startWayOut, destPocket, destNarrow, destWayIn," not in flat \
            or "() => g.JoinedByLadders(k, cs, cd, p))" not in flat:
        probs.append("CliffMaskChecks call-site pins no longer match")
    return probs


def main():
    print("selftest_flowworks_review1022_superdeep")
    trap = read(os.path.join("Superdeep", "RM_SuperdeepTrap.cs"))
    p = veto_problems(trap)
    check("RelativeVeto_builds_no_closure_at_entry", not p, "; ".join(p))

    # planted regression: the pre-fix shape (lambda inline in RelativeVeto, no helper) must fail
    planted = trap.replace(
        "return VetoedWhole(startPocket, startNarrow, startWayOut, destPocket, destNarrow, destWayIn, g, k, cs, cd, p);",
        "return RM_PocketGridMath.ReachVetoedWhole(startPocket, startNarrow, startWayOut, destPocket, destNarrow, destWayIn,\n"
        "\t\t\t\t() => g.JoinedByLadders(k, cs, cd, p));", 1)
    check("can-fail: inline lambda in RelativeVeto is caught", planted != trap and bool(veto_problems(planted)))
    # planted regression: the helper dropping the ladder graph must fail
    planted2 = trap.replace("() => g.JoinedByLadders(k, cs, cd, p));", "() => false);", 1)
    check("can-fail: helper without the ladder graph is caught", planted2 != trap and bool(veto_problems(planted2)))

    if FAILS:
        print("FAILED: %d" % len(FAILS))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
