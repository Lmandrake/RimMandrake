import csv, math, collections, json, sys
W="/mnt/d/Luke/dev/Rimworld/world/"
tiles={}
for r in csv.DictReader(open(W+"_verify/live_tiles.csv")):
    t=int(r["tile"]); tiles[t]=dict(r); tiles[t]["tile"]=t
nb={}
for row in csv.reader(open(W+"world_neighbors_sub7b.csv")):
    if row[0]=="tile": continue
    nb[int(row[0])]=[int(x) for x in row[1:] if int(x)>=0]
RANK={"Creek":1,"River":2,"LargeRiver":3,"HugeRiver":4}
adj=collections.defaultdict(set); defs={}
for l in csv.DictReader(open(W+"_verify/live_links.csv")):
    if l["kind"]!="river": continue
    a,b=int(l["a"]),int(l["b"]); adj[a].add(b); adj[b].add(a)
    for x in (a,b): defs[x]=max(defs.get(x,""),l["def"],key=lambda y:RANK.get(y,0))
mut={int(r["tile"]):[x for x in r["mutators"].split(";") if x] for r in csv.DictReader(open(W+"_verify/live_mutators.csv"))}
comp={}; cid=0
for s in adj:
    if s in comp: continue
    st=[s]
    while st:
        x=st.pop()
        if x in comp: continue
        comp[x]=cid; st.extend(adj[x])
    cid+=1
size=collections.Counter(comp.values())
def vec(la,lo):
    la,lo=math.radians(la),math.radians(lo)
    return (math.cos(la)*math.cos(lo),math.cos(la)*math.sin(lo),math.sin(la))
def find(lat,lon):
    tv=vec(lat,lon)
    return min(tiles.values(), key=lambda d: -sum(x*y for x,y in zip(tv,vec(float(d["lat"]),float(d["lon"])))))["tile"]
def report(lat,lon,rings=3):
    t=find(lat,lon); d=tiles[t]
    print("=== %.2f %.2f -> tile %d (%.2fN %.2fE) ==="%(lat,lon,t,float(d["lat"]),float(d["lon"])))
    print("  %-24s %sm  temp %s  arc %s  hill %s  region %s"%(d["biome"],d["elev_m"],d["temp_c"],d["arc"],d["hilliness"],d["region"]))
    print("  river: %s  def %s  deg %s  system %s(size %s)  mutators %s"%(
        t in adj, defs.get(t,"-"), len(adj.get(t,[])), comp.get(t), size.get(comp.get(t)), mut.get(t)))
    seen={t:0}; fr=[t]
    for k in range(1,rings+1):
        nx=[]
        for x in fr:
            for n in nb[x]:
                if n not in seen: seen[n]=k; nx.append(n)
        fr=nx
    riv=[x for x in seen if x in adj]
    print("  river tiles within %d hexes: %d in systems %s"%(rings,len(riv),
          collections.Counter(comp[x] for x in riv)))
    for x in sorted(riv,key=lambda x:float(tiles[x]["elev_m"])):
        print("    %5d %-11s %6sm deg%d sys%-2d %-16s %-24s -> %s"%(
            x,defs[x],tiles[x]["elev_m"],len(adj[x]),comp[x],tiles[x]["region"],tiles[x]["biome"],
            sorted(adj[x])))
    return t,seen
if __name__=="__main__":
    import sys
    for a in sys.argv[1:]:
        la,lo=a.split(","); report(float(la),float(lo)); print()
