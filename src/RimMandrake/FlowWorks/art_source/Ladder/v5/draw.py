"""Ladder art v5 (owner 2026-10-23/24, three items):

  PORTABLE_LADDER_FIX_EW_LIES_ALONG_WALL ("OBVIOUSLY broken"): the portable ladder's east/west facings were drawn running
      north-south along the side wall. v5 re-projects the kept redraw-8 art (the same source v4 used for the steeper north)
      by a homography onto a lean that runs EAST-WEST: foot on the pit floor off the face, top over the rim. West = east
      mirrored. North/south facings are unchanged.
  RAIL_LADDER_REDRAW_FAT_RUNG_FENCE (owner by card "Send it back first"; liked "North wall x2 after"): the v4 steel north
      lowered view is kept as drawn. Raised north no longer floats: the ladder slides up only so far that its foot stays in
      the guide rails (slide clips on the rails), its top standing up past the rim between the goosenecks. Rails get a rim
      anchor plate each. East/west: steeper lean that stays on the side wall face (short run, tall rise).
  LADDER_TEXT_RECONCILE_STEEL_NOT_WOOD (owner by card "Steel and wood versions"): the same thin shape in two palettes.
      Steel -> RM_LadderSteel / RM_LadderSteelRaised (new def RM_LadderSteel); wood -> RM_Ladder / RM_LadderRaised
      (timber stringers and rails, iron brackets and hooks).

Rig unchanged (both rail defs, the portable): Graphic_Multi, 384 px canvas, drawSize 1.5 -> 256 px per cell, offsets
N/E/W (0,0,+0.25), S (0,0,-0.25). On the E/W canvas the cell spans x 64..320, y 128..384; the east rim is x 320.

    python3 draw.py   -> out/*.png
"""
import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "v4"))
import draw as v4                      # noqa: E402  (Pen, bar, rung, gooseneck, rung_rows, shadowed, finish, homography)
from draw import Pen, bar, rung, gooseneck, rung_rows, shadowed, finish, lerp, x_at, homography, S, C  # noqa: E402

OUT = HERE / "out"

STEEL = dict(OUTL=(14, 14, 16, 255), RAIL=(52, 54, 58, 255), RAIL_HI=(118, 122, 128, 255), STR=(66, 68, 73, 255),
             STR_HI=(146, 150, 156, 255), RUNG=(88, 88, 90, 255), RUNG_HI=(190, 186, 178, 255), BOLT=(150, 146, 138, 255),
             HOOK=(52, 54, 58, 255), HOOK_HI=(118, 122, 128, 255), rung_d=3.8, str_w=(5.4, 4.8), rail_w=(6.6, 5.8))
WOOD = dict(OUTL=(34, 20, 10, 255), RAIL=(104, 68, 38, 255), RAIL_HI=(170, 122, 74, 255), STR=(128, 86, 48, 255),
            STR_HI=(196, 146, 92, 255), RUNG=(142, 98, 56, 255), RUNG_HI=(214, 170, 112, 255), BOLT=(120, 116, 108, 255),
            HOOK=(58, 58, 62, 255), HOOK_HI=(130, 132, 136, 255), rung_d=4.6, str_w=(6.2, 5.6), rail_w=(7.4, 6.6))

CX, RIM, FOOT = v4.CX, v4.RIM, v4.FOOT
RAIL_HALF, LAD_HALF = v4.RAIL_HALF, v4.LAD_HALF
# contact shadow: tight and faint (judge 2026-10-24 ALPHA_HALO: v4's 95-alpha offset read as a grey ghost on the band)
SHADOW = dict(dx=1, dy=2, alpha=52, blur=1.1)   # dx, dy whole canvas px (v4 pastes at S(dx))
RAISE_N = 62                          # raised slide: the ladder foot stays inside the rails (rails end at FOOT+2)


# ---------------------------------------------------------------- north (lowered = v4 geometry)
def north_rails(P):
    pen = Pen()
    top, bot = RIM - 6, FOOT + 2
    for side in (-1, 1):
        xt, xb = CX + side * x_at(RAIL_HALF, top), CX + side * x_at(RAIL_HALF, bot)
        bar(pen, (xt, top), (xb, bot), *P["rail_w"], P["RAIL"], P["RAIL_HI"], P["OUTL"])
        for yb in (RIM + 12, (RIM + FOOT) / 2 + 4, FOOT - 8):     # wall brackets, bolted to the face
            xr = CX + side * x_at(RAIL_HALF, yb)
            bar(pen, (xr - 6.5, yb), (xr + 6.5, yb), 4.2, 4.2, P["HOOK"], P["HOOK_HI"], P["OUTL"], hi_side=1)
            pen.disc((xr + side * 4.5, yb), 1.1, P["BOLT"])
        # rim anchor plate: the rail is bolted down at the lip, not hanging loose
        bar(pen, (xt - 7, RIM - 1), (xt + 7, RIM - 1), 3.6, 3.6, P["HOOK"], P["HOOK_HI"], P["OUTL"], hi_side=1)
        pen.disc((xt - side * 4.5, RIM - 1), 1.1, P["BOLT"])
        gooseneck(pen, xt, top, side, 5.4, P["HOOK"], P["HOOK_HI"], P["OUTL"], rise=10, reach=12)
    return pen.im


def north_ladder(P, dy=0, n_rungs=7, rung_k=1.0, ratio=0.88, str_k=1.0):
    pen = Pen()
    top, bot = RIM - 8, FOOT - 2
    for y in rung_rows(RIM + 7, FOOT - 10, n_rungs, ratio):
        rung(pen, CX - x_at(LAD_HALF, y), CX + x_at(LAD_HALF, y), y + dy, P["rung_d"] * rung_k, P["RUNG"], P["RUNG_HI"], P["OUTL"])
    for side in (-1, 1):
        xt, xb = CX + side * x_at(LAD_HALF, top), CX + side * x_at(LAD_HALF, bot)
        bar(pen, (xt, top + dy), (xb, bot + dy), *[w * str_k for w in P["str_w"]], P["STR"], P["STR_HI"], P["OUTL"])
        pen.disc((xb, bot + dy + 1), 3.0, P["OUTL"])
        pen.disc((xb, bot + dy + 1), 1.9, P["STR"])
        pen.disc((xt, top + dy), 3.6, P["OUTL"])
        pen.disc((xt, top + dy), 2.3, P["STR_HI"])
        # slide clips: two short shoes from the stringer out to its rail, near the ladder foot (they move with it)
        for yc in (bot - 30, bot - 6):
            y = yc + dy
            xs = CX + side * x_at(LAD_HALF, yc)
            xr = CX + side * x_at(RAIL_HALF, y)
            bar(pen, (xs, y), (xr, y), 3.2, 3.2, P["HOOK"], P["HOOK_HI"], P["OUTL"], hi_side=1)
    return pen.im


def wood_grain(im, seed=7):
    """Painterly grain on the timber (saturated warm pixels only; iron stays smooth): fine mottling plus streaks along
    the stringers (screen-vertical in the north view; turned with it for the side views)."""
    import numpy as np
    from PIL import ImageFilter
    rng = np.random.default_rng(seed)
    h, w = im.size[1], im.size[0]
    n = Image.fromarray((rng.random((h, w)) * 255).astype(np.uint8), "L")
    streak = np.asarray(n.resize((w // 3, h // 24), Image.BILINEAR).resize((w, h), Image.BICUBIC), dtype=np.float64)
    fine = np.asarray(n.filter(ImageFilter.GaussianBlur(S(0.6))), dtype=np.float64)
    g = (streak - streak.mean()) / (streak.std() + 1e-6) * 0.07 + (fine - fine.mean()) / (fine.std() + 1e-6) * 0.04
    a = np.asarray(im, dtype=np.float64)
    r, gg, b = a[..., 0], a[..., 1], a[..., 2]
    warm = ((r - b) > 30) & (a[..., 3] > 0)
    a[..., :3] = np.where(warm[..., None], a[..., :3] * (1 + g)[..., None], a[..., :3])
    return Image.fromarray(np.clip(a, 0, 255).round().astype(np.uint8), "RGBA")


def rail_north(P, raised, **ladder_kw):
    im = shadowed(north_rails(P), **SHADOW)
    im.alpha_composite(shadowed(north_ladder(P, -RAISE_N if raised else 0, **ladder_kw), **SHADOW))
    return finish(wood_grain(im) if P is WOOD else im)


# ---------------------------------------------------------------- east/west: the north view turned onto the side wall
# Owner 2026-10-24: "The ladders are running north/south rather then up/down!!!" and "east and west needs to have a steeper
# perspective ... It should not extend into the dark of the pit." The pit is drawn with its wall faces as bands that slope
# toward the pit centre: on the north wall "down the wall" is screen-down, on the east wall it is screen-LEFT (the east
# face band is about x 262..320). So the east facing is the north facing turned a quarter clockwise (rim end east, rungs
# running north-south along the wall) and squeezed into the face band: rim row 128 -> x 320, depth row d -> 320 - SIDE_S*d.
# The squeeze is the steepness; the ladder's width (north-south on screen) is kept. West = east mirrored.
SIDE_S = 0.47                         # foot end lands at x ~262, the band's inner edge, not on the dark floor


def side_from_north(north, s=SIDE_S, ss=4):
    import numpy as np
    a = np.asarray(north.convert("RGBA"), dtype=np.float64)
    a[..., :3] *= a[..., 3:4] / 255.0
    pm = Image.fromarray(a.round().astype(np.uint8), "RGBA").resize((C * ss, C * ss), Image.BICUBIC)
    # inverse map, output (X, Y) -> input (x, y), in ss-scaled pixels: x = 192 + (Y - 256); y = 128 + (320 - X) / s
    f = ss
    coeff = (0.0, 1.0, f * (192 - 256), -1.0 / s, 0.0, f * 128 + f * 320 / s)
    w = pm.transform(pm.size, Image.AFFINE, coeff, Image.BICUBIC).resize((C, C), Image.LANCZOS)
    b = np.asarray(w, dtype=np.float64)
    al = b[..., 3:4]
    b[..., :3] = np.where(al > 0, b[..., :3] * 255.0 / np.maximum(al, 1), 0)
    return Image.fromarray(np.clip(b, 0, 255).round().astype(np.uint8), "RGBA")


def rail_east(P, raised):
    # Squeezed to half its depth, seven rungs read as a fence (the owner's FAT_RUNG_FENCE): five, drawn rounder, gaps
    # narrowing faster with depth (the squeeze hides the north view's 0.88), stringers thicker (side face shows).
    # Raised: on the side wall "up the wall" is screen-right (east), so the slid-up top continues east past the rim the
    # way the north view's raised top continues screen-up past the north rim.
    return side_from_north(rail_north(P, raised, n_rungs=5, rung_k=1.6, ratio=0.72, str_k=1.6))


# ---------------------------------------------------------------- south (near rim at row 256): v4 shape, palette
S_RIM, S_HALF = 256, 62


def rail_south(P, raised):
    pen = Pen()
    if raised:
        top = S_RIM - 66
        for y in rung_rows(S_RIM - 6, top + 10, 4, 1.06):
            k = (S_RIM - y) / (S_RIM - top)
            h = lerp(LAD_HALF[0], LAD_HALF[0] + 3, k)
            rung(pen, CX - h, CX + h, y, P["rung_d"] * .95, P["RUNG"], P["RUNG_HI"], P["OUTL"])
        for side in (-1, 1):
            bar(pen, (CX + side * LAD_HALF[0], S_RIM + 1), (CX + side * (LAD_HALF[0] + 3), top), 4.6, 5.0,
                P["STR"], P["STR_HI"], P["OUTL"])
            pen.disc((CX + side * (LAD_HALF[0] + 3), top), 3.8, P["OUTL"])
            pen.disc((CX + side * (LAD_HALF[0] + 3), top), 2.4, P["STR_HI"])
    for side in (-1, 1):
        bar(pen, (CX + side * S_HALF - 7, S_RIM + 1), (CX + side * S_HALF + 7, S_RIM + 1), 3.6, 3.6,
            P["HOOK"], P["HOOK_HI"], P["OUTL"], hi_side=1)
        gooseneck(pen, CX + side * S_HALF, S_RIM + 1, side, 5.4, P["HOOK"], P["HOOK_HI"], P["OUTL"], rise=11, reach=12)
    return finish(shadowed(pen.im, **SHADOW))


# ---------------------------------------------------------------- portable east/west: the kept north facing, turned
TEX = HERE.parents[2] / "Textures" / "Things" / "Building" / "FlowWorks" / "Canals"


def portable_east():
    return side_from_north(Image.open(TEX / "RM_LadderPortable_north.png"), s=0.42)   # a leaned ladder: steeper still


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    outs = {}
    for name, P in (("RM_Ladder", WOOD), ("RM_LadderSteel", STEEL)):
        raised = name.replace("RM_Ladder", "RM_LadderRaised") if name == "RM_Ladder" else "RM_LadderSteelRaised"
        for r, tag in ((False, name), (True, raised)):
            outs[f"{tag}_north"] = rail_north(P, r)
            outs[f"{tag}_east"] = rail_east(P, r)
            outs[f"{tag}_south"] = rail_south(P, r)
            outs[f"{tag}_west"] = outs[f"{tag}_east"].transpose(Image.FLIP_LEFT_RIGHT)
    outs["RM_LadderPortable_east"] = portable_east()
    outs["RM_LadderPortable_west"] = outs["RM_LadderPortable_east"].transpose(Image.FLIP_LEFT_RIGHT)
    for k, im in outs.items():
        bb = im.getchannel("A").getbbox()
        assert bb and bb[0] > 0 and bb[1] > 0 and bb[2] < C and bb[3] < C, (k, bb)
        im.save(OUT / f"{k}.png")
        print(k, bb)


if __name__ == "__main__":
    main()
