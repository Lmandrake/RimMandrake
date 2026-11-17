# Explosive Knockback 0.1.0: the Fable Rescue of 2026-11-17

Item `RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX`. The sheet for the owner is
`D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX\inventions.md`; this folder is the
evidence it cites. Every number below is measured on the run named beside it.

## What changed

- **One decision, run offline.** The whole throw decision (who is spared, held goods, gas shove, shield, the rim, the walk,
  a container's rest, a rebound, where a landing stack is put) moved out of Verse code into
  `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackPlan.cs`, which the SelfTest compiles as shipped. The game side
  (`RM_MapComponent_Knockback.Execute`, the two flyers) reads facts and applies the plan.
- **The situation map** (`Source/SelfTest/KnockbackMap.cs`, `selftest_explosiveknockback_map.py`): the shipped decision on a
  model map over 121,920 enumerated lanes, 2,496 spared cases, 20,000 seeded storerooms x 2 tie orders, 13 fixed cases and
  11 settings flips, read as 21 bar readings; 30 planted faults, each seen.
- **What the map found and the plan now does** (`map_before_fix_map-1.txt` against `map_selftest_after.txt`):
  a stack with a wall, door or map edge right behind it sat still (14,070 of 47,952 reached goods in storerooms): it now
  takes the hit where it lies and flies the bounce; a stack landing on a pit cell that already held one was put on any
  neighbour, the far rim included (401 of 2,200 pit flights): pit floor first, then the side it came from, never past the
  pit; a short throw ending on sandbags was undone: it clears them; a container's rest cell was read off a shorter line
  than its walk (14 of 874): one line.
- **Saved with the map:** which explosion threw a pawn (it was a static a load forgot, so a colonist reloaded in mid-air
  stood on the cover it should have broken).
- **Proof scenes repaired:** `storeroom_bomb_pit_control` (its cover stack must END on the cover cell on flat ground; since
  610b127ba8 every log count "planned onto" a covered pit), `closed_containers` (the heavy locker is filled to its real
  mass), `pawn_arc` (the blast goes two ticks after the walker's order).

## Live (Archmagi, RimWorld 1.6.4871, the mod's 34-mod list with every DLC, AridShrubland quicktest; proof build md5 9329b24cafac25efd06b594c1b7134c4 from this commit's source)

| run | result | file |
|---|---|---|
| model against game, 115 staged cases | **115 of 115 agree** | `live/agreement.txt`, `live/agreement_result.jsonl` (cases: `live/agreement_cases.jsonl`) |
| the same set, first run on one site | 91 of 115; all 24 misses gas cases 300 ticks apart on one cell (a gas cell bursts once in 600 ticks): harness, fixed by taking sites in turn | `live/agreement_run1_same_site_gas_reburst.txt` |
| every proof scene, 300 ticks | 65 PASS of 69; the other four need their own command (below, or the full list) | `live/all_scenes_300_ticks.txt` |
| sc_storeroom_bomb_pit and its control, 900 ticks | PASS, PASS (the flagship: visit 3 FAIL on the cover) | `live/sc_storeroom_bomb_pit.txt` |
| sc_pit_fetch, 60000 ticks | PASS | `live/sc_pit_fetch.txt` |
| frame_probe_selfcheck, 25 s unpaused | PASS | `live/frame_probe_selfcheck.txt` |
| a pawn saved in mid-flight, plain and onto a cover | 5 of 5 rows PASS | `live/pawn_flight_saveload.txt` |
| pawn_arc before its head start | INVALID 3 of 3 on one site (4 of 9 over the sitting); after: 10 of 10 PASS | `live/pawn_arc_before_head_start.txt` |

UNRUN (they need the owner's full list, 316 mods): `sc_barrage_perf` and `sc_walk_raid`, with the commands in
`../test_table.md`. The bounce off a wall puts more stacks in the air in a walled room than before: the barrage bar is
the check that reads it.
