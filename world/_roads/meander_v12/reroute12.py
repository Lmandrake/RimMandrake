"""Decompose the non-ancient road network into runs between fixed anchors and
reroute each over the comfort field. Ancient asphalt is never touched.

Mechanism is route.py's Router (STRAIGHT_W 0.55, TURN_W 0.30, untouched) and
waypoint.py's insert(). Only the corridor scan is accelerated with numpy - same
predicate, same result set.
"""
import sys, os, json, time, math, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import numpy as np
from field12 import build
from load12 import gcdeg, undirected
from route import Router
from waypoint import insert

ARC = 0.934
ANCIENT_PREFIX = 'AncientAsphalt'
COLD = -10.0
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 0


class FastRouter(Router):
    def __init__(self, F, forbid=()):
        Router.__init__(self, F, forbid=forbid)
        self.ids = np.array(sorted(self.tiles), dtype=np.int64)
        self.P = np.array([self.vec[int(t)] for t in self.ids], dtype=np.float64)

    def corridor(self, a, b, pad):
        va = np.array(self.vec[a]); vb = np.array(self.vec[b])
        aa = np.degrees(np.arccos(np.clip(self.P @ va, -1.0, 1.0)))
        ab = np.degrees(np.arccos(np.clip(self.P @ vb, -1.0, 1.0)))
        lim = self._ang(self.vec[a], self.vec[b]) + pad
        return set(self.ids[(aa + ab) <= lim + 1e-9].tolist())


def main():
    F = build()
    tiles, roads, setts = F['tiles'], F['roads'], F['setts']
    sett_tile = {o['tile'] for o in setts}

    E = undirected(roads)
    anc = {e: roads[e[0]][e[1]] for e in E
           if roads[e[0]][e[1]].startswith(ANCIENT_PREFIX)}
    non = {e: roads[e[0]][e[1]] for e in E if e not in anc}

    g = collections.defaultdict(set)
    for a, b in non:
        g[a].add(b); g[b].add(a)
    degf = {t: len(d) for t, d in roads.items()}

    nodes = {t for t in g if len(g[t]) != 2}
    nodes |= {t for t in g if degf.get(t, 0) != len(g[t])}   # touches ancient
    nodes |= (set(g) & sett_tile)

    runs, seen = [], set()

    def key(a, b):
        return (a, b) if a < b else (b, a)

    def walk(a, b):
        path = [a, b]
        while len(g[path[-1]]) == 2 and path[-1] not in nodes:
            nxts = [x for x in g[path[-1]] if x != path[-2]]
            if not nxts:
                break
            path.append(nxts[0])
        return path

    for n in sorted(nodes):
        for m in sorted(g[n]):
            if key(n, m) in seen:
                continue
            p = walk(n, m)
            for i in range(len(p) - 1):
                seen.add(key(p[i], p[i + 1]))
            runs.append(p)
    for a in sorted(g):
        for b in sorted(g[a]):
            if key(a, b) in seen:
                continue
            p = walk(a, b)
            for i in range(len(p) - 1):
                seen.add(key(p[i], p[i + 1]))
            runs.append(p)

    print("ANCIENT %d edges   NON-ANCIENT %d edges" % (len(anc), len(non)))
    print("RUNS %d  (edges covered %d of %d)" % (len(runs), len(seen), len(non)))
    assert len(seen) == len(non), (len(seen), len(non))

    # anchors never move; nothing else is fixed
    anchors = set()
    for p in runs:
        anchors.add(p[0]); anchors.add(p[-1])

    forbid = set(sett_tile) - anchors
    forbid |= {t for t in tiles if tiles[t]['temp'] < COLD} - anchors
    rt = FastRouter(F, forbid=forbid)

    def steps_len(p):
        return len(p) - 1

    def sinu(p):
        """Exact: walked arc / great-circle chord. No ARC constant."""
        if len(p) < 2:
            return None
        c = gcdeg(tiles, p[0], p[-1])
        if c < 1e-6:
            return None
        L = sum(gcdeg(tiles, p[i], p[i + 1]) for i in range(len(p) - 1))
        return L / c

    def straight_legs(p):
        """Maximal chains of consecutive steps that HOLD a bearing (route.py's
        cos>0.93 test). Returns the longest such chain, in steps."""
        if len(p) < 3:
            return len(p) - 1
        best = cur = 1
        for i in range(1, len(p) - 1):
            u = rt._unit(p[i - 1], p[i]); v = rt._unit(p[i], p[i + 1])
            cs = sum(x * y for x, y in zip(u, v))
            if cs > 0.93:
                cur += 1
                best = max(best, cur)
            else:
                cur = 1
        return best

    out, t0 = [], time.time()
    todo = runs[:LIMIT] if LIMIT else runs
    for i, old in enumerate(todo):
        a, b = old[0], old[-1]
        rec = dict(a=a, b=b, path=old, new=old, via=[], note='')
        if a != b and len(old) >= 3 and gcdeg(tiles, a, b) >= 1.4:
            p, wp = insert(rt, F, a, b)
            if p is not None and p[0] == a and p[-1] == b:
                rec['new'] = p; rec['via'] = wp
            else:
                rec['note'] = 'reroute refused'
        else:
            rec['note'] = 'too short'
        out.append(rec)
        if (i + 1) % 20 == 0:
            print("  %3d/%d  %.0fs" % (i + 1, len(todo), time.time() - t0))

    json.dump(out, open(os.path.join(HERE, 'rerouted_v12.json'), 'w'))
    json.dump({'%d,%d' % k: v for k, v in anc.items()},
              open(os.path.join(HERE, 'ancient_edges.json'), 'w'))

    def rep(tag, keyname):
        s = [sinu(r[keyname]) for r in out if sinu(r[keyname])]
        L = [straight_legs(r[keyname]) for r in out]
        print("%-7s runs %d  sinuosity mean %.3f med %.3f   straight-leg mean %.2f max %d"
              % (tag, len(out), sum(s) / len(s), sorted(s)[len(s) // 2],
                 sum(L) / float(len(L)), max(L)))
    rep('BEFORE', 'path')
    rep('AFTER', 'new')
    print("edges before %d -> after %d" % (sum(steps_len(r['path']) for r in out),
                                           sum(steps_len(r['new']) for r in out)))
    print("%.0fs" % (time.time() - t0))


if __name__ == '__main__':
    main()
