#!/usr/bin/env python3
"""A doorway grown the way a player grows one, a shot at every step, with the game running between: what does each edit do to the cords?

    python.exe ralph/live/grow_door.py TAG [--look Modern] [--fresh-map]

Steps: one heater beyond a door; a lamp and a branch added; the run extended; the heater removed and put back elsewhere; the branch removed; a wall built across a loop; the door walled up; save and load.
"""
import argparse, json, os, shutil, sys, time
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "northstar"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "northstar_matrix"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(REPO, "ralph", "live"))
import run_live as RL  # noqa: E402
from lived_in import Run, line, perimeter, KEY, SHOTS  # noqa: E402


class Grow(Run):
    def go(self, tag, look, fresh):
        B = self.B
        if fresh:
            B.call("rimworld/go_to_main_menu")
            B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
            from await_lifecycle import await_lifecycle
            lc = await_lifecycle(B.call, "map_ready", 240, poll_s=0.5)
            if not lc.ok:
                raise SystemExit("no fresh map: %s" % lc.reason)
        self.call("rimworld/set_god_mode", enabled=True)
        self.call("jawa/research_bulk", mode="finish_all")
        self.call("jawa/storyteller_swap", difficultyDef="Peaceful")
        self.call("jawa/incident_queue_clear")
        self.call("jawa/set_fog", action="unfog", rect="0,0,250,250")
        ox, oz = self.site()
        self.ox, self.oz, self.tag, self.look = ox, oz, tag, look
        key = KEY[look]

        def rect(x, z, w, h):
            return "%d,%d,%d,%d" % (ox + x, oz + z, w, h)
        self.rect = rect
        self.call("jawa/destroy_batch", rects=rect(-2, -4, 34, 22), categories="Plant,Item,Filth,Building")
        self.call("jawa/set_terrain_batch", ops="WoodPlankFloor:%s" % rect(1, 1, 11, 11))
        walls = [c for c in perimeter(0, 0, 12, 12) if c != (12, 6)]
        self.batch("Wall", walls, stuff="BlocksGranite")
        self.batch("Door", [(12, 6)], rot=1, stuff="WoodLog")
        self.call("jawa/set_roof_batch", ops="RoofConstructed:%s" % rect(1, 1, 11, 11))
        self.ap("clearpicks"); self.ap("cclearpicks")
        self.key = key
        self.batch("SolarGenerator", [(20, 12)])
        self.batch("Battery", [(3, 6)], rot=0)
        for t in B.call("jawa/list_things", defName="Battery", rect=rect(0, 0, 40, 20), limit=5).get("things") or []:
            self.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=1.0)
        self.step("0_start", conduit=line(5, 6, 11, 6) + [(12, 6)] + line(13, 6, 18, 6), place=[("Heater", (19, 6))])
        self.step("1_lamp", conduit=line(16, 7, 16, 9), place=[("StandingLamp", (16, 10))])
        self.step("2_extend", conduit=line(19, 7, 22, 7) if False else line(17, 9, 24, 9), place=[("StandingLamp", (25, 9))])
        self.step("3_noheater", remove=[(19, 6)])
        self.step("4_heater2", place=[("Heater", (18, 10))])
        self.step("5_nobranch", remove=line(16, 7, 16, 8))
        self.step("6_wall", walls=line(14, 3, 14, 5) + line(14, 7, 14, 9))
        self.step("7_doorwall", remove=[(12, 6)], walls=[(12, 6)], conduit=[(12, 6)])
        self.call("rimworld/set_god_mode", enabled=False)
        self.shot("8_final")
        print("census", json.dumps({k: v for k, v in B.probe("census").items() if isinstance(v, (int, str, bool))})[:300])

    def batch(self, d, cells, rot=None, stuff=None):
        ox, oz = self.ox if hasattr(self, "ox") else 0, self.oz if hasattr(self, "oz") else 0
        kw = {"ops": ";".join("%s:%d,%d%s" % (d, c[0] + ox, c[1] + oz, "" if rot is None else ",%d" % rot) for c in cells), "wipeExisting": False}
        if stuff:
            kw["stuff"] = stuff
        r = self.call("jawa/build_batch", **kw)
        if r.get("survived") != len(cells):
            self.notes.append("build %s %s/%d %s" % (d, r.get("survived"), len(cells), json.dumps(r.get("failed") or [])[:200]))

    def step(self, name, conduit=(), place=(), remove=(), walls=()):
        for c in remove:
            self.call("jawa/destroy_batch", rects=self.rect(c[0], c[1], 1, 1), categories="Building")
        for c in walls:
            self.call("jawa/destroy_batch", rects=self.rect(c[0], c[1], 1, 1), categories="Plant,Item,Filth")
        if walls:
            self.batch("Wall", list(walls), stuff="BlocksGranite")
        for c in conduit:
            self.ap("cplace:PowerConduit:%s:%d,%d:god" % (self.key, c[0] + self.ox, c[1] + self.oz))
        self.ap("cprocess")
        for d, c in place:
            self.batch(d, [c])
        self.B.call("rimworld/set_time_speed", speed=1)
        time.sleep(2.5)  # the game running, as a player's would: the frame-sliced rebuild, no forced one
        self.B.call("rimworld/set_time_speed", speed=0)
        self.shot(name)

    def shot(self, name):
        full = "%s_%s_%s" % (self.tag, self.look, name)
        self.B.call("jawa/clear_ui", all=True)
        w, h = 30, 18
        res = self.B.call("rimworld/screenshot_cell_rect", x=self.ox - 1, z=self.oz - 2, width=w, height=h, paddingCells=0, fileName=full, rootSize=max(h, w * 9.0 / 16.0) / 2.0)
        src = res.get("filePath") or res.get("path") or res.get("savedPath")
        for _ in range(40):
            if src and os.path.exists(src) and os.path.getsize(src) > 0:
                break
            time.sleep(0.5)
        time.sleep(1.0)
        if src and os.path.exists(src):
            shutil.copyfile(src, os.path.join(SHOTS, full + ".png"))
        print(name, json.dumps({k: v for k, v in self.B.probe("census").items() if k in ("pieces", "strands", "pending", "terminals", "edges")}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--look", default="Modern")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    R = Grow()
    R.go(a.tag, a.look, a.fresh_map)
    if R.notes:
        print("NOTES (%d):\n  %s" % (len(R.notes), "\n  ".join(R.notes[:30])))


if __name__ == "__main__":
    main()
