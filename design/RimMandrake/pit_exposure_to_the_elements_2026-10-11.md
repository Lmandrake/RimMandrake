# Pit: "exposed to the elements" on vanilla's own temperature path — design pass, 2026-10-11

Owner, 2026-10-11, by card (verbatim):

> "as a principle to keep: Why does anyone suffer in a real pit? Because they are "exposed to the
> elements." This effectively does raise the temperature standing in the hot sun unable to escape,
> but it can do the same to cold if left there too. Normal game assumes you're using wind breaks or
> shade as you walk around when possible. A pit prevents that. Do a brief design pass on what the
> fastest way is for us to simulate being "exposed to the elements" as one would if constrained to
> the outside without shelter, shade, or windbreak that best leverages how Vanilla already works."

Bound by "One kind of heat, planet-wide" (`SOLAR_HEAT_EXPOSURE_1`) and `PIT_SUPERDEEP_COLLAPSE_1` §5.

## What vanilla 1.6 already does (read via RimSage)

- **Heatstroke**: `HediffGiver_Heat.OnIntervalPassed` raises severity only while
  `pawn.AmbientTemperature > SafeTemperatureRange().max`, and sheds it below the comfort max.
- **Hypothermia**: `HediffGiver_Hypothermia.OnIntervalPassed` is the mirror: it raises severity below
  `SafeTemperatureRange().min`, and adds frostbite below 0 °C past severity 0.37.
- `SafeTemperatureRange` = `ComfortableTemperatureRange` ± 10 °C. The comfort range is
  `GetStatValue(ComfyTemperatureMin/Max)`, re-read every tick (cache 1 tick), so **hediff
  `statOffsets` on those two stats reach both givers at once.** Vanilla hediffs already do this
  (Anomaly mutants, Odyssey prosthetics).
- **Vanilla has no windchill, wind-on-pawn or shade concept.** A search for windchill finds nothing,
  and wind only drives turbines and fire. "Outdoors" means `Room.UsesOutdoorTemperature`: it touches
  the map edge, or at least 25% of its cells are unroofed. Such a room simply reads the map's outdoor
  temperature. So an unroofed pit cell is **already** at full outdoor temperature. Vanilla's only
  model of the elements is that number set against the pawn's comfort range.
- **Our sun is already vanilla heat.** `RM_SunHeatPatches.Postfix_AmbientTemperature` (CreatureBehaviors)
  adds the cell's sun exposure, as felt degrees, on sun-heat biomes. A pit cell with no roof and no
  shade-caster gets the full offset. Nothing in the pit needs to know about the sun.

## Recommendation: an "exposed" hediff that narrows the comfort range, and nothing else

1. `RM_PitExposure` becomes a **flat marker hediff**. It is present while `RM_PitExposure.IsExposed`
   holds (a D=4 cell, unroofed, uncovered) and removed the moment it does not.
2. Its one stage carries `statOffsets`: `ComfyTemperatureMin +8`, `ComfyTemperatureMax −8`
   (PROVISIONAL, set as a Mod Setting). These stand for the shelter, shade and windbreak a free pawn
   would use and a pit takes away.
3. Vanilla does the rest. On a hot day, Heatstroke starts 8 °C sooner. On a cold night, Hypothermia
   and frostbite start 8 °C sooner. Mild weather does nothing. Hot and Cold mood thoughts fire
   earlier too, and the health tab says why ("exposed").
4. On a sun-heat biome, the sun's felt degrees stack on top through the existing patch. A pit
   gives no shade, so the "brutal sun" case is the strongest by construction. The model has one
   kind of heat, and **it cannot produce heatstroke at night** because the giver needs real heat.

## Alternatives

| | mechanism | for | against |
|---|---|---|---|
| A | A **felt-temperature offset** on `AmbientTemperature` for pit cells: + when ambient is above comfort, − when below. This is the same pattern as the sun patch. | It reuses a proven Harmony seam, and the temperature readout matches what the pawn feels. | It needs a sign rule (which way is "worse"?) and a second postfix on the hottest getter in the game. It also double-counts the sun unless it is ordered against the CreatureBehaviors patch. |
| B | **Rate multipliers** on `HediffGiver_Heat`/`_Hypothermia` severity gain while exposed (two Harmony prefixes). | Thresholds are untouched and only speed changes, which matches "wears them down swiftly". | It is more code than (1), and a patch to vanilla internals. It does nothing to mood or comfort, so the effect is invisible until a hediff appears. |

## Deleted from FlowWorks' current pit exposure

- `Pit_Hediffs.xml` `RM_PitExposure`: the **`heatstruck` stage with `HediffGiver_Random` →
  Heatstroke (mtb 1 day)**. This is the night-heatstroke bug, a second kind of heat. Also delete both
  `painOffset`s, `initialSeverity`/`maxSeverity`, and the recovery comp entry.
- `RM_PitExposureMath`: `SeverityGainPerInterval`, `SeverityDecayPerInterval`, `NextSeverity`.
- `RM_PitExposure.cs`: `HediffComp_PitExposureRecovery` + `HediffCompProperties_PitExposureRecovery`.
  Presence is now binary, and removal happens in `Tick` plus on despawn or when the setting is off.
- **`RM_Patch_PitRoomCoupling`** (the Harmony postfix on `NoRoofEqualizationTempChangePerInterval`)
  and `Coupling`/`pitTemperatureCoupling`. An exposed cell is unroofed, and vanilla already gives
  outdoor temperature to any room ≥25% unroofed or touching the edge. The coupling only ever reached
  mostly-roofed rooms, where a pawn is not exposed. (This is from the code. Confirm it with the
  inspect-pane temperature on one dug pit before deleting.)
- Kept: the `IsExposed` predicate, the resistance loss and the `RM_ExposedPrisoner` thought.
  Those are the separate captivity dial (question 2).

## Build size

Small. The XML is about 15 lines rewritten. The C# shrinks by about 80 lines net (two classes, one
patch, three math members), and one Mod Setting changes from "coupling" to "exposure narrowing
(°C)". Selftests: delete the severity and coupling checks, then add one offline check that a ±N
narrowing moves both safe bounds by N. One DLL rebuild. Estimate under 2 h including the live check.

## The test that proves it

Run it as a live quicktest through FlowWorks' functional script, on a non-sun-heat map. Use two
identically dressed colonists: one in the open pit, and a control on open ground beside it at the
same outdoor temperature. That isolates the pit's effect. Set the outdoor temperature through the
bridge so it falls **between the normal and the narrowed safe bound**. The values below are for a
human with comfort 16–26 °C, so safe 6–36 °C, narrowed by 8 to 14–28 °C:

1. **Hot**: outdoor 32 °C. The pit pawn's Heatstroke severity rises and the control's stays 0.
2. **Cold**: outdoor 10 °C. The pit pawn's Hypothermia rises and the control's stays 0. The pit
   pawn has no Heatstroke at all.
3. **Mild**: outdoor 20 °C. Neither pawn gains a temperature hediff over 6 in-game hours.
4. **Sheltered**: roof the pit cell, or cover it. `RM_PitExposure` is gone within one 250-tick
   interval, and the pit pawn's `ComfortableTemperatureRange` equals the control's.
5. (Sun-heat map, optional) The pit pawn's felt temperature = outdoor + sun offset (the sun-load
   gizmo shows full exposure).

Every reading is a deterministic state read (hediff severity, `ComfortableTemperatureRange`). No
visual judgment is needed.

## Questions for the owner (card-ready)

**Q1. How much worse is the open pit than walking around outside?**
- a) Mild, ±5 °C. A pit is unpleasant and lethal only in already-dangerous weather.
- b) **Moderate, ±8 °C (proposed).** A desert noon or a freezing night hurts within hours.
- c) Harsh, ±12 °C. Most non-temperate days hurt.
- d) Growing: it starts at ±3 °C and widens to ±12 °C over a day left in the pit.

**Q2. Should a prisoner's resistance still drop just for being in the open pit?**
- a) Yes, always while exposed (today's behaviour), even in mild weather.
- b) **Only while the elements are actually hurting them**, meaning a vanilla Heatstroke,
  Hypothermia, or Hot/Cold thought is present (proposed). That keeps "exposure" honest.
- c) No. Leave resistance alone and let pain and mood do it through vanilla.
