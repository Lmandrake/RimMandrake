# belt_merges_20261009m — Silooth override fold + MATERIAL_MERGES_CLEANUP_1

FOUNDRY offline builder, 2026-10-09. No bridge, no deploy.

## Task 1 — Silooth art override fold
- Silooth home = SWBestiary (Patches/Silooth/Silooth_Warbeast.xml). Art moved to SWBestiary/Textures/RimStarWars/SWBestiary/Silooth/;
  patch now redirects li[2]+li[3] bodyGraphicData texPath (the two stages the same-path override reached).
- src/RimStarWars/SiloothArtOverride deleted. No modlist/compose/loadAfter referenced it (git grep: only ledgers, art ledger, Transient).
- Item SILOOTH_ART_FOLD_1 filed; deploy note lives in its prose.

## Other ArtOverride mods (report only)
- 59 more standalone *ArtOverride mods: 28 under src/RimStarWars (donor mlie.starwarsanimalcollection, Lockjaw on sarg.alphaanimals),
  31 under src/RimUtinni (donors sarg.alphaanimals, alphamemes, mlie.horrors, VGeneticsE, vfe.insectoid2, BOTR).
  All texture-only same-path swaps (Grutt, Grithe carry 1 xml each). Same shape as Silooth -> fold candidates.
- MantistanisArtOverride and MycoidColossusArtOverride have NO About.xml (not deployable as mods at all).
- Existing item ART_OVERRIDE_FAMILY_SCRIPT_1 covers the family.

## Task 2 — MATERIAL_MERGES_CLEANUP_1
(pending)

## Deploy notes (next game-down, NOT applied)
- Silooth: deploy SWBestiary; delete C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\SiloothArtOverride; drop its packageId from live ModsConfig if active.

### 2a. Chitin (in progress)
- Groups: brittle RM_WeakChitin/RM_RotWeakChitin/RSW_WeakChitin; fragile RM_FragileChitin/RSW_FragileChitin; tough RM_MediumChitin/RM_RotMediumChitin/RSW_MediumChitin;
  toxic RM_ToxiChitin/RSW_ToxiChitin; gray RM_GrayChitin/RSW_GrayChitin; crystal RM_CrystalChitin/RSW_CrystalChitin.
- DONE (uncommitted): survivors RM_WeakChitin/RM_MediumChitin/RM_GrayChitin/RM_CrystalChitin (LanternDeeps), RM_FragileChitin/RM_ToxiChitin (Rot).
  Removed RM_RotWeakChitin, RM_RotMediumChitin, 6x RSW_*Chitin; 30 refs redirected (Rot races, Bestiary races, RM_Gristle, RM_Liliana).
  LD chitin base also carries RM_ChitinStuff (Rot spider helmet consumer). RSW_ChitinStuff/RM_DeepChitinStuff have no consumers.
- Save check (literal scan, MEASURE_ALLOW_SCAN): canonical save HOLDS all 6 RSW_*Chitin (stuff + thingDef refs); ship export none; RM_Rot* none.
  -> mapped via RM_DefAliasDef (EnvironmentalHazards mechanism).

### 2b. 7 RUT_ duplicates (in progress)
- Deleted RUT_GlowerCrust, RUT_CathedralRoachShell, RUT_Hardwood, RUT_SweetlineWool (whole files) and RUT_BrinePlate/SeepStone/SaltCameo blocks.
- Producers redirected (tags only): RUT_Glower, RUT_CathedralRoach, RUT_BrineDeposit_BrinePlate, RUT_RareGreyCatches/RareOasisCatches, RUT_SweetlineTree.
- RUT_Greatbole_CampaignBindings: hardwoodDef/mineableThing ops dropped (RM_GreatboleHardwood is already the default); C# refs to RUT_Hardwood were comments only.
- AshkarrFlora now depends on / loads after mandrake.rm.biomes (RM_SweetlineWool).

### 2c. Salt (in progress)
- One common salt = RM_RawSalt (most-referenced, C#-referenced), relabelled "salt". RM_DeltaSalt, RM_SeepSalt, RM_KettlewickSalt folded into it (plants, recipes, DecayCell cost).
- RM_Brine -> RM_BoilBrineToSalt (2 brine -> 3 salt, any cooking fire). RM_BrinePlate -> RM_CrackBrinePlate (1 plate -> 20 salt). Both stay as items.
- 4 crystal salts untouched. Bezoars untouched (not in the approved scope).

### 2d. Plasteel slag + tibanna (in progress)
- ChunkSlagPlasteel_GT removed; GravForge killedLeavings -> KotORChunk_plasteel.
- RUT_TibannaGas removed (was DEPLOY_HOLD'd, never deployed); beldon tap gatherDef -> KOTOR_Tibanna, gated on KotOR Resources / Armoury FindMod; both hold lines lifted.
- New UtinniPatches/Patches/TibannaEmbargo_CutDeepRoute.xml strips KOTOR_Tibanna's deep-drill fields (beldons the only source).

### 2e. Save migration + item
- RM_MaterialMerges_Aliases.xml (EnvironmentalHazards, RM_DefAliasDef) maps all 21 removed names; save-check table in the item.
- Bronzium split to BRONZIUM_DROP_1 (donor-only at runtime; Cherry Picker + ship re-stuff work, not a fold).
- Selftests: 282 pass, 5 fail, none from this change (ledger_lint BENCH shard, FlowWorks harmony/northstar, Halquin allowlist, Greentide acceptance map).
