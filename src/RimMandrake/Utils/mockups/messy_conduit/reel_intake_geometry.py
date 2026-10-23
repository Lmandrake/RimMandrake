#!/usr/bin/env python3
"""Measure where a relay hose meets the 2x2 hose reel's drawn outline, per look and per art (stored / deployed), and
write src/RimMandrake/FlowWorks/Source/Hose/ReelIntakeGeometry.cs (the hose moved to FlowWorks at the hose port) (Verse-free, selftested).

Owner, station 42 (2026-10-04): "pipe does NOT hook up properly to the next reel station". The round-6 hose ended on the
midpoint of the intake cell's shared edge, which on the west side is 0.45 cell below the art's one brass inlet and 0.29
cell inside its face, and on the north/south sides leaves bare ground between the edge and the drawn reel.

Rule measured here (alpha > 128, the reel drawn at the defs' drawSize centred on the footprint, any square canvas):
  * WEST: the art's one outlet/inlet nozzle (rows whose leftmost opaque pixel is within NOZZLE_PX of the leftmost opaque
    column): the hose's coupling face meets the nozzle face, both west intake cells go to it, and a laid hose leaves the
    deployed art's nozzle there (outlet table: tip dx, tip dz). HOSE_ENDS_FIX_MISSES_THE_PORTS (2026-10-21): the old rule
    (u < 20, drawSize 2.8 hard-coded) silently described the 10-05 art after 2e22f30e3c / 2c27b49569 replaced it.
  * EAST / NORTH / SOUTH, per edge cell: along that cell's half of the edge (cell centre +-0.45, 0.05..0.8 from the edge's middle), the line where the drawn
    outline lies closest to the footprint edge (median of a +-0.12-cell band, so a one-pixel spur cannot win); ties go to
    the cell centre. The hose's coupling face meets the outline there.
Depth = outline position minus the footprint edge along the outward normal (cells; + = outside the edge).

REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED (owner card 2026-10-22, "install all 16"): north and south have pictures of their own
(Reel_<art>_north / _south beside the west art). Each is measured TURNED INTO THE WEST PICTURE'S FRAME (north rot90 ccw,
south rot90 cw: its outlet on the left), so every table row is in the frame HoseReelRect.ToArt/FromArt already use, and
the C# keeps one set of rules. Frames: 0 = west (east is it mirrored), 1 = north, 2 = south; 8 rows per frame.

Run: python3 src/RimMandrake/Utils/mockups/messy_conduit/reel_intake_geometry.py   (rewrites the .cs; deterministic)
     ... --check   exit 1 when the committed .cs no longer matches the installed art / drawSize (FlowWorks/selftest_hose_ports.py)
     ... --out P   write the generated .cs to P instead
     ... --tex D   measure candidate art under D (laid out like Textures/.../Hose) instead of the installed art
"""
import os
import re
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
MOD = os.path.join(REPO, "src", "RimMandrake", "FlowWorks")
TEX = os.path.join(MOD, "Textures", "RimMandrake", "FlowWorks", "Hose")
OUT = os.path.join(MOD, "Source", "Hose", "ReelIntakeGeometry.cs")
LOOKS = [("Scrapper", ""), ("Industrial", "Styles/Industrial/"), ("Modern", "Styles/Modern/"), ("Futuristic", "Styles/Futuristic/")]
ARTS = ["Reel_PumpHookup", "Reel_Deployed"]   # index 0 = stored (hose reeled in), 1 = deployed (hose laid)
FRAMES = [("", 0, "west"), ("_north", 1, "north"), ("_south", -1, "south")]   # file suffix, np.rot90 k into the west frame
DEFS = [os.path.join(MOD, "Defs", "Hose", "RM_HoseReel.xml"), os.path.join(MOD, "Defs", "Hose", "RM_HoseReelStyles.xml")]
NOZZLE_PX = 6
BAND = 0.12


def draw_size():
    """The one reel drawSize every reel def and style uses (the C# assumes one); refuses when they disagree."""
    vals = set()
    for p in DEFS:
        vals.update(float(m.group(1)) for m in re.finditer(r"<drawSize>\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\)</drawSize>", open(p).read()))
    if len(vals) != 1:
        raise SystemExit("reel drawSize is not one value across %s: %s" % (DEFS, sorted(vals)))
    return vals.pop()


DRAW = draw_size()


def outline(a, side, perp):
    """Outline coordinate (cells from the footprint centre along the outward normal) on the line at `perp`."""
    n = a.shape[0]
    px = int(round(BAND / DRAW * n))
    hits = []
    for b in range(-px, px + 1):
        if side in "EW":
            v = int(round(n / 2 - perp / DRAW * n)) + b
            idx = np.nonzero(a[v])[0]
            if not len(idx):
                continue
            hits.append(((idx[-1] + 1) - n / 2) / n * DRAW if side == "E" else (n / 2 - idx[0]) / n * DRAW)
        else:
            u = int(round(n / 2 + perp / DRAW * n)) + b
            idx = np.nonzero(a[:, u])[0]
            if not len(idx):
                continue
            hits.append((n / 2 - idx[0]) / n * DRAW if side == "N" else ((idx[-1] + 1) - n / 2) / n * DRAW)
    return float(np.median(hits)) if hits else None


def measure(path, k=0):
    a = np.rot90(np.array(Image.open(path).convert("RGBA"))[..., 3] > 128, k)
    n = a.shape[0]
    umin = min(np.nonzero(a[v])[0][0] for v in range(n) if a[v].any())
    rows = [v for v in range(n) if a[v].any() and np.nonzero(a[v])[0][0] <= umin + NOZZLE_PX]
    vc = (rows[0] + rows[-1]) / 2.0
    face = float(np.median([np.nonzero(a[v])[0][0] for v in rows]))
    inlet = ((n / 2 - vc) / n * DRAW, (n / 2 - face) / n * DRAW - 1.0)   # (perp dz, depth beyond the west edge)
    tip = ((umin / n - 0.5) * DRAW, inlet[0])   # the nozzle tip (dx, dz) from the footprint centre
    out = {}
    for side in "ENS":
        for ci, centre in enumerate((-0.5, 0.5)):   # edge cell 0 = lower x / z, 1 = higher
            best = None
            steps = int(round(0.45 / DRAW * n))
            for s in range(-steps, steps + 1):
                perp = centre + s / n * DRAW
                if abs(perp) > 0.8 or abs(perp) < 0.05:
                    continue   # keep the coupling (~0.5 wide) off the footprint corner and off the other cell's half
                o = outline(a, side, perp)
                if o is None:
                    continue
                d = o - 1.0
                score = abs(d) + 0.05 * abs(perp - centre)
                if best is None or score < best[0] - 1e-9:
                    best = (score, perp, d)
            out[(side, ci)] = (best[1], best[2])
    return inlet, out, tip


def generate():
    lines, tips = [], []
    for suffix, k, _fname in FRAMES:
        for look, folder in LOOKS:
            for art in ARTS:
                art = art + suffix
                p = os.path.join(TEX, folder + art + ".png")
                if not os.path.exists(p):
                    raise SystemExit("missing reel art %s (every look needs west, north and south pictures)" % p)
                inlet, out, tip = measure(p, k)
                row = [inlet[0], inlet[1]]
                for side in "ENS":
                    for cell in range(2):
                        row += list(out[(side, cell)])
                lines.append("            { " + ", ".join("%.3f" % x for x in row) + " },   // " + look + " " + art)
                tips.append("            { %.3f, %.3f },   // %s %s" % (tip[0], tip[1], look, art))
    cs = '''using System;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// GENERATED by src/RimMandrake/Utils/mockups/messy_conduit/reel_intake_geometry.py from the reel art (all four looks,
    /// stored Reel_PumpHookup and laid Reel_Deployed, drawSize ''' + ('%g' % DRAW) + '''). Do not hand-edit: re-run the script.
    /// Owner, station 42 (2026-10-04): "pipe does NOT hook up properly to the next reel station". Where a relay hose's
    /// coupling face meets the drawn reel, per approach side, in cells from the 2x2 footprint centre:
    /// REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED: rows come in three frames (0 west/east, 1 north, 2 south; 8 rows each); a
    /// north or south picture is measured turned into the west picture's frame (outlet on the left), so callers read every
    /// row in the frame HoseReelRect.ToArt/FromArt use for that facing.
    ///   row = { westInletDz, westInletDepth, E0 perp, E0 depth, E1 perp, E1 depth, N0.., N1.., S0.., S1.. }
    /// perp = offset along the edge from the footprint centre (x for N/S, z for E); depth = outline minus the footprint edge
    /// along the outward normal (+ = outside). West: the art's one brass inlet (both west cells couple to it).
    /// </summary>
    public static class ReelIntakeGeometry
    {
        public static readonly string[] Looks = { "Scrapper", "Industrial", "Modern", "Futuristic" };

        private static readonly double[,] table =
        {
''' + "\n".join(lines) + '''
        };

        public static int LookIndex(string look)
        {
            int i = Array.IndexOf(Looks, look);
            return i < 0 ? 0 : i;
        }

        /// <summary>The picture frame a reel facing (Rot4 int: 0 N, 1 E, 2 S, 3 W) is drawn from: 1 north, 2 south, else 0
        /// (west; east is the west picture mirrored).</summary>
        public static int Frame(int rot) { int r = ((rot % 4) + 4) % 4; return r == 0 ? 1 : r == 2 ? 2 : 0; }

        private static int Row(string look, bool deployed, int rot = 3) => Frame(rot) * RowCount + LookIndex(look) * 2 + (deployed ? 1 : 0);

        /// <summary>The (art-frame) west inlet: (dz from the footprint centre, depth beyond the west edge), for the picture
        /// a reel facing <paramref name="rot"/> shows.</summary>
        public static void WestInlet(string look, bool deployed, out double dz, out double depth, int rot = 3)
        {
            int r = Row(look, deployed, rot);
            dz = table[r, 0];
            depth = table[r, 1];
        }

        /// <summary>side 0 = E, 1 = N, 2 = S; cell 0 = the lower-coordinate edge cell, 1 = the higher.</summary>
        public static void Edge(string look, bool deployed, int side, int cell, out double perp, out double depth, int rot = 3)
        {
            int r = Row(look, deployed, rot), c = 2 + (side * 2 + cell) * 2;
            perp = table[r, c];
            depth = table[r, c + 1];
        }

        /// <summary>Rows per frame (4 looks x stored/laid).</summary>
        public const int RowCount = 8;

        /// <summary>The reel drawSize the tables were measured at (= every reel def's; the generator refuses otherwise).</summary>
        public const double DrawSize = ''' + ('%g' % DRAW) + ''';

        private static readonly double[,] outlet =
        {
''' + "\n".join(tips) + '''
        };

        /// <summary>HOSE_ENDS_FIX_MISSES_THE_PORTS: the drawn nozzle's tip, (dx, dz) cells from the 2x2 footprint centre, for
        /// this look's stored or laid art, in the art frame of the picture facing <paramref name="rot"/> shows. The laid hose's end coupling meets it; the hose leaves it westward.</summary>
        public static void OutletTip(string look, bool deployed, out double dx, out double dz, int rot = 3)
        {
            int r = Row(look, deployed, rot);
            dx = outlet[r, 0];
            dz = outlet[r, 1];
        }
    }
}
'''
    return cs


def main(argv):
    global TEX
    if "--tex" in argv:
        TEX = os.path.abspath(argv[argv.index("--tex") + 1])
    cs = generate()
    if "--check" in argv:
        have = open(OUT, newline="").read()
        if have != cs:
            print("STALE: %s does not match the installed reel art at drawSize %g -- re-run %s" % (OUT, DRAW, os.path.basename(__file__)))
            return 1
        print("OK: reel intake/outlet geometry matches the installed art at drawSize %g" % DRAW)
        return 0
    out = argv[argv.index("--out") + 1] if "--out" in argv else OUT
    with open(out, "w", newline="\n") as f:
        f.write(cs)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
