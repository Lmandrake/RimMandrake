#!/usr/bin/env python3
"""
RimUtinni Shell — animated menu-background loop (PROVENANCE).

Turns the static `utinni_menu_1.png` (grey-gunmetal Ishko gate, D_helm-era
art) into a short seamless-loop .webm: drifting dust motes, a slow drifting
fog band along the dune line, and Ishko's eyes pulsing gently. Admissible
per VBE.BackgroundImageDef's own C# (measured, not guessed — see
`BackgroundImageDef.cs`'s `animated`/`Video`/`FindPath()`): set
`<animated>true</animated>` in the def and ship the video under a
`Videos/<same relative path as the def's path>.webm` folder, sibling to
`Textures/`. The static PNG stays in `Textures/...` too — VBE's `iconPath`
(the theme-picker thumbnail) always resolves a real Texture2D, animated or not.

Eye coordinates below are MEASURED against the shipped PNG (a numpy
amber-pixel threshold in a doorway-bounded box), not guessed.

Run:  python3 animate_menu.py
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
SRC_PNG = os.path.join(MOD, "Textures", "UI", "Backgrounds", "utinni_menu_1.png")
OUT_WEBM = os.path.join(MOD, "Videos", "UI", "Backgrounds", "utinni_menu_1.webm")

W, H = 1600, 896             # working/shipped resolution; both divisible by 16 so no
                              # codec macro-block padding is inserted (896 vs a true
                              # 900 16:9 height is a <0.5% stretch, imperceptible)
FPS = 20
DURATION_S = 5.0
N_FRAMES = int(FPS * DURATION_S)

# measured eye centroids on the 2560x1440 source, scaled to W,H
SCALE = W / 2560.0
EYES = [(1247 * SCALE, 1222 * SCALE), (1320 * SCALE, 1221 * SCALE)]
EYE_R = 5 * SCALE

random.seed(11)
np.random.seed(11)


def make_dust_sprite(radius, color=(224, 214, 190), peak_alpha=110):
    """A soft round mote — oversampled then downscaled so it stays circular
    (a raw few-pixel PIL ellipse draws as a hard plus/star, not a soft dot)."""
    ss = 4  # supersample factor
    d = (radius * 2 + 4) * ss
    im = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    cx = cy = d / 2
    r_ss = radius * ss
    dr.ellipse([cx - r_ss, cy - r_ss, cx + r_ss, cy + r_ss], fill=color + (peak_alpha,))
    im = im.filter(ImageFilter.GaussianBlur(radius=r_ss * 0.6))
    final = max(4, (radius * 2 + 4))
    return im.resize((final, final), Image.LANCZOS)


def make_glow_sprite(radius, color=(255, 150, 40)):
    d = radius * 2
    im = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    for r in range(radius, 0, -1):
        a = int(200 * (1 - r / radius) ** 1.6)
        dr.ellipse([radius - r, radius - r, radius + r, radius + r], fill=color + (a,))
    return im


def make_fog_band(width, height):
    """A horizontally-tileable soft noise band (wraps via np.roll), pre-faded
    to zero at both the top and bottom edges so blending it in leaves no
    hard seam against the still image above/below it."""
    noise = np.random.rand(height, width).astype(np.float32)
    im = Image.fromarray((noise * 255).astype(np.uint8), "L")
    im = im.filter(ImageFilter.GaussianBlur(radius=max(width, height) * 0.03))
    arr = np.asarray(im).astype(np.float32)
    arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-6)
    # smoothstep fade: 0 at the very top edge, full by ~35% down, fading
    # out again over the last ~25% so the band's bottom edge is invisible too
    y = np.linspace(0, 1, height)
    fade_in = np.clip(y / 0.35, 0, 1)
    fade_in = fade_in * fade_in * (3 - 2 * fade_in)
    fade_out = np.clip((1 - y) / 0.25, 0, 1)
    fade_out = fade_out * fade_out * (3 - 2 * fade_out)
    vfade = np.minimum(fade_in, fade_out)
    arr = arr * vfade[:, None]
    return arr  # 0..1 grey noise, height x width, edge-faded


def main():
    base = Image.open(SRC_PNG).convert("RGB").resize((W, H), Image.LANCZOS)

    n_dust = 55
    dust = []
    for _ in range(n_dust):
        x0 = random.uniform(0, W)
        y0 = random.uniform(H * 0.58, H * 0.97)   # foreground dune air only, not the starfield
        depth = random.uniform(0.4, 1.0)          # closer (bigger depth) drifts faster + bigger
        r = max(2, int(round(random.uniform(2.0, 4.5) * depth * (W / 1600))))
        sprite = make_dust_sprite(r, peak_alpha=int(70 + 50 * depth))
        drift_px = 50 * depth                     # total horizontal travel over one loop
        dust.append((x0, y0, sprite, drift_px))

    fog_h = int(H * 0.32)
    fog_y0 = int(H * 0.62)
    fog_noise = make_fog_band(W, fog_h)           # 0..1
    fog_col = np.array([150, 158, 165], dtype=np.float32)  # cool grey-blue haze

    glow = make_glow_sprite(int(26 * SCALE * (1600 / W) * (W / 1600)) or 26)

    os.makedirs(os.path.dirname(OUT_WEBM), exist_ok=True)
    import imageio_ffmpeg
    # VP8, not VP9: measured live, 2026-09-05 - Unity's VideoPlayer on this
    # RimWorld build refuses VP9 ("Unsupported video codec 'VP9'"), logged
    # as a hard error, not a silent fallback. VP8 is the format RimWorld's
    # own engine actually decodes.
    writer = imageio_ffmpeg.write_frames(
        OUT_WEBM, (W, H), fps=FPS, codec="libvpx",
        output_params=["-b:v", "2200k", "-crf", "10", "-deadline", "good"],
    )
    writer.send(None)

    for i in range(N_FRAMES):
        t = i / N_FRAMES  # 0..1 over the loop

        frame = base.copy().convert("RGBA")

        # --- gentle drifting fog along the dune line ---
        shift = int(t * W) % W
        rolled = np.roll(fog_noise, shift, axis=1)
        breathe = 0.5 + 0.5 * math.sin(2 * math.pi * t * 1.0)  # one slow breath per loop
        alpha = (rolled * (0.10 + 0.05 * breathe) * 255).astype(np.uint8)
        fog_rgba = np.zeros((fog_h, W, 4), dtype=np.uint8)
        fog_rgba[..., 0:3] = fog_col
        fog_rgba[..., 3] = alpha
        fog_im = Image.fromarray(fog_rgba, "RGBA")
        frame.alpha_composite(fog_im, (0, fog_y0))

        # --- drifting dust motes ---
        for x0, y0, sprite, drift_px in dust:
            x = (x0 + t * drift_px) % W
            sw, sh = sprite.size
            frame.alpha_composite(sprite, (int(x - sw / 2), int(y0 - sh / 2)))

        # --- pulsing eyes ---
        pulse = 0.55 + 0.45 * math.sin(2 * math.pi * t * 2)  # two pulses per loop
        gw, gh = glow.size
        for ex, ey in EYES:
            tinted = glow.copy()
            a = tinted.split()[3].point(lambda v: int(v * pulse))
            tinted.putalpha(a)
            frame.alpha_composite(tinted, (int(ex - gw / 2), int(ey - gh / 2)))

        out = frame.convert("RGB")
        writer.send(np.asarray(out))
        if i % 20 == 0:
            print(f"frame {i}/{N_FRAMES}")

    writer.close()
    print("wrote", OUT_WEBM)


if __name__ == "__main__":
    main()
