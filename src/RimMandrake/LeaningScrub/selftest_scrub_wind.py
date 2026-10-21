#!/usr/bin/env python3
"""Offline first script for SCRUB_WIND_BUILD_LEAN_ON_PURPOSE (owner card 2026-10-20, biome_bars_sitting §5.1-5.3).

What a machine can check without the game:
  lean   RM_LeanExtension carries the lean data (leanPlants, westLeaningTextures); every listed plant is one of this mod's
         plants; every west-leaning name is a real variant PNG of a listed plant; and the art agrees with the list:
         re-measured from the PNGs, a variant leaning clearly west (top drawn left of the base by >= 4.5% of the canvas)
         must be listed, one leaning clearly east must not be. RM_PlantLean.cs names no defName (selection is data).
  gale   RM_Gale carries RM_WeatherOverlay_GaleDust; no RM_GaleDust texture is installed (unreviewed art never ships:
         the overlay runs on its honestly-marked placeholder until review).
  calm   the biome table carries no stock weather above 0 (incl. Overcast, GrayPall, DryThunderstorm); every windy twin
         exists, blows (windSpeedOffset > 0, factor not under 1) and replaced its stock row at the same commonality; and
         against the vanilla 1.6 Data, when present, each twin copies its stock def's fields except the wind and words.
Each check is proved able to fail on a broken copy (the BREAKS at the bottom).

    python3 src/RimMandrake/LeaningScrub/selftest_scrub_wind.py
"""
import copy
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
BIOME = os.path.join(HERE, "Defs", "BiomeDefs", "RM_LeaningScrub_Biome.xml")
WEATHER_DIR = os.path.join(HERE, "Defs", "WeatherDefs")
PLANTS_DIR = os.path.join(HERE, "Defs", "ThingDefs_Plants")
TEX = os.path.join(HERE, "Textures", "Things", "Plant")
GALE_TEX = os.path.join(HERE, "Textures", "Weather")
PLANT_LEAN_CS = os.path.join(HERE, "Source", "RM_PlantLean.cs")
VANILLA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
TWINS = {"Overcast": ("RM_ScrubOvercast", "Odyssey"), "GrayPall": ("RM_ScrubGrayPall", "Anomaly"),
         "DryThunderstorm": ("RM_ScrubDryThunderstorm", "Core")}
STOCK = ("Clear", "Fog", "Rain", "RainyThunderstorm", "FoggyRain", "SnowGentle", "SnowHard") + tuple(TWINS)
WIND_FIELDS = {"windSpeedOffset", "windSpeedFactor", "label", "description", "defName", "ambientSounds"}
LEAN_CLEAR = 0.045      # |lean| at or past this (fraction of canvas width) is a clear lean the list must agree with


def load():
    weathers = {}
    for f in sorted(os.listdir(WEATHER_DIR)):
        if f.endswith(".xml"):
            for w in ET.parse(os.path.join(WEATHER_DIR, f)).getroot().iter("WeatherDef"):
                weathers[w.findtext("defName")] = w
    plants = set()
    for f in sorted(os.listdir(PLANTS_DIR)):
        if f.endswith(".xml"):
            for d in ET.parse(os.path.join(PLANTS_DIR, f)).getroot().iter("ThingDef"):
                if d.findtext("defName"):
                    plants.add(d.findtext("defName"))
    return {"biome": ET.parse(BIOME).getroot(), "weathers": weathers, "plants": plants,
            "cs": open(PLANT_LEAN_CS, encoding="utf-8").read(), "leans": measure_leans(), "gale_tex": gale_textures()}


def measure_leans():
    """{texture name: lean} for every variant PNG of every plant folder. lean > 0 = the top is drawn right of the base."""
    from PIL import Image
    import numpy as np
    out = {}
    for folder in sorted(os.listdir(TEX)):
        p = os.path.join(TEX, folder)
        if not os.path.isdir(p):
            continue
        for f in sorted(os.listdir(p)):
            if not f.endswith(".png"):
                continue
            a = np.asarray(Image.open(os.path.join(p, f)).convert("RGBA"))[:, :, 3]
            ys, xs = np.nonzero(a > 40)
            if len(xs) == 0:
                continue
            lo, hi = ys.min(), ys.max()
            third = (hi - lo) / 3.0
            top, bot = xs[ys < lo + third], xs[ys > hi - third]
            if len(top) and len(bot):
                out[f[:-4]] = (top.mean() - bot.mean()) / a.shape[1]
    return out


def gale_textures():
    if not os.path.isdir(GALE_TEX):
        return []
    return [f for f in os.listdir(GALE_TEX) if f.startswith("RM_GaleDust")]


def lean_ext(biome):
    for li in biome.iter("li"):
        if (li.get("Class") or "").endswith("RM_LeanExtension"):
            return li
    return None


def findings(d):
    bad = []
    # ---- lean
    ext = lean_ext(d["biome"])
    if ext is None:
        return ["the biome carries no RM_LeanExtension"]
    listed = [li.text.strip() for li in ext.findall("leanPlants/li")]
    west = [li.text.strip() for li in ext.findall("westLeaningTextures/li")]
    if not listed:
        bad.append("lean: leanPlants is empty (no plant would face the wind)")
    for n in listed:
        if n not in d["plants"]:
            bad.append("lean: leanPlants names %s, not a plant of this mod" % n)
    variants = {name: v for name, v in d["leans"].items() if any(name.startswith(p + "_") for p in listed)}
    for n in west:
        if n not in variants:
            bad.append("lean: west-leaning texture %s is not a variant PNG of a listed plant" % n)
    for name, v in sorted(variants.items()):
        if v <= -LEAN_CLEAR and name not in west:
            bad.append("lean: %s leans west (%.1f%%) but is not listed in westLeaningTextures" % (name, 100 * v))
        if v >= LEAN_CLEAR and name in west:
            bad.append("lean: %s leans east (%.1f%%) but is listed as west-leaning" % (name, 100 * v))
    code = re.sub(r"//[^\n]*", "", d["cs"])
    hard = sorted(set(re.findall(r'"(RM_[A-Za-z]+)"', code)))
    if hard:
        bad.append("lean: RM_PlantLean.cs hardcodes defNames %s (selection must be data)" % hard)
    if "Rand.Bool" not in d["cs"] or "PushState" not in d["cs"]:
        bad.append("lean: RM_PlantLean.cs no longer patches after Rand.Bool or no longer restores the Rand state")
    # ---- gale
    gale = d["weathers"].get("RM_Gale")
    if gale is None or not any((li.text or "").strip().endswith("RM_WeatherOverlay_GaleDust")
                               for li in gale.findall("overlayClasses/li")):
        bad.append("gale: RM_Gale carries no RM_WeatherOverlay_GaleDust overlay")
    if d["gale_tex"]:
        bad.append("gale: RM_GaleDust art is installed (%s) - only reviewed art ships; remove this check when the "
                   "owner has reviewed it" % d["gale_tex"])
    # ---- calm days
    table = {}
    for c in d["biome"].iter("baseWeatherCommonalities"):
        for row in c:
            table[row.tag] = float(row.text)
    for n in STOCK:
        if table.get(n, 0) > 0:
            bad.append("calm: stock weather %s has commonality %s on the Scrub" % (n, table[n]))
    for stock, (twin, _dlc) in TWINS.items():
        w = d["weathers"].get(twin)
        if w is None:
            bad.append("calm: twin %s missing" % twin)
            continue
        off = float(w.findtext("windSpeedOffset") or 0)
        fac = float(w.findtext("windSpeedFactor") or 1)
        if off <= 0 or fac < 1:
            bad.append("calm: twin %s can fall calm (offset %s, factor %s)" % (twin, off, fac))
        if not table.get(twin):
            bad.append("calm: twin %s is not in the biome table" % twin)
    return bad


def vanilla_findings(d):
    """Each twin copies its stock def field for field, except wind and words. Skipped (None) without the game Data."""
    if not os.path.isdir(VANILLA):
        return None
    bad = []
    for stock, (twin, dlc) in TWINS.items():
        path = os.path.join(VANILLA, dlc, "Defs", "WeatherDefs", "Weathers.xml")
        src = [w for w in ET.parse(path).getroot().iter("WeatherDef") if w.findtext("defName") == stock]
        if not src:
            bad.append("vanilla %s not found in %s" % (stock, path))
            continue
        a = {c.tag: ET.tostring(c) for c in src[0] if c.tag not in WIND_FIELDS}
        b = {c.tag: ET.tostring(c) for c in d["weathers"][twin] if c.tag not in WIND_FIELDS}
        norm = lambda x: re.sub(rb"\s+", b"", re.sub(rb"<!--.*?-->", b"", x, flags=re.S))
        for k in sorted(set(a) | set(b)):
            if norm(a.get(k, b"")) != norm(b.get(k, b"")):
                bad.append("calm: twin %s differs from %s in <%s>" % (twin, stock, k))
    return bad


def _break(d, fn):
    d = dict(d, biome=copy.deepcopy(d["biome"]), weathers={k: copy.deepcopy(v) for k, v in d["weathers"].items()})
    fn(d)
    return d


def _drop_west(d, name):
    ext = lean_ext(d["biome"])
    for li in ext.findall("westLeaningTextures/li"):
        if li.text.strip() == name:
            ext.find("westLeaningTextures").remove(li)


def _set_row(d, tag, val):
    for c in d["biome"].iter("baseWeatherCommonalities"):
        el = c.find(tag)
        if el is None:
            el = ET.SubElement(c, tag)
        el.text = val


BREAKS = {
    "west variant unlisted": lambda d: _drop_west(d, "RM_Whipfuzz_c"),
    "east variant listed": lambda d: ET.SubElement(lean_ext(d["biome"]).find("westLeaningTextures"), "li").__setattr__("text", "RM_Whipfuzz_b"),
    "non-plant listed": lambda d: ET.SubElement(lean_ext(d["biome"]).find("leanPlants"), "li").__setattr__("text", "RM_NoSuchPlant"),
    "hardcoded defName": lambda d: d.__setitem__("cs", d["cs"] + '\nstatic string x = "RM_Fuzz";'),
    "gale overlay gone": lambda d: d["weathers"]["RM_Gale"].remove(d["weathers"]["RM_Gale"].find("overlayClasses")),
    "unreviewed art installed": lambda d: d.__setitem__("gale_tex", ["RM_GaleDust_A.png"]),
    "stock Overcast back": lambda d: _set_row(d, "Overcast", "5"),
    "twin calm": lambda d: d["weathers"]["RM_ScrubOvercast"].find("windSpeedOffset").__setattr__("text", "0"),
    "twin unlisted": lambda d: _set_row(d, "RM_ScrubGrayPall", "0"),
}


def main():
    d = load()
    fails = findings(d)
    v = vanilla_findings(d)
    if v is None:
        print("vanilla Data not reachable: twin field-for-field copy UNMEASURED")
    else:
        fails += v
        broken = _break(d, lambda x: x["weathers"]["RM_ScrubDryThunderstorm"].find("durationRange").__setattr__("text", "1~2"))
        if not vanilla_findings(broken):
            fails.append("break 'twin drifted from vanilla' was not caught")
    for name, fn in BREAKS.items():
        if not findings(_break(d, fn)):
            fails.append("break '%s' was not caught" % name)
    listed = len(lean_ext(d["biome"]).findall("leanPlants/li"))
    for f in fails:
        print("FAIL " + f)
    print("selftest scrub wind: %d lean plants, %d variants measured, %d breaks -> %s"
          % (listed, len(d["leans"]), len(BREAKS), "FAIL" if fails else "OK"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
