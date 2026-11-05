#!/usr/bin/env python3
"""Selftest for STEVE_STALE_LOAD_DIAGNOSE_CAMERA_MOD_GONE: runner.compose_test_list names the zoom mod
(ray1203.simplecamerasetting) only when its folder is installed on the host. RimWorld silently drops an id with no
folder, so an unconditional add made the run's own composed list fail its load check (SteveDesktop job
J20261104T074700Z-42d8eb, INVALID stale_load `not loaded: ray1203.simplecamerasetting`). Offline: temp ModsConfig,
the install probe injected and, for the default path, a temp WORKSHOP/LOCAL_MODS pair."""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import runner  # noqa: E402
import zoom_guard  # noqa: E402

FAILS = []


def ok(what, cond, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def config(ids):
    fd, path = tempfile.mkstemp(suffix="_ModsConfig.xml")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("<ModsConfigData>\n  <activeMods>\n%s  </activeMods>\n</ModsConfigData>\n"
                % "".join("    <li>%s</li>\n" % p for p in ids))
    return path


def active(path):
    return runner.active_mods(path)


BASE = ["ludeon.rimworld", "brrainz.harmony"]
TOY = "mandrake.rm.toy"

# 1. not installed: the zoom id is NOT composed (the instance: Steve before its folder arrived)
p = config(BASE)
try:
    added = runner.compose_test_list([TOY], config_path=p, zoom_installed=False)
    ok("absent zoom mod: not composed", zoom_guard.ZOOM not in active(p), active(p))
    ok("absent zoom mod: the mod under test still composed", added == [TOY], added)
finally:
    os.unlink(p)

# 2. installed: the zoom id IS composed (owner 2026-10-04 rule kept where the mod exists)
p = config(BASE)
try:
    added = runner.compose_test_list([TOY], config_path=p, zoom_installed=lambda: True)
    ok("installed zoom mod: composed first", added == [zoom_guard.ZOOM, TOY], added)
finally:
    os.unlink(p)

# 3. list already carries Camera+: nothing added, no probe needed
p = config(BASE + [zoom_guard.CAMERAPLUS])
try:
    def boom():
        raise AssertionError("probe called")
    added = runner.compose_test_list([TOY], config_path=p, zoom_installed=boom)
    ok("Camera+ present: no zoom added and the probe is not consulted", added == [TOY], added)
finally:
    os.unlink(p)

# 4. default probe reads the host's folders: empty mod roots -> not composed; a folder with its About -> composed
import game_paths  # noqa: E402
root = tempfile.mkdtemp()
saved = (game_paths.WORKSHOP, game_paths.LOCAL_MODS)
try:
    ws, lm = os.path.join(root, "ws"), os.path.join(root, "mods")
    os.makedirs(ws), os.makedirs(lm)
    game_paths.WORKSHOP, game_paths.LOCAL_MODS = ws, lm
    p = config(BASE)
    try:
        runner.compose_test_list([TOY], config_path=p)
        ok("default probe, empty roots: zoom not composed", zoom_guard.ZOOM not in active(p), active(p))
    finally:
        os.unlink(p)
    os.makedirs(os.path.join(lm, "3232415388", "About"))
    with open(os.path.join(lm, "3232415388", "About", "About.xml"), "w", encoding="utf-8") as f:
        f.write("<ModMetaData><packageId>ray1203.SimpleCameraSetting</packageId></ModMetaData>")
    p = config(BASE)
    try:
        runner.compose_test_list([TOY], config_path=p)
        ok("default probe, folder in local Mods (Steve's 3232415388 shape): zoom composed",
           zoom_guard.ZOOM in active(p), active(p))
    finally:
        os.unlink(p)
finally:
    game_paths.WORKSHOP, game_paths.LOCAL_MODS = saved
    shutil.rmtree(root, ignore_errors=True)

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
