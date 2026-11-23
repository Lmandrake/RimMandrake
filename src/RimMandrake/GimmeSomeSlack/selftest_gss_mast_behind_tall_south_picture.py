#!/usr/bin/env python3
"""T_MAST_BEHIND_TALL_SOUTH_PICTURE_OFFLINE (bar poles_draw_in_front_when_south; RIMMANDRAKE_ORDER_SLACK_MAST_BEHIND_TALL_SOUTHERN_PICTURES):
a building whose picture reaches north into a mast just north of it draws in front of the mast.

Reads the SHIPPED decision, not a copy: MandrakePatches/Source/SouthDrawsFront/SouthDrawsFrontKernel.cs is compiled alone into
MandrakePatches/Scenario/SouthDrawsFrontKernelProbe (plain net8.0, winbuild.stage_build) and asked, for every case, the altitude a
thing prints and draws at (BuildingAltitude, PlantAltitude, BuildingLift, Orders). Each mast's layer comes from
Defs/Aerial/RM_AerialAnchors.xml through selftest_gss_pole_south_draws_front.mast_defs (inheritance resolved). The wiring checks
read SouthDrawsFrontPatches.cs: the print path and the real-time path both take their number from the kernel. Larger y is in front.

The range of situations (what the game can vary for this bar):
  the mast        RM_AerialMast, RM_AerialLampMast (their def's altitudeLayer); any row of the map, edges included
  the neighbour   a non-plant thing on Building (15), BuildingBelowTop (16) or BuildingOnTop (17), whose footprint's south row is
                  any row south of the mast (the bar) or north of it (the mirror). Its picture's size and drawOffset, its
                  footprint's width and depth, dx and its drawer type do not enter the altitude: the print path and the real-time
                  path give one altitude per thing from (layer, footprint minZ, map depth) alone (SouthDrawsFrontPatches.cs). So
                  every picture that reaches the mast, inside its footprint or north past it, is one of these cases
  plants          the other users of the rule (BiomesShell RM_Canopy's trees, every vanilla plant) against those buildings: a
                  plant foot at a cell's south edge or a quarter-cell inside it (multi-mesh grass), a whole row or more apart
  the map         depth 25, 50, 75, 100, 150, 200, 225 .. 400 by 25, 500, 750, 1000 (pocket and quest maps up to modded giants)
  seeds, time     nothing: the kernel has no random or clock input, and a map-mesh print is rebuilt only when a cell changes
Regimes read: BAR (neighbour south of a mast), MIRROR (mast south of a neighbour), ALL_PAIRS (any two ordered non-plant things on
different rows), ROW_ORDER (same row: vanilla's layer order is kept), PLANTS (either way, a row or more apart), BAND (every ordered
altitude plus an overlay's AltInc stays under the Item layer, over the layer below the common one plus its band), LIFT (each
thing's one lift is its altitude less its vanilla altitude; Orders covers exactly 11..17 for plants and 15..17 for the rest),
MODEL (the pole test's Python copy of the rule equals the compiled kernel), WIRING (the patch calls the kernel).
Left out, with the reason: two things on the same row against a plant (neither is south: the tie inside a row is the layer
order); the mast head overlay over a plant over 4 cells tall (polish.md, region (b)); pawns (the Pawn layer, two layers above,
draws over every printed thing: SouthDrawsFront NOT covered); a part a building draws at an explicit altitude such as
def.altitudeLayer.AltitudeFor() (5 sites in vanilla 1.6, e.g. CompBandNode): it does not follow its body's lift.

    python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_mast_behind_tall_south_picture.py
Exit 0 PASS, 1 FAIL. Each check prints its worst value, its limit and its case count.
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MPDIR = os.path.join(HERE, "..", "MandrakePatches")
PROBE = os.path.join(MPDIR, "Scenario", "SouthDrawsFrontKernelProbe")
PATCHES = os.path.join(MPDIR, "Source", "SouthDrawsFront", "SouthDrawsFrontPatches.cs")
POLE = os.path.join(HERE, "selftest_gss_pole_south_draws_front.py")
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
import winbuild  # noqa: E402

MAPS = (25, 50, 75, 100, 150) + tuple(range(200, 401, 25)) + (500, 750, 1000)
ORDERED = (15, 16, 17)                 # Building, BuildingBelowTop, BuildingOnTop (AltitudeLayer indices)
ITEM = 18                              # AltitudeLayer.Item, the next layer anything prints on above BuildingOnTop
MODEL_LIMIT = 2e-6                     # 4 float32 ulps at y ~ 6.6 (ulp 4.8e-7): the compiled kernel is float32, the copy float64
PLANT_FEET = tuple(j / 8 for j in range(8))   # a cell's south edge (Plant.Print, one mesh) and sub-cell grass feet, every 1/8 cell


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ask(lines):
    rc, rec = winbuild.stage_build(os.path.join(PROBE, "SouthDrawsFrontKernelProbe.csproj"), stage_name="SouthDrawsFrontKernelProbe",
                                   extra_dirs=[os.path.join(MPDIR, "Source", "SouthDrawsFront")])
    if rc:
        return None, "probe build failed rc %d" % rc
    dll = winbuild.staged_win(rec, PROBE) + "\\bin\\Release\\net8.0\\SouthDrawsFrontKernelProbe.dll"
    r = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll], input="\n".join(lines) + "\n", stdout=__import__("subprocess").PIPE,
                                      text=True, cwd="/mnt/d/Luke/dev", timeout=300)
    out = (r.stdout or "").splitlines()
    if r.returncode or len(out) != len(lines):
        return None, "probe rc %d, %d answers for %d queries" % (r.returncode, len(out), len(lines))
    errs = [o for o in out if o.startswith("ERR")]
    if errs:
        return None, "probe refused %d queries, first: %s" % (len(errs), errs[0])
    return dict(zip(lines, out)), None


class Check:
    def __init__(self, name, limit_text):
        self.name, self.limit_text, self.n, self.worst, self.where, self.bad = name, limit_text, 0, None, "", 0

    def read(self, value, ok, where):
        self.n += 1
        if not ok:
            self.bad += 1
        if self.worst is None or value < self.worst:
            self.worst, self.where = value, where

    def line(self):
        return "%-9s %s: worst %s (limit %s), %d cases, %d refused%s" % (
            self.name, "PASS" if self.ok() else "FAIL", "%.7f" % self.worst if self.worst is not None else "none", self.limit_text,
            self.n, self.bad, " at " + self.where if self.where else "")

    def ok(self):
        return self.n > 0 and self.bad == 0


def main():
    pole = load("pole_south_selftest", POLE)
    m, c = pole.kernel()
    masts = pole.mast_defs()
    mast_layers = {}
    for dn in pole.MASTS:
        lname = masts.get(dn, (None,))[0]
        if lname not in pole.LAYERS:
            print("FAIL could not look: %s altitudeLayer %r" % (dn, lname))
            return 1
        mast_layers[dn] = pole.LAYERS[lname]
    q = []
    for mz in MAPS:
        for z in range(mz):
            q += ["B %d %d %d" % (l, z, mz) for l in ORDERED] + ["L %d %d %d" % (l, z, mz) for l in ORDERED]
            q += ["P %r %d" % (z + f, mz) for f in PLANT_FEET]
    q += ["O %d %d" % (p, l) for p in (0, 1) for l in range(0, 40)] + ["A %d" % l for l in range(0, 40)]
    ans, err = ask(q)
    if err:
        print("FAIL could not look: " + err)
        return 1
    A = {l: float(ans["A %d" % l]) for l in range(40)}
    tie = c["LayerTie"]
    # the one pair the layer tie turns (SouthDrawsFrontKernel.LayerTie): a plant north of an L-thing's foot by at most
    # (CommonLayer - L) * LayerTie / row step of a cell
    window = {l: {mz: (c["CommonLayer"] - l) * tie / (c["PrintBand"] / (mz + 2)) for mz in MAPS} for l in ORDERED}

    bar, mirror, allp, roword = Check("BAR", "> 0"), Check("MIRROR", "> 0"), Check("ALL_PAIRS", "> 0"), Check("ROW_ORDER", "> 0")
    plants, band_top, band_low = Check("PLANTS", "> 0"), Check("BAND_TOP", "> 0"), Check("BAND_LOW", "> 0")
    tiewin = Check("TIE_WIN", "inside the documented window")
    lift, orders, model = Check("LIFT", "<= 1e-6 off"), Check("ORDERS", "= vanilla range"), Check("MODEL", "<= %g off" % MODEL_LIMIT)
    for mz in MAPS:
        yb = {l: [float(ans["B %d %d %d" % (l, z, mz)]) for z in range(mz)] for l in ORDERED}
        # prefix max / suffix max of every ordered layer's y over rows, so each pair (south row < north row) is read exactly
        south_min = {l: [None] * mz for l in ORDERED}          # min over rows < z of y(l, row): the lowest southern neighbour
        north_max = {l: [None] * mz for l in ORDERED}          # max over rows > z of y(l, row): the highest northern neighbour
        for l in ORDERED:
            run = None
            for z in range(mz):
                south_min[l][z] = run
                run = yb[l][z] if run is None else min(run, yb[l][z])
            run = None
            for z in range(mz - 1, -1, -1):
                north_max[l][z] = run
                run = yb[l][z] if run is None else max(run, yb[l][z])
        for z in range(mz):
            for ln in ORDERED:                                  # the northern / southern thing of a pair, here at row z
                for l in ORDERED:
                    if south_min[l][z] is not None:            # every l-thing on any row south of an ln-thing on row z
                        d = south_min[l][z] - yb[ln][z]
                        where = "map%d L%d at z<%d vs L%d at z%d" % (mz, l, z, ln, z)
                        allp.read(d, d > 0, where)
                        for dn, ml in mast_layers.items():
                            if ml == ln:
                                bar.read(d, d > 0, dn + " " + where)
                    if north_max[l][z] is not None:            # every l-thing on any row north of an ln-thing on row z
                        d = yb[ln][z] - north_max[l][z]
                        for dn, ml in mast_layers.items():
                            if ml == ln:
                                mirror.read(d, d > 0, "%s map%d at z%d vs L%d north of it" % (dn, mz, z, l))
            for lo, hi in zip(ORDERED, ORDERED[1:]):
                d = yb[hi][z] - yb[lo][z]
                roword.read(d, d > 0, "map%d z%d L%d over L%d" % (mz, z, hi, lo))
            for l in ORDERED:
                d = A[ITEM] - (yb[l][z] + c["AltInc"])
                band_top.read(d, d > 0, "map%d z%d L%d" % (mz, z, l))
                d = yb[l][z] - (A[c["CommonLayer"] - 1] + c["PrintBand"] + c["AltInc"])
                band_low.read(d, d > 0, "map%d z%d L%d" % (mz, z, l))
                lf = float(ans["L %d %d %d" % (l, z, mz)])
                d = abs(lf - (yb[l][z] - A[l]))
                lift.read(-d, d <= 1e-6, "map%d z%d L%d lift %.6f" % (mz, z, l, lf))
                d = abs(pole.printed_y(m, c, "building", l, z, mz) - yb[l][z])
                model.read(-d, d <= MODEL_LIMIT, "building map%d z%d L%d" % (mz, z, l))
            for f in PLANT_FEET:
                foot = z + f
                yp = float(ans["P %r %d" % (foot, mz)])
                d = abs(pole.printed_y(m, c, "plant", None, foot, mz) - yp)
                model.read(-d, d <= MODEL_LIMIT, "plant map%d foot %g" % (mz, foot))
                for l in ORDERED:
                    # near rows (within 3 cells of the foot) pair by pair; farther rows through the prefix / suffix extremes
                    for row in range(max(0, z - 3), min(mz, z + 4)):
                        g = foot - row                          # > 0: the plant stands north of the building's foot
                        if abs(g) < 1e-9:
                            continue                            # one foot: neither is south
                        d = (yb[l][row] - yp) if g > 0 else (yp - yb[l][row])
                        where = "map%d L%d row %d vs plant foot %g" % (mz, l, row, foot)
                        if g > 0 and d <= 0 and g <= window[l][mz] + 1e-9:
                            tiewin.read(g, True, where)         # inside the layer tie's documented window: counted apart
                            continue
                        plants.read(d, d > 0, where)
                    if z - 4 >= 0:
                        d = south_min[l][z - 3] - yp            # every row < z-3
                        plants.read(d, d > 0, "map%d L%d rows < %d vs plant foot %g" % (mz, l, z - 3, foot))
                    if z + 4 < mz:
                        d = yp - north_max[l][z + 3]            # every row > z+3
                        plants.read(d, d > 0, "map%d plant foot %g vs L%d rows > %d" % (mz, foot, l, z + 3))
    for p in (0, 1):
        for l in range(40):
            want = (11 if p else 15) <= l <= 17
            got = ans["O %d %d" % (p, l)] == "1"
            orders.read(0.0 if got == want else -1.0, got == want, "plant=%d layer %d -> %s" % (p, l, got))

    src = open(PATCHES, encoding="utf-8").read()
    wiring = [
        ("print path decides with the kernel", "SouthDrawsFrontKernel.Orders(plant, layer)" in src),
        ("print lift is the kernel's BuildingLift", re.search(r"printingLift = SouthDrawsFrontKernel\.BuildingLift\(layer, t\.OccupiedRect\(\)\.minZ, map\.Size\.z\)", src) is not None),
        ("a building quad gets that one lift", "center.y += printingLift;" in src),
        ("a plant quad prints at the kernel's PlantAltitude", "SouthDrawsFrontKernel.PlantAltitude(foot, printingMapZ)" in src),
        ("real-time lift is the same BuildingLift", re.search(r"drawingLift = SouthDrawsFrontKernel\.BuildingLift\(layer, __instance\.OccupiedRect\(\)\.minZ, map\.Size\.z\)", src) is not None),
        ("Thing.DynamicDrawPhase and Thing.DrawPos are patched", "nameof(Thing.DynamicDrawPhase)" in src and "nameof(Thing.DrawPos)" in src),
        ("DrawPos carries the lift only for the thing being drawn", "__instance == drawingThing && drawingHere" in src and "__result.y += drawingLift;" in src),
        ("no own-layer lift left in the patch", "PrintOffset(" not in src),
        # the one vanilla building part drawn at an explicit def.altitudeLayer.AltitudeFor() (decompiled 1.6,
        # CompBandNode.cs:176, the band node's tuning bar at Building + AltInc, under its lifted body on every row)
        ("the band node's tuning bar follows its body's lift",
         "typeof(CompBandNode), nameof(CompBandNode.PostDraw)" in src and "nameof(PartAltitudeTranspiler)" in src
         and "return drawingHere ? y + drawingLift : y;" in src),
    ]
    checks = (bar, mirror, allp, roword, plants, band_top, band_low, lift, orders, model)
    print("mast behind tall south picture: masts %s; maps %s..%s (%d depths); compiled kernel answered %d queries"
          % (", ".join("%s L%d" % kv for kv in sorted(mast_layers.items())), MAPS[0], MAPS[-1], len(MAPS), len(q)))
    for ch in checks:
        print(ch.line())
    print("TIE_WIN   apart: %d plant-building pairs inside the layer tie's window (widest %.4f cell, L15 on a %d-deep map); the "
          "plant draws over the building there" % (tiewin.n, max(window[15].values()), MAPS[-1]))
    print("WIRING    %s: %d of %d" % ("PASS" if all(ok for _, ok in wiring) else "FAIL", sum(ok for _, ok in wiring), len(wiring)))
    for name, ok in wiring:
        if not ok:
            print("  MISSING " + name)
    good = all(ch.ok() for ch in checks) and all(ok for _, ok in wiring)
    print("PASS" if good else "FAIL")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
