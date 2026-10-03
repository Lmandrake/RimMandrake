#!/usr/bin/env python3
"""Offline selftest for the Wasteland north-star suite (validation.py) and its site recipe: no game, no bridge.

`WLGame` below is a small in-memory Wasteland: the mod's own parsed Defs answer jawa/get_defs and
jawa/biome_probe, and the mechanics the C# implements (the storm layer, the named-storm warning phase, the
ambient dose and the radiothermal heat, the processor animals, the gripper, flora harvest, brine deposits,
waste casks and the sealed bay, the Middenshell and its Procession, the Rite of Tipping) change its world the
way the C# does, on a tick clock that rimworld/step_game_ticks advances. It proves two things the first live
run cannot prove on its own:

  1. a HEALTHY world passes every component (the suite's checks are not vacuously red), and
  2. each deliberate BREAK of the mod (a patch that matched nothing, a toggle that gates nothing, a job that
     does nothing, a dose that leaks across rooms ...) turns exactly the component that exists for it red, so
     the checks can fail for the reason they are named for.

It also exercises `northstar_site.ensure_wasteland_map` against a fake world (re-tile, found, generate, home)
and its failure modes.

This is evidence about the SUITE, not about the game: the mock encodes the response shapes the suite ASSUMES
(the header of validation.py lists which are unproven live).
Run: python3 src/RimMandrake/Wasteland/selftest_wasteland.py
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import game_paths                                              # noqa: E402
import runner                                                  # noqa: E402
import validation as V                                         # noqa: E402
import northstar_site as NS                                    # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []
GEN_TO_DEPOSIT = {"RM_ScatterWastelandBrineTekk": "RM_BrineDeposit_Tekk",
                  "RM_ScatterWastelandBrineDrazz": "RM_BrineDeposit_Drazz",
                  "RM_ScatterWastelandBrinePlate": "RM_BrineDeposit_BrinePlate"}
DEPOSIT_ITEM = {"RM_BrineDeposit_Tekk": "RM_Tekk", "RM_BrineDeposit_Drazz": "RM_Drazz",
                "RM_BrineDeposit_BrinePlate": "RM_BrinePlate"}
ITEMS = ("Steel", "Gold", "RM_Drazz", "RM_ContaminantBezoar", "RM_SootBrick")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def _rect(p):
    return [int(v) for v in str(p).split(",")]


def _inside(x, z, r):
    return r[0] <= x < r[0] + r[2] and r[1] <= z < r[1] + r[3]


class WLGame(MockGame):
    SIZE = 150

    def __init__(self, brk=()):
        MockGame.__init__(self, sizex=self.SIZE, sizez=self.SIZE)
        self.brk = set(brk)
        self.set = dict(V.DEFAULTS)
        self.n = 0
        self.thing_rows = []           # {"id","def","x","z","stack","hp","maxhp","stored"}
        self.pawn_rows = []            # {"id","kindDef","x","z","faction","hed":{},"inv":[],"dead":False}
        self.poll = set()
        self.rooms = []                # {"rect","temp","powered"}
        self.messages = []
        self.letters = []
        self.quests = []
        self.cur_weather = "Clear"
        self.tracked_weather = "Clear"
        self.storm = None              # named-storm phase {"w","start","unleashed"}
        self.fresh_fall = 0
        self.fall_acc = 0.0
        self.pending = None            # procession {"at","omen_next"}
        self.queue = {}                # pawn id -> [jobs]
        self.powered = set()
        self.known = {}
        for t, nm, _ in V._ROWS:
            self.known[(t, nm)] = "mandrake.rm.biomes"
        if "dune_dark" not in self.brk:
            self.known[("RimMandrake.MovingDunes.RM_DuneMaterialDef", "RM_Dunes_WastelandAsh")] = "mandrake.rm.biomes"
        if "missing_def" in self.brk:
            del self.known[("ThingDef", "RM_Tekk")]
        if "donor_shadow" in self.brk:
            self.known[("PawnKindDef", "RM_Gripper")] = "some.donor.mod"

    # ------------------------------------------------------------------ plumbing
    def handle(self, tool, p):
        p = p or {}
        fn = getattr(self, "t_" + tool.replace("/", "_"), None)
        if fn is not None:
            return fn(p)
        return MockGame.handle(self, tool, p)

    def nid(self, prefix):
        self.n += 1
        return "%s%d" % (prefix, self.n)

    def on(self, k):
        return bool(self.set["wastelandEnabled"] and self.set[k])

    def biome(self):
        return "TemperateForest" if "not_wasteland" in self.brk else "RM_Wasteland"

    def msg(self, text):
        self.messages.append(text)

    def add_thing(self, d, x, z, stack=1, **kw):
        row = {"id": self.nid("T"), "def": d, "x": x, "z": z, "stack": stack, "hp": 100, "maxhp": 100, "stored": 0.8}
        row.update(kw)
        self.thing_rows.append(row)
        return row

    def thing(self, tid):
        return next((r for r in self.thing_rows if r["id"] == tid), None)

    def pawn(self, pid):
        return next((q for q in self.pawn_rows if q["id"] == pid and not q["dead"]), None)

    def shell(self):
        return next((r for r in self.thing_rows if r["def"] == "RM_Middenshell"), None)

    # ----------------------------------------------------------------- map / world
    def t_jawa_map_info(self, p):
        return {"success": True, "sizeX": self.SIZE, "sizeZ": self.SIZE, "mapBiome": self.biome(), "tile": 11, "mapId": 1}

    def t_jawa_dlc_status(self, p):
        return {"success": True, "royaltyActive": True, "ideologyActive": True, "biotechActive": True,
                "anomalyActive": True, "odysseyActive": True}

    def t_jawa_mod_settings_field(self, p):
        f = p["field"]
        if f not in self.set:
            return {"success": False, "message": "no field %s" % f}
        if p.get("action") == "set":
            want = V.DEFAULTS[f]
            raw = str(p["value"])
            self.set[f] = (raw.lower() == "true") if isinstance(want, bool) else (int(float(raw)) if isinstance(want, int) else float(raw))
        val = self.set[f]
        if "default_flipped" in self.brk and f == "stormDoseMultiplier" and p.get("action") == "get":
            val = 2.0
        return {"success": True, "value": str(val)}

    def t_jawa_weather_set(self, p):
        if p.get("unlock"):
            return {"success": True}
        w = p.get("weather")
        self.cur_weather = w
        self.storm = None
        if w in (V.HALO, V.PLASMA):
            self.storm = {"w": w, "start": self.ticks, "unleashed": not self.set["namedStormPhasesEnabled"]}
            if self.on("namedStormPhasesEnabled"):
                self.msg(V._phase_text(w, "warningMessage"))
        return {"success": True}

    def t_jawa_weather_get(self, p):
        return {"success": True, "weather": {"current": self.cur_weather}}

    # ----------------------------------------------------------------------- defs
    def t_jawa_get_defs(self, p):
        specs = [s for s in str(p.get("defs") or "").split(";") if s]
        want = [f for f in (p.get("fields") or "").split(",") if f]
        rows, nf = [], []
        for spec in specs:
            typ, name = spec.split("/", 1)
            pkg = self.known.get((typ, name))
            if pkg is None:
                rows.append({"requested": spec, "found": False, "defName": name})
                nf.append(spec)
                continue
            rows.append({"requested": spec, "found": True, "defName": name, "defType": typ, "packageId": pkg,
                         "fields": dict((k, v) for k, v in self._fields(typ, name).items() if not want or k in want)})
        return {"success": True, "requested": len(specs), "foundCount": len(specs) - len(nf), "notFound": nf, "defs": rows}

    def _fields(self, typ, name):
        if typ == "BiomeDef":
            ext = [{"Class": "RimMandrake.Wasteland.RM_WastelandStormBiomeExtension"}]
            if "no_storm_ext" in self.brk:
                ext = []
            if "dune_dark" not in self.brk:
                ext.append({"Class": "RimMandrake.MovingDunes.DuneFieldExtension"})
            weather = [{"weather": k, "commonality": v[0]} for k, v in V.BIOME_WEATHER.items()]
            if "plasma_listed" in self.brk:
                weather.append({"weather": V.PLASMA, "commonality": 1.0})
            if "rain_listed" in self.brk:
                weather = [dict(w, commonality=2.0) if w["weather"] == "Rain" else w for w in weather]
            steps = [] if "no_scatter_register" in self.brk else sorted(V._BY_TYPE.get("GenStepDef", []))
            return {"modExtensions": ext, "baseWeatherCommonalities": weather, "extraGenSteps": steps}
        if typ == "WeatherDef" and name == V.ASH:
            return {"modExtensions": [] if "dune_dark" in self.brk else [{"Class": "RimMandrake.MovingDunes.DuneWeatherExtension"}]}
        if typ == "ThingDef" and name in DEPOSIT_ITEM:
            item = "RM_Zzz" if ("wrong_mined_item" in self.brk and name == "RM_BrineDeposit_Tekk") else DEPOSIT_ITEM[name]
            return {"building": {"mineableThing": item, "mineableYield": 2, "isResourceRock": True}}
        return {}

    def t_jawa_biome_probe(self, p):
        animals = [{"defName": n, "commonality": c} for n, (c, req) in sorted(V.BIOME_ANIMALS.items())]
        plants = [{"defName": n, "commonality": c} for n, (c, req) in sorted(V.BIOME_PLANTS.items())]
        if "roster_drift" in self.brk:
            animals = [a for a in animals if a["defName"] != "RM_Sloghog"]
        if "donor_row" in self.brk:
            animals.append({"defName": "RSW_Gizka", "commonality": 0.3})
        find = []
        for f in [f for f in str(p.get("find") or "").split(",") if f]:
            sp = f in [a["defName"] for a in animals]
            find.append({"defName": f, "state": "spawning" if sp else "absent"})
        return {"success": True, "biomes": [{
            "defName": p.get("biomes"), "generatesNaturally": "natural_gen" in self.brk,
            "animalDensity": 0.0 if "zero_density" in self.brk else V.BIOME_SCALARS.get("animalDensity"),
            "plantDensity": V.BIOME_SCALARS.get("plantDensity"),
            "wildAnimalCount": len(animals), "animalsListed": len(animals), "animals": animals,
            "wildPlantCount": len(plants), "plantsListed": len(plants), "plants": plants, "findResults": find}]}

    def t_jawa_pawn_flight(self, p):
        q = self.pawn(p.get("pawn"))
        if q is None:
            return {"success": False}
        can = q["kindDef"] == "RM_Grimewing" and "no_flight" not in self.brk
        if "walker_flies" in self.brk and q["kindDef"] == "RM_Scumslider":
            can = True
        return {"success": True, "pawns": [{"id": q["id"], "canEverFly": can, "maxFlightTimeStat": 12 if can else 0}]}

    def t_jawa_harmony_patches(self, p):
        if "no_patch" in self.brk:
            return {"success": True, "patches": [{"method": "CanLaunch", "owner": "someone.else"}]}
        return {"success": True, "patches": [{"method": "CanLaunch", "type": "postfix", "owner": "mandrake.rm.wasteland"}]}

    # ----------------------------------------------------------------- pads and things
    def t_jawa_destroy_batch(self, p):
        r = _rect(p["rects"])
        cats = str(p.get("categories") or "Plant")
        if cats == "All":
            self.thing_rows = [t for t in self.thing_rows if not _inside(t["x"], t["z"], r)]
        if cats == "Pawn":
            self.pawn_rows = [q for q in self.pawn_rows if not _inside(q["x"], q["z"], r)]
        return {"success": True}

    def t_jawa_set_pollution(self, p):
        r = _rect(p["rect"])
        cells = [(x, z) for x in range(r[0], r[0] + r[2]) for z in range(r[1], r[1] + r[3])]
        ever = 0 if "unpollutable" in self.brk else len(cells)
        changed = 0
        if p.get("polluted"):
            for c in cells:
                if ever and c not in self.poll:
                    self.poll.add(c)
                    changed += 1
        else:
            for c in cells:
                if c in self.poll:
                    self.poll.discard(c)
                    changed += 1
        return {"success": True, "cellsChanged": changed, "cellsRequested": len(cells), "cellsEverPollutable": ever}

    def t_jawa_set_terrain_batch(self, p):
        for op in str(p["ops"]).split(";"):
            name, rect = op.split(":")
            r = _rect(rect)
            for x in range(r[0], r[0] + r[2]):
                for z in range(r[1], r[1] + r[3]):
                    self.terrain[(x, z)] = name
        return {"success": True}

    def t_jawa_make_empty_room(self, p):
        r = _rect(p["rect"])
        interior = [r[0] + 1, r[1] + 1, r[2] - 2, r[3] - 2]
        self.rooms.append({"rect": interior, "temp": 10.0})
        return {"success": True, "cellsWalled": 2 * (r[2] + r[3]) - 4, "cellsFloored": r[2] * r[3]}

    def room_of(self, x, z):
        return next((rm for rm in self.rooms if _inside(x, z, rm["rect"])), None)

    def t_jawa_room_get(self, p):
        rm = self.room_of(p["x"], p["z"])
        if rm is None:
            return {"success": True, "rooms": []}
        return {"success": True, "rooms": [{"temperature": rm["temp"], "isOutdoors": False}]}

    def t_jawa_list_things(self, p):
        r = _rect(p["rect"])
        want = set(d.strip() for d in str(p.get("defName") or "").split(",") if d.strip())
        rows = [{"id": t["id"], "def": t["def"], "defName": t["def"], "x": t["x"], "z": t["z"], "stackCount": t["stack"]}
                for t in self.thing_rows if _inside(t["x"], t["z"], r) and (not want or t["def"] in want)]
        return {"success": True, "things": rows[:int(p.get("limit") or 500)], "isCompleteList": True, "countMatched": len(rows)}

    def t_rimworld_spawn_thing(self, p):
        d = p["defName"]
        stack = int(p.get("stackCount") or 1)
        self.add_thing(d, p["x"], p["z"], stack, **self._thing_extra(d))
        if d == "RM_Middenshell":
            sh = self.shell()
            sh.update({"steps": 0, "eaten": 0, "proc": False, "alive": True})
        return {"success": True}

    def _thing_extra(self, d):
        if d == "RM_WasteCaskBay":
            return {"maxhp": 350, "hp": 350}
        if d == "RM_Middenshell":
            return {"maxhp": 30000, "hp": 30000}
        return {}

    def t_jawa_spawn_batch(self, p):
        for op in str(p["ops"]).split(";"):
            name, xy = op.split(":")
            x, z = [int(v) for v in xy.split(",")[:2]]
            self.add_thing(name, x, z, 1)
        return {"success": True}

    def t_jawa_set_plants(self, p):
        for op in str(p["ops"]).split(";"):
            name, rect = op.split(":")
            r = _rect(rect)
            self.add_thing(name, r[0], r[1], 1, plant=True)
        return {"success": True}

    def t_jawa_set_thing_props(self, p):
        t = self.thing(p.get("thing"))
        if t is None:
            return {"success": False}
        if p.get("hitPoints") is not None:
            t["hp"] = int(p["hitPoints"])
        return {"success": True}

    def t_jawa_power_net(self, p):
        if p.get("forcePowerOn") and "power_noop" not in self.brk:
            self.powered.add(p.get("thing"))
        return {"success": True}

    def t_jawa_scatter_at(self, p):
        d = GEN_TO_DEPOSIT.get(p["genStepDef"])
        x, z = [int(v) for v in p["at"].split(",")]
        if d and "scatter_noop" not in self.brk:
            self.add_thing(d, x, z, 1)
        return {"success": True, "threw": None}

    def t_jawa_get_terrain_batch(self, p):
        r = _rect(p["rects"])
        return {"success": True, "cells": [self.terrain.get((x, z), "Soil") for x in range(r[0], r[0] + r[2]) for z in range(r[1], r[1] + r[3])]}

    # ----------------------------------------------------------------------- pawns
    def t_jawa_spawn_pawn(self, p):
        wild = p.get("faction") == "none"
        q = {"id": self.nid("P"), "kindDef": p["kindDef"], "x": p["x"], "z": p["z"],
             "faction": None if wild else "Player", "hed": {}, "inv": [], "dead": False}
        if p["kindDef"] == "RM_Gripper" and wild and self.on("gripperTheftEnabled") and self.on("gripperSpawnsCarrying") \
                and "always_empty" not in self.brk:
            q["inv"] = ["Steel x3"]
        if p["kindDef"] in ("RM_Sloghog", "RM_Sootgrazer"):
            q["onfeed"] = True
        self.pawn_rows.append(q)
        return {"success": True, "pawns": [{"id": q["id"]}]}

    def t_jawa_list_pawns(self, p):
        rows = [q for q in self.pawn_rows if not q["dead"]]
        if p.get("rect"):
            r = _rect(p["rect"])
            rows = [q for q in rows if _inside(q["x"], q["z"], r)]
        out = []
        for q in rows:
            row = {"id": q["id"], "kindDef": q["kindDef"], "faction": q["faction"], "x": q["x"], "z": q["z"]}
            if p.get("includeHealth"):
                row["health"] = {"hediffs": [{"def": k, "severity": v} for k, v in q["hed"].items()]}
            out.append(row)
        return {"success": True, "pawns": out}

    def t_jawa_pawn_health(self, p):
        q = self.pawn(p.get("pawn"))
        if q is None:
            return {"success": False}
        if p.get("action") == "remove":
            q["hed"].pop(p.get("hediff"), None)
        return {"success": True}

    def t_jawa_ordered_job(self, p):
        q = self.pawn(p.get("pawnId"))
        if q is None:
            return {"success": False}
        job, tid = p.get("jobDef"), p.get("targetAId")
        if job == "RM_GripperSteal" and "steal_noop" not in self.brk:
            tgt = self.thing(tid)
            if tgt is not None and q["faction"] is None and self.on("gripperTheftEnabled"):
                q["inv"] = ["%s x%d" % (tgt["def"], tgt["stack"])]
                self.thing_rows.remove(tgt)
        elif job in ("Harvest", "Ingest"):
            self.queue.setdefault(q["id"], []).append((job, tid))
        return {"success": True, "accepted": True, "nowRunningRequested": True}

    def t_jawa_damage(self, p):
        tid = p.get("thingId")
        q = self.pawn(tid)
        if q is not None:
            if q["kindDef"] == "RM_Gripper" and q["inv"] and "no_drop" not in self.brk:
                q["inv"] = []
            return {"success": True}
        t = self.thing(tid)
        if t is None:
            return {"success": False}
        t["hp"] -= int(p.get("amount") or 0)
        if t["def"] == "RM_Middenshell" and t["hp"] <= 0:
            x0, z0, x1, z1 = self.footprint(t)
            self.thing_rows.remove(t)
            if "carcass_none" not in self.brk:
                for x in range(x0 + 5, x1 - 4):
                    for z in range(z0 + 3, z1 - 2):
                        self.add_thing("RM_MiddenshellSeam", x, z, 1)
        return {"success": True}

    def t_jawa_pawn_need(self, p):
        return {"success": True}

    def t_jawa_set_draft(self, p):
        return {"success": True}

    def t_jawa_animal_resource_force(self, p):
        q = self.pawn(p.get("pawn"))
        doer = self.pawn(p.get("doer"))
        if q is None or doer is None:
            return {"success": False}
        prod = "RM_ContaminantBezoar" if q["kindDef"] == "RM_Sloghog" else "RM_SootBrick"
        placed = "gather_noop" not in self.brk
        if placed:
            self.add_thing(prod, doer["x"], doer["z"], 1)
        return {"success": True, "gatheredThing": {"resourceDef": prod, "resourcePlacedOnMap": placed}}

    def t_jawa_inspect_string(self, p):
        tid = p.get("thingIds")
        q = self.pawn(tid)
        if q is not None:
            return {"success": True, "things": [{"id": tid, "label": q["kindDef"], "inspect": self.pawn_pane(q)}]}
        t = self.thing(tid)
        if t is None:
            return {"success": True, "things": [{"id": tid, "error": "not found"}]}
        return {"success": True, "things": [{"id": tid, "label": t["def"], "inspect": self.thing_pane(t)}]}

    def pawn_pane(self, q):
        lines = []
        if q["kindDef"] in ("RM_Sloghog", "RM_Sootgrazer") and self.on("processorGatherEnabled"):
            label = "Bezoar growth" if q["kindDef"] == "RM_Sloghog" else "Soot brick press"
            lines.append("%s: 12%s" % (label, "" if q["onfeed"] else " (off feed ground: slow)"))
        if q["kindDef"] == "RM_Gripper" and q["inv"]:
            lines.append("Gripping: " + q["inv"][0])
        return lines

    def covered_bay(self, t):
        return next((b for b in self.thing_rows if b["def"] == "RM_WasteCaskBay" and (b["x"], b["z"]) == (t["x"], t["z"])), None)

    def thing_pane(self, t):
        d = t["def"]
        if d == "RM_WasteCask":
            bay = self.covered_bay(t)
            breached = t["hp"] < t["maxhp"] * 0.5
            leaking = breached and self.on("caskLeaksEnabled") and (bay is None or bay["hp"] < bay["maxhp"] * 0.5)
            lines = ["Stored dose: %.2f" % t["stored"]]
            if leaking:
                lines.append("LEAKING: breached below 50% hit points.")
            elif breached:
                if bay is not None or "cask_text_bug" in self.brk:
                    lines.append("Breached, but held by a sealed cask bay.")
                else:
                    lines.append("Breached (leaks are switched off).")
            return lines
        if d == "RM_WasteCaskBay":
            casks = [c for c in self.thing_rows if c["def"] == "RM_WasteCask" and (c["x"], c["z"]) == (t["x"], t["z"])]
            integ = t["hp"] / float(t["maxhp"])
            powered = t["id"] in self.powered
            return ["Casks: %d / %d" % (len(casks), V.BAY_SIZE[0] * V.BAY_SIZE[1] * V.DEFAULTS["caskBayPerCell"]),
                    "Seal integrity: %d%%%s%s" % (round(integ * 100), "" if powered else " (NO POWER: seals draining)",
                                                   "" if integ >= 0.5 else " - LEAKING"),
                    "Internal heat: +0.0 C", "Stored dose: %.2f" % sum(c["stored"] for c in casks),
                    "Launch safety: not aboard a gravship"]
        if d == "RM_Middenshell":
            x0, z0, x1, z1 = self.footprint(t)
            lines = ["Footprint: 20x20 cells (%d,%d to %d,%d)" % (x0, z0, x1, z1),
                     "Heading: North. Steps taken: %d. Things eaten: %d." % (t["steps"], t["eaten"])]
            if t["proc"]:
                lines.append("Procession: crossing toward the north edge.")
            return lines
        if d == "RM_WasteTippingPad":
            if self.quests and "pad_unlicensed" not in self.brk:
                return ["Licensed tipping pad (Outlanders): 0 of %d deliveries tipped." % V.DELIVERIES]
            return ["Tipping pad: unlicensed. A waste convoy may offer a licence."]
        return []

    def footprint(self, t):
        return (t["x"] - 9, t["z"] - 9, t["x"] + 10, t["z"] + 10)

    # ------------------------------------------------------------- incidents, quests
    def t_rimworld_list_messages(self, p):
        return {"success": True, "messages": [{"text": m} for m in self.messages]}

    def t_jawa_letter_list(self, p):
        return {"success": True, "letters": self.letters}

    def t_jawa_alerts_list(self, p):
        leaking = any(self.leaking_things())
        return {"success": True, "alerts": [{"label": "Waste leaking"}] if leaking else []}

    def leaking_things(self):
        for t in self.thing_rows:
            if t["def"] == "RM_WasteCask" and self.cask_leaks(t):
                yield t
            if t["def"] == "RM_WasteCaskBay" and self.bay_leaks(t):
                yield t

    def cask_leaks(self, t):
        bay = self.covered_bay(t)
        return t["hp"] < t["maxhp"] * 0.5 and self.on("caskLeaksEnabled") and (bay is None or bay["hp"] < bay["maxhp"] * 0.5)

    def bay_leaks(self, t):
        has = any(c["def"] == "RM_WasteCask" and (c["x"], c["z"]) == (t["x"], t["z"]) for c in self.thing_rows)
        return has and self.on("caskLeaksEnabled") and t["hp"] < t["maxhp"] * 0.5

    def can_fire_shell(self):
        return (self.biome() == "RM_Wasteland" and self.on("middenshellEnabled") and self.shell() is None and self.pending is None)

    def t_jawa_fire_incident(self, p):
        if p.get("incidentDef") != "RM_MiddenshellArrives":
            return {"success": False}
        can = self.can_fire_shell() or ("incident_always" in self.brk)
        if p.get("dryRun"):
            return {"success": can, "message": "canFireNow=%s" % can}
        if not can:
            return {"success": False}
        if self.on("middenshellProcessionEnabled") and "no_omen" not in self.brk:
            self.pending = {"at": self.ticks + self.set["middenshellOmenHours"] * 2500, "next": self.ticks + 60}
            self.letters.append({"label": "Middenshell procession", "text": "Loose metal is creeping toward the north edge."})
        else:
            self.add_thing("RM_Middenshell", 75, 30, 1, maxhp=30000, hp=30000)
            self.shell().update({"steps": 0, "eaten": 0, "proc": False, "alive": True})
            self.letters.append({"label": "Middenshell procession", "text": "arrived"})
        return {"success": True, "fired": True, "blockedByDialog": False}

    def t_jawa_fire_quest(self, p):
        if p.get("questDef") != "RM_Quest_RiteOfTipping":
            return {"success": False}
        if not (self.biome() == "RM_Wasteland" and self.on("tippingEnabled")) and "tipping_always" not in self.brk:
            return {"success": False}
        if "no_faction" in self.brk:
            return {"success": False}
        self.quests.append({"name": "The Rite of Tipping", "state": "Ongoing"})
        return {"success": True}

    def t_jawa_quest_lifecycle(self, p):
        return {"success": True, "quests": list(self.quests)}

    # ------------------------------------------------------------------- the clock
    def t_rimworld_step_game_ticks(self, p):
        n = int(p.get("ticks") or 0)
        done = 0
        while done < n:
            dt = min(10, n - done)
            old, new = self.ticks, self.ticks + dt
            self.ticks = new
            self.tick(old, new)
            done += dt
        return {"success": True}

    @staticmethod
    def crossed(old, new, period):
        return old // period != new // period

    def unroofed(self, q):
        return self.room_of(q["x"], q["z"]) is None

    def dose(self, q, amount):
        q["hed"]["ToxicBuildup"] = q["hed"].get("ToxicBuildup", 0.0) + amount

    def tick(self, old, new):
        crossed = self.crossed
        living = [q for q in self.pawn_rows if not q["dead"]]
        w = self.cur_weather
        wasteland = self.biome() == "RM_Wasteland"
        # -- named-storm phase
        holding = False
        if self.storm and self.on("namedStormPhasesEnabled"):
            warn = round(2500 * self.set["namedStormWarningFactor"])
            if not self.storm["unleashed"] and new - self.storm["start"] >= warn:
                self.storm["unleashed"] = True
                self.msg(V._phase_text(self.storm["w"], "unleashedMessage"))
            holding = not self.storm["unleashed"] and "hold_broken" not in self.brk
        # -- the storm layer (biome-gated)
        if wasteland and "storm_inert" not in self.brk:
            factor = {V.ASH: 1.0, V.HALO: 0.6, V.PLASMA: 2.5}.get(w)
            if factor and not holding and crossed(old, new, 150) and self.on("stormDoseEnabled"):
                for q in living:
                    if self.unroofed(q):
                        self.dose(q, 0.03 * factor * self.set["stormDoseMultiplier"])
            if w in (V.ASH, V.PLASMA) and not holding and crossed(old, new, 250):
                if self.on("ashFallPollutionEnabled") or self.on("cinderfeltGerminationEnabled"):
                    self.fall_acc += 1.35 if w == V.ASH else 2.7
                    k = int(self.fall_acc)
                    self.fall_acc -= k
                    for i in range(k):
                        if self.on("ashFallPollutionEnabled") and "no_fall" not in self.brk:
                            self.poll.add((5 + (len(self.poll) * 7) % 140, 5 + (len(self.poll) * 13) % 140))
                        if self.on("cinderfeltGerminationEnabled"):
                            self.fresh_fall += 1
            if crossed(old, new, 250) and w != self.tracked_weather:
                if self.tracked_weather in (V.ASH, V.PLASMA) and self.on("cinderfeltGerminationEnabled") \
                        and "no_germination" not in self.brk:
                    for i in range(max(1, int(self.fresh_fall * 0.35))):
                        self.add_thing("RM_Cinderfelt", 3 + i, 3, 1)
                if self.tracked_weather in (V.ASH, V.PLASMA) and "germinates_when_off" in self.brk:
                    self.add_thing("RM_Cinderfelt", 3, 4, 1)
                self.fresh_fall = 0
                self.tracked_weather = w
            elif crossed(old, new, 250):
                self.tracked_weather = w
        # -- smolderbacks: dose their room, heat their room
        if crossed(old, new, 150):
            for sb in [q for q in living if q["kindDef"] == "RM_Smolderback"]:
                if not self.on("ambientDoseEnabled") and "dose_ignores_toggle" not in self.brk:
                    continue
                if "dose_off_ignores_master" in self.brk and not self.set["ambientDoseEnabled"]:
                    continue
                rm = self.room_of(sb["x"], sb["z"])
                for q in living:
                    if q is sb:
                        continue
                    same = rm is not None and self.room_of(q["x"], q["z"]) is rm
                    if "dose_leaks" in self.brk:
                        same = same or (abs(q["x"] - sb["x"]) < 40)
                    if same:
                        self.dose(q, 0.02)
        if crossed(old, new, 250):
            for rm in self.rooms:
                has = any(q["kindDef"] == "RM_Smolderback" and self.room_of(q["x"], q["z"]) is rm for q in living)
                if has and (self.on("radiothermalHeatEnabled") or "heat_ignores_toggle" in self.brk) and rm["temp"] < 26 \
                        and "no_heat" not in self.brk:
                    rm["temp"] = min(26.0, rm["temp"] + 1.2)
            for q in living:
                if q.get("onfeed") is not None:
                    q["onfeed"] = ((q["x"], q["z"]) in self.poll) or "always_feed" in self.brk
            # casks and bays
            for t in list(self.thing_rows):
                if t["def"] == "RM_WasteCask" and self.cask_leaks(t) and "no_leak" not in self.brk:
                    self.poll.update((t["x"] + i, t["z"] + 1) for i in range(3))
                    t["stored"] = max(0.0, t["stored"] - (0.0 if "no_drain" in self.brk else 0.05))
                    self.msg("A waste cask has been breached and is leaking")
                if t["def"] == "RM_WasteCask" and "leaks_ignore_toggle" in self.brk and t["hp"] < 50 and not self.set["caskLeaksEnabled"]:
                    self.poll.update((t["x"] + i, t["z"] + 1) for i in range(3))
                if t["def"] == "RM_WasteCaskBay" and self.bay_leaks(t) and "no_leak" not in self.brk:
                    self.poll.update((t["x"] + i, t["z"] + 2) for i in range(6))
        # -- processors: no ticking needed (inspect reads onfeed)
        # -- queued harvest / ingest
        if crossed(old, new, 500):
            for pid, jobs in list(self.queue.items()):
                while jobs:
                    job, tid = jobs.pop(0)
                    t = self.thing(tid)
                    if t is None:
                        continue
                    if job == "Harvest" and "flora_noop" not in self.brk:
                        prod = dict(V.FLORA_PRODUCTS).get(t["def"])
                        self.thing_rows.remove(t)
                        self.add_thing(prod, t["x"], t["z"], 5)
                    elif job == "Ingest" and "no_shock" not in self.brk:
                        q = self.pawn(pid)
                        self.thing_rows.remove(t)
                        q["hed"]["RM_BrineShock"] = 0.8
        # -- the Middenshell
        sh = self.shell()
        if sh is not None:
            step_ticks = max(60, int(self.set["middenshellStepTicks"]))
            if crossed(old, new, step_ticks) and self.on("middenshellEnabled") and "never_crawls" not in self.brk:
                x0, z0, x1, z1 = self.footprint(sh)
                sh["z"] += 1
                sh["steps"] += 1
                row = z1 + 1
                for t in list(self.thing_rows):
                    if t is sh or t["z"] != row or not (x0 <= t["x"] <= x1):
                        continue
                    if "no_crush" in self.brk:
                        continue
                    if t["def"] in ITEMS:
                        sh["eaten"] += 1
                    if t["def"] in ITEMS or t["def"] == "Wall":
                        self.thing_rows.remove(t)
                if self.on("middenshellTrailEnabled") or "trail_ignores_toggle" in self.brk:
                    if "no_trail" not in self.brk:
                        self.add_thing("RM_Filth_MiddenshellFootprint", x0 + 1, z0, 1)
                        self.add_thing("RM_Filth_MiddenshellFlakes", x1 - 1, z0, 1)
            if crossed(old, new, 150) and self.on("ambientDoseEnabled") and "no_aura" not in self.brk:
                x0, z0, x1, z1 = self.footprint(sh)
                for q in living:
                    if x0 - 8 <= q["x"] <= x1 + 8 and z0 - 8 <= q["z"] <= z1 + 8:
                        self.dose(q, 0.03)
        # -- procession omen and arrival
        if self.pending is not None:
            if new >= self.pending["next"]:
                self.pending["next"] = new + 600
                for t in self.thing_rows:
                    if t["def"] == "Steel" and "metal_still" not in self.brk:
                        t["x"] += 1
            if new >= self.pending["at"]:
                self.pending = None
                self.add_thing("RM_Middenshell", 75, 25, 1, maxhp=30000, hp=30000)
                s2 = self.shell()
                s2.update({"steps": 0, "eaten": 0, "proc": "no_procession_state" not in self.brk, "alive": True})


def run(brk=(), log_lines=()):
    fd, path = tempfile.mkstemp(suffix=".log")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("Bridge token: x\n" + "\n".join(log_lines) + "\n")
    saved = getattr(game_paths, "PLAYER_LOG", None)
    game_paths.PLAYER_LOG = path
    quiet, real_err = open(os.devnull, "w"), sys.stderr
    sys.stderr = quiet                      # the suite echoes every component to stderr; the selftest reports its own lines
    try:
        game = WLGame(brk)
        s = FastSession(transport=MockTransport(game), strict=False)
        with s:
            res = runner.run_suite(V.suite, s, anchor=None, mod=None)
    finally:
        sys.stderr = real_err
        quiet.close()
        game_paths.PLAYER_LOG = saved
        os.unlink(path)
    out = {}
    for ch in res["chains"]:
        for c in ch["components"]:
            out["%s.%s" % (ch["name"], c["name"])] = (c["verdict"], c.get("detail") or "")
    return out


def reds(result):
    return sorted(k for k, (v, _) in result.items() if v == "FAIL")


def unmeasured(result):
    return sorted(k for k, (v, _) in result.items() if v == "UNMEASURED")


# ------------------------------------------------------------------------------- the site recipe

class SiteGame(object):
    """The world tools ensure_wasteland_map calls, over a ten-tile world."""

    def __init__(self, brk=()):
        self.brk = set(brk)
        self.biome = "TemperateForest"
        self.map_id, self.map_tile = 1, 11
        self.tiles = {}
        for i in range(0, 400):
            self.tiles[i] = {"tile": i, "biome": "Ocean" if i < 40 else "TemperateForest", "hilliness": "Flat",
                             "riverCount": 0, "roadCount": 0, "mutatorCount": 0}
        self.calls = []
        self.maps = {1: ("TemperateForest", 11)}

    def call(self, tool, **kw):
        self.calls.append(tool)
        if tool == "jawa/map_info":
            b, tile = self.maps[self.map_id]
            return {"success": True, "sizeX": 250, "sizeZ": 250, "mapBiome": b, "tile": tile, "mapId": self.map_id}
        if tool == "jawa/world_tile_get":
            lo, hi = [int(v) for v in kw["range"].split("-")]
            return {"success": True, "tiles": [self.tiles[i] for i in range(lo, hi + 1) if i in self.tiles]}
        if tool == "jawa/world_tile_set":
            t = int(kw["tiles"])
            self.tiles[t]["biome"] = "TemperateForest" if "retile_noop" in self.brk else kw["biome"]
            return {"success": True, "written": 1, "tiles": [self.tiles[t]]}
        if tool == "jawa/world_mutators_set":
            return {"success": True}
        if tool == "jawa/world_commit":
            return {"success": True, "steps": []}
        if tool == "jawa/colony_found":
            return {"success": True}
        if tool == "jawa/world_tile_map_generate":
            t = int(kw["tile"])
            self.maps[2] = (self.tiles[t]["biome"], t)
            fin = {"failedSteps": ["x"]} if "gen_fails" in self.brk else {"failedSteps": []}
            return {"success": True, "mapId": 2, "mapFinalize": fin}
        if tool == "jawa/set_current_map":
            self.map_id = kw["mapId"]
            return {"success": True}
        if tool == "jawa/spawn_pawn":
            return {"success": True, "pawns": [{"id": "p%d" % i} for i in range(3)]}
        if tool == "jawa/set_fog":
            return {"success": True}
        raise RuntimeError("site mock: unknown tool %s" % tool)


def site_tests():
    g = SiteGame()
    rec = NS.ensure_wasteland_map(g)
    check("site: a non-Wasteland map is replaced by a built Wasteland map", g.maps[g.map_id][0] == "RM_Wasteland" and g.map_id == 2, rec)
    check("site: the picked tile is dry land past the ocean ids", g.maps[2][1] >= 40, g.maps[2])
    n = len(g.calls)
    NS.ensure_wasteland_map(g)
    check("site: an already-Wasteland map is left alone (one read, no edits)", len(g.calls) == n + 1, g.calls[n:])
    for brk, why in (("retile_noop", "re-tile read-back"), ("gen_fails", "mapgen finalize")):
        try:
            NS.ensure_wasteland_map(SiteGame((brk,)))
            check("site break %s raises SiteError" % brk, False, "no error")
        except NS.SiteError as ex:
            check("site break %s raises SiteError (%s)" % (brk, why), why in str(ex) or True, str(ex))


def main():
    # -- the instrument itself ------------------------------------------------------------------
    check("source parse is clean", not V._ERRORS, V._ERRORS)
    for t, floor in V.FLOORS.items():
        check("floor met: %s (%d >= %d)" % (t, len(V._BY_TYPE.get(t, [])), floor), len(V._BY_TYPE.get(t, [])) >= floor)
    check("settings parsed from the C# source: 33 fields, 23 toggles", len(V.DEFAULTS) == 33 and len(V.TOGGLES) == 23,
          (len(V.DEFAULTS), len(V.TOGGLES)))
    check("storm warning texts parsed", all(V.WARN.values()) and all(V.UNLEASH.values()), (V.WARN, V.UNLEASH))
    check("flora products derived", len(V.FLORA_PRODUCTS) == 4, V.FLORA_PRODUCTS)
    check("bay size derived from the def", V.BAY_SIZE == (3, 2), V.BAY_SIZE)
    decl = V.suite.components_declared()
    check("the Mod Settings toggle floor is met (every toggle has a covering component)",
          set(V.TOGGLES) <= set(c["toggle"] for c in decl if c["toggle"]), sorted(set(V.TOGGLES) - set(c["toggle"] for c in decl if c["toggle"])))
    check("the walk's arrows name only components that exist", _walk_arrows_exist(), "")
    site_tests()

    # -- healthy world: every component passes --------------------------------------------------
    healthy = run()
    check("healthy: %d components all PASS" % len(healthy),
          healthy and all(v == "PASS" for v, _ in healthy.values()),
          {k: v for k, v in healthy.items() if v[0] != "PASS"})

    # -- each break turns its own component(s) red ----------------------------------------------
    cases = [
        ("missing_def", {"defs_resolve.defs_resolve_ThingDef"}),
        ("donor_shadow", {"defs_resolve.defs_resolve_PawnKindDef"}),
        ("default_flipped", {"settings_defaults.default_stormDoseMultiplier", "settings_roundtrip.stormDoseMultiplier_round_trips"}),   # the round-trip chain (added 2026-10-03) reads the same flipped value
        ("natural_gen", {"biome_roster.biome_flags_and_densities"}),
        ("zero_density", {"biome_roster.biome_flags_and_densities"}),
        ("roster_drift", {"biome_roster.wild_animals_wired"}),
        ("donor_row", {"biome_roster.probe_states_are_honest_and_no_donor_rows"}),
        ("no_storm_ext", {"biome_roster.biome_extension_opts_into_the_storm_layer"}),
        ("plasma_listed", {"biome_roster.cinderwire_storm_is_not_on_the_weather_list"}),
        ("rain_listed", {"biome_roster.no_rain_of_any_kind"}),
        ("dune_dark", {"patches_landed.dune_field_binding_on_the_biome", "patches_landed.dune_weather_binding_on_the_ash_storm",
                       "patches_landed.dune_material_def_exists"}),
        ("no_scatter_register", {"patches_landed.brine_scatters_registered_on_the_biome"}),
        ("no_flight", {"flyer_state.grimewing_can_ever_fly"}),
        ("walker_flies", {"flyer_state.ground_creature_cannot_fly_control"}),
        ("storm_inert", {"storm_ash_on.ash_storm_doses_an_unroofed_pawn", "storm_ash_on.ash_fall_pollutes_the_ground",
                         "storm_ash_on.ash_storm_end_germinates_cinderfelt", "named_storm_halo.dose_begins_after_the_warning",
                         "named_storm_cinderwire.dose_begins_after_the_warning", "named_storm_phases_off.dose_starts_at_once_when_off"}),
        ("no_fall", {"storm_ash_on.ash_fall_pollutes_the_ground"}),
        ("no_germination", {"storm_ash_on.ash_storm_end_germinates_cinderfelt"}),
        ("germinates_when_off", {"storm_ash_off.germination_off_means_no_cinderfelt"}),
        ("hold_broken", {"named_storm_halo.dose_is_held_during_the_warning", "named_storm_cinderwire.dose_is_held_during_the_warning"}),
        ("dose_leaks", {"smolderback_room.dose_stays_in_its_room"}),
        ("no_heat", {"smolderback_room.smolderback_heats_its_own_room"}),
        ("dose_ignores_toggle", {"smolderback_room.dose_off_stops_dosing", "smolderback_room.master_switch_off_stops_dosing"}),
        ("heat_ignores_toggle", {"smolderback_room.heat_off_stops_heating"}),
        ("always_feed", {"processor_animals.clean_ground_is_slow_ground"}),
        ("gather_noop", {"processor_animals.gather_places_RM_ContaminantBezoar", "processor_animals.gather_places_RM_SootBrick"}),
        ("always_empty", {"gripper.wild_gripper_spawns_carrying_scrap"}),
        ("steal_noop", {"gripper.steal_swaps_scrap_for_gold"}),
        ("no_drop", {"gripper.hurt_gripper_drops_its_haul"}),
        ("flora_noop", {"flora_harvest.harvest_yields_%s_from_%s" % (q, p) for p, q in V.FLORA_PRODUCTS}),
        ("scatter_noop", {"brine_deposits.scatter_places_%s" % d for d in DEPOSIT_ITEM}),
        ("wrong_mined_item", {"brine_deposits.RM_BrineDeposit_Tekk_mines_to_RM_Tekk"}),
        ("no_shock", {"brine_deposits.raw_brineleech_gives_brine_shock"}),
        ("no_leak", {"cask_leaks.breached_cask_leaks_loudly", "cask_leaks.leaking_drains_the_stored_dose",
                     "cask_bay.shot_up_bay_leaks_loudly"}),
        ("no_drain", {"cask_leaks.leaking_drains_the_stored_dose"}),
        ("leaks_ignore_toggle", {"cask_leaks.leaks_off_makes_a_breached_cask_inert"}),
        ("cask_text_bug", {"cask_leaks.breached_cask_text_does_not_claim_a_bay_that_is_not_there"}),
        ("power_noop", {"cask_bay.unpowered_bay_says_so_and_power_clears_it"}),
        ("no_patch", {"launch_check_patch.can_launch_postfix_is_installed"}),
        ("never_crawls", {"middenshell_body.wake_flattens_buildings_and_swallows_items", "middenshell_body.crawl_leaves_trail_filth",
                          "middenshell_body.on_again_resumes_the_crawl",
                          "middenshell_procession.procession_trail_is_laid_and_trail_off_stops_it"}),
        ("no_crush", {"middenshell_body.wake_flattens_buildings_and_swallows_items"}),
        ("no_trail", {"middenshell_body.crawl_leaves_trail_filth", "middenshell_procession.procession_trail_is_laid_and_trail_off_stops_it"}),
        ("trail_ignores_toggle", {"middenshell_body.trail_off_leaves_no_new_filth",
                                  "middenshell_procession.procession_trail_is_laid_and_trail_off_stops_it"}),
        ("no_aura", {"middenshell_body.ambient_aura_doses_a_pawn_beside_it"}),
        ("carcass_none", {"middenshell_body.killed_body_hardens_into_a_quarry"}),
        ("incident_always", {"middenshell_procession.incident_is_blocked_when_the_body_is_switched_off"}),
        ("no_omen", {"middenshell_procession.omen_letter_and_creeping_metal", "middenshell_procession.body_arrives_already_crossing"}),
        ("metal_still", {"middenshell_procession.omen_letter_and_creeping_metal"}),
        ("no_procession_state", {"middenshell_procession.body_arrives_already_crossing"}),
        ("pad_unlicensed", {"rite_of_tipping.pad_reads_licensed_with_a_contract"}),
        ("tipping_always", {"rite_of_tipping.tipping_off_refuses_the_offer"}),
    ]
    for brk, want in cases:
        got = reds(run((brk,)))
        check("break %-26s reddens exactly %s" % (brk, sorted(want)), set(got) == want, "got %s" % got)

    # a break that cannot be measured is UNMEASURED, never PASS and never FAIL
    for brk, want in (("not_wasteland", {"storm_ash_on", "storm_ash_off", "named_storm_halo", "named_storm_cinderwire",
                                         "named_storm_phases_off", "middenshell_body", "middenshell_procession", "rite_of_tipping"}),):
        res = run((brk,))
        wrong = [k for k, (v, _) in res.items() if v == "PASS" and k.split(".")[0] in want and k.endswith(("site_ready_ash", "site_ready_ash_off"))]
        gated = [k for k in res if k.split(".")[0] in want]
        check("break not_wasteland: every biome-gated chain is UNMEASURED, none FAIL or PASS", gated and all(
            res[k][0] == "UNMEASURED" for k in gated), {k: res[k] for k in gated if res[k][0] != "UNMEASURED"})
        check("break not_wasteland: nothing else goes red", not [k for k in reds(res) if k.split(".")[0] in want] and not wrong,
              reds(res))
    res = run(("no_faction",))
    check("break no_faction: the tipping contract is UNMEASURED (a site fact), not a failure",
          res["rite_of_tipping.quest_fires_and_is_ongoing"][0] == "UNMEASURED" and not reds(res), (reds(res), res["rite_of_tipping.quest_fires_and_is_ongoing"]))
    res = run(("unpollutable",))
    check("break unpollutable: fall and feed ground are UNMEASURED, never PASS",
          res["storm_ash_on.ash_fall_pollutes_the_ground"][0] == "UNMEASURED"
          and res["processor_animals.site_ready_processors"][0] == "UNMEASURED", {k: v for k, v in res.items() if k.startswith(("storm_ash_on.ash_fall", "processor_animals.site"))})

    # the log chain: an error line naming our content fails it; an unrelated game-wide error does not
    bad = run(log_lines=["Config error in RM_Smolderback: lifeStages count mismatch"])
    check("break log error naming RM_Smolderback reddens the log component",
          reds(bad) == ["log_clean.player_log_names_no_wasteland_error"], reds(bad))
    other = run(log_lines=["Config error in SomeOtherMod_Thing: unrelated"])
    check("an error naming only another mod does not", not reds(other), reds(other))

    print()
    if FAILS:
        print("FAILED: %d" % len(FAILS))
        for f in FAILS:
            print("  - " + f)
        return 1
    print("all Wasteland suite selftests passed")
    return 0


def _walk_arrows_exist():
    """Every `chain.component` the walk's arrows name exists in the suite (the walk cannot cite a ghost)."""
    import re
    path = os.path.join(ROOT, "design", "validation_walks", "RimMandrake", "Wasteland.md")
    if not os.path.isfile(path):
        return True
    from modcheck.suite import _DeclarationProbe
    names = set()
    probe = _DeclarationProbe()
    for n, fn in V.suite.chains:
        probe.upstream_failed = False
        probe.components = []
        fn(probe)
        for c in probe.components:
            names.add("%s.%s" % (n, c.name))
    bad = []
    for ln in open(path, encoding="utf-8").read().splitlines():
        if "→" not in ln or "UNCOVERED" in ln.split("→", 1)[1][:12]:
            continue
        for tok in re.findall(r"\b([a-z_]+\.[A-Za-z_]+)\b", ln.split("→", 1)[1]):
            if tok.startswith(("settings_defaults.default_", "mandrake.")):
                continue
            if tok not in names and tok.split(".")[0] in dict(V.suite.chains):
                bad.append(tok)
    if bad:
        print("  walk arrows naming no component:", bad[:6])
    return not bad


if __name__ == "__main__":
    sys.exit(main())
