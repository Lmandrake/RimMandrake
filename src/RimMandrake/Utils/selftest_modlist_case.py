#!/usr/bin/env python3
"""MINIMALLIST_FIX_OUTERRIMCORE_CTOR_NRE: every list-writing door writes lowercase packageIds, and every stored list
is lowercase (temp files only, except the read of infrastructure/state/modlists)."""
import os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "modcheck"))
import zoom_guard as Z
import modlist_swap as S
import modset_builder as MB
import modlist_case as C
import runner as R

fails = []
def check(name, cond):
    if not cond:
        fails.append(name)

def cfg(ids):
    return "<ModsConfigData>\n  <activeMods>\n%s  </activeMods>\n</ModsConfigData>" % "".join("    <li>%s</li>\n" % i for i in ids)

def ids_of(p):
    return Z.active_ids(open(p, encoding="utf-8").read())

# The engine's rule, as decompiled from Verse.ModsConfig 1.6: the set holds raw strings, IsActive lowercases the query.
def engine_is_active(file_ids, package_id):
    return package_id.lower() in set(file_ids)

MIXED = ["brrainz.harmony", Z.ZOOM, "ludeon.rimworld", "Neronix17.OuterRim.Core", "erdelf.HumanoidAlienRaces"]
check("instance: the old MINIMAL spelling reads inactive to the engine",
      not engine_is_active(MIXED, "Neronix17.OuterRim.Core"))

# the stored lists, MINIMAL first: the instance this item was filed on
mini = os.path.join(C.STORE, "ModsConfig.MINIMAL.xml")
check("MINIMAL holds outer rim core lowercase", "neronix17.outerrim.core" in ids_of(mini))
check("MINIMAL: outer rim core reads active to the engine", engine_is_active(ids_of(mini), "Neronix17.OuterRim.Core"))
check("every stored list lowercase", C.stored() == 0)

with tempfile.TemporaryDirectory() as d:
    live, src = os.path.join(d, "live.xml"), os.path.join(d, "min.xml")
    orig = Z.zoom_installed; Z.zoom_installed = lambda: True
    try:
        # lower_text touches activeMods only
        t = cfg(MIXED).replace("</ModsConfigData>", "<knownExpansions><li>Keep.Me</li></knownExpansions></ModsConfigData>")
        lt = Z.lower_text(t)
        check("lower_text lowercases activeMods", Z.mixed_case(Z.active_ids(lt)) == [])
        check("lower_text leaves the rest", "Keep.Me" in lt and len(lt) == len(t))
        # door 1: swap
        open(src, "w").write(cfg(MIXED))
        S.LIVE = live; S.STORE = os.path.join(d, "store")
        S.swap(src, True)
        check("swap writes lowercase", Z.mixed_case(ids_of(live)) == [] and "neronix17.outerrim.core" in ids_of(live))
        # door 2: enable (with_zoom)
        check("with_zoom lowercases", Z.with_zoom(MIXED) == [m.lower() for m in MIXED])
        open(live, "w").write(cfg(MIXED)); S.FULL = src
        S.enable(["Kutte.Stairs"], True)
        got = ids_of(live)
        check("enable writes lowercase", Z.mixed_case(got) == [] and "kutte.stairs" in got)
        # door 3: write_config
        MB.CONFIG = live
        MB.write_config(list(MIXED) + ["neronix17.outerrim.core"], src)
        check("write_config writes lowercase", Z.mixed_case(ids_of(live)) == [])
        check("write_config writes a repeat once", ids_of(live).count("neronix17.outerrim.core") == 1)
        # door 4: compose_test_list
        open(live, "w").write(cfg(MIXED))
        R.compose_test_list(["Kutte.Stairs"], config_path=live, zoom_installed=True)
        got = ids_of(live)
        check("compose_test_list writes lowercase", Z.mixed_case(got) == [] and "kutte.stairs" in got)
        check("compose_test_list adds no duplicate", len(got) == len({g.lower() for g in got}))
        # check_live: reports, then repairs
        open(live, "w").write(cfg(MIXED))
        import game_paths; game_paths.MODS_CONFIG = live
        r = Z.check_live()
        check("check_live reports capitals", bool(r) and r.startswith("REFUSED") and "Neronix17.OuterRim.Core" in r)
        r = Z.check_live(repair=True)
        check("check_live repair lowercases", bool(r) and r.startswith("lowercased") and Z.check_live() is None)
        check("modlist_case live sees it clean", C.live() == 0)
        # the live-proof reader
        lg = os.path.join(d, "Player.log")
        open(lg, "w").write("x\n<color=#00FFFFFF>%s</color> 1.6.9306 ::\nError ... at OuterRimCore.%s () [0x0000b]\n" % (C.BANNER, C.NRE))
        check("log reader fails the instance", C.log(lg) == 1)
        open(lg, "w").write("x\n<color=#00FFFFFF>%s</color> 1.6.9306 ::\nok\n" % C.BANNER)
        check("log reader passes a clean load", C.log(lg) == 0)
        open(lg, "w").write("no outer rim here\n")
        check("log reader says unmeasured without the mod", C.log(lg) == 2)
    finally:
        Z.zoom_installed = orig

if fails:
    print("FAIL selftest_modlist_case: " + "; ".join(fails))
    sys.exit(1)
print("PASS selftest_modlist_case")
