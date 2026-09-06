#!/usr/bin/env python3
"""compose_gl_vs_painter.py — MAPGEN_CONVERGENCE_LOOP_1's sheet: for each plan, the
in-game GL screenshot (top) over the offline painter render (bottom), captioned with
the plan's landform + premise. Pillow only.

  python3 compose_gl_vs_painter.py --shots Transient/mapgen_gl/shots \
      --renders Transient/mapgen_v1 --plans Transient/mapgen_v1 \
      --out Transient/mapgen_gl/comparator_gl_vs_painter.png

A plan with no screenshot (a skipped cycle) gets a grey "no GL shot" tile so the
gap is visible, never silently dropped. The caption also carries the proof state
read from <shots>/<id>.log.txt (the Player.log 'Landforms:' field) so a picture
whose landform was NOT applied is labelled as such.
"""
import argparse, glob, json, os
from PIL import Image, ImageDraw, ImageFont

TILE = 420

def fit(im, size):
    im = im.convert("RGB")
    w, h = im.size
    s = min(size / w, size / h)
    im = im.resize((max(1, int(w * s)), max(1, int(h * s))))
    canvas = Image.new("RGB", (size, size), (30, 30, 30))
    canvas.paste(im, ((size - im.size[0]) // 2, (size - im.size[1]) // 2))
    return canvas

def crop_game(im):
    """Trim RimWorld's letterbox/UI: keep the central square of the frame."""
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    return im.crop((left, 0, left + side, side))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", required=True)
    ap.add_argument("--renders", required=True, help="dir holding seedNN.png painter renders")
    ap.add_argument("--plans", required=True, help="dir holding seedNN.plan.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    plans = sorted(glob.glob(os.path.join(a.plans, "seed*.plan.json")))
    n = len(plans)
    font = ImageFont.load_default()
    sheet = Image.new("RGB", (TILE * n, TILE * 2 + 70), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    rows = []
    for i, pp in enumerate(plans):
        seed = os.path.basename(pp).split(".")[0]           # seed01
        gid = "RUT_Gen_" + seed[-2:]
        plan = json.load(open(pp))
        shot = os.path.join(a.shots, gid + ".png")
        proof = "no proof line"
        lt = os.path.join(a.shots, gid + ".log.txt")
        if os.path.isfile(lt):
            txt = open(lt).read()
            proof = "APPLIED" if ("Landforms: " + gid) in txt else ("NOT applied (%s)" % txt.strip()[-30:] if txt.strip() else "no map")
        if os.path.isfile(shot):
            sheet.paste(fit(crop_game(Image.open(shot)), TILE), (i * TILE, 0))
        else:
            d.rectangle([i * TILE, 0, (i + 1) * TILE, TILE], fill=(60, 60, 60))
            d.text((i * TILE + 10, TILE // 2), "no GL shot", fill=(200, 200, 200), font=font)
            proof = "no shot"
        rend = os.path.join(a.renders, seed + ".png")
        if os.path.isfile(rend):
            sheet.paste(fit(Image.open(rend), TILE), (i * TILE, TILE))
        else:
            d.rectangle([i * TILE, TILE, (i + 1) * TILE, 2 * TILE], fill=(60, 60, 60))
        lf = plan.get("landform", {}).get("id", "?")
        prem = plan.get("premise", "")[:58]
        d.text((i * TILE + 6, 2 * TILE + 6), f"{gid} {lf} | GL: {proof}", fill=(230, 230, 230), font=font)
        d.text((i * TILE + 6, 2 * TILE + 24), prem, fill=(180, 180, 180), font=font)
        d.text((i * TILE + 6, 2 * TILE + 42), "top: in-game (GL)   bottom: painter v1", fill=(140, 140, 140), font=font)
        rows.append((gid, lf, proof))
    sheet.save(a.out)
    print("wrote", a.out, sheet.size)
    for r in rows:
        print("  ", *r)

if __name__ == "__main__":
    main()
