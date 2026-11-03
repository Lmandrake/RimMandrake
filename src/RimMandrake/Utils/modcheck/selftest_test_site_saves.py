#!/usr/bin/env python3
"""selftest_test_site_saves -- offline checks of modcheck/test_site_saves.py against a small fake map (no game)."""
# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_test_site_saves_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_site_saves as T  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s %s" % ("PASS" if ok else "FAIL", name, detail if not ok else ""))
    if not ok:
        FAILS.append(name)


class Fake(object):
    """A map with a shrine (casket holding a sleeper, crate, trigger pair), a hive, a ruin wall, a warhead, fog, a
    hostile pawn the fog hides until the unfog, 3 colonists, rain off."""

    def __init__(self):
        self.things = [
            {"id": "AncientCryptosleepCasket1", "def": "AncientCryptosleepCasket", "x": 10, "z": 10, "faction": None},
            {"id": "AncientHermeticCrate2", "def": "AncientHermeticCrate", "x": 12, "z": 10, "faction": None},
            {"id": "Hive3", "def": "Hive", "x": 50, "z": 50, "faction": "Insect"},
            {"id": "Wall4", "def": "Wall", "x": 11, "z": 12, "faction": None},
            {"id": "Geyser5", "def": "SteamGeyser", "x": 90, "z": 90, "faction": None},
            {"id": "Shell6", "def": "Shell_AntigrainWarhead", "x": 13, "z": 11, "faction": None, "item": True},
            {"id": "RectTrigger7", "def": "RectTrigger", "x": 10, "z": 9, "faction": None, "ethereal": True},
            {"id": "SignalAction_Letter8", "def": "SignalAction_Letter", "x": 10, "z": 9, "faction": None, "ethereal": True},
            {"id": "Bed9", "def": "Bed", "x": 100, "z": 100, "faction": "PlayerColony"},
            {"id": "Turret10", "def": "Turret_MiniTurret", "x": 102, "z": 100, "faction": "PlayerColony",
             "factionName": "New Arrivals"},
        ]
        self.pawns = [{"id": "C%d" % i, "isPlayer": True, "intelligence": "Humanlike", "dead": False, "downed": False,
                       "hostile": False, "spawned": True} for i in range(3)]
        self.hidden = [{"id": "Fleshbeast1", "isPlayer": False, "intelligence": "Animal", "dead": False, "hostile": True}]
        self.fogged = 500
        self.log = []
        self.state = "Playing"

    def _rect_hit(self, rects, t):
        for r in rects.split(";"):
            x, z = [int(v) for v in r.split(",")[:2]]
            if (t["x"], t["z"]) == (x, z):
                return True
        return False

    def __call__(self, tool, **kw):
        self.log.append(tool)
        if tool == "jawa/list_things":
            rows = [t for t in self.things]
            if kw.get("defName"):
                want = set(kw["defName"].split(","))
                rows = [t for t in rows if t["def"] in want]
            if kw.get("group") == "BuildingArtificial":
                rows = [t for t in rows if not t.get("item") and not t.get("ethereal")]
            return {"success": True, "things": rows, "countMatched": len(rows), "isCompleteList": True}
        if tool == "jawa/destroy_batch":
            cats = set(kw.get("categories", "Plant").split(","))

            def kind(t):
                return "Ethereal" if t.get("ethereal") else ("Item" if t.get("item") else "Building")
            self.things = [t for t in self.things if not (self._rect_hit(kw["rects"], t) and (kind(t) in cats or "All" in cats))]
            return {"success": True}
        if tool == "jawa/destroy_bulk":
            n = len([p for p in self.pawns if not p["isPlayer"]])
            self.pawns = [p for p in self.pawns if p["isPlayer"]]
            return {"success": True, "matchedCount": n}
        if tool == "jawa/list_pawns":
            rows = self.pawns
            if kw.get("faction") == "hostile":
                rows = [p for p in rows if p.get("hostile")]
            return {"success": True, "pawns": rows}
        if tool == "jawa/set_fog":
            if kw.get("action") == "unfogAll":
                before, self.fogged = self.fogged, 0
                self.pawns.extend(self.hidden)          # the unfog releases what the fog held (r7/r8)
                self.hidden = []
                return {"success": True, "foggedCellsBefore": before, "foggedCellsNow": 0}
            return {"success": True, "foggedCellsNow": self.fogged}
        if tool == "jawa/map_info":
            return {"success": True, "tile": 77, "mapId": 0, "sizeX": 250, "sizeZ": 250, "mapBiome": "TemperateForest",
                    "outdoorTempNow": 18.0}
        if tool == "jawa/weather_get":
            return {"success": True, "weather": {"current": "Clear", "rainRate": 0.0}, "conditions": []}
        if tool == "jawa/weather_set":
            return {"success": True, "after": "Clear"}
        if tool == "jawa/map_fire":
            return {"success": True, "firesExtinguished": 0}
        if tool == "jawa/quiet_site":
            hives = [t for t in self.things if t["def"] == "Hive"]
            return {"success": True, "threats": [{"def": t["def"], "id": t["id"]} for t in hives]}
        if tool == "rimworld/get_ui_state":
            return {"programState": self.state}
        if tool == "rimworld/go_to_main_menu":
            self.state = "Entry"
            return {"success": True}
        if tool == "rimworld/load_game":
            self.load_args = dict(kw)
            self.state = "Playing"
            return {"success": True}
        return {"success": True}


# 1. the danger classifier
for d in ("AncientCryptosleepCasket", "AncientHermeticCrate", "Sarcophagus", "Hive", "EggSac", "GlowPod",
          "Shell_AntigrainWarhead", "PsychicAnimalPulser"):
    check("1 danger: %s" % d, T.is_danger_def(d))
for d in ("Wall", "Column", "Urn", "Slate", "SteamGeyser", "Bed", "AncientBarrel"):
    check("1 not danger: %s" % d, not T.is_danger_def(d))

# 2. a calm clean leaves nothing and releases the fog-held pawn into the sweep
f = Fake()
rec = T.clean_map(f, "calm", quiet=False)
check("2 calm clean reads back clean", not rec["problems"], rec["problems"])
check("2 casket + crate + warhead + hive vanished before the unfog",
      {"AncientCryptosleepCasket", "AncientHermeticCrate", "Shell_AntigrainWarhead", "Hive"} <= set(rec["dangerFound"]))
check("2 the casket went BEFORE the unfog",
      f.log.index("jawa/destroy_batch") < f.log.index("jawa/set_fog"))
check("2 the released fleshbeast was swept", rec["fog"].get("releasedByUnfog") == ["Fleshbeast1"], rec["fog"])
check("2 ruins gone; geyser, the player's bed and the player's turret (factionName is the colony's name) kept",
      sorted(t["def"] for t in f.things) == ["Bed", "SteamGeyser", "Turret_MiniTurret"], [t["def"] for t in f.things])
chk = T.check_map(f, "calm")
check("2 check_map verified on the cleaned map", chk["verified"], chk["problems"])

# 3. the danger profile keeps the ruins (Pyrelands reads them)
f = Fake()
rec = T.clean_map(f, "danger", quiet=False)
check("3 danger clean reads back clean", not rec["problems"], rec["problems"])
check("3 ruin wall kept", any(t["def"] == "Wall" for t in f.things))
check("3 casket gone", not any(t["def"] == "AncientCryptosleepCasket" for t in f.things))

# 4. check_map catches each dirt kind
f = Fake()
chk = T.check_map(f, "calm")
p = " | ".join(chk["problems"])
for word in ("fogged", "triggers", "danger", "ruins", "threat structures"):
    check("4 dirty map: %s named" % word, word in p, p)
check("4 dirty map not verified", not chk["verified"])
f = Fake()
T.clean_map(f, "calm", quiet=False)
f.pawns[0]["downed"] = True
f.pawns[1]["downed"] = True
chk = T.check_map(f, "calm")
check("4 two downed colonists fail the standing-colonist bar", any("standing colonist" in x for x in chk["problems"]))

# 5. a save is never overwritten
d = tempfile.mkdtemp()
open(os.path.join(d, T.SITES["calm"]["save"] + ".rws"), "w").close()   # the CURRENT calm save name (v2 since 2026-10-17), never a hard-coded version
try:
    T.save_site(lambda *a, **k: {}, T.SITES["calm"]["save"], d, sleep=lambda s: None)
    check("5 save refuses an existing name", False)
except RuntimeError as ex:
    check("5 save refuses an existing name", "never overwritten" in str(ex))
try:
    T.build(Fake(), "calm", d, d)
    check("5 build refuses before touching the game", False)
except RuntimeError as ex:
    check("5 build refuses before touching the game", "exists" in str(ex))

# 6. load goes through the main menu, then reads back
f = Fake()
T.clean_map(f, "calm", quiet=False)
f.log = []
T.read_registry = lambda path=None: {}
import quiet_site as QS  # noqa: E402
QS.site_profile_receipt = lambda *a, **k: {"problems": [], "error": None}
r = T.load_site(f, "calm", sleep=lambda s: None)
check("6 load via main menu before load_game", f.log.index("rimworld/go_to_main_menu") < f.log.index("rimworld/load_game"))
check("6 loaded clean map verified", r["verified"], r["problems"])
check("6 load ignores the save's mod header (fixture save, tier list differs)",
      getattr(f, "load_args", {}).get("ignoreModCompatibility") is True, getattr(f, "load_args", None))
try:
    T.load_site(f, "pyrelands")
    check("6 pyrelands has no save of its own here", False)
except ValueError:
    check("6 pyrelands has no save of its own here", True)

# 7. RIVER_SITE_REBUILD_FOR_FOURTEEN_MODS: river is v2 on fw_gss_sitting; prove refuses a header off the running list or
#    beyond the tier, refuses to BUILD on a superset, and leaves a failed load at the main menu
check("7 river site is v2", T.SITES["river"]["save"] == "RM_TestSite_river_v2", T.SITES["river"]["save"])
check("7 river fixture tier is fw_gss_sitting", T.SITES["river"].get("tier") == "fw_gss_sitting")
DLC = ["ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
       "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey"]
TIER = ["brrainz.harmony"] + DLC + ["brrainz.rimbridgeserver", "mandrake.rm.flowworks", "mandrake.rm.biomes"]


def fake_save(dirpath, name, ids):
    path = os.path.join(dirpath, name + ".rws")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("<?xml version=\"1.0\"?>\n<savegame><meta><gameVersion>1.6</gameVersion><modIds>%s</modIds></meta>"
                 "<game/></savegame>" % "".join("<li>%s</li>" % i for i in ids))
    return path


d = tempfile.mkdtemp()
v1 = fake_save(d, "v1like", TIER + ["oskarpotocki.vfe.insectoid2"])
P, ids = T.header_problems(v1, TIER, TIER)
check("7 header with a mod off the running list fails", any("running list lacks" in x and "insectoid2" in x for x in P), P)
check("7 header beyond the fixture tier fails", any("beyond its fixture tier" in x for x in P), P)
check("7 header reads every id", len(ids) == len(TIER) + 1, ids)
ok = fake_save(d, "fits", TIER)
check("7 header that fits the tier passes on a superset running list", T.header_problems(ok, TIER + ["x.y"], TIER)[0] == [])
check("7 missing DLC fails", any("lacks DLC" in x for x in T.header_problems(fake_save(d, "nodlc", TIER[:3]), TIER, TIER)[0]))
check("7 missing file fails", T.header_problems(os.path.join(d, "nope.rws"), TIER, TIER)[0] != [])
check("7 empty running list is unreadable, never a pass", any("unreadable" in x for x in T.header_problems(ok, [], TIER)[0]))


class ProveFake(Fake):
    def __init__(self, running):
        Fake.__init__(self)
        self.running = running

    def __call__(self, tool, **kw):
        if tool == "jawa/running_mods":
            self.log.append(tool)
            return {"success": True, "packageIds": list(self.running)}
        return Fake.__call__(self, tool, **kw)


T.tier_ids = lambda tier: list(TIER)
_built = []
_real_build, _real_load = T.build, T.load_site
T.build = lambda *a, **k: _built.append(a) or {"save": "x"}
f = ProveFake(TIER + ["sarg.extra"])
r = T.prove(f, "river", d, d, build_if_missing=True, sleep=lambda s: None)
check("7 prove refuses to build on a list beyond the tier", not _built and any("beyond tier" in x for x in r["A1"]), r["A1"])
check("7 prove does not load after A1 fails", "rimworld/load_game" not in f.log and not r["verified"])
f = ProveFake(TIER)
r = T.prove(f, "river", d, d, build_if_missing=True, sleep=lambda s: None)
check("7 prove builds when absent on the tier list", len(_built) == 1, _built)
fake_save(d, T.SITES["river"]["save"], TIER)
T.load_site = lambda call, site, **k: {"problems": ["the load logged Map.FinalizeLoading"], "verified": False}
f = ProveFake(TIER)
f.state = "Playing"
r = T.prove(f, "river", d, d, sleep=lambda s: None)
check("7 a failed load is not verified", not r["verified"] and r["A2"], r)
check("7 a failed load is left at the main menu", f.state == "Entry" and (r.get("menu") or {}).get("reached"), r.get("menu"))
T.load_site = lambda call, site, **k: {"problems": [], "verified": True}
f = ProveFake(TIER)
f.state = "Playing"
r = T.prove(f, "river", d, d, sleep=lambda s: None)
check("7 a fitting save that loads clean is verified, game left playing", r["verified"] and f.state == "Playing", r)
f = ProveFake(TIER)
r = T.prove(f, "river", d, d, sleep=lambda s: None, load=False)
check("7 prove --no-load judges A1 without loading", r["verified"] and "rimworld/load_game" not in f.log, r)
T.build, T.load_site = _real_build, _real_load
ep = open(os.path.join(HERE, "..", "..", "FlowWorks", "northstar", "extension_proof.py"), encoding="utf-8").read()
i, j = ep.find("TSS.to_main_menu("), ep.find("did not load clean")
check("7 extension_proof goes to the main menu before refusing a NOT CLEAN site", 0 < i < j, (i, j))


# 8. extension_proof's NOT CLEAN branch, driven: a fake bridge whose site load is NOT verified. The run must call
# rimworld/go_to_main_menu, refuse with SystemExit, and never reach the chains (runner.ensure_playing_map).
# A text find alone stayed green with the call commented out (blind check at adfadf5c99, gen 3).
import types  # noqa: E402


class EPFake(object):
    def __init__(self):
        self.log, self.state = [], "Playing"

    def call(self, tool, **kw):
        self.log.append(tool)
        if tool == "rimworld/go_to_main_menu":
            self.state = "Entry"
            return {"success": True}
        if tool == "rimworld/get_ui_state":
            return {"programState": self.state}
        return {"success": False}


def _drive_extension_proof(verified):
    ep_fake, reached = EPFake(), []

    class _Session(object):
        def __init__(self, **kw):
            pass

        def __enter__(self):
            return ep_fake

        def __exit__(self, *exc):
            return False

    def _ensure_playing_map():
        reached.append("ensure_playing_map")
        raise RuntimeError("chains reached")      # stop here: the suite itself is not under test

    fakes = {"rimdrive": types.SimpleNamespace(Session=_Session),
             "runner": types.SimpleNamespace(ensure_playing_map=_ensure_playing_map),
             "status": types.SimpleNamespace(mod_hash=lambda mod: "fakehash")}
    saved = {k: sys.modules.get(k) for k in fakes}
    real_load = T.load_site
    sys.modules.update(fakes)
    T.load_site = lambda call, site: {"verified": verified, "problems": [] if verified else ["FinalizeLoading NRE"],
                                      "load_s": 1, "ready_s": 1}
    outcome = None
    try:
        nsdir = os.path.join(HERE, "..", "..", "FlowWorks", "northstar")
        if nsdir not in sys.path:
            sys.path.insert(0, nsdir)
        import extension_proof as EP
        if sys.modules.get("test_site_saves") is not T:
            outcome = "test_site_saves resolved to a different module than the one patched"
        else:
            EP.main(["--live", "--site", "river", "--out", os.path.join(_st_tempfile.gettempdir(), "ep.json")])
            outcome = "returned"
    except SystemExit as ex:
        outcome = "SystemExit: %s" % ex
    except RuntimeError as ex:
        outcome = "RuntimeError: %s" % ex
    finally:
        T.load_site = real_load
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return ep_fake, reached, outcome


ef, reached, outcome = _drive_extension_proof(verified=False)
check("8 NOT CLEAN site: extension_proof calls rimworld/go_to_main_menu", "rimworld/go_to_main_menu" in ef.log,
      (ef.log, outcome))
check("8 NOT CLEAN site: extension_proof refuses (SystemExit naming the load)",
      str(outcome).startswith("SystemExit") and "did not load clean" in str(outcome) and "main menu reached" in str(outcome),
      outcome)
check("8 NOT CLEAN site: no chain runs", not reached, reached)
ef, reached, outcome = _drive_extension_proof(verified=True)   # sanity probe: the instrument sees the other branch
check("8 CLEAN site: no main menu, the chains are reached",
      "rimworld/go_to_main_menu" not in ef.log and reached == ["ensure_playing_map"], (ef.log, reached, outcome))

# 9. A retired donor in the header fails even when the running list carries it (the contract's 'refuses a retired
#    donor' clause on its own, not hidden behind 'off the running list' or 'beyond the tier').
from retired_mods import is_retired  # noqa: E402
RET = "oskarpotocki.vfe.insectoid2"
check("9 sanity: the probe id is retired", is_retired(RET))
check("9 sanity: no TIER id is retired", not [i for i in TIER if is_retired(i)], [i for i in TIER if is_retired(i)])
P9, _ = T.header_problems(fake_save(d, "retired_on_run", TIER + [RET]), TIER + [RET], None)
check("9 retired donor on the running list, no tier: header fails", any("retired donor" in x and RET in x for x in P9), P9)
check("9 ...and fails ONLY as retired (not as off-list)", not any("running list lacks" in x for x in P9), P9)
P9t, _ = T.header_problems(fake_save(d, "retired_in_tier", TIER + [RET]), TIER + [RET], TIER + [RET])
check("9 retired donor inside running list AND tier: header still fails", P9t and all("retired donor" in x for x in P9t), P9t)


# 10. A2 river edges: the live probe test_site_river_edges reads >= SITES['river']['minRiverEdges'] moving edges on the
#     current map; a map whose river reaches < 2 edges (ends in the sea, or no river at all) fails.
import test_site_river_edges as RE  # noqa: E402


class RingFake(object):
    def __init__(self, moving, size=250, ok=True, short=False):
        self.moving, self.size, self.ok, self.short = moving, size, ok, short

    def __call__(self, tool, **kw):
        if tool == "jawa/map_info":
            return {"sizeX": self.size, "sizeZ": self.size}
        if tool == "jawa/get_terrain_batch":
            if not self.ok:
                return {"success": False, "message": "refused"}
            n = self.size
            ops = ["Sand:%s" % r for r in kw["rects"].split(";")]
            if self.short:
                ops = ops[:1]
            line = {"south": "40,0,3,1", "north": "40,%d,3,1" % (n - 1), "west": "0,40,1,3", "east": "%d,40,1,3" % (n - 1)}
            ops += ["WaterMovingShallow:%s" % line[e] for e in self.moving]
            return {"success": True, "ops": ";".join(ops)}
        raise AssertionError(tool)


check("10 river spec asks for >= 2 edges", T.SITES["river"].get("minRiverEdges") == 2, T.SITES["river"].get("minRiverEdges"))
P10, rd = RE.river_edge_problems(RingFake(["south", "north"]), "river")
check("10 two moving edges hold", P10 == [] and rd.get("edges") == {"south": 3, "north": 3}, (P10, rd))
P10, rd = RE.river_edge_problems(RingFake(["west"]), "river")
check("10 river ending in the sea (one edge) fails", any("1 edge" in x for x in P10), (P10, rd))
P10, rd = RE.river_edge_problems(RingFake([]), "river")
check("10 no river at all fails", any("0 edge" in x for x in P10), (P10, rd))
check("10 unreadable ring fails, never zero", RE.river_edge_problems(RingFake(["south", "north"], ok=False), "river")[0] != [])
check("10 a partial ring read fails", any("ring cells" in x for x in
                                          RE.river_edge_problems(RingFake(["south", "north"], short=True), "river")[0]))
check("10 wrong-size map (not the site) fails", RE.river_edge_problems(RingFake(["south", "north"], size=200), "river")[0] != [])
check("10 a site with no river requirement is refused, not passed", RE.river_edge_problems(RingFake(["south", "north"]), "calm")[0] != [])

# 11. The live proof file wires both: A2 runs the edge probe after a verified prove.
_LP = os.path.join(HERE, "..", "..", "..", "..", "infrastructure", "state", "live_proofs", "RIVER_SITE_REBUILD_FOR_FOURTEEN_MODS.txt")
_a2 = [ln for ln in open(_LP, encoding="utf-8").read().splitlines() if ln.startswith("live-proof A2:")]
check("11 live A2 proves the load, then reads river edges",
      len(_a2) == 1 and "test_site_saves.py prove river" in _a2[0] and "&& " in _a2[0]
      and "test_site_river_edges.py river" in _a2[0].split("&&", 1)[1], _a2)

# 12. Tier gate (live 2026-11-03: prove ran on another item's 28-mod game and the round wrote FAIL): the gate reads the
#     RUNNING list against the site's tier and exits 2 (UNMEASURED, restage) on a wrong game, never 1; both live lines
#     run it first, and the proof file names live-mods so the round restages on a list holding the tier's mods.
import test_site_tier_gate as TG  # noqa: E402

import modset_builder as _MB  # noqa: E402  (section 7 fakes T.tier_ids; resolve the real tier here)
_ids, _miss, _ref = _MB.resolve_tier("fw_gss_sitting", _MB.scan())
_TL = [i.lower() for i in _ids]
check("12 fw_gss_sitting resolves", _TL and not _miss and not _ref, (_miss, _ref))
_W = TG.tier_want("fw_gss_sitting")
check("12 tier want carries the bridge, FlowWorks, GSS, Biomes, VEF core",
      {"mandrake.rm.flowworks", "mandrake.rm.gimmesomeslack", "mandrake.rm.biomes",
       "oskarpotocki.vanillafactionsexpanded.core"} <= set(_W) and set(_W) <= set(_TL), _W)
check("12 the resolved tier itself fits", TG.tier_gaps(_TL, "river", tier_list=_TL) == [], TG.tier_gaps(_TL, "river", tier_list=_TL))
_G28 = list(_TL) + ["sarg.alphabiomes", "erdelf.humanoidalienraces"]
_g = TG.tier_gaps(_G28, "river", tier_list=_TL)
check("12 the 2026-11-03 game (retired alphabiomes + HAR) is a wrong game",
      any("retired" in x for x in _g) and any("beyond tier" in x for x in _g), _g)
_g = TG.tier_gaps([i for i in _TL if i != "mandrake.rm.gimmesomeslack"], "river", tier_list=_TL)
check("12 a list lacking a tier want is a wrong game", any("lacks tier" in x and "gimmesomeslack" in x for x in _g), _g)
_g = TG.tier_gaps([i for i in _TL if i != "ludeon.rimworld.odyssey"], "river", tier_list=_TL)
check("12 a list lacking a DLC is a wrong game", any("DLC" in x for x in _g), _g)
check("12 an empty running read is a problem, never a fit", TG.tier_gaps([], "river", tier_list=_TL) != [])
check("12 the gate never exits 1 (it judges the game, not the item)", 1 not in (TG.FITS, TG.WRONG_GAME, TG.BLIND),
      (TG.FITS, TG.WRONG_GAME, TG.BLIND))
_LPT = open(_LP, encoding="utf-8").read().splitlines()
for _c in ("A1", "A2"):
    _ln = [ln for ln in _LPT if ln.startswith("live-proof %s:" % _c)]
    check("12 live %s runs the tier gate first, then the prove" % _c,
          len(_ln) == 1 and _ln[0].split(":", 1)[1].strip().startswith("python.exe src/RimMandrake/Utils/modcheck/test_site_tier_gate.py river")
          and "test_site_saves.py prove river" in _ln[0].split("&&", 1)[1], _ln)
sys.path.insert(0, os.path.join(HERE, "..", "..", "rimflow"))
import relentless_live_round as RLR  # noqa: E402
_lm = RLR.live_mods("\n".join(_LPT))
check("12 live-mods names FlowWorks, GimmeSomeSlack, RimMandrake.Biomes",
      {"FlowWorks", "GimmeSomeSlack", "RimMandrake.Biomes"} <= set(_lm), _lm)

print("selftest_test_site_saves: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
