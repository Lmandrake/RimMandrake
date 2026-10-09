# DUNG_HATCH_WILDLIFE_CAP_1 — CB-4: dung-hatched young respect the map wildlife limit

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row CB-4 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| CB-4 | Young animals that hatch from dung respect the map's wildlife limit, the same as vanilla's spawner, so a shade whale's dung trail cannot fill the map. | Gate SeedYoungCreature on `map.wildAnimalSpawner.AnimalEcosystemFull`. | S | low | CreatureBehaviors (consumer: shade whale, DESERT_SHADE_WHALE_FILTERFEED_1) | `RM_CompDungSeeder.cs:230-257`: chance roll only, no population ceiling; same gate already used in `BlueDesert/Source/RM_MurrekDrift.cs:409` |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.
