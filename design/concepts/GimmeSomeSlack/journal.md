# Gimme Some Slack: journal

The mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. Below it the
**history** is only added to. Test of this file: a restarted Conductor can do the next stage change from it alone.

This mod is not the pilot. It advances beside Explosive Knockback, offline only (owner by card 2026-11-14, "All four now,
offline only"), and its table uses the pilot's columns (`design/concepts/ExplosiveKnockback/version/test_table.json`) so the
mods read alike.

## The mod as it stands

- **Design Version 0.1.0, locked** on his word 2026-11-13 ~3:40 PM PST (`version/VERSION.json`); the lock record pins the text
  at that word, `bf33322d77` (re-pinned 2026-11-14, steward's decision). Code: `src/RimMandrake/GimmeSomeSlack/` (C#, 62
  sources; C# SelfTest 4508 checks; `validation.py`; `northstar/proof_all.py`, the one dense live proof).
- **Stage now:** Stage 3 (reconcile) done 2026-11-14 13:05 PST, offline only. Preflight: 4 refusals before, **1 after**
  (`built_offline_tests_green`: `T_CORD_GEOMETRY_OFFLINE` red, filed `RIMMANDRAKE_SLACKEN_GSS_SHORT_LEADS_UNDER_BAR`); after
  the bar his card added (2026-11-14 14:10 PST) **2**, the second `built_mod_decider_entries_exist`: `sc_cords_under_items`
  has no entry point yet (owed Stage 3, item `GSS_SCENES_BUILD_EVERY_CORD_A_FOIL`). [measured]
  Next: build that entry and decide the geometry red (mod or criterion), then Stages 4 and 5 (blind challenge), then Stage 6
  runs the 27 scenes live.
- **Bars:** 48 (23 inventory rows of `record.json` + 26 leaves of `tree.json`; `shock_reach_setting` is both, so 49 rows
  name 48 ids; `cords_draw_under_things` added by his card 2026-11-14). The test-and-stage table is
  `version/test_table.json` (read view `version/test_table.md`), made by the throwaway `version/make_test_table.py`. Of 48
  bars: 48 have a deciding test runnable today, 46 have every deciding test runnable (not `cords_draw_under_things`, whose
  scene is owed, nor `walk_scavenger_base`, his walk), 22 have offline deciders all green today. [measured, 14:10 PST]
- **Waiting on:** the geometry red's reading (below, question 4); Stage 6 for every in-game test (all UNRUN, commands in
  `version/test_table.md`). Built in Stage 3: the floor-end shock and its three-value setting; the 4 offline tests; the 26
  scene entry points; tier `gimmesomeslack_flowworks`.
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
2. **The lock was re-pinned once.** The first pin (`237b791167`, 13:58 PST) predated the Designer's five gap fixes
   (`910f69411e`, 15:13); his "lock" came at ~15:40 (`bf33322d77`). Re-pinned to `bf33322d77` on 2026-11-14 by the steward's
   decision; no bar was edited.
3. **A scene is a verdict over the one dense proof, not a load of its own.** The 26 entry points (`validation.py::scene_*`,
   `gss_playtest_runner.py::scene_walk`) read the rows `proof_all.py --live` makes and decide by the rows citing the scene's
   leaves (`validation.scene_verdict`; a missing row is UNMEASURED, never a pass). Replay any saved result offline with
   `validation.py --scenes-from <json>`.
4. **The committed judge verdict is still "not covered".** `coverage_verdict.json` is `rm-coverage-judge-1794599377`
   (5 gaps). The fixes are claimed in `coverage_fixes.json` and landed, but no judge has read them. `bars_met` 39 in
   `VERSION.json` is against that old verdict.
5. **The old on/off shock name still exists, as a mirror.** `AerialSettings.fallenWireShock` is now derived
   (`shockReach != None`), kept only because FlowWorks' `lines_proof.py` reads it; the setting is `shockReach`. `record.json`
   still says `impl: absent` for `floor_end_shock` and `shock_reach_setting` (a locked file: not edited).
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
3. ~~Two scenes need FlowWorks~~: answered by the steward, tier `gimmesomeslack_flowworks` (2026-11-14). Question 1 is
   answered the same way (re-pinned).
4. **The geometry bar reads red offline.** `T_CORD_GEOMETRY_OFFLINE` reads the `cords_lie_slack` and `no_unforced_sharp_turn`
   oracles as written: 25 of 76 strands on the oracle scenes are under 1.4 times their chord (all short leads, chord 2 to 3
   cells), 1 long strand is flat, 7 bends are unforced. Is "1.4 per edge" meant for a 2-cell lead? If yes, the builder must
   slacken short leads (a mod fix); if no, the bar needs a length floor (his change, through the neutral fixer). The unforced
   bends are the mod's either way. Item `RIMMANDRAKE_SLACKEN_GSS_SHORT_LEADS_UNDER_BAR`.
5. **Seven Harmony patches belong to no switch.** The `settings_switch_cleanly` oracle says every patch maps to exactly one
   switch, none unmapped. Seven are save-integrity bookkeeping (keep our components out of saves, load pre-rename saves,
   drain the style queue before a save, mark sections stale); a switch on them would break saves. The sweep lists them as
   "infra, no switch by design" and passes. Is that what the bar means?

## History (dated, added to only)

### Conductor interventions (one line each, added to only; the form is in the spec §5, "The steward and the journal")

- CONDUCTOR INTERVENED (stage 3, 2026-11-14 12:15 PST, kind re-pin): the lock record is re-pinned to the text he actually locked (his lock word came after the gap fixes); done in `a4be8a3ff3` at `bf33322d77`, answering question 1. Source: Steward's decisions in the Stage 3 brief of run `rm-detached-bench-rimmandrake-advance-gimmesomeslack-offli-1794687332`.
- CONDUCTOR INTERVENED (stage 3, 2026-11-14 2:10 PM PST, kind bar-added): bar `cords_draw_under_things` added to 0.1.0 (record.json inventory, scope opened_by_owner): "A floor cord, and the strip or connector at its junction, draws beneath any item, building or furniture standing over it, a battery included, on dry floor and under the liquid of a pit alike, so nothing a player put down ever has a wire showing through it." Decided by `T_CORE` (slideunder "under", stage 4-5) and `sc_cords_under_items` (stage 6, entry owed Stage 3); the three held rows moved onto it; record.json re-pinned `a6fa51434c`. Source: owner by card 2026-11-14 (OWNER:1794693278631337978).

### 2026-11-14 11:25 PST, run begins (rm-builder, detached, offline only)

Brief from the Conductor: rows 1 to 3 of the pilot table, by hand, throwaway scripts, stop before Stage 3. Owner,
2026-11-14: "We need to get this going." Addendum: not the pilot; measure this mod's own counts.

### 2026-11-14 11:32 PST, row 1 done: journal started

- **Cost:** about $2.5 of model spend by the harness budget line (tokens not separately measured), 7 minutes wall. Reading
  dominated: the spec, the version folder, `record.json`, `tree.json`, `scenes.json`, the verdict, the holding store, the
  pilot's journal and table. The offline gate (2 min 21 s) and the 20 selftests (about 2 min 11 s) ran alongside.
- **Boring enough to automate:** the drift check (current blob and tree hash against `bars.md`, with commit times against his
  lock word); "does every `scenes.json` entry point exist"; collecting his words from `sheet.md`; finding held statements for
  a mod (a grep by mod name finds two; the third, row 36, says "the wires" and belongs by context to row 34).
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
  in-game draw-order read, `sc_cords_under_items`, specified. No bar of the 47 says "floor cords draw beneath items"
  (his card 2026-11-14 added it: `cords_draw_under_things`).
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

### 2026-11-14 11:48 PST, row 3 done: Stage 2, a throwaway preflight

- **Program:** `version/preflight_throwaway.py`, no model; record `version/preflight.json`. 19 checks: the table holds
  exactly `required_ids`; every bar has a deciding test; every test names a known stage; every cited test is listed;
  every game test says why the game is needed and every full-list test why the full list; every named path is real (1091
  paths); every `record.json` evidence path or item is real; built mod: every deciding scene's entry exists and every
  deciding offline test was built and is green; the 59 def-like names in the bars' text are defs (dump of 2026-11-12, 316
  mods, plus our XML), C# symbols or files; the mods the scenes stage are on the tier; all DLC on the tier; every held
  statement naming GSS is placed; the locked blobs match `bars.md`.
- **Watched it fail:** `GSS_PREFLIGHT_PLANT=1` plants one fault each (an unlisted test, a missing file, an empty
  why-the-game, a dropped held placement, a fake item, a fake def name); all six checks went red. [measured]
- **Its own first misses, fixed before the verdict:** it refused 24 items that exist only in the ledger (no prose file) and
  two paths carrying `:line`; and it took "FlowWorks DLL md5 … + GSS" in a build column as a statement about GSS (17 false
  rows). After the fixes those checks pass.
- **Verdict: refuse, 4 refusals** (run 10.4 s, of which 10.0 s reading the 442 MB def dump over `/mnt/c`):
  1. `built_mod_decider_entries_exist`: 26 deciding scenes have no entry point. Back to Stage 3 (reconcile), item
     `GSS_SCENES_BUILD_EVERY_CORD_A_FOIL`.
  2. `built_mod_offline_deciders_run`: 3 deciding offline tests are specified, not built (`T_SETTINGS_SWEEP_OFFLINE`,
     `T_SHOCK_RULE_OFFLINE`, `T_CORD_GEOMETRY_OFFLINE`). Back to Stage 3.
  3. `named_mods_on_the_tier`: `sc_settings` and `sc_shock_reach` stage FlowWorks; the tier lacks it. Back to Stage 1 as a
     fact (question 3).
  4. `lock_pins_current`: 6 of the 8 pinned files differ from `bars.md`'s blobs. Back to Stage 1: re-pin (question 1).
  Refusals 1 and 2 are Stage 3 work, as in the pilot.
- **Cost:** about $1.2 of model spend (harness budget line, $4.2 to $5.4), 5 minutes wall.
- **Boring enough to automate:** all of it; this script is a fair seed for the Stage 2 program (spec §9 build order 3).
  The dump read wants a cached defName index keyed on the dump's fingerprint (10 s each run over `/mnt/c`).
- **Needed judgment:** whether a refusal is the mod's or the instrument's (three of the first seven were the instrument);
  where a refusal goes back to (a missing build is Stage 3, a wrong fact is Stage 1); and whether "every named def is
  real" is even testable from prose: the name check covers CamelCase and `RM_` names only, so a plain word like "battery"
  or "chemfuel puddle" is not checked.

### 2026-11-14 12:40 PST, Stage 3 (reconcile) begins; batch 1: lock re-pinned, FlowWorks tier, preflight def hole

- **Re-pinned** (steward's decision, Conductor, delegated): `version/bars.md` and `VERSION.json` now pin the 8 locked files at
  `bf33322d77` (his lock word, 15:40 PST), not `237b791167` (13:58). What changed between the two: only the Designer's five
  gap fixes of `910f69411e` (the `experience` text of 4 leaves, the oracle of 2, the text of 5 scenes, the exam and stage
  record). No bar's meaning was edited by this run; all 8 files at HEAD are byte-identical to `bf33322d77`. [measured]
  Answers question 1 by the steward's call.
- **The test mod list for the two FlowWorks scenes:** tier `gimmesomeslack_flowworks` in `modset_builder.TIERS` (the
  `gimmesomeslack` tier plus `mandrake.rm.flowworks`, both tiers' guards; dry-resolves to 12 mods). `sc_settings` and
  `sc_shock_reach` carry `tier` in the table. Answers question 3 as recommended.
- **Preflight stale-def hole fixed** (lesson `20261114T194216Z`): a name the 2026-11-12 dump attributes to a `mandrake.*`
  mod, or any `RM_`/`RSW_`/`RUT_` name, counts as a def only if the repo's current XML under `src/RimMandrake` defines it;
  otherwise it is refused as `STALE_DUMP_DEF`. Planted `RM_PlantedStaleDef` (in the dump, not the repo): refused. The
  tier check now reads each scene's own tier (planted FlowWorks scene on the GSS tier: refused).
- **Preflight:** 4 refusals before, 2 after (`built_mod_decider_entries_exist` 26, `built_mod_offline_deciders_run` 3).

### 2026-11-14 13:05 PST, Stage 3 (reconcile) done: batches 2 to 5

- **Built, mod:** `Aerial/ShockRule.cs` (the who-is-shocked rule, pure), `Aerial/FloorEndShock.cs` (every live floor-cord end
  bites at its end cell, whatever the spark budget, with the overhead master off; the colonist whose job builds a conduit
  blueprint on that end or beside it is spared), setting `shockReach` (None, Only downed lines, All; default All; radio
  buttons; applies at once) replacing the `fallenWireShock` box. DLL built (`63ac285403`).
- **Built, offline tests:** `T_SHOCK_RULE_OFFLINE` (36-row table plus source binding with 4 planted bindings; red on the old
  rule, 4 FAILs, then green), `T_STATICS_CENSUS` (349 statics classed; planted leak and dropped reset refused),
  `T_SETTINGS_SWEEP_OFFLINE` (48 settings owned, 30 patches mapped; planted dropped read and ungated patch refused; its first
  run refused 4 read sites, which were the instrument's, and 4 patches, now classed infra: question 5),
  `T_CORD_GEOMETRY_OFFLINE` (**red**, question 4; runs under `--geometry` so T_CORE stays a green gate).
- **Built, in-game (UNRUN):** the 26 scene entry points; 10 new rows `SC_floor_end_*` and `SC_shock_reach_*` in
  `northstar/scene_rows.py` (2 UNMEASURED by design: the fixer's blueprint order has no known bridge call offline; the
  FlowWorks deck cord per value runs on the FlowWorks tier). Commands: `version/test_table.md`.
- **Not built:** `sc_cords_under_items` (now the deciding scene of `cords_draw_under_things`, owed Stage 3); the M2c lab world (needs a `rect:` capture of the live core site).
- **Cost:** about $10.3 of model spend for Stage 3 by the harness budget line (this run's whole $15 cap; tokens not
  separately measured), 50 minutes wall (12:15 to 13:05 PST), of which about 15 minutes were tests running (C# SelfTest 3
  times at ~105 s, the offline gate twice at ~140 s, the full table run 6.4 min). His minutes: 0.
- **Boring enough to automate:** re-pinning a lock (blob per file at a named commit, a journal line); the red-first ritual
  for a C# rule (stub the old rule, run, restore); regenerating the table and re-running the preflight after each batch;
  the scene entry points themselves (each is "the rows citing my leaves", now one generic `scene_verdict`); the statics and
  settings censuses (both are source reads any mod could share).
- **Needed judgment:** whether a red is the mod's or the criterion's (geometry: left red and filed, never loosened);
  whether save-integrity patches count as "unmapped" (question 5); keeping a derived `fallenWireShock` for another mod's
  reader rather than editing FlowWorks (another helper's code); making scenes verdicts over one dense run rather than 26
  loads (the spec's Stage 6 asks for dense maps); what a test may assume of bridge tools it cannot try offline.

### Run total

About $5.4 of model spend and 23 minutes wall for rows 1 to 3 (11:25 to 11:48 PST), plus the 4.6-minute test run inside
row 2; Stage 3 about $10.3 and 50 minutes (12:15 to 13:05 PST). No helpers, no game, no bridge.
