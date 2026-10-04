# MIASMA_ROTTING_BED_CORPSES_1 — the rotting bed takes corpses and gives back skulls and bones

Split from `MIASMA_DECAY_CELLS_1` spec 4 (part A built `4b0614b9f`). Owner, typed 2026-10-02: *"That rotting bed could
also be used to corpse dispose as well... and produce skulls and bones!"* Free tier, `mandrake.rm.miasma`.

## spec (numbers `// INVENTED`)
1. `RM_RottingBed` (`src/RimMandrake/Miasma/Defs/ThingDefs_Buildings/RM_DecayCell.xml`) accepts corpses as a disposal
   target, hauled like a grave or a crematorium (a corpse-filtered storage building, or a bill), one at a time.
2. A corpse in the bed rots down over a few days, then is consumed and leaves bones and, for a humanlike, its skull.
3. MEASURED 2026-10-03 (RimSage): Core 1.6 has ThingDef `Skull` (`Items_Resource_AnimalProduct.xml`, `CompHasSources`,
   so it records whose it was). No bone item exists in 1.6 + DLCs or in `src/`: invent `RM_Bones` (placeholder art, art job).
4. Settings: on/off and the rot-down days. The bed's Star Wars Cuisine yield stays `MIASMA_ROTTING_BED_CUISINE_1`.

## criteria
- A corpse hauled to the bed is consumed after the rot-down and leaves bones; a humanlike's skull names its source.
