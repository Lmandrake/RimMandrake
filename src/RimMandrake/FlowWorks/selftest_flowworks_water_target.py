#!/usr/bin/env python3
"""selftest_flowworks_water_target.py — RIMMANDRAKE_MOCK_FLOWWORKS_WATER_BY_DEPTH_ON_REAL_GROUND, its acceptance test.

WHY: three reversals on the water look (11-12 too opaque, 11-13 great, 11-20 too transparent) had no written target.
The target is now written: design/concepts/FlowWorks/version/water_by_depth_target.json (the FIRM mockup, picked by a
naive taste judge on the Conductor's ruling). This test holds the shipped law to it:
  1. the target is the picture that was judged: water_mockup.law_firm hides and colours a mid grey as the target says
     at each listed depth;
  2. the model (model/underliquid.py, the twin of RM_UnderLiquid) hides what the target says at each listed depth, and
     its fresh-water body colour is the target's;
  3. the C# side: RM_UnderLiquid's defaults (shallow, deep, full metres, curve) and WaterColour/BodyGamma/Darken give
     the target, and the golden table the dotnet SelfTest checks Seen against holds a row at each listed depth equal to
     the target (UnderLiquid_seen_matches_the_offline_model);
  4. the range the game can produce, not only the listed depths: every clarity a LiquidDef ships (0, 0.25, 0.35, 0.45)
     and a 0.05 grid, depth 0 to 10 m by 1 cm, and the setting grid (shallow 0/0.2/0.35/0.6, deep 0.5/0.9/1, full
     1/4/10 m): seen stays in [0, 1], never clearer deeper, dry above the line, an opaque liquid hides at once, and a
     clear liquid hides at least its shallow strength and at most its deep strength. Left out: per-pixel drawing (a live
     look, Stage 6), waves (0.2.0).
  5. the effects (second pass, RIMMANDRAKE_RESEARCH_FLOWWORKS_WATER_LOOK_FIRM_ALREADY_PICKED: BLEND picked): the judged
     mockup's BLEND numbers are the target's; the model's wet ground, wet band and ripple light equal the target
     (ripple alpha at each listed depth); RM_UnderLiquid's literals equal them; and the drawers call them
     (RM_ExcavationWalls draws the wet tint and band, RM_LiquidSurface the ripple light). The judged pale waterline is
     removed (owner walk 2026-11-22, target "waterline.removed"): the model, the C# literals and the wall drawer carry
     none of it.
CAN IT FAIL: run in this file: the law shipped before this build (shallow 0), a pale body (Darken 0.3), a spliced golden
row, a C# shallow default of 0, a model with dry ground (wet darken 0), a C# ripple peak of 0.3 (RIPPLE's, refused), a
wall drawer that never calls the wet tint, a model / a C# file / a wall drawer that brings the pale waterline back must
each go RED.
    python3 src/RimMandrake/FlowWorks/selftest_flowworks_water_target.py
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TARGET = REPO / "design" / "concepts" / "FlowWorks" / "version" / "water_by_depth_target.json"
UL = HERE / "Source" / "Superdeep" / "RM_UnderLiquid.cs"
GOLD = HERE / "Source" / "SelfTest" / "UnderLiquidParityChecks.cs"
WALLS = HERE / "Source" / "Superdeep" / "RM_ExcavationWalls.cs"
SURFACE = HERE / "Source" / "RM_LiquidSurface.cs"
sys.path.insert(0, str(HERE / "model"))
sys.path.insert(0, str(HERE))
import underliquid as ul  # noqa: E402
import water_mockup as wm  # noqa: E402
from selftest_flowworks_underliquid_parity import cs_float, gold_rows_in, mask_comments  # noqa: E402

TOL = 5e-4          # the target file states hides to 4 places
COLOUR_TOL = 1.5e-3  # and colours to 3


def cs_water_colour(text):
    m = re.search(r"WaterColour\s*=\s*new\s+Float3\(\s*([0-9.]+)f\s*,\s*([0-9.]+)f\s*,\s*([0-9.]+)f\s*\)", text)
    return tuple(float(x) for x in m.groups()) if m else None


def cs_float3(text, name):
    m = re.search(name + r"\s*=\s*new\s+Float3\(\s*([0-9.]+)f\s*,\s*([0-9.]+)f\s*,\s*([0-9.]+)f\s*\)", text)
    return [float(x) for x in m.groups()] if m else None


def effects_checks(t, model, ul_cs, walls_cs, surface_cs):
    out = []
    e = t["effects"]
    wg, wb, rl = e["wet_ground"], e["wet_band"], e["ripple_light"]
    wl = e["waterline"]["judged"]  # history of the judged picture; the line itself is removed (e["waterline"]["removed"])
    gone = bool(e["waterline"].get("removed"))
    wl_names = ("WaterlineCells", "WaterlineAlpha", "WaterlineColour")
    near = lambda a, b, tol=1e-6: a is not None and b is not None and abs(a - b) <= tol
    nearv = lambda a, b, tol=1e-6: a is not None and b is not None and len(a) == len(b) and all(abs(x - y) <= tol for x, y in zip(a, b))
    # 5a. the judged picture: water_mockup's BLEND
    fx = wm.FX.get("BLEND", {})
    px = float(wm.PX)
    bad = [n for n, ok in (
        ("BLEND wet", fx.get("wet") is True), ("BLEND waterline", fx.get("waterline") is True),
        ("BLEND ripple peak", near(fx.get("ripple"), rl["peak"])),
        ("BLEND warp (judged)", near(fx.get("warp", 0) / px, e["bottom_distortion"]["judged_peak_cells"])),
        ("wet value", near(wm.WET_VALUE, 1 - wg["darken"])), ("wet saturation (judged)", near(wm.WET_SAT, wg["saturation_judged"])),
        ("band", near(wm.WET_BAND_PX / px, wb["cells"])), ("line", near(wm.WATERLINE_PX / px, wl["cells"])),
        ("line alpha", near(wm.WATERLINE_ALPHA, wl["alpha"])), ("line colour", nearv(list(map(float, wm.WATERLINE_COLOUR)), wl["colour"], 1e-6)),
        ("ripple colour", nearv(list(map(float, wm.RIPPLE_COLOUR)), rl["colour"])),
        ("ripple fade", all(near(float(wm.ripple_amp(1.0, d)), math.exp(-d / rl["fade_metres"]), 1e-5) for d in (0.2, 1.0, 2.0))),
    ) if not ok]
    out.append((f"5a the target's effects are the judged BLEND mockup's (12 read){': ' + ', '.join(bad) if bad else ''}", not bad))
    # 5b. the model
    g = lambda n: getattr(model, n, None)
    bad = [n for n, ok in (
        ("WET_DARKEN", near(g("WET_DARKEN"), wg["darken"])), ("WET_BAND_CELLS", near(g("WET_BAND_CELLS"), wb["cells"])),
        ("WET_BAND_DARKEN", near(g("WET_BAND_DARKEN"), wb["darken"])),
        ("waterline removed in the target", gone),
        *[(f"{n} still in the model (the waterline is removed)", g(n) is None)
          for n in ("WATERLINE_CELLS", "WATERLINE_ALPHA", "WATERLINE_COLOUR")],
        ("RIPPLE_PEAK", near(g("RIPPLE_PEAK"), rl["peak"])), ("RIPPLE_FADE_METRES", near(g("RIPPLE_FADE_METRES"), rl["fade_metres"])),
        ("RIPPLE_COLOUR", nearv(g("RIPPLE_COLOUR") and list(g("RIPPLE_COLOUR")), rl["colour"])),
    ) if not ok]
    w = 0.0
    if callable(g("ripple_alpha")):
        for k, v in rl["alpha_by_depth"].items():
            w = max(w, abs(model.ripple_alpha(float(k)) - v))
        if model.ripple_alpha(0.0) != 0.0 or model.ripple_alpha(-1.0) != 0.0:
            bad.append("ripple_alpha lights a dry floor")
    else:
        bad.append("ripple_alpha missing")
    out.append((f"5b model effects = target ({len(rl['alpha_by_depth'])} ripple depths, worst {w:.5f} limit {TOL})"
                + (f": {', '.join(bad)}" if bad else ""), not bad and w <= TOL))
    # 5c. the C# literals
    ulm = mask_comments(ul_cs)
    got = {n: cs_float(ulm, n) for n in ("DefaultWetDarken", "WetBandCells", "WetBandDarken",
                                          "DefaultRipplePeak", "RippleFadeMetres")}
    want = {"DefaultWetDarken": wg["darken"], "WetBandCells": wb["cells"], "WetBandDarken": wb["darken"],
            "DefaultRipplePeak": rl["peak"], "RippleFadeMetres": rl["fade_metres"]}
    bad = [f"{n}={got[n]} want {v}" for n, v in want.items() if not near(got[n], v)]
    for n, v in (("RippleColour", rl["colour"]),):
        if not nearv(cs_float3(ulm, n), v):
            bad.append(f"{n}={cs_float3(ulm, n)} want {v}")
    bad += [f"{n} still declared (the waterline is removed)" for n in wl_names if re.search(r"\b" + n + r"\b", ulm)]
    out.append((f"5c C# effect literals are the target's (6 read, 3 removed names checked absent){': ' + '; '.join(bad) if bad else ''}", not bad))
    # 5d. the drawers call them
    wm_ = mask_comments(walls_cs)
    sm_ = mask_comments(surface_cs)
    need = [("RM_ExcavationWalls", wm_, n) for n in ("RM_UnderLiquid.WetAlpha", "RM_UnderLiquid.WetBandCells")] + \
           [("RM_LiquidSurface", sm_, "RM_UnderLiquid.RippleAlpha")]
    miss = [f"{f} never calls {n}" for f, txt, n in need if n not in txt]
    miss += [f"{f} draws the removed waterline ({n})" for f, txt in (("RM_ExcavationWalls", wm_), ("RM_LiquidSurface", sm_))
             for n in wl_names if re.search(r"RM_UnderLiquid\." + n + r"\b", txt)]
    out.append((f"5d wiring: the wall drawer draws wet tint and band and no pale waterline, the surface draws ripple light"
                + (f": {'; '.join(miss)}" if miss else ""), not miss))
    return out


def checks(t, model, ul_cs, gold_cs, walls_cs="", surface_cs=""):
    out = []
    depths = sorted(float(d) for d in t["hides_by_depth"])
    c = t["clarity"]

    # 1. the target is the judged picture
    w = 0.0
    for d in depths:
        w = max(w, abs(wm.hides(wm.law_firm, d) - t["hides_by_depth"][key(t, d)]))
    wc = max(abs(a - b) for d in depths for a, b in zip(wm.colour_at(wm.law_firm, d), t["mid_grey_becomes"][key(t, d)]))
    out.append((f"1 the target's law is the judged mockup's (FIRM's law, BLEND keeps it): hides worst {w:.5f} limit {TOL} · colour worst {wc:.4f} limit "
                f"{COLOUR_TOL} · cases {2 * len(depths)}", w <= TOL and wc <= COLOUR_TOL))

    # 2. the model hides and colours as the target says
    w, worst_d = 0.0, None
    for d in depths:
        e = abs((1.0 - model.seen(c, d)) - t["hides_by_depth"][key(t, d)])
        if e >= w:
            w, worst_d = e, d
    out.append((f"2 model seen = target at each listed depth: worst {w:.5f} at {worst_d:g} m limit {TOL} cases {len(depths)}",
                w <= TOL))
    body = model.body(model.WATER_COLOUR)
    wb = max(abs(a - b) for a, b in zip(body, t["body_colour"]))
    out.append((f"2 model fresh-water body colour {tuple(round(x, 4) for x in body)} = target {tuple(t['body_colour'])}: "
                f"worst {wb:.5f} limit {TOL} cases 3", wb <= TOL))
    grey = np.array((0.5, 0.5, 0.5))
    wg = 0.0
    for d in depths:
        s = model.seen(c, d)
        got = np.array(model.sheet(body, tuple(grey), s))
        wg = max(wg, float(np.abs(got - np.array(t["mid_grey_becomes"][key(t, d)])).max()))
    out.append((f"2 model sheet over a mid grey = target: worst {wg:.4f} limit {COLOUR_TOL} cases {len(depths)}",
                wg <= COLOUR_TOL))

    # 3. the C# side
    ulm = mask_comments(ul_cs)
    got = {n: cs_float(ulm, n) for n in ("DefaultShallowOpacity", "DefaultDeepOpacity", "DefaultFullMetres", "CurvePower",
                                          "ReferenceClarity", "BodyGamma", "DefaultDarken")}
    want = {"DefaultShallowOpacity": t["shallow_opacity"], "DefaultDeepOpacity": t["deep_opacity"],
            "DefaultFullMetres": t["full_metres"], "CurvePower": t["curve_power"], "ReferenceClarity": c}
    bad = [f"{n}={got[n]} want {v}" for n, v in want.items() if got[n] is None or abs(got[n] - v) > 1e-6]
    out.append((f"3 C# defaults are the target's ({len(want)} read){': ' + '; '.join(bad) if bad else ''}", not bad))
    wcol = cs_water_colour(ulm)
    if wcol is None or got["BodyGamma"] is None or got["DefaultDarken"] is None:
        out.append(("3 C# body colour: UNMEASURED (WaterColour, BodyGamma or DefaultDarken not found)", False))
    else:
        cb = tuple(max(0.0, min(1.0, x)) ** got["BodyGamma"] * (1 - got["DefaultDarken"]) for x in wcol)
        e = max(abs(a - b) for a, b in zip(cb, t["body_colour"]))
        out.append((f"3 C# Body(WaterColour) from its literals = target: worst {e:.5f} limit {TOL} cases 3", e <= TOL))
    rows = gold_rows_in(gold_cs) or []
    have = {(round(r[0], 5), round(r[1], 5)): r[2] for r in rows}
    miss, w = [], 0.0
    for d in depths:
        v = have.get((round(c, 5), round(d, 5)))
        if v is None:
            miss.append(f"{d:g}")
        else:
            w = max(w, abs((1.0 - v) - t["hides_by_depth"][key(t, d)]))
    out.append((f"3 golden table (dotnet checks Seen against it) = target: {len(rows)} rows, worst {w:.5f} limit {TOL}"
                + (f", MISSING depths {miss}" if miss else ""), not miss and rows != [] and w <= TOL))

    # 4. the range of situations
    clar = sorted({0.0, 0.25, 0.35, 0.45} | {round(0.05 * k, 2) for k in range(1, 20)})
    ms = [k / 100 for k in range(0, 1001)]
    n, worst = 0, {"range": 0.0, "clearer_deeper": 0.0, "below_shallow": 0.0, "above_deep": 0.0, "dry": 0.0, "opaque": 0.0}
    for sh in (0.0, 0.2, 0.35, 0.6):
        for dp in (0.5, 0.9, 1.0):
            if sh > dp:
                continue
            for full in (1.0, 4.0, 10.0):
                for cl in clar:
                    prev = None
                    for m in ms:
                        s = seen_with(model, cl, m, sh, dp, full)
                        n += 1
                        worst["range"] = max(worst["range"], -s, s - 1)
                        if prev is not None:
                            worst["clearer_deeper"] = max(worst["clearer_deeper"], s - prev)
                        prev = s
                        if m <= 0:
                            worst["dry"] = max(worst["dry"], abs(1 - s))
                        elif cl <= 0:
                            worst["opaque"] = max(worst["opaque"], s)
                        else:
                            worst["below_shallow"] = max(worst["below_shallow"], sh - (1 - s))
                            worst["above_deep"] = max(worst["above_deep"], (1 - s) - dp)
    out.append((f"4 the range: {n} cases (clarities {len(clar)}, depths {len(ms)}, settings 30); worst excess "
                + ", ".join(f"{k} {v:.2e}" for k, v in worst.items()) + " limit 1e-6",
                all(v <= 1e-6 for v in worst.values())))
    out += effects_checks(t, model, ul_cs, walls_cs, surface_cs)
    return out


def key(t, d):
    for k in t["hides_by_depth"]:
        if abs(float(k) - d) < 1e-9:
            return k
    raise KeyError(d)


def seen_with(model, cl, m, sh, dp, full):
    """model.seen at these settings; a model without a shallow strength is read with its own (it then has none)."""
    try:
        return model.seen(cl, m, deep_opacity=dp, full=full, shallow_opacity=sh)
    except TypeError:
        return model.seen(cl, m, deep_opacity=dp, full=full)


class Planted:
    """The model with one thing changed."""

    def __init__(self, **kw):
        self.__dict__.update({k: getattr(ul, k) for k in dir(ul) if not k.startswith("__")})
        self.__dict__.update(kw)


def main():
    t = json.loads(TARGET.read_text(encoding="utf-8"))
    ul_cs, gold_cs = UL.read_text(encoding="utf-8"), GOLD.read_text(encoding="utf-8")
    walls_cs, surface_cs = WALLS.read_text(encoding="utf-8"), SURFACE.read_text(encoding="utf-8")
    bad = 0
    for name, ok in checks(t, ul, ul_cs, gold_cs, walls_cs, surface_cs):
        print(("PASS " if ok else "FAIL ") + name)
        bad += not ok

    old = getattr(ul, "seen_approved_1113", None)
    plants = [
        ("the law shipped before this build (no shallow strength)",
         Planted(seen=(lambda c, m, deep_opacity=0.9, full=4.0, shallow_opacity=0.0: old(c, m)) if old else
                 (lambda c, m, deep_opacity=0.9, full=4.0, shallow_opacity=0.0: ul.seen(c, m, deep_opacity, full))),
         ul_cs, gold_cs, "2 model seen"),
        ("a pale body (Darken 0.3)", Planted(body=lambda col, darken=0.3: ul.body(col, darken)), ul_cs, gold_cs,
         "2 model fresh-water body"),
        ("a spliced golden row", ul, ul_cs, re.sub(r"(\{ 0\.45f, 0\.2f, )[0-9.]+f", r"\g<1>0.99f", gold_cs, count=1)
         if "{ 0.45f, 0.2f," in gold_cs else gold_cs.replace("{ 0.45f, 0.5f,", "{ 0.45f, 0.55f,", 1),
         "3 golden table"),
        ("a C# shallow default of 0", ul, re.sub(r"(DefaultShallowOpacity\s*=\s*)[0-9.]+f", r"\g<1>0.0f", ul_cs), gold_cs,
         "3 C# defaults"),
        ("a model with dry ground (wet darken 0)", Planted(WET_DARKEN=0.0), ul_cs, gold_cs, "5b model effects"),
        ("a C# ripple peak of 0.3 (RIPPLE's, refused by the judge)",
         ul, re.sub(r"(DefaultRipplePeak\s*=\s*)[0-9.]+f", r"\g<1>0.3f", ul_cs), gold_cs, "5c C# effect"),
        ("a wall drawer that never calls the wet tint", ul, ul_cs, gold_cs, "5d wiring", walls_cs.replace("RM_UnderLiquid.WetAlpha", "0f")),
        ("a model that brings the waterline back", Planted(WATERLINE_CELLS=0.03125, WATERLINE_ALPHA=0.45,
                                                           WATERLINE_COLOUR=(0.80, 0.88, 0.92)), ul_cs, gold_cs, "5b model effects"),
        ("a C# file that declares the waterline again", ul,
         ul_cs.replace("public const float WetBandDarken", "public const float WaterlineAlpha = 0.45f;\n\t\tpublic const float WetBandDarken", 1),
         gold_cs, "5c C# effect"),
        ("a wall drawer that draws the pale waterline (white frames at every water edge)", ul, ul_cs, gold_cs, "5d wiring",
         walls_cs.replace("float band = RM_UnderLiquid.WetBandCells;", "float band = RM_UnderLiquid.WetBandCells, l = RM_UnderLiquid.WaterlineCells;", 1)),
    ]
    for plant in plants:
        name, model, u, g, must = plant[:5]
        walls = plant[5] if len(plant) > 5 else walls_cs
        reds = [n for n, ok in checks(t, model, u, g, walls, surface_cs) if not ok]
        ok = any(r.startswith(must) for r in reds)
        print(("PASS " if ok else "FAIL ") + f"can-fail: {name} goes red ({'; '.join(r[:60] for r in reds)[:200]})")
        bad += not ok
    print("RESULT " + ("GREEN" if not bad else f"RED {bad}"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
