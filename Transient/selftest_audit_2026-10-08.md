# Selftest audit 2026-10-08

Status: complete. Audit only - no selftest or runner code was changed.

## 1. Inventory and timing

- **342** runnable selftests discovered by the runner's own `find_selftests()` (0 excluded). Sanity probe: `selftest_memwatch.py`, `selftest_flyer_lock.py` both FOUND.
- Inventory: `Transient/selftest_audit_2026-10-08/selftest_inventory.csv` (script beside it, `inventory.py`). Timings = the runner's own recorded per-test wall times from three contained 6-worker runs today (`~/.seat-tmp/FOUNDRY/` 14:11, `~/.seat-tmp/BENCH/` 08:22, `/tmp` 07:25); peaks = max recorded `memory.peak`.
- **Suite total: MEASURED from recorded data, not re-run.** Sum of per-test median wall = **1886 s** (range 1798-2049 across the three runs). Contained 6-worker wall = **298 s** (runner docstring, 2026-10-08); 8 workers = 307 s. Under the 3-suites-at-once contention earlier today: 30+ min (reported, not re-measured).
- Shape: 159 tests <1 s, 101 at 1-5 s, 44 at 5-15 s, 31 at 15-30 s, 7 >30 s. The 38 tests >=15 s carry **1206 s (64%)** of the total.
- Wall is **throughput-bound**, not pole-bound: 1886 s / 6 workers ~ 314 s ~ the measured 298 s. So cutting total work maps almost 1:1 to wall; cutting only the long pole does not.

| family | n | sum s | note |
|---|---|---|---|
| per-mod lint, shared planted-defect harness (`selftest_modpack_lint.H.run`) | 29 | 528 | **507 subprocess lint runs** |
| `_fuzz` (dotnet.exe build+run via winbuild.stage_build) | 65 | 260 | deterministic seeds |
| modcheck/* | 26 | 250 | modcheck/selftest.py alone 157 |
| other `_lint` (moddefs_lint etc.) | 16 | 48 | |
| rimflow | 14 | 36 | |
| hooks / skills / artpipe | 25 | 52 | |
| everything else | 167 | 712 | |

Flag census (static grep of the test file only, so an UNDER-count of what imported code does): 103 tests touch drvfs paths (663 s), 66 call `winbuild.stage_build` (284 s), 23 name Windows exes (227 s), 6 peak >1 GB (411 s), 30 run git (65 s).


## 2. Slowest 20 and why

All MEASURED unless marked. "t" = median recorded wall under the 6-worker pool.

| t s | peak | test | why it is slow |
|---|---|---|---|
| 157 | 2.7G | `src/RimMandrake/Utils/modcheck/selftest.py` | one sub-test, `t_floor_triage_positive_counts`, runs floor.triage over the REAL deployed mod tree on drvfs (~17k stat + 26k lstat; ~110 s wall, ~27 s CPU per its own header). Rest of the file is fast fakes. |
| 111 | 2.2G | `src/RimMandrake/MandrakePatches/selftest_mandrakepatches.py` | `validation._dump_inputs` json-loads whole def-dump type files from `/mnt/c/.../DefDump/captures/<id>/defs/` — **ThingDef.json is 406 MB** — plus `_installed_names()` globs ~1.4k `About.xml` across Steam workshop+Mods on /mnt/c. |
| 105 | 2.5G | `src/RimStarWars/StarWarsPatches/selftest_starwarspatches_semantics.py` | `V.dump_names()` loads 7 dump types incl. ThingDef.json (406 MB over 9p) just to build defName SETS. |
| 79-95 | 79M | `src/RimMandrake/Utils/selftest_deployed_biome_refs.py` | scans Steam Mods + Data on drvfs (already parallelised 2026-09-23, 541->~80 s). Live-install check, not a unit test. |
| 65 | 57M | `src/RimMandrake/Utils/selftest_stillsand_lint.py` | harness: ~30 plants -> ~32 lint subprocesses, each rescanning ALL src C# (see §3). |
| 55 | 41M | `src/RimMandrake/Utils/modcheck/live_queue/selftest_live_queue.py` | **54.6 of 55.5 s is `time.sleep`** (cProfile solo, this audit): 364 calls of `clockgate.verify_pause(gap_s=0.15)` against FakeWorld. `verify_pause` already takes an injectable `sleep=`; the selftest doesn't pass a no-op. |
| 36 | 54M | `selftest_pyrelands_lint.py` | lint harness (as stillsand) |
| 28 | 23M | `src/RimStarWars/BrainWorms/selftest_brainworms.py` | resolves xpaths against installed vanilla `Data/` on /mnt/c |
| 27 | 166M | `src/RimMandrake/HugeThings/selftest_hugethings_footprint.py` | image-mask measurement of real textures (PIL) |
| 25 | 57M | `selftest_longshade_lint.py` | lint harness |
| 24 | 26M | `src/RimUtinni/AftermathRites/selftest_aftermathrites.py` (57 s in one run) | vanilla Data on /mnt/c |
| 24 | 39M | `src/RimMandrake/Utils/selftest_gimmesomeslack.py` | oracle export + dotnet.exe build staged on D: + run |
| 23 | 19M | `src/RimStarWars/Sarlacc/selftest_longshade_audio.py` | walks vanilla `Data` Sounds on /mnt/c |
| 22 | 52M | `selftest_cauldron_lint.py` | lint harness |
| 21-36 | 23M | `skills/generating-images/scripts/selftest_codex_image.py` | 815 lines, many cases; python.exe/drvfs paths; small sleeps |
| 21 | 175M | `src/RimMandrake/Utils/art/selftest_placeholder_lint.py` | REQUIRED lint; walks all shipped textures |
| 21 | 54M | `selftest_feverwood_lint.py` | lint harness: 15 plants = 17 lint runs x ~1.1-2.4 s |
| 18-20 | 30-316M | theforge / explosiveknockback / hugethings_titanic / oasismaker / wreckage / kineticarms / nightsideice / structureinjections / watchers / weathersuite `_lint` | lint harness |
| 19 | 116M | `src/RimMandrake/rimflow/selftest_lease.py` | real cli.py subprocesses + `time.sleep(2.2)` + wait-until-time sleeps + git ls-tree/show |
| 18 | 227M | `src/RimMandrake/GimmeSomeSlack/northstar_matrix/selftest.py` | contact-sheet rendering |

**The lint-harness root cause (MEASURED, cProfile of one `lint_feverwood_defs.py` run, 2.38 s):** `lint_modpack_defs.run()` calls `scan_csharp(SRC)` — every `.cs` under `src/`, comment-stripped by regex, then a Python char-by-char brace loop (10.7 M `len()` calls) — **1.94 s of 2.38 s**. `allc` is scanned from the REAL `src/`, not the planted temp copy, so it is **identical for all 507 lint runs in the suite** (only `our = scan_csharp(<copy>/Source)` sees plants). The harness also runs each lint as a fresh subprocess.


## 3. Redundancy and dead tests

**Redundant work (same computation repeated), MEASURED counts:**
1. **`scan_csharp(src/)` repeated 507x** across 29 harness lint tests (~1.9 s each solo) — the single largest redundancy, ~400 s of the 528 s family.
2. **Planted-defect proofs re-run on every run** (449 plants). A plant proves *the lint can fail*; that only changes when `lint_<mod>_defs.py`, `lint_modpack_defs.py` or `selftest_modpack_lint.py` change, or the planted file's anchor text moves. The "clean on the real mod" check (1 run) is the only part that depends on mod content.
3. **The def dump parsed in full by >=4 processes per run** (mandrakepatches, starwarspatches_semantics, utinnipatches_dump 4.5 GB peak; modcheck/selftest.py also peaks 2.7 GB, source not traced) plus ecosystem_pyramid_check / label_collision_check (1.7 GB each, not traced) — 406 MB ThingDef.json over 9p each time, to extract defName sets or a few fields. The capture is immutable per capture id, so a derived slim index (per type: defName set + needed fields), keyed on capture id + manifest hash, would serve all of them.
4. **Vanilla `Data/` and Steam `About.xml` globbed on /mnt/c by ~19 tests (259 s)** — immutable between game updates.
5. **65 `_fuzz` wrappers are one 40-line template** (median 0.65 similarity after name-normalising; differences are csproj/stage name/extra dirs) — each does rsync to D: + its own `dotnet.exe build` (msbuild start-up per project) + run. Seeds are fixed (`new Random(seed)`), so **an unchanged kernel source gives an identical result**: pure re-computation. Could be one table-driven test, one solution build.
6. 29 per-mod lint selftests are already one harness + a PLANTS table each — parametrisation already exists; the waste is execution, not code.

**Dead / unreachable:** `git grep -w` of each file-under-test's stem outside itself and its selftest (sanity probe: `winbuild` 83 refs) returned 32 hits — **all false positives on inspection**: 30 are `lint_<mod>_defs.py` / `moddefs_lint.py`, whose ONLY executor is their selftest (the selftest IS the deployed guard, so the lint is reachable through the suite), and `art/flyer_lock.py` is a hand-run CLI committed today (`e322de57b`). **Confirmed dead tests: 0.** 94 tests have no single file-under-test (they test themselves or a whole package) and were not checked — UNMEASURED.

Consequence worth stating: the 30 per-mod lints never run in any hook or CI except via this suite, so a "fast" tier must keep their **clean-on-real-mod** half or those guards stop running at all.


## 4. Live/bridge/Windows/network tests

- **None drives the live game or bridge** in the default suite as far as static reads show; "bridge" hits (40 files) are FakeWorld/MockTransport fakes. Network: 3 files, ~1 s, mocked.
- **Windows exes:** 66 tests build via `dotnet.exe` (winbuild.stage_build, staged on `D:\Luke\dev\_rmbuild`) — 284 s; codex_image targets `codex.exe` but fakes it.
- **Live-install readers (not unit tests):** modcheck `t_floor_triage_positive_counts` (deployed Mods tree), `selftest_deployed_biome_refs.py` (Steam Mods+Data), the dump readers (DefDump capture on /mnt/c), vanilla-Data readers. These answer "is the installed world consistent" — a nightly / on-change concern, not a per-commit one.


## 5. Runner-level waste

- **Per-test systemd scope cost is NOT the problem** (MEASURED this audit): bare python 8 ms; scope+python 18 ms; scope+runner wrapper 46 ms -> ~16 s CPU / ~3 s wall over 342 tests. Rule it out.
- **No result caching.** A test whose input closure (its file + imported repo modules + the data files it reads) is byte-identical to its last PASS re-runs anyway. The repo already has the content-hash idea (`code_review_status.py`, `.srchash`). Highest-yield targets: 65 deterministic fuzz (inputs = SelfTest dir + kernel Source dir, already passed to stage_build as `extra_dirs`), and the 449 plant proofs.
- **No tiers.** Every invocation is the full 342. 260 tests <5 s sum to 277 s (~46 s wall at 6); the 181 that are also free of drvfs / Windows exes / dotnet builds sum to 109 s (~18 s wall).
- **No CPU-vs-wall record.** The runner keeps wall time and memory.peak but not CPU (`cpu.stat usage_usec` is readable in the same wrapper that reads `memory.peak`). live_queue's 55 s of sleep was invisible until profiled; a wall >> CPU column would flag every such sleeper or drvfs-IO-bound test automatically.
- MEMORY_HEAVY one-at-a-time lane exists only because of the full-dump parses; a slim index removes the lane and its 2-4.5 GB peaks.
- Timings cache lives in TMPDIR per seat (3 divergent copies today) — fine for LPT ordering, but nothing records history, so regressions in a test's time are invisible.


## 6. GPT perspective (independent)

Transcript: `Transient/selftest_audit_2026-10-08/gpt_round1_answer.md` (prompt `gpt_q1.txt`; gpt-6.1-sol, effort high; sent inventory + runner + 10 sample files, NOT my findings). Each claim below was checked against the code by me after it came back.

| GPT claim | verdict |
|---|---|
| `run_one()` returns PASS on rc 0 before looking for the UNMEASURED phrase, so a test that prints UNMEASURED and exits 0 is recorded PASS | **VERIFIED** (runner reads `if proc.returncode == 0: return PASS` first). `selftest_deployed_biome_refs.py` returns 0 on UNMEASURED at lines ~329/344 — VERIFIED. This is a correctness bug and **a precondition for any result cache**. |
| `selftest_modpack_lint.py` is discovered as a selftest but has no `__main__` — bare execution defines functions and "passes" | **VERIFIED** — a guaranteed-green non-test counted in N/N. |
| `--only` with a nonexistent path yields a green 0/0 | **VERIFIED by reading** (nonexistent `want` entries are dropped; the empty-tests guard runs before filtering). |
| Lint correctness trap: `resolve()` uses `allc` scanned from the REAL `src/`, so a plant that renames/removes a class in the temp copy can still resolve against the original | **VERIFIED by reading** `lint_modpack_defs.run()`. Means the cache-allc fix must overlay the copy's Source over a background index with the target mod's own classes REMOVED — not just memoise. |
| StarWarsPatches runs the real chain 10x and eagerly evaluates `chain(finding)` twice per negative case | **VERIFIED**, and worse than GPT could see: `V.patch_semantics_static` calls `dump_names()` AND `dump_defs("ThingDef")` with **no memoisation** (`dump_defs` is a bare `json.load`), so every chain call parses **ThingDef.json (387 MB) twice**. MEASURED one load: read 1.8 s + parse 2.9 s = **4.7 s** (warm cache, harness slice). ~22 loads x 4.7 s ~ **100 s of the 105 s** (count read from code; product INFERRED). |
| MandrakePatches deep-copies all dump rows 9x (`fx()` x8 + `r9`) and calls each chain twice | **VERIFIED** (`copy.deepcopy(rows)` at lines 63, 108; 9 `fx(` call sites; `check(..., chain(rows), chain(rows))`). Fraction of the 111 s UNMEASURED; deep-copying a ~2 GB dict graph 9x is the most plausible bulk. |
| `admit()` returns True whenever THIS runner has nothing in flight, even if another runner fills the slice; heavy lane and SEQUENTIAL_ISOLATED are per-invocation | **VERIFIED by reading**. Explains the 3-suites-at-once 30+ min collapse better than worker count: three runners each admit a heavy test. |
| `winbuild.stage_build` stage identity is the stage name, not the clone — two suites can rsync/build/execute against the same D: tree | **VERIFIED by reading** (`stage_name=` fixed strings like `NinefoldFuzzSelfTest`). A cross-runner race, and a reason a fuzz/build cache must key on content, not on `.srchash`'s HEAD+dirty bit. |
| deployed_biome_refs workshop cache keyed on entry count + top-level mtime; can launch 16 greps | **UNVERIFIED** (not re-read; plausible from the 2026-09-23 rewrite notes). |
| Recorded timings stores overwrite each other across runners | **VERIFIED by reading** (`save_timings` read-modify-write, no lock) — low impact (ordering only). |
| "selftest_cli.py ~150 s long pole" comment is stale (4.6 s now) | **VERIFIED** against the CSV. |


## 7. GPT perspective (after findings)

Transcript: `Transient/selftest_audit_2026-10-08/gpt_round2_answer.md` (prompt `gpt_q2.txt`; sent this file through §6 + runner + lint lib + 2 samples). New material only:

| GPT round-2 point | verdict |
|---|---|
| A signal death can be classified UNMEASURED (not FAIL): the signal branch only appends text, then falls into the UNMEASURED classifier | **VERIFIED by reading** `run_one()` — the appended "KILLED by signal" line contains no `FAIL`, so a child that printed the phrase then died exits the run green. |
| Timeout cleanup `p.communicate()` after killpg has no timeout — an escaped descendant holding the pipe can hang the runner | **VERIFIED by reading** `_run_capped()`. |
| Lint "untouched copy is clean" is not "the shipped mod is clean": harness drops `Textures/` (and Languages/About) so `texpath-resolves` goes quiet | **VERIFIED by reading** the `ignore_patterns` list. So texture-path checking of 29 mods runs nowhere unless a wrapper passes `keep`. Needs a clean run on the REAL mod dir. |
| The repo-wide XML "wired" scan and `other_defs` also read the original tree, so overlays need replacement semantics for XML as well as C# | **VERIFIED by reading** (same pattern as `allc`). |
| My 507 x 1.94 s = 984 s exceeds the family's 528 s, so the estimate is inflated | **Correct critique.** The 1.94 s was under cProfile; a plain run is 1.14 s total (MEASURED). Re-estimated: scan_csharp(src) ~80% of ~1.1 s x 507 ~ **~420 s**, INFERRED; needs a before/after family benchmark. |
| `time.sleep(0.05)` per submission ~17 s serialised dispatcher time; `wall_start` excludes probe+discovery | **VERIFIED by reading.** Small now, material once tests are fast. |
| Governance: per-guard evidence receipts (input fingerprint, env fingerprint, case count, outcome) with executed / reused / missing shown separately in the denominator; nightly bypasses receipts to audit the dependency declarations; first failure is retained (no silent rerun-to-green); new tests declare inputs and take a budget | Design proposal, not a code claim. Fits the repo's existing content-hash habit (`code_review_status.py`). Adopt as the cache design. |
| Virtual clock for `verify_pause` rather than a no-op sleep, to keep the "ticks moved during the gap" negative cases | Sound refinement of my fix. |
| A fork-server/persistent worker is NOT the lead: interpreter start is cheap, and tests monkeypatch module globals (StarWars swaps `V.patch_findings`) so shared processes leak state | Agrees with my scope measurement (46 ms/test). Rule it out. |
| Honest budget: with lint, fuzz, the two patch tests, floor, deployed-biome and live-queue all removed from execution, ~590 aggregate s remain ~ 98 s at perfect 6-way — <2 min is plausible for routine commits only with receipts, and modcheck's 157 s real-tree check alone breaks it unless its freshness can be established or it moves cadence | Arithmetic checks against the CSV. Accept: the <2 min target is for **routine commits with reuse**, not a cold run. |

**What GPT got wrong or could not see:** round 1 did not find that StarWars re-parses ThingDef.json inside every chain call (it hedged "validation.py might already memoize" — it does not), and so under-ranked a ~100 s, ~5-line fix; it attributed live_queue to "repeated job execution", but cProfile shows 98% is `time.sleep` in `verify_pause`; it did not measure the scope overhead and proposed reducing launcher overhead (item 8) which is ~3 s wall.


## 8. Ranked recommendations and tiering

Savings are aggregate test-seconds (wall ~ /6 while throughput-bound). MEASURED = profiled or timed this audit; INFERRED = from code + recorded time.

| # | change | est. save | effort | risk | basis |
|---|---|---|---|---|---|
| 1 | **Memoise `dump_defs`/`dump_names` in `src/RimStarWars/StarWarsPatches/validation.py`** (per-process cache) and bind `got = chain(..)` once in the selftest | **~95 of 105 s**, and 22 x 2.5 GB peaks -> 1 | tiny | none (same data, same process) | 4.7 s/load MEASURED x ~22 loads read from code |
| 2 | **`selftest_live_queue.py`: virtual clock into `clockgate.verify_pause`** (it already takes `sleep=`) | **~54 of 55 s** | tiny | low if the virtual clock keeps the ticks-moved-during-gap cases | cProfile MEASURED: 54.6 s in 364 sleeps |
| 3 | **Lint harness: build the background C#/XML index once per run, overlay the target copy with replacement semantics** (fixes the `allc` coverage trap too); add a clean run against the REAL mod dir (restores texpath checks) | **~420 of 528 s** | medium | medium — overlay must remove the target's original classes/XML | 0.9 of 1.1 s/run is `scan_csharp(src)` (profiled); x507 INFERRED |
| 4 | **Receipts for deterministic work**: 65 fixed-seed fuzz + 449 plant proofs skip when their declared input closure (wrapper, harness, lint/kernel source, SelfTest dir, toolchain id) is byte-identical to a recorded executed PASS; unknown inputs => run | fuzz ~260 s + plants ~(remaining) on routine commits | medium | medium — needs #6 first; nightly runs uncached | seeds fixed (`new Random(seed)`) read from code |
| 5 | **MandrakePatches: mutate-and-restore one row instead of 9 full `deepcopy(rows)`; bind chain results once** | most of 111 s (INFERRED) | small | low | deepcopy sites read from code |
| 6 | **Runner verdict fixes (precondition for any caching)**: UNMEASURED-with-rc-0 must not be PASS; signal death always FAIL/KILLED; empty `--only` is an error; bounded cleanup after timeout; un-discover `selftest_modpack_lint.py` (library, not a test) | 0 s, correctness | small | none | all VERIFIED by reading |
| 7 | **Machine-wide suite lock** (flock held by the runner; second invocation queues and says so) and shared admission across runners | the 30+ min contention case -> ~3 x 5 min serial | small | none | `admit()` per-invocation VERIFIED |
| 8 | **Split live-install checks into an `env` tier**: modcheck `t_floor_triage_positive_counts` (~110 s; keep a small fixture-tree version in default), `selftest_deployed_biome_refs.py` (~80 s), vanilla-Data readers when Data's version stamp is unchanged | ~190 s+ per commit | small-medium | cadence change: run on deploy / game update / nightly | header measurements in those files |
| 9 | **Slim dump projection** (per capture id: defName sets + the few fields used), shared by the 6 dump readers; removes the MEMORY_HEAVY lane | rest of the ~411 s heavy group after #1/#5 | medium | parity test vs full reader required | ThingDef.json 387 MB on /mnt/c MEASURED |
| 10 | Record CPU (`cpu.stat usage_usec` in the wrapper beside `memory.peak`) and keep timing history; flag wall >> CPU | finds the next live_queue | tiny | none | — |

**Proposed tiering** (flags on `run_selftests.py`):
- `--fast` (pre-commit default target <2 min wall): every test whose receipt is invalid, plus all hermetic tests; lint clean-runs always; plants and fuzz only when their closure changed. Excludes the `env` tier. Today, before any fix, the 181 tests that are <5 s and touch no drvfs/Windows exe/dotnet sum to 109 s (~18 s wall); all 260 tests <5 s sum to 277 s (~46 s wall).
- `--full` (nightly, and before a release): everything, receipts bypassed, compares fresh vs receipt verdicts.
- `--env` (after deploy / game update / dump capture): live-install readers.
- Rule for new tests: declare a tier and inputs; a test >15 s in `--fast` fails a budget lint unless it names an exemption.

**Dead / redundant list:**
- Dead tests: **0 confirmed** (32 grep hits all false positives — selftest-only lint executors and a hand-run CLI). 94 tests without a single file-under-test UNMEASURED.
- Non-test counted as a test: **1** — `src/RimMandrake/Utils/selftest_modpack_lint.py` (library, no `__main__`, always green).
- Redundant computation: **29** harness lint tests (repeated `scan_csharp(src)` x507), **65** fuzz wrappers (one template, deterministic re-runs), **3** tests repeating full dump loads/copies (StarWars x~22 loads, Mandrake x9 deepcopies, Utinni 4.5 GB), **1** sleep-dominated test (live_queue). Total **98** tests with removable repeated work; none is redundant in WHAT it guards — each family guards distinct mods/kernels, so merge execution, keep cases.

**What GPT added that I missed:** verdict holes (rc-0 UNMEASURED = PASS; signal -> UNMEASURED; empty `--only` green; harness library counted as a test), the `allc`/XML coverage trap in the lint overlay, the stripped-`Textures` blind spot, cross-runner admission and shared D: stage races, unbounded timeout cleanup, receipts-as-evidence governance, and the honest framing that <2 min is a routine-commit target, not a cold-run one. **What it got wrong:** missed the StarWars per-chain re-parse (my top win), misattributed live_queue, overweighted launcher overhead; it correctly caught my inflated 984 s lint figure.


## Progress
- 18:50 inventory done: 342 tests, median-sum 1886 s CPU (recorded timings, 3 runs); reading slow 20
- 19:00 slow-20 reasons gathered (dump on /mnt/c 406 MB ThingDef.json; lint harness rescans all src C#; 66 dotnet.exe builds); reachability next
- 19:15 sections 1-5 written; building GPT bundle
- 19:20 GPT round 1 (independent) sent
- 19:35 GPT round 1 back + verified; round 2 (findings, ask for DIFFERENT angles) sent
- 19:50 synthesis written; publishing
