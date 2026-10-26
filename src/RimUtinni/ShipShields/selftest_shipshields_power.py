#!/usr/bin/env python3
"""SHIELDGEN_DECIDE_INTERCEPT_UNPOWERED + SHIELDGEN_FIX_RECHARGE_UNPOWERED: source contract. Offline, no game.

The bubble (CompShieldGenerator, a CompProjectileInterceptor subclass) must block nothing and recharge nothing
while unpowered. Vanilla's Active getter has no power test and is not virtual, so the comp drives the base's
private `shutDown` field (which Active, CheckIntercept, absorption and the drawn bubble all read). This checks
the C# that does it, because nothing offline can run it:

  * the shutDown field is reached by AccessTools.FieldRefAccess<CompProjectileInterceptor, bool>("shutDown");
  * CompTick calls SyncPowerShutdown() BEFORE base.CompTick() (so a cut lands the same tick);
  * SyncPowerShutdown only clears a shutdown it set itself (unpoweredShutDown), and that flag is scribed;
  * a power cut never zeroes currentHitPoints (that would fire the collapse explosion);
  * HitPointsPerInterval still returns 0 unpowered (the recharge fix);
  * the built DLL carries the new member and its .srchash matches the source.

Sanity probe: each regex must MISS on a mutated copy of the source, or the check could not see a regression.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source", "CompShieldGenerator.cs")
DLL = os.path.join(HERE, "Assemblies", "RimMandrake.Utinni.ShipShields.dll")
SRCHASH = DLL + ".srchash"

CHECKS = [
    ("shutDown reached by FieldRefAccess",
     r'AccessTools\.FieldRefAccess<CompProjectileInterceptor,\s*bool>\("shutDown"\)'),
    ("CompTick syncs power before base.CompTick",
     r'void CompTick\(\)\s*\{\s*SyncPowerShutdown\(\);\s*base\.CompTick\(\);'),
    ("unpowered sets shutDown and remembers it",
     r'if \(!FieldPowered\)\s*\{\s*if \(!shutDown\)\s*\{\s*shutDown = true;\s*unpoweredShutDown = true;'),
    ("only its own shutdown is cleared",
     r'else if \(unpoweredShutDown\)\s*\{\s*shutDown = false;\s*unpoweredShutDown = false;'),
    ("own flag is scribed",
     r'Scribe_Values\.Look\(ref unpoweredShutDown, "unpoweredShutDown", false\)'),
    ("no recharge unpowered",
     r'power == null \|\| power\.PowerOn \? base\.HitPointsPerInterval : 0'),
]
FORBIDDEN = [
    ("a power cut must not zero hit points (collapse explosion is for forced collapse)",
     r'currentHitPoints\s*=\s*0\s*;'),
]


def check(text):
    bad = []
    for label, rx in CHECKS:
        if not re.search(rx, text):
            bad.append("missing: " + label)
    for label, rx in FORBIDDEN:
        if re.search(rx, text):
            bad.append("forbidden: " + label)
    return bad


def srchash_ok():
    if not os.path.exists(SRCHASH):
        return "no .srchash beside the DLL"
    with open(SRC, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    with open(SRCHASH, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2 and parts[1] == "CompShieldGenerator.cs":
                return None if parts[0] == h else "DLL built from a different CompShieldGenerator.cs (rebuild)"
    return "CompShieldGenerator.cs not listed in .srchash"


def main():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()
    fails = check(text)

    # Sanity: every check must be able to fail.
    mutants = [
        text.replace('"shutDown"', '"shutdown"'),
        text.replace("SyncPowerShutdown();\n            base.CompTick();", "base.CompTick();\n            SyncPowerShutdown();"),
        text.replace("unpoweredShutDown = true;", ""),
        text.replace("else if (unpoweredShutDown)", "else"),
        text.replace('"unpoweredShutDown", false', '"x", false'),
        text.replace("? base.HitPointsPerInterval : 0", "? base.HitPointsPerInterval : 1"),
        text + "\n// currentHitPoints = 0;\n",
    ]
    for i, m in enumerate(mutants):
        if m == text or not check(m):
            fails.append("sanity: mutant %d not detected (instrument blind)" % i)

    with open(DLL, "rb") as f:
        if b"unpoweredShutDown" not in f.read():
            fails.append("built DLL lacks unpoweredShutDown (not rebuilt)")
    err = srchash_ok()
    if err:
        fails.append(err)

    for x in fails:
        print("FAIL", x)
    if fails:
        return 1
    print("PASS selftest_shipshields_power: %d contract checks, %d mutants caught, DLL current" % (len(CHECKS) + len(FORBIDDEN), len(mutants)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
