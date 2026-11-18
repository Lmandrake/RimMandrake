#!/usr/bin/env python3
"""selftest for mod_names.py, the one live-mods name resolver (LIVE_MODS_ENFORCE_ROLL_CALL_BEFORE_BOARDING). Its cases
moved from selftest_relentless_needs.py with the resolver (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES).

Offline and deterministic: a synthetic index; no game folder, no git.

    python3 src/RimMandrake/rimflow/selftest_mod_names.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import mod_names as N  # noqa: E402

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


def t_one_resolver():
    import modlist_swap as M
    saved = N._DEFAULT
    try:
        N._DEFAULT = index()
        pk, dirs = M.split_names(["RimMandrake.Biomes", "7f.alienworlds", "FlowWorks"])
        ok(pk == ["7f.alienworlds"] and dirs == ["RimMandrake.Biomes", "FlowWorks"],
           "modlist_swap.split_names asks the one resolver", (pk, dirs))
        ok(M.is_mod_folder("RimMandrake.Biomes") and not M.is_mod_folder("NoSuchMod"),
           "modlist_swap.is_mod_folder asks the one resolver")
    finally:
        N._DEFAULT = saved


def t_fixture_roundtrip():
    ix = index()
    back = N.Index.from_json(ix.as_json())
    ok(back.as_json() == ix.as_json(), "an index survives the fixture's json")


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


def main():
    for t in (t_resolve, t_blind_index, t_one_resolver, t_fixture_roundtrip, t_srchash_stale):
        t()
    print('{"ok": %d, "fails": %d}' % (n_ok, len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
