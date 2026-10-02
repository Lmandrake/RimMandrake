# MIASMA_FREE_NURSERY_YOUNG_1 — the free nursery: young of four invented sea beasts

**Free tier**, `mandrake.rm.miasma` (adults live in `mandrake.rm.terminalbiomes`). Design: `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §1 (a) 2, §3, §4 row 0a. Caused by `MIASMA_SCORING_SITTING_1` (turn 1).
Decision taken by question card (owner, 2026-10-02 15:39 PDT, item 1, *Build first*): land everything the card's first option listed, plus the giant's choice in the same batch.

## What exists
- The pattern: `RM_RustNipperJuv`, `RM_SiltLampreyJuv` (`src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_SeaBeasts_Invented.xml`,
  child of the adult, juvenile-locked lifeStages, the adult's texPath; `MIASMA_NURSERY_KINDS_1`, `SEA_BEASTS_TIER_RULING_1`).
- The adults: `RM_CrimsonOpee`, `RM_ThornbackColo`, `RM_ShaleGorger`, `RM_Reefback` (same file). No juvenile for any (searched).

## spec
1. `RM_CrimsonOpeeJuv`, `RM_ThornbackColoJuv`, `RM_ShaleGorgerJuv`, `RM_ReefbackJuv` on the existing pattern (the adult's art,
   no new art).
2. Add them to `RM_Miasma/wildAnimals`, the stranding-pool juvenile list and the crèche's young. Weights `// INVENTED`, near the
   existing 0.25.

## criteria
- `jawa/get_defs` on the four `PawnKindDef`s: `foundCount` 4. A recede on a free-only tier strands at least one of the new young
  (spawn many; one result can be RNG).
