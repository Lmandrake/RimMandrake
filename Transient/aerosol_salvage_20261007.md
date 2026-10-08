# Aerosol salvage (part 7) 2026-10-07 — built, offline only, never run in game

Files (all under src/RimMandrake/Scarlands/): Source/RM_WarscarRings.cs (condition enum+comp fields, roll, inspect, gizmos, DoSalvage), Source/RM_WarscarSalvage.cs (new: designation DefOf, 3 WorkGivers, 3 JobDrivers), Source/RM_WarscarMod.cs (ringSalvageEnabled + projectorCoreChance, scribed + UI), Source/RM_Warscar.csproj (Compile Include), Defs/JobDefs/RM_RingSalvageJobs.xml (new), Defs/ThingDefs_Buildings/RM_WarscarProjectors.xml (wild flag, new RM_WarscarProjector_Salvaged).

Choices:
- Condition: Dead def always dead; Live def 70% working / 30% failing; genstep forces ring #1 Working. Saved (ringCond, ringEvaluated). Inspect says "unassessed" until evaluated. Only a Working ring screens (failing stutters, no dome, no analysis).
- Evaluate: Crafting 6, 2500 ticks. Driven by designation from ring gizmo + WorkGiver.
- Working/failing wild ring -> salvage job (Crafting 6, 3000 ticks) destroys ring, spawns minified RM_WarscarProjector_Salvaged carrying the condition. Own def, not same def: self-powered (needsPower=false), no research, reinstall via vanilla install designator; vanilla uninstall works after install. Dome ends when the ring despawns.
- Failing salvaged ring: Repair job (Crafting 8, 2 ComponentIndustrial hauled, 4000 ticks) -> Working. WreckedMachines ladder NOT reused: it is a def-level DefModExtension, not a comp.
- Dead ring: strip job destroys it in code, drops steel 30-60, components 1-3, RM_ProjectorCore at projectorCoreChance (default 0.3). Code drop chosen because wild buildings are not deconstructible (no faction); leavingsDef not used.
- Why designations: wild rings have no faction, so vanilla uninstall/deconstruct designators refuse them.

Build: winbuild Scarlands csproj: 0 errors, 0 warnings. validate_patch: 0 errors (2 advisory activateTexPath warnings, pre-existing).
Unverified: everything in game (gizmos on unowned buildings, WorkGivers firing, MakeMinified of a fresh building, install designator for a def with no designationCategory, StartCarryThing signature semantics, DefOf static ctor pattern); no --defs validation; UI icon path UI/Designators/Deconstruct unchecked; spec part 9 not started; item file and the RM_AerosolScreen.xml "Not yet part 7" header comment not updated; nothing committed.
