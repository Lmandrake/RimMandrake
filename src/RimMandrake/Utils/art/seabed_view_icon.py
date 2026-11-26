#!/usr/bin/env python3
"""seabed_view_icon.py - draws the sea-floor view gizmo icon UI/Commands/RM_ViewSeaFloor (SEABED_LAYER_DESIGN_ITS_OWN_SEA_FLOOR).

A 128 px command icon in the manner of vanilla's UI/Commands/ViewPlanet and ViewOrbit: a disc showing a pale sea surface,
the water column darkening downward, a dark rock floor, and a pale arrow pointing down to the floor. Drawn at 512 px and
downsampled (LANCZOS) so the edges stay clean at gizmo size. Deterministic: no randomness.

    python3 src/RimMandrake/Utils/art/seabed_view_icon.py <out.png>
Install the result through the art ledger only:
    python3 src/RimMandrake/Utils/art/art.py install DivingInteraction UI/Commands/RM_ViewSeaFloor.png --file <out.png> \\
        --reason script:src/RimMandrake/Utils/art/seabed_view_icon.py
"""
import math, sys
from PIL import Image, ImageDraw


def draw(size=128, S=512):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cx = cy = S // 2
    R = 220
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse((cx - R, cy - R, cx + R, cy + R), fill=255)
    body = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    b = ImageDraw.Draw(body)
    for y in range(S):  # water column: pale near the surface, deep navy below
        t = max(0, min(1, (y - (cy - R)) / (2 * R)))
        b.line([(0, y), (S, y)], fill=(int(70 * (1 - t) + 8 * t), int(150 * (1 - t) + 22 * t), int(190 * (1 - t) + 60 * t), 255))
    wave = [(x, cy - 120 + 14 * math.sin(x / 38.0)) for x in range(0, S + 1, 4)]
    b.polygon([(0, 0), (S, 0), (S, wave[-1][1])] + wave[::-1], fill=(150, 205, 225, 255))
    b.line(wave, fill=(235, 245, 250, 255), width=10)
    ridge = [(x, cy + 95 + 28 * math.sin(x / 55.0 + 1.3) + 12 * math.sin(x / 17.0)) for x in range(0, S + 1, 4)]
    b.polygon([(0, S)] + ridge + [(S, S)], fill=(46, 40, 36, 255))
    b.line(ridge, fill=(120, 104, 88, 255), width=8)
    b.rectangle((cx - 18, cy - 70, cx + 18, cy + 20), fill=(240, 236, 220, 255))
    b.polygon([(cx - 58, cy + 10), (cx + 58, cy + 10), (cx, cy + 78)], fill=(240, 236, 220, 255))
    body.putalpha(mask)
    img = Image.alpha_composite(img, body)
    ImageDraw.Draw(img).ellipse((cx - R, cy - R, cx + R, cy + R), outline=(20, 24, 30, 255), width=14)
    return img.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    draw().save(sys.argv[1])
    print("wrote", sys.argv[1])
