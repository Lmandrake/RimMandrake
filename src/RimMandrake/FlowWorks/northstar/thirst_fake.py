"""ThirstFakeBridge -- the offline stand-in thirst_live.py --mock runs against (no game, no bridge).

A small world model, NOT the mod: it answers each bridge tool the driver calls, and plays the mod's thirst behaviour well
enough that every row's control flow runs, including the 2026-10-18 harness branches (ingest_done waits for the job to end,
T24's refused-pawn replacement, T23's in-flight fill drained before the Store baseline). With no faults the model behaves
as the shipped mod is specified; a fault flips ONE behaviour so a selftest can prove the intended row goes red (or
UNMEASURED), i.e. that the row can fail. It is not evidence about the game: a mock PASS proves the driver's logic, never
the mod. Result files written under --mock say mode "mock" so validation.py's live reader refuses them.

faults (name -> intended effect):
  ingest_slow         Ingest takes ~1,400 ticks (the old fixed 600-tick wait would have read it as 'drank for nothing')
  ingest_never_ends   Ingest never finishes -> T4/T5 UNMEASURED (budget exhausted), never PASS/FAIL
  salt_ratio          salt bottle hydrates like a fresh one -> T5 FAIL
  no_dehydration      T6 reads no RM_Dehydration -> UNMEASURED
  slow_dehydration    dehydration accrues at half rate -> T6 FAIL
  fast_decay          need falls twice as fast -> T3 FAIL
  no_terrain_drink    colonists never drink from terrain -> T10 FAIL
  terrain_when_off    the drinkFromTerrain setting is ignored -> T10 FAIL
  salt_routine        a thirsty colonist drinks salt water -> T12 FAIL
  fill_salt           the fill giver takes the nearest water, salt included -> T11 FAIL
  no_fire_job         nobody douses -> T24 FAIL
  douse_single        a douse puts out one fire -> T24 FAIL
  refuse_first_2      the first two colonists refuse Firefighter/Hauling/Cooking work -> T24/T23/T25 must REPLACE them
  refuse_all          every colonist refuses -> the driver raises after six replacements
  store_still_fills   a Store tank still orders brine fills -> T23 FAIL
  inflight_pour       stop_job leaves a pour finishing 1,000 ticks later (T23 baseline must wait it out)
  no_melt             snow buckets never melt -> T25 FAIL
  no_biomes           mandrake.rm.biomes absent from the running list -> T15/T16/T27 UNMEASURED SITE
  stale_mark          the no-water mark survives a reload -> T15R FAIL
  stock_overfill      the bottle stock fills 12 past the target -> T29 FAIL
  no_xenotype         spawn_pawn ignores the xenotype -> T28 UNMEASURED
  no_ordered_job      ordered_job answers accepted=False -> T4/T5/T20 UNMEASURED
  dubs_need           every colonist carries a DBHThirst need -> T2 FAIL
  no_fuel             fires do not take -> T24 UNMEASURED SITE
  site_blocked        a rock stays in the site rect -> site_ready UNMEASURED SITE, run aborts
"""
import re

SETTINGS0 = {"thirstEnabled": True, "thirstRateMultiplier": 1.0, "thirstHeatScaling": True, "animalsGetThirst": True,
             "drinkFromTerrain": True, "waterQualityEffects": True, "lastResortDrinking": True, "saltBreakEnabled": True,
             "roughDrinkPenalty": True, "snowGathering": True, "filledBottlesPerColonist": 3}
FRESH = ("WaterShallow", "WaterDeep", "WaterMovingShallow", "WaterMovingChestDeep", "RM_WaterFrigidShallow", "RM_WaterFrigidDeep",
         "RM_Water_Rust", "RM_Water_Verdigris", "RM_Water_Amber", "RM_Water_Violet", "RM_Water_Chalk", "Marsh")
SALT = ("WaterOceanShallow", "WaterOceanDeep")
BRINE = ("RM_WaterBrineShallow", "RM_WaterBrineDeep")
TOXIC = ("RM_WaterPoisonedShallow",)
SLIME = {"RM_SlimeRedShallow": "RM_ContagionTouched", "RM_SlimeGreenShallow": "RM_Slimification",
         "RM_SlimeWhiteShallow": "RM_SporeFlesh", "RM_SlimeYellowShallow": "RM_SlimeNausea", "RM_Slime_Liquid": "RM_Slimification"}
SLIME_SEV = {"RM_ContagionTouched": 1.0, "RM_Slimification": 0.3, "RM_SporeFlesh": 0.01, "RM_SlimeNausea": 0.2}
BIOMES_ONLY_HEDIFFS = ("RM_ContagionTouched", "RM_Slimification", "RM_SporeFlesh")
WET = FRESH + SALT + BRINE + TOXIC + tuple(SLIME) + ("RM_Fill_Water_Trace", "RM_Fill_Water_Half", "RM_Fill_Water_Brim",
                                                    "RM_Fill_Water_Superdeep")
NATIVE = ("Dromedary",)
ANIMALS = ("Muffalo", "Dromedary", "Gazelle", "Iguana", "Hare", "Rat", "Elephant", "Rhinoceros", "Ostrich", "Emu", "Squirrel",
           "Deer", "Boar", "Alpaca", "Megasloth", "Tortoise", "Cobra", "Raccoon", "Fox_Fennec")
WALK = 13           # ticks per cell
DT = 10


def _cells(rect):
    x, z, w, h = rect
    return [(i, j) for i in range(x, x + w) for j in range(z, z + h)]


def _rect(s):
    return tuple(int(v) for v in str(s).split(","))


def _in(rect, x, z):
    return rect[0] <= x < rect[0] + rect[2] and rect[1] <= z < rect[1] + rect[3]


class Pawn(object):
    def __init__(self, pid, num, kind, faction, x, z):
        self.id, self.num, self.kind, self.faction, self.x, self.z = pid, num, kind, faction, x, z
        self.need, self.hed, self.mem = 0.9, {}, []
        self.drafted, self.job, self.job_t, self.ctx = False, None, 0, {}
        self.refuse, self.prio = set(), {}
        self.xeno, self.break_t, self.think_now = None, 0, True

    @property
    def human(self):
        return self.kind == "Colonist"


class ThirstFakeBridge(object):
    def __init__(self, faults=(), biomes=True):
        self.faults = set(faults)
        self.biomes = biomes and "no_biomes" not in self.faults
        self.calls = []
        self.log = []
        self.settings = dict(SETTINGS0)
        self.marks = {}
        self.reloads = 0
        self._reset()

    # ----------------------------------------------------------- world
    def _reset(self):
        self.tick, self.nid, self.tid = 2, 0, 0
        self.terrain, self.things, self.pawns = {}, {}, {}
        self.snow, self.grass, self.tanks, self.bills = {}, set(), {}, {}
        self.refused_n = 0
        for c in _cells((60, 60, 6, 2)):         # a river the driver's first act must dry
            self.terrain[c] = "WaterShallow"
        for i in range(3):
            self._new_pawn("Colonist", "colony", 20 + i, 16)
        if "site_blocked" in self.faults:
            self._thing("Rock_Granite", 155, 135)

    def reload(self):
        """test_site_saves.load_site: the save restarts the clock and the thing-ID counter."""
        self.reloads += 1
        if "stale_mark" not in self.faults:
            self.marks = {}
        self._reset()
        return {"verified": True, "site": "calm"}

    def _new_pawn(self, kind, faction, x, z):
        self.nid += 1
        p = Pawn("Human%d" % self.nid if kind == "Colonist" else "%s%d" % (kind, self.nid), self.nid, kind, faction, x, z)
        p.drafted = False
        if kind == "Colonist":
            if "refuse_all" in self.faults or ("refuse_first_2" in self.faults and self.refused_n < 2):
                p.refuse = {"Firefighter", "Hauling", "Cooking"}
                self.refused_n += 1
            if "dubs_need" in self.faults:
                p.dubs = True
        self.pawns[p.id] = p
        return p

    def _thing(self, defn, x, z, n=1, stuff=None, **kw):
        self.tid += 1
        t = {"id": "T%d" % self.tid, "def": defn, "x": x, "z": z, "stackCount": n, "stuff": stuff,
             "label": ("wooden " if stuff == "WoodLog" else "") + defn}
        if defn == "RM_Bucket_FreshWater":
            t["liters"] = 15.0
        t.update(kw)
        self.things[t["id"]] = t
        return t

    def of(self, defn, rect=None):
        return [t for t in self.things.values() if t["def"] == defn and (rect is None or _in(rect, t["x"], t["z"]))]

    def terr(self, defs):
        return [c for c, d in self.terrain.items() if d in defs]

    def _nearest(self, p, cells):
        return min(cells, key=lambda c: abs(c[0] - p.x) + abs(c[1] - p.z)) if cells else None

    # ----------------------------------------------------------- bridge surface
    def call(self, tool, **kw):
        self.calls.append(tool)
        fn = getattr(self, "t_" + re.sub(r"[^a-z0-9]", "_", tool.lower()), None)
        if fn is None:
            return {"success": True}
        r = fn(**kw)
        return r if r is not None else {"success": True}

    def probe(self, cmd, wait_s=20.0):
        return {"success": True, "pawns": []}

    def ticks(self, n):
        self.advance(int(n))
        return {"success": True, "advanced": int(n)}

    def tank_units(self, x, z):
        t = self._tank_at(x, z)
        return None if t is None else t["units"]

    def _tank_at(self, x, z):
        for t in self.of("RM_LiquidTank"):
            if (t["x"], t["z"]) == (x, z):
                return self.tanks.setdefault(t["id"], {"mode": "Store", "liquid": "RM_Liquid_FreshWater", "units": 0})
        return None

    # --- generic reads
    def t_rimworld_get_game_info(self, **kw):
        return {"success": True, "ticksGame": self.tick}

    def t_rimworld_list_colonists(self, **kw):
        return {"success": True, "colonists": [{"pawnId": "Thing_" + p.id, "thingIdNumber": p.num, "job": p.job, "dead": False}
                                               for p in self.pawns.values() if p.human]}

    def t_jawa_running_mods(self, **kw):
        ids = ["ludeon.rimworld", "mandrake.rm.flowworks"] + (["mandrake.rm.biomes"] if self.biomes else [])
        return {"success": True, "packageIds": ids}

    def t_jawa_type_probe(self, **kw):
        return {"success": True, "mvidMatchesFile": True, "assemblyFileSha256": "00" * 32}

    def t_jawa_mod_inventory(self, **kw):
        return {"success": True, "mods": [{"id": i} for i in range(11)]}

    def t_jawa_mod_settings_field(self, typeName="", action="get", field="", value=None, **kw):
        if action == "set":
            old = self.settings.get(field)
            if isinstance(old, bool):
                self.settings[field] = str(value).lower() == "true"
            elif isinstance(old, int):
                self.settings[field] = int(float(value))
            elif isinstance(old, float):
                self.settings[field] = float(value)
            else:
                self.settings[field] = value
            return {"success": True}
        return {"success": True, "value": self.settings.get(field)}

    def t_jawa_get_roof_batch(self, **kw):
        return {"success": True, "roofs": []}

    # --- terrain / things
    def t_jawa_get_terrain_batch(self, rects="", **kw):
        r = _rect(rects)
        ops = ["%s:%d,%d,1,1" % (d, c[0], c[1]) for c, d in sorted(self.terrain.items()) if _in(r, *c) and d != "Soil"]
        return {"success": True, "ops": ";".join(ops)}

    def t_jawa_set_terrain_batch(self, ops="", **kw):
        for op in ops.split(";"):
            if ":" not in op:
                continue
            d, rc = op.split(":")
            for c in _cells(_rect(rc)):
                if d == "Soil":
                    self.terrain.pop(c, None)
                else:
                    self.terrain[c] = d

    def t_jawa_spawn_pawn(self, kindDef="Colonist", x=0, z=0, count=1, faction="PlayerColony", xenotype=None, **kw):
        p = self._new_pawn(kindDef, "colony" if faction == "PlayerColony" else "wild", int(x), int(z))
        if kindDef != "Colonist":
            p.drafted = False
        out = {"id": p.id, "thingId": p.id}
        if xenotype and "no_xenotype" not in self.faults:
            p.xeno = xenotype
            out.update(xenotype=xenotype, xenotypeApplied=True)
        elif xenotype:
            out.update(xenotype="Baseliner", xenotypeApplied=False)
        return {"success": True, "pawns": [out]}

    def t_rimworld_spawn_thing(self, defName="", x=0, z=0, stackCount=1, **kw):
        t = self._thing(defName, int(x), int(z), int(stackCount))
        return {"success": True, "thingId": "Thing_" + t["id"]}

    def t_jawa_spawn_batch(self, ops="", stuff=None, **kw):
        for op in ops.split(";"):
            d, rc = op.split(":")
            x, z, n = (int(v) for v in rc.split(","))
            self._thing(d, x, z, n, stuff=stuff)

    def t_jawa_list_things(self, defName="", rect=None, limit=100, **kw):
        names = set(defName.split(",")) if defName else None
        r = _rect(rect) if rect else None
        out = [dict(t) for t in self.things.values()
               if (names is None or t["def"] in names) and (r is None or _in(r, t["x"], t["z"]))]
        return {"success": True, "things": out[:int(limit)], "countMatched": len(out), "isCompleteList": True}

    def t_jawa_destroy_batch(self, rects="", categories="All", **kw):
        cats = set(categories.split(","))
        n = 0
        for rc in rects.split(";"):
            r = _rect(rc)
            for t in list(self.things.values()):
                if not _in(r, t["x"], t["z"]) or t["def"] == "Fire" or (t["def"].startswith("Rock") and "site_blocked" in self.faults):
                    continue
                cat = ("Building" if t["def"] in ("RM_LiquidTank", "Campfire") else
                       "Plant" if t["def"].startswith("Plant_") else "Item")
                if "All" in cats or cat in cats or (t["def"].startswith("Rock") and "Building" in cats):
                    del self.things[t["id"]]
                    n += 1
        return {"success": True, "destroyed": n}

    def t_jawa_build_batch(self, ops="", **kw):
        for op in ops.split(";"):
            d, rc = op.split(":")
            x, z = (int(v) for v in rc.split(",")[:2])
            self._thing(d, x, z)

    def t_jawa_set_plants(self, ops="", **kw):
        d, rc = ops.split(":")
        self.grass.update(_cells(_rect(rc)))

    def t_jawa_map_fire(self, action="", rect="", fireSize=0.5, **kw):
        r = _rect(rect)
        if action == "start":
            if "no_fuel" in self.faults:
                return
            for c in _cells(r):
                if c in self.grass:
                    self._thing("Fire", c[0], c[1])
        else:
            for t in self.of("Fire", r):
                del self.things[t["id"]]

    def t_jawa_thing_refuel(self, **kw):
        return {"success": True}

    def t_jawa_bill_add(self, giverId="", recipe="", **kw):
        self.bills[giverId] = recipe
        return {"success": True}

    def t_jawa_set_weather_buildup(self, kind="snow", mode="set", rect="", depth=0.0, **kw):
        if mode == "set":
            for c in _cells(_rect(rect)):
                if depth > 0:
                    self.snow[c] = depth
                else:
                    self.snow.pop(c, None)
        return {"success": True, "cellsChanged": 1, "sample": list(self.snow.values())[:3]}

    def t_jawa_cell_temperature(self, **kw):
        return {"success": True, "temperature": 26.0}

    def t_jawa_comp_read(self, thing="", **kw):
        t = self.things.get(thing) or {}
        return {"success": True, "values": {"warmTicks": t.get("warm", 0)}}

    def t_jawa_inspect_string(self, thingIds="", **kw):
        out = []
        for i in str(thingIds).split(","):
            t = self.things.get(i)
            if t:
                part = t.get("liters", 15.0) < 15.0 and t["def"] == "RM_Bucket_FreshWater"
                out.append({"id": i, "inspect": [t["def"]] + (["Partly drunk"] if part else [])})
        return {"success": True, "things": out}

    # --- pawns
    def _p(self, pid):
        return self.pawns.get(re.sub(r"^Thing_", "", str(pid)))

    def t_jawa_pawn_need(self, pawn="", action="list", need="", level=None, **kw):
        p = self._p(pawn)
        if p is None:
            return {"success": False, "error": "no pawn"}
        if action == "need":
            if need == "RM_Thirst":
                p.need = float(level)
            return {"success": True}
        names = ["Food", "Rest", "Joy", "Mood", "RM_Thirst"] + (["DBHThirst"] if getattr(p, "dubs", False) else [])
        return {"success": True, "needs": [{"need": n, "level": p.need if n == "RM_Thirst" else 1.0} for n in names],
                "memories": [{"def": m} for m in p.mem]}

    def t_jawa_pawn_get(self, pawn="", **kw):
        p = self._p(pawn)
        h = dict(p.hed) if p else {}
        if "no_dehydration" in self.faults:
            h.pop("RM_Dehydration", None)
        return {"success": True, "pawns": [{"hediffs": [{"def": k, "severity": v} for k, v in h.items()]}]}

    def t_jawa_pawn_health(self, **kw):
        return {"success": True}

    def t_jawa_set_draft(self, pawnId="", drafted=True, **kw):
        p = self._p(pawnId)
        if p:
            p.drafted = bool(drafted)
            p.job, p.job_t = (None, 0) if drafted else (p.job, p.job_t)
            p.think_now = True

    def t_jawa_stop_job(self, pawnId="", **kw):
        p = self._p(pawnId)
        if p is None:
            return
        if "inflight_pour" in self.faults and p.job == "RM_FillBottleJob" and p.ctx.get("brine"):
            # stop_job does not end a fill already past the point of no return: it lands ~1,000 ticks later (past the 600-tick settle: only the wait loop covers it) as a brine bucket
            # on the ground (T23's Store baseline must wait this out, then clear it)
            self.late_stops = getattr(self, "late_stops", 0) + 1
            p.job_t, p.ctx = 1000, {"late": True}
            return
        p.job, p.job_t, p.think_now = None, 0, True

    def t_jawa_set_work_priority(self, pawnId="", workType="", priority=1, **kw):
        p = self._p(pawnId)
        if p is None or workType in p.refuse:
            return {"success": False, "error": "work type disabled for this pawn"}
        p.prio[workType] = int(priority)
        return {"success": True}

    def t_jawa_pawn_mental(self, pawn="", action="list", **kw):
        p = self._p(pawn)
        if action == "end" and p:
            p.break_t = 0
        return {"success": True, "state": "RM_Break_DrinkBrine" if p and p.break_t > 0 else "none"}

    def t_jawa_pawn_force_mental_break(self, pawn="", breakDef="", **kw):
        p = self._p(pawn)
        if p is None:
            return {"success": False}
        p.break_t, p.job, p.job_t = 1000, "RM_Break_DrinkBrine", 0
        return {"success": True, "started": True, "breakDef": breakDef}

    def t_jawa_ordered_job(self, pawnId="", jobDef="", targetAId=None, targetBId=None, waitTicks=0, **kw):
        p = self._p(pawnId)
        if p is None or "no_ordered_job" in self.faults:
            return {"success": True, "accepted": False, "message": "refused"}
        before = p.job
        tgt = self.things.get(targetAId)
        if tgt is None:
            return {"success": True, "accepted": False, "message": "target gone"}
        d = abs(tgt["x"] - p.x) + abs(tgt["z"] - p.z)
        dur = {"Ingest": 500 + (900 if "ingest_slow" in self.faults else 0), "RM_DrinkFromContainer": 120,
               "RM_EmptyIntoTankJob": 150}.get(jobDef, 200)
        if jobDef == "Ingest" and "ingest_never_ends" in self.faults:
            dur = 10 ** 9
        p.job, p.job_t, p.ctx, p.think_now = jobDef, WALK * d + dur, {"a": targetAId, "b": targetBId, "ordered": True}, False
        self.advance(int(waitTicks))
        return {"success": True, "accepted": True, "beforeJobDef": before, "afterJobDef": jobDef}

    def t_jawa_static_call(self, type="", method="", args="", **kw):
        if method == "ProofTank":
            xz, mode, liquid, units = args.split(";")
            x, z = (int(v) for v in xz.split(","))
            t = self._tank_at(x, z)
            if t is None:
                return {"success": False, "result": "no tank at %s" % xz}
            t.update(mode=mode, liquid=liquid, units=int(units))
            return {"success": True, "result": "tank %s %s %s" % (mode, liquid, units)}
        if method == "NativeHere":
            p = self._p(args)
            return {"success": True, "result": str(bool(p and p.kind in NATIVE))}
        if method == "Have":
            return {"success": True, "result": str(sum(t["stackCount"] for t in self.of("RM_Bottle_FreshWater")))}
        if method == "Warning":
            self.log.append(args)
        return {"success": True, "result": ""}

    # ----------------------------------------------------------- the simulation
    def advance(self, n):
        left = n
        while left > 0:
            dt = min(DT, left)
            self.tick += dt
            left -= dt
            self._world(dt)
            for p in list(self.pawns.values()):
                self._pawn(p, dt)

    def _world(self, dt):
        if "no_melt" in self.faults:
            return
        for t in self.of("RM_BucketSnow"):
            t["warm"] = t.get("warm", 0) + dt
            if t["warm"] >= 5000:
                del self.things[t["id"]]
                self._thing("RM_Bucket_FreshWater", t["x"], t["z"], stuff=t.get("stuff"))

    def _pawn(self, p, dt):
        s = self.settings
        if s["thirstEnabled"] and (p.human or s["animalsGetThirst"]):
            rate = 0.2 / 15000.0 * float(s["thirstRateMultiplier"]) * (2 if "fast_decay" in self.faults else 1)
            p.need = max(0.0, p.need - rate * dt)
        if p.need <= 0.0 and p.human:
            k = 0.5 if "slow_dehydration" in self.faults else 1.0
            p.hed["RM_Dehydration"] = min(1.0, p.hed.get("RM_Dehydration", 0.0) + k * 0.30 / 60000.0 * dt)
        if p.break_t > 0:
            p.break_t -= dt
            if p.break_t <= 0:
                p.need = 1.0
                p.hed["RM_SaltPoisoning"] = p.hed.get("RM_SaltPoisoning", 0.0) + 0.5
                p.mem.append("RM_Thought_SaltRelief")
                p.job = None
                p.think_now = True
            return
        if p.drafted and not p.ctx.get("ordered"):
            return
        if p.job:
            p.job_t -= dt
            if p.job_t <= 0:
                job, p.job, p.job_t = p.job, None, 0
                self._done(p, job)
                p.think_now = True
            return
        if p.think_now:
            p.think_now = False
            self._think(p)

    def _wander(self, p, ticks=1200):
        p.job, p.job_t, p.ctx = "GotoWander", ticks, {}

    def _start(self, p, job, dur, ctx=None, at=None):
        d = abs(at[0] - p.x) + abs(at[1] - p.z) if at else 0
        p.job, p.job_t, p.ctx = job, WALK * d + dur, ctx or {}

    def _think(self, p):
        s = self.settings
        if p.human and p.drafted:
            return
        if not p.human:
            return self._think_animal(p)
        thirsty = s["thirstEnabled"] and p.need < 0.3
        desperate = s["thirstEnabled"] and p.need <= 0.0
        if thirsty and self._think_drink(p, desperate):
            return
        if not thirsty and self._think_work(p):
            return
        if thirsty:
            self.marks[p.num] = self.tick + 600       # the terrain search failed: marked
            return self._wander(p)                    # a failed drink search leaves the long GotoWander (poll_job's stop_job)
        self._wander(p, 150)                          # idle and not thirsty: a short wander, then work is looked for again

    def _think_drink(self, p, desperate):
        s = self.settings
        fresh = [t for t in self.of("RM_Bottle_FreshWater") + self.of("RM_Bottle_IcyWater")]
        if fresh:
            t = min(fresh, key=lambda t: abs(t["x"] - p.x) + abs(t["z"] - p.z))
            dur = 500 + (900 if "ingest_slow" in self.faults else 0)
            self._start(p, "Ingest", dur, {"a": t["id"]}, (t["x"], t["z"]))
            return True
        can = self.of("RM_BlueIceMeltwaterCan")
        if can:
            t = can[0]
            self._start(p, "RM_DrinkWaterItem", 150, {"a": t["id"]}, (t["x"], t["z"]))
            return True
        bk = self.of("RM_Bucket_FreshWater")
        if bk:
            t = bk[0]
            self._start(p, "RM_DrinkFromContainer", 120, {"a": t["id"]}, (t["x"], t["z"]))
            return True
        if self.marks.get(p.num, -1) > self.tick:
            return False
        if "no_terrain_drink" not in self.faults and (s["drinkFromTerrain"] or "terrain_when_off" in self.faults):
            c = self._nearest(p, self.terr(FRESH))
            if c:
                self._start(p, "RM_DrinkFromTerrain", 200, {"cell": c, "kind": "fresh"}, c)
                return True
            if "salt_routine" in self.faults:
                c = self._nearest(p, self.terr(SALT))
                if c:
                    self._start(p, "RM_DrinkFromTerrain", 200, {"cell": c, "kind": "salt"}, c)
                    return True
            if desperate and s["lastResortDrinking"]:
                for kind, defs in (("toxic", TOXIC), ("slime", tuple(SLIME))):     # toxic (3) outranks slime (4)
                    c = self._nearest(p, self.terr(defs))
                    if c:
                        self._start(p, "RM_DrinkFromTerrain", 200, {"cell": c, "kind": kind}, c)
                        return True
        return False

    def _think_animal(self, p):
        if not (self.settings["animalsGetThirst"] and p.need < 0.3):
            return self._wander(p, 300)
        c = self._nearest(p, self.terr(FRESH))
        kind = "fresh"
        if c is None and p.kind in NATIVE:
            c, kind = self._nearest(p, self.terr(SALT)), "salt"
        if c is None:
            return self._wander(p, 300)
        self._start(p, "Drink", 200, {"cell": c, "kind": kind}, c)

    def _water_for_fill(self, p):
        if "fill_salt" in self.faults:
            return self._nearest(p, self.terr(FRESH + SALT))
        return self._nearest(p, self.terr(FRESH))

    def _think_work(self, p):
        pr = p.prio
        haul = pr.get("Hauling", 3) > 0 and "Hauling" not in p.refuse
        fires = self.of("Fire")
        if fires and "no_fire_job" not in self.faults and pr.get("Firefighter", 3) > 0 and "Firefighter" not in p.refuse:
            bk = self.of("RM_Bucket_FreshWater")
            if bk:
                t = bk[0]
                self._start(p, "RM_DouseFireWithBucket", 200, {"a": t["id"], "fire": fires[len(fires) // 2]["id"]}, (t["x"], t["z"]))
                return True
        if haul:
            # a Fill-mode tank holding brine orders brine buckets; a Store tank must not (store_still_fills breaks that)
            for tid, tk in self.tanks.items():
                if tk["liquid"] == "RM_Liquid_Brine" and (tk["mode"] == "Fill" or "store_still_fills" in self.faults):
                    emp = self.of("RM_BucketEmpty")
                    brine = self._nearest(p, self.terr(BRINE))
                    if emp and brine:
                        self._start(p, "RM_FillBottleJob", 300, {"empty": emp[0]["id"], "tank": tid, "brine": True}, brine)
                        return True
            water = self._water_for_fill(p)
            stock = sum(t["stackCount"] for t in self.of("RM_Bottle_FreshWater"))
            target = int(self.settings["filledBottlesPerColonist"]) * len([q for q in self.pawns.values() if q.human])
            emp_b = self.of("RM_BottleEmpty")
            if water and emp_b and stock < target + (12 if "stock_overfill" in self.faults else 0):
                k = min(10, target - stock + (12 if "stock_overfill" in self.faults else 0), sum(t["stackCount"] for t in emp_b))
                self._start(p, "RM_FillBottleJob", 300, {"bottles": max(1, k), "salt": water in self.terr(SALT)}, water)
                return True
            emp_k = self.of("RM_BucketEmpty")
            if water and emp_k:
                self._start(p, "RM_FillBottleJob", 300, {"bucket": emp_k[0]["id"], "salt": water in self.terr(SALT)}, water)
                return True
            if self.settings["snowGathering"] and self.snow and emp_k and not self.terr(FRESH):
                c = self._nearest(p, list(self.snow))
                self._start(p, "RM_GatherSnow", 200, {"bucket": emp_k[0]["id"], "cell": c}, c)
                return True
        if pr.get("Cooking", 3) > 0 and "Cooking" not in p.refuse:
            for fid, recipe in self.bills.items():
                ice = self.of("RM_BlueIce")
                emp = self.of("RM_BucketEmpty")
                if ice and emp and fid in self.things:
                    self._start(p, "DoBill", 300, {"ice": ice[0]["id"], "bucket": emp[0]["id"]}, (self.things[fid]["x"], self.things[fid]["z"]))
                    return True
        return False

    def _hurt(self, p, name, sev):
        if name in BIOMES_ONLY_HEDIFFS and not self.biomes:
            return
        p.hed[name] = p.hed.get(name, 0.0) + sev

    def _done(self, p, job):
        c = p.ctx
        p.ctx = {}
        ordered = c.get("ordered")
        if job == "Ingest":
            t = self.things.pop(c.get("a"), None)
            if t is None:
                return
            if t["def"] == "HemogenPack":
                p.need = min(1.0, p.need + (0.5 if p.xeno == "Sanguophage" else 0.0))
            elif t["def"] == "RM_Bottle_SaltWater":
                p.need = min(1.0, p.need + (0.6 if "salt_ratio" in self.faults else 0.42))
                self._hurt(p, "RM_SaltPoisoning", 0.25)
                p.mem.append("RM_Thought_SaltRelief")
                self._thing("RM_BottleDirty", t["x"], t["z"])
            else:
                p.need = min(1.0, p.need + 0.6)
                self._thing("RM_BottleDirty", t["x"], t["z"])
        elif job == "RM_DrinkFromContainer":
            t = self.things.get(c.get("a"))
            if t is None:
                return
            t["liters"] = t.get("liters", 15.0) - 1.5
            p.need = min(1.0, p.need + 0.15)
            if self.settings["roughDrinkPenalty"]:
                p.mem.append("RM_Thought_DrankRough")
            if t["liters"] <= 0.01:
                del self.things[t["id"]]
                self._thing("RM_BucketDirty", t["x"], t["z"])
        elif job == "RM_DrinkWaterItem":
            t = self.things.pop(c.get("a"), None)
            if t:
                p.need = min(1.0, p.need + 0.67)
                p.mem.append("RM_Thought_DrankDistilled")
        elif job == "RM_DrinkFromTerrain":
            kind = c.get("kind")
            p.need = min(1.0, p.need + 0.5)
            ter = self.terrain.get(c.get("cell"))
            if kind == "toxic":
                self._hurt(p, "ToxicBuildup", 0.1)
            elif kind == "slime":
                self._hurt(p, SLIME.get(ter, "RM_Slimification"), SLIME_SEV.get(SLIME.get(ter), 0.3))
                self._hurt(p, "RM_SlimePurge", 0.5)
                p.mem.append("RM_Thought_DrankSlime")
        elif job == "Drink":
            p.need = min(1.0, p.need + 0.5)
        elif job == "RM_EmptyIntoTankJob":
            t = self.things.get(c.get("a"))
            tk = self.tanks.get(c.get("b"))
            if c.get("late"):
                pass
            elif t and tk:
                tk["units"] += int(round(t.get("liters", 15.0) * 10))
                del self.things[t["id"]]
                self._thing("RM_BucketEmpty", t["x"], t["z"])
        elif job == "RM_FillBottleJob":
            if c.get("late"):
                self.late_drops = getattr(self, "late_drops", 0) + 1
                self._thing("RM_Bucket_Brine", p.x, p.z)
            elif c.get("brine"):
                e = self.things.pop(c["empty"], None)
                if e:
                    self._thing("RM_Bucket_Brine", p.x, p.z)
                    self._thing("RM_BucketEmpty", p.x + 3, p.z)   # the next empty stays for a second trip
                    tk = self.tanks.get(c["tank"])
                    if tk and tk["mode"] == "Fill":
                        tk["units"] += 100
            elif c.get("bottles"):
                left = c["bottles"]
                for t in self.of("RM_BottleEmpty"):          # stacks: a trip takes up to `bottles` empties in all
                    if left <= 0:
                        break
                    q = min(left, t["stackCount"])
                    left -= q
                    t["stackCount"] -= q
                    if t["stackCount"] <= 0:
                        del self.things[t["id"]]
                    self._thing("RM_Bottle_SaltWater" if c.get("salt") else "RM_Bottle_FreshWater", t["x"], t["z"], q)
            elif c.get("bucket"):
                t = self.things.pop(c["bucket"], None)
                if t:
                    self._thing("RM_Bucket_FreshWater", t["x"], t["z"])
        elif job == "RM_GatherSnow":
            t = self.things.pop(c.get("bucket"), None)
            if t:
                x, z = c["cell"]
                self._thing("RM_BucketSnow", x, z, stuff=t.get("stuff"))
        elif job == "RM_DouseFireWithBucket":
            bk = self.things.pop(c.get("a"), None)
            f = self.things.get(c.get("fire"))
            if f:
                if "douse_single" in self.faults:
                    del self.things[f["id"]]
                else:
                    for g in self.of("Fire"):
                        if abs(g["x"] - f["x"]) <= 1 and abs(g["z"] - f["z"]) <= 1:
                            del self.things[g["id"]]
            if bk:
                self._thing("RM_BucketEmpty", bk["x"], bk["z"])
        elif job == "DoBill":
            ice = self.things.get(c.get("ice"))
            b = self.things.pop(c.get("bucket"), None)
            if ice and b:
                ice["stackCount"] -= 1
                if ice["stackCount"] <= 0:
                    del self.things[ice["id"]]
                self._thing("RM_Bucket_FreshWater", b["x"], b["z"], stuff=b.get("stuff") or "WoodLog")
        if ordered:
            p.think_now = False
