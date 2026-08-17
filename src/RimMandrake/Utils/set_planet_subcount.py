#!/usr/bin/env python3
"""Force the tile density of an Alien Worlds planet type.

Worldbuilder overwrites My Little Planet's Scale slider twice - once with a
hardcoded 10 in Page_CreateWorldParams_Reset_Patch, and again at Generate with
`preset.myLittlePlanetSubcount`, which Scribes to 10 when the element is absent.
The Alien Worlds preset is generated without it, so the slider can never win.

Writing the element in makes the Generate-time write - the last one before the
grid is built - say what we want instead.

    python3 src/RimMandrake/Utils/set_planet_subcount.py 8

⚠️ AlienWorldsFramework.Refresh() DELETES and rewrites that folder at every
startup, so this has to be re-run after each launch, before generating.
Verify by reading <subdivisions> back out of the saved world, never by trusting
the slider - the slider shows the value that is about to be overwritten.
"""
import re
import sys

PRESET = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
          "3626210061/Worldbuilder/TidallyLocked/Preset.xml")
FIELD = "myLittlePlanetSubcount"

# Worldbuilder's Page_CreateWorldParams_Reset_Patch reads these off the preset and
# pushes them into the page, so the preset can PRE-SET the sliders. It only does so
# when saveGenerationParameters is true AND generationData is present.
# ⚠️ Write EVERY field the patch reads. A present-but-empty generationData Scribes the
# missing ones to enum 0, which would silently set rainfall/temperature/population to
# their minimum. Enum spellings MEASURED: rainfall/temperature/axialTilt/landmarkDensity
# from a real save; OverallPopulation is Low/Normal/High, read off the game's own
# PlanetPopulation_* translation keys - an earlier guess of "Much" was WRONG.

# 🔑 THE FACTION LIST. WorldGenerationData.ResetFactionCounts() fills factionCounts by
# repeating each ConfigurableFaction's defName startingCountAtWorldCreation times - so a
# preset carrying an explicit list pre-sets exactly which factions the world generates.
# ⚠️ Scribed under the element name "factionCountsStrings", NOT "factionCounts".
# Mechanoid and Insect are hidden factions: they are not configurable and arrive anyway.
FACTIONS_WANTED = [
    ("Empire", 3), ("OutlanderCivil", 4), ("TribeCivil", 3), ("Pirate", 2),
    ("Jawa_IndigenousTribes", 3), ("Jawa_HuttCartel", 2), ("Jawa_Junkers", 2),
    ("Jawa_WildsteamClan", 2), ("Jawa_DeepwaterCompact", 2), ("Jawa_AscendantHelix", 1),
    ("Jawa_FreeDroidEnclaves", 2), ("Jawa_GeonosianFoundryHive", 1),
]
FACTION_XML = ("    <factionCountsStrings>\n"
               + "".join("      <li>%s</li>\n" % d for d, n in FACTIONS_WANTED for _ in range(n))
               + "    </factionCountsStrings>\n")

GENDATA = """  <saveGenerationParameters>True</saveGenerationParameters>
  <disableExtraBiomes>False</disableExtraBiomes>
  <generationData>
__FACTIONS__    <planetCoverage>1</planetCoverage>
    <rainfall>Normal</rainfall>
    <temperature>Normal</temperature>
    <population>High</population>
    <pollution>0.05</pollution>
    <riverDensity>1</riverDensity>
    <ancientRoadDensity>1</ancientRoadDensity>
    <settlementRoadDensity>1</settlementRoadDensity>
    <mountainDensity>1</mountainDensity>
    <seaLevel>1</seaLevel>
    <axialTilt>Normal</axialTilt>
    <landmarkDensity>Normal</landmarkDensity>
  </generationData>
"""


def main():
    subcount = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    if not 6 <= subcount <= 10:
        # ModCompatibilityHelper.TrySetMLPSubcount refuses outside this range and
        # returns false silently, leaving the previous value in place.
        sys.exit("subcount must be 6..10; Worldbuilder refuses anything else silently")

    with open(PRESET, encoding="utf-8") as fh:
        xml = fh.read()

    line = "  <%s>%d</%s>\n" % (FIELD, subcount, FIELD)
    if FIELD in xml:
        xml = re.sub(r"[ \t]*<%s>\d+</%s>\n" % (FIELD, FIELD), line, xml)
    else:
        xml = xml.replace("  <biomes", line + "  <biomes")

    # pre-set the sliders too, so coverage cannot be got wrong by hand again
    if "<generationData>" not in xml:
        xml = xml.replace("  <biomes", GENDATA.replace("__FACTIONS__", FACTION_XML) + "  <biomes")
        pre = "coverage 1.0, population High, %d faction slots across %d factions" % (sum(n for _, n in FACTIONS_WANTED), len(FACTIONS_WANTED))
    else:
        pre = "already present"

    with open(PRESET, "w", encoding="utf-8") as fh:
        fh.write(xml)
    print("%s = %d  |  pre-set: %s" % (FIELD, subcount, pre))
    print("  -> %s" % PRESET)
    print("  RELOAD the preset in game; Worldbuilder caches the parsed object.")


if __name__ == "__main__":
    main()
