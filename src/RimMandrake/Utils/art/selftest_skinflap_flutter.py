#!/usr/bin/env python3
"""selftest_skinflap_flutter.py - the Skinflap is one size on the ground and in the air, and its flight is a
whole-body flutter, not two moving skin edges (RIMMANDRAKE_REDRAW_SKINFLAP_FLUTTER_BUTTERFLY_NOT_SAME_PICTURE).

Owner, at the joint flight sitting 2026-11-27 12:36 AM PST: the flying picture was the walking picture with two skin
edges that move, and the two differed in size; he asked for "a chaotic butterfly flying effect" and "the size
differential must be fixed".

Offline, read-only, no game. Checks:
  1. size: for every life stage, the texels-per-cell of the flight frames equal those of the walking picture, so the
     creature's own drawing is one size on the ground and in the air (the game's take-off lift and shadow are its own).
     The flight draw size is computed here the way RimWorld 1.6 computes it, written out by hand from the decompile of
     AnimationDefGenerator_Flying.InitializeNeededDefs (not imported from the module under test):
       - flyingAnimationInheritColors false and no female prefix: ONE size for every life stage, taken from
         lifeStages.First() (the baby) when the size is a multiplier;
       - otherwise: per life stage, but the animation is cached by bodyGraphicData.color, so a later stage with the
         same colour reuses the first stage's animation and its size.
  2. motion: in every facing, each flight frame differs from its neighbour (the loop's last frame against its first
     included) over at least half of the drawn body (the union of both frames' pixels with alpha > 128).
  3. form: the def's frame count of PNGs exists per facing; each frame is square, and no drawn pixel touches the
     canvas edge (a clipped creature).
Planted faults (each must be red): the parent's def (baby-sized flight), equal life-stage colours, a loop of one
repeated frame, frames that move only two edge strips.
Exit 0 = all pass, 1 = a check failed.

    python3 src/RimMandrake/Utils/art/selftest_skinflap_flutter.py
"""
from __future__ import annotations

import copy
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
DEFS = REPO / "src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml"
TEXROOT = REPO / "src/RimMandrake/Contagion/Textures"
DEF = "RM_Skinflap"
FACINGS = ("east", "north", "south")
MIN_CHANGED = 0.50     # share of the drawn body that must change between neighbouring frames
SIZE_TOL = 0.01        # relative: 1% of the texels per cell
DIFF_ALPHA = 64        # a pixel changed: alpha differs by more than this, or both drawn and RGB differs by more
DIFF_RGB = 40

fails: list[str] = []


def want(ok: bool, what: str) -> None:
    print(f"{'PASS' if ok else 'FAIL'} {what}")
    if not ok:
        fails.append(what)


def parse_color(text: str | None) -> tuple:
    """RimWorld's Color parse: '(r,g,b[,a])'; any component above 1 means the 0-255 scale. Unset is white."""
    if not text:
        return (1.0, 1.0, 1.0, 1.0)
    v = [float(x) for x in text.strip().strip("()").split(",")]
    if any(x > 1 for x in v):
        v = [x / 255.0 for x in v]
    if len(v) == 3:
        v.append(1.0)
    return tuple(round(x, 6) for x in v)


def parse_size(text: str | None) -> float:
    """drawSize.x: a scalar or '(x,y)'."""
    t = (text or "1").strip().strip("()")
    return float(t.split(",")[0])


def flight_sizes(pk: ET.Element) -> list[float]:
    """Per life stage, the drawSize the engine gives the flight frames (AnimationDefGenerator_Flying, 1.6)."""
    stages = pk.findall("lifeStages/li")
    base = float(pk.findtext("flyingAnimationDrawSize") or "1")
    mult = (pk.findtext("flyingAnimationDrawSizeIsMultiplier") or "false").strip().lower() == "true"
    inherit = (pk.findtext("flyingAnimationInheritColors") or "false").strip().lower() == "true"
    female = bool((pk.findtext("flyingAnimationFramePathPrefixFemale") or "").strip())
    if inherit or female:
        cache: dict = {}
        out = []
        for st in stages:
            num = parse_size(st.findtext("bodyGraphicData/drawSize")) * base if mult else base
            col = parse_color(st.findtext("bodyGraphicData/color"))
            if col not in cache:
                cache[col] = num
            out.append(cache[col])
        return out
    num = parse_size(stages[0].findtext("bodyGraphicData/drawSize")) * base if mult else base
    return [num] * len(stages)


def kind(root: ET.Element) -> ET.Element:
    pk = [e for e in root.findall("PawnKindDef") if e.findtext("defName") == DEF]
    if len(pk) != 1:
        raise SystemExit(f"{DEF}: PawnKindDef x{len(pk)} in {DEFS}")
    return pk[0]


def size_rows(pk: ET.Element) -> list[tuple[int, float, float]]:
    """(stage, ground texels per cell, flight texels per cell) per life stage."""
    prefix = pk.findtext("flyingAnimationFramePathPrefix")
    rows = []
    for i, (st, fly) in enumerate(zip(pk.findall("lifeStages/li"), flight_sizes(pk))):
        tex = st.findtext("bodyGraphicData/texPath")
        static_w = Image.open(TEXROOT / f"{tex}_east.png").width
        frame_w = Image.open(TEXROOT / f"{prefix}1_east.png").width
        rows.append((i, static_w / parse_size(st.findtext("bodyGraphicData/drawSize")), frame_w / fly))
    return rows


def size_ok(pk: ET.Element) -> tuple[bool, str]:
    rows = size_rows(pk)
    bad = [r for r in rows if abs(r[2] / r[1] - 1) > SIZE_TOL]
    txt = "; ".join(f"stage {i}: ground {g:.1f} px/cell, air {a:.1f} px/cell" for i, g, a in rows)
    return not bad, txt


def changed_share(a: np.ndarray, b: np.ndarray) -> float:
    aa, ba = a[..., 3].astype(int), b[..., 3].astype(int)
    body = (aa > 128) | (ba > 128)
    both = (aa > 128) & (ba > 128)
    rgb = np.abs(a[..., :3].astype(int) - b[..., :3].astype(int)).max(axis=2)
    diff = (np.abs(aa - ba) > DIFF_ALPHA) | (both & (rgb > DIFF_RGB))
    n = int(body.sum())
    return float((diff & body).sum() / n) if n else 0.0


def motion_ok(frames: list[np.ndarray]) -> tuple[bool, list[float]]:
    n = len(frames)
    shares = [changed_share(frames[k], frames[(k + 1) % n]) for k in range(n)]
    return (n > 1 and min(shares) >= MIN_CHANGED), shares


def load_frames(pk: ET.Element, facing: str) -> list[np.ndarray] | None:
    prefix, count = pk.findtext("flyingAnimationFramePathPrefix"), int(pk.findtext("flyingAnimationFrameCount") or 0)
    paths = [TEXROOT / f"{prefix}{k}_{facing}.png" for k in range(1, count + 1)]
    if not count or not all(p.is_file() for p in paths):
        return None
    return [np.asarray(Image.open(p).convert("RGBA")) for p in paths]


def edge_clear(f: np.ndarray) -> bool:
    a = f[..., 3]
    return not (a[0].any() or a[-1].any() or a[:, 0].any() or a[:, -1].any())


def planted(pk: ET.Element, frames: list[np.ndarray]) -> None:
    """Each planted fault must make its check red, or the check cannot see."""
    p = copy.deepcopy(pk)
    for tag in ("flyingAnimationInheritColors",):
        e = p.find(tag)
        if e is not None:
            e.text = "false"
    for st in p.findall("lifeStages/li"):
        c = st.find("bodyGraphicData/color")
        if c is not None:
            st.find("bodyGraphicData").remove(c)
    want(not size_ok(p)[0], "planted: inherit colours off (sizes from the first life stage) is red")
    p = copy.deepcopy(pk)
    for st in p.findall("lifeStages/li"):
        g = st.find("bodyGraphicData")
        c = g.find("color")
        if c is None:
            c = ET.SubElement(g, "color")
        c.text = "(255,255,255)"
    want(not size_ok(p)[0], "planted: equal life-stage colours (the engine's colour cache) is red")
    want(not motion_ok([frames[0]] * len(frames))[0], "planted: a loop of one repeated frame is red")
    edges = []
    for k in range(len(frames)):
        f = frames[0].copy()
        w = f.shape[1]
        f[:, : w // 6] = np.roll(frames[0][:, : w // 6], 6 * (k % 2), axis=0)
        f[:, -w // 6:] = np.roll(frames[0][:, -w // 6:], -6 * (k % 2), axis=0)
        edges.append(f)
    want(not motion_ok(edges)[0], "planted: frames that move only two edge strips are red")


def main() -> int:
    root = ET.parse(DEFS).getroot()
    pk = kind(root)
    ok, txt = size_ok(pk)
    want(ok, f"{DEF}: one size on the ground and in the air ({txt})")
    first = None
    for f in FACINGS:
        frames = load_frames(pk, f)
        want(frames is not None, f"{DEF} {f}: every flight frame PNG exists")
        if frames is None:
            continue
        first = first or frames
        want(all(fr.shape[0] == fr.shape[1] for fr in frames), f"{DEF} {f}: frames are square")
        want(all(edge_clear(fr) for fr in frames), f"{DEF} {f}: no drawn pixel touches the canvas edge")
        ok, shares = motion_ok(frames)
        want(ok, f"{DEF} {f}: each frame differs from its neighbour over >= {MIN_CHANGED:.0%} of the body "
                 f"(min {min(shares):.0%}, all {[round(s, 2) for s in shares]})")
    if first:
        planted(pk, first)
    print(f"{'OK' if not fails else 'FAILED'}: {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
