"""raw/<tag>_{north,south,east}.png -> out/<tag>/RM_PitRamp_<facing>.png, 256 px, west = east mirrored.

Premultiplied BOX to 256 (no dark halo, no LANCZOS ringing), alpha < 32 zeroed, > 235 snapped solid.
    python3 finalize_v2.py A B C
"""
import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
SIZE = 256


def conform(im):
    im = im.convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v >= 32 else 0).getbbox()
    im = im.crop(bb)                                         # fill the cell like the guide did (8 px inset, as v1 north)
    im = im.convert("RGBa").resize((SIZE - 16, SIZE - 16), Image.BOX).convert("RGBA")
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    out.alpha_composite(im, (8, 8))
    out.putalpha(out.getchannel("A").point(lambda v: 0 if v < 32 else (255 if v > 235 else v)))
    return out


def main(tags):
    for tag in tags:
        o = HERE / "out" / tag
        o.mkdir(parents=True, exist_ok=True)
        done = {f: conform(Image.open(HERE / "raw" / f"{tag}_{f}.png")) for f in ("north", "south", "east")}
        done["west"] = done["east"].transpose(Image.FLIP_LEFT_RIGHT)
        for f, im in done.items():
            im.save(o / f"RM_PitRamp_{f}.png")
        print(tag, "ok")


if __name__ == "__main__":
    main(sys.argv[1:])
