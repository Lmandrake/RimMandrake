#!/usr/bin/env python3
"""Cut the claim-rumour item icon out of its generated frame and size it for RimWorld.

The generator returns a large image on a flat #00ff00 key (this install is
chatgpt-auth, so chroma-key is the only route to alpha). This does three things
and nothing else:

  1. chroma-keys the green via the shared skills/generating-images script,
  2. crops to the subject and pads it square so the icon is centred and cannot
     be stretched by the aspect,
  3. downsamples premultiplied to 128x128 — plain averaging on a cutout drags
     the transparent black outside the keyline into the rim and darkens it.

⚠️ 128 is the ITEM convention, not a rule the engine enforces. Vanilla's own
item art is inside AssetBundles and cannot be measured on disk, so this is taken
from the loose modded items in the active stack rather than from Core.

Run:  /home/mandrake/.venvs/art/bin/python Source/build_claim_rumour.py
      (Pillow is not on the system python here; that venv has it.)
"""

import os
import subprocess
import sys
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(MOD, "..", "..", ".."))
CHROMA = os.path.join(REPO, "skills", "generating-images", "scripts",
                      "chroma_key.py")

RAW = os.path.join(HERE, "claim_rumour_raw.png")
OUT = os.path.join(MOD, "Textures", "Things", "Item", "Special",
                   "JawaClaimRumour.png")
SIZE = 128
MARGIN = 4          # px of clear canvas at 128, so the icon does not touch the edge


def premultiplied_resize(img: Image.Image, w: int, h: int) -> Image.Image:
    pm = Image.new("RGBA", img.size)
    src, dst = img.load(), pm.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = src[x, y]
            f = a / 255.0
            dst[x, y] = (int(r * f), int(g * f), int(b * f), a)
    pm = pm.resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", pm.size)
    s, o = pm.load(), out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = s[x, y]
            if a == 0:
                o[x, y] = (0, 0, 0, 0)
            else:
                f = 255.0 / a
                o[x, y] = (min(255, int(r * f)), min(255, int(g * f)),
                           min(255, int(b * f)), a)
    return out


def main() -> None:
    tmp = os.path.join(tempfile.gettempdir(), "claim_rumour_keyed.png")
    subprocess.run([sys.executable, CHROMA, "--input", RAW, "--out", tmp],
                   check=True)
    keyed = Image.open(tmp).convert("RGBA")

    bbox = keyed.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    subject = keyed.crop(bbox)
    print(f"raw {keyed.size}  subject {subject.size} at {bbox[:2]}")

    side = max(subject.size)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.alpha_composite(subject, ((side - subject.width) // 2,
                                     (side - subject.height) // 2))

    inner = SIZE - MARGIN * 2
    icon = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    icon.alpha_composite(premultiplied_resize(square, inner, inner),
                         (MARGIN, MARGIN))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    icon.save(OUT)
    a = icon.getchannel("A")
    print(f"wrote {os.path.normpath(OUT)}  {icon.size}  bbox {a.getbbox()}  "
          f"alpha max {max(a.getdata())}  corners "
          f"{[icon.getpixel(p)[3] for p in ((0,0),(SIZE-1,0),(0,SIZE-1),(SIZE-1,SIZE-1))]}")


if __name__ == "__main__":
    main()
