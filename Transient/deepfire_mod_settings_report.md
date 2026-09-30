# DEEPFIRE_MOD_SETTINGS_1 — report

Status: BUILT, dotnet build clean, XML parses clean, NOT deployed, NOT live-tested.
run_selftests.py running in foreground (exceeded the 120s tool timeout, moved to
background by the harness — not backgrounded by choice; awaiting completion).

## csproj check
Every `.cs` under `Source/` already had a `<Compile Include>` line — no missing
entries, nothing added (verified by diffing the csproj's Include list against
`ls Source/*.cs`).

## What this item added (spec §7 "Painting" group, plus Status/Gods gaps)
All new settings are read LIVE at point of use (the file's established pattern),
so no per-field ApplySettings() push was needed except two cases baked into defs:

- `moodScale`: pushed into `RM_WearingDeepfireTitled/Common`, `RM_SawCommonerInDeepfire`,
  `RM_DeepfireBedroom` stage `baseMoodEffect` by a new `ApplyStatusMoodScale()`
  (same shape as the existing `opinionAboveStation` -> `RM_WearsAboveStation` push).
- `clusterBlock`: block indices are keyed off the block SIZE, so a live change
  stales every map's existing cluster bookkeeping. Added
  `MapComponent_DeepfireLights.RebuildAllClustering()` (clear + re-derive from
  the floor grid + every coated 1x1 building) and call it from ApplySettings()
  for every `Find.Maps` entry.

New settings (33 fields): paintingEnabled, maxCoats, coatRadius[4], coatIntensity[4],
glowMinValue, costWallCell, costFloorCell, costFurnitureBase, costFurniturePerExtraCell,
costFurnitureCap, costArt, costApparel, costWeapon, clusterBlock, floorsPaintable,
wallsPaintable, furniturePaintable, apparelPaintable, weaponsPaintable, wornLightEnabled,
stylingStationLacquer, wornLightTickInterval, glowTargetFactor, glowDodgePenalty,
combatPenaltiesEnabled, artQualityBump, beautyFlat, beautyPct, beautySizeCap,
floorBeautyPerCell, floorRoomBonusPer10, floorRoomBonusCap, moodScale,
goodwillPerImpressedVisit, ishkoIdolPaintable (35 counting the two coat arrays as
one field each; 37 counting each array's 4/4 elements separately).

Gates added: `paintingEnabled` (Designator_Deepfire.CanDesignateCell/Thing +
both WorkGivers' ShouldSkip), the 5 paintable-class toggles (new
`DeepfireTargetClassUtility.IsPaintable`, checked in the designator and both
WorkGivers), `wornLightEnabled` (MapComponent_DeepfireLights.Worn.RefreshWornPawn),
`stylingStationLacquer` (StylingStationLacquer.DrawCheckboxes), `combatPenaltiesEnabled`
(both combat hooks), `artQualityBump` (DeepfireFirstCoatBonus.Apply),
`ishkoIdolPaintable` (Designator_Deepfire.CanDesignateThing, via
DeepfireGodDeltas.StatueGodOf).

Out of scope (confirmed, not this item's job per its own Build section): Cuisine's
per-family weight sliders and effectScale — not named by any of the 5 follow-on
items this one wires.

## Correctness fix (not part of the item's own rows, fixed on sight)
`About.xml`'s description was badly stale: it still said painting/worn-glow/status/
gods were "STILL NOT IN THIS BUILD" and filed under a superseded item name — all
six landed in the six commits before this one. Rewrote it to describe what the mod
actually ships now (without claiming anything is live-verified, since none of it
is yet).

## Verification so far
- dotnet build (Release, Windows SDK): 0 warnings, 0 errors.
- 23 XML files under the mod parse clean (including the edited About.xml and
  RM_SumptuaryThoughts.xml comment fix).
- DLL + .srchash both rebuilt in this same build (git status shows both modified).

## Selftests
`run_selftests.py`: 78/79 passed, 0 failed, 1 unmeasured (`selftest_tool_metadata.py`,
needs a Windows-side JawaBench build, pre-existing/expected per every prior
DEEPFIRE_* report). `selftest_deployed_biome_refs.py`, which FAILED in all five
prior follow-on reports, PASSED here (fixed elsewhere, not by this item).

## Land
- [x] commit `75f5887f7` (pre-rebase)
- [x] rebase onto origin/main (clean, no conflicts; the one new commit
      `ad2e123a4` touched only Transient proof outputs + a new bridgetools
      script, nothing under LuminousPigment/Source, so no rebuild was needed)
- [x] push origin HEAD:main
- [x] ancestry confirmed: `git merge-base --is-ancestor 75f5887f7 origin/main` -> 0

## Result
Landed at `75f5887f758715e3ffb2b59d51efe13cd4219321` on origin/main.
