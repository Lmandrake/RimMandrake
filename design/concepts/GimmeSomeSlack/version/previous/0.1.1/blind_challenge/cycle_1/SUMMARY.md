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
38 of 38 offline tests rerun with their recorded commands, 38 match [measured] (`lane2/reruns.jsonl`). The verdicts all
match. One last line differed only in a wall time (`"wall_s": 315.4` vs `315.7`, T_GATE); the timing mask now covers that,
and `rerun_offline.py --recheck` re-derives the match from the stored rows. T_NO_HOSE, the decider of both offline bars:
PASS, `PASS  G0_clean_copy  want=green got=[]`. T_CORE, T_SHOCK_RULE_OFFLINE and T_SWITCH_OFF_NODE_OFFLINE share one
command, so it ran once for all three (4606/4606).

## Planted
17 faults in `lane2/planted_faults.json`, planted one per call by `lane2/plant_faults.py`
(`WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c1_mut/`). The baseline row comes first and
`{"tree_clean_after": true}` last. One plant does nothing (PF_P_SWITCH_NOT_STYLEABLE: the patch's own fallback adds the same
comp), so it is marked `equivalent` and not counted. 16 counted [measured]:
- **Builder deciders caught 14 of 16.** T_NO_HOSE caught all 4 no-hose plants: a hose label, a GSS mast set to string pipe
  spans (a behaviour plant: no name changes), a GSS-own pipe texture literal, a hose class. T_CORE caught all 6 kernel plants
  (roof on one end only, the re-stringer shocked, a tap that creates power, a span that sags upward, cut spans falling again,
  a fallen wire that ignores walls), plus the floor ends that bite under "only downed lines" and the shipped reach default.
  T_SHOCK_OUTLIVES caught the span shocking with the master off and any job being exempt on a cut.
- **Missed by every offline test: 2.** PF_G_TAPS_DOUBLE_CLAIM_SURPLUS is Polish (see Faults). PF_G_LINK_RANGE_DOUBLED, in the
  caller's range: `overhead_spans` and `spans_above_everything` have no offline decider and are decided at Stage 6 by
  `sc_spans` ("an out-of-range link is refused"), so this miss is expected.
- **Lane 1 caught 9 of 16**: every kernel plant except the fallen-wire one (its row was already red on the baseline), plus 3
  no-hose plants and the default plant. It missed the pipe-kind plant (fault
  RIMMANDRAKE_MISS_SLACK_PIPE_KIND_IN_BLIND_LANE_ONE) and the caller plants, which are game-side.
- No planted behaviour fault survived a green decider of an offline bar.

## Faults
`lane2/faults.json`: **0 Problems, 4 Polish** [measured count]. No rimflow item was filed, because none passes test 1.
- RIMMANDRAKE_NOTE_SLACK_DLL_HOSE_NAMES_ONLY_ALTITUDES (check, HARNESS): clears lane-1 row `ns_dll_no_hose_reel_name`. The
  five hose names in the DLL are altitude and draw-queue constants from `_Shared/SlackGeometry/DrawOrder.cs`, compiled in.
  T_NO_HOSE allows the same five names for the same reason.
- RIMMANDRAKE_CLIP_SLACK_FALLEN_WIRE_TENTH_CELL_INTO_WALL (mod, MOD): clears lane-1 row `fallen_wire_never_on_a_wall`.
  `LayFallen` checks walkability every 0.2 cell, so a bend can clip at most 0.117 cell into a wall face, in 0.25% of random
  walled lays. The wire never crosses a wall.
- RIMMANDRAKE_SHARE_SLACK_TAP_SURPLUS_UNTESTED_IN_CALLER (check, HARNESS): nothing tests two taps on one victim. The shipped
  code shares the surplus correctly, and no bar names several taps.
- RIMMANDRAKE_MISS_SLACK_PIPE_KIND_IN_BLIND_LANE_ONE (check, HARNESS): my own lane-1 scanner misses a `lineKind` pipe plant
  that T_NO_HOSE catches.
- Game-side callers read: CompPowerTap (tap sharing), PowerTheftConsequences (witness and accrual), RM_FallenWireShock
  (CheckPawns, the re-stringer's scoped exemption), ShockRule, RoofOverMast (the 0.1.1 roof gate), AerialMaterials.PipeMats.
  No Problem found.

## Fixes
None. No Problem was found, so `lane2/fixes.jsonl` is empty and no fresh reader is owed.

## Steward's decisions enacted
None acted on in this cycle, so no OWNER ledger event was written. The seven decisions cover cycles 4 to 6 of
0.1.0 and the hold of 2026-11-16 10:45 PM PST, which was released 2026-11-17 9:04 AM PST. None binds 0.1.1 cycle 1: no hold
is live and no cycle count is at three.

## Tests edited
No builder test, decider or test-table row was touched, so no `red-seen` is owed. One test of my own is listed in
`tests_edited.json`: `lane1/blind_no_hose.py`. Lane 2 found the rule that decides the UNSETTLED row `ns_pipe_words_in_code`:
GSS draws a pipe only for its own `lineKind` Pipe def or its own pipe art. Lane 2 also found the scanner missed
PF_NOHOSE_GSS_MAST_LAYS_PIPE. The row is now decided. It reads FAIL on that plant (`lane2/planted_results.jsonl`) and PASS on
the real tree (`lane2/lane1_rows_after_fix.jsonl`: 33 PASS, 2 FAIL owned by Polish faults, 34 not_kernel). Both readings
were taken in this sitting. `lane1/lane1_rows.jsonl` stays as recorded, blind.

## Unsettled
- Lane-1 `ns_pipe_words_in_code` is **settled in lane 2: met.** GSS's aerial engine draws a pipe-pole span only for a def that
  sets `lineKind Pipe`. Only FlowWorks does that (`src/RimMandrake/FlowWorks/Defs/Machinery/RM_PipePoles.xml`), and the
  art is FlowWorks' own (`spanTexPath` `RimMandrake/FlowWorks/PipePole/{look}/PipeSpan`; all four looks exist). GSS ships no
  pipe def, line kind or texture. The rerun row is PASS in `lane2/lane1_rows_after_fix.jsonl`.
- 34 `not_kernel` rows name only game-side bars that prove at Stage 6. The pipeline's reader defers them to Stage 6; they
  name no offline bar.

## Exit
offline_bars: {no_hose: green, no_hose_in_gss: green}
problems_open: 0
exit_met: true

## Owed
Nothing for this cycle: no mod fix was made, so no fresh reader is owed. `maturation.py next GimmeSomeSlack` reads
"exit met: the block says exit_met true and every file check agrees" [measured, 2026-11-20 ~9:20 PM PST]. The Conductor
confirms or refuses the move. Stage 6 owes the 34 game-side bars, including the
four 0.1.1 live halves the journal records as UNRUN.
