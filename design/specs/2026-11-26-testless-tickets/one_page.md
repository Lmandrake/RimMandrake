# Open tickets with no test: where each one stands, and the holes

Item `RIMMANDRAKE_PROVE_TESTLESS_TICKETS_ROUTE_HE_WAS_TOLD_NONE`. Read at 2026-11-26 9:34 PM PST. The owner asked that every ticket
without a test has a pathway to get one (2026-11-26: "Please make sure there is a pathway to provide tests for all tickets without
them, given that I'm being told they can't participate in bundling otherwise").

## The answer in one paragraph

**1,076 open tickets have no test** [measured: `python3 -I design/specs/2026-11-26-testless-tickets/testless_census.py`; the
count is `list_shape.needs_shape_run`, the lane's own reading]. Only 48 are on a route today. 29 are not work. 469 wait for a mod
that is not in the Maturation Pipeline. 412 wait on a park or a hold. **332 sit in a hole that no program ends**: 248 have no home
(105 plainly, 143 more behind a hold or a park), 80 have a block with no end condition, and 10 belong to a mod that is ON but has
no route. Nothing in the machinery was broken, so I fixed none of it. Three of the holes need a decision from the Conductor
(questions below). The count moves by a few tickets an hour; each row below was read in the same run.

## The three routes, as the code has them

| route | code | takes |
|---|---|---|
| Shape stage | `list_shape.due`, `list_dispatch` Shape rows | a non-mod ticket named for Shape, or filed at or after 2026-11-23 6:00 AM PST (`shape_from`), after 24 h |
| onboarding run | `list_dispatch.onboard_step`, `work_bundle.onboard_homes` | old tickets of a `pipeline:`, `machine:` or `game:` home whose class is on (`onboard_classes`) |
| mod bundle | `maturation_dispatch.pilot_holders` → `road_back_holder` → `work_bundle.mod_members` | old tickets of a mod, only inside the holder run of a ledger pilot mod that has an open road back |

`mod_members` has no other caller [measured: `grep -rn mod_members src/RimMandrake --include=*.py`]. The ledger pilots are
ExplosiveKnockback, GimmeSomeSlack and FlowWorks [measured: `modledger.config()["pilot_mods"]`].

## States (each ticket in one state; the first rule that matches wins, in this order: not work, park, mod, switch, route)

| state | count | five examples |
|---|---|---|
| ON A ROUTE | 48 | `LEVEL_ALLOC_SHRINK_EIGHTFOLD_OVER_BAR` (FlowWorks holder), `MIDCHANNEL_ISLAND_FILL_REACH_UNMEASURED` (FlowWorks holder), `OPS_DISPATCH_CLONE_BEHIND_UNSTICK_YUYW` (onboarding, `pipeline:operations`), `OPS_LIST_GATE_HOLDS_READY_WORK_ON_COULD_NOT_LOOK_WTHJ` (Shape), `OPS_MATURATION_MOD_STALLED_KHOT_RRON` (Shape). By route: Shape 34, mod bundle 13, onboarding 1 |
| PARKED | 206 | `ABYSS_CRAGS_ART_ON_PORTED_DEFS_1` (block, no kind), `BAZAAR_BANTER_LINES_1` (block on an open item), `BEER_DIAGNOSE_NON_DRUG_3200_LOG_ERRORS` (owner block), `BIOME_PAINT_ONCE_AT_THE_END_1` (dated wait), `BRIDGE_TPS_CAPTURE_FIXES_1` (refused by a bundle) |
| CLASS OFF | 0 first, 59 underneath | `GRAVSHIP_FACING_GAPS_REDRAW_BORROWED_SIDES`, `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS`, `MAP_SILENCE_SINGLE_OWNER_1`, `RIMMANDRAKE_RESEAT_BRATHEK_NORTH_BATCH_ACCEPT_DROPPED_IT` (all `game:`, off since 2026-11-26 7:35 PM PST). Every `game:` ticket is parked or held first, so its class shows in the cross-table below |
| MOD HELD | 206 | `AGARILUX_PRINT_FIX_NRE_ON_RELOAD` (LeaningScrub), `ANT_HIVE_WALLS_VERIFY_NOT_WALKED_IN` (FeverWood), `ARIDSHRUBLAND_TITAN_POPULATE_FORTY_NO_GIANT` (LeaningScrub), `ARTEVAL_INSTALL_DEPLOY_HELD_BIOMES` (Cauldron), `BROOD_GIZMO_TOOL_BUILD_CLICKS_GO_NOWHERE` (FeverWood). 135 of the 206 are tickets whose id or title names a held mod, not tickets of a mod home (the lane's own `_off` rule) |
| MOD NOT ADMITTED | 469 | `ABYSS_FIRST_SCRIPT_1`, `ABYSS_HIDDEN_SHIP_PROBES_1`, `ABYSS_LIGHTFALL_BROOD_WRECK_1`, `ABYSS_SHEET_DONOR_PORT_1`, `ACOUSTICSCANNER_DESIGN_FIRST_TOUCH`. 88 mods with no stage record (15 mods have one, the same 15 that `./pipe show` lists) |
| NO HOME | 105 | `BIOME_ARRIVAL_LETTERS_ALL_1`, `BIOME_DEFNAME_MIGRATION_WAVE_1`, `COLD_STORAGE_ART_BUILD_SPRITE_BATCH`, `COLD_STORAGE_CARBONFREEZE_REDRAW_INTERIM_ART`, `COLD_STORAGE_CHAMBER_BUILD_DRINKS_CHILLER` |
| NO ROUTE | 13 (10 a hole) | `FIRE_CLOCK_FIX_RAIDS_IGNORE_THE_SWITCH` and `RITE_HARVEST_FIX_PICKS_PAST_FULL` (Pyrelands, ON, not a pilot); `RAKATAN_ARCHOTECH_MACHINES_1`, `SHIP_ALLOY_FORGE_1`, `WRECKED_DISTILLATION_MODULE_1` (WreckedMachines, ON, not a pilot, 8 in all). Not holes: 3 ExplosiveKnockback tickets, whose mod rests after its pass and whose tickets are on the Conductor's owed view (`conductor_stops` mod_rest) |
| NOT WORK | 29 | kind owed 28, kind standing 1: `RIMMANDRAKE_ADD_COVER_FADE_STATION_TO_NEXT_FLOWWORKS_LOOK_HE_JUDGES_IT`, `RIMMANDRAKE_ADMIT_INHABITED_TO_PIPELINE_AFTER_FOUR_MODS_NEVER_SEEN_IT`, `RIMMANDRAKE_ALLOW_CODEX_CALLS_IN_WRECKED_MACHINES_FABLE_RUN_HE_ASKED`, `RIMMANDRAKE_ASK_STEVEN_DRAWDOWN_TUESDAY_HE_DECIDES_THEN`, `RIMMANDRAKE_BRING_PIPELINE_FORECAST_HE_ORDERED_NO_PAUSE` |
| COULD NOT LOOK | 0 | none |
| **total** | **1,076** | |

Parks, by kind (the 206): block with no kind and no end 80 · block on an open item 29 · refused by a bundle 28 · owner block 25 ·
dated wait 23 · external block 12 · live-game block 4 · `pipe off` switch 5. What each parked or held ticket would be if the park
or hold ended, which is where it goes next:

| park or hold | would be | count |
|---|---|---|
| PARKED (206) | ON A ROUTE 66 · CLASS OFF 58 · MOD NOT ADMITTED 47 · MOD HELD 21 · **NO HOME 12** · **NO ROUTE 2** | 206 |
| MOD HELD, non-mod home (206) | **NO HOME 131** · ON A ROUTE 3 · CLASS OFF 1 · mod home 71 (own state) | 206 |

## The holes (a state that no act of the owner or the Conductor ends)

| hole | tickets | why nothing ends it |
|---|---|---|
| **NO HOME**, old (filed before 2026-11-23 6:00 AM PST, never named) | **248**: 105 plain, 131 behind a mod hold, 12 behind a park [measured] | No `home` field (all 248 read `None`), and the parent supplies none. The Shape stage takes an old ticket only when someone names it (`list_shape.due`); onboarding never starts an `item:` or `cause:` home (`work_bundle.onboard_class`, boundary page line 203). 79 parents (`cause:`) cover 112 of them; 136 are `item:` singles. 118 were filed in November, 112 in October, 18 in September |
| **Block with no kind and no end** | **80** (29 on mod homes, 16 `game:`, 13 `pipeline:`, 5 `machine:`, 17 with no home) [measured] | `blocked_kind` empty, no `--on`, no lift date. The age line (`list_dispatch.block_age`) needs a `needs` window that opens (game UP, bridge free); 61 of these need `offline`, which has no opening event. Under it, 18 would be on a route, 16 CLASS OFF, 28 MOD NOT ADMITTED, 11 MOD HELD, 7 NO HOME. 18 of the 80 are on `pipeline:` and `machine:` homes: the unpark run reads those (not changed here) |
| **ON mod that is not a ledger pilot** | **10**: WreckedMachines 8, Pyrelands 2 | The holder run starts only for a pilot mod with an open road back. WreckedMachines stands at designer, Pyrelands at offline_build, neither is a pilot |

Not holes, by the rule: MOD NOT ADMITTED (admitting the mod is the Conductor's act, and its old tickets then join its bundle);
CLASS OFF (the Conductor turns `game` on again on or after 2026-12-02); MOD HELD (the owner's hold); a block on an open item, an
owner block, a dated wait (each ends by a named event); the 3 resting-mod tickets; NOT WORK.

## Do the routes run? [measured: bundle records in `D:\ClaudeWork\rimmandrake\dispatcher\work_bundle\bundles\`, ledger `shape` events]

- 122 onboarding bundles exist, all started on 2026-11-26 PST: 74 ended, 24 replaced, 24 launch_failed. The 24 failures were all
  between 3 AM and 8 AM PST on 2026-11-26 (12 on `pipeline:operations`); none since. The newest record is `game:direct-sun`, 7:47 PM PST.
- Outcomes of their 362 member slots: fixed 68, dropped 38, routed to a judge or the owner 26, refused 22, waiting 14, open 2.
- **80 tickets got a test from an onboarding run in the last 7 days** (`shape` events by an onboarding unit, or citing a "work
  bundle WB-" id): 34 are still open and none of the 34 is testless now; 46 were closed or dropped since.
- Only 1 of the 1,076 is on the onboarding route today. The route works; its homes are empty because the tickets are parked, held
  or off (the `game` class is off since 7:35 PM PST).

## What I fixed

Nothing in the machinery. Each hole is a choice between known fixes that changes how many model runs the lane launches, while
the owner's card of 2026-11-26 puts pipeline repairs ahead of the account room (`list_dispatch.json` `onboard_classes` note). I built
the instrument instead: `design/specs/2026-11-26-testless-tickets/testless_census.py` (read-only; changes no ticket) and its
selftest `selftest_testless_census.py`: 27 checks pass; with the NO HOME hole flag planted false, 3 fail; with the untyped-block end
planted true, 1 fails. Run it again after any fix: the hole counts must fall.

## Questions for the Conductor

1. **248 old tickets have no home and no route. May the lane name them for Shape, a few a day?** Evidence: all 248 have `home = None`;
   Shape runs one ticket per run and the lane has two slots (`max_live` 2). Recommended: the lane names the oldest unparked,
   unheld no-home ticket, up to 5 a day, from 2026-12-02 (when the accounts reset). Else they stay untested; the 131 behind a mod hold
   wait for that hold. Cost per Shape run: UNMEASURED here.
2. **80 blocks have no kind and no end. May the age line take them?** Evidence: `block_age` returns "needs offline: no ledger event
   opens that window" for 61. Recommended: a block with no kind, no `--on` and no lift date, idle 3 days, is due for Shape whatever its
   `needs`; the Shape run types it (`rimflow block --kind`) or lifts it. Launches now: at most 18 runs (the rest sit behind a class
   that is off, a mod that is not admitted or a hold).
3. **10 tickets of Pyrelands and WreckedMachines have no route. Make Pyrelands (and later WreckedMachines) a ledger pilot?**
   Evidence: `pilot_holders` is the only caller of `mod_members`; pilots are three mods. Making a pilot needs the mod ledger backfill
   and `ledger_ready`: the readiness list gates it (CLAUDE.md §No mod runs forward on a broken pipeline), so I did not do it.

Could not look at: the cost of one Shape run (no record of it was read); whether a held mod's `item:` tickets really belong to that
mod (the lane's word match decides, as the lane does).
