# FOUNDRY_REBOOT_HANDOFF_202610071234 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202610050845`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Offline belt is exhausted: every remaining item needs the bridge, the owner, or art. The live acceptance work is the lever now, and Transient/foundry_green_20261007.md + Transient/l2_failure_triage_20261007.md say exactly what is proven and what is not.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Decisions: Solar Mirrors remainder (several days, needs a scope check); art rulings for Gembug/Megapleura, hum primer, LivingBolt corpse; 3 Abyss + 2 facet-moth facings failed pipeline checks twice; PROVISIONAL numbers on kinetic arms (35% ruins, 5-12 shells, 120-tick window, shield drain 10), Wildsteam goodwill 50, volunteer quest window 4-6 days, burial thresholds 0.6/0.3. Cord/pit item answers: dew plants all five, scanner on every biome (done), Empire already can siege. Push-hook was fixed to check the pushed commit.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `ABYSS_DARK_MUFFLE_ALL_SOUNDS_1` — not started this window; listed by ledger; NEXT: re-read the item and probe whether it is still live, else drop it
- `ABYSS_LIGHTFALL_BROOD_WRECK_1` — built offline 6f4ca7660; NEXT: run L1 def read then L2 brood-lair scene on a minimal tier
- `ABYSS_SHEET_DONOR_PORT_1` — built offline 627a6aea5; NEXT: L1 read of the ported defs on a tier with the Abyss mod
- `ALPHA_ANIMAL_PORTS_REHOME_1` — open; not worked this window; NEXT: read the item and decide stale-drop or build
- `ART_LEDGER_SEAT_DEFAULT_1` — done 9c284892e; 82 misfiled events stay in BENCH.jsonl (append-only); NEXT: none needed unless crediting matters; close if still open
- `BILEWORM_CORPSE_ROT_1` — built offline aef4566f7; NEXT: L2 bileworm corpse-rot scene on a minimal tier
- `BIOME_KITS_PUSH_TO_TEST_1` — open; not worked this window; NEXT: read the item and run the GREEN-MIN sitting if a validated script exists
- `EMPIRE_ESCALATION_LADDER_1` — built 0179380c7; Empire already canSiege true; NEXT: L1 read plus five L2 rung quicktests
- `FEVERWOOD_BROOD_RANSOM_1` — campaign half built 81f360450; NEXT: six bridge checks: tank placement, free-the-young, goodwill, cask sale
- `FLOWWORKS_SLUICE_TWO_DOORS_1` — live pass: flow_doors 6/6, sluice playtest passes; NEXT: remove expectedFailUntil from the sluice scene in JawaBenchFlowWorksPlaytestScenes.cs and rebuild the DLL
- `MESSYCONDUIT_CABLE_PILE_LOOK_1` — built 8bab86beb; DLL rebuilt, not deployed; NEXT: deploy the GimmeSomeSlack DLL when the game is down, then run the A2-A3 L2 checks
- `RUSTCATHEDRAL_BASE_FINISH_BUILD_1` — built adbeaa649; NEXT: L1 plus L2 on the Rust Cathedral tier; seven checks
- `RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1` — built; art outstanding (Worn south facing failed in artpipe); NEXT: re-queue the failed facing, then L1 def read
- `SALVAGE_WRECKAGE_EVERYWHERE_1` — partial; waiting on 22 wreck renders and biome sittings; NEXT: install finished wreck_* renders via art ledger, then the remaining mechanics
- `SARLACC_SEEKER_ROOTING_1` — open from the prior handoff; not worked this window; NEXT: read the item and decide build or drop
- `STILLSAND_SKELETONS_REMAINDER_1` — built 225fd2245; giant-bone part blocked on DESIGN_MATERIALS_REVIEW_1; NEXT: L2 burial/strip scene once Stillsand map readiness is fixed
- `UNFINISHED_LINE_WORLD_FOUNDRY_1` — built 863f9089f; NEXT: L1 quest-def read then three L2 volunteer-quest checks
- `WEEPINGSTONES_CONDENSER_QUESTS_1` — built 1ed0cb8a3; NEXT: three in-game condenser-quest checks plus one load check

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
Autostash in ./publish leaves conflict markers in a dirty clone (see: Transient/foundry_offline_helper_20261007.md). Stillsand quicktest maps read 'map not ready 300 s after Regenerate' on every chain, cause unfound (see: Transient/foundry_green_20261007.md). Vanilla Invisibility-hediff NRE on a corpse aborts map updates; restart the game after it (see: Transient/foundry_green_20261007.md). WeepingStones forced-job pawns vanish (see: WEEPINGSTONES_HANDLER_VANISHES_1). Shell checks that call a failing check FAIL when the cause is test setup (see: Transient/l2_failure_triage_20261007.md).

## Closed since the last handoff (20)

- `MANTISTANIS_DONOR_ABSENT_1` — 2db4fb19919ef46c59e7cb8cef67f2d09263dd42
- `MYCOID_ART_OVERRIDE_DEAD_1` — 2db4fb19919ef46c59e7cb8cef67f2d09263dd42
- `GRAFFITI_LINKED_MARK_FIX_1` — ed70a915047780aaaed05322d43af48100e3b8fc
- `FEVERWOOD_OIL_FLASH_BARE_GROUND_1` — ee6e6dd1cbdc37a7e1b0df04b26099ac6f7d96c8
- `FLOWWORKS_NORTHSTAR_SITE_PREP_1` — 73d377946ff8f01e1fd6a39d38fd513f8c61e465
- `FLOWWORKS_PIT_PAWN_ROWS_RED_1` — b222e43f1e70cf1d3eae404e5ac29660af87ad98
- `DEF_DUMP_RECAPTURE_1` — 15072607325109d483785f8ad888e325bfe7e047
- `RESEARCHRETAG_HEARTH_VFET_OVERLAP_1` — 153582f76792e287b2362472a5b30d173419e0de
- `SUPERDEEP_PRISON_ROOM_1` — 73408b80e502
- `LIQUID_BODY_FLUID_IDENTITY_1` — 5d5e6cc12
- `PIT_FILL_EFFECTS_1` — eabc44700
- `PIT_DEPTH_DRAW_OFFSET_1` — 0d599e5cd
- `NORTHSTAR_RESULTS_JOIN_1` — 6dfd31920
- `LUMINOUS_PIGMENT_STARTUP_NRE_1` — e0cc57ab8
- `BURROW_TIMER_SAVE_LOAD_1` — b9217d8a4
- `PROOF_ALL_DURABLE_RESULTS_1` — 807ba7756
- `VOSSKA_SANDSWIM_GRAPHIC_WIRING_1` — 28b41ccf5
- `SELFTEST_RUNNER_SILENT_OOM_1` — ff20caec5
- `MESSYCONDUIT_STYLED_POLES_1` — 7edf12aa8
- `WYYYSCHOKK_IDENTITY_COLLISION_1` — 4583b5a75

## Filed and still open (29) — the next seat's queue

- `ABYSS_SHEET_DONOR_PORT_1` — Abyss sheet 2026-10-05: port 17 donor rows to owned RM_ defs under new names, wire the ruled art
- `NORTHSTAR_PROCESS_RETRO_1` — Northstar process retro after GimmeSomeSlack goes Green: what worked, update skills, build Python helpers
- `GIMMESOMESLACK_NORTHSTAR_VALIDATE_1` — Owner validates the seeded GimmeSomeSlack north star and views the sheet once (Green)
- `LEANINGSCRUB_SHEET_ART_REDO_1` — Leaning Scrub sheet: wiring, variants and design asks
- `NIGHTSIDEICE_SHEET_ART_REDO_1` — Nightside Ice sheet: redo art and Tauntaun canon wiring
- `RUSTCATHEDRAL_SHEET_ART_REDO_1` — Rust Cathedral sheet: LivingBolt redo art, roach size, installs
- `RUSTCATHEDRAL_LIVINGBOLT_WALL_FLIT_1` — LivingBolt flits on walls and surfaces: no mechanism exists, design owed
- `FLOWWORKS_VISUAL_PRINCIPLES_1` — FlowWorks look: owner's five visual rules (deep cuts as walls, dirt/stone faces, moving water, tar as liquid, scorched pit)
- `LANTERNDEEPS_SHEET_ART_REDO_1` — Lantern Deeps art sheet 2026-10-05: eye repaints, blinker redo, plant variants to install on return
- `MYNOCK_FLIPBOOK_FRAMES_1` — RSW_Mynock flies with no wing-beat: its 8-frame flight flip-book is owed art
- `WARSCAR_SHEET_DONOR_PORT_1` — Warscar donor rows: ruled art picks wait for owned defs
- `FLOWWORKS_CHECKOUT_SCOPE_1` — FlowWorks: ordinary features only in the on-request extension proof; walk lines lack coverage arrows
- `FLOWWORKS_TANK_LOOP_ROW_WRONG_1` — extensions toggle_tank_loop asserts a mechanic that does not exist: tankLoopEnabled gates the bottle pour-in/draw-out WorkGivers (WorkGiver_FillBottle
- `FLOWWORKS_PIT_OCCUPANT_HIDDEN_BY_LIP_1` — Visual (read from live shots 2026-10-06, DLL with visual principles 1-5): a pawn on a D=4 pit's SOUTH row (and a 1x1 pit) is drawn 1.2 cells south and
- `FLOWWORKS_SLUICE_TWO_DOORS_1` — Sealed sluice gate holds liquid; grate gate always passes it
- `FLOWWORKS_PIT_FALL_ONLY_FORCED_1` — Pit falls only when forced/blown in; enemies also when concealed
- `ART_LEDGER_SEAT_DEFAULT_1` — art ledger tool defaults to BENCH shard when no seat set; salvage wave-2 art events landed in BENCH.jsonl; plus push hook checks local HEAD not pushed
- `LIVINGBOLT_CORPSE_ART_1` — RM_LivingBolt corpse render (none exists; body graphic stands in)
- `QUICKTEST_POLICY_NRE_FULLLIST_1` — quicktest map will not start on the 613-mod list: NRE in ReadingPolicyDatabase.GenerateStartingPolicies (first exception); isolate the mod
- `BILEWORM_CORPSE_ROT_1` — Bileworm: corpses near it rot fast into corpse bile it drinks; colonists nearby feel the stench (description already promises it; VEF comps dropped at
- `HORIZON_CARAVAN_VANILLA_REFUSES_1` — Stillsand horizon_warns_then_arrives: vanilla TraderCaravanArrival also refused on the L2 site. Repro: regenerated Stillsand site, horizonWarningsEnab
- `MUDSWALLOW_PARENTHOLDER_GUARD_1` — Greentide MudSwallow guard fixed offline (ParentHolder skipped every spawned item; DLL rebuilt, not deployed). Live verify: deploy Greentide, rerun sw
- `JAWABENCH_DESTROY_PAWNS_1` — jawa/destroy_batch never removes pawns even with categories=Pawn ('1 pawn(s) left alone'), so Greentide _clear_hostiles and Cauldron kill_pawns are in
- `WEEPINGSTONES_HANDLER_VANISHES_1` — WeepingStones L2: every chain-spawned pawn (handler + target) left AllPawnsSpawned during forced jobs (13->11), all 7 FAILs; LeaningScrub dripping_sur
- `LEANINGSCRUB_STALL_SHARED_MOVE_1` — LeaningScrub stall: both animals (0.4 Thornhold + 0.7 Shirrel control) made the same +12,+12 move in the first 250 ticks in both L2 runs, then held. R
- `LEANINGSCRUB_CROWN_MOB_LIVE_1` — LeaningScrub crown mob: dustflutters ranged 23-70 cells with mob ON or OFF; CrownMob claims only idle mobbers. Repro: crown pad (anchor-45,+45), lock 
- `LEANINGSCRUB_SWEETLINE_SHED_LIVE_1` — LeaningScrub sweetline: mature tree shed 0 felt after +5.5 d. Repro: sweetline pad (anchor+45,+45), set_plants RM_SweetlineTree growth 1, time_set_tic
- `MODCHECK_ULTRAFAST_CLOCK_STALL_1` — modcheck Ultrafast wait never advances TicksGame (0 successes in 47 result JSONs; LeaningScrub smother + bloom order_pawn waitTicks timeouts). Repro: 
- `BRIDGE_LOCK_CROSS_CLONE_RACE_1` — rimflow bridge take can't see the other clone's unpushed take: BENCH and FOUNDRY both held the bridge 2026-10-07 10:47/10:48Z and FOUNDRY killed two B

## Commits

```
4615cb909 acceptance: FlowWorks sluice done, biomes/flowworks sittings, green log
c78842824 modcheck: empty-string setting reads back null (Greentide/suite); acc_biomes tier
0bc006c2a file BRIDGE_LOCK_CROSS_CLONE_RACE_1; BENCH releases bridge to FOUNDRY
378bbf152 FULL.LATEST: add ExplosiveKnockback, KineticArms, GimmeSomeSlack (613)
8552e43bc restart #2 progress: second load killed by FOUNDRY tier cycling; live checks blocked
d85ad84c2 restart #2 progress: load killed by an unbridged FOUNDRY modcheck run, relaunched
4378527cf acceptance: GREEN-MIN for 6 mods; suite bool-case compare; TrophyCraft instrument gaps -> UNMEASURED
967a7bee8 acceptance: L1 passes for 6 unmeasured items, findings, green log
00161611b L2 failure triage 2026-10-07 + 8 live items filed
b6daa7175 LeaningScrub script: 6 L2 FAILs were setup faults or harness stalls (SCRIPT/HARNESS)
74e7f18f3 WeepingStones script: job/flora checks go UNMEASURED when the handler vanished (was FAIL / false PASS)
ee35ebd20 SWBestiary: drop dependency on retired mandrake.rm.lanterndeeps; add acc_l1x tier
cf4e103fa Restart #2: 613-mod list (FULL.LATEST + ExplosiveKnockback, KineticArms, GimmeSomeSlack)
b168259cf ledger: BENCH bridge take for full restart #2
23550555d Greentide DLL rebuilt (MudSwallow guard fix)
2daf513e3 Greentide: MudSwallow skipped every spawned item (MOD); 3 script setup faults (SCRIPT)
c1218ab09 Stillsand: sun checks read a stale shade grid (SCRIPT); loomma sunstruck could be deleted at 0 (MOD)
03c2cf180 CreatureBehaviors script: invisible walker used a self-expiring hediff (SCRIPT)
2dc400065 GSS kinetic sway progress: deploy blocked by locked DLL
177261fc7 GSS: kinetic blasts swing aerial spans instead of cutting them (Q3)
... 625 more: git log --oneline 0d65607fc..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-07T12:33:55Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
?? conversations/   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ModsConfig.before-tier-acc_biomes.xml   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ModsConfig.before-tier-acc_l1x.xml   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T142015.xml   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T161529.xml   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ns_flowworks_backup.20261002T070221.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ns_flowworks_backup.20261005T142015.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? deployed/config/ns_flowworks_backup.20261005T161529.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_dry_dirt.png   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_dry_stone.png   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_scorched_dirt.png   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_scorched_stone.png   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261005T232949.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261005T233603.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T000710.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T001245.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T002141.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003132.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003420.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003624.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003701.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003821.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T004655.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T010918.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T011022.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T011246.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T020515.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021000.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021144.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021337.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021908.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T033840.json   FOUNDRY (this clone: modlist backups and run artifacts, untracked by design)
```

