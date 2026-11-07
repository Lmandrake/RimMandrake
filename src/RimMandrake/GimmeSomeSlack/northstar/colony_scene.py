#!/usr/bin/env python3
"""colony_scene.py -- the same small colony built four times, once per look, for judging at play zoom.

    python.exe src/RimMandrake/GimmeSomeSlack/northstar/colony_scene.py --build [--fresh-map]
    python.exe src/RimMandrake/GimmeSomeSlack/northstar/colony_scene.py --shots TAG [--looks Modern,Scrapper] [--frames house,yard]

The proof's boards are bare soil and test lines. This is what a player builds: a walled house and a battery shed on a
conduit run from a solar field, a dense yard of conduit, a run cut by accident, masts out to a far hut with one span down,
and a second run in another look beside the first. Every piece goes through the real style machinery (AerialProbe cplace).
Shots land in D:\\ClaudeWork\\rimmandrake\\ralph_gss\\shots\\ at the play zoom (64 px per cell).
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "northstar_matrix"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import run_live as RL  # noqa: E402

SHOTS = r"D:\ClaudeWork\rimmandrake\ralph_gss\shots"
LOOKS = ("Modern", "Scrapper", "Industrial", "Futuristic")
KEY = {"Scrapper": "Scrapper", "Industrial": "Industrial", "Modern": "Modern_Multi", "Futuristic": "Futuristic"}
OTHER = {"Modern": "Scrapper", "Scrapper": "Modern", "Industrial": "Futuristic", "Futuristic": "Industrial"}
ORIGINS = {"Modern": (10, 10), "Scrapper": (140, 10), "Industrial": (10, 165), "Futuristic": (140, 165)}
W, H = 74, 40
# name: (x, z, w, h), local cells. 30x17 cells is one 1920x1080 frame at 64 px per cell.
FRAMES = {"house": (6, 2, 30, 17), "workshop": (7, 3, 15, 9), "shed": (20, 3, 22, 13), "yard": (22, 12, 18, 13), "cut": (22, -2, 12, 9),
          "masts": (28, 14, 30, 17), "fallen": (44, 2, 30, 17), "pair": (34, 4, 30, 17), "all": (0, 0, 74, 40)}


def line(x0, z0, x1, z1):
    if x0 == x1:
        return [(x0, z) for z in range(min(z0, z1), max(z0, z1) + 1)]
    return [(x, z0) for x in range(min(x0, x1), max(x0, x1) + 1)]


def perimeter(x0, z0, x1, z1, gaps=()):
    cells = line(x0, z0, x1, z0) + line(x0, z1, x1, z1) + line(x0, z0, x0, z1) + line(x1, z0, x1, z1)
    return [c for c in sorted(set(cells)) if c not in gaps]


def plan():
    """Local cells. The main run: solar field -> battery shed -> yard -> house, each branch ending in a machine."""
    door1, door2, door3 = (16, 4), (16, 11), (28, 7)
    p = {"walls": perimeter(8, 4, 24, 16, (door1,)) + [c for c in line(16, 4, 16, 16) if c not in (door1, door2)]
         + perimeter(28, 6, 33, 12, (door3,)) + perimeter(50, 24, 56, 30, ((50, 27),)),
         "doors": [(door1, 0), (door2, 1), (door3, 1), ((50, 27), 1)]}
    main = line(35, 5, 35, 13) + line(25, 9, 35, 9) + line(9, 9, 24, 9)     # field, through the shed, across the yard, into the house
    main += line(20, 6, 20, 14) + line(12, 6, 12, 14)                      # a + in each room
    main += line(26, 9, 26, 14) + [(x, z) for x in range(26, 31) for z in range(15, 20)]   # the yard's dense block
    main += line(31, 19, 31, 20)                                           # the first mast's foot onto the block
    main += line(26, 3, 26, 8)                                             # south spur, cut at z=2
    p["main"] = sorted(set(main))
    p["cutoff"] = line(26, -1, 26, 1)                                      # past the cut
    p["second"] = line(44, 22, 44, 27) + line(45, 27, 53, 27) + line(47, 24, 47, 26)   # the other look, its own battery
    p["machines"] = [("ElectricStove", (10, 13), 0, None), ("ElectricTailoringBench", (13, 6), 0, None), ("HiTechResearchBench", (21, 13), 0, None),
                     ("TubeTelevision", (18, 15), 2, None), ("Heater", (18, 6), None, None), ("StandingLamp", (14, 14), None, None),
                     ("StandingLamp", (22, 6), None, None), ("StandingLamp", (10, 6), None, None), ("CommsConsole", (22, 11), 1, None),
                     ("Bed", (14, 11), 0, "WoodLog")]
    p["batteries"] = [((30, 10), 0), ((32, 10), 0)]
    p["solar"] = [(38, 6), (38, 12)]
    p["far_end"] = ("StandingLamp", (26, -2))
    p["second_machines"] = [("Battery", (43, 21), 0), ("StandingLamp", (54, 25), None), ("Heater", (47, 23), None), ("StandingLamp", (52, 29), None)]
    p["masts"] = [("RM_AerialMast", (31, 21)), ("RM_AerialMast", (48, 19)), ("RM_AerialLampMast", (62, 22)), ("RM_AerialMast", (62, 8))]
    p["links"] = [(0, 1), (1, 2), (2, 3)]
    p["cuts"] = [(2, 3)]
    p["hut_lamp"] = ("StandingLamp", (64, 8))
    return p


class Scene(object):
    def __init__(self):
        self.B = RL.LiveBridge()
        self.notes = []

    def call(self, tool, **kw):
        r = self.B.call(tool, **kw)
        if r.get("success") is False:
            self.notes.append("%s: %s" % (tool, json.dumps(r)[:200]))
        return r

    def ap(self, cmd):
        r = self.B.ap(cmd)
        if not r.get("success"):
            self.notes.append("%s: %s" % (cmd, json.dumps(r)[:200]))
        return r

    def calm(self):
        self.call("jawa/weather_set", weather="Clear", lockWeather=True)
        self.call("jawa/incident_queue_clear")
        self.call("jawa/storyteller_swap", difficultyDef="Peaceful")
        self.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        self.call("jawa/research_bulk", mode="finish_all")
        self.call("rimworld/set_god_mode", enabled=True)
        self.call("jawa/screenshot_mode", enabled=False)

    def site(self, ox, oz):
        r = "%d,%d,%d,%d" % (ox - 2, oz - 4, W + 4, H + 6)
        self.call("jawa/destroy_batch", rects=r, categories="All")
        self.call("jawa/set_terrain_batch", ops="Soil:" + r, clearOverlays=True)
        self.call("jawa/set_fog", action="unfog", rect=r)
        self.call("jawa/set_roof_batch", ops="None:" + r)
        self.call("jawa/set_terrain_batch", ops="WoodPlankFloor:%d,%d,17,13;PavedTile:%d,%d,6,7;MetalTile:%d,%d,7,7" % (
            ox + 8, oz + 4, ox + 28, oz + 6, ox + 50, oz + 24))

    def batch(self, d, cells, ox, oz, rot=None, stuff=None):
        kw = {"ops": ";".join("%s:%d,%d%s" % (d, c[0] + ox, c[1] + oz, "" if rot is None else ",%d" % rot) for c in cells), "wipeExisting": False}
        if stuff:
            kw["stuff"] = stuff
        r = self.call("jawa/build_batch", **kw)
        if r.get("survived") != len(cells):
            self.notes.append("build %s %s/%d %s" % (d, r.get("survived"), len(cells), (r.get("failed") or [])[:2]))

    def colony(self, look):
        ox, oz = ORIGINS[look]
        p = plan()
        self.site(ox, oz)
        self.batch("Wall", p["walls"], ox, oz, stuff="Steel")
        for c, rot in p["doors"]:
            self.batch("Door", [c], ox, oz, rot=rot, stuff="Steel")
        key, okey = KEY[look], KEY[OTHER[look]]
        self.ap("clearpicks")
        self.ap("cclearpicks")
        self.ap("set:autoLink=False")                  # the spans are the plan's: a real player would see these three
        for c in p["main"]:
            self.ap("cplace:PowerConduit:%s:%d,%d:god" % (key, c[0] + ox, c[1] + oz))
            if key.endswith("_Multi"):
                self.ap("cprocess")
        for c in p["cutoff"]:
            self.ap("cplace:PowerConduit:%s:%d,%d:god" % (key, c[0] + ox, c[1] + oz))
        for c in p["second"]:
            self.ap("cplace:PowerConduit:%s:%d,%d:god" % (okey, c[0] + ox, c[1] + oz))
        self.ap("cprocess")
        for d, c, rot, stuff in p["machines"]:
            self.batch(d, [c], ox, oz, rot=rot, stuff=stuff)
        for c, rot in p["batteries"]:
            self.batch("Battery", [c], ox, oz, rot=rot)
        self.batch("SolarGenerator", p["solar"], ox, oz)
        self.batch(p["far_end"][0], [p["far_end"][1]], ox, oz)
        self.batch(p["hut_lamp"][0], [p["hut_lamp"][1]], ox, oz)
        for d, c, rot in p["second_machines"]:
            self.batch(d, [c], ox, oz, rot=rot)
        for d, c in p["masts"]:
            self.ap("place:%s:%s:%d,%d:god" % (d, look, c[0] + ox, c[1] + oz))
        self.ap("cprocess")
        self.B.ticks(2)
        self.ap("set:autoLink=True")
        apos = {(a["x"], a["z"]): a["id"] for a in self.B.ap("census").get("anchors") or []}
        ids = [apos.get((c[0] + ox, c[1] + oz)) for _, c in p["masts"]]
        for a, b in p["links"]:
            self.ap("link:%d,%d" % (ids[a], ids[b]))
        self.B.ticks(2)
        for a, b in p["cuts"]:
            self.ap("cut:%d,%d" % (ids[a], ids[b]))
        rect = "%d,%d,%d,%d" % (ox - 2, oz - 4, W + 4, H + 6)
        for t in self.B.call("jawa/list_things", defName="Battery", rect=rect, limit=50).get("things") or []:
            self.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=1.0)
        self.call("jawa/paint_area", area="BuildRoof", ops=rect, value=False)
        self.call("jawa/paint_area", area="Home", ops=rect, value=False)

    def colonists(self, looks):
        pawns = [q for q in self.B.call("jawa/list_pawns").get("pawns") or [] if q.get("isPlayer") and q.get("kind") == "Colonist"]
        ox, oz = ORIGINS[looks[0]]
        for q, s in zip(pawns, [(14, 8), (40, 20), (20, 11)]):           # under the span, in the workshop, in the rec room
            pid = int("".join(ch for ch in str(q["id"]) if ch.isdigit()))
            self.B.probe("pawn:%d=tp:%d,%d" % (pid, s[0] + ox, s[1] + oz))
            self.B.probe("pawn:%d=draft" % pid)

    def noon(self):
        mi = self.B.call("jawa/map_info")
        clk = self.B.call("jawa/time_clock")
        local = (clk["ticksAbs"] + int(round(mi.get("longitude", 0) / 360.0 * 60000))) % 60000
        add = (12 * 2500 - local) % 60000
        if add:
            self.call("jawa/time_set_ticks", ticks=clk["ticksGame"] + add, timeException=True)

    def shot(self, tag, look, frame, rect=None, px=64.0):
        ox, oz = ORIGINS[look]
        x, z, w, h = rect or FRAMES[frame]
        name = "%s_%s_%s" % (tag, look, frame)
        self.B.call("jawa/clear_ui", all=True)
        res = self.B.call("rimworld/screenshot_cell_rect", x=x + ox, z=z + oz, width=w, height=h, paddingCells=0, fileName=name,
                          rootSize=max(h, w * 9.0 / 16.0) / 2.0)
        src = res.get("filePath") or res.get("path") or res.get("savedPath")
        for _ in range(40):
            if src and os.path.exists(src) and os.path.getsize(src) > 0:
                break
            time.sleep(0.5)
        time.sleep(1.0)
        os.makedirs(SHOTS, exist_ok=True)
        if src and os.path.exists(src):
            dst = os.path.join(SHOTS, name + ".png")
            shutil.copyfile(src, dst)
            print(dst)
        else:
            print("SHOT FAILED %s %s" % (name, json.dumps(res)[:300]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--looks", default=",".join(LOOKS))
    ap.add_argument("--shots", default=None, help="capture name tag: use a new one each time, the writer is asynchronous")
    ap.add_argument("--frames", default="house,yard,cut,fallen")
    ap.add_argument("--rect", default=None, help="x,z,w,h local cells, with --frames naming it")
    ap.add_argument("--save", default=None)
    a = ap.parse_args()
    S = Scene()
    looks = a.looks.split(",")
    if a.fresh_map:
        S.B.call("rimworld/go_to_main_menu")
        S.B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        from await_lifecycle import await_lifecycle
        lc = await_lifecycle(S.B.call, "map_ready", 240, poll_s=0.5)
        if not lc.ok:
            raise SystemExit("no fresh map: %s" % lc.reason)
    if a.build:
        S.calm()
        for look in looks:
            S.colony(look)
            print("built %s" % look)
        S.colonists(looks)
        S.call("jawa/map_commit")
        S.B.ticks(400)                                     # a fresh consumer reads off for ~170 ticks, and the live ends poll at 250
        S.B.probe("rebuild")
        S.noon()
        S.B.call("rimworld/set_god_mode", enabled=False)
        print("census", json.dumps({k: v for k, v in S.B.probe("census").items() if isinstance(v, (int, str, bool))})[:400])
    if a.save:
        S.call("rimworld/save_game", saveName=a.save)
    if a.shots:
        rect = tuple(int(v) for v in a.rect.split(",")) if a.rect else None
        for look in looks:
            for f in a.frames.split(","):
                S.shot(a.shots, look, f, rect)
    if S.notes:
        print("NOTES (%d):\n  %s" % (len(S.notes), "\n  ".join(S.notes[:40])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
