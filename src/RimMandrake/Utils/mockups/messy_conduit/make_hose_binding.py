"""make_hose_binding.py -- the hose-end binding wrap and the plain open mouth (owner review 2026-10-04 B22).

    python3 src/RimMandrake/Utils/mockups/messy_conduit/make_hose_binding.py

Owner: *"you're going to need to make a binding material at the beginnig and end that looks good for any hose type
within, perhaps as though it were wrapped with dense cloth many times like a mummy and wider than the pipe so that it
can explain the width difference gracefully."* Writes into Textures/.../Hose/:
  * Binding.png -- the cloth wrap ALONE, cropped from the accepted artpipe render messyconduit_hose_binding_v1
    (128x64: hose enters at -X, wrap columns 22-103, fitting at +X). The render's own black hose and fitting are cut
    away (the hose and fitting drawn beside it are the game's own), leaving the wrap, 82x40, wrap axis along +X.
  * Mouth.png -- the plain dark open mouth of an open free end (replaces the pale rough OpenEnd stub): a 64x64 ellipse,
    a darkened rim round a near-black bore; drawn hose-width across, squashed along the hose.
  * Coupling_Bare.png / EndCap_Bare.png / Nozzle_Bare.png -- the fittings with their painted hose stub cut away
    (alpha 0 left of the brass, BARE_FROM columns of 128): the wrap covers the join, and the stub otherwise showed
    as a rust patch beyond the wrap on a plump hose (live review round 2). The originals stay for gizmo icons.
RM_MapComponent_Hoses.BindBand is the wrap's widest opaque band of Binding.png's height; validation.py O6 re-measures it.
"""
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
H = os.path.join(HERE, "..", "..", "..", "MessyConduit", "Textures", "RimMandrake", "MessyConduit", "Hose")
SRC = "/mnt/d/Luke/dev/_artpipe/_artsrc/messyconduit_hose_binding_v1/messyconduit_hose_binding_v1.png"
X0, X1, Y0, Y1 = 22, 104, 12, 52
BARE_FROM = {"Coupling_Brass": 58, "EndCap": 44, "Nozzle": 42}   # first brass column, judged on a 3x enlargement


def binding():
    im = Image.open(SRC).convert("RGBA").crop((X0, Y0, X1, Y1))
    px = im.load()
    w, h = im.size
    for x in range(w):
        for y in range(h):
            r, g, b, a = px[x, y]
            if (x <= 3 or x >= w - 6) and (r + g + b) / 3 < 70:       # the render's own black hose / fitting at the edges
                px[x, y] = (r, g, b, 0)
    im.save(os.path.join(H, "Binding.png"))
    return im


def mouth():
    s = 4
    c = Image.new("RGBA", (64 * s, 64 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.ellipse((2 * s, 2 * s, 62 * s, 62 * s), fill=(46, 40, 35, 255))
    d.ellipse((12 * s, 9 * s, 52 * s, 55 * s), fill=(12, 10, 9, 255))
    c = c.filter(ImageFilter.GaussianBlur(s * 0.6)).resize((64, 64), Image.LANCZOS)
    c.save(os.path.join(H, "Mouth.png"))
    return c


def bare():
    for n, x0 in BARE_FROM.items():
        im = Image.open(os.path.join(H, n + ".png")).convert("RGBA")
        px = im.load()
        for x in range(x0):
            for y in range(im.size[1]):
                px[x, y] = px[x, y][:3] + (0,)
        im.save(os.path.join(H, n.split("_")[0] + "_Bare.png"))


def main():
    bare()
    b = binding()
    a = b.getchannel("A")
    band = max(sum(1 for y in range(b.size[1]) if a.getpixel((x, y)) > 128) for x in range(b.size[0]))
    mouth()
    print("wrote Binding.png %dx%d (widest band %d px) and Mouth.png 64x64" % (b.size[0], b.size[1], band))


if __name__ == "__main__":
    main()
