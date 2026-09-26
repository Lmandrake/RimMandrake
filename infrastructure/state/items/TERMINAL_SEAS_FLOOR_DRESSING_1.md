# TERMINAL_SEAS_FLOOR_DRESSING_1 — 5 owed terminal-seas floor/flora slugs

## what

Five slugs from `COMMISSION_LEDGER_CLEANUP_1`'s 85-row commission list, all
in the Grey Sea / Twilight Sea groups, verified 2026-09-26 (FOUNDRY) as
**still genuinely unbuilt** after `TERMINALBIOMES_RM_MOD_BUILD_1` landed the
rest of those two sheets' fauna:

- **Grey Sea**: `the pillar-mason` (crystal-binding film that builds
  mineral columns — referenced only as flavor text, "pillar-mason columns",
  in `RM_Sorruth`/`RM_Fessk`'s own descriptions in
  `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_GreySeaFauna.xml`;
  no def of its own exists), `salt-rimed blade flora, Grey shore variant`
  (endemic, distinct from Twilight's own).
- **Twilight Sea**: `salt-rimed blade flora` (Twilight variant, "black sail
  on white pan"), `the mold-mat roof organism` (the monoculture referenced
  constantly as "the mat-roof" in `RM_TwilightSeaFauna.xml`'s own
  descriptions — the biome's single most load-bearing piece of flavor text
  has no backing def), `condensate drinker (fog-lick fauna)` — checked every
  description in `RM_TwilightSeaFauna.xml` for "condensate"/"dew"/"fog" and
  found no match; the file's own header states its cast is a closed set of
  exactly 4 species (noolim/loohn/weloon/lunoowa) from
  `terminal_seas_cast_proposal_2026-09-25.md` verdict 1, **owner-approved as
  that specific four** — condensate-drinker was not among them, so it is a
  genuine gap between the ledger wish-list and the ruled roster, not a
  build omission.

Full per-row exact source rows: `design/Jawa/worldbuilding/biomes/rosters/
the_grey_sea.json` and `the_twilight_sea.json`, `new_defs` arrays.

## why it's not a plain PlantDef/wildAnimals add

Checked `RM_GreySea.xml`/`RM_TwilightSea.xml`
(`src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/`) directly: both are
`isWaterBiome=true`, `hasVirtualPlants=false`, **no `<wildPlants>` block at
all** — an ordinary terrestrial-style PlantDef commission (the pattern this
item's own prior waves used, e.g. `RUT_Fuzz`) does not fit this biome shape.
"Pillar-mason columns" and "the mat-roof" read as underwater/floor geology
and ceiling organisms respectively — the natural home for them is the
sea-floor pocket-map system `SEA_DIVE_MAPS_BUILD_1` (closed 2026-09-26,
`mandrake.rm.divinginteraction`) just built: `GenStep_SeaFloorTerrain`,
`GenStep_SeaFloorFauna`, `RM_SeaFloorHabitat` TileMutatorDef. That item's own
close note explicitly lists "per-sea floor dressing (chimney-iron ore, floor
droids, Scald Rakatan wreck, named bottom-walker fauna...)" as **deferred,
not owed by that close** — pillar-mason and the mat-roof are exactly that
class of floor dressing, just discovered from the other direction (the
ledger's wish-list) rather than that spec's own S2.2.

The two salt-rimed-blade-flora rows are plausibly the same floor-dressing
class (described as "planar, vertical, hundreds of metres apart" — reef/
floor scenery, not overworld-map wildPlants), though this needs confirming
against whatever floor-dressing content shape `SEA_DIVE_MAPS_BUILD_1`'s
eventual dressing pass settles on.

## work owed

1. Author pillar-mason (Grey) and the mat-roof organism (Twilight) as
   floor-dressing content inside the `RM_SeaDiveGenerator_GreySea`/
   `_TwilightSea` pocket-map generators (or whatever shape a future
   floor-dressing pass picks) — not as ordinary BiomeDef wildPlants.
2. Author the two salt-rimed-blade-flora variants (Grey/Twilight), likely
   the same floor-dressing shape, confirmed distinct defs per the roster's
   own "endemism" note (do not share one def between the two seas).
3. Condensate-drinker (Twilight, fog-lick fauna) needs an **owner ruling**
   before building at all — it would be a 5th species added to a roster the
   owner already closed at exactly 4 (`terminal_seas_cast_proposal_2026-09-25.md`
   verdict 1). Do not add it to `RM_TwilightSeaFauna.xml`/wildAnimals
   without that ruling; per this project's own standing practice
   (`BIOME_SPECIFIC_FAUNA_LAW_1`'s eviction-freeze precedent), an
   owner-approved cast is not casually extended mid-flight.

## watch out

- Re-verify currency before building: `SEA_DIVE_MAPS_BUILD_1` is very
  recent (closed same day this item was filed) and its floor-dressing
  follow-on may already be filed or claimed by the time this is picked up —
  check `infrastructure/state/items/` for anything naming "floor dressing"/
  "sea floor"/"pillar-mason"/"mat-roof" first.
- Do not build these as ordinary wildPlants entries — both sea BiomeDefs
  have `hasVirtualPlants=false` and no `<wildPlants>` block; that shape is
  wrong for this content, confirmed by direct read 2026-09-26.

## verify

Each of the 5 slugs resolves to: built (in whatever shape the floor-dressing
system ends up using), queued, dropped, or superseded — with the condensate
drinker specifically requiring a recorded owner ruling before "built" is a
valid outcome for it.

## criteria

All 5 slugs resolved per-slug, matching `COMMISSION_LEDGER_CLEANUP_1`'s own
closing bar.
