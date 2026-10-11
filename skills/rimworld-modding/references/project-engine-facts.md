# Engine facts measured in this project (ticking, MayRequire, csproj, patches)

Moved from the project `CLAUDE.md` on 2026-10-11 (weekly cleaning), text unchanged except heading levels. CLAUDE.md keeps a one-line rule and points here. Entries state what IS: delete a line the moment it turns false, never annotate it.

- 🔴 **`Plant` never overrides `Tick()` — only `TickLong()`.** A `ThingComp` attached to a
  `PlantBase`-derived def (via `<comps>`) must override `CompTickLong()`, never `CompTick()`,
  or it will likely never fire at all: `ThingWithComps.TickLong()` is what loops
  `comps[i].CompTickLong()`, and nothing schedules the Normal ticker for a plant. This also
  means the engine's own Long-ticker cadence already throttles the comp — do not add a manual
  `IsHashIntervalTick` gate on top of it (RimSage-confirmed against decompiled 1.6 source,
  2026-09-27, building `RM_CompPlantPredator`/`MIASMA_SCUTTLER_PREDATION_1`).

## Patch and def behaviour

- **A patch that matches nothing logs nothing.** `PatchOperationConditional` and
  `PatchOperationFindMod` both return true on no match.
- 🔴 **`MayRequire` on a top-level `<Operation>` node is IGNORED by the decompiled
  1.6 engine — it does nothing.** Two patches (`RUT_Bitumen_KorvethSource.xml`,
  `RUT_ThrummelSeepwax_RosterSource.xml`, added `6714ad67c`) each carried
  `<Operation MayRequire="mandrake.rm.thesump">` to guard a recipe that pays with a
  TheSump-only item — TheSump is not in the canonical mod list, so the intent
  was "skip this patch when TheSump is absent." The guard is silently inert: both
  applied anyway, the ingredient resolved null, and `RecipeDefGenerator.SetIngredients`
  NREd → RimWorld's own corrupted-mods recovery **reset `ModsConfig.xml` to
  Core-only**, live-hit twice in one night (2026-09-27) before this was found. Same
  failure shape as `MODCHECK_DONOR_ENVIRONMENTS_1`'s Armoury/ModularWeapons2 case.
  ⇒ **`MayRequire` only works on the elements it's documented for** (a `<li>` inside
  a list, a `ModExtension`, a `ThingDef`'s own attribute) — never assume it gates a
  whole `<Operation>` block; guard with `PatchOperationFindMod`/`Conditional` instead,
  or (the fix actually applied) test that the referenced def actually exists before
  applying. MEASURED 2026-10-09: **0** live top-level `<Operation MayRequire>` remain in
  `src/` and all 14 `<li>`-level attributes resolve (`Transient/belt_mayrequire_census_20261009.md`).
  ⚠️ A composed member (e.g. `mandrake.rm.longshade`) has a standalone About.xml in `src/` but
  **no packageId at runtime** — its id is folded into `mandrake.rm.biomes`, so a `MayRequire`
  naming a member id silently never loads (sitting 2 found 26 such sites).

- ⚠️ **`RM_CreatureBehaviors.csproj` sets `EnableDefaultCompileItems false` and lists every file.** A new
  `.cs` in `Source/` without a `<Compile Include>` line **compiles into nothing, with no error**. Adding a
  file to that assembly is always a two-file change.
