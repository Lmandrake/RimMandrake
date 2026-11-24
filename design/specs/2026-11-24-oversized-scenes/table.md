# Oversized scenes: the three questions, scene by scene

Item `RIMMANDRAKE_SHRINK_OVERSIZED_SCENES_IN_EVERY_MOD_AFTER_PYRE`. Pyrelands is the other item. The owner's page is `one_page.md`.

How the numbers were read [measured]: "runs / not passed" counts the lines of `version/in_game/visit_*/rows.jsonl` for the
test, every mod-side and test-side cause together. A re-classed row is a line of its own, so the counts are high by the
re-classed rows. Seconds are the `wall_s` (or `seconds`) the rows carry; Explosive Knockback's walk rows carry none (UNMEASURED).
A held mod has no visit, so a held scene has 0 runs.

A scene is oversized by the brief's rule. One line of judgment was added. Several readings from one short staging (under a
day, small list, everything held still) stay together when splitting them would only repeat the staging. Those scenes are in
section 5. A bundle of claims that came back not passed for reasons outside the mod is split, whatever its length.

## 1. In-game mods (design only: a live run holds each mod)

| mod, scene | runs / not passed | why oversized | what is tested, and its bar | should a script test it | the minimum test |
|---|---|---|---|---|---|
| FlowWorks `sc_walk` | 11 / 3, 1,384 s | full list; about 8 claims in one scene; a season in the bar | (a) a save and reload keeps pond, moat and swimmer; (b) off and on leaves the water alone; (c) fuel first, then water, works (`walk_moat_season`) | yes, as three scenes; a season of play is his walk | kind A, FlowWorks tier list, calm profile. `sc_walk_reload`: dig, fill, swimmer, save, 60 ticks, load, digest equal; control: the pre-fill save differs. `sc_walk_switch`: off, dig, 600 ticks, nothing moves; on, it moves. `sc_walk_second_order`: fuel pit, then a pond drained. Each reads the log for FlowWorks lines. No row reads another mod, so the full list adds nothing |
| FlowWorks `sc_source_pays` | 13 / 10, 1,519 s | about 8 claims; two mod lists; up to 8,000 pulses and 14,000 ticks | (a) a draw lowers litres and shore; (b) an empty pond stops paying; (c) rain refills; (d) an edge body is Endless (`source_pays_and_refills`, `no_full_source_after_draw`) | (b) is arithmetic: offline | `sc_source_draws` (one draw, the tap-0 control). `sc_source_refills` (rain set, two reads 1,000 ticks apart). `sc_lake_endless` inside the river scene, which already stands on the river site. The last-drop follow goes to `T_STOCK` and `PY_PUMP_DRAW_CONSERVES` [guess ~60%: the builder shows the planted endless-pond fault red there first, or keeps the row] |
| FlowWorks `sc_garden` | 15 / 9, 1,941 s | a game day; seven machines in one staging; a fed colony | seven machine rates; it decides no bar, it only supports | no: `T_CONVERT`, `T_DRILL`, `T_THIRST`, `T_NET`, `T_SHEET` decide the bars it supports | two small supports: pump beside no-pump sprinkler, one pulse (2,500 ticks); faucet drink, one colonist, 2,500 ticks. Converter and still rates: the kernel tests. The run that builds this first proves the three planted faults (CALLER_CONV_DROPS_CLIPPED, CALLER_SPR_SPRAYS_WITHOUT_PUMP, DEF_STILL_RATE_TENFOLD) red offline, or keeps the live row that reds them |
| FlowWorks `sc_hung_bridge` | 27 / 10, 4,438 s | nine sections in one command; the costliest scene of any mod | the bar is two paths, over and under (`hung_bridge_spans`, `inv_bridges`) | yes, its first section | `--only posts` (the option exists). Crush, shots, grate, burns, jetty, islands and reach: each keeps its section, run only when a change touches it |
| FlowWorks `sc_hole_prison` | 14 / 2, 2,204 s | a full game day of real needs | captured with no bed, held, fed (`drained_hole_is_a_prison`) | yes | capture, one meal delivered and eaten, no escape route read, 5,000 ticks. A day adds only other ways to spoil it |
| FlowWorks `sc_pawn_height` | 11 / 5, 3,113 s | 46 orders, one cell each | height follows depth both ways; swims at 2 m (`pawn_height_follows_depth`) | yes | one order over five depths and back, the offset read every tick; one swim |
| FlowWorks `OL_OWNER_LOOK_READS` | 9 / 8, 419 s | many reads; an evening list | what is drawn over what; it decides no bar | no: `T_UNDERLIQUID` decides | the reads whose list is the tier list, as supports; the rest is his look |
| FlowWorks `sc_moat_raid`, `sc_trench_cover`, `sc_pit_trap_raid`, `sc_fetch_fallen`, `sc_islands` | 67 / 32 | raids | raiders at the moat | moved out of 0.1.0 on 2026-11-23; raid tests are paused | done: `sc_moat_walkers`, `sc_trench_cover_pawns`, `sc_islands_walker` |
| Explosive Knockback `sc_walk_blasts` (was `sc_walk_raid`) | 14 / 12 | 18 rows: two orders, a save, gas, cover, frames | 17 of 18 rows look decided by other scenes [guess ~80%; the builder checks each row's bar first]; the new one is a save with a thing in the air (`walk_storeroom_raid`) | the save only | kind A, tier list, quicktest: `sc_save_in_air`. One shell, save at 2 ticks, load, each thing counted once. Frames stay with `sc_barrage_perf`; his card on the walk's frame row (2026-11-16) is named in the ticket, because a bar's clause would leave the script |
| Explosive Knockback `sc_storeroom_bomb_pit` | 14 / 11, 90 s | eight claims in one blast; it decides no bar | the flagship picture | no: each of the eight has its own scene | his walk keeps the staging; the scene leaves Stage 6 |
| Explosive Knockback `sc_pit_fetch` | 12 / 6, 926 s | a hauler at large for up to a day | a haul out of a pit by the ladder (`pit_goods_fetched`) | yes | needs held, the haul ordered twice (stack, corpse), path cells read, 5,000 ticks |
| Gimme Some Slack `sc_walk` | 3 / 1 | the text says a week on the full list | save and reload keep the cords true; the switch off and on (`walk_scavenger_base`) | yes; but the code runs no week: its verdict is already read from the proof's save rows on the small list [measured, read] | `sc_save_reload_wire_down`: the rows `P_S7`, `P_SL1` to `P_SL3`, with a wire down, on the 12-mod list. The table's `live_full` and the week in the text go; a week of play is his walk |
| Gimme Some Slack `sc_tap_theft` | in the proof | the text reads goodwill daily for two days | a tap costs goodwill (`tap_steals_and_costs_goodwill`) | yes | one daily tick of the goodwill code called once with the tap seen, once with it removed |
| Gimme Some Slack `sc_gravship` | 2 flights a visit | a new ship and an 83 s boarding wait per flight | the link survives, or not, by the switch | yes | one boarded save, two flights (`design/specs/2026-11-23-costly-test-acts/`); the Codex run edits it now |

## 2. Held mods, not locked: scenes rewritten now (text only, all UNRUN)

| mod | scene | why oversized | what replaces it |
|---|---|---|---|
| Contagion | `sc_walk_red_lid` | two weeks, full list, three stories | one save and load mid-tells; new `sc_gestation_burn_order` from one checkpoint |
| | `sc_genome_brings_tissue` | four days, about ten claims | one birth with its deadline set ahead; new `sc_genome_matched_install`, `sc_genome_refusals`, `sc_genome_birth_no_burst` |
| | `sc_cast_lives_here` | a day, then 30 days | the biome's spawner called per row; new `sc_wreck_fragments_age` |
| | `sc_wombpod_hatch`, `sc_zhooliza` | three days; a day | the sac's tick set ahead; the spawner called |
| | `sc_sunbeam_arrest_treats`, `sc_touched_reads_early` | a day outdoors, five claims each | 250 to 2,500 ticks from one step below the threshold; new `sc_sunbeam_orders`, `sc_touched_who_and_how_fast` |
| | `sc_burn_dash` | five bars in one scene | a showcase for his look; each bar keeps its own scene |
| PyrelandsMechanics | `sc_walk_tribes_season` | a season, full list, waits for a chance | a forced rite saved and reloaded; new `sc_rite_second_order`, `sc_rite_switch_off_cleans`, `sc_rite_own_roll` (offline) |
| | `sc_fruit_defence` | two runs and three days | the warning only; new `sc_fruit_fightback` reads the queue at once |
| | `sc_attack_raids`, `sc_no_arson_tally` | days, and a raid that vanilla sends | the relation read within 250 ticks; three fires read when out |
| Cauldron | `resume_walk`, `routine_day` | two orders, a purge and a reload; forty colonists | one save and load; new `resume_walk_second_order`; three workers and one bloom |
| FeverWood | `ordinary_reload_walk` | seven obligations and two orders | one seizure; new `reload_owed_obligations`, `return_before_or_after_shore` |
| | `normal_suppression`, `young_establishment` | several days; a campaign salvage journey in both | one job, one deadline set ahead; new `suppression_refusals`, `campaign_reagent_lane`, `young_poison_choice` |
| | `two_front_journey`, `branch_work` | two raiding factions; forty colonists | the schedule offline and one held pawn; two workers |
| GelatinousSlime | `walk_reload_repeat` | forty colonists, two orders | one patient; new `repeat_with_fresh_dose`, `production_and_expedition_order` |
| Stillsand | `walk_accept`, `workshop_jobs` | the whole expedition; forty colonists | one save and load; new `emptied_cave_stays_empty`, `workshop_before_or_after_cave`, `workshop_bill_interrupted` |

Each new scene carries `cheaper_why`, and `shrunk` or `split_from`. The six mods' walk leaves in `tree.json` say what the script
does and what his walk does. 22 scenes were rewritten and 22 were added [measured]. `lost:` a scripted run of several systems at once,
and how often a rite, a reagent or a herd comes by itself; his walk keeps both. `undo:` revert the commit of this item.

The rest of these designs is in section 5.

## 3. Held and locked mods: the design, for the day the hold lifts

Their scenes are pinned bytes of a locked version, and their scene code is a build. So the text waits with the code.

| mod, scene | why | what is tested | minimum |
|---|---|---|---|
| Graffiti `sc_lived_in_soak` | three weeks, full list, a colony at large | (a) a negative mood returns to zero between stories; (b) messages are few (`stories_not_tax`) | (b) offline: the message counter's own rate limit (`T_MSG_COUNTERS_RESET`). (a) `sc_mood_returns_to_zero`: six spawned viewers, each temperament, one mark of each kind read once, thought ages set past their ends, the sum read as zero; control: hourly marks do not reach zero. A colony over weeks is his walk |
| Graffiti `sc_walk` | full list; a raid and a trader in two orders | marks and the pressure record survive a reload; a visit costs goodwill once | `sc_marks_survive_reload` (no raid: the record written by the mod's own call), `sc_visit_orders` (the two visit hooks called in both orders from one checkpoint) |
| Graffiti `sc_raider_pressure` | six raids | letter, size or delay by the setting | the points and delay function called with marks and without; the letter read; no raid sent |
| Graffiti `sc_breach_bias_raid` | a breaching raid | the wall the breach picks | `FindBuildingToBreach` read with the bias on and off; no raid sent |
| Graffiti `sc_raid_exit` | raiders under an assault lord | tags on the way out | one held pawn of the faction given the leaving toil. It is paused today; this needs no raid |
| Graffiti `sc_rereads`, `sc_fights` | two and three days | one thought a day; a fight has a reason | the read made twice on one day and once on the next, the day set by the clock of the memory; the fight giver asked for each pair |
| LeaningScrub `sc_colony_walk` | forty colonists, six systems, two orders | claims and the bank survive a reload; both orders pay alike | `sc_claim_survives_reload`, `sc_trip_orders`, two workers |
| LeaningScrub `floor_persistence` | three saves and 30 cycles | state survives; nothing grows | `floor_reload_once` live; `floor_growth_offline` for the 30 cycles |

## 4. Mods with no scenes

Abyss, BlueDesert, ColdStorage, CrackedLands, Greentide, LanternDeeps, LongShade, MachineLooks, Miasma, RustCathedral,
SleepingIce, TerminalBiomes, TheForge, TheRot, TheSump, Warscar, Wastes, Webwork, WeepingStones and WreckedMachines have no
`scenes.json` [measured]. There is nothing to shrink. The Designer reads the size rule already
(`src/RimMandrake/rimflow/roles/designer_scene_contract.md` §The cheapest scene that decides the bar).

## 5. Looked at and kept, with the reason

- Short bundles on a small list, everything held still: Explosive Knockback `sc_closed_containers`, `sc_goods_obstacles`,
  `sc_settings_sweep`, `sc_blast_kinds`, `sc_spared`, `sc_cover_breaks`; FlowWorks `sc_ways_out` (10 / 0), `sc_ice`; Slack
  `sc_floor_end_shock`, `sc_settings`. One staging, one row per reading.
- Acceptance scenes whose expectation has four or more parts, or two bars, in the designs that wait (a text count, so an
  estimate): Cauldron 20 of 33, FeverWood 32 of 46, GelatinousSlime 7 of 33, Stillsand 18 of 31, Contagion 6 of 30,
  PyrelandsMechanics 1 of 13, Graffiti 4 of 29, LeaningScrub 19 of 71 [measured by the text rule; that a given one is too
  big: guess ~50%]. None plays days, a raid or the full list after section 2. Each mod's ticket asks its builder to write one
  row per claim, and to split a scene when one claim can spoil another. No ticket is filed per scene.
