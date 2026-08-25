import json,csv,math,collections
B='/mnt/d/Luke/dev/Rimworld/world/'
O=B+'_organic/'

def load():
    tiles={}
    for r in csv.DictReader(open(B+'_now2.csv')):
        t=int(r['tile'])
        tiles[t]=dict(tile=t,lat=float(r['lat']),lon=float(r['long']),biome=r['biome'],
            elev=float(r['elevation']),temp=float(r['temperature']),rain=float(r['rainfall']),
            hill=r['hilliness'],swamp=float(r['swampiness']),riverDist=float(r['riverDist'] or 0),
            feature=r['feature'],water=int(r['waterCovered']),roads=int(r['roadCount']),
            rivers=int(r['riverCount']),muts=int(r['mutatorCount']))
    nb={}
    for r in csv.DictReader(open(O+'neighbors.csv')):
        t=int(r['tile']); nb[t]=[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0]
    links=json.load(open(O+'links_raw.json'))
    roads=collections.defaultdict(dict)   # a -> {b: def}
    for l in links:
        for pr in l['potentialRoads']:
            roads[l['tile']][pr['neighbor']]=pr['def']
    objs=json.load(open(O+'objects.json'))
    setts=[o for o in objs if o['isSettlement']]
    return tiles,nb,roads,setts,objs

def xyz(tt):
    la=math.radians(tt['lat']); lo=math.radians(tt['lon'])
    return (math.cos(la)*math.cos(lo), math.cos(la)*math.sin(lo), math.sin(la))
def gcdeg(a,b):
    d=sum(x*y for x,y in zip(xyz(a),xyz(b))); d=max(-1,min(1,d))
    return math.degrees(math.acos(d))

def bfs_ring(nb,src,maxd):
    """tile -> hex distance, out to maxd"""
    seen={src:0}; frontier=[src]
    for d in range(1,maxd+1):
        nxt=[]
        for t in frontier:
            for n in nb[t]:
                if n not in seen: seen[n]=d; nxt.append(n)
        frontier=nxt
        if not frontier: break
    return seen

import math as _m
def vnoise(lat,lon,freq,seed):
    """coherent value noise on the sphere-ish lat/lon lattice, bilinear."""
    x=(lon+180.0)/360.0*freq; y=(lat+90.0)/180.0*freq
    x0=int(_m.floor(x)); y0=int(_m.floor(y)); fx=x-x0; fy=y-y0
    def h(i,j):
        n=(i*374761393+j*668265263+seed*1442695040888963407)&0xffffffffffff
        n=(n^(n>>13))*1274126177&0xffffffffffff
        return ((n>>11)&65535)/65535.0
    def sm(t): return t*t*(3-2*t)
    sx,sy=sm(fx),sm(fy)
    a=h(x0,y0)+(h(x0+1,y0)-h(x0,y0))*sx
    b=h(x0,y0+1)+(h(x0+1,y0+1)-h(x0,y0+1))*sx
    return a+(b-a)*sy
