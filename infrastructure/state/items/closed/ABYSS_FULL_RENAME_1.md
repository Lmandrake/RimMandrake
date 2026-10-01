# ABYSS_FULL_RENAME_1 — Forsaken Crags / Black Crags to the Abyss

Owner typed 2026-09-30 (question card notes): "Actually I want to call it the Abyss. And do the full rename in content, code, def, mod, and put it all in the consolidated biome mod now."

Done in one change (CAULDRON_FULL_RENAME_1 shape): `RM_ForsakenCrags` -> `RM_Abyss`, `RUT_ForsakenCrags` -> `RUT_Abyss`, mod folder `src/RimMandrake/ForsakenCrags/` -> `src/RimMandrake/Abyss/`, packageId `mandrake.rm.abyss`, assembly/namespace `RimMandrake.Abyss`, worker `RM_BiomeWorker_Abyss`, patches `Abyss_Rename.xml` / `Abyss_WildSpawns.xml`, SWBestiary `*_Abyss.xml`, design sheet `abyss.md`, roster `rosters/abyss.json`. Label "the Abyss". `Biomes.compose.json` key `Abyss` (already a composed entry, wave 0 <= compose_wave 2), so the biome ships inside `mandrake.rm.biomes`.

## Accepted consequence

The canonical start save (`CANONICAL_ASHKARR_START_2026-09-12.rws`) carries `RUT_ForsakenCrags` on 1,135 tiles. Renaming the def leaves those tiles as dead references until the world repaint/remake (owner rule: the planet is repainted once, at the end). Expected and accepted; the save is NOT edited. A BiomeDef carrying 0 tiles is not a defect.

## Not changed on purpose

- "Forsaken" naming the Rakata, the Forsakens cryptid visitors, the six Forsaken vaults, donor defs (`AB_Forsaken*`, `VCEF_ForsakenAnglerfish`...): the naming question for those is still open.
- Legacy item ids `FORSAKEN_CRAGS_FAUNA_1`, `FORSAKEN_CRAGS_PREDATORS_BUILD_1`, `FORSAKENCRAGS_RM_MOD_BUILD_1` and `BLACKCRAGS_*` (ids are never renamed).
- History: `Transient/`, ledger, handoffs, closed items, artpipe job files, `world/ASHKARR_WORLDMAP_tiles.csv` (a RECORD).
- `AB_RockyCrags` (donor def, relabelled "the Abyss").

## spec

Executed. See the commit.

## criteria

- No live src/design/open-item reference to the old names remains except the list above.
- DLL rebuilt with `.srchash`; selftests and patch validation pass.

## verify

`git grep -i 'forsaken.\?crags'` over src/ and design/ returns only legacy item ids.
