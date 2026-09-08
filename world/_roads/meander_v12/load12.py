"""Current-lineage loader for the v12 meander pass.

Replaces rcommon.load(), which reads the DEPRECATED lineage's cached artefacts.
Everything here comes from either the frozen canon tiles CSV or the live harvest
in this directory.

temp_min_c / temp_max_c are NOT in the canon CSV. They are recovered as
temp +/- A(|lat|), where A is read off the old lineage's export purely as a
LATITUDE->seasonal-amplitude table: it is a function of planet geometry only
(verified: the 2835 distinct |lat| values are identical between lineages, and
tmax-temp == temp-tmin == |seasonal_shift_c| on every row).
"""
import csv, json, collections, math, os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
W = os.path.join(REPO, 'world')
V = os.path.join(W, '_roads', 'meander_v12')


def _amp_table():
    amp = {}
    with open(os.path.join(W, '_roads', 'base_tiles.csv')) as fh:
        for r in csv.DictReader(fh):
            amp[round(abs(float(r['lat'])), 4)] = abs(float(r['seasonal_shift_c']))
    return amp


def load():
    amp = _amp_table()
    tiles = {}
    with open(os.path.join(W, 'ASHKARR_WORLDMAP_tiles.csv')) as fh:
        for r in csv.DictReader(fh):
            t = int(r['tile'])
            temp = float(r['temp_c'])
            a = amp.get(round(abs(float(r['lat'])), 4), 0.0)
            tiles[t] = dict(tile=t, lat=float(r['lat']), lon=float(r['lon']),
                            arc=float(r['arc']), biome=r['biome'],
                            elev=float(r['elev_m']), temp=temp,
                            rain=float(r['rain_mm']), hill=int(r['hilliness']),
                            swamp=float(r['swampiness']), region=r['region'],
                            water=int(r['water']), riverDist=0.0,
                            tmin=temp - a, tmax=temp + a)
    nb = {}
    with open(os.path.join(W, 'world_neighbors_sub7b.csv')) as fh:
        for r in csv.DictReader(fh):
            nb[int(r['tile'])] = [int(r['n%d' % i]) for i in range(6)
                                  if int(r['n%d' % i]) >= 0]
    roads = collections.defaultdict(dict)
    rivers = collections.defaultdict(dict)
    allow = {}
    allow_r = {}
    hidden = []
    with open(os.path.join(V, 'links_live_before.json')) as fh:
        chunks = json.load(fh)
    for ch in chunks:
        for l in ch['tiles']:
            t = l['tile']
            allow[t] = l['allowRoads']
            allow_r[t] = l['allowRivers']
            tiles[t]['riverDist'] = float(l.get('riverDist') or 0)
            if l['hiddenByBiome']:
                hidden.append(t)
            for pr in l['potentialRoads']:
                roads[t][pr['neighbor']] = pr['def']
            for pr in l['potentialRivers']:
                rivers[t][pr['neighbor']] = pr['def']
    with open(os.path.join(V, 'objects_before.json')) as fh:
        objs = json.load(fh)['objects']
    setts = [o for o in objs if o.get('def') == 'Settlement']
    lm = collections.defaultdict(list)
    with open(os.path.join(V, 'landmarks_before.json')) as fh:
        for l in json.load(fh)['landmarks']:
            lm[l['tile']].append(l['def'])
    return dict(tiles=tiles, nb=nb, roads=roads, rivers=rivers, setts=setts,
                objs=objs, allow=allow, allow_rivers=allow_r, lm=lm,
                hidden=hidden)


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
