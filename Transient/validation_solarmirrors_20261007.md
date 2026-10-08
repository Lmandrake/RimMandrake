# SolarMirrors validation (Approach B), 2026-10-07 - DONE, nothing committed

Sizing: 1585 lines, ~560 of them non-engine (beam maths + the whole relay pass); the rest is comps, UI, Harmony-free engine plumbing. Done because the pass is a pure relay graph over a grid.

## Kernel (Verse-free, `src/RimMandrake/SolarMirrors/Source/Kernel/RM_MirrorKernel.cs`, in RM_SolarMirrors.csproj; the mod calls it)
- Maths on a float `RM_Vec` (no UnityEngine): sun vector, moving sun, normal, cosine law, reflect, ground hit, 4-connected beam walk, quantise, hysteresis, reflectivity, pass-interval / depth-cap clamps, daylight, blind gain, NormalFor.
- `RM_MirrorKernel.Pass`: the whole light pass (collectors -> shots -> relays, acyclic, depth-capped, relay share per footprint cell) over an abstract `IRM_BeamWorld`, plus the change hash.
- `RM_MirrorMath.cs` is now a Vector3 facade over it (one implementation). `RM_MapComponent_MirrorLight` builds `RM_MirrorSpec`s from the comps, runs the pass, writes results back (`last*`, committed normal for tracking heliostats). `RM_CompMirror.Reflectivity` uses `RM_MirrorKernel.Reflectivity`.
- Rejected as kernels: RM_CompMirror gizmos / targeter / inspect string, RM_CompLightReceiver (3 lines over Hysteresis), RM_ReAimMirror (WorkGiver/JobDriver), RM_SolarMirrorsMod (settings UI), TickBlinding/rendering (pawn lists, Graphics.DrawMesh): engine calls.

## Fuzz
`python3 src/RimMandrake/Utils/selftest_solarmirrors_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only math|pass|sequence]` (project `Source/SelfTest/RimMandrakeSolarMirrors.SelfTest.csproj`).
- math: sun unit/height/opposite shadow, moving sun (night, rise east / set west, noon elevation 90-|lat|, equatorward lean, morning/afternoon mirror image), Reflect(in, Normal(in,out)) == out, n.s == sqrt((1+s.t)/2), back face passes nothing, ground hit on the ray within range, beam walk (strictly-between cells, 4-connected, in bbox, within a cell of the line, blocked cell stops it), hysteresis state machine, quantise, reflectivity, clamps, daylight, blind gain, NormalFor commit only when tracking.
- pass: random worlds (roofs, walls, closed doors, mirrors size 1-2, targets half on other mirrors) -> every field of every mirror result and the whole light grid == an independent reference pass; invariants: light conserved (grid total == sum delivered x lit cells), no light on a roof/wall/closed door (own footprint excepted), fire-once, depth < cap, no delivery above the input, relay input <= light delivered upstream, no shots with sun down / effects off, idempotent second pass, change hash reacts to 2 quanta and ignores jitter inside one.
- sequence: add / remove / re-aim / build / sun / chain / night actions on ONE persistent pass: equals a fresh pass after every run (nothing stale), PrevLitCells == last pass's lit set.
- Seeds: default 4000 / 4000 / 1500 (0.6 s). `--fuzz-scale 25`: 237,500 cases, 1.47M steps, 5.7 s, 0 failures. Blind check: relays, deep chains, blocked, sky/edge misses, commits, big spots, mutual-aim cycles, targeted/untargeted, night, idempotent must all be reached.

## Mutation (23 planted, 23 caught, all restored byte-identical)
`python3 src/RimMandrake/Utils/mutate_kernel_fuzz.py selftest_solarmirrors_fuzz.py src/RimMandrake/Utils/mutations_solarmirrors_fuzz.json`. Two first-draft mutants were EQUIVALENT (the fire-once guard is redundant with the per-depth filters; the cell-count term in the hash) and were replaced by real ones (relay direction reversed, hash ignores light). Others: efficiency without the half, back face passes light, range ignored, walk tests target/origin cell, hysteresis inverted, relay floor/share, depth cap +1 / unclamped, even spot centred wrong, daylight early, blind gain uncapped/threshold, reflectivity uncapped, non-tracking commits, stale light kept, own footprint blocks own beam, off-map target accepted, moving sun sets east.

## Lint
`python3 src/RimMandrake/Utils/lint_solarmirrors_defs.py [--quiet]`: 3 defs, 18 classes, 8 refs, 5 field checks, 1 driver, 11 settings: 0 ERROR, 0 WARN. 5 planted defects caught (class typo, field typo, csproj omission, missing Scribe, default mismatch).

## Defects
- None that change shipped behaviour. NOTE: a mirror aimed at its own footprint lights it even under a roof (own footprint is exempt from blocking); harmless, left as designed.
- Wrote the oracle independently of the kernel loop and it agreed on 100,000 cases, so no hidden drift from the extraction.

## Build / regressions
`winbuild.py SolarMirrors/Source/RM_SolarMirrors.csproj` -> 0 warnings 0 errors; DLL + .srchash rebuilt, UNCOMMITTED. `SolarMirrors/validation.py` STATIC PASS (it pins structure of the component, not the moved maths; its Python mirror of SunVector/Efficiency stays valid). `run_selftests.py`: 278/279; the one failure is `selftest_swbestiary_fuzz.py` (kiln, another builder's mod in progress), nothing pinned SolarMirrors source text.
