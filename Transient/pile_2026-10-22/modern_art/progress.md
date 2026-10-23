# Modern FlowWorks art — progress (BENCH helper, 2026-10-22)

## 1. Item filed
`MODERN_TANK_REDRAW_NOT_JUST_RED_PAINT` (owner's words via --owner-said; ledger event rode in dac298d0c1, item prose
f1c25b3a03, pushed with 2ef76419c3).

## 2. Modern variants found (defs, texPaths, facings)
| def / slot | texture (under src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/) | footprint · drawSize · canvas | facings |
|---|---|---|---|
| RM_LiquidTank_Modern | Tank/Modern/RM_LiquidTank | 2×2 · 2×2 · 512² | Graphic_Single |
| RM_LiquidTankTall_Modern | Tank/Modern/RM_LiquidTankTall | 2×2 · 2×3 +0.5N · 512×768 | Graphic_Single |
| RM_UniversalCargoTank_Modern | Tank/Modern/RM_UniversalCargoTank | 2×2 · 2×2 · 512² | Graphic_Single |
| RM_UniversalCargoTankXTall_Modern | Tank/Modern/RM_UniversalCargoTankXTall | 2×2 · 2×4 +1N · 512×1024 | Graphic_Single |
| RM_HoseReel_Modern | Hose/Styles/Modern/Reel_{PumpHookup,Deployed}{,_north,_south} | 2×2 · 2.15 · 256² | west picture (east mirrors), north, south; stored + laid-out states |
| pump (style) | Pump/Modern/RM_LiquidPump | 512² | single — same red-repaint problem, NOT redrawn here |
| sprinkler | Sprinkler/Modern/RM_SprinklerHead | — | not redrawn |
| containers | Things/Item/Resource/FlowWorks/Modern/RM_{Barrel,Bottle,Bucket}(+_m) | — | not redrawn |
| hose ends | Hose/Styles/Modern/{Coupling_Bare,EndCap_Bare,Nozzle_Bare,Mouth,Binding,Strand_Flat,Strand_Plump} | — | not redrawn |
| joins | Joins/Modern/{Coupler,Flange,Saddle} | — | not redrawn |
(Non-liquid Modern sets also exist: Pipe, PipePole, Weir, Drawbridge, SuspensionBridge.)

## 3. Web research (sources)
18 numbered references (≈25 URLs) in `design/RimMandrake/flowworks_modern_art_brief.md` (2ef76419c3).

## 4. Drafts generated
Codex $imagegen, raw renders in `D:\ClaudeWork\rimmandrake\modern_art\raw`; fitted onto each def's canvas (contain
inside the shape master's width, standing on its ground line) in `drafts/`.
- Tanks: 4 buildings × 3 options = 12 (`drafts/RM_<Tank>_Modern_{A,B,C}.png`).
  - short: A white poly leg tank · B light-blue heavy-duty leg tank · C blue-steel pressure tank on cradle
  - tall: A black vertical poly tank · B green vertical poly tank · C slate-grey slimline rain tank
  - cargo: A IBC tote (black plastic pallet) · B IBC tote (galvanised pallet) · C squat natural poly tank with straps
  - extra-tall: A natural translucent poly tank · B stainless vertical tank on legs · C black vertical poly tank
- Reels: 3 options × 6 pictures = 18 (`drafts/Reel_{PumpHookup,Deployed}{,_north,_south}_{A,B,C}.png`):
  A resin cart (taupe, green hose) · B enclosed box reel (slate grey) · C stainless spring reel (black hose)

## 5. Judge pass verdicts (self-judge against art_judge_brief.md + brief M1–M4; the seat runs the independent judge)
| picture | verdict | notes |
|---|---|---|
| LiquidTank A/B/C | KEEP | M1–M4 yes; real product classes. C3: drawn near side-on (little top face) — same as the kept Scrapper master; advisory |
| LiquidTankTall A | KEEP | M1–M4 yes. C3 UNSURE: top ellipse looks ~0.35, below 0.48–0.64 (validator found no reliable fit) |
| LiquidTankTall B | KEEP | as A; validator fit 0.82 unreliable (rms 3.7) |
| LiquidTankTall C v1 | REDO → done | C3 violated: side elevation, top rim 0.26, no top face. Re-edited from a higher camera; v2 shows the lit top with the strainer — KEEP |
| UniversalCargoTank A/B | KEEP | IBC tote reads instantly; fills the 2×2 canvas in depth (inside the footprint since drawSize = size) |
| UniversalCargoTank C | KEEP | |
| UniversalCargoTankXTall A | KEEP | C3 advisory (0.35, unreliable fit) |
| UniversalCargoTankXTall B/C | KEEP | B 0.53 ✓; C 0.66 borderline |
| Reel A (6) | KEEP | facings agree; laid-out drum empty with leader stub |
| Reel B (6) | KEEP | enclosed: laid-out differs from stored only by the slot/stub — honest for this product class |
| Reel C south v1 | REDO → done | C2: a crank appeared that the west picture does not have. Regenerated without crank — KEEP |
| Reel C (others) | KEEP | |
| D-family | note | validate_sprite reference-vs-candidate REJECTs span/aspect/origin on every tank: expected for a restyle (skill: wrong check for a new product class). Reference-independent checks: real alpha, clean corners, ≥2 px top pad, base on the master's ground line |
| E3 | note | these replace art he kept → no install; his pick decides |

Dropped before the collection (owner rule 2026-10-22, look at every image): LiquidTankTall C v1 (side-on), Reel C south
v1 (phantom crank), and the first fit of every reel Deployed north/south (fitted into the OLD laid-out bbox, which is
smaller than the stored one, so the reel visibly shrank when the hose ran out — refitted to the stored bbox).
All 38 phone images were Read (option sheets, facings sheets, montages of every full-res and scale image): none broken.

## 6. Collections (phone, ≤1600 px wide)
`Transient/pile_2026-10-22/modern_art/phone/`, per building `<Def>_0_options.png` (current red beside A/B/C), then per
option `_1_full.png` (full-res alone on checkerboard), `_2_scale.png` (true scale beside the vanilla composed human,
scale_panel.py, + 32 px/cell), reels also `_3_facings.png` (stored and laid-out, west/north/south).

## 7. Findings filed
- Item `MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY` — the Modern pump (and sprinkler/containers/hose ends/joins) are the
  same red repaint.
- Lesson: stale `~/.codex_sandbox_seed` breaks every isolated `--codex-home` worker; fix by copying the shared home's
  three sandbox dirs (the tool's own message).
- Lesson: when redrawing reel art, fit the laid-out (Deployed) pictures to the STORED picture's bbox per facing; the old
  Modern Deployed north/south were smaller, so the reel shrank on deploy.

## Install notes (for after his pick)
Copy picks to `Tank/Modern/` and `Hose/Styles/Modern/`, then re-run
`src/RimMandrake/Utils/mockups/messy_conduit/reel_intake_geometry.py` (regenerates `Source/Hose/ReelIntakeGeometry.cs`
from the art), rebuild, deploy.

## Shas
f1c25b3a03 (item) · 2ef76419c3 (brief) · 50733d22fb (drafts, phone collections, pump item, 2 lessons). DONE.

## 8. Seat pre-review + naive judge fixes (2026-10-22, later)
- Defect the seat caught: the four tank `_0_options.png` sheets showed only the current red art. Cause: the reel-only
  re-run of `build_phone.py` (keep = reels) still walked the tank loop with zero options and overwrote the tank option
  sheets AFTER I had looked at them. Fixed (loop skips buildings with no kept options); all four rebuilt and re-read.
- Naive judge: best picks reel A, LiquidTankTall B, UniversalCargoTank B, XTall A. Dropped short C (pressure tank reads as
  plumbing gear), Cargo C (≈ short A) and XTall C (≈ Tall A) from drafts and phone.
- Short A and B redrawn twice with a raised camera (v3, axis-aligned): A now shows a lit top with the lid as an
  ellipse; B is axis-aligned but its top face is still weak (the generator resists a high angle on horizontal drums) —
  flagged, not hidden. v1/v2 raws kept in D:\ClaudeWork\rimmandrake\modern_art\raw.

## 9. Owner picks installed + fire hose reels (2026-10-22, later)
- Owner by card: short A white leg tank, tall B green poly, cargo B IBC steel, extra-tall A white poly → installed with
  `art.py install` (--owner-said carries the card label; art.py has no --by-card), fb34c9bc2d. Selftests looks_round +
  liquid_look_tune GREEN; tanks are Graphic_Single, no geometry tool reads them. Not deployed.
- Reel: none picked; owner "Try looking up firehose reel". Brief gained a fire-hose-reel section (12 sources F1–F12).
- Fire reel drafts (`drafts/Reel_{PumpHookup,Deployed}{,_north,_south}_F{A,B,C}.png`): FA swinging pedestal fire reel
  (EN 671 style, red drum, handwheel stop valve), FB stainless fire-reel cabinet with glass door, FC Hannay-style red
  booster reel with bevel-gear crank and brass swivel.
- Self-judge: REDO and regenerated — FA stored south, FA laid-out north/south, FC laid-out north/south (the generator
  turned the drum axis left-right, unlike the stored views); laid-out views were then drawn by emptying the matching
  stored picture. KEEP all 18 now. Notes: FA laid-out west shows a steel-grey core where N/S show red (minor); FB's
  turned views vary a little in cabinet proportion. Codex returned the three west masters as OPAQUE RGB on black despite
  the prompt; cut by border flood fill (rembg was OOM-killed, rc 137).
- Phone: garden-reel A/B/C images removed from phone/ (drafts kept); `RM_HoseReel_0_options.png` = current + FA/FB/FC;
  per option full, true-scale, facings. All re-Read after the final build; tank option sheets verified intact (1596–1600 px).
