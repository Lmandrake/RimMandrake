#!/usr/bin/env python3
"""The station allocator of a stage map (RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS).

Pure: no game, no bridge. A stage is one map of a test game that holds stations and cast and nothing else
(design/specs/2026-11-23-bridge-v2/05_build_design.md §Decision 7: the station fence). This module says WHERE on that map a
scene may stage: it gives each request a rectangle that keeps its margin from every other station given on the map and
its distance from the map edge, it never gives a retired station again, and it refuses by name a request that the map
kind cannot serve. Promises and tests: design/specs/2026-11-23-bridge-v2/boundary.md §THE STATION ALLOCATOR.

The three map kinds (`needs.map` of the design):
  settlement  the default: an ordinary player settlement map, with edges, a home status and incident targets.
  pocket      no map edge, no home status, no incident, no sun or weather of a tile: a request that needs one is refused.
  colony      a real colony (the walks): a station there is marked "shared map" (bystanders are held per pawn only).
"""
import json

KINDS = ("settlement", "pocket", "colony")
POCKET_CANNOT = ("incident", "edge", "home", "weather")   # what a pocket map does not have (05_build_design.md §Decision 7)
REQUEST_KEYS = {"size", "margin", "edge", "incident", "home", "weather", "scene"}
EDGE_BAND = 1   # RimWorld keeps the outermost ring of cells for edge arrivals and refuses most builds there
SCHEMA = "stage_stations_v1"


class Refused(Exception):
    """A request that this stage cannot serve. `name` is the refusal, `why` says what would serve it."""

    def __init__(self, name, why):
        super().__init__("%s: %s" % (name, why))
        self.name, self.why = name, why


def _overlap(a, b):
    """Two rectangles (x, z, w, h) share a cell."""
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def _grow(r, m):
    return (r[0] - m, r[1] - m, r[2] + 2 * m, r[3] + 2 * m)


class Stage:
    """The stations of one stage map. `size` is the map's (x, z) as read from the game."""

    def __init__(self, name, kind, size, stations=None):
        if kind not in KINDS:
            raise Refused("UNKNOWN_MAP_KIND", "the map kinds are %s, not %r" % (", ".join(KINDS), kind))
        if not (isinstance(size, (tuple, list)) and len(size) == 2 and all(isinstance(n, int) and n > 2 * EDGE_BAND for n in size)):
            raise Refused("BAD_ARGS", "size is the map's (x, z) in cells, read from the game, not %r" % (size,))
        self.name, self.kind, self.size = name, kind, tuple(size)
        self.stations = [dict(s) for s in (stations or [])]

    # ---- requests
    def _check(self, req):
        odd = sorted(set(req) - REQUEST_KEYS)
        if odd:
            raise Refused("BAD_ARGS", "a station request takes %s, not %s" % (", ".join(sorted(REQUEST_KEYS)), ", ".join(odd)))
        size = req.get("size")
        if not (isinstance(size, (tuple, list)) and len(size) == 2 and all(isinstance(n, int) and n > 0 for n in size)):
            raise Refused("BAD_ARGS", "size is the station's (w, h) in cells, not %r" % (size,))
        for k in ("margin", "edge"):
            v = req.get(k, 0)
            if not isinstance(v, int) or v < 0:
                raise Refused("BAD_ARGS", "%s is a count of cells, 0 or more, not %r" % (k, v))
        if self.kind == "pocket":
            wants = [k for k in POCKET_CANNOT if req.get(k)]
            if wants:
                raise Refused("POCKET_CANNOT_SERVE", "a pocket map has no %s; this scene asks for it: stage it on a settlement map" % (
                    " and no ".join(wants)))

    def give(self, **req):
        """-> the station: a dict with `id`, `rect` (x, z, w, h in map cells), `kind`, `shared_map`. Refused names why not."""
        self._check(req)
        w, h = req["size"]
        margin, edge = req.get("margin", 0), req.get("edge", 0)
        band = EDGE_BAND + edge
        mx, mz = self.size
        if w > mx - 2 * band or h > mz - 2 * band:
            raise Refused("NO_ROOM", "a %dx%d station with %d cells from the edge needs a map of at least %dx%d; this map is %dx%d" % (
                w, h, edge, w + 2 * band, h + 2 * band, mx, mz))
        taken = [s for s in self.stations if s["state"] in ("given", "retired")]
        for z in range(band, mz - band - h + 1):
            for x in range(band, mx - band - w + 1):
                r = (x, z, w, h)
                if any(_overlap(_grow(r, margin), _grow(tuple(s["rect"]), s["margin"])) for s in taken):
                    continue
                free = [s for s in self.stations if s["state"] == "free" and tuple(s["rect"]) == r and s["margin"] == margin]
                if free:
                    st = free[0]
                else:
                    st = {"id": "st%d" % (len(self.stations) + 1), "rect": list(r), "margin": margin, "state": "free", "why": None}
                    self.stations.append(st)
                st.update(state="given", scene=req.get("scene"), why=None)
                return self._view(st)
        given = sum(1 for s in self.stations if s["state"] == "given")
        retired = sum(1 for s in self.stations if s["state"] == "retired")
        raise Refused("NO_ROOM", "no %dx%d station with margin %d fits %d cells from the edge of this %dx%d map: %d given, %d retired; "
                      "release a station, or make the stage again" % (w, h, margin, edge, mx, mz, given, retired))

    def _view(self, st):
        return {"id": st["id"], "rect": tuple(st["rect"]), "margin": st["margin"], "kind": self.kind, "stage": self.name,
                "shared_map": self.kind == "colony"}

    def _get(self, sid):
        for s in self.stations:
            if s["id"] == sid:
                return s
        raise Refused("UNKNOWN_STATION", "no station %r on the stage %s" % (sid, self.name))

    def release(self, sid):
        """The station was cleaned: it may be given again."""
        s = self._get(sid)
        if s["state"] == "retired":
            raise Refused("RETIRED", "%s was retired (%s); it is never given again" % (sid, s["why"]))
        s.update(state="free", scene=None)

    def retire(self, sid, why):
        """The station could not be cleaned: it is never given again, and its cells and margin stay taken."""
        if not why:
            raise Refused("BAD_ARGS", "a retirement names why the station could not be cleaned")
        self._get(sid).update(state="retired", why=why)

    # ---- the state on disk (one file per stage; the caller owns the path)
    def to_json(self):
        return json.dumps({"schema": SCHEMA, "name": self.name, "kind": self.kind, "size": list(self.size), "stations": self.stations},
                          sort_keys=True, indent=1)

    @classmethod
    def from_json(cls, text):
        d = json.loads(text)
        if d.get("schema") != SCHEMA:
            raise Refused("BAD_STATE", "the stage file is schema %r, not %s" % (d.get("schema"), SCHEMA))
        return cls(d["name"], d["kind"], tuple(d["size"]), d.get("stations"))
