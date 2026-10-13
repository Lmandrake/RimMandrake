#!/usr/bin/env python3
"""Offline selftest for the Pyrelands north-star site preparation (PYRELANDS_GREEN_MINIMAL_1).

No game, no bridge, no ModsConfig.xml, no Saves/ folder: every bridge answer comes from FakeGame
below and every machine read from a temp-dir Env. Proves each pre-flight row REFUSES the dirty
case it exists for (and names its row id), that "could not ask" is UNMEASURED and refuses, that
the manifests/defaults cannot drift from validation.py and the C# source, and that the site recipe
runs end to end, restores its toggles on failure and never overwrites a save.
Run: python3 src/RimMandrake/Pyrelands/selftest_pyrelands_site.py
"""
import contextlib
import csv
import glob
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)

import preflight_pyrelands as P          # noqa: E402
import northstar_site as S               # noqa: E402
import modset_builder as mb              # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def rows_by_id(rows):
    return {r.id: r for r in rows}


# ------------------------------------------------------------------ fake world + game

W, H = 40, 30                                        # synthetic hex lattice, 1200 tiles


def tid(c, r):
    return r * W + c


def hex_nbrs(t):
    c, r = t % W, t // W
    d = [(1, 0), (-1, 0), (0, 1), (0, -1)] + ([(-1, 1), (-1, -1)] if r % 2 == 0 else [(1, 1), (1, -1)])
    out = [tid(c + dc, r + dr) for dc, dr in d if 0 <= c + dc < W and 0 <= r + dr < H]
    return out


def world_rows():
    rows = {}
    for t in range(W * H):
        c, r = t % W, t // W
        lat = (r - H // 2) * 3.0                      # rows 7..22 are |lat| <= 25
        water = c < 3 or (c in (20, 21) and r < 18)   # an ocean edge + an inlet
        rows[t] = {"tile": t, "lat": lat, "long": c * 9.0 - 180, "biome": "Ocean" if water else "AridShrubland",
                   "elevation": 100, "temperature": 25.0, "rainfall": 300, "hilliness": "Flat",
                   "swampiness": 0, "pollution": 0, "waterCovered": water,
                   "riverCount": 1 if (c == 10 and 10 <= r <= 20) else 0,
                   "roadCount": 0, "mutatorCount": 0, "mutators": [], "landmark": None}
    rows[tid(30, 15)]["landmark"] = "Some Landmark"
    return rows


class FakeGame(object):
    TOOLS = {"jawa/mod_inventory", "jawa/running_mods", "jawa/get_defs", "jawa/mod_settings_field",
             "jawa/window_list_close", "rimworld/step_game_ticks", "rimworld/take_screenshot", "jawa/weather_get", "jawa/weather_set",
             "jawa/map_info", "jawa/world_mutators_get", "jawa/world_mutators_set", "jawa/list_things",
             "jawa/get_roof_batch", "jawa/cell_temperature", "rimworld/get_cell_info", "jawa/world_tile_get",
             "jawa/time_clock", "jawa/incident_queue_clear", "jawa/list_pawns", "jawa/storyteller_swap",
             "rimworld/get_ui_state", "rimworld/go_to_main_menu", "rimworld/start_debug_game_ready",
             "rimworld/get_game_info", "jawa/world_info_get", "jawa/world_tile_export", "jawa/world_neighbors",
             "jawa/world_tile_set", "jawa/world_commit", "jawa/world_tile_map_generate", "jawa/colony_found", "jawa/set_current_map",
             "jawa/spawn_pawn", "jawa/set_fog", "jawa/time_date_at", "jawa/time_set_ticks",
             "rimworld/save_game", "rimworld/load_game", "jawa/name_colony", "jawa/spawn_batch", "jawa/pawn_need"}

    def __init__(self, manifest, dll_shas, faults=(), saves_dir=None):
        self.faults = set(faults)
        self.tools = set(self.TOOLS)
        self.manifest = list(manifest)
        self.dll_shas = dll_shas
        self.settings = {k: str(v) for k, v in P.DEFAULTS.items()}
        self.windows = []
        self.weather, self.storyteller, self.queue = "Clear", "Tutor", []
        self.ticks, self.abs_off, self.paused = 5000, 3600000 * 5500 // 1000, True
        self.state = "Entry"
        self.world = world_rows()
        self.maps = {1: {"tile": tid(35, 15), "biome": "AridShrubland"}}
        self.current = 1
        self.food = []          # [(x, z, stackCount)] spawned through spawn_batch
        self.needs = {}         # pawn id -> {"Food": level}
        self.pawns = [{"id": "C%d" % i, "faction": "PlayerColony", "dead": False, "downed": False} for i in range(3)]
        self.saves_dir = saves_dir
        self.calls = []
        self.site = None
        self.named = False        # unnamed colony: ticks raise the naming dialog and hop to map 1 (live 2026-10-11)
        self.saved_named = None
        self.queue_clears = 0
        if "modal" in self.faults:
            self.windows.append({"type": "Dialog_NodeTree", "optionalTitle": "a letter"})
        if "logwin" in self.faults:
            self.windows.append({"type": "EditWindow_Log", "optionalTitle": None})

    # --- helpers
    def _map(self):
        return self.maps[self.current]

    def call(self, tool, **p):
        self.calls.append((tool, p))
        f = self.faults
        if tool == "jawa/mod_inventory":
            ids = list(self.manifest)
            if "extra_mod" in f:
                ids.append("zylle.mapdesigner")
            if "no_odyssey" in f:
                ids.remove("ludeon.rimworld.odyssey")
            if "reorder" in f:
                ids[-1], ids[-2] = ids[-2], ids[-1]
            return {"success": True, "mods": [{"loadOrder": i, "packageId": x} for i, x in enumerate(ids)]}
        if tool == "jawa/running_mods":
            asm = p["assembly"]
            sha = self.dll_shas[asm]
            if "dll_drift" in f and asm == "FireEcologyHook":
                sha = "0" * 64
            pid = {"FireEcologyHook": "mandrake.rm.biomes", "RimMandrake.Biomes": "mandrake.rm.biomes",
                   "RimMandrake.Utinni.PyrelandsMechanics": "mandrake.rut.pyrelandsmechanics",
                   "RimMandrake.Utinni.UtinniPatches": "mandrake.rut.patches"}[asm]
            m = [{"location": "x", "mvid": "mv-" + asm, "sha256": sha, "claimedBy": [pid]}]
            if "dll_twice" in f and asm == "RimMandrake.Biomes":
                m = m * 2
            return {"success": True, "assembly": {"name": asm, "matchCount": len(m), "matches": m}}
        if tool == "jawa/get_defs":
            if "defs_fail" in f:
                return {"success": False, "message": "InvalidCastException"}
            specs = p["defs"].split(";")
            nf = ["ThingDef/RM_FE_Plant_ScorchFruit"] if "defs_missing" in f else []
            rows = [{"requested": x, "found": x not in nf, "defType": x.split("/")[0], "defName": x.split("/")[1],
                     "packageId": "mandrake.rm.biomes"} for x in specs]
            return {"success": True, "foundCount": len(specs) - len(nf), "notFound": nf, "defs": rows}
        if tool == "jawa/mod_settings_field":
            fld = p["field"]
            if p["action"] == "set":
                self.settings[fld] = p["value"]
                return {"success": True, "valueAfter": p["value"]}
            v = self.settings[fld]
            if "setting_off" in f and fld == "fulguriteEnabled":
                v = "False"
            return {"success": True, "field": fld, "value": v}
        if tool == "rimworld/step_game_ticks":
            n = int(p.get("ticks") or 0)
            first = self.ticks - self.ticks % 1000 + 200
            if first <= self.ticks:
                first += 1000
            crosses = first <= self.ticks + n
            self.ticks += n
            if not self.named and crosses and len(self.maps) > 1:
                # Faction.FactionTick: TicksGame % 1000 == 200 -> Dialog_NamePlayerFactionAndSettlement, which
                # force-pauses and makes the quicktest colony (map 1) current.
                self.windows.append({"type": "Dialog_NamePlayerFactionAndSettlement", "forcePause": True})
                self.current = 1
            return {"success": True, "status": "completed", "completedTicks": n}
        if tool == "jawa/name_colony":
            if "name_refused" in f:
                return {"success": True, "factionName": p.get("factionName"), "settlements": []}
            self.named = True
            return {"success": True, "factionName": p.get("factionName"),
                    "settlements": [{"tile": m["tile"], "name": p.get("settlementName"), "namedByPlayer": True}
                                    for m in self.maps.values()]}
        if tool == "jawa/window_list_close":
            if p.get("action") == "close":
                self.windows = [w for w in self.windows if w["type"] != p.get("typeName")
                                and not (p.get("closeAll") and p.get("typeName", "") in w["type"])]
                return {"success": True, "closedCount": 1}
            return {"success": True, "count": len(self.windows), "windows": list(self.windows)}
        if tool == "rimworld/take_screenshot":
            return {"success": True, "path": "C:/shots/x.png"}
        if tool == "jawa/weather_get":
            return {"success": True, "weather": "Rain" if "rain" in f else self.weather,
                    "storyteller": "Cassandra" if "loud" in f else self.storyteller}
        if tool == "jawa/weather_set":
            if p.get("weather"):
                self.weather = p["weather"]
            return {"success": True, "before": "x", "after": self.weather}
        if tool == "jawa/storyteller_swap":
            before = self.storyteller
            self.storyteller = p["storytellerDef"]
            return {"success": True, "before": before, "after": self.storyteller}
        if tool == "jawa/incident_queue_clear":
            self.queue_clears += 1
            n = 2 if "queue" in f else 0
            return {"success": True, "clearedCount": n, "cleared": [{"defName": "RaidEnemy"}] * n}
        if tool == "jawa/map_info":
            m = self._map()
            t = self.world[m["tile"]]
            return {"success": True, "mapId": self.current, "tile": m["tile"], "sizeX": m.get("size", 250),
                    "sizeZ": m.get("size", 250), "mapBiome": "RM_Grass" if "wrong_biome" in f else m["biome"],
                    "latitude": 40.0 if "high_lat" in f else t["lat"], "longitude": t["long"],
                    "outdoorTempNow": 52.0, "season": "Summer"}
        if tool == "jawa/world_mutators_get":
            ids = [int(x) for x in str(p["tiles"]).split(",")]
            return {"success": True, "count": len(ids), "tiles": [
                {"tile": i, "mutators": (["Caves"] if "mutators" in f else []) + self.world[i]["mutators"],
                 "landmark": self.world[i]["landmark"]} for i in ids]}
        if tool == "jawa/world_mutators_set":
            for i in str(p["tiles"]).split(","):
                self.world[int(i)]["mutators"] = []
            return {"success": True}
        if tool == "jawa/spawn_batch":
            for op in str(p["ops"]).split(";"):
                d, rest = op.split(":")
                x, z, n = [int(v) for v in rest.split(",")]
                if "no_food_land" not in f:
                    self.food.append((x, z, n))
            return {"success": True}
        if tool == "jawa/pawn_need":
            if p["action"] == "need":
                self.needs.setdefault(p["pawn"], {})[p["need"]] = p["level"]
                return {"success": True}
            return {"success": True, "needs": [{"need": k, "level": v} for k, v in self.needs.get(p["pawn"], {}).items()]}
        if tool == "jawa/list_things" and p.get("defName") == "MealSurvivalPack":
            return {"success": True, "isCompleteList": True,
                    "things": [{"def": "MealSurvivalPack", "x": x, "z": z, "stackCount": n} for x, z, n in self.food]}
        if tool == "jawa/list_things":
            return {"success": True, "things": [{"def": "Fire", "x": 10, "z": 10}], "isCompleteList": True}
        if tool == "jawa/get_roof_batch":
            x, z = [int(v) for v in p["rects"].split(",")[:2]]
            return {"success": True, "cellsRead": 1, "roofs": ["RoofRockThin" if (x + z) % 7 == 0 else "None"]}
        if tool == "jawa/cell_temperature":
            x = int(p["cell"].split(",")[0])
            t = 52.0 + (0.5 if x % 2 else -0.5)
            if "hot_spot" in f and x % 5 == 0:
                t = 70.0
            if (x * 3 + int(p["cell"].split(",")[1])) % 11 == 0:      # solid rock: no air, no temperature
                return {"success": True, "ok": False}
            return {"success": True, "ok": True, "temperature": t}
        if tool == "rimworld/get_cell_info":
            return {"success": True, "cell": {"fogged": "fog" in f, "walkable": (p["x"] * 3 + p["z"]) % 11 != 0}}
        if tool == "jawa/world_tile_get":
            ids = [int(x) for x in str(p["tiles"]).split(",")]
            return {"success": True, "tiles": [dict(self.world[i], temperature=(40.0 if "raw_temp" in f else self.world[i]["temperature"])) for i in ids]}
        if tool == "jawa/time_clock":
            return {"success": True, "ticksGame": self.ticks, "ticksAbs": self.ticks + self.abs_off,
                    "paused": "running" not in f and self.paused}
        if tool == "jawa/list_pawns":
            pw = [dict(x) for x in self.pawns]
            if "few" in f:
                pw = pw[:2]
            if "downed" in f:
                pw[0]["downed"] = True
            return {"success": True, "pawns": pw}
        # ---- site recipe
        if tool == "rimworld/get_ui_state":
            return {"success": True, "programState": self.state}
        if tool == "rimworld/go_to_main_menu":
            self.state = "Entry"
            return {"success": True}
        if tool == "rimworld/start_debug_game_ready":
            self.state = "Playing"
            if "start_timeout" in f:
                raise IOError("socket timed out")
            return {"success": True}
        if tool == "rimworld/get_game_info":
            return {"success": True, "ticksGame": self.ticks}
        if tool == "jawa/world_info_get":
            return {"success": True, "info": {"seedString": "fake-seed", "planetCoverage": 0.3}}
        if tool == "jawa/world_tile_export":
            cols = ["tile", "lat", "long", "biome", "elevation", "temperature", "rainfall", "hilliness",
                    "swampiness", "pollution", "tempMin", "tempMax", "seasonalShift", "riverDist", "feature",
                    "featureId", "waterCovered", "roadCount", "riverCount", "mutatorCount"]
            with open(p["path"], "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(cols)
                for t, r in sorted(self.world.items()):
                    w.writerow([t, r["lat"], r["long"], r["biome"], r["elevation"], r["temperature"],
                                r["rainfall"], r["hilliness"], 0, 0, 0, 0, 0, 0, "", -1,
                                "True" if r["waterCovered"] else "False", r["roadCount"], r["riverCount"],
                                len(r["mutators"])])
            return {"success": True, "path": p["path"], "tilesTotal": len(self.world)}
        if tool == "jawa/world_neighbors":
            with open(p["path"], "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["tile", "n0", "n1", "n2", "n3", "n4", "n5"])
                for t in sorted(self.world):
                    nb = hex_nbrs(t)
                    w.writerow([t] + nb + [-1] * (6 - len(nb)))
            return {"success": True, "path": p["path"]}
        if tool == "jawa/world_tile_set":
            ids = [int(x) for x in str(p["tiles"]).split(",")]
            for i in ids:
                r = self.world[i]
                r.update(biome=p["biome"], temperature=float(p["temperature"]), rainfall=p["rainfall"],
                         elevation=p["elevation"], hilliness=p["hilliness"])
            return {"success": True, "written": len(ids), "tiles": [dict(self.world[i]) for i in ids]}
        if tool == "jawa/world_commit":
            return {"success": True, "steps": [{"step": "redraw", "status": "ok"}]}
        if tool == "jawa/colony_found":
            return {"success": True, "tile": p.get("tile")}
        if tool == "jawa/world_tile_map_generate":
            if "mapgen_fail" in f:
                return {"success": True, "wasAlreadyGenerated": False, "mapSize": {"x": 250, "z": 250},
                        "mapFinalize": {"failedSteps": ["GenStep_Animals"]}, "mapId": 9}
            mid = 1 + max(self.maps)
            self.maps[mid] = {"tile": p["tile"], "biome": self.world[p["tile"]]["biome"], "size": p["sizeX"]}
            self.site = p["tile"]
            return {"success": True, "wasAlreadyGenerated": False, "mapSize": {"x": p["sizeX"], "z": p["sizeZ"]},
                    "mapFinalize": {"failedSteps": [], "steps": []}, "mapId": mid, "mapIndex": 1,
                    "pawnCount": 40, "thingCount": 9000}
        if tool == "jawa/set_current_map":
            if p["mapId"] not in self.maps:
                return {"success": False, "message": "no map %s" % p["mapId"]}
            prev, self.current = self.current, p["mapId"]
            return {"success": True, "mapId": self.current, "previousMapId": prev}
        if tool == "jawa/spawn_pawn":
            ids = ["S%d" % i for i in range(p["count"])]
            return {"success": True, "pawns": [{"id": i} for i in ids]}
        if tool == "jawa/set_fog":
            return {"success": True, "foggedCellsBefore": 9000, "foggedCellsNow": 0}
        if tool == "jawa/time_date_at":
            # Summer = quadrum index 1 of each year (quadrum = 900000 ticks) for the north.
            q = (int(p["ticksAbs"]) // 900000) % 4
            return {"success": True, "season": "Summer" if q == 1 else "Spring"}
        if tool == "jawa/time_set_ticks":
            self.ticks = int(p["ticks"])
            return {"success": True, "ticksGameAfter": self.ticks}
        if tool == "rimworld/save_game":
            if "save_wrong_slot" in f:
                victim = sorted(x for x in os.listdir(self.saves_dir) if x.endswith(".rws"))[0]
                with open(os.path.join(self.saves_dir, victim), "ab") as fh:
                    fh.write(b"clobbered")
            with open(os.path.join(self.saves_dir, p["saveName"] + ".rws"), "wb") as fh:
                fh.write(b"<savegame/>")
            self.saved_named = self.named
            return {"success": True}
        if tool == "rimworld/load_game":
            self.state = "Playing"
            # MEASURED 2026-10-11: the reloaded pilot fixture came up on the quicktest colony (tile 52347)
            self.current = 1 if "load_on_colony" in f else max(self.maps)
            if self.saved_named is not None:
                self.named = self.saved_named
            return {"success": True}
        raise RuntimeError("fake: unknown tool %s" % tool)


# ------------------------------------------------------------------ fake environment

class FakeEnv(P.Env):
    def __init__(self, tmp, manifest, faults=()):
        self.faults = set(faults)
        self.root = os.path.join(tmp, "repo")
        self.mods_dir = os.path.join(tmp, "Mods")
        self.config_dir = os.path.join(tmp, "Config")
        self.player_log = os.path.join(tmp, "Player.log")
        self.saves_dir = os.path.join(tmp, "Saves")
        self.python = sys.executable
        self._manifest = manifest
        self.dll_shas = {}
        for d in (self.config_dir, self.saves_dir):
            os.makedirs(d, exist_ok=True)
        for repo_dll, dep_rel, _pid in P.DLLS:
            body = ("dll:" + repo_dll).encode()
            stamp = b"# project: x.csproj\n# dll: abc\n"
            for base, rel in ((self.root, repo_dll), (self.mods_dir, dep_rel)):
                path = os.path.join(base, rel)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as fh:
                    fh.write(body)
                with open(path + ".srchash", "wb") as fh:
                    fh.write(stamp + (b"drift" if ("stamp_drift" in self.faults and base == self.mods_dir) else b""))
            self.dll_shas[os.path.basename(repo_dll)[:-4]] = hashlib.sha256(body).hexdigest()
        for d in P.DEPLOYED_DIRS:
            os.makedirs(os.path.join(self.mods_dir, d), exist_ok=True)
            with open(os.path.join(self.mods_dir, d, "About.xml"), "w") as fh:
                fh.write("<x/>")
        log = ["RimWorld 1.6"]
        log += ["Config error in RM_FE_Ground_Sand: burnedDef is flammable"] * (1 if "log_burn5" in self.faults else 0)
        if "log_nre" in self.faults:
            log.append("Exception in GenStep_Animals: NullReferenceException at CommonalityOfAnimal")
        if "log_xref" in self.faults:
            log.append("Could not resolve cross-reference to Verse.PawnKindDef named RSW_Gizka")
        with open(self.player_log, "w") as fh:
            fh.write("\n".join(log) + "\n")
        with open(os.path.join(self.config_dir, "Mod_123_RM_PyrelandsMod.xml"), "w") as fh:
            fh.write("<SettingsBlock><ModSettings><fulguriteEnabled>True</fulguriteEnabled></ModSettings></SettingsBlock>")
        biome_off = "<li><key>Pyrelands</key><value>False</value></li>" if "biome_off" in self.faults else ""
        with open(os.path.join(self.config_dir, "Mod_456_RM_BiomesMod.xml"), "w") as fh:
            fh.write("<SettingsBlock><ModSettings><enabled>%s<li><key>Warscar</key><value>True</value></li>"
                     "</enabled></ModSettings></SettingsBlock>" % biome_off)
        self._born = 2000.0 if "deploy_after_launch" not in self.faults else 500.0
        for dp, _dn, fn in os.walk(self.mods_dir):
            for x in fn:
                os.utime(os.path.join(dp, x), (1000.0, 1000.0))

    def run(self, argv, timeout=600):
        a = " ".join(str(x) for x in argv)
        if "bridge who" in a:
            other = "FOUNDRY" if P.SEAT == "BENCH" else "BENCH"
            return 0, "bridge held by %s since 2026-10-01T15:26:45Z" % (other if "other_seat" in self.faults else P.SEAT)
        if "bridge release" in a:
            return 0, "released"
        if "deploy_custom_mods.py" in a:
            if "deploy_drift" in self.faults and "biomes" in a:
                return 1, "RimMandrake.Biomes mandrake.rm.biomes\n    ~  Biomes/Pyrelands/Defs/x.xml\n"
            return 0, "UtinniPatches mandrake.rut.patches\n    in sync (40 files)\n"
        if "modset_builder.py" in a:
            return 0, "restored"
        raise RuntimeError("fake env: unexpected command %s" % a)

    def manifest(self):
        return list(self._manifest), [], []

    def stamp_status(self, repo_dll):
        if "src_drift" in self.faults and "PyrelandsMechanics" in repo_dll:
            return "MISMATCH", ["Foo.cs: hash in stamp does not match committed source"]
        return "MATCH", []

    def loadavg(self):
        return {"load_high": 12.0, "load_unknown": None}.get(
            next((x for x in self.faults if x.startswith("load_")), ""), 1.5)

    def run_wsl(self, argv, timeout=600):
        argv = [a for a in argv if a != "env" and not a.startswith("AGENT_SEAT=")]
        return self.run(["py" if a == "python3" else a for a in argv], timeout)

    def log_birth(self):
        return self._born


MANIFEST = (["brrainz.harmony", "ludeon.rimworld"] + list(P.DLCS) +
            ["brrainz.rimbridgeserver", "sarg.alphabiomes", "mandrake.rm.biomes", "mandrake.rut.patches",
             "mandrake.rsw.swbestiary", "mandrake.rut.pyrelandsmechanics"])


@contextlib.contextmanager
def quiet():
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        yield buf
    finally:
        sys.stdout = old


def run_gate(gate, faults=(), **kw):
    tmp = tempfile.mkdtemp(prefix="pyre_site_")
    try:
        env = FakeEnv(tmp, MANIFEST, faults)
        g = FakeGame(MANIFEST, env.dll_shas, faults, saves_dir=env.saves_dir)
        g.state, g.current = "Playing", 1
        if gate == "A":
            rows, out = P.gate_a(g, env, os.path.join(tmp, "snap"))
        elif gate == "B":
            g.maps[2] = {"tile": tid(15, 15), "biome": P.BIOME, "size": 250}
            g.current = 2
            g.world[tid(15, 15)]["temperature"] = 50.0
            rows, out = P.gate_b(g, env, tile=tid(15, 15), expect_temp=50.0)
        else:
            snap = os.path.join(tmp, "snap")
            P.snapshot_settings(env, snap)
            with open(os.path.join(env.config_dir, "Mod_123_RM_PyrelandsMod.xml"), "a") as fh:
                fh.write("<!-- edited by a toggle -->")
            g.settings["burnLineEnabled"] = "False"
            rows, out = P.gate_c(g, env, snap, "Cassandra", restore_tier=kw.get("restore_tier", False))
        return rows_by_id(rows), rows, out, g, env
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------ tests

def test_tier():
    t = mb.TIERS.get("pyrelands")
    check("tier pyrelands exists", t is not None)
    if not t:
        return
    check("tier dlc True (owner 2026-09-19)", t["dlc"] is True)
    check("tier want = plan 3.1", set(t["want"]) == {mb.BRIDGE, "mandrake.rm.biomes", "mandrake.rut.patches",
                                                    "mandrake.rsw.swbestiary", "mandrake.rut.pyrelandsmechanics"})
    ex = set(t["forbid"])
    check("tier excludes transitions/mapdesigner/BCP", {"m00nl1ght.geologicallandforms",
          "m00nl1ght.geologicallandforms.biometransitions", "zylle.mapdesigner",
          "kopp.biomecompatibilityproject"} <= ex)
    check("alphabiomes NOT excluded (hard dep of mandrake.rm.biomes)", "sarg.alphabiomes" not in ex)

    def rec(pid, deps=()):
        return {"packageId": pid, "name": pid, "deps": list(deps), "after": [], "before": []}
    inst = {p: rec(p) for p in ["ludeon.rimworld", "brrainz.harmony", mb.BRIDGE, "mandrake.rut.patches",
                                "mandrake.rsw.swbestiary", "mandrake.rut.pyrelandsmechanics", "sarg.alphabiomes"]
            + list(P.DLCS)}
    inst["mandrake.rm.biomes"] = rec("mandrake.rm.biomes", ["sarg.alphabiomes"])
    ordered, missing, banned = mb.resolve_tier("pyrelands", inst)
    check("resolve_tier clean: nothing missing/banned", not missing and not banned, (missing, banned))
    check("resolve_tier carries all 5 DLCs", all(d in ordered for d in P.DLCS))
    inst["zylle.mapdesigner"] = rec("zylle.mapdesigner")
    inst["mandrake.rut.patches"] = rec("mandrake.rut.patches", ["zylle.mapdesigner"])
    _o, _m, banned = mb.resolve_tier("pyrelands", inst)
    check("resolve_tier refuses a forbidden mod pulled in by closure", any("zylle.mapdesigner" in r for r in banned), banned)
    # main() must refuse too (plan-only, no ModsConfig write): patch scan + --tier
    old_scan = mb.scan
    mb.scan = lambda: inst
    try:
        with quiet() as buf:
            old_argv = sys.argv
            sys.argv = ["modset_builder.py", "--tier", "pyrelands"]
            try:
                rc = mb.main()
            finally:
                sys.argv = old_argv
        check("modset_builder --tier pyrelands (plan) refuses a banned closure", rc == 1 and "REFUSING" in buf.getvalue(),
              buf.getvalue()[-300:])
    finally:
        mb.scan = old_scan


def test_manifests_match_suite():
    sys.path.insert(0, UTILS)
    spec = importlib.util.spec_from_file_location("pyre_validation", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    check("PLANTS == validation.PLANT_MANIFEST", set(P.PLANTS) == set(v.PLANT_MANIFEST))
    check("ANIMALS == validation.ANIMAL_MANIFEST (16)", set(P.ANIMALS) == set(v.ANIMAL_MANIFEST) and len(P.ANIMALS) == 16)
    check("site isolation == validation ISOLATION_OFF", set(v.ISOLATION_OFF) <= set(S.ISOLATION_OFF),
          (sorted(v.ISOLATION_OFF), sorted(S.ISOLATION_OFF)))
    check("SETTINGS type == validation SETTINGS", P.SETTINGS == v.SETTINGS)
    cs = open(os.path.join(HERE, "Source", "PyrelandsTuning.cs"), encoding="utf-8").read()
    q = re.search(r"StandingBurnQuietTicks\s*=\s*([\d_]+)", cs)
    w = re.search(r"BurnWatchIntervalTicks\s*=\s*([\d_]+)", cs)
    check("burn_line arm constants == PyrelandsTuning (quiet/watch)",
          bool(q and w) and int(q.group(1).replace("_", "")) == v.BURN_QUIET_TICKS
          and int(w.group(1).replace("_", "")) == v.BURN_WATCH_TICKS and v.BURN_LINE_WAIT_TICKS > v.BURN_QUIET_TICKS)
    check("burn_line chain is registered and skipped in the main split",
          any(getattr(c, "name", c) == "burn_line" or "burn_line" in str(c) for c in getattr(v.suite, "chains", [])) or "burn_line" in open(os.path.join(HERE, "validation.py"), encoding="utf-8").read(),
          "")
    check("northstar_plan main split skips burn_line",
          "--skip-chains embergrass_regrow,burn_line" in open(os.path.join(HERE, "northstar_plan.py"), encoding="utf-8").read())


def test_defaults_match_source():
    src = open(os.path.join(HERE, "Source", "RM_PyrelandsMod.cs"), encoding="utf-8").read()
    tun = open(os.path.join(HERE, "Source", "PyrelandsTuning.cs"), encoding="utf-8").read()
    block = src[src.index("class RM_PyrelandsSettings"):src.index("public override void ExposeData")]
    found = {}
    for m in re.finditer(r"public static (bool|int|float|string) (\w+) = ([^;]+);", block):
        typ, name, val = m.groups()
        val = val.strip()
        cm = re.match(r"PyrelandsTuning\.(\w+)", val)
        if cm:
            val = re.search(r"const \w+ %s = ([^;]+);" % cm.group(1), tun).group(1)
        val = val.rstrip("f").strip('"')
        found[name] = (val == "true") if typ == "bool" else (val if typ == "string" else float(val))
    check("DEFAULTS covers every static settings field", set(found) == set(P.DEFAULTS),
          sorted(set(found) ^ set(P.DEFAULTS)))
    diff = {k: (found[k], P.DEFAULTS[k]) for k in found if k in P.DEFAULTS
            and P._norm_val(found[k]) != P._norm_val(P.DEFAULTS[k])}
    check("DEFAULTS values == C# initialisers", not diff, diff)


def test_gate_a():
    by, rows, out, g, _env = run_gate("A")
    check("gate A clean: every row PASS", all(r.status == P.PASS for r in rows), [(r.id, r.status, r.observed) for r in rows if r.status != P.PASS])
    check("gate A clean: verdict ok", P.verdict(rows)[0])
    check("gate A records a def fingerprint", bool(out.get("def_fingerprint")))
    check("gate A records storyteller for gate C", out.get("storyteller_before") == "Tutor")
    for fault, rid, want in (("other_seat", "3.8.1", P.FAIL), ("deploy_after_launch", "3.8.2", P.FAIL),
                             ("extra_mod", "3.8.3", P.FAIL), ("no_odyssey", "3.8.3", P.FAIL),
                             ("reorder", "3.8.3", P.FAIL), ("deploy_drift", "3.2.1", P.FAIL),
                             ("stamp_drift", "3.8.4", P.FAIL), ("src_drift", "3.8.4", P.FAIL),
                             ("dll_twice", "3.2.3", P.FAIL), ("dll_drift", "3.2.3", P.FAIL),
                             ("defs_missing", "3.8.5", P.FAIL), ("defs_fail", "3.8.5", P.UNMEASURED),
                             ("setting_off", "3.3", P.FAIL), ("biome_off", "3.3", P.FAIL),
                             ("log_nre", "3.8.7", P.FAIL), ("log_xref", "3.8.7", P.FAIL),
                             ("log_burn5", "3.8.7", P.FAIL), ("load_high", "3.8.12", P.FAIL),
                             ("load_unknown", "3.8.12", P.UNMEASURED), ("modal", "3.8.dialogs", P.FAIL)):
        by, rows, _o, _g, _e = run_gate("A", [fault])
        ok, bad = P.verdict(rows)
        check("gate A %-19s -> %s %s, run refused" % (fault, rid, want),
              by[rid].status == want and not ok and rid in [r.id for r in bad], (by[rid].status, by[rid].observed))
        others = [r.id for r in rows if r.status != P.PASS and r.id != rid]
        check("gate A %-19s -> no collateral rows" % fault, not others, others)
    by, rows, _o, g, _e = run_gate("A", ["logwin"])
    check("benign log window is closed, not refused", by["3.8.dialogs"].status == P.PASS and not g.windows)
    by, rows, _o, _g, _e = run_gate("A", ["extra_mod", "log_nre", "other_seat"])
    bad_ids = sorted(r.id for r in P.verdict(rows)[1])
    check("gate A reports ALL failures together (GPT #20)", bad_ids == ["3.8.1", "3.8.3", "3.8.7"], bad_ids)
    g2 = FakeGame(MANIFEST, {}, ())
    g2.tools.discard("jawa/running_mods")
    tmp = tempfile.mkdtemp()
    try:
        env = FakeEnv(tmp, MANIFEST)
        r = P.a_loaded_assemblies(g2, env)
        check("missing bridge tool -> UNMEASURED, never PASS", r.status == P.UNMEASURED, r.observed)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_gate_b():
    by, rows, out, g, _e = run_gate("B")
    check("gate B clean: every row PASS", all(r.status == P.PASS for r in rows), [(r.id, r.status, r.observed) for r in rows if r.status != P.PASS])
    check("gate B sampled >= 20 unroofed cells", len(out["site"]["temps"]) >= 20)
    temp_cells = [c[1]["cell"] for c in g.calls if c[0] == "jawa/cell_temperature"]
    roofed = [c for c in temp_cells if sum(int(v) for v in c.split(",")) % 7 == 0]
    check("gate B never samples a roofed cell", temp_cells and not roofed, roofed)
    burn = P.sample_cells((250, 250), 60, out["site"]["tile"], avoid={(10, 10)})
    check("gate B cell sampler honours the burning-cell avoid set", (10, 10) not in burn)
    for fault, rid in (("wrong_biome", "3.8.8"), ("mutators", "3.8.8"), ("high_lat", "3.8.8"),
                       ("raw_temp", "3.8.8"), ("hot_spot", "3.8.8"), ("fog", "3.8.8"),
                       ("rain", "3.8.9"), ("running", "3.8.9"), ("loud", "3.8.10"), ("queue", "3.8.10"),
                       ("few", "3.8.11"), ("downed", "3.8.11"), ("modal", "3.8.dialogs-B")):
        by, rows, _o, _g, _e = run_gate("B", [fault])
        check("gate B %-12s -> %s FAIL, run refused" % (fault, rid),
              by[rid].status == P.FAIL and not P.verdict(rows)[0], (by[rid].status, by[rid].observed))


def test_gate_c():
    by, rows, _o, g, _e = run_gate("C")
    check("gate C settings files restored byte-exact", by["C.settings_files"].status == P.PASS, by["C.settings_files"].observed)
    check("gate C in-memory toggle drift is set back", by["C.settings_defaults"].status == P.PASS
          and g.settings["burnLineEnabled"] == "true", g.settings["burnLineEnabled"])
    check("gate C storyteller restored", by["C.storyteller_restored"].status == P.PASS and g.storyteller == "Cassandra")
    check("gate C bridge release attempted", by["C.bridge_released"].status in (P.PASS, P.FAIL))
    check("gate C without --restore-tier is UNMEASURED (refuses)", by["C.tier_restored"].status == P.UNMEASURED)


def test_site_pure():
    rows = world_rows()
    nbrs = {t: hex_nbrs(t) for t in rows}
    tmp = tempfile.mkdtemp()
    try:
        p = os.path.join(tmp, "n.csv")
        with open(p, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["tile", "n0", "n1", "n2", "n3", "n4", "n5"])
            w.writerow([0, 1, 40, -1, -1, -1, -1])
        check("neighbour csv drops -1 padding", S.read_neighbor_csv(p) == {0: [1, 40]})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    colony = tid(35, 15)
    cands = list(S.site_candidates(rows, nbrs, colony))
    check("site candidates exist", bool(cands))
    first, patch = cands[0]
    d = S.distances_from(nbrs, colony, 50)
    check("candidate centre |lat| <= 25", all(abs(rows[c]["lat"]) <= 25 for c, _ in cands))
    check("candidate >= 10 steps from colony", all(d.get(c, 99) >= 10 for c, _ in cands))
    check("candidate patch: no water/river/road", all(not rows[t]["waterCovered"] and rows[t]["riverCount"] == 0
                                                      for _c, pt in cands for t in pt))
    check("candidate patch is 2 rings (19 interior)", len(patch) == 19, len(patch))
    check("candidate order is deterministic (|lat|, id)", cands[0][0] == sorted(
        (c for c, _ in cands), key=lambda c: (abs(rows[c]["lat"]), c))[0])
    # midsummer noon: forward, Summer, local noon
    clk = {"ticksGame": 5000, "ticksAbs": 5000 + 10 * 900000}
    tgt = S.midsummer_noon_ticks(clk, 0.0, 45.0,
                                 lambda ta: "Summer" if (ta // 900000) % 4 == 1 else "Spring")
    ta = tgt + 10 * 900000
    check("midsummer: forward in time", tgt > 5000)
    check("midsummer: lands in a Summer quadrum", (ta // 900000) % 4 == 1)
    check("midsummer: local noon at lon 45 (tz +3h)", ((ta + 3 * 2500) % 60000) == 12 * 2500)


def run_site(faults=(), pre_saves=("CANONICAL_ASHKARR_START_2026-09-12.rws",)):
    tmp = tempfile.mkdtemp(prefix="pyre_build_")
    env = FakeEnv(tmp, MANIFEST)
    for n in pre_saves:
        with open(os.path.join(env.saves_dir, n), "wb") as fh:
            fh.write(b"keep me")
    g = FakeGame(MANIFEST, env.dll_shas, faults, saves_dir=env.saves_dir)
    g.state = "Playing"
    err, rec = None, None
    censused = []
    try:
        with quiet():
            rec = S.build_site(g, 1, "abcdef1234567890", env.saves_dir, os.path.join(tmp, "work"),
                               census=lambda s, r: censused.append(s.call("jawa/time_clock")["ticksGame"]) or {"n": 1},
                               sleep=lambda _s: None)
    except Exception as ex:
        err = ex
    return rec, err, g, env, tmp, censused


def test_site_build():
    rec, err, g, env, tmp, censused = run_site()
    try:
        check("build_site runs end to end on the fake", err is None, repr(err))
        if err:
            return
        tile = rec["pick"]["centre"]
        check("fresh world: went to menu then quicktest", [c[0] for c in g.calls[:3]] ==
              ["rimworld/get_ui_state", "rimworld/go_to_main_menu", "rimworld/get_ui_state"])
        check("seedString recorded, never chosen", rec["world"]["seedString"] == "fake-seed" and
              not any("seed" in json.dumps(c[1]).lower() for c in g.calls if c[0] == "rimworld/start_debug_game_ready"))
        check("patch re-tiled to RM_Pyrelands at 50", all(g.world[t]["biome"] == P.BIOME and g.world[t]["temperature"] == 50.0
                                                         for t in rec["pick"]["patch"]))
        check("only the patch was re-tiled (19 tiles)", sum(1 for r in g.world.values() if r["biome"] == P.BIOME) == 19)
        tset = [i for i, c in enumerate(g.calls) if c[0] == "jawa/world_tile_set"][0]
        reads = [i for i, c in enumerate(g.calls) if c[0] in ("jawa/map_info", "jawa/cell_temperature", "jawa/world_tile_get")
                 and i < tset and str(tile) in json.dumps(c[1])]
        check("temperature written before anything reads the site tile", not reads, reads)
        gen = [i for i, c in enumerate(g.calls) if c[0] == "jawa/world_tile_map_generate"][0]
        off_before_gen = [c for c in g.calls[:gen] if c[0] == "jawa/mod_settings_field" and c[1]["action"] == "set"]
        check("all 7 fire/migration toggles OFF before mapgen", len(off_before_gen) == len(S.ISOLATION_OFF))
        clr = [i for i, c in enumerate(g.calls) if c[0] == "jawa/world_mutators_set" and c[1]["action"] == "clear"]
        check("mutators cleared before mapgen", clr and clr[0] < gen)
        check("census ran at the gen tick (before time moved)", censused == [rec["tickAtGen"]], (censused, rec["tickAtGen"]))
        check("toggles restored to shipped defaults", all(P._norm_val(g.settings[f]) is True for f in S.ISOLATION_OFF))
        names = sorted(os.listdir(env.saves_dir))
        check("fixture saved under NS_Pyrelands_site_1_<fp12>", "NS_Pyrelands_site_1_abcdef123456.rws" in names, names)
        check("existing save untouched", open(os.path.join(env.saves_dir, "CANONICAL_ASHKARR_START_2026-09-12.rws"), "rb").read() == b"keep me")
        check("Saves backed up before saving", os.path.isfile(os.path.join(tmp, "work", "saves_backup_1",
                                                                      "CANONICAL_ASHKARR_START_2026-09-12.rws")))
        check("reloaded via load_game, current map is the site", rec["reload"]["tile"] == tile
              and any(c[0] == "rimworld/load_game" for c in g.calls))
        check("no load_game_ready used as a load", not any(c[0] == "rimworld/load_game_ready" for c in g.calls))
        check("never unfogAll", not any(c[0] == "jawa/set_fog" and c[1].get("action") == "unfogAll" for c in g.calls))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec, err, g, env, tmp, _c = run_site(["mapgen_fail"])
    try:
        check("mapgen failed step -> SiteError", isinstance(err, S.SiteError), repr(err))
        check("toggles restored even when mapgen fails (finally)",
              all(P._norm_val(g.settings[f]) is True for f in S.ISOLATION_OFF))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec, err, g, env, tmp, _c = run_site(["save_wrong_slot"])
    try:
        check("save touching another slot -> SiteError", isinstance(err, S.SiteError) and "touched" in str(err), repr(err))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec, err, g, env, tmp, _c = run_site(pre_saves=("CANONICAL_ASHKARR_START_2026-09-12.rws",
                                                    "NS_Pyrelands_site_1_abcdef123456.rws"))
    try:
        check("existing fixture name is never overwritten", isinstance(err, S.SiteError) and "never overwritten" in str(err), repr(err))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec, err, g, env, tmp, _c = run_site(["start_timeout"])
    try:
        n = sum(1 for c in g.calls if c[0] == "rimworld/start_debug_game_ready")
        check("quicktest timeout: polled, never resent", err is None and n == 1, (repr(err), n))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _fixture_game(faults=()):
    """A fake mid-reload: quicktest colony map 1 + the Pyrelands site map 2, saved UNNAMED (the 2026-10-11 pilot
    fixture), game Playing on the colony map."""
    tmp = tempfile.mkdtemp(prefix="pyre_reload_")
    env = FakeEnv(tmp, MANIFEST)
    g = FakeGame(MANIFEST, env.dll_shas, faults, saves_dir=env.saves_dir)
    site = tid(15, 15)
    g.world[site]["biome"] = P.BIOME
    g.maps[2] = {"tile": site, "biome": P.BIOME, "size": 250}
    g.state, g.current, g.saved_named, g.ticks = "Playing", 1, False, 424800
    return g, site, tmp


def test_naming_dialog_lesson():
    """2026-10-11 pilot: an unnamed colony raised the naming dialog at TicksGame % 1000 == 200, which hopped the
    current map to the quicktest colony; the reload crashed before its settle step and gate B refused."""
    g, site, tmp = _fixture_game()
    try:
        g.current = 2
        g.call("rimworld/step_game_ticks", ticks=600)
        check("fake models the hop: unnamed + crossing NNN200 -> colony map current",
              g.current == 1 and any("NamePlayer" in w["type"] for w in g.windows), (g.current, g.windows))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for faults in ((), ("load_on_colony",)):
        g, site, tmp = _fixture_game(faults)
        try:
            with quiet():
                mi = S.reload_fixture(g, "NS_Pyrelands_site_1_abcdef123456", site, sleep=lambda _s: None, map_id=None)
            names = [i for i, c in enumerate(g.calls) if c[0] == "jawa/name_colony"]
            steps = [i for i, c in enumerate(g.calls) if c[0] == "rimworld/step_game_ticks"]
            check("reload %s: lands on the site after the settle ticks" % (faults or "plain",),
                  mi.get("tile") == site and mi.get("mapBiome") == P.BIOME, mi)
            check("reload %s: name_colony runs before any tick" % (faults or "plain",),
                  names and steps and names[0] < steps[0], (names, steps))
            check("reload %s: settle runs %d ticks, queue cleared before AND after" % (faults or "plain", S.SETTLE_TICKS),
                  sum(c[1]["ticks"] for c in g.calls if c[0] == "rimworld/step_game_ticks") == S.SETTLE_TICKS
                  and g.queue_clears >= 2, g.queue_clears)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    g, site, tmp = _fixture_game(("name_refused",))
    try:
        err = None
        try:
            with quiet():
                S.reload_fixture(g, "x", site, sleep=lambda _s: None, map_id=2)
        except Exception as ex:
            err = ex
        check("name_colony that names no site settlement -> SiteError (never ticks unnamed)",
              isinstance(err, S.SiteError) and not any(c[0] == "rimworld/step_game_ticks" for c in g.calls), repr(err))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec, err, g, env, tmp, _c = run_site()
    try:
        nm = [i for i, c in enumerate(g.calls) if c[0] == "jawa/name_colony"]
        sv = [i for i, c in enumerate(g.calls) if c[0] == "rimworld/save_game"]
        check("build_site names the colony before saving the fixture", err is None and nm and sv and nm[0] < sv[0],
              (repr(err), nm, sv))
        check("the saved fixture is named (a reload raises no dialog)", g.saved_named is True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_plan_refuses_on_gate_b():
    """The suite must never run on a site gate B refused (2026-10-11 pilot ran NOT GREEN on one)."""
    spec = importlib.util.spec_from_file_location("pyre_plan", os.path.join(HERE, "northstar_plan.py"))
    plan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plan)
    check("plan exposes preflight(s) for cli.py's site hook", callable(getattr(plan, "preflight", None)))
    for faults, rid in (((), None), (("hot_spot",), "3.8.8"), (("queue",), "3.8.10"), (("modal",), "3.8.dialogs-B")):
        tmp = tempfile.mkdtemp(prefix="pyre_plan_")
        try:
            env = FakeEnv(tmp, MANIFEST)
            g = FakeGame(MANIFEST, env.dll_shas, faults, saves_dir=env.saves_dir)
            g.maps[2] = {"tile": tid(15, 15), "biome": P.BIOME, "size": 250}
            g.world[tid(15, 15)]["temperature"] = 50.0
            g.state, g.current = "Playing", 2
            msgs = plan.preflight(g)
            if rid is None:
                check("plan preflight: clean site -> no refusal", msgs == [], msgs)
            else:
                check("plan preflight: %s -> refusal naming %s" % (faults[0], rid),
                      any(m.startswith("gateB %s:" % rid) for m in msgs), msgs)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


def test_suite_reads_no_genstep_as_a_thing():
    """A GenStepDef defName passed to list_things matches nothing, forever: ruins_scorched read UNMEASURED on every
    site by construction (2026-10-11) because it listed things named RM_FE_ScorchRuins, a GenStepDef."""
    gensteps = set()
    for f in glob.glob(os.path.join(HERE, "Defs", "GenStepDefs", "*.xml")):
        gensteps |= set(re.findall(r"<defName>([^<]+)</defName>", open(f, encoding="utf-8").read()))
    check("Pyrelands GenStepDefs found (the instrument can see)", "RM_FE_ScorchRuins" in gensteps, gensteps)
    src = open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()
    used = set(re.findall(r'(?:_things|_count|_ids_on_map)\(t, "([^"]+)"', src))
    used |= set(re.findall(r'list_things", defName="([^"]+)"', src))
    check("validation.py thing reads were found (the instrument can see)", "RM_FE_Filth_LooseAsh" in used, used)
    check("no thing read names a GenStepDef", not (used & gensteps), used & gensteps)


def test_suite_wait_names_colony_and_reasserts_site():
    """validation._wait: names the colony once, and re-asserts the site after a SHORT wait too."""
    sys.path.insert(0, UTILS)
    spec = importlib.util.spec_from_file_location("pyre_validation_w", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    v._GEN.clear()

    class _S(object):
        def __init__(self):
            self.calls, self.cur = [], 1

        def call(self, tool, **p):
            self.calls.append(tool)
            if tool == "jawa/map_info":
                return {"mapId": self.cur, "mapBiome": "RM_Pyrelands" if self.cur == 2 else "RM_TheRot"}
            if tool == "jawa/set_current_map":
                self.cur = p["mapId"]
            if tool == "jawa/name_colony":
                return {"success": True, "settlements": [{"tile": 5}]}
            return {"success": True}

    class _T(object):
        upstream_failed, watch = False, None

        def __init__(self):
            self.session, self.rec = _S(), []

        def wait_ticks(self, n):
            self.session.cur = 1          # the hop the naming dialog made mid-wait
            return n

        def _record(self, *a):
            self.rec.append(a)

    t = _T()
    v._GEN["site_map"] = 2
    t.session.cur = 2
    v._wait(t, 100)
    v._wait(t, 100)
    check("short _wait re-asserts the site after the ticks", t.session.cur == 2, t.session.calls)
    check("name_colony called exactly once per run", t.session.calls.count("jawa/name_colony") == 1, t.session.calls)


def _load_validation(name):
    sys.path.insert(0, UTILS)
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    return v


def test_harness_fixes_2026_10_12():
    """The 2026-10-12 triage: animal manifest via biome_probe, a refused ignition names its fuel, the spoil wait
    stops once the stack is gone, and both sealed-room rows build rooms with no door."""
    v = _load_validation("pyre_validation_h")
    man = sorted(v.ANIMAL_MANIFEST)
    ok = {"success": True, "biomes": [{"defName": "RM_Pyrelands", "wildAnimalCount": len(man),
                                       "animals": [{"defName": a, "commonality": 0.1} for a in man]}]}
    got, why = v.biome_probe_animals(ok, "RM_Pyrelands")
    check("biome_probe_animals reads the resolved roster", got is not None and set(got) == set(man), why)
    capped = {"success": True, "biomes": [dict(ok["biomes"][0], wildAnimalCount=len(man) + 3)]}
    check("a capped biome_probe list is UNREADABLE, never a short roster",
          v.biome_probe_animals(capped, "RM_Pyrelands")[0] is None)
    check("a refused biome_probe is unreadable", v.biome_probe_animals({"success": False}, "RM_Pyrelands")[0] is None)
    check("a missing biome row is unreadable", v.biome_probe_animals({"success": True, "biomes": []}, "RM_Pyrelands")[0] is None)

    lp = {"rect": "50,180,20,20", "reply": {"planted": 0, "rejected": 400, "rejectionReasons": {"impassable": 400}}}
    msg = v.fire_refusal("50,180,20,20", {"firesStarted": 0}, lp, {"Plant": {}})
    check("a refused ignition quotes this rect's planting", "rejected" in msg and "impassable" in msg, msg)
    msg2 = v.fire_refusal("1,1,2,2", {"firesStarted": 0}, lp, {})
    check("another rect's planting is never quoted as this one's", "none recorded for this rect" in msg2, msg2)

    # 2026-10-12 fixes: probe species, per-attempt ignition log, regrow burn precondition
    check("probe plant is a roster plant, never Plant_Grass",
          v.probe_plant(["RM_FE_Plant_Quickgrass", "RM_FE_Plant_EmberGrass", "Plant_Grass"]) == "RM_FE_Plant_EmberGrass")
    check("probe plant ignores keys outside the allowlist", v.probe_plant(["Plant_Grass"]) is None)
    check("probe plant with no live keys is None", v.probe_plant(None) is None)
    check("probe host is another standing roster def",
          v.probe_host("RM_FE_Plant_EmberGrass", {"RM_FE_Plant_EmberGrass": 5, "RM_FE_Plant_Quickgrass": 3,
                                                  "Plant_Grass": 9}) == "RM_FE_Plant_Quickgrass")
    check("regrow burn outlasts EmberGrass (~4500) and stops before the 7500-tick floor burn",
          4500 <= v.REGROW_BURN_TICKS < 7500)
    check("probe host is None when only the probe's own def stands",
          v.probe_host("RM_FE_Plant_EmberGrass", {"RM_FE_Plant_EmberGrass": 5}) is None)
    h = [v.ignition_record("1,1,2,2", {"firesStarted": 4, "success": True}, None),
         v.ignition_record("1,1,2,2", {"firesStarted": 0, "message": "no fuel"}, lp)]
    check("ignition_record keeps the fire reply per attempt", h[0]["fire"]["firesStarted"] == 4 and
          h[1]["fire"]["message"] == "no fuel", str(h))
    msg3 = v.fire_refusal("1,1,2,2", {"firesStarted": 0}, None, {}, history=h)
    check("a refusal quotes every earlier attempt in full", "attempts so far (2)" in msg3 and "no fuel" in msg3, msg3)
    ok, txt = v.burn_cleared(256, 256)
    check("burn that left all 256 originals standing is not cleared and says 256", not ok and "256 of 256" in txt, txt)
    check("burn that left 10 of 256 is cleared", v.burn_cleared(256, 10)[0])
    check("burn_cleared with no pre-burn plants is not cleared", not v.burn_cleared(0, 0)[0])
    src_ = open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()
    check("regrow row stops UNMEASURED before waiting when the burn did not clear",
          src_.index("burn_cleared(len(pre_ids)") < src_.index("d0 = new_count()"))

    check("spoil sampling continues while the stack is present",
          not v.spoil_sampling_done([{"day": 0.5, "present": True}, {"day": 1.0, "present": True}]))
    check("spoil sampling stops once the stack vanished before day 3",
          v.spoil_sampling_done([{"day": 0.5, "present": False}]))
    check("a stack gone at day 3+ is the rot verdict's, not an early stop",
          not v.spoil_sampling_done([{"day": 3.0, "present": False}]))

    src = open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()
    rooms = [ln for ln in src.splitlines() if '"jawa/make_empty_room"' in ln]
    sealed = [ln for ln in src.splitlines() if 'doorDef="Wall"' in ln]
    check("spoil room and both furnace rooms are built without a door", len(sealed) >= 2 and
          'stuffDef="Steel", doorDef="Wall")' in src.split("def scorchfruit_spoils")[1].split("def ")[0] and
          'doorDef="Wall"' in src.split("def furnace_room")[1].split("def ")[0], (len(rooms), len(sealed)))
    check("the animal manifest is no longer read through get_defs wildAnimals",
          '"BiomeDef/RM_Pyrelands", "wildAnimals"' not in src)


def test_fixture_tag():
    """A rebuild whose Pyrelands defs did not change needs its own fixture name (save_fixture never overwrites)."""
    a = S.fixture_name(1, "a32c5db7c6f1abcdef", S.TARGET_TEMP)
    b = S.fixture_name(1, "a32c5db7c6f1abcdef", S.TARGET_TEMP, "anima0")
    check("untagged name is unchanged", a == "NS_Pyrelands_site_1_a32c5db7c6f1", a)
    check("tagged name appends the tag", b == "NS_Pyrelands_site_1_a32c5db7c6f1_anima0", b)
    check("control-temp tag order", S.fixture_name(2, "ff" * 8, 30.0, "x1") == "NS_Pyrelands_site_2_t30_ffffffffffff_x1")
    for bad in ("", "a b", "x/y", "..", "anima_0"):
        try:
            S.fixture_name(1, "a32c5db7c6f1", S.TARGET_TEMP, bad)
            check("bad tag %r refused" % bad, False)
        except S.SiteError:
            check("bad tag %r refused" % bad, True)


def test_tick_rate_probe_math():
    sys.path.insert(0, HERE)
    import tick_rate_probe as R
    check("rate: 2000 ticks in 10 s = 200 tps", R.rate(0, 2000, 0.0, 10.0) == 200.0)
    check("rate: a clock that did not move is None, never 0", R.rate(5, 5, 0.0, 10.0) is None)
    check("rate: an unreadable clock is None", R.rate(None, 5, 0.0, 1.0) is None)


def test_probe_skips_rock_and_food_and_clock():
    """PYRE_SITE_TEMP_REPAIR_PROBE_HIT_ROCK, PYRE_SITE_FOOD_REPAIR_COLONY_STARVES, PYRE_SITE_CLOCK_REPAIR_ASH_EXPIRES_FIRST."""
    by, rows, out, g, _e = run_gate("B")
    walk_asked = [c[1] for c in g.calls if c[0] == "rimworld/get_cell_info"]
    rock = [q for q in walk_asked if (q["x"] * 3 + q["z"]) % 11 == 0]
    temp_cells = [tuple(int(v) for v in c[1]["cell"].split(",")) for c in g.calls if c[0] == "jawa/cell_temperature"]
    check("fake world has rock cells the sampler meets (the instrument can see)", rock, len(walk_asked))
    check("temperature is never read on a solid-rock cell", not [c for c in temp_cells if (c[0] * 3 + c[1]) % 11 == 0], temp_cells)
    check("gate B still PASSes with rock in the sample", by["3.8.8"].status == P.PASS, by["3.8.8"].observed)

    # food: pure sizing, covers the longest declared wait, spawn ops well formed
    v = _load_validation("pyre_validation_food")
    src = open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()
    waits = [int(n) for n in re.findall(r"_wait\(t, (\d+)\)", src)]
    chain_regrow = v.REGROW_BURN_TICKS + 7 * S.TICKS_PER_DAY      # embergrass_regrow: 5000 + 3 d + 4 d
    longest = max(waits + [v.BURN_LINE_WAIT_TICKS, chain_regrow])
    check("FOOD_RUN_TICKS covers the longest declared chain", S.FOOD_RUN_TICKS >= longest, (S.FOOD_RUN_TICKS, longest))
    packs = S.food_packs_needed()
    check("food covers 6 colonists x 2 packs x (8 days + 1 spare)", packs == 6 * 2 * 9, packs)
    ops = S.food_ops(25, 125, 125).split(";")
    check("food_ops makes stacks of 10,10,5 along +x", ops == ["MealSurvivalPack:150,125,10", "MealSurvivalPack:151,125,10",
                                                              "MealSurvivalPack:152,125,5"], ops)
    check("food cache is outside the centre pad's clear_area and the burrow pad",
          125 + S.FOOD_CACHE_DX - 0 >= 125 + 20 and 125 + S.FOOD_CACHE_DX + packs // S.FOOD_STACK + 1 < 170)

    rec, err, g, env, tmp, _c = run_site()
    try:
        check("site build stocks the food cache (read back) and tops needs", err is None and rec["food"]["packs"] >= packs
              and rec["food"]["colonists"], (repr(err), rec.get("food")))
        check("colonists' Food need set to 1.0", all(g.needs.get(c, {}).get("Food") == 1.0 for c in rec["food"]["colonists"]))
        calls = [c[0] for c in g.calls]
        check("clock jumps BEFORE mapgen and never after the colonists exist",
              calls.index("jawa/time_set_ticks") < calls.index("jawa/world_tile_map_generate") < calls.index("jawa/spawn_pawn")
              and calls.count("jawa/time_set_ticks") == 1, calls.count("jawa/time_set_ticks"))
        check("the clock set passes timeException=true (safe-advance gate)",
              all(c[1].get("timeException") is True for c in g.calls if c[0] == "jawa/time_set_ticks"))
        check("tickAtGen is the mid-Summer noon tick", rec["tickAtGen"] == rec["ticksGameNoon"], (rec["tickAtGen"], rec["ticksGameNoon"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    rec, err, g, env, tmp, _c = run_site(["no_food_land"])
    try:
        check("a cache that reads back short is a SiteError", isinstance(err, S.SiteError) and "food cache" in str(err), repr(err))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # vitals -> RESTART
    ok = {"a": {"dead": False, "downed": False, "food": 0.9}}
    check("intact colony -> no damage", v.vitals_damage(ok, {"a": {"dead": False, "downed": False, "food": 0.5}}) == [])
    check("death -> damage", "died" in " ".join(v.vitals_damage(ok, {"a": {"dead": True}})))
    check("newly downed -> damage", v.vitals_damage(ok, {"a": {"dead": False, "downed": True, "food": 0.5}}) != [])
    check("starving -> damage", v.vitals_damage(ok, {"a": {"dead": False, "downed": False, "food": 0.0}}) != [])
    check("already-dead colonist is not new damage", v.vitals_damage({"a": {"dead": True}}, {"a": {"dead": True}}) == [])
    check("unreadable food is not damage", v.vitals_damage(ok, {"a": {"dead": False, "downed": False, "food": None}}) == [])

    class _Sess(object):
        def __init__(self, die):
            self.die, self.calls, self.cur = die, [], 2

        def call(self, tool, **q):
            self.calls.append((tool, q))
            if tool == "jawa/map_info":
                return {"mapId": 2, "mapBiome": "RM_Pyrelands"}
            if tool == "jawa/name_colony":
                return {"success": True, "settlements": [{"tile": 5}]}
            if tool == "jawa/list_pawns":
                dead = self.die and any(c[0] == "mark" for c in self.calls)
                return {"success": True, "pawns": [{"id": "a", "dead": bool(dead), "downed": False}]}
            if tool == "jawa/pawn_need" and q["action"] == "list":
                return {"success": True, "needs": [{"need": "Food", "level": 0.1}]}
            return {"success": True}

    class _Comp(object):
        verdict, detail = None, ""

    class _T(object):
        upstream_failed, watch = False, None

        def __init__(self, die):
            self.session, self.components, self.rec, self.die = _Sess(die), [], [], die

        def component(self, name, **kw):
            t = self

            class _Ctx(object):
                def __enter__(s_):
                    return t

                def __exit__(s_, *a):
                    c = _Comp()
                    c.name, c.verdict = name, "PASS"
                    if t.die:
                        t.session.calls.append(("mark", {}))   # the death happens inside the row
                    t.components.append(c)
                    return True
            return _Ctx()

        def _record(self, *a):
            self.rec.append(a)

    v._GEN.clear()
    t = _T(False)
    with v._comp(t, "some_row"):
        pass
    topped = [c for c in t.session.calls if c[0] == "jawa/pawn_need" and c[1].get("action") == "need"]
    check("row start tops a low Food need to 1.0", topped and topped[0][1]["level"] == 1.0, t.session.calls)
    check("intact colony: the row keeps its PASS", t.components[-1].verdict == "PASS", t.components[-1].detail)
    t = _T(False)
    with v._comp(t, "scorchfruit_produces"):
        pass
    check("a needs-measuring row is never topped up", not [c for c in t.session.calls if c[0] == "jawa/pawn_need" and c[1].get("action") == "need"])
    v._GEN.clear()
    t = _T(True)
    with v._comp(t, "some_row"):
        pass
    c = t.components[-1]
    check("a death inside the row -> UNMEASURED RESTART, never FAIL", c.verdict == "UNMEASURED" and "RESTART" in c.detail, (c.verdict, c.detail))
    check("a death ends the chain (reload) and is listed", t.upstream_failed and v._GEN.get("restart") == ["some_row"])
    check("the ruins guard on ticksGame is gone", "RUIN_FILTH_MAX_AGE_TICKS" not in src and "site clock vs loose-ash" not in src)


def test_plan_offline():
    with quiet() as buf:
        rc = S.main(["--plan"])
    check("northstar_site --plan prints the recipe offline", rc == 0 and "world_tile_map_generate" in buf.getvalue())


def main():
    for t in (test_tier, test_manifests_match_suite, test_defaults_match_source, test_gate_a, test_gate_b,
              test_gate_c, test_site_pure, test_site_build, test_naming_dialog_lesson, test_plan_refuses_on_gate_b,
              test_suite_reads_no_genstep_as_a_thing, test_suite_wait_names_colony_and_reasserts_site,
              test_harness_fixes_2026_10_12, test_probe_skips_rock_and_food_and_clock, test_fixture_tag, test_tick_rate_probe_math, test_plan_offline):
        try:
            t()
        except Exception as ex:
            import traceback
            traceback.print_exc()
            check("%s raised" % t.__name__, False, repr(ex))
    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
