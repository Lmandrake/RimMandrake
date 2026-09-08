"""CereanMane_south - front view of the Cerean mane crest.

Drawn to match the donor's own conventions, all measured from the LIVE bundle art
(Outer Rim - Galactic Diversity, Common/AssetBundles, 1.6 LoadFolders uses Common):
  * canvas 512x512 RGBA
  * pure black keyline, 11 px, measured on CereanMane_north row y=300
  * fill = vertical greyscale gradient, 247 at y=120 -> 181 at y=300
  * registration: in EVERY healthy Cerean pair (Long, Pony, Male/Female head) the
    south shares the north's x-range and TOP edge and is shorter. Mane north is
    bbox (195, 92, 317, 357), so south is pinned to x 195-317, top y 92.
"""
from PIL import Image, ImageDraw

SS = 4                      # supersample
W = H = 512
TARGET = (195, 92, 317, 300)   # x0, y0, x1, y1  (width 122, height 208)
OUTLINE = 11

# Right half of the crest, as (dx, y) offsets from the spire axis, apex first.
# Three notched tiers per side, mirroring the north view's layered silhouette,
# then a bottom edge that sweeps UP to centre - the parting over the brow, the
# same idea as CereanPony_south's arch but narrower.
RIGHT = [(0, 92),
         (34, 152), (23, 161),
         (52, 208), (38, 217),
         (66, 262), (50, 271),
         (60, 300)]
BOTTOM_IN = [(45, 296), (24, 282), (0, 272)]

def build():
    pts = [(256 + dx, y) for dx, y in RIGHT]
    pts += [(256 + dx, y) for dx, y in BOTTOM_IN]
    pts += [(256 - dx, y) for dx, y in reversed(BOTTOM_IN[:-1])]
    pts += [(256 - dx, y) for dx, y in reversed(RIGHT)]
    return pts

def draw():
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    poly = [(x * SS, y * SS) for x, y in build()]
    d.polygon(poly, fill=(255, 255, 255, 255))
    d.line(poly + [poly[0]], fill=(0, 0, 0, 255), width=OUTLINE * SS, joint="curve")
    return big.resize((W, H), Image.LANCZOS)

def apply_gradient(im):
    px = im.load()
    for y in range(H):
        v = max(150, min(255, round(247 - (y - 120) * 0.3667)))
        for x in range(W):
            r, g, b, a = px[x, y]
            if a > 0 and r > 60:        # fill only, never the keyline
                px[x, y] = (v, v, v, a)
    return im

def fit(im, box):
    bb = im.getchannel("A").getbbox()
    crop = im.crop(bb)
    x0, y0, x1, y1 = box
    crop = crop.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(crop, (x0, y0))
    return out

img = fit(apply_gradient(draw()), TARGET)
import sys
img.save(sys.argv[1])
a = img.getchannel("A")
print("bbox", a.getbbox(), "alphaMax", max(a.get_flattened_data()))
n = sum(1 for p in a.get_flattened_data() if p > 8)
print("coverage %.2f%%" % (100 * n / (W * H)))
