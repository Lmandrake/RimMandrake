#!/usr/bin/env python3
"""GPT pass-12 broaden leads, played on a look's saved colony (gss_ba_<Look>). Runs on Steve: python.exe ralph/live/p12_reno.py TAG Look

  reno    (#5) colonists build a wall across the kitchen through the cords lying there, and a bedroom wall the conduit runs under
          becomes a door: shots while the blueprints are pending, while they are frames, and when built
  supply  (#4) a blast cuts the span to the hut, whose only source is its battery: fallen-wire liveness and shots with the
          battery full, drained, and full again
  reload  (#8) a mortar drops the lamp mast and its blueprint is placed; save, quit to the menu, reload, let colonists build it,
          save and reload again: census and shots at each step
A thin driver over lived_in.Run, like p12_look.py: only lived_in's frame table knows where these saves keep their rooms.
"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "ralph", "live"))
import lived_in as LI  # noqa: E402
from await_lifecycle import await_lifecycle  # noqa: E402

BA = "ralph/live/ba_state.json"
LI.FRAMES.update({"kitchen": (-1, -1, 16, 10), "bed2": (6, 9, 13, 7), "hutline": (52, -5, 22, 12), "line": (36, -5, 34, 15)})


def load(R, name):
    print("load", name, json.dumps(R.B.call("rimworld/load_game_ready", saveName=name, timeoutMs=240000))[:90])
    print("map_ready", await_lifecycle(R.B.call, "map_ready", 240, poll_s=0.5).ok)
    time.sleep(8)


def census(R, what):
    c = R.B.ap("census")
    a = [{k: x.get(k) for k in ("id", "x", "z", "fallenLive")} | {"fallen": len(x.get("fallen") or []), "links": len(x.get("links") or [])} for x in c.get("anchors") or []]
    print("@%d %s anchors=%s relinks=%s priced=%s" % (R.B.call("jawa/time_clock")["ticksGame"], what, json.dumps(a), c.get("orphanRelinks"), c.get("liveWirePriced")))
    return c


def things(R, d, rect):
    return R.B.call("jawa/list_things", defName=d, rect=rect, limit=50).get("things") or []


def main():
    tag, look = sys.argv[1], sys.argv[2]
    parts = sys.argv[3].split(",") if len(sys.argv) > 3 else ["reno", "supply", "reload"]
    st = json.load(open(BA))[look]
    ox, oz = st["ox"], st["oz"]
    R = LI.Run()
    load(R, "gss_ba_%s" % look)
    json.dump(st, open(LI.STATE, "w"))
    R.call("jawa/spawn_batch", ops="Steel:%d,%d,75;Steel:%d,%d,75;WoodLog:%d,%d,75" % (ox + 2, oz - 6, ox + 4, oz - 6, ox + 6, oz - 6))

    if "reno" in parts:
        R.shots(tag + "r0", ["kitchen", "bed2"])
        # a partition across the kitchen, through the cords lying on its floor; the wall between bedrooms 2 and 3 at the conduit becomes a door
        part = [(7, z) for z in range(1, 5)]
        r = R.call("jawa/blueprint_place", **{"def": "Wall", "x": ox + 7, "z": oz + 1, "stuff": "WoodLog"})
        for x, z in part[1:]:
            R.call("jawa/blueprint_place", **{"def": "Wall", "x": ox + x, "z": oz + z, "stuff": "WoodLog"})
        print("blueprint wall", json.dumps(r)[:160])
        R.call("rimworld/set_god_mode", enabled=True)
        R.call("jawa/destroy_batch", rects="%d,%d,1,1" % (ox + 12, oz + 13), categories="Building")   # takes the conduit under the wall too
        R.ap("cplace:PowerConduit:%s:%d,%d:god" % (LI.KEY[look], ox + 12, oz + 13))                    # so it goes back, in its run's look
        R.ap("cprocess")
        R.call("rimworld/set_god_mode", enabled=False)
        R.B.ticks(2)
        print("door", json.dumps(R.call("jawa/blueprint_place", **{"def": "Door", "x": ox + 12, "z": oz + 13, "stuff": "WoodLog", "rot": 1}))[:160])
        R.shots(tag + "r1", ["kitchen", "bed2"])          # pending: blueprints, and a gap where the wall was
        for _ in range(12):
            R.play(400)
            fr = things(R, "Frame_Wall", "%d,%d,1,4" % (ox + 7, oz + 1))
            if fr:
                R.shots(tag + "r2", ["kitchen"])          # frames going up
                break
        for _ in range(20):
            if len(things(R, "Wall", "%d,%d,1,4" % (ox + 7, oz + 1))) >= 4 and things(R, "Door", "%d,%d,1,1" % (ox + 12, oz + 13)):
                break
            R.play(400)
        print("built walls", len(things(R, "Wall", "%d,%d,1,4" % (ox + 7, oz + 1))), "door", len(things(R, "Door", "%d,%d,1,1" % (ox + 12, oz + 13))))
        R.play(300)
        R.shots(tag + "r3", ["kitchen", "bed2"])

    if "supply" in parts:
        R.call("jawa/explosion_at", at="%d,%d" % (ox + 60, oz + 2), damType="Bomb", damAmount=40, radius=2.5)
        R.play(300)
        census(R, "cut, hut battery as saved")
        R.shots(tag + "s0", ["hutline"])
        hut = [t.get("id") or t.get("thingId") for t in things(R, "Battery", "%d,%d,3,3" % (ox + 71, oz))]
        print("hut battery", hut)
        for pct, n in ((0.0, "s1"), (1.0, "s2")):
            for t in hut:
                R.call("jawa/battery_set", thing=t, mode="setPct", value=pct)
            R.play(300)
            census(R, "hut battery %d%%" % (pct * 100))
            R.shots(tag + n, ["hutline"])

    if "reload" in parts:
        mid = st["masts"][1]
        for shell in range(6):
            R.call("jawa/explosion_at", at="%d,%d" % (ox + 53, oz + 1), damType="Bomb", damAmount=50, radius=1.9)
            R.B.ticks(1)
            if not any(a.get("id") == mid for a in R.B.ap("census").get("anchors") or []):
                break
        R.play(200)
        print("blueprint", json.dumps(R.ap("place:RM_AerialLampMast:%s:%d,%d:build" % (look, ox + 53, oz + 1)))[:120])
        census(R, "mast down, blueprint placed")
        R.shots(tag + "m0", ["line"])
        print("save", json.dumps(R.B.call("rimworld/save_game", saveName="gss_p12_mid_%s" % look))[:100])
        time.sleep(3)
        R.B.call("rimworld/go_to_main_menu")
        time.sleep(5)
        load(R, "gss_p12_mid_%s" % look)
        census(R, "reloaded")
        R.shots(tag + "m1", ["line"])
        for _ in range(20):
            if any((a.get("x"), a.get("z")) == (ox + 53, oz + 1) for a in R.B.ap("census").get("anchors") or []):
                break
            R.play(400)
        R.play(300)
        census(R, "rebuilt")
        R.shots(tag + "m2", ["line"])
        print("save", json.dumps(R.B.call("rimworld/save_game", saveName="gss_p12_mid2_%s" % look))[:100])
        time.sleep(3)
        R.B.call("rimworld/go_to_main_menu")
        time.sleep(5)
        load(R, "gss_p12_mid2_%s" % look)
        census(R, "reloaded again")
        R.shots(tag + "m3", ["line"])
    if R.notes:
        print("NOTES", R.notes[:8])


if __name__ == "__main__":
    main()
