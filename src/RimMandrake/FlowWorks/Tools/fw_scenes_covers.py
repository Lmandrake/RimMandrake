#!/usr/bin/env python3
"""Offline concealed-pit (pit cover) scenes and checks (PLANK_COVER_REDRAW_READS_AS_EMPTY_PIT).

Owner 2026-10-24, of a plank cover in a pit: "says it's a plank covered pit, but it sure doesn't look like it (empty pit
appearance?)". His shot (owner_shots/20261024061650_1.jpg): a 3x3 dug pit with ONE cover on its centre square. The
shipped Building_PitCover.Print draws no art of its own: it prints the terrain round the pit (SurfaceAround) on its cell, so
a lid inside an open pit is a floating square of dirt and the pit reads as empty.

What it emulates (read from the C#, not guessed):
  * the pit: fw_scenes_spikes.render (RM_ExcavationWalls faces + outline, stand-in colours) with no spikes;
  * the ground: fw_compositor.soil (world-aligned, as terrain materials are: a cover printing the ground's material
    matches the ground beside it pixel for pixel -- the concealment the 2026-10-21 card asked for);
  * the cover (FloorEmplacement, above the wall faces at TerrainScatter + 0.003):
      "before"        the shipped Print: the ground's material on the 1x1 cell;
      "planks"        Graphic_Single of the def's own texPath (lattice B, the owner's pick 2026-10-22) on the 1x1 cell,
                      over whatever the pit draws below it (its gaps show the hole);
      "planks_ground" the same texture over the ground's material (the gaps show dirt: laid planks, still disguised-ish);
      "planks_full"   "planks" with the texture cropped to its opaque box (its ~6% transparent margin gone), so a deck of
                      covers meets edge to edge instead of reading as separate pallets (needs a texture change).

Checks (selftest_fw_offline_art.py runs them):
  cover_reads_as_material(res, cell) -> (ok, r, slope): the cover cell shows the tier texture's structure: luminance Pearson
      r >= R_MIN against the texture over its opaque pixels and regression slope >= SLOPE_MIN (a texture dusted to near-invisible
      still correlates; it fails the slope). FAILS on the shipped print, PASSES on "planks".
  deck_matches_ground(res, cells) -> (ok, diff): the cover cells equal the ground beside them (what "before" achieves on a deck that
      covers the WHOLE pit: the north star pit_covered_invisible). Informational: it is why "before" was ruled right.

    python3 fw_scenes_covers.py <out_dir>     # SHEET_covers.png (owner composite) + per-scene renders + checks.txt
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fw_compositor as fc  # noqa: E402
import fw_scenes_spikes as spk  # noqa: E402

TIERS = ("RM_PitCover_PlankLattice", "RM_PitCover_WovenScrap", "RM_PitCover_ReinforcedFrame")
TEX = "Things/Building/FlowWorks/Canals/%s"
MODES = ("before", "planks", "planks_ground", "planks_full", "dusted")   # dusted: can-fail only
DEPTH = 4            # 2 m (RM_Volume 0.5 m a level): the shallowest superdeep pit a cover may sit on
R_MIN = 0.6
SLOPE_MIN = 0.5


def pit_3x3(covers):
    """The owner's shot: a 3x3 dug pit in a 5x5 board, covers = cells (x, z) z north (board coords, pit is 1..3)."""
    depth = [[0] * 5] + [[0, DEPTH, DEPTH, DEPTH, 0] for _ in range(3)] + [[0] * 5]
    return spk.Pit(depth), set(covers)


SCENES = (
    ("centre lid (owner's shot)", lambda: pit_3x3([(2, 2)])),
    ("whole pit covered", lambda: pit_3x3([(x, z) for x in (1, 2, 3) for z in (1, 2, 3)])),
    ("north row covered", lambda: pit_3x3([(x, 3) for x in (1, 2, 3)])),
)


def render(pit, covers, mode, tier=TIERS[0], P=96):
    """-> dict(img RGB, ground RGB array, P, covers, tier, mode)."""
    base = spk.render(pit, mode="after", P=P)["img"]
    a = np.asarray(base, np.float32).copy()
    H, W = a.shape[:2]
    ground = np.asarray(fc.soil(W, H), np.float32)[..., :3]
    is_soil = np.all(a == np.array(spk.SOIL, np.float32), axis=-1)
    a[is_soil] = ground[is_soil]                        # undug ground: the world-aligned terrain
    t = cover_texture(tier, full=(mode == "planks_full")).resize((P, P), Image.LANCZOS)
    T = np.asarray(t, np.float32) / 255.0
    for (x, z) in covers:
        r0, c0 = (pit.H - z - 1) * P, x * P
        cell = a[r0:r0 + P, c0:c0 + P]
        g = ground[r0:r0 + P, c0:c0 + P]
        if mode == "before":
            cell[:] = g
        elif mode in ("planks", "planks_ground", "planks_full", "dusted"):
            under = g if mode == "planks_ground" else cell.copy()
            al = T[..., 3:4] * (0.15 if mode == "dusted" else 1.0)
            cell[:] = T[..., :3] * 255 * al + under * (1 - al)
        else:
            raise ValueError(mode)
    if mode not in MODES:
        raise ValueError(mode)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")
    return dict(img=img, ground=ground, P=P, covers=covers, tier=tier, mode=mode, pit=pit,
                texture=cover_texture(tier, full=(mode == "planks_full")))


def cover_texture(tier, full=False):
    """The tier's texture; full: cropped to its opaque box (alpha > 40) so a deck of covers meets edge to edge."""
    t = fc.tex(TEX % tier)
    if full:
        t = t.crop(t.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox())
    return t


def _lum(rgb):
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


def cover_reads_as_material(res, cell):
    """(ok, r, slope): the cover cell's luminance against the tier texture's, over the texture's opaque pixels."""
    P, pit = res["P"], res["pit"]
    x, z = cell
    if cell not in res["covers"]:
        return False, 0.0, 0.0
    r0, c0 = (pit.H - z - 1) * P, x * P
    L = _lum(np.asarray(res["img"], np.float32)[r0:r0 + P, c0:c0 + P]).ravel()
    T = np.asarray(res["texture"].resize((P, P), Image.LANCZOS), np.float32)
    opaque = (T[..., 3] >= 230).ravel()                 # the material itself, whatever lies under its gaps
    Lt = _lum(T[..., :3]).ravel()[opaque]
    L = L[opaque]
    if opaque.sum() < 100 or Lt.std() < 1e-6 or L.std() < 1e-6:
        return False, 0.0, 0.0
    r = float(np.corrcoef(L, Lt)[0, 1])
    slope = float(np.cov(L, Lt)[0, 1] / Lt.var())
    return (r >= R_MIN and slope >= SLOPE_MIN), r, slope


def deck_matches_ground(res, cells=None):
    """(ok, mean abs diff): the cover cells against the world-aligned ground at the same pixels."""
    P, pit = res["P"], res["pit"]
    a = np.asarray(res["img"], np.float32)
    diffs = []
    for (x, z) in sorted(cells or res["covers"]):
        r0, c0 = (pit.H - z - 1) * P, x * P
        diffs.append(np.abs(a[r0:r0 + P, c0:c0 + P] - res["ground"][r0:r0 + P, c0:c0 + P]).mean())
    m = float(np.mean(diffs)) if diffs else 999.0
    return m < 3.0, m


def sheet(out):
    """Rows: scenes; columns: shipped / drawn / drawn edge to edge for the plank tier, then edge to edge for the other two.
    (planks_ground is not offered: a judge found it erases the pit's rim, 2026-10-24; the selftest still checks it.)"""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    cols = [("A  shipped: ground print", "before", TIERS[0]),
            ("B  lattice drawn, gaps show hole", "planks", TIERS[0]),
            ("C  B cropped edge to edge", "planks_full", TIERS[0]),
            ("D  C for woven scrap", "planks_full", TIERS[1]),
            ("E  C for reinforced frame", "planks_full", TIERS[2])]
    P = 72
    cw, ch, top, left = 5 * P, 5 * P, 40, 230
    pad = 12
    W = left + len(cols) * (cw + pad)
    H = top + len(SCENES) * (ch + pad) + 30
    sh = Image.new("RGB", (W, H), (30, 30, 30))
    d = ImageDraw.Draw(sh)
    f = fc.font(15)
    for j, (lab, _, _) in enumerate(cols):
        d.text((left + j * (cw + pad), 12), lab, fill=(255, 255, 255), font=f)
    lines = []
    for i, (name, mk) in enumerate(SCENES):
        for k, part in enumerate(name.split(" (")):
            d.text((8, top + i * (ch + pad) + ch // 2 + 18 * k), part if k == 0 else "(" + part, fill=(255, 255, 255), font=f)
        for j, (lab, mode, tier) in enumerate(cols):
            pit, cov = mk()
            res = render(pit, cov, mode, tier, P=P)
            sh.paste(res["img"], (left + j * (cw + pad), top + i * (ch + pad)))
            res["img"].save(out / ("cover_%d_%s_%s.png" % (i, mode, tier)))
            ok = [cover_reads_as_material(res, c)[0] for c in sorted(cov)]
            lines.append("%s | %s | %s: reads_as_material %d/%d; matches_ground %s" % (
                name, mode, tier, sum(ok), len(ok), deck_matches_ground(res)))
    d.text((8, H - 24), "true geometry: 1 cell = %d px; pit 2 m deep, 3x3, faces/outline as RM_ExcavationWalls draws them "
           "(stand-in colours); ground world-aligned" % P, fill=(200, 200, 200), font=fc.font(13))
    sh.save(out / "SHEET_covers.png")
    (out / "checks.txt").write_text("\n".join(lines) + "\n")
    return out / "SHEET_covers.png", lines


if __name__ == "__main__":
    p, lines = sheet(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(p)
    print("\n".join(lines))
