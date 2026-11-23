"""RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR, live look read: a dry pit floor draws darker at every doubling of
depth past 2 m, at the brightness RM_PitReliefMath.FloorBrightness promises.

Why a live row: the C# case PitRelief_floor_shade_draws_the_brightness_law proves the blend arithmetic; only the game shows
what the loaded DLL puts on the screen over the real floor terrain.

Scene: one 3x3 dry pit per depth in LADDER (notches of 0.5 m), one square apart, from --origin x,z (south-west corner), on
open unroofed ground in full daylight. Each pit is captured alone (rimworld/screenshot_cell_rect, 1 square of margin) and
ONLY ITS CENTRE SQUARE is measured (whole-square mean, 5 % inset): the centre has no face, no lip and no south band.

Rows, once with the Mod Setting "Pit relief: shadows and depth shading" off and once on (RM_NorthstarProofs.ProofPitRelief; the
script ends with it on, the shipped default):
  FLOOR_LADDER_EACH_DOUBLING_DARKER_relief_<off|on>  2 -> 4 -> 8 -> 16 m: each floor at least 10 % darker than the one before.
  FLOOR_LADDER_DRAWS_THE_LAW_relief_<off|on>         every depth's brightness against the 2 m floor's, beside the law read from
      the running game (jawa/static_call): FloorBrightness with the relief off, within 0.06 both ways; StepFloorBrightness with
      it on, at most 0.06 brighter (the relief casts the walls' shadow over the shade, so a floor may be darker than the law).
SITE (never PASS, never FAIL): not full daylight (glow < 0.95), a roof, a pit that did not dig, or the undug margin not at
least twice as bright as the 2 m floor (the camera does not see the scene). HARNESS: a refused call or a missing capture.
Exit 0 only when all four rows PASS; 1 on any FAIL; 2 otherwise. The pits are filled back in unless --keep.

## anti-guessing notes (Test Pilot sitting 2026-11-22, ArchBig, RM_TheRot stage map, noon)
  - RULED OUT: "the black tint quad does not blend, or draws under the floor" (MOD) -- the ladder's centre squares read red
    34.4 / 32.5 / 29.6 / 26.2 / 23.5 / 21.0 / 18.4 at 2 / 3 / 4 / 6 / 8 / 12 / 16 m, which is (1 - a) x 34.4 + a x 10 with
    a = the live FloorShade(d), within 0.6 at every depth: the game drew exactly the code, a blend toward (10, 8, 7).
  - RULED OUT: "ArchSmall ran a DLL without the shade" (SITE) -- the filing's own picture
    (design/specs/2026-11-22-stepped-pit-floor-look/img/captures_close_six_pits.png) reads 35.3 at 2 m, 28 at 6 m, 25 at 8 m.
  - TRUE (HARNESS): the filing's "one colour" (33.1 / 33.4 / 32.8 / 33.6) was a whole-floor mean of a square on a pit's SOUTH
    edge. A floor's south third carries a light band (45.6 where the middle third reads 27.4 and the north third 23.8, 8 m),
    so the 8 m south-east square averaged 32.3 beside an unbanded 4 m square at 33-34. Measure a centre square, never a rim one.
  - TRUE (MOD, fixed with this script): the shade colour was (10, 8, 7), not black, so over the dark deep floor it drew less
    than the law: 16 m at 0.535 of the 2 m floor (law 0.34), 3 m at 0.945 (law 0.871). FloorTint is now pure black.
  - rimworld/screenshot_cell_rect names its file by the wall-clock second: two captures in one second return ONE file (the
    first run of this script read 4 m and 8 m as the same 29.6 / 22.1 / 15.1). Each capture here has its own fileName, waits
    for the file to stop growing, and refuses a file that is not this call's (name and age). Equal means are NOT a stale-file
    sign: the soil texture repeats every 16 squares, so two pits of one depth 16 squares apart read alike to 0.1.
  - capture_stepped_pits.py frames 4 squares east of its target where the camera's closest zoom is 11 (ArchBig): use
    rimworld/screenshot_cell_rect, which centres and crops by itself.

    python.exe src\\RimMandrake\\FlowWorks\\northstar\\pit_floor_ladder_live.py [<captures_dir>] [--origin 146,171] [--keep]
    ... --plant-flat   digs every pit 4 m deep and still claims the ladder: all four rows must FAIL (the check can go red).
The result is northstar/pit_floor_ladder_result_<stamp>.json, stamped by driver_stamp (mod hash + the loaded DLL), so
validation.py's chain pit_floor_ladder reads it only at the current mod hash. A --plant-flat result is stamped mode
'planted' and is never read as evidence.
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)

LADDER = [4, 6, 8, 16, 32]          # notches: 2, 3, 4, 8, 16 m
DOUBLINGS = [(4, 8), (8, 16), (16, 32)]
ITEM = "RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR"
PLAN = (
    ("ladder", ("FLOOR_LADDER_EACH_DOUBLING_DARKER_relief_off", "FLOOR_LADDER_DRAWS_THE_LAW_relief_off",
                "FLOOR_LADDER_EACH_DOUBLING_DARKER_relief_on", "FLOOR_LADDER_DRAWS_THE_LAW_relief_on")),
)
MATH = "RimMandrake.FlowWorks.RM_PitReliefMath"
PROOFS = "RimMandrake.FlowWorks.RM_NorthstarProofs"


def centre_mean(png):
    """Mean R, G, B of the centre square of a 5-square-wide capture (square cells from the width, centred vertically)."""
    from PIL import Image, ImageStat
    im = Image.open(png).convert("RGB")
    cw = im.size[0] / 5.0
    mid_y = im.size[1] / 2.0
    box = (int(2.05 * cw), int(mid_y - 0.45 * cw), int(2.95 * cw), int(mid_y + 0.45 * cw))
    edge = (int(0.1 * cw), int(mid_y - 0.45 * cw), int(0.6 * cw), int(mid_y + 0.45 * cw))
    return ImageStat.Stat(im.crop(box)).mean, ImageStat.Stat(im.crop(edge)).mean


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None, help="captures folder (default: the system temp folder)")
    ap.add_argument("--result-dir", default=HERE)
    ap.add_argument("--origin", default="146,171")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--plant-flat", action="store_true")
    a = ap.parse_args(argv)
    from rimbridge_client import RimBridge, resolve_endpoint
    import tempfile
    a.out = a.out or os.path.join(tempfile.gettempdir(), "pit_floor_ladder")
    os.makedirs(a.out, exist_ok=True)
    x0, z0 = [int(v) for v in a.origin.split(",")]
    stamp_s = time.strftime("%Y%m%dT%H%M%S")
    res = {"script": "pit_floor_ladder_live.py", "item": ITEM, "stamp": stamp_s, "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "origin": [x0, z0], "ladder": LADDER, "planted_flat": a.plant_flat, "verdicts": {}, "rows": [], "site": [],
           "harness": [], "captures": a.out}
    h, p, t = resolve_endpoint()
    with RimBridge(h, p, t) as B:
        c = lambda name, **kw: B.call(name, kw, check=False)
        import driver_stamp  # noqa: E402  (mode/mod_hash/env: what validation.py checks before it reads this result)
        driver_stamp.stamp(res, c)
        if a.plant_flat:
            res["mode"] = "planted"     # a planted fault's FAIL rows are the check's own red, never evidence about the mod
        w = len(LADDER) * 4 + 1
        rr = "%d,%d,%d,%d" % (x0 - 1, z0 - 1, w, 5)

        def fill():
            ex = c("jawa/flowworks_excavation_rect", x=x0 - 1, z=z0 - 1, w=w, h=5, onlyNonZero=True, includeTerrain=False)
            for q in ex.get("rows") or []:
                if q.get("isExcavated"):
                    c("jawa/flowworks_excavation_drive", x=q["x"], z=q["z"], deepenLevels=0, setBodyWaterM=0.0, fillInLevels=int(q.get("d") or 0))
        fill()
        if (c("jawa/list_pawns", rect=rr, limit=5).get("returned") or 0) > 0:
            res["site"].append("a pawn stands in the strip " + rr)
        c("jawa/destroy_batch", rects=rr, categories="All")
        c("jawa/set_terrain_batch", ops="Soil:" + rr)
        c("jawa/set_fog", action="unfog", rect=rr)
        c("jawa/set_roof_batch", ops="None:" + rr)
        for i, d in enumerate(LADDER):
            for dx in range(3):
                for dz in range(3):
                    r = c("jawa/flowworks_excavation_drive", x=x0 + i * 4 + dx, z=z0 + dz, deepenLevels=8 if a.plant_flat else d, setBodyWaterM=-1)
                    if not r.get("success", True):
                        res["harness"].append("dig refused at d=%d: %s" % (d, str(r.get("message"))[:120]))
        rb = c("jawa/flowworks_excavation_rect", x=x0, z=z0 + 1, w=w - 1, h=1, onlyNonZero=True, includeTerrain=False)
        got = {q["x"]: q.get("d") for q in rb.get("rows") or []}
        res["dug"] = [got.get(x0 + i * 4 + 1) for i in range(len(LADDER))]
        if not a.plant_flat and res["dug"] != LADDER:
            res["site"].append("the pits did not dig to the ladder: %s" % res["dug"])
        g = c("jawa/glow_at", cells="%d,%d" % (x0 + 1, z0 + 1))
        cell = (g.get("cells") or [{}])[0]
        res["light"] = {"hour": g.get("hour"), "skyGlow": g.get("skyGlow"), "groundGlow": cell.get("groundGlow"), "roofed": cell.get("roofed")}
        if not (float(cell.get("groundGlow") or 0) >= 0.95) or cell.get("roofed"):
            res["site"].append("not full open daylight: %s" % res["light"])
        laws = {}
        for mode, method in (("off", "FloorBrightness"), ("on", "StepFloorBrightness")):
            laws[mode] = {}
            for d in LADDER:
                r = c("jawa/static_call", type=MATH, method=method, args=str(d))
                try:
                    laws[mode][d] = float(r.get("result"))
                except (TypeError, ValueError):
                    res["harness"].append("%s(%d) not read: %s" % (method, d, str(r.get("message"))[:120]))
        c("jawa/clear_ui", all=True)
        c("rimworld/set_camera_zoom", rootSize=11)
        stamp, seen, soil = int(time.time()), {}, {}
        for mode in ("off", "on"):          # ends on, the shipped default
            r = c("jawa/static_call", type=PROOFS, method="ProofPitRelief", args=mode)
            if ("setting=%s" % (mode == "on")) not in str(r.get("result")):
                res["harness"].append("ProofPitRelief %s answered %s" % (mode, str(r.get("result") or r.get("message"))[:120]))
                continue
            time.sleep(1.0)
            seen[mode] = {}
            for i, d in enumerate(LADDER):
                # a name of its own: the tool's default name is the wall-clock second, and two captures in one second share a file
                name = "pitladder_%d_%s_d%02d" % (stamp, mode, d)
                asked = time.time()
                r = c("rimworld/screenshot_cell_rect", x=x0 + i * 4, z=z0, width=3, height=3, paddingCells=1, fileName=name, suppressMessage=True)
                src = str(r.get("path") or "")
                size = -1
                for _ in range(30):
                    now = os.path.getsize(src) if src and os.path.isfile(src) else -1
                    if now > 0 and now == size:
                        break
                    size = now
                    time.sleep(0.4)
                if not (src and os.path.isfile(src)):
                    res["harness"].append("no capture for %s d=%d: %s" % (mode, d, str(r.get("message"))[:120]))
                    continue
                if name not in os.path.basename(src) or os.path.getmtime(src) < asked - 2:
                    res["harness"].append("the capture for %s d=%d is not this call's file: %s" % (mode, d, os.path.basename(src)))
                    continue
                dst = os.path.join(a.out, "ladder_%s_d%02d.png" % (mode, d))
                shutil.copyfile(src, dst)
                m, edge = centre_mean(dst)
                seen[mode][d] = sum(m) / 3.0
                soil[mode] = sum(edge) / 3.0 if d == 4 else soil.get(mode)
                res.setdefault("drawn_rgb", {}).setdefault(mode, {})[d] = [round(v, 1) for v in m]
        if not a.keep:
            fill()
    for mode in ("off", "on"):
        lum, law = seen.get(mode) or {}, laws.get(mode) or {}
        k1, k2 = "FLOOR_LADDER_EACH_DOUBLING_DARKER_relief_" + mode, "FLOOR_LADDER_DRAWS_THE_LAW_relief_" + mode
        site = list(res["site"])
        if 4 in lum and soil.get(mode) is not None and soil[mode] < 2.0 * lum[4]:
            site.append("the undug margin is not twice as bright as the 2 m floor: the camera does not see the scene")
            res["site"] = site
        if len(lum) == len(LADDER) and len(law) == len(LADDER) and not res["harness"] and not site:
            steps = {"%d->%d" % (s, e): round(1 - lum[e] / lum[s], 3) for s, e in DOUBLINGS}
            res["verdicts"][k1] = {"verdict": "PASS" if all(v >= 0.10 for v in steps.values()) else "FAIL", "darker": steps}
            ratio = {d: [round(lum[d] / lum[4], 3), round(law[d] / law[4], 3)] for d in LADDER}
            # relief off: the shade alone, both ways. Relief on: a cast shadow lies over the shade, so the floor may only be darker.
            ok = all((v[0] - v[1]) <= 0.06 and (mode == "on" or (v[1] - v[0]) <= 0.06) for v in ratio.values())
            res["verdicts"][k2] = {"verdict": "PASS" if ok else "FAIL", "drawn_vs_law": ratio}
        else:
            why = "HARNESS" if res["harness"] else "SITE"
            res["verdicts"][k1] = {"verdict": "UNMEASURED", "class": why}
            res["verdicts"][k2] = {"verdict": "UNMEASURED", "class": why}
    for rid in PLAN[0][1]:
        v = res["verdicts"].get(rid) or {"verdict": "UNMEASURED", "class": "HARNESS"}
        det = {k: v[k] for k in v if k not in ("verdict", "class")}
        if v["verdict"] == "UNMEASURED":
            det = {"why": (res["harness"] or res["site"] or ["not reached"])[:3]}
        res["rows"].append({"id": rid, "status": v["verdict"], "class": v.get("class") or ("MOD" if v["verdict"] == "FAIL" else ""),
                            "item": ITEM, "detail": json.dumps(det)})
    os.makedirs(a.result_dir, exist_ok=True)
    out = os.path.join(a.result_dir, "pit_floor_ladder_result_%s%s.json" % (stamp_s, "_planted" if a.plant_flat else ""))
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    vs = [r["verdict"] for r in res["verdicts"].values()]
    print(json.dumps({k: res.get(k) for k in ("verdicts", "light", "dug", "site", "harness")}, default=str))
    print("RESULT", out)
    print("VERDICT", "PASS" if all(v == "PASS" for v in vs) else "FAIL" if "FAIL" in vs else "UNMEASURED")
    return 0 if all(v == "PASS" for v in vs) else 1 if "FAIL" in vs else 2


if __name__ == "__main__":
    sys.exit(main())
