#!/usr/bin/env python3
"""Offline proof for WORLD_PATHS_VERIFY_WATER_FINALLY_WET: roads never read as water, rivers are water.

Owner 2026-10-20: "Strangely I see what looks like a blue road on the Scald's shore towards the Anvil. Looks like a
river, but it isn't. And the river is shown brown and red."

Checks, against the source AND the deployed game copy:
  1. no road layer in RM_WorldPaths.LayerColor is blue or teal (b never above r); Stone is grey-brown (r >= g >= b);
  2. the fallback river water (RM_WorldPaths.riverWater) and FlowWorks' default waterColor are blue (b largest);
  3. the FlowWorks river tint switch names exactly RM_Contagion, RM_Miasma, RM_Wastes, RM_RustCathedral, each a real
     BiomeDef in src/, and every other tile falls to the default water colour;
  4. the deployed RimMandrake.Biomes.dll carries the river restyle (RM_RiverWater) and the deployed
     RimMandrakeFlowWorks.dll carries all four tint defNames (UTF-16 user strings).
Exit 0 = all hold, 1 = a check failed, 2 = UNMEASURED (a file is missing).
A biome of ours on 0 tiles is expected (owner 2026-09-20); this proof never counts tiles.
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
SRC = os.path.join(ROOT, "src")
PATHS_CS = os.path.join(SRC, "RimMandrake/BiomesShell/Source/RM_WorldPaths.cs")
TINT_CS = os.path.join(SRC, "RimMandrake/FlowWorks/Source/RiverColors/RM_RiverColors.cs")
SETTINGS_CS = os.path.join(SRC, "RimMandrake/FlowWorks/Source/RiverColors/RM_RiverColorsSettings.cs")
GAME_MODS = os.environ.get("RIMWORLD_MODS", "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods")
DEPLOYED = {
    os.path.join(GAME_MODS, "RimMandrake.Biomes/Assemblies/RimMandrake.Biomes.dll"): ["RM_RiverWater", "RM_RiverBank"],
    os.path.join(GAME_MODS, "FlowWorks/Assemblies/RimMandrakeFlowWorks.dll"):
        ["RM_Contagion", "RM_Miasma", "RM_Wastes", "RM_RustCathedral"],
}
TINTED = {"RM_Contagion", "RM_Miasma", "RM_Wastes", "RM_RustCathedral"}

fails, unmeasured = [], []


def check(ok, what):
    print(("PASS  " if ok else "FAIL  ") + what)
    if not ok:
        fails.append(what)


def read(path):
    if not os.path.isfile(path):
        unmeasured.append(path)
        print("UNMEASURED  missing " + path)
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    paths, tint, settings = read(PATHS_CS), read(TINT_CS), read(SETTINGS_CS)
    if paths:
        block = re.search(r"LayerColor\s*=\s*new Dictionary<string, Color>\s*\{(.*?)\};", paths, re.S)
        layers = {m.group(1): tuple(float(v) for v in m.group(2, 3, 4)) for m in re.finditer(
            r'\{\s*"(\w+)",\s*new Color\(([\d.]+)f,\s*([\d.]+)f,\s*([\d.]+)f\)\s*\}', block.group(1) if block else "")}
        check(set(layers) == {"Outline", "Dirt", "Stone", "Gravel", "Asphalt"},
              "RM_WorldPaths.LayerColor sets the five road layers: %s" % sorted(layers))
        for name, (r, g, b) in sorted(layers.items()):
            check(b <= r + 0.01, "road layer %s %s is not blue/teal (b <= r)" % (name, (r, g, b)))
        st = layers.get("Stone")
        check(bool(st) and st[0] >= st[1] >= st[2], "Stone road %s is grey-brown (r >= g >= b)" % (st,))
        m = re.search(r"riverWater\s*=\s*new Color32\((\d+),\s*(\d+),\s*(\d+)", paths)
        rw = tuple(int(v) for v in m.groups()) if m else None
        check(bool(rw) and rw[2] > rw[1] > rw[0], "fallback river water %s is blue" % (rw,))
    if settings:
        m = re.search(r"waterColor\s*=\s*new Color\(([\d.]+)f,\s*([\d.]+)f,\s*([\d.]+)f\)", settings)
        wc = tuple(float(v) for v in m.groups()) if m else None
        check(bool(wc) and wc[2] > wc[1] > wc[0], "FlowWorks default river waterColor %s is blue" % (wc,))
    if tint:
        body = re.search(r"ColorFor\(PlanetTile tile\)(.*?)\n        \}", tint, re.S)
        body = body.group(1) if body else ""
        cases = set(re.findall(r'case "(\w+)":', body))
        check(cases == TINTED, "river tint switch names exactly the four story biomes: %s" % sorted(cases))
        check(re.search(r"default:\s*return RM_RiverColorsSettings\.waterColor", body) is not None,
              "every other biome falls to the default water colour")
        defs = set()
        for dp, _, fs in os.walk(SRC):
            for f in fs:
                if f.endswith(".xml") and "BiomeDef" in dp:
                    with open(os.path.join(dp, f), encoding="utf-8", errors="replace") as h:
                        defs.update(re.findall(r"<defName>(\w+)</defName>", h.read()))
        for b in sorted(TINTED):
            check(b in defs, "%s is a real BiomeDef under src/ (BiomeDefs folder)" % b)
    for dll, needles in DEPLOYED.items():
        if not os.path.isfile(dll):
            unmeasured.append(dll)
            print("UNMEASURED  missing deployed " + dll)
            continue
        with open(dll, "rb") as h:
            data = h.read()
        for n in needles:
            check(n.encode("utf-16-le") in data, "deployed %s carries %s" % (os.path.basename(dll), n))
    if fails:
        print("RESULT FAIL (%d)" % len(fails))
        return 1
    if unmeasured:
        print("RESULT UNMEASURED (%d missing)" % len(unmeasured))
        return 2
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
