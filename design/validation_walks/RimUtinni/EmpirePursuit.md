# EmpirePursuit — validation walk
subject: src/RimUtinni/EmpirePursuit  (packageId mandrake.rut.empirepursuit)
deps: Ludeon.RimWorld.Odyssey, brrainz.harmony (both modDependencies AND loadAfter);
incompatibleWith matathias.ruthlessmechanoids (the upstream mod this forks — same
namespace/defName/scenPartClass on purpose, must never run alongside it)
list: minimal+harmony     # Odyssey is an owned DLC (always available, not a mod pick);
                          # Harmony (brrainz.harmony) is the only genuine third-party mod
                          # dependency and is cheap — no other content needed to exercise
                          # this mod's own behavior end to end
status-hint: Forked ScenPart from "Ruthless Faction Pursuit" (workshop 3621784437,
Matathias, GPLv3) — endless timed pursuit raids from a chosen faction, with a
Jawa-specific "survey shadow" that multiplies the raid/warning delay 4x on poorly-
surveyed biomes (Forsaken Crags today).

## must be true
- `ScenPartDef_RuthlessPursuit` (class `RuthlessPursuingMechanoids.ScenPartDef_RuthlessPursuit`)
  carries an owner-editable `surveyShadowBiomes` list and `surveyShadowMultiplier` float,
  read directly off the def by `ScenPart_RuthlessPursuingMechanoids.ShadowMultiplier(map)` —
  returns `shadowDef.surveyShadowMultiplier` when `map.Biome` is in the list, else `1f`.
- The shipped `ScenPartDef RUT_RuthlessPursuingMechanoids` sets `surveyShadowMultiplier=4`
  and `surveyShadowBiomes` = [`AB_RockyCrags`] ("Forsaken Crags").
- `StartTimers` multiplies both the raid timer and the warning timer by `ShadowMultiplier(map)`
  before scheduling — a map on `AB_RockyCrags` gets ~4x the mean 156h(±36h) raid delay and
  48h(±12h) warning delay every other biome gets (`FirstRaidDelayHoursDef`/`WarningDelayHoursDef`
  constants, ruled by the owner 2026-08-28, not upstream's 18-35 day default).
- `Tick()` fires a raid at the raid timer (`InitialRaidMultiplier` 1.5x, floor 2000 points),
  again at `raidTimer + SecondWaveHours` (`SecondRaidMultiplier` 2.0x, floor 8000), then
  endlessly every `EndlessWavesHours` (`EndlessRaidMultiplier` 2.0x, floor 10000) unless
  `disableEndlessWaves` is set.
- `UpdateDisabled()` disables pursuit (sends a defeat/goodwill letter) once the pursuit
  faction is deactivated, defeated, or — for a non-permanent-enemy faction — no longer
  hostile to the player; `ReenableDueToRelations` restarts timers at their minimum if the
  faction turns hostile again later.
- `HarmonyPatcher` installs Harmony id `"mandrake.rut.empirepursuit"` and postfixes
  `IncidentWorker_RaidEnemy.FactionCanBeGroupSource` to exclude the pursuit faction from
  ordinary (non-pursuit) raid selection unless its ScenPart's `canDoNormalRaid` is true.
- A part added mid-game (not at scenario creation) never receives `PostWorldGenerate`/
  `PostMapGenerate` from the engine — its timer dictionaries stay empty and it never fires
  — so any live test must run both init calls explicitly.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.empirepursuit" and
   no XML error naming `ScenParts_EmpirePursuit.xml`
2. [D] def read-back: ScenPartDef `RUT_RuthlessPursuingMechanoids` exists; Class =
   `RuthlessPursuingMechanoids.ScenPartDef_RuthlessPursuit`; `scenPartClass` =
   `RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids`; `surveyShadowMultiplier`
   = 4; `surveyShadowBiomes` contains `AB_RockyCrags`
3. [B] `jawa/scenario_part_add` `className=RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids`
   `defName=RUT_RuthlessPursuingMechanoids`
   `fields="pursuitFactionDef=Mechanoid;firstRaidDelayHours=1;firstRaidDelayVarianceHours=0;warningDelayHours=1;warningDelayVarianceHours=0;canDoNormalRaid=false"`
   `initCalls="PostWorldGenerate;PostMapGenerate"` `dryRun=false` → `success:true`, the part
   appears in `parts[]` (the tool's own docstring names this exact ScenPart as needing both
   init calls "or its timer dicts stay empty and it never fires")
4. [B] `jawa/scenario_parts_get` → the added part's reflected fields match step 3
   (`pursuitFactionDef=Mechanoid`, `firstRaidDelayHours=1`, `canDoNormalRaid=false`, …)
5. [B] `jawa/raid_preview` `points=2000` → the hostile-factions list it reports does NOT
   include Mechanoid (canDoNormalRaid is false, so the Harmony postfix on
   `FactionCanBeGroupSource` should exclude it from ordinary raid selection)
6. [B] `rimworld/step_game_ticks` `ticks=5000` (comfortably past `TickInterval` = 2500 and
   past the 1-hour `firstRaidDelayHours` set in step 3) → advances the paused game enough
   for the first-period raid timer to trip
7. [B] `jawa/letter_list` → a letter labeled "Incoming mechanoids"
   (`LetterLabelMechanoidThreatRuthless`) is on the stack, or a raid has already fired —
   either is evidence the timer armed and `Tick()` reached its raid branch
8. [B] `jawa/alerts_list` → `Alert_PursuitFactionThreat` is active (`GetAlerts` only yields
   once the warning timer has tripped) once the warning window has passed
9. [B] `jawa/scenario_part_add` `className=RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids`
   `defName=RUT_RuthlessPursuingMechanoids` `fields="canDoNormalRaid=true"` `allowDuplicate=true`
   `dryRun=false`, then `jawa/raid_preview` `points=2000` again → Mechanoid now DOES appear
   among the hostile factions available (confirms the Harmony postfix's `canDoNormalRaid`
   branch flips both ways, not just the default)
10. [L] Player.log after the ticks step contains no exception naming
    `RuthlessPursuingMechanoids` or `ScenPart_RuthlessPursuingMechanoids`
11. [S] (human pass) none of substance — `RFPSettings`'s "Print Debug Messages" checkbox and
    the ScenPart's `DoEditInterface` scenario-edit screen are ordinary Mod Settings/scenario
    UI, out of scope here. Testing the `AB_RockyCrags` survey-shadow multiplier itself needs
    a live map on that biome (Alpha Biomes, full list only) and its own `DebugUtility.DebugLog`
    is gated behind `RFPSettings.printDebug` (off by default, no known bridge control) — not
    attempted here; a future pass could compare `mapRaidTimers` on an `AB_RockyCrags` map vs.
    a plain-biome map directly rather than relying on the debug log line.
