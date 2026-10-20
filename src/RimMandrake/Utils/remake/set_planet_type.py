#!/usr/bin/env python3
"""set_planet_type.py — save Alien Worlds' planet type for new worlds, so it survives launches.

Why (world remake run 2026-10-20): with no Alien Worlds settings file in Config, every PAINT
launch started with `AlienWorldsSettings.selectedPlanetType = "Default"` — a VANILLA planet —
and the conductor had to force TidallyLocked live (`jawa/static_call AlienWorlds.PlanetTypeManager
set_Current TidallyLocked`) before each generation.

Mechanism (AlienWorlds.dll, 7f.alienworlds, decompiled 2026-10-20 with ilspycmd):
  * `AlienWorldsFramework : Mod` calls `GetSettings<AlienWorldsSettings>()` in its constructor,
    so the file is `Config/Mod_<mod folder>_AlienWorldsFramework.xml`, read once at startup.
  * `AlienWorldsSettings.ExposeData`: `Scribe_Values.Look(ref selectedPlanetType,
    "selectedPlanetType", "Default")`.
  * `Startup` (StaticConstructorOnStartup): ONLY on the Standalone backend (Worldbuilder NOT
    loaded — true on PAINT) it sets `PlanetTypeManager.Current = selectedPlanetType`; an unknown
    defName falls back to "Default" (so `7f.alienworlds.tidallylocked` must be active for
    TidallyLocked to stick). With Worldbuilder loaded (the full list) the setting is ignored and
    Worldbuilder's preset decides — writing this file is harmless there.
  * The game writes this file back only when someone closes this mod's settings window.

Verify the result from the WORLD, never from this file: a saved world carries
`<alienWorldsFrameworkPlanetType>TidallyLocked</alienWorldsFrameworkPlanetType>`.

    python3 src/RimMandrake/Utils/remake/set_planet_type.py            # dry run: state + plan
    python3 src/RimMandrake/Utils/remake/set_planet_type.py --apply    # write (idempotent)
    python3 src/RimMandrake/Utils/remake/set_planet_type.py --check    # exit 0 iff already set
Options: --type <PlanetTypeDef defName> (default TidallyLocked), --config-dir <dir> (tests).
Exit: 0 ok/already set · 1 --check and not set · 2 refused (bad file, mod folder unverifiable).
"""
import argparse
import os
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

MOD_FOLDER = "3626210061"          # Steam workshop id of Alien Worlds Framework (7f.alienworlds)
MOD_CLASS = "AlienWorldsFramework"
SETTINGS_CLASS = "AlienWorlds.AlienWorldsSettings"
FIELD = "selectedPlanetType"
PACKAGE_ID = "7f.alienworlds"
WORKSHOP = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"


def default_config_dir():
    from game_paths import LOCALLOW
    return os.path.join(LOCALLOW, "Config")


def verify_mod_folder(workshop=WORKSHOP):
    """None if the workshop folder holds 7f.alienworlds (or the workshop is not visible), else
    a refusal string: a settings file under the wrong folder name is read by nothing."""
    about = os.path.join(workshop, MOD_FOLDER, "About", "About.xml")
    if not os.path.isdir(workshop):
        return None
    if not os.path.isfile(about):
        return f"{about} missing: Alien Worlds is no longer workshop folder {MOD_FOLDER}"
    text = open(about, encoding="utf-8-sig", errors="replace").read()
    m = re.search(r"<packageId>\s*([^<\s]+)\s*</packageId>", text)
    if not m or m.group(1).lower() != PACKAGE_ID:
        return f"{about} is {m.group(1) if m else '?'}, not {PACKAGE_ID}"
    return None


def settings_path(config_dir):
    return os.path.join(config_dir, f"Mod_{MOD_FOLDER}_{MOD_CLASS}.xml")


def render(value):
    return ('﻿<?xml version="1.0" encoding="utf-8"?>\n<SettingsBlock>\n'
            f'\t<ModSettings Class="{SETTINGS_CLASS}">\n'
            f'\t\t<{FIELD}>{value}</{FIELD}>\n'
            '\t</ModSettings>\n</SettingsBlock>\n')


def read_current(path):
    """(value or None, error or None). A missing file reads as None (the mod's default)."""
    if not os.path.exists(path):
        return None, None
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return None, f"unparseable: {exc}"
    ms = root.find("ModSettings")
    if root.tag != "SettingsBlock" or ms is None or ms.get("Class") != SETTINGS_CLASS:
        return None, "not an AlienWorldsSettings block"
    el = ms.find(FIELD)
    return (el.text or "").strip() if el is not None else None, None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--type", default="TidallyLocked")
    ap.add_argument("--config-dir")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--workshop", default=WORKSHOP, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)

    bad = verify_mod_folder(a.workshop)
    if bad:
        print(f"REFUSED: {bad}")
        return 2
    path = settings_path(a.config_dir or default_config_dir())
    cur, err = read_current(path)
    if err:
        print(f"REFUSED: {path}: {err} — inspect it by hand")
        return 2
    shown = cur if cur is not None else "(no file: mod default 'Default', a vanilla planet)"
    if cur == a.type:
        print(f"ALREADY SET {FIELD}={cur} in {path}")
        return 0
    if a.check:
        print(f"NOT SET {FIELD}={shown} in {path}")
        return 1
    if not a.apply:
        print(f"DRY RUN would set {FIELD}: {shown} -> {a.type} in {path} (--apply to write)")
        return 0
    if os.path.exists(path):
        shutil.copy2(path, path + time.strftime(".bak-%Y%m%dT%H%M%S"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(a.type))
    os.replace(tmp, path)
    back, err = read_current(path)
    if back != a.type:
        print(f"FAILED read-back {back!r} ({err}) in {path}")
        return 2
    print(f"WROTE {FIELD}={back} in {path} (was {shown}); takes effect at the next launch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
