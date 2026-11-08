#!/usr/bin/env python3
"""GPT pass-13 broaden lead 1, played on a look's saved colony (gss_ba_<Look>): remodel a powered bedroom and watch its cords.
Runs on Steve: python.exe ralph/live/bedroom_reno.py TAG Look [Look ...]

Bedroom 2 (lived_in.plan: walls x=6..12, z=10..15, door (9,10), bed (9,12), lamp (10,14), conduit along z=13): the bed is moved
onto the cord's path, an end table and a dresser go in at its foot, the doorway is walled off, then opened again. A shot after every
step, a few ticks on, so a re-lay that jumps the cord about, a cord under the new furniture or one more cord into the room shows.
A thin driver over lived_in.Run, like p12_look.py: only lived_in's frame table knows where these saves keep their rooms.
"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "ralph", "live"))
import lived_in as LI  # noqa: E402
from await_lifecycle import await_lifecycle  # noqa: E402

BA = "ralph/live/ba_state.json"
LI.FRAMES.update({"bed2": (5, 8, 9, 9)})


def main():
    tag, looks = sys.argv[1], sys.argv[2:] or ["Modern"]
    st = json.load(open(BA))
    for look in looks:
        R = LI.Run()
        R.B.call("rimworld/load_game_ready", saveName="gss_ba_%s" % look, timeoutMs=240000)
        print("map_ready", look, await_lifecycle(R.B.call, "map_ready", 240, poll_s=0.5).ok)
        time.sleep(8)
        json.dump(st[look], open(LI.STATE, "w"))
        ox, oz = st[look]["ox"], st[look]["oz"]

        def at(x, z, w=1, h=1):
            return "%d,%d,%d,%d" % (ox + x, oz + z, w, h)

        def build(op, x, z, rot=None, stuff=None):
            kw = {"ops": "%s:%d,%d%s" % (op, ox + x, oz + z, "" if rot is None else ",%d" % rot), "wipeExisting": False}
            if stuff:
                kw["stuff"] = stuff
            r = R.call("jawa/build_batch", **kw)
            print("build", op, x, z, r.get("survived"), json.dumps(r.get("failed") or [])[:160])

        def shot(step):
            R.B.ticks(60)
            R.shots("%s%s" % (tag, step), ["bed2"])

        shot("0")
        # 1: the bed moves onto the conduit row, where the cord lies
        print("bed out", json.dumps(R.call("jawa/destroy_batch", rects=at(9, 12, 1, 2), categories="Building"))[:120])
        build("PowerConduit", 9, 13)   # the destroy takes the conduit under the bed's foot with it: a player moving a bed keeps the conduit
        build("Bed", 8, 13, rot=1, stuff="WoodLog")
        shot("1")
        # 2: an end table and a dresser at its foot
        build("EndTable", 10, 13, stuff="WoodLog")
        build("Dresser", 8, 11, rot=0, stuff="WoodLog")
        shot("2")
        # 3: the doorway walled off
        R.call("jawa/destroy_batch", rects=at(9, 10), categories="Building")
        build("Wall", 9, 10, stuff="BlocksGranite")
        shot("3")
        # 4: and opened again
        R.call("jawa/destroy_batch", rects=at(9, 10), categories="Building")
        build("Door", 9, 10, rot=0, stuff="WoodLog")
        shot("4")
        if R.notes:
            print("NOTES", R.notes[:6])


if __name__ == "__main__":
    main()
