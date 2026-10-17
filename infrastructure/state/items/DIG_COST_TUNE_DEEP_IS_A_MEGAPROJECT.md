## spec
Plan P6 of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`), inside P5's pass. Default V1 (veto-able on
`DEPTH_DEFAULTS_ASK_ELEVEN_VETOES`): keep today's work curve, 3,200 × the notch being cut. Rock digging
(`DIG_ROCK_TUNE_STONE_FIGHTS_BACK`) multiplies this curve, it does not replace it.

## verify
- L1: work for notch n is 3,200 × n at every depth to the 20 m cap; one 7 m square ≈ 5½ digger-days and the 4/7/7/4
  square ≈ 45 (state the measured figures, not these estimates).
- L1: settings text says metres; lowering the cap never shallows a dug cell.

## criteria
- A1 L0: offline built cb8194587 — SelfTest DeepDig_cost_curve_numbers_measured (3,200 x notch to 20 m; 7 m square 3.29 digger-days, 4/7/7/4 square 26.73, flat option 16.06, at vanilla's 1.7 work a tick).
- A2 L2: P10 walk — a dig past 2 m takes the curve's work (progress-bar time) in game.
