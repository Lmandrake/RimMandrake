#!/usr/bin/env python3
"""Sh'kaar the All-Searing — animated menu-background loop (PROVENANCE).

Base scene: `raw/god_shkaar_scene_raw.png` (Codex, wide cinematic scene,
searing white-gold light blown out from the hood, hard radiating shadows
across a grey-gunmetal ancient-ship-hull chamber). Glow-point centroid
measured on the raw 1672x941 PNG via numpy near-white threshold
(r,g,b>253) restricted to the hood region (x 750-950, y 250-450): (845,362)
— NOT guessed.

Effect: one LARGE, bright `GlowPulse` centered on the hood with a fast
pulse rate (`pulses_per_loop=4.5`) so the throb reads as dangerous/violent
rather than a gentle breathing glow, per spec. Output: 1600x896, 8s loop,
20fps, VP8.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene_anim import GlowPulse, render_loop

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
RAW_PNG = os.path.join(HERE, "raw", "god_shkaar_scene_raw.png")
OUT_WEBM = os.path.join(
    MOD, "RimThemes", "Utinni Shell", "Textures",
    "UI_BackgroundMain.BGPlanet_shkaar.webm",
)

W, H = 1600, 896
RAW_W, RAW_H = 1672, 941
SCALE = W / RAW_W

GLOW_POINT = [(845 * SCALE, 362 * SCALE)]


def main():
    effects = [
        GlowPulse(
            GLOW_POINT, color=(255, 250, 220), radius=int(260 * SCALE),
            pulses_per_loop=4.5, base=0.55, amp=0.45,
        ),
    ]
    render_loop(RAW_PNG, OUT_WEBM, effects, duration_s=8.0, fps=20, size=(W, H))


if __name__ == "__main__":
    main()
