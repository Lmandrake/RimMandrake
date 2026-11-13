#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_BUILD_PYRE_SMOKE_WEATHER_ONLY_LONGSHADE_HAS_ONE: the Pyrelands get a choking smoke that
arrives as its own weather.

Owner, 2026-11-13 (RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES, walk_season_on_the_pyre): "And I won't miss having to sweep
the ash away from all my paths to keep walking clear, or the choking smoke that sometimes come as its own weather..."

Offline, over the defs and source the mod ships (the live "it chokes" is the season walk's beat, not this test). Rows:
  smoke_weather_defined        a WeatherDef in Pyrelands/Defs whose label holds "smoke"          RED on a68d89e622 (none)
  smoke_weather_in_biome_table RM_Pyrelands' baseWeatherCommonalities lists it with weight > 0   RED on a68d89e622
  smoke_weather_has_effect     it does more than look: its defName is read by Pyrelands C#, or the def carries
                               modExtensions or an exposedThought                                RED on a68d89e622
  smoke_not_rain_rated         its rainRate <= 0.1 (it neither puts fires out nor joins vanilla's x15 rain-on-fire roll)
  old_weathers_kept            AshDrift, AshFall, Cinderfall, BlackRain and DryThunderstorm stay in the table, weight > 0
  black_rain_only_rain         RM_FE_BlackRain stays the only rain-rated (> 0.1) weather in the table (Pyrelands.xml's
                               "NO VANILLA RAIN IN THIS TABLE, AND THAT IS THE MECHANISM")
The smoke rows count once; when no smoke weather exists, rows 2-4 fail with "no smoke weather".

    python3 src/RimMandrake/rimflow/acceptance/pyre_smoke_weather_accept.py [--root <repo>]   (exit 0 = PASS 6/6)
The builder does not edit it; a clause believed wrong goes to the Conductor.
"""
import glob
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
if "--root" in sys.argv:
    REPO = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
MOD = os.path.join(REPO, "src", "RimMandrake", "Pyrelands")
VANILLA_TABLE = {"DryThunderstorm"}
fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def weather_defs():
    out = {}
    for p in glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as e:
            check("parse " + os.path.relpath(p, REPO), False, e)
            continue
        for w in root.iter("WeatherDef"):
            name = (w.findtext("defName") or "").strip()
            if name:
                out[name] = w
    return out


def biome_table():
    p = os.path.join(MOD, "Defs", "BiomeDefs", "Pyrelands.xml")
    for b in ET.parse(p).getroot().iter("BiomeDef"):
        if (b.findtext("defName") or "").strip() == "RM_Pyrelands":
            t = b.find("baseWeatherCommonalities")
            return {} if t is None else {c.tag: float((c.text or "0").strip()) for c in t}
    return {}


def rain_rate(w):
    try:
        return float((w.findtext("rainRate") or "0").strip())
    except ValueError:
        return 0.0


weathers = weather_defs()
table = biome_table()
source = ""
for p in glob.glob(os.path.join(MOD, "Source", "**", "*.cs"), recursive=True):
    with open(p, encoding="utf-8", errors="replace") as f:
        source += f.read()

smoke = [n for n, w in weathers.items() if "smoke" in (w.findtext("label") or "").lower()]
check("smoke_weather_defined", bool(smoke), "no WeatherDef in Pyrelands/Defs has 'smoke' in its label")
listed = [n for n in smoke if table.get(n, 0) > 0]
check("smoke_weather_in_biome_table", bool(listed),
      "no smoke weather" if not smoke else "%s not in RM_Pyrelands baseWeatherCommonalities with weight > 0" % smoke)
effect = [n for n in smoke if ('"%s"' % n) in source or weathers[n].find("modExtensions") is not None
          or weathers[n].find("exposedThought") is not None]
check("smoke_weather_has_effect", bool(effect),
      "no smoke weather" if not smoke else "%s: no C# reads it, no modExtensions, no exposedThought" % smoke)
check("smoke_not_rain_rated", bool(smoke) and all(rain_rate(weathers[n]) <= 0.1 for n in smoke),
      "no smoke weather" if not smoke else {n: rain_rate(weathers[n]) for n in smoke})
kept = ["RM_FE_Weather_AshDrift", "RM_FE_Weather_AshFall", "RM_FE_Weather_Cinderfall", "RM_FE_BlackRain", "DryThunderstorm"]
check("old_weathers_kept", all(table.get(n, 0) > 0 for n in kept), {n: table.get(n) for n in kept})
rainy = sorted(n for n in table if n in weathers and rain_rate(weathers[n]) > 0.1)
foreign = sorted(n for n in table if n not in weathers and n not in VANILLA_TABLE and n not in
                 {"Fog", "GrayPall", "Windy", "Overcast"})
check("black_rain_only_rain", rainy == ["RM_FE_BlackRain"] and not foreign,
      "rain-rated: %s; unknown table entries (rain rate unread): %s" % (rainy, foreign))

total = 6
print("PASS %d/%d" % (total - len(fails), total) + ("" if not fails else " failed: " + ", ".join(fails)))
sys.exit(1 if fails else 0)
