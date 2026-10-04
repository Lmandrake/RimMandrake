"""make_hose_open_end.py -- the plain open hose end (owner review 2026-10-04 B8).

    python3 src/RimMandrake/Utils/mockups/messy_conduit/make_hose_open_end.py

Owner: *"hose end with fire hose-like end has mismatched hose width. Should not look like a firehose ending, just an
open ending."* Writes Textures/.../Hose/OpenEnd.png (128x128): the flat hose strip itself (Strand_Flat.png, so colour
and weave match the laid hose exactly) entering from -X at a 40 px band, ending in a cut mouth at x = 102 (+0.30
canvas, RM_MapComponent_Hoses.OpenMouth): a slightly lighter rim ellipse round a dark bore. No fitting.
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
H = os.path.join(HERE, "..", "..", "..", "MessyConduit", "Textures", "RimMandrake", "MessyConduit", "Hose")
MOUTH = 102


def main():
    strip = Image.open(os.path.join(H, "Strand_Flat.png")).convert("RGBA")   # 256x64, opaque band rows 2-60
    band = strip.crop((0, 2, 256, 61)).resize((int(256 * 40 / 59), 40), Image.LANCZOS)
    c = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    c.alpha_composite(band.crop((0, 0, MOUTH, 40)), (0, 44))
    d = ImageDraw.Draw(c)
    rim = tuple(min(255, int(v * 1.15)) for v in band.getpixel((10, 20))[:3]) + (255,)
    d.ellipse((MOUTH - 6, 44, MOUTH + 6, 83), fill=rim)
    d.ellipse((MOUTH - 4, 48, MOUTH + 4, 79), fill=(22, 16, 12, 255))
    c.save(os.path.join(H, "OpenEnd.png"))
    print("wrote OpenEnd.png, alpha bbox", c.getchannel("A").getbbox())


if __name__ == "__main__":
    main()
