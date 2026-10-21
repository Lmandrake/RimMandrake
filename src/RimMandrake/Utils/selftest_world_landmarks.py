#!/usr/bin/env python3
"""Offline check for the soft landmark icons (RM_WorldLandmarks.cs, LANDMARK_ICONS_DECIDE_THE_REAL_SPECKLE).

Checks: every soft-landmark setting is a static field whose initialiser equals its Scribe default and is drawn on the
settings screen; the csproj compiles RM_WorldLandmarks.cs; the patches target WorldDrawLayer_Landmarks.Regenerate and the
WorldDrawLayerBase.Alpha getter; the Regenerate wrapper lets vanilla run first; the file never writes world data
(look-only, owner by card 2026-10-20). Then plants one defect per check and requires each to be caught.

    python3 src/RimMandrake/Utils/selftest_world_landmarks.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL = os.path.join(ROOT, "BiomesShell", "Source")
SETTINGS = ["worldSoftLandmarks", "worldLandmarkSize", "worldLandmarkOpacity", "worldLandmarksFullClose"]
WORLD_WRITES = re.compile(r"landmarks\s*\.\s*(Add|Remove|landmarks\s*\[)|\.landmarks\s*\[[^\]]*\]\s*=|SetLandmark|hilliness\s*=")


def check(mod, look, proj):
    errs = []
    for s in SETTINGS:
        init = re.search(r"public static (?:bool|float) " + s + r"\s*=\s*([^;]+);", mod)
        scribe = re.search(r'Scribe_Values\.Look\(ref ' + s + r', "' + s + r'", ([^)]+)\)', mod)
        if not init or not scribe:
            errs.append(s + ": not a Scribed static field"); continue
        if init.group(1).strip() != scribe.group(1).strip():
            errs.append(s + ": initialiser %s != Scribe default %s" % (init.group(1).strip(), scribe.group(1).strip()))
        draw = mod.split("DoSettingsWindowContents", 1)[-1]
        if "RM_BiomesSettings." + s not in draw:
            errs.append(s + ": not drawn on the settings screen")
    if '<Compile Include="RM_WorldLandmarks.cs" />' not in proj:
        errs.append("csproj does not compile RM_WorldLandmarks.cs")
    if not re.search(r'typeof\(WorldDrawLayer_Landmarks\), "Regenerate"', look):
        errs.append("no patch on WorldDrawLayer_Landmarks.Regenerate")
    if not re.search(r'PropertyGetter\(typeof\(WorldDrawLayerBase\), "Alpha"\)', look):
        errs.append("no patch on the WorldDrawLayerBase.Alpha getter")
    wrap = look.split("static IEnumerable Wrap", 1)[-1]
    if not re.match(r"[^{]*\{\s*foreach \(object o in inner\) yield return o;", wrap):
        errs.append("Regenerate wrapper does not run vanilla first")
    if WORLD_WRITES.search(look):
        errs.append("writes world data (must be look-only)")
    return errs


def main():
    mod = open(os.path.join(SHELL, "RM_BiomesMod.cs"), encoding="utf-8").read()
    look = open(os.path.join(SHELL, "RM_WorldLandmarks.cs"), encoding="utf-8").read()
    proj = open(os.path.join(SHELL, "RM_Biomes.csproj"), encoding="utf-8").read()
    n = ok = 0
    errs = check(mod, look, proj)
    n += 1; ok += not errs
    print(("ok  " if not errs else "FAIL") + " live source" + ("" if not errs else ": " + "; ".join(errs)))
    plants = [
        ("default drift", mod.replace('"worldLandmarkSize", 0.6f', '"worldLandmarkSize", 0.7f'), look, proj),
        ("undrawn slider", mod.replace("ref RM_BiomesSettings.worldLandmarksFullClose", "ref dummy"), look, proj),
        ("csproj missing", mod, look, proj.replace('<Compile Include="RM_WorldLandmarks.cs" />', "")),
        ("no Alpha patch", mod, look.replace('PropertyGetter(typeof(WorldDrawLayerBase), "Alpha")', 'Method(typeof(X), "Y")'), proj),
        ("vanilla not first", mod, look.replace("foreach (object o in inner) yield return o;", "yield break;"), proj),
        ("world write", mod, look + "\n// Find.World.landmarks.Remove(tile);\n", proj),
    ]
    for name, m, l, p in plants:
        n += 1
        caught = bool(check(m, l, p))
        ok += caught
        print(("ok  " if caught else "FAIL") + " plant: " + name + (" is caught" if caught else " NOT caught"))
    print("world landmarks selftest: %d/%d ok" % (ok, n))
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
