"""wire_tap_clamp_art.py -- the power-tap clamp texture, JAWS ONLY (owner round 3, 2026-10-04).

    python3 src/RimMandrake/Utils/mockups/messy_conduit/wire_tap_clamp_art.py              # install via the art ledger
    python3 src/RimMandrake/Utils/mockups/messy_conduit/wire_tap_clamp_art.py --preview P  # write a preview PNG only

Owner, 2026-10-04 (station 11): the clamp "shows the enemy grid as a solid piece of conduit. That isn't true when this
mod is being used: it will look like the same art. So the bite should just be 'on top of' whatever's being drawn in the
middle of their node there." The only render (artpipe RM_MessyConduit_Jawa_TapClamp, 64 px) draws the jaws biting a grey
length of pipe at its left. This removes that pipe: every low-saturation (grey) pixel left of the jaws' hinge column is
cleared, the copper jaws and the rusted handle stay, then the 64 px render is upscaled to 128 px (Lanczos) as round 2 did.
The jaws' bite line stays at -0.375 of the width (RM_MapComponent_Aerial.TapBiteX), now drawn on the tap node where the
two grids' cables meet.
"""
import colorsys
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "art"))
import artledger  # noqa: E402  the only sanctioned writer into Textures

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
DEST = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "Textures", "RimMandrake", "GimmeSomeSlack", "Aerial", "TapClamp.png")
SRC = "/mnt/d/Luke/dev/_artpipe/_artsrc/RM_MessyConduit_Jawa_TapClamp/RM_MessyConduit_Jawa_TapClamp.png"
PIPE_X = 15          # 64 px render: the pipe spans x 2..14; the jaws' hinge starts right of it
GREY_SAT = 0.28      # saturation below this is pipe steel; the copper jaws are well above it


def _sat(p):
    return colorsys.rgb_to_hsv(p[0] / 255.0, p[1] / 255.0, p[2] / 255.0)[1]


def jaws_only(im):
    """Left of the hinge: rows without copper are pipe and go entirely; rows with the jaws keep only coloured pixels."""
    im = im.convert("RGBA")
    px = im.load()
    # a jaw row carries a RUN of copper (>= 4 px) left of the hinge; rust flecks on the pipe carry one or two
    jaw_rows = [y for y in range(im.height) if sum(1 for x in range(min(PIPE_X, im.width))
                                                   if px[x, y][3] > 128 and _sat(px[x, y]) > 0.45) >= 4]
    lo, hi = (min(jaw_rows), max(jaw_rows)) if jaw_rows else (im.height, -1)
    cleared = 0
    for y in range(im.height):
        for x in range(min(PIPE_X, im.width)):
            if px[x, y][3] == 0:
                continue
            if not (lo <= y <= hi) or _sat(px[x, y]) < GREY_SAT:
                px[x, y] = (0, 0, 0, 0)
                cleared += 1
    return im, cleared


def main(argv):
    im, cleared = jaws_only(Image.open(SRC))
    out = im.resize((128, 128), Image.LANCZOS)
    out.putdata([p if p[3] > 8 else (0, 0, 0, 0) for p in list(out.getdata())])
    if "--preview" in argv:
        bg = Image.new("RGBA", out.size, (120, 90, 60, 255))
        bg.alpha_composite(out)
        bg.resize((512, 512), Image.NEAREST).save(argv[argv.index("--preview") + 1])
        print("preview: cleared %d pipe pixels" % cleared)
        return 0
    r = artledger.install_image(DEST, out, reason="script:src/RimMandrake/Utils/mockups/messy_conduit/wire_tap_clamp_art.py")
    print("cleared %d pipe pixels; %s" % (cleared, r.get("status")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
