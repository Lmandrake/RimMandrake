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
(pending)

## Planted
(pending)

## Faults
(pending)

## Fixes
(pending)

## Steward's decisions enacted
(pending)

## Tests edited
(pending)

## Unsettled
(pending)

## Exit
(pending)

## Owed
(pending)
