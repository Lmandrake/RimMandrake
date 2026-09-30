# WASTELAND_GRIPPER_STEAL_BEHAVIOR_1: report

## Source ruling
`Transient/bedazzle_art_sheets_2026-09-28/wasteland/sheet.decisions.json`, row `RM_Middenbeetle`
(decision `improve`, 2026-09-29T03:56Z), typed note:
> "This beast is capable of stealing. Needs a new name to deconflict Middenshell. How about a Gripper? Always carrying something."

The cast bible entry (`design/Jawa/worldbuilding/biomes/wasteland_survivor_cast_2026-09-28.md` §Middenbeetle) adds "hauling scraps of everything back to middens" and "Swarms a carcass, never a colonist." The ruling doesn't mention tamed grippers, so a tamed gripper never steals and keeps whatever it already holds.

## Spec (what was built)
- **Gate:** `RM_CompGripperThief` is on `RM_Gripper` only. The job giver returns nothing without that comp, and it also returns nothing for any pawn with a faction, a downed pawn or a pawn in a mental state. Mod Settings (Wasteland) has `gripperTheftEnabled` (default on), `gripperSpawnsCarrying` (default on) and `gripperTheftMtbHours` (default 3 h, slider 0.5 to 24). The master Wasteland toggle also gates it.
- **Always carrying:** a wild gripper spawned fresh (not on load) gets one random scrap put into its inventory: Steel 2–5, Silver 5–20, Cloth 3–10 or ComponentIndustrial 1. The item shows in the vanilla Gear tab, because `ITab_Pawn_Gear.ShouldShowInventory` shows a non-humanlike's inventory when it holds anything. The inspect pane also reads "Gripping: X".
- **Steal:** a ThinkTreeDef is spliced into Core `Animal` at `Animal_PreWander` (insertPriority 45). That is after needs, mating and trained work, and before idle wandering. It sits behind an MTB node that reads the settings value (vanilla `ThinkNode_ChancePerHour`, which makes at most one roll per 2500 ticks). The target is found with `GenClosest.ClosestThingReachable` over `HaulableEver` within 20 cells, at Danger.Some. It must be a spawned item that is EverHaulable. Corpses, minified things, pawns and burning things are excluded, as are items forbidden to the player and items in fog. The pawn must be able to reserve it. At least one unit must fit the 3 kg mass cap, and the take is capped at 10 units. Its value times the units taken must be greater than the value of what the gripper already carries, so it swaps up and never down. Reachability covers "a stockpile it can't reach", since wild animals can't open doors.
- **Job** `RM_GripperSteal` (custom `RM_JobDriver_GripperSteal`) runs these steps:
  1. Jog to the item.
  2. Drop the old scrap there.
  3. Take the item into inventory with `Toils_Haul.TakeToInventory`.
  4. Scurry to a random wander cell 6–12 cells away.

  It fails if the gripper gains a faction mid-job, or if the target despawns or is forbidden during the approach. It expires after 2000 ticks.
- **Why inventory, not carryTracker:** RimSage showed that `Pawn_JobTracker` drops a carried thing at every job start and end unless the job def says `carryThingAfterJob`. Wander jobs don't, so the item would fall at the first wander. Inventory persists.
- **Drop on harm/death:** each damaging hit has a 50% chance to drop the whole haul (`inventory.DropAllNearPawn`, not forbidden). On death the vanilla `Pawn.Kill → DropAndForbidEverything` empties the inventory with forbid:true. It does the same when the gripper is downed (`Pawn_HealthTracker`), so a killed thief's loot lands forbidden, as it does for every pawn.

## Engine seams confirmed (RimSage, decompiled 1.6)
Core `Animal` ThinkTreeDef (the `Animal_PreWander` tag) · `ThinkNode_ChancePerHour.MtbHours` · `Pawn_CarryTracker` plus the drop lines in `Pawn_JobTracker` (lines 358 and 509) · `JobDriver_TakeInventory` / `Toils_Haul.TakeToInventory` / `ErrorCheckForCarry` · `ForbidUtility.IsForbidden` (wild pawns don't care about forbidden, so the filter checks against `Faction.OfPlayer` explicitly) · `Pawn.DropAndForbidEverything` callers · `PawnComponentsUtility` (every pawn has an inventory) · `ITab_Pawn_Gear.ShouldShowInventory` · `RCellFinder.RandomWanderDestFor` (radius ≤ 12, falls back to pawn.Position) · `ThingDefCountRangeClass` custom loader · `GenClosest.ClosestThingReachable` signature.

## Files
- `src/RimMandrake/Wasteland/Source/RM_GripperTheft.cs` (new; comp, props, MTB node, job giver, job driver, DefOf)
- `src/RimMandrake/Wasteland/Defs/ThinkTreeDefs/RM_GripperTheft.xml` (new; JobDef and ThinkTreeDef)
- `src/RimMandrake/Wasteland/Defs/ThingDefs_Races/RM_Gripper.xml` (comp added; removed the stale "no theft mechanic is wired" comment)
- `src/RimMandrake/Wasteland/Source/RM_WastelandMod.cs` (3 settings, UI, header)
- `src/RimMandrake/Wasteland/Source/RM_Wasteland.csproj` (`<Compile Include="RM_GripperTheft.cs" />`)
- `src/RimMandrake/Wasteland/Assemblies/RimMandrake.Wasteland.dll` plus `.srchash`

## Verify
- XML: both def files parse (ElementTree).
- `dotnet build -c Release`: Build succeeded, 0 warnings, 0 errors.
- `run_selftests.py`: 76/78 passed. The one failure is the known `selftest_deployed_biome_refs.py`, and `selftest_tool_metadata.py` could not run here (UNMEASURED).
- **Unverified (not live-tested, by brief):** that the in-game def loads cleanly (comp XML, `ThingDefCountRangeClass` list, ThinkTree splice); that a wild gripper actually picks, swaps and scurries; the balance of the 3 h MTB. Not deployed.
