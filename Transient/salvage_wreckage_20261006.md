# SALVAGE_WRECKAGE_EVERYWHERE_1 — FOUNDRY slice 2026-10-06

## State found
- The three landed commits are DESIGN only (d1ac95b46, bf8dfed16, 9d8d78f86). No wreck engine had been built.
- Build plan: design/RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md §7. The scavenge system
  (design/RimMandrake/jawa_scavenge_system_design_2026-10-03.md §9) is gated on that design's family defs, and
  its §7 makes this loot comp the fallback path when "wreck pieces" is off.
- FASCINATING_WORLD_JUNK_1 owns the roster and the vanilla-junk reskin (Phase 3/4). Not touched here.

## Slice chosen: design step 1, the loot half (§3c + §6 loot rows), with the Scald wired as the first consumer
- New engine `src/RimMandrake/Wreckage/` (mandrake.rm.wreckage), composed into mandrake.rm.biomes as an engine entry.
- RM_CompSalvageLoot: rolls only on DestroyMode.Deconstruct, on top of vanilla's costList. Smashing leaves slag only.
- The rare roll scales with the salvager's Construction skill: 0.25x at 0, 2x at 20 (PROVISIONAL, until RM_Salvaging exists).
  The pawn comes from a Harmony prefix/finalizer on JobDriver_Deconstruct.FinishedRemoving.
- 9 ThingSetMakerDefs: RM_SalvageLoot_{Scrap,Hull,Tank,Carapace,Sealed} and _Rare for all but Scrap. All numbers
  are PROVISIONAL. The rare rows are vanilla stand-ins (ComponentSpacer, or components for Tank); Star Wars parts
  are for the RUT_/RSW_ patch layer.
- Settings: salvageLoot, lootGenerosity (0.25-3x), skillScalesRare. The two bools are registered as RM_MechanicGates
  `Wreckage.loot` / `Wreckage.skillScalesRare`.
- Scald: Hull→Hull tier, Tank→Tank tier, Frame→Scrap tier (rareChance 0). The file header's "no loot comp, deferred"
  paragraph is corrected.

## Files
- src/RimMandrake/Wreckage/About/About.xml
- src/RimMandrake/Wreckage/Source/{RM_Wreckage.csproj, RM_WreckageMod.cs, RM_CompSalvageLoot.cs, RM_Patch_DeconstructSalvager.cs}
- src/RimMandrake/Wreckage/Assemblies/RimMandrake.Wreckage.dll (+ .srchash)
- src/RimMandrake/Wreckage/Defs/ThingSetMakerDefs/RM_SalvageLoot.xml
- src/RimMandrake/Wreckage/Languages/English/Keyed/RM_Wreckage.xml
- src/RimMandrake/Wreckage/validation.py (first script)
- design/validation_walks/RimMandrake/Wreckage.md (walk)
- src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RUT_ScaldWrecks.xml (comps + header fix)
- src/RimMandrake/Biomes.compose.json (Wreckage engine entry, wave 2)

## Validation (offline)
- winbuild.py Wreckage: Build succeeded, 0 warnings, 0 errors.
- validate_patch.py --defs on both XML files: 0 errors, 0 warnings. An info line says the comp class is not seen in
  the load set; that is expected, because the class is our own public type.
- validation.py static_checks: PASS (0 findings). A sanity probe with two injected faults returned 2 findings.
- deploy_custom_mods.py --compose biomes (plan only, NOT applied): Wreckage composes 4 files into Biomes/_Kits/Wreckage.
  biomes_compose_sweeps: no finding names Wreckage. The 5 sweeps with findings are pre-existing.
- No art needed for this slice. Nothing deployed, nothing live.

## What is left (design §7)
- No item filed yet: a bridge verb that deconstructs with a pawn. Every drop, smash and toggle line in the walk waits on it.
- Steps 1b-2: family parents, RM_WreckWeatheringDef, RM_GenStep_WreckField, the Scald migration from RUT_ to RM_.
- Steps 3-9: per-biome lists (Riddled/High first), wreck falls, art waves, the RSW/RUT layers. Then the scavenge-system build.
- New files are DIRTY under code review until a full review marks them clean.
- The item cannot close. This is slice 1 of about 10.
