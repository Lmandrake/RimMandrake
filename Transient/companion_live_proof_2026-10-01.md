# Companion live proof 2026-10-01 (NORTHSTAR_COMPANION_LIVE_PROOF_1)

Log (append-only):
- start: worktree /mnt/d/Luke/dev/wt_proof from origin/main (main tree is 254 behind)
- minimal list swapped (26 active), bridge taken, steam launch issued 18:25
- 18:26 game up, quicktest map Playing (prove_quicktest_world exit ok)
- 6/6 tools present in tools/list (488 total), params match. Player.log line 311: "[JawaBench] event recorder: damage=True kill=True lineage=True" -> recorder start-up line MEASURED.
- Baseline (tick 1): pawn_census 14 pawns (3 Colonist, 1 Horse PlayerColony, 8 Rhinoceros/1 Emu/1 Hare factionless); nested rows (mentalState null, breakImminent{}, needs{}, job null) arrive as JSON objects -> nested-arrival MEASURED for dict/null; non-null nested job/mentalState to be shown below. damage_log status: installed damage+kill, totalRecorded 0. incident_queue_peek: count 0.
- 18:28 /tmp tmpfs hit 100% (other agents' worktrees); removed pushed /tmp/wt_comp (4.2G, ancestor of origin/main; its only untracked file saved as Transient/modcheck/fixtures.wt_comp_saved.json)
- A MEASURED: pawn_force_mental_break Wander_Sad on Human960 -> census (30 ticks later): inMentalState true, mentalState{def Wander_Sad,isAggro false,ageTicks 60,causedByMood true,...}, job{def GotoWander,targetA{thingId null,x135,z103},targetB null}. Nested objects arrive populated.
- B MEASURED (job forced via jawa/ordered_job PredatorHunt, natural hunt did not occur in 960 ticks: wolf not hungry): census wolf isPredatorHunting true, preyId Hare11402, job{def PredatorHunt, targetA{thingId Hare11402,def Hare,x49,z40}}, hostile false faction null (factionless predator not hostile - as documented).
- C damage_log MEASURED (natural wolf->hare): seq0 damage Bite 12.28 victim Hare11402 instigator Wolf_Timber11403 weapon Wolf_Timber hediffsAdded[Bite] tick 1244 x52 z37; seq1 Stun; seq2 kind=kill culpritHediff Bite tick 1364; seq3 damage victimDeadAfter true. kind filter works (kind=kill -> 1). NOTE hitPart null on every event (gap, minor, C# not touched). Controlled jawa/damage + pawn_force_incapacitate runs next.
- D MEASURED (Rat11419): jawa/damage Cut 3 -> exactly 1 damage event (seq4, amount 3, victimDeadAfter false, instigator None); pawn_force_incapacitate action=kill -> exactly 1 kill event (seq5, damageDef None since no DamageInfo, victimDeadAfter true). Total recorded delta 2.
- E MEASURED incident queue: scheduled 3 (FarmAnimalsWanderIn@51381, WandererJoin@52381, FarmAnimalsWanderIn@53381); peek count 3 with index/defName/fireTick/ticksUntilFire rows; remove dryRun (default) matched 1 removed 0, queue 3->3; real remove defName+fireTick -> removedCount 1 (measured 3->2), the OTHER same-def entry and WandererJoin survived (peek confirms 2); no-match (defName+wrong fireTick) success=false 'Nothing in the incident queue matches...'; bad def success=false; no selector success=false.
- F1 thing_lineage (stacks 11422 x20 @134,106 and 11423 x15 @135,106): split_stack 8 -> journal seq0 split (otherId ...11424, count 8, stackAfter 12) then seq2 absorb 11424 -> 11422 (placed piece merged straight back): split+absorb recorded; holderChain [map:0, worldObject:WorldObject_111, world]. Haul-merge + ingest next.
- F2 thing_lineage haul-merge MEASURED: HaulToCell moved 1 unit; journal on 11423 seq3 tick1446 split (otherId 11425 count1 stackAfter14); on 11422 seq6 tick1477 absorb (11425 -> 11422 count 1); stacks 21/14 confirmed by list_things (sum 35 conserved). Ingest next.
- F3 MEASURED: haul-merge (above) plus ingest: Human963 Ingest order -> 11429 (1 split off 11423) journal: seq8 split, seq9 detach, seq11 destroy(Vanish) holder carriedBy, seq12 ingest otherId Human963; fate 'destroyed:Vanish' for gone ids; mid-meal holderChain [carriedBy:Human963, thing:Human963, map:0,...]. Unknown id Meat_Muffalo99999 -> found false fate UNRECORDED events [].

## Verdicts (all MEASURED live, minimal 26-mod list, quicktest map, DLL --gm as deployed)
- recorder start-up line: MEASURED (Player.log "[JawaBench] event recorder: damage=True kill=True lineage=True"; installed on first tool call).
- jawa/pawn_census: MEASURED. Forced Wander_Sad shows mentalState{def,isAggro,ageTicks,causedByMood..} + job{def GotoWander,targetA{...}}; predator row isPredatorHunting true + preyId (job forced via ordered_job PredatorHunt; a natural hunt did not start in ~960 ticks); unresolved id fails loudly.
- jawa/pawn_roles: MEASURED. Colony Horse isPlayer true / isColonist false / isAnimal true; unresolved id fails.
- jawa/incident_queue_peek + remove: MEASURED. 3 queued, dryRun removes 0, real removes exactly 1 (measured 3->2, the other same-def entry survives), 3 no-match/invalid forms fail loudly.
- jawa/damage_log: MEASURED. Natural wolf->hare bite/stun/kill/death-bite sequence and controlled Rat: one damage event + one kill event. Minor gap: hitPart is null on every event (not fixed, no C# edit).
- jawa/thing_lineage: MEASURED. split, absorb (merge, both ways), detach, destroy(Vanish), ingest by Human963; fate 'destroyed:Vanish'; unknown id -> UNRECORDED; holderChain carriedBy mid-meal.
- Nested rows over the bridge: MEASURED (dicts, nulls and arrays arrive as JSON).
- NOT done: "abort path with a real hazard" from the item title (outside the brief; stays open as its own follow-up).
- Housekeeping: /tmp tmpfs hit 100% mid-run; removed pushed worktree /tmp/wt_comp. Game killed, full list restored (612 active), bridge released.
