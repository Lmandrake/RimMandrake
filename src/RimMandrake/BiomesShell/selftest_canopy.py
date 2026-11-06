#!/usr/bin/env python3
# selftest-timeout: 600   (lost WSL launches winbuild.run_interop repeats: up to 3 at ~2 min each, INTEROP_RETRY_FIX_EIGHTY_SCRIPTS_LEFT)
"""Offline proof of the zoom-gated canopy layer (CANOPY_LAYER_BUILD_ROOF_OF_THE_WORLD).

Owner, 2026-10-18: "Titanic trees should be seen only as the solid trunk" and "scroll out from the map enough that
only the top forest canopy is seen". Constants are PARSED from Source/RM_Canopy.cs, so this cannot drift from the C#.

  The sweeps in C1 and C2 run the REAL CanopyMath block cut out of RM_Canopy.cs, compiled with dotnet.exe (the
  selftest_world_paths_drawn.py convention); Python only judges its answers.
  C1 fade: CanopyMath.Alpha swept over 0.5..80 px per cell and every threshold/fade the
     settings sliders allow: 0 at or above the threshold, 1 at or below threshold - fade, monotone between; the
     defaults are hidden at vanilla's starting zoom and solid at vanilla's furthest zoom on 1080p and 1440p.
  C2 extent: for canopies of 12..30 cells at every growth, jitter and foot lift Plant.Print can produce, the cells
     CanopyMath.QuadCells reports cover the whole printed quad, and the C# encapsulates them into GetBoundaryRect.
  C3 defs + art: every tree def carrying RM_CanopyExtension (the Titanic tier: RM_SweetlineTree) names trunk and
     canopy pools holding exactly its own pool's letters; canopy PNGs are ArtPxPerCell px per cell of its largest
     visual size; trunk PNGs keep the whole picture's canvas; the canopy prints below LayingPawn and Pawn.
  C4 settings: canopyEnabled / canopyThresholdPx / canopyFadePx exist, are saved, default to the shipped values,
     and a change reprints the maps.
  C5 build: the committed RimMandrake.Biomes.dll's .srchash names RM_Canopy.cs with its current hash (the DLL was
     built from this source).
"""
import hashlib
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CS = HERE / "Source" / "RM_Canopy.cs"
MOD_CS = HERE / "Source" / "RM_BiomesMod.cs"
CSPROJ = HERE / "Source" / "RM_Biomes.csproj"
STAMP = HERE / "Assemblies" / "RimMandrake.Biomes.dll.srchash"
ART_PY = HERE / "canopy_art.py"
sys.path.insert(0, str(HERE.parent / "Utils"))
# dotnet.exe needs a Windows drive (selftest_world_paths_drawn.py's convention).
EXEC_SCRATCH = os.environ.get("RM_SELFTEST_EXEC_SCRATCH", "/mnt/d/ClaudeWork/rimmandrake/selftest_tmp")
HARNESS = r"""
using System;
using System.Globalization;
using System.IO;
using RimMandrake.Biomes;
public static class Harness
{
    public static void Main(string[] a)
    {
        var ci = CultureInfo.InvariantCulture;
        var o = new System.Text.StringBuilder();
        foreach (string line in File.ReadAllLines(a[0]))
        {
            string[] p = line.Split(' ');
            if (p[0] == "A")
                o.Append("A ").Append(p[1]).Append(' ').Append(p[2]).Append(' ').Append(p[3]).Append(' ')
                 .Append(CanopyMath.Alpha(float.Parse(p[1], ci), float.Parse(p[2], ci), float.Parse(p[3], ci)).ToString("R", ci)).Append('\n');
            else if (p[0] == "Q")
            {
                float cz = CanopyMath.AnchoredZ(float.Parse(p[2], ci), int.Parse(p[3], ci), float.Parse(p[4], ci));
                CanopyMath.QuadCells(float.Parse(p[1], ci), cz, float.Parse(p[4], ci), out int x0, out int z0, out int x1, out int z1);
                o.Append(line).Append(" -> ").Append(cz.ToString("R", ci)).Append(' ').Append(x0).Append(' ').Append(z0)
                 .Append(' ').Append(x1).Append(' ').Append(z1).Append('\n');
            }
        }
        Console.Write(o.ToString());
    }
}
"""
EXEC_CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><Nullable>disable</Nullable>
  <EnableDefaultCompileItems>false</EnableDefaultCompileItems><ImplicitUsings>disable</ImplicitUsings></PropertyGroup>
  <ItemGroup><Compile Include="Harness.cs" /><Compile Include="CanopyMath.cs" /></ItemGroup>
</Project>
"""
ALT = ["BelowTerrain", "TerrainEdges", "Terrain", "TerrainScatter", "Floor", "Conduits", "FloorCoverings",
       "FloorEmplacement", "Filth", "Zone", "SmallWire", "LowPlant", "MoteLow", "Shadows", "DoorMoveable", "Building",
       "BuildingBelowTop", "BuildingOnTop", "Item", "ItemImportant", "LayingPawn", "PawnRope", "Projectile", "Pawn"]
# Verse.AltitudeLayer order (decompiled 1.6), the same list src/RimMandrake/Utils/plant_draw_layers.py carries.

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def const(text, name):
    m = re.search(r"public const (?:int|float) " + name + r"\s*=\s*([0-9.]+)f?;", text)
    if not m:
        raise SystemExit("FAIL cannot parse %s from %s" % (name, CS))
    return float(m.group(1))


def canopy_math_source(text):
    """The REAL `public static class CanopyMath { ... }` block of RM_Canopy.cs (brace-matched), compilable alone."""
    i = text.index("public static class CanopyMath")
    j = text.index("{", i)
    depth = 0
    for k in range(j, len(text)):
        depth += {"{": 1, "}": -1}.get(text[k], 0)
        if depth == 0:
            return "using System;\nnamespace RimMandrake.Biomes\n{\n" + text[i:k + 1] + "\n}\n"
    raise SystemExit("FAIL CanopyMath block is not brace-balanced")


def run_csharp(text, lines):
    """Compile CanopyMath with the harness, feed it `lines`, return its output lines (None if it cannot run)."""
    import winbuild  # noqa: E402
    os.makedirs(EXEC_SCRATCH, exist_ok=True)
    where = tempfile.mkdtemp(prefix="canopymath_", dir=EXEC_SCRATCH)
    try:
        Path(where, "CanopyMath.cs").write_text(canopy_math_source(text))
        Path(where, "Harness.cs").write_text(HARNESS)
        Path(where, "CanopyExec.csproj").write_text(EXEC_CSPROJ)
        Path(where, "in.txt").write_text("\n".join(lines) + "\n")
        dotnet = winbuild.dotnet_exe()
        for _ in range(2):   # one retry: a cold dotnet.exe build on a fresh temp dir has failed once with no output
            built = winbuild.run_interop_captured([dotnet, "build", winbuild.win(os.path.join(where, "CanopyExec.csproj")), "-c", "Release",
                                    "--nologo", "-v", "quiet"], cwd=where, capture_output=True, text=True, timeout=300)
            if built.returncode == 0:
                break
        if built.returncode != 0:
            print("execution: harness build failed: " + built.stdout[-1200:])
            return None
        ran = winbuild.run_interop_captured([dotnet, winbuild.win(os.path.join(where, "bin", "Release", "net8.0", "CanopyExec.dll")),
                              winbuild.win(os.path.join(where, "in.txt"))], cwd=where, capture_output=True, text=True,
                             timeout=200)
        if ran.returncode != 0:
            print("execution: harness exited %d: %s" % (ran.returncode, (ran.stdout + ran.stderr)[-600:]))
            return None
        return ran.stdout.replace("\r", "").splitlines()
    finally:
        shutil.rmtree(where, ignore_errors=True)


def fmt(x):
    return repr(float(x))


def c12(text):
    """C1 + C2 on the C# itself: every case below is computed by the compiled CanopyMath, then judged here."""
    thr0, fade0 = const(text, "DefaultThresholdPx"), const(text, "DefaultFadePx")
    lo, hi, fmax = const(text, "MinThresholdPx"), const(text, "MaxThresholdPx"), const(text, "MaxFadePx")
    jit = const(text, "VanillaJitter")
    pxs = [0.5 + 0.25 * i for i in range(318)]
    thrs = [lo + 0.5 * i for i in range(int((hi - lo) / 0.5) + 1)]
    fades = [0.5 * i for i in range(int(fmax / 0.5) + 1)]
    lines = ["A %s %s %s" % (fmt(px), fmt(t), fmt(f)) for t in thrs for f in fades for px in pxs]
    extra = [(h / 48.0, "%dp starting zoom" % h) for h in (1080, 1440)] + \
            [(h / 120.0, "%dp vanilla furthest zoom" % h) for h in (1080, 1440)]
    lines += ["A %s %s %s" % (fmt(px), fmt(thr0), fmt(fade0)) for px, _ in extra]
    lines.append("A NaN %s %s" % (fmt(thr0), fmt(fade0)))
    quads = []
    for side_tenths in range(120, 301, 7):              # 12..30 cell canopies
        for growth in (0.05, 0.3, 0.6, 1.0):
            visual = side_tenths / 10.0 * (0.4 + 0.6 * growth)
            for px in (0, 7, 16):                       # cell within a section
                for pz in (0, 3, 16):
                    for jx in (-jit, 0, jit):
                        for jz in (-jit, 0, jit):
                            quads.append((px + 0.5 + jx, pz + 0.5 + jz, pz, visual))
    lines += ["Q %s %s %d %s" % (fmt(cx), fmt(cz), pz, fmt(v)) for cx, cz, pz, v in quads]
    out = run_csharp(text, lines)
    check(out is not None, "C1/C2 the real CanopyMath compiled and ran (dotnet.exe, %d cases)" % len(lines))
    if out is None:
        return
    alpha = {}
    qres = []
    for ln in out:
        p = ln.split()
        if p[0] == "A":
            alpha[(p[1], p[2], p[3])] = float(p[4])
        elif p[0] == "Q":
            qres.append(ln)
    bad = 0
    for t in thrs:
        for f in fades:
            prev = 2.0
            for px in pxs:                              # px rising = zooming IN: alpha must never rise
                a = alpha.get((fmt(px), fmt(t), fmt(f)))
                if a is None or not 0 <= a <= 1 or a > prev + 1e-6:
                    bad += 1
                    continue
                if px >= t and a != 0:
                    bad += 1
                if (px < t - f or (f >= 0.01 and px <= t - f)) and a != 1:
                    bad += 1
                if f >= 0.01 and t - f < px < t and abs(a - (t - px) / f) > 1e-5:
                    bad += 1                             # linear in between
                prev = a
    check(bad == 0, "C1 C# Alpha swept %d thresholds x %d fades x %d zooms: bounded, monotone, linear, 0 at/above "
                    "threshold, 1 at/below threshold-fade (%d violations)" % (len(thrs), len(fades), len(pxs), bad))
    for (px, what), want in zip(extra, (0, 0, 1, 1)):
        a = alpha.get((fmt(px), fmt(thr0), fmt(fade0)))
        check(a == want, "C1 %s (%.1f px/cell): canopy %s (alpha %s)" % (what, px, "solid" if want else "hidden", a))
    check(alpha.get(("NaN", fmt(thr0), fmt(fade0))) == 0, "C1 NaN cell size -> hidden")
    for needle in ("CanopyMath.Alpha(px, RM_BiomesSettings.canopyThresholdPx, RM_BiomesSettings.canopyFadePx)",
                   "cam.CellSizePixels"):
        check(needle in text, "C1 the C# draws on the absolute cell size: '%s' present" % needle)
    check("if (RM_Canopy.FrameAlpha() <= 0f)" in text, "C1 DrawLayer returns before drawing at alpha 0")

    bad = 0
    lifted = 0
    for ln in qres:
        left, right = ln.split(" -> ")
        _, cx, cz0, pz, v = left.split()
        cz, x0, z0, x1, z1 = right.split()
        cx, cz0, pz, v, cz = float(cx), float(cz0), int(pz), float(v), float(cz)
        x0, z0, x1, z1 = int(x0), int(z0), int(x1), int(z1)
        want_cz = pz + v / 2 if cz0 - v / 2 < pz else cz0   # Plant.Print's foot lift
        lifted += want_cz != cz0
        h = v / 2
        if abs(cz - want_cz) > 1e-4:
            bad += 1
        if not (x0 <= cx - h + 1e-4 and x1 + 1 >= cx + h - 1e-4 and z0 <= cz - h + 1e-4 and z1 + 1 >= cz + h - 1e-4):
            bad += 1                                     # misses part of the quad
        if (x1 - x0 + 1) > math.ceil(v) + 1 or (z1 - z0 + 1) > math.ceil(v) + 1:
            bad += 1                                     # more than one cell of slack
    check(len(qres) == len(quads) and lifted > 0 and bad == 0,
          "C2 C# AnchoredZ + QuadCells: foot lift as Plant.Print (%d lifted), every printed quad covered, at most one "
          "cell of slack (%d cases, %d bad)" % (lifted, len(qres), bad))
    check("bounds = bounds.Encapsulate(CanopyRect(center, side));" in text
          and "public override CellRect GetBoundaryRect() => bounds;" in text,
          "C2 the canopy's true extent is encapsulated into GetBoundaryRect")
    check("Rand.Seed = p.Position.GetHashCode();" in text and "Gen.RandomHorizontalVector(CanopyMath.VanillaJitter)" in text
          and text.index("flip = Rand.Bool;") < text.index("index = Rand.Range(0, pool.SubGraphicsCount);"),
          "C2 canopy replays Plant.Print's Rand order (seed, jitter, flip, variant) so trunk and canopy share a variant")


def letters(folder, prefix):
    if not folder.is_dir():
        return None
    return sorted(p.stem[len(prefix):] for p in folder.glob(prefix + "*.png"))


def c3(text):
    from PIL import Image
    art_px = const(text, "ArtPxPerCell")
    m = re.search(r"AltitudeLayer\.(\w+)\.AltitudeFor\(5f\)", text)
    layer = m.group(1) if m else None
    check(layer in ALT and ALT.index(layer) > ALT.index("BuildingOnTop") and ALT.index(layer) < ALT.index("LayingPawn"),
          "C3 canopy altitude %s+5 is above every plant layer and below LayingPawn/Pawn" % layer)
    found = []
    for xml in sorted((REPO / "src").glob("*/*/Defs/**/*.xml")):
        try:
            root = ET.parse(xml).getroot()
        except ET.ParseError:
            continue
        for td in root.iter("ThingDef"):
            ext = None
            for li in td.findall("modExtensions/li"):
                if li.get("Class") == "RimMandrake.Biomes.RM_CanopyExtension":
                    ext = li
            if ext is None:
                continue
            name = td.findtext("defName")
            found.append(name)
            tex_root = xml.parents[0]
            while tex_root.name != "Defs":
                tex_root = tex_root.parent
            tex_root = tex_root.parent / "Textures"
            whole = td.findtext("graphicData/texPath")
            vis = td.findtext("plant/visualSizeRange") or ""
            big = float(vis.split("~")[-1]) if vis else 0
            draw = float((td.findtext("graphicData/drawSize") or "1").strip("()").split(",")[0])
            scale = float(ext.findtext("canopyScale") or 1)
            base = letters(tex_root / whole, Path(whole).name)
            trunk_p, canopy_p = ext.findtext("trunkTexPath"), ext.findtext("canopyTexPath")
            tl = letters(tex_root / trunk_p, Path(trunk_p).name)
            cl = letters(tex_root / canopy_p, Path(canopy_p).name)
            check(td.findtext("graphicData/graphicClass") == "Graphic_Random" and base,
                  "C3 %s: whole pool is a Graphic_Random with %d letters" % (name, len(base or [])))
            check(tl == base, "C3 %s: trunk pool letters == whole pool letters (%s)" % (name, "".join(tl or [])))
            check(cl == base, "C3 %s: canopy pool letters == whole pool letters (%s)" % (name, "".join(cl or [])))
            want = int(round(big * draw * scale * art_px))
            sizes_c = {Image.open(tex_root / canopy_p / (Path(canopy_p).name + L + ".png")).size for L in cl or []}
            check(sizes_c == {(want, want)}, "C3 %s: canopy art %s == %d px (%.0f px/cell x %.1f cells)"
                  % (name, sorted(sizes_c), want, art_px, big * draw * scale))
            ok_t = all(Image.open(tex_root / trunk_p / (Path(trunk_p).name + L + ".png")).size
                       == Image.open(tex_root / whole / (Path(whole).name + L + ".png")).size for L in tl or [])
            check(bool(tl) and ok_t, "C3 %s: every trunk keeps its whole picture's canvas" % name)
            # the trunk really drops the crown: its opaque area is a minority of the whole picture's
            ratios = []
            for L in tl or []:
                ta = Image.open(tex_root / trunk_p / (Path(trunk_p).name + L + ".png")).getchannel("A")
                wa = Image.open(tex_root / whole / (Path(whole).name + L + ".png")).getchannel("A")
                ratios.append(sum(ta.point(lambda v: 255 if v > 128 else 0).histogram()[255:])
                              / max(1, sum(wa.point(lambda v: 255 if v > 128 else 0).histogram()[255:])))
            check(bool(ratios) and max(ratios) < 0.5 and min(ratios) > 0.05,
                  "C3 %s: trunks keep %.0f-%.0f%% of the whole tree's opaque area (crown dropped, bole kept)"
                  % (name, 100 * min(ratios or [0]), 100 * max(ratios or [0])))
    tiers = REPO / "Transient" / "biome_ffar" / "tree_tiers_sheet_2026-10-18.decisions.json"
    if tiers.is_file():
        import json
        titanic = sorted(k for k, v in json.loads(tiers.read_text())["decisions"].items()
                         if (v.get("q") or {}).get("tier") == "titanic")
        check(bool(titanic) and set(titanic) <= set(found),
              "C3 every Titanic of the owner's tier sheet carries the extension (titanic %s; carried by %s)"
              % (titanic, found))
    else:
        check("RM_SweetlineTree" in found, "C3 RM_SweetlineTree carries RM_CanopyExtension (carried by %s)" % found)
    m = re.search(r"^ART_PX_PER_CELL = (\d+)", ART_PY.read_text(encoding="utf-8"), re.M)
    check(m is not None and int(m.group(1)) == art_px,
          "C3 canopy_art.py ART_PX_PER_CELL (%s) == CanopyMath.ArtPxPerCell (%d)" % (m and m.group(1), art_px))


def c4():
    t = MOD_CS.read_text(encoding="utf-8")
    for f, d in (("canopyEnabled", "true"), ("canopyThresholdPx", "CanopyMath.DefaultThresholdPx"),
                 ("canopyFadePx", "CanopyMath.DefaultFadePx")):
        check(re.search(r"public static (bool|float) %s = %s;" % (f, re.escape(d)), t) is not None,
              "C4 setting %s defaults to %s" % (f, d))
        check('Scribe_Values.Look(ref %s, "%s", %s);' % (f, f, d) in t, "C4 setting %s is saved" % f)
    check("RM_Canopy.Reprint();" in t, "C4 a toggle reprints the running maps")
    check("CanopyMath.MinThresholdPx, CanopyMath.MaxThresholdPx" in t and "0f, CanopyMath.MaxFadePx" in t,
          "C4 sliders span the ranges C1 swept")


def c5():
    check('<Compile Include="RM_Canopy.cs" />' in CSPROJ.read_text(encoding="utf-8"), "C5 RM_Canopy.cs is compiled")
    stamp = STAMP.read_text(encoding="utf-8") if STAMP.is_file() else ""
    for f in ("RM_Canopy.cs", "RM_BiomesMod.cs"):
        h = hashlib.sha256((HERE / "Source" / f).read_bytes()).hexdigest()
        check(("%s %s" % (h, f)) in stamp, "C5 committed DLL stamp carries %s at its current hash" % f)
    dll = HERE / "Assemblies" / "RimMandrake.Biomes.dll"
    m = re.search(r"# dll: ([0-9a-f]{64})", stamp)
    check(m is not None and dll.is_file() and hashlib.sha256(dll.read_bytes()).hexdigest() == m.group(1),
          "C5 the DLL's own bytes match its stamp")


def main():
    text = CS.read_text(encoding="utf-8")
    check(const(text, "ArtPxPerCell") == 32, "C3 canopy art density is 32 px per cell (the item's ruling)")
    c12(text)
    c3(text)
    c4()
    c5()
    print("selftest_canopy: %s (%d failing)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
