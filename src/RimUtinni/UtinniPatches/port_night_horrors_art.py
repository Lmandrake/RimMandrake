#!/usr/bin/env python3
"""HORRORS_RAIDING_FACTION_1: install the stand-in Assailant-horror art into UtinniPatches through the art ledger.

The donor (Mlie.Horrors, ws 3535224844) ships its textures only inside an AssetBundle and is off the live mod list.
Extract them first (Windows python, UnityPy):
    python.exe src/RimMandrake/Utils/extract_bundle.py '<workshop>\\3535224844\\AssetBundles\\Mlie_Horrors' --extract <DIR> --keep-paths
then:
    python3 src/RimUtinni/UtinniPatches/port_night_horrors_art.py <DIR>/things [--dry-run]
Each picture is downscaled to at most 512 px on its long side (the donor's run to 2000 px) and installed by
artledger.install_bytes at Textures/RimUtinni/UtinniPatches/NightHorrors/<name>. Stand-in art, as the tail-donor
retirement precedent did (design/RimMandrake/tail_mods_art_retirement_2026-10-18.md); a redraw replaces it later."""
import io
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "RimMandrake", "Utils", "art"))
import artledger  # noqa: E402

DST = os.path.join(HERE, "Textures", "RimUtinni", "UtinniPatches", "NightHorrors")
REASON = "script:src/RimUtinni/UtinniPatches/port_night_horrors_art.py"
FACINGS = {
    "pawn/animal/bulwark/bulwark_%s.png": "Bulwark/Bulwark_%s.png",
    "pawn/animal/harvester/harvester_%s.png": "Harvester/Harvester_%s.png",
    "pawn/animal/prowler/prowler_%s.png": "Prowler/Prowler_%s.png",
}
SINGLE = {
    "building/hive/horrornest.png": "Hive/HorrorHive.png",
    "building/hive/den.png": "Hive/HorrorDen.png",
    "building/hive/burrow.png": "Hive/HorrorBurrow.png",
    "building/hive/sinkhole.png": "Hive/HorrorSinkhole.png",
    "building/hive/crysalis.png": "Hive/HorrorCrysalis.png",
    "building/hive/mitenest.png": "Hive/HorrorMiteLarder.png",
}


def pairs():
    for s, d in FACINGS.items():
        for f in ("north", "east", "south"):
            yield s % f, d % f
    yield from SINGLE.items()


def main(src, dry_run=False, cap=512):
    for s, d in pairs():
        im = Image.open(os.path.join(src, s)).convert("RGBA")
        k = min(1.0, cap / max(im.size))
        if k < 1.0:
            im = im.resize((max(1, round(im.size[0] * k)), max(1, round(im.size[1] * k))), Image.LANCZOS)
        b = io.BytesIO()
        im.save(b, format="PNG", optimize=True)
        r = artledger.install_bytes(os.path.join(DST, d), b.getvalue(), reason=REASON, dry_run=dry_run)
        print(r.get("status"), d, im.size)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], dry_run="--dry-run" in sys.argv)
