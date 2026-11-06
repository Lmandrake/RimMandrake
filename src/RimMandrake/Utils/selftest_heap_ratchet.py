#!/usr/bin/env python3
"""selftest_heap_ratchet.py - heap_ratchet.py can tell the causes apart. Synthetic TPS records in a temp dir, offline."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import heap_ratchet as H  # noqa: E402

FAILS = []
SID = "abcd1234" + "0" * 24
FINDING = os.path.join(HERE, "..", "..", "..", "infrastructure", "state", "facts", "heap_reload_ratchet_2026-11-06.md")


def check(name, ok, detail=None):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  :: %r" % (detail,)))
    if not ok:
        FAILS.append(name)


def session(d, games, sid=SID, mods=317, torn=False):
    """games: [(save, floor, reserved, things)]. Each game: a high reading, a GC down to the floor, a climb back."""
    rows, seq, gc = [{"seq": 1, "kind": "session", "mods": mods}], 1, 100
    for i, (save, floor, reserved, things) in enumerate(games, 1):
        def add(**kw):
            nonlocal seq
            seq += 1
            kw["seq"] = seq
            rows.append(kw)
        add(kind="game", game=i, save=save)
        add(kind="sample", heapMB=floor + 400, gc=gc)
        gc += 1
        add(kind="sample", heapMB=floor, gc=gc)
        add(kind="sample", heapMB=floor + 300, gc=gc)
        add(kind="context", heapMB=floor + 300, monoUsedMB=floor + 300, monoHeapMB=reserved,
            maps=[{"things": things}])
    path = os.path.join(d, "tps_20261106T000000Z_%s_1_000.jsonl" % sid)
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
        if torn:
            fh.write('{"seq": 99, "kind": "sam')
    return sid


def read(games, **kw):
    with tempfile.TemporaryDirectory() as d:
        session(d, games, **kw)
        return H.report(d, SID[:8])


# things deliberately unrelated to the game count: 5k, 40k, 12k, 60k, 8k, 30k
THINGS = [5000, 40000, 12000, 60000, 8000, 30000]

v = read([("s", 3000 + 200 * i, 4000 + 200 * i, THINGS[i]) for i in range(6)])
check("floor climbing with the game count, things unrelated, reads reload_ratchet", v["verdict"] == "reload_ratchet", v)
check("the floor is the post-GC low, not the highest or the context reading", v["games"][0]["floor"] == 3000, v["games"][0])

v = read([("s", 2000 + THINGS[i] / 20.0, 6000, THINGS[i]) for i in range(6)])
check("floor following things, not order, reads map_scale", v["verdict"] == "map_scale", v["evidence"])

v = read([("s", 3000 + (i % 2) * 40, 4000 + 300 * i, THINGS[i]) for i in range(6)])
check("level floor under rising reserved reads high_water_only", v["verdict"] == "high_water_only", v["evidence"])

v = read([("s", 3000, 4000, THINGS[i]) for i in range(6)])
check("nothing moving reads flat", v["verdict"] == "flat", v["evidence"])

v = read([("s", f, 6000, 8000) for f in (3000, 3000, 5000, 3000, 5000, 3000, 3500, 3500)])
check("a rise following neither series reads mixed", v["verdict"] == "mixed", v["evidence"])

v = read([("s", 3000 + 200 * i, 4000, 5000) for i in range(3)])
check("three games cannot separate causes: UNMEASURED", v["verdict"] == "UNMEASURED", v["evidence"])

# a game with no GC has no floor: its lowest reading would be a guess, never zero and never a data point
games = H.per_game([{"seq": 1, "kind": "game", "game": 1, "save": ""}, {"seq": 2, "kind": "sample", "heapMB": 500, "gc": 7},
                    {"seq": 3, "kind": "sample", "heapMB": 450, "gc": 7}])
check("no GC in the game: floor is None", games[0]["floor"] is None, games)

# a run of same-save loads is the control that holds the map fixed
v = read([("calm", 3000 + 60 * i, 4000, 13000) for i in range(4)] + [("other", 3500, 4000, 9000)])
check("same-save run found and its slope is per load", v["sameSave"][0]["save"] == "calm" and v["sameSave"][0]["mbPerLoad"] == 60.0,
      v["sameSave"])

with tempfile.TemporaryDirectory() as d:
    session(d, [("s", 3000 + 200 * i, 4000 + 200 * i, THINGS[i]) for i in range(6)], torn=True)
    check("a torn last line is skipped, not fatal", H.report(d, SID[:8])["verdict"] == "reload_ratchet")
    check("an absent session exits 2 (UNMEASURED), never a verdict", H.main(["--dir", d, "--session", "ffffffff"]) == 2)
    check("--require matched exits 0", H.main(["--dir", d, "--session", SID[:8], "--require", "reload_ratchet"]) == 0)
    check("--require missed exits 1", H.main(["--dir", d, "--session", SID[:8], "--require", "map_scale"]) == 1)
    check("--same-save with no such run exits 2", H.main(["--dir", d, "--session", SID[:8], "--same-save", "nope"]) == 2)

with open(FINDING, encoding="utf-8") as fh:
    text = fh.read()
check("the written finding names the verdict and the item", "reload_ratchet" in text and
      "HEAP_DIAGNOSE_RELOAD_RATCHET_NOT_MAP_SCALE" in text)

print("%d failures" % len(FAILS))
sys.exit(1 if FAILS else 0)
