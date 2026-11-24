# Pyrelands: journal

The mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. Below it the
**history** is only added to. Test of this file: a restarted Conductor can do the next stage change from it alone.

Pyrelands is not the pilot. It advances beside the pilot (Explosive Knockback), offline only (owner, by card
2026-11-14: "All four now, offline only"). Its numbers are its own; none is copied from Explosive Knockback.

## The mod as it stands

- **Design Version 0.1.0, locked** on his word 2026-11-13 (`version/VERSION.json`). Scope: the biome alone; the Deep
  Desert Tribes are a separate mod (`design/concepts/PyrelandsMechanics`), started only after this version passes.
  Code exists: `src/RimMandrake/Pyrelands/` (packageId `mandrake.rm.pyrelands`, ships composed in `mandrake.rm.biomes`).
- **Stage now:** Stage 8, his live walk, since 2026-11-24 3:21 PM PST (`version/stage_record.json`).
- **Bars:** 42 (21 inventory rows of `record.json` + 21 leaves of `tree.json`), as `version/bars.md` counts them; 41 at
  the lock, `inv_firehawk_hunt_rewards` added by his card 2026-11-14.
  Two inventory rows (`inv_firebreak_firefoam`, `inv_lightning_breaker`) are scope `out`: cut, kept only as absence checks.
  The test-and-stage table is `version/test_table.json` (read view `version/test_table.md`), same columns as Explosive
  Knockback's.
- **Measured 2026-11-14 12:35 (after Stage 3):** all 41 bars have every deciding test runnable today (offline green, or a
  live scene whose entry exists in `validation.py`); 14 have an offline deciding test green; the 6 decided offline only are
  all built and green. 15 built offline tests ran green for this mod, 0 specified. All 23 scenes have an entry. No live
  scene ran (offline only); the four new entries are UNRUN with their commands in `version/test_table.json`.
- **Measured 2026-11-14 14:19 (the hunt-rewards bar added):** 42 bars, all with every deciding test runnable today; 15
  with an offline deciding test green; 17 built offline tests green (`T_FH_LETTER`, `T_FH_CRESTFEATHER` new in the table).
  The two live chains in `firehawk_rewards_live.py` have their entries and are UNRUN (offline only).
- **Judge gaps:** 18 from the round-6 coverage verdict (rm-coverage-judge-1794750987, `version/gaps_sorted.md` Round 6):
  14 PROBLEM, 3 CORRECTION, 1 POLISH (g3). By his card 2026-11-15 12:22 PM PST the 17 are fixed in one locked change
  (`RIMMANDRAKE_FIX_PYRELANDS_ROUND_SIX_SEVENTEEN_GAPS`); g3 stays in `version/polish.md`, out of passing.
- **Held look statements for this mod:** 0 (measured).
- **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-24 3:21 PM PST).

### The vision (his root paragraph, approved by card 2026-11-06, OWNER:1793950669508519029)

The ten-line version vision is `version/vision.md`, written only from his root paragraph, `sheet.md` and his quoted
words. In one line: a genetically engineered grass savanna that has burned for millennia and is burning still; deep
fertile ash, ash blowing like snow, a burn line that never goes out for long, scorch-fruit right behind the front, the
fire's own cast of animals, three skies and never ordinary rain, whole on its own, judged first on a fresh map.

### His words on this mod (verbatim; the full list with ledger ids is `sheet.md` "his words" and `record.json` decisions)

- 2026-10-12: "the Pyrelands have burned for millennia, so most places should already have deep ash; the ash should be
  QUITE fertile with water added." · "Normal ground. And there should also be a LOT of free-flying ash blowing around
  like snow."
- 2026-11-05, by card: "How should black rain compound on a fresh burn scar? → Just stop the wipe (wet plus burn 190%,
  bonus fades on its 6-day clock)"
- 2026-11-05: "I don't think this is a needed feature for this mod." (the firebreak)
- 2026-11-05, on the flagship: "The first. But the scorchfruit are rapid after the fire not in two days."
- 2026-11-13: "the grasses grow swiftly even on seemingly dry ash due to their very deep roots and underground storage
  systems. … When watered they accelerate even faster and even do the gentle burst. This was ruled on before. Ordinary
  crops should still just treat it as very fertile ground and benefit from water as before."
- 2026-11-13, by card: "World switch → ship biomeGenerationEnabled OFF, labelled unsupported; Firebreak → delete leaf
  paved_strip_holds_the_line; Banks heat → same as the tested warmth and sleep-ignition, fold the leaf"
- 2026-11-13, the lock: "Yes, lock the other four mods" (typed to the Conductor) and, by card, "Own mod, own version, later"
  (the Deep Desert Tribes split).
- 2026-11-15 12:22 PM PST, by card: "How should Pyrelands 0.1.0 proceed? → Fix the 17 gaps, one final look"
  (OWNER:1794774724955142310; `record.json` d_fix_seventeen_round_six_gaps).

### Oddities (things a reader would otherwise get wrong)

1. **Two bar sets exist.** The 41 coverage checklist rows are the bars of 0.1.0. The 21 north-star bars
   (`pyre_*`, `design/validation_walks/RimMandrake/Pyrelands.md`) are the older list the leaves' `root` fields point at
   and that `validation.py` reads. Every leaf names its north-star bar, so the two are linked, not rivals.
2. **No judge has read the locked tree.** The last verdict (`rm-coverage-judge-1794594804`, 20 of 41 met) judged a
   slightly earlier tree; its gaps still stand on the locked files (`version/gaps_sorted.md`).
3. **The exam is stale** (gap g14): `exam.json` was taken on an older tree and sheet. Rerunning it is a Designer step,
   not test text.
4. **A deleted def is still counted by four scenes** (gap g1): `RM_FE_Filth_LooseAsh` was removed 2026-11-08 when ash
   moved onto the sand grid; scenes that count it read zero whether ash works or not.
5. **"Every leaf runs at quicktest" is a proposal, not a measurement.** 18 of 21 leaves propose tier `quicktest`, which
   needs the live game; this run is offline only, so no live scene is run here and every live test reads `runs_today:
   no (not run: offline only)` unless an offline test also decides it.
6. **The Designer stage record says stage 4, blocked**, on a pending note about the 2026-11-06 verdict's five gaps.
   That note is stale (the worldgen question was answered by card 2026-11-13). The version lock supersedes it.
8. **One entry, three skies.** `sc_three_skies` names `validation.py::cinderfall` as its entry; whether that function
   also forces ash fall and black rain is for Stage 2 or the Stage 4 challenger to read, not assumed here.
9. **`selftest_settings_screens.py` is red as a file** (851/856 today) on five rows of other mods (Explosive Knockback,
   Rites, CathedralPass, KyberTradePlot); every Pyrelands row is green, and the table reads only those rows.

## History (dated, added to only)

### Conductor interventions (one line each, added to only; the form is in the spec §5, "The steward and the journal")

- CONDUCTOR INTERVENED (stage 3, 2026-11-14 12:15 PST, kind decision): a locked file that changed after the lock only by test-text corrections or by today's table work is re-pinned in `version/bars.md` with a journal line saying what changed; a changed bar is never re-pinned (`plan.md`'s fire-hawk reach change, question 5). Source: Steward's decisions in the Stage 3 brief of run `rm-detached-bench-rimmandrake-advance-pyrelands-offline-be-1794687328`.
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 12:15 PST, kind decision): the two places the judge asked for a new bar stay with him; Stage 3 builds no bar for them and keeps the named tests. Source: the same brief.
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 14:25 PST, kind re-pin): `plan.md` re-pinned in `version/bars.md` to its current blob `dd3ec4b45d`; the fire-hawk's map-wide ember carry (commit `82d9247595`) is Pyrelands 0.1.0, owner by card 2026-11-14 ("Keep anywhere on the map"); settles questions 5 and 6. Source: OWNER:1794694152010085063.
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 14:25 PST, kind decision): ullai keep vanilla herd migration, owner by card 2026-11-14 ("Yes, let them cross"); new offline check `T_ULLAI_HERD_MIGRATES` supports `inv_ullai_herd_giant`, and `T_CUT_STAYS_CUT` no longer refuses herdMigrationAllowed true (the cut leg was the world-map migration only); settles question 7. Source: OWNER:1794694157698359872.
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 2:30 PM PST, kind bar-added): bar `inv_firehawk_hunt_rewards` added to 0.1.0 (record.json inventory, scope opened_by_owner): "The first time a fire-hawk is seen carrying an ember on your map, one letter names the hawk and the ember it carries and jumps to it, once per game and switchable off in Mod Settings; butchering a hunted fire-hawk sometimes yields a Pristine Firehawk Crestfeather, a valuable object of beauty that rewards the hunt." Decided by `T_FH_LETTER` and `T_FH_CRESTFEATHER` (stage 4-5, green) and the live chains `firehawk_first_sighting_letter` and `firehawk_crestfeather_yield` (stage 6, entries exist, UNRUN: `modcheck run Pyrelands --chains firehawk_first_sighting_letter,firehawk_crestfeather_yield`); supported by `T_FUZZ` (rewards family) and `LOOK_STAGE8`. record.json re-pinned `f478008aa8`; settles question 1 and oddity 7. Source: owner by card 2026-11-14, OWNER:1794693278631337978.
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 14:35 PST, kind re-pin): the root's sentence that ordinary paving stops the ground fire is deleted with every line that promised it (record.json root, d_firebreak_cut, d_root_ending, inv_firebreak_firefoam; tree.json walk leaf; scenes.json sc_walk; sheet.md; plan.md), and tree.json, scenes.json, sheet.md, record.json and plan.md are re-pinned in `version/bars.md`, owner by card 2026-11-14 ("Drop the sentence"); the mod's About text, arrival letter and two fire letters lose the same promise. Source: RIMMANDRAKE_ASK_PYRE_ROOT_STILL_PROMISES_PAVING_HOLDS.
- CONDUCTOR INTERVENED (stage 4+5, 2026-11-16 8:36 PM PST, kind hold): the Dispatch tick launches no blind cycle 3 on Pyrelands while the Fable rescue run (item `RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE`, unit `rm-detached-bench-rimmandrake-rescue-pyrelands-black-rain-1794889288`, started 8:21 PM PST) reworks its fire and rain requirements; a cycle judged underneath it would judge a moving tree. Lift it when that run has ended and published: a later line of the same form, `kind release`, for stage 4+5. Source: the Conductor's order in `RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS`.

### 2026-11-14 11:25 PST, advance begins (rm-builder, detached, offline only)

Brief from the Conductor: pilot rows 1 to 3 by hand for Pyrelands (journal, finish Stage 1, Stage 2), throwaway
scripts only, stop before Stage 3, edit tests and `design/concepts/Pyrelands` only (another helper may be changing
FlowWorks water code). Owner, 2026-11-14: "We need to get this going."

### 2026-11-14 11:30 PST, row 1 done: journal started

- **Held statements measured:** `grep -iE 'pyre|ember|scorch|\bash\b'` over `design/RimMandrake/validation_holding/*.md`
  finds 0 lines; the same grep for `knockback` finds 7 lines (5 in its own held file), so the instrument can see. Pyrelands has **0 held look
  statements** to place.
- **Cost:** about $1.2 of model spend (harness budget line; tokens not separately measured), about 5 minutes wall.
  Almost all of it reading: the spec, the version folder, the verdict's 14 gaps, the leaves and the inventory.
- **Boring enough to automate:** collecting his words (already in `sheet.md` with ledger ids); the held-statement
  count per mod (one grep, but the mod's vocabulary has to be chosen); the stale-exam check (hash of tree and sheet
  against `exam.json`).
- **Needed judgment:** which oddities a cold reader trips on (the two bar sets; the stale Designer note).

### 2026-11-14 11:37 PST, row 2 done: Stage 1 finished by hand

- **The table:** `version/test_table.json` and `.md`, made by a throwaway script
  (`D:\ClaudeWork\scratch\pyrelands_advance\make_test_table.py`, 84 s, most of it the lint's planted-defect run). Each
  of the 41 bars names the tests that decide it, the tests that support it, and the highest deciding stage. The counts are above.
- **How many already had a runnable test: 34 of 41** (any test), 27 with every decider runnable [measured; "runnable" for a
  live scene means its entry function exists, not that it ran].
- **Corrections applied (test text only):** g1 (the deleted loose-ash def swapped for the sand-grid ash reading
  `ProbeAsh`, in 4 scenes and 3 leaf oracles), g3 (dry ash 70%, dry fresh scar 120%, from the code's 0.70 / 1.40 / +0.50),
  g5 (the world switch's default is checked, by `selftest_pyrelands_site.py`), g11 (art coverage rests on his sheet
  approval), g12 (the false "still promises migration" lines removed; grep finds none), g13 (showcase 3 described as
  staged). In `tree.json` only `oracle_proposed` and `scenario` fields moved; every `experience` and `red` is
  byte-identical to the lock [measured against `237b791167`]. Where a judge fix asked for a new leaf (g5, g12) a test was
  named instead, since a leaf is a bar. g14 not applied.
- **The settings move:** `inv_settings_gate` was proven only by the two-week walk. It is now decided offline by
  `T_SETTINGS_SWEEP_OFFLINE` (specified: defaults, readers, the roster gate checked by every mechanic), with the built
  `selftest_settings_screens.py` (Pyrelands rows) and `selftest_pyrelands_site.py`; the walk keeps the gate-off read in
  play only as support.
- **Held statements placed:** none exist for this mod (0).
- **Cost:** about $2.3 of model spend for the row (running total about $3.6), 7 minutes wall.
- **Boring enough to automate:** entry-exists per scene; running every offline test with a time and a result; the
  "only oracle and scenario fields moved" check; applying a judge's literal text fixes once its `smallest_fix` is exact.
- **Needed judgment:** which tests decide a bar and which only support it; whether an existing test really observes the
  bar (the fuzz covers the fertility kernel, not a crop growing); declining the judge's "add a leaf" (a new bar) for a
  test; spotting the unbarred fire-hawk rewards.

### 2026-11-14 11:43 PST, row 3 done: Stage 2 preflight, by a throwaway program

- **The program:** `version/pilot_throwaway/preflight_pyre.py`, adapted from the pilot's `preflight_ek.py` so the mods
  read alike (no model; reads `version/test_table.json`, the repo, the def dump and the ledger; writes
  `version/preflight.json`). 16 checks; the pilot's two Knockback-only checks are replaced by Pyrelands ones (C13 the
  six corrections hold, C14 every C# `Type.Member` of ours that the text names exists, C16 every scene's leaf and
  coverage name resolves). **Run time 0.8 to 4.7 s** (the spread is the def dump read from `C:`). Def list: the live
  dump `defs.sqlite`, captured 2026-11-12T08:10Z, 59262 entries.
- **Each check was watched going red** on its own planted fault in a copy (bar dropped, bar with no test, stage 7,
  missing file, missing read, no game reason, no full-list reason, unknown def, unknown packageId, unknown settings
  field, the deleted loose-ash def put back, a misspelt `ProbeSleep`, a held row naming scorch-fruit, a scene requiring
  an unknown leaf), and an unchanged copy stayed at the baseline.
- **The check caught itself:** with the loose-ash def put back, C9 at first stayed green, because the 2026-11-12 dump still
  holds `RM_FE_Filth_LooseAsh` (as "loose ash (old)" in `mandrake.rm.biomes`) though the repo deleted it 2026-11-08. C9
  now requires a def of ours to exist in the repo. Lesson filed; `preflight_ek.py` has the same hole.
- **Result: 17 refusals, in three checks:**
  - **C6 "Built: runs" (8).** 4 offline tests are specified, not built (`T_SETTINGS_SWEEP_OFFLINE`, `T_DEFS_OFFLINE`,
    `T_CUT_STAYS_CUT`, `T_ASH_PROBE_OFFLINE`), and 4 deciding scenes have no entry in `validation.py` (`walk_season`,
    `firefoam_sprayer`, `rite_hook_alone`, `flamefang_venom`). Route: Stage 3. The three items `scenes.json` names for
    those entries (`PYRELANDS_SHOWCASES_BUILD_THREE_PYRE_FACES`, `PYRELANDS_SCENES_BUILD_EIGHT_JUDGE_GAPS`,
    `PYRELANDS_SCENES_BUILD_VENOM_GIANT_DUST_DOME`) have ledger events but no item file, live or closed.
  - **C12 locked files changed (5).** `tree.json`, `scenes.json`, `sheet.md`, `record.json`: this run's corrections
    (test text; leaf `experience` and `red` byte-identical to the lock). `plan.md`: commit `82d9247595` (2026-11-13 19:42,
    the fire-hawk carries its ember anywhere on the map), after the lock. Route: the Conductor reads each; test text is
    re-pinned in `bars.md`, a meaning change goes to him.
  - **C15 items (4).** The four new offline tests name items not yet filed; filed at Stage 3 start.
- **Cost:** about $1.3 for the row (running total about $4.9), 6 minutes wall.
- **Boring enough to automate:** all 16 checks; the mutation run (one planted fault per check) is itself a loop a program
  can do. A real preflight wants scenes to list their defs, settings and C# probes as fields, not free text.
- **Needed judgment:** whether a dump-only def of ours is real (it is not); whether `plan.md`'s post-lock fire-hawk change
  is test text or meaning (not judged here).

### Stage 3 must build (sizes are guesses)

1. `T_DEFS_OFFLINE`: static def reads (no ordinary rain on the list, "engineered" in the text, venom tendable, body
   size 6 and the heat-immunity patch, shovel yield). Small, ~1 hour.
2. `T_CUT_STAYS_CUT`: firebreak, lightning breaker and migration stay absent. Small, under 1 hour.
3. `T_SETTINGS_SWEEP_OFFLINE`: defaults, readers and the roster gate for 41 settings, with mutants. Medium, 2 to 3 hours.
4. `T_ASH_PROBE_OFFLINE`: `ProbeCell` parts and its refusal, compiled against stubs like the allowlist test. Medium, ~2 hours.
5. Four missing scene entries in `validation.py`: `flamefang_venom` and `rite_hook_alone` small (~1 hour each);
   `firefoam_sprayer` medium (`firefoam_aim_live_proof.py` exists to start from); `walk_season` large (two weeks of play
   with a reload, the showcase build).
6. The 6 PROBLEM gaps (g2 foreign arrivals, g4 dry-ash grass reads, g6 heat immunity, g7 venom tending, g9 allowlist
   eviction shown, g10 gate off): scene text plus validation code, small to medium each.

### Questions (open)

2. **g14, the stale exam.** Rerunning the Cold Reader exam is a model step. Does a locked version still owe it, or does
   Stage 4's blind challenger replace it (spec open question 7)?
4. **`no_ordinary_rain` is decided twice.** If the biome's weather list holds no ordinary rain, can anything choose
   it? If not, `sc_no_rain` could drop to support and the bar proves offline (pipeline bar 4). For the Stage 4
   challenger.

### 2026-11-14 12:40 PST, Stage 3 (offline build, as reconcile) done by hand (rm-builder, detached, offline only)

- **Preflight: 17 refusals before, 1 after** [measured, `version/preflight.json`, 3.7 s]. C6 8 -> 0 (all 8 owed tests
  built), C15 4 -> 0 (items filed), C12 5 -> 1 (four files re-pinned, `plan.md` not).
- **Offline tests built, each green with its own planted faults red:** `T_DEFS_OFFLINE` (6 def facts, 12 of 12 mutants;
  reads patch-added weather too, so the ash-storm patch is counted), `T_CUT_STAYS_CUT` (10 absence facts incl. the shipped
  DLL, 9 of 9), `T_SETTINGS_SWEEP_OFFLINE` (41 settings scribed, shipped as ruled, read, gated; 10 of 10),
  `T_ASH_PROBE_OFFLINE` (real kernel compiled with a harness; 8 of 8; red on the base commit: "RM_FireEcoKernel has no
  ProbeLine"). The first three are new tests of built behaviour, so their red is the planted faults, not the base.
- **Mod behaviour built (C#, `FireEcologyHook.dll` rebuilt):** the ash probe the leaf `ash_fertility_probe` asks for:
  `RM_FireEcoKernel.ProbeLine` (base, watered lift, fresh-burn bonus with age and days left, rain on the cell, expected
  beside the grid's value); `ProbeCell` now goes through it and starts `refused=<reason>;` when the ash field or the
  gate is off, still listing the parts (the gate-off check `ash_field_activates_after_init` reads them);
  `ProbeRect` for a rectangle. For `rite_hook_alone`: a counting test listener on `PyrelandsFireRiteHook`
  (refuses to replace a real hook) and `MapComponent_BurnLine.ForceFrontDue` (one fire-clock beat on demand).
- **Scene entries built, UNRUN (Stage 6):** `flamefang_venom`, `rite_hook_alone`, `firefoam_sprayer`, `walk_season`
  in `validation.py`, each with its control. Import-checked and run through the offline declaration probe (every
  component declares, none crashes). `walk_season` runs only with `PYRE_WALK=1` (two game weeks, full list); it does
  not automate the harvest, the sowing or the furnace-beast shelter (the colony's own work; his walk reads them).
- **Items:** filed `RIMMANDRAKE_PIN_PYRE_DEF_FACTS_OFFLINE`, `RIMMANDRAKE_PIN_PYRE_CUT_LEGS_ABSENT`,
  `RIMMANDRAKE_MOVE_PYRE_SETTINGS_SWEEP_OFFLINE`, `RIMMANDRAKE_PIN_PYRE_ASH_PROBE_OFFLINE`, each with its acceptance test;
  all four closed on their landing commits.
- **Re-pinned (steward's decision):** `tree.json`, `scenes.json`, `sheet.md`, `record.json`, checked field by field
  against the lock blobs (only test text and the g5/g12/g13 false lines moved; `record.json`'s `inv_ullai_herd_giant`
  sentence about the cut migration's text is among them). `plan.md` is not: commit `82d9247595` changed the fire-hawk's
  reach after the lock. Detail in `version/bars.md`.
- **Preflight hole fixed:** C9 judges a def with our prefix against the repo's current Defs/Patches (or a declared C#
  type), never the 2026-11-12 dump or a C# string; a built-in probe refuses if it cannot see the deleted loose-ash def.
  The pilot's `preflight_ek.py` still has the hole (not this mod's file).
- **Regressions:** fuzz, lint, allowlist, burn cost, site, fruit clear green after the C# change.
  `selftest_settings_screens.py` stays red on other mods' rows only (oddity 9).
- **Code review:** every C# and test file touched is DIRTY (`code_review_status.py`); Stage 4's blind review is the review.
- **Cost:** about $7.3 of model spend (harness budget line; running total about $12.2), about 25 minutes wall, 0 of his minutes.
- **Boring enough to automate:** deriving "built" from the test file existing (now in `make_test_table.py`); the mutant
  loop every test repeats (copy, plant, run, expect red) is one helper; field-by-field diff of a locked file against its
  pin, sorting test-text fields from bar fields; filing an item with its acceptance test from the table row.
- **Needed judgment:** whether `plan.md`'s reach change is meaning (yes, so not re-pinned); what "refuses" means for a
  probe another check reads (prefix plus parts); what "herdMigrationAllowed false" asks (no def sets it true; see Q7);
  which parts of the two-week walk a script can honestly decide.

### Questions (added at Stage 3)

8. **The PROBLEM gaps' live halves** (g2 foreign arrivals, g4 dry-ash grass, g6 heat immunity, g7 venom tended, g9 eviction
   shown, g10 gate off) need scene text in the locked `scenes.json` or a ruling that their offline halves suffice.

### 2026-11-14 9:28 PM PST, stage change: Offline build (Stage 3) to Blind challenge, tests first (Stages 4 and 5) (by CONDUCTOR)

- Why: every Stage 3 exit test passes (maturation.py next, 2026-11-14 9:27 PM PST)
- Checks passed: order, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle.
- Blind cycle 1 of this visit (1 in all).
- Was, "Stage now": - **Stage now:** Stage 3 ("reconcile") done offline 2026-11-14 12:40 PST. Preflight re-run 2026-11-14 14:32: **0 refusals**, verdict pass (17 before Stage 3; 1 after it, `plan.md`, since re-pinned by his card). Stages 4-5 are next.
- Was, "Waiting on": - **Waiting on:** the Conductor's read of `plan.md`'s post-lock change (the one preflight refusal); the live halves of the PROBLEM gaps g2, g4, g6, g7, g9, g10 (Stage 6, or more scene text); the questions at the end of the history.
- Record: `version/stage_record.json`.

### 2026-11-14 9:45 PM PST, owed exam and coverage judge: refused by the stage machine before either ran (helper RIMMANDRAKE_SIT_PYRELANDS_OWED_EXAM_AND_JUDGE_LOCKED_FIRST)

- His card 2026-11-14: one exam and one coverage judge pass on the locked tree, no loop. Neither ran; stage.json untouched.
- Refused 1: the concept is past its loop ceiling (8,070,268 of 8,000,000); the park lifts only on his word naming `BAROQUE_SCRIPT_MEASURE_PREP_AND_CONTROLS`, and his card sits on the ADVANCE item.
- Refused 2: his 2026-11-14 card changed the root (commit f71693d77a), so the next open reopens Designer stage 1, not the exam (`RIMMANDRAKE_REPIN_LOCKED_CHANGE_STAGES_CARD_REOPENS_STAGE_ONE`).
- The judge runs only at stage 5 after a passing exam, so it waits on both.
- Record: `version/evidence/exam_and_judge_refusal_2026-11-14.json`.

### 2026-11-15 1:47 AM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to In-game acceptance (Stage 6) (by CONDUCTOR)

- Why: Blind challenge cycle 1 exit met by the program's reading after a neutral reconcile (2f13be38482c); night order of 2026-11-15
- Checks passed: order, version, hold, steward_confirms.
- Steward confirms: Read the judge's report and the neutral fixer's: 6 offline bars green on fresh reruns (9 deciders), both Problems (herd anchor, forced rain) shown red on the pre-fix tree and green at HEAD by the fixer's own runs, no test weakened (six before/after hashes match), 20 of 22 planted faults caught and the two misses are game-side. Owed to Stage 6: the rain swap and the anchorless-herd fallback, never run live.
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-14 9:28 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-14 9:28 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-15 7:26 AM PST, stage change: In-game acceptance (Stage 6) to Offline build (Stage 3) (by BENCH)

- Why: steward: visit 1 exit not met; sc_three_skies FAIL is a MOD defect (black rain tuning), so the road back is offline_build, not blind_challenge; 6 items filed caused-by RIMMANDRAKE_ROUTE_PYRELANDS_VISIT_ONE_FAILURES_BACK
- Checks passed: order, version, hold.
- Steward confirms: read design/concepts/Pyrelands/version/in_game/visit_1/SUMMARY.md + findings.md: 34 PASS, 1 FAIL (sc_three_skies, MOD), 4 UNMEASURED (sc_ruins, sc_ullai, P_opening_front, sc_walk: checks judged wrong); verdict: back to offline_build
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-15 1:47 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-15 1:47 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-15 11:50 AM PST, Evidence-for-Ask: questions 2, 4 and 8 taken, round-6 gaps sorted (BENCH helper, delegated)

Under his Evidence-for-Ask rule (2026-11-15, `RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME`): each
question below has an obvious answer from his recorded words or the shipped record, and no evidence was found against it,
so the Conductor takes it. These are Conductor decisions, not his.

- CONDUCTOR INTERVENED (stage 3, 2026-11-15 11:50 AM PST, kind decision): answers question 2 (g14, the stale exam):
  yes, a locked version owes the Cold Reader exam again whenever its tree or sheet changes, and Stage 4's blind
  challenger does not replace it. Already done: the exam was retaken on the current tree at `292b94bca8` (20 of 20,
  readers agree, control missed; its inputs hash equals the tree the round-6 judge read). Source: his card 2026-11-14
  "one exam on the locked tree"; the re-pin rule `RIMMANDRAKE_REPIN_STAGE_FOUR_LEAVES_EXAM_VOID`.
- CONDUCTOR INTERVENED (stage 3, 2026-11-15 11:50 AM PST, kind decision): answers question 4 (`no_ordinary_rain`
  decided twice): no, `sc_no_rain` does not drop to support. Something other than the weather list can choose ordinary
  rain: a game condition's forced weather and Odyssey's wet-climate tile mutator (`version/blind_challenge/cycle_1/SUMMARY.md`
  "Rain question"). The code fix landed (`RIMMANDRAKE_FIX_FORCED_WEATHER_SKIPS_THE_RAIN_LIST`) and visit 1 showed the
  forced-rain swap live. `sc_no_rain` stays the decider and still owes the forced-weather case (round-6 g8).
- CONDUCTOR INTERVENED (stage 3, 2026-11-15 11:50 AM PST, kind decision): answers question 8 (the PROBLEM gaps' live
  halves): they stay in 0.1.0 with scene text, and offline halves alone do not suffice. Source: his card 2026-11-15 "Fix
  all 12 in 0.1.0" (OWNER:1794748469904049550). The scene text landed in `91a7c61989`. Visit 1 (`f5c2c3cf0b`) passed
  `sc_grass_regreens`, `sc_populations`, `sc_furnace_bed`, `sc_flamefang_venom` and the gate-off check. `sc_foreign_arrivals`
  was not run and is owed at the next Stage 6.
- Dry-ash text: the biome description said dry ash "barely feeds a crop". The locked leaf `ash_fertile_when_watered`
  says sowable dry (about 70%), very fertile watered, and "must not read as ash being barren" (his card 2026-11-07:
  "Keep 70%, sowable"). That number became his locked bar when his card 2026-11-15 "Fix all 12 in 0.1.0" took the
  11-14 judge's g13 fix (70% dry, 140% watered); the judge read his 2026-11-13 "benefit from water as before" as keeping
  70/140. The biome description and `version/vision.md` item 2 ("very fertile for ordinary crops", which went further
  than the root he approved: "quite fertile wherever water reaches it") were fixed to match. The bar did not move
  (`RIMMANDRAKE_RECONCILE_DRY_ASH_TEXT_WITH_VERY_FERTILE_BAR`).
- Round-6 gaps (rm-coverage-judge-1794750987) are sorted in `version/gaps_sorted.md` "Round 6". Of the 18, 14 are
  PROBLEM, 3 CORRECTION, 1 POLISH (`version/polish.md`, proposed) and 0 NEXT VERSION. Judging stays stopped
  (REFUSAL_NOTHING_COULD_EVER_PASS); this sort releases nothing.

### 2026-11-15 12:35 PM PST, his card: fix the 17 gaps, one final look (BENCH helper, by card)

- His card 2026-11-15 12:22 PM PST (OWNER:1794774724955142310, on `BAROQUE_SCRIPT_MEASURE_PREP_AND_CONTROLS`): "Fix the
  17 gaps, one final look". Builders fix the 14 PROBLEM and 3 CORRECTION gaps of round 6 (g1, g2, g4-g18 of
  rm-coverage-judge-1794750987). g3 (POLISH) stays in `version/polish.md` and is not part of passing. The exam is retaken,
  then the coverage judge looks ONE more time. This supersedes his 2026-11-14 limit (OWNER:1794721773574845016) for that
  one look only; it is not a rework loop.
- Route, by the pipeline's own mechanism: one fix ticket, `RIMMANDRAKE_FIX_PYRELANDS_ROUND_SIX_SEVENTEEN_GAPS` (BENCH,
  offline, Relentless). It applies the 17 fixes, writes `coverage_fixes.json` against the round-6 judge (g3 claimed as out
  in his words, `record.json` d_fix_seventeen_round_six_gaps), and ends with ONE `designer_stage.py repin` citing this card.
  It does not release and does not judge. The re-pin is a `locked_change`, which owes the maturation chain steward
  (`maturation_autonomy.py` chain_owed): it retakes the Cold Reader exam, runs `coverage_judge.py release` once and the
  judge once. A seventh not_covered stops judging again (`coverage_judge.py` stop_reason counts only rounds after the last
  release) and pauses Pyrelands for him.
- The exam on file predates the exam gate of `677d7dfdb4` and fails it (no Challenger scenario, no control copy, control
  `missed_ids` unset), so the chain's retake must follow `roles/designer_exam.md` in full; the judge skips while the exam
  fails (`coverage_judge.py` 753-755).
- Not released now, on purpose: Pyrelands sits at Offline build with its exit tests green, so a release before the fixes
  would let the maturation steward advance it to Blind challenge with the 17 gaps open. Until the re-pin, judging stays
  stopped and maturation stays paused on the coverage stop.

### 2026-11-15 1:08 PM PST, the 17 round-6 gaps fixed, ONE re-pin (BENCH helper, his card OWNER:1794774724955142310)
- RIMMANDRAKE_FIX_PYRELANDS_ROUND_SIX_SEVENTEEN_GAPS fixed g1, g2 and g4-g18 in 6a4318a295, 6d8f7fe94c, 4a7b2faf61 and
  5b463ff0f9; `coverage_fixes.json` (c45f0b13aa) holds 18 claims against rm-coverage-judge-1794750987, g3 out in his
  words. T_ROUND6_GAPS (`src/RimMandrake/Pyrelands/selftest_pyrelands_round6_gaps.py`) read 17 of 17 gap checks FAIL on
  7c9f5784b1 and passes 18 of 18 now (the gates included: concept_tree lint, scene_errors, showcase_check).
- One `designer_stage.py repin` re-pinned stages 2 and 3 (26fe15df8b); the history ends with a `locked_change` at
  21:06:06Z, newer than the 14:05:35Z coverage_stop; `chain_owed` reads true. Not released, not judged.
- No tree leaf was added (each would be a new locked bar): the fixes extend five leaves' experience text
  (walk_season_on_the_pyre, ash_fertile_when_watered, firehawk_lights_ahead, populations_are_the_biomes_own,
  grass_carpets_and_regreens) and furnacebeast_warms (the furnace-hide heat bank, the giant's margin), add three scenes
  (sc_furnace_hide_bank, sc_roof_withers, sc_herd_thirst) and a fourth showcase (fire_solace).
- For the chain's exam retake: the exam on file (`exam.json`, 292b94bca8) still fails the 677d7dfdb4 gate (no
  `"by": "challenger"` scenario, no `exam_control/copy.json`, control `missed_ids` unset). Retake it per
  `src/RimMandrake/rimflow/roles/designer_exam.md` in full: `designer_stage.py exam-control <dir> --leaf <id>`, the
  control Reader on that copy, Challenger-marked scenarios. The sheet now states behaviours the old exam never probed
  (fire sense and eat-before-duty, wet roots, the far hawk's seek-burn, the fire-cast top-up, roof withering, slow
  thirst, the hide bank), so the retake can give them scenarios.
- False text corrected on the way: record.json said the ashwallow dome sprite is the standing body; AshwallowDome_* is
  its own art since adf45e2103 (2026-10-15).
- Owed: RIMMANDRAKE_BUILD_PYRELANDS_ROUND_SIX_PARTS_AFTER_THE_TEN (script parts; every new or extended live read UNRUN,
  commands in scenes.json), RIMMANDRAKE_JUDGE_PYRELANDS_ART_ADDED_SINCE_HIS_SHEET, RIMMANDRAKE_DRAW_CRESTFEATHER_OWN_ART_NOT_A_THRUMBO_HORN.

### 2026-11-15 4:36 PM PST, advance steward: NOT advanced to Blind challenge (BENCH, RIMMANDRAKE_ADVANCE_PYRELANDS_PAST_OFFLINE_BUILD)
- `maturation.py next` read every Stage 3 exit test green, but `every_bar_has_a_check_that_runs` only read the test
  table's stored `every_decider_runnable_today` (42 of 42 true). 22 deciding scenes in `scenes.json` still carry
  `owed_parts_item` naming two open build items, RIMMANDRAKE_BUILD_PYRELANDS_GAP_SCENE_PARTS_TEN_SCENES_OWED (no
  claim, no commit; its NEW chains `foreign_arrivals` and `fire_sense` are absent from `validation.py`) and
  RIMMANDRAKE_BUILD_PYRELANDS_ROUND_SIX_PARTS_AFTER_THE_TEN. Sorted as a REAL MISS of Stage 3 (the checks are not
  built), and a pipeline defect (the clause trusted the stored flag).
- Fixed: RIMMANDRAKE_REFUSE_EXIT_ON_OWED_SCENE_PARTS_STALE_FLAG. The clause now counts a bar as not runnable while a
  deciding scene owes parts to an open item; `maturation.py next Pyrelands` reads 28 of 42 bars not runnable and names
  both items. The Dispatch tick's builder works them; then the advance.
- The round-8 coverage look (released 2026-11-16T00:11:33Z after the furnace-beast fix, 6120bb02aa) ran and signed
  covered with 0 gaps at 00:52Z (rm-coverage-judge-1794790345).
- 2026-11-16 (RIMMANDRAKE_AUTOBUILD_PYRELANDS_ZERO_BARS_LEFT): the twelve scenes' owed parts were built offline in
  validation.py (d6ab2b6632) and RIMMANDRAKE_BUILD_PYRELANDS_GAP_SCENE_PARTS_TEN_SCENES_OWED was closed. The live
  halves are UNRUN. `maturation.py next` now reads 16 of 42 bars not runnable. Still open:
  RIMMANDRAKE_BUILD_PYRELANDS_ROUND_SIX_PARTS_AFTER_THE_TEN. The table was not remade: make_test_table.py refuses
  because tree.json and record.json now hold 44 bars and the maker lacks firehawk_hunt_rewards and
  ullai_cross_the_map_as_vanilla_herds.
- 2026-11-16 (RIMMANDRAKE_AUTOBUILD_PYRELANDS_ZERO_LEFT): the round-6 scenes' owed parts were built offline (34b6b83c05;
  selftest_pyrelands_round6_parts) and RIMMANDRAKE_BUILD_PYRELANDS_ROUND_SIX_PARTS_AFTER_THE_TEN closed; `certificate
  --run` re-stamped the offline deciders. `maturation.py next` reads 0 of 42 bars not runnable and every exit test
  passing. Live halves UNRUN. The table is still not remade (the same 44-vs-42 refusal), now filed for the Conductor as
  RIMMANDRAKE_LOCK_PYRELANDS_TWO_LEAVES_THE_TABLE_MAKER_REFUSES; T_BURN_COST (a supporting test) is red, filed as
  RIMMANDRAKE_FIX_PYRELANDS_BURN_COST_TEST_RED_TWICE_TODAY.

## 2026-11-15 — his answer on the giant (the furnace-beast size bar): settled, do not ask again

- Card, answered 3:53 PM PST: "How should the giant be made the giant?" → "Keep 'twice', raise body to 9+". The picked
  option's own words: "overturns your ruled body size of 6, changes its health, meat and combat balance, needs bigger
  art, and breaks again if a larger animal is ever patched in." The bar stays as written.
- Size: body 9, twice RSW_Zeer's 4.5 (decision `d_furnace_body_nine` in record.json; built by
  RIMMANDRAKE_ENLARGE_FURNACE_BEAST_TWICE_THE_ZEER_MEANS_NINE, 6120bb02aa). Art: redrawn bigger by
  RIMMANDRAKE_REDRAW_FURNACE_BEAST_BIGGER_ART_CARD_PROMISED_IT (99507bc992; in git, not deployed; the revert is in
  infrastructure/state/art_eval/fauna_installs.jsonl).
- He was asked it twice more after answering (6:11 and 6:42 PM PST, from a stale incident plan); the guard is
  RIMMANDRAKE_STOP_ANSWERED_ASKS_RERAISED_THIRD_TIME_TO_HIM.

### 2026-11-16 12:40 PM PST, stage change: Offline build (Stage 3) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: steward: every Stage 3 exit test passes (order, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate); maturation.py next 2026-11-16
- Checks passed: order, by, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate.
- Steward confirms: Read maturation.py next (no not-met reason, so nothing to sort as RECORD GAP/CRITERION FLAW/REAL MISS), certificate OK (16 bars' offline deciders green on this build; red_seen UNPROVEN warn only, ticket RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN open), all 6 visit-1 road-back items closed (black rain fix 24a2069d18 red at dousing 0, green at 40 in the fuzz model), cycle_1 tests_edited.json: 0 weakened; bar 43 added by his card OWNER:1794748469904049550, not by an agent. Owed live at Stage 6: rain_fire.py UNRUN. Verdict: advance.
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: steward: every Stage 3 exit test passes (order, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate); maturation.py next 2026-11-16
- Blind cycle 1 of this visit (2 in all).
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-15 7:26 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** `RIMMANDRAKE_FIX_PYRELANDS_ROUND_SIX_SEVENTEEN_GAPS` (his card 2026-11-15 12:22 PM PST, OWNER:1794774724955142310): the 17 round-6 gaps fixed and committed, then ONE `designer_stage.py repin`. Judging stays stopped until that re-pin. The re-pin owes the chain steward (Cold Reader exam retake, ONE `coverage_judge.py release`, ONE look). That look is the last: a not_covered stops judging and pauses Pyrelands for him again, with its verdict as the evidence. No second release is given without his word.
- Record: `version/stage_record.json`.

### 2026-11-16 2:28 PM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: delegated: steward: blind cycle 2 exit_met false only because three Problems (all test-strength) were FIXED at b7b77c929e; a new blind judge is owed to judge the two edited tests; certificate re-stamped on this build (record gap)
- Checks passed: order, by, version, hold, fourth_cycle, judge_certificate.
- Steward confirms: read cycle_2/SUMMARY.md, faults.json, tests_edited.json and the diff 85c4d61bee..b7b77c929e of both edited tests: stricter only (one regex replaced by a stricter fact, sweep facts and mutants added), weakened false verified; 0 Problems open, 6 offline bars green; certificate --run on this build: OK 16 bars. Verdict: open cycle 3, file nothing new
- Blind cycle 2 of this visit (3 in all).
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-16 12:40 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-16 12:40 PM PST).
- Record: `version/stage_record.json`.
- CONDUCTOR INTERVENED (stage 4+5, 2026-11-16 9:57 PM PST, kind release): the Fable rescue (item `RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE`) ended and landed 49e11870b4 (wind-carried fire, bar `burn_line_walks` reworded by the owner, certificate OK); the hold of 8:36 PM PST is lifted and the Dispatch tick may launch blind cycle 3.

### 2026-11-17 6:52 AM PST, his card of 6:33 AM changes three bars; the change waits for blind cycle 3 (Conductor helper)

Owner, by card 2026-11-17 6:33 AM PST: his two numbers become experiences ("ash is sowable dry, a watered strip grows
clearly faster"; "burnt ground is green again within about a week"; 70%, 140% and the grass shares stay the shipped
tuning) (OWNER:1794926128945577969); one bar joins 0.1.0, worded exactly "The fire walks with the wind."
(OWNER:1794926130118775229); black rain filling moats and tanks, and a Pyrelands smoke weather, go to 0.2.0
(OWNER:1794926131273790638, OWNER:1794926132427945325; landed a6cf02f441). Blind cycle 3 was live when the card came, so
the tree, record and test-table edits, the re-pin and the lock-bars add are queued, not made: the patch and its steps are
`D:\ClaudeWork\rimmandrake\conductor\apply_card_rewords_20261117.py`, item RIMMANDRAKE_REWORD_DESIGNER_BARS_PINNING_NUMBERS_NOT_HIS.
- CONDUCTOR INTERVENED (stage 4+5, 2026-11-17 6:52 AM PST, kind hold): no advance past Stages 4 and 5 and no blind cycle 4 on Pyrelands until the owner's card of 6:33 AM PST (OWNER:1794926128945577969, OWNER:1794926130118775229) has landed in tree.json, record.json and test_table.json and been re-pinned; blind cycle 3 (unit `rm-detached-bench-rimmandrake-judge-pyrelands-blind-cycle-1794925887`, started 6:31 AM PST) runs on to its end and is not stopped, and it judges the bars as they stood when it began. Lift it with a later line of the same form, `kind release`, once the queued change has landed and re-pinned. Source: the Conductor's order in RIMMANDRAKE_REWORD_DESIGNER_BARS_PINNING_NUMBERS_NOT_HIS.
- CONDUCTOR INTERVENED (stage 4+5, 2026-11-17 9:26 AM PST, kind re-pin): his card of 6:33 AM PST landed: `ash_fertile_when_watered` and `grass_carpets_and_regreens` read as experiences (his 70%, 140% and grass shares stay the shipped tuning), five Designer leaves and their scenes and test-table observes reworded the same way, in tree.json, scenes.json, version/test_table.json and sheet.md (1d7b17ad85); record.json needed no edit (its matches are dated card history, no bar text). `designer_stage.py repin` re-pinned stages 2, 3 and 5 (7e59c0c1ba, citing also his 2026-11-16 burn-line words carried out by 49e11870b4); stage 4's exam is void and the concept is unlocked for its retake (RIMMANDRAKE_UNLOCK_REPIN_VOIDED_EXAM_NEXT_OPEN_REFUSED, d2a3509a53), so the maturation chain retakes the Cold Reader exam and gives ONE coverage-judge look before anything else. Source: OWNER:1794926128945577969, OWNER:1794842055508243067.
- CONDUCTOR INTERVENED (stage 4+5, 2026-11-17 9:26 AM PST, kind bar-added): bar `fire_walks_with_wind`, "The fire walks with the wind." (his words), added to 0.1.0 with scene `sc_fire_walks_with_wind` and its test-table row (1d7b17ad85); `maturation.py lock-bars --add` records 44 bars (d55977d87f). Source: OWNER:1794926130118775229.
- CONDUCTOR INTERVENED (stage 4+5, 2026-11-17 9:26 AM PST, kind release): both blind-cycle judge runs have ended (cycle 3 here, unit `rm-detached-bench-rimmandrake-judge-pyrelands-blind-cycle-1794925887`, exit not met, 5 Problems fixed at 4a7c450d6b) and the queued card change has landed and been re-pinned; the hold of 6:52 AM PST is lifted. Source: the Conductor's order in RIMMANDRAKE_REWORD_DESIGNER_BARS_PINNING_NUMBERS_NOT_HIS (item RIMMANDRAKE_APPLY_BARS_CARD_PATCH_WHEN_BLIND_JUDGES_END).
- STEWARD (stage 4+5, 2026-11-17 10:08 AM PST, item RIMMANDRAKE_RETAKE_PYRELANDS_EXAM_AFTER_LOCKED_CHANGE_RUN_TWO): re-pin of the locked change checked (history 17:09:38Z re-pinned stages 2, 3, 5; 17:26Z repair d2a3509a53 unlocked stage 4). Cold Reader exam retaken in full on tree c1b1d874f8 / sheet a0d6beb6b9: 40 scenarios (Examiner e1-e32, Challenger c1-c8), both Readers 40/40, no reject accepted, control with `fire_walks_with_wind` removed missed e2, e5, c1 (8141978707). Two coverage looks ran on this tree, not one: the steward's (rm-coverage-judge-1794938181, kept at version/evidence/coverage_verdict.rm-coverage-judge-1794938181.json: 1 Problem `burn_line_walks` cannot tell the line from a flood, 1 Polish wind at one bearing, 3 advisory text leftovers) and the launcher's stage-5 Designer run rm-role-designer-1794938276 (rm-coverage-judge-1794938280, coverage_verdict.json: the same flood Problem, the wind gap raised to a Problem, plus a wind-scene restore Polish); filed RIMMANDRAKE_GUARD_ONE_COVERAGE_LOOK_STEWARD_LAUNCHER_BOTH_RAN for the double look; filed RIMMANDRAKE_MEASURE_PYRE_BURNED_SHARE_FLOOD_ALSO_MOVES, RIMMANDRAKE_REVERSE_PYRE_WIND_BEARING_ONE_DIRECTION_STAGED, RIMMANDRAKE_CORRECT_PYRE_STALE_TEXT_THREE_ADVISORY_LEFTOVERS (acceptance: version/evidence/accept_round9_gaps.py). Pyrelands waits on his card for the locked-tree fix; no blind cycle 4 opened.

### 2026-11-17 12:31 PM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: delegated: evidence-for-ask: cycle 3 fixed 5 Problems red-first at 4a7c450d6b and found every offline bar green after, so by its brief its own fixes cannot pass its exit: a NEW blind judge is owed (spec rule 3). Nothing new filed (the lane-1 FAIL is one of the 5 fixed; the 30 UNSETTLED prove at stage 6; the one Polish item is already filed). Certificate's stale stamps were a RECORD GAP, redone for real by certificate --run (22 tests, 16 bars green). Cycle 4 is cycle 3 of visit 2's road, inside the 3-per-visit limit. The Designer's stage-5 delta coverage look released 12:22 PM PST reads the same locked tree and edits nothing, so it need not gate the judge
- Checks passed: order, by, version, hold, fourth_cycle, judge_certificate.
- Steward confirms: read cycle_3/SUMMARY.md, lane2/faults.json, fixes.jsonl, tests_edited.json and the diffs of the 3 edited tests (all additions, nothing weakened); exit_met false only because the cycle fixed its own Problems; verdict: a new blind judge is owed
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: delegated: evidence-for-ask: cycle 3 fixed 5 Problems red-first at 4a7c450d6b and found every offline bar green after, so by its brief its own fixes cannot pass its exit: a NEW blind judge is owed (spec rule 3). Nothing new filed (the lane-1 FAIL is one of the 5 fixed; the 30 UNSETTLED prove at stage 6; the one Polish item is already filed). Certificate's stale stamps were a RECORD GAP, redone for real by certificate --run (22 tests, 16 bars green). Cycle 4 is cycle 3 of visit 2's road, inside the 3-per-visit limit. The Designer's stage-5 delta coverage look released 12:22 PM PST reads the same locked tree and edits nothing, so it need not gate the judge
- Blind cycle 3 of this visit (4 in all).
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-16 2:28 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-16 2:28 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-20 6:01 PM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to In-game acceptance (Stage 6) (by BENCH)

- Why: steward: blind cycle 4 exit met, read and confirmed; certificate OK after the sand_shovel fix 01853a05a6
- Checks passed: order, by, version, hold, steward_confirms, exit_met, judge_certificate.
- Steward confirms: read design/concepts/Pyrelands/version/blind_challenge/cycle_4/SUMMARY.md, faults.json, fixes.jsonl, tests_edited.json: exit_met true, 6 offline bars green, 0 Problems open (the one Problem, a HARNESS gate decider miss, fixed 3962b91eb4). Re-ran myself: T_SETTINGS_SWEEP_OFFLINE green (27/27 mutants red) and red under 3 of the 5 plants (H_wind_ignores_its_switch, K_douse_ignores_gate, H_stamp_caller_skips_gate); the test edit is 126 lines added, 0 removed, sha256 matches. Certificate refusal (sand_shovel asks_on_empty_game) was a wrong check, fixed 01853a05a6; certificate --to in_game now OK. Verdict: exit met, advance.
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-17 12:31 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-17 12:31 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-21 3:04 AM PST, stage change: In-game acceptance (Stage 6) to Offline build (Stage 3) (by BENCH)

- Why: visit 2 not met: one MOD line not fixed in the sitting (sc_ashwallow, RIMMANDRAKE_FIX_PYRE_ASHWALLOW_SHADE_DASH_BEATS_FIRE_DIVE, game-up), one MOD fault no row caught (RIMMANDRAKE_FIX_PYRE_HAWK_LETTER_BLANKS_FOUR_NAMED_SLOTS, offline), and 16 bars undecided whose checks each keep an open owner item; a mix, so offline_build for the offline line, the game-only one waits for in_game
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_2 SUMMARY.md, rows.jsonl, strange.jsonl and read_ingame_exit: 2 reader faults of form repaired (two-commit repair record; status-explained strange rows), 8 needless checks removed (polish.md), sc_ashwallow MOD stands, 16 undecided bars owned by 7 open items; verdict: road back to offline_build
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-20 6:01 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-20 6:01 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-21 4:28 AM PST, stage change: Offline build (Stage 3) to In-game acceptance (Stage 6) (by DISPATCH)

- Why: every open road-back item (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN, RIMMANDRAKE_FIX_PYRE_ASHWALLOW_SHADE_DASH_BEATS_FIRE_DIVE, RIMMANDRAKE_FRAME_PYRE_CHAIN_SHOTS_ON_THEIR_SUBJECT, RIMMANDRAKE_RENEW_SAFE_ADVANCE_AUTO_ARM_HOURLY, RIMMANDRAKE_REORDER_PYRE_BURN_WALK_BEFORE_ITS_FRONT_DIES, RIMMANDRAKE_SHIELD_PYRE_WALK_FROM_FULL_LIST_EVENTS, RIMMANDRAKE_STAGE_PYRE_FLAMEFANG_BITES_LAND_ONCE_NOT_MAUL, RIMMANDRAKE_TRACE_PYRE_ASHFALL_FIRE_IN_FIRST_LIGHTNING_WINDOW, RIMMANDRAKE_TRACE_PYRE_FIREHAWK_TURNS_MANHUNTER_IN_BURN_WALK, RIMMANDRAKE_TRACE_PYRE_SITE_WITH_NO_STANDING_WATER_LEFT) is a fault only the game can show, and the version's offline Problems are closed: the Maturation tick takes the game-only exit back to Stage 6 (RIMMANDRAKE_UNPARK_FLOWWORKS_STUCK_AT_OFFLINE_STAGE_EIGHT_HOURS)
- Checks passed: order, game_only, by, version, hold.
- Game only: RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN, RIMMANDRAKE_FIX_PYRE_ASHWALLOW_SHADE_DASH_BEATS_FIRE_DIVE, RIMMANDRAKE_FRAME_PYRE_CHAIN_SHOTS_ON_THEIR_SUBJECT, RIMMANDRAKE_RENEW_SAFE_ADVANCE_AUTO_ARM_HOURLY, RIMMANDRAKE_REORDER_PYRE_BURN_WALK_BEFORE_ITS_FRONT_DIES, RIMMANDRAKE_SHIELD_PYRE_WALK_FROM_FULL_LIST_EVENTS, RIMMANDRAKE_STAGE_PYRE_FLAMEFANG_BITES_LAND_ONCE_NOT_MAUL, RIMMANDRAKE_TRACE_PYRE_ASHFALL_FIRE_IN_FIRST_LIGHTNING_WINDOW, RIMMANDRAKE_TRACE_PYRE_FIREHAWK_TURNS_MANHUNTER_IN_BURN_WALK, RIMMANDRAKE_TRACE_PYRE_SITE_WITH_NO_STANDING_WATER_LEFT
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-21 3:04 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-21 3:04 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-21 2:30 PM PST, stage change: In-game acceptance (Stage 6) to Offline build (Stage 3) (by BENCH)

- Why: visit 3 exit not met: two MOD lines not fixed in the sitting (sc_firefoam_sprayer: the sprayer carrier never foams, RIMMANDRAKE_DESIGN_PYRE_SPRAYER_CARRIER_NEVER_FOAMS_ITS_PATH; sc_flamefang_venom: one untended bite kills, RIMMANDRAKE_TUNE_PYRE_FLAMEFANG_BITE_KILLS_BEFORE_IMMUNITY), plus undecided bars whose checks the driver could not repair (RIMMANDRAKE_FIND_PYRE_BURNLINE_OFF_CONTROL_THAT_CAN_FAIL, RIMMANDRAKE_READ_PYRE_REGROW_GROWTH_NONE_ON_ALL_SIX_DAYS, game-up) and sc_walk (game a, his full list, next visit). Road back for the MOD lines.
- Checks passed: order, by, version, hold.
- Steward confirms: read design/concepts/Pyrelands/version/in_game/visit_3/SUMMARY.md, rows and lines: 33 PASS, 2 FAIL (MOD, real miss), 3 UNMEASURED (2 HARNESS unrepaired, owned by filed items; sc_walk needs game a); no test assertion weakened (validation.py diff 6ea9314ad1..HEAD read); fix_readers_owed none; verdict: not met, mod wrong, road back to offline_build
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-21 4:28 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-21 4:28 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-21 5:53 PM PST, stage change: Offline build (Stage 3) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: Conductor's repair brief RIMMANDRAKE_UNSTICK_PYRELANDS_FIXER_COUNT_TWELVE_FOUR_REFUSED step 3: certificate --run reran the stale deciders (T_SITE green on build 7015ef7c8aee35e715c3), CERTIFICATE OK, every exit test passes; this hand act is folded by that item
- Checks passed: order, by, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate.
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: Conductor's repair brief RIMMANDRAKE_UNSTICK_PYRELANDS_FIXER_COUNT_TWELVE_FOUR_REFUSED step 3: certificate --run reran the stale deciders (T_SITE green on build 7015ef7c8aee35e715c3), CERTIFICATE OK, every exit test passes; this hand act is folded by that item
- Blind cycle 1 of this visit (5 in all).
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-21 2:30 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-21 2:30 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-21 9:49 PM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to In-game acceptance (Stage 6) (by BENCH)

- Why: steward run RIMMANDRAKE_CONFIRM_PYRELANDS_CYCLE_FIVE_EXIT_MET: blind cycle 5 exit met, read and confirmed; certificate refusal was a RECORD GAP (stale build stamps after the judge's own decider edits), repaired by certificate --run (OK)
- Checks passed: order, by, version, hold, steward_confirms, exit_met, judge_certificate.
- Steward confirms: read cycle_5/SUMMARY.md and its rows (judge unit RIMMANDRAKE_JUDGE_PYRELANDS_BLIND_CYCLE_FIVE_TESTS_FIRST): lane1 49 rows 45 PASS 3 INFO 1 UNSETTLED (game_side_bars, Stage 6) 0 FAIL; 6 offline bars green; planted 33/37 caught (34 after repair; 3 misses are Stage-6 ashwallow caller faults, owed live); 2 Problems both check repairs shown red on plant and green on build, red_seen recorded; no mod fault, no fix reader owed; tests_edited: nothing weakened; certificate --run to in_game OK. Verdict: exit met, advance to in_game.
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-21 5:53 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-21 5:53 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-22 1:47 AM PST, stage change: In-game acceptance (Stage 6) to In-game acceptance (Stage 6) (by BENCH)

- Why: steward, visit 4 not met: every line that goes back is game-only and already filed by the driver (needs game-up); road back is the next visit, never offline_build
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_4/SUMMARY.md, rows and maturation.py next (4 not-met reasons). Judge-the-judge sort: sc_grass_regreens FAIL = REAL MISS (MOD presumed: ember grass +0.054/day vs vanilla +0.118 on the same ground, growDays 0.8 vs 2.5; the run laid soil, a SITE fault repaired 4fff1aa5e7 but not rerun; reader and census-log repairs 897516fc92, aa441a608f also unrun), item RIMMANDRAKE_TRACE_PYRE_EMBERGRASS_GROWS_TENTH_OF_ITS_RATE, game-up; sc_firefoam_sprayer FAIL = REAL MISS (MOD, carrier lays 0 foam, undesigned, Designer first), item RIMMANDRAKE_DESIGN_PYRE_SPRAYER_CARRIER_NEVER_FOAMS_ITS_PATH, game-up; bar flamefang_bite_carries_venom undecided = REAL MISS (SITE unrepaired, starving bystander stopped the wait-out; planted run voided by a death), item RIMMANDRAKE_FEED_PYRE_VENOM_FIXTURES_HUNGER_STOPS_WAITOUT, game-up; bar walk_season_on_the_pyre undecided = REAL MISS (rerun not done, sc_walk not run at the bound, his full list on game a), owed to the next visit. No RECORD GAP, no CRITERION FLAW (the vanilla-rate expectation follows the def's growDays; the description says a day or two). No mod file changed in the visit, so no fix reader owed. Test edits read: round6_parts re-pins the off-control wait constant, venom_staging adds the doctor-job fake, growth_lines is new: none weakened. Verdict: road back to in_game (next visit) when the three items close; plant_density_one_control_map stays owned by RIMMANDRAKE_BUILD_PYRE_GRASS_FOIL_SAME_SEED_DENSITY_ONE.
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-21 9:49 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-21 9:49 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-22 8:54 AM PST, stage change: In-game acceptance (Stage 6) to In-game acceptance (Stage 6) (by BENCH)

- Why: steward visit 5: no mod-wrong line; 5 undecided bars rest on 3 game-only check/scene lines already filed by the driver (sprayer ring scene SITE, grass density-1.0 foil HARNESS, burn-history probe HARNESS for sc_walk); fixers at Stage 6, then visit 6
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_5 SUMMARY.md, rows (32 PASS 0 FAIL 3 UNMEASURED), exit.lines and the counted repairs' diffs (2613e2e96a, e8cb081456, 15431f983f: none weakens what its check observes, each shown planted FAIL / real PASS); verdict: not met, road back in_game on RIMMANDRAKE_SEAL_PYRE_SPRAYER_RING_BOTH_COLONISTS_WAIT_IT_OUT, RIMMANDRAKE_BUILD_PYRE_GRASS_FOIL_SAME_SEED_DENSITY_ONE, RIMMANDRAKE_FIX_PYRE_BURN_HISTORY_PROBE_COUNTS_BEFORE_IT_PRUNES
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-22 1:47 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-22 1:47 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-23 4:04 AM PST, stage change: In-game acceptance (Stage 6) to In-game acceptance (Stage 6) (by BENCH)

- Why: steward of visit 6: one undecided bar (walk_season_on_the_pyre), its only check sc_walk UNMEASURED because ArchSmall cannot hold his full list beside ArchBig; game-only, a rerun not done (REAL MISS, not a mod fault); no mod-wrong line, no mod fix, no fix reader owed. Next visit re-runs the 32 checks the Ullai art (99cede2bfa) and site-loader change touched; a visit owing only sc_walk now waits for ArchBig (aacba60155)
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_6 SUMMARY.md and rows.jsonl: 34 PASS, 0 FAIL, 1 UNMEASURED (sc_walk, class SITE, unrepaired: game placement); 7 harness/site repairs read, each tightens or re-classes, none weakens an observation; verdict: send back to in_game for sc_walk on ArchBig
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-22 8:54 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-22 8:54 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-23 9:55 AM PST, stage change: In-game acceptance (Stage 6) to Offline build (Stage 3) (by BENCH)

- Why: steward of visit 7: two mod-wrong lines not fixed in the sitting, both shown red offline: RIMMANDRAKE_WIDEN_PYRE_LONE_FIRE_INTO_A_FRONT (sc_burn_line_walks' judge clause; accept_lone_fire_lane.py 0 of 8) and RIMMANDRAKE_SPARE_PYRE_FURNACE_BARN_ROOF_FROM_TITAN_WAKE (P_furnace_room; accept_furnace_beast_spares_roof.py FAIL). sc_walk stays UNMEASURED: it needs ArchBig's full list and is the next visit's
- Checks passed: order, by, version, hold.
- Steward confirms: read visit_7 SUMMARY.md, rows.jsonl, strange.jsonl, the day-end sheet and the lane mask by eye (one-cell lanes and flat-sided bands, wind-off row ragged), and the harness repair 5e888e1af2 (weakens nothing: an asked kind or a critical trigger still stops; planted wrong tend FAIL, real 5/5 PASS); no mod fix in the visit, no fix reader owed; verdict: not met, REAL MISS on both, road back offline_build
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-23 4:04 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-23 4:04 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-23 2:16 PM PST, stage change: Offline build (Stage 3) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: steward: every Stage 3 exit test passes; certificate rerun 2b9c29ee0f is on main; both visit 7 road-back items closed (510d96f7b8 lone fire, aca7464fe3 furnace barn roof)
- Checks passed: order, by, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate.
- Steward confirms: read maturation.py next (7 exit tests pass, no refusals, no not-met reason to sort), certificate OK (16 bars, red_seen 6 grandfathered, WARN only), gate open; re-ran accept_lone_fire_lane.py 8 of 8 and accept_furnace_beast_spares_roof.py PASS on this build; read the removed test lines of 510d96f7b8 (T_BURN_LANES, T_BURN_ECOLOGY, fuzz): nothing read was weakened; bars unchanged since d55977d87f. Live checks sc_burn_line_walks, sc_fire_walks_with_wind, P_furnace_room recorded UNRUN for Stage 6. Verdict: advance
- Blind cycle 1 of this visit (6 in all).
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-23 9:55 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-23 9:55 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-23 3:46 PM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to In-game acceptance (Stage 6) (by BENCH)

- Why: blind cycle 6 exit met: both mod fixes of 454764adbe read sound by the steward as fresh reader (lane2/fix_reviews.jsonl); RIMMANDRAKE_ROUTE_PYRELANDS_CYCLE_SIX_FAILURES_BACK
- Checks passed: order, by, version, hold, steward_confirms, exit_met, judge_certificate.
- Steward confirms: read cycle_6 SUMMARY.md, faults.json, fixes.jsonl, tests_edited.json and both test diffs (checks added, none weakened), red_seen for both edited deciders; reran red on 956fb0c600 and green on 454764adbe, lane 1 34 PASS 0 FAIL; run rm-detached-bench-rimmandrake-judge-pyrelands-blind-cycle-1795472682, verdict exit met
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-23 2:16 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-23 2:16 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-24 4:28 AM PST, stage change: In-game acceptance (Stage 6) to Walk brief (Stage 7) (by BENCH)

- Why: in-game visit 8 exit met: 40 of 40 stage-6 checks PASS on checked sites on the walk build; the one mod fix of the sitting (4a9d62cae0) read sound by its fresh reader
- Checks passed: order, by, version, hold, steward_confirms, exit_met, build_match.
- Steward confirms: Read visit_8/SUMMARY.md, all 29 rows, strange.jsonl, polish.md, the diffs of the sitting's test edits (177a585e57, 694d79e5b8, f83b30b60a, 05d3da7407, 6e9257a1af: no assertion weakened; each repaired check has a planted FAIL beside its real PASS), and the fix: red at its parent (job_ends_off, rc 1), green at 4a9d62cae0 (35 of 35 mutants red), engine order read in Verse.AI.JobDriver. No line is mod wrong, undecided, spoiled or unresolved. Verdict: met.
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-23 3:46 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-23 3:46 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-24 4:50 AM PST, stage change: Walk brief (Stage 7) to His live walk (Stage 8) (by BENCH)

- Why: walk brief arrival_1 written
- Checks passed: order, by, version, hold, walk_brief, walk_items_closed.
- Was, "Stage now": - **Stage now:** Stage 7, the walk brief, since 2026-11-24 4:28 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-24 4:28 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-24 7:14 AM PST, stage change: His live walk (Stage 8) to In-game acceptance (Stage 6) (by DISPATCH)

- Why: in-game checks are owed before he walks (P_ambient_ash_drift, P_blackrain, P_gate, P_grass_cover, P_mapgen_log, sc_ash_watered, sc_ashwallow, sc_burn_compounds, sc_burn_line_walks, sc_fire_dusts_ash, sc_fire_walks_with_wind, sc_full_list_smoke, sc_grass_regreens, sc_heat_dome, sc_no_rain, sc_reload_keeps_the_burn, sc_scorchfruit, sc_ullai): the Maturation tick opens the next visit for only these (RIMMANDRAKE_FIX_CHANGE_RELATION_BLIND_TO_CSHARP_NINE_ROWS_MISSED)
- Checks passed: order, by, version, hold.
- Was, "Stage now": - **Stage now:** Stage 8, his live walk, since 2026-11-24 4:50 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-24 4:50 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-24 2:44 PM PST, stage change: In-game acceptance (Stage 6) to Walk brief (Stage 7) (by BENCH)

- Why: visit 9 exit met: 39 of 39 in-game checks PASS on checked sites on the walk build; the one thing owed, the fresh reader of a6f05380df, read it sound (visit_9/fix_reviews.jsonl, 18cf1d0cd8)
- Checks passed: order, by, version, hold, steward_confirms, exit_met, build_match, unrun_run.
- Steward confirms: Read visit_9/SUMMARY.md, rows.jsonl and strange.jsonl (8 strange things, all explained), and the diff of validation.py and the selftests the visit edited: the regrow row keeps its three claims on exact per-plant growth and gains a positive control, burn-line waits are staged through the saved quiet counter, each repair seen red on a planted fault and green on the build; no assertion lost but the season wording his no-long-play ruling retired. Fresh reader of a6f05380df: sound, its selftest rc 1 on the parent (six facts) and rc 0 at the fix (48 of 48 mutants red), DLL MATCH. The visit 7 control-pad run of sc_burn_compounds is on an older build and is being classed under RIMMANDRAKE_CLASS_PYRE_CONTROL_PAD_BURN_NOBODY_LIT; its reading so far finds no mod ignition. Verdict: exit met.
- Was, "Stage now": - **Stage now:** Stage 6, in-game acceptance, since 2026-11-24 7:14 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-24 7:14 AM PST).
- Record: `version/stage_record.json`.

### 2026-11-24 3:21 PM PST, stage change: Walk brief (Stage 7) to His live walk (Stage 8) (by BENCH)

- Why: walk brief arrival_2 written
- Checks passed: order, by, version, hold, walk_checks_stand, walk_brief, walk_items_closed.
- Was, "Stage now": - **Stage now:** Stage 7, the walk brief, since 2026-11-24 2:44 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-24 2:44 PM PST).
- Record: `version/stage_record.json`.
