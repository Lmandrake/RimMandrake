# BLOWER_ROOM_COOLER_1 — the dry-air blower is a special room cooler that never heats a room

Decision taken by question card 2026-10-08. Owner typed: *"Just add this as a special kind of room
cooler. No one wants a room heater in that biome..."* Answers the open question that
`WETBULB_FOLD_INTO_HEAT_1` left (the blower's `CompHeatPusher` made the room behind it hotter).

## spec

1. `RM_DryAirBlower` (Greentide) loses `CompHeatPusher`. It gains vanilla `CompTempControl` (the
   target-temperature gizmo, `lowPowerConsumptionFactor` 0.3) and `RM_CompBlowerRoomCooler`
   (EnvironmentalHazards).
2. Every rare tick while powered, fuelled and switched on, it cools the enclosed room on its BACK
   cell (the cell a vanilla cooler cools) toward the target, through vanilla
   `GenTemperature.ControlTemperatureTempChange`. Any positive change is dropped
   (`RM_RoomCoolerKernel.ClampNeverHeat`), and there is no exhaust side: it never heats any room.
   Outdoors or an impassable back cell, it does nothing. One kind of heat: it changes room
   temperature only.
3. Mod Settings (Environmental Hazards Kit), PROVISIONAL: cooling on/off, strength 14 heat/s
   (vanilla cooler 21), power draw 250 W while cooling, 0.3x while idle.
4. Its dry-air role now that wet-bulb is folded: there is no "dry room" state. Cooling the room behind
   is its whole climate role; the dry-air curtain in front keeps the plant-growth suppression and the
   wild-animal repel. Description, aversion hediff text and the spec (M2) say so; "hot air" wording
   deleted.

## criteria

- A1 L0: EnvironmentalHazards DLL builds with the new comp; envhazards fuzz `cooler` family passes (energy <= 0, applied change <= 0, power bounded); validate_patch on RM_DryAirBlower.xml clean
- A2 L1: on a load, Player.log has no config error or cross-reference error naming RM_DryAirBlower, CompProperties_BlowerRoomCooler or CompProperties_TempControl
- A3 L2: live, a powered fuelled blower built into the wall of an enclosed room, front facing out, lowers that room toward its target and never raises it; the room outside its front is not heated
- A4 L2: live, changing the strength and power settings changes the cooling rate and the power draw shown on the power net
- H1 L4: the owner judges strength 14 and draw 250 W in a sitting (PROVISIONAL until then)

## verify

Run each criterion at its stated level and record it with `rimflow verify BLOWER_ROOM_COOLER_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- L0: offline build, selftest/fuzz/lint (already run at implementation).
- L1: one minimal-list load, read Player.log for config/cross-reference errors and the specific line, or one spawn-and-read bridge probe.
- L2: one quicktest map via the bridge or modcheck: set up the scenario in the criterion, step ticks, read the state named.
- L4: owner judgement in a sitting; not a FOUNDRY acceptance task.
Evidence is the Player.log line or bridge read the criterion names; a screenshot is not evidence of state.

### Exact checks 2026-10-09 (acceptance sitting)
- A2 CHECK: Read Player.log (WSL: `/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log`) after the load with regex `RM_DryAirBlower|CompProperties_BlowerRoomCooler|CompProperties_TempControl` restricted to lines also matching `Config error|Could not resolve cross-reference|XML error`. Positive control: `jawa/get_defs defs="ThingDef/RM_DryAirBlower" fields="defName"` (needs EnvironmentalHazards + Greentide loaded). PASS: zero matching error lines AND get_defs success=true, foundCount=1 (the def exists, so zero errors is not an absent mod). FAIL: any matching error line, or foundCount=0 (then the list lacked the mod: UNMEASURED, not pass).
