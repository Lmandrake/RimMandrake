# AtmosphericBase — kernel cost and regrid count at 11 / 200 / 1000 fixtures (2026-11-02)

Item `ATMOSPHERIC_BASE_HARDEN_SMALL_LAMP_COUNTS`; raw lines: `src/RimMandrake/AtmosphericBase/measurements/quota_cost_11_200_1000.txt`; rules in
`design/RimMandrake/atmospheric_base_mod_definition.md` §2.6a. **MEASURED offline** by `Q3Measure` in
`src/RimMandrake/AtmosphericBase/Source/SelfTest/QuotaTests.cs`, run by
`python3 src/RimMandrake/AtmosphericBase/selftest_atmosphericbase_kernel.py` (dotnet.exe, net472, Release, on
Archmagi). Each run prints the `MEASURE` lines again; the timings vary from run to run, the write counts do not.

**What it measures:** the kernel half of one compositor evaluation — tremor assignment from three contributors
(cap 3, 30 s slot, 0.8 s flicker, 1 in 4, 4%), the flasher pick (asked 2), the pattern index per fixture, and the
changed-only tracker. 600 evaluations = 60 s of real time at 60 fps with one evaluation every 6 frames, then one
evaluation after a 30 s hitch. A **write** is one `CompGlower` colour change, i.e. one glow-grid dirty, so
`writes_per_eval` is the regrid count the evaluation causes.

**What it does not measure (owed live):** the Verse half of `Evaluate` (the `TakenThings` walk, `InGroup`,
territory allocation), the in-game frame time, and what each glow-grid regrid costs the engine. Those need the
running game.

| fixtures | mean eval ms | max eval ms | writes / eval (regrids) | regrids / s | max burst (one eval) | after a 30 s hitch | alloc bytes / eval | flashers | tremor cap |
|---|---|---|---|---|---|---|---|---|---|
| 11 | 0.0020 | 0.0235 | 0.26 | 2.6 | 3 | 0 | 3,631 | 1 | 1 |
| 200 | 0.0391 | 1.4087 | 1.38 | 13.8 | 8 | 6 | 69,057 | 2 | 8 |
| 1000 | 0.1995 | 0.5318 | 5.44 | 54.4 | 13 | 35 | 347,342 | 2 | 40 |

Reading it:

- Cost is linear in fixtures (about 0.2 µs per fixture per evaluation) and the writes track the moving front, not
  the grid: at 1000 fixtures fewer than 1% are written per evaluation.
- **No synchronized burst:** the largest single evaluation writes 13 of 1000; a 30 s hitch writes 35 (one per
  fixture whose state differs, never a replay). The first evaluation writes every fixture once, by design (§9.9).
- The maxima are single outlier evaluations that move from run to run (200 fixtures: 0.84 ms in one run, 1.41 ms
  in the next, while the 1000 row stayed near 0.5 ms): host GC or scheduling, not the kernel. Budget with the means.
- Allocation is about 350 B per fixture per evaluation in this harness, scaling with fixtures rather than with
  flickers, so it comes from the per-fixture path (`RM_SchemeKernel.PaletteIndex` and what it calls), not the
  tremor dictionary; which call allocates is not attributed here. At 1000 fixtures and 10 evaluations a second
  that is ~3.5 MB/s of garbage, before the compositor's own per-evaluation lists (review package K7).
