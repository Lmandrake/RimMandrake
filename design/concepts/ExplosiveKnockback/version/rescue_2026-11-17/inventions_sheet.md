# Explosive Knockback 0.1.0: the rescue sheet (11:12 AM PST 2026-11-17)

Landed: `ffc3937ee7` (the plan, the map, the fixes), `5e44c9c0b6` (three text checks, the steward's repair), `ac2ebc01cb` (a Slack proof that kept this mod's certificate red). Certificate: 16 of 16 offline tests, OK [measured 11:1x AM PST]. Evidence index: `D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\rescue_2026-11-17\README.md`.

## The problem as I wrote it down

Five blind cycles and three in-game visits did not converge. Two different things were going round:

1. **Every real miss the judges found since cycle 4 sat in code no offline test could run.** The kernel (path maths) was Verse-free and tested; the DECISION around it (who is spared, held goods, the gas shove, shields, the rim, a container's rest, the landing, the cover break) lived in the game-side file. Each blind cycle wrote 57 "unsettled, not kernel" rows, planted about ten faults there that every offline suite missed, and then found the next real miss by reading the callers by eye (a pawn on a cover, a throw over a covered pit, a stack on a cover). [measured: cycle_5/SUMMARY.md]
2. **Every flipping live check was the harness or the site, not the mod** [measured from the three visits' own summaries, and again today]: a pond bed under a scene, rain filling a pit, earlier scenes' corpses hauled into this scene's stockpile, a locker filled by estimated mass (74.9 kg against a 76 kg floor), a gas cell re-used inside its once-only window, a walker with a two-tick window, and a control scene whose staging a kernel fix had broken unseen because the scene was UNRUN since.

So yes: **the judging was part of the trouble.** The blind lane could not see where the faults were, and the live scenes read hidden inputs (the site, the clock, a random pawn's speed).

Underspecified, found on the way: what a good does when a wall, door, sandbags or deep water takes its whole throw; where a stack goes when the pit cell it is thrown at already holds one; whether a flight saved in mid-air must still break its cover.

## Every check that read the same ground

The pit and cover ground alone was read by: leaves `thrown_into_pit_falls`, `blast_breaks_pit_cover`, `the_spared`, `gas_goes_clump_by_clump`, `closed_container_holds`, `no_careless_fall`, `pit_goods_fetched`; inventory rows `inv_pits_receive`, `inv_pit_floor_goods_stay`, `inv_pit_floor_haul`; kernel tests K-08, K-24, K-25; the judges' `accept_covered_pit.py` and `check_pit_pawn.py`; scenes sc_pit_fall, sc_pit_enemy, sc_cover_breaks, sc_gas_shove_into_pit, sc_storeroom_bomb_pit (and its control), sc_closed_containers' pit lane, P_in_pit_skip, P_corpse_into_pit, P_land_no_bump_pit, the walk's cover rows. The goods-against-a-wall ground was read by NO check: every scene staged its stacks in the open or two cells off a wall.

## The instrument

**One decision, run offline.** `RM_KnockbackPlan.cs` holds the whole throw decision, Verse-free, compiled by the SelfTest as shipped; the game side reads facts and applies the plan.

**The situation map** (`selftest_explosiveknockback_map.py`): the shipped decision on a model map, the bars read off where things end.
- Declared range [measured]: 121,920 enumerated lanes (8 things x 5 blasts x 16 directions x 3 distances x 11 obstacles x 7 obstacle steps x narrow or wide), 2,496 spared cases, 20,000 seeded storerooms x both tie orders of the game's "place near", 13 fixed cases (the mod's scenes and the cases that used to fail), 11 settings flips. 21 readings.
- NOT covered: two blasts in sequence (recovery, barrages, gas chains), covers wider than a cell, things the blast kills, doors opening mid-flight, map edges, the drawn arc, frame time, save and load (that one is a live proof now).
- It can see: 30 planted faults, 30 seen. On its first run it saw 26; the four it missed became four more readings.
- **Agreement with the game: 115 of 115 staged cases** end where the model puts them (34-mod list, proof build 9329b24c) [measured]. The first run read 91: all 24 misses were gas cases 300 ticks apart on one cell (a gas cell bursts once in 600 ticks); with the sites taken in turn, 115.

## The map (before, on the code as I found it; after, as landed)

| reading | before | after |
|---|---|---|
| every_good_moves: a reached good with a throw of a cell or more leaves its cell | **14,070 of 47,952 in storerooms sit still** | 0 of 236,118; 8,166 counted as pinned by the map itself (deep water behind, a one-cell throw into a wall, boxed in) |
| goods_arc_spin_rebound: a good that hits a wall with speed to spare bounces | 13,448 of 27,256 | 0 of 110,138 |
| thrown_into_pit_falls: a flight that meets a pit ends on a pit floor | **401 of 2,200 in storerooms end on the rim or past it** | 0 of 25,568; 4,674 full-floor landings all set down on the side they came from |
| a thrown container comes down on the path its walk read | 14 of 874 | 0 of 15,524 |
| the spared, covers under a landing, gas leaves covers whole, gas shove one cell, rests, pawn stops, nothing lost, reach | hold | hold |

PICTURE: `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX\pictures\wall_before_after.png` (WSL `/mnt/d/ClaudeWork/rimmandrake/showings/RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX/pictures/wall_before_after.png`)
PICTURE: `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX\pictures\pit_before_after.png` (WSL `/mnt/d/ClaudeWork/rimmandrake/showings/RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX/pictures/pit_before_after.png`)
PICTURE: `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX\pictures\sandbags_before_after.png` (WSL `/mnt/d/ClaudeWork/rimmandrake/showings/RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX/pictures/sandbags_before_after.png`)

## The candidates and the account

**Resolve two into one (the pick).** The "blocked" stack and the flying stack were one thing split in two: a good that hits a wall. A stack right against the wall hit it at step zero and was treated as not thrown; one cell out it flew and bounced. Now both take the hit and fly the bounce, by the same rebound rule. Likewise the decision and its callers were one rule described twice; now once.
- Benefit: the two biggest regions closed (table); the flagship scene sc_storeroom_bomb_pit PASSES live with its control (visit 3: FAIL on the cover) [measured]; ten "caller" fault classes are plantable offline.
- Risk: more stacks in the air in a walled room; the frame bar on the full list (sc_barrage_perf, sc_walk_raid) is UNRUN on this build.
- Added: one file (the plan, 430 lines) against about 330 lines of rules deleted from the game side; two constants, each with its derivation in the code (HopExtraCells 2, PitSpread 1.5, RimSpread 2.9). No new setting, no new art, no bar text changed.

**Invent: pit floor first, then the side it came from.** What a real pit does: the second crate lands beside the first on the floor, and when the floor is full it tumbles back, never across. Benefit: the pit region closed. Complexity: one ordered list (`KbPlanner.LandingOrder`). 44 of 20,000 storerooms still had no free ground on the near side either; those stacks go back beside where they started (counted, reading M17).

**Invent: a good clears sandbags it would end on.** Dropped for people: a colonist's one-cell throw onto sandbags is still undone, as before (no bar reads it; listed below).

**Lost: tuning.** No constant was moved to turn a check. **No relaxation is proposed.**

## Proposed bars (each with its check already passing; yours to accept)

1. *A stack lying against a wall is not left behind by a blast: the player sees it slam into the wall and bounce away like its neighbours.* Check: map readings M04 and M13; live case 97.
2. *When the pit a stack is thrown at is full, it comes to rest on the side it came from; nothing ever comes to rest past a pit.* Check: M02, M15; live cases 100 and 101.
3. *A thing saved in mid-air ends where it would have: a colonist reloaded in flight lands on its planned cell and still breaks the cover it comes down on.* Check: `proof/pawn_flight_saveload.py`, 5 of 5 live.
4. *The model and the game agree.* A Stage 6 row: `proof/map_agreement.py`, every case agrees.

## Still open (each needs the live full list or your word)

- sc_barrage_perf and sc_walk_raid on the 316-mod list: UNRUN on this build (commands in `version/test_table.md`).
- Q2 below (a full pit).
- A burning gas clump reaches everything within its radius with no line of sight, so it can shove a thing diagonally past a wall corner [read in code, not measured live]; the map's model copies that, so its "reach" reading cannot see it.
- A colonist with a one-cell throw onto sandbags stays put, unhurt (unchanged).
- Polish and later-version tickets: `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX\tickets_sorted.md` (51 sorted: 2 closed here, 5 need the full list, 4 are record-keeping, 8 Polish, 11 built but open on paper, 5 past-stage records, 3 later version, 13 not this mod).

## For the judge who did not build this

Look first at: (1) `RM_MapComponent_Knockback.Execute` against the plan: does any rule still live on the game side? (2) the map's model assumptions A1 to A5 at the top of `KnockbackMap.cs`: each is a copy of game behaviour, and the 115 live cases are the only thing vouching for them; (3) the wall bounce in a full storeroom on the full list, for frame time.
