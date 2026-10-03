# SCALD_FLOOR_VENT_FIELDS_1 work log 2026-10-03
Item has no prose; criteria = title + sitting Q3 ruling (a)/(c) in design/Jawa/worldbuilding/biomes/the_scald_floor_sitting_agenda_2026-10-02.md:
generate vent fields on the Scald floor map; anchor bubble-sailors (no placeholder penguin); vent flora (glasskelle, pulsebead); Sail Forecast (GPT idea 2) eruption warning.
Return Gallery is a separate item (SCALD_RETURN_GALLERY_1), not touched.

Mod folder edited: src/RimMandrake/DivingInteraction (new files only + csproj + settings lines).
One edit outside: TerminalBiomes/Defs/MapGeneration/RUT_ScaldSailScatterer.xml pawnKind Penguin -> RM_Noohm (def-only, no DLL).

Choices:
- Floor map generator that exists today = RM_SeaDiveGenerator_TheScald (hatch pocket map). The live RM_SeabedLayer has NO per-sea floor map generator yet (SEABED phase 2/3), so
  the new GenStepDef RM_ScaldVentField (order 870) is listed on RM_SeaDiveGenerator_TheScald only and refuses non-Scald maps. When a layer generator exists, list the step there.
- Vents: 3-5 RUT_ScaldVent (2x2), min spacing 14, clear of the dive-exit keep-out, spawned by GenStep.
- Flora: RM_Glasskelle (3-8 per vent r<=4), RM_Pulsebead (5-12 per vent r<=5), new defs RM_ScaldVentFlora.xml, tinted vanilla placeholder textures (same precedent as RM_Stillbloom); real art owed (queued, see below).
- Sailors: 2-3 RM_Noohm wild pawns per vent at gen. Tether by MapComponent sweep (noohm >10 cells from a vent are sent back to nearest), not a new comp on the pawn.
- Forecast: RM_MapComponent_ScaldVentForecast. Cycle: quiet 6000-12000 ticks -> warning 2500 ticks (every noohm gathers on the target vent, bubble flecks) -> discharge 300 ticks (burn damage r3 + job interrupt) -> quiet.
  Same warning behaviour precedes every discharge. Displacement of loose items NOT built (damage + interrupt only) - tuning numbers are guesses.
- Toggles (RM_DivingSettings): ventFieldsEnabled (worldgen-affecting), ventForecastEnabled, ventDischargeHarms.
- Does not read Scald.S4 gate of TerminalBiomes (no hard ref); the geyser's own spray gate there is separate.

Result: winbuild DivingInteraction BUILT (0 err). validate_patch: new defs only error = PlantBase unresolvable because Core is not under --defs (same parent used by Scarlands/Miasma plants); texPath warnings = vanilla bundle paths (RM_Stillbloom precedent). validation.py chain scald_vent_fields added (parse-checked only; no live run).
Art: artpipe searched first (0 hits), queued scald_glasskelle_v1 and scald_pulsebead_v1 (Transient/vent_art.json); defs still point at tinted vanilla placeholders until art is wired.
Unproven/owed: live run (vents land on standable floor, flora/sailors spawn, warning gather visibly works), Return Gallery separate, loose-item displacement, glasskelle keepsake item, floor generator for RM_SeabedLayer (step must be listed there once it exists).
