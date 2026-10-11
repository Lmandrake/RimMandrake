# FlowWorks P-series AH 2026-10-11 (FOUNDRY)

## Pick
`FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO` (P7, GPT G3.6). The unclaimed P-series items were P5, P6a, P6b, P7, P8, P9a
and P9b. P7 is the middle one. P4 and P11 were held by the other agents, and P10 and P14 were already fixed.

## Defect (verified at origin/main 8e0c925e1)
`RM_MapComponent_Excavation.PaletteKey` returned key 0 once the palette held 254 entries. Every writer still filled
the cell: the pump spread, the kernel's `Claim`, rain, and `TrySetDriverFillOutcome`. `SyncFluidIdentity` then read
key 0 on a wet cell as "unrecorded" and stamped it as `ActiveFluid`, so the liquid silently changed identity. The
palette was only compacted on load (`RepairLoadedGrids`).

## Fix
- `RM_ExcavationSanityMath.AllocateKey<T>` (Verse-free) does the work. When the palette is full, it compacts it IN
  SESSION, using the same drop-unused rule and grid remap as the load repair. It returns 0 for a real fluid only when
  every key is in use. The palette list is kept by reference.
- In the adapter, `TryPaletteKey` logs each compaction and warns once if the palette is truly exhausted. Every writer
  now refuses a dry cell it cannot key BEFORE it changes fill:
  - pump spread: the cell gets room 0, so the remainder is the disclosed overflow
  - rain: the cell is skipped
  - driver fill: returns `Refused`
- Kernel: `RM_IFlowWorld.CanClaim(fluid)` is checked before the source debit, for a dry recipient only. The fuzz
  `ArrayWorld` answers true unless a test sets `canClaim`.
- Once the palette is compacted, exhaustion can only happen with more than 253 distinct liquids sitting in cells at
  once.

## Proof (offline)
- `src/RimMandrake/FlowWorks/Source/SelfTest/PaletteExhaustionChecks.cs` adds three cases:
  - compaction keeps every cell's identity
  - all keys in use: refused, with the palette and grid untouched
  - the kernel refuses a dry claim with no debit
  
  Each case carries a can-fail check against the old rule. The SelfTest passes 162/162, with hose 130/130 and 344/344.
- Mutation probe: with compaction disabled and the kernel `CanClaim` check removed, the result was 160/162. Both P7
  cases that test those paths FAILED, then were restored.
- `winbuild` for FlowWorks gave 0 warnings and 0 errors, and the DLL was rebuilt from clean source.
- Trap: `selftest_winstage` stages to ONE shared `_rmbuild\selftest_RimMandrakeFlowWorks.SelfTest` dir for every
  clone. A run while AF/AG were also staging executed THEIR source (P11/P9b cases, none of mine). I ran under a
  per-clone stage name instead.
- Not deployed, and there was no live run.
