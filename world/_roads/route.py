"""Route one road between two fixed tiles, over the comfort field.

🔴 ELEVATION IS A HARD CONSTRAINT, not a soft cost. references/river-networks.md §4 records
what happens otherwise: costing a climb softly routed a creek over a 1128 m ridge. A
per-step ascent CAP is the fix. ⚠️ But the cap must not be tighter than the country: a
180 m cap made every crags road detour 2.5x round a pass a real road would simply climb.

🔴 A BOUNDED bonus, never an exponent. `exp(-3*comfort)` made a lush tile cost an EIGHTH
of a barren one, which buys a detour of seven tiles - measured sinuosity 2.49 on an 8-step
run. Base 1.0 per step minus a bonus capped at 0.45 means a detour must SAVE more than it
COSTS, and sinuosity lands where meandering roads actually live.

🔑 Shade is the LEE of relief, not the relief itself. Walking over a mountain is work;
walking along its foot is shade. So hilliness on the tile is a penalty while a hilliness-3+
NEIGHBOUR under low hilliness is a bonus.

🔴 THE PENALTY IS ON HOLDING A BEARING, NOT ON TURNING. Measured 2026-08-26 and this is
what finally moved the map. A hex path from A to B spends the same number of steps whether
it runs eight tiles of one direction then five of another, or interleaves the two - the
LENGTH is identical and only the LOOK differs. A turn penalty buys the first (laser); a
STRAIGHT penalty buys the second (organic) for no extra distance at all. So `STRAIGHT_W` is
charged on a deflection of zero and `TURN_W` is left small, biting only on a hairpin.
⛔ It does not degenerate into a sawtooth: among the many equal-length interleavings the
terrain terms below decide which, so the phase of the wander is the ground's.

🔑 The ROUGHNESS term is what stops a night trail being a perfect geodesic. In country
with no shade and no water to steer toward, |dElev| is the only gradient left, so the road
picks its way between the dunes instead of ruling a line. It is the terrain's own wiggle.

⛔ No RNG anywhere. Owner, 2026-08-25: a seed is a knob that could roll a second planet.
"""
import sys, math, heapq
sys.path.insert(0, '/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import xyz

CLIMB_CAP  = 300.0     # m of ascent in one step; above this the step does not exist
COMFORT_W  = 0.45      # max discount off a 1.0 step
COMFORT_S  = 0.55      # comfort at which the discount saturates
CLIMB_W    = 1.0/120
DESC_W     = 1.0/1200
ROUGH_W    = 0.10/100  # per metre of |dElev| - prefers flat ground everywhere
HILL4_W    = 0.35
HILL3_W    = 0.12
LEE_W      = 0.18      # low ground with a range beside it: the shaded foot
RIDE_W     = 1.20      # a river tile entered FROM a river tile - riding the channel
FORD_W     = 0.20      # a river tile entered from dry land - a crossing
TURN_W     = 0.30      # per (1 - cos deflection); only bites on a hairpin
STRAIGHT_W = 0.55      # 🔑 the cost of HOLDING A BEARING - see below

class Router(object):
    def __init__(self, F, forbid=()):
        t = F['tiles']
        self.nb = F['nb']; self.tiles = t; self.comfort = F['comfort']
        self.allow = F['allow']; self.river = F['river_t']
        self.vec = {k: xyz(v) for k, v in t.items()}
        self.forbid = set(forbid)
        self.lee = {k: (1.0 if t[k]['hill'] <= 2 and any(t[n]['hill'] >= 3 for n in self.nb[k])
                        else 0.0) for k in t}

    def passable(self, x, ends):
        if x in ends: return True
        tt = self.tiles[x]
        return (not tt['water']) and self.allow.get(x, True) and x not in self.forbid

    def step_cost(self, a, b, prev, turn_w, comfort_w, straight_w=STRAIGHT_W):
        ta, tb = self.tiles[a], self.tiles[b]
        d = tb['elev'] - ta['elev']
        # ⚠️ SYMMETRIC. A road is bidirectional, so capping only the uphill sense lets a
        # 629 m step in by laying it downhill - measured 2026-08-26 on the first full pass.
        if abs(d) > CLIMB_CAP: return None
        c = 1.0 - comfort_w * min(1.0, self.comfort[b] / COMFORT_S)
        c += max(0.0, d) * CLIMB_W + max(0.0, -d) * DESC_W + abs(d) * ROUGH_W
        h = tb['hill']
        if h >= 4: c += HILL4_W
        elif h == 3: c += HILL3_W
        c -= LEE_W * self.lee[b]
        if b in self.river:
            c += RIDE_W if a in self.river else FORD_W
        if prev is not None:
            u = self._unit(prev, a); v = self._unit(a, b)
            cosang = max(-1.0, min(1.0, sum(x*y for x, y in zip(u, v))))
            c += turn_w * (1.0 - cosang)
            if cosang > 0.93: c += straight_w          # held the bearing
        return max(0.05, c)

    def _unit(self, a, b):
        va, vb = self.vec[a], self.vec[b]
        w = [vb[i] - va[i] for i in range(3)]
        n = math.sqrt(sum(x*x for x in w)) or 1.0
        return [x/n for x in w]

    def _ang(self, p, q):
        return math.degrees(math.acos(max(-1.0, min(1.0, sum(x*y for x, y in zip(p, q))))))

    def corridor(self, a, b, pad):
        va, vb = self.vec[a], self.vec[b]
        lim = self._ang(va, vb) + pad
        return {t for t, v in self.vec.items() if self._ang(v, va) + self._ang(v, vb) <= lim}

    def route(self, a, b, turn_w=TURN_W, comfort_w=COMFORT_W, pad=None, straight_w=STRAIGHT_W):
        if pad is None:
            pad = min(10.0, 2.5 + 0.45 * self._ang(self.vec[a], self.vec[b]))
        ends = {a, b}
        area = {x for x in self.corridor(a, b, pad) if self.passable(x, ends)}
        if a not in area or b not in area: return None
        dist = {(a, None): 0.0}; prevmap = {}
        pq = [(0.0, a, None)]
        while pq:
            d, x, p = heapq.heappop(pq)
            if d > dist.get((x, p), 1e18) + 1e-9: continue
            if x == b: break
            for n in self.nb[x]:
                if n not in area or n == p: continue
                c = self.step_cost(x, n, p, turn_w, comfort_w, straight_w)
                if c is None: continue
                nd = d + c
                if nd < dist.get((n, x), 1e18) - 1e-9:
                    dist[(n, x)] = nd; prevmap[(n, x)] = (x, p)
                    heapq.heappush(pq, (nd, n, x))
        best = min((k for k in dist if k[0] == b), key=lambda k: dist[k], default=None)
        if best is None: return None
        path = []; cur = best
        while cur is not None:
            path.append(cur[0]); cur = prevmap.get(cur)
        path.reverse()
        return path if path and path[0] == a else None
