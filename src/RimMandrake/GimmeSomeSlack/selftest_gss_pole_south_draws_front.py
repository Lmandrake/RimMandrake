#!/usr/bin/env python3
"""T_POLE_SOUTH_DRAWS_FRONT_OFFLINE (bar poles_draw_in_front_when_south; RIMMANDRAKE_DRAW_SLACK_POLES_IN_FRONT_WHEN_SOUTH, his walk of
2026-11-20 row 13: "Power poles need the 'huge things' ordering rule of appearing 'in front' when they are south of something.")

Reads the SHIPPED decision: each standing mast's altitudeLayer from Defs/Aerial/RM_AerialAnchors.xml (inheritance resolved), and the
SouthDrawsFront rule's constants from MandrakePatches/Source/SouthDrawsFront/SouthDrawsFrontKernel.cs (through MandrakePatches'
own selftest parser, so neither can drift). The printed y of each thing is the patch's (SouthDrawsFrontPatches.cs): a plant prints
flat on the common layer at its quad's foot; a building on Building..BuildingOnTop prints on the common layer too, lifted by its
footprint's minZ, its own layer only breaking the tie inside one row (SouthDrawsFrontKernel.BuildingAltitude);
the mast head overlay draws real-time at TopAltitude (PawnState, RM_MapComponent_Aerial.cs:840). Larger y is in front.

The range of situations (what the game varies for this bar):
  mast      RM_AerialMast and RM_AerialLampMast; map depth 75, 250, 400; standing near the north edge, mid-map, near the south edge
  neighbour dx -2..2, dz -21..+6 cells from the mast (not its own cell):
            single-mesh plants (trees, bushes) of visual size 0.4..20 (vanilla tops out at 3.0, our greatboles reach 20) and
            drawSize.x 1 or 1.5, placed as Plant.Print places them (foot on the cell's south edge once the size passes 1);
            multi-mesh plants (grass, maxMeshCount 4 and 9) at every sub-cell, sizes 0.3..1;
            buildings on the Building (15), 16 and BuildingOnTop (17) layers: 1x1 and 2x2 footprints, drawn to their footprint
            or reaching north (drawOffset z 0.3..1.1 as in vanilla's obelisks and condition causers, drawSize up to 1x3); another mast
  pairs     every pair of mast part (body, head) and neighbour picture whose rectangles overlap, with feet on different rows
Left out, with the reason: two things on the same row (neither is south; the print order decides); a pawn (vanilla draws pawns over
every building and plant, SouthDrawsFront NOT covered); the mast's wires (they hang from the head).
Two regions the mast's own layer cannot reach are counted apart and are questions to the Conductor (not passes, not fails here):
  BUILDING_LAYER_REACH  a picture on the Building (15) or 16 layer south of a mast that reaches north into it, drawn behind the mast:
                        0 since every building joined the common layer (RIMMANDRAKE_ORDER_SLACK_MAST_BEHIND_TALL_SOUTHERN_PICTURES;
                        selftest_gss_mast_behind_tall_south_picture.py reads that rule across every row and map depth)
  HEAD_OVER_SOUTHERN_PICTURE  a plant or building south of a mast whose picture reaches the head overlay, which draws above pawns as
                        the wires do (no vanilla plant reaches it; our greatbole-class plants and pictures over 3 cells tall do)

    python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_pole_south_draws_front.py [--mast-layer Building]   (planted: the old layer)
Exit 0 PASS, 1 FAIL.
"""
import glob
import importlib.util
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
DEFS = os.path.join(HERE, "Defs", "Aerial", "RM_AerialAnchors.xml")
MP = os.path.join(HERE, "..", "MandrakePatches", "selftest_south_draws_front.py")
POLE_TABLE = os.path.join(HERE, "Source", "Aerial", "PoleGeometryTable.cs")
LAYERS = {"Building": 15, "BuildingOnTop": 17}      # AltitudeLayer indices, as SouthDrawsFrontKernel names them
PAWN_STATE = 25                                     # AltitudeLayer.PawnState (SouthDrawsFrontKernel.cs header)
MASTS = ("RM_AerialMast", "RM_AerialLampMast")
TEX = os.path.join(HERE, "Textures", "RimMandrake", "GimmeSomeSlack", "Aerial")
BAND = 0.25          # cells: the height of one band of the mast's opaque outline (16 bands over its 4-cell picture)
ALPHA = 16           # of 255: a pixel this opaque or more is part of the drawn mast


def opaque_bands(tex_name, w, h):
    """The mast's drawn outline, union over every look's art: [(x0, x1, z0, z1)] relative to the picture's SW corner, one per
    BAND-high band that holds an opaque pixel. A bounding box would count the transparent margins beside the pole."""
    from PIL import Image
    paths = [os.path.join(TEX, tex_name + ".png")] + sorted(glob.glob(os.path.join(TEX, "Styles", "*", tex_name + ".png")))
    out = {}
    for pth in paths:
        im = Image.open(pth).convert("RGBA")
        W, H = im.size
        a = im.getchannel("A").load()
        nb = int(round(h / BAND))
        for b in range(nb):
            r0, r1 = int(H - (b + 1) * H / nb), int(H - b * H / nb)
            cols = [x for x in range(W) if any(a[x, y] >= ALPHA for y in range(r0, r1))]
            if cols:
                x0, x1 = min(cols) / W * w, (max(cols) + 1) / W * w
                o = out.get(b)
                out[b] = (min(x0, o[0]), max(x1, o[1])) if o else (x0, x1)
    return [(x0, x1, b * BAND, (b + 1) * BAND) for b, (x0, x1) in sorted(out.items())], len(paths)


def kernel():
    spec = importlib.util.spec_from_file_location("sdf_selftest", MP)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, m.constants()


def mast_defs():
    """defName -> (layer name, drawSize (w,h), drawOffset z, head offsets z over looks) from the def file, parents resolved."""
    root = ET.parse(DEFS).getroot()
    by_name = {d.get("Name"): d for d in root.findall("ThingDef") if d.get("Name")}

    def field(d, path):
        while d is not None:
            v = d.find(path)
            if v is not None:
                return v.text.strip()
            d = by_name.get(d.get("ParentName"))
        return None
    tops = {}
    for line in open(POLE_TABLE, encoding="utf-8"):
        if 'd["' in line and "new Vector2(" in line and "Mast" in line:
            key = line.split('d["')[1].split('"]')[0]
            z = float(line.split("new Vector2(")[1].split(",")[1].strip().rstrip("f);").split("f")[0])
            tops.setdefault(key.split("/")[1], []).append(z)
    out = {}
    for d in root.findall("ThingDef"):
        dn = d.findtext("defName")
        if dn not in MASTS:
            continue
        w, h = [float(x) for x in field(d, "graphicData/drawSize").strip("()").split(",")]
        oz = float(field(d, "graphicData/drawOffset").strip("()").split(",")[2])
        fallback = float(field(d, "modExtensions/li/topOffsetZ"))
        bands, looks = opaque_bands(os.path.basename(field(d, "graphicData/texPath")), w, h)
        out[dn] = (field(d, "altitudeLayer"), (w, h), oz, sorted(set(tops.get(dn) or [fallback])), bands, looks)   # head: the def's own only for a look with no art
    return out


def neighbours():
    """(kind, layer, foot z offset from the cell, rect (x0,x1,z0,z1) relative to the cell's SW corner, name)."""
    out = []
    for v in (0.4, 0.8, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 20.0):
        for dsx in (1.0, 1.5):
            q = dsx * v
            cz = 0.5 if 0.5 - v / 2 >= 0 else v / 2          # Plant.Print, maxMeshCount 1: lifted so the foot is the cell's south edge
            out.append(("plant", None, cz - v / 2, (0.5 - q / 2, 0.5 + q / 2, cz - q / 2, cz + q / 2), "tree v%g ds%g" % (v, dsx)))
    for n in (2, 3):
        for i in range(n):
            for j in range(n):
                for v in (0.3, 0.6, 1.0):
                    cx, cz = (i + 0.5) / n, (j + 0.5) / n
                    out.append(("plant", None, cz - v / 2, (cx - v / 2, cx + v / 2, cz - v / 2, cz + v / 2), "grass%d v%g" % (n * n, v)))
    for layer in (15, 16, 17):
        for (fw, fh) in ((1, 1), (2, 2)):
            for (dh, oz) in ((fh, 0.0), (fh + 0.6, 0.3), (fh + 1.0, 0.5), (fh + 1.5, 0.75), (fh + 2.0, 1.1)):
                cz = fh / 2 + oz
                out.append(("building", layer, 0.0, (0, fw, cz - dh / 2, cz + dh / 2), "building L%d %dx%d h%g off%g" % (layer, fw, fh, dh, oz)))
    return out


def printed_y(m, c, kind, layer, foot, map_z):
    """The y SouthDrawsFrontPatches prints a thing at (foot: a plant quad's foot, a building's footprint minZ). A copy of
    SouthDrawsFrontKernel.PlantAltitude / BuildingAltitude in Python; selftest_gss_mast_behind_tall_south_picture.py holds this
    copy to the compiled kernel."""
    L = c["LayerSpacing"]
    if kind == "plant":
        return m.plant_base(foot, c, map_z)
    if c["BuildingMinLayer"] <= layer <= c["CommonLayer"]:
        return c["CommonLayer"] * L + c["PrintBand"] * m.southness(foot, map_z) - (c["CommonLayer"] - layer) * c["LayerTie"]
    return layer * L


def main(argv):
    planted = argv[argv.index("--mast-layer") + 1] if "--mast-layer" in argv else None
    m, c = kernel()
    L = c["LayerSpacing"]
    masts = mast_defs()
    if set(masts) != set(MASTS):
        print("FAIL could not look: mast defs read %s" % sorted(masts))
        return 1

    def printed(kind, layer, foot, map_z):
        return printed_y(m, c, kind, layer, foot, map_z)
    cases = ties = 0
    worst = None
    bad, apart = [], {"BUILDING_LAYER_REACH": [], "HEAD_OVER_SOUTHERN_PICTURE": []}
    for dn, (lname, (w, h), oz, tops, bands, looks) in sorted(masts.items()):
        if not bands:
            print("FAIL could not look: no opaque pixel in %s's art (%d files)" % (dn, looks))
            return 1
        layer = LAYERS[planted or lname]
        for map_z in (75, 250, 400):
            for Z in (1, map_z // 2, map_z - 6):
                X = 30
                yb = printed("building", layer, Z, map_z)
                x0, z0 = X + 0.5 - w / 2, Z + 0.5 + oz - h / 2
                parts = [("body", (x0 + b[0], x0 + b[1], z0 + b[2], z0 + b[3]), yb) for b in bands] + [("head", (X + 0.5 - 1, X + 0.5 + 1, Z + 0.5 + t - 0.5, Z + 0.5 + t + 0.5), PAWN_STATE * L + 4 * c["AltInc"])
                                                for t in tops]
                for dx in range(-2, 3):
                    for dz in range(-21, 7):
                        if dx == 0 and dz == 0:
                            continue
                        x, z = X + dx, Z + dz
                        for kind, nl, foot_off, r, name in neighbours() + [("building", layer, 0.0, (0.5 - w / 2, 0.5 + w / 2, 0.5 + oz - h / 2, 0.5 + oz + h / 2), "another mast")]:
                            fw = int(round(r[1] - r[0])) if kind == "building" and name != "another mast" else 1
                            if x <= X < x + fw and z <= Z < z + fw:
                                continue                      # a footprint on the mast's own cell: nothing can stand there
                            foot = z + foot_off
                            rect = (x + r[0], x + r[1], z + r[2], z + r[3])
                            yn = printed(kind, nl, foot, map_z)
                            seen = set()
                            for pname, pr, yp in parts:
                                if pname in seen:
                                    continue
                                if min(pr[1], rect[1]) - max(pr[0], rect[0]) <= 1e-9 or min(pr[3], rect[3]) - max(pr[2], rect[2]) <= 1e-9:
                                    continue
                                seen.add(pname)
                                if abs(foot - Z) < 1e-9:
                                    ties += 1
                                    continue
                                cases += 1
                                mast_south = Z < foot
                                margin = (yp - yn) if mast_south else (yn - yp)
                                where = "%s map%d z%d %s at (%+d,%+d) %s: mast %s, y %.5f vs %.5f" % (
                                    dn, map_z, Z, name, dx, dz, pname, "south" if mast_south else "north", yp, yn)
                                if margin > 0:
                                    if worst is None or margin < worst[0]:
                                        worst = (margin, where)
                                    continue
                                if pname == "head" and not mast_south:
                                    apart["HEAD_OVER_SOUTHERN_PICTURE"].append((where, name))
                                elif pname == "body" and kind == "building" and nl < layer and not mast_south:
                                    apart["BUILDING_LAYER_REACH"].append((where, name))
                                else:
                                    bad.append(where)
    print("pole south draws front%s: %d overlapping pairs read (%d on one row, left out); refused %d (limit 0); worst margin %s"
          % (" (PLANTED mast layer %s)" % planted if planted else "", cases, ties, len(bad),
             "%.5f at %s" % worst if worst else "none"))
    for b in bad[:8]:
        print("REFUSED " + b)
    for k, v in apart.items():
        kinds = sorted({n for _, n in v})
        print("APART %s: %d pairs (a question to the Conductor, not decided here)%s" % (k, len(v), (": " + "; ".join(kinds[:6])) if kinds else ""))
    beside = sum(1 for _, n in apart["BUILDING_LAYER_REACH"] if n.endswith("off0"))
    print("  BUILDING_LAYER_REACH: %d by a picture drawn inside its footprint (a 2x2 or wider building beside the mast, its north row "
          "on the mast's row), %d by a picture reaching north past its footprint" % (beside, len(apart["BUILDING_LAYER_REACH"]) - beside))
    head_plants = sorted({float(n.split(" v")[1].split()[0]) for _, n in apart["HEAD_OVER_SOUTHERN_PICTURE"] if n.startswith("tree")})
    print("  HEAD_OVER_SOUTHERN_PICTURE: smallest plant reaching the head %s cells (vanilla's largest is 3.0)" % (head_plants[0] if head_plants else "none"))
    print("note: the margin between two rows is PrintBand / (map depth + 2) per cell of foot difference (SouthDrawsFrontKernel."
          "Southness), so a sub-cell grass foot ordered against the mast foot passes by that resolution, not by a seed")
    if cases < 1000:
        print("FAIL could not look: only %d overlapping pairs" % cases)
        return 1
    print("PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
