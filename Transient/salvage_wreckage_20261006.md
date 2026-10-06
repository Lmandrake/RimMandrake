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

## Slice 2 (2026-10-06): family parents + the Scald's weathering as the template
- Family parents (abstract, design §3a): RM_WreckFamilyBase (on ShipChunkBase; Walkable; fraction 1.0) and
  RM_WreckFamily_{Hull,Tank,Frame,Speeder,Carapace,Tread}, each with Inherit="False" costList/killedLeavings and the
  RM_CompSalvageLoot tier. Hull/Tank/Frame numbers are the Scald's shipped ones; Speeder/Carapace/Tread are INVENTED
  (no child, no art, guessed footprints 2x2/1x1/3x3). Speeder and Tread roll the Hull table. All PROVISIONAL.
- RM_WreckWeatheringDef (yieldFactor, lootTierShift, labelPrefix, extraLeavings) + RM_WreckWeathering extension.
  The fold-in runs in DefModExtension.ResolveReferences(parentDef): yieldFactor -> resourcesFractionWhenDeconstructed
  (not costList: 1-count components would truncate), label fallback, extraLeavings -> killedLeavings, tier shift on the
  ladder Scrap < Hull/Tank/Carapace < Sealed (landing on Scrap zeroes rareChance).
- One weathering row: RM_WreckWeathering_Cooked (0.75, shift 0, "scalded", no extraLeavings: the slag is the family's).
- Scald reparented (defNames kept RUT_, no rename): the three defs now carry only label/description/texPath/shadow +
  the Cooked extension. Same yields, tiers and art; validation.py proves the cost x fraction equals the 96f8113e9 values.
- Files: src/RimMandrake/Wreckage/Source/RM_WreckWeathering.cs (+ csproj Compile line), .../Defs/ThingDefs_Buildings/
  RM_WreckFamilies.xml, .../Defs/RM_WreckWeatheringDefs/RM_WreckWeatherings.xml, DLL+.srchash rebuilt,
  .../validation.py, design/validation_walks/RimMandrake/Wreckage.md, TerminalBiomes/.../RUT_ScaldWrecks.xml (header
  "no new abstract needed" paragraph replaced: it was false after this slice).
- Checks: winbuild Wreckage 0 warn/0 err (new types confirmed in the DLL); validate_patch --defs (Data+workshop+Mods)
  4 files 0 err 0 warn (info lines only: our own classes); Wreckage validation.py static PASS, sanity probes (bad
  weathering name, changed family cost, Frame reparented to Hull) each caught; TerminalBiomes validation.py static PASS;
  compose plan (not applied) puts Wreckage 6 files in Biomes/_Kits/Wreckage beside Biomes/TerminalBiomes.
- Art: none owed this slice (Scald texPaths unchanged; artpipe find scald2_wreck = 56 hits, done). Owed when a biome
  first casts Speeder/Carapace/Tread: ~2 variants per biome x family; search first (landspeeder/junk renders exist).
- Left: RM_GenStep_WreckField (custom element-name loader) + the 3->1 Scald GenStep collapse and S6 alias; the RUT_->RM_
  rename; RM_WreckDensityClassDef; the other ~7 weathering rows with their biomes (Riddled/High first); RM_WreckSurface
  category; wreck-fall incident; the deconstruct bridge verb; a live load proving the fraction lands at 0.75.

## Slice 3 (2026-10-06): the wreck-field placement step, the Scald merged 3 -> 1, Riddled/High weathering rows
- RM_GenStep_WreckField (new file Source/RM_GenStep_WreckField.cs + csproj Compile line; RM_WreckWeathering.cs untouched):
  on GenStep_Scatterer (ScatterThings' tag lists are private and its rotation check is per its single thingDef).
  Weighted <wrecks> in element-name form (RM_WreckFieldEntry.LoadDataFromXmlCustom, the BiomeAnimalRecord pattern),
  densityClass, own countPer10kCellsRange override, cluster chance/size (class default), tag-based terrain validation
  over terrainValidationRadius, placement via GenSpawn.CanSpawnAt (affordance) + never wiping a non-plant/filth thing.
  Clusters ignore minSpacing (spacing separates fields, not a field's pieces). warnOnFail off by default.
- RM_WreckDensityClassDef + Defs/RM_WreckDensityClassDefs/RM_WreckDensityClasses.xml: Riddled 6~10/0.5, High 4~6/0.3,
  Moderate 1.5~3/0.2, Low 0.3~0.8/0, Eroded 1~2/0 (design §3d-i; Moderate cluster and all sizes INVENTED). No Cleaned or
  Fresh row by design. The law's "+1 tier" rides the weathering rows (a tier is per-def), not the class.
- Settings (RM_WreckageMod.cs): wreckFields, wreckDensity (0-3), disabledFields (comma string, so the bridge's settings
  tool can flip one field). FieldActive(key) = master && key not disabled && RM_MechanicGates.Enabled(key).
  Gates: Wreckage.fields (ctor); Wreckage.field.<key> + each gateAliases entry, registered by RM_WreckFieldStartup
  ([StaticConstructorOnStartup], after def load and after every Mod ctor).
- Scald: RUT_ScaldWreckScatter.xml now holds ONE RM_WreckField_Scald (order 965, key Scald, alias Scald.S6, Moderate,
  ceiling 1.2~1.8 = the old 3 x 0.4~0.6, same tag/radius/minSpacing/allowInWaterBiome); register patch adds it to
  RM_TheScald/RUT_TheScald. The new GenStepDef is RM_-named (new def, not a rename); the wreck defs stay RUT_.
  Behaviour change, flagged: minSpacing 6 now spaces any wreck kind, and 2-3 can cluster.
- S6 fold (TerminalBiomes): scaldS6WreckSalvageEnabled, its Scribe line, checkbox and Scald.S6 registration removed;
  RM_GenStep_ScaldWreckScatter deleted; ScaldActive made public and registered as the bare gate "Scald", which the field
  reads so the Scald's biome switch still stops its wrecks. A saved S6=false is lost (defaults on). TerminalBiomes
  validation.py's S6 UNMEASURED chain and its walk line moved to Wreckage.
- Weathering rows: Frozen (1.0, +1; Nightside Ice/Lantern Deeps), Picked (0.2, -2; Twilight Deep), CrystalJacketed
  (1.0, +1, INVENTED from the High default; Grey Deep). No child def names them yet. Known gaps: Picked still gets a
  Scrap roll (no noLoot field: that needs RM_WreckWeathering.cs); the crystal jacket and shard table are not expressible.
- Checks: winbuild Wreckage 0/0 and TerminalBiomes 0/0; validate_patch --defs (Data+workshop+Mods) 4 files 0 errors,
  4 advisory warnings on the register patch's unchanged nomatch shape; Wreckage validation.py static PASS (new
  _field_checks: field XML elements vs C#+base fields, li-form, class/tag/def refs, density law order, pinned weathering
  numbers, both register arms, stale refs to the 3 old steps/S6 bool across src/, TB gate registrations), 9 injected
  faults each caught; TerminalBiomes validation.py static PASS; compose plan (not applied) puts 7 Wreckage files in.
- Art: none owed this slice (no new child def). Search: scald2_wreck 56 hits (probe), landspeeder 36, PickedWreck 0,
  wreck_frozen 0, expedition 0. Owed when step 3's biome children exist: Riddled expedition rig/hull/tank (Nightside Ice,
  Lantern Deeps), Twilight picked hull-rib, Grey crystal-jacketed hull, ~2 variants each.
- Left: biome children + fields for Riddled/High (Nightside Ice, Lantern Deeps, Cauldron edge; sea floors in their floor
  map generators, not extraGenSteps); the repairable-few entry; Picked noLoot + an extraTable field (after the review of
  RM_WreckWeathering.cs); RUT_->RM_ wreck rename; RM_WreckSurface; wreck falls; the deconstruct bridge verb; a live
  fresh-Scald-map pass for the three mapgen components.
