# belt bridge7 — fold cleanup deploy + full-list cold load + live checks, 2026-10-09 (helper #6)

## Status
- 22:20 started; read predecessor log + ART_OVERRIDE_FOLD_ALL_1 deploy note.

## (1) Kill, deploy owners, remove 59 ArtOverride mods
- 22:22 killed game (pid 20980). Backups: Player.log -> scratch; ModsConfig -> deployed/config/ModsConfig.before-bridge7_20261009.xml.
- Dry run: Biomes compose already in sync (3290 files, bridge6). Drift applied (all VERIFIED in sync): Shokk (+4 ~1), UtinniPatches (+105 ~1, fold art), JawaRules (DLL hood fix 04916d360), SWBestiary --prune (3 stale swanimals/Dewback masks; masks now at the fold path). FlowWorks game-only leftovers left alone (as bridge6).
- Deleted all 59 *ArtOverride game folders (0 absent, 0 leftover *artoverride dirs). ModsConfig parsed: 612 -> 565 active, 47 artoverride entries dropped (matches the item's 47).

### Decide strings (written before launch)
- Load up: `Bridge token:`. Dead load: `Recovered from incompatible or corrupted mods` / `Caught exception while loading play data`.
- F3 log half: 0 `Failed to find any textures` naming `RimStarWars/SWBestiary/`, `RimStarWars/Shokk/`, `RimUtinni/UtinniPatches/` (and none naming a fold creature at `Things/Pawn/Animal/Megathrips`).
- Fold patches: 0 lines naming `ArtFold` with error; 0 `Could not resolve cross-reference` new vs bridge6 baseline.
- Leather texPath fix: 0 texture errors naming RM_ToxinSealant / RM_RoyalRind / RM_GreatboleGrubSpines / RSW_TelluroxShell.
- Missing-mod warnings for artoverride ids expected 0 (entries dropped).
## (2) Relaunch, Player.log decide strings, art gaps
## (3) Jawa hood proof on a swimmer
## (4) Live checks (ZERSIUM_FORGE_BIOME_1, SHIP_ALLOY_FORGE_1 L5, MATERIAL_MERGES_CLEANUP_1, SILOOTH_ART_FOLD_1, ART_OVERRIDE_FOLD_ALL_1 F3)
## (5) Remaining acceptance rows
## Commits
## Status at close
