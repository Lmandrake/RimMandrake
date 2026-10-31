#!/usr/bin/env python3
"""pack_placeholder_repair.py -- install a transparent `<texPath>Pack_<facing>.png` for every SWBestiary
pack-animal graphic that ships none (DONOR_PACK_TEX_REPAIR_SEVEN_LEFT_BEHIND).

    python3 src/RimStarWars/SWBestiary/art/pack_placeholder_repair.py            # plan
    python3 src/RimStarWars/SWBestiary/art/pack_placeholder_repair.py --apply    # write through the art ledger

The list of missing files comes from selftest_swbestiary_pack_textures.py --list-missing, so the
repair and the check can never disagree about the rule.

Why transparent and not a byte copy of the base facing (the Ronto repair, 4c3071cca3): the engine
draws the Pack graphic with ShaderDatabase.Cutout and Color.white over the body
(PawnRenderNode_AnimalPack.GraphicFor). A copy of the body redraws it untinted, so a pack animal
with a graphic colour would lose its tint whenever it carries cargo, and 159 copies are ~30 MB.
A transparent 4x4 draws nothing: the animal looks exactly as it does today and the startup
"Failed to find any textures at ...Pack" error is gone. Real saddlebag art is owed separately
(BESTIARY_PACK_ART_REDRAW_REAL_SADDLEBAGS) and replaces these through the art ledger.
"""
import os
import struct
import subprocess
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MOD, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "art"))


def transparent_png(w=4, h=4):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + b"\x00\x00\x00\x00" * w for _ in range(h))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def missing():
    out = subprocess.run([sys.executable, os.path.join(MOD, "selftest_swbestiary_pack_textures.py"), "--list-missing"],
                         capture_output=True, text=True, check=True).stdout
    return [ln.split("\t")[1] for ln in out.splitlines() if "\t" in ln]


def main(argv):
    apply = "--apply" in argv
    todo = missing()
    print("%d Pack facing file(s) missing" % len(todo))
    if not apply:
        for rel in todo:
            print("  would write Textures/" + rel)
        return 0
    from artwrite import TextureWriter
    tw = TextureWriter(__file__, provenance={"placeholder": "transparent-4x4",
                                             "item": "DONOR_PACK_TEX_REPAIR_SEVEN_LEFT_BEHIND"})
    data = transparent_png()
    for rel in todo:
        tw.put(data, os.path.join(MOD, "Textures", rel))
    return 1 if tw.report() else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
