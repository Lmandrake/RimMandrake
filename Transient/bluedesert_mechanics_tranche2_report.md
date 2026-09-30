# BLUEDESERT_MECHANICS_BUILD_1 — tranche 2 report (§6 murrek re-seeding)

## Status
§6 built offline. The item stays open: §2, §7, §8 and the remainders listed in the tranche 1 report are
untouched.

## Built (all under `src/RimMandrake/BlueDesert/`)

- `Source/RM_MurrekDrift.cs`, registered in the csproj with a `<Compile Include>` line:
  - `RM_MapComponent_MurrekDrifts` checks every 250 ticks, and only on maps whose biome is `RM_BlueDesert`.
    When the weather changes from `RM_IceSandDrift` to anything else, it runs `Reseed()`:
    1. Every idle wild murrek walks to the nearest reachable deep drift and gets the burrow job. "Deep"
       means sand depth ≥ `minDriftDepth` on a standable, unroofed cell, within 40 cells. Murrek that are
       tamed, downed, in a mental state, hunting, eating, sleeping or urgently hungry are skipped.
    2. It also spawns 0–2 new murrek already buried, under three limits: the map holds fewer than 6
       murrek, `WildAnimalSpawner.AnimalEcosystemFull` is false, and the spot is unfogged, outside the
       home area and more than 18 cells from any colonist. Every buried murrek sits at least 6 cells
       from the next.
  - `RM_JobDriver_MurrekBurrow` is the biome's first new job driver. The murrek walks to the cell, digs in
    for 180 ticks under the ClearSand effecter, then lies buried under the `RM_MurrekBuried` hediff. That
    hediff is vanilla `HediffComp_Invisibility` with HoraxianInvisibility's figures, so the murrek can't be
    seen or targeted, and fire, damage or a disruptor still reveal it. It comes out of the drift when:
    - prey comes within 2.9 cells (tested with `FoodUtility.IsAcceptablePreyFor`); it erupts into a
      vanilla `PredatorHunt` against that prey
    - the cell's sand drops below `flushDepth`. This is "dig the drift, flush the thing": vanilla
      clear-sand work zeroes the cell, and the digger stands inside the ambush radius
    - it takes damage
    - it becomes urgently hungry or very tired
    - it has been buried for 2 days

    One finish action makes the murrek visible again on every exit path.
- Tuning lives in XML on the drift weather: the `RM_MurrekReseedExtension` block on `RM_IceSandDrift` in
  `Defs/WeatherDefs/RM_BlueDesertWeathers.xml`. Every figure is INVENTED. `ConfigErrors` checks that the
  kind, job and hediff are set, and that `flushDepth` is below `minDriftDepth`.
- New defs: `Defs/JobDefs/RM_BlueDesertJobs.xml` (`RM_MurrekBurrow`) and
  `Defs/HediffDefs/RM_MurrekBuried.xml`.
- Setting `murrekReseedEnabled`, default on. Off: nothing is re-seeded when a storm ends, and a murrek
  that is already buried surfaces at its next check.
- The murrek's STUB comment in `RM_BlueDesertFauna.xml` now describes what is built.

## Engine seams (RimSage, decompiled 1.6)
`SandGrid` (GetDepth/SetDepth, 0..1), `SteadyEnvironmentEffects.DoCellSteadyEffects` (sand builds up while
sandRate > 0.001 and erodes 1/180 per pass otherwise), `JobDriver_ClearSnowAndSand` (SetDepth 0 when done),
`WeatherBuildupUtility.GetBuildupCategory`, `HediffComp_Invisibility` / `InvisibilityUtility`,
`FoodUtility.IsAcceptablePreyFor` (refuses hidden prey), `JobDriver.DriverTick` (tickAction runs every tick),
`JobDriver.Notify_DamageTaken`, `WildAnimalSpawner.AnimalEcosystemFull`, `PredatorHunt` JobDef,
`HoraxianInvisibility` HediffDef.

## Verification
- Every BlueDesert XML file parses.
- `dotnet build RM_BlueDesert.csproj`: 0 warnings, 0 errors. The DLL and its `.srchash` are committed
  together.
- `run_selftests.py`: 76/78 passed, 2 skipped, 1 unmeasured (bridge tool metadata). The 1 failure is
  `selftest_deployed_biome_refs.py`, which was already failing before this tranche.
- Not deployed and not live-tested, per the brief.

## Remaining
- The item's verify quicktest "drift end re-seeds murrek" is still owed. `Reseed()` is public so a
  debug action or bridge tool can fire it without waiting for a storm. Checking whether a murrek is buried
  is a state read: `RM_MurrekBuried` present and `CurJobDef == RM_MurrekBurrow`.
- Tuning needs a live look: whether 0.5 is a reachable drift depth after one storm (vanilla Sandstorm's
  1.6 sandRate is Perlin-patchy), the ambush radius, and how many new murrek a storm should seed.
- No eruption art or sound. The eruption is a dust puff plus vanilla's predator-attack message. A
  dedicated eruption sound falls under §5's audio pipeline.
- A buried murrek stands in place: no rest recovery while buried. Being very tired pulls it up instead.
- §7 drift burial and §8 are still unbuilt, as in the tranche 1 report.
