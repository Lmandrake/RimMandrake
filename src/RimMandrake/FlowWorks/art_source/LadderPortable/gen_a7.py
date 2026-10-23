"""Option A7 = A6 with the perspective reversed (camera looks down: the raised rim end is closer, so WIDE; the foot on the pit floor is
farther, so NARROW), the foot further into the pit (x=362), the shadow cast only near the foot (growing toward the floor end, none at the
rim end), and a faint matching shadow at north's foot. Owner card 2026-10-22 (D4 exception, west/east; north's faint foot shadow is by
the coordinator's instruction). East = mirror."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
import gen as G
import gen_a2 as A2
import gen_a4 as A4

W = [(6, 128), (6, 272), (362, 238), (362, 164)]


def shade(im, axis, start, span, alpha, shift, blur):
    a = np.array(im.getchannel("A"), float) / 255
    idx = np.arange(384)
    ramp = np.clip((idx - start) / span, 0, 1) ** 1.3
    ramp = ramp[None, :] if axis == "x" else ramp[:, None]
    m = Image.fromarray((a * ramp * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(m.point(lambda v: int(v * alpha)))
    sh = sh.transform(im.size, Image.AFFINE, (1, 0, -shift[0], 0, 1, -shift[1]))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(sh); out.alpha_composite(im)
    return out


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    L = G.upright()
    A2.THICK = 2
    north = shade(A2.facing(L, A4.N), "y", 170, 100, 0.38, (4, 9), 4)
    south = A2.facing(L, A2.QUADS["S"], (0.0, 0.30))
    A2.THICK = 3
    west = shade(A2.facing(L, W), "x", 190, 150, 0.62, (10, 20), 7)
    for f, im in {"north": north, "south": south, "west": west, "east": G.mirror(west)}.items():
        im.save(out / f"optA7_{f}.png")
