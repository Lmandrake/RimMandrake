#!/usr/bin/env python3
"""Regression check: the DEF halves of the owner's followed notes on the ruled biome sheets.

SHEET_NOTES_FINISH_SEVENTEEN_DEF_HALVES. These are the 17 rows from the 2026-10-10 incomplete sweep
whose art redraw was carried out but whose def edit (description, size, rename, new creature)
was owed. Each row below pairs the owner's note (verbatim, from its sheet's decisions.json) with
what the def must now say. A failure means a later edit undid one of his notes.

Run: python3 src/RimMandrake/Utils/selftest_sheet_notes_def_halves.py   (exit 0 = all hold)
"""
import glob
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# (sheet row, defName, owner note, {field: expected}) — "desc~" is a list of lowercase
# substrings the description must all contain; "label", "bodySize", "adultDraw" are exact.
# "kind" demands a PawnKindDef of that defName whose <race> is the row's ThingDef; "roster" =
# (BiomeDef, minimum commonality) — the creature must be on that biome's <wildAnimals>, so a
# new creature cannot silently stop spawning.
ROWS = [
    ("abyss/DuskProwler", "RM_Ysvaltha",
     "Change description to match image. Make four glowing yellow eyes though.",
     {"desc~": ["four glowing yellow eyes"]}),
    ("abyss/Murkling", "RM_Lirrith",
     "Needs regenerated description ... dark-skinned with four yellow glowing eyes",
     {"desc~": ["dark skin", "four eyes glow yellow"]}),
    ("abyss/NightMule", "RM_Aveluthia",
     "Regenerate the description ... like black flesh. There should also be four glowing yellow eyes.",
     {"desc~": ["black flesh", "four yellow eyes glow"]}),
    ("abyss/Nightling", "RM_Sesserith",
     "Regenerate description based on image. Make its surface pitch black and its eyes glow yellow.",
     {"desc~": ["pitch black", "glowing yellow"]}),
    ("abyss/Septimum", "RM_PaddleVine",
     "Needs whole new description and name ... Wide paddles ... scarlet twining vine ... eye of a fly.",
     {"label": "paddle vine", "desc~": ["scarlet", "paddles", "flower-like leaf", "eye of a fly"]}),
    ("abyss/Aveluthia", "RM_Aveluthia",
     "(same note as NightMule, carried row)",
     {"desc~": ["black flesh"]}),
    ("abyss/PaddleVine", "RM_PaddleVine",
     "(same note as Septimum, carried row)",
     {"desc~": ["photoreceptors"]}),
    ("blue_desert/Thunderbeast", "RM_Thunderbeast",
     "Also needs improved description. Half the size.",
     {"bodySize": 0.75, "adultDraw": 1.25, "desc~": ["blue desert"]}),
    ("desert/Chorn", "RM_Chorn",
     "Make this thing 5 cells wide please ... Regenerate description.",
     {"label": "chorn", "adultDraw": 5.0, "desc~": ["hooked beak"]}),
    ("desert/Ultracactus", "RM_UltrissPad",
     "semi-transparent and mostly pale clear with only a hint of green. Rename this to Ultriss Pad.",
     {"label": "ultriss pad", "desc~": ["semi-transparent", "hint of green", "most extreme desert"]}),
    ("greysea/Hessal", "RM_Hessal",
     "A patch of frost lying on the floor, sealed for years ... Made of salt crystal. No legs.",
     {"desc~": ["patch of frost", "seals for years", "crystal"]}),
    ("leaningscrub/Chikka", "RM_Chikka",
     "reverse teardrop ... angry-looking pair of eyes ... pale green porcupine. Tiny feet ... Change description.",
     {"desc~": ["furious pair of eyes", "pale green quills", "porcupine", "tiny feet"]}),
    ("thescald/ScaldWalker", "RM_ScaldWalker",
     "Rename to Iridesce",
     {"label": "iridesce"}),
    ("thescald/Thuum", "RM_Thuum",
     "dull rainbows along its body length. Make its head armored ... Rename it to a Shimmer Eel.",
     {"label": "shimmer eel", "desc~": ["dull rainbows", "head is armored"]}),
    ("thesump/SumpMouse", "RM_SumpMouse",
     "less mouse-like and more alien please. Can still call it a sump mouse.",
     {"label": "sump-mouse"}),  # art half outstanding: SUMPMOUSE_ART_INSTALL_STILL_SQUEAKS
    ("twilightsea/DancingSkresh", "RM_DancingSkresh",
     "The existing (B) render should be made into its own new creature: The Dancing Skresh, new description.",
     {"label": "dancing skresh", "desc~": ["skresh"], "kind": "RM_DancingSkresh",
      "roster": ("RM_TwilightSea", 0.0)}),
    ("twilightsea/Hollu", "RM_Hollu",
     "this Hollu is supposed to be a section of almost stained glass-like waveglass ... curved-in piece of this sheet in its final life stage.",
     {"desc~": ["section of the waveglass", "stained glass", "transparent", "final life stage", "curls in"]}),
]
# The hollu's two catch items describe the same organism.
CATCH_DESC = {"RM_HolluCatch": ["section of the waveglass", "stained glass"],
              "RUT_Hollu": ["section of the waveglass", "stained glass"]}


def load():
    things, kinds, biomes = {}, {}, {}
    for f in glob.glob(os.path.join(ROOT, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for d in root:
            dn = d.findtext("defName")
            if not dn:
                continue
            if d.tag == "ThingDef":
                things[dn] = d
            elif d.tag == "PawnKindDef":
                kinds[dn] = d
            elif d.tag == "BiomeDef":
                biomes[dn] = d
    return things, kinds, biomes


def main():
    things, kinds, biomes = load()
    if len(things) < 500:  # sanity: the instrument can see the repo's defs
        print(f"FAIL: only {len(things)} ThingDefs parsed under {ROOT}/src — instrument blind")
        return 1
    bad = []
    for row, dn, note, want in ROWS:
        d = things.get(dn)
        if d is None:
            bad.append(f"{row}: {dn} missing")
            continue
        desc = " ".join((d.findtext("description") or "").lower().split())
        for k, v in want.items():
            if k == "label" and (d.findtext("label") or "").strip() != v:
                bad.append(f"{row}: {dn} label {d.findtext('label')!r} != {v!r}")
            elif k == "desc~":
                bad += [f"{row}: {dn} description lacks {s!r} (note: {note[:60]})" for s in v if s not in desc]
            elif k == "bodySize" and float(d.findtext("race/baseBodySize") or -1) != v:
                bad.append(f"{row}: {dn} baseBodySize {d.findtext('race/baseBodySize')} != {v}")
            elif k == "adultDraw":
                k_ = kinds.get(dn)
                ls = k_.findall("lifeStages/li") if k_ is not None else []
                got = float(ls[-1].findtext("bodyGraphicData/drawSize")) if ls else None
                if got != v:
                    bad.append(f"{row}: {dn} adult drawSize {got} != {v}")
            elif k == "kind":
                k_ = kinds.get(v)
                if k_ is None:
                    bad.append(f"{row}: PawnKindDef {v} missing — {dn} cannot spawn")
                elif (k_.findtext("race") or "").strip() != dn:
                    bad.append(f"{row}: PawnKindDef {v} race {k_.findtext('race')!r} != {dn!r}")
            elif k == "roster":
                biome, floor = v
                b = biomes.get(biome)
                el = b.find(f"wildAnimals/{dn}") if b is not None else None
                try:
                    c = float(el.text) if el is not None else None
                except (TypeError, ValueError):
                    c = None
                if b is None:
                    bad.append(f"{row}: BiomeDef {biome} missing")
                elif c is None or c <= floor:
                    bad.append(f"{row}: {dn} not on {biome} wildAnimals (commonality {c})")
    for dn, subs in CATCH_DESC.items():
        d = things.get(dn)
        desc = " ".join((d.findtext("description") or "").lower().split()) if d is not None else ""
        bad += [f"catch {dn}: description lacks {s!r}" for s in subs if s not in desc]
    for b in bad:
        print("FAIL:", b)
    print(f"{len(ROWS) - len({b.split(':')[0] for b in bad})}/{len(ROWS)} sheet rows hold; "
          f"{len(bad)} failure(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
