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
        self.queue = []            # queued incidents
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
        if p["isPlayer"] and p["intelligence"] == "Humanlike":
            self.stats["colonistsKilled"] += 1
            self.letters.append({"defName": "Death", "label": "Death: %s" % pid,
                                 "arrivalTick": self.ticks})

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
        return {"success": True, "mapId": 0, "sizeX": self.size, "sizeZ": self.size,
                "cellCount": self.size * self.size, "mapBiome": "FakeBland"}

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
        if defName == "Fire":
            return {"success": True, "things": [dict(f, **{"def": "Fire"}) for f in self.fires],
                    "scanned": 43183, "countReturned": len(self.fires), "countMatched": len(self.fires),
                    "isCompleteList": True, "truncated": 0, "ticksGame": self.ticks}
        return {"success": True, "things": [], "scanned": 0, "countReturned": 0, "countMatched": 0,
                "isCompleteList": True, "truncated": 0, "ticksGame": self.ticks}

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
        if action == "kill" and "kill_noop" not in self.modes:
            if "kill_explodes" in self.modes and p["kind"] == "Boomalope":
                for i in range(25):                      # MEASURED: 25 fires within 5 ticks of one death
                    self.add_fire(p["x"] + i % 5, p["z"] + i // 5)
            self.kill(pawn)
        return {"success": True, "action": action, "deadBefore": before, "deadAfter": p["dead"],
                "changed": p["dead"] != before}

    def _t_jawa_destroy_bulk(self, filter=None, dryRun=True, **_):
        ids = [pid for pid, p in self.pawns.items()
               if filter == "factionlessAnimals" and p["faction"] is None and p["intelligence"] == "Animal" and not p["dead"]]
        if not dryRun:
            for pid in ids:
                del self.pawns[pid]
        return {"success": True, "dryRun": dryRun, "filter": filter, "matchedCount": len(ids),
                "destroyed": [{"thingId": i} for i in ids]}

    def _t_jawa_damage(self, thingId=None, damageDef="Cut", amount=10, **_):
        # the measured lie: success with a big amount, target may still be alive
        p = self.pawns.get(thingId)
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

    # ------------------------------------------------ extra reads the snapshot takes (full tier)
    def _t_jawa_alerts_list(self):
        return {"success": True, "count": 0, "alerts": [], "ticksGame": self.ticks}

    def _t_jawa_weather_get(self, **_):
        return {"success": True, "readErrors": [], "weather": {"current": "Clear"}, "conditions": [],
                "activeConditionCount": 0, "storyteller": {"def": "Cassandra", "difficulty": "Rough",
                                                            "threatScale": self.difficulty["threatScale"],
                                                            "allowBigThreats": self.difficulty["allowBigThreats"]}}

    def _t_jawa_drain_log(self, limit=50, errorsOnly=False, **_):
        return {"success": True, "messages": [], "totalInBuffer": 0, "ticksGame": self.ticks}

    def _t_jawa_window_list_close(self, action="list", **_):
        return {"success": True, "action": action, "count": 0, "windows": [], "ticksGame": self.ticks}

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
        self._fid += 1
        pid = "%s%d" % (kindDef, self._fid)
        hostile = faction == "hostile"
        self.pawns[pid] = pawn_row(pid, kind=kindDef, faction=("TribeRough" if hostile else
                                   ("PlayerColony" if faction == "player" else None)),
                                   is_player=(faction == "player"), hostile=hostile, x=x, z=z)
        return {"success": True, "spawnedCount": 1, "pawns": [{"id": pid, "name": pid}]}

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
