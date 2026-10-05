#!/usr/bin/env python3
"""Contact sheets + automated image sanity metrics for the scene-matrix screenshots.

    python3 contact_sheet.py --shots <dir> --catalog <catalog.json> --out <dir> [--per-sheet 12] [--cols 4]
    python3 contact_sheet.py --shots <dir> --out <dir>          # no catalog: every *.png, captions = file names

Shots are matched to cases by file name: <case>.png (mod on) and, optionally, <case>_off.png (the same frame
with the master switch off, placer.py's last two steps). Output: sheet_NN.png + report.json.

Per-image metrics (each with its threshold in the report, never a bare number):
  non_blank      luminance std > 6
  no_magenta     fewer than 50 pixels with R>200, G<70, B>200 (RimWorld's missing-texture colour)
  brightness     mean luminance in [25, 230]
  wire_evidence  ON vs OFF pair: fraction of pixels whose max-channel difference > 40 must be >= 0.002, and the
                 pair must be aligned (median difference <= 4, else lighting or camera moved -> UNMEASURED).
                 A single image CANNOT prove cords are present: measured 2026-10-02 on the live pass, a dark-ridge
                 detector reads 0.019 with cords and 0.023 with vanilla conduit (real_art_01 vs real_art_05), and
                 a palette-distance test reads >0.5 on bare dark soil. So without an OFF pair it is UNMEASURED.
  style_hue      extcord only: share of pixels near the cord hues (orange/green/yellow/blue), informational.
  one_colour     non_blank also fails when > 98% of pixels share one (quantised) colour (design 4.6 #1)

Design 4.6 #2, the census-mask check (the preferred wire test once the census returns laid vertices):
  mask_check(image, polylines_px)  mean luminance inside a 3-px mask along every laid cord must be >= 12% darker
                                   than the rest of the frame (Jawa: matte black on soil). An empty polyline list is
                                   NO_WIRES (the empty-plot control must read that).
  frame_ok(size, plot_wh, px_per_cell)  image size == plot x px_per_cell within 2% (a zoom/framing slip).
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
T = {"std_min": 6.0, "magenta_px_max": 50, "bright": (25.0, 230.0), "diff_px": 40, "diff_frac_min": 0.002,
     "pair_median_max": 4.0}
EXTCORD_HUES = [(0xee, 0x7a, 0x1c), (0x3d, 0x9c, 0x3c), (0xef, 0xc8, 0x24), (0x2f, 0x6f, 0xd6)]


def metrics(path, off_path=None, style=None):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    lum = a.mean(axis=2)
    mag = int(((a[..., 0] > 200) & (a[..., 1] < 70) & (a[..., 2] > 200)).sum())
    m = {"file": os.path.basename(path), "size": list(im.size),
         "lum_mean": round(float(lum.mean()), 2), "lum_std": round(float(lum.std()), 2), "magenta_px": mag}
    q = (a // 8).reshape(-1, 3)
    _, counts = np.unique(q[:: max(1, len(q) // 200000)], axis=0, return_counts=True)
    m["top_colour_frac"] = round(float(counts.max()) / float(counts.sum()), 4)
    m["non_blank"] = bool(m["lum_std"] > T["std_min"] and m["top_colour_frac"] <= 0.98)
    m["no_magenta"] = mag < T["magenta_px_max"]
    m["brightness_ok"] = T["bright"][0] <= m["lum_mean"] <= T["bright"][1]
    if off_path and os.path.exists(off_path):
        b = np.asarray(Image.open(off_path).convert("RGB")).astype(np.int16)
        if b.shape != a.shape:
            m["wire_evidence"] = "UNMEASURED"
            m["wire_detail"] = "off frame size %s != on %s" % (b.shape[:2], a.shape[:2])
        else:
            d = np.abs(a - b).max(axis=2)
            med = float(np.median(d))
            frac = float((d > T["diff_px"]).mean())
            m["pair_median_diff"] = med
            m["wire_diff_frac"] = round(frac, 5)
            if med > T["pair_median_max"]:
                m["wire_evidence"] = "UNMEASURED"
                m["wire_detail"] = "pair not aligned (median diff %.1f > %.1f): light or camera moved" % (
                    med, T["pair_median_max"])
            else:
                m["wire_evidence"] = "PASS" if frac >= T["diff_frac_min"] else "FAIL"
    else:
        m["wire_evidence"] = "UNMEASURED"
        m["wire_detail"] = "no <case>_off.png pair (a single frame cannot prove cords)"
    if style == "extcord":
        px = a.reshape(-1, 3).astype(float)
        hues = np.array(EXTCORD_HUES, float)
        dist = np.min(np.linalg.norm(px[:, None, :] - hues[None], axis=2), axis=1)
        m["style_hue_frac"] = round(float((dist < 45).mean()), 5)
    m["ok"] = bool(m["non_blank"] and m["no_magenta"] and m["brightness_ok"] and m["wire_evidence"] != "FAIL")
    return m


def mask_check(path, polylines_px, width=3, darker=0.12):
    """Design 4.6 #2. polylines_px: [[(x, y), ...], ...] in image pixels (census vertices projected by the runner)."""
    from PIL import ImageDraw as _D
    im = Image.open(path).convert("L")
    if not polylines_px or not any(len(p) >= 2 for p in polylines_px):
        return {"verdict": "NO_WIRES", "detail": "no laid cord vertices in this frame"}
    mk = Image.new("L", im.size, 0)
    dr = _D.Draw(mk)
    for pl in polylines_px:
        if len(pl) >= 2:
            dr.line([tuple(map(float, p)) for p in pl], fill=255, width=width)
    m = np.asarray(mk) > 0
    lum = np.asarray(im).astype(float)
    if m.sum() == 0 or (~m).sum() == 0:
        return {"verdict": "UNMEASURED", "detail": "mask covers nothing or everything"}
    inside, outside = float(lum[m].mean()), float(lum[~m].mean())
    ratio = 1.0 - inside / max(outside, 1e-6)
    return {"verdict": "PASS" if ratio >= darker else "FAIL", "inside": round(inside, 2), "outside": round(outside, 2),
            "darker_by": round(ratio, 4), "threshold": darker, "mask_px": int(m.sum())}


def frame_ok(size, plot_wh, px_per_cell, tol=0.02):
    want = (plot_wh[0] * px_per_cell, plot_wh[1] * px_per_cell)
    return all(abs(size[i] - want[i]) <= tol * want[i] for i in (0, 1))


def _font(sz):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:  # noqa: BLE001
            pass
    return ImageFont.load_default()


def caption(case):
    if not case:
        return []
    return ["%s" % case.get("case", "?"),
            "%s | %s | %s" % (case.get("topology"), case.get("tangle"), case.get("style")),
            "n=%s break=%s air=%s hose=%s" % (case.get("density"), case.get("break"), case.get("aerial"), case.get("hose"))]


def sheet(items, out, cols=4, tile=(420, 300), title=""):
    """items: [(path, caption lines, metric dict)]"""
    rows = int(math.ceil(len(items) / float(cols)))
    cap_h = 58
    W = cols * tile[0] + (cols + 1) * 8
    H = 40 + rows * (tile[1] + cap_h + 8) + 8
    S = Image.new("RGB", (W, H), (34, 28, 22))
    dr = ImageDraw.Draw(S)
    f, fb = _font(13), _font(18)
    dr.text((10, 10), title, fill=(240, 220, 180), font=fb)
    for k, (p, cap, m) in enumerate(items):
        r, c = divmod(k, cols)
        x = 8 + c * (tile[0] + 8)
        y = 40 + r * (tile[1] + cap_h + 8)
        try:
            im = Image.open(p).convert("RGB")
            im.thumbnail(tile, Image.LANCZOS)
        except Exception:  # noqa: BLE001
            im = Image.new("RGB", tile, (90, 0, 90))
        S.paste(im, (x + (tile[0] - im.size[0]) // 2, y + (tile[1] - im.size[1]) // 2))
        col = (120, 210, 120) if m.get("ok") else (235, 90, 70)
        dr.rectangle([x - 2, y - 2, x + tile[0] + 1, y + tile[1] + 1], outline=col, width=2)
        flags = "%s  wire:%s" % ("OK" if m.get("ok") else "CHECK", m.get("wire_evidence"))
        for i, line in enumerate(cap + [flags]):
            dr.text((x + 2, y + tile[1] + 4 + i * 14), line[:64], fill=(230, 215, 190) if i < len(cap) else col, font=f)
    S.save(out)
    return out


def assemble(shots, out, catalog=None, per_sheet=12, cols=4):
    os.makedirs(out, exist_ok=True)
    cases = {}
    if catalog:
        cat = json.load(open(catalog))
        for c in cat["cases"]:
            cases[c["case"]["case"]] = c["case"]
    files = sorted(p for p in glob.glob(os.path.join(shots, "*.png")) if not p.endswith("_off.png"))
    items, report = [], []
    for p in files:
        name = os.path.splitext(os.path.basename(p))[0]
        case = cases.get(name)
        m = metrics(p, os.path.join(shots, name + "_off.png"), (case or {}).get("style"))
        m["case"] = name if case else None
        report.append(m)
        items.append((p, caption(case) or [name], m))
    if catalog:
        missing = sorted(set(cases) - {m["case"] for m in report if m["case"]})
    else:
        missing = []
    sheets = []
    for k in range(0, len(items), per_sheet):
        sheets.append(sheet(items[k:k + per_sheet], os.path.join(out, "sheet_%02d.png" % (k // per_sheet + 1)),
                            cols=cols, title="Gimme Some Slack scene matrix  sheet %d  (%d-%d of %d)" % (
                                k // per_sheet + 1, k + 1, min(k + per_sheet, len(items)), len(items))))
    summ = {"thresholds": {k: list(v) if isinstance(v, tuple) else v for k, v in T.items()},
            "images": len(report), "ok": sum(m["ok"] for m in report),
            "wire_evidence": {s: sum(m["wire_evidence"] == s for m in report) for s in ("PASS", "FAIL", "UNMEASURED")},
            "cases_without_shot": missing, "sheets": [os.path.basename(s) for s in sheets], "per_image": report}
    with open(os.path.join(out, "report.json"), "w") as f:
        json.dump(summ, f, indent=1)
    return summ


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shots", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--catalog")
    ap.add_argument("--per-sheet", type=int, default=12)
    ap.add_argument("--cols", type=int, default=4)
    a = ap.parse_args(argv)
    s = assemble(a.shots, a.out, a.catalog, a.per_sheet, a.cols)
    print("%d images, %d ok, wire %s, %d sheets -> %s" % (s["images"], s["ok"], s["wire_evidence"], len(s["sheets"]), a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
