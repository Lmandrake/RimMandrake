> Provenance: copied unchanged from the owner's Downloads (C:\Users\Mandrake\Downloads\flowworks_water_solver_literature_review.md, file dated 2026-11-12 13:58), filed 2026-11-12 by BENCH; digest in design/plans/2026-11-12-flowworks-water-solver-bakeoff.md.

# FlowWorks: CPU-Efficient Water Simulation on a Single-Valued Elevation Grid

**Technical review and implementation research memo**  
**Date:** 2026-11-12  
**Audience:** Claude Code / RimMandrake architecture, design, and implementation agents  
**Status:** Research synthesis; proposed solvers and optimizations are **NOT IMPLEMENTED OR BENCHMARKED** in FlowWorks unless explicitly indicated.

## 0. Executive decision

**Do not yet commit to design 7 as the final numerical engine.** Keep its *architecture*—bed elevation plus conserved water volume in every square, shared edge fluxes, edge-based structures, and currents derived from actual flux—but compare at least two credible numerical engines before C# implementation:

1. **Stabilized local-inertial shallow-water solver with coupled friction** (highest-priority new prototype). Stores one signed flow per edge, accelerates it using surface-height differences, damps it using bed friction, and commits conservative transfers. No global nonlinear solve each substep. Strong river/flood literature basis [1–3]; important limits at wet/dry fronts [4].
2. **Repaired implicit diffusion-wave solver** (retain existing design 7 as competitor). Benchmark warm starts, residual-aware sleeping, sound preconditioning, nonlinear convergence, and directionally split tridiagonal line solves [7–9]. Existing ~1,600 iterations/pulse are *an observation of one solver*, not an unavoidable property of implicit hydraulics.
3. **Published weighted cellular automaton (WCA2D/CADDIES)** (fallback if low computational cost and water levels matter more than momentum-driven current accuracy) [10–11].
4. **Well-balanced, positivity-preserving first-order full shallow-water equations (SWE)** as a *reference and possible winner*, especially for bursts, breaches, wet/dry fronts, and jets [5–6]. The existing failed wave prototype does not establish that SWE is inherently unusable.

**High-payoff orthogonal improvements:** coarse hydraulic cells with detailed subgrid terrain [12–13]; caching steady flow; active/dry-region skipping; sparse-array/vectorization work [14]. These address different costs and should be benchmarked separately.

### Important interpretation

The user's request was to find **cheaper physics approximations for evolving fluid level *and velocity*** over a single-valued elevation map. Nearly all relevant candidates still evaluate spatial differences (`η_R − η_L`). A numerical derivative is not intrinsically expensive. Cost usually comes from the **number of cells × substeps × inner solver iterations × repeated unchanged work**, not the subtraction used to compute a gradient. Do not optimize away derivatives at the expense of solving an inaccurate or costlier model.

## 1. Existing FlowWorks facts and provenance

**Primary internal source:** `FlowWorks rivers: final design report (2026-11-12)` (provided as `Pasted text.txt`). All findings in this section are **reported by that document**, not independently replicated in this review. Original report paths are Windows paths and are not embedded in this memo.

Internal research bundle: `D:\ClaudeWork\rimmandrake\conductor\rivers_20261112\` — `00_research.md`, `01_designs.md`, `02_gpt_skeptic.md`, `03_gpt_improve.md`, `FINAL_REPORT.md`, `py\implicit_v3.py`, `py\out_implicit3_a.txt`, `py\out_implicit3_e.txt`, `py\out_implicit3_wl.txt`, `py\out_implicit3_cg.txt`.

### 1.1 State and semantics worth preserving

- Each grid cell has one fixed bed elevation `z_i`, true water volume `V_i` (committed as **whole decilitres**), and reconstructed water surface `η_i = z_i + h_i`. No stacked water layers, tunnels, or multivalued bathymetry.
- Each shared edge owns one transfer. The same amount is subtracted from the donor and added to the receiver. Treat sources/outlets as separate counted ledger entries. Currents should be inferred from signed edge flux and wetted cross-section; graphical vectors can follow rather than dictate the model.
- Edge types include open, wall, weir, and sluice/gate. Structure formulas belong to *edges*, not artificially raised water cells.
- The river is allowed to change topology when the player builds dams, digs canals, or breaches moats.
- Boundary semantics remain a **game design decision**, especially what happens when a dam backs water to the upstream map edge.

### 1.2 Reported offline-twin results (not this review's measurements)

| Reported experiment | Result | Original report evidence |
|---|---|---|
| Design 7 plain river, 100×100 map, 12-square river, 41.7 river-s pulse | 16.75 m³/s, settled in one pulse | `py\out_implicit3_a.txt` |
| Full dam | Upper/lower levels ~−0.0999/−0.400 m; no reversals in reported case | `py\out_implicit3_a.txt` |
| Three-square gap in 12-square river | ~15.9 m³/s, with faster local gap current | `py\out_implicit3_a.txt` |
| Moat fills | End level ~−0.156 m after ~625 s with 41.7-s pulses | `py\out_implicit3_a.txt` |
| Fill-time sensitivity | Same final level but ~625 s vs ~3,753 s at 41.7-s vs 417-s pulses | `py\out_implicit3_e.txt` |
| Weir represented as edge | 0.64 m³/s vs 0.66 m³/s hand estimate | `py\out_implicit3_wl.txt` |
| Quiescent solver cost | ~1,647 iterations/pulse on average; ~1,615 in final ten | `py\out_implicit3_cg.txt` |
| Design 2 local neighbor equalization | ~26,000–166,000 passes to settle in test scenes | `py\out_D.txt` |
| Original wave prototype | Several false-flood test outcomes | `py\out_diagI.txt`, `py\out_diagI2.txt`, `py\out_diagI4.txt` |
| Initial dam-build test | 267,455 dL deleted by test harness when replacing wet cells; **not solver leakage** | `py\out_implicit3_e.txt` |

Interpret the report's `0 dL` ledger result as **volume accounting success in the particular tested scenes**. It does not prove hydraulic correctness, stable transient evolution, C# performance, reproducible floating-point computation, or general positivity.

**Unmeasured:** C# in-game runtime, terrain repaint, vanilla shader response, multiplayer/replay bit identity, and numerical performance of any new candidate.

## 2. Mathematical problem, units, and conservation contract

Let `z_i` denote bed height, `h_i ≥ 0` water depth, `η_i = z_i + h_i` free-surface height, and `V_i` true water volume. For square plan area `A_i`, `V_i = A_i h_i` (unless introducing subgrid storage curves).

For face `e = i→j`, let `Q_e` be **signed volume flow** (m³/s), where positive means from `i` to `j`.

Continuity, integrated over a cell:

\[
V_i^{n+1} = V_i^n + \Delta t\left(\sum_{e\in\mathrm{in}(i)}Q_e - \sum_{e\in\mathrm{out}(i)}Q_e + S_i\right).
\]

The decisive software contract is **one shared edge transfer**, committed once and reflected with opposite signs in the adjacent cells. Source/sink ledgers account for external volume. Water volume and momentum/edge flux can be stored in floating point during numerical evolution, with quantized integer-dL commits; fractional remainders and volume limiting require careful design.

For current reconstruction, cell accumulation is *not* current. A steady river may have `dV/dt = 0` yet large inflow and outflow. Reconstruct velocity from **directional face fluxes / actual wetted cross section**, using agreed spatial and temporal averaging. The resulting current is *consistent with the chosen model*; conservation alone does **not** guarantee that modeled velocity is physically accurate.

### Time and performance

Report costs as **CPU milliseconds per simulated river-second at specified accuracy**. Separate:

- Active cells and evaluated edges;
- Substeps per game pulse;
- Nonlinear outer iterations;
- Linear iterations per outer iteration;
- Matrix assembly/preconditioner work;
- Integer transfer resolution/limiter;
- Cached and sleeping components;
- Render/terrain update cost (not part of solver-only timing).

Do not compare a one-pass local kernel to a 1,600-iteration implicit kernel without accounting for the local kernel's required time steps and accepted errors.

## 3. Candidate A: stabilized local-inertial shallow-water solver — PRIMARY PROTOTYPE

**Literature:** Bates, Horritt & Fewtrell (2010) [1]; de Almeida et al. (2012) [2]; de Almeida & Bates (2013) [3]; critical analysis in Cozzolino et al. (2019) [4].

### Physical approximation

Retain hydrostatic pressure gradient, local acceleration, and bed friction. **Discard nonlinear advective momentum transport**. Contrast with the pure diffusion-wave assumption, which calculates discharge nearly instantly from the current free-surface slope and friction. The local-inertial model gives edge flow *memory*.

A representative stabilized face update is:

\[
q_e^{n+1}=\frac{\widetilde q_e^n - gh_e\Delta t\,(\eta_R-\eta_L)/\Delta x}{1 + g\Delta t\,n_M^2\,|\mathbf q|_e/h_e^{7/3}}.
\]

Here `q` is discharge **per unit face width** in m²/s, `Q = b_e q` is volume discharge in m³/s, `n_M` is Manning roughness, `h_e` is hydraulic depth associated with the face, and `q_tilde` represents a stabilized weighted combination of previous nearby face discharges [2]. **This is schematic, not drop-in code**: implement wet/dry logic, face geometry, weighted momentum update, transverse/coupled friction, and stabilization from a specific published scheme. Beware division by vanishing depth.

Then convert proposed signed `Q_e Δt` into conservative face transfers, applying a nonnegative donor-volume limiter that cannot silently add water. Quantization requires maintaining fractional residuals without leaking or inventing integer dL.

### Expected computational behavior

- A small fixed number of local calculations per edge **per stable substep**; no global nonlinear system each substep.
- Simple fit for changing walls, weirs, gates, cut channels, and local rebuilding.
- Earlier flow can persist for physical reasons even if the current surface gradient is small.
- Well suited to friction-dominated rivers, spreading inundation, and most gentle backwater.

But it has a gravity-wave Courant time-step condition approximately

\[
\Delta t \lesssim \alpha\frac{\Delta x}{\sqrt{gh_{\max}}},\qquad 0<\alpha<1.
\]

For **illustration only** with `Δx = 1 m`, `α = 0.5`, 41.7 simulated seconds per pulse:

| Maximum depth | Approx. stable step | Approx. steps per 41.7-s pulse |
|---|---:|---:|
| 0.6 m | 0.206 s | 203 |
| 1 m | 0.160 s | 261 |
| 10 m | 0.050 s | 826 |

These are **not benchmarks**; use the actual cell scale, time conversion, active depths, stability condition, and scheme. A single deep cell can restrict the global step unless the method is adapted. The **2010 paper's reported maximum 1,120× speedup** applied to its own explicit diffusive comparator and is **not** an expected speedup over FlowWorks design 7 [1].

### Physical validity limits

The 2013 analysis identifies favorable conditions for lower subcritical Froude numbers, notably `Fr = |u|/sqrt(gh) < ~0.5`, but this is not a binary accuracy guarantee [3]. The model is incomplete for strong momentum advection, sharp contractions, fast jets, bores, and some hydraulic jumps. Cozzolino et al. identify fundamental difficulties at receding wet/dry fronts and discontinuous bottoms [4]. **Mandatory tests:** draining dry moat, abrupt trench excavation, gate opened onto dry bed, dam break, sharply narrowing gap.

**Prototype outcome sought:** Can this achieve acceptable flow and water-level errors with *much lower total CPU cost per simulated interval* than the repaired implicit design?

## 4. Candidate B: better implicit diffusion wave — KEEP AS CONTENDER

Design 7 is an implicit diffusion-wave/storage formulation, not unapproximated Navier–Stokes. HEC-RAS documents an analogous diffusion-wave numerical system [7–8]. Its main strengths: potentially long physical time steps and robust level/backwater behavior. Its potential weaknesses: conditioning, nonlinear wet/dry effects, iterative cost, and inaccurate rapid transients.

### Why the reported ~1,600 iterations are not decisive

For fixed positive conductance and suitably treated boundaries, the linearized water-level system resembles

\[
\left(\frac{\text{storage}}{\Delta t}+\mathcal L_{\mathrm{weighted}}\right)\boldsymbol\eta = \mathbf b,
\]

where `L` is a weighted graph Laplacian. Depending on the exact nonlinear discretization and boundary conditions, efficient preconditioned iterative and multigrid methods may apply.

**Test in order:**

1. Instrument **outer nonlinear iterations vs inner linear iterations**, residuals, matrix build, and convergence failures. Audit current stopping criteria.
2. Warm-start from the previous valid solution; measure residual before any new solve.
3. Sleep genuinely steady bodies, including **steady flowing** rivers whose `V` and `Q` fields are stable (not merely empty or disconnected water).
4. Cache connectivity, sparsity pattern, geometry, and preconditioner where valid; invalidate on terrain, barrier, or significant coefficient changes.
5. Compare sparse solvers and preconditioners (e.g., incomplete factorization, geometric/algebraic multigrid). **Conjugate gradient only if the actual matrix is SPD**; gates, one-way conditions, and full nonlinear Jacobians may violate this.
6. Try **operator/directional splitting** with inexpensive tridiagonal row/column solves, as in Artichowicz & Gąsiorowski [9]. Splitting errors and anisotropy require tests.
7. Tune solve error in physical terms: committed volume/level tolerances, discharge, and filling-time error; do not solve much more accurately than the state resolution requires.

The diffusivity/conductivity associated with Manning flow often contains `1/sqrt(|∇η|)`, which is problematic near a flat surface even though the physical discharge tends to zero. HEC-RAS discusses related regularization [8]. This may be a conditioning issue rather than evidence that a calm river intrinsically needs repeated computation.

### Caveat on huge implicit steps

Large-step numerical stability does **not** imply accurate timing. The report's **625 s versus 3,753 s** moat-fill discrepancy is unacceptable for a system where water timing has gameplay consequences. A candidate explanation is lagged wet-face geometry: HEC-RAS documents cases where lagging face areas effectively constrains flood propagation through a grid despite implicit stepping [7]. This is an **investigation hypothesis, not a diagnosis**. Compare substepping, revised geometry evaluation, full convergence, and reference transients.

## 5. Candidate C: weighted cellular automata (WCA2D / CADDIES)

Guidolin et al. (2016) [10] provide a published weighted cellular-automata model specifically for 2D inundation. It distributes water locally using hydraulic weighting, transfer constraints, and adaptive time stepping. It is considerably more defensible than an arbitrary `move 1/5 of neighbor level difference` rule.

**Benefits:** simple bounded local work, potentially strong CPU behavior, naturally conservative transfer architecture if implemented carefully, useful flooding/filling/draining. **Costs:** no full momentum conservation; velocity in rapid transients, contractions, or backwater can be less accurate than with inertia-capable schemes. It still has time-step requirements; “CA” does not imply unlimited time steps.

A published urban study reported the coupled LISFLOOD-FP comparator taking roughly 3–5 times as long as a coupled WCA2D implementation on its four-core test scenarios [11]. That is **not** a FlowWorks speed prediction and does not match every version of either model.

**Decision criterion:** If the game principally values filling and draining terrain with approximate physically meaningful currents, compare WCA2D. If precise pawn-shoving jets and fast breaches are central, expect tradeoffs.

## 6. Candidate D: virtual pipes — useful formulation, not automatically a distinct solver

O'Brien & Hodgins (1995) modeled water columns linked through virtual pipes [15]. Each connection retains a flow state, accelerated by the difference in surface head:

\[
Q_{ij}^{*}=Q_{ij}^{old}+\Delta t\frac{g A_{ij}}{L_{ij}}(\eta_i-\eta_j).
\]

Then resist/damp flow and transfer water conservatively. This maps naturally to FlowWorks' “tank per cell / edge connection” design. But pipe areas, resistance, and wet/dry behavior need physical or validated numerical meanings; ad hoc values are another tuning burden. The later graphics literature includes implicit viscosity techniques without a large global solve [16].

**Recommendation:** Use this as an intuitive *implementation model* for edge-flow memory, but derive numerical coefficients and stabilization from a documented local-inertial method. Do not count it as an independent high-priority benchmark unless the discretizations genuinely differ.

## 7. Candidate E: first-order, well-balanced full shallow-water solver — REFERENCE

A first-order finite-volume SWE implementation with hydrostatic reconstruction [5] and positivity-preserving flux limiting can represent more momentum physics than local inertia. This is particularly important for wet/dry fronts, waves, abrupt terrain, and breaches. It still requires a CFL-constrained explicit time step, and it is more complicated than the simplest local-inertial scheme.

The reported wave-kernel “false floods” in the internal twin are **specific implementation failures**, not proof that wave-carrying models inevitably false-flood. Test against analytical cases (SWASHES [17]) and lake-at-rest on nonflat terrain.

In one published multicore comparison, first-order full SWE ran around **1.5–2.5× slower** than a local-inertial model for benchmark settings [6]. This is not a general bound or a forecast for C#, but it means a competent full-SWE reference may be nearer in CPU cost than the initial report assumes.

**Reference purpose:** Identify what the cheaper approximations lose; if the difference in end-to-end CPU time is small at the target accuracy, consider full SWE for production.

## 8. Orthogonal acceleration: coarse hydraulic grid, fine bed geometry

**Subgrid bathymetry** [12–13] allows detailed bed elevations to determine storage, wet-face areas, and conveyance while the dynamic model evolves water levels over larger hydraulic cells.

For a connected aggregate of equal-area fine terrain cells with area `a`, the storage curve is

\[
V_C(\eta)=a\sum_{k\in C}\max(\eta-z_k,0).
\]

Sort elevations and precompute prefix sums to evaluate/invert this curve efficiently. In practice, face-specific geometry and connected flow pathways need equal care; volume alone is not enough.

A 2025 SFINCS study found a **100 m subgrid model could achieve comparable accuracy to a 25 m standard grid with roughly 35–50× less runtime in its test cases** [13]. At *equal* cell size, subgrid methods had added work. The savings come from using fewer unknowns and potentially larger stable steps, not a magical faster single-cell computation.

**Suggested FlowWorks policy:** retain full resolution at gates, dams, narrows, sharp bends, diggable channels, intersections, and zones where pawn current matters; use larger hydraulic aggregates for broad calm reservoirs and topographically simple regions. **Never aggregate two water regions separated by a wall into one shared water level**; preserve hydraulic connectivity. Coarse levels do not automatically give physically correct high-resolution velocity fields.

**Sequencing:** First establish solver accuracy/performance on a uniform grid. Then add aggregation as an independently measurable optimization, not simultaneously with a new flux law.

## 9. Supplemental techniques and non-solvers

### Fill–Spill–Merge

Barnes et al. (2021) [18] compute how water fills interconnected depressions efficiently using a hierarchy of basins and spill elevations. Useful for **initial state, basin bookkeeping, storage groups, or equilibrium targets**. Does *not* supply dynamic travel times and local currents by itself.

### Kinematic wave

Simple and fast for runoff primarily governed by downhill terrain slope, but discards backwater effects and is a poor universal engine for reservoirs, dams, and pits connected to rivers.

### Lattice Boltzmann

Published shallow-water LBM variants exist [19]. They replace some macroscopic calculations with directional populations or more specialized macroscopic schemes. They are not automatically cheaper on the target CPU, have their own stability regime, and are lower-priority than the candidates above for this project.

### Sleeping and cache reuse

A steady river can have **unchanged depth and nonzero continuous discharge**. Sleep only when (1) hydraulic boundary conditions and topology are unchanged, (2) governing residuals are acceptable, (3) flux state is stable, and (4) the storage/flow bookkeeping remains correct. Wake from terrain change, gate change, upstream/outlet change, rain/source change, new connection, or residual growth. Empty/dry components can be skipped. Reusing a settled flow field must account for integer residual accumulators and source/sink ledgers.

### Low-level CPU work

Neal et al. (2018) [14] reported roughly **4.2–8.4× single-core improvement** from architecture and algorithm optimizations including reducing dry-cell operations, memory work, and vectorization. These improvements may be available regardless of solver selection. Benchmark actual C# memory layout (separate contiguous arrays for elevations, volumes, and edge state vs object-heavy cells).

## 10. Corrections to the current report's assumptions

These are **analysis and deductions**, not offline-twin measurements.

### 10.1 Directional Manning friction can cause an exact 18.9% idealized error

If independent axiswise Manning laws use `q_x ∝ sign(S_x) sqrt(|S_x|)` and the same for `y`, then on a uniform slope at 45° the computed speed magnitude is `2^(1/4) ≈ 1.1892` times the isotropic-vector formulation. That is an **18.9% excess for this idealized calculation**, not an error bound for rotated rasterized channels. Treat `~19%` as a diagnostic clue, not unavoidable grid anisotropy. Use a coupled vector magnitude/friction law and benchmark radial spreading plus 0°/45° channels [3, 20].

### 10.2 Flat storage does not prohibit current reconstruction

The original pool-plus-field idea ignored time-changing storage. The continuity condition is

\[
\nabla\cdot(h\mathbf u)=s-\frac{\partial h}{\partial t}.
\]

A reduced pool model could reconstruct internal fluxes *consistent with* storage accumulation, but needs a hydrodynamic closure (resistance/momentum) and typically a field solve. That provides an alternative avenue for large, calm bodies, **not proof the discarded prototype was already correct**.

### 10.3 Conservation != hydraulic accuracy

Moving every decilitre exactly does not guarantee realistic wave timing, discharge, fluid velocity, or shoreline behavior. Likewise deriving current from transferred water guarantees internal bookkeeping consistency, not an accurate velocity closure. Benchmark level, discharge, current, and wet/dry front speed separately.

### 10.4 Lake-at-rest and monotonicity are different acceptance conditions

The report rejects **any cell rising above the prior neighboring max without a source**. That monotonicity criterion can suit a diffusion model, but **physical inertia can pile water up against obstacles or create sloshing**. Instead require correct no-source conservation, no spurious spontaneous flooding in lake-at-rest tests, nonnegative depth, and agreement against an appropriate transient reference. Do not reject physically valid inertial overshoot by design.

### 10.5 `sqrt(gh)` is a wave speed, not a universal max water velocity

A hard `|u| ≤ sqrt(gh)` cap enforces a subcritical-flow restriction and can suppress legitimate supercritical jets. It may be chosen as explicit *gameplay simplification*, but not justified as a universal physics law. Conservative positivity checks, suitable numerical fluxes, and CFL requirements are different safeguards.

### 10.6 The upstream fixed-stage boundary can still create backwater

A held upstream stage prevents unbounded upstream rise past that fixed boundary, but **does not make impoundment everywhere impossible**. It can still produce a reservoir and elevated water levels in portions of the river upstream of a dam. Compare fixed-stage, fixed-discharge, and stage-responsive source laws with actual experiments.

### 10.7 “Never iterate edge depth” is overly general

The internal report observed a failed particular nonlinear edge-depth iteration. That failure does not show all geometry iterations are invalid. Decide whether to lag or update wet-face area and conductance based on a consistent formulation and convergence analysis; measure transient timing and positivity.

### 10.8 “Stable at any pulse length” is not “correct at any pulse length”

An implicit scheme may remain bounded for very large steps while giving dramatically wrong filling time. FlowWorks already observed that. Require **temporal convergence** at a declared gameplay tolerance; adaptive substepping can reduce error, but must be weighed against computational cost.

## 11. Benchmark plan for Claude Code

### 11.1 Keep the public solver interface fixed

Proposed abstraction, not an API prescription:

```text
HydraulicState:
  bed_height[cell]                 # static until terrain edit
  committed_water_dL[cell]          # integer conservative ledger
  working_volume_or_depth[cell]     # numerical state
  edge_flow[edge]                   # signed; persistent for inertial/SWE
  edge_fractional_carry[edge]       # quantization residual if needed
  edge_kind_and_structure[edge]     # open/wall/weir/gate + parameters
  upstream_and_downstream_BC        # policy specified by game

Solver.advance(simulated_dt, changed_cells, changed_boundaries):
  -> committed transfers, current field, diagnostics
```

Define **cell width in metres**, seconds per game tick, Manning roughness units, source discharge units, and exact definition of current used for pawn motion before comparing algorithms. A visually acceptable current multiplier is a separate gameplay parameter.

### 11.2 Prototype arms

- `A`: documented stabilized local-inertial scheme with coupled vector friction and conservative positivity treatment [2–4].
- `B0`: current implicit v3 baseline; preserve exact existing output.
- `B1`: instrumented, warm-started, residual-aware implicit scheme; then compare preconditioner / split-line alternative [7–9].
- `C`: documented WCA2D-style update [10].
- `R`: reference first-order well-balanced SWE [5–6, 17].

Do **not** combine new solver + coarse grid + altered boundaries in one experiment. Control each variable so performance and accuracy are attributable.

### 11.3 Discriminating scenes, in proposed order

1. Closed, irregular-bed lake at rest (zero spurious momentum and volume drift).
2. Plain steady river, including 0° and 45° reaches, plus radial spreading (directional symmetry).
3. Narrow 12→3→12 gap at steady and transient flow (contraction and backwater).
4. Weir, adjustable gate, and full dam (structure laws and closure).
5. Side canal to filling moat, then isolated/draining moat (storage timing and recession).
6. Gate opening onto dry terrain; wet-bed and dry-bed dam breaks (front velocity, positivity, momentum).
7. A dam built/demolished in water (displaced water accounted for, no deletion).
8. Two rivers joining; river to sea; isolated pits; frozen boundaries.
9. Unchanged *flowing* river for thousands of pulses (settled CPU burden).
10. 1,000 randomized construction sequences with terrain and boundary perturbations (ledger/invariants).

Use analytic cases from **SWASHES** [17] where possible, and a refined trustworthy numerical reference elsewhere. Compare **volume, levels, flux, velocity, wet/dry area, front-arrival time, and runtime**. For formula-based weirs validate both free and submerged regimes.

### 11.4 Required diagnostics

For each scene/solver publish:

| Dimension | Required measurement |
|---|---|
| Conservation | Exact committed dL ledger error, plus uncommitted numerical residue |
| Positivity | Minimum volume/depth, limiter activity, any rejected step |
| Temporal fidelity | Fill time and front-arrival sensitivity under 2×/10× step refinement |
| Hydraulic fidelity | Depth and stage error, flux error, velocity/direction error, rotated-grid error |
| Cost | CPU ms per fixed simulated interval, total edge updates, substeps, iteration counts |
| Settled efficiency | CPU per pulse at unchanged nonzero flow / disturbed pulse |
| Event handling | Build/remove dam, gate reopen, basin split/merge |
| Reproducibility | Fixed input state → repeated output; cross-runtime bit identity if required |

Measure at source-report sizes ~3,000 / 13,000 / 62,500 wet squares; keep terrain and forcing identical between candidates. Test with appropriate simulated time step, rather than blindly requiring a solver to take an unstable giant explicit step. Report errors at a **comparable accuracy budget**.

### 11.5 Gates to adopt a production solver

1. Correct conservation/positivity on all specified construction events.
2. Acceptable water-stage and dynamic-current behavior in gameplay-critical scenes.
3. Defined temporal error tolerance met by 2× timestep refinement (not merely final-level convergence).
4. Settled components cheaply bypass unnecessary updates while preserving persistent current.
5. Measured C# performance at 13k and 62.5k wet squares fits game-thread budget; otherwise tune scheduling or water-time scaling explicitly.
6. Shader/terrain repaint costs isolated from solver costs.
7. Explicitly document where physics is sacrificed for gameplay.

The internal report proposed <10% fill-time difference, <5% settled-versus-disturbed cost, and 0 dL ledger drift over 100k pulses. Treat these as **provisional project acceptance targets**, not literature-derived requirements. The report's absolute no-overshoot rule should be replaced by a physically meaningful reference test (see §10.4).

## 12. Open decisions requiring product input (not numerical conclusions)

1. **Upstream boundary behavior under impoundment:** fixed water level, fixed inflow, or a declining discharge with backwater stage. Different policies produce fundamentally different reservoirs. The report currently favors a stage-responsive discharge rule, not yet tested.
2. **Current-to-pawn-shove conversion:** physical model speed vs game feel multiplier. Keep the water simulation's units separate from animation/shove tuning.
3. **Waves:** purely visual surge vs solver-produced inertial waves. Visual surge must not alter conserved water or pawn shove without explicit mechanics.
4. **Disturbance latency:** brief frame hitch, scheduled work across ticks, or slower in-game water clock; do not silently advance water without consistent current, sources, and animations.
5. **Displacement when building structures in wet water:** conservative push-aside vs prohibit placement beyond a depth limit.

## 13. Literature and reference links

Bibliographic details/links below were assembled in the research discussion. **Do not treat linked article speedups as transferable predictions for RimWorld.** DOI and publisher versions are preferred where known.

1. **Bates, P. D., Horritt, M. S., & Fewtrell, T. J. (2010).** “A simple inertial formulation of the shallow water equations for efficient two-dimensional flood inundation modelling.” *Journal of Hydrology*. https://doi.org/10.1016/j.jhydrol.2010.03.027
2. **de Almeida, G. A. M., Bates, P., Freer, J. E., & Souvignet, M. (2012).** “Improving the stability of a simple formulation of the shallow water equations for 2-D flood modeling.” *Water Resources Research*. https://doi.org/10.1029/2011WR011570
3. **de Almeida, G. A. M., & Bates, P. (2013).** “Applicability of the local inertial approximation of the shallow water equations to flood modeling.” *Water Resources Research*. https://doi.org/10.1002/wrcr.20366
4. **Cozzolino et al. (2019).** Critical study of local-inertia equations, wet/dry fronts and discontinuities. https://arxiv.org/abs/1904.12564
5. **Audusse, B., Bouchut, F., Bristeau, M.-O., Klein, R., & Perthame, B. (2004).** “A fast and stable well-balanced scheme with hydrostatic reconstruction for shallow water flows.” https://publications.imp.fu-berlin.de/478/
6. **Shaw et al. (2021).** Multi-core flood-model evaluation comparing local-inertial and first-order full shallow-water methods. *Geoscientific Model Development*. https://gmd.copernicus.org/articles/14/3577/2021/
7. **USACE HEC-RAS Hydraulic Reference.** “Numerical Methods — Diffusion Wave Equation Solver.” https://www.hec.usace.army.mil/confluence/rasdocs/ras1dtechref/6.4/theoretical-basis-for-one-dimensional-and-two-dimensional-hydrodynamic-calculations/2d-unsteady-flow-hydrodynamics/numerical-methods/diffusion-wave-equation-solver
8. **USACE HEC-RAS Hydraulic Reference.** “Diffusive Wave Equation” (including low-slope behavior). https://www.hec.usace.army.mil/confluence/hecras/beta/technical-reference/hydraulic-equations/diffusive-wave-equation
9. **Artichowicz, W., & Gąsiorowski, D. (2019).** “Computationally Efficient Solution of a 2D Diffusive Wave Equation Used for Flood Inundation Problems.” *Water*. https://www.mdpi.com/2073-4441/11/10/2195
10. **Guidolin et al. (2016).** “A weighted cellular automata 2D inundation model for rapid flood analysis.” *Environmental Modelling & Software*. https://doi.org/10.1016/j.envsoft.2016.07.008 ; CADDIES project: https://www.exeter.ac.uk/research/centres/cws/resources/caddies/
11. **Urban-flood coupled-model comparison (2022).** WCA2D/SWMM against LISFLOOD-FP/SWMM. *International Journal of Disaster Risk Science*. https://link.springer.com/article/10.1007/s13753-022-00416-3
12. **USACE HEC-RAS.** “Subgrid Bathymetry.” https://www.hec.usace.army.mil/confluence/rasdocs/ras1dtechref/6.4/theoretical-basis-for-one-dimensional-and-two-dimensional-hydrodynamic-calculations/2d-unsteady-flow-hydrodynamics/subgrid-bathymetry
13. **van Ormondt et al. (2025).** SFINCS subgrid corrections and computational performance. *Geoscientific Model Development*. https://gmd.copernicus.org/articles/18/843/2025/
14. **Neal et al. (2018).** “Optimisation of the two-dimensional hydraulic model LISFLOOD-FP for CPU architecture.” https://research-information.bris.ac.uk/en/publications/optimisation-of-the-two-dimensional-hydraulic-model-lisfood-fp-fo/
15. **O’Brien, J. F., & Hodgins, J. K. (1995).** “Dynamic Simulation of Splashing Fluids.” https://objf.ai/papers/Obrien-DSS-1995-04/Obrien-DSS-1995-04.pdf
16. **Dagenais et al. (2018).** Implicit viscosity for a virtual-pipe water model. https://profs.etsmtl.ca/epaquette/Research/Papers/Dagenais.2018/
17. **SWASHES:** Analytic shallow-water benchmarks and reference test cases. https://www.idpoisson.fr/swashes/
18. **Barnes, Callaghan, & Wickert (2021).** Fill–Spill–Merge depression filling. *Earth Surface Dynamics*. https://esurf.copernicus.org/articles/9/105/2021/
19. **Shallow-water lattice-Boltzmann methods (2022).** *Water*. https://www.mdpi.com/2073-4441/14/13/2065
20. **Cozzolino et al. (2020/2021).** Analysis of rotational-invariance errors from directionally decoupled friction. https://arxiv.org/abs/2009.11188
21. **Landlab de Almeida overland-flow component source/documentation.** Concrete implementation of time-step considerations. https://landlab.readthedocs.io/en/latest/_modules/landlab/components/overland_flow/generate_overland_flow_deAlmeida.html

## 14. Suggested immediate task for the next Claude session

> Read `FINAL_REPORT.md` and this review. Preserve FlowWorks' exact-volume cell/edge accounting. First instrument the existing Python implicit v3 solver to explain the ~1,600 settled iterations and the pulse-dependent moat-fill time. In parallel, implement a **separate** stabilized local-inertial Python twin using a published de Almeida formulation with coupled friction, careful wet/dry handling, conservative donor limiting, and no hidden source of mass. Run identical lake-at-rest, river, rotated-channel, gap, dam, weir, canal/moat, and gate-breach tests. Compare end-to-end CPU time *for matched hydraulic accuracy*, including substeps and book-keeping. Use a well-balanced first-order shallow-water reference on the most disputed transients. Report measured outcomes and explicit failures; do not implement in C# until the numerical tradeoff is resolved.

**Bottom line:** Choose the conservation **architecture** now, but select the numerical **engine** empirically. The leading experiment is local inertia versus a properly optimized implicit diffusion wave, with full shallow-water physics as an accuracy reference and subgrid/storage caching as independent later accelerations.
