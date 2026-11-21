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
CAN IT FAIL: run in this file: the law shipped before this build (shallow 0), a pale body (Darken 0.3), a spliced golden
row and a C# shallow default of 0 must each go RED.
    python3 src/RimMandrake/FlowWorks/selftest_flowworks_water_target.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TARGET = REPO / "design" / "concepts" / "FlowWorks" / "version" / "water_by_depth_target.json"
UL = HERE / "Source" / "Superdeep" / "RM_UnderLiquid.cs"
GOLD = HERE / "Source" / "SelfTest" / "UnderLiquidParityChecks.cs"
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


def checks(t, model, ul_cs, gold_cs):
    out = []
    depths = sorted(float(d) for d in t["hides_by_depth"])
    c = t["clarity"]

    # 1. the target is the judged picture
    w = 0.0
    for d in depths:
        w = max(w, abs(wm.hides(wm.law_firm, d) - t["hides_by_depth"][key(t, d)]))
    wc = max(abs(a - b) for d in depths for a, b in zip(wm.colour_at(wm.law_firm, d), t["mid_grey_becomes"][key(t, d)]))
    out.append((f"1 the target is the FIRM mockup: hides worst {w:.5f} limit {TOL} · colour worst {wc:.4f} limit "
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
    bad = 0
    for name, ok in checks(t, ul, ul_cs, gold_cs):
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
    ]
    for name, model, u, g, must in plants:
        reds = [n for n, ok in checks(t, model, u, g) if not ok]
        ok = any(r.startswith(must) for r in reds)
        print(("PASS " if ok else "FAIL ") + f"can-fail: {name} goes red ({'; '.join(r[:60] for r in reds)[:200]})")
        bad += not ok
    print("RESULT " + ("GREEN" if not bad else f"RED {bad}"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
