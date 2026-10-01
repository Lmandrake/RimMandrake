# CAULDRON_ENRICHMENT_LIVE_PROOF_1 — live proof of the offline Cauldron enrichment

`CAULDRON_GPT_ENRICHMENT_1` built three pieces offline (not deployed, not live-tested). Its
criterion "each quicktest-proven on a Cauldron map" is owed here for them.

## criteria (state reads, never a screenshot hunt)

- A thornwood / martyr tree's inspect string carries `Assay grade: …` (`RM_CompMetalYield`).
- A vexxiss wading in water on a map with a colonist converts cells to ToxicWater* AND a
  `Vexxiss poisoning water` letter arrives; a second within the same day does not.
- Raven nettles spawn on land touching toxic water: `RM_MapComponent_CondensateGardens`
  (mapgen pass + hourly sampling). Toxic water is rare at Cauldron mapgen, so stage it: spawn a
  vexxiss in a pond and read nettle count on its banks over a few in-game days.
- All three toggles off: none of the above happens.
