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
