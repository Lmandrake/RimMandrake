"""Shared loader for the road pass. Live-harvested artefacts only."""
import json, csv, math, collections, os
B = '/mnt/d/Luke/dev/Rimworld/world/'
R = B + '_roads/'

def load():
    tiles = {}
    for r in csv.DictReader(open(R + 'base_tiles.csv')):
        t = int(r['tile'])
        tiles[t] = dict(tile=t, lat=float(r['lat']), lon=float(r['lon']),
                        biome=r['biome'], elev=float(r['elev_m']),
                        temp=float(r['temp_c']), rain=float(r['rain_mm']),
                        hill=int(r['hilliness']), swamp=float(r['swampiness']),
                        region=r['region'], water=int(r['water']),
                        riverDist=float(r['river_dist'] or 0),
                        rivers=int(r['river_count']), roads=int(r['road_count']),
                        tmin=float(r['temp_min_c']), tmax=float(r['temp_max_c']))
    nb = {}
    for r in csv.DictReader(open(B + 'world_neighbors_sub7b.csv')):
        t = int(r['tile'])
        nb[t] = [int(r['n%d' % i]) for i in range(6) if int(r['n%d' % i]) >= 0]
    roads = collections.defaultdict(dict)
    rivers = collections.defaultdict(dict)
    for ch in json.load(open(R + '_links_raw.json')):
        for l in ch['tiles']:
            for pr in l['potentialRoads']:
                roads[l['tile']][pr['neighbor']] = pr['def']
            for pr in l['potentialRivers']:
                rivers[l['tile']][pr['neighbor']] = pr['def']
    objs = json.load(open(R + '_objects.json'))['objects']
    setts = [o for o in objs if o['isSettlement']]
    return tiles, nb, roads, rivers, setts, objs

def xyz(tt):
    la = math.radians(tt['lat']); lo = math.radians(tt['lon'])
    return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))

def gcdeg(tiles, a, b):
    d = sum(x * y for x, y in zip(xyz(tiles[a]), xyz(tiles[b])))
    return math.degrees(math.acos(max(-1.0, min(1.0, d))))

def undirected(g):
    out = set()
    for a, d in g.items():
        for b in d:
            out.add((a, b) if a < b else (b, a))
    return out
