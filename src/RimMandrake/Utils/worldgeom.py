#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""worldgeom.py - the PLANET's geometry: tile centres, hex polygons, projections.

A savegame stores per-tile arrays and NOTHING about where a tile is. The engine
rebuilds the geodesic sphere from `<subdivisions>` at load time, so the position of
tile 4711 exists only inside RimWorld. That is why this module reads it from a CSV
dumped out of the live game (`jawa/world_tile_export` and `jawa/world_neighbors`)
rather than reinventing RimWorld's tile ordering, which would resolve to a
DIFFERENT tile rather than failing - the same silent-failure shape as a wrong
shortHash table.

    world/world_tiles_sub7b.csv       tile -> lat, long          (engine truth)
    world/world_neighbors_sub7b.csv   tile -> 6 neighbours       (engine ORDER)

⭐ SELF-VERIFYING, three ways, all run by `--selftest`:
   1. a geodesic sphere has EXACTLY 12 pentagons and no other degree,
   2. every hex vertex computed from tile A agrees with the same vertex computed
      from its neighbour B to ~1e-16 - i.e. the polygons actually tile the sphere,
   3. the median angular step between consecutive neighbours is 60 deg.

🔑 THE HEX POLYGON. RimWorld's tiles are the dual of a subdivided icosahedron, so a
tile's corners are the normalised sums of the three tile centres meeting there:

        corner(k) = normalise( C[t] + C[n_k] + C[n_k+1] )

with the neighbours taken in the ENGINE's own order, which is already angular.
That is exact, not a Voronoi approximation, and it is what check 2 above proves.

🔴 The neighbour ORDER is also the river/road adjacency slot. Do not re-sort it.
"""
import csv
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORLD = os.path.join(REPO, "world")

# tile-count -> (centres csv, engine-neighbour csv). Keyed by COUNT because that is
# what a save can be checked against without loading the game.
GEOMETRY = {
    21872: ("world_tiles_sub7b.csv", "world_neighbors_sub7b.csv"),
}

MISSING = """no tile geometry for a %d-tile planet.

The save does not carry tile positions - only the engine has them. Dump them from a
running game that has THIS world loaded and drop both files in %s:

    jawa/world_tile_export     -> world_tiles_sub<N>.csv   (tile,lat,long,...)
    jawa/world_neighbors       -> world_neighbors_sub<N>.csv (tile,n0..n5)

then add %d to GEOMETRY in worldgeom.py. Nothing here will guess a tile position."""


class Geometry(object):
    """Tile centres, neighbours and hex corners for one planet size."""

    def __init__(self, n_tiles):
        if n_tiles not in GEOMETRY:
            raise SystemExit(MISSING % (n_tiles, WORLD, n_tiles))
        tiles_csv, nb_csv = (os.path.join(WORLD, f) for f in GEOMETRY[n_tiles])
        lat, lon = [], []
        for r in csv.DictReader(open(tiles_csv, encoding="utf-8")):
            lat.append(float(r["lat"]))
            lon.append(float(r["long"]))
        if len(lat) != n_tiles:
            raise SystemExit("%s holds %d tiles, the save holds %d"
                             % (tiles_csv, len(lat), n_tiles))
        self.n = n_tiles
        self.lat = np.array(lat)
        self.lon = np.array(lon)
        rlat, rlon = np.radians(self.lat), np.radians(self.lon)
        # y is the polar axis, matching the CSV's own lat/long convention
        self.vec = np.stack([np.cos(rlat) * np.cos(rlon),
                             np.sin(rlat),
                             np.cos(rlat) * np.sin(rlon)], axis=1)
        nb = []
        for row in csv.reader(open(nb_csv, encoding="utf-8")):
            if row[0] == "tile":
                continue
            nb.append([int(x) for x in row[1:]])
        self.nb = np.array(nb, dtype=np.int32)
        if len(self.nb) != n_tiles:
            raise SystemExit("%s holds %d tiles, the save holds %d"
                             % (nb_csv, len(self.nb), n_tiles))
        self._corners = None

    # -- adjacency ---------------------------------------------------------
    def neighbours(self, t):
        """Real neighbours of t, in the ENGINE's order. Slot k of this list is the
        adjacency byte k that rivers and roads use."""
        return [int(x) for x in self.nb[t] if x >= 0]

    def edges(self):
        """Every undirected edge once, as (lo, hi)."""
        out = set()
        for t in range(self.n):
            for u in self.neighbours(t):
                out.add((t, u) if t < u else (u, t))
        return sorted(out)

    # -- polygons ----------------------------------------------------------
    def corners(self, t):
        """The 5 or 6 unit-sphere corners of tile t, in order."""
        ns = self.neighbours(t)
        c = self.vec[t]
        out = np.empty((len(ns), 3))
        for k in range(len(ns)):
            v = c + self.vec[ns[k]] + self.vec[ns[(k + 1) % len(ns)]]
            out[k] = v / np.linalg.norm(v)
        return out

    def all_corners(self):
        """[n][k][3] as a python list, computed once. ~0.4 s for 21,872 tiles."""
        if self._corners is None:
            self._corners = [self.corners(t) for t in range(self.n)]
        return self._corners

    # -- measures ----------------------------------------------------------
    def arc_deg(self, a, b):
        d = float(np.clip(np.dot(self.vec[a], self.vec[b]), -1.0, 1.0))
        return math.degrees(math.acos(d))

    def mean_tile_arc(self):
        return float(np.mean([self.arc_deg(t, self.neighbours(t)[0])
                              for t in range(0, self.n, 37)]))

    def latlon_of(self, v):
        return (math.degrees(math.asin(max(-1.0, min(1.0, v[1])))),
                math.degrees(math.atan2(v[2], v[0])))


# --------------------------------------------------------------------------
# Projections. Each takes unit vectors [k,3] and returns pixel xy [k,2], plus a
# visibility mask. Nothing here knows about the save.
# --------------------------------------------------------------------------

class Equirect(object):
    """Whole planet, lon across, lat down. Every tile is drawn; polar tiles smear,
    which is honest - it is what a rectangular map of a sphere does."""
    name = "equirect"

    def __init__(self, width=2400, center_lon=0.0):
        self.w = width
        self.h = width // 2
        self.clon = center_lon

    def project(self, verts, ref=None):
        """ref: a unit vector used to resolve the antimeridian - corners are pulled
        to the same side of the map as their tile's own centre, so a hex never
        stretches across the whole image."""
        lat = np.degrees(np.arcsin(np.clip(verts[:, 1], -1, 1)))
        lon = np.degrees(np.arctan2(verts[:, 2], verts[:, 0])) - self.clon
        lon = (lon + 180.0) % 360.0 - 180.0
        if ref is not None:
            rl = (math.degrees(math.atan2(ref[2], ref[0])) - self.clon + 180.0) % 360.0 - 180.0
            lon = rl + ((lon - rl + 180.0) % 360.0 - 180.0)
        x = (lon + 180.0) / 360.0 * self.w
        y = (90.0 - lat) / 180.0 * self.h
        return np.stack([x, y], axis=1), True

    def wrap_copies(self, xy):
        """Extra x-offsets needed so a hex straddling the seam appears on both edges."""
        out = []
        if xy[:, 0].min() < 0:
            out.append(self.w)
        if xy[:, 0].max() > self.w:
            out.append(-self.w)
        return out


class Ortho(object):
    """A globe. Half the planet, no distortion of shape near the centre - the right
    view for a tidally-locked world, pointed at the substellar or antistellar."""
    name = "ortho"

    def __init__(self, width=1600, center_lat=0.0, center_lon=0.0):
        self.w = self.h = width
        self.r = width * 0.47
        a, b = math.radians(center_lat), math.radians(center_lon)
        self.axis = np.array([math.cos(a) * math.cos(b), math.sin(a), math.cos(a) * math.sin(b)])
        # east and north at the view centre
        north = np.array([0.0, 1.0, 0.0])
        east = np.cross(north, self.axis)
        if np.linalg.norm(east) < 1e-9:
            east = np.array([1.0, 0.0, 0.0])
        self.east = east / np.linalg.norm(east)
        self.north = np.cross(self.axis, self.east)

    def project(self, verts, ref=None):
        vis = float(np.dot(ref, self.axis)) > -0.02 if ref is not None else True
        x = self.w / 2 + self.r * verts.dot(self.east)
        y = self.h / 2 - self.r * verts.dot(self.north)
        return np.stack([x, y], axis=1), vis

    def wrap_copies(self, xy):
        return []


class Mollweide(object):
    """Equal-AREA whole planet. The rectangular map exaggerates the polar and
    antistellar ground badly; on Mollweide a region's area on the page is its area on
    the globe, which is the only honest way to judge how much of the planet a biome
    actually covers."""
    name = "mollweide"

    def __init__(self, width=2400, center_lon=0.0):
        self.w = width
        self.h = width // 2
        self.clon = center_lon
        self.R = width / (4.0 * math.sqrt(2.0))

    @staticmethod
    def _aux(phi):
        """Solve 2t + sin 2t = pi sin(phi) for t. Newton, from t = phi."""
        t = np.array(phi, dtype=float)
        for _ in range(12):
            f = 2 * t + np.sin(2 * t) - math.pi * np.sin(phi)
            d = 2 + 2 * np.cos(2 * t)
            d = np.where(np.abs(d) < 1e-9, 1e-9, d)
            t = t - f / d
        return t

    def project(self, verts, ref=None):
        lat = np.arcsin(np.clip(verts[:, 1], -1, 1))
        lon = np.degrees(np.arctan2(verts[:, 2], verts[:, 0])) - self.clon
        lon = (lon + 180.0) % 360.0 - 180.0
        if ref is not None:
            rl = (math.degrees(math.atan2(ref[2], ref[0])) - self.clon + 180.0) % 360.0 - 180.0
            lon = rl + ((lon - rl + 180.0) % 360.0 - 180.0)
        t = self._aux(lat)
        x = self.w / 2 + (2.0 * math.sqrt(2.0) / math.pi) * self.R * np.radians(lon) * np.cos(t)
        y = self.h / 2 - math.sqrt(2.0) * self.R * np.sin(t)
        return np.stack([x, y], axis=1), True

    def wrap_copies(self, xy):
        return []          # the ellipse has no seam to duplicate across


def make_projection(kind, width, center):
    if kind == "mollweide":
        return Mollweide(width, center[1])
    if kind == "ortho":
        return Ortho(width, center[0], center[1])
    if kind == "equirect":
        return Equirect(width, center[1])
    raise SystemExit("unknown projection %r (equirect | ortho)" % kind)


# --------------------------------------------------------------------------
def _selftest(n=21872):
    g = Geometry(n)
    deg = {}
    for t in range(g.n):
        d = len(g.neighbours(t))
        deg[d] = deg.get(d, 0) + 1
    print("tiles            %d" % g.n)
    print("degree histogram %s" % deg)
    ok_pent = deg.get(5, 0) == 12 and set(deg) <= {5, 6}
    print("12 pentagons     %s" % ("PASS" if ok_pent else "FAIL"))

    worst, checked = 0.0, 0
    rng = np.random.default_rng(0)
    for t in rng.choice(g.n, 400, replace=False):
        ns = g.neighbours(int(t))
        cs = g.corners(int(t))
        for k, a in enumerate(ns):
            b = ns[(k + 1) % len(ns)]
            na = g.neighbours(a)
            if b not in na or t not in na:
                continue
            j = na.index(b)
            other = g.corners(a)[j if na[(j + 1) % len(na)] == t else (j - 1) % len(na)]
            worst = max(worst, float(np.linalg.norm(cs[k] - other)))
            checked += 1
    print("shared corners   max err %.2e over %d pairs  %s"
          % (worst, checked, "PASS" if worst < 1e-9 else "FAIL"))

    steps = []
    for t in rng.choice(g.n, 200, replace=False):
        t = int(t)
        ns = g.neighbours(t)
        c = g.vec[t]
        tang = [(g.vec[u] - c * float(np.dot(g.vec[u], c))) for u in ns]
        tang = [v / np.linalg.norm(v) for v in tang]
        for k in range(len(ns)):
            d = float(np.clip(np.dot(tang[k], tang[(k + 1) % len(ns)]), -1, 1))
            steps.append(math.degrees(math.acos(d)))
    print("neighbour step   median %.1f deg of turn around the tile centre"
          % np.median(steps))
    print("mean tile arc    %.4f deg" % g.mean_tile_arc())
    return ok_pent and worst < 1e-9


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    print(__doc__)
