"""Add the TRIM region (mask GREEN -> DrawColorTwo = the container's Stuff colour) to the 12 pilot sprites.
Owner by card 2026-10-16: material colour on the trim only (cap/handle/hoops); body keeps its painted style.
Source: trim_raw/<size>_<style>.png, an edit of the sprite with trim painted flat green and the rest black (trim_gen.sh).
The edit's silhouette drifts, so it is registered onto the sprite by alpha bounding box (x and y scaled separately).
Trim pixels are neutralised to grey in the base sprite so the Stuff colour multiplies true, as the liquid already is.
Writes out/<Size>/<Style>/RM_<Size>.png and RM_<Size>_m.png in place (run after make_pilot.py)."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
HERE = Path(__file__).resolve().parent
for size in ["Bottle", "Bucket", "Barrel"]:
    for style in ["Scrapper", "Industrial", "Modern", "Futuristic"]:
        d = HERE / "out" / size / style
        base = Image.open(d / f"RM_{size}.png").convert("RGBA")
        mask = np.array(Image.open(d / f"RM_{size}_m.png").convert("RGBA"))
        if mask[..., 1].any():
            print(size, style, "already has trim; skipped"); continue
        ed = Image.open(HERE / "trim_raw" / f"{size.lower()}_{style.lower()}.png").convert("RGBA")
        bb_src = base.getchannel("A").point(lambda v: 255 if v >= 32 else 0).getbbox()
        bb_ed = ed.getchannel("A").point(lambda v: 255 if v >= 32 else 0).getbbox()
        e = np.array(ed).astype(int)
        green = ((e[..., 1] > 150) & (e[..., 0] < 110) & (e[..., 2] < 110) & (e[..., 3] > 127)).astype(np.uint8) * 255
        g = Image.fromarray(green).crop(bb_ed).resize((bb_src[2] - bb_src[0], bb_src[3] - bb_src[1]), Image.BOX)
        gm = Image.new("L", base.size, 0); gm.paste(g, bb_src[:2])
        gm = gm.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
        a = np.array(base)[..., 3]
        trim = (np.array(gm) > 127) & (a > 0) & (mask[..., 0] < 128)
        arr = np.array(base).astype(float)
        v = arr[..., :3].max(axis=2) / 255.0
        grey = np.clip(0.25 + 0.80 * v, 0, 1) * 255
        for i in range(3):
            arr[..., i] = np.where(trim, grey, arr[..., i])
        Image.fromarray(arr.astype(np.uint8), "RGBA").save(d / f"RM_{size}.png")
        mask[..., 1] = np.where(trim, 255, 0)
        Image.fromarray(mask, "RGBA").save(d / f"RM_{size}_m.png")
        print(f"{size:7s} {style:10s} trim px {int(trim.sum()):6d}  liquid px {int((mask[...,0]>127).sum()):6d}")
