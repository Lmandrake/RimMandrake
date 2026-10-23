# NINEFOLD_MERGE_NINE_GODS_ONE_ROOF

Owner, 2026-10-22, by question card: "Ninefold home → fold Ninefold into Salvation Rites". His words: *"the Nine
Gods belong in Salvation Rites. They are NOT a general reuse mod."* Options and facts:
`design/RimMandrake/gpt_review_findings_2026-10-22.md` § Ninefold home (option a).

## What was built (offline, 79de4ebe3 + 2da7880bd)

- The 32 C# files, settings screen (Mod Settings: "Salvation Rites") and fuzz selftest moved from
  `src/RimMandrake/Ninefold` to `src/RimUtinni/Rites/Source`; namespace `RimMandrake.Utinni.Rites`, DLL
  `RimMandrake.Utinni.Rites.dll`, Harmony id `mandrake.rut.rites`. Rites' About gains the Harmony dependency.
- The 20 tilts are `RUT_Tilt_*` in `Defs/RUT_GodFavourTilts.xml` (no canonical save names an `RM_Tilt_` def).
- Save type alias: `NinefoldLegacyTypeConverter` (a vanilla `BackCompatibilityConverter`, put at the front of the
  private `BackCompatibility.conversionChain` from the Mod constructor) maps any saved `RimMandrake.Ninefold.X`
  class to `RimMandrake.Utinni.Rites.X`. All 18 canonical Ash'karr start saves hold
  `RimMandrake.Ninefold.GameComponent_Ninefold`, 6 hold `RimMandrake.Ninefold.MapComponent_NinefoldOfferings`.
- `RUT_NineFaults.xml` lost its `MayRequire="mandrake.rm.ninefold"` guards; reflection strings fixed in
  Aftermath, LuminousPigment, EnvironmentalHazards, LanternDeeps and Atlas (DLLs rebuilt); `loadAfter` dropped
  from Aftermath and LuminousPigment (reflection at startup needs no order; a free-tier mod would otherwise load
  after a campaign mod), retargeted in AftermathRites; Atlas subjects now `mandrake.rut.rites`.
- `mandrake.rm.ninefold` removed from the DEV/TEST/AUTHORING/SHIP/FULL.LATEST lists, retired in the mod archive,
  its modcheck key forgotten, its suite merged into `src/RimUtinni/Rites/validation.py`, its walk into
  `design/validation_walks/RimUtinni/Rites.md` (section "The Nine").

## criteria

- A1 L0: `python3 src/RimMandrake/Utils/selftest_ninefold_fuzz.py --saves` passes: the fuzz, plus every
  `RimMandrake.Ninefold.*` class in the canonical saves maps to a class Rites declares, with every saved field
  still a Scribe label (fixture copied verbatim from a canonical save).
- A2 L0: the Rites DLL and the five consumer DLLs build clean; settings-screen, suite-corrections, Atlas,
  AftermathRites and SacredGraffiti selftests pass; validate_patch reports 0 errors on Rites' defs.
- A3 L2: on the minimal `rites` tier (`modset_builder.py --tier rites`), Player.log shows `[Ninefold] ready: N`
  with N > 0, no "Config error in mandrake.rut.rites", and the Rites suite's Ninefold chains run.
- A4 L2: loading a canonical Ash'karr start save made before the fold logs no "Could not find class
  RimMandrake.Ninefold" and `GetSatiation` returns its saved values (AREAFIX save: Rekko 90, TaBaa 67, Zizzik 87,
  Shkaar 100), not a fresh zero vector.

## Watch out

- Deploy is owed (dry-run only so far): the game copy `Mods\Ninefold` must be REMOVED and the live ModsConfig
  must drop `mandrake.rm.ninefold` before the sitting. If the old folder stays active its own classes answer
  first and every hook runs twice.
- Settings saved under the old mod (`Mod_Ninefold_RM_NinefoldSettings.xml`) are not carried over: defaults.
- The alias runs only when the save's mod list differs from the running game's
  (`BackCompatibility.CheckSaveIdenticalToCurrentEnvironment`); a save naming the old class always differs.
- Graffiti's `ModExtension_Graffiti.cs` comment still names `RimMandrake.Ninefold.God`; left alone while another
  helper had Graffiti mid-edit (a comment, but it moves Graffiti's srchash).
