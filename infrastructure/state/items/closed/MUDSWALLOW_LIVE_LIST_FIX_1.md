# MUDSWALLOW_LIVE_LIST_FIX_1 — MudSwallow mutates the live haulables list mid-loop

Found by a BENCH full-file review 2026-09-12; confirmed by BENCH reading the code.

## The bug
`src/RimMandrake/Greentide/Source/RM_MapComponent_MudSwallow.cs` `Scan()`
(lines ~53-81): `map.listerThings.ThingsInGroup(ThingRequestGroup.HaulableEver)`
returns the LIVE internal list (engine source confirmed, not a copy). The
index-based loop calls `Bury(thing)` → `thing.Destroy()` →
`ListerThings.Remove` synchronously mutates that list mid-iteration: the
element shifted into slot i is skipped this pass, lands outside `stillPresent`,
and its `firstSeenTick` entry is wrongly purged as "moved off hazardous
ground" — full dwell-timer reset. No exception, no log.

## Fix shape
Snapshot before iterating (e.g. iterate a copy, or collect burial candidates
and Bury after the loop). Rebuild + redeploy the DLL (game must be down for
the deploy window).

## Also, same review (fold into the same change)
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml:144-156` —
`wildPlants` has 11 unguarded foreign defNames (sarg.alphabiomes /
biomesteam.biomescaverns / mlie.starwarsanimalcollection); every `wildAnimals`
entry above it is MayRequire-guarded. All resolve today; add the guards.

## verify
Selftest or scripted check: two adjacent swallow-ready haulables on mire
terrain both bury in one Scan pass and no timer resets; wildPlants entries all
carry MayRequire. Neither file gets mark-clean until a re-review after the fix
finds nothing.

## criteria
- `RM_MapComponent_MudSwallow.Scan()` no longer iterates the live
  `ThingsInGroup` list while destroying elements from it: the list is
  snapshotted (`new List<Thing>(...)`) before the loop, burial candidates are
  collected into `toBury` during the scan pass, and `Bury()` is called on each
  only after the scan loop completes. Two adjacent swallow-ready haulables
  both bury correctly in one `Scan()` pass with no dwell-timer reset on the
  shifted one.
- `RUT_Greentide.xml`'s `wildPlants` block: all 11 entries carry the correct
  `MayRequire` guard, matching each defName's actual owning mod (verified via
  the mod's own Defs/About.xml on disk, not guessed):
  - `AB_JungleTree`, `AB_SugarFamewort` -> `sarg.alphabiomes` (Alpha Biomes)
  - `BMT_GiantLeaf` -> `biomesteam.biomescaverns` (Biomes! Caverns)
  - `Plant_HydenockTree_Wild`, `Plant_JoganTree_Wild`, `Plant_MujaFruit_Wild`,
    `Plant_HubbaGourd_Wild`, `Plant_FelucianGlowspore_Wild`,
    `Plant_Bubblespore_Wild`, `Plant_Chakroot_Wild`, `Plant_TookeTrap_Wild`
    -> `mlie.starwarsanimalcollection` (Star Wars Animal Collection
    (Continued))
- `RM_Greentide.csproj` builds clean (0 errors/warnings) with the fix.
- `RUT_Greentide.xml` passes `validate_patch.py --live` with 0 errors.
- Both touched files pass a genuine full-file code review with no findings
  and are marked clean in `CODE_REVIEW_STATUS.json`.
