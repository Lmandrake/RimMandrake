"""Acceptance test for RIMMANDRAKE_SHIP_PYRELANDS_TRIBES_DEFAULT_OFF.

Pyrelands 0.1.0 is the biome alone (owner card 2026-11-13, "One mod, Tribes next version"), so every Deep Desert
Tribes switch in mandrake.rut.pyrelandsmechanics must ship OFF: the field initialiser AND the Scribe_Values default
(a missing key in an old settings file reads the Scribe default). Run from the repo root:
    python3 <this file>
Exit 0 = pass, 1 = fail (names each switch still on).
"""
import re
import sys

SRC = "src/RimUtinni/PyrelandsMechanics/Source/PyrelandsMechanicsMod.cs"
SWITCHES = ("fireRiteEnabled", "flameHarvestEnabled", "arsonJusticeEnabled")

text = open(SRC, encoding="utf-8").read()
bad = []
for name in SWITCHES:
    init = re.findall(r"public\s+static\s+bool\s+" + name + r"\s*=\s*(true|false)\s*;", text)
    scribe = re.findall(r"Scribe_Values\.Look\(\s*ref\s+" + name + r'\s*,\s*"' + name + r'"\s*,\s*(true|false)\s*\)', text)
    if init != ["false"]:
        bad.append(f"{name}: initialiser {init or 'NOT FOUND'}")
    if scribe != ["false"]:
        bad.append(f"{name}: Scribe default {scribe or 'NOT FOUND'}")
if bad:
    print("FAIL: Tribes switches not shipped off:\n  " + "\n  ".join(bad))
    sys.exit(1)
print(f"PASS: {len(SWITCHES)} Tribes switches ship off (initialiser and Scribe default)")
