"""frame_lock_probe.py - is the bridge latency floor the RENDER FRAME, or a fixed tick?

THE QUESTION
============
On the 568-mod stack every main-thread bridge call bottoms out at ~16.66 ms, and
`rimbridge/ping` -- the one call that never hops the main thread -- does not.
16.66 ms is exactly one frame at 60 Hz, which suggests a call waits for a frame
boundary. But every sample so far was taken AT 60 FPS, so "60 Hz" and "16.66 ms"
merely agree; neither is evidence for the other.

Two hypotheses that fit the data identically at 60 FPS:

  RENDER-FRAME   the call waits for the next rendered frame.
                 -> at 34 FPS the floor should rise to ~29 ms.
                 -> uncapping the frame rate would make every hop cheaper.

  FIXED-TICK     the bridge pumps its queue on a fixed 60 Hz timer.
                 -> the floor stays ~16.66 ms no matter what the frame rate does.
                 -> uncapping the frame rate buys nothing.

They differ only when the frame rate differs, so this script changes the frame
rate and re-measures.

HOW IT LOWERS FPS
=================
By zooming the camera out. That raises render cost only -- the game stays
paused, so tick work, mod count and Harmony depth are all held constant. This is
the cleanest single-variable lever available over the bridge.

WHY IT READS FPS OFF A SCREENSHOT
=================================
The frame rate has to be measured, not assumed, and it must not be inferred from
the latency we are trying to explain -- that would assume the conclusion. So at
each zoom level it captures the game's own FPS counter and the caller reads it.

Leaves nothing behind: the camera is restored, and no game state is touched.
"""
import argparse
import os
import statistics as st
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rimbridge_client import RimBridge, resolve_endpoint

# RimWorld's CameraZoomRange, closest -> furthest.
ZOOMS = ["Closest", "Close", "Middle", "Far", "Furthest"]


def measure(rb, x, z, n, warmup=10):
    """Median/min round trip for a main-thread read, in ms."""
    for _ in range(warmup):
        rb.call("rimworld/get_cell_info", {"x": x, "z": z})
    xs = []
    for _ in range(n):
        t0 = time.perf_counter()
        rb.call("rimworld/get_cell_info", {"x": x, "z": z})
        xs.append((time.perf_counter() - t0) * 1000.0)
    xs.sort()
    return {
        "n": n,
        "min_ms": round(xs[0], 3),
        "median_ms": round(st.median(xs), 3),
        "p90_ms": round(xs[int(0.9 * (len(xs) - 1))], 3),
        "max_ms": round(xs[-1], 3),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-n", type=int, default=80, help="samples per zoom level")
    ap.add_argument("--x", type=int, default=125)
    ap.add_argument("--z", type=int, default=125)
    ap.add_argument("--shots", default="framelock",
                    help="screenshot basename; one per zoom level")
    args = ap.parse_args()

    host, port, token = resolve_endpoint()
    print("frame-lock probe on %s:%s, n=%d per zoom level" % (host, port, args.n))

    rows = []
    # ONE CONNECTION PER ZOOM LEVEL, deliberately. A timed-out call leaves its
    # late response sitting in the socket, and the next call reads that instead
    # of its own -- "unexpected response id", after which every later number is
    # suspect. A fresh socket per level contains a stall to the level that
    # caused it. Cost is one connect per level; the alternative is silent
    # cross-contamination of the whole run.
    for zoom in ZOOMS:
        try:
            with RimBridge(host, port, token) as rb:
                rb.call("rimworld/jump_camera_to_cell",
                        {"x": args.x, "z": args.z})
                rb.call("rimworld/set_camera_zoom", {"zoom": zoom})
                # let the renderer settle at the new zoom before timing it
                time.sleep(0.6)
                r = measure(rb, args.x, args.z, args.n)
                shot = "%s-%s" % (args.shots, zoom.lower())
                rb.call("rimworld/take_screenshot",
                        {"fileName": shot, "suppressMessage": True})
        except Exception as ex:
            print("  %-9s SKIPPED (%s)" % (zoom, str(ex)[:70]))
            continue
        r["zoom"] = zoom
        r["screenshot"] = shot + ".png"
        rows.append(r)
        print("  %-9s min %6.2f  median %6.2f  p90 %6.2f  max %7.2f   -> %s"
              % (zoom, r["min_ms"], r["median_ms"], r["p90_ms"],
                 r["max_ms"], r["screenshot"]))

    # leave the view as we found it
    try:
        with RimBridge(host, port, token) as rb:
            rb.call("rimworld/set_camera_zoom", {"zoom": "Middle"})
    except Exception:
        pass

    if not rows:
        print("no zoom levels measured; is rimworld/set_camera_zoom available?")
        return 1

    meds = [r["median_ms"] for r in rows]
    spread = max(meds) - min(meds)
    print("\nmedian spread across zoom levels: %.2f ms" % spread)
    print("Read the FPS counter off each screenshot before concluding.")
    print("  medians track FPS   -> RENDER-FRAME: uncapping the frame rate helps")
    print("  medians stay flat   -> FIXED-TICK:   uncapping buys nothing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
