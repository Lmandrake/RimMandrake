#!/usr/bin/env python3
"""A cord end that turns live or dead OFF SCREEN is laid again at once (RIMMANDRAKE_MEND_SLACK_FRESH_BUILD_DIFFERS_BY_ONE_EDGE).

The proof row D2_fresh_builder_same failed about once in five runs, always "missing 1, extra 1" on one edge whose two keys differed
only in its end's live/dead letter: the mod's own liveness poll saw the flip and dirtied its section, but only a section on screen
is redrawn that frame, and nothing told the cord component to rebuild an off-screen one (every other change does:
StaleOffscreen). Until vanilla got round to that section the published cord was the old one.

Here: a battery, three cells of conduit and nothing else, far from where the camera is framed. Twelve times the battery is filled
or emptied, two ticks played, the mod's poll run (it must report a flip) and, on the very next probe, the live cords compared with a
fresh build. PASS: every flip was seen and every compare equal.

    python.exe src\\RimMandrake\\GimmeSomeSlack\\northstar\\live_flip_fresh.py [--out result.json]

Game up with a map on the gimmesomeslack tier, bridge held. The run builds on the map at SITE and clears it after. Exit 0 = PASS.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Utils"))

PROBE = "RimMandrake.GimmeSomeSlack.GimmeSomeSlackProbe"
SITE = (30, 30)          # the battery's cell; the camera is framed CAM_OFF cells east of it
CAM_OFF = 120
CYCLES = 12


def verdict(cycles):
    """(status, why) from the cycles' readings: [{"flips": n, "fresh": {...}}]. UNMEASURED when a poll saw no flip (the battery
    did not change the net: nothing was tested) or a compare gave no counters; FAIL when any compare differs."""
    if not cycles:
        return "UNMEASURED", "no cycle ran"
    for i, c in enumerate(cycles):
        f = c.get("fresh") or {}
        if not isinstance(c.get("flips"), int) or c["flips"] < 1:
            return "UNMEASURED", "cycle %d: the poll saw no flip" % i
        if not all(isinstance(f.get(k), int) for k in ("edges", "missing", "extra", "different")) or f["edges"] < 1:
            return "UNMEASURED", "cycle %d: the fresh compare gave no counters" % i
    bad = [i for i, c in enumerate(cycles) if c["fresh"]["missing"] or c["fresh"]["extra"] or c["fresh"]["different"]]
    return ("FAIL", "cycles %s: the live cords differ from a fresh build right after the flip" % bad) if bad else ("PASS", "%d flips, every compare equal" % len(cycles))


def run(B):
    x, z = SITE
    rect = "%d,%d,8,5" % (x - 1, z - 2)
    B.call("jawa/destroy_batch", rects=rect, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:" + rect)
    B.call("jawa/set_fog", action="unfog", rect=rect)
    B.call("jawa/build_batch", ops="Battery:%d,%d,0" % (x, z), faction="player")
    B.call("jawa/build_batch", ops=";".join("PowerConduit:%d,%d,0" % (x + k, z) for k in (1, 2, 3)), faction="player", wipeExisting=False)
    bat = next((t.get("id") or t.get("thingId") for t in (B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % (x, z), limit=3).get("things") or [])), None)
    B.call("rimworld/frame_cell_rect", x=x + CAM_OFF, z=z, width=1, height=1, paddingCells=0)
    B.call("jawa/battery_set", thing=bat, mode="setPct", value=0.0)
    B.ticks(3)
    B.probe_of(PROBE, "rebuild", 60.0, 0.3)
    B.probe_of(PROBE, "poll", 60.0, 0.3)
    cycles = []
    try:
        for i in range(CYCLES):
            B.call("jawa/battery_set", thing=bat, mode="setPct", value=1.0 if i % 2 == 0 else 0.0)
            B.ticks(2)
            p = B.probe_of(PROBE, "poll", 60.0, 0.05)
            f = B.probe_of(PROBE, "fresh", 60.0, 0.05)
            cycles.append({"flips": p.get("flips"), "fresh": {k: f.get(k) for k in ("edges", "same", "different", "missing", "extra", "pending", "freshOnly", "liveOnly")}})
    finally:
        B.call("jawa/destroy_batch", rects=rect, categories="All")
    st, why = verdict(cycles)
    return {"row": "live_flip_fresh", "result": st, "why": why, "battery": bat, "site": list(SITE), "cycles": cycles}


def main(argv):
    import validation_core as vc
    r = run(vc.Bridge())
    if "--out" in argv:
        with open(argv[argv.index("--out") + 1], "w", encoding="utf-8") as f:
            json.dump(r, f, indent=1)
    print(json.dumps({k: r[k] for k in ("result", "why")}))
    print("flips/missing/extra per cycle: " + " ".join("%s/%s/%s" % (c["flips"], c["fresh"].get("missing"), c["fresh"].get("extra")) for c in r["cycles"]))
    print("live_flip_fresh " + r["result"])
    return 0 if r["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
