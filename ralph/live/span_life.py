#!/usr/bin/env python3
"""A cut span's whole life in a played colony (GPT pass-13 lead 2): blast a live span, watch the fallen wires writhe and spark at play zoom
and close up (frame sequences with the probe's tip beside each frame), cut the mast's supply and see them lie dead, restore it, then let
the colonists re-string it. Runs on Steve: python.exe ralph/live/span_life.py TAG Look [--night]

A thin driver over lived_in.Run and motion_frames: only lived_in's frame table knows where the gss_ba_<Look> saves keep their rooms.
Every shot name is unique (the screenshot tool writes asynchronously).
"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "ralph", "live"))
import lived_in as LI  # noqa: E402
import motion_frames as MF  # noqa: E402
from await_lifecycle import await_lifecycle  # noqa: E402

BA = "ralph/live/ba_state.json"
LI.FRAMES.update({"line": (36, -5, 34, 15), "cut2": (50, -5, 22, 12)})
# the conduit that carries the house grid to the first mast (lived_in.plan: line(38,5..39,5) + line(39,3..39,4))
FEED = (38, 3, 2, 3)


def anchors(R):
    return R.B.ap("census").get("anchors") or []


def fallen(R):
    out = []
    for a in anchors(R):
        for f in a.get("fallen") or []:
            out.append({"anchor": a["id"], "live": a.get("fallenLive"), "ends": [w["laid"] for w in f.get("wireEnds") or []]})
    return out


def frames(R, tag, label, cells, n=10):
    """A frame sequence round the first live fallen wire end, at `cells` half-width (3.2 close, 8 about play zoom)."""
    for a in anchors(R):
        if a.get("fallenLive") is not True:
            continue
        for f in a.get("fallen") or []:
            ends = f.get("wireEnds") or []
            if not ends:
                continue
            ex, ez = ends[0]["laid"]
            aid = a["id"]

            def read():
                for q in anchors(R):
                    if q.get("id") == aid and q.get("fallen"):
                        return [w["now"] for w in q["fallen"][0]["wireEnds"]]
                return None
            MF.grab(R.B, "%s_%s_warm" % (tag, label), ex, ez, cells)
            time.sleep(0.5)
            return MF.sequence(R.B, tag, label, read, ex, ez, n, cells)
    print("no live fallen wire for", label)
    return None


def main():
    tag, look = sys.argv[1], sys.argv[2]
    night = "--night" in sys.argv
    st = json.load(open(BA))
    R = LI.Run()
    R.B.call("rimworld/load_game_ready", saveName="gss_ba_%s" % look, timeoutMs=240000)
    lc = await_lifecycle(R.B.call, "map_ready", 240, poll_s=0.5)
    print("map_ready", lc.ok, lc.reason)
    time.sleep(8)
    json.dump(st[look], open(LI.STATE, "w"))
    ox, oz = st[look]["ox"], st[look]["oz"]
    R.shots(tag + "a0", ["line"])
    if night:
        clk = R.B.call("jawa/time_clock")
        print("clock", json.dumps(clk)[:300])
        hour = clk.get("hourOfDay", clk.get("hour"))
        if hour is not None:
            R.play(int(((22 - hour) % 24) * 2500))
    R.blast()
    R.B.ticks(120)
    print("fallen", json.dumps(fallen(R))[:600])
    R.shots(tag + "a1", ["line", "cutspan"])
    R.B.call("rimworld/set_time_speed", speed=1)
    frames(R, tag, "play", 8.0)
    frames(R, tag, "close", 3.2)
    R.B.call("rimworld/set_time_speed", speed=0)
    # the supply cut: the conduit from the house grid to the first mast goes
    x, z, w, h = FEED
    print("cut feed", json.dumps(R.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (ox + x, oz + z, w, h), categories="Building"))[:200])
    R.B.ticks(400)
    print("fallen after feed cut", json.dumps(fallen(R))[:400])
    R.shots(tag + "a2", ["line", "cutspan"])
    # and back
    cells = [(38, 5), (39, 5), (39, 3), (39, 4)]
    print("restore feed", json.dumps(R.call("jawa/build_batch", ops=";".join("PowerConduit:%d,%d" % (ox + a, oz + b) for a, b in cells), wipeExisting=False))[:200])
    R.B.ticks(400)
    print("fallen after restore", json.dumps(fallen(R))[:400])
    R.shots(tag + "a3", ["line", "cutspan"])
    # the colonists re-string every cut anchor
    for a in anchors(R):
        r = R.B.ap("restringstate:%d" % a["id"])
        if r.get("cut"):
            print("order", a["id"], json.dumps(R.ap("restringorder:%d" % a["id"]))[:160])
    t0 = time.time()
    R.play(5000)
    print("fallen after re-string play (%.0fs)" % (time.time() - t0), json.dumps(fallen(R))[:400])
    R.shots(tag + "a4", ["line", "cutspan"])
    if R.notes:
        print("NOTES", R.notes[:6])


if __name__ == "__main__":
    main()
