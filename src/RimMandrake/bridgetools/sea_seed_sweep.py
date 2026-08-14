#!/usr/bin/env python3
"""sea_seed_sweep.py - measure vanilla's sea across N generated worlds.

WHY THIS EXISTS
===============
VISION's sea spec asks for ~25% water in exactly THREE oddly-shaped bodies, and
was one commit from authoring a WorldGenStep to produce it. The first world we
ever measured -- quicktest seed "green" -- landed 25.0% in exactly 2 bodies.

One seed is an anecdote. It cannot distinguish "vanilla already does this" from
"we got lucky", and those two answers differ by a whole v1 build item. This runs
the same measurement over N fresh worlds so the question is answered by a
distribution instead of a coin flip.

    measure the baseline BEFORE building the thing that improves it.

WHAT IT DOES, PER ITERATION
===========================
    rimworld/go_to_main_menu          <- REQUIRED. start_debug_game_ready waits
                                         for the ENTRY scene and returns
                                         "Timed out waiting for RimWorld entry
                                         scene readiness" if a game is loaded.
    rimworld/start_debug_game_ready   <- new world + map, ~90 s on this stack
    jawa/world_stats                  <- read-only

Only requirements 1 and 2 of the sea gate are collected: waterPct, bodiesTotal
and bodiesOverMinSize. Requirements 3 and 4 (raggedness, centroidLat) are
DELIBERATELY not reported -- their units are wrong in the deployed companion and
a wrong number is worse than a missing one.

WHAT THIS CANNOT TELL YOU
=========================
- Quicktest generates at planetCoverage 0.3. A campaign world may use a
  different coverage, and body COUNT is the statistic most likely to move with
  it. Treat these as vanilla's shape at 0.3, not as the campaign's.
- JawaSeaShaper.dll is NOT deployed, so this is the sea WITHOUT our step.
  That is the point: it is the baseline the step would have to beat.
- A seed passing 1 and 2 is a CANDIDATE, never an acceptance -- 3 and 4 are
  uncollectable until the companion redeploys.

⚠️ Destroys the current map on every iteration. Do not run while another seat
holds the instrument.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CLIENT = REPO / "src" / "RimMandrake" / "Utils" / "rimbridge_client.py"

# python.exe, not python3: the bridge binds Windows loopback and WSL2 is
# NAT-mode, so a WSL interpreter has no route at all. This is the network half
# of the per-script interpreter rule, not a habit.
PY = "python.exe"


def call(tool, params, timeout=200):
    """One bridge call. Returns the parsed dict, or None on any failure."""
    cmd = [PY, str(CLIENT), "--timeout", str(timeout - 30), "--call", tool,
           "--json", json.dumps(params), "--yes-i-know-this-is-live"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=timeout, cwd=str(REPO)).stdout
    except subprocess.TimeoutExpired:
        return None
    # The client prints the envelope as JSON; find the outermost object.
    start = out.find("{")
    if start < 0:
        return None
    try:
        return json.loads(out[start:])
    except json.JSONDecodeError:
        return None


def wait_playable(limit_s=240):
    """Poll until a map scene exists. Returns True if it arrived.

    🔴 start_debug_game_ready routinely TIMES OUT AT THE CLIENT AND WORKS
    ANYWAY -- measured 2026-08-14, hasCurrentGame went false->true while the
    call reported failure. So the caller must never retry it; it polls instead.
    """
    deadline = time.time() + limit_s
    while time.time() < deadline:
        st = call("rimworld/get_ui_state", {}, timeout=90)
        if st and st.get("programState") == "Playing":
            return True
        time.sleep(10)
    return False


def one_world(i):
    """Generate one world and measure it. Returns a row dict."""
    if not call("rimworld/go_to_main_menu", {}, timeout=120):
        return {"i": i, "error": "go_to_main_menu failed"}
    time.sleep(5)

    # Fire and forget -- the result is read from get_ui_state, never from this
    # call's own return, for the timeout reason above.
    call("rimworld/start_debug_game_ready",
         {"readiness": "playable", "pauseIfNeeded": True, "timeoutMs": 150000},
         timeout=200)

    if not wait_playable():
        return {"i": i, "error": "no map scene within 240s"}

    w = call("jawa/world_stats", {}, timeout=200)
    if not w or not w.get("success"):
        return {"i": i, "error": "world_stats failed",
                "message": (w or {}).get("message")}

    return {
        "i": i,
        "seedString": w.get("seedString"),
        "planetCoverage": w.get("planetCoverage"),
        "tilesTotal": w.get("tilesTotal"),
        "waterPct": w.get("waterPct"),
        "bodiesTotal": w.get("bodiesTotal"),
        "bodiesOverMinSize": w.get("bodiesOverMinSize"),
        "largestBodyPct": w.get("largestBodyPct"),
        # Requirement 1 is 22-28%; requirement 2 is exactly 3 above min size.
        # Scored here so nobody re-derives the band from prose.
        "req1_pass": 22.0 <= (w.get("waterPct") or 0) <= 28.0,
        "req2_pass": w.get("bodiesOverMinSize") == 3 and w.get("bodiesTotal") == 3,
    }


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    rows = []
    for i in range(1, n + 1):
        row = one_world(i)
        rows.append(row)
        print(json.dumps(row), flush=True)

    good = [r for r in rows if "error" not in r]
    summary = {
        "generated": len(rows),
        "measured": len(good),
        "req1_pass": sum(1 for r in good if r["req1_pass"]),
        "req2_pass": sum(1 for r in good if r["req2_pass"]),
        "both_pass": sum(1 for r in good if r["req1_pass"] and r["req2_pass"]),
        "waterPct": sorted(r["waterPct"] for r in good),
        "bodiesOverMinSize": sorted(r["bodiesOverMinSize"] for r in good),
    }
    print("SUMMARY " + json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
