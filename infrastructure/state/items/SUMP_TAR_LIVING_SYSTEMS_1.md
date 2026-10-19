# SUMP_TAR_LIVING_SYSTEMS_1 — living-map responders, and tar rain (mod vs scenario)

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

2. **Tar rain — BUILT (2026-10-18).** Owner, typed 2026-10-09: *"Flowworks supports tar rain but campaign does
   not. The biome itself does except for the campaign. Correct."* The shared no-rain lock is split:
   - `RM_TheSump` now carries `RM_SumpTarRainLock` (TheSump `Defs/GameConditionDefs/`): the shared
     `RM_GameCondition_WeatherPulse` forcing `RUT_SumpWeather` (the dusk) with `RM_TarRain` spells. `RUT_SumpDuskLock`
     is unchanged and still what `RUT_Sump` carries.
   - The campaign layer swaps `RM_TheSump` back onto `RUT_SumpDuskLock`
     (`UtinniPatches/Patches/Campaign_SumpNoTarRain.xml`, FindMod on the composed "RimMandrake: Baroque Biomes"), so
     no-rain stays campaign-only through the final repaint onto RM_ biomes.
   - `RM_TarRain` (`rainRate` 0: no fire dousing, no water) fires `RM_WeatherEvent_FilthRain` (EnvironmentalHazards):
     each event coats random open-sky cells with `RM_Filth_Tar` via `RM_TarCoatingUtility` and gives exposed pawns a
     chance of tar filth (they become tarred through the existing carried-filth hediff).
   - Shared kit: `WeatherPulseExtension.burstGateKey`/`burstFrequencyKey` (burst switch keeps the dusk forced) and
     `RM_MechanicGates.RegisterScale/Scale`; pure numbers in `RM_FilthRainKernel` (fuzz family `filthrain`).
   - Mod Settings (the Sump, "Tar rain"): on/off, how often, how heavy; defaults on, 1x, 1x.
   - **PROVISIONAL numbers**: a spell every ~96 h on average, 60-180 min; an event every ~250 ticks; 6 cells per
     250x250 map per event; 4% per exposed pawn per event.
   - NOT done (FlowWorks was off-limits to this pass): tar rain refilling tar bodies or filling excavations with tar.
     FlowWorks reads `rainRate`, which tar rain keeps at 0 on purpose.
   Checks: `src/RimMandrake/TheSump/selftest_sump_tar_rain.py`, `selftest_envhazards_fuzz.py --fuzz-only filthrain`.

## what already exists to reuse

- `RM_TarCoatingUtility.CoatCells`/`CoatRadius`
  (`mandrake.rm.environmentalhazards`, `SUMP_TAR_NASTINESS_1`) is the
  existing, proven "splash tar filth across cells" mechanism a tar-rain
  weather worker would call per-tick on exposed cells/pawns — no new
  filth-application code needed, only a `WeatherEvent`/`WeatherWorker` that
  calls it and a `WeatherDef`.
- `RUT_Tarred` hediff + `RM_CarriedFilthHediffExtension`
  (`RM_TheSump_Biome.xml`) already turn tracked filth into the tarred
  condition — a tar-rain weather gets "tars pawns" for free once it
  produces `RM_Filth_Tar`.

## verify

Tar-rain weather rolls on an `RM_TheSump` map outside the campaign and is provably absent from
the Ash'karr scenario's actual rolled weather; a soffeth ring visibly forms
near a genuinely new seep/glass-front within a bounded number of days.

## criteria

The literacy game (soffeth rings, mouse lines, glass margins) keeps telling
the truth about the map as the map keeps changing, and the tar-rain split
matches what the owner actually meant by "mod, not scenario" — not a guess.
