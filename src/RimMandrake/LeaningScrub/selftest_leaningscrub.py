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

_CLASS_RE = re.compile(r"\n    (?:public |internal )?(?:static )?(?:sealed )?(?:partial )?class (\w+)")
_ARITY = {}


def cs_arities(type_name, method):
    """Parameter counts of every `public static` overload of `method` on the mod's own C# class `type_name` (read off
    Source/*.cs). The fake's static_call resolves through this exactly as jawa/static_call does live (args split on
    '|', the arg count picks the overload), so a caller passing "<form>|<mode>" to a one-parameter method fails here
    offline instead of live (LIVE 2026-10-16: twelve forms rows read 'No public static ProofForm with 2 params')."""
    key = (type_name, method)
    if key not in _ARITY:
        cls = type_name.rsplit(".", 1)[-1]
        found = set()
        for root, _dirs, files in os.walk(os.path.join(HERE, "Source")):
            for f in files:
                if not f.endswith(".cs"):
                    continue
                src = open(os.path.join(root, f), encoding="utf-8-sig").read()
                heads = [(m.start(), m.group(1)) for m in _CLASS_RE.finditer(src)]
                for i, (start, name) in enumerate(heads):
                    if name != cls:
                        continue
                    body = src[start:heads[i + 1][0] if i + 1 < len(heads) else len(src)]
                    for m in re.finditer(r"public static \w+(?:<[^>]*>)? %s\(([^)]*)\)" % re.escape(method), body):
                        a = m.group(1).strip()
                        found.add(0 if not a else a.count(",") + 1)
        _ARITY[key] = found
    return _ARITY[key]


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
                        pl["growth"] = 1.0 if "regrow_full" in b else 0.3
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
                      ("RM_ScrubDryThunderstorm", 1), ("RM_ScrubGrayPall", 1), ("RM_ScrubOvercast", 5), ("Rain", 0))]
            if "no_weather_entry" in self.broken:
                table = [r for r in table if r["weather"] != "RM_Gale"]
            if "stock_overcast" in self.broken:
                table = [r for r in table if r["weather"] != "RM_ScrubOvercast"] + [{"weather": "Overcast", "commonality": 5}]
            plants = [{"plant": n, "commonality": 0.1} for n in
                      ("RM_Fuzz", "RM_VenomvineThicket", "RM_DrippingVenomvine", "RM_TwitcherVenomvine",
                       "RM_HollowVenomvine", "RM_CrownVenomvine", "RM_Whipfuzz", "RM_Cruststar")
                      + V.FORM_PLANTS]
            ext = [] if "no_lean_ext" in self.broken else ["RM_LeanExtension"]
            return {"success": True, "foundCount": 1, "notFound": [], "defs": [{
                "defName": "RM_LeaningScrub", "fields": {
                    "baseWeatherCommonalities": table, "animalDensity": 1.8, "wildPlants": plants,
                    "modExtensions": ext}}]}
        if want and all(w.startswith("WeatherDef/RM_Scrub") for w in want):
            rows = []
            for w in want:
                n = w.split("/", 1)[1]
                off = 0.0 if ("twin_calm" in self.broken and n == "RM_ScrubGrayPall") else 0.4
                rows.append({"defName": n, "fields": {"windSpeedOffset": off, "windSpeedFactor": 1.0}})
            return {"success": True, "foundCount": len(rows), "notFound": [], "defs": rows}
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
        n = 0 if not args else len(args.split("|"))
        if n not in cs_arities(type, method):
            return {"success": False, "message": "No public static %s with %d params." % (method, n),
                    "details": {"available": sorted(cs_arities(type, method))}}
        if method == "ProofStamp":
            # The suite must name the pad it cleared ("mode@x,z"): LIVE 2026-10-16 the wooded run map held no ambient
            # clear 22-cell disc, so a bare mode is the UNMEASURED the live hook returned.
            if "@" not in args:
                return {"success": True, "result": "UNMEASURED: no unroofed, empty, fire-free 22-cell disc on this map"}
            args = args.split("@")[0]
            on = (args != "off" and "stamp_never" not in self.broken) or (args == "off" and "stamp_ignores_toggle" in self.broken)
            if args != "off":
                return {"success": True, "result": ("PASS sent=1 stamped=2" if on else
                                                     "FAIL: a six-fire blaze sent no stamper toward it")}
            return {"success": True, "result": ("FAIL: fireStampEnabled off but the herd answered" if on
                                                 else "PASS off sent=0 stamped=0")}
        if method == "ProofLean":
            if args == "off":
                return {"success": True, "result": "FAIL faced with the toggle off east=0 west=40" if "lean_ignores_toggle" in self.broken
                        else "PASS east=0 west=0 rolled=12"}
            return {"success": True, "result": "FAIL mixed lean east=3 west=37" if "lean_mixed" in self.broken
                    else "PASS east=0 west=40 rolled=12 windWest=True"}
        if method == "ProofGale":
            if self.weather != "RM_Gale":
                return {"success": True, "result": "UNMEASURED the Gale is not the current weather"}
            return {"success": True, "result": "FAIL RM_Gale does not carry RM_WeatherOverlay_GaleDust" if "gale_no_overlay" in self.broken
                    else "PASS weather=RM_Gale art=PLACEHOLDER (vanilla fog sheet) drew=True"}
        if method == "ProofRipple":
            hides = (args != "off" and "ripple_never" not in self.broken) or (args == "off" and "ripple_ignores_toggle" in self.broken)
            if args != "off":
                return {"success": True, "result": "PASS wind=True stallStill=True" if hides else
                        "FAIL: small wild creature on fuzz in wind was not hidden"}
            return {"success": True, "result": "FAIL: rippleEnabled off but the creature hid" if hides else "PASS off wind=False"}
        if method == "ProofStallHunt":
            hunts = (args != "off" and "stallhunt_never" not in self.broken) or (args == "off" and "stallhunt_ignores_toggle" in self.broken)
            if args != "off":
                return {"success": True, "result": "PASS hunting=True" if hunts else "FAIL: a stall hunter did not hunt"}
            return {"success": True, "result": "FAIL: stallHuntEnabled off but the hawk hunted" if hunts else "PASS off hunting=False"}
        if method == "ProofWarden":
            mode = args.split("@")[0]
            if mode == "tame":
                return {"success": True, "result": "FAIL: the tamed warden is still the lead leadBefore=True tamedIsLead=True"
                        if "tamed_still_leads" in self.broken else
                        "PASS leadBefore=True tamedIsLead=False nextIsLead=True listed=True"}
            if mode == "read":
                cut = getattr(self, "cut_from", None)
                d = 0.1 if (cut is not None and self.ticks >= cut + 120 and "tamed_tree_unwatched" not in self.broken) else 0.0
                return {"success": True, "result": "disturbance=%.3f live=2" % d}
            return {"success": True, "result": "CALM removed=1"}
        if method == "ProofManhunter":
            return {"success": True, "result": "FAIL: the manhunter was ordered to flee calmJob=Flee rageState=Manhunter rageJob=Flee"
                    if "bloom_scares_manhunter" in self.broken else
                    "PASS calmJob=Flee rageState=Manhunter rageJob=none"}
        if method == "ProofRefusesPawnCell":
            return {"success": True, "result": "FAIL: the refused cell lost its steel or grass planted=False steelKept=False"
                    if "genstep_tidies" in self.broken else "PASS planted=False steelKept=True grassKept=True"}
        if method == "ProofArmScavengers":
            on = args.startswith("on") or "arm_ignores_toggle" in self.broken
            drawn = on and "arm_draws_none" not in self.broken
            if args.startswith("on"):
                return {"success": True, "result": "PASS drawn=[RM_Surrik,RM_Ribbonwhip] notDrawn=[]" if drawn else
                        "FAIL: a hungry meat eater beside the arm chose something else drawn=[] notDrawn=[RM_Surrik]"}
            return {"success": True, "result": "FAIL: visslerArmFoodEnabled off but the arm drew drawn=[RM_Surrik]" if drawn
                    else "PASS off drawn=[] notDrawn=[RM_Surrik,RM_Ribbonwhip]"}
        if method == "ProofPyre" and args.startswith("thin@"):
            return {"success": True, "result": "FAIL: five fires as five islands read as a catch islandsThin=False clusterThin=False"
                    if "pyre_counts_fires" in self.broken else "PASS fires=5 gap=8 islandsThin=True clusterThin=False"}
        if method == "ProofPyre":
            if args == "defs":
                return {"success": True, "result": "FAIL: RM_CallingPyre_Venerated not gated on Ritualist"
                        if "pyre_ungated" in self.broken else "PASS defs"}
            if args == "off":
                return {"success": True, "result": "FAIL: callingPyreEnabled off but the gate said ok"
                        if "pyre_ignores_toggle" in self.broken else "PASS off: gate refuses"}
            if "@" not in args:     # the suite must name its crop patch: the scrub's own flora is fireproof (ban 9)
                return {"success": True, "result": "FAIL: the pyre lit fewer fires than the stamp threshold lit=0"}
            return {"success": True, "result": "FAIL: the pyre lit fewer fires than the stamp threshold lit=2"
                    if "pyre_no_fire" in self.broken else "PASS lit=6 came=3 raging=1"}
        if method == "ProofVaporator":
            return {"success": True, "result": "FAIL: no techprint for RM_WindVaporators"
                    if "vaporator_unlearnable" in self.broken else "PASS vaporator"}
        if method == "ProofInjections":
            wrecks = 0 if "no_farmstead" in self.broken else 3
            people = 0 if "no_camp_people" in self.broken else 4
            return {"success": True, "result": "PLACED sites=4 vaporatorWrecks=+%d campPeople=+%d farmers=True scavengers=False" % (wrecks, people)}
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
        if method == "ProofIslands":
            return {"success": True, "result": "FAIL: laid under half the target share islands=0" if "no_islands" in self.broken
                    else "PASS islands=40 planned=42 planted=8100 target=8250 rooms=70"}
        if method == "ProofCreep":
            if args == "on":
                return {"success": True, "result": "FAIL: a grown stand put no runner" if "no_creep" in self.broken
                        else "PASS mode=on laid=1 besideTestStand=1 runnerGrowth=0.05"}
            ran = (args == "off" and "creep_ignores_toggle" in self.broken) or (args == "cap" and "creep_ignores_cap" in self.broken)
            return {"success": True, "result": "FAIL: creep ran with %s" % args if ran else "PASS mode=%s laid=0" % args}
        if method == "ProofExempt":
            return {"success": True, "result": "FAIL: the venomvine exemption roster did not load" if "no_exempt" in self.broken
                    else "PASS roster RM_LeaningScrub_VenomvineExempt loaded"}
        if method == "ProofForm" and type and type.endswith("RM_FourFormsProof"):
            form, mode = args.split("|")
            on = self.on(dict(V.FOUR)[form])
            if mode == "on":
                acts = on and ("four_%s_never" % form) not in self.broken
                return {"success": True, "result": "PASS %s" % form if acts else "FAIL: %s did nothing" % form}
            acts = ("four_%s_ignores_toggle" % form) in self.broken
            return {"success": True, "result": "FAIL: %s off but it acted" % form if acts else "PASS off %s" % form}
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

    def t_pawn_force_incapacitate(self, pawn=None, action=None, **k):
        if action == "vanish" and pawn in self.pawns:
            del self.pawns[pawn]
            return {"success": True, "destroyedAfter": True}
        return {"success": pawn in self.pawns}

    def t_destroy_batch(self, rects="", categories="All", **k):
        rr = V_rect(rects)
        if "Pawn" in str(categories):    # live: refused; and no category ever removes a pawn
            return {"success": False, "message": "destroy_batch never removes pawns (DESTROY_BATCH_NEVER_KILLS_PAWNS_1)"}
        for tid in [i for i, t in self.things.items() if inrect(t["x"], t["z"], rr)]:
            del self.things[tid]
        self.claims = dict((s, t) for s, t in self.claims.items() if s in self.things)
        return {"success": True}

    def t_make_empty_room(self, rect=None, **k):
        self.rooms.append(V_rect(rect))
        return {"success": True}

    def t_set_roof_batch(self, ops="", **k):
        for op in ops.split(";"):
            d, nums = op.split(":")
            if d in ("None", "Clear"):
                ROOF_STRIPS.append(tuple(int(v) for v in nums.split(",")))
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
        if jobDef == "CutPlant":       # SCRUB_WARDEN_FIX_TAMED_BOSS_STILL_REIGNS: the cut arm (ProofWarden read)
            self.cut_from = self.ticks
            self.pawns[pawnId]["job"] = "CutPlant"
            return {"success": True, "accepted": True, "nowRunningRequested": True}
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
            # vanilla Plant.GetInspectString: "<N>% grown" plus "Growth rate: <R>%" (the trap 4cdec5dd8 fixed: the old
            # regex read the RATE line and failed a correct 30% stand)
            lines = ["%d%% grown" % int(100 * t.get("growth", 1)), "Growth rate: 100%"]
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

ROOF_STRIPS = []    # rects the suite opened to the sky (modcheck4 2026-10-16: unsupported mountain roof crushed actors)


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
    "tamed_still_leads": "sweetline.warden_tamed_lead_hands_over",
    "tamed_tree_unwatched": "sweetline.warden_tamed_tree_still_watched",
    "pyre_counts_fires": "edge_fixes.pyre_thin_line_follows_blaze",
    "bloom_scares_manhunter": "edge_fixes.bloom_spares_manhunter",
    "genstep_tidies": "edge_fixes.map_step_refuses_pawn_cell",
    "arm_draws_none": "edge_fixes.vissler_arm_draws_meat_eaters",
    "arm_ignores_toggle": "edge_fixes.vissler_arm_off_draws_none",
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
    "regrow_full": "dripping.dripping_survives_harvest",
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
    "four_strangler_never": "four_forms.strangler_acts",
    "four_weeper_never": "four_forms.weeper_acts",
    "four_sleeper_never": "four_forms.sleeper_acts",
    "four_lure_never": "four_forms.lure_acts",
    "four_strangler_ignores_toggle": "four_forms.strangler_toggle_off",
    "four_weeper_ignores_toggle": "four_forms.weeper_toggle_off",
    "four_sleeper_ignores_toggle": "four_forms.sleeper_toggle_off",
    "four_lure_ignores_toggle": "four_forms.lure_toggle_off",
    "no_comfort": "sweetline.felt_furniture_comfort",
    "comfort_ignores_toggle": "sweetline.felt_comfort_toggle_off_plain",
    "map_step_ignores_chance": "sweetline.map_step_chance_zero_plants_none",
    "visitors_ignore_toggle": "sweetline.visitors_toggle_off_quiet",
    "no_visits": "sweetline.visitors_come_and_leave_marks",
    "log_error": "log.log_clean",
    "stamp_never": "stamp.stamp_answers_a_blaze",
    "stamp_ignores_toggle": "stamp.stamp_toggle_off_ignores_fire",
    "stallhunt_never": "stallhunt.stallhawk_hunts_in_the_stall",
    "stallhunt_ignores_toggle": "stallhunt.stallhawk_toggle_off_idle",
    "ripple_never": "ripple.ripple_hides_small_creatures",
    "ripple_ignores_toggle": "ripple.ripple_toggle_off_nobody_hides",
    "pyre_ungated": "pyre.pyre_beliefs_gated_on_memes",
    "pyre_no_fire": "pyre.pyre_lights_fields_and_calls_herd",
    "pyre_ignores_toggle": "pyre.pyre_toggle_off_refuses",
    "vaporator_unlearnable": "injections.vaporator_learned_from_farmstead",
    "no_farmstead": "injections.map_holds_ruins_and_camps",
    "no_camp_people": "injections.map_holds_ruins_and_camps",
    "no_islands": "islands.islands_laid_share",
    "no_creep": "islands.creep_runner_unarmed",
    "creep_ignores_toggle": "islands.creep_toggle_off",
    "creep_ignores_cap": "islands.creep_cap_stops",
    "no_exempt": "islands.growth_exempt_from_explosive_growth",
    "stock_overcast": "defs.biome_weather_table",
    "twin_calm": "windlean.twins_carry_wind",
    "lean_mixed": "windlean.lean_faces_wind",
    "lean_ignores_toggle": "windlean.lean_toggle_off_vanilla",
    "gale_no_overlay": "windlean.gale_dust_overlay",
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
    # SITE guard (modcheck4 2026-10-16): every cleared pad must be opened to the sky before any tick, or a mountain
    # site's unsupported roof drops on the chain's actors (Koyo crushed in lash; the bloom cohort crushed).
    pads = set(re.findall(r'_prep\(t, "(\w+)"', open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()))
    centres = set((x + w // 2, z + h // 2) for x, z, w, h in ROOF_STRIPS)
    want = set((100 + V.PADS[p][0], 100 + V.PADS[p][1]) for p in pads if p in V.PADS)
    if want - centres:
        bad.append("pads cleared but never opened to the sky (roof strip): %s" % sorted(want - centres))
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
