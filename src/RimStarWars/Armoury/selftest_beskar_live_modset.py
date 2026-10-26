#!/usr/bin/env python3
"""Offline selftest: CANON_MATERIALS_BUILD_1 L7 holds on the mod set the owner actually runs
(BESKAR_FIX_DEEPDRILL_UNDER_LK_GATE).
    python3 src/RimStarWars/Armoury/selftest_beskar_live_modset.py [--patch PATH]

prove_canon_materials.beskar_check replays RSW_BeskarNeverReforged.xml twice: once with every donor loaded, once with
Outer Rim - Core alone (the 2026-10-26 load: no LK Mineable Resources, no KotOR donor). Outer Rim ships
OuterRim_Beskar deepCommonality 0.001 itself, and the zeroing op sat under the LK gate, so beskar stayed
deep-drillable. --patch runs against another copy (`git show <old>:...RSW_BeskarNeverReforged.xml` -> red).
A planted fixture defect proves the replay can see: a patch with no ops leaves both problems standing.
"""
import argparse
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prove_canon_materials as P  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch")
    a = ap.parse_args(argv)
    fails = []
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write("<Patch></Patch>")
    try:
        blind = P.beskar_check(f.name)
    finally:
        os.unlink(f.name)
    for want in ("OuterRim_Beskar still a deep-drill deposit with Outer Rim and no LK",
                 "OuterRim_Beskar smelts back to beskar with Outer Rim and no LK"):
        if want not in blind:
            fails.append("instrument blind: empty patch does not report %r (got %r)" % (want, blind))
    got = P.beskar_check(a.patch)
    fails += ["L7: " + g for g in got]
    if fails:
        print("FAIL (%d)" % len(fails))
        for m in fails:
            print("  - " + m)
        return 1
    print("OK: L7 beskar replay clean with all donors and with Outer Rim alone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
