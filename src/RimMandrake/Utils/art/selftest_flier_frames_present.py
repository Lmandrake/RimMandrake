#!/usr/bin/env python3
"""selftest_flier_frames_present.py - every flier flip-book our defs declare exists in src and animates.

FLIER_FRAMES_FILL_FIVE_GHOST_FLOCKS: a `flyingAnimationFramePathPrefix[Female]` whose PNGs are missing from the mod
draws a bad texture the first time the animal takes off (Brezak, Drexl, Thranta, Tibidee shipped that way until
2026-10-20). Offline, read-only. For every ThingDef in src/**/Defs that sets a prefix:
  * frames 1..flyingAnimationFrameCount x {east,north,south} exist under that mod's Textures/ (west mirrors east), or
    the prefix is a vanilla asset listed in VANILLA (RM_Kirruk reuses Core's Chicken_Flying_ by design);
  * per facing the frames are not all pixel-identical (identical frames = a flip-book that does not move).
A sanity probe first proves the scan sees the known sets, so a parse/glob bug cannot pass as "nothing missing".
    python3 src/RimMandrake/Utils/art/selftest_flier_frames_present.py
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[4]
SRC = REPO / "src"
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
FACINGS = ("east", "north", "south")
TAGS = ("flyingAnimationFramePathPrefix", "flyingAnimationFramePathPrefixFemale")
# Vanilla flip-books a def may reuse (not in src by design). Prefix -> why.
VANILLA = {"Things/Pawn/Animal/Chicken/Chicken_Flying_": "Core Chicken flip-book (RM_Kirruk)"}
# Sets that must be seen, so a blind scan fails loudly instead of passing empty.
MUST_SEE = ("swanimals/Brezak/Brezak_Flying_", "swanimals/Drexl/Drexl_Flying_", "swanimals/Thranta/Thranta_Flying_",
            "swanimals/Tibidee/Tibidee_Flying_", "swanimals/Beldon/BeldonC_Flying_")


def mod_root(p: Path) -> Path:
    m = p
    while m.parent.name not in TIERS:
        if m.parent == m:
            raise ValueError(f"{p} is not under a tier folder")
        m = m.parent
    return m


def declared():
    """Yield (xml path, defName, tag, prefix, frame count, mod root) for every prefix a def sets."""
    for p in sorted(SRC.rglob("*.xml")):
        if "Defs" not in p.parts:
            continue
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for td in root.iter():
            for tag in TAGS:
                e = td.find(tag)
                if e is None or not (e.text or "").strip():
                    continue
                n = int((td.findtext("flyingAnimationFrameCount") or "0").strip() or 0)
                yield p, td.findtext("defName") or "?", tag, e.text.strip(), n, mod_root(p)


def frame(mod: Path, prefix: str, i: int, facing: str):
    hits = sorted(mod.glob(f"**/Textures/{prefix}{i}_{facing}.png"))
    return hits[0] if hits else None


def identical(paths) -> bool:
    ims = [Image.open(x).convert("RGBA") for x in paths]
    if len({im.size for im in ims}) > 1:
        return False
    # Byte compare: getbbox() on an RGBA difference reads alpha only, so it calls recoloured frames identical.
    return all(ims[0].tobytes() == im.tobytes() for im in ims[1:])


def main() -> int:
    rows = list(declared())
    seen = {r[3] for r in rows}
    fails = []
    lost = [m for m in MUST_SEE if m not in seen]
    if len(rows) < 20 or lost:
        print(f"FAIL sanity: scan saw {len(rows)} prefixes; missing known sets {lost}")
        return 1
    checked = 0
    for p, dn, tag, prefix, n, mod in rows:
        where = f"{p.relative_to(REPO)} {dn} {tag}"
        if prefix in VANILLA:
            continue
        if n < 1:
            fails.append(f"{where}: prefix {prefix} with flyingAnimationFrameCount {n}")
            continue
        for facing in FACINGS:
            got = [frame(mod, prefix, i, facing) for i in range(1, n + 1)]
            miss = [i for i, g in enumerate(got, 1) if g is None]
            if miss:
                fails.append(f"{where}: {prefix}<{miss}>_{facing}.png missing under {mod.relative_to(REPO)}/**/Textures")
            elif n > 1 and identical(got):
                fails.append(f"{where}: {prefix}*_{facing} - all {n} frames pixel-identical (no animation)")
        checked += 1
    for f in fails:
        print("FAIL", f)
    print(f"{'FAIL' if fails else 'PASS'} flier frames: {checked} sets checked, {len(rows) - checked} vanilla, "
          f"{len(fails)} problems")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
