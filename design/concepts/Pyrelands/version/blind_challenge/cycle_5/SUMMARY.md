# Pyrelands 0.1.0, blind challenge cycle 5

## Start time
2026-11-22T03:01:26Z (2026-11-21 19:01 PST). Judge unit: RIMMANDRAKE_JUDGE_PYRELANDS_BLIND_CYCLE_FIVE_TESTS_FIRST (seat BENCH, detached).

## Changed files to bars
`git diff --name-only 91be0bc987 origin/main -- <the brief's paths> | grep -v /blind_challenge/` lists 363 files [measured]
(the list: `/tmp` at run time; regenerate with the same command). Most are records (in_game visits, evidence, result
files, exam, journal, test table). The ones whose content is a bar's input:

| changed file | bars whose inputs it touches |
|---|---|
| `Source/Kernel/RM_FireEcoKernel.cs` (burrower nudge kinds added) | ashwallow_dives_unharmed, inv_burrowers_heat_dome; it is also the ash_fertility_probe kernel, so that offline bar is in scope |
| `Source/MapComponent_BurnLine.cs` (nudge reads the kernel) | ashwallow_dives_unharmed, inv_burrowers_heat_dome |
| `Source/RM_JobGiver_BurrowOnFire.cs`, `Defs/ThinkTreeDefs/RM_BurrowOnFireThinkTree.xml` | ashwallow_dives_unharmed, inv_burrowers_heat_dome |
| `Source/FireHawkRewards.cs`, `Languages/English/Keyed/Pyrelands.xml` | inv_firehawk_hunt_rewards; inv_art_and_text (text) |
| `Defs/DamageDefs/RM_FlamefangVenomBite.xml`, `Defs/HediffDefs/RM_FlamefangVenom.xml` | flamefang_bite_carries_venom, inv_animal_roster |
| `Assemblies/FireEcologyHook.dll` (+ `.srchash`) | every C# bar (the built image of the sources above) |
| `preflight_pyrelands.py` | inv_settings_gate (a kernel the brief names) |
| `selftest_pyrelands_settings_sweep.py`, `selftest_pyrelands_site.py` | inv_settings_gate (deciders) |
| `selftest_pyrelands_defs_offline.py` | biome_text_says_engineered (decider) |
| `validation.py`, `human_review.py`, `wind_burn_live.py`, `firehawk_rewards_live.py`, `venom_dose.py` and the other changed `selftest_pyrelands_*.py` | the stage-6 bars their scenes read (opened only in lane 2) |
| `tree.json` (locked) | no leaf changed: only `root_hash` and the `coverage` stamp moved [measured field by field] |
| `scenes.json` (locked) | controls removed from the scenes of ash_ground_and_blowing_ash, populations_are_the_biomes_own, the herd-thirst scene, ruins_stand_blackened, no_ordinary_rain, flamefang_bite_carries_venom and the furnace-beast size scene (stage-6 bars) |

Lane-1 scope from this map: the 6 offline bars (all; the FireEcoKernel change puts the probe's kernel in scope, and the
settings deciders changed), plus the kernel halves of the stage-6 bars above and of every bar a shipped kernel decides.

## Lane 1
Committed blind, before anything sealed was opened. `python3 lane1/run_lane1.py` (C#: `BlindLane1.cs` compiled with the six
game-free kernels as shipped, per-user Windows dotnet, staged under `D:\ClaudeWork\rimmandrake\scratch\pyrelands_blind_c5_lane1`;
Python: `lane1/lane1_defs.py` on the defs, text and settings). Inputs: tree.json, sheet.md, plan.md, VERSION.json,
bars.md, record.json's inventory rows (the inventory bars' text lives there), the three settings files, Defs/, Patches/,
Languages/ (text is part of inv_art_and_text), the kernels; RimSage for six vanilla texture paths.

Rows: **49; 45 PASS, 3 INFO, 1 UNSETTLED, 0 FAIL** [measured].
- Offline bars: ash_fertility_probe 3 rows PASS (wet fresh vs dry old part by part; refuses with the ash field or the gate
  off; 20 000 random cells, seed 20261121); biome_text_says_engineered 2 PASS; inv_firebreak_firefoam 2 PASS;
  inv_lightning_breaker 1 PASS; inv_settings_gate 7 PASS + 1 INFO (every gate predicate shut with its switch off,
  4 000 random input sets; 44 settings saved with their shipped default; 17 slider ranges hold the default; worldgen ships
  off, labelled unsupported); inv_art_and_text 6 PASS + 1 INFO (60 texture paths resolve, 6 of them vanilla Core seen in
  RimSage; 43 defs labelled and described; 36 keyed keys present; no `{A_B}` slot; the approval itself is a record, INFO).
- Stage-6 kernel halves: 27 rows over furnace warmth, charge and sleep ignition, the hawk's drop (600 random grids), the
  letter and crestfeather, the keep-alive and fire clock, front lines, wind probes (1.49 M cases), black rain, the
  burrower nudge and dome, wet roots, scorch-fruit rolls and the allowlist.
- INFO `compound_slider_corners`: at slider corners past the shipped values the fertility cap 2.0 makes a wet fresh
  scar equal wet old ash, and watered can be set below dry: player tuning, not the shipped experience.
- UNSETTLED `game_side_bars`: 17 bars, all stage 6, have no game-free kernel; each settles by its Stage 6 scene.
- One row was reframed before recording: `wind_probes_never_back_or_sideways` first asked the mean carry DISPLACEMENT to
  sit within 1.5 degrees of the wind at one bearing (a number the bar does not hold); it read 2.4 there because a diagonal
  step is sqrt 2 long. It now asks every probe downwind and the mean carry within 10 degrees at every bearing (worst 5.0).

## Lane 2 reruns
`lane2/rerun_offline.py` with each test's recorded command, a private WINBUILD_ROOT per test.
- `reruns.jsonl`: **25 tests** (the 7 deciders of the offline bars, then the 18 other offline/record tests); verdict equal
  to the recorded one on **24 of 25** [measured]. The one difference: `T_SETTINGS_SCREENS` FAIL 855/856 against a recorded
  856/856; its failing row is FlowWorks#Main (a FlowWorks setting in no section), not Pyrelands (all 14 Pyrelands rows ok).
  `T_FUZZ`'s `match` is false only on its timing digits (11.99 s against 11.46 s); `T_ROUND6_GAPS` is red as recorded
  (5 of 18) and decides no offline bar.
- `reruns_after_fix.jsonl` (at 697e3eb8ad; `rerun_relation.py --old c8ef19b610`, once repaired, names 5 touched checks:
  T_SETTINGS_SCREENS, T_DEFS_OFFLINE, RECORD_ART_SHEET, T_ROUND6_GAPS and the live sc_walk): T_SETTINGS_SCREENS PASS 14/14,
  T_DEFS_OFFLINE PASS (11 facts, 22 of 22 mutants), RECORD_ART_SHEET PASS, T_ROUND6_GAPS FAIL as recorded. Their `match`
  reads false where the last line legitimately changed (the scoped command, the new fact). sc_walk is a Stage 6 scene.

## Planted
`lane2/planted_faults.json` (37, written by `make_planted.py`, each `old` checked to occur once), run by `plant_faults.py`
with WINBUILD_ROOT under `D:\ClaudeWork\rimmandrake\scratch\pyrelands_blind_c5_mut\`: per fault, lane 1 and 15 offline suites
in parallel, restore on SIGTERM/SIGINT/SIGHUP (one batch was killed at its bound and the tree came back clean), `git diff
--quiet` after. Caught means a new failing row against the baseline, never an rc alone.
- **33 of 37 caught** [measured] (34 after the T_DEFS_OFFLINE repair). Every fault in an offline bar's kernel or files is
  caught: the probe (4 kernel, 2 caller), the biome text (2), firebreak and breaker (4; the two C# constants by lane 1
  only, Polish), the settings gate (8: kernel, gate, field and Scribe defaults, screen group, worldgen, preflight), art and
  text (4), plus the venom (2), the hawk letter (2) and the think tree (3, by `selftest_pyrelands_burrow_beats_dash.py`).
- Not caught: `TEXT_FURNACE_DESC_GONE` (fixed, below) and three game-side caller faults of the stage-6 ashwallow bar:
  `CALLER_YIELDS_READS_REASK` and `CALLER_IDLE_NONE` (MapComponent_BurnLine's nudge reads the wrong kind) and
  `GIVER_FIRE_LIST_GATE_FLIPPED` (RM_JobGiver_BurrowOnFire's fire-list early-out inverted). That bar is decided live
  (sc_ashwallow, sc_heat_dome), so these are named for the Stage 6 visit, not faults of an offline decider.
- A first description plant (`TEXT_FURNACE_DESC_EMPTY`) broke the XML instead of blanking the text; it was caught for that
  reason only, and `TEXT_FURNACE_DESC_GONE` replaced it as the real case.
- Lane 1 caught 19 faults, T_SETTINGS_SWEEP_OFFLINE 7, T_ASH_PROBE_OFFLINE 6, T_SITE 6, T_LINT 5.

## Faults
`lane2/faults.json`: **2 Problems, both against a check, both FIXED, both `miss_of: 4`; 3 Polish** [measured].
- Problem `RIMMANDRAKE_SCOPE_SETTINGS_SCREENS_DECIDER_TO_ITS_OWN_MOD` (inv_settings_gate): the decider ran every mod's screen
  rows; the table's `mod_rows: 'Pyrelands:'` is read by nothing, so FlowWorks' row made it red.
- Problem `RIMMANDRAKE_PIN_PYRE_DESCRIPTIONS_FURNACE_CARD_COULD_READ_BLANK` (inv_art_and_text): deleting the furnace-beast's
  description left every suite green; its vanilla parent holds none, so its info card would read blank.
- Polish (version/polish.md): the cut check sees defs, not dead C# constants; the burrow-order selftest is outside the
  table; the fertility cap flattens the compound at slider corners past the shipped values.
- No mod fault was found.

## Fixes
`lane2/fixes.jsonl`: two check repairs, each red on its plant and green on the build at 697e3eb8ad [measured]; no mod
code changed, so no fresh reader is owed (`check_repairs`).
- fa0f590a35: `selftest_settings_screens.py --mod`; T_SETTINGS_SCREENS runs `--mod Pyrelands` (plant SETTING_SCREEN_GROUP_DROP:
  rc 1, 13/14; build: rc 0, 14/14).
- ca2accf045: T_DEFS_OFFLINE fact `descriptions_present` and its mutant (plant TEXT_FURNACE_DESC_GONE: rc 1; build: rc 0,
  11 facts, 22 of 22 mutants).
- `maturation.py red-seen` recorded for T_DEFS_OFFLINE and T_SETTINGS_SCREENS (version/evidence/red_seen.json).

Pipeline defects found, filed and fixed in this run:
- `RIMMANDRAKE_SCOPE_SETTINGS_SCREENS_DECIDER_TO_ITS_OWN_MOD`, fa0f590a35 (above).
- `RIMMANDRAKE_KEEP_RERUN_RELATION_READABLE_PAST_THE_STEAM_FOLDER`, 697e3eb8ad: `rerun_relation.py` passed test-table paths
  outside the repo (`/mnt/c/Program Files`) to `git diff`, git exited 128, and all 64 Pyrelands checks read "no readable
  relation". Test first (red: every check unreadable; green: 0 of 20 failed), boundary page promise added. Live reading
  went from 64 unreadable to 5 touched and 59 untouched.
Filed, not fixed: `RIMMANDRAKE_STEADY_GAME_LOCK_TIMING_TEST_UNDER_LOAD_TWENTY` (selftest_game_lock.py's 50 ms rows red at load
17-20, read as new by the door; the 697e3eb8ad landing used the recorded door skip). The FlowWorks fault already had its
item, `RIMMANDRAKE_LIST_FLOWWORKS_SHALLOW_OPACITY_SO_SECTION_RESET_REACHES_IT`; my duplicate was dropped onto it.

## Steward's decisions enacted
None were written for this cycle (read after lane 1 was committed): every bar judged as locked, no bar or criterion
written up as NOTED_FOR_CONDUCTOR, nothing recorded under CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM.

## Tests edited
`tests_edited.json`: `selftest_settings_screens.py` (added `--mod`), `test_table.json` (T_SETTINGS_SCREENS command),
`selftest_pyrelands_defs_offline.py` (one fact, one mutant), `selftest_rerun_relation.py` (one pipeline row). Nothing was
removed or loosened; before/after hashes are in the file.

## Unsettled
- Lane 1 `game_side_bars`: 17 bars, all proving at stage 6, have no game-free kernel; each settles by its Stage 6 scene.
- The three surviving ashwallow caller faults above: settle by sc_ashwallow and sc_heat_dome on the live game.
- No offline bar is unsettled.

## Exit
offline_bars: {ash_fertility_probe: green, biome_text_says_engineered: green, inv_firebreak_firefoam: green, inv_lightning_breaker: green, inv_settings_gate: green, inv_art_and_text: green}
problems_open: 0
exit_met: true

## Owed
- Stage 6: the 17 game-side bars, and a live read of the three ashwallow caller faults that no offline test can see.
- `RIMMANDRAKE_STEADY_GAME_LOCK_TIMING_TEST_UNDER_LOAD_TWENTY` (the owner of that limit decides its danger).
- `RIMMANDRAKE_LIST_FLOWWORKS_SHALLOW_OPACITY_SO_SECTION_RESET_REACHES_IT` (FlowWorks' run).
- `code_review_status.py check selftest_pyrelands_defs_offline.py` reads UNREADABLE because the table's runs_today rows are
  on older builds; the next certificate run (`maturation.py certificate Pyrelands --run`) refreshes them.
