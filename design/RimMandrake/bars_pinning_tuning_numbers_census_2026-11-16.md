# Bars that pin a tuning number or an asset count — census, 2026-11-16

Item `RIMMANDRAKE_TEACH_JUDGES_BARS_HOLD_NO_TUNING_NUMBERS`. The ruling: `standing_rulings.md` §A passing bar is an
experience (owner 2026-11-16: *"The mod passing bars should not specify flora and fauna yield rates! That would mean
every time we renormalize every mod must repass its bars... drop that!"*). The test applied to every row: would this bar
have to be re-passed after we renormalize numbers or add an art variant?

**No bar was edited.** A north-star bar is his to change; the concept-tree leaves are listed so the Conductor can bring
them to him and the Designer can reword them at each mod's next sitting. Contagion is being re-scoped by another builder
right now; its rows are as of this census.

## How it was found

`bar_rule.detect` plus a number-and-unit pattern over every leaf (`experience`, `oracle`, `oracle_proposed`, `scenario`,
`red`) of the 16 concept trees in `design/concepts/*/tree.json` (89 hits), and over the 411 checkbox bars of the 94
`## north star` sections in `design/validation_walks/` (6 hits); every hit read by hand. Not scanned: `scenes.json`
expects (scene parameters, not bars) and the `_drafts` walks. A bar that pins a number in words this pattern does not
know ("a handful", "most") could be missed.

## North-star bars (his)

| mod | bar | pins | proposed wording as an experience |
|---|---|---|---|
| Graffiti | `mark_ugliness_is_visible` (`design/validation_walks/RimMandrake/Graffiti.md`) | Beauty −15 scrawl vs Beauty −3 tally | A vandal scrawl looks clearly uglier at a glance than a tally mark, and the game's own beauty reading agrees on which is uglier. |

Read and kept off the list: WreckedMachines `wreck_occupies_its_tiles` (a 3×4 footprint is the building's shape, which
no renormalization changes); FlowWorks `fill_tier_legible` and `depth_and_fill_jointly_legible` (depth stated in metres
is his depth ruling, a geometry, not a tuning number); Oracle `persona_block_carries_the_cast_law` (a rule number, R-W6);
WreckedMachines `tiers_distinguishable_at_glance` (the 4×5 is a measurement note, not the bar).

## Concept-tree leaves (the Designer's bars)

"His number" marks a number he set by card: rewording it is his call even though the leaf is not a north-star bar.

| mod | leaf | pins | proposed wording as an experience |
|---|---|---|---|
| Contagion | `fauna_specials_declared` | a declared-field table per native (fast, docile, MeatAmount, leather) | Each native shows the special its description promises in play: acid or slime deaths, the leaker's leak, the armoured natives walking through the Burn. |
| Contagion | `zhooliza_lives_here` | "both of its whole-body variants" spawn | The Zhool'Iza spawns from the roster and reads as its own creature beside the Zhool. |
| Contagion | `genome_brings_tissue` | a batch of 2 to 4 donor-labelled parts | When the wanted part misses, the player still gets matched or sellable tissue, never nothing. |
| ExplosiveKnockback | `people_thrown_three_cells` (and the `doors_and_deep_water_stop` control, "3 cells out") | a throw of about three cells | A colonist one cell from a shell is thrown clear over a sandbag line and lands alive and briefly stunned. |
| ExplosiveKnockback | `the_spared`, `heavier_flies_less` | 150 kg creature mass limit | A pawn heavier than the configured creature mass limit is not moved; lighter ones fly farther the lighter they are. |
| ExplosiveKnockback | `every_good_moves` | 75 kg goods mass limit | Every loose good under the goods mass limit that the blast reaches moves; none sits still while its neighbours fly. |
| ExplosiveKnockback | `closed_container_holds` | 250 kg container limit | Goods inside a closed container stay put unless the container itself is light enough to be thrown. |
| ExplosiveKnockback | `goods_arc_spin_rebound` | about 70% of speed kept per rebound | Thrown goods arc, spin, rebound visibly off walls and doors, losing speed each bounce, then come to rest. |
| ExplosiveKnockback | `heavy_stack_knocks` | blunt damage 2 to 5 | A heavy stack that hits a pawn gives a small blunt hit and a stagger, never a serious wound, while light goods fly past harmlessly. |
| ExplosiveKnockback | `gas_goes_clump_by_clump` | a one-cell shove, at most once every 2 seconds | A burning gas cloud goes off clump by clump, shoving a nearby pawn a short way without hurting them, not on every burst. |
| LeaningScrub | `smother_claim` | default 120 days, range 120–600 | One blanket buys one long, fixed countdown the player can read, and finishing the job never charges twice. |
| LeaningScrub | `cane_fuel` | two wood-equivalents per cane; 1.25× heat rate | A cane burns longer and gives more heat than the same count of wood. |
| Pyrelands | `ash_fertile_when_watered` | about 70% dry, about 140% watered (his number) | Deep ash is sowable dry, and a strip beside a watered channel grows clearly faster than the same crop on dry ash. |
| Pyrelands | `fresh_burn_compounds_with_black_rain` | about 190% / 120% / 140% | A wet fresh scar out-grows a dry fresh scar and wet old ash while the black rain lasts. |
| Pyrelands | `grass_carpets_and_regreens` | green share ≥25% on day 3, ≥60% on day 7 (his number) | Burnt open ground is green again within about a week; roofed grass withers soon. |
| Pyrelands | `sand_shovel_yields_glass_sand` | 5 glass sand per cell | Shovelling a sand cell gives glass sand once and turns it to gravel, so a patch is a finite deposit. |
| Pyrelands | `firehawk_hunt_rewards` | crestfeather drop rate 35% within 4 sigma | Butchering a fire-hawk sometimes gives a Pristine Crestfeather worth more than the hawk; butchering anything else never does. |
| Pyrelands | `furnacebeast_warms` | body size 9 (≥2× any other); room ≥5 °C above its twin, ≤21 °C | The furnace-beast is far larger than any other animal on the map, and a hide bank keeps a closed room clearly warmer with no fuel or power. |
| Pyrelands | `scorchfruit_born_of_fire` | a ripe plant withers within about a day; fruit rots within about four days | Scorch-fruit rots fast: an unpicked plant is soon gone and picked fruit spoils unless refrigerated. |
| Graffiti | `ugliness_visible` (the tree twin of the north-star bar above) | Beauty −15 vs −3 | As the north-star rewording. |
| Graffiti | `marks_various` | at least 3 distinct defs and 5 def-variant pairs (an asset count) | In one colony the player sees several visibly different kinds of mark, not recolours of one. |
| Graffiti | `rereads_daily` | at most once per 60000 ticks | A colonist who keeps passing the same mark is not hit by it again on every pass, and changes opinion once. |
| FlowWorks | `hose_reads_as_hose` | "four styles told apart" (an asset count) | The hose styles are told apart from each other, and a hose never reads as a power cord. |
| Cauldron | `falter_warning` | cue-to-bloom about 2500 ticks (the leaf calls it a "ruled approximate" target; whose ruling is unmeasured) | The cues come early enough that a worker who reads them reaches shelter before the bloom. |

Read and kept off the list, with why: ExplosiveKnockback `per_weapon_tuning` (its numbers are inputs to a settings
precedence check, not a tuning target); ExplosiveKnockback `walk_storeroom_raid` (a frame-time bar of 10% against the
mod-off arm, his card 2026-11-16: performance, not tuning); LeaningScrub `wind_plain` (0.1° is a measurement tolerance);
Contagion `biome_def_declared` (a nonzero animal density is a correctness rule, `CLAUDE.md`, not a tuning value);
Contagion `airborne_stats` (MaxFlightTime above zero is the flight rule); Graffiti `temperament` (compares to the def's
own values, so a renormalization moves the test with it: that is the right shape).

## Count

25 rows across 7 mods: 1 north-star bar (Graffiti) and 24 concept-tree rows covering 26 leaves (Contagion 3,
ExplosiveKnockback 7 rows / 9 leaves, LeaningScrub 2, Pyrelands 7, Graffiti 3, FlowWorks 1, Cauldron 1). Two carry a
number he set by card (Pyrelands ash fertility, Pyrelands grass thresholds).
