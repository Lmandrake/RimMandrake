#!/usr/bin/env python3
"""Offline static selftest for FlowWorks River colours (River Colors, WORLD_RIVER_COLORS_1; was its own mod
mandrake.rut.rivercolors until RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW, 2026-10-16). No game, no bridge.

It replaces that mod's validation.py, whose live suite proved only that GeneratePaths carried the patch, that the
`enabled` setting round-tripped and that its Harmony id owned the patch; the colour actually drawn per tile was never
proven (it needs a world-map look with the owner). Checks here what goes silently wrong in this repo:
  * the csproj has EnableDefaultCompileItems=false, so a .cs missing a <Compile> line builds into nothing;
  * the settings section is scribed and drawn from FlowWorks' one settings class, every scribe key is unique across
    FlowWorks' settings file, every field the patch reads exists, and its [PatchFeature] names a real bool field;
  * no standalone Harmony bootstrap survives (RM_FlowWorksHarmony applies the whole assembly);
  * the RiverColors mod folder and packageId are gone, and no modset tier still wants mandrake.rut.rivercolors.
  * every biome tint (RIVER_WATER_BY_BIOME) names a BiomeDef we ship.
Sanity probes: the scribe-key regex must see a key we know exists (swaleEnabled), and the field regex riverColorsEnabled.
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FAILS = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAILS.append(name)


def main():
    src = os.path.join(HERE, "Source")
    csproj = open(os.path.join(src, "RimMandrake_FlowWorks.csproj"), encoding="utf-8").read()
    listed = {p.replace("\\", "/") for p in re.findall(r'<Compile Include="([^"]+)"', csproj)}
    listed_rc = {p for p in listed if p.startswith("RiverColors/")}
    on_disk = {"RiverColors/" + os.path.basename(p) for p in glob.glob(os.path.join(src, "RiverColors", "*.cs"))}
    check("sanity: RiverColors/ holds the two .cs files", len(on_disk) == 2, sorted(on_disk))
    check("csproj compiles every RiverColors .cs", on_disk <= listed_rc, sorted(on_disk - listed_rc))
    check("csproj lists no missing RiverColors .cs", listed_rc <= on_disk, sorted(listed_rc - on_disk))

    settings = open(os.path.join(src, "RiverColors", "RM_RiverColorsSettings.cs"), encoding="utf-8").read()
    patch = open(os.path.join(src, "RiverColors", "RM_RiverColors.cs"), encoding="utf-8").read()
    fw = open(os.path.join(src, "RimMandrakeFlowWorksMod.cs"), encoding="utf-8").read()
    key = re.compile(r'Scribe_Values\.Look\(ref \w+, "(\w+)"')
    others = ""
    for p in glob.glob(os.path.join(src, "**", "*.cs"), recursive=True):
        if os.path.basename(p) != "RM_RiverColorsSettings.cs":
            others += open(p, encoding="utf-8").read()
    k_other, k_rc = key.findall(others), key.findall(settings)
    check("sanity: scribe-key regex sees swaleEnabled", "swaleEnabled" in k_other)
    check("River colours scribe keys are prefixed riverColors_", k_rc and all(k.startswith("riverColors_") for k in k_rc), k_rc)
    check("River colours scribe keys unique across FlowWorks' settings",
          not (set(k_other) & set(k_rc)) and len(k_rc) == len(set(k_rc)), sorted(set(k_other) & set(k_rc)))
    check("FlowWorks settings scribe the River colours section", "RiverColors.RM_RiverColorsSettings.ExposeData()" in fw)
    check("FlowWorks settings window draws the River colours section",
          "RiverColors.RM_RiverColorsSettings.DoSettingsSection)" in fw)

    fields = set(re.findall(r"public static (?:bool|Color) (\w+)\s*=", settings))
    check("sanity: field regex sees riverColorsEnabled", "riverColorsEnabled" in fields, sorted(fields))
    for f in sorted(fields):
        check("setting %s is scribed" % f, re.search(r"Scribe_Values\.Look\(ref %s," % f, settings) is not None)
    read = set(re.findall(r"RM_RiverColorsSettings\.(\w+)", patch))
    check("every setting the patch reads exists", read and read <= fields, sorted(read - fields))
    m = re.search(r'PatchFeature\("[^"]+", typeof\(RM_RiverColorsSettings\), "(\w+)"\)', patch)
    check("[PatchFeature] names a real bool switch", m is not None and m.group(1) in fields and
          re.search(r"public static bool %s\b" % (m.group(1) if m else "-"), settings) is not None)
    check("patch scoped to WorldDrawLayer_Rivers (roads untouched)", "__instance is WorldDrawLayer_Rivers" in patch)
    # RIVER_WATER_BY_BIOME (2026-10-20): every tint keys on a BiomeDef we ship. The gradient's anchors
    # (AB_OcularForest, AB_FeraliskInfestedJungle, Wasteland) matched no tile, so every river fell to elevation colours.
    tints = re.findall(r'case "(\w+)": return RM_RiverColorsSettings\.(\w+);', patch)
    check("sanity: tint regex sees RM_Contagion", any(t == "RM_Contagion" for t, _ in tints), tints)
    shipped = set()
    for p in glob.glob(os.path.join(REPO, "src", "**", "*.xml"), recursive=True):
        if "/Defs/" in p.replace("\\", "/"):
            shipped.update(re.findall(r"<BiomeDef[^>]*>\s*<defName>(\w+)</defName>", open(p, encoding="utf-8", errors="replace").read()))
    check("sanity: BiomeDef scan sees RM_Greentide", "RM_Greentide" in shipped, len(shipped))
    check("every tint biome is a BiomeDef we ship", all(t in shipped for t, _ in tints), [t for t, _ in tints if t not in shipped])
    check("default water is not vanilla riverColor (73,82,100), so RM_WorldPaths keeps it",
          "waterColor = new Color(73" not in settings)
    check("no standalone Harmony bootstrap or old namespace survives",
          "new Harmony(" not in patch + settings and "RimMandrake.Utinni.RiverColors" not in patch + settings + csproj)
    check("settings default on (shipped behaviour)", re.search(r"public static bool riverColorsEnabled = true;", settings))

    sys.path.insert(0, os.path.join(HERE, "northstar"))
    import site_spec as S  # noqa: E402
    cls = "RimMandrake.FlowWorks.RiverColors.RM_RiverColorsSettings"
    check("site_spec registers the section", S.SETTINGS.get(cls) == {"riverColorsEnabled": True} and cls in S.SETTINGS_SOURCES)

    about = ET.parse(os.path.join(HERE, "About", "About.xml")).getroot()
    check("packageId mandrake.rm.flowworks", about.findtext("packageId") == "mandrake.rm.flowworks")
    check("the RiverColors mod folder is gone (merged)",
          not os.path.exists(os.path.join(REPO, "src", "RimUtinni", "RiverColors")))
    mb = open(os.path.join(REPO, "src", "RimMandrake", "Utils", "modset_builder.py"), encoding="utf-8").read()
    check("no modset tier wants mandrake.rut.rivercolors", '"mandrake.rut.rivercolors"' not in mb)

    print("\n%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
