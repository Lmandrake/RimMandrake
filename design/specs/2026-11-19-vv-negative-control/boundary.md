# BOUNDARY: the shipped-settings matrix's negative control, Design Version 0.1.0

Code: `src/RimMandrake/Utils/vv_shipped_matrix.py` (`stage_flowworks(control=True)`, `negative_control`, `derive` with
`read_at`) and the `VV_CONTROL` split in `src/RimMandrake/FlowWorks/Source/SelfTest/VV/ShippedMatrixProbe.cs`. Item:
`RIMMANDRAKE_INSTALL_VV_MATRIX_CLOCK_WRITTEN_NOT_RUNNING`. Written 2026-11-19. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_vv_negative_control.py`, which builds and runs the control for real (dotnet.exe,
offline, no game) into its own `_selftest` stage folder. The control keeps no state between runs, so the page has no
LIFE CYCLES.

What it is for: criterion (3) of the matrix (STAGE2 adversarial review, 2026-10-16). On the pre-fix kernel
`CONTROL_REV`, `fills_from_limitless` at base seed 1000, n=2000, must read red with the shipped configuration forced
and 0 with the authored one, so a green matrix is known to be able to go red. Measured 2026-11-19: 194/2000 and
0/2000, the STAGE2 numbers exactly.

Why the page exists: on 2026-11-19 the `rm-vv-matrix` clock ran 36 minutes and died at its last step with no VERDICT
line. The control compiles `CONTROL_REV`'s kernel and fuzz world with today's probe, and the probe's law plants and
trace (2026-11-13 and 2026-11-18) read `k.water`, `RM_LevelSolve` and `Notch`, which that kernel lacks (18 errors).
Fixing the compile then showed a second, silent fault: the control forced today's derived configuration, which no
longer names `levelSetEnabled` / `levelBySurfaceEnabled` / `creepEnabled` (the exact solve became the only engine on
2026-11-13), so the old kernel ran with them at false and read 0/2000. The control had been blind since that day.

## ACCEPTS (the only inputs the control is built for)

- **a-revision-whose-sources-parse.** `CONTROL_REV` resolves in the clone, and its settings file, its adapter's
  `DoPulse` (started by `flowKernel.BeginPulse(` or `flowKernel.Pulse(`) and its kernel parse with the same parsers
  `derive()` uses on today's tree.
- **a-probe-that-compiles-against-both-kernels.** Probe code outside `#if !VV_CONTROL` reads only kernel members the
  pre-fix kernel also has. Code that needs today's kernel goes inside the guard.

## DOES NOT SURVIVE (not promised)

- **no-windows-dotnet.** With no `dotnet.exe` the build fails and the control reads not reproduced: a red VERDICT,
  never a pass.
- **a-revision-that-will-not-parse.** An adapter at `CONTROL_REV` that `adapter_lines` cannot read raises, and the
  matrix stops without a VERDICT line. The clock then writes UNMEASURED with its exit code.

## PROMISES (each one is owed a test of the same name)

- **the-control-builds.** `stage_flowworks(control=True)` compiles `CONTROL_REV`'s kernel and fuzz world with this
  tree's probe, SequenceFuzz and math files, and yields a dll.
- **the-control-goes-red.** `negative_control` forces the configuration derived at `CONTROL_REV` (that revision's own
  settings, adapter and kernel, read by `git show`), never today's. It reports reproduced only when SHIPPED has
  failures, is measured, and AUTHORED completed with 0 failures, no exceptions and no time-out. The test prints both
  counts and their limits.
- **a-plant-or-trace-is-refused-in-the-control.** The control build does not compile the law plants or the trace.
  `--plant <name>` and `trace` there exit 2 and say "not compiled into the negative-control build", never a silent
  no-op that reads green.
- **the-control-is-built-before-the-long-runs.** `main()` builds the control right after the probe, before any suite
  or rates run, so a control that no longer compiles stops the run in its first minute, not after 36.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
