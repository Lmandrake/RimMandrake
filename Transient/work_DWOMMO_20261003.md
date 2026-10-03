# DWOMMO 2026-10-03 (started)
## Choices (GELATINOUSSLIME_DWOMMO_FLIER_1)
- Census: no dwommo in src/ or artpipe before (find: 0). Template donor stays in reserve.
- Defs/ThingDefs_Races/Dwommo.xml: RM_Dwommo (Bird body, bs 0.6, MaxFlightTime 60, FlightCooldown 2, flightSpeedFactor 1.5, flightStartChance 0.6, canFlyIntoMap, canLeaveMapFlying false, non-predator, manhunter 0, SlimeResistantExtension) + PawnKindDef. No flyingAnimation* (no frames), no Spastic node. All // INVENTED.
- Biome: RM_Dwommo 0.2 inline on wildAnimals.
- Toggle: SlimeSettings.dwommoFlies -> Source/DwommoFlight.cs (in csproj) zeroes/restores the MaxFlightTime statBase at startup and WriteSettings (stat caches on spawned pawns may lag).
- Not built: "lands only on hardened slime" (flavour text only, no behaviour code); the amber glow is art only.
- Validation: new component dwommo_flight_def: offline XML check (MaxFlightTime>0, cooldown, speed factor, no Spastic/flip-book) always runs; live statBases read reports UNMEASURED if unserialised. Mock+fault noflight. Selftest 50 clean / 23 faults / 0 problems.
- Art: 3 jobs filed in artpipe pending (RM_Dwommo east/north/south) from the turn1 CSV row; texPath magenta until generated (3 validate_patch WARNs, 0 errors).
- Build: winbuild GelatinousSlime ok.
