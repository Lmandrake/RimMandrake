#!/usr/bin/env python3
"""GSS_END_HEAPS_FIX_BYPASS_LOOP_BUDGET (GPT review FB_hose_gss_3.3): the long-run end heaps of CordLayer.AddLoops were
spliced without the target budget the ordinary loops honour. Static guard, runnable anywhere (no dotnet):

1. CordLayer.cs defines ONE budget predicate, OverBudget, charging a shape against target * 1.25;
2. the long-run end-heap branch (between `if (L > LongRun` and `int nloops`) calls it, and so do the ordinary loops;
3. the behavioural C# check EndHeapBudgetChecks.cs (45-cell cord, target 47, seeds 1..40, can-fail with target 200) is
   compiled by the GSS SelfTest csproj and run from Program.cs (python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py);
4. GssFuzz's length limit no longer excuses a long run 4 extra cells for its end heaps.

Can-fail: every check is also run against a copy of the source with the end-heap budget call removed (or the fuzz
allowance restored) and must then report a failure.

    python3 src/RimMandrake/Utils/selftest_gss_end_heap_budget.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
LAYER = os.path.join(REPO, "src", "RimMandrake", "_Shared", "SlackGeometry", "CordLayer.cs")
ST = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "Source", "SelfTest")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def layer_faults(text):
    bad = []
    if not re.search(r"static bool OverBudget\([^)]*\)\s*=>[^;]*target \* 1\.25", text):
        bad.append("no OverBudget predicate charging a shape against target * 1.25")
    m = re.search(r"if \(L > LongRun(.*?)int nloops", text, re.S)
    if not m:
        bad.append("long-run end-heap branch not found (if (L > LongRun ... int nloops)")
    elif not re.search(r"OverBudget\([^;]*target", m.group(1)):
        bad.append("the long-run end-heap branch places a heap without OverBudget(..., target ...)")
    tail = text[m.end():] if m else ""
    if not re.search(r"bool over = OverBudget\([^;]*target", tail):
        bad.append("the ordinary loops do not use the shared OverBudget predicate")
    return bad


def wiring_faults(csproj, program, fuzz, have_check):
    bad = []
    if not have_check:
        bad.append("EndHeapBudgetChecks.cs is missing")
    if '<Compile Include="EndHeapBudgetChecks.cs" />' not in csproj:
        bad.append("the SelfTest csproj does not compile EndHeapBudgetChecks.cs")
    if not re.search(r"^\s*EndHeapBudgetChecks\.Run\(\);", program, re.M):
        bad.append("Program.cs does not run EndHeapBudgetChecks")
    if "CordLayer.LongRun ? 4.0" in fuzz:
        bad.append("GssFuzz still allows a long run 4 extra cells for its end heaps")
    return bad


def main():
    text = read(LAYER)
    chk = os.path.join(ST, "EndHeapBudgetChecks.cs")
    have = os.path.exists(chk)
    csproj = read(os.path.join(ST, "RimMandrakeGimmeSomeSlack.SelfTest.csproj"))
    program = read(os.path.join(ST, "Program.cs"))
    fuzz = read(os.path.join(ST, "GssFuzz.cs"))
    fails = 0
    bad = layer_faults(text) + wiring_faults(csproj, program, fuzz, have)
    if have:
        ct = read(chk)
        for need in ("CordLayer.AddLoops", "worstRoomy > bar", "worstTight <= bar"):
            if need not in ct:
                bad.append("EndHeapBudgetChecks.cs lacks " + need)
    for b in bad:
        print("FAIL " + b)
    fails += len(bad)
    # can-fail probes
    m = re.search(r"if \(L > LongRun(.*?)int nloops", text, re.S)
    if m:
        branch = re.sub(r"[^\n]*OverBudget\([^\n]*\n", "", m.group(1))
        mutant = text[:m.start(1)] + branch + text[m.end(1):]
        ok = any("end-heap branch" in b for b in layer_faults(mutant))
        print(("ok" if ok else "FAIL") + " can-fail: removing the end-heap budget call is caught")
        fails += 0 if ok else 1
    ok = any("4 extra cells" in b for b in wiring_faults(csproj, program, fuzz + " CordLayer.LongRun ? 4.0", have))
    print(("ok" if ok else "FAIL") + " can-fail: restoring the fuzz long-run allowance is caught")
    fails += 0 if ok else 1
    print("gss end-heap budget: " + ("ok" if fails == 0 else "FAIL (%d)" % fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
