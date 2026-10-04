"""wire_bracket_art.py -- per-look, per-facing wall bracket art into MessyConduit (owner review 2026-10-04 B7, round 2 T3).

    python3 src/RimMandrake/Utils/mockups/messy_conduit/wire_bracket_art.py            # wire every landed render, regen table
    python3 src/RimMandrake/Utils/mockups/messy_conduit/wire_bracket_art.py --check    # exit 1 if wired art / table is stale

Artpipe jobs messyconduit_bracket_<look>_<v>_<facing> (facing east / north / south) render a 128x128 transparent bracket.
The bracket's rotation points AT its wall (vanilla Placeworker_AttachedToWall) and its graphic is drawn 1x1, 0.9 cell onto
the wall. Which side of a render the PLATE is on (the wall side) was judged by eye per render (PLATE below): the "east"
renders all put the plate on the LEFT, i.e. the wall to the WEST, so the in-game _east texture is the MIRRORED render and
west (the game's own mirror of east) is the render as drawn. For each look with art this
  * writes Textures/RimMandrake/MessyConduit/Aerial/Styles/<Look>/WallBracket_{north,east,south}.png,
  * MEASURES the insulator: the centroid of the opaque pixels within 22 px of the extreme far from the plate,
  * regenerates Source/Aerial/BracketGeometryTable.cs: the insulator's offset from the graphic centre per Look/rotation
    (cells; x east, z north; 128 px per cell), west = east mirrored.
A look missing any facing is not wired at all (it keeps the tinted shared stand-in): never a mixed set.

Round 2 (owner 2026-10-04, station 9: "some are shown as leaning INTO the wall"): the plate MUST be on the wall side of
every in-game facing (north: top, south: bottom, east: right after the mirror). A render whose plate is on the other side
(Scrapper and Futuristic "south" came back plate-TOP) is FLIPPED here so it leans out, never wired as drawn. The table also
records each texture's PLATE EDGE (the plate's extreme toward the wall, cells along the wall normal from the graphic
centre); AerialMath.BracketDrawOffset turns it into the per-look draw offset that puts the plate on the wall's outer edge.
The table is Verse-free (P2) so the SelfTest compiles it and asserts the lean and the offsets for all four facings.
"""
import glob
import os
import sys

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
MOD = os.path.join(REPO, "src", "RimMandrake", "MessyConduit")
STY = os.path.join(MOD, "Textures", "RimMandrake", "MessyConduit", "Aerial", "Styles")
TABLE = os.path.join(MOD, "Source", "Aerial", "BracketGeometryTable.cs")
ARTPIPE = "/mnt/d/Luke/dev/_artpipe"
LOOKS = {"scrapper": "Scrapper", "industrial": "Industrial", "modern": "Modern", "futuristic": "Futuristic"}
FACINGS = ("east", "north", "south")
# plate (wall) side of each render AS DRAWN, judged by eye 2026-10-04 (contact sheet of all landed renders)
PLATE = {("scrapper", "east"): "left", ("scrapper", "north"): "top", ("scrapper", "south"): "top",
         ("industrial", "east"): "left", ("industrial", "north"): "top", ("industrial", "south"): "bottom",
         ("modern", "east"): "left", ("modern", "north"): "bottom", ("modern", "south"): "top",
         ("futuristic", "east"): "left", ("futuristic", "north"): "top", ("futuristic", "south"): "top"}
VERSIONS = ("v2", "v1")          # newest first
# in-game facing -> render facing, where a render came back drawn for the opposite wall (judged by eye 2026-10-04): the
# modern v2 "north" render has its plate at the BOTTOM and its "south" at the TOP, the reverse of the other three looks
SOURCE = {("modern", "north"): "south", ("modern", "south"): "north"}
N = 128


def find_render(look, facing):
    for v in VERSIONS:
        job = "messyconduit_bracket_%s_%s_%s" % (look, v, facing)
        if not os.path.exists(os.path.join(ARTPIPE, "done", job + ".manifest.json")):
            continue
        hits = glob.glob(os.path.join(ARTPIPE, "_artsrc", job, job + ".png"))
        if hits:
            return hits[0]
    return None


def insulator(im, plate):
    """Centroid (px, py) of the opaque pixels within 22 px of the extreme opposite the plate."""
    a = im.getchannel("A")
    pts = [(x, y) for y in range(N) for x in range(N) if a.getpixel((x, y)) > 128]
    if not pts:
        raise ValueError("empty render")
    if plate == "left":
        far = max(p[0] for p in pts); sel = [p for p in pts if p[0] >= far - 22]
    elif plate == "right":
        far = min(p[0] for p in pts); sel = [p for p in pts if p[0] <= far + 22]
    elif plate == "top":
        far = max(p[1] for p in pts); sel = [p for p in pts if p[1] >= far - 22]
    else:
        far = min(p[1] for p in pts); sel = [p for p in pts if p[1] <= far + 22]
    return sum(p[0] for p in sel) / float(len(sel)), sum(p[1] for p in sel) / float(len(sel))


# in-game facing -> the side of the texture the plate must be on (the wall side; the bracket points AT its wall)
WALL_SIDE = {"north": "top", "south": "bottom", "east": "right"}


def plate_edge(im, plate):
    """The plate's extreme toward the wall: cells from the graphic centre along the wall normal (positive = toward it)."""
    bb = im.getchannel("A").point(lambda v: 255 if v > 128 else 0).getbbox()
    x0, y0, x1, y1 = bb
    if plate == "top":
        return round(0.5 - y0 / float(N), 3)
    if plate == "bottom":
        return round(y1 / float(N) - 0.5, 3)
    if plate == "right":
        return round(x1 / float(N) - 0.5, 3)
    return round(0.5 - x0 / float(N), 3)


def cells(px, py):
    return round((px + 0.5) / N - 0.5, 3), round(0.5 - (py + 0.5) / N, 3)


def build(check):
    rows, notes, stale = [], [], False
    for lk, look in LOOKS.items():
        srcs = {f: find_render(lk, SOURCE.get((lk, f), f)) for f in FACINGS}
        have = [f for f in FACINGS if os.path.exists(os.path.join(STY, look, "WallBracket_%s.png" % f))]
        if not check:
            if all(srcs.values()):
                for f, p in srcs.items():
                    im = Image.open(p).convert("RGBA")
                    if im.size != (N, N):
                        notes.append("REFUSED %s %s: size %s" % (look, f, im.size)); break
                    plate = PLATE[(lk, SOURCE.get((lk, f), f))]
                    if f == "east":
                        im = ImageOps.mirror(im)       # render has the wall WEST; in-game east has it EAST
                        plate = {"left": "right", "right": "left"}.get(plate, plate)
                    if plate != WALL_SIDE[f]:          # drawn for the opposite wall: it would lean INTO this one
                        im = ImageOps.flip(im) if f in ("north", "south") else ImageOps.mirror(im)
                        notes.append("%s %s: render plate %s, flipped to %s" % (look, f, plate, WALL_SIDE[f]))
                    os.makedirs(os.path.join(STY, look), exist_ok=True)
                    im.save(os.path.join(STY, look, "WallBracket_%s.png" % f))
                have = list(FACINGS)
            else:
                notes.append("%s: renders missing %s (stays the tinted stand-in)" % (look, [f for f, p in srcs.items() if not p]))
        if len(have) != len(FACINGS):
            if have:
                notes.append("STALE %s: partial facing set %s" % (look, have)); stale = True
            continue
        for f in FACINGS:
            im = Image.open(os.path.join(STY, look, "WallBracket_%s.png" % f)).convert("RGBA")
            plate = WALL_SIDE[f]               # wired textures always carry the plate on the wall side (flipped above)
            x, z = cells(*insulator(im, plate))
            e = plate_edge(im, plate)
            rows.append((look, f.capitalize(), x, z, e))
            if f == "east":
                rows.append((look, "West", -x, z, e))
        notes.append("%s: wired %s" % (look, ", ".join("%s (%.2f,%.2f)" % (r[1], r[2], r[3]) for r in rows if r[0] == look)))
    return rows, notes, stale


def table_src(rows):
    body = "\n".join('            d["%s/%s"] = new P2(%.3f, %.3f);' % r[:4] for r in rows)
    edges = "\n".join('            d["%s/%s"] = %.3f;' % (r[0], r[1], r[4]) for r in rows)
    return '''// GENERATED by src/RimMandrake/Utils/mockups/messy_conduit/wire_bracket_art.py -- do not edit by hand.
// Wall bracket geometry per Look/rotation, measured from each look's own per-facing art (cells; x east, z north). Absent =
// the look has no art of its own yet (tinted stand-in, def attachZ). Verse-free: the SelfTest compiles this file.
using System.Collections.Generic;

namespace RimMandrake.MessyConduit.Aerial
{
    public static class BracketGeometryTable
    {
        /// <summary>The insulator's offset from the graphic centre.</summary>
        public static Dictionary<string, P2> Build()
        {
            var d = new Dictionary<string, P2>();
%s
            return d;
        }

        /// <summary>The plate's extreme toward the wall: cells from the graphic centre along the wall normal (+ = toward it).</summary>
        public static Dictionary<string, double> PlateEdge()
        {
            var d = new Dictionary<string, double>();
%s
            return d;
        }
    }
}
''' % (body, edges)


def main(argv):
    check = "--check" in argv
    rows, notes, stale = build(check)
    src = table_src(rows)
    print("\n".join(notes))
    if check:
        cur = open(TABLE, encoding="utf-8").read() if os.path.exists(TABLE) else ""
        ok = cur == src and not stale
        print("bracket geometry table %s" % ("current" if ok else "STALE"))
        return 0 if ok else 1
    with open(TABLE, "w", encoding="utf-8", newline="\n") as f:
        f.write(src)
    print("wrote %s (%d rows)" % (TABLE, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
