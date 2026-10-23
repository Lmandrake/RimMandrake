#!/usr/bin/env python3
"""Linked-deck atlases for the suspension bridge (SUSPENSION_DECK_LINKED_NO_SEAMS).

Each deck picture (a vertical-run 256 px tile: planks/panels along the run, a side band down each edge) becomes a 4x4 atlas
in vanilla's Basic link format (Verse.MaterialAtlasPool: sub-material i shows UV offset ((i%4)/4 + 1/32, (i//4)/4 + 1/32),
scale 0.1875 -> the inner 3/4 of each quarter-tile, rows from the BOTTOM; i = N*1 + E*2 + S*4 + W*8, tile frame).
Same format as art_source/pipe/build_pipe_atlas.py.

A side with a linked neighbour continues the deck surface; a side with none shows the band. The surface continuing across a
lane seam is the source centre mirrored about the cell centre, so the two edges of every tile are the same column and
neighbouring lanes meet pixel-identically. The tile runs N-S; Building_SuspensionDeck.Print turns it 90 degrees on an E-W
bridge and remaps the mask (RM_SuspensionDeckLink.TileMask). Vertically the source repeats at its own period.

Usage: build_deck_atlas.py [--install] [--only SUBSTRING]     (--install goes through the art ledger, install_image; previews: preview_decks.py)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
TEXROOT = REPO / "src/RimMandrake/FlowWorks/Textures"
T = 344                 # tile edge in the atlas
P = T // 8              # 43: padding outside the displayed cell
C = T - 2 * P           # 258: displayed cell
ATLAS = 4 * T           # 1376
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
THINGS = "Things/Building/FlowWorks/SuspensionBridge"
# (source texPath, atlas texPath, band width in the source)
JOBS = []
for look in LOOKS:
    for part in ("RM_SuspensionDeck", "RM_SuspensionDeckGrated"):
        JOBS.append((f"RimMandrake/FlowWorks/SuspensionBridge/{look}/{part}",
                     f"RimMandrake/FlowWorks/SuspensionBridge/{look}/{part}_Atlas", 28))
    # per-tier styled decks (BRIDGE_ART_REDRAW_CABINETS_GROW_SADDLES, 2026-10-21): a look's tier with its own picture
    # (<part>_<Tier>.png) gets its own atlas; a tier without one keeps the look's shared atlas above
    for part, tiers in (("RM_SuspensionDeck", ("Timber", "Steel", "Heavy")), ("RM_SuspensionDeckGrated", ("Steel", "Heavy"))):
        for tier in tiers:
            src = f"RimMandrake/FlowWorks/SuspensionBridge/{look}/{part}_{tier}"
            if (TEXROOT / (src + ".png")).is_file():
                JOBS.append((src, src + "_Atlas", 28))
for tier in ("Rope", "Timber", "Steel", "Heavy", "SteelGrated", "HeavyGrated"):
    JOBS.append((f"{THINGS}/RM_SuspensionDeck_{tier}", f"{THINGS}/RM_SuspensionDeck_{tier}_Atlas", 26 if tier == "Rope" else 28))


def premul_resize(a: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    """float RGBA 0..1 -> premultiplied Lanczos resize -> straight alpha again (no dark fringe at transparency)."""
    pm = a.copy()
    pm[..., :3] *= pm[..., 3:4]
    ch = [np.asarray(Image.fromarray(pm[..., i].astype(np.float32), "F").resize(size, Image.LANCZOS)) for i in range(4)]
    o = np.stack(ch, -1)
    al = np.clip(o[..., 3:4], 0, 1)
    o[..., :3] = np.where(al > 1e-4, o[..., :3] / np.maximum(al, 1e-4), 0)
    o[..., 3:4] = al
    return np.clip(o, 0, 1)


def surface(src: np.ndarray, band: int) -> np.ndarray:
    """The deck surface continued across the whole cell width: the centre's left half stretched to half a cell and
    mirrored, so column 0 == column 255 (neighbouring lanes meet exactly)."""
    n = src.shape[1]
    half = src[:, band + 10:n // 2]          # inset: the centre's own edge outline/shading is not surface                                        # centre, left half
    left = np.asarray(Image.fromarray((half * 255 + .5).astype(np.uint8), "RGBA").resize((n // 2, src.shape[0]), Image.LANCZOS),
                      dtype=np.float32) / 255
    return np.concatenate([left, left[:, ::-1]], 1)


def cell(src: np.ndarray, band: int, mask: int) -> np.ndarray:
    n = src.shape[1]
    f = surface(src, band)
    if not mask & 8:                       # no west neighbour: the west band
        f[:, :band] = src[:, :band]
    if not mask & 2:                       # no east neighbour: the east band
        f[:, n - band:] = src[:, n - band:]
    return f


def tile(src: np.ndarray, band: int, mask: int) -> np.ndarray:
    c = premul_resize(cell(src, band, mask), (C, C))
    out = np.zeros((T, T, 4), np.float32)
    out[P:P + C, P:P + C] = c
    rows = slice(P, P + C)
    for side, lo in ((8, True), (2, False)):             # lateral pads
        for k in range(P):
            col = c[:, k] if mask & side else c[:, 0 if lo else C - 1].copy()
            if mask & side:
                col = c[:, k] if lo else c[:, C - 1 - k]
            else:
                col = col.copy(); col[:, 3] = 0
            out[rows, (P - 1 - k) if lo else (P + C + k)] = col
    for side, top in ((1, True), (4, False)):            # vertical pads (the source repeats at its own period)
        for k in range(P):
            if mask & side:
                row = out[P + C - 1 - k] if top else out[P + k]
            else:
                row = out[P if top else P + C - 1].copy(); row[:, 3] = 0
            out[(P - 1 - k) if top else (P + C + k)] = row
    return out


def build(src_path: Path, band: int) -> Image.Image:
    src = np.asarray(Image.open(src_path).convert("RGBA"), dtype=np.float32) / 255
    if src_path.name.startswith("RM_SuspensionDeck_Rope"):
        # the rope deck's planks end short of the tile's top and bottom (clear gaps): cut them off so the run is continuous
        src = np.asarray(Image.fromarray((src[6:250] * 255 + .5).astype(np.uint8), "RGBA").resize((256, 256), Image.LANCZOS),
                         dtype=np.float32) / 255
    atlas = np.zeros((ATLAS, ATLAS, 4), np.float32)
    for i in range(16):
        r, c = divmod(i, 4)
        y = ATLAS - (r + 1) * T                          # rows count from the BOTTOM of the image
        atlas[y:y + T, c * T:(c + 1) * T] = tile(src, band, i)
    return Image.fromarray((atlas * 255 + .5).astype(np.uint8), "RGBA")


def sub_cell(atlas: Image.Image, i: int) -> Image.Image:
    """What the game shows for link index i: the inner 3/4 of its quarter tile."""
    r, c = divmod(i, 4)
    y = ATLAS - (r + 1) * T
    return atlas.crop((c * T + P, y + P, c * T + P + C, y + P + C))


# ----------------------------------------------------------- preview: the game's own selection logic, in Python
def tile_mask(map_links: dict[str, bool], horizontal: bool) -> int:
    """Mirror of RM_SuspensionDeckLink.TileMask: tile side t shows map side rot_cw(t) when the bridge runs E-W."""
    order = ["N", "E", "S", "W"]
    m = 0
    for k, t in enumerate(order):
        mapside = order[(k + (1 if horizontal else 0)) % 4]
        if map_links[mapside]:
            m |= 1 << k
    return m


def bridge_image(atlas: Image.Image, length: int, width: int, horizontal: bool, px: int = 128) -> Image.Image:
    gx, gz = (length, width) if horizontal else (width, length)
    cells = {(x, z) for x in range(gx) for z in range(gz)}
    out = Image.new("RGBA", (gx * px, gz * px), (0, 0, 0, 0))
    for (x, z) in cells:
        # map frame: +z is NORTH (up on screen); the image's row 0 is z = gz-1
        def has(dx, dz):
            n = (x + dx, z + dz)
            if n in cells:
                return True
            # beyond the run's ends: the anchors (a link); beyond its sides: nothing
            return (horizontal and dz == 0 and dx != 0) or ((not horizontal) and dx == 0 and dz != 0)
        links = {"N": has(0, 1), "E": has(1, 0), "S": has(0, -1), "W": has(-1, 0)}
        sub = sub_cell(atlas, tile_mask(links, horizontal))
        if horizontal:
            sub = sub.rotate(-90, expand=True)            # extraRotation 90 = clockwise
        out.alpha_composite(sub.resize((px, px), Image.LANCZOS), (x * px, (gz - 1 - z) * px))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    for src, dst, band in JOBS:
        if a.only and a.only not in dst:
            continue
        atlas = build(TEXROOT / (src + ".png"), band)
        out = HERE / "out" / (dst.replace("/", "_") + ".png")
        out.parent.mkdir(exist_ok=True)
        atlas.save(out)
        print("built", out.name)
        if a.install:
            sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
            import artledger as L
            print("  ", L.install_image(TEXROOT / (dst + ".png"), atlas,
                                        reason="script:src/RimMandrake/FlowWorks/art_source/SuspensionLooks/build_deck_atlas.py",
                                        provenance={"kind": "derived", "job": "suspension_deck_atlas", "from": src}))


if __name__ == "__main__":
    main()
