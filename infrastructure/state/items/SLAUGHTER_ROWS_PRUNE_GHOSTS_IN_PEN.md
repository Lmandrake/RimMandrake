# SLAUGHTER_ROWS_PRUNE_GHOSTS_IN_PEN

Caused by `BIOMES_PORT_PRUNE_FORTY_TWO_HITCHHIKERS` (5814416460), which deleted 42 Biomes! port creatures and their
closure (eggs, leathers, drugs, the Pustule Hornets faction).

## spec

The canonical start save (`canon.yml` `planet.start_savegame`, R3) names no def of that prune. Measured 2026-11-26:
131 deleted names, 272 references (230 food-restriction filter rows, 31 auto-slaughter rows, 4 drug-policy rows,
2 worn-apparel `<stuff>`, 2 inventory things, the whole `RSW_PustuleHornets` Faction loadID 17 with 24 relation rows).
Each is one `Could not load reference` Log.Error on every load (ScribeExtractor.DefFromNode), plus FactionManager's
`Some factions were null after loading.` Strip them offline by the CANONICAL_SAVE.md procedure (backups first), in the
Saves file and the byte-identical repo copy `world/ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws`. The frozen
09-12 save is record only (owner card 2026-11-06) and is not touched.

## verify

`python3 src/RimMandrake/Utils/save_ghost_defs.py check world/ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws`
reads NONE (exit 0); `landmark_names_check.py` (repo and Saves copies equal) and `save_world_check.py` PASS.

## criteria

- O1: the check above exits 0 on the published repo copy, and the Saves copy has the same sha256.

## refs

file: world/ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws
new: src/RimMandrake/Utils/save_ghost_defs.py
file: infrastructure/state/CANONICAL_SAVE.md
