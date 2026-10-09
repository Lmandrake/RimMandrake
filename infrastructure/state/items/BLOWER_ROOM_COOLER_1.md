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
- A3 CHECK: Scene: `jawa/make_empty_room rect=<x1,z1,x2,z2>` (roofed, walled) then `jawa/spawn_batch ops="RM_DryAirBlower:<x>,<z>" rot=<N>` in a wall cell with rotation so its back cell (`position + South.RotatedBy(rotation)`, per `RM_CompBlowerRoomCooler.CoolOnce`) is inside the room; fuel it (`jawa/ordered_job jobDef=Refuel` as in `LuminousPigment/validation.py`), power it on a generator/battery (`jawa/power_net thing=<id>` must show CurrentEnergyGainRate>=0 and PowerOn), set target below room temp. Heat the room with `jawa/room_heat mode=set x=<inside> z=<inside> value=35`. Sample `jawa/room_get x= z=` (room temperature) inside and `jawa/cell_temperature cell="<x,z>"` on a cell just outside the front, every 250 ticks (`rimworld/step_game_ticks` chunks, clock verified by `jawa/time_clock`) for ~2000 ticks. Control: the same room with the blower switched off. PASS: inside temperature trends down toward the target (monotone non-increasing across samples, never above the previous sample by more than ambient drift) while the outside-front cell never rises above its first sample; the off control does not cool. FAIL: inside temperature rises at any sample while powered and fuelled (the blower heated the room), the outside front warms, or no cooling at all (check `jawa/comp_read thing=RM_DryAirBlower comp="BlowerRoomCooler"`; also `dryAirBlowerCoolingEnabled` must read true).
- A4 CHECK: Same scene as A3. Read the draw: `jawa/power_net thing=<blower id>` (CurrentEnergyGainRate before, with the blower cooling) at defaults 250 W; then `jawa/mod_settings_field typeName="RimMandrake.EnvironmentalHazards.RM_EnvironmentalHazardsSettings" action=set field="dryAirBlowerPowerWatts" value="500"` and re-read; set `dryAirBlowerCoolingStrength` 14 to 28 and compare the room temperature drop over the same 1000 ticks against a second identical room; restore all three fields. PASS: net draw changes by about the set difference (250 W more), and the strength-28 room cools about twice as fast as the strength-14 room over equal ticks. FAIL: draw unchanged after the set (the setting is not read at runtime), the cooling rates equal, or a field rejected by `jawa/mod_settings_field`.
