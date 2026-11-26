# Explosive Knockback: journal

The mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. Below it the
**history** is only added to. Test of this file: a restarted Conductor can do the next stage change from it alone.

## The mod as it stands

- **Design Version 0.1.0, locked** on his word 2026-11-13 (`version/VERSION.json`). Code exists:
  `src/RimMandrake/ExplosiveKnockback/`.
- **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-25 7:01 PM PST (`version/stage_record.json`).
- **Bars:** 59 (30 inventory rows of `record.json` + 29 leaves of `tree.json`). The test-and-stage table is
  `version/test_table.json` (read view `version/test_table.md`).
- **Measured 2026-11-14 12:45 PST:** 53 of 59 bars have at least one test that runs today; 47 have every deciding test
  runnable; 41 have all their offline deciding tests green. All 15 offline tests are built (13 PASS, 2 known red,
  unchanged). In-game scenes: 56, entry exists 50, absent 6. Every in-game scene is UNRUN (Stage 6); commands in the table.
- **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-25 7:01 PM PST).
- **Open questions:** see "Questions" at the end of the history.

### The vision (his root paragraph, approved by card 2026-11-11, OWNER:1794468835221748501)

> Every blast in RimWorld now throws what it hits. A mortar shell beside a colonist hurls them three cells straight away
> from it, clean over sandbags, until a wall stops them hard; anything light goes too, so loose goods and corpses fly
> through the air, spinning and rebounding off walls, and no open shelf keeps them safe. When gas catches, it goes off
> clump by clump, each small burst scattering whatever lies near it, as the fire whooshes through the whole cloud. And
> where a blast meets a pit, its cover breaks and whoever it throws in falls.

The nine-line version vision (mass limit, blast power, shields, flagship, Mod Settings) is `version/vision.md`; it adds
his cards of 2026-11-13 and nothing inferred.

### His words on this mod (verbatim; full list with ledger ids in `sheet.md` "his words" and `record.json` decisions)

- 2026-10-06: "You can't fall in by careless colonist pathing. Only if they get blown/forced in do they fall."
- 2026-11-10: "1:1 totally. Even better if they can bounce inelastically off walls and rotate while they fly."
- 2026-11-11: "(1) but the closed containers may themselves get shoved a bit" · "2 and remember the gas in the Cauldron"
- 2026-11-12, the flagship: "Just put a bomb into a storeroom with people in it beside a pit. Shows some items falling
  into the pit and some people as well."
- 2026-11-12, 4:05 PM PST: "1: Anything that draws its contents is open. … 4: I am confused. Items should be blown off a
  shelf, and a shelf should be ruled as open, period. So the scene is staged misleadingly. No blockers."
- 2026-11-13: "We really shouldn't blow back creatures beyond a certain mass, and the heavier something is, the less it
  should fly. That should also be a function of the explosive damage itself as well." · "with a single scene we can
  check ALL these things together" · "Melee shove is a great idea, but it belongs in FlowWorks, not here."
- 2026-11-13, the lock: "Yes, fix it like that, and then please record this as an actual Pass." (OWNER:1794608649743135329)
- 2026-11-13, on the settings sweep: "can't we actually simulate that settings check offline? That seems a gratuitous use
  of the game, unless that's actually a very fast check?"

### Oddities (things a reader would otherwise get wrong)

1. **Three bar sets exist.** The 59 coverage checklist rows are the bars of 0.1.0, and Stage 6 reports against them.
   The 16 "north-star bars" (his card 2026-11-12, "Approve as written") and the 49 "must be true" rows of
   `design/validation_walks/RimMandrake/ExplosiveKnockback.md` (measured 2026-11-14; an older count said 30) are older
   lists that `validation.py` still reads. `version/bar_lists_map.json` maps them onto the 59: north-star 16 of 16;
   walk rows 49 with 3 unmapped, 1 in conflict and 1 partial (question 11).
2. **The locked files moved after the lock.** `version/bars.md` pins blobs at `237b791167`; since then `scenes.json`
   (sc_spared, sc_mass_and_power, sc_settings_sweep), `record.json` (decisions) and `tree.json` (the owner-certify
   stamp only) changed. The scene edits are test text (creatures chosen by mass, never named; the g1 mass pin), not bar
   meaning. `tree.json` leaves are byte-identical in content to the lock. [measured 2026-11-14]
3. **Judge round count has three answers** (12 / 13 / 19); not reconciled (spec §10).
4. **97.2 million tokens** were charged to the Designer stage, 86.5 million of them estimates (`version/VERSION.json`).
5. **Proof build versus release build.** Most live scenes exist only in the proof build (`RM_KnockbackProof.cs`,
   `proof_build_gate.py`); the test queue cannot deploy a proof build today (RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE).
6. **The scene ids in `scenes.json` are not the scene names in the proof code.** `scenes.json` entry points name 35
   scenes by proof method; `RM_KnockbackProof.Names` holds 41 older names, and only some of the 35 are among them
   (measured in Stage 2 below).

## History (dated, added to only)

### Conductor interventions (one line each, added to only; the form is in the spec §5, "The steward and the journal")

- CONDUCTOR INTERVENED (stage 3, 2026-11-14 12:15 PST, kind decision): a locked file that changed after the lock only by test-text corrections or by today's table work is re-pinned in `version/bars.md` with a journal line saying what changed; a changed bar is never re-pinned (the 3 post-lock changes in Oddities 2). Source: Steward's decisions in the Stage 3 brief of run `rm-detached-bench-rimmandrake-design-maturation-pipeline-w-1794687322`.
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 12:15 PST, kind decision): scene g4's colonist weight is pinned to 64-76 kg by a test-only proof hook; the bar is not changed, answering question 1. Source: the same brief.
- CONDUCTOR INTERVENED (stage 5, 2026-11-14 14:55 PST, kind re-pin): sc_pawn_arc's check text no longer says the colonist re-hauls "the stack it dropped at takeoff"; it checks the colonist holds the same stack through flight and landing, as built (`flyWithCarriedThing: true`) and as the owner kept for 0.1.0 ("For today have them hold it", question 7); bar meaning unchanged, `scenes.json` re-pinned in `version/bars.md`. Source: Conductor brief of 2026-11-14 about 2:45 PM PST to the BENCH builder (owner answers on questions 7 and 8; steward decisions on 3, 4, 6 and 9).
- CONDUCTOR INTERVENED (stage 5, 2026-11-14 14:55 PST, kind decision): 0.1.0 keeps the harmless landing on a pawn that walked in mid-flight (owner by card, "Bruise in the next version", question 8). Source: Conductor brief of 2026-11-14 about 2:45 PM PST to the BENCH builder (owner answers on questions 7 and 8; steward decisions on 3, 4, 6 and 9).
- CONDUCTOR INTERVENED (stage 5, 2026-11-14 14:55 PST, kind decision): deferred to 0.2.0 and listed in `version/next_version/README.md`: the carried thing flies its own trajectory (RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC, owner's words) and a landing on a pawn bruises both by the thrown pawn's weight (RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN, by card). Source: Conductor brief of 2026-11-14 about 2:45 PM PST to the BENCH builder (owner answers on questions 7 and 8; steward decisions on 3, 4, 6 and 9).
- CONDUCTOR INTERVENED (stage 5, 2026-11-14 14:55 PST, kind decision): Stage 6 reports against the 59 locked bars; the 16 north-star bars and the walk's "must be true" rows are mapped onto them in `version/bar_lists_map.json` (north-star 16 of 16; walk rows measured 49, not 30: 3 unmapped, 1 conflict, 1 partial; question 4). Source: Conductor brief of 2026-11-14 about 2:45 PM PST to the BENCH builder (owner answers on questions 7 and 8; steward decisions on 3, 4, 6 and 9).
- CONDUCTOR INTERVENED (stage 5, 2026-11-14 14:55 PST, kind re-pin): `record.json` state fields are bookkeeping, not bar meaning: inv_creature_mass_limit and inv_blast_power_damage read `impl: present` with evidence (built 40f4e85120, K-18 to K-20 pass, live proof unrun), and inv_big_corpse_spared names skip reason too_heavy; re-pinned (questions 3 and 9). Source: Conductor brief of 2026-11-14 about 2:45 PM PST to the BENCH builder (owner answers on questions 7 and 8; steward decisions on 3, 4, 6 and 9).
- CONDUCTOR INTERVENED (stage 5, 2026-11-14 14:55 PST, kind re-pin): sc_settings_sweep's lane, action and expectations now name every saved setting (46; 0 unnamed against 20 before, by the sweep test's own rule); test text, re-pinned (question 6). Source: Conductor brief of 2026-11-14 about 2:45 PM PST to the BENCH builder (owner answers on questions 7 and 8; steward decisions on 3, 4, 6 and 9).
- CONDUCTOR INTERVENED (stage 5, 2026-11-15 00:05 PST, kind decision): rulings on blind challenge cycle 1's four notes, for cycle 2: the 1.6 goods factor stays a constant (no Mod Setting in 0.1.0); the `sc_storeroom_mortar` ratio criterion is flawed (whole cells make 1.3 to 2.0 impossible for short throws and at the cap) and goes to a neutral fixer, never loosened by the builder; wild cells are journaled on the move line; the fire, EMP, smoke, extinguish and toxic-gas forces are pinned in the def lint. Also owed by the locked design: the closed-guard-off switch, the fire-at-half switch and a visible jolt. Source: Steward's decisions in `D:\ClaudeWork\rimmandrake\conductor\briefs\blind_challenge_ExplosiveKnockback_cycle2.md`.
- CONDUCTOR INTERVENED (stage 5, 2026-11-15 02:08 PST, kind re-pin): sc_storeroom_mortar's goods-factor clause, unattainable on whole cells (a correct build's per-good ratio runs 1.0 to 2.0; 53% of modelled goods outside 1.3 to 2.0 at cap 6), is replaced by the band 1.6 allows from each good's kernel cells, with a good of kernel 3 or more staged (INVALID otherwise), and reads the move line; bar meaning unchanged, `scenes.json` re-pinned in `version/bars.md`; refusal record `version/criterion_repairs/sc_storeroom_mortar_2026-11-15/refusal.json`. Source: Conductor night order of 2026-11-15 to the BENCH reconcile helper (item RIMMANDRAKE_CHALLENGE_KNOCKBACK_BLIND_TWO_FIRST_EXIT_MISSED), part A.
- CONDUCTOR INTERVENED (stage 5, 2026-11-15 02:08 PST, kind re-pin): the tests follow the owner's card of 2026-11-14 ~9:47 PM PST (OWNER:1794721689897638306, "Throw it, as built; the locked bar's wording changes by his word from 'slides one cell' to 'thrown a short way', and the test follows"): sc_closed_containers, sc_settings_sweep and sc_storeroom_bomb_pit and the closed_containers proof read "thrown a short way" (at least one cell, never past the cap, action thrown); the bar's words in `tree.json` and `sheet.md` are held as a patch because his coverage certificate is bound to the tree hash (RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING). Source: the same night order, part B.
- CONDUCTOR INTERVENED (stage 3, 2026-11-15 19:37 PST, kind re-pin): sc_barrage_perf's bar is reworded to the owner's answer (OWNER:1794799770273329641, "1 agree.", 2026-11-15 ~7:28 PM PST): the 99th-percentile frame inside the barrage-and-gas-chain window (0.9-8.25 s) at most 50 ms replaces the single worst frame, which the mod-off control broke on random list stalls (151.3 / 54.4 / 100.8 ms in the window). Decider KbFrameStats.WithinBudget, scenes.json, record.json, plan.md and the test table follow; tree.json and sheet.md words are HELD as `version/criterion_repairs/sc_barrage_perf_2026-11-15/tree_sheet_rewording.patch` because his coverage certificate is bound to the tree hash and his answer is not on the concept's item. Re-pinned with `designer_stage.py repin`. Source: item RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO.

### 2026-11-14 11:14 PST, pilot begins (rm-builder, detached, offline only)

Brief from the Conductor: do pilot rows 1 to 3 by hand (journal, finish Stage 1, Stage 2), throwaway scripts only, stop
before Stage 3. Owner, 2026-11-14: "We need to get this going."

### 2026-11-14 11:21 PST, row 1 done: journal started

- **Cost:** about $1.9 of model spend (the harness budget line; tokens not separately measured), 7 minutes wall.
  Almost all of it reading: the spec, the version folder, `record.json`, `tree.json`, `scenes.json`, the verdict.
- **Boring enough to automate:** collecting "his words" (already in `sheet.md` and `record.json` decisions with ledger
  ids; a program can render them); the post-lock drift check (blob hash per pinned file against `bars.md`).
- **Needed judgment:** which oddities a cold reader would trip on; noticing that `scenes.json` and the proof code use two
  scene vocabularies.

### 2026-11-14 11:27 PST, row 2 done: Stage 1 finished (the test-and-stage table)

- **What was done.** Every one of the 59 bars now names its deciding tests and the stage that proves it
  (`version/test_table.json`, read view `version/test_table.md`), built by a throwaway script whose bar-to-test
  placement is hand judgment and whose "runs today" column is measured by running every offline test
  (`D:\ClaudeWork\rimmandrake\maturation_pilot_ek\make_test_table.py`, 62 s per run, 60 s of it the tests).
  No bar's text was edited.
- **Offline tests run today:** kernel 142/142, fuzz 42001 cases, def lint, lint planted-defect 20/20, storage census,
  validation STATIC and mock (41/41 scenes staged), proof-build gate, FlowWorks cover breaks: PASS. Two known reds touch
  this mod: `selftest_settings_screens.py` (EK has 7 setting groups, expected 6; `debugDrawVectors` in no group;
  RIMMANDRAKE_REGROUP_SETTINGS_SCREENS_FOUR_MODS_OUTGREW_AUDIT) and `selftest_proof_restore_check.py` (two
  unrestored-on-throw leaks in `RM_KnockbackProof.cs`; RIMMANDRAKE_RESTORE_ON_THROW_IN_KNOCKBACK_PROOF_TWO_LEAKS).
- **The six judge corrections** (g1 to g6) were already in the test text (`scenes.json`, commits dea7804728 and
  39886c4919); the table re-checks each by text match. **g4 is reopened** by the post-lock commit 92fe261f36: the
  colonist band in `sc_mass_and_power` widened to 45-76 kg because live colonists weighed 48.75 and 60.75 kg, and under
  63.5 kg the kernel throws a colonist 6 cells at damage 100, tying the capped light animal. The scene's expect still
  says "light > colonist", the leaf's oracle still says "the colonist 5", and kernel check K-19 still tests 64-76 kg.
  Not edited: it is a question (below).
- **The 2 held look statements are placed** in the table (`held_statements`): "Anything that draws its contents is
  open" on the storage census test (offline, runs today, PASS); "a shelf should be ruled as open, period … staged
  misleadingly" on sc_open_storage and sc_closed_containers plus a Stage 2 staging check. Their rows stay in
  `design/RimMandrake/validation_holding/` as the verbatim source the preflight reads.
- **The settings sweep is moved offline in the table:** `settings_scale_and_switch` and `inv_settings` are decided by
  the specified offline test T_SETTINGS_SWEEP_OFFLINE (its acceptance is the already-filed
  RIMMANDRAKE_SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING); `sc_settings_sweep` keeps only the game-side wiring
  lines. The leaf text and the scene text are unchanged; Stage 3 shrinks the scene.
- **Cost:** about $1.2 (harness budget line, $1.9 to $3.1), 6 minutes wall.
- **Boring enough to automate:** running every offline test and recording rc, time and last line; listing each
  `scenes.json` entry point and checking it against `RM_KnockbackProof.Names`; checking the judge corrections by text
  match; rendering the read view.
- **Needed judgment:** which tests decide a bar and which only support it; which part of a bar an offline test can
  decide and why the rest needs the game (`why_game` per scene, to be re-asked by the Stage 4 challenger); spotting the
  reopened g4; the old proof-scene names (20 kept as support) versus the locked scene ids.

### 2026-11-14 11:32 PST, row 3 done: Stage 2 preflight, by a throwaway program

- **The program:** `version/pilot_throwaway/preflight_ek.py` (no model; reads `version/test_table.json`, the repo, the
  def dump and the ledger; writes `version/preflight.json`). 15 checks. **Run time 0.7 s** (6.8 s on the D: drive copy).
  Def list: the live dump `defs.sqlite`, 59262 defs, captured 2026-11-12T08:10Z (not the frozen official dump; every
  name it was asked about was found in it or in the repo).
- **Each check was watched going red** on a planted fault in a copy (bar dropped, bar without a test, stage 7, missing
  file, missing read, no game reason, held row unplaced, unknown def, unknown packageId, unknown settings field, a Hopper
  staged as closed, unknown item) and C13 was watched staying green with a 64-76 kg band. C14 missed its planted Hopper
  on the first try (it read the whole start text, where "drawing" appears elsewhere) and was fixed to judge each mention.
- **First run: 27 refusals.** One was Stage 1's own slip: the table (copied from the ticket text) named a settings field
  `landingStun`; the fields are `landingStunMin` and `landingStunMax`. Fixed in the table at once (back to Stage 1 for
  that line only) and re-run.
- **Second run: 26 refusals, in three checks:**
  - **C6 "Built: runs" (22).** 5 offline tests are specified, not built (the settings sweep, the gas tag census, the gas
    clump order, the heavy-knock kernel cases, the explosions-only hook scope) and 17 deciding in-game scenes have no
    entry in `RM_KnockbackProof.cs` (pawn_arc, spared_states, hose_carry_drop, settings_sweep, pawn_hits_pawn,
    goods_fly_wild, open_storage, closed_containers, blast_kinds, only_explosions, gas_chain, gas_census,
    no_cross_ordered, pit_goods_fetch, frame_probe_selfcheck, barrage_perf, walk_storeroom_raid). Route: Stage 3. The
    bars are sound; the tests are owed, each under the item `scenes.json` names.
  - **C12 locked files changed (3):** `tree.json` (the owner-certify stamp only), `scenes.json` (sc_spared,
    sc_mass_and_power, sc_settings_sweep), `record.json` (decisions). Route: the Conductor reads each change; test text
    is re-pinned in `bars.md`, a meaning change goes to him.
  - **C13 g4 (1):** the reopened colonist band (Questions, 1).
- **Cost:** about $1.2 (harness line, $3.1 to $4.3), 5 minutes wall.
- **Boring enough to automate:** all 15 checks; they are mechanical. The program is the seed of build-order step 3
  ("the Stage 2 preflight for a mod"). Def and packageId extraction from free scene text is a heuristic; a real
  preflight wants scenes to list their defs and mods as fields.
- **Needed judgment:** whether each post-lock change is test text or meaning; the g4 fix.

### 2026-11-14 12:45 PST, Stage 3 ("reconcile") done offline (rm-builder, detached, offline only)

- **Preflight refusals:** 26 before (11:32 run), **6 after** (12:43 run), all measured by `preflight_ek.py`.
- **Offline tests built, all PASS today, each watched red first** (on missing code, or on planted faults where the
  behaviour already existed): T_HEAVY_KNOCK_RULE (K-21 in `Source/SelfTest/Program.cs`, red on a missing kernel function,
  then green 152/152; a planted `<=` mutant goes red), T_ONLY_EXPLOSIONS_STATIC (`selftest_explosiveknockback_hook_scope.py`,
  3/3 planted faults caught), T_GAS_TAG_CENSUS (`selftest_explosiveknockback_gas_census.py` + `gas_census.json`, red with no
  census, 10 sources, 5/5 planted), T_GAS_CLUMP_ORDER (`selftest_explosiveknockback_gas_clumps.py`, the Cauldron's burn
  scan as a model plus the rule read from the C#, 6/6 planted), T_SETTINGS_SWEEP_OFFLINE
  (`selftest_explosiveknockback_settings_sweep.py` + `Source/SelfTest/KnockbackSweep.cs`: 24 runs, 2/2 coupling mutants and
  4/4 planted static faults caught).
- **Mod behaviour built:** the heavy-goods knock rule is now a kernel function (`RM_KnockbackMath.HeavyKnock`), called by
  the flyer (same behaviour). A thrown pawn whose planned landing cell gets a pawn on it mid-flight now lands there and the
  journal writes `land_on_pawn` naming that pawn (before, it was re-targeted to an earlier cell, against the leaf
  pawn_flight_arc, "lands on the cell chosen at the blast"). A test-only mass pin (`RM_KnockbackProof.PinnedMass`, proof
  build only) holds the sc_mass_and_power colonist at 64 to 76 kg (g4, the Conductor's decision).
- **In-game scenes written and compile-checked, UNRUN (Stage 6).** Each runs as `python.exe
  src\RimMandrake\ExplosiveKnockback\knockback_runner.py --scenes <entry> --ticks <n>` on a proof build: pawn_hits_pawn 300,
  only_explosions 300, open_storage 300, no_cross_ordered 2000, spared_states 300, blast_kinds 300, goods_fly_wild 300,
  gas_chain 300, gas_census 300, pawn_arc 900, pit_goods_fetch 60000. Three are renames of older scenes (goods_fly_wild of
  goods_fly_rebound; gas_chain and gas_census of gas_clumps); what each renamed or trimmed scene does not yet check is in the
  table's `partial` field.
- **Not built (the 6 refusals), and why:** hose_carry_drop (stages a FlowWorks hose reel; another helper is editing
  FlowWorks now); settings_sweep (the game-side wiring lanes, with the Cauldron and LWM's Deep Storage on the list; large);
  closed_containers (LWM's Deep Storage, Jawa Armoury and its four dependencies on the list; large); frame_probe_selfcheck and
  barrage_perf (need a frame-time instrument that does not exist yet); walk_storeroom_raid (full list, in `validation.py`).
- **What the builder could not test:** nothing in the game ran (offline only). The flying lane of sc_spared is left out
  on purpose: a flyer's flight is never live-tested without the owner present. The Outer Rim lanes of sc_blast_kinds are
  left out (that mod is not on the minimal list).
- **Re-pinned** in `version/bars.md`: `tree.json` (coverage stamp only), `scenes.json` (test text: sc_spared,
  sc_mass_and_power with g4 back to 64 to 76 kg, sc_settings_sweep), `record.json` (decisions log only). No bar changed.
- **Preflight fixed:** C9 now requires a def of ours in the repo's current Defs/Patches XML, not only in the older dump
  (watched red on a planted deleted def, `RM_FE_Filth_LooseAsh`); C6 now measures each test's entry point in the code at
  run time instead of trusting the table's saved flags.
- **Landed:** f243b4bf1b, 8498e2b493, d9d5ec1122, cf40045d0c.
- **Cost:** about $9.4 of model spend (the harness budget line, $0 to $9.4), 32 minutes wall, 0 of his minutes.
- **Boring enough to automate:** compiling the proof build to check new scenes (the proof-gate selftest already does
  it); regenerating the table and re-running the preflight after each batch; re-pinning a locked file after a
  test-text change (hash, edit the pin row); the gas-source census (a program can list sources; only the reasons need a
  writer); listing each renamed scene's unchecked clauses.
- **Needed judgment:** which scene expectations can be met by renaming an older scene and what that leaves unchecked;
  spotting that the landing patch re-targeted a pawn against the leaf; keeping the flyer lane out; deciding the census
  reasons; telling the restore-check red apart from new leaks (the same pre-existing lines; none added).

### 2026-11-14 about 1:50 PM PST, his card on the held statements

- **Owner, by card 2026-11-14 about 1:40 PM PST:** "Per mod, as it advances." A mod's held statements are placed in its
  table when it reaches preflight, and that placement counts as the ingest (spec §8, decision 12). This mod's 2 were
  placed at row 2, so they are ingested; the former question 2 is deleted as answered.

### 2026-11-14 about 2:55 PM PST, his answers on questions 7 and 8, and the steward's on 3, 4, 6 and 9

- **Owner, 2026-11-14 about 2:40 PM PST (question 7):** "For today have them hold it. Next version it should go flying
  independently of the person holding it. Different trajectories." **By card (question 8):** "Bruise in the next version".
- Changed: `scenes.json` (sc_pawn_arc, sc_settings_sweep), `record.json` (three rows' state fields), `version/bars.md`
  (both re-pinned), `version/bar_lists_map.json` (new), `version/next_version/README.md` (two 0.2.0 entries). Questions
  3, 4, 6, 7, 8 and 9 are deleted as answered; 10 and 11 are new.
- Preflight, measured: 6 refusals before (14:45 run) and 6 after (14:57 run), all C6 (built tests not yet run, such as
  sc_hose_drop); C12, the locked-file pins, passes after the re-pin. Copies: `D:\ClaudeWork\rimmandrake\helpers\ek_owner_answers_20261114\`.

### 2026-11-14 9:21 PM PST, Stage 3: the eleven bars made runnable (rm-builder, detached, offline only)

- **Item** RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN. **Bars with every deciding check runnable: 48 of 59
  before, 58 of 59 after**, measured by `make_test_table.py` and `maturation.py next`, which no longer refuses
  `every_bar_has_a_check_that_runs`. The one left is `walk_storeroom_raid` (its scene `validation.py::walk_storeroom_raid`
  is not written; the separate `walk_bars_confirmed` clause asks the steward about it). Preflight: 6 refusals before, 1
  after (that same walk scene).
- **Built, compile-checked, UNRUN (Stage 6)**, in `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof_StageThree.cs`,
  each with its control lane: `hose_carry_drop` (+`_off`), `closed_containers` (+`_control`), `settings_sweep` (+ one
  `settings_sweep_<lane>` per game-side setting, + `_after`), `frame_probe_selfcheck` (+`_paused`), `barrage_perf`
  (+`_off`). The frame-time probe (leaf `frame_time_probe`) is a proof-build MonoBehaviour writing one row per frame to
  `RM_FrameProbe_<stamp>.csv`. The commands, with their lanes and mod lists, are in `version/test_table.json`.
  `knockback_runner.py` gained `--real-seconds` (frame scenes run unpaused; ticks stepped inside one frame are not frames).
- **Offline tests, each watched red first:** K-22 in `Source/SelfTest/Program.cs` (the probe's reading as a pure kernel
  function `KbFrameStats`: red on the missing function, then 164/164; a planted rows-vs-frames bypass and a planted
  paused-row leak each went red); `selftest_explosiveknockback_stage3_scenes.py` (29 fails on the base commit, 0 now; 3/3
  planted faults caught: a control lane dropped from SceneNames, a missing restore, a sweep field dropped).
- **Mod behaviour:** none changed for players. Proof build only: a debug-vector draw counter in the map component (the
  sweep's debugDrawVectors lane reads it). Release DLL rebuilt with its `.srchash` (the kernel file gained `KbFrameStats`).
- **Tests run:** kernel 164/164, proofgate PASS (proof build compiles; release DLL carries no proof names, RM_FrameProbe
  added to that list), script mock 41/41, settings sweep offline PASS, lint planted 20/20, stage3 scenes PASS; restore
  check stays KNOWN RED with the same 12 pre-existing hits in `RM_KnockbackProof.cs` (12 on the base too), none in the
  new file.
- **Built around, not fixed (bar text is locked):** questions 10, 12, 13 and 14 below.
- **Cost:** about $6.5 of model spend, about 75 minutes wall, 0 of his minutes.
- **Boring enough to automate:** remaking the table and the preflight after a batch; compiling the proof build; the
  scene static check (names, routing, restores) generalises to every mod's proof file.
- **Needed judgment:** staging a real hose-carry job and firing on the walk rather than at Stage; deciding that the sweep's
  game-side half is lanes compared against the default run; spotting that the locked closed-container text says slide
  where the shipped code (on his 2026-11-12 words) throws.

### Questions (open)

1. ~~g4~~ settled 2026-11-14 by the Conductor's decision: a test-only proof hook pins the colonist at 64 to 76 kg (Stage 3).

Questions 10 to 14 are answered in the history entry of 2026-11-15 11:45 AM PST.

### 2026-11-14 9:28 PM PST, stage change: Offline build (Stage 3) to Blind challenge, tests first (Stages 4 and 5) (by CONDUCTOR)

- Why: Stage 3 exit: all 59 bars have a check that runs after tonight's builder; the one walk bar proves at Stage 8
- Checks passed: order, version, hold, every_bar_has_a_check_that_runs, walk_bars_confirmed, table_version, fourth_cycle.
- Steward confirms: walk_storeroom_raid: a walk bar proving at Stage 8, decided by scene sc_walk_raid and his Stage 8 look; correctly not runnable offline (Conductor read the test table 2026-11-14 9:29 PM PST)
- Blind cycle 1 of this visit (1 in all).
- Was, "Stage now": - **Stage now:** Stage 3 ("reconcile") done as far as it goes offline, 2026-11-14 12:45 PST. Preflight re-run: **refuse, 6 refusals** (was 26), all C6 "built: runs" (`version/preflight.json`). Stages 4-5 can start on everything else; the 6 are listed under Stage 3 below with why each was not built.
- Was, "Waiting on": - **Waiting on:** a builder for the 6 unbuilt scenes (or a Stage 4-5 start without them); the questions below.
- Record: `version/stage_record.json`.

### 2026-11-15 12:34 AM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to Blind challenge, tests first (Stages 4 and 5) (by CONDUCTOR)

- Why: Cycle 1 of the blind challenge did not meet the exit (inv_proof_scenes red, four notes for the Conductor); cycle 2 starts with the Conductor's rulings in its brief
- Checks passed: order, version, hold, fourth_cycle.
- Blind cycle 2 of this visit (2 in all).
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-14 9:28 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-14 9:28 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-15 2:14 AM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to In-game acceptance (Stage 6) (by CONDUCTOR)

- Why: Blind challenge cycle 2 exit met by the program's reading after a neutral reconcile (ed645c5495, 709c740f76); night order of 2026-11-15
- Checks passed: order, version, hold, steward_confirms.
- Steward confirms: Read the cycle 2 judge's report and the neutral fixer's: both offline bars green on real reruns (5 deciders), all 10 Problems fixed and shown red at each fix's parent and green at the fix by the fixer's own runs, 29 of 29 planted faults caught, no assertion weakened. The storeroom-mortar criterion was repaired by the neutral fixer (refusal record, re-pin). Held for the owner: the container bar's wording in tree.json and sheet.md (RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING). Every live test is UNRUN and owed to Stage 6.
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-15 12:34 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-15 12:34 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-15 8:34 AM PST, stage change: In-game acceptance (Stage 6) to Offline build (Stage 3) (by BENCH)

- Why: steward run, visit 1 exit not met: 4 FAIL (sc_pit_fetch; gas chain sc_gas_chain/sc_cauldron_gas/P_gas_clumps, one scene) and 5 UNMEASURED (sc_storeroom_bomb_pit, sc_gas_shove_into_pit, sc_goods_obstacles, sc_walk_raid: no entry; sc_closed_containers heavy lane unstageable); not every failure is a blind-lane check (pit_fetch and the gas chain are MOD or Cauldron behaviour), so the road back is offline_build; 8 items filed caused by RIMMANDRAKE_ROUTE_EXPLOSIVEKNOCKBACK_VISIT_ONE_FAILURES
- Checks passed: order, by, version, hold.
- Steward confirms: read design/concepts/ExplosiveKnockback/version/in_game/visit_1/SUMMARY.md exit block (47 pass, 4 fail, 5 unmeasured of 56, exit_met false) and evidence; verdict: road back to offline_build
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-15 2:14 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-15 2:14 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-15 9:04 AM PST, stage change: Offline build (Stage 3) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: steward run: Stage 3 exit met after the visit-1 road back; all 9 items caused by RIMMANDRAKE_ROUTE_EXPLOSIVEKNOCKBACK_VISIT_ONE_FAILURES closed with L0 verifies; every live row UNRUN and owed to Stage 6
- Checks passed: order, by, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle.
- Steward confirms: read maturation next (exit tests order, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle pass) and the ledger: storeroom_bomb_pit 5298951585, gas_into_pit d4e34dda04, goods_obstacles 16a4636cf1, walk_raid live mode 3d1f9ae2ca, heavy locker lane 7c910364ce, gas chain fix d1817022db (cauldron fuzz 17002 cases), pit_fetch runner advance 266aaf93ef, pit_fetch control fixed ladder 7c17ebc622, steward git-lock retry 79a4ef9107: each closed with a pass verify, base watched red; live reruns UNRUN with commands recorded. Verdict: advance to blind_challenge
- Blind cycle 1 of this visit (3 in all).
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-15 8:34 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-15 8:34 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-15 11:45 AM PST, questions 10 to 14 answered (by BENCH)

Delegated under his Evidence-for-Ask ruling (RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME): each takes the
answer the locked bar, his recorded words or the shipped code already gives; no evidence against it was found.

- This answers question 10: the leaf is right. Steward decision 6 of blind cycle 2 (`version/blind_challenge/cycle_2/SUMMARY.md`)
  added the setting, built at 587529cee1: `closedContainerGuard`, "Closed containers protect their goods" (`RM_KnockbackMod.cs`).
- This answers question 11: the walk row yields to its bar (steward decision 8, 587529cee1): off means goods are not thrown,
  and `validation.py` now reads `off_goods_unthrown`.
- This answers question 12: he answered it himself, "Throw it, as built" (OWNER:1794721689897638306), and recertified the
  rule (OWNER:1794748823561950419); sc_closed_containers is re-pinned to "thrown a short way" (`version/bars.md`).
- This answers question 13: 0.1.0 owes the drawn jolt, and steward decision 6 built it (`RM_MapComponent_Knockback.cs`
  MapComponentUpdate). The scene's offset row still prints `drawnOffset=UNMEASURED` (`RM_KnockbackProof_StageThree.cs`),
  because the proof counters are map-wide and per frame; wiring a per-container read is item
  RIMMANDRAKE_READ_CONTAINER_JOLT_OFFSET_IN_PROOF.
- This answers question 14: `fireAtHalf`, "Fire throws at half strength", exists (steward decision 6, 587529cee1) and the
  `fireHalf` lane switches it. Still owed by the steward at the next re-pin: name `closedContainerGuard` and `fireAtHalf` in
  sc_settings_sweep's action.

### 2026-11-15 2:08 PM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: delegated: steward road back: cycle 3 fixed 3 Problems (RIMMANDRAKE_SWITCH_ELECTRICAL_BURN_WITH_FIRE_HALF_FLAME_HEIR, RIMMANDRAKE_PROVE_PROOF_GATE_EXIT_AN_OR_PASSED_GREEN, RIMMANDRAKE_RUN_STOREROOM_RESTORE_WAIVER_TAKEN_ON_TRUST, red first); his road back sends a fixed mod to a new blind judgement pass; judge's exit_met true came from the brief defect fixed in 228cb916de; nothing new filed (3 Polish already filed by the judge)
- Checks passed: order, by, version, hold, fourth_cycle.
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: delegated: steward road back: cycle 3 fixed 3 Problems (RIMMANDRAKE_SWITCH_ELECTRICAL_BURN_WITH_FIRE_HALF_FLAME_HEIR, RIMMANDRAKE_PROVE_PROOF_GATE_EXIT_AN_OR_PASSED_GREEN, RIMMANDRAKE_RUN_STOREROOM_RESTORE_WAIVER_TAKEN_ON_TRUST, red first); his road back sends a fixed mod to a new blind judgement pass; judge's exit_met true came from the brief defect fixed in 228cb916de; nothing new filed (3 Polish already filed by the judge)
- Blind cycle 2 of this visit (4 in all).
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-15 9:04 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-15 9:04 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-15 3:13 PM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to In-game acceptance (Stage 6) (by BENCH)

- Why: delegated: steward advance: blind cycle 4 exit met, verified against its own files; Polish call on L1_PATH_RANDOM_CONSERVATION concurred (his confirmation of the Polish-list move asked by card)
- Checks passed: order, by, version, hold, steward_confirms.
- Steward confirms: Read version/blind_challenge/cycle_4/SUMMARY.md, lane1/lane1_rows.jsonl (60 rows: 22 PASS, 1 FAIL, 6 INFO, 31 UNSETTLED not_kernel), lane2/faults.json (0 Problems, 1 Polish), reruns.jsonl (16/16 PASS), planted_results (41 of 50 caught, 9 misses carried to Stage 6) and tests_edited.json ([]; no test or mod file changed after the cycle opened 14:14 PST, last EK edit bace1c29cc 13:36). Reran the five offline deciders myself: T_KERNEL 180/180, T_FUZZ 42001 OK, T_SCRIPT, T_PROOFGATE, T_RESTORE all PASS. Judge the judge: maturation next gives no not-met reason, so nothing to sort as record gap, criterion flaw or real miss. The one FAIL, L1_PATH_RANDOM_CONSERVATION (a hit across a sandbag with no contact, 42/30000 random grids), I read as Polish: no bar's words break, and in game it reads as blast damage to a pawn that does not move. Verdict: exit met; advance to in_game. Test table regenerated by its maker (stale known_reds of closed items dropped, inv_proof_scenes now offline-green).
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: delegated: steward advance: blind cycle 4 exit met, verified against its own files; Polish call on L1_PATH_RANDOM_CONSERVATION concurred (his confirmation of the Polish-list move asked by card)
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-15 2:08 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-15 2:08 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-15 5:50 PM PST, stage change: In-game acceptance (Stage 6) to Offline build (Stage 3) (by BENCH)

- Why: delegated: steward road back: in-game visit 2 exit not met (52 PASS, 3 FAIL, 1 UNMEASURED of 56); 4 lines filed caused by RIMMANDRAKE_ROUTE_EXPLOSIVEKNOCKBACK_VISIT_TWO_FAILURES; offline_build because pit_fetch and walk_raid may be mod defects, not only blind-lane checks
- Checks passed: order, by, version, hold.
- Steward confirms: read design/concepts/ExplosiveKnockback/version/in_game/visit_2/SUMMARY.md and rows.jsonl: sc_storeroom_bomb_pit UNMEASURED (REAL MISS, harness never staged), sc_pit_fetch FAIL (REAL MISS), sc_walk_raid FAIL (REAL MISS), sc_barrage_perf FAIL (CRITERION FLAW suspected: mod-off control fails the 50 ms bar too; neutral fixer + refusal record); no RECORD GAP; cycle 4 tests_edited.json empty; verdict: road back to offline_build
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: delegated: steward road back: in-game visit 2 exit not met (52 PASS, 3 FAIL, 1 UNMEASURED of 56); 4 lines filed caused by RIMMANDRAKE_ROUTE_EXPLOSIVEKNOCKBACK_VISIT_TWO_FAILURES; offline_build because pit_fetch and walk_raid may be mod defects, not only blind-lane checks
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-15 3:13 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-15 3:13 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-16 1:18 AM PST, stage change: Offline build (Stage 3) to In-game acceptance (Stage 6) (by BENCH)

- Why: every open road-back item of the visit 2 road back needs the live game: the dry-pit hauler fault has no offline cause yet (only a live job-logging experiment can show it); walk-raid and barrage have their offline halves landed and green, and only their live reruns remain, being worked now by live holder rm-detached-bench-rimmandrake-fix-dry-pit-hauler-descent-s-1794816095. Offline stages never wait for a game (RIMMANDRAKE_CLOSE_OFFLINE_STAGE_ITEMS_OFFLINE_GAME_WAS_DEMANDED)
- Checks passed: order, game_only, by, version, hold.
- Game only: RIMMANDRAKE_FIX_DRY_PIT_HAULER_DESCENT_SWIMS_HID_IT, RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES, RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-15 5:50 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-15 5:50 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-16 12:28 PM PST, stage change: In-game acceptance (Stage 6) to Offline build (Stage 3) (by BENCH)

- Why: steward run: visit 3 exit not met; the one FAIL (sc_storeroom_bomb_pit cover half, REAL MISS: no code breaks a cover under a landing stack) is offline-fixable C#, filed RIMMANDRAKE_BREAK_COVER_UNDER_LANDING_STACK_STILL_WHOLE --needs offline; sc_walk_raid UNMEASURED already resolved by closed RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES (773b9baea3, 18/18 PASS), the next visit reruns it
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_3 SUMMARY.md and rows.jsonl last rows: 54 PASS, sc_storeroom_bomb_pit FAIL (cover gone=False; goods half harness fix 6ab864cf7e judged a repair aligned with inv_too_weak_skip, not a weakening), sc_walk_raid UNMEASURED (later PASS by the pilot); verdict: road back to offline_build for one MOD fix
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: steward run: visit 3 exit not met; the one FAIL (sc_storeroom_bomb_pit cover half, REAL MISS: no code breaks a cover under a landing stack) is offline-fixable C#, filed RIMMANDRAKE_BREAK_COVER_UNDER_LANDING_STACK_STILL_WHOLE --needs offline; sc_walk_raid UNMEASURED already resolved by closed RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES (773b9baea3, 18/18 PASS), the next visit reruns it
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-16 1:18 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-16 1:18 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-16 1:43 PM PST, stage change: Offline build (Stage 3) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: steward: every Stage 3 exit test passes (order, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate); the visit-3 REAL MISS RIMMANDRAKE_BREAK_COVER_UNDER_LANDING_STACK_STILL_WHOLE closed at a9eedde493 with tests added only, certificate rerun 81519824c0
- Checks passed: order, by, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate.
- Steward confirms: read maturation.py next: no not-met reasons to sort (no RECORD GAP, CRITERION FLAW or REAL MISS); a9eedde493 adds 20 selftest lines, deletes none; verdict: advance
- Blind cycle 1 of this visit (5 in all).
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-16 12:28 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-16 12:28 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-16 10:21 PM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: steward road back: blind cycle 5 exit not met; 2 Problems filed under RIMMANDRAKE_ROUTE_EXPLOSIVEKNOCKBACK_CYCLE_FIVE_FAILURES (RIMMANDRAKE_DROP_THROWS_INTO_COVERED_PITS_K08_MUST_FLIP, RIMMANDRAKE_LIFT_PROOF_VERDICTS_INTO_TESTED_CODE_NINE_SLIPPED); cycle 6 judges their fixes and the judge's own fix 42225e0686
- Checks passed: order, by, version, hold, fourth_cycle, judge_certificate.
- Steward confirms: Read cycle_5/SUMMARY.md, lane2/faults.json, planted_results.jsonl, tests_edited.json (K-25 added, 14 insertions, 0 deletions: no assertion weakened). Judge the judge: RIMMANDRAKE_STOP_THROWS_OVER_COVERED_PITS_K08_SAYS_GROUND = REAL MISS (sc_pit_fall's locked expect demands the covered lane; accept_covered_pit.py rc 1, 2 of 6 at 10abd71ff0, watched). RIMMANDRAKE_PIN_KNOCKBACK_PROOF_VERDICTS_NINE_MUTANTS_UNSEEN = REAL MISS, not a criterion flaw (a correct build can lift verdict arithmetic into tested code, the judge's own would_pass); re-pin not taken (it would change what decides inv_proof_scenes). Stale T_KERNEL runs_today = RECORD GAP, redone: certificate --run, 16 offline tests; T_RESTORE red on Pyrelands wind_burn_live.py:56 was a checker false positive, fixed 20eca8db5d. Certificate OK. Verdict: exit not met; road back to blind_challenge, cycle 6 (visit 2 of 3).
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: steward road back: blind cycle 5 exit not met; 2 Problems filed under RIMMANDRAKE_ROUTE_EXPLOSIVEKNOCKBACK_CYCLE_FIVE_FAILURES (RIMMANDRAKE_DROP_THROWS_INTO_COVERED_PITS_K08_MUST_FLIP, RIMMANDRAKE_LIFT_PROOF_VERDICTS_INTO_TESTED_CODE_NINE_SLIPPED); cycle 6 judges their fixes and the judge's own fix 42225e0686
- Blind cycle 2 of this visit (6 in all).
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-16 1:43 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-16 1:43 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-23 6:21 AM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to In-game acceptance (Stage 6) (by BENCH)

- Why: delegated: steward advance: blind cycle 6 exit met at 6586e989e2 (the judge was killed; the steward completed its record from its own reruns at e0e997836e; the one fresh reader read the mod fix fa2de6ee4b sound); certificate --to in_game rc 0
- Checks passed: order, by, version, hold, steward_confirms, exit_met, judge_certificate.
- Steward confirms: run-1795441975 read cycle_6 SUMMARY, faults, fixes, tests_edited (M04 narrowed: stronger; restore BASELINE: check repair shown red on a planted EK leak), planted results (12 not caught, all in the two open findings' classes), and read fa2de6ee4b once: sound. Polish confirmed for lane-1 rows L1_FIRE_SWITCH_ON_UNPATCHED_FIRE_TYPE and L1_GAS_SHOVE_PAWN_ON_INTACT_COVER (no failure, no concrete case in normal play; test 1 fails). Verdict: exit met.
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-16 10:21 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-16 10:21 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-23 11:44 AM PST, stage change: In-game acceptance (Stage 6) to In-game acceptance (Stage 6) (by BENCH)

- Why: steward road back: visit 4 exit not met; every open line is game-only: sc_spared (SITE, four bars undecided, RIMMANDRAKE_HOLD_SPARED_CARRIER_IN_BLAST_IT_WALKED_AWAY) and sc_walk_raid (HARNESS/SITE, RIMMANDRAKE_RUN_KNOCKBACK_WALK_FRAME_ARMS_SMALL_COLONY_ABSENT); no mod-wrong line open: fix 2590111487 read sound dc7550420b; koth.isid identity fixed 4ecd015e866f
- Checks passed: order, by, version, hold.
- Steward confirms: run-1795461416 read visit_4 SUMMARY, rows, strange, the three commits that touched tests (cabe962231, 092b2e358b: lanes and a memory reset added, no assertion weakened) and read fix 2590111487 once: sound. 22 of 23 EK offline selftests rc 0, selftest_explosiveknockback_map.py past my 110 s limit: UNMEASURED. Verdict: next visit, never a stage back.
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: steward road back: visit 4 exit not met; every open line is game-only: sc_spared (SITE, four bars undecided, RIMMANDRAKE_HOLD_SPARED_CARRIER_IN_BLAST_IT_WALKED_AWAY) and sc_walk_raid (HARNESS/SITE, RIMMANDRAKE_RUN_KNOCKBACK_WALK_FRAME_ARMS_SMALL_COLONY_ABSENT); no mod-wrong line open: fix 2590111487 read sound dc7550420b; koth.isid identity fixed 4ecd015e866f
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-23 6:21 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-23 6:21 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-23 6:14 PM PST, stage change: In-game acceptance (Stage 6) to Walk brief (Stage 7) (by BENCH)

- Why: Stage 6 exit met at visit 5 (run-1795478277, unit rm-detached-bench-rimmandrake-drive-explosiveknockback-in-1795478768): build match counts 56 of 56, SUMMARY and rows read by the steward bear it out
- Checks passed: order, by, version, hold, steward_confirms, exit_met, build_match.
- Steward confirms: visit 5 (run-1795478277): read SUMMARY.md, all 10 rows, their evidence, strange.jsonl, screenshots and the diffs fa3f95313d and 6dfc987697. sc_spared, sc_frame_probe_check, sc_barrage_perf (p99 22.1 ms, limit 50, mod off 21.7) and sc_walk_raid (18 of 18) PASS; the reload repair waits only, seen FAIL on planted goods lost on reload and PASS on the real build; the mod's own code is unchanged since visit 4, so its 52 rows stand; build_match rerun: 56 count, 0 to run. Verdict: exit met.
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-23 11:44 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-23 11:44 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-23 7:31 PM PST, stage change: Walk brief (Stage 7) to His live walk (Stage 8) (by BENCH)

- Why: walk brief arrival_1 written
- Checks passed: order, by, version, hold, walk_brief, walk_items_closed.
- Was, "Stage now": - **Stage now:** Stage 7, the walk brief, since 2026-11-23 6:14 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-23 6:14 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-23 7:31 PM PST, stage change: His live walk (Stage 8) to In-game acceptance (Stage 6) (by BENCH)

- Why: steward road back, before he walks: the mod's code changed at db80fab783 (gas corner, the Conductor's call of 2026-11-23 6:24 PM PST: a Problem of 0.1.0, fixed before his walk). build_match: 54 of 56 count, sc_barrage_perf and sc_walk_raid (full list, ArchBig) to run; both need the game (RIMMANDRAKE_RUN_KNOCKBACK_FULL_LIST_CHECKS_AFTER_GAS_CORNER_FIX). Back to Stage 6 for exactly those 2; no mod-wrong line open; fix db80fab783 read sound. Precedent: FlowWorks his_walk to in_game 2026-11-21
- Checks passed: order, by, version, hold.
- Steward confirms: read db80fab783 once (sound, visit_5/fix_reviews.jsonl), selftest map PASS 31 of 31 faults, before DISAGREE / after AGREE 123 of 123, build_match 54 of 56
- Was, "Stage now": - **Stage now:** Stage 8, his live walk, since 2026-11-23 7:31 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-23 7:31 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-24 11:41 AM PST, stage change: In-game acceptance (Stage 6) to Walk brief (Stage 7) (by BENCH)

- Why: Stage 6 exit met at visit 6 (run-1795510833): 56 of 56 checks PASS and count on the walk build e089dc2573; ArchBig's DLL equals the committed one; steward read SUMMARY, 140 rows and evidence
- Checks passed: order, by, version, hold, steward_confirms, exit_met, build_match, unrun_run.
- Steward confirms: visit 6 (drive run-1795510833, read by run-1795548573): SUMMARY.md, 140 rows, strange, planted, fix_reviews (1acc05e0ed, d61b1e2b31, e089dc2573 read sound by an earlier steward; none owed) and the evidence files. Last rows 57 of 57 PASS on e089dc2573 (56 checks, 1 map agreement); no evidence file has FAIL, UNMEASURED or INVALID; build_match 56 of 56, 0 to run, no undecided bar; ArchBig DLL md5 equals the committed DLL (c41f0c11); only a proof script changed since. sc_walk_blasts repair a1dd0592dc planted FAIL, real PASS. sc_blast_kinds stages no Outer Rim lane (table partial): its bar is decided by P_harmful_unpatched (untuned Thump 100 percent, 3 cells as Bomb) and P_fire_half, and OuterRim_Sonic is DamageWorker_AddInjury, untuned, so the same path. Verdict: exit met.
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: Stage 6 exit met at visit 6 (run-1795510833): 56 of 56 checks PASS and count on the walk build e089dc2573; ArchBig's DLL equals the committed one; steward read SUMMARY, 140 rows and evidence
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-23 7:31 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-23 7:31 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-24 2:58 PM PST, stage change: Walk brief (Stage 7) to His live walk (Stage 8) (by BENCH)

- Why: walk brief arrival_2 written
- Checks passed: order, by, version, hold, walk_checks_stand, walk_brief, walk_items_closed.
- Was, "Stage now": - **Stage now:** Stage 7, the walk brief, since 2026-11-24 11:41 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** the Dispatch tick's walk-brief run (Stage 7, arrival 2; visit 6's own session wrote arrival 1, so a fresh run writes it). Walk save EK_VISIT6_WALK_20261124_C on ArchBig, which holds the walk build.
- Record: `version/stage_record.json`.

### 2026-11-24 3:44 PM PST, stage change: His live walk (Stage 8) to Version passed (Passed) (by CONDUCTOR)

- Why: his live walk of Explosive Knockback 0.1.0 on ArchSmall, save EK_VISIT6_WALK_20261124_C, walk brief arrival_2.md, 2026-11-24; item RIMMANDRAKE_RECORD_KNOCKBACK_VERSION_PASS_HE_CALLED_THE_WALK_VERY_FUN
- Checks passed: order, by, version, hold, owner_said, walk_build, raid_bars_decided, pass_record_new.
- Owner said: OWNER:1795563826491035058
- Was, "Stage now": - **Stage now:** Stage 8, his live walk, since 2026-11-24 2:58 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-24 2:58 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-24 4:34 PM PST, version change: 0.1.0 to 0.2.0 (by CONDUCTOR)

- Why: 0.2.0 (MINOR) opened on his words of 2026-11-24 (OWNER:1795565769863524396, OWNER:1795565863812726726): the carried thing on its own arc, collision bruises by size, our own blast show (design/specs/2026-11-24-knockback-blast-show/design.md) and three polish lines the Conductor judged relevant; 73 bars, every 0.1.0 bar kept; item RIMMANDRAKE_OPEN_KNOCKBACK_ZERO_TWO_BLAST_SHOW_HE_SAID_GET_CREATIVE
- The 0.1.0 record (at Version passed (Passed)) is kept as `version/stage_record_0.1.0.json`.
- Its numbered evidence (14 cycle, visit and arrival paths) is set aside in `version/previous/0.1.0`.
- Was, "Stage now": - **Stage now:** Version passed on his word, since 2026-11-24 3:44 PM PST (`version/stage_record.json`).
- Record: `version/stage_record.json`.

### 2026-11-24 5:07 PM PST, Preflight (Stage 2) for 0.2.0 (steward run RIMMANDRAKE_STEWARD_EXPLOSIVEKNOCKBACK_PREFLIGHT_STAGE, BENCH)

- First run of the 0.1.0 program on the 0.2.0 folder: 18 refusals. 14 were the 0.2.0 bars absent from `version/test_table.json` (C1). 4 were `version/bars.md` pins (C12): the 0.2.0 lock kept the last 0.1.0 pins, which predate his frame-row rulings of 2026-11-15 and 2026-11-16 (applied and passed in 0.1.0).
- Re-pin, a fault of form: `version/bars.md` now pins each locked file at the 0.2.0 lock commit `c276d1b00edd`. Every file is byte-identical to its lock blob, so no bar's meaning moved. Its 0.1.0 text was a byte-for-byte copy of `version/previous/0.1.0/bars.md`; it was removed and that path is named.
- Test table: the 14 bars added with the deciders that each bar's `record.json` proof_note names (`version/pilot_throwaway/extend_test_table_0_2_0.py`). The 14 new tests are `new: true`: specified, and Stage 3 builds each red first. `sc_blast_show` carries a `cheaper_why`.
- Program: `version/pilot_throwaway/preflight_ek_0_2_0.py`, a copy of the 0.1.0 program. It reads the version from VERSION.json. C6 counts a `new: true` decider as Stage 3 work, not a refusal (spec, Stage 2 exit). C6 refuses a `new` flag whose kernel marker is already built. Planted faults gave red on C6 (2) and C12 (1).
- Two scope items named in VERSION.json were not on the ledger (C15). They are filed now under their scope names: RIMMANDRAKE_FOLD_KNOCKBACK_POLISH_LINES_INTO_ZERO_TWO_THREE_JUDGED_IN and RIMMANDRAKE_REWORD_KNOCKBACK_REBOUND_LEAF_THEN_RETAKE_WHOLE_EXAM.
- Result: `version/preflight.json` for 0.2.0, verdict pass, 0 refusals, about 11 s.

### 2026-11-24 5:09 PM PST, stage change: Preflight (Stage 2) to Offline build (Stage 3) (by BENCH)

- Why: Preflight (Stage 2) for 0.2.0 passes: version/preflight.json verdict pass, 0 refusals, 15 checks, by version/pilot_throwaway/preflight_ek_0_2_0.py at 9883d9cf762c; item RIMMANDRAKE_STEWARD_EXPLOSIVEKNOCKBACK_PREFLIGHT_STAGE
- Checks passed: order, by, version, hold, preflight_record.
- Steward confirms: read version/preflight.json (0.2.0, pass, 0 refusals), VERSION.json bars_new (14), record.json proof_note of each new bar, version/bars.md (pins = lock commit c276d1b00edd blobs; every locked file byte-identical, no bar meaning moved), version/test_table.json (73 bars = locked_bars.json; 14 new deciders new: true, Stage 3 builds them red first: offline-build work, not a spec fault)
- Was, "Stage now": - **Stage now:** Stage 2, preflight, since 2026-11-24 4:34 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-24 3:44 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-24 9:00 PM PST, Stage 3 build batch: the blast show's checks (RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_FOURTEEN_BARS_LEFT, BENCH)

- Built the blast show's kernel (`Source/RM_KnockbackShowPlan.cs`, Verse-free; its generator `Source/SelfTestShow`), its hook and drawing (`Source/RM_KnockbackShow.cs`: fire and flash, shake, ripple, scars), four part switches with the shake slider and the marks-last choice, the fleck and scar defs, the offline check T_BLAST_SHOW_OFFLINE (`selftest_explosiveknockback_blast_show.py`, seen red first and red-seen on a planted fault) and the live scene sc_blast_show (`proof/scene_blast_show.py`, UNRUN); the table maker now measures what is built. Bars not runnable: 14 before, 6 after. T_BLAST_SHOW_OFFLINE runs red until the queued art (22 jobs, `version/art/blast_show_art_0_2_0.json`) is installed and the smoke and soot parts are built.

### 2026-11-24 10:43 PM PST, Stage 3 build batch: the six bars left (RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_SIX_BARS_LEFT, BENCH)

- Built four behaviours, kernel first, each case seen red (absent functions) before the code: the carried thing on its own plan (`KbPlanner.Carried`/`CarriedRest`; game side `ThrowCarried` and `RM_ThingFlyer_Knockback.LaunchFromHands`, the pawn now flies with `flyWithCarriedThing: false`), the bruise by size (`RM_KnockbackMath.CollisionBruise`, `KbPlanner.Collide`, on a path hit and on a landing), no hit across a sandbag (new stop `PawnBeyondCover`), and the burning-gas shove of a person on an intact cover (`KbFacts.onCover`). Offline deciders: K_CARRY_OWN_PLAN, K_COLLISION_BRUISE, K_GAS_COVER_SHOVE, K_NO_CONTACT (kernel 277/277, sweeps of 1200, 5043, 150 and 13104 cases, 0 failing) and T_CARRY_STATIC (red on the 0.1.0 code); T_SETTINGS_SWEEP_SHOW (red while smoke and soot have no switch: RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS); six live scenes on the scene library, UNRUN. Every edited decider has its red run in `version/evidence/red_seen.json`.
- Old checks that turned red, and why: the fuzz walker and blind cycle 1 encoded the 0.1.0 hit across a sandbag (the walker now holds the 0.2.0 rule; the stop got its own name so the cycle-1 invariant stands); a map plant and a lint plant pointed at reworded lines; blind cycle 1 had lost its lanes to `version/previous/0.1.0`; T_RESTORE was red on plant settings left unrestored in five scenes (fixed in all five).
- Bars not runnable: 6 before, 0 after. The judge certificate refuses 10 bars, all the blast show's (art and the smoke and soot parts are still owed).

## 2026-11-24 — the blast show's last three parts and its art (RIMMANDRAKE_GREEN_EXPLOSIVEKNOCKBACK_T_BLAST_SHOW_RED_DECIDER)

- Red cause: not a regression. T_BLAST_SHOW_OFFLINE and T_SETTINGS_SWEEP_SHOW were red by design until the smoke and soot parts were built and the art was installed.
- Built smoke (non-rotating flecks that rise and lean with the wind; a barrage cap of three blasts' worth of puffs), soot on things (Pyrelands' paint slot and RM_FE_Charred, added by a patch when Pyrelands is absent; `RM_MapComponent_Soot` gives the old paint back as the soot wears off, and drops the record when the player repaints), and soot on pawns (hediff `RM_KnockbackSoot` that carries its own render nodes, drawn as firefoam is; it wears off and washes off in rain or water).
- A conflict found before it went red: the plan's one `sootReach` served both soot parts, so one soot switch off could not give its part the unmodded look (S_OFF_OWN). Split into `sootThingsReach` and `sootPawnsReach`; the kernel's S_SWITCH now checks both.
- Art: 10 new jobs (6 smoke, 4 soot tiles); a fresh Opus judge accepted 30 of 32, refused spark_a (grey box) and smoke_e (pale rim); both rerolls accepted; 34 verdicts in `version/art/blast_show_art_verdict_2026-11-24.json`; 32 installed by `art install`.
- Red seen on planted faults: T_BLAST_SHOW_OFFLINE and T_SETTINGS_SWEEP_SHOW (`evidence/plants/soot_pawns_on_things_switch.patch`), T_SETTINGS_SWEEP_OFFLINE (`evidence/plants/soot_setting_unswept.patch`). sc_blast_show gains V_SOOT_THING and V_SOOT_PAWN (UNRUN); the sweep's showOff lane turns the three new switches off too (UNRUN).

### 2026-11-25 4:42 AM PST, stage change: Offline build (Stage 3) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: Stage 3 offline build for 0.2.0: every exit test passes (order, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate); item RIMMANDRAKE_ADVANCE_EXPLOSIVEKNOCKBACK_PAST_OFFLINE_BUILD
- Checks passed: order, by, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate.
- Steward confirms: read maturation.py next (0 refusals, 0 hand steps, no fix readers owed, no blind cycle open); ran judge_certificate.certify: ok, did_not_run [], 296 rows = 279 PASS + 17 WARN, every WARN a grandfathered red_seen on a test file unchanged since red_seen_grandfather.json (no red proof owed); bar rebound_goes_shorter loosened at 380aa4ee6d is a logged Conductor act under RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS with lost/undo, not re-judged here. Verdict: advance.
- Blind cycle 1 of this visit (1 in all).
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-24 5:09 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-24 5:09 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-25 6:33 AM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to In-game acceptance (Stage 6) (by BENCH)

- Why: steward run RIMMANDRAKE_CONFIRM_EXPLOSIVEKNOCKBACK_CYCLE_ONE_EXIT_MET: blind cycle 1 exit met, read and confirmed
- Checks passed: order, by, version, hold, steward_confirms, exit_met, judge_certificate.
- Steward confirms: read blind_challenge/cycle_1 SUMMARY.md, faults.json, fixes.jsonl, tests_edited.json and row files: lane1 after fix 28 PASS/0 FAIL/1 INFO/71 UNSETTLED (all not_kernel, game-side, none on inv_kernel or inv_proof_scenes); reruns 36/36 PASS; planted 31/35 caught, 4 misses explained (2 Polish owned by Stage 6 scenes, 1 owned by sc_pawn_arc_bruise_sizes, 1 equivalent mutant); 1 Problem (check) FIXED 08b632f259, T_PROOFGATE D1 additive only, nothing weakened; I reran D1 myself: PASS on HEAD, FAIL 'no Build case for wall_stop' on P_SCENE_CASE_RENAMED; red_seen recorded. No mod fix, so no fix reader owed. Verdict: exit met.
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-25 4:42 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-25 4:42 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-25 9:58 AM PST, stage change: In-game acceptance (Stage 6) to Offline build (Stage 3) (by BENCH)

- Why: Conductor's brief (steward act after in-game visit 1): send ExplosiveKnockback 0.2.0 down its road back to the nearest stage that repairs every mod-wrong line. offline_build: the scar-def rename (RIMMANDRAKE_RENAME_KNOCKBACK_SCAR_DEFS_DIGIT_ENDING_CONFIG_ERROR) and the missing IED scar (RIMMANDRAKE_FIND_KNOCKBACK_IED_SCAR_MISSING_ONE_RUN_IN_THREE, sc_blast_show MOD FAILURE) are changes of mod code/defs; RIMMANDRAKE_COVER_KNOCKBACK_BAR_HALVES_NO_LIVE_CHECK_SEES and RIMMANDRAKE_CLASS_KNOCKBACK_SHELL_KILLS_COLONIST_TWO_OF_FIVE_RUNS go with it; P_goods_fly_wall/P_goods_fly_rebound stay UNRESOLVED, owned by RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS
- Checks passed: order, by, version, hold.
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: Conductor's brief (steward act after in-game visit 1): send ExplosiveKnockback 0.2.0 down its road back to the nearest stage that repairs every mod-wrong line. offline_build: the scar-def rename (RIMMANDRAKE_RENAME_KNOCKBACK_SCAR_DEFS_DIGIT_ENDING_CONFIG_ERROR) and the missing IED scar (RIMMANDRAKE_FIND_KNOCKBACK_IED_SCAR_MISSING_ONE_RUN_IN_THREE, sc_blast_show MOD FAILURE) are changes of mod code/defs; RIMMANDRAKE_COVER_KNOCKBACK_BAR_HALVES_NO_LIVE_CHECK_SEES and RIMMANDRAKE_CLASS_KNOCKBACK_SHELL_KILLS_COLONIST_TWO_OF_FIVE_RUNS go with it; P_goods_fly_wall/P_goods_fly_rebound stay UNRESOLVED, owned by RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-25 6:33 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-25 6:33 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-25 7:01 PM PST, stage change: Offline build (Stage 3) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: steward: every Stage 3 exit test passes (maturation.py next); certificate --to blind_challenge OK at HEAD, 58 bars certified
- Checks passed: order, by, version, hold, road_back_items, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate.
- Steward confirms: read maturation.py next (all 8 exit tests passing, no fix reader owed) and certificate --to blind_challenge (OK, 58 bars, 7 grandfathered red_seen); verdict: advance
- Blind cycle 1 of this visit (2 in all).
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-25 9:58 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-25 9:58 AM PST).
- Record: `version/stage_record.json`.
