#!/usr/bin/env python3
"""DESERT_PORT_PLACEHOLDER_ART_1: wire the 13 remaining species' already-generated
artpipe renders (from infrastructure/artpipe/done/) into their ThingDef texPaths,
replacing the donor placeholder paths. One-shot, not reusable."""
import shutil
from pathlib import Path

REPO = Path("/mnt/d/Luke/dev/Rimworld")
ARTSRC = REPO / "infrastructure/artpipe/_artsrc"
TEX_ROOT = REPO / "src/RimStarWars/SWBestiary/Textures/Things"

# defName -> list of (donor_texpath, replace_with_our_new_path) pairs, LONGEST
# donor string first so a "_baby"-suffixed variant is matched before its own
# shorter prefix would otherwise eat it first.
FAUNA_REPLACEMENTS = {
    "RSW_Sandstrider": [("Things/Pawn/Animal/AA_DesertAve/AA_DesertAve", None)],
    "RSW_Spineroller": [("Things/Pawn/Animal/AA_Needleroll/AA_Needleroll", None)],
    "RSW_Sandhorn": [
        # baby stage donor uses a distinct "_baby" texture; we have no separate
        # baby render, so point it at the same adult render (same shortcut the
        # donor itself used for every OTHER species in this file).
        ("Things/Pawn/Animal/AA_Gigantelope/AA_Gigantelope_baby", "SELF"),
        ("Things/Pawn/Animal/AA_Gigantelope/AA_Gigantelope", None),
    ],
    "RSW_Dunestalker": [("Things/Pawn/Animal/AA_SandProwler/AA_SandProwler", None)],
    "RSW_Ferroclaw": [("Things/Pawn/Animal/AA_Terramorph/AA_Terramorph", None)],
    "RSW_Sandmaw": [("Things/Pawn/Animal/AA_SandSquid/AA_SandSquid", None)],
    "RSW_Tuskcoil": [("Things/Pawn/Animal/AA_MammothWorm/AA_MammothWorm", None)],
    "RSW_Cindermite": [("Things/Pawn/Animal/Fuelmite/Fuelmite", None)],
    "RSW_Stareling": [("Things/Pawn/Animal/AA_Eyeling/AA_Eyeling", None)],
    "RSW_Voltmaw": [("Things/Pawn/Animal/AA_TetraSlug/AA_TetraSlug", None)],
}

FAUNA_FILE = REPO / "src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml"
PLANTS_FILE = REPO / "src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Plants.xml"

FACINGS = ["south", "east", "north"]


def copy_fauna_art(name):
    dest_dir = TEX_ROOT / "Pawn/Animal" / name
    dest_dir.mkdir(parents=True, exist_ok=True)
    for facing in FACINGS:
        src = ARTSRC / f"{name}_{facing}" / f"{name}_{facing}.png"
        assert src.exists(), f"missing render: {src}"
        dest = dest_dir / f"{name}_{facing}.png"
        shutil.copyfile(src, dest)
    return f"Things/Pawn/Animal/{name}/{name}"


def copy_plant_art(name):
    dest_dir = TEX_ROOT / "Plant" / name
    dest_dir.mkdir(parents=True, exist_ok=True)
    src = ARTSRC / name / f"{name}.png"
    assert src.exists(), f"missing render: {src}"
    dest = dest_dir / f"{name}A.png"
    shutil.copyfile(src, dest)
    return f"Things/Plant/{name}"


def apply_replacements(text, pairs):
    for donor_path, new_path in pairs:
        count = text.count(donor_path)
        assert count > 0, f"{donor_path!r} not found (0 occurrences)"
        text = text.replace(donor_path, new_path)
        print(f"  {donor_path} -> {new_path}  ({count}x)")
    return text


def main():
    print("Copying art + rewriting fauna texPaths:")
    ftext = FAUNA_FILE.read_text()
    for name, pairs in FAUNA_REPLACEMENTS.items():
        new_path = copy_fauna_art(name)
        resolved = [(d, new_path if n is None or n == "SELF" else n) for d, n in pairs]
        print(f" {name}:")
        ftext = apply_replacements(ftext, resolved)
    FAUNA_FILE.write_text(ftext)

    print("\nCopying art + rewriting plant texPaths:")
    ptext = PLANTS_FILE.read_text()

    sweetbark_new = copy_plant_art("RSW_SweetbarkTree")
    print(" RSW_SweetbarkTree (unique donor path, global replace):")
    ptext = apply_replacements(ptext, [("Things/Plants/AB_DessertTree", sweetbark_new)])

    # Dunegrass and VellaraBloom both currently point at the SAME donor path
    # (AB_Aaklac) -- scope each replacement to its own <defName>...</graphicData>
    # block so they don't clobber each other.
    for name in ("RSW_Dunegrass", "RSW_VellaraBloom"):
        new_path = copy_plant_art(name)
        marker = f"<defName>{name}</defName>"
        idx = ptext.index(marker)
        block_end = ptext.index("</graphicData>", idx)
        block = ptext[idx:block_end]
        assert "Things/Plants/AB_Aaklac" in block, f"{name}: AB_Aaklac not in its own block"
        new_block = block.replace("Things/Plants/AB_Aaklac", new_path)
        ptext = ptext[:idx] + new_block + ptext[block_end:]
        print(f" {name}: Things/Plants/AB_Aaklac -> {new_path}  (scoped to its own block)")

    PLANTS_FILE.write_text(ptext)
    print("\nDone.")


if __name__ == "__main__":
    main()
