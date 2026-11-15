# Explosive Knockback: journal

The mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. Below it the
**history** is only added to. Test of this file: a restarted Conductor can do the next stage change from it alone.

## The mod as it stands

- **Design Version 0.1.0, locked** on his word 2026-11-13 (`version/VERSION.json`). Code exists:
  `src/RimMandrake/ExplosiveKnockback/`.
- **Stage now:** Stage 3 ("reconcile") done as far as it goes offline, 2026-11-14 12:45 PST. Preflight re-run:
  **refuse, 6 refusals** (was 26), all C6 "built: runs" (`version/preflight.json`). Stages 4-5 can start on everything
  else; the 6 are listed under Stage 3 below with why each was not built.
- **Bars:** 59 (30 inventory rows of `record.json` + 29 leaves of `tree.json`). The test-and-stage table is
  `version/test_table.json` (read view `version/test_table.md`).
- **Measured 2026-11-14 12:45 PST:** 53 of 59 bars have at least one test that runs today; 47 have every deciding test
  runnable; 41 have all their offline deciding tests green. All 15 offline tests are built (13 PASS, 2 known red,
  unchanged). In-game scenes: 56, entry exists 50, absent 6. Every in-game scene is UNRUN (Stage 6); commands in the table.
- **Waiting on:** a builder for the 6 unbuilt scenes (or a Stage 4-5 start without them); the questions below.
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
10. **The leaf settings_scale_and_switch names a "closed guard off" setting, but no such setting exists**
    (`RM_KnockbackMod.cs` saves 46 settings; none switches the closed-container guard off: `shoveClosedContainers` throws the
    container whole, `vanillaCratesClosed` covers only vanilla's sealed crates). Either the leaf's word is wrong or a setting is missing; it is bar text, so not edited here.
11. **One walk row contradicts a bar**: `flying_goods.off_is_the_instant_move` says goods in the air off means an
    instant move, while the bar says goods are then not thrown at all (`version/bar_lists_map.json`). Stage 6 reports
    against the 59, but `validation.py` still reads the walk, so the row would report against the bar.
12. **sc_closed_containers says a container "slid one cell (action slide)"; the shipped code throws it whole** (on his
    2026-11-12 words, "the whole crate/chest would go flying a bit", item RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE),
    journaled as action `thrown`, possibly more than one cell. The scene checks "moved exactly one cell away" and reports the
    action word; Stage 6 may fail it on distance. Which is right for 0.1.0: the bar's one-cell slide, or the throw?
13. **The same scene asks for "a drawn offset above zero in the thing trace" for each jolt**, but no thing trace exists and
    a jolt draws nothing (`RM_MapComponent_Knockback.cs` journals `jolt` only). Reported UNMEASURED; building it is a
    visible behaviour plus an instrument, so it is the Conductor's call whether 0.1.0 owes it.
14. **sc_settings_sweep switches "fire at half" off, but no Mod Settings field does that**; the same scene's expect says the
    fire half is a def-patch value proven in sc_blast_kinds. The `fireHalf` lane answers INVALID with that reason, like
    `closedGuard` (question 10).
