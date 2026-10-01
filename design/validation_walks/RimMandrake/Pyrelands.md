# Pyrelands — validation walk
subject: src/RimMandrake/Pyrelands  (dev source folder, own About.xml packageId `mandrake.rm.pyrelands`, which is never deployed standalone: the biome ships COMPOSED inside `mandrake.rm.biomes`, RimMandrake: Baroque Biomes — test that)
feature: biome-core
deps: mandrake.rm.biomes (the composed biome itself); mandrake.rut.patches (the fauna roster is patch-added, UtinniPatches/Patches/WildAnimals_Pyrelands.xml); mandrake.rsw.swbestiary (seven roster keys — the guard on that patch Operation is inert, so the tier must carry it); mandrake.rut.pyrelandsmechanics
list: minimal+mandrake.rm.biomes+mandrake.rut.patches+mandrake.rsw.swbestiary+mandrake.rut.pyrelandsmechanics
status-hint: THE campaign fire biome; its BiomeDef is RM_Pyrelands (renamed from RM_FE_Pyrelands, PYRELANDS_DEFNAME_RENAME_1, closed). Tile assignment is redone wholesale at the one planet-painting pass, so a tile count is never evidence about this biome. Trial plan: design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md.

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
validated-hash: eca2fe9b0bd54f26ae17fac366c34ed410e796927dda5c0b9131e0a858ac652a

Owner, 2026-09-17 (verbatim): *"Any wrong animals present? Btw these are two
validation script bars you should add for pyrelands. Correct animal and plant
distributions."* The remaining bars are distilled from the owner-ruled biome
sheet and the shipped mechanics; each is one thing a player can check on a
freshly generated Pyrelands map in ordinary play.

### must show

**The biome's own populations**
- [ ] `pyre_plant_distribution_correct` — every wild plant on a fresh Pyrelands
      map is ember grass, quick grass or scorch-fruit; no other wild plant
      species grows there.
- [ ] `pyre_animal_distribution_correct` — every wild animal on a fresh
      Pyrelands map belongs to the biome's fire-ecology cast, no other kind
      wanders in, and the small common grazers outnumber the big predators.
- [ ] `pyre_mapgen_log_clean` — generating a fresh Pyrelands map raises no
      error message on screen.

**The fire ecology**
- [ ] `pyre_ground_ash_ladder` — all exposed soil, sand and gravel on a fresh
      Pyrelands map is scorchable ground, and repeated burns visibly darken it
      through trace, light, heavy and deep ash stages.
- [ ] `pyre_grass_chokes_ground` — unburned soil is carpeted densely in grass;
      there are no bare-dirt expanses where grass should carry the ground.
- [ ] `pyre_embergrass_regrows` — a burned patch of grass is visibly
      re-greening within a few days and largely green again within about a
      week, at the biome's own heat.
- [ ] `pyre_burn_line_present` — a fresh Pyrelands map shows an active line
      of fire somewhere, with a visibly scorched trail behind its advancing
      front.
- [ ] `pyre_scorchfruit_fire_born` — scorch-fruit appears only on freshly
      burned ground, never as ordinary wild growth on unburned land.
- [ ] `pyre_scorchfruit_produces` — a ripe scorch-fruit plant yields edible
      fruit that a colonist can harvest, and eating it raises a hungry
      colonist's food meter.
- [ ] `pyre_scorchfruit_spoils_fast` — unrefrigerated, harvested scorch-fruit
      rots within about four days, and a ripe unharvested plant withers within
      about a day.
- [ ] `pyre_ruins_scorched` — ruins on a fresh Pyrelands map stand blackened
      and fire-scarred, not pristine.
- [ ] `pyre_fulgurite_after_lightning` — after a dry-lightning storm strikes
      sandy ground, at least one impact site bears a visible lump of fulgurite
      glass.

**The fire cast at work**
- [ ] `pyre_firehawk_carries_ember` — a fire-hawk picks up a burning twig and
      a new fire starts where it drops it, ahead of the existing blaze.
- [ ] `pyre_furnacebeast_warmth` — a pawn standing in the open near a
      furnace-beast shows a readable warmth status that disappears after it
      walks away.
- [ ] `pyre_furnacebeast_heats_room` — an enclosed room holding a
      furnace-beast becomes clearly hotter than a comparable room without
      one.
- [ ] `pyre_burrowers_dive` — when fire reaches a burrowing grazer it shows a
      readable burrowed status and comes through unharmed once the fire has
      passed.

**The weather**
- [ ] `pyre_ashfall_darkens_drifts` — ash fall dims the map and lays visible
      loose-ash drifts that keep accumulating while it lasts.
- [ ] `pyre_cinderfall_distinct` — cinderfall is recognisable at a glance as
      its own weather, not ash fall renamed.
- [ ] `pyre_blackrain_reads` — black rain falls visibly dark, plainly
      different from ordinary blue-grey rain.

### cannot show
- [ ] `pyre_cannot_ordinary_rain` — ordinary rain falling on a Pyrelands map;
      its only wet weather is black rain.
