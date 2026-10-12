"""Offline selftest of river_site's fish preference (RIVER_SITE_FIX_FISHLESS_ROT_RIVER). No bridge."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0]]
import river_site as R  # noqa: E402

FAILS = []


def check(name, cond, why=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else why))
    if not cond:
        FAILS.append(name)


check("salt-only fish table is not river fish", R.biome_has_fish({"maxFishPopulation": 9, "fishTypes": {"saltwater_Common": {"a": 1}}}) is False)
check("fish biome", R.biome_has_fish({"maxFishPopulation": 540, "fishTypes": {"freshwater_Common": {"Fish_Bass": 1}}}) is True)
check("zero population is fishless", R.biome_has_fish({"maxFishPopulation": 0, "fishTypes": {"freshwater_Common": {"a": 1}}}) is False)
check("no field read is unknown, not fishless", R.biome_has_fish({}) is None and R.biome_has_fish(None) is None)
check("empty fish table is fishless", R.biome_has_fish({"maxFishPopulation": 50, "fishTypes": {}}) is False)

xml = """<Defs>
<BiomeDef><defName>A_Fishy</defName><maxFishPopulation>300</maxFishPopulation>
 <fishTypes><freshwater_Common><Fish_Bass>1</Fish_Bass></freshwater_Common></fishTypes></BiomeDef>
<BiomeDef><defName>A_Barren</defName><maxFishPopulation>0</maxFishPopulation></BiomeDef>
<BiomeDef><defName>A_SaltOnly</defName><maxFishPopulation>90</maxFishPopulation>
 <fishTypes><saltwater_Common><Fish_X>1</Fish_X></saltwater_Common></fishTypes></BiomeDef>
<BiomeDef ParentName="Base"><defName>A_Child</defName></BiomeDef></Defs>"""
fx = R.biome_fish_from_xml(xml)
check("xml: fishy / barren / salt-only / inherited skipped",
      fx == {"A_Fishy": True, "A_Barren": False, "A_SaltOnly": False}, str(fx))

rows = [{"tile": 1, "biome": "RM_TheRot"}, {"tile": 2, "biome": "TemperateForest"}, {"tile": 3, "biome": "Mystery"},
        {"tile": 4, "biome": "RM_TheRot"}]
order, rej = R.prefer_fish(rows, {"RM_TheRot": False, "TemperateForest": True, "Mystery": None})
check("fish tiles first, unknown next, fishless dropped", [r["tile"] for r in order] == [2, 3], str(order))
check("rejection is named with a count", rej == [("RM_TheRot", 2)], str(rej))
calls = []
def fake(tool, **kw):
    calls.append(kw["defs"])
    return {"defs": [{"fields": {"maxFishPopulation": 10, "fishTypes": {"freshwater_Common": {"f": 1}}}}]} if "Good" in kw["defs"] else {"defs": []}
fb = R.fish_by_biome(fake, ["Good", "Bad", None, "Good"])
check("fish_by_biome: one read per biome, unreadable is None", fb == {"Good": True, "Bad": None} and len(calls) == 2, str(fb))
fb2 = R.fish_by_biome(lambda tool, **kw: {"defs": []}, ["Z"], {"Z": False})
check("fish_by_biome falls back to the XML table when the live read is unknown", fb2 == {"Z": False}, str(fb2))
xf = R._xml_fish()
print("xml fallback biomes read:", len(xf))
print("selftest_river_site: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
