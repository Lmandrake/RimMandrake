#!/usr/bin/env python3
"""Selftest for SEABED_DESCENT_ASCENT_1: the Verse glue around the depth-fuel kernel, offline.

selftest_divinginteraction_fuzz.py (family 'descent') proves RM_SeabedDescentKernel.ExtraFuel. It never sees the
code that makes the game call it, so a broken wire there stays green. This test reads that wire from the source
and the committed DLL stamp and requires, for "fuel cost per depth both ways":

  1. Patch_SeabedDescentFuel.cs is a Harmony postfix on GravshipUtility.TryGetPathFuelCost, in the namespace
     RM_DivingSettings hands to PatchApplier.Apply, that adds (+=, never =) to the out cost only when the vanilla
     result is true and the setting is on;
  2. its ExtraFor reads the FLOOR end's elevation (floorEnd = fromFloor ? from : to), so the climb pays the same
     depth as the descent, and passes the four end flags in the kernel's order with the settings' per-metre value;
  3. RM_DivingSettings ships the feature ON at the kernel's default rate (field initialisers and Scribe defaults);
  4. RM_SeabedLayer.cs adds the surface->floor AND floor->surface layer connections (the console's
     TryGetPathFuelCost refuses a pair with no connection);
  5. RM_DivingInteraction.csproj compiles the patch and the kernel; the fuzz csproj compiles the kernel;
  6. the committed DLL's .srchash records those exact source bytes, and its "# dll:" line is the DLL's own sha256,
     so the shipped assembly carries this source;
  7. the bridge surface the live proof (prove_seabed_descent.py) drives still reaches the floor layer:
     tool_schemas.json lists 'layer' on jawa/gravship_launch and jawa/gravship_launch_check, the C# tools take
     `string layer`, jawa/gravship_status reports currentMapLayer/currentMapParent/currentMapTile, and the proof
     script passes layer= to both and reads currentMapLayer (gen 6: another item's schema edit sent the build back
     stale; this check is what says the edit left the descent's tools whole).

Then it runs the same checker on mutated copies (one per gap) and requires each to fail, so a green run proves the
checker can see each gap.

Usage: selftest_seabed_descent_wiring.py [--root <repo>]   (default: this file's repo)
"""
import hashlib
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MOD = os.path.join("src", "RimMandrake", "DivingInteraction")
SRC = os.path.join(MOD, "Source")
PATCH = os.path.join(SRC, "Patch_SeabedDescentFuel.cs")
KERNEL = os.path.join(SRC, "RM_SeabedDescentKernel.cs")
SETTINGS = os.path.join(SRC, "RM_DivingSettings.cs")
LAYER = os.path.join(SRC, "RM_SeabedLayer.cs")
CSPROJ = os.path.join(SRC, "RM_DivingInteraction.csproj")
FUZZ_CSPROJ = os.path.join(SRC, "SelfTest", "RimMandrakeDiving.SelfTest.csproj")
DLL = os.path.join(MOD, "Assemblies", "RimMandrake.DivingInteraction.dll")
STAMP = DLL + ".srchash"
SCHEMAS = os.path.join("src", "RimMandrake", "Utils", "northstar_driver", "tool_schemas.json")
GRAV_TOOLS = os.path.join("src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools", "JawaBenchGravshipTools.cs")
PROVE = os.path.join("src", "RimMandrake", "bridgetools", "prove_seabed_descent.py")
FILES = (PATCH, KERNEL, SETTINGS, LAYER, CSPROJ, FUZZ_CSPROJ, DLL, STAMP, SCHEMAS, GRAV_TOOLS, PROVE)


def _read(root, rel):
    with open(os.path.join(root, rel), "rb") as f:
        return f.read()


def _txt(root, rel):
    return _read(root, rel).decode("utf-8", "replace")


def _squash(s):
    """Whitespace-insensitive form for matching one statement."""
    return re.sub(r"\s+", "", s)


def _strip_comments(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def check(root):
    fails = []
    for rel in FILES:
        if not os.path.isfile(os.path.join(root, rel)):
            fails.append("missing " + rel)
    if fails:
        return fails

    patch = _squash(_strip_comments(_txt(root, PATCH)))
    settings_raw = _strip_comments(_txt(root, SETTINGS))
    settings = _squash(settings_raw)

    # 1. the postfix
    m = re.search(r'PatchApplier\.Apply\(newHarmony\("[^"]+"\),typeof\(RM_DivingSettings\)\.Assembly,"([^"]+)"\)', settings)
    ns = m.group(1) if m else None
    if not ns:
        fails.append("1: RM_DivingSettings does not apply Harmony patches through PatchApplier with a namespace")
    elif ("namespace" + ns + "{") not in patch:
        fails.append("1: the patch is not in namespace %s, which PatchApplier.Apply patches" % ns)
    if "[HarmonyPatch(typeof(GravshipUtility),nameof(GravshipUtility.TryGetPathFuelCost))]publicstaticclassPatch_SeabedDescentFuel" not in patch:
        fails.append("1: Patch_SeabedDescentFuel is not a [HarmonyPatch] on GravshipUtility.TryGetPathFuelCost")
    if "publicstaticvoidPostfix(PlanetTilefrom,PlanetTileto,reffloatcost,bool__result)" not in patch:
        fails.append("1: no Postfix(PlanetTile from, PlanetTile to, ref float cost, bool __result)")
    if "if(!__result||!RM_DivingSettings.seabedDescentDepthFuelEnabled)return;" not in patch:
        fails.append("1: the postfix does not return early on a refused path or the setting off")
    if "cost+=ExtraFor(from,to);" not in patch:
        fails.append("1: the postfix does not ADD the depth fuel to the vanilla cost")

    # 2. the floor end and the kernel call
    if "PlanetTilefloorEnd=fromFloor?from:to;" not in patch:
        fails.append("2: ExtraFor does not take the floor end (fromFloor ? from : to) for the depth")
    if "floorEnd.Tile.elevation" not in patch:
        fails.append("2: ExtraFor does not read the floor end's elevation")
    if "boolfromFloor=RM_SeabedLayerUtility.IsSeabedTile(from);" not in patch or "booltoFloor=RM_SeabedLayerUtility.IsSeabedTile(to);" not in patch:
        fails.append("2: fromFloor/toFloor are not RM_SeabedLayerUtility.IsSeabedTile of from/to")
    if "boolfromSurface=from.Layer==surface;" not in patch or "booltoSurface=to.Layer==surface;" not in patch:
        fails.append("2: fromSurface/toSurface are not from.Layer/to.Layer == the surface layer")
    if "RM_SeabedDescentKernel.ExtraFuel(fromFloor,fromSurface,toFloor,toSurface,elevation,RM_DivingSettings.seabedDescentFuelPerMeter)" not in patch:
        fails.append("2: ExtraFor does not call ExtraFuel(fromFloor, fromSurface, toFloor, toSurface, elevation, setting)")
    kern = _squash(_strip_comments(_txt(root, KERNEL)))
    if "publicstaticfloatExtraFuel(boolfromFloor,boolfromSurface,booltoFloor,booltoSurface,floatfloorEndElevation,floatfuelPerMeter)" not in kern:
        fails.append("2: the kernel's ExtraFuel signature is not (fromFloor, fromSurface, toFloor, toSurface, elevation, perMetre)")

    # 3. shipped defaults
    if "publicstaticboolseabedDescentDepthFuelEnabled=true;" not in settings:
        fails.append("3: seabedDescentDepthFuelEnabled does not ship true")
    if "publicstaticfloatseabedDescentFuelPerMeter=RM_SeabedDescentKernel.DefaultFuelPerMeter;" not in settings:
        fails.append("3: seabedDescentFuelPerMeter does not ship at the kernel default")
    if 'Scribe_Values.Look(refseabedDescentDepthFuelEnabled,"seabedDescentDepthFuelEnabled",true);' not in settings:
        fails.append("3: the saved default of seabedDescentDepthFuelEnabled is not true")
    if 'Scribe_Values.Look(refseabedDescentFuelPerMeter,"seabedDescentFuelPerMeter",RM_SeabedDescentKernel.DefaultFuelPerMeter);' not in settings:
        fails.append("3: the saved default of seabedDescentFuelPerMeter is not the kernel default")
    dm = re.search(r"publicconstfloatDefaultFuelPerMeter=([0-9.]+)f;", kern)
    if not dm or float(dm.group(1)) <= 0:
        fails.append("3: the kernel's DefaultFuelPerMeter is not a positive rate")

    # 4. both layer connections
    layer = _squash(_strip_comments(_txt(root, LAYER)))
    if "surface.AddConnection(layer," not in layer:
        fails.append("4: no surface -> sea-floor layer connection")
    if "layer.AddConnection(surface," not in layer:
        fails.append("4: no sea-floor -> surface layer connection (the climb would be refused)")

    # 5. compiled
    csproj = _txt(root, CSPROJ)
    for name in ("Patch_SeabedDescentFuel.cs", "RM_SeabedDescentKernel.cs", "RM_SeabedLayer.cs", "RM_DivingSettings.cs"):
        if not re.search(r'<Compile\s+Include="%s"\s*/>' % re.escape(name), csproj):
            fails.append("5: RM_DivingInteraction.csproj does not compile " + name)
    if not re.search(r'<Compile\s+Include="\.\.\\RM_SeabedDescentKernel\.cs"\s*/>', _txt(root, FUZZ_CSPROJ)):
        fails.append("5: the fuzz csproj does not compile the production kernel")

    # 6. the committed DLL carries this source
    stamp = _txt(root, STAMP)
    recorded = {}
    dll_hash = None
    for line in stamp.splitlines():
        line = line.strip()
        if line.startswith("# dll:"):
            dll_hash = line.split(":", 1)[1].strip()
        elif line and not line.startswith("#"):
            h, _, name = line.partition(" ")
            recorded[name.strip()] = h
    for rel in (PATCH, KERNEL, SETTINGS, LAYER):
        name = os.path.basename(rel)
        want = hashlib.sha256(_read(root, rel)).hexdigest()
        if recorded.get(name) != want:
            fails.append("6: the DLL stamp records %s as %s, the source is %s (DLL not rebuilt from it)" % (
                name, recorded.get(name), want))
    if not dll_hash or hashlib.sha256(_read(root, DLL)).hexdigest() != dll_hash:
        fails.append("6: the committed DLL's bytes are not the ones its stamp records")

    # 7. the bridge tools the live proof drives can still name the floor layer
    import json
    try:
        tools = json.loads(_txt(root, SCHEMAS)).get("tools") or {}
    except ValueError as e:
        tools = {}
        fails.append("7: tool_schemas.json does not parse: %s" % e)
    for name in ("jawa/gravship_launch", "jawa/gravship_launch_check", "jawa/gravship_status", "jawa/gravship_land"):
        if name not in tools:
            fails.append("7: tool_schemas.json has no %s" % name)
    for name in ("jawa/gravship_launch", "jawa/gravship_launch_check"):
        if "layer" not in ((tools.get(name) or {}).get("parameters") or []):
            fails.append("7: tool_schemas.json: %s takes no 'layer' parameter" % name)
    cs = _strip_comments(_txt(root, GRAV_TOOLS))
    for meth in ("GravshipLaunchCheck", "GravshipLaunch"):
        m = re.search(r"public\s+static\s+async\s+Task<object>\s+%s\s*\((.*?)\)\s*\{" % meth, cs, re.S)
        if not m or not re.search(r"\bstring\s+layer\b", m.group(1)):
            fails.append("7: %s takes no `string layer` parameter" % meth)
    if not re.search(r"\bResolveTargetTile\s*\(\s*\w+\s*,\s*layer\b", cs):
        fails.append("7: no tool resolves its target through ResolveTargetTile(tile, layer, ...)")
    for field in ("currentMapLayer", "currentMapParent", "currentMapTile"):
        if not re.search(r"\b%s\s*=" % field, cs):
            fails.append("7: jawa/gravship_status does not report %s" % field)
    prove = _txt(root, PROVE)
    for name in ("jawa/gravship_launch", "jawa/gravship_launch_check"):
        if not re.search(r'call\("%s",[^)]*\blayer=' % re.escape(name), prove):
            fails.append("7: prove_seabed_descent.py never calls %s with layer=" % name)
    if 'get("currentMapLayer")' not in prove:
        fails.append("7: prove_seabed_descent.py never reads currentMapLayer")
    return fails


# Each mutant: (what it breaks, file, old, new). Every one must turn the checker red.
MUTANTS = [
    ("floor end taken from the surface on the climb", PATCH, "fromFloor ? from : to", "to"),
    ("cost overwritten instead of added", PATCH, "cost += ExtraFor", "cost = ExtraFor"),
    ("postfix ignores a refused path", PATCH, "!__result || ", ""),
    ("patch attribute dropped", PATCH, "[HarmonyPatch(typeof(GravshipUtility), nameof(GravshipUtility.TryGetPathFuelCost))]", ""),
    ("patch aimed at another method", PATCH, "nameof(GravshipUtility.TryGetPathFuelCost)", "nameof(GravshipUtility.MaxDistForFuel)"),
    ("kernel flags passed out of order", PATCH, "ExtraFuel(fromFloor, fromSurface, toFloor, toSurface,", "ExtraFuel(fromFloor, toFloor, fromSurface, toSurface,"),
    ("per-metre setting not passed", PATCH, "RM_DivingSettings.seabedDescentFuelPerMeter)", "0f)"),
    ("feature ships off", SETTINGS, "seabedDescentDepthFuelEnabled = true;", "seabedDescentDepthFuelEnabled = false;"),
    ("saved default off", SETTINGS, '"seabedDescentDepthFuelEnabled", true)', '"seabedDescentDepthFuelEnabled", false)'),
    ("climb connection missing", LAYER, "layer.AddConnection(surface, 0f);", ";"),
    ("descent connection missing", LAYER, "surface.AddConnection(layer, 0f);", ";"),
    ("patch not compiled", CSPROJ, '<Compile Include="Patch_SeabedDescentFuel.cs" />', ""),
    ("schema drops layer from the launch", SCHEMAS, '"expectEngineId",\n    "layer",\n    "quality",', '"expectEngineId",\n    "quality",'),
    ("schema drops layer from the launch check", SCHEMAS, '"expectEngineId",\n    "layer",\n    "targetTile"', '"expectEngineId",\n    "targetTile"'),
    ("schema loses gravship_status", SCHEMAS, '"jawa/gravship_status"', '"jawa/gravship_status_gone"'),
    ("C# launch check drops its layer parameter", GRAV_TOOLS, 'Optional when only one engine exists.")] string expectEngineId = null,\n            [ToolParameter(Description = "SEABED_DESCENT_ASCENT_1: PlanetLayerDef defName of the destination layer (e.g. RM_SeabedLayer, Orbit). Empty = the surface.")] string layer = null)\n        {', 'Optional when only one engine exists.")] string expectEngineId = null)\n        {'),
    ("status stops reporting the map layer", GRAV_TOOLS, "currentMapLayer = ", "currentMapLayerGone = "),
    ("status stops reporting the map parent", GRAV_TOOLS, "currentMapParent = ", "currentMapParentGone = "),
    ("proof launches without a layer", PROVE, 'call("jawa/gravship_launch", targetTile=target, layer=layer,', 'call("jawa/gravship_launch", targetTile=target,'),
    ("fuzz tests a copy, not the kernel", FUZZ_CSPROJ, '<Compile Include="..\\RM_SeabedDescentKernel.cs" />', ""),
]


def _mutant_copy(root, tmp, rel, old, new):
    for f in FILES:
        dst = os.path.join(tmp, f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(root, f), dst)
    path = os.path.join(tmp, rel)
    with open(path, "rb") as f:
        data = f.read().decode("utf-8")
    if old not in data:
        return False
    with open(path, "wb") as f:
        f.write(data.replace(old, new, 1).encode("utf-8"))
    return True


def main(argv):
    root = DEFAULT_REPO
    if "--root" in argv:
        root = os.path.abspath(argv[argv.index("--root") + 1])
    fails = check(root)
    for f in fails:
        print("FAIL", f)
    bad = len(fails)
    # A mutant must stay red even after the stamp is regenerated to match it: re-stamp the copy so check 6 alone
    # cannot be what catches it (the stamp-only mutant below covers check 6).
    for what, rel, old, new in MUTANTS:
        with tempfile.TemporaryDirectory() as tmp:
            if not _mutant_copy(root, tmp, rel, old, new):
                print("FAIL mutant '%s': its anchor text is gone from %s; update the mutant" % (what, rel))
                bad += 1
                continue
            _restamp(tmp)
            got = check(tmp)
            if got:
                print("ok   mutant '%s' -> %s" % (what, got[0]))
            else:
                print("FAIL mutant '%s' passed the checker" % what)
                bad += 1
    with tempfile.TemporaryDirectory() as tmp:
        _mutant_copy(root, tmp, PATCH, "cost += ExtraFor", "cost += 2f * ExtraFor")
        got = [g for g in check(tmp) if g.startswith("6:")]
        print(("ok   mutant 'source edited, DLL not rebuilt' -> %s" % got[0]) if got else "FAIL mutant 'source edited, DLL not rebuilt' passed")
        bad += 0 if got else 1
    with tempfile.TemporaryDirectory() as tmp:
        _mutant_copy(root, tmp, KERNEL, "", "")   # a plain copy
        with open(os.path.join(tmp, DLL), "ab") as f:
            f.write(b"\0")
        got = [g for g in check(tmp) if g.startswith("6:")]
        print(("ok   mutant 'DLL bytes swapped' -> %s" % got[0]) if got else "FAIL mutant 'DLL bytes swapped' passed")
        bad += 0 if got else 1
    print("selftest_seabed_descent_wiring: %s (%d real-tree failures, %d mutants)" % (
        "PASS" if bad == 0 else "FAIL", len(fails), len(MUTANTS) + 2))
    return 0 if bad == 0 else 1


def _restamp(tmp):
    """Rewrite the copy's stamp so it matches the copy's sources and DLL: a mutant is then caught by its own check."""
    path = os.path.join(tmp, STAMP)
    lines = _txt(tmp, STAMP).splitlines()
    out = []
    for line in lines:
        s = line.strip()
        if s.startswith("# dll:"):
            out.append("# dll: " + hashlib.sha256(_read(tmp, DLL)).hexdigest())
            continue
        if s and not s.startswith("#"):
            h, _, name = s.partition(" ")
            for rel in (PATCH, KERNEL, SETTINGS, LAYER):
                if os.path.basename(rel) == name.strip():
                    h = hashlib.sha256(_read(tmp, rel)).hexdigest()
            out.append(h + " " + name.strip())
            continue
        out.append(line)
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
