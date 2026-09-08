"""field.py's comfort field, fed the CURRENT lineage's inputs.

The mechanism (weights, seeds, spreads) is field.py's, verbatim. Only the loader
changes: load12.load() instead of the deprecated rcommon.load().
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from load12 import load
from field import SHADE_LM, WATER_LM, RUIN_LM, CANOPY


def build():
    F = load()
    tiles, nb, lm = F['tiles'], F['nb'], F['lm']
    allow = F['allow']

    def spread(seed, maxd):
        d = {t: 0 for t in seed}; fr = list(seed)
        for k in range(1, maxd + 1):
            nx = []
            for t in fr:
                for n in nb[t]:
                    if n not in d:
                        d[n] = k; nx.append(n)
            fr = nx
            if not fr:
                break
        return d

    shade_seed = {t for t, ds in lm.items() if set(ds) & SHADE_LM}
    water_seed = {t for t, ds in lm.items() if set(ds) & WATER_LM}
    water_seed |= {t for t in tiles if tiles[t]['water']}
    ruin_seed = {t for t, ds in lm.items() if set(ds) & RUIN_LM}
    ds_, dw_ = spread(shade_seed, 4), spread(water_seed, 5)

    river_t = set(F['rivers'])
    comfort, parts = {}, {}
    for t, tt in tiles.items():
        relief = min(1.0, max(0.0, (tt['hill'] - 1) / 3.0))
        near_shade = max(0.0, 1.0 - ds_.get(t, 9) / 4.0)
        shade = min(1.0, 0.60 * relief + 0.55 * near_shade)
        cool = min(1.0, max(0.0, (48.0 - tt['tmax']) / 55.0))
        canopy = CANOPY.get(tt['biome'], 0.35)
        near_water = max(0.0, 1.0 - dw_.get(t, 9) / 5.0)
        rd = tt['riverDist']
        near_river = 1.0 if 1 <= rd <= 3 else (0.5 if rd == 4 else 0.0)
        water = min(1.0, 0.70 * near_water + 0.45 * near_river)
        c = 0.30 * shade + 0.25 * cool + 0.20 * canopy + 0.25 * water
        comfort[t] = c
        parts[t] = (shade, cool, canopy, water)
    F.update(dict(comfort=comfort, parts=parts, river_t=river_t,
                  ruin_seed=ruin_seed, shade_seed=shade_seed,
                  water_seed=water_seed, ds=ds_, dw=dw_))
    return F
