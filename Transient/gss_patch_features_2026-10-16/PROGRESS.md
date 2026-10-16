# GSS patch features — GSS_PATCHES_FIX_TWENTY_THREE_UNLABELLED

## Mechanism
- `[PatchFeature(label, typeof(Settings), "field")]` (src/RimMandrake/_Shared/HarmonyResilience/PatchApplier.cs) does NOT gate a
  patch at runtime. It names the feature, and when that class fails to patch it forces the bool field OFF for the session.
- Label-only `[PatchFeature("label")]` is what the lint accepts as always-on (precedent: FlowWorks PipeLook): a failure is
  reported by feature name and switches nothing off.
- GSS called `PatchApplier.Apply` but never `BeforeExpose`/`AfterExpose`, so a forced-off field would have been SAVED off.
  Wired both into GimmeSomeSlackSettings.ExposeData and AerialSettings.ExposeData (no effect unless a patch fails).
- Defaults unchanged: attributes + expose wiring only; no patch body was edited, no gate added.

## Mapping (23)
| feature (label) | field | classes |
|---|---|---|
| Messy cords: conduit run looks | GimmeSomeSlackSettings.enabled | DesignatorBuild_ProcessInput_Conduit, DesignatorBuild_StyleGetter_Conduit, DesignatorBuild_JoinsHint, PowerSwitch_Graphic, Building_SpawnSetup_Runs, Building_GetGizmos_Restyle, TryLink_Bridge (7) |
| Messy cords: hide vanilla hookup wires | GimmeSomeSlackSettings.hideHookupWires | PrintWirePieceConnecting (1) |
| Overhead lines: power through spans | AerialSettings.enabled | PowerNetManager_UpdateFirst_Scope, PowerNetMaker_NewNet_Scope, GenAdj_CellsAdjacentCardinal_AerialLinks (3) |
| Overhead lines: anchor looks | AerialSettings.enabled | DesignatorBuild_ProcessInput, DesignatorBuild_StyleGetter, BuildCopyCommand_CarryStyle, Thing_StyleDef, Frame_KeepStyle (5) |
| Overhead lines: explosions cut wires | AerialSettings.explosionsCut | GenExplosion_CutSpans (1) |
| Power taps | AerialSettings.tapsEnabled | PowerNet_GainRate_TapDebit, TryConnect_TapOwnFaction, ConnectToTransmitter_TapGuard (3) |

Notes
- Power-through-spans: the aerial master deliberately never gates power carry (placed links keep powering a save), so the
  field here means only "on failure, stop offering anchors" — wires that cannot carry power should not be buildable.
- Not gated by their field today (toggle off does not stop them; unchanged on purpose to keep 1.0.0 behaviour):
  Building_SpawnSetup_Runs, TryLink_Bridge, the five anchor-look patches, the three power-scope patches, TapDebit
  (inert when no tap drains). GenExplosion_CutSpans also carries kineticSway (one field per class).

## Always-on
| class | label | why |
|---|---|---|
| Patch_Thing_Graphic_LampMasterOff | Messy cords: vanilla lamp art when switched off | it IS the master-off path; forcing the master off on its failure makes it worse |
| Patch_Map_ExposeComponents_SkipAerial | Overhead lines: save stays loadable without the mod | save bookkeeping, must run whatever the settings |
| Patch_GenTypes_LegacyTypeName | Messy cords: load saves from before the rename | save compatibility for RimMandrake.MessyConduit.* names |

## New settings proposed (NOT built)
- **Conduit run looks** (style menu, restyle gizmo, joins hint, styled switch art): today governed only by the cords master
  switch. A separate toggle would let a player keep messy cords but vanilla-look conduits. Proposal only — adding it
  changes the 1.0.0 settings page and needs gating code.

## Build / lint / selftests
- `winbuild.py GimmeSomeSlack`: Build succeeded, 0 warnings, 0 errors; DLL + .srchash rewritten together. NOT deployed.
- `lint_harmony_targets.py --mod GimmeSomeSlack`: targets 27 | ok 27 | feature-findings 0 (was 23).
- `run_selftests.py --only` (selftest_gimmesomeslack, selftest_lint_harmony_targets, GSS human_review, northstar
  playtest_runner, proof_all): PASS 5/5, GREEN.
- Edited .cs files are DIRTY for code review (code_review_status.py) until reviewed.

## Ledger
- `rimflow implemented` with O1 L0 (offline: lint 0 + build + selftests) and A1 L1 owed: settings all-off / all-on at the
  next GSS live round (Harmony census line "patched 23, missing 0", no red line, each master off reverts its art).
