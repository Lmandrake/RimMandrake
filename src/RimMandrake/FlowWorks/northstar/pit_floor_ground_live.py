"""RIMMANDRAKE_DARKEN_PIT_FLOOR_BELOW_GROUND_SLATE_DRAWS_BRIGHTER, live look read: a dry pit floor draws darker than the
ground the pit was dug in, on every ground a player digs in.

Why a live row: the depth tone (RM_PitReliefMath.StepK, "a multiplier on undug ground") is laid over ONE floor terrain
(RM_Channel_*, the gravel texture) whatever the ground is, so only the game shows the floor beside its real ground.

Scene: per ground in GROUNDS a 6-wide patch of that terrain with two dry 3x3 pits, 0.5 m and 2 m deep, from --origin x,z on
open unroofed ground in full daylight, pit relief on (the shipped default). Each pit is captured alone and ONLY ITS CENTRE
SQUARE is measured against the undug margin of the same capture (pit_floor_ladder_live.centre_mean).

Rows: FLOOR_DARKER_THAN_ITS_GROUND_<terrain>  both floors at least 10 % darker (grey mean) than their own ground.
SITE (never PASS, never FAIL): not full daylight, a roof, a pawn in the strip, a pit that did not dig, a ground that did not
lay. HARNESS: a refused call or a missing capture. Exit 0 only when every row PASSes; 1 on any FAIL; 2 otherwise.

## anti-guessing notes (Test Pilot sitting 2026-11-23, ArchBig, save RM_STEPPED_PIT_12_CASES, 14 h, build 81ee41df54)
  - TRUE (MOD): floor / ground grey at 0.5 m | 2 m: Soil .81 | .56, Gravel .82 | .58, Sand .59 | .40, Marble_Rough .66 | .49,
    Granite_Rough .89 | .73, SoilRich 1.00 | .74, MarshyTerrain .98 | .68, Mud 1.11 | .76, Slate_Rough 1.22 | .90. The floor
    draws 60-65 grey at 0.5 m and 42-46 at 2 m on EVERY ground: the tone is a multiplier on gravel, not on the ground.
  - RULED OUT: "the lifted ladder of 2026-11-23 caused the bright shallow floor" -- with the relief off (the old law) 0.5 m
    still reads Mud 1.04, Slate 1.14, Soil .77 (on: .81). The lift changed the 2 m floor: Slate .59 -> .90, Mud .44 -> .76.
  - RULED OUT: "the lifted Deep / Superdeep terrain colours show under water" -- a 4 m pit at 0 / 0.25 / 0.5 / 1 / 2 / 4 m of
    water reads (48,35,22) / (19,30,49) / (19,32,53) / (19,35,61) / (18,41,77) / (17,48,97): any water turns the floor blue.
  - jawa/sky_glow_set is overwritten on the next frame (its own note): a "night" capture made with it is a day capture. Night
    is jawa/time_set_ticks (design/specs/2026-11-23-pit-floor-depth-ladder/live_look.py).
  - The Soil, Gravel, Sand and Marble rows PASS on the build that fails Slate: the check can see both ways in one run.

    python.exe src\\RimMandrake\\FlowWorks\\northstar\\pit_floor_ground_live.py [<captures_dir>] [--origin 62,62] [--keep]
The result is northstar/pit_floor_ground_result_<stamp>.json, stamped by driver_stamp; FlowWorks' functional script reads it
(validation.py chain pit_floor_ground).
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))
for _p in (UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

GROUNDS = ["Soil", "SoilRich", "Sand", "Gravel", "MarshyTerrain", "Mud", "Slate_Rough", "Granite_Rough", "Marble_Rough"]
DEPTHS = [1, 4]                 # notches: 0.5 m and 2 m
DARKER = 0.10                   # the same step the ladder asks between doublings: under it two tones read as one at default zoom
ITEM = "RIMMANDRAKE_DARKEN_PIT_FLOOR_BELOW_GROUND_SLATE_DRAWS_BRIGHTER"
# a literal: validation.py reads PLAN with ast, never by import
PLAN = (
    ("grounds", ("FLOOR_DARKER_THAN_ITS_GROUND_Soil", "FLOOR_DARKER_THAN_ITS_GROUND_SoilRich", "FLOOR_DARKER_THAN_ITS_GROUND_Sand",
                 "FLOOR_DARKER_THAN_ITS_GROUND_Gravel", "FLOOR_DARKER_THAN_ITS_GROUND_MarshyTerrain", "FLOOR_DARKER_THAN_ITS_GROUND_Mud",
                 "FLOOR_DARKER_THAN_ITS_GROUND_Slate_Rough", "FLOOR_DARKER_THAN_ITS_GROUND_Granite_Rough",
                 "FLOOR_DARKER_THAN_ITS_GROUND_Marble_Rough")),
)
assert [r[len("FLOOR_DARKER_THAN_ITS_GROUND_"):] for r in PLAN[0][1]] == GROUNDS
PROOFS = "RimMandrake.FlowWorks.RM_NorthstarProofs"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None, help="captures folder (default: the system temp folder)")
    ap.add_argument("--result-dir", default=HERE)
    ap.add_argument("--origin", default="62,62")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args(argv)
    from rimbridge_client import RimBridge, resolve_endpoint
    from pit_floor_ladder_live import centre_mean
    import tempfile
    a.out = a.out or os.path.join(tempfile.gettempdir(), "pit_floor_ground")
    os.makedirs(a.out, exist_ok=True)
    x0, z0 = [int(v) for v in a.origin.split(",")]
    stamp_s = time.strftime("%Y%m%dT%H%M%S")
    res = {"script": "pit_floor_ground_live.py", "item": ITEM, "stamp": stamp_s, "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "origin": [x0, z0], "grounds": GROUNDS, "depths": DEPTHS, "verdicts": {}, "rows": [], "site": [], "harness": [],
           "captures": a.out, "seen": {}}
    h, p, t = resolve_endpoint()
    with RimBridge(h, p, t) as B:
        c = lambda name, **kw: B.call(name, kw, check=False)
        import driver_stamp  # noqa: E402
        driver_stamp.stamp(res, c)
        W, H = len(GROUNDS) * 6, len(DEPTHS) * 6
        rr = "%d,%d,%d,%d" % (x0 - 1, z0 - 1, W, H)

        def fill():
            ex = c("jawa/flowworks_excavation_rect", x=x0 - 1, z=z0 - 1, w=W, h=H, onlyNonZero=True, includeTerrain=False)
            for q in ex.get("rows") or []:
                if q.get("isExcavated"):
                    c("jawa/flowworks_excavation_drive", x=q["x"], z=q["z"], deepenLevels=0, setBodyWaterM=0.0, fillInLevels=int(q.get("d") or 0))
        fill()
        if (c("jawa/list_pawns", rect=rr, limit=5).get("returned") or 0) > 0:
            res["site"].append("a pawn stands in the strip " + rr)
        c("jawa/destroy_batch", rects=rr, categories="All")
        c("jawa/set_fog", action="unfog", rect=rr)
        c("jawa/set_roof_batch", ops="None:" + rr)
        for i, g in enumerate(GROUNDS):
            c("jawa/set_terrain_batch", ops="%s:%d,%d,%d,%d" % (g, x0 - 1 + i * 6, z0 - 1, 6, H))
            for j, d in enumerate(DEPTHS):
                for dx in range(3):
                    for dz in range(3):
                        r = c("jawa/flowworks_excavation_drive", x=x0 + i * 6 + dx, z=z0 + j * 6 + dz, deepenLevels=d, setBodyWaterM=-1)
                        if not r.get("success", True):
                            res["harness"].append("dig refused on %s d=%d: %s" % (g, d, str(r.get("message"))[:120]))
        gl = c("jawa/glow_at", cells="%d,%d" % (x0 + 1, z0 + 1))
        cell = (gl.get("cells") or [{}])[0]
        res["light"] = {"hour": gl.get("hour"), "skyGlow": gl.get("skyGlow"), "groundGlow": cell.get("groundGlow"), "roofed": cell.get("roofed")}
        if not (float(cell.get("groundGlow") or 0) >= 0.95) or cell.get("roofed"):
            res["site"].append("not full open daylight: %s" % res["light"])
        r = c("jawa/static_call", type=PROOFS, method="ProofPitRelief", args="on")
        if "setting=True" not in str(r.get("result")):
            res["harness"].append("ProofPitRelief on answered %s" % str(r.get("result") or r.get("message"))[:120])
        c("jawa/clear_ui", all=True)
        c("rimworld/set_camera_zoom", rootSize=11)
        time.sleep(1.0)
        stamp = int(time.time())
        for i, g in enumerate(GROUNDS):
            res["seen"][g] = {}
            for j, d in enumerate(DEPTHS):
                px, pz = x0 + i * 6, z0 + j * 6
                ex = c("jawa/flowworks_excavation_rect", x=px - 1, z=pz + 1, w=2, h=1, onlyNonZero=False, includeTerrain=True)
                at = {q.get("x"): q for q in ex.get("rows") or []}
                if (at.get(px) or {}).get("d") != d:
                    res["site"].append("%s: the pit did not dig to %d: %s" % (g, d, (at.get(px) or {}).get("d")))
                if (at.get(px - 1) or {}).get("terrain") != g:
                    res["site"].append("%s: the ground did not lay: %s" % (g, (at.get(px - 1) or {}).get("terrain")))
                name = "pitground_%d_%s_d%02d" % (stamp, g, d)     # a name of its own: see pit_floor_ladder_live's notes
                asked = time.time()
                r = c("rimworld/screenshot_cell_rect", x=px, z=pz, width=3, height=3, paddingCells=1, fileName=name, suppressMessage=True)
                src, size = str(r.get("path") or ""), -1
                for _ in range(30):
                    now = os.path.getsize(src) if src and os.path.isfile(src) else -1
                    if now > 0 and now == size:
                        break
                    size = now
                    time.sleep(0.4)
                if not (src and os.path.isfile(src)) or name not in os.path.basename(src) or os.path.getmtime(src) < asked - 2:
                    res["harness"].append("no capture of this call for %s d=%d: %s" % (g, d, str(r.get("message") or src)[:120]))
                    continue
                dst = os.path.join(a.out, "ground_%s_d%02d.png" % (g, d))
                shutil.copyfile(src, dst)
                m, edge, _sd = centre_mean(dst)
                res["seen"][g][d] = [round(sum(m) / 3.0, 1), round(sum(edge) / 3.0, 1)]
        if not a.keep:
            fill()
    for g in GROUNDS:
        rid, seen = "FLOOR_DARKER_THAN_ITS_GROUND_" + g, res["seen"].get(g) or {}
        mine = [s for s in res["site"] if s.startswith(g + ":") or ":" not in s.split(" ")[0]]
        if res["harness"] or mine or len(seen) != len(DEPTHS):
            res["verdicts"][rid] = {"verdict": "UNMEASURED", "class": "HARNESS" if res["harness"] else "SITE",
                                    "why": (res["harness"] or mine or ["not captured"])[:3]}
            continue
        ratio = {"%g m" % (d * 0.5): round(seen[d][0] / seen[d][1], 3) for d in DEPTHS}
        res["verdicts"][rid] = {"verdict": "PASS" if all(v <= 1.0 - DARKER for v in ratio.values()) else "FAIL",
                                "floor_over_ground": ratio, "floor_ground_grey": {str(d): seen[d] for d in DEPTHS}}
    for rid in PLAN[0][1]:
        v = res["verdicts"][rid]
        res["rows"].append({"id": rid, "status": v["verdict"], "class": v.get("class") or ("MOD" if v["verdict"] == "FAIL" else ""),
                            "item": ITEM, "detail": json.dumps({k: v[k] for k in v if k not in ("verdict", "class")})})
    os.makedirs(a.result_dir, exist_ok=True)
    out = os.path.join(a.result_dir, "pit_floor_ground_result_%s.json" % stamp_s)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    vs = [r["verdict"] for r in res["verdicts"].values()]
    for rid in PLAN[0][1]:
        print(rid, res["verdicts"][rid]["verdict"], res["verdicts"][rid].get("floor_over_ground") or res["verdicts"][rid].get("why"))
    print(json.dumps({k: res.get(k) for k in ("light", "site", "harness")}, default=str))
    print("RESULT", out)
    print("VERDICT", "PASS" if all(v == "PASS" for v in vs) else "FAIL" if "FAIL" in vs else "UNMEASURED")
    return 0 if all(v == "PASS" for v in vs) else 1 if "FAIL" in vs else 2


if __name__ == "__main__":
    sys.exit(main())
