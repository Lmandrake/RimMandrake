#!/usr/bin/env python3
"""The small scenes of RIMMANDRAKE_DECIDE_SLACK_WALK_BAR_CODE_PLAYS_NO_WEEK against a fake game, offline: save_wire_down.py
(sc_save_reload_wire_down), tap_goodwill.py (sc_tap_theft) and gravship_scene.py's reads (sc_gravship).

A live check that has only run on a good game proves nothing. On the shipped behaviour every row must read PASS; on each planted wrong
game the named row must read FAIL; on a game that cannot be read, or a scene that did not stage, no row may read PASS. The gravship case
runs the whole of gravship_scene.scene() with a fake bridge and a fake flight. It also holds scenes.json, the test table and the proof's
row lists together: sc_save_reload_wire_down keeps every row sc_walk was read from, and sc_walk is gone from all three.

    python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_small_scenes.py        exit 0 PASS, 1 FAIL
"""
import contextlib
import io
import json
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import gravship_scene as GS  # noqa: E402
import proof_leaves as PL  # noqa: E402
import save_wire_down as W  # noqa: E402
import tap_goodwill as TG  # noqa: E402
import validation as V  # noqa: E402
import validation_aerial as VA  # noqa: E402

N, FAILS = [0], []


def check(name, ok, detail=""):
    N[0] += 1
    if not ok:
        FAILS.append(name)
        print("FAIL  %s  %s" % (name, str(detail)[:300]))


def status(rows):
    return {r["id"]: r["status"] for r in rows}


# ------------------------------------------------------------------ save_wire_down
class WireGame:
    """The plot: whole or cut, with `plant` naming what the load (or the staging) does wrong."""

    def __init__(self, plant=None):
        self.plant, self.built, self.linked, self.floor_cut, self.span_cut, self.loaded = plant, False, False, False, False, False

    def call(self, tool, **k):
        if tool == "jawa/build_batch":
            self.built = True
        if tool == "jawa/destroy_batch" and k.get("categories") == "Building" and k["rects"] == "%d,%d,1,1" % W.FLOOR_CUT:
            self.floor_cut = self.plant != "floor not cut"
        return {"success": True, "things": []}

    def ticks(self, n):
        pass

    def ap(self, cmd):
        if cmd == "census":
            if self.plant == "blind":
                return {"success": False}
            st = "Cut" if self.span_cut else "Up"
            cut_live = {W.POLE_A: True, W.POLE_B: False}
            wrong_link = self.loaded and self.plant == "cut span loads whole"
            an = []
            for i, p in ((1, W.POLE_A), (2, W.POLE_B)):
                live = cut_live[p] if self.span_cut else None
                if self.loaded and self.plant == "fallen half loads dead":
                    live = False
                an.append({"id": i, "x": p[0], "z": p[1], "netLive": p == W.POLE_A or not self.span_cut, "fallenLive": live,
                           "fallen": [{}] if self.span_cut else [],
                           "links": [{"other": 3 - i, "state": "Up" if wrong_link else st}] if self.linked else []})
            if self.plant == "a pole is lost by the load" and self.loaded:
                an = an[:1]
            return {"success": True, "anchors": an if self.built else []}
        if cmd.startswith("link:"):
            self.linked = True
        if cmd.startswith("cut:"):
            self.span_cut = self.plant != "span not cut"
            return {"success": True, "done": self.span_cut}
        if cmd.startswith("net:"):
            at = tuple(int(v) for v in cmd[4:].split(","))
            on = not (self.floor_cut if at == W.FLOOR_LAMP else self.span_cut)
            if self.plant == "lamp dark when whole":
                on = False
            if self.loaded and self.plant == "lamp lit after the load" and at == W.FLOOR_LAMP:
                on = True
            return {"success": True, "things": [{"def": "StandingLamp", "powerOn": on}]}
        return {"success": True}

    def probe(self, cmd):
        if not cmd.startswith("rect:"):
            return {"success": True}
        if self.plant == "blind":
            return {"success": False}
        whole = not self.floor_cut
        cords = {"end:1|end:9": "a"} if whole else {"end:1|end:5": "a", "end:7|end:9": "b"}
        ends = [] if whole else [{"cell": list(W.FLOOR[5]), "registryLive": True, "netLive": True},
                                 {"cell": list(W.FLOOR[7]), "registryLive": False, "netLive": False}]
        out = {"success": True, "cordEdges": len(cords), "cordsAcrossNets": 0, "cordEndsWithoutNet": 0, "verticesInUnwalkable": 0}
        if self.loaded:
            if self.plant == "cut line draws whole":
                cords, ends = {"end:1|end:9": "a"}, []
            if self.plant == "a cord is lost":
                cords.pop("end:7|end:9", None)
            if self.plant == "cord joins two nets":
                out["cordsAcrossNets"] = 1
            if self.plant == "cord end on no net":
                out["cordEndsWithoutNet"] = 1
            if self.plant == "cord in a wall":
                out["verticesInUnwalkable"] = 2
            if self.plant == "dead end loads live":
                ends = [dict(e, registryLive=True) for e in ends]
            if self.plant == "an end is lost":
                ends = ends[:1]
        return dict(out, edgeHashes=cords, ends=ends)


class Clock:
    t = 0.0

    def __call__(self):
        return Clock.t

    @staticmethod
    def sleep(s):
        Clock.t += max(s, 0.5)


def wire_run(plant=None, blobs=None):
    B = WireGame(plant)
    W.stage(B, V)
    uncut = W.read(B, Clock.sleep)
    W.wire_down(B)
    before = W.read(B, Clock.sleep)
    B.loaded = True
    after = W.read_after_load(B, before, Clock.sleep, Clock())
    n = 2 if B.span_cut else 0
    blobs = blobs or (b"<x/>", b"<x/>" + W.CUT_MARK * n)
    rows = [(W.ROWS[0],) + W.control_row(uncut, *blobs)] + W.reload_rows(before, after)
    return {r[0]: (r[1], r[2]) for r in rows}, rows


C, G, E = W.ROWS
good, raw = wire_run()
check("wire: the shipped behaviour passes every row", {k: v[0] for k, v in good.items()} == {C: "PASS", G: "PASS", E: "PASS"}, raw)
WIRE_PLANTS = {"cut line draws whole": G, "a cord is lost": G, "cord joins two nets": G, "cord end on no net": G, "cord in a wall": G,
               "dead end loads live": E, "an end is lost": E, "fallen half loads dead": E, "cut span loads whole": E,
               "a pole is lost by the load": E, "lamp lit after the load": E}
for plant, rid in sorted(WIRE_PLANTS.items()):
    got, raw = wire_run(plant)
    check("wire planted: %s reads FAIL at %s" % (plant, rid), got[rid] == ("FAIL", "MOD"), raw)
for plant in ("blind", "floor not cut", "span not cut"):
    got, raw = wire_run(plant)
    check("wire: %s, no reload row passes" % plant, got[G][0] == got[E][0] == "UNMEASURED", raw)
got, raw = wire_run("lamp dark when whole")
check("wire: a scene that never stood whole cannot pass its control", got[C][0] == "UNMEASURED", raw)
got, raw = wire_run(None, (b"", b""))
check("wire control: a wire-down save that holds no more cut links than the uncut one reads FAIL", got[C][0] == "FAIL", raw)
got, raw = wire_run(None, (None, W.CUT_MARK * 2))
check("wire control: an unread uncut save is UNMEASURED", got[C][0] == "UNMEASURED", raw)
got, raw = wire_run(None, (W.CUT_MARK * 4, W.CUT_MARK * 6))
check("wire control: cuts left by other blocks are in both saves and do not stop it", got[C][0] == "PASS", raw)
B0 = WireGame()
W.stage(B0, V)
r0 = W.read(B0, Clock.sleep)
check("wire control: a comparison from before any cut is refused as not mid-way", len(W.compare(r0, r0)["refused"]) == 3, W.compare(r0, r0))


# ------------------------------------------------------------------ tap_goodwill
class TapGame:
    """A clamp, a victim faction, two others; the clamp's counter and the mod's rule at each 250-tick event."""
    PER = 2

    def __init__(self, plant=None):
        self.plant, self.drain, self.seen, self.witness, self.clamp = plant, 0, False, False, False
        self.gw = {"OutlanderCivil": 30, "Tribe": 10, "Pirate": -100}
        self.charged, self.caught_n = 0, 0

    def facs(self):
        return [{"defName": d, "name": d + "!", "goodwill": g, "hostile": g < -75, "isPlayer": False, "permanentEnemy": d == "Pirate", "hidden": False}
                for d, g in self.gw.items()] + [{"defName": "PlayerColony", "name": "us", "isPlayer": True, "goodwill": 0}]

    def call(self, tool, **k):
        if tool == "jawa/list_factions":
            if self.plant == "factions unreadable":
                return {"success": False}
            return {"success": True, "factions": self.facs()}
        if tool == "jawa/mod_settings_field":
            f = k["field"]
            vals = {"theftGoodwillPerDay": str(self.PER), "theftSightRange": "12", "theftGoodwill": "True", "goodwillCharged": str(self.charged),
                    "caughtCount": str(self.caught_n)}
            return {"success": True, "value": vals.get(f, "True")}
        if tool == "jawa/build_batch" and "RM_PowerTapClamp" in k.get("ops", ""):
            self.clamp = True
        if tool == "jawa/list_things":
            d = k.get("defName")
            if d == "RM_PowerTapClamp":
                return {"success": True, "things": [{"id": "RM_PowerTapClamp77", "x": 30, "z": 221}] if self.clamp else []}
            return {"success": True, "things": [{"id": "Battery5"}]}
        if tool == "jawa/destroy_batch":
            if k.get("rects", "").endswith(",1,1") and self.plant != "clamp not removed":
                self.clamp = False
            return {"success": True}
        if tool == "jawa/comp_set":
            if self.plant == "no comp_set tool":
                return {"success": False, "message": "no such tool"}
            was, self.drain = self.drain, int(k["value"])
            return {"success": True, "before": str(was), "after": str(self.drain)}
        if tool == "jawa/spawn_pawn":
            if self.plant == "no witness spawns":
                return {"success": True, "pawns": []}
            self.witness = True
            return {"success": True, "pawns": [{"id": "Human1"}, {"id": "Human2"}]}
        if tool == "jawa/pawn_census":
            far = 40 if self.plant == "witness walked off" else 0
            return {"success": True, "pawns": [{"id": "Human1", "faction": "OutlanderCivil", "x": 30 + far, "z": 226}] if self.witness else []}
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": 250, "sizeZ": 250}
        return {"success": True}

    def ap(self, cmd):
        if cmd == "census":
            return {"success": True, "anchors": [], "taps": [{"id": 77, "lastStolenW": 0 if self.plant == "clamp drains nothing" else 400}] if self.clamp else []}
        return {"success": True}

    def ticks(self, n):
        for _ in range(n // 250):
            self.event()

    def event(self):
        ghost = self.plant == "removed clamp still charges" and not self.clamp and self.drain >= TG.DAY
        if (not self.clamp and not ghost) or self.plant == "clamp drains nothing":
            return
        day, self.drain = self.drain >= TG.DAY, 0
        if not self.seen and self.plant != "charges unseen":
            near = self.witness and self.plant not in ("never catches", "witness walked off")
            if near or self.plant == "catches with nobody there":
                self.seen, self.caught_n = True, self.caught_n + 1
            return
        if not day:
            return
        cost = {"charges nothing": 0, "charges double": 4}.get(self.plant, self.PER)
        who = "Tribe" if self.plant == "charges the wrong faction" else "OutlanderCivil"
        self.gw[who] -= cost
        self.charged -= cost
        if self.plant == "a third faction falls too":
            self.gw["Tribe"] -= 1


def tap_run(plant=None):
    rows = []
    with contextlib.redirect_stdout(io.StringIO()):
        TG.run(TapGame(plant), V, rows, VA)
    return status(rows), rows


U, S, R = TG.ROWS
got, raw = tap_run()
check("tap: the shipped behaviour passes every row", got == {U: "PASS", S: "PASS", R: "PASS"}, raw)
for plant, rid in (("charges unseen", U), ("catches with nobody there", U), ("charges nothing", S), ("charges double", S), ("never catches", S),
                   ("charges the wrong faction", S), ("a third faction falls too", S), ("removed clamp still charges", R)):
    got, raw = tap_run(plant)
    check("tap planted: %s reads FAIL at %s" % (plant, rid), got[rid] == "FAIL", raw)
for plant in ("factions unreadable", "no comp_set tool", "clamp drains nothing"):
    got, raw = tap_run(plant)
    check("tap: %s, no row passes" % plant, set(got) == {U, S, R} and not [k for k, v in got.items() if v == "PASS"], raw)
for plant in ("no witness spawns", "witness walked off"):
    got, raw = tap_run(plant)
    check("tap: %s is the scene's, UNMEASURED, and the removal row cannot pass beside it" % plant, got[S] == "UNMEASURED" and got[R] == "UNMEASURED", raw)
got, raw = tap_run("clamp not removed")
check("tap: a clamp the script could not remove is UNMEASURED, never PASS", got[R] == "UNMEASURED", raw)


# ------------------------------------------------------------------ gravship_scene: the pure reads, then a whole flight
E1 = [("end:4,16|bend:8,16", (4, 16), (8, 16))]
check("ship: cord_edges reads the end cells out of the names", GS.cord_edges({"edgeHashes": {"end:4,16|bend:8,16": "x"}}) == E1)
check("ship: an edge name with no cells is a fault, never skipped", GS.true_to_grid(GS.cord_edges({"edgeHashes": {"odd": "x"}}), lambda c: 1) != [])
check("ship: one net is true to the grid", GS.true_to_grid(E1, lambda c: 5) == [])
check("ship planted: a cord joining two nets", GS.true_to_grid(E1, lambda c: c[0])[0][1] == "joins two nets")
check("ship planted: a cord end off the net", "outside the landed net" in GS.true_to_grid(E1, lambda c: None if c[0] == 8 else 1)[0][1])
check("ship: a lamp's own net stands in for its cell's", GS.cell_net({"success": True, "net": -1, "things": [{"net": -1}, {"net": 6}]}) == 6
      and GS.cell_net({"success": True, "net": -1, "things": []}) is None and GS.cell_net({"success": False, "net": 3}) is None)
check("ship planted: a lamp on another net than its battery", GS.true_to_grid([("k", (1, 1), (2, 2))], lambda c: GS.cell_net(
    {"success": True, "net": 5 if c == (2, 2) else -1, "things": [{"net": 8}]}))[0][1] == "joins two nets")
check("ship control: fails by name on the landed map", GS.control_verdict(E1, lambda c: None)[0] == "PASS")
check("ship control: a read that cannot fail is not a pass", GS.control_verdict(E1, lambda c: 1)[0] == "UNMEASURED")
check("ship control: no pre-launch cord is UNMEASURED", GS.control_verdict([], lambda c: None)[0] == "UNMEASURED")
AN = lambda aid, n: {"success": True, "anchors": [{"id": aid, "fallen": [{}] * n}]}
check("ship snap: a half lies at the ground anchor and one hangs from the ship's pole", GS.snap_verdict((0, 0), 1, 1)[0] == "PASS")
check("ship snap planted: the wire coiled (nothing fell anywhere)", GS.snap_verdict((0, 0), 0, 0)[0] == "FAIL")
check("ship snap planted: the ship keeps no half", GS.snap_verdict((0, 0), 1, 0)[0] == "FAIL")
check("ship snap: a count that could not be read is UNMEASURED, never 0", GS.snap_verdict((0, 0), None, 1)[0] == "UNMEASURED" and GS.fallen_of({"success": False}, 3) is None
      and GS.fallen_of(AN(4, 1), 3) is None and GS.fallen_of(AN(3, 1), 3) == 1)
check("ship: one net needs the battery and both consumers", GS.one_net([("b", 1), ("l", 1)])[0] is None and GS.one_net([("b", 1), ("l", 1), ("m", 1)])[0]
      and GS.one_net([("b", 1), ("l", 1), ("m", 2)])[0] is False and GS.one_net([("b", -1), ("l", -1), ("m", -1)])[0] is False)

FAKE_PROVE = "X, Z = 40, 50\ndef call(*a, **k):\n    return {}\n# -- 5. launch\nFLY()\n# -- 6. land\npass\nfor part in ():\n    pass\n"


class Ship:
    """The pad, then the landed map: every cell moves by MOVE, and every net gets a new id."""
    MOVE = (60, 30)

    def __init__(self, plant=None):
        if plant == "lands where it stood":
            self.MOVE = (0, 0)
        self.plant, self.at, self.things, self.links, self.auto, self.keep, self.landed = plant, {}, [], [], True, True, False

    def add(self, d, x, z):
        if self.plant == "one lamp" and d == "StandingLamp" and any(t[1] == d for t in self.things):
            return
        if self.plant == "brackets refused" and d == "RM_AerialWallBracket":
            return
        self.things.append([len(self.things) + 1, d, x, z])

    def fly(self):
        ground = [t for t in self.things if t[1] == "RM_AerialMast"][-1][0]
        ship = {t[0] for t in self.things if t[0] != ground}
        keep = self.keep if self.plant != "switch ignored" else not self.keep
        self.links = [q for q in self.links if set(q) <= ship and keep]
        if self.plant == "ground link kept":
            self.links.append((ground, [t[0] for t in self.things if t[1] == "RM_AerialMast"][0]))
        self.things = [[i, d, x + self.MOVE[0], z + self.MOVE[1]] for i, d, x, z in self.things if i in ship]
        if self.auto and self.plant == "re-strung on landing":
            br = [t[0] for t in self.things if t[1] == "RM_AerialWallBracket"]
            self.links.append(tuple(br))
        self.landed = True

    # the bridge
    def call(self, tool, **k):
        if tool == "jawa/build_batch":
            for op in k["ops"].split(";"):
                d, v = op.split(":")
                v = [int(q) for q in v.split(",")]
                self.add(d, v[0], v[1])
        if tool == "jawa/list_things":
            return {"success": True, "things": [{"id": "%s%d" % (d, i), "x": x, "z": z} for i, d, x, z in self.things if d == k["defName"]]}
        return {"success": True}

    def ticks(self, n):
        pass

    def conduit(self):
        return sorted((x, z) for _, d, x, z in self.things if d == "PowerConduit")

    def net(self, d):
        if d not in ("PowerConduit", "Battery", "StandingLamp"):
            return 9
        if self.plant == "two nets before" and d == "StandingLamp" and not self.landed:
            return 4
        if self.plant == "consumers cut off by the landing" and d == "StandingLamp" and self.landed:
            return 4
        return 7 if self.landed else 3

    def ap(self, cmd):
        p = cmd.split(":")
        if p[0] in ("place", "cplace"):
            x, z = p[3].split(",")
            self.add(p[1], int(x), int(z))
        elif p[0] == "link":
            a, b = p[1].split(",")
            self.links.append((int(a), int(b)))
            return {"success": True, "verdict": "Ok"}
        elif cmd.startswith("set:autoLink"):
            self.auto = cmd.endswith("True")
        elif cmd.startswith("set:keepWires"):
            self.keep = cmd.endswith("True")
        elif p[0] == "net":
            at = tuple(int(q) for q in p[1].split(","))
            here = [t for t in self.things if (t[2], t[3]) == at]
            trans = [t for t in here if t[1] != "StandingLamp"]
            n = self.net(trans[0][1]) if trans else -1
            return {"success": True, "net": n, "things": [{"id": t[0], "def": t[1], "net": self.net(t[1])} for t in here]}
        elif cmd == "census":
            if self.plant == "blind" and self.landed:
                return {"success": False}
            an = [t for t in self.things if t[1].startswith("RM_Aerial")]
            return {"success": True, "spansUp": len(self.links), "spansCut": 0,
                    "anchors": [{"id": i, "x": x, "z": z, "links": [{"other": (b if a == i else a), "state": "Up"} for a, b in self.links if i in (a, b)]}
                                for i, d, x, z in an]}
        return {"success": True}

    WALL = 15                      # the cord of a wall bracket runs this many vertices into the bracket's own wall (read live 2026-11-24)

    def probe(self, cmd):
        walls = [(x, z + 1) for _, d, x, z in self.things if d == "RM_AerialWallBracket"]
        if cmd.startswith("rect:"):
            if self.plant == "bracket wall unread":
                return {"success": False}
            at = tuple(int(q) for q in cmd.split(":")[1].split(",")[:2])
            return {"success": True, "verticesInUnwalkable": self.WALL if walls[:1] == [at] else 0}
        if cmd != "census":
            return {"success": True}
        bad = (self.WALL if walls else 0) + (4 if self.landed and self.plant == "a cord in another wall" else 0)
        c = self.conduit()
        if self.landed and self.plant == "cords left behind":
            c = [(x - self.MOVE[0], z - self.MOVE[1]) for x, z in c]
        e = {"end:%d,%d|end:%d,%d" % (c[0] + c[-1]): "h"} if c and not (self.landed and self.plant == "no cords after") else {}
        dev = {d: (x, z) for _, d, x, z in self.things if d in ("Battery", "StandingLamp")}
        if e and len(dev) == 2:    # vanilla's own link: a lamp wired straight to the battery; its end stands on the lamp's cell
            e["consumer:%d,%d|battery:%d,%d" % (dev["StandingLamp"] + dev["Battery"])] = "h2"
        return {"success": True, "edgeHashes": e, "cordEdges": len(e), "cordsAcrossNets": 0, "verticesInUnwalkable": bad, "conduitCells": len(c)}


def fly(mode, plant=None):
    ship = Ship(plant)
    src = os.path.join(os.environ.get("TMPDIR", "/tmp"), "fake_prove_%d.py" % os.getpid())
    with open(src, "w") as f:
        f.write(FAKE_PROVE)
    rl = types.ModuleType("run_live")
    rl.LiveBridge = lambda: ship
    old = sys.modules.get("run_live"), GS.PROVE, __builtins__.__dict__.get("FLY")
    sys.modules["run_live"], GS.PROVE = rl, src
    __builtins__.FLY = ship.fly
    det = {}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            rc = GS.scene(types.SimpleNamespace(mode=mode, shot=None), det)
    finally:
        GS.PROVE = old[1]
        del __builtins__.FLY
        if old[0] is not None:
            sys.modules["run_live"] = old[0]
        else:
            del sys.modules["run_live"]
        os.remove(src)
    return rc, det, ship


for mode in ("on", "off", "off_autolink"):
    rc, det, ship = fly(mode)
    check("flight %s: the shipped behaviour passes, with the control red by name" % mode, rc == 0 and det["control"][0] == "PASS", det)
    check("flight %s: every poked setting is put back" % mode, ship.auto is True and ship.keep is True)
    check("flight %s: the staging asks for brackets, a battery, two lamps" % mode,
          [sum(t[1] == d for t in ship.things) for d in ("RM_AerialWallBracket", "Battery", "StandingLamp")] == [2, 1, 2])
for mode, plant in (("on", "switch ignored"), ("off", "switch ignored"), ("off_autolink", "switch ignored"), ("off_autolink", "re-strung on landing"),
                    ("on", "ground link kept"), ("off", "ground link kept"), ("on", "no cords after"), ("off", "cords left behind"),
                    ("on", "consumers cut off by the landing"), ("off", "a cord in another wall")):
    rc, det, _ = fly(mode, plant)
    check("flight %s planted: %s reads FAIL" % (mode, plant), rc == 1, det)
rc, det, _ = fly("off", "re-strung on landing")
check("flight off: the old flight (auto-link off) cannot see the re-string, which is why off_autolink flies", rc == 0, det)
for plant in ("lands where it stood", "one lamp", "two nets before", "brackets refused", "blind", "bracket wall unread"):
    rc, det, _ = fly("on", plant)
    check("flight: %s is UNMEASURED, never a pass" % plant, rc == 2, det)

# ------------------------------------------------------------------ the records agree
C_ = os.path.join(PL.REPO, "design", "concepts", "GimmeSomeSlack")
scn = {s["id"]: s for s in json.load(open(os.path.join(C_, "scenes.json")))["scenes"]}
tt = json.load(open(os.path.join(C_, "version", "test_table.json")))
sys.path.insert(0, os.path.join(PL.REPO, "src", "RimMandrake", "Utils", "testq"))
import stage6_checks as SC  # noqa: E402


def ROUTE(tid):
    r, why = SC.route("GimmeSomeSlack", tid, tt["tests"][tid])
    return r["key"].split(":")[1] if r else why


dec = {b["id"]: b["decides"] for b in tt["bars"]}
check("records: the Steve lane flies the third flight", ROUTE("P_GS3_auto_link_on_keep_wires_off_span_stays_down") == "off_autolink" and ROUTE("P_GS1_keep_wires_on_gravship_off_aboard_span_taken_down") == "off")
OLD = {"S7_save_load_styles", "S12d_D4_pending_queue_save", "SL1_save_landed_new_file_only", "SL2_save_names_no_class_of_ours",
       "SL3_after_load_census_equal", "O7_gpt_read_fixes", "Z_log_budget"}
want = set(V.scene_rows_for("sc_save_reload_wire_down"))
check("records: sc_save_reload_wire_down keeps the seven rows sc_walk was read from, and adds its own three", want == OLD | set(W.ROWS), sorted(want))
check("records: sc_tap_theft is read from its three net rows and the three goodwill rows",
      set(V.scene_rows_for("sc_tap_theft")) == {"M19_tap_drains_one_way", "M19n_taps_off_control", "M19m_tap_mixed_net_connects_own_conduit"} | set(TG.ROWS))
check("records: sc_gravship is read from the auto-link flight and the control too", set(GS.ROW_IDS.values()) <= set(V.scene_rows_for("sc_gravship")))
check("records: sc_walk decides nothing and is no scene", "sc_walk" not in scn and "sc_walk" not in tt["tests"] and not [b for b, d in dec.items() if "sc_walk" in d])
check("records: walk_scavenger_base is decided by the small scene and his walk", dec["walk_scavenger_base"] == ["sc_save_reload_wire_down", "LOOK_STAGE8"])
check("records: the master off and on reads keep deciding through sc_settings",
      {"M7_off_restores_vanilla", "M7b_on_again_invisible"} <= set(V.scene_rows_for("sc_settings")) and "sc_settings" in dec["settings_switch_cleanly"])
check("records: the scene's entry stands in the code", callable(getattr(V, "scene_save_reload_wire_down", None)))
rows = [{"id": r, "status": "PASS"} for r in want]
check("records: the scene passes on its ten rows", V.scene_verdict("sc_save_reload_wire_down", rows)[0] == "PASS")
check("records: the scene does not pass with one row missing", all(V.scene_verdict("sc_save_reload_wire_down", [x for x in rows if x["id"] != r])[0] == "UNMEASURED" for r in want))

print("gss small scenes: %d/%d passed" % (N[0] - len(FAILS), N[0]))
sys.exit(1 if FAILS else 0)
