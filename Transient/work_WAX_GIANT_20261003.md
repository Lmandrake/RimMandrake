# CHILL_WAX_PROCESSION_GIANT_1 work notes (2026-10-03)
Item has no prose; spec = the_propane_lake_floor_sitting_agenda_2026-10-02.md section 4 idea 1 + Q4b (yes: the Procession is the floor's giant, fills Q1(a) hole).
Choices (scaled to M, reduced vs the sketch):
- Race RM_Hesuun ("hesuun", invented name, RM_ tier, no canon; artpipe + src searched: no prior art/def). Giant OmnivoreAnimal bodySize 3.5, MoveSpeed 0.9, untameable (trainability None), not predator, no flight. Row on RM_TheChill wildAnimals at 0.12, wildGroupSize 3~5 (a "file").
- Mechanic is ONE ThingComp (RM_Comp_WaxProcession), not LordJob + MapComponent + WorkGiver: pauses = the colony being stationary at a CompTickRare; a countdown (about 2 days, settings-scaled) runs while walking and a dead filter sheet RM_DeadFilterSheet is extruded at the first stationary moment after it elapses. Collection/return is ordinary hauling (sheet is alwaysHaulable, deteriorates, so distance + time are the pressure). No custom collect job: vanilla haul covers it; the agenda's own System line says "ordinary hauling handles the return".
- Kill spoils: PostDestroy(KillFinalize) turns the colony's uncollected sheets and the pending one into RM_HydrocarbonFlesh (existing def, ordinary fuel-chain flesh), never a sheet.
- Sheet is the only export, an inert industrial item; colony not fishable, not tameable.
- Mod Settings: TerminalBiomes HAS a settings class; added chillWaxProcessionEnabled (+ ChillWaxProcessionActive) and a Mod Settings checkbox. Off = no new sheets (defs/row remain; def rows cannot be gated by a toggle).
- Art: artpipe has none; placeholder = flat generated silhouette PNG 256x256 (Textures/Things/Pawn/Animal/RM_Hesuun); sheet reuses own-mod Pitchpearl sprite; real art owed, not queued. Spoil product = existing RM_HydrocarbonFlesh (also the meatDef).
- Live behaviour UNMEASURED (no bridge); validation is def/source level, live pause/extrude reported UNMEASURED.
