# BENCH_REBOOT_HANDOFF_202611130137 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611122135`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner spent the afternoon ruling on PROCESS as much as on the game, and every ruling is verbatim and dated in the Conductor log (`D:\ClaudeWork\rimmandrake\conductor\log.md`, tail 80 lines first). The four that change how every seat works: (1) no judge or gate may refuse without a full refusal record, an attainable fix and a verdict on the criterion itself; flawed criteria go to a neutral fixer; "nothing could ever pass" is an alarm (spec `design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md`; the evidence gate stays in SHADOW); (2) unattended work PARKS as waiting-on-owner, it never grinds (last night's Designer loop burned about 90M tokens on ExplosiveKnockback; fixes landed, not live until the dispatch clone pulls); (3) if any part of a mod is built, the Designer suggests a live walk before adding design; (4) a zero-token Python preflight checks a ticket before any token is spent (spec `design/specs/2026-11-12-ticket-preflight-before-any-token.md`, six owner questions uncarded). On the game: no above-zero elevation, ever (closed); one under-liquid draw rule (`RM_UnderLiquid`, 441c321a20dc) is built and was being proven live when this was written. And a habit to keep: LOOK at anything before it opens on his screen; I opened a helper's viewer unlooked and he rightly asked what it was.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Second look owed, pit fittings under liquid: keeper save `UNDER_LIQUID_LAW_MATRIX_20261112` plus his requested big assorted-items pit (several fill levels, 4 m deep, installed furniture, mod items); key `D:\ClaudeWork\rimmandrake\conductor\submerge_matrix_20261112\live_proof\BIG_PIT_KEY.md`. Check the helper's captures yourself before telling him it is ready. Open, no confirmed cause: the dark halo around full deep pits.
- MandrakeModels (`D:\Luke\dev\MandrakeModels`, 6b707e2 plus the viewer rework): he rejected the first compare page ("don't look like anything we'd see in a water-surface simulation"). Stills for YOUR check go to `D:\ClaudeWork\mandrakemodels\compare\stills\` before anything is opened for him. Its recommendation (virtual pipes or local-inertial; waves as a visual layer) disagrees with the RimMandrake bakeoff plan's shortlist; unreconciled.
- Cards owed, one topic at a time: preflight (6, spec section 9); Designer light path (2: drop the exam; build the save before the sitting); water clock, waves, pass bar, tie rule (bakeoff plan); fill history (5); rivers (3); clear water; aquatic grow zones; Relentless retirement steps 3-5 (`...\validation_inventory_20261112\RELENTLESS_RETIRE_SCOPE.md`).
- His word wanted, no card needed: keep the player-truth sweep for good (it is live code, never dormant); findings judge stays on at about $2 a day (it was off by his own 2026-11-07 stop); whether he looked at the gas-clumps and heavy-goods knockback matrices (items left open); the ladder-slowdown look.
- ExplosiveKnockback: his "No blockers" is recorded as certification (owner note), four gap fixes landed; `coverage_verdict.json` is stale and unsigned on purpose (no judge was run). Cold Storage lockers and crock are now OPEN by his rule; no container of ours hides its contents, so his morning wish (a crate that flies with contents safe) needs one. Kept for good by card: Better Explosions, Dynamic Effects Forge, Custom Gas Types; absorb Extra Explosion Effects into EK (not started).
- Fleet dashboard (Augur, branch `augur-wsl`, 5e99de1): links at the foot, STALE in red; GPT's ten improvements unapplied (`D:\ClaudeWork\claude-dash-design\GPT_GRAPHICAL_REVIEW.md`); legend still lists Haiku; finished helpers drawn as live; merge to main is his after a Mac check. PR to Steven's repo: https://github.com/bannigan/claude-dash/pull/1.
- Lakebed idea (textured mud, stranded plants and fish, beasts, planting, drying): his words are on the natural-water item; sized by guess only, no study launched.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `RIMMANDRAKE_POINT_SEAL_FOODS_AT_REAL_TEXTURES_SEVEN_BLANKS` — fix landed 6a5ce0ad37 (Graphic_Single on 7 defs), deployed; live check rides the under-liquid proof load; NEXT: read the live-proof helper's sealed-food line; close with `rimflow close ... --sha 6a5ce0ad37` if zero Texture2D errors, else note UNMEASURED and check on the next load that has ColdStorage and TheSump
- `RIMMANDRAKE_REMOVE_WHITTLE_ACCOUNT_LINE_FLEET_DASHBOARD_OWNS_IT` — code landed 2f6357d677, selftest 51/51; the live page drops the line only after the dispatch clone pulls; NEXT: confirm `D:\ClaudeWork\rimmandrake\conductor\WHITTLE_NOW.md` no longer shows the account line, then close with the --live command in the item note
- `RIMMANDRAKE_STOP_COVERAGE_LOOP_AT_THIRD_REFUSAL` — landed 5e1fb090e736 (stops at the third refusal on the nine replayed EK verdicts), not live; NEXT: check the dispatch clone has pulled it; it is proven live only when a real Designer coverage run stops and raises its alarm; do not launch one to prove it

- `RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE` -- an in-window rm-bridge helper was deploying FlowWorks 441c321a20dc, restarting, running the matrix proof and building the big-pit scene; it holds the bridge as BENCH and DIES with this window; NEXT: read `D:\ClaudeWork\rimmandrake\conductor\submerge_matrix_20261112\live_proof\` (PLAN.md, captures, BIG_PIT_KEY.md); if unfinished, free a stale bridge hold and relaunch an rm-bridge helper from the item and the Conductor log entries of 2026-11-13 01:2x Z.
- `MANDRAKEMODELS_BUILD_FLUID_BAKEOFF_ONE_INTERFACE_MANY_WATERS` -- viewer rework (water drawn as water, 128+ cells, water scenes first) running in-window, dies with it; NEXT: read `D:\ClaudeWork\mandrakemodels\progress.md`, look at `compare\stills\`, relaunch the rework from the pushed repo if unfinished, and open nothing for him until you have looked.
- `RIMMANDRAKE_PREFLIGHT_TICKETS_BEFORE_ANY_TOKEN_IS_SPENT` -- spec published 9b61b770b892 (95 checks), nothing built, tickets unfiled; NEXT: card him the six questions in spec section 9, then file the first three build tickets it names.
- `RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS` -- T1, T2 and T3's dead-Marker clause landed; park-when-away, 2x ceiling, re-judge-only-changes and quick-look landed (e3c6fa76427b, 7a7f9bbc5dcb, 3d0fdca88662); T4-T10 unbuilt; gate in shadow; NEXT: launch an Opus rm-builder on T4 (judge briefs emit refusal records) and on the 12 leftover truncation sites (`RIMMANDRAKE_STORE_TEXT_WHOLE_FINISH_LEFTOVERS`), then rerun the unrun test batch ub_03 on a quiet machine.
- `RIMMANDRAKE_OFFER_OWNER_QUICK_LOOK_LOUDLY` -- his live-walk rule is in roles/designer.md and the light-path spec (a5a18d5659e2) as text only; NEXT: give a Sonnet rm-fixer the program enforcement in designer_stage.py (walk proposal required on stage 1-2 results when any inventory entry has impl: present) with a selftest.
- `RIMMANDRAKE_INVENTORY_VALIDATION_SCHEMES_BEFORE_ANY_LADDER` -- his four card answers recorded; owed: the "throws you backwards" rule (an objection revalidates only touched line items), the one clean-up of the always-red nightly sweep, five inventory errors unfiled; NEXT: draft the stage map and rules as `design/RimMandrake/validation_map_and_rules.md` from `...\validation_inventory_20261112\CARD_DRAFT.md` with that rule first, and file the nightly clean-up as an item.
- `RIMMANDRAKE_DECIDE_EXPLOSION_MODS_KEEP_ABSORB` -- decided by card; NEXT: close it and file the absorb of Extra Explosion Effects' idea into ExplosiveKnockback as its own item.
- `RIMMANDRAKE_DEPLOY_KNOCKBACK_DRAWING_STORAGE_OPEN` -- the game copy still holds the retired closed-container patch; five changed files await review; NEXT: have an Opus rm-builder review the five files, then deploy ExplosiveKnockback and run `RIMMANDRAKE_PROVE_KNOCKBACK_HIDING_LOCKER_LIVE`.
- `STEVE_LANE_UNSTICK_BRAKED_UNOWNED_51AC` -- still braked for a real reason (harness failures; one fixed 7de68f7c4d; canary retry was running); NEXT: read the canary's result with the testq tools; lift the brake only on a DONE canary; no hardware diagnosis.
- `RIMMANDRAKE_SWEEP_WATER_SOLVERS_ON_BIG_MAPS` -- plan published 19e26c039250; MandrakeModels now holds the solvers; NEXT: reconcile the plan's shortlist with MandrakeModels' results table, fold in his groundwater, evaporation and edge-refill rulings, then card the water clock.
- `RIMMANDRAKE_EXTEND_PLAYER_TRUTH_SWEEP_LADDER_WAS_ONE` -- filed, untouched; NEXT: give it to an Opus rm-builder once he confirms the sweep stays.
- `BENCH_REBOOT_HANDOFF_202611122135` -- the predecessor's pointers not touched this window stand as written there and in `BENCH_REBOOT_HANDOFF_202611121724` (fill steps, GSS switchboard, Pyrelands, HugeThings, the "one mod one agent one checklist" offer, which I advised holding); NEXT: run `handoff.py --wake` and settle each against the ledger.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- fork and general-purpose subagents are hook-refused here; rm-builder with model fable ran as Fable 5.2 in-window (filed: lessons/20261113T013735Z-BENCH-agent-tool-conductor-window-subagent-type).
- Helper budget N=2 once he is "silent"; card answers do not count as typing (filed: lessons/20261113T013735Z-BENCH-conductor-helper-budget-hook-allows-n).
- In-window helpers stop at 250 turns mid-task; SendMessage resumes them (filed: lessons/20261113T013735Z-BENCH-window-helpers-stop-at-250-turn).
- Eight helpers at once overloaded the machine; timed-out test batches are unrun, not passed (filed: lessons/20261113T013735Z-BENCH-eight-or-more-window-helpers-at).
- Closing a no-code study: `--no-code` without `--sha` (filed: lessons/20261113T013735Z-BENCH-rimflow-close-study-or-ruling-with).
- Look at a helper's page before opening it on his screen (filed: lessons/20261113T012223Z-BENCH-conductor-opened-helper-s-10-mb).
- The validation inventory called live schemes dormant (player-truth sweep) and I recommended from its one-line table unread; read the row before recommending (see: Conductor log 2026-11-12, owner "Didn't you read these before?").

## Closed since the last handoff (8)

- `RIMMANDRAKE_FIX_CAPTURE_ZOOM_WONT_TIGHTEN_ON_SCENES` — 1e47e973822a
- `RIMMANDRAKE_BUILD_REFUSAL_CONTRACT_CHECK_AND_CACHE` — 40fde3bc437fa19b0891d579d79264c985d19870
- `RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS` — 9fa4614958e071124d9a6476a73d1e77e7896e48
- `RIMMANDRAKE_PARK_UNATTENDED_DESIGNER_LOOPS` — e3c6fa76427b
- `RIMMANDRAKE_CEIL_JUDGE_LOOPS_AT_TWICE_CAP` — e3c6fa76427b
- `RIMMANDRAKE_STUDY_WHOLE_MAP_ELEVATION_OWNER_EXPECTS_A_NO` — done by verify, no close
- `RIMMANDRAKE_REJUDGE_ONLY_CHANGED_GAPS` — done by verify, no close
- `RIMMANDRAKE_OFFER_OWNER_QUICK_LOOK_LOUDLY` — done by verify, no close

## Filed and still open (34) — the next seat's queue

- `RIMMANDRAKE_REMOVE_WHITTLE_ACCOUNT_LINE_FLEET_DASHBOARD_OWNS_IT` — Whittle page: drop the bold account line (and codex/history readers); Augur fleet dashboard is the accounts front page
- `RIMMANDRAKE_SWEEP_WATER_SOLVERS_ON_BIG_MAPS` — Python bakeoff of FlowWorks water solvers (local-inertial, repaired implicit, WCA2D, full shallow-water referee, design-7 baseline) at 250/325/400 map
- `RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS` — Every refusal by a judge or gate carries detail equal to the evidence, an attainable path to pass and an assessment of the acceptance criteria; flawed
- `RIMMANDRAKE_STOP_COVERAGE_LOOP_AT_THIRD_REFUSAL` — T1 Designer coverage judge: a 3rd not_covered on one concept stops judge launches and raises REFUSAL_NOTHING_COULD_EVER_PASS; later gaps tagged unfixe
- `RIMMANDRAKE_RECORD_GATE_REFUSALS_DROP_DEAD_MARKER` — T3 evidence_gate.py before the flip: reasons become refusal records, producer-liveness check, the no-Marker clause replaced (Marker stopped since 2026
- `RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_JUDGE_BRIEFS` — T4 scene_look_judge_brief.md, art_judge_brief.md and the coverage prompt emit refusal records and their launchers call refusal_contract.py check. Done
- `RIMMANDRAKE_BUILD_NEUTRAL_CRITERIA_FIXER_WITH_GUARD` — T5 neutral criteria fixer: roles/criteria_fixer.md, refusal_contract.py repair and diffguard, the recording path and the fresh-instance rejudge. Done 
- `RIMMANDRAKE_SEED_JUDGE_CALIBRATION_FROM_CORPORA` — T6 infrastructure/state/judge_calibration.json and refusal_contract.py calibrate, seeded from evidence_gate_corpus, the art regression set and the sce
- `RIMMANDRAKE_KEY_TESTQ_SKIP_CACHE_ON_INPUTS` — T7 piecemeal revalidation: testq skip-when-unchanged cache keyed (line, criterion hash, inputs hash, build) and lines declare inputs. Done = the cache
- `RIMMANDRAKE_ROUTE_ART_ROUND_CAP_TO_CRITERIA_FIXER` — T8 art_eval/round_series.py: at the round-3 cap a suspect criterion (OPEN criteria-ledger row) goes to the criteria fixer; only owner bars go to the o
- `RIMMANDRAKE_KEEP_WHOLE_REFUSALS_CACHE_CONCEPT_GATE` — T9 Relentless store keeps whole refusal detail (no 600-char cut; a pointer to the record) and concept_refused uses the repeat-key cache so one sentenc
- `RIMMANDRAKE_PROPAGATE_REFUSAL_CONTRACT_TO_DOCS` — T10 one line each in CLAUDE.md, delegation_policy.md §4, rimworld-art-evaluation and rimworld-live-review skills, standing_rulings.md, and every file 
- `RIMMANDRAKE_UNJAM_FINDINGS_FOLD_THREE_ITEMS_ONE_NAME` — findings_fold run is UNMEASURED since 2026-11-12T15:44Z: testq ingest gave three items (ASH_FIELD_FIX_FORGETS_THE_WATER, PYRELANDS_GREEN_MINIMAL_1, PY
- `RIMMANDRAKE_PREPARE_FIRST_LOOK_MATRIX_SAVEGAME` — First-human-look savegame standard: merge the review map rulebook with matrix scenes (one prepared cell replicated over the variables, labelled) into 
- `RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE` — PRIORITIZED: shared in-game C# scene runner (fast-testing step 8): one [RMTest] runner, row table per scene, ticks in process; first slice ports one s
- `RIMMANDRAKE_FOLD_FRAME_JUDGE_INTO_PRELOOK` — Fold the north-star frame judge (judge_cli.py) into the pre-look scene judge as its pass-2 checklist: one brief, one entry point
- `RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS` — Revive the shipped-settings fuzz matrix as a standing offline scheme with written conservation laws and sanity principles per mod, on a clock, each la
- `RIMMANDRAKE_BUILD_OBSERVATORY_SMALL_PROVEN_FIRST` — Build the bridge validation observatory small: a per-run report that leads with required checks proven, diagnostics underneath, no LLM
- `RIMMANDRAKE_PREFLIGHT_TICKETS_BEFORE_ANY_TOKEN_IS_SPENT` — A deterministic Python preflight checks everything checkable about a ticket (files, paths, defs, races real and expected on the named mod list; accept
- `RIMMANDRAKE_EXTEND_PLAYER_TRUTH_SWEEP_LADDER_WAS_ONE` — Re-examine the player-truth sweep (obvious truths checked offline; pilot 2026-10-26: 19 truths, 1 violation class): run more trials, and bake truths i
- `RIMMANDRAKE_STORE_TEXT_WHOLE_FINISH_LEFTOVERS` — Finish the no-cuts sweep: 12 sites in the T1-T3 files, the 2-digit pass, reviews owed
- `RIMMANDRAKE_ROLE_FILES_NAME_CONDUCTOR_RULING` — selftest_conductor_authority red: roles artisan, conductor_restart, relentless, runner_options, whittle do not name CONDUCTOR_AUTHORITY_DECIDE_NO_ASKI
- `RIMMANDRAKE_HEAD_SELFTESTS_RED_NOT_DESIGNER` — Four selftests red on HEAD, none touching designer code: incident (bindjudge alarm kinds unrouted), entrypoint_inventory (relentless_head_age doc in l
- `RIMMANDRAKE_PROVE_KNOCKBACK_HIDING_LOCKER_LIVE` — Explosive Knockback: re-prove closed containers live with LWM's Deep Storage weapons locker, no shelf or hopper tagged closed; delete or restage the t
- `RIMMANDRAKE_CENSUS_KNOCKBACK_STORAGE_OPEN_CLOSED` — Explosive Knockback: offline census selftest, every storage def closed exactly when it hides its contents (Shelf, ShelfSmall, Hopper open)
- `RIMMANDRAKE_DEPLOY_KNOCKBACK_DRAWING_STORAGE_OPEN` — Explosive Knockback: review the 5 DIRTY files, then deploy so the game copy loses the closed-tag patch on Cold Storage lockers
- `RIMMANDRAKE_PROVE_KNOCKBACK_OUTERRIM_BLAST_LANES` — Explosive Knockback: stage and prove sc_blast_kinds' Outer Rim sonic and plasma grenade lanes
- `RIMMANDRAKE_DECIDE_EXPLOSION_MODS_KEEP_ABSORB` — Owner card: keep, absorb into Explosive Knockback, or drop each of the four explosion-effect mods
- `RIMMANDRAKE_REPAINT_SWALE_AS_FLOOR_TILE` — RM_Swale texture is a trough/slide picture (perspective walls); the owner wants it drawn as a flat floor tile. Code already draws it flat as a floor l
- `RIMMANDRAKE_RETIRE_SPIKE_SUBMERGED_ALPHA` — RM_SpikeDrawMath.SubmergedAlpha is dead in production since RM_UnderLiquid (441c321a20dc) but still used by SpikeDrawChecks, the spike_parity harness,
- `RIMMANDRAKE_COVER_REALTIME_MINIFIED_UNDER_LIQUID` — MinifiedThingRealtimeDraw (drawerType RealtimeOnly) is not covered by the map-mesh PrintPlane split in RM_SubmergeDraw: a realtime-drawn minified thin
- `RIMMANDRAKE_UNHANG_ARTPIPE_STATE_FIND` — python3 src/RimMandrake/Utils/artpipe/artpipe_state.py find swale hung past 60 s (timeout exit 124) on 2026-11-12 in the bench clone
- `RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE` — Live proof owed for 441c321a20dc: deploy FlowWorks (deploy_custom_mods.py --mod FlowWorks, then --apply with the game closed), then python.exe src/Rim
- `RIMMANDRAKE_REVIEW_UNDER_LIQUID_LAW_CODE` — Full-file code review owed (all DIRTY, never self-marked) for 441c321a20dc: RM_UnderLiquid.cs, RM_SubmergeDraw.cs, RM_Spikes.cs, RM_FlowDoors.cs, RM_E

## Commits

```
52ae2524ff conversations: catch-up 3 record(s)
90a3e35ed1 ledger: owner look notes on SUBMERGE_PIT_FITTINGS_BY_LEVEL, goods/swale decision closed, follow-ups filed (441c321a20dc)
511a1c5da8 ledger: owner card answers on the explosion mods (keep Forge, Better Explosions, Custom Gas Types; absorb Extra Explosion Effects)
441c321a20 FlowWorks: one law for everything in a pit under liquid (RM_UnderLiquid); tar dark; shade only inside; cover needs 2 solid sides
3a83d6abec explosion mods: code reading (Forge decompiled, Better Explosions, Custom Gas Types); replace UNMEASURED lines with measured facts
b5c92e8385 lesson: look at a helper's page before opening it on the owner's screen
a1c6216002 evidence_gate: replace the dead 'no Marker verdict' clause per the owner's D4 card (criteria repair; gate stays shadow)
a5a18d5659 Designer: any built part means suggest a live walk first; no share-built threshold (owner 2026-11-12)
2d39be20c0 ledger: note B-E landed and the light-path spec on the parent item
7d31ffb706 spec: the Designer's light path when code exists (not built)
76c085cfb7 ledger: E verified and closed at 3d0fdca88662
3d0fdca886 designer: refuse an ask without a quick_look once code exists (E)
03d206ee09 ledger: D verified and closed at 7a7f9bbc5dcb
ea0c92bcf0 ledger: EK certify, owner rulings on the 4 gaps, 5 follow-up items filed
7a7f9bbc5d coverage judge: re-judge only claimed gaps and changed entries (D)
6485aafec2 EK: anything that draws its contents is open; drop the closed-tag patch on Cold Storage, proof stages LWM weapons locker
0c1592e2d7 EK concept: draws-its-contents is open (hoppers, shelves), drop 'rack', restage storeroom pit on LWM weapons locker, name blast_kinds lanes
32cb7b0c08 EK: characterize the explosion-effect mods on our lists (gap 2), choices left to the owner
3eeed00bd5 ledger: B and C verified and closed at e3c6fa76427b
f97312bc94 ledger: steward retired a recovered incident
... 50 more: git log --oneline b99048a3dd..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : LOADING  → corrected to UP, measured now
- Bridge: for     deploy and prove under-liquid law

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M deployed/config/ModsConfig.before-tier-pyrelands.xml   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M infrastructure/state/ledger/events/BENCH.jsonl   -- this window and its helpers: ledger events, committed before the ready signal
 M infrastructure/state/ledger/events/OWNER.jsonl   -- this window and its helpers: ledger events, committed before the ready signal
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
 M src/RimMandrake/HugeThings/Source/Kernel/RM_HugeTitanKernel.cs   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? cards.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? deployed/config/ModsConfig.before-tier-mods__mandrake_rm_explosiveknockback__mandrake_rm_flowworks__mandrake_rm_gimmesomeslack__mandrake_rm_patches.xml   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? deployed/config/ModsConfig.swap-active.pyrelands.stale-20261112.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? deployed/config/ModsConfig.swap-active.weepingstones_solo.stale-20261108.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? design/RimMandrake/designer_drawing_out.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? design/concepts/Pyrelands/coverage_verdict.json   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/BENCH.md.tmp.1153431.1794098233190787055   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_FWLIVE.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE1.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE2.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE3.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_FWLIVE.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE1.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE2.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE3.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE4.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE5.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE6.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE7.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE8.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CODEX_ARCHMAGI_FWDRAIN.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? infrastructure/state/queue/CODEX_STEVEDESKTOP_HUGETHINGS.md   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? ralph/.context_warned   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
?? shortcuts.ps1.txt   -- not this window's: already dirty at the 13:51 wake (older seats' leftovers, same list as the last two handoffs)
```

