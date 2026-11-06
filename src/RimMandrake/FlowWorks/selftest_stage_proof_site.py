#!/usr/bin/env python3
"""selftest_stage_proof_site.py - FlowWorks/stage_proof_site.py against a fake bridge, offline.

GAMEENV_FIX_PROOFSITE_DFFDAFCB_ITEMS_WAIT: a stage that did not make a real 100-link scene must never read READY (it would
send the alloc proof to another `links=7`), the phases must lay every rig exactly once with the first one building the site,
and a failed stage must not leave hose maxLength at 80. The live read of the scene is LEVEL_ALLOC_SHRINK_EIGHTFOLD_OVER_BAR's
A1. Exit 0 = every case as expected.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage_proof_site as S  # noqa: E402

bad = 0


def check(name, ok, extra=""):
    global bad
    bad += not ok
    print("%s %s%s" % ("ok " if ok else "BAD", name, "" if ok else "  " + str(extra)[:300]))


def tile(t, biome="TemperateForest", hill="Flat", temp="20", elev="100", swamp="0"):
    return {"tile": str(t), "biome": biome, "hilliness": hill, "temperature": temp, "elevation": elev, "swampiness": swamp}


ROWS = [tile(1, biome="Ocean"), tile(2, hill="Mountainous"), tile(3, temp="-30"), tile(4, elev="-5"), tile(5, swamp="0.9"),
        tile(6, hill="SmallHills"), tile(7, temp="30"), tile(8, temp="21"), {"tile": "x", "temperature": "?"}]
GOOD_PHASE = {"laySlice": [0, 25], "layFailures": 0, "staged": [{"dug": 38125}, {"dug": 38125}],
              "rows": [{"detail": {"why": "phase only", "stagedOk": True}}] * 2}


class Fake:
    """call(tool, **kw) as V.guard(PH.PB()) takes it. `links` is what ProofLevelPerf reads, per call (the last one repeats)."""

    def __init__(self, links=(100,), ticks=500, size=(250, 250), refuse=(), gen_ok=True, no_clock=False):
        self.links, self.tick_n, self.size, self.refuse, self.gen_ok, self.no_clock = list(links), ticks, size, refuse, gen_ok, no_clock
        self.calls, self.advanced, self.current = [], 0, None

    def names(self):
        return [c[0] for c in self.calls]

    def ticks(self, n):
        self.advanced += n

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "jawa/time_clock":
            return {} if self.no_clock else {"ticksGame": self.tick_n}
        if tool == "jawa/map_info":
            return {"sizeX": self.size[0], "sizeZ": self.size[1]}
        if tool == "jawa/list_factions":
            return {"factions": [{"def": "Ancients"}, {"def": "PlayerColony", "isPlayer": True}]}
        if tool == "jawa/world_objects_add":
            return {"success": kw["tile"] not in self.refuse}
        if tool == "jawa/world_tile_map_generate":
            return {"success": self.gen_ok, "mapId": 4}
        if tool == "jawa/set_current_map":
            self.size = (S.MAP_SIDE, S.MAP_SIDE)
            return {"success": True}
        if tool == "jawa/list_things":
            return {"things": [{"x": 150, "z": 40}, {"x": 20, "z": 40}]}
        if tool == "jawa/static_call":
            n = self.links.pop(0) if len(self.links) > 1 else self.links[0]
            return {"result": "LEVELPERF calls=1 links=%d moves=1" % n}
        return {"success": True}


def run(b, phase=lambda args: GOOD_PHASE, rows=ROWS, max_ticks=120000, left=lambda: 2100):
    seen = []

    def run_phase(args):
        seen.append(args)
        return phase(args)
    code, line = S.stage(b, lambda: rows, run_phase, lambda B, margin=6: b.calls.append(("clear", {"margin": margin})),
                         lambda B: b.calls.append(("settle", {})), max_ticks, left)
    return code, line, seen


def length_writes(b):
    return [kw["value"] for t, kw in b.calls if t == "jawa/mod_settings_field" and kw.get("field") == "maxLength"]


check("pick_tiles: mild flat land, flat first then nearest 20 C; water, mountain, cold, below sea, swamp, junk all out",
      S.pick_tiles(ROWS) == [8, 7, 6], S.pick_tiles(ROWS))
check("pick_tiles: `index` serves when the export has no `tile`", S.pick_tiles([{**tile(0), "tile": None, "index": "9"}]) == [9])
ph = S.phases()
laid = [int(x) for a in ph for x in range(*map(int, a[a.index("--lay") + 1].split(":")))]
check("phases: every rig laid exactly once", laid == list(range(100)), laid[:8])
check("phases: only the first builds the site; all are --no-time at 100 rigs",
      "--resume" not in ph[0] and all("--resume" in a for a in ph[1:]) and all("--no-time" in a and a[a.index("--rigs") + 1] == "100" for a in ph))
check("phase_fault: a clean slice is no fault", S.phase_fault(GOOD_PHASE) is None)
for name, res in (("no result", None), ("a failed lay", {**GOOD_PHASE, "layFailures": 2}), ("basins not staged whole (a partial dig)", {**GOOD_PHASE, "rows": [{"detail": {"stagedOk": False}}]}),
                  ("no rows to say the basins took", {**GOOD_PHASE, "rows": []}), ("one row unsure of the basins", {**GOOD_PHASE, "rows": [{"detail": {"stagedOk": True}}, {"detail": {}}]}),
                  ("a crash mid-slice: laySlice but no layFailures", {k: v for k, v in GOOD_PHASE.items() if k != "layFailures"}),
                  ("a spent watchdog", {**GOOD_PHASE, "watchdog": "budget"}), ("a stop before the lays", {"mapSize": [250, 250], "rows": [{"detail": {"why": "site"}}]})):
    check("phase_fault: %s is a fault" % name, S.phase_fault(res))

b = Fake()
code, line, seen = run(b)
check("stage: READY with links=100 read back, map made first, 4 phases: %s" % line,
      code == 0 and line.startswith("READY") and "links=100" in line and len(seen) == 4)
n = b.names()
check("stage: order is map, current, colonist, plants, then the phases' 260 ticks and settle",
      n.index("jawa/world_tile_map_generate") < n.index("jawa/set_current_map") < n.index("jawa/spawn_pawn") < n.index("clear") < n.index("settle") and b.advanced == 260, n)
gen = [kw for t, kw in b.calls if t == "jawa/world_tile_map_generate"][0]
check("stage: the map asked for is 325x325 on the best tile", gen == {"tile": 8, "sizeX": 325, "sizeZ": 325}, gen)
check("stage: success leaves maxLength for the proof to put back", length_writes(b) == [])
check("stage: only trunk blockers inside the rig gap are destroyed",
      [kw["rects"] for t, kw in b.calls if t == "jawa/destroy_batch"] == ["150,40,1,1"])
check("stage: nothing is saved", not [t for t in n if "save" in t])

b = Fake(links=(7,))
code, line, _ = run(b)
check("stage: a scene reading links=7 is NOT READY, never READY, and names the count: %s" % line[:80],
      code == 2 and line.startswith("NOT READY") and "links=7" in line and length_writes(b) == ["40"], line)
b = Fake(links=(99,))
code, line, _ = run(b)
check("stage: links=99 is NOT READY", code == 2 and "links=99" in line and length_writes(b) == ["40"], line)
b = Fake()
code, line, seen = run(b, phase=lambda args: None if "25:50" in args else GOOD_PHASE)
check("stage: a phase that fails stops the rest and puts maxLength back",
      code == 2 and len(seen) == 2 and "25:50" in line and length_writes(b) == ["40"] and b.advanced == 0, (line, seen))
clock = iter([S.PHASE_TIMEOUT_S + S.FINISH_S, S.PHASE_TIMEOUT_S + S.FINISH_S - 1, 500, 500])
b = Fake()
code, line, seen = run(b, left=lambda: next(clock))
check("stage: too little time left for the next phase -> stops itself, no phase started, maxLength back",
      code == 2 and "out of time" in line and len(seen) == 1 and length_writes(b) == ["40"], (line, seen))
b = Fake(size=(325, 325), links=(100,))
code, line, seen = run(b)
check("stage: a standing scene is not rebuilt, and maxLength is held at 80 again for it",
      code == 0 and not seen and "jawa/world_tile_map_generate" not in b.names() and length_writes(b) == ["80"], line)


class NoHold(Fake):
    def call(self, tool, **kw):
        r = Fake.call(self, tool, **kw)
        return {"success": False} if tool == "jawa/mod_settings_field" else r


class NoCurrent(Fake):
    def call(self, tool, **kw):
        if tool == "jawa/set_current_map":
            return {"success": False}
        return Fake.call(self, tool, **kw)


b = NoCurrent(size=(325, 325), links=(50,))
code, line, seen = run(b)
check("stage: a new map that will not go current never stages the old 325 map", code == 2 and "would not go current" in line and not seen, line)
b = NoHold(size=(325, 325), links=(100,))
code, line, seen = run(b)
check("stage: a standing scene whose 80 is refused is NOT READY", code == 2 and "would not go back" in line, line)
b = Fake(size=(325, 325), links=(50, 100))
code, line, seen = run(b)
check("stage: a 325 map short of the links (r17's 50) gets a fresh scene", code == 0 and len(seen) == 4 and "jawa/world_tile_map_generate" in b.names(), line)
b = Fake(ticks=900000)
code, line, seen = run(b)
check("stage: a colony past --max-ticks is refused and untouched",
      code == 2 and "past --max-ticks" in line and not seen and "jawa/world_objects_add" not in b.names())
b = Fake(no_clock=True)
code, line, seen = run(b)
check("stage: an unread clock is refused, not read as tick 0", code == 2 and "ticksGame" in line and "jawa/world_objects_add" not in b.names())
b = Fake(refuse=(8,))
code, line, seen = run(b)
check("stage: a tile that takes no Settlement moves to the next", code == 0 and [kw for t, kw in b.calls if t == "jawa/world_tile_map_generate"][0]["tile"] == 7, line)
b = Fake(gen_ok=False)
code, line, seen = run(b)
check("stage: no tile makes a map -> NOT READY, no phases", code == 2 and "made no map" in line and not seen, line)
b = Fake()
code, line, seen = run(b, rows=[tile(1, biome="Ocean")])
check("stage: a world with no fit tile -> NOT READY", code == 2 and "no flat mild land" in line and "jawa/world_objects_add" not in b.names(), line)


class Boom(Fake):
    def ticks(self, n):
        raise RuntimeError("bridge gone")


b = Boom()
try:
    run(b)
    raised = False
except RuntimeError:
    raised = True
check("stage: a raise past the phases still puts maxLength back", raised and length_writes(b) == ["40"])

print("RESULT: %s" % ("FAIL (%d)" % bad if bad else "PASS"))
sys.exit(1 if bad else 0)
