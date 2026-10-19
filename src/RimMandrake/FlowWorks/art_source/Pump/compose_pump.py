"""Compose RM_LiquidPump.png (512x512, 4-fold symmetric ports) from two generator renders.

raw/pump_v1.png  -> the square housing + motor cap (kept as drawn, top-left light)
raw/pump_v2.png  -> the top port (spigot + bolted flange), an edit of v1 with wider bores
The top port is reused for all four sides: bottom = vertical flip, left = transpose,
right = mirror of left, so the highlight stays on the top/left of every spigot.
Geometry (final canvas): housing 300 px square, flange outer face 232 px from centre,
spigot bore ~118 px (= the rigid pipe's 0.23 cell). Corners and the 24 px band between
each flange and the canvas edge are alpha 0, so pipes drawn under the pump show there.
Run: python3 compose_pump.py  (writes ./RM_LiquidPump.png; then art.py install ... --file it)
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "RM_LiquidPump.png")  # installed with: art.py install --file
CANVAS, C = 512, 256
HOUSING = 300
FACE = 232          # centre -> flange outer face
NECK_CUT = (200, 228)  # v2 rows dropped from the spigot neck to shorten the port


def clean(im):
    a = np.array(im.convert("RGBA"))
    al = a[..., 3].astype(int)
    al[al >= 200] = 255
    al[al < 24] = 0
    a[..., 3] = al
    return Image.fromarray(a)


def main():
    v1 = clean(Image.open(os.path.join(HERE, "raw", "pump_v1.png")))
    v2 = clean(Image.open(os.path.join(HERE, "raw", "pump_v2.png")))

    housing = v1.crop((249, 254, 775, 763)).resize((HOUSING, HOUSING), Image.LANCZOS)

    arm = np.array(v2.crop((340, 50, 684, 276)))  # cols 340..683, rows 50..275
    r0, r1 = NECK_CUT[0] - 50, NECK_CUT[1] - 50
    arm = np.concatenate([arm[:r0], arm[r1:]], axis=0)
    arm = Image.fromarray(arm)
    k = 118 / 272.0  # v2 neck width 272 px -> 118 px bore
    aw, ah = round(arm.width * k), round(arm.height * k)
    arm = arm.resize((aw, ah), Image.LANCZOS)
    # trim the transparent rows above the flange face so the face lands at FACE
    top = np.nonzero(np.array(arm)[..., 3].max(axis=1) > 128)[0][0]
    arm = arm.crop((0, top, aw, ah))
    aw, ah = arm.size

    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    top_arm = arm
    bottom_arm = arm.transpose(Image.FLIP_TOP_BOTTOM)
    left_arm = arm.transpose(Image.TRANSPOSE)
    right_arm = left_arm.transpose(Image.FLIP_LEFT_RIGHT)
    canvas.alpha_composite(top_arm, (C - aw // 2, C - FACE))
    canvas.alpha_composite(bottom_arm, (C - aw // 2, C + FACE - ah))
    canvas.alpha_composite(left_arm, (C - FACE, C - aw // 2))
    canvas.alpha_composite(right_arm, (C + FACE - ah, C - aw // 2))
    canvas.alpha_composite(housing, (C - HOUSING // 2, C - HOUSING // 2))

    a = np.array(canvas)
    al = a[..., 3]
    al[al < 24] = 0
    a[..., 3] = al
    Image.fromarray(a).save(OUT)
    print("wrote", os.path.normpath(OUT), "arm", aw, "x", ah)


if __name__ == "__main__":
    main()
