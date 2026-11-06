#!/usr/bin/env python3
"""selftest_skerrel_bespoke_art — SKERREL_REDRAW_BESPOKE_SHARED_FIREWASP_ART.

RM_Skerrel (the wasp) and RM_SkerrelGall once borrowed other creatures' art
(Pyrelands' FireWasp; the gall's header named RegenerantVeil), so a redraw of
the Fire Wasp silently changed the skerrel too. This pins the bespoke art:

  1. every texPath of RM_Skerrel's PawnKindDef lifeStages and RM_SkerrelGall's
     graphicData resolves to PNG(s) inside Greentide's own Textures folder
     (Graphic_Multi: _south, _east, _north; Graphic_Single: the bare file);
  2. each PNG is RGBA with real alpha (clear corners, some fully opaque pixels);
  3. no PNG is pixel-identical to any FireWasp or RegenerantVeil PNG;
  4. the delegated judge verdict for the wasp exists and reads overall KEEP.

A control case proves check 3 can see: a FireWasp PNG compared to itself must
be flagged identical (a blind comparator would pass anything).
"""
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / "src/RimMandrake/Greentide"
RACE = MOD / "Defs/ThingDefs_Races/RM_Skerrel_Race.xml"
GALL = MOD / "Defs/ThingDefs/RM_SkerrelGall.xml"
VERDICT = ROOT / "infrastructure/state/delegated/2026-11-05/RM_Skerrel.json"
BORROWED_DIRS = [
    ROOT / "src/RimMandrake/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands/FireWasp",
    ROOT / "src/RimMandrake/TheRot/Textures/RotSporeKit/Things/Plant/RegenerantVeil",
]

FAILS = []


def fail(msg):
    FAILS.append(msg)
    print("FAIL", msg)


def pixel_hash(p):
    im = Image.open(p).convert("RGBA")
    return hashlib.sha256(im.tobytes() + repr(im.size).encode()).hexdigest()


def graphic_nodes(path, defname, tag):
    root = ET.parse(path).getroot()
    out = []
    for d in root:
        if d.findtext("defName") != defname:
            continue
        for g in d.iter(tag):
            out.append((g.findtext("texPath"), g.findtext("graphicClass")))
    return out


def resolve(tex, cls):
    base = MOD / "Textures" / tex
    if cls == "Graphic_Multi":
        return [base.parent / f"{base.name}_{f}.png" for f in ("south", "east", "north")]
    return [base.with_suffix(".png")]


def main():
    borrowed = {}
    for d in BORROWED_DIRS:
        pngs = sorted(d.glob("*.png"))
        if not pngs:
            fail(f"instrument blind: no borrowed PNGs under {d}")
        for p in pngs:
            borrowed[pixel_hash(p)] = p
    # control: the comparator must flag a known borrowed file as identical
    ctl = next(iter(sorted(BORROWED_DIRS[0].glob("*.png"))), None)
    if ctl is None or pixel_hash(ctl) not in borrowed:
        fail("control: comparator did not flag a FireWasp PNG against itself")

    nodes = [("RM_Skerrel", n) for n in graphic_nodes(RACE, "RM_Skerrel", "bodyGraphicData")]
    nodes += [("RM_SkerrelGall", n) for n in graphic_nodes(GALL, "RM_SkerrelGall", "graphicData")]
    wasp = len([n for n in nodes if n[0] == "RM_Skerrel"])
    if wasp < 3:
        fail(f"RM_Skerrel: expected 3 lifeStage bodyGraphicData, found {wasp}")
    if not any(n[0] == "RM_SkerrelGall" for n in nodes):
        fail("RM_SkerrelGall: no graphicData found")

    checked = 0
    for owner, (tex, cls) in nodes:
        if not tex:
            fail(f"{owner}: empty texPath")
            continue
        for p in resolve(tex, cls):
            if not p.is_file():
                fail(f"{owner}: {p.relative_to(ROOT)} missing from Greentide's Textures")
                continue
            im = Image.open(p)
            if im.mode != "RGBA":
                fail(f"{owner}: {p.name} mode {im.mode}, not RGBA")
                continue
            a = im.getchannel("A")
            w, h = im.size
            corners = [a.getpixel(c) for c in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
            if any(corners):
                fail(f"{owner}: {p.name} corners not clear {corners}")
            if a.histogram()[255] == 0:
                fail(f"{owner}: {p.name} has no fully opaque pixel")
            hit = borrowed.get(pixel_hash(p))
            if hit:
                fail(f"{owner}: {p.name} is pixel-identical to {hit.relative_to(ROOT)}")
            checked += 1

    if not VERDICT.is_file():
        fail(f"judge verdict missing: {VERDICT.relative_to(ROOT)}")
    else:
        v = json.loads(VERDICT.read_text())
        if str(v.get("overall", "")).upper() != "KEEP":
            fail(f"judge verdict overall={v.get('overall')!r}, not KEEP")

    print(f"checked {checked} PNG(s) against {len(borrowed)} borrowed PNG hash(es)")
    if checked < 4:
        fail(f"only {checked} PNGs checked; expected 3 wasp facings + 1 gall")
    print("RESULT", "FAIL" if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
