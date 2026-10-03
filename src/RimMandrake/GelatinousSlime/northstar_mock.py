"""Mock game behaviour for GelatinousSlime (OFFLINE ONLY). `install()` wraps MockGame.handle so the suite in
validation.py can run to completion under `northstar_driver cli.py run --mock`, and so each check can be
SEEN to go red: set env NS_SLIME_MOCK_BREAK to a comma list of faults and the matching component must FAIL
(selftest_slime_suite.py runs every fault). Never imported by a live run (a live run has no MockGame).

The sim mirrors the shipped C# rules; defs/stages/patch values are read from this mod's own XML, so breaking
the XML breaks the mock the same way it would break the game.

Faults: nodef:<Type/name> notag nodry nolaw2 nostage nodissolve nosmear nosmearsetting noexpose growfast
        nosalve antidote_noop antidote_nocost eat_nocure eat_nofee nomarkedcost noshed noclamp noalert noweather
        noseeker defaultswrong
"""
import os
import random
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SLIME_TERRAINS = {"RM_Slime_Hardened", "RM_Slime_Rich", "RM_Slime_Grass", "RM_Slime_Mud", "RM_Slime_Liquid"}
DEFAULTS = {"rarityFactor": "1", "flavorEntryRecorded": "True", "flavorReadMarks": "True",
            "titanoslimeSpawnFactor": "1", "titanoslimeEngulfs": "True", "titanoslimeGrows": "True",
            "preferHigherPriorityArchive": "True", "titanoslimeReversible": "False",
            "titanoslimeMaxStage": "5", "titanoslimeSheds": "True",
            "slimificationEnabled": "True", "slimificationClockDays": "7", "fieldConversionEnabled": "True",
            "fieldConversionRate": "1", "visitorsEnabled": "True", "visitorArrivalRate": "1", "gappoChannels": "True", "fubbumHunts": "True", "dwommoFlies": "True", "glurroSalve": "True", "pitSolvent": "True"}
TITAN_STAGES = [0, 0, 1, 2, 1, 0, 2, 1, 0, 0, 1, 2, 0, 1, 0, 2]


def _faults():
    return {f for f in os.environ.get("NS_SLIME_MOCK_BREAK", "").split(",") if f}


def _walk_defs():
    out = {}
    for dp, _, fns in os.walk(os.path.join(HERE, "Defs")):
        for fn in fns:
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    nm = el.find("defName") if isinstance(el.tag, str) else None
                    if nm is not None and (el.get("Abstract") or "").lower() != "true":
                        out["%s/%s" % (el.tag, nm.text.strip())] = el
    return out


def _drying():
    out = {}
    p = os.path.join(HERE, "Patches", "DryingBiomes.xml")
    for op in ET.parse(p).getroot().iter("Operation"):
        xp = op.find("xpath")
        d = op.find(".//decayPerDay")
        if xp is not None and d is not None:
            import re
            m = re.search(r'defName="([^"]+)"', xp.text)
            if m:
                out[m.group(1)] = float(d.text)
    return out


class SlimeSim(object):
    def __init__(self, game):
        self.g = game
        self.defs = _walk_defs()
        self.dry = _drying()
        self.pawns = {}
        self.n = 0
        self.rng = random.Random(7)
        self.settings = dict(DEFAULTS)
        self.pending = []
        self.titans = 0
        self.dmg = {}
        self.f = _faults()
        self.biome = os.environ.get("NS_SLIME_MOCK_BIOME", "TemperateForest")
        self.weather = "Clear"
        if "defaultswrong" in self.f:
            self.settings["titanoslimeReversible"] = "True"

    # ------------------------------------------------------------------ helpers
    def terrain(self, x, z):
        return self.g.terrain.get((x, z), "Soil")

    def on_slime(self, p):
        return self.terrain(p["x"], p["z"]) in SLIME_TERRAINS

    def decay(self):
        return None if "nodry" in self.f else self.dry.get(self.biome)

    def _row(self, pid, health=True):
        p = self.pawns[pid]
        r = {"id": pid, "kind": p["kind"], "kindDef": p["kind"], "x": p["x"], "z": p["z"], "dead": False,
             "faction": p["faction"], "isPlayer": p["faction"] == "player"}
        if health:
            r["health"] = {"hediffs": [{"def": k, "severity": v} for k, v in p["hed"].items()]}
        return r

    def _put(self, name, x, z):
        self.g.things.setdefault((x, z), []).append(name)

    def _take(self, tid):
        d, rest = tid.rsplit("#", 1)
        x, z = [int(v) for v in rest.split("_")]
        if d in self.g.things.get((x, z), []):
            self.g.things[(x, z)].remove(d)
            return True
        return False

    def stage_of(self, p):
        return p.get("stage", 0)

    # ------------------------------------------------------------------ dispatch
    def handle(self, tool, p):
        h = getattr(self, "t_" + tool.replace("/", "_"), None)
        return NotImplemented if h is None else h(p)

    def t_jawa_get_defs(self, p):
        rows, nf = [], []
        want = [w.strip() for w in str(p["defs"]).split(";") if w.strip()]
        fields = [f.strip() for f in str(p.get("fields") or "").split(",") if f.strip()]
        for w in want:
            row = {"requested": w, "found": True, "defName": w.split("/", 1)[1], "fields": {}}
            typ, name = w.split("/", 1)
            ok = w in self.defs or w in {"BiomeDef/Desert", "BiomeDef/ExtremeDesert", "BiomeDef/AridShrubland",
                                         "BiomeDef/Ocean", "BiomeDef/TemperateForest",
                                         "MapGeneratorDef/Base_Player"} or typ == "GeneDef" and name in self.genes()
            if ("nodef:" + w) in self.f:
                ok = False
            if not ok:
                rows.append({"requested": w, "found": False})
                nf.append(w)
                continue
            el = self.defs.get(w)
            fl = row["fields"]
            if typ == "TerrainDef":
                fl["tags"] = [] if "notag" in self.f else ["RM_SlimeTerrain"]
            if typ == "HediffDef" and name == "RM_Slimification":
                st = []
                for li in el.findall("stages/li"):
                    d = {"minSeverity": float(li.findtext("minSeverity") or 0), "label": li.findtext("label"),
                         "painFactor": float(li.findtext("painFactor") or 1), "mentalStateGivers": None}
                    if li.find("mentalStateGivers") is not None:
                        d["mentalStateGivers"] = [{"x": 1}]
                    st.append(d)
                fl.update(stages=st, maxSeverity=float(el.findtext("maxSeverity") or 0),
                          comps=[{"compClass": "HediffComp_Slimification"}], scenarioCanAdd=False)
            if typ == "BiomeDef":
                d = self.dry.get(name) if "nodry" not in self.f else None
                fl["modExtensions"] = [{"decayPerDay": d}] if d else []
            if typ == "ThingDef" and el is not None and el.find("race") is not None:
                r = el.find("race")
                fl["race"] = {k: r.findtext(k) for k in ("predator", "maxPreyBodySize", "baseBodySize",
                                                          "manhunterOnDamageChance", "manhunterOnTameFailChance")}
            if typ == "ThingDef" and el is not None and el.find("statBases/MaxFlightTime") is not None:
                fl["statBases"] = {"MaxFlightTime": 0 if "noflight" in self.f else float(el.findtext("statBases/MaxFlightTime"))}
            if typ == "MapGeneratorDef":
                fl["genSteps"] = ["TerrainGen"] + ([] if "nostep" in self.f else ["RM_SlimeVisitorSeed"])
            if typ.endswith("GeneArchiveDef"):
                tg, rg = self.archive()
                fl.update(priority=0, targetGenes=tg, riderGenes=rg)
            rows.append(row)
        return {"success": True, "foundCount": len(rows) - len(nf), "notFound": nf, "malformed": [], "defs": rows}

    def archive(self):
        el = self.defs["RimMandrake.GelatinousSlime.GeneArchiveDef/RM_Archive_Default"]
        return ([x.text.strip() for x in el.findall("targetGenes/li")],
                [x.text.strip() for x in el.findall("riderGenes/li")])

    def genes(self):
        tg, rg = self.archive()
        return set(tg + rg)

    def t_jawa_map_info(self, p):
        return {"success": True, "sizeX": 250, "sizeZ": 250, "mapBiome": self.biome}

    def t_jawa_mod_settings_field(self, p):
        k = p["field"]
        if k not in self.settings:
            return {"success": False, "message": "no field"}
        if p.get("action") == "set":
            self.settings[k] = str(p["value"])
        return {"success": True, "value": self.settings[k]}

    def t_jawa_get_terrain_batch(self, p):
        x, z, w, h = [int(v) for v in str(p["rects"]).split(",")]
        d = sorted({self.terrain(x + i, z + j) for i in range(w) for j in range(h)})
        return {"success": True, "distinctTerrains": d, "ops": ""}

    def t_jawa_weather_get(self, p):
        return {"success": True, "weather": {"current": self.weather}}

    def t_jawa_weather_set(self, p):
        if p.get("weather") == "RM_Weather_SlimeRain" and "noweather" in self.f:
            return {"success": False}
        self.weather = p.get("weather")
        return {"success": True}

    def t_jawa_spawn_pawn(self, p):
        self.n += 1
        pid = "Pawn%d" % self.n
        kind = p["kindDef"]
        pw = {"kind": kind, "x": p["x"], "z": p["z"], "faction": p.get("faction"), "hed": {}, "genes": [],
              "mental": None}
        if kind == "RM_Titanoslime":
            st = TITAN_STAGES[self.titans % len(TITAN_STAGES)]
            self.titans += 1
            if "noclamp" not in self.f:
                st = min(st, int(float(self.settings["titanoslimeMaxStage"])) - 1)
            pw["stage"] = st
        self.pawns[pid] = pw
        return {"success": True, "pawns": [{"id": pid}]}

    def t_jawa_list_pawns(self, p):
        return {"success": True, "pawns": [self._row(i, bool(p.get("includeHealth"))) for i in self.pawns]}

    def t_jawa_destroy_batch(self, p):
        return NotImplemented

    def t_jawa_pawn_health(self, p):
        pw = self.pawns.get(p.get("pawn"))
        if pw is None:
            return {"success": False}
        if p.get("action") == "add":
            sev = p.get("severity", -1)
            pw["hed"][p["hediff"]] = 0.01 if sev is None or sev < 0 else float(sev)
        elif p.get("action") == "remove":
            pw["hed"].pop(p["hediff"], None)
        return {"success": True}

    def t_jawa_pawn_severity_adjust(self, p):
        pw = self.pawns.get(p.get("pawn"))
        if pw is None or p["hediff"] not in pw["hed"]:
            return {"success": False}
        pw["hed"][p["hediff"]] += float(p["offset"])
        return {"success": True}

    def t_jawa_pawn_genes(self, p):
        pw = self.pawns.get(p.get("pawn"))
        if pw is None:
            return {"success": False}
        if p.get("action") == "add":
            pw["genes"].append(p["gene"])
        return {"success": True, "endogenes": list(pw["genes"]), "xenogenes": []}

    def t_jawa_pawn_mental(self, p):
        pw = self.pawns.get(p.get("pawn"))
        if pw is None:
            return {"success": False}
        if p.get("action") == "start":
            pw["mental"] = p["state"]
            return {"success": True, "started": True, "currentState": pw["mental"]}
        return {"success": True, "currentState": pw["mental"], "states": []}

    def t_jawa_alerts_list(self, p):
        if "noalert" in self.f or not any(x["hed"].get("RM_Slimification", 0) >= 0.2 for x in self.pawns.values()):
            return {"success": True, "alerts": []}
        return {"success": True, "alerts": [{"type": "Alert_Slimification", "label": "Being absorbed"}]}

    def t_jawa_read_opinion(self, p):
        pw = self.pawns[p["pawn"]]
        sev = pw["hed"].get("RM_SlimeMarked", 0)
        off = 0 if "nomarkedcost" in self.f or sev <= 0 else (36 if sev >= 4 else 22 if sev >= 2 else 12)
        return {"success": True, "opinionOfPawn": 20 - off}

    def t_jawa_inspect_string(self, p):
        tid = str(p.get("thingIds"))
        if tid in self.pawns and self.pawns[tid]["kind"] == "RM_Titanoslime":
            return {"success": True, "things": [{"id": tid, "inspect": ["Stage %d of 5 - titanoslime" % (self.pawns[tid]["stage"] + 1)]}]}
        if tid.startswith("RM_GeneSeeker") and "noseeker" not in self.f:
            return {"success": True, "things": [{"id": tid, "inspect": ["Not primed. Ask the archive for an entry."]}]}
        return {"success": True, "things": [{"id": tid, "inspect": ["-"]}]}

    def t_jawa_damage(self, p):
        tid = p.get("thingId")
        pw = self.pawns.get(tid)
        if pw is None:
            return {"success": False}
        self.dmg[tid] = self.dmg.get(tid, 0) + float(p["amount"])
        if (self.settings["titanoslimeSheds"] == "True" or "shedignore" in self.f) and "noshed" not in self.f \
                and pw.get("stage", 0) >= 1 and self.dmg[tid] >= 28.8:
            self.dmg[tid] = 0
            self.n += 1
            self.pawns["Pawn%d" % self.n] = {"kind": "RM_Gelatid", "x": pw["x"], "z": pw["z"], "faction": None,
                                             "hed": {}, "genes": [], "mental": None}
        return {"success": True}

    def t_jawa_ordered_job(self, p):
        if p.get("jobDef") in ("UseItem", "Ingest"):
            self.pending.append(dict(p))
            return {"success": True, "accepted": True, "nowRunningRequested": True}
        return NotImplemented

    # ------------------------------------------------------------------ time
    def step(self, t0, t1):
        for tk in range(((t0 // 100) + 1) * 100, t1 + 1, 100):
            if tk % 200 == 0:
                self._slim_checks()
            if tk % 500 == 0:
                self._exposure()
        if t1 - t0 >= 400:
            self._jobs()

    def _slim_checks(self):
        for pid in list(self.pawns):
            pw = self.pawns[pid]
            sev = pw["hed"].get("RM_Slimification")
            if sev is None:
                continue
            if sev >= 0.5 and pw["mental"] == "PanicFlee" and "nolaw2" not in self.f:
                pw["mental"] = None
            if sev >= 1.0 and "nodissolve" not in self.f:
                del self.pawns[pid]
                self._put("RM_RawSlime", pw["x"], pw["z"])
                if "nosmear" not in self.f:
                    self._put("RM_Filth_SlimeSmear", pw["x"], pw["z"])
                continue
            d = self.decay()
            if d:
                r = -abs(d)
            elif self.on_slime(pw):
                r = 1.0 / 7 * (3 if "growfast" in self.f else 1)
                gs = pw["hed"].get("RM_GlurroSalved")
                if gs is not None and "nosalve" not in self.f and self.settings.get("glurroSalve") == "True":
                    r *= 1.0 - min(gs, 0.8)
            else:
                r = -0.5 if sev < 0.2 else 0.0
            sev = min(1.0, sev + r * 200.0 / 60000.0)
            if sev <= 0:
                del pw["hed"]["RM_Slimification"]
            else:
                pw["hed"]["RM_Slimification"] = sev

    def _exposure(self):
        if "noexpose" in self.f:
            return
        for pw in list(self.pawns.values()):
            if not self.on_slime(pw) or pw["kind"] in ("RM_Gelatid", "RM_Titanoslime") \
                    or "RM_Gene_SlimeResistance" in pw["genes"]:
                continue
            pw["hed"].setdefault("RM_Slimification", 0.01)
            if self.settings["flavorReadMarks"] == "True" or "nosmearsetting" in self.f:
                if pw["hed"]["RM_Slimification"] >= 0.2 and self.rng.random() < 0.06:
                    self._put("RM_Filth_SlimeSmear", pw["x"], pw["z"])

    def _jobs(self):
        for j in self.pending:
            pw = self.pawns.get(j.get("targetBId") or j.get("pawnId"))
            if j["jobDef"] == "UseItem" and pw is not None:
                self._take(j["targetAId"])
                if "antidote_noop" not in self.f:
                    pw["hed"].pop("RM_Slimification", None)
                if "antidote_nocost" not in self.f:
                    pw["hed"]["ToxicBuildup"] = pw["hed"].get("ToxicBuildup", 0) + 0.14
            if j["jobDef"] == "Ingest":
                pw = self.pawns.get(j["pawnId"])
                self._take(j["targetAId"])
                if "eat_nocure" not in self.f:
                    pw["hed"].pop("ToxicBuildup", None)
                if "eat_nofee" not in self.f:
                    pw["hed"]["RM_Slimification"] = pw["hed"].get("RM_Slimification", 0.01) + 0.12
        self.pending = []


def install():
    from northstar_driver import transport
    if getattr(transport.MockGame, "_slime_installed", False):
        return
    orig = transport.MockGame.handle

    def handle(self, tool, p):
        sim = getattr(self, "_slime", None)
        if sim is None:
            sim = self._slime = SlimeSim(self)
        p = p or {}
        if tool == "rimworld/step_game_ticks":
            t0 = self.ticks
            r = orig(self, tool, p)
            sim.step(t0, self.ticks)
            return r
        if tool == "jawa/destroy_batch":
            r = orig(self, tool, p)
            x, z, w, h = [int(v) for v in str(p["rects"]).split(",")]
            if str(p.get("categories") or "") in ("All", "Pawn"):
                for pid in [k for k, q in sim.pawns.items() if x <= q["x"] < x + w and z <= q["z"] < z + h]:
                    del sim.pawns[pid]
            return r
        r = sim.handle(tool, p)
        if r is not NotImplemented:
            return r
        return orig(self, tool, p)

    transport.MockGame.handle = handle
    transport.MockGame._slime_installed = True
