# UNUSED_MUTATORS_WORLD_ASSIGNMENT_1 — put the unused tile mutators and landforms on the frozen world

Owner, 2026-09-06: *"File a ticket for us to put all of those unused mutators and
landforms on the world. That's a bunch of content we're not even using."*

## measured (2026-09-06)

- `world/ASHKARR_WORLDMAP_mutators.csv`: 6,710 tiles carry mutators, **88 distinct**
  mutator defNames in use (top: Caves 1,540 · Dunes 1,501 · VEE_DeepOreDevoid /
  VEE_MineralDevoid 1,455 · Mountain 1,249 · MineralRich 382 · VEE_SaltPlains 325 ·
  Oasis 247 · River 239 · Cliffs 151).
- Available on the full list: ~336 `TileMutatorDef`s (vanilla + VLE 151 + Alpha
  Biomes + Dark Ages …) plus Geological Landforms' 44 stock landforms as
  `GL_<Id>` TileMutatorDefs (P14/§5.8 of `map_content_injection_research.md`).
- **Zero `GL_*` ids on the frozen world.** Geological Landforms is installed,
  active, and entirely unused by Ash'karr today.
- With Odyssey active GL auto-disables 14 of its own (Archipelago, Coast, Cove,
  Cliff, CliffCorner, CliffAndCoast, CoastalIsland, DryLake, Fjord, Lake,
  LakeWithIsland, Oasis, Peninsula, Valley) in favour of vanilla's — those are a
  settings choice (`Config\Mod_2773943594_GeologicalLandformsMod.xml`), not a ban.

## spec

1. **Exact census** (offline, haiku-tier): every TileMutatorDef on the full list
   (live def dump, `official`) minus the 88 in use → the UNUSED roster, with label,
   source mod, `categories`, and any biome/hilliness/coast gate the worker declares.
   Same for the 30 non-disabled GL landforms and the 14 disabled ones, flagged.
2. **Contact sheet for the owner** (bridge, one quicktest session): one quicktest map
   per candidate mutator, forced onto the tile with `jawa/world_mutators_set` before
   `jawa/world_tile_map_generate`, whole-map screenshot each, one review sheet
   (`review-sheets` skill). ⚠️ For GL landforms prove first that setting a
   `GL_<Id>` mutator on a tile actually makes `TileMutatorWorker_Landform` apply it
   — on the 2026-09-06 quicktest world GL placed NO `GL_*` mutators itself, so the
   mutator route for GL is unproven. GL's own log line
   `Map generator context: TileId: N, Landforms: X` is the proof string.
3. **Owner picks** on the sheet: keep / cut, and which biome sheet(s) each keeper
   belongs to (`design/Jawa/worldbuilding/biomes/*.md` field 8).
4. **Assignment** (bridge, opus per `Agent_Policy.md` — the frozen world): per
   keeper, a tile rule (biome + hilliness + coast/river adjacency + region), applied
   with `world_mutators_set` in batches, `world_commit`, read back with
   `world_mutators_get` — never the write's return value. Respect the
   anti-bullseye caveat (no regularising into rings) and category conflicts
   (`AddMutator` resolves them; log what it dropped).
5. **Re-export** `world/ASHKARR_WORLDMAP_mutators.csv` and restamp
   (`verify_frozen.py --restamp`), then a review save with a grid key.

## verify

```
PROVE   world_mutators_get over the assigned tiles lists the new mutator; GL log names the landform on a quicktest of one assigned tile
EXPECT  the census's UNUSED count drops by exactly the number of keepers; no tile gained a mutator the owner did not pick
LIES    world_mutators_set reports success while AddMutator's category conflict silently drops the add — read back, count, diff against the CSV
```

## not chasing

Custom (our own) landforms — that is the map generator (§9.3). Landmark
re-rolls (`WORLD_MUTATOR_LANDMARK_IMPORTERS_1`, dropped).
