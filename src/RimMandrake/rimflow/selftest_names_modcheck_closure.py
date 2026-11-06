#!/usr/bin/env python3
"""GAMEENV_FIX_PROOFSITE_9E77C59D_ITEMS_WAIT: the live gate plans every packageId a proof's `modcheck/cli.py run <Mod>`
composes, so modcheck never refuses the run as stale_load on a load the gate itself chose.

2026-11-06 09:03Z and 09:54Z: ACC_BIOMES_FIXES_LIVE_RERUN_1's A2 named live-mods RimMandrake.Biomes, GimmeSomeSlack,
UtinniPatches; modcheck composed LeaningScrub's tier (it wants mandrake.rsw.swbestiary), found it absent in the running
load and refused: "the running load is not the composed list (restart the game on it): not loaded: mandrake.rsw.swbestiary".
No lane step could fix it: the gate never knew modcheck's list.

Offline and deterministic: a synthetic index and a fake composer for the gate logic; the real modcheck runner only for
LeaningScrub's composed list, which reads the repo's src/ and modset_builder tiers (no game folder, no git)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless_names as N  # noqa: E402

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


# the A2 line as it stood at 6e631066a811 (frozen here: the live file may move on)
A2 = ("live-proof A2: MODCHECK_SKIP_DEPLOY=1 MODCHECK_KEEP_MODLIST=1 WSLENV=MODCHECK_SKIP_DEPLOY:MODCHECK_KEEP_MODLIST "
      "python.exe src/RimMandrake/Utils/modcheck/cli.py run LeaningScrub --chains bloom --gate off --purpose fix "
      "--item LeaningScrub=ACC_BIOMES_FIXES_LIVE_RERUN_1 --seat BENCH < /dev/null; python3 "
      "src/RimMandrake/Utils/modcheck/live_queue/row_verdict.py --max-age-min 30 --mod LeaningScrub --row bloom_toggle_off_quiet")
TEXT = "live-mods: RimMandrake.Biomes, GimmeSomeSlack, UtinniPatches\n" + A2 + "\n"


def index():
    return N.Index(["GimmeSomeSlack", "UtinniPatches", "SWBestiary", "AshkarrWeatherSuite"],
                   {"LeaningScrub": ("RimMandrake.Biomes", "LeaningScrub")},
                   ["GimmeSomeSlack", "UtinniPatches", "SWBestiary", "AshkarrWeatherSuite", "RimMandrake.Biomes"],
                   ["brrainz.rimbridgeserver", "brrainz.harmony"],
                   {"mandrake.rsw.swbestiary": "SWBestiary", "mandrake.rut.patches": "UtinniPatches",
                    "mandrake.rm.biomes": "RimMandrake.Biomes", "mandrake.rm.weathersuite": "AshkarrWeatherSuite",
                    "mandrake.rm.gimmesomeslack": "GimmeSomeSlack"},
                   {}, {})


def t_parse():
    ok(N.modcheck_runs(TEXT) == ["LeaningScrub"], "the A2 line hands LeaningScrub to modcheck", N.modcheck_runs(TEXT))
    two = "live-proof A1: python.exe src/RimMandrake/Utils/modcheck/cli.py run Miasma RustCathedral --gate off\n"
    ok(N.modcheck_runs(two) == ["Miasma", "RustCathedral"], "several mods before the first flag", N.modcheck_runs(two))
    tail = "live-proof A1: python.exe src/RimMandrake/Utils/modcheck/cli.py run Miasma; echo done\n"
    ok(N.modcheck_runs(tail) == ["Miasma"], "a shell separator ends the mod list", N.modcheck_runs(tail))
    prose = "# python.exe src/RimMandrake/Utils/modcheck/cli.py run Miasma --gate off\n"
    ok(N.modcheck_runs(prose) == [], "a comment line is no proof line")
    ok(N.modcheck_runs("live-proof A1: python3 src/RimMandrake/Utils/modcheck/cli.py status Miasma\n") == [],
       "a modcheck verb other than run composes nothing")


def t_real_composed():
    ids = N.modcheck_composed("LeaningScrub")
    ok("mandrake.rm.biomes" in ids, "sanity: the real runner composes LeaningScrub's composed mod", ids)
    ok("mandrake.rsw.swbestiary" in ids, "the real runner's LeaningScrub list holds the bestiary the game lacked", ids)


def t_gate():
    ix = index()
    named = N.check(["RimMandrake.Biomes", "GimmeSomeSlack", "UtinniPatches"], ix)["mods"]
    nd = N.needs(TEXT, {}, named, [], ix)
    add = {N._one(ix)(a["mod"]): a["src"] for a in nd["add"]}
    ok(add.get("SWBestiary") == "proof_modcheck", "the gate adds the bestiary modcheck will check", nd["add"])
    ok(any(N._one(ix)(m) == "SWBestiary" for m in nd["planned"]), "the planned load holds it", nd["planned"])
    ok("RimMandrake.Biomes" not in add and "UtinniPatches" not in add, "what live-mods named is never re-added", add)
    full = TEXT.replace("UtinniPatches", "UtinniPatches, SWBestiary, AshkarrWeatherSuite, brrainz.rimbridgeserver", 1)
    named2 = N.check(["RimMandrake.Biomes", "GimmeSomeSlack", "UtinniPatches", "SWBestiary", "AshkarrWeatherSuite",
                      "brrainz.rimbridgeserver"], ix)["mods"]
    ok(N.needs(full, {}, named2, [], ix)["add"] == [], "a proof naming the whole composed list gets no addition")
    # an unknown mod is a warning, never a crash or an addition
    bad = "live-proof A1: python.exe src/RimMandrake/Utils/modcheck/cli.py run NoSuchModHere --gate off\n"
    adv = N.advise(bad, {}, set(named), ix, composer=lambda m: (_ for _ in ()).throw(RuntimeError("no src folder")))
    ok(adv and all(a["src"] not in N.SURE for a in adv), "an uncomposable mod only warns", adv)
    ok("proof_modcheck" in N.SURE and "proof_modcheck" in N.SELF_EVIDENT, "a modcheck need is enforced and self-evident")
    # the injected composer is what the gate reads
    adv = N.advise(TEXT, {}, set(named), ix, composer=lambda m: ["mandrake.rm.weathersuite"])
    ok([(a["mod"], a["src"]) for a in adv if a["src"] == "proof_modcheck"] == [("mandrake.rm.weathersuite", "proof_modcheck")],
       "advise asks the composer it is given", adv)


t_parse()
t_real_composed()
t_gate()
print("%d ok, %d failed" % (n_ok, len(fails)))
sys.exit(1 if fails else 0)
