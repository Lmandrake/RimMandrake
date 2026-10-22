#!/usr/bin/env python3
"""Phone collections for 2026-10-22 joint fittings + pipe atlas/pump drafts (one-off; Transient)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/home/mandrake/rm/bench")
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils/art"))
import scale_panel as SP  # noqa: E402

P = ROOT / "Transient/pile_2026-10-22"
OUT = P / "phone"
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
BG = (24, 21, 18, 255)
SOIL = (122, 104, 84, 255)
FG = (235, 225, 205)
ACC = (255, 200, 90)


def font(sz):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", sz)


def checker(w, h, c1=(70, 64, 58), c2=(90, 83, 75), s=8):
    im = Image.new("RGBA", (w, h), c1 + (255,))
    d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range(0, w, s):
            if (x // s + y // s) % 2:
                d.rectangle([x, y, x + s - 1, y + s - 1], fill=c2 + (255,))
    return im


def on_bg(img, bg_img):
    b = bg_img.copy()
    b.alpha_composite(img, ((b.width - img.width) // 2, (b.height - img.height) // 2))
    return b


def letter_box(d, x, y, letter, sz=40):
    d.rectangle([x, y, x + sz + 14, y + sz + 8], fill=ACC + (255,))
    d.text((x + 7, y + 2), letter, font=font(sz), fill=(20, 15, 10))


def human(ppc):
    img, m, hoff = SP.human_sprite(ppc)
    return img


def resize_ppc(img, src_ppc, dst_ppc):
    f = dst_ppc / src_ppc
    return SP._premul_resize(img, max(1, round(img.width * f)), max(1, round(img.height * f)))


def scene(items, ppc, label, h_cells=2.6, pad_cells=0.4):
    """items: [(img_at_ppc, caption)] laid left->right after a human, all bottoms on one baseline, grid lines."""
    hum = human(ppc)
    parts = [(hum, "human")] + items
    W = int(sum(p.width for p, _ in parts) + pad_cells * ppc * (len(parts) + 1))
    H = int(h_cells * ppc) + 30
    sc = Image.new("RGBA", (W, H), SOIL)
    d = ImageDraw.Draw(sc)
    for x in range(0, W, ppc):
        d.line([x, 0, x, H - 30], fill=(110, 93, 75, 255))
    for y in range(H - 30, -1, -ppc):
        d.line([0, y, W, y], fill=(110, 93, 75, 255))
    x = int(pad_cells * ppc)
    base = H - 30 - int(0.15 * ppc)
    f = font(14)
    for im, cap in parts:
        y = base - im.height if cap == "human" else (base - int(0.75 * ppc) - im.height // 2)
        sc.alpha_composite(im, (x, max(0, y)))
        d.text((x, H - 26), cap, font=f, fill=FG)
        x += im.width + int(pad_cells * ppc)
    lab = Image.new("RGBA", (W, 26), BG)
    ImageDraw.Draw(lab).text((4, 4), label, font=font(16), fill=ACC)
    out = Image.new("RGBA", (W, H + 26), BG)
    out.alpha_composite(lab, (0, 0))
    out.alpha_composite(sc, (0, 26))
    return out


def stack(parts, gap=14, bg=BG):
    W = max(p.width for p in parts)
    H = sum(p.height for p in parts) + gap * (len(parts) - 1)
    out = Image.new("RGBA", (W, H), bg)
    y = 0
    for p in parts:
        out.alpha_composite(p, (0, y))
        y += p.height + gap
    return out


def row(parts, gap=14, bg=BG):
    W = sum(p.width for p in parts) + gap * (len(parts) - 1)
    H = max(p.height for p in parts)
    out = Image.new("RGBA", (W, H), bg)
    x = 0
    for p in parts:
        out.alpha_composite(p, (x, 0))
        x += p.width + gap
    return out


def title(text, sub, W):
    im = Image.new("RGBA", (W, 74), BG)
    d = ImageDraw.Draw(im)
    d.text((10, 6), text, font=font(28), fill=ACC)
    d.text((10, 44), sub, font=font(17), fill=FG)
    return im


def zoom_bbox(img, W, H, pad=4):
    b = img.getchannel("A").getbbox()
    c = img.crop((max(0, b[0]-pad), max(0, b[1]-pad), min(img.width, b[2]+pad), min(img.height, b[3]+pad)))
    k = max(1, min((W - 8) // c.width, (H - 8) // c.height))
    return c.resize((c.width * k, c.height * k), Image.NEAREST), k


def caption_tile(img, letter, cap, W, H):
    t = Image.new("RGBA", (W, H + 34), BG)
    t.alpha_composite(on_bg(img, checker(W, H)), (0, 34))
    d = ImageDraw.Draw(t)
    letter_box(d, 0, 0, letter, 24)
    d.text((48, 6), cap, font=font(17), fill=FG)
    return t


def crop_centre(img, cx, cy, w, h):
    return img.crop((cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2))


def bbox_centre(img):
    b = img.getchannel("A").getbbox()
    return ((b[0] + b[2]) // 2, (b[1] + b[3]) // 2)


# ─────────────────────────────── a) joint fittings ──
def joint_fittings():
    letters = iter("ABCDEFGHIJKLMN")
    key = []
    cols = []
    tw = 330
    for look in LOOKS:
        tiles = []
        for part, comp_ppc in (("Flange", 256), ("Coupler", 256), ("Saddle", 256), ("Saddle_v2", 256)):
            cand = P / f"joinfit/cand/{look}_{part}.png"
            if not cand.exists():
                tiles.append(Image.new("RGBA", (tw, 1), BG))
                continue
            base = part.replace("_v2", "")
            comp = P / f"joinfit/comp/{look}_{base}_{'v2' if part.endswith('v2') else 'v1'}.png"
            L = next(letters)
            key.append((L, look, part, cand, comp))
            ci = Image.open(cand).convert("RGBA")
            z, k = zoom_bbox(ci, tw, 230)
            full = caption_tile(z, L, f"{look} {part.replace('_', ' ')} x{k}", tw, 230)
            co = Image.open(comp).convert("RGBA")
            # on-pipe view cropped near the piece, at the comp's own 256 px/cell
            if base == "Flange":
                cx, cy = co.width - tw // 2, co.height // 2
            else:
                cx, cy = co.width // 2, co.height // 2
            cr = crop_centre(co, cx, cy, tw, min(co.height, 200))
            onp = Image.new("RGBA", (tw, cr.height + 22), BG)
            onp.alpha_composite(on_bg(cr, Image.new("RGBA", cr.size, SOIL)), (0, 22))
            ImageDraw.Draw(onp).text((2, 2), "on its pipe (256 px/cell)", font=font(14), fill=FG)
            tiles.append(stack([full, onp], gap=4))
        cols.append(stack(tiles, gap=18))
    grid = row(cols, gap=16)
    # true scale: per look human + flange/coupler/saddle comps at 64 px/cell (normal play) and 128 (close zoom)
    scales = []
    for look in LOOKS:
        items = []
        for part in ("Flange", "Coupler", "Saddle"):
            co = Image.open(P / f"joinfit/comp/{look}_{part}_v1.png").convert("RGBA")
            items.append((resize_ppc(co, 256, 128), part.lower()))
        scales.append(scene(items, 128, f"{look}: TRUE SCALE at 128 px/cell (close zoom) — human, then each piece on its pipe"))
    sc_block = stack([row(scales[:2], gap=10), row(scales[2:], gap=10)], gap=10)
    W = max(grid.width, sc_block.width)
    img = stack([title("Joint fittings — 14 drafts (A–N)",
                       "Each look has its own Flange (pipe meets tank), Coupler, Saddle (hose meets pipe). Saddles: two tries for Scrapper and Industrial.", W),
                 grid, sc_block])
    out = OUT / "joint_fittings_phone.png"
    img.convert("RGB").save(out, optimize=True)
    with open(OUT / "joint_fittings_phone.md", "w") as f:
        f.write("# joint_fittings_phone.png — letter key\n\nItem `PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID`; sheet "
                "`Transient/biome_ffar/joint_fittings_sheet_2026-10-22.html`. Nothing installed; `joinFittings` stays off "
                "until he picks. Each piece is its look's ONLY candidate except the two Saddles marked v1/v2 (pick one).\n\n"
                "| letter | look | piece | candidate | on-pipe composite |\n|---|---|---|---|---|\n")
        for L, look, part, cand, comp in key:
            f.write(f"| {L} | {look} | {part} | `{cand.relative_to(ROOT)}` | `{comp.relative_to(ROOT)}` |\n")
        f.write("\nBottom of the image: true scale at 128 px/cell (close zoom) beside a vanilla human, per look.\n"
                "Top tiles: the candidate cropped to its pixels and enlarged with hard pixels (xN shown; canvas 128 px, saddle 256 px).\n"
                "Card shape: per look 'accept all / redo <letters>', plus Saddle v1 vs v2 for Scrapper and Industrial "
                "(letters in the table above).\n")
    return out


# ─────────────────────────────── b) pipe atlas + pumps ──
def pipe_atlas():
    outs = []
    letters = dict(zip(LOOKS, "ABCD"))
    key = []
    # image 1: draft layout vs today's, per look, at 88 px/cell (layout is 792 px / 9 cells)
    rows_ = []
    for look in LOOKS:
        L = letters[look]
        dr = Image.open(P / f"pipefit/comp/{look}_layout.png").convert("RGBA")
        lv = Image.open(P / f"pipefit/comp/{look}_live_layout.png").convert("RGBA")
        a = caption_tile(dr, L, f"{look} DRAFT atlas (test layout, 88 px/cell)", dr.width, dr.height)
        b = Image.new("RGBA", (lv.width, lv.height + 34), BG)
        b.alpha_composite(lv, (0, 34))
        ImageDraw.Draw(b).text((6, 6), f"{look} — TODAY's atlas, same layout", font=font(17), fill=(170, 160, 150))
        rows_.append(row([a, b], gap=16))
        key.append((L, look, "pipe atlas draft (tees, crosses, couplings, end caps)",
                    P / f"pipefit/draft/{look}/UniversalPipe_Atlas.png"))
    W = rows_[0].width
    img1 = stack([title("Pipe atlas drafts A–D (left) vs today (right)",
                        "Real tee and cross fittings, ONE coupling per joint (no ladder bands), end caps matched per look.", W)]
                 + rows_)
    o1 = OUT / "pipe_atlas_phone_1_layouts.png"
    img1.convert("RGB").save(o1, optimize=True)
    outs.append(o1)
    # image 2: the fitting pieces at full res (x4 nearest, small) + true scale crop with human at 64 and 128 px/cell
    cols = []
    for look in LOOKS:
        L = letters[look]
        tiles = []
        for part in ("Tee", "Cross", "Coupling", "EndCap"):
            ci = Image.open(P / f"pipefit/cand/{look}_{part}.png").convert("RGBA")
            k = 4 if ci.width < 40 else 2
            big = ci.resize((ci.width * k, ci.height * k), Image.NEAREST)
            tiles.append(caption_tile(big, L, f"{part} {ci.width}x{ci.height} x{k}", 300, 180))
        cols.append(stack(tiles, gap=10))
    grid = row(cols, gap=14)
    scs = []
    for look in LOOKS:
        dr = Image.open(P / f"pipefit/comp/{look}_layout.png").convert("RGBA")
        # crop around the cross (centre of the layout's crossing) — 4x3 cells
        cx, cy = 396, 308
        cr = crop_centre(dr, cx, cy, 4 * 88, 3 * 88)
        scs.append(scene([(resize_ppc(cr, 88, 64), f"{letters[look]} draft"),
                          (resize_ppc(crop_centre(Image.open(P / f'pipefit/comp/{look}_live_layout.png').convert('RGBA'), cx, cy, 4 * 88, 3 * 88), 88, 64), "today")],
                         64, f"{letters[look]} {look}: TRUE SCALE at 64 px/cell (normal play), the crossing", h_cells=3.6))
    W = max(grid.width, max(s.width for s in scs) * 2 + 14)
    img2 = stack([title("Pipe fittings A–D, close up + true scale",
                        "Top: each piece at full resolution (enlarged with hard pixels). Bottom: the crossing beside a human.", W),
                  grid, row(scs[:2]), row(scs[2:])])
    o2 = OUT / "pipe_atlas_phone_2_pieces_scale.png"
    img2.convert("RGB").save(o2, optimize=True)
    outs.append(o2)
    # image 3: pumps — today's (all looks) + E/F/G at full res 512, and true scale beside a human
    live = Image.open(ROOT / "src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Machinery/RM_LiquidPump.png").convert("RGBA")
    pl = {"Industrial": "E", "Modern": "F", "Futuristic": "G"}
    tiles = [caption_tile(live.resize((400, 400), Image.LANCZOS) if live.width > 400 else live, "–",
                          f"TODAY (every look) {live.width}px", 400, 400)]
    for look, L in pl.items():
        ci = Image.open(P / f"pipefit/cand/{look}_Pump.png").convert("RGBA")
        tiles.append(caption_tile(ci.resize((400, 400), Image.LANCZOS), L, f"{look} pump, 512px (shown 400)", 400, 400))
        key.append((L, look, "4-port pump look", P / f"pipefit/cand/{look}_Pump.png"))
    g = stack([row(tiles[:2]), row(tiles[2:])])
    items = [(SP._premul_resize(live, 128, 128), "today")] + [
        (SP._premul_resize(Image.open(P / f"pipefit/cand/{lk}_Pump.png").convert("RGBA"), 128, 128), pl[lk]) for lk in pl]
    sc = scene(items, 128, "TRUE SCALE at 128 px/cell (close zoom): human, then each 1x1 pump")
    items64 = [(SP._premul_resize(it, 64, 64), c) for it, c in items]
    sc64 = scene(items64, 64, "and at 64 px/cell (normal play)")
    W = max(g.width, sc.width)
    img3 = stack([title("Pump looks E–G", "Today one rusty pump shows on every look. A pump look also needs a small def change after the pick.", W),
                  g, sc, sc64])
    o3 = OUT / "pipe_atlas_phone_3_pumps.png"
    img3.convert("RGB").save(o3, optimize=True)
    outs.append(o3)
    with open(OUT / "pipe_atlas_phone.md", "w") as f:
        f.write("# pipe_atlas_phone_{1,2,3}.png — letter key\n\nItem `PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS`; sheet "
                "`Transient/biome_ffar/pipe_fittings_atlas_sheet_2026-10-22.html`. Nothing installed.\n\n"
                "| letter | look | what | file |\n|---|---|---|---|\n")
        for L, look, what, p in key:
            f.write(f"| {L} | {look} | {what} | `{p.relative_to(ROOT)}` |\n")
        f.write("\n- `pipe_atlas_phone_1_layouts.png`: A–D draft test layout (left) vs today's atlas (right).\n"
                "- `pipe_atlas_phone_2_pieces_scale.png`: A–D tee / cross / coupling / end cap at full res, then the "
                "crossing at true scale (64 px/cell) beside a human, draft vs today.\n"
                "- `pipe_atlas_phone_3_pumps.png`: today's pump (Scrapper, shown on every look) and E–G, full res and "
                "true scale.\nCard shape: per letter accept / redo; a pump pick also owes a def/C# change.\n")
    return outs


if __name__ == "__main__":
    which = sys.argv[1:] or ["a", "b"]
    if "a" in which:
        print(joint_fittings())
    if "b" in which:
        for o in pipe_atlas():
            print(o)
