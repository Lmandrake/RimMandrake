#!/usr/bin/env python3
"""Contagion saved-site recipe, offline: SITES row == site_spec, NATIVES == the BiomeDef's MayRequire-free rows, the
sky probe (no Burn at save or reload), the food cache off every pad, and the build ORDER -- nothing is saved when the
clean read-back, the native census or the sky fails; a good build saves once, registers, reloads, and a reload into a
Burn is registered loadVerified False. Every bridge call is a fake."""
# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_contagion_site_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import glob
import importlib.util
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
FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append("%s %s" % (name, str(detail)[:300]))


check("SITES row single-sourced", TS.SITES.get(S.SITE) == S.site_entry(), (TS.SITES.get(S.SITE), S.site_entry()))
check("STEPS mention the save, biome and sky", S.SAVE in PS.STEPS and S.BIOME in PS.STEPS and S.SKY_COMP in PS.STEPS)
check("plan entry prints", PS.main([]) == 0)

roster = []
for f in glob.glob(os.path.join(HERE, "Defs", "BiomeDefs", "*.xml")):
    for d in ET.parse(f).getroot().iter("BiomeDef"):
        if d.findtext("defName") == S.BIOME:
            roster = [e.tag for e in (d.find("wildAnimals") or []) if "MayRequire" not in e.attrib]
check("NATIVES == roster", tuple(roster) == S.NATIVES and roster, (roster, S.NATIVES))

# Food cache (stock_food: 6 stacks at x FOOD_AT.x+25.., row FOOD_AT.z) clear of every validation.py pad.
_v = importlib.util.spec_from_file_location("contagion_validation_pads", os.path.join(HERE, "validation.py"))
try:
    V = importlib.util.module_from_spec(_v)
    _v.loader.exec_module(V)
    c = S.MAP_SIZE // 2
    fx, fz = S.FOOD_AT
    food = [(fx + 25 + i, fz) for i in range((S.FOOD_PACKS + 9) // 10)]
    half = V.PAD_SIZE // 2
    hit = [(n, cell) for n, (dx, dz) in V.PADS.items() for cell in food
           if abs(cell[0] - (c + dx)) <= half and abs(cell[1] - (c + dz)) <= half]
    check("food cache off every pad", not hit, hit)
except Exception as ex:                                    # noqa: BLE001 - an unreadable suite is a failure here
    check("validation.py PADS readable", False, ex)


DLC5 = ["ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
        "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey"]   # A1: "all five DLC" (every DLC is assumed)
MODS = ["brrainz.harmony", "ludeon.rimworld"] + DLC5 + ["mandrake.rm.biomes"]   # a donor-free running list

class Fake(object):
    def __init__(self, natives=2, biome=S.BIOME, burn=False):
        self.log, self.natives, self.biome, self.burn = [], natives, biome, burn

    def call(self, tool, **p):
        self.log.append(tool)
        if tool == "jawa/running_mods":
            return {"success": True, "packageIds": list(getattr(self, "mods", None) or MODS)}
        if tool == "jawa/map_info":
            return {"tile": 77, "mapId": 4, "mapBiome": self.biome, "outdoorTempNow": 25.0}
        if tool == "jawa/world_tile_set":
            tiles = [int(t) for t in p["tiles"].split(",")]
            return {"written": len(tiles), "tiles": [{"tile": t, "biome": p["biome"], "temperature": p["temperature"],
                                                       "hilliness": p["hilliness"]} for t in tiles]}
        if tool == "jawa/list_things":
            if p.get("defName") == "RM_Gawpsack":
                return {"things": [{"id": i} for i in range(self.natives)]}
            return {"things": []}
        if tool == "jawa/map_comp_read":
            assert p["comp"] == S.SKY_COMP
            return {"success": True, "missing": [],
                    "values": {"BurnActive": str(self.burn), "NextBurnTick": "180000", "TellsBegun": "False"}}
        if tool == "jawa/list_pawns":     # biome_site.clear_colonist_ground reads the colonists' cells
            return {"pawns": [{"id": "a", "isPlayer": True, "intelligence": "Humanlike", "x": 125, "z": 125}]}
        if tool == "jawa/name_colony":
            return {"settlements": [{"tile": 77}]}
        return {"success": True}


P, info = PS.probe(Fake().call, "save")
check("calm sky is clean", not P and info.get("NextBurnTick") == "180000", (P, info))
P, _i = PS.probe(Fake(burn=True).call, "save")
check("active Burn is a problem", any("Burn" in x for x in P), P)
P, _i = PS.site_problems(Fake(biome="TemperateForest").call)
check("wrong biome is a problem", any("biome" in x for x in P), P)
P, _i = PS.site_problems(Fake(natives=0).call)
check("no native is a problem", any("natives" in x for x in P), P)
P, _i = PS.site_problems(lambda tool, **p: {"success": False} if tool == "jawa/map_comp_read" else Fake().call(tool, **p))
check("unreadable sky is a problem, never clean", any("probe" in x for x in P), P)

B._NS = types.SimpleNamespace(
    fresh_quicktest_world=lambda s, sleep=None: {"seedString": "x"},
    strip_mutators=lambda s, c: None,
    generate=lambda s, c, size: {"mapId": 4},
    home=lambda s, m, n: {"colonists": ["a", "b", "c"]},
    retire_offsite_colonies=lambda s, c: {"retired": []},
    stock_food=lambda s, x, z, packs=None: events.append("food:%d,%d" % (x, z)) or {"packs": packs},
)
B.choose_tile = lambda s, spec, d, t: {"centre": 77, "patch": [77, 78], "lat": 10.0, "long": 3.0}
events = []
orig = {k: getattr(TS, k) for k in ("clean_map", "check_map", "save_site", "load_site", "backup_saves",
                                    "write_registry", "saves_stat")}


def run(check_ok=True, fake=None, burn_on_reload=False):
    events[:] = []
    fk = fake or Fake()
    TS.clean_map = lambda call, prof: events.append("clean") or {"problems": []}
    TS.check_map = lambda call, site: events.append("check") or {"verified": check_ok, "problems": [] if check_ok else ["fog"]}
    TS.backup_saves = lambda d, b: events.append("backup") or 1
    TS.save_site = lambda call, name, d, sleep=None: events.append("save:" + name) or {"bytes": 10}
    TS.write_registry = lambda site, entry: events.append("registry:%s:%s" % (site, entry.get("loadVerified")))

    def _load(call, site, sleep=None):
        events.append("load")
        fk.burn = burn_on_reload
        return {"verified": True, "problems": []}
    TS.load_site = _load
    TS.saves_stat = lambda d: {}
    d = tempfile.mkdtemp(prefix="cg_")
    try:
        return PS.build_site_save(fk, d, saves_dir=d, sleep=lambda x: None)
    finally:
        for k, v in orig.items():
            setattr(TS, k, v)


rec = run()
check("good build order", events == ["food:%d,%d" % S.FOOD_AT, "clean", "check", "backup", "save:" + S.SAVE,
                                     "registry:%s:None" % S.SITE, "load", "registry:%s:True" % S.SITE], events)
check("good build verified", rec.get("verified") is True)
for kw, why in (({"check_ok": False}, "unclean check"), ({"fake": Fake(natives=0)}, "no natives"),
                ({"fake": Fake(burn=True)}, "a Burn at save")):
    try:
        run(**kw)
        check("raises on " + why, False)
    except B.SiteError:
        check("never saved on " + why, not any(e.startswith("save:") for e in events), events)
for mods, why in ((MODS + ["sarg.alphabiomes"], "a retired donor running"), (["", None], "an unreadable mod list"),
                  ([m for m in MODS if m not in DLC5], "no DLC running"),
                  ([m for m in MODS if m != "ludeon.rimworld.odyssey"], "one DLC (odyssey) missing")):
    fk = Fake()
    fk.mods = mods
    try:
        run(fake=fk)
        check("raises on " + why, False)
    except B.SiteError:
        check("nothing built on " + why, not events and "jawa/world_tile_set" not in fk.log, (events, fk.log))
check("registry entry records the running mods", rec.get("mods") == MODS, rec.get("mods"))
check("SITES row and site_spec agree on v3", TS.SITES[S.SITE]["save"] == S.SAVE == "RM_TestSite_contagion_v3",
      (TS.SITES[S.SITE]["save"], S.SAVE))
_hd = tempfile.mkdtemp(prefix="cg_hdr_")
_st_atexit.register(_st_shutil.rmtree, _hd, True)


def _hdr(name, ids):
    f = _st_os.path.join(_hd, name)
    with open(f, "w", encoding="utf-8") as fh:
        fh.write("<savegame><meta><modIds>%s</modIds></meta></savegame>" % "".join("<li>%s</li>" % i for i in ids))
    return f


P, _ids = PS.header_problems(_hdr("ok.rws", MODS))
check("donor-free header is clean", not P and _ids == MODS, (P, _ids))
P, _ids = PS.header_problems(_hdr("v1.rws", MODS + ["sarg.alphabiomes", "oskarpotocki.vfe.insectoid2"]))
check("retired donor in the header is a problem", P and "alphabiomes" in P[0], P)
P, _ids = PS.header_problems(_hdr("nodlc.rws", [m for m in MODS if m not in DLC5]))
check("header with none of the five DLC is a problem", bool(P), (P, _ids))
for _d in DLC5:
    P, _ids = PS.header_problems(_hdr("no_%s.rws" % _d.split(".")[-1], [m for m in MODS if m != _d]))
    check("header missing %s is a problem" % _d, bool(P) and any(_d in x for x in P), (P, _ids))
P, _ids = PS.header_problems(_hdr("empty.rws", []))
check("empty header is a problem, never clean", P and "unreadable" in P[0], P)
P, _ids = PS.header_problems(_st_os.path.join(_hd, "absent.rws"))
check("missing save is a problem", P and "no save" in P[0], P)
rec = run(burn_on_reload=True)
check("Burn on reload -> loadVerified False", rec.get("verified") is False
      and events[-1] == "registry:%s:False" % S.SITE, events)

# A2 "no FinalizeLoading error": the REAL TS.load_site, fed a journal that logged one after the load, must not read
# verified, and prove() must carry it into A2 (exit 1). Control: the same load with a clean journal reads verified.
FINALIZE = "Error in Map.FinalizeLoading: System.NullReferenceException"


class LoadFake(Fake):
    def __init__(self, journal=(), **kw):
        Fake.__init__(self, **kw)
        self.journal, self.loaded = list(journal), False

    def call(self, tool, **p):
        if tool == "rimworld/get_ui_state":
            return {"programState": "Playing" if self.loaded else "Entry"}
        if tool == "rimworld/load_game":
            self.log.append(tool)
            self.loaded = True
            return {"success": True}
        if tool == "rimbridge/list_logs":
            if "afterSequence" not in p:
                return {"logs": [{"Sequence": 5, "Message": "baseline"}]}
            return {"logs": [{"Sequence": 6 + i, "Message": m} for i, m in enumerate(self.journal)] if self.loaded
                    else []}
        return Fake.call(self, tool, **p)


_qs = types.ModuleType("quiet_site")
_qs.MAP_ONLY = ()
_qs.site_profile_receipt = lambda S_, tag, controls=(): {"ok": True}
_nd, _nds = types.ModuleType("northstar_driver"), types.ModuleType("northstar_driver.session")


class _Sess(object):
    fake = None

    def __init__(self, strict=False):
        self.call = _Sess.fake.call

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


_nds.FastSession = _Sess
_nd.session = _nds
_saved_mods = {k: sys.modules.get(k) for k in ("quiet_site", "northstar_driver", "northstar_driver.session")}
_orig_ld = {k: getattr(TS, k) for k in ("read_registry", "call_session", "check_map")}
_orig_calm = TS.TG.calm_sky
sys.modules.update({"quiet_site": _qs, "northstar_driver": _nd, "northstar_driver.session": _nds})
TS.read_registry = lambda path=None: {}
TS.call_session = lambda call: call
TS.check_map = lambda call, site: {"verified": True, "problems": []}
TS.TG.calm_sky = lambda S_, size: {"ok": True}
try:
    for jr, want, why in (([], True, "clean journal"), ([FINALIZE], False, "FinalizeLoading error in the journal"),
                          (["Some unrelated error"], True, "unrelated error")):
        fk = LoadFake(journal=jr)
        ld = TS.load_site(fk.call, S.SITE, sleep=lambda x: None)
        check("load_site verified=%s on %s" % (want, why), ld.get("verified") is want
              and "rimworld/load_game" in fk.log, ld)
        if not want:
            check("load_site names the FinalizeLoading error", any("FinalizeLoading" in x for x in ld["problems"]), ld)
    _pd = tempfile.mkdtemp(prefix="cg_prove_")
    with open(_st_os.path.join(_pd, S.SAVE + ".rws"), "w", encoding="utf-8") as fh:
        fh.write("<savegame><meta><modIds>%s</modIds></meta></savegame>" % "".join("<li>%s</li>" % i for i in MODS))
    for jr, code, why in (([], 0, "clean load"), ([FINALIZE], 1, "FinalizeLoading error")):
        _Sess.fake = LoadFake(journal=jr)
        rc, prec = PS.prove(saves_dir=_pd)
        check("prove exit %d on %s" % (code, why), rc == code and not prec["A1"], (rc, prec))
        if code:
            check("prove A2 carries the FinalizeLoading error", any("FinalizeLoading" in x for x in prec["A2"]), prec)
        else:
            check("prove A2 clean on a clean load", prec["A2"] == [], prec)
    # GAP 1 (blind check 05d368ee): prove's A2 must carry the reload's own site reads, not just load_site's problems.
    for kw, word, why in (({"burn": True}, "Burn", "Burn active after reload"),
                          ({"biome": "TemperateForest"}, "biome", "wrong biome after reload"),
                          ({"natives": 0}, "natives", "no native alive after reload")):
        _Sess.fake = LoadFake(**kw)
        rc, prec = PS.prove(saves_dir=_pd)
        check("prove exit 1 on %s" % why, rc == 1 and not prec["A1"], (rc, prec))
        check("prove A2 names %s" % why, any(word in x for x in prec["A2"]), prec)
    # GAP 2: a dirty check_map read-back must make load_site unverified and reach prove's A2.
    TS.check_map = lambda call, site: {"verified": False, "problems": ["fog over the colony"]}
    try:
        ld = TS.load_site(LoadFake().call, S.SITE, sleep=lambda x: None)
        check("dirty check_map -> load_site verified False", ld.get("verified") is False
              and "fog over the colony" in ld["problems"], ld)
        _Sess.fake = LoadFake()
        rc, prec = PS.prove(saves_dir=_pd)
        check("dirty check_map -> prove exit 1, A2 names it", rc == 1 and "fog over the colony" in prec["A2"], (rc, prec))
    finally:
        TS.check_map = lambda call, site: {"verified": True, "problems": []}
    # GAP 3: A2 "loaded from the main menu" -- a game already Playing goes to the main menu BEFORE load_game.
    class PlayingFake(LoadFake):
        def __init__(self, **kw):
            LoadFake.__init__(self, **kw)
            self.menu = False

        def call(self, tool, **p):
            if tool == "rimworld/get_ui_state":
                return {"programState": "Playing" if (self.loaded or not self.menu) else "Entry"}
            if tool == "rimworld/go_to_main_menu":
                self.log.append(tool)
                self.menu = True
                return {"success": True}
            return LoadFake.call(self, tool, **p)

    pf = PlayingFake()
    ld = TS.load_site(pf.call, S.SITE, sleep=lambda x: None)
    lg = pf.log
    check("Playing at start -> go_to_main_menu before load_game",
          "rimworld/go_to_main_menu" in lg and "rimworld/load_game" in lg
          and lg.index("rimworld/go_to_main_menu") < lg.index("rimworld/load_game"), lg)
    check("Playing at start -> load still verified", ld.get("verified") is True, ld)
    ef = LoadFake()
    ld = TS.load_site(ef.call, S.SITE, sleep=lambda x: None)
    check("control: from Entry no go_to_main_menu", ld.get("verified") is True
          and "rimworld/go_to_main_menu" not in ef.log, (ld, ef.log))
except Exception as ex:                                   # noqa: BLE001 - a crash here is a failure, never a pass
    check("A2 FinalizeLoading cases ran", False, repr(ex))
finally:
    for k, v in _orig_ld.items():
        setattr(TS, k, v)
    TS.TG.calm_sky = _orig_calm
    for k, v in _saved_mods.items():
        if v is None:
            sys.modules.pop(k, None)
        else:
            sys.modules[k] = v

print("FAIL: " + " | ".join(FAILS) if FAILS else "OK selftest_contagion_site")
sys.exit(1 if FAILS else 0)
