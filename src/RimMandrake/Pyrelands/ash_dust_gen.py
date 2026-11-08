"""Pyrelands ash-dust plant overlays: one per living grass sprite, the same silhouette, printed over the plant while its cell
holds a loose-ash drift (Source/PyrelandsAshDust.cs). Vanilla prints a plant's snowOverlayGraphic the same way when snow is
deep; ash fall lays loose-ash filth instead of snow, and filth draws BELOW LowPlant, so on this biome's grass carpet a
six-hour ash fall laid ~3,000 drifts that a player could not see at all (map w, 2026-11-08, af_s1_4.png).

Each overlay keeps the blade's own shading (pale ash scaled by the base's luminance) so a dusted clump reads as grass under
ash, not a grey cut-out. Ash settles thickest on the upper faces (pixels with open sky above them) and as a fine grain
everywhere else. Same file names as the bases, so Graphic_Random's sorted sub-graphic index matches one for one.

  Things/Plant/RM_FE_AshDust/EmberGrass/...      over RM_FE_EmberGrass
  Things/Plant/RM_FE_AshDust/Quickgrass/...      over RM_FE_Quickgrass
  Things/Plant/RM_FE_AshDust/QuickgrassSprout/.. over RM_FE_QuickgrassStages/Sprout
  Things/Plant/RM_FE_AshDust/QuickgrassHalf/...  over RM_FE_QuickgrassStages/Half
The charred leafless sprites take none: they are already black.

python3 src/RimMandrake/Pyrelands/ash_dust_gen.py [OUTDIR] [--preview PNG]
"""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PLANT = os.path.join(HERE, "Textures", "Things", "Plant")
SETS = (
    ("RM_FE_EmberGrass", "EmberGrass"),
    ("RM_FE_Quickgrass", "Quickgrass"),
    ("RM_FE_QuickgrassStages/Sprout", "QuickgrassSprout"),
    ("RM_FE_QuickgrassStages/Half", "QuickgrassHalf"),
)
ASH = np.array([170.0, 165.0, 158.0])      # a mid ash grey, under the drift's (184,180,172) tint: paler read as frost


def _bases(sub):
    d = os.path.join(PLANT, *sub.split("/"))
    return [(f, os.path.join(d, f)) for f in sorted(os.listdir(d)) if f.lower().endswith(".png")]


def dust(base, seed):
    rgba = np.asarray(base.convert("RGBA"), dtype=np.float64) / 255.0
    a = rgba[..., 3]
    lum = 0.30 * rgba[..., 0] + 0.59 * rgba[..., 1] + 0.11 * rgba[..., 2]
    solid = (a > 0.35).astype(np.float64)
    h, w = a.shape
    # A cap, as vanilla's snow overlays sit on a bush: ash lies on the clump's upper reach and thins down it, so the grass's own
    # colour still shows below and a dusted clump reads as grass under ash, not a grey ghost of itself (the first cut, a 30%
    # film over the whole silhouette plus soft 2 px noise, read hazy at 1:1 in game: shots/ad_s1_6.png).
    rows = np.arange(h, dtype=np.float64)[:, None]
    any_col = solid.any(axis=0)
    top = np.where(any_col, solid.argmax(axis=0), h).astype(np.float64)
    bottom = np.where(any_col, h - 1 - solid[::-1, :].argmax(axis=0), 0).astype(np.float64)
    # Columns smoothed over 9 px so one tall blade does not drag its neighbours' caps up with it.
    k = np.ones(9) / 9.0
    top = np.convolve(np.pad(top, 4, mode="edge"), k, mode="valid")
    span = np.maximum(bottom.max() - top.min(), 1.0)
    depth = (rows - top[None, :]) / span
    cap = 1.0 - np.clip((depth - 0.18) / 0.30, 0.0, 1.0)
    # Open sky straight above (8 px): the upper face of each blade lower down catches a rim of ash too.
    above = np.zeros_like(a)
    for d in range(1, 9):
        shifted = np.zeros_like(solid)
        shifted[d:, :] = solid[:-d, :]
        above += (1.0 - shifted) / 8.0
    rim = np.clip((above - 0.45) / 0.3, 0.0, 1.0) * 0.8
    rng = np.random.default_rng(seed)
    # Grit: specks about 4 px across with rounded, hard edges (blurred noise, thresholded), big enough to survive the game's mip
    # down to ~40 px a clump; square blocks read as a pixel mosaic at 1:1.
    g = rng.random((h // 3 + 1, w // 3 + 1))
    g = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
                   .filter(ImageFilter.GaussianBlur(1.0)), dtype=np.float64) / 255.0
    grit = np.clip((g - 0.60) / 0.06, 0.0, 1.0) * 0.75
    cover = np.clip(np.maximum(np.maximum(cap, rim), grit), 0.0, 1.0)
    cover = np.where(cover > 0.5, np.minimum(1.0, cover * 1.15), cover * 0.6)
    shade = 0.72 + 0.42 * np.clip(lum, 0.0, 1.0)
    rgb = np.clip(ASH[None, None, :] * shade[..., None], 0, 255)
    alpha = np.clip(a * cover * 0.95, 0.0, 1.0)
    out = np.dstack([rgb, alpha * 255.0]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def build(outdir):
    written = []
    for i, (src, dst) in enumerate(SETS):
        od = os.path.join(outdir, dst)
        os.makedirs(od, exist_ok=True)
        for j, (name, path) in enumerate(_bases(src)):
            img = dust(Image.open(path), seed=1000 * i + j)
            p = os.path.join(od, name)
            img.save(p)
            written.append((path, p))
    return written


def preview(pairs, out, bg=(52, 48, 44), cell=48):
    """Top row: the bases at 256 px. Second: base with the dust at full and at the light strength. Bottom: a 3x3 carpet of
    each at about play zoom (cell px), clean against dusted, to judge what a player sees."""
    n = len(pairs)
    sheet = Image.new("RGBA", (n * 256, 256 * 3 + cell * 3 + 20), bg + (255,))
    for k, (b, o) in enumerate(pairs):
        base = Image.open(b).convert("RGBA")
        ov = Image.open(o).convert("RGBA")
        sheet.alpha_composite(base, (k * 256, 0))
        full = base.copy(); full.alpha_composite(ov)
        sheet.alpha_composite(full, (k * 256, 256))
        light = base.copy()
        ovl = ov.copy(); ovl.putalpha(ov.getchannel("A").point(lambda v: int(v * 0.55)))
        light.alpha_composite(ovl)
        sheet.alpha_composite(light, (k * 256, 512))
        small_c = base.resize((cell, cell), Image.LANCZOS)
        small_d = full.resize((cell, cell), Image.LANCZOS)
        for r in range(3):
            for c in range(2):
                sheet.alpha_composite(small_c, (k * 256 + c * cell // 2 + 10, 768 + 10 + r * cell // 2))
                sheet.alpha_composite(small_d, (k * 256 + 128 + c * cell // 2, 768 + 10 + r * cell // 2))
    sheet.save(out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    outdir = args[0] if args else os.path.join(PLANT, "RM_FE_AshDust")
    pairs = build(outdir)
    for b, o in pairs:
        print(os.path.relpath(o))
    if "--preview" in sys.argv:
        preview(pairs, sys.argv[sys.argv.index("--preview") + 1])
