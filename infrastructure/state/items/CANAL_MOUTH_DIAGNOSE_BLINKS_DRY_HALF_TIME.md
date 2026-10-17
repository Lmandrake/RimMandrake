# CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME

Found by V&V pilot 1 (`design/RimMandrake/vv_methods/pilot1_shipped_matrix_2026-10-16.md` §4.2). Offline only, production
`RM_FlowKernel.cs` at HEAD `4475adc54`. Not seen live yet.

## What

The scene of the SelfTest case `CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY_dead_end_fills_from_far_end`: a 60-cell water body beside
the mouth of a dead-end 1x10 D=1 channel. At the SHIPPED kernel flags (viscosity, thick creep, water creep, level by surface,
level set, edge sinks, seam rotation), the channel after each pulse (mouth first):

```
pulse 1: 1000000000   pulse 2: 0100000000   pulse 3: 1100000000   pulse 4: 0110000000
pulse 5: 1110000000   pulse 6: 0111000000   ...                   pulse 18: 0111111111   pulse 19: 1111111111
```

- The mouth is DRY on every even pulse until the run is full (9 of the 18 filling pulses), with wet water beyond it.
- The front moves one cell per TWO pulses, and the source pays one level per two pulses (stock 299, 299, 298, 298, ...).
- The same for a LIMITLESS body. With level-by-surface off (the C# defaults the case runs at) the run is worse: `1010101010` stripes.

## Why it may be a defect

- The case's own docstring states the property: *"after each of the first 3 pulses the mouth is the first wet cell"*. The code
  checks only pulse 1 (`if (p == 1 && at != "1000000000")`), so the case passes while the stated property fails at pulse 2.
- The ruling it implements (CANAL_FRONT_FIX_WRONG_END_WETS_FIRST, owner by card 2026-10-12): *"the wet front must visibly
  advance outward from the mouth like a flood front"*. A mouth that blinks dry every 250 ticks behind a wet front is the look the
  owner reported live as "mouth stays dry".

## Mechanism (INFERRED, not traced line by line)

Water creep: a cell that received water this pulse may not pass it on. The mouth takes a level from the source (pulse 1), passes it
on next pulse, and the source does not top the mouth back up in that same pulse, so the mouth reads 0 at the end of every
second pulse.

## Reproduce

`python3 src/RimMandrake/Utils/vv_shipped_matrix.py --skip-ep --skip-control` builds the probe, then
`dotnet.exe VVProbe.dll trace --body limited --pulses 20 --set "<shipped set string from the run's derived.json>"`
(in `D:\Luke\dev\_rmbuild\VV_PILOT1_b4c18606\src\RimMandrake\FlowWorks\Source\SelfTest\VV\bin\Release\net8.0`).

## NEXT

Classify by reading `RM_FlowKernel` (the creep gate against the source→mouth move). If confirmed: fix in the kernel, mirror it in
`validation_v2.PulseOracle`, and make the case check the mouth after EVERY pulse while the run fills. Ask the owner only if the
1-cell-per-2-pulses speed turns out to be a trade against the ruling.
