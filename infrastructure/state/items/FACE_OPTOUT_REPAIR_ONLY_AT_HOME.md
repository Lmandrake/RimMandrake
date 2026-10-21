# FACE_OPTOUT_REPAIR_ONLY_AT_HOME

Found in `design/RimStarWars/face_art_reassessment_2026-10-21.md` §7: Facial Animation's opt-out for our species lived only in the owner's own `Config\Mod_1635901197_FacialAnimationMod.xml` (68 `Human-RSW_*` entries), so on a player's install FA's anime face draws over every painted head.

## How FA decides (READ, FA 1.6 DLL decompiled with ilspycmd, 2026-10-21)
- `FacialAnimation.DrawFaceGraphicsComp.CheckEnableDrawing(Pawn)` → gender switches → `FacialAnimationMod.Settings.ShouldDrawRaceXenoType(pawn)`.
- `ShouldDrawRaceXenoType` checks the keys `<race>-null` and `<race>-<xenotypeDefName>` against `IgnoreEnableAnimationForRaceXenoTypeList` (saved as `IgnoreEnableAnimationForRaceXenoTypeListAA`). For a custom xenotype it looks up the def whose translated label equals `genes.xenotypeName`.
- That list exists only in the player's ModSettings. FA reads no def, DefModExtension or patchable XML for this, so a `PatchOperationFindMod` patch has nothing to target.

## Spec (built)
- `src/RimStarWars/StarWarsRaces/Defs/Misc/RSW_FacialAnimationOptOut.xml`: the list as data (custom def `RimMandrake.StarWars.Races.RSW_FacialAnimationOptOutDef`). It holds the owner's 68 entries plus `RSW_RimMandrakeSithKissai`, which wears `RSW_*_HeavyBoneNormal` and was missing from his config.
- `Source/RSW_FacialAnimationOptOut.cs`: a Harmony postfix on `ShouldDrawRaceXenoType`, resolved by name. It only ever turns true into false. Without FA, `Prepare()` finds no target, so nothing is patched and nothing is logged; the assembly has no reference to FA (this is the C# equivalent of the FindMod guard).
- Mod Setting "Keep Facial Animation's face off our species", default ON (`RSW_StarWarsRacesMod.cs`, SettingsKit group, registered in `selftest_settings_screens.py`).
- StarWarsRaces gains its first assembly `Assemblies/RimMandrakeStarWarsRaces.dll` and a Harmony dependency.
- NOT listed (owner question, cosmetic): `RSW_MandrakeJawa` and `RSW_Jawa_Xeno_Gamorrean` wear vanilla heads and are absent from his config (his config's `Human-Jawa_Xeno_Gamorrean` is the pre-rename name). Adding them would change how they look today.

## Verify
- L1 offline, done: `python3 src/RimStarWars/StarWarsRaces/selftest_fa_optout.py` checks that every src/ xenotype whose genes force an RSW_ head is listed (41 of 41), that every listed name exists, that the owner config is a subset (68 of 68), and that the FA DLL has the target method. Planted defects are caught. `validate_patch.py --defs` reports 0 errors.
- L2 live, owed: deploy StarWarsRaces. Rename the FA config aside so FA starts fresh, load a quicktest with FA active, and spawn a painted-head species (for example Rodian, Twi'lek, Sith Kissai). The head must show no FA eyes or mouth, and the log must show `[RimMandrake.StarWarsRaces] Harmony: patched 1, missing 0`. Then restore the owner's config.
