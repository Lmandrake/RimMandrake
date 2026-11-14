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
- **Stage now:** Stage 2 (preflight) run by hand 2026-11-14 11:43 PST: **refuse, 17 refusals** (`version/preflight.json`).
  Stage 3 ("reconcile") is next; not begun.
- **Bars:** 41 (20 inventory rows of `record.json` + 21 leaves of `tree.json`), as `version/bars.md` counts them.
  Two inventory rows (`inv_firebreak_firefoam`, `inv_lightning_breaker`) are scope `out`: cut, kept only as absence checks.
  The test-and-stage table is `version/test_table.json` (read view `version/test_table.md`), same columns as Explosive
  Knockback's.
- **Measured 2026-11-14:** 34 of 41 bars have at least one test that runs today (a built offline test that ran green, or
  an in-game scene whose entry exists in `validation.py`); 27 have every deciding test runnable; 6 have offline deciding
  tests, and none of those 6 is decided by built tests alone. 11 built offline tests ran green for this mod; 4 are
  specified for Stage 3. 4 of the 23 `scenes.json` scenes have no entry in `validation.py`. No live scene ran (offline only).
- **Judge gaps:** 14 from the last coverage verdict (`version/gaps_sorted.md`). 6 of the 7 CORRECTIONs are applied to test
  text (g1 g3 g5 g11 g12 g13); g14 (rerun the exam) is a model step and stays open. 6 PROBLEM and 1 POLISH stay for Stage 3.
- **Held look statements for this mod:** 0 (measured).
- **Waiting on:** a builder for Stage 3 (the 8 missing deciding tests, the 6 PROBLEM gaps), the Conductor's read of the
  post-lock file changes (Stage 2 C12), and the questions at the end of the history.

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
7. **Built behaviour with no bar.** The fire-hawk's hunt rewards (the once-per-game letter and the crestfeather trophy,
   `FireHawkRewards.cs`, two green selftests) are in the lock commit but no bar or inventory row names them. They are
   left out of the table, as a question.
8. **One entry, three skies.** `sc_three_skies` names `validation.py::cinderfall` as its entry; whether that function
   also forces ash fall and black rain is for Stage 2 or the Stage 4 challenger to read, not assumed here.
9. **`selftest_settings_screens.py` is red as a file** (851/856 today) on five rows of other mods (Explosive Knockback,
   Rites, CathedralPass, KyberTradePlot); every Pyrelands row is green, and the table reads only those rows.

## History (dated, added to only)

### Conductor interventions (one line each, added to only; the form is in the spec §5, "The steward and the journal")

- CONDUCTOR INTERVENED (stage 3, 2026-11-14 12:15 PST, kind decision): a locked file that changed after the lock only by test-text corrections or by today's table work is re-pinned in `version/bars.md` with a journal line saying what changed; a changed bar is never re-pinned (`plan.md`'s fire-hawk reach change, question 5). Source: Steward's decisions in the Stage 3 brief of run `rm-detached-bench-rimmandrake-advance-pyrelands-offline-be-1794687328`.
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 12:15 PST, kind decision): the fire-hawk hunt rewards and the two places the judge asked for a new bar stay with him; Stage 3 builds no bar for them and keeps the named tests. Source: the same brief.

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

1. **The fire-hawk's hunt rewards have no bar.** The letter and the crestfeather trophy are built and tested
   (2026-11-13) but no bar names them. Polish, next version, or a bar owed? (His call if it is a bar.)
2. **g14, the stale exam.** Rerunning the Cold Reader exam is a model step. Does a locked version still owe it, or does
   Stage 4's blind challenger replace it (spec open question 7)?
3. **g5 and g12 asked for a new leaf.** A leaf is a bar, and the design is locked, so a test was named instead
   (`T_SITE` for the world switch, `T_CUT_STAYS_CUT` for migration). Is that acceptable?
4. **`no_ordinary_rain` is decided twice.** If the biome's weather list holds no ordinary rain, can anything choose
   it? If not, `sc_no_rain` could drop to support and the bar proves offline (pipeline bar 4). For the Stage 4
   challenger.
5. **`plan.md` changed after the lock** (fire-hawk reach). Test text or meaning? For the Conductor.
