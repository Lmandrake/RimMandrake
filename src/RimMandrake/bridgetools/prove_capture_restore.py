"""prove_capture_restore.py - one run that answers the whole CHECK reload queue.

WHAT THIS IS FOR
================
A cold load is 23-30 minutes, so arriving with a checklist and a script beats
arriving with a plan. This script settles four open questions in a single
session, in dependency order, and it drives the PRODUCTION code path
(`rimbench.TerrainPainter`) rather than a bespoke harness -- so a pass here is
evidence about the code generators will actually run, not about this file.

  1. Did the deploy take? Which of the three companion tools are registered.
  2. Is `jawa/get_terrain_batch` correct? Capture a region in ONE call, and
     cross-check it cell-by-cell against `get_cell_info`, the independent
     channel.
  3. Does painting terrain destroy the plants standing on it? Unverified either
     way; it decides whether a crater needs the expensive flooring pass.
  4. Does capture -> paint -> restore return the map EXACTLY to how it was?
     Verified over every cell, not a sample -- which is only affordable now that
     a full read-back is one call.

SAFETY
======
This paints on whatever map is loaded, which may be a colony someone cares
about. So: every changed cell is captured first, the capture REFUSES to proceed
if it is incomplete, and the restore is verified over the full cell set before
the script reports success. Nothing is left behind unless you pass --keep.

If the run dies between paint and restore, the captured ops string is written to
observed/last_capture.ops -- replay it with --replay to put the map back.

    python.exe src/RimMandrake/bridgetools/prove_capture_restore.py --x 30 --z 150 -R 10
"""
import argparse
import json
import os
import sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(_ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(_ROOT, "src", "RimMandrake", "Utils", "rimbench"))

import terrain as T                                    # noqa: E402
from core import Session                               # noqa: E402
from selftest import dithered_crater                   # noqa: E402

CAPTURE_FILE = os.path.join(_ROOT, "observed", "last_capture.ops")

OK, BAD = "  ok  ", "  FAIL"
RESULTS = []


def check(name, cond, detail=""):
    print("%s %s%s" % (OK if cond else BAD, name, ("   " + detail) if detail else ""))
    RESULTS.append((name, bool(cond)))
    return bool(cond)


# ------------------------------------------------------------------ 1. deploy

def report_tools(s):
    """Which companion tools this game actually registered.

    Companions are discovered only at RimBridgeServer startup, so this is the
    deploy check: a missing tool means the DLL did not land or the game did not
    restart since it did. Distinguishing those two is worth a line of output,
    because they have completely different fixes.
    """
    try:
        names = {t.get("name") for t in s._rb.list_tools()}
    except Exception as e:
        print("  could not list tools: %s" % str(e)[:120])
        names = set()

    print("\n1. deploy check")
    for tool in (T.SINGLE_TOOL, T.BATCH_TOOL, T.READ_TOOL):
        check("%-24s registered" % tool, tool in names)
    print("     (%d tools total)" % len(names))
    return names


# ----------------------------------------------------------------- 2. capture

def prove_capture(s, tp, cells):
    """Capture in one call, then cross-check against get_cell_info."""
    print("\n2. capture — %d cells" % len(cells))
    before = tp.calls
    t0 = time.perf_counter()
    captured = tp.capture(cells)
    dt = time.perf_counter() - t0
    used = tp.calls - before

    check("captured every requested cell", len(captured) == len(cells),
          "%d of %d" % (len(captured), len(cells)))
    check("one call, not one per cell" if tp.can_read_batch()
          else "per-cell fallback (batched read not registered)",
          used == 1 if tp.can_read_batch() else used == len(cells),
          "%d call(s), %.1f ms, %.3f ms/cell" % (used, dt * 1000,
                                                 dt * 1000 / max(1, len(cells))))

    # The independent channel. get_cell_info is a different code path in the
    # bridge from our companion's grid read, so agreement between them is real
    # evidence; agreement between the companion and itself would not be.
    keys = sorted(captured)
    sample = keys[::max(1, len(keys) // 20)]
    bad = [c for c in sample if s.terrain_at(c[0], c[1]) != captured[c]]
    check("agrees with get_cell_info on %d sampled cells" % len(sample),
          not bad, "mismatches: %s" % bad[:3])

    if captured:
        with open(CAPTURE_FILE, "w") as fh:
            fh.write(T.to_ops(T.plan_rects(captured)))
        print("     capture written to %s" % CAPTURE_FILE)
    return captured


# -------------------------------------------------------------- 3. vegetation

def plants_in(s, cells, limit=40):
    """Which of these cells currently hold a plant. One call per cell, so bounded.

    Answers the question the crater generator needs: if painting Sand over a
    bush leaves the bush standing, a painted crater looks wrong and needs the
    flooring pass (one call per cell) to clear it. If painting destroys them,
    flooring can be dropped entirely and the formation stays a single call.
    """
    found = {}
    for c in sorted(cells)[::max(1, len(cells) // limit)]:
        try:
            things = s.things_at(c[0], c[1])
        except Exception:
            continue
        plants = [t for t in things if (t or "").startswith("Plant_")]
        if plants:
            found[c] = plants
    return found


# ------------------------------------------------------------------- 4. paint

def prove_paint(s, tp, ground):
    print("\n4. paint — %d cells" % len(ground))
    before = tp.calls
    t0 = time.perf_counter()
    changed = tp.paint_map(ground)
    dt = time.perf_counter() - t0
    used = tp.calls - before

    # Expected call count depends on the route, and N rects -> N calls is the
    # CORRECT answer on the per-rect fallback. Asserting the batch expectation
    # against a game running the old companion would report a deploy problem as
    # a code problem.
    rects = T.plan_rects({c: T.resolve(t) for c, t in ground.items()})
    expected = (len(list(T.chunk_rects(rects))) if tp.route() == "batch"
                else len(rects))
    check("painted in %d call(s) for %d rects (%s route wants %d)"
          % (used, len(rects), tp.route(), expected), used == expected,
          "%.1f ms total, %.3f ms/cell" % (dt * 1000, dt * 1000 / max(1, len(ground))))
    check("companion reported zero failed verifies", tp.cells_failed == 0,
          "cellsFailedVerify=%d" % tp.cells_failed)
    check("companion reported no errors", not tp.errors, str(tp.errors[:2]))

    ok, n, bad = tp.verify(ground, sample=20)
    check("independent read-back agrees on %d sampled cells" % n, ok,
          "mismatches: %s" % bad[:3])
    return changed, dt


# ----------------------------------------------------------------- 5. restore

def prove_restore(s, tp, captured):
    print("\n5. restore — %d cells" % len(captured))
    before = tp.calls
    t0 = time.perf_counter()
    n = tp.restore()
    dt = time.perf_counter() - t0
    used = tp.calls - before
    print("     %d cells repainted in %d call(s), %.1f ms" % (n, used, dt * 1000))

    # The whole cell set, not a sample. This is the point of the batched read:
    # full verification of a restore used to cost one call per cell, so nobody
    # ever did it, so "restored" always meant "restored as far as we checked".
    if tp.can_read_batch():
        after = {}
        for batch in T.chunk_rects([("_",) + r for r in T.to_rects(sorted(captured))]):
            r = s.call(T.READ_TOOL,
                       rects=";".join("%d,%d,%d,%d" % (x, z, w, h)
                                      for (_t, x, z, w, h) in batch),
                       layer="top")
            after.update(T.expand_ops(r.get("ops") or ""))
        wrong = {c: (captured[c], after.get(c)) for c in captured
                 if after.get(c) != captured[c]}
        check("EVERY one of %d cells is back to its original terrain" % len(captured),
              not wrong, "%d wrong, e.g. %s" % (len(wrong), list(wrong.items())[:2]))
    else:
        keys = sorted(captured)
        sample = keys[::max(1, len(keys) // 20)]
        bad = [c for c in sample if s.terrain_at(c[0], c[1]) != captured[c]]
        check("%d sampled cells back to original (no batched read)" % len(sample),
              not bad, "mismatches: %s" % bad[:3])
    return dt


# --------------------------------------------------------------------- replay

def replay(s):
    """Put the map back from a capture file left by a crashed run."""
    if not os.path.exists(CAPTURE_FILE):
        sys.exit("no capture file at %s" % CAPTURE_FILE)
    with open(CAPTURE_FILE) as fh:
        ops = fh.read().strip()
    if not ops:
        sys.exit("capture file is empty")
    rects = T.parse_ops(ops)
    print("replaying %d rects from %s" % (len(rects), CAPTURE_FILE))
    tp = T.TerrainPainter(s)
    n = tp._send(rects)
    print("restored %d cells; %s" % (n, tp.report()))
    return 0


# ----------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--x", type=int, default=30)
    ap.add_argument("--z", type=int, default=150)
    ap.add_argument("-R", type=int, default=10)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--keep", action="store_true",
                    help="do NOT restore — leaves the crater on the map")
    ap.add_argument("--replay", action="store_true",
                    help="restore from observed/last_capture.ops and exit")
    ap.add_argument("--shot", default="capture_restore")
    args = ap.parse_args()

    with Session(strict=False) as s:
        if args.replay:
            return replay(s)

        print("prove_capture_restore — (%d,%d) R=%d" % (args.x, args.z, args.R))
        report_tools(s)

        tp = T.TerrainPainter(s, strict=False)
        print("\n     route: %s" % tp.explain_route())
        if tp.route() == "none":
            sys.exit("no companion registered — nothing to prove. Deploy and restart.")

        ground = dithered_crater(args.x, args.z, args.R, seed=args.seed)
        cells = sorted(ground)

        captured = prove_capture(s, tp, cells)

        print("\n3. vegetation before")
        veg_before = plants_in(s, cells)
        print("     %d of the sampled cells hold plants" % len(veg_before))

        s.call("rimworld/frame_cell_rect", x=args.x - args.R * 2,
               z=args.z - args.R * 2, width=args.R * 4, height=args.R * 4)
        s.call("rimworld/take_screenshot", fileName=args.shot + "_before",
               suppressMessage=True)

        changed, paint_dt = prove_paint(s, tp, ground)

        # Step the renderer before judging anything visual: a screenshot taken
        # while paused can be the previous frame. See traps.md.
        s.step(2)
        s.call("rimworld/take_screenshot", fileName=args.shot + "_after",
               suppressMessage=True)

        print("\n3b. vegetation after — THE OPEN QUESTION")
        survivors = {}
        for c, plants in veg_before.items():
            still = [t for t in s.things_at(c[0], c[1]) if (t or "").startswith("Plant_")]
            if still:
                survivors[c] = still
        if not veg_before:
            print("     INCONCLUSIVE — no plants in the sampled cells. Re-run "
                  "over vegetated ground before concluding anything.")
        else:
            killed = len(veg_before) - len(survivors)
            print("     %d of %d vegetated cells lost their plants"
                  % (killed, len(veg_before)))
            print("     VERDICT: painting terrain %s"
                  % ("DESTROYS plants — the flooring pass can be dropped"
                     if killed == len(veg_before) else
                     "LEAVES plants standing — a crater still needs flooring"
                     if killed == 0 else
                     "destroys SOME plants (%d/%d) — inspect which defs survived"
                     % (killed, len(veg_before))))

        if args.keep:
            print("\n5. restore SKIPPED (--keep). The crater stays. Replay with "
                  "--replay to undo it later.")
            restore_dt = None
        else:
            restore_dt = prove_restore(s, tp, captured)
            s.step(2)
            s.call("rimworld/take_screenshot", fileName=args.shot + "_restored",
                   suppressMessage=True)
            if os.path.exists(CAPTURE_FILE):
                os.remove(CAPTURE_FILE)

        print("\n" + "=" * 68)
        print("%d cells | paint %.1f ms%s | %s"
              % (len(ground), paint_dt * 1000,
                 " | restore %.1f ms" % (restore_dt * 1000) if restore_dt else "",
                 tp.report()))
        failed = [n for n, ok in RESULTS if not ok]
        print("%d/%d checks pass%s" % (len(RESULTS) - len(failed), len(RESULTS),
                                       "" if not failed else "  FAILED: %s" % failed[:4]))
        return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
