"""rimdrive.fake -- a scripted bridge for offline tests of the modcheck situational layer.

`FakeWorld.call(tool, **params)` answers from a WORLD MODEL, not canned replies, and its result
keys are the ones MEASURED live on 2026-10-01 (see
`modcheck/testdata/contract_probe_2026-10-01.json` and design/RimMandrake/northstar_helpers_plan.md
section 11). A key a fake invents that the real bridge lacks makes a selftest lie, so every shape
below is copied from a recorded result.

Adversarial modes reproduce the lies the real bridge told us:
  - `damage_kill_lies`  : `jawa/damage` says success and the target is still alive (measured: a
                          Cut 500 on a raider reported success and left it standing).
  - `list_truncate_at`  : `jawa/list_pawns` honours a limit and reports `truncated` (E3).
  - `kill_noop`         : `pawn_force_incapacitate kill` says success and changes nothing.
  - `settings_lie`      : `debug_settings set` says valueAfter but the value did not change.
  - `part_mismatch`     : `pawn_health remove` with a bodyPart says 'no hediff on <part>' (measured).
  - `kill_explodes`     : killing a Boomalope ignites 25 fires (MEASURED 2026-10-01).
  - `step_zero`         : `rimworld/step_game_ticks` completes 0 ticks (stall).
  - `step_truncate_to`  : a step completes fewer ticks than asked (E9).

Scheduled events (`at(tick, fn)`) fire as `step_game_ticks` advances, so a test can put a raid or a
death INSIDE a wait. Pure python, no sockets; runs under python3 and python.exe.
"""
import copy
import os
import struct
import zlib


def pawn_row(pid, kind="Colonist", faction="PlayerColony", is_player=True, hostile=False,
             intelligence="Humanlike", dead=False, x=100, z=100, hediffs=None):
    """A list_pawns row with exactly the keys the live bridge returned."""
    return {
        "bodySize": 1.0, "dead": dead, "def": "Human" if intelligence == "Humanlike" else kind,
        "downed": False, "faction": faction, "factionName": faction, "fleshType": "Normal",
        "hasGenes": True, "health": {"hediffs": list(hediffs or []), "capacities": {"Consciousness": 1.0},
                                      "bleedRate": 0.0, "painTotal": 0.0},
        "hostile": hostile, "id": pid, "intelligence": intelligence, "isFlesh": True,
        "isMechanoid": False, "isPlayer": is_player, "kind": kind, "kindDef": kind,
        "name": pid, "spawned": not dead, "stunTicksLeft": 0, "stunned": False,
        "uniqueXenotype": False, "x": x, "xenotype": "Baseliner", "xenotypeLabel": "baseliner", "z": z,
    }


def hediff(defname, part=None, severity=1.0):
    return {"def": defname, "label": defname.lower(), "severity": severity, "part": part,
            "partLabel": part}


class FakeWorld(object):
    """The world model plus the tool surface. One instance == one connected session."""

    def __init__(self, pawns=None, ticks=0, size=250):
        self.ticks = ticks
        self.paused = True
        self.size = size
        self.pawns = {p["id"]: copy.deepcopy(p) for p in (pawns or [])}
        self.fires = []            # list of {"id","x","z"}
        self.letters = []          # {"defName","label","arrivalTick"}
        self.stats = {"numRaidsEnemy": 0, "numThreatBigs": 0, "colonistsKilled": 0}
        self.debug = {"enableStoryteller": True, "enableRandomMentalStates": True,
                      "enableRandomDiseases": True, "noAnimals": False}
        self.difficulty = {"threatScale": 1.0, "allowBigThreats": True}
        self.mental = {}           # pawn id -> state
        self.needs = {}            # pawn id -> {need: level}
        self.queue = []            # queued incidents: {"defName","fireTick",...} (peek row shape)
        self.jobs = {}             # pawn id -> {"def": JobDef, "targetA": thing id or None}
        self.lords = {}            # pawn id -> {"loadId","lordJob","toil"}
        self.damage_log = []       # recorder ring (jawa/damage_log event rows)
        self.lineage = []          # item journal (jawa/thing_lineage event rows)
        self.things = {}           # live item id -> {"def","stackCount","holder": [..], "x","z"}
        self.recorder_installed = True
        self._dseq = 0             # damage ring seq (real: JawaEventRing.Total)
        self._lseq = 0             # lineage journal seq
        self.calls = []            # (tool, params) log
        self.events = []           # (tick, fn) scheduled
        self.modes = set()
        self.list_truncate_at = None
        self.step_truncate_to = None
        self._fid = 1000
        self.shot_dir = None       # set by a test to make take_screenshot write real PNG files
        self.litter = []           # rimdrive.Session surface used by TestContext
        self.shots = 0

    # ----------------------------------------------------------- scripting
    def at(self, tick, fn):
        self.events.append((tick, fn))
        self.events.sort(key=lambda e: e[0])

    def add_fire(self, x, z):
        self._fid += 1
        self.fires.append({"id": "Fire%d" % self._fid, "x": x, "z": z})

    def kill(self, pid):
        p = self.pawns[pid]
        if p["dead"]:
            return
        p["dead"] = True
        p["spawned"] = False
        self.record_damage(pid, kind="kill", damage_def=None, amount=0.0)
        if p["isPlayer"] and p["intelligence"] == "Humanlike":
            self.stats["colonistsKilled"] += 1
            self.letters.append({"defName": "Death", "label": "Death: %s" % pid,
                                 "arrivalTick": self.ticks})

    def record_damage(self, victim, kind="damage", damage_def="Cut", amount=10.0, instigator=None):
        p = self.pawns.get(victim, {})
        self._dseq += 1
        self.damage_log.append({
            "seq": self._dseq - 1, "tick": self.ticks, "kind": kind, "victimId": victim,
            "victimDef": p.get("def"), "victimIsPawn": victim in self.pawns, "victimFaction": p.get("faction"),
            "victimColonist": bool(p.get("isPlayer")) and p.get("intelligence") == "Humanlike",
            "victimDeadAfter": bool(p.get("dead")), "damageDef": damage_def, "amount": amount,
            "totalDealt": amount if kind == "damage" else 0.0, "deflected": False,
            "instigatorId": instigator, "instigatorDef": None, "instigatorFaction": None, "weapon": None,
            "hitPart": None, "culpritHediff": None, "hediffsAdded": [], "mapUniqueId": 0,
            "x": p.get("x", -1), "z": p.get("z", -1)})

    def record_lineage(self, kind, thing_id, other_id=None, count=1, stack_after=0, destroy_mode=None):
        t = self.things.get(thing_id, {})
        self._lseq += 1
        self.lineage.append({"seq": self._lseq - 1, "tick": self.ticks, "kind": kind, "thingId": thing_id,
                             "def": t.get("def"), "otherId": other_id, "otherDef": None, "count": count,
                             "stackAfter": stack_after, "holder": None, "destroyMode": destroy_mode,
                             "mapUniqueId": 0, "x": t.get("x", -1), "z": t.get("z", -1)})

    def eat(self, thing_id, pawn_id):
        """A pawn eats a whole tracked item: the journal shows ingest then destroy (as in game)."""
        t = self.things.pop(thing_id)
        self.record_lineage("ingest", thing_id, pawn_id, count=t["stackCount"], stack_after=0)
        self.record_lineage("destroy", thing_id, None, count=0, destroy_mode="Vanish")

    def merge(self, thing_id, into_id):
        t = self.things.pop(thing_id)
        self.things[into_id]["stackCount"] += t["stackCount"]
        self.record_lineage("absorb", thing_id, into_id, count=t["stackCount"], stack_after=0)
        self.record_lineage("destroy", thing_id, None, count=0, destroy_mode="Vanish")

    # ----------------------------------------------------------- tool surface
    def call(self, tool, **p):
        self.calls.append((tool, dict(p)))
        fn = getattr(self, "_t_" + tool.replace("/", "_"), None)
        if fn is None:
            return {"success": False, "message": "FakeWorld has no tool %s" % tool}
        return fn(**p)

    def _t_jawa_time_clock(self):
        return {"success": True, "ticksGame": self.ticks, "ticksAbs": self.ticks,
                "curTimeSpeed": "Normal", "paused": self.paused}

    def _t_rimworld_pause_game(self, pause=True):
        self.paused = bool(pause)
        return {"success": True, "paused": self.paused}

    def _t_rimworld_step_game_ticks(self, ticks=1, pauseFirst=True):
        n = int(ticks)
        if "step_zero" in self.modes:
            n = 0
        elif self.step_truncate_to is not None:
            n = min(n, self.step_truncate_to)
        start = self.ticks
        for _ in range(n):
            self.ticks += 1
            while self.events and self.events[0][0] <= self.ticks:
                self.events.pop(0)[1](self)
        return {"success": True, "status": "completed", "requestedTicks": int(ticks),
                "completedTicks": n, "remainingTicks": int(ticks) - n, "startTicksGame": start,
                "endTicksGame": self.ticks}

    def _t_jawa_map_info(self):
        return {"success": True, "mapId": 0, "sizeX": self.size, "sizeZ": self.size, "tile": 4375, "tileValid": True,
                "cellCount": self.size * self.size, "mapBiome": getattr(self, "map_biome", "FakeBland")}

    def _t_jawa_world_tile_set(self, tiles=None, biome=None, temperature=None, readBack=0, **_):
        ov = self.__dict__.setdefault("tile_overrides", {}).setdefault(int(tiles), {})
        if biome is not None:
            ov["biome"] = biome
            self.map_biome = biome
        if temperature is not None:
            ov["temperature"] = temperature
        return {"success": True}

    def _t_jawa_world_commit(self, **_):
        return {"success": True}

    def _t_jawa_list_pawns(self, includeHealth=False, includeCorpses=False, limit=500, faction=None, rect=None):
        rows = [copy.deepcopy(p) for p in self.pawns.values() if includeCorpses or not p["dead"]]
        if not includeHealth:
            for r in rows:
                r.pop("health", None)
        cap = self.list_truncate_at if self.list_truncate_at is not None else int(limit)
        total = len(rows)
        cut = max(0, total - cap)
        rows = rows[:cap]
        return {"success": True, "message": "%d pawn(s)%s." % (len(rows), (", %d beyond the limit" % cut) if cut else ""),
                "pawns": rows, "returned": len(rows), "truncated": cut, "totalOnMap": total,
                "ticksGame": self.ticks}

    def _t_jawa_letter_list(self):
        return {"success": True, "count": len(self.letters), "ticksGame": self.ticks,
                "letters": [{"label": {"RawText": l["label"]}, "defName": l["defName"],
                             "arrivalTick": l["arrivalTick"]} for l in self.letters]}

    def _t_jawa_story_stats(self):
        d = dict(self.stats)
        d.update({"success": True, "ticksGame": self.ticks})
        return d

    def _t_jawa_list_things(self, defName=None, group=None, **_):
        if group == "Corpse":
            rows = list(getattr(self, "corpses", []))
            return {"success": True, "things": rows, "countReturned": len(rows), "countMatched": len(rows),
                    "isCompleteList": True, "truncated": 0, "ticksGame": self.ticks}
        if defName == "Fire":
            return {"success": True, "things": [dict(f, **{"def": "Fire"}) for f in self.fires],
                    "scanned": 43183, "countReturned": len(self.fires), "countMatched": len(self.fires),
                    "isCompleteList": True, "truncated": 0, "ticksGame": self.ticks}
        return {"success": True, "things": [], "scanned": 0, "countReturned": 0, "countMatched": 0,
                "isCompleteList": True, "truncated": 0, "ticksGame": self.ticks}

    def _t_jawa_destroy_batch(self, rects="", categories="Plant", **_):
        """Things only (never pawns, like the live tool): removes fake corpses standing in the given 1x1 cells."""
        cells = set()
        for r in str(rects).split(";"):
            v = [int(q) for q in r.split(":")[-1].split(",") if q != ""]
            if len(v) >= 2:
                cells.add((v[0], v[1]))
        before = len(getattr(self, "corpses", []))
        if "Item" in categories or "All" in categories:
            self.corpses = [c for c in getattr(self, "corpses", []) if (c["x"], c["z"]) not in cells]
        return {"success": True, "message": "Destroyed %d thing(s) across %d cell(s)." % (
            before - len(getattr(self, "corpses", [])), len(cells))}

    def _t_jawa_map_fire(self, action="start", rect=None, fireSize=0.5):
        if action == "extinguish":
            n = len(self.fires)
            self.fires = []
            return {"success": True, "action": "extinguish", "firesExtinguished": n, "firesStarted": 0,
                    "cellsFailed": 0, "errors": []}
        x, z, w, h = [int(v) for v in rect.split(",")]
        for i in range(3):
            self.add_fire(x + i % w, z)
        return {"success": True, "action": "start", "firesStarted": 3, "errors": []}

    def _t_jawa_pawn_force_incapacitate(self, pawn=None, action="downed", **_):
        p = self.pawns.get(pawn)
        if p is None:
            return {"success": False, "message": "no such pawn"}
        before = p["dead"]
        if action == "vanish":                           # Destroy(Vanish): gone, no death, no death action
            if "kill_noop" not in self.modes:
                del self.pawns[pawn]
            return {"success": pawn not in self.pawns, "action": action, "deadBefore": before,
                    "destroyedAfter": pawn not in self.pawns}
        if action == "kill" and "kill_noop" not in self.modes:
            if "kill_divides" in self.modes and p["kind"] == "Toughspike":
                for i in range(2):                       # MEASURED 2026-10-05: DeathActionWorker_Divide -> fingerspikes
                    cid = "%s_child%d" % (pawn, i)
                    self.pawns[cid] = pawn_row(cid, kind="Fingerspike", faction="Entities", is_player=False,
                                               hostile=True, intelligence="Animal", x=p["x"] + i, z=p["z"])
            if "kill_explodes" in self.modes and p["kind"] == "Boomalope":
                for i in range(25):                      # MEASURED: 25 fires within 5 ticks of one death
                    self.add_fire(p["x"] + i % 5, p["z"] + i // 5)
            self.kill(pawn)
        return {"success": True, "action": action, "deadBefore": before, "deadAfter": p["dead"],
                "changed": p["dead"] != before}

    def _t_jawa_destroy_bulk(self, filter=None, dryRun=True, **_):
        ids = [pid for pid, p in self.pawns.items()
               if (filter == "factionlessAnimals" and p["faction"] is None and p["intelligence"] == "Animal" and not p["dead"])
               or (filter == "nonColonists" and not (p["isPlayer"] and p["intelligence"] == "Humanlike"))]
        if not dryRun:
            for pid in ids:
                del self.pawns[pid]
        return {"success": True, "dryRun": dryRun, "filter": filter, "matchedCount": len(ids),
                "destroyed": [{"thingId": i} for i in ids]}

    def _t_jawa_damage(self, thingId=None, damageDef="Cut", amount=10, **_):
        # the measured lie: success with a big amount, target may still be alive
        p = self.pawns.get(thingId)
        if p is not None:
            self.record_damage(thingId, damage_def=damageDef, amount=float(amount))
        if p is not None and "damage_kill_lies" not in self.modes and amount >= 500:
            self.kill(thingId)
        return {"success": True, "message": "Damaged 1 thing(s) with %s %s." % (damageDef, amount),
                "targetsHit": 1}

    def _t_jawa_pawn_resurrect(self, pawn=None, **_):
        p = self.pawns.get(pawn)
        if p is None or not p["dead"]:
            return {"success": False, "resurrected": False, "message": "not dead"}
        p["dead"] = False
        p["spawned"] = True
        p["health"]["hediffs"] = []
        return {"success": True, "resurrected": True, "deadBefore": True, "deadAfter": False, "spawned": True}

    def _t_jawa_pawn_health(self, pawn=None, action="add", hediff=None, bodyPart=None, **_):
        p = self.pawns.get(pawn)
        if p is None:
            return {"success": False, "message": "no such pawn"}
        hs = p["health"]["hediffs"]
        if action == "remove":
            if "part_mismatch" in self.modes and bodyPart:
                return {"success": False, "message": "Pawn has no hediff '%s' on %s." % (hediff, bodyPart)}
            keep = [h for h in hs if not (h["def"] == hediff and (bodyPart in (None, "") or h["part"] == bodyPart))]
            ok = len(keep) != len(hs)
            p["health"]["hediffs"] = keep
            return {"success": ok}
        return {"success": False, "message": "fake supports remove only"}

    def _t_jawa_pawn_mental(self, pawn=None, action="list", **_):
        st = self.mental.get(pawn)
        if action == "end":
            if st is None:
                return {"success": False, "message": "Pawn is not in a mental state."}
            self.mental.pop(pawn)
            return {"success": True, "action": "end", "currentState": None}
        return {"success": True, "action": "list", "currentState": st}

    def _t_jawa_pawn_need(self, pawn=None, action="list", need=None, level=0.5, **_):
        n = self.needs.setdefault(pawn, {"Food": 0.8, "Rest": 0.9, "Joy": 0.5, "Mood": 0.5})
        if action == "need":
            n[need] = float(level)
            return {"success": True}
        return {"success": True, "action": "list",
                "needs": [{"need": k, "level": v, "pct": v} for k, v in n.items()]}

    def _t_jawa_debug_settings(self, action="list", field=None, value=None):
        if action == "set":
            if field not in self.debug:
                return {"success": False, "message": "unknown field"}
            before = self.debug[field]
            if "settings_lie" not in self.modes:
                self.debug[field] = bool(value)
            return {"success": True, "field": field, "valueBefore": before, "valueAfter": self.debug[field]}
        return {"success": True, "action": "list", "count": len(self.debug),
                "fields": [{"name": k, "value": v} for k, v in self.debug.items()]}

    def _t_jawa_difficulty_tune(self, threatScale=None, allowBigThreats=None, **_):
        before = dict(self.difficulty)
        if threatScale is not None:
            self.difficulty["threatScale"] = float(threatScale)
        if allowBigThreats is not None:
            self.difficulty["allowBigThreats"] = bool(allowBigThreats)
        return {"success": True, "before": before, "after": dict(self.difficulty)}

    def _t_jawa_incident_queue_clear(self):
        n = len(self.queue)
        cleared = list(self.queue)
        self.queue = []
        return {"success": True, "clearedCount": n, "cleared": cleared}

    # ------------------------------------------------ situational companion reads (NORTHSTAR_COMPANION_GAPS_1)
    # Keys copied from JawaBenchSituationalTools.cs's ResultDescription; selftest checks every key
    # the fake emits appears in the real tool's ResultDescription. NOT live-measured yet.

    def _select(self, faction, ids, includeDead):
        if ids:
            want = [i.strip() for i in ids.split(",") if i.strip()]
            missing = [i for i in want if i not in self.pawns]
            if missing:
                return None, "No pawn matching: %s. Nothing was read; fix the id list." % ", ".join(missing)
            return [self.pawns[i] for i in want], None
        if faction not in (None, "", "player", "hostile", "nonplayer", "none"):
            return None, "Unknown faction filter '%s'." % faction
        rows = [p for p in self.pawns.values() if includeDead or not p["dead"]]
        f = faction or ""
        if f == "player":
            rows = [p for p in rows if p["isPlayer"]]
        elif f == "hostile":
            rows = [p for p in rows if p["hostile"]]
        elif f == "nonplayer":
            rows = [p for p in rows if not p["isPlayer"]]
        elif f == "none":
            rows = [p for p in rows if p["faction"] is None]
        return rows, None

    def _t_jawa_pawn_census(self, faction=None, ids=None, includeDead=False, limit=500):
        if not 1 <= int(limit) <= 2000:
            return {"success": False, "message": "limit must be 1-2000"}
        sel, err = self._select(faction, ids, includeDead)
        if err:
            return {"success": False, "message": err}
        rows = []
        for p in sel[:int(limit)]:
            st = self.mental.get(p["id"])
            job = self.jobs.get(p["id"])
            hunting = bool(job and job["def"] == "PredatorHunt")
            humanlike = p["intelligence"] == "Humanlike"
            n = self.needs.get(p["id"], {"Food": 0.8, "Rest": 0.9, "Joy": 0.5, "Mood": 0.5})
            rows.append({
                "id": p["id"], "name": p["name"], "kindDef": p["kindDef"], "faction": p["faction"],
                "isPlayer": p["isPlayer"], "hostile": p["hostile"],
                "isColonist": p["isPlayer"] and humanlike, "spawned": p["spawned"], "dead": p["dead"],
                "downed": p["downed"], "x": p["x"], "z": p["z"], "inMentalState": st is not None,
                "mentalState": None if st is None else {
                    "def": st, "isAggro": st in ("Berserk", "Manhunter", "ManhunterPermanent"),
                    "ageTicks": 0, "causedByMood": False, "causedByDamage": False, "causedByPawn": None,
                    "forceRecoverAfterTicks": -1},
                "breakImminent": {"minor": False, "major": False, "extreme": False} if humanlike else None,
                "job": None if job is None else {"def": job["def"],
                                                 "targetA": None if not job.get("targetA") else {
                                                     "thingId": job["targetA"], "def": None, "x": -1, "z": -1},
                                                 "targetB": None},
                "isPredatorHunting": hunting, "preyId": job.get("targetA") if hunting else None,
                "enemyTargetId": None, "meleeThreatId": None, "lastAttackTargetTick": -99999,
                "anyCloseHostilesRecently": False,
                "needs": {"food": n.get("Food"), "rest": n.get("Rest"),
                          "mood": n.get("Mood") if humanlike else None, "joy": n.get("Joy") if humanlike else None},
                "lord": self.lords.get(p["id"]), "duty": None})
        return {"success": True, "count": len(rows), "totalSelected": len(sel),
                "truncated": max(0, len(sel) - int(limit)), "readErrors": [], "pawns": rows,
                "ticksGame": self.ticks}

    def _t_jawa_pawn_roles(self, faction=None, ids=None, includeDead=False, limit=500):
        if not 1 <= int(limit) <= 2000:
            return {"success": False, "message": "limit must be 1-2000"}
        sel, err = self._select(faction, ids, includeDead)
        if err:
            return {"success": False, "message": err}
        rows = []
        for p in sel[:int(limit)]:
            humanlike = p["intelligence"] == "Humanlike"
            col = p["isPlayer"] and humanlike
            rows.append({
                "id": p["id"], "name": p["name"], "kindDef": p["kindDef"], "faction": p["faction"],
                "isPlayer": p["isPlayer"], "isColonist": col, "isFreeColonist": col, "isSlave": False,
                "isSlaveOfColony": False, "isPrisoner": False, "isPrisonerOfColony": False,
                "guestStatus": "Guest" if humanlike else None, "hostFaction": None, "isQuestLodger": False,
                "isQuestHelper": False, "isWildMan": False, "isCreepJoiner": False, "isMutant": False,
                "isGhoul": False, "isAnimal": p["intelligence"] == "Animal", "isColonyMech": False,
                "isColonistPlayerControlled": col and not p["dead"], "isCaravanMember": False,
                "isWorldPawn": False, "dead": p["dead"], "spawned": p["spawned"], "ideoRole": None,
                "royalTitle": None, "royalTitleFaction": None, "lord": self.lords.get(p["id"]), "duty": None,
                "mapUniqueId": 0, "mapIndex": 0})
        return {"success": True, "count": len(rows), "totalSelected": len(sel),
                "truncated": max(0, len(sel) - int(limit)), "readErrors": [], "pawns": rows,
                "ticksGame": self.ticks}

    def _t_jawa_incident_queue_peek(self):
        rows = [self._qrow(q, i) for i, q in enumerate(self.queue)]
        return {"success": True, "count": len(rows), "queue": rows, "ticksGame": self.ticks}

    def _t_jawa_incident_queue_remove(self, defName=None, fireTick=-1, dryRun=True):
        if not defName and int(fireTick) < 0:
            return {"success": False, "message": "Give defName and/or fireTick."}
        hits = [q for q in self.queue if (not defName or q["defName"].lower() == defName.lower())
                and (int(fireTick) < 0 or q["fireTick"] == int(fireTick))]
        if not hits:
            return {"success": False, "message": "Nothing in the incident queue matches. Nothing was removed.",
                    "details": {"queue": list(self.queue)}}
        before = len(self.queue)
        matched = [self._qrow(q, self.queue.index(q)) for q in hits]
        if not dryRun:
            self.queue = [q for q in self.queue if q not in hits]
        return {"success": True, "dryRun": dryRun, "matchedCount": len(hits), "matched": matched,
                "removedCount": before - len(self.queue), "countBefore": before,
                "countAfter": len(self.queue),
                "remaining": [self._qrow(q, i) for i, q in enumerate(self.queue)], "ticksGame": self.ticks}

    def _qrow(self, q, i):
        return dict(q, index=i, ticksUntilFire=q["fireTick"] - self.ticks)

    def _t_jawa_damage_log(self, action="read", sinceSeq=-1, sinceTick=-1, thingId=None, pawnsOnly=True,
                           kind=None, limit=500):
        if action not in ("read", "status", "clear"):
            return {"success": False, "message": "Unknown action"}
        if not self.recorder_installed:
            return {"success": False, "message": "The damage recorder is not installed. Refusing."}
        if action == "clear":
            n = len(self.damage_log)
            self.damage_log = []
            return {"success": True, "action": action, "clearedTotal": n, "totalAfter": 0, "ticksGame": self.ticks}
        hits = [] if action == "status" else [
            e for e in self.damage_log if e["seq"] > int(sinceSeq) and (int(sinceTick) < 0 or e["tick"] >= int(sinceTick))
            and (not pawnsOnly or e["victimIsPawn"]) and (kind is None or e["kind"] == kind)
            and (thingId is None or thingId in (e["victimId"], e["instigatorId"]))]
        ret = hits[-int(limit):]
        oldest = self.damage_log[0]["seq"] if self.damage_log else self._dseq
        return {"success": True, "action": action, "installed": {"damage": True, "kill": True},
                "installErrors": [], "recorderInstalledUtc": "2026-10-01T00:00:00Z", "capacity": 4096,
                "totalRecorded": len(self.damage_log), "overwritten": 0, "oldestRetainedSeq": oldest,
                "oldestRetainedTick": self.damage_log[0]["tick"] if self.damage_log else -1,
                "completeSinceSeq": int(sinceSeq) + 1 >= oldest, "recordErrors": 0, "lastRecordError": None,
                "matchedCount": len(hits), "returned": len(ret), "truncated": len(hits) - len(ret),
                "nextSeq": self._dseq, "events": ret, "ticksGame": self.ticks}

    def _t_jawa_thing_lineage(self, ids=None, includeEvents=True):
        if not ids or not ids.strip():
            return {"success": False, "message": "Give ids: comma-separated thing ids."}
        out = []
        for tid in [i.strip() for i in ids.split(",") if i.strip()]:
            evs = [e for e in self.lineage if tid in (e["thingId"], e["otherId"])]
            t = self.things.get(tid)
            if t is None:
                own = [e for e in evs if e["thingId"] == tid]
                kinds = [e["kind"] for e in own]
                if not own:
                    fate = "UNRECORDED"
                elif "absorb" in kinds:
                    fate = "absorbedInto:" + [e for e in own if e["kind"] == "absorb"][-1]["otherId"]
                elif "ingest" in kinds:
                    fate = "eatenBy:" + [e for e in own if e["kind"] == "ingest"][-1]["otherId"]
                elif "destroy" in kinds:
                    fate = "destroyed:" + [e for e in own if e["kind"] == "destroy"][-1]["destroyMode"]
                else:
                    fate = "gone-after:" + kinds[-1]
                out.append({"id": tid, "found": False, "fate": fate, "events": evs if includeEvents else None})
                continue
            out.append({"id": tid, "found": True, "def": t["def"], "label": t["def"], "stackCount": t["stackCount"],
                        "spawned": not t.get("holder"), "destroyed": False, "mapUniqueId": 0,
                        "x": t.get("x", -1), "z": t.get("z", -1), "holderChain": list(t.get("holder") or ["map:0"]),
                        "carriedBy": None, "forbidden": False, "rotStage": "Fresh", "rotProgress": 0.0, "fate": None,
                        "events": evs if includeEvents else None})
        return {"success": True, "lineageInstalled": self.recorder_installed, "installErrors": [],
                "recorderInstalledUtc": "2026-10-01T00:00:00Z", "journalTotal": len(self.lineage),
                "journalOverwritten": 0, "results": out, "ticksGame": self.ticks}

    # ------------------------------------------------ hazard levers + world tools (northstar live queue)
    # Keys from each tool's ResultDescription in JawaBench.BridgeTools (NOT live-measured shapes); used by
    # modcheck/live_queue dry runs and selftest_companion_detectors.py.

    def _t_jawa_pawn_force_mental_break(self, pawn=None, breakDef=None, intensity="minor", reason="", **_):
        p = self.pawns.get(pawn)
        if p is None:
            return {"success": False, "message": "No pawn matching %s." % pawn}
        before = self.mental.get(pawn)
        self.mental[pawn] = breakDef or "Wander_Sad"
        return {"success": True, "started": True, "breakDef": self.mental[pawn], "before": before,
                "after": self.mental[pawn]}

    def _t_jawa_ordered_job(self, pawnId=None, jobDef=None, targetAId=None, **_):
        if pawnId not in self.pawns:
            return {"success": False, "message": "No pawn matching %s." % pawnId}
        before = (self.jobs.get(pawnId) or {}).get("def")
        self.jobs[pawnId] = {"def": jobDef, "targetA": targetAId}
        return {"success": True, "accepted": True, "beforeJobDef": before, "afterJobDef": jobDef,
                "nowRunningRequested": True}

    def _t_jawa_incident_schedule(self, incidentDef=None, delayTicks=2500, **_):
        before = len(self.queue)
        row = {"defName": incidentDef, "fireTick": self.ticks + int(delayTicks)}
        self.queue.append(row)
        return {"success": True, "queued": dict(row), "countBefore": before, "countAfter": len(self.queue),
                "ticksUntilFire": int(delayTicks)}

    def _t_jawa_world_tile_get(self, tiles=None, **_):
        rows = []
        for t in str(tiles).split(","):
            t = int(t)
            rows.append(dict({"tile": t, "biome": "AridShrubland", "hilliness": "Flat", "swampiness": 0.0,
                              "temperature": 22.0, "elevation": 120.0, "mutatorCount": 0, "roadCount": 0,
                              "riverCount": 0}, **getattr(self, "tile_overrides", {}).get(t, {})))
        return {"success": True, "count": len(rows), "tiles": rows}

    def _t_jawa_world_tile_export(self, path=None, **_):
        rows = getattr(self, "tile_rows", None) or [
            {"tile": 4375, "biome": "AridShrubland", "hilliness": "Flat", "swampiness": 0.0, "temperature": 22.0,
             "elevation": 120.0}]
        if path:
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
        return {"success": True, "path": path, "rows": len(rows)}

    def _t_jawa_colony_found(self, tile=-1, faction="Player", name=None, dryRun=False, **_):
        self.settled = getattr(self, "settled", set())
        if tile in self.settled:
            return {"success": False, "message": "Tile %s already carries a Settlement." % tile}
        if not dryRun:
            self.settled.add(tile)
        if not dryRun:
            self.dialogs = getattr(self, "dialogs", []) + ["Dialog_NamePlayerFactionAndSettlement"]
        return {"success": True, "tile": tile, "layerId": 0, "faction": faction, "settlementId": 900 + tile % 97,
                "name": name or "Bland", "limitReached": False}

    def _t_jawa_world_tile_map_generate(self, tile=-1, suggestedMapParent="Settlement", dryRun=False, **_):
        self.maps = getattr(self, "maps", [0])
        if not dryRun:
            self.maps.append(tile)
        wild = getattr(self, "arrival_wildlife", 0)
        for i in range(wild):               # MEASURED 2026-10-01: tile 4375 arrived with 47 wildlife pawns
            pid = "Megasloth%d" % (5000 + i)
            self.pawns[pid] = pawn_row(pid, kind="Megasloth", faction=None, is_player=False,
                                       intelligence="Animal", x=50 + i, z=50)
        return {"success": True, "tile": tile, "mapParentDef": suggestedMapParent, "wasAlreadyGenerated": False,
                "mapSize": {"x": self.size, "z": self.size}, "mapIndex": len(self.maps) - 1,
                "pawnCount": wild, "thingCount": 16753, "mapFinalize": {"failedSteps": [], "steps": []}}

    def _t_jawa_set_current_map(self, mapId=None, **_):
        self.maps = getattr(self, "maps", [0])
        if int(mapId) >= len(self.maps):
            return {"success": False, "message": "no map %s" % mapId,
                    "loadedMaps": [{"mapId": i, "tile": t} for i, t in enumerate(self.maps)]}
        prev = getattr(self, "current_map", 0)
        self.current_map = int(mapId)
        return {"success": True, "mapId": int(mapId), "tile": self.maps[int(mapId)], "biome": "AridShrubland",
                "mapCount": len(self.maps), "previousMapId": prev, "ticksGame": self.ticks}

    # ------------------------------------------------ extra reads the snapshot takes (full tier)
    def _t_jawa_alerts_list(self):
        return {"success": True, "count": 0, "alerts": [], "ticksGame": self.ticks}

    def _t_jawa_weather_get(self, **_):
        conds = list(getattr(self, "conditions", []))
        return {"success": True, "readErrors": [], "weather": {"current": "Clear"}, "conditions": conds,
                "activeConditionCount": len(conds), "storyteller": {"def": "Cassandra", "difficulty": "Rough",
                                                            "threatScale": self.difficulty["threatScale"],
                                                            "allowBigThreats": self.difficulty["allowBigThreats"]}}

    def _t_jawa_drain_log(self, limit=50, errorsOnly=False, **_):
        return {"success": True, "messages": [], "totalInBuffer": 0, "ticksGame": self.ticks}

    def _t_jawa_window_list_close(self, action="list", typeName=None, closeAll=False, **_):
        dlgs = getattr(self, "dialogs", [])
        rows = [{"typeName": d} for d in dlgs]
        closed = 0
        if action == "close":
            keep = [d for d in dlgs if not (typeName and typeName.lower() in d.lower())]
            closed = len(dlgs) - len(keep)
            self.dialogs = keep
        return {"success": True, "action": action, "count": len(rows), "windows": rows, "closedCount": closed,
                "ticksGame": self.ticks}

    def _t_jawa_name_colony(self, factionName=None, settlementName=None, **_):
        self.named = True
        self.dialogs = [d for d in getattr(self, "dialogs", []) if "NamePlayer" not in d]
        return {"success": True, "factionName": factionName or "Northstar Test Colony",
                "settlements": [{"tile": t, "name": settlementName or "Northstar Base", "namedByPlayer": True}
                                for t in sorted(getattr(self, "settled", set()))]}

    def _t_rimworld_save_game(self, saveName=None, **_):
        """Snapshots the world model; with `saves_dir` set also writes <saveName>.rws (size > 1000 bytes).
        Mode `save_wrong_slot` reproduces the MEASURED lie: success, but the CURRENT slot is rewritten."""
        self.saves = getattr(self, "saves", {})
        d = getattr(self, "saves_dir", None)
        target = getattr(self, "current_save", None) if "save_wrong_slot" in self.modes else saveName
        self.saves[target] = (copy.deepcopy(self.pawns), copy.deepcopy(self.fires), bool(getattr(self, "named", False)))
        path = None
        if d and target:
            path = os.path.join(d, target + ".rws")
            with open(path, "wb") as f:
                f.write(b"<savegame>" + b"x" * (2000 + len(self.pawns)))
        return {"success": True, "path": path or ("%s.rws" % saveName)}

    def _t_rimworld_load_game_ready(self, saveName=None, **_):
        snap = getattr(self, "saves", {}).get(saveName)
        if snap is None:
            return {"success": False, "message": "no save %s" % saveName}
        self.pawns, self.fires, self.named = copy.deepcopy(snap[0]), copy.deepcopy(snap[1]), snap[2]
        self.dialogs = []
        self.queue = []
        self.current_save = saveName
        return {"success": True, "saveName": saveName}

    def _t_jawa_clear_ui(self, **_):
        return {"success": True}

    def _t_rimworld_jump_camera_to_cell(self, **_):
        return {"success": True}

    def _t_rimworld_take_screenshot(self, fileName="shot", **_):
        self.shots += 1
        if self.shot_dir is None:
            return {"success": True, "path": None}
        path = os.path.join(self.shot_dir, "%s.png" % fileName)
        with open(path, "wb") as f:
            f.write(make_png(1280, 720, self.shots))
        return {"success": True, "path": path, "sizeBytes": os.path.getsize(path)}

    def _t_jawa_spawn_pawn(self, kindDef=None, x=0, z=0, faction="hostile", count=1, **_):
        """Row keys as the live tool (JawaBenchTerrainTools.cs SpawnPawn): kindRequested / kindActual /
        kindSubstituted. Mode `spawn_substitutes` reproduces E5 (SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1): the
        pawn comes back a vanilla Colonist."""
        self._fid += 1
        pid = "%s%d" % (kindDef, self._fid)
        actual = "Colonist" if "spawn_substitutes" in self.modes else kindDef
        hostile = faction == "hostile"
        humanlike = actual in ("Colonist", "Villager", "Tribal_Warrior", "Pirate") or hostile
        self.pawns[pid] = pawn_row(pid, kind=actual, faction=("TribeRough" if hostile else
                                   ("PlayerColony" if faction == "player" else None)),
                                   is_player=(faction == "player"), hostile=hostile, x=x, z=z,
                                   intelligence="Humanlike" if humanlike else "Animal")
        ok = actual == kindDef
        return {"success": ok, "spawnedCount": 1 if ok else 0, "substitutedCount": 0 if ok else 1,
                "pawns": [{"ok": ok, "id": pid, "name": pid, "kindRequested": kindDef, "kindActual": actual,
                           "kindSubstituted": not ok, "x": x, "z": z, "spawned": True}]}

    # ------------------------------------------------ rimdrive.Session surface used by TestContext
    def _ticks(self):
        return self.ticks

    def track(self, kind, id_, x=None, z=None):
        self.litter.append({"kind": kind, "id": id_, "x": x, "z": z})

    def things_at(self, x, z):
        return []

    def sweep(self):
        return {"swept": 0, "left": []}


def make_png(w, h, salt=0):
    """A structurally valid PNG larger than the verifier's minimum, distinct per `salt`."""
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    raw = b"".join(b"\x00" + bytes(((x * 7 + y * 13 + salt * 31) & 0xff) for x in range(w * 3 // 2))
                   for y in range(h // 2))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 0)) + chunk(b"IEND", b""))
