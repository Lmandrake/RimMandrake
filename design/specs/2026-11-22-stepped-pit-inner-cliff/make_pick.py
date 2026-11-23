"""The one pick image for the owner: in game today, the build before the shelf fix (option B, his narrow north shelf), and
the build now; his L and the 2 m / 6 m step, close, plus a default-zoom row. Warm dark-brown background; no text but the
column labels. (Its first version showed options A and B; he accepted the shadows and flagged the narrow shelf, 2026-11-22.)

    python3 make_pick.py <tex_dir> <captures_dir> <out.png>

captures_dir is the earlier item's ArchSmall captures (close_a_his_L_8m_with_4m_L.png, close_b_straight_step_2m_north_6m_south.png,
default_zoom_area_crop.png; 2026-11-22). The options are drawn by render.py from pitrule.py.
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as Rr  # noqa: E402

BG = (44, 32, 23)
TEXT = (236, 214, 172)
PPC = 110          # close rows, px a square
DZ = 24            # the default zoom, px a square (measured on the capture: a 3-square pit is 72 px)
COLS = [("In game today", None), ("Before  narrow shelf", "before"), ("Now  shelf fixed", "now")]
BEFORE = dict(NORTH_TABLE=[0.0, 0.12, 0.23, 0.35, 0.50, 0.62], H_TOP=0.97, SHADOW_K=0.15)   # the rule as first built (ea50968f56)
L = Rr.CASES["his L: 4 m L in 8 m"]
STEP = Rr.CASES["step 2 m / 6 m (E-W edge)"]


def main(tex, caps, out):
    today_L = Image.open(os.path.join(caps, "close_a_his_L_8m_with_4m_L.png")).convert("RGB").resize((5 * PPC, 5 * PPC), Image.LANCZOS)
    today_S = Image.open(os.path.join(caps, "close_b_straight_step_2m_north_6m_south.png")).convert("RGB").resize((6 * PPC, 6 * PPC), Image.LANCZOS)
    dz = Image.open(os.path.join(caps, "default_zoom_area_crop.png")).convert("RGB")
    today_dL = dz.crop((60, 84, 60 + 5 * DZ, 84 + 5 * DZ))
    today_dS = dz.crop((206, 59, 206 + 6 * DZ, 59 + 6 * DZ))
    cells = []
    for label, opt in COLS:
        if opt is None:
            cells.append((label, today_L, today_S, today_dL, today_dS))
        else:
            saved = {k: getattr(Rr.R, k) for k in BEFORE}
            saved_rk, saved_reach = Rr.SHADOW_K, Rr.R.SHADOW_REACH
            if opt == "before":
                for k, v in BEFORE.items():
                    setattr(Rr.R, k, list(v) if isinstance(v, list) else v)
                Rr.SHADOW_K = BEFORE["SHADOW_K"]
                Rr.R.SHADOW_REACH = Rr.R.SHADOW_K * Rr.R.DEEPEST ** Rr.R.SHADOW_POW + Rr.R.MARCH_STEP
            Rr.retable()
            try:
                cells.append((label, Rr.render(L, "NW", tex, PPC), Rr.render(STEP, "NW", tex, PPC),
                              Rr.render(L, "NW", tex, DZ), Rr.render(STEP, "NW", tex, DZ)))
            finally:
                for k, v in saved.items():
                    setattr(Rr.R, k, v)
                Rr.SHADOW_K, Rr.R.SHADOW_REACH = saved_rk, saved_reach
                Rr.retable()
    colw = 6 * PPC
    gap = 40
    head = 70
    rows_h = [5 * PPC, 6 * PPC, 6 * DZ * 2]
    W = gap + len(cells) * (colw + gap)
    H = head + sum(rows_h) + gap * (len(rows_h) + 1)
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    f = Rr.font(40)
    for i, (label, cL, cS, dL, dS) in enumerate(cells):
        x = gap + i * (colw + gap)
        dr.text((x, 16), label, fill=TEXT, font=f)
        y = head + gap
        sheet.paste(cL, (x + (colw - cL.width) // 2, y))
        y += rows_h[0] + gap
        sheet.paste(cS, (x, y))
        y += rows_h[1] + gap
        d1 = dL.resize((dL.width * 2, dL.height * 2), Image.NEAREST)
        d2 = dS.resize((dS.width * 2, dS.height * 2), Image.NEAREST)
        pad = (colw - d1.width - d2.width) // 3
        sheet.paste(d1, (x + pad, y + (rows_h[2] - d1.height) // 2))
        sheet.paste(d2, (x + 2 * pad + d1.width, y))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(*sys.argv[1:4])
