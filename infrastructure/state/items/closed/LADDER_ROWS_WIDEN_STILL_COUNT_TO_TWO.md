## spec
HARNESS (found 2026-10-23 preparing FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING; review page
`Transient/flowworks_bars_review_20261023.md`). The four depth bars of FlowWorks' `## north star` were re-stated in metres by
the 2026-10-17 depth rebuild (bae58577c) and the 2026-10-20 card ("Keep sinking to 4 m"), but every row that claims them
still stages the old notch ladder that stops at 2 m:
- `pit_depth_ladder_legible` (0.5, 1, 1.5, 2, 4, 8 m): v2 `S1_dig_ladder` asserts depths `[1, 2, 3, 4]` notches
  (`northstar/validation_v2.py` ~2382); extensions plot H `depth_ladder_look` digs pads D=0..4 (`northstar/extensions.py`
  `plot_H_depth_ladder`).
- `pawn_height_ladder_legible` (a colonist lower in each hole down to 4 m, no lower past 4 m): v2 `X1_pawn_height_ladder`
  spawns a **Hare** on D=0..4 (`validation_v2.py` ~3375); plot H `pawn_height_ladder_look` frames a colonist at D=1 and D=4.
- `fill_tier_legible` (six looks: dry, <25 cm, 0.5, 1, 1.5, 2 m+): plot B `fill_tier_four_look` stages F=0..3 in D=3 runs.
- `depth_and_fill_jointly_legible` (1 m water in 1/2/4 m holes; 4 m holes with 0.5/1/2 m): plot B `depth_and_fill_joint_look`
  stages pads D=1..4 half full.
Widen each row to the bar's own ladder (D 0,1,2,3,4,8,16 notches; a colonist; F 0..4+ with the <25 cm rung; the joint
grid), update site_spec plot footprints and each script's mock/selftest so the old ladder is a planted fault that goes red.

## verify
- L0: selftest_extensions.py / selftest_flowworks_northstar.py carry the widened ladders and a planted 2 m ladder reads red.
- L2: the next live v2 + extension_proof run reads S1_dig_ladder / X1 / plot H / plot B on the metres the bars name.
