Every claim in the frozen statement is supported by the source and the raw outputs, and I found no material defect. All three bullets are **true**.

### Bullet 1 — recognized, disconnected runs; near reached, far excluded: **TRUE**

- **Pipe names:** the fake graph treats any name starting with `c` as a pipe (`HoseNetChecks.cs:47`). The new fixture's cells `cA1`/`cB1` (`:178-181`) are therefore pipes. The old `a1`/`b1` were not.
- **The pump really reaches T through the pipe:**
  - The pump's only entry point is `cA1` (`Seeds`, `RM_LiquidNetKernel.cs:312-318`).
  - Building from `cA1` attaches T through the pipe-to-tank contact (`:372-375`).
  - `StoreOf` (`:537-566`) then lists T with the route found by `RouteIn` (`:520-534`), which is empty because both attach at the same node.
- **No shortcut:** `g3` has no touching tanks, no hoses and no pipe adjacency, so there is no alternate path and the two runs are disconnected.
- **The assertion checks both directions:** `Tanks(r3).SequenceEqual({"T"}) && Route(r3,"T")==""` (`:183`) requires the pump to reach T, not only to miss TV.
- **Both runs are tested to exist:** `:186-189` checks that both components are non-null and distinct, that both hold T, that only the far one holds TV, and that `ComponentsOf("T").Count==2`. T's two contacts come from `OriginPipeCells` (`:55`). This matches design §3.1:108 and the kernel header `:8-10`.

### Bullet 2 — meaningful controls; production-linked selftest passes: **TRUE**

- **Old fixture (reproduce run):**
  - It ran on the pre-change file (hash `c5d0cc…`, matching `integrity_original.json:474`).
  - Output: `MEASURED roles a1=None b1=None tanks=[]`. The old exclusion check passed anyway, so it proved nothing. The repaired assertion failed (`fast_reproduce/stdout.txt:1-3`).
- **Old fixture against the new assertion:**
  - `fast_old_fixture/hose.diff` only renames `cA1`→`a1` and `cB1`→`b1`; `kernel.diff` is empty.
  - Exactly the two targeted checks fail (`stdout.txt:12-13`) and the other 38 pass.
- **Tank-conduction mutant:**
  - `kernel.diff` adds a pipe→tank→`OriginPipeCells(tank)` hop in Build pass 1, and records the step so the canonical re-rooting stays consistent. `hose.diff` is empty.
  - Tracing it by hand, `cB1` joins the near component, so TV is reached and near==far. That matches the two FAILs at `fast_tank_conduction/stdout.txt:12-13`. All 38 other checks pass.
- **No instrument error:** both mutants ran in their own stage, compiling the complete production kernel and `HoseNetChecks.cs`. Since all other checks passed, no unrelated suite or tool fault explains the failures.
- **Production linkage:**
  - The SelfTest csproj compiles `..\Machinery\RM_LiquidNetKernel.cs` (`:209`) and `HoseNetChecks.cs` (`:242`); `HoseChecks.cs:58` runs the suite.
  - Wrapper result: `PASS 1/1`, `RESULT: GREEN` (`selftest_stdout.txt:6-9`).
  - The raw stdout shows `HoseNetChecks: 40/40` (`csharp_stdout.txt:1487`), and the strace shows the wrapper and runner exiting 0 (`selftest_output_writes.strace:23,30`).

### Bullet 3 — exact tested source, limitations, preservation: **TRUE**

- **Source identity:**
  - Final `HoseNetChecks.cs` is `5b6470…` and the kernel is `738d60…` in every receipt.
  - Between the original and the before-review snapshots, only `HoseNetChecks.cs` changed (`changed_since_original`), so the kernel and all GSS/`_Shared` sources and media are unchanged by hash.
- **Mutants stayed isolated:** the mutant kernel (`4c598e…`) existed only in the staged copy. Every receipt records the real source as `738d60…` and `staged_inputs_match_saved: true`.
- **Wrapper inputs:** the wrapper scripts (`selftest_flowworks_stock.py`, `winbuild.py`, `selftest_winstage.py`) have identical hashes before and after.
  - The after-test integrity snapshot shows the staged copy matching the source (`missing: []`, `mismatch: []`, `same_as_test_input: true`).
  - The staged DLL was rebuilt after the probe runs.
- **"Changed during the run":** that note in the wrapper stdout is about whether the result could be cached, not about test results. The script's hash did not change.
- **Limitations** are written down in `proof_checks.json:78`.

### Limitations and minor defects (none material)

1. The raw production stdout only gives `HoseNetChecks: 40/40`, not the case names. The named PASS lines come from `fast_final`, which ran the same source hashes behind a stub `Program.Check` and produced the same 40 checks.
2. The graph is fake: each "run" is a single cell, with no real map geometry and no live game. The adapter `RM_LiquidNet.cs` is not exercised.
3. The mutant covers only one form of tank conduction: pipe→tank→pipe. Conduction across hoses is covered by the existing TU checks, not by this mutant.
4. The negative controls ran only in the fast stub harness, not in the full wrapper.
5. The GSS cord appearance is preserved because the files are unchanged by hash; it was not visually re-approved. Media files are excluded from staging.
6. The refusal row in `cache_record_refusal.json` gives different reasons (`/etc`, the clock, external dotnet) than the stdout's "changed during the run: selftest_flowworks_stock.py". There is also an unparseable line 1462. This is a bookkeeping mismatch about cacheability only and does not affect the executed result.

would show: yes