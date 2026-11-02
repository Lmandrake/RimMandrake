# 16 — Hand-placed geological landmarks, planned for the paint (2026-11-01)

Item `GEO_LANDMARKS_SKETCH_BEFORE_THE_PAINT_DRIES`, the before-paint gate of `BIOME_PAINT_ONCE_AT_THE_END_1`.
Origin: idea 7 and card 4 of `12_rocks_design.md`; the owner chose by card on 2026-10-19 to plan them for the paint
(`13_owner_rulings_2026-10-19.md` row 16). This file is the plan: **the list, the locations and the stones.** The
build is a separate item, `GEOSTONE_BUILD_SIX_LABELS_AWAIT_STAMP`.

**Data of record** (committed; this prose only explains it):
- `design/RimMandrake/world_remake_2026-10-19/geo_landmarks.csv`: one row per landmark.
- `design/RimMandrake/world_remake_2026-10-19/geo_landmarks_tiles.csv`: the **frozen** tile list, 120 rows.
- Checker: `python3 src/RimMandrake/Utils/remake/geo_landmarks.py check --save <dev start save> --dump <capture>/defs`
  (and `selftest`).

## Rules this plan keeps

- **Hand-authored, one planet.** Each centre was picked by hand on the dev planet
  (`ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws`). The tile list was written once: the centre plus 2 or 3 rings
  of neighbours, minus the excluded biomes below. It is then frozen: `author` refuses to overwrite it, and nothing
  re-derives it at runtime. No generator, no variants, no rule placing landmarks in game (CLAUDE.md worldgen rulings).
- **Tile ids are where they live.** The repaint re-stamps biomes onto the same 21,872 tiles, so the ids survive
  it (`big_repaint_plan_2026-10-21.md` §3). The biomes in the table are the dev planet's today, as context.
  ⛔ They are not a target. A biome's tile count is never evidence of anything.
- **Never in a sea or in the Rust Cathedral.** The excluded biomes are `RM_TheScald`, `RM_TwilightSea`,
  `RM_GreySea` and `RM_RustCathedral`. The first three are water. The cathedral forces its own stones
  (`forceRockTypes`), so a landmark there would replace them.
- **Geology crosses biome lines.** That is the point of idea 7. Five of the six landmarks span four or five
  biomes. The sixth, the Coldstone Shield, is a single upland.
- **Stones come in two columns.** `stones_now` takes only defs that exist; the checker resolves each against `src/`
  and the def db. `stones_planned` may name a stone that does not exist yet, but only with the live item that owes
  it. Every landmark keeps at least one plain (non-resource) natural rock, because
  `src/RimMandrake/Stillsand/Source/RM_PreciousCaves.cs:846` picks one from the list.
- **Metal is not stone.** Any metal a landmark suggests, such as meteoric iron or the deck plate's Steel, is a row
  in the mineral matrix (`MINERAL_MATRIX_DESIGN_ROUND_TWO_SPARSER`), not something decided here.

## The six

Location = centre tile (lat, long) and arc from the substellar point. Arc 0 is the noon point, 90 the terminator,
180 the antistellar point. Region = the world label the patch sits in.

| id | name | what it is | centre · arc · region | tiles | biomes it crosses (dev planet) | stones now | stones planned |
|---|---|---|---|---|---|---|---|
| `RM_Geo_BlackStair` | The Black Stair | basalt province: flood basalt stepping down off the Forge | 3653 (−13.3, −25.7) · 29° · Dune Sea | 27 | TheForge 13, Contagion 6, FloodedCanyon 5, Greentide 3 | Slate, Granite | `RM_Basalt` (owed: `BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND`), Slate |
| `RM_Geo_SaltKnolls` | The Salt Knolls | salt dome field: limestone caprock over salt plugs | 9802 (−13.2, 95.3) · 95° · Salt | 19 | Wastes 6, Abyss 5, LeaningScrub 4, FloodedCanyon 4 | Limestone | Limestone, `RM_SaltRock` (proposed, owed: same item) |
| `RM_Geo_StarfallRim` | Starfall Rim | meteorite strewn field on the rim of the Scald crater | 770 (7.6, −47.7) · 48° · Cratercrown | 19 | Webwork 6, WeepingStones 5, Contagion 5, Greentide 3 | Granite, Marble | same |
| `RM_Geo_Hullbed` | The Hullbed | exposed wreck stratum: the cathedral's buried deck plate surfacing outside it | 19418 (10.2, −10.2) · 14° · Anvil/Scorch | 17 | Warscar 4, Webwork 4, Greentide 3, WeepingStones 3, Pyrelands 3 | `RM_CathedralDeckPlate`, Sandstone | same |
| `RM_Geo_ChalkStep` | The Chalk Step | exposed stratum: one chalk bed cut across the twilight | 20193 (−75.9, −39.8) · 79° · Chalk Marches | 19 | Cauldron 6, Wastes 5, LongShade 5, GelatinousSlime 3 | Limestone (a one-stone map on purpose) | same |
| `RM_Geo_ColdstoneShield` | The Coldstone Shield | night-side granite upland with ice in its joints | 13720 (−62.6, −129.5) · 107° · Coldstone | 19 | Abyss 18, Wastes 1 | Granite, `SolidIce` | same |

"Wastes" stands for the 1,853 tiles whose biome hash the current dump cannot decode (`?18404`). That hash matches
the old `RM_Wasteland` (StableStringHash mod 65535 is 18403, plus the usual +1 collision step; INFERRED), and
`RM_Wasteland` is renamed `RM_Wastes` in `src/`. The repaint moves those tiles to the new name. The landmark tiles
do not move.

Why these six. They are the four named in card 4 (basalt province, salt dome field, meteorite field, exposed
wreck layer), plus one exposed stratum and one night-side landmark, so that both ends of the sun axis get one.
They sit at arcs 14° to 107°. Where the world already has a label that fits, the landmark sits inside it:
Cratercrown is the rim of the Scald crater lake (`the_one_map.md`, "THE SCALD IS A PERCHED LAKE"), and the other
fits are Salt, Chalk Marches and Coldstone.
None of the six names is canon IP: all are invented, so they belong to the `RM_` tier (CLAUDE.md, the Q11a ruling).

## How it will work (the build item owns this; recorded so the paint can stamp it)

1. **Decompiled 1.6 has no stone field on `TileMutatorDef` or `LandmarkDef`.** Measured on the def dump: neither
   def type's field list names a rock. So each landmark becomes:
   - a `TileMutatorDef` `RM_Geo_<Name>`, carrying a `DefModExtension` that lists its stones;
   - a Harmony postfix on `World.NaturalRockTypesIn(tile)` (`12_rocks_design.md` §0). If the tile carries an
     `RM_Geo_*` mutator and the landmark's setting is on, the postfix returns that mutator's stones in place of
     the biome's.
   Give each mutator a category of its own. `Tile.AddMutator` resolves category conflicts, so a shared category
   would let a later mutator remove ours.
2. **One named `LandmarkDef` per landmark, on its label tile.** The label tile is the centre. The checker confirms
   every centre is free of other landmarks and of settlements, because `LandmarkDef.IsValidTile` rejects both
   (`jawa/world_landmarks_set` description). The landmark gives the name and the icon players travel to. Its
   `mutatorChances` holds only its own `RM_Geo_*` mutator, marked required. `AddLandmark` rolls every chance
   in that list onto the tile, so any other entry would put random extras on the one planet.
3. **Mod Settings:** one on/off per landmark, on by default. Off means the tile keeps its biome's stones.
4. **It touches only maps generated afterwards.** The stone list is computed fresh each time and never saved, so
   maps that already exist keep their stone.
5. **Stamping, in the paint's game-up phase** (after `big_repaint_plan_2026-10-21.md` §3 step 6, before the save in
   step 8):
   - `jawa/world_mutators_set` adds `RM_Geo_<Name>` to every tile in `geo_landmarks_tiles.csv`;
   - `jawa/world_landmarks_set` places the landmark on the label tile;
   - `jawa/world_commit`;
   - read the result back with `jawa/world_mutators_get` (120 tiles) and `jawa/world_landmarks_get` (6 labels).
   The stones need no world edit; the postfix supplies them.

## What is owed, and by whom

- `GEOSTONE_BUILD_SIX_LABELS_AWAIT_STAMP`: build the defs, the extension, the postfix and the settings. Then stamp
  them as in step 5 and prove one generated map per landmark shows the planned walls.
- `BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND`: `RM_Basalt` (owner-wanted) and, if ruled, `RM_SaltRock`. Until they
  exist, the Black Stair runs on Slate and Granite and the Salt Knolls on Limestone alone.
- `MINERAL_MATRIX_DESIGN_ROUND_TWO_SPARSER`: any metal at Starfall Rim or the Hullbed.
