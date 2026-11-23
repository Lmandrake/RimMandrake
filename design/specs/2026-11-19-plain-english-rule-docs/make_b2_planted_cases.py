#!/usr/bin/env python3
"""make_b2_planted_cases.py - how the three B2 ("grey mud") planted pictures of the art judge calibration were made.

Item RIMMANDRAKE_ANSWER_SEVEN_TERMS_NO_SOURCE_DEFINES_GREY_MUD. Each card is the owner-picked RM_DecayDrake r2 (three
facings), altered offline by this script. No art is generated. The cards go beside the source card in the run dir that
src/RimMandrake/rimflow/art_calibration.json names; that file pins every picture by sha256. The card names p1, p2, p3 tell the judge nothing.

  p1  blends into the ground: hue and value moved to the panel's ground colour, shapes kept (contrast x0.28)
  p2  dull with no clear shapes: grey, darker than the ground, interior blurred and flattened, small parts rounded off
  p3  plain but legible: nearly grey, darker than the ground, every shape kept (contrast x0.65, so no edge turns black)

    python3 make_b2_planted_cases.py <out_dir>     writes <out_dir>/RM_DecayDrake__p1..p3, prints the sha256 pins
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
sys.path.insert(0, str(REPO / "src/RimMandrake/rimflow"))
import scale_panel as SP  # noqa: E402
import art_calibration as AC  # noqa: E402

GROUND = np.array(SP.DEFAULT_TERRAIN[:3], float)
W = np.array([0.299, 0.587, 0.114])


def load(p):
    a = np.asarray(Image.open(p).convert("RGBA"), float)
    return a[..., :3], a[..., 3]


def save(rgb, al, p):
    a = np.dstack([np.clip(rgb, 0, 255), np.clip(al, 0, 255)]).round().astype("uint8")
    a[a[..., 3] == 0] = 0
    Image.fromarray(a, "RGBA").save(p)


def blur(x, r):
    return np.asarray(Image.fromarray(np.clip(x, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(r)), float)


def stats(rgb, al):
    lum = rgb @ W
    m = al > 128
    return lum, lum[m].mean(), m


def blend(rgb, al):
    lum, mean, _m = stats(rgb, al)
    chroma = (rgb - lum[..., None]) * 0.12                 # a trace of the old hue, so it stays a painted picture
    return GROUND + ((lum - mean) * 0.28)[..., None] + chroma, al


def dull(rgb, al):
    lum, mean, _m = stats(rgb, al)
    w = blur(al, 11)
    soft = blur(lum * al / 255, 11) / np.maximum(w, 1) * 255   # blurred inside the silhouette only
    flat = 78 + (soft - mean) * 0.12 + (lum - mean) * 0.05
    sm = blur(al, 7)
    al2 = np.clip((sm - 110) * 12, 0, 255)                 # spines, claws and wing tips rounded off; the edge stays hard
    return flat[..., None] * np.array([1.0, 0.985, 0.96]), al2


def plain(rgb, al):
    lum, mean, _m = stats(rgb, al)
    chroma = (rgb - lum[..., None]) * 0.22
    return (80 + (lum - mean) * 0.65)[..., None] + chroma, al


def main(out):
    src = Path(AC.source_dir()) / "RM_DecayDrake__r2"
    pins = {}
    for name, f in (("p1", blend), ("p2", dull), ("p3", plain)):
        d = Path(out) / ("RM_DecayDrake__" + name)
        d.mkdir(parents=True, exist_ok=True)
        for face in ("south", "east", "north"):
            rgb, al = f(*load(src / (face + ".png")))
            save(rgb, al, d / (face + ".png"))
            _l, mean, _m = stats(rgb, al)
            print(name, face, "body luminance %.0f, ground %.0f" % (mean, GROUND @ W), file=sys.stderr)
        SP.render_panel((d / "east.png").read_bytes(), {"kind": "animal", "drawSize": (2.75, 2.75)}, d / "scale.png",
                        d / "scale_full.png")
        (d / "scale_full.png").unlink()
        card = json.loads((src / "card.json").read_text())
        card = {k: card[k] for k in AC.FACT_KEYS if k in card}
        card["candidate"] = name
        card["provenance"] = "made by design/specs/2026-11-19-plain-english-rule-docs/make_b2_planted_cases.py"
        (d / "card.json").write_text(json.dumps(card, indent=1))
        pins[d.name] = {x + ".png": hashlib.sha256((d / (x + ".png")).read_bytes()).hexdigest()
                        for x in ("south", "east", "north", "scale")}
    print(json.dumps(pins, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
