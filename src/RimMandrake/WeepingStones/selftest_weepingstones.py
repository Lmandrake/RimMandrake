#!/usr/bin/env python3
"""Offline selftest for the WeepingStones north-star suite (validation.py): no game, no bridge.

`WSGame` below is a small in-memory WeepingStones: the mod's own parsed Defs answer jawa/get_defs and
jawa/biome_probe, a zone list answers jawa/map_zones, and the five husbandry jobs and the flora harvest
change its world the way the C# does. It proves two things the first live run cannot prove on its own:

  1. a HEALTHY world passes every component (the suite's checks are not vacuously red), and
  2. each deliberate BREAK of the mod (a patch that matched nothing, a pen on dry floor, a job that does
     nothing, a toggle that gates nothing, a donor-shadowed def ...) turns exactly the component that
     exists for it red, so the checks can fail for the reason they are named for.

This is evidence about the SUITE, not about the game: the mock encodes the response shapes the suite
ASSUMES (the header of validation.py lists which are unproven live).
Run: python3 src/RimMandrake/WeepingStones/selftest_weepingstones.py
"""
import os
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
PRODUCT_OF_PLANT = dict(V.FLORA_PRODUCTS)


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def _kind_of(item_def):
    """RM_SkarrinBreedingStock -> RM_Skarrin ; RM_SkarrinMeat -> RM_Skarrin."""
    for suf in ("BreedingStock", "Meat", "Catch"):
        if item_def.endswith(suf):
            return item_def[:-len(suf)]
    return None


class WSGame(MockGame):
    PEN_ID = "architect-designator:zone:rm-designator-zoneadd-poolpen"
    GROW_ID = "architect-designator:zone:zone-add-growing"

    def __init__(self, brk=()):
        MockGame.__init__(self, sizex=200, sizez=200)
        self.brk = set(brk)
        self.zones = []                    # {"label","type","cells":set}
        self.toggle = True
        self.n_zone = 0
        self.known = {}                    # (DefType, name) -> packageId
        for group, deftype, names, _ in V.GROUPS:
            for n in names:
                self.known[(deftype, n)] = "mandrake.rm.biomes"
        for n in V.PAIRED:
            self.known[("ThingDef", n)] = "mandrake.rm.biomes"
        for k in ("ElectricStove", "FueledStove"):
            self.known[("ThingDef", k)] = "Ludeon.RimWorld"
        if "oasis_unwired" not in self.brk:
            self.known[("TileMutatorDef", "Oasis")] = "Ludeon.RimWorld.Odyssey"
        if "missing_def" in self.brk:
            plain = [n for n in V.GROUPS[2][2] if n not in V.PAIRED and n not in V.ROTTABLE_ITEMS][-1]
            del self.known[("ThingDef", plain)]
        if "donor_shadow" in self.brk:
            self.known[("ThingDef", V.GROUPS[3][2][0])] = "some.donor.mod"

    # ----------------------------------------------------------------- the dispatcher
    def handle(self, tool, p):
        p = p or {}
        fn = getattr(self, "t_" + tool.replace("/", "_"), None)
        if fn is not None:
            self._tick()
            return fn(p)
        return MockGame.handle(self, tool, p)

    def t_jawa_destroy_bulk(self, p):
        # the real tool removes every non-colonist pawn map-wide (what _reset_pad needs: destroy_batch leaves pawns)
        before = len(self.pawns)
        if p.get("filter") == "nonColonists" and not p.get("dryRun", True):
            self.pawns = [q for q in self.pawns if q.get("kindDef") == "Colonist"]
        return {"success": True, "matchedCount": before - len(self.pawns)}

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
            allf = {"fishTypes": {"freshwater_Common": dict((n, 1.0) for n in V.FISH_NAMES[:3]),
                                  "freshwater_Uncommon": dict((n, 1.0) for n in V.FISH_NAMES[3:])},
                    "maxFishPopulation": V.BIOME_SCALARS.get("maxFishPopulation"),
                    "modExtensions": ([] if "no_truce" in self.brk else [{"Class": "RM_WaterTruceExtension", "radius": 10}])
                                      + [{"Class": "RM_SunHeatExtension", "heatKind": "lowSun"}]}
            if "no_fish" in self.brk:
                allf["fishTypes"] = {}
        elif typ == "TileMutatorDef":
            allf = {"biomeWhitelist": ["Desert", "ExtremeDesert", V.BIOME], "workerClass": V.OASIS_WORKER}
        elif name in ("ElectricStove", "FueledStove"):
            allf = {"recipes": ["CookMealSimple"] + ([] if "no_recipe_patch" in self.brk else list(V.RECIPES))}
        elif name in V.ROTTABLE_ITEMS:
            allf = {"tickerType": "Never" if ("ticker_never" in self.brk and name == "RM_HulduFat") else "Rare"}
        return dict((k, v) for k, v in allf.items() if not want or k in want)

    def t_jawa_biome_probe(self, p):
        def live(roster):
            return [{"defName": n, "commonality": c} for n, (c, req) in sorted(roster.items())
                    if not req or req in V.ACTIVE_ON_TIER]
        animals, plants = live(V.BIOME_ANIMALS), live(V.BIOME_PLANTS)
        if "roster_zero_commonality" in self.brk:
            animals = [dict(a, commonality=0.0) if a["defName"] == "RM_Sillik" else a for a in animals]
        find = []
        for f in [f for f in str(p.get("find") or "").split(",") if f]:
            spawning = f in [a["defName"] for a in animals] or (f == "RM_Vhorrin" and "vhorrin_wild" in self.brk)
            find.append({"defName": f, "present": spawning, "state": "spawning" if spawning else "absent"})
        if "vhorrin_wild" in self.brk:
            animals.append({"defName": "RM_Vhorrin", "commonality": 0.1})
        return {"success": True, "biomes": [{
            "defName": p.get("biomes"), "generatesNaturally": "natural_gen" in self.brk,
            "animalDensity": 0.0 if "zero_density" in self.brk else V.BIOME_SCALARS.get("animalDensity"),
            "plantDensity": V.BIOME_SCALARS.get("plantDensity"),
            "wildAnimalCount": len(animals), "animalsListed": len(animals), "animals": animals,
            "wildPlantCount": len(plants), "plantsListed": len(plants), "plants": plants,
            "findResults": find}]}

    # ------------------------------------------------------------------- settings / UI
    def t_jawa_mod_settings_field(self, p):
        if p.get("field") in V.SLIDERS or p.get("field") in V.EH_SLIDERS:
            if not hasattr(self, "sliders"):
                self.sliders = {k: v[0] for k, v in list(V.SLIDERS.items()) + list(V.EH_SLIDERS.items())}
            if p.get("action") == "set":
                self.sliders[p["field"]] = float(p.get("value"))
            return {"success": True, "value": str(self.sliders[p["field"]])}
        if p.get("field") == V.EH_TOGGLE:
            if not hasattr(self, "eh_toggle"):
                self.eh_toggle = True
            if p.get("action") == "set":
                self.eh_toggle = str(p.get("value")) == "True"
            return {"success": True, "value": str(self.eh_toggle)}
        if p.get("field") != V.TOGGLE:
            return MockGame.handle(self, "jawa/mod_settings_field", p)
        if p.get("action") == "set":
            self.toggle = str(p.get("value")) == "True"
        return {"success": True, "value": str(self.toggle)}

    def t_rimworld_list_architect_categories(self, p):
        return {"success": True, "categories": [{"id": "cat-zone", "categoryDefName": "Zone"},
                                                {"id": "cat-orders", "categoryDefName": "Orders"}]}

    def t_rimworld_list_architect_designators(self, p):
        ds = [{"id": self.GROW_ID, "label": "Growing zone"}]
        if "no_designator" not in self.brk and (self.toggle or "toggle_ignored" in self.brk):
            ds.append({"id": self.PEN_ID, "label": "Pool pen"})
        return {"success": True, "designators": ds}

    # ------------------------------------------------------------------------- zones
    def t_rimworld_apply_architect_designator(self, p):
        if p.get("designatorId") != self.PEN_ID:
            return {"success": False}
        x, z, w, h = p["x"], p["z"], p["width"], p["height"]
        cells = set((cx, cz) for cx in range(x, x + w) for cz in range(z, z + h)
                    if self.terrain.get((cx, cz)) == "WaterShallow" or "pen_on_dry" in self.brk)
        if not cells:
            return {"success": False, "message": "no valid cells"}
        self.n_zone += 1
        self.zones.append({"label": "Pool pen %d" % self.n_zone, "type": "RM_Zone_PoolPen", "cells": cells})
        return {"success": True}

    def t_jawa_map_zones(self, p):
        if p.get("action") == "deleteZone":
            before = len(self.zones)
            self.zones = [z for z in self.zones if z["label"] != p.get("zone")]
            return {"success": before != len(self.zones)}
        return {"success": True, "zones": [{"label": z["label"], "type": z["type"], "cells": len(z["cells"])}
                                           for z in self.zones]}

    def _in_pen(self, x, z):
        return any((x, z) in zn["cells"] for zn in self.zones)

    # ------------------------------------------------------------- pawns, things, jobs
    def t_jawa_spawn_pawn(self, p):
        pid = "Pawn%d" % self._id()
        self.pawns.append({"id": pid, "kindDef": p["kindDef"], "x": p["x"], "z": p["z"],
                           "faction": None if p.get("faction") == "none" else "Player", "painting": False})
        return {"success": True, "pawns": [{"id": pid}]}

    def t_jawa_list_pawns(self, p):
        rows = list(self.pawns)
        if p.get("rect"):
            x, z, w, h = [int(v) for v in str(p["rect"]).split(",")]
            rows = [q for q in rows if x <= q["x"] < x + w and z <= q["z"] < z + h]
        return {"success": True, "pawns": rows}

    def t_jawa_list_things(self, p):
        r = MockGame.handle(self, "jawa/list_things", p)
        for row in r["things"]:
            d = row["def"]
            row["stackCount"] = 20 if d == "RM_VhorrinMeat" else (3 if d.endswith("Meat") else 1)
        return r

    def t_jawa_set_plants(self, p):
        for op in str(p["ops"]).split(";"):
            name, rect = op.split(":")
            x, z, w, h = [int(v) for v in rect.split(",")]
            if name == "CLEAR":
                continue
            for cx in range(x, x + w):
                for cz in range(z, z + h):
                    self.things.setdefault((cx, cz), []).append(name)
        return {"success": True}

    def _take_item(self, tid):
        d, rest = tid.split("#", 1)
        cx, cz = [int(v) for v in rest.split("_")]
        self.things[(cx, cz)].remove(d)
        return d, cx, cz

    def _pawn(self, pid):
        return next((q for q in self.pawns if q["id"] == pid), None)

    def t_jawa_ordered_job(self, p):
        if self._pawn(p.get("pawnId")) is None:
            return {"success": False}
        job, a = p.get("jobDef"), p.get("targetAId")
        ok = {"success": True, "accepted": True, "nowRunningRequested": True}
        if job == "RM_NetPoolBreeder" and "net_noop" not in self.brk:
            q = self._pawn(a)
            self.pawns.remove(q)
            self.things.setdefault((q["x"], q["z"]), []).append("%sBreedingStock" % q["kindDef"])
        elif job == "RM_StockPoolPen":
            d, cx, cz = self._take_item(a)
            bx, bz = p["targetBX"], p["targetBZ"]
            if (self._in_pen(bx, bz) or "stock_in_dry" in self.brk) and "stock_noop" not in self.brk:
                self.pawns.append({"id": "Pawn%d" % self._id(), "kindDef": _kind_of(d), "x": bx, "z": bz,
                                   "faction": None, "painting": False})
        elif job == "RM_FeedPoolPen" and "feed_noop" not in self.brk:
            self._take_item(a)
        elif job in ("RM_HarvestPoolPen", "RM_CullVhorrin") and "harvest_noop" not in self.brk:
            q = self._pawn(a)
            self.pawns.remove(q)
            self.things.setdefault((q["x"], q["z"]), []).append("%sMeat" % q["kindDef"])
        elif job == "Harvest" and "flora_noop" not in self.brk:
            d, cx, cz = self._take_item(a)
            self.things.setdefault((cx, cz), []).append(PRODUCT_OF_PLANT[d])
        return ok


def run(brk=(), log_lines=()):
    fd, path = tempfile.mkstemp(suffix=".log")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("Bridge token: x\n" + "\n".join(log_lines) + "\n")
    saved = getattr(game_paths, "PLAYER_LOG", None)
    game_paths.PLAYER_LOG = path
    try:
        game = WSGame(brk)
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


def main():
    # -- the instrument itself ------------------------------------------------------------------
    check("source parse is clean", not V._ERRORS, V._ERRORS)
    for group, _, names, floor in V.GROUPS:
        check("floor met: %s (%d >= %d)" % (group, len(names), floor), len(names) >= floor)
    check("convention pairs derived (%d)" % len(V.PAIRED), len(V.PAIRED) == 15, V.PAIRED)
    check("rottable items derived (%d)" % len(V.ROTTABLE_ITEMS), len(V.ROTTABLE_ITEMS) >= 10)
    check("flora products derived", [p for p, _ in V.FLORA_PRODUCTS] == ["RM_Bladderquill", "RM_Steamfrond", "RM_Dewgourd"],
          V.FLORA_PRODUCTS)
    check("stocked catch kinds derived", len(V.CATCH_KINDS) == 7, V.CATCH_KINDS)   # 7 with RM_MurrinCatch (2026-10-03)
    check("settings field named in the C# source",
          "stockedPoolsEnabled" in open(os.path.join(HERE, "Source", "RM_WeepingStonesSettings.cs"), encoding="utf-8").read())
    decl = V.suite.components_declared()
    check("the Mod Settings toggle floor is met", V.TOGGLE in set(c["toggle"] for c in decl if c["toggle"]))

    # -- healthy world: every component passes --------------------------------------------------
    healthy = run()
    check("healthy: %d components all PASS" % len(healthy),
          healthy and all(v[0] == "PASS" or (k in V.LIVE_ONLY_UNMEASURED and v[0] == "UNMEASURED")
                          for k, v in healthy.items()),
          {k: v for k, v in healthy.items() if v[0] != "PASS" and k not in V.LIVE_ONLY_UNMEASURED})

    # -- each break turns its own component red -------------------------------------------------
    cases = [
        ("missing_def", {"defs_resolve.defs_resolve_items"}),
        ("donor_shadow", {"defs_resolve.defs_resolve_plants"}),
        ("natural_gen", {"biome_roster.biome_flags_and_densities"}),
        ("zero_density", {"biome_roster.biome_flags_and_densities"}),
        ("roster_zero_commonality", {"biome_roster.wild_animals_wired"}),
        ("vhorrin_wild", {"biome_roster.vhorrin_never_ambient_and_probe_is_honest"}),
        ("no_fish", {"biome_roster.fish_types_wired"}),
        ("no_truce", {"biome_roster.water_truce_extension_present"}),
        ("no_recipe_patch", {"cuisine_wiring.recipes_on_both_stoves"}),
        ("ticker_never", {"cuisine_wiring.rottable_items_tick"}),
        ("no_designator", {"settings_and_designator.designator_listed_when_on"}),   # pen chains go UNMEASURED
        ("toggle_ignored", set()),   # a still-listed row is UNMEASURED (stale DLL vs cached listing), asserted below
        ("pen_on_dry", {"pen_zone.pen_refuses_dry_floor"}),
        ("oasis_unwired", {"oasis_flora.oasis_def_accepts_our_biome"}),
        ("net_noop", {"job_net.net_turns_wild_pawn_into_breeding_stock"}),
        ("stock_noop", {"job_stock.stock_releases_species_pawn_into_pen"}),
        ("stock_in_dry", {"job_stock_outside_pen.stock_outside_pen_releases_nothing"}),
        ("feed_noop", {"job_feed.feed_consumes_food_at_the_pen"}),
        ("harvest_noop", {"job_harvest.harvest_yields_species_meat", "job_cull.cull_yields_enormous_harvest"}),
        ("flora_noop", {"flora_%s.harvest_yields_%s" % (p, q) for p, q in V.FLORA_PRODUCTS}),
    ]
    um = run(("toggle_ignored",)).get("settings_and_designator.designator_hidden_when_off")
    check("break toggle_ignored goes UNMEASURED, not PASS", um is not None and um[0] == "UNMEASURED", "got %s" % (um,))
    for brk, want in cases:
        got = reds(run((brk,)))
        check("break %-24s reddens exactly %s" % (brk, sorted(want)), set(got) == want, "got %s" % got)

    # the log chain: an error line naming our content fails it; an unrelated game-wide error does not
    bad = run(log_lines=["Config error in RM_Murrin: lifeStages count mismatch"])
    check("break log error naming RM_Murrin reddens the log component",
          reds(bad) == ["log_clean.player_log_names_no_weepingstones_error"], reds(bad))
    other = run(log_lines=["Config error in SomeOtherMod_Thing: unrelated"])
    check("an error naming only another mod does not", not reds(other), reds(other))

    print()
    if FAILS:
        print("FAILED: %d" % len(FAILS))
        for f in FAILS:
            print("  - " + f)
        return 1
    print("all WeepingStones suite selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
