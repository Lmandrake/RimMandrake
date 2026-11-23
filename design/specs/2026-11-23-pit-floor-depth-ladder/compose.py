"""One before/after image of the pit depth ladder from two live_look.py runs (RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR).

    python3 compose.py <captures_dir> <out.png>

Each row (before, after): the ladder row at default zoom with a colonist at its west end, then close captures of the 2, 3, 4,
8 and 16 m pits, then his L (case 1) close. Labels name the depth. A picture of captures; nothing here judges.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

CLOSE = [2, 3, 4, 8, 16]


def font(sz):
    f = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(f, sz) if os.path.exists(f) else ImageFont.load_default()


def fit_h(im, h):
    return im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS)


def tag(im, text):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 9 * len(text) + 10, 20), fill=(250, 250, 250))
    d.text((5, 3), text, fill=(0, 0, 0), font=font(14))
    return im


def row(cap, t):
    parts = []
    lad = Image.open(os.path.join(cap, "%s_ladder_default_day.png" % t)).convert("RGB")
    parts.append(tag(fit_h(lad, 170), "default zoom: 2 3 4 6 8 12 16 m, colonist at left"))
    for m in CLOSE:
        p = os.path.join(cap, "%s_ladder_close_%02dm.png" % (t, m))
        if os.path.exists(p):
            parts.append(tag(fit_h(Image.open(p).convert("RGB"), 170), "%d m" % m))
    p = os.path.join(cap, "%s_case_close_01.png" % t)
    if os.path.exists(p):
        im = Image.open(p).convert("RGB")
        # the case sits in the slot's north-west; the rest of the 8-square slot is bare ground (and the colonist above it)
        im = im.crop((0, 0, int(im.width * 0.62), int(im.height * 0.62)))
        parts.append(tag(fit_h(im, 170), "his L: 4 m in 8 m"))
    w = sum(x.width for x in parts) + 8 * (len(parts) - 1)
    out = Image.new("RGB", (w, 170), (30, 24, 18))
    x = 0
    for p_ in parts:
        out.paste(p_, (x, 0))
        x += p_.width + 8
    return out


def main(cap, out):
    rows = [("BEFORE (shipped): 2 m floor at 0.38 of the ground; 3 m vs 4 m and 8 m vs 16 m alike", row(cap, "before")),
            ("AFTER: 2 m floor lifted, grain kept to 16 m, north face taller with depth (3 m vs 4 m by the wall)", row(cap, "after"))]
    W = max(r.width for _, r in rows) + 20
    H = sum(r.height + 34 for _, r in rows) + 44
    s = Image.new("RGB", (W, H), (30, 24, 18))
    d = ImageDraw.Draw(s)
    d.text((10, 8), "FlowWorks dry pit floors by depth, in game (ArchBig on a 23-mod tier, 14 h sun; save RM_PIT_DEPTH_LADDER_AFTER)", fill=(240, 220, 180), font=font(20))
    y = 44
    for t, r in rows:
        d.text((10, y), t, fill=(230, 210, 170), font=font(15))
        s.paste(r, (10, y + 24))
        y += r.height + 34
    s.save(out)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
