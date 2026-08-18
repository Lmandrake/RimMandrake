#!/usr/bin/env python3
"""Steps 5+6: biomes from climate, and the riparian ribbon.

🔴 WHAT CHANGED. The old painter chose biome from `region_of(arc, bearing, elev)` -
a lat/long predicate. Water was not an input to that function, which is the whole
reason the owner could look at the planet and find no jungle beside any river.

Here biome is a lookup on (temperature, humidity, relief), Whittaker-style, over the
fields the earlier steps produced. Two consequences fall out for free:

  * gradients. Desert -> arid shrubland -> forest happens because the humidity field
    is continuous, not because anyone wrote a boundary.
  * the ribbon. A river raises the humidity of its own tile and its neighbours, so
    lush terrain appears ALONG WATER without a rule that says so. The owner's ruling
    is Nile-style: the ribbon threads into the deep desert wherever a river goes.

Authored overrides sit on top for the things that are story rather than climate - the
Rust Cathedral, the Scald's volcanics, the propane lakes, the Horror Wastes.

Reads  world/relief.npz, world/hydro.npz
Writes world/biomes.npz    biome index + name table, hilliness
       world/biomes.png    the planet as it will look, plus the humidity field

    python3 src/RimMandrake/Utils/world_biomes.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world_graph
import world_relief as wr
import world_shape

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT_NPZ = os.path.join(REPO, "world", "biomes.npz")
OUT_PNG = os.path.join(REPO, "world", "biomes.png")

# ---------------------------------------------------------------- the palette
# Colour is only for the preview; the defName is what ships. Kept close to how each
# biome actually reads on RimWorld's world map so the picture is worth trusting.
COLOUR = {
    "Ocean":                      (30, 58, 112),
    "SeaIce":                     (176, 196, 214),
    "ExtremeDesert":              (232, 206, 150),
    "Desert":                     (216, 186, 128),
    "AridShrubland":              (188, 176, 116),
    "Wasteland":                  (156, 142, 122),
    "ZBiome_Badlands":            (172, 130, 92),
    "Scarlands":                  (168, 96, 78),
    "Volcano":                    (110, 74, 66),
    "LavaField":                  (140, 62, 48),
    "AB_MechanoidIntrusion":      (150, 128, 176),
    "AB_PyroclasticConflagration": (128, 70, 60),
    "AB_GallatrossGraveyard":     (150, 132, 96),
    "ZBiome_DesertOasis":         (140, 176, 110),
    "AB_FeraliskInfestedJungle":  (74, 136, 72),
    "AB_MycoticJungle":           (96, 130, 148),
    "BMT_FungalForest":           (110, 116, 156),
    "PoisonForest":               (104, 128, 84),
    "Glowforest":                 (86, 148, 140),
    "AB_RockyCrags":              (128, 132, 138),
    "AB_PropaneLakes":            (96, 108, 140),
    "AB_TarPits":                 (52, 46, 50),
    "HorrorWastes":               (128, 84, 104),
    "AB_GelatinousSuperorganism": (150, 140, 168),
}

# no Hills/ art -> magenta above flat. See CHECK.md, settled 2026-08-17.
FLAT_ONLY = {"AB_TarPits", "AB_IdyllicMeadows", "AB_MiasmicMangrove",
             "ZBiome_DesertOasis"}
# declares a snow threshold it ships no art for; keep off cold tiles above flat
COLD_FLAT = {"ExtremeDesert": -5.0, "Scarlands": -21.0}

RIPARIAN_REACH = 2          # tiles either side of a river that the ribbon reaches


def humidity_rank(rain, water):
    """Rain in percentile rank over land, 0..1.

    The raw field spans four orders of magnitude on a desert world - p75 is 0.001
    and p99 is 25 - so an absolute threshold on it is meaningless. Rank is what
    makes 'the wettest fifth of the planet' a statement you can write down.
    """
    h = np.zeros(len(rain))
    land = ~water
    r = rain[land]
    o = np.argsort(np.argsort(r))
    h[land] = o / max(len(r) - 1, 1)
    return h


def frost_water(T):
    """Meltwater availability at the frost line.

    🔑 THE GAP THE CENSUS FOUND. With the wind blowing sunward, no rain reaches past
    the terminator, so the humidity rank made the whole nightside AB_RockyCrags and
    every cold-wet biome the fiction calls for - the glow forests, the mycotic
    jungle, the fungal forest - came out with ZERO tiles.

    Rain is not the only water on a cold-trap world. Everything that ever crossed the
    terminator is still there, frozen into the ground, and the band where that ice
    meets enough warmth to melt is the liveable one. That band is a bump in
    TEMPERATURE, not in rainfall: too warm and the ice is long gone, too cold and it
    never melts. It is why the Twilight Glow is where it is.
    """
    return np.exp(-((T + 6.0) / 21.0) ** 2)


def riparian(nb, grade, playa, reach=RIPARIAN_REACH):
    """Distance in tiles to the nearest river, capped. 0 on the river itself."""
    n = len(grade)
    d = np.full(n, reach + 1, dtype=np.int8)
    front = list(np.flatnonzero((grade > 0) | playa))
    for i in front:
        d[i] = 0
    for step in range(1, reach + 1):
        nxt = []
        for i in front:
            for j in nb[i]:
                if d[j] > step:
                    d[j] = step
                    nxt.append(j)
        front = nxt
    return d


def classify(T, H, elev, arc, riv, grade, water, slope):
    """The Whittaker lookup. Temperature down the side, humidity across."""
    n = len(T)
    out = np.empty(n, dtype=object)
    for i in range(n):
        if water[i]:
            out[i] = "SeaIce" if T[i] < -12.0 else "Ocean"
            continue
        t, h = T[i], H[i]

        # a river carries its own climate with it: the ribbon. Distance 0 counts as
        # a full band of humidity, distance 2 as a third of one.
        if riv[i] <= RIPARIAN_REACH:
            h = min(1.0, h + (0.42, 0.26, 0.13)[riv[i]])

        if t < -35.0:                       # the deep nightside: nothing grows
            out[i] = "AB_PropaneLakes" if h > 0.9 else "AB_RockyCrags"
        elif t < -8.0:                      # the dark cold
            if h > 0.86:
                out[i] = "BMT_FungalForest"
            elif h > 0.62:
                out[i] = "AB_MycoticJungle"
            else:
                out[i] = "AB_RockyCrags"
        elif t < 14.0:                      # the twilight band - the liveable one
            if h > 0.97:
                out[i] = "AB_GelatinousSuperorganism"
            elif h > 0.90:
                out[i] = "Glowforest"
            elif h > 0.80:
                out[i] = "PoisonForest"
            elif h > 0.58:
                out[i] = "AridShrubland"
            else:
                out[i] = "Wasteland"
        elif t < 46.0:                      # the outer dayside
            if h > 0.962:
                out[i] = "AB_FeraliskInfestedJungle"
            elif h > 0.90:
                out[i] = "ZBiome_DesertOasis"
            elif h > 0.66:
                out[i] = "AridShrubland"
            elif h > 0.40:
                out[i] = "Desert"
            else:
                out[i] = ("ZBiome_Badlands" if slope[i] > 150
                          else "AB_GallatrossGraveyard" if h < 0.14 else "Desert")
        else:                               # the scorched inner dayside
            if h > 0.955:
                out[i] = "ZBiome_DesertOasis"
            elif h > 0.62:
                out[i] = "Desert"
            else:
                out[i] = "ExtremeDesert"
    return out


def overrides(name, arc, bear, elev, T, H, water, riv, rng, awarp):
    """Story, not climate. Kept small and kept SEPARATE, so it is obvious which
    tiles were argued for and which ones the physics produced."""
    n = len(arc)

    def angdiff(a, b):
        return np.abs((a - b + 180.0) % 360.0 - 180.0)

    # the Rust Cathedral: the machine mass on the substellar plateau
    arc = arc + awarp                    # nothing authored may be a clean circle
    m = (~water) & (arc < 11.5) & (angdiff(bear, 40.0) < 118.0)
    name[m] = "AB_MechanoidIntrusion"
    # the scorch ring around it
    m = (~water) & (arc >= 11.5) & (arc < 15.0)
    name[m] = "Scarlands"
    # the Scald's own volcanics: the rim, where the crust is thin
    d = np.abs(arc - 35.0)
    rim = (~water) & (wr.ang(VEC, wr.to_vec(35.0, 185.0))[:, 0] > 12.0) & \
          (wr.ang(VEC, wr.to_vec(35.0, 185.0))[:, 0] < 21.0) & (elev > 1500)
    pick = rng.random(n)
    name[rim & (pick < 0.34)] = "Volcano"
    name[rim & (pick >= 0.34) & (pick < 0.60)] = "LavaField"
    name[rim & (pick >= 0.60) & (pick < 0.74)] = "AB_PyroclasticConflagration"
    # the propane lakes: the antistellar cold trap floor
    m = (~water) & (arc > 148.0) & (elev < 260)
    name[m] = "AB_PropaneLakes"
    # the Horror Wastes: scattered SMALL holdings in the rotting twilight, and
    # retreating - so a handful of blots, never a belt. (build_concepts 2026-08-17)
    m = (~water) & (T > -20.0) & (T < 12.0) & (H > 0.50) & (pick > 0.965)
    name[m] = "HorrorWastes"
    # tar pits: they sit beside the water in the rotting band, not on their own
    m = (~water) & (riv <= 2) & (T > -18.0) & (T < 26.0) & (pick > 0.90)
    name[m] = "AB_TarPits"
    return name


def hilliness(elev, slope, name, T):
    h = np.ones(len(elev), dtype=np.int8)
    h[slope > 45] = 2
    h[slope > 120] = 3
    h[slope > 240] = 4
    h[slope > 430] = 5
    h[elev > 2600] = np.maximum(h[elev > 2600], 4)
    for i, nm in enumerate(name):
        if nm in FLAT_ONLY:
            h[i] = 1
        elif nm in COLD_FLAT and T[i] < COLD_FLAT[nm]:
            h[i] = 1
        elif nm in ("Ocean", "SeaIce"):
            h[i] = 1
    return h


def audit(name, hill, riv, T, H, water, nb):
    """The sanity pass, run BEFORE anyone looks at the planet. That ordering is the
    entire point of the rebuild."""
    bad = 0
    lush = {"AB_FeraliskInfestedJungle", "ZBiome_DesertOasis", "Glowforest",
            "PoisonForest"}
    off = sum(1 for i, nm in enumerate(name)
              if nm in lush and riv[i] > RIPARIAN_REACH and H[i] < 0.80)
    mag = sum(1 for i, nm in enumerate(name)
              if hill[i] > 1 and (nm in FLAT_ONLY
                                  or (nm in COLD_FLAT and T[i] < COLD_FLAT[nm])))
    counts = {}
    for nm in name:
        counts[nm] = counts.get(nm, 0) + 1
    lab = [sorted(COLOUR).index(nm) if nm in COLOUR else -1 for nm in name]
    comps = world_shape.components(lab, nb)
    specks = sum(1 for _, c in comps if len(c) == 1)
    print("biomes: %d distinct, %d connected masses, %d single-tile specks"
          % (len(counts), len(comps), specks))
    print("🔴 magenta risk (flat-only biome above flat): %d" % mag)
    print("🔴 lush tiles with neither a river nor the humidity for it: %d" % off)
    for nm, c in sorted(counts.items(), key=lambda kv: -kv[1]):
        print("    %-28s %5d  %4.1f%%" % (nm, c, 100.0 * c / len(name)))
    bad = mag + off
    return bad


def render(name, H, water, elev, V, nb, size=520, pad=14):
    W, Hh, discs = wr.disc_maps(V, size, pad)
    keys = sorted(COLOUR)
    idx = np.array([keys.index(nm) if nm in COLOUR else 0 for nm in name])
    lut = np.array([COLOUR[k] for k in keys], dtype=np.int16)
    mean_nb = np.array([elev[x].mean() for x in nb])
    shade = np.clip((elev - mean_nb) / 62.0, -1.0, 1.0)

    out = np.zeros((Hh * 2 + pad, W, 3), dtype=np.uint8)
    out[:, :] = (10, 10, 14)
    img = wr.blank(W, Hh)
    for x0, y0, inside, near in discs:
        c = lut[idx[near]] + (shade[near] * 26).astype(np.int16)[:, None]
        tile = np.zeros((size, size, 3), dtype=np.uint8)
        tile[:, :] = (10, 10, 14)
        tile[inside] = np.clip(c, 0, 255).astype(np.uint8)
        img[y0:y0 + size, x0:x0 + size] = tile
    out[0:Hh] = img

    himg = wr.blank(W, Hh)
    for x0, y0, inside, near in discs:
        t = H[near]
        c = np.stack([(226 - 190 * t), (196 - 60 * t), (140 + 60 * t)], axis=1)
        c[water[near]] = (30, 58, 112)
        tile = np.zeros((size, size, 3), dtype=np.uint8)
        tile[:, :] = (10, 10, 14)
        tile[inside] = np.clip(c, 0, 255).astype(np.uint8)
        himg[y0:y0 + size, x0:x0 + size] = tile
    out[Hh + pad:] = himg
    return out


VEC = None


def main():
    global VEC
    r = np.load(os.path.join(REPO, "world", "relief.npz"))
    hy = np.load(os.path.join(REPO, "world", "hydro.npz"))
    elev, water, arc, bear = r["elev"].astype(float), r["water"], r["arc"], r["bear"]
    T, rain, grade, playa = hy["temp"], hy["rain"], hy["grade"], hy["playa"]
    nb, lat, lon, V = world_graph.load()
    VEC = np.asarray(V, dtype=np.float64)
    rng = np.random.default_rng(20260817)

    slope = np.array([np.abs(elev[x] - elev[i]).max() for i, x in enumerate(nb)])
    # 🔴 the first cut took max(rank(rain), rank(frost)) and painted the nightside as
    # CONCENTRIC RINGS - frost was a pure function of T, T is a pure function of arc,
    # so every band came out a circle. Two fixes, both physical:
    #   * ice is PATCHY. It collects in hollows and survives in shadow, so where a
    #     glacier actually lies is a field of its own, not a latitude.
    #   * add the two water sources, then rank ONCE. Ranking each separately and
    #     taking the max declared half the planet wet.
    gl = wr.sphere_noise(VEC, np.random.default_rng(4242),
                         octaves=[(2.5, 1.0), (5.0, 0.62), (11.0, 0.38),
                                  (23.0, 0.22), (47.0, 0.12)], waves=28)
    gl = (gl - gl.min()) / max(gl.max() - gl.min(), 1e-9)
    cover = np.clip(0.10 + 1.45 * gl - slope / 420.0, 0.0, 1.0)   # ice hates a ridge
    rain_n = np.clip(rain / max(np.percentile(rain[~water], 99), 1e-9), 0.0, 1.4)
    avail = rain_n + 1.25 * frost_water(T) * cover
    H = humidity_rank(avail, water)
    print("water: rain-fed %d tiles, ice-fed %d, both %d"
          % ((rain_n > 0.25).sum(),
             (1.25 * frost_water(T) * cover > 0.25).sum(),
             ((rain_n > 0.25) & (1.25 * frost_water(T) * cover > 0.25)).sum()))
    riv = riparian(nb, grade, playa)
    print("river-adjacent tiles (ribbon reach %d): %d"
          % (RIPARIAN_REACH, (riv <= RIPARIAN_REACH).sum()))

    name = classify(T, H, elev, arc, riv, grade, water, slope)
    awarp = wr.sphere_noise(VEC, np.random.default_rng(909),
                            octaves=[(4.0, 1.0), (9.0, 0.5), (19.0, 0.28)], waves=24)
    awarp = 2.8 * awarp / max(np.abs(awarp).max(), 1e-9)
    name = overrides(name, arc, bear, elev, T, H, water, riv, rng, awarp)

    keys = sorted(COLOUR)
    lab, moved = world_shape.despeckle(
        [keys.index(nm) if nm in COLOUR else 0 for nm in name], nb, min_size=4,
        protect={keys.index("Ocean"), keys.index("SeaIce"),
                 keys.index("AB_TarPits"), keys.index("HorrorWastes")})
    name = np.array([keys[k] for k in lab], dtype=object)
    print("despeckle moved %d tiles" % moved)

    lush = {"AB_FeraliskInfestedJungle", "ZBiome_DesertOasis", "Glowforest",
            "PoisonForest", "AB_GelatinousSuperorganism"}
    fixed = 0
    for i, nm in enumerate(name):
        if nm in lush and riv[i] > RIPARIAN_REACH and H[i] < 0.80:
            name[i] = "AridShrubland" if T[i] < 40 else "Desert"
            fixed += 1
    if fixed:
        print("demoted %d lush tiles the despeckle had stranded off water" % fixed)

    hill = hilliness(elev, slope, name, T)
    bad = audit(name, hill, riv, T, H, water, nb)

    np.savez_compressed(OUT_NPZ, name=np.array(list(name)), hill=hill,
                        humidity=H.astype(np.float32), riparian=riv)
    print("wrote", OUT_NPZ)
    wr.write_png(OUT_PNG, render(name, H, water, elev, VEC, nb))
    print("wrote", OUT_PNG, "(top: the planet; bottom: the humidity field)")
    return bad


if __name__ == "__main__":
    main()
