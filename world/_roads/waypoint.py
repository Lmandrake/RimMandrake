"""Why a desert track bends: it goes VIA things.

🔴 Measured 2026-08-26, and this is the finding that decided the whole pass. In Ash'karr's
barren country there is NO gradient to steer by - the six neighbours of a Long Sand tile
carry comfort 0.12-0.14 and a median elevation step of 2-6 m. A comfort weight there scales
every candidate equally and never changes the argmin; four sweeps from 0.45 to 0.90 returned
byte-identical routes. ⛔ So bending those roads by TUNING is inventing a reason the map
cannot show.

✅ What a real desert track bends for is a REASON ON THE GROUND: a well, the lee of a cliff,
a wadi, a ruin worth stopping at. Insert those as waypoints and the meander is explicable -
a reader can see why the road went south, because the cenote is there.

The insertion is greedy on length-added-per-unit-value and stops at a sinuosity ceiling, so
a road never detours further than the thing is worth.
"""
import sys, math
sys.path.insert(0, '/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import gcdeg

# what is worth a detour, and how much
VALUE = {
    'Oasis': 1.00, 'VEE_Cenotes': 0.95, 'HotSprings': 0.85, 'VEE_StagnantRivulet': 0.60,
    'DryLake': 0.45, 'VEE_DryRiver': 0.55, 'VEE_AlluvialFan': 0.45,
    'Cliffs': 0.70, 'Valley': 0.70, 'Cavern': 0.75, 'Hollow': 0.60, 'Chasm': 0.55,
    'VEE_SerpentineCanyons': 0.70, 'VEE_RockRidge': 0.45, 'Plateau': 0.40, 'Basin': 0.45,
    'VEE_StoneForest': 0.40, 'VEE_MeteorCrater': 0.35,
    'Ruins': 0.55, 'AncientGarrison': 0.60, 'AncientWarehouse': 0.60, 'AncientQuarry': 0.50,
    'AncientChemfuelRefinery': 0.50, 'AbandonedColonyTribal': 0.45,
    'AbandonedColonyOutlander': 0.45, 'TerraformingScar': 0.30, 'AncientHeatVent': 0.35,
    'AncientLaunchSite': 0.70, 'FrozenRuins': 0.35, 'sw_DeadSarlacc': 0.45,
}

def tile_value(lm, t):
    return max((VALUE.get(d, 0.0) for d in lm.get(t, ())), default=0.0)

def insert(router, F, a, b, ceiling=1.70, max_wp=4, min_gain=0.10, climb_m=170.0):
    """Route a->b, greedily detouring via worthwhile tiles the corridor already holds.

    `min_gain` is value per unit of DETOUR PRICE, where the price is extra tiles walked
    PLUS extra metres climbed / `climb_m`. ⚠️ Measured 2026-08-26: pricing the detour in
    tiles alone raised total ascent 22,130 -> 28,532 m (+29%) while the owner had asked for
    EASIER terrain - a well on a shelf is not worth the climb to reach it.
    Returns (path, [waypoints used]).
    """
    tiles, lm = F['tiles'], F['lm']
    base = router.route(a, b)
    if base is None: return None, []
    chord = gcdeg(tiles, a, b)
    if chord < 1e-6: return base, []

    def arclen(p):
        return sum(gcdeg(tiles, p[i], p[i + 1]) for i in range(len(p) - 1))

    def ascent(p):
        return sum(max(0.0, tiles[p[i + 1]]['elev'] - tiles[p[i]]['elev'])
                   for i in range(len(p) - 1))

    def stitch(seq):
        out = [seq[0]]
        for i in range(len(seq) - 1):
            leg = router.route(seq[i], seq[i + 1])
            if leg is None or len(leg) < 2: return None
            out += leg[1:]
        # a stitched route may double back on itself; drop the loop
        seen = {}
        clean = []
        for t in out:
            if t in seen:
                del clean[seen[t] + 1:]
                for k in list(seen):
                    if seen[k] > seen[t]: del seen[k]
            else:
                seen[t] = len(clean); clean.append(t)
        return clean

    step = chord / max(1, len(base) - 1)
    chosen, cur, cur_len, cur_up = [], base, arclen(base), ascent(base)
    on = set(base)
    cands = sorted(((tile_value(lm, t), t) for t in router.corridor(a, b, 7.0)
                    if tile_value(lm, t) > 0 and router.passable(t, {a, b})),
                   reverse=True)[:60]
    for _ in range(max_wp):
        best = None
        for val, t in cands:
            if t in on or t in chosen: continue
            seq = sorted(chosen + [t], key=lambda x: gcdeg(tiles, a, x))
            cand = stitch([a] + seq + [b])
            if cand is None: continue
            L, U = arclen(cand), ascent(cand)
            if L / chord > ceiling: continue
            price = (L - cur_len) / step + max(0.0, U - cur_up) / climb_m
            gain = 99.0 if price <= 0.01 else val / price
            if gain < min_gain: continue
            if best is None or gain > best[0]: best = (gain, t, cand, L, U)
        if best is None: break
        chosen.append(best[1]); cur, cur_len, cur_up = best[2], best[3], best[4]
        on = set(cur)
    return cur, chosen
