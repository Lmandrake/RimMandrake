# Contagion sheet close — progress 2026-10-05

The owner typed "Finished Contagion. Some of the creatures had the strangest green, red, or blue tints in the Scaled image, but not in their art on the left on the sheet..."
Sheet: `contagion_sheet_2026-10-04.decisions.json` (writeCount 37). 22 rows touched; 13 rows untouched are prefill, not rulings.

## Owner notes, read as a group
- **Tints (5 rows):** he says the colour is wrong on Doublemaw, Eyestinger, Gawpsack, Shambles and Sparkleech.
- **Ikee:** he wants the ikee art he picked before.
- **Shambles:** belongs in the Rot.
- **Sizes:** Fleshsop bodysize 0.8; Gnashling bodysize 1.
- **"add variants" (13 plants):** Bleedleaf, BloodyFist, Eyebark, Gorestalk, HalfmadeTree, HalfmadeTreeBlighted, Lashgrass, Meatvine, Rattlegrope, RustPuff (B), Sapblister, Toothmoss, Wombpod.
- **BloodyMess, Fleshsop:** purges.

## Ingest — DONE
- Stamped ruled, then ran `art.py ingest`: 20 rulings, 6 purges (BloodyMess B ×3, Fleshsop B ×3), 0 refused.
- BloodyMess and Fleshsop were touched only to purge, so the ingest records no ruling for them. A is already live on both.

## Tints — DONE (5 stripped), 57 more on an item
**What the game does (MEASURED, decompiled GraphicData.Init):** none of the five sets `shaderType`, so it defaults to `Cutout`. None has an `_m` mask.
`<color>` therefore multiplies EVERY pixel. Doublemaw goes red, Eyestinger red, Gawpsack pink, Shambles green, Sparkleech blue. The scale panel was faithful.
`CutoutComplex` with a mask tints only the mask's red channel; none of the five is that case.
- **Removed:** every `<color>` on all 3 lifeStages of each of the five, in `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml`.
  No base-def graphicData, patch or RUT_ twin sets a colour on them; the RUT_Contagion twin still carries the donor AA_ roster and none of the five.
- **Audit:** every RM_/RSW_/RUT_ creature and plant def across all biomes. **57 other defs** put a non-white `<color>` on full-colour art (mean saturation >0.15).
  - 15 tinted defs have greyscale art, which is fine.
  - 30 have donor art not in src, so they are unmeasured.
  - All 57 went to **TINT_ON_COLOUR_ART_1** for his ruling, untouched.
  - ⚠️ That list includes **RM_ContagionIkee (190,170,202, lilac)**, so the restored ikee still renders lilac-tinted in game until he rules.

| def | kind | <color> | shader | game effect | art sat | file |
|---|---|---|---|---|---|---|
| RM_Blisterfloat | creature | `(192,142,172)` | Cutout(default) | whole sprite multiplied | 0.476 | `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml` |
| RM_Bloodlurk | creature | `(42,8,14)` | Cutout(default) | whole sprite multiplied | 0.66 | `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml` |
| RM_BloodyMess | creature | `(120,12,22)` | Cutout(default) | whole sprite multiplied | 0.775 | `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml` |
| RM_BrineCrown | plant | `(212,196,206)` | Cutout(default) | whole sprite multiplied | 0.214 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaFlora.xml` |
| RM_Brinecomb | plant | `(150,156,158)` | Cutout(default) | whole sprite multiplied | 0.367 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaUnderstorey.xml` |
| RM_Brogg | creature | `(49, 38, 32)` | CutoutComplex | whole sprite multiplied (no _m mask; INFERRED from the shader default) | 0.421 | `src/RimMandrake/TheRot/Defs/Fauna/RM_TheRot_Fauna_ThingDefs_Races.xml` |
| RM_ContagionIkee | creature | `(190,170,202)` | Cutout(default) | whole sprite multiplied | 0.484 | `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml` |
| RM_CruciblePod | plant | `(228,206,222)` | Cutout(default) | whole sprite multiplied | 0.367 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaFlora.xml` |
| RM_CubicSculpture | plant | `(214,186,228)` | Cutout(default) | whole sprite multiplied | 0.418 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaFlora.xml` |
| RM_Dewfringe | plant | `(196,201,184)` | Cutout(default) | whole sprite multiplied | 0.241 | `src/RimMandrake/LongShade/Defs/ThingDefs_Plants/RM_Dewfringe.xml` |
| RM_FE_Plant_EmberGrass | plant | `(198, 142, 68)` | Cutout(default) | whole sprite multiplied | 0.61 | `src/RimMandrake/Pyrelands/Defs/ThingDefs_Plants/EmberGrass.xml` |
| RM_Fleshsop | creature | `(224,198,198)` | Cutout(default) | whole sprite multiplied | 0.36 | `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml` |
| RM_Gelatid | creature | `(112, 178, 92)` | Cutout(default) | whole sprite multiplied | 0.462 | `src/RimMandrake/GelatinousSlime/Defs/ThingDefs_Races/Gelatid.xml` |
| RM_GlassVeilKelp | plant | `(226,236,234)` | Cutout(default) | whole sprite multiplied | 0.372 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaFlora.xml` |
| RM_Glasskelle | plant | `(214,236,238)` | Cutout(default) | whole sprite multiplied | 0.372 | `src/RimMandrake/DivingInteraction/Defs/ThingDefs_Plants/RM_ScaldVentFlora.xml` |
| RM_Glomvar | creature | `(226,218,200)` | Cutout(default) | whole sprite multiplied | 0.284 | `src/RimMandrake/FeverWood/Defs/ThingDefs_Races/RM_Glomvar_Race.xml` |
| RM_Gnashling | creature | `(168,148,128)` | Cutout(default) | whole sprite multiplied | 0.493 | `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml` |
| RM_GreatboleGrub | creature | `(96, 40, 110)` | Cutout(default) | whole sprite multiplied | 0.682 | `src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_GreatboleGrub.xml` |
| RM_Hoarstock | plant | `(186,186,182)` | Cutout(default) | whole sprite multiplied | 0.214 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaUnderstorey.xml` |
| RM_HoolimbrePlant | plant | `(170,225,180)` | Cutout(default) | whole sprite multiplied | 0.372 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_TwilightLightPlants.xml` |
| RM_Leachmoss | plant | `(98,92,60)` | Cutout(default) | whole sprite multiplied | 0.38 | `src/RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Plants/RM_Leachmoss.xml` |
| RM_Masonmat | plant | `(232,230,222)` | Cutout(default) | whole sprite multiplied | 0.478 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaUnderstorey.xml` |
| RM_Meltgut | creature | `(96,128,100)` | Cutout(default) | whole sprite multiplied | 0.402 | `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml` |
| RM_Milkwell | plant | `(230,224,208)` | Cutout(default) | whole sprite multiplied | 0.367 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaUnderstorey.xml` |
| RM_MosaicFanPalm | plant | `(232,196,152)` | Cutout(default) | whole sprite multiplied | 0.387 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaFlora.xml` |
| RM_Mournweft | plant | `(224,222,214)` | Cutout(default) | whole sprite multiplied | 0.387 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaUnderstorey.xml` |
| RM_Murkblush | plant | `(140,148,156)` | Cutout(default) | whole sprite multiplied | 0.418 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaUnderstorey.xml` |
| RM_Neverset | plant | `(176,176,172)` | Cutout(default) | whole sprite multiplied | 0.372 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaUnderstorey.xml` |
| RM_NoothelmPlant | plant | `(220,190,110)` | Cutout(default) | whole sprite multiplied | 0.214 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_TwilightLightPlants.xml` |
| RM_Peeper | creature | `(148,158,190)` | Cutout(default) | whole sprite multiplied | 0.428 | `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml` |
| RM_Pulsebead | plant | `(172,196,164)` | Cutout(default) | whole sprite multiplied | 0.478 | `src/RimMandrake/DivingInteraction/Defs/ThingDefs_Plants/RM_ScaldVentFlora.xml` |
| RM_Rimebeard | plant | `(198,198,192)` | Cutout(default) | whole sprite multiplied | 0.372 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaUnderstorey.xml` |
| RM_SaltBladeGrey | plant | `(238,238,232)` | Cutout(default) | whole sprite multiplied | 0.372 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaSaltBlade.xml` |
| RM_SaltBladeTwilight | plant | `(20,22,24)` | Cutout(default) | whole sprite multiplied | 0.372 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_TwilightSeaFlora.xml` |
| RM_SaltChimneyVine | plant | `(240,238,230)` | Cutout(default) | whole sprite multiplied | 0.456 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaFlora.xml` |
| RM_Saltswoon | plant | `(96,98,96)` | Cutout(default) | whole sprite multiplied | 0.418 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaUnderstorey.xml` |
| RM_Scaldhide | creature | `(112,86,70)` | Cutout(default) | whole sprite multiplied | 0.407 | `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml` |
| RM_Scorchpod | creature | `(138,112,64)` | Cutout(default) | whole sprite multiplied | 0.446 | `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml` |
| RM_SparkleechGrub | creature | `(58,140,168)` | Cutout(default) | whole sprite multiplied | 0.311 | `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml` |
| RM_SpherePlant | plant | `(236,232,220)` | Cutout(default) | whole sprite multiplied | 0.478 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaFlora.xml` |
| RM_Stillbloom | plant | `(238,236,230)` | Cutout(default) | whole sprite multiplied | 0.456 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaUnderstorey.xml` |
| RM_UltrissPad | plant | `(176,196,158)` | Cutout(default) | whole sprite multiplied | 0.31 | `src/RimMandrake/LongShade/Defs/ThingDefs_Plants/RM_Ultracactus.xml` |
| RM_VauliskLure | plant | `(214,182,84)` | CutoutComplex | whole sprite multiplied (no _m mask; INFERRED from the shader default) | 0.214 | `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_VauliskLure.xml` |
| RM_Vrekka | creature | `(185, 175, 165)` | Cutout(default) | whole sprite multiplied | 0.485 | `src/RimMandrake/LongShade/Defs/ThingDefs_Races/RM_LongShade_Fills.xml` |
| RM_Vurrak | creature | `(120,110,170)` | Cutout(default) | whole sprite multiplied | 0.369 | `src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_Vurrak.xml` |
| RSW_Bantha | creature | `(67,38,32)` | CutoutComplex | mask red channel only | 0.502 | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Bantha.xml` |
| RSW_BloodropPupa | creature | `(137,162,166)` | Cutout(default) | whole sprite multiplied | 0.632 | `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml` |
| RSW_CrystalCrab | creature | `(126,104,94)` | CutoutComplex | whole sprite multiplied (no _m mask; INFERRED from the shader default) | 0.462 | `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml` |
| RSW_Jerba | creature | `(198,182,152)` | Cutout(default) | whole sprite multiplied (its _m mask is ignored: Cutout reads none) | 0.48 | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Jerba.xml` |
| RSW_SandLeaper | creature | `(192,193,192)` | CutoutComplex | whole sprite multiplied (no _m mask; INFERRED from the shader default) | 0.237 | `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml` |
| RSW_Scavrat | creature | `(200,175,100)` | CutoutComplex | whole sprite multiplied (no _m mask; INFERRED from the shader default) | 0.351 | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Scavrat.xml` |
| RSW_ShadeWhale | creature | `(178, 148, 104)` | Cutout(default) | whole sprite multiplied | 0.179 | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_ShadeWhale.xml` |
| RSW_VentStalker | creature | `(60, 55, 65)` | Cutout(default) | whole sprite multiplied | 0.583 | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_VentStalker.xml` |
| RSW_WraidAlpha | creature | `(140, 60, 30)` | Cutout(default) | whole sprite multiplied | 0.647 | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_WraidAlpha.xml` |
| RUT_DyingCreep | plant | `(196, 30, 30, 255)` | Transparent | Transparent: whole sprite multiplied | 0.455 | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_DyingCreep.xml` |
| RUT_GreentideAnt | creature | `(120, 110, 100)` | Cutout(default) | whole sprite multiplied | 0.46 | `src/RimUtinni/GreentideRaidAnt/Defs/ThingDefs_Races/RUT_PawnKinds_GreentideAnt.xml` |
| RUT_GreentideAntSoldier | creature | `(80,80,80)` | Cutout(default) | whole sprite multiplied | 0.46 | `src/RimUtinni/GreentideRaidAnt/Defs/ThingDefs_Races/RUT_PawnKinds_GreentideAnt.xml` |

## Ikee — DONE (restored the art he liked)
**What he had.** On 2026-09-29 he ruled RM_Ikee "regen" with the note: "ERROR! We liked the Ikee from before! … This thing is hideous."
The ikee he liked is the RSW_Stareling-derived render. He re-kept it as RSW_Ikee A in desert sitting 1 (2026-10-04) and on the deep_desert sheet (2026-10-05).

**What replaced it.**
- `63a75d429` (09-28) restored the liked render into Stillsand's `RM_Ikee` folder.
- `0aff70110` (09-29, Wave A of CONTAGION_RULED_CONTENT_1) renamed the Contagion ikee to RM_ContagionIkee to avoid a name collision. It seeded the new folder with the **rejected** `RM_Ikee_*` render from `_artsrc`, calling it "already generated and validated".
- `ef1a9f4c4` copied the same rejected render onto RM_Ogleknot, which is why Ikee and Ogleknot showed identical bytes.
- `50ec04dd4` (10-04) cut RM_Ikee, the def that held his restore.

**Root cause.** His keep sat on RM_Ikee and RSW_Ikee. The renamed def started with no ruling and no history, and the rejected render was copied in as if new.

**Why the guard didn't refuse.** The write was on 09-29; the art ledger and its guard only exist from 2026-10-04.
- Even today a rename carries no ruling across.
- A "regen" verdict does not mark the rejected bytes.
- Tonight's purge of `0ccc…` was refused as "live elsewhere" (Ogleknot, which he kept as A), and nobody was told the Ikee slot held it too.
- Filed as **ART_RULING_RENAME_CARRY_1** (for FOUNDRY).

**Tonight's B is NOT his earlier art.** B is `stillsand_regen_RSW_Ikee_v2`, a fresh render. The ingest recorded his B as a keep, but it is not installed.

**Now live** in `src/RimMandrake/Contagion/Textures/Things/Pawn/Animal/RM_ContagionIkee/`: east 0a52fabd2e89, north f124c52df712, south a336837e6bad.
These are byte-identical to RSW_Ikee. They went in via `art install --ruling`, recorded with his note as owner keeps. placeholder_detect: real ×3.

## Shambles move — DONE
- Def (ThingDef + PawnKindDef) moved from `RM_ContagionFauna.xml` to `src/RimMandrake/TheRot/Defs/Fauna/RM_Shambles.xml`. TheRot does not depend on Contagion, so a cross-mod roster row would not resolve.
- Casting: removed from `RM_Contagion` wildAnimals; added to `RM_TheRot` wildAnimals at the same 0.5.
- RUT_ twins: RUT_Contagion never listed it (donor AA_ roster). The frozen RUT_TheRot was left as is.
- Art A was installed into TheRot via the ledger (ruling a61aefe1bfc4). placeholder_detect: real ×3.
- ⚠️ The Contagion copies of the Shambles PNGs are STILL ON DISK, unused, because no def points at them.
  - Why: retiring an owner-kept picture is refused by the commit hook even with his words. `artledger.retire(owner_said=…)` writes either reason "retire", which the guard calls unrecognised, or a `script:` reason, which the guard refuses for displacing a kept picture.
  - That is a gap between retire() and art_guard. It is noted on ART_RULING_RENAME_CARRY_1.

## Body sizes — DONE
Convention in this file: for creatures of size 1 or less, the adult drawSize is about equal to baseBodySize (Bloodlurk 0.8 → 0.85, BloodyMess 1.0 → 1.0). The game draws drawSize only.
- **Fleshsop:** baseBodySize 0.2 → **0.8**; drawSize 0.22/0.26/0.3 → **0.62/0.74/0.85** (stage proportions kept).
- **Gnashling:** baseBodySize 0.25 → **1**; drawSize 0.28/0.32/0.35 → **0.8/0.91/1.0**.

## Installs — DONE
- **A (13 plants + BloodyMess):** already IN GAME, nothing to copy. placeholder_detect: real.
- **RustPuff B:** the `rot_rustpuff_v2` render was already in the Graphic_Random folder as `RustPuff_A.png`. I retired the two donor files `BMT_RustPuffA/B.png` through the ledger, so B is the only picture.
- `art guard worktree`: 0 unledgered changes.

## Variant jobs — DONE: 39 jobs in `contagion_close_jobs_2026-10-05.json`
- 13 plants × var1–3. Each job carries `owner_note` "add variants" verbatim and derives from the job whose render is live (Eyebark from `RM_Eyebark_v2`, RustPuff from `rot_rustpuff_v2`).
- No facing words in any prompt; the ingest req-9 check passes.
- Graphic_Random wiring is OWED when the renders land and he picks them (same as Kethevar/Lisqueth).

## Validation
- **validate_patch, full list:** run over Contagion/Defs, TheRot/Defs and origin's `Contagion_Rename.xml` (after 0d6e51a3a), with `--mods-config infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (610 mods). Result: **0 errors**, 72 warnings, all of them vanilla texPaths it cannot see.
- **Contagion_Rename op 24 error (`AA_OcularNightling` lifeStages/li[1]/labelPlural, 0 matches) is NOT a real defect.**
  - It appears only because the live `ModsConfig.xml` is currently a **10-mod** minimal list, which does not load Alpha Animals.
  - The donor's 1.6 def does carry that `labelPlural` (lxml match = 1). The same false error shows on `Abyss_Rename.xml` for AA_Nightling, AA_NightRam and AA_NightMule.
  - The RM_ChokingSpores ParentName error is the same artifact. Nothing to fix.
- **run_selftests:** 191/192. The one failure is `bridgetools/selftest_tool_metadata.py` (DLL tool surface vs source), which is unrelated.
