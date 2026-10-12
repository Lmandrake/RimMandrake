# WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME — 2026-10-12

## Symptom
Live 2026-10-12c (`Transient/bench_live_20261012c/ext_river.json`): `BREACH heldBefore=3 heldAfter=3 at=(112,0,52)`.
Wet cell neighbourhood: `wetCell=112,52 wetDir=6 nbr=1,0:-1|1,1:-1|0,1:6|-1,1:6|-1,0:6|-1,-1:-1|0,-1:-1|1,-1:-1`
(the wet cell flows S; S/SE/SW/E carry no flow; only N, NW, W do, all S).

## Cause
Not a code regression. `RM_Building_BankWeir.WashCatch`'s walk + strand are unchanged since the 2026-10-05 move
(3643347505); 137743f756/404e1b3074 only moved the per-stack placement into `WashHeld`, and 7a2a9c425c touched the
pool (UpstreamWalk) and proof diagnostics, not the wash. What changed is the SITE: ec13854219 (river_site prefers fish
biomes) put the proof weir on tile 60145 at (112,52) instead of the 2026-10-06 z=12 bank edges. The latent bug:
the walk follows the wet cell's quantised direction blindly and stops at the first no-flow cell (here after one step,
onto bank), then strands on the nearest no-flow standable cell to that end — (112,51), inside the weir's own 2.5-cell
`HeldCatchRadius`; nothing kept the strand outside the disc. Offline, the pre-fix rule strands the catch "home" on
645 of 1988 synthetic bank-edge weir sites.

## Fix
`RM_RiverMath` (Verse-free): `DownstreamStep` (UpstreamStep's mirror; both now share `AlignedStep`, best-aligned
in-flow neighbour within ~67.5°), `DownstreamWalk`, and `WashStrand`: walk `breachWashCells` downstream, then strand
on the nearest standable no-flow cell to the walk end that is farther than `HeldCatchRadius + 1.5` from the weir AND
downstream within 45° of the wet cell's flow (along >= across, along >= 1); fallback any cell outside the disc.
`WashCatch` calls it with `Position` and `HeldCatchRadius`.
Known limit: Near placement spilling past the strand's first ring (all neighbours occupied) can still land closer.

## SelfTest
`src/RimMandrake/FlowWorks/Source/SelfTest/RiverWashChecks.cs`, 4 `WeirBreach_*` cases: the live 3x3 scene (old
strand (0,-1) inside the disc, new (-1,-4)); 1988 off-axis bank-edge sites (all outside reach, all downstream, 0
outside the 45° cone; can-fail oldStrandedHome=645); downstream walk monotone; WashCatch routes through WashStrand.
FlowWorks SelfTest 284/284; run_selftests 345 PASS / 1 FAIL (known red selftest_art_checks.py).

## Build / commits
DLL md5 e3cfcfdbf8f0c149c4b372e94719f64e. Shas: see the item's ledger events.

## Live command
`extension_proof --live --site river` (breach_wash row and the 6 it gates), after deploying FlowWorks.
