"""Offline mocks for the P9 water review (WATER_DEPTH_RESKIN_HE_LOOKS_FIRST + children). Writes only into its own img/ folder.
   python3 make_water_art.py   (inputs: the two live screenshots; very-shallow candidates come from art_source/WaterThin)"""
import sys, numpy as np
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw, ImageFont
HERE = Path(__file__).resolve().parent; OUT = HERE / "img"; OUT.mkdir(exist_ok=True)
LIVE = Path("/home/mandrake/rm/foundry/Transient/fw_scenes/live")
REPO = HERE.parents[2]
rng = np.random.default_rng(17)
def font(n):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", n)
    except Exception: return ImageFont.load_default()
def label(im, text):
    d = ImageDraw.Draw(im); f = font(22); w = d.textlength(text, font=f)
    d.rectangle([0, 0, w + 14, 32], fill=(0, 0, 0)); d.text((7, 4), text, fill=(255, 255, 255), font=f); return im
def hstack(ims, gap=8):
    h = max(i.height for i in ims); w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    o = Image.new("RGB", (w, h), (20, 20, 20)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width + gap
    return o

# ---------------- job 1: canal vs lake ----------------
S = 3467 / 2000
def px(v): return int(round(v * S))
src = np.array(Image.open(LIVE / "S2_p60.png").convert("RGB")).astype(np.float32)
CROP = (px(672), px(392), px(1180), px(664))      # lake + canal square + strip
cr = src[CROP[1]:CROP[3], CROP[0]:CROP[2]].copy(); H, W, _ = cr.shape
def rect(x0, y0, x1, y1): return (px(x0) - CROP[0], px(y0) - CROP[1], px(x1) - CROP[0], px(y1) - CROP[1])
R_SQ = rect(979, 495, 1021, 537); R_ST = rect(1021, 517, 1153, 537)
canal = np.zeros((H, W), bool)
for x0, y0, x1, y1 in (R_SQ, R_ST): canal[y0 + 2:y1 - 2, x0 + 2:x1 - 2] = True
lakem = np.zeros((H, W), bool); lx1 = px(978) - CROP[0]; lakem[px(402) - CROP[1]:px(648) - CROP[1], 4:lx1 - 4] = True
lake_mean = cr[lakem].mean(0); lake_std = cr[lakem].std(0)
print("lake mean", lake_mean.round(1), "sq", cr[canal][:0], )
soil = src[px(560):px(640), px(1100):px(1250)]; soil_mean = soil.reshape(-1, 3).mean(0)
def tile_soil(h, w):
    ph, pw = soil.shape[:2]; return np.tile(soil, (h // ph + 1, w // pw + 1, 1))[:h, :w]
SOIL = tile_soil(H, W)
def save(a, name, text=None):
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    if text: label(im, text)
    im.save(OUT / name); return im
orig = save(cr, "canal_0_now.png", "now: lake (left) vs canal (right)")
# A tint: shift canal colour to the lake mean, keep its (flat) texture
A = cr.copy()
for r in (R_SQ, R_ST):
    m = np.zeros((H, W), bool); x0, y0, x1, y1 = r; m[y0 + 2:y1 - 2, x0 + 2:x1 - 2] = True
    A[m] = A[m] - cr[m].mean(0) + lake_mean
save(A, "canal_A_tint.png", "A: tint canal to the lake colour")
# B same texture as the lake (what the same ramp + depth shader gives): lake pixels sampled into the canal
lake_tex = cr[px(410) - CROP[1]:px(640) - CROP[1], 6:lx1 - 6]
def lake_at(h, w, ox=0, oy=0):
    th, tw = lake_tex.shape[:2]; yy = (np.arange(h)[:, None] + oy) % th; xx = (np.arange(w)[None, :] + ox) % tw; return lake_tex[yy, xx]
LT = lake_at(H, W, 37, 11)
B = cr.copy(); B[canal] = LT[canal]
save(B, "canal_B_lake_texture.png", "B: canal uses the lake's wavy texture")
# C = B + FadeRough soft rough edge on the canal
mask = np.zeros((H, W), np.float32)
for x0, y0, x1, y1 in (R_SQ, R_ST): mask[y0:y1, x0:x1] = 1
ex = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))
soft = np.array(ex).astype(np.float32) / 255
noise = np.array(Image.fromarray(rng.integers(0, 255, (H // 6 + 1, W // 6 + 1), dtype=np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))).astype(np.float32) / 255
alpha = np.clip((soft - 0.30) / 0.35 + (noise - 0.5) * 0.9 * (soft > .02) * (soft < .98), 0, 1)
alpha = alpha * (mask > 0.0) + (soft * 0) ; alpha = np.where(soft > 0.97, 1, alpha)
C = cr.copy(); under = cr.copy(); under[mask > 0.5] = SOIL[mask > 0.5]
Ccanal = LT
sel = soft > 0.02
C = np.where((sel)[..., None], under * (1 - alpha[..., None]) + Ccanal * alpha[..., None], cr)
C = np.where(lakem[..., None] | (np.arange(W)[None, :, None] < lx1 + 4), cr, C)
save(C, "canal_C_lake_texture_fadeRough.png", "C: lake texture + rough soft edge (FadeRough)")
hstack([orig, Image.open(OUT / "canal_B_lake_texture.png")]) if False else None

# ---------------- job 4: deep lake tints ----------------
lk = cr[px(402) - CROP[1]:px(648) - CROP[1], 4:lx1 - 4]
def strip(fn, names, name):
    tiles = [label(Image.fromarray(np.clip(fn(lk, i), 0, 255).astype(np.uint8)), n) for i, n in enumerate(names)]
    hstack(tiles).save(OUT / name)
names = ["2 m (vanilla deep now)", "5 m+", "10 m+"]
f1 = [1.0, .78, .58]
strip(lambda a, i: a * f1[i], names, "deep_T1_darker.png")
navy = np.array([28, 40, 66], np.float32); f2 = [0.0, .42, .70]
strip(lambda a, i: (a * (1 - .25 * i) * (1 - f2[i]) + navy * f2[i] * (1 + .0)) if i else a, names, "deep_T2_navy.png")
tint3 = [np.array([1, 1, 1]), np.array([.74, .80, .92]), np.array([.50, .60, .82])]
strip(lambda a, i: a * tint3[i], names, "deep_T3_blue_shift.png")
for n in ("deep_T1_darker.png", "deep_T2_navy.png", "deep_T3_blue_shift.png"): pass

# ---------------- job 3: wall band over art_strip ----------------
strp = np.array(Image.open(LIVE / "art_strip_labeled.png").convert("RGB")).astype(np.float32)
cols = [453, 652, 851, 1050, 1249]; rows = {2.0: 280, 1.5: 429, 1.0: 578, 0.5: 728}; wat = [0, .5, 1, 1.5, 2]
SC = (px(440), px(262), px(1316), px(790))
def band_mock(style):
    a = strp.copy()
    for hole, ry in rows.items():
        for ci, w in enumerate(wat):
            if w <= 0 or w > hole: continue
            gap = hole - w
            x0, y0 = px(cols[ci]), px(ry); c = px(48)
            if gap <= 0: continue
            t = max(3, int(c * 0.34 * gap / 2.0 * (1 if style != 2 else 1)))
            t = min(t, c // 2)
            if style == 1:      # north+west inner shadow band, dark wall brown, fading toward the water
                for k in range(t):
                    f = 0.75 * (1 - k / t)
                    a[y0 + k, x0:x0 + c] = a[y0 + k, x0:x0 + c] * (1 - f) + np.array([48, 34, 24]) * f
                    a[y0:y0 + c, x0 + k] = a[y0:y0 + c, x0 + k] * (1 - f * .8) + np.array([48, 34, 24]) * f * .8
            elif style == 2:    # lit soil wall face, hard-edged, one metre-line per half metre of gap
                face = np.array([128, 96, 66]); 
                a[y0:y0 + t, x0:x0 + c] = face; a[y0:y0 + c, x0:x0 + t] = face * .85
                for m in range(1, int(round(gap / 0.5))):
                    yy = y0 + int(t * m / (gap / 0.5)); a[yy, x0:x0 + c] = (70, 50, 34)
            else:               # all four sides, thin, darkest at the water line
                for k in range(t):
                    f = 0.6 * (k + 1) / t
                    col = np.array([40, 30, 22])
                    for sl in (np.s_[y0 + k, x0:x0 + c], np.s_[y0 + c - 1 - k, x0:x0 + c], np.s_[y0:y0 + c, x0 + k], np.s_[y0:y0 + c, x0 + c - 1 - k]):
                        a[sl] = a[sl] * (1 - f * .8) + col * f * .8
    return a[SC[1]:SC[3], SC[0]:SC[2]]
save(strp[SC[1]:SC[3], SC[0]:SC[2]], "wall_0_now.png", "now: wet cells show only the water")
save(band_mock(1), "wall_1_shadow_band.png", "1: soft shadow band on the north and west edge")
save(band_mock(2), "wall_2_lit_face_lines.png", "2: lit wall face, a line per half metre")
save(band_mock(3), "wall_3_thin_ring.png", "3: thin shadow ring, darkest at the water")

# ---------------- job 2: very shallow candidates ----------------
sys.path.insert(0, str(REPO / "src/RimMandrake/FlowWorks/art_source/WaterThin"))
code = (REPO / "src/RimMandrake/FlowWorks/art_source/WaterThin/make_water_thin.py").read_text()
code = code.replace("    out = bed * (1 - depth", "    depth = depth * DK\n    out = bed * (1 - depth", 1).replace("* .045\n", "* .045 * SK\n", 1)
assert "DK" in code and "SK" in code
def gen(dk, sk):
    g = {"__name__": "wt", "DK": dk, "SK": sk}; exec(compile(code, "make_water_thin", "exec"), g); return g["make"]()
cands = {"VS1_wet_bed": (0.0, 3.0), "VS2_faint_veil": (0.28, 1.6), "VS3_half_veil": (0.55, 1.0), "now_WaterThin_0p5m": (1.0, 1.0)}
tex = {}
for n, (dk, sk) in cands.items():
    a = gen(dk, sk) * 255; tex[n] = a; Image.fromarray(a.astype(np.uint8)).save(OUT / (n + "_tex1024.png"))
    print(n, a.reshape(-1, 3).mean(0).round(1))
CELL = 96     # px per cell in the previews (1024 px tile = 8 cells => 128 px/cell; shown at 96)
def cellpatch(a, cells=3):
    t = Image.fromarray(a.astype(np.uint8)).resize((1024 * CELL // 128, 1024 * CELL // 128), Image.LANCZOS); return t.crop((0, 0, cells * CELL, cells * CELL))
# the drying ladder: dry mud | VS | thin (0.5 m) , 3x3 cells each
mud = gen(0.0, 0.0) * 255  # bed only, no veil, no sheen
shallow = np.array(Image.open(REPO.parent.parent / "foundry/Transient/water_thin_2026-10-16/work/WaterShallow_approx.png").convert("RGB")).astype(np.float32) if False else None
wt = LIVE.parent.parent / "water_thin_2026-10-16/work"
shallow = np.array(Image.open(wt / "WaterShallow_approx.png").convert("RGB")); deep = np.array(Image.open(wt / "WaterDeep_approx.png").convert("RGB"))
for n in ("VS1_wet_bed", "VS2_faint_veil", "VS3_half_veil"):
    parts = [("dry mud", mud), ("<25 cm: " + n, tex[n]), ("0.5 m (RM_WaterThin now)", tex["now_WaterThin_0p5m"]), ("1 m vanilla shallow", shallow), ("2 m vanilla deep", deep)]
    hstack([label(cellpatch(np.asarray(t), 2), l) for l, t in parts]).save(OUT / (n + "_ladder.png"))
# user view of a candidate at in-game cell size on a mud ground: the 3x3 cell patch alone (scale panel)
for n in cands: cellpatch(tex[n], 3).save(OUT / (n + "_3x3cells.png"))
print("done")
