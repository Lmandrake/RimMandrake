## diagnosis
Mod: Cherry Picker (`Owlchemist.CherryPicker`). Its kill list holds `ThingDef/Beer`, so it sets Beer's `ingestible.drugCategory` to None and strips DrugPolicyDef entries, but a save's own DrugPolicy keeps its Beer entry. Pawns reading that policy log 'AllowedToTakeScheduledEver on non-drug Beer'. "Then almost none" in `Player_ee0fbaa8.log` is the Verse.Log message cap, not the errors stopping.

## fix
`CutDrugPolicyGuard` in RimMandrake Patches (`src/RimMandrake/MandrakePatches/Source/CutDrugPolicyGuard/CutDrugPolicyGuard.cs`), built in 837b152d83: a Harmony postfix on `DrugPolicy.ExposeData` at PostLoadInit removes cut drugs from a loaded policy; default-on toggle. Whether Beer should stay cut is `BEER_CUT_DECIDE_BARREL_STILL_BREWS_IT`.

## rebuild note
2dd007742f (`LOVIN_LOGSPAM_DIAGNOSE_IN_PLAY_EVICTIONS`) rebuilt the shared `RimMandrakePatches.dll` from a tree holding the guard's source unchanged (its hash is in the `.srchash`), and added unrelated lines to `RM_PatchesMod.cs` and `selftest_mandrakepatches.py`. No guard code changed; the live clause A1 is owed against the commit carrying this note.
