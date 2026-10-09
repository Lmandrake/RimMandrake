The biggest opportunity is **removing repeated global work while preserving the negative controls**. Increasing the worker count is unlikely to help much; the runner already records 6 workers beating 8.

Two concentrations stand out in the CSV:

- **29 shared lint-harness tests total 528.0 s**, about 28% of the stated 1,886 s aggregate.
- The six slowest tests total **571.2 s**, about 30%. Together with the harness family, excluding their overlap, they account for **1,034.4 s—55% of aggregate test time**.

Those are aggregate per-test seconds, not directly removable wall-clock seconds. Sums of medians from different runs also cannot establish an exact scheduling lower bound for one run.

I read the inlined code and did not run the tests. Below, `Utils/` abbreviates `src/RimMandrake/Utils/`. I distinguish code findings from hypotheses requiring the missing implementations or profiling.

| Priority | Change | Quantitative opportunity | Effort | Coverage risk |
|---|---|---:|---|---|
| 1 | Coordinate concurrent runners and lock Windows stages | Three comparable 300 s runs serialized would take ~900 s, versus the reported ≥1,800 s under contention | Low–medium | Low |
| 2 | Reuse lint indexes; retain individual plants | **528 s family budget**; unchanged-result caching could avoid almost all of it, while cold-run savings need profiling | Medium | Medium: indexes must reflect planted changes |
| 3 | Separate `floor.triage` integration from core modcheck selftests | Most of a **156.7 s file** appears attributable to one real-tree check | Low–medium | Low if that integration check remains mandatory on relevant changes |
| 4 | Split dump integration from fixture proofs; remove duplicate chain calls and large copies | Mandrake + StarWars patch tests total **215.7 s**; the three-test heavy lane totals **229.8 s** | Medium | Low–medium |
| 5 | Move deployed-install audit to deployment/environment validation | **78.7 s per ordinary sweep** | Low | Low for commit validation; important deployment coverage must remain |
| 6 | Cache verified C# builds, then execute tests against those artifacts | **64 `*_fuzz.py` rows total 259.0 s**; build fraction unknown | Medium–high | Medium–high with current staging implementation |
| 7 | Profile fake-world jobs and inject time where appropriate | Live queue + watch + companion detectors total **86.5 s** | Medium | Unknown until helper code is examined |
| 8 | Reduce launcher overhead or batch selected small tests | The runner introduces **17.1 s of launch sleeps** for 342 tests, mostly overlapped | Medium | Low for reservation fixes; higher for shared-process batching |

**The slow-test causes supported by the code are these.**

| Test and median | Code evidence | Diagnosis and limit |
|---|---|---|
| `Utils/modcheck/selftest.py`, **156.7 s** | `t_floor_triage_positive_counts()` calls `floor.triage(runner.ROOT)` and only asserts nonempty rows, one resolvable subject, and a nonempty footer. Its comment attributes an earlier ~110 s run to 112 component declarations and thousands of stat/lstat calls over live data. | A large integration traversal is embedded among small contract tests. The comment is evidence of an earlier measurement; I cannot confirm its breakdown in the current ext4 checkout without `floor.py` and its callees. |
| `src/RimMandrake/MandrakePatches/selftest_mandrakepatches.py`, **111.2 s** | `main()` loads real dump-derived rows. Its nested `fx()` deep-copies **all `rows` for each of eight cases**. A ninth full copy creates `r9`. It calls each clean/failing chain twice. | Confirmed unnecessary copying and repeated evaluation of large inputs. The 2,183 MB peak supports substantial materialized data. Loading, copying, and evaluation fractions are unmeasured. |
| `src/RimStarWars/StarWarsPatches/selftest_starwarspatches_semantics.py`, **104.5 s** | `main()` calls `dump_names()`, later `dump_defs()` for two types, and runs the real chain **10 times when a dump exists**. Four negative cases each invoke `chain(finding)` twice because the diagnostic argument is eagerly evaluated. | Repeated integration evaluations are confirmed. Repeated parsing of the 716 MB JSON is **not** confirmed: `validation.py` might already memoize those functions. |
| `Utils/selftest_deployed_biome_refs.py`, **78.7 s** | `main()` scans Mods, Data, and Workshop. `_scan_root_careful()` still walks and stats files on cache hits. `_scan_workshop_fast()` can launch **16 simultaneous greps** across Workshop folders. | Explicit drvfs traversal and external-install validation. A warm name cache does not eliminate directory traversal. Internal parallelism also multiplies contention across runners. |
| `Utils/selftest_stillsand_lint.py`, **64.8 s** | Inventory reports shared harness and 26 plants. `selftest_modpack_lint.run()` launches a complete lint for the clean baseline, every plant, and the restored baseline. | **28 lint invocations** through the supplied harness shape. Its particular linter was not supplied, so attributing all 64.8 s to `lint_modpack_defs.run()` would be an inference. |
| `Utils/modcheck/live_queue/selftest_live_queue.py`, **55.3 s** | `main()` executes every job body, then repeats several complete bodies under sabotage. `abort_proof` executes at least three times. Save waits are already explicitly zero. | Repeated job execution is confirmed. Real polling waits, image generation, or other helper costs are plausible but unproven without `common`, job modules, and their helpers. Do not blame a save delay already disabled by the test. |

For `selftest_pyrelands_lint.py` (**36.4 s**), the harness and 22 plants imply 24 complete lint invocations. For BrainWorms (**28.2 s**), HugeThings footprint (**27.2 s**), AftermathRites (**24.1 s**), and codex-image (**21.3 s**), only inventory information was supplied. I cannot responsibly name their internal bottlenecks. Static grep flags are investigation leads, not runtime call counts.

**The lint family has the clearest repeated computation—and a correctness trap.**

`Utils/selftest_modpack_lint.py:run()` creates one stripped mod copy, then spawns a fresh Python linter for every plant. Across the 28 flagged tests with numeric plant counts, there are **449 plants and 505 baseline/plant/restoration invocations**, plus the XML-only family.

In `Utils/lint_modpack_defs.py:run()`, each invocation:

- Parses the target’s C# through `scan_csharp(mod/Source)`.
- Parses **all RimMandrake C#** through `scan_csharp(SRC)`.
- Parses target XML, then parses Defs XML again for missing job drivers.
- Reads target C# again into `all_text`, then reads the settings file again.
- Potentially reads other mods’ Defs for name resolution.
- Reads **every XML under repository `src/`** for wiring references, even with `--quiet`.

`--quiet` suppresses warning output, not computation.

I would introduce a lint context containing parsed source and XML indexes. Build the immutable background once, then evaluate each plant against a fresh target overlay. Preserve each plant’s label and expected finding. Keep a few subprocess tests for CLI arguments, exit codes, and output formatting; the hundreds of semantic cases can call the engine directly inside a dedicated family subprocess.

Two details must be corrected before doing that:

1. **Planted C# is not consistently authoritative today.** `our` is scanned from the temporary copy, but `resolve()` uses `allc` scanned from the original repository. A class removed or changed in the temporary copy can still resolve against the unchanged original. The background index must exclude the original target’s contribution, then incorporate the planted target. Simply updating an index leaves deleted entries behind.
2. **Copied-out directories weaken coverage.** The harness excludes Textures by default, while `texpath-resolves` only checks when the texture folder exists. That branch can become quiet in the stripped copy. Add explicit fixture coverage for it, and run the production texture check against actual shipped assets.

The original target also remains in the repository-wide XML wiring scan and other-def index. Those need the same replacement semantics where relevant.

Parametrization alone saves little if each parameter still performs all those scans. The valuable abstraction is **one immutable background plus correctly isolated changed inputs**.

Generic rules such as class resolution, field matching, Scribe consistency, and compile-list completeness can have centralized fixture matrices. Keep mod-specific rules and a clean production check for each mod. For example, FeverWood’s two missing-kernel compile plants exercise the same generic error class, but its gift and tank constraints are distinct coverage. Do not delete them merely because another mod also has a planted-defect test.

**Several tests combine “the checker works” with “today’s environment is valid.” Those should be separate results.**

In `Utils/modcheck/selftest.py:t_floor_triage_positive_counts()`, build a small fixture repository containing a declared walk and a resolvable subject. That proves the traversal and indexing contract cheaply. Retain the real-tree smoke check separately, triggered by changes to discovery, declarations, relevant About files, or indexing code, and run it in the full suite.

For the patch tests:

- In MandrakePatches’ nested `fx()`, copy only the affected row/subtree or restore the precise mutation in `finally`. Preserve the complete fields needed by `effect_findings()`.
- The “installed donor name missing” case makes no row mutation and needs no row copy.
- Store `got = chain(rows)` before calling `check()`. Do likewise for the failing chain.
- In StarWarsPatches, store each `chain(finding)` result once. This reduces real-dump chain executions from **10 to 6** without dropping an assertion.
- Exercise grading and chain wiring with compact synthetic inputs. Run the shipped-patches/current-dump comparison once as an integration check.

The nine MandrakePatches deep copies are a stronger demonstrated target than StarWars’ copies: StarWars copies XML roots and name sets, **not the whole dump** in `brk()`.

An immutable, compact dump projection could be shared across processes. Its key should include the dump content digest, extractor implementation, and projection schema. It must preserve distinctions such as missing definition, undumped type, and present empty fields. Merely moving the JSON to ext4 improves reading latency; it does not remove repeated parsing or Python object expansion.

The inventory’s ecosystem, label-collision, and Utinni dump tests are additional projection-sharing candidates based on their memory peaks. Their implementations were not supplied, so shared parsing there remains an inference.

**Fix verdict completeness before caching anything.**

`Utils/run_selftests.py:run_one()` returns PASS immediately for exit code 0. It checks the UNMEASURED phrase only afterward, for nonzero exits.

Consequently, `selftest_deployed_biome_refs.py:main()` explicitly prints UNMEASURED and returns 0 when prerequisites are absent or a Workshop scan fails, but the runner records **PASS**.

There are further partial-success paths:

- MandrakePatches catches dump-loading exceptions, prints a different UNMEASURED message, skips the dump block, and can return 0. Empty `rows` also skips it.
- StarWarsPatches deliberately substitutes synthetic inputs when the dump is absent; its shipped-data finding assertion is then permissive. Fixture coverage remains, but current-dump coverage was not obtained.
- `selftest_modpack_lint.py` is discovered as a standalone test but has no executable selftest entry point. Bare execution defines the harness and succeeds without exercising it.

Use a structured result with required check IDs, completed check IDs, verdicts, and prerequisite availability. Cache only a **complete measured PASS for the requested coverage contract**. An overall rc=0 is insufficient.

Also reject invalid or empty `--only` selections. Currently nonexistent requested paths can disappear and yield a successful 0/0 run.

**A safe result-cache key needs the execution’s actual input closure.**

A practical starting design is:

```text
SHA256(
    cache schema and verdict-contract version
    + test path and exact invocation
    + test and transitive helper implementation digests
    + canonical input manifest: paths, types, content digests, relevant metadata
    + interpreter/toolchain/dependency identity
    + explicitly controlled relevant environment
    + fixture selections, fuzz seed/scale, and required check IDs
)
```

For the supplied families, the closures are concretely different:

| Family | Required dependencies |
|---|---|
| Generic modpack lint | Test/plants, harness, wrapper, generic engine, extra checker; target source/project/Defs/Patches; all background C# and XML actually consulted; relevant textures/languages; directory membership |
| Patch fixture proof | Checker and runner dependencies, synthetic fixtures, expected checks |
| Current-dump patch comparison | Above plus shipped patches, dump digest, pack definitions, and installed/active mod identities where consumed |
| Ninefold fuzz | Wrapper, `winbuild`, complete evaluated build inputs, C# test/oracle sources, build properties, SDK/packages/runtime, seed/scale/filter |
| Deployed biome audit | Scanner code, deployed biome files, installation identities and complete scanned content snapshot |
| Real floor traversal | Discovery/indexing code, relevant declarations, subjects, and discovered-tree membership |

This must cover **additions and deletions**, not just hashes of previously read files. Missing-path observations and empty globs are dependencies too. Imports alone cannot identify files opened through globbing, project evaluation, or dynamic lookup.

A cached PASS becomes a lie when, for example:

- A dirty, untracked, or ignored input changes while Git HEAD remains unchanged.
- A file retains its size and mtime.
- A new file enters a glob or a previously required file disappears.
- An external dump, deployment, or active-mod set changes.
- A helper changes but only the selftest file is keyed.
- A staged DLL belongs to another clone.
- The prior result skipped required checks.
- A skipped test was expected to produce an artifact that downstream work still requires.

Prefer execution against an immutable snapshot. Pre/post hashing can reject many concurrent changes, but cannot establish immutable execution as strongly.

Use explicit dependency manifests initially; unknown dependencies mean run, not skip. Keep periodic uncached full runs to detect manifest mistakes. Report executed, cached, unavailable, and failed checks separately, retaining the source run and input key for cached results.

**The deployed-biome caches are already unsafe as authoritative freshness proofs.**

`_scan_workshop_fast()` keys the entire Workshop universe by entry count and the largest **integer top-level mtime**. Editing XML deeper inside an existing folder need not change that key. The key also omits the root identity and scanner version.

`_scan_root_careful()` keys file results by size and mtime_ns. That can miss timestamp-preserving edits. Its traversal and read errors are silently skipped. Likewise, `extract_species_refs()` turns a read failure into no references, allowing coverage to shrink.

For authoritative results, use a verified snapshot or trusted deployment generation with a content manifest. Without such a mechanism, freshness requires inspecting the external content; TTLs and directory mtimes are heuristics.

There is also a scope limitation independent of caching: the universe contains names from all installed folders and does not prove a referenced name is a loaded concrete ThingDef after patches. Workshop comments can satisfy names by an explicitly accepted tradeoff. Preserve its useful deployed-presence guard, but do not present its PASS as stronger loaded-game proof.

**C# build reuse is worthwhile, but the current stage is not a safe cache boundary.**

`Utils/selftest_ninefold_fuzz.py:main()` always calls `winbuild.stage_build()` before executing the DLL. `winbuild` already retains Windows `bin/obj`; warm incremental building is existing behavior, not a new recommendation.

The problems in `Utils/winbuild.py:stage_build()` are:

- Stage identity comes from `stage_name` or mod name, not clone or input content. Multiple suites can rsync, build, and execute against the same mutable tree.
- `source_sha()` records HEAD and a dirty boolean. Different dirty contents share that identity.
- `rsync -rt --modify-window=2` can miss same-size changes within its timestamp tolerance.
- `needed_dirs()` is a staging heuristic, not a complete evaluated MSBuild dependency graph.

Lock the entire **stage → build → DLL execution** interval, or use immutable directories keyed by build inputs. Unlocking after build still permits another runner to replace the DLL before execution. Verify staged contents, and ensure incremental compilation cannot reuse outputs after a content change hidden by timestamps.

A build key must include evaluated project/import/Compile/resource/reference inputs, directory membership for globs, Directory.Build files, SDK selection, packages, configuration, and supplied properties. Keep provenance properties if the tests or stamps consume them.

Cache verified build artifacts separately from test results. Executing an already verified selftest DLL preserves fresh runtime coverage while avoiding staging/build cost.

The Linux slice also does not measure or cap the native Windows compiler’s memory. WSL launches Windows executables through host-side interop; the implication is that cgroup peaks cannot represent the whole build footprint. Record Windows resource use separately and verify Windows-child cleanup on timeout. [Microsoft’s WSL interop documentation](https://github.com/microsoft/WSL/blob/master/doc/docs/technical-documentation/interop.md)

**I would make the default suite change-aware, with explicit coverage tiers.**

- **Default:** hermetic contract tests and negative controls; changed-input production lints; deterministic kernel examples and a bounded seeded fuzz workload; required repository policy checks.
- **Relevant-change integration:** full mod-specific plants, current-dump comparisons, real floor discovery, full affected kernel fuzz, asset checks, and Windows staging/build contracts.
- **Nightly/full:** every integration check uncached, larger or rotating fuzz seeds, and checks of dependency-manifest correctness.
- **Deployment/environment validation:** deployed-biome resolution and other checks whose subject is the installed game state.
- **Performance validation:** timing assertions and overhead benchmarks on a quiet machine.

The deployed-biome audit should leave the ordinary per-commit sweep: its primary assertion validates deployed content, while repository discrepancies are warnings only. Run it after deployment and external installation changes.

Keep fake-world job coverage in the default/change-triggered system. “Live queue” in the filename does not make an offline FakeWorld test unsuitable. Likewise, do not move all fuzz or planted defects to nightly.

`selftest_placeholder_lint.py` is explicitly `REQUIRED` in the runner. Preserve that policy coverage; any caching must conservatively include its complete relevant inputs.

**Scheduling changes should address shared resources before adding workers.**

In `run_selftests.py:main()` and `admit()`:

- The heavy lane is local to one invocation. Three runners can launch three heavy tests simultaneously.
- `_RUNNING` reservations are local, and `admit()` returns True when that dictionary is empty even if other runners occupy the slice.
- Reservation registration happens in worker threads; the 50 ms sleep is only a timing heuristic.
- `SEQUENTIAL_ISOLATED` means isolated from this runner, not from other suites.
- Nested Workshop greps and native dotnet workers sit beneath the nominal six-test concurrency.

The simplest first fix is a kernel-held lock serializing full suites. It releases on process death; this differs from a stale lock file or leaked counter. Identical requests for the same immutable inputs can share one completed result.

If concurrent suites must remain supported, use shared admission reservations and separate tokens for heavy memory users, Windows builds, and drvfs scans. Register reservations synchronously before launching, then replace them with observed usage. Keep longest-first scheduling within resource eligibility.

Update timing/peak stores atomically with coordinated merges; current shared `/tmp` writes can overwrite one another. Record successful measured timings separately from unavailable prerequisite checks. The runner’s comment calling CLI a ~150 s long pole is already contradicted by its current 4.6 s inventory median.

Finally, instrument **phases**, not just files: lint scan/index/evaluate, dump read/parse/copy/check, and Windows stage/build/execute. Measure CPU time, elapsed time, queue delay, memory, contention, and external-input cache state. Profile the fake-world jobs before replacing waits, then use injected clocks for logical-time contracts while retaining focused real timeout/process tests.

I would implement concurrency locks and complete verdicts first, then the lint context and fixture/integration split. Those changes attack the largest demonstrated costs while preserving the suite’s essential guard: each checker must still detect its planted defect.