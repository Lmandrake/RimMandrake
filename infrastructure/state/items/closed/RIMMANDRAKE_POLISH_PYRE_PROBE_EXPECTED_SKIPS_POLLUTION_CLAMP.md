## spec
Polish (Pyrelands, bar ash_fertility_probe; blind challenge cycle 2). ProbeLine's expected value is AshFertility of the parts,
but the real FertilityPostfix also clamps a polluted cell to FertilityGrid.MaxPollutedFertility (0.5) and skips a cell whose
edifice sets fertility; on such a cell the probe prints consistent=False though the grid is right. Its raining= field reads
curWeather only, not the weather blend. The bar's oracle (wet fresh vs dry old, refusal off) is met; this is a probe that can
cry wolf on a polluted or built-over cell. Smallest fix: pass polluted and edifice-fertility into ProbeLine and apply the same
clamp in expected.

## verify
A ProbeLine case with a polluted watered cell (grid 0.5) reads consistent=True; the existing T_ASH_PROBE_OFFLINE mutants stay red.

## criteria
Acceptance test: none yet runnable; drafted: one added row in selftest_pyrelands_ash_probe.py (polluted watered cell, grid 0.5,
consistent=True), 1 pass; on the base it reads consistent=False (expected 1.400).

## refs
file: src/RimMandrake/Pyrelands/Source/Kernel/RM_FireEcoKernel.cs
