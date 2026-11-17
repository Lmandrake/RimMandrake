# Graffiti 0.1.0 — blind challenge, cycle 2 (visit 2)

Judge: detached helper, item RIMMANDRAKE_JUDGE_GRAFFITI_BLIND_CYCLE_TWO_TESTS_FIRST (Opus 5.5).

## Start time
2026-11-17T14:20:48Z (06:20 PST), written before opening anything.

## Changed files to bars
`git diff --name-only 5f1a43837e origin/main` (brief's command), 25 files [measured]. Mapped by what each file's diff touches
(source diffs read mechanically; the blinded files mapped by name only):

| changed file | bars whose inputs it touches |
|---|---|
| `Source/Kernel/RM_GraffitiKernel.cs` (+RM_PressureMode, Pressure*, ScrawlVandalism, MarkBeauty) | raider_pressure, inv_raider_future_marks, ugliness_visible, inv_beauty_and_craft, art_skill |
| `Source/RaiderPressure.cs` (new, 277 lines), `Graffiti.csproj` (compiles it) | raider_pressure, inv_raider_future_marks, stands_alone_settings (save/reload of the record) |
| `Source/RM_GraffitiMod.cs` (3 new settings: switch, mode, push) | stands_alone_settings, inv_settings, raider_pressure |
| `Source/Filth_Mark.cs` (NetBeauty now MarkBeauty by form) | ugliness_visible, inv_beauty_and_craft, art_skill |
| `Source/StatPart_GraffitiCraft.cs` (inspect line names a scrawl) | ugliness_visible, inv_beauty_and_craft |
| `Source/RM_GraffitiStage.cs` (new `Pair` staging) | ugliness_visible (its live scene) |
| `northstar_site.py` (3 pressure settings in the site preflight) | stands_alone_settings, inv_settings |
| `Assemblies/RimMandrakeGraffiti.dll` + `.srchash` | every bar proven live (the build of the above) |
| `tree.json` (ugliness_visible re-pinned on his card), `scenes.json` (sc_beauty_pair control) | ugliness_visible |
| `Source/SelfTest/*`, `validation.py`, `selftest_graffiti_ugliness.py`, `test_table.*`, `pilot_throwaway/make_test_table.py` | blinded until lane 1 was recorded; tests of the above (ugliness_visible, raider_pressure) |
| `journal.md`, `bars.md`, `stage_record.json`, `run_spend.jsonl`, `in_game/unrun.jsonl`, `next_version/README.md` | records, no bar input (bars.md re-pins tree.json's blob for ugliness_visible) |

Lane-1 scope from the changes: raider_pressure, inv_raider_future_marks, ugliness_visible, inv_beauty_and_craft, art_skill,
stands_alone_settings, inv_settings. "All once": the rest of the kernel's bars were tested too.

## Lane 1
Recorded blind 2026-11-17 06:28 PST, before opening anything sealed. Inputs: tree.json, sheet.md, plan.md, VERSION.json,
bars.md, record.json's inventory text, RM_GraffitiMod.cs (defaults, slider ranges), Defs/ (TemperamentDefs, mark forms),
the kernel. `lane1/BlindLane1.cs`, `python3 lane1/run_lane1.py [--kernel <file>]`.

**55 rows: 37 PASS, 0 FAIL, 3 INFO, 15 UNSETTLED** [measured] (14 `not_kernel` rows for game-side logic, owed to stage 6,
and one kernel row, L1_TRIBUTE_RIVAL_BAND). No offline bar exists in 0.1.0, so every row's bars prove at stage 6.
Leads for lane 2 (INFO): a hand-edited NaN push gives a NaN factor (the slider cannot reach it); the clean freak's extra
debuff is in the table only for Neurotic:2 (the rest must come from `neat` in the caller); a tribute gives no reaction to a
viewer at -29..-15 toward its subject.

## Lane 2 reruns
`python3 lane2/rerun_offline.py` (prefix-tolerant last-line compare, private WINBUILD_ROOT): **14 offline tests rerun, 14 of 14
the recorded verdict, 13 of 14 the recorded last line** [measured] (`lane2/reruns.jsonl`). The 14th, T_MSG_COUNTERS_RESET, is red both
times for the same reason (its file `selftest_graffiti_message_counters.py` does not exist) and its last line differs only in the
clone path. T_SHIP_CHECK red both times ("Drift found": the game copy is not this tree; never deployed here). Neither decides an
offline bar. After the fixes, both edited deciders rerun green: `lane2/reruns_after_fix.jsonl` (2 of 2).

## Planted
44 faults in `lane2/planted_faults.json` (20 kernel, 19 game-side callers, settings and staging, 5 in tests and scenes),
run by `lane2/plant_faults.py` against 10 offline suites (+T_LINT for settings/scene files) and lane 1; baseline all green.
**Before the fixes 27 of 44 caught; after, 30 of 44** [measured] (`lane2/planted_results.jsonl`, the last row per fault counts;
it ends `tree_clean_after: true`). One first-pass catch of PF_C_WORN_NEVER_WEARS was `OSError: Cannot allocate memory` in
T_RAID_TAG_BUILT_WALL_ONLY, not a catch: rerun, it survives.
- Kernel: 20 of 20 caught by lane 1; T_FUZZ 16 of 20 (see RIMMANDRAKE_EXTEND_GRAFFITI_FUZZ_RULES_ONLY_LANE_ONE_SAW).
- Survivors past a green **offline decider** (the Problems): PF_C_NETBEAUTY_SCRAWL_AS_TAG and PF_C_STATPART_KEEPS_DEF past
  T_UGLINESS_OFFLINE (decides ugliness_visible), PF_C_WEATHER_ROOF_INVERTED past T_WEATHER_OFFLINE (decides
  weathering_bounds_marks). All three caught after the fixes.
- Survivors whose bars have only live deciders (owed to Stage 6, not Problems against an offline test): the four RaiderPressure.cs
  faults (postfix never pushes, crossed-out marks stand, never lifts, letter with no look-target) and the csproj dropping
  RaiderPressure.cs (sc_raider_pressure decides); RM_GraffitiStage.Pair uncapped / skipping awful and poor (sc_beauty_pair);
  validation.py's two weakened pressure checks (no offline test reads that scene); NetBeauty's crossed-out cap lifted and worn
  removed (no bar pins the number); the inspect line's "a vandal's scrawl" label inverted (cosmetic).
- Survivors that weaken a test itself (no meta-check exists, none expected): T_UGLINESS ignoring its source half, the fuzz's
  pressure family dropped.

## Faults
`lane2/faults.json`, each filed as a rimflow item [measured: 6 filed]:

| id | class | bar | status | miss_of |
|---|---|---|---|---|
| RIMMANDRAKE_TIGHTEN_GRAFFITI_UGLINESS_READ_SCRAWL_PASSED_AS_TAG | Problem | ugliness_visible | FIXED dad3e902ac | 0 |
| RIMMANDRAKE_CHECK_GRAFFITI_WEATHER_CALLER_ROOF_KERNEL_NEVER_SAW | Problem | weathering_bounds_marks | FIXED dad3e902ac | 1 |
| RIMMANDRAKE_KEEP_WEATHERED_SCRAWL_UGLIER_THAN_FRESH_TALLY | Polish | ugliness_visible | PENDING | 0 |
| RIMMANDRAKE_CLAMP_GRAFFITI_PUSH_ON_LOAD_NAN_REACHES_RAIDS | Polish | raider_pressure | PENDING | 0 |
| RIMMANDRAKE_HOLD_SOONER_RETURN_WHEN_MODE_FLIPS_MID_CLAIM | Polish | raider_pressure | PENDING | 0 |
| RIMMANDRAKE_EXTEND_GRAFFITI_FUZZ_RULES_ONLY_LANE_ONE_SAW | Polish | visitors, temperament, sits_on_wall, stories_not_tax | PENDING | 1 |

2 Problems (1 miss_of), 4 Polish (1 miss_of). Both Problems are tests short of their own claims; the mod code itself was right in
every case read. No bar or criterion was found wrong: nothing NOTED_FOR_CONDUCTOR.

## Fixes
Both test fixes landed in **dad3e902ac** (`./publish`), red first: `lane2/fixes.jsonl`. Each catching run is
`python3 lane2/catch_check.py --fault <id> --test <T>` (rc 0 = caught): rc 1 on the parent f2618b2a60 (the old test file from
that sha; the mod source is byte-identical there), rc 0 at dad3e902ac, and the unplanted test rc 0 at dad3e902ac. Lane 1 rerun
after the fixes: `lane2/lane1_rows_after_fix.jsonl`, 37 PASS, 0 FAIL, 3 INFO, 15 UNSETTLED (unchanged). Both items closed at
dad3e902ac. The two test files stay DIRTY in code_review_status (never marked clean before; this pass read the changed functions,
not the whole files).

## Steward's decisions enacted
None written for this cycle; the standing default held (every bar judged as locked, Problems fixed in place red first). No ledger entry under CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM was needed.

## Tests edited
`tests_edited.json`: `src/RimMandrake/Utils/selftest_graffiti_ugliness.py`, `src/RimMandrake/Utils/selftest_graffiti_weather.py` (both tightened, mutants added; no assertion weakened, skipped or removed).

## Unsettled
- 14 `not_kernel` lane-1 rows: game-side behaviour of every bar, owed to Stage 6 (all 47 bars prove at stage 6).
- L1_TRIBUTE_RIVAL_BAND: a viewer at -29..-15 toward a tribute's subject takes no reaction; the bar does not say whose rival or where
  rivalry starts. Settled by the live tribute_memorial scene's rival, read with its opinions.
- The raider-pressure callers (postfix, lift, letter target, crossed-out marks) have no offline guard; only sc_raider_pressure decides.

## Exit
offline_bars: {}
problems_open: 0
exit_met: false

No offline bar exists in 0.1.0: all 47 bars prove at stage 6 (`test_table.json` bars[].proves_at), so `offline_bars` is empty.
Two Problems were found and FIXED in this cycle, so by the brief this cycle's exit is not met: a new blind judge is owed.

## Owed
- A new blind judge (cycle 3 of this visit), since this cycle fixed two Problems.
- Stage 6: every `not_kernel` row and the survivors listed under Planted.
- The four Polish items (PENDING, not part of passing).
