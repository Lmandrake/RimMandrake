"""Composite the rail-mounted pit ladder (PIT_LADDER_RAILS_ON_THE_WALL, owner spec 2026-10-18) from two flat parts:

  rails   raw/<tag>_rails_front.png  (codex edit of guides/guide_rails_front.png; fixed to the wall in every state)
  ladder  ../raw/B_hung_north.png     (the 2026-10-16 face-on ladder master; slides on the rails)

Owner: "The wall mounted ladders should have "rails" on the wall that they attach to. The west/east wall mounts should
show the angled wall mounts with the ladder either in place or raised up out of reach of those below (empty rails
below). The north facing wall mount should show the whole apparatus very cleanly. the south facing one should be barely
visible when down and look like a ladder poking up when raised."

Rotation = the wall the ladder hangs on (RM_LadderWallMath.FX/FZ: 0 north +z = far wall, top of screen; 1 east +x;
2 south -z = near wall, bottom of screen; 3 west -x), the same convention as vanilla TorchWallLamp/WallLamp.

Both states are one canvas per facing: drawSize 1.5 (384 px, 256 px/cell), drawn with the def's per-rotation offset
(OFFSETS below, copied into FlowWorks_ThingDefs.xml), so the rails sit at the same pixels lowered and raised.

  north  face-on, whole apparatus; rail tops at the far rim; raised = ladder slid up 0.38 cell, poking above the rim
  south  the near wall's face is hidden: only what stands above the near rim shows (ladder seen from behind, darker);
         lowered = hook tips at the rim, raised = the ladder's top poking up
  east   the flat apparatus on the side wall, foreshortened and sheared (affine of the face-on view: far/north pole
         higher and darker), angled stand-off arms from every bracket to the wall line
  west   east mirrored

    python3 compose.py <tag> OUTDIR      -> RM_Ladder_<facing>.png, RM_LadderRaised_<facing>.png
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance

HERE = Path(__file__).resolve().parent
CELL = 256                     # px per cell in the shipped texture
CANVAS = 384                   # drawSize 1.5
SS = 4                         # supersample, then premultiplied BOX down
OFFSETS = {"north": (0, 0.25), "east": (0, 0.25), "south": (0, -0.25), "west": (0, 0.25)}   # (x, z) cells

# unit space: the face-on apparatus in "guide units" (guide_rails_front.png is 1024 u wide)
POLE_X = (320, 704)            # rail / pole centre lines
RAIL_LEN = 782                 # rails 0.9 x the ladder: the ladder pokes above the rails' top when down
LADDER_SCALE = 384 / 395       # B_hung_north.png pole spacing (430 -> 825 px) onto POLE_X
LADDER_LEN = 869               # its solid height after scaling (894 px)
T = 520                        # rails' top in unit space (room above for the raised ladder)
UW, UH = 1024, T + RAIL_LEN + 40
K = 0.75 * CELL / RAIL_LEN     # px (shipped) per unit: rails span 0.75 cell, rim to floor
RAISE = round(0.38 * CELL / K) # raised = slid up 0.38 cell
RAIL_SPREAD = 1.25
BRACKETS = (90, 380, 670, 930) # guide bracket heights (guide y, 24..1010 -> rails)


def rails_layer(tag):
    src = Image.open(HERE / "raw" / f"{tag}_rails_front.png").convert("RGBA")
    if src.size != (1024, 1024):
        src = src.resize((1024, 1024), Image.LANCZOS)
    a = src.getchannel("A").point(lambda v: 255 if v > 64 else 0)
    x0, y0, x1, y1 = a.getbbox()
    gx0, gy0, gx1, gy1 = 258, 24, 766, 1010                    # the guide's rails bbox
    # spread 1.25x about the centre so each rail and its brackets show outside the pole riding in it
    gw = round((gx1 - gx0) * RAIL_SPREAD)
    part = src.crop((x0, y0, x1, y1)).resize((gw, RAIL_LEN), Image.LANCZOS)
    out = Image.new("RGBA", (UW, UH), (0, 0, 0, 0))
    out.alpha_composite(part, (512 - gw // 2, T))
    return out


def bracket_ys():
    return [T + (y - 24) * RAIL_LEN / (1010 - 24) for y in BRACKETS]


def ladder_layer(raised):
    src = Image.open(HERE.parent / "raw" / "B_hung_north.png").convert("RGBA")
    w, h = src.size
    s = src.resize((round(w * LADDER_SCALE), round(h * LADDER_SCALE)), Image.LANCZOS)
    pole_mid = (430 + 825) / 2 * LADDER_SCALE
    foot = 914 * LADDER_SCALE
    out = Image.new("RGBA", (UW, UH), (0, 0, 0, 0))
    dy = (T + RAIL_LEN - 12) - foot - (RAISE if raised else 0)  # foot on the stop blocks when down
    out.alpha_composite(s, (round(512 - pole_mid), round(dy)))
    return out


def down(im):
    return im.convert("RGBa").resize((CANVAS, CANVAS), Image.BOX).convert("RGBA")


def clean(im):
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    return im


def place(layer, scale, top_px, cx_px=CANVAS / 2):
    """Uniform scale of unit space onto the SS canvas: unit y=T lands on top_px, unit x=512 on cx_px."""
    big = Image.new("RGBA", (CANVAS * SS, CANVAS * SS), (0, 0, 0, 0))
    s = scale * SS
    lw, lh = round(UW * s), round(UH * s)
    l = layer.resize((lw, lh), Image.LANCZOS)
    big.alpha_composite(l, (round(cx_px * SS - 512 * s), round(top_px * SS - T * s)))
    return big


def north(rails, ladder):
    big = place(rails, K, 128)
    big.alpha_composite(place(ladder, K, 128))
    return clean(down(big))


def south(rails, ladder):
    rim = 256                                                  # near rim: cell bottom edge (offset z -0.25)
    back = ImageEnhance.Brightness(ladder.transpose(Image.FLIP_LEFT_RIGHT)).enhance(0.62)
    big = place(rails, K, rim - 4)                             # rails' top caps just show at the rim
    big.alpha_composite(place(back, K, rim))
    # everything below the near rim is behind the earth: cut, with a short darkening at the cut
    px = big.load()
    cut = rim * SS
    for y in range(cut - 6 * SS, CANVAS * SS):
        for x in range(CANVAS * SS):
            r, g, b, a = px[x, y]
            if not a:
                continue
            if y >= cut:
                px[x, y] = (0, 0, 0, 0)
            else:
                k = 0.55 + 0.45 * (cut - y) / (6 * SS)
                px[x, y] = (int(r * k), int(g * k), int(b * k), a)
    return clean(down(big))


def east(rails, ladder):
    """Affine of the face-on apparatus onto the east wall: x squashed, far (north = left) pole higher and darker."""
    SQ, SH = 0.40, 0.25
    flat = Image.new("RGBA", (UW, UH), (0, 0, 0, 0))
    flat.alpha_composite(rails)
    flat.alpha_composite(ladder)
    # far side darker: brightness ramp across unit x
    ramp = Image.linear_gradient("L").rotate(90, expand=True).resize((UW, UH))   # 255 left .. 0 right
    dark = ImageEnhance.Brightness(flat).enhance(0.62)
    shade = Image.composite(dark, flat, ramp.point(lambda v: int(v * 0.85)))
    shade.putalpha(flat.getchannel("A"))
    s = K * SS
    right = (CANVAS / 2 + CELL / 2 - 22) * SS                 # stand-off from the east wall line: the arms show
    top = 140 * SS
    # forward map: X = ox + SQ*s*u,  Y = oy + s*v + SH*s*(u-512)   (left/north pole higher)
    ox = right - SQ * s * (512 + 254 * RAIL_SPREAD)
    oy = top - s * T
    A, B = SQ * s, SH * s                                      # inverse for PIL: u = aX + bY + c, v = dX + eY + f
    coef = (1 / A, 0, -ox / A, -B / (A * s), 1 / s, (-oy + B * ox / A + 512 * B) / s)
    big = shade.transform((CANVAS * SS, CANVAS * SS), Image.AFFINE, coef,
                          resample=Image.BICUBIC)
    # angled stand-off arms: from each bracket on both rails to the wall line, drawn behind
    arms = Image.new("RGBA", big.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(arms)
    wall_x = (CANVAS / 2 + CELL / 2) * SS
    for i, px_ in enumerate(POLE_X):
        ux = 512 + (px_ - 512) * RAIL_SPREAD
        col = (70, 56, 44, 255) if i == 0 else (118, 96, 74, 255)      # far (north) rail's arms darker
        for vy in bracket_ys():
            X = ox + SQ * s * (ux + 62 * RAIL_SPREAD)
            Y = oy + s * vy + SH * s * (ux - 512)
            d.line([(X - 2 * SS, Y - 3 * SS), (wall_x, Y + 4 * SS)], fill=col, width=5 * SS)
            d.line([(X - 2 * SS, Y + 3 * SS), (wall_x, Y + 4 * SS)], fill=col, width=4 * SS)
            d.ellipse([wall_x - 3 * SS, Y + 1 * SS, wall_x + 2 * SS, Y + 7 * SS], fill=(35, 28, 22, 255))
    arms.alpha_composite(big)
    return clean(down(arms))


def main(tag, outdir):
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    rails = rails_layer(tag)
    for raised, name in ((False, "RM_Ladder"), (True, "RM_LadderRaised")):
        lad = ladder_layer(raised)
        e = east(rails, lad)
        faces = {"north": north(rails, lad), "south": south(rails, lad), "east": e,
                 "west": e.transpose(Image.FLIP_LEFT_RIGHT)}
        for f, im in faces.items():
            im.save(out / f"{name}_{f}.png")
            print(name, f, im.size, im.getchannel("A").getbbox())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
