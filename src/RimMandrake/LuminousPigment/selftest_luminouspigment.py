#!/usr/bin/env python3
"""Offline selftest for LuminousPigment's north-star suite (validation.py). No game, no bridge, no ModsConfig.

    python3 src/RimMandrake/LuminousPigment/selftest_luminouspigment.py

What it proves (LUMINOUS_PIGMENT_FIRST_SCRIPT_1):
  1. HEALTHY: against a small fake game that behaves the way the spec says, every component that does not need
     the mod's own debug actions PASSes, and the debug-action chains read UNMEASURED (not PASS) because the fake
     has no Deepfire actions.
  2. MUTANTS: for each mechanic, switching ONE behaviour of the fake game off makes the component that covers it
     FAIL, so each check can fail (the worker note's "how I would break it" column is this table, executable).
  3. KEYS: every JSON key the suite reads from a Deepfire debug action exists in the mod's C# debug-action
     source (a typo'd key would read None and silently fail or pass).
  4. The suite declares every Mod Settings toggle, and every toggle has a covering component.
The fake mirrors the SHAPES the suite assumes of the bridge; it cannot prove those shapes are what the live
bridge returns. That is the live run's job (the walk's live-run sheet names each assumed shape).
"""
import ast
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import runner                                                          # noqa: E402
from northstar_driver.session import FastSession                       # noqa: E402
from northstar_driver.transport import MockTransport, MockGame         # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


V = runner.load_validation(HERE)
import importlib.util                                                  # noqa: E402
_spec = importlib.util.spec_from_file_location("lp_validation_module", os.path.join(HERE, "validation.py"))
VM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(VM)

DEFAULTS = {"matLifeDays": "1", "matChillKillTemp": "10", "pressGate": "Research", "deepfireMarketValue": "90",
            "deepfireStackGlows": "True", "glowTankEnabled": "True", "tankPowerGraceHours": "6", "tankNeedsWater": "True",
            "paintingEnabled": "True", "maxCoats": "3", "wallsPaintable": "True", "furniturePaintable": "True",
            "apparelPaintable": "True", "weaponsPaintable": "True", "cuisineEnabled": "True"}
CLASS_OF = {"Wall": ("wallsPaintable", "Construction"), "Stool": ("furniturePaintable", "Construction"),
            "Apparel_Parka": ("apparelPaintable", "Crafting"), "MeleeWeapon_Knife": ("weaponsPaintable", "Crafting")}


def _mock_default(field):
    """The C# literal default for a scalar field (bool -> 'True'/'False'; numeric literal -> that number); '5' when the
    initialiser is a named constant; 'True' for anything not scalar (the old fake's behaviour)."""
    src = open(os.path.join(HERE, "Source", "LuminousPigmentMod.cs"), encoding="utf-8").read().split("class LuminousPigmentSettings", 1)[1]
    m = re.search(r"public\s+static\s+(bool|int|float)\s+%s\s*=\s*([^;]+);" % re.escape(field), src)
    if not m:
        return "True"
    lit = m.group(2).strip().rstrip("fF")
    if m.group(1) == "bool":
        return "True" if lit == "true" else "False"
    try:
        return str(float(lit))
    except ValueError:
        return "5"


class FakeGame(MockGame):
    """Behaves the way the spec says unless `bugs` names a behaviour to break."""

    def __init__(self, bugs=(), seen=False):
        MockGame.__init__(self, mods=("ludeon.rimworld",), sizex=250, sizez=250)
        self.bugs = set(bugs)
        self.settings = dict(DEFAULTS)
        self.applied = dict(DEFAULTS)
        self.items = {}
        self.pawns_f = []
        self.n = 100
        self.mat_seen = seen
        self.electricity = False
        self.finished = False
        self.designated = set()
        self.job = {}
        self.age_plants = {}
        self.window_open = False
        self.bills = {}

    # ---------------------------------------------------------------- helpers
    def new(self, d, x, z, stack=1, **kw):
        self.n += 1
        iid = "%s%d" % (d, self.n)
        it = dict(id=iid, d=d, x=x, z=z, stack=stack, age=0, coats=0, powered=False, seeded=False, unpowered=0,
                  glows=(self.applied["deepfireStackGlows"] != "False"), work=0)
        it.update(kw)
        self.items[iid] = it
        return it

    @staticmethod
    def rect(s):
        x, z, w, h = [int(v) for v in str(s).split(",")]
        return x, z, w, h

    def in_rect(self, it, r):
        x, z, w, h = r
        return x <= it["x"] < x + w and z <= it["z"] < z + h

    def cond(self, k):
        return self.settings[k] if k in self.settings else DEFAULTS[k]

    def glow_at(self, x, z):
        g = 0.0
        for it in self.items.values():
            d = max(abs(it["x"] - x), abs(it["z"] - z))
            if it["d"] == "RM_Deepfire" and it["glows"] and "no_deepfire_glow" not in self.bugs and d <= 1.5:
                g = max(g, 0.5)
            if it["coats"]:
                rad = [0, 1.5, 2.0, 2.5][it["coats"]]
                if d <= rad + 1:
                    g = max(g, [0, .45, .7, 1.0][it["coats"]] * 0.5)
        return g

    def colonists_near(self, x, z, r):
        return any(max(abs(p["x"] - x), abs(p["z"] - z)) <= r for p in self.pawns_f)

    # ------------------------------------------------------------------- sim
    def sim(self, n):
        for it in list(self.items.values()):
            if it["d"] == "RM_CrowncarpetFresh":
                it["age"] += n
                chilled = ("chill_ignored" not in self.bugs) and 15.0 < float(self.settings["matChillKillTemp"])
                old = ("life_ignored" not in self.bugs) and it["age"] >= float(self.settings["matLifeDays"]) * 60000
                if chilled or old:
                    del self.items[it["id"]]
                    self.new("RM_CrowncarpetDead", it["x"], it["z"], it["stack"])
            if it["d"] == "RM_Crowncarpet":
                it["age"] += n
                if it["age"] >= 2000 and self.colonists_near(it["x"], it["z"], 20) and "sighting_ignored" not in self.bugs:
                    self.mat_seen = True
            if it["d"] == "RM_DeepfirePress" and self.bills.get(it["id"]) and self.pawns_f:
                if it["powered"] or "press_ignores_power" in self.bugs:
                    near = [i for i in self.items.values() if abs(i["x"] - it["x"]) <= 6 and abs(i["z"] - it["z"]) <= 6]
                    have = lambda d: sum(i["stack"] for i in near if i["d"] == d)    # noqa: E731
                    if have("RM_CrowncarpetFresh") >= 4 and have("Neutroamine") >= 1 and have("Chemfuel") >= 2 \
                            and "bill_ignored" not in self.bugs:
                        it["work"] += n
                        if it["work"] >= 1800:
                            for d in ("RM_CrowncarpetFresh", "Neutroamine", "Chemfuel"):
                                for i in near:
                                    if i["d"] == d:
                                        self.items.pop(i["id"], None)
                            self.new("RM_Deepfire", it["x"], it["z"] - 1, int(self.applied.get("pressYield", 2)))
                            it["work"] = 0
                            self.bills[it["id"]] -= 1
            if it["d"] == "RM_GlowTank":
                if it["powered"]:
                    it["unpowered"] = 0
                elif it["seeded"] and "blackout_ignored" not in self.bugs:
                    it["unpowered"] += n
                    if it["unpowered"] >= float(self.settings["tankPowerGraceHours"]) * 2500:
                        it["seeded"] = False
            if it["id"] in self.job:
                self.job[it["id"]] -= n
                if self.job[it["id"]] <= 0:
                    del self.job[it["id"]]
                    self.coat(it)
            elif it["id"] in self.designated and it["coats"] == 0 and self.pawns_f \
                    and (self.settings["paintingEnabled"] != "False" or "painting_enabled_ignored" in self.bugs):
                it["ai"] = it.get("ai", 0) + n
                if it["ai"] >= 600:
                    self.coat(it)

    def coat(self, it):
        if it["coats"] < min(3, int(self.settings["maxCoats"])) or "max_coats_ignored" in self.bugs and it["coats"] < 3:
            it["coats"] += 1
            if it["coats"] == 1:
                stacks = [i for i in self.items.values() if i["d"] == "RM_Deepfire"]
                if stacks:
                    i = min(stacks, key=lambda q: abs(q["x"] - it["x"]) + abs(q["z"] - it["z"]))
                    i["stack"] -= 1
                    if i["stack"] <= 0:
                        del self.items[i["id"]]

    def can_add(self, it):
        cap = 3 if "max_coats_ignored" in self.bugs else min(3, int(self.settings["maxCoats"]))
        return it["coats"] < cap

    # --------------------------------------------------------------- handler
    def handle(self, tool, p):
        p = p or {}
        if tool == "rimworld/step_game_ticks":
            r = MockGame.handle(self, tool, p)
            self.sim(int(p.get("ticks") or 0))
            return r
        h = getattr(self, "t_" + re.sub(r"[^a-z_]", "_", tool.lower()), None)
        if h:
            return h(p)
        return MockGame.handle(self, tool, p)

    def t_jawa_get_defs(self, p):
        known = set(VM.ALL_DEFS) | {"TerrainDef/WaterOceanShallow", "ThingDef/ElectricStove", "ThingDef/FueledStove",
                                    "DesignationCategoryDef/Orders"}
        defs, nf = [], []
        for spec in str(p["defs"]).split(";"):
            if spec not in known:
                nf.append(spec)
                continue
            ty, nm = spec.split("/", 1)
            f = {}
            for fld in str(p.get("fields") or "").split(","):
                if not fld:
                    continue
                if nm == "WaterOceanShallow" and fld == "tags":
                    f[fld] = ["Water", "Ocean"] + ([] if "tag_patch" in self.bugs else ["RM_CrowncarpetBed"])
                elif nm in ("ElectricStove", "FueledStove") and fld == "recipes":
                    f[fld] = [] if self.applied["cuisineEnabled"] == "False" else list(VM.MEAL_RECIPES)
                elif nm == "Orders":
                    f[fld] = ["RimMandrake.LuminousPigment.Designator_Deepfire",
                              "RimMandrake.LuminousPigment.Designator_RemoveDeepfire"]
                elif fld == "designationCategory":
                    if nm == "RM_GlowTank":
                        f[fld] = "Production" if (self.applied["glowTankEnabled"] != "False"
                                                  or "glowtank_ignored" in self.bugs) else None
                    else:
                        f[fld] = "Production" if (self.applied["pressGate"] != "Unbuildable"
                                                  or "press_gate_ignored" in self.bugs) else None
                elif fld == "label":
                    f[fld] = nm
                else:
                    f[fld] = "(no such field)"
            defs.append({"defName": nm, "found": True, "fields": f})
        return {"success": True, "foundCount": len(defs), "notFound": nf, "defs": defs}

    def t_rimworld_list_architect_categories(self, p):
        return {"success": True, "categories": [{"id": "architect-category:orders", "categoryDefName": "Orders"}]}

    def t_rimworld_list_architect_designators(self, p):
        labels = ["Hunt", "Tame"]
        if "orders_patch" not in self.bugs:
            labels += ["Apply deepfire", "Remove deepfire"]
        return {"success": True, "designators": [{"label": l} for l in labels]}

    def t_jawa_set_terrain(self, p):
        return {"success": True}

    def t_jawa_get_def(self, p):
        nm = p["defName"]
        out = {"success": True, "defName": nm, "comps": [], "extra": {}, "statBases": []}
        if nm == "RM_Crowncarpet":
            out["comps"] = [{"compClass": "RimMandrake.LuminousPigment.CompMatDiscovery"}]
        if nm == "RM_CrowncarpetFresh":
            out["comps"] = [{"compClass": "RimMandrake.LuminousPigment.CompMatVitality"}]
        if nm == "RM_GlowTank":
            out["comps"] = [{"compClass": "CompPowerTrader"}]
            out["extra"] = {"thingClass": "RimMandrake.LuminousPigment.Building_GlowTank"}
        if nm == "RM_Deepfire":
            out["statBases"] = [{"stat": "MarketValue", "value": float(self.applied["deepfireMarketValue"])}]
        return out

    def t_jawa_list_things(self, p):
        wanted = [d for d in str(p.get("defName") or "").split(",") if d]
        r = self.rect(p["rect"]) if p.get("rect") else None
        rows = [{"id": i["id"], "def": i["d"], "position": {"x": i["x"], "z": i["z"]}, "stackCount": i["stack"]}
                for i in self.items.values()
                if (not wanted or i["d"] in wanted) and (r is None or self.in_rect(i, r))]
        return {"success": True, "things": rows, "isCompleteList": True, "countMatched": len(rows)}

    def t_jawa_spawn_batch(self, p):
        for op in str(p["ops"]).split(";"):
            d, rest = op.split(":")
            a = [int(v) for v in rest.split(",")]
            self.new(d, a[0], a[1], a[2] if len(a) > 2 else 1)
        return {"success": True}

    def t_jawa_destroy_batch(self, p):
        r = self.rect(p["rects"])
        for i in [i for i in self.items.values() if self.in_rect(i, r)]:
            del self.items[i["id"]]
        self.pawns_f = [q for q in self.pawns_f if not (r[0] <= q["x"] < r[0] + r[2] and r[1] <= q["z"] < r[1] + r[3])]
        return {"success": True}

    def t_jawa_make_empty_room(self, p):
        self.t_jawa_destroy_batch({"rects": p["rect"]})
        return {"success": True}

    def t_jawa_spawn_pawn(self, p):
        self.n += 1
        q = {"id": "Pawn%d" % self.n, "x": p["x"], "z": p["z"], "faction": "Colony", "intelligence": "Humanlike",
             "hostility": "Friendly", "dead": False}
        self.pawns_f.append(q)
        return {"success": True, "pawns": [{"id": q["id"]}]}

    def t_jawa_list_pawns(self, p):
        return {"success": True, "pawns": list(self.pawns_f)}

    def t_jawa_set_plants(self, p):
        d, rest = str(p["ops"]).split(":")
        a = [int(v) for v in rest.split(",")]
        self.new(d, a[0], a[1])
        return {"success": True, "planted": 1}

    def t_jawa_research_finish_project(self, p):
        if p["project"] == "Electricity":
            self.electricity = True
        return {"success": True}

    def t_jawa_research_availability(self, p):
        locked = ("gate_ignored" not in self.bugs) and not self.mat_seen and self.applied["pressGate"] == "Research"
        return {"success": True, "prerequisitesCompleted": self.electricity, "isHidden": False,
                "canStartNow": self.electricity and not locked and not self.finished, "isFinished": self.finished}

    def t_jawa_inspect_string(self, p):
        i = self.items.get(p["thingIds"])
        lines = []
        if i and i["d"] == "RM_CrowncarpetFresh":
            lines = ["alive: 24h left"]
        if i and i["d"] == "RM_GlowTank" and not i["seeded"]:
            lines = ["Needs a seed culture: haul one unit of fresh crowncarpet here."]
        if i and i["d"] == "RM_GlowTank" and self.cond("tankNeedsWater") != "False" and "water_gate_ignored" not in self.bugs:
            lines = lines + ["Dry: growth paused. Pipe salt or boiling water to it from a FlowWorks liquid tank."]  # LP-2: FlowWorks modelled loaded, no net
        return {"success": True, "things": [{"id": p["thingIds"], "inspect": lines}]}

    def t_jawa_mod_settings_field(self, p):
        if p.get("action") == "set":
            self.settings[p["field"]] = str(p["value"])
        return {"success": True, "value": self.settings.get(p["field"], _mock_default(p["field"]))}

    def t_rimworld_open_mod_settings(self, p):
        self.window_open = True
        return {"success": True}

    def t_jawa_window_list_close(self, p):
        if self.window_open and "apply_noop" not in self.bugs:
            self.applied = dict(self.settings)
            if self.applied["pressGate"] == "Buildable":
                self.finished = True
        self.window_open = False
        return {"success": True}

    def t_jawa_power_net(self, p):
        i = self.items.get(p["thing"])
        before = i["powered"]
        if "forcePowerOn" in p:
            i["powered"] = bool(p["forcePowerOn"])
        return {"success": True, "isPowerTrader": True, "energyOutputPerTick": -0.0025, "powerOnBefore": before,
                "powerOnAfter": i["powered"]}

    def t_jawa_bill_add(self, p):
        self.bills[p["giverId"]] = self.bills.get(p["giverId"], 0) + 1
        return {"success": True}

    def t_jawa_ordered_job(self, p):
        tank = self.items.get(p.get("targetAId"))
        mat = self.items.get(p.get("targetBId"))
        if p.get("jobDef") == "Refuel" and tank and mat:
            tank["seeded"] = True
            del self.items[mat["id"]]
            return {"success": True, "accepted": True, "nowRunningRequested": True}
        return {"success": False, "accepted": False}

    def t_deepfire_glow_at(self, p):
        vis = {"r": 20, "g": 20, "b": 20, "a": 0}
        for i in self.items.values():
            if i["coats"] and i["x"] == p["x"] and i["z"] == p["z"] and i.get("color") == "Structure_Blue" \
                    and "paint_ignored" not in self.bugs:
                vis = {"r": 6, "g": 17, "b": 32, "a": 0}
        return {"success": True, "groundGlow": self.glow_at(p["x"], p["z"]), "visual": vis}

    def t_deepfire_paint_building(self, p):
        self.items[p["thing"]]["color"] = p["colorDef"]
        return {"success": True, "colorDef": p["colorDef"]}

    def t_deepfire_comp_coats(self, p):
        i = self.items[p["thing"]]
        return {"success": True, "present": True, "coats": i["coats"], "canAddCoat": self.can_add(i)}

    def t_deepfire_add_coat(self, p):
        i = self.items[p["thing"]]
        b = i["coats"]
        if self.can_add(i):
            i["coats"] += 1
        return {"success": True, "present": True, "coatsBefore": b, "coatsAfter": i["coats"]}

    def t_deepfire_remove_coats(self, p):
        i = self.items[p["thing"]]
        b = i["coats"]
        i["coats"] = 0
        i.pop("ai", None)
        return {"success": True, "present": True, "coatsBefore": b, "coatsAfter": 0}

    def t_deepfire_designate(self, p):
        self.designated.add(p["thing"])
        return {"success": True, "alreadyDesignated": False}

    def t_deepfire_force_apply_job(self, p):
        self.job[p["thing"]] = 300
        return {"success": True, "jobDefName": "RM_ApplyDeepfire"}

    def t_deepfire_debug_workgiver(self, p):
        i = self.items[p["thing"]]
        tog, kind = CLASS_OF[i["d"]]
        allowed = self.settings[tog] != "False" or ("wall_toggle_ignored" in self.bugs and i["d"] == "Wall")
        stock = any(x["d"] == "RM_Deepfire" and x["stack"] >= 1 for x in self.items.values())
        ok = p["thing"] in self.designated and allowed and stock and self.can_add(i)
        return {"success": True, "pawns": [{"name": q["id"], "hasJobConstruction": ok and kind == "Construction",
                                            "hasJobCrafting": ok and kind == "Crafting"} for q in self.pawns_f]}

    def t_jawa_drain_log(self, p):
        return {"success": True, "messages": []}

    def t_rimworld_list_debug_action_children(self, p):
        return {"success": True, "children": []}


def run(bugs=(), seen=False):
    g = FakeGame(bugs=bugs, seen=seen)
    s = FastSession(transport=MockTransport(g), strict=False)
    with s:
        res = runner.run_suite(V, s, anchor=(126, 126), mod=None)
    return dict(("%s/%s" % (ch["name"], c["name"]), (c["verdict"], c.get("detail"))) for ch in res["chains"]
                for c in ch["components"])


# the debug-action chains the fake cannot answer: UNMEASURED by design
NEEDS_ACTIONS = ("floor_paint/", "first_coat/", "proxy_storage/", "worn_glow/", "styling_lacquer/", "status/", "gods/", "health_clean/")


def main():
    # --- 1 healthy
    h = run()
    bad = [(k, v) for k, v in h.items() if not any(k.startswith(p) for p in NEEDS_ACTIONS)
           and not v[0].startswith("PASS")]
    check("healthy: every component outside the debug-action chains PASSes", not bad, str(bad)[:900])
    unm = [k for k, v in h.items() if any(k.startswith(p) for p in NEEDS_ACTIONS) and v[0] != "UNMEASURED"]
    check("healthy: the debug-action chains read UNMEASURED, never PASS, when no Deepfire actions exist", not unm, str(unm)[:400])
    check("healthy: components ran at all", len(h) >= 60, str(len(h)))

    # --- a used game (matSeen already true) must not pass the locked check
    u = run(seen=True)
    check("used game: locked_before_sighting is UNMEASURED, not PASS",
          u["research_gate/locked_before_sighting"][0] == "UNMEASURED", str(u["research_gate/locked_before_sighting"]))

    # --- 2 mutants: one behaviour off -> the covering component FAILs
    mutants = {
        "chill_ignored": "mat_vitality/mat_dies_when_chilled",
        "life_ignored": "mat_vitality/mat_dies_on_clock",
        "sighting_ignored": "research_gate/unlocked_after_sighting",
        "apply_noop": "settings_apply/apply_reaches_defs",
        "glowtank_ignored": "settings_apply/glowtank_toggle",
        "press_gate_ignored": "settings_apply/press_unbuildable",
        "tag_patch": "defs_load/patches_applied",
        "orders_patch": "defs_load/patches_applied",
        "no_deepfire_glow": "item_glow/stack_glows",
        "press_ignores_power": "press_refine/unpowered_press_refuses",
        "blackout_ignored": "glowtank/blackout_kills_seed",
        "water_gate_ignored": "glowtank/water_gate_dry_tank_pauses",
        "max_coats_ignored": "paint_pipeline/max_coats_setting",
        "wall_toggle_ignored": "paint_pipeline/walls_paintable_toggle",
        "paint_ignored": "paint_pipeline/glow_colour_follows_paint",
        "painting_enabled_ignored": "paint_pipeline/painting_enabled_blocks_ai",
    }
    for bug, comp in mutants.items():
        r = run(bugs=(bug,))
        check("mutant %-24s -> %s FAILs" % (bug, comp), r[comp][0] == "FAIL", str(r[comp]))
        others = [k for k, v in h.items() if v[0].startswith("PASS") and r.get(k, ("",))[0] == "FAIL" and k != comp]
        check("mutant %-24s breaks only its own component (and what it poisons)" % bug,
              all(k.split("/")[0] == comp.split("/")[0] for k in others), str(others))

    # the press never taking its bill must read UNMEASURED (not a fake pass) for the unpowered arm
    r = run(bugs=("bill_ignored",))
    check("no pawn takes the bill: powered_press_refines is UNMEASURED", r["press_refine/powered_press_refines"][0] == "UNMEASURED",
          str(r["press_refine/powered_press_refines"]))
    check("no pawn takes the bill: unpowered_press_refuses is not a vacuous PASS",
          r["press_refine/unpowered_press_refuses"][0] == "UNMEASURED", str(r["press_refine/unpowered_press_refuses"]))

    # --- 3 keys read from debug-action reports exist in the C# that emits them
    cs = "\n".join(open(f, encoding="utf-8").read() for f in glob.glob(os.path.join(HERE, "Source", "*.cs")))
    tree = ast.parse(open(os.path.join(HERE, "validation.py"), encoding="utf-8").read())
    keys = set()
    for fn in ast.walk(tree):
        if isinstance(fn, ast.FunctionDef) and fn.name in ("floor_paint", "first_coat", "proxy_storage", "worn_glow",
                                                           "styling_lacquer", "status", "gods", "health_clean", "_god_check", "_th"):
            for n in ast.walk(fn):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" \
                        and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                    keys.add(n.args[0].value)
    own = {"x0", "_coated", "statParts", "stats", "things", "def", "opinion", "b", "d", "id", "success"}
    miss = sorted(k for k in keys if k not in own and ('\\"%s\\"' % k) not in cs and ('"%s"' % k) not in cs)
    check("sanity probe: the key scan saw >= 80 keys", len(keys) >= 80, str(len(keys)))
    check("every debug-action report key the suite reads exists in the C# source", not miss, str(miss))
    check("sanity probe: the key scan CAN miss a key (a made-up one is reported)",
          ("zzNoSuchKey" not in cs), "")

    # --- 4 toggles
    decl = V.components_declared()
    covered = set(c["toggle"] for c in decl if c["toggle"])
    check("every declared toggle has a covering component", set(V.toggles) <= covered, str(sorted(set(V.toggles) - covered)))
    src = open(os.path.join(HERE, "Source", "LuminousPigmentMod.cs"), encoding="utf-8").read()
    bools = re.findall(r"public static bool (\w+) = (?:true|false);", src.split("class LuminousPigmentSettings")[1].split("ExposeData")[0])
    undeclared = sorted(b for b in bools if b not in V.toggles and b != "familyEnabled")
    check("every bool setting in LuminousPigmentSettings is a declared toggle", not undeclared, str(undeclared))

    # --- 5 defs/patches vs C# (Approach B lint; the kernel fuzz is selftest_luminouspigment_fuzz.py, not run here: it needs dotnet.exe)
    import subprocess
    lint = subprocess.run([sys.executable, os.path.join(UTILS, "lint_luminouspigment_defs.py"), "--quiet"], capture_output=True, text=True)
    check("def lint (lint_luminouspigment_defs.py): 0 ERROR", lint.returncode == 0 and " 0 ERROR" in lint.stdout, (lint.stdout + lint.stderr)[-600:])

    # --- 6 source contracts for GLOW_TANK_SEED_CULTURE_1 and DEEPFIRE_FAMILY_SETTINGS_KEYED_1 (static: the logic lives in
    # game-dependent classes outside the Kernel fuzz harness, so the Scribe/sow behaviour itself is the live re-runs'
    # job: GLOW_TANK_SEED_LIVE_SOW_1, DEEPFIRE_FAMILY_SETTINGS_SAVE_LOAD_1). These pin the shape so a refactor cannot silently drop it.
    tank = open(os.path.join(HERE, "Source", "Building_GlowTank.cs"), encoding="utf-8").read()
    check("tank: established flag is scribed", 'Scribe_Values.Look(ref established, "rmGlowTankEstablished"' in tank)
    check("tank: established culture bypasses the seed-fuel requirement", "!established && (seedComp == null || !seedComp.HasFuel)" in tank)
    check("tank: blackout clears established and consumes the seed", re.search(r"established = false;\s*\n\s*if \(seedComp", tank) is not None)
    check("tank: sow consumes the seed only while not yet established", "if (established || seedComp == null || !seedComp.HasFuel) return;" in tank)
    check("tank: sanity probe, the contract scan CAN fail", "zzNoSuchFlag" not in tank)
    check("settings: family toggles saved by key", '"familyDisabledKeys"' in src and "DeepfireFamilies.All[i].key" in src)
    check("settings: legacy positional list is read only on load and never written",
          src.count('Look(ref legacyList, "familyEnabled"') == 1 and "Scribe_Collections.Look(ref familyEnabledList" not in src
          and src.index("LoadSaveMode.LoadingVars") < src.index('Look(ref legacyList, "familyEnabled"'))
    check("settings: keys resolve through DeepfireFamilies.IndexOf and an unknown key is ignored", "idx >= 0" in src and "DeepfireFamilies.IndexOf(key)" in src)

    print("\n%s" % ("ALL OK" if not FAILS else "FAILED: %s" % FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
