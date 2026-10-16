"""mock.py -- the laid hose joined to the reel's outlet, composited offline at the code's own geometry.

Everything in reel-art pixels (256 px = drawSize 2.8 cells -> 91.4 px/cell), the reel's art centred on its 2x2 footprint:
  * hose strand (Strand_Flat), mesh width MeshWidthFlat(0.465) = 0.504 cells, from the far left to Mouth (u 38.4, v 135);
  * end coupling (Coupling_Bare, as drawn, face pointing into the reel) size FittingSize(0.465) = 1.13 cells, centred
    NozzleTip + NozzleSeat - JoinerFace*size = u -32.1, v 135 (RM_MapComponent_Hoses.cs:746 Fitting);
  * its binding wrap (Binding) 0.6 x 0.636 cells centred u -58;
  * the reel sprite on top (the coupling's threaded stub slides under it).
    python3 mock.py <reel png> <look> <out png> [--scale 2]
"""
import os
import sys

from PIL import Image

H = os.path.dirname(os.path.abspath(__file__))
T = H + "/../../src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/"
SUB = {"Scrapper": "", "Industrial": "Styles/Industrial/", "Modern": "Styles/Modern/", "Futuristic": "Styles/Futuristic/"}
PX = 256 / 2.8
VIS = 0.465
SIZE = min(VIS / 0.25, 0.95 * 1.3 * VIS / 0.508)
TIP, SEAT, JF, MV, MOUTH_U = 9, 0.07, 0.46, 135, 128 - 0.98 * PX
LEFT = 230                      # px of ground left of the reel canvas


def put(canvas, im, cx, cy, w, h):
    im = im.resize((max(1, round(w)), max(1, round(h))), Image.LANCZOS)
    canvas.alpha_composite(im, (round(cx - w / 2) + LEFT, round(cy - h / 2) + 20))


def main(reel, look, out, scale=2):
    c = Image.new("RGBA", (LEFT + 256, 256 + 40), (128, 100, 70, 255))
    strand = Image.open(T + SUB[look] + "Strand_Flat.png").convert("RGBA")
    sw = 0.465 / (59 / 64) * PX
    seg = strand.resize((round(strand.width * sw / strand.height), round(sw)), Image.LANCZOS)
    x = -LEFT
    while x < MOUTH_U:
        w = min(seg.width, MOUTH_U - x)
        c.alpha_composite(seg.crop((0, 0, round(w), seg.height)), (round(x) + LEFT, round(MV - sw / 2) + 20))
        x += seg.width
    end = TIP + SEAT * PX
    cc = end - JF * SIZE * PX
    put(c, Image.open(T + SUB[look] + "Coupling_Bare.png").convert("RGBA"), cc, MV, SIZE * PX, SIZE * PX)
    brass = cc - 0.03 * SIZE * PX
    put(c, Image.open(T + SUB[look] + "Binding.png").convert("RGBA"), brass + (0.05 - 0.3) * PX, MV, 0.6 * PX,
        1.3 * VIS / 0.95 * PX)
    c.alpha_composite(Image.open(reel).convert("RGBA"), (LEFT, 20))
    c.resize((c.width * scale, c.height * scale), Image.NEAREST).save(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[5]) if len(sys.argv) > 5 else 2)
