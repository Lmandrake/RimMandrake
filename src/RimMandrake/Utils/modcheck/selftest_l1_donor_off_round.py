#!/usr/bin/env python3
"""Offline selftest for modcheck/l1_donor_off_round.py (no game, no bridge).
Run: python3 src/RimMandrake/Utils/modcheck/selftest_l1_donor_off_round.py

Proves, against the REAL repo for the derive half and a scripted fake bridge for the live half:
  derive: the subject list comes from the tracker / P2 table / Phase 0 commits and resolves to defs (the burst, oomb and
    zhool subjects are in it, a removed tracker twin is not); flyers come from MaxFlightTime; art-owed detection sees a
    missing PNG and a Graphic_Multi/Random hit; the save name is read from the P6 census when it exists;
    the donor_off_phase0 tier forbids all three donor ids and carries every DLC (tier_guard refuses a dragged-in donor).
  live: every row can go each way it claims -- tier truth FAILs on a donor in the running list; a spawn with a dead pawn
    FAILs; a governor stop is UNMEASURED, never PASS; the acid burst PASSes on new acid and FAILs on none; the gestation
    death FAILs if acid appears; flight is UNMEASURED/OWNER without his words and a state read with them; the save row
    is UNMEASURED with no save; the log rows FAIL on an exception and are UNMEASURED on a log that is not this load;
    oomb growth PASSes when the kind changes and is UNMEASURED when it never does; the haze row refuses a map whose
    biome did not change and restores the rate it raised; the portal enters and exits; mapgen FAILs an empty map.
"""
import json
import os
import re
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import l1_donor_off_round as L  # noqa: E402

N = [0, 0]


def check(ok, name, why=""):
    N[0] += 1
    if not ok:
        N[1] += 1
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else "  " + str(why)[:300]))


# ----------------------------------------------------------------- fake bridge
class Stop(Exception):
    pass


class FakeBridge(object):
    def __init__(self, **cfg):
        self.cfg = cfg
        self.n = 0
        self.cur = 1
        self.maps = {1: {"mapId": 1, "index": 0, "biome": "TemperateForest", "tile": 100}}
        self.pawns = [{"id": "Human1", "kind": "Colonist", "faction": "PlayerColony", "dead": False, "x": 125, "z": 125,
                       "map": 1}]
        self.things = []
        self.settings = {"zhoolConversionRate": "1", "zhoolConversionEnabled": "True"}
        self.hungry = set()
        self.feed = {}
        self.calls = []
        self.running = cfg.get("running", list(L.DLC) + [L.VEF, "mandrake.rm.biomes"])

    def list_tools(self):
        return [{"name": n} for n in self.cfg.get("tools", [
            "jawa/running_mods", "jawa/spawn_pawn", "jawa/list_pawns", "jawa/list_things", "jawa/thing_graphic",
            "jawa/kill_hostiles", "jawa/static_call", "jawa/pawn_need", "jawa/mod_settings_field",
            "jawa/world_tile_map_generate", "jawa/world_tile_set", "jawa/map_drop", "jawa/biome_probe",
            "jawa/ordered_job", "jawa/set_current_map", "jawa/pawn_flight", "jawa/set_plants", "jawa/spawn_batch",
            "jawa/destroy_bulk", "jawa/safe_advance"])]

    def _id(self, p):
        self.n += 1
        return "%s%d" % (p, self.n)

    def _in(self, o, rect):
        if not rect:
            return o.get("map") == self.cur
        x, z, w, h = [int(v) for v in rect.split(",")]
        return o.get("map") == self.cur and x <= o["x"] < x + w and z <= o["z"] < z + h

    def _add(self, d, x, z, **kw):
        t = dict({"id": self._id(d), "def": d, "x": x, "z": z, "map": self.cur, "hitPoints": 100,
                  "maxHitPoints": 100}, **kw)
        self.things.append(t)
        return t

    def ticks(self, n):
        if self.cfg.get("stop_on_ticks"):
            raise Stop("GovernorStop: vitals latch")
        for p in self.pawns:
            if p["dead"]:
                continue
            if p["kind"] in self.cfg.get("die_after_spawn", ()):
                p["dead"] = True
            if p["id"] in self.hungry and p["kind"] in ("RM_LesserOomb", "RM_GreaterOomb"):
                self.hungry.discard(p["id"])
                if not self.cfg.get("oomb_never_eats"):
                    self.feed[p["id"]] = self.feed.get(p["id"], 0) + 1
                need = 10 if p["kind"] == "RM_LesserOomb" else 20
                if self.feed.get(p["id"], 0) >= need:
                    p["dead"] = True
                    p["gone"] = True
                    into, k = ("RM_Oomb", 1) if p["kind"] == "RM_LesserOomb" else ("RM_LesserOomb", 2)
                    for _ in range(k):
                        self.pawns.append({"id": self._id(into), "kind": into, "faction": "PlayerColony",
                                           "dead": False, "x": p["x"], "z": p["z"], "map": p["map"]})
        zh = [p for p in self.pawns if p["kind"] == "RM_OcularJelly" and not p["dead"]]
        if zh and self.maps[self.cur]["biome"] == "RM_Contagion" and not self.cfg.get("haze_inert"):
            grass = [t for t in self.things if t["def"] == "Plant_Grass"][:3]
            for g in grass:
                g["def"] = "RM_Lashgrass"
        self.pawns = [p for p in self.pawns if not p.get("gone")]
        return {"success": True}

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        h = getattr(self, "t_" + tool.split("/")[1], None)
        return h(**kw) if h else {"success": True}

    # tools
    def t_running_mods(self, **kw):
        return {"success": True, "packageIds": self.running}

    def t_set_game_speed(self, **kw):
        return {"success": True}

    def t_map_info(self, **kw):
        m = self.maps[self.cur]
        return {"success": True, "mapId": self.cur, "tile": m["tile"], "mapBiome": m["biome"], "sizeX": 250,
                "sizeZ": 250}

    def t_list_pawns(self, rect=None, faction=None, includeCorpses=False, limit=500, **kw):
        out = []
        for p in self.pawns:
            if not self._in(p, rect):
                continue
            if p["dead"] and not includeCorpses:
                continue
            if faction == "player" and p["faction"] != "PlayerColony":
                continue
            out.append({"id": p["id"], "kind": p["kind"], "faction": p["faction"], "dead": p["dead"],
                        "downed": False, "x": p["x"], "z": p["z"]})
        return {"success": True, "pawns": out}

    def t_spawn_pawn(self, kindDef, x, z, faction="hostile", count=1, **kw):
        if kindDef in self.cfg.get("unknown_kinds", ()):
            return {"success": False, "error": "Unknown kindDef"}
        rows = []
        fac = {"none": None, "player": "PlayerColony", "hostile": "Pirate"}.get(faction, faction)
        for i in range(count):
            p = {"id": self._id(kindDef), "kind": kindDef, "faction": fac, "dead": False, "x": x, "z": z + i,
                 "map": self.cur}
            self.pawns.append(p)
            rows.append({"ok": True, "id": p["id"], "kindActual": kindDef, "kindSubstituted": False})
        return {"success": True, "spawnedCount": count, "pawns": rows}

    def t_thing_graphic(self, thing=None, **kw):
        ids = (thing or "").split(",")
        return {"success": True, "things": [{"id": i, "badTex": i.startswith(tuple(self.cfg.get("bad_tex", ()))) and
                                              bool(self.cfg.get("bad_tex")), "resolvedPath": "Things/x"} for i in ids]}

    def t_destroy_bulk(self, filter=None, **kw):
        if filter == "factionlessAnimals":
            self.pawns = [p for p in self.pawns if p["faction"] is not None]
        elif filter == "playerAnimals":
            self.pawns = [p for p in self.pawns if p["kind"] == "Colonist" or p["faction"] != "PlayerColony"]
        elif filter == "nonColonists":
            self.pawns = [p for p in self.pawns if p["kind"] == "Colonist"]
        return {"success": True}

    def t_list_things(self, defName=None, rect=None, group=None, limit=200, **kw):
        if group == "Plant":
            n = self.maps[self.cur].get("plants", len([t for t in self.things if t["map"] == self.cur]))
            return {"success": True, "things": [], "countMatched": n}
        want = set((defName or "").split(","))
        got = [t for t in self.things if t["def"] in want and self._in(t, rect)]
        return {"success": True, "things": got, "countMatched": len(got)}

    def t_spawn_batch(self, ops=None, **kw):
        for op in (ops or "").split(";"):
            d, rest = op.split(":")
            q = [int(v) for v in rest.split(",")]
            self._add(d, q[0], q[1])
        return {"success": True}

    def t_set_plants(self, ops=None, **kw):
        for op in (ops or "").split(";"):
            d, rest = op.split(":")
            x, z, w, h = [int(v) for v in rest.split(",")]
            for i in range(min(w * h, 40)):
                self._add(d, x + i % w, z + i // w)
        return {"success": True}

    def _burst(self, p):
        if p["kind"] in self.cfg.get("acid_kinds", ()):
            for i in range(4):
                self._add(L.ACID_FILTH, p["x"] + i % 2, p["z"] + i // 2)
        if p["kind"] in self.cfg.get("flame_kinds", ()):
            for t in self.things:
                if t["def"] == L.SENTINEL and abs(t["x"] - p["x"]) <= 2:
                    t["hitPoints"] = 60

    def t_kill_hostiles(self, pawnDef=None, **kw):
        for p in self.pawns:
            if p["kind"] == pawnDef and p["faction"] == "Pirate" and not p["dead"]:
                p["dead"] = True
                self._burst(p)
        return {"success": True}

    def t_static_call(self, type=None, method=None, args="", **kw):
        if method != "CompleteGestation":
            return {"success": True}
        pid = args.split("|")[0]
        for p in self.pawns:
            if p["id"] == pid:
                p["dead"] = True
                self._add("Kidney", p["x"], p["z"])
                if self.cfg.get("gestation_bursts"):
                    self._burst(p)
        return {"success": True, "result": "null"}

    def t_pawn_need(self, pawn=None, **kw):
        self.hungry.add(pawn)
        return {"success": True}

    def t_comp_read(self, thing=None, **kw):
        return {"success": True, "values": {"feedingsCounter": str(self.feed.get(thing, 0))}}

    def t_mod_settings_field(self, typeName=None, action="get", field=None, value=None, **kw):
        if action == "set":
            self.settings[field] = value
        return {"success": True, "value": self.settings.get(field)}

    def t_world_tile_set(self, tiles=None, biome=None, **kw):
        self.pending = (int(tiles), biome)
        return {"success": True}

    def t_world_commit(self, **kw):
        tile, biome = getattr(self, "pending", (None, None))
        if self.cfg.get("biome_sticks_not"):
            return {"success": True}
        for m in self.maps.values():
            if m["tile"] == tile and biome:
                m["biome"] = biome
        return {"success": True}

    def t_set_current_map(self, mapId=None, **kw):
        if mapId not in self.maps:
            return {"success": False, "details": {"loadedMaps": [dict(m) for m in self.maps.values()]}}
        self.cur = mapId
        return {"success": True}

    def t_ordered_job(self, pawnId=None, jobDef=None, targetAId=None, **kw):
        t = next((t for t in self.things if t["id"] == targetAId), None)
        col = next(p for p in self.pawns if p["id"] == pawnId)
        if t and t["def"] == L.SARLACC["portal"] and not self.cfg.get("portal_dead"):
            mid = max(self.maps) + 1
            self.maps[mid] = {"mapId": mid, "index": len(self.maps), "biome": "Underground", "tile": 100}
            self.things.append({"id": self._id("CaveExit"), "def": "CaveExit", "x": 5, "z": 5, "map": mid})
            col["map"] = mid
        elif t and t["def"] == "CaveExit":
            col["map"] = 1
        return {"success": True}

    def t_tile_settleable(self, tiles=None, **kw):
        return {"success": True, "tiles": [{"tile": int(t), "settleable": True} for t in tiles.split(",")]}

    def t_world_tile_get(self, tiles=None, **kw):
        return {"success": True, "tiles": [{"tile": int(tiles), "biome": "TemperateForest"}]}

    def t_world_tile_map_generate(self, tile=None, biome=None, **kw):
        mid = max(self.maps) + 1
        self.maps[mid] = {"mapId": mid, "index": len(self.maps), "biome": biome, "tile": tile,
                          "plants": 0 if biome in self.cfg.get("empty_biomes", ()) else 500}
        if biome not in self.cfg.get("empty_biomes", ()):
            for i in range(3):
                self.pawns.append({"id": self._id("Wild"), "kind": "RM_Wuum", "faction": None, "dead": False,
                                   "x": i, "z": i, "map": mid})
        return {"success": True, "mapIndex": self.maps[mid]["index"]}

    def t_map_drop(self, mapIndex=None, **kw):
        for k, m in list(self.maps.items()):
            if m["index"] == mapIndex and k != 1:
                del self.maps[k]
        return {"success": True}

    def t_biome_probe(self, biomes=None, find=None, **kw):
        names = (find or "").split(",") if find else []
        return {"success": True, "biomes": [{"defName": b, "findResults": [
            {"name": n, "state": "absent" if n in self.cfg.get("absent_rows", ()) else "spawning"} for n in names]}
            for b in (biomes or "").split(",")]}

    def t_pawn_flight(self, kind=None, **kw):
        return {"success": True, "pawns": [{"canEverFly": True, "maxFlightTimeStat": 10, "flightState": "Grounded"}]}

    def t_savegame_mod_match(self, **kw):
        return {"success": True, "loadedModsSummary": "x"}


class FakeTap(object):
    def __init__(self, entries=()):
        self.entries = list(entries)
        self.last = 0
        self.lost = 0

    def poll(self):
        pass

    def since(self, mark=None):
        return [e for e in self.entries if e["Sequence"] > (mark or 0)]


def fake_V(log_path, tap_entries=()):
    V = types.SimpleNamespace()
    V.PLAYER_LOG = log_path
    V.prepare_site = lambda B, rect, rows, rid: True
    V.log_revive = lambda B: {"alive": True, "cleared": True}
    V.tap_start = lambda B: FakeTap(tap_entries)
    V._wait_playing = lambda B, budget_s=0: (True, 3)
    return V


def args(**kw):
    a = dict(phase="all", owner_present=None, save=None, player_log=None, only_kinds=None, only_biomes=None,
             force=True, out=None)
    a.update(kw)
    return types.SimpleNamespace(**a)


def species(kind, **kw):
    s = {"race": kind, "kind": kind, "kinds": [kind], "source": ["test"], "texPaths": ["Things/Pawn/Animal/%s/%s" % (kind, kind)],
         "texOwed": [], "flyer": False}
    s.update(kw)
    return s


MAN = {"tier": {"closure": list(L.DLC) + [L.VEF, "mandrake.rm.biomes"]}, "head": "test",
       "species": [species("RM_Wuum"), species("RM_Zhissa")], "plants": [{"def": "RSW_Plant_JoganTree_Wild",
       "texPaths": ["Things/Plant/RSW_Plant_JoganTree_Wild"], "texOwed": []}],
       "biomes": [{"biome": "RM_GelatinousSlime", "portRows": ["RM_Wuum"], "donorGuarded": [], "tileTemperature": 22.5}],
       "flyers": ["RSW_Porg"], "bursts": L.BURSTS, "oomb": L.OOMB, "haze": L.HAZE, "sarlacc": L.SARLACC,
       "save": None, "donorNames": {"old": ["sw_Sarlacc"], "new": ["RSW_Sarlacc"]}}


def go(rd, ph):
    rd.phase_pre()
    getattr(rd, "phase_" + ph)()
    return {r["id"]: r for r in rd.rows}


def mk(cfg=None, man=None, a=None, log=None, tap=()):
    B = FakeBridge(**(cfg or {}))
    rd = L.Round(B, json.loads(json.dumps(man or MAN)), a or args(), fake_V(log, tap))
    return B, rd


# ------------------------------------------------------------------ live tests
def test_pre():
    B, rd = mk()
    r = go(rd, "spawn")
    check(r["P01_TIER_TRUTH"]["status"] == "PASS", "tier truth PASS on a donor-free list with DLC and VEF", r["P01_TIER_TRUTH"])
    B, rd = mk({"running": list(L.DLC) + [L.VEF, "sarg.alphaanimals"]})
    r = go(rd, "spawn")
    check(r["P01_TIER_TRUTH"]["status"] == "FAIL", "tier truth FAILs on Alpha Animals in the running list")
    B, rd = mk({"running": [L.VEF, "ludeon.rimworld"]})
    r = go(rd, "spawn")
    check(r["P01_TIER_TRUTH"]["status"] == "FAIL", "tier truth FAILs on a missing DLC")
    B, rd = mk({"tools": ["jawa/running_mods"]})
    r = go(rd, "spawn")
    check(r["P02_TOOLS"]["status"] == "FAIL", "a missing bridge tool FAILs P02")


def test_spawn():
    B, rd = mk()
    r = go(rd, "spawn")
    check(r["SPAWN_RM_Wuum"]["status"] == "PASS", "a species that stays alive PASSes", r["SPAWN_RM_Wuum"])
    B, rd = mk({"die_after_spawn": ("RM_Zhissa",)})
    r = go(rd, "spawn")
    check(r["SPAWN_RM_Zhissa"]["status"] == "FAIL" and r["SPAWN_RM_Wuum"]["status"] == "PASS",
          "a species that dies FAILs, its batch-mate still PASSes", r["SPAWN_RM_Zhissa"])
    B, rd = mk({"stop_on_ticks": True})
    r = go(rd, "spawn")
    check(r["SPAWN_RM_Wuum"]["status"] == "UNMEASURED", "a governor stop is UNMEASURED, never PASS")
    B, rd = mk({"bad_tex": ("RM_Wuum",)})
    r = go(rd, "spawn")
    check(r["SPAWN_RM_Wuum"]["status"] == "FAIL", "badTex FAILs the spawn row", r["SPAWN_RM_Wuum"])
    B, rd = mk(tap=[{"Sequence": 5, "Message": "Failed to find any textures at Things/Pawn/Animal/RM_Wuum/RM_Wuum"}])
    r = go(rd, "spawn")
    check(r["SPAWN_RM_Wuum"]["status"] == "FAIL", "a new log line naming the texPath FAILs the spawn row")
    left = [p for p in B.pawns if p["faction"] is None]
    check(not left, "each batch is cleaned up (factionless animals destroyed)", left)


def test_bursts():
    B, rd = mk({"acid_kinds": ("RM_BloodyMess", "RM_InfectedAerofleet", "RM_Scorchpod"), "flame_kinds": ("RM_Bulloo",)})
    r = go(rd, "burst")
    for rid in ("BURST_BLOODYMESS_KILLED", "BURST_BLISTERED_BULLOO", "BURST_SCORCHPOD", "BURST_BULLOO",
                "BURST_BLOODYMESS_GESTATION"):
        check(r[rid]["status"] == "PASS", "%s PASSes on its tell" % rid, r[rid])
    B, rd = mk({"acid_kinds": ()})
    r = go(rd, "burst")
    check(r["BURST_BLOODYMESS_KILLED"]["status"] == "FAIL", "a killed Bloody Mess with no acid FAILs (the row can go red)")
    check(r["BURST_BULLOO"]["status"] == "FAIL", "a bulloo death that hurts nothing FAILs")
    B, rd = mk({"acid_kinds": ("RM_BloodyMess",), "gestation_bursts": True})
    r = go(rd, "burst")
    check(r["BURST_BLOODYMESS_GESTATION"]["status"] == "FAIL", "acid on the gestation death FAILs (owner Q3)")


def test_oomb():
    B, rd = mk()
    r = go(rd, "oomb")
    check(r["OOMB_GROWTH"]["status"] == "PASS", "lesser oomb grows into the oomb", r["OOMB_GROWTH"])
    check(r["OOMB_SPLIT"]["status"] == "PASS", "greater oomb splits into two lesser oombs", r["OOMB_SPLIT"])
    B, rd = mk({"oomb_never_eats": True})
    r = go(rd, "oomb")
    check(r["OOMB_GROWTH"]["status"] == "UNMEASURED" and r["OOMB_GROWTH"]["detail"]["counter"] is not None,
          "no growth inside the budget is UNMEASURED with the counter read", r["OOMB_GROWTH"])


def test_haze():
    B, rd = mk()
    r = go(rd, "haze")
    check(r["HAZE_ZHOOL"]["status"] == "PASS", "zhool haze converts grass on a Contagion map", r["HAZE_ZHOOL"])
    check(B.settings["zhoolConversionRate"] == "1", "the raised conversion rate is restored", B.settings)
    check(B.maps[1]["biome"] == "TemperateForest", "the home tile's biome is restored", B.maps[1])
    B, rd = mk({"haze_inert": True})
    r = go(rd, "haze")
    check(r["HAZE_ZHOOL"]["status"] == "FAIL", "no conversion FAILs (can go red)")
    B, rd = mk({"biome_sticks_not": True})
    r = go(rd, "haze")
    check(r["HAZE_ZHOOL"]["status"] == "UNMEASURED", "a map whose biome did not change is UNMEASURED/SITE")


def test_portal():
    B, rd = mk()
    r = go(rd, "portal")
    check(r["PORTAL_ENTER"]["status"] == "PASS" and r["PORTAL_EXIT"]["status"] == "PASS", "enter and exit the Sarlacc",
          (r.get("PORTAL_ENTER"), r.get("PORTAL_EXIT")))
    B, rd = mk({"portal_dead": True})
    r = go(rd, "portal")
    check(r["PORTAL_ENTER"]["status"] == "FAIL", "no pocket map FAILs PORTAL_ENTER")


def test_mapgen():
    B, rd = mk()
    r = go(rd, "mapgen")
    check(r["MAPGEN_RM_GelatinousSlime"]["status"] == "PASS", "a generated map with animals PASSes",
          r["MAPGEN_RM_GelatinousSlime"])
    check(r["ROSTER_RM_GelatinousSlime"]["status"] == "PASS", "a spawning port row PASSes the roster row")
    check(set(B.maps) == {1}, "the scratch map is dropped", B.maps)
    B, rd = mk({"empty_biomes": ("RM_GelatinousSlime",), "absent_rows": ("RM_Wuum",)})
    r = go(rd, "mapgen")
    check(r["MAPGEN_RM_GelatinousSlime"]["status"] == "FAIL", "an empty map FAILs")
    check(r["ROSTER_RM_GelatinousSlime"]["status"] == "FAIL", "an absent port row FAILs the roster row")


def test_flight_and_save():
    B, rd = mk()
    r = go(rd, "flight")
    check(r["FLIGHT_RSW_Porg"]["status"] == "UNMEASURED" and r["FLIGHT_RSW_Porg"]["class"] == "OWNER",
          "flight is skipped as UNMEASURED/OWNER without the owner")
    check(not [c for c in B.calls if c[0] == "jawa/pawn_flight"], "no flight tool is called without the owner")
    B, rd = mk(a=args(owner_present="ok go ahead with the flight read"))
    r = go(rd, "flight")
    check(r["FLIGHT_RSW_Porg"]["status"] == "PASS", "with his words the state read PASSes", r["FLIGHT_RSW_Porg"])
    fl = [c for c in B.calls if c[0] == "jawa/pawn_flight"]
    check(fl and all(c[1].get("action") == "report" for c in fl), "the flight call is report-only", fl)
    B, rd = mk()
    r = go(rd, "save")
    check(r["SAVE_LOAD"]["status"] == "UNMEASURED", "no fixed save is UNMEASURED")


def test_log():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "Player.log")
    open(p, "w").write("[JawaBench] ready: 300 tools, build x\nConfig error in Foo\n"
                       "Could not resolve cross-reference to Verse.ThingDef named RSW_Ghost\n"
                       "Failed to find any textures at Things/Pawn/Animal/RM_Zhissa/RM_Zhissa\n"
                       "System.NullReferenceException: boom\n")
    B, rd = mk(a=args(player_log=p))
    r = go(rd, "log")
    check(r["L01_FIRST_EXCEPTION"]["status"] == "FAIL" and "Config error" in r["L01_FIRST_EXCEPTION"]["detail"]["first"],
          "first-exception row FAILs and names the first line", r["L01_FIRST_EXCEPTION"])
    check(r["L02_XREF_OURS"]["status"] == "FAIL", "a cross-ref to RSW_ FAILs")
    check(r["L03_TEX_PORTED"]["status"] == "FAIL" and r["L04_TEX_OURS"]["status"] == "FAIL", "a ported texture miss FAILs")
    q = os.path.join(d, "old.log")
    open(q, "w").write("System.NullReferenceException\n")
    B, rd = mk(a=args(player_log=q))
    r = go(rd, "log")
    check(r["L01_FIRST_EXCEPTION"]["status"] == "UNMEASURED", "a log without this load's JawaBench line is UNMEASURED")
    clean = os.path.join(d, "clean.log")
    open(clean, "w").write("[JawaBench] ready: 300 tools, build x\nNo textures found at Things/Item/Other\n")
    B, rd = mk(a=args(player_log=clean))
    r = go(rd, "log")
    check(all(r[k]["status"] == "PASS" for k in ("L01_FIRST_EXCEPTION", "L02_XREF_OURS", "L03_TEX_PORTED",
                                                  "L04_TEX_OURS")), "a clean log PASSes all four", r)


# ----------------------------------------------------------------- derive tests
def test_parsers():
    d = tempfile.mkdtemp()
    t = os.path.join(d, "tracker.md")
    open(t, "w").write("| species | class | twin | W0 | canon | rows | status | sha |\n|---|---|---|---|---|---|---|---|\n"
                       "| A | x | RSW_A | MATCH | a | 0 | PORTED | s |\n| B | x | RSW_B (removed) | x | b | 0 | PORTED | s |\n"
                       "| C | x | RSW_C | x | c | 0 | DECLINED | s |\n")
    keep, skipped = L.tracker_names(t)
    check(keep == ["RSW_A"], "tracker keeps PORTED twins only", keep)
    check({s["name"] for s in skipped} == {"RSW_B (removed)", "RSW_C"}, "removed and declined twins are listed", skipped)
    c = os.path.join(d, "p2.md")
    open(c, "w").write("| 1 | AA_X | Forge | plain | **RM_X** (TheForge) |\n| 2 | AA_Y | x | plain | NOT ported: Q1 |\n"
                       "| 3 | AA_Z | x | RIDER | P3 |\n| 4 | AA_W | x | MATCH | RM_W (W0 identical); row repointed |\n")
    check(L.classification_names(c) == ["RM_X", "RM_W"], "P2 outcomes skip NOT ported and P3", L.classification_names(c))
    idx = {"Things/Pawn/A/A_south", "Things/Plant/P/P1", "Things/Item/I"}
    check(not L.tex_owed("Things/Pawn/A/A", idx), "Graphic_Multi facings serve a texPath")
    check(not L.tex_owed("Things/Plant/P", idx), "a Graphic_Random folder serves a texPath")
    check(not L.tex_owed("Things/Item/I", idx), "an exact file serves a texPath")
    check(L.tex_owed("Things/Item/Missing", idx), "a texPath with no PNG is owed")
    s = os.path.join(d, "census.md")
    open(s, "w").write("wrote `CANONICAL_ASHKARR_START_2026-09-12_donorfree.rws` (backup first)\n")
    check(L.find_fixed_save(s) == "CANONICAL_ASHKARR_START_2026-09-12_donorfree", "fixed save read from the P6 census")
    check(L.find_fixed_save(os.path.join(d, "nope.md")) is None, "no census -> no save (the row says UNMEASURED)")


def test_tier():
    import modset_builder as M
    t = M.TIERS.get(L.TIER)
    check(t is not None, "modset_builder has the %s tier" % L.TIER)
    if not t:
        return
    check(set(L.DONORS) <= set(x.lower() for x in t.get("forbid", ())), "the tier forbids all three donor ids", t.get("forbid"))
    check(t.get("dlc") is True, "the tier carries every DLC (owner 2026-09-19)")
    check(not set(L.DONORS) & set(x.lower() for x in t["want"]), "no donor is wanted")
    ref = M.tier_guard(t, list(M.DLC_IDS) + ["sarg.alphaanimals"])
    check(any("sarg.alphaanimals" in x for x in ref), "tier_guard refuses a closure that drags Alpha Animals back", ref)
    ref = M.tier_guard(t, [d for d in M.DLC_IDS if not d.endswith("odyssey")])
    check(any("DLC missing" in x for x in ref), "tier_guard refuses a list missing a DLC", ref)


def test_derive_real_repo():
    closure = {"ordered": list(L.DLC) + ["mandrake.rm.biomes", "mandrake.rsw.swbestiary", "mandrake.rsw.shokk",
                                         "mandrake.rut.patches"], "missing": [], "refusals": []}
    man = L.derive(closure=closure)
    kinds = {s["kind"] for s in man["species"]}
    for k in ("RM_BloodyMess", "RM_Bulloo", "RM_InfectedAerofleet", "RM_Scorchpod", "RM_OcularJelly", "RM_LesserOomb",
              "RM_GreaterOomb", "RM_Thunderbeast", "RSW_Bantha"):
        check(k in kinds, "derived subjects include %s" % k)
    check(not man["problems"], "every mechanism subject resolves to a def", man["problems"])
    check(not any(s["race"] == "RSW_Aiwha" for s in man["species"]), "the owner-retired Aiwha is not a subject")
    check(man["gitError"] is None and man["commitFiles"], "the Phase 0 commits resolve to Def files", man["gitError"])
    check(all(s["flyer"] for s in man["species"] if s["kind"] in man["flyers"]) and "RSW_Porg" in man["flyers"],
          "flyers come from MaxFlightTime (the porg flies)", man["flyers"][:6])
    check(not any(s["flyer"] for s in man["species"] if s["kind"] in ("RSW_Bantha", "RM_Bulloo")),
          "a ground animal and a VEF floater are not flyers")
    names = {b["biome"] for b in man["biomes"]}
    check({"RM_TheRot", "RM_Webwork", "RUT_AridShrubland", "RM_Contagion"} <= names,
          "the W4 handoff's three biomes and the Contagion are mapgen subjects", sorted(names))
    check(not any(b.startswith("RUT_") and b != "RUT_AridShrubland" for b in names),
          "frozen RUT_ twins are not mapgen subjects by default")
    check(all(r["id"].startswith("O0") for r in L.offline_rows(man)), "offline gate rows are produced")
    check(man["donorNames"]["old"] and "sw_Sarlacc" in man["donorNames"]["old"], "donor rename names read for the save row")


def main():
    for t in (test_pre, test_spawn, test_bursts, test_oomb, test_haze, test_portal, test_mapgen, test_flight_and_save,
              test_log, test_parsers, test_tier, test_derive_real_repo):
        t()
    print("\n%d checks, %d failed" % (N[0], N[1]))
    return 1 if N[1] else 0


if __name__ == "__main__":
    sys.exit(main())
