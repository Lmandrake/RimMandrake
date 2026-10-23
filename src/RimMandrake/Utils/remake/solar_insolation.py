#!/usr/bin/env python3
"""Solar insolation by geometry: a line-for-line port of SolarMirrors/Source/Kernel/RM_InsolationKernel.cs.

VEE_SOLAR_REWIRE_GEOMETRY_PAINTS_IT (design/RimMandrake/vee_port_plan_2026-10-22.md §4). The world-map labels
RM_StrongInsolation / RM_Sunless are DERIVED from the tile's sun elevation alone (no biome exclusions); the one stamp
(VEE_WORLD_RENAME_ONE_STAMP_AT_END) takes its tile lists from `tiles_by_label()` here, never from the old VEE paint.

    python3 src/RimMandrake/Utils/remake/solar_insolation.py      # print the label counts over world_tiles_sub7b.csv
"""
import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
KERNEL_CS = os.path.join(REPO, "src", "RimMandrake", "SolarMirrors", "Source", "Kernel", "RM_InsolationKernel.cs")
TILES = os.path.join(REPO, "world", "world_tiles_sub7b.csv")

RAMP_START = 20.0          # RM_InsolationKernel.RampStartDegrees
RAMP_FULL = 35.0           # RM_InsolationKernel.RampFullDegrees
STRONG_MIN = 35.0          # RM_InsolationKernel.StrongInsolationMinDegrees
SUNLESS_MAX = -35.0        # RM_InsolationKernel.SunlessMaxDegrees
DEFAULT_BONUS = 0.25       # RM_InsolationKernel.DefaultHighSunBonus

LABELS = {1: "RM_StrongInsolation", -1: "RM_Sunless"}


def arc_deg(lat, lon):
    c = math.cos(math.radians(lat)) * math.cos(math.radians(lon))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def elevation_deg(lat, lon):
    return 90.0 - arc_deg(lat, lon)


def insolation_factor(e, bonus=DEFAULT_BONUS):
    if bonus <= 0:
        return 1.0
    e = max(0.0, min(90.0, e))
    t = (e - RAMP_START) / (RAMP_FULL - RAMP_START)
    if t <= 0:
        return 1.0
    if t >= 1:
        return 1.0 + bonus
    return 1.0 + bonus * t * t * (3 - 2 * t)


def label_for(e):
    if e >= STRONG_MIN:
        return 1
    if e <= SUNLESS_MAX:
        return -1
    return 0


def load_tiles(path=TILES):
    with open(path, encoding="utf-8") as f:
        return {int(r["tile"]): (float(r["lat"]), float(r["long"])) for r in csv.DictReader(f)}


def tiles_by_label(tiles=None):
    """{defName: sorted tile ids} for the two derived labels."""
    tiles = load_tiles() if tiles is None else tiles
    out = {name: [] for name in LABELS.values()}
    for t, (lat, lon) in tiles.items():
        lab = label_for(elevation_deg(lat, lon))
        if lab:
            out[LABELS[lab]].append(t)
    return {k: sorted(v) for k, v in out.items()}


if __name__ == "__main__":
    for name, ts in tiles_by_label().items():
        print(f"{name} {len(ts)}")
