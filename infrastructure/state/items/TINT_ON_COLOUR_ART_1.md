# TINT_ON_COLOUR_ART_1 — 57 defs multiply full-colour art by a <color> tint

**Needs the owner's ruling.** On the Contagion sheet (2026-10-05) he asked, of five creatures, verbatim:
"stop tintint red" (Doublemaw, Eyestinger), "stop tinting it pink, I like the original art as shown on left."
(Gawpsack), "Why tinted green?" (Shambles), "why is that showing blue?" (Sparkleech). Those five tints were
removed. An audit found the same pattern on the rows below, which are left as they are until he rules.

**What the game does (MEASURED in decompiled 1.6 code, GraphicData.Init and Graphic_Multi.Init):** when
`shaderType` is unset, the default is `Cutout`, and the def's `<color>` multiplies **every pixel** of the
texture. A tint only makes sense on greyscale art. On full-colour art it recolours the painting, and that is
what the scale panel shows (`src/RimMandrake/Utils/art/scale_panel.py`). `CutoutComplex` with an `_m` mask
tints only the mask's red channel. Without a mask it tints the whole sprite; that case is INFERRED from the
shader's default mask, not measured.

**Audit method:** `~/.cache` script, re-runnable. Every RM_/RSW_/RUT_ ThingDef (plant or race) and PawnKindDef
under src/ was checked for a graphicData or bodyGraphicData `<color>` that is not white (each channel ≥250
counts as white). The texture was then resolved and its mean HSV saturation measured over opaque pixels;
above 0.15 counts as full-colour.
- 15 more tinted rows have greyscale art (≤0.15), so a tint is legitimate there and they are not listed.
- 30 have no texture under src/ (donor art), so they are UNMEASURED.
- Note that RM_ContagionIkee is on this list: its restored art (see the Contagion close progress file) is
  still multiplied by a lilac (190,170,202).

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

NEXT: show him this list as a question card. Per def or per group, the choice is to strip the tint (art shows as painted) or keep it.
