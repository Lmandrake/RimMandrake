# FlowWorks hoses: geometry as physics (C0 / G1 / G2, bend limit, length) — 2026-10-23

Item: HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS. Owner, 2026-10-23 ~22:15 (verbatim): "Ok, we need to talk. The connected hose
logic is just broken in terms of proper hose behavior. There should be constraints on the absolute (location), first
derivative (slope/angle), and second derivative (curvature) of the hoses to avoid precisely this sort of thing. Each pipe
segment must join with the others absolutely by location and slope and curvature. Try that, that's the actual physics. Look
up algorithms for realistic segment matching in splines and physical cable and wire simulations. Please do this right, this
is getting embarassing."

Owner, ~22:25 (verbatim): "I think you need to add both a human review and Lodestar station with very complex hose
connections that force challenging matching criteria. Hoses connected to hoses, sharp turns, mazes, the works. Do a design
pass to find the minimum set of these that tests a range of difficult matching. Currently you mostly test nearly linear runs."

## 1. Requirements (what "right" means, measurably)

| id | requirement | measured as (on the polyline the game DRAWS) | threshold |
|----|-------------|-----------------------------------------------|-----------|
| R1 | C0 at every joint (reel nozzle, port, relay inlet, hose-to-hose coupling, mid-hose joiner) | distance of the drawn end from the point it must meet | ≤ 0.02 cell |
| R2 | G1, and a hose leaves a coupler/port along the port axis | angle between every drawn segment inside the lead-out (first `S` cells) and the port axis | ≤ 2° |
| R3 | G2, κ = 0 at a straight lead-out | (a) curvature inside the lead-out ≤ 0.05 /cell; (b) curvature change per unit length, max over the hose, ≤ J_max | J_max = κ_max / 0.4 = 2.08 /cell² |
| R4 | \|κ\| ≤ 1/R_min everywhere, ends included (today's measure skips 0.5 cell at each end) | discrete Menger curvature at every vertex | ≤ 1.05/R_min (R_min = 1.2 cell) |
| R5 | two hoses on one fitting never cusp; each leaves along its own port axis | per fitting, the angle between each hose's first segment and that hose's port axis | ≤ 2°; no two hoses on one axis point |
| R6 | length conserved; slack shows as a smooth drape | \|L(pose) − L(flat)\| / L(flat) for flat, plump, every transition tick sampled and every port/mate re-fit | ≤ 2% |

Discrete curvature at vertex i: κ_i = 2 sin θ_i / |x_{i+1} − x_{i−1}| (θ_i the turning angle). A single-vertex kink of angle θ
at spacing h reads κ ≈ 2θ/h, so a 15° kink at h = 0.25 reads 2.1 /cell > 0.875: R4 sees every kink, which is why it is also
the G1 test away from the lead-outs. J_max: "the curvature may ramp from 0 to the bend limit over no less than 0.4 cell" — a
clothoid transition of 0.4 cell is a little over one drawn hose width-and-a-half at the closest zoom, the shortest ramp that
does not read as a corner. A step in curvature (an arc butted to a straight, a Dubins path) reads κ_max / h = 3.3 /cell² at
h = 0.25 and fails it, as it should: that is the visible "corner" at the start of every lead-out today.

**R_min = 1.2 cells, kept.** Drawn widths are 0.18 cell (flat) and 0.23 cell (plump, the outside diameter that matters for
kinking). Manufacturer minimum-bend-radius tables for rubber/PVC water and hydraulic hose run roughly 4–10 × OD (SAE J517
hydraulic hose; garden and fire hose ≈ 5–8 × OD for the kink-free radius). 1.2 / 0.23 = 5.2 × OD: inside that band, the
existing setting (HoseShapeParams.MinBendRadius, a player setting) and the owner's earlier stations already read it. Lower
would let the hose fold like string in a one-cell corridor; higher would refuse most indoor lays. A path that cannot meet it is
re-routed (the planner already rounds corners at R and tries wider routes) or refused with a reason — never drawn kinked.

## 2. Why today's hoses break (inventory, read in full: HoseMath.cs, RM_MapComponent_Hoses.cs draw path, HoseRelay.cs,
HoseSpliceMath.cs)

The lay is a chain of LOCAL position edits, each correct for its own concern and blind to the derivatives the previous one
set:

1. `CordPlanner.Plan` (A*, string pull) → `RoundCorners(R)` → `SCurves` (seeded sinusoid slack) → `CordLayer.Settle` (rope)
   → `Stiffen` (midpoint pulls while a turn exceeds seg/R; ends PINNED BY POSITION ONLY — no tangent, no curvature boundary
   condition). On failure a fallback chain ends in the raw string-pulled plan, a polyline with sharp corners.
2. `StraightenEnd` (an end into a relay/port): a 0.5-cell smoothstep POSITION blend onto the inlet axis. A position blend of
   a curve onto a line has a curvature spike at both blend ends, and a cusp when the curve arrives from the side.
3. Reel lead-out: a straight run, then a Dubins arc onto the chord of the flat pose. Dubins = straight + arc: curvature jumps
   0 ↔ 1/R (G1, not G2), then a Catmull-Rom resample.
4. `Finish` → `StraightenAt` per joiner: chord + 0.5-cell position blend — curvature spikes at the blend ends.
5. Draw time (`RM_MapComponent_Hoses.DrawAll`): `Pose` adds a wobble with envelope sin(πs) — nonzero SLOPE at the ends, so
   every fill transition rotates the lead-out off the port axis. Then `EndOnPort` (a cubic Hermite over 1.2 cells, tangent
   magnitude = chord): G1 at both ends, curvature discontinuous at the cut, and a lateral offset d over L = 1.2 gives
   κ ≈ 6d/L² — **screenshot 20261023221102**: d ≈ 0.3 → κ ≈ 1.25 (R ≈ 0.8 < 1.2): the S-jog one cell before the tank port.
   A side arrival instead gets `SlideEndOnto` (a 0.75-cell lateral position slide).
6. The bend measure `MinBendRadius` skips 0.5 cell at each end: every defect above lives in the unmeasured half cell.
7. **Screenshot 20261023221228** (sleeve on the nozzle axis, one hose leaving the sleeve ~30° off axis, the other in a ~150°
   V): a relay reel. `LayFrom` gives a FED reel no lead-out axis at all (code comment: "a relay reel's west nozzle is where the
   FEEDING hose couples ... its own hose keeps the pre-2026-10-05 start; flagged to the owner, not redesigned here"), so its
   own hose leaves the nozzle at whatever angle the plan starts with, while the feed is straightened INTO the same nozzle
   from the opposite direction. Two hoses on one coupling is physically impossible; `joint_check.py` already FAILs it live
   (`feed_nozzle_shared`). The reel art has ONE connector — giving the relay a second port is an art/owner decision (§7).

The one place that is already G2 is `HoseSpliceMath` (hose-to-hose mates): a clothoid chain with curvature knots and an
active set |κ| ≤ κ_max. It is the right idea used in one corner.

## 3. Candidates

References: Moreton & Séquin, "Functional optimization for fair surface design" (SIGGRAPH 1992 — the minimum-variation
curve, ∫(dκ/ds)²); Bertolazzi & Frego, "G1 and G2 fitting with clothoids" (Math. Meth. Appl. Sci. 2015/2018); Levien,
"From spiral to spline" (PhD thesis, 2009 — the Euler spiral / MEC; why elastica alone cannot give κ = 0 at a clamp);
Bergou et al., "Discrete Elastic Rods" (SIGGRAPH 2008); Müller et al., "Position Based Dynamics" (2007) and Umetani et
al., "Position-based elastic rods" (SCA 2014) for inextensible cable simulation; Bertails et al., "Super-helices" for
clamped-rod boundary conditions; de Boor, "A Practical Guide to Splines" for C2 cubic B-splines.

**A. Clothoid (G2) spline through waypoints** (Bertolazzi–Frego; extend HoseSpliceMath.Join to the whole hose). Exact G2,
curvature piecewise linear in arc length, κ bound by active set. Cost: Gauss-Newton per segment pair, a global nonlinear
solve over all waypoints for G2 at interior knots; the waypoints themselves must be chosen (the planner's corners are not
G2-feasible at R). Obstacles are not in the formulation — a re-solve can swing a segment into a wall and must be checked and
re-seeded. Length is an output, not a constraint (R6 needs a length target as an extra equation). Stability: Newton on
Fresnel integrals is well-conditioned near a good seed, poorly near U-turns (the Dubins seeds already needed in the mate
solver). Deterministic given a fixed seed order.

**B. C2 cubic B-spline, end control points collinear on the port axis.** C2 ⇒ G2 at every knot for free; κ = 0 at a clamp by
making three end control points collinear on the axis. Cheap (linear least squares fit to the existing pose). But: |κ| ≤ κ_max
is not expressible linearly (a post-check + knot insertion loop), length is not linear, and arc length is not the parameter
(sampling must re-parameterise). Obstacle avoidance is outside the fit. Stable and deterministic.

**C. Constrained discrete fairing of the drawn polyline ("HoseFair") — CHOSEN.** The variables are the N drawn sample points
themselves (N fixed, so Flat/Plump/Centre still blend index for index and joiner indices stay valid). Minimise, by banded
Gauss-Newton (Levenberg-damped) with a fixed iteration count:

- stretch  w_s (|x_{i+1} − x_i| − h)/h — inextensibility (PBD/elastic-rod constraint): length = (N−1)h = the FLAT length (R6);
- bend     w_b √h (x_{i−1} − 2x_i + x_{i+1})/h² — discrete elastica ∫κ² (Bergou; linear residual);
- jerk     w_j √h (x_{i+2} − 3x_{i+1} + 3x_i − x_{i−1})/h³ — Moreton–Séquin ∫κ'². This is what makes the curvature RAMP from 0
           at a clamped straight: elastica alone puts a curvature step at a clamp (Levien §4), the jerk term removes it (R3);
- bend cap w_k √h max(0, |D2_i|/h² − κ_max) — the active-set bound (R4), only on vertices over the bound;
- clearance w_o max(0, c₀ − Clearance(x_i)) with CordWorld.ClearanceGradient — never pushed into a wall;
- anchor   w_a (x_i − x_i⁰) — tiny; keeps the route the planner chose (no drift through a doorway it did not take).

Constraints are pins, not penalties: the reel lead-out (S cells), the port/relay lead-in (EndStraight = 0.6 cell), every
joiner's straight span and every mate coupling's straight have FIXED positions on their axes. Because a pinned straight run
enters the bend and jerk residuals of the first free vertices, the free curve meets it with matching position, tangent AND
zero curvature: C0, G1 and G2 at every joint by construction, with no blend to spike. Interleaved (x,z) ordering gives a
half-bandwidth of 7, so a solve is O(N): a 40-cell hose at h = 0.25 is 160 points, 30 iterations ≈ 0.3 ms.

Why C over A and B: it is the only one where position, tangent, curvature, the bend bound, length AND the walls are in ONE
problem — A and B each need a separate obstacle and length loop around them, and those loops are exactly the "local fix after
local fix" that broke today's code. C is also what the cable/rope literature does (discrete rods, PBD constraints), it runs
on the pose the game already has (no new representation, no re-sampling of joiners), and its failure mode is soft: an
infeasible bend (a one-cell corridor U-turn) shows as a residual over the bound, which the lay rejects and re-routes (the
planner's wider route) or refuses with a reason — never a drawn kink.

Determinism: no RNG, fixed iteration count, fixed weights, deterministic banded Cholesky; inputs are the existing seeded
lay. Stability: Levenberg damping λ adapted by accept/reject; a step that raises the objective is rejected; the result is
accepted only if it is wall-clear and its bend/kink measure is no worse than the input's, else the input is kept (no
regression path).

Where it runs:
1. End of `HoseMath.Finish` (lay time, cached): Flat and Plump faired with their pins; Plump gets the FLAT length as its
   stretch target, so filling straightens the drape but conserves length (R6: the extra shows as a gentle sag, not as hose
   vanishing). The old StraightenEnd/StraightenAt blends and the Dubins corner now only produce the initial guess.
2. Draw time, a moved port (`EndOnPort`/`SlideEndOnto` retired): a WINDOWED fair — the last ~2.5 cells free, everything before
   pinned, the end pinned to the port with its straight lead-in. Cached by the existing pose key.
3. `Pose` wobble: envelope sin³(πu) over the stretch between the lead-out and lead-in (zero value, slope and curvature at
   both), so a fill transition never rotates a lead-out (R2/R3 during transitions).
4. Mates keep HoseSpliceMath.MateTail (already G2); the instrument measures them like every other joint.

GSS `_Shared/SlackGeometry` is UNTOUCHED (HoseFair only reads CordWorld.Clearance / ClearanceGradient), so Gimme Some Slack
cords stay byte-compatible; their own geometry is out of scope.

## 4. Hard hose stations

### 4.1 Difficulty dimensions

| id | dimension | why it is hard for matching |
|----|-----------|-----------------------------|
| D1 | hose-to-hose splice (two open ends meeting, at an angle) | G2 at a coupling not on any building; both tails re-shaped |
| D2 | relay chain (hose → relay reel → hose) | two hoses at one reel; R5 |
| D3 | turn sharper than R_min forcing a re-route (wider loop) or a refusal | κ bound is binding |
| D4 | U-turn (target behind the reel) | 180° with clamped tangent at the nozzle |
| D5 | S-bend (lateral offset < 2 R_min over a short run) | inflection, curvature sign change |
| D6 | maze / obstacle corridor (2-wide serpentine) | many bends, clearance active |
| D7 | several hoses on one fitting at different port axes (a tank fed from two faces) | R5 |
| D8 | crossing / over-under | drawn order, crossing lift (no geometric coupling, must stay smooth) |
| D9 | slack + drape (long free run) | length conservation, plump straightening |
| D10 | very short span between ports (≤ 3 cells) | lead-out + lead-in nearly overlap, no room to ramp |
| D11 | all four reel facings | axis maths per rotation |
| D12 | side arrival at a port (the hose comes in parallel to the face) | the lead-in must turn 90° within the port's reach |
| D13 | height: over a walk-over building | hoses have no levels; the only "height" is drawn over/under (D8) and over buildings |

### 4.2 Minimum station set

A review_map station is 16 × 14 local cells; a hose needs ~2 R_min = 2.4 cells to turn round, so no single station can hold
every case readable at once. Three stations is the minimum that fits each dimension with room to read it (a two-station set
was tried on paper: the maze plus the four-facing set overflow 16 × 14 and the fittings could not be separated from the bends
in a screenshot). Each station is ALSO an offline canned scene (`HoseCurveChecks`, cells identical) and a NORTHSTAR row set.

- **S1 `hose_hard_bends`** — four reels, one per facing: E-facing with its target directly behind it (U-turn, D4); N-facing to a
  target one cell lateral and three ahead (S-bend, D5); W-facing to a tank 2 cells in front (short span, D10, port lead-in);
  S-facing into an L-corridor one cell wide (sub-R_min corner: re-route round the corridor's open end or a refusal, D3).
- **S2 `hose_hard_maze`** — a reel in a 2-wide serpentine (three 180° turns, D6/D4), its hose crossing a second, straight hose
  laid across the maze's exit (D8), a third reel with a long slack run (14 cells, D9) over a power conduit (D13).
- **S3 `hose_hard_fittings`** — two reels whose open ends meet at 90° (splice, D1); a relay chain (D2); a 2×2 tank fed by two
  hoses on two faces (D7) one of which arrives from the side (D12).

| dim | S1 | S2 | S3 |
|-----|----|----|----|
| D1 splice | | | ✔ |
| D2 relay | | | ✔ |
| D3 sub-R_min | ✔ | | |
| D4 U-turn | ✔ | ✔ | |
| D5 S-bend | ✔ | | |
| D6 maze | | ✔ | |
| D7 two hoses one fitting | | | ✔ |
| D8 crossing | | ✔ | |
| D9 slack drape | | ✔ | |
| D10 short span | ✔ | | |
| D11 four facings | ✔ (all 4) | | |
| D12 side arrival | | | ✔ |
| D13 over building | | ✔ | |

### 4.3 HUMAN (review_map.py stations + capture list)

Stations `hose_hard_bends`, `hose_hard_maze`, `hose_hard_fittings` (section "carry", after `hose_their_tank`, caps K09). The
capture list, each at the closest zoom, flat AND plump (fill toggled through the reel), one transition mid-wobble:

| shot | station | subject | what fails it |
|------|---------|---------|---------------|
| HH1 | S1 | U-turn reel, whole loop | any corner; a loop tighter than the reel's own width |
| HH2 | S1 | S-bend into its free end | a jog; the hose not straight for the first ~0.6 cell out of the nozzle |
| HH3 | S1 | short span into the tank port | the hose entering the coupling at an angle |
| HH4 | S1 | L-corridor reel | a hose drawn folded in the corridor (a refusal message is a PASS) |
| HH5 | S2 | maze, all three turns | a bend clipping a wall; a flat spot then a corner |
| HH6 | S2 | crossing | not cleanly over/under; a kink at the crossing |
| HH7 | S2 | slack run, flat then plump | hose "vanishing" when it fills (length) |
| HH8 | S3 | the splice coupling | the two hoses not leaving the coupling on its axis |
| HH9 | S3 | relay reel | two hoses on one nozzle (KNOWN, owner item §7) |
| HH10 | S3 | tank with two hoses | either hose off its port's axis; side arrival bent at the coupling |

### 4.4 NORTHSTAR (deterministic rows)

`northstar/hose_curve_proof.py` asks a new read-only HoseProbe verb `curves` that runs the SAME Verse-free metric class the
offline selftest uses (`HoseCurveMetrics`) on every laid hose's DRAWN strand (`RM_MapComponent_Hoses.DrawnStrand`) and its
end targets. Per hose, rows (PASS/FAIL against §1, UNMEASURED when no strand was drawn):

| row | reads | dims |
|-----|-------|------|
| C1.end_gap | R1 at both ends (port/nozzle/relay/mate) | all |
| C2.leadout_angle / C2.leadin_angle | R2 | D10, D11, D12, D7 |
| C3.leadout_kappa, C3.dkappa_max | R3 | D4, D5, D10 |
| C4.kappa_max | R4, ends included | D3, D4, D5, D6 |
| C5.fitting_cusp | R5 per fitting with ≥ 2 hoses | D1, D2, D7 |
| C6.length_err | R6 flat vs drawn | D9, D8 |
| C7.station_cover | every station hose present and laid (a refused lay is a PASS only on the S1 L-corridor reel, with its reason) | D3 |

The offline selftest (`--hose-curves`) builds the three layouts as CordWorld scenes with the same cells, lays each hose with
`HoseMath.LayAlong` as `LayFrom` does, runs the draw path (Pose at e = 0, 0.5 + wobble, 1; port re-fit; mate) and asserts
the same rows. It must FAIL on the pre-change code (numbers in §6).

Relation to GPT_REVIEW plans H/N (compression): these three stations are the hose bays of plan H's H1 joint station
(captures H1-06/H1-07 become HH1–HH10) and C1–C7 are N1's hose geometry rows (H05–H10); nothing here duplicates them —
plan H/N decide where the stations sit, this decides what they contain.

## 5. GPT attack

Raw reply: `D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023\gpt\answer.md` (question `q.txt` beside it). Verdict:
"reject as written" for the first plan (HoseFair, a pinned-sample jerk-penalty fairing of the shaped polyline). 9 blockers,
6 majors, 1 minor. **Adopted:**
- the method it proposed instead: a **material-coordinate piecewise clothoid chain** (curvature linear in arc length per
  0.5-cell piece, integrated exactly by 4-point Gauss-Legendre), so G1 and G2 hold by construction, not by penalty
  (blockers 1, 2, 4, 10); `Hose/HoseClothoid.cs`;
- exact material length (sum of piece lengths = the lay's flat length, fixed N per solve) (blocker 5, R6);
- straight leads and joiner spans as zero-curvature node runs padded by one drawn sample, so the ruler's stencil reads
  the release straight (blocker 2);
- |kappa| <= kmax and |dkappa| <= J*l per piece as hard checks at the end (`BoundsHold`), the solver only proposes (blocker 12);
- wobble faded to zero over the leads (SmootherStep envelope) so the pose cannot break a lead (blocker 6);
- the tail onto a port re-solved as a clothoid window of the SAME length with the kept head's position, heading and
  curvature at the cut (blocker 7: window grows 2.5/4/6/all until feasible, and fails honestly);
- the fallback is explicit: a lay whose fit is infeasible keeps today's shaped pose and is tagged `[shaped: why]` in the
  ruler, so a failure is visible, never hidden (blocker 1's "do not report a penalty as a constraint").

**Not yet adopted** (remaining work, §6): clearance as interval constraints (blocker 14/15 point: today Clear is checked on
samples after the solve); HoseSpliceMath's MateTail still its own solver (blocker 8, the mate rows fail); a temporal
stability term between poses (major 15); an analytic Jacobian (major 11/15: the finite-difference LM costs seconds per lay,
which is why G2 is OFF in the game).

## 6. Instrument numbers

Instrument: `SelfTest/HoseCurveChecks.cs` + `Hose/HoseCurveMetrics.cs` (the ruler: C0 gap, lead angle and lead curvature
per end, max kappa vs 1/R x 1.05, dkappa/ds vs 2.5/R, length error, splice seams), over the hard stations
(`hose_hard_bends`, `hose_hard_maze`, `hose_hard_fittings`, §4.2) in four poses each (flat, plump, filling, settling),
plus 6 synthetic clothoid cases (`SelfTest/HoseClothoidChecks.cs`). Run: `RimMandrakeFlowWorks.SelfTest --hose-curves
[g2off] [report <path>|dump <path>]` (G2 is on by default since 2026-10-24; `g2off` measures the shaped poses alone);
not in the default run while it fails. `--hose-fuzz [g2off]` runs the hose fuzz alone and prints the solver's cost.

| run | passed |
|---|---|
| today's code (before, 2026-10-23 23:00) | 12/52 (+5 of 6 synthetic cases once added = 17/58) |
| `--hose-curves` with G2 off (game default) | 17/58 |
| `--hose-curves g2` (clothoid fit on) | 30/58 |
| step 1 (2026-10-24): Gauss-Newton solver, G2 on by default | 30/58 (same cases as the old solver); `g2off` 17/58 |

Solver cost (step 1, 2026-10-24; logs `D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023\st_full3.log`, `hc_on.log`):

| solver | per solve | hose fuzz (2798 cases, 2407 laid) |
|---|---|---|
| finite-difference Levenberg-Marquardt (before) | seconds per lay | not run (G2 off in the fuzz) |
| GN-SQP with analytic Jacobian, retry any infeasible fit | 0.72 ms | 13092 solves, 9.4 s = 3.9 ms per laid hose |
| GN-SQP, retry only fits whose end came within 0.3 cell (kept) | 0.55 ms | 9450 solves, 5.2 s = 2.2 ms per laid hose; 3054 of 5298 poses fitted (58%) |

Feasible solves take ~20 iterations (~0.35 ms); the cost is the infeasible ones, which press the curvature bounds (the
shaped route is tighter than 0.95/R with the ramp limit): step 4's re-route. In the game the fit runs at lay time and,
for a G2 port tail, once per drawn-pose cache miss (once a tick during a fill/settle transition, not per frame).
The full FlowWorks selftest with G2 on: 428/428 hose assertions, fuzz 4/4, known-gap classes 4 -> 1 (G3, G5 and the free
G4 gone; G4 outlet 8 -> 6); the hose fuzz takes 16.4 s instead of 10.9 s. `LayOpen`'s "plump is shorter / straighter"
asserts hold only for a shaped (non-G2) lay; a G2 lay is asserted to keep its length (R6) and drape no wider.

Remaining failures with g2 on (`D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023\after_report.txt`):
- **mates** (mateA/B, splice): the flat G2 lays are clean (pre-mate lead 0.0 deg), then `HoseSpliceMath.MateTail` re-lays
  the tail with its own solver, which frees the length (4.9 -> 21.3 cells on mateA: a loop) and bends the start lead
  5.3 deg. Fix: MateTail through `HoseClothoid.TailOnto` with length conserved, partner clearance kept.
- **tank ports** (tankE/W): the lay ends at the cell centre with a free heading and DrawnPose bends it onto the flange
  afterwards; a perpendicular arrival half a cell from the face cannot turn at R=1.2. Fix: lay to the flange with
  `endInward` = port axis (as relays already do), in `EnsureLay` and in the test alike.
- **short / tankW fits infeasible** (end gap 0.11-0.34 with the bound pressed): the shaped route is too tight for R; the
  route must be re-planned wider (R4: re-route, never kink), not fitted.
- **uturn**: the 26-node fit stalls (gap 0.38) -> shaped fallback, dk/ds 2.4-2.5 vs 2.1.
- **TailOnto synthetic** (port 1.5 north of an eastward hose): no window feasible; needs an S-dip guide.
- **relay**: KNOWN owner item (§7).

### Step 2 (2026-10-24): mates keep length and leave the start lead alone

- With G2 on, `HoseSpliceMath.MatePair` goes through `MatePairG2`. Each end is re-shaped by `HoseClothoid.TailOnto`, using a G2 cut and a window of the same material length, with the start lead plus 0.25 untouched. The coupling point slides (rings 0, 0.3, 0.6, 1.0, 1.6, 2.4 cells) toward the inner corner, behind either hose, or diagonally behind it. The first ring with a clear pair wins. With length kept, a fixed coupling cannot bend toward the partner.
- The game draw (`Mated` → `MateEnd`) and the ruler share it. The old `MateTail` is used only with G2 off.
- `--hose-curves`: 30/58 before, 31/59 after. The new passing case is the synthetic slack 90-degree mate, which proves that length is kept to within 1%, the lead samples are unchanged, and both ends pass the ruler.
- mateA, mateB and splice (12 rows) now fail honestly with "no mate fits (length and start leads kept)" instead of looping. Those hoses are near-taut (4.72 of material against a 4.59 chord) and need a 37-degree turn. This is owed to step 4, as a lay-level re-route or mate.
- Full FlowWorks selftest is green at 935/935. S5 judges a G2 MatePair with the ruler and checks that both lengths are kept.

### Step 3 (2026-10-24): tank port ends point inward

- `HoseMath.PortLay` first lays to the drawn end on the flange (`port - axis x 0.5`) with `endInward` = the port axis. `EnsureLay` and `HoseCurveChecks` use the same call. The lay key carries the port point and axis.
- If that lay does not fit G2, or is refused, PortLay falls back to the old cell-centre lay and records `PortWhy`. That way EnsureLay never refuses a hose it used to lay. `DrawnPose` leaves a pose that is already on the port axis (`OnPortAxis`, within 1 degree over the end straight) untouched.
- `--hose-curves`: 31/59 before, 35/59 after (tankE passes in all four poses).
- tankW and short still fail, now with an honest reason: no G2 curve fits onto the port axis (step 4). Full FlowWorks selftest is green at 935/935. Log: `D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023\h4_full1.log`.

### Step 4 (2026-10-24): re-route when no curve fits
- When the flat fit fails, `HoseMath.Reroute` lays guides between the two lead ends as Dubins paths.
  - Radii are 1.15, 1.4 and 1.8 times 1/kmax, with every word tried.
  - A free end's heading is tried as shaped and turned by ±30 and ±60 degrees.
- A guide is kept only if it is clear, has no loop, crosses no more reels than the shaped lay, is no longer than the hose and is at most 2x the shaped length.
- The hose is fitted to the shortest guide first, at 1.0 and 1.05 of the guide's length, with at most 8 fits.
  - One curve serves both poses, so its body must clear every wall by the full charged half-width.
  - It is not allowed to be merely as close as the shaped pose. With that weaker rule, D1 shaved 14 of 200 plain sweep lays.
- `HoseLay.Rerouted` marks the result, and the ruler's row tag reads `[g2 re-routed]`. Lays with joiners are not re-routed.
- `--hose-curves`: 35/59 before, 38/59 after (uturn passes in every pose). Full FlowWorks selftest is green at 935/935.
  - Logs: `D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023\h4_14.log` and `full6.log`.
- 21 rows still fail. Hand reasoning (not a proof) says they are infeasible under today's leads, which makes them owner items (§7):
  - short (4): the port-axis lay is refused on its lead-out (LeadOutBlocked). An S onto the port axis needs dx of about 2.17 at R, and only 1.73 is free after the leads.
  - tankW (4): dx is 0.91, which is less than R. Every Dubins guide loops over a reel: it crosses 2-3 reels where the shaped lay crosses none, and runs 14-22 cells for a 5-cell hose.
    - The cell-centre fallback then lays G2, but `DrawnPose` bends it onto the flange, so it draws a kink.
  - mateA, mateB and splice (12): each hose is 4.72 long, and 2.2 of that is its lead-out, so only 2.27 is free for B's S-turn onto the shared axis. B's `TailOnto` misses its end by 0.4 to 1.1 cells at every coupling ring.
    - Tried and dropped: letting the reels pay out up to 3.2 more cells (with every slide ring) fixed no row, so the code does not ship.
  - TailOnto synthetic (1): unchanged from step 2.

### Step 5 (2026-10-24): the ruler guards the default run
- The synthetic TailOnto case asked for a port that no 9-cell hose can reach.
  - At (8, 1.5) the 0.6 end straight leaves 0.9, which is less than R, so the turn must dip south first. The shortest path within R is then 6.74 + 1.98 + 0.6 = 9.32 cells.
  - Moved to (7, 2), where the shortest path is about 8.3 cells. It now passes.
- `HoseCurveChecks.Guard` runs the whole `--hose-curves` set inside the default FlowWorks selftest as one case. The case fails when:
  - a row outside `Owed` fails (the 20 rows owed to HOSE_SHORT_SPAN_DECIDE_NO_CURVE);
  - fewer than `Floor` rows pass;
  - the row count is not 59.
- MEASURED: 39/59 pass, floor 39. The full selftest is 936/936 and `run_selftests.py --only selftest_flowworks_stock.py` is GREEN (175.8 s).
- Can-fail check: with the short prefix taken out of `Owed`, the case fails ("4 row(s) outside the owed set fail"). Logs: `full7.log` and `full7_canfail.log` in `D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023\`.

### Step 6 (2026-10-24): shorten the lead-out on short spans
Owner by card 2026-10-24 "Shorten the lead-out" (option (b) of §7). Owner, relayed: "Write python to explore these arrangements rather than slowly waste time during the game, solve the problem completely, then implement".
- The rule: a hose keeps the 2.2 lead-out when a G2 curve fits behind it. Only when none fits does the lead-out shrink. It takes the LARGEST lead in [0.6, 2.2) whose lay is G2.
  - The search tries 1.8, 1.4, 1.0 and 0.6 in turn, then bisects to 0.05 (`HoseMath.LeadSearch`). Long hoses never enter it.
  - A lead-out a wall blocks stays refused (card 2026-10-06).
- How the C# code does it:
  - `HoseMath.LayAlong` runs the search with `HoseShapeParams.WithLeadOut` and marks `HoseLay.LeadShortened`.
  - Mates shrink one common lead for both halves (`HoseSpliceMath.MatePair`).
  - A shortened lay fits on a 0.25 node step and scans length x{1.0, 0.97, 1.03, 0.94, 1.07} (`G2Fit.FitAt`).
  - It is drawn without the transition wobble: a span at its bend limit has no room to wobble.
  - A re-route (step 4) now tries guide lengths x{1.0, 1.05, 1.12, 1.2, 1.3}, not x{1.0, 1.05}. tankW's guide needs 1.12 or more.
- The offline explorer is `src/RimMandrake/FlowWorks/Tools/hose_geometry_explore.py`. It is a free-length G2 solver with Dubins seeds, plus a continuous coupling for mates. Pictures and data are in `D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023\explore\` (`rows.png`, `map_port.png`, `map_free.png`, `gallery_*_{shrunk,nofit}.png`, `summary.json`). MEASURED sweeps:
  - port (4480 placements):
    - 3966 keep 2.2 and 208 shrink (median lead 1.5, min 0.6).
    - 126 are layout cases: the end run hits the reel or fixture.
    - 108 are detour-only: they fit only at 2.41x the shortest path or more.
    - 72 have no fit even at 0.6. These are too close for the bend limit. A continuous S-bend bound gives a maximum lateral offset of 0.127, 0.398 and 0.941 cells at forward 1.33, 1.9 and 2.5.
  - free ends (1280): 1228 keep, 34 shrink, 18 have no fit.
  - mates (400): 208 keep, 77 shrink, 115 have no fit.
  - These are findings about geometry, not new policy. A span with no fit at 0.6 keeps today's fallback (§7 (c)).
- `--hose-curves`: 39/59 before, 47/59 after (MEASURED, `c_run10.txt` in the explore folder; the full FlowWorks selftest is 942/942 in `full_47b.txt`). short now fits at lead 0.8 and tankW at 1.85.
  - Solver total went from 915 ms to 1529 ms over 3985 solves.
  - `HoseCurveChecks.Floor` is now 47. With the floor at 48 the guard case fails ("47 rows pass, floor 48", `full_guard48.txt`).
- Still failing: mateA, mateB and splice (12 rows): "no mate fits".
  - The explorer finds a mate at lead 1.05 (coupling (6.30, 10.12), axis -42.8 degrees).
  - With the coupling fixed at any C# `MateSlide` candidate, it finds none at 1.0 or 0.6.
  - So the discrete coupling slide is at fault, not the geometry. Owed to HOSE_MATE_REWIRE_CONTINUOUS_COUPLING.
- Known gaps, filed:
  - C# shrinks more than the geometry needs (short 0.8 vs the explorer's 1.15), because it fits at a fixed length with leads padded to the node step: HOSE_FIT_HARDEN_FREE_LENGTH_SHORT_LEAD.
  - The explorer runs out of seeds above lead 1.4 on tankW, so its lead there is a lower bound: HOSE_EXPLORER_WIDEN_SEEDS_LONG_LEAD.

## 7. Owner items

- **Relay reel has one connector.** A relay's feed couples into its nozzle while its own hose leaves the same nozzle —
  physically impossible (R5), drawn as the V in screenshot 20261023221228. Options: (a) a second fitting on the reel art (an
  inlet swivel on the drum's hub side) and the feed couples there; (b) the feed couples at the nozzle and the relay's own
  hose leaves from the drum's opposite face. Not decided here; joint_check keeps failing it live until he picks.
- **Short and taut hoses that no G2 curve can carry** (step 4: short, tankW, mates and splice, 20 rows). DECIDED: owner by card 2026-10-24 "Shorten the lead-out" -- option (b), shrink the lead-out on short spans only, down to 0.6 (step 6). Options (a) refuse and (c) the shaped fallback were not picked; (c) remains only where no curve fits even at 0.6. short and tankW pass; the 12 mate/splice rows are owed to HOSE_MATE_REWIRE_CONTINUOUS_COUPLING.

## 8. Rejected (GPT attack and own)

- **HoseFair (own first plan)**: penalised fairing of the shaped polyline with pinned straight samples; rejected by the
  GPT attack (blockers 1, 2, 4) and by the first solver run (an active-set KKT version stalled with zero accepted steps).
- **Active-set KKT solve** of the clothoid chain: replaced by Levenberg-Marquardt with penalty continuation (weights
  10 -> 1e7) and a hard final bound check (itself replaced 2026-10-24: its finite-difference Jacobian cost seconds a lay;
  now Gauss-Newton SQP with the end equalities hard through a KKT step, the bounds as steep one-sided penalties, an
  analytic Jacobian from the rigid-rotation identity, an L1 merit line search and a minimum-norm Newton polish); plus `Snap`, a similarity about the start (<= 1% stretch, <= 0.01 rad) that
  closes the small gap a near-taut length leaves.
- **GPT's point that a too-narrow corridor is an infeasible success fixture** (blocker 3): accepted; the 1-wide L
  corridor row in `hose_hard_bends` may refuse with a reason (`MayRefuse`) but fails if it is laid through the corridor.
- **Flat/plump interpolation as-is** (blocker 6): kept for now, with both poses fitted separately and the wobble faded
  over the leads; a fit of the interpolated pose itself is owed if the filling/settling rows keep failing.
