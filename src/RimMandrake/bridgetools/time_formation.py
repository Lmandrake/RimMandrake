"""time_formation.py - time a REAL formation end to end, generator -> bridge -> map.

WHAT THIS ANSWERS
=================
`design/RimMandrake/map_authoring_decision.md` step 3: "time a real formation end to end and
compare against save-edit + reload of the same result." Everything measured
before this was a synthetic probe -- a single cell, or one hand-picked 6x6 rect.
A generator does neither. It produces a few hundred cells of irregular, dithered,
multi-terrain shape, and the open question is what THAT costs once it is
decomposed into the rect batches the bridge is fast at.

THE FORMATION
=============
An impact crater in terrain: four concentric zones with dithered boundaries and
an elliptical squash, so it does not read as a bullseye. The noise is a hash of
(x, z, seed), so the same seed paints the same crater and a re-run is idempotent
rather than additive. Zone logic and the `noise` hash are reused from
`src/RimMandrake/Utils/rimbench/crater.py`, which paints filth over the same shape -- same
generator, different output layer.

WHY THE SHAPE MATTERS TO THE MEASUREMENT
========================================
A dithered ellipse is close to the worst realistic case for rect packing: the
boundary interlocks deliberately, so the decomposer cannot return a few fat
rectangles the way a plain disc would. If batching still wins here, it wins.

REVERSIBILITY
=============
Every changed cell's original terrain is read back BEFORE painting and restored
afterwards through the same rect machinery. That is a real test of the
reversibility claim the whole decision rests on, not just politeness toward a
live colony: the revert is timed too, because "the player just reloads" is only
the fallback -- an authoring tool should be able to undo itself.

Nothing here trusts `success: true`. Painted cells are verified by independent
`get_cell_info` read-back, and the restore is verified the same way.
"""
import argparse
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "Utils"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "Utils", "rimbench"))
from rimbridge_client import RimBridge, resolve_endpoint
from crater import noise            # same deterministic hash the filth crater uses
# Rect decomposition and ops encoding live in the generator library, not here.
# One implementation, proven offline by src/RimMandrake/Utils/rimbench/selftest.py — a timing
# harness measuring its own private copy of the encoder would measure the wrong
# thing the moment the two drifted.
from terrain import parse_ops, plan_rects, to_ops as rects_to_ops, to_rects

# Four zones, outermost last. Vanilla Core terrain only, so this runs on any
# mod tier -- the 3-mod bench and the 568-mod campaign alike.
MELT, BOWL, RIM, EJECTA = "Sand", "Gravel", "Soil", "Gravel"


def terrain_at(rb, x, z):
    """Read one cell's terrain defName.

    The payload is {"cell": {"terrainDefName": ...}} -- NOT {"terrain": ...}.
    Getting this wrong returns None for every cell, which then paints
    `terrainDef: None` on the revert (a silent no-op) while a None==None
    comparison reports the restore as clean. It cost a whole run.
    """
    r = rb.call("rimworld/get_cell_info", {"x": x, "z": z})
    cell = r.get("cell") or {}
    return cell.get("terrainDefName")


def plan_crater(cx, cz, R=12, seed=7, squash=0.82, ray_dir=0.6):
    """Return {(x, z): terrainDefName} for one crater. No bridge calls."""
    cells = {}
    span = int(R * 1.7) + 1
    for dx in range(-span, span + 1):
        for dz in range(-span, span + 1):
            x, z = cx + dx, cz + dz
            ex, ez = dx, dz / squash
            d = math.sqrt(ex * ex + ez * ez) / R
            n = noise(x, z, seed)
            d += (n - 0.5) * 0.18                      # interlock the edges
            ang = math.atan2(dz, dx)
            ray = 0.5 + 0.5 * math.cos((ang - ray_dir) * 3.0)
            if d < 0.30:
                cells[(x, z)] = MELT
            elif d < 0.65:
                cells[(x, z)] = BOWL
            elif d < 1.00:
                cells[(x, z)] = RIM
            elif d < 1.45:
                fade = (1.45 - d) / 0.45
                if n < 0.42 * fade * ray:              # sparse, rayed ejecta
                    cells[(x, z)] = EJECTA
    return cells


def paint(rb, cells, label, defer_refresh=False):
    """Paint {cell: terrain} as rects. Returns (seconds, rects, reported).

    ⚠️ `defer_refresh` IS NOT SAFE, and is kept only to reproduce the historical
    measurement. It passes refresh=False on every call but the last, on the
    theory that one mesh rebuild is cheaper than 115. It is not equivalent:
    `RefreshRect` in the companion dirties only the cells of the rect it was
    given, and the map mesh is cached in 17x17 sections. A radius-12 crater
    spans about 3x3 sections, so refreshing on the LAST rect alone dirties one
    section and leaves the other eight stale -- correct in the terrain grid and
    visibly unpainted on screen until something else happens to dirty them.

    That makes the 12.59 ms/cell figure this flag produced an under-refreshed
    measurement. **The honest per-rect baseline is 13.99 ms/cell** (~5,750 ms
    for 411 cells), which is what `jawa/set_terrain_batch` should be compared
    against -- the batch tool collects every changed cell in a HashSet and
    flushes it once, so it refreshes CORRECTLY and completely.

    Doing deferred refresh properly needs a companion tool that dirties an
    arbitrary rect without painting it (`jawa/refresh_rect`). Until that exists,
    leave this flag off.
    """
    batches = plan_rects(cells)

    changed = failed = 0
    t0 = time.perf_counter()
    for i, (terr, x, z, w, h) in enumerate(batches):
        args = {"x": x, "z": z, "terrainDef": terr, "width": w, "height": h}
        if defer_refresh:
            args["refresh"] = (i == len(batches) - 1)
        r = rb.call("jawa/set_terrain", args)
        changed += r.get("cellsChanged", 0)
        failed += r.get("cellsFailedVerify", 0)
    dt = time.perf_counter() - t0

    print("  %-8s %5d cells -> %4d rects (%.1f cells/rect)  %8.1f ms  "
          "%.2f ms/cell   changed=%d failedVerify=%d"
          % (label, len(cells), len(batches), len(cells) / float(len(batches)),
             dt * 1000, dt * 1000 / len(cells), changed, failed))
    return dt, len(batches), changed, failed


def to_ops(cells):
    """Encode {cell: terrain} as the batch tool's ops string. -> (ops, nrects)"""
    rects = plan_rects(cells)
    return rects_to_ops(rects), len(rects)


def paint_batch(rb, cells, label):
    """Paint the whole formation in ONE call. Returns (seconds, rects, changed)."""
    ops, nrects = to_ops(cells)
    t0 = time.perf_counter()
    r = rb.call("jawa/set_terrain_batch", {"ops": ops})
    dt = time.perf_counter() - t0
    changed = r.get("cellsChanged", 0)
    failed = r.get("cellsFailedVerify", 0)
    errs = r.get("errors") or []
    print("  %-8s %5d cells -> %4d rects in ONE call        %8.1f ms  "
          "%.2f ms/cell   changed=%d failedVerify=%d%s"
          % (label, len(cells), nrects, dt * 1000, dt * 1000 / len(cells),
             changed, failed, "" if not errs else "  errors=%s" % errs[:2]))
    return dt, nrects, changed, failed


def has_batch_tool(rb):
    try:
        return any(t.get("name") == "jawa/set_terrain_batch" for t in rb.list_tools())
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--x", type=int, default=60)
    ap.add_argument("--z", type=int, default=60)
    ap.add_argument("-R", type=int, default=12)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--keep", action="store_true",
                    help="do NOT restore the original terrain")
    ap.add_argument("--defer-refresh", action="store_true",
                    dest="defer_refresh",
                    help="refresh the map mesh once at the end, not per rect")
    ap.add_argument("--mode", choices=["rects", "batch", "both"], default="both",
                    help="rects = one call per rect (the old path); batch = one call "
                         "for the whole formation; both = measure each and compare")
    ap.add_argument("--shot", default="formation")
    args = ap.parse_args()

    cells = plan_crater(args.x, args.z, R=args.R, seed=args.seed)
    rects = to_rects(set(cells))
    print("formation: crater R=%d at (%d,%d), %d cells, %d rects if single-terrain"
          % (args.R, args.x, args.z, len(cells), len(rects)))

    host, port, token = resolve_endpoint()
    with RimBridge(host, port, token, timeout=60) as rb:
        # --- capture originals, so the revert is exact ---------------------
        # Capture used to dominate this whole script: 413 cells at one
        # get_cell_info each was 6.09 s, against 19 ms to paint them. Measured
        # 2026-08-12 -- and that imbalance is exactly why jawa/get_terrain_batch
        # exists. Fall back to per-cell only if the companion predates it.
        t0 = time.perf_counter()
        originals = {}
        if any(t.get("name") == "jawa/get_terrain_batch" for t in rb.list_tools()):
            rects = to_rects(set(cells))
            r = rb.call("jawa/get_terrain_batch",
                        {"rects": ";".join("%d,%d,%d,%d" % q for q in rects)})
            for (t, x, z, w, h) in parse_ops(r.get("ops") or ""):
                for dx in range(w):
                    for dz in range(h):
                        originals[(x + dx, z + dz)] = t
            originals = {c: originals.get(c) for c in cells}
        else:
            for (x, z) in sorted(cells):
                originals[(x, z)] = terrain_at(rb, x, z)
        if any(v is None for v in originals.values()):
            raise SystemExit(
                "read-back returned None for some cells -- refusing to paint. "
                "An exact revert is impossible without the originals, and a "
                "None here silently becomes a no-op revert.")
        read_dt = time.perf_counter() - t0
        kinds = {}
        for t in originals.values():
            kinds[t] = kinds.get(t, 0) + 1
        print("  capture  %5d cells read back  %8.1f ms  %.2f ms/cell  "
              "(%d distinct terrains)"
              % (len(originals), read_dt * 1000,
                 read_dt * 1000 / len(originals), len(kinds)))
        top = sorted(kinds.items(), key=lambda kv: -kv[1])[:4]
        print("           originals: %s" % ", ".join("%s x%d" % kv for kv in top))

        # --- paint --------------------------------------------------------
        batch_ok = has_batch_tool(rb)
        mode = args.mode
        if mode in ("batch", "both") and not batch_ok:
            print("  NOTE     jawa/set_terrain_batch is NOT registered -- the companion "
                  "predates it, or the game has not restarted since deploy. Falling "
                  "back to per-rect only.")
            mode = "rects"

        batch_dt = None
        paint_dt, nrects, changed, failed = paint(rb, cells, "PAINT",
                                          defer_refresh=args.defer_refresh)
        if mode in ("batch", "both"):
            # Revert first so the batch run starts from the same ground the
            # per-rect run did; otherwise every cell is already correct and the
            # batch time is measured against a no-op.
            paint(rb, originals, "restore", defer_refresh=True)
            batch_dt, brects, bchanged, bfailed = paint_batch(rb, cells, "BATCH")

        # --- verify independently ------------------------------------------
        sample = sorted(cells)[::max(1, len(cells) // 12)]
        ok = sum(1 for (x, z) in sample if terrain_at(rb, x, z) == cells[(x, z)])
        print("  verify   %d/%d sampled cells hold the painted terrain"
              % (ok, len(sample)))

        rb.call("rimworld/frame_cell_rect",
                {"x": args.x - args.R * 2, "z": args.z - args.R * 2,
                 "width": args.R * 4, "height": args.R * 4})
        rb.call("rimworld/take_screenshot",
                {"fileName": args.shot, "suppressMessage": True})
        print("  shot     %s.png" % args.shot)

        # --- revert ---------------------------------------------------------
        if args.keep:
            print("  revert   SKIPPED (--keep)")
            revert_dt = None
        else:
            revert_dt, _, _, rfail = paint(rb, originals, "REVERT",
                                           defer_refresh=args.defer_refresh)
            bad = [c for c in sample
                   if terrain_at(rb, c[0], c[1]) != originals[c]]
            print("  restored %d/%d sampled cells back to original%s"
                  % (len(sample) - len(bad), len(sample),
                     "" if not bad else "  !! %s" % bad[:3]))

    # --- the comparison the decision doc actually asked for -----------------
    n = len(cells)
    per_cell = paint_dt * 1000 / n
    unbatched = n * 16.7 / 1000.0
    print("\n  %d cells painted in %.2f s  (%.2f ms/cell)" % (n, paint_dt, per_cell))
    print("  same cells one-at-a-time would cost ~%.1f s at the 16.7 ms floor "
          "-> per-rect batching wins %.1fx" % (unbatched, unbatched / paint_dt))
    if batch_dt:
        print("  ONE-CALL batch: %.3f s (%.2f ms/cell)" % (batch_dt, batch_dt * 1000 / n))
        print("  batch vs per-rect: %.0fx faster   batch vs one-at-a-time: %.0fx faster"
              % (paint_dt / batch_dt, unbatched / batch_dt))
    if revert_dt:
        print("  full round trip, paint + exact revert: %.2f s" % (paint_dt + revert_dt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
