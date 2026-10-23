"""Option A6 = A5 with the west lower end reaching well onto the pit floor (foot x=340) and a soft floor shadow attached to the
foot and lower rails (owner card 2026-10-22, "Keep side walls, add a shadow": west/east of the portable ladder only; D4 exception).
Top end still over the rim (x=6). North/south = A5. East = mirror."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
import gen as G
import gen_a2 as A2
import gen_a4 as A4

W = [(6, 164), (6, 238), (340, 276), (340, 124)]


def with_shadow(im):
    a = np.array(im.getchannel("A"), float) / 255
    ramp = np.clip((np.arange(384) - 120) / 140.0, 0, 1)[None, :]          # none at the rim end, full on the lower half
    m = Image.fromarray((a * ramp * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(5))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(m.point(lambda v: int(v * 0.6)))
    sh = sh.transform(im.size, Image.AFFINE, (1, 0, -9, 0, 1, -16))        # shifted down-right, so it hugs the foot
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(sh); out.alpha_composite(im)
    return out


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    L = G.upright()
    A2.THICK = 2
    north = A2.facing(L, A4.N); south = A2.facing(L, A2.QUADS["S"], (0.0, 0.30))
    A2.THICK = 3
    west = with_shadow(A2.facing(L, W))
    for f, im in {"north": north, "south": south, "west": west, "east": G.mirror(west)}.items():
        im.save(out / f"optA6_{f}.png")
