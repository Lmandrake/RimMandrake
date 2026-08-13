"""Object placement — the bottleneck that appeared once terrain stopped being one.

WHY THIS MODULE EXISTS
======================
Terrain used to dominate a formation: 411 cells cost 5.15 s because it was 103
separate calls. `jawa/set_terrain_batch` made that ONE call at 14 ms, and the
cost immediately moved somewhere else. Measured 2026-08-12, a radius-12 crater:

    ground (977 cells)  ............ 1 call    ~20 ms
    scattered objects (100 things) . 100 calls ~1.7 s      <-- now 98% of it

Same lesson as terrain, one layer up: **cost tracks call count.** So objects get
the same treatment — queue them, encode once, send in as few hops as the
companion's guards allow.

    p = Placer(s)
    for x, z in ash_cells:    p.add("Filth_Ash", x, z)
    for x, z in slag_cells:   p.add("ChunkSlagSteel", x, z)
    p.flush()                 # one call

FILTH IS NOT A THING YOU SPAWN
==============================
`Filth_Ash` and friends go through `FilthMaker`, which asks the terrain whether
it accepts filth at all — water does not. Spawning filth through the ordinary
path produces filth the game never agreed to and cannot clean up properly. The
companion routes by `def.IsFilth` so callers do not have to know, but the
consequence is visible: **filth ops can legitimately fail**, and a crater over a
pond will report fewer spawns than it asked for. That is correct behaviour, not
an error to suppress.

DESTRUCTION FINALLY WORKS
=========================
`jawa/destroy_batch` is the first working direct destruction primitive. Until it
existed the only way to clear ground was to lay a floor over it — which cleared
the vegetation and left a floor. `clear()` removes plants (or items, or filth)
and leaves the ground exactly as it was.

**It never destroys pawns**, whatever categories you pass. A rect typo should not
be able to kill a colonist.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from terrain import MAX_CELLS, MAX_OPS, to_rects

SPAWN_TOOL = "jawa/spawn_batch"
DESTROY_TOOL = "jawa/destroy_batch"
FALLBACK_SPAWN = "rimworld/spawn_thing"


def to_spawn_ops(items):
    """[(defName, x, z, count)] -> 'Def:x,z,count' joined by ';'.

    Count is emitted even when it is 1. The grammar allows omitting it, but a
    fixed arity makes the payload trivially diffable when a spawn goes wrong,
    and the few extra bytes never mattered.
    """
    return ";".join("%s:%d,%d,%d" % (d, x, z, c) for (d, x, z, c) in items)


def chunk_items(items, max_ops=MAX_OPS):
    """Split queued spawns into payloads the companion will accept."""
    for i in range(0, len(items), max_ops):
        yield items[i:i + max_ops]


class Placer(object):
    """Queue objects, then place them in as few calls as possible.

    Nothing is sent until `flush()`. That is deliberate: a generator naturally
    emits objects zone by zone, and batching only pays if the whole formation is
    encoded together rather than once per zone.
    """

    def __init__(self, session, strict=False):
        self.s = session
        self.strict = strict
        self.queue = []
        self.calls = 0
        self.spawned = 0
        self.failed = 0
        self.errors = []
        self.per_def = {}
        self._route = None
        self._can_destroy = None

    # ------------------------------------------------------------- capability
    def _tools(self):
        try:
            return {t.get("name") for t in self.s._rb.list_tools()}
        except Exception:
            return set()

    def route(self):
        """'batch' if the companion can spawn in bulk, else 'single'.

        Cached: companions are discovered only at RimBridgeServer startup, so a
        tool absent now stays absent until the game restarts.
        """
        if self._route is None:
            self._route = "batch" if SPAWN_TOOL in self._tools() else "single"
        return self._route

    def can_destroy(self):
        if self._can_destroy is None:
            self._can_destroy = DESTROY_TOOL in self._tools()
        return self._can_destroy

    # ------------------------------------------------------------------ queue
    def add(self, defName, x, z, count=1):
        self.queue.append((defName, int(x), int(z), int(count)))
        return self

    def extend(self, defName, cells, count=1):
        """Queue one def across many cells. Accepts (x, z) or (x, z, extra)."""
        for c in cells:
            self.add(defName, c[0], c[1], count)
        return self

    # ------------------------------------------------------------------ flush
    def flush(self, stuff=None):
        """Place everything queued. Returns the number actually spawned."""
        if not self.queue:
            return 0
        items, self.queue = self.queue, []
        if self.route() == "batch":
            n = self._flush_batch(items, stuff)
        else:
            n = self._flush_single(items)
        self.spawned += n
        return n

    def _flush_batch(self, items, stuff=None):
        n = 0
        for chunk in chunk_items(items):
            args = {"ops": to_spawn_ops(chunk)}
            if stuff:
                args["stuff"] = stuff
            r = self.s.call(SPAWN_TOOL, **args)
            self.calls += 1
            n += r.get("spawned", 0) or 0
            self.failed += r.get("failed", 0) or 0
            for e in (r.get("errors") or []):
                self.errors.append(e)
            for d, c in (r.get("perDef") or {}).items():
                self.per_def[d] = self.per_def.get(d, 0) + c
        return n

    def _flush_single(self, items):
        """One call per object. The old path — kept so a generator still runs
        against a companion that predates the batch tool, just slowly."""
        n = 0
        for (d, x, z, c) in items:
            try:
                p = {"defName": d, "x": x, "z": z}
                if c > 1:
                    p["stackCount"] = c
                if self.s.call(FALLBACK_SPAWN, **p).get("success"):
                    n += 1
                    self.per_def[d] = self.per_def.get(d, 0) + 1
                else:
                    self.failed += 1
                self.calls += 1
            except Exception as e:
                self.failed += 1
                self.errors.append({"def": d, "x": x, "z": z, "error": str(e)[:100]})
        return n

    # ---------------------------------------------------------------- destroy
    def clear(self, cells, categories="Plant"):
        """Destroy things in these cells. Returns the number destroyed.

        The first working direct destruction primitive — `Clear area (rect)` is
        a drag tool and silently does nothing over the bridge. Cells are
        decomposed to rects first, so clearing a blob costs a handful of ops
        rather than one per cell.

        Never destroys pawns, whatever `categories` says.
        """
        if not self.can_destroy():
            if self.strict:
                raise NotImplementedError(
                    "%s is not registered. Deploy the companion and RESTART the "
                    "game; until then the only way to clear ground is to lay a "
                    "floor over it." % DESTROY_TOOL)
            return 0
        rects = to_rects(set(tuple(c[:2]) for c in cells))
        n = 0
        batch, count = [], 0
        for r in rects + [None]:
            if r is None or len(batch) + 1 > MAX_OPS or count + r[2] * r[3] > MAX_CELLS:
                if batch:
                    res = self.s.call(DESTROY_TOOL,
                                      rects=";".join("%d,%d,%d,%d" % q for q in batch),
                                      categories=categories)
                    self.calls += 1
                    n += res.get("destroyed", 0) or 0
                batch, count = [], 0
            if r is not None:
                batch.append(r)
                count += r[2] * r[3]
        return n

    # ----------------------------------------------------------------- report
    def report(self):
        bits = ["route=%s" % self.route(), "%d calls" % self.calls,
                "%d spawned" % self.spawned]
        if self.failed:
            bits.append("%d FAILED" % self.failed)
        if self.errors:
            bits.append("errors: %s" % (self.errors[:2],))
        if self.queue:
            bits.append("%d still queued (flush() not called)" % len(self.queue))
        return "place: " + ", ".join(bits)
