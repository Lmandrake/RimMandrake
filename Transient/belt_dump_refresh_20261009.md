# Def dump refresh 2026-10-09 (FOUNDRY helper) -- NOT CAPTURED, mismatch

- Newest capture 2026-10-09T01-58-44Z: 613 mods (full canonical set). Live ModsConfig (tier acc_20261009d): 68 mods.
- The dump writes only at game startup (dump_request.txt armed, no [RimDefDump] line in the current Player.log); a live bridge cannot re-dump.
- A capture of the 68-mod tier would become newest = DEF_DUMP for every reader, a mismatched stand-in for the canonical set. Not done.
- Dump lacks RUT_FoundrySalvageCache / RUT_FoundryFloor_SalvageCache because it predates the deploy; selftest stays red until the next full-set load.
