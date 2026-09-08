# ResearchRetag — validation walk
subject: src/RimUtinni/ResearchRetag  (packageId `mandrake.rut.researchretag`)
deps: no modDependencies/loadAfter declared; About.xml instead carries a 52-entry `forceLoadAfter` list of every third-party packageId that owns a patched ResearchProjectDef (e.g. als.gravtech, oskarpotocki.vfe.tribals, vanillaexpanded.vfespacer — full list in About.xml), so this mod always loads after them without hard-requiring any one.
list: minimal (own ResearchTabDefs + log-clean) | full (verifying actual patch results needs the real third-party ResearchProjectDefs the manifest targets)
status-hint: GENERATED research normalization — rewrites techLevel/baseCost/prerequisites on 269 surviving cross-mod ResearchProjectDefs per the frozen manifest, plus 16 campaign ResearchTabDefs and a 403-op per-row tab assignment. Patches are emitted by `design/Jawa/research_review/build_retag_patches.py` — never hand-edited (except the two named hand-authored supplement files).

## must be true
- 15 campaign ResearchTabDefs exist in RUT_Tree_Defs.xml (RUT_Tree_Scavenging, Refinery, Workshop, Hearth, PowderAndSlug, Utinni, Shell, Unbolting, Blasterworks, WakingMind, Reach, AscendantLadder, StrangeSchools, JunkerYards, FoundryHive) — plus the pre-existing RUT_Rites tab = 16 total for the campaign; RUT_Antiquities ships its own tab separately and is untouched here.
- Every PatchOperationConditional in RUT_ResearchRetag.xml is conditional on the target ResearchProjectDef existing first (`Defs/ResearchProjectDef[defName="..."]`) — a missing target mod means that block matches nothing and logs nothing; never treat log silence as proof a retag applied.
- A representative retagged def, e.g. `ABF_ResearchProject_Synstruct_CoreAssistants`, resolves techLevel=Industrial with its original `prerequisites` node removed (per the manifest's tier grammar).
- RUT_ResearchTabAssign.xml reassigns `tab` on the same surviving rows to a RUT_Tree_* def — e.g. `ABF_ResearchProject_Synstruct_InterchangeableParts` resolves tab=RUT_Tree_Scavenging — never RUT_Rites or RUT_Antiquities-tab rows (those are explicitly excluded).
- RUT_ResearchRetag_Supplement.xml's 13 hand-authored rows (10 DP_RGiveArea* + 3 RUT_Antiq_*) resolve the same as generator output would, e.g. `DP_RGiveArea50` and `DP_RGiveArea52` resolve techLevel=Industrial.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.researchretag" and no XML error naming RUT_ResearchRetag.xml, RUT_ResearchRetag_Supplement.xml, RUT_ResearchTabAssign.xml, or RUT_Tree_Defs.xml
2. [D] def read-back: ResearchTabDef RUT_Tree_Scavenging exists, label "jawa scavenging"; ResearchTabDef RUT_Tree_WakingMind exists (confirms The Waking Mind shipped unfolded, not merged)
3. [B] jawa/get_def {defName: "ABF_ResearchProject_Synstruct_CoreAssistants", defType: "ResearchProjectDef"} → techLevel=Industrial, no prerequisites node (only present if the third-party mod owning it is in the active list — else this check is UNMEASURED, not failed)
4. [B] jawa/get_def {defName: "ABF_ResearchProject_Synstruct_InterchangeableParts", defType: "ResearchProjectDef"} → tab=RUT_Tree_Scavenging
5. [B] jawa/get_def {defName: "DP_RGiveArea50", defType: "ResearchProjectDef"} → techLevel=Industrial (proves the hand-authored Supplement file, not just generator output, actually applies)
6. [D] def read-back: no ResearchProjectDef whose defName matches an RR_* prefix carries a RUT_* tab or retagged techLevel (Research Reinvented's own techprint-spliced projects are explicitly out of scope per About.xml)

Surprising: About.xml documents a still-open defect, RETAG_BUILDER_SELF_ERASE_1 — build_retag_patches.py, run against any capture where mandrake.rut.researchretag is already active (i.e. every capture currently on disk), would regenerate itself into erasing the Supplement's 13 rows. RUT_ResearchTabAssign.xml separately flags one row, OilPourCageResearch, as an UNCERTAIN judgment call (placed in The Refinery) awaiting owner confirmation — worth a [D] read-back once he rules on it, not asserted here as "must be true".
