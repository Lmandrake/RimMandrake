# TheftHauler — validation walk
subject: src/RimMandrake/TheftHauler  (packageId mandrake.rm.theft_hauler)
deps: mandrake.rm.property (hard, modDependencies); loadAfter also mandrake.rsw.droidworks (soft, MayRequire-gated patch only)
list: minimal+property   # the Droidworks-marked-chassis patch check additionally needs +droidworks; note per-step
status-hint: the heist verb — a pawn carrying `RM_TheftHaulerExtension` can uninstall ANY Building (not gated by ownership) into a haulable MinifiedThing via a right-click order, firing `RimMandrake.Property.PropertyEngine.Fire(TakingEvent(Act=Strip))` at the moment of uninstall. Ships a MayRequire-gated patch marking Droidworks' Muckraker Crab Droid chassis as the reused heavy hauler.

## must be true
- `JobDef RM_TheftHaulUninstall` loads and drives `RimMandrake.TheftHauler.JobDriver_TheftHaulUninstall` (a `JobDriver_RemoveBuilding` subclass) with `suspendable=false`.
- `FloatMenuOptionProvider_TheftHaulUninstall.AppliesInt` only offers "Steal and haul away <building>" for a pawn whose race `ThingDef` carries `TheftHaulerExtension`, and only targets `Building`-category, `Minifiable` things.
- `JobDriver_TheftHaulUninstall.FinishedRemoving` fires `PropertyEngine.Fire(TakingEvent(Act=Strip))` unconditionally BEFORE calling the real `MinifyUtility.Uninstall()` (via `Building.Uninstall()`), then enqueues a `HaulToStorageJob` for the resulting `MinifiedThing` so it doesn't just sit at the removed building's old position.
- The `MuckrakerChassis_TheftHauler.xml` patch (`PatchOperationFindMod MayRequire="mandrake.rsw.droidworks"`) is a silent no-op with Droidworks absent, and APPENDS `TheftHaulerExtension` to `RSW_DW_Race_OuterRim_MuckrakerDroid`'s existing `modExtensions` list (not replacing it — `DroidworksExtension` must survive) when present.
- `DebugActions_TheftHauler`'s "Test: theft-haul-uninstall clicked building (any pawn, bypasses chassis gate)" action reuses the SAME `category != Building || !Minifiable` gate as the real float-menu provider, and refuses (Log.Warning, no job) a target failing either check.
- Without Droidworks active, no pawn kind on the map carries `TheftHaulerExtension`, so the REAL float-menu option never appears for anyone — the debug action is the only way to exercise the job driver on this mod list.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.theft_hauler" and no XML error naming `JobDefs_TheftHauler.xml` or `MuckrakerChassis_TheftHauler.xml`
2. [D] def read-back: `JobDef` `RM_TheftHaulUninstall` exists; `driverClass` = "RimMandrake.TheftHauler.JobDriver_TheftHaulUninstall", `suspendable` = false
3. [D] with Droidworks NOT active (current live mod list, per this mod's own DebugActions comment): a def dump of `RSW_DW_Race_OuterRim_MuckrakerDroid` either does not exist or shows no `TheftHaulerExtension` in `modExtensions` — confirms the MayRequire gate is truly a no-op absent the dependency
4. [B] `rimworld/search_debug_actions {"query": "theft-haul-uninstall"}` → returns exactly one match in category `RimMandrake.TheftHauler`, giving its stable path
5. [B] `jawa/list_things {"group": "BuildingArtificial"}` on a quicktest map → pick a real building's `ThingID`, then `rimworld/execute_debug_action {"path": "<path from step 4>", "thingId": "<that id>"}` → Player.log gets `[RimMandrake.TheftHauler] <pawn> ordered to theft-haul-uninstall <building> (faction ...) -- job started=True`
6. [B] `jawa/list_things {"defName": "<the building's defName>"}` before and after step 5's job completes → the live `Building` is gone and a `MinifiedThing` wrapping it exists instead (confirms `MinifyUtility.Uninstall()` actually ran, not just that the job started)
7. [D] `PropertyEngine.Fire`'s own success path is silent by design (Property.md: no Log.Message on a normal Fire call, only Log.Warning for a stackable Thing and Log.Error for a bad ClaimBasis) — there is no bridge tool to read `GameComponent_PropertyLedger`'s `Dictionary<Thing, ClaimRecordList>` directly (confirmed against Property.md's own walk: "PropertyEngine itself has no bridge tool"). This step is a known gap, not a check: attributing the theft to a real `ClaimRecord` currently needs a debugger or a new bridge tool, not this walk.
8. [D] with Droidworks active (list=minimal+property+droidworks): def read-back of `RSW_DW_Race_OuterRim_MuckrakerDroid` shows `TheftHaulerExtension` present in `modExtensions` ALONGSIDE `DroidworksExtension` (both, not one replacing the other)

[S] none — the whole mechanism resolves to a log line, a job outcome, and a def read-back; no rendered art is unique to this mod (it reuses Droidworks' existing chassis sprite unchanged).
