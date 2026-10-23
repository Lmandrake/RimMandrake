#!/usr/bin/env python3
"""TANK_FLANGE_FIX_HOVERS_MID_PIPE -- where each tank's DRAWN edge is, per pipe lane, measured from the installed art.

Live 2026-10-22 (map C, C3 north, Transient/pile_2026-10-22/live_fit/fit_C3n_flange_zoom.jpg): a pipe entering the
universal tank from the south drew its joinFittings flange on the FOOTPRINT edge, ~0.46 cell below the tank's drawn skid
(the art's bottom rows are transparent), so the flange hung mid-pipe. Every tank's art leaves a margin on some side (the
tall and cargo tanks on all four), so the flange must sit where the pipe's centre line meets the drawn outline.

This script measures that outline from Textures/RimMandrake/FlowWorks/Tank/<Look>/<Tank>.png (alpha > 128, a 12 px band
round the lane's centre line) at each def's drawSize / drawOffset (read from the defs, style defs included), and
  default : checks Source/Machinery/TankArtEdges.cs is exactly what it would generate (exit 1 if not)
  --write : regenerates Source/Machinery/TankArtEdges.cs
Any art reinstall that moves an outline turns this red until the table is regenerated.

Hose-port fittings are not the tank body (MODERN_TANK_PORT_REDRAW_COUPLER_FLOATS): the Modern tall / IBC / extra-tall art
carries camlock fittings drawn by art_source/TankPorts/modern_port_fittings.py out to the canvas edge on the lane rows, and
their bulkhead nut buries the wall under it, so the installed picture cannot show where a PIPE meets the outline (a naive
measurement reads 0, the canvas edge). For those three this script rebuilds the picture from the fittings script's base
art, requires it to equal the installed PNG pixel for pixel (red if not: the art was reinstalled some other way and the
body under the fittings is UNMEASURED), and measures the outline on that base, i.e. the body without its fittings.

Inset = cells from the footprint edge INWARD (along the step from the pipe into the tank) to the drawn edge, on the
lane's centre line (lane = the pipe cell's index along that side, 0 or 1). Negative = the art overhangs the footprint
(the tall tanks' tops, drawn up over the pipe cell north of them).
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "art_source", "TankPorts"))
import modern_port_fittings  # noqa: E402  (the fittings overlay: which pictures carry one, and their base art)
TEX = os.path.join(HERE, "Textures", "RimMandrake", "FlowWorks", "Tank")
OUT = os.path.join(HERE, "Source", "Machinery", "TankArtEdges.cs")
DEFS = [os.path.join(HERE, "Defs", "LiquidTypes", "ThingDefs", "RM_LiquidTank.xml"),
        os.path.join(HERE, "Defs", "Machinery", "RM_LiquidLogistics.xml")]
STYLES = os.path.join(HERE, "Defs", "LiquidTypes", "ThingDefs", "RM_LiquidTankStyles.xml")
TANKS = ["RM_LiquidTank", "RM_LiquidTankTall", "RM_UniversalCargoTank", "RM_UniversalCargoTankXTall"]
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
SIDES = ["south", "north", "west", "east"]   # the side of the tank the pipe is on
BAND = 6
fails = []


def vec(s):
    return [float(x) for x in s.strip("() ").split(",")]


def graphic(el):
    g = el.find("graphicData")
    ds = vec(g.findtext("drawSize") or "(1,1)")
    off = vec(g.findtext("drawOffset") or "(0,0,0)")
    return ds, off


def read_defs():
    out = {}
    for f in DEFS:
        for d in ET.parse(f).getroot():
            dn = d.findtext("defName")
            if dn in TANKS:
                size = vec(d.findtext("size"))
                out[dn] = (size, graphic(d))
    styles = {}
    for d in ET.parse(STYLES).getroot():
        dn = d.findtext("defName") or ""
        if "_" in dn:
            styles[dn] = graphic(d)
    return out, styles


def body_alpha(tank, look):
    """Opaque mask of the tank BODY: the installed picture, or, where the fittings overlay drew hose ports on it, its base."""
    installed = Image.open(os.path.join(TEX, look, tank + ".png")).convert("RGBA")
    if look != "Modern" or tank not in modern_port_fittings.TANKS:
        return np.array(installed)[..., 3] > 128
    base = modern_port_fittings.base_image(tank)
    if np.array_equal(np.array(base.convert("RGBA")), np.array(installed)):
        # 2026-10-23 owner ruling (couplers drawn UNDER the fixture): the painted fittings came off, the base is installed
        return np.array(installed)[..., 3] > 128
    rebuilt, _ = modern_port_fittings.build(tank)
    if not np.array_equal(np.array(rebuilt), np.array(installed)):
        fails.append("%s Modern: the installed art is not modern_port_fittings.py's base + fittings, so the body outline under "
                     "the hose fittings is UNMEASURED (re-derive the base for the new art)" % tank)
        return np.array(installed)[..., 3] > 128
    return np.array(base)[..., 3] > 128


def measure(tank, look, size, ds, off):
    a = body_alpha(tank, look)
    h, w = a.shape
    ppx, ppz = w / ds[0], h / ds[1]
    fw, fh = int(size[0]), int(size[1])
    # art rectangle in footprint-local cells (footprint min corner = 0,0)
    ax0 = fw / 2.0 - ds[0] / 2.0 + off[0]
    az0 = fh / 2.0 - ds[1] / 2.0 + off[2]
    res = {}
    for lane in range(fw):   # south / north: a column
        c = int(round((lane + 0.5 - ax0) * ppx))
        rows = np.nonzero(a[:, max(0, c - BAND):c + BAND].any(axis=1))[0]
        bottom = az0 + (h - 1 - rows[-1]) / ppz   # world z of the drawn bottom edge (the lowest opaque pixel's underside)
        top = az0 + (h - rows[0]) / ppz           # world z of the drawn top edge
        res[("south", lane)] = bottom
        res[("north", lane)] = fh - top
    for lane in range(fh):   # west / east: a row
        r = int(round(h - (lane + 0.5 - az0) * ppz))
        cols = np.nonzero(a[max(0, r - BAND):r + BAND, :].any(axis=0))[0]
        res[("west", lane)] = ax0 + cols[0] / ppx
        res[("east", lane)] = fw - (ax0 + (cols[-1] + 1) / ppx)
    return res


def generate():
    defs, styles = read_defs()
    rows = []
    for tank in TANKS:
        size, (ds, off) = defs[tank]
        for look in LOOKS:
            sds, soff = styles.get(tank + "_" + look, (ds, off))
            if sds != ds or soff != off:
                fails.append("%s_%s: style drawSize/drawOffset %s/%s differ from the def's %s/%s" % (tank, look, sds, soff, ds, off))
            m = measure(tank, look, size, sds, soff)
            vals = []
            for side in SIDES:
                for lane in range(2):
                    vals.append(m[(side, lane)])
            rows.append((tank, look, vals))
    lines = []
    lines.append("// GENERATED by FlowWorks/selftest_tank_art_edges.py --write from the installed tank art; do not edit by hand.")
    lines.append("// Verse-free (the SelfTest compiles this file). TANK_FLANGE_FIX_HOVERS_MID_PIPE.")
    lines.append("using System;")
    lines.append("")
    lines.append("namespace RimMandrake.FlowWorks.Machinery")
    lines.append("{")
    lines.append("    /// <summary>Where each tank's DRAWN outline meets a pipe's centre line, per look, side and lane: cells from the footprint")
    lines.append("    /// edge inward (negative = the art overhangs the footprint). Measured from Textures/RimMandrake/FlowWorks/Tank (alpha &gt; 128)")
    lines.append("    /// at each def's drawSize/drawOffset; FlowWorks/selftest_tank_art_edges.py pins it to the art.</summary>")
    lines.append("    public static class TankArtEdges")
    lines.append("    {")
    lines.append("        public static readonly string[] Tanks = { %s };" % ", ".join('"%s"' % t for t in TANKS))
    lines.append("        public static readonly string[] Looks = { %s };" % ", ".join('"%s"' % l for l in LOOKS))
    lines.append("        /// <summary>[tank][look] -> south lane 0, 1; north 0, 1; west 0, 1; east 0, 1 (a lane = the pipe cell's index along the side).</summary>")
    lines.append("        private static readonly double[][] Table =")
    lines.append("        {")
    for tank, look, vals in rows:
        lines.append("            new[] { %s },   // %s %s" % (", ".join("%.3f" % v for v in vals), tank, look))
    lines.append("        };")
    lines.append("")
    lines.append("        /// <summary>The drawn edge's inset for a pipe on the side the unit step (sx, sz) (pipe -> tank) enters, on lane")
    lines.append("        /// <paramref name=\"lane\"/>; false = not a measured tank (keep the footprint edge).</summary>")
    lines.append("        public static bool TryInset(string tankDef, string look, int sx, int sz, int lane, out double inset)")
    lines.append("        {")
    lines.append("            inset = 0;")
    lines.append("            int t = Array.IndexOf(Tanks, tankDef);")
    lines.append("            if (t < 0 || lane < 0 || lane > 1 || Math.Abs(sx) + Math.Abs(sz) != 1) return false;")
    lines.append("            int l = Array.IndexOf(Looks, look);")
    lines.append("            if (l < 0) l = 0;   // an unstyled tank draws the def's own (Scrapper) art")
    lines.append("            int side = sz == 1 ? 0 : sz == -1 ? 1 : sx == 1 ? 2 : 3;")
    lines.append("            inset = Table[t * Looks.Length + l][side * 2 + lane];")
    lines.append("            return true;")
    lines.append("        }")
    lines.append("    }")
    lines.append("}")
    return "\n".join(lines) + "\n", rows


def main():
    text, rows = generate()
    if "--write" in sys.argv:
        open(OUT, "w", encoding="utf-8", newline="\n").write(text)
        print("wrote", OUT)
    else:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != text:
            fails.append("Source/Machinery/TankArtEdges.cs differs from the installed art's measurement (run --write)")
        else:
            print("ok    TankArtEdges.cs matches the installed art (%d tank x look rows)" % len(rows))
    # sanity: the measurement can see -- the live capture's Scrapper universal tank skid sits ~0.46 cell above its footprint
    sc = [v for t, l, v in rows if t == "RM_LiquidTank" and l == "Scrapper"][0]
    if not (0.40 <= sc[0] <= 0.50):
        fails.append("can-fail: Scrapper RM_LiquidTank south inset %.3f, the live capture shows ~0.46" % sc[0])
    else:
        print("ok    Scrapper universal tank: south inset %.3f (live capture ~0.46)" % sc[0])
    for f in fails:
        print("FAIL  " + f)
    print("%s: %d failure(s)" % (os.path.basename(__file__), len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
