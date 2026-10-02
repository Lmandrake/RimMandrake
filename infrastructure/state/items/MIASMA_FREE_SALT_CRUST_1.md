# MIASMA_FREE_SALT_CRUST_1 — the free Miasma gets its own salt crust, so the salt line paints without the campaign

**Free tier**, `mandrake.rm.miasma`. Design: `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §1 (b′), §4 row 0a. Caused by `MIASMA_SCORING_SITTING_1` (turn 1).
Decision taken by question card (owner, 2026-10-02 15:39 PDT, item 1, *Build first*): land everything the card's first option listed, plus the giant's choice in the same batch.

## The defect
`RM_Miasma`'s gradient axis (`landTerrain`) and stranding pools (`dryTerrain`) name `RUT_Jawa_SaltCrust`, defined only in
`src/RimUtinni/UtinniPatches/Defs/TerrainDefs/JawaSaltCrust.xml`, with no guard. Without the campaign the biome's signature
mechanic (the salt line moving over the land) has no terrain to paint: a cross-reference error at load and a dead repaint.

## What exists (reuse first)
- `RM_SaltCrustShore` (`src/RimMandrake/TerminalBiomes/Defs/TerrainDefs/RM_GreySeaTerrains.xml`, `mandrake.rm.terminalbiomes`):
  a free salt-crust terrain, but its description is the Grey Sea's (*"Every shore of this sea"*), and `mandrake.rm.miasma`
  does not depend on that mod. Reuse it only if that dependency is acceptable and the text is made biome-neutral; otherwise
  author `RM_MiasmaSaltCrust` in the Miasma mod (FOUNDRY's call; say which in the close).

## spec
1. Point `landTerrain` and `dryTerrain` on `RM_Miasma` at the free terrain.
2. The campaign twin `RUT_Miasma` keeps `RUT_Jawa_SaltCrust`.

## criteria
- Offline: no `RUT_` defName referenced from `src/RimMandrake/Miasma/Defs/BiomeDefs/RM_Miasma.xml`'s gradient and pool extensions.
- Live, on a tier **without** `mandrake.rut.patches`: no `Could not resolve` for a salt crust; a surge's recede repaints land
  to the free crust. This is also a bar for `MIASMA_FIRST_SCRIPT_1` (the salt crust painting with the campaign absent).
