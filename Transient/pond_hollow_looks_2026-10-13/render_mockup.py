"""Offline mockup: one drained pond bed (rim depth 2, middle depth 4) shown three ways.
POND_HOLLOW_DESIGN_THREE_LOOKS_ONE_BED. No game. Wall faces/sink approximate the live code's numbers
(RM_WallFaceMath NorthByDrop/SideByDrop/SouthLiningByDrop/FootDarkness, pitSinkPerLevel 0.3)."""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = "/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures/ludeon.rimworld.core"
PX = 32                      # pixels per cell
TILE_CELLS = 8               # one 1024 terrain texture spans 8 cells (approximation)
W, H = 30, 22                # map cells per panel
NORTH = [0, .12, .23, .35, .50]; SIDE = [0, .06, .11, .17, .23]; SOUTHL = [0, .045, .055, .065, .08]
foot = lambda d: 0 if d <= 0 else min(.95, .35 + .15 * d)

def tex(path, tint=(1, 1, 1), match=None):
    im = Image.open(path).convert("RGB").resize((TILE_CELLS * PX,) * 2, Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255 * np.array(tint, np.float32)
    if match is not None:   # concept art brought to the vanilla textures' brightness, so (b) is not flattered
        a = a * (match / a.reshape(-1, 3).mean())
    reps = (math.ceil(H / TILE_CELLS) + 1, math.ceil(W / TILE_CELLS) + 1, 1)
    return np.tile(a, reps)[:H * PX, :W * PX]

# --- the pond: ~20x14 bed, deep middle -------------------------------------------------
rng = random.Random(7)
depth = np.zeros((H, W), int)          # row 0 = NORTH (top of image)
cx, cy = W / 2 - .5, H / 2 - .5
for y in range(H):
    for x in range(W):
        wob = 1 + .08 * math.sin(3 * math.atan2(y - cy, x - cx) + 1) + .05 * math.sin(5 * math.atan2(y - cy, x - cx))
        r = math.hypot((x - cx) / 10.2, (y - cy) / 7.2) / wob
        rd = math.hypot((x - cx - .8) / 6.2, (y - cy + .3) / 3.6) / wob
        depth[y, x] = 4 if rd < 1 else (2 if r < 1 else 0)

def fade_mask(sel):
    """FadeRough-ish edge: cell mask, blurred, then noise-thresholded."""
    m = Image.fromarray((sel * 255).astype(np.uint8)).resize((W * PX, H * PX), Image.NEAREST)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(PX * .22))).astype(np.float32) / 255
    n = np.random.default_rng(3).random((H * PX // 4 + 1, W * PX // 4 + 1)).astype(np.float32)
    n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((W * PX + 4, H * PX + 4), Image.BICUBIC))[:H * PX, :W * PX] / 255
    return np.clip((m - .5) * 3 + .5 + (n - .5) * .6 * (1 - abs(m - .5) * 2), 0, 1)[..., None]

def render(floor2, floor4, face_inner):
    sand = tex(f"{CACHE}/Sand.png")
    img = sand.copy()
    img = img * (1 - fade_mask(depth >= 2)) + floor2 * fade_mask(depth >= 2)
    img = img * (1 - fade_mask(depth >= 4)) + floor4 * fade_mask(depth >= 4)
    out = img.copy()
    sandface, innerface = sand, face_inner
    def at(y, x): return depth[y, x] if 0 <= y < H and 0 <= x < W else 0
    for y in range(H):
        for x in range(W):
            d = depth[y, x]
            if d == 0: continue
            x0, y0 = x * PX, y * PX
            # north face: hangs from this cell's north edge when the north neighbour is shallower
            dn = at(y - 1, x)
            if d > dn:
                drop = d - dn; h = int(round(NORTH[drop] * PX)); src = sandface if dn == 0 else innerface
                for j in range(h):
                    t = j / max(1, h - 1)
                    light = 1.18 - t * (0.18 + foot(d) * .75)       # lit top, occluded foot
                    strata = .9 if (j % 5 == 2) else 1.0
                    out[y0 + j, x0:x0 + PX] = src[y0 + j, x0:x0 + PX] * light * strata
                out[y0:y0 + max(1, int(.04 * PX)), x0:x0 + PX] *= .15          # rim line
                cs = min(PX - h, 4)
                for j in range(cs):                                            # contact shadow at the foot
                    out[y0 + h + j, x0:x0 + PX] *= .55 + .45 * j / max(1, cs)
            # west / east side strips
            for nx, lit in ((x - 1, False), (x + 1, True)):
                dw = at(y, nx)
                if d > dw:
                    drop = d - dw; w = max(1, int(round(SIDE[drop] * PX))); src = sandface if dw == 0 else innerface
                    xs = slice(x0, x0 + w) if not lit else slice(x0 + PX - w, x0 + PX)
                    out[y0:y0 + PX, xs] = src[y0:y0 + PX, xs] * (1.12 if lit else .55)
                    edge = slice(x0, x0 + 1) if not lit else slice(x0 + PX - 1, x0 + PX)
                    out[y0:y0 + PX, edge] *= .2
            # south lining
            ds = at(y + 1, x)
            if d > ds:
                l = max(1, int(round(SOUTHL[d - ds] * PX)))
                out[y0 + PX - l:y0 + PX, x0:x0 + PX] *= .12
    return np.clip(out, 0, 1)

def pawn_layer(canvas, cxp, cyp):
    body = Image.open(f"{CACHE}/Naked_Male_south.png").convert("RGBA")
    head = Image.open(f"{CACHE}/Male_Average_Normal_south.png").convert("RGBA")
    s = int(1.5 * PX)
    skin = np.array([.93, .76, .60, 1], np.float32)
    def tinted(im):
        a = np.asarray(im.resize((s, s), Image.LANCZOS)).astype(np.float32) / 255 * skin
        return Image.fromarray((a * 255).astype(np.uint8))
    b, h = tinted(body), tinted(head)
    canvas.alpha_composite(b, (int(cxp - s / 2), int(cyp - s / 2)))
    canvas.alpha_composite(h, (int(cxp - s / 2), int(cyp - s / 2 - .34 * PX)))

def panel(floor2, floor4, face_inner):
    arr = render(floor2, floor4, face_inner)
    im = Image.fromarray((arr * 255).astype(np.uint8)).convert("RGBA")
    # colonist in the deep middle: drawn 0.3 cell lower per level (4 levels = 1.2 cells), the live sink rule
    dy, dx = np.argwhere(depth == 4).mean(0)
    pawn_layer(im, (dx + .5) * PX, (dy - 1.0 + .5 + 1.2) * PX)
    # same colonist on level sand for comparison
    pawn_layer(im, 27.5 * PX, 19.0 * PX)
    return im

mud = tex(f"{CACHE}/Mud.png")
gravel = f"{CACHE}/Gravel.png"
A = panel(tex(gravel, (.78, .75, .70)), tex(gravel, (.38, .36, .33)), mud)
import sys
FINAL = sys.argv[1] if len(sys.argv) > 1 else None   # dir holding RM_Lakebed_Shallow/Deep.png: the real tiles, shown as-is
if FINAL:
    B = panel(tex(f"{FINAL}/RM_Lakebed_Shallow.png"), tex(f"{FINAL}/RM_Lakebed_Deep.png"), mud)
else:
    B = panel(tex(f"{HERE}/concept_lakebed_shallow.png", match=0.47), tex(f"{HERE}/concept_lakebed_deep.png", match=0.25), mud)
C = panel(mud, mud, mud)

F = lambda s, b=False: ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if b else ''}.ttf", s)
pw, ph = W * PX, H * PX
gap, top, bot = 24, 150, 70
sheet = Image.new("RGB", (3 * pw + 4 * gap, ph + top + bot), (34, 30, 27))
d = ImageDraw.Draw(sheet)
d.text((gap, 14), "Drained pond bed: the picked look (b) with its real tiles" if FINAL else "What a drained pond bed could look like - same pond, three looks", font=F(34, True), fill=(240, 228, 205))
d.text((gap, 58), "Rim of the pond is 2 levels deep, the middle is 4 levels deep. Desert sand all round. The colonist stands in the deep middle; a second one stands on level sand (bottom right) for comparison.",
       font=F(18), fill=(200, 188, 168))
caps = [("(a) Looks like a dug pit", "Reuses the dug-ditch ground at the same depth (gravel, darker the deeper it goes).", "No new art. A drained pond looks man-made.", False),
        ("(b) Looks like a dried lakebed", "New cracked-mud ground, one look per depth.",
         "REAL TILES: RM_Lakebed_Shallow (rim) and RM_Lakebed_Deep (middle), shown at game brightness." if FINAL
         else "CONCEPT ART, NOT INSTALLED - would need an art pass.", not FINAL),
        ("(c) Mud stays on top", "The bed keeps the pond's mud everywhere.", "Cheapest. Depth shows only in the walls and the colonist sinking.", False)]
for i, (im, (t, l1, l2, warn)) in enumerate(zip((A, B, C), caps)):
    x = gap + i * (pw + gap)
    sheet.paste(im.convert("RGB"), (x, top))
    d.text((x, top - 58), t, font=F(26, True), fill=(250, 236, 200))
    d.text((x, top - 26), l1, font=F(16), fill=(214, 200, 178))
    d.text((x, top + ph + 10), l2, font=F(17, True) if warn else F(17), fill=(255, 150, 90) if warn else (214, 200, 178))
d.text((gap, top + ph + 40), f"Offline mockup, {PX} px per cell. Real game textures: Sand, Gravel, Mud, colonist body/head (Core). Wall faces and sink follow the live FlowWorks numbers; approximate, not a game screenshot.",
       font=F(14), fill=(160, 150, 135))
outp = os.path.join(HERE, "pond_hollow_lakebed_final.png" if FINAL else "pond_hollow_three_looks.png")
sheet.save(outp)
print("wrote", outp, sheet.size)
