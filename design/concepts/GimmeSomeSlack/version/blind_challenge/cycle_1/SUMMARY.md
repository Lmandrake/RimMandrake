# GimmeSomeSlack 0.2.0, blind challenge cycle 1

## Start time
2026-11-23T19:13:53Z (written before any input was opened)

## Lane 1
52 rows: 41 PASS, 3 FAIL, 6 INFO, 2 UNSETTLED (both `not_kernel`, naming only game-side bars) [measured]. One command:
`python3 lane1/run_lane1.py`. Recorded blind: nothing on the stay-blind list was opened. Two honest limits: file names of
`version/evidence/` and the body of the settings screen were seen while listing inputs; no file there was opened.

- Offline bars `no_hose`, `no_hose_in_gss`: 7 PASS, 2 INFO (hose literals; pipe identifiers). The scan covers every
  shipped xml value, every picture name, the picture bytes against FlowWorks' 56 hose pictures, the names and literals of the
  shipped DLL, and the csproj. `blind_no_hose.py --self-check` plants four faults; each one turns a row FAIL.
- One oracle correction before recording: the first run failed on five numbers of `_Shared/SlackGeometry/DrawOrder.cs`
  (HoseQueue and the like). Both mods compile that table, and it draws nothing, so the row leaves exactly those names out.
- FAIL `SWAY_STAYS_HANGING_SLIDER_VANILLA_WIND_GUST`: at strength 2 in wind 2.0 a Gust wire rises to 1.38 x its sag (above
  its chord) in 25% of frames. The shipped strength 1 never does this, at any wind to 2.5.
- FAIL `FALLEN_WIRE_LIES_ON_OPEN_GROUND`: 21 of 4000 random fallen wires clip a wall corner, at most 0.047 cells deep.
- FAIL `FALLEN_STRANDS_ONE_PER_WIRE`: in 517 of 20000 broken 3-wire spans two wire tips lie within 0.25 cells.

## Lane 2 reruns
## Planted
## Faults
## Fixes
## Steward's decisions enacted
## Tests edited
## Unsettled
## Exit
## Owed
