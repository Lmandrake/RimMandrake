# MIASMA_ROUND2_IMPORTS_1 — the September round-2 imports onto the campaign cast (bogwing flier, blarth, blixus, marsh haunt)

**Campaign tier** (canon or donor IP): `RSW_` races, cast through the Utinni patch `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Miasma.xml`.
Design: `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §1 (a) 1, §3. Caused by `MIASMA_SCORING_SITTING_1` (turn 1).
Decision taken by question card (owner, 2026-10-02 15:39 PDT, item 1, *Build first*): land everything the card's first option listed, plus the giant's choice in the same batch.

## What exists
- Owner-ruled imports, 2026-09-10 (`rosters/the_miasma.json`, *"owner review 2026-09 (round2 move mapping)"*), on neither Miasma def.
- In `src/`: only `RSW_Bogwing` (a **BodyDef**, `RSW_MlieWaveC_Bodies.xml`, also used by `RSW_Uvak`) and the call/angry/wounded/death
  SoundDefs for bogwing, blarth, blixus and marsh haunt (`RSW_Pawn_*`). No race def for any of them.

## spec
1. A race def for each (from the donor where one is installed; check `About.xml` across both mod roots before assuming none).
   The **bogwing flies** (standing rule: `MaxFlightTime`, race flight flags; no unattended live flight test).
2. Add each to the Miasma cast patch. The blarth is also faction stock (dual-listed in the json).
3. **Held, not built:** the sando aqua monster adult conflicts with the json's own note that the wild roster *"carries only the
   YOUNG side"* and with *"no second giant"* (review §1 (a) 1). Ask the owner before building it.

## criteria
- Each race resolves through `jawa/get_defs`; the patch op's xpath resolves to `RM_Miasma/wildAnimals`; the bogwing's
  `MaxFlightTime` > 0 by state read.
