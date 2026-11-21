# GimmeSomeSlack 0.1.1, blind challenge cycle 1

## Start time
2026-11-21T03:30:19Z (2026-11-20 7:30 PM PST), before any input was opened.

## Lane 1
Recorded blind, before any builder test, test table or journal was opened. Command:
`GSS_LANE1_STAGE=/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c1_lane1 python3 lane1/run_lane1.py`.
69 rows [measured]: 32 PASS, 2 FAIL, 35 UNSETTLED (34 `not_kernel` game-side bars plus 1 info row on pipe drawing).
- Offline bars (`no_hose`, `no_hose_in_gss`): my scanner (`lane1/blind_no_hose.py`, which catches its own planted hoses)
  finds nothing in defs, patches, textures or C# source, but **FAIL `ns_dll_no_hose_reel_name`**: the shipped DLL
  `Assemblies/RimMandrakeGimmeSomeSlack.dll` still carries the names `HoseQueue`, `LayerHose`, `HoseBaseLift`,
  `HoseFittingLift` and `HoseTopAltitude`, which the source does not have. UNSETTLED `ns_pipe_words_in_code`: does GSS
  itself draw a pipe span for FlowWorks pipe poles? Lane 2 reads that.
- Kernel (`AerialMath.cs`): 22 property rows (links, auto-link, MST, span curve, sway, removal plan, watchdog, shock,
  knockback, blast, tap, theft, restring) pass. **FAIL `fallen_wire_never_on_a_wall`**: in 15 of 5934 random cases a fallen
  wire puts a ground point inside a wall cell, at most 0.117 cell past the face (seed 20261120; smallest: seed 714544641).
- Settings (`lane1/blind_settings.py`): 44 saved settings have initialiser = saved default, and 14 slider ranges hold
  their defaults (PASS).

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
