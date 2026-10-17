# V&V methods, stage 1: what we already do, and nine methods we don't (2026-10-16)

This is stage 1 of 3, written by a FOUNDRY helper working offline. No bridge, game or deploy was used. Stage 2 picks
pilots and stage 3 runs them. **One pilot was run as part of this survey (§3.1). It turned up a live lead, filed as
`LEVELSET_DIAGNOSE_SHALLOW_RIM_STAYS_DRY`.**

## 0. Bottom line

- The project already does more classic V&V than its name suggests. Hand-curated **mutation testing** of C# kernels
  exists (49 `mutate_*` drivers). So does **stateful property-based fuzzing with shrinking** (66 `selftest_*_fuzz.py`
  wrappers over 55 Verse-free `Source/Kernel/` dirs), and so does **differential testing** against an independent
  oracle (FlowWorks kernel vs Python `PulseOracle`; offline vs live defs via `def_diff.py`). The new methods below are
  ways to **audit those existing instruments**, not replacements for them.
- The weak spot those instruments share: **the same agent picks the inputs, the configurations, the mutants and the
  oracle.** The canal first-cell stall got past a 3000/3000 kernel==oracle differential. The oracle had the same flaw
  ("Oracle mirrored", f11976b49), and the one liveness family that would have caught it never ran with the shipped
  flags (§3.1).
- Ranked by value/cost (detail in §3):

| rank | method | first pilot | effort | game time |
|---|---|---|---|---|
| 1 | Configuration-matrix property runs (combinatorial testing; shipped defaults are mandatory) | FlowWorks `FlowKernelFuzz` under the shipped flags | **done: 1 h probe**; 4–6 h to make it a real feature | 0 |
| 2 | Code coverage of the fuzz projects (coverlet.console, Windows dotnet) | FlowWorks SelfTest + EmpirePursuit fuzz | 3 h | 0 |
| 3 | Tool-generated mutation (Stryker.NET) to audit the hand lists, starting where no list exists | `RM_FlowKernel.cs` (no list at all) | 6–8 h + hours of CPU | 0 |
| 4 | Mutation of the Python harness and oracle (mutmut) | `modcheck/clockgate.py`, `vacuity.py`, `validation_v2.PulseOracle` | 4 h | 0 |
| 5 | Systematic metamorphic relations (split-step, rotate/mirror, save→rebuild→continue) | FlowKernel symmetry + state round-trip; Stillsand split-step | 4–5 h | 0 |
| 6 | Real-parser static analysis (Semgrep / Roslyn analyzers) for our own bug idioms | 4 Semgrep rules over `src/**/*.cs` | 4–6 h | 0 |
| 7 | Verdict statistics and order randomization (flaky-test science) | per-row verdict history from existing modcheck records | 3 h offline | 0 offline; live shuffles later |
| 8 | Record-replay (cassettes) to contract-test the offline fakes | wrap `northstar_driver/transport.py` during the next scheduled live run | 4 h | piggyback only |
| 9 | Bounded model checking of our own state machines | rimflow lifecycle (`rimflow/model.py`) | 4–6 h | 0 |
| — | Runtime contracts in live debug builds; golden master of effective defs | §4 (worth doing, ranked lower) | | |

## 1. What already exists (so nobody proposes it again)

| classic method | what we have | where |
|---|---|---|
| Stateful property-based testing + shrinking | seeded action sequences over the production kernels, invariants after every step, shrinker, `--fuzz-seed N` replay | `src/RimMandrake/Utils/selftest_*_fuzz.py` → `<Mod>/Source/SelfTest*/…Fuzz.cs` (built by `winbuild.stage_build`, run by Windows `dotnet.exe`) |
| Mutation testing (hand-curated) | plant one exact-text defect, demand FAIL, restore byte-identically, record equivalent mutants by hand | `mutate_kernel_fuzz.py`, `mutate_explosivegrowth_fuzz.run_mutations`, 49 `mutate_*_fuzz.py`, `mutations_*.json` |
| Mutation of the lints ("planted breaks") | each lint plants defects into in-memory inputs and must catch each one | `selftest_*_lint.py` (e.g. `selftest_abyss_lint.py` `planted()`), `selftest_utinnipatches.py` |
| Differential / N-version testing | C# kernel vs an independent Python oracle; offline def tree vs live dump | `FlowWorks/Source/SelfTest/selftest_flowworks_kernel_oracle.py`, `def_diff.py`, `animal_live_diff.py` |
| Partial metamorphic testing | "a larger flinch circle never un-flinches", "closer/hotter/darker never un-fires" | `Watchers/Source/SelfTest/WatcherFuzz.cs` only |
| Exhaustive small tables | truth tables, lattice brute force | `Droidworks/…/DroidFuzz.cs`, `Scarlands/…/ScarlandsFuzz.cs` |
| Fault injection (offline) | `MockGame(faults=…)`: zombie, modal, pause_lies, dirty, unfrozen…; per-action refusals in fuzz | `northstar_driver/transport.py`, `Inhabited/SelfTest/InhabitedFuzz.cs` |
| Vacuous-test detection | AST: components that never read back; LLM triage for weak ones | `modcheck/vacuity.py`, `modcheck/jev_triage.py` |
| Silent XML no-op detection | replays Patches/ over the merged tree; a non-test op matching 0 nodes = FAIL | `modcheck/patch_targets.py`, `patch_sim.py`, `effective_def_lint.py` |
| Approval-ish manifests | hand-written expected-def manifests, one runner | `expectations_manifest.py`, `run_expectations.py` |
| Build identity | DLL ↔ source hash stamp; deploy fingerprint | `dll_source_stamp.py`, `.srchash`, `modcheck/run_identity.py` |
| Fake-vs-live contract | one AST rule (destroy_batch never kills pawns) | `northstar_driver/fake_contracts.py` |
| Grader / validity hygiene | validity floors, grader-validation, blind evaluation, negative controls, frozen inputs | skills `validity-floors`, `grader-validation`, `blind-evaluation`; `experiment_manifest.py`; `bridge_validation_observatory.md` §6.1 |
| Environment guards | fog triggers, heat, hostiles, bystander ground (added after each live hit) | `modcheck/testenv_guards.py`, `helpers.clear_bystander_ground` |
| Code-review gate | content-hash CLEAN/DIRTY per file | `code_review_status.py` |
| Selftest scheduling | contention-flaky tests run isolated; nightly full sweep | `run_selftests.py`, `rm-selftests-nightly.timer` |

Searched for and **absent** (whole repo minus `Transient/` and `conversations/`): Stryker/mutmut/cosmic-ray (0 files);
coverlet/dotnet-coverage as tools (0; one hit is a defName); `hypothesis` (not installed); Semgrep/Roslyn
analyzers/`<Nullable>`/`AnalysisLevel` (the only Roslyn hit is `RoslynCodeTaskFactory` in `src/Directory.Build.targets`);
`Debug.Assert`/`#if DEBUG` (0 in `*.cs`); TLA+/TLC/java (no java in WSL); bridge cassettes or recorded responses (0);
flake-rate, Wilson or binomial statistics and test-order shuffling in modcheck/northstar (0); a save→load→continue vs
uninterrupted comparison (proposed in `northstar_review_2026-10-06.md` #9, never built).

Toolchain as measured today: Windows `C:\Users\Mandrake\.dotnet\dotnet.exe`, SDK 8.0.423, with `ilspycmd` already
installed as a global dotnet tool, so other dotnet tools install the same way. WSL has Python 3.14.4 and pip but **no
dotnet**. Each C# method below therefore runs on Windows through `/mnt/c/...dotnet.exe` from a staged copy on D:,
exactly as `winbuild.py` already does. The fuzz projects are `net8.0` console exes, not test-framework projects. That
matters for Stryker (§3.3).

## 2. The incidents used as the yardstick

| incident | what happened | which instrument missed it |
|---|---|---|
| Canal first-cell stall (`CANAL_INLET_DIAGNOSE_FIRST_CELL_ONLY`, fixed f11976b49) | a source-fed D=1 canal sat at 1,0,0,0 for ever under the level solve | kernel==oracle 3000/3000 (oracle shared the bug, then got "mirrored" with the fix); found only by live `validation_v2` fill rows |
| Oracle drift (`FLOWWORKS_ORACLE_SYNC_V2_MISSES_THE_CREEP`) | v2 RED 49/12 after `waterFrontCreepEnabled`: the oracle modelled only thick-liquid creep | differential needs a hand-synced oracle; nothing checks the sync |
| `\|\| true` (BRIDGETOOLS_CSHARP_SWEEP_BUGS_1) | `CapableOf(cap) \|\| true` in `jawa/list_pawns` neutered the capability gate | no static rule; found by a manual sweep |
| Vacuous fuzz invariant (EmpirePursuit, 2026-10-14) | `a \|\| true` invariant, and the warning-hours setter sat inside a comment, so the warning path was never run | 16,000 passing cases; no coverage or mutation over that family |
| Cumulative counter (Stillsand `RM_DuneTrackEraser`) | compares one SetDepth call's delta against 0.08; repeated sub-threshold steps never erase | no split-step relation |
| Save/load (`BURROW_TIMER_SAVE_LOAD_1`) | the safety-cap start tick was a closure local, lost on save/load, so the cap never fired | no save-state round-trip, no static rule for toil-captured state |
| Yume on a vine (SPRINT_SITES_DIAGNOSE_VENOMVINE_SCRATCHES) | 6/6 reruns: the same bystander saved standing on a venomvine cell got scratched | a deterministic SITE fault; reruns cannot vary it |
| Harness 0-damage hit (TheForge Dhoggur lesson 2026-10-16) | `jawa/damage` returned success with `totalDamageDealt 0.0`, read as a mod FAIL | fakes/mock never return "success, no effect" |
| Shared-budget order dependence (`PYRE_HARNESS_SCORCH_CAP_REPAIR_SHARED_BUDGET`) | an earlier row left 35/40 ScorchFruit, so a later row found 0 (FAIL in the full run, 25 PASS alone) | no order randomization, no per-row verdict history |
| Marginal window (`PYRE_SCORCH_YIELD_DIAGNOSE_FLAKY_HARVEST`) | 1500-tick ingest window failed once, passed once at 1200 | no rerun statistics |
| Fake diverges from live (DESTROY_BATCH_NEVER_KILLS_PAWNS_1) | offline fakes removed pawns the live tool never removes | one hand AST rule; no recorded truth |
| Silent def loss | `modExtension` with a missing type discards the def; inherited `<li>` cannot be patched away | offline engine does not model loader-side discards; only a live dump sees them |

## 3. The nine methods

### 3.1 Configuration-matrix property runs (combinatorial interaction testing) — RANK 1, PILOT RUN

**What it is.** Run every property family under the cartesian (or pairwise) product of the kernel's feature flags, and
always under the **shipped defaults**. Pairwise is the classic NIST/ACTS form.

**Nearest existing.** `Program.cs` hand-sets `FlowKernelFuzz.LevelSet = true` for five "rewire" cases and sets it back
to `false` straight after. The generic families construct `ArrayWorld` with every kernel flag at its C# default,
which is **false**. The shipped defaults in `RimMandrakeFlowWorksMod.cs` are `viscosityEnabled`,
`levelBySurfaceEnabled` and `levelSetEnabled` = **true**.

**The pilot (run today).** I copied `FlowWorks/Source` to `D:\Luke\dev\_rmbuild\VV_STAGE1_probe\{pre,post}`
(nothing in the clone was touched). I added one line to the copy of `FlowKernelFuzz.FillsFromLimitless` (the existing
liveness property "every dug cell 4-connected to a limitless source ends full") so it sets the flags, plus a 15-line
`Probe.cs` main. Then I ran 400 seeds per configuration on Windows dotnet:

| kernel | flags off | levelBySurface | levelBySurface + levelSet (shipped) |
|---|---|---|---|
| `f11976b49^` (pre-fix) | OK | OK | **FAIL 5/400** (first: seed 1001) |
| `f11976b49` (current HEAD) | OK | OK | **FAIL 5/400**, unchanged at 20× the pulse budget and with viscosity + creep also on |

The **existing** property, run only at the shipped configuration, goes red on the pre-fix kernel with no new oracle.
That is the class of bug that reached live. On current HEAD the same 5 seeds still fail. Seed 1001 (W=7): a depth-1
cell orthogonally beside a full 4/4 wet cell of a limitless-source region stays 0/1 for ever. Seeds 1014, 1020 and
1023 end one unit short (2/3, 1/2, 1/2). **This is a lead, not a finding.** It may be a real level-set rim defect, or
an `ArrayWorld` modelling gap (how a natural source's surface is declared under the solve), or a property that no
longer holds by design under level-by-surface. Classifying it is owed: `LEVELSET_DIAGNOSE_SHALLOW_RIM_STAYS_DRY`.
Reproduce: `D:\Luke\dev\_rmbuild\VV_STAGE1_probe\post\src\RimMandrake\FlowWorks\Source\SelfTest`, build Release,
`dotnet.exe bin\Release\net8.0\RimMandrakeFlowWorks.SelfTest.dll 400`.

**To make it a real feature (4–6 h FlowWorks, ~1 h per kernel after).** Add a `Flags` struct to each fuzz world, read
from one table that names each flag's shipped value. Every family runs at the shipped defaults plus pairwise
alternates. A lint (in the style of `lint_kernel_guards.py`) refuses a kernel bool that no family exercises at its
shipped value.

**Cost.** CPU only, about ×3–×8 fuzz runtime.
**False positives and maintenance.** Some properties really are configuration-dependent. They need per-configuration
expectations, and an agent "fixing" a red row by narrowing the expectation is the obvious failure mode.
**Cannot see.** Engine glue (the MapComponent → kernel call), Verse behaviour, art, anything outside the flags the
kernel exposes.

### 3.2 Code coverage of fuzz and selftest projects — RANK 2

**What it is.** Line and branch coverage of `Source/Kernel/*.cs` while the fuzz runs, reported per family.
Coverage-guided fuzzing (SharpFuzz/libFuzzer) is the expensive follow-on; not proposed yet.

**Nearest existing.** `northstar_coverage_audit_2026-10-03.md` and the required-check manifest measure **behaviour**
coverage of live scripts. Nothing measures which kernel branches the offline fuzz executes.

**Would have caught.** EmpirePursuit's commented-out setter: the warning-letter branch shows 0 hits. The canal family:
`FillsFromLimitless` shows 0 hits in the level-set solve. It is cheap and unarguable, and it tells you where a
mutation list (§3.3) is blind before you write one.

**Pilot (3 h).** `dotnet tool install -g coverlet.console` on Windows (same route as `ilspycmd`). Then run
`coverlet <SelfTest.dll> --target dotnet.exe --targetargs <SelfTest.dll> --include "[*]RimMandrake.FlowWorks.RM_FlowKernel" -f cobertura`
for FlowWorks and EmpirePursuit, and have a 60-line Python script in WSL turn the XML into a per-file
uncovered-branch list.

**Cost.** Low. Coverlet instruments IL, so there is no source change.
**False positives.** None as such. The risk is misreading: covered ≠ checked. A vacuous `|| true` invariant is fully
covered, which is why §3.3/§3.4 pair with it. Instrumenting also slows the fuzz (~2–5×).
**Cannot see.** Whether any assertion reads the covered result; Verse-bound code (not in the fuzz projects at all).

### 3.3 Tool-generated mutation (Stryker.NET) — RANK 3

**What it is.** Mutants generated systematically by a tool (operator, boundary, boolean, statement removal), not
chosen by the person who wrote the tests.

**Nearest existing.** The 49 hand lists. They are good (Abyss records its equivalent mutants by reasoning), but the
author picks the mutants. **`RM_FlowKernel.cs`, the kernel of the current top priority (GSS/FlowWorks), has no
mutation list at all**: no `mutate_flowworks*` file exists and no `mutations_*.json` names it.

**Would have caught.** Mutants inside the level-set code (`CellKey` ordering, the drop-of-1 swap guard) survive
whenever no family runs with `levelSetEnabled`. Survivors there are the §3.1 signal, raised automatically.

**Pilot (6–8 h + CPU).** Stryker.NET needs a VSTest-style test project. Add a one-`[Fact]` xUnit wrapper that calls
the fuzz `Program.Main` and asserts exit 0, scoped by `--mutate "**/RM_FlowKernel.cs"`. Every mutant reruns the whole
fuzz, so start with a seed-reduced fuzz (`--fuzz-scale 0.1`). Also run it once on Abyss and compare its survivors
with the hand list, which measures how much the hand lists miss.

**Cost.** CPU-hours per kernel (hundreds of mutants × fuzz runtime), then human triage.
**False positives and maintenance.** Equivalent mutants. Typically 10–30% of survivors need a reasoned "equivalent"
note, the same work Abyss already does by hand. Stryker on a staged D: copy must never write back into the clone.
**Cannot see.** Spec errors where test and code agree (the mirrored-oracle case), configuration that is never
exercised but has no code to mutate, and anything outside the kernel files.

### 3.4 Mutation of the Python harness, oracle and judge (mutmut) — RANK 4

**What it is.** Mutate the **instruments**: the clock gate, vacuity lint, verdict classifier, `PulseOracle`. Then ask
whether their selftests notice.

**Nearest existing.** The selftests of `modcheck/*` and MockGame fault injection test the harness against named
faults. Nothing mutates the harness itself.

**Would have caught.** The `|| true` class in Python form; a judge that classifies "success, 0 effect" as a mod FAIL
(the Dhoggur lesson: a mutant that drops the `totalDamageDealt` read should be caught by a harness selftest, and today
it would not be); weakened helpers, which the observatory §6.1 says assertion hashes cannot see.

**Pilot (4 h, all WSL).** `pip install --user mutmut` (first check that it supports Python 3.14; fall back to a
40-line AST mutator using the existing `mutate_kernel_fuzz.py` restore protocol). Targets: `modcheck/clockgate.py`
with `selftest_clockgate.py`, `modcheck/vacuity.py` with `selftest_vacuity.py`, and the `PulseOracle` class in
`FlowWorks/northstar/validation_v2.py` with the offline O1–O11 checks.

**Cost.** Minutes of CPU per module.
**False positives.** Equivalent mutants in logging and formatting code, so exclude print and format lines.
**Cannot see.** Whether the harness matches the live game. Mutation tests the selftest of the instrument, not the
instrument's truth.

### 3.5 Systematic metamorphic relations — RANK 5

**What it is.** When no oracle gives the right answer, assert a relation between two runs: split one step into many,
rotate or mirror the scene, add more source and never get less water, save → rebuild → continue ≡ uninterrupted.

**Nearest existing.** Two monotonicity relations in `WatcherFuzz.cs`. `northstar_review_2026-10-06.md` #9 proposed
save→load→continue; it was never built.

**Would have caught.** Stillsand's cumulative counter: "erase after N steps of δ/N" ≡ "erase after one step of δ"
fails at once. The BURROW class at kernel level: rebuild the kernel from only its persisted fields mid-run, continue,
and compare against the uninterrupted run; any state that lives outside the saved fields diverges. Rotate/mirror on
`RM_FlowKernel` tests whether `CellKey` tie-breaks depend on scan order, the kind of ordering rule that caused the
canal stall. Whether rotation alone would have caught that stall is **unmeasured**.

**Pilot (4–5 h).** Add rotate/mirror and "persist-only round-trip" families to `FlowKernelFuzz.cs` (the kernel's
`depth`/`fill` byte grids are its save surface). Add a split-step family for the dune eraser once its threshold logic
is lifted into a Verse-free kernel; it is a Harmony postfix today, so this one is 1–2 h of refactor first.

**Cost.** Low CPU. The design work is choosing relations that really hold.
**False positives.** Relations that hold only approximately (float rounding, intentional anisotropy such as a
directional flow). Each relation needs a stated tolerance.
**Cannot see.** Errors common to both runs (a bug that is rotation-invariant passes rotation); a live save/load still
needs the game (a quicktest map ~90 s per round trip).

### 3.6 Real-parser static analysis (Semgrep / Roslyn analyzers) — RANK 6

**What it is.** Pattern rules over a real C# syntax tree, plus the .NET analyzers. Full abstract interpretation (e.g.
InferSharp) is out of scope: heavy, and poorly suited to net472 Unity assemblies.

**Nearest existing.** Regex and AST-lite lints: `lint_harmony_targets.py`, `lint_kernel_guards.py`,
`lint_ticker_compat.py`, per-mod `settings-scribed` checks (settings fields only). `src/Directory.Build.props` sets
only the Harmony path: no analyzers, no nullable, no warnings-as-errors.

**Would have caught.** `|| true` / `&& false` / `if (false)` constant conditions (two incidents). A local captured by
a `Toil` lambda and mutated across ticks inside a `JobDriver` (BURROW). A field of a `ThingComp`/`MapComponent`/
`JobDriver` subclass assigned outside its constructor but absent from `ExposeData` (generalises the settings-only
scribe lint). And dead stores (EmpirePursuit's setter moved into a comment leaves an unused variable, CS0219/IDE0059).

**Pilot (4–6 h).** In WSL, `pip install --user semgrep` (it runs here; C# support is GA). Write four rules over
`src/**/*.cs` (179 files carry `HarmonyPatch`; 2,376 `.cs` overall) and triage the first run. In parallel, one
throw-away Windows build of three mod csprojs with `/p:EnableNETAnalyzers=true /p:AnalysisLevel=latest-minimum
/p:TreatWarningsAsErrors=false`, collecting counts only.

**Cost.** Low run cost; triage is the cost.
**False positives.** High for generic CA rules, so curate a small subset. The scribe rule will flag transient caches
on purpose: a `// not-saved: <reason>` waiver comment keeps it honest.
**Cannot see.** XML, runtime types, Harmony patch interaction, anything semantic.

### 3.7 Verdict statistics and order randomization — RANK 7

**What it is.** Treat each live row's verdict as a Bernoulli trial per code fingerprint. Report pass rate with a
Wilson interval. Flag rows whose verdict depends on run order (shuffle, or run alone vs in suite).

**Nearest existing.** `run_selftests.py` isolates contention-flaky selftests. The observatory states that "repetition
is how reliability is estimated", but nothing computes it.

**Would have caught.** The Pyre shared budget (fails in the full run, passes alone, which is the signature of order
dependence) and the marginal 1500-tick window. It would **not** have caught Yume: that site fault is deterministic,
6/6 the same. For that class, vary the fixture seed and require the verdict to be seed-invariant. That runs against
the "static boring test worlds" preference, so it belongs to stage 2 as a question for the owner.

**Pilot (3 h, offline).** Join the existing modcheck records (`infrastructure/state/modcheck_status.json` and the
per-run records) by `(mod, row, run_identity fingerprint)`. List rows with mixed verdicts at an identical
fingerprint. Zero game time. The live part (a shuffled-order arm) costs a full suite run and waits for an owner slot.

**Cost.** Offline: trivial. Live: one extra suite run per shuffle.
**False positives.** Fingerprint granularity: a fixture change that is not in the fingerprint looks like flakiness.
**Cannot see.** Deterministic bugs; rows that only ever ran once (most rows today: report them as UNMEASURED, not
stable).

### 3.8 Record-replay cassettes to contract-test the fakes — RANK 8

**What it is.** Record real bridge request/response pairs once (a golden master of the live tools). Then require
every offline fake and `MockGame` to answer the recorded requests with the same shape and the same refusals.

**Nearest existing.** `fake_contracts.py` (one hand rule), `tool_schemas.json`, MockGame faults.

**Would have caught.** DESTROY_BATCH_NEVER_KILLS_PAWNS_1 (the recorded live answer kept the pawn). The Dhoggur
"success, totalDamageDealt 0" answer would then exist offline, so the harness classifier could be tested against it.

**Pilot (4 h + piggyback).** An opt-in JSONL tap in `northstar_driver/transport.py` writing to `/tmp`, stamped with
the mod-set fingerprint, switched on during the next live run someone is already doing (no extra game time). Then a
replay test of MockGame for the 10 most-called tools.

**Cost.** Low; the cassettes decay with the mod set, so they are fingerprinted and refreshed opportunistically.
**False positives.** Fields that legitimately vary (thing IDs, ticks) need masking.
**Cannot see.** State-dependent behaviour beyond the recorded inputs.

### 3.9 Bounded model checking of our own state machines — RANK 9

**What it is.** Enumerate every event sequence up to length k over a small world (2 seats × 2 items × all verbs).
Check safety invariants (FORBIDDEN never accepted; `replay(events)` equals incremental state; projections idempotent)
and liveness (every non-terminal state has some accepted exit). TLA+/TLC would need Java, which is absent; a 150-line
Python BFS needs nothing.

**Nearest existing.** `rimflow/selftest_model.py` (71 hand cases), the `FORBIDDEN` table, `replay()`.

**Would have caught.** The stuck-state class in `rimflow_system_and_stuck_state_2026-10-07.md` (states with no legal
exit for any seat), and future verb additions that forget an owner exemption (the `reassign` precedent in
`model.py`).

**Pilot (4–6 h).** Do rimflow first, then the BRIDGE hold (take/release/stale-after-45-min/force).
**Cost.** Low.
**False positives.** Low; the work is writing the invariants.
**Cannot see.** Real file concurrency (torn ledger lines; `repair_torn_ledger.py` exists for that), and anything about
the game. **Value to the mods is indirect, hence last.**

## 4. Two more, ranked below the line

- **Runtime contracts in a debug build, run during live sessions.** There are 0 `Debug.Assert`/`#if DEBUG` today. A
  `DEBUG` build of a kernel's glue that checks conservation of liquid volume per pulse and `fill ≤ depth`, logging
  once, would read the **real** game, so it would not depend on a hand-synced oracle (the creep drift). It needs a
  debug DLL deployed (FOUNDRY's call, not this helper's) and must never ship: the `.srchash` guard has to distinguish
  the configurations.
- **Golden master of each mod's effective defs.** `expectations_manifest.py` is hand-authored. A committed projection
  from the `effective_def_lint.py` engine, diffed on every change, catches a patch that still matches but now matches
  something else (`patch_targets.py` only demands ≥1 match). It **cannot** see the loader-side def discards (missing
  `modExtension` type) unless it is built from a live dump, which costs loads.

## 5. Honest limits

- No dotnet in WSL: every C# method stages to D: and runs Windows `dotnet.exe`, as `winbuild.py` does. Stryker also
  needs a test-framework wrapper (the fuzz projects are console exes), so its first run is the expensive one.
- Everything above ranks 1–6 sees **only the Verse-free kernels** (55 Kernel dirs). The Verse glue, Harmony patches
  and XML-to-runtime behaviour stay the job of the live harness, whose cost (quicktest ~90 s, minimal list ~22 s to
  load, full list ~15 min) is why the offline methods rank first.
- Mutation and coverage measure the tests, not the spec. The mirrored oracle is a spec failure. The defence against
  it is configuration-matrix properties at the shipped defaults (§3.1) plus metamorphic relations that do not need an
  oracle (§3.5). Re-deriving the oracle from the code it checks is the anti-pattern to name in the stage-2 rules.
- The §3.1 HEAD failure is unclassified (MOD vs HARNESS fake-world gap vs a property superseded by design). Until
  `LEVELSET_DIAGNOSE_SHALLOW_RIM_STAYS_DRY` is closed, it should not be cited as a FlowWorks defect.
