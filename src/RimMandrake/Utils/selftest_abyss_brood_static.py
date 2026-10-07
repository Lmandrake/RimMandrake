#!/usr/bin/env python3
"""Planted-break selftest for src/RimMandrake/Abyss/validation.py brood_check()
(ABYSS_LIGHTFALL_BROOD_WRECK_1). Copies the Abyss mod and the one Utinni patch it reads into a
temp tree, proves brood_check() passes on the real files (sanity), then plants one break at a
time and proves each is caught. A checker that cannot fail proves nothing.

    python3 selftest_abyss_brood_static.py
"""
from __future__ import annotations

import importlib.util
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))            # .../src
ABYSS = os.path.join(SRC, "RimMandrake", "Abyss")
UT_PATCH = os.path.join(SRC, "RimUtinni", "UtinniPatches", "Patches", "RUT_Lightfall_BroodLair.xml")


def _load(mod_dir):
    spec = importlib.util.spec_from_file_location("abyss_validation_copy", os.path.join(mod_dir, "validation.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.HERE = mod_dir
    return m


def _tree(tmp):
    mod = os.path.join(tmp, "src", "RimMandrake", "Abyss")
    for sub in ("Defs", "Source", "Patches", "Textures"):
        shutil.copytree(os.path.join(ABYSS, sub), os.path.join(mod, sub),
                        ignore=shutil.ignore_patterns("bin", "obj", "__pycache__"))
    shutil.copy(os.path.join(ABYSS, "validation.py"), mod)
    ut = os.path.join(tmp, "src", "RimUtinni", "UtinniPatches", "Patches")
    os.makedirs(ut)
    shutil.copy(UT_PATCH, ut)
    return mod


def _edit(path, old, new):
    s = open(path).read()
    if old not in s:
        raise SystemExit("planted-break setup failed: %r not in %s" % (old, path))
    open(path, "w").write(s.replace(old, new, 1))


BREAKS = [
    ("dragon in a description", "Defs/BroodLair/RM_BroodLair.xml",
     "Awake, nothing you carry", "Awake, the dragon"),
    ("a greedy part makes a modest haul wake her", "Defs/BroodLair/RM_RescueShipWreck.xml",
     "<greed>0.18</greed>", "<greed>0.70</greed>"),
    ("great bone placeable off the ship", "Defs/BroodLair/RM_BroodLair.xml",
     "<li>PlaceWorker_OnSubstructure</li>", ""),
    ("a stocked part with no salvage bill", "Defs/BroodLair/RM_RescueShipWreck.xml",
     "<RM_ShipPart_RescueBerth>1</RM_ShipPart_RescueBerth>\n        </stock>",
     "<RM_ShipPart_RescueBerth>1</RM_ShipPart_RescueBerth>\n          <RM_ShipPart_SealGaskets>1</RM_ShipPart_SealGaskets>\n        </stock>"),
    ("refused part consumed", "Defs/BroodLair/RM_RescueShipWreck.xml",
     "<accepted>false</accepted>\n      </li>\n    </comps>",
     "<accepted>false</accepted>\n      </li>\n      <li Class=\"CompProperties_UseEffectDestroySelf\" />\n    </comps>"),
    ("brood-mother killable", "Defs/BroodLair/RM_BroodLair.xml",
     "<IncomingDamageFactor>0.03</IncomingDamageFactor>", "<IncomingDamageFactor>0.5</IncomingDamageFactor>"),
    ("a setting lost its control", "Source/RM_AbyssMod.cs",
     'list.CheckboxLabeled("A bonded summ kills what it finds", ref baneEnabled,', 'list.CheckboxLabeled("A bonded summ kills what it finds", ref cryptidSignsEnabled,'),
    ("a file dropped from the csproj", "Source/RM_Abyss.csproj",
     '<Compile Include="RM_ShipWreck.cs" />', ""),
    ("whole haul no longer wakes her", "Source/RM_BroodWakeLogic.cs",
     "public const float EggWeight = 0.35f;", "public const float EggWeight = 0.05f;"),
    ("dragon in a C# string", "Source/RM_BroodEgg.cs",
     '"A summ has come for the egg"', '"A dragon has come for the egg"'),
]


def main():
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        mod = _tree(tmp)
        base = _load(mod).brood_check()
        if base:
            print("FAIL sanity: brood_check fails on the real files: %s" % base)
            return 1
        print("ok   sanity: brood_check passes on the real files")
    # planted breaks, each on a fresh copy (one break at a time)
    for name, rel, old, new in BREAKS:
        with tempfile.TemporaryDirectory() as tmp:
            mod = _tree(tmp)
            _edit(os.path.join(mod, rel), old, new)
            got = _load(mod).brood_check()
            if got:
                print("ok   caught: %s -> %s" % (name, got[0][:90]))
            else:
                failures += 1
                print("FAIL missed: %s" % name)
    # the Utinni patch deleted
    with tempfile.TemporaryDirectory() as tmp:
        mod = _tree(tmp)
        os.remove(os.path.join(tmp, "src", "RimUtinni", "UtinniPatches", "Patches", "RUT_Lightfall_BroodLair.xml"))
        got = _load(mod).brood_check()
        if any("RUT_Lightfall" in g for g in got):
            print("ok   caught: Utinni patch missing")
        else:
            failures += 1
            print("FAIL missed: Utinni patch missing")
    total = len(BREAKS) + 2
    print("%s abyss brood static selftest: %d/%d" % ("PASS" if failures == 0 else "FAIL", total - failures, total))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
