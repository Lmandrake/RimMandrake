# CHIKKA_RENAME_UNREVIEWED

Caused by CHIKKA_HOME_DECIDE_NOT_STAR_WARS (card 2026-10-24 "Where should Chikka live? → Move it now").

## spec
Review, then mark clean with `code_review_status.py`, every file the move changed:
- src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_Chikka.xml (moved verbatim; leather/meat now RM_)
- src/RimMandrake/LeaningScrub/Defs/ThingDefs_Items/RM_ChikkaSupport.xml (RM_CactusHide, RM_CactusMeat)
- src/RimMandrake/LeaningScrub/Defs/Misc/RM_Chikka_Aliases.xml (RSW_Cactus* -> RM_Cactus* save aliases)
- src/RimMandrake/LeaningScrub/Defs/BiomeDefs/RM_LeaningScrub_Biome.xml (MayRequire swbestiary dropped)
- src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml, RSW_DesertPortMisc_Items.xml (cuts)
- src/RimMandrake/Utils/aa_port.py (REPOINT AA_Cactipine -> mandrake.rm.leaningscrub)
- src/RimMandrake/Utils/art/chikka_rehome_art_move.py (applied once)
- src/RimMandrake/Utils/art/art_guard.py: a retire of a kept picture whose sha is live in another slot now
  passes, matching artledger.retire (e2ac63ff8e loosened retire and the displaced check but not this one).
  Test: selftest_art_ledger_fixes.py test_d.

## deploy caveat
LeaningScrub ships inside mandrake.rm.biomes (`deploy_custom_mods.py --compose biomes`). Deploy it together
with SWBestiary (`--mod SWBestiary --prune`, 4 stale Chikka/meat PNGs) — one without the other loads
RM_Chikka twice or not at all.
