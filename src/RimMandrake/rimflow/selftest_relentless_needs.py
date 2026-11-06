#!/usr/bin/env python3
"""LIVE_MODS_ENFORCE_ROLL_CALL_BEFORE_BOARDING: the one live-mods name resolver (relentless_names), its refusal before a
slot, per-rider validation before a batch union, and need inference that only ever ADVISES.

Offline and deterministic: a synthetic index, fake fx objects; no game folder, no git. The census replay runs on its own
frozen fixture (relentless_names.py replay)."""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless_names as N  # noqa: E402
import relentless_live_round as R  # noqa: E402
import relentless_game as G  # noqa: E402

fails = []
n_ok = 0


def ok(cond, what, got=None):
    global n_ok
    if cond:
        n_ok += 1
        print("ok   " + what)
    else:
        fails.append(what)
        print("FAIL %s%s" % (what, ("  got: %r" % (got,)) if got is not None else ""))


def index(**kw):
    d = dict(folders=["FlowWorks", "Armoury", "UtinniPatches", "KeelHoist", "RimProperty"],
             folded={"Stillsand": ("RimMandrake.Biomes", "Stillsand"), "CreatureBehaviors": ("RimMandrake.Biomes", "CB")},
             game=["FlowWorks", "Armoury", "RimMandrake.Biomes", "HugeThings"],
             packages=["7f.alienworlds", "ebsg.framework", "neronix17.toolbox", "neku.largepawns"],
             repo_pids={"mandrake.rsw.armoury": "Armoury", "mandrake.rm.flowworks": "FlowWorks",
                        "mandrake.rut.utinnipatches": "UtinniPatches"},
             namespaces={"RimMandrake.Property": "RimProperty"},
             deps={"UtinniPatches": ["mandrake.rsw.armoury"], "Armoury": ["neronix17.toolbox"],
                   "neronix17.toolbox": ["ebsg.framework"]})
    d.update(kw)
    return N.Index(d["folders"], d["folded"], d["game"], d["packages"], d["repo_pids"], d["namespaces"], d["deps"],
                   d.get("defs"), d.get("stale"))


def t_resolve():
    ix = index()
    k = lambda n: N.resolve(n, ix)    # noqa: E731
    ok(k("FlowWorks")["kind"] == "folder", "a repo folder resolves as itself")
    ok(k("HugeThings")["kind"] == "folder", "a folder in the game's Mods folder resolves")
    ok(k("RimMandrake.Biomes")["kind"] == "composed", "the dotted composed folder is a folder, never a packageId")
    r = k("CreatureBehaviors")
    ok(r["kind"] == "folded" and r["canon"] == "RimMandrake.Biomes", "a folded source normalises to its composed mod", r)
    r = k("mandrake.rsw.armoury")
    ok(r["kind"] == "repo_pid" and r["canon"] == "mandrake.rsw.armoury" and "Armoury" in r["why"],
       "our own packageId resolves, loaded by packageId as before (never planned as a tree)", r)
    ok(k("7f.alienworlds")["kind"] == "package" and k("7F.AlienWorlds")["canon"] == "7f.alienworlds",
       "an installed workshop packageId resolves, lower-cased")
    r = k("RimMandrake.FlowWorks")
    ok(r["kind"] == "unknown" and "packageId" in r["why"] and r.get("near", [None])[0] == "FlowWorks",
       "RimMandrake.FlowWorks is refused as a packageId nobody carries, nearest FlowWorks", r)
    r = k("infrastructure/state/modlists/ModsConfig.SHIP.xml")
    ok(r["kind"] == "unknown" and "file path" in r["why"], "a modlist file is refused as a path", r)
    r = k("flowworks")
    ok(r["kind"] == "unknown" and r.get("near", [None])[0] == "FlowWorks", "a case slip is refused with the right name", r)
    ok(k("ludeon.rimworld.anomaly")["kind"] == "package", "a DLC packageId is always loadable")


def t_blind_index():
    ix = index(packages=None)
    r = N.resolve("some.workshop.mod", ix)
    ok(r["kind"] == "unverified", "no packageId index: a dotted name is passed on, never refused", r)
    ix = index(game=None)
    ok(N.resolve("NotHere", ix)["kind"] == "unverified", "no game Mods listing: a bare name is passed on")
    ok(N.resolve("FlowWorks", ix)["kind"] == "folder", "the repo half still resolves")
    ix = N.Index(None)
    ok(N.resolve("Anything", ix)["kind"] == "unverified", "no repo at all: nothing is refused")
    boom = N.Index(["A"], {}, [], lambda: (_ for _ in ()).throw(OSError("unmounted")))
    ok(N.resolve("x.y", boom)["kind"] == "unverified", "a workshop scan that raises is blindness, not a refusal")


def t_check_and_refusal():
    chk = N.check(["FlowWorks", "Stillsand", "CreatureBehaviors", "RimMandrake.FlowWorks", "mandrake.rsw.armoury"], index())
    ok(chk["mods"] == ["FlowWorks", "RimMandrake.Biomes", "mandrake.rsw.armoury"], "canonical, no repeats, the bad one left out",
       chk["mods"])
    line = N.refusal(chk["refused"])
    ok(line and "'RimMandrake.FlowWorks'" in line and "nearest: FlowWorks" in line,
       "the refusal says what it looked like and the nearest name", line)
    ok(N.refusal([]) is None, "nothing refused: no line")


def t_comment():
    ok(R.live_mods("live-mods: FlowWorks  # auto: Armoury\n") == ["FlowWorks"],
       "an inline # comment on a live-mods line is not read as mod names (review caution :108)")


def t_advise():
    ix = index()
    text = "live-mods: FlowWorks\nlive-proof A1: python3 src/RimMandrake/Utils/p.py --absent RUT_PaleMoss --without Armoury\n"
    scripts = {"src/RimMandrake/Utils/p.py": 'assert "Stillsand" must not be loaded\nx = 1\n# the RUT_PaleMoss is absent\n'}
    adv = N.advise(text, scripts, {"FlowWorks"}, ix)
    ok(adv == [], "a name only in an absence assertion adds nothing", adv)
    text = ("live-mods: KeelHoist\nlive-proof A1: python3 src/RimMandrake/RimProperty/proof.py --needs 7f.alienworlds "
            "--json '{\"type\":\"RimMandrake.Property.RM_Verbs\"}'\n")
    scripts = {"src/RimMandrake/RimProperty/proof.py": 'MODS = ["UtinniPatches"]\n'}
    before = (text, dict(scripts))
    adv = N.advise(text, scripts, {"KeelHoist"}, ix)
    mods = [a["mod"] for a in adv]
    ok("RimProperty" in mods, "the mod a proof script lives in is advised", mods)
    ok("7f.alienworlds" in mods, "a packageId the proof line needs is advised", mods)
    ok("UtinniPatches" in mods, "a quoted folder name in the script is advised", mods)
    ok(all(":" in a["at"] or a["at"].startswith("About.xml") for a in adv), "every advice carries file:line evidence", adv)
    adv2 = N.advise(text, scripts, {"KeelHoist"}, ix)
    ok(adv2 == adv and (text, scripts) == before, "repeated run: the same advice, nothing written", adv2)
    gaps = N.closure_gaps({"UtinniPatches"}, ix)
    ok(("UtinniPatches", "neronix17.toolbox", "mandrake.rsw.armoury") in gaps and
       ("UtinniPatches", "ebsg.framework", "neronix17.toolbox") in gaps,
       "a transitive dependency modlist_swap would not add is found", gaps)
    ok(not any(g[1] == "mandrake.rsw.armoury" for g in gaps), "an immediate dependency is no gap (the enable adds it)")
    adv = N.advise("live-mods: UtinniPatches, Armoury\n", {}, {"UtinniPatches", "Armoury"}, ix)
    ok([a["mod"] for a in adv] == ["ebsg.framework"], "a dependency of a named dependency is the only gap left", adv)


class GapFx(object):
    """A RoundFx-shaped fake for mod_gap/batch_gap: names_index is the synthetic index."""

    def __init__(self, mods):
        self.mods, self.plans = mods, []

    def names_index(self):
        return index()

    def mods_of(self, sha):
        return list(self.mods.get(sha, []))

    def folded(self):
        return {"Stillsand": ("RimMandrake.Biomes", "Stillsand"), "CreatureBehaviors": ("RimMandrake.Biomes", "CB")}

    def deploy_plan(self, args, _max_s):
        self.plans.append(args)
        return 0, ""

    def running_load_gap(self, mods):
        return None


def t_batch():
    fx = GapFx({"lead": ["KeelHoist"], "good": ["Armoury"], "bad": ["RimProperty"]})
    g = R.batch_gap(fx, [("lead", "live-mods: FlowWorks\n", "L"), ("good", "live-mods: UtinniPatches\n", "V"),
                         ("bad", "live-mods: RimMandrake.FlowWorks\n", "X")])
    # ebsg.framework: neronix17.toolbox's hard dependency, two hops below the riders' folders, which the enable alone
    # would miss; the gate now adds it (LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT: a hard closure need is enforced)
    ok(g["mods"] == ["Armoury", "FlowWorks", "KeelHoist", "UtinniPatches", "ebsg.framework"],
       "leader + valid rider ride; the invalid rider's own mods are left out", g["mods"])
    ok([(x["item"], x["pos"]) for x in g["refused"]] == [("X", 2)] and "nearest: FlowWorks" in g["refused"][0]["why"],
       "the bad rider is named with an actionable reason", g["refused"])
    ok(len(fx.plans) == 1 and "RimProperty" not in fx.plans[0], "one plan over the union, no bad rider in it", fx.plans)
    g = R.batch_gap(fx, [("lead", "live-mods: Bogus\n", "L"), ("good", "live-mods: UtinniPatches\n", "V")])
    ok("KeelHoist" in g["mods"] and "UtinniPatches" in g["mods"] and g["refused"][0]["pos"] == 0,
       "a leader's bad name is reported, its valid mods and its riders still ride", g)
    g = R.mod_gap(fx, "lead", "live-mods: CreatureBehaviors, Nope\n", running=False)
    ok(g["mods"] == ["KeelHoist", "RimMandrake.Biomes"] and "'Nope'" in (g["unknown"] or ""),
       "mod_gap: a folded source loads as its composed mod, an unknown name is reported and left out", g)
    old = R.batch_gap(types.SimpleNamespace(mods_of=lambda s: [], folded=dict, deploy_plan=lambda *a: (0, "")),
                      [("a", "live-mods: Whatever\n")])
    ok(old["mods"] == ["Whatever"] and old["refused"] == [], "a fake with no names_index checks nothing (old behaviour)")


class Store(object):
    def __init__(self):
        self.st = {"I": {"status": G.GAME, "game": {}}}

    def load(self, item):
        return self.st.get(item)

    def save(self, st):
        pass

    def lock(self):
        import contextlib
        return contextlib.nullcontext()


def t_preflight_names():
    calls = []

    class Fx(object):
        def game_names_check(self, item, sha):
            calls.append((item, sha))
            return ("live-mods names no mod this machine has: 'X' ...", [{"mod": "Y", "at": "p.py:3", "line": "Y"}])
    store, acts = Store(), []
    bad = G._names_bad(store, Fx(), "I", "s1", acts)
    ok(len(bad) == 1 and bad[0]["kind"] == "refused" and bad[0]["cid"] == "live-mods" and bad[0]["fp"].startswith("names:"),
       "an unknown name is a preflight refusal (the item goes back with the reason)", bad)
    ok([a["do"] for a in acts] == ["live_mods_advice"] and store.st["I"]["game"]["advised"] == "s1",
       "advice is journaled, never written into a proof", acts)
    acts2 = []
    G._names_bad(store, Fx(), "I", "s1", acts2)
    ok(acts2 == [], "the same build is advised once", acts2)
    ok(G._names_bad(store, object(), "I", "s1", []) == [], "a fake without game_names_check checks nothing")

    class Fx3(object):      # LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT: (refusal, warnings, inferred additions)
        def game_names_check(self, item, sha):
            return ("live-without FlowWorks, but the planned load holds it", [],
                    [{"mod": "KeelHoist", "src": "script_home", "at": "src/RimMandrake/KeelHoist/p.py:0"}])
    store, acts = Store(), []
    bad = G._names_bad(store, Fx3(), "I", "s2", acts)
    ok(len(bad) == 1 and "live-without" in bad[0]["why"], "a live-without conflict is a preflight refusal", bad)
    ok(acts and acts[0].get("inferred") == ["KeelHoist (script_home src/RimMandrake/KeelHoist/p.py:0)"],
       "the gate's additions are journaled with their evidence", acts)


def t_one_resolver():
    import modlist_swap as M
    import relentless_live as L
    saved = N._DEFAULT
    try:
        N._DEFAULT = index()
        L._FOLDER_SEEN.clear()
        ok(L.is_package("7f.alienworlds") and not L.is_package("RimMandrake.Biomes"),
           "relentless_live.is_package asks the one resolver")
        pk, dirs = M.split_names(["RimMandrake.Biomes", "7f.alienworlds", "FlowWorks"])
        ok(pk == ["7f.alienworlds"] and dirs == ["RimMandrake.Biomes", "FlowWorks"],
           "modlist_swap.split_names asks the one resolver", (pk, dirs))
    finally:
        N._DEFAULT = saved
        L._FOLDER_SEEN.clear()


def t_fixture_roundtrip():
    ix = index()
    back = N.Index.from_json(ix.as_json())
    ok(back.as_json() == ix.as_json(), "an index survives the fixture's json")


def t_typed_and_data():
    ix = index()
    # SETTLEMENT_VERBS_WAVE_1: the type's mod is the build's (derived), not named -> still advised
    text = 'live-proof A1: x --json \'{"type":"RimMandrake.Property.RM_SettlementVerbsProof"}\'\n'
    adv = N.advise(text, {}, {"RimProperty"}, ix, named=[])
    ok([a["mod"] for a in adv] == ["RimProperty"], "a C# type the proof calls is advised until live-mods NAMES its mod", adv)
    adv = N.advise("live-mods: RimProperty\n" + text, {}, {"RimProperty"}, ix, named=["RimProperty"])
    ok(adv == [], "a named type mod is no advice", adv)
    adv = N.advise("live-proof A1: python3 src/RimMandrake/Utils/q.py\n", {"src/RimMandrake/Utils/q.py": "x = 'KeelHoist'\n"},
                   {"KeelHoist"}, ix, named=[])
    ok(adv == [], "an untyped name the build already carries needs no naming", adv)
    # ART_OVERRIDE_FAMILY_SCRIPT_1: the donors live only in a data file a sibling module reads
    files = {"src/RimMandrake/Utils/live.py": "import fold_check as fc  # noqa\nimport os\n",
             "src/RimMandrake/Utils/fold_check.py": 'MANIFEST = os.path.join(HERE, "fold_manifest.json")\n',
             "src/RimMandrake/Utils/fold_manifest.json": '{"src": "src/RimMandrake/KeelHoist/Textures/a.png",\n'
                                                         ' "donor": "donor:7f.alienworlds"}\n',
             "src/RimMandrake/Utils/os.py": ""}
    text = "live-proof A1: python.exe src/RimMandrake/Utils/live.py --live\n"
    got = N.gather_scripts(text, lambda p: files.get(p, ""))
    ok(sorted(got) == ["src/RimMandrake/Utils/fold_manifest.json", "src/RimMandrake/Utils/live.py"],
       "gather_scripts: the script and the data its sibling module names; the module itself is not scanned", sorted(got))
    mods = [a["mod"] for a in N.advise(text, got, set(), ix, named=[])]
    ok("KeelHoist" in mods and "7f.alienworlds" in mods, "a mod named only in the read data file is advised", mods)
    big = dict(files, **{"src/RimMandrake/Utils/fold_manifest.json": "x" * (N.MAX_DATA + 1)})
    ok("src/RimMandrake/Utils/fold_manifest.json" not in N.gather_scripts(text, lambda p: big.get(p, "")),
       "a data file over MAX_DATA is not read")

    # WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR: a bare folder on a line that says it must be active
    adv = N.advise("live-proof A1: python3 src/RimMandrake/Utils/z.py\n",
                   {"src/RimMandrake/Utils/z.py": "# run with RimThemes + KeelHoist active\n# KeelHoist draws it\n"},
                   set(), ix, named=[])
    ok([(a["mod"], a["at"]) for a in adv] == [("KeelHoist", "src/RimMandrake/Utils/z.py:1")],
       "a bare mod folder counts only on a line with a need cue", adv)
    adv = N.advise("", {"x.py": "# KeelHoist must not be loaded\n"}, set(), ix, named=[])
    ok(adv == [], "an absence line with a need word still gives nothing", adv)
    # WARSCAR_HOSPICE_DESERTERS_1: a folded build source is noted with the composed mod the load holds
    adv = N.advise("", {}, {"RimMandrake.Biomes"}, ix, named=[], build={"Stillsand"})
    ok([(a["mod"], a["at"]) for a in adv] == [("RimMandrake.Biomes", "build: Stillsand")],
       "a folded build source is noted with its composed mod", adv)
    adv = N.advise("live-mods: RimMandrake.Biomes\n", {}, {"RimMandrake.Biomes"}, ix, named=["RimMandrake.Biomes"],
                   build={"Stillsand"})
    ok(adv == [], "no note once live-mods names the composed mod", adv)


def t_replay_strict():
    ix = index()
    case = {"item": "R1X", "root": "R1", "text": "live-proof A1: true\n", "scripts": {}, "build_mods": [],
            "added": ["neku.largepawns"]}
    fx = {"index": ix.as_json(), "cases": [case], "passes": []}
    code, rep = N.replay(fx)
    ok(code == 1 and rep["R1_caught"] == "0/1", "an R1 item with no warning FAILS the replay (no unreachable escape)", rep)
    warned = dict(case, text="# needs neku.largepawns\nlive-proof A1: true\n")
    code, rep = N.replay(dict(fx, cases=[warned, case]))
    ok(code == 1 and rep["R1_caught"] == "0/1", "an item is caught only when EVERY failed run of it is warned", rep)
    other = dict(case, text="live-proof A1: python3 src/RimMandrake/KeelHoist/p.py\n")
    code, rep = N.replay(dict(fx, cases=[other]))
    ok(code == 1 and rep["R1_caught"] == "0/1", "advice naming only OTHER mods does not catch a case that owes one", rep)
    named = dict(case, text="live-mods: mandrake.rsw.armoury\nlive-proof A1: python3 src/RimMandrake/Utils/q.py\n")
    adv = N.advise(named["text"], {"src/RimMandrake/Utils/q.py": "x = 'Armoury'\n"}, {"mandrake.rsw.armoury"}, ix,
                   named=["mandrake.rsw.armoury"])
    ok(not any(a["mod"] == "Armoury" for a in adv), "a mod named by packageId is not advised again by folder", adv)
    by_pid = dict(case, text="live-mods: mandrake.rsw.armoury\nlive-proof A1: true\n", added=["Armoury"])
    code, rep = N.replay(dict(fx, cases=[by_pid]))
    ok(rep["R1"]["R1X"]["cases"][0]["owed"] == [], "a mod named by packageId is not owed by its folder name", rep)
    pid_adv = dict(case, text="# needs mandrake.rsw.armoury\nlive-proof A1: true\n", added=["Armoury"])
    code, rep = N.replay(dict(fx, cases=[pid_adv]))
    ok(code == 0 and rep["R1"]["R1X"]["hit"] == ["Armoury"], "advice by packageId hits an owed folder", rep)
    code, rep = N.replay(dict(fx, cases=[warned]))
    ok(code == 0 and rep["R1_caught"] == "1/1" and rep["R1_hit"] == "1/1", "a warned R1 run passes", rep)


# ---------------------------------------------------------------- LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT: enforce

DEFS = {"RM_FallRails": ["FlowWorks"], "RUT_PaleMoss": ["UtinniPatches"], "RM_Shared": ["FlowWorks", "KeelHoist"]}
SAVE = ('<?xml version="1.0"?><savegame><meta><gameVersion>1.6</gameVersion><modIds><li>ludeon.rimworld</li>'
        '<li>brrainz.harmony</li><li>7f.alienworlds</li><li>mandrake.rsw.armoury</li></modIds></meta><game>')


def added(nd):
    return sorted(a["mod"] for a in nd["add"])


def t_each_source():
    ix = index(defs=DEFS)
    nd = lambda text, scripts=None, named=(), build=(), saves=None: N.needs(  # noqa: E731
        text, scripts or {}, list(named), list(build), ix, saves=saves)
    got = nd("live-proof A1: python3 src/RimMandrake/Utils/p.py --save Saves/fixture_a.rws\n",
             saves={"Saves/fixture_a.rws": SAVE})
    ok(set(added(got)) >= {"7f.alienworlds", "mandrake.rsw.armoury"} and
       all(a["src"] == "fixture" for a in got["add"] if a["mod"] in ("7f.alienworlds", "mandrake.rsw.armoury")),
       "a fixture save's <modIds> are needs (the base game and Harmony are never advice)", got["add"])
    ok(N.proof_saves("live-proof A1: x --save Saves/a.rws\n# the b.rws save is absent here\n") == ["Saves/a.rws"],
       "a save named only on an absence line is no fixture")
    got = nd("live-proof A1: python3 src/RimMandrake/KeelHoist/p.py\n")
    ok(added(got) == ["KeelHoist"] and got["add"][0]["src"] == "script_home", "the proof script's own mod", got["add"])
    got = nd("live-proof A1: python3 src/RimMandrake/Wastes/plan.py\n", build=[])
    ix2 = index(defs=DEFS, folded={"Wastes": ("RimMandrake.Biomes", "Wastes")})
    got = N.needs("live-proof A1: python3 src/RimMandrake/Wastes/plan.py\n", {}, [], [], ix2)
    ok(added(got) == ["RimMandrake.Biomes"], "a folded source's script needs the composed mod", got["add"])
    got = N.needs("live-proof A1: true\n", {}, [], ["Stillsand"], ix)
    ok(added(got) == ["RimMandrake.Biomes"] and got["add"][0]["src"] == "folded",
       "the build's folded source adds the composed mod the load holds", got["add"])
    got = nd("live-proof A1: python3 src/RimMandrake/Utils/live_def_check.py --needs 7f.alienworlds --needs ebsg.framework"
             " --has ThingDef/X\n")
    ok(set(added(got)) >= {"7f.alienworlds", "ebsg.framework"} and all(a["src"] == "proof_cli" for a in got["add"]),
       "every --needs argument of a proof line is a need", got["add"])
    got = nd("# `modlist_swap.py --enable neku.largepawns ebsg.framework --apply`\nlive-proof A1: true\n")
    ok(set(added(got)) == {"neku.largepawns", "ebsg.framework"}, "a staging --enable run names every mod", got["add"])
    got = nd("# Stager: the list ALSO needs Large Pawns (neku.largepawns, workshop 1)\nlive-proof A1: true\n")
    ok(added(got) == ["neku.largepawns"] and got["add"][0]["src"] == "proof_cue", "a staging-cue line", got["add"])
    got = nd("live-proof A1: python3 src/RimMandrake/Utils/q.py\n",
             {"src/RimMandrake/Utils/q.py": 'call("RimMandrake.Property.RM_Verbs.Run")\n'})
    ok(added(got) == ["RimProperty"] and got["add"][0]["src"] == "script_type",
       "a C# type in one root namespace names its mod", got["add"])
    got = nd("live-proof A1: python3 src/RimMandrake/Utils/live_def_check.py --has ThingDef/RM_FallRails\n")
    ok(added(got) == ["FlowWorks"] and got["add"][0]["src"] == "proof_defname",
       "a defName exactly one mod defines names that mod", got["add"])
    got = nd("live-mods: UtinniPatches\nlive-proof A1: true\n", named=["UtinniPatches"])
    ok(added(got) == ["ebsg.framework", "neronix17.toolbox"] and all(a["src"] == "closure" for a in got["add"]),
       "the hard dependencies the enable would miss (below an immediate one) are added", got["add"])
    got = nd("live-proof A1: python3 src/RimMandrake/Utils/q.py --has ThingDef/RM_Shared\n",
             {"src/RimMandrake/Utils/q.py": 'X = "UtinniPatches"\n'})
    ok(added(got) == [] and sorted(a["mod"] for a in got["warn"]) == ["FlowWorks", "KeelHoist", "UtinniPatches"],
       "a defName two mods define, and a quoted name in a script, only warn", got)


def t_absence_gives_nothing():
    ix = index(defs=DEFS)
    for text, scripts in (("live-proof A1: python3 src/RimMandrake/Utils/p.py --absent RUT_PaleMoss\n", {}),
                          ("live-proof A1: python3 src/RimMandrake/Utils/p.py\n",
                           {"src/RimMandrake/Utils/p.py": 'assert_absent("RUT_PaleMoss")\n'}),
                          ("live-proof A1: python3 src/RimMandrake/Utils/p.py\n",
                           {"src/RimMandrake/Utils/p.py": '# RUT_PaleMoss is not present on this tier\n'}),
                          ("live-proof A1: python3 src/RimMandrake/Utils/live_def_check.py --without UtinniPatches "
                           "--has ThingDef/X\n", {})):
        got = N.needs(text, scripts, [], [], ix)
        ok(got["add"] == [] and got["warn"] == [], "an absence assertion gives no need: %s" % (text + str(scripts))[:70],
           got)


def t_live_without():
    ix = index(defs=DEFS)
    ok(N.live_without("live-without: UtinniPatches, 7f.alienworlds  # it measures their absence\n") ==
       ["UtinniPatches", "7f.alienworlds"], "live-without parses like live-mods, # tail a comment")
    ok(R.live_mods("live-without: UtinniPatches\nlive-mods: FlowWorks\n") == ["FlowWorks"],
       "a live-without line is never read as mods to load")
    text = ("live-without: UtinniPatches\nlive-proof A1: python3 src/RimMandrake/Utils/live_def_check.py "
            "--needs mandrake.rut.utinnipatches --has ThingDef/RUT_PaleMoss\n")
    got = N.needs(text, {}, [], [], ix)
    ok(got["add"] == [] and got["without"] == ["UtinniPatches"] and got["conflict"] == [] and
       N.without_conflict(got) is None, "inference never adds a live-without mod (by folder or packageId)", got)
    ok(any(a["mod"] in ("UtinniPatches", "mandrake.rut.utinnipatches") and "live-without" in a.get("why", "")
           for a in got["warn"]), "the blocked need is still shown, as a warning", got["warn"])
    got = N.needs("live-mods: FlowWorks\nlive-without: FlowWorks\n", {}, ["FlowWorks"], [], ix)
    ok(got["conflict"] == ["FlowWorks"] and "FlowWorks" in (N.without_conflict(got) or ""),
       "a planned load holding a live-without mod is refused", got)
    got = N.needs("live-without: Utinipatches\n", {}, [], ["UtinniPatches"], ix)
    line = N.without_conflict(got)
    ok(line and "'Utinipatches'" in line, "an unknown live-without name is refused", line)
    got = N.needs("live-without: UtinniPatches\nlive-proof A1: true\n", {}, [], ["UtinniPatches"], ix)
    ok(got["conflict"] == ["UtinniPatches"], "the build's own mod in live-without conflicts", got)


def t_gate_enforces():
    fx = GapFx({"lead": ["KeelHoist"]})
    fx.names_index = lambda: index(defs=DEFS)
    g = R.mod_gap(fx, "lead", "live-proof A1: python3 src/RimMandrake/Utils/live_def_check.py --needs 7f.alienworlds "
                              "--has ThingDef/RM_FallRails\n", running=False)
    ok(g["mods"] == ["7f.alienworlds", "FlowWorks", "KeelHoist"], "mod_gap adds sure needs to the planned load", g["mods"])
    ok(sorted((x["mod"], x["src"]) for x in g["inferred"]) == [("7f.alienworlds", "proof_cli"),
                                                              ("FlowWorks", "proof_defname")] and
       all(x["at"] for x in g["inferred"]), "each addition carries its source and file:line", g["inferred"])
    ok(fx.plans and "FlowWorks" in str(fx.plans[-1]) and "7f.alienworlds" not in str(fx.plans[-1]),
       "an inferred folder is planned for deploy; a packageId only loaded", fx.plans)
    g = R.mod_gap(fx, "lead", "live-without: KeelHoist\n", running=False)
    ok(g["conflict"] and "KeelHoist" in g["conflict"], "mod_gap reports a live-without conflict before the slot", g)
    fx2 = GapFx({"lead": ["KeelHoist"]})
    fx2.names_index = lambda: index(defs=DEFS, stale={"FlowWorks": "its deployed DLL is older than its source"})
    g = R.mod_gap(fx2, "lead", "live-proof A1: x --has ThingDef/RM_FallRails\n", running=False)
    ok(g["mods"] == ["KeelHoist"] and g["warn"] == ["FlowWorks"] and not g["conflict"] and not g["unknown"],
       "a stale index degrades the need to a warning, never a refusal", g)


def t_srchash_stale():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        for side, line in (("repo", "# dll: aaa\n"), ("game", "# dll: bbb\n")):
            os.makedirs(os.path.join(d, side, "Assemblies"))
            with open(os.path.join(d, side, "Assemblies", "M.dll.srchash"), "w") as f:
                f.write("# project: x\n" + line + "123 a.cs\n")
        ok(N._srchashes(os.path.join(d, "repo")) != N._srchashes(os.path.join(d, "game")),
           "a deployed DLL stamped with another build reads as a different .srchash (stale index)")
        ok(N._srchashes(os.path.join(d, "none")) == {}, "a mod with no stamped DLL has no staleness to report")


def t_batch_split():
    fx = GapFx({"lead": ["KeelHoist"], "rider": ["Armoury"], "third": ["FlowWorks"]})
    fx.names_index = lambda: index(defs=DEFS)
    g = R.batch_gap(fx, [("lead", "live-mods: UtinniPatches\n", "L"), ("rider", "live-without: UtinniPatches\n", "W"),
                         ("third", "live-proof A1: true\n", "T")])
    ok([x["item"] for x in g["split"]] == ["W"] and "UtinniPatches" in g["split"][0]["why"] and
       "Armoury" not in g["mods"] and "FlowWorks" in g["mods"],
       "a rider live-without what the leader needs rides another load; the rest still ride", g)
    g = R.batch_gap(fx, [("rider", "live-without: UtinniPatches\n", "W"), ("lead", "live-mods: UtinniPatches\n", "L")])
    ok([x["item"] for x in g["split"]] == ["L"] and "UtinniPatches" not in g["mods"],
       "the reverse: a rider needing what the leader is live-without splits off", g)
    g = R.batch_gap(fx, [("lead", "live-proof A1: python3 src/RimMandrake/Utils/live_def_check.py --has ThingDef/"
                                  "RM_FallRails\n", "L"), ("rider", "live-without: FlowWorks\n", "W")])
    ok([x["item"] for x in g["split"]] == ["W"], "an INFERRED need splits a live-without rider too", g)
    ok(g["inferred"].get("L") and g["inferred"]["L"][0]["mod"] == "FlowWorks", "the batch records each rider's additions",
       g["inferred"])


def t_idempotent_and_run_row():
    ix = index(defs=DEFS)
    text = "live-proof A1: python3 src/RimMandrake/KeelHoist/p.py --needs 7f.alienworlds\n"
    a, b = N.needs(text, {}, [], ["Stillsand"], ix), N.needs(text, {}, [], ["Stillsand"], ix)
    ok(a == b and added(a) == ["7f.alienworlds", "KeelHoist", "RimMandrake.Biomes"], "needs is a pure function", a)
    named = ["7f.alienworlds", "KeelHoist", "RimMandrake.Biomes"]
    c = N.needs("live-mods: %s\n" % ", ".join(named) + text, {}, named, ["Stillsand"], ix)
    ok(c["add"] == [], "a proof naming every addition gets none (the derived list is a fixed point)", c["add"])
    seen = {}

    class RunFx(GapFx):
        def items(self):
            return [{"id": "L", "stage": "game", "built_sha": "lead", "criteria": [{"id": "A1"}]}]

        def proofs(self, item):
            return text

        def game_started(self):
            return 1_799_999_000.0

    def run(fx, root, item_id, cid, proof, deploy, r, now=None, needs=(), site=None, trees=(), env=None):
        seen.update(needs=list(needs), env=env)
        return {"item": item_id, "criterion": cid, "outcome": "PASS", "why": "", "sha": "lead"}
    import tempfile
    fx = RunFx({"lead": ["KeelHoist"]})
    fx.names_index = lambda: ix
    fx.folded = lambda: {}
    orig = R.candidates
    R.candidates = lambda items, proofs, hist, now, retry, game: ([("L", "A1", "python3 p.py", "lead")], {})
    try:
        with tempfile.TemporaryDirectory() as root:
            R.run_round(fx, root, {}, now=1_800_000_000, run=run)
    finally:
        R.candidates = orig
    env = seen.get("env") or {}
    ok("7f.alienworlds" in seen.get("needs", []) and "7f.alienworlds" in env.get("mods", []) and
       {"mod": "7f.alienworlds", "src": "proof_cli"}.items() <= (env.get("inferred") or [{}])[0].items(),
       "the run row records the effective mod list and each inferred addition with its evidence", seen)


def main():
    for t in (t_resolve, t_blind_index, t_check_and_refusal, t_comment, t_advise, t_batch, t_preflight_names,
              t_one_resolver, t_fixture_roundtrip, t_typed_and_data, t_replay_strict, t_each_source,
              t_absence_gives_nothing, t_live_without, t_gate_enforces, t_srchash_stale, t_batch_split, t_idempotent_and_run_row):
        t()
    print('{"ok": %d, "fails": %d}' % (n_ok, len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
