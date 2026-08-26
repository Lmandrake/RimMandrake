"""THE ABANDONED MINES - an Oxalyte operation the old company walked away from.

Owner, 2026-08-26: *"We MUST add something at 4.89S 59.16 to be the Oxalyte mining operation
that was abandoned by the old mining company a century ago. Maybe copious ruined buildings in
the area... if there are tile modifiers saying anything about ore and mining, it's time to use
them copiously. These should stretch from roughly this location all the way to The Unfinished
Work through the mountains and road regions. A placename should be added 'The Abandoned Mines'"*

Anchors, measured: the head is **tile 9171** (lat -4.887, lon 59.160 - a 0.003 deg hit on the
coordinate; Desert, 718 m, hilliness 4, Ashfall Range) and the foot is **The Unfinished Work,
tile 7722** (Notch, AridShrubland, 20 m). 14 deg of corridor down out of the range.

🔑 THE GATES GIVE THE OPERATION ITS SHAPE, so it is not decorated at random:
   `AncientQuarry`  min hilliness MOUNTAINOUS -> the workings, high in the range
   `Junkyard`       max hilliness SMALLHILLS  -> the spoil yards, down at the Notch end
   `MineralRich`    blacklisted on 5 biomes only -> the ore province, the whole length
   `VEE_DeepOreRich` ungated                   -> what the deep drills were after
⛔ `VEE_MineralDevoid` / `VEE_DeepOreDevoid` are the OPPOSITES and 1,455 tiles carry each of
them. They are removed wherever the rich pair goes in, or the tile would claim both.

⛔ No RNG - every choice is a hash of the tile id or a terrain threshold.
"""
import sys, json, collections
sys.path.insert(0, '/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *
from field import build
from route import Router

HEAD, FOOT = 9171, 7722
F = build(); tiles, nb, lm = F['tiles'], F['nb'], F['lm']
water = {t for t in tiles if tiles[t]['water']}
setl = {o['tile'] for o in F['setts']}
h = lambda t: (t * 2654435761) % 100

rt = Router(F)
spine = rt.route(HEAD, FOOT, comfort_w=0.0, straight_w=0.30, turn_w=0.35, pad=7.0)
print("spine %d tiles, %.1f deg" % (len(spine), gcdeg(tiles, HEAD, FOOT)))

# dilate: the ore province is a belt, wider where the ground is broken
belt = {}
for i, t in enumerate(spine):
    belt[t] = 0
    w = 2 if tiles[t]['hill'] >= 3 else 1
    frontier = {t}
    for r in range(1, w + 1):
        nxt = set()
        for x in frontier:
            for n in nb[x]:
                if n in water or n in belt or n in setl: continue
                nxt.add(n); belt[n] = r
        frontier = nxt
belt = {t: d for t, d in belt.items() if t not in water}
print("belt %d tiles (core %d, ring1 %d, ring2 %d)"
      % (len(belt), sum(1 for v in belt.values() if v == 0),
         sum(1 for v in belt.values() if v == 1), sum(1 for v in belt.values() if v == 2)))
print("regions: %s" % collections.Counter(tiles[t]['region'] for t in belt).most_common(6))
print("hilliness: %s" % dict(collections.Counter(tiles[t]['hill'] for t in belt)))
print("biomes: %s" % collections.Counter(tiles[t]['biome'] for t in belt).most_common(6))

add = collections.defaultdict(list)     # mutator -> tiles
rem = collections.defaultdict(list)

for t, d in sorted(belt.items()):
    tt = tiles[t]
    # --- the ore province: the whole belt is why anyone came here -------
    add['MineralRich'].append(t); rem['VEE_MineralDevoid'].append(t)
    if d <= 1 and h(t) < 70:
        add['VEE_DeepOreRich'].append(t); rem['VEE_DeepOreDevoid'].append(t)
    # --- the workings, high and broken ---------------------------------
    if tt['hill'] >= 4 and h(t) < 55:
        add['AncientQuarry'].append(t)
    # --- the spoil yards, low and flat ---------------------------------
    elif tt['hill'] <= 2 and h(t) < 40:
        add['Junkyard'].append(t)
    # --- the buildings they left ---------------------------------------
    # 🔑 "copious ruined buildings" - dense on the spine, thinning outward, so the
    # ruin field has a centre of gravity along the haul route rather than an even wash.
    g = h(t)
    if d == 0:
        if   g < 34: add['AncientRuins'].append(t)
        elif g < 52: add['AncientWarehouse'].append(t)
        elif g < 66: add['AncientChemfuelRefinery'].append(t)
        elif g < 78: add['AbandonedColonyOutlander'].append(t)
    elif d == 1:
        if   g < 30: add['AncientRuins'].append(t)
        elif g < 46: add['AncientWarehouse'].append(t)
        elif g < 56: add['AbandonedColonyOutlander'].append(t)
        elif g < 64: add['AncientChemfuelRefinery'].append(t)
    else:
        if   g < 26: add['AncientRuins'].append(t)
        elif g < 38: add['AncientWarehouse'].append(t)
    if tt['hill'] >= 3 and 80 <= g < 92: add['AncientGarrison'].append(t)
    if tt['hill'] <= 2 and 92 <= g < 99: add['TerraformingScar'].append(t)

print("\nPLAN")
for k in sorted(add, key=lambda x: -len(add[x])):
    print("   add %-28s %3d" % (k, len(add[k])))
for k in sorted(rem):
    print("   rem %-28s %3d" % (k, len(rem[k])))
json.dump({'belt': {str(k): v for k, v in belt.items()},
           'add': {k: v for k, v in add.items()},
           'rem': {k: v for k, v in rem.items()},
           'spine': spine}, open(R + 'mines_plan.json', 'w'))
