"""Portable ladder E/W/S from GPT image edits (owner 2026-10-24: v5's squeezed east "read as totally flat"; south must be
"only small nubs sticking up", like vanilla wall-hanging souths).

    python3 portable_gpt.py [east_round] [south_round]   # fits gpt/<round>_{east,south}.png onto the 384 rig canvas -> out/

Sources in gpt/ are Codex $imagegen edits: east = seed v5 flat east + kept north ("restore proper 3D"); south = kept
north + a strip of vanilla wall-attachment N/E/S views (TorchWallLamp, WallLamp, Odyssey lights/pumps).
Rig: 384 px canvas, drawSize 1.5 (256 px/cell). East canvas: wall face band x ~262..320, rim x 320; the top pokes past
the rim as the kept north's top pokes past its rim. South canvas: near rim at row 256; nubs stand on it.
"""
import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
GPT, OUT = HERE / "gpt", HERE / "out"
CANVAS = 384
E_RIGHT, E_LEN, E_CY = 378, 120, 257        # top end 58 px past the rim (north pokes 65 past its rim), foot at x 258 on the band (judge c: 252 touched the dark)
S_RIM, S_W, S_CX = 258, 112, 192            # nubs' feet on the near rim; spread ~ the north's stringer span (119)
S_KEEP = 0.5                                # judge round 1: the whole U read as a truncated north; keep the caps only


def _opaque(im, t=40):
    """Crop to pixels with alpha > t and zero the faint haze GPT leaves elsewhere."""
    a = im.getchannel("A").point(lambda v: v if v > t else 0)
    im = im.copy()
    im.putalpha(a)
    return im.crop(a.getbbox())


def _fit(src, width):
    im = _opaque(Image.open(src).convert("RGBA"))
    h = round(im.height * width / im.width)
    return im.resize((width, h), Image.LANCZOS)


def _match(im, ref):
    """Per-channel mean/std transfer from the kept north (judge round 2: GPT's side view was brighter and cleaner)."""
    import numpy as np
    a, r = np.asarray(im, dtype=np.float32).copy(), np.asarray(ref, dtype=np.float32)
    m, mr = a[..., 3] > 200, r[..., 3] > 200
    for c in range(3):
        x, y = a[..., c][m], r[..., c][mr]
        a[..., c][m] = (x - x.mean()) / (x.std() + 1e-6) * y.std() + y.mean()
    return Image.fromarray(a.clip(0, 255).astype("uint8"), "RGBA")


def east(rnd):
    north = Image.open(HERE.parents[2] / "Textures/Things/Building/FlowWorks/Canals/RM_LadderPortable_north.png").convert("RGBA")
    im = _match(_fit(GPT / f"{rnd}_east.png", E_LEN), north)
    out = Image.new("RGBA", (CANVAS, CANVAS))
    out.alpha_composite(im, (E_RIGHT - im.width, E_CY - im.height // 2))
    return out


def south(rnd):
    im = _fit(GPT / f"{rnd}_south.png", S_W)
    im = im.crop((0, 0, im.width, round(im.height * S_KEEP)))      # the near wall hides the rest
    out = Image.new("RGBA", (CANVAS, CANVAS))
    out.alpha_composite(im, (S_CX - im.width // 2, S_RIM - im.height))
    return out


def main():
    erd = sys.argv[1] if len(sys.argv) > 1 else "r4"         # east round
    srd = sys.argv[2] if len(sys.argv) > 2 else "r1"         # south round
    e = east(erd)
    outs = {"east": e, "west": e.transpose(Image.FLIP_LEFT_RIGHT), "south": south(srd)}
    for f, im in outs.items():
        p = OUT / f"RM_LadderPortable_{f}.png"
        im.save(p)
        print(p, im.getbbox())


if __name__ == "__main__":
    main()
