# PACK_ANIMALS_RESTORE_EMPTY_SADDLES — offline verification (FOUNDRY, 2026-10-11)

Item prose (claim, evidence, fix, per-biome table): `infrastructure/state/items/PACK_ANIMALS_RESTORE_EMPTY_SADDLES.md`.

- Engine rule read via RimSage: `PawnGroupKindWorker_Trader.CanGenerateFrom` / `GenerateCarriers`, `BiomeDef.IsPackAnimalAllowed`.
- Dump (2026-10-04T17:39:06Z): 62 of our BiomeDefs, 56 empty `allowedPackAnimals`; 302 packAnimal races (sanity: Muffalo, RSW_Bantha present).
- Mod DLL literal scan (5,538 DLLs, both roots; 8 relevant 1.6 assemblies): Biomes! Framework extraCarriers (unused by us),
  BCP representatives (none configured for ours). Neither opens our biomes.
- Fix: 4 biomes via `PackAnimals_RestoreSaddles.xml`, RM_WeepingStones inline, 6 carriers added, droid enclave carriers node.
- Simulator extended (`--simulate` repeatable; allowedPackAnimals add-if-missing conditional modelled); 73 pairs opened, 0 lost.
- Judgement calls left: 42 biome rows marked "sitting" in the item table; 11 N/A (no home map).
