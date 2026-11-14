# Gimme Some Slack: journal

The mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. Below it the
**history** is only added to. Test of this file: a restarted Conductor can do the next stage change from it alone.

This mod is not the pilot. It advances beside Explosive Knockback, offline only (owner by card 2026-11-14, "All four now,
offline only"), and its table uses the pilot's columns (`design/concepts/ExplosiveKnockback/version/test_table.json`) so the
mods read alike.

## The mod as it stands

- **Design Version 0.1.0, locked** on his word 2026-11-13 ~3:40 PM PST (`version/VERSION.json`). Code exists:
  `src/RimMandrake/GimmeSomeSlack/` (C#, 60 sources; a C# SelfTest of 4485 + 155 checks; 20 Python selftests; `validation.py`
  and `northstar/proof_all.py`, the live proof of 156 rows).
- **Stage now:** Stage 1 finished by hand 2026-11-14 11:43 PST; Stage 2 (a throwaway preflight) next.
- **Bars:** 47 (22 inventory rows of `record.json` + 26 leaves of `tree.json`; `shock_reach_setting` is both, so 48 rows
  name 47 ids). The test-and-stage table is `version/test_table.json` (read view `version/test_table.md`), made by the
  throwaway `version/make_test_table.py`. Of 47 bars: 18 have a deciding test runnable today, 2 have every deciding test
  runnable (both `no_hose` bars), 43 have some runnable evidence when the older proof rows count, 4 have nothing
  (`floor_end_shock`, `floor_end_shocks_crossers`, `shock_reach_setting`, `uninstall_clean`). [measured]
- **Waiting on:** this run (row 3), then a builder for Stage 3.
- **Open questions for him:** "Questions for him", the last part of this top section.

### The vision (his root paragraph, `record.json` root, OWNER:1793895896496551063)

> Gimme Some Slack hides the tidy conduit and draws in its place what a scavenger base really looks like: too-long extension
> cords sprawling across the floor in loose loops and coils, piling against walls, plugging into power strips (or
> connectors, in the other three looks) at every three- or four-way junction, and sagging overhead lines strung between
> masts. The mess is honest: it faithfully represents connectivity but not the precise conduit path. Every cord explains a
> real power connection, nothing is drawn that is not wired, and a cut line lies on the ground sparking where it is live and
> dead where it is not. Even a huge base with many wires and connectors shows no problematic delay.

The nine-line version vision (shock rule, Wire down, the tap, four looks, switches, no hoses) is `version/vision.md`.

### His words on this mod (verbatim; full list with ledger ids in `sheet.md` "his words")

- 2026-10-10: "We need to move the GimmeSomeSlack hose code/functionality over to FlowWorks. That's the right home, and it
  allows GimmeSomeSlack to be entirely about cables and conduits and electricity."
- 2026-10-10, power theft: "If caught, steady goodwill drain (like living too close to a settlement)"
- 2026-10-22, pipe poles: "Their own switch."
- 2026-10-26: "find out if gimme some slack also has the same problemmatic delay with large numbers of wires and connectors."
- 2026-11-02: "The power strips (modern style art) or connectors (other art styles) should appear whenever there are three or
  four way junctions of conduit." · "they should explain the connectivity if power between the actual conduits and devices
  and the visual appearance of the wires. But the wires are allowed to get there through a much more circuitous route as
  overly long extension cables do." · "No, I don't much care about savegame continuity"
- 2026-11-05, the root: "Restate Honest: Faithfully represents connectivity but not precise conduit path. … if they approach
  intending to fix it, they are safe. If they incidentally go over the sparking end with a different job, they (or anyone
  else) gets shocked."
- 2026-11-06, floor-cord ends: "Every sparking end shocks, but settable in settings to those three options: None, only downed
  lines, or all."
- 2026-11-07 19:07 PST: "I do agree that cords take slowly curving paths rather than straight lines often: what they avoid
  are sharp curves unless they must."
- 2026-11-13, the lock: "Yes, lock the other four mods" (said of FlowWorks, Gimme Some Slack, Pyrelands, Pyrelands Mechanics).
- Held look statements (`design/RimMandrake/validation_holding/`): 2026-11-12 row 34 "Here is a screenshot of a GSS connector
  unfortunately showing up through the battery it should be beneath in a pit." · row 36 "The wires are also above the items
  and furniture otherwise, likely all the same problem." · 2026-11-13 row 16 "[Image #8] Also, the GSS cables are now
  correctly below the items." (an approval).

### Oddities (things a reader would otherwise get wrong)

1. **47, not 48.** `VERSION.json` says "47 = 22 + 26"; the sum is 48 because `shock_reach_setting` is an inventory row and a
   leaf at once. `coverage_judge.required_ids()` de-duplicates. [measured 2026-11-14]
2. **The lock pin predates the text he locked.** `version/bars.md` pins blobs at `237b791167` (13:58 PST). The Designer's
   five gap fixes landed in `910f69411e` at 15:13 PST; his "lock" word came at ~15:40 and was recorded in `bf33322d77`.
   Between pin and word, 5 leaves changed (`experience` text of 4: `floor_end_shocks_crossers`, `shock_reach_setting`,
   `live_wire_lights_fuel`, `statics_clear_between_games`; oracle only on `no_unforced_sharp_turn`, `owner_change_coils_wires`)
   and 5 scenes. The current tree hash `5e3aa0d4…` is the one the exam passed 26/26. This run reads the current text as
   0.1.0 and asks whether to re-pin (question 1). [measured]
3. **No scene entry point exists.** `scenes.json` names 26 entry points (`validation.py::scene_*`,
   `gss_playtest_runner.py::scene_walk`); `def scene_` occurs 0 times in the mod. Item `GSS_SCENES_BUILD_EVERY_CORD_A_FOIL`
   (live, proposed) owes them. The live proof that does exist is `northstar/proof_all.py --live`: 156 rows, mapped to leaves
   by `northstar/proof_leaves.py`, whose own rule is "a row cites a leaf it is evidence FOR, not a leaf it proves whole".
   [measured]
4. **The committed judge verdict is still "not covered".** `coverage_verdict.json` is `rm-coverage-judge-1794599377`
   (5 gaps). The fixes are claimed in `coverage_fixes.json` and landed, but no judge has read them. `bars_met` 39 in
   `VERSION.json` is against that old verdict.
5. **Two bars have no build.** `floor_end_shock` and `shock_reach_setting` are `impl: absent`; `proof_leaves.OWED` names
   item `RIMMANDRAKE_BUILD_GSS_FLOOR_END_SHOCK_ANSWERED_WEEK_AGO` (live).
6. **The last live proof is red on two rows.** testq `J20261113T075443Z-3da526` (SteveDesktop, `35aaf354ea`, 2026-11-13):
   154 of 156 PASS; FAIL `M2c_no_sharp_bends` (the same bend three times, item
   `RIMMANDRAKE_UNBEND_GSS_LEAD_AT_JUNCTION_BATTERY_TWICE`) and `SC_no_two_cords_alike`. [ledger, BENCH shard]
7. **Older bar lists still exist.** The walk bars M1 to M22 (`design/validation_walks/RimMandrake/GimmeSomeSlack.md`) and the
   north-star must-show ids (`validation.ROW_SHOWS`) are read by `modcheck floor`; they are not the 47.
8. **The held statements are about FlowWorks pits.** All three GSS statements were said during FlowWorks under-liquid looks;
   the cords' draw order under liquid lives in `src/RimMandrake/GimmeSomeSlack/Source/CordUnderLiquid.cs`, the liquid in
   FlowWorks.

### Questions for him (open; each written here, no bar edited)

1. **Which bytes are 0.1.0?** `bars.md` pins `237b791167`; his "lock" came after `910f69411e` landed the five gap fixes
   (4 leaves' `experience` text changed). This run reads the later text. Re-pin `bars.md` to `910f69411e`?
   Recommendation: yes; it is what stood when he said "lock".
2. **A held defect with no bar.** He reported cords drawn over a battery and over items (2026-11-12 rows 34, 36) and later
   approved the fix (2026-11-13 row 16). No bar of the 47 says "floor cords draw beneath items, buildings and furniture,
   dry and under liquid". Add it to 0.1.0 as a Problem bar (its in-game read `sc_cords_under_items` is specified), or leave
   it to the walk? Recommendation: add it; a cord over a battery is the kind of thing a player rejects.

## History (dated, added to only)

### 2026-11-14 11:25 PST, run begins (rm-builder, detached, offline only)

Brief from the Conductor: rows 1 to 3 of the pilot table, by hand, throwaway scripts, stop before Stage 3. Owner,
2026-11-14: "We need to get this going." Addendum: not the pilot; measure this mod's own counts.

### 2026-11-14 11:32 PST, row 1 done: journal started

- **Cost:** about $2.5 of model spend by the harness budget line (tokens not separately measured), 7 minutes wall. Reading
  dominated: the spec, the version folder, `record.json`, `tree.json`, `scenes.json`, the verdict, the holding store, the
  pilot's journal and table. The offline gate (2 min 21 s) and the 20 selftests (about 2 min 11 s) ran alongside.
- **Boring enough to automate:** the drift check (current blob and tree hash against `bars.md`, with commit times against his
  lock word); "does every `scenes.json` entry point exist"; collecting his words from `sheet.md`; finding held statements for
  a mod (a grep of the holding store by mod name and short name found the three).
- **Needed judgment:** reading the lock-pin drift as "which text did he lock", not as an error to fix; deciding the three held
  statements belong to GSS though they were said at FlowWorks looks.

### 2026-11-14 11:43 PST, row 2 done: Stage 1 finished (the test-and-stage table)

- **What was done.** Every bar got its deciding and supporting tests and the stage that proves it, in the pilot's columns.
  Every built offline test was run by the script (23, all PASS; the slowest are the C# SelfTest at 103 s and the offline
  gate at 141 s, 4 min 38 s in all). In-game tests were not run: their "runnable" is whether their entry exists in code.
- **The measured answer.** 0 of the 26 `scenes.json` scenes has an entry point, so no bar whose test is a scene is fully
  runnable today. 18 bars have a deciding offline test that ran green (the C# SelfTest decides the logic half of most look
  and graph bars; `T_NO_HOSE` decides both `no_hose` bars outright). The 156 older proof rows of `proof_all.py --live` all
  exist in code and passed 154 of 156 on 2026-11-13; they are supports, not deciders, by `proof_leaves.py`'s own rule.
- **The five judge corrections** (g1 to g5 of rm-coverage-judge-1794599377) are all present in the current `scenes.json`
  text (needle check in the script); they were applied by the Designer and landed in `910f69411e`. Nothing new to apply.
  No judge has read them.
- **The held statements** (three, all about cords drawing over or under items) are placed on `drawing_true_to_grid` and
  `walk_scavenger_base`, with FlowWorks' offline `selftest_flowworks_pit_draw_census.py` (PASS today) as support and a new
  in-game draw-order read, `sc_cords_under_items`, specified. No bar of the 47 says "floor cords draw beneath items":
  question 2.
- **The settings sweep, moved offline.** Specified `T_SETTINGS_SWEEP_OFFLINE`: flip-and-return for each of the 26 shipped
  floor settings and each aerial setting, or a listed reason and its live row; every Harmony patch gated by exactly one
  setting (a source read). The C# SelfTest already flips the aerial switches offline (`SwitchFlipChecks.cs`). `sc_settings`
  keeps only the renderer and live-Harmony parts. The leaf is not edited.
- **Specified for Stage 3** (4 offline): `T_SETTINGS_SWEEP_OFFLINE`, `T_SHOCK_RULE_OFFLINE` (who is shocked, as a pure table),
  `T_CORD_GEOMETRY_OFFLINE` (slack ratio 1.4, excursion, unforced turns, with the M2c site as a lab world: the bend that
  failed live three times should be caught offline), `T_STATICS_CENSUS`.
- **Cost:** about $1.6 of model spend (harness budget line, $2.5 to $4.2), 11 minutes wall, of which 4.6 minutes the script
  running tests.
- **Boring enough to automate:** all of the table except the decide/support map: scene lookup by requirement, inventory
  rows to scenes from the verdict checklist, proof rows from `proof_leaves.ROW_LEAVES`, entry-exists, running the tests, the
  correction needle check, the counts and the read view.
- **Needed judgment:** which offline test *decides* a bar versus only supports it (the hand map in the script); calling the
  156 proof rows supports; which bar the three held statements belong to, and seeing that none fits; what of the settings
  sweep can leave the game.
