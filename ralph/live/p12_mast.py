#!/usr/bin/env python3
"""A mast failure as an unfolding event (GPT pass-10 lead 6) over a shed with colonists under the line, which is also the
overhead_span_above_everything look for buildings. Runs on Steve: python.exe ralph/live/p12_mast.py TAG Look

On the played save gss_ba_<Look>: a granite shed is built under the first span (masts 0 and 1), two colonists stand under the
wires, then mortar shells land on the lamp mast until it falls. Shots: before, the tick it falls, a second later, ten seconds
later; then the player puts the mast's blueprint back where it stood, colonists build it, the cut anchors get the re-string
order, and shots follow each stage. Every shot name is unique (the screenshot tool writes asynchronously).
A thin driver over lived_in.Run, like p12_look.py: only lived_in's frame table knows where these saves keep their rooms.
"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "ralph", "live"))
import lived_in as LI  # noqa: E402

BA = "ralph/live/ba_state.json"
LI.FRAMES.update({"shed": (38, -2, 20, 11), "line": (36, -5, 34, 15), "mast1": (46, -3, 14, 8)})


def anchors(R):
    return R.B.ap("census").get("anchors") or []


def say(R, what):
    t = R.B.call("jawa/time_clock")["ticksGame"]
    a = [{k: x.get(k) for k in ("id", "x", "z", "fallenLive")} | {"fallen": len(x.get("fallen") or []), "links": len(x.get("links") or [])} for x in anchors(R)]
    c = R.B.ap("census")
    print("@%d %s anchors=%s counters=%s" % (t, what, json.dumps(a), json.dumps({k: c.get(k) for k in ("autoLinks", "orphanRelinks", "liveWirePriced", "explosionCuts")})))
    ps = [q for q in R.B.call("jawa/list_pawns").get("pawns") or [] if q.get("isPlayer")]
    print("   colonists", len(ps), "downed", [q.get("name") for q in ps if q.get("downed")])


def play_until(R, ticks, done, step=300):
    t0 = R.B.call("jawa/time_clock")["ticksGame"]
    while R.B.call("jawa/time_clock")["ticksGame"] - t0 < ticks:
        R.play(step)
        if done():
            return True
    return done()


def main():
    tag, look = sys.argv[1], sys.argv[2]
    st = json.load(open(BA))[look]
    R = LI.Run()
    print("load", json.dumps(R.B.call("rimworld/load_game_ready", saveName="gss_ba_%s" % look, timeoutMs=240000))[:100])
    from await_lifecycle import await_lifecycle
    print("map_ready", await_lifecycle(R.B.call, "map_ready", 240, poll_s=0.5).ok)
    time.sleep(8)
    json.dump(st, open(LI.STATE, "w"))
    ox, oz = st["ox"], st["oz"]
    m1 = (53, 1)

    # a shed where the yard has room, right under the first span's wires
    R.call("rimworld/set_god_mode", enabled=True)
    R.call("jawa/destroy_batch", rects="%d,%d,6,5" % (ox + 44, oz + 0), categories="Plant,Item,Filth")
    walls = [c for c in LI.perimeter(44, 0, 49, 4) if c != (46, 0)]
    R.call("jawa/build_batch", ops=";".join("Wall:%d,%d" % (x + ox, z + oz) for x, z in walls), stuff="BlocksGranite", wipeExisting=False)
    R.call("jawa/build_batch", ops="Door:%d,%d,0" % (ox + 46, oz + 0), stuff="WoodLog", wipeExisting=False)
    R.call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,4,3" % (ox + 45, oz + 1))
    R.call("jawa/spawn_batch", ops="WoodLog:%d,%d;Steel:%d,%d" % (ox + 45, oz + 1, ox + 48, oz + 3))
    R.call("rimworld/set_god_mode", enabled=False)
    for x, z in ((42, 5), (51, 5)):
        R.call("jawa/spawn_pawn", kindDef="Colonist", x=ox + x, z=oz + z, count=1, faction="PlayerColony")
    R.B.ticks(2)
    say(R, "before")
    R.shots(tag + "0", ["shed", "line"])

    # mortar shells on the lamp mast until it is down
    mid = st["masts"][1]
    for shell in range(6):
        R.call("jawa/explosion_at", at="%d,%d" % (ox + m1[0], oz + m1[1]), damType="Bomb", damAmount=50, radius=1.9)
        R.B.ticks(1)
        if not any(a.get("id") == mid for a in anchors(R)):
            print("mast down after", shell + 1, "shells")
            break
    say(R, "fell")
    R.shots(tag + "1", ["line", "mast1"])
    R.B.ticks(60)
    R.shots(tag + "2", ["line", "shed"])
    R.play(600)
    say(R, "after 600")
    R.shots(tag + "3", ["line", "shed", "mast1"])

    # what a colony has: the saves' stockpile holds one unit a stack, so a real stack of steel goes in the stockpile first
    R.call("jawa/spawn_batch", ops="Steel:%d,%d,75;Steel:%d,%d,75" % (ox + 2, oz - 6, ox + 4, oz - 6))
    # the player puts the mast back: a blueprint on the same cell, built by colonists
    print("blueprint", json.dumps(R.ap("place:RM_AerialLampMast:%s:%d,%d:build" % (look, ox + m1[0], oz + m1[1])))[:200])
    built = play_until(R, 6000, lambda: any((a.get("x"), a.get("z")) == (ox + m1[0], oz + m1[1]) for a in anchors(R)))
    say(R, "rebuilt=%s" % built)
    R.shots(tag + "4", ["line", "mast1"])

    # re-string orders on every anchor with a cut link
    for a in anchors(R):
        r = R.B.ap("restringstate:%d" % a["id"])
        if r.get("cut"):
            print("order", a["id"], json.dumps(R.ap("restringorder:%d" % a["id"]))[:160])
    play_until(R, 6000, lambda: all(not R.B.ap("restringstate:%d" % a["id"]).get("cut") for a in anchors(R)))
    say(R, "restrung")
    R.shots(tag + "5", ["line", "shed"])
    if R.notes:
        print("NOTES", R.notes[:8])


if __name__ == "__main__":
    main()
