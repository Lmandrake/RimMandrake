#!/usr/bin/env python3
"""The 0.2.0 live checks sc_restyle_whole_line, sc_look_menu_icons and sc_wall_lamp_looks (northstar/scene_rows.py) against a fake game, offline.

A live check that has only ever been run on a good game proves nothing. Here a fake bridge plays the game: it keeps the things the scenes
build (cords, a switch, poles, a wall bracket, standing and wall lamps), the overhead spans and their cut state, each piece's look, and the
master switch, and answers the probe verbs the scenes use (cplace, cline, crestyleone, crestyle, clamp, link, cut, cstyles, clookicons,
set:enabled). On the shipped behaviour every row that a program decides must PASS (a capture row stays UNMEASURED for its judge); on each
planted wrong game at least one row must FAIL; on a probe that cannot answer, no row may read PASS. Exit 0 PASS, 1 FAIL.

    python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_look_scenes.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "northstar"))
import scene_rows as S  # noqa: E402

MEMBERS = {"PowerConduit", "PowerSwitch", "RM_AerialMast", "RM_AerialWallBracket"}
LAMPS = {"StandingLamp", "WallLamp"}
ANCHORS = {"RM_AerialMast", "RM_AerialWallBracket"}
LOOKS = S.LOOK_NAMES


class Fake:
    """A game with GSS's run rule. `plant` names one wrong behaviour; `blind` makes every probe answer fail."""

    def __init__(self, plant=None, blind=False):
        self.plant, self.blind = plant, blind
        self.things, self.spans, self.next, self.enabled = {}, {}, 1, True

    # ---- building
    def add(self, d, x, z, look=None, rot=0):
        if d not in MEMBERS | LAMPS:
            return None
        t = {"id": self.next, "def": d, "x": x, "z": z, "look": look, "rot": rot}
        self.things[self.next] = t
        self.next += 1
        # a new pole or bracket links itself to the nearest anchor in range, as the mod's own auto-link does (in-game visit 1 of 0.2.0: the
        # first pole linked itself to the bracket too, so the cut of the poles' span left the line whole)
        if d in ANCHORS:
            for o in [u for u in self.things.values() if u["def"] in ANCHORS and u is not t]:
                self.spans[(o["id"], t["id"])] = True
        return t

    def call(self, tool, **k):
        if tool == "jawa/build_batch":
            for op in k.get("ops", "").split(";"):
                d, _, xz = op.partition(":")
                v = [int(n) for n in xz.split(",")]
                self.add(d, v[0], v[1], None, v[2] if len(v) > 2 else 0)
        return {"success": True}

    def ticks(self, n):
        pass

    def at(self, x, z, kinds):
        return next((t for t in self.things.values() if (t["x"], t["z"]) == (x, z) and t["def"] in kinds), None)

    # ---- the run rule
    def run_of(self, seed):
        seen, todo = {seed["id"]}, [seed]
        while todo:
            t = todo.pop()
            for u in self.things.values():
                if u["def"] not in MEMBERS or u["id"] in seen:
                    continue
                if abs(u["x"] - t["x"]) + abs(u["z"] - t["z"]) <= 1:
                    seen.add(u["id"]); todo.append(u)
            if self.plant != "stops_at_pole":
                for (a, b), up in self.spans.items():
                    if (up or self.plant == "crosses_cut") and t["id"] in (a, b):
                        o = self.things[b if t["id"] == a else a]
                        if o["id"] not in seen:
                            seen.add(o["id"]); todo.append(o)
        return [self.things[i] for i in sorted(seen)]

    def hooked(self, lamp, run):
        if lamp["def"] == "WallLamp" and self.plant == "wall_lamp_not_a_lamp":
            return False
        return any(abs(m["x"] - lamp["x"]) + abs(m["z"] - lamp["z"]) <= 1 for m in run)

    def drawn(self, lamp):
        if lamp["def"] == "WallLamp" and (not self.enabled and self.plant != "master_off_ignored" or lamp["look"] is None):
            return "Things/Building/Furniture/WallLamp/WallLamp"
        if lamp["look"] is None:
            return "Things/Building/Furniture/LampStanding"
        art = "StandingLamp" if self.plant == "wall_lamp_standing_art" else lamp["def"]
        return "RimMandrake/GimmeSomeSlack/Styles/%s/%s" % (lamp["look"], art)

    # ---- probes
    def probe(self, cmd):
        if self.blind:
            return {"success": False, "error": "probe down"}
        if cmd.startswith("set:enabled="):
            self.enabled = cmd.endswith("True")
            return {"success": True}
        return {"success": True}

    def ap(self, cmd):
        if self.blind:
            return {"success": False, "error": "probe down"}
        verb, _, rest = cmd.partition(":")
        p = rest.split(":")

        def cell(s):
            x, z = s.split(",")
            return int(x), int(z)
        if verb in ("cplace", "clamp") and self.plant == "wall_lamp_not_a_lamp":
            # the mod without WallLamp in its lamp list: the picker refuses it by name, and cstyles never lists it
            if verb == "cplace" and p[0] == "WallLamp":
                return {"success": False, "error": "not a stage-2 styled def: WallLamp"}
            if verb == "clamp" and self.at(*cell(p[0]), {"WallLamp"}):
                return {"success": False, "error": "no styled floor lamp there"}
        if verb == "cplace":
            t = self.add(p[0], *cell(p[2]), look=p[1])
            return {"success": t is not None}
        if verb == "cline":
            (x0, z0), (x1, z1) = cell(p[2]), cell(p[3])
            for x in range(min(x0, x1), max(x0, x1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.add(p[0], x, z, look=p[1])
            return {"success": True}
        if verb == "link":
            a, b = (int(v) for v in rest.split(","))
            self.spans[(a, b)] = True
            return {"success": True}
        if verb == "cut":
            a, b = (int(v) for v in rest.split(","))
            ok = (a, b) in self.spans
            if ok:
                self.spans[(a, b)] = False
            return {"success": True, "done": ok}
        if verb == "unlink":
            a, b = (int(v) for v in rest.split(","))
            return {"success": True, "done": self.spans.pop((a, b), self.spans.pop((b, a), None)) is not None}
        if verb == "census":
            return {"success": True, "anchors": [{"id": t["id"], "links": [{"other": b if t["id"] == a else a, "state": "Up" if up else "Cut"}
                    for (a, b), up in self.spans.items() if t["id"] in (a, b)]} for t in self.things.values() if t["def"] in ANCHORS]}
        if verb == "crestyleone":
            t = self.at(*cell(p[0]), MEMBERS)
            if t:
                t["look"] = p[1]
            return {"success": t is not None, "changed": int(t is not None)}
        if verb == "crestyle":
            t = self.at(*cell(p[0]), MEMBERS)
            if not t:
                return {"success": False, "error": "no run member there"}
            run = self.run_of(t)
            before = {m["look"] or "Scrapper" for m in run}
            for m in run:
                m["look"] = p[1]
            if self.plant != "lamps_never_follow":
                for l in self.things.values():
                    if l["def"] in LAMPS and self.hooked(l, run) and (l["look"] is None or l["look"] in before):
                        l["look"] = p[1]
            return {"success": True, "changed": len(run)}
        if verb == "clamp":
            t = self.at(*cell(p[0]), LAMPS)
            if t:
                t["look"] = p[1]
            return {"success": t is not None}
        if verb == "cstyles":
            x, z, w, h = (int(v) for v in rest.split(","))
            inside = [t for t in self.things.values() if x <= t["x"] < x + w and z <= t["z"] < z + h]
            members = []
            for t in inside:
                if t["def"] in MEMBERS:
                    members.append(dict(t, run=min(m["id"] for m in self.run_of(t))))
            lamps = [dict(t, drawnPath=self.drawn(t)) for t in inside if t["def"] in LAMPS
                     and not (t["def"] == "WallLamp" and self.plant == "wall_lamp_not_a_lamp")]
            return {"success": True, "members": members, "lamps": lamps}
        if verb == "clookicons":
            t = self.at(*cell(p[0]), MEMBERS | LAMPS)
            if not t:
                return {"success": False, "error": "nothing there"}
            entries = []
            menus = (["build"] if t["def"] != "RM_AerialMast" else []) + ["restyle This item", "restyle All connected", "restyle All on map"]
            for menu in menus:
                for look in LOOKS:
                    icon = look
                    if self.plant == "strand_icon" and look == "Modern" and menu == "restyle All connected":
                        icon = "Strand_Orange"
                    entries.append({"menu": menu, "label": look, "look": look, "icon": icon, "lookIcon": icon == look})
                if t["def"] in LAMPS and menu == "restyle This item":
                    entries.append({"menu": menu, "label": "Match its cable run", "look": None, "icon": None, "lookIcon": False})
            return {"success": True, "entries": entries}
        return {"success": True}


class V:
    """The validation module's parts the scenes call: ops, a row writer, frame_fit and shot."""

    @staticmethod
    def ops(d, cells, rot=None):
        return ";".join("%s:%d,%d%s" % (d, c[0], c[1], "" if rot is None else ",%d" % rot) for c in cells)

    @staticmethod
    def row(rows, rid, status, cls, detail):
        rows.append({"id": rid, "status": status, "class": cls, "detail": detail})

    @staticmethod
    def frame_fit(B, rect):
        pass

    @staticmethod
    def shot(B, name, rect, log):
        return "/fake/%s.png" % name


SCENES = [("restyle_whole_line", S.RESTYLE_LINE_ROWS, lambda B, rows: S.restyle_whole_line(B, V, rows)),
          ("look_menu_icons", S.LOOK_ICON_ROWS, lambda B, rows: S.look_menu_icons(B, V, rows, [])),
          ("wall_lamp_looks", S.WALL_LAMP_ROWS, lambda B, rows: S.wall_lamp_looks(B, V, rows, []))]
# each planted wrong game, and the scene that must catch it
PLANTS = [("stops_at_pole", "restyle_whole_line"), ("crosses_cut", "restyle_whole_line"), ("lamps_never_follow", "restyle_whole_line"),
          ("lamps_never_follow", "wall_lamp_looks"), ("wall_lamp_not_a_lamp", "wall_lamp_looks"), ("wall_lamp_standing_art", "wall_lamp_looks"),
          ("master_off_ignored", "wall_lamp_looks"), ("strand_icon", "look_menu_icons")]


def play(name, plant=None, blind=False):
    fn = next(f for n, _, f in SCENES if n == name)
    rows = []
    fn(Fake(plant, blind), rows)
    return {r["id"]: r for r in rows}


def main():
    fails = []
    for name, want, _ in SCENES:
        got = play(name)
        missing = [w for w in want if w not in got]
        if missing:
            fails.append("%s: rows not written: %s" % (name, missing))
        decided = {k: r["status"] for k, r in got.items() if r["class"] != "LOOK"}
        bad = {k: (s, got[k]["detail"]) for k, s in decided.items() if s != "PASS"}
        print("good game, %s: %d rows decided by the program, %d not PASS; capture rows %s" % (
            name, len(decided), len(bad), sorted(k for k, r in got.items() if r["class"] == "LOOK")))
        for k, v in bad.items():
            fails.append("good game, %s: %s reads %s (%s)" % (name, k, v[0], v[1]))
        looks = [k for k, r in got.items() if r["class"] == "LOOK" and r["status"] != "UNMEASURED"]
        if looks:
            fails.append("%s: a capture row decided itself: %s" % (name, looks))
        blind = play(name, blind=True)
        passed = [k for k, r in blind.items() if r["status"] == "PASS"]
        print("blind probe, %s: %d rows, %d PASS (limit 0)" % (name, len(blind), len(passed)))
        if passed:
            fails.append("blind probe, %s: rows read PASS with no answer: %s" % (name, passed))
    for plant, name in PLANTS:
        got = play(name, plant)
        red = sorted(k for k, r in got.items() if r["status"] == "FAIL")
        print("planted %s, %s: FAIL rows %s" % (plant, name, red or "none"))
        if not red:
            fails.append("planted %s was not caught by %s" % (plant, name))
    for f in fails:
        print("FAIL " + f)
    print("PASS" if not fails else "FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
