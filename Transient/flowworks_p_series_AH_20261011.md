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

---

# Item 2: `HEAT_BUDGET_PREFIX_MEND_LATE_CELLS_STARVE` (P9a, GPT G3.8)

## Pick
The only P-series item still unclaimed after P7. P8 and P9b were held by the other agents.

## Defect (verified)
When the source count passed the 3000-cell budget, `RM_LiquidHeat.Push` credited an excavated PREFIX starting at
index 0 every interval, with one global `scale = total/3000`. That caused three problems:
- excavated cells past index 3000 never pushed heat
- natural cells got nothing once the excavated cells filled the budget
- the excavated cells that were visited every interval were multiplied by the global scale, so they were
  overweighted (x3.37 for 100 excavated cells beside a 10,000-cell lake)

## Fix
- `RM_LiquidHeatMath.SplitBudget` splits the budget between the two classes in proportion to their counts. Each class
  gets its own scale (count/visited), and a class with any cells gets at least one slot.
- `RM_LiquidHeatMath.Rotate` is the per-class ring cursor (excavated `exCursor`, natural `cursor`). Push and the
  selftest both call it.
- Gathering still scans every excavated cell once per interval, as before. `lastSourceCells` is the gathered count and
  `lastVisited` is the credited count.

## Proof (offline)
- `src/RimMandrake/FlowWorks/Source/SelfTest/HeatBudgetChecks.cs` adds four cases. Over 60 intervals, every cell's
  credited weight equals 60, within one scale step. Each case has a can-fail check against the old prefix loop. The
  SelfTest passes 171/171.
- Mutation probes:
  - the old prefix split put into `SplitBudget`: 2 of the 4 cases FAILED
  - `Rotate` pinned to index 0: 3 of the 4 cases FAILED
  
  Both were restored afterwards.
- `winbuild` gave 0 warnings and 0 errors. Not deployed, and there was no live run.

---

# Second-pair-of-eyes review: P10 (137743f75) and P14 (0dfde0348)

No unclaimed P-series item was left after P9a, so I reviewed the two earlier fixes.

## P10, the weir WashCatch restore
- **Code: sound.** RimSage's `GenSpawn.SpawningWipes` shows that an item spawned onto a cell holding other items
  wipes nothing. So respawning the remaining stack at `from` cannot vanish co-held catch. If the stack was partly
  absorbed before a failed Near placement, the respawned remainder still counts as moved. That is correct.
- **Test: weak.** `selftest_flowworks_rivers.py` only string-matches the source text. Its "can-fail" removes the
  string and then checks the string is absent, so it can never fail: it is tautological. No behaviour is exercised,
  so a reordered or wrong respawn would still pass. That is acceptable only because the logic is Verse-bound. A real
  proof would need either the live A2 or a Verse-free extraction.

## P14, the mission tank goal bound to the destination
- **Correct.** `jawa/list_things` `id` is `thing.ThingID` (`JawaBenchTerrainTools.cs` ListThings), the same string
  form the THING_ID_RX binding expects. `rect_str` matches the `x,z,w,h` rect the tool parses.
- **Finding 1 (judgement, not changed).** `goal_check` uses `run.get("tank_baseline", {})`. A run.json written
  before this fix therefore reads every delta from 0, so a destination tank PRE-FILLED before the mission still
  PASSES. That is exactly the G6.5 negative. The selftest asserts this deliberately ("a pre-fix run.json with no
  baseline key reads deltas from 0 -> PASS"). The safer default is `run.get("tank_baseline")`, where None means
  UNMEASURED. This matters only for runs started before 0dfde0348.
- **Finding 2 (minor).** `read_dest_tanks` asks for `limit 50` and ignores the `truncated` count. A tank that exists
  at the start but is unlisted gets baseline 0 (`base.get(id, 0.0)`), which allows a false PASS on a site with more
  than 50 tanks. It is unlikely on a mission site.
- **Finding 3 (disclosed already).** When the selection semantics name no tank ThingID at all, the read binds by
  `cell`, and `UNITS_RX` takes the FIRST "(a / b units)" in the whole selection. It is unverified live.
