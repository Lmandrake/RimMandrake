#!/usr/bin/env python3
"""ZOOM_MOD_ENFORCE_NOT_JUST_ONE_DOOR: every door that writes the live list leaves a zoom mod in it (temp files only)."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modcheck"))
import zoom_guard as Z
import modlist_swap as S
import modset_builder as MB

fails = []
def check(name, cond):
    if not cond:
        fails.append(name)

def cfg(ids):
    return "<ModsConfigData>\n  <activeMods>\n%s  </activeMods>\n</ModsConfigData>" % "".join("    <li>%s</li>\n" % i for i in ids)

BARE = ["brrainz.harmony", "ludeon.rimworld", "mandrake.rm.x"]
with tempfile.TemporaryDirectory() as d:
    live, src = os.path.join(d, "live.xml"), os.path.join(d, "min.xml")
    open(src, "w").write(cfg(BARE))
    # door 1: modlist_swap.swap of a zoom-less list (the --minimal swap that lost it)
    S.LIVE = live
    S.STORE = os.path.join(d, "store")
    Z.has_zoom  # noqa
    orig = Z.zoom_installed; Z.zoom_installed = lambda: True
    try:
        S.swap(src, True)
        ids = Z.active_ids(open(live).read())
        check("swap adds zoom after harmony", ids[:2] == ["brrainz.harmony", Z.ZOOM])
        # Camera+ satisfies the rule: never add the conflicting one on top
        open(src, "w").write(cfg(BARE + [Z.CAMERAPLUS]))
        S.swap(src, True)
        check("cameraplus list not given the second zoom", Z.ZOOM not in Z.active_ids(open(live).read()))
        # door 2: enable
        open(live, "w").write(cfg(BARE)); S.FULL = src
        S.enable(["brrainz.rimbridgeserver"], True)
        check("enable adds zoom", Z.has_zoom(Z.active_ids(open(live).read())))
        # door 3: modset_builder.write_config
        MB.CONFIG = live
        MB.write_config(list(BARE), src)
        check("write_config adds zoom", Z.has_zoom(Z.active_ids(open(live).read())))
        # check_live repair
        open(live, "w").write(cfg(BARE))
        Z.MODS = live
        import game_paths; game_paths.MODS_CONFIG = live
        check("check_live reports missing", Z.check_live() and Z.check_live().startswith("REFUSED"))
        check("repair adds", Z.check_live(repair=True).startswith("added") and Z.check_live() is None)
    finally:
        Z.zoom_installed = orig
    # not installed -> loud refusal, nothing written
    open(live, "w").write(cfg(BARE)); before = open(live).read()
    Z.zoom_installed = lambda: False
    try:
        try:
            Z.enforce_file(live); check("uninstalled refuses", False)
        except RuntimeError:
            check("uninstalled refuses", open(live).read() == before)
    finally:
        Z.zoom_installed = orig
check("shipped MINIMAL carries a zoom mod", Z.has_zoom(Z.active_ids(open(S.MINIMAL).read())))
print("selftest_zoom_guard: %s" % ("FAIL " + ", ".join(fails) if fails else "OK"))
sys.exit(1 if fails else 0)
