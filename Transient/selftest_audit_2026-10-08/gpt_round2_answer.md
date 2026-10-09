The main constraint is **what “under two minutes” must mean**. A routine commit can reuse valid evidence and stay below that target without dropping guards. A cold run, or a commit that invalidates every expensive guard, needs a separate measurement. The supplied timings do not support promising both within three small commits.

Labels below: **Reading** means the inlined implementation establishes the claim; **Inference** means a prediction or a dependency on files supplied only through your audit.

**Three additional correctness issues affect the optimization plan.**

- **Reading — the default lint fixture does not exercise texture existence.** `selftest_modpack_lint.py:run()` omits `Textures` unless a wrapper explicitly includes it in `keep`. In `lint_modpack_defs.py:run()`, `texpath-resolves` checks missing images only when the containing directory exists. Consequently, “untouched copy is clean” is not equivalent to “the shipped mod passes every lint check.” Keep the mutation fixture small, but add an explicit clean invocation against the actual mod directory. Wrappers that already retain textures need separate inspection.
- **Reading — a signal death can become an accepted UNMEASURED result.** In `run_selftests.py:run_one()`, the signal branch appends diagnostic text and then continues into the UNMEASURED classifier. A child that prints the convention phrase before receiving SIGKILL or SIGSEGV can become UNMEASURED; `main()` permits that status to exit successfully. Signal termination must establish a failing verdict before interpreting output.
- **Reading — the advertised timeout has an unbounded cleanup step.** `_run_capped()` ends its timeout handler with `p.communicate()` without another timeout. **Inference:** if an escaped descendant survives cleanup and retains a pipe, the runner can still hang. Use a bounded cleanup grace period, then close the pipes and report cleanup failure. This matters when enforcing an actual suite deadline.

There is also a coverage trap beyond the class-index overlay you already identified. **Reading:** `lint_modpack_defs.py:run()` consults the original tree through both `other_defs` and the final repository XML scan for “wired” classes. A planted deletion can therefore retain evidence from the shipped file it supposedly replaced. Any shared lint context needs replacement semantics for **C# and XML**, with the target’s original files removed before adding its fixture files.

**I would change the interpretation of the timing estimates.**

Your 1886 seconds are summed **per-process wall times**, not CPU time. Nested build concurrency, sleeps and IO all contribute. The proximity to six times the suite duration suggests high worker occupancy; it does not establish that removing one second of work removes one-sixth of a second from suite wall.

Two consequences:

1. The isolated tail and serialized heavy lane remain separate constraints. Removing pool work eventually stops helping when either dominates.
2. `507 × 1.94 seconds` is about **984 seconds**, exceeding the entire recorded lint family. That profile is useful attribution, but its absolute duration cannot be multiplied into a savings estimate for the recorded runs. The proposed ~400-second saving needs a family-level before/after benchmark.

**Reading:** `main()` also introduces `time.sleep(0.05)` after every pooled submission. At roughly 342 submissions that is about **17 seconds of serialized dispatcher activity**, much of it overlapping execution. It becomes material once the tests get fast. Replace the delay with an acknowledgment that the submitted task has registered its reservation; do not simply delete it and reopen the admission race.

Finally, `wall_start` occurs after containment probing, discovery and timing loads. **Reading:** the displayed wall time excludes those costs. A commit-budget measurement must start at process entry and include receipt validation, queueing, setup and the isolated tail.

**The execution mechanisms I would prioritize differ from a general persistent worker.**

| Mechanism | Practical choice and coverage constraint |
|---|---|
| Shared Python worker / fork-server | Ordinary interpreter startup has too small a measured ceiling to lead the work. A reusable process also changes isolation: the supplied StarWars test monkeypatches module functions and maintains global `FAILS`. Prefer sharing immutable expensive data first. A fork-server is worthwhile only for an explicitly opted-in family, with children retaining per-test containment and attribution. |
| Collection | Introduce stable case IDs and a cheap collection manifest before adopting pytest. Importing every test to collect it can execute expensive setup or collide on generic module names such as `validation` and `runner`, which the StarWars test resolves through `sys.path` manipulation. Collection should list cases without loading their large inputs. |
| JSON access | `mmap` alone does not eliminate parsing or the Python object graph. Streaming helps build a projection; it does not make repeated full scans cheap. A read-only SQLite projection is attractive for selective queries across processes. Preserve order, duplicate rows, and missing-versus-null distinctions wherever consumers observe them. |
| ext4 mirrors | Useful for immutable captures and versioned vanilla inputs. A mirror of the deployed mod tree must have trustworthy freshness evidence. Otherwise it changes “installed world is consistent” into “an earlier copied world was consistent.” Include mirror construction and validation in the cold-run benchmark. |
| One .NET solution | Worth testing after the larger waste is removed. It saves build orchestration, not all compilation or execution. Bound internal build parallelism so six runner workers do not each launch another wide build pool. Verify output/intermediate-directory separation before batching. |
| Diff-driven selection | Start with conservative declared input groups. An import graph is insufficient: these tests also consume XML, textures, executable versions, subprocess scripts and installed state. Unknown dependencies must invalidate broadly. Optimize selection precision later. |

**Inference:** Linux `memory.peak` also should not be treated as a complete resource measurement for host-side `dotnet.exe` work. Your audit identifies Windows builds, but the staging implementation was not inlined. Verify that accounting boundary before using low recorded peaks to admit many builds.

**The governance mechanism should be an evidence ledger, not merely a fast/full tier switch.**

Each guard should produce a receipt containing its stable identity, input fingerprint, environment fingerprint, outcome, case count and resource measurements. The commit summary should distinguish **executed PASS**, **valid prior PASS**, and **missing evidence**. Reuse must remain visible in the denominator.

Ownership and cadence can then be simple:

- **Pre-commit:** the six-worker default validates receipts and executes invalidated guards. Unknown inputs mean execution, not exemption.
- **Pre-push or merge:** validate evidence against the exact proposed tree and the required environment. A local successful invocation is insufficient if files changed during its run.
- **Nightly:** bypass receipts to audit dependency declarations, flakes and performance. Compare fresh outcomes with reusable receipts; discrepancies invalidate the affected selection rule.

Assign each expensive guard an owner and an input-contract owner. Require new tests to declare inputs, use injected clocks for simulated waits, and justify subprocess boundaries. A new slow test should consume an explicit suite-budget allocation rather than silently entering discovery.

For flakes, retain the first failure. An automatic rerun supplies diagnostic evidence; it does not rewrite the first run into PASS. Quarantine requires an owner and replacement coverage before the guard stops blocking.

Use one machine-wide coordinator for the six execution slots and exclusive tests. The cheapest implementation is a kernel-held suite lock with a visible queue; identical requests can share an evidence receipt. That lock coordinates execution—it does not replace cgroup memory accounting. Queue time counts toward the user-facing deadline.

**The first three commits I would make are these.**

1. **Make evidence trustworthy and budget measurement complete.**

   Incorporate the correctness repairs already agreed, plus signal-verdict precedence, bounded timeout cleanup and the real-directory clean lint check above. Add structured receipts, conservative input groups, CPU measurements and an end-to-end clock. Coordinate simultaneous suite invocations with the machine-wide lock.

   Receipt validity must include relevant untracked files, additions/deletions, interpreter/toolchain identity and declared external inputs. Validate that the tested inputs remained stable, or execute against a stable snapshot. Do not initially attempt precise import-graph selection.

   **Acceptance:** malformed, incomplete, stale or unrunnable evidence cannot satisfy a required guard. The summary accounts for every guard, including reused evidence.

2. **Give the lint family one immutable repository context.**

   Build the background C# and XML context once per stable run snapshot. Keep fixture scans fresh; overlay replacement files for every repository lookup described above. Preserve `scan_csharp()`’s current alias/collision behavior during the performance change—its `setdefault()` behavior makes reconstruction order observable. Give callbacks fresh mutable class records so one plant cannot contaminate another.

   Keep subprocess isolation initially. Sharing the expensive context captures most of the expected benefit without introducing worker-state contamination. Cache proof receipts only against the conservative closure of the harness, wrapper, callback, anchor files and background context.

   **Acceptance:** all plant IDs remain represented; invalidated plants execute; real-directory checks remain mandatory when their inputs change. Compare fresh diagnostics with the corrected uncached implementation.

3. **Remove repeated environment materialization and simulated elapsed time.**

   Implement the dump projection and inject it into semantic-chain tests as an immutable baseline. Read it once per test process; use isolated mutation overlays instead of repeatedly copying unrelated rows.

   For `clockgate.py:verify_pause()`, inject a **virtual clock that records and advances each requested gap**, rather than a bare no-op. Preserve adversarial cases where ticks advance during that gap, reads fail, or the paused flag is false. This retains the temporal logic the function documents.

   Add receipts for deterministic fuzz inputs with conservative build-environment dependencies. Reuse deployed-world evidence only if its current input identity can be established reliably. Otherwise retain the live check and report that the budget remains unmet.

   **Acceptance:** projection-versus-full-reader parity on the real capture and representative malformed/missing data; virtual-time negative cases still fail; fuzz receipts invalidate on relevant build configuration changes.

**The timing target is plausible for routine commits, but still a hypothesis.** Taking the reported lint, fuzz, two patch-semantic tests, floor check, deployed-biome check and live-queue check entirely out of execution leaves roughly **590 aggregate test-seconds**, or **98 seconds at perfect six-worker utilization**. That allows only a modest margin for setup and tails. Receipt validation costs work too, and changing any of those inputs restores some execution.

Thus the release condition for these three commits should be measured: **under 120 seconds end-to-end on six machine-wide workers, with every guard backed by execution or valid evidence**. If deployed-input freshness cannot be established cheaply, the supplied 157-second test alone prevents that promise. Moving it to nightly would change the coverage cadence; it would not satisfy your “without weakening any guard” requirement.