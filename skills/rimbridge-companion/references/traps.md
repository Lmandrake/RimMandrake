# Traps by topic

Lessons folded in from the lessons inbox, by the section of `../SKILL.md` they belong to.

## 4. `build.py`'s guards are right — read them, do not bypass
- **Moving types between mods (or making shared source `internal`) breaks the JawaBench companion with no error until its next build**, because it compiles against the DEPLOYED mod DLLs. Compile-check it against the repo DLLs (no `--apply`): `GSS_MOD_DIR=<repo>/GimmeSomeSlack/Assemblies FLOWWORKS_MOD_DIR=<repo>/FlowWorks/Assemblies python3 src/RimMandrake/bridgetools/build.py`.

## 3. The eleven design rules, each learned by getting it wrong
- **Never add an overload to a public method a bridge tool reflects by name.** JawaBench calls `type.GetMethod("Deepen")` on `RM_MapComponent_Excavation`; a second `Deepen` overload makes it throw `AmbiguousMatchException` at runtime with no compile error. Give the new variant its own name (`DeepenWithin`). Check first: `grep -rn 'GetMethod("<Name>"\|"<Name>"' src/`.
- **A tool's TIMEOUT branch must not clean up through `ctx.MainThread.InvokeAsync`.** The main-thread queue is pumped from Update, so the stall that caused the timeout (frames stopped) makes the cleanup await hang forever and the tool never returns. Disarm with `Interlocked`/volatile fields off-thread, clamp every caller timeout (`timeoutMs=-1` meant wait forever), and always pass `cancellationToken` to `InvokeAsync`.
- **Start no background work that JIT-compiles new methods while startup Harmony patching is still running.** A threadpool SHA-256 archive queued at bridge registration crashed mono natively in a JIT trampoline (`HashFinal`), uncatchable from C#, ~1 start in 3. Warm the code path on the main thread and defer the work until frames show no long event (`JawaBenchTpsSampler.PumpArchive`).
- **Identify a companion DLL by content, not size or build stamp.** A PE file is 512-byte aligned, so a rebuild from different source often has the identical byte count (a file-count+bytes "same" check let a test box run a companion missing `manualPrioritiesOn`). The `AssemblyInformationalVersion` `+<sha>` is the HEAD of whichever clone built it, often a scratch commit absent elsewhere. `build.py` embeds `AssemblyMetadata JawaBenchSrcHash` (hash of the companion sources); `companion_identity.py` compares it with the git tree at the job's sha; the test-queue worker's deploy phase refuses or installs a FRESH staged copy with the game down. Compare binaries by sha256 or the embedded source hash.
- **A read-only tool whose name lacks a `list_`/`get_` prefix must be added to `READ_ONLY_TOOLS`** in `src/RimMandrake/Utils/rimbridge_client.py`, or the client refuses it as "not read-only" (exit 3) and every caller reads UNMEASURED instead of FAIL (`jawa/running_mods` was refused this way). A probe of the real call, not a fake, is the only check that sees it.
- **Unity's Mono cannot walk another thread's managed stack.** `System.Diagnostics.StackTrace(Thread, bool)` throws `NotImplementedException` for any thread but the caller, so a stall diagnostic must use breadcrumbs (`JawaBenchTpsWatchdog` phase stack, `JawaBenchStallProbe` tick bucket) and native thread CPU, not a stack dump; `JawaBenchLoadStallProbe`'s eventThread `stackTrace` hits the same wall.

## 5. Prove it, or it is not done
- **Adding a parameter to `jawa/set_terrain_batch` or `jawa/build_batch` in the companion C# must also update the `known` calibration set in `src/RimMandrake/Utils/rimplace/contract.py`,** or `tool_parameters()` returns None and the rimplace selftest goes red.

## Building and exporting the companion
- **`bridgetools/build.py` needs the user site-packages** (`closure_scan` imports `dnfile`): run it without `python -I`, or it fails 'No module named dnfile' after a good dotnet build. A `git archive` export of the companion needs `src/Directory.Build.props/.targets`, `Utils` and `contracts` beside `bridgetools`.
