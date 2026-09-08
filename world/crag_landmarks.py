#!/usr/bin/env python3
"""Apply the Forsaken Crags sheet to the map: (1) LIGHTFALL, the one massive terminator
chasm (site+name owner-ratified, forsaken_crags.md §3, LIGHTFALL_CHASM_AUTHORING_1) on
the arc-90 spine, deepest at tile 9023; (2) the 'obsidian teeth' density -- Cliffs/Chasm/
Cavern/JaggedRocks across the crags so the hilliest biome reads dense, denser in the deep
regions, hash-gapped (~45%, anti-bullseye, deterministic). Skips tiles already carrying a
landmark. LandmarkDefs confirmed live: Cliffs, Chasm, Cavern, VEE_JaggedRocks."""
import sys, json, collections, csv, hashlib
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
LIGHTFALL_SPINE=[12253,15934,107,7924,1445,15951,9023]
DEEP={'Rimewall','Twilight Crags','Coldstone','Nightspill'}   # deep-dark regions
geo={int(r['tile']):r for r in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"))}
def h(t,salt): return int(hashlib.md5(f"{t}:{salt}".encode()).hexdigest(),16)
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    live={}
    for i in range(0,21872,2000):
        rr=rb.call("jawa/world_tile_get", {"range": f"{i}-{min(i+1999,21871)}", "limit": 2500})
        for t in rr.get("tiles",[]): live[t["tile"]]=t["biome"]
    crags={t for t,b in live.items() if b=='AB_RockyCrags'}
    lm=rb.call("jawa/world_landmarks_get", {"limit":3000})
    has_lm={l['tile'] for l in lm.get("landmarks",[])}
    # verify LIGHTFALL site
    site_ok=[t for t in LIGHTFALL_SPINE if live.get(t)=='AB_RockyCrags']
    print("LIGHTFALL spine still crags:", len(site_ok), "of", len(LIGHTFALL_SPINE), "->", [t for t in LIGHTFALL_SPINE if t not in site_ok],"not crags")
    # density plan
    plan={}   # tile -> landmark def
    for t in LIGHTFALL_SPINE:
        if live.get(t)=='AB_RockyCrags': plan[t]='Chasm'   # Lightfall = chasm complex
    cand=[t for t in crags if t not in has_lm and t not in plan]
    for t in cand:
        deep = geo[t]['region'] in DEEP
        thresh = 55 if deep else 35                        # deeper regions denser
        if h(t,'cover')%100 >= thresh: continue            # hash-gap
        r=h(t,'def')%100
        if deep:   d = 'Chasm' if r<25 else 'Cavern' if r<50 else 'Cliffs' if r<80 else 'VEE_JaggedRocks'
        else:      d = 'Cliffs' if r<45 else 'VEE_JaggedRocks' if r<80 else 'Cavern'
        plan[t]=d
    print(f"crag landmark plan: {len(plan)} tiles ({len([t for t in plan if t not in LIGHTFALL_SPINE])} density + LIGHTFALL) | by def:", dict(collections.Counter(plan.values())))
    json.dump([{'tile':t,'def':d} for t,d in plan.items()], open(r"D:\Luke\dev\Rimworld\world\crag_landmarks_plan.json",'w'))
    # apply grouped by def
    for d in set(plan.values()):
        tiles=[t for t,dd in plan.items() if dd==d]
        for i in range(0,len(tiles),800):
            ch=tiles[i:i+800]
            rr=rb.call("jawa/world_landmarks_set", {"tiles":",".join(map(str,ch)), "def":d})
            print(f"  {d}: +{rr.get('added')} (of {len(ch)}) success={rr.get('success')}")
    c=rb.call("jawa/world_commit", {}); print("commit:", c.get("success"), "failed", c.get("failedSteps"))
    # read back
    lm2=rb.call("jawa/world_landmarks_get", {"limit":4000})
    got={l['tile']:l['def'] for l in lm2.get("landmarks",[])}
    ok=sum(1 for t,d in plan.items() if got.get(t)==d)
    print(f"READ BACK: {ok}/{len(plan)} landmarks present as planned")
    lf=[t for t in LIGHTFALL_SPINE if got.get(t)=='Chasm']
    print(f"LIGHTFALL chasm tiles confirmed: {len(lf)}/{len(site_ok)} incl 9023={got.get(9023)}")
