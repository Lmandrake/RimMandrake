#!/usr/bin/env python3
"""Planted-defect selftest for lint_xmlonly_defs.py across the six XML-only mods: clean on each real mod, then one planted defect at a
time is caught.

    python3 src/RimMandrake/Utils/selftest_xmlonly_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_modpack_lint as H  # noqa: E402

SCRIPT = "lint_xmlonly_defs.py"
TR = "Defs/ThingDefs/RM_Traces_Spike.xml"
AB = "About/About.xml"
SUITES = {
    "Traces": [
        ("a Defs file does not parse", TR, "</Defs>", "</Def>", "xo-parse"),
        ("duplicate defName in one file", TR, "<defName>RM_Trace_SpikeFloor</defName>", "<defName>RM_Trace_SpikeWall</defName>", "xo-unique"),
        ("validation.py names a spike the mod does not define", "validation.py", 'WALL_SPIKE = "RM_Trace_SpikeWall"', 'WALL_SPIKE = "RM_Trace_SpikeWal"', "tr-spike"),
        ("placementMask word typo", TR, "<placementMask>Natural, Unnatural</placementMask>", "<placementMask>Natural, Unnatral</placementMask>", "tr-filth"),
        ("empty placementMask", TR, "<placementMask>Unnatural</placementMask>", "<placementMask></placementMask>", "tr-filth"),
        ("trace is not a Filth", TR, "<thingClass>Filth</thingClass>", "<thingClass>Thing</thingClass>", "tr-filth"),
        ("cleaning work zero", TR, "<cleaningWorkToReduceThickness>70</cleaningWorkToReduceThickness>", "<cleaningWorkToReduceThickness>0</cleaningWorkToReduceThickness>", "tr-filth"),
        ("rainWashes not a bool", TR, "<rainWashes>true</rainWashes>", "<rainWashes>yes</rainWashes>", "tr-filth"),
        ("colour byte out of range", TR, "(27, 22, 18, 200)", "(27, 22, 18, 300)", "tr-filth"),
        ("packageId not in the scheme", AB, "<packageId>mandrake.rm.traces</packageId>", "<packageId>Mandrake Traces</packageId>", "xo-about"),
        ("1.6 dropped from supportedVersions", AB, "<li>1.6</li>", "<li>1.5</li>", "xo-about"),
    ],
    "HostileFlora": [
        ("manhunter chance non-zero", "Defs/ThingDefs_Races/RM_Gallowroot.xml", "<manhunterOnDamageChance>0</manhunterOnDamageChance>", "<manhunterOnDamageChance>0.5</manhunterOnDamageChance>", "hf-race"),
        ("pawn kind names another race", "Defs/ThingDefs_Races/RM_Gallowroot.xml", "<race>RM_Gallowroot</race>", "<race>RM_Gallowrot</race>", "hf-race"),
        ("a Defs file does not parse", "Defs/ThingDefs_Races/RM_Gallowroot.xml", "</Defs>", "</Def>", "xo-parse"),
        ("1.6 dropped from supportedVersions", AB, "<li>1.6</li>", "<li>1.5</li>", "xo-about"),
    ],
    "AssailantSalvage": [
        ("def loses its RUT_ prefix", "Defs/ThingDefs/RUT_AncientAirlocks.xml", "<defName>RUT_AncientAirlock</defName>", "<defName>AncientAirlock</defName>", "as-def"),
        ("texture typo beside real art", "Defs/ThingDefs/RUT_AncientAirlocks.xml", "<texPath>Things/Building/Ancient/RUT_JammedAncientAirlock</texPath>", "<texPath>Things/Building/Ancient/RUT_JammedAncientAirlok</texPath>", "xo-tex"),
        ("no label", "Defs/ThingDefs/RUT_AncientAirlocks.xml", "<label>ancient airlock</label>", "", "as-def"),
        ("hit points zero", "Defs/ThingDefs/RUT_AncientAirlocks.xml", "<MaxHitPoints>200</MaxHitPoints>", "<MaxHitPoints>0</MaxHitPoints>", "as-def"),
        ("two defs share a name", "Defs/ThingDefs/RUT_AncientAirlocks.xml", "<defName>RUT_AncientAirlock_Large</defName>", "<defName>RUT_AncientAirlock</defName>", "xo-unique"),
    ],
    "Pyrinth": [
        ("unbalanced xpath", "Patches/Absorbed_EpochsPyrinth/Absorbed_EpochsPyrinth_Royalty_Patch.xml", '<xpath>Defs/RoyalTitleDef[defName="Acolyte"', '<xpath>Defs/RoyalTitleDef[defName="Acolyte', "py-xpath"),
        ("operation MayRequire is inert", "Patches/Absorbed_EpochsPyrinth/Absorbed_EpochsPyrinth_Royalty_Patch.xml", "<Operation Class=\"PatchOperationAdd\">", "<Operation Class=\"PatchOperationAdd\" MayRequire=\"Ludeon.RimWorld.Royalty\">", "inert"),
        ("operation without a class", "Patches/Absorbed_EpochsPyrinth/Absorbed_EpochsPyrinth_Royalty_Patch.xml", "<Operation Class=\"PatchOperationAdd\">", "<Operation>", "without Class"),
        ("donor incompatibility dropped", "About/About.xml", "<li>det.epochspyrinth</li>", "<li>det.epochspyrinth.x</li>", "incompatibleWith"),
        ("a Defs file does not parse", "Defs/Absorbed_EpochsPyrinth/Effects/Absorbed_EpochsPyrinth_Effecter_Pyrinth.xml", "</Defs>", "</Def>", "xo-parse"),
    ],
    "StrandedQuest": [
        ("quest names a missing history event", "Defs/QuestScriptDefs/Quest_Stranded.xml", "<goodwillChangeReason>RM_StrandedTravellerTaken</goodwillChangeReason>", "<goodwillChangeReason>RM_StrandedTravelerTaken</goodwillChangeReason>", "sq-quest"),
        ("history event renamed", "Defs/HistoryEventDefs/HistoryEvents_Stranded.xml", "<defName>RM_StrandedTravellerTaken</defName>", "<defName>RM_StrandedTravelerTaken</defName>", "sq-quest"),
        ("a Defs file does not parse", "Defs/HistoryEventDefs/HistoryEvents_Stranded.xml", "</Defs>", "</Def>", "xo-parse"),
        ("quest node class typo (validator)", "Defs/QuestScriptDefs/Quest_Stranded.xml", '<root Class="QuestNode_Sequence">', '<root Class="QuestNode_Sequenc">', "sq-quest"),
    ],
    "MandrakePatches": [
        ("top-level patch unguarded", "Patches/BuzzerApostrophe_Fix.xml", "<Operation Class=\"PatchOperationFindMod\">", "<Operation Class=\"PatchOperationReplace\">", "unguarded"),
        ("FindMod with no mods", "Patches/BuzzerApostrophe_Fix.xml", "<li>Det's Xenotypes - Buzzers</li>", "", "no <mods>"),
        ("success word typo", "Patches/BuzzerApostrophe_Fix.xml", "<mods>", "<success>Alwayz</success><mods>", "success"),
        ("top-level Operation MayRequire is inert", "Patches/BuzzerApostrophe_Fix.xml", "<Operation Class=\"PatchOperationFindMod\">", "<Operation Class=\"PatchOperationFindMod\" MayRequire=\"x.y\">", "inert"),
    ],
}

if __name__ == "__main__":
    rc = 0
    for mod, plants in SUITES.items():
        keep = ("About", "Languages", "Textures") if mod in ("AssailantSalvage", "Pyrinth") else ("About", "Languages")
        rc |= H.run(mod, SCRIPT, plants, keep=keep)
    sys.exit(rc)
