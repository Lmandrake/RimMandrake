# SCRUB_WIND_BUILD_LEAN_ON_PURPOSE

## spec
Owner, by card 2026-10-20 (`design/RimMandrake/biome_bars_sitting_2026-10-20.md` §5 items 1-3): on Leaning Scrub maps
stop random plant mirroring and face the scrub/fuzz with the map's wind heading (bars `scrub_lean_visible`,
`scrub_never_lean_mixed`); the Gale shows driven dust and fuzz on screen; Overcast, GrayPall and DryThunderstorm get
the Scrub's wind as weather twins.

## built (11e47a767a, BENCH offline)
- Lean: `src/RimMandrake/LeaningScrub/Source/RM_PlantLean.cs` — one transpiler after the single `Rand.Bool` in
  `Plant.Print`; the coin is still consumed, so the seeded stream is unchanged. Listed plants get
  `RM_LeanKernel.FaceFlip`. The plants are data: `RM_LeanExtension.leanPlants` (7 fuzz/scrub plants). The variant art
  leans both ways, so `westLeaningTextures` lists the west-leaning variants, measured from the PNGs, and the variant
  vanilla is about to pick is peeked with a Rand push and pop. No per-frame allocation. Setting `leanPlantsEnabled`
  (on) redraws the maps when it changes.
- Gale: `RM_WeatherOverlay_GaleDust` on `RM_Gale` streams downwind. It is a PLACEHOLDER (vanilla fog sheet tinted
  dust-brown, `ArtState` says so) until art is reviewed. The art is queued as `RM_GaleDust_A_v1`/`_B_v1`
  (`infrastructure/artpipe/art_lists/scrub_gale_dust_2026-10-20.json`): grayscale on black, and brightness becomes
  alpha at install. NOT installed. Setting `galeDustOverlayEnabled` (on).
- Twins: `Defs/WeatherDefs/RM_LeaningScrub_WindyTwins.xml` (`RM_ScrubOvercast`, `RM_ScrubGrayPall`,
  `RM_ScrubDryThunderstorm`) are swapped into the biome at the same commonalities. DryThunderstorm already blew harder
  than the Scrub, so its twin keeps its own wind.
- Tests: `selftest_scrub_wind.py` checks the data against the art, no hardcoded defNames, the overlay wired, no
  installed art, no stock weather above 0, and the twins against vanilla Data, with 10 proven breaks.
  `LeaningScrubPlantLeanCheck.cs` covers 720 heading×art cases. `validation.py` gets the `windlean` chain (4 rows) and
  twins in `biome_weather_table`.

## owed
- Live: windlean rows need a Leaning Scrub map (LEANING_SCRUB_LEAN_SITE_1); on another map the lean rows read UNMEASURED.
- Owner: judge the look (lean read, Gale dust) at a joint session. Review the Gale dust art, then install it with
  luminance→alpha.

## criteria
- A1 L0: selftest_scrub_wind.py, LeaningScrubPlantLeanCheck (selftest_leaningscrub_fuzz.py) and selftest_leaningscrub.py pass at 11e47a767a
- A2 L1: validation.py windlean.twins_carry_wind and defs.biome_weather_table PASS live (twins load, blow, replace stock rows)
- A3 L2: validation.py windlean.lean_faces_wind and lean_toggle_off_vanilla PASS on a Leaning Scrub map
- A4 L2: validation.py windlean.gale_dust_overlay PASS live under RM_Gale (art reported as PLACEHOLDER until reviewed)
- A5 L4: owner sees the scrub lean one way with the wind, and the Gale reads as driven dust (scrub_lean_visible, scrub_gale_reads_as_gale)
