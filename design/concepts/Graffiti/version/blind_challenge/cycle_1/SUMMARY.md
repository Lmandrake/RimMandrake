# Graffiti 0.1.0 — blind challenge, cycle 1

## Start time
2026-11-16T21:46:25Z (UTC), before any input was opened.

## Lane 1
Recorded blind, before any builder test, journal, evidence or test table was opened. Inputs: tree.json, sheet.md, plan.md,
VERSION.json, bars.md, RM_GraffitiMod.cs (defaults, slider range), Defs/ (54 graffiti ThingDefs, 39 temperament rows), the
kernel `Source/Kernel/RM_GraffitiKernel.cs` and its two enum files. 0.1.0 has no offline bar (`proves_at` 2 or 4-5), so lane 1
went to stage-6 bars whose logic lives in the kernel.

`lane1/run_lane1.py` -> `lane1/lane1_rows.jsonl`: **63 rows: 40 PASS, 0 FAIL, 20 UNSETTLED (not_kernel), 3 INFO** [measured].
Seeds are in each random row. INFO rows carried to lane 2:
- `ugliness_craft_vs_def_stat`: the kernel calls CraftBeauty "a mark's net beauty"; best scrawl -2.5 vs awful tally -6, so if the
  game uses craft beauty alone, the def stat (-15 vs -3) is not what a player inspects.
- `temper_clean_freak_multipliers`: clean-freak rows raise bad/ugly by multipliers only in Neurotic 2 (1.1); the "extra debuff"
  must come from `neat`, game-side.
- `settings_count_vs_bar`: 8 settings ship; none for the raider pressure (sheet: "8 today, 11 with...").
- also UNSETTLED `sigil_no_ideo_control`: sigil defs carry no requiresAnyMeme, so the "no ideo, no sigil" control lives in a caller.

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
offline_bars: {}
problems_open: 0
exit_met: false

## Owed
(in progress)
