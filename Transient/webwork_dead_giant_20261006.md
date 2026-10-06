# WEBWORK_DEAD_GIANT_BUILD_1 — offline build progress (2026-10-06)

## Recon
- No existing urraveth defs or code; examine-job shape copied from Scarlands `RM_JobDriver_WorkPanelLoose` +
  Antiquities `JobDriver_ExamineAntiquity`; GenStep shape from `RM_GenStep_WebworkNest`; proof shape from `RM_WebworkProof`.
- Vanilla `CompStudiable` rejected: `CompProperties_Studiable` is Anomaly knowledge plumbing (anomalyKnowledge,
  knowledgeCategory, monolith level) with no per-piece completion hook (RimSage). Custom JobDriver used, as the spec allows.
- Collapse maths: `RoofCollapserImmediate.ThinRoofCrushDamageRange` = 15~30 Crush, SourceCategory.Collapse (RimSage).
- Art: 10 finished renders in `D:\Luke\dev\_artpipe\_artsrc\RM_Urraveth_*` (wrapped + bare x 5). NOT installed.
- Thrixweave = vanilla `Hyperweave` defName (renamed by RM_Thrixweave_Rename.xml); WEBWORK_BASE_PORT_BUILD_1 is done.

## Built (uncommitted, Webwork only)
- `src/RimMandrake/Webwork/Defs/ThingDefs_Buildings/RM_Urraveth_Remains.xml` — 5 piece defs (skull, neck, rib, pelvis, limb pile).
- `src/RimMandrake/Webwork/Defs/JobDefs/RM_Urraveth_Jobs.xml` — RM_ExamineUrravethRemains.
- `src/RimMandrake/Webwork/Defs/MapGeneration/RM_UrravethRemains.xml` + `Patches/RM_UrravethRemains_MapGenPatch.xml`.
- `src/RimMandrake/Webwork/Source/RM_UrravethRemains.cs` — piece building, examine job, reading MapComponent, GenStep (7-piece 15x9 layout).
- `src/RimMandrake/Webwork/Source/RM_UrravethProof.cs` — ProofSite / ProofRead / ProofLoad static tools.
- `RM_WebworkMod.cs` (5 settings) and `RM_Webwork.csproj` (2 Compile lines).

## Checks
- winbuild.py Webwork: 0 warnings, 0 errors; new types present in the DLL (sanity probe ProofNest also present).
- validate_patch.py: 0 errors, 1 warning (unwrapped Core add, same as the sibling nest patch). XML well-formed.
- validation.py STATIC: PASS (0 findings) — new settings Scribed, on screen, read by code.

## Left / blockers
- `art install` of the 10 RM_Urraveth_* renders (texPaths are magenta until then).
- Live criteria (all five) via ProofSite/ProofRead/ProofLoad, plus a world read; record in validation.py — not edited
  here because the traction-lance agent has uncommitted edits in it.
- PROVISIONAL numbers: footprints, draw sizes, HP, load capacities, examine ticks, near radius, settings defaults.
- Stand-ins: creak sound = Building_Deconstructed, outline filth = Filth_LooseGround; no bone chunk def (rubble = filth only);
  deconstruction yields no bone resource. Ribcage is wholly Standable (per-cell impassable ribs not built).
- Webwork settings window has no scroll view and is getting long.
