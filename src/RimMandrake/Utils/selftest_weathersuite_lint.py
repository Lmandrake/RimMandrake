#!/usr/bin/env python3
"""Planted-defect selftest for lint_weathersuite_defs.py: clean on the real mod, then one planted defect at a time is caught.
The geometry def lives in the RimUtinni wiring mod, so its plants go through a copied --geometry-dir (see below).

    python3 src/RimMandrake/Utils/selftest_weathersuite_lint.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modpack_lint_harness as H  # noqa: E402

I = "Defs/IncidentDefs/IncidentDefs_DarkAurora.xml"
C = "Defs/GameConditionDefs/GameConditionDefs_DarkAurora.xml"
T = "Defs/GameConditionDefs/GameConditionDefs_TerminatorFront.xml"
K = "Source/Kernel/RM_WeatherKernel.cs"
GEO = os.path.join(os.path.dirname(HERE), "..", "RimUtinni", "AshkarrWeatherSuite", "Defs", "WeatherGeometryDefs", "WeatherGeometryDefs_Ashkarr.xml")
PLANTS = [
    ("incident condition typo", I, "<gameCondition>RM_WS_DarkAurora</gameCondition>", "<gameCondition>RM_WS_DarkAuroraa</gameCondition>", "gameCondition"),
    ("incident targets a map", I, "<li>World</li>", "<li>Map_PlayerHome</li>", "targets the World"),
    ("incident worker swapped", I, "IncidentWorker_NightsideAurora</workerClass>", "IncidentWorker_Aurora</workerClass>", "worker"),
    ("condition class swapped", C, "GameCondition_DarkAuroraMax</conditionClass>", "GameCondition_Aurora</conditionClass>", "GameCondition_DarkAuroraMax"),
    ("front not permanent-capable", T, "<canBePermanent>true</canBePermanent>", "<canBePermanent>false</canBePermanent>", "canBePermanent"),
    ("front allowed underground", T, "<allowUnderground>false</allowUnderground>", "<allowUnderground>true</allowUnderground>", "underground"),
    ("kernel imports Verse", K, "using System;", "using System;\nusing Verse;", "ws-kernel"),
    ("kernel missing from the csproj", "Source/WeatherSuiteHook.csproj", '<Compile Include="Kernel\\RM_WeatherKernel.cs" />', "", "ws-kernel"),
    ("hand copy of the arc", "Source/WeatherSuiteHook.cs", "return RM_WeatherKernel.ArcDegrees(", "return Mathf.Acos(0f) + RM_WeatherKernel.ArcDegrees(", "hand copy of the arc"),
    ("slider floor drifts from vanilla", "Source/WeatherSuiteSettings.cs", "list.Slider(auroraSkyBrightness, 0.73f, 2f)", "list.Slider(auroraSkyBrightness, 0.5f, 2f)", "slider floor"),
    ("settings Scribe default drifts", "Source/WeatherSuiteSettings.cs", '"auroraSkyBrightness", 1.15f)', '"auroraSkyBrightness", 1.5f)', "settings-scribed"),
    ("incident class typo", I, "IncidentWorker_NightsideAurora</workerClass>", "IncidentWorker_NightsideAuror</workerClass>", "class-resolves"),
]


def geometry_plants():
    """Plants into a COPY of the wiring mod's geometry def, linted with --geometry-dir so the real file is never touched."""
    plants = [
        ("dark side starts inside the wall", "<nightsideBandMinArc>117</nightsideBandMinArc>", "<nightsideBandMinArc>100</nightsideBandMinArc>", "inside the wall"),
        ("wall arcs reversed", "<terminatorBandMinArc>63</terminatorBandMinArc>", "<terminatorBandMinArc>130</terminatorBandMinArc>", "0 <= min <= max"),
        ("substellar latitude off the globe", "<substellarLat>0</substellarLat>", "<substellarLat>120</substellarLat>", "off the globe"),
    ]
    bad = 0
    orig = open(GEO, encoding="utf-8").read()
    for label, old, new, want in plants:
        if old not in orig:
            print(f"FAIL {label}: pattern not found")
            bad += 1
            continue
        with tempfile.TemporaryDirectory() as td:
            open(os.path.join(td, "g.xml"), "w", encoding="utf-8").write(orig.replace(old, new, 1))
            p = subprocess.run([sys.executable, os.path.join(HERE, "lint_weathersuite_defs.py"), "--quiet", "--geometry-dir", td], capture_output=True, text=True)
            hit = p.returncode == 1 and any(l.startswith("ERROR") and want in l for l in p.stdout.splitlines())
            print(("ok   " if hit else "FAIL ") + label)
            bad += not hit
    with tempfile.TemporaryDirectory() as td:   # two geometry defs: ambiguous
        shutil.copy(GEO, os.path.join(td, "a.xml"))
        shutil.copy(GEO, os.path.join(td, "b.xml"))
        p = subprocess.run([sys.executable, os.path.join(HERE, "lint_weathersuite_defs.py"), "--quiet", "--geometry-dir", td], capture_output=True, text=True)
        hit = p.returncode == 1 and "ship exactly one" in p.stdout
        print(("ok   " if hit else "FAIL ") + "two geometry defs")
        bad += not hit
    return bad


if __name__ == "__main__":
    rc = H.run("WeatherSuite", "lint_weathersuite_defs.py", PLANTS)
    bad = geometry_plants()
    sys.exit(1 if (rc or bad) else 0)
