# GimmeSomeSlack 0.1.0 — blind challenge cycle 6 (judge-1794822890)

> **Why this folder is not `cycle_6/`.** Two blind judges were launched on cycle 6 thirty-four seconds apart:
> `judge-1794822790` (item `RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_SIX_TESTS_FIRST`, the Dispatch tick, 01:54:31 PST) and this one,
> `judge-1794822890` (item `RIMMANDRAKE_JUDGE_SLACK_BLIND_CYCLE_SIX_CONFIRMS_HOSE_FIX`, 01:55:05 PST). The other landed its lane 1 in
> `cycle_6/` first (86a8964054); this record would have overwritten it, so it lives here, beside it, as a second independent blind
> reading for the steward. `maturation.py next` reads `cycle_6/` only. Neither judge saw the other's work before its own lane 1 was
> written (this judge saw only the other's commit subject and its SUMMARY's first lines, after lane 1 was complete).
> Pipeline defect filed and fixed: see Owed / Fixes.

## Start time
2026-11-16T09:55:28Z (01:55 PST). Precondition: `blind_challenge {'visit': 6, 'total': 6}` [measured].

## Changed files to bars
`git diff --name-only 0e6e0c844a origin/main -- <the brief's paths> | grep -v /blind_challenge/` at `33d88d7163`: 14 files [measured]. No locked file changed (`tree.json`, `sheet.md`, `scenes.json` absent from the list).

| changed file | bars whose inputs it touches |
|---|---|
| `src/RimMandrake/GimmeSomeSlack/Source/GimmeSomeSlackMod.cs` (3 lines: the Mod Settings `Header`) | `no_hose`, `no_hose_in_gss`, `mod_settings`, `settings_switch_cleanly` (the settings entry's one header line) |
| `src/RimMandrake/GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll` + `.srchash` | the same four (the DLL rebuilt from that source change) |
| `src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py` | `no_hose`, `no_hose_in_gss` (their decider T_NO_HOSE) |
| `version/test_table.json` | the deciders' recorded results for every bar (a record, no behaviour) |
| `version/stage_record.json`, `version/run_spend.jsonl`, `journal.md`, `ledger/*` (7 files) | none (records) |

Lane-1 scope therefore: the two offline bars `no_hose` and `no_hose_in_gss` first, then the settings bars touched (`mod_settings`, `settings_switch_cleanly`), then the stage-6 bars whose logic sits in the kernels `Source/Aerial/AerialMath.cs` and the Verse-free `Source/Aerial/ShockRule.cs`.

## Lane 1
Blind, from `tree.json`, `sheet.md`, `plan.md`, `record.json` rows, `version/bars.md`, `version/VERSION.json`, the shipped settings (`AerialSettings.cs`, `GimmeSomeSlackMod.cs`) and the kernels. One command:
`LANE1_STAGE=/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c6_lane1 python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_6_judge-1794822890/lane1/run_lane1.py`
(C# rows: `lane1/BlindLane1.cs` against `AerialMath.cs` + `ShockRule.cs`; no-hose rows: `lane1/blind_no_hose.py`, with its own planted-hose self-check.)

**34 rows: 26 PASS, 1 FAIL, 5 UNSETTLED, 2 INFO** [measured, `lane1/lane1_rows.jsonl`].

- no_hose / no_hose_in_gss: 8 decided rows PASS: textures in every content root (125 files), defs and patches parsed as XML (8 files), C# types compiled into the DLL incl. the csproj's `_Shared` includes (74 files), C# player strings, About/Languages, the changed settings header ("Drawn wires to better display simple circuit-like plans underneath."), the shipped DLL's 489 type definitions (none hose/reel; 7 hose-named *members* are shared draw-order numbers and the cord-kind enum value, INFO), and the scanner's self-check (12 planted hoses, each caught by its row).
- INFO `NH_PIPE_SPAN_HOSTING_INFO`: GSS's aerial engine does draw overhead **pipe spans** between FlowWorks pipe poles (`AerialLineKind.Pipe`, `AerialMaterials.PipeMats`). The owner chose this by card on 2026-10-22 (`PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES`, after the 2026-10-10 hose ruling; bar `pipe_pole_switch`). Read as his design, not a hose; the bar's word "pipe" is ambiguous (Polish, lane 2).
- Kernel rows (stage-6 bars): link rules and range swept over the maxSpan slider 8..40, auto-link forest, sag swept 0..0.15, pole-top flatness, pipe-span shape, strands, removal (killed / dismantled / gravship), watchdog, blasts, shock tables (both kernels; the three-way shock setting, default All), floor-end fixer scope, tap conservation swept over tap rate 50..2000, theft sighting and the steady goodwill leak swept over 0..10/day, switch tables, sway bounds, fallen-wire lay on random walled grids: all PASS.
- FAIL `L1_RESTRING_TICKS_SWEEP`: `AerialMath.RestringTicks(NaN)` = -2147483648 (shrunk form: the one input NaN; `Math.Max(0.1, NaN)` is NaN). Lane 2 classes it.
- UNSETTLED (not_kernel, Stage 6): span altitude, shock exemption keyed on the job's target wire, which faction's goodwill falls, the owner-change sweep, fuel ignition.
- Two instrument errors of mine were found and fixed before this record (not kernel faults): the sag row measured a north-south span's screen-down droop as if it were vertical, and the fallen-lay row counted a point lying exactly on a wall's face edge (<= 0.044 cell in) as inside the wall.

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
