#!/usr/bin/env python3
"""Cauldron saved-site recipe, offline: SITES row == site_spec, retile/census read-backs, and the build ORDER --
nothing is saved when the clean read-back or the native census fails; a good build saves once, registers, reloads.
Every bridge call is a fake; test_site_saves' clean/check/save/load and Pyrelands' world steps are stubbed."""
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prep_site as PS  # noqa: E402
import biome_site as B  # noqa: E402  (prep_site put Utils/modcheck on sys.path)
import test_site_saves as TS  # noqa: E402

S = PS.S

FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append("%s %s" % (name, str(detail)[:300]))


check("SITES row single-sourced", TS.SITES.get("cauldron") == S.site_entry(), (TS.SITES.get("cauldron"), S.site_entry()))
check("STEPS mention the save and biome", S.SAVE in PS.STEPS and S.BIOME in PS.STEPS)
check("plan entry prints", PS.main([]) == 0)


class Fake(object):
    def __init__(self, natives=2, biome=S.BIOME, tile_biome=S.BIOME):
        self.log, self.natives, self.biome, self.tile_biome = [], natives, biome, tile_biome

    def call(self, tool, **p):
        self.log.append(tool)
        if tool == "jawa/map_info":
            return {"tile": 77, "mapId": 4, "mapBiome": self.biome, "outdoorTempNow": 12.0}
        if tool == "jawa/world_tile_set":
            tiles = [int(t) for t in p["tiles"].split(",")]
            return {"written": len(tiles), "tiles": [{"tile": t, "biome": self.tile_biome, "temperature": p["temperature"],
                                                       "hilliness": p["hilliness"]} for t in tiles]}
        if tool == "jawa/list_things":
            if p.get("defName") == "RM_Vexxiss":
                return {"things": [{"id": i} for i in range(self.natives)]}
            if p.get("defName") == S.VENT:
                return {"things": [{"id": 1}]}
            return {"things": []}
        if tool == "jawa/name_colony":
            return {"settlements": [{"tile": 77, "namedByPlayer": True}]}
        return {"success": True}


# retile read-back
check("retile ok", B.retile(Fake(), S, [1, 2, 3]) == 3)
try:
    B.retile(Fake(tile_biome="TemperateForest"), S, [1, 2])
    check("retile wrong biome raises", False)
except PS.SiteError:
    pass
# census / site problems
P, c = PS.site_problems(Fake(natives=2).call)
check("census counts natives", c["natives"]["RM_Vexxiss"] == 2 and c["probe"]["vents"] == 1 and not P, (P, c))
P, _c = PS.site_problems(Fake(natives=0).call)
check("no native is a problem", any("natives" in x for x in P), P)
P, _c = PS.site_problems(Fake(biome="TemperateForest").call)
check("wrong biome is a problem", any("biome" in x for x in P), P)

# build order, with every heavy step stubbed
NS = types.SimpleNamespace(
    fresh_quicktest_world=lambda s, sleep=None: {"seedString": "x"},
    strip_mutators=lambda s, c: None,
    generate=lambda s, c, size: {"mapId": 4},
    home=lambda s, m, n: {"colonists": ["a", "b", "c"]},
    retire_offsite_colonies=lambda s, c: {"retired": []},
    stock_food=lambda s, x, z, packs=None: {"packs": packs},
)
B._NS = NS
B.choose_tile = lambda s, spec, d, t: {"centre": 77, "patch": [77, 78], "lat": 10.0, "long": 3.0}
events = []
orig = {k: getattr(TS, k) for k in ("clean_map", "check_map", "save_site", "load_site", "backup_saves",
                                    "write_registry", "saves_stat")}


def run(check_ok=True, natives=2, load_ok=True):
    events[:] = []
    TS.clean_map = lambda call, prof: events.append("clean") or {"problems": []}
    TS.check_map = lambda call, site: events.append("check") or {"verified": check_ok, "problems": [] if check_ok else ["fog"]}
    TS.backup_saves = lambda d, b: events.append("backup") or 1
    TS.save_site = lambda call, name, d, sleep=None: events.append("save:" + name) or {"bytes": 10}
    TS.write_registry = lambda site, entry: events.append("registry:%s:%s" % (site, entry.get("loadVerified")))
    TS.load_site = lambda call, site, sleep=None: events.append("load") or {"verified": load_ok, "problems": []}
    TS.saves_stat = lambda d: {}
    d = tempfile.mkdtemp(prefix="cs_")
    try:
        return PS.build_site_save(Fake(natives=natives), d, saves_dir=d, sleep=lambda x: None)
    finally:
        for k, v in orig.items():
            setattr(TS, k, v)


rec = run()
check("good build order", events == ["clean", "check", "backup", "save:" + S.SAVE, "registry:cauldron:None", "load",
                                     "registry:cauldron:True"], events)
check("good build verified", rec.get("verified") is True)
for kw, why in (({"check_ok": False}, "unclean check"), ({"natives": 0}, "no natives")):
    try:
        run(**kw)
        check("raises on " + why, False)
    except PS.SiteError:
        check("never saved on " + why, not any(e.startswith("save:") for e in events), events)
rec = run(load_ok=False)
check("failed reload recorded, not verified", rec.get("verified") is False and events[-1] == "registry:cauldron:False", events)

print("FAIL: " + " | ".join(FAILS) if FAILS else "OK selftest_cauldron_site")
sys.exit(1 if FAILS else 0)
