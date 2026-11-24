#!/usr/bin/env python3
"""Compare adult standing and frame-1 flying widths from src defs and PNGs."""
import math
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from def_inventory import resolve_inherit, txt  # noqa: E402

HELD_MODS = {
    "GimmeSomeSlack", "FlowWorks", "ExplosiveKnockback", "Pyrelands", "Contagion",
    "Cauldron", "FeverWood", "GelatinousSlime", "LeaningScrub", "Stillsand", "Graffiti",
}
EXCEPTIONS = {"RM_Kirruk": "vanilla Chicken flight frames are unavailable in src"}


def opaque_fraction(textures, tex_path):
    for folder in textures:
        for suffix in ("_east.png", "_south.png", ".png"):
            path = folder / (tex_path + suffix)
            if path.is_file():
                with Image.open(path) as image:
                    alpha = image.convert("RGBA").getchannel("A")
                    box = alpha.point(lambda value: 255 if value > 32 else 0).getbbox()
                    if box is None:
                        raise ValueError(f"empty alpha bounds in {path}")
                    return (box[2] - box[0]) / image.width
    raise FileNotFoundError(f"texture missing from src: {tex_path}")


def draw_width(value, field):
    if not value:
        raise ValueError(f"missing {field}")
    width = float(value.strip("()").split(",")[0])
    if not math.isfinite(width) or width < 0:
        raise ValueError(f"invalid {field}: {value}")
    return width


def measure(kind, prefix, textures):
    adult = kind.find("lifeStages/li[last()]/bodyGraphicData")
    standing_size = draw_width(txt(adult, "drawSize"), "adult drawSize")
    if standing_size == 0:
        raise ValueError("zero adult drawSize")
    standing_tex = txt(adult, "texPath")
    if not standing_tex or not prefix:
        raise ValueError("missing adult texPath or default flight prefix")
    flying_size = draw_width(txt(kind, "flyingAnimationDrawSize"), "flyingAnimationDrawSize")
    # RimWorld 1.6 uses absolute size unless the flag scales the standing graphic's drawSize.
    flying_unit = opaque_fraction(textures, prefix + "1")
    if txt(kind, "flyingAnimationDrawSizeIsMultiplier").lower() == "true":
        flying_unit *= standing_size
    standing_width = standing_size * opaque_fraction(textures, standing_tex)
    return flying_size * flying_unit / standing_width, standing_width / flying_unit


def main(root=HERE.parents[3]):
    kinds, named, cache = [], {}, {}
    counts = Counter()
    for path in sorted(root.glob("src/**/Defs/**/*.xml")):
        try:
            defs = ET.parse(path).getroot()
        except (ET.ParseError, OSError) as exc:
            print(f"UNRESOLVED {path.relative_to(root)}: {exc}")
            counts["UNRESOLVED"] += 1
            continue
        if defs.tag != "Defs":
            continue
        mod = next(parent.parent for parent in path.parents if parent.name == "Defs")
        for kind in defs:
            if kind.tag.split(".")[-1] != "PawnKindDef":
                continue
            if kind.get("Name"):
                named[kind.get("Name")] = kind
            if kind.get("Abstract", "false").lower() != "true":
                kinds.append((mod, kind))

    texture_dirs = sorted(root.glob("src/**/Textures"))
    flyers = 0
    for mod, kind in sorted(kinds, key=lambda row: txt(row[1], "defName")):
        kind, _, _ = resolve_inherit(kind, named, cache)
        prefix = txt(kind, "flyingAnimationFramePathPrefix")
        if not prefix and not txt(kind, "flyingAnimationFramePathPrefixFemale"):
            continue
        flyers += 1
        name = txt(kind, "defName") or str(mod.relative_to(root)) + " (missing defName)"
        local = mod / "Textures"
        if mod.name in HELD_MODS:
            status, detail = "EXCEPTION", f"held mod ({mod.name})"
        elif name in EXCEPTIONS and prefix == "Things/Pawn/Animal/Chicken/Chicken_Flying_":
            status, detail = "EXCEPTION", EXCEPTIONS[name]
        else:
            try:
                ratio, target = measure(kind, prefix, [local] + [d for d in texture_dirs if d != local])
                status = "PASS" if 0.75 <= ratio <= 1.5 else "FAIL"
                detail = f"ratio {ratio:.2f}"
                if status == "FAIL":
                    detail += f" (flyingAnimationDrawSize {target:.2f} for ratio 1.0)"
            except (OSError, ValueError) as exc:
                status, detail = "UNRESOLVED", str(exc)
        print(f"{status} {name} {detail}")
        counts[status] += 1

    if not flyers:
        print("EMPTY: no PawnKindDefs with a flying animation in src")
    print(f"flyers {flyers}: {counts['PASS']} PASS, {counts['FAIL']} FAIL, "
          f"{counts['UNRESOLVED']} UNRESOLVED, {counts['EXCEPTION']} EXCEPTION")
    return int(not flyers or counts["FAIL"] > 0 or counts["UNRESOLVED"] > 0)


if __name__ == "__main__":
    sys.exit(main())
