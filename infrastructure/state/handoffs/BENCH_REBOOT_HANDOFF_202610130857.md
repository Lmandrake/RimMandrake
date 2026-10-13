# BENCH_REBOOT_HANDOFF_202610130857 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610130004`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Testing changed shape tonight, by owner rulings now in `design/RimMandrake/debug_process.md` (sections "Test disturbances" and "Long-duration properties"): **no more long runs**; build and test what can be measured directly, in minutes. Long-duration properties are compressed (shorten constants, restore, read back) or decomposed and recorded INFERRED. A disturbed row restarts, never FAILs; every threat gets a TESTENV_* item. The tooling that enforces this now exists and is deployed: the in-game vitals/threat monitor (`jawa/vitals`), `jawa/safe_advance` (chunked, interruptible, refuses unsafe advances), the row governor (`modcheck/governor.py`), the quiet-site profile (`modcheck/quiet_site.py`), and the bridge concurrency guard. Clock sets (`jawa/time_set_ticks`) are refused on populated maps unless `timeException=true`. Owner's AFK order (Mon 2026-10-12 ~21:50 PDT): *"Check off the items, then plan on not validating them again for some time. We need to keep moving other items."* It ends when he next writes.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Pilot exit criterion 3 was changed by his card (INFERRED and labelled gaps are accepted). The pilot is still open: Pyrelands never finished one run at one HEAD (pass 8 was stopped on his order). Review-queue rows 1-4, 6 and 8 still need his sign-off: `D:\Luke\dev\RimMandrake\Transient\ratchet_owner_review_2026-10-12.md`.
- The pond bed hollow needs his look decision, with three options on `POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE`. It also needs `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` first.
- The pond volume unify shrank the 2x2 liquid tank from 300 to 80 units; the cargo tank is 160. This is per the design card, and he can veto it. New tank sizes wait on art and costs.
- `jawa/time_set_ticks` now refuses on populated maps; all 18 existing callers pass `timeException=true`.
- GPT's test-control review is `design/RimMandrake/test_control/test_control_review_gpt_20261013.md`.
- `ART_SHEET_REDESIGN_FRESH_OR_REFUSE` is still HIGH for Wednesday night.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP` — doing; criteria 1, 2 and 5 met, criterion 3 (Pyrelands, new INFERRED wording) not run to the end, and criteria 4 and 6 open; NEXT: when the owner opts in, run the three suites at one HEAD in short governed pieces (no single long run) and judge them against design §H.
- `PYRE_SITE_FOOD_REPAIR_COLONY_STARVES` — built; the site is now 3 colonists, fed, with the quicktest colony removed; NEXT: close it on the next short site build that reads every colonist fed after the rows (no full run).
- `PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE` — diagnosed: a late dive on a cold first burn, not flee; the fix direction is on the item; NEXT: implement the CheckForJobOverride on the BurnLine rising edge in C#, then run a cold-map probe.
- `SAFE_ADVANCE_MENU_DIAGNOSE_LUCKY_NULLREF` — filed; going to the menu mid-advance ends the run only via a caught NRE; NEXT: make safe_advance end cleanly on a game or map change, then probe it.
- `POND_RETURN_LEG_BUILD_WATER_GOES_HOME` — built and partly proven live; NEXT: run the channel-route leg and the occupied-bed refill delay as short checks.
- `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` — proposed (FOUNDRY); NEXT: build it offline; it unblocks the pond bed hollow.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Notes made with --owner-said/--by-card land in `ledger/events/OWNER.jsonl`, not the seat shard; commit both. (filed: lessons)
- `rimflow implemented --none-owed` makes an item terminally done even when live proof is owed. (filed: lessons)
- `modset_builder --restore` wrote FULL.LATEST instead of the owner's list; it now uses a swap marker and an md5 check. (see: Transient/night_20261013/modset_restore.md)
- Pass 7's colony starved during long tick runs; a clock SET simulates nothing but ages absolute-tick timers. (filed: lessons; see skills/rimbridge/references/silent-failures.md)
- The Man in Black fires through the incident queue even with the storyteller off. (see: Transient/night_20261013/quiet_profile.md)
- A second site build sent the game to the menu mid-run; the bridge concurrency guard now refuses that. (see: Transient/night_20261013/menu_drop.md)

## Closed since the last handoff (38)

- `PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED` — 365b428d7b
- `PYRE_SCORCH_YIELD_DIAGNOSE_FLAKY_HARVEST` — 365b428d7b
- `TELEMETRY_NONE_REPAIR_PHANTOM_FAILURES` — 7be154332ce5
- `CLOCK_SET_CALLERS_MIGRATE_DECLARE_FIRST` — 46eadf3f56
- `PYRE_RUINS_ASH_DIAGNOSE_TEN_THEN_TWO` — 380163e211
- `POND_BED_DESIGN_LAKES_ARE_TALL_CANALS` — dbdfef28f7
- `PYRE_SITE_VITALS_REPAIR_HALF_THE_COLONY` — dbdfef28f7
- `TESTENV_TOXIC_HARDEN_SITE_POISONS_ITS_GUESTS` — dbdfef28f7
- `TESTENV_VITALS_REPAIR_TICKSABS_SECOND_SOURCE` — dbdfef28f7
- `TESTENV_VITALS_HARDEN_LOADS_ARE_NOT_JUMPS` — dbdfef28f7
- `WATCH_WAIT_WIRE_SMALL_STEPS` — dbdfef28f7
- `RIVER_COLORS_FIRST_SCRIPT_1` — f5b3f4bc9d26
- `FLOODED_CANYON_FIRST_SCRIPT_1` — 8ca92b2aa6
- `FLOWWORKS_NORTHSTAR_BASELINE_RUN_1` — dbe92f0c92879477af71f45aaecb6de08e0db05a
- `THICK_LIQUID_CREEP_1` — dbe92f0c92879477af71f45aaecb6de08e0db05a
- `PYRE_REGROW_BUILD_A_WEEK_IN_MINUTES` — bc29bc5f6c
- `MAP_DROP_DIAGNOSE_MENU_MIDRUN_GHOST` — ecc7577e69f7
- `GSS_SWITCHES_PROVE_TWENTY_UNFLIPPED` — 6d19ccfa49a0
- `TESTENV_MODSET_RESTORE_WRONG_FILE` — 0ece8ec993a0
- `POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK` — c0216b47b0
- `LIQUID_HEAT_PUSH_1` — c0216b47b0
- `FLOOD_DEBIT_MEND_DEEP_CELL_ONE_LEVEL` — c0216b47b0
- `FLOOD_DRIVER_OWNERSHIP_CONTRACT_1` — c0216b47b0
- `FLOOD_SWITCH_RACE_MEND_ENGINE_OFF` — c0216b47b0
- `PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD` — c0216b47b0
- `PYRE_ANIMALS_DIAGNOSE_TEN_IS_NOT_TWELVE` — 0b603ed46aed
- `TESTENV_GUARD_UNSTICK_BLOCKS_ITS_OWN_SEQUEL` — 03fa69c87db1a3c97c344d09d376fde3344d35fb
- `TESTENV_SITE_BACKUP_REPAIR_READONLY_REUSE` — 03fa69c87db1a3c97c344d09d376fde3344d35fb
- `TANK_LOOP_PROVE_LIVE_DONE_TOO_SOON` — d76d4f55dc45267c5f971632baaa81dc21c1ffe0
- `TESTENV_QUICKTEST_HIVES_HARDEN_EMPTY_NEST` — 4f015f41a2e7
- `TESTENV_VITALS_HARDEN_FIXTURES_ARE_NOT_HIVES` — 4f015f41a2e7
- `TESTENV_MONOLITH_HARDEN_UNINVITED_GUEST` — 4f015f41a2e7
- `TESTENV_STRANGER_JOINS_HARDEN_LET_IT_END` — 4f015f41a2e7
- `TESTENV_FACTION_DIALOG_HARDEN_FIVE_KNOCKS` — e167f49523f0
- `TESTENV_GOVERNOR_STOP_DIAGNOSE_NO_NOTE_LEFT` — 4f015f41a2e7
- `TESTENV_INJURY_HARDEN_WHO_HURT_CAIT` — 4f015f41a2e7
- `SAFE_ADVANCE_PROVE_DISARM_ENDS_THE_RUN` — f9163831e0
- `COMPANION_STATIC_LAMBDAS_UNBLOCK_WITHOUT_GSS` — 0f40db2abe54

## Filed and still open (12) — the next seat's queue

- `PYRE_SITE_CLOCK_REPAIR_ASH_EXPIRES_FIRST` — Pyrelands site builder jumps the clock ~10 days past mapgen, so 6-9 day loose ash on ruins decays before ruins_scorched samples it (cause: 7f4f8f3f79 
- `PYRE_SITE_TEMP_REPAIR_PROBE_HIT_ROCK` — Pyrelands site builder's temperature preflight sampled a solid-rock cell and refused map B; sample an open, walkable cell.
- `PYRE_SITE_FOOD_REPAIR_COLONY_STARVES` — Pyrelands test sites start 6 colonists unfed with no food on a 56C summer map; long splits (120k-220k ticks) and main run C (439k->715k) starved all 6
- `VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL` — Measure the vitals monitor's overhead armed vs off on the 23-mod tier and the full list (GPT §5): busy pawn maps, arrivals, paused UI, long stepping; 
- `TESTENV_HIVES_HARDEN_RIVER_MAP_SQUATTERS` — FlowWorks river_site map carried a dormant insect Hive + GlowPod (vitals threat_structure, 04:28Z) during extension_proof: site prep should destroy hi
- `TESTENV_FLOODS_HARDEN_SEASON_CRASHES_PARTY` — 'Seasonal flooding' ThreatSmall letter on the FlowWorks river site map during extension_proof (04:29Z): storyteller incidents/conditions must be off o
- `FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY` — River extension returns_home / panning_draws_stock / flood_refill UNMEASURED on every pass 4-8 (SWEPT pending=0; pan=nothing). Classed SITE presumed: 
- `TESTENV_MEGAPEDE_HARDEN_GATECRASHER` — Test environment: a VFEI2_Megapede + 3 Spelopede (Insect) arrived on the FlowWorks golden site mid liquid_heat (safe_advance stopped 60/600); the site
- `TESTENV_BURROW_HEAT_HARDEN_COLONISTS_COOKED` — Burrow diag repeats (11 trials, ~8000 ticks at 52 C) killed 2 of 3 colonists and burnt the tracked grazer
- `TESTENV_BURROW_COLD_PROVE_RELOAD_PER_TRIAL` — Repeat fire trials on one map are warm (standing-burn window) so only the first is a cold dive; reload the fixture per trial
- `TESTENV_TRIALSITE_DIAGNOSE_NOBODY_HOME` — Test environment: NS_FlowWorks_TrialSite_v1 on ratchet_pilot+patches loads with NO living colonist on the current map (list_pawns: 0 colonists) and a 
- `SAFE_ADVANCE_MENU_DIAGNOSE_LUCKY_NULLREF` — safe_advance: a return to menu mid-advance ends the run via a caught NullReferenceException (abortWhy 'stepper exception') instead of the readiness ga

## Commits

```
b0dbd07e11 Companion proofs live without GSS: static-lambda tools answer; safe_advance disarm/menu end the run
0f40db2abe Companion: GSS-typed lambdas move to GssLambdaHome; build refuses a shared <>c naming an optional mod
edfce1aba0 Ledger: supersede duplicate companion-lambda item
ee4e237ec5 Code review: mark VitalsCore, SafetyCore, TransferChecks, UnitsVitals clean
f9163831e0 Night C# review: safe_advance no longer wedges after a disarm/TTL; refusal paths in quiet_site, time_set_ticks, ProofTank/Pump/Lip
154299de6e Ledger: quiet profile pass - close 7 TESTENV items, note 4, file TESTENV_TRIALSITE_DIAGNOSE_NOBODY_HOME
18b88b2cf5 Quiet profile live probe: evidence and write-up
e167f49523 quiet_site modal broker tracks each window by ID: VEF asks one faction at a time
f3aaa39a56 quiet_site modal broker waits for a click to land before the next round
4f015f41a2 Quiet isolated test-site profile: one shared profile + jawa/quiet_site, wired into site builders
ddbf0a520a Ledger: supersede duplicate burrow-cold item
4cdef00ebf Ledger: close tank-loop live proof and two TESTENV items
d76d4f55dc toggle_tank_loop stages 60 units (tank holds 80); live proof 5/5 PASS
03fa69c87d Guard refuses only an active foreign client; site backup reuse clears read-only copy
1816ce6d78 Ledger: close PYRE_ANIMALS_DIAGNOSE_TEN_IS_NOT_TWELVE as variance
0b603ed46a Pyrelands night live: animals 17/25/23 = variance; burrow dive delay is cold GotoWander, not Flee-first
1aca6b8216 lesson: implemented --none-owed is terminal done
c2beb1316e Ledger: file tank-loop live proof item
e2420abfa9 Ledger: tank-loop live check still owed
d2668c1df7 Ledger: tank_loop items implemented (live check owed)
... 60 more: git log --oneline 365b428d7b..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-10-13T08:51:52Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   pre-existing at session start, not this session's; left alone
 M Transient/mc_human_review/KEYSHEET.md   pre-existing at session start, not this session's; left alone
 M Transient/mc_human_review/keysheet.html   pre-existing at session start, not this session's; left alone
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   pre-existing at session start, not this session's; left alone
 M conversations/2026-10-12-1403-b0ee9afc.md   generated (conversations.py; hourly sweep commits)
 M deployed/config/ModsConfig.before-tier-bridge.xml   generated (modset_builder ModsConfig backups)
?? conversations/2026-10-02-1217-54206aec.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-02-1952-4b4a687b.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-02-2332-d58606e4.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-03-1458-7ed5ddfd.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-04-2105-400ef7dc.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-04-2219-962263b0.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-05-1426-fab8a134.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-06-0601-5ab77072.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-06-1305-ecebcb6f.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-0058-b305fb53.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-0059-c857706d.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-0120-033b16fc.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-0547-d6861da6.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-1520-6a6f7a30.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-0001-cc216258.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-0158-8aeef5fc.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-0215-c4ae9260.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-0217-3acaea39.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1348-bac7589f.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1411-2294fe53.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1411-3ffd55d0.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1413-52caf5c0.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1413-658e0588.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1414-b4b8553c.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1428-de9591de.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-09-0450-85e0a0f9.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-09-1308-818639f9.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-0040-5e2fd376.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-0049-58eabd09.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-0440-c71b568d.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-1341-91d07ad1.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-2102-71d8c9eb.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-11-0052-2f152d1c.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-11-1934-f086ce1a.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-11-1953-24347684.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-11-2000-edefebc8.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-12-0625-88710e84.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-13-0007-b342a8ee.md   generated (conversations.py; hourly sweep commits)
?? deployed/config/ModsConfig.before-gss-restore-20261010.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-flowworks_vepipe.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-ratchet_pilot.xml   generated (modset_builder ModsConfig backups)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   untracked art, not BENCH's (artpipe/FOUNDRY); left alone
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/   untracked art, not BENCH's (artpipe/FOUNDRY); left alone
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T034753.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T040637.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T041535.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T042312.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T050823.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261011T052325.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/GSS   stray path, not BENCH's this session; left alone
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T220702.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T230453.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261011T033650.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230218.json   generated harness output from tonight's GSS flip runs (not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230455.json   generated harness output from tonight's GSS flip runs (not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230639.json   generated harness output from tonight's GSS flip runs (not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T231027.json   generated harness output from tonight's GSS flip runs (not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T231203.json   generated harness output from tonight's GSS flip runs (not committed by design)
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   untracked art, not BENCH's (artpipe/FOUNDRY); left alone
```

