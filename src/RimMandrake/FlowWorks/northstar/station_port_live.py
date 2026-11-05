#!/usr/bin/env python3
"""station_port_live.py -- live proof of HOSE_END_FIX_CELL_SHORT_OF_PORT A1: a hose laid to the cell beside a pumping
station's EAST side is drawn coupled on that side's port within the joint tolerance (0.05 cell).

Restages the S5 scene of bridge run 1e (stage36.py: Kludged and Repaired stations, a reel 8 cells east of each laid to
(x+2, z)) on the CURRENT map, then asks HoseProbe "joints" (HoseJointProbe, the joint_check measurement). Before the fix the
end lay loose: no free_port_end row was ever written for it, so a plain joint_check read clean. This proof therefore demands
the row: for each station, a free_port_end joint naming the station's def, ok, gap <= tolerance.

  python.exe src/RimMandrake/FlowWorks/northstar/station_port_live.py [--x0 X --z0 Z] [--out FILE.json]
Exit 0 = both stations' east ends couple and pass; 1 = any is missing or out of tolerance; 2 = the bridge never answered.
Writes things on the map (two stations, two reels; wipeExisting inside the build cells): use a quicktest map.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import joint_check as J  # noqa: E402

STATIONS = ("RM_PumpingStation_Kludged", "RM_PumpingStation_Repaired")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--x0", type=int, default=None, help="first station x (default: map centre - 12)")
    ap.add_argument("--z0", type=int, default=None, help="station z (default: map centre)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    B = J._bridge()

    def call(n, **kw):
        try:
            return B.call(n, kw) or {}
        except Exception as e:  # noqa: BLE001
            return {"success": False, "error": str(e)[:300]}

    x0, z0 = a.x0, a.z0
    if x0 is None or z0 is None:
        mi = call("jawa/map_info")
        cx, cz = mi.get("sizeX"), mi.get("sizeZ") or mi.get("sizeY")
        if not cx or not cz:
            print("UNMEASURED: map size unreadable (%s); pass --x0/--z0" % str(mi)[:200])
            return 2
        x0 = cx // 2 - 12 if x0 is None else x0
        z0 = cz // 2 if z0 is None else z0
    rows, report = [], {"stations": []}
    for i, d in enumerate(STATIONS):
        x, z = x0 + 12 * i, z0
        reel, end = (x + 8, z), (x + 2, z)
        r = call("jawa/build_batch", ops=";".join(["%s:%d,%d" % (d, x, z), "RM_HoseReel:%d,%d,3" % reel]),
                 faction="player", wipeExisting=True)
        lay = J._probe(B, "lay:%d,%d,%d,%d" % (reel + end))
        report["stations"].append({"def": d, "at": [x, z], "reel": list(reel), "end": list(end),
                                   "build": {k: r.get(k) for k in ("success", "placed", "failed")}, "lay": lay})
        print("BUILD %s at %d,%d: placed=%s failed=%s; LAY %s -> %s: %s" % (d, x, z, r.get("placed"), str(r.get("failed"))[:120],
                                                                          reel, end, str(lay)[:160]))
    call("rimworld/pause_game", pause=False)
    ans = J._probe(B, "joints", wait=60.0)
    report["joints"] = ans
    if not isinstance(ans, dict) or not ans.get("success"):
        print("UNMEASURED: joints probe did not answer: %s" % str(ans)[:200])
        return 2
    tol = float(ans.get("tolerance") or 0.05)
    ok_all = True
    for s in report["stations"]:
        d = s["def"]
        # the row of THIS station's east reel (its "at" is the reel's Position), naming the station: not any end of that def
        hits = [j for j in ans.get("joints") or [] if j.get("kind") == "free_port_end" and d in str(j.get("note"))
                and list(j.get("at") or []) == s["reel"]]
        good = [j for j in hits if j.get("ok") is True and float(j.get("gap") or 0) <= tol]
        s["free_port_end"] = hits
        ok = bool(good)
        ok_all &= ok
        rows.append(ok)
        print("%s  %s east end: %d free_port_end row(s) %s" % ("PASS" if ok else "FAIL", d, len(hits),
              "; ".join("gap %.3f ok %s at %s (%s)" % (float(j.get("gap") or 0), j.get("ok"), j.get("where"), j.get("note")) for j in hits)
              or "-- the end couples to nothing (the S5 defect)"))
    v, lines = J.judge(ans)
    print("joint_check on the map: %s (%s)" % (v, lines[0]))
    if a.out:
        with open(a.out, "w") as f:
            json.dump(report, f, indent=1)
    print("station_port_live: %s" % ("PASS" if ok_all else "FAIL"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
