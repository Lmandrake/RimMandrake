"""WATER_DEPTH_RESKIN_HE_LOOKS_FIRST L3, live state read: the five wall looks by drop (0.5, 1, 1.5, 2, over 2 m) and the
floor bands past 2 m (2, 4, 8 m) are DIFFERENT pictures in the running game, not only in the SelfTest.

Why a live row: the SelfTest (WallFaces_five_looks_by_drop_to_over_2m, WallFaces_floor_bands_past_2m) proves the source;
only the game shows the DLL it actually loaded drawing the engine's own staged depths. An old deploy (ca3c9d4a: the face
arrays and FootDarkness saturate at D4 = 2 m) reads FAIL here while the SelfTest on the new source is green.

What it reads (every number comes from the running game):
  staging   RM_NorthstarProofs.ProofStageBasin "x;z;3;3;levels;fill;RM_Fluid_Water" (the engine's Deepen + TrySetDriverFill).
  depths    RM_WaterLookProofs.ProofWaterLook "x,z" -> hollow (notches) and waterM of a pit's north-west corner square and of
            its dry north neighbour (hollow 0: the full wall).
  faces     jawa/static_call RimMandrake.FlowWorks.RM_WallFaceMath ExposedDrop(hollow, northHollow, fillNotches) then
            NorthFaceHeight / SideFaceWidth of that drop, and FootDarkness(hollow): the very calls
            SectionLayer_RMExcavationWalls.Regenerate draws each face and floor with (RM_ExcavationWalls.cs: nd/wd/ed, h, Dark).
  This is a state read of the loaded DLL on live depths, not a pixel judge; a frame of the same site is for the human look (L4).

Plots (3x3 pits from --origin, default 40,52; 3 dry squares between pits; site rect origin-(2,2) .. +50 x 9):
  D1 x0 1 notch dry (0.5 m)  D2 x6 2 (1 m)  D3 x12 3 (1.5 m)  D4 x18 4 (2 m)  D5 x24 5 (2.5 m, the over-2 m look)
  WET x30 5 notches, fill 2 (water 1 m: the exposed drop is 3 = lip minus surface, so it draws D3's face, not D5's)
  FL4 x36 8 notches dry (4 m)   FL8 x42 16 notches dry (8 m)

Rows (criterion L3 of the item):
  L3_FIVE_WALL_LOOKS_BY_DROP  exposed drops read 1..5 on D1..D5 (and 3 on WET); the north face heights AND the side widths
                              strictly increase D1 < D2 < D3 < D4 < D5 (no two equal, none zero); WET's face equals D3's and
                              differs from D5's (the water covers the foot of the wall). FAIL/MOD when any two looks collapse.
  L3_FLOOR_BANDS_PAST_2M      FootDarkness strictly increases D1 < D2 < D3 < D4 (2 m) < FL4 (4 m) < FL8 (8 m). FAIL/MOD on a tie.
  LIES: a pit that did not dig to its notches, or a north neighbour that is not dry ground, is SITE (UNMEASURED), never FAIL;
  a missing proof type or a refused static call is HARNESS.
Exit 0 only when every asked row PASSes; 1 on any FAIL; 2 otherwise.
"""
import argparse
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
import validation_core as V  # noqa: E402
from water_looks_proof import parse, fnum, WLP, NPROOF, WATER_FLUID, METRES_PER_NOTCH  # noqa: E402

WFM = "RimMandrake.FlowWorks.RM_WallFaceMath"
ITEM = "WATER_DEPTH_RESKIN_HE_LOOKS_FIRST"
ROW_IDS = ["L3_FIVE_WALL_LOOKS_BY_DROP", "L3_FLOOR_BANDS_PAST_2M"]
# plot -> (x offset, notches, fill notches, expected exposed drop at the north wall)
PITS = {"D1": (0, 1, 0, 1), "D2": (6, 2, 0, 2), "D3": (12, 3, 0, 3), "D4": (18, 4, 0, 4), "D5": (24, 5, 0, 5),
        "WET": (30, 5, 2, 3), "FL4": (36, 8, 0, 8), "FL8": (42, 16, 0, 16)}
LOOKS = ["D1", "D2", "D3", "D4", "D5"]
FLOORS = ["D1", "D2", "D3", "D4", "FL4", "FL8"]
FILL_SLACK = 0.2                         # waterM / 0.5 must sit this close to a whole notch


def strictly_up(vals):
    return all(v is not None for v in vals) and all(b > a for a, b in zip(vals, vals[1:]))


def site_ok(reads):
    """reads: plot -> {"corner": kv, "north": kv, "fill": int|None}. -> list of SITE reasons (empty = staged as planned)."""
    bad = []
    for p, (_dx, levels, fill, _e) in PITS.items():
        r = reads.get(p) or {}
        c, n = r.get("corner") or {}, r.get("north") or {}
        if fnum(c, "hollow") != levels:
            bad.append("%s hollow %s != %d" % (p, c.get("hollow"), levels))
        if fnum(n, "hollow") not in (0.0,):
            bad.append("%s north neighbour hollow %s != 0" % (p, n.get("hollow")))
        if r.get("fill") != fill:
            bad.append("%s fill %s != %d" % (p, r.get("fill"), fill))
    return bad


def looks_verdict(m):
    """m: plot -> {"drop": int, "north": float, "side": float} from the live DLL. -> (status, cls, why)."""
    if any(p not in m or any(m[p].get(k) is None for k in ("drop", "north", "side")) for p in LOOKS + ["WET"]):
        return "UNMEASURED", "HARNESS", "a face read is missing"
    drops = [m[p]["drop"] for p in LOOKS]
    if drops != [1, 2, 3, 4, 5] or m["WET"]["drop"] != 3:
        return "FAIL", "MOD", "exposed drops %s, wet %s (want 1..5, wet 3 = lip minus surface)" % (drops, m["WET"]["drop"])
    north, side = [m[p]["north"] for p in LOOKS], [m[p]["side"] for p in LOOKS]
    if not (north[0] > 0 and strictly_up(north)):
        return "FAIL", "MOD", "north faces by drop %s do not all differ (strictly rising)" % north
    if not (side[0] > 0 and strictly_up(side)):
        return "FAIL", "MOD", "side faces by drop %s do not all differ (strictly rising)" % side
    if (m["WET"]["north"], m["WET"]["side"]) != (m["D3"]["north"], m["D3"]["side"]) or m["WET"]["north"] == m["D5"]["north"]:
        return "FAIL", "MOD", "wet pit face %s/%s, want D3's %s/%s and not D5's" % (
            m["WET"]["north"], m["WET"]["side"], m["D3"]["north"], m["D3"]["side"])
    return "PASS", "MOD", "five looks distinct"


def floors_verdict(dark):
    """dark: plot -> FootDarkness from the live DLL. -> (status, cls, why)."""
    vals = [dark.get(p) for p in FLOORS]
    if any(v is None for v in vals):
        return "UNMEASURED", "HARNESS", "a floor read is missing"
    if not strictly_up(vals):
        return "FAIL", "MOD", "floor darkness %s (0.5,1,1.5,2,4,8 m) has a tie or falls" % vals
    return "PASS", "MOD", "floor bands distinct"


def offline_gate():
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(HERE, "selftest_wall_faces_proof.py")], capture_output=True, text=True,
                       timeout=600)
    steps = {"selftest_wall_faces_proof": {"exit": r.returncode, "tail": r.stdout.strip().splitlines()[-1:]}}
    return {"red": [k for k, v in steps.items() if v["exit"]], "steps": steps}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,52")
    ap.add_argument("--only", default="", help="comma list of rows: " + ",".join(ROW_IDS))
    ap.add_argument("--offline-gate", action="store_true")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-faults", default="", help="comma list: " + ",".join(FakeBridge.FAULTS))
    a = ap.parse_args(argv)
    if a.offline_gate:
        g = offline_gate()
        print("GATE_JSON " + json.dumps(g))
        return 1 if g["red"] else 0
    only = [x.strip().upper() for x in a.only.split(",") if x.strip()] or list(ROW_IDS)
    if set(only) - set(ROW_IDS):
        ap.error("unknown --only row(s) %s" % ",".join(sorted(set(only) - set(ROW_IDS))))
    faults = [f for f in a.mock_faults.split(",") if f]
    if set(faults) - set(FakeBridge.FAULTS):
        ap.error("unknown --mock-faults %s" % ",".join(sorted(set(faults) - set(FakeBridge.FAULTS))))
    if a.mock:
        raw = FakeBridge(faults)
    else:
        import proof_hose as PH          # noqa: E402  (bridge-side imports only on a live run)
        raw = PH.PB()
    B = V.guard(raw)
    out = a.out or (os.path.join(tempfile.gettempdir(), "wall_faces_mock_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
                    if a.mock else os.path.join(HERE, "wall_faces_result_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    rows = []
    res = {"script": "wall_faces_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    if a.mock:
        res["mode"] = "mock"
    else:
        import driver_stamp
        driver_stamp.stamp(res, raw.call)

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        try:
            os.replace(out + ".tmp", out)
        except OSError:
            with open(out, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1, default=str)

    def row(rid, st, det, cls="MOD"):
        if rid not in only:
            return
        st, cls, det = V.PRE.judge(st, cls, det)
        if st == "FAIL" and cls != "MOD":
            st = "UNMEASURED"
        if a.mock:
            det = dict(det, mock=st)
            st = "SKIP"
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "criterion": "L3", "detail": det})
        print("%-30s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def all_rows(why, cls):
        for rid in only:
            row(rid, "UNMEASURED", {"why": why}, cls=cls)
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        return 2

    def look(arg):
        r = B.call("jawa/static_call", type=WLP, method="ProofWaterLook", args=arg, _answer=True) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        ok = r.get("success") is True and not txt.startswith("REFUSED")
        return (parse(txt) if ok else {}), txt

    def math(method, *args):
        r = B.call("jawa/static_call", type=WFM, method=method, args="|".join(str(int(x)) for x in args), _answer=True) or {}
        if r.get("success") is not True:
            return None
        try:
            return round(float(r.get("result")), 4)
        except (TypeError, ValueError):
            return None

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)        # noqa: E731
    xz = lambda c: "%d,%d" % c                   # noqa: E731

    ok = True if a.mock else V._wait_playing(B, leave_s=0)[0]
    if not ok:
        return all_rows("no game in Playing", "HARNESS")
    k0, t0 = look(xz(P(0, 0)))
    if not k0.get("cell"):
        return all_rows("%s.ProofWaterLook is not in the loaded FlowWorks: %s" % (WLP, t0[:160]), "HARNESS")
    if math("NorthFaceHeight", 1) is None:
        return all_rows("%s.NorthFaceHeight cannot be called through jawa/static_call" % WFM, "HARNESS")
    if not a.mock:
        rect = (max(ox - 2, 1), max(oz - 2, 1), 50, 9)
        res["site_calm"] = V.site_calm(B)
        B.call("jawa/kill_hostiles")
        site_rows = []
        with V.scope("site"):
            V.prepare_site(B, rect, site_rows, "wall_faces_site")
        bad = [r for r in site_rows if r.get("status") not in (None, "PASS")]
        if bad:
            return all_rows("site not prepared: %s" % json.dumps(bad[:3], default=str)[:300], "SITE")
    staged = {}
    with V.scope("stage"):
        for plot, (dx, levels, fill, _e) in PITS.items():
            x, z = P(dx, 0)
            r = B.call("jawa/static_call", type=NPROOF, method="ProofStageBasin",
                       args="%d;%d;3;3;%d;%d;%s" % (x, z, levels, fill, WATER_FLUID), _answer=True) or {}
            staged[plot] = parse(r.get("result") or "")
        r = B.call("rimworld/step_game_ticks", ticks=2, pauseFirst=True, timeoutMs=60000) or {}
    res["staged"] = staged
    reads, m, dark = {}, {}, {}
    for plot, (dx, levels, fill, _e) in PITS.items():
        c, _ = look(xz(P(dx, 2)))                # the north-west corner square
        n, _ = look(xz(P(dx, 3)))                # its north neighbour: dry ground
        w = fnum(c, "waterM")
        f = None if w is None else int(round(w / METRES_PER_NOTCH))
        if w is not None and abs(w / METRES_PER_NOTCH - f) > FILL_SLACK:
            f = None
        reads[plot] = {"corner": c, "north": n, "fill": f}
        h, nh = fnum(c, "hollow"), fnum(n, "hollow")
        if h is None or nh is None or f is None:
            continue
        drop = math("ExposedDrop", h, nh, f)
        drop = None if drop is None else int(drop)
        m[plot] = {"drop": drop, "north": None if drop is None else math("NorthFaceHeight", drop),
                   "side": None if drop is None else math("SideFaceWidth", drop)}
        dark[plot] = math("FootDarkness", h)
    res["reads"], res["faces"], res["floorDarkness"] = reads, m, dark
    bad = site_ok(reads)
    if bad:
        return all_rows("not staged as planned: %s" % "; ".join(bad[:6]), "SITE")
    st, cls, why = looks_verdict(m)
    row("L3_FIVE_WALL_LOOKS_BY_DROP", st, {"why": why, "faces": m}, cls=cls)
    st, cls, why = floors_verdict(dark)
    row("L3_FLOOR_BANDS_PAST_2M", st, {"why": why, "floorDarkness": dark}, cls=cls)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    if a.mock:
        bad = [r["id"] for r in rows if r["detail"].get("mock") != "PASS"]
        print("MOCK: wall faces: %d rows, mock verdicts not PASS: %s -> %s" % (len(rows), bad or "none", out))
        return 1 if any(r["detail"].get("mock") == "FAIL" for r in rows) else (2 if bad else 0)
    fails = [r for r in rows if r["status"] == "FAIL"]
    print("wall faces: %d rows, %d FAIL, %d not PASS -> %s" % (len(rows), len(fails), sum(r["status"] != "PASS" for r in rows), out))
    return 1 if fails else (2 if any(r["status"] != "PASS" for r in rows) else 0)


# ====================================================================== offline stand-in
class FakeBridge(object):
    """A small world model answering in ProofWaterLook / ProofStageBasin's line formats and RM_WallFaceMath's numbers (the
    68f76502 arrays). It proves the script's control flow and its MOD/SITE/HARNESS split only. Faults, one wrong thing each:
      old_deploy      RM_WaterLookProofs missing                         -> both rows UNMEASURED/HARNESS
      blind_math      RM_WallFaceMath cannot be static-called            -> both rows UNMEASURED/HARNESS
      no_dig          one pit (D5) refuses to deepen                     -> both rows UNMEASURED/SITE
      faces_saturate  MOD: the ca3c9d4a arrays, the face stops at D4     -> L3_FIVE_WALL_LOOKS_BY_DROP FAIL
      sides_flat      MOD: side faces one width whatever the drop        -> L3_FIVE_WALL_LOOKS_BY_DROP FAIL
      fill_ignored    MOD: the water does not cover the foot of the wall -> L3_FIVE_WALL_LOOKS_BY_DROP FAIL
      floor_saturate  MOD: the ca3c9d4a FootDarkness, 0.95 from D4 on    -> L3_FLOOR_BANDS_PAST_2M FAIL"""
    FAULTS = ("old_deploy", "blind_math", "no_dig", "faces_saturate", "sides_flat", "fill_ignored", "floor_saturate")
    NORTH = [0, 0.12, 0.23, 0.35, 0.50, 0.62]
    SIDE = [0, 0.06, 0.11, 0.17, 0.23, 0.29]

    def __init__(self, faults=()):
        self.f = set(faults)
        self.cells = {}                    # (x, z) -> [hollow notches, water metres]

    def _math(self, method, args):
        a = [int(v) for v in args.split("|")]
        north = self.NORTH[:5] if "faces_saturate" in self.f else self.NORTH
        side = self.SIDE[:5] if "faces_saturate" in self.f else self.SIDE
        if method == "ExposedDrop":
            drop = a[0] - a[1]
            return 0 if drop <= 0 else max(0, drop - (0 if "fill_ignored" in self.f else max(0, a[2])))
        if method in ("NorthFaceHeight", "SideFaceWidth"):
            arr = north if method == "NorthFaceHeight" else side
            if a[0] <= 0:
                return 0.0
            if method == "SideFaceWidth" and "sides_flat" in self.f:
                return 0.17
            return arr[min(a[0], len(arr) - 1)]
        if method == "FootDarkness":
            import math
            d = a[0]
            if d <= 0:
                return 0.0
            if d <= 3:
                return 0.35 + 0.15 * d
            if "floor_saturate" in self.f:
                return 0.95
            return min(0.95, 0.80 + 0.0375 * math.log(d - 2, 2))
        raise KeyError(method)

    def stage(self, arg):
        x, z, w, h, levels, fill, _fl = arg.split(";")
        x, z, w, h, levels, fill = (int(v) for v in (x, z, w, h, levels, fill))
        depth = levels - 1 if "no_dig" in self.f and levels == 5 and fill == 0 else levels
        for i in range(w):
            for j in range(h):
                self.cells[(x + i, z + j)] = [depth, min(fill, depth) * METRES_PER_NOTCH]
        return "BASIN cells=%d dug=%d filled=%d refused=0 maxDepth=%d" % (w * h, w * h if depth >= levels else 0, w * h, depth)

    def look(self, arg):
        x, z = (int(v) for v in arg.split(","))
        cell = self.cells.get((x, z))
        hollow, wm = cell if cell else (0, 0.0)
        return ("WATERLOOK cell=%d,%d terrain=Soil still=%s dug=%s hollow=%d waterM=%.4f dlPerMetre=2000 tint=0 tn=0 tw=0 key=0 "
                "watchKey=0 tintOn=True bandOn=True facesOn=True tintVisible=True bandVisible=True lookDirty=False") % (
            x, z, bool(cell and wm > 0), bool(cell), hollow, wm)

    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            if kw.get("type") == WLP:
                if "old_deploy" in self.f:
                    return {"success": False, "error": "Type not found: " + WLP}
                return {"success": True, "result": self.look(kw.get("args") or "")}
            if kw.get("type") == WFM:
                if "blind_math" in self.f:
                    return {"success": False, "error": "Type not found: " + WFM}
                return {"success": True, "result": str(self._math(kw.get("method"), kw.get("args") or ""))}  # ProbeRender: invariant text
            if kw.get("method") == "ProofStageBasin":
                return {"success": True, "result": self.stage(kw.get("args") or "")}
            return {"success": False, "error": "unknown"}
        return {"success": True}


if __name__ == "__main__":
    sys.exit(main())
