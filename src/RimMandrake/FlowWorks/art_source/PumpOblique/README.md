# PumpOblique — LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB

The four RM_LiquidPump looks redrawn from plan-view medallions to the oblique building camera, deterministically
from the installed plan art (`plan/`, a copy of the 2026-10-23 installed textures, kept as the source and revert).

- `oblique_pump.py [outdir]` writes `<Look>.png` for Scrapper, Industrial, Modern and Futuristic. Its output is
  deterministic and is not committed.
- `check_oblique.py [--dir D]` is the gate. Each look must be oblique, meaning the south wall is no brighter than
  0.80 × the north rim. Each of the four ports must be centred on its edge centre within 0.02 cell, and its face must
  be within 0.10 cell of the edge.

Measured 2026-11-05:

| art | oblique ratio | ports |
|---|---|---|
| installed plan art | 0.98–1.06, all four FAIL | pass |
| candidates | 0.51–0.58 | all 16 pass (offsets ≤ 0.010 cell, gaps ≤ 0.053 cell) |

## Candidates

The candidates are in the art store (`art.py put`), sha256 prefixes:

| look | sha256 prefix |
|---|---|
| Scrapper | c9bda35b4bc0 |
| Industrial | 307c455cd973 |
| Modern | 3188aa2146b9 |
| Futuristic | 67b0925cb84c |

Copies and a before/after sheet at true scale are in `D:\ClaudeWork\rimmandrake\relentless\LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB\candidates\`.

Three fresh Opus judges looked at successive versions. Their verdicts are `judge_verdict_v1..v3.json` in the folder
above `candidates\`; each version's defects were fixed in the next.

- **v1:** rejected for a black-box wall and streaks.
- **v2:** rejected because the top was too round.
- **v3:** said the art reads oblique (the top face's height is 0.575 of its width). It rejected the art for a
  translucent seam, ghost rings in the wall and a south neck with no collar.

The current version fixes all three v3 findings. It has not been judged by a fresh agent.

## Blocked: owner-kept art

All four installed looks are owner-KEPT pictures (960ddf23f012, ea7ddc15b970, 87725568582f, afffd14b1d58), so
`art.py install --why` refuses. Replacing kept art is his call (delegation_policy.md §2.3).

## Once he rules

1. Install each look:

   ```
   art.py install src/RimMandrake/FlowWorks <rel> <sha> --owner-said|--by-card ...
   ```

   The `<rel>` values are:
   - `Textures/Things/Building/FlowWorks/Machinery/RM_LiquidPump.png` (Scrapper)
   - `Textures/RimMandrake/FlowWorks/Pump/<Look>/RM_LiquidPump.png` (Industrial, Modern, Futuristic)
2. Regenerate the under-coupler reach table:

   ```
   python3 src/RimMandrake/FlowWorks/art_source/UnderCouplers/under_coupler_reach.py --write
   ```

   This rewrites `UnderCouplerReach.cs`, and the DLL is rebuilt by publish.
3. Promote `check_oblique.py` to `src/RimMandrake/FlowWorks/selftest_pump_oblique.py`. That is the contract's proof.
4. Run `selftest_hose_fittings.py`.

Both scripts are still DIRTY in `code_review_status`: no independent full-file review has been done.
