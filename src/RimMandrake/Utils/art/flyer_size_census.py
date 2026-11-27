#!/usr/bin/env python3
"""flyer_size_census.py - does each flyer's flight picture follow its life stage's size, or another stage's?

Found by RIMMANDRAKE_REDRAW_SKINFLAP_FLUTTER_BUTTERFLY_NOT_SAME_PICTURE. RimWorld 1.6 (AnimationDefGenerator_Flying)
sizes the flight frames of EVERY life stage from lifeStages.First() (the baby) when flyingAnimationInheritColors is
false and flyingAnimationDrawSizeIsMultiplier is true; when InheritColors is true it caches the animation by
bodyGraphicData.color, so a later stage with an earlier stage's colour gets that stage's size. Either way a flyer whose
stages grow flies at its baby's or juvenile's size (the Skinflap adult: 0.8 on the ground, 0.5 in the air).

The rule read here is the def's own, independent of the art: with the size as a multiplier, each stage's flight size
must be its own bodyGraphicData drawSize times the multiplier. The engine's size is computed by
selftest_skinflap_flutter.flight_sizes, written out from the decompile. A flyer with an absolute size
(IsMultiplier false) chose one flight size for every stage on purpose and is not judged here.

A stage's female graphic is judged too: the engine caches male and female animations in one colour cache unless a
female frame prefix is set, so a female whose colour matches another stage's flies at that stage's size.

Exit 0 = every multiplier flyer in src/ follows its stages, 1 = a flyer does not (listed), 2 = a def could not be
read (UNMEASURED, named). --except-held prints a flyer of a mod on the owner's hold list (mod_owner_hold.json) as
HELD and does not judge it: work on a held mod waits for its hold to lift.

    python3 src/RimMandrake/Utils/art/flyer_size_census.py [--except-held]
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import selftest_skinflap_flutter as T  # noqa: E402

TOL = 0.01


def kinds() -> list[tuple[str, Path, ET.Element]]:
    out = []
    for f in sorted((REPO / "src").rglob("Defs/**/*.xml")):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for pk in root.iter("PawnKindDef"):
            if (pk.findtext("flyingAnimationFramePathPrefix") or "").strip():
                out.append((pk.findtext("defName"), f, pk))
    return out


def held_mods() -> dict[str, str]:
    """{mod folder name: hold date} from the owner's hold list (mod_owner_hold.json)."""
    data = json.loads((REPO / "src/RimMandrake/rimflow/mod_owner_hold.json").read_text())
    return {h["mod"]: h.get("date", "?") for h in data["holds"]}


def mod_of(f: Path) -> str:
    """The mod folder of a def file: src/<tier>/<Mod>/Defs/..."""
    return f.relative_to(REPO / "src").parts[1]


def main(argv: list[str]) -> int:
    except_held = "--except-held" in argv
    held = held_mods() if except_held else {}
    off, blind, skipped, n = [], [], [], 0
    for d, f, pk in kinds():
        if (pk.findtext("flyingAnimationDrawSizeIsMultiplier") or "false").strip().lower() != "true":
            continue
        n += 1
        try:
            base = float(pk.findtext("flyingAnimationDrawSize") or "1")
            stages = pk.findall("lifeStages/li")
            own = [round(T.parse_size(s.findtext("bodyGraphicData/drawSize")) * base, 4) for s in stages]
            own_f = [round(T.parse_size(s.findtext("femaleGraphicData/drawSize")) * base, 4)
                     if s.find("femaleGraphicData") is not None else None for s in stages]
            both = T.flight_sizes_by_sex(pk)
            got = [round(m, 4) for m, _ in both]
            got_f = [round(x, 4) if x is not None else None for _, x in both]
        except (ValueError, IndexError, AttributeError) as e:
            blind.append(f"{d} ({f.relative_to(REPO)}): {type(e).__name__}: {e}")
            continue
        if not stages:
            blind.append(f"{d} ({f.relative_to(REPO)}): no lifeStages")
            continue
        bad = [i for i, (a, b) in enumerate(zip(own, got)) if abs(a - b) > TOL * a]
        bad += [i for i, (a, b) in enumerate(zip(own_f, got_f)) if a is not None and abs(a - b) > TOL * a]
        fem = f"; female flight {got_f}, own {own_f}" if any(x is not None for x in own_f) else ""
        line = f"{d}: flight size by stage {got}, own size by stage {own}{fem}"
        if bad and mod_of(f) in held:
            print(f"HELD {line} (mod {mod_of(f)} held by the owner since {held[mod_of(f)]}; not judged)")
            skipped.append(d)
            continue
        print(f"{'OFF' if bad else 'ok '} {line}")
        if bad:
            off.append(d)
    for b in blind:
        print(f"UNMEASURED {b}")
    tail = f", {len(skipped)} on held mods not judged" if except_held else ""
    print(f"{n} flyers sized as a multiplier, {len(off)} take another stage's size, {len(blind)} unmeasured{tail}")
    return 2 if blind else (1 if off else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
