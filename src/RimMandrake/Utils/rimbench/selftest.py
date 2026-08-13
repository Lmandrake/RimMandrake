"""Offline proof of the terrain pipeline. No game, no bridge, no mods.

WHAT THIS IS FOR
================
The expensive failure in this project is a generator that paints a hole nobody
can see: a decomposer that drops a cell, an encoder that mangles a rect, a
payload that silently exceeds the companion's guard and gets rejected after a
5-second round trip. Every one of those is decidable on this side of the socket,
and a game load is 23–30 minutes.

So everything between "the generator produced a cell map" and "the bytes leave
the client" is proven here, offline, in under a second:

  1. `to_rects` is an EXACT COVER — same cell set, zero overlap.
  2. `plan_rects` keeps terrains separate and still covers exactly.
  3. `to_ops` round-trips through a faithful port of the C# parser.
  4. `chunk_rects` never exceeds MaxOps or MaxCells, and never loses a rect.

Point 3 is the one that matters most and is easiest to get wrong: the parser
below is deliberately a re-implementation of `TryParseOps` in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs`, not a reuse of our
own encoder. An encoder tested against itself proves nothing.

    python3 src/RimMandrake/Utils/rimbench/selftest.py

Runs under plain Linux python3 — this is the one part of the bridge stack that
does NOT need `python.exe`, because it never opens a socket.
"""
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from scatter import noise
from terrain import (MAX_CELLS, MAX_OPS, chunk_rects, expand_ops, plan_rects,
                     to_ops, to_read_ops, to_rects)
from terrain import parse_ops as production_parse_ops

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s  %s" % (name, detail))
        FAILURES.append(name)


# ------------------------------------------------------------------ fixtures

def dithered_crater(cx, cz, R, seed=7, squash=0.82, ray_dir=0.6):
    """The same four-zone dithered crater the timing harness paints.

    Reproduced here rather than imported because `crater.py` opens the bridge
    client at import time. The shape is what matters: a dithered boundary
    interlocks on purpose, which is close to the worst realistic case for rect
    packing. If the pipeline is exact on this, it is exact on anything.
    """
    cells = {}
    span = int(R * 1.7) + 1
    for dx in range(-span, span + 1):
        for dz in range(-span, span + 1):
            x, z = cx + dx, cz + dz
            ex, ez = dx, dz / squash
            d = math.sqrt(ex * ex + ez * ez) / R
            n = noise(x, z, seed)
            d += (n - 0.5) * 0.18
            ang = math.atan2(dz, dx)
            ray = 0.5 + 0.5 * math.cos((ang - ray_dir) * 3.0)
            if d < 0.30:
                cells[(x, z)] = "Sand"
            elif d < 0.65:
                cells[(x, z)] = "Gravel"
            elif d < 1.00:
                cells[(x, z)] = "Soil"
            elif d < 1.45:
                fade = (1.45 - d) / 0.45
                if n < 0.42 * fade * ray:
                    cells[(x, z)] = "Gravel"
    return cells


def parse_ops(ops, default_terrain=None):
    """Faithful port of TryParseOps from JawaBenchTerrainTools.cs.

    Deliberately mirrors the C# including its tolerances — ';' or newline
    separators, optional 'Terrain:' prefix, optional w/h defaulting to 1 — so a
    disagreement between this and `to_ops` is a real protocol bug rather than a
    difference of opinion between two of our own functions.

    Returns (rects, errors). The C# treats ANY error as fatal to the whole
    call ("partial success is worse than none"), so errors must be empty.
    """
    rects, errors = [], []
    tokens = [t for t in ops.replace("\r", "\n").replace("\n", ";").split(";") if t]
    for i, raw in enumerate(tokens):
        token = raw.strip()
        if not token:
            continue
        terrain, coord = default_terrain, token
        if ":" in token:
            head, coord = token.split(":", 1)
            terrain = head.strip()
        if not terrain:
            errors.append("op %d names no terrain" % i)
            continue
        nums = [p for p in coord.split(",") if p]
        if not 2 <= len(nums) <= 4:
            errors.append("op %d needs x,z[,w[,h]] — got %d" % (i, len(nums)))
            continue
        try:
            vals = [int(p.strip()) for p in nums]
        except ValueError:
            errors.append("op %d has a non-integer coordinate" % i)
            continue
        x, z = vals[0], vals[1]
        w = vals[2] if len(vals) > 2 else 1
        h = vals[3] if len(vals) > 3 else 1
        if w < 1 or h < 1:
            errors.append("op %d has width/height < 1" % i)
            continue
        rects.append((terrain, x, z, w, h))
    return rects, errors


def expand(rects):
    """Rects -> {(x, z): terrain}, and the count of doubly-covered cells."""
    out, overlaps = {}, 0
    for (t, x, z, w, h) in rects:
        for dx in range(w):
            for dz in range(h):
                c = (x + dx, z + dz)
                if c in out:
                    overlaps += 1
                out[c] = t
    return out, overlaps


# --------------------------------------------------------------------- tests

def test_exact_cover():
    print("\nto_rects is an exact cover")
    for R in (3, 6, 12, 20, 32):
        cells = dithered_crater(100, 100, R)
        keys = set(cells)
        rects = to_rects(keys)
        got, overlaps = expand([("X", x, z, w, h) for (x, z, w, h) in rects])
        check("R=%-3d %5d cells -> %4d rects, same set" % (R, len(keys), len(rects)),
              set(got) == keys,
              "missing=%d extra=%d" % (len(keys - set(got)), len(set(got) - keys)))
        check("R=%-3d zero overlap" % R, overlaps == 0, "overlaps=%d" % overlaps)


def test_plan_rects_multi_terrain():
    print("\nplan_rects keeps terrains separate and covers exactly")
    for R in (6, 12, 20):
        cells = dithered_crater(100, 100, R)
        rects = plan_rects(cells)
        got, overlaps = expand(rects)
        check("R=%-3d %d terrains, cell set preserved"
              % (R, len(set(cells.values()))), got == cells,
              "%d cells differ" % len({c for c in set(got) | set(cells)
                                       if got.get(c) != cells.get(c)}))
        check("R=%-3d zero overlap across terrains" % R, overlaps == 0,
              "overlaps=%d" % overlaps)
        check("R=%-3d deterministic" % R, plan_rects(cells) == rects)


def test_ops_round_trip():
    print("\nto_ops round-trips through the C# grammar")
    for R in (3, 6, 12, 20, 32):
        cells = dithered_crater(100, 100, R)
        rects = plan_rects(cells)
        ops = to_ops(rects)
        back, errors = parse_ops(ops)
        check("R=%-3d %5d bytes, %4d ops, parses clean" % (R, len(ops), len(rects)),
              not errors, "; ".join(errors[:3]))
        check("R=%-3d rect list identical" % R, back == rects)
        got, _ = expand(back)
        check("R=%-3d decoded cell map identical" % R, got == cells)


def test_negative_coordinates():
    print("\nnegative and zero coordinates survive the grammar")
    # A formation near the map edge legitimately plans cells at x<0; the
    # companion clips them as out-of-bounds rather than failing, but the ops
    # string still has to carry the minus sign intact.
    rects = [("Sand", -4, 0, 3, 2), ("Gravel", 0, -7, 1, 1)]
    back, errors = parse_ops(to_ops(rects))
    check("negatives parse clean", not errors, "; ".join(errors[:3]))
    check("negatives round-trip", back == rects)


def test_chunking():
    print("\nchunk_rects respects both guards and loses nothing")
    cells = dithered_crater(100, 100, 32)
    rects = plan_rects(cells)
    for max_ops, max_cells in ((MAX_OPS, MAX_CELLS), (64, MAX_CELLS),
                               (MAX_OPS, 200), (16, 100)):
        chunks = list(chunk_rects(rects, max_ops, max_cells))
        worst_ops = max(len(c) for c in chunks)
        worst_cells = max(sum(r[3] * r[4] for r in c) for c in chunks)
        flat = [r for c in chunks for r in c]
        check("ops<=%-5d cells<=%-6d -> %3d chunks (worst %d ops, %d cells)"
              % (max_ops, max_cells, len(chunks), worst_ops, worst_cells),
              worst_ops <= max_ops and worst_cells <= max_cells)
        check("ops<=%-5d cells<=%-6d every rect kept, in order"
              % (max_ops, max_cells), flat == rects)


def test_guard_headroom():
    print("\na realistic formation fits inside one call")
    # The guards exist to stop a payload stalling the main thread. This asserts
    # they are not so tight that ordinary generator output trips them, which
    # would turn every formation into a multi-call operation and give back the
    # call-count win the batch tool exists to deliver.
    for R in (12, 20, 32):
        cells = dithered_crater(100, 100, R)
        rects = plan_rects(cells)
        total = sum(r[3] * r[4] for r in rects)
        chunks = list(chunk_rects(rects))
        check("R=%-3d %5d cells / %4d ops -> %d call(s)"
              % (R, total, len(rects), len(chunks)), len(chunks) == 1,
              "needs %d calls; ops=%d/%d cells=%d/%d"
              % (len(chunks), len(rects), MAX_OPS, total, MAX_CELLS))


def test_whole_map_is_rejected_loudly():
    print("\na whole-map paint exceeds the guard, and must chunk rather than lie")
    # 250x250 = 62,500 cells, under MaxCells; 300x300 = 90,000, over it. The
    # correct behaviour is to split into several accepted calls, never to send
    # one the companion will refuse.
    big = [("Sand", 0, z, 300, 1) for z in range(300)]
    chunks = list(chunk_rects(big))
    worst = max(sum(r[3] * r[4] for r in c) for c in chunks)
    check("90,000 cells -> %d chunks, worst %d cells" % (len(chunks), worst),
          worst <= MAX_CELLS and len(chunks) > 1)
    check("no rect lost", [r for c in chunks for r in c] == big)


def test_production_decoder_agrees():
    print("\nthe production decoder agrees with the independent C# port")
    # terrain.parse_ops is what capture() actually runs against a live reply.
    # Checking it against parse_ops above — written from the C# rather than from
    # our encoder — is the only way it gets tested by something that did not
    # inherit its assumptions.
    for R in (6, 12, 20):
        cells = dithered_crater(100, 100, R)
        ops = to_ops(plan_rects(cells))
        ref, errors = parse_ops(ops)
        check("R=%-3d reference parser clean" % R, not errors)
        check("R=%-3d production parser identical" % R,
              production_parse_ops(ops) == ref)
        check("R=%-3d expand_ops reproduces the cell map" % R,
              expand_ops(ops) == cells)


def test_capture_round_trip():
    print("\ncapture -> restore round-trips through the companion's grammar")
    # jawa/get_terrain_batch answers in the same grammar jawa/set_terrain_batch
    # accepts, run-length encoded one row at a time. This simulates that reply
    # and proves a captured region restores to exactly what was there.
    for R in (6, 12, 20):
        cells = dithered_crater(100, 100, R)
        original = {c: "Slate_Rough" if (c[0] + c[1]) % 3 else "Sand"
                    for c in cells}                      # two-terrain ground

        req = to_read_ops(set(cells))
        asked = set()
        for (_t, x, z, w, h) in production_parse_ops(req, default_terrain="_"):
            for dx in range(w):
                for dz in range(h):
                    asked.add((x + dx, z + dz))
        check("R=%-3d read request covers exactly the cells wanted" % R,
              asked == set(cells))

        # the companion's RunLengthEncode: runs along x within a row
        runs, keys = [], sorted(original, key=lambda c: (c[1], c[0]))
        for c in keys:
            t = original[c]
            if runs and runs[-1][2] == c[1] and runs[-1][1] + runs[-1][3] == c[0] \
                    and runs[-1][0] == t:
                runs[-1][3] += 1
            else:
                runs.append([t, c[0], c[1], 1])
        reply = ";".join("%s:%d,%d,%d,1" % tuple(r) for r in runs)
        check("R=%-3d %d cells -> %d runs (%d bytes)"
              % (R, len(original), len(runs), len(reply)),
              expand_ops(reply) == original)


def test_spawn_ops():
    print("\nspawn ops encode and parse under the same C# grammar")
    from place import chunk_items, to_spawn_ops
    items = [("Filth_Ash", 10, 20, 1), ("ChunkSlagSteel", -3, 4, 7),
             ("Filth_RubbleRock", 0, 0, 1)]
    ops = to_spawn_ops(items)
    back, errors = parse_ops(ops)
    check("spawn ops parse clean", not errors, "; ".join(errors[:3]))
    # The companion reuses TryParseOps, so a spawn op arrives as (def,x,z,W,H)
    # with W carrying the stack count and H defaulting to 1. Assert that
    # mapping explicitly -- it is a shared-grammar shortcut and the kind of
    # thing that silently means something else after an edit.
    check("count lands in W, H defaults to 1",
          back == [("Filth_Ash", 10, 20, 1, 1), ("ChunkSlagSteel", -3, 4, 7, 1),
                   ("Filth_RubbleRock", 0, 0, 1, 1)], str(back))
    big = [("Filth_Ash", i % 250, i // 250, 1) for i in range(9000)]
    chunks = list(chunk_items(big))
    check("9,000 spawns -> %d chunks, worst %d ops"
          % (len(chunks), max(len(c) for c in chunks)),
          max(len(c) for c in chunks) <= MAX_OPS
          and [i for c in chunks for i in c] == big)


def test_formations_are_batched():
    """Every formation must be O(1)-ish in calls, not O(cells).

    This is the regression that matters: the whole point of the companion is
    that a formation is a handful of hops. A refactor that reintroduces a
    per-cell loop would still look correct and still produce the right map --
    it would just take 100x longer, which no unit test would otherwise notice.
    """
    print("\nformations stay batched (call counts, against a stub game)")
    import formations

    class StubRB(object):
        def list_tools(self):
            return [{"name": n} for n in
                    ("jawa/set_terrain", "jawa/set_terrain_batch",
                     "jawa/get_terrain_batch", "jawa/spawn_batch",
                     "jawa/destroy_batch")]

    class StubSession(object):
        def __init__(self):
            self._rb = StubRB()
            self.tally = {}

        def call(self, tool, **p):
            self.tally[tool] = self.tally.get(tool, 0) + 1
            if tool == "rimworld/get_cell_info":
                return {"cell": {"terrainDefName": "Soil", "things": []}}
            if tool == "jawa/get_terrain_batch":
                return {"ops": "Soil:0,0,1,1"}
            if tool == "jawa/set_terrain_batch":
                return {"cellsChanged": 1, "cellsFailedVerify": 0, "errors": []}
            if tool == "jawa/spawn_batch":
                n = len(p["ops"].split(";"))
                return {"spawned": n, "failed": 0, "errors": [], "perDef": {}}
            return {"success": True, "cellsChanged": 1, "cellsFailedVerify": 0}

        def terrain_at(self, x, z):
            return self.call("rimworld/get_cell_info", x=x, z=z)["cell"]["terrainDefName"]

        def things_at(self, x, z):
            return []

    for name, fn, budget in (
            ("crater", lambda s: formations.crater(s, 100, 100, radius=12), 4),
            ("geyser_field", lambda s: formations.geyser_field(s, 100, 100), 4),
    ):
        s = StubSession()
        fn(s)
        total = sum(s.tally.values())
        spawn = s.tally.get("jawa/spawn_batch", 0)
        paint = s.tally.get("jawa/set_terrain_batch", 0)
        check("%-13s %d call(s) total (<=%d): %d paint, %d spawn"
              % (name, total, budget, paint, spawn),
              total <= budget and spawn <= 1 and paint <= 1, str(s.tally))


def main():
    print("rimbench terrain pipeline — offline selftest")
    print("MAX_OPS=%d  MAX_CELLS=%d  (mirroring JawaBenchTerrainTools.cs)"
          % (MAX_OPS, MAX_CELLS))
    test_exact_cover()
    test_plan_rects_multi_terrain()
    test_ops_round_trip()
    test_negative_coordinates()
    test_chunking()
    test_guard_headroom()
    test_whole_map_is_rejected_loudly()
    test_production_decoder_agrees()
    test_capture_round_trip()
    test_spawn_ops()
    test_formations_are_batched()
    print("\n%s" % ("ALL PASS" if not FAILURES
                    else "%d FAILURES: %s" % (len(FAILURES), FAILURES[:5])))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
