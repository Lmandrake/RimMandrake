#!/usr/bin/env python3
"""A base on an untouched generated map, built the way a player lays one out, then PLAYED: colonists free, stockpiles full, real blast cuts.

    python.exe ralph/live/lived_in.py build --look Modern [--fresh-map]
    python.exe ralph/live/lived_in.py play --ticks 6000
    python.exe ralph/live/lived_in.py blast
    python.exe ralph/live/lived_in.py shots TAG [--frames all,house,...]

Unlike colony_scene.py nothing is flattened: the ground, the plants and the trees are the generator's, and only what a building stands on is cleared.
"""
import argparse, json, os, shutil, sys, time
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "northstar"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "northstar_matrix"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import run_live as RL  # noqa: E402

SHOTS = r"D:\ClaudeWork\rimmandrake\ralph_gss\shots"
KEY = {"Scrapper": "Scrapper", "Industrial": "Industrial", "Modern": "Modern_Multi", "Futuristic": "Futuristic"}
STATE = "ralph/live/lived_state.json"
SPAN_W, SPAN_H = 76, 26
FRAMES = {"all": (-3, -6, 80, 30), "house": (-2, -3, 30, 20), "kitchen": (0, 0, 16, 10), "rec": (13, 0, 13, 11), "beds": (0, 9, 26, 8),
          "work": (26, -2, 18, 12), "yard": (24, 9, 26, 12), "span": (36, -6, 40, 18), "cutspan": (46, -6, 26, 16), "stock": (-2, -9, 26, 14), "spanpawn": (40, -3, 14, 9)}


def line(x0, z0, x1, z1):
    if x0 == x1:
        return [(x0, z) for z in range(min(z0, z1), max(z0, z1) + 1)]
    return [(x, z0) for x in range(min(x0, x1), max(x0, x1) + 1)]


def perimeter(x0, z0, x1, z1):
    return sorted(set(line(x0, z0, x1, z0) + line(x0, z1, x1, z1) + line(x0, z0, x0, z1) + line(x1, z0, x1, z1)))


def plan():
    doors = [(19, 0), (0, 5), (3, 10), (9, 10), (15, 10), (21, 10), (14, 3), (28, 4), (30, 11)]
    walls = perimeter(0, 0, 24, 15) + line(0, 10, 24, 10) + line(6, 10, 6, 15) + line(12, 10, 12, 15) + line(18, 10, 18, 15) + line(14, 0, 14, 10) \
        + perimeter(28, 0, 38, 9) + perimeter(28, 11, 34, 17)
    walls = sorted(set(c for c in walls if c not in doors))
    conduit = line(35, 13, 44, 13) + line(29, 13, 34, 13) + line(25, 13, 28, 13) + line(1, 13, 24, 13) \
        + line(13, 1, 13, 12) + line(2, 5, 12, 5) + line(14, 7, 22, 7) \
        + line(26, 5, 26, 12) + line(27, 5, 37, 5) + line(38, 5, 39, 5) + line(39, 3, 39, 4)
    machines = [("ElectricStove", (3, 7), 0, None), ("TableButcher", (8, 7), 0, "Steel"), ("StandingLamp", (6, 3), None, None), ("Heater", (11, 2), None, None),
                ("Table2x2c", (18, 3), None, "WoodLog"), ("DiningChair", (17, 3), 1, "WoodLog"), ("DiningChair", (20, 3), 3, "WoodLog"),
                ("TubeTelevision", (20, 8), 2, None), ("ChessTable", (16, 8), None, "WoodLog"), ("StandingLamp", (22, 2), None, None), ("HorseshoesPin", (22, 5), None, None),
                ("Bed", (3, 12), 0, "WoodLog"), ("Bed", (9, 12), 0, "WoodLog"), ("Bed", (15, 12), 0, "WoodLog"), ("Bed", (21, 12), 0, "WoodLog"),
                ("StandingLamp", (1, 11), None, None), ("StandingLamp", (10, 14), None, None), ("StandingLamp", (17, 14), None, None), ("StandingLamp", (23, 14), None, None),
                ("ElectricSmithy", (31, 7), 0, None), ("ElectricTailoringBench", (35, 7), 0, None), ("HiTechResearchBench", (33, 2), 2, None), ("StandingLamp", (37, 1), None, None),
                ("Battery", (30, 14), 0, None), ("Battery", (32, 14), 0, None), ("SolarGenerator", (41, 16), None, None), ("SolarGenerator", (46, 16), None, None), ("SolarGenerator", (41, 10), None, None)]
    masts = [("RM_AerialMast", (39, 2)), ("RM_AerialLampMast", (53, 1)), ("RM_AerialMast", (67, 2))]
    hut = [("StandingLamp", (70, 3)), ("Heater", (70, -2)), ("Battery", (72, 1))]
    hut_conduit = line(68, 2, 71, 2) + line(71, -1, 71, 3)
    return dict(doors=doors, walls=walls, conduit=sorted(set(conduit)), machines=machines, masts=masts, hut=hut, hut_conduit=hut_conduit)


class Run(object):
    def __init__(self):
        self.B = RL.LiveBridge()
        self.notes = []

    def call(self, tool, **kw):
        r = self.B.call(tool, **kw)
        if r.get("success") is False:
            self.notes.append("%s %s: %s" % (tool, json.dumps(kw)[:90], json.dumps(r)[:200]))
        return r

    def ap(self, cmd):
        r = self.B.ap(cmd)
        if not r.get("success"):
            self.notes.append("%s: %s" % (cmd, json.dumps(r)[:200]))
        return r

    def site(self):
        """The most open stretch of the generator's ground, read cell by cell. Natural water or rock in the margin is left alone."""
        best = None
        for oz in range(60, 170, 20):
            for ox in range(40, 150, 25):
                r = self.B.call("jawa/get_terrain_batch", rects="%d,%d,%d,%d" % (ox - 1, oz - 10, SPAN_W, SPAN_H))
                bad = 0
                for op in (r.get("ops") or "").split(";"):
                    if ":" not in op:
                        continue
                    t, q = op.split(":")
                    if "Rough" in t or "Water" in t or "Marsh" in t or "Mud" in t:
                        v = q.split(",")
                        bad += int(v[2]) * int(v[3])
                if best is None or bad < best[0]:
                    best = (bad, ox, oz)
        print("site", best)
        return best[1], best[2]

    def build(self, look, fresh):
        if fresh:
            self.B.call("rimworld/go_to_main_menu")
            self.B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
            from await_lifecycle import await_lifecycle
            lc = await_lifecycle(self.B.call, "map_ready", 240, poll_s=0.5)
            if not lc.ok:
                raise SystemExit("no fresh map: %s" % lc.reason)
        print("map", json.dumps({k: v for k, v in self.B.call("jawa/map_info").items() if k in ("mapBiome", "season", "tile")}))
        self.call("rimworld/set_god_mode", enabled=True)
        self.call("jawa/research_bulk", mode="finish_all")
        self.call("jawa/storyteller_swap", difficultyDef="Peaceful")
        self.call("jawa/incident_queue_clear")
        self.call("jawa/set_fog", action="unfog", rect="0,0,250,250")
        ox, oz = self.site()
        p = plan()
        key = KEY[look]

        def rect(x, z, w, h):
            return "%d,%d,%d,%d" % (ox + x, oz + z, w, h)

        def clear(cells):
            self.call("jawa/destroy_batch", rects=";".join("%d,%d,1,1" % (c[0] + ox, c[1] + oz) for c in cells), categories="Plant,Item,Filth,Building")

        def batch(d, cells, rot=None, stuff=None):
            kw = {"ops": ";".join("%s:%d,%d%s" % (d, c[0] + ox, c[1] + oz, "" if rot is None else ",%d" % rot) for c in cells), "wipeExisting": False}
            if stuff:
                kw["stuff"] = stuff
            r = self.call("jawa/build_batch", **kw)
            if r.get("survived") != len(cells):
                self.notes.append("build %s %s/%d %s" % (d, r.get("survived"), len(cells), json.dumps(r.get("failed") or [])[:200]))

        for r in (rect(-1, -1, 26, 17), rect(27, -1, 13, 19), rect(39, 8, 11, 12), rect(66, -3, 8, 8)):
            self.call("jawa/destroy_batch", rects=r, categories="Plant,Item,Filth,Building")
        self.call("jawa/set_terrain_batch", ops="WoodPlankFloor:%s;PavedTile:%s;WoodPlankFloor:%s;Concrete:%s" % (rect(1, 1, 23, 14), rect(1, 1, 13, 9), rect(29, 1, 9, 8), rect(29, 12, 5, 5)))
        batch("Wall", p["walls"], stuff="BlocksGranite")
        doors_rot = {(19, 0): 0, (0, 5): 1, (3, 10): 0, (9, 10): 0, (15, 10): 0, (21, 10): 0, (14, 3): 1, (28, 4): 1, (30, 11): 0}
        for c in p["doors"]:
            batch("Door", [c], rot=doors_rot[c], stuff="WoodLog")
        self.ap("clearpicks")
        self.ap("cclearpicks")
        self.ap("set:autoLink=False")
        self.call("jawa/destroy_batch", rects=";".join("%d,%d,1,1" % (c[0] + ox, c[1] + oz) for c in p["conduit"] + p["hut_conduit"]), categories="Plant,Item,Filth")
        for c in p["conduit"]:
            self.ap("cplace:PowerConduit:%s:%d,%d:god" % (key, c[0] + ox, c[1] + oz))
            if key.endswith("_Multi"):
                self.ap("cprocess")
        for c in p["hut_conduit"]:
            self.ap("cplace:PowerConduit:%s:%d,%d:god" % (key, c[0] + ox, c[1] + oz))
        self.ap("cprocess")
        for d, c, rot, stuff in p["machines"]:
            clear([c, (c[0] + 1, c[1]), (c[0], c[1] + 1), (c[0] + 1, c[1] + 1)] if d == "SolarGenerator" else [c])
            batch(d, [c], rot=rot, stuff=stuff)
        for d, c in p["hut"]:
            clear([c])
            batch(d, [c])
        for d, c in p["masts"]:
            clear([c])
            self.ap("place:%s:%s:%d,%d:god" % (d, look, c[0] + ox, c[1] + oz))
        self.ap("cprocess")
        self.B.ticks(2)
        self.ap("set:autoLink=True")
        apos = {(a["x"], a["z"]): a["id"] for a in self.B.ap("census").get("anchors") or []}
        ids = [apos.get((c[0] + ox, c[1] + oz)) for _, c in p["masts"]]
        print("masts", ids)
        for a, b in ((0, 1), (1, 2)):
            self.ap("link:%d,%d" % (ids[a], ids[b]))
        self.call("jawa/set_roof_batch", ops="RoofConstructed:%s;RoofConstructed:%s;RoofConstructed:%s" % (rect(1, 1, 23, 14), rect(29, 1, 9, 8), rect(29, 12, 5, 5)))
        # what a colony owns: a stockpile out front, full; a growing plot; food in the kitchen
        self.call("jawa/map_zones", action="createZone", zoneType="Stockpile", rect=rect(0, -8, 20, 6))
        self.call("jawa/map_zones", action="createZone", zoneType="Growing", plant="Plant_Rice", rect=rect(27, -9, 12, 6))
        for d, x, z in (("Steel", 1, -7), ("Steel", 3, -7), ("WoodLog", 5, -7), ("WoodLog", 7, -7), ("Cloth", 9, -7), ("ComponentIndustrial", 11, -7), ("BlocksGranite", 13, -7), ("BlocksGranite", 15, -6),
                        ("WoodLog", 1, -4), ("Steel", 6, -4), ("RawPotatoes", 9, -4), ("RawCorn", 12, -4), ("MedicineIndustrial", 15, -4), ("MealSimple", 3, 2), ("MealSimple", 4, 2), ("MealSimple", 5, 2), ("MealSimple", 16, 2)):
            self.call("jawa/spawn_batch", ops="%s:%d,%d" % (d, x + ox, z + oz))
        rc = rect(-1, -9, SPAN_W, 26)
        for t in self.B.call("jawa/list_things", defName="Battery", rect=rc, limit=50).get("things") or []:
            self.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=1.0)
        self.call("jawa/paint_area", area="Home", ops=rect(-3, -10, 80, 30), value=True)
        self.call("jawa/map_commit")
        self.B.ticks(300)
        self.B.probe("rebuild")
        self.call("rimworld/set_god_mode", enabled=False)
        json.dump({"ox": ox, "oz": oz, "look": look, "masts": ids}, open(STATE, "w"))
        c = self.B.probe("census")
        print("census", json.dumps({k: v for k, v in c.items() if isinstance(v, (int, str, bool))})[:400])

    def st(self):
        return json.load(open(STATE))

    def play(self, ticks, speed=3):
        """Real play: unpaused, colonists on their own schedules."""
        t0 = self.B.call("jawa/time_clock")["ticksGame"]
        self.call("rimworld/set_time_speed", speed=speed)
        end = time.time() + max(10, ticks / 150.0)
        while time.time() < end:
            time.sleep(3)
            if self.B.call("jawa/time_clock")["ticksGame"] - t0 >= ticks:
                break
        self.call("rimworld/set_time_speed", speed=0)
        t1 = self.B.call("jawa/time_clock")["ticksGame"]
        ps = [q for q in self.B.call("jawa/list_pawns").get("pawns") or [] if q.get("isPlayer")]
        print("played", t1 - t0, "ticks; colonists", len(ps), "downed", sum(1 for q in ps if q.get("downed")))

    def blast(self):
        """What a mortar does: one blast on a span, one on the yard trunk."""
        s = self.st()
        ox, oz = s["ox"], s["oz"]
        print(json.dumps(self.call("jawa/explosion_at", at="%d,%d" % (ox + 60, oz + 2), damType="Bomb", damAmount=40, radius=2.5))[:200])
        print(json.dumps(self.call("jawa/explosion_at", at="%d,%d" % (ox + 26, oz + 9), damType="Bomb", damAmount=40, radius=1.2))[:200])
        self.B.ticks(300)
        c = self.B.ap("census")
        print("anchors", json.dumps([{k: a.get(k) for k in ("id", "fallenLive")} | {"fallen": len(a.get("fallen") or [])} for a in c.get("anchors") or []]))

    def spanpawn(self):
        """Colonists standing under the live span between the first two masts, for overhead_span_above_everything."""
        s = self.st()
        # a span draws lifted: on screen its wires pass about 3 cells north of its ground line, so that is where a pawn stands under them
        for x, z in ((44, 5), (46, 4), (48, 4)):
            print(json.dumps(self.call("jawa/spawn_pawn", kindDef="Colonist", x=s["ox"] + x, z=s["oz"] + z, count=1, faction="PlayerColony"))[:120])
        self.B.ticks(2)

    def shots(self, tag, frames):
        s = self.st()
        out = []
        for f in frames:
            x, z, w, h = FRAMES[f]
            name = "%s_%s_%s" % (tag, s["look"], f)
            self.B.call("jawa/clear_ui", all=True)
            root = max(h, w * 9.0 / 16.0) / 2.0
            res = self.B.call("rimworld/screenshot_cell_rect", x=x + s["ox"], z=z + s["oz"], width=w, height=h, paddingCells=0, fileName=name, rootSize=root)
            src = res.get("filePath") or res.get("path") or res.get("savedPath")
            for _ in range(40):
                if src and os.path.exists(src) and os.path.getsize(src) > 0:
                    break
                time.sleep(0.5)
            time.sleep(1.0)
            if src and os.path.exists(src):
                shutil.copyfile(src, os.path.join(SHOTS, name + ".png"))
                out.append(name)
            else:
                print("SHOT FAILED", name, json.dumps(res)[:200])
        print("shots", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("tag", nargs="?")
    ap.add_argument("--look", default="Modern")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--ticks", type=int, default=6000)
    ap.add_argument("--frames", default="all,house,work,yard,span,stock")
    a = ap.parse_args()
    R = Run()
    if a.cmd == "build":
        R.build(a.look, a.fresh_map)
    elif a.cmd == "play":
        R.play(a.ticks)
    elif a.cmd == "blast":
        R.blast()
    elif a.cmd == "spanpawn":
        R.spanpawn()
    elif a.cmd == "shots":
        R.shots(a.tag, a.frames.split(","))
    if R.notes:
        print("NOTES (%d):\n  %s" % (len(R.notes), "\n  ".join(R.notes[:30])))


if __name__ == "__main__":
    main()
