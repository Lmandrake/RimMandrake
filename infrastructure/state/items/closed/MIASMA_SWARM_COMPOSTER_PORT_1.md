# MIASMA_SWARM_COMPOSTER_PORT_1 — port the fever swarm, the karrobel and the delta loam to RM_, and the pollination gate into the free mod

**Free tier**, `mandrake.rm.miasma`. Design: `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §1 (b), §3, §4 row 0a. Caused by `MIASMA_SCORING_SITTING_1` (turn 1).
Decision taken by question card (owner, 2026-10-02 15:39 PDT, item 1, *Build first*): land everything the card's first option listed, plus the giant's choice in the same batch.

## What exists
- `RUT_FeverSwarm` (`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_FeverSwarm.xml`), `RUT_Karrobel` (`RUT_Karrobel.xml`)
  and `RUT_DeltaLoam` (`ThingDefs_Items/RUT_DeltaLoam.xml`): invented, franchise-free, authored in `mandrake.rut.patches` and wired
  into the **free** `RM_Miasma` under `MayRequire="mandrake.rut.patches"`. Both headers say a later pass should port them.
- The pollination gate: `RM_PollinationGateExtension` (free C#), but the patch that applies it
  (`src/RimUtinni/UtinniPatches/Patches/RUT_Miasma_PollinationGate.xml`) is campaign and names the campaign swarm.
- Naming context: `MIASMA_SHIPPING_NAMES_1` (open) records why these shipped `RUT_`; this port answers its retiering question
  for these two creatures.
- Art: the karrobel has a finished render, `done/rutkarrobel_v1_south` (artpipe), not in `src/`; the swarm has a south PNG only.

## spec
1. `RM_FeverSwarm`, `RM_Karrobel`, `RM_DeltaLoam` in `src/RimMandrake/Miasma/`; every reference renamed (rosters, the twin, patches,
   `RM_Miasma_MuckAndSilt.xml`'s validator note). Delete the `RUT_` originals; the twin keeps working through the renamed defs.
2. Drop the `MayRequire` gates on the free roster rows.
3. Apply the pollination gate in the free mod to its own mangals (the thessamor and quennath), naming `RM_FeverSwarm`. The
   campaign patch keeps only the donor mangal pair for the twin. (*"you cannot have the trees without the fever"* now holds in the
   free tier.)
4. Wire the karrobel's render.

## criteria
- Offline: no `MayRequire="mandrake.rut.patches"` under `src/RimMandrake/Miasma/Defs/BiomeDefs/`; no `RUT_FeverSwarm`/`RUT_Karrobel`/`RUT_DeltaLoam` anywhere in `src/`.
- Live, without the campaign: the swarm and karrobel spawn on `RM_Miasma`; a gated mangal does not spread where no swarm is.
