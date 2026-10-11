# PACK_ANIMALS_RESTORE_EMPTY_SADDLES — empty allowedPackAnimals block land trade caravans

Filed 2026-10-11 by the VANILLA_BEAST_EXCISION_1 wave-3 slice (`a64d41ac1`); verified and partly fixed
offline the same day (FOUNDRY). Working notes: `Transient/pack_animals_20261011.md`.

## Claim — VERIFIED offline

1. **Engine rule** (RimSage, decompiled 1.6): `PawnGroupKindWorker_Trader.CanGenerateFrom` on a valid tile returns
   `groupMaker.carriers.Any(x => PrimaryBiome.IsPackAnimalAllowed(x.kind.race))`, and `BiomeDef.IsPackAnimalAllowed`
   is `allowedPackAnimals.Contains(race)`. `GenerateCarriers` draws from the same intersection. So an empty
   `allowedPackAnimals`, or a trader group with no carriers, means **no land trade caravan** on that home map.
2. **56 of our 62 BiomeDefs have an empty list** — measured from the full-list def dump (captured
   2026-10-04T17:39:06Z, post-patch), parsed as elements; current src agrees (the only `allowedPackAnimals` in src
   are the six non-empty lists plus deliberate `<allowedPackAnimals />` empties in the nightside/blue-desert defs).
3. **`RUT_Jawa_FreeDroidEnclaves`' Trader group had no `<carriers>`** — confirmed in
   `src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaFreeDroidEnclaves.xml`; it never generated.
4. **No mod routes around it on the active list.** Literal scan of every 1.6 mod DLL on both roots for
   `IsPackAnimalAllowed` / `PawnGroupKindWorker_Trader` / `allowedPackAnimals` found 8 assemblies; the active ones:
   - *Biomes! Framework* (`BiomesTeam.CoreFramework`): postfix on `CanGenerateFrom` + transpiler on `GenerateCarriers`
     (source `ExtendCaravanCarriers.cs`) — only for biomes carrying its `BiomesMap.extraCarriers` extension; none
     of ours do, and `GenerateCarriers` still filters by `IsPackAnimalAllowed`.
   - *Biome Compatibility Project* (`Kopp.BiomeCompatibilityProject`): adds mod-added pack animals to a mod biome's
     list only from its configured "representative" vanilla biomes; ours are not in its defaults and no BCP
     settings file exists, so it adds nothing (the post-startup dump agrees).
   - RimQuest names the type only; VTE and VFE Medieval 2 are inactive.

## Fixed (unambiguous cases only)

Rule applied: a biome gets only OWNED beasts that **already live in its own roster** and whose description calls
them pack animals / beasts of burden. No roster edited, no beast moved.

- `RM_WeepingStones` — inline `RM_Tirbak`, `RM_Vellak` (its own natives) in `RM_WeepingStones_Biome.xml`.
- `src/RimUtinni/UtinniPatches/Patches/PackAnimals_RestoreSaddles.xml` (add-if-missing conditionals):
  `RM_LeaningScrub` +RSW_Bantha/Ronto/Eopie/Kybuck/Skalder; `RM_WeepingStones` +RSW_Dewback/Bantha/Eopie/Jamel;
  `RM_FeverWood` +RSW_Fambaa; `RM_Cauldron` +RSW_Skalder.
- Faction carriers (Utinni): RSW_Kybuck, RSW_Skalder, RSW_Dewback, RSW_Fambaa added to
  `VanillaBeastExcision_Carriers.xml`; the literal lists in `DeepDesertTribes.xml` / `HomesteadDefenseLeague.xml` and
  `RUT_Jawa_FreeDroidEnclaves`' `<carriers>` node carry the 12 owned carriers.
- **Free tier (decision taken by question card 2026-10-11: "Yes, add them to vanilla factions").** The owned RM_
  carriers RM_Tirbak, RM_Vellak (`src/RimMandrake/WeepingStones/Patches/RM_TraderCarriers_WeepingStones.xml`) and
  RM_Vaalok (`src/RimMandrake/Stillsand/Patches/RM_TraderCarriers_Stillsand.xml`) are added to every faction trader
  group, vanilla factions included, by the Baroque Biomes mod itself; they left the Utinni carriers list. Guarded by the
  Mod Settings toggle "Traders bring our pack animals" (`RM_PatchOperationBiomesSettingGate`, setting
  `ownedCaravanCarriers`, default on, next game start; BiomesShell DLL) and a `PatchOperationConditional`; idempotent
  by `[not(<first kind>)]`.
- **Correction found on the way:** RM_BovineBeetle and RM_ShatterjawBeetle were cut from the Lantern Deeps on
  2026-10-05 (`66a0d9db1`), but the carriers lists still named them (the 10-04 dump predates the cut, so the simulation
  saw them) and the Utinni patch removed Muffalo and Alpaca from RM_LanternDeeps "because its beetles carry", which
  left the Deeps with no pack animal at all under Utinni. The dead beetle lines and the two removals are gone; the
  simulator now refuses a carrier kind that is not a PawnKindDef in src.
- Proof: `vanilla_beast_carriers.py` with all four files simulated → 72 (faction, biome) pairs opened, 0 lost; with
  `--free-tier` (official factions, src RM_ lists) RM_WeepingStones and RM_Stillsand go from 0 to 11 of 11 vanilla
  traders; selftest 33 checks pass; `validate_patch.py --live` 0 errors.

## Residuals

- **Live verify (game-up)**: a trader caravan reaches a home map in each fixed biome, and the droid enclave sends one;
  on a free-tier list a vanilla caravan reaches the Weeping Stones and the Stillsand.
- Re-run `vanilla_beast_carriers.py` on the next full-list dump.

## Per-biome table (the rest is per-biome sitting work — do NOT sweep)

| BiomeDef | home map? | allowedPackAnimals (dump 10-04) | packAnimal species in its wildAnimals | verdict |
|---|---|---|---|---|
| RM_Abyss | yes | - | AA_NightMule, AA_CrepuscularBeetle, AA_NightAve | sitting: only DONOR pack beasts (AA_NightMule, AA_CrepuscularBeetle, AA_NightAve) - needs an owned port or a new creature |
| RM_BlueDesert | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RM_Cauldron | yes | - | RSW_Skalder | **FIXED** -> RSW_Skalder (Utinni) |
| RM_ChillCrater | no (impassable/no base) | - | - | N/A - no home map, no land caravan |
| RM_Contagion | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RM_FeverWood | yes | - | RSW_Gelagrub, RSW_Fambaa | **FIXED** -> RSW_Fambaa (Utinni) |
| RM_FloodedCanyon | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RM_GelatinousSlime | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RM_Greentide | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RM_GreySea | no (impassable/no base) | - | - | N/A - no home map, no land caravan |
| RM_LanternDeeps | yes | Muffalo, Alpaca (src; the dump's beetles were cut 2026-10-05) | - | sitting: vanilla pack animals only - needs an owned pack beast |
| RM_LeaningScrub | yes | - | RSW_Eopie, RSW_Mudhorn, RSW_Ronto, RSW_Kybuck, RSW_Bantha, RSW_Skalder | **FIXED** -> RSW_Bantha, RSW_Ronto, RSW_Eopie, RSW_Kybuck, RSW_Skalder (Utinni) |
| RM_LongShade | yes | RSW_Bantha, RSW_Ronto, RSW_Eopie, RSW_Jamel, RSW_Falumpaset | RM_Ossik, RM_Thurra, RM_Sollak, RM_Gennok, RSW_Bantha, RSW_Jamel, RSW_Ronto, RSW_Eopie, RSW_Skalder, RSW_Uvak, RSW_Varactyl, RSW_Falumpaset, RSW_Nerf, RSW_Shaak, RSW_TeeMuss, RSW_Bolotaur, RSW_Runyip, RSW_Dewback | has list (owned); opened by VanillaBeastExcision_Carriers.xml |
| RM_Miasma | yes | - | RSW_Runyip | sitting: owned packAnimal RSW_Runyip not described as a beast of burden |
| RM_NightsideIce | yes | - | Tauntaun | sitting: only DONOR pack beasts (Tauntaun) - needs an owned port or a new creature |
| RM_Pyrelands | yes | Muffalo, Dromedary, Elephant | RSW_Orray, RSW_Dalgo | has list but vanilla only (Muffalo/Dromedary/Elephant); owned RSW_Orray/RSW_Dalgo in roster - swap at its sitting |
| RM_RustCathedral | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RM_SeabedFloor | seabed layer | - | - | sitting: ship-only layer; does a land trade caravan belong at all? |
| RM_SeabedFloor_GreySea | seabed layer | - | - | sitting: ship-only layer; does a land trade caravan belong at all? |
| RM_SeabedFloor_TheChill | seabed layer | - | - | sitting: ship-only layer; does a land trade caravan belong at all? |
| RM_SeabedFloor_TheScald | seabed layer | - | - | sitting: ship-only layer; does a land trade caravan belong at all? |
| RM_SeabedFloor_TwilightSea | seabed layer | - | - | sitting: ship-only layer; does a land trade caravan belong at all? |
| RM_SeabedUnavailable | no (impassable/no base) | - | - | N/A - no home map, no land caravan |
| RM_Stillsand | yes | RM_Vaalok, RSW_Bantha, RSW_Ronto, RSW_Eopie, RSW_Jamel, RSW_Falumpaset | RM_Aurrok | has list (owned); RM_Vaalok carried by RM_TraderCarriers_Stillsand.xml (free tier), the RSW_ beasts by VanillaBeastExcision_Carriers.xml |
| RM_TheChill | no (impassable/no base) | - | - | N/A - no home map, no land caravan |
| RM_TheForge | yes | - | RSW_LavaFlea | sitting: owned packAnimal RSW_LavaFlea not described as a beast of burden |
| RM_TheRot | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RM_TheScald | no (impassable/no base) | - | - | N/A - no home map, no land caravan |
| RM_TheSump | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RM_TwilightSea | no (impassable/no base) | - | - | N/A - no home map, no land caravan |
| RM_Warscar | yes | - | AA_SpinedGow, RSW_FoundryBeetle | sitting: owned packAnimal RSW_FoundryBeetle not described as a beast of burden; donor AA_SpinedGow |
| RM_Wasteland | yes | - | VAEWaste_Megatardi, RSW_Sacapillar | sitting: owned packAnimal RSW_Sacapillar not described as a beast of burden; donor VAEWaste_Megatardi |
| RM_Webwork | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RM_WeepingStones | yes | - | RM_Tirbak, RM_Vellak, RSW_Dewback, RSW_Dactillion, RSW_Bantha, RSW_Eopie, RSW_Jamel | **FIXED** -> RM_Tirbak, RM_Vellak (inline RM_, carried by RM_TraderCarriers_WeepingStones.xml, free tier) + RSW_Dewback, RSW_Bantha, RSW_Eopie, RSW_Jamel (Utinni) |
| RUT_Abyss | yes | - | AA_NightMule, AA_CrepuscularBeetle, AA_NightAve | sitting: only DONOR pack beasts (AA_NightMule, AA_CrepuscularBeetle, AA_NightAve) - needs an owned port or a new creature |
| RUT_AridShrubland | yes | - | Eopie, Mudhorn, Ronto, Kybuck, Bantha, Skalder | sitting: only DONOR pack beasts (Eopie, Mudhorn, Ronto, Kybuck, Bantha, Skalder) - needs an owned port or a new creature |
| RUT_BlueDesert | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RUT_Cauldron | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RUT_Contagion | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RUT_CrackedLands | yes | - | Eopie | sitting: only DONOR pack beasts (Eopie) - needs an owned port or a new creature |
| RUT_Desert | yes | RSW_Bantha, RSW_Ronto, RSW_Eopie, RSW_Jamel, RSW_Falumpaset | RSW_Bantha, RSW_Jamel, RSW_Ronto, RSW_Ossik, RSW_Eopie, RSW_Skalder, RSW_Uvak, RSW_Varactyl, RSW_Falumpaset, RSW_Nerf, RSW_Shaak, RSW_TeeMuss, RSW_Bolotaur, RSW_Runyip, RSW_Thurra | has list (owned); opened by VanillaBeastExcision_Carriers.xml |
| RUT_ExtremeDesert | yes | RSW_Bantha, RSW_Ronto, RSW_Eopie, RSW_Jamel, RSW_Falumpaset | - | has list (owned); opened by VanillaBeastExcision_Carriers.xml |
| RUT_FeverWood | yes | - | Gelagrub, Fambaa | sitting: only DONOR pack beasts (Gelagrub, Fambaa) - needs an owned port or a new creature |
| RUT_FuelSnows | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RUT_Greentide | yes | - | Falumpaset, Gelagrub, Fambaa, Dalgo | sitting: only DONOR pack beasts (Falumpaset, Gelagrub, Fambaa, Dalgo) - needs an owned port or a new creature |
| RUT_GreySea | no (impassable/no base) | - | - | N/A - no home map, no land caravan |
| RUT_Jawa_BackgroundWater | no (impassable/no base) | - | - | N/A - no home map, no land caravan |
| RUT_Miasma | yes | - | Runyip | sitting: only DONOR pack beasts (Runyip) - needs an owned port or a new creature |
| RUT_NightsideIce | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RUT_PropaneLake | no (impassable/no base) | - | - | N/A - no home map, no land caravan |
| RUT_RustCathedral | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RUT_Scarlands | yes | - | RSW_FoundryBeetle, AA_SpinedGow | sitting: owned packAnimal RSW_FoundryBeetle not described as a beast of burden; donor AA_SpinedGow |
| RUT_Slime | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RUT_Sump | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RUT_TheForge | yes | - | LavaFlea | sitting: only DONOR pack beasts (LavaFlea) - needs an owned port or a new creature |
| RUT_TheRot | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RUT_TheScald | no (impassable/no base) | - | - | N/A - no home map, no land caravan |
| RUT_TwilightSea | no (impassable/no base) | - | - | N/A - no home map, no land caravan |
| RUT_Umbra | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RUT_Wasteland | yes | - | RSW_Sacapillar, VAEWaste_Megatardi | sitting: owned packAnimal RSW_Sacapillar not described as a beast of burden; donor VAEWaste_Megatardi |
| RUT_Webwork | yes | - | - | sitting: no pack beast at all - a NEW creature |
| RUT_WeepingStones | yes | - | Dewback, Dactillion, Bantha, Eopie, Jamel | sitting: only DONOR pack beasts (Dewback, Dactillion, Bantha, Eopie, Jamel) - needs an owned port or a new creature |
