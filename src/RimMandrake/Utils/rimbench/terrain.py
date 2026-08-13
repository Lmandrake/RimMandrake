"""Terrain painting — the capability that used to be missing, now the fast path.

STATE OF PLAY, verified 2026-08-12
==================================
  ✅ NATURAL terrain (soil, gravel, sand, water, rock) CAN be painted, via the
     `JawaBench.BridgeTools` companion. `jawa/set_terrain` takes a rect and
     reads every cell back off the grid before answering, so its
     `cellsFailedVerify` is authoritative rather than hopeful. Proven
     reversible: exact capture and restore, failedVerify=0.
  ✅ `jawa/set_terrain_batch` paints MANY rects in one call. Staged 2026-08-12
     and inert until RimWorld next restarts — companions are discovered only at
     RimBridgeServer startup.
  ✅ Player FLOORS still work through the architect designator, and laying one
     still DESTROYS the vegetation underneath. That remains the only working
     destruction primitive.
  ❌ RimWorld's own `Set terrain (rect)` debug action is still a silent no-op
     over the bridge. It is drag-based and the bridge cannot drag. Nothing here
     calls it any more; it is recorded only so nobody re-discovers it.

WHY CALL COUNT IS THE ONLY NUMBER THAT MATTERS
==============================================
Cost tracks CALLS, not cells. Measured on the live 568-mod stack:

    one 6x6 rect, 36 cells, one call ............  15.2 ms   (0.42 ms/cell)
    one 411-cell dithered crater, 103 calls ..... 5150.0 ms  (12.59 ms/cell)

Same map, minutes apart. The crater is 30x worse per cell purely because a
dithered boundary interlocks on purpose — that is what stops it reading as a
bullseye — and greedy rect decomposition yields only ~4 cells per rect. So the
generator's job is not to touch fewer cells. It is to make fewer calls.

Hence the shape of this module: everything funnels into `paint_map`, which
decomposes to rects ONCE, packs them into as few `jawa/set_terrain_batch`
payloads as the companion's guards allow, and sends those. A whole formation
should be one hop.

THE GUARDS ARE NOT ADVISORY
===========================
`MAX_OPS` and `MAX_CELLS` mirror the constants compiled into the companion
(JawaBenchTerrainTools.cs). Exceed either and the call is REJECTED outright, so
we chunk on this side rather than discovering it a round trip later. The guards
exist because the whole batch runs inside one `MainThread.InvokeAsync`: an
oversized payload does not merely take a while, it stalls the simulation and the
renderer for the duration, which is indistinguishable from a freeze. This
project has already lost a colony to a main-thread livelock.

REVERSIBILITY IS BUILT IN — BUT IT IS TERRAIN-ONLY
==================================================
`capture()` before painting and `restore()` after. The whole "live bridge beats
save-editing" argument in `design/RimMandrake/map_authoring_decision.md` rests on being able
to undo, so an authoring tool that cannot undo itself has given that away.

⚠️ **`restore()` puts the TERRAIN back. It does not undo the paint.** Measured
live 2026-08-12: painting destroys the plants on a cell whenever the new terrain
cannot support them, and repainting the original TerrainDef does not bring them
back. A restore verified 2,601 cells with 0 wrong and left the ground bare.

So: "terrain is exactly restorable" is true; "the paint is reversible" is not.
On a colony that matters, **the save is the undo.**

WHICH TERRAINS CLEAR VEGETATION — verified live, 2026-08-12
===========================================================
Grass, dandelions and chokevine, over Soil/SoilRich/Gravel:

    Sand, PackedDirt, WaterShallow, <stone>_Rough  ->  plants DESTROYED
    Gravel                                         ->  plants SURVIVE
    the cell's own existing terrain                ->  no-op, nothing dies

The rule is `CanEverPlantAt`: the plant dies iff it cannot grow on the new
terrain. Gravel supports grass, so a "gravel crater bowl" fills with healthy
grass and looks absurd. **Choose terrain for what it does to the vegetation as
well as for its colour** — see `formations.CRATER_GROUND`, which was wrong until
this was measured.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from build import D

BS = chr(92)

# Mirrors JawaBenchTerrainTools.cs. Keep in step with the C# or the first thing
# you learn about a mismatch is a rejected 5-second payload.
MAX_OPS = 4096
MAX_CELLS = 70000            # a 250x250 map is 62,500 cells

BATCH_TOOL = "jawa/set_terrain_batch"
SINGLE_TOOL = "jawa/set_terrain"
READ_TOOL = "jawa/get_terrain_batch"

# Floors reachable through the architect menu. Keys are intent, not defs, so a
# generator says what it MEANS and this table decides how to achieve it.
FLOOR_PALETTE = {
    "wood":      "woodplankfloor",
    "concrete":  "concrete",
    "paved":     "pavedtile",
    "metal":     "metaltile",
    "sterile":   "steriletile",
    "straw":     "strawmatting",
    "stone":     "flagstonegranite",
    "tile":      "tilegranite",
}

# Natural terrain defNames. Vanilla only, so the same generator runs on the
# 3-mod bench and the 568-mod campaign. The companion resolves case-insensitively
# and suggests near-misses, but spelling them right here saves a round trip.
#
# EVERY NAME BELOW WAS READ OUT OF THE SHIPPED DEFS, 2026-08-12:
#   grep -rh '<defName>' "C:\Program Files (x86)\Steam\steamapps\common\
#       RimWorld\Data\*\Defs\TerrainDefs\"
# Do not add an entry you have not seen in that output. A wrong defName does not
# fail loudly — `jawa/set_terrain` returns success:false with suggestions, but a
# generator that ignores the reply paints nothing and looks like a renderer bug.
# `BurnedGrass` was in this table and in the companion's own help text until it
# was checked: it does not exist in vanilla at all. The burned terrains are all
# FLOORS (BurnedCarpet, BurnedWoodPlankFloor, BurnedStrawMatting).
NATURAL = {
    "soil": "Soil", "rich_soil": "SoilRich", "grassland": "GrasslandSoil",
    "gravel": "Gravel", "fungal_gravel": "FungalGravel",
    "sand": "Sand", "soft_sand": "SoftSand",
    "mud": "Mud", "marsh": "Marsh", "marshy": "MarshyTerrain",
    "packed": "PackedDirt", "dry_lake": "DryLakeBed",
    "ice": "Ice", "thin_ice": "ThinIce", "moss": "MossyTerrain",
    "lava_cooled": "CooledLava", "volcanic": "VolcanicRock",
    "broken_asphalt": "BrokenAsphalt", "riverbank": "Riverbank",
    "water_shallow": "WaterShallow", "water_deep": "WaterDeep",
    "water_moving": "WaterMovingShallow",
    # Stone terrain is GENERATED at runtime, one set per natural-rock ThingDef,
    # so these appear in no XML file and grepping the Data folder will not find
    # them. They are real: `Slate_Rough` was read back off a live 568-mod map
    # (observed/2026-08-13_pre-restructure/latency_568mod.json). Substitute the map's own stone type —
    # Sandstone here is a desert-world guess, not a universal default.
    "rock_rough": "Sandstone_Rough", "rock_hewn": "Sandstone_RoughHewn",
    "rock_smooth": "Sandstone_Smooth",
}


def resolve(name):
    """Intent name -> TerrainDef defName. Passes unknown names through, so a
    generator can name a modded terrain directly."""
    return NATURAL.get(name, name)


# --------------------------------------------------------------- decomposition

def to_rects(cells):
    """Greedy maximal-rectangle decomposition of a cell set.

    Grow width first, then height while the full-width row still fits. Not
    optimal — optimal rect cover is NP-hard and the win here is already large —
    but it is deterministic and it is an EXACT COVER: every input cell appears
    in exactly one output rect, and no rect covers a cell that was not asked
    for. `selftest.py` asserts both properties, because a decomposer that
    quietly drops cells paints a hole the caller cannot see.
    """
    remaining = set(cells)
    rects = []
    while remaining:
        x0, z0 = min(remaining, key=lambda c: (c[1], c[0]))
        w = 0
        while (x0 + w, z0) in remaining:
            w += 1
        h = 0
        while all((x0 + i, z0 + h) in remaining for i in range(w)):
            h += 1
        for i in range(w):
            for j in range(h):
                remaining.discard((x0 + i, z0 + j))
        rects.append((x0, z0, w, h))
    return rects


def plan_rects(cellmap):
    """{(x, z): terrainDef} -> [(terrain, x, z, w, h)], grouped by terrain.

    Decomposition happens per terrain because a rect carries exactly one
    TerrainDef. Sorting by terrain name keeps the output deterministic, which
    is what makes a re-run idempotent rather than additive.
    """
    by_terrain = {}
    for cell, terr in cellmap.items():
        by_terrain.setdefault(terr, set()).add(cell)
    rects = []
    for terr, cs in sorted(by_terrain.items()):
        for (x, z, w, h) in to_rects(cs):
            rects.append((terr, x, z, w, h))
    return rects


def chunk_rects(rects, max_ops=MAX_OPS, max_cells=MAX_CELLS):
    """Split rects into payloads the companion will accept.

    Yields lists of rects, each within BOTH guards. A single rect larger than
    `max_cells` cannot be split by this function and is yielded alone — the
    companion will reject it, which is the correct and loud outcome; splitting
    it silently would hide a generator asking for something absurd.
    """
    batch, cells = [], 0
    for r in rects:
        n = r[3] * r[4]
        if batch and (len(batch) + 1 > max_ops or cells + n > max_cells):
            yield batch
            batch, cells = [], 0
        batch.append(r)
        cells += n
    if batch:
        yield batch


def to_ops(rects):
    """Encode rects as the companion's ops string: 'Terrain:x,z,w,h' joined by ';'.

    A compact string rather than JSON on purpose — no JSON library is guaranteed
    in the game's assembly set, and this is a generator's hot path. About 18
    characters per rect, so 100 rects is under 2 KB.
    """
    return ";".join("%s:%d,%d,%d,%d" % (t, x, z, w, h) for (t, x, z, w, h) in rects)


def to_read_ops(cells):
    """Encode a cell set as coordinate-only rects for `jawa/get_terrain_batch`.

    Decomposed first, so reading a 977-cell crater asks for ~100 rects rather
    than 977 points. The companion ignores a leading 'Name:' anyway, but leaving
    it off makes the request obviously a read.
    """
    return ";".join("%d,%d,%d,%d" % r for r in to_rects(cells))


def parse_ops(ops, default_terrain=None):
    """Decode an ops string back to [(terrain, x, z, w, h)].

    The companion's capture tool answers in exactly the grammar its paint tool
    accepts, so a captured region round-trips without translation. This is the
    production decoder; `selftest.py` keeps a SEPARATE port of the C# parser and
    checks the two agree, because an encoder and decoder written together will
    happily agree on the same mistake.
    """
    rects = []
    for token in ops.replace("\r", "\n").replace("\n", ";").split(";"):
        token = token.strip()
        if not token:
            continue
        terrain, coord = default_terrain, token
        if ":" in token:
            head, coord = token.split(":", 1)
            terrain = head.strip()
        nums = [int(p.strip()) for p in coord.split(",") if p.strip()]
        if not 2 <= len(nums) <= 4 or not terrain:
            raise ValueError("bad op %r" % token)
        x, z = nums[0], nums[1]
        w = nums[2] if len(nums) > 2 else 1
        h = nums[3] if len(nums) > 3 else 1
        rects.append((terrain, x, z, w, h))
    return rects


def expand_ops(ops):
    """Ops string -> {(x, z): terrainDefName}."""
    out = {}
    for (t, x, z, w, h) in parse_ops(ops):
        for dx in range(w):
            for dz in range(h):
                out[(x + dx, z + dz)] = t
    return out


# ------------------------------------------------------------------- the painter

class TerrainPainter(object):
    """Paint terrain, by the fastest route the running game actually offers.

    Route is probed once per session and cached:

        batch   jawa/set_terrain_batch is registered  -> whole formation per call
        single  only jawa/set_terrain is registered   -> one call per rect
        none    no companion at all                   -> nothing is painted

    `strict=False` (default) means an unavailable route is COUNTED and reported
    rather than raised, so a generator can run end to end and tell you exactly
    how much of it the current game could not do. `strict=True` raises instead —
    use that in tests, where a silent no-op is the bug you are hunting.
    """

    def __init__(self, session, strict=False, layer="top"):
        self.s = session
        self.strict = strict
        self.layer = layer
        self.unavailable = {}       # terrain -> cells attempted but not painted
        self.calls = 0
        self.cells_changed = 0
        self.cells_failed = 0
        self.errors = []
        self._route = None
        self._read_batch = None
        self._originals = {}        # (x, z) -> terrainDefName, for restore()

    # ------------------------------------------------------------- capability
    def route(self):
        """Which painting route this game supports. Probed once, then cached.

        Cached deliberately: `list_tools` is cheap but the answer cannot change
        mid-session — companions are discovered only at RimBridgeServer startup,
        so a tool that is absent now stays absent until the game restarts.
        """
        if self._route is None:
            try:
                names = {t.get("name") for t in self.s._rb.list_tools()}
            except Exception:
                names = set()
            if BATCH_TOOL in names:
                self._route = "batch"
            elif SINGLE_TOOL in names:
                self._route = "single"
            else:
                self._route = "none"
        return self._route

    def explain_route(self):
        return {
            "batch": "%s registered — whole formations in one call" % BATCH_TOOL,
            "single": ("only %s registered — one call per rect. The companion "
                       "predates the batch tool, or the deploy landed but the "
                       "game has not restarted since." % SINGLE_TOOL),
            "none": ("no JawaBench companion registered. Terrain painting is "
                     "unavailable; run src/RimMandrake/bridgetools/build.py --deploy and "
                     "RESTART the game."),
        }[self.route()]

    # ------------------------------------------------------------------ floors
    def floor_rect(self, x, z, w, h, kind="wood"):
        """Lay a floor rectangle through the architect menu. Instant in god mode.

        CLEARS VEGETATION inside the rect. Distinct from painting terrain: a
        floor is a built thing a pawn can deconstruct, natural terrain is not.
        """
        name = FLOOR_PALETTE.get(kind, kind)
        r = self.s.call("rimworld/apply_architect_designator",
                        designatorId=D("floors", name), x=x, z=z,
                        width=w, height=h, keepSelected=True)
        self.calls += 1
        return bool(r.get("success"))

    def clear_rect(self, x, z, w, h, kind="wood"):
        """Destroy vegetation in a rect by flooring it.

        Still the only PROVEN destruction primitive — the direct ones
        (`Clear area (rect)`) do nothing over the bridge. Use where a built
        surface is plausible, or accept the floor as part of the art.

        ⚠️ Painting terrain is NOT known to do this. See `clears_vegetation`.
        """
        return self.floor_rect(x, z, w, h, kind)

    def floor_cells(self, cells, kind="wood"):
        """Floor an arbitrary cell shape, decomposed into as few rects as possible.

        Follows any shape — blob interiors, cavern chambers, a wrecked hull's
        footprint. There is no batch tool for the architect designator, so this
        is still one call per RECT; decomposing first is what makes it
        affordable. A 400-cell deck is ~40 calls rather than 400.

        Use this only when you want an actual built FLOOR — something a pawn can
        deconstruct. For ground colour, `paint_map` is one call for the whole
        shape and leaves natural terrain rather than a slab.
        """
        name = FLOOR_PALETTE.get(kind, kind)
        did = D("floors", name)
        n = 0
        for (x, z, w, h) in to_rects(set(tuple(c[:2]) for c in cells)):
            try:
                if self.s.call("rimworld/apply_architect_designator",
                               designatorId=did, x=x, z=z, width=w, height=h,
                               keepSelected=True).get("success"):
                    n += w * h
                self.calls += 1
            except Exception:
                pass
        return n

    # ------------------------------------------------------------------ terrain
    def paint(self, cells, terrain):
        """Paint one terrain over an iterable of cells. Returns cells changed."""
        tdef = resolve(terrain)
        return self.paint_map({tuple(c[:2]): tdef for c in cells})

    def paint_rect(self, x, z, w, h, terrain):
        """Paint a single rectangle. One call, no decomposition."""
        return self._send([(resolve(terrain), x, z, w, h)])

    def paint_map(self, cellmap):
        """Paint {(x, z): terrainDef} — the generator entry point.

        Decomposes to rects once, chunks against the companion's guards, and
        sends as few calls as those guards allow. Returns cells changed.
        """
        if not cellmap:
            return 0
        cellmap = {c: resolve(t) for c, t in cellmap.items()}
        return self._send(plan_rects(cellmap))

    def _send(self, rects):
        route = self.route()
        if route == "none":
            for (t, _x, _z, w, h) in rects:
                self.unavailable[t] = self.unavailable.get(t, 0) + w * h
            if self.strict:
                raise NotImplementedError(self.explain_route())
            return 0
        if route == "batch":
            return self._send_batch(rects)
        return self._send_single(rects)

    def _send_batch(self, rects):
        changed = 0
        for batch in chunk_rects(rects):
            # refresh=True on EVERY chunk, not just the last. The companion only
            # dirties the cells it actually changed, so a chunk that skips the
            # refresh leaves its own sections stale — correct in the grid and
            # untouched on screen. Chunks are disjoint, so there is nothing to
            # defer to the end.
            r = self.s.call(BATCH_TOOL, ops=to_ops(batch), layer=self.layer,
                            refresh=True)
            self.calls += 1
            changed += r.get("cellsChanged", 0) or 0
            self.cells_failed += r.get("cellsFailedVerify", 0) or 0
            for e in (r.get("errors") or []):
                self.errors.append(e)
        self.cells_changed += changed
        return changed

    def _send_single(self, rects):
        changed = 0
        for (t, x, z, w, h) in rects:
            try:
                r = self.s.call(SINGLE_TOOL, x=x, z=z, terrainDef=t,
                                width=w, height=h, layer=self.layer,
                                refresh=True)
                self.calls += 1
                changed += r.get("cellsChanged", 0) or 0
                self.cells_failed += r.get("cellsFailedVerify", 0) or 0
            except Exception as e:
                self.errors.append({"rect": (t, x, z, w, h), "error": str(e)[:120]})
                self.unavailable[t] = self.unavailable.get(t, 0) + w * h
        self.cells_changed += changed
        return changed

    # ---------------------------------------------------------- reversibility
    def can_read_batch(self):
        """Is the batched capture tool registered? Probed with the write route."""
        if self._read_batch is None:
            try:
                names = {t.get("name") for t in self.s._rb.list_tools()}
            except Exception:
                names = set()
            self._read_batch = READ_TOOL in names
        return self._read_batch

    def capture(self, cells):
        """Read the current terrain of every cell, so `restore()` can be exact.

        ONE call where the companion offers `jawa/get_terrain_batch`, otherwise
        one `get_cell_info` per cell. That difference is not a micro-optimisation:
        once a formation paints in a single call, the per-cell capture becomes
        the entire cost of the operation — 977 reads is ~16 s against a paint of
        ~1 call. Reversibility should not cost a thousand times the thing it
        makes reversible.

        REFUSES a partial capture, by either route. A None becomes `terrainDef:
        None` on the revert — a silent no-op — while a None == None comparison
        then reports the restore as clean. That exact bug left the permanent
        crater at (45, 190) on a live map.

        On the per-cell route the payload key is `cell.terrainDefName`, NOT
        `cell.terrain`. Getting it wrong returns None for every cell, which is
        the same failure wearing a different hat.
        """
        wanted = sorted(set(tuple(c[:2]) for c in cells))
        if not wanted:
            return {}

        if self.can_read_batch():
            got = {}
            for batch in chunk_rects(
                    [("_",) + r for r in to_rects(wanted)]):
                r = self.s.call(READ_TOOL,
                                rects=";".join("%d,%d,%d,%d" % (x, z, w, h)
                                               for (_t, x, z, w, h) in batch),
                                layer=self.layer)
                self.calls += 1
                got.update(expand_ops(r.get("ops") or ""))
            missing = [c for c in wanted if c not in got]
            source = "%s returned no terrain for" % READ_TOOL
        else:
            got = {}
            for c in wanted:
                got[c] = self.s.terrain_at(c[0], c[1])
                self.calls += 1
            missing = [c for c, v in got.items() if v is None]
            source = "terrain read-back returned None for"

        if missing:
            raise RuntimeError(
                "%s %d of %d cells (e.g. %s). Refusing to capture: an exact "
                "revert is impossible without the originals, and a missing "
                "value becomes a silent no-op on restore. Cells outside the map "
                "and cells with no under-terrain are the usual causes."
                % (source, len(missing), len(wanted), missing[:3]))

        got = {c: t for c, t in got.items() if c in set(wanted)}
        self._originals.update(got)
        return got

    def restore(self, cells=None):
        """Repaint captured originals. Returns cells changed."""
        if cells is None:
            todo = dict(self._originals)
        else:
            wanted = set(tuple(c[:2]) for c in cells)
            todo = {c: t for c, t in self._originals.items() if c in wanted}
        if not todo:
            return 0
        n = self.paint_map(todo)
        for c in todo:
            self._originals.pop(c, None)
        return n

    # ------------------------------------------------------------------ verify
    def verify(self, cellmap, sample=12):
        """Independently read back a sample. Returns (ok, checked, mismatches).

        `cellsFailedVerify` from the companion is already a real grid read-back,
        so this is a second, weaker check on a different channel
        (`get_cell_info`). Cheap insurance against the companion and the bridge
        disagreeing about which map is current.
        """
        keys = sorted(cellmap)
        if not keys:
            return True, 0, []
        step = max(1, len(keys) // max(1, sample))
        picked = keys[::step]
        bad = []
        for (x, z) in picked:
            if self.s.terrain_at(x, z) != resolve(cellmap[(x, z)]):
                bad.append((x, z))
        return (not bad), len(picked), bad

    # ------------------------------------------------------------------ report
    def report(self):
        bits = ["route=%s" % self.route(),
                "%d calls" % self.calls,
                "%d cells changed" % self.cells_changed]
        if self.cells_failed:
            bits.append("%d FAILED VERIFY" % self.cells_failed)
        if self.errors:
            bits.append("%d errors (%s)" % (len(self.errors), self.errors[:2]))
        if self.unavailable:
            total = sum(self.unavailable.values())
            worst = sorted(self.unavailable.items(), key=lambda kv: -kv[1])[:4]
            bits.append("%d cells NOT painted: %s"
                        % (total, ", ".join("%s x%d" % kv for kv in worst)))
        if self._originals:
            bits.append("%d captured cells not yet restored" % len(self._originals))
        return "terrain: " + ", ".join(bits)
