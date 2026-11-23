# PumpOblique — LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB

The four RM_LiquidPump looks redrawn from plan-view medallions to the oblique building camera.

- `plan/` holds a copy of the 2026-10-23 installed plan art: the parts reference, and the revert.
- `oblique_pump.py` is the 2026-11-05 attempt. It squashes the flat plan picture, adds a synthetic wall and pastes the
  flat pipe arms back. The owner rejected its output on 2026-11-23 ("the rest of the graphics have just been crudely
  distorted to match it. Entirely wrong."). Do not install its output.
- `v2/` is the 2026-11-23 redraw, generated from a true 3D model:
  - `blockout.py <out.png> [flange_radius] [neck_radius]` raymarches the grey 3D pump under the building camera. Modern
    uses 56 38; the other looks use the defaults.
  - `render.py <Look> <blockout.png> <out.png>` holds the prompt and makes one codex edit: image 1 the blockout, image 2
    the look's tank, image 3 the plan pump.
  - `finish.py <raw.png> <out.png> [scale]` makes the 512 px sprite. Industrial used scale 0.985.
  - `sheet.py <showing dir> <dated dir> <out.png>` builds the owner's pick sheet.
- `check_oblique.py [--dir D]` reads ports and an oblique clause. Each port must be centred on its edge centre within
  0.02 cell, with its face within 0.10 cell of the edge. Trust the port clause only. The oblique clause is a brightness
  ratio: it passed all four rejected candidates, and it fails the white Futuristic v2, which an independent judge kept.

Measured 2026-11-23, v2 round 1: `validate_sprite.py` passes all four; 16 of 16 ports pass. An independent GPT judge kept
all four.

## Candidates

`D:\ClaudeWork\rimmandrake\showings\LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB\2026-11-23_true_oblique\` holds the candidates,
raw renders, exact prompts, GPT's advice, the judge's answer and `pump_pick_sheet.png`.

## Blocked: owner-kept art

All four installed looks are owner-KEPT pictures (960ddf23f012, ea7ddc15b970, 87725568582f, afffd14b1d58), so
`art.py install --why` refuses. Replacing kept art is his call (delegation_policy.md §2.2).

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
3. Promote only the port clause of `check_oblique.py` to `src/RimMandrake/FlowWorks/selftest_pump_oblique.py`.
4. Run `selftest_hose_fittings.py`.

