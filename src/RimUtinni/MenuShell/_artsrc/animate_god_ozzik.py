#!/usr/bin/env python3
"""Ozzik the Shamed — animated menu-background loop (PROVENANCE).

Base scene: `raw/god_ozzik_scene_raw.png` (Codex, wide cinematic scene,
grandeur amid ruin: torn purple/gold robe, broken crown, collapsed
grey-gunmetal ancient-ship-hull chamber). Crown-glint centroid measured on
the raw 1672x941 PNG via numpy threshold (bright pixels, r>140 and
r+g+b>350, restricted to the crown region x 680-850, y 280-380): (760,360)
— NOT guessed.

Effect: gentle settling Dust (low drift, ash in his ruined domain) plus a
very subtle, SLOW GlowPulse on the crown (low `pulses_per_loop=0.7`) so it
reads as a dying light rather than a vital one, per spec. Output: 1600x896,
10s loop, 20fps, VP8.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene_anim import Dust, GlowPulse, render_loop

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
RAW_PNG = os.path.join(HERE, "raw", "god_ozzik_scene_raw.png")
OUT_WEBM = os.path.join(
    MOD, "RimThemes", "Utinni Shell", "Textures",
    "UI_BackgroundMain.BGPlanet_ozzik.webm",
)

W, H = 1600, 896
RAW_W, RAW_H = 1672, 941
SCALE = W / RAW_W

CROWN = [(760 * SCALE, 360 * SCALE)]


def main():
    effects = [
        # gentle settling ash/dust across the ruined chamber -- low drift,
        # low alpha, reads as still, heavy air rather than a windstorm
        Dust(
            n=60, region=(0.0, 1.0, 0.05, 0.95), color=(190, 185, 175),
            w=W, h=H, seed=7, size_range=(1.5, 3.5), drift_px=18,
        ),
        # dying-light crown glow: slow, subtle pulse, faded purple/gold
        GlowPulse(
            CROWN, color=(190, 150, 210), radius=int(22 * SCALE),
            pulses_per_loop=0.7, base=0.5, amp=0.3,
        ),
    ]
    render_loop(RAW_PNG, OUT_WEBM, effects, duration_s=10.0, fps=20, size=(W, H))


if __name__ == "__main__":
    main()
