# Line joins review — pipes, hoses, reels, pumps, sprinklers, taps (2026-10-21)

Item: `LINE_JOINS_JUDGE_GPT_SEES_FIRST` (with `PIPE_GIRTH_TUNE_HALF_AS_THICK`, `HOSE_GIRTH_TUNE_MUCH_THINNER`).
Owner, 2026-10-21 ~21:02 PDT: *"sprinkler isn't centered on the pipe. And I'm sorry, but that pipe is crazy thick. Make the pipes half as thick. Flexible hoses need to be much thinner too. ..."*

Status: phases 1-4 done OFFLINE (no bridge). Sample images are REFERENCES for the redraw, not installs.

## Inputs

- 🔴 **Every `Transient/fw_hoses_walk/FlowWorks_HosePipeWalk_2026101[8-21]_*` file is a MOCK** (a flat green frame reading
  "MOCK SCREENSHOT …" — selftest output, ~140 colours), and so are `Transient/owner_review_stage/hoses_*`. No in-game close-up of
  tonight's joins exists on disk except the owner's own 4K screenshot. The real 2026-10-18 captures
  (`Transient/owner_review_20261018_2349/hoses_*`) are at far zoom on older art and show nothing at join scale.
- So the crops below come from `Transient/pile_2026-10-21/walk/pipes_sprinkler_2026-10-21.png` (3840x2160, game zoomed in).
  Measured there: **1 cell = 82 screen px** (pipe band period and the 1x2 battery agree); the pipe draws **24 px = 0.29 cell**
  thick (outline incl.); the hose ~0.45 cell.
- Installed art (deployed = repo, md5-checked for all four pipe atlases): pipe atlas 704x704 = 4x4 tiles of **176 px/cell**;
  straight-run girth **40 px of 176 = 0.23 cell** (rows 68-107 of the tile, centred), all four looks identical.
  `RM_SprinklerHead` 256x256 at drawSize 1 (Scrapper bbox 80-175 x 49-207: dome centred on the cell, stem foot 0.31 cell below).
  Hose visible width `HoseMath.FlatVisible 0.38` + `PlumpExtra 0.085` = **0.38-0.465 cell**, `WidthScale` 1 (setting floor 0.5).
  `RM_HoseReel` drawSize 2.8 on a 2x2, reel art bbox only 117x87 of 256 (= 1.28 x 0.95 cells drawn).
- Panel of crops: `line_joins/joins_panel_owner_screenshot.png` (A tank-pipe, B pump on pipe, C pipe end + sprinkler + hose start,
  D hose end / reel / pump, E pump with power cord, F pipe end cap / liquid tap / hose mouth, G reel row 2).
- True-scale sheet of current art, four looks, 64 px/cell with a vanilla pawn: `line_joins/current_truescale_64px.png`.
## Current art (offline, true scale)

`line_joins/current_truescale_64px.png` — all four looks at 64 px/cell. `line_joins/samples_vs_current_truescale.png` — the
Scrapper row against the three samples, all at 64 px/cell, with a vanilla pawn body. GPT's verbatim answer:
`line_joins/gpt_review_joins.md` (codex exec with the three images attached by `-i`; `gpt_consult.py` inlines text files only
and cannot attach images). Style reference fed to the image edits: `line_joins/style_ref_scrapper_current.png`.

GPT's girth targets (visible width, outline excluded):

| part | now | target (cells) | at 176 px/cell (pipe atlas) | at 256 px/cell |
|---|---|---|---|---|
| rigid pipe | 0.23 (40 px) | 0.12-0.14 | 21-25 px | 31-36 px |
| flexible hose | 0.38-0.465 | 0.08-0.10 | 14-18 px | 20-26 px |
| ordinary coupling / collar | (collars ~0.3) | 0.15-0.18 | 26-32 px | 38-46 px |
| outline | thick double black | 0.006-0.009 | 1-1.5 px | 1.5-2.3 px |
## Per-join: crop · GPT verdict · sample · redraw spec

Crops are in `line_joins/crop_<X>.png` (2x nearest from the owner's 4K frame); samples in `line_joins/sample_*.png`.

### 1. Pipe run and segment ends — crops B, F · sample 1, sample 3
- **GPT:** the pipe is 40-48% of a pawn's body width and over twice a vanilla conduit; heavy collars read as ducting; the end cap
  (F) is an oversized projecting dome.
- **Sample:** `sample_1_pipe_run_half_girth.png` (pipe ~0.17 cell, slim collars, flat cap plate) and `sample_3_pump_tap_handoff.png`.
- **Spec (`PIPE_GIRTH_TUNE_HALF_AS_THICK`):** redraw all 16 tiles of `Textures/RimMandrake/FlowWorks/Pipe/<Look>/UniversalPipe_Atlas.png`
  (704x704, 176 px/cell; 4 looks) with the straight girth **40 -> 20-22 px**, centred on tile row/col 88 (rows 77-98). Collars
  <= 28 px across; junction box (today ~72 px) -> ~40 px; end cap a flat plate <= 28 px across projecting <= 5 px past the run's end
  (no dome). Bends keep the same 20-22 px bore. `damageData rect (0,0.35,1,0.3)` -> `(0,0.44,1,0.12)` in
  `Defs/Machinery/RM_UniversalPipeStyles.xml` (4 styles) and `RM_LiquidLogistics.xml`. Menu icons too. The pipe centre-stubs under
  tanks/machines (`Source/Machinery/RM_LiquidJoins.cs` ~l.244, `SectionLayer_RM_PipeCentreStubs`) sample the atlas straight tile,
  so they thin with it — no code. Re-run the seam checker in `art_source/pipe/`.

### 2. Pipe-to-hose handoff — crops C, D · sample 3 (right end)
- **GPT:** the brown stubs read as torn cloth leaving metal; in C the hose's binding + backward brass nozzle sits after a gap; in D
  the stub enters the pump with no fitting; the cloth is wider than the pipe.
- **What the stub is:** `RM_MapComponent_Hoses.DrawPortStub` (PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE) draws the hose ribbon from the
  shared edge to the building's centre, below the building layer — on a pipe-end/pump cell it shows as a cloth tongue.
- **Spec:** one compact metal reducer, 0.16-0.18 cell wide x 0.12-0.16 long, bore on the pipe axis, midpoint on the shared cell
  edge (+-0.5 cell from either centre); hose inserted with 0.02-cell hidden overlap; remove the gap and the backward-facing nozzle
  at a coupled end. With the hose at 0.09-0.11 the ribbon stub shrinks automatically (width from `VisibleWidth`).

### 3. Hose girth and hose-to-reel — crops C, D, G · sample 2
- **GPT:** hose endpoint loose beside an isolated reel; the reel is a side-elevation drum, small, on a dark square — "an inventory
  object pasted on the ground"; 2.8-cell draw conflicts with its 2x2 footprint.
- **Sample:** `sample_2_hose_reel_thin.png` (spool with both flanges, wound wraps on the lit top, crank, iron frame; one thin
  continuous hose to a brass coupling on a pipe stub; hose ~0.12 cell).
- **Spec (`HOSE_GIRTH_TUNE_MUCH_THINNER`):** `Source/Hose/HoseMath.cs` `FlatVisible 0.38 -> 0.09`, `PlumpExtra 0.085 -> 0.025`
  (plump 0.115 at amount 1). The `thickness` Mod Setting cannot get there (`ApplyThickness` clamps `WidthScale` to 0.5-1, i.e.
  >= 0.19 cell). Every fitting (`FittingSize`, `WrapWidth` = 1.3 x visible, `JoinerHalf`, `NozzleSeat`) scales off the visible width,
  so couplings/bindings follow; re-check `Binding.png`/`Coupling_*` stay legible at ~20 px. Strand strips already fill their band.
  `LiquidJoinRule.ProposedHoseThickness 0.65` is superseded by this ruling. Hose selftests that pin widths need new numbers.
- **Reel:** redraw `Hose/Reel_PumpHookup.png` + `Reel_Deployed.png` (Scrapper root + `Styles/<Industrial|Modern|Futuristic>/`),
  256 px at drawSize 2.8: art today fills only 117x87 px (1.28 x 0.95 cells). Target 1.6-1.8 cells wide (~150-165 px), drawn from
  the building camera (lit top, short south face, flanges as ellipses), wound hose at the new girth, a defined ground-level exit
  port (e.g. (-0.75, 0) cell for a west exit; geometry in `Source/Hose/ReelIntakeGeometry.cs`). Shrink `shadowData volume
  (1.6,0.35,1.35)` (RM_HoseReel.xml, RM_HoseReelStyles.xml) to the frame's real base — it is the dark square behind the reel.

### 4. Pump on pipe / reel-to-pump — crops B, D, E, G · sample 3 (cell 3)
- **GPT:** the pump's broad flanges overwhelm the pipe; at normal zoom bolts and rings merge into a dark lump; no readable port for
  the reel's line.
- **Spec:** `Things/Building/FlowWorks/Machinery/RM_LiquidPump.png` (512, drawSize 1): body 0.65-0.75 cell, port mouths at
  (+-0.5, 0) and (0, +-0.5) tapered to 0.16-0.18-cell couplings sized to the NEW pipe bore; one housing, fewer bolts.

### 5. Sprinkler head on pipe — crop C · sample 1 (cell 4)
- **GPT:** reads as standing beside/above the pipe; the image's visual centre is the dome, not the pipe connection; too big.
- **Measured:** `Sprinkler/<Look>/RM_SprinklerHead.png` 256 at drawSize 1 with no `drawOffset`: the dome is at the cell centre
  and the stem's foot sits **0.29-0.34 cell south** of it (Scrapper foot y=207/256, Industrial 204, Modern 214, Futuristic 203) —
  that is the "not centred on the pipe".
- **Quick fix (no art):** `<drawOffset>(0,0,0.31)</drawOffset>` on `RM_SprinklerHead`'s graphicData and its four
  `RM_SprinklerHead_<Look>` ThingStyleDefs (`Defs/Sprinklers/RM_Sprinklers.xml`) puts the foot on the pipe axis.
- **Redraw:** riser foot exactly at texture (128,128) with a saddle clamp ~0.15 cell around the pipe; dome 0.20-0.24 cell
  (51-61 px at 256), stem 0.06-0.08 cell; dome may stand 0.06-0.10 cell north of the foot.

### 6. Liquid tap and hose mouth — crop F · sample 3 (cell 6)
- **GPT:** three disconnected objects; the tap + bucket is a side elevation; the open black hose mouth reads as a tunnel.
- **Note:** `RM_LiquidTap` is the well-tap building (Defs/Drilling, `Things/Building/FlowWorks/Machinery/RM_LiquidTap.png`), not
  a pipe fitting. Spec: top-visible valve assembly, manifold at (0,0), hose port at (+0.25,0) rotating with it, bucket shrunk or
  gone; an open mouth only on a genuinely free hose end, as a shallow ellipse the size of the new hose bore (`Hose/Mouth.png`).

### 7. Tank to pipe — crop A
- **GPT:** pipe emerges from behind the tank's skid with no outlet. Spec: short outlet neck + 0.18-cell coupling on the pipe axis
  at the tank's connection edge, 0.02-cell overlap; supports clear of the outlet. (Tank art: `Tank/<Look>/RM_LiquidTank*.png`.)

### GPT's ranked changes
1. Halve rigid-pipe girth and thin hoses. 2. One connection anchor rule; no gaps or cloth stubs. 3. Redraw and resize reels.
4. Replace bulbous caps and oversized fittings. 5. Fix sprinkler/tap perspective; simplify small detail.
## Redraw spec summary (defs / texPaths / offsets)

| change | file(s) | kind |
|---|---|---|
| pipe girth 40 -> 20-22 px, collars <= 28, flat caps, junction ~40 px | `Textures/RimMandrake/FlowWorks/Pipe/{Scrapper,Industrial,Modern,Futuristic}/UniversalPipe_Atlas.png` + `_MenuIcon` | art (art ledger) |
| pipe damage rect | `Defs/Machinery/RM_UniversalPipeStyles.xml`, `RM_LiquidLogistics.xml` | XML |
| hose visible width 0.38/0.085 -> 0.09/0.025 | `Source/Hose/HoseMath.cs` (`FlatVisible`, `PlumpExtra`) | C# + selftests |
| sprinkler foot on pipe | `Defs/Sprinklers/RM_Sprinklers.xml` drawOffset (0,0,0.31) now; redraw `Sprinkler/<Look>/RM_SprinklerHead.png` later | XML / art |
| reel reads as a reel, 1.6-1.8 cells, real exit port | `Hose/Reel_PumpHookup.png`, `Reel_Deployed.png` (+3 Styles); shadowData in `Defs/Hose/RM_HoseReel*.xml`; `ReelIntakeGeometry.cs` | art + XML |
| pipe->hose reducer instead of cloth stub | `RM_MapComponent_Hoses.DrawPortStub`, `Hose/Coupling_*.png` | C# + art |
| pump ports sized to new bore | `Things/Building/FlowWorks/Machinery/RM_LiquidPump.png` | art |
| tap top-visible | `Things/Building/FlowWorks/Machinery/RM_LiquidTap.png` | art |

Nothing here was installed; `Textures/`, the art ledger and source are untouched.
## Live close-ups still needed

🔴 Take them with a REAL capture (`system_screenshot.py` or the bridge's screenshot), not `validation_hose`'s walk: its
`FlowWorks_HosePipeWalk_*` frames are mocks. Zoom so **1 cell = 80-100 screen px** (as in the owner's frame), dev-mode spawn,
daylight, no selection box; crop to ~6x4 cells around the subject.
1. Sprinkler head on a MID-run pipe cell (not the end), all four looks side by side.
2. Pipe end caps facing E, W, N, S; an L-bend, a T and a 4-way on one run (Scrapper + one other look).
3. A hose coupled to a pipe END (pipe -> hose port), hose flat AND plump (dev "flow through hose").
4. A hose coupled to a tank side and to a pump side (the cloth centre-stub cases).
5. Each look's 2x2 hose reel with its hose laid 5 cells east, reel centred in frame.
6. Pump with pipes on all four sides; pump with a reel hose on one side.
7. `RM_LiquidTap` beside a pipe end and a free hose mouth.
8. One pipe run beside a vanilla power conduit with a colonist standing on it (scale).
