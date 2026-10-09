#!/usr/bin/env python3
"""Offline selftest for the FeverWood north-star suite (validation.py): no game, no bridge.

`FWGame` below is a small in-memory Fever Wood: the mod's own parsed Defs answer jawa/get_defs and
jawa/biome_probe, a settings table answers jawa/mod_settings_field, and the limbs, the porter, the lash, the
tank, the suppressant job, the sap-suckers, the lure stake, the flora harvest and the swarm raid change its
world the way the C# does. It proves two things the first live run cannot prove on its own:

  1. a HEALTHY world passes every component (the suite's checks are not vacuously red), and
  2. each deliberate BREAK of the mod (a patch that matched nothing, a limb that never severs, a tank that
     ignores its toggle, a refusal that is a roll, a raid that ignores its toggle ...) turns exactly the
     component that exists for it red, so the checks can fail for the reason they are named for.

This is evidence about the SUITE, not about the game: the mock encodes the response shapes the suite ASSUMES
(the header of validation.py lists which are unproven live).
Run: python3 src/RimMandrake/FeverWood/selftest_feverwood.py
"""
import json
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import game_paths                                              # noqa: E402
import runner                                                  # noqa: E402
import validation as V                                         # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []
SWARM = "RM_FactionDef_KurrethSwarm"
PHRASE = "The pool's water %s - no tentacles" % V.SUPPRESSED_PHRASE


OILBOIL_CS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source", "RM_OilBoil.cs")


def flash_chance_on_bare_ground(cs_path):
    """FireUtility.ChanceToStartFireIn (RimSage, 1.6) for a hazed cell with terrain flammability 0 and nothing on it,
    using the curve RM_OilBoil.Flash actually passes to TryStartFireIn. No curve -> 0 (vanilla refuses the cell)."""
    import re
    src = open(cs_path, encoding="utf-8").read()
    call = re.search(r"FireUtility\.TryStartFireIn\(([^;]*)\);?", src[src.find("public bool Flash("):])
    if not call:
        return 0.0
    args = [a.strip() for a in call.group(1).split(",")]
    name = args[-1].split(".")[-1].rstrip(")")  # the optional flammabilityChanceCurve is the last argument
    body = re.search(r"SimpleCurve\s+" + re.escape(name) + r"\s*=\s*new\s+SimpleCurve\s*\{(.*?)\};", src, re.S)
    if not body:
        return 0.0
    pts = sorted((float(x.rstrip("f")), float(y.rstrip("f")))
                 for x, y in re.findall(r"CurvePoint\(\s*([-\d.]+f?)\s*,\s*([-\d.]+f?)\s*\)", body.group(1)))
    if not pts:
        return 0.0
    x = 0.0
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def _fmt(v):
    return str(v) if isinstance(v, (bool, int)) else ("%g" % v)


class FWGame(MockGame):
    def __init__(self, brk=()):
        MockGame.__init__(self, sizex=300, sizez=300)
        self.brk = set(brk)
        self.objs = []                    # buildings, items, plants: dicts
        self.msgs = []
        self.n = 0
        self.sett = dict((k, _fmt(d)) for k, (_, d) in V.SETTING_FIELDS.items())
        self.sett["reactionDetectionEnabled"] = "True"     # CreatureBehaviors' field, same mock table
        if "settings_drift" in self.brk:
            self.sett["twoFrontLureRaidMtbHours"] = "7"
        self.known = {}                   # (DefType, name) -> packageId
        for group, deftype, names, _ in V.GROUPS:
            for n in names:
                self.known[(deftype, n)] = "mandrake.rm.biomes"
        self.known[("SoundDef", "RM_FeverWood_CrownHum")] = "mandrake.rm.biomes"
        self.known[("ThingDef", "TableMachining")] = "Ludeon.RimWorld"
        self.known[("MapGeneratorDef", "Base_Player")] = "Ludeon.RimWorld"
        self.known[("LetterDef", "RM_DeepGiftLetter")] = "mandrake.rm.biomes"   # Defs/LetterDefs (not a parsed group)
        if "missing_def" in self.brk:
            plain = next(n for g, _, ns, _ in reversed(V.GROUPS) if g == "items_ThingDef" for n in reversed(ns)
                         if ("ThingDef", n) not in [bn for bn in V.BY_NAME] and n not in V.ROTTABLE_ITEMS)
            del self.known[("ThingDef", plain)]
        if "donor_shadow" in self.brk:
            self.known[("ThingDef", next(n for g, _, ns, _ in V.GROUPS if g == "plants_ThingDef" for n in ns))] = "some.donor.mod"
        if "name_missing" in self.brk:
            del self.known[("HediffDef", "RM_LureStaked")]

    # ----------------------------------------------------------------- helpers
    def _id(self):
        self.n += 1
        return self.n

    def sb(self, name):
        return self.sett.get(name) == "True"

    def sf(self, name):
        return float(self.sett.get(name))

    def handle(self, tool, p):
        p = p or {}
        fn = getattr(self, "t_" + tool.replace("/", "_"), None)
        if fn is not None:
            self._tick()
            return fn(p)
        return MockGame.handle(self, tool, p)

    def t_jawa_static_call(self, p):
        """RM_KurrethTheftProof (FEVERWOOD_ANT_THEFT_RAIDBACK_1): ProofRaid stages the column; ProofState reads
        the outcome the C# would leave -- a healthy theft takes one thornbug alive and sends the letter."""
        if p.get("type") == "RimMandrake.FeverWood.RM_OilBoilProof":
            m = p.get("method")
            if m == "ProofGate":
                return {"success": True, "result": "canOccur=%s temp=40.0 min=35.0 enabled=%s" % (
                    self.sb("oilBoilEnabled") and "gate_stuck" not in self.brk, self.sb("oilBoilEnabled"))}
            if m == "ProofYield":
                return {"success": True, "result": "yieldOff=8 yieldOn=%d" % (8 if "yield_flat" in self.brk else 16)}
            if m == "ProofSpark":
                # fires come from the SHIPPED C#: the proof's haze lies on bare ground (terrain flammability 0), so
                # vanilla's gate starts a fire only if Flash passes a curve whose value at 0 is > 0
                cold = "haze_inert" in self.brk
                lit = 0 if cold else sum(1 for _ in range(23) if flash_chance_on_bare_ground(OILBOIL_CS) > 0)
                return {"success": True, "result": "flashed=%s firesBefore=0 firesAfter=%d conditionEnded=%s" % (
                    not cold, lit, not cold)}
        if p.get("type") == "RimMandrake.FeverWood.RM_KurrethColumnProof":
            if not getattr(self, "theft_raid", False) or not self.sb("kurrethColumnEnabled") or "column_never" in self.brk:
                return {"success": True, "result": "quest=0"}
            phase = "Column"
            if p.get("method") == "ProofHive":
                phase = "Column" if "column_stuck" in self.brk else "Done"
            return {"success": True, "result": "quest=1 phase=%s site=1 siteTile=101 held=1 bound=1 victimIds=4242" % phase}
        if p.get("type") != "RimMandrake.FeverWood.RM_KurrethTheftProof":
            raise RuntimeError("mock: unknown static_call type %s" % p.get("type"))
        if p.get("method") == "ProofRaid":
            self.theft_raid = True
            return {"success": True, "result": "RAID ants=6 thornbugs=3 edge=(0,0,5) faction=Faction_9"}
        if not getattr(self, "theft_raid", False) or not self.sb("antTheftEnabled"):
            return {"success": True, "result": "thefts=0 heldByKurreth=0 thornbugsOnMap=3 thornbugCorpses=0 stolenIds= letters=0"}
        if "theft_kills" in self.brk:
            return {"success": True, "result": "thefts=0 heldByKurreth=0 thornbugsOnMap=1 thornbugCorpses=2 stolenIds= letters=0"}
        letters = 0 if "theft_silent" in self.brk else 1
        return {"success": True, "result": "thefts=1 heldByKurreth=1 thornbugsOnMap=2 thornbugCorpses=0 "
                                           "stolenIds=4242 letters=%d" % letters}

    def _obj(self, tid):
        return next((o for o in self.objs if o["id"] == tid), None)

    def _pawn(self, pid):
        return next((q for q in self.pawns if q["id"] == pid), None)

    def _rect(self, p):
        if not p.get("rect"):
            return None
        return [int(v) for v in str(p["rect"]).split(",")]

    @staticmethod
    def _in(r, x, z):
        return r is None or (r[0] <= x < r[0] + r[2] and r[1] <= z < r[1] + r[3])

    def _add(self, d, x, z, **kw):
        o = {"id": "%s#%d" % (d, self._id()), "def": d, "x": x, "z": z, "stack": 1, "born": self.ticks,
             "hp": 100.0, "maxhp": 100.0, "first_hit": None, "dmg": 0.0, "bait": None, "next": self.ticks}
        o.update(kw)
        self.objs.append(o)
        return o

    # ------------------------------------------------------------------ defs & biome
    def t_jawa_get_defs(self, p):
        rows, nf = [], []
        want = [f for f in (p.get("fields") or "").split(",") if f]
        specs = [s for s in str(p.get("defs") or "").split(";") if s]
        for spec in specs:
            typ, name = spec.split("/", 1)
            pkg = self.known.get((typ, name))
            if pkg is None:
                rows.append({"requested": spec, "found": False, "defName": name})
                nf.append(spec)
                continue
            rows.append({"requested": spec, "found": True, "defName": name, "defType": typ,
                         "packageId": pkg, "fields": self._fields(typ, name, want)})
        return {"success": True, "requested": len(specs), "foundCount": len(specs) - len(nf),
                "notFound": nf, "defs": rows}

    def _fields(self, typ, name, want):
        allf = {}
        if typ == "BiomeDef":
            exts = [c for c in V.EXT_CLASSES if not ("no_ext" in self.brk and c == "RM_AntHiveBiomeExtension")]
            allf = {"modExtensions": [dict({"Class": "RimMandrake.X." + c},
                                           **({"heatKind": "ambient"} if c == "RM_SunHeatExtension" else {}))
                                      for c in exts]}
        elif typ == "MapGeneratorDef":
            allf = {"genSteps": [n for n, _ in V.GENSTEPS_REGISTERED
                                 if not ("genstep_unregistered" in self.brk and n == "RM_GenStep_AntHiveDungeon")] + ["Terrain"]}
        elif name == "TableMachining":
            allf = {"recipes": ["Make_ComponentIndustrial"] + ([] if "no_recipe" in self.brk else ["RM_MakeRadioactiveSuppressant"])}
        elif name == "RUT_BoughSoil":
            allf = {"fertility": 0.0 if "bough_infertile" in self.brk else 1.4,
                    "affordances": ["Light", "Medium", "GrowSoil"] + (["Heavy"] if "bough_heavy" in self.brk else [])}
        elif name in V.ROTTABLE_ITEMS:
            allf = {"tickerType": "Never" if ("ticker_never" in self.brk and name == V.ROTTABLE_ITEMS[0]) else "Rare"}
        return dict((k, v) for k, v in allf.items() if not want or k in want)

    def t_jawa_biome_probe(self, p):
        def live(roster):
            return [{"defName": n, "commonality": c} for n, (c, req) in sorted(roster.items())
                    if not req or req in V.ACTIVE_ON_TIER]
        animals, plants = live(V.BIOME_ANIMALS), live(V.BIOME_PLANTS)
        if "roster_zero_commonality" in self.brk:
            animals = [dict(a, commonality=0.0) if a["defName"] == "RM_Chellow" else a for a in animals]
        find = []
        for f in [f for f in str(p.get("find") or "").split(",") if f]:
            spawning = f in [a["defName"] for a in animals]
            find.append({"defName": f, "present": spawning, "state": "spawning" if spawning else "absent"})
        return {"success": True, "biomes": [{
            "defName": p.get("biomes"), "generatesNaturally": "natural_gen" in self.brk,
            "animalDensity": 0.0 if "zero_density" in self.brk else V.BIOME_SCALARS.get("animalDensity"),
            "plantDensity": V.BIOME_SCALARS.get("plantDensity"),
            "wildAnimalCount": len(animals), "animalsListed": len(animals), "animals": animals,
            "wildPlantCount": len(plants), "plantsListed": len(plants), "plants": plants,
            "findResults": find}]}

    # ------------------------------------------------------------------- settings / UI / registry
    def t_jawa_mod_settings_field(self, p):
        f = p.get("field")
        if f not in self.sett:
            return {"success": False, "message": "no such field"}
        if p.get("action") == "set" and not ("toggle_stuck" in self.brk and f == "antHiveDungeonEnabled"):
            self.sett[f] = str(p.get("value"))
        return {"success": True, "value": self.sett[f]}

    def t_rimworld_list_architect_categories(self, p):
        return {"success": True, "categories": [{"id": "cat-orders", "categoryDefName": "Orders"}]}

    def t_rimworld_list_architect_designators(self, p):
        ds = [{"id": "d-hunt", "label": "Hunt"}]
        if "no_orders_designator" not in self.brk:
            ds += [{"id": "d-foul", "label": "Foul pool with suppressant"}, {"id": "d-stake", "label": "Stake as lure"}]
        return {"success": True, "designators": ds}

    def t_jawa_harmony_patches(self, p):
        if "no_harmony" in self.brk:
            return {"success": True, "methodCount": 0, "methods": []}
        return {"success": True, "methodCount": 1, "methods": [{"method": p.get("methodName"), "postfixCount": 1,
                                                                  "postfixes": [{"owner": V.HARMONY_ID}]}]}

    def t_rimworld_list_messages(self, p):
        out = []
        for m in self.msgs:
            if m["reads"] < 1:
                out.append({"text": m["text"]})
            m["reads"] += 1
        return {"success": True, "messages": out}

    # ------------------------------------------------------------------- spawning / listing
    def t_jawa_spawn_batch(self, p):
        for op in str(p["ops"]).split(";"):
            name, rest = op.split(":")
            x, z = [int(v) for v in rest.split(",")[:2]]
            hp = {"RM_SekkulaathTank": V.TANK_HP}.get(name) or {"RM_Sekkulaath_Feeler": V.LIMB_FEELER["hp"],
                                                               "RM_Sekkulaath_Lash": V.LIMB_LASH["hp"],
                                                               "RM_Sekkulaath_Porter": V.LIMB_PORTER["hp"]}.get(name, 100.0)
            self._add(name, x, z, hp=hp, maxhp=hp, next=self.ticks + V.LIMB_LASH["lash_interval"])
        return {"success": True}

    def t_rimworld_spawn_thing(self, p):
        self._add(p["defName"], p["x"], p["z"], stack=int(p.get("stackCount") or 1))
        return {"success": True}

    def t_jawa_set_plants(self, p):
        for op in str(p["ops"]).split(";"):
            name, rest = op.split(":")
            x, z = [int(v) for v in rest.split(",")[:2]]
            self._add(name, x, z)
        return {"success": True}

    def t_jawa_spawn_pawn(self, p):
        pid = "Pawn%d" % self._id()
        self.pawns.append({"id": pid, "kindDef": p["kindDef"], "x": p["x"], "z": p["z"],
                           "faction": None if p.get("faction") == "none" else "Player", "factionDef": None,
                           "hediffs": {}, "downed": False, "last_refusal": None, "refusals": 0})
        return {"success": True, "pawns": [{"id": pid}]}

    def _pawn_row(self, q):
        return {"id": q["id"], "kindDef": q["kindDef"], "x": q["x"], "z": q["z"], "faction": q["faction"],
                "downed": q["downed"], "health": {"hediffs": [{"def": h, "severity": s} for h, s in q["hediffs"].items()]}}

    def t_jawa_list_pawns(self, p):
        r = self._rect(p)
        rows = [self._pawn_row(q) for q in self.pawns if self._in(r, q["x"], q["z"])
                and (not p.get("faction") or q.get("factionDef") == p.get("faction"))]
        return {"success": True, "pawns": rows}

    def t_jawa_pawn_census(self, p):
        ids = [i for i in str(p.get("ids") or "").split(",") if i]
        rows = [{"id": q["id"], "kindDef": q["kindDef"], "mentalState": q.get("mental"), "dead": q.get("dead", False),
                 "downed": q["downed"],
                 "job": {"def": "Wait_Wander"}} for q in self.pawns if not ids or q["id"] in ids]
        return {"success": True, "pawns": rows}

    def t_jawa_pawn_need(self, p):
        q = self._pawn(p.get("pawn"))
        if q is not None and p.get("need") == "Food":
            q["food"] = float(p.get("level"))
        return {"success": True}

    def t_jawa_list_things(self, p):
        r = self._rect(p)
        want = set(d.strip() for d in str(p.get("defName") or "").split(",") if d.strip())
        rows = [{"defName": o["def"], "def": o["def"], "id": o["id"], "x": o["x"], "z": o["z"],
                 "stackCount": o["stack"]} for o in self.objs
                if self._in(r, o["x"], o["z"]) and (not want or o["def"] in want)]
        return {"success": True, "things": rows, "isCompleteList": True}

    def t_jawa_destroy_batch(self, p):
        r = self._rect({"rect": p["rects"]})
        if p.get("categories") == "Pawn":
            self.pawns = [q for q in self.pawns if not self._in(r, q["x"], q["z"])]
            return {"success": True}
        keep = []
        for o in self.objs:
            if self._in(r, o["x"], o["z"]):
                self._on_destroyed(o)
            else:
                keep.append(o)
        self.objs = keep
        return {"success": True}

    def _on_destroyed(self, o):
        if o["def"] == "RM_LureStake" and o.get("bait") and "stake_leaves_hediff" not in self.brk:
            q = self._pawn(o["bait"])
            if q:
                q["hediffs"].pop(V.LURE_STAKED, None)

    # ------------------------------------------------------------------- health / pawns
    def t_jawa_pawn_health(self, p):
        q = self._pawn(p.get("pawn"))
        if q is None:
            return {"success": False}
        if p.get("action") == "remove":
            q["hediffs"].pop(p.get("hediff"), None)
        return {"success": True}

    def t_jawa_pawn_force_incapacitate(self, p):
        q = self._pawn(p.get("pawn"))
        if q is None:
            return {"success": False}
        q["downed"] = True
        return {"success": True, "downedAfter": True}

    def t_jawa_inspect_string(self, p):
        o = self._obj(str(p.get("thingIds")))
        if o is None:
            return {"success": True, "things": []}
        if o["def"] == "RM_LureStake":
            bait = o.get("bait")
            line = "Baited with Colonist - raiders may be drawn to it." if bait else \
                   ("Baited with nobody." if "stake_empty_wrong" in self.brk else "No bait staked.")
        elif o["def"] == "RM_SekkulaathTank":
            line = "Occupant fed - producing while stock lasts."
        elif o["def"] == "RM_SekkulaathYoungCask":
            on = self.sett.get("broodRansomEnabled") == "True" or "brood_ignores_toggle" in self.brk
            line = "Young of the deep held in the world: 1 (the pools are uneasy, tentacles x1.10)" if on else ""
        else:
            line = ""
        return {"success": True, "things": [{"id": o["id"], "inspect": [line]}]}

    # ----------------------------------------------------------------------- damage
    def t_jawa_damage(self, p):
        amount = float(p["damageDef"] and p.get("amount") or 0)
        tid = p.get("thingId")
        o = self._obj(tid)
        if o is not None:
            self._hit_obj(o, amount, p.get("damageDef") or "Blunt")
            return {"success": True}
        q = self._pawn(tid)
        if q is not None:
            if amount >= 9000:
                self.pawns.remove(q)
            else:
                self._hit_pawn(q)
            return {"success": True}
        return {"success": False, "message": "no such thing"}

    def _hit_obj(self, o, amount, damage_def="Blunt"):
        d = o["def"]
        if d.startswith("RM_Sekkulaath_") and damage_def == "Blunt" and "no_building_factor" not in self.brk:
            amount = amount * V.BLUNT_BUILDING_FACTOR    # DamageWorker.Apply: Blunt buildingDamageFactor 1.5
        if d.startswith("RM_Sekkulaath_") and d != "RM_Sekkulaath_Bloom" and o["hp"] - amount <= 0:
            # Kill runs before the comp's damage hook: the comp sees no map; only killedLeavingsRanges drop flesh
            self.objs.remove(o)
            if "no_kill_leavings" not in self.brk:
                self._add("RM_SeveredTentacleFlesh", o["x"], o["z"], stack=3)
            return
        o["hp"] -= amount
        o["dmg"] += amount
        if d == "RM_Sekkulaath_Porter":
            if "porter_survives_hit" in self.brk or "porter_hit_still_deposits" in self.brk:
                return
            self.objs.remove(o)
        elif d.startswith("RM_Sekkulaath_") and d != "RM_Sekkulaath_Bloom":
            if o["first_hit"] is None:
                o["first_hit"] = self.ticks
            if "feeler_nosever" in self.brk:
                return
            if o["dmg"] >= o["maxhp"] * V.LIMB_FEELER["severe"]:
                self.objs.remove(o)
                if "no_flesh" not in self.brk:
                    self._add("RM_SeveredTentacleFlesh", o["x"], o["z"], stack=3)
        elif d == "RM_SekkulaathTank":
            if "tank_unbreakable" in self.brk:
                return
            lost = 1.0 - o["hp"] / o["maxhp"]
            if lost < V.TANK_THRESHOLD and "tank_light_breaks" not in self.brk:
                return
            if not (self.sb("sekkulaathTankEnabled") or "tank_ignores_toggle" in self.brk):
                return
            chance = min(1.0, 0.35 / max(0.01, self.sf("sekkulaathEscapeRiskMultiplier")))
            if chance >= 1.0:
                self.objs.remove(o)
                q = self.t_jawa_spawn_pawn({"kindDef": V.TANK_OCCUPANT, "x": o["x"] + 1, "z": o["z"], "faction": "none"})
                if "tank_no_memory" not in self.brk:
                    self._pawn(q["pawns"][0]["id"])["hediffs"][V.CAPTIVITY_MEMORY] = 1.0

    def _hit_pawn(self, q):
        spec = next((s for s in V.SAP_KINDS if s[0] == q["kindDef"]), None)
        if spec is None:
            return
        kind, hediff, sev, cd = spec
        if "sap_noop" in self.brk and kind == "RM_Vaulm":
            return
        ready = q["last_refusal"] is None or self.ticks - q["last_refusal"] >= cd
        if "sap_no_cooldown" in self.brk:
            ready = True
        if "sap_one_shot" in self.brk and q["refusals"] >= 1:
            ready = False
        if ready:
            q["last_refusal"] = self.ticks
            q["refusals"] += 1
            q["hediffs"][hediff] = sev

    # --------------------------------------------------------------------------- jobs
    def t_jawa_ordered_job(self, p):
        q = self._pawn(p.get("pawnId"))
        if q is None:
            return {"success": False}
        job, a = p.get("jobDef"), p.get("targetAId")
        ok = {"success": True, "accepted": True, "nowRunningRequested": True}
        if job == "RM_FoulPool":
            o = self._obj(a)
            amt = int(self.sf("tentacleUraniumSuppressantAmountPerUse"))
            if "foul_noconsume" not in self.brk:
                o["stack"] -= amt
            announce = self.sb("tentacleUraniumSuppressionEnabled") or "foul_message_ignores_toggle" in self.brk
            if announce and "foul_no_message" not in self.brk:
                self.msgs.append({"text": PHRASE, "reads": 0})
        elif job == "RM_HaulToStake":
            bait, stake = self._pawn(a), self._obj(p.get("targetBId"))
            if bait is not None and bait["downed"] and stake is not None and "stake_no_chain" not in self.brk:
                bait["hediffs"][V.LURE_STAKED] = 1.0
                stake["bait"] = bait["id"]
                stake["staked_at"] = self.ticks
        elif job == "Harvest" and "flora_noop" not in self.brk:
            o = self._obj(a)
            prod = next(prod for pl, prod, _ in V.FLORA_PRODUCTS if pl == o["def"])
            self.objs.remove(o)
            self._add(prod, o["x"], o["z"], stack=3)
        return ok

    # --------------------------------------------------------------------- time
    def t_rimworld_step_game_ticks(self, p):
        r = MockGame.handle(self, "rimworld/step_game_ticks", p)
        self._sim()
        return r

    def _sim(self):
        self._sim_hive()
        self._sim_parasite()
        for o in list(self.objs):
            d = o["def"]
            if d.startswith("RM_Sekkulaath_") and o["first_hit"] is not None and d != "RM_Sekkulaath_Porter":
                if self.ticks - o["first_hit"] >= V.LIMB_FEELER["retreat_window"] and "feeler_noretreat" not in self.brk:
                    self.objs.remove(o)
                    if "retreat_drops_flesh" in self.brk:
                        self._add("RM_SeveredTentacleFlesh", o["x"], o["z"], stack=3)
            elif d == "RM_Sekkulaath_Porter" and self.ticks - o["born"] >= 900:
                self.objs.remove(o)
                if "porter_noloot" not in self.brk:
                    self._add("Silver", o["x"] + 1, o["z"], stack=20)
            elif d == "RM_Sekkulaath_Lash":
                while self.ticks >= o["next"]:
                    o["next"] += V.LIMB_LASH["lash_interval"]
                    rng = 999.0 if "lash_range_infinite" in self.brk else V.LIMB_LASH["lash_range"]
                    if "lash_dead" in self.brk:
                        continue
                    for q in self.pawns:
                        if not q["downed"] and math.hypot(q["x"] - o["x"], q["z"] - o["z"]) <= rng:
                            q["hediffs"]["Cut"] = 1.0
                            break
            elif d == "RM_LureStake" and o.get("bait") and not o.get("raided"):
                if self.ticks - o["staked_at"] >= 5000 and "raid_never" not in self.brk \
                        and (self.sb("twoFrontLureEnabled") or "raid_ignores_toggle" in self.brk):
                    o["raided"] = True
                    self.pawns.append({"id": "Pawn%d" % self._id(), "kindDef": "RM_Kurreth", "x": 5, "z": 5,
                                       "faction": "Hostile", "factionDef": SWARM, "hediffs": {}, "downed": False,
                                       "last_refusal": None, "refusals": 0})

    def _sim_hive(self):
        """RM_CompReactionSource detection (7, LOS assumed on the flat pad) + responder propagation (9 per hop)
        + rally, as the C# does: wild kurreth only, the intruder is the event's instigator."""
        if not (self.sb("reactionDetectionEnabled") or "hive_ignores_toggle" in self.brk) or "hive_blind" in self.brk:
            return
        wild = [q for q in self.pawns if q["kindDef"] == "RM_Kurreth" and q["faction"] is None]
        intruders = [q for q in self.pawns if q["kindDef"] != "RM_Kurreth" and q["faction"] is not None]
        for a in wild:
            if a.get("mental"):
                continue
            col = next((c for c in intruders if math.hypot(c["x"] - a["x"], c["z"] - a["z"]) <= 7), None)
            if col is None:
                continue
            reached, frontier = [a], [a]
            while frontier and "hive_no_hop" not in self.brk:
                cur = frontier.pop()
                for b in wild:
                    if b not in reached and not b.get("mental") and math.hypot(b["x"] - cur["x"], b["z"] - cur["z"]) <= 9:
                        reached.append(b)
                        frontier.append(b)
            for b in reached[:11]:
                b["mental"] = {"def": V.HIVE_RALLY, "causedByPawn": col["id"]}
            if "hive_silent" not in self.brk:
                self.msgs.append({"text": "The kurreth hive has noticed you. The alarm is spreading.", "reads": 0})


    def _sim_parasite(self):
        """RM_CompHiveParasite: a hungry glomvar kills the nearest calm wild kurreth within 12; never a colonist."""
        if not (self.sb("antHiveParasiteChamberEnabled") or "parasite_ignores_toggle" in self.brk):
            return
        for g in [q for q in self.pawns if q["kindDef"] == "RM_Glomvar" and not q.get("dead")]:
            if g.get("food", 1.0) > 0.4:
                continue
            if "parasite_bites_colonist" in self.brk:
                for c in self.pawns:
                    if c["faction"] is not None:
                        c["downed"] = True
            if "parasite_never" in self.brk:
                continue
            prey = [q for q in self.pawns if q["kindDef"] == "RM_Kurreth" and q["faction"] is None and not q.get("dead")
                    and math.hypot(q["x"] - g["x"], q["z"] - g["z"]) <= 12]
            if prey:
                prey[0]["dead"] = True
                g["food"] = 1.0
                if "parasite_rings_alarm" in self.brk:
                    self.msgs.append({"text": "The kurreth hive has noticed you.", "reads": 0})


def run(brk=(), log_lines=()):
    fd, path = tempfile.mkstemp(suffix=".log")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("Bridge token: x\n" + "\n".join(log_lines) + "\n")
    saved = getattr(game_paths, "PLAYER_LOG", None)
    game_paths.PLAYER_LOG = path
    try:
        game = FWGame(brk)
        s = FastSession(transport=MockTransport(game), strict=False)
        with s:
            res = runner.run_suite(V.suite, s, anchor=None, mod=None)
    finally:
        game_paths.PLAYER_LOG = saved
        os.unlink(path)
    out = {}
    for ch in res["chains"]:
        for c in ch["components"]:
            out["%s.%s" % (ch["name"], c["name"])] = (c["verdict"], c.get("detail") or "")
    return out


def reds(result):
    return sorted(k for k, (v, _) in result.items() if v == "FAIL")


CLEAN_FACTION = ("<Defs><FactionDef Name=\"BaseHidden\" Abstract=\"True\"><fixedName>the base</fixedName></FactionDef>"
                 "<FactionDef><defName>RM_FactionDef_KurrethSwarm</defName><fixedName>the swarm</fixedName><hidden>true</hidden></FactionDef>"
                 "<FactionDef ParentName=\"BaseHidden\"><defName>Inherits</defName><hidden>true</hidden></FactionDef></Defs>")


def guards_with(extra_files, leak_text=None, faction=CLEAN_FACTION):
    """Run ONLY the source_guards chain over a synthetic mod tree: a 12-entry compose file whose entries each
    have an About.xml, plus the Patches/ files in `extra_files`. Proves the two source guards can go red."""
    tmp = tempfile.mkdtemp()
    saved = (V._HERE, V._PATCH_DIR)
    try:
        mod = os.path.join(tmp, "FeverWood")
        os.makedirs(os.path.join(mod, "Patches"))
        entries = []
        for i in range(12):
            os.makedirs(os.path.join(tmp, "E%d" % i, "About"))
            with open(os.path.join(tmp, "E%d" % i, "About", "About.xml"), "w") as fh:
                fh.write("<ModMetaData><packageId>fake.e%d</packageId></ModMetaData>" % i)
            entries.append({"source": "E%d" % i, "wave": 0})
        with open(os.path.join(tmp, "Biomes.compose.json"), "w") as fh:
            json.dump({"compose_wave": 2, "entries": entries}, fh)
        for i in range(5):
            with open(os.path.join(mod, "Patches", "ok%d.xml" % i), "w") as fh:
                fh.write("<Patch><Operation Class=\"PatchOperationFindMod\"><mods><li>Ludeon.RimWorld</li></mods></Operation></Patch>")
        for fn, txt in extra_files.items():
            with open(os.path.join(mod, "Patches", fn), "w") as fh:
                fh.write(txt)
        os.makedirs(os.path.join(mod, "Defs", "BiomeDefs"))
        with open(os.path.join(mod, "Defs", "BiomeDefs", "RM_FeverWood.xml"), "w") as fh:
            fh.write("<Defs><BiomeDef><defName>RM_FeverWood</defName><preventGenSteps><li>ScatterShrines</li></preventGenSteps></BiomeDef></Defs>")
        os.makedirs(os.path.join(mod, "Defs", "FactionDefs"))
        with open(os.path.join(mod, "Defs", "FactionDefs", "RM_FactionDef_KurrethSwarm.xml"), "w") as fh:
            fh.write(faction)
        os.makedirs(os.path.join(mod, "Defs", "ThingDefs"))
        with open(os.path.join(mod, "Defs", "ThingDefs", "Things.xml"), "w") as fh:
            fh.write("<Defs>%s</Defs>" % "".join(
                "<ThingDef><defName>T%d</defName><label>thing %d</label><description>%s</description></ThingDef>"
                % (i, i, (leak_text if (leak_text and i == 7) else "a plain thing")) for i in range(30)))
        utp = os.path.join(tmp, "WildAnimals_FeverWood.xml")
        with open(utp, "w") as fh:
            fh.write("<Patch><!-- RM_FeverWood roster --></Patch>")
        V._UTINNI_FW_PATCH = utp
        V._HERE, V._PATCH_DIR = mod, os.path.join(mod, "Patches")
        game = FWGame()
        s = FastSession(transport=MockTransport(game), strict=False)
        only = V.Suite("FeverWood")
        only.chains = [(n, f) for n, f in V.suite.chains if n == "source_guards"]
        with s:
            res = runner.run_suite(only, s, anchor=None, mod=None)
        return dict(("%s.%s" % (ch["name"], c["name"]), c["verdict"]) for ch in res["chains"] for c in ch["components"])
    finally:
        V._HERE, V._PATCH_DIR = saved
        V._UTINNI_FW_PATCH = None
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    # -- the instrument itself ------------------------------------------------------------------
    check("source parse is clean", not V._ERRORS, V._ERRORS)
    for group, _, names, floor in V.GROUPS:
        check("floor met: %s (%d >= %d)" % (group, len(names), floor), len(names) >= floor)
    check("settings parsed (%d fields, %d toggles)" % (len(V.SETTING_FIELDS), len(V.BOOL_TOGGLES)),
          len(V.SETTING_FIELDS) >= 24 and len(V.BOOL_TOGGLES) == 24, V.BOOL_TOGGLES)  # +sillochAmbushEnabled, brathekBoresWood (cast pass 2), +broodRansomEnabled, +tentacleLimbLingerEnabled (FV-1); 2026-10-09: -naturalPlacementEnabled, +foulingWithdrawsLimbs, +kurrethTheftPerColumn, +twoFrontLureTrueFronts, +tentaclePoolsAreClusters, +kurrethLossFinalize
    check("sap-sucker kinds derived", [k for k, _, _, _ in V.SAP_KINDS] == ["RM_Vaulm", "RM_Drommath"], V.SAP_KINDS)
    check("harvest flora derived", len(V.FLORA_PRODUCTS) == 4, V.FLORA_PRODUCTS)
    check("crown plants derived", len(V.CROWN_PLANTS) >= 5, V.CROWN_PLANTS)
    check("genstep registrations derived", len(V.GENSTEPS_REGISTERED) == 3, V.GENSTEPS_REGISTERED)
    check("limb and tank numbers derived", V.LIMB_FEELER["hp"] > 0 and V.TANK_HP > 0 and V.TANK_OCCUPANT)
    decl = V.suite.components_declared()
    declared_toggles = set(c["toggle"] for c in decl if c["toggle"])
    check("the Mod Settings toggle floor is met", set(V.BOOL_TOGGLES) <= declared_toggles, sorted(set(V.BOOL_TOGGLES) - declared_toggles))

    # -- healthy world: every component passes --------------------------------------------------
    healthy = run()
    check("healthy: %d components all PASS" % len(healthy),
          healthy and all(v == "PASS" for v, _ in healthy.values()),
          {k: v for k, v in healthy.items() if v[0] != "PASS"})

    # -- each break turns its own component red -------------------------------------------------
    cases = [
        ("missing_def", {"defs_resolve.defs_resolve_items_ThingDef"}),
        ("donor_shadow", {"defs_resolve.defs_resolve_plants_ThingDef"}),
        ("name_missing", {"defs_resolve.defs_resolve_hediff_HediffDef", "defs_resolve.defs_named_in_code_exist"}),
        ("natural_gen", {"biome_roster.biome_flags_and_densities"}),
        ("zero_density", {"biome_roster.biome_flags_and_densities"}),
        ("roster_zero_commonality", {"biome_roster.wild_animals_wired"}),
        ("no_ext", {"biome_roster.hazard_and_hive_extensions_present"}),
        ("genstep_unregistered", {"registrations.gensteps_registered_on_their_map_generator"}),
        ("no_orders_designator", {"registrations.orders_designators_listed"}),
        ("no_recipe", {"registrations.suppressant_recipe_on_the_machining_table"}),
        ("no_harmony", {"registrations.failed_tame_hook_is_patched_in"}),
        ("settings_drift", {"settings.all_fields_at_shipped_defaults_and_assembly_loaded"}),
        ("toggle_stuck", {"settings.toggle_roundtrip_antHiveDungeonEnabled"}),
        ("bough_infertile", {"bough_soil.bough_soil_fertile_for_every_crown_plant"}),
        ("bough_heavy", {"bough_soil.bough_soil_fertile_for_every_crown_plant"}),
        ("ticker_never", {"rottable_items_tick.rottable_items_tick"}),
        ("feeler_nosever", {"tentacle_ladder.severe_damage_severs_the_limb_and_drops_flesh"}),
        ("no_flesh", {"tentacle_ladder.severe_damage_severs_the_limb_and_drops_flesh"}),
        ("no_kill_leavings", {"tentacle_ladder.a_killing_blow_still_drops_flesh"}),
        ("no_building_factor", {"tentacle_ladder.severe_damage_severs_the_limb_and_drops_flesh"}),
        ("feeler_noretreat", {"tentacle_ladder.mild_damage_retreats_without_dropping_anything"}),
        ("retreat_drops_flesh", {"tentacle_ladder.mild_damage_retreats_without_dropping_anything"}),
        ("porter_noloot", {"tentacle_porter.unmolested_porter_deposits_loot_then_withdraws"}),
        ("porter_survives_hit", {"tentacle_porter.a_hit_porter_vanishes_and_brings_nothing"}),
        ("porter_hit_still_deposits", {"tentacle_porter.a_hit_porter_vanishes_and_brings_nothing"}),
        ("lash_dead", {"tentacle_lash.lash_cuts_a_pawn_inside_its_range"}),
        ("lash_range_infinite", {"tentacle_lash.lash_spares_a_pawn_outside_its_range"}),
        ("brood_ignores_toggle", {"brood_ransom.with_the_brood_toggle_off_the_cask_says_nothing"}),
        ("tank_unbreakable", {"tank.a_heavy_hit_breaches_the_tank_and_the_juvenile_escapes_remembering"}),
        ("tank_no_memory", {"tank.a_heavy_hit_breaches_the_tank_and_the_juvenile_escapes_remembering"}),
        ("tank_light_breaks", {"tank.a_hit_below_the_threshold_keeps_the_tank_shut"}),
        ("tank_ignores_toggle", {"tank.with_the_tank_toggle_off_the_same_hit_breaks_nothing"}),
        ("foul_noconsume", {"foul_pool.job_consumes_the_configured_amount_and_announces_suppression",
                            "foul_pool.with_the_toggle_off_the_charge_is_spent_and_nothing_is_announced"}),
        ("foul_no_message", {"foul_pool.job_consumes_the_configured_amount_and_announces_suppression"}),
        ("foul_message_ignores_toggle", {"foul_pool.with_the_toggle_off_the_charge_is_spent_and_nothing_is_announced"}),
        ("sap_noop", {"sap_RM_Vaulm.RM_Vaulm_refuses_with_its_hediff_when_hurt"}),
        ("sap_no_cooldown", {"sap_RM_Vaulm.RM_Vaulm_refusal_is_cooldown_gated_not_a_roll",
                             "sap_RM_Drommath.RM_Drommath_refusal_is_cooldown_gated_not_a_roll"}),
        ("sap_one_shot", {"sap_RM_Vaulm.RM_Vaulm_refusal_is_cooldown_gated_not_a_roll",
                          "sap_RM_Drommath.RM_Drommath_refusal_is_cooldown_gated_not_a_roll"}),
        ("stake_no_chain", {"lure_stake.haul_to_stake_chains_the_downed_bait"}),
        ("stake_empty_wrong", {"lure_stake.an_empty_stake_reads_no_bait"}),
        ("stake_leaves_hediff", {"lure_stake.destroying_the_stake_frees_the_bait"}),
        ("flora_noop", {"flora_harvest.every_flora_yields_its_harvest_item"}),
        ("raid_ignores_toggle", {"lure_raid.with_the_lure_toggle_off_no_raid_comes"}),
        ("raid_never", {"lure_raid.a_staked_lure_draws_the_swarm"}),
        ("hive_blind", {"hive_rally.a_seen_intruder_rallies_the_whole_line"}),
        ("hive_no_hop", {"hive_rally.a_seen_intruder_rallies_the_whole_line"}),
        ("hive_silent", {"hive_rally.a_seen_intruder_rallies_the_whole_line"}),
        ("hive_ignores_toggle", {"hive_rally.with_detection_off_the_same_layout_rallies_nobody"}),
        ("parasite_never", {"hive_parasite.a_hungry_glomvar_eats_a_kurreth_unseen_and_ignores_the_colonist"}),
        ("parasite_bites_colonist", {"hive_parasite.a_hungry_glomvar_eats_a_kurreth_unseen_and_ignores_the_colonist"}),
        ("parasite_rings_alarm", {"hive_parasite.a_hungry_glomvar_eats_a_kurreth_unseen_and_ignores_the_colonist"}),
        ("parasite_ignores_toggle", {"hive_parasite.with_the_parasite_toggle_off_the_kurreth_lives"}),
        ("theft_kills", {"ant_theft.a_kurreth_column_carries_thornbugs_off_alive"}),
        ("theft_silent", {"ant_theft.a_kurreth_column_carries_thornbugs_off_alive"}),
        ("column_never", {"kurreth_column.a_theft_opens_a_column_camp_holding_the_animals"}),
        ("column_stuck", {"kurreth_column.an_unreached_column_moves_on_and_says_so"}),
        ("gate_stuck", {"oil_boil.gate_follows_the_temperature_setting"}),
        ("yield_flat", {"oil_boil.seepril_yield_doubles_while_boiling"}),
        ("haze_inert", {"oil_boil.a_spark_in_the_haze_flashes_and_burns_it_off"}),
    ]
    for brk, want in cases:
        got = reds(run((brk,)))
        check("break %-28s reddens exactly %s" % (brk, sorted(want)), set(got) == want, "got %s" % got)

    # the log chain: an error line naming our content fails it; an unrelated game-wide error does not
    bad = run(log_lines=["Config error in RM_LureStake: bad comp"])
    check("break log error naming RM_LureStake reddens the log component",
          reds(bad) == ["log_clean.player_log_names_no_feverwood_error"], reds(bad))
    other = run(log_lines=["Config error in SomeOtherMod_Thing: unrelated"])
    check("an error naming only another mod does not", not reds(other), reds(other))

    # FEVERWOOD_OIL_FLASH_BARE_GROUND_1: the shipped Flash lights bare ground; a source without the curve would not
    import tempfile
    check("shipped Flash lights a bare-ground hazed cell", flash_chance_on_bare_ground(OILBOIL_CS) > 0,
          flash_chance_on_bare_ground(OILBOIL_CS))
    src = open(OILBOIL_CS, encoding="utf-8").read()
    for label, text in [("no curve argument", src.replace(", null, RM_OilBoil.HazeFlashChance)", ", null)")),
                        ("curve zero at 0", src.replace("new CurvePoint(0f, 0.5f)", "new CurvePoint(0f, 0f)"))]:
        with tempfile.NamedTemporaryFile("w", suffix=".cs", delete=False, encoding="utf-8") as tf:
            tf.write(text)
        check("break %s -> bare ground never catches" % label, flash_chance_on_bare_ground(tf.name) == 0,
              flash_chance_on_bare_ground(tf.name))
        os.unlink(tf.name)

    # the two source guards, over a synthetic tree
    clean = guards_with({})
    check("source guards pass on a clean synthetic tree", set(clean.values()) == {"PASS"}, clean)
    folded = guards_with({"x.xml": '<Patch><Operation Class="PatchOperationAdd"><value><li MayRequire="fake.e3">a</li></value></Operation></Patch>'})
    check("break MayRequire naming a folded standalone mod reddens its guard only",
          [k for k, v in folded.items() if v == "FAIL"] == ["source_guards.no_mayrequire_names_a_folded_standalone_mod"], folded)
    topop = guards_with({"y.xml": '<Patch><Operation Class="PatchOperationAdd" MayRequire="some.mod"><xpath>/Defs</xpath></Operation></Patch>'})
    check("break top-level <Operation MayRequire> reddens its guard only",
          [k for k, v in topop.items() if v == "FAIL"] == ["source_guards.no_top_level_operation_carries_mayrequire"], topop)

    leak = guards_with({}, leak_text="canon dianoga tentacles are suckered")
    check("break a Star Wars name in free text reddens its guard only",
          [k for k, v in leak.items() if v == "FAIL"] == ["source_guards.free_text_names_no_canon_and_dianoga_patches_guarded"], leak)

    nameless = guards_with({}, faction=CLEAN_FACTION.replace("<fixedName>the swarm</fixedName>", ""))
    check("break a hidden faction with no fixedName/factionNameMaker reddens its guard only",
          [k for k, v in nameless.items() if v == "FAIL"] == ["source_guards.hidden_raider_factions_have_a_name_source"], nameless)
    orphan = guards_with({}, faction=CLEAN_FACTION.replace('<fixedName>the base</fixedName>', ""))
    check("break an inherited name source removed from the abstract parent reddens its guard only",
          [k for k, v in orphan.items() if v == "FAIL"] == ["source_guards.hidden_raider_factions_have_a_name_source"], orphan)
    found, bad = V.hidden_faction_findings([os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")])
    check("every shipped hidden FactionDef under src/ has a name source (%d found)" % found, found >= 5 and not bad, bad)

    print()
    if FAILS:
        print("FAILED: %d" % len(FAILS))
        for f in FAILS:
            print("  - " + f)
        return 1
    print("all FeverWood suite selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
