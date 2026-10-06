# FORGE_SPUNSTONE_SOURCES_1 — build log 2026-10-06 (FOUNDRY, offline, uncommitted)

Rulings (owner card 2026-10-03, via BENCH note): foundry salvage caches are a second spunstone study
source, campaign only; spunstone bonding unlocks the keel brace PLUS a light fast floatstone door AND
floatstone structural parts (light wall/beam for the ship).

## sweep
- `RUT_FoundrySalvageCache` lives in `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/` (inert shell,
  `tickerType Never`, no art). No floatstone door, wall, hull or beam existed anywhere in `src/`.
- Floatstone is `StoneBlocksBase` (Stony), so vanilla Wall/Door already accept it, but stone stuff is
  NOT airtight (RimSage 1.6: only metal stuffs set `stuffProps.isAirtight`).
- MEASURED (RimSage): gravship launch fuel is distance x `FuelUseageFactor` (linked facilities); mass
  never enters it. "Light" therefore has no mechanical lever.
- Odyssey `GravshipHull` has no `Name=` attribute, so it cannot be a ParentName (validate_patch --defs
  caught it); its body is copied onto `Wall`.

## shipped (TheForge only)
- `RM_SpunstoneWeave` StuffCategoryDef, carried by `RM_Floatstone` alone (Vexxith-plate pattern).
- `RM_FloatstoneDoor`: floatstone-only, airtight outright, DoorOpenSpeed base 2.5 (x0.8 = 200%), gated by
  `RM_SpunstoneBonding`. PROVISIONAL numbers.
- `RM_SpunstoneHull`: floatstone-only airtight gravship hull (Substructure only, GravshipHull body),
  gated by `RM_SpunstoneBonding`. PROVISIONAL numbers.
- Mod Settings: `floatstoneDoorEnabled`, `spunstoneHullEnabled` (restart to apply; startup gate
  `RM_SpunstonePartsGate` removes the designator, copied from `RM_VexxithDoorGate`). Window already
  scrolls with maxOneColumn=true.
- Research description and stale "not defined yet" comments corrected.
- validation.py: `def_wiring.spunstone_parts_need_spunstone_research` (live def read),
  `keelwork.spunstone_parts_source_floatstone_only_and_gated`, `keelwork.spunstone_hull_gate_keyed_on_toggle`
  (source claims, labelled); toggles added to WIRED; stale "27 settings" counts replaced.
  selftest: mock + break `parts_no_research` + two stripped-source checks.

## deferred
- Salvage cache as a study source: campaign-only, so the patch belongs in UtinniPatches (read-only for
  this pass). Shape: PatchOperationAdd onto `RUT_FoundrySalvageCache/comps` of
  `RimMandrake.TheForge.CompProperties_SpunstoneStudy` (project RM_SpunstoneBonding, frequencyTicks,
  studyEnabledByDefault false); the cache also needs `tickerType Rare` (it is `Never`, so the comp's
  Refresh would only run at spawn and never stop after the reveal or on a toggle flip).
- "Beam": not built. See open questions.
- Walk lines in `design/validation_walks/RimMandrake/TheForge.md` (read-only for this pass).

## validation
- winbuild TheForge: 0 warnings, 0 errors.
- validate_patch --defs (installed game) on TheForge Defs + Patches: 0 errors, 4 warnings (vanilla
  bundle texPaths, same as the Vexxith door).
- selftest_theforge.py: all passed, 98 healthy components, 64 breaks.

## art owed
`artpipe_state.py find floatstone` / `spunstone`: nothing for a door or hull (only RM_Floatstone,
RM_FloatstoneGarden, RM_FloatstoneKeelBrace). Owed: RM_FloatstoneDoor (mover + menu icon),
RM_SpunstoneHull (linked atlas + menu icon). Placeholders: vanilla simple door / gravship hull atlas
tinted by floatstone colour.

## open questions
1. Is the "beam" a separate part from the hull wall, and if so what does it DO (roof-holding column on
   substructure, or extra substructure capacity like a grav field extender, which the keel-brace ruling
   declined)?
2. "Light": nothing in vanilla gravship cost reads mass. Fiction only, or should the hull carry a
   mechanical effect (e.g. a fuel saving), which would need new C#?
