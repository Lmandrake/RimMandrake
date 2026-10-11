# RUST_CATHEDRAL_MECHANICS_1 — next offline slice (2026-10-11)

## the slice
Stage-keyed droid commentary: the hook CATHEDRAL_STAGE_COMMENTARY_POOLS_1 waits on.

## what "RUT_HumCommentary" actually is on origin
It never existed and is not needed. The kit's droid commentary shipped as inline
`<commentary>` entries on `RM_RustCathedralAttitude` (an `RM_BiomeAttitudeDef`),
keyed by band only, at
`src/RimMandrake/RustCathedral/Defs/RM_BiomeAttitudeDefs/RM_RustCathedralAttitude.xml`.
The map component already stores a conduct-stage (`SetStage`/`GetStage`,
CATHEDRAL_STAGE_HUM_BRIDGE_1). The missing piece was choosing lines by band x stage.
The kit spec, the arc spec, CATHEDRAL_STAGE_COMMENTARY_POOLS_1 and
CATHEDRAL_EXPOSURE_COMPLETION_1 named a RulePack that does not exist. They now name the real hook.

## build
- `RM_BandCommentaryEntry.stage` (default -1 = any stage), so the shipped band-only XML behaves as before.
- `RM_AttitudeKernel.CommentaryEntryIndex` (Verse-free): an exact band x stage entry wins, then the
  band's any-stage entry, otherwise silence. A stage-keyed entry never speaks for another stage.
- `RM_AttitudeKernel.CommentaryKeyErrors`, called by the new `RM_BiomeAttitudeDef.ConfigErrors`,
  rejects a band out of range, a stage below -1, and a duplicate (band, stage) key.
- `RM_MapComponent_BiomeAttitude.FindCommentaryFor(def, band, stage)` (now public static) uses the kernel.
- Mod Settings: `stageKeyedCommentaryEnabled` (default on). Off means only any-stage pools speak.
  It sits in the "The hum and the Cathedral's standing" group.
- Hum DLL rebuilt with winbuild, with its `.srchash`.

## proof
`python3 src/RimMandrake/Utils/selftest_rustcathedral_attitude_fuzz.py` has a new `commentary` family:
- 55 fixed cases: the legacy shape, exact-after-fallback ordering, setting off, no-fallback silence,
  and the key-error counts.
- 20,000 random lists checked against an independent reference.
- Result: 0 failures, whole fuzz OK.
- A mutant that ignored the setting was caught with 11 failures, so the test is tested, not trusted.

## not done (rest of the item)
Owed rungs are unchanged: A2 L2 whole-kit quicktest, A3 GREEN-MIN north-star bars, A4/A5 the bolt-dance look.
All of them need the bridge. The commentary-on-transition firing still needs a quicktest
(CATHEDRAL_STAGE_COMMENTARY_POOLS_1's own verify). The pools themselves (4 stages x bands) and the
bans-2/6 linter belong to that item, which is now unblocked offline.
