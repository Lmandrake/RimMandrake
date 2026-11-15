# Pyrelands 0.1.0 — blind offline challenge (Stages 4 and 5), cycle 1

## Start time
2026-11-15T08:35:40Z (UTC), before any input was opened. Judge: detached helper RIMMANDRAKE_CHALLENGE_PYRELANDS_BLIND_JUDGE_REFUSED_FIRST (seat BENCH).

## Lane 1
Recorded before any lane-2 input was opened (journal, exam, evidence, test table, builder selftests: unopened).
`lane1/run_lane1.py` (C# `BlindLane1.cs` over the six kernel files + Python def/text rows): **97 rows: 83 PASS, 1 FAIL,
5 INFO, 8 UNSETTLED** [measured, `lane1/lane1_rows.jsonl`].
- FAIL `herd_anchor_never_fresh_ash` (bar `ullai_graze_old_burns`): with only a fresh burn in the history,
  `RM_BurnKernel.HistoryIndexAgo` falls back to the OLDEST sample (an hour old) and `FollowBurnDecision` sends the herd to
  it, i.e. to fresh ash. Shrunk form: one sample 2500 ticks old, lag 2 days. Kernel-level; whether a caller rejects a
  too-young anchor is lane 2's.
- INFO rows: the watered/dry sliders can invert the water lift; the 2-day quiet spell before a relight; a burn grid
  defaulting to 0 would read as burned (ScarStampTick/BurnBonus); `MarkOnce` clears the whole roll set past its bound;
  a herd with no record drifts to the nearest ash of any age.
- UNSETTLED (not_kernel, owed to Stage 6): the walk, the sprayer, the rite hook, the three skies' look, venom severity in
  play, the live census, grass green shares, the art.

## Lane 2 reruns
(pending)

## Planted
(pending)

## Faults
(pending)

## Fixes
(pending)

## Tests edited
(pending)

## Rain question
(pending)

## Unsettled
(pending)

## Exit
(pending)

## Owed
(pending)
