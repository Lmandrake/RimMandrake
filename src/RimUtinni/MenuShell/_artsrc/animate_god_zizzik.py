#!/usr/bin/env python3
"""Zizzik the Spark-Maker — animated menu-background loop (PROVENANCE).

Base scene: `raw/god_zizzik_scene_raw.png` (Codex, wide cinematic scene,
ancient-ship-helm grey-gunmetal chamber lit by chaotic spark-green arcs).
Eye centroids measured on the raw 1672x941 PNG via numpy threshold
(amber: r>180, b<100, r>g, 90<g<200, distinct from the green sparks where
g>>r): (793,370) and (822,371) — NOT guessed.

Effect: several `Arcs` instances at different points/seeds/phases so the
flicker reads as busy chaos rather than one lone bolt, per the spec's
"multiple Arcs objects at different phases for a busier flicker" note.
Output: 1600x896, 9s loop, 20fps, VP8.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene_anim import Arcs, GlowPulse, render_loop

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
RAW_PNG = os.path.join(HERE, "raw", "god_zizzik_scene_raw.png")
OUT_WEBM = os.path.join(
    MOD, "RimThemes", "Utinni Shell", "Textures",
    "UI_BackgroundMain.BGPlanet_zizzik.webm",
)

W, H = 1600, 896
RAW_W, RAW_H = 1672, 941
SCALE = W / RAW_W

EYES = [(793 * SCALE, 370 * SCALE), (822 * SCALE, 371 * SCALE)]

# points around the scene where sparks/arcs erupt (hands + the already-lit
# sparking machinery in the raw render), read from the generated image
ARC_POINTS = [
    (650 * SCALE, 430 * SCALE),   # raised left hand
    (990 * SCALE, 430 * SCALE),   # raised right hand
    (370 * SCALE, 160 * SCALE),   # top-left sparking conduit
    (1460 * SCALE, 150 * SCALE),  # top-right sparking conduit
    (140 * SCALE, 520 * SCALE),   # left droid glowing eye
    (1310 * SCALE, 480 * SCALE),  # right droid sparking hand
]

SPARK_GREEN = (150, 230, 90)


def main():
    effects = [
        GlowPulse(EYES, color=(255, 175, 50), radius=int(12 * SCALE),
                   pulses_per_loop=3, base=0.55, amp=0.4),
        # multiple independent Arcs instances at different seeds/phases so
        # bolts fire out of sync across the frame -> busy chaotic flicker,
        # not one lone synchronized bolt
        Arcs(ARC_POINTS[0:2], SPARK_GREEN, seed=3, length=int(55 * SCALE), burst_hz=4.0),
        Arcs(ARC_POINTS[2:4], SPARK_GREEN, seed=17, length=int(70 * SCALE), burst_hz=5.5),
        Arcs(ARC_POINTS[4:6], SPARK_GREEN, seed=42, length=int(60 * SCALE), burst_hz=3.2),
        Arcs(ARC_POINTS, SPARK_GREEN, seed=99, length=int(35 * SCALE), burst_hz=7.0),
    ]
    render_loop(RAW_PNG, OUT_WEBM, effects, duration_s=9.0, fps=20, size=(W, H))


if __name__ == "__main__":
    main()
