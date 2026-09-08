import sys, collections, hashlib
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
def h(t,s): return int(hashlib.md5(f"{t}:{s}".encode()).hexdigest(),16)
# per-biome landmark palettes chosen from each sheet's theme; modest ~26% density (first pass)
PAL={
 'BiomeCypreJungle':      ['VEE_Cenotes','Valley','Oasis'],           # Greentide: river-jungle pools, folds, springs
 'AB_OcularForest':       ['TerraformingScar','Ruins','AncientGarrison'], # Contagion: the weapon site
 'AB_FeraliskInfestedJungle':['Cavern','Valley','VEE_SerpentineCanyons'], # Webwork: dense silk jungle
 'ZBiome_DesertOasis':    ['Oasis','VEE_Cenotes'],                    # Weeping Stones: the dew/oasis engine
 'AB_GelatinousSuperorganism':['VEE_Cenotes','Cavern'],              # Slime: pits
 'Scarlands':             ['Ruins','AncientGarrison','TerraformingScar'], # Rakatan last stand battlefield
 'ZBiome_Grasslands':     ['TerraformingScar','Ruins','VEE_DryRiver'], # Pyrelands: fire-scarred
 'ZBiome_Badlands':       ['DryLake','VEE_DryRiver','Valley'],        # Cracked Lands: the flood
}
DENS=26
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    biome={}
    for i in range(0,21872,2000):
        rr=rb.call("jawa/world_tile_get", {"range": f"{i}-{min(i+1999,21871)}", "limit": 2500})
        for t in rr.get("tiles",[]): biome[t["tile"]]=t["biome"]
    lm=rb.call("jawa/world_landmarks_get", {"limit":6000})
    haslm={l['tile'] for l in lm.get("landmarks",[])}
    plan={}
    for t,b in biome.items():
        if b not in PAL or t in haslm: continue
        if h(t,'cov')%100 >= DENS: continue
        pal=PAL[b]; plan[t]=pal[h(t,'d')%len(pal)]
    print("dense-biome first pass:", len(plan), "landmarks |", dict(collections.Counter(plan.values())))
    for d in set(plan.values()):
        tiles=[t for t,dd in plan.items() if dd==d]
        for i in range(0,len(tiles),800):
            rb.call("jawa/world_landmarks_set", {"tiles":",".join(map(str,tiles[i:i+800])),"def":d})
    rb.call("jawa/world_commit", {})
    lm2=rb.call("jawa/world_landmarks_get", {"limit":8000})
    got={l['tile']:l['def'] for l in lm2.get("landmarks",[])}
    ok=sum(1 for t,d in plan.items() if got.get(t)==d)
    print(f"READ BACK: {ok}/{len(plan)} placed")
    import json; json.dump([{'tile':t,'def':d} for t,d in plan.items()], open(r"D:\Luke\dev\Rimworld\world\dense_biomes_plan.json",'w'))
