import sys, collections, csv, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
geo={int(r['tile']):r for r in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"))}
nb={int(row['tile']):[int(row[f'n{i}']) for i in range(6) if int(row[f'n{i}'])>=0]
    for row in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\world_neighbors_sub7b.csv"))}
SPINE=[12253,15934,107,7924,1445,15951,9023]
# Damp chain candidate = the ruled site window: arc 87-93, lat -37..-64, lon 86..97
cand=[t for t,g in geo.items() if 87<=float(g['arc'])<=93 and -64<=float(g['lat'])<=-37 and 86<=float(g['lon'])<=97]
# plus the spine's 1-ring (contiguity)
ring=set(cand)|set(SPINE)
for t in list(SPINE): ring|=set(nb.get(t,[]))
ring=list(ring)
host, port, token = resolve_endpoint()
def defs_of(v):
    return [(m.get('def') if isinstance(m,dict) else m) for m in (v or [])]
with RimBridge(host, port, token) as rb:
    # targeted read: mutators + tile info for the candidate set only (light)
    info=rb.call("jawa/world_tile_get", {"tiles":",".join(map(str,ring)), "limit":200}).get("tiles",[])
    binfo={t['tile']:t for t in info}
    mut=rb.call("jawa/world_mutators_get", {"tiles":",".join(map(str,ring)), "limit":200})
    muts={m.get('tile'):defs_of(m.get('mutators') or m.get('defs')) for m in mut.get('tiles', mut.get('mutators',[]))}
    lm=rb.call("jawa/world_landmarks_get", {"limit":4000})
    haslm={l['tile']:l['def'] for l in lm.get('landmarks',[])}
    # score: chasm-worthy = mountainous/deep + carries cave/chasm mutator
    CAVE={'Chasm','Caves','CaveLakes'}
    scored=[]
    for t in ring:
        b=binfo.get(t,{})
        hill=b.get('hilliness',''); elev=b.get('elevation',0)
        cave=any(d in CAVE for d in muts.get(t,[]))
        score = (1 if hill in ('Mountainous','Impassable') else 0.5 if hill=='LargeHills' else 0) + (1 if cave else 0) + (0.3 if t in SPINE else 0)
        scored.append((score, t, hill, elev, cave, haslm.get(t)))
    scored.sort(reverse=True)
    print("candidate window:", len(cand), "tiles | ring:", len(ring))
    print("cave/chasm mutator tiles in window:", sum(1 for t in ring if any(d in CAVE for d in muts.get(t,[]))))
    print("top-18 chasm-worthy (score,tile,hill,elev,cave,landmark):")
    for s in scored[:18]: print("  ", s)
    # select the enlarged Lightfall: spine + highest-scoring contiguous tiles up to ~15
    sel=set(SPINE)
    for s,t,hill,elev,cave,cur in scored:
        if len(sel)>=15: break
        if s>=1.0: sel.add(t)
    sel=list(sel)
    json.dump([{'tile':t,'def':'Chasm'} for t in sel], open(r"D:\Luke\dev\Rimworld\world\lightfall_enlarge_plan.json",'w'))
    print(f"\nENLARGED LIGHTFALL selection: {len(sel)} tiles")
