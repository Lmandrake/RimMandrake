#!/usr/bin/env python3
"""stage_proof_site.py -- make the levelling perf scene in the RUNNING game: a fresh 325x325 map, two dug basins, 100 hose
rigs laid, read back at links >= 100. `live_site.py --stage-with FlowWorks` runs it before a proof that reads that scene.

    python.exe src/RimMandrake/FlowWorks/stage_proof_site.py [--max-ticks N] [--max-seconds N]

GAMEENV_FIX_PROOFSITE_DFFDAFCB_ITEMS_WAIT: LEVEL_ALLOC_SHRINK_EIGHTFOLD_OVER_BAR's A1 was sited on the save BENCH_r17_midrain
and read `links=7 < 100`. That save never could hold: every levelling reading on it, on the full list too, peaks at
ports=100 links=50 and starts at 13-15 after a load (D:\\ClaudeWork\\rimmandrake\\levelling_spike\\run\\*_pt.txt, ticks
48007..64257). The links=100 of record (round5, 2026-10-26) was this scene, freshly staged and never reloaded
(infrastructure/state/evidence/LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP/perf_L0_timed.txt).

So this saves nothing: the proof reads the scene in the same game, as round5 did. A saved copy would read what r17 reads.
The recipe is round5's stage.py (a player Settlement on a tile, jawa/world_tile_map_generate at 325x325, a colonist, huge
plants cleared), then pipe_levelling_perf_proof.py's own --no-time phases, so the layout has one owner. Hose maxLength stays
at 80 on success, as the phases leave it: the far lip is 50 away and a hose holds 40 as shipped. The proof reading the scene
puts it back (prove_level_alloc.py); a failed stage puts it back here.

Exit 0 the scene is up and read back, 2 it could not be made (never 1: a site is not a verdict). The last line printed is the
reason. Refuses a game past --max-ticks, like every site that changes a map. --max-seconds: it starts no phase that could
outrun this limit and stops itself cleanly, maxLength put back, because a kill from outside would skip that and leave the
perf proof child running (round5's five phases took 43 + 203 + 235 + 279 + 319 s). Runs under Windows Python: RimBridge binds
Windows loopback.
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PERF_PROOF = os.path.join(HERE, "northstar", "pipe_levelling_perf_proof.py")
NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
HOSE_SETTINGS = "RimMandrake.FlowWorks.Hose.RM_HoseSettings"
SHIPPED_MAX_LENGTH = "40"       # HoseMath.DefaultMaxLength
MAP_SIDE, RIGS, MIN_LINKS = 325, 100, 100
SLICE = 25                      # rigs laid per phase: round5's slices, each inside the phase's 540 s cap
PHASE_TIMEOUT_S = 600
FINISH_S = 120                  # kept back from --max-seconds for the last ticks, the settle and the read-back
TILE_TRIES = 5
GAP_X = (135, 190)              # the rig gap between the basins' lips (pipe_levelling_perf_proof.layout, a 325 map)
NO_LAND = ("Ocean", "Lake", "SeaIce", "IceSheet")
LINKS = re.compile(r"\blinks=(\d+)")


def pick_tiles(rows):
    """jawa/world_tile_export rows -> candidate tiles, best first: land that digs and holds water, flat before small hills,
    nearest a mild 20 C. Pure."""
    found = []
    for r in rows:
        try:
            temp = float(r.get("temperature"))
            tile = int(r.get("tile") if r.get("tile") is not None else r.get("index"))
            if (r.get("hilliness") in ("Flat", "SmallHills") and r.get("biome") not in NO_LAND and float(r.get("elevation")) >= 0
                    and 5 <= temp <= 35 and float(r.get("swampiness") or 0) < 0.3):
                found.append((r.get("hilliness") != "Flat", abs(temp - 20), tile))
        except (TypeError, ValueError):
            continue
    return [t for _, _, t in sorted(found)]


def phases(rigs=RIGS, step=SLICE):
    """-> the perf proof's argument lists: one --no-time phase per slice, the first of them building the site. Pure."""
    out = []
    for lo in range(0, rigs, step):
        a = ["--no-time", "--rigs", str(rigs), "--lay", "%d:%d" % (lo, min(lo + step, rigs))]
        out.append(a if lo == 0 else ["--resume"] + a)
    return out


def phase_fault(res):
    """A --no-time phase's result JSON (None: it wrote none) -> what went wrong, or None. Its exit is 2 by construction (rows
    UNMEASURED 'phase only'), so this reads what it did: it reached the end of its lays, none failed, and the proof's own
    staged_basins_ok held (every row carries it as stagedOk: all dug, all filled, none refused). Pure."""
    if not isinstance(res, dict):
        return "wrote no result"
    if res.get("watchdog") or res.get("governorStop"):
        return str(res.get("watchdog") or res.get("governorStop"))[:200]
    if "laySlice" not in res:
        why = [(r.get("detail") or {}).get("why") for r in res.get("rows") or []]
        return "stopped before the lays: %s" % str(next((w for w in why if w), res.get("mapSize")))[:200]
    if "layFailures" not in res:        # written after the last lay; a crash mid-slice still saves the JSON
        return "stopped inside the lays of slice %s" % (res["laySlice"],)
    if res["layFailures"]:
        return "%s lays failed in slice %s" % (res["layFailures"], res["laySlice"])
    oks = [(r.get("detail") or {}).get("stagedOk") for r in res.get("rows") or []]
    if not oks or not all(ok is True for ok in oks):
        return "the basins did not stage whole: %s" % str(res.get("staged"))[:200]
    return None


def links_of(text):
    """ProofLevelPerf's readout -> links, or None. Pure."""
    m = LINKS.search(text or "")
    return int(m.group(1)) if m else None


def static_call(B, method, arg):
    r = B.call("jawa/static_call", type=NPROOF, method=method, args=arg) or {}
    if not isinstance(r, dict):
        return str(r)
    return str(r.get("result") or r.get("message") or r.get("error") or "")


def make_map(B, rows):
    """A player Settlement and a 325x325 map on the first tile that takes them, made current -> (map id, None) or (None, why)."""
    fs = B.call("jawa/list_factions") or {}
    fs = fs.get("factions") or fs.get("items") or []
    player = [f.get("def") or f.get("defName") for f in fs if f.get("isPlayer")]
    if not player:
        return None, "no player faction in jawa/list_factions"
    tiles = pick_tiles(rows)
    if not tiles:
        return None, "no flat mild land tile among %d in the world" % len(rows)
    why = None
    for tile in tiles[:TILE_TRIES]:
        add = B.call("jawa/world_objects_add", **{"def": "Settlement", "tile": tile, "faction": player[0], "name": "RM_PerfSite"}) or {}
        if add.get("success") is False:
            why = "tile %s took no Settlement: %s" % (tile, str(add)[:160])
            continue
        g = B.call("jawa/world_tile_map_generate", tile=tile, sizeX=MAP_SIDE, sizeZ=MAP_SIDE) or {}
        mid = g.get("mapId") if g.get("mapId") is not None else g.get("mapIndex")
        if not g.get("success") or mid is None:
            why = "tile %s made no map: %s" % (tile, str(g)[:160])
            continue
        cur = B.call("jawa/set_current_map", mapId=int(mid)) or {}
        if cur.get("success") is not True:      # else the map_info below reads the OLD map, maybe a 325 one like r17's
            return None, "map %s would not go current: %s" % (mid, str(cur)[:160])
        mi = B.call("jawa/map_info") or {}
        if (mi.get("sizeX"), mi.get("sizeZ")) != (MAP_SIDE, MAP_SIDE):
            return None, "the current map reads %sx%s after making a %d map" % (mi.get("sizeX"), mi.get("sizeZ"), MAP_SIDE)
        return int(mid), None
    return None, why


def clear_gap(B, clear_plants):
    """Huge plants off the map, then any trunk blocker they left in the rig gap (round5 stage.py)."""
    clear_plants(B)
    clear_plants(B)
    clear_plants(B, margin=10)
    things = (B.call("jawa/list_things", defName="RM_HugeTrunkBlocker", limit=5000) or {}).get("things") or []
    for t in things:
        if GAP_X[0] <= t.get("x", -1) <= GAP_X[1]:
            B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t["x"], t["z"]), categories="Building")


def scene_up(B):
    """True when the current map is 325x325 and a levelling cycle reads the scene's links (a game whose scene still stands)."""
    mi = B.call("jawa/map_info") or {}
    if (mi.get("sizeX"), mi.get("sizeZ")) != (MAP_SIDE, MAP_SIDE):
        return False
    return (links_of(static_call(B, "ProofLevelPerf", "1")) or 0) >= MIN_LINKS


def stage(B, rows_of, run_phase, clear_plants, settle, max_ticks=120000, seconds_left=lambda: PHASE_TIMEOUT_S + FINISH_S):
    """-> (exit code, last line). The seams are the bridge B, rows_of() (the world's tile rows), run_phase(args) (one perf
    proof phase's result JSON), clear_plants(B, margin=), settle(B) (waits for the laid hoses) and seconds_left()."""
    ticks = (B.call("jawa/time_clock") or {}).get("ticksGame")
    if ticks is None:
        return 2, "NOT READY: the bridge gave no ticksGame, so a colony cannot be told from a test map"
    if int(ticks) > max_ticks:
        return 2, "NOT READY: the game is %s ticks old, past --max-ticks %d: a colony, not a test map" % (ticks, max_ticks)
    if scene_up(B):
        # an earlier proof may have put maxLength back to 40 after reading it; the hoses are still down, so hold 80 again
        # restore-check: ok a site holds 80 for the proof after it; prove_level_alloc.put_back undoes it in a finally
        held = B.call("jawa/mod_settings_field", typeName=HOSE_SETTINGS, action="set", field="maxLength", value="80") or {}
        if held.get("success") is not True:
            return 2, "NOT READY: the scene stands, but hose maxLength would not go back to 80: %s" % str(held)[:160]
        return 0, "READY: the 100-rig scene already stands on the current map"
    mid, why = make_map(B, rows_of())
    if why:
        return 2, "NOT READY: %s" % why
    fail = None
    try:
        B.call("jawa/spawn_pawn", kindDef="Colonist", x=320, z=323, faction="player")
        clear_gap(B, clear_plants)
        for args in phases():
            if seconds_left() < PHASE_TIMEOUT_S + FINISH_S:
                fail = "out of time before perf phase %s (%.0f s left, a phase may take %d and the finish %d)" % (
                    " ".join(args), seconds_left(), PHASE_TIMEOUT_S, FINISH_S)
                return 2, "NOT READY: " + fail
            fault = phase_fault(run_phase(args))
            if fault:
                fail = "perf phase %s: %s" % (" ".join(args), fault)
                return 2, "NOT READY: " + fail
        B.ticks(260)        # as the perf proof's timing phase does before it reads the links
        settle(B)
        text = static_call(B, "ProofLevelPerf", "1")
        links = links_of(text)
        if links is None or links < MIN_LINKS:
            fail = "the staged scene reads links=%s < %d: %s" % (links, MIN_LINKS, text[:200])
            return 2, "NOT READY: " + fail
        return 0, "READY: map %s 325x325, %d rigs, links=%d, hose maxLength 80 until the proof puts it back" % (mid, RIGS, links)
    except Exception:
        fail = "raised"
        raise
    finally:
        if fail:    # the phases leave 80 for the next one; there is no next one, and no proof to put it back
            B.call("jawa/mod_settings_field", typeName=HOSE_SETTINGS, action="set", field="maxLength", value=SHIPPED_MAX_LENGTH)


def _phase_runner(args):
    """One perf proof phase in its own process -> its result JSON or None (its exit is 2 by construction: not read)."""
    fd, out = tempfile.mkstemp(prefix="level_perf_stage_", suffix=".json")
    os.close(fd)
    try:
        r = subprocess.run([sys.executable, PERF_PROOF, out] + args, capture_output=True, text=True, timeout=PHASE_TIMEOUT_S,
                           stdin=subprocess.DEVNULL)
        print(((r.stdout or "") + (r.stderr or "")).strip()[-400:], flush=True)
        with open(out, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError, subprocess.TimeoutExpired) as e:
        print("perf phase %s: %s: %s" % (args, type(e).__name__, str(e)[:200]), flush=True)
        return None
    finally:
        try:
            os.unlink(out)
        except OSError:
            pass


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--max-ticks", type=int, default=120000)
    ap.add_argument("--max-seconds", type=int, default=2100)
    a = ap.parse_args(argv)
    t0 = time.time()
    for p in (os.path.join(HERE, "..", "Utils"), os.path.join(HERE, "northstar")):
        sys.path.insert(0, p)
    try:
        import proof_hose as PH
        import validation_core as V
        B = V.guard(PH.PB())

        def rows_of():
            path = os.path.join(os.environ.get("TEMP") or tempfile.gettempdir(), "level_perf_stage_tiles.csv")
            r = B.call("jawa/world_tile_export", path=path) or {}
            if not r.get("success"):
                raise RuntimeError("jawa/world_tile_export failed: %s" % str(r)[:200])
            with open(path, encoding="utf-8") as f:
                return list(csv.DictReader(f))

        def settle(bridge):
            V.settle_census(lambda: bridge.hp("census", answer=True), lambda h: True)

        def run_phase(args):
            res = _phase_runner(args)
            B.S.close()         # this socket sat idle through the phase: the next call gets a fresh one
            B.S.connect()
            return res

        rc, line = stage(B, rows_of, run_phase, V.clear_huge_plants, settle, a.max_ticks, lambda: a.max_seconds - (time.time() - t0))
    except Exception as e:      # noqa: BLE001  any bridge failure is a site not made, never a verdict
        rc, line = 2, "NOT READY: %s: %s" % (type(e).__name__, str(e)[:300])
    print(line, flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
