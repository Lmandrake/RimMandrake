"""wire_pole_art.py -- per-look power pole art into MessyConduit (owner review 2026-10-04 B6/B16/B19, v2 stout poles).

    python3 src/RimMandrake/Utils/mockups/messy_conduit/wire_pole_art.py            # wire every v2 render, regen table
    python3 src/RimMandrake/Utils/mockups/messy_conduit/wire_pole_art.py --check    # exit 1 if wired art / table is stale

Artpipe jobs messyconduit_{mast,lampmast}_{scrapper,industrial,modern,futuristic}_v2 render a 256x512 transparent pole,
base at the bottom, drawn by the defs at drawSize (2,4) with drawOffset (0,0,1.5): 128 px per cell, pixel row r (0 = top)
sits at z = 3.5 - r/128 cells above the cell centre, column 128 is the cell centre. For each render this
  * copies it unchanged to Textures/RimMandrake/MessyConduit/Aerial/Styles/<Look>/<AerialMast|AerialLampMast>.png,
  * CROPS its top 128 rows into <...>Top.png (256x128, the overlay drawn above pawns; same pixels so alignment is exact;
    the code draws it 2x1 cells centred at topOffsetZ = 3.5 - 64/128 = 3.0),
  * MEASURES the insulator tips: topmost opaque row inside the two outer-insulator column bands (10-30% and 70-90% of
    the width), averaged -> attachZ = 3.5 - row/128,
  * regenerates Source/Aerial/PoleGeometryTable.cs. --check recomputes everything from the wired PNGs (state, not eyes):
    size, crop identical to the mast's top rows, table identical.
"""
import glob
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
MOD = os.path.join(REPO, "src", "RimMandrake", "MessyConduit")
STY = os.path.join(MOD, "Textures", "RimMandrake", "MessyConduit", "Aerial", "Styles")
TABLE = os.path.join(MOD, "Source", "Aerial", "PoleGeometryTable.cs")
ARTPIPE = "/mnt/d/Luke/dev/_artpipe"
LOOKS = {"scrapper": "Scrapper", "industrial": "Industrial", "modern": "Modern", "futuristic": "Futuristic"}
KINDS = {"mast": ("AerialMast", "RM_AerialMast"), "lampmast": ("AerialLampMast", "RM_AerialLampMast")}
W, H = 256, 512


def find_render(job):
    """The PNG of a done job (done/<job>.manifest.json present): _artsrc/<job>/<job>.png, the daemon's output."""
    for p in (os.path.join(ARTPIPE, "done", job + ".json"),):
        if os.path.exists(p):
            try:
                d = json.load(open(p, encoding="utf-8"))
            except Exception:
                d = {}
            for k in ("output", "out", "png", "result", "final", "path"):
                v = d.get(k)
                if isinstance(v, str) and v.lower().endswith(".png"):
                    v = v.replace("D:\\", "/mnt/d/").replace("\\", "/")
                    if os.path.exists(v):
                        return v
    if not os.path.exists(os.path.join(ARTPIPE, "done", job + ".manifest.json")):
        return None                       # not finished (pending/ or running): never wire a half-written file
    hits = sorted(glob.glob(os.path.join(ARTPIPE, "_artsrc", job, job + ".png")) + glob.glob(os.path.join(ARTPIPE, "_artsrc", job + "*.png")))
    return hits[-1] if hits else None


def fit(im):
    """Renders come back with the pole drawn small in the tall canvas (the generator works square, then fits). Crop to
    the alpha bbox and scale UNIFORMLY to fill the 128x512 canvas (2 px side margin), base on the bottom row, centred.
    Returns (fitted image, scale, fitted height px)."""
    bb = im.getchannel("A").getbbox()
    if bb is None:
        return im, 1.0, 0
    c = im.crop(bb)
    k = min((W - 4) / float(c.size[0]), (H - 2) / float(c.size[1]))
    c = c.resize((max(1, int(round(c.size[0] * k))), max(1, int(round(c.size[1] * k)))), Image.LANCZOS)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(c, ((W - c.size[0]) // 2, H - c.size[1]))
    return out, k, c.size[1]


def measure(im):
    """Insulator tip row: mean over the two outer-insulator bands of the first row holding opaque pixels."""
    a = im.getchannel("A")
    tops = []
    for lo, hi in ((0.10, 0.30), (0.70, 0.90)):
        x0, x1 = int(W * lo), int(W * hi)
        for r in range(int(H * 0.5)):
            if any(a.getpixel((x, r)) > 128 for x in range(x0, x1)):
                tops.append(r)
                break
    if len(tops) != 2:
        raise ValueError("no insulator found in both outer bands")
    return sum(tops) / 2.0, tops


# insulator tips the band rule cannot see, read by eye on a 4x gridded enlargement (2026-10-04): the Scrapper poles'
# splintered post top stands above their middle insulator, so the middle band's first opaque row is the post, not it
TIP_OVERRIDE = {("Scrapper", "RM_AerialMast", 1): (0.158, 3.172), ("Scrapper", "RM_AerialLampMast", 1): (0.051, 3.305)}


def measure_ins(im):
    """Each insulator's TIP (owner round 2 B23: every span wire ends exactly at an insulator tip). In each third of the
    width: the first opaque row (the tip) and the alpha-weighted centre column of the 20 rows below it. Returned as
    (x, z) cells from the cell centre: x = column/128 - 1 (column 128 = pole centre), z = 3.5 - row/128."""
    a = im.getchannel("A")
    out = []
    for lo, hi in ((0.03, 0.36), (0.36, 0.64), (0.64, 0.97)):
        x0, x1 = int(W * lo), int(W * hi)
        top = next((r for r in range(int(H * 0.5)) if any(a.getpixel((x, r)) > 128 for x in range(x0, x1))), None)
        if top is None:
            raise ValueError("no insulator in band %.2f-%.2f" % (lo, hi))
        wsum = csum = 0
        for r in range(top, top + 20):
            for x in range(x0, x1):
                if a.getpixel((x, r)) > 128:
                    wsum += 1
                    csum += x
        out.append((round((csum / float(wsum) + 0.5) / 128.0 - 1.0, 3), round(3.5 - top / 128.0, 3)))
    return out


def sane(im):
    if im.size != (W, H):
        return "size %s, want %dx%d" % (im.size, W, H)
    a = list(im.getchannel("A").getdata())
    frac = sum(1 for v in a if v > 128) / float(len(a))
    if not 0.01 <= frac <= 0.70:
        return "opaque fraction %.2f outside 0.05-0.70 (no real alpha?)" % frac
    return None


def table_src(rows):
    body = "\n".join('            d["%s/%s"] = new Vector2(%.3ff, %.3ff);   // insulator tip row %.1f of 512' % r[:5] for r in rows)
    ins = "\n".join('            d["%s/%s"] = new[] { %s };' % (r[0], r[1], ", ".join("new Vector2(%.3ff, %.3ff)" % xz for xz in r[5])) for r in rows)
    return '''// GENERATED by src/RimMandrake/Utils/mockups/messy_conduit/wire_pole_art.py -- do not edit by hand.
// Per-look pole geometry measured from each look's own 256x512 render (attachZ, topOffsetZ; cells above the cell centre).
using System.Collections.Generic;
using UnityEngine;

namespace RimMandrake.MessyConduit.Aerial
{
    public static class PoleGeometryTable
    {
        public static Dictionary<string, Vector2> Build()
        {
            var d = new Dictionary<string, Vector2>();
%s
            return d;
        }

        /// <summary>Insulator TIPS on the crossarm, left to right: (x, z) cells from the cell centre (z = height), per look/def.</summary>
        public static Dictionary<string, Vector2[]> Insulators()
        {
            var d = new Dictionary<string, Vector2[]>();
%s
            return d;
        }
    }
}
''' % (body, ins)


def main(argv):
    check = "--check" in argv
    rows, notes = [], []
    stale = False
    for look_k, look in LOOKS.items():
        for kind_k, (base, defn) in KINDS.items():
            dst = os.path.join(STY, look, base + ".png")
            src = None if check else find_render("messyconduit_%s_%s_v2" % (kind_k, look_k))
            if src:
                im = Image.open(src).convert("RGBA")
                why = sane(im)
                if not why:
                    bb = im.getchannel("A").getbbox()
                    if bb is None or bb[3] - bb[1] < 0.9 * H:
                        why = "pole spans %s rows of %d (want >= 90%%)" % (None if bb is None else bb[3] - bb[1], H)
                if why:
                    notes.append("REFUSED %s/%s: %s (%s)" % (look, base, why, src))
                    src = None
                else:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    im.save(dst)
                    im.crop((0, 0, W, 128)).save(os.path.join(STY, look, base + "Top.png"))
            if os.path.exists(dst):
                im = Image.open(dst).convert("RGBA")
                if im.size != (W, H):
                    notes.append("STALE %s/%s: size %s, want %dx%d" % (look, base, im.size, W, H))
                    stale = True
                    continue
                top = os.path.join(STY, look, base + "Top.png")
                if not os.path.exists(top) or list(Image.open(top).convert("RGBA").getdata()) != list(im.crop((0, 0, W, 128)).getdata()):
                    notes.append("STALE %s/%s: Top overlay is not the crop of the mast" % (look, base))
                    stale = True
                row, tops = measure(im)
                ins = [TIP_OVERRIDE.get((look, defn, i), xz) for i, xz in enumerate(measure_ins(im))]
                rows.append((look, defn, 3.5 - row / 128.0, 3.0, row, ins))
                notes.append("%s/%s: insulator tips rows %s -> crossarm row %.1f of 512 -> attachZ %.3f%s" % (look, base, tops, row, 3.5 - row / 128.0, "" if src or check else " (already wired)"))
            else:
                notes.append("%s/%s: no render yet (stand-in tint stays)" % (look, base))
    src = table_src(rows)
    if check:
        cur = open(TABLE, encoding="utf-8").read() if os.path.exists(TABLE) else ""
        print("\n".join(notes))
        print("pole geometry table %s" % ("current" if cur == src and not stale else "STALE"))
        return 0 if cur == src and not stale else 1
    with open(TABLE, "w", encoding="utf-8", newline="\n") as f:
        f.write(src)
    print("\n".join(notes))
    print("wrote %s (%d looks/defs measured)" % (TABLE, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
