#!/usr/bin/env python3
"""facing_scale_lint.py — is a creature drawn at the same size in every facing?

Owner, 2026-10-15 20:20: "Some of the beasts have art in one facing that is larger than the others. Mostly this is
North/South is larger than East/West. This perhaps can be corrected by a scaling operation, or regeneration if
necessary. Please programmatically detect this problem and then determine the best way to fix it."

    python3 facing_scale_lint.py calibrate                 vanilla ratios -> facing_scale_calibration.json
    python3 facing_scale_lint.py lint [DEF ...] [--repo] [--json OUT] [--md OUT] [--all]
    python3 facing_scale_lint.py fix --json ROWS --defs D1,D2 --out DIR [--owner-said "..."] [--dry-run]

WHAT IS MEASURED. Each facing PNG's opaque silhouette (alpha >= 128, rows/columns with >= 2 such pixels), as a
fraction of its canvas. RimWorld stretches every facing of a Graphic_Multi onto the SAME drawSize quad, so canvas
fractions compare directly between facings (and world units = fraction x drawSize). A facing whose canvas has a
different pixel size is stretched too — normalising by canvas catches that case as well.

TWO VIEWPOINTS. Vanilla draws S/N TOP-DOWN, so they stand taller than E by the foreshortened body length (the depth
model below). This project's own art is drawn from a GROUND CAMERA (elevation: front, side and back views of a
standing creature), so its S/N vertical extent is the creature's height, the same as E's. Art shipped from a
mandrake.* mod whose S/N silhouette stands on two or more separate feet (bottom 6% of its rows), with an east that does too, is judged as elevation (S/E and N/E height ratio expected 1, tolerance = vanilla's inter-quartile scatter
around the depth model, re-centred on 1 — see elevation_band); donor and vanilla art is judged top-down. Judging our
elevation art by the top-down model passes N/S drawn ~30% too large — which is exactly what the owner saw.

WHAT MAY LEGITIMATELY DIFFER. East shows body LENGTH, south/north show body WIDTH, so widths differ by design. The
comparison is HEIGHT (vertical extent) of south and north against east — and, as a second check, the width each
side view would have after its height is made right. The acceptable spread is not a guess: `calibrate` measures
every vanilla Core/DLC animal's facings (ludeon.* textures from the AssetBundle extract), and the band per ratio is
vanilla's 2.5..97.5 percentile (swimming poses excluded: not a standing silhouette). A hand-drawn _west is compared with east (it should match).

THE FIX RULE. When south AND north are both too small, east is the odd one out and east is shrunk instead. Otherwise
a flagged facing is RESCALED about its ground-contact point (bottom-centre of its silhouette), canvas
size kept, to bring its height ratio to the nearest edge of vanilla's inter-quartile range — when that is a pure
scale problem: the factor is <= MAX_UPSCALE when enlarging and the rescaled width ratio lands inside vanilla's width
band. Otherwise the proportions are wrong, not just the scale: REGENERATE.

The graphics measured are every texPath the game resolves for each creature: PawnKindDef lifeStages[]
bodyGraphicData / femaleGraphicData / dessicatedBodyGraphicData and alternateGraphics, read from BOTH the deployed
mods' XML (current) and the newest DefDump capture (post-patch, possibly older), deduplicated by texPath; each
texPath resolves to the picture the game draws through gametex (deployed Mods folders, live load order, later mods
win). --repo measures the repo copy of a deployed file where one exists (what the NEXT deploy will ship).
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

CAL = HERE / "facing_scale_calibration.json"
GAME_DATA = Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data")
ALPHA = 128
MIN_RUN = 2
MARGIN = 0.0             # band = vanilla p2.5 / (1+M) .. p97.5 * (1+M)
MAX_UPSCALE = 1.25
WEST_BAND = (0.95, 1.05)
MIN_PLAN_N = 8           # a body plan with fewer vanilla animals than this borrows the all-vanilla band
MARGINS = (0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20)   # widening of vanilla's per-plan ENVELOPE tried, smallest first
TARGET_FLAG_RATE = 0.05  # vanilla's own flag rate (animal level, S or N or N:S; leave-one-out) must not exceed this
FEET_PLANS = ("quadruped", "biped", "flyer")   # plans whose legs are visible as separate feet in a ground-camera view
FACES = ("east", "south", "north", "west")
FEET_TOL = 0.03          # ground-camera S/N feet row (silhouette bottom, canvas fraction) within this of the same picture's east
CENTRE_KEEP = 0.05       # a S/N centred further than this from the canvas middle is a deliberate offset: kept, not re-centred


# ───────────────────────────────────────────────────────── measurement ──

def silhouette(img) -> dict | None:
    """Opaque bbox of an RGBA image as canvas fractions. None when nothing is opaque."""
    import numpy as np
    a = np.asarray(img.convert("RGBA"))[:, :, 3] >= ALPHA
    H, W = a.shape
    rows = np.where(a.sum(axis=1) >= MIN_RUN)[0]
    cols = np.where(a.sum(axis=0) >= MIN_RUN)[0]
    if not len(rows) or not len(cols):
        return None
    y0, y1, x0, x1 = int(rows[0]), int(rows[-1]), int(cols[0]), int(cols[-1])
    feet = 0                               # separate opaque runs in the bottom 6% of the silhouette: legs on the ground
    for y in range(max(y0, y1 - max(2, round((y1 - y0) * 0.06))), y1 + 1):
        row = a[y]
        runs = [len(g) for g in np.split(row, np.where(np.diff(row.astype(np.int8)) != 0)[0] + 1) if g[0]]
        feet = max(feet, sum(1 for n in runs if n >= max(2, W // 100)))
    return {"feet": feet, "W": W, "H": H, "x0": x0, "y0": y0, "x1": x1, "y1": y1,
            "h": (y1 - y0 + 1) / H, "w": (x1 - x0 + 1) / W, "area": float(a.sum()) / (W * H),
            "bottom": (y1 + 1) / H, "cx": (x0 + x1 + 1) / 2 / W}


def measure_file(path) -> dict | None:
    from PIL import Image
    try:
        with Image.open(path) as im:
            return silhouette(im)
    except OSError:
        return None


def ratios(m: dict, coef: dict | None = None) -> dict:
    """m: facing -> silhouette. Width of S/N over east's width, hand-drawn west over east, north over south, and —
    given the depth-model coefficients — each S/N height over the height the model predicts from east's silhouette."""
    e = m.get("east")
    out = {}
    if not e:
        return out
    for f in ("south", "north"):
        s = m.get(f)
        if s:
            out[f"w_{f}"] = s["w"] / e["w"]
            out[f"e_{f}"] = s["h"] / e["h"]
            if coef:
                a, b = coef[f]
                out[f"d_{f}"] = s["h"] / (a * e["h"] + b * e["w"])
    if m.get("south") and m.get("north"):
        out["ns"] = m["north"]["h"] / m["south"]["h"]
        out["nsw"] = m["north"]["w"] / m["south"]["w"]
    if m.get("west"):
        out["h_west"] = m["west"]["h"] / e["h"]
    return out


# ───────────────────────────────────────────────────────── calibration ──

def _quant(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def vanilla_animal_bases() -> set:
    out = set()
    for p in GAME_DATA.glob("*/Defs/**/*.xml"):
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in re.finditer(r"<texPath>(Things/Pawn/Animal/[^<]+)</texPath>", txt):
            b = m.group(1).rsplit("/", 1)[-1]
            if not re.search(r"dess?icc?ated", b, re.I):
                out.add(b)
    return out


def vanilla_faces(base: str) -> dict:
    """facing -> extracted PNG of a ludeon.* texture named <base>_<facing> (the AssetBundle extract)."""
    import csv
    import gametex as G
    out = {}
    with open(G.BUNDLES / "index.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            m = re.fullmatch(re.escape(base) + r"_(east|south|north)", r["m_Name"])
            if m and r["sourceKey"].startswith("ludeon."):
                out.setdefault(m.group(1), str(G.BUNDLES / r["file"]))
    return out


def vanilla_kind_index() -> dict:
    """texture base name -> {PawnKindDef defName} for the BASE GAME's kinds, read from the game's own Data/*/Defs XML
    (the DefDump is post-patch: mods retexture vanilla kinds, e.g. Rat -> FancyRat, so it cannot say who drew Rat)."""
    by = {}
    for p in GAME_DATA.glob("*/Defs/**/*.xml"):
        try:
            root = ET.parse(p).getroot()
        except (ET.ParseError, OSError):
            continue
        for k in root.iter("PawnKindDef"):
            dn = (k.findtext("defName") or "").strip()
            for tp in k.iter("texPath"):
                t = (tp.text or "").strip()
                if dn and t.startswith("Things/Pawn/Animal/"):
                    by.setdefault(t.rsplit("/", 1)[-1], set()).add(dn)
    return by


def vanilla_plan(base: str, kidx: dict) -> tuple[str, str]:
    """(plan, evidence) of a vanilla texture base via its PawnKindDef's race body; UNCLASSIFIED when no kind owns it."""
    import facing_body_plan as BP
    for cand in (base, re.sub(r"\d+$", "", base), re.sub(r"(_?[AB]|Male|Female|Baby|_Stationary)$", "", base)):
        for k in sorted(kidx.get(cand, ())):
            plan, ev = BP.plan_of_kind(k)
            if plan != "UNCLASSIFIED":
                return plan, f"{k}: {ev}"
    return "UNCLASSIFIED", "no ludeon PawnKindDef draws this texture"


def plan_stats(animals, plan, margin):
    """d_south / d_north statistics over the animals of one plan (None = all). The BAND is vanilla's observed envelope
    for that plan (min..max) widened by `margin`: percentile tails (even 0.25%) flag 8-17% of vanilla itself, because
    four ratios per animal each have their own extremes; only the envelope keeps vanilla near 5%."""
    sel = [a for a in animals if plan is None or a["plan"] == plan]
    out = {"n": len(sel)}
    for k in ("d_south", "d_north"):
        xs = [a["ratios"][k] for a in sel]
        q = {"min": round(min(xs), 4), "max": round(max(xs), 4)}
        q.update({p: round(_quant(xs, v), 4) for p, v in (("p25", .25), ("p50", .5), ("p75", .75))})
        q["p02.5"], q["p97.5"] = round(q["min"] / (1 + margin), 4), round(q["max"] * (1 + margin), 4)
        q["band"] = [q["p02.5"], q["p97.5"]]
        out[k] = q
    return out


def build_cal(animals, base_cal, margin):
    """base_cal's coefficients/quantiles with per-plan envelope bands from `animals`."""
    c = dict(base_cal)
    c["quantiles"] = {k: dict(v) for k, v in base_cal["quantiles"].items()}
    xs = [a["ratios"]["ns"] for a in animals]
    c["quantiles"]["ns"]["band"] = [round(min(xs) / (1 + margin), 4), round(max(xs) * (1 + margin), 4)]
    counts = {}
    for a in animals:
        counts[a["plan"]] = counts.get(a["plan"], 0) + 1
    c["plans"] = {"all": plan_stats(animals, None, margin)}
    for pl, n in counts.items():
        if n >= MIN_PLAN_N:
            c["plans"][pl] = plan_stats(animals, pl, margin)
    c["margin_envelope"] = margin
    return c


def calibrate() -> dict:
    import csv
    import gametex as G
    import numpy as np
    bases = vanilla_animal_bases()
    kidx = vanilla_kind_index()
    rows = {}
    with open(G.BUNDLES / "index.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            if not r["sourceKey"].startswith("ludeon."):
                continue
            m = re.fullmatch(r"(.+)_(east|south|north)", r["m_Name"])
            if m and m.group(1) in bases and not m.group(1).lower().startswith("swimming"):   # not a standing pose
                rows.setdefault((r["sourceKey"], m.group(1)), {})[m.group(2)] = str(G.BUNDLES / r["file"])
    animals = []
    for (src, base), faces in sorted(rows.items()):
        if set(faces) != {"east", "south", "north"}:
            continue
        m = {f: measure_file(p) for f, p in faces.items()}
        if all(m.values()):
            plan, ev = vanilla_plan(base, kidx)
            animals.append({"source": src, "base": base, "m": m, "plan": plan, "plan_evidence": ev})
    # depth model: a south/north view's vertical extent is part body height, part foreshortened body LENGTH (east's
    # width) — vanilla's N/S are taller than E for exactly this reason (median S/E height 1.20, N/E 1.33)
    E = np.array([[a["m"]["east"]["h"], a["m"]["east"]["w"]] for a in animals])
    coef = {}
    for f in ("south", "north"):
        y = np.array([a["m"][f]["h"] for a in animals])
        c, *_ = np.linalg.lstsq(E, y, rcond=None)
        coef[f] = [round(float(c[0]), 4), round(float(c[1]), 4)]
    for a in animals:
        a["ratios"] = ratios(a["m"], coef)
    keys = ("d_south", "d_north", "ns", "nsw", "w_south", "w_north")
    q = {}
    for k in keys:
        xs = [a["ratios"][k] for a in animals]
        q[k] = {p: round(_quant(xs, v), 4) for p, v in (("p02.5", .025), ("p25", .25), ("p50", .5), ("p75", .75),
                                                        ("p97.5", .975))}
        q[k]["min"], q[k]["max"] = round(min(xs), 4), round(max(xs), 4)
        q[k]["band"] = [round(q[k]["p02.5"] / (1 + MARGIN), 4), round(q[k]["p97.5"] * (1 + MARGIN), 4)]
    res = {"what": "vanilla animal facing ratios from ludeon.* AssetBundle textures (Core + DLC animals with all three "
                   "facings); d_* = S/N silhouette height over the depth model's prediction a*hE + b*wE; "
                   "regenerate with `facing_scale_lint.py calibrate`",
           "alpha": ALPHA, "margin": MARGIN, "n": len(animals), "coef": coef, "quantiles": q}
    # per-body-plan envelope bands for d_south/d_north: widen the margin until vanilla flags <= TARGET_FLAG_RATE of
    # itself when each animal is judged against the envelope of all the OTHERS (leave-one-out: an honest rate)
    plan_counts = {}
    for a in animals:
        plan_counts[a["plan"]] = plan_counts.get(a["plan"], 0) + 1
    res["loo_by_margin"] = {}
    for mg in MARGINS:
        flagged = [a for a in animals
                   if judge(a["m"], build_cal([x for x in animals if x is not a], res, mg), "topdown", a["plan"])["flags"]]
        res["loo_by_margin"][str(mg)] = round(len(flagged) / len(animals), 4)
        if len(flagged) / len(animals) <= TARGET_FLAG_RATE:
            break
    res.update({k: v for k, v in build_cal(animals, res, mg).items() if k in ("plans", "margin_envelope")})
    res["quantiles"] = build_cal(animals, res, mg)["quantiles"]
    res["tail"] = None
    flagged = [a for a in animals if judge(a["m"], res, "topdown", a["plan"])["flags"]]   # in-sample
    res["vanilla_flag_rate_in_sample"] = round(len(flagged) / len(animals), 4)
    res["vanilla_flag_rate"] = res["loo_by_margin"][str(mg)]       # leave-one-out, at the chosen margin
    res["vanilla_flagged_in_sample"] = [a["base"] for a in flagged]
    res["plan_counts"] = plan_counts
    res["animals"] = [{"base": a["base"], "source": a["source"], "plan": a["plan"], "plan_evidence": a["plan_evidence"],
                       **{k: round(v, 4) for k, v in a["ratios"].items()}} for a in animals]
    CAL.write_text(json.dumps(res, indent=1) + "\n")
    return res


def load_cal() -> dict:
    return json.loads(CAL.read_text())


# ──────────────────────────────────────────────────────────── verdicts ──

def _excess(v, band):
    lo, hi = band
    ex = v / hi - 1 if v > hi else (lo / v - 1 if v < lo else 0.0)
    return ex if ex > 0.002 else 0.0               # bands are stored to 4 places: an animal ON the edge is inside


def elevation_band(cal) -> list:
    """Tolerance for ELEVATION art (S/N drawn from a ground camera, so the vertical extent is the creature's height in
    every facing and the expected S/E, N/E height ratio is 1): vanilla's own inter-quartile scatter around the depth
    model, re-centred on 1."""
    q = cal["quantiles"]
    lo = min(q["d_south"]["p25"] / q["d_south"]["p50"], q["d_north"]["p25"] / q["d_north"]["p50"])
    hi = max(q["d_south"]["p75"] / q["d_south"]["p50"], q["d_north"]["p75"] / q["d_north"]["p50"])
    return [round(lo, 4), round(hi, 4)]


def plan_band(cal: dict, plan: str | None) -> dict:
    """The per-plan d_south/d_north stats, or the all-vanilla ones when the plan has too few vanilla animals."""
    P = cal.get("plans") or {}
    return P.get(plan) if plan in P else P.get("all")


def judge(m: dict, cal: dict, view: str = "topdown", plan: str | None = None) -> dict:
    """-> {ratios, flags:[{facing, key, value, band, excess}], severity, fixes:{facing: {...}}}.
    A S/N facing is flagged when its depth-model height ratio is outside the band of its BODY PLAN (vanilla's 2.5..97.5
    percentile scatter, widened until vanilla flags <= 5% of itself); when only the N:S ratio is out, the facing
    further from the model's median is the one flagged. A hand-drawn west must match east.
    ELEVATION art (ground camera) expects S/E and N/E height 1: the same band re-centred on its plan median. A S/N is
    elevation when the picture comes from a mandrake.* mod and either its plan is one whose legs read as separate feet
    (FEET_PLANS: and the silhouette then stands on 2+ feet, as does east) or its plan has no reliable feet signal
    (fish, serpent, blob, lowslung, insect: convention alone decides — the feet test misreads their splayed or absent
    legs)."""
    q = dict(cal["quantiles"])
    pb = plan_band(cal, plan) if cal.get("plans") else None
    if pb:
        q["d_south"], q["d_north"] = dict(pb["d_south"]), dict(pb["d_north"])
    r = ratios(m, cal["coef"])
    views = {}
    for f in ("south", "north"):
        feet_ok = (plan in FEET_PLANS or plan is None) and m.get(f, {}).get("feet", 0) >= 2 and m["east"].get("feet", 0) >= 2
        if f in m and view == "elevation" and (feet_ok or (plan is not None and plan not in FEET_PLANS)):
            views[f] = "elevation"
            if f"e_{f}" in r:
                r[f"d_{f}"] = r[f"e_{f}"]
            if pb:                          # the plan's scatter around its own median, re-centred on 1
                med = pb[f"d_{f}"]["p50"]
                qq = {k: v / med for k, v in pb[f"d_{f}"].items() if k != "band"}
                qq["band"] = [qq["p02.5"], qq["p97.5"]]
                q[f"d_{f}"] = qq
            else:
                eb = elevation_band(cal)
                q[f"d_{f}"] = {"band": eb, "p25": 1.0, "p75": 1.0, "p50": 1.0, "p02.5": eb[0], "p97.5": eb[1]}
        elif f in m:
            views[f] = "topdown"
    flags = []
    for f in ("south", "north"):
        k = f"d_{f}"
        if k in r:
            ex = _excess(r[k], q[k]["band"])
            if ex > 0:
                flags.append({"facing": f, "key": k, "value": round(r[k], 3), "band": q[k]["band"],
                              "excess": round(ex, 3)})
    if "ns" in r and not flags:
        ex = _excess(r["ns"], q["ns"]["band"])
        if ex > 0:
            f = max(("south", "north"), key=lambda f: abs(math.log(r[f"d_{f}"] / q[f"d_{f}"]["p50"])))
            flags.append({"facing": f, "key": "ns", "value": round(r["ns"], 3), "band": q["ns"]["band"],
                          "excess": round(ex, 3)})
    if "h_west" in r:
        ex = _excess(r["h_west"], WEST_BAND)
        if ex > 0:
            flags.append({"facing": "west", "key": "h_west", "value": round(r["h_west"], 3), "band": list(WEST_BAND),
                          "excess": round(ex, 3)})
    fixes, plan = {}, {}
    for fl in flags:                       # every flagged facing's factor first: the checks see the whole fix
        f = fl["facing"]
        if f == "west":
            plan[f] = (1.0, 1.0 / r["h_west"])
        else:
            v = r[f"d_{f}"]
            tgt = min(max(v, q[f"d_{f}"]["p25"]), q[f"d_{f}"]["p75"])
            plan[f] = (tgt, tgt / v)
    if {"south", "north"} <= set(plan) and plan["south"][1] > 1 and plan["north"][1] > 1:
        # both front/back views too SMALL: east is the odd one out — shrink east instead of enlarging two facings
        k = math.sqrt(plan["south"][1] * plan["north"][1])
        why = []
        for f in ("south", "north"):
            d, w = r[f"d_{f}"] * k, r[f"w_{f}"] * k
            if not (q[f"d_{f}"]["p02.5"] <= d <= q[f"d_{f}"]["p97.5"]):
                why.append(f"{f} height/model after shrinking east {d:.2f} still outside vanilla")
            if not (q[f"w_{f}"]["band"][0] <= w <= q[f"w_{f}"]["band"][1]):
                why.append(f"{f} width/E after shrinking east {w:.2f} outside vanilla")
        fixes["east"] = {"action": "regenerate" if why else "rescale", "scale": round(1 / k, 4), "target": None,
                         "width_after": None, "why": "; ".join(why)}
        plan = {f: v for f, v in plan.items() if f == "west"}
    for fl in flags:
        f = fl["facing"]
        if f not in plan:
            continue
        w_after = None
        tgt, s = plan[f]
        why = []
        if s > MAX_UPSCALE:
            why.append(f"enlarging x{s:.2f} > {MAX_UPSCALE} loses detail")
        if f != "west":
            w_after = r[f"w_{f}"] * s
            wb = q[f"w_{f}"]["band"]
            if not (wb[0] <= w_after <= wb[1]):
                why.append(f"width/E after rescale {w_after:.2f} outside vanilla {wb[0]:.2f}-{wb[1]:.2f}")
            if "nsw" in r and views.get("south") == views.get("north"):   # its width must still agree with the other S/N view
                nsw = r["nsw"] * plan.get("north", (0, 1.0))[1] / plan.get("south", (0, 1.0))[1]
                nb = q["nsw"]["band"]
                if not (nb[0] <= nsw <= nb[1]) and abs(math.log(nsw)) > abs(math.log(r["nsw"])) + 0.02:
                    why.append(f"N:S width after rescale {nsw:.2f} outside vanilla {nb[0]:.2f}-{nb[1]:.2f} "
                               "and worse than before (the extra height is pose or anatomy, not scale)")
        fit = m[f]
        if s > 1 and (fit["h"] * s > 1 or fit["w"] * s > 1):
            why.append("rescaled silhouette would leave the canvas")
        fixes[f] = {"action": "regenerate" if why else "rescale", "scale": round(s, 4), "target": round(tgt, 4),
                    "width_after": None if w_after is None else round(w_after, 3), "why": "; ".join(why)}
    return {"ratios": {k: round(v, 4) for k, v in r.items()}, "flags": flags, "views": views,
            "severity": round(max([f["excess"] for f in flags], default=0.0), 3), "fixes": fixes}


# ─────────────────────────────────────────────────────── graphic discovery ──

def _gd(el) -> dict | None:
    if el is None:
        return None
    tp = (el.findtext("texPath") or "").strip()
    if not tp:
        return None
    ds = (el.findtext("drawSize") or "").strip()
    try:
        if ds.startswith("("):
            x, y = (float(v) for v in ds.strip("()").split(","))
        elif ds:
            x = y = float(ds)
        else:
            x = y = 1.0
    except ValueError:
        x = y = 1.0
    return {"texPath": tp, "drawSize": [x, y], "graphicClass": (el.findtext("graphicClass") or "").strip()}


def _kind_graphics(node, by_name) -> list[dict]:
    """[(slot, gd)] for a PawnKindDef XML node, inheriting lifeStages / alternateGraphics from ParentName."""
    def inherited(tag):
        n, seen = node, set()
        while n is not None:
            e = n.find(tag)
            if e is not None:
                return e
            pn = n.get("ParentName")
            if not pn or pn in seen:
                return None
            seen.add(pn)
            n = by_name.get(pn)
        return None
    out = []
    ls = inherited("lifeStages")
    body = None
    if ls is not None:
        for i, li in enumerate(ls.findall("li")):
            for fld in ("bodyGraphicData", "femaleGraphicData", "dessicatedBodyGraphicData"):
                g = _gd(li.find(fld))
                if g:
                    out.append({"slot": f"lifeStages[{i}].{fld}", **g})
                    if fld == "bodyGraphicData":
                        body = g
    alts = inherited("alternateGraphics")
    if alts is not None:
        for i, li in enumerate(alts.findall("li")):
            tp = (li.findtext("texPath") or "").strip()
            if tp:
                out.append({"slot": f"alternateGraphics[{i}]", "texPath": tp,
                            "drawSize": (body or {}).get("drawSize", [1.0, 1.0]), "graphicClass": ""})
    return out


def deployed_kinds() -> dict:
    """defName -> {mod, packageId, graphics:[...]} from the XML of every active mandrake.* mod, deployed copy."""
    import gametex as G
    ix = G.index()
    order, _ = G.load_order()
    active = set(order)
    nodes, by_name, owner = [], {}, {}
    for m in ix["mods"]:
        pid = (m.get("packageId") or "")
        if not pid.startswith("mandrake.") or m["load_index"] < 0:
            continue
        for lf in G.load_folders(Path(m["dir"]), active):
            for p in (lf / "Defs").rglob("*.xml") if (lf / "Defs").is_dir() else []:
                try:
                    root = ET.parse(p).getroot()
                except (ET.ParseError, OSError):
                    continue
                for el in root.iter("PawnKindDef"):
                    nodes.append(el)
                    owner[id(el)] = (m["name"] or Path(m["dir"]).name, pid)
                    if el.get("Name"):
                        by_name[el.get("Name")] = el
    out = {}
    for el in nodes:
        dn = (el.findtext("defName") or "").strip()
        if not dn or el.get("Abstract", "").lower() == "true":
            continue
        gs = _kind_graphics(el, by_name)
        if gs:
            mod, pid = owner[id(el)]
            out[dn] = {"mod": mod, "packageId": pid, "graphics": gs, "source": "deployed-xml"}
    return out


def dump_kinds() -> dict:
    from game_paths import DEF_DUMP
    p = Path(DEF_DUMP) / "defs" / "PawnKindDef.json"
    if not p.is_file():
        return {}
    out = {}

    def g(d):
        if not isinstance(d, dict) or not d.get("texPath"):
            return None
        ds = d.get("drawSize") or {}
        return {"texPath": d["texPath"], "drawSize": [ds.get("x", 1.0), ds.get("y", 1.0)],
                "graphicClass": d.get("graphicClass") or ""}
    for d in json.loads(p.read_text())["defs"]:
        pid = d.get("packageId") or ""
        if not pid.startswith("mandrake."):
            continue
        f = d.get("fields") or {}
        gs, body = [], None
        for i, ls in enumerate(f.get("lifeStages") or []):
            if not isinstance(ls, dict):
                continue
            for fld in ("bodyGraphicData", "femaleGraphicData", "dessicatedBodyGraphicData"):
                x = g(ls.get(fld))
                if x:
                    gs.append({"slot": f"lifeStages[{i}].{fld}", **x})
                    body = body or (x if fld == "bodyGraphicData" else None)
        for i, a in enumerate(f.get("alternateGraphics") or []):
            if isinstance(a, dict) and a.get("texPath"):
                gs.append({"slot": f"alternateGraphics[{i}]", "texPath": a["texPath"],
                           "drawSize": (body or {}).get("drawSize", [1.0, 1.0]), "graphicClass": ""})
        if gs:
            out[d["defName"]] = {"mod": d.get("modName"), "packageId": pid, "graphics": gs, "source": "dump"}
    return out


def roster(defs=None) -> dict:
    """defName -> {mod, packageId, graphics}. The deployed XML is authoritative (current); the DefDump capture fills
    only defs the XML scan does not find (it can be days older, so its texPaths for a def that exists in XML are
    stale, not patches). BLIND SPOT: a texPath changed only by a PatchOperation is seen only through the dump."""
    xk, dk = deployed_kinds(), dump_kinds()
    out = {}
    for dn in set(xk) | set(dk):
        if defs and dn not in defs:
            continue
        out[dn] = xk.get(dn) or dk[dn]
    return out


def repo_copy(path: str) -> str | None:
    """The repo file the next deploy would ship over a deployed mandrake file, or None. A composed mod
    (Mods/RimMandrake.Biomes/Biomes/Pyrelands/Textures/...) is matched by its innermost folder (src/*/Pyrelands)."""
    m = re.search(r"/Mods/(.+?)/Textures/(.+)$", path)
    if not m:
        return None
    for seg in reversed(m.group(1).split("/")):
        if re.fullmatch(r"v?\d+\.\d+|Common", seg):
            continue
        hits = sorted((REPO / "src").glob(f"*/{seg}/Textures/{m.group(2)}")) or \
            sorted((REPO / "src").glob(f"*/{seg}/*/Textures/{m.group(2)}"))
        if hits:
            return str(hits[0])
    return None


def faces_of(texpath: str, use_repo: bool) -> tuple[dict, str]:
    import gametex as G
    r = G.resolve_res(texpath)
    win = next((c for c in r["copies"] if c.get("winner")), r["copies"][0] if r["copies"] else None)
    if win:
        faces = {f: p for f, p in win["faces"].items() if f in FACES or f == "single"}
        where = win["mod"]
        view = "elevation" if (win.get("packageId") or "").startswith("mandrake.") else "topdown"
    else:
        faces = {b["facing"]: str(G.BUNDLES / b["path"]) if not str(b["path"]).startswith("/") else b["path"]
                 for b in r["bundle"] if b["facing"] in FACES}
        where = "bundle" if faces else "UNRESOLVED"
        view = "topdown"
    if use_repo:
        faces = {f: (repo_copy(p) or p) for f, p in faces.items()}
    return faces, where, view


def kind_plan(kind: str) -> tuple[str, str]:
    import facing_body_plan as BP
    return BP.plan_of_kind(kind)


def lint(defs=None, use_repo=False) -> list[dict]:
    cal = load_cal()
    rows, done = [], {}
    for dn, k in sorted(roster(defs).items()):
        for gr in k["graphics"]:
            if gr["graphicClass"] and not gr["graphicClass"].endswith("Graphic_Multi"):
                continue
            key = gr["texPath"].lower()
            if key not in done:
                faces, where, view = faces_of(gr["texPath"], use_repo)
                m = {f: measure_file(p) for f, p in faces.items() if f in FACES}
                m = {f: v for f, v in m.items() if v}
                done[key] = (faces, where, m, view)
            faces, where, m, view = done[key]
            row = {"def": dn, "mod": k["mod"], "slot": gr["slot"], "texPath": gr["texPath"],
                   "drawSize": gr["drawSize"], "resolved_in": where, "view": view, "files": faces,
                   "silhouette": m}
            if "east" not in m or not ({"south", "north"} & set(m)):
                row.update(verdict="UNMEASURED", severity=0.0, flags=[], fixes={},
                           why=("one picture, no facings" if set(faces) <= {"single"} else
                                "no east facing" if "east" not in m else "no south/north facing"))
            else:
                plan, plan_ev = kind_plan(dn)
                j = judge(m, cal, view, None if plan == "UNCLASSIFIED" else plan)
                row.update(j, plan=plan, plan_evidence=plan_ev, verdict="FLAG" if j["flags"] else "ok")
                # A FLAG under the owner's ground-camera standard may still sit inside what VANILLA ships (vanilla's
                # S/N are top-down, taller than E by design). beyond_vanilla = also TOO BIG against vanilla's own
                # top-down envelope for the plan: indefensible by either standard.
                if j["flags"] and view == "elevation":
                    tv = judge(m, cal, "topdown", None if plan == "UNCLASSIFIED" else plan)
                    row["beyond_vanilla"] = any(x["value"] > x["band"][1] for x in tv["flags"])
                else:
                    row["beyond_vanilla"] = bool(j["flags"])
                if view == "elevation":      # ground-camera S/N must stand where east stands (the creature must not drop when it turns)
                    off = {f: round(m[f]["bottom"] - m["east"]["bottom"], 4) for f in ("south", "north")
                           if f in m and abs(m[f]["bottom"] - m["east"]["bottom"]) > FEET_TOL}
                    row["feet_off"] = off
                    for f in off:
                        row["fixes"].setdefault(f, {"action": "reseat", "scale": 1.0, "target": None, "width_after": None,
                                                   "why": f"feet row {off[f]:+.3f} of canvas height from east's"})
                    if off:
                        row["verdict"] = "FLAG"
                        row["severity"] = max(row.get("severity", 0.0), round(max(abs(v) for v in off.values()), 3))
                for f, s in m.items():
                    s["h_world"] = round(s["h"] * gr["drawSize"][1], 3)
                    s["w_world"] = round(s["w"] * gr["drawSize"][0], 3)
            rows.append(row)
    rows.sort(key=lambda r: (-r["severity"], r["def"], r["slot"]))
    return rows


def pictures(rows) -> list[dict]:
    """One row per distinct picture (texPath): the worst slot's verdict, with every def/slot that draws it."""
    by = {}
    for r in rows:
        k = r["texPath"].lower()
        if k not in by:
            by[k] = dict(r, users=[])
        by[k]["users"].append(f"{r['def']}:{r['slot']}")
    return sorted(by.values(), key=lambda r: (-r["severity"], r["texPath"]))


def to_md(rows, title) -> str:
    pics = pictures(rows)
    fl = [r for r in pics if r["verdict"] == "FLAG"]
    act = lambda r, a: [f for f, x in r["fixes"].items() if x["action"] == a]  # noqa: E731
    lines = [f"# {title}", "",
             f"{len(pics)} distinct pictures ({len(rows)} def slots) measured: {len(fl)} FLAG "
             f"({sum(bool(act(r, 'rescale')) and not act(r, 'regenerate') for r in fl)} rescale, "
             f"{sum(bool(act(r, 'regenerate')) for r in fl)} regenerate), "
             f"{sum(r['verdict'] == 'UNMEASURED' for r in pics)} UNMEASURED, "
             f"{sum(r['verdict'] == 'ok' for r in pics)} ok. "
             f"{sum(bool(r.get('beyond_vanilla')) for r in fl)} of the FLAGs are also too big against vanilla's own "
             "top-down envelope for their body plan (the rest are ground-camera-standard only).",
             "", "| sev | picture | drawn by | S, N height / depth model; N:S | fix |", "|---|---|---|---|---|"]
    for r in fl:
        rt = r["ratios"]
        fx = "; ".join(f"{f}: {x['action']} x{x['scale']}" + (f" ({x['why']})" if x["why"] else "")
                       for f, x in r["fixes"].items())
        users = sorted({u.split(":")[0] for u in r["users"]})
        lines.append(f"| {r['severity']:.2f} | `{r['texPath']}` | {', '.join(users)} | S {rt.get('d_south', '-')}, "
                     f"N {rt.get('d_north', '-')}; N:S {rt.get('ns', '-')}"
                     + (f", W {rt['h_west']}" if "h_west" in rt else "") + f" | {fx} |")
    um = [r for r in pics if r["verdict"] == "UNMEASURED"]
    if um:
        lines += ["", "UNMEASURED: " + "; ".join(f"`{r['texPath']}` ({r['why']})" for r in um)]
    return "\n".join(lines) + "\n"


# ───────────────────────────────────────────────────────────────── fix ──

def reseat(img, east: dict, keep_offset: float = CENTRE_KEEP):
    """Integer-translate a S/N picture (no resample) so its feet row equals EAST's (canvas fraction) and its
    silhouette is centred on the canvas, unless it sits more than keep_offset of the width off-centre (deliberate:
    kept). A translation that would clip opaque pixels is cut short. -> (image, {dx, dy, kept_offset})."""
    from PIL import Image
    im = img.convert("RGBA")
    sil = silhouette(im)
    W, H = im.size
    dy = round(east["bottom"] * H) - (sil["y1"] + 1)
    dy = max(-sil["y0"], min(H - 1 - sil["y1"], dy))
    kept = abs(sil["cx"] - 0.5) > keep_offset
    dx = 0 if kept else round(W / 2 - (sil["x0"] + sil["x1"] + 1) / 2)
    dx = max(-sil["x0"], min(W - 1 - sil["x1"], dx))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(im, (dx, dy))
    return out, {"dx": dx, "dy": dy, "kept_offset": kept}


def rescale(img, s: float, east: dict | None = None):
    """Resample the silhouette about its ground-contact point (bottom-centre of the opaque bbox); canvas kept.
    With `east` (its silhouette) the result is then seated: feet row = east's feet row, centred (see reseat) —
    anchoring at the S/N's own bottom left creatures standing lower than in their east view."""
    from PIL import Image
    im = img.convert("RGBA")
    sil = silhouette(im)
    W, H = im.size
    nw, nh = max(1, round(W * s)), max(1, round(H * s))
    big = im.convert("RGBa").resize((nw, nh), Image.LANCZOS).convert("RGBA")
    ax, ay = (sil["x0"] + sil["x1"] + 1) / 2, sil["y1"] + 1          # anchor in source px
    ox, oy = round(ax - ax * s), round(ay - ay * s)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(big, (ox, oy))                       # a plain paste: the transparent margin replaces, never blends
    if east and silhouette(out):
        out, _ = reseat(out, east)
    return out


def fix(rows, defs, out_dir: Path, owner_said: str | None, dry_run: bool) -> list[dict]:
    import artledger as L
    from PIL import Image
    done, res = set(), []
    for r in rows:
        if r["def"] not in defs or r["verdict"] != "FLAG":
            continue
        for f, x in r["fixes"].items():
            src = r["files"][f]
            if x["action"] not in ("rescale", "reseat") or src in done:
                continue
            done.add(src)
            try:
                mod, rel = L.locate(src)
            except L.Refused as e:
                res.append({"def": r["def"], "facing": f, "file": src, "status": f"REFUSED: {e}"})
                continue
            dst = out_dir / mod / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(src) as im:
                rescale(im, x["scale"], r["silhouette"].get("east")).save(dst)
            row = {"def": r["def"], "texPath": r["texPath"], "facing": f, "file": src, "fixed": str(dst),
                   "scale": x["scale"], "mod": mod, "rel": rel}
            if not dry_run:
                cmd = [sys.executable, str(HERE / "art.py"), "install", mod, rel, "--file", str(dst)]
                cmd += ["--owner-said", owner_said] if owner_said else ["--reason", "script:" + str(
                    Path(__file__).resolve().relative_to(REPO))]
                p = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
                row["status"] = (p.stdout.strip().splitlines() or [p.stderr.strip()])[-1][:300]
            else:
                row["status"] = "dry-run"
            res.append(row)
    return res


def sheet(groups, out, px_per_cell=150, title=""):
    """groups: [(label, drawSize, {facing: PIL image or path})] -> one RGB PNG; every facing drawn at TRUE scale
    (drawSize x px_per_cell for the full canvas) standing on a shared baseline per row, with a 1-cell ruler."""
    from PIL import Image, ImageDraw
    rows = []
    for label, ds, faces in groups:
        ims = []
        for f in ("east", "south", "north", "west"):
            im = faces.get(f)
            if im is None:
                continue
            im = Image.open(im) if isinstance(im, (str, Path)) else im
            im = im.convert("RGBA").resize((max(1, round(ds[0] * px_per_cell)), max(1, round(ds[1] * px_per_cell))),
                                           Image.LANCZOS)
            ims.append((f, im))
        rows.append((label, ims))
    pad, lab = 12, 18
    W = max([pad + sum(im.width + pad for _, im in ims) for _, ims in rows] + [600]) + 90
    H = 30 + sum(lab + max([im.height for _, im in ims] + [40]) + pad for _, ims in rows)
    can = Image.new("RGB", (W, H), (205, 196, 178))
    d = ImageDraw.Draw(can)
    d.text((pad, 8), title, fill=(30, 20, 10))
    y = 30
    for label, ims in rows:
        d.text((pad, y), label, fill=(30, 20, 10))
        y += lab
        hmax = max([im.height for _, im in ims] + [40])
        x = pad
        d.rectangle([W - 70, y + hmax - px_per_cell, W - 62, y + hmax], fill=(60, 40, 20))
        d.text((W - 58, y + hmax - 14), "1 cell", fill=(30, 20, 10))
        for f, im in ims:
            d.rectangle([x, y, x + im.width - 1, y + hmax - 1], outline=(170, 160, 140))
            sil = silhouette(im)
            if sil:
                d.line([x, y + hmax - im.height + sil["y0"], x + im.width, y + hmax - im.height + sil["y0"]],
                       fill=(200, 60, 40))
            can.paste(im, (x, y + hmax - im.height), im)
            d.text((x + 3, y + 2), f[0].upper(), fill=(30, 20, 10))
            x += im.width + pad
        y += hmax + pad
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    can.save(out)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("calibrate")
    li = sub.add_parser("lint")
    li.add_argument("defs", nargs="*")
    li.add_argument("--repo", action="store_true")
    li.add_argument("--json")
    li.add_argument("--md")
    li.add_argument("--title", default="Facing scale lint")
    rs = sub.add_parser("reseat", help="shift-only: seat installed S/N pictures on east's feet row (no resample)")
    rs.add_argument("files", nargs="+", help="repo S/N PNGs; east is the sibling *_east.png")
    rs.add_argument("--out", required=True, help="mirror dir (<mod>/<rel>) for art.py install")
    fx = sub.add_parser("fix")
    fx.add_argument("--json", required=True)
    fx.add_argument("--defs", required=True)
    fx.add_argument("--out", required=True)
    fx.add_argument("--owner-said")
    fx.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "calibrate":
        c = calibrate()
        for k, v in c["quantiles"].items():
            print(f"{k:8} n={c['n']} p2.5={v['p02.5']} p25={v['p25']} p50={v['p50']} p75={v['p75']} "
                  f"p97.5={v['p97.5']} band={v['band']}")
        return 0
    if a.cmd == "lint":
        rows = lint(set(a.defs) or None, a.repo)
        if a.json:
            Path(a.json).write_text(json.dumps(rows, indent=1))
        md = to_md(rows, a.title)
        if a.md:
            Path(a.md).write_text(md)
        print("\n".join(md.splitlines()[:3 + 2 + 30]))
        return 1 if any(r["verdict"] != "ok" for r in rows) else 0
    if a.cmd == "reseat":
        import artledger as AL
        from PIL import Image
        for f in a.files:
            e = measure_file(re.sub(r"_(south|north)\.png$", "_east.png", f))
            with Image.open(f) as im:
                out, info = reseat(im, e)
            if info["dx"] or info["dy"]:
                mod, rel = AL.locate(f)
                dst = Path(a.out) / mod / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                out.save(dst)
            print(json.dumps({"file": f, **info}))
        return 0
    rows = json.loads(Path(a.json).read_text())
    res = fix(rows, set(a.defs.split(",")), Path(a.out), a.owner_said, a.dry_run)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
