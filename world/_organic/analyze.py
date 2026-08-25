import json,csv,math,collections,statistics as st
B='/mnt/d/Luke/dev/Rimworld/world/'
objs=json.load(open(B+'_organic/objects.json'))
tiles={int(r['tile']):r for r in csv.DictReader(open(B+'_now2.csv'))}
links={l['tile']:l for l in json.load(open(B+'_organic/links_raw.json'))}
deg=collections.defaultdict(int)
for tid,l in links.items(): deg[tid]=len(l['potentialRoads'])
S=[o for o in objs if o['isSettlement']]
def xyz(t):
    r=tiles[t]; la=math.radians(float(r['lat'])); lo=math.radians(float(r['long']))
    return (math.cos(la)*math.cos(lo), math.cos(la)*math.sin(lo), math.sin(la))
def gc(a,b):
    A,Bv=xyz(a),xyz(b); d=sum(x*y for x,y in zip(A,Bv)); d=max(-1,min(1,d))
    return math.degrees(math.acos(d))
pos={o['tile']:o for o in S}
T=[o['tile'] for o in S]
nn={}
for a in T:
    nn[a]=min(gc(a,b) for b in T if b!=a)
vals=list(nn.values())
print('SETTLEMENTS %d  nearest-neighbour separation (great-circle degrees)'%len(T))
print('  mean %.2f  median %.2f  sd %.2f  CV %.3f  min %.2f  max %.2f'%(
   st.mean(vals),st.median(vals),st.pstdev(vals),st.pstdev(vals)/st.mean(vals),min(vals),max(vals)))
h=collections.Counter(round(v) for v in vals)
print('  histogram (deg):', dict(sorted(h.items())))
print()
print('ROAD DEGREE at settlement tiles, by faction')
for f in sorted({o['factionName'] for o in S}):
    ss=[o for o in S if o['factionName']==f]
    dd=collections.Counter(deg[o['tile']] for o in ss)
    nnv=[nn[o['tile']] for o in ss]
    print('  %-26s n=%2d  deg=%s  nnMean=%.2f'%(f,len(ss),dict(sorted(dd.items())),st.mean(nnv)))
print()
print('HUTT (want deg>=3):')
for o in sorted([o for o in S if o['factionName']=='Hutt Cartel'],key=lambda o:deg[o['tile']]):
    r=tiles[o['tile']]
    print('  %-34s tile %6d deg %d  %-18s %-12s feat=%s'%(o['name'],o['tile'],deg[o['tile']],r['biome'],r['hilliness'],r['feature']))
print()
hdl=[o for o in S if o['factionName']=='Homestead Defense League']
print('HOMESTEAD/moisture farmers (want deg==1, remote): n=%d'%len(hdl))
dd=collections.Counter(deg[o['tile']] for o in hdl); print('  degree spread', dict(sorted(dd.items())))
print('  nn separation: mean %.2f sd %.2f CV %.3f'%(st.mean([nn[o['tile']] for o in hdl]),
      st.pstdev([nn[o['tile']] for o in hdl]), st.pstdev([nn[o['tile']] for o in hdl])/st.mean([nn[o['tile']] for o in hdl])))
