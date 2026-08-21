## spec
Create `src/Jawa/Inhabited/`, mirroring `src/Jawa/JawaPlantGrowth/` exactly —
that mod is the working reference for this toolchain and its csproj comments
carry the build line.
  `src/Jawa/Inhabited/About/About.xml`
     `<packageId>mandrake.inhabited</packageId>`, `<name>Inhabited (local)</name>`,
     `<author>mandrake</author>`, `<supportedVersions><li>1.6</li>`.
     `<modDependencies>`: `Ludeon.RimWorld`, `brrainz.harmony`.
     `<loadAfter>`: `brrainz.harmony`, `Ludeon.RimWorld`.
  `src/Jawa/Inhabited/Source/Inhabited.csproj`
     `<TargetFramework>net472</TargetFramework>`, `AssemblyName`/`RootNamespace`
     `Inhabited`, `<OutputPath>..\Assemblies\</OutputPath>`,
     `<AppendTargetFrameworkToOutputPath>false`,
     🔴 `<CopyLocalLockFileAssemblies>false</CopyLocalLockFileAssemblies>` —
     three mods in this load set shipped the base game's assemblies into their
     own folder and caused silent chaos. Harmony must come from
     `brrainz.harmony` at runtime, never from us.
  `src/Jawa/Inhabited/Defs/` — empty for now, created so deploy sees it.
Build with the WINDOWS-NATIVE dotnet; it cannot take a `/mnt/d` path:
  `"%USERPROFILE%\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\Jawa\Inhabited\Source\Inhabited.csproj -c Release`
⛔ Do NOT deploy while the game is running — the OS locks assemblies. Everything
else in this mod (Defs, About) deploys game-up.

## verify
the build produces `src/Jawa/Inhabited/Assemblies/Inhabited.dll` and
`python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Inhabited` plans a
copy with no `-` lines. ⚠️ A mod with no About.xml or packageId is not
deployable and deploy will say so rather than failing loudly.

## criteria
the mod appears in RimSort / the in-game mod list under `mandrake.inhabited`.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

done 2026-08-20, `f0a9f6c`. Built at `src/Jawa/Inhabited/`, deployed, in sync.
⚠️ **Two deviations from the spec text, both deliberate and both mine to make:**
(a) `<name>Inhabited (local)</name>` as specified, but the mod carries a real
`Defs/` tree already rather than an empty one — the core landed in the same pass.
(b) `EnableDefaultCompileItems` is left ON rather than listing every `.cs`
explicitly as `JawaPlantGrowth` does; this project grows files weekly and an
explicit list is a silent-omission machine. `CopyLocalLockFileAssemblies` is
`false` as required and `Assemblies/` holds **only** `Inhabited.dll`.
verify output:
  `Inhabited -> ...\Assemblies\Inhabited.dll   Build succeeded. 0 Warning(s) 0 Error(s)`
  `deploy_custom_mods.py --mod Inhabited` -> 6 `+` lines, **no `-` lines**,
  then `--apply` -> `-> VERIFIED in sync`
⚠️ It is **not in ModsConfig.xml**, so the game will not load it until it is
enabled. That is a start-prep step, not a deploy step.
