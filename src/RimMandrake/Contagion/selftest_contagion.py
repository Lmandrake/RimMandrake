#!/usr/bin/env python3
"""Offline selftest for Contagion's validation.py: a scripted FAKE GAME that implements the mod's
behaviours (read off the C# in Source/ and the XML in Defs/), run (1) healthy -- every component must
PASS -- and (2) once per mod behaviour broken -- the named component must go FAIL and no other
component may.

That second half is the proof every check can fail: each break is a mod defect (a gate that ignores its
toggle, an effect that never fires, a patch that matched nothing) and the suite must see it.
The fake encodes the response SHAPES validation.py assumes (read off the JawaBench [Tool]
descriptions); it proves the predicates and wiring, not the shapes -- those are UNPROVEN until the
first live run (the walk lists them).

    python3 src/RimMandrake/Contagion/selftest_contagion.py
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

spec = importlib.util.spec_from_file_location("contagion_validation", os.path.join(HERE, "validation.py"))
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
V.time.sleep = lambda s: None                      # the fast-wait poll loop must not really sleep

from suite import TestContext                     # noqa: E402

_NULL = open(os.devnull, 'w')

NATIVES = set(V.WILD_ANIMALS) | {"RM_TheUnfinished"}
ARMORED = {"RM_Scaldhide", "RM_Crispling"}
LEAKERS = {"RM_Scorchpod"}
ORGANS = ["Kidney", "Liver", "Lung", "Heart", "RM_GrownLeg", "RM_GrownArm"]


def rect(s):
    return [int(v) for v in str(s).replace(";", ",").split(",")][:4]


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
            del self.settings["coalescenceEnabled"]
        if "default_wrong" in self.broken:
            self.settings["burnFrequency"] = "2.0"
        self.weather, self.biome = "Clear", "TemperateForest"
        self.things, self.pawns, self.conds, self.roofs = {}, {}, [], []
        self.next_burn, self.bills = -1, set()

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

    def on(self, f):
        return self.settings.get(f) == "True"

    def num(self, f):
        return float(self.settings[f])

    def newid(self, p):
        self.n += 1
        return "%s%d" % (p, self.n)

    def new(self, d, x, z, **kw):
        tid = self.newid("T")
        self.things[tid] = dict(id=tid, x=x, z=z, stackCount=1, **dict(kw, **{"def": d}))
        return tid

    def of(self, *defs):
        return [t for t in self.things.values() if t["def"] in defs]

    def pawn(self, kind, x, z, faction):
        pid = self.newid("P")
        p = dict(id=pid, kind=kind, x=x, z=z, faction=faction, dead=False, hed=[], inv=[], mental=None,
                 vanished=False)
        self.pawns[pid] = p
        if kind == "RM_TheUnfinished":
            if "no_limbs" not in self.broken:
                for h in V.LIMB_POOL[:2]:
                    self.addh(p, h, 0.1)
            if "no_lifespan" not in self.broken:
                self.addh(p, "RM_UnfinishedUnraveling", 0.2)
        if kind == V.HOST:
            p["next_spawn"] = self.ticks + 36000
        return p

    def addh(self, p, d, sev):
        for h in p["hed"]:
            if h["def"] == d:
                h["severity"] += sev
                return h
        h = {"def": d, "severity": sev}
        p["hed"].append(h)
        return h

    def is_native(self, p):
        return p["kind"] in NATIVES

    def exposed(self, x, z):
        return not any(inrect(x, z, r) for r in self.roofs)

    # ------------------------------------------------------------ simulation
    def advance(self, n):
        while n > 0:
            d = min(250, n)
            n -= d
            self.ticks += d
            self.step()

    def cond(self, name):
        for c in self.conds:
            if c["def"] == name:
                return c
        return None

    def start_cond(self, name, dur):
        c = self.cond(name)
        if c:
            c["until"] = max(c["until"], self.ticks + dur)
            return c
        c = {"def": name, "start": self.ticks, "until": self.ticks + dur}
        self.conds.append(c)
        return c

    def step(self):
        b = self.broken
        contagion = self.biome == V.BIOME
        self.conds = [c for c in self.conds if self.ticks <= c["until"]]
        # --- the Cloud Repulsor
        for r in self.of(V.REPULSOR):
            enabled = self.on("cloudRepulsorEnabled") or "rep_ignores_toggle" in b
            if not enabled or not r.get("power"):
                r["warm"] = 0
                continue
            if r["warm"] < 2500:
                r["warm"] += 250
                continue
            if contagion:
                if "no_force_burn" not in b:
                    self.start_cond(V.BURN_COND, 750)
            elif "rep_no_clear" not in b:
                self.start_cond(V.CLEAR_COND, 750)
                if "rep_forces_burn_offbiome" in b:
                    self.start_cond(V.BURN_COND, 750)
            if "rep_sticky" in b and not contagion:
                self.start_cond(V.CLEAR_COND, 10 ** 9)
        # --- the sky clock (Contagion maps only)
        burn = self.cond(V.BURN_COND)
        if contagion:
            if burn:
                self.next_burn = -1
            else:
                on = self.on("burnEnabled") or "sched_ignores_toggle" in b
                if not on:
                    self.next_burn = -1
                elif self.next_burn < 0:
                    freq = 1.0 if "freq_ignored" in b else max(0.05, self.num("burnFrequency"))
                    self.next_burn = self.ticks + int(3 * 60000 / freq)
                elif self.ticks >= self.next_burn and "no_schedule" not in b:
                    self.start_cond(V.BURN_COND, 2000)
                    self.next_burn = -1
        burn = self.cond(V.BURN_COND)
        # --- weather the Burn forces
        if contagion and burn and self.ticks - burn["start"] >= 600:
            self.weather = "Clear" if "weather_not_burn" in b else V.BURN_WEATHER
        elif self.weather == V.BURN_WEATHER:
            self.weather = "RM_ContagionBloom"
        # --- Burn pressure on everything exposed
        if contagion and burn and self.weather == V.BURN_WEATHER and \
                (self.on("burnEnabled") or "harm_ignores_burn_toggle" in b):
            f = self.num("burnDamageFactor")
            if f > 0 or "zero_dmg_hurts" in b:
                for p in list(self.pawns.values()):
                    if p["dead"] or p["vanished"] or not self.exposed(p["x"], p["z"]):
                        continue
                    if self.is_native(p):
                        if p["kind"] in ARMORED and "armored_hurt" not in b:
                            continue
                        if "native_unhurt" not in b:
                            self.addh(p, "Burn", 3 * max(f, 0.5))
                        if p["kind"] not in LEAKERS and "no_dive" not in b:
                            roof = self.roofs[0]
                            p["x"], p["z"] = roof[0] + 2, roof[1] + 2
                    elif "no_dose" not in b:
                        self.addh(p, "RM_BurnDose", 0.02 * max(f, 0.5))
            if "dose_roofed" in b:
                for p in self.pawns.values():
                    if p["kind"] == "Colonist" and not self.exposed(p["x"], p["z"]):
                        self.addh(p, "RM_BurnDose", 0.02)
        # --- the spawner (the host's own comp)
        for p in list(self.pawns.values()):
            if p["kind"] == V.HOST and not p["dead"] and not p["vanished"] and "next_spawn" in p:
                gate = self.on("unfinishedSpawnerEnabled") or "spawner_ignores_toggle" in b
                if gate and self.ticks >= p["next_spawn"] and "no_bud" not in b:
                    near = [q for q in self.pawns.values() if q["kind"] == "RM_TheUnfinished"
                            and abs(q["x"] - p["x"]) <= 20 and abs(q["z"] - p["z"]) <= 20
                            and not q["vanished"]]
                    if len(near) < 3 or "spawner_no_cap" in b:
                        for _ in range(4 if "spawner_no_cap" in b else 1):
                            self.pawn("RM_TheUnfinished", p["x"] + 1, p["z"], "none")
                    p["next_spawn"] = self.ticks + 36000
        # --- lifespans and gestation
        for p in list(self.pawns.values()):
            for h in list(p["hed"]):
                if h["def"] == "RM_UnfinishedUnraveling":
                    h["severity"] += 0.3 * 250 / 60000.0
                    if h["severity"] >= 1.0:
                        self.die(p)
                if h["def"] == "RM_AmoebaGestation":
                    h["severity"] += 0.25 * 250 / 60000.0
                    if h["severity"] >= 0.999:
                        self.complete_gestation(p, h)
        # --- the Coalescence
        for c in self.of(V.COALESCENCE):
            if self.cond(V.BURN_COND) and "no_collapse" not in b:
                self.collapse(c)
                continue
            if not (self.on("coalescenceEnabled") or "coal_ignores_toggle" in b):
                continue
            if self.ticks - c["last_growth"] >= 6000 and "no_passive" not in b:
                c["last_growth"] = self.ticks
                c["mass"] += 1
            # Building_RM_Coalescence.Absorb, per 250-tick pass: one inside the ring (footprint expanded by 1)
            # is eaten; one further out is ordered a step closer and eaten on a LATER pass. "slow_walkers"
            # (impaired Unfinished, live 2026-10-08) take three passes per step: the harness must still PASS.
            for p in list(self.pawns.values()):
                if p["kind"] == "RM_TheUnfinished" and not p["vanished"] and not p["mental"] \
                        and "no_absorb" not in b and abs(p["x"] - c["x"]) <= 18 and abs(p["z"] - c["z"]) <= 18:
                    if abs(p["x"] - c["x"]) <= 2 and abs(p["z"] - c["z"]) <= 2:
                        p["vanished"] = True
                        c["mass"] += 1
                    elif "slow_walkers" in b and p.setdefault("walk", 0) < 2:
                        p["walk"] += 1
                    else:
                        p["walk"] = 0
                        p["x"] += (c["x"] > p["x"]) - (c["x"] < p["x"])
                        p["z"] += (c["z"] > p["z"]) - (c["z"] < p["z"])
            st = self.stage(c)
            if self.ticks - c["last_emit"] >= (5000, 3000, 1800)[st] and "no_passive" not in b:
                c["last_emit"] = self.ticks
                live = [q for q in self.pawns.values() if q["kind"] == "RM_TheUnfinished" and q["mental"]]
                if len(live) < (2, 4, 6)[st]:
                    q = self.pawn("RM_TheUnfinished", c["x"] + 2, c["z"], "none")
                    q["mental"] = "Manhunter"

    def stage(self, c):
        s = 0
        for i, m in enumerate(V.STAGE_MASS):
            if c["mass"] >= m:
                s = i
        return s

    def die(self, p):
        if "corpse_persists" in self.broken:
            p["dead"] = True
            self.new("Corpse_" + p["kind"], p["x"], p["z"])
        else:
            p["vanished"] = True

    def collapse(self, c):
        st = self.stage(c)
        n = min(V.SAMPLES_MAX, V.SAMPLES_BASE + V.SAMPLES_PER_STAGE * st + c["mass"] // V.MASS_PER_SAMPLE)
        if "wrong_samples" in self.broken:
            n += 1
        del self.things[c["id"]]
        for _ in range(n):
            self.new(V.SAMPLE, c["x"] + 1, c["z"] + 1, monstrous="samples_not_monstrous" not in self.broken)

    def complete_gestation(self, p, h):
        if "host_survives" not in self.broken:
            p["vanished"] = True
        p["hed"].remove(h)
        x, z = p["x"], p["z"]
        if h.get("monstrous") and (self.on("grownLimbsEnabled") or "limbs_ignore_toggle" in self.broken) \
                and "monstrous_organs" not in self.broken:
            self.new(V.LIMB_ITEMS[0], x, z)
            return
        n = 1 if "organ_count" in self.broken else 3
        for i in range(n):
            self.new(ORGANS[i], x, z + 1)

    # ------------------------------------------------------------ tools
    def t_step_game_ticks(self, ticks=0, **k):
        self.advance(int(ticks))
        return {"success": True}

    def t_set_time_speed(self, speed=None, **k):
        self.fast = speed == "Ultrafast"
        return {"success": True}

    def t_time_set_ticks(self, ticks=0, **k):
        self.ticks = int(ticks)
        return {"success": True, "ticksGameAfter": self.ticks}

    def t_weather_set(self, weather=None, **k):
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
        if want == ["BiomeDef/" + V.BIOME]:
            tab = [{"weather": "RM_ContagionBloom", "commonality": 70}, {"weather": "Rain", "commonality": 2}]
            if "burn_in_table" in self.broken:
                tab.append({"weather": V.BURN_WEATHER, "commonality": 1})
            ext = [] if "no_sky_ext" in self.broken else ["RimMandrake.Contagion.RM_ContagionSkyExtension"]
            return {"success": True, "foundCount": 1, "notFound": [], "defs": [{"defName": V.BIOME, "fields": {
                "baseWeatherCommonalities": tab, "animalDensity": 3.0, "modExtensions": ext,
                "wildAnimals": [{"animal": a, "commonality": 1} for a in V.WILD_ANIMALS],
                "wildPlants": [{"plant": a, "commonality": 1} for a in V.WILD_PLANTS]}}]}
        missing = [d for d in want if d.endswith("NoSuchDef_Probe")]
        if "missing_def" in self.broken and want and want[0] in V.SHIPPED:
            missing.append(want[3])
        return {"success": True, "notFound": missing, "foundCount": len(want) - len(missing)}

    def t_get_def(self, defName=None, **k):
        comps = [{"class": "CompProperties_Forbiddable"}]
        if "organ_unpatched" not in self.broken or defName != "Liver":
            comps.append({"class": "RimMandrake.Contagion.CompProperties_GenomeMatched"})
        return {"success": True, "comps": comps}

    def t_map_info(self, **k):
        return {"success": True, "tile": 77, "tileValid": True, "mapBiome": self.biome,
                "sizeX": 250, "sizeZ": 250}

    def t_world_tile_set(self, biome=None, **k):
        if "retile_noop" not in self.broken:
            self.biome = biome
        return {"success": True, "written": 1}

    def t_site_state(self, **k):
        return {"success": True, "conditions": {"map": [{"def": c["def"], "ticksLeft": c["until"] - self.ticks}
                                                        for c in self.conds], "world": []},
                "pawns": [{"id": p["id"], "job": "Wait_Wander"} for p in self.pawns.values()]}

    def t_game_condition(self, action="start", condition=None, durationTicks=0, **k):
        if action == "start":
            self.start_cond(condition, durationTicks or 60000)
            return {"success": True}
        c = self.cond(condition)
        if not c:
            return {"success": False, "message": "not active"}
        self.conds.remove(c)
        return {"success": True}

    def t_destroy_batch(self, rects="", categories="All", **k):
        rr = rect(rects)
        bldg = (V.REPULSOR, V.COALESCENCE, "Bed")
        if categories != "Pawn":
            for tid in [i for i, t in self.things.items() if inrect(t["x"], t["z"], rr)
                        and (categories == "All" or t["def"] not in bldg)]:
                del self.things[tid]
        if categories in ("Pawn", "All"):
            for pid in [i for i, p in self.pawns.items() if inrect(p["x"], p["z"], rr)]:
                del self.pawns[pid]
        self.roofs = [r for r in self.roofs if not (inrect(r[0], r[1], rr))]
        return {"success": True}

    def t_set_roof_batch(self, ops="", **k):
        for op in ops.split(";"):
            self.roofs.append(rect(op.split(":")[1]))
        return {"success": True}

    def t_spawn_batch(self, ops="", **k):
        for op in ops.split(";"):
            d, nums = op.split(":")
            n = [int(v) for v in nums.split(",")]
            if d == V.REPULSOR:
                self.new(d, n[0], n[1], power=False, warm=0)
            elif d == V.COALESCENCE:
                self.new(d, n[0], n[1], mass=0, last_growth=self.ticks, last_emit=self.ticks)
            elif d == V.SAMPLE:
                self.new(d, n[0], n[1], monstrous=False)
            else:
                self.new(d, n[0], n[1])
        return {"success": True}

    def t_list_things(self, defName=None, rect=None, limit=1, **k):
        rr = globals()["rect"](rect) if rect else None
        want = set((defName or "").split(","))
        rows = [t for t in self.things.values() if t["def"] in want and (not rr or inrect(t["x"], t["z"], rr))]
        return {"success": True, "scanned": 100, "countMatched": len(rows), "isCompleteList": True,
                "things": [dict(t) for t in rows[:limit]]}

    def t_spawn_pawn(self, kindDef=None, x=0, z=0, faction="none", **k):
        p = self.pawn(kindDef, x, z, faction)
        return {"success": True, "pawns": [{"id": p["id"]}]}

    def t_list_pawns(self, rect=None, includeHealth=False, limit=500, **k):
        rr = globals()["rect"](rect) if rect else None
        rows = []
        for p in self.pawns.values():
            if p["vanished"] or (rr and not inrect(p["x"], p["z"], rr)):
                continue
            row = {"id": p["id"], "kind": p["kind"], "kindDef": p["kind"], "x": p["x"], "z": p["z"],
                   "dead": p["dead"]}
            if includeHealth:
                row["health"] = {"hediffs": [dict(h) for h in p["hed"]]}
            rows.append(row)
        return {"success": True, "pawns": rows}

    def t_pawn_get(self, pawn=None, **k):
        # The real jawa/pawn_get carries NO mental-state field (live 2026-10-08); the mock used to invent
        # one, which is how a validation that could never pass live passed here.
        return {"success": True, "pawns": [{"thingId": pawn}]}

    def t_pawn_mental(self, pawn=None, action="list", **k):
        return {"success": True, "action": action, "currentState": self.pawns[pawn]["mental"] or None}

    def t_set_draft(self, **k):
        return {"success": True}

    def t_order_pawn(self, pawnId=None, x=None, z=None, waitTicks=0, **k):
        # The real tool runs the clock for waitTicks while the pawn walks (live 2026-10-08: a visitor walked
        # 200 ticks under the Burn and was dosed before the toggle it was meant to test went off).
        self.advance(int(waitTicks or 0))
        self.pawns[pawnId]["x"], self.pawns[pawnId]["z"] = x, z
        return {"success": True}

    def t_power_net(self, thing=None, forcePowerOn=None, **k):
        t = self.things[thing]
        if forcePowerOn is not None:
            t["power"] = bool(forcePowerOn)
        return {"success": True, "powerOnAfter": t.get("power", False)}

    def t_inspect_string(self, thingIds=None, **k):
        t = self.things.get(thingIds)
        if t is None:
            return {"success": True, "things": []}
        d, lines = t["def"], []
        if d == V.REPULSOR:
            if not (self.on("cloudRepulsorEnabled") or "rep_ignores_toggle" in self.broken):
                lines = ["Disabled in Mod Settings."]
            elif not t.get("power"):
                lines = ["Unpowered."]
            elif t["warm"] < 2500:
                lines = ["Warming up: 1 hour"]
            elif self.biome == V.BIOME:
                lines = ["Holding the storm open: the Burn is forced."]
            else:
                lines = ["Holding the sky clear."]
        elif d == V.COALESCENCE:
            lines = ["Stage %d, absorbed mass %d." % (self.stage(t) + 1, t["mass"])]
        elif d == V.SAMPLE:
            lines = ["Grade: Monstrous (grows a single limb, unmatched to anyone)"] if t.get("monstrous") \
                else (["Genome source: %s" % t["source"]] if t.get("source") else [])
        return {"success": True, "things": [{"id": t["id"], "label": d, "inspect": lines}]}

    def t_set_pawn_skill(self, **k):
        return {"success": True}

    def t_damage(self, damageDef=None, amount=5, thingId=None, **k):
        p = self.pawns[thingId]
        f = self.num("sunbeamNativeFactor")
        if (self.is_native(p) and f > 1 and "uv_no_multiplier" not in self.broken) or \
                "uv_person_multiplied" in self.broken:
            amount = amount * f
        self.addh(p, "RM_UVSunburn", amount)
        return {"success": True}

    def t_pawn_severity_adjust(self, pawn=None, hediff=None, offset=0, **k):
        p = self.pawns[pawn]
        h = self.addh(p, hediff, offset) if not any(x["def"] == hediff for x in p["hed"]) \
            else self.addh(p, hediff, offset)
        if hediff == "RM_UnfinishedUnraveling" and h["severity"] >= 1.0:
            self.die(p)
        if hediff == "RM_AmoebaGestation" and h["severity"] >= 0.999:
            self.complete_gestation(p, h)
        return {"success": True, "severityChanged": True}

    def t_bill_add(self, giverId=None, recipe=None, **k):
        self.bills.add(giverId)
        return {"success": True}

    def t_do_bill_now(self, billGiverId=None, pawnId=None, **k):
        if billGiverId in self.bills:
            self.bills.discard(billGiverId)
            p = self.pawns[billGiverId]
            if self.on("genomeOrganGrowingEnabled") and "extract_nothing" not in self.broken:
                self.new(V.SAMPLE, p["x"] + 1, p["z"], monstrous=False, source="Patient")
        return {"success": True, "accepted": True, "nowRunningRequested": True}

    def t_inventory_transfer(self, pawn=None, mode=None, thing=None, **k):
        t = self.things.pop(thing, None)
        if t is None:
            return {"success": True, "movedCount": 0}
        self.pawns[pawn]["inv"].append(t)
        return {"success": True, "movedCount": 1}

    def t_ordered_job(self, pawnId=None, jobDef=None, targetAId=None, **k):
        if jobDef == "RM_InjectGenomeSample":
            doer, host = self.pawns[pawnId], self.pawns.get(targetAId)
            if doer["inv"] and host and host["kind"] == V.HOST and "no_gestation" not in self.broken:
                s = doer["inv"].pop(0)
                h = self.addh(host, "RM_AmoebaGestation", 0.001)
                h["monstrous"] = bool(s.get("monstrous"))
        return {"success": True, "accepted": True, "nowRunningRequested": True}

    def t_drain_log(self, contains=None, errorsOnly=False, limit=1, **k):
        msgs = []
        if "log_error" in self.broken and contains == "Contagion":
            msgs = [{"text": "RM_Contagion: Could not resolve"}]
        return {"success": True, "totalInBuffer": 100, "messages": msgs}


# ------------------------------------------------------------------ the runner

def run(broken=()):
    sys.stderr, keep = _NULL, sys.stderr
    try:
        return _run(broken)
    finally:
        sys.stderr = keep


def _run(broken=()):
    game = Fake(broken)
    V._STATE.clear()
    results = {}
    for name, fn in V.suite.chains:
        t = TestContext(game, anchor=(150, 150))
        try:
            fn(t)
        except Exception as ex:            # a chain-level crash is a script bug
            results[name + ".<CRASH>"] = ("CRASH", "%s: %s" % (type(ex).__name__, ex))
            continue
        for c in t.components:
            results["%s.%s" % (name, c.name)] = (c.verdict, c.detail)
    return results


# break -> the component(s) that must go FAIL (and nothing else)
BREAKS = {
    "missing_def": ["defs.defs_resolve"],
    "burn_in_table": ["defs.biome_table_and_roster"],
    "no_sky_ext": ["defs.biome_table_and_roster"],
    "organ_unpatched": ["defs.organ_patch_comps"],
    "setting_missing": ["settings.defaults", "settings_coalescenceEnabled.coalescenceEnabled_roundtrip",
                        "coalescence.coalescence_off_absorbs_nothing"],
    "default_wrong": ["settings.defaults"],
    "rep_ignores_toggle": ["repulsor_clear.off_when_setting_off", "burn_forced.repulsor_off_lapses_burn"],
    "rep_no_clear": ["repulsor_clear.holds_sky_clear"],
    "rep_forces_burn_offbiome": ["repulsor_clear.holds_sky_clear"],
    "rep_sticky": ["repulsor_clear.lapses_without_power"],
    "spawner_ignores_toggle": ["spawner.spawner_off_buds_nothing"],
    "no_bud": ["spawner.spawner_buds_unfinished"],
    "spawner_no_cap": ["spawner.spawner_buds_unfinished"],
    "no_limbs": ["spawner.unfinished_rolls_limbs_and_lifespan"],
    "no_lifespan": ["spawner.unfinished_rolls_limbs_and_lifespan"],
    "corpse_persists": ["spawner.unfinished_dissolves_on_death"],
    "retile_noop": ["site.retile_to_contagion"],
    "no_force_burn": ["burn_forced.repulsor_forces_burn"],
    "weather_not_burn": ["burn_forced.repulsor_forces_burn"],
    "zero_dmg_hurts": ["burn_forced.burn_harmless_at_zero_damage"],
    "no_dose": ["burn_forced.burn_doses_the_exposed_visitor"],
    "dose_roofed": ["burn_forced.burn_doses_the_exposed_visitor"],
    "native_unhurt": ["burn_forced.burn_hurts_native_spares_armored"],
    "armored_hurt": ["burn_forced.burn_hurts_native_spares_armored"],
    "no_dive": ["burn_forced.native_dives_for_roof"],
    "harm_ignores_burn_toggle": ["burn_forced.burn_off_means_no_harm"],
    "sched_ignores_toggle": ["burn_natural.burn_off_never_schedules"],
    "freq_ignored": ["burn_natural.slow_frequency_defers_burn"],
    "no_schedule": ["burn_natural.natural_burn_arrives_on_schedule"],
    "uv_no_multiplier": ["uv.uv_native_multiplier"],
    "uv_person_multiplied": ["uv.uv_native_multiplier"],
    "coal_ignores_toggle": ["coalescence.coalescence_off_absorbs_nothing"],
    "no_absorb": ["coalescence.coalescence_absorbs_and_grows_a_stage"],
    "slow_walkers": [],                       # stragglers miss a pass: the harness polls, nothing goes red
    "no_passive": ["coalescence.coalescence_emits_manhunters_and_grows_on_its_own"],
    "no_collapse": ["coalescence.burn_collapses_it_into_monstrous_samples"],
    "wrong_samples": ["coalescence.burn_collapses_it_into_monstrous_samples"],
    "samples_not_monstrous": ["coalescence.burn_collapses_it_into_monstrous_samples"],
    "extract_nothing": ["genome.extraction_surgery_yields_sample"],
    "no_gestation": ["genome.inject_starts_gestation", "coalescence.monstrous_gestation_grows_one_limb"],
    "host_survives": ["genome.gestation_dies_producing_one_organ_batch"],
    "organ_count": ["genome.gestation_dies_producing_one_organ_batch", "coalescence.grown_limbs_off_grows_organs"],
    "monstrous_organs": ["coalescence.monstrous_gestation_grows_one_limb"],
    "limbs_ignore_toggle": ["coalescence.grown_limbs_off_grows_organs"],
    "log_error": ["log.log_clean"],
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
    ok_breaks = 0
    for brk, target in sorted(BREAKS.items()):
        res = run([brk])
        reds = sorted(k for k, v in res.items() if v[0] in ("FAIL", "CRASH"))
        if reds != sorted(target):
            bad.append("break %-26s expected only %s FAIL, got %s" % (brk, target, reds))
        else:
            ok_breaks += 1
    print("selftest Contagion: %d components, healthy PASS %d/%d; %d/%d breaks each turn exactly "
          "their component red" % (n_comp, n_comp - len(notpass), n_comp, ok_breaks, len(BREAKS)))
    for b in bad:
        print("  BAD:", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
