#!/usr/bin/env python3
"""MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY: fit gen.py's raw renders onto the live canvases (drafts, NOT installed).
  pump<X>.png -> cand/Pump_Modern_<X>.png : 512x512, trimmed and fitted inside the live Modern pump's fill box, centred
                 on it (ports end where today's ports end; UnderCouplerReach.cs must be regenerated on install).
  spr<X>.png  -> cand/Sprinkler_Modern_<X>.png : 256x256, same height and same bottom (foot) row as the live Modern
                 head, centred on x 128 (the def's drawOffset is measured from the foot; re-measure on install).
Also writes phone/<subject>_options.png (live beside each option, checkerboard) and a play-zoom strip.
    python3 compose.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

H = Path(__file__).resolve().parent
REPO = H.parents[2]
RAW = Path("/mnt/d/ClaudeWork/rimmandrake/modern_pump/raw")
FW = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks"
LIVE = {"Pump": FW / "Pump/Modern/RM_LiquidPump.png", "Sprinkler": FW / "Sprinkler/Modern/RM_SprinklerHead.png"}


def alpha_clean(im):
    a = np.array(im.convert("RGBA"))
    al = a[..., 3].astype(int)
    al[al < 24] = 0
    al[al >= 232] = 255
    a[..., 3] = al
    a[al == 0, :3] = 0
    return Image.fromarray(a)


def trim(im):
    bb = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    return im.crop(bb)


def resize(im, w, h):
    a = im.convert("RGBa").resize((max(1, round(w)), max(1, round(h))), Image.LANCZOS)
    return a.convert("RGBA")


def live_box(p):
    return Image.open(p).convert("RGBA").getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()


def pump(key):
    lb = live_box(LIVE["Pump"])
    t = trim(alpha_clean(Image.open(RAW / f"{key}.png")))
    k = min((lb[2] - lb[0]) / t.width, (lb[3] - lb[1]) / t.height)
    s = resize(t, t.width * k, t.height * k)
    c = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    c.alpha_composite(s, (round((lb[0] + lb[2]) / 2 - s.width / 2), round((lb[1] + lb[3]) / 2 - s.height / 2)))
    return alpha_clean(c)


def sprinkler(key):
    lb = live_box(LIVE["Sprinkler"])
    t = trim(alpha_clean(Image.open(RAW / f"{key}.png")))
    hh = lb[3] - lb[1]
    k = hh / t.height
    if t.width * k > 200:
        k = 200 / t.width
    s = resize(t, t.width * k, t.height * k)
    c = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    c.alpha_composite(s, (round(128 - s.width / 2), lb[3] - s.height))
    return alpha_clean(c)


def checker(w, h, n=16):
    im = Image.new("RGBA", (w, h), (200, 200, 200, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, n):
        for x in range(0, w, n):
            if (x // n + y // n) % 2:
                d.rectangle([x, y, x + n - 1, y + n - 1], fill=(160, 160, 160, 255))
    return im


def options(subject, ims, labels, tile=360):
    W = Image.new("RGBA", (tile * len(ims), tile + 40 + 80), (40, 30, 22, 255))
    d = ImageDraw.Draw(W)
    for i, (im, lab) in enumerate(zip(ims, labels)):
        bg = checker(tile - 10, tile - 10)
        bg.alpha_composite(im.resize((tile - 10, tile - 10), Image.LANCZOS))
        W.alpha_composite(bg, (i * tile + 5, 30))
        d.text((i * tile + 10, 8), lab, fill=(255, 240, 220, 255))
        # play zoom: 32 and 48 px per cell over sand
        for j, ppc in enumerate((32, 48)):
            g = Image.new("RGBA", (ppc, ppc), (120, 104, 80, 255))
            g.alpha_composite(im.convert("RGBa").resize((ppc, ppc), Image.BOX).convert("RGBA"))
            W.alpha_composite(g, (i * tile + 10 + j * 60, tile + 30 + 10))
    return W


if __name__ == "__main__":
    (H / "cand").mkdir(exist_ok=True)
    (H / "phone").mkdir(exist_ok=True)
    for subject, fn, keys in (("Pump", pump, "ABC"), ("Sprinkler", sprinkler, "ABC")):
        ims, labs = [Image.open(LIVE[subject]).convert("RGBA")], ["today (red repaint)"]
        for x in keys:
            raw = RAW / f"{'pump' if subject == 'Pump' else 'spr'}{x}.png"
            if (RAW / f"{raw.stem}2.png").is_file():  # judge_v1 redraw
                raw = RAW / f"{raw.stem}2.png"
            if not raw.is_file():
                print("missing", raw)
                continue
            im = fn(raw.stem)
            im.save(H / "cand" / f"{subject}_Modern_{x}.png")
            ims.append(im)
            labs.append(f"option {x}")
        options(subject, ims, labs).convert("RGB").save(H / "phone" / f"{subject}_Modern_options.png")
        print(subject, len(ims) - 1, "candidates")
