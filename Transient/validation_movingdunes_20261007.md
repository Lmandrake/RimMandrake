# MovingDunes validation (Approach B), 2026-10-07 - DONE, nothing committed

## Kernels (Verse-free, `src/RimMandrake/MovingDunes/Source/Kernel/`, both in RimMandrake_MovingDunes.csproj; mod code calls them)
- `RM_DuneKernel.cs` - the sand-grid engine behind an `IDuneField` interface (the real grid via new `MapDuneField.cs`, an array in the fuzz): `RunTransport` (Werner slab: erode, wind-shadow, hop, deposit-prefers-low, roof/wall banking, leeward loss, in-place restore), `SetDepthHysteretic`, `RunInflux` (windward source/sink with debt, cap, band, bounded work), wind shift/schedule, storm factors, wind-lock gate, attempts/choke scaling. `MapComponent_DuneField` is now orchestration only.
- `RM_CacheKernel.cs` - burial crossing, bury gate + per-map cap, burial candidate predicate, absorb tick, reveal depth, accept rule. `DuneBurialUtility`, `Thing_BuriedCache`, `TryBuryAt`.
- `DuneWindBearing.cs` was already pure; it is compiled into the fuzz as is.
- Rejected (engine calls): SectionLayer_DuneSand (mesh rendering), Patch_SandGrid (Harmony prefixes on engine methods), Thing_BuriedCache's ThingOwner transfers, MovingDunesMod bootstrap, debug actions, MovingDunesProof (bridge hooks).

## Fuzz
`python3 src/RimMandrake/Utils/selftest_movingdunes_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only transport|influx|wind|cache]` (project `Source/SelfTest/RimMandrakeMovingDunes.SelfTest.csproj`).
- transport (TOP INVARIANT, mass conservation): on random fields with roofs, walls and cells that cannot hold sand, with the boundary nudge off the whole field after every batch EQUALS an independent single-slab oracle exactly, and `total after - total before == -Lost + DepositError - ErodeError + InPlaceDelta` (so every grain is accounted: leeward loss, deposits, refused/clamped sand, erosion, in-place restore); depth never leaves [0,max]; roofed cells never change; walls never hold sand; a slab never lands on a wall or under a roof. With the nudge on: erosion error bounded by the hysteresis, and no changed cell rests inside the boundary band. Closed-field unit: 40x30 attempts, running total never drifts from the ledger.
- influx: debt never negative, bounded work per batch, sand only in the windward band, only added, never under a roof or on ground that cannot hold it, `gain > 0` iff something was placed (a refused cell is not sand), at the mass cap nothing is placed and the debt is cleared, debt == previous + delta - q*placed; cold start receives sand; dead calm brings none; the drift slider scales only the flat baseline, once.
- wind: shifts are +-1/2 on the 8-point circle, next shift in the future, lock gate truth, storm-factor table, attempts monotone and >= 1, choke damage == hp/(days*visits), DuneWindBearing against a vector-geometry oracle on random points, wind-away is opposite wind-toward, compass points.
- cache: bury gate and cap == spec, crossing verdicts, ITEM CONSERVATION (ground + buried == created, no item twice, no empty cache), absorb keeps the older tick, reveal at depth <= revealDepth, exhaustive 2048-row candidate table.
- Seeds: 1500 transport/influx, 3000 wind/cache, 4 s. `--fuzz-scale 20`: 180,000 cases, 4.8M steps, 62 s, 0 failures (3.2M slab moves, 447k leeward, 2.8M influx slabs, 75k buries, 1.9k reveals). Blind check on every transition.

## Mutation (26 planted, 26 caught, restored byte-identical)
`python3 src/RimMandrake/Utils/mutate_kernel_fuzz.py selftest_movingdunes_fuzz.py src/RimMandrake/Utils/mutations_movingdunes_fuzz.json`. Planted: leeward loss uncounted / doubled, slab deposited twice, erosion takes half, in-place slab not put back, walls do not shelter, roofed cells erode, low-cell margin lost, nudge toward the boundary, cap doubled, influx on the wrong edge, double debt spend, a refused cell spends the debt (first NOT caught, drove the `gain > 0 iff placed` check and the lake unit), the squared drift-slider bug, wind wraps on 4 points, lock ignores flag, calm counted as storm, attempts/damage reach 0, wind blows the wrong way, bearing loses the latitude scale, re-bury on every deposit, cap blocks merging, younger burial wins, reveal one hair deep, unhaulable buried.

## Lint
`python3 src/RimMandrake/Utils/lint_movingdunes_defs.py`: 2 defs + 1 patch, 28 classes, 7 refs, 7 settings: 0 ERROR, 0 WARN. 5 planted defects caught (def type typo, csproj omission, missing Scribe, default mismatch, DefOf typo).
- Shared lint fix (`lint_mod_defs.py`): a namespaced def tag (`<RimMandrake.MovingDunes.RM_DuneMaterialDef>`) now keys as its type `RM_DuneMaterialDef`; before, `defof-resolves` falsely reported RM_Dunes_Sand missing (the committed baseline also errored). Wasteland / WeepingStones / Greentide / LeaningScrub lint output unchanged.

## Defects
- None that change shipped behaviour in the extracted logic: the squared drift-slider fix recorded in `InfluxDebtDelta`'s comment is correct and now locked by the fuzz.
- NOTE (design, measured by the oracle) sand that hops onto a cell that cannot hold sand (water; the `CanHaveSand` rule) is deleted: the landing refuses it, `Lost` counts only the leeward edge, so influx never replaces it. A dune field beside a lake slowly loses mass to it. Probably "sand sinks into the lake"; say so if influx should replace it, or make a non-holding cell bank like a wall (`landing = prev`).
- NOTE a slab landing on a cell within 0.03 of `MaxDepth` loses the overflow the same way.
- NOTE eroding then restoring a cell in place re-applies the boundary nudge, so an untouched-looking cell can move by up to 0.012 (tracked as `InPlaceDelta`).

## Repairs to existing tooling (my refactor broke text scans)
`validation.py` `USES`/`load_sources` and `selftest_movingdunes_proofs.py` scanned `MapComponent_DuneField.cs` for the inline `influxDebt += InfluxDebtDelta(` and `if (!MovingDunesSettings.burialEnabled)`. They now read `Kernel/RM_DuneKernel.cs` and a `bool burialOn = MovingDunesSettings.burialEnabled;` line. `selftest_movingdunes_proofs.py` PASSES again.

## Build
`winbuild.py src/RimMandrake/MovingDunes/Source/RimMandrake_MovingDunes.csproj` -> 0 warnings 0 errors; `Assemblies/RimMandrakeMovingDunes.dll` + `.srchash` rebuilt, UNCOMMITTED. Not wired into run_selftests.py.
