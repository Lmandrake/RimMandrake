# CRACKEDLANDS_ENRICHMENT_QUICKTEST_1 — prove the GPT-enrichment tranche live

The parent `CRACKEDLANDS_GPT_ENRICHMENT_1` built its offline tranche and verified it only by a
clean build and selftests. Its criterion, "each quicktest-proven", is owed here for what was built.
Use STATE reads only. ⛔ No unattended flyer screenshot hunts: the migrants' fly-in and fly-out is
read from state.

## what to prove (all on an `RM_FloodedCanyon` quicktest map, dev actions under `RMFloodedCanyon`)

1. **Five beats.** Run "Arm chime + flood soon". Then "Report flood state" should walk
   `phase=Herald` with heraldBeat 1→4, then `Warned`, then `Flooding` with `roar=on` and
   `tarruqSilenced=True`. `Player.log` should hold no errors from the beat SoundDefs.
2. **Peakstorm.** Force `RM_PeakstormLight`. The report shows `peakstormConsidered=True` after one
   in-game hour, and `nextFloodTick` moves on about 60% of trials. The weather makes no
   precipitation.
3. **Recede feast.** Run "Start flood NOW", then "Recede flood NOW", then "Report recede aftermath".
   It should show `cohort>0`, `migrants>0` (only if the biome roster holds a flight-capable kind;
   on the campaign that is the convor and the can-cell), and `salvage` 2–6. Each irqit carries
   `RM_IrqitFloodBorn`. After `soakDecayDays` the cohort is corpses, not despawned, and the migrants
   hold an `ExitMapFlying` job.
4. **Salvage decay.** Forbidden salvage left in place vanishes at expiry with its message. A piece
   that was unforbidden or hauled stays.

needs: bridge.
