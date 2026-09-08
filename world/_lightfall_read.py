import sys, collections, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
geo={int(r['tile']):r for r in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"))}
nb={int(row['tile']):[int(row[f'n{i}']) for i in range(6) if int(row[f'n{i}'])>=0]
    for row in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\world_neighbors_sub7b.csv"))}
SPINE=[12253,15934,107,7924,1445,15951,9023]
def defs_of(v):
    out=[]
    for m in (v or []):
        out.append(m.get('def') if isinstance(m,dict) else m)
    return out
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    muts={}
    for lo in range(0,21872,5500):
        r=rb.call("jawa/world_mutators_get", {"range": f"{lo}-{min(lo+5499,21871)}", "limit": 6000})
        for m in r.get("tiles", r.get("mutators", [])):
            muts[m.get("tile")]=defs_of(m.get("mutators") or m.get("defs"))
    ring=set(SPINE)
    for t in SPINE: ring|=set(nb.get(t,[]))
    mc=collections.Counter()
    for t in ring:
        for d in muts.get(t,[]): mc[d]+=1
    print("Lightfall neighborhood mutator defs:", mc.most_common(12))
    for t in SPINE:
        g=geo[t]; print(f"  {t}: elev={g['elev_m']} hill={g['hilliness']} biome_now? muts={muts.get(t,[])}")
    CH={'Chasm','Caves','CaveLakes'}
    ct={t for t,ds in muts.items() if any(d in CH for d in ds)}
    seen=set(); comps=[]
    for t in ct:
        if t in seen: continue
        comp=[]; st=[t]
        while st:
            u=st.pop()
            if u in seen or u not in ct: continue
            seen.add(u); comp.append(u); st+=nb.get(u,[])
        comps.append(comp)
    comps.sort(key=len,reverse=True)
    print("chasm/cave mutator tiles:", len(ct), "| biggest clusters:", [len(c) for c in comps[:6]])
    print("9023 cluster size:", next((len(c) for c in comps if 9023 in c), 0))
    # Gray Crags biome now
    gc=collections.Counter()
    rr={}
    for i in range(0,21872,2000):
        x=rb.call("jawa/world_tile_get", {"range": f"{i}-{min(i+1999,21871)}", "limit": 2500})
        for t in x.get("tiles",[]): rr[t['tile']]=t['biome']
    gray=[t for t,g in geo.items() if g['region']=='Gray Crags']
    print("Gray Crags region biomes now:", collections.Counter(rr.get(t) for t in gray).most_common())
