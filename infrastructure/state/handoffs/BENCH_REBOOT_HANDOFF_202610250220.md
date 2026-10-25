# BENCH_REBOOT_HANDOFF_202610250220 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610241710`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
🔴 ALMOST_OUT mode is ON (owner 2026-10-24): ONE subagent at a time, critical-path testing/debugging/fixing only (no code-health reviews, docs, audits), heavy reasoning to Codex first via gpt_consult.py, and every Codex attempt logged in infrastructure/state/facts/almost_out_codex_log.md. Mode ends only on his word. (see: auto-memory almost-out-mode.md)

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Sheets waiting on him (served this session; re-serve with serve_gated.py if the ports died): weir_by_photo, modern_bridge, sluice_gate_lifts_up, grate_door_lifts_up, suspension_redesign (Transient/biome_ffar/*_2026-10-24.html). Weir picks already ruled (on WEIR_LOOKS_REDRAW_ONE_PER_PIPE_STYLE); new weirs not installed yet.
- Spike trial (2x size, half density): D:\ClaudeWork\rimmandrake\fw_art_geometry_20261024\live_defects\SHEET_spikes_trial_x2size_halfdensity.png — BENCH recommends it; he says "trial" or keeps C (installed).
- Design decision BRIDGES_DIG_DESIGN_THREE_WAYS_EACH: D:\ClaudeWork\rimmandrake\design_bridges_dig_20261024\READ_FIRST.md (GPT recommends A in all three areas). Also: relabel Heavy "heavy truss bridge"? (his photo is a truss, his words say box-girder).
- Delegated calls BENCH took today (his to veto): TAR_GLASS option A (undug edge hardens to glass); hose lays with no curve refused with a reason.
- Second-workstation study: design/RimMandrake/second_workstation_study_2026-10-24.md; SteveDesktop plan design/RimMandrake/stevedesktop_bringup_plan_2026-10-24.md.
- RimFlow standalone docs ready for his readers: src/RimMandrake/rimflow/docs/ (383960172a).
- Last live run: FlowWorks modcheck 331 PASS / 1 FAIL / 283 UNMEASURED (was 345/6/265) — fixture raids and waking mechs still kill the colony mid-run, so the raids fix did not take live.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `STEVEDESKTOP_TRIAL_MEASURE_TOKEN_FREE_FIRST` — filed for Wed 2026-10-28 >16:00; NEXT: on that date, run Phase 0 + the GPT section of design/RimMandrake/stevedesktop_bringup_plan_2026-10-24.md on Archmagi.
- `STEVEDESKTOP_BRINGUP_BUILD_SECOND_BENCH` — filed for Fri 2026-10-30; NEXT: when he powers SteveDesktop on, follow Phases 1-3 of the same plan (check its Steam account owns all 5 DLC first).
- `MODCHECK_SITE_FIX_MECHS_WAKE_MID_RUN` — live run4: mechs at tick 4801 killed the colony, 21 rows UNMEASURED; NEXT: make the modcheck site mech-free/threat-free in the harness with a failing selftest, then one live rerun.
- `MODCHECK_SITE_FIX_RAIDS_KILL_THE_RUN` — offline fix c59c4ed212 did not take live (run4 FAIL); NEXT: find why fixture-raid stops still fire live (compare run4_LOG.md against clockgate.py/watch.py), fix, rerun.
- `PUMP_DRAW_FIX_LOSES_A_LEVEL` — new live FAIL (6→2 with moved=3), ran after the colony died; NEXT: reproduce offline in the flow kernel selftest before touching C#.
- `BODY_CLASSIFY_FIX_STICKY_OFF_NEVER_FORMS` — validation_v2 S5 regression; NEXT: trace with D:\ClaudeWork\rimmandrake\live_20261024\modcheck_run4\probe_w6.txt, fix with a failing selftest.
- `HOSE_MATRIX_FIX_WIDTH_BAR_PREDATES_GIRTH` — 9 proof_hose width FAILs are a stale bar (pre thin-hose ruling); NEXT: update the bar to the ruled girth, rerun proof_hose offline checks.
- `FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS` — 3 of 6 now pass live, 2 UNMEASURED (fixture colonist crushed/shot), 1 row missing; NEXT: after the mechs/raids site fixes, rerun modcheck and close.
- `FLOWWORKS_LIVE_ROWS_REMEASURE_STALE_HASH` — v2 61/63, proof_hose 37/9/6 at 0a5ad53d73b6; NEXT: rerun after the site fixes above land.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A lapsed companion profile makes bridge calls refuse silently and rows read UNMEASURED with no reason. (filed: lessons)
- Offline art sheets rendered on a stand-in floor lie; render on the real game floor. (filed: lessons 20261024T195137Z)
- Agents re-planned/re-verified deploys 5x (45 min); one plan, one apply, trust "VERIFIED in sync". (filed: lessons 20261024T220055Z)
- Fill-in waits must scale with the pawn's MiningSpeed. (filed: lessons 20261025T010851Z)
- ./publish -F with a ledger shard path is blocked by the ledger hook; use -m. (filed: lessons)
- A refused publish lands later under a different sha; closes must cite the landed sha. (filed: lessons)

## Closed since the last handoff (28)

- `LADDER_PORTABLE_DECIDE_EAST_WEST_FACING` — 3017ad0438c2ea401e7df891849e376db2230260
- `DUG_WATER_FILL_FIX_NO_CANAL_DEBIT` — cfb6f3820338
- `DRILL_FILL_FIX_LOSES_FRACTIONAL_BRIM` — cfb6f3820338
- `DISABLED_LIQUID_FIX_LIMITLESS_SOURCE` — cfb6f3820338
- `UNLIMITED_SINK_FIX_FRACTIONAL_WATER` — 65097834dde8497c267f0e06835a33f5990ad925
- `LEVEL_HOLDER_FIX_REFILLS_FRACTIONAL_BASIN` — 65097834dde8497c267f0e06835a33f5990ad925
- `PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE` — a953364956
- `GAME_DRIFT_DEPLOY_OLDER_COMMITS` — c68ae270245c
- `LEVELLING_BANDS_FIX_STOPS_PAST_EIGHT` — 675f96c57192575e9af3c2174ddb990e16a3e1f3
- `HOSE_RELOAD_FIX_SPILLS_SAVED_FLOW` — 52851352e4f2300126577f28315d58ed4a91c4db
- `TAR_GLASS_FLOOD_FIX_UNREACHABLE_PATH` — 4169fce37691
- `DUG_FILL_FIX_WALKS_TO_SHEET` — c42010afd35b
- `SPRINKLER_HEAD_REDRAW_SEEN_FROM_ABOVE` — cb78420900
- `MODCHECK_RUN_DIAGNOSE_TICK_ONE_STALL` — 87998efd85c5
- `HOSE_EXPLORER_WIDEN_SEEDS_LONG_LEAD` — 8d64560c3f0d
- `HOSE_FIT_HARDEN_FREE_LENGTH_SHORT_LEAD` — 8c355b364fb9
- `HOSE_MATE_REWIRE_CONTINUOUS_COUPLING` — 4b02e5884cd6
- `HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS` — 1ec89cc35d
- `DEPLOY_PLAN_FIX_REDUNDANT_TREE_PASSES` — a5a7bf7d22aa
- `DEPLOY_PLAN_FIX_STALE_INVENTORY_CACHE` — 0fd4436617c18f5fba338fd432f5f5bf6684bdc0
- `SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS` — 9f60e97d1e
- `GRATE_DOOR_REBUILD_LIFTS_LIKE_THE_SLUICE` — 9f60e97d1e
- `WET_PIT_LADDER_FIX_STILL_REFUSED` — aca6902967
- `WET_LADDER_FIX_NO_WALL_WHEN_BRIMFULL` — aca6902967
- `REVIEW_STAGER_FIX_NUMBER_EVERY_STATION` — bae1f9c239
- `SAVE_GUARD_FIX_BOM_READ_AS_BROKEN` — d95ee433db74
- `REVIEW_STAGER_FIX_BARS_OFF_SMALL_MAP` — 1c2472af4b62
- `REVIEW_STAGER_FIX_BRIDGE_LANES_SWAPPED` — 1c2472af4b62

## Filed and still open (22) — the next seat's queue

- `WEIR_SELFTEST_FIX_DEPOSIT_SCOPE_GONE` — selftest_flowworks_gpt_c.py C6-F9 red: RM_Weir.Deposit(ThingDef,int) no longer exists after 08a8e67cc6 (river flotsam rework); re-scope the case to th
- `WOVEN_SCRAP_COVER_REDRAW_FILLS_ITS_CELL` — Woven scrap pit cover texture is a round mat ~80% of its cell; if covers draw their art it reads as debris in the hole, not a lid
- `PIT_OCCLUDER_LID_FIX_DRAWS_COVER_ART` — RM_PitLipOcclusion.DrawBand paints a lid square with lid.PrintedSurface (terrain); if Building_PitCover.Print draws its own art the occluder must draw
- `MODCHECK_SITE_FIX_RAIDS_KILL_THE_RUN` — modcheck quicktest map takes pirate raids mid-run; colonists die, 29 rows UNMEASURED
- `FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS` — FlowWorks modcheck: 6 FAIL rows (4 standing since 09:27Z) need tracing
- `LADDERCLIMBERS_RENAME_MOVED_RM_DEFS` — FlowWorks_LadderClimbers.xml xpath lists RSW_Diplocaulus/Holcorobeus/Platyhystrix/Protosolpuga/Excretor, which no longer exist (moved to RM_ 2026-10-2
- `BANK_WEIR_FIX_TIMBER_TEXT_ON_STONE` — RM_BankWeir still describes 'A low timber wall' and costs WoodLog+Cloth, wood-stuffed, while its looks are now stone/concrete per pipe style
- `REVIEW_MAP_FIX_COVER_NEW_DEFS` — FlowWorks selftest_review_map and selftest_extensions are RED at HEAD, not caused by the gate rebuild: 18 uncovered inventory items (ThingDef RM_Ladde
- `WEIR_SPILL_REDRAW_ANIMATED_NOT_PAINTED` — Weir overflow: replace the baked-in static white spill in the weir sprites with a separate, much better animated water-over-the-weir layer (owner 2026
- `BRIDGES_DIG_DESIGN_THREE_WAYS_EACH` — Pick a way forward for suspension bridges, drawbridges and dig/fill materials: 3 GPT options each in D:\ClaudeWork\rimmandrake\design_bridges_dig_2026
- `FLOWWORKS_LIVE_ROWS_REMEASURE_STALE_HASH` — 93 FlowWorks modcheck rows UNMEASURED for one cause: no live result recorded at the current mod hash (63 core/v2 rows: validation_v2.py --live --fresh
- `MODCHECK_FINDINGS_FIX_WRITTEN_AS_REPR` — modcheck report summary.findings is a list of '<suite.Component object at 0x...>' strings: runner.py:647 puts Component objects in summary and runner.
- `PUMP_DRAW_FIX_LOSES_A_LEVEL` — Liquid pump: channel lost 4 levels while pump counted 3 draws (tank 30000) - conservation break, presumed MOD
- `MODCHECK_SITE_FIX_MECHS_WAKE_MID_RUN` — modcheck FlowWorks map: hostile Mech_Pikeman+Scyther arrive mid-run (undeclared), shoot colonists to death
- `FILL_IN_FIXTURE_FIX_CRUSHES_COLONIST` — toggle_fill_in: fixture colonist dies of Crush 60 ticks after fill-in designate
- `MODCHECK_VERIFY_FIX_SEAT_LOST_OVER_WSL` — modcheck run: emit_verify refused 'cannot tell which seat' even with RIMFLOW_SEAT in WSLENV
- `BODY_CLASSIFY_FIX_STICKY_OFF_NEVER_FORMS` — FlowWorks: edge pond W6 classified with stickyLimitless OFF never forms a body (S5 regression, was PASS 2026-10-24T02:48)
- `STEVEDESKTOP_TRIAL_MEASURE_TOKEN_FREE_FIRST` — Wed 2026-10-28 after 16:00 (accounts refresh): on Archmagi, measure held-vs-busy bridge time and tokens per accepted result; build the no-LLM scripted
- `STEVEDESKTOP_BRINGUP_BUILD_SECOND_BENCH` — Fri 2026-10-30 (owner back, powers SteveDesktop on): bring-up per design/RimMandrake/stevedesktop_bringup_plan_2026-10-24.md Phases 1-3 (SSH/LAN, WSL+
- `HOSE_MATRIX_FIX_WIDTH_BAR_PREDATES_GIRTH` — proof_hose MX_H00-H08 FAIL on width only: GSS northstar_matrix/design_spec.py:337 bar (Flat 0.375-0.385, Plump 0.46-0.47, width/wire>=4) predates the 
- `HOSE_SITE_FIX_TERRAIN_WONT_READ_BACK` — proof_hose style_hose and realflow blocks abort: jawa/set_terrain_batch on the fresh quicktest leaves cells that do not read back (R_site_ready 4 cell
- `HOSE_SL4_FIX_CARRY_NEVER_STAGED` — proof_hose SL4_carry_states_survive UNMEASURED every run: the CR4a/CR4b staging never gives pawn 407 a carry (all carry/trail fields null before and a

## Commits

```
62ec1cad31 conversations: catch-up 5 record(s)
b713d5a57e BENCH run4: FlowWorks modcheck/v2/proof_hose remeasured at 0a5ad53d73b6, modcheck record RED, three hose findings filed
94511d06c5 SteveDesktop bring-up plan + GPT enhancement; file Wed/Fri items; codex log row
2ecc1bce3a codex log: second-workstation study row
2639a72c69 second workstation study: testing workflows, bottlenecks, GPT cost/benefit
ba050337af ALMOST_OUT mode: Codex consultation log (owner 2026-10-24)
4517606d7e FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS: code-review marks for extensions.py, selftest_extensions.py, validation.py (full-file review, no findings)
9c5defd5f0 ledger: FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS note, two findings filed, all-off item dropped, MiningSpeed lesson
cfa085dba6 FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS: six FAIL rows fixed offline (recession on a shelving pond, fill-in waits on MiningSpeed, slime wades cell by cell, pump off the pond, all-off digs dry ground)
ce7e785b00 ledger: BENCH notes for raids fix and all-off item
15e176269d FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS: code-review marks for the raids fix (c59c4ed212)
52fbc13f81 using-rimflow skill: claim lands in doing under a lease, not ready (was false since the lease redesign; cli.py cmd_claim)
383960172a rimflow docs: standalone README, design history, AGENTS, comparison, ideogram
c59c4ed212 MODCHECK_SITE_FIX_RAIDS_KILL_THE_RUN: the row's own spawned Pirate fixture arriving no longer stops safe_advance
0612029904 ledger: OWNER shard game stamps
dc6ff5d723 ledger + code-review mark: stager/save_guard fixes
1c2472af4b REVIEW_STAGER_FIX_BARS_OFF_SMALL_MAP + BRIDGE_LANES_SWAPPED: fit origin to map, off-map refuses, rails-on bridges built north
d95ee433db SAVE_GUARD_FIX_BOM_READ_AS_BROKEN: accept a UTF-8 BOM before <?xml
01a60e50f4 ledger: run3 live - wet ladder row PASS (2 closed), stager numbering closed, 3 defects filed; lesson profile expiry
330d7e5fe4 ledger: BRIDGES_DIG_DESIGN_THREE_WAYS_EACH filed (bridges + dig/fill design session, needs owner)
... 114 more: git log --oneline d78e91a908..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-10-25T02:19:10Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M infrastructure/state/ledger/events/OWNER.jsonl   — BENCH (live run4 game stamps), committed with this handoff
?? deployed/config/ModsConfig.swap-active.json   — modlist_swap.py live state (tool-owned, deliberately untracked)
?? infrastructure/state/art_eval/regen_rounds.json.lock   — art_eval lock file (tool-owned, deliberately untracked)
```

