# BIOME_PAINT_ONCE_AT_THE_END_1 — the worldmap gets painted once, after every biome is a mod

## the ruling

Owner, 2026-09-20, verbatim:

> *"Don't worry about worldmap painting. Once we have all the biomes in mods we will do
> the painting once and for all."*

Given in the same sitting as, and governing, the tier ruling recorded in
`design/RimMandrake/biome_mod_architecture.md`:

> *"please make sure that each of our actively converted biomes is its own mod at the
> RimMandrake level. Lanterndeep, two deserts, pyrelands, the rot, etc. only Star Wars
> creatures become patches applies from the utinni scenario layer."*

## what it decides

1. **Painting is a SINGLE TERMINAL STEP.** Build every biome mod first; paint the planet
   once, at the end. ⛔ No per-biome repaint, ever.
2. 🔑 **No biome's work is gated on its tile count.** A biome mod being "on zero tiles"
   is the expected mid-migration state, not a defect and not a reason to defer anything.
3. ⛔ **Stop citing tile counts as evidence of what is built.** They answer a question
   nobody is asking until the painting pass.

## why this ruling was needed — the trap it closes

`world/ASHKARR_WORLDMAP_tiles.csv` is a **record exported from the savegame**, not the
planet. Its own freeze stamp (`ASHKARR_WORLDMAP_tiles.csv.frozen.json`, 2026-09-07,
owner ruling) says so outright:

> *"This CSV is now EXPORTED FROM THE SAVEGAME … It is a RECORD of the planet, not a
> rival to it. To change the world, change the WORLD and re-export — never edit this
> file and import it back."*

and, from the same stamp, the lesson that had already been paid for once:

> *"Any future live-vs-CSV validate must state which direction it is evidence for."*

🔴 **It was last exported 2026-09-12, and BENCH read it on 2026-09-20 as the state of the
planet.** That produced `PYRELANDS_WRONG_BIOME_DEF_1` — filed on the reading
`ZBiome_Grasslands` 222 tiles / `RM_FE_Pyrelands` 0 — while a committed comment from a
**live** read on 2026-09-19 asserts the exact reverse. Both cannot describe one moment,
and the live world decides. The item's premise was therefore never established.

⇒ Under this ruling the question is moot rather than merely unresolved, which is the
better outcome: nothing downstream should have depended on it.

## what is still true and still owed

- The **offline** half of `PYRELANDS_WRONG_BIOME_DEF_1` was real and landed at `e07eca2d0`:
  the ash storm was being added to a *More Vanilla Biomes* donor def instead of to
  `RM_FE_Pyrelands`, and three files carried false prose about which def the world
  carries. That was a content-wiring defect, independent of any tile count.
- Duplicate defs in **our own source** remain a real defect and are not a world question:
  `RM_Greentide` (123 lines) beside `RUT_Greentide` (287 lines, sheet-derived), and
  `RM_GelatinousSlime` beside `RUT_Slime`. Resolution belongs to the architecture spec.

## verify

Every biome named in `design/RimMandrake/biome_mod_architecture.md` ships as its own
RimMandrake mod with its own BiomeDef and Mod Settings, before any painting is attempted.

## criteria

The planet is painted exactly once, from a settled set of biome mods — and no item in the
queue is blocked on a tile count before then.

## parked items

An item this list parks carries a `parked: <ID>` line at the start of a line in its addition below. Relentless reads
those lines (`relentless_rules.json` `pool_parked_lists`, `relentless.parked_ids`) and never staffs the item, nor this
one, until this item closes. Add the line with the addition.

## Paint list addition 2026-10-09 (decision taken by question card)

`WARSCAR_PILGRIM_CAMP_SITES_1` (pilgrim camp SitePartDefs at authored tiles along the Ashfall Road) is done at the final world painting, not before.

parked: WARSCAR_PILGRIM_CAMP_SITES_1

## Paint list addition 2026-10-20 (from `WORLD_PHYSICS_AUDIT_LOCKED_SUN_TEMPS_RINGS`)

The Scald (`RM_TheScald`): its 312 tiles are at arc 23–51 (median 36), where the owner placed it, and stay there
(owner, by card 2026-10-22). They are 7.8 °C under the ruled curve on every tile (perched-1,411 m values never
re-derived after the −30 m ruling; `design/RimMandrake/world_physics_audit_2026-10-20.md` §3). Stamp
`world/repaint_2026-10-21/scald_temperature.csv` (`tile,temp_c`) at the final painting.

## Paint list addition 2026-11-02 — Long Shade and Wasteland mutator density (`BIOME_ENRICHMENT_DESERT_WASTELAND_1`)

Apply `world/ASHKARR_DESERT_WASTELAND_ENRICHMENT_plan.json` at the final painting: 735 bare Long Shade tiles and 626
bare Wasteland tiles each gain one existing mutator (Caves, Junkyard, AncientRuins, MineralRich, Stockpile), taking
both from ~61–64 % mutator-free to 30 %; the bare tiles left are the ones farthest from any road (the sheets' wide
gaps). Owner ruling 2026-09-20, option (b). The dune sea gets nothing. The plan is built from the save named in
its `inputs` (sha256 recorded); if the save being painted is a different file, point the generator's `SAVE` at it and
rebuild (tiles that are no longer that biome, or no longer bare, drop out) before applying. The apply recipe
is the plan's `apply` field. Its proof is `src/RimMandrake/Utils/selftest_desert_wasteland_enrichment_plan.py`.

## Paint list addition 2026-11-02 (from `PLAYER_START_SITE_1`)

The player start tile, `canon.yml` `planet.start_tile` (17007, Zeddo's Yard), carries the tile mutator
`planet.start_tile_mutator` (`RUT_ZeddosYard`): stamp it on that tile at the final painting, before the start
landing is flown and the start savegame is cut, so the arrival map generates the junkyard around the landing clearing.

## Paint list addition 2026-11-02 — the §8 structure archetypes (`INHABITED_AUGMENTATION_BUILD_1` criterion 3)

Putting a structure on an Ash'karr tile means adding its `TileMutatorDef` to that tile: the same kind of planet write
as the Wasteland mutator density above. So it happens here, once, at the final painting, and never as its own
pass on the canonical save before that. Every responder below exists in `src/` and replays a rimplace plan through
its `GenStepDef` (`design/Jawa/worldbuilding/structure_procedural_spec.md` §8). The painter picks the tiles using the
siting rule in each row, which comes from the archetype's own spec paragraph. The pass is done when each row has at
least one tile and the tile list is exported as `world/ASHKARR_STRUCTURE_ARCHETYPES_plan.json`
(`tile,mutator`). The proof that this list covers every responder is
`src/RimMandrake/Utils/selftest_inhabited_augmentation_paint_list.py`.

| § | archetype | TileMutatorDef(s) | siting |
|---|---|---|---|
| 8.1 | abode / homestead / compound | `RUT_HomesteadAbode`, `RUT_Homestead`, `RUT_HomesteadCompound` | settled desert tiles on or near a road; the compound only where several households make sense |
| 8.2 | moisture farm | `RSW_MoistureFarm`, `RUT_MoistureFarmRuined`, `RUT_MoistureHomestead`, `RUT_MoistureVaporatorField`, `RUT_MoistureWalledCompound` | open Badlands/desert flats (catalogue B1) |
| 8.3 | mining site | `RSW_MiningSite` | against a rock mass; it answers the `AncientQuarry` landmark (catalogue E1) |
| 8.4 | trading outpost | `RSW_TradingPost` | a road tile (catalogue D2, civilian half) |
| 8.5 | road warehouse | `RSW_RoadWarehouse` | a road tile; it answers the `AncientWarehouse` landmark (catalogue E2) |
| 8.6 | tiny garrison | `RSW_GarrisonTiny` | a road chokepoint or border tile (catalogue D2/D3/E3) |
| 8.7 | tar refinery | `RSW_TarRefinery` | a tar-seep tile (catalogue A7/F3) |
| 8.8 | gas-geyser station | `RSW_GasStation` | a gas-geyser tile (catalogue A4/A5) |
| 8.9 | crashed ship | `RSW_CrashedShip` | open ground away from settlements (catalogue C2) |
| 8.10 | dead caravan | `RSW_DeadCaravan` | a road tile in empty country (catalogue C1) |
| 8.11 | beast lair | `RSW_BeastLair` | wild, settlement-free tiles, rock-edged where possible (catalogue F1/F2) |
| 8.12 | battle site | none; it is the `state=ruined` read of another archetype | painted as a ruined host row above, at the painter's choice |
| 8.13 | beast pens | `RSW_BeastPens` | Hutt or homestead country near a road |
| 8.14 | storage cache | none yet; it is whisper-shaped and waits on the whisper engine | not painted until a responder exists |

## Paint list addition 2026-11-03 — the Fall Line mutator (`FALL_LINE_MUTATOR_PLACEMENT_1`)

At the final painting, stamp the tile mutator `RUT_FallLine` on every tile in `world/ASHKARR_FALL_LINE_MUTATOR_plan.json`.
That is 308 tiles: the world features "Fall Line" (155) and "The Breaks" (153; the 2026-08-24 CSV calls it "Fall Line
Barrens"). Start tile 17007 is one of them. The list is rebuilt from the canonical save (sha256 in `inputs`) by
`src/RimMandrake/Utils/fall_line_mutator_plan.py`. If the save being painted is a different file, point its `SAVE` at
that file and `--write` again before applying. The apply recipe is the plan's `apply` field. Until the painting,
`FallLineGate` falls back to the tile's feature name. Both names are in its `FeatureNames`, so the gate already holds
on these 308 tiles (proof: `src/RimMandrake/Utils/selftest_fall_line_mutator_plan.py`).
