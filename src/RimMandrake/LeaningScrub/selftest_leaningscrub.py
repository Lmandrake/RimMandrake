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
        # --- sweetline wool
        for tr in self.of(V.TREE):
            tr.setdefault("wool", self.ticks + 3 * 60000)
            long_tick = self.ticks // 2000 != (self.ticks - d) // 2000
            if self.on("sweetlineStationsEnabled") and "no_wool" not in b and long_tick \
                    and self.ticks >= tr["wool"]:
                tr["wool"] = self.ticks + 5 * 60000
                self.new("RM_SweetlineWool", tr["x"], tr["z"], stackCount=5)

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
                       "RM_HollowVenomvine", "RM_CrownVenomvine", "RM_Whipfuzz", "RM_Cruststar")]
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
                               flee_until=0)
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
                row["health"] = {"hediffs": [{"def": h} for h in p["hediffs"]]}
            rows.append(row)
        return {"success": True, "pawns": rows}

    def t_site_state(self, **k):
        return {"success": True, "pawns": [
            {"id": p["id"], "job": "Flee" if self.ticks < p.get("flee_until", 0) else "Wait_Wander"}
            for p in self.pawns.values()]}

    def t_list_things(self, defName=None, rect=None, limit=1, **k):
        rr = V_rect(rect) if rect else None
        rows = [t for t in self.of(defName) if not rr or inrect(t["x"], t["z"], rr)]
        return {"success": True, "scanned": 100, "countMatched": len(rows),
                "things": [dict(t) for t in rows[:limit]]}

    def t_spawn_batch(self, ops="", **k):
        for op in ops.split(";"):
            d, nums = op.split(":")
            n = [int(v) for v in nums.split(",")]
            self.new(d, n[0], n[1], stackCount=n[2] if len(n) > 2 else 1)
        return {"success": True}

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
                    tid = self.new(d, cx, cz, growth=growth, stackCount=1)
                    if d == V.TREE:
                        self.things[tid]["wool"] = self.ticks + 3 * 60000     # staggered first shed
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

    def t_ordered_job(self, pawnId=None, jobDef=None, targetAId=None, targetBId=None, **k):
        kind = {"RM_SmotherVenomvine": "smother", "Refuel": "refuel", "Harvest": "harvest"}.get(jobDef)
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
            lines = ["Fuel: 10"]
        elif d == V.TREE and (self.on("sweetlineStationsEnabled") or "station_ignores_toggle" in self.broken):
            if "no_name" not in self.broken:
                label = "Ashveil (sweetline tree)"
            lines = ["Snagged giant-wool sheds in 4 days."]
        elif d == V.TREE:
            label = "sweetline tree"
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
    "no_weather_entry": "defs.biome_weather_table",
    "no_lean_ext": "defs.biome_lean_extension",
    "rule_unarmed": "patches.rules_armed",
    "thicket_unpatched": "patches.thicket_smotherable",
    "fuel_unpatched": "patches.dead_venomvine_fuels_fire",
    "setting_missing": "settings.defaults",
    "set_plants_drops": "flora.flora_spawns",
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
    "log_error": "log.log_clean",
}


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
