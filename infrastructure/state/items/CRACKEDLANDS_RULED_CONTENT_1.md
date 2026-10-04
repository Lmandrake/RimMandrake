# CRACKEDLANDS_RULED_CONTENT_1 — roster surgery, five new natives, fossils, the wax suit

Ruled at `FLOODEDCANYON_BEDAZZLE_SITTING_1` (2026-09-28; four-turn volley,
owner-typed final). **Authorities:** the 2026-09-28 amendment in
`the_cracked_lands.md`, `floodedcanyon_bedazzle_review_2026-09-28.md`, and the
cast bible `cracked_lands_bedazzle_cast_2026-09-28.md`. Coordinate with
`CRACKEDLANDS_FULL_RENAME_1` (defName base changes under it — build against
whichever name state is current when claimed).

## Scope

1. **Roster surgery on the RM_ tier**: vanilla terrestrial zoo OUT
   (Iguana/Dromedary/Fennec/Warg/Rat/Cougar + vanilla cacti rows); invented cast
   migrates to owned RM_ defs (SealedSleeper, EmperorVulture, SandLeaper,
   SandPillar, Mantrap-creature, Norphea) reusing their existing art; true canon
   (Gornt, CanCell, Convor, Woolamander) stays on the RSW_/Utinni layer.
2. **The missing patch rows**: `RUT_SealedSleeper` (0.2) and `RUT_EmperorVulture`
   (0.15) added to `WildAnimals_CrackedLands.xml` — today the paint survivor
   loses both signature creatures.
3. **Eopie off the roster, onto the roads**: remove from this biome's rows; add
   eopie (and the common-beast family the bible lists) to trader stock /
   caravan pack-animal availability so they arrive with merchants. Fliers
   (CanCell/Convor) STAY — guests and migrants, owner-ruled; the woolamander
   stays as a walking resident (canon arboreal, no flight; owner 2026-10-03).
4. **Five new natives** per the bible: RM_Muttavaq (pan giant — def lands here,
   wake/terrain mechanics in the mechanics item), RM_Uttaqar (rock troll ported
   as ours from DA_RockTroll — donor def leaves, ours replaces), RM_Irqit,
   RM_Tarruq, RM_Veqma (flora).
5. **Fossil defs**: fossil-bearing strata mineables + the item family
   (impressions / articulated skeletons / deep-stratum uniques) + mounted-display
   furniture (sculpture family, quality). GenStep/flood hooks are the mechanics
   item's.
6. **The wax suit**: crack-wax sealed underwater suit — apparel granting
   water/underwater TERRAIN survival for exploration. 🔴 Terrain survival ONLY:
   no sea-floor access, no pawn dive verb — the ship-only law is untouched
   (`WARCASKET_SUIT_CLASS_1` reconciliation).
7. **Fang Leaf relabel**: verify which of the two mantrap-labelled defs is the
   plant-form; relabel THAT one "fang leaf". defNames untouched.
8. Crack-wax texPath placeholder resolved (art riding this sitting's
   commission).

## Watch out

- `<li>` in wildAnimals/wildPlants silently discards — shorthand element form only.
- animalDensity/plantDensity stay explicitly set after the zoo eviction.
- Batch-4h renames are DRAFT — apply NO renames; current names ship.
- Two giants must not share a band: uttaqar ranges the crag walls, muttavaq the
  pans.
- Migration reuses existing art — queue nothing for the migrated six.

## verify

- RM_ roster: zero vanilla animal/plant rows, all migrated + new rows at ruled
  commonalities (measured). Sleeper + vulture present on the RM_ patch.
- Eopie absent from the roster, present in trader/caravan pools.
- Quicktest: new natives spawn; the wax suit equips and survives deep-water
  terrain; fossils mine to items; Fang Leaf label renders.
