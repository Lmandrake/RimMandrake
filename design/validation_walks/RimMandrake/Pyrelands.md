# Pyrelands — validation walk
subject: src/RimMandrake/Pyrelands  (packageId `mandrake.rm.pyrelands`)
deps: none — self-contained biome mod (own terrain/plants/weathers, RM_FE_ prefix); fauna wiring rides mandrake.rut.patches (WildAnimals_Pyrelands.xml)
list: minimal+mandrake.rm.pyrelands+mandrake.rut.patches
status-hint: THE campaign biome since PYRELANDS_WORLD_SWITCH_1 (2026-09-18): all 222 of Ash'karr's Pyrelands tiles are RM_FE_Pyrelands; the ZBiome_Grasslands donor is retired from the worldmap.

## must be true
- A generated RM_FE_Pyrelands map's plant population comes from the biome's own
  roster (RM_FE_Plant_EmberGrass, RM_FE_Plant_Quickgrass, RM_FE_Plant_ScorchFruit
  and any later ruled additions) — not from other mods' global flora injection.
- A generated RM_FE_Pyrelands map's wild animal population comes from the def's
  wildAnimals list as patched (core placeholder 13 + FindMod adds today; the
  ruled roster once PYRELANDS_FAUNA_WIRING_1 completes) — no foreign kinds.
- GenStep_Animals completes on Pyrelands mapgen with no
  BiomeDef.CommonalityOfAnimal NRE (a dangling wildAnimals PawnKindDef key kills
  the whole genstep and GiddyUp's startup cache — see MAYREQUIRE_OPERATION_INERT_SWEEP_1).

## the walk
1. [L] Player.log after a Pyrelands map generation contains no
   ArgumentNullException through RimWorld.BiomeDef.CommonalityOfAnimal and no
   "Could not resolve cross-reference: No Verse.PawnKindDef named ... to give to
   RimWorld.BiomeAnimalRecord"
2. [B] generate a fresh RM_FE_Pyrelands map, save it; per-map plant census of the
   save (iterparse `<thing>` defs per `<maps>/<li>`) → every plant def present is
   on the biome's own roster; foreign plant defs number ZERO. (Instrument and
   2026-09-17 baseline: Transient/pyre-census method — measured 78% foreign
   plants, 45 alien defs led by GRim*/TreePalma/Areebian*/AB_* before the fix.)
3. [B] same save, pawn-kind census of wild (factionless) pawns → every kind is in
   the live wildAnimals list of RM_FE_Pyrelands (jawa/get_def read-back at run
   time, not a doc); foreign wild kinds number ZERO. (2026-09-17 baseline:
   RSW_Bantha ×7, GRimCobra ×2, Squirrel ×2, Turkey ×1 present wrongly.)
4. [D] def read-back: RM_FE_Pyrelands wildAnimals resolves every key to a live
   PawnKindDef (no null keys); entries for kinds from optional mods carry
   MayRequire on the keyed element (never on a patch Operation — inert).
X. [S] (human pass) walk a fresh Pyrelands map at play zoom: the ground cover
   reads as ember/quick grass on the scorchable-terrain ladder, and the fauna
   read as the fire-ecology cast, not a mixed zoo.

## north star
state: VALIDATED
validated-hash: 90a286aa83f12acdeb8cc6a8f94b10b23efd3f2aa58e991edfe72bc7f88a6e2c

Owner, 2026-09-17 (verbatim): *"Any wrong animals present? Btw these are two
validation script bars you should add for pyrelands. Correct animal and plant
distributions."*

### must show

**The biome's own populations**
- [ ] `pyre_plant_distribution_correct` — the plants on a Pyrelands map are the
      biome's own flora roster; no other mod's grasses, trees, bushes or fungi
      appear via global biome injection.
- [ ] `pyre_animal_distribution_correct` — the wild animals on a Pyrelands map
      are the biome's wildAnimals roster; no foreign kinds wander in through
      other mods' biome-blind spawn patches.
