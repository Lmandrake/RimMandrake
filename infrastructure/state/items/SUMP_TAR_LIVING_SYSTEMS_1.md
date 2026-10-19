# SUMP_TAR_LIVING_SYSTEMS_1 — living-map responders (tar rain ruled out 2026-10-18)

Split out of `SUMP_TAR_HYDROLOGY_1` (FOUNDRY, 2026-09-26) — the two remaining
sub-mechanisms of that six-piece item, both needing iterative live tuning or
an explicit design decision this pass could not respons­ibly guess at.

## what this item owns

1. **The living map** (`SUMP_TAR_HYDROLOGY_1` ruling 8): "slow responders
   after every rewrite — soffeth rings grow at new seeps, mouse-lines
   re-route, flora margins migrate to new edges over days. The literacy game
   stays true after every belch." This is a multi-day simulation with no
   numbers named anywhere (growth rate, re-route delay, migration speed).
   Owner ruling 2026-10-03 (by question card): FOUNDRY picks first-guess
   pacing numbers, marks them PROVISIONAL in this item and in the def
   comment / settings tooltip, and they are tuned live later. Depends on the belch (or a
   canal release) actually rewriting the map first, which after
   `SUMP_TAR_FIRE_NETWORK_1`'s item 2 (belch -> real flood release) will be
   true; today the belch only splashes filth, so there is no real "after
   every rewrite" trigger yet to hang a responder off.

   **Part 1 BUILT (2026-10-03, round 36)** as `RM_MapComponent_SumpLivingMap`
   (`mandrake.rm.environmentalhazards`): an hourly terrain diff spots any cell
   turned to tar or tar glass (belch release, canal release), so no FlowWorks
   hook is needed. **PROVISIONAL numbers** (all scaled by one Mod Setting,
   `sumpLivingMapPace`, 1.0x): a rewrite of >= 8 cells seeds a soffeth ring
   (6 stalks, radius 2-4.9, first stalk after 1 day, then one per 6 h); new
   glass is fresh crust that mice avoid (via `RM_MapComponent_DreadField.
   IsDreaded`) from 6 h after it forms until it sets at 6 days or mirrelin
   grows onto it; mirrelin reaches new glass after 2 days at ~1/72 chance
   per cell per hour, max 4 sprouts per hour. Gate: the biome carries
   RM_Soffeth or RM_Mirrelin as a wild plant (RUT_Sump carries neither today).
   First script: `validation.py` `_living_map_findings` (offline) + live
   chain `sump_living_map` (`RM_SumpLivingMapProof.ProofRewrite on|off`).

2. **No rain of any kind (owner, by question card 2026-10-18, "Sump rain -> No precipitation at all"; his
   2026-10-16 words: "Sump... NOT snowing! No precipitation").** Tar rain does not exist in any version: `RM_TheSump`
   carries `RUT_SumpDuskLock` (dusk, `RUT_SumpWeather`, rainRate 0) exactly like `RUT_Sump`; Rain, RainyThunderstorm,
   FoggyRain and both snows are 0 in its weather commonalities. The earlier tar-rain build (`RM_TarRain`,
   `RM_SumpTarRainLock`, the campaign swap, the "Tar rain" Mod Settings, `selftest_sump_tar_rain.py`) was removed.
   The shared `RM_WeatherEvent_FilthRain` kit in EnvironmentalHazards has no Sump consumer.

## what already exists to reuse

- `RM_TarCoatingUtility.CoatCells`/`CoatRadius`
  (`mandrake.rm.environmentalhazards`, `SUMP_TAR_NASTINESS_1`) is the
  existing, proven "splash tar filth across cells" mechanism a tar-rain
  weather worker would call per-tick on exposed cells/pawns — no new
  filth-application code needed, only a `WeatherEvent`/`WeatherWorker` that
  calls it and a `WeatherDef`.
- `RUT_Tarred` hediff + `RM_CarriedFilthHediffExtension`
  (`RM_TheSump_Biome.xml`) already turn tracked filth into the tarred
  condition — tracked tar filth tars pawns for free.

## verify

A soffeth ring visibly forms near a genuinely new seep/glass-front within a bounded number of days; no
precipitation of any kind ever rolls on an `RM_TheSump` map.

## criteria

The literacy game (soffeth rings, mouse lines, glass margins) keeps telling the truth about the map as the map
keeps changing.
