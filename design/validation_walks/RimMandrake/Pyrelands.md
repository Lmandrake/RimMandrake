# Pyrelands — validation walk
subject: src/RimMandrake/Pyrelands  (packageId `mandrake.rm.pyrelands`)
feature: biome-core
deps: none — self-contained biome mod (own terrain/plants/weathers, RM_FE_ prefix); fauna wiring rides mandrake.rut.patches (WildAnimals_Pyrelands.xml)
list: minimal+mandrake.rm.pyrelands+mandrake.rut.patches
status-hint: THE campaign biome since PYRELANDS_WORLD_SWITCH_1 (2026-09-18): all 222 of Ash'karr's Pyrelands tiles are RM_Pyrelands (renamed from RM_FE_Pyrelands, PYRELANDS_DEFNAME_RENAME_1, closed); the ZBiome_Grasslands donor is retired from the worldmap.

## must be true
- A generated RM_Pyrelands map's plant population comes from the biome's own
  roster (RM_FE_Plant_EmberGrass, RM_FE_Plant_Quickgrass, RM_FE_Plant_ScorchFruit
  and any later ruled additions) — not from other mods' global flora injection.
- A generated RM_Pyrelands map's wild animal population comes from the def's
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
2. [B] generate a fresh RM_Pyrelands map ON A TILE WHOSE NEIGHBOURS ARE ALSO
   RM_Pyrelands (⚠️ m00nl1ght.geologicallandforms.biometransitions blends NEIGHBOUR biomes into a map's edge zones (owner confirmed 2026-09-17; deactivated in the live list for the R&D phase, still in ModsConfig.FULL.LATEST for play),
   so a lone re-tiled scratch tile censuses as contaminated when it is not —
   measured 2026-09-17: 78% foreign plants, 45 alien defs led by
   GRim*/TreePalma/Areebian*, regionally zoned, on a tile ringed by GRiNDTerra
   biomes; the campaign's 222-tile regions have interior tiles). Save it;
   per-map plant census of the save (iterparse `<thing>` defs, keyed by the
   record's own `<map>` field) → every plant def present is on the biome's own
   roster; foreign plant defs number ZERO.
3. [B] same save, pawn-kind census of wild (factionless) pawns → every kind is in
   the live wildAnimals list of RM_Pyrelands (jawa/get_def read-back at run
   time, not a doc); foreign wild kinds number ZERO. Same interior-tile rule as
   step 2. (2026-09-17 lone-tile baseline: RSW_Bantha ×7, GRimCobra ×2,
   Squirrel ×2, Turkey ×1 present.)
4. [D] def read-back: RM_Pyrelands wildAnimals resolves every key to a live
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

**The fire ecology**
- [ ] `pyre_ground_ash_ladder` — the ground reads as the scorchable family with
      real ash states after burns (trace through deep), not stock desert ground.
- [ ] `pyre_grass_chokes_ground` — ember/quick grass carpets unburned soil
      densely; no bare-dirt expanses where grass should carry the ground.
- [ ] `pyre_embergrass_regrows` — a burned patch re-greens within days; the
      burn-and-regrow cycle is readable in ordinary play, not just in defs.
- [ ] `pyre_scorchfruit_produces` — scorch-fruit plants bear a harvestable
      yield a colonist can actually pick and eat.
- [ ] `pyre_scorchfruit_spoils_fast` — that yield visibly spoils within days
      (faster still on the plant) — eat-or-lose pressure, no walking a
      stockpile out of the biome.
- [ ] `pyre_ashfall_darkens_drifts` — ash fall dims the map and lays visible
      loose-ash drifts that accumulate while it lasts.
- [ ] `pyre_cinderfall_distinct` — cinderfall reads as its own weather at a
      glance, not ash fall renamed.
- [ ] `pyre_blackrain_reads` — black rain reads as black rain, visually its own
      event among the biome's weathers.
