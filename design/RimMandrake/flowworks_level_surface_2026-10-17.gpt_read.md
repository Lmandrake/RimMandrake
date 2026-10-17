The current ruling confuses **excavation resolution, water quantity, and water surface height**. They do not need the same unit. Half-metre digging can stay. Half-metre increments of water **per square** cannot reliably produce a level surface.

The flow bug explains gross patterns such as `0,4,0,0,4`; fixing it cannot remove the representation’s inherent staircase.

**1. What whole notches can achieve**

On a common floor, write \(W=Nq+r\), where \(0≤r<N\). The best integer distribution gives \(r\) squares \(q+1\) notches and the others \(q\). Unless \(r=0\), their surfaces differ by **0.5 m**.

For the flat 3×3 pond holding 26 of 36 notches:

- \(26=9×2+8\): eight squares hold 3 notches, one holds 2.
- Depths are eight at **1.5 m**, one at **1 m**.
- The physically level answer is \(26,000÷(9×2,000)=\mathbf{1.4444\ m}\) everywhere, with the surface 0.5556 m below ground.

Three dry squares beside six full squares is worse than the best integer answer. Nevertheless, even the best answer has a half-metre discontinuity. A finer integer step shrinks this error; it does not eliminate it.

Assume a common ground datum and join this pond to a canal whose floor is 0.5 m below ground. At 26 notches, the level pond surface is **below the canal floor**: no gravity flow is correct.

Now start the pond full, with 36 notches, and attach ten such canal squares. Let \(h\) be surface elevation relative to ground:

\[
36,000=2,000[9(h+2)+10(h+0.5)].
\]

Thus \(h=-5/19=-0.2632\) m. Pond depth is **1.7368 m**; every canal square holds **0.2368 m**.

The spec’s “never all ten wet” conclusion is an integer-model artifact. All ten can be wet; they cannot all be brim-full. Even one full pond square connected to ten canal squares can wet all ten at **4.55 cm**, assuming an unobstructed connection.

**2. Four representations**

The following costs are algorithmic estimates, not timings. A 250×250 map contains 62,500 cells and about 124,500 internal cardinal edges.

**A. Exact volume per hydraulic region; derived common surface — recommended first**

Keep byte excavation and bed grids. Store authoritative **`long` decilitres per region**, a derived `double` surface elevation, and an `int` region-ID grid, about 250 kB. Integer-notch totals could also produce fractional surfaces, but decilitres already match the equipment.

Solve:

\[
V=2,000\sum_i\max(0,H-z_i)
\]

in litres, subject to basin boundaries and spill elevations. Floors are \(z_i\); depths are computed from the resulting \(H\). With half-metre floors, a histogram has at most 251 floor elevations. Building it costs O(M); solving it costs O(B). Cache unchanged geometry.

Conservation belongs to the integer volume ledger. The computed depths need not individually round to decilitres and must never be rounded and summed back into stock.

Migrate canal fill as `oldFill × 10,000 dL`; convert pond stock using its saved unit definition. Preserve fractional legacy stock through an explicit rounding policy and record the migration difference.

Main risks: instantaneous equalisation through long narrow canals, and incorrect region membership. **Geometric connectivity alone is insufficient:** two basins connected above the current surface cannot share one height. Drawdown may split regions; rising water may merge them.

**B. Finer fixed-point water per cell**

Use 0.1 m/200 L or 1 cm/20 L units. A `ushort` covers 125 m at either resolution: **125 kB** for a whole-map water grid. Excavation and bed grids can remain half-metre bytes; there is no requirement to rescale geometry.

Use a bulk equalisation solve, assigning quotient and remainder units. Conservation remains exact integer arithmetic. Carry sub-unit pump/burn residuals rather than discarding them.

Migration multiplies old fills by 5 or 50; convert pond totals consistently. This is one versioned conversion, not inherently five times the migration effort.

Likewise, **five times the flow work is not inherent**. It follows from moving one quantum per operation. Bulk transfers avoid that multiplier.

Risk: the staircase remains—10 cm or 1 cm—and tiny volumes still concentrate into selected cells. Extra resolution does not fix broken connectivity.

**C. Per-cell continuous volume with local relaxation**

Store `float` litres or `int` decilitres per cell: **250 kB**, commonly another buffer of similar size. Decilitres give 0.05 mm depth resolution in one square; 16-bit decilitres cannot hold deep lakes.

Compute neighbouring surface differences and transfer volume toward equilibrium. Bound simultaneous outflows by available water and apply transfers consistently. Each sweep examines about 125,000 edges; \(k\) sweeps cost O(kM). Long canals can converge slowly, and aggressive updates can oscillate.

Integer transfers conserve exactly. Floating-point transfers need a stated error tolerance and accounting; equal-and-opposite updates alone do not establish exact global conservation.

Migration can initialise each old filled cell directly and distribute pond stock using a surface solve. The main attraction is visible propagation and local interactions. The main risk is spending many pulses approaching the flatness the owner wants immediately.

**D. Basin reservoirs connected by hydraulic links**

Store volume and derived height per basin, with links carrying crest elevation and flow limits. Cells reference a basin. Transfer water between basins according to head difference and link conductance; merge freely communicating reservoirs when appropriate.

After geometry construction, pulse work is O(number of basins + links), plus affected-cell reads/rendering. Topology rebuilds can require whole-map work.

Integer link transfers give exact conservation. Migration starts from the same legacy volumes and basin construction as A.

This preserves flat lake surfaces while allowing restricted flow through channels and gates. Its principal cost is implementing and validating splitting, merging and spill relationships. It is a strong eventual model if instantaneous region-wide redistribution proves objectionable.

**Shared integration requirements**

All four should expose one authoritative API: surface, floor, water depth, available volume, and intake accessibility.

Pumps withdraw only accessible water and deposit volume; their existing 1,000 L pour can remain. That pour still creates a temporal jump—5.56 cm over nine wet cells—so smooth animation or smaller pours may be needed separately.

Burn/evaporation removes volume using elapsed time and burning/wetted area, with fractional-rate accumulation. Heat uses actual water mass and an explicit mixing assumption. Pit excavation stays 2 m; water-dependent trap behaviour reads actual water depth. Canal joins compare surface and connection elevations. **Gameplay must never read delayed terrain pictures as water truth.**

Four terrain bands can remain a depth legend, but they cannot convey continuously changing depth or shoreline position. Define a visible state for **0 < depth < 0.5 m**. A blended overlay or shader is needed if smoothness includes appearance; interpolate rendering between slow pulses. Do not interpolate authoritative gameplay state. Full-cell columns also retain tile-shaped shorelines unless partial coverage is added.

**3. Recommendation and ASAP order**

Choose **A with exact decilitre totals**, retaining half-metre floors and digging. It achieves level equilibrium without fine water grids. Treat correct basin connectivity as part of the solver.

Order:

1. Let the separate flow fix land; establish measured surface-error diagnostics.
2. Build the common-height solver and volume/depth API. Remove whole-square recession from truth.
3. Verify the numerical examples above, unequal floors, tiny withdrawals, canal closure, and basin splitting/rejoining. Existing conservation tests establish only part of correctness.
4. Integrate pumps, heat, burn and traps; migrate old saves with volume audits.
5. Show the owner actual output. Add continuous rendering where discrete terrains still obscure the result.

I would move toward D if bottlenecks or visible travel time matter. I would choose C if local flowing behaviour justifies its convergence cost. I would accept B if measured 1 cm errors are visually sufficient and it ships substantially sooner. Benchmark pulse cost and worst-case settling; the supplied day estimates do not establish either.

**4. Rulings to reopen**

- One integer quantity unit must equal one square’s depth step.
- Water amount must be stored in whole notches per square.
- Recession must dry whole squares while leaving others full.
- Four discrete terrains suffice for smooth-looking water.
- A permanent pond identity remains one hydraulic body after drawdown or excavation.
- One `float` stock is the appropriate authoritative ledger.
- Finer resolution necessarily multiplies flow work by five.
- The integer S5 examples describe physical gravity limits.