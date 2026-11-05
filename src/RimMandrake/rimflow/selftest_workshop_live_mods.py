#!/usr/bin/env python3
"""selftest_workshop_live_mods.py -- LIVE_MODS_FIX_WORKSHOP_UNNAMEABLE: a Relentless `live-mods:` line may name a
workshop mod by packageId, and the game lane loads it with its dependency closure across BOTH mod roots (the Steam
workshop content folder and the game's Mods folder).

Before: TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING's clause needed Alien Worlds, its Tidally Locked add-on and Worldbuilder;
live-mods named only repo folders, so no staging ever loaded them and the proof read "Type not found:
AlienWorlds.PlanetTypeManager" 20 times (12.2M tokens, 8 generations). No game, no bridge, no disk outside a temp dir.
What must hold, each red under its mutant:
  modset_builder.package_closure walks dependencies across every root it scans, in load order, and names what no root
  holds; a packageId on live-mods stays on live_mods (it is loaded) but never reaches a deploy plan (it is no tree of
  ours), nor live_deploy; the running-load gate wants the packageId and its closure and names one installed nowhere;
  modlist_swap --enable adds the closure, dependencies first, and refuses by name a packageId installed nowhere.
"""
import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
sys.path.insert(0, HERE)
sys.path.insert(0, UTILS)
import modset_builder as M          # noqa: E402
import relentless_live as L         # noqa: E402
import relentless_live_round as R   # noqa: E402

FAILS = []


def ok(cond, msg):
    print("%s %s" % ("ok  " if cond else "FAIL", msg))
    if not cond:
        FAILS.append(msg)


def about(root, folder, pid, deps=()):
    d = os.path.join(root, folder, "About")
    os.makedirs(d)
    with open(os.path.join(d, "About.xml"), "w") as f:
        f.write("<ModMetaData><packageId>%s</packageId><modDependencies>%s</modDependencies></ModMetaData>"
                % (pid, "".join("<li><packageId>%s</packageId></li>" % x for x in deps)))


@contextlib.contextmanager
def two_roots():
    """A workshop root and a game Mods root, each holding half of the closure, as on this machine."""
    shop, mods = tempfile.mkdtemp(prefix="wlm_shop_"), tempfile.mkdtemp(prefix="wlm_mods_")
    about(shop, "3626210061", "7f.AlienWorlds", ["brrainz.harmony"])
    about(shop, "3631364335", "7f.alienworlds.tidallylocked", ["7f.alienworlds", "brrainz.harmony", "ludeon.rimworld"])
    about(mods, "Harmony", "brrainz.harmony")
    old = (M.DATA, M.WORKSHOP, M.LOCAL_MODS, M._SCANNED)
    M.DATA, M.WORKSHOP, M.LOCAL_MODS, M._SCANNED = os.path.join(shop, "none"), shop, mods, None
    try:
        yield mods
    finally:
        M.DATA, M.WORKSHOP, M.LOCAL_MODS, M._SCANNED = old


def t_closure_spans_both_roots():
    with two_roots():
        got, missing = M.package_closure(["7f.alienworlds.tidallylocked"])
        ok(got == ["brrainz.harmony", "7f.alienworlds", "7f.alienworlds.tidallylocked"] and missing == [],
           "the closure crosses the workshop and the Mods folder, dependencies first, DLC never missing: %s %s"
           % (got, missing))
        got, missing = M.package_closure(["ferny.worldbuilder", "7F.ALIENWORLDS"])
        ok(missing == ["ferny.worldbuilder"] and "7f.alienworlds" in got, "a packageId no root holds is named: %s" % missing)


class PlanFx(object):
    def __init__(self):
        self.plans = []

    def folded(self):
        return {}

    def deploy_plan(self, args, timeout):
        self.plans.append(args)
        return 0, ""

    def mods_of(self, sha):
        return ["Graffiti"]

    def running_load_gap(self, mods):
        return None


def t_live_mods_split():
    text = "live-mods: CreatureBehaviors, 7f.alienworlds.tidallylocked ferny.worldbuilder\nlive-deploy: Graffiti 7f.x\n"
    ok(R.live_mods(text) == ["CreatureBehaviors", "7f.alienworlds.tidallylocked", "ferny.worldbuilder", "Graffiti",
                             "7f.x"], "a packageId stays on live_mods: the load must hold it: %s" % R.live_mods(text))
    ok(R.live_deploy(text) == ["Graffiti"], "a packageId owes no tree: %s" % R.live_deploy(text))
    ok(R.is_package("7f.alienworlds") and not R.is_package("CreatureBehaviors"), "a dot is a packageId")
    fx = PlanFx()
    gap = R.mod_gap(fx, "s", text)
    ok(gap["mods"] == sorted(["CreatureBehaviors", "Graffiti", "7f.alienworlds.tidallylocked", "ferny.worldbuilder",
                              "7f.x"]) and not gap["error"], "the gap carries the packageIds to enable: %s" % gap)
    ok(fx.plans and all("." not in a.replace("--gate", "") for a in fx.plans) and "--mod Graffiti" in fx.plans[0],
       "but the deploy plan names repo folders only: %s" % fx.plans)
    fx = PlanFx()
    R._plan_into(fx, ["7f.alienworlds"], {"off": {}, "dll": [], "error": None})
    ok(fx.plans == [], "a list of packageIds alone plans nothing: %s" % fx.plans)


def t_running_load_gate_wants_the_closure():
    import live_def_check
    old = live_def_check.call_running_mods
    with two_roots() as mods:
        fx = L.Fx(mods_dir=mods)
        try:
            live_def_check.call_running_mods = lambda t: {"brrainz.harmony", "7f.alienworlds"}
            gap = fx.running_load_gap(["7f.alienworlds.tidallylocked"]) or ""
            ok("7f.alienworlds.tidallylocked" in gap and gap.startswith("not in the running load"),
               "a running load without the workshop mod is a gap naming it: %s" % gap)
            live_def_check.call_running_mods = lambda t: {"brrainz.harmony"}
            gap = fx.running_load_gap(["7f.alienworlds.tidallylocked"]) or ""
            ok("needs 7f.alienworlds" in gap, "and one without its dependency names the dependency: %s" % gap)
            live_def_check.call_running_mods = lambda t: {"brrainz.harmony", "7f.alienworlds",
                                                          "7f.alienworlds.tidallylocked"}
            ok(fx.running_load_gap(["7f.alienworlds.tidallylocked"]) is None, "a load holding the closure serves it")
            gap = fx.running_load_gap(["ferny.worldbuilder"]) or ""
            ok("installed in neither" in gap and "ferny.worldbuilder" in gap, "one installed nowhere says so: %s" % gap)
        finally:
            live_def_check.call_running_mods = old


def t_enable_adds_the_closure():
    import modlist_swap as S
    import zoom_guard
    tmp = tempfile.mkdtemp(prefix="wlm_cfg_")
    live = os.path.join(tmp, "ModsConfig.xml")
    with open(live, "w") as f:
        f.write("<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>brrainz.harmony</li></activeMods>"
                "</ModsConfigData>")
    old = (S.LIVE, S.FULL, zoom_guard.with_zoom)
    S.LIVE, S.FULL, zoom_guard.with_zoom = live, os.path.join(tmp, "none.xml"), lambda ids: list(ids)
    try:
        with two_roots():
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = S.enable(["7f.alienworlds.tidallylocked"], False)
            ok(rc == 0 and "enable   : 7f.alienworlds, 7f.alienworlds.tidallylocked" in out.getvalue(),
               "enable adds the packageId and its workshop dependency, dependency first: %s" % out.getvalue())
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = S.enable(["ferny.worldbuilder"], True)
            ok(rc == 2 and "ferny.worldbuilder (installed in neither" in out.getvalue(),
               "a packageId installed nowhere is refused by name: %s" % out.getvalue())
            with open(live) as f:
                ok("ferny" not in f.read(), "and nothing is written")
    finally:
        S.LIVE, S.FULL, zoom_guard.with_zoom = old


def main():
    for t in (t_closure_spans_both_roots, t_live_mods_split, t_running_load_gate_wants_the_closure,
              t_enable_adds_the_closure):
        print("--", t.__name__)
        t()
    print("selftest_workshop_live_mods: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
