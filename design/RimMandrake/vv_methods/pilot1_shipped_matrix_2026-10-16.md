# V&V pilot 1: the shipped-configuration matrix, with honest counts (2026-10-16)

This is the first piece of the extra-V&V programme, the part the owner chose ("first piece only"). A FOUNDRY helper ran it offline:
no bridge, no game, no deploy, and no change to any mod or kernel source. Inputs were stage 1, stage 2 §1/§4.3/§4.4/§6 and stage 3
§3/§6. Kernel under test: HEAD `4475adc54`.

**Re-run:** `python3 src/RimMandrake/Utils/vv_shipped_matrix.py`. That builds and runs everything; the probes are
`FlowWorks/Source/SelfTest/VV/ShippedMatrixProbe.cs` and `EmpirePursuit/Source/SelfTest/VV/EpRatesProbe.cs`.
`--lint-only` runs the derivation and the static lint alone (2 s). Results go to
`D:\Luke\dev\_rmbuild\VV_PILOT1_<clone hash>_results\<timestamp>\`. This run is `20261016T224233`; the numbers are copied
below, because that folder is outside the repo.

## 0. Bottom line

- **The pass criterion was met (exit 0): 0 failures at the shipped flags.** That covers 266,000 randomised kernel and model
  scenes (21,000 of them through `RM_FlowKernel`), 4,298 hose/trail cases and 16,000 EmpirePursuit cases. Every count is a
  real count; nothing stops at 5.
- **The harness can see the bug it was built for.** On the pre-fix kernel (`c82dd1c08^`), `fills_from_limitless` reads
  **194/2000 at SHIPPED and 0/2000 at AUTHORED**. That is stage 2's number, reproduced exactly.
- **One real-bug candidate was filed, but the pass criterion did not catch it.** It turned up while reading why a
  forced-shipped case failed (§4.2): a canal mouth that goes dry every other pulse while a dead-end D=1 run fills, at the
  shipped flags. Item: `CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME`.
- **Flag lint.** All 9 adapter-set kernel flags are set to their shipped value by some test. But **0 of the 34 kernel-pulsing
  SelfTest cases ever runs the full shipped combination**, and thick creep is on in only 1 case. Item:
  `KERNEL_SELFTEST_WIRE_SHIPPED_TUPLE_NEVER`.
- Every red at a single-flag-off configuration was classified, with evidence. Each is by design (the property being tested
  is the switched-off feature) or a test-oracle coupling (§4.3). None is a real bug.

## 1. Method (declared before the first run; it sits in the script's docstring)

**Shipped values are derived, not typed in.** The script reads the field initialisers of `RimMandrakeFlowWorksSettings`
(`RimMandrakeFlowWorksMod.cs`) and cross-checks each against its Scribe default (no literal drift found). It then evaluates
every adapter line `flowKernel.<field> = <expr>;` in `RM_MapComponent_Excavation.DoPulse` against those defaults.
`AnyDrainEdge(map)` is taken as false, which is the default map.

| kernel field | shipped | from |
|---|---|---|
| flowPerPulse | 1 | `FlowPerPulse` = clamp(round(flowPerPulse = 1), 1, 4) |
| edgeSinksEnabled | true | `edgeSinksEnabled \|\| AnyDrainEdge(map)` |
| viscosityEnabled | true | `viscosityEnabled` |
| creepEnabled | true | `viscosityEnabled && thickCreepEnabled` |
| creepWaterEnabled | true | `waterFrontCreepEnabled` |
| levelBySurfaceEnabled | true | `levelBySurfaceEnabled` |
| levelSetEnabled | true | `levelBySurfaceEnabled && levelSetEnabled` |
| maxComponentCells | 6000 | `MaxNetworkCells` |
| seamRotationEnabled | true | `networkSeamsMoveEnabled` |
| sealedCell, externalInput | scene | door lambda; `pumpFedSpreadEnabled && driverInputs.Count > 0` |

- **Owner's saved settings.** The file `Mod_FlowWorks_RimMandrakeFlowWorksMod.xml` holds **none** of the 10 adapter-read keys,
  so his game loads the Scribe defaults, which are the shipped values above. This was read, not assumed.
- **Single-flag-off.** The script flips one adapter-read bool setting at a time and re-evaluates the adapter. Turning
  viscosity off therefore also turns creep off, as in game. That gives 7 kernel configurations; `pumpFedSpreadEnabled`
  changes only scene state, so it has none.
- **Forcing the flags.** The script stages the SelfTest tree on D: and deletes the probe's bin/obj every run, per the
  stale-stage lesson of 2026-10-16. It inserts one line into the **staged** `ArrayWorld.Pulse`:
  `VV.MatrixFlags.Apply(k)`, placed just before `k.Pulse`. That is the same moment the adapter writes the settings each pulse
  in game. Every kernel pulse in the SelfTest goes through `ArrayWorld.Pulse`, so the hook sees all of them (2,074,818 pulses in
  one full suite run). `AUTHORED` means no forcing: each family keeps the flags it sets itself.
- **Counting.** The probe calls each family once per seed (n = 1), using reflection for the private generator and runner.
  This bypasses the families' `fails.Count < 5` caps. It keeps every failing seed and shrinks only the first 5. It records
  attempted, completed, failures, exceptions and timeouts separately (stage 3's accounting point).
- **Seeds.** Base 500000, fresh. Program.cs uses 1, 7, 11, 13, 101, 202 and 1000. The control uses 1000, to compare with
  stage 2.
- **Bounds.** 0 in n gives the rule-of-three 95% upper bound, 3/n. k > 0 gives a Wilson 95% interval. Both describe the
  generator's scene distribution, not how often a player would hit the failure.

**Pass criterion.**
1. At SHIPPED, every randomised family completes its fixed n with 0 failures, 0 exceptions and no timeout.
2. Kernel families show more than 0 pulses through the hook.
3. The negative control reproduces: red at SHIPPED, 0 at AUTHORED, on `c82dd1c08^`.
4. The AUTHORED full suite run through the probe is clean.

**Stopping rule.** Each family has a fixed n, set before the run and never extended or cut on results. The only early stop
is a 1200 s wall cap per family; a capped family would be reported as TIMEOUT, meaning NOT EVIDENCED, never a pass. No family
reached the cap; the slowest took 8 s.

## 2. Run log (honest)

| run | verdict | cause |
|---|---|---|
| 1 | FAIL | HARNESS: the control would not build, because HEAD's fuzz file calls `SeamSlot`, which the pre-fix kernel lacks. 6 AUTHORED cases failed reading `Patches/`, which was not staged. Fixed: the control now compiles the same-revision fuzz file, and `Patches/` is staged |
| 2 | FAIL | HARNESS: 1 AUTHORED case read `Tools/generate_liquid_suite.py`, which was not staged. Fixed |
| 3 | **PASS** | the numbers below |

Rates were identical in all three runs: the generators are deterministic. Runs 1 and 2 went red on the staging check
(criterion 4), not on the mod.

## 3. Results at the shipped flags

| family | what it checks | scenes | failures | 95% bound |
|---|---|---|---|---|
| kernel_fuzz (`FlowKernelFuzz.Gen/Run`) | ledger, 0≤F≤D≤4, per-fluid conservation, sink accounting, fixed point | 10,000 | 0 | < 0.03% |
| fills_from_limitless | every dug cell connected to a limitless source ends full | 10,000 | 0 | < 0.03% |
| surface_random (fixed rng, 1000 scenes) | at rest by 150, conserves, no wet step of 2+ | 1,000 | 0 | < 0.3% |
| seq_sequences | cell/body/tank sequences (no kernel flags; settings-fed parameters sampled in ranges that include the shipped values) | 20,000 | 0 | < 0.015% |
| seq_orders | flow and recession orders are strict | 200,000 | 0 | < 0.0015% |
| seq_conversion | the converter never overspends | 5,000 | 0 | < 0.06% |
| seq_pitwidth | pit width is monotone | 20,000 | 0 | < 0.015% |
| hose (seeds 1-1500, both reel modes) | lay geometry; MinR sampled from {0.6, 1.2, 1.2, 2.0}, shipped 1.2; slack and plump at shipped 1.0 | 2,798 | 0 | < 0.107% |
| trail | carry/trail state machine | 1,500 | 0 | < 0.2% |
| ep_ladder | EmpirePursuit ladder vs spec; gates start at the shipped all-on and are mutated by actions | 8,000 | 0 | < 0.0375% |
| ep_timers | hourly scheduler | 3,000 | 0 | < 0.1% |
| ep_math | EmpireLadderMath properties | 5,000 | 0 | < 0.06% |

**AUTHORED baseline** (no forcing, same seeds): kernel_fuzz 0/10000; fills_from_limitless 0/10000;
`fills_from_limitless(shipped: true)` 0/10000; surface_random 0/1000; surface_random with LevelSet 0/1000.

**Negative control** (`c82dd1c08^` kernel and fuzz file, base seed 1000): SHIPPED **194/2000**, which is 9.7% (Wilson 95%:
8.5-11.1%); AUTHORED **0/2000**. This is the class of bug the matrix exists for, and the harness sees it.

## 4. Single-flag-off, and the forced full suites

### 4.1 Randomised families, n = 2000 (surface_random 1000)

| config | kernel_fuzz | fills_from_limitless | surface_random |
|---|---|---|---|
| OFF edgeSinks | **163/2000** (8.15%; Wilson 7.0-9.4%) | 0 | 0 |
| OFF levelBySurface (levelSet off too) | 0 | 0 | **668/1000** (66.8%; 63.8-69.6%) |
| OFF levelSet | 0 | 0 | 0 |
| OFF networkSeamsMove | 0 | 0 | 0 |
| OFF thickCreep | 0 | 0 | 0 |
| OFF viscosity (creep off too) | 0 | 0 | 0 |
| OFF waterFrontCreep | 0 | 0 | 0 |

- **OFF edgeSinks, kernel_fuzz: TEST ORACLE COUPLING, not a bug.** First example: seed 500020, `pulse 6: sink drained 0, cells
  account for 1`. The fuzz oracle computes the expected drain from the scene's `s.sinks`, not from the kernel flag. With the
  setting off, the kernel correctly drains nothing, and the oracle still expects a drain. In game, turning the setting off means
  map edges do not drain, which is the documented behaviour. Not filed; a property that wants to run in this configuration
  should read `k.edgeSinksEnabled`.
- **OFF levelBySurface, surface_random: BY DESIGN.** All 668 are "a wet step of 2+" (0 not at rest, 0 unbalanced). The family
  asserts the level-by-surface rule. With the setting off, the old gravity rule runs, and that rule leaves those steps. Its
  stranding is the very reason the setting exists (WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND).

### 4.2 The full SelfTest (435 cases) once per configuration, flags forced

| config | passed | extra failures vs AUTHORED |
|---|---|---|
| AUTHORED | 435/435 | — |
| SHIPPED | 424/435 | 11 |
| OFF edgeSinks | 420/435 | 15 |
| OFF levelBySurface | 418/435 | 17 |
| OFF levelSet | 421/435 | 14 |
| OFF networkSeamsMove, thickCreep, viscosity | 424/435 each | 11 (the same 11 as SHIPPED) |
| OFF waterFrontCreep | 422/435 | 13 |

**All 11 SHIPPED-forced failures are CONTROL ARMS: by design.** Forcing the flags at every pulse also forces each case's
"before the fix" arm, so the case's can-it-fail probe can no longer show the defect. Examples:
- PumpFedChannelSpreads: `farPlain=1`, want 0.
- PumpFedReload: old-rule probe 2, want 0.
- OversizedNetwork: `controlStuck=False`, because the forced cap of 6000 overrides the case's 50.
- FrontSpeed: `controlRaces=False`.
- The six WATER_SURFACE / WATER_LEVELSET rewire cases: "old rule F=" now equals the new rule.
- CanalMouth: `raceShape=False`.

In every one the **fix arm's** numbers still pass (for example, flat channel spread 1, drained 26/26, mouth first after
pulse 1). This is evidence that the shipped combination keeps each fix. It is not a defect.

**The extra single-off failures are BY DESIGN.** Each case asserts the feature that was switched off:
- edge drains with sinks off: "drained 0/40";
- level-set basins and stripes with levelSet off: "pieces 4", "stripes 20";
- the old gravity rule with levelBySurface off: "left 30, drained 10/40", and a MapControl holder that reads "4" in place of
  half full;
- mouth-first fill with waterFrontCreep off.

The player can reach these configurations through Mod Settings. In each, they get the documented pre-fix behaviour, as
"all-off degrades gracefully" intends.

**Real-bug candidate: `CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME`.** The CanalMouth case's forced trace read
`1000000000 0100000000 1100000000`. A dedicated reproducer (`VVProbe.dll trace`) shows the same at SHIPPED for both a limited
and a limitless body:
- The mouth is **dry on every even pulse** until the run is full (9 of 18 filling pulses), with water beyond it.
- The front moves one cell per two pulses.
- The source pays one level per two pulses.

The case's docstring states the property *"after each of the first 3 pulses the mouth is the first wet cell"*, but its code
checks pulse 1 only, so it passes. The ruling it implements is "the wet front must visibly advance outward from the mouth like
a flood front" (owner by card, 2026-10-12). Classification:
- **REAL (provisional):** shipped behaviour breaks the case's own stated, ruling-derived property, and the test is too weak to
  notice.
- The mechanism is INFERRED: the water-creep gate, with no source top-up of the mouth that gave this pulse.
- It is not observed live, and the fix is not made. Kernel code is out of this helper's scope.

Shipped-flag string for the reproducer:
`creepEnabled=1;creepWaterEnabled=1;edgeSinksEnabled=1;flowPerPulse=1;levelBySurfaceEnabled=1;levelSetEnabled=1;maxComponentCells=6000;seamRotationEnabled=1;viscosityEnabled=1`.

### 4.3 Classification summary

| failure family | where | rate | class | evidence |
|---|---|---|---|---|
| mouth dry every other pulse | CanalMouth scene, SHIPPED | deterministic, 9/18 filling pulses | **real (provisional)** — filed | trace above; docstring vs check |
| sink drain mismatch | kernel_fuzz, OFF edgeSinks | 163/2000 | test-oracle coupling | oracle reads `s.sinks`, not the kernel flag |
| wet step of 2+ | surface_random, OFF levelBySurface | 668/1000 | by design | the family asserts the switched-off rule |
| control arm cannot fail | 11 cases, every forced config | 11/435 | by design (forcing artefact) | each failing clause is the control/old-rule arm |
| feature-specific cases | 2-6 per single-off config | — | by design | each asserts the switched-off feature |
| staging gaps (runs 1-2) | AUTHORED suite through the probe | 6, then 1 | harness | missing `Patches/`, `Tools/`; fixed |

Following stage 2's rule, the agent that runs a pilot does not classify its reds. That rule was **not** met here: one helper ran
and classified everything. Treat §4.3 as provisional until a second reader checks the filed item.

## 5. Flag lint (stage 2 §4.4)

**Static** (regex over `SelfTest/*.cs`): every adapter-set field is assigned its shipped value somewhere.
- 7 fields are literal-shipped.
- `flowPerPulse` and `maxComponentCells` are default-is-shipped.
- `creepEnabled` is the weakest: expression only (`FrontAfter(..., creep, ...)`).
- **No static gap.**

**Dynamic** (the AUTHORED suite with the hook recording each flag at every pulse; per field, the number of cases that pulse it
at its shipped value):

| field | cases at shipped | cases at other values |
|---|---|---|
| flowPerPulse | 34 | 0 |
| edgeSinksEnabled | 9 | 30 |
| viscosityEnabled | 21 | 14 |
| **creepEnabled** | **1** | 34 |
| creepWaterEnabled | 22 | 13 |
| levelBySurfaceEnabled | 21 | 19 |
| levelSetEnabled | 14 | 24 |
| maxComponentCells | 34 | 1 (cap 50) |
| **seamRotationEnabled** | **2** (both at cap 50) | 33 |

**Gaps:**
- (a) **0 of 34 kernel-pulsing cases ever runs the full shipped tuple.** The shipped combination is exercised only by this
  pilot's forced runs, which are not in `run_selftests.py` or the nightly sweep. Filed: `KERNEL_SELFTEST_WIRE_SHIPPED_TUPLE_NEVER`.
- (b) Thick creep at its shipped value is tested by one hand case, with level-by-surface off.
- (c) Seam rotation is never tested at the shipped cap of 6000. The random scenes are at most 10x10, so the kernel's cap path
  cannot fire there at all.
- (d) The scene-state inputs (`externalInput` from pumps and drills, `sealedCell` from doors) appear only in hand cases. No
  randomised family generates them.
- (e) Hose, Sequence and EmpirePursuit have no adapter-set kernel bools. Their settings-fed parameters are sampled in ranges
  that contain the shipped values; they are not pinned to them.

As stage 3 warned, a field seen at its shipped value does **not** prove the branch it guards ran or was asserted. Coverage
(pilot 3) is the instrument for that.

## 6. Honest limits

- `fails/n` is a property of each generator's distribution: small grids (4-10 cells), no doors, no drivers, at most 120 pulses.
  It is not a player failure rate. "0 in 10,000" bounds only the generator's own space.
- Forcing at `ArrayWorld.Pulse` overrides flags the families set on purpose. For deterministic cases that is why §4.2 needs
  reading, not counting. The random families' sink oracle is coupled to the scene, not the flag, so OFF edgeSinks is not a
  valid configuration for kernel_fuzz without an oracle change.
- `surface_random`'s count is a lower bound on failing scenes (the max of its three per-check counts). It is exact here,
  because only one check ever failed.
- Hose failures are counted from the fuzz's own report. The hose family's per-seed shipped subset (MinR = 1.2) is not
  separated out.
- Nothing here sees the Verse glue, Harmony patches, saved-game state or the live adapter. "Shipped" means the adapter
  expression evaluated offline. The pilot cannot observe a live run with a dev drain edge, or a setting changed at runtime.
- The mouth-blink finding has not been seen in game and its mechanism is inferred.
- One helper ran, classified and wrote this (a self-grading risk). The negative control is the only independent anchor: stage 2
  measured that number and this harness reproduced it.
