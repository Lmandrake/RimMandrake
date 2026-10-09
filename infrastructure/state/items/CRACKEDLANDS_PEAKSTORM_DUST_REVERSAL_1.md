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

## verify
Ruled by card 2026-10-08 (custom sky overlay). Built 2026-10-09, all numbers PROVISIONAL: `RM_WeatherOverlay_PeakstormDust` (FloodedCanyon) on `RM_PeakstormLight.overlayClasses`; `RM_DustKernel` period 2400 ticks, 300 reversed, 60 ramp. Mod Settings toggle `peakstormDustReversalEnabled`. Dust art is vanilla's fog sheet standing in.
- Offline: kernel check in the FloodedCanyon selftest Main (forward at tick 0, reaches -1, inert when off); `selftest_floodedcanyon_fuzz.py` passes.
- Live (needs bridge): `validation.py` chain `peakstorm_dust_reversal` samples `RM_PeakstormDustProof.ProofState` across a period and requires both `reversed=True` and `reversed=False`. State read only, no screenshots.

### Exact checks 2026-10-09 (acceptance sitting)
- A2 CHECK: Existing chain `peakstorm_dust_reversal` in `FloodedCanyon/validation.py`. Raw: with Peakstorm Light standing (`jawa/weather_set` / `jawa/game_condition`; the proof refuses otherwise), call `jawa/static_call type="RimMandrake.FloodedCanyon.RM_PeakstormDustProof" method="ProofState" args=""` 10 times, 270 ticks apart (`rimworld/step_game_ticks`, clock verified with `jawa/time_clock`), and collect the `reversed=` value from each result. PASS: every result contains `weather=RM_PeakstormLight` and the collected set of reversed values is exactly {True, False}. FAIL: only one value seen in 10 samples (never reverses or never returns), or a result without `weather=RM_PeakstormLight` (UNMEASURED: wrong weather, not a fail).
