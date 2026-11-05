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
    return N.Index(d["folders"], d["folded"], d["game"], d["packages"], d["repo_pids"], d["namespaces"], d["deps"])


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
    ok(g["mods"] == ["Armoury", "FlowWorks", "KeelHoist", "UtinniPatches"],
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


def main():
    for t in (t_resolve, t_blind_index, t_check_and_refusal, t_comment, t_advise, t_batch, t_preflight_names,
              t_one_resolver, t_fixture_roundtrip):
        t()
    print('{"ok": %d, "fails": %d}' % (n_ok, len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
