# FlowWorks + GSS art: GPT art review, verified (BENCH, 2026-10-24)

Owner, 2026-10-23 ~22:35: *"Put all of the FlowWorks art on a single massive review sheet with context, descriptions as
well as the codebase and intended interactions and validation methods and plans and sent it all to GPT for art review,
recommendations, etc. Make sure it's all scaled to each other to a normal human..."*

No art was regenerated or installed. No game, bridge or deploy was used. Every GPT claim below was checked against the
pictures (and against the drawing code where scale was in doubt) before it was kept.

## What was sent

- **Sheet** (415 rows, 11 families, true scale beside a vanilla human, gate PASS, pre-reviewed 341 OK / 74 FLAG):
  `\\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\biome_ffar\flowworks_gpt_art_review_sheet_2026-10-23.html`
  (snapshot `D:\Luke\dev\RimMandrake\infrastructure\state\art\sheets\flowworks_gpt_art_review_sheet_2026-10-23.snapshot.json`).
  The Scrapper pipe atlas was captured at blob `e0f0249673529672c1f4163b60dd6d1389597fdd`. A peer is redrawing it, so the
  Scrapper PipeSpan row may already be out of date.
- **GPT panels** (31; per family, one detail panel and one true-scale panel with a human):
  `D:\ClaudeWork\rimmandrake\scratch\gpt_art_review\panels\` (`index.json` maps panel to rows).
- **In-game context pages** (17: bridge-run captures plus the owner's 2026-10-23 screenshots):
  `D:\ClaudeWork\rimmandrake\scratch\gpt_art_review\context\`.
- **Dossier** (owner request, owner art principles, art judge brief, 127 needs-eyes feature rows, PLAN H / PLAN N,
  BRIDGE_RUN_1, hose doc, code paths): `D:\ClaudeWork\rimmandrake\scratch\gpt_art_review\dossier\`.
- **Raw GPT replies**, in three groups: A = pipes, fittings, sprinklers, tanks, pumps and works, hoses; B = rivers, pits,
  bridges, liquids, containers; C = GSS cords and aerial lines, dev props, other.
  `D:\ClaudeWork\rimmandrake\scratch\gpt_art_review\raw\{A,B,C}.md`

## Confirmed findings (filed)

| item | sev | what |
|---|---|---|
| `PIPE_POLE_REDRAW_NOT_A_POWER_POLE` | major | Pipe poles use the GSS AerialMast power-pole art (RM_PipePoles.xml:47), insulators included. |
| `LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB` | major | The pump and every PumpLook are drawn as a face-on plan-view medallion, next to tanks drawn oblique. |
| `DETOX_WORKS_REDRAW_SAME_PLANT_EACH_STAGE` | minor | The Kludged stage has a different plant layout from Repaired and Wrecked. |
| `SPRINKLER_SEAT_FIX_HEAD_BESIDE_ELBOW` | minor | In game the sprinkler head sits beside the elbow, not on the pipe (owner screenshot 221805). |
| `SILT_TRAP_STYLES_REDRAW_HALF_RES_FLAT` | minor | The styled silt traps are 107 ppc frontal panels; the base trap is 213 ppc and oblique. |
| `GSS_JUNCTION_REDRAW_BODY_WIDER_THAN_CORD` | minor | The Modern and Futuristic T/X junctions are about 1.15 cells wide, and their sleeves are much wider than the 0.08-cell cord. |
| `PIT_LIP_OCCLUDER_FIX_GHOSTED_HALVES` | minor, live | The lip cover runs past the pit edge and ghosts a pawn outside the pit. The occupant window was not seen (the setting may have been off). |
| `FW_ART_POLISH_REDRAW_FOUR_SMALL_MISSES` | minor | Four small misses: the Char0 scorch keyline, a baked shadow on the station sign, weir-spill strips that do not read as falling water, and a photoreal FreshWater bottle. |
| `GSS_ART_MANIFEST_FIX_OVERLAY_SIZES` | tooling | The review manifest draws mast tops at [2,4] where the code draws 2x1, and draws hose Mouth/Binding as 1.52 squares where the code draws an edge-on lip and len x width. This sheet shows them at the wrong scale. |

Duplicates of open items (cited, not re-filed):
- Reels drawn in side elevation: `REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON`.
- Two hoses on one relay-reel coupling (owner screenshot 221228): `HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS`.
- Modern pump, containers and joins in the same red gloss: `MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY`.

## Rejected GPT claims (and why)

- **Hose Mouth "oversized bore" (A rank 1) and Binding "squashed square" (A rank 4):** the sheet was wrong, not the art.
  The code draws the Mouth edge-on as a lip and the Binding as len x WrapWidth (RM_MapComponent_Hoses.cs:1167-1172, :1616).
  Filed as the manifest bug.
- **Mast-top overlays "stretched":** the same manifest bug. The code draws them 2x1 (RM_MapComponent_Aerial.cs:535).
- **Drawbridge winch "uses suspension-anchor art":** the def XML says so, but RM_DrawbridgeArt.cs:175-176 swaps in the winch art at 1.5x1.5.
- **Styled aerial wall brackets "tiny" (C rank 1):** the panel showed the south facing of a Graphic_Multi. The bracket is in scale.
- **SiltWedge "dirt heap" (B rank 6):** it is a flat plan-view wedge. GPT called this a preference, and it breaks no rule.
- **WaterThin / WaterVeryShallow "look like dirt" (B rank 2):** this depends on the shader and cannot be judged from a flat
  PNG. It needs a live look (H1-10), not a redraw.
- **Ladders:** a peer helper is redrawing them now from the owner's cards of 2026-10-23.
- **RM_FlowSource stand-in (C rank 3):** a dev-only prop.
- **"Facing not visible" gaps across families:** these are gaps in what the sheet showed, not defects. The validation
  recommendations below cover them.

## Ranked redraw list (confirmed only)

1. `LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB`: the most-seen FlowWorks building, and the camera is wrong. Do it together with
   `MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY`. Keep the four port necks registered within 0.02 cell.
2. `PIPE_POLE_REDRAW_NOT_A_POWER_POLE`: every pipe line on poles reads as a power line. Four looks, each with a saddle clamp at the PipeSpan seat height.
3. `REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON`: existing item, reconfirmed by GPT.
4. `SILT_TRAP_STYLES_REDRAW_HALF_RES_FLAT`: four looks, at the base trap's resolution and camera.
5. `GSS_JUNCTION_REDRAW_BODY_WIDER_THAN_CORD`: smaller housing, with necks within 20% of the strand width.
6. `FW_ART_POLISH_REDRAW_FOUR_SMALL_MISSES`: weir spill first, then the bottle, scorch and sign.
7. `DETOX_WORKS_REDRAW_SAME_PLANT_EACH_STAGE`: one layout across the three stages.

Fix the sprinkler seat and the pit-lip cover before or alongside the art (code or compositing). Fix the manifest before the next
review sheet, or that sheet will show the same false shapes again.

## Validation recommendations (GPT, filtered)

- **Scale instruments:** measure ppc per axis (X and Y separately) and flag anisotropy. Make the manifest sizes come from
  the drawing code, never a hand table (this round's two false findings came from such a table).
- **Linked atlases:** check that the edge-alpha centrelines match across all 16 masks. Set mating-diameter bands: hose,
  collar and mouth within 10%; cord neck within 20% of the strand.
- **Machines with ports:** port registration within 0.02 cell. Build a reel census of look x state x facing.
- **Composites:** at 32, 80 and 160 ppc on varied grounds (soil, sand, ice, floor); each mast overlay on its mast; on/off switch registration; strand repeat seams.
- **Live checks** in PLAN H1: 03 (pit-lip clipping), 04/05 (ladder banks and walkers), 06/07, 08 (containers in every fill
  state), 10 (water motion, weir spill, wedge, ferry ends), 11-13, 16.
- **Plan gap:** neither plan has a per-asset art check for the ridge, weir, wedge, winch, guardrail, scorch, junctions or
  mast heads. PLAN N O6/O8 is the right place for them.
