#!/usr/bin/env python3
"""selftest_closure_scan.py - the shared [Tool] class's <>c must never name an optional mod's type.

1. Signature walker units on hand-made blobs (true positive and true negative).
2. On the built companion DLL (artifacts/, untracked - built by build.py):
   - JawaBenchTerrainTools and its <>c: ZERO optional-mod field types (the live failure of
     2026-10-13 was 8 GSS-typed fields there);
   - GssLambdaHome's <>c: MUST show the GSS-typed fields - the calibration that the scan can see
     what it is looking for, in the same DLL.
No DLL built yet = the DLL half is UNMEASURED, said aloud.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import closure_scan as cs  # noqa: E402

DLL = os.path.join(HERE, "artifacts", "BridgeTools", "JawaBench", "JawaBench.BridgeTools.dll")
fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


# FIELD GENERICINST CLASS TypeRef#5 2 args: CLASS TypeRef#9, BOOLEAN   (Func<X,bool>)
blob = bytes([0x06, 0x15, 0x12, (5 << 2) | 1, 0x02, 0x12, (9 << 2) | 1, 0x02])
check("generic delegate yields both TypeRefs", cs.field_type_tokens(blob) == [(1, 5), (1, 9)], cs.field_type_tokens(blob))
check("primitive field yields nothing", cs.field_type_tokens(bytes([0x06, 0x08])) == [])
check("szarray of class", cs.field_type_tokens(bytes([0x06, 0x1D, 0x12, (3 << 2) | 1])) == [(1, 3)])
two_byte = (300 << 2) | 1                       # compressed 2-byte token
check("2-byte compressed token", cs.field_type_tokens(bytes([0x06, 0x12, 0x80 | (two_byte >> 8), two_byte & 0xFF])) == [(1, 300)])
check("core assemblies are core", cs.is_core("UnityEngine.CoreModule") and cs.is_core("Assembly-CSharp") and cs.is_core("mscorlib"))
check("mod assemblies are optional", not cs.is_core("RimMandrakeGimmeSomeSlack") and not cs.is_core("RimMandrakeFlowWorks"))

if not os.path.exists(DLL):
    print("companion DLL not built (%s): the DLL half is UNMEASURED, not a pass or a fail" % DLL)
else:
    offenders, checked, owners = cs.scan(DLL)
    check("shared class saw fields (instrument not blind)", checked > 50 and owners >= 2, (checked, owners))
    check("shared class + <>c name no optional mod type", not offenders, offenders[:5])
    home, hchecked, _ = cs.scan(DLL, shared="GssLambdaHome")
    check("calibration: GssLambdaHome <>c DOES show GSS-typed fields",
          any(a == "RimMandrakeGimmeSomeSlack" for _, _, a, _ in home), (hchecked, home[:3]))

print("%d/%d checks failed" % (len(fails), len(fails)) if fails else "all checks passed")
sys.exit(1 if fails else 0)
