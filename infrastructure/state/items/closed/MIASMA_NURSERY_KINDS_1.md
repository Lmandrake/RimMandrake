# MIASMA_NURSERY_KINDS_1

## spec
Owner rulings 2026-09-10 (sitting + card): the sea creatures raise their young in
the Miasma's brine rings — juvenile-ONLY wild spawns there. Roster (carded, all
four options taken): **RSW_Faa, RSW_Laa, RSW_Mee, RSW_OpeeSeaKiller,
RSW_SiltLamprey, Yobshrimp, RSW_SandoAquaMonster (young), Blixus (young),
RSW_ElderSando (young)** — ElderSando young has direct lore backing (the Grey Deep
sheet: the crusted giant is "bred at the Miasma's crèches, returned here for its
solitary centuries").

Mechanism (engine-verified in Verse.PawnKindDef): one `_Young` PawnKindDef per
species — same `race`, `maxGenerationAge` capped below the race's adult
lifeStage threshold (read each race's `lifeStageAges`), `combatPower` reduced to
match juvenile stats — added to the Miasma BiomeDef `wildAnimals`. Body size and
stats scale automatically via lifeStages.

## verify
- Quicktest map on the Miasma biome: every nursery spawn is a juvenile
  (dev-inspect biological age < adult threshold); no adult of the nine spawns
  wild there.
- combatPower of each young kind sanity-checked against similar-size vanilla
  juveniles (raid-point math).
- On-map aging into adulthood is ACCEPTED fiction (the one that stayed too long),
  not a defect.
