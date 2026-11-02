#!/usr/bin/env python3
"""LeaningScrub saved-site recipe, offline: SITES row == site_spec, NATIVES == the BiomeDef's MayRequire-free
non-predator rows, the Lean probe (heading == 90 - sun bearing at save, the SAME heading off the reload), and the build ORDER --
nothing is saved when the clean read-back, the native census or the Lean fails; a good build saves once, registers,
reloads, and a reload whose heading moved is registered loadVerified False. Every bridge call is a fake."""
# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_leaningscrub_site_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import glob
import math
import os
import sys
import tempfile
import types
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prep_site as PS  # noqa: E402
import biome_site as B  # noqa: E402  (prep_site put Utils/modcheck on sys.path)
import test_site_saves as TS  # noqa: E402

S = PS.S
with open(os.path.join(HERE, "Source", "RM_TheLean.cs")) as _fh:
    _LEAN_CS = _fh.read()
FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append("%s %s" % (name, str(detail)[:300]))


check("SITES row single-sourced", TS.SITES.get(S.SITE) == S.site_entry(), (TS.SITES.get(S.SITE), S.site_entry()))
check("STEPS mention the save, biome and lean", S.SAVE in PS.STEPS and S.BIOME in PS.STEPS and S.LEAN_COMP in PS.STEPS)
check("plan entry prints", PS.main([]) == 0)

# NATIVES drift: the BiomeDef's MayRequire-free wildAnimals whose race is not a predator.
roster, pred = [], {}
for f in glob.glob(os.path.join(HERE, "Defs", "**", "*.xml"), recursive=True):
    root = ET.parse(f).getroot()
    for d in root.iter("BiomeDef"):
        if d.findtext("defName") == S.BIOME:
            roster = [e.tag for e in (d.find("wildAnimals") or []) if "MayRequire" not in e.attrib]
    for d in root.iter("ThingDef"):
        if d.find("race") is not None:
            pred[d.findtext("defName")] = (d.findtext("race/predator") or "false").strip().lower() == "true"
derived = tuple(a for a in roster if a in pred and not pred[a])
check("NATIVES == roster non-predators", derived == S.NATIVES and derived, (derived, S.NATIVES))


MODS = ["brrainz.harmony", "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology",
        "ludeon.rimworld.biotech", "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey",
        "mandrake.rm.biomes"]   # a donor-free running list with all five DLC (biome_site.DLC5)

class Fake(object):
    """The lean comp answers like RM_MapComponent_Lean: SunBearingDegrees 212.5 -> HeadingDegrees 237.5 (90 - bearing,
    mod 360) -> Downwind (cos, sin) of it. heading_skew moves HeadingDegrees off the sun (a broken wind); a reload
    that moves it is set from run(reload_moves_heading=True)."""
    def __init__(self, natives=2, biome=S.BIOME, applies=True, sun=212.5, heading_skew=0.0, downwind=None):
        self.log, self.natives, self.biome, self.applies = [], natives, biome, applies
        self.sun, self.skew, self.downwind = sun, heading_skew, downwind

    @property
    def heading(self):
        return ((90.0 - self.sun) % 360.0 + self.skew) % 360.0

    def call(self, tool, **p):
        self.log.append(tool)
        if tool == "jawa/running_mods":
            return {"success": True, "packageIds": list(getattr(self, "mods", None) or MODS)}
        if tool == "jawa/map_info":
            return {"tile": 77, "mapId": 4, "mapBiome": self.biome, "outdoorTempNow": 18.0}
        if tool == "jawa/world_tile_set":
            tiles = [int(t) for t in p["tiles"].split(",")]
            return {"written": len(tiles), "tiles": [{"tile": t, "biome": p["biome"], "temperature": p["temperature"],
                                                       "hilliness": p["hilliness"]} for t in tiles]}
        if tool == "jawa/list_things":
            if p.get("defName") == "RM_Fuzzrunner":
                return {"things": [{"id": i} for i in range(self.natives)]}
            return {"things": []}
        if tool == "jawa/map_comp_read":
            assert p["comp"] == S.LEAN_COMP
            vals = {}
            for m in p["members"].split(","):
                if m == "Applies":
                    vals[m] = str(self.applies)
                elif m == "SunBearingDegrees":
                    vals[m] = "%s" % self.sun
                elif m == "HeadingDegrees":
                    vals[m] = "%s" % self.heading
                elif m == "Downwind":
                    r = math.radians(self.heading)
                    vals[m] = self.downwind or "(%.2f, %.2f)" % (math.cos(r), math.sin(r))
            return {"success": True, "values": vals, "missing": []}
        if tool == "jawa/list_pawns":     # biome_site.clear_colonist_ground reads the colonists' cells
            return {"pawns": [{"id": "a", "isPlayer": True, "intelligence": "Humanlike", "x": 125, "z": 125}]}
        if tool == "jawa/name_colony":
            return {"settlements": [{"tile": 77}]}
        return {"success": True}


# probe: the save reads a sun-pointed heading; a reload with the same heading is clean, a moved one is not
f = Fake()
P, info = PS.probe(f.call, "save")
check("save probe reads the sun-pointed heading", not P and info["heading"] == 237.5 and info["applies"]
      and info["sunBearing"] == 212.5, (P, info))
P, _i = PS.probe(f.call, "reload", info)
check("reload with the same heading is clean", not P, P)
f.skew = 40.0
P, _i = PS.probe(f.call, "reload", info)
check("reload whose heading moved is a problem", any("heading" in x for x in P), P)
P, _i = PS.probe(Fake(heading_skew=90.0).call, "save")
check("a heading off the sun is a problem at save", any("sun" in x for x in P), P)
P, _i = PS.probe(Fake(downwind="(1.00, 0.00)").call, "save")
check("Downwind off the heading is a problem at save", any("Downwind" in x for x in P), P)
P, _i = PS.probe(Fake(downwind="garbage").call, "save")
check("unreadable Downwind is a problem at save", any("unreadable" in x for x in P), P)
P, _i = PS.probe(Fake(sun=0.0).call, "save")
check("due-north sun -> heading 90, clean", not P and _i["heading"] == 90.0, (P, _i))
check("save reads the PROPERTY, never the private field", "HeadingDegrees" in S.LEAN_LOCK_MEMBERS
      and "headingDegrees" not in S.LEAN_LOCK_MEMBERS + S.LEAN_RELOAD_MEMBERS)
check("the C# component still exposes the members the site reads",
      all(("public %s %s" % (ty, m)) in _LEAN_CS for ty, m in (("bool", "Applies"), ("Vector2", "Downwind"),
                                                              ("float", "HeadingDegrees"), ("float", "SunBearingDegrees"))))
P, _i = PS.probe(Fake(applies=False).call, "save")
check("Applies False is a problem", any("Applies" in x for x in P), P)
P, _i = PS.site_problems(Fake(biome="TemperateForest").call)
check("wrong biome is a problem", any("biome" in x for x in P), P)
P, _i = PS.site_problems(Fake(natives=0).call)
check("no native is a problem", any("natives" in x for x in P), P)
try:
    B.comp_read(lambda tool, **p: {"success": False, "message": "no comp"}, S.LEAN_COMP, ("Applies",))
    check("unreadable comp raises", False)
except B.SiteError:
    pass

# build order, every heavy step stubbed
B._NS = types.SimpleNamespace(
    fresh_quicktest_world=lambda s, sleep=None: {"seedString": "x"},
    strip_mutators=lambda s, c: None,
    generate=lambda s, c, size: {"mapId": 4},
    home=lambda s, m, n: {"colonists": ["a", "b", "c"]},
    retire_offsite_colonies=lambda s, c: {"retired": []},
    stock_food=lambda s, x, z, packs=None: {"packs": packs},
)
B.choose_tile = lambda s, spec, d, t: {"centre": 77, "patch": [77, 78], "lat": 10.0, "long": 3.0}
events = []
orig = {k: getattr(TS, k) for k in ("clean_map", "check_map", "save_site", "load_site", "backup_saves",
                                    "write_registry", "saves_stat")}


def run(check_ok=True, fake=None, reload_moves_heading=False):
    events[:] = []
    fk = fake or Fake()
    TS.clean_map = lambda call, prof: events.append("clean") or {"problems": []}
    TS.check_map = lambda call, site: events.append("check") or {"verified": check_ok, "problems": [] if check_ok else ["fog"]}
    TS.backup_saves = lambda d, b: events.append("backup") or 1
    TS.save_site = lambda call, name, d, sleep=None: events.append("save:" + name) or {"bytes": 10}
    TS.write_registry = lambda site, entry: events.append("registry:%s:%s" % (site, entry.get("loadVerified")))

    def _load(call, site, sleep=None):
        events.append("load")
        if reload_moves_heading:
            fk.skew = 40.0
        return {"verified": True, "problems": []}
    TS.load_site = _load
    TS.saves_stat = lambda d: {}
    d = tempfile.mkdtemp(prefix="ls_")
    try:
        return PS.build_site_save(fk, d, saves_dir=d, sleep=lambda x: None)
    finally:
        for k, v in orig.items():
            setattr(TS, k, v)


rec = run()
check("good build order", events == ["clean", "check", "backup", "save:" + S.SAVE, "registry:%s:None" % S.SITE, "load",
                                     "registry:%s:True" % S.SITE], events)
check("the recipe clears the plants around every colonist before the save (Yume on a dripping venomvine, 2026-10-16)",
      rec.get("colonistGround") == ["123,123,5,5"], rec.get("colonistGround"))
check("good build verified, heading recorded", rec.get("verified") is True
      and rec["census"]["probe"]["heading"] == 237.5, rec.get("census"))
for kw, why in (({"check_ok": False}, "unclean check"), ({"fake": Fake(natives=0)}, "no natives"),
                ({"fake": Fake(applies=False)}, "no lean")):
    try:
        run(**kw)
        check("raises on " + why, False)
    except B.SiteError:
        check("never saved on " + why, not any(e.startswith("save:") for e in events), events)
rec = run(reload_moves_heading=True)
check("moved heading on reload -> loadVerified False", rec.get("verified") is False
      and events[-1] == "registry:%s:False" % S.SITE, events)

print("FAIL: " + " | ".join(FAILS) if FAILS else "OK selftest_leaningscrub_site")
sys.exit(1 if FAILS else 0)
