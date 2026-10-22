#!/usr/bin/env python3
"""Offline code review of the liquid net, 2026-10-22. Each check reads FlowWorks source and fails on the pre-fix code; each
carries a planted regression that must fail (can-fail).

OUTSIDE_ORIGIN_STORE_STALE_AFTER_MOVE: an outside consumer (LuminousPigment's glow tank, kind None) gets a touch store
  (OriginTanks via TouchesTanks), and RM_NetComponents.StoreOf caches it per topology revision. Its own despawn never bumped
  the revision (ChangesTopology is false for kind None), so a glow tank reinstalled elsewhere kept drawing from the tanks it
  used to touch until some unrelated pipe/tank/machine changed. Store() now records such origins, Bump() clears the record,
  and the Building.DeSpawn postfix bumps when the despawning thing is a recorded outside origin.
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


def outside_origin_ok(src):
    """True when the outside-origin staleness fix is in place in RM_LiquidNet.cs text."""
    try:
        store = body_of(src, "public static RM_NetResult Store(Thing origin)")
        bump = body_of(src, "public static void Bump(Map map)")
        probe = body_of(src, "internal static bool IsOutsideOrigin(Map map, Thing t)")
        despawn_cls = body_of(src, "public static class RM_Patch_NetTopologyDespawn")
        despawn = body_of(despawn_cls, "public static void Postfix(")
    except ValueError:
        return False
    records = re.search(r"!ChangesTopology\(origin\)\)\s*\{[^}]*outsideOrigins\.Add\(origin\)", store) is not None
    # the record must be added AFTER Components() (which may bump and clear it via RM_HoseLinks.For)
    order = "Components(origin.Map)" in store and store.index("Components(origin.Map)") < store.find("outsideOrigins.Add")
    clears = "outsideOrigins.Clear()" in bump and "revision++" in bump
    looks = "outsideOrigins.Contains(t)" in probe
    bumps = re.search(r"else if \(RM_LiquidNet\.IsOutsideOrigin\(__state,\s*__instance\)\)\s*\{\s*RM_LiquidNet\.Bump\(__state\);", despawn) is not None
    return records and order and clears and looks and bumps


def test_outside_origin():
    src = read("Machinery/RM_LiquidNet.cs")
    check("outside origin: store recorded, bump clears, despawn bumps", outside_origin_ok(src))
    # planted regressions: each pre-fix shape must fail
    pre_despawn = re.sub(r"\s*else if \(RM_LiquidNet\.IsOutsideOrigin\(__state,\s*__instance\)\)\s*\{\s*RM_LiquidNet\.Bump\(__state\);\s*\}", "", src)
    check("planted: despawn without the outside-origin bump fails", not outside_origin_ok(pre_despawn))
    pre_store = src.replace("StateOf(origin.Map).outsideOrigins.Add(origin);", "")
    check("planted: store that never records fails", not outside_origin_ok(pre_store))
    pre_bump = src.replace("s.outsideOrigins.Clear();", "")
    check("planted: bump that never clears fails", not outside_origin_ok(pre_bump))


def test_touch_store_rule():
    # the kernel rule the fix depends on: an outside consumer (kind None) has a touch store; tank/pipe/theft-refused do not
    k = read("Machinery/RM_LiquidNetKernel.cs")
    m = re.search(r"TouchStoreFor\(RM_NetRole kind, RM_NetRole role\)\s*=>\s*([^;]+);", k)
    ok = m is not None and "role == RM_NetRole.Machine" in m.group(1) and "kind == RM_NetRole.None" in m.group(1)
    check("kernel: TouchStoreFor = Machine role or kind None", ok)


def main():
    print("selftest_flowworks_review1022_liquidnet")
    test_outside_origin()
    test_touch_store_rule()
    if FAILS:
        print("FAILED: %d (%s)" % (len(FAILS), ", ".join(FAILS)))
        return 1
    print("all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
