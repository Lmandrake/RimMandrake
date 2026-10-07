#!/usr/bin/env python3
"""Offline selftest for LeaningScrub's validation.py: a scripted FAKE GAME that implements the
mod's behaviours, run (1) healthy -- every component must PASS -- and (2) once per mod behaviour
broken -- the named component must go FAIL and no other component may.

That second half is the proof every check can fail: each break is a mod defect (a patch that is
not armed, a toggle that gates nothing, an effect that never fires) and the suite must see it.
The fake encodes the response SHAPES validation.py assumes (read off the JawaBench [Tool]
descriptions and Pyrelands' live-measured helpers); it proves the predicates and wiring, not the
shapes -- those are UNPROVEN until the first live run.

    python3 src/RimMandrake/LeaningScrub/selftest_leaningscrub.py
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

spec = importlib.util.spec_from_file_location("lscrub_validation", os.path.join(HERE, "validation.py"))
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
V.time.sleep = lambda s: None                      # the fast-wait poll loop must not really sleep

from suite import TestContext                     # noqa: E402

BODY = {"RM_Thornhold": 0.4, "RM_Shirrel": 0.7, "RM_Dustflutter": 0.08, "RM_Crustweevil": 0.05,
        "RM_Fuzzrunner": 0.2, "RM_Vissler": 0.15, "Colonist": 1.0}
BLOOM = {"RM_Crustweevil", "RM_Fuzzrunner", "RM_Dustflutter", "RM_Vissler"}
SMALL_SPAWN_ONLY = None


def rect(s):
    return [int(v) for v in str(s).split(",")]


def inrect(x, z, r):
    return r[0] <= x < r[0] + r[2] and r[1] <= z < r[1] + r[3]


class Fake(object):
    def __init__(self, broken=()):
        self.broken = set(broken)
        self.ticks = 1000
        self.fast = False
        self.n = 0
        self.settings = dict((k, str(v)) for k, v in V.DEFAULTS.items())
        if "setting_missing" in self.broken:
            del self.settings["leanFireBias"]
        self.weather, self.things, self.pawns = "RM_ScrubWind", {}, {}
        self.rooms, self.claims, self.jobs, self.log = [], {}, {}, []
        self.walker_until, self.bloom_done, self.tick_hist = -1, False, 0
        self.paths = {}
        self.polluted = set()

    # ------------------------------------------------------------ session surface
    def _ticks(self):
        if self.fast:
            self.advance(2000)
        return self.ticks

    def track(self, *a, **k):
        pass

    def things_at(self, x, z):
        return []

    def call(self, tool, **p):
        h = getattr(self, "t_" + tool.split("/")[-1], None)
        if h is None:
            return {"success": True}
        return h(**p)

    def new(self, d, x, z, **kw):
        self.n += 1
        tid = "T%d" % self.n
        row = dict(id=tid, **dict(kw, x=x, z=z))
        row["def"] = d
        self.things[tid] = row
        return tid

    def of(self, d):
        return [t for t in self.things.values() if t["def"] == d]

    def on(self, f):
        return self.settings.get("modEnabled") == "True" and self.settings.get(f) == "True"

    # ------------------------------------------------------------ simulation
    def advance(self, n):
        while n > 0:
            d = min(250, n)
            n -= d
            self.ticks += d
            self.chunk(d)

    def chunk(self, d):
        b = self.broken
        # --- jobs
        for pid, job in list(self.jobs.items()):
            job["left"] -= d
            if job["left"] > 0:
                continue
            del self.jobs[pid]
            if job["kind"] == "smother" and "no_smother_bank" not in b:
                st = self.things.get(job["a"])
                bl = self.things.get(job["b"])
                if st and bl and bl.get("stackCount", 0) > 0:
                    bl["stackCount"] -= 1
                    self.claims[st["id"]] = self.ticks
                    st["smother_start"] = self.ticks
            if job["kind"] == "refuel" and "fuel_unpatched" not in b:
                bl = self.things.get(job["b"])
                if bl:
                    bl["stackCount"] = max(0, bl["stackCount"] - 10)
            if job["kind"] == "harvest":
                pl = self.things.get(job["a"])
                if pl:
                    self.new("RM_RawVenom", pl["x"], pl["z"], stackCount=3)
                    if "regrow_broken" in b:
                        del self.things[pl["id"]]
                    else:
                        pl["growth"] = 0.3
        # --- the Stall freeze and wandering
        for p in self.pawns.values():
            if p["faction"] != "none" or p["dead"]:
                continue
            gate = self.on("stallFreezeEnabled")
            if "master_ignored" in b:
                gate = self.settings.get("stallFreezeEnabled") == "True"
            if "freeze_ignores_toggle" in b:
                gate = True
            frozen = (self.weather == "RM_Stall" and BODY.get(p["kind"], 1) <= 0.5
                      and "no_freeze" not in b and gate)
            crown = [t for t in self.of("RM_CrownVenomvine")]
            if (self.weather == "RM_Stall" and p["kind"] == "RM_Dustflutter" and crown
                    and self.on("crownMobEnabled") and "no_crown" not in b) \
                    or ("crown_ignores_toggle" in b and p["kind"] == "RM_Dustflutter" and crown):
                p["x"], p["z"] = crown[0]["x"] + 2, crown[0]["z"]
                continue
            p["job"] = "Wait_Wander" if frozen else "GotoWander"
            if not frozen:
                p["x"] += 1
        # --- Gale: deafen
        if self.weather == "RM_Gale":
            gate = self.on("galeDeafenEnabled") or "deafen_ignores_toggle" in b
            for p in self.pawns.values():
                if p["faction"] != "player" or "no_deafen" in b or not gate:
                    continue
                roofed = any(inrect(p["x"], p["z"], r) for r in self.rooms)
                if roofed and "deafen_ignores_roof" not in b:
                    continue
                if "RM_GaleDeafened" not in p["hediffs"]:
                    p["hediffs"].append("RM_GaleDeafened")
        # --- turbines (2500 boundary)
        if self.ticks // 2500 != self.tick_hist:
            self.tick_hist = self.ticks // 2500
            if (self.weather == "RM_Gale" and self.on("galeTurbineSurgeEnabled")
                    and 0 < float(self.settings["galeTurbineBreakdownMtbDays"]) < 0.1
                    and "no_breakdown" not in b):
                for t in self.of("WindTurbine"):
                    if t.get("faction") == "PlayerColony":    # listerBuildings.allBuildingsColonist only
                        t["broken"] = True
            # smother maturation
            if self.on("smotherCraftEnabled") or "smother_ignores_toggle" in b:
                days = float(self.settings["smotherDays"])
                for sid, start in list(self.claims.items()):
                    if "no_mature" in b:
                        continue
                    if self.ticks >= start + days * 60000 and sid in self.things:
                        st = self.things.pop(sid)
                        del self.claims[sid]
                        self.new("RM_DeadVenomvine", st["x"], st["z"], stackCount=40)
        # --- ambient: a hot map gives a colonist whole-body heatstroke a while after spawning (LIVE 2026-10-07)
        for p in self.pawns.values():
            if p["faction"] == "player" and self.ticks - p.get("born", self.ticks) >= 150 \
                    and "Heatstroke" not in p["hediffs"]:
                p["hediffs"].append("Heatstroke")
        # --- lash
        for pl in self.of("RM_TwitcherVenomvine"):
            enabled = self.on("twitcherLashEnabled") or "lash_ignores_toggle" in b
            if "no_lash" in b or not enabled:
                continue
            if self.ticks < pl.get("ready", 0):
                continue
            for p in self.pawns.values():
                if p["faction"] == "player" and abs(p["x"] - pl["x"]) <= 1 and abs(p["z"] - pl["z"]) <= 1:
                    p["hediffs"].append("Cut")
                    pl["ready"] = self.ticks + (60 if "lash_repeats" in b else 3600)
                    break
        # --- runway bloom
        if self.ticks <= self.walker_until and not self.bloom_done:
            if self.on("runwayBloomEnabled") or "bloom_ignores_toggle" in b:
                if "no_bloom" not in b:
                    self.bloom_done = True
                    arms = 0
                    for p in self.pawns.values():
                        if p["kind"] in BLOOM and p["faction"] == "none":
                            p["flee_until"] = self.ticks + 300
                            if p["kind"] == "RM_Vissler" and arms < 4:
                                arms += 1
                                self.new("RM_VisslerArm", p["x"], p["z"], stackCount=1)
        # --- sweetline scratching (one ordered rub at a time)
        sc = getattr(self, "scratch", None)
        if sc and self.ticks >= sc["due"]:
            self.scratch = None
            trs = self.of(V.TREE)
            if trs and "no_scratch" not in b:
                self.new("WoolSheep", trs[0]["x"] + 1, trs[0]["z"], stackCount=36)
                trs[0]["felt"] = trs[0].get("felt", 0) + 2.25
        # --- sweetline wool
        for tr in self.of(V.TREE):
            tr.setdefault("wool", self.ticks + 3 * 60000)
            long_tick = self.ticks // 2000 != (self.ticks - d) // 2000
            if self.on("sweetlineStationsEnabled") and "no_wool" not in b and long_tick \
                    and self.ticks >= tr["wool"]:
                tr["wool"] = self.ticks + 5 * 60000
                self.new("RM_SweetlineWool", tr["x"], tr["z"], stackCount=5)
            tr.setdefault("visit", self.ticks + 8 * 60000)
            tr.setdefault("visits", 0)
            if self.on("sweetlineStationsEnabled") and long_tick and "no_visits" not in b \
                    and (self.on("sweetlineVisitorsEnabled") or "visitors_ignore_toggle" in b) \
                    and self.ticks >= tr["visit"]:
                tr["visit"] = self.ticks + 8 * 60000
                tr["visits"] += 1
                self.new("RM_SweetlineToken", tr["x"], tr["z"], stackCount=1)

    # ------------------------------------------------------------ tools
    def t_step_game_ticks(self, ticks=0, **k):
        self.advance(int(ticks))
        return {"success": True}

    def t_set_time_speed(self, speed=None, **k):
        self.fast = speed == "Ultrafast"
        return {"success": True}

    def t_time_set_ticks(self, ticks=0, **k):
        self.ticks = int(ticks)
        return {"success": True}

    def t_weather_set(self, weather=None, lockWeather=False, unlock=False, **k):
        if weather:
            self.weather = weather
        return {"success": True}

    def t_weather_get(self, **k):
        return {"success": True, "weather": {"current": self.weather}}

    def t_mod_settings_field(self, typeName=None, action=None, field=None, value=None, **k):
        if field not in self.settings:
            return {"success": False, "message": "no such field"}
        if action == "set":
            self.settings[field] = str(value)
        return {"success": True, "value": self.settings[field]}

    def t_get_defs(self, defs="", fields=None, limit=200, **k):
        want = [d for d in defs.split(";") if d]
        if want == ["BiomeDef/RM_LeaningScrub"]:
            table = [{"weather": w, "commonality": c} for w, c in
                     (("RM_ScrubWind", 28), ("RM_ScrubWindFog", 40), ("RM_Stall", 3), ("RM_Gale", 7),
                      ("DryThunderstorm", 1), ("Rain", 0))]
            if "no_weather_entry" in self.broken:
                table = [r for r in table if r["weather"] != "RM_Gale"]
            plants = [{"plant": n, "commonality": 0.1} for n in
                      ("RM_Fuzz", "RM_VenomvineThicket", "RM_DrippingVenomvine", "RM_TwitcherVenomvine",
                       "RM_HollowVenomvine", "RM_CrownVenomvine", "RM_Whipfuzz", "RM_Cruststar")
                      + V.FORM_PLANTS]
            ext = [] if "no_lean_ext" in self.broken else ["RM_LeanExtension"]
            return {"success": True, "foundCount": 1, "notFound": [], "defs": [{
                "defName": "RM_LeaningScrub", "fields": {
                    "baseWeatherCommonalities": table, "animalDensity": 1.8, "wildPlants": plants,
                    "modExtensions": ext}}]}
        if want == ["ThingDef/%s" % V.TREE]:
            return {"success": True, "foundCount": 1, "notFound": [],
                    "defs": [{"defName": V.TREE, "fields": {"label": "sweetline tree"}}]}
        missing = [d for d in want if d.endswith("NoSuchDef_Probe")]
        if "missing_def" in self.broken and want and want[0] in V.SHIPPED:
            missing.append(want[3])
        return {"success": True, "notFound": missing, "foundCount": len(want) - len(missing)}

    def t_get_def(self, defName=None, **k):
        if defName == "RM_VisslerArm":
            return {"success": True, "comps": ([] if "arm_not_rotting" in self.broken
                                               else [{"class": "RimWorld.CompProperties_Rottable"}])
                    or [{"class": "RimWorld.CompProperties_Forbiddable"}]}
        comps = [{"class": "RimMandrake.EnvironmentalHazards.RM_CompProperties_BodySizeBarrier"}]
        if "thicket_unpatched" not in self.broken:
            comps.append({"class": "RimMandrake.LeaningScrub.RM_CompProperties_Smotherable"})
        return {"success": True, "comps": comps}

    def t_harmony_patches(self, typeName=None, methodName=None, **k):
        for typ, meth, kind, patch in V.RULES:
            if (typ, meth) == (typeName, methodName):
                armed = not ("rule_unarmed" in self.broken and typ == "JobGiver_Wander")
                row = {"owner": V.HARMONY_OWNER, "patchMethod": "RimMandrake.LeaningScrub." + patch}
                m = {"method": meth, "prefixes": [], "postfixes": []}
                if armed:
                    m[kind].append(row)
                return {"success": True, "methods": [m]}
        return {"success": True, "methods": []}

    def t_drain_log(self, contains=None, errorsOnly=False, limit=50, **k):
        msgs = []
        if "log_error" in self.broken and contains == "LeaningScrub":
            msgs = [{"type": "Error", "text": "[RM LeaningScrub] stall-freeze: rule NOT armed"}]
        return {"success": True, "totalInBuffer": 321, "messages": msgs}

    def t_spawn_pawn(self, kindDef=None, x=0, z=0, faction="none", count=1, **k):
        self.n += 1
        pid = "P%d" % self.n
        self.pawns[pid] = dict(id=pid, kind=kindDef, x=x, z=z, faction=faction, dead=False, hediffs=[],
                               flee_until=0, born=self.ticks)
        return {"success": True, "pawns": [{"id": pid}]}

    def t_list_pawns(self, rect=None, includeHealth=False, limit=500, **k):
        rr = V_rect(rect) if rect else None
        rows = []
        for p in self.pawns.values():
            if rr and not inrect(p["x"], p["z"], rr):
                continue
            row = {"id": p["id"], "kindDef": p["kind"], "x": p["x"], "z": p["z"],
                   "faction": None if p["faction"] == "none" else p["faction"], "dead": p["dead"],
                   "downed": False, "intelligence": "Humanlike" if p["kind"] == "Colonist" else "Animal"}
            if includeHealth:
                row["health"] = {"hediffs": [{"def": h, "part": "Torso" if h == "Cut" else None}
                                             for h in p["hediffs"]]}
            rows.append(row)
        return {"success": True, "pawns": rows}

    def t_site_state(self, **k):
        return {"success": True, "pawns": [
            {"id": p["id"], "job": "Flee" if self.ticks < p.get("flee_until", 0) else p.get("job", "Wait_Wander")}
            for p in self.pawns.values()]}

    def t_list_things(self, defName=None, rect=None, limit=1, **k):
        rr = V_rect(rect) if rect else None
        rows = [t for t in self.of(defName) if not rr or inrect(t["x"], t["z"], rr)]
        return {"success": True, "scanned": 100, "countMatched": len(rows),
                "things": [dict(t) for t in rows[:limit]]}

    def t_static_call(self, type=None, method=None, args="", **k):
        if method == "ProofStamp":
            on = (args != "off" and "stamp_never" not in self.broken) or (args == "off" and "stamp_ignores_toggle" in self.broken)
            if args != "off":
                return {"success": True, "result": ("PASS sent=1 stamped=2" if on else
                                                     "FAIL: a six-fire blaze sent no stamper toward it")}
            return {"success": True, "result": ("FAIL: fireStampEnabled off but the herd answered" if on
                                                 else "PASS off sent=0 stamped=0")}
        if method == "ProofComfortDelta":
            on = self.on("sweetlineFeltComfortEnabled") or "comfort_ignores_toggle" in self.broken
            d = 0.10 if on and "no_comfort" not in self.broken else 0.0
            return {"success": True, "result": "DELTA %.2f" % d}
        if method == "ProofVisuals":
            on = self.on("runwayBloomEnabled")
            return {"success": True, "result": "SWAYING %d HOLES +%d ANSWERED %d" % ((1, 1, 2) if on else (0, 0, 0))}
        if method == "ProofMapStep":
            chance = float(args.split("|")[1])
            n = 0
            if (chance > 0 or "map_step_ignores_chance" in self.broken) and "no_map_step" not in self.broken:
                n = 1
                self.new(V.TREE, 5, 5, growth=1.0, stackCount=1)
            return {"success": True, "result": "PLANTED %d" % n}
        if method == "ProofForm":
            form, mode = args.split("|")
            on = self.on(V.FORM_TOGGLES[form])
            if mode == "on":
                acts = on and ("%s_never" % form) not in self.broken
                return {"success": True, "result": "PASS %s" % form if acts else "FAIL: %s did nothing" % form}
            acts = ("%s_ignores_toggle" % form) in self.broken      # the hook flips the setting off itself
            return {"success": True, "result": "FAIL: %s off but it acted" % form if acts else "PASS off %s" % form}
        if method != "ProofOrderScratch":
            return {"success": False, "message": "No public static " + str(method)}
        on = self.on("sweetlineStationsEnabled") and self.on("sweetlineScratchingEnabled")
        if not on and "scratch_ignores_toggle" not in self.broken:
            return {"success": True, "result": "REFUSED: scratching is off"}
        self.scratch = {"due": self.ticks + 700}
        return {"success": True, "result": "ORDERED P1 -> T1"}

    def t_spawn_batch(self, ops="", **k):
        for op in ops.split(";"):
            d, nums = op.split(":")
            n = [int(v) for v in nums.split(",")]
            self.new(d, n[0], n[1], stackCount=n[2] if len(n) > 2 else 1, born=self.ticks)
        return {"success": True}

    def t_set_thing_props(self, thing=None, faction=None, **k):
        t = self.things.get(thing)
        if t is None:
            return {"success": False, "message": "no thing %r" % thing}
        if faction is not None:
            t["faction"] = None if faction.lower() in ("null", "none") else faction
        return {"success": True, "changed": ["faction"] if faction is not None else [], "skipped": []}

    def t_set_pollution(self, rect="", polluted=True, **k):
        x, z, w, h = [int(v) for v in rect.split(",")]
        cells = set((cx, cz) for cx in range(x, x + w) for cz in range(z, z + h))
        if "no_pollute" in self.broken:
            return {"success": True, "cellsRequested": len(cells), "cellsEverPollutable": len(cells), "cellsChanged": 0}
        self.polluted = (self.polluted | cells) if polluted else (self.polluted - cells)
        return {"success": True, "cellsRequested": len(cells), "cellsEverPollutable": len(cells),
                "cellsChanged": len(cells)}

    def t_set_plants(self, ops="", growth=1.0, **k):
        for op in ops.split(";"):
            d, nums = op.split(":")
            n = [int(v) for v in nums.split(",")]
            if d == "CLEAR":
                continue
            if "set_plants_drops" in self.broken and d == "RM_Cruststar":
                continue
            for cx in range(n[0], n[0] + (n[2] if len(n) > 2 else 1)):
                for cz in range(n[1], n[1] + (n[3] if len(n) > 3 else 1)):
                    # PlantUtility.CanEverPlantAt: a PollutedOnly plant is rejected on a clean cell (LIVE 2026-10-07)
                    if d in V.POLLUTED_ONLY and (cx, cz) not in self.polluted:
                        continue
                    tid = self.new(d, cx, cz, growth=growth, stackCount=1)
                    if d == V.TREE:
                        self.things[tid]["wool"] = self.ticks + 3 * 60000     # staggered first shed
                        if self.on("sweetlineGuardiansEnabled") and "no_roost" not in self.broken:
                            for dx in (1, -1):                                # two roosting bark-wardens
                                wid = self.new("RM_Barkwarden", cx + dx, cz, stackCount=1)   # inspectable thing ...
                                self.pawns[wid] = dict(id=wid, kind="RM_Barkwarden", x=cx + dx, z=cz, faction="none",
                                                       dead=False, hediffs=[], flee_until=0)   # ... and a pawn row (the suite lists pawns)
        return {"success": True}

    def t_destroy_batch(self, rects="", categories="All", **k):
        rr = V_rect(rects)
        if categories != "Pawn":
            for tid in [i for i, t in self.things.items() if inrect(t["x"], t["z"], rr)]:
                del self.things[tid]
        if categories in ("Pawn", "All"):
            for pid in [i for i, p in self.pawns.items() if inrect(p["x"], p["z"], rr)]:
                del self.pawns[pid]
        self.claims = dict((s, t) for s, t in self.claims.items() if s in self.things)
        return {"success": True}

    def t_make_empty_room(self, rect=None, **k):
        self.rooms.append(V_rect(rect))
        return {"success": True}

    def t_get_roof_batch(self, rects=None, **k):
        return {"success": True, "roofedCells": 49}

    def t_pawn_health(self, pawn=None, action=None, hediff=None, **k):
        p = self.pawns[pawn]
        if action == "remove" and hediff in p["hediffs"]:
            p["hediffs"].remove(hediff)
        return {"success": True}

    def t_pawn_flight(self, pawn=None, **k):
        return {"success": True, "pawns": [{"id": pawn, "canEverFly": "no_fly" not in self.broken,
                                            "maxFlightTimeStat": 6.0}]}

    def fuel(self, tid):
        """Campfire fuel: spawned full (20), burns 10 per day (Core CompProperties_Refuelable)."""
        t = self.things.get(tid) or {}
        return max(0.0, 20 - 10.0 * (self.ticks - t.get("born", self.ticks)) / 60000)

    def t_ordered_job(self, pawnId=None, jobDef=None, targetAId=None, targetBId=None, **k):
        kind = {"RM_SmotherVenomvine": "smother", "Refuel": "refuel", "Harvest": "harvest"}.get(jobDef)
        if kind == "refuel" and 20 - self.fuel(targetAId) < 1:   # JobDriver_Refuel ends on CompRefuelable.IsFull
            return {"success": False, "accepted": True, "afterJobDef": "Wait_MaintainPosture"}
        self.jobs[pawnId] = {"kind": kind, "a": targetAId, "b": targetBId, "left": 800}
        return {"success": True, "accepted": True, "nowRunningRequested": True}

    def t_order_pawn(self, pawnId=None, x=None, z=None, **k):
        self.walker_until, self.bloom_done = self.ticks + 400, False
        self.pawns[pawnId]["x"] += 0
        return {"success": True}

    def t_inspect_string(self, thingIds=None, **k):
        t = self.things.get(thingIds)
        if t is None:
            return {"success": True, "things": []}
        lines, label = [], t["def"]
        d = t["def"]
        if d == "WindTurbine":
            lines = ["Broken down"] if t.get("broken") else [
                "Power output: %d W" % (round(1000 * (1.3 if self.weather == "RM_Gale" and
                                                      self.on("galeTurbineSurgeEnabled")
                                                      and "no_surge" not in self.broken else 1.0)))]
        elif d == "RM_TwitcherVenomvine":
            if self.on("twitcherLashEnabled") or "lash_ignores_toggle" in self.broken:
                lines = ["Poised to strike." if self.ticks >= t.get("ready", 0)
                         else "Spent, drooping: strikes again in 1 hour."]
        elif d == "RM_HollowVenomvine" and t["id"] in self.claims:
            due = self.ticks >= self.claims[t["id"]] + float(self.settings["smotherDays"]) * 60000
            lines = ["Smothered: dead through, ready to fall." if due
                     else "Smothered under a blanket: dead wood in 2 days."]
        elif d == "RM_DrippingVenomvine":
            lines = ["Growth: %d%%" % int(100 * t.get("growth", 1))]
        elif d == "Campfire":
            lines = ["Fuel: %d / 20" % round(self.fuel(t["id"]))]
        elif d == V.TREE and (self.on("sweetlineStationsEnabled") or "station_ignores_toggle" in self.broken):
            if "no_name" not in self.broken:
                label = "Ashveil (sweetline tree)"
            lines = ["Loose sweetline felt falls in 4 days."]
            if t.get("felt", 0) >= 1:
                lines.append("Felted into the bark: %d (harvestable)." % int(t["felt"]))
            if self.on("sweetlineGuardiansEnabled") and "no_roost" not in self.broken:
                lines.append("Bark-wardens roost here (2). Calm.")
            if t.get("visits") and (self.on("sweetlineVisitorsEnabled") or "visitors_ignore_toggle" in self.broken):
                lines.insert(0, "Visitors remembered: %d camps, 0 pilgrims." % t["visits"])
        elif d == V.TREE:
            label = "sweetline tree"
        elif d == "RM_Barkwarden":
            label, lines = "bark-warden", ["Roosting in the crown of Ashveil."]
        return {"success": True, "things": [{"id": t["id"], "label": label, "inspect": lines}]}


def V_rect(s):
    return rect(s)


# ------------------------------------------------------------------ the runner

def run(broken=()):
    game = Fake(broken)
    results = {}
    for name, fn in V.suite.chains:
        t = TestContext(game, anchor=(100, 100))
        try:
            fn(t)
        except Exception as ex:            # a chain-level crash is a script bug
            results[name + ".<CRASH>"] = ("CRASH", "%s: %s" % (type(ex).__name__, ex))
            continue
        for c in t.components:
            results["%s.%s" % (name, c.name)] = (c.verdict, c.detail)
    return results


# break -> the component that must go FAIL
BREAKS = {
    "missing_def": "defs.defs_resolve",
    "no_roost": "sweetline.guardians_roost_on_spawn",
    "no_weather_entry": "defs.biome_weather_table",
    "no_lean_ext": "defs.biome_lean_extension",
    "rule_unarmed": "patches.rules_armed",
    "thicket_unpatched": "patches.thicket_smotherable",
    "arm_not_rotting": "patches.vissler_arm_is_rotting_meat",
    "fuel_unpatched": "patches.dead_venomvine_fuels_fire",
    "setting_missing": "settings.defaults",
    "set_plants_drops": "flora.flora_spawns",
    "no_pollute": "flora.flora_spawns",          # LIVE 2026-10-07: RM_Grellspine on a clean cell
    "no_fly": "fauna.dustflutter_can_fly",
    "no_freeze": "stall.stall_freezes_small",
    "freeze_ignores_toggle": "stall.stall_toggle_off_wanders",
    "master_ignored": "stall.stall_master_off_wanders",
    "no_deafen": "gale.gale_deafens_outdoors",
    "deafen_ignores_roof": "gale.gale_spares_roofed",
    "deafen_ignores_toggle": "gale.gale_deafen_toggle_off",
    "no_surge": "gale.gale_turbine_surge",
    "no_breakdown": "gale.gale_turbine_breakdown",
    "lash_ignores_toggle": "lash.lash_toggle_off_quiet",
    "no_lash": "lash.lash_strikes_once",
    "lash_repeats": "lash.lash_strikes_once",
    "no_smother_bank": "smother.smother_claims_stands",
    "smother_ignores_toggle": "smother.smother_off_holds_claims",
    "no_mature": "smother.smother_matures_to_dead_wood",
    "regrow_broken": "dripping.dripping_survives_harvest",
    "crown_ignores_toggle": "crown.crown_toggle_off_stays_away",
    "no_crown": "crown.crown_mob_gathers",
    "bloom_ignores_toggle": "bloom.bloom_toggle_off_quiet",
    "no_bloom": "bloom.bloom_answers_a_walker",
    "station_ignores_toggle": "sweetline.station_toggle_off_plain",
    "no_name": "sweetline.station_named_and_timed",
    "no_wool": "sweetline.station_sheds_wool",
    "no_scratch": "sweetline.scratch_drops_coat",
    "scratch_ignores_toggle": "sweetline.scratch_toggle_off_refused",
    "no_map_step": "sweetline.map_step_plants_one_or_two",
    "no_comfort": "sweetline.felt_furniture_comfort",
    "comfort_ignores_toggle": "sweetline.felt_comfort_toggle_off_plain",
    "map_step_ignores_chance": "sweetline.map_step_chance_zero_plants_none",
    "visitors_ignore_toggle": "sweetline.visitors_toggle_off_quiet",
    "no_visits": "sweetline.visitors_come_and_leave_marks",
    "log_error": "log.log_clean",
    "stamp_never": "stamp.stamp_answers_a_blaze",
    "stamp_ignores_toggle": "stamp.stamp_toggle_off_ignores_fire",
}
for _form, _plant in V.FORMS:
    BREAKS["%s_never" % _form] = "forms.%s_acts" % _form
    BREAKS["%s_ignores_toggle" % _form] = "forms.%s_toggle_off" % _form


def main():
    bad = []
    healthy = run()
    notpass = dict((k, v) for k, v in healthy.items() if v[0] != "PASS")
    n_comp = len(healthy)
    if notpass:
        bad.append("healthy run: %d of %d components not PASS: %s" % (len(notpass), n_comp, notpass))
    declared = len(V.suite.components_declared())
    if declared != n_comp:
        bad.append("declared %d components but the run produced %d" % (declared, n_comp))
    for brk, target in sorted(BREAKS.items()):
        res = run([brk])
        reds = sorted(k for k, v in res.items() if v[0] in ("FAIL", "CRASH"))
        if reds != [target]:
            bad.append("break %-24s expected only %s FAIL, got %s" % (brk, target, reds))
    print("selftest LeaningScrub: %d components healthy-PASS %d/%d; %d breaks each turn exactly "
          "their component red" % (n_comp, n_comp - len(notpass), n_comp,
                                   len(BREAKS) - len([1 for b in bad if b.startswith("break ")])))
    for b in bad:
        print("  BAD:", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
