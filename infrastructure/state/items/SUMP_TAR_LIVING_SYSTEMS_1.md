# SUMP_TAR_LIVING_SYSTEMS_1 — living-map responders, and tar rain (mod vs scenario)

Split out of `SUMP_TAR_HYDROLOGY_1` (FOUNDRY, 2026-09-26) — the two remaining
sub-mechanisms of that six-piece item, both needing iterative live tuning or
an explicit design decision this pass could not respons­ibly guess at.

## what this item owns

1. **The living map** (`SUMP_TAR_HYDROLOGY_1` ruling 8): "slow responders
   after every rewrite — soffeth rings grow at new seeps, mouse-lines
   re-route, flora margins migrate to new edges over days. The literacy game
   stays true after every belch." This is a multi-day simulation with no
   numbers named anywhere (growth rate, re-route delay, migration speed) —
   it needs either an owner ruling on pacing or a build-then-live-tune pass,
   not an invented set of constants shipped cold. Depends on the belch (or a
   canal release) actually rewriting the map first, which after
   `SUMP_TAR_FIRE_NETWORK_1`'s item 2 (belch -> real flood release) will be
   true; today the belch only splashes filth, so there is no real "after
   every rewrite" trigger yet to hang a responder off.

2. **Tar rain — genuinely blocked on an architecture question, not merely
   deferred for time.** Ruling 1 (typed verbatim): "Tar rain is part of mod
   but not this scenario." `SUMP_TAR_HYDROLOGY_1`'s own build-status section
   found the actual blocker: **both** `RM_TheSump` (the standalone mod
   biome) and `RUT_Sump` (the campaign biome) currently force the SAME
   `RUT_SumpDuskLock` `GameCondition` via `GameCondition.ForcedWeather()`,
   which is why `RUT_SumpWeather`'s own header already calls its
   `baseWeatherCommonalities` table "pre-mod-load documentation... it never
   actually gets rolled." A new `RUT_TarRain` `WeatherDef` added the same
   way would never roll on EITHER biome under the current architecture.
   Making "mod ships it, scenario doesn't" real needs one of:
   - A scenario-level override (e.g. a `ScenPart` on the Ash'karr scenario
     that keeps forcing zero rain specifically, while the base `RM_TheSump`
     biome's own forced condition is loosened to allow tar rain through), or
   - Splitting `RUT_SumpDuskLock` into two conditions (a "permanent dusk"
     half both share, and a "no rain at all" half only the campaign keeps),
     or
   - Some other shape the owner prefers.

   This is a real fork in the campaign's already-shipped "no rain" guarantee
   (sheet ban #4) and should not be resolved silently by whichever agent
   happens to pick this item up — surface it as a question before building
   either half, per this session's own "when a tier/provenance question
   starts generating sub-questions, ask whether the category is needed at
   all" lesson (it applies here in miniature: ask which SHAPE before
   building any of them).

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

Once the architecture question above is answered: tar-rain weather exists in
`RM_TheSump` (or wherever the answer places it) and is provably absent from
the Ash'karr scenario's actual rolled weather; a soffeth ring visibly forms
near a genuinely new seep/glass-front within a bounded number of days.

## criteria

The literacy game (soffeth rings, mouse lines, glass margins) keeps telling
the truth about the map as the map keeps changing, and the tar-rain split
matches what the owner actually meant by "mod, not scenario" — not a guess.
