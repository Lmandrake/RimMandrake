#!/usr/bin/env python3
"""Source/XML pins for the Contagion fixes from the GPT edge-case consult
(design/RimMandrake/gpt_consults/Contagion_edge_cases_2026-10-16.md). Each check names its rimflow item; each
fails on the pre-fix source (control run by reverting the file to its pre-fix commit, 2026-10-16). The dive-window
fix (CONTAGION_DIVE_FIX_FOUR_WALLED_CELLS) is also a behaviour row in Source/SelfTest/ContagionFuzz.cs (DiveOffset),
run by src/RimMandrake/Utils/selftest_contagion_fuzz.py.

    python3 src/RimMandrake/Contagion/selftest_contagion_gpt_fixes.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def read(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as f:
        return f.read()


def method_body(src, signature):
    i = src.find(signature)
    if i < 0:
        return ""
    j = src.find("{", i)
    depth, k = 0, j
    while k < len(src):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j:k + 1]
        k += 1
    return ""


def defs_by_name(rel, tag):
    root = ET.parse(os.path.join(HERE, rel)).getroot()
    return {d.findtext("defName"): d for d in root.findall(tag)}


def main():
    inj = method_body(read(os.path.join("Source", "JobDriver_RM_InjectGenomeSample.cs")),
                      "protected override IEnumerable<Toil> MakeNewToils()")
    check("sanity: injection MakeNewToils found", "TryBeginGestation" in inj and "InjectGenomeSample" in inj)
    # CONTAGION_INJECT_FIX_CANCEL_STILL_STABS: gestation starts only from an Instant toil after the delay
    check("CONTAGION_INJECT_FIX_CANCEL_STILL_STABS: no finish action on the inject toil", "AddFinishAction" not in inj)
    fin = inj.find("ToilCompleteMode.Instant")
    check("CONTAGION_INJECT_FIX_CANCEL_STILL_STABS: gestation runs in an Instant toil's initAction after the delay",
          inj.find("ToilCompleteMode.Delay") < fin < inj.find("finish.initAction") < inj.find("TryBeginGestation"))
    # CONTAGION_INJECT_FIX_HOST_WANDERS_OFF: the delay toil fails when the host drifts out of reach
    check("CONTAGION_INJECT_FIX_HOST_WANDERS_OFF: inject toil has a reach FailOn",
          re.search(r"inject\.FailOn\(\(\) => !pawn\.Position\.InHorDistOf\(Host\.Position, InjectReach\)\);", inj) is not None)
    # CONTAGION_INJECT_FIX_IGNORES_OFF_SWITCH
    check("CONTAGION_INJECT_FIX_IGNORES_OFF_SWITCH: job fails when genome organ growing is switched off",
          "this.FailOn(() => !RM_ContagionSettings.genomeOrganGrowingEnabled);" in inj)

    burn = method_body(read(os.path.join("Source", "RM_GameCondition_ContagionBurn.cs")), "private static void TryDive(")
    check("sanity: TryDive found", "PickDive" in burn)
    # CONTAGION_DIVE_FIX_FOUR_WALLED_CELLS
    check("CONTAGION_DIVE_FIX_FOUR_WALLED_CELLS: TryDive collects DiveCandidates and rotates by DiveOffset",
          "RM_SkyKernel.DiveCandidates" in burn and "RM_SkyKernel.DiveOffset(" in burn and "sheltered.Count > 4" not in burn)

    sky = read(os.path.join("Source", "RM_MapComponent_ContagionSky.cs"))
    expose = method_body(sky, "public override void ExposeData()")
    check("sanity: sky ExposeData found", "tellsBegun" in expose)
    # CONTAGION_SINKERS_FIX_RESET_AFTER_LOAD
    check("CONTAGION_SINKERS_FIX_RESET_AFTER_LOAD: PostLoadInit seeds wasTellsBegun from tellsBegun",
          re.search(r"if \(Scribe\.mode == LoadSaveMode\.PostLoadInit\) wasTellsBegun = tellsBegun;", expose) is not None)

    # CONTAGION_WOMBPOD_FIX_SAC_NEVER_HATCHES: CompHatcher only overrides CompTick, so the def must tick Normal
    sac = defs_by_name(os.path.join("Defs", "ThingDefs", "RM_WombpodSac.xml"), "ThingDef").get("RM_WombpodSac")
    check("sanity: RM_WombpodSac has a CompHatcher",
          sac is not None and any(li.get("Class") == "CompProperties_Hatcher" for li in sac.findall("comps/li")))
    check("CONTAGION_WOMBPOD_FIX_SAC_NEVER_HATCHES: sac tickerType is Normal",
          sac is not None and (sac.findtext("tickerType") or "").strip() == "Normal")

    hd = defs_by_name(os.path.join("Defs", "HediffDefs", "RM_UnfinishedHediffs.xml"), "HediffDef")
    # CONTAGION_CLAWS_FIX_ABSTRACT_VERB
    limbs = ("RM_UnfinishedClaw", "RM_UnfinishedSpike", "RM_UnfinishedFang")
    check("sanity: the three attack limbs exist", all(n in hd for n in limbs))
    classes = [v.text.strip() for n in hd.values() for v in n.iter("verbClass")]
    check("CONTAGION_CLAWS_FIX_ABSTRACT_VERB: no hediff verb names the abstract Verb_MeleeAttack",
          len(classes) >= 3 and "Verb_MeleeAttack" not in classes, classes)
    # CONTAGION_UNRAVEL_FIX_CURED_BY_SERUM
    un = hd.get("RM_UnfinishedUnraveling")
    check("CONTAGION_UNRAVEL_FIX_CURED_BY_SERUM: unraveling is never curable by item",
          un is not None and (un.findtext("everCurableByItem") or "").strip().lower() == "false")
    # CONTAGION_MONSTROUS_FIX_HP_BONUS_NOTHING: MaxHitPoints does not reach pawn part health
    mon = hd.get("RM_UnfinishedMonstrous")
    check("sanity: monstrous keeps its other offsets", mon is not None and mon.find(".//MeleeDamageFactor") is not None)
    check("CONTAGION_MONSTROUS_FIX_HP_BONUS_NOTHING: no dead MaxHitPoints offset",
          mon is not None and mon.find(".//statOffsets/MaxHitPoints") is None)
    if fails:
        print("FAIL: %d failed" % len(fails))
        return 1
    print("PASS: 0 failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
