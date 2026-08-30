# DROIDWORKS_DLL_COMPILE_1 — compile the Droidworks phase-0 DLL

Filed by BENCH 2026-08-30, caused by `DROID_SYSTEM_BUILD_1`. Full spec is in the
ledger's `file` event (`rimflow show` prints it) — summary: build the 5 hand-written
C# sources at `src/Jawa/Droidworks/Source/Droidworks/*.cs` into `Droidworks.dll`,
copying `JawaIonWeapons.csproj`'s known-good net472 pattern verbatim, fixing ONLY
signature-level compile drift (no design changes).

## Done

`src/Jawa/Droidworks/Source/Droidworks/Droidworks.csproj` — verbatim copy of
`JawaIonWeapons.csproj`'s structure (net472, `Microsoft.NETFramework.ReferenceAssemblies`,
`RimWorldManaged` hint paths, `OutputPath ..\..\Assemblies\` — one level deeper than
JawaIonWeapons's own `..\Assemblies\` since these sources sit in `Source/Droidworks/`
not bare `Source/`), all 6 `.cs` files listed explicitly (`CompDroidDetonation`,
`DroidworksDefOf`, `DroidworksModExtension`, `HediffComp_PoweredDown`, `Need_Power`,
`Recipe_RebootDroid` — spec said "5 files" but the source folder holds 6; all 6
compile as one unit, `CompDroidDetonation`/`DroidworksModExtension` are two classes
BENCH's own note bundled under one filename count).

`dotnet build -c Release`: **0 warnings, 0 errors, first try** — no signature drift
to fix, BENCH's C# already matched the live API. `Droidworks.dll` (9,216 bytes)
present at `src/Jawa/Droidworks/Assemblies/Droidworks.dll`, fresh (built
2026-08-30, this pass).

**Not deployed, on purpose** — game is UP; deploy rides the next game-down window
per the item's own instruction.

## criteria

- [x] Build exit 0.
- [x] Fresh `Droidworks.dll` exists in `Assemblies/`.
- [x] No design changes made (none were needed).
- [x] Not deployed (game up).

--- history ---
