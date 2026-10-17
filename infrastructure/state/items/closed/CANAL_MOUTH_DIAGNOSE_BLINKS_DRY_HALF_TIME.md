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

## Verdict (independent re-derivation, FOUNDRY helper 2026-10-16): REAL kernel bug, fixed offline

- Reproduced exactly from a D: scratch build of HEAD `eb0c40d9f` (own trace, not the pilot's probe): limited and limitless
  bodies, D=1 and D=2 runs. The off-configs (level-by-surface off, level-set off) stripe 1010 for the same root cause.
- Mechanism (traced, not inferred): `ResolveComponent` builds its recipient list before anything moves, so a brim mouth is
  not a recipient in the pulse it passes its unit on (the level solve's `CellKey` deliberately puts the part band away
  from the live mouth); the source refilled it only next pulse. The owner's ruling (flood front from the mouth) and the
  creep flag's own promise (one cell a pulse) both say this is wrong; nothing in the rulings asks for a blinking mouth.
- Already seen live: the recorded E2 vectors of 2026-10-12e (`validation_v2.O11_LIVE_E2`) read the mouth 0 on pulses 2 and
  4, first full at 2n-1 = 7. The 8-cell trench full at tick 3753 is ~15 pulses = 2n-1 as well: the blink slowed it, it
  did not stall it.
- Fix: `RM_FlowKernel.TopUpWaterMouths` (water creep on): after the pass and the solve, a dug cell beside a supplying water
  source that took nothing this pulse and has room takes up to flowPerPulse from it, cell-index order. Mirrored in
  `PulseOracle._top_up_mouths`. Shipped trace now `1000000000 1100000000 ... 1111111111` (full at pulse 10, was 19); the
  source pays one level a pulse. The case checks EVERY pulse while the run fills (fails on the old kernel at pulse 2).
- The differential test gained a `shipped` mode (creeps on): 3000/3000 agree; with the oracle mirror removed 804/3000
  disagree. The live rows `E2_channels_fill_every_direction`/O7/O11 now expect first full at n = 4 (O11 replays the
  recorded vectors with the top-up off).

## Owed

- LIVE: deploy the rebuilt DLL and run `validation_v2.py --live`; E2 must read full at pulse 4, mouth wet every pulse.

## LIVE result (FOUNDRY helper 2026-10-16, deployed DLL sha256 82f3943b…, byte-identical to the git-archive export; ratchet_pilot tier, 21 mods)

- `validation_v2.py --live` on `RM_TestSite_calm_v1`: **61 PASS, 0 FAIL, 0 UNMEASURED**. E2 first-full pulse 4 in all four directions; the 4-cell run reads `1000, 1100, 1110, 1111` (mouth wet every pulse); E2_rerun_determinism and E2s shared-source PASS.
- River `extension_proof --site river`: 20 PASS / 0 FAIL / 1 UNMEASURED (baseline 20/0/1).
- Headline scene (`live_probes/fw_water_headline.py`): 8-cell trench full at **tick 2002** (8 pulses, one cell a pulse) against 3753 before (about 15 pulses); the save taken mid-fill and reloaded continued identically (A == B chunk for chunk, +1 tick offset). Evidence: `Transient/fw_mouth_live_20261016/`.
