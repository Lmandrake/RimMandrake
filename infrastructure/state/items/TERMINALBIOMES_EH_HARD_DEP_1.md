# TERMINALBIOMES_EH_HARD_DEP_1 — TerminalBiomes' hard assembly dep on EnvironmentalHazards is declared only as loadAfter

## the defect, MEASURED 2026-09-26 (Scald load round)

`TerminalBiomes/Source/RM_TerminalBiomesMod.cs` line 2 is
`using RimMandrake.EnvironmentalHazards;`, and the `.csproj` carries

```
<Reference Include="RimMandrake.EnvironmentalHazards">
  <HintPath>..\..\EnvironmentalHazards\Assemblies\RimMandrake.EnvironmentalHazards.dll</HintPath>
```

16 of TerminalBiomes' defs also carry `MayRequire="mandrake.rm.environmentalhazards"`.
But `About.xml` lists EnvironmentalHazards only in `<loadAfter>`, never in
`<modDependencies>`.

`modset_builder.close_over()` walks `modDependencies` only, so
`--tier proof_terminalbiomes` produces a **10-mod list with EnvironmentalHazards
absent**. That is the exact shape of the `TypeLoadException` ->
`Recovered from incompatible or corrupted mods` failure in `rimworld-load-round` §10.

⚠️ The tier has apparently never been run, so this has not yet cost a load. The Scald
round added EH by hand and the load was clean (`jawa/startup_types`: 1 live type for
Terminal Biomes, 10 for Environmental Hazards).

## spec
1. Move `mandrake.rm.environmentalhazards` into TerminalBiomes' `<modDependencies>`.
2. Sweep the other `BIOME_PROOF_MODS` tiers the same way: per biome mod, compare its
   `.csproj` `<Reference Include="RimMandrake.*">` lines against its `About.xml`
   `<modDependencies>`. Any reference not declared there is the same latent bug.

## criteria
- [ ] `modset_builder --tier proof_terminalbiomes` lists EnvironmentalHazards with no hand-editing.
- [ ] No biome mod has a `RimMandrake.*` assembly reference missing from its `modDependencies`.
