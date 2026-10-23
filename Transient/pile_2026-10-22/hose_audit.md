# Hose / reel / connector audit — save RM_fw_walkthrough_20261022b (2026-10-22)

BENCH helper, evening of 2026-10-22, live on the game the owner had just walked (mod list fw_gss_sitting, both maps,
game paused at tick 145425, nothing saved). Captures: `Transient/pile_2026-10-22/hose_audit/` (C## = map C, R## = map R,
E## = experiment). Phone sheet of the worst eight: `Transient/pile_2026-10-22/hose_audit/phone_defects.png`.
Live state reads: `hose_audit/census_mapC.json`, `census_mapR.json` (HoseProbe `census`), `things_C3north.txt`.
Tools: `hose_audit/ha.py` (bridge: census, things, shoot), `crop.py` (screenshot -> cell-gridded crop), `phone.py`.

## 1. Owner's words and items filed

Owner, 2026-10-22, verbatim: *"So the reels on the lower left of the map (screenshot) obvious problems, I thought you were
going to check connections? (2nd screenshot) This one has obvious problems everywhre, you obviously didn't check any graphics
for connectors. Do we need to give up on this and just have hoses go under like pipes? I'm beginning to think so. And the hose
is going under the battery and wall... we used to be better than this. ... I can't even tell what's going on here with the
connnectors. Just look at them! Obviously not even checked before showing us."*

Filed first (ledger, 972f60301a): `HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES`, `HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS`,
`HOSE_LOOK_DECIDE_OVERGROUND_OR_UNDERPIPE` (his call). Later findings: §6.

## 2. What his screenshots show

His four shots (`Transient/pile_2026-10-22/walk_owner_shots/`), each matched to the live census:

| shot | where | what he saw | live cause |
|---|---|---|---|
| 20261022184157 | map C, C3 reel park (reels at x13-14, z15-34) | every laid hose leaves the reel westward, swings a big U-turn and runs back east past the reel to its free end; the collar beside each nozzle does not touch it | reels staged facing West with their free ends 6 cells EAST; the straight lead-out rule makes the hose leave by the nozzle first (SITE + design rule); collar gap (ART/offset) |
| 20261022184237 | map C, C3 north, reel o1 (19,42) beside pump (17,42), pipe (17,43), tank (17,44), battery (18,39) | hose loops through the pond, runs under the power connector and the yellow battery and through the wall; a tan collar stub on the pump; a brown stub crossing the pipe sideways; green cords under the battery | see D1-D4 below |
| 20261022184620 / 184658 | map C, C7 "one hose net, no pump" (reels (24,127), (24,134)) | a vertical "hose" between two red reels with tan pieces that do not meet them | the vertical line is a PIPE (RM_UniversalPipe x23 z129-133); the tan pieces are the hose-port sleeves drawn on the pipe's ends; they stop short of the reels and the reels have no inlet on that side (D6) |

## 3. Live audit — every joint, both maps

Inventory (census): map C 18 reels (13 laid, 5 stored), map R 2 reels (both laid). Every reel, every hose end, every
hose-to-pipe/pump/tank coupling and the pipe joints beside them were captured at the game's closest zoom (114 px/cell;
the camera clamps rootSize at 8). Cell-coordinate ticks are on the top and left edge of each crop.

| # | defect (plain words) | instances (reel / place) | capture | class |
|---|---|---|---|---|
| D1 | Hose drawn straight **through a wall**: reel o1's laid hose crosses wall cells (22,39)/(22,40). A fresh re-lay (E01, shape setting nudged and restored) draws it through the same wall, so it is the planner, not a stale lay | 41679 | `C09_C3n_battery_wall.jpg`, `C3north_overview.jpg`, `E01_relay_C3north.jpg` | CODE |
| D2 | Hose drawn **under buildings**: under the pump body (17,42), the power connector and the battery (18,39-40). A battery is PassThroughOnly, so the hose world prices it like bare ground, and the hose draws below every building | 41679 (3 buildings) | `C08_C3n_junction.jpg`, `C09_C3n_battery_wall.jpg` | CODE + SITE |
| D3 | **Two hoses from one nozzle**: reel o1 is port-coupled to the pump (tan collar stub on the pump's east flange, a gap from the nozzle) AND laid out free from the same nozzle, the laid hose leaving westward from under the pump | 41679 | `C08_C3n_junction.jpg` | CODE |
| D4 | **Stray pipe stub** drawn sideways across the vertical pipe just under the tank (x17.5-18.3, z44.3), ending in air | tank (17,44) | `C08_C3n_junction.jpg` | CODE |
| D5 | **Pump-to-reel stub floats** between the pump's west flange and the reel's crank; the reel has no inlet on that side | 42229 (C4) | `C17_C4_pump_reel.jpg` | CODE (+ART: no rear inlet drawn) |
| D6 | **Pipe-end hose sleeves stop short** of both reels (~0.4-0.6 cell) and point at the reel's top/bottom, where it has no inlet; a loose pipe end-cap square floats between the lower sleeve and its reel (23,128.5) | 42334, 42335 (C7) | `C26_C7_vertical.jpg`, `C24_C7_reel127.jpg`, `C25_C7_reel134.jpg` | CODE + SITE |
| D7 | **Tank-to-reel stub** rises from the tank's top edge to the reel's base, not to a port on the reel | 42490 | `C33_X_reel237.jpg` | CODE |
| D8 | **Hose end stops ~0.4 cell short of the tank flange**, with a small upward kink just before it | 42273 (C5), 42490 far end | `C21_C5_tank_end.jpg`, `C33_X_reel237.jpg` | CODE |
| D9 | **Collar floats off the nozzle**: on every laid reel the hose's first collar ends ~0.1-0.3 cell before the brass nozzle tip (worst Scrapper/Industrial, least Modern) | all 15 laid reels | `C02_C3park_r41683.jpg`, `C03_…r41684`, `C04_…r41685`, `C13_C3drop_reel.jpg`, `C20_C5_reel.jpg`, `R04_R_reel182.jpg` | ART or CODE offset (undetermined: coupling sprite padding vs start point) |
| D10 | **U-turn loop**: the free end is behind the reel, so the hose leaves the west nozzle and swings round 180° past the reel | 41679, 41683, 41684, 41685, 41687, 41688, 42273, 42433, 382378, 382379 (10) | `C04_C3park_r41685.jpg`, `C15_C3drop_overview.jpg`, `C29_C7_tower_reel.jpg`, `R01_R_overview.jpg` | SITE (every staged reel built rot 3 = West although reels turn since 73b8805755) + rule (straight lead-out, owner card 2026-10-06) |
| D11 | Two laid hoses **cross flat**, one painted over the other with no lift or shadow | 382378 x 382379 (map R) | `R01_R_overview.jpg` | CODE (minor) |
| D12 | Green GSS power cords from the connector run **under the battery** | C3 north, C4 | `C08_C3n_junction.jpg`, `C17_C4_pump_reel.jpg` | CODE/SITE (GSS, not hose) |

Clean (looked at, no defect): free ends lying free (C11 Hobb, C14, C27, C28, C31, R03, R05), the hose down the C4 ramp into
the drain canal (C19), the stored/wound reels (C05, C12), the three turned reels N/E/S (C16: art as installed today), the
hose under the tall power-pole picture (C10: the pole's art overlaps, the hose does not cross its cell).

**Counts: 12 defect kinds, 39 instances — CODE 13 (D1-D8, D11, D12), ART/offset 15 (D9), SITE 11 (D10 x10, D6 placement).**
(The C7 sleeves count once under CODE; D2's SITE share is the same hose as D1.)

## 4. Why hoses route under buildings and walls (and the regression)

**Through the wall (D1) — a hole in the wall test, measured.** `HoseMath.Clear` (FlowWorks `Source/Hose/HoseMath.cs` ~l.762)
walks the centreline at 0.05 cell and refuses a sample whose `WallDepth` exceeds `ClipTolerance = 0.06`. `WallDepth` (l.748)
is the distance from the sample to the nearest edge **of its own cell**, whatever lies across that edge. A hose lying on the
seam between two wall cells — here z = 40.0, between walls (22,39) and (22,40) — reads depth ~0 in both and passes as clear.
`SegmentClear` (string-pulling in `RoutePulled`) and every shaping stage (`LayOnce`, lead-out joins) use the same test, so the
whole lay is accepted. Evidence: the hose's centreline sits on the z=40 grid line in both crops; `check:19,42,35,27` returns
no reason; a forced fresh re-lay (E01) draws the identical pose (len 35.79 vs 35.77) through the same wall. The real route
exists through the wall gap at (22,42)-(22,43), two cells north. Fix: depth must be measured to the nearest WALKABLE cell
(or a seam between two blocked cells counts as blocked). Filed `HOSE_CLEAR_FIX_WALL_SEAM_LOOPHOLE`.

**Under the battery/connector/pump (D2).** `RM_MapComponent_Hoses.World()` (l.104-130) marks any path-walkable cell as free;
only reels and pumps cost extra (`CostsAsBuilding`, 86e8a90bfe 2026-10-20). A battery and a power connector are walk-over
(PassThroughOnly), so the hose prices them as ground; the hose mesh draws below buildings, so it vanishes under them. Why it
went there at all: the reel faces West toward the pump and its free end is 16 cells to the south-east, so the straight lead-out
sends the hose west under the pump, round the pond and back east (D10 shape) along the row the battery stands in.

**Regression — "we used to be better than this".** No single sha turns a good lay bad; three changes stack:
- **0476fadd29 (2026-10-05) + b59ebcfec1 (2026-10-06, owner card "straight lead-out")**: the hose must leave by the reel's west
  nozzle and run straight before bending, and the reel's own footprint is solid to its hose (LayFrom). Before these the hose
  left the reel on the side facing its target. Since then every target behind the reel is a 180° loop (D10), and loops are
  what sweep hoses under neighbouring buildings.
- **73b8805755 (2026-10-22 07:59)** let reels turn to 4 facings — the fix for D10 — but **0ab8470911 (09:10)** and the
  scenario stagers (`liquid_checks.py:77`, `water_scenes_walk.py:739`: `RM_HoseReel:x,z,3`) still build every staged reel
  West, so the walkthrough shows the loops the turn was built to remove (SITE).
- **f256450686 (2026-10-22 00:17)**: hose 2x thicker and the nozzle moved to a per-look measured point; it made every
  near-miss joint (D5-D9) twice as visible and moved the mouth the loops start from.
The wall-seam hole (D1) is older: `WallDepth`'s per-cell rule dates from GSS round 4 (9e9f153d4e, 2026-10-04, moved to
FlowWorks 7cf08bf64e 2026-10-11); it was latent until a loop's return leg landed exactly on a seam.

## 5. His question: give up and draw hoses under like pipes?

### (a) Fixing the over-ground look — what it takes

| fix | defects | size |
|---|---|---|
| F1 wall test measures depth to the nearest walkable cell; selftest of a hose on a wall seam | D1 | S (half a day) |
| F2 hoses avoid non-rig buildings (cost like reels/pumps, or blocked), and draw ABOVE a walk-over building they must cross | D2, D12 (same rule in GSS) | S-M |
| F3 one coupling rule: a reel couples to a pump/tank/pipe only through its nozzle; delete the back/top stubs; the coupling ends ON the measured port point | D3, D5, D6, D7 | M (geometry x 4 facings x 4 looks; per-port selftest) |
| F4 tank end lands on the flange (end point = flange tip, no kink) | D8 | S |
| F5 collar overlaps the nozzle: measure the coupling sprite's opaque start per look and draw the collar from the tip | D9 | S (art measurement exists: `reel_intake_geometry.py`) |
| F6 stagers face each reel at its target (rot from the target side); optionally auto-face on placement for players | D10 | S staging / M player auto-face |
| F7 stray stubs: find what draws the sideways stub at the tank and the loose end cap | D4, D6 | S |
| F8 hose-over-hose crossing: draw the later hose over with a shadow | D11 | S-M |
| F9 **joint gate**: a mechanical check before anything is shown — for every reel/port, the drawn collar's box must overlap the nozzle/port sprite box (state read + zoomed crop per joint), red blocks the showing | all | M |

Total ≈ 3-5 agent-days. Risk: the joints have been "fixed" before (HOSE_ENDS_FIX_MISSES_THE_PORTS last night) and the walk
still showed them; without F9 the same thing recurs.

### (b) Hoses under like pipes — what it means

In code: a hose becomes a cell-linked thing like `RM_UniversalPipe` — a cell path (the A* already exists), drawn by a section
layer in an atlas beneath buildings, connections solved by the atlas the way pipes already solve T/cross/ends. The reel stays
a building; the hose leaves from its cell edge. Retired: the slack/S-curves, settle, stiffen, lead-out, joiners, plump/flat
meshes, carry/drag drawing, most of HoseMath (~7,200 lines in `Source/Hose`) and its selftests.
Look: a hose reads like a second, differently coloured pipe; straight runs and 90° corners; no gaps by construction; under
batteries and walls like every pipe (that is then correct, as it is for pipes).
Cost: M-L (2-4 days) for draw + routing + save migration of laid hoses + new atlas art per look (4 looks).
Loses: the hose's whole character — the loose curve, the swelling when it fills (could survive only as a tint/width atlas
swap), a colonist visibly dragging it out and the reel paying it out, hoses lying across water and ramps, and every owner card
on lead-out, slack and girth. Hoses and pipes would no longer be different things to look at; the reel becomes a pipe valve
with a range limit.

### (c) Recommendation

Keep the over-ground hose, but stop drawing it where it cannot look right: fix the wall-test hole and the building rule
(F1, F2), face staged reels at their targets (F6), and make every fixed short coupling one simple rule ending on a measured
port (F3-F5) — and add the joint gate (F9) so no agent can show him a joint that has not passed. If the gate cannot go green
on both walkthrough maps in one sitting, take (b): that would show the geometry is not worth its cost.

## 6. Findings filed

- `HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES` — D3, D4, D5, D6, D7, D8, D9, D11 (instances listed in its item file).
- `HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS` — D2, D12, and the D1 symptom.
- `HOSE_CLEAR_FIX_WALL_SEAM_LOOPHOLE` — D1 mechanism (new).
- `SCENARIO_REELS_FIX_STILL_FACING_WEST` — D10 staging (new).
- `HOSE_LOOK_DECIDE_OVERGROUND_OR_UNDERPIPE` — §5, his decision.
- Lesson (lessons.py): a forced fresh re-lay (nudge a shape setting, restore it) tells a stale lay from a planner bug.
- Existing items that already carry part of this: `REEL_OUTLET_DECIDE_ALWAYS_GOES_WEST` (D10 rule), `PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID`,
  `PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS`, `HOSE_PLUMP_FIX_SKINNIER_WHEN_FULL` (joints study, `Transient/pile_2026-10-22/joints_study.md`).
- Process: lesson cb9c257eb3 (walk previews must check every hose/reel joint up close) already filed before this audit.
