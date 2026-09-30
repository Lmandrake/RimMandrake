# FORGE_CYCLE_MECHANICS_1 tranche 1 report

Status: DONE (offline). No deploy, no game, no bridge, no ledger writes.

## What was built

**The pulse was extended, not re-authored.** `RM_GameCondition_WeatherPulse` (EnvironmentalHazards) gained four seams: `InBurst`, `ForceBurst(ticks)`, `AllowRandomBurstNow()` and `NonBurstWeatherOverride()`. A plain pulse behaves exactly as before. TheForge's `RM_GameCondition_ForgeCycle` subclasses it, and `RM_ForgePulse` now names that class. It is gated on the biome because only `RM_TheForge` lists the condition. Any biome that lists a condition carrying `RM_ForgeCycleExtension` gets the cycle.

| Phase | Built |
|---|---|
| 1 Still heat | The ordinary random pulses roll here only. A "hiss in the vents" letter arrives `hissLeadHours` before the gas wash. |
| 2 Gas wash | 2 to 4 waves. Each picks an unroofed cell with flammable plants and lights cells in a 7-cell radius with vanilla fire. |
| 3 Rain | The whole phase is one forced pulse burst, which brings the pulse's own weather, scald and flash window. It also spawns 2 to 4 **FlowWorks water floods** (`Flood_FlowWorks.Configure(RM_Fluid_Water)`, the clean call already used by TarPitBelch). |
| 4 Freeze | `Fog` weather and steam smoke. `LavaDeep` cells get `RM_BasaltShingle` or `RM_PumiceRubble` laid on the **1.6 temp-terrain layer** in batches (capped at 6000 cells). The lava underneath is untouched, and the engine re-derives walkability. |
| 5 Growth | 5 to 10 `RM_FloatstoneGarden` are seeded on the crust at growth 0.35, so they ripen inside the phase. The flash window spans the whole phase, as the spec says. |
| 6 Cracks | Unharvested gardens tear free and drift off, with a fleck and a counted message. The crust turns to `RM_GlowingCrackCrust`, which glows and is avoided by wanderers. A ThreatBig letter gives the time left. |
| 6 Melt | The temp layer is removed in batches. Pawns take 4×18 flame damage and are set on fire. Buildings, plants and items are killed with flame. Every loss is summarised in a message, so nothing vanishes silently. Survivors are moved to safe ground. |

**Creatures.** `RM_CompForgeCycleDormancy` sits on top of stock `CompCanBeDormant`, following the `RM_CompPanSleeper` precedent.
- The dhokkur is awake only in the rain.
- The julmox and the dhuvvox are awake during the rain and the flash window.
- Tamed animals never seal.
- `RM_DormantAnimalBody` is a copy of the vanilla Animal render tree with a custom body worker. It shows `stationaryGraphicData` only while the animal is sealed. The dhokkur uses the shipped `RM_DhokkurDormant` sprite and the dhuvvox uses `RM_DhuvvoxNodule`.

**Settings.** The Weather-pulse toggle now really works, through the gate key `TheForge.Pulse`. There are eight new toggles: grand cycle, gas wash, flooding, lava freeze, destructive melt, floatstone bloom, dormancy and warning letters. With everything off, the cycle stops and any standing crust melts back gently, harming nothing. The settings screen now scrolls.

**State reads.** Use the dev actions `RMTheForge → Forge cycle: report state` and `advance one phase`. `DebugStateReport()` returns the phase, crust count and the Stat* counters.

## Verification
- Every touched or new XML file parses.
- `validate_patch.py` over TheForge Defs, with both roots: the only error is the pre-existing `RM_CinderCrust` texPath. The new texPaths resolve.
- `dotnet build`: EnvironmentalHazards and TheForge both have 0 errors and 0 warnings.
- `run_selftests.py`: 76/78. The failure is `selftest_deployed_biome_refs`, which was already known. 1 test was UNMEASURED (bridge metadata).

## Remaining, and why
- **Soundscape.** It needs audio, and none exists. The letter fallback is built.
- **Vapor-column rendering and sky herds.** Not reached.
- **Dhuvvox mass eruption "by the hundred."** Today the wild population seals and hatches, but no swarm is spawned or despawned at a burst.
- **Dhokkur path memory.** Not built.
- **Live quicktest.** It needs a Forge map with LavaDeep. The RM_TheForge terrain bands are AB_ pebbles and grass, so lava only exists where a lava mutator or landmark put it. On a map with no lava the freeze is a no-op and the cycle closes early at the freeze. That is by design, but it should be checked live.
- **Crust art.** It reuses vanilla CooledLava and Gravel tinted.
- **Existing saves keep the old condition class.** The class name is saved, so the cycle only appears on newly generated Forge maps.
- **Every phase length and count is INVENTED.**
