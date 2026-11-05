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
import json
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
        self._ws_init(brk)

    def _ws_init(self, brk=()):
        """The WeepingStones model's own state; also run on a generic MockGame adopted by northstar_plan.mock_extension."""
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
        if p["kindDef"] == "Colonist":
            self._handlers = getattr(self, "_handlers", set()) | {pid}
        self.pawns.append({"id": pid, "kindDef": p["kindDef"], "x": p["x"], "z": p["z"],
                           "faction": None if p.get("faction") == "none" else "Player", "painting": False})
        return {"success": True, "pawns": [{"id": pid}]}

    def t_jawa_list_pawns(self, p):
        # live row shape (JawaBenchTerrainTools.ListPawns): spawned/dead/downed are always present
        rows = [dict({"spawned": True, "dead": False, "downed": False}, **q) for q in self.pawns]
        if "handler_vanishes" in self.brk:     # LIVE 2026-10-07: every chain-spawned pawn left AllPawnsSpawned
            rows = [q for q in rows if not (q.get("kindDef") == "Colonist" and q["id"] in getattr(self, "_handlers", ()))]
        net_at = getattr(self, "_net_tick", None)
        if net_at is not None and self.ticks - net_at >= 400:     # WEEPINGSTONES_HANDLER_VANISHES_1: mid-job exits
            netter = getattr(self, "_netter", None)
            hx, hz = self.size[0] // 2 + V.PAD_OFFSET, self.size[1] // 2 + V.PAD_OFFSET      # the home pad's centre
            me = self._pawn(netter) or {}
            on_pad = abs(me.get("x", -999) - hx) <= V.PAD // 2 and abs(me.get("z", -999) - hz) <= V.PAD // 2
            if "handler_leaves_mid_job" in self.brk:
                rows = [q for q in rows if q["id"] != netter]
                self._log_once(netter, "%s left the map (mock: despawned mid-job)" % netter)
            elif "handler_dies_mid_job" in self.brk or ("pad_site_kills" in self.brk and on_pad):
                rows = [dict(q, dead=True, spawned=False, health={"hediffs": [{"label": "Bite", "def": "Bite"}]})
                        if q["id"] == netter else q for q in rows]
                self._log_once(netter, "%s died: Bite by Megascarab (mock)" % netter)
        if p.get("rect"):
            x, z, w, h = [int(v) for v in str(p["rect"]).split(",")]
            rows = [q for q in rows if x <= q["x"] < x + w and z <= q["z"] < z + h]
        return {"success": True, "pawns": rows}

    def _log_once(self, pid, line):
        """The game's Player.log line for a pawn's exit, written once, as the live game would during that step."""
        seen = self.__dict__.setdefault("_logged", set())
        if pid not in seen and getattr(game_paths, "PLAYER_LOG", None):
            seen.add(pid)
            with open(game_paths.PLAYER_LOG, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")

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
        if job == "RM_NetPoolBreeder":
            self._net_tick, self._netter = self.ticks, p.get("pawnId")
        if job == "RM_NetPoolBreeder" and "target_flees" in self.brk:
            self.pawns.remove(self._pawn(a))       # off the map with no stock (WEEPINGSTONES_NET_TARGET_FLEES_1's path)
        elif job == "RM_NetPoolBreeder" and "net_noop" not in self.brk:
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


LIVE_PROOFS = os.path.join(ROOT, "infrastructure", "state", "live_proofs", "WEEPINGSTONES_HANDLER_VANISHES_1.txt")


def _a1_rows():
    """The row ids live proof A1 hands prove_rows.py (the tokens after its results path), or None."""
    try:
        with open(LIVE_PROOFS, encoding="utf-8") as fh:
            lines = [ln for ln in fh if ln.startswith("live-proof A1:")]
    except OSError:
        return None
    if len(lines) != 1 or "prove_rows.py " not in lines[0]:
        return None
    return lines[0].split("prove_rows.py ", 1)[1].split()[1:]


def _prove_rows_exit(result, rows):
    """Run the real prove_rows.py on a results file built from a mock run, with A1's row list."""
    import subprocess
    bars = [{"id": k, "status": v[0], "evidence": v[1]} for k, v in result.items()]
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a1.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"bars": bars}, fh)
        return subprocess.run([sys.executable, os.path.join(ROOT, "src", "RimMandrake", "BlueDesert", "prove_rows.py"),
                               p] + list(rows), capture_output=True, timeout=60).returncode


def _a2_line():
    try:
        with open(LIVE_PROOFS, encoding="utf-8") as fh:
            lines = [ln for ln in fh if ln.startswith("live-proof A2:")]
    except OSError:
        return None
    return lines[0] if len(lines) == 1 else None


def _prove_job_net_exit(doc):
    """Run the real prove_job_net.py on a results doc (None = a file that is not JSON)."""
    import subprocess
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a2.json")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("not json{" if doc is None else json.dumps(doc))
        return subprocess.run([sys.executable, os.path.join(HERE, "prove_job_net.py"), p],
                              capture_output=True, timeout=60).returncode


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

    import northstar_plan as PLAN
    check("northstar_plan.MOCK_LIVE_ONLY is exactly validation.LIVE_ONLY_UNMEASURED",
          set(PLAN.MOCK_LIVE_ONLY) == set(V.LIVE_ONLY_UNMEASURED), (PLAN.MOCK_LIVE_ONLY, V.LIVE_ONLY_UNMEASURED))

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
    gone = run(("handler_vanishes",))
    jobs = [k for k in gone if k.startswith(("job_", "flora_")) and not k.split(".")[1].startswith("site_ready")]
    bad = [(k, gone[k][0]) for k in jobs if gone[k][0] != "UNMEASURED"]
    check("break handler_vanishes: every job/flora proof goes UNMEASURED, none PASS or FAIL (%d)" % len(jobs),
          len(jobs) >= 9 and not bad, "got %s" % bad)
    # -- WEEPINGSTONES_HANDLER_VANISHES_1: the stepped fate trace names WHEN and HOW a pawn left ----------------
    hf = dict((k, v) for k, v in healthy.items() if k.startswith("handler_fate."))
    check("healthy: handler_fate has its 5 components, all PASS", len(hf) == 5 and all(v[0] == "PASS" for v in hf.values()), hf)
    for brk, comp, needle, logged in (
            ("handler_leaves_mid_job", "net_job_handler_stays_on_map", "despawned alive", "left the map (mock"),
            ("handler_dies_mid_job", "net_job_handler_stays_on_map", "dead (corpse at", "died: Bite by Megascarab")):
        res = run((brk,))
        v, d = res.get("handler_fate." + comp, (None, ""))
        check("break %s: handler_fate.%s FAILs naming the tick and '%s'" % (brk, comp, needle),
              v == "FAIL" and needle in d and "at tick " in d and "step " in d, (v, d[:300]))
        check("break %s: the FAIL carries that step's Player.log tail line" % brk,
              "Player.log that step" in d and logged in d, d[-400:])
        ctl = res.get("handler_fate.control_no_job_nobody_vanishes", (None,))[0]
        check("break %s: the no-job control still PASSes (the exit is the job's)" % brk, ctl == "PASS", ctl)
        off = res.get("handler_fate.off_pad_control_net_job_nobody_vanishes", (None, ""))
        check("break %s: the off-pad control FAILs too (the job, not the site)" % brk,
              off[0] == "FAIL" and "off the pad" in off[1] and logged in off[1], off)
    ps = run(("pad_site_kills",))
    psv = dict((k.split(".", 1)[1], v[0]) for k, v in ps.items() if k.startswith("handler_fate."))
    check("break pad_site_kills: the on-pad job row FAILs while the off-pad and no-job controls PASS (the site)",
          psv.get("net_job_handler_stays_on_map") == "FAIL" and psv.get("off_pad_control_net_job_nobody_vanishes") == "PASS"
          and psv.get("control_no_job_nobody_vanishes") == "PASS", psv)
    check("break handler_dies_mid_job: the injury is named", "Bite" in run(("handler_dies_mid_job",)).get(
        "handler_fate.net_job_handler_stays_on_map", ("", ""))[1])
    tf = run(("target_flees",))
    check("break target_flees: only the target row reddens, the handler row PASSes",
          tf.get("handler_fate.net_job_target_leaves_only_as_stock", ("",))[0] == "FAIL"
          and tf.get("handler_fate.net_job_handler_stays_on_map", ("",))[0] == "PASS",
          dict((k, v[0]) for k, v in tf.items() if k.startswith("handler_fate.")))
    # the live A1 line must hand prove_rows EVERY handler_fate row: a row it omits can FAIL and A1 stays green
    a1 = _a1_rows()
    check("live proof A1 names every handler_fate component", a1 is not None and set(hf) <= set(a1),
          "missing %s" % sorted(set(hf) - set(a1 or ())))
    for label, res, want in (("healthy", healthy, 0), ("target_flees", tf, 1),
                             ("handler_leaves_mid_job", run(("handler_leaves_mid_job",)), 1),
                             # the blind checker's probe: every row PASS but the target, which despawned alive
                             ("healthy-but-target-despawned", dict(healthy, **{
                                 "handler_fate.net_job_target_leaves_only_as_stock":
                                     ("FAIL", "wild skarrin despawned alive")}), 1)):
        got = _prove_rows_exit(res, a1 or [])
        check("live proof A1's prove_rows on the %s results exits %d" % (label, want), got == want, got)
    # live proof A2 reads the job_net rows through prove_job_net.py: a refused/unmeasured run exits 2, never 1
    a2 = _a2_line()
    check("live proof A2 hands its results to prove_job_net.py", a2 is not None and "prove_job_net.py " in a2, a2)
    jn = lambda res: [{"id": k, "status": v[0], "evidence": v[1]} for k, v in res.items() if k.startswith("job_net.")]
    for label, doc, want in (
            ("healthy", {"bars": jn(healthy)}, 0),
            ("handler_vanishes", {"bars": jn(run(("handler_vanishes",)))}, 1),
            ("net_noop", {"bars": jn(run(("net_noop",)))}, 0),   # a FAIL is a reading, the clause is the handler
            # 2026-11-04T02:38 live: an UNKNOWN-outcome bridge call refused every preflight; bars=[]
            # the clause itself: a net row that names the handler gone fails A2 whatever its status
            ("net FAIL naming the handler gone", {"bars": [
                {"id": "job_net.site_ready_net", "status": "PASS"},
                {"id": "job_net.net_turns_wild_pawn_into_breeding_stock", "status": "FAIL",
                 "evidence": "handler Colonist is not alive on the map after the wait"}]}, 1),
            ("refused", {"refused": "site:dlc_status FAIL; site:weather FAIL", "bars": []}, 2),
            ("no job_net rows", {"bars": [{"id": "log_clean.x", "status": "PASS"}]}, 2),
            ("unreadable", None, 2)):
        got = _prove_job_net_exit(doc)
        check("live proof A2's prove_job_net on the %s results exits %d" % (label, want), got == want, got)
    hv = run(("handler_vanishes",)).get("handler_fate.control_no_job_nobody_vanishes", ("", ""))
    check("break handler_vanishes: the no-job control FAILs (the exit is not the job's)", hv[0] == "FAIL", hv)

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
