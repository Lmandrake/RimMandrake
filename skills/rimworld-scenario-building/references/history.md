# History: corrected lines and their evidence

The active file holds the lessons. This file holds old lines that were wrong or that moved, and what showed it
(2026-11-23). Each engine fact was read in the decompiled 1.6 source or the shipped defs, through RimSage.

- **Where "0% anomaly threats" is.** `SKILL.md` named `anomalyThreatsActiveFraction` and
  `anomalyThreatsInactiveFraction`. Under `AmbientHorror`, `GameComponent_Anomaly.AnomalyThreatFractionNow` returns
  `Difficulty.overrideAnomalyThreatsFraction` when the field has a value. `DifficultyDef` has no such field.
- **"Nothing auto-spawns" under `AmbientHorror`.** False at the default: `Dialog_AnomalySettings` sets 0.15. At 0,
  `StorytellerComp.UsableIncidentsInCategory` never takes the Anomaly pool, but only for a category with
  `canUseAnomalyChance`: `ThreatSmall` and `ThreatBig`. The other categories return each usable incident first. `WeatherDecider` still allows `GrayPall`
  (`canOccurInAmbientHorror`), and most shipped biomes list it. Harbinger trees do not spawn: without a spawned monolith,
  `LevelDef` is `Inactive`, whose `desiredHarbingerTreeCount` is 0 (`GenStep_HarbingerTrees.DesiredTreeCountForMap`).
- **Custom and the Anomaly slider.** `Dialog_AnomalySettings` draws the slider with each preset. `StorytellerUI` draws
  its own slider block only on Custom. `Storyteller.SetupNonCustomDifficultyAnomalySettings` saves and loads the chosen
  values on each other preset. `Difficulty.CopyFrom` does not write the playstyle or the override.
- **`StartingHumanlikes`.** The defName is `HAR_StartingHumanlikes` (class `AlienRace.ScenPart_StartingHumanlikes`,
  workshop item 839005762). `StartingVehicle` is from workshop item 3014915404. Neither part is vanilla.
- **`ForcedTrait` and the other pawn modifiers.** `SKILL.md` said that they hit everyone. `ScenPart_PawnModifier` has
  `chance`, `context` and `hideOffMap`. With `hideOffMap`, a starter gets the change after the map generates.
- **`DisableIncident` / `DisableQuest`.** `SKILL.md` said that a quest can still fire either one. The incident part is
  one check in `IncidentWorker.CanFireNow` that `forced` and `bypassStorytellerSettings` skip. The quest part is in
  `QuestScriptDef.CanRun`, which has no bypass; `IncidentWorker_GiveQuest.CanFireNowSub` calls `CanRun`.
- **`scariaRotChance`.** `SKILL.md` listed it as animal hostility. `Pawn.Kill` uses it for `CompRottable.RotImmediately`.
- **`fixedWealthMode`.** `Map.PlayerWealthForStoryteller` reads `AgeInDays`, which counts from `generationTick` of the
  map.
- **The frequency "dropdown".** The `AnomalyFrequency_*` keys label a slider. A real state file once held a check
  written against them, and that check failed on a correct setup.
- **The faction page as "the only record of what was chosen".** `WorldInfo.ExposeData` writes `factions`. One observed
  save held `<factions IsNull="True" />` (`SCENARIO_SETTINGS_SPEC.md` B13). `WorldInfo.ExposeData` does not write
  `overallPopulation` or `landmarkDensity`.
- **Factions after world creation.** `BackCompatibility.FactionManagerPostLoadInit` adds `HoraxCult`, `Entities`,
  `TradersGuild` and `Salvagers` at load when they are absent. It adds `Empire` only when `World.info.factions` is null.
  No vanilla screen adds a faction.
- **A scenario part with a missing def.** `GameDataSaveLoader.TryLoadScenario` removes the part and sets `valid` to
  false. `Page_SelectScenario` then shows a warning icon and the mod-check window.
- **ScenPart count.** On one heavily modded 1.6 stack: **72 ScenPartDefs** across ten categories.
- **Planet types.** `SKILL.md` said: most "we must hand-build this world" problems are really zonation problems, and a
  PlanetTypeDef does zonation better than a person can. The root `CLAUDE.md` rule "There is no worldgen feature" decides
  otherwise for our one map. `SCENARIO_SETTINGS_SPEC.md` B4 still sets one planet type. The fields were read in `Source/PlanetTypeDef.cs` and by literal search of
  `AlienWorlds.dll` (workshop item 3626210061).
