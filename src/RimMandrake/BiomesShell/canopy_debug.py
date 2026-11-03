#!/usr/bin/env python3
"""The canopy layer's debug script (CANOPY_LAYER_BUILD_ROOF_OF_THE_WORLD; every mod ships with its first script).

    python3 src/RimMandrake/BiomesShell/canopy_debug.py --offline     the offline proof: selftest_canopy.py (C1-C5)
    python.exe src/RimMandrake/BiomesShell/canopy_debug.py L1         live, far zoom: canopy drawn
    python.exe src/RimMandrake/BiomesShell/canopy_debug.py L2         live, near zoom: canopy not drawn, trunk shown
    python.exe src/RimMandrake/BiomesShell/canopy_debug.py state      live, read only: the numbers, no verdict

Live clauses go through jawa/static_call into RimMandrake.Biomes.RM_CanopyProof (Source/RM_Canopy.cs) on the
CURRENT map of a quicktest colony with Baroque Biomes loaded: Setup puts the camera on a canopy tree (spawning one
mature RM_SweetlineTree near the centre if the map has none) at a zoom that makes the canopy solid (L1) or hidden
(L2), the script waits for frames to draw, then Read returns PASS/FAIL with every number it rests on:
  L1 far   alpha 1, the tree's section printed >= 1 canopy, its boundary wider than the 17x17 section (a crown
           reaching past its section stays drawn: design §4.1), the layer drew in the last 30 frames, the plant's
           Graphic is the trunk pool.
  L2 near  alpha 0, the canopy is printed but not drawn for > 5 frames, the plant's Graphic is still the trunk pool.
Exit 0 = PASS, 1 = FAIL, 2 = UNMEASURED (bridge or game not reachable: an instrument failure, never a verdict).

Learned (write every live session's findings here, false theories included):
  * 2026-11-03 build: a colour mask cannot cut a trunk from the sweetline art (grey-green and gold crown, gold bark
    highlights); canopy_art.py cuts geometrically at the crown base instead.
  * 2026-11-03 build: defaults 14/4 px left a 1440p screen half-faded at vanilla's furthest zoom (12 px/cell); 18/5.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TYPE = "RimMandrake.Biomes.RM_CanopyProof"
ZOOM = {"L1": "far", "L2": "near"}
SETTLE_S = 2.0


def offline():
    r = subprocess.run([sys.executable, os.path.join(HERE, "selftest_canopy.py")])
    return r.returncode


def hook(c, method, args):
    r = c.call("jawa/static_call", {"type": TYPE, "method": method, "args": args})
    if not isinstance(r, dict) or r.get("success") is False:
        raise RuntimeError("static_call %s refused: %r" % (method, r))
    return str(r.get("result", ""))


def live(clause):
    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
    import rimbridge_client as rb  # noqa: E402
    try:
        h, p, tok = rb.resolve_endpoint()
        c = rb.RimBridge(host=h, port=p, token=tok, timeout=120.0)
        c.connect()
        if clause == "state":
            print("state " + hook(c, "Read", "current|far"))
            return 0
        zoom = ZOOM[clause]
        print("  setup: " + hook(c, "Setup", "current|" + zoom), flush=True)
        time.sleep(SETTLE_S)
        line = hook(c, "Read", "current|" + zoom)
    except Exception as e:  # noqa: BLE001 -- any bridge failure is an instrument error, never a verdict
        print("%s UNMEASURED: %s: %s" % (clause, type(e).__name__, e))
        return 2
    print("%s %s" % (clause, line))
    return 0 if line.startswith("PASS") else 1


def main(argv):
    if len(argv) != 2 or argv[1] not in ("--offline", "L1", "L2", "state"):
        print(__doc__)
        return 2
    return offline() if argv[1] == "--offline" else live(argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
