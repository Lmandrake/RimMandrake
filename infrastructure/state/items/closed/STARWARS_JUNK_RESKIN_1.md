# STARWARS_JUNK_RESKIN_1

Spec: `design/RimMandrake/starwars_junk_reskin_2026-10-03.md`. Caused by `SALVAGE_WRECKAGE_EVERYWHERE_1`
(owner typed ruling 2026-10-03, quoted in the spec §1).

## Done when
- The 184 `RSW_Junk_*` artpipe jobs are finished and the owner has curated them on a review sheet.
- Kept PNGs sit in `src/RimStarWars/StarWarsPatches/Textures/Things/Building/Ruins/RSW_Junk/<VanillaDefName>/`,
  `WreckedLandspeeder.png` copied in as PodCar variant 00.
- `Patches/AncientJunk_StarWarsReskin.xml` repoints texPath (+ graphicClass to Graphic_Random where needed) and
  replaces label/description for the 24 defs in spec §2; `PodCarIsLandspeeder.xml` folded in.
- Mod Settings toggle per `MOD_OPTIONS_RETROFIT_1`.

## Watch out
- Appearance only: never touch size, drawSize, HP, passability or killedLeavings; GenSteps and prefabs place these defs.
- Graphic_Multi → Graphic_Random on rotatable defs relies on the Single being drawn rotated (as vanilla
  `AncientRustedCar` does); art is drawn pointing north. Check one rotated truck/leg in a quicktest.
- No MayRequire: all targets are Core/DLC.
