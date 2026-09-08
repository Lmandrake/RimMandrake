#!/usr/bin/env python3
"""Cut the east pair out of a raw generator frame, and MEASURE the three
constants build_eopie_sled_east.py needs, instead of leaving them hand-tuned.

WHY THIS EXISTS. The first east pair was cut and its constants
(ANIMAL_CY_FRACS, ATTACH_X_FRAC) were measured by hand and written into the
build script. That is fine once and a trap twice: any regenerated pair has a
different silhouette, so the hand numbers silently point at the wrong part of
the new animal — the traces attach to a shoulder that has moved. This script
re-derives them from the pixels every time, so a regeneration costs one run
instead of one careful remeasure.

WHAT IT DOES
  1. chroma-keys the raw's flat #00ff00 to real alpha (via the shared
     skills/generating-images/scripts/chroma_key.py, same threshold path the
     first cut used — the cut is not a second, divergent implementation).
  2. crops to the subject's alpha bbox. That is exactly how the shipped
     eopie_pair_gen_east.png was cut: raw subject x 462-1334, y 19-797 is
     873x779, its committed size to the pixel.
  3. splits the subject into its two animals by finding the empty rows between
     them, and reports each one's vertical centre as a fraction of the crop's
     height -> ANIMAL_CY_FRACS.
  4. finds the collar — the rightmost harness-brown column that still has
     animal above and below it — and reports it as a fraction of the crop's
     width -> ATTACH_X_FRAC.

⚠️ It does NOT write the build script. It prints the constants; you paste them,
and you look at the numbers first. A measurement that moved a long way from the
old value means the generator drifted more than the muzzle, which is a review
finding, not a paste.

Run:  /home/mandrake/.venvs/art/bin/python Source/recrop_east_v2.py \
          Source/art/raw/sled_east_raw_v2.png Source/art/eopie_pair_gen_east_v2.png
      (Pillow is not on the system python here; that venv has it.)
"""

import os
import subprocess
import sys
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CHROMA = os.path.join(REPO, "skills", "generating-images", "scripts",
                      "chroma_key.py")

# Harness leather, from the build scripts. Used only to FIND the collar, never
# to paint anything.
LEATHER = (99, 65, 24)
LEATHER_TOL = 60


def _keyed(raw_path: str) -> Image.Image:
    """Chroma-key via the shared script so this cut matches the first one."""
    tmp = os.path.join(tempfile.gettempdir(), "east_keyed.png")
    subprocess.run([sys.executable, CHROMA, "--input", raw_path, "--out", tmp],
                   check=True, capture_output=True)
    return Image.open(tmp).convert("RGBA")


def _animal_bands(img: Image.Image):
    """Row runs that contain animal. The traces cross the whole width, so a row
    is only 'animal' if it is thick — a trace is a handful of px, a body is
    hundreds."""
    px = img.load()
    w, h = img.size
    counts = [sum(1 for x in range(w) if px[x, y][3] > 8) for y in range(h)]
    thick = max(counts) * 0.25
    bands, run = [], None
    for y, c in enumerate(counts):
        if c >= thick and run is None:
            run = y
        elif c < thick and run is not None:
            bands.append((run, y - 1))
            run = None
    if run is not None:
        bands.append((run, h - 1))
    return bands


def _body_left(img: Image.Image) -> int:
    """First column that is a BODY rather than a rope."""
    px = img.load()
    w, h = img.size
    counts = [sum(1 for y in range(h) if px[x, y][3] > 8) for x in range(w)]
    thick = max(counts) * 0.30
    for x, c in enumerate(counts):
        if c >= thick:
            return x
    return 0


def _is_leather(r: int, g: int, b: int) -> bool:
    """Harness brown, and NOT the black keyline's anti-aliased edge.

    ⚠️ Distance-to-LEATHER alone is not enough and got this wrong once: a soft
    keyline pixel like (60,50,45) sits inside a 60-wide box around (99,65,24)
    and reported the collar as being out on the snout tip. Brown is a HUE, so
    test the hue — warm, and clearly warmer than it is blue.
    """
    return (abs(r - LEATHER[0]) < LEATHER_TOL
            and abs(g - LEATHER[1]) < LEATHER_TOL
            and abs(b - LEATHER[2]) < LEATHER_TOL
            and r > g > b and (r - b) > 30)


def _collar_x(img: Image.Image, band) -> int:
    """Rightmost leather column inside a band — the collar, where a trace ends."""
    px = img.load()
    w, _ = img.size
    top, bot = band
    best = None
    for x in range(w - 1, -1, -1):
        for y in range(top, bot + 1):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            if _is_leather(r, g, b):
                best = x
                break
        if best is not None:
            break
    return best if best is not None else w // 2


def main() -> None:
    raw = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        HERE, "art", "raw", "sled_east_raw_v2.png")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        HERE, "art", "eopie_pair_gen_east_v2.png")
    # A relative path is resolved against the CWD first and only then against
    # this file's directory, so `Source/art/...` from the mod root and
    # `art/...` from Source/ both work. Joining HERE unconditionally produced
    # `Source/Source/art/...` and a confusing chroma_key failure.
    def _resolve(p):
        if os.path.isabs(p) or os.path.exists(p):
            return os.path.abspath(p)
        return os.path.join(HERE, p)

    raw, out = _resolve(raw), _resolve(out)

    keyed = _keyed(raw)
    bbox = keyed.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    print(f"raw {keyed.size}  subject bbox {bbox}")
    # ⚠️ The subject bbox is NOT the crop. The two traces run off the raw's left
    # edge, so the bbox always starts at x=0 and would drag ~460 px of rope into
    # the pair — which the build script then scales down along with the animals
    # and draws its own traces over. The first cut dropped them (raw x 462-1334
    # = the committed 873 px exactly); this reproduces that by cutting at the
    # first column thick enough to be a body rather than a rope.
    left = _body_left(keyed)
    bbox = (left, bbox[1], bbox[2], bbox[3])
    print(f"body-only crop box {bbox}  (dropped {left} px of trace)")
    crop = keyed.crop(bbox)
    crop.save(out)
    w, h = crop.size
    print(f"wrote {os.path.normpath(out)}  {w}x{h}  aspect {w / h:.4f}")

    bands = _animal_bands(crop)
    print(f"animal bands (rows): {bands}")
    if len(bands) != 2:
        print("⚠️  expected exactly 2 animals; check the image before pasting")
    fracs = tuple(round(((t + b) / 2) / h, 4) for t, b in bands)
    print(f"ANIMAL_CY_FRACS = {fracs}")

    collars = [_collar_x(crop, b) for b in bands]
    print(f"collar columns: {collars}")
    print(f"ATTACH_X_FRAC = {round(sum(collars) / len(collars) / w, 4)}")


if __name__ == "__main__":
    main()
