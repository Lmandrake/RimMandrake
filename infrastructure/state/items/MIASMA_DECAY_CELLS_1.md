# MIASMA_DECAY_CELLS_1 — decay cells: a learned generator that makes power from rot

**Free tier**, `mandrake.rm.miasma`. Design: `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §4 row 2, §5 idea 3 (GPT's *vorrsalt cells*; the name fails the stem rule, so
"decay cells"). Caused by `MIASMA_SCORING_SITTING_1` (turn 1).
Decision taken by question card (owner, 2026-10-02 15:39 PDT, item 3, *New marks*): decay cells; and the owner typed:
*"Decay cells, but they become a rotting bed that is part of Star Wars Cuisine ingredients"*. The rotting bed is
`MIASMA_ROTTING_BED_CUISINE_1` (Star Wars tier); this item is the cell itself.

## spec (numbers `// INVENTED`)
1. Learned here: a research project unlocked by finding an old meter still reading current in a compost bed (a Miasma map feature);
   buildable anywhere after.
2. A bed of delta loam, silt ceramic and delta salt fed rotting goods (`CompRottable` items, spoiled meals, corpses at FOUNDRY's call)
   makes electricity (`CompPowerPlant`-style), output falling as the feed is spent.
3. **A spent cell becomes a rotting bed** (BENCH's reading of the typed ruling): the building swaps to a rotting-bed state that
   `MIASMA_ROTTING_BED_CUISINE_1` gives a yield. In the free tier the bed is inert or yields only compost; the yield is Star Wars tier.
4. Clear of ban 1 (it collects rot, directs nothing) and ban 3 (not medicine). Settings: on/off and a power slider.

## Depends on
`MIASMA_SWARM_COMPOSTER_PORT_1` (delta loam must be free tier first). Delta salt finally gets a use.

## criteria
- A fed cell powers a lamp in a quicktest; unfed, output falls to zero; a spent cell shows its rotting-bed state.
