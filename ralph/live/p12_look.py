#!/usr/bin/env python3
"""Load each look's played save (gss_ba_<Look>) and shoot named frames at play zoom; --blast then cuts a span and the yard trunk and
shoots again. Runs on Steve: python.exe ralph/live/p12_look.py TAG [--frames dense,span] [--blast] [--cut-frames cutspan,drop] [Look ...]

A thin driver over lived_in.Run (its frames, origins and shot copy), so no scenelib helper: the saves were built by lived_in, and only
its frame table knows where their rooms are.
"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "ralph", "live"))
import lived_in as LI  # noqa: E402

BA = "ralph/live/ba_state.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("looks", nargs="*", default=["Modern", "Scrapper", "Industrial", "Futuristic"])
    ap.add_argument("--frames", default="dense,span")
    ap.add_argument("--blast", action="store_true")
    ap.add_argument("--cut-frames", default="cutspan,drop,yard")
    ap.add_argument("--play", type=int, default=0)
    ap.add_argument("--rect", default="", help="ad-hoc frames in the site's own cells: name:x,z,w,h[;...]")
    ap.add_argument("--tiles", action="store_true", help="also shoot the whole colony at play zoom, 20x11-cell tiles named t<col><row>")
    a = ap.parse_args()
    st = json.load(open(BA))
    for look in a.looks:
        R = LI.Run()
        r = R.B.call("rimworld/load_game_ready", saveName="gss_ba_%s" % look, timeoutMs=240000)
        print("load", look, json.dumps(r)[:120])
        from await_lifecycle import await_lifecycle
        lc = await_lifecycle(R.B.call, "map_ready", 240, poll_s=0.5)   # load_game_ready can answer while "Spawning things" still shows
        print("map_ready", lc.ok, lc.reason)
        time.sleep(8)
        json.dump(st[look], open(LI.STATE, "w"))
        if a.play:
            R.play(a.play)
        frames = [f for f in a.frames.split(",") if f]
        for q in [q for q in a.rect.split(";") if q]:
            nm, v = q.split(":")
            LI.FRAMES[nm] = tuple(int(t) for t in v.split(","))
            frames.append(nm)
        if a.tiles:
            for i, x in enumerate(range(-3, 77, 20)):
                for j, z in enumerate(range(8, -12, -11)):
                    LI.FRAMES["t%d%d" % (i, j)] = (x, z, 20, 11)
                    frames.append("t%d%d" % (i, j))
        R.shots(a.tag, frames)
        if a.blast:
            R.blast()
            R.B.ticks(120)
            R.shots(a.tag + "cut", a.cut_frames.split(","))
        if R.notes:
            print("NOTES", R.notes[:5])


if __name__ == "__main__":
    main()
