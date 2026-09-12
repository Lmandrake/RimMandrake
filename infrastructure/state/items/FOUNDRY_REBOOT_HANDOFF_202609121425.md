# FOUNDRY_REBOOT_HANDOFF_202609121425 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609120305`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A bare `git commit -m "..."` — EVEN AFTER `git add <your own files>` first — still commits
whatever else happens to be staged in the shared index at that instant. This bit at least
four separate commits tonight (content was always intact, just misattributed under the
wrong message) despite CLAUDE.md already saying "explicit paths, never git add -A." The
fix that actually stopped it, once every dispatch prompt required it: put the SAME paths
on the `git commit` line itself — `git add path/a path/b && git commit path/a path/b -m
"..."` — never rely on `add` alone. No sweep occurred in any commit using that form after
it was mandated partway through the night. This should go in CLAUDE.md's git section
directly, not just a lesson entry — the current prose ("explicit paths, never git add -A")
reads as satisfied by add-then-commit, and it is not.

## What the owner should see

- **HELIX_TELLUROX_BUILD_1 found `HorrorWastes` has ZERO cast rows** — the whole biome
  currently wild-spawns on mod defaults, not a hand-authored roster. Populating an entire
  un-cast biome's ecosystem from one hand-invented row would be a content call, not
  something to improvise solo overnight — left for the design loop.
- **Two real canon-drift contradictions found** by `CANON_CONSISTENCY_CHECKER_1`'s first
  real run against the full `design/Jawa/` corpus: `forbidden_mods.md`/`required_mods.md`
  restate the same ruling with wording that's already drifted apart, and
  `the_rust_cathedral.md`/its own amendment-draft companion have done the same. Both are
  genuine RULED-vs-RULED disagreements, not tool noise — worth a reconciliation pass.
- **VAULT_DUNGEON_BUILD_1's shipped V6 letter text doesn't match what you actually
  accepted** — `design/Jawa/worldbuilding/dungeons_arc_spec.md` §3.10 records specific
  owner-approved wording from 2026-09-11, but `RUT_VaultThaw.xml`'s live text differs
  throughout (not a rewrite, just drifted). Flagged, not touched — not this session's file
  to hand-fix.
- **The four commit-sweep incidents tonight** (see "one thing to carry forward" above) all
  came from a shared checkout with a concurrent BENCH/Fable window — worth checking that
  window's own commit habits if this keeps happening, since the mandated-pathspec-on-commit
  fix only applied to what I could control (my own dispatch prompts).
- Shipped deliberately, flagging: `RUST_CATHEDRAL_MECHANICS_1`'s new hum-mood mod was
  deployed but left DISABLED in `ModsConfig.xml` on purpose — it's new/unverified, so it
  never touched the running game tonight. Enable it only after a live test.
- `PLANETARY_BEAUTY_LOADSCREENS_1` was dropped per your own live verbal ruling this
  session ("Terminate project. We will do this manually.") — recorded in case that wasn't
  meant to also kill the item's queue entry, only the auto-build attempt.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `ASHFALL_SPIRE_LANDMARK_1` — re-blocked, `needs=offline`. Both candidate tiles are
  Impassable hilliness; `LandmarkDef.IsValidTile` refuses them and a bare marker would
  ConfigError forever. Next action: author real content (icon+mutator+nameMaker) offline
  before attempting placement again — this is not a bridge problem.
- `DROIDWORKS_WIPE_SEVERITY_1` — `needs=deploy`. Root cause fixed (droids can never
  satisfy `InBed()`, silently blocking every whole-pawn Droidworks surgery recipe, not
  just the wipe) via a Harmony prefix on `Pawn.CurrentlyUsableForBills`. DLL rebuilt,
  never deployed — locked by the running game all night. Next action: deploy once the
  game is down, then live-test that a memory-wipe bill actually gets picked and completes.
- `INHABITED_AUGMENTATION_BUILD_1` — 12/14 archetypes built, 12/14 wired (4 more wired
  tonight: trading outpost, tiny garrison, dead caravan, beast pens), 0/14 placed on
  Ash'karr (bridge was never free during any pass that touched this). 8.7/8.8 genuinely
  blocked on a missing Rimefeller/VHGE buildability strip (doesn't exist, would need its
  own build). 8.9/8.11 need their own lint sweep before an export seed. 8.12 needs a
  BENCH/owner call on which host it damages. 8.14 blocked on the whisper subsystem. Next
  action: a placement pass once the bridge is genuinely free, or continue wiring 8.9/8.11.
- `MLIE_FAUNA_ABSORPTION_1` — defName-drift sweep run tonight: 0 drift, all 91 species
  confirmed live under exact donor names — corrected worklist at
  `infrastructure/state/facts/mlie_wave_c_worklist.json`. Ported 2 more (Iriaz, Mudhorn);
  89 of 91 remain. Next action: continue porting in small complete batches straight from
  the worklist — no re-sweep needed, it's fresh.
- `NINEFOLD_MISSING_EVENT_HOOKS_1` — build half done long ago (98863702); tonight
  live-verified Sh'kaar (organic battle-kill) and Ohm (droid spawn), 5/9 → 7/9 gods now
  live. `CheckOrdinalContract()` confirmed clean. Mob'Unloo (trade) and Ta'Baa (launch)
  have NO existing bridge tool to trigger them — `needs` is currently unset/undecided.
  Next action: a small `rimbridge-companion` addition to force a trade and a launch, then
  finish the last 2 gods.
- `RUST_CATHEDRAL_MECHANICS_1` — 2/6 sections done before tonight (walls, roaches);
  added §1 hum-mood as its own new mod tonight, deployed but left DISABLED in
  `ModsConfig.xml` on purpose (new/unverified). §3 living bolts, §4 eel-fishing, §5
  deep-drill response still entirely untouched. Next action: enable+live-test hum-mood,
  or start §3.
- `SETTLEMENT_VERBS_WAVE_1` — salvage-law was already live; walkable-commerce built and
  added tonight (2/4 families live). Crime suite and social-fabric deliberately NOT
  attempted — both need a cast-NPC/vendor concept from `SETTLEMENT_VISIT_LOOP_1`, itself
  still open; building them now would be shallow stubs. Next action: wait on that
  dependency, or rescope crime/social-fabric to not need it.
- `SETTLEMENT_VISIT_LOOP_1` — engine offline-complete, deploy already in sync (verified
  byte-exact, no redeploy needed), deep re-verified against RimSage tonight (~20 files,
  zero bugs). Only the full arrival→teardown loop live observation remains. Next action:
  one bridge session with a colony that can run the whole loop start to finish.
- `SHOKKWEAVE_SOLE_SOURCE_1` — rename/strip done long ago; web-cutting and nest-raid
  routes built AND live-verified tonight. Found and fixed a real bug live:
  `wakeUpIfAnyTargetClose` defaulted false, so "wakes on approach" never fired — fixed
  (one XML field), deployed, but defs bake at process start so it needs the NEXT restart
  to re-verify. Trader-stock zero-proof and the border creep-web route (needs
  `WEBWORK_KIT_BUILD_1`'s FrontCreep, which now exists but isn't wired into this mod yet)
  remain. Left `needs=owner` per the closing report — worth double-checking that's the
  right tag vs. `needs=bridge` for the next-restart re-verify.
- `TILE_STRUCTURE_DESIGNS_1` — "whispers" mechanism now understood (rides an EXISTING
  tile mutator via vanilla's own random selector, unlike "promises," which are new
  hand-placed ones) — 3/22 whisper rows built (Never Was / Rootstock / Choir Wind), 19/22
  honestly declared MISSING-MECHANISM (no nameable anchor, or the content is its own
  incident/quest design — a real design gap, not padding). The coverage-lint tool itself
  was extended to measure whispers mechanically instead of a hardcoded 0/22. Next action:
  author more whisper anchors as spec content grows, or treat the 19 MISSING-MECHANISM
  rows as a design question.
- `VAPOR_PLACEMENT_CLEANUP_1` — magma-vent orphans (5 tiles) and ancient-vent non-ruin
  outliers (24 tiles) cleaned up live tonight. Helixien re-seat correctly NOT touched
  since its mechanism is still unmeasured. Next action: measure the helixien mechanism
  before touching it.
- `VAULT_DUNGEON_BUILD_1` — 3 grammar templates re-verified byte-identical/clean
  tonight; deliberately did NOT write new dialogue since the sibling
  `VAULT_THAW_QUEST_FAMILY_1` build already ships complete letter text for all six vaults
  (would have duplicated it). All 6 real-site hand-finish passes remain explicitly
  owner-joint work per this item's own doctrine, not solo work. V5's landmark (tile 37)
  is authored but not placed live. Next action: a joint hand-finish session, or place V5
  once bridge time allows.
- `VAULT_THAW_QUEST_FAMILY_1` — found why 2/3 V6 branches were inert (no vanilla code
  ever sent the `RUT_SleepersWoken`/`RUT_SleepersLooted` signals those quest nodes wait
  on); built `MapComponent_VaultSleepers` to send them on the right casket-state
  transition. Built and validated offline, NOT deployed (StructureInjectionsRUT DLL
  locked by the running game all night) and NOT live-tested. Next action: deploy once the
  game is down, then live-quicktest the V6 Umbra vault's wake/loot/leave branches.
- `WORLD_NAME_FIXES_1` — Colony renamed to "Zeddo's Salvage Yard" live tonight (done,
  matches your verbatim ruling). The other renames (Fall Line Barrens + Scald Spine
  near-dups, four Ascendant Helix settlement renames) are RULED per commit `7138c5455`
  ("All seven world renames RULED") but that commit landed the SPEC only — the world
  edits themselves are NOT yet applied live. Next action: apply the remaining ruled
  renames live — every decision is already made, this is pure execution.

## Traps learned

All filed to `LESSONS_INBOX.md` tonight, summarized here:
- `git commit -m` after `git add <files>` (no pathspec on the commit line itself) still
  commits the WHOLE shared index — 4 occurrences tonight; fix is pathspec on both add AND
  commit. See "one thing to carry forward" above.
- Three separate background bridge agents ended their own turn to "wait" for a load/
  notification instead of blocking synchronously in a foreground poll loop — each sat
  idle until I noticed and resent the correction. Already-documented doctrine, agents
  keep reaching for it anyway under a genuinely long wait; say it explicitly in every
  bridge-dispatch prompt, don't assume it's remembered.
- `jawa/step_game_ticks` silently times out (~2,800 ticks/~10s call) and returns
  `success:false, status:"timedout"` in the payload while the outer envelope still reads
  `Success:true` — must be looped with a real `ticksGame` re-read, never trusted for one
  big request.
- A ThingDef missing `thingClass` crashes `ReadingPolicyDatabase.GenerateStartingPolicies`
  on EVERY game construction, not just when that def is used — `validate_patch.py` does
  not catch it.
- A self-referencing `ResearchProjectDef` prerequisite (injected by a third-party mod's
  own runtime patch operation) causes an uncatchable stack overflow in vanilla
  `ResearchManager.FinishProject` (no cycle guard) — silent process death, no managed
  exception. An XML patch removing the self-ref is NOT sufficient if the donor mod
  re-injects it at a different load point; the durable fix is a Harmony prefix on
  `FinishProject` itself. Verify via a live `get_defs` read after a fresh restart, never
  by trusting the patch file exists.
- `Pawn.CurrentlyUsableForBills()` requires `InBed()` for every billable pawn — droids
  never satisfy this (non-organic, no rest drive, bed-hauling workgiver refuses them),
  silently blocking every whole-pawn Droidworks surgery recipe at once.

## Closed since the last handoff (22)

- `MUDSWALLOW_LIVE_LIST_FIX_1` — eb5826bf0b23f267769f29dfc95f1f156d536c19
- `HUB_LAMP_TIME_FIX_1` — a49c5ea7774d623903f5e91013b5f6255339f318
- `VAPOR_TERMINATOR_GEYSER_FIX_1` — 0ba73d7a25a91a440ca63ab4afdbace3dea529e1
- `FLOOD_CANYON_BIOME_1` — e319ec73f74ffd145e285343a4b0861ea0d3d599
- `MODLIST_RESTORE_AND_BATCH_DEPLOY_1` — e93f9b9fd7849d6b9bc5d5e1c30e12823cdee6ea
- `COMPANION_SILENT_FAILURE_HARDENING_1` — 26cd324b7793b67d12bdfd5e75d23873e5f69e1d
- `CHECK_CANON_WATER_RULE_1` — ce9a1ca542b9ac87c7f91770d37faa0897a45a3e
- `CANON_CLAIM_TAGGING_1` — c53845fdf2dbf5ec08345557e63beb02c1dc2e1b
- `CANON_CONSISTENCY_CHECKER_1` — 7629d0884392daad945a96334a40bcace48622d2
- `WRECKAGE_VERMIN_SPAWN_1` — 84c4afa20381cf577e774242a7b828cb8b8d74c7
- `HEALTH_UNMEASURED_HEADLINE_1` — 785b67074605507e583a9a141a9166b15cbf79e7
- `HUB_TAB_PUBLISHER_MIGRATION_1` — 51813d54edd500203c73ef7933d0fbe1abf86e90
- `LIQUID_TYPES_SPIKES_1` — 4457f42c18f343e45d8d1f05fe850bd515a230a9
- `TIBANNA_SOURCE_CUT_1` — 16ae5500fe21d599e13e2e3fa3c5fd4eae7f11eb
- `GIZKA_HOLD_HOOK_SPIKE_1` — 415669d91a4c40770e4c756a0f4e3f38bb5a6158
- `SARLACC_WORLDMAP_RELOCATE_1` — f28cd7521cb26d410d2a60fac258081176f5be68
- `BUILDING_THEFT_HAULER_1` — 0ce4c1c30
- `NINEFOLD_FIRE_HOOK_RATELIMITED_1` — 133a257c52201c78bfa368b92acfc4a801717c15
- `DROID_SYSTEM_BUILD_1` — 5736f2888e204afd86ac854d63d5f188ba7065bc
- `QUICKTEST_POSTSETUP_CRASH_1` — fa95b3fdc93410c85a54f241e1c1be58b574ded9
- `SHRINE_GUARDIAN_BIOME_GATE_1` — 4d73c5a804e822a7390ab01ad32f98fd48417a71
- `WEBWORK_KIT_BUILD_1` — 421ee05dba2e959df76023a47d878a3c945a2d7d

## Filed and still open (5) — the next seat's queue

- `VAPOR_PLACEMENT_CLEANUP_1` — Vapor emitter part-4 cleanup per the 2026-09-12 ruled rules: magma-vent 5 out-of-lock tiles, ancient-vent ruin-only audit, swamp/ruin gas re-seat, Poi
- `SCALD_DIVING_MOD_1` — Diving mod, v1 (owner: 'make the diving mod v1 content now!!'): RimMandrake-tier diving mechanic — hunt/commune at the Scald's deep center, priced in 
- `ASHFALL_SPIRE_LANDMARK_1` — Place The Spire landmark (Ashfall Research Base site): thin black needle, disc pad near top, intermittently visible through Scald turbulence — live pl
- `SARLACC_HABITAT_BUILD_1` — Build the accepted sarlacc design (sarlacc_native_habitat_draft.md, ACCEPTED + all forks RULED 2026-09-12): RSW-tier mod, Devourer-modeled swimmer, ro
- `WORLD_NAME_FIXES_1` — World name fixes (owner 2026-09-12): rename player settlement 'Colony' to 'Zeddo's Salvage Yard' (ruled, verbatim on event); Fall Line Barrens + Scald

## Commits

```
3f7352f6b rimflow: sync ledger/queue views after tonight's FOUNDRY session, bridge released
424f8c743 NINEFOLD_MISSING_EVENT_HOOKS_1: live-verify Sh'kaar and Ohm, 5/9 -> 7/9 gods live
ccff212c5 WEBWORK_KIT_BUILD_1: live-verify FrontCreep on a bordering-biome map, close SHOKKWEAVE_SOLE_SOURCE_1: live-verify web-cutting + nest raid; fix wake-on-approach bug
421ee05db Health hook cycle outputs
7b7137b98 BENCH reboot handoff 202609121357: card-sitting hinge, three owner sittings queued, traps recorded
7138c5455 All seven world renames RULED (owner cards): Site Aurek, Farside Station, Site Cresh, Cold Stores, The Breaks, Cratercrown, Zeddo's Salvage Yard — WORLD_NAME_FIXES_1 spec complete
bb9438816 SHRINE_GUARDIAN_BIOME_GATE_1: live-verify on a repainted Desert quicktest map, close
4d73c5a80 rimflow: sync ledger/queue views after QUICKTEST_POSTSETUP_CRASH_1 close
fa95b3fdc QUICKTEST_POSTSETUP_CRASH_1: live-verify the XML self-prereq fix was insufficient; real fix is a Harmony guard
76025543f Mark MandrakePatches About.xml CLEAN (new loadAfter entry for tonight's research self-prereq fix, correctly documented)
bd35a33b5 rimflow: sync ledger/queue views after DROID_SYSTEM_BUILD_1 close
5736f2888 DROID_SYSTEM_BUILD_1: fresh minimal-list spawn/NRE proof; item's reopen premise was stale
b6b5d5ba2 QUICKTEST_POSTSETUP_CRASH_1: fix RR_ElectricityBasics self-referencing prerequisite
daf8e2592 HELIX_TELLUROX_BUILD_1: live spawn/butcher proof done, re-blocked on HorrorWastes cast wiring
9fb08f576 rimflow: sync ledger/queue views after tonight's close/needs wave
65b2dc41c File QUICKTEST_POSTSETUP_CRASH_1; re-block 3 items on it
3e05542a6 CreatureBehaviors: rebuild DLL -- committed copy was stale vs source
133a257c5 Closes: NINEFOLD_FIRE_HOOK_RATELIMITED_1
0ce4c1c30 Closes: BUILDING_THEFT_HAULER_1
e9cce8686 Live world batch: SARLACC relocate, Colony rename, VAPOR Part-4 cleanup
f28cd7521 ASHFALL_SPIRE_LANDMARK_1: live-checked, re-blocked needs=offline
257bbbc7f fix: RUT_Webwork_{Anchor,Web,Gutter,Nest} missing thingClass crashed EVERY game load
a0936110a Code review: 6 tonight's-work files clean, no fixes needed
f3754dac7 rimflow: note on DIRTY_CODE_REVIEW_STANDING_LOOP_1's cleaning pass
682f5c0ac Code review: LanternDeeps mineshaft/darkness files clean
cd536a36a LanternDeeps: rebuild DLL (no code change, verification build for review)
ea656f205 Mark ShokkweaveEconomy About.xml CLEAN after fix
b0d3ba6fc ShokkweaveEconomy: correct stale About.xml claim (FrontCreep now exists); mark StructureInjectionsRUT.csproj CLEAN after review
02648abb2 Droidworks: rebuild DLL, mark Droidworks.csproj clean
d9f505eae rimflow: note on DIRTY_CODE_REVIEW_STANDING_LOOP_1's cleaning pass
7c69183af DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean tonight's dashboard/tooling fixes
9e5089f22 DIRTY_CODE_REVIEW_STANDING_LOOP_1: fix silent-zero ledger failure in project_maturity_dashboard.py
62c3d3c9a Code review: StructureInjections.csproj clean
c89c85687 StructureInjections: rebuild DLL (no code change, verification build for review)
d261cc238 Code review: RimProperty PropertyTuning.cs and RM_Property.csproj clean
ee8057a78 RimProperty: remove dead AnimalTheft MTB constants from PropertyTuning
17d4028dc Code review: ShipShields particulate/predictive/landing-advisory files clean
291b653cf ShipShields: rebuild DLL (no code change, verification build for review)
73ee4d1bb DROIDWORKS_WIPE_SEVERITY_1: root cause fixed - droid patients can never be InBed()
72034dd1f Deploy ShipShields DLL (not in live ModsConfig, no lock); SHIELD_MODS_LEVERAGE_1 now needs=bridge
ea5d07d5c SHIELD_MODS_LEVERAGE_1: finish particulate screen, build predictive-failure alert and landing advisory
220eef337 SETTLEMENT_VISIT_LOOP_1: staleness already resolved, deep re-verify vs RimSage finds no bugs
6e08a7e7e rimflow: BUILDING_THEFT_HAULER_1 reclaim/start/needs=bridge, plus queue re-render
3d4c98650 BUILDING_THEFT_HAULER_1: mechanism re-verified clean, DLL deploy confirmed already done
8a20ae7b2 VAULT_DUNGEON_BUILD_1: tally pass, no new creative content this round
e93bb33d6 NINEFOLD_FIRE_HOOK_RATELIMITED_1: still deploy-blocked, mod DLL locked live
415669d91 Close GIZKA_HOLD_HOOK_SPIKE_1: live-confirm Scenario.PostGravshipLanded fires
f9f45c391 INHABITED_AUGMENTATION_BUILD_1: wire 4 more built archetypes (8.4/8.6/8.10/8.13)
80244e7f8 RUST_CATHEDRAL_MECHANICS_1: build §1 hum-mood system (2/6 sections now, walls+roaches prior)
3eced2c32 LANTERN_DEEPS_INJECTION_1: ruined-mineshaft entrance + darkness mechanic
d0e3b19ab VAULT_THAW_QUEST_FAMILY_1: build the missing WAKE/LOOT signal sender for V6
97416ab49 SETTLEMENT_VERBS_WAVE_1: build walkable-commerce verb (2/4 families now live)
999b1aa0a TILE_STRUCTURE_DESIGNS_1: whisper batch 1 - engine + 3/22 rows wired
d4d359683 World rename proposals: Helix sites + two feature near-dups, SW-precedent grounded
cc6692c8f SHOKKWEAVE_SOLE_SOURCE_1: build web-cutting + nest-raid harvest routes
040cc28df canon.yml settlements: live census landed (96, owner card); WORLD_NAME_FIXES_1 filed (Zeddo's Salvage Yard ruled verbatim)
16ae5500f Close TIBANNA_SOURCE_CUT_1: fix a CherryPicker-crashing comment, verify both cuts live
5fc19bff1 WORLDMAP_FINAL_REVIEW_1: capture full-planet STARE screenshot set
e2b1262d3 MLIE_FAUNA_ABSORPTION_1: defName-drift sweep + Iriaz/Mudhorn ported
09c2eb0b1 Ledger: close LIQUID_TYPES_SPIKES_1
4457f42c1 WORLDMAP_FINAL_REVIEW_1: evidence pack recorded; STARE + verdict remain for the owner sitting
190484852 WORLDMAP_FINAL_REVIEW_1: night audit report — features/regions 0 mismatch, terminator fix confirmed live, 283 ancient-vent violations quantified, sarlacc landmark counts flagged
a0b7c4b21 Ledger: close CSV_REGION_SYNC_1 (all 809 region mismatches resolved)
0b3c6d937 CSV_REGION_SYNC_1 complete: Abandoned Mines 34 tiles landed from live feature read (22 Ashfall + 12 Notch), freeze re-stamped; night world dumps committed
c56a541e8 SHRINE_GUARDIAN_BIOME_GATE_1: build + validate the ambient shrine guardian gate
a2ca0eb73 Lessons: map parallel-spawn agent IDs from results, not order
08b909d33 WAR_LAB_CRATER_HOOK_1: wire CompIgniteCraterOnDestroy to a new reactor-core def
3a3596e8e rimflow: note real landing commit for HUB_TAB_PUBLISHER_MIGRATION_1's close
8ff50a8be Repoint artpipe + maturity publishers to the dashboard hub
51813d54e Surveyor-misdirection quest spec (three deception verbs, GM-fired offer); both night quest specs registered in INDEX
e887d0192 Flood-witness invitation quest spec (prose, per ruled design; alert-unlock flagged unruled)
942e51465 Art verdict sheet v2: 95/147 lanes with true original-vs-regen side-by-sides (89 extracted from live textures); 52 no-original lanes listed with reasons
27cbded5f Owner AFK: "I'm going to bed, afk. Go as far as you can. Keep subagents going!"
98ab47464 rimflow: sync ledger for DIRTY_CODE_REVIEW_STANDING_LOOP_1 note
45e009211 mark-clean: RM_CompVerminNest.cs, RM_ShipVermin.csproj
daaf1cd31 mark-clean: check_canon.py, selftest_check_canon.py, doc_claims.py
af13037d4 doc_claims.py: flush the table before absorbing trailing prose with no blank line
785b67074 Fix codebase_health headline lying '0 clean' on an all-unmeasured run
31431ae8e rimflow: sync ledger for SARLACC_HABITAT_BUILD_1 claim/block
91a75fd0f SARLACC_HABITAT_BUILD_1: build the sarlacc's native-habitat creature/mechanics (RSW tier)
4f657da7e Art verdict sheet v1 (147 lanes) + generator and verdict-applier; originals resolution pass owed for 141 redo lanes
12cd5c306 TIBANNA_SOURCE_CUT_1: cut the non-beldon tibanna sources (CARD T1)
5f4f56066 Health rebuild after git-lock-starved run (1669 green, 0 unmeasured); hub v10; HEALTH_UNMEASURED_HEADLINE_1 filed
cd320df9c Note: CANON_CONSISTENCY_CHECKER_1 close content landed in 21b30f26a
84c4afa20 Note: WRECKAGE_VERMIN_SPAWN_1 close content landed in 21b30f26a
21b30f26a Hub: retheme embedded health page to the brown palette (retheme_health.py); iframe backgrounds off white; published v9
7629d0884 Hub: embed full health/maturity pages as iframed tabs; art tab gains unresolved-review-sheets links (artsheets subcommand + manifest); published v8
bdebe751f Sarlacc design ACCEPTED (owner 2026-09-12): all forks ruled, Devourer-modeled swimmer, RSW tier; spec struck in part; deep_desert ban-5 carve-out under the freeze; SARLACC_HABITAT_BUILD_1 replaces design item
16f42b74b CANON_CLAIM_TAGGING_1: Phase 0 canon tagging in doc_claims.py
c53845fdf Fix check_canon [water] rule matching any 25% regardless of context
ce9a1ca54 SCALD_DIVING_MOD_1: v1 Deep Diving mod (blocked, not closed)
5782ab18e Spire plot-discussion prep: threads, tensions, four candidate shapes + sitting agenda
d56e28654 Canon storage adopted (Phase 0+1, owner card); three FOUNDRY items filed; checker water-rule fix filed
9b45ff076 Regenerate project tracking (owner request): all four hub tabs re-sourced, lamps GREEN, hub republished v7
26cd324b7 Close MODLIST_RESTORE_AND_BATCH_DEPLOY_1 (criteria met 2026-09-09, still healthy); note Ikee-half-dead finding on IKEE_MYNOCK_ART_REGEN_1
e93f9b9fd Drop PLANETARY_BEAUTY_LOADSCREENS_1: owner terminated it live this session
05ffb83af Planet status: remaking -> frozen (owner card; the freeze's own condition met) — planet rules bite; FactionSlate 14->13 stale count; gizka free-gift IN v1
c9bc11ff7 Miasma strange tier ruled in full: five hediffs selected (Swarm-marked, Salt-blooded, Loam-lunged, Mother-dreamed, Fever-tempered); Tide-reader cut
b20a3ebc6 GIZKA_HOLD_HOOK_SPIKE_1: gravship-landing hook identified, live proof owed
facc17f68 Ledger: close MECHANICS_CARDS_SITTING_1
6d13d4b07 Card sitting 2026-09-12 complete: PF weather ratified, injection fauna = envelope union; sitting record; ASHFALL_SPIRE_LANDMARK_1 filed
f9a1329c9 rimflow ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 tail-wave note
c92b4eaf6 Mark 10-module DIRTY_CODE_REVIEW_STANDING_LOOP_1 tail wave CLEAN (Greentide, LoreStages, Ninefold, RaidRedesigner, SacredGraffiti, DesertVehicleReskin, Shokk, LanternDeeps, RestrainingBolts, StructureInjectionsRUT)
fd3bafa39 Liquid+Scald cards ruled: Scald FRESH (rivers flow OUT — wrong inflow premise deleted), steam-catch both+toggle, diving is v1 (SCALD_DIVING_MOD_1), coolant Other bucket, films in v1
3b8e16ddf Mark 5 leftover .csproj files CLEAN (missed in the hydro/dune batch pass)
ce01a5a8a rimflow ledger sync: close FLOOD_CANYON_BIOME_1, block WRECKAGE_VERMIN_SPAWN_1, bridge released
083dea2c7 Mark RiverColors and ShipMemory .csproj files CLEAN (missed in earlier pass)
582ebeaf7 rimflow ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 five-module wave note
53cb421d2 Mark Aftermath/FluidCanals/ManyWaters/MovingDunes/ProximityHatch CLEAN after full-file review
5f12f476e Fix MovingDunes influx double-scaling on the drift-speed slider
fa13c2092 rimflow ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 tail-wave note
d9bac2fc3 Mark Pyrelands/RustChrome/StructureInjections/WeatherSuite/JawaRules CLEAN after full-file review
2467e0a2d rimflow ledger sync: RiverColors/ShipMemory clean-review note on DIRTY_CODE_REVIEW_STANDING_LOOP_1
94349307e Mark RiverColors + ShipMemory Source CLEAN after full-file review
1cff9edb0 Mark DroidRepairJobs QuestNode + Antiquities job/workgiver CLEAN after full-file review
e758283f4 Snapshot the live campaign mod list before the flood/shipvermin test swap
d5afc7409 WRECKAGE_VERMIN_SPAWN_1: fix two live-confirmed defects, spawn still unproven
e319ec73f FLOOD_CANYON_BIOME_1: live-verify the chime/flood/recede cycle and the master toggle
3469c9625 Mark Inhabited Source (InhabitedFateWorker, MapComponent_InhabitedWatch, Patch_BeggarsFromPool) CLEAN after full-file review
6cbc02a1e Mark RimUtinni/FungalSoilTrade Source (GenStep_ScatterFungalGround, MapComponent_RotFungalDistress, csproj) CLEAN after full-file review
5f3ba0678 rimflow ledger sync: SWBestiary clean-review note on DIRTY_CODE_REVIEW_STANDING_LOOP_1
5a13e0abc rimflow ledger sync: Visibility clean-review note on DIRTY_CODE_REVIEW_STANDING_LOOP_1
e28106030 Mark SWBestiary Source (ThoughtWorker_IkeeNearby, CompKilnBelly, CompLightAversion) CLEAN after full-file review
4b5c50715 Fix CompKilnBelly: doseFeedDef was never checked, any CompKilnFeed item counted as a dose
fe34bf6ea Mark RimMandrake/Visibility Source module (3 files) CLEAN after full-file review
b4a195534 rimflow ledger sync: PlantGrowth clean-review note on DIRTY_CODE_REVIEW_STANDING_LOOP_1
2467077e3 Mark RimUtinni/PlantGrowth Source module (3 files) CLEAN after full-file review
5f995fb3f Mark RimUtinni/LongHunger Source module (3 files) CLEAN after full-file review
e2333e565 Fix LongHunger: nextPulseAt ignores durationMultiplier for the first tremor
ac5d19d92 Mark RustCathedralWalls Source module (3 files) CLEAN after full-file review
67fdbff6b BrainWorms: rebuild DLL with tonight's 3 fixes (stale-cold expulsion check, dead expelledWorm setting, ETA tooltip ignoring rate multiplier)
1056c8a11 rimflow ledger sync: BrainWorms clean-review note on DIRTY_CODE_REVIEW_STANDING_LOOP_1
456c555e5 Mark BrainWorms module CLEAN after full-file review
6e94c55d0 Fix BrainWorms: stale cold-flag surgery race, dead expelledWorm field, ETA math
e7bf384ea ShipShields: rebuild DLL with the thermal-veil PushHeat double-divide fix
38e75a3fd Mark ShipShields Source module (4 files) CLEAN after full-file review
fdbba895e Fix ShipShields thermal veil: apply room temp delta directly, not via PushHeat
0f6497f66 rimflow note: JawaIonWeapons clean-review summary on DIRTY_CODE_REVIEW_STANDING_LOOP_1
aeccad6b9 Mark JawaIonWeapons module (6 files) CLEAN after full-file review
635efab7f rimflow note: Graffiti Source clean-review summary on DIRTY_CODE_REVIEW_STANDING_LOOP_1
433aea6f5 Mark Graffiti Source module (6 files) CLEAN after full-file review
76a58422a rimflow note: ScavengerEvents clean-review summary on DIRTY_CODE_REVIEW_STANDING_LOOP_1
982aa8ce7 Mark PyrelandsMechanics Source module (7 files) CLEAN after full-file review
2679d79d8 Mark ScavengerEvents module (7 files) CLEAN after full-file review
d2db1fa70 ScavengerEvents: fix ShipBreak's silently-empty loot corpse; correct a mislabeled DropThingsNear param
84a2a0e39 Mark TitanicCreatures CorpseSite/Footprint/Wake module (7 files) CLEAN after full-file review
7c9b0e9ef TitanicCreatures: fix broken thick-roof pathfinding avoidance
afe33b556 Sump beast, Forge tower/rain/beldons, Tibanna T1+T2 ruled (owner sitting 2026-09-12); TIBANNA_SOURCE_CUT_1 filed
457e31588 rimflow note: CreatureBehaviors clean-review summary on DIRTY_CODE_REVIEW_STANDING_LOOP_1
64ea45985 Mark CreatureBehaviors module (7 files) CLEAN after full-file review
20ce46f24 Mark EnvironmentalHazards module (9 files) CLEAN after full-file review
0637431c1 EnvironmentalHazards: apply hazardDamageMultiplier where the retrofit missed it
0ba73d7a2 VAPOR_TERMINATOR_GEYSER_FIX_1: zero SteamGeysers_Increased at/past the terminator
60d204c4a Mark Pits module (8 files) CLEAN after full-file review
744da3686 Fever Wood cards 2-3 + Sump cards 1-2 ruled: Tenant rescue window, 40-cell fear, moat fire cascades, traps disarmable
831201d4c Miasma cards ruled (strange tier real: 2-3 hediffs owed; surge kills unfloored crops; creche marked-only); Fever Wood plumbing factions fine
4b440f019 Pits: fix stale build-command path in csproj header comment
2d76cdd96 Ledger note: RimProperty code-review wave closed
a8216aed8 Gizka cards ruled (tunable slow default, 15 silver, cull guilt in, HOLD for hold-hook); spike filed as the gate
db6532a4d Mark RimProperty's 10 dirty files CLEAN after full-file review
c62d11c4c RimProperty code review: fix suspicion-prune half-life mismatch, stale build-path comments
2752470f8 rimflow: log Droidworks code-review wave note
720f2f8a9 Mark Droidworks module (21 files) CLEAN after full-file review
d0c985e6a Droidworks: fix garbled log tag in BoltCorePatches error messages
8f86f501a canon.yml helix_lineage: splice_motive ruled — the key over the Cathedral's machines; works, or seems to; cost held open
8990896f2 Ashfall base cards ruled: literacy-ladder gating, Helix key-motive (works, or seems to), landmark = The Spire; campaign function TBD
f921a1e78 KYBER_TRADE_PLOT_1: Mod Settings retrofit for the kyber quest content
90059a2a1 KYBER_TRADE_PLOT_1: build the Homestead visit + donation/smuggle quests, block on GM-layer Heat
822b6fa48 CATHEDRAL_PLAYER_CONCEALMENT_ARC_1: all five cards ruled, build unblocked
803cec81c Cathedral A2-A5 RULED (owner cards 2026-09-12): reveal scope minimal; exposure is a real losable outcome; surveyor quest IN; sale exposure by volume
99295c49c Cathedral A1 RULED: the Utinni knows — she receives the Rakatan transponder on dead frequencies; ledger: close MUTATION_MODIFIERS_SURVEY_1
f4a40fd1d Contagion mutation deck RULED (owner cards 2026-09-12): custom gene, vanilla removal risk, 50/50 large-variance rolls
0660a11f1 MOD_OPTIONS_RETROFIT_1: record progress, block pending live verification
7a14e5ed2 MOD_OPTIONS_RETROFIT_1: real Mod Settings for 46 mods (Greentide's cross-biome opt-in included)
4c98263c4 mark-clean: WRECKAGE_VERMIN_SPAWN_1 ShipVermin/Utinni files
96156db67 rimflow: claim/block WRECKAGE_VERMIN_SPAWN_1
5b0fefcf5 WRECKAGE_VERMIN_SPAWN_1: wreck-anchored vermin nest mechanism
1325cfac6 mark-clean: AmbientShrineGuardians.cs, GeothermalDensityField.cs
4cd37218f MOD_OPTIONS_RETROFIT_1: settings gate for UtinniPatches ambient shrine doctrine and geothermal density field
a99079e96 mark-clean: HUB_LAMP_TIME_FIX_1 dashboard hub scripts
a49c5ea77 HUB_LAMP_TIME_FIX_1: fix hub dashboard timestamp/staleness bugs
cb2e69890 FLOOD_CANYON_BIOME_1: standalone RimMandrake Flooded Canyon biome mod
338d886c4 rimflow: claim/close MUDSWALLOW_LIVE_LIST_FIX_1
eb5826bf0 mark-clean: MudSwallow Scan() fix and RUT_Greentide.xml wildPlants guards
7949f4eac MUDSWALLOW_LIVE_LIST_FIX_1: fix live-list mutation bug, guard Greentide wildPlants
74c87278e Ledger: close CANON_PLANET_CENSUS_1
d49aa5f03 CANON_PLANET_CENSUS_1: land the corrected planet census; frozen CSV declared sole census source (owner card 2026-09-12)
869a4dd61 Vapor rulings landed (owner card sitting 2026-09-12): 3 ratified + PoisonForest gases + helixien junker rule; cleanup filed for FOUNDRY
2e68e1674 CSV_REGION_SYNC_1: land five region renames + freeze re-stamp (owner card yes, provenance verified)
7c8ccb757 CANON_PLANET_CENSUS_1: owner caution — CypreJungle/GreaterSwamp are pending-swap donor names, not canon rows
0881775a6 CANON_PLANET_CENSUS_1: frozen-CSV re-census closes the gaps (29 biomes explained, rivers 298, water 6.62%)
593c9a619 WRECKAGE_VERMIN_SPAWN_1: vermin spawn from wreckage (owner 2026-09-12, verbatim)
90f35057f Card-sitting agenda (46 pending decisions); correct two stale awaits-ruling claims — explosive design's core rulings landed 2026-09-10
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-12T14:21:47Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 D infrastructure/artpipe/pending/dactillion_v1_east.json
 D infrastructure/artpipe/pending/dactillion_v1_north.json
 D infrastructure/artpipe/pending/dactillion_v1_south.json
 D infrastructure/artpipe/pending/fanback_v1_east.json
 D infrastructure/artpipe/pending/fanback_v1_north.json
 D infrastructure/artpipe/pending/fanback_v1_south.json
 D infrastructure/artpipe/pending/grank_v1_east.json
 D infrastructure/artpipe/pending/grank_v1_north.json
 D infrastructure/artpipe/pending/grank_v1_south.json
 M infrastructure/artpipe/registry.jsonl
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? infrastructure/artpipe/daemon_run_20260911_105041.log
?? infrastructure/artpipe/done/aa_frostmite_v1_east.json
?? infrastructure/artpipe/done/aa_frostmite_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.manifest.json
?? infrastructure/artpipe/done/boma_v1_east.json
?? infrastructure/artpipe/done/boma_v1_east.manifest.json
?? infrastructure/artpipe/done/boma_v1_north.json
?? infrastructure/artpipe/done/boma_v1_north.manifest.json
?? infrastructure/artpipe/done/boma_v1_south.json
?? infrastructure/artpipe/done/boma_v1_south.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_east.json
?? infrastructure/artpipe/done/borcatu_v1_east.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_north.json
?? infrastructure/artpipe/done/borcatu_v1_north.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_south.json
?? infrastructure/artpipe/done/borcatu_v1_south.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_east.json
?? infrastructure/artpipe/done/cinderwing_v1_east.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_north.json
?? infrastructure/artpipe/done/cinderwing_v1_north.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_south.json
?? infrastructure/artpipe/done/cinderwing_v1_south.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_east.json
?? infrastructure/artpipe/done/dactillion_v1_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_north.json
?? infrastructure/artpipe/done/dactillion_v1_north.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_south.json
?? infrastructure/artpipe/done/dactillion_v1_south.manifest.json
?? infrastructure/artpipe/done/duskram_v1_east.json
?? infrastructure/artpipe/done/duskram_v1_east.manifest.json
?? infrastructure/artpipe/done/duskram_v1_north.json
?? infrastructure/artpipe/done/duskram_v1_north.manifest.json
?? infrastructure/artpipe/done/duskram_v1_south.json
?? infrastructure/artpipe/done/duskram_v1_south.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_east.json
?? infrastructure/artpipe/done/emberscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_north.json
?? infrastructure/artpipe/done/emberscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_south.json
?? infrastructure/artpipe/done/emberscythe_v1_south.manifest.json
?? infrastructure/artpipe/done/fanback_v1_east.json
?? infrastructure/artpipe/done/fanback_v1_east.manifest.json
?? infrastructure/artpipe/done/fanback_v1_north.json
?? infrastructure/artpipe/done/fanback_v1_north.manifest.json
?? infrastructure/artpipe/done/fanback_v1_south.json
?? infrastructure/artpipe/done/fanback_v1_south.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_east.json
?? infrastructure/artpipe/done/featherfeel_v1_east.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_north.json
?? infrastructure/artpipe/done/featherfeel_v1_north.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_south.json
?? infrastructure/artpipe/done/featherfeel_v1_south.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_east.json
?? infrastructure/artpipe/done/fenshear_v1_east.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_south.json
?? infrastructure/artpipe/done/fenshear_v1_south.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.manifest.json
?? infrastructure/artpipe/done/grank_v1_east.json
?? infrastructure/artpipe/done/grank_v1_east.manifest.json
?? infrastructure/artpipe/done/grank_v1_north.json
?? infrastructure/artpipe/done/grank_v1_north.manifest.json
?? infrastructure/artpipe/done/grank_v1_south.json
?? infrastructure/artpipe/done/grank_v1_south.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_east.json
?? infrastructure/artpipe/done/grubhorn_v1_east.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_north.json
?? infrastructure/artpipe/done/grubhorn_v1_north.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_south.json
?? infrastructure/artpipe/done/grubhorn_v1_south.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_east.json
?? infrastructure/artpipe/done/hawkbat_v1_east.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_north.json
?? infrastructure/artpipe/done/hawkbat_v1_north.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_south.json
?? infrastructure/artpipe/done/hawkbat_v1_south.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_east.json
?? infrastructure/artpipe/done/insectomorph_v1_east.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_north.json
?? infrastructure/artpipe/done/insectomorph_v1_north.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_south.json
?? infrastructure/artpipe/done/insectomorph_v1_south.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_east.json
?? infrastructure/artpipe/done/kinrath_v1_east.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_north.json
?? infrastructure/artpipe/done/kinrath_v1_north.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_south.json
?? infrastructure/artpipe/done/kinrath_v1_south.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_east.json
?? infrastructure/artpipe/done/mycolith_v1_east.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_north.json
?? infrastructure/artpipe/done/mycolith_v1_north.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_south.json
?? infrastructure/artpipe/done/mycolith_v1_south.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_east.json
?? infrastructure/artpipe/done/ollopom_v1_east.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_north.json
?? infrastructure/artpipe/done/ollopom_v1_north.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_south.json
?? infrastructure/artpipe/done/ollopom_v1_south.manifest.json
?? infrastructure/artpipe/done/orray_v1_east.json
?? infrastructure/artpipe/done/orray_v1_east.manifest.json
?? infrastructure/artpipe/done/orray_v1_north.json
?? infrastructure/artpipe/done/orray_v1_north.manifest.json
?? infrastructure/artpipe/done/orray_v1_south.json
?? infrastructure/artpipe/done/orray_v1_south.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_east.json
?? infrastructure/artpipe/done/pekopeko_v1_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_north.json
?? infrastructure/artpipe/done/pekopeko_v1_north.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_south.json
?? infrastructure/artpipe/done/pekopeko_v1_south.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_east.json
?? infrastructure/artpipe/done/scarrend_v1_east.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_north.json
?? infrastructure/artpipe/done/scarrend_v1_north.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_south.json
?? infrastructure/artpipe/done/scarrend_v1_south.manifest.json
?? infrastructure/artpipe/done/shiro_v1_east.json
?? infrastructure/artpipe/done/shiro_v1_east.manifest.json
?? infrastructure/artpipe/done/shiro_v1_north.json
?? infrastructure/artpipe/done/shiro_v1_north.manifest.json
?? infrastructure/artpipe/done/shiro_v1_south.json
?? infrastructure/artpipe/done/shiro_v1_south.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_east.json
?? infrastructure/artpipe/done/slagmaw_v1_east.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_north.json
?? infrastructure/artpipe/done/slagmaw_v1_north.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_south.json
?? infrastructure/artpipe/done/slagmaw_v1_south.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_east.json
?? infrastructure/artpipe/done/sludrin_v1_east.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_north.json
?? infrastructure/artpipe/done/sludrin_v1_north.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_south.json
?? infrastructure/artpipe/done/sludrin_v1_south.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_east.json
?? infrastructure/artpipe/done/verdaunt_v1_east.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_north.json
?? infrastructure/artpipe/done/verdaunt_v1_north.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_south.json
?? infrastructure/artpipe/done/verdaunt_v1_south.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_east.json
?? infrastructure/artpipe/done/vornskyr_v1_east.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_north.json
?? infrastructure/artpipe/done/vornskyr_v1_north.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_south.json
?? infrastructure/artpipe/done/vornskyr_v1_south.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_east.json
?? infrastructure/artpipe/done/whisperbird_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_north.json
?? infrastructure/artpipe/done/whisperbird_v1_north.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_south.json
?? infrastructure/artpipe/done/whisperbird_v1_south.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.manifest.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.manifest.json
?? infrastructure/artpipe/failed/fenshear_v1_north.json
?? infrastructure/artpipe/failed/fenshear_v1_north.manifest.json
?? infrastructure/artpipe/registry.jsonl.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
```

**Attribution**: the ~180 `infrastructure/artpipe/{done,failed,pending}/*` and
`registry.jsonl`/`throughput.jsonl`/`registry.jsonl.lock` lines are the standing
`artpiped.py -N 3` daemon's own live churn (the BELT art-regen floor requirement) —
not mine, not a task, running continuously and expected to always show dirty. The
`Transient/codebase_health*` and `infrastructure/dashboards/hub/data/health.json`/
`infrastructure/state/codebase_health_last.json` lines are from a health-report
regen mid-session, also not mine, harmless. `defs.sqlite`, `deployed/config/
ModsConfig.before-tier-stagedlore.xml`, the three `design/Jawa/worldbuilding/
review/serve_*.log` files, and `infrastructure/state/cherrypicker/CherryPicker.
PRESWAP.20260911_234759.xml` are pre-existing scratch/backup artifacts from other
sessions tonight (BENCH and Fable), not this window's. Nothing here was mine to
commit or clean up.

