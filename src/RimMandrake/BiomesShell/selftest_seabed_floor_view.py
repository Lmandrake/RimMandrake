#!/usr/bin/env python3
"""Selftest for SEABED_LAYER_DESIGN_ITS_OWN_SEA_FLOOR: the sea-floor layer is drawn on its own, with a real icon.

The need (world look 2, owner 2026-10-24: "get the water right too, then the sea floors on their own layers"): the
floor view was bare faces with hard hex edges, because RM_WorldLook drew only on the root surface, and its view
gizmo was vanilla's PlaceholderImage.

What this reads (the shipped sources and defs; constants parsed, so it cannot drift):
  S1 RM_WorldLook.Wrap draws on the floor layer (IsSeabedLayer: PlanetLayerDef "RM_SeabedLayer") while
     worldSeabedShading is on, and on the root surface as before.
  S2 the floor branch builds BuildSeabed and, with soft borders on, BuildBlend; never the surface's sea films,
     swirls, glass or decals.
  S3 BuildSeabed keys each floor tile on its land-layer twin (Find.WorldGrid.Surface, same tile count): under water a
     depth film rising with BuildCoastField's coast distance over seabedDepthTiles; under dry land a flat dim film.
  S4 the switch worldSeabedShading: public static bool, default true, scribed true, reset to true, in the redraw key,
     drawn as a checkbox.
  S5 DivingInteraction's PlanetLayerDef RM_SeabedLayer (the name S1 reads) shows UI/Commands/RM_ViewSeaFloor, a
     texture git tracks in DivingInteraction/Textures; not PlaceholderImage.
  S6 the committed RimMandrake.Biomes.dll is built from RM_WorldLook.cs and RM_BiomesMod.cs (.srchash).
Not read: the look on screen (a judge's call, by the shaped route) and the floor's own faces per sea.
Named mutants must each turn it red, or the check is blind.

  python3 src/RimMandrake/BiomesShell/selftest_seabed_floor_view.py            the shipped files
  python3 src/RimMandrake/BiomesShell/selftest_seabed_floor_view.py --rev REV  the files at a git revision
"""
import hashlib, os, re, subprocess, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../.."))
LOOK = "src/RimMandrake/BiomesShell/Source/RM_WorldLook.cs"
MOD = "src/RimMandrake/BiomesShell/Source/RM_BiomesMod.cs"
SRCHASH = "src/RimMandrake/BiomesShell/Assemblies/RimMandrake.Biomes.dll.srchash"
LAYER = "src/RimMandrake/DivingInteraction/Defs/PlanetLayerDefs/RM_SeabedLayer.xml"
TEX_ROOT = "src/RimMandrake/DivingInteraction/Textures/"


def body(text, signature_re):
    m = re.search(signature_re, text)
    if not m:
        return None
    i = text.index("{", m.end())
    depth = 0
    for j in range(i, len(text)):
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        if depth == 0:
            return text[i:j + 1]
    return None


def check(look, mod, layer_xml, tracked, srchash, look_b, mod_b):
    errs = []
    wrap = body(look, r"static IEnumerable Wrap\(IEnumerable inner, WorldDrawLayer_Terrain layer\)") or ""
    if not re.search(r'public static bool IsSeabedLayer\(PlanetLayer pl\) => pl\?\.Def != null && pl\.Def\.defName == "RM_SeabedLayer";', look):
        errs.append("S1 IsSeabedLayer does not name the PlanetLayerDef RM_SeabedLayer")
    if "bool floor = IsSeabedLayer(layer.planetLayer);" not in wrap or \
            "if (!layer.planetLayer.IsRootSurface && !(floor && RM_BiomesSettings.worldSeabedShading)) yield break;" not in wrap:
        errs.append("S1 Wrap does not draw on the floor layer behind worldSeabedShading (it stops at the root surface)")
    fb = wrap.split("if (floor)", 1)[-1].split("else", 1)[0] if "if (floor)" in wrap else ""
    if "BuildSeabed(layer, mine)" not in fb or "if (RM_BiomesSettings.worldBorderBlend)" not in fb or "BuildBlend(layer, mine)" not in fb:
        errs.append("S2 the floor branch does not build BuildSeabed and the soft borders")
    for other in ("BuildSea(", "BuildSwirls(", "RM_WorldDecals.Build("):
        if other in fb:
            errs.append("S2 the floor branch builds %s (a surface layer)" % other.rstrip("("))
    sb = body(look, r"static string BuildSeabed\(WorldDrawLayer_Terrain layer, List<LayerSubMesh> mine\)") or ""
    if not sb:
        errs.append("S3 BuildSeabed not found")
    else:
        if "Find.WorldGrid?.Surface" not in sb or "surf.TilesCount != pl.TilesCount" not in sb:
            errs.append("S3 BuildSeabed does not key on the land-layer twin of the same tiles")
        if "BuildCoastField(pl, wet," not in sb or "d / Mathf.Max(0.01f, seabedDepthTiles)" not in sb:
            errs.append("S3 the basin film is not keyed on the coast distance over seabedDepthTiles")
        if "d => seabedLandAlpha" not in sb:
            errs.append("S3 the floor under dry land gets no flat dim film")
    for name, default in (("worldSeabedShading", "true"),):
        if not re.search(r"public static bool %s = %s;" % (name, default), mod):
            errs.append("S4 %s is not a public static bool, default %s" % (name, default))
        if 'Scribe_Values.Look(ref %s, "%s", %s);' % (name, name, default) not in mod:
            errs.append("S4 %s is not scribed with default %s" % (name, default))
        reset = body(mod, r"public static void ResetWorldLook\(\)") or ""
        if "%s = %s;" % (name, default) not in reset:
            errs.append("S4 ResetWorldLook does not reset %s" % name)
        key = mod.split("static string WorldLookKey() =>", 1)[-1].split(";", 1)[0]
        if "RM_BiomesSettings.%s" % name not in key:
            errs.append("S4 %s is not in the redraw key (a flip would not redraw)" % name)
        if "ref RM_BiomesSettings.%s," % name not in mod:
            errs.append("S4 %s is not drawn as a checkbox" % name)
    try:
        root = ET.fromstring(layer_xml)
    except ET.ParseError as e:
        return errs + ["S5 %s does not parse: %s" % (LAYER, e)]
    ld = [d for d in root.findall("PlanetLayerDef") if d.findtext("defName") == "RM_SeabedLayer"]
    if not ld:
        errs.append("S5 no PlanetLayerDef RM_SeabedLayer: the floor branch would never fire")
    else:
        tex = (ld[0].findtext("viewGizmoTexPath") or "").strip()
        if tex in ("", "PlaceholderImage"):
            errs.append("S5 the view gizmo is still %r" % (tex or "empty"))
        elif TEX_ROOT + tex + ".png" not in tracked:
            errs.append("S5 the view gizmo %s has no tracked texture %s%s.png" % (tex, TEX_ROOT, tex))
    for name, b in (("RM_WorldLook.cs", look_b), ("RM_BiomesMod.cs", mod_b)):
        line = [l for l in srchash.splitlines() if l.endswith(" " + name)]
        if not line:
            errs.append("S6 srchash has no %s line" % name)
        elif line[0].split()[0] != hashlib.sha256(b).hexdigest():
            errs.append("S6 RimMandrake.Biomes.dll is not built from this %s (srchash stale): run winbuild.py BiomesShell" % name)
    return errs


def read(rev, path):
    if rev:
        return subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (rev, path)], capture_output=True, check=True).stdout
    with open(os.path.join(REPO, path), "rb") as fh:
        return fh.read()


def tracked_textures(rev):
    if rev:
        out = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", rev, TEX_ROOT], capture_output=True, text=True).stdout
    else:
        out = subprocess.run(["git", "-C", REPO, "ls-files", "--cached", "--others", "--exclude-standard", TEX_ROOT],
                             capture_output=True, text=True).stdout
    return set(out.split())


def main(argv):
    rev = argv[argv.index("--rev") + 1] if "--rev" in argv else None
    look_b, mod_b, sh_b, layer_b = (read(rev, p) for p in (LOOK, MOD, SRCHASH, LAYER))
    look, mod, sh, layer = (b.decode("utf-8-sig") for b in (look_b, mod_b, sh_b, layer_b))
    tracked = tracked_textures(rev)
    errs = check(look, mod, layer, tracked, sh, look_b, mod_b)
    if not rev:
        mutants = {
            "root surface only (the parent)": (look.replace("if (!layer.planetLayer.IsRootSurface && !(floor && RM_BiomesSettings.worldSeabedShading)) yield break;",
                                                            "if (!layer.planetLayer.IsRootSurface) yield break;"), mod, layer),
            "floor draws the sea films": (look.replace("sb.Append(BuildSeabed(layer, mine));", "sb.Append(BuildSea(layer, mine));"), mod, layer),
            "no land mask": (look.replace("d => seabedLandAlpha", "d => 0f"), mod, layer),
            "switch not in the redraw key": (look, mod.replace("+ RM_BiomesSettings.worldSeabedShading + \"/\"", ""), layer),
            "placeholder icon back": (look, mod, layer.replace("UI/Commands/RM_ViewSeaFloor</viewGizmoTexPath>", "PlaceholderImage</viewGizmoTexPath>")),
            "layer renamed": (look, mod, layer.replace("<defName>RM_SeabedLayer</defName>", "<defName>RM_SeaFloorLayer</defName>")),
        }
        for name, (lk, md, ly) in mutants.items():
            if (lk, md, ly) == (look, mod, layer):
                errs.append("mutant '%s' did not apply (the source moved; update the mutant)" % name)
            elif not check(lk, md, ly, tracked, sh, look_b, mod_b):
                errs.append("mutant '%s' stayed green: the check is blind" % name)
        if not check(look, mod, layer, tracked, sh, look_b + b"\n// edit", mod_b):
            errs.append("mutant 'stale srchash' stayed green: the check is blind")
    for e in errs:
        print("FAIL:", e)
    if errs:
        return 1
    print("OK the sea floor is drawn on its own (basins by coast distance, continents above dimmed, soft borders), "
          "behind 'Planet: sea-floor shading'; icon UI/Commands/RM_ViewSeaFloor; DLL srchash matches; 7 mutants red")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
