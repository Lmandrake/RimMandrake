#!/usr/bin/env python3
"""x10_canal_fire_live.py -- run ONE row of validation_v2, X10 (`_x10_canal_fire`: a lit 1x6 tar run creeps, persists and
burns to a spent, ashed channel), on the clean calm site, without the rest of the v2 session (validation_v2 has no
per-step flag; its X phase reaches X10 only after phases A..J). Stage 6 check sc_canal_fire (FlowWorks 0.1.0 visit 1).

    python.exe src/RimMandrake/FlowWorks/northstar/x10_canal_fire_live.py --out <json>     (bridge held, minimal list)

The run's six cells are dug to D=1 here (v2's site prep digs them otherwise); every setting X10 forces is restored in
finally by Live.restore_settings. Exit 0 PASS, 1 FAIL, 2 UNMEASURED.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation_v2 as V2  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    import test_site_saves as TSS
    B = V2.RealBridge()
    L = V2.Live(B)
    res = {"script": __file__, "mode": "live", "started": time.time()}
    try:
        site = TSS.load_site(B.call, "calm")
        res["site"] = site
        if not site.get("verified"):
            L.row("X10_canal_fire", False, "SITE", "calm site did not load clean: %s" % site.get("problems"), status="UNMEASURED")
        else:
            for x, z in V2.SCENES["X_fire"]["cells"]:
                r = B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=V2.SCENES["X_fire"]["D"], setBodyWaterM=0.0)
                if not r.get("success"):
                    L.row("X10_canal_fire", False, "HARNESS", "dig (%d,%d): %r" % (x, z, r), status="UNMEASURED")
                    break
            else:
                V2._x10_canal_fire(L)
    except Exception as ex:                         # noqa: BLE001 - a crash is a row, never a pass
        L.row("X10_canal_fire", False, "HARNESS", "crash: %r" % ex, status="UNMEASURED")
    finally:
        try:
            L.restore_settings()
        except Exception as ex:                     # noqa: BLE001
            res["restore_error"] = repr(ex)
        res["rows"] = L.rows
        res["finished"] = time.time()
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
    st = [r["status"] for r in L.rows]
    return 1 if "FAIL" in st else (2 if (not st or "UNMEASURED" in st) else 0)


if __name__ == "__main__":
    sys.exit(main())
