#!/usr/bin/env python3
"""BIOME_TRANSITIONS_JUDGE_VS_BAROQUE: the verdict stands on its evidence and nothing contradicts it.

Checks the committed same-tile measurement (a control that matches, a border that bleeds, the MixedBiome crash and its
fix), that the mod is off the full list and forbidden on the sprint tiers, that the inert patch is the shipped answer,
and that no live doc or tool still says it is on the list or to keep it.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
MOD = "m00nl1ght.geologicallandforms.biometransitions"
DOC = "design/RimMandrake/biome_transitions_judgment_2026-11-01.md"
PATCH = "src/RimMandrake/TerminalBiomes/Patches/RM_MixedBiome_Inert.xml"
fails = []


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


doc = read(DOC)
check(re.search(r"\*\*Verdict: GO\.\*\*", doc) is not None, "the judgment states a verdict")

ev = json.loads(read(DOC.replace(".md", ".evidence.json")))
r = ev["results"]
check(ev["modDelta_on_vs_off"] == [MOD], "the arms differ by this one mod")
c = r["control_rot"]
check(abs(c["on"]["plants"] - c["off"]["plants"]) / c["off"]["plants"] < 0.02, "control sites agree within 2%")
b = r["border_cauldron_rot"]
check(b["on"]["plantsOnlyInBiomeB"] / b["on"]["plants"] > 0.3 and b["off"]["plantsOnlyInBiomeB"] == 0,
      "the mod bleeds a neighbour's flora in; without it none")
m = r["mixed_rot_blue"]
check(m["off"]["plants"] < 10 and m["fix"]["plants"] > 10000, "MixedBiome kills the map; the patch restores it")
check(ev["logOffArm"]["Error in GenStep"] > 0 and ev["logFixArm"]["Error in GenStep"] == 0, "the crash is gone in the log")

active = [e.text.lower() for e in
          ET.parse(os.path.join(ROOT, "infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml")).find("activeMods")]
check(len(active) > 100, "FULL.LATEST parsed (sanity: a real list)")
check(MOD not in active, "off ModsConfig.FULL.LATEST.xml")
check(read("src/RimMandrake/Utils/modset_builder.py").count('"%s"' % MOD) >= 2, "forbidden on the sprint tiers")

ops = ET.fromstring(read(PATCH)).findall("Operation")
check(len(ops) == 1 and ops[0].get("Class") == "PatchOperationRemove"
      and ops[0].findtext("xpath") == 'Defs/TileMutatorDef[defName="MixedBiome"]/workerClass', "inert patch is exact")
for rel in ("src/RimMandrake/EnvironmentalHazards/Defs/RetiredMutatorPorts/RM_RetiredMutatorPorts_Shared.xml",
            "src/RimStarWars/SWBestiary/Defs/DonorPackPort/RSW_DonorPack_Sarlacc.xml"):
    check("<MixedBiome>" not in read(rel), "no roll left in " + os.path.basename(rel))

for rel, stale in (("src/RimMandrake/Utils/worldmap_prefill.py", "GL_BiomeTransitions"),
                   ("design/Jawa/mods/required_mods.md", "Biome Transitions"),
                   ("design/Jawa/concept.md", "Biome Transitions"),
                   ("design/Jawa/worldbuilding/setup_checklist.md", "Biome Transitions"),
                   ("design/validation_walks/RimMandrake/Pyrelands.md", "still in ModsConfig.FULL.LATEST"),
                   ("design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md", "accepts that biometransitions"),
                   ("design/RimMandrake/biome_map_makers_design_2026-10-10.md", "GL and BiomeTransitions are active"),
                   ("design/RimMandrake/mod_audit/OWNER_RULINGS.md", "BIOME_TRANSITIONS_WITH_BAROQUE_JUDGE")):
    check(stale not in read(rel), "no stale claim in " + os.path.basename(rel))

print("%d failure(s)" % len(fails))
sys.exit(1 if fails else 0)
