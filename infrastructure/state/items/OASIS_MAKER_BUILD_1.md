# OASIS_MAKER_BUILD_1 — build the oasis-maker machine

Build per the RULED spec `design/RimMandrake/oasis_maker_machines_spec.md`
(rulings in its ⚖️ header, owner quotes verbatim). RimMandrake tier,
`RM_WeepingStones` kit home with the standard cross-biome enable.

## scope

1. **The machine** — dormant relic → placed → working; no fuel/power (ancient:
   it works or it doesn't); ring-by-ring stepwise terrain ladder (~3 days ring
   1, ~1.5× per ring, radius cap 6–9 by placement quality); interruption
   freezes forever, never reverses. **Center becomes REAL shallow-water pool
   terrain** (RULED) — fishable/stockable, truce + retribution radius applies.
2. **Placement** — hard floor: shadeScore≥8 (`RM_MapComponent_ShadeGrid.ShadeAt
   ≥0.5` within R=8; copy the ~100-line sampler to stay standalone per spec
   recommendation) AND rock≥15; refuse below floor; live projected-footprint
   green/red overlay (precedent `RM_PlaceWorker_OnRequiredVentComp`, vanilla
   `PlaceWorker_WatermillGenerator`).
3. **Acquisition (RULED, owner typed)** — *"sold but very expensive. Same tech
   as moisture farming itself. You can start a colony with some of those. And
   priced accordingly."* ⇒ trader stock at very high price, moisture-farming
   tech tier, scenario-start legal (a scenario part carrying 1–2). NOT
   craftable v1 (BENCH rec; reopen only on his word). Quest obtain/sabotage
   stubs deferred to quest passes.
4. R21: zero rain terms; pattern source Fertile Fields 1.6 (license unstated —
   pattern only, NO code port).

## Watch out

The projected-footprint overlay is a per-cell function of the ghost position,
not a static radius — the spec names it the honest hard part. And the grown
pool terrain must register with whatever pool-body bookkeeping
STOCKED_POOL_BUILD_1 lands (`RM_MapComponent_PoolStock`) or grown oases will
be second-class to natural ones, which the water-at-center ruling exists to
prevent.
