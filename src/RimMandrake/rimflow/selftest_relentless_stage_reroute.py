#!/usr/bin/env python3
"""STAGER_SNAG_REWIRE_BUILDER_WOKEN_FOR_HARNESS: a stager stop after a blind PASS wakes no builder unless it names the
item's own mod (relentless_game._stage_stop), on the real supervisor with a fake world.

  a stop naming no own mod: bridge released, restaged after a wait, no strike, no generation, no worker;
  the same stop again (even on another source hash): one repair item, the item waiting on it, still no worker;
  a stop naming the item's own mod: back to the builder, as before;
  the own mod named by a namespace or packageId that holds no folder name: back to the builder too, on every repo mod;
  the own mod in the stop's `done so far` log or quoted deploy arguments alone is no accusation;
  a failed repair filing restages; a build whose mods cannot be read is the environment; another class still goes back.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                      # noqa: E402
import relentless_envcause as E             # noqa: E402
import relentless_game as G                 # noqa: E402
import relentless_names as N                # noqa: E402
import selftest_relentless_game as SG       # noqa: E402
import selftest_relentless_stage_machine as SM      # noqa: E402

FAILS = SG.FAILS
ok = SG.ok

# HEAVY_TEXTURES_MEASURE_REAL_VRAM gen 5's stop, 2026-11-06, word for word
GATE = ("python stager stopped: the companion sources in this clone (hash %s) are not the build's (%s): build.py would "
        "deploy another companion (done so far: nothing)")
INCIDENT = GATE % ("65dacf9e3143", "1ce3e989b891")


def stopped(x, text, klass="game_stage"):
    """A staging on `x` that ends in this snag, settled by the real step."""
    st = SM.staging(x)
    R.snag(x.s, "I0", st["gen"], klass, text, x.r)
    SM.end_unit(x, st)
    return st


def t_incident_restages_no_worker():
    x = SG.rig(1)
    st = stopped(x, INCIDENT)
    now = x.st("I0")
    g = now["game"]
    ok(now["status"] == "game" and now["gen"] == st["gen"], "still in the game lane, same generation: %s gen %s -> %s"
       % (now["status"], st["gen"], now["gen"]))
    ok(not now.get("last_fail") and not now.get("strikes"), "no failure and no strike: %s" % now.get("last_fail"))
    ok("release" in x.w.events, "the bridge is released")
    ok(g["phase"] == "stage" and g["retry_at"] > x.now and g["stages"] == 0 and not g.get("snag"),
       "restaged after a wait, the snag spent: %s" % {k: g.get(k) for k in ("phase", "retry_at", "stages", "snag")})
    ends = [a["end"] for a in x.s.attempts("I0") if a.get("end")]
    ok(ends[-1] == "game_env_fix" and "game_stage" not in ends, "the attempt ends as the environment: %s" % ends)
    launches = len(x.w.launches)
    x.tick()
    ok(len(x.w.launches) == launches, "no launch before the wait is over")
    x.now = g["retry_at"]
    x.tick()
    again = x.st("I0")
    ok(again["game"]["phase"] == "staging" and x.w.launches[-1][3] == G.STAGE_AGENT and again["gen"] == st["gen"],
       "the wait over, the python stager runs again, no builder: %s %s" % (again["game"]["phase"], x.w.launches[-1][3]))
    x.done()


def t_same_stop_routes_to_one_repair():
    x = SG.rig(1)
    st = stopped(x, INCIDENT)
    x.now = x.st("I0")["game"]["retry_at"]
    x.tick()
    run = x.st("I0")
    R.snag(x.s, "I0", run["gen"], "game_stage", GATE % ("aaaaaaaaaaaa", "bbbbbbbbbbbb"), x.r)
    SM.end_unit(x, run)
    now = x.st("I0")
    reps = [i[0] for i in x.w.repairs]
    ok(now["status"] == "blocked" and len(reps) == 1 and reps[0].startswith("GAMEENV_FIX_HARNESS_"),
       "the same stop on other hashes files one repair: %s %s" % (now["status"], reps))
    ok(now["wait"]["on"] == reps[0] and now["wait"]["resume"] == G.GAME and now["gen"] == st["gen"]
       and not now.get("last_fail"), "the item waits on it and resumes its game phase, no worker: %s" % now["wait"])
    x.done()


def t_own_mod_goes_back():
    x = SG.rig(1)
    x.w.own["I0"] = ["FlowWorks"]
    st = stopped(x, "python stager stopped: the game died during the load: a missing or stale type, first exception: "
                    "TypeLoadException RimMandrake.FlowWorks.CompPipe (done so far: nothing)")
    now = x.st("I0")
    ok(now["status"] != "game" and now["gen"] > st["gen"] and now["last_fail"]["class"] == "game_stage",
       "a stop naming the item's own mod goes back to its builder: %s %s" % (now["status"], now.get("last_fail")))
    x.done()


def t_names_read_the_cause_only():
    own = ["FlowWorks"]
    for text, want in (
            ("the game died: RimMandrake.FlowWorks.CompPipe", own),
            ("mandrake.rm.flowworks would not load", own),
            ("Mods\\FlowWorks\\Assemblies\\FlowWorks.dll is stale", own),
            ("the game died: RimMandrake.FlowWorksPipes.Comp", []),
            ("steam would not start (done so far: deployed --mod FlowWorks; FlowWorks enabled)", []),
            ("deploy plan --mod FlowWorks --mod Other exit 2: Traceback", []),
            ("deploy --compose biomes --with FlowWorks: the plan did not finish", []),
            ("", [])):
        ok(E.stage_names(text, own) == want, "stage_names(%r) == %s" % (text, want))
    # the whole road, with the log naming the own mod: the environment
    x = SG.rig(1)
    x.w.own["I0"] = ["FlowWorks"]
    stopped(x, "python stager stopped: Steam launch exit 1: no (done so far: deployed --mod FlowWorks)")
    ok(not x.st("I0").get("last_fail") and x.st("I0")["game"]["phase"] == "stage", "a log's own mod wakes no builder")
    x.done()
    # a real death's text: its exception accuses Armoury; ferny.worldbuilder is only in the log, and is not accused
    x = SG.rig(1)
    st = SM.staging(x)
    ops, execs, _ = SM.run_stager(x, st, token="gone")
    text = ops.reports[0][1]
    ok(not execs and ops.reports[0][0] == "snag" and "ferny.worldbuilder" in text
       and E.stage_names(text, ["Armoury", "ferny.worldbuilder"]) == ["Armoury"],
       "a rule's death accuses the mod of its exception, never its log's: %s" % text)
    x.done()


BAZAAR_DEATH = ("python stager stopped: the game died during the load: a missing or stale type, first exception: "
                "Could not find type named RimMandrake.Bazaar.CompStall (done so far: nothing)")


def t_own_mod_by_namespace_goes_back():
    """The blind check's probe, through the real step: the namespaces hold no folder name."""
    for mod, text in (("TheBazaar", BAZAAR_DEATH),
                      ("HugeThings", BAZAAR_DEATH.replace("RimMandrake.Bazaar.CompStall", "RimMandrake.TitanicCreatures.CompX")),
                      ("RimProperty", BAZAAR_DEATH.replace("RimMandrake.Bazaar.CompStall", "RimMandrake.Property.CompX")),
                      ("Scarlands", "python stager stopped: mandrake.rm.warscar would not load (done so far: nothing)")):
        x = SG.rig(1)
        x.w.own["I0"] = [mod]
        st = stopped(x, text)
        now = x.st("I0")
        ok(now["status"] != "game" and now["gen"] > st["gen"] and now["last_fail"]["class"] == "game_stage",
           "%s named by its own namespace or packageId goes back: %s %s" % (mod, now["status"], now.get("last_fail")))
        ok(not getattr(x.w, "repairs", None), "%s: no repair filed for the build's own defect" % mod)
        x.done()


def t_own_names_are_the_mods_alone():
    own = ["TheBazaar"]
    for text, want in (
            ("Could not find type named RimMandrake.Bazaar.CompStall", own),
            ("mandrake.rm.bazaar would not load", own),
            ("Could not find type named rimmandrake.bazaar.compstall", own),     # any case, as a folder name
            ("RimMandrake.Bazaars.Comp is a different namespace", []),
            ("RimMandrake.FlowWorks.Comp is another mod's", []),
            ("steam would not start (done so far: enabled mandrake.rm.bazaar)", []),
            ("deploy plan --mod mandrake.rm.bazaar exit 2: Traceback", []),
            ("brrainz.harmony would not load; Ludeon.RimWorld too", []),         # its About.xml dependencies, not its names
            ("Verse.AI.JobDriver threw in RimWorld.Pawn; System.Linq; HarmonyLib.Harmony; UnityEngine.Object", [])):
        ok(E.stage_names(text, own) == want, "stage_names(%r, TheBazaar) == %s" % (text, want))
    names = N.own_names("TheBazaar")
    ok("mandrake.rm.bazaar" in names and "RimMandrake.Bazaar" in names, "the names are read from its source: %s" % names)
    ok(N.own_names("NoSuchModAnywhere") == [], "an unknown mod has no other names")
    biomes = N.own_names("RimMandrake.Biomes")
    ok("mandrake.rm.biomes" in biomes, "a composed mod's names come from its manifest and shell: %s" % biomes)
    # engine namespaces name no mod even for a mod that declares one (Verse, RimWorld and HarmonyLib all do)
    engine = [(m, n) for m in repo_mods() for n in N.own_names(m) if n.split(".")[0] in N.ENGINE_NS]
    ok(not engine, "no mod owns an engine namespace: %s" % engine[:5])


def repo_mods():
    """Every repo mod folder (a dir with About/About.xml), read from this tree as deploy_custom_mods.mod_dirs does."""
    src = os.path.join(N.BOOKS, "src")
    return sorted(m for t in os.listdir(src) if os.path.isdir(os.path.join(src, t))
                  for m in os.listdir(os.path.join(src, t))
                  if os.path.isfile(os.path.join(src, t, m, "About", "About.xml")))


def t_census_every_mod_is_named_by_its_names():
    """The blind check's census: 8 of 114 C# mods missed by dominant namespace, 13 of 134 by packageId. Now none. The
    sanity floors say the instrument saw the tree: a missing src reads as 'no misses'."""
    mods = repo_mods()
    by_pid = by_ns = 0
    miss = []
    for m in mods:
        for n in N.own_names(m):
            by_pid += n.startswith("mandrake.")
            by_ns += not n.startswith("mandrake.")
            if E.stage_names("the game died: %s.CompX would not load" % n, [m]) != [m]:
                miss.append((m, n))
    ok(len(mods) >= 100 and by_pid >= 100 and by_ns >= 100, "the census saw the repo: %d mods, %d packageIds, %d namespaces"
       % (len(mods), by_pid, by_ns))
    ok(not miss, "every mod's every name accuses it: %s" % miss[:10])
    for m in ("TheBazaar", "HugeThings", "RimProperty", "Armoury", "EmpirePursuit", "MandrakePatches", "StarWarsPatches",
              "StarWarsRaces", "Scarlands"):
        ok(m in mods and N.own_names(m), "%s, a mod the folder name alone missed, has names: %s" % (m, N.own_names(m)))


def t_fp_is_the_cause():
    a, b = E.stage_stop(INCIDENT), E.stage_stop(GATE % ("0123456", "fedcba9876543210"))
    c = E.stage_stop("python stager stopped: Steam launch exit 1: no (done so far: nothing)")
    d = E.stage_stop("stages(s): deploy_plan=0 load=200 total=205; " + INCIDENT)
    ok(a.fp == d.fp, "the stager's own seconds, which head every real stop, are no part of it")
    ok(a.fp == b.fp and a.fp != c.fp and a.kind == "harness" and not a.fix, "the fp is the stop, not its hashes or log")
    ok(G.repair_id(a).startswith("GAMEENV_FIX_HARNESS_"), "and it mints the lane's repair id: %s" % G.repair_id(a))


def t_failed_filing_restages():
    x = SG.rig(1)
    stopped(x, INCIDENT)
    x.now = x.st("I0")["game"]["retry_at"]
    x.tick()
    x.w.env_repair = lambda item, title, text: "rimflow: refused"
    run = x.st("I0")
    R.snag(x.s, "I0", run["gen"], "game_stage", INCIDENT, x.r)
    SM.end_unit(x, run)
    now = x.st("I0")
    ok(now["status"] == "game" and now["game"]["phase"] == "stage" and now["game"]["harness"] == 2
       and not now.get("last_fail"), "a repair that cannot be filed restages, no worker: %s %s"
       % (now["status"], now["game"].get("harness")))
    x.done()


def t_unreadable_build_is_the_environment():
    x = SG.rig(1)
    x.w.own["I0"] = ValueError("git cannot read it")
    st = stopped(x, "Steam launch exit 1: no")
    now = x.st("I0")
    ok(now["game"]["phase"] == "stage" and now["gen"] == st["gen"] and not now.get("last_fail"),
       "a build whose mods cannot be read wakes no builder: %s" % now.get("last_fail"))
    x.done()


def t_other_class_goes_back():
    x = SG.rig(1)
    st = stopped(x, "a stager's other word", klass="game_contract")
    now = x.st("I0")
    ok(now["gen"] > st["gen"] and "a stager's other word" in now["last_fail"]["detail"],
       "another class goes back as before (attributed by sup.fail): %s" % now.get("last_fail"))
    x.done()


def t_real_fx_reads_the_build_only():
    class Round(object):
        def mods_of(self, sha):
            return ["FlowWorks"]

    class Fx(G.GameFx):
        def _round_fx(self):
            return Round()
    ok(Fx().game_own_mods("I0", "abc") == ["FlowWorks"], "GameFx.game_own_mods reads the build's mods through item_mods")


def main():
    for t in (t_incident_restages_no_worker, t_same_stop_routes_to_one_repair, t_own_mod_goes_back,
              t_names_read_the_cause_only, t_own_mod_by_namespace_goes_back, t_own_names_are_the_mods_alone,
              t_census_every_mod_is_named_by_its_names, t_fp_is_the_cause, t_failed_filing_restages,
              t_unreadable_build_is_the_environment, t_other_class_goes_back, t_real_fx_reads_the_build_only):
        print("--", t.__name__)
        t()
    print("selftest_relentless_stage_reroute: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
