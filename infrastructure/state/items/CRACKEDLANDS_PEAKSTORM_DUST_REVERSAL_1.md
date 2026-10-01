# CRACKEDLANDS_PEAKSTORM_DUST_REVERSAL_1 — dust briefly reverses under Peakstorm Light

Split from `CRACKEDLANDS_GPT_ENRICHMENT_1` §3. Peakstorm Light now has the bruised-red sky, gusty
wind (`windSpeedFactor` 1.6, TUNED) and a flood pull that is a chance, not a timer
(`src/RimMandrake/FloodedCanyon/Defs/WeatherDefs/RM_PeakstormLight.xml`). One clause of the pick is
still owed: *"dust motes briefly reverse direction as cool, wet-clay air pushes through the slots."*

## open question

A WeatherDef has no field for mote direction. Options:

- a custom `SkyOverlay` / `WeatherOverlay` drifting dust one way, then briefly the other;
- a weather event that throws dust motes travelling against the wind for a few seconds;
- drop the clause.

Pick one: the first two are small C#, and both need dust art or a vanilla dust mote reused.

## criteria

During Peakstorm Light, the dust visibly flows one way and reverses at intervals. This is checked
in a joint session or by a state read of the overlay's direction, never by an unattended
screenshot hunt.
