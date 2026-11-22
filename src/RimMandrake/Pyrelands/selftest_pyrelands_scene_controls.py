#!/usr/bin/env python3
"""T_SCENE_CONTROLS (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN): no part of the Pyrelands scenes is
UNMEASURED by construction.

Visit 2 (2026-11-20) found scene parts that stopped UNMEASURED on every visit because no bridge tool could run them. Each
was either given its read or removed as a control no bar needs (polish.md). This test, offline:

  1. construction: no `with _comp(t, "<part>")` body in validation.py STARTS with an unconditional `_unmeasured(`, and
     the removed controls are gone;
  2. tools: every bridge tool and argument the repaired parts send is declared by the companion (tool_schemas.json,
     which tool_snapshot_guard keeps equal to the JawaBench [Tool] sources);
  3. verdicts on a scripted game, the shipped part code run against it: the forced-Rain parts (sc_no_rain) PASS on a
     working mod and go FAIL or UNMEASURED on four planted faults; the GrowthRateFactor_Temperature verdict
     (sc_ash_watered) on worked reads; the roster toggle setter (sc_walk, sc_fire_sense) on a companion with and without
     the dictionary key.

The range it declares: the forced-Rain roll over storyteller (tutorial or not), mod postfix (working or absent), lock
(forcing or not) and gate (respected or ignored); the factor verdict over wet/dry/vanilla relations, hot and mild days,
unreadable reads and the unwatered far column. Left out: the live game itself (Stage 6 runs the parts; the commands are
in unrun.jsonl).

  python3 <this file> [--validation PATH] [--schemas PATH]     exit 0 = every check PASS, 1 = any FAIL
"""
import argparse
import ast
import contextlib
import importlib.util
import json
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NAME = "selftest_pyrelands_scene_controls"

# (part, scene) that must hold a real read now
REPAIRED = (("forced_rain_becomes_black_rain", "sc_no_rain"), ("forced_rain_gate_off_control", "sc_no_rain"),
            ("growth_rate_factor_temperature", "sc_ash_watered"), ("walk_roster_toggle", "sc_walk"),
            ("fire_sense_roster_toggle_off", "sc_fire_sense"), ("wild_plant_allowlist_day", "sc_populations"),
            ("roof_withers_roster_toggle_off", "sc_roof_withers"))
# controls removed as no bar needs them (polish.md)
REMOVED = ("same_seed_gate_off_map", "vanilla_ruins_unpainted", "giant_classic_restore_control",
           "forced_rain_vanilla_control", "venom_immunity_read", "herd_thirst_gate_off_map",
           "ash_ground_gate_off_regeneration")
# by construction still, each with the filed item that owns it (--strict ignores this list)
KNOWN_OPEN = {}
# tool -> the arguments the repaired parts send
TOOLS = {"jawa/thing_read": ("rect", "defName", "members"),
         "jawa/mod_settings_field": ("typeName", "action", "field", "key", "value"),
         "jawa/weather_set": ("weather", "lockWeather", "unlock"),
         "jawa/weather_roll_next": (),
         "jawa/storyteller_swap": ("storytellerDef",),
         "jawa/weather_get": (),
         "jawa/static_call": ("type", "method", "args"),
         "jawa/map_seed_foil": ("overrides", "censusGroup", "builtGroup")}

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" (%s)" % detail) if detail and not ok else ""))


def load_validation(path):
    mc = types.ModuleType("modcheck")

    class Suite(object):
        def __init__(self, name):
            self.chains = {}

        def chain(self, name):
            def deco(fn):
                self.chains[name] = fn
                return fn
            return deco

    class ExpectationFailed(Exception):
        pass

    mc.Suite, mc.Component, mc.ExpectationFailed = Suite, object, ExpectationFailed
    sys.modules.setdefault("modcheck", mc)
    sys.path.insert(0, HERE)
    spec = importlib.util.spec_from_file_location("pyre_validation_controls", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- 1. construction

def comp_bodies(text):
    """{part name: [first statement node, ...]} for every `with _comp(t, "<name>")` in the module."""
    out = {}
    for node in ast.walk(ast.parse(text)):
        if not isinstance(node, ast.With):
            continue
        for item in node.items:
            c = item.context_expr
            if (isinstance(c, ast.Call) and getattr(c.func, "id", None) == "_comp" and len(c.args) >= 2
                    and isinstance(c.args[1], ast.Constant) and isinstance(c.args[1].value, str)):
                out.setdefault(c.args[1].value, []).append(node.body)
    return out


def unconditional_unmeasured(body):
    s = body[0] if body else None
    return (isinstance(s, ast.Expr) and isinstance(s.value, ast.Call)
            and getattr(s.value.func, "id", None) == "_unmeasured")


def construction_checks(text, strict=False):
    bodies = comp_bodies(text)
    by_construction = sorted(n for n, bs in bodies.items() if any(unconditional_unmeasured(b) for b in bs))
    owned = {} if strict else KNOWN_OPEN
    loose = [n for n in by_construction if n not in owned]
    check("construction: no part of validation.py starts with an unconditional _unmeasured (%d parts read; %d owned by "
          "a filed item: %s)" % (len(bodies), len([n for n in by_construction if n in owned]),
                                 ", ".join("%s -> %s" % kv for kv in sorted(owned.items())) or "none"),
          not loose, "by construction: %s" % loose)
    for part, scene in REPAIRED:
        check("construction: %s (%s) is a part" % (part, scene), part in bodies, "absent")
    for part in REMOVED:
        check("construction: the removed control %s is gone" % part, part not in bodies, "still a part")


# ---------------------------------------------------------------- 2. tools

def tool_checks(schemas_path):
    tools = json.load(open(schemas_path))["tools"]
    for tool, args in sorted(TOOLS.items()):
        have = set((tools.get(tool) or {}).get("parameters") or [])
        missing = [a for a in args if a not in have]
        check("tools: %s declared with %s" % (tool, ", ".join(args) or "no arguments"),
              tool in tools and not missing, "absent" if tool not in tools else "missing %s" % missing)
    return tools


# ---------------------------------------------------------------- 3. the scripted game

class Game(object):
    """A Pyrelands site's weather decider and settings as the engine runs them (WeatherDecider.ChooseNextWeather:
    TutorSystem.TutorialMode && ClearWeatherAllowed -> Clear, then the forced weather, then the commonality roll; the
    PyrelandsNoOrdinaryRain postfix after it). Faults: postfix absent, lock not forcing, gate ignored."""
    BLACK = "RM_FE_BlackRain"

    def __init__(self, tools, postfix=True, lock_forces=True, gate_respected=True, natural="RM_FE_BlackRain",
                 dict_key=True):
        self.tools, self.postfix, self.lock_forces, self.gate_respected = tools, postfix, lock_forces, gate_respected
        self.natural, self.dict_key = natural, dict_key
        self.storyteller, self.lock, self.cur, self.age, self.tick = "Tutor", "Clear", "Clear", 0, 0
        self.settings = {"pyrelandsEnabled": True}
        self.roster = {}
        self.calls = []

    def gate(self):
        return self.settings["pyrelandsEnabled"] and self.roster.get("Pyrelands", True)

    def forced(self):
        return self.lock if self.lock_forces else None

    def choose(self):
        if self.storyteller == "Tutor":
            w = "Clear"
        elif self.forced():
            w = self.forced()
        else:
            w = self.natural
        if self.postfix and w == "Rain" and (self.gate() or not self.gate_respected):
            w = self.BLACK
        return w

    def wait(self, n):
        self.tick += n
        self.age += n
        if self.forced() and self.cur != self.forced() and self.age > 4000:
            self.cur, self.age = self.choose(), 0

    def call(self, tool, **kw):
        self.calls.append(tool)
        declared = set((self.tools.get(tool) or {}).get("parameters") or [])
        bad = [k for k in kw if k not in declared]
        if tool not in self.tools or bad:
            return {"success": False, "error": "unknown tool or argument %s %r" % (tool, bad)}
        if tool == "jawa/weather_get":
            return {"success": True, "weather": self.cur,
                    "conditions": [{"def": "WeatherController"}] if self.lock else []}
        if tool == "jawa/storyteller_swap":
            before = {"storytellerDef": self.storyteller}
            if kw.get("storytellerDef"):
                self.storyteller = kw["storytellerDef"]
            return {"success": True, "before": before, "after": {"storytellerDef": self.storyteller}}
        if tool == "jawa/weather_set":
            if kw.get("unlock"):
                self.lock = None
            if kw.get("weather"):
                if kw.get("lockWeather"):
                    self.lock = kw["weather"]
                self.cur, self.age = kw["weather"], 0
            return {"success": True, "after": self.cur, "lockInForce": self.lock is not None}
        if tool == "jawa/weather_roll_next":
            locked = self.forced()
            self.cur, self.age = self.choose(), 0
            return {"success": True, "after": {"weather": self.cur}, "lockedTo": locked}
        if tool == "jawa/mod_settings_field":
            if kw.get("key") is not None and not self.dict_key:
                return {"success": False, "error": "no key"}
            if kw.get("field") == "enabled" and kw.get("key"):
                self.roster[kw["key"]] = str(kw.get("value")).lower() == "true"
                return {"success": True}
            return {"success": True}
        return {"success": True}


def run_parts(V, game, fn):
    """Run validation part function `fn` against `game`, the harness around it stubbed -> {part: verdict}."""
    res = {}

    class T(object):
        upstream_failed = False
        components = []
        session = object()

        def bridge_call(self, tool, **kw):
            return game.call(tool, **kw)

        def _record(self, *a):
            pass

    @contextlib.contextmanager
    def comp(t, name, **kw):
        try:
            yield t
            res[name] = "PASS"
        except V._Unmeasured:
            res[name] = "UNMEASURED"
        except V.ExpectationFailed:
            res[name] = "FAIL"
        t.upstream_failed = False

    def static(t, ty, method, args=None):
        if method == "get_On":
            return str(game.gate())
        if method == "Enabled":
            return str(game.roster.get(args, True))
        return None

    stubs = {"_comp": comp, "_independent": lambda t: None, "_on_site": lambda t: None,
             "_wait": lambda t, n, fast=None: game.wait(n), "_set": lambda t, v: game.settings.update(v),
             "_ten_static": static, "_note": lambda t, label, data: None}
    saved = dict((k, getattr(V, k)) for k in stubs if hasattr(V, k))
    try:
        for k, v in stubs.items():
            setattr(V, k, v)
        fn(T())
    finally:
        for k, v in saved.items():
            setattr(V, k, v)
    return res


def rain_checks(V, tools):
    good = run_parts(V, Game(tools), V._r6_no_ordinary_rain)
    check("sc_no_rain: a working mod reads forced_rain_becomes_black_rain PASS and the gate-off control PASS",
          good.get("forced_rain_becomes_black_rain") == "PASS" and good.get("forced_rain_gate_off_control") == "PASS",
          good)
    faults = (
        ("the postfix absent (the forced roll stays Rain)", dict(postfix=False),
         {"forced_rain_becomes_black_rain": "FAIL"}),
        ("the gate ignored (black rain with the mechanics off)", dict(gate_respected=False),
         {"forced_rain_gate_off_control": "FAIL"}),
        ("a lock that does not force the roll (the natural roll is black rain)", dict(lock_forces=False),
         {"forced_rain_becomes_black_rain": "UNMEASURED", "forced_rain_gate_off_control": "UNMEASURED"}),
        ("a companion with no weather_roll_next", dict(), None),
    )
    for what, kw, want in faults:
        g = Game(tools if want is not None else dict((k, v) for k, v in tools.items() if k != "jawa/weather_roll_next"),
                 **kw)
        got = run_parts(V, g, V._r6_no_ordinary_rain)
        if want is None:
            ok = all(got.get(p) in ("FAIL", "UNMEASURED") for p in ("forced_rain_becomes_black_rain",
                                                                     "forced_rain_gate_off_control"))
        else:
            ok = all(got.get(p) == v for p, v in want.items())
        check("sc_no_rain planted: %s -> %s" % (what, want or "neither part PASS"), ok, got)
    g = Game(tools)
    run_parts(V, g, V._r6_no_ordinary_rain)
    check("sc_no_rain: the storyteller and the site's Clear lock are put back",
          g.storyteller == "Tutor" and g.lock == "Clear" and g.settings["pyrelandsEnabled"] is True,
          (g.storyteller, g.lock, g.settings))


def factor_checks(V):
    v = getattr(V, "growth_factor_verdict", None)
    check("sc_ash_watered: growth_factor_verdict exists", v is not None)
    if v is None:
        return
    top = 32.0

    def day(temp, wet, dry, van):
        return {"temp": temp, "wetFactor": wet, "dryFactor": dry, "vanillaDry": van, "dryTemp": temp}

    hot_good = day(38.0, [0.9, 0.9, 0.55], [0.55, 0.55, 0.55], 0.55)    # far wet column unwatered: reads the dry factor
    mild = day(25.0, [1.0] * 3, [1.0] * 3, 1.0)
    cases = (
        ("hot and mild days, wet roots cooling the watered columns", [hot_good, mild], True),
        ("wet roots doing nothing on a hot day", [day(38.0, [0.55] * 3, [0.55] * 3, 0.55)], False),
        ("the dry strip off vanilla's factor", [day(38.0, [0.9] * 3, [0.7] * 3, 0.55)], False),
        ("the watered strip below the dry strip", [mild, day(25.0, [0.8] * 3, [1.0] * 3, 1.0), hot_good], False),
        ("no hot day", [mild, mild], None),
        ("an unreadable factor", [hot_good, day(38.0, None, [0.55], 0.55)], None),
        ("an unread vanilla factor", [day(38.0, [0.9], [0.55], None)], None),
    )
    for what, reads, want in cases:
        ok, why = v({"reads": reads, "top": top})
        check("sc_ash_watered factor verdict: %s -> %s" % (what, want), ok is want, "%r %s" % (ok, why))
    ok, why = v(None)
    check("sc_ash_watered factor verdict: no reads at all -> None", ok is None, "%r %s" % (ok, why))


def roster_checks(V, tools):
    setter = getattr(V, "_ten_roster_set", None)
    check("sc_walk / sc_fire_sense: _ten_roster_set exists", setter is not None)
    if setter is None:
        return

    def run(game):
        res = {}

        def part(t):
            with V._comp(t, "roster"):
                V._ten_roster_set(t, False)
                if V._ten_roster_on(t) is not False or V._ten_gate_on(t) is not False:
                    V._fail("the roster toggle did not turn the gate off")
                V._ten_roster_set(t, True)
        res.update(run_parts(V, game, part))
        return res, game

    got, g = run(Game(tools))
    check("roster toggle: the dictionary-key setter turns the gate off and back on", got.get("roster") == "PASS"
          and g.roster.get("Pyrelands") is True, (got, g.roster))
    got, _ = run(Game(tools, dict_key=False))
    check("roster toggle planted: a companion without key= -> not PASS", got.get("roster") in ("FAIL", "UNMEASURED"), got)



# the visit-5 site census (design/concepts/Pyrelands/version/in_game/visit_5: 54545 of 54686 open plantable cells)
SITE_CENSUS = {"mutationsBefore": [], "ratio": 54545.0 / 54686, "covered": 54545, "plantable": 54686, "plantDensity": 16.0}
FOIL_TERRAIN = {"RM_FE_Ground_SoilRich": 2000, "RM_PyreAshDeep": 50000, "Sand": 5000, "Granite_Rough": 5500}
FOIL_FERT = {"RM_FE_Ground_SoilRich": 1.4, "RM_PyreAshDeep": 0.25, "Sand": 0.06, "Granite_Rough": 0.0}


def foil_reply(covered=20000, tile_hash=77, foil_hash=77, held=1.0, restored=16.0, ticks_after=1000, maps_after=1,
               biome="RM_Pyrelands", generator="Base_Player", success=True, terrain=None):
    """A jawa/map_seed_foil reply as the C# tool (JawaBenchSeedFoilTools.cs) shapes it; plantable cells 57000 - 0 built."""
    per = {"RM_FE_Plant_EmberGrass": covered * 7 // 10, "RM_FE_Plant_Quickgrass": covered - covered * 7 // 10}
    return {"success": success,
            "site": {"mapIndex": 0, "tile": 5, "tileHash": tile_hash, "generatorDef": "Base_Player", "biome": "RM_Pyrelands",
                     "sizeX": 250, "sizeZ": 250},
            "foil": {"seed": 1, "seedEqual": tile_hash == foil_hash, "tileHash": foil_hash, "generatorDef": generator,
                     "biome": biome, "sizeX": 250, "sizeZ": 250, "cells": 62500, "scanned": covered,
                     "countMatched": covered, "perDef": per, "terrain": dict(terrain or FOIL_TERRAIN), "terrainNull": 0,
                     "built": 0, "pawnsVanished": 30, "pawnsToWorld": 0},
            "overrides": [{"target": "BiomeDef/RM_Pyrelands", "field": "plantDensity", "value": 1.0, "before": 16.0,
                           "heldAfterGeneration": held, "restored": restored}],
            "mapCountBefore": 1, "mapCountAfter": maps_after, "currentMapRestored": True, "ticksBefore": 1000,
            "ticksAfter": ticks_after}


class FoilGame(Game):
    def __init__(self, tools, reply):
        Game.__init__(self, tools)
        self.reply = reply
        self.sent = None

    def call(self, tool, **kw):
        if tool == "jawa/map_seed_foil" and tool in self.tools:
            self.calls.append(tool)
            self.sent = kw
            bad = [k for k in kw if k not in set(self.tools[tool].get("parameters") or [])]
            return {"success": False, "error": "unknown argument %r" % bad} if bad else self.reply
        if tool == "jawa/get_defs":
            self.calls.append(tool)
            names = [d.split("/", 1)[1] for d in kw.get("defs", "").split(";") if "/" in d]
            return {"success": True, "defs": [{"defName": n, "fields": {"fertility": FOIL_FERT[n]}}
                                              for n in names if n in FOIL_FERT]}
        return Game.call(self, tool, **kw)


def foil_checks(V, tools):
    v = getattr(V, "density_foil_verdict", None)
    check("sc_grass_regreens: density_foil_verdict and cover_ratio exist", v is not None and hasattr(V, "cover_ratio"))
    if v is None:
        return
    # the census function itself: roster plants over fertile cells less buildings, None on no plantable cell
    c = V.cover_ratio({"RM_FE_Plant_EmberGrass": 3, "Plant_TreeOak": 9}, {"A": 4, "B": 6}, {"A": {"fertility": 1.0},
                                                                                           "B": {"fertility": 0}}, 1)
    check("sc_grass_regreens cover_ratio: roster plants only, infertile cells and buildings out -> (3, 3, 1.0)",
          c == (3, 3, 1.0), c)
    check("sc_grass_regreens cover_ratio: no plantable cell -> ratio None", V.cover_ratio({}, {}, {}, 0)[2] is None)

    def part(reply, tl=tools, census=SITE_CENSUS):
        V._GEN.clear()
        if census is not None:
            V._GEN["grass_census"] = dict(census)
        g = FoilGame(tl, reply)
        got = run_parts(V, g, V._r6_embergrass_regrow).get("plant_density_one_control_map")
        return got, g

    worst = {}
    cases = (
        ("the shipped density's foil: 20000 of 57000 cells at 1.0 under the site's 0.997", foil_reply(), None, "PASS"),
        ("planted: a foil census thicker than the site's (57000 of 57000)", foil_reply(covered=57000), None, "FAIL"),
        ("planted: a foil exactly equal to the site's share (54545 of 54686)",
         foil_reply(covered=54545, terrain={"RM_PyreAshDeep": 54686, "Granite_Rough": 7814}), None, "FAIL"),
        ("planted: a foil one cell thicker than the site (54546 of 54686)",
         foil_reply(covered=54546, terrain={"RM_PyreAshDeep": 54686, "Granite_Rough": 7814}), None, "FAIL"),
        ("a foil one cell thinner than the site (54544 of 54686): strictly below is the bar",
         foil_reply(covered=54544, terrain={"RM_PyreAshDeep": 54686, "Granite_Rough": 7814}), None, "PASS"),
        ("a companion without map_seed_foil (a stale DLL)", foil_reply(),
         dict((k, x) for k, x in tools.items() if k != "jawa/map_seed_foil"), "UNMEASURED"),
        ("a failed foil call", foil_reply(success=False), None, "UNMEASURED"),
        ("a foil of another seed", foil_reply(foil_hash=78), None, "UNMEASURED"),
        ("plantDensity re-asserted to 16 during generation", foil_reply(held=16.0), None, "UNMEASURED"),
        ("plantDensity left at 1.0 after the call", foil_reply(restored=1.0), None, "UNMEASURED"),
        ("a tick ran during the call", foil_reply(ticks_after=1001), None, "UNMEASURED"),
        ("the foil left on the map list", foil_reply(maps_after=2), None, "UNMEASURED"),
        ("a foil of another biome", foil_reply(biome="AridShrubland"), None, "UNMEASURED"),
        ("a foil of another generator", foil_reply(generator="Encounter"), None, "UNMEASURED"),
    )
    for what, reply, tl, want in cases:
        got, g = part(reply, tl if tl is not None else tools)
        check("sc_grass_regreens foil: %s -> %s" % (what, want), got == want, got)
    got, _ = part(foil_reply(), census=None)
    check("sc_grass_regreens foil: no site census earlier in the run -> UNMEASURED", got == "UNMEASURED", got)
    got, g = part(foil_reply())
    check("sc_grass_regreens foil: the call holds BiomeDef/RM_Pyrelands.plantDensity at 1.0",
          (g.sent or {}).get("overrides") == "BiomeDef/RM_Pyrelands.plantDensity=1.0", g.sent)
    os.environ[V.PLANT_FOIL_AT_SITE_ENV] = "1"
    try:   # the planted state: the foil at the site's own density regenerates the site (54545 of 54686) -> FAIL
        got, g = part(foil_reply(covered=54545, held=16.0, terrain={"RM_PyreAshDeep": 54686, "Granite_Rough": 7814}))
    finally:
        del os.environ[V.PLANT_FOIL_AT_SITE_ENV]
    check("sc_grass_regreens foil planted %s=1: the foil sent at the site's 16 and, equal to the site, read FAIL"
          % V.PLANT_FOIL_AT_SITE_ENV, got == "FAIL" and (g.sent or {}).get("overrides")
          == "BiomeDef/RM_Pyrelands.plantDensity=16.0", (got, g.sent))
    ok, why, reading = v(SITE_CENSUS, foil_reply(), dict((k, {"fertility": f}) for k, f in FOIL_FERT.items()))
    print("  foil reading: fixture margin %.3f (site %.3f, foil %.3f, limit: foil strictly below site), %d cases read"
          % (reading.get("margin") or 0, reading["site"]["ratio"], reading["foil"]["ratio"], len(cases) + 1))
    V._GEN.clear()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validation", default=os.path.join(HERE, "validation.py"))
    ap.add_argument("--schemas", default=os.path.join(ROOT, "src", "RimMandrake", "Utils", "northstar_driver",
                                                      "tool_schemas.json"))
    ap.add_argument("--strict", action="store_true", help="no by-construction part allowed, owned or not")
    a = ap.parse_args()
    text = open(a.validation).read()
    construction_checks(text, a.strict)
    tools = tool_checks(a.schemas)
    V = load_validation(a.validation)
    for fn in (lambda: rain_checks(V, tools), lambda: factor_checks(V), lambda: roster_checks(V, tools),
               lambda: foil_checks(V, tools)):
        try:
            fn()
        except Exception as e:   # a part that cannot run on the base is a FAIL here, never a crash with no verdict
            check("scripted run raised %s: %s" % (type(e).__name__, e), False)
    bad = RESULTS.count(False)
    print("%s: %d of %d checks failed" % (NAME, bad, len(RESULTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
