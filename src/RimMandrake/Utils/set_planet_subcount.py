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

    with open(PRESET, "w", encoding="utf-8") as fh:
        fh.write(xml)
    print("%s = %d in %s" % (FIELD, subcount, PRESET))


if __name__ == "__main__":
    main()
