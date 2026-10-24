#!/usr/bin/env python3
"""The redesigned suspension bridges over a real 4 m pit, offline (the owner: "Need to see these bridges over pits to
truly evaluate"). The pit is Tools/fw_scenes_spikes.render's dry pit on the real dug-floor texture and wall faces; the
ground around it is Core's Soil texture; deck runs are laid by build_deck_atlas.bridge_image from the atlas exactly as
the Basic-linked deck links in game (E-W runs turned 90 degrees), the anchors at the two ends as Graphic_Multi draws them
(west end = the east picture, east end = the east picture mirrored; north end = south picture, south end = north).
Not emulated: the anchor's rope prints (RM_DrawbridgeArt) and the railing/tower things; lighting is flat daylight.

Usage: scenes.py ART_ROOT OUT_PNG [--px 83] [--tier Steel|Heavy] [--set new|base|scrapper]
  ART_ROOT  folder holding Things/Building/FlowWorks/SuspensionBridge/... (suspension_redesign.py's output, or the mod's
            Textures folder for the current art)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent
FW = HERE.parents[1]
sys.path.insert(0, str(FW / "Tools"))
sys.path.insert(0, str(FW / "art_source/SuspensionLooks"))
import build_deck_atlas as BDA  # noqa: E402
import fw_scenes_spikes as FS  # noqa: E402

VANILLA = Path("/mnt/d/ClaudeWork/rimmandrake/scratch/vanilla_tex/ludeon.rimworld.core")

# 11 x 9 cells, north row first: a 4-long x 3-wide depth-4 pit for an E-W bridge (rows 1..3), and a 3-wide x 4-long
# depth-4 pit for a N-S bridge (cols 7..9, rows 4..7)
GRID = [
    "00000000000",
    "00444400000",
    "00444400000",
    "00444400000",
    "00000004440",
    "00000004440",
    "00000004440",
    "00000004440",
    "00000000000",
]


def _paths(root: Path, tier: str, which: str):
    if which == "scrapper":
        d = root / "RimMandrake/FlowWorks/SuspensionBridge/Scrapper"
        return (d / f"RM_SuspensionDeck_{tier}_Atlas.png", {f: d / f"RM_SuspensionAnchor_{tier}_{f}.png"
                                                             for f in ("south", "east", "north")})
    d = root / "Things/Building/FlowWorks/SuspensionBridge"
    return (d / f"RM_SuspensionDeck_{tier}_Atlas.png", {f: d / f"RM_SuspensionAnchor_{tier}_{f}.png"
                                                         for f in ("south", "east", "north")})


def scene(root: Path, tier: str, which: str, px: int = 83) -> Image.Image:
    pit = FS.Pit([[int(c) for c in r] for r in GRID])
    res = FS.render(pit, "before", P=px, floor="real")
    img = Image.fromarray(np.asarray(res["img"]).astype(np.uint8)).convert("RGBA")
    soil = Image.open(VANILLA / "Soil.png").convert("RGBA")
    tile = soil.resize((px * 2, px * 2), Image.LANCZOS)
    for r, row in enumerate(GRID):
        for c, ch in enumerate(row):
            if ch == "0":
                img.paste(tile.crop(((c % 2) * px, (r % 2) * px, (c % 2) * px + px, (r % 2) * px + px)), (c * px, r * px))
    atlas_p, anchors = _paths(root, tier, which)
    atlas = Image.open(atlas_p).convert("RGBA")
    an = {f: Image.open(p).convert("RGBA").resize((px, px), Image.LANCZOS) for f, p in anchors.items()}
    # E-W one-lane bridge on row 2 over cols 2..5, anchors at cols 1 and 6
    run = BDA.bridge_image(atlas, 4, 1, True, px)
    img.alpha_composite(run, (2 * px, 2 * px))
    img.alpha_composite(an["east"], (1 * px, 2 * px))
    img.alpha_composite(ImageOps.mirror(an["east"]), (6 * px, 2 * px))
    # N-S one-lane bridge on col 8 over rows 4..7, anchors at rows 3 (north end, deck below) and 8
    run = BDA.bridge_image(atlas, 4, 1, False, px)
    img.alpha_composite(run, (8 * px, 4 * px))
    img.alpha_composite(an["south"], (8 * px, 3 * px))
    img.alpha_composite(an["north"], (8 * px, 8 * px))
    return img.convert("RGB")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--px", type=int, default=83)
    ap.add_argument("--tier", default="Steel")
    ap.add_argument("--set", dest="which", default="new", choices=("new", "base", "scrapper"))
    a = ap.parse_args(argv)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    scene(a.root, a.tier, a.which, a.px).save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
