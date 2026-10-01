# CAULDRON_VENT_ENRICHMENT_HOOKS_1 — the Cauldron enrichments that hang on vents

Split from `CAULDRON_GPT_ENRICHMENT_1` (owner-picked by card, 2026-09-30). Every piece here needs a
vent / gas-tap ThingDef to exist, and none does: `CAULDRON_MECHANICS_BUILD_1` part 3 (The Gas) is
blocked on the design call over the Biotech gas grid's fixed GasTypes. **Blocked until that lands.**

## spec

From the parent's spec, verbatim in substance:

1. **Four-stroke weather, vent half.** Vent bloom raises local vent output after a conspicuous
   pre-bloom falter; exposure is strongest near vents, not a whole-map toxin tax. Today
   `RM_MapComponent_VentBloomExposure` taxes every outdoor unroofed pawn map-wide; it becomes
   vent-distance-weighted once vents exist. The falter also needs the next-weather foreknowledge
   design call already open on `CAULDRON_MECHANICS_BUILD_1` part 1.
2. **Vexxiss, warden of the breath, vent half.** Follows high-pressure groans, braces over a vent
   and inhales until it falls silent for several days; the silenced vent visibly recovers
   (parent criterion). Vent-drinking JobGiver + vent-suppression state.
3. **Condensate Gardens, vent half.** Crystal flowers ring stable taps; blood bouquets mark chronic
   leaks; giant toxic flowers favour recent blowouts. Extend `RM_CondensateHabitatExtension`
   (`src/RimMandrake/Cauldron/Source/RM_CondensateGardens.cs`) with vent-keyed habitats.

## open question

What IS a vent (ThingDef + GenStep + how its gas exists without a custom GasType)? Answered by
`CAULDRON_MECHANICS_BUILD_1` part 3, not here.

## criteria

- Each piece quicktest-proven on a Cauldron map; a silenced vent visibly recovers.
- Each has a Mod Settings toggle.
