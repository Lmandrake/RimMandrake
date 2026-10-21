#!/usr/bin/env python3
"""Build world/ASHKARR_LABELS70_2026-10-20_plan.json: every region label's maxDrawSizeInTiles
re-derived so its DISPLAYED width is world_label_curve.LABEL_DISPLAY_SCALE (70%) of the U1
canonical one (owner card 2026-10-20 7:36 PM PDT: 'Smaller, about 70%'). Centres unchanged.
`before` = the U1 plan's `after` (apply U1 first). Also draws the before/after footprint preview.

    python3 labels70_plan.py [--preview <out.png>]
Apply: world/_parity_apply_2026-10-20.py labels70 <outdir> [--apply]
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world_label_curve as C

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
U1 = os.path.join(REPO, "world/ASHKARR_PARITY_U1_labels_2026-10-20_plan.json")
OUT = os.path.join(REPO, "world/ASHKARR_LABELS70_2026-10-20_plan.json")


def build(u1_path=U1, scale=C.LABEL_DISPLAY_SCALE):
    u1 = json.load(open(u1_path, encoding="utf-8"))
    feats, floor = [], []
    for f in u1["features"]:
        a = f["after"]
        old = float(a["size"]); new = C.scaled_max_draw(old, scale)
        e0, e1 = C.effective_draw_size(old), C.effective_draw_size(new)
        if new <= C.DRAW_SIZE_CURVE[0][0]:
            floor.append(f["name"])
        feats.append({"name": f["name"], "uid": f["uid"], "tiles": f["tiles"],
                      "before": {"centerOnTile": a["centerOnTile"], "drawCenter": a["drawCenter"],
                                 "size": old, "effectiveWidthTiles": round(e0, 2)},
                      "after": {"centerOnTile": a["centerOnTile"], "drawCenter": a["drawCenter"],
                                "size": new, "effectiveWidthTiles": round(e1, 2),
                                "atFloor": new <= C.DRAW_SIZE_CURVE[0][0],
                                "sizeSource": "U1 canonical x %.2f displayed width" % scale}})
    return {"what": "LABELS70: displayed label width x%.2f of the U1 canonical sizes (owner card "
                    "2026-10-20 7:36 PM PDT 'Smaller, about 70%%'); centres unchanged. Requires U1 "
                    "applied. Apply: world/_parity_apply_2026-10-20.py labels70" % scale,
            "source": {"u1Plan": os.path.basename(u1_path)},
            "scale": scale,
            "curve": {"knots": C.DRAW_SIZE_CURVE, "floorEffectiveTiles": C.DRAW_SIZE_CURVE[0][1]},
            "counts": {"features": len(feats), "sizeChanges": sum(1 for x in feats if x["after"]["size"] != x["before"]["size"]),
                       "atFloor": len(floor)},
            "atFloor": sorted(floor), "features": feats}


def preview(plan, png):
    import numpy as np
    from PIL import Image, ImageDraw
    import worldgeom, feature_drawcenter_audit as A
    geo = worldgeom.Geometry(21872)
    W, H = 2400, 1200
    im = Image.new("RGB", (W, H), (28, 24, 20)); d = ImageDraw.Draw(im)
    for la, lo in zip(geo.lat, geo.lon):
        x, y = (lo + 180) / 360 * W, (90 - la) / 180 * H
        d.point((x, y), fill=(70, 62, 52))
    tile_deg = float(np.degrees(np.sqrt(4 * np.pi / 21872)))
    for f in plan["features"]:
        lon, lat = A.engine_longlat(f["before"]["drawCenter"])
        cx, cy = (lon + 180) / 360 * W, (90 - lat) / 180 * H
        for key, col in (("before", (255, 120, 90)), ("after", (90, 220, 230))):
            wdeg = f[key]["effectiveWidthTiles"] * tile_deg
            hw = wdeg / 360 * W / 2 / max(0.25, np.cos(np.radians(lat)))
            hh = max(3.0, wdeg * 0.07 / 180 * H)  # a text line is ~1/7 as tall as it is wide
            d.rectangle([cx - hw, cy - hh, cx + hw, cy + hh], outline=col, width=3 if key == 'after' else 2)
        d.text((cx - 20, cy - 4), f["name"], fill=(240, 234, 210))
    d.text((12, 8), "Label footprints (label width = effective tiles x %.2f deg): orange = before, cyan = 70%% after. "
           "%d of %d at the 15-tile floor." % (tile_deg, plan["counts"]["atFloor"], plan["counts"]["features"]), fill=(240, 234, 210))
    os.makedirs(os.path.dirname(png), exist_ok=True); im.save(png)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--preview"); a = ap.parse_args()
    p = build(); json.dump(p, open(OUT, "w", encoding="utf-8"), indent=1)
    print("wrote", OUT, p["counts"])
    if a.preview: preview(p, a.preview); print("preview", a.preview)
