#!/usr/bin/env python3
"""
bridge_latency.py - measure RimBridge round-trip latency on a LIVE game.

WHY THIS EXISTS
===============
`design/RimMandrake/map_authoring_decision.md` chose live-bridge map authoring over
save-editing on the strength of one number: **2 ms per bridge call**, measured
on a 3-mod, paused game. That number decides the architecture, and it was never
checked against the real 568-mod stack, where Harmony patch depth and a live
tick could plausibly make it 100x worse.

So this script exists to be run TWICE - once per mod tier - and produce numbers
that are directly comparable. Run it, record the JSON, compare.

WHAT IT MEASURES
================
Three classes, because they hit different amounts of game code:

  read       rimbridge/ping, rimworld/get_game_info, rimworld/get_cell_info
             - pure query. Isolates transport + main-thread handoff.
  mutpath    apply_architect_designator with dryRun:true
             - runs placement validation (the expensive part of a real build)
             but commits nothing. Safe on a real colony.
  mutation   apply_architect_designator for real, then a floor over the top
             - ONLY with --real. Leaves marks on the map. Never use this on a
             colony you care about.

Latency is reported as min/median/p90/p99/max, not a mean. A mean hides the
thing that would actually break a generator: a fat tail where one call in fifty
blocks for a frame. 2 ms mean with a 400 ms p99 is not a 2 ms system.

SAFETY
======
Default mode mutates nothing. `--real` does, and says so loudly.
This never calls the `*_debug_action*` discovery tools: on a 562-mod install
they hung the game for 4 minutes and cost a 23-minute reload. See the header of
rimbridge_client.py.

⚠️ LATENCY TRACKS THE COLONY, NOT THE MOD COUNT
===============================================
Measured 2026-08-12: the same five classes read **16.7 ms** on a real 21-colonist
colony at 568 mods and **5.8 ms** on a fresh quicktest at 573 -- both PAUSED,
same bridge version, same probe cell. Main-thread calls queue behind the frame's
real work, so a busy map is slow and a fresh one is not.

That also killed the "16.7 ms is a 60 Hz frame lock" theory: at 568 all three
main-thread classes agreed to three decimals (16.656 / 16.673 / 16.708), which
looked like a hard gate and was actually three calls queued behind one busy
frame. At 573 they separate to 5.7 / 19.7 / 21.0.

So **name the colony in --label**, and compare two reports only when their
workload matches. The `workload` block in the output records colonist and pawn
counts for exactly this reason.

USAGE
=====
    python src/RimMandrake/Utils/bridge_latency.py                       # safe, 200 samples
    python src/RimMandrake/Utils/bridge_latency.py -n 500 --label 568mod-jawa21
    python src/RimMandrake/Utils/bridge_latency.py --real --label 3mod-quicktest  # real builds
    python src/RimMandrake/Utils/bridge_latency.py --label 573mod-quicktest \
        --out observed/2026-08-13/latency_573mod.json
"""

import argparse
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rimbridge_client import RimBridge, RimBridgeError, resolve_endpoint  # noqa: E402


def percentile(sorted_vals, pct):
    """Nearest-rank percentile. No interpolation - with n>=100 it does not
    matter, and nearest-rank never invents a latency that was not observed."""
    if not sorted_vals:
        return None
    k = max(0, min(len(sorted_vals) - 1,
                   int(round(pct / 100.0 * len(sorted_vals) + 0.5)) - 1))
    return sorted_vals[k]


def summarise(name, samples_ms):
    s = sorted(samples_ms)
    return {
        "name": name,
        "n": len(s),
        "min_ms": round(s[0], 3),
        "median_ms": round(statistics.median(s), 3),
        "p90_ms": round(percentile(s, 90), 3),
        "p99_ms": round(percentile(s, 99), 3),
        "max_ms": round(s[-1], 3),
        "mean_ms": round(statistics.fmean(s), 3),
    }


def find_designator(rb, category_def_name, id_suffix):
    """Resolve a live architect designator id, e.g. ('Floors','build-concrete')
    -> 'architect-designator:floors:build-concrete'.

    list_architect_designators REQUIRES a categoryId and returns the id scoped
    by category, including dropdown parents. Match on the trailing segment so a
    designator nested under a dropdown still resolves."""
    cats = rb.call("rimworld/list_architect_categories", {}) or []
    if isinstance(cats, dict):
        cats = cats.get("categories", [])
    cat_id = next((c.get("id") for c in cats
                   if c.get("categoryDefName") == category_def_name), None)
    if cat_id is None:
        return None
    listing = rb.call("rimworld/list_architect_designators",
                      {"categoryId": cat_id}) or {}
    for d in listing.get("designators", []):
        if str(d.get("id", "")).rsplit(":", 1)[-1] == id_suffix:
            return d["id"]
    return None


def timed(rb, tool, params):
    """One call, wall-clock around the round trip. Returns (ms, result)."""
    t0 = time.perf_counter()
    out = rb.call(tool, params)
    return (time.perf_counter() - t0) * 1000.0, out


def _workload(rb, tools):
    """How busy is the main thread? THE variable these numbers depend on.

    Measured 2026-08-12: the same five classes at 568 mods on a real
    21-colonist colony and at 573 on a fresh 3-colonist quicktest differed by
    3x on reads -- 16.7 ms against 5.8 ms -- with both runs PAUSED, same bridge
    version, same probe cell. Main-thread calls queue behind the frame's real
    work, so what matters is how much of that there is, not how many mods are
    installed.

    Before this block existed a report recorded `toolCount` and the mod tier and
    nothing about the colony, so two runs that differed 3x looked comparable and
    the reports could not explain their own disagreement. Recording it is what
    makes "16.7 ms" mean something later.

    Everything here is best-effort: a missing field must never fail a bench.
    """
    out = {}
    names = {t.get("name") for t in (tools or [])}
    try:
        cols = rb.call("rimworld/list_colonists", {}) or {}
        lst = cols.get("colonists") or cols.get("pawns") or []
        out["colonistCount"] = len(lst) if isinstance(lst, list) else None
    except Exception as e:
        out["colonistCount"] = "unavailable: %s" % str(e)[:60]

    # Total pawns is the better proxy -- animals and hostiles tick too, and a
    # 3-colonist quicktest can still be crowded.
    if "jawa/list_pawns" in names:
        try:
            lp = rb.call("jawa/list_pawns", {}) or {}
            out["totalPawnsOnMap"] = lp.get("totalOnMap")
        except Exception as e:
            out["totalPawnsOnMap"] = "unavailable: %s" % str(e)[:60]
    else:
        out["totalPawnsOnMap"] = "jawa/list_pawns not registered"

    try:
        gi = rb.call("rimworld/get_game_info", {}) or {}
        out["ticksGame"] = gi.get("ticksGame")
        out["mapCount"] = gi.get("mapCount")
    except Exception:
        pass

    out["NOTE"] = ("Latency tracks main-thread business, NOT mod count. Compare "
                   "two reports only when their workload matches; a quicktest "
                   "map and a real colony are not the same measurement.")
    return out


def run(rb, n, do_real, verbose):
    results = {"classes": [], "context": {}}

    # -- context: what game are we even measuring? -------------------------
    _, info = timed(rb, "rimworld/get_game_info", {})
    _, status = timed(rb, "rimbridge/get_bridge_status", {})
    tools = rb.list_tools()

    results["context"] = {
        "gameInfo": info,
        "paused": (status or {}).get("state", {}).get("paused"),
        "timeSpeed": (status or {}).get("state", {}).get("timeSpeed"),
        "bridgeVersion": (status or {}).get("version", {}).get("bridgeVersion"),
        "sdkVersion": (status or {}).get("version", {}).get("sdkVersion"),
        "companionCount": (status or {}).get("companions", {}).get("totalCount"),
        "toolCount": len(tools),
        "optionalPatchSuccessCount":
            (status or {}).get("patches", {}).get("optionalPatchSuccessCount"),
        "workload": _workload(rb, tools),
    }

    # A cell we can safely probe: the map centre is always in bounds.
    size = None
    for key in ("mapSize", "size", "currentMapSize"):
        if isinstance(info, dict) and key in info:
            size = info[key]
            break
    cx = cz = 125
    if isinstance(size, dict):
        cx = int(size.get("x", 250)) // 2
        cz = int(size.get("z", size.get("y", 250))) // 2
    elif isinstance(size, (list, tuple)) and len(size) >= 2:
        cx, cz = int(size[0]) // 2, int(size[-1]) // 2
    results["context"]["probeCell"] = {"x": cx, "z": cz}

    # -- warm-up: never measure the first call of anything -----------------
    # JIT, lazy tool resolution and the first main-thread handoff all land on
    # call #1 and would otherwise show up as the max.
    for _ in range(10):
        rb.call("rimbridge/ping", {})
        rb.call("rimworld/get_cell_info", {"x": cx, "z": cz})

    # -- read classes ------------------------------------------------------
    reads = [
        ("read: rimbridge/ping", "rimbridge/ping", {}),
        ("read: get_game_info", "rimworld/get_game_info", {}),
        ("read: get_cell_info", "rimworld/get_cell_info", {"x": cx, "z": cz}),
    ]
    for label, tool, params in reads:
        samples = []
        for _ in range(n):
            ms, _out = timed(rb, tool, params)
            samples.append(ms)
        results["classes"].append(summarise(label, samples))
        if verbose:
            print("  %-28s median %.3f ms" % (label, results["classes"][-1]["median_ms"]))

    # -- mutation-path (dryRun) -------------------------------------------
    # dryRun runs the full placement validation - footprint, clearance,
    # terrain, reachability - and commits nothing. It is the honest proxy for
    # what a generator's calls actually cost.
    #
    # designatorId is a scoped UI path, NOT a defName: 'Floor_Concrete' is
    # rejected, 'architect-designator:floors:build-concrete' works. Those paths
    # are built from the live architect menu, so they shift as mods add
    # entries - discover it every run rather than hardcoding one tier's answer.
    designator_id = find_designator(rb, "Floors", "build-concrete")
    results["context"]["designatorId"] = designator_id
    if designator_id is None:
        results["classes"].append({"name": "mutpath: designator dryRun",
                                   "skipped": "no concrete floor designator found"})
        return results

    dry_params = {"designatorId": designator_id, "x": cx, "z": cz,
                  "width": 1, "height": 1, "dryRun": True}
    ok_ms, probe = timed(rb, "rimworld/apply_architect_designator", dry_params)
    if isinstance(probe, dict) and probe.get("success") is not False:
        samples = [ok_ms]
        for _ in range(n - 1):
            ms, _out = timed(rb, "rimworld/apply_architect_designator", dry_params)
            samples.append(ms)
        results["classes"].append(summarise("mutpath: designator dryRun", samples))
        if verbose:
            print("  %-28s median %.3f ms" % ("mutpath: dryRun",
                                              results["classes"][-1]["median_ms"]))
    else:
        results["classes"].append({"name": "mutpath: designator dryRun",
                                   "skipped": "probe call did not succeed",
                                   "probe": probe})

    # -- companion: jawa/set_terrain ---------------------------------------
    # The whole point of measuring on the full stack is to decide whether live
    # map authoring stays viable, and terrain painting is the primitive that
    # authoring is actually built on. Measure the thing we will use.
    #
    # Safety: this paints ONE cell, alternating between two terrains so the
    # real write path is exercised rather than a no-op, then puts the original
    # terrain back. On a real colony that is a single cell, restored.
    tool_names = {t.get("name") for t in tools}
    if "jawa/set_terrain" in tool_names:
        original = ((rb.call("rimworld/get_cell_info", {"x": cx, "z": cz}) or {})
                    .get("cell") or {}).get("terrainDefName")
        results["context"]["terrainBenchCell"] = {"x": cx, "z": cz, "original": original}
        flip = ["Sand", "Gravel"]
        samples = []
        try:
            for i in range(n):
                ms, _out = timed(rb, "jawa/set_terrain",
                                 {"x": cx, "z": cz, "terrainDef": flip[i % 2]})
                samples.append(ms)
            results["classes"].append(summarise("companion: jawa/set_terrain", samples))
            if verbose:
                print("  %-28s median %.3f ms" % ("companion: set_terrain",
                                                  results["classes"][-1]["median_ms"]))
        finally:
            if original:
                rb.call("jawa/set_terrain", {"x": cx, "z": cz, "terrainDef": original})
                back = ((rb.call("rimworld/get_cell_info", {"x": cx, "z": cz}) or {})
                        .get("cell") or {}).get("terrainDefName")
                results["context"]["terrainBenchRestored"] = (back == original)
                if verbose and back != original:
                    print("  !! probe cell left as %s, expected %s" % (back, original))
    else:
        results["context"]["terrainBenchCell"] = "jawa/set_terrain not registered"

    # -- real mutation -----------------------------------------------------
    if do_real:
        # Paint a 1x1 concrete floor, walking across a strip so each call is a
        # genuinely new placement rather than a no-op on an already-floored cell.
        samples = []
        for i in range(n):
            ms, _out = timed(rb, "rimworld/apply_architect_designator",
                             {"designatorId": designator_id,
                              "x": cx + (i % 20) - 10, "z": cz + (i // 20) % 20 - 10,
                              "width": 1, "height": 1})
            samples.append(ms)
        results["classes"].append(summarise("mutation: designator real", samples))
        if verbose:
            print("  %-28s median %.3f ms" % ("mutation: real",
                                              results["classes"][-1]["median_ms"]))

    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", "--samples", type=int, default=200)
    ap.add_argument("--label", default="unlabelled",
                    help="what is being measured. Name the COLONY, not just the "
                         "mod tier: '573mod-quicktest' or '568mod-jawa21'. "
                         "Latency tracks main-thread business, and a quicktest "
                         "map reads 3x faster than a real colony at the same "
                         "mod count.")
    ap.add_argument("--real", action="store_true",
                    help="ALSO time real (committing) mutations - marks the map")
    ap.add_argument("--out", help="write the JSON report here")
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    host, port, token = resolve_endpoint()
    if not token:
        print("no bridge token in Player.log - is RimWorld up?", file=sys.stderr)
        return 2

    if args.real:
        print("*** --real WILL PERMANENTLY MARK THE LIVE MAP (concrete floors) ***")

    if not args.quiet:
        print("measuring %s, n=%d per class, %s:%s" % (args.label, args.samples,
                                                       host, port))
    try:
        with RimBridge(host, port, token, timeout=args.timeout) as rb:
            t0 = time.perf_counter()
            report = run(rb, args.samples, args.real, not args.quiet)
            report["label"] = args.label
            report["samplesPerClass"] = args.samples
            report["wallClockSeconds"] = round(time.perf_counter() - t0, 2)
    except RimBridgeError as ex:
        print("bridge error: %s" % ex, file=sys.stderr)
        return 1

    # A report that cannot say which colony it measured is not comparable to
    # any other report. Say so at the end, where it will actually be read.
    wl = (report.get("context") or {}).get("workload") or {}
    if not args.quiet:
        print("\nworkload: colonists=%s totalPawns=%s paused=%s"
              % (wl.get("colonistCount"), wl.get("totalPawnsOnMap"),
                 (report.get("context") or {}).get("paused")))
        if args.label == "unlabelled":
            print("*** UNLABELLED. Re-run with --label naming the colony "
                  "(e.g. 573mod-quicktest);")
            print("    otherwise this file cannot be compared with any other.")

    text = json.dumps(report, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        if not args.quiet:
            print("wrote %s" % os.path.abspath(args.out))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
