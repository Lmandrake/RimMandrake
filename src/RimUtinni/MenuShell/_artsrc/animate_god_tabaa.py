#!/usr/bin/env python3
"""Ta'Baa the Unrooted — animated menu-background loop (PROVENANCE).

Base scene: `raw/god_tabaa_scene_raw.png` (Codex, wide cinematic scene,
ancient-ship-helm grey-gunmetal material, windswept dune-crest departure).
Eye centroids measured on the raw 1672x941 PNG via numpy amber-threshold
scan restricted to the hood region (x 800-1000, y 250-400): (896,309) and
(922,315) — NOT guessed.

Effect: strong one-directional windblown Dust (drift_px ~140, biased
leftward to match the wind direction visible in the robe/cloth streaks)
plus a gentle eye GlowPulse for life. Output per UI_SHELL task spec:
1600x896, 8s loop, 20fps, VP8.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene_anim import Dust, GlowPulse, render_loop

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
RAW_PNG = os.path.join(HERE, "raw", "god_tabaa_scene_raw.png")
OUT_WEBM = os.path.join(
    MOD, "RimThemes", "Utinni Shell", "Textures",
    "UI_BackgroundMain.BGPlanet_tabaa.webm",
)

W, H = 1600, 896
RAW_W, RAW_H = 1672, 941
SCALE = W / RAW_W

# measured eye centroids on the raw PNG, scaled to output size
EYES = [(896 * SCALE, 309 * SCALE), (922 * SCALE, 315 * SCALE)]


def main():
    effects = [
        # strong windswept dust, biased leftward (matches the robe/cloth
        # streaming leftward in the source render), covering the dune floor
        Dust(
            n=80, region=(0.0, 1.0, 0.45, 1.0), color=(196, 176, 140),
            w=W, h=H, seed=21, size_range=(2.0, 5.0), drift_px=-140,
        ),
        GlowPulse(EYES, color=(255, 170, 60), radius=int(14 * SCALE) or 10,
                   pulses_per_loop=1.5, base=0.6, amp=0.35),
    ]
    render_loop(RAW_PNG, OUT_WEBM, effects, duration_s=9.0, fps=20, size=(W, H))


if __name__ == "__main__":
    main()
