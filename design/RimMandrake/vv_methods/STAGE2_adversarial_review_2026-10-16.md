# V&V methods, stage 2: an adversarial review of stage 1 (2026-10-16)

Stage 2 of 3. It was written by a FOUNDRY helper working offline: no bridge, game or deploy was used. The only input
taken on trust was `design/RimMandrake/vv_methods/STAGE1_report_2026-10-16.md`. Every claim in it was re-checked
against the repo, `git log` and the ledger, and the headline probe was re-run on Windows dotnet. Scratch builds are in
`D:\Luke\dev\_rmbuild\VV_STAGE2_fix` (HEAD and the fix) and `D:\Luke\dev\_rmbuild\VV_STAGE2_pre` (the pre-canal-fix
kernel).

## 0. Verdict

**Stage 1 is broadly right, and its headline was understated about eightfold.** The survey of what exists is
accurate on the counts: 49 `mutate_*.py`, 66 `selftest_*_fuzz.py` and 55 `Kernel` dirs all check out. Its central
diagnosis also holds: one agent picks the inputs, the configurations, the mutants and the oracle. Rank 1 is confirmed
by a real bug, now fixed.

Four "would have caught" claims do not survive a check:
- **Model checking** of rimflow would not have caught the cited stuck states.
- **Semgrep** would not have caught the EmpirePursuit tautology.
- Two of the dead-store or analyzer claims are wrong.

Three "absent" claims are only partly true. Metamorphic relations, harness mutation and save/load modelling each
already exist in places.

The stage-1 methods share a blind spot of their own. **None of the top six changes who writes the oracle.** The
same author writes the tests, then runs coverage, Stryker and mutmut over them. The highest-value addition here is
therefore a property suite derived from the owner's rulings and written blind (§4.1).

- **Headline: a real level-set kernel bug, not a test fake-world gap and not by design.** At the shipped flags it
  failed **194 of 2000 scenes**. Stage 1's "5/400" was the family's own failure cap (`fails.Count < 5`), not a rate.
  It is fixed in `c82dd1c08` and the item is closed. Detail in §1.
- **Refuted or downgraded:**
  - Model checking: "would have caught" refuted, so it drops to last.
  - Stryker.NET: effort under-estimated and the tool is the wrong one, so do generated mutation through the existing
    protocol instead.
  - Semgrep: over-sold, and a regex lint covers the incidents it cites.
  - mutmut: partly exists already as O-NEG and O-LIVE-NEG.
  - Verdict statistics: the data it needs is not kept.
  - Metamorphic: no longer novel, and the rotate/mirror relation is false by design.
- **Added:**
  - Blind ruling-derived properties.
  - An oracle-independence audit.
  - Uncapped failure-rate reporting.
  - An adapter-flag lint.
  - Fake-vs-C#-source contracts.
  - An effective-def golden master, promoted from stage 1's §4.
  - Production-input replay.
  - Seeded-bug detection rate for the northstar harnesses.
  - Canary/shadow kernels and test-impact analysis, both judged and ranked low.
- **First three pilots** (§6): shipped-configuration matrix plus uncapped rates; blind ruling-derived properties;
  coverage. All three can run unattended.

## 1. The headline: `LEVELSET_DIAGNOSE_SHALLOW_RIM_STAYS_DRY`

**Classification: a REAL level-set bug in the shipped kernel.**

### Reproduction

I ran the unmodified `FlowKernelFuzz.FillsFromLimitless` property with no failure cap, base seed 1000, under four
flag sets:

| kernel | all off (C# defaults) | levelBySurface | + levelSet | + levelSet + viscosity + water creep (shipped) |
|---|---|---|---|---|
| `f11976b49^` (before the canal fix) | 0/2000 | 0/2000 | **219/2000** | **219/2000** |
| HEAD `f07f81d9c` (after the canal fix) | 0/2000 | 0/2000 | **194/2000** | **194/2000** |
| `c82dd1c08` (this fix) | 0/10000 | 0/10000 | **0/10000** | **0/10000** |

- **"5/400" was an instrument trap.** The family stops at five failures, so "5" is a floor. 44 C# files contain
  roughly 95 such capped loops (`fails.Count < 5` appears 63 times, `< 4` 24 times), so any rate quoted from them has
  the same problem (§4.3).

### Mechanism

Seed 1001 shows it. A depth-1 square sits beside a brim-full 4/4 pool square, and that pool square is fed through a
mouth (a 4/4 square beside the source).

- The level-set solve re-lays only the region's own volume.
- The source adds a unit only when a mouth has room.
- `CellKey` ranks by `lowHops` first, so a deep mouth always kept its top unit. The mouth never had room, so the volume
  never grew and the rim stayed dry for ever.
- Seed 1011 is the second shape: the dry square lies **beyond** a 1/1 mouth. `PickBand` grows one contiguous patch,
  so reaching that square forced the patch through the mouth, which used up the last unit.
- The f11976b49 canal fix ("a mouth never keeps its unit for being wet") changed only the second key tier. It
  therefore missed both shapes.

### Why it is not a fake-world gap

- `ArrayWorld` models a natural source exactly as the adapter does: `IsSource` plus `CanSupply`, limitless body.
- The only path by which a limitless source adds water in the kernel is the source→mouth neighbour move. The game
  uses the same kernel file.
- So, in game: dig a deep pond beside a river, then a 1-deep trench off the pond, and the trench stays dry.

### Why it is not "by design"

- The level-set ruling ("levelset down to a smooth 0 or 1 across a too-wide field … not 0, deep, 0") is about a
  **limited** volume.
- The level-by-surface ruling ("they will try to spread out evenly") and the existing family
  `Kernel_limitless_source_fills_its_component` both expect a limitless source to fill everything connected to it.
- No ruling makes a fed square stay dry.

### Fix (`c82dd1c08`, 34 lines)

- In `PickBand`, a live mouth (a square beside a supplying source, in a non-draining component) is passed **through**
  but filled **last**. The square left short is then the mouth, and the source tops it up next pulse. The loop ends
  when the region is full.
- `validation_v2.PulseOracle` is mirrored line for line.
- A new case, `LEVELSET_DIAGNOSE_SHALLOW_RIM_STAYS_DRY_limitless_source_fills_at_shipped_flags`, runs the family at
  the shipped flags. These are the same seeds that were 194/2000 red before the fix.

### Evidence

- FlowWorks SelfTest: **428/428**.
- Kernel==oracle differential: 3000/3000 in each of the depth, surface and levelset modes.
- **Negative control on the oracle mirror:** with the mirror disabled, the differential goes DISAGREE on levelset
  seeds 5, 21 and 25.
- `validation_v2 --offline` is green.
- `--mock` is green, 61/0 with all 43 faults red.
- `dll_source_stamp check` reports MATCH.
- **Not run:** a live in-game check (no bridge). The rule change is in shipped behaviour, so the next FlowWorks live
  sitting should include a "pond + 1-deep trench beside a river" row.

### Two findings about stage 1's own pilot

1. **Stage 1 said the family "goes red on the pre-fix kernel … the class of bug that reached live". That is only
   partly true.** It goes red on both kernels, mostly for this rim bug. Only the extra 25 of 2000 scenes (219 − 194)
   are canal-sensitive. If the family had run at the shipped flags when the level-set solve landed, it would have
   blocked the merge. It could never have told anyone that the canal fix worked.
2. **The new deferral alone also clears the canal stall.** The pre-canal kernel plus only this deferral gives 0/2000.
   So the f11976b49 `IsLiveMouth` change to the wet tier in `CellKey` may now be redundant. It is left in place; this
   is not a request to remove it.

### Self-grading caveat (evaluation-independence)

- The same agent diagnosed, fixed and wrote the regression case.
- Mitigations:
  - The property is pre-existing and was written by someone else.
  - Its seeds were fixed before the fix.
  - Its red/green was measured on both sides.
  - The oracle mirror was proven sensitive.
- What it cannot rule out is a shared blind spot in "what should fill". §4.1 exists for that.

## 2. The overall framing

| stage-1 framing claim | check | verdict |
|---|---|---|
| Hand mutation, stateful PBT with shrinking and differential testing already exist | counts reproduced exactly | TRUE |
| "Differential testing against an **independent** oracle" | `validation_v2.PulseOracle` is a **port**: its docstrings name the C# method each part mirrors (`"RM_FlowKernel.CellKey"`, `"RM_FlowKernel.IsLiveMouth"`). 7 of the kernel's 14 commits also touch `validation_v2.py`. My fix had to be mirrored by hand, and the differential only proved the transcription | **FALSE as worded.** It is a port-equivalence check, which catches typos, not spec errors. Stage 1 half-says this ("Oracle mirrored") but still lists it as N-version |
| The weak spot is one agent choosing inputs, configs, mutants and oracle | confirmed by §1: the port-oracle agreed with both bugs, and the physical property caught them | TRUE, and stage 1's own top six do not address it (coverage, Stryker and mutmut all grade the same author's tests) |
| The canal stall was found only by live `validation_v2` fill rows | f11976b49's message does not say where it was found. The O11 record is dated 2026-10-12 | UNVERIFIED |
| The offline methods see only Verse-free kernels | true for coverage, Stryker and the matrix. Two of the cited incidents (`\|\| true` in `JawaBenchTerrainTools.cs`, and BURROW in a JobDriver) are Verse-bound, so no kernel method could have caught them | TRUE, and it limits ranks 2–3 more than the table shows |

## 3. The nine methods, re-checked

Columns:
- **a**: is the method really absent, and what is the nearest existing thing?
- **b**: are the cited incidents real, and would the method have caught them?
- **c**: are the effort and tooling estimates realistic?
- **d**: false-positive, maintenance and incentive cost.
- **e**: ranking verdict.

| # | method | a. absent? | b. incidents | c. effort | d. false positives, maintenance, incentive | e. verdict |
|---|---|---|---|---|---|---|
| 1 | Configuration-matrix property runs | Mostly. `Program.cs:1824-1839` runs five rewire cases with `LevelSet = true`; `LevelSetChecks.cs` sets all flags on; generic families run at the C# defaults (off). The adapter's flag mapping (`RM_MapComponent_Excavation.cs:1827-1834`) is exercised by no test | **Real, and caught a live bug** (§1). The canal stall is only weakly separated (25/2000) | Accurate: the probe and fix took about 2 h, and the families run in under 1 s each | **The incentive risk is real:** a red row "fixed" by narrowing a per-config expectation. Mitigation: expectations come from rulings (§4.1), never from the kernel author | **Keep at #1** |
| 2 | Coverage (coverlet) | TRUE absent. Only `ilspycmd` is in `C:\Users\Mandrake\.dotnet\tools`; SDK 8.0.423 | EmpirePursuit: the warnHours setter sat inside a comment (fix `f5ca06ffd`, **2026-10-15**, not 10-14), so the warning branch has 0 hits. Coverage would show it. The tautology in the same commit was `\|\| k.active >= 0` under a `k.active >= 0` guard, which is covered and not detectable by coverage | 3 h is plausible. The SelfTest project is a net8.0 Exe, which suits coverlet.console | Low false positives; the risk is reading "covered" as "checked". It needs no oracle, so it has **no shared-author bias**, which is rare | **Keep high (#3)** |
| 3 | Stryker.NET | TRUE that no FlowKernel mutation list exists (no `mutate_*flow*`). One `mutations_terminalbiomes.json` string-matches "RM_FlowKernel"; its role is unverified | Plausible but untested. Survivors in level-set code would have pointed at §1 | **Under-estimated.** The SelfTest csproj source-links the kernel (`<Compile Include="..\RM_FlowKernel.cs" />`) with no `ProjectReference`. Stryker wants a test project referencing a project under test, so it needs a new library csproj plus an xUnit wrapper, staged on D:. Kernel families run in under 1.3 s, so the CPU is cheaper than claimed, while the setup costs more | **Same-author bias:** a Stryker survivor is graded by the same tests. Equivalent-mutant triage runs 10–30% | **Downgrade the tool, keep the method.** A ~60-line Python operator generator feeding the existing `mutate_*_fuzz.py` plant/restore protocol is cheaper and fits the house pattern. Use Stryker only if that saturates |
| 4 | Mutating the Python harness and oracle (mutmut) | **PARTLY exists.** `validation_v2` has O-NEG (each offline check mutated in memory and shown to go red) and O-LIVE-NEG (43 MockBridge faults, all red). `modpack_lint_harness.py` plants XML defects. Mutating the instrument's **code** is absent | Dhoggur is real (`infrastructure/state/lessons/20261016T161714Z-FOUNDRY-dhoggur-swell-theforge-harness-hit-must.md`), and **still unguarded: 0 reads of `totalDamageDealt` in `src/`**. A mutant cannot be caught by a check that does not exist. The direct fix is the guard (§4.5), not mutation | mutmut is not installed and its Python 3.14 support is unverified. The 40-line AST fallback is realistic | Moderate equivalents in formatting code | **Downgrade to #9** |
| 5 | Metamorphic relations | **FALSE that only WatcherFuzz has them.** Monotone, symmetric or idempotent relations appear in Attitude, Armoury, OasisMaker, Droid, ShipVermin, Webwork, Scarlands, LoreStages, Weather, Axis, Contagion and Ion fuzzes. `MiasmaFuzz.cs:153` already models save+load, and `AxisFuzz.cs` models ExposeData order. What is absent is a persist-only round-trip compared against an uninterrupted branch, and a split-step relation | Stillsand is real (fix `1091295cb`, found by the GPT review). BURROW is real (fix `c602c50fe`), but it was a JobDriver closure local, which is Verse-bound. **A kernel round-trip could not have seen it** | 4–5 h is fair for FlowKernel. The Stillsand split-step needs the postfix lifted into a kernel first | **The rotate/mirror relation is false by design:** `CellKey` and `TakerKey` tie-break on cell index, so a rotated grid legitimately lays a part-filled band differently. Only weaker relations (equal total volume, equal settled-or-not) hold | **Keep the persist round-trip and split-step; drop rotate-equals. #8** |
| 6 | Semgrep / Roslyn | TRUE absent: no analyzers, no nullable, no warnaserror, no constant-condition lint. `settings_audit.py` covers settings scribing only | `\|\| true` (`JawaBenchTerrainTools.cs`, found by a manual 3-subagent sweep): a **5-line regex lint** catches it. The EmpirePursuit tautology was not literal, so Semgrep would miss it. "Dead stores, CS0219/IDE0059" would **not** fire on a field assignment moved into a comment, because nothing is left to warn on. BURROW's closure local is catchable by a Semgrep rule | Semgrep is not installed. C# triage cost is real. The analyzer build on three csprojs is about 1 h | High for generic CA rules. The ExposeData rule needs waivers | **Downgrade: a regex lint now (1 h), Semgrep only for the Toil-capture and ExposeData rules. #11** |
| 7 | Verdict statistics | TRUE that nothing computes rates (no flake, Wilson or rerun code) | The Pyre incidents are real. **`PYRE_SCORCH_YIELD_DIAGNOSE_FLAKY_HARVEST` was closed on a single PASS with the cause "MOD or HARNESS untraced"**: the flake was closed by one more trial, which is exactly the failure this method addresses | **The offline pilot cannot run as described.** `modcheck_status.json` keeps only the latest verdict per mod (`status.record_run` overwrites), with no per-row data. The 50 `Transient/northstar/*.json` files are keyed by `mod_hash`, with no run_identity. Only 8 of 14 non-mock (mod, hash) pairs have any repeat | Fingerprint granularity, as stage 1 said | **Step 0 is to keep per-row history** (an append-only JSONL in `status.record_run`). Statistics come later. #10 |
| 8 | Record-replay cassettes | TRUE: no persisted responses exist. `transport.CallLog` holds in-memory timings only. `tool_schemas.json` has 523 signatures and no responses. `fake_contracts.py` has one AST rule, with a planted-liar probe | DESTROY_BATCH is real (`5c93c206ab`, plus four more fakes fixed in `b23e0e543`). A cassette would have shown the live answer kept the pawn | 4 h is fair, but it waits on someone else's live run | Masking IDs and ticks; decays with the mod set | **Keep, but below the offline source-contract check (§4.5), which needs no live time. #12** |
| 9 | Model checking rimflow | TRUE absent (no BFS; 71 hand cases; FORBIDDEN has 7 entries; no java) | **Refuted.** The cited stuck states in `rimflow_system_and_stuck_state_2026-10-07.md` are **process** states: 232 items in `doing`, 201 of them idle for more than 3 days; 186 "built but not closed". Every one of those items had a legal exit; nobody took it. A model checker finds unreachable or exit-less states, which were not the problem | Effort fine | Low | **Last (#16)** |
| §4 | Golden master of effective defs | TRUE absent: no committed post-patch snapshot. `patch_targets.py` demands at least 1 match; `expectations_manifest.py` is hand-written | A patch that still matches but now matches the wrong node is invisible today | `effective_def_lint.py` already builds the merged tree, so about 3 h | Churn on every legitimate def edit, so review is a diff, not a verdict | **Promote to #6.** Unattended, no game |

## 4. Methods stage 1 missed

Each entry uses the same fields.

### 4.1 Blind ruling-derived properties (spec-based, N-version by author) — NEW #2

- **What.** A second agent reads only the owner's rulings (the docstring quotes, `standing_rulings.md`, item rulings)
  and the kernel's public world interface (`RM_IFlowWorld`, `ArrayWorld`), never the kernel or the oracle. It writes
  properties: "a limitless source fills every dug square 4-connected to it", "a closed basin conserves volume", "a
  sink drains its run to empty", "a too-wide field with little water is one patch, never 0, deep, 0". They run under
  the shipped flags.
- **Nearest existing.** `RulingsWetDoorWakeBottleChecks.cs`, `HoseRulingTextChecks.cs` and
  `selftest_species_skin_rulings.py` are hand-written by the code author. There is no blind authorship anywhere.
- **Would have caught.** This bug. The only instrument that did catch it was a physical property, while the port
  oracle agreed with both defects. The canal stall too: "a fed D=1 run fills".
- **Effort.** 4 h for FlowWorks. Unattended authoring and running; a red is triaged by FOUNDRY, not the owner.
- **False positives and incentives.** A blind author will misread rulings. Each red is a question (is the ruling or
  the code wrong?), so it needs a referee who is neither author. Never let the kernel author edit the property to
  green.

### 4.2 Oracle-independence audit — NEW #4

- **What.** Classify every differential check:
  - Is the "oracle" a port (does it name the method it mirrors, and is it co-changed with the kernel)?
  - Or is it independent (written from a spec, by another author, with a different algorithm)?
- Report the co-change ratio per pair: FlowKernel ↔ `validation_v2` is 7/14. A port is reported as "transcription
  check", never as N-version.
- **Nearest existing.** Nothing. The skills `evaluation-independence` and `grader-validation` state the rule, but no
  tool measures it.
- **Would have caught.** It would not have found the bug. It would have stopped "kernel==oracle 3000/3000" being
  cited as evidence that the canal behaviour was right.
- **Effort.** 1–2 h, git-only, unattended.
- **False positives.** A co-change can be a legitimate spec change; read the ratio, not a threshold.

### 4.3 Uncapped failure rates in fuzz families — NEW (fold into pilot 1)

- **What.** A `--rate` mode, or a counter, so each family reports `fails/n` and the first K shrunk examples, instead
  of stopping at K.
- **Nearest existing.** Each family returns at most 3–8 failures, in 44 files.
- **Would have caught.** Stage 1's "5/400" (really 194/2000, about 9.7%). A rate also separates "this fix moved
  25/2000" from "still red".
- **Effort.** About 1 h for a shared helper; mechanical edits after that.
- **False positives.** None; it costs CPU on red runs only.

### 4.4 Adapter-flag parity lint — NEW (fold into pilot 1)

- **What.** Parse the adapter lines that copy Mod Settings into kernel bools (`RM_MapComponent_Excavation.cs:1827-1834`
  for FlowWorks). Look up each setting's shipped default in `RimMandrakeFlowWorksMod.cs`. Refuse if no SelfTest
  family constructs a kernel with that bool at its shipped value.
- **Nearest existing.** `lint_kernel_guards.py` (structural only) and `settings_audit.py` (initialiser == Scribe
  default).
- **Would have caught.** Every family running at `false` while the game ships `true`.
- **Effort.** 2 h, unattended.
- **False positives.** A kernel bool with no adapter line; waive with a comment.

### 4.5 Fake-vs-source tool contracts (offline differential of bridge fakes) — NEW #7

- **What.** From each JawaBench `[Tool]` C# method, extract the response keys it can return, and whether a "success"
  can carry a zero-effect payload (for example `totalDamageDealt`). Then require:
  - every MockGame or offline fake answers with the same keys;
  - every harness reader that judges that tool reads the effect field.
- **Nearest existing.** `fake_contracts.py` (one rule) and `tool_schemas.json` (parameters only).
- **Would have caught.** Dhoggur, which is still unguarded today, and the destroy_batch class, with no live time.
- **Effort.** 4–6 h, unattended.
- **False positives.** Dynamic response building (dictionaries assembled at runtime) will be UNMEASURED, not passed.

### 4.6 Production-input replay — NEW #13

- **What.** Feed the kernels real map grids read from savegames (`rimbench/savemap.py`), at real size: 250×250,
  `maxComponentCells` 6000, seam rotation. Today's random worlds are 3–12 cells on a side.
- **Nearest existing.** None. All fuzz worlds are small and random.
- **Would have caught.** Partition and seam behaviour, which no small grid exercises (`FLOW_ORDER_EXTERNAL_INPUT_1`
  part 2 was found live). This is unmeasured for the current bug class.
- **Effort.** 6 h. The save must come from the same def set (the shortHash trap).
- **Maintenance.** Fixtures decay with saves; fingerprint them.

### 4.7 Seeded-bug detection rate for each northstar harness — NEW #5

- **What.** Generalise FlowWorks' O-LIVE-NEG to every mod with a `--mock` tier: inject each MockGame fault and
  report detection rate = rows that went red / rows that should have.
- **Nearest existing.** `validation_v2` O-LIVE-NEG (43/43 for FlowWorks only) and MockGame faults in
  `northstar_driver/transport.py`.
- **Would have caught.** Harness rows that cannot fail. It measures the instrument instead of trusting it, which is
  what stage 1's mutmut was trying to do, and is cheaper.
- **Effort.** 3 h plus 30 min per mod, unattended.

### 4.8 Ranked low, with reasons

- **Canary or shadow kernel.** Run the old and new kernels side by side in a dev-mode build and log any divergence.
  It needs a deploy and live time, it is the owner's slot, and it is redundant with §4.6 for kernels. **#14.**
- **Test-impact analysis.** It largely exists: `suite_evidence.py` skips deterministic tests whose inputs are
  byte-identical, `run_selftests.py --only` exists, and the nightly sweep runs everything. Small marginal value.
  **#15.**
- **Def mutation.** It partly exists in `modpack_lint_harness.py`. Extend it only when the golden master (#6) exists,
  because the golden master gives def mutants an oracle.

## 5. Re-ranked list

| rank | method | stage-1 rank | first target | effort | unattended | game time |
|---|---|---|---|---|---|---|
| 1 | Shipped-configuration matrix + uncapped rates (§4.3) + adapter-flag lint (§4.4) | 1 | FlowWorks, then every kernel with adapter-set bools | 4–6 h | yes | 0 |
| 2 | Blind ruling-derived properties (§4.1) | new | FlowWorks liquids | 4 h | yes (triage by FOUNDRY) | 0 |
| 3 | Coverage of fuzz projects | 2 | FlowWorks + EmpirePursuit | 3 h | yes | 0 |
| 4 | Oracle-independence audit (§4.2) | new | every differential pair | 1–2 h | yes | 0 |
| 5 | Seeded-bug detection rate per northstar harness (§4.7) | new (replaces most of old #4) | mods with `--mock` | 3 h | yes | 0 |
| 6 | Golden master of effective defs | §4 | one patch-heavy mod (UtinniPatches) | 3 h | yes | 0 |
| 7 | Fake-vs-source tool contracts (§4.5) | new | `jawa/damage`, `destroy_batch`, the 10 most-called tools | 4–6 h | yes | 0 |
| 8 | Metamorphic: persist round-trip + split-step, with no rotate-equals | 5 | FlowKernel state round-trip | 4 h | yes | 0 |
| 9 | Generated mutation through the house plant/restore protocol (Stryker only if saturated) | 3 | `RM_FlowKernel.cs` | 4 h (Stryker 8–12 h) | yes | 0 |
| 10 | Per-row verdict history, then statistics | 7 | `status.record_run` append-only JSONL | 1 h, then 3 h | yes | 0 offline |
| 11 | Constant-condition regex lint; Semgrep for the Toil-capture and ExposeData rules | 6 | `src/**/*.cs` | 1 h / 4 h | yes | 0 |
| 12 | Record-replay cassettes | 8 | `transport.py` tap | 4 h | piggyback on a live run | 0 extra |
| 13 | Production-input replay (§4.6) | new | FlowKernel on a real map | 6 h | yes | 0 |
| 14 | Canary/shadow kernel | new | — | — | no | live |
| 15 | Test-impact analysis | new | — | — | — | — |
| 16 | Model checking rimflow | 9 | — | 4–6 h | yes | 0 |
| 17 | Python-code mutation (mutmut) | 4 | only after #5 shows a gap | 4 h | yes | 0 |

## 6. Recommended first three pilots (stage 3)

1. **Shipped-configuration matrix (#1)**, with uncapped rates and the adapter-flag lint.
   - Scope: generalise `FillsFromLimitless(shipped:)` to every FlowKernelFuzz family, then pairwise alternates. Then
     do the same for the next two kernels that have adapter-set bools.
   - Success criterion, written before the run: report `fails/n` per family per configuration. Any red at the shipped
     configuration becomes a filed item with its classification.
   - **Unattended: yes.** Windows `dotnet.exe` on a D: stage.
2. **Blind ruling-derived properties (#2)** for FlowWorks liquids.
   - The author agent gets the rulings and the `RM_IFlowWorld` interface only, plus a negative-control requirement:
     every property must be shown red on a planted kernel defect.
   - A third agent classifies each red (MOD, PROPERTY, or RULING unclear) without seeing who expected what.
   - **Unattended: yes.** Rulings that turn out ambiguous are batched into one question card for the owner later.
3. **Coverage (#3)** of FlowWorks and EmpirePursuit, joined with pilot 1's flag table. A kernel branch with 0 hits at
   the shipped flags is a matrix gap.
   - **Unattended: yes.**

**Rules for stage 3, from the shared-blind-spot finding:**
- The agent who runs a pilot does not classify its reds.
- The kernel author never edits a property or expectation to turn it green.
- Every new check ships with a demonstrated red on a planted defect, as was done for §1's case and the oracle mirror.
- A port-oracle differential is never cited as evidence that behaviour is right.
