# BENCH_REBOOT_HANDOFF_202611130629 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611130137`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner's looks drive the pit work, and each look is now a stored record: every defect he reports goes into `design/RimMandrake/validation_holding/` when reported, and nothing from it is wired into a validation ladder until the ladder is fully defined and regenerated (his ruling, 2026-11-12 ~9:35 PM PST). A detached helper cannot be messaged after launch: a late correction means relaunching it with an amended brief, or a follow-up helper.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- The situation brief for his return, opened for him: `D:\ClaudeWork\rimmandrake\conductor\situation_20261112_2235.md`. Read it first; it is the ranked list.
- The game is UP, PAUSED on keeper `UNDER_LIQUID_LAW_AFK_20261112c` (FlowWorks and Gimme Some Slack at origin/main fe7c271f4b: round 2, water colour, geyser hot tub). His look is owed: big pits (SW corners 10,30 29,30 48,30 67,30 10,10 29,10 48,10), hot tub at 111,230, geyser row z=112, matrix at 120,200. Review note `D:\ClaudeWork\rimmandrake\conductor\afk_20261112_night\live\REVIEW_ME.md`.
- Conductor's own look at the overview capture: 2 m to brim read as blue water; the 0.5 m pit looks like the dry one and the 0.5 m to 1 m step is abrupt; the muffalo corpse reads crisp at every depth; dark rectangles under drowned furniture.
- ops-watch was NOT switched on although he chose it by card: the full sweep still shows 37 FAIL and 6 CRASH of 1,605, 22 new since the 03:00 nightly. He should say: on anyway, or another clean-up first.
- Explosive Knockback live proof did not run: the SteveDesktop queue cannot deploy a proof build, and the Outer Rim blast scene does not exist. One certification question for him is in `D:\ClaudeWork\rimmandrake\conductor\carryover_20261112\ek\STATE_AT_STOP.md`.
- Anomaly found unattended: colonists walking a natural river channel take a bruise every few hundred ticks (one fell to 56%); cause unknown, vanilla or ours (RIMMANDRAKE_FIND_RIVER_SWIM_BRUISES_FUEGO_HURT_FIVE_TIMES).
- The Designer cannot loop overnight: the Dispatcher that launches it has been paused since 2026-11-06 and the 2x-cap park and third-refusal stop were each watched refusing.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE` -- AFK live run done; game paused on `UNDER_LIQUID_LAW_AFK_20261112c`; fails filed (battery bar and bolt over tar, human corpse head crisp, shadow rectangles under water, spill arrives all at once, soaker invisible in a deep pool); NEXT: when he has looked, append his objections to `design/RimMandrake/validation_holding/` and give the filed fails to one Opus rm-builder, then redeploy.
- `RIMMANDRAKE_ALLOW_MEDIUM_FURNITURE_ON_PIT_FLOOR` -- detached Opus builder still running (flat things cast no shadow box, pit floor carries its ground's support, proof hooks ProofPitLabel and ProofOverlays built, more in flight); nothing of it deployed; NEXT: run `python3 src/RimMandrake/rimflow/detached_helper.py status`, read `D:\ClaudeWork\rimmandrake\conductor\afk_20261112_night\build\STATE_AT_STOP.md` when it ends, then deploy at the next restart and walk its LIVE_LOOK_CHECKLIST.md.
- `RIMMANDRAKE_PROVE_GSS_SWITCHBOARD_DENSE` -- detached Opus helper running (GSS census, 7 FAIL rows, batched setting reads, SteveDesktop proof); NEXT: read `D:\ClaudeWork\rimmandrake\conductor\carryover_20261112\gss\STATE_AT_STOP.md` when it ends and bring its questions to him by card.
- `RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES` -- detached Opus helper running (SteveDesktop results, Pyrelands scenes, HugeThings five Designer questions, FlowWorks toggles, findings fold, tick-burst table); NEXT: read `D:\ClaudeWork\rimmandrake\conductor\carryover_20261112\biomes\STATE_AT_STOP.md` when it ends; card the HugeThings questions; act on its verdict on the uncommitted HugeThings kernel diff.
- `RIMMANDRAKE_SWEEP_WATER_SOLVERS_ON_BIG_MAPS` -- recommendation published (`design/specs/water_solver_decision_2026-11-12.md`, local-inertial); four owner questions ready and read by the Conductor; NEXT: put `D:\ClaudeWork\rimmandrake\conductor\water_models_20261112\QUESTIONS.md` questions 1-4 (water clock, waves, map size, groundwater) to him on one card and record the answers with --by-card.
- `RIMMANDRAKE_INVENTORY_VALIDATION_SCHEMES_BEFORE_ANY_LADDER` -- five card answers written into validation_map_and_rules.md (0fe13e054f), flyer paused-read guard landed, nightly clean-up done; ops-watch left OFF, publish-gate state unread by the Conductor; NEXT: read steps (c) and (d) of `D:\ClaudeWork\rimmandrake\conductor\validation_inventory_20261112\STATE_AT_STOP_enact.md`, then ask him by card: ops-watch on with the reds listed, or another clean-up pass first.
- `RIMMANDRAKE_DEPLOY_KNOCKBACK_DRAWING_STORAGE_OPEN` -- census, review and the explosion-mods close landed; the Archmagi game copy still holds the retired closed-container patch; NEXT: run the deploy command written in `D:\ClaudeWork\rimmandrake\conductor\carryover_20261112\ek\STATE_AT_STOP.md` at the next Archmagi restart, and put its one certification question to him by card.
- `RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS` -- T4, T6 closed; T5 partial; T10 owes two skills; T7, T8, T9-cache not built; truth table in `D:\ClaudeWork\rimmandrake\conductor\carryover_20261112\designer\TRUTH_TABLE.md`; NEXT: launch one Opus rm-builder on T5's wiring (automatic launch from criteria_suspect and the fresh-instance rejudge), then T7 and T8.
- `RIMMANDRAKE_SINK_GEYSER_INTO_PIT_BUBBLING_HOT_TUB` -- built 1eaef24497 and proven live by state read (sinks, bathable liquids, generator caps, survives reload); the soaker and vent are invisible in deep water (RIMMANDRAKE_SHOW_SOAKER_IN_DEEP_POOL_FURR_VANISHED); bubble art is a placeholder; NEXT: after his look at the tub at 111,230, give the soaker item to the builder that takes the other live fails.
- `RIMMANDRAKE_PIN_OWNER_LOOK_DEFECTS_AS_NAMED_TESTS` -- holding store in place (a029c244cd), early tests kept unwired, ingest item filed and blocked on the ladder; `owner_look_regressions.py` ran live once: 1037 PASS, 137 FAIL, 2 BLOCKED; NEXT: append each new owner look to the store; build nothing more until the ladder is defined.
- `RIMMANDRAKE_PREFLIGHT_TICKETS_BEFORE_ANY_TOKEN_IS_SPENT` -- spec published 9b61b770b892, untouched this window; NEXT: card him the six questions in spec section 9, then file the first three build tickets it names.
- `RIMMANDRAKE_EXTEND_PLAYER_TRUTH_SWEEP_LADDER_WAS_ONE` -- untouched this window; NEXT: ask him whether the sweep stays, then give it to an Opus rm-builder.
- `RIMMANDRAKE_FIX_CLIMB_SLOW_OUTLASTS_LADDER` -- live rows pass, his look owed (ladder pits in save EK_SITTING_STATION4_FLYING_SHELVES_20261112); NEXT: ask him to order a climb there and say if the slow part matches the ladder, then close with --owner-said.
- `RIMMANDRAKE_PROVE_FLOWWORKS_FILL_AGAINST_DEPTH_METRES` -- no bug; NEXT: ask him the part-notch question, record, close.
- `BENCH_REBOOT_HANDOFF_202611130137` -- its pointers not named above (Whittle account line, coverage-loop stop live check, validation-ladder builds held by his holding ruling, swale repaint, artpipe find hang) stand as written there; NEXT: settle each against the ledger with `handoff.py --wake`.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A detached helper cannot be messaged; an addendum file in its folder is not read (filed: LESSONS)
- `rimflow file --owner-said` refuses a question as authority; file on the Conductor's authority and record his later instruction with `note --owner-said` (filed: LESSONS)
- In-game screenshot mode (F11) throws away every click and hides the HUD; it looked like a dead selector (see: `infrastructure/state/lessons/20261113T030256Z-BENCH-screenshot-mode-eats-clicks.md`)
- The SteveDesktop test queue can only deploy the release DLL, so proof-build scenes cannot run there (see: item RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE)

## Closed since the last handoff (9)

- `PYRELANDS_TEXT_FIX_ENGINEERED_NEVER_SAID` — 8fb9f7f2b6
- `RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_JUDGE_BRIEFS` — deb663480bbd
- `RIMMANDRAKE_CENSUS_KNOCKBACK_STORAGE_OPEN_CLOSED` — c20328a876
- `RIMMANDRAKE_UNJAM_FINDINGS_FOLD_THREE_ITEMS_ONE_NAME` — d986a87f908b
- `RIMMANDRAKE_TESTQ_DEPLOY_MEMO_SKIP_UNCHANGED` — 6f4c65fc7f
- `RIMMANDRAKE_TESTQ_PREFLIGHT_REFUSE_BEFORE_THE_GAME` — 5b84a35699
- `RIMMANDRAKE_FIX_CRITERIA_BULLETS_BREAK_PROOF_PARSE` — 4e59b77b27
- `RIMMANDRAKE_SEED_JUDGE_CALIBRATION_FROM_CORPORA` — a52ff877e6ee
- `RIMMANDRAKE_ROLE_FILES_NAME_CONDUCTOR_RULING` — ad403fd090

## Filed and still open (53) — the next seat's queue

- `RIMMANDRAKE_ADD_PIT_LABEL_STATE_READER_MOUSEOVER_HAS_NONE` — A static [proof] method returning PitLabelAt(x,z) so a live run can read the cell label text a player sees (today only the mouseover patch can)
- `RIMMANDRAKE_SINK_GEYSER_INTO_PIT_BUBBLING_HOT_TUB` — Digging a pit on a steam geyser lowers the geyser to the pit floor; a filled pit bubbles over it and nearby pawns get hot-tub benefits like the Hot Sp
- `RIMMANDRAKE_UPDATE_LOOKS_ROUND_TAR_ASSERT_AFTER_DARKENING` — selftest_flowworks_looks_round.py is RED: line 93 still demands a neutral grey tar tint (r==g==b), but 441c321a20 made tar the warm near-black (0.07,0
- `RIMMANDRAKE_ALIGN_CORPSE_LIQUID_COVER_SKEWED_TWIN` — Corpse liquid cover is rotated off its body; head and edges show through tar. Live 2026-11-12 (FlowWorks cd3a3e243c26): BP3 2 m water, the Muffalo cor
- `RIMMANDRAKE_COVER_BOOKS_UNDER_LIQUID_NOVEL_READS_THROUGH_TAR` — Books (class Book) draw crisp under liquid. Live 2026-11-12: Novel at 82,100 in BP6 (1.5 m tar) draws fully crisp; ProofSubmerge there reads kind=item
- `RIMMANDRAKE_SINK_HOSES_AND_OVERLAYS_TORCHES_BURN_IN_TAR` — Hose ropes, torch flames and power-off icons draw crisp over liquid. Live 2026-11-12: in every wet big-pit copy the RM_HoseReel hose rope (FlowWorks' 
- `RIMMANDRAKE_TINT_PIT_WATER_READS_AS_WATER_NOT_MUD` — Pit water reads as dim brown floor, not water, at every depth. Live 2026-11-12 after the retune (Darken 0.25, DeepOpacity 0.5): matrix D8 F1..F8 and b
- `RIMMANDRAKE_LET_GROUND_DRAIN_ALL_FIND_SPILL_EMPTY_CLICK` — God-mode drain-all on ground refuses once a part-drain emptied the clicked square. Live 2026-11-12: overflow ON, Pour 152,102 tar 10000 L OK; Drain 15
- `RIMMANDRAKE_FIX_MOD_SETTINGS_FIELD_STATIC_CLASS_TRAP` — jawa/mod_settings_field throws on a static settings class. Live 2026-11-12: typeName=RimMandrake.FlowWorks.Sheet.RM_SheetSettings field=sheetOverflowE
- `RIMMANDRAKE_CLEAN_NIGHTLY_SWEEP_ONCE_THEN_RED_RINGS` — One clean-up of the always-red nightly sweep (RED 29 of 29 nights; 44 reds on 2026-11-12: 26 repo-wide guards broken by unrelated commits, 8 stale fix
- `RIMMANDRAKE_RECOUNT_INVENTORY_KERNELS_ONE_FILTER_THREE_ANSWERS` — validation_inventory_2026-11-12.md quotes kernel/fuzz counts from three different filters (§0: 72 ran, 71 passed; table row: 81 PASS, 1 UNMEASURED; a 
- `RIMMANDRAKE_CORRECT_INVENTORY_SKIPPED_MEANS_TIER_NOT_CACHE` — validation_inventory_2026-11-12.md §2 defines SKIPPED as 'skipped on unchanged evidence', but the 3 SKIPPED of 2026-11-12 are deployed-tier tests not 
- `RIMMANDRAKE_RECOUNT_NEVER_BUILT_ONE_SAID_THREE_LISTED` — validation_inventory_2026-11-12.md §0 counts 1 designed-never-built scheme while §4 lists the shared in-game scene runner and the bridge validation ob
- `RIMMANDRAKE_REWORD_STOPPED_A_FREEZE_IS_NOT_A_PAUSE` — validation_inventory_2026-11-12.md labels three schemes 'STOPPED with Relentless on 2026-11-06', mixing the 2026-11-06 freeze card (no new machinery) 
- `RIMMANDRAKE_STRIP_FOUNDRY_ACCEPTANCE_PROSE_RETIRED_TWICE` — False prose about acceptance testing: CLAUDE.md calls Relentless' game_prove lane (relentless_live_round.py) 'the acceptance sweep for every mod' thou
- `RIMMANDRAKE_DRAW_GEYSER_PLUME_BUBBLE_ART_PLACEHOLDER_IN_USE` — Real art for the sunk-geyser bubble plume; today it reuses RM_Fleck_LiquidBubble (Biotech vat bubble) as a placeholder; install only via art.py instal
- `RIMMANDRAKE_FIX_LIQUID_REGISTRY_DRIFTED_FROM_ITS_TABLE` — selftest_liquid_looks.py red on origin/main e6c3749f36: RM_LiquidDefRegistry.xml no longer matches the generate_liquid_suite.py table. Acceptance test
- `RIMMANDRAKE_FIX_NORTHSTAR_MOCK_RUN_RED_ON_MAIN` — northstar/selftest_extensions.py red on origin/main e6c3749f36: 'clean mock run not green'. Acceptance test: python3 src/RimMandrake/FlowWorks/northst
- `RIMMANDRAKE_REMOVE_DARK_SQUARE_AROUND_SUNK_GEYSER_UNWELCOME_BOX` — A geyser on a pit floor draws inside a darker square the size of its 2x2 footprint (capture underliquid_20261112_evening\live\captures\geyser_pit.png,
- `RIMMANDRAKE_PIN_OWNER_LOOK_DEFECTS_AS_NAMED_TESTS` — Every defect the owner reported in the 2026-11-12 pit looks gets a named regression check that fails on the build he saw: offline where possible, else
- `RIMMANDRAKE_ADD_OVERLAY_PROOF_HOOK_LAW_CANNOT_SEE_ICONS` — Proof hook: overlays, ropes, flames and the corpse cover report the alpha they drew vs the under-liquid law (ProofSubmerge cannot see them). Acceptanc
- `RIMMANDRAKE_REFUSE_OWNER_DEFECT_CLOSE_WITHOUT_REGRESSION` — rimflow close refuses an owner-reported defect without --regression <path::row> or --no-regression "<reason>". Acceptance test: in the item's first no
- `RIMMANDRAKE_REALIGN_FLOWWORKS_PROOFS_AFTER_UNDER_LIQUID_LAW` — FlowWorks proof fixtures behind the under-liquid law and new settings: tier mod sets, 4 new settings fields, RM_GeyserPitSettings source, LINES_CASES 
- `RIMMANDRAKE_REFILE_TWILIGHTSEA_COMMISSION_THREE_YOUNG_COLOCLAWS` — Extra-art commission: RM_TwilightSea owes 3 RSW_ColoClawFish young jobs (east/north/south); rerun plan and refile the biome (queues art). Parked on th
- `RIMMANDRAKE_REPAIR_NORTHSTAR_DRIVER_FIXTURES_COUNTS_DRIFTED` — Northstar driver fixtures drifted: graffiti mock rolls up 33 bars not 22, record_status sees a sinking FAIL row, checkout_identity v2 report all 63 ta
- `RIMMANDRAKE_REGROUP_SETTINGS_SCREENS_FOUR_MODS_OUTGREW_AUDIT` — Settings screens outgrew their audit: ExplosiveKnockback, Rites, CathedralPass, KyberTradePlot have ungrouped settings or extra groups. Parked on the 
- `RIMMANDRAKE_RESTORE_ON_THROW_IN_KNOCKBACK_PROOF_TWO_LEAKS` — RM_KnockbackProof.cs:755 and :1285 do not restore on throw (proof_restore_check). Parked on the known-red list by the nightly clean-up. Acceptance tes
- `RIMMANDRAKE_CLEAR_DEAD_STANDINS_AND_REFIT_MORAVATHA_PACK` — Art drift: 4 dead shadowed stand-ins under src, and RM_Moravatha north pack overlay no longer matches pack_overlay_fit.render(). Parked on the known-r
- `RIMMANDRAKE_UNHOOK_SELFTESTS_FROM_LIVE_HOST_STATE_ON_WSL` — Three selftests read live host state (net.exe pre-launch guard sees a Linux sandbox, tasklist.exe absent, a 315 s /tmp reap): stub the host or tag the
- `RIMMANDRAKE_FIX_METAL_EATER_HUNGER_JOB_EXPECTATIONS` — metal_eater: a hungry RM_Khorrak beside Steel gets no RM_EatMetal job, and a fed one still seeks metal. Parked on the known-red list by the nightly cl
- `RIMMANDRAKE_RECONCILE_RESEARCHRETAG_WORKSHOP_TREE_WITH_DUMP` — ResearchRetag: RM_WM_AlloyForgeRestoration and RM_WM_PlasteelAlloying patch says RUT_Tree_Workshop, the raw dump has Main. Parked on the known-red lis
- `RIMMANDRAKE_WRAP_NULL_TEXTURE_PROBE_WALKSTACK_IN_TRY` — JawaBenchNullTextureProbe.cs Prefix calls WalkStack outside any try, and HOOKS.md lists 1 site where the source has 2. Parked on the known-red list by
- `RIMMANDRAKE_BUDGET_SECOND_GAME_MUTANTS_PAST_FIVE_HUNDRED_SECONDS` — selftest_second_game_mutants ran past 500 s on 2026-11-12 (killed, rc 124) and the 03:00 nightly saw 1 of 79 planted mutants (session_b_uses_steam) no
- `RIMMANDRAKE_COVER_DROWNED_SPRITES_IN_BODY_COLOUR_NOT_FLOOR` — A drowned thing in clear pit liquid shows less body colour than the water around it, a lighter patch per thing at middle depths. Cause: RM_SubmergeDra
- `RIMMANDRAKE_SPARE_DET_CLONE_WHEN_NEXT_RUN_STARTS` — detached_helper.py return deleted a .det clone a NEW run of the same item had just started in. Measured 2026-11-12: unit rm-detached-bench-rimmandrake
- `RIMMANDRAKE_LIST_MOVED_PINS_IN_LOOK_NOTES` — Rule 2e tooling: the notes of his next look list EVERY pinned line (a pass he gave, stored with its value) whose value a fix moved, old beside new, an
- `RIMMANDRAKE_LABEL_CHANGED_SINCE_LAST_LOOK_IN_REVIEW_SAVES` — Rule 2f tooling: a review save's builder labels every cell whose inputs changed since his last look 'changed since your last look', so each objection 
- `RIMMANDRAKE_ADMIT_PAUSED_FLYER_READS_AT_BRIDGE_TAKE` — Rule 11 follow-through: the delegated bridge take (cli._delegated_gate, flight_purpose) refuses ANY purpose with flight wording, so a paused flyer sta
- `RIMMANDRAKE_FADE_LAID_HOSE_ON_PIT_FLOOR_LIKE_CORDS` — Laid FlowWorks hoses, pipe joins and under-couplers on a pit floor draw crisp under liquid. Round 2 routed every realtime THING (Thing.DynamicDrawPhas
- `RIMMANDRAKE_INGEST_HELD_LOOK_DEFECTS_WHEN_LADDER_REGENERATED` — Ingest the held owner-look defects into the regenerated validation ladder, where and how each belongs, then empty the holding store. Acceptance test: 
- `RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS` — Explosive Knockback: absorb Extra Explosion Effects' idea, our own blast flecks, smoke, debris and big-blast shockwave
- `RIMMANDRAKE_UNBEND_GSS_LEAD_AT_JUNCTION_BATTERY_TWICE` — GSS M2c: one unforced 235-degree bend on the core site's junction:163,153 to battery:153,153 lead, same in both 2026-11-12 Steve runs; planner kink or
- `RIMMANDRAKE_TRACE_GSS_ILLEGAL_PATH_ONLY_ON_FIRST_START` — GSS log rows: 'Illegal characters in path' (ContentFinder, a GSS frame in the stack) on one start, 'DrawGUITexture: texture is null' on the next; rows
- `RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE` — Test queue: a proof-build job route (build -p:RmProofs=true and deploy it on SteveDesktop); Explosive Knockback's live scenes cannot run without it
- `RIMMANDRAKE_CUT_RELENTLESS_RELEASE_BEFORE_ANY_TIMER_RESTART` — The Relentless release tree (release/current -> 76283ad5ba1a) predates the Designer loop guards (5e1fb090e736, e3c6fa76427b): re-enabling rm-relentles
- `RIMMANDRAKE_TRIAGE_TWENTY_TWO_REDS_BORN_AFTER_THE_NIGHTLY` — 22 selftests red in the 2026-11-12 evening full sweep that were green at the 03:00 nightly (358 commits between; many FlowWorks under-liquid: hose_por
- `RIMMANDRAKE_SHOW_SOAKER_IN_DEEP_POOL_FURR_VANISHED` — A colonist soaking in a 4 m geyser pool, and the geyser itself, are not drawn at all
- `RIMMANDRAKE_FIND_RIVER_SWIM_BRUISES_FUEGO_HURT_FIVE_TIMES` — A colonist swimming a natural river took a bruise every few hundred ticks
- `RIMMANDRAKE_ANIMATE_POUR_SPILL_SHEET_ARRIVES_ALL_AT_ONCE` — A dev overflow pour lays its whole spill at tick 0: no bulge, nothing to watch move
- `RIMMANDRAKE_SPLIT_GEYSER_PROOF_COUNTERS_EVERY_VENT_SHARES_ONE` — RM_GeyserPoolProof's plumeBubbles/dryPuffs are global, so no per-vent bubble check can be read
- `RIMMANDRAKE_RECONCILE_SHADOW_JUDGE_WITH_TINT_SHEET_130_RED` — Floor shadows under water stay at the dry alpha 0.3: the regression judge says FAIL and the look shows dark patches
- `RIMMANDRAKE_EXPLAIN_BRIM_POUR_LITRES_WITH_NOWHERE_TO_GO` — An overflow pour reports litres with 'nowhere to go' on open ground
- `RIMMANDRAKE_REFRESH_LABEL_FADE_AFTER_SET_LEVEL_SEVEN_BRIGHT` — After SetLevel lowered a pit, 7 labels read full brightness over drowned things

## Commits

```
f4de28730a conversations: catch-up 2 record(s)
6422d8520e conversations: catch-up 1 record(s)
0a7f71a767 ledger: detached run on RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE ended
e4d3af18a1 ledger: RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE AFK hour: 7 items filed, notes, 3 lessons
33879e99d6 ledger: RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS clone bundled
1e1d56bd97 conversations: catch-up 1 record(s)
a26d45126b ledger: detached run on RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS ended
78ee2b72bf ledger: RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS note
ac6bf76c35 ledger: RUNNER ingest of 1 testq job(s)
ad403fd090 docs: the refusal contract ruling in standing_rulings, CLAUDE.md, delegation_policy §4, designer.md (T10)
d7312278fc ledger: RIMMANDRAKE_INVENTORY_VALIDATION_SCHEMES_BEFORE_ANY_LADDER clone bundled
4e4df8f428 conversations: catch-up 1 record(s)
dc0ee87533 ledger: detached run on RIMMANDRAKE_INVENTORY_VALIDATION_SCHEMES_BEFORE_ANY_LADDER ended
acdd18bdb6 ledger: RIMMANDRAKE_INVENTORY_VALIDATION_SCHEMES_BEFORE_ANY_LADDER note
d1e2057535 ledger: RUNNER ingest of 1 testq job(s)
fa0019db0b validation map: clean-up pass result and the 22 reds born after the nightly; waker stays off until they are cleared or listed
648af67803 owner_look_regressions: the pour row calls PourOverflow, what the dev menu runs (Pour refuses a brim pit by design); live PASS
e4092c5418 ledger: RIMMANDRAKE_ALLOW_MEDIUM_FURNITURE_ON_PIT_FLOOR note
dddb88fd7a ledger: RUNNER ingest of 1 testq job(s)
08ab6d11a8 ledger: steward retired a recovered incident
... 131 more: git log --oneline d9933d344e..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-13T04:09:10Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M deployed/config/ModsConfig.before-tier-pyrelands.xml   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
 M src/RimMandrake/HugeThings/Source/Kernel/RM_HugeTitanKernel.cs   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? cards.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? deployed/config/ModsConfig.before-tier-mods__mandrake_rm_explosiveknockback__mandrake_rm_flowworks__mandrake_rm_gimmesomeslack__mandrake_rm_patches.xml   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? deployed/config/ModsConfig.swap-active.pyrelands.stale-20261112.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? deployed/config/ModsConfig.swap-active.weepingstones_solo.stale-20261108.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? design/RimMandrake/designer_drawing_out.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? design/concepts/Pyrelands/coverage_verdict.json   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/BENCH.md.tmp.1153431.1794098233190787055   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_FWLIVE.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE1.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE2.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE3.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_FWLIVE.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE1.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE2.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE3.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE4.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE5.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE6.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE7.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE8.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CODEX_ARCHMAGI_FWDRAIN.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? infrastructure/state/queue/CODEX_STEVEDESKTOP_HUGETHINGS.md   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? ralph/.context_warned   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
?? shortcuts.ps1.txt   -- not this window's: already dirty at the 18:32 wake (older seats' leftovers, same list as the last three handoffs; the Pyrelands-group helper was asked to read the HugeThings kernel diff and designer_drawing_out.md and say whether they should land)
```

