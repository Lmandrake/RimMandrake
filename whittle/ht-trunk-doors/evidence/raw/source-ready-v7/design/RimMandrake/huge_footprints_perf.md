# HugeFootprints performance: current scheduler and retained measurements

Owner ruling `ROT_GIANTS_DENSITY_JUDGE_TWELVE_PCT_BLOCKED`: the dense forest is intended and acceptable; handle its
cost in code. Do not thin the roster or biome plant density. Owner answer 4 in
`hugethings_codex_2026-11-09/ANSWERS_OWNER.md` (2026-11-11) permits growing trunks to seal doors and disconnect rooms.
The previous connectivity/root-access requirements and algorithms implementing them are deleted.

Source: `src/RimMandrake/HugeThings/Source/MapComponent_HugeFootprints.cs`, `CompHugeFootprint.cs`,
`Kernel/RM_HugeClaimsKernel.cs`, `Kernel/RM_HugeFootprintKernel.cs`, and `HugePlantCutting.cs`.
Logical-work bounds below describe source behavior; section 2 preserves dated measurements of the old DLL.

## 1. Current data model and lifecycle

### 1.1 What it is for

Measured ground-contact masks follow the actual plant picture and growth. One impassable partial-cover edifice
per realized contact cell makes the trunk solid while leaving the canopy open. The root remains its plant Thing;
no blocker is spawned over it. Per-species masks and current variant identity come from the generated
`TheRot/Patches/RotGiants_HugeFootprint.xml` and its measurement selftest.

### 1.2 Shared claims and physical cells

`ClaimLedger` maps each cell to all claiming owner IDs. The map component holds one physical blocker per realized
cell. The lowest claimant is its display/damage owner; cutting checks all claimants. Removing one plant releases
only its claims, and a shared cell remains solid until its last claimant is removed.

### 1.3 Refresh and load

Registration queues the owner. Growth/harvest/signature changes and settings generations trigger a sliced refresh;
geometry, old claims, removals and additions resume across ticks. Reconcile indexes all physical blockers, drops
duplicates and unclaimed cells, rebuilds claims from spawned plants and attempts pending placement. Runtime death
queues bounded cleanup instead of walking and relabeling the whole map synchronously.

### 1.4 Placement and cutting

Planner accepts exactly passable unprotected cells without pawns or items. Protection includes the entire pawn
body, existing buildings (including doors), blueprints, frames, interactions, trees, other giants and indestructibles.
Ordinary items move only to valid free destinations outside every claim when pushing is enabled; quest items remain
pending. Failed placement never permits wiping. Door approaches have no special protection; no connectivity or
root-access flood remains. A colonist can cut an enclosed root by working from an owned realized trunk cell through
the registered giver and vanilla plant-cutting toils. Gravship clearing retains its existing mode/owner policy.

## 2. Measurements so far and reproduction

### 2.1 Numbers (MEASURED 2026-10-10, old DLL, Rot quicktest, 550-mod list, speed Normal)

Source: `Transient/foundry_tps_diagnose_20261010.md` (lines 8, 14, 15, 18-23). That file is Transient (14-day shelf
life); the numbers are copied here so this doc does not depend on it.

| quantity | value | instrument |
|---|---|---|
| tick time | 93.6 ms/tick | always-on TPS record, 64 run windows, 3,247 ticks |
| map-component stage | 88.4 ms/tick (94% of tick) | same; `tl:Normal` 3.1, world 0.9, `mapPre` 0.7, rest < 0.2 |
| `MapComponent_HugeFootprints` | **70.0 ms/tick of 70.9 summed (99%)**, max 457 ms in one tick | `jawa/map_comp_timing`, 304 ticks |
| next component | `RM_MapComponent_AcceleratedRot` 0.13 ms/tick | same |
| GC | 12.8 collections/min running vs 5.3/min paused; 135 in 634 s (one per 4.7 s) | TPS record `gc` counter |
| managed heap | ~5.0 GB | TPS record `heapMB` |
| worst frame gap | 350-780 ms per window | TPS record `gapMaxMs` |
| process memory | 30.6 GB private, 24 GB commit headroom, 9 GB physical free: no paging evidence | OS counters |
| map | 250x250 `RM_TheRot`, 36.3k things, 19 pawns, ~230 map components | TPS record / bridge |
| giants | 2,811 footprint giants | `jawa/list_things` over the 9 defs |
| blockers | ~7,400 `RM_HugeTrunkBlocker` (~12% of 62,500 cells) | `jawa/list_things` |
| refused claims | ~1,315 pending cells | quoted in the old diagnosis; original instrument unrecorded, so UNVERIFIED. Current `DebugCounts` exists and reads pending counts. |

Gap between 88.4 (stage) and 70.9 (component sum): the two instruments ran in different windows and the stage figure
includes the profiler's own per-call overhead and other overrides; the 99% share is the robust fact, not the absolute.

GC attribution to HugeFootprints is a **hypothesis** (diagnosis line 21): the old path allocated per owner per tick
(the old per-owner planning path). On a ~5 GB heap each collection is expensive (UNVERIFIED engine fact: Unity's Mono runtime uses the
non-generational Boehm collector, so each collection marks the whole live heap; that would make pause length scale with
heap size and pause frequency scale with our allocation rate, which matches 350-780 ms gaps). The proof run must
measure GC/min with the fix to settle it.

### 2.2 The instrument: `jawa/map_comp_timing` (`91f9c0a14`)

The test-only `JawaBenchMapCompTiming.cs` tool profiles distinct MapComponentTick overrides with a Stopwatch prefix
and finalizer, then unpatches in finally. It measures per-component wall time, not internal geometry/flags/planning
phases. GC triggered by another allocation can be charged to the component running during that collection. Nested
base calls are not double-counted; thing TickLong/TickRare costs are outside this component counter. Patching also
perturbs execution, so compare the same tool/workload and retain its build, settings, map and process identities.

### 2.3 Reproduction procedure (existing disposable site)

Use an existing registered disposable save, one held host-specific bridge lease, current preflights, a guarded unique
scene-begin snapshot and exact restoration. Keep the same saved workload for an A/B and record the ordered running
mods, source/DLL/stamp hashes, giant and blocker census, pending cells, settings, actual ticks and profiler windows.
The historical quicktest generation recipe is not the current acceptance route. Current `DebugCounts` is available.
The old 70 ms figure above does not measure this scheduler or establish its current latency.

## 3. Current work bounds and costs

All loaded maps share `WorkUnitsPerTick = 200000` logical units; a map receives a child share. Each tick visits at
most `RefreshesPerTick = 8` owners in a deduplicated fair ring. A pending owner retries at most eight candidates in
that visit and then waits `PendingRetryInterval = 250`. Large geometry resumes in slices. Mutations reserve work
before moving items or editing claims, and exhaustion leaves unproved cells pending. These are logical bounds,
not a stopwatch cap. Reconcile's load work is separate from the normal per-tick queue.

Placement still allocates bounded flag windows and sorts distinct candidate keys. OccupiedRect protection visits
spawned pawn bodies. Item assignment still performs a bounded nearest-valid-cell search with shared destination
capacity. Dense workloads, many maps and huge masks can increase convergence delay. There is no remaining root-list
walk or connectivity flood to optimize.

## 4. Further optimization work

Any new cache must invalidate on every consuming input and preserve placement, shared ownership, item conservation,
fairness and cleanup. Measure the actual hot path first; the old no-new-pocket/simple-point/region-connectivity
proposals no longer apply. Pooling flags or changing ledger storage needs a measured allocation/latency benefit and
the same production tests. Density remains ruled intended.

## 5. Test plan

### 5.1 Instrumentation

`DebugCounts` reports realized/pending counts, work used/cap, refusals, owner visits and queued removals. These counters
measure logical work and convergence, not elapsed time. Collect latency/GC separately on the same frozen workload.

### 5.2 Offline production tests

`Utils/selftest_hugethings_budget.py` compiles the production scheduler with declared engine stubs and checks
same-phase fairness, cross-map caps, sliced geometry, re-registration, queued death cleanup and shared owners.
`Utils/selftest_hugethings_fuzz.py` checks exact placement eligibility, sole-entrance closure with occupied/protected
controls, geometry, items and cache behavior. `Utils/selftest_hugethings_trunk_doors.py` tests the production contact
IL rewrite and refuses mismatched call counts, arguments, branch metadata or missing driver context without partially
patching vanilla.

### 5.3 Live acceptance

`northstar/workload_corpse_live.py` retains sparse scheduler and corpse-conversion controls.
`northstar/trunk_doors_live.py` demonstrates natural growth sealing an occupied workshop, an unreachable enclosed root,
a real inside cutting job with vanilla reservations/work and mid-job save/reload, restored access through the intact
door, and pawn/item/building/free-space/disabled-feature controls. Both restore their scene-begin snapshot exactly.

### 5.4 Determinism across save/load

Compare exact source/settings/claims/blocker identities, pending work and in-progress job targets/work. A signature
alone does not prove physical convergence or successful cleanup. Shared blockers must remain while another owner
still claims them.

### 5.5 Dense Rot timing

A dense Rot workload needs its own current raw timing, allocation and convergence receipts on a preserved site.
The unit fixtures and sparse live tests do not establish dense latency, full-list integration or cross-map live
exhaustion. No such result is claimed by this document.
