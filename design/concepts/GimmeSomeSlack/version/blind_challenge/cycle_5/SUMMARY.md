# GimmeSomeSlack 0.1.0, blind challenge cycle 5

Judge: detached BENCH helper on RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_FIVE_FROM_PACKET (holder run-1794814806, role blind_judge).

## Start time
2026-11-16T07:40:43Z (11:40 PM PST 2026-11-15), before any mod file was opened.

Blindness note: this run started from the mod-ledger packet, which lists the mod's open findings by earlier cycles
(titles, evidence lines, proposed fixes). The judge therefore was NOT blind to earlier findings. Recorded as a pipeline
defect (see Owed / Faults).

## Changed files to bars
`git diff --name-only 47882f8c22 origin/main` (brief's command) at 863ca5c461 lists 11 files [measured]:

| changed file | bars whose inputs it touches |
|---|---|
| `src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py` | `no_hose`, `no_hose_in_gss` (their decider T_NO_HOSE) |
| `design/concepts/GimmeSomeSlack/version/test_table.json` | bars on its changed lines: mapped in lane 2 (the file is sealed until lane 1 is committed) |
| `version/stage_record.json`, `version/run_spend.jsonl`, `journal.md`, `ledger/*.jsonl`, `ledger/views/*` | records only: no bar input |

No locked file (`tree.json`, `sheet.md`, `scenes.json`, `plan.md`, `record.json`, `VERSION.json`, `bars.md`) changed.
Lane-1 scope: the two offline bars, then the kernel `AerialMath.cs` for stage-6 bars whose logic lives there.

## Lane 1
Written from tree.json, sheet.md, record.json (the no_hose row), VERSION.json, bars.md, AerialSettings.cs (defaults,
slider ranges), Defs/, Patches/ and the kernel AerialMath.cs; nothing sealed opened. Command:
`python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_5/lane1/run_lane1.py` (rc 1).

70 rows [measured]: 21 PASS, 7 FAIL, 3 INFO, 39 UNSETTLED (39 `not_kernel`, every one a stage-6+ bar).

FAIL rows:
- `NH_SOURCE_NO_TEXT_SAYING_GSS_DRAWS_PIPES` (no_hose, no_hose_in_gss): the Mod Settings header,
  `GimmeSomeSlackMod.Header` = "Drawn flexible pipes and wires to better display simple circuit-like plans underneath."
- `NH_SHIPPED_DLL_NO_HOSE_SYMBOL` (no_hose, no_hose_in_gss): the shipped DLL holds `HoseBaseLift`, `HoseFittingLift`,
  `HoseQueue`, `HoseTopAltitude`, `LayerHose` (from the shared `_Shared/SlackGeometry/DrawOrder.cs` compiled in; no GSS
  caller found by grep).
- `L1_SPAN_VISIBLE_OFF_CHORD_EVERY_BEARING` (spans_above_everything): 104 of 2000 random spans at sag 0.06 leave their chord
  by under 0.1 cell; shrunk to a north-south span, drawn exactly on its chord.
- `L1_RESTRING_TICKS_SWEEP` (restring_cut_span): `RestringTicks(NaN)` = -2147483648, `RestringTicks(+inf)` = 0.
- `L1_FALLEN_ON_GROUND_NOT_IN_WALLS` (fallen_span_on_ground): 7 of 2500 fallen wires put a grounded point inside a wall cell
  (deepest 0.139 cell), Blocked false.
- `L1_FALLEN_LENGTH_NOTHING_CREATED` (fallen_span_on_ground): 7 of 2500 draw over 2 x cable + 2 cells on the ground
  (13.9 cells for a 5.6-cell cable).
- `L1_FALLEN_STRANDS_EACH_ITS_OWN` (fallen_span_on_ground): 32 tip pairs under 0.25 cell apart in 1000 spans (closest 0.066).

INFO: `NH_PIPE_POLE_SPANS_DRAWN_BY_GSS_CODE` (GSS code draws FlowWorks' overhead pipe-pole spans: the sheet's "no ... pipe
is drawn by this mod" and the record's `pipe_pole_switch` bar disagree), `NH_DEFS_PROSE_MENTIONS`, `L1_SPAN_SAG_SLIDER_ZERO_IS_STRAIGHT`.

Blindness, stated plainly: the run's packet named earlier cycles' open findings, several of which (restring NaN, fallen wire
in walls / coils, tips meeting, north-south span, pipe-pole wording) overlap these rows. The rows were written from the bars
and measured here, but they are not independent of that knowledge.

## Lane 2 reruns
(owed)

## Planted
(owed)

## Faults
(owed)

## Fixes
(owed)

## Steward's decisions enacted
(owed)

## Tests edited
(owed)

## Unsettled
(owed)

## Exit
(owed)

## Owed
(owed)
